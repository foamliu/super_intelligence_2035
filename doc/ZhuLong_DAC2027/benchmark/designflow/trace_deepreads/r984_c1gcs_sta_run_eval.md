# r984 deepread — c1gcs STA run evaluation

**session**: 1795160566075_c1gcs (e0046913@hfeg0pkn005, mc51)
**keywords**: netlist:243;primetime:36;pt_shell:29;synopsys:14;rtl:12;verilog:5 → A-pure pnr_signoff/STA
**trace**: 70 msgs / 6 user turns, scp 24KB

## User intent (verbatim)

- U#0 (M0): long STA flow requirements spec (流程概述: PrimeTime, netlist/sdc/lib, setup/hold/DRV/Glitch, 分析模式 best/worst, 裕量, SI/IR-drop, MVDD, CXDP Makefile 三阶段)
- U#1 (M19):「我针对脚本进行了修改，并新跑了sta任务。请评估本次sta运行结果，并评估脚本修改是否已满足设计需求。」
- U#2 (M38): same +「(先不关注设计收敛问题，而关注脚本问题)」
- U#3 (M51): same (3rd re-run)
- U#4 (M60):「根据现有脚本，结合需求规格书，为我写一份 CXDP STA flow SOP」
- U#5 (M62):「将以上SOP内容写进home目录，写为.md格式的文件」

## Session main line

CXDP STA auto-flow (PrimeTime) 评估 + SOP 生成. 用户贴需求规格书→assistant 读全套脚本(Makefile/sta.tcl/sta_setup.tcl/proc/0-10_*.tcl/script/sta_qa_chk.pl)+run产物→给出符合性评估+缺口. 用户3轮"改脚本+重跑+评估"循环, assistant 逐轮核查产物+脚本改动, 聚焦脚本问题(非设计收敛). 最后写SOP .md.

## Trace gold (key findings per round)

### Round 1 (M18): initial conformance assessment
- 框架完整度高, 4类缺口: ①Makefile run_pt pipefail→PT失败不跑post_process ②proc/9无resolved SDC/TWF ③proc/10 QA缺glitch/clock_type/signal_level ④sta_qa_chk.pl缺sdc/twf/session检查
- proc/5.4: read_sdc错误未进gating

### Round 2 (M37): 2nd run — perl BROKEN
- flow step 0-10全跑通, 产物齐全
- **QA/sta_qa_result 缺失** — sta_qa_chk.pl编译错: 用户删了`my $sdc_err`+`@cc`/check_constraints循环但L146仍用`$sdc_err`→`use strict`下未声明变量→编译期致命→perl从未执行→QA文件从未创建
- 改进A(PIPESTATUS捕获PT_RC+无条件post_process)✅, 改进C(proc/10 QA字段齐全)✅, 改进E(proc/4 SDC错误捕获)✅
- 违例: max_transition 1457 / max_fanout 400 / max_cap 36 / hold 6 (设计收敛, WL无wireload)

### Round 3 (M50): 3rd run — perl FIXED, QA generated
- **QA/sta_qa_result ✅ 生成** (perl修复: `my $sdc_err`已补, check_constraints扫描已恢复)
- RESULT: FAIL (transition/fanout/hold), PASS: SDC errors clean
- sdc_read_errors: 0, warnings: 4 (UITE-121/136)
- twf_generated: 0 (session兜底), resolved_sdc ✅, timing_report ✅
- **仍存健壮性问题**:
  1. count_constraint_violations格式敏感: 前导`-`的check名(如`- min_capacitance`)被漏计
  2. report_drv_all充斥`min_capacitance: Slack 0.000 (VIOLATED: increase significant digits)`精度伪影
  3. TWF仍未独立生成
  4. GCA check_constraints DES-001白名单豁免

### Round 4 (M59): 4th run — proc/10 fixed
- proc/10_qa.tcl采纳建议①: clock_tran/clock_type改用step-08独立报告(report_clock_tran/report_clock_type)的count_violated_lines, 不再依赖report_drv_all块解析
- proc/10_qa.tcl采纳建议②: count_violated_lines加`&& ![regexp ... {increase significant digits}]`过滤精度伪影
- 建议③TWF仍未落地
- 脚本层面已满足设计需求, QA门/SDC错误门/交付物产出与判定全部正常

## Case reframe (produce-task)

提炼U#2核心意图: 给定STA run产物+脚本, 产生结构化评估JSON.

**evaluate_sta_run.py <run_dir>** → JSON:
1. 解析QA/sta_qa_result → verdict(PASS/FAIL), fail_categories
2. 解析QA/qa_summary.txt → violation_counts, sdc_read_errors, twf/session/deliverable flags
3. 解析report/report_drv_all.report → 假违例伪影检测("increase significant digits"行数)
4. 静态分析script/sta_qa_chk.pl → use strict下未声明变量检测(perl_compiles)
5. 静态分析run/proc/10_qa.tcl → clock_tran/clock_type来源(step08独立 vs report_drv_all块解析), increase_significant_digits过滤是否存在

**A (visible, 3rd run state)**: perl fixed, QA generated FAIL(transition/fanout/cap/hold), proc/10仍用report_drv_all块解析, count_violated_lines无精度伪影过滤
**Hidden B (4th run state)**: perl fixed, QA generated FAIL(setup/hold, 不同计数), proc/10改用step-08独立报告, count_violated_lines有精度伪影过滤

## 选料注

- r963 scan池, _a_dom_cands_r963.tsv broadened filter (A>0, A>=C) 得29 fresh, 排除intent-dup(rose3wang bltup/lq85o/ibtdi/whuon/y3hlf=ciw0o+elb1i+9ofdu dup; guomings ewjfi/le2ke等=r971+r975 dup; e0039102 iehz0/v7a78=r976 dup), c1gcs(e0046913 mc51 primetime/pt_shell STA pnr_signoff A域, NEW user)选中
- 与r983 kvz8n(ethanw verification ncelab cache)无intent-dup(不同用户不同域: STA flow评估 vs ncelab cache诊断)
