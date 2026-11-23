# Deepread stub: fwzs7 — nevinrao SV checker diagnosis (r1082)

**Session**: 1795413599900_fwzs7.messages.json
**User**: nevinrao @ hfeg0pkn004 (10.129.2.13)
**mc**: 142 | **msgs**: 105 | **keywords**: verilog:1247;systemverilog:207;cmos:46;analog:5;synopsys:1;rtl:1;pex:1;cadence:1
**Domain**: verification (A-pure, SV checker analysis)
**trace_source**: {user: nevinrao, host: hfeg0pkn004, session_file: 1795413599900_fwzs7.messages.json, match_count: 142, real_task_summary: SV auto-check checker diagnosis — determine which check failures are real vs false}

## User intent (msg[0])
用户有 tm_auto_check_checker.v 文件（autocheck checker），其中有些检查可以采纳，有些错误的需要进一步确定。具体错误示例：
```
At time 1004181179, cm1_ag_VcslBiasAct_m check failed! channelif...trim_monitors[151][493][[1:0]] is 1, cm1_ag_VcslBiasAct_m is 1 , I_TM_VCSLBIASACT_13
```
用户想让 agent 分析 checker 文件，判断哪些 check 是正确的、哪些有错误需要修正。

## Key observations (from msg[0]-[3])
- checker 文件路径: /rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.blocknew/patterns/proj_function/cmds_tmscan/out_files_special/tm_auto_check_checker.v
- 文件结构: 每个 checker module 用 `bind` 绑定到 DUT instance
- 例: `bind CaEnCtrl hdl_TM_ENOSCOUT_0 I_TM_ENOSCOUT_0 (.cm0_io_EnOscOut_m(cm0_io_EnOscOut...))`
- 用户关注 cm1_ag_VcslBiasAct_m 的 check failure

## VIABLE for case synthesis (r1083)
- **形态**: diagnosis-Q&A (A-domain verification, 合法真实意图 per 11-15 令)
- **交付**: diagnosis.md (逐 checker 判定 pass/fail/needs-fix + 理由) + verify_diagnosis.py (泛化解析 checker.v → 结构化判定)
- **hidden-B**: 不同 checker instance 集 (不同 bind 目标 + 不同错误模式)
- **k≥8**: 每个 checker 分类 = 1 独立断言
- **自包含**: tm_auto_check_checker.v 作为 attachment (需 scp)
- **A-pure**: verilog:1247+systemverilog:207 dominant (90%+), 纯 verification

## Next steps (r1083)
1. scp tm_auto_check_checker.v from 10.129.2.13 (nevinrao) 或找 .75 上的副本
2. 完整深读 105 msgs (user 后续反馈 + agent 分析结论)
3. 合成 case: assets/A/ + reference/ + hidden/ + negative/ + check.py
4. 自验 + pi 实跑
