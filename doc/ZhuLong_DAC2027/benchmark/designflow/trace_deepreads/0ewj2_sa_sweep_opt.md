# Deepread: 0ewj2 — SA slicer width-optimization sweep (analog_context, A-faithful)

- **trace**: `1791946488468_0ewj2` / jiangbaol @ hfeg0plg99 / mc=29 / 82 msgs / 301KB
- **session_file**: `/home/jiangbaol/.cline/data/sessions/1791946488468_0ewj2/1791946488468_0ewj2.messages.json`
- **domain**: analog_context (SPICE device-sizing optimization; FineSim + LSF sweep)
- **A-faithful 提需求轮**: ✓ U#0 单 shot 提出目标，未指出根因/未给修复方案

## U#0 (逐字原文)
```
/proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa.sp
根据该.sp调节pmoswidth/pmosfinger/nmoswidth/nmosfinger/itailwidth/itailwidthfinger/inwidth/inwidthfinger使Cur_slicer_latch_avg在TT_1V_45 corner下最大不超过380uA，使slicer2nd_dly_r0/slicer2nd_dly_r1最小，工作过程文件可放在/proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/SA_opt
```
意图：调 8 个器件参数（4 对 width/finger），使 TT_1V_45 corner 下电流 ≤380uA 且二级 latch 延迟 r0/r1 最小。

## agent 工具链
1. `get_agent_policy_status` + `list_allowed_files` 探 strongarm 目录 → 发现 SA_opt 已有基建（README/scripts/results.tsv/runs/000 baseline + runs/001-006 旧 run）
2. `read_files` 读 `004_onlySlicer_delay_dejoa.sp`（73-205 行）+ `DEJOA_SA_5corner_VDD2C.sp`（5 corner .alter 结构）
3. `read_files` 读 SA_opt/README.md + results.tsv + scripts/{sa_submit,sa_collect,sa_wait}.sh → baseline 000: pmos12/6 nmos1/1 itail24/8 in28/4 → cur=350uA dly_r0=46.11ps dly_r1=45.12ps
4. `run_approved_command` sa_check.sh → bjobs + 旧 run log：旧 run 全 "Completed with error(s)" 无 mt0.csv
5. 诊断：旧 run 失败 = FineSim license daemon down（`License to run is temporarily unavailable` + `daemon is down` + `ERROR! exit due to the previous license problem`）
6. lic_probe.sh → lmstat：1881 端口 ansyslmd 全 UP，但 FineSim FSPRO vendor daemon 对 exec host 仍 down
7. `editor` 写 `sa_sweep.sh`（自包含 sweep driver：submit/wait/collect 三模式）
   - submit_one：把 8 个 `.param Xwidth = <val>` + `.param Xfinger = Xwidth/<den>` 注入 per-run .sp
   - `bsub -q fqueue2h` 提交 `finesim -i run_$ID.sp -o run_$ID -np 16`
   - wait：轮询 `run_$ID.mt0.csv` 是否生成
   - collect：解析 mt0.csv 第一行（alter#=1 = TT_1V_45）抽 current + delays → results.tsv
8. submit 9 candidate（001-009，变 8 参数）：001 itail+28/7；002 itail++32/8；003 pmos+16/8；004 in+34/4；005 itail+&in+；006 nmos+2/1；007 pmos+&itail+；008 nmos+&itail+；009 全加
9. wait 100s/115s × 2 → 9 job 全 RUN 但卡 "License to run is temporarily unavailable"，120s 后 ERROR 退出（同 10-14 失败）
10. sa_tail.sh 确认：run_001.sp 参数替换正确，netlist 解析正常，纯 license 阻塞
11. `editor` sa_finalize.sh：cp sa_sweep.sh → SA_opt/scripts/，追加 README Campaign B 文档（9 候选表 + 选择规则：在 cur≤380uA 的 TT 行中选 max(dly_r0,dly_r1) 最小者 + license 阻塞记录 + 重跑命令链）
12. 末尾文字汇报：优化 campaign 已搭好，license 阻塞是环境问题；附 strongarm offset 仿真方法（用户 U#5 旁问）

## 金标准（用户实际接受的结果）
agent 未拿到真实 sim 数值（license 阻塞），但固化了完整优化 campaign：
- **sa_sweep.sh**：config 驱动 sweep driver（参数注入 + bsub LSF + mt0.csv 轮询 + results.tsv 收集）
- **Campaign B 文档**：9 候选配置表 + baseline + 选择规则（cur≤target ∧ min max(dly_r0,dly_r1)）+ corner=TT_1V_45 alter#=1 + 重跑命令
用户未反驳（trace 末尾无异议）→ 接受 campaign 设置。

## 合成计划（A 档 trace-faithful，L1-boundary）
真实 FineSim/LSF 执行非确定性 + license 阻塞 → 降级为 config-driven 生成器 `gen_sa_sweep_ref.py`：
- 读 config → 生成 `sa_sweep.sh`（参数注入 + bsub + mt0.csv 轮询 + results.tsv 收集）+ `opt_plan.json`（候选表 + 选择规则 + 量指标 + corner + baseline）
- **case-id**: `EDA-Eval-DesignFlow-SaSweepOpt-001`（analog_context）
- **资产 A**：config_A.json（8 参数 / TT_1V_45 / cur≤380uA / 9 候选 / baseline 000=12/6 1/1 24/8 28/4 cur=350uA）+ prompt.txt（U#0 逐字）+ task_brief.md
- **hidden B**：config_B.json（不同 deck/corner=FF_1V1_-40 / cur≤420uA / 量指标 I_dd_avg/clk2q_dly / 7 候选 / baseline 不同）+ hidden_manifest.json（cross_guard）
- **reference**: gen_sa_sweep_ref.py + reference_submit.zip
- **check.py**: 15 条件 a-o（zip含gen / py_compile / 跑B出sweep.sh+plan / bsub / .param 8参数 / mt0.csv轮询 / results.tsv收集 / profile.lsf / finesim -i -o / plan候选数+8值 / plan量指标==B / plan corner+baseline+deck==B / 选择规则 / 跨输入护栏 / 非退化+3sha+§4.9三假FAIL）
- **5 negatives**: fake_empty→c / fake_print_fixed_A→n / fake_core_deleted→d / naive_no_param_subst→e / naive_no_collect→g
- k_rationale == k_check == 15 ≥ 8 ✓
