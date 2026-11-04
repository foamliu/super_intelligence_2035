# 深读：1793065824220_rigwz — FineSim/Solido MC 运行失败模式诊断 + 状态/聚合一致性审计

## trace 元数据
- session: 1793065824220_rigwz.messages.json
- user: e0024852 @ hfeg0pkn004 (ip 10.129.2.x), mc=72
- N_msgs: 99；keywords: hspice:171;netlist:137;schematic:109;.def:20;cmos:7
- domain: spice_sim（MC 仿真结果诊断）

## 用户意图（逐轮）
- U0 "solido software usage" → Solido 工具使用（RAG ask-eda，非交付）
- **U9 "see /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/variation_designer_7, find data bug, and how to debug"** ← 核心任务（A-档合规：用户未给根因，只要求找 bug）
- U33 "check testbench" → 检查 tt_-40_0.675.sp
- U45 "how to fix each bug to make results more acceptable" → 修复建议
- U57+ 切换到 PEX/dspf-tool 流程的 permission/command-not-found/module-load 环境报错诊断（独立任务）
- U96-98 "tell me the different in ... each *.sp ... in chinese" → 未完成（末轮）

## 真实流（U9-U45）
- 工具：Siemens EDA Solido Variation Designer 2022.1.2 + FineSim，MC 1000 samples Optimal Spread target sigma=3.0，4 次 MC 运行 (MC-0..MC-3)
- testbench: tt_-40_0.675.sp (TT corner, -40°C, VVDD=0.825V)，`.DC VIN 0.0 VVDD 10e-3 sweep monte=1`
- 输出指标: Ileak, Iread, Iwrite, WNM_1, WNM_2
- agent 工具链: list_allowed_files → read project_setup_12.xml → read MC-0/engine.log（分页 40-200 / 1500-1725）→ read MC-1/summary.json → read project.setup → read process-model-files/devices.json → grep stdout error/fail/warn（shell-runner DENIED：profile 需 filePath）→ 文字诊断
- **agent 从未真跑 FineSim**（全程 read_files + 一次 run_approved_command DENIED）→ L1（读附件诊断）忠实

## agent 发现的 Bug（A[32] 报告）
- **Bug #1（关键）**: "所有仿真均标记为 Failed，但 yield 报告为 +infinity" — engine.log 全 Failed，summary yield=+inf。**根因 = 状态/聚合不一致**：per-run status (Failed) 未传播到 aggregate yield 计算
- 报告还涉及 testbench 结构（.include option_hspice.sp / pwr.sp / switch.sp / bitcell netlist / .LIB ttg_sram_fs / pre_sim_fs）

## 便携 reframe（B-档 synthesized, L1）
- trace 原 Solido Variation Designer + foundry SRAM PEX 不可移植 .75；agent 也未真跑 → 保留「MC 运行失败模式分类 + 状态/聚合一致性审计」子技能
- 取 FineSim 风格 MC/corner-sweep 的 run logs + result.mt0 + per-run status.json + summary.json 作为附件（静态文本，无 sim）
- **失败模式分类（7 类，按优先级）**: license_fail > port_mismatch_abort > env_error > non_convergence > measure_error > timeout > passed
  - passed: log 含 "Successfully Completed" + .mt0 有有效 measure
  - non_convergence: log 含 "DC not converged" / "non-convergence"
  - measure_error: ".measure ... failed" / .mt0 空/全 NaN
  - port_mismatch_abort: "subckt ... and ... have different number of pins" / "undefined subckt" → abort
  - license_fail: "no valid license" / "License to run is temporarily unavailable"
  - timeout: log 截断 / 无 "job concluded" / SIGKILL
  - env_error: "Permission denied" / "command not found" / "module: command not found"（来自 trace U57-U95）
- **一致性审计**: 从 per-run verdicts 算 computed_n_pass，与 summary.json reported_n_pass/yield 比对，不匹配则 aggregate_inconsistency=True
- A: 8 runs, **故意植入 trace 的 Bug #1**（全 failed 但 summary yield=+inf/n_pass=8 → inconsistency=True）
- B: 10 runs, 不同失败模式组合（含 license_fail + measure_error + port_mismatch + non-conv + timeout + env_error + passes），summary **一致**（inconsistency=False）；名/指标/run 名全不同

## distinct
- r4p2e McRonMismatch = MC .md0 6σ/std 统计提取器（成功运行的统计）
- NetlistLintHsp-001 = 网表语法 lint（含 pin_count_mismatch 但非运行时失败分类）
- FineSimDcConvFix-001 = 单运行 non-conv 修复器
- 本条 = **多运行失败模式分类器 + 状态/聚合一致性审计器**（shard B 首个「MC run failure-mode classifier + consistency auditor」），distinct ✓

## case 设计：EDA-Eval-DesignFlow-McFailModeDiag-001
- spice_sim, B档 synthesized, L1, track synthesized, k=14
- 候选 mc_faildiag.py（CLI <runs_dir> <summary.json> <out_dir>）
- check.py 14 条 a-n: zip/compile/subprocess-B/B-verdict-set/non-conv-count/measure-error-count/port-mismatch-count/license-fail-count/env-error-count/aggregate-consistency/root-cause-evidence/name-agnostic/cross-input-A-rerun/determinism
- 6 neg + §4.9 三假 + selftest（本地 L1，无 .75）

## A-档不可用
- 用户未明确接受 variation_designer 诊断结果（U45 后切到 PEX 任务）；多任务 session 无单一接受产物 → B-档 synthesized（子技能忠实）
