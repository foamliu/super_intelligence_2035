# Deepread: 1795907092176_vdeyi — LSF bsub HSPICE farm job failure diagnosis

**trace**: `1785907092176_vdeyi.messages.json` (e0025768 @ hfeg0plg49 / 10.129.8.86, mc=65, hspice:361, 51 msgs, 2026-08-05, model deepseek-v4-pro-fp4)
> 注：台账/trace_source 记 `1795907092176_vdeyi`（首位 179 vs 真实 178，claim 时 typo，与并发 case trace_source 一致，保留不改正以免破坏 anchor 去重）。

## 用户真实意图（A-档合规轮）
- **T0（msg[0]，纯需求轮）**：「我在执行模拟电路优化工作流时，第三步验证流程报错：... merge.py --sim-dir .../delay_pvt ... Warning: 未找到匹配的 CSV 文件: .../2_delay_*.out.mt0.csv 帮我分析一下原因」
  - 用户只给表象（merge.py 找不到 CSV），未指出根因/未给修复 → A-档合规。
- **msg[49]**：「stop current task」— 用户叫停修复编辑（未显式接受修复方案 → A-档 disqualified，归 B-档 synthesized）。

## 真实诊断链（agent 还原）
1. merge.py 找不到 `2_delay_*.out.mt0.csv` → 查 sim/delay_pvt/ 目录为空（无任何 .mt0.csv）。
2. `bjobs -a | grep 4335` → 38 个 bsub HSPICE 作业（433489–433534，series: delay/Ioff/speed_delay/funtrip）全部 **EXIT**。
3. `bjobs -l 433489/433500/433515/433534` → 全部 **Exited with exit code 1, CPU time 0.0 seconds**（HSPICE 二进制从未在执行节点跑起来）。
4. 对比：`bjobs -l 316076`（8月3日同执行节点 hfeg0pjn088）→ **DONE, CPU 2.6s**（历史作业正常）。
5. 手动测试：提交节点 hfeg0plg49 上 `which hspice` → `/apps/synopsys/SRB/hspice/V-2023.12/hspice/bin/hspice`，直跑 `hspice -i 2_delay_NV_T2T.sp` 成功，产出 `.out.mt0.csv`（194B）等 6 文件。
6. **根因**：`module load hspice/V-2023.12` 只影响提交节点环境，不传播到 LSF 执行节点 → 执行节点 PATH 无 hspice → bsub 作业 exit 1 / 0 CPU。
7. **修复**：run_4.sh 的 `run_simulation_series()` 中捕获 `HSPICE_BIN=$(which hspice)`，bsub 命令用 `$HSPICE_BIN -i ...` 绝对路径而非裸 `hspice`（agent 开始编辑 msg[47]，用户 msg[49] 叫停）。
8. 次因：`check_series_errors()` 假阳性 — 无 .lis 文件时跳过检查 → 误报"无 error"。

## .75 HSPICE 真跑验证（本轮自验）
- 便携 inverter delay testbench（level-1 NMOS/PMOS，`.lib tt` 块）在 .75 HSPICE V-2023.12-SP1-1 跑通：`hspice -i portable.sp -o ./out` → 产出 `.mt0`（$DATA1），tpdf=5.671e-11, tpdr=4.830e-11。
- 注：.75 HSPICE 不直接产 `.mt0.csv`（CSV 是工作流后处理转换的产物）；本 case 验证用 `.mt0` $DATA1 解析。

## 本轮产出 = 0 新 jsonl 行（碰撞并发）

**并发迭代 @15:23（commit 6b6d3db）已先 ship `EDA-Eval-DesignFlow-LvlshftBsubDiag-001`**（spice_sim, B-档 synthesized, L1, k=17）于同一 trace vdeyi。按 §3「1 trace = 1 case」+ 2tuxj 先例（并发先到 → revert 后到变体），**本轮不追加 B.jsonl**，我的 L2 变体不进库。

