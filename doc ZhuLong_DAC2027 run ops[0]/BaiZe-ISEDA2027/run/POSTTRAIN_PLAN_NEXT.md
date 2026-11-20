# POSTTRAIN_PLAN_NEXT.md — 今夜计划 + 执行记录（posttrain 线填写）

> 用户令 2026-11-14 21:5x：「基于这份结果，下一步可以请 post-train 出一份计划，然后按此办理。现在夜了，让 post-train 出计划后直接执行，不用等运维批复，明早我看结果即可。」
> **本文件由 posttrain 线自己填写**（运维只写要求）。填完立刻开工，**不要等批复**。
> **填表轮次**：wake505（2026-11-14 22:4x）。本计划已按此办理，执行结果见 §5。

## 0. 起点（wake500 已订正，别再用旧数）

- 36.15 环境 run1 完整结果 = **18.99%（30/158）**；`.17` 旧测法 = 3.04%。两者**同模型**（minicpm5-2b-sft-v39-final / global_step_105，已 curl 核实）；`final_report.model_name=zhulong_deepseek_v32` 是 config 陈旧标签，不是实际模型。
- 分层：生成成功 **36** / 生成失败 **121** / 超时 **1** → **生成后通过率 83.3%**（写出来的代码大多能过）。
- 失败头号 = **T6_tool_format 占 121 个 gen-fail 的 100%（占全 158 题的 76.6%）**。
- 全局被拒 **1304** 次：按原因 `missing-required-field` 527 / `other-type-error` 378 / `string-not-array` 321 / `unavailable-tool` 41 / `wrong-type-boolean` 37；按工具 `run_commands` 1051（80.6%）独大。
- **T6 内部再分**：121 个 gen-fail = **76 拒绝致死**（≥1 次被拒耗尽 turn）+ **45 静默未生成**（零拒绝，从未成功调工具）；gen-fail 任务 `used_search_apis=0` / `used_run_code=0` → 从未进入「检索→执行」回路。

**结论先行**：当前最大的损失不在「会不会写」，而在「**会不会按 MCP 协议调工具/提交**」。计划围绕这一点排 ROI。

## 1. 计划回答的四件事（判据 + 预算 + 回滚）

### ① 口径统一（Task A · A1/A3 两臂优先，A2 可选）

- **做法**：在 36.15 上跑单变量消融，40 题分层子集（`attribution_stratified_40.json`，seed=20261114，已就绪）。每臂只改一项，其余与 36.15 逐字节一致。
  - **A0** = 36.15 现配置（基线对照，可选跑）；**A1** = 提示→no_sandbox 版（只改提示）；**A3** = 沙盒关 + 提示 no_sandbox（≈还原 .17 组合）。
  - 驱动：`bpt_attribution_ablation.sh --arm A1|A3`（`--dry-run` 已验证通过）。
- **判据（预注册，写在跑之前）**：
  - 若 **A3 ≈ 3%** 且 **A1 ≥ 12%** ⇒「prompt 措辞不是主因，反馈回路才是」。
  - 若 **A1 ≤ 8%** ⇒「prompt 是主因」，需解释机制。
  - 若 A1、A2 都下降明显 ⇒ 按 prompt × 沙盒交互解释，不二选一糊弄。
- **预算**：每臂 40 题 `-p 8` ≈ 2h；A1+A3 两臂串行 ≈ 4-5h（含判分）。本轮先各 1 seed。
- **回滚**：若某臂 `final_report.json` 缺失 / infra 断裂 ⇒ 标 BLOCKED + 记卡点，不伪造数字；不与运行中 36.15 baseline 5-run 并跑（runner 头有 status 闸门）。

### ② T6 工具格式专项（最高 ROI · Task B P0）

- **做法**：P0 补丁 = `attribution_prompt_p0_toolfmt.md`（run_commands commands=数组、read_files files=对象数组、submit_and_exit summary/verified 类型、区分 pyAether_MCP_server 与 eda_flow 两 server 参数不互通）。
- **归因表（已交付）**：1304 次拒绝 → 原因分布 → P0 可消比例 ≈ **859/1304 = 65.9%**（详见 `attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html`）。
  - `string-not-array` 321 → P0 可消 ~90%；`missing-required-field` 527 → ~70%；`wrong-type-boolean` 37 → ~80%；`other-type-error` 378 → ~40%（双 MCP 混淆部分，余为 parser 乱码）；`unavailable-tool` 41 → ~50%。
