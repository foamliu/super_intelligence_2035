# deepread — sid 1795907092176_vdeyi (e0025768 / hfeg0plg49 / mc=65 / spice_sim)

- **session**: `/home/e0025768/.cline/data/sessions/1795907092176_vdeyi/1795907092176_vdeyi.messages.json` (214KB, 51 msgs, 2 real UI)
- **host**: hfeg0plg49 (10.129.x), scp 经 eda_flow run_commands 到 .75 workdir
- **domain**: spice_sim（LP5 level-shifter PVT corner 优化工作流的 LSF bsub 批量仿真失败诊断）
- **选档**: A-档 seed UI#0 逐字「我在执行模拟电路优化工作流时，第三步验证流程报错... merge.py ... 未找到匹配的 CSV 文件 ... 帮我分析一下原因」= 纯需求（只给现象，未给根因/修复）；但末轮 UI#49 = "stop current task"（用户中断，未显式接受修复产物）→ A-档 disqualified → **B-档 synthesized**。金标准 = agent 真实定位的三层根因链（root/secondary/symptom）+ 修复方向，人工确认逻辑自洽。

## 真实流（agent 25 轮排查，3 层根因）
1. 读 merge.py（test-type 配置 delay_pvt/funtrip_pvt/Ioff_pvt/speed_delay_pvt + tag 提取正则）→ merge.py 本身逻辑正确，只是 glob 找不到 CSV。
2. ls sim/delay_pvt/ → 4 个输出目录全空（0 文件）。
3. find *.out.mt0.csv → 全无；但 split/ 下 .sp 文件齐全（2_delay_NV_T2T.sp 等）。
4. 读 run_log → 4 系列 bsub 共提交 38 作业，check_series_errors 全报「✅ 无error错误」，但步骤4.5 报「38 个文件未找到」。
5. bjobs -l → **所有 38 作业 Status=EXIT, exit code 1, CPU time 0.0 秒**，执行节点 hfeg0pjn088，提交节点 hfeg0plg49。
6. 关键对照：bjobs -l 316076（8月3日历史作业）→ Status=DONE, CPU 2.6 秒，**同一执行节点 hfeg0pjn088** → 证明 .sp 没问题 + 执行节点本来能跑 hspice。
7. 在提交节点直接 `hspice -i 2_delay_NV_T2T.sp` → 成功，产出 .out.mt0.csv → 再次证明 .sp + hspice 本身 OK。
8. 读 run_4.sh → `bsub -q "$QUEUE" "hspice -i '$file' -o '$output_file'"` 用**裸 hspice**；`module load hspice/V-2023.12` 在 run_simulation_series 顶部（只影响提交节点 shell）。
9. 读 check_series_errors → `[ -f "$lis_file" ]` 判断，无 .lis 时跳过 → total_errors=0 → 误报「无error」。

**根因链**：
- 🔴 根因：bsub 作业在**执行节点** hfeg0pjn088 跑，`module load` 只影响提交节点 shell 环境，执行节点上裸命令 `hspice` 不在 PATH → 38 作业全 exit1/CPU0.0。
- 🟡 次因：check_series_errors 假阳性（无 .lis 文件 → 跳过 error 检查 → 误报「无error」，仿真实则没跑）。
- 🟠 表现：merge.py 找不到 CSV（sim 目录空 → 无 .mt0.csv → 下游报错）。

**修复**：run_4.sh 中 `which hspice` 取绝对路径 → `HSPICE_BIN=$(which hspice 2>/dev/null || echo /apps/synopsys/hspice/V-2023.12/hspice/bin/hspice)` → bsub 命令改 `"$HSPICE_BIN -i '$file' -o '$output_file'"`。agent 已开始 editor 改 run_4.sh（msg47-48 diff 可见），用户 msg49 中断。

