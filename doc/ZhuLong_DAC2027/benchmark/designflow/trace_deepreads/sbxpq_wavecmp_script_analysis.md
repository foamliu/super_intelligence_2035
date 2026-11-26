# Deepread — sbxpq: 波形对比两脚本分析 Q&A (code-grounded script-analysis)

**Session**: `1792473479665_sbxpq` | **User**: rongjiez | **Host**: hfeg0plg98 (10.129.8.230)
**mc**: 20 | **Domain**: schematic_netlist | **Agent**: lead | **NMSG**: 198
**旧判定**: parked (r612) "Q&A analyze two copied scripts testcase_copy/run.sh (analysis, not produce)"
**11-15 revival**: ✅ 复活 — 真实用户意图=code-grounded script-analysis Q&A，单轮闭环可造

## 1. 用户原话（A档 verbatim U#0）
> @testcase_copy.sh @testcase_run.sh 这两个脚本是从别人拷贝过来的，帮我分析一下这两个脚本

后续轮 U#17（怎么用 testcase_copy.sh）/ U#27（link 文件修改是否影响源）/ U#37（重写脚本：大文件 link 小文件 copy）为延伸，本 case 取单意图 U#0。

## 2. 金标准（assistant A#16, 5521 字符）
两脚本 = LSF 波形对比批量测试框架：
- **testcase_copy.sh**: 从 MatrixRun 源目录挑"合格 case"（需同时有 compare.rep/raw/finesim.fsdb/config_pincheck/pincheck），在目标目录建精简环境（raw/config_pincheck/compare.rep 软链, pincheck 拷贝）。
- **testcase_run.sh**: 遍历目标目录每个含 pincheck 的子目录，`bsub -q pincheck pincheck` 提交 LSF 作业。
- 5 类问题：①NEW_PATH 硬编 yanxvwei 路径 ②sed 替换 pincheck 路径被注释掉（核心）③cd 在 mkdir 之前（相对路径坑）④MAX_CASES=100 上限 ⑤bsub 返回 0 仅表提交成功非作业成功。

## 3. 资产可达性
原脚本在 10.129.8.230:/home/rongjiez/jira_dev/compare_wave/testcase/，经 .75 eda_flow ssh 可达。但会话内已被 agent 编辑（U#22/U#23/U#40/U#41）。**asset A = 从 trace read_query 结果重建原始未修改版**（testcase_copy.sh 原始: NEW_PATH=yanxvwei + sed 注释 + cd-before-mkdir + ln -s; testcase_run.sh 原始未编辑, msg#62 74 行 verbatim）。

## 4. 落库
**Case ID**: EDA-Eval-DesignFlow-WaveCmpScriptAnalysisQA-001
**candidate.py**: 通用 bash 两脚本分析器（无硬编码标识符, 检 hardcoded_path/patch_sed_disabled/cd_before_mkdir/case_cap/scheduler_return_not_job_success + symlink_targets/arg_checks/scheduler）→ 8 顶层键 JSON。
**hidden B**: wavebuild_clone.sh + wavebatch_launch.sh（identifier-renamed: yanxvwei→mincheol, WaveformCompare→WaveDiffTool, compare_wave→diffwave, pincheck→signalcheck, bsub→jsub, LSF→SGE, PIPESTATUS→pipeline_status, MAX_CASES→CASE_CAP, 等；同 5 类问题结构；零 A 标识符重叠）。
**check.py**: 12 断言 a-l，re-run on hidden B + anti-hardcode(23 A-only token word-boundary) + 3-run md5 确定性。
**自验**: ref 12/12 PASS + 5neg FAIL distinct labels(empty→b / print_only→d / core_deleted→f / hardcode_a→g / naive→f) NEG_RC=0 + §4.9 三退化全 FAIL + test==disk byte-sync + candidate on A 产 yanxvwei/bsub(A 专属) 与 B 输出 mincheol/jsub 不同(非 canned)。
**D.jsonl**: 454→455。**k_rationale=k_check=12≥8 GATE PASS**。