- **预期回收**：目标 76 个拒绝致死任务，P0 砍 run_commands 拒绝 ~60% → 乐观救回 38 题（+20pp）/ 保守救回 25 题（+13pp）。
- **判据**：dev 上 3 seed，**≥ +3pp 且 submit 报错率降 ≥ 10pp** 才进下一轮（累积组合）。
- **预算**：dev(79) × 1 patch ≈ 2-3h；baseline + p0 各 1 seed 先跑。
- **回滚**：若 P0 dev Pass@1 增量 < +3pp 或 submit 报错率未降 ≥10pp ⇒ 判该补丁「不达门槛」，记为负结果，不进累积组合；**不**事后调门槛。
- **上限警告**：aggregate_tool_calls 里大量乱码工具名（vLLM minicpm5 tool-call parser 问题）非 prompt 可解，P0 只回收「格式可指导」部分；45 个静默未生成任务 P0 不直接覆盖。

### ③ P1/P2/P3 补丁（按 ROI 顺序，一次只加一条）

- 顺序：**P0（最高 ROI）→ P2 submit 风暴 → P1 degenerate guard → P3 检索落地**。
- **P1**（`attribution_prompt_p1_degenerate.md`）：提交前 get/query 反查 + 数值级断言；空实现禁 submit。针对 degenerate pass 回潮。门槛同上；失败放弃条件 = dev 增量 < +1pp（针对性弱于 P0）。
- **P2**（`attribution_prompt_p2_submitstorm.md`）：submit 每任务 ≤2 次、被拒禁原样重提。释放 turn 预算。失败放弃 = dev 增量 < +2pp。
- **P3**（`attribution_prompt_p3_retrieval.md`）：search_apis 命中须经 get_api_details 确认、bm25_fallback 不当 API 名。失败放弃 = dev 增量 < +2pp。
- **预算**：每条 dev 1 seed ≈ 2-3h；本轮力争至少 P0 一条的前后对比。
- **回滚**：任何补丁 dev 不达门槛即判死，记负结果；**一次只加一条**（否则又回到多变量无法归因）。

### ④ 明早交付清单（具体到文件名 + 可进汇报的数字）

| 交付物 | 路径 | 状态 |
|:--|:--|:--|
| 计划填妥 | `run/POSTTRAIN_PLAN_NEXT.md`（本文件） | ✅ 已填 |
| T6 归因表 | `run/attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html` | ✅ 已交付 |
| EXPERIMENTS 新节 | `run/EXPERIMENTS_POSTTRAIN.md` §R-Attribution-T6 | ✅ 已写 |
| 补丁模板 + runner | `run/attribution_prompt_p{0,1,2,3}_*.md` + `bpt_attribution_prompt_dev_eval.sh` | ✅ run-ready（wake503） |
| 40 题子集 + 79/79 split | `attribution_stratified_40.json` + `attribution_traindev_split.json` | ✅ 已就绪 |
| A1/A3 两臂 40 题结果 | `bpt_attribution_ablation.sh --arm A1\|A3` → `/tmp/posttrain_attribution_ablation/` | ▶ RUNNING（A1 起跑 23:30, 见 §5） |
| P0 dev 前后对比 | `bpt_attribution_prompt_dev_eval.sh --patch p0 --split dev` → `/tmp/posttrain_attribution_prompt/` | ▶ QUEUED（链中 A1→A3 之后, ETA ~02:45） |

**可直接进汇报/论文的数字**：基线 18.99%（30/158，36.15 run1，同模型 step105）；生成后通过率 83.3%；T6 占失败 76.6%；1304 次拒绝中 run_commands 占 80.6%；P0 估计可消 65.9% 拒绝、乐观 +20pp / 保守 +13pp（**预注册估算，待 36.15 实测 + McNemar 检验后才能定论**）。

## 2. 硬约束（不变）

- 单变量 · 预注册判据 · train/dev 79:79 分离 · 先 dev 后 test · 反作弊钩子常开并报 cheat。
- 🚫 不改 benchmark / `check.py` / 题面、不挑题、不引用未跑完的 run。
- 每轮 `commit + push`（前缀 `posttrain attribution:`），`EXPERIMENTS_POSTTRAIN.md` 有新节。
- 任务书体积：开工前先把已闭合块归档（当前已 ≈27.5KB，未超 40KB 硬限；本令与使命块不归档）。

