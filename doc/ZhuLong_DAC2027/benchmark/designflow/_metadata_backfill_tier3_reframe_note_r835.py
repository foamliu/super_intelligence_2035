#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r835 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch10.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        r830 batch5 +12 (283->295, miss 112->100).
        r831 batch6 +12 (295->307, miss 100->88).
        r832 batch7 +12 (307->319, miss 88->76).
        r833 batch8 +12 (319->331, miss 76->64).
        r834 batch9 +12 (331->343, miss 64->52).
        本轮 batch10 = alphabetical 续 12 missing after SarAdc8bNetlistGen (r834 batch9 末位),
        起算 SenseMarginAnalysis, S 段.
        reframe_note 343->355, miss 52->40.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r835 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch10 12 case = 9 keep_reframe portability + 2 keep_reframe Q&A-analysis + 1 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe portability + 2 keep_reframe Q&A-analysis + 1 keep_faithful):
  - portability-driver (real sim dir/deck/.mt0/.md0/.bisec_mt0/log/config 不可沙盒复刻 -> synth_*):
      9 case: SenseMarginAnalysis (real PrimeSim/Finesim 960 .bisec_mt0 仿真输出不可沙盒复刻->synth_data, spice_sim, L2) /
              ShmooCfgParser (real tr0 波形+cxmtGen2DShmooFromWv.pl 项目路径不可复刻, 抽 cfg-parse 子技能->synth_data, characterization, L1) /
              SimConfigEditReport (real config.yaml 含项目 model_lib 路径不可复刻->synth_data config+edit_plan, spice_sim, L1) /
              SimResultGrep (real /proj MatrixRun 目录不可 scp 便携->synth_data fixture, spice_sim, L1; **track=faithful 但 asset=synth_data mismatch 待 @A**) /
              SimSavedCornerComplete (real /proj sim.saved.total 含项目路径不可 scp 便携->synth_data fixture, characterization, L1; **track=faithful 但 asset=synth_data mismatch 待 @A**) /
              SimStatusMonitor (real FineSim MatrixRun 目录+finesim.log 不可复刻->synth_log fixture, spice_sim, L1; track=synthesized) /
              SlicerDmMeasAdd (real /proj/dscqa strongarm_tb_cm.sp deck 不可复刻->synth_deck, spice_sim, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              SlicerFbTimeOpt (real 01_slicer_tran_DECQA.sp+IO_DqIbSADoubleTail netlist 不可复刻->synth_deck, spice_sim, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              SlicerSweepFomOpt (real FineSim .mt0.csv sweep 结果不可复刻->synth_data, spice_sim, L2)
  - Q&A-analysis-driver (原 trace 为 analysis/explain/Q&A, reframe 为 produce-report 加 §4 牙):
      2 case: SimModelMismatchDiag (原 '你分析一下我那里错了' 纯分析, reframe->produce diagnostic_report.json, asset=A-faithful real DSPF/stimulus/HSPICE error log 文本便携, spice_sim, L1) /
              SnmAnalyzerExplain-001-v2 (原 '处理 HSNM/RSNM/统计结果的逻辑是什么' 纯 explain, reframe->produce snm_explanation.json 结构化 schema, A=trace-verbatim mc_snm_analyzer.py 761 行便携, hidden-B=synthesized 8T vs 6T cross-input, spice_sim, L1; **v2 case** 来自 11-15 reaudit 重做)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      1 case: SimProgressCheck (用户显式要 '执行 check_sim 查看仿真进度' produce-action, real corner_stb 目录+Perl cxmt_check_sim→Python 改写 trace-verbatim 便携, asset=A-faithful, track=faithful, spice_sim, L1)

S 段 domain-wave 观察: batch10 keep_faithful 占比 8%(1/12) 显著低于 batch7 N段 50%, 与 batch8 P段 8% 持平,
  因 S 段 Sim*/Slicer* 群多为 real sim dir/deck/log/.mt0 不可沙盒复刻 -> portability-heavy (9/12=75% portability);
  Q&A-analysis 2/12=17% (SimModelMismatchDiag 诊断 + SnmAnalyzerExplain explain) 反映 S 段含 diagnosis/explain 真实用户意图子群;
  S 段 spice_sim 域占比 10/12=83% (仅 ShmooCfgParser/SimSavedCornerComplete 为 characterization), 高于 batch9 R段 42% characterization,
  S 段是 spice_sim 域主流段.
  track≠asset_provenance mismatch 累计: batch10 内 4 例(SimResultGrep/SimSavedCornerComplete track=faithful asset=synth_data; SlicerDmMeasAdd/SlicerFbTimeOpt track=faithful asset=synth_deck), r834 累计 57 -> 61 待 @A 档2 sweep.
  v2 case 1 例(SnmAnalyzerExplain-001-v2) 来自 11-15 reaudit 重做, 与 r740 等历史 v2 同类.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 标 L2 待复核(若 check 仅 subprocess 跑候选 python 解析文本 0 EDA 二进制应 L1): SenseMarginAnalysis/SlicerDmMeasAdd/SlicerFbTimeOpt/SlicerSweepFomOpt
  - k_check/k_rationale 缺标应补(SenseMarginAnalysis=12/SimConfigEditReport=15/SimModelMismatchDiag=13/SimResultGrep=14/SimSavedCornerComplete=17/SimStatusMonitor=15/SlicerFbTimeOpt=14/SlicerSweepFomOpt=13)
  - track 缺标应补(SenseMarginAnalysis/SimModelMismatchDiag/SlicerSweepFomOpt track=None 应 synthesized; SimProgressCheck track=faithful 已标 ✓)
  - shard 缺标应 B (全 12 case shard=None)
  - track≠asset_provenance mismatch 4 例(SimResultGrep/SimSavedCornerComplete/SlicerDmMeasAdd/SlicerFbTimeOpt track=faithful 但 asset=synth_*)
  - 与 r773-r800/r826-r834 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-SenseMarginAnalysis-001":
        "DRAM Sense Margin (SM) characterization pipeline: 12 BLs × 5 tOC × 2 cell × 8 pattern=960 .bisec_mt0 仿真+vtarget parse+BL 汇总统计+tOC low-envelope+最优 tOC 选取->produce (portability-driver reframe, real PrimeSim/Finesim 960 .bisec_mt0 仿真输出不可沙盒复刻->synth_data, §4 有牙必要, r835 reframe_note backfill batch10): 用户 e0025730@hfeg0plg49 (sess 1787646109879_mwyd9, mc=82, spice_sim 域) 在 CXMT DRCOA 产品上用 PrimeSim/Finesim 跑 960 个 .bisec_mt0 仿真, 调 /sense-margin-test skill 做结果抽取: 从每个 .bisec_mt0 读 vtarget, 按 BL 汇总统计、按 tOC 算 low-envelope、挑使最差情形 SM 最大的最优 tOC; A 不可行原因=real 960 .bisec_mt0 PrimeSim/Finesim 仿真输出不可沙盒复刻(数量+体积+项目路径) -> 收敛为 sm_analysis.py(读 hidden B synth .bisec_mt0 群, asset_fidelity=synth_data); reframe 由 portability-driver(real 960 .bisec_mt0 不可复刻); 意图核心(vtarget parse + BL 汇总统计 + tOC low-envelope + 最差情形 SM + 最优 tOC 选取 + results.json 含 bl_stats/toc_lowenv/optimal_toc)完整保留; check.py 12 断言验 zip 含 sm_analysis.py + results.json 含全部顶层键 bl_stats/toc_lowenv/optimal_toc/bl_names/toc_names + 候选在 hidden B 上 exit0 + cross-input guard(A≠B .bisec_mt0 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 解析 .bisec_mt0 文本 0 EDA 二进制应 L1), level 缺标, k_rationale/k_check 缺标应 12, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-ShmooCfgParser-001":
        "2D Shmoo 流程 shmoo.cfg 解析函数 parse_shmoo_cfg(Perl getInfoFromCfgFile 口径: key=value/Signal 逗号→冒号/大小写不敏感/多行收集/Wave_Path 剥引号)->produce (portability-driver reframe, real tr0 波形+cxmtGen2DShmooFromWv.pl 项目路径不可复刻, 抽 cfg-parse 子技能->synth_data, §4 有牙必要, r835 reframe_note backfill batch10): 用户 yanxvwei@hfeg0pkn002 (sess 1792630397654_fyfm9, mc=54, characterization 域) 在 2D Shmoo 流程(cxmtGen2DShmooFromWv.pl)多轮演进: 先问 cfg 怎么写、排查 Excel 中空、写 tr0_to_wvshmoo.py(读 tr0 生成 wv_shmoo.txt), U#185 要求使其能吃 shmoo.cfg; 本 case 取该轮把 read_cfg() 重构成通用 parse_shmoo_cfg(cfg_text); A 不可行原因=real tr0 二进制波形+Perl 脚本 /apps/imctf 项目路径不可沙盒复刻, 抽 cfg-parsing 子技能(纯文本 cfg 便携但原 workflow 不可整体复刻) -> 收敛为 cfg_parser.py(读 hidden B synth shmoo.cfg, asset_fidelity=synth_data); reframe 由 portability-driver(real tr0/Perl workflow 不可复刻, 子技能提取); 意图核心(key=value parse + # 注释 + key 大小写不敏感 + Signal 逗号→冒号去空格 + 多行按序收集 + Wave_Path 剥引号 + A2D_Vth/CL 等键)完整保留; check.py 21 断言验 zip 含 cfg_parser.py 且可导入 + parse_shmoo_cfg 可调用 + parse(B1) 返回 dict + B1 signals 精确匹配(逗号→冒号/去空格/顺序保留) + cross-input guard(A≠B cfg 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 解析 cfg 文本 0 EDA 二进制), level 缺标应 L1, k_check=21==k_rationale=21 ✓, track=synthesized 一致 asset=synth_data ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SimConfigEditReport-001":
        "SPICE 仿真 config.yaml 编辑器+变更审计器(mode/duration/step/vdd/temp/corner/measure/model_lib set|remove, dotted path, 逐条应用, from→to 留痕)->produce (portability-driver reframe, real config.yaml 含项目 model_lib 路径不可复刻->synth_data config+edit_plan, §4 有牙必要, r835 reframe_note backfill batch10): 用户 e0023936@hfeg0pkn004 (sess 1794290403498_45msy, mc=42, spice_sim 域) 分多轮请求修改 SPICE 仿真 config.yaml: transient→DC、VDD 1.2→1.0、duration 100ns→50ns、temp 25→85, 最后要求参数变更汇总(每参数 from→to); 本 case 抽通用 sim_config_editor.py; A 不可行原因=real config.yaml 含项目 model_lib/corner 路径不可沙盒复刻 -> 收敛为 sim_config_editor.py(读 hidden B synth config.yaml+edit_plan.json, asset_fidelity=synth_data); reframe 由 portability-driver(real config 含项目路径不可复刻); 意图核心(YAML 读 + dotted path set|remove 逐条应用 + 中间状态留痕 + out_config.yaml + out_report.json 变更审计 from→to)完整保留; check.py 15 断言验 zip 含 sim_config_editor.py + py_compile + 候选在 hidden B1 上 exit0 产 out_config.yaml+out_report.json + out_config 合法 YAML + out_report 含每参数 from→to + cross-input guard(A≠B config/edit_plan 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 编辑 YAML 文本 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 15, track=synthesized 一致 asset=synth_data ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SimResultGrep-001":
        "仿真结果抓取脚本 result_grep(-result 抓 zzresult* 最新一个输出 zzresult_YMD.list / -path 抓 MatrixRun* folder 输出 allpath_YMD.list, 绝对路径)->produce (portability-driver reframe, real /proj/drcpa MatrixRun 目录不可 scp 便携->synth_data fixture, §4 有牙必要, r835 reframe_note backfill batch10): 用户 tzuo@hfhds201 (sess 1791448400305_kwiij, mc=49, spice_sim 域) USER#0 verbatim「写一个脚本实现仿真路径下到结果抓取…起名叫 result_grep, 规则: 1. -result 选项 抓取当前 path 下所有 folder 内的 zzresult* 文件, folder 内可能存在多个只抓最新一个, 输出到 zzresult_YMD.list, 绝对路径 2. -path 选项 抓取所有 MatrixRun* folder 输出 allpath_YMD.list」——纯需求轮, A-档①合规(verbatim 用户原话); A 不可行原因=real /proj/drcpa/V0/simdir/finesim/drcpaF/MatrixRun 目录不可 scp 便携(项目 /proj 路径沙盒无法访问) -> 收敛为 result_grep.py(扫 hidden B synth MatrixRun fixture, asset_fidelity=synth_data); reframe 由 portability-driver(real /proj MatrixRun 目录不可 scp); 意图核心(-result 抓 zzresult* 最新一个 + -path 抓 MatrixRun* folder + YMD 命名 + 绝对路径输出 + 无参/未知选项非零退出)完整保留; check.py 14 断言验 zip 含可执行 python + py_compile + 无参数非零退出 + 未知选项非零退出 + -result 在 hidden B exit0 产 zzresult_YMD.list + -path 产 allpath_YMD.list + cross-input guard(A≠B fixture 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 扫目录 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 14, **track=faithful 但 asset=synth_data mismatch**(track≠asset_provenance, real /proj 目录不可便携故 asset=synth_data, track 应为 synthesized 或 asset 应标注 hidden-B-fixture-synth), shard 缺标应 B。**注**: 本 case 用户原话 verbatim A-档①, 脚本逻辑 track=faithful(与 trace 同形), asset=synth_data 仅因 real /proj 目录不可 scp 便携作 hidden-B fixture, 区别 real 仿真输出内容不可复刻的 synth_data reframe。",

    "EDA-Eval-DesignFlow-SimSavedCornerComplete-001":
        "DDR5 DRVQA sim.saved.total PVT corner 补全(每 case 应 5 corner, 缺失补全, 多出行输出 sim.saved.total.zl, 相同 corner 不同电压温度前方相同)->produce (portability-driver reframe, real /proj sim.saved.total 含项目路径不可 scp 便携->synth_data fixture, §4 有牙必要, r835 reframe_note backfill batch10): 用户 ynbai@hfhds201 (sess 1794018867939_1qlnn, mc=2736, characterization 域) USER#0 verbatim「识别…sim.saved.total 文件, 内容例如[5 行 case+corner 路径]…每一个 case 应该都有 5 个, 但是文件不全, 部分不是五个, 帮忙补全, 补全文件生成为 sim.saved.total.zl, 相同 corner 不同电压温度下前方相同」+ USER#1「多出来的 case 行输出到 sim.saved.total.zl」; A 不可行原因=real /proj/drvqa sim.saved.total 含项目路径不可 scp 便携 -> 收敛为 sim_saved_corner_complete.py(读 hidden B synth sim.saved.total fixture, asset_fidelity=synth_data); reframe 由 portability-driver(real /proj 路径不可 scp); 意图核心(每 case 5 corner 检测 + 缺失补全 + 多出行分流 sim.saved.total.zl + PVT 5 expected(FF1.3v110C/FF1.3v-40C/TT0.94v25C/SS0.78v110C/SS0.78v-40C) + 行格式 <path> <PVT> X<4|8>)完整保留; check.py 17 断言验 zip 含 .py + py_compile + 无参数非零退出 + hidden B exit0 产 output + 每行格式 <path> <PVT> X<4|8> + PVT ∈ 5 expected + cross-input guard(A≠B fixture 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 补全文本 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 17, **track=faithful 但 asset=synth_data mismatch**(track≠asset_provenance, real /proj 路径不可便携故 asset=synth_data, track 应为 synthesized 或 asset 应标注 hidden-B-fixture-synth), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SimStatusMonitor-001":
        "FineSim MatrixRun 批量仿真状态监控(finesim.log 解析 banner/Completed/ires=/ERROR/WARNING + .mt0/.tr0/.pt0/.lock 检查, 归类 COMPLETED_SUCCESS/COMPLETED_ERROR/RUNNING/STALLED + summary)->produce (portability-driver reframe, real FineSim MatrixRun 目录+finesim.log 不可复刻->synth_log fixture, §4 有牙必要, r835 reframe_note backfill batch10): 用户 xinweif@hfeg207 (sess 1792031615605_mf0l3, mc=15, spice_sim 域)「可以帮助我监控这个路径下的仿真状态吗, 看看是否退出」; A 不可行原因=real FineSim MatrixRun 批量仿真目录+finesim.log 内容不可沙盒复刻 -> 收敛为 sim_status_monitor.py(扫 hidden B synth_log rundir fixture, asset_fidelity=synth_log); reframe 由 portability-driver(real MatrixRun 目录+finesim.log 不可复刻); 意图核心(扫 case 子目录 + finesim.log parse banner/Completed/ires=/ERROR/WARNING + .mt0/.tr0/.pt0 产出 + .lock 检查 + 四态归类(COMPLETED_SUCCESS/COMPLETED_ERROR/RUNNING/STALLED) + report.json 含每 case 字段+summary 计数 + WARNING 不翻 SUCCESS)完整保留; check.py 15 断言验 zip 含 sim_status_monitor.py + py_compile + 候选在 hidden B rundir 上 exit0 产 report.json + report schema 完整(cases 列表+每 case 含 case/status/exit_code/log_completed 等字段) + summary 计数 + cross-input guard(A≠B fixture 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 扫目录+parse log 文本 0 EDA 二进制), k_rationale/k_check 缺标应 15, track=synthesized 一致 asset=synth_log ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SlicerDmMeasAdd-001":
        "StrongARM comparator strongarm_tb_cm.sp 加 .measure dm 语句(双测量 dm 上升/下降 delay 注入, /proj/dscqa FineSim deck)->produce (portability-driver reframe, real /proj/dscqa strongarm_tb_cm.sp deck 不可复刻->synth_deck, §4 有牙必要, r835 reframe_note backfill batch10): 用户 jiangbaol@hfeg0pkn002 (sess 1793932002608_suauw, mc=113, spice_sim 域) USER#11 verbatim A-档「/proj/dscqa/V0_LP6/.../004_onlySlicer...strongarm_tb_cm.sp」要求加 .measure dm 测量; A 不可行原因=real /proj/dscqa strongarm_tb_cm.sp FineSim deck 不可沙盒复刻(项目 /proj 路径) -> 收敛为 add_dm_meas.py(读 hidden B synth deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck 不可复刻); 意图核心(读 deck + 注入 .measure dm 上升/下降 delay 语句 + 输出 *_cmdm.sp 行数 > 源 .sp)完整保留; check.py 12 断言验 zip 含 add_dm_meas.py + py_compile + --help 打印用法 exit0 + 在可见 A 上生成 *_cmdm.sp 且行数 > 源 .sp + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 注入文本 0 EDA 二进制应 L1), level 缺标, k_check=12==k_rationale=12 ✓, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real /proj deck 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SlicerFbTimeOpt-001":
        "FineSim slicer t0/t1_feedbacktime 优化(改网表 mos 参数+仿真迭代, t0/t1<60ps, I_total 越小越好, 双尾 slicer DECQA)->produce (portability-driver reframe, real 01_slicer_tran_DECQA.sp+IO_DqIbSADoubleTail netlist 不可复刻->synth_deck, §4 有牙必要, r835 reframe_note backfill batch10): 用户 cynthiaz@hfeg0pkn005 (sess 1793870063634_h15ge, mc=193, spice_sim 域) 给 FineSim 仿真激励 01_slicer_tran_DECQA.sp 与 IO_DqIbSADoubleTail_DECOA_schematic.netlist, 要求把 t0/t1_feedbacktime 做到 60ps 以下、I_total 越小越好, 方法=直接改网表 mos 管参数+仿真迭代优化(队列 fqueue3_io); A-档②合规(用户给需求+方法未给根因/修复); A 不可行原因=real FineSim deck+netlist 不可沙盒复刻(项目路径) -> 收敛为 slicer_fbtime_opt.py(读 hidden B synth deck+params, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck+netlist 不可复刻); 意图核心(slicer sizing sweep + HSPICE 真跑 + t0/t1_feedbacktime <60ps 约束 + I_total 最小 + best_config 选取 + opt_result.json)完整保留; check.py 14 断言验 zip 含 slicer_fbtime_opt.py + py_compile + 候选脚本接受 3 参签名(src_sp,params,out_dir) + B 的 opt_result.json 含必需键(best_config/best_t0/best_t1) + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制应 L1; 若真跑 HSPICE 则 L2), level 缺标, k_rationale/k_check 缺标应 14, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real deck 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SlicerSweepFomOpt-001":
        "DDR4 DFE slicer doubletail_nmoslatch 尺寸 sweep 优化(输入对管 M1/M2 win + 尾电流管 MP1 wtail, FineSim .mt0.csv parse, 6 轮目标变更 max|ldfe_dm|→max|slicer1st_out|→min CK2Q→min FOM=power×delay, pulvt→prvt→puhvt)->produce (portability-driver reframe, real FineSim .mt0.csv sweep 结果不可复刻->synth_data, §4 有牙必要, r835 reframe_note backfill batch10): 用户 jiangbaol@hfeg0pkn004 (sess 1794540366981_p3c57, mc=208, spice_sim 域) 迭代调节输入对管+尾电流管, FineSim 仿真 .mt0.csv 解析, 6 轮目标变更, sweep_batch.sh 批处理+.mt0.csv 解析+约束过滤+最优选择; A 不可行原因=real FineSim .mt0.csv 多轮 sweep 结果不可沙盒复刻 -> 收敛为 sweep_fom_optimizer.py(读 hidden B synth .mt0.csv+spec, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0.csv 不可复刻); 意图核心(sizing sweep + .mt0.csv parse + 约束过滤 + FOM=power×delay 最优选择 + best_point + sweep_log)完整保留; check.py 13 断言验 zip 含 sweep_fom_optimizer.py + py_compile + 脚本在 hidden B 上 subprocess 真跑 exit0 + JSON 含必需键(total_points/feasible_count/best_point) + cross-input guard(A≠B .mt0.csv 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 解析 .mt0.csv 文本 0 EDA 二进制应 L1), level 缺标, k_rationale/k_check 缺标应 13, track 缺标应 synthesized, shard 缺标应 B。",

    # ===== 2 keep_reframe_for_teeth (Q&A-analysis-driver) =====
    "EDA-Eval-DesignFlow-SimModelMismatchDiag-001":
        "SRAM bitcell 后仿「换 bitcell 252→336 + width→40nm 结果不变」根因诊断(DSPF 器件引 hc_pu_fs/hc_pg_fs/hc_pd_fs 模型但 stimulus .LIB 加载 tt_sram_dbc corner 只定义 hd_p* 模型, model/subckt not found)->produce-report (Q&A-analysis-driver reframe, 原 trace 纯分析「你分析一下我那里错了」->produce diagnostic_report.json 加 §4 牙, asset=A-faithful real DSPF/stimulus/HSPICE error log 文本便携, r835 reframe_note backfill batch10): 用户 e0024852@hfeg0pkn005 (sess 1794549248472_sjaal, mc=971, spice_sim 域) 原始请求「运行…stimulus_pex_rev06_model_rev04.sp 的时候 我从原来的 CH252 换成 336 网表的 width 换成了 40 但是我现在仿真出来的结果跟 252 一样 你分析一下我那里错了」+ HSPICE 报错 model/subckt 'hc_pu_fs' is not found; 真实助手 zhulong 根因诊断链: DSPF 器件引用 hc_pu_fs/hc_pg_fs/hc_pd_fs 模型(HC bitcell FS 变体 width=4e-08=40nm)→ stimulus .LIB 却加载 tt_sram_dbc corner(只定义 hd_p*)→ model not found; 意图形态=Q&A-analysis(原是「分析哪里错了」纯讲解); A 不可行原因=Q&A 无 check 牙(纯讲解无法区分真假交付) -> 收敛为 diagnose_model_mismatch.py+diagnostic_report.json(在 hidden B real sim 文件上重跑诊断, asset_fidelity=A-faithful); reframe 由 Q&A-analysis-driver(原 Q&A→produce diagnostic_report.json 含 root_cause+evidence+fix_action); 意图核心(根因定位: DSPF 模型名 vs .LIB corner 模型定义不匹配 + evidence: hc_pu_fs not found 报错 + fix: 切换 PF 模型库或 corner)完整保留; check.py 13 断言验 zip 含 diagnose_model_mismatch.py+diagnostic_report.json + report 合法 JSON 含全部顶层键 + 候选在可见 A sim 目录上重跑 exit0 复现诊断 + root_cause 与 oracle 一致 + cross-input guard(A≠B sim 文件不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-report 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 解析+诊断文本 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 13, track 缺标应 synthesized, shard 缺标应 B, asset=A-faithful 一致(DSPF/stimulus/error log 文本 scp 便携) ✓。",

    "EDA-Eval-DesignFlow-SnmAnalyzerExplain-001-v2":
        "mc_snm_analyzer.py(761 行 6T SRAM HSPICE MC GUI 分析器)HSNM/RSNM/统计结果逻辑讲解(2 数据源+蝶形表流式提取状态机+Seevinck 最大内接正方形+14 次二分+sigma 统计)->produce-report (Q&A-analysis-driver reframe, 原 trace 纯 explain「处理 HSNM、RSNM 和统计结果的逻辑是什么」->produce snm_explanation.json 结构化 schema 加 §4 牙, A=trace-verbatim mc_snm_analyzer.py 761 行便携, hidden-B=synthesized 8T vs 6T cross-input, **v2 case** 来自 11-15 reaudit 重做, r835 reframe_note backfill batch10): 用户 e0030760@hfeg0pkn004 (sess 1794461037123_hxrml, mc=28, spice_sim 域) 问 mc_snm_analyzer.py(761 行, 6T SRAM HD_FS_CH252_6T ttg_25T 0.75V HSPICE MC GUI 分析器)「处理 HSNM、RSNM 和统计结果的逻辑是什么? 分别在做什么?」; agent read_files 分 4 段读完全部 761 行+核对 .ms0/.lis/.snm_cache.csv/.butterfly_index 数据格式, 给结构化讲解: 总体架构(2 数据源)+RSNM/HSNM(蝶形表流式提取状态机+Seevinck 最大内接正方形+14 次二分); 意图形态=Q&A-explain(原是「逻辑是什么」纯讲解); A 不可行原因=Q&A 无 check 牙 -> 收敛为 snm_explanation.json(结构化 schema 含 sram_type/node_names/params/data_source 等 16 键, A=trace-verbatim analyzer.py 761 行从 trace read_files 工具结果逐行还原, hidden-B=synthesized 8T SRAM 不同节点/参数/扩展名/二分次数/bin/phi_inv/统计字段/sigma 字段/块大小/缓存后缀/校验键/bug 数, A 与 B 在 14 维全部不同 ≥6 满足 cross-input 区分); reframe 由 Q&A-analysis-driver(原 explain→produce snm_explanation.json 结构化 schema); 意图核心(2 数据源架构 + RSNM/HSNM 蝶形表流式提取 + Seevinck 最大内接正方形 + 14 次二分 + sigma 统计字段)完整保留; check.py 21 断言验 submit.zip 含 snm_explanation.json 合法 JSON + 16 个 schema 键齐全 + sram_type==A 真值 + node_names==A 真值(4 蝶形节点) + params==A 真值 + data_source + cross-input guard(A≠B analyzer 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-report 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 解析+比对文本 0 EDA 二进制), level 缺标应 L1, k_check=21==k_rationale=21 ✓, track 缺标应 synthesized(A=trace-verbatim 但 hidden-B=synthesized, 整体 track=synthesized), shard 缺标应 B。**注**: 本 case 是 **v2 case**(来自 2026-11-15 reaudit 重做, v2 相对 v1 改 hidden-B 为 synthesized 8T vs 6T cross-input 加 §4 牙, 原 v1 见 ARCHIVE), 11-15 用户令「重做 = 新增版本 + 标状态, 不删旧 case」产物。",

    # ===== 1 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-SimProgressCheck-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r835 reframe_note backfill batch10): 用户 shanmei@hfeg0plg53 (sess 1793775649853_zns2p, mc=2853, spice_sim 域)「我的目录下有一个 tb_OTA_stb_farcap 的子目录, 请在下面 corner_stb 文件夹中执行 check_sim 指令, 查看仿真完成进度, 执行前先执行 source ~/.bashrc 指令, 保证已经加载自定义的函数」; 金标准=assistant 实现 check_sim Python 等价逻辑: 原 Perl 脚本 cxmt_check_sim 因 Spreadsheet::ParseXLSX 模块缺失无法运行, assistant 改写为 Python——扫描 corner_stb 下仿真完成进度; 意图形态=produce-action(check_sim.py+progress_report.txt, Perl→Python 改写 trace-verbatim); 可便携性=高(real corner_stb 目录+Perl cxmt_check_sim 脚本+Python 改写均文本可 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 check_sim.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「执行 check_sim 查看仿真进度」与 case 交付 check_sim.py 扫 corner_stb 产 progress_report 同形映射, asset A-faithful 因 corner_stb 目录+Perl/Python 脚本文本 scp 便携); check.py 14 断言验 zip 含 check_sim.py+progress_report.txt + check_sim.py py_compile + 接受 corner_stb 目录路径参数且在隐藏 B 上 exit0 + progress_report 含进度字段 + cross-input guard(A≠B corner_stb 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 扫目录 0 EDA 二进制), level 缺标应 L1, k_check=14==k_rationale=14 ✓, track=faithful 一致 asset=A-faithful ✓, shard 缺标应 B。**注**: plg 独立子网新候选, 11-05 重扫令首扫发现, mc=2853 高命中。",
}


def main():
    applied = 0
    skipped = []
    for case_id, note in REFRAME_NOTES.items():
        path = os.path.join(CASES_DIR, f"{case_id}.json")
        if not os.path.exists(path):
            skipped.append((case_id, "MISSING FILE"))
            continue
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "reframe_note" in md:
            skipped.append((case_id, "ALREADY HAS reframe_note"))
            continue
        # insert reframe_note as last metadata key, preserve existing order
        md["reframe_note"] = note
        d["metadata"] = md
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        applied += 1
        print(f"  APPLY {case_id}")
    print(f"\nApplied: {applied} / Skipped: {len(skipped)}")
    for cid, why in skipped:
        print(f"  SKIP {cid}: {why}")


if __name__ == "__main__":
    main()
