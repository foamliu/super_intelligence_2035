#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os

with open('MEMORY_DESIGNFLOW_B.md','r',encoding='utf-8') as f:
    lines = f.readlines()

# r834 verbose is line index 36
r834_verbose = lines[36]
assert r834_verbose.startswith('- r834 **'), f"line 36 not r834 verbose: {r834_verbose[:60]}"

# Append r834 verbose to ARCHIVE
with open('ARCHIVE_OPERATOR_DESIGNFLOW_B.md','a',encoding='utf-8') as f:
    f.write('\n\n## r834 verbose原文 (r835-mem-trim 移入)\n\n')
    f.write(r834_verbose if r834_verbose.endswith('\n') else r834_verbose+'\n')

# r833 dup verbose is line index 38
r833_dup = lines[38]
assert r833_dup.startswith('- r833 **'), f"line 38 not r833 verbose: {r833_dup[:60]}"
assert lines[37].startswith('- [r833 archived]'), f"line 37 not r833 archived: {lines[37][:60]}"

r834_pointer = (
    "- [r834 archived] 11-18 r834 0-case + 档3 reframe_note backfill batch9 +12 落地"
    "（mc-matrix 1115_081559: mc>=10 池 943/已动 943/fresh=0 第 205 轮 reconfirm; "
    "reframe_note 331→343, miss 64→52; batch9 R→S 段 RcVizTreeAnalyzer→SarAdc8bNetlistGen, "
    "7 keep_reframe portability + 1 keep_reframe harness + 4 keep_faithful(含 1 WAVEVIEW restored-image β7 RiseEdgeMarginMeas); "
    "**harness-driver from-scratch generation 亚型首实证** SarAdc8bNetlistGen; "
    "**harness-driver 三亚型全实证**(file→script + multi-round→single + from-scratch generation); "
    "R 段 keep_faithful 33% hetero + characterization 域回流 42%; "
    "§4.9 抽查 RonMonoDiag-001 6 neg 全 FAIL ref PASS NEG_RC=0）原文滚入 ARCHIVE (r835-mem-trim)\n"
)