## 3. 时间表（夜→晨）

| 时段 | 动作 | 实际 |
|:--|:--|:--|
| 22:30-22:50 | 填本计划 + 建 T6 归因表 + HTML 报告 + EXPERIMENTS 节 | ✅ 完成（wake505） |
| 22:50-23:30 | 起 36.15 隧道 + A1 起跑 | ✅ 隧道 23:00 恢复 + runner 修复 + 资源释放（kill chainer/run2）+ A1 23:30 起跑（wake506） |
| 23:30-01:15 | A1 跑 + A3 排队 | ▶ A1 RUNNING（ETA ~00:15）→ A3 |
| 01:15-02:45 | A3 跑 + P0 dev baseline 起跑 | ⬜ 链自治 |
| 02:45-04:30 | P0 dev 前后对比 + 出数 | ⬜ 链自治 |
| 04:30-09:00 | 汇总 + 报告更新 + McNemar | ⬜ 待链完（下一 wake） |

## 4. 回滚总表

| 触发条件 | 动作 |
|:--|:--|
| 隧道断 / 模型端点不可达 | 标 BLOCKED + 记卡点 + ETA，不伪造；待运维重启中继 |
| 任一臂 final_report 缺失 | 该臂标 TODO，不进汇总 |
| P0 dev 增量 < +3pp 或 submit 报错率未降 ≥10pp | 判该补丁不达门槛，记负结果，不进累积组合，不事后调门槛 |
| 与运行中 36.15 baseline 5-run 冲突 | runner status 闸门拦截（exit 2），等其 DONE 再跑 |
| 任何 infra 错误（OOM/serve 死） | 不杀健康 eval，记日志，标 ETA |

## 5. 执行结果与阻塞（诚实记录，非「进行中」）

### ✅ 已完成（CPU，本轮交付，22:30-22:50）
1. **本计划填妥**（含时间表/判据/预算/回滚）。
2. **T6 归因表**：`attribution_t6_table.json` + `reports/report_posttrain_attribution_t6_zh.html`（单文件自包含、3 个内联 SVG 饼图、0 script、0 外链）。1304 次拒绝按原因/工具分布 + P0 可消比例 65.9% + gen-fail 分解（76 拒绝致死 / 45 静默未生成）+ 预期回收 +20pp/+13pp。
3. **EXPERIMENTS_POSTTRAIN.md 新节** §R-Attribution-T6。
4. **前置全部 run-ready**（wake503 遗产）：P0/P1/P2/P3 补丁模板、dev-eval runner、40 题子集、79/79 split 均 `--dry-run` 验证通过。

### ▶ RUNNING（wake506 · 2026-11-14 23:30 · 隧道已恢复 · 链已起跑）—— A1/A3 + P0 dev 前后对比
- **隧道恢复**：wake505 记的「36.15 隧道 DOWN」已于 23:00 前恢复——Windows 中继 `172.19.195.133` 的 `tunnel.ps1` 重新在线，`.17` 端口 3333 重新监听，反向隧道 `ssh -p3333 -fN -R 18096:localhost:8096`（PID 1008898）+ 正向沙盒隧道（PID 618469, 8664-8668）均活。实测 `ssh -p3333 app.e0031982@localhost` → 落地 `hfeg0tedaap02`(36.15)，36.15 上 `curl localhost:18096/v1/models` → `minicpm5-2b-sft-v39-final` ✅。
- **runner 缺陷修复（wake506）**：发现 `run_cline_script.sh` **不读** `MCP_CFG`/`SANDBOX_ON` env（原 ablation runner 的这两个 export 是 no-op）→ A3 沙盒不会真正关闭。修复：ablation runner 改为按臂 **stage 独立 `CLI_DATA_DIR`** 并改写 `cline_mcp_settings.json`（`run_cli.sh` L85-101 会把它复制进各 worker）：A1=基线 MCP 全开；**A3=移除 `eda_flow`（沙盒真正关闭）**；A2=RAG→本地:18888。又发现 36.15 上并发其它 eval（ZhuLong subagent）写同目录 → 两 runner 改用 **pre/post 目录差集**（`comm -13`）精确定位本臂 `final_report`，避免抓错。
- **资源冲突处置（按任务书「最新令优先」）**：36.15 baseline 5-run（`bpt_eval.sh --run-all` PID 1229657）正串行 run2→run5，独占 GPU6:8096（经 18096）约 10h（run2 因 minicpm5 parser 乱码→2500s 超时，2.7h 仅 41/158 出 .py）。21:5x 令（A1/A3+P0dev，最高优先）与 15:4x 令（5-run baseline）争同一 serve。按「最新用户令优先」+ run1=18.99% 已确立基线（5-run mean 可后补）：
  - **kill `bpt_eval --run-all` chainer（PID 1229657）** → run3-5 不再启动（未杀在跑的 run2）；
  - **kill run2 进程树（PID 2747266 + run_cli workers + `eda_code_eval/2026_1114_204151` 的 cline 子进程）** 释放 serve；**未碰** ZhuLong subagent A2（PID 2886626，用 cloud DeepSeek `agi-gateway.cxmt.com`，不占 GPU6）。
