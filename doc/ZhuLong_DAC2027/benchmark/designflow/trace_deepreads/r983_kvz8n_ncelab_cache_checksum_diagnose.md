# r983 trace_deepread: kvz8n (ethanw@hfeg0pkn004, mc26, verification)

## Session
- session_file: 1795072565975_kvz8n.messages.json (subdir: 1795072565975_kvz8n/)
- user: ethanw, host: hfeg0pkn004, mc=26
- keywords: verilog:173;netlist:145;aether:4;cadence:3;virtuoso:1;systemverilog:1;synopsys:1;pt_shell:1;.def:1
- scp: ssh e0031982@hfeg0pkn004, find subdir, scp 140KB/20msgs
- A-domain verdict: verilog:173 dominant → A-pure verification ✓

## User intents (4 turns)
- U#0 (msg 0): ncelab *E,RDUNCA tstrim_init + *E,DLCSMD ddr5_package→MRS_DQ_monitor + *E,RDUNCA MRS_DQ_monitor → "分析原因和解决方案"
- U#4 (msg 4): vsim -c 1119 -p drvqa/V0 -a ddr5 → "什么都没输出" (为什么?)
- U#12 (msg 12): ncelab *E,ICFNR coverage_ccf.ccf (drjpa path) + *E,ELBERR → 分析
- U#14/U#19 (msg 14/19): more DLCSMD/RDUNCA (real_wrl_gen/internal_monitor_ref/error_injection/DCA_ADJUST_GLOBAL_CLK_monitor) + "我在...coverage_spf跑的,你说删除的内容是什么"

## Trace gold (assistant diagnosis)
1. **DLCSMD/RDUNCA** = Xcelium 增量编译缓存校验和不一致。改了 ddr5_package.sv (checksum 变)，但 import 它的模块(MRS_DQ_monitor/real_wrl_gen/internal_monitor_ref 等)旧缓存 VST 头里记录的依赖 checksum 仍是旧的 → ncelab 拒绝使用旧缓存 → DLCSMD + RDUNCA
   - DLCSMD = Dependent Library Checksum Mismatch Detected
   - RDUNCA = Read Unit Not Cached (Read During Caching Aborted)
   - 修复: `rm -rf INCA_libs xcelium.d xrun.history worklib/*.sv/* && recompile` (全量清理+重编)

2. **vsim -c no output** = `-c` 只创建 testbench 目录不跑仿真(静默无输出); 且 `–` 可能是 en-dash(U+2013) 非 ASCII hyphen 导致 Getopt::Long 不识别 → 参数全 undef → 零输出

3. **ICFNR** = Instrumentation Configuration File Not Readable. vsim 脚本 L1319 硬编码 `-covfile /proj/drvqa/V0/.../coverage_ccf.ccf`，用 `-p drjpa/V0` 时该路径不存在 → ELBERR
   - 修复: 建软链接 / 改脚本用 $tbproj 变量 / 删 -covfile 选项 / touch 空文件

## Case synthesis
- **提炼点**: U#0+U#12 合并 → ncelab 错误日志诊断脚本 (debug-Q&A→diagnose produce-task)
- **通用化**: diagnose_ncelab_errors.py <error_log> <output.json> → 结构化 JSON (10 字段)
- **A**: 真实 trace ncelab 日志 (DLCSMD ddr5_package→MRS_DQ_monitor/real_wrl_gen/internal_monitor_ref, RDUNCA tstrim_init/MRS_DQ_monitor/real_wrl_gen, ICFNR coverage_ccf.ccf drvqa, ELBERR)
- **hidden B**: 同构异值 (lpddr6_package, wr_ctrl_gen/rd_path_monitor/error_detect_unit, wrdq_path_init, drjpb/cov_setup.ccf)
- **check.py**: 17 断言 (25 assert statements), B-specific anti-hardcode + anti-leak A + §4.9 三假 FAIL
- **ref PASS 17/17 + 3neg全FAIL** ✓

## Intent-dup check
- r964 IsoLationUndeclDiagnoseQA (UNDIDN undeclared identifier) — 不同错误码，不同根因
- r968 IrunCofllxGenFailDiagnoseQA (COFILX cannot open include) — 不同错误码
- r969 CompErrRerunGen (编译错误 rerun 脚本生成) — 不同任务形态(生成 rerun 脚本 vs 诊断报告)
- r982 IrunWarnClassifyProduce (*W 告警分类) — 警告分类 vs 错误诊断
- 本 case: DLCSMD/RDUNDA/ICFNR/ELBERR 缓存校验和不一致诊断 — 独特错误码组合，无 intent-dup ✓