r835_verbose = (
    "- r835 **0-case 维持轮 + 档3 reframe_note backfill batch10 +12 落地**"
    "（mc-matrix --shard B --src summary_1115_081559: mc>=10 池 943/已动 943/fresh=0 **第 206 轮 reconfirm** 四快照结构性饱和 ⇒ 0-case; "
    "discuss r834→r835 diff=1<4 不发言, 下次 mandatory due r837; "
    "reframe_note backfill batch10 = alphabetical 续 12 missing after SarAdc8bNetlistGen 起算 SenseMarginAnalysis S 段"
    "(SenseMarginAnalysis/ShmooCfgParser/SimConfigEditReport/SimModelMismatchDiag/SimProgressCheck/SimResultGrep/"
    "SimSavedCornerComplete/SimStatusMonitor/SlicerDmMeasAdd/SlicerFbTimeOpt/SlicerSweepFomOpt/SnmAnalyzerExplain-001-v2), "
    "driver 三分 9 keep_reframe portability + 2 keep_reframe Q&A-analysis + 1 keep_faithful; "
    "9 portability: 6 synth_data(SenseMarginAnalysis real PrimeSim/Finesim 960 .bisec_mt0 不可复刻 / "
    "ShmooCfgParser real tr0 波形+Perl 项目路径不可复刻抽 cfg-parse 子技能 / "
    "SimConfigEditReport real config.yaml 含项目 model_lib 路径不可复刻 / "
    "SimResultGrep real /proj MatrixRun 目录不可 scp 便携 **track=faithful 但 asset=synth_data mismatch 待@A** / "
    "SimSavedCornerComplete real /proj sim.saved.total 含项目路径不可 scp 便携 **track=faithful 但 asset=synth_data mismatch 待@A** / "
    "SimStatusMonitor real FineSim MatrixRun 目录+finesim.log 不可复刻->synth_log / "
    "SlicerSweepFomOpt real FineSim .mt0.csv sweep 结果不可复刻) + 3 synth_deck(SlicerDmMeasAdd real /proj/dscqa strongarm_tb_cm.sp 不可复刻 **track=faithful 但 asset=synth_deck mismatch 待@A** / SlicerFbTimeOpt real 01_slicer_tran_DECQA.sp+IO_DqIbSADoubleTail netlist 不可复刻 **track=faithful 但 asset=synth_deck mismatch 待@A**); "
    "2 Q&A-analysis: SimModelMismatchDiag(原 '你分析一下我那里错了' 纯分析->produce diagnostic_report.json, asset=A-faithful real DSPF/stimulus/HSPICE error log 文本便携) / "
    "SnmAnalyzerExplain-001-v2(原 '处理 HSNM/RSNM/统计结果的逻辑是什么' 纯 explain->produce snm_explanation.json 结构化 schema, A=trace-verbatim mc_snm_analyzer.py 761 行便携, hidden-B=synthesized 8T vs 6T cross-input, **v2 case 来自 11-15 reaudit 重做**); "
    "1 keep_faithful: SimProgressCheck(用户显式要 '执行 check_sim 查看仿真进度' produce-action, real corner_stb 目录+Perl cxmt_check_sim→Python 改写 trace-verbatim 便携, asset=A-faithful, track=faithful); "
    "复用 r834 档3 脚本模式(_metadata_backfill_tier3_reframe_note_r835.py, reframe_note 末位 key 保留键序, indent=2 ensure_ascii=False, 不动 test_rationale/check.py/negative/asset_fidelity); "
    "**存储架构**: cases/B single source of truth, build_jsonl.py --shard B 本地 rebuild reframe_note 343→355 == B.jsonl 395 case rebuild ✓ 0 起数据丢失 12/12 applied 0 skipped, B.jsonl gitignored 不入 commit; "
    "**S 段 domain-wave 新发现**: keep_faithful 占比 8%(1/12) 与 batch8 P段 8% 持平, 因 S 段 Sim*/Slicer* 群多为 real sim dir/deck/log/.mt0 不可沙盒复刻→portability-heavy 75%(9/12), "
    "Q&A-analysis 17%(2/12: SimModelMismatchDiag 诊断 + SnmAnalyzerExplain explain) 反映 S 段含 diagnosis/explain 真实用户意图子群; "
    "S 段 spice_sim 域占比 83%(10/12, 仅 ShmooCfgParser/SimSavedCornerComplete 为 characterization), 显著高于 batch9 R段 42% characterization, S 段是 spice_sim 域主流段; "
    "**track≠asset_provenance mismatch 累计**: batch10 内 4 例(SimResultGrep/SimSavedCornerComplete track=faithful asset=synth_data; SlicerDmMeasAdd/SlicerFbTimeOpt track=faithful asset=synth_deck), r834 累计 57→61 待 @A 档2 sweep; "
    "**v2 case 1 例**(SnmAnalyzerExplain-001-v2 来自 11-15 reaudit 重做); "
    "**metadata bug 待 @A**: 多 case layer 标 L2 待复核(若 check 仅 subprocess 跑候选 python 解析文本 0 EDA 二进制应 L1) + k_check/k_rationale 缺标应补(8 case) + track 缺标(3 case) + shard 缺标(全 12); "
    "§4.9 抽查 SimSavedCornerComplete-001 5 neg(fake_empty/fake_print_expected/fake_hardcode_B/fake_wrong_count/fake_dup_existing) 全 FAIL + ref check PASS True NEG_RC=0; "
    "下轮 r836 reframe_note backfill batch11(SnmButterflyCalc 起算 S 段续, miss 40→~28)）\n"
)

# Surgery:
# - Replace line 36 (r834 verbose) with r835_verbose + r834_pointer
# - Keep line 37 ([r833 archived] pointer)
# - Remove line 38 (r833 dup verbose)
# - Keep lines 39+ ([r832 archived] etc.)
new_lines = lines[:36] + [r835_verbose, r834_pointer] + lines[37:38] + lines[39:]

with open('MEMORY_DESIGNFLOW_B.md','w',encoding='utf-8') as f:
    f.writelines(new_lines)

sz = os.path.getsize('MEMORY_DESIGNFLOW_B.md')
print(f"MEMORY_B size after trim+add: {sz} B ({sz/1024:.1f} KB)")
txt = open('MEMORY_DESIGNFLOW_B.md').read()
print("r835 present:", "- r835 **0-case" in txt)
print("r834 pointer present:", "[r834 archived]" in txt)
print("r833 dup verbose removed:", txt.count("- r833 **0-case") == 0)
print("r833 archived pointer kept:", "[r833 archived]" in txt)