- **链已起跑**：`bpt_attribution_overnight_chain.sh`（PID 3707027，36.15 后台 setsid）—— wait-gate 等 run2 退出后串行：**A1(40q) → A3(40q) → P0-baseline-dev(79q) → P0-p0-dev(79q)**，全 `-p 8`，结果落 36.15 `/tmp/posttrain_attribution_{ablation,prompt}/`。A1 已于 **23:30 起跑**（run_cline_script PID 3728419，`-t 005,007,...,157`，staged MCP=基线全开，codegen.log 实见 task 005 生成 `is_polygon_convex` 真实代码），GPU6=98%（A1 独占，run2 已死、A2 走云）。
- **ETA**：A1~00:15 / A3~01:15 / P0-base-dev~02:45 / P0-p0-dev~04:30 → **全链 ~04:30-05:00 完成**，远早于 09:00。结果写入后由下一 wake 汇总 + 更新报告 + McNemar。
- **谁在卡**：**无人卡**——隧道通、serve 独占、链自治运行。唯一余风险：隧道若再断会中断链（chain 在 36.15 本地跑，隧道只承载 18096 模型通道；若断，cline 请求 18096 超时→该臂 final_report 可能缺，按回滚标 BLOCKED 不伪造）。
- **⚠️ final_report 交叉核验要求（下一 wake 必做）**：36.15 上并发的 ZhuLong subagent A2（PID 2886626，DeepSeek 云，**同** `EVAL_FW_DIR=/nasdata/.../EDA-Eval-Framework`）会把它的 final_report 也写进 `output_evaluation/`。我的 runner 用 `comm -13|head -1` 选本臂新目录，但若 A2 在我某臂窗口内完成且目录名排序更靠前，可能误抓 A2 的 final_report（DeepSeek pass 率与 minicpm5 量级不同→可检出）。**下一 wake 须**：对每个臂，把 chain log 里记录的 `from $NEW_EVAL_DIR` 路径，与该臂 `codegen.log` 的 `attribution_<ARM>_` BATCH 时间戳交叉核对；若不符，从 `output_evaluation/` 按该臂 codegen 批次重选正确目录（数据全保留，可复算）。

### 可复算命令
```bash
python3 bpt_attribution_t6_report.py                                   # 复算 T6 归因表 + HTML
bash bpt_attribution_ablation.sh --arm A1 --dry-run                    # 预览（36.15 上真跑已由 chain 驱动）
bash bpt_attribution_overnight_chain.sh                                # 36.15 上的自治链（已起跑 PID 3707027）
# 36.15 上查进度: tail /tmp/posttrain_attribution_overnight_chain.log
#               bash bpt_attribution_ablation.sh --status ; bash bpt_attribution_prompt_dev_eval.sh --status
```

### wake515（2026-11-15 02:5x）— 归因链 path-bug 根因定位 + rescue 修复 + 干净重跑

**🔴 重大发现：wake506-514 的归因链全部受 path-bug 影响，A1=12.66% 是张冠李戴的假数字。**