**本轮真实贡献**：
1. **ledger 覆盖**：claim 14:17 + mark 15:28 vdeyi → case（指 concurrent case-id LvlshftBsubDiag-001）。并发 commit 未动 ledger_B.tsv（68gc9 先例），claim+mark 补齐覆盖率唯一分子，covered 33→34, spice_sim 25→26。
2. **独立 L2 变体 recipe**（本笔记 + .75 workdir `shardB_20261103-shardB_vdeyi-deepread_0`，可在 fresh trace 复用，见下）。
3. **并发 case viability 独立复核**：concurrent LvlshftBsubDiag-001 = L1 离线日志/脚本静态分析（无 EDA 工具运行），与本轮 L2（真跑 HSPICE）设计独立。

## L2 变体 recipe（可复用，未入库）

**case 设计** `EDA-Eval-DesignFlow-BsubFarmDiag-001`（未入库，recipe 存档供 fresh trace 复用）：
- **便携子技能**：候选写 `diag_farm_fail.py <log_dir> <sp_file> <out_json>`，解析 bjobs 日志（`bjobs -a` summary + `bjobs -l` 失败块 + DONE 对比块）→ 分类失败模式（exit_code+cpu_time）→ 对便携 .sp **真跑 HSPICE** 验证网表有效性 → 产出结构化 diagnosis.json。
- **A 输入**：env_launch_failure（全 38 作业 exit 1 / CPU 0.0 / module 不传播到执行节点）。
- **隐藏 B（跨输入守卫）**：resource_oom（作业 exit 137 / CPU>0 / TERM_MEMLIMIT / MAX MEM 4096M）→ 候选须分类为 resource_oom 非 env_launch（防硬编 A）。
- **check.py 15 条断言 a-o**：a zip含 diag+diagnosis_A · b py_compile · c 必需键 · d failure_class==env_launch_failure · e n_affected==EXIT 计数(21) · f 全 exit1+cpu0.0 · g root_cause 提 env/PATH/module 传播 · h fix 提绝对路径/module load · i evidence 含 exit code 1 · j evidence 含 cpu 0.0 · k contrast_job 316076 DONE cpu>0 · l hspice_ran=true · m tpdf 候选值 vs check.py 独立 HSPICE GT ±5%（防纯打印/防 skip HSPICE）· n B failure_class==resource_oom（跨输入守卫）· o B evidence 含 137+cpu>0。
- **.75 端到端 negative_selftest 一把过**：ref PASS 15/15 + 5 neg 全 FAIL 互异 primary tag (a/n/m/d/l)：naive_empty→a · naive_hardcode_a→n（B 误判 env_launch）· naive_print_expected→m（假 tpdf 1e-10 vs GT 5.671e-11）· naive_unknown_class→d · naive_no_hspice→l。§4.9 三假（空壳/print-expected/掏空 HSPICE）全 FAIL。
- **资产**：真实 bjobs 日志（bjobs_a_summary/bjobs_l_fail/bjobs_l_done/hspice_manual_test/merge_error，逐字保留 e0025768/hfeg0plg49/hfeg0pjn088/路径）+ portable.sp（level-1 inverter delay testbench）+ corner.lib + params_A.json；hidden={B bjobs 日志 OOM + params_B + hidden_manifest}。

**教训**：
1. JS template literal 会吞单反斜杠 → Python 正则 `\d` 变 `d`。规避：用 `[0-9]`/`[A-Za-z]`/`[(]`/`[)]` 等无反斜杠字符类。
2. MCP `write_file` 对 JSON 形 content 有自动解析 bug（dict vs string）→ JSON 文件改用 `run_commands` 里 `python json.dump` 写。
3. `/tmp/opencode` 在本机被 app.e0042624 占有不可写 → 用 `$HOME` 下临时目录。
4. 选 trace 前先 `tail -1 B.jsonl | grep vdeyi` + `git log -- B.jsonl` 查并发是否已 ship；本会话 claim@14:17 但并发 ship@15:23 在后，git pull 才可见——本轮 0 新 jsonl 归并发，ledger 覆盖为唯一贡献。
5. .75 HSPICE 不直接产 `.mt0.csv`（CSV 是工作流后处理）；便携验证用 `.mt0` $DATA1 解析即可。
6. 候选 workdir 只放 prompt+assets+task_brief（§4.8 泄漏隔离）；check.py 在 workdir 外独立跑，reference/绝不进 SUT 沙箱。