## 便携化（L1 离线静态 + subprocess 候选，无 EDA 工具运行）
- **任务**：B-档 synthesized。候选写 `lvlshft_bsub_diag.py`（CLI `<asset_dir> <out_json>`），读 run_4.sh / bjobs_log.txt / run_log.txt / sim_dir_listing.txt / merge.py / sp_sample.sp → 结构化 diagnosis_report.json，定位根因（不限于复述 "merge.py 找不到 CSV" 表象）。
- **A 附件**（真实 trace 内容，轻裁剪）：run_4.sh（含 check_series_errors + run_simulation_series 裸 hspice bsub）/ bjobs_log.txt（38 作业 EXIT CPU0.0 + 316076 DONE 对照）/ run_log.txt（假阳性「无error」+「38 文件未找到」+ merge.py 报错）/ sim_dir_listing.txt（空目录 + 提交节点直跑成功）/ merge.py / sp_sample.sp / prompt.txt / task_brief.md
- **隐藏 B**（结构性不同，不进 SUT 沙箱）：vint 模式 / vss2vpp 电路 / 提交节点 hfeg0plg55 / 执行节点 hfeg0pjn077 / queue rscalc2 / 系列分布 delay=7 funtrip=3 Ioff=7 speed_delay=7 共 24 作业 / 历史成功作业 499021(10-27)。根因与 A 同，所有数值/节点不同 → 跨输入守卫。

## check.py 17 条独立断言 (a)-(q)，k=17=k_check≥8 GATE PASS
a zip含diag.py · b py_compile · c B上exit0+合法JSON · d root_cause==hspice_not_on_exec_node · e failed_jobs_count==B的24(跨输入 vs A的38) · f 全 exit_code==1 · g cpu_time_max==0.0 · h 假阳性识别(报无error但无.lis) · i files_not_found==B的24(跨输入) · j symptom.is_root_cause==False(不把表象当根因) · k sp_files_valid==True(不冤枉.sp) · l direct_run_works==True · m exec_node==B的hfeg0pjn077(跨输入) · n fix用绝对路径非module load · o bsub裸hspice检出 · p 3次重跑字节一致(确定性) · q submit_node!=exec_node(环境错配)

## 核心陷阱（烤进 check.py）
1. **表象 vs 根因**：naive_blame_merge 把 merge.py 当根因 → 击穿 (d)(j)。
2. **假阳性 error 检测器**：check_series_errors 报「无error」但仿真没跑（无 .lis 跳过检查）→ naive 采信则误判 → 击穿 (h)。
3. **跨输入守卫**：naive_hardcode_a 硬编 A 的 38/hfeg0pjn088/316076 → B 期望 24/hfeg0pjn077/499021 → 击穿 (e)(i)(m)(q)。
4. **冤枉 .sp**：naive_blame_sp 说 .sp 坏 → 击穿 (k)(l)（提交节点直跑成功 + 历史作业 DONE 反证）。
5. **错修复**：naive_module_fix 建议「执行节点 module load」→ 击穿 (n)（真实修复是 bsub 命令里用 $HSPICE_BIN 绝对路径）。

## 自验（本地纯 Python3，L1 无需 .75）
- ref **PASS 17/17**（a-q 全过）
- 5 negative 全 FAIL-as-expected（NEG_RC=0，10 个互异 FAIL label）：
  - naive_empty→c（空壳，无 JSON）
  - naive_hardcode_a→e,i,m,q（§4.9b print-expected，跨输入守卫击穿）
  - naive_blame_merge→d,j（§4.9c core-deleted，根因+表象倒置）
  - naive_blame_sp→k,l（冤枉 .sp）
  - naive_module_fix→n（错修复）
- §4.9 三假（空壳/print-expected/掏空根因）全 FAIL。
- test 字段==disk check.py（md5 4214f3e3fe2795f1d8c22155db94f6ed，roundtrip OK）。
- 断言闸门 k_rationale=k_check=17≥8 ✓。
- ledger vdeyi claimed→case，covered 33→34，spice_sim 25→26，追加 EDA-Eval-DesignFlow_B.jsonl 第 37 行。

## distinct vs 已有 B case
- SiOutDiag=PrimeSim si.out 内存/OOM 诊断（资源耗尽型失败）；本条=LSF bsub 批量仿真 env/PATH 型失败 + 假阳性 error 检测器（环境错配型失败），失败模式与诊断路径完全不同。
- Vcc2scPVTvar/InvPVTchar/PVTalterChar=多角 PVT 表征（仿真跑通后的指标聚合）；本条=仿真**没跑通**的根因诊断（上游失败，非指标分析）。
- TaperBufOpt/VihTripTune=优化搜索；本条=故障诊断。无重叠。