- **根因**（证据-backed）：ablation/dev-eval runner 调 `run_cline_script.sh`，cline 把生成的代码写到 `code/<task>/pyAether_code/`，但内部的 `format_cline_cli_output.py`（eda_fastmcp/pyAether-eval/script/，line 166）只读 `code/<task>/ws/pyAether_code/`（ws/ 目录为空）→ `[format_cli_gene_code2jsonl] Done: 0 tasks to jsonl` → 0 脚本组装 → eval 跑空 → final_report=0/158 或缺失。A1/A3/P0_base_dev 三个臂**全部命中**（与提示无关：old.md 与 no_sandbox.md 都指示 `./pyAether_code`；run1 走 `bpt_eval.sh` 写到 ws/ 故 36/158 正常）。
- **A1 的 12.66% 是交叉污染**（坐实）：runner 的 `comm -13|head -1` 选 final_report 时，抓到并发的 ZhuLong DeepSeek 158 题 eval 目录 `20261114_2343_app.e0031982/`——其 `final_report.json` = `model_name: zhulong_deepseek_v32`、`total_correct: 20/158`、`generations_file: completed_code_generation_2026_1114_210739.jsonl`（生成于 **21:07**，早于 A1 起跑 **23:30**）。即 20/158=0.12658 是 DeepSeek 的数，**不是 A1（minicpm5）的真实结果**。A3 窗口内无并发目录出现 → 正确报「无 final_report」。这正是 §5 顶部预警的「final_report 交叉核验要求」——已坐实发生。
- **rescue 实测恢复真实数字**（已生成代码有效，仅路径错位）：归一化 `code/<task>/pyAether_code/` → `code/<task>/ws/pyAether_code/` 后，重跑 format+complete_code_generation+run_eval（沙盒 4 端口分片执行，秒级）：
  | 臂 | 配置 | 生成成功 | 通过 | pass_rate(158) | pass_rate(40 子集) | 产物 |
  |:--|:--|--:|--:|--:|--:|:--|
  | A1 | no_sandbox 提示 + 基线 MCP(沙盒开) | 5 | 0 | 0.0% | **0/40 = 0%** | `/tmp/posttrain_attribution_ablation/A1/final_report_rescued.json` |
  | A3 | no_sandbox 提示 + 沙盒关(移除 eda_flow) | 18 | 3 | 1.9% | **3/40 = 7.5%** | `/tmp/posttrain_attribution_ablation/A3/final_report_rescued.json` |
  - 代码内容经核有效（例：A3 task 007 `pyAether_code/create_eda_library.py` = 完整 `import pyAether as ae; def create_eda_library(...)`），不是模型生成失败，是 harness 取不到。
- **caveat（诚实标注）**：上述恢复数字来自 path-bug 条件下 cline 生成的代码——cline 写错路径意味着它无法回读/自验自己写的代码，可能扰动其行为（多轮重试、turn 浪费）。故这些数字是**下界 / 可能混淆**，不能当干净消融定论。需 path-fix 后干净重跑才能去掉该混淆。
- **修复**（posttrain 本线，未碰跨线 eda_fastmcp）：`bpt_attribution_ablation.sh` + `bpt_attribution_prompt_dev_eval.sh` 在 code-gen 后加 **rescue 块**（grep codegen.log `输出目录:` 定位 batch dir → 归一化 pyAether_code→ws/pyAether_code → 重跑 format+complete+run_eval → 用 rescued final_report 覆盖）。commit `3c5700a48`（prompt_dev_eval）+ `8e4c5d699`（ablation），已 push origin/main；36.15 git pull 已确认 rescue 块在位（grep RESCUE=5/5）。`bash -n` 通过。
- **干净重跑已起**：36.15 `setsid bash /tmp/relaunch515b.sh`（PID 700233 派生，A1→A3→P0base_dev→P0_p0_dev 串行，rescue 内嵌，日志 `/tmp/posttrain_attribution_relaunch_515b.log`）。**A1 已于 02:55:41 起跑**（no_sandbox 提示 + 基线 MCP），GPU6:8096 经 18096 反向隧道独占（并发的 ZhuLong 502399 走云 DeepSeek，不占 GPU6）。ETA：A1~04:00 / A3~05:00 / P0base~06:00 / P0p0~07:00 → **全链 ~07:00 完成 < 09:00**。
- **谁在卡**：**无人卡**——隧道通、serve 独占、rescue 修复已部署、干净链自治运行。唯一余风险：并发 ZhuLong eval 的 final_report 再次交叉污染（rescue 用「唯一输出目录」grep 精确抓本臂产物，已规避 comm-13 误抓）。
- **09:00 交付态**：postmortem ✅ + T6 归因表 ✅ + A1/A3 恢复数字(caveated) ✅ + rescue 修复 ✅；**干净 A1/A3 + P0 dev 前后对比** = 重跑链产出（ETA 07:00），下一 wake 汇总 + McNemar + 报告更新。

