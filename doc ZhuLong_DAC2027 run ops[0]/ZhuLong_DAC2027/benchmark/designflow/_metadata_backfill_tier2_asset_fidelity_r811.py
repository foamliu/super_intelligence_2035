#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r811.py — r811 档2 asset_fidelity backfill batch11.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done. r806 batch6 (+12, 166→178) done.
      r807 batch7 (+12, 178→190) done. r808 batch8 (+12, 190→202) done.
      r809 batch9 (+12, 202→214) done. r810 batch10 (+12, 214→226) done.
      本轮 r811 推进 档2 batch11 — 12 cases
      (alphabetical next 12 missing after r810 batch10 ModelQaRefactorAnalyze:
       MonteCarloDeckGen..Mt0PvrefAbsGroupStat, M 段尾部).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r810 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 /
                    真实 scp 自内网 / 真实用户 paste / "reproduced faithfully" /
                    "faithful compact/trimmed representation" 标注 / "Real content from" 显式 verbatim 声明 /
                    "elided for brevity" 忠实节选标记 / 真实 export header banner /
                    task_spec 显式 "trace 原文件 verbatim" 标注 / desc 显式 "逐字"/"原始" 标注 /
                    真实内网 /proj//apps//home//rundata/ 路径)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl/bash 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/PDK/model fixture / 合成 .md0/.lis/.mt0 仿真输出数据 /
                    合成 .sv/.v verilog/SystemVerilog testbench fixture (precedent: CbrForceMechanismExplain/CovBinMetaExtract)
                    含 "real export banner + 合成数据" 中间态 (task_brief/desc 显式 "示例"/"合成" 覆盖 export banner)
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver +
      task_spec verbatim 标注。A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized /
      portability reframe / "样本"/"合成"/"self-contained sample" / "auto-generated stub" / "示例" /
      "portable mirror" / "decoy" 添加 distractor / "(reconstructed from cline trace ...)" /
      desc 显式 "合成" / "示例" / placeholder foundry 名 / 无 verbatim 标注 / "忠实复刻" 格式重建声明。

本批 12 case 判定:
  - 5 A-faithful (42%): MonteCarloDeckGen / MosDcGuiTool / MrrTaskSignatureExtract / Mt0ParseFix / Mt0PvrefAbsGroupStat
  - 7 synth_data: MonteMt0Stats / MrSelfClearExpDiag / Mt0AggMinMax / Mt0FolderAggStat /
                  Mt0GroupedStatsGen / Mt0MeasureStat / Mt0MetastabDiag
  (实际分布: A-faithful=5 / synth_data=7; synth_deck/synth_script/synth_doc/synth_log=0)

关键发现:
  - "Real content from" + "elided for brevity" 双信号 → A-faithful (MrrTaskSignatureExtract):
    A_test.sv 文件 header 显式 "Real content from /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/ddr6_test.sv"
    + "Contains the MRR (Mode Register Read) task definition (originally around line 2823)"
    + "Middle of the task body (CA-bus drive, compare, multi-cycle handling) elided for brevity"
    + body 含真实生产 SV 代码 + 真实工程师注释 (//valley added for temperature, //lichi 0428, //TODO: For FSP MRs...)
    + "// ... (MRR task body elided: ... ~1500 lines omitted.) ..." 忠实节选标记
    ⇒ file-verbatim (A-faithful, "Real content from" 显式 verbatim 声明 + "elided for brevity" 忠实节选 标记).
    与 r810 ModelQaRefactorAnalyze (task_spec verbatim 标注) + r805 "reproduced faithfully" 同型,
    新增 "Real content from" + "elided for brevity" 双信号族.
  - "decoy MR1/MR4 definitions" 添加 distractor → synth_data (MrSelfClearExpDiag):
    A_specdef.sv/A_test.sv/A_timing_load.sv header "(excerpt, trace-time)" + "Source: /proj/dscqa/.../ddr6_specdef.sv"
    + "Lines 283-315 (MR7 ZQ control register block) + decoy MR1/MR4 definitions"
    ⇒ 真实 MR7 段 (task focus) + 添加 decoy MR1/MR4 distractor ⇒ constructed SV fixture, 非 pure verbatim excerpt.
    "trace-time" 措辞弱于 "Real content from"; "decoy" 添加 distractor 是 fabrication 信号 ⇒ synth_data.
    与 r810 MdMaskBeatZeroDiag (合成 SV fixture 无 user@host trace marker) 同型; "decoy" 添加 distractor 首例.
    MrrTaskSignatureExtract (A-faithful) 与 MrSelfClearExpDiag (synth_data) 同批对照:
    前者 "Real content from" + "elided for brevity" (无 fabrication), 后者 "decoy" (有 fabrication)
    ⇒ 是否含 fabrication (decoy/synthetic 添加) 是 A-faithful vs synth_data 的判别线.
  - "portable mirror of real 1_run" 显式合成标记 → synth_data (MonteMt0Stats):
    1_run_A 文件首行注释显式 "# 1_run_A - monte simulation submission loop (portable mirror of real 1_run)"
    + .mt0 文件虽含真实 PrimeSim HSPICE V-2023.12 export banner 但每文件仅 1 行数据 (12 文件 × 1 行 = 12 measurements,
    真实 monte 通常是 1 文件 × N 行) + task_brief "样例" ⇒ 合成 portable mirror.
    "portable mirror" 是新合成信号 (与 "auto-generated stub"/"示例" 同列), 显式标注合成 portable 镜像.
  - "逐字" + "原始" desc 标注 → A-faithful (MosDcGuiTool):
    example_nmos_dc.sp/example_pmos_dc.sp desc 显式 "原始 NMOS DC bench 示例(003_nmos_dc.sp 逐字..."
    + 文件含真实 /proj/drgqa/V0/workdir/haojianh/simulation/003_Control/SP/hspice.sp + .lib /proj/drgqa/V0/model/current_D5_v0d9_t05/model.sp tt 真实内网路径
    + 无 stub/synthetic 标记 ⇒ A-faithful (file-verbatim).
    simdir/ 子资产 desc 显式 "合成 HSPICE .printsw0/.printsw1 nmos+pmos 样例 + config.json... 按 trace 文档化格式与量级合成" ⇒ synth_data,
    但主资产 example_*.sp 是 verbatim ⇒ 案件按主资产标 A-faithful.
    "逐字" desc 标注与 r810 ModelQaRefactorAnalyze (task_spec verbatim 标注) 同型, 新增 "逐字"+"原始" 双 desc 标注族.
  - "A-faithful 资产... 真实附件" desc 标注 → A-faithful (Mt0PvrefAbsGroupStat):
    a7_AG_ThinFsComp_rerun.mt0 desc 显式 "A-faithful 资产：FineSim .mt0 量测文件 ... 来自 trace declanzh@hfeg0pkn002 yez2i 真实附件"
    + 文件含真实 FineSimPro V-2023.12-1 export banner + 276 行真实 pvref/voffset_vout_d_mv 数据 ⇒ A-faithful (file-verbatim).
  - "真实" + prompt.txt "A-faithful" 标注 → A-faithful (Mt0ParseFix):
    results/*.mt0 desc 显式 "4 个真实 FineSim .mt0 量测文件" + prompt.txt desc 显式 "真实用户原话（A-faithful，yifansun @ hfeg0pkn001...)"
    + .mt0 含真实 FineSimPro V-2023.12-1 export banner + session_record.md 含真实用户 yifansun + 真实 /proj/ddgoa/V0/workdir/yifansun 路径
    + parse_results.py 含真实 /proj/ddgoa/V0/workdir/yifansun/simulation/ddgoa_cmos_pc40_DPmux8 内网路径 ⇒ A-faithful (file-verbatim).
  - 真实 FineSim deck 无合成标记 → A-faithful (MonteCarloDeckGen):
    sim_driver_x20_adj.sp 含真实 /proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/ 多处内网路径
    + 真实 FineSim options (finesim_mode=spicexd, finesim_vdd=3.5v) + 真实 .lib /proj/ddgoa/V0/model/current/model.sp 引用
    + 无 stub/synthetic/示例 标记 + track=faithful + task_brief 仅称 "FineSim 仿真 deck" ⇒ A-faithful (file-verbatim).
  - "示例" task_brief 覆盖 real export banner → synth_data (Mt0AggMinMax):
    12 个 .mt0 文件含真实 FineSimPro V-2023.12-1 export banner + 真实列名 i_vfsbln/i_vwlp_fsbln/ieff./temper/alter#,
    但 task_brief 显式 "12 个示例 .mt0 文件" + 每文件仅 1 行数据 (12 文件 × 1 行 = 12 measurements, 真实 .mt0 通常 1 文件 × N 行)
    + config.json/example_output_A.txt 合成 ⇒ synth_data. "示例" task_brief 标记覆盖 real export banner (与 r810 McLisSnmExtractor "示例 .lis 无 export banner" 形成 "示例 .lis 有 export banner" 对照, 中间态).
  - "忠实复刻" 格式重建声明 + desc 显式 "合成" → synth_data (Mt0MetastabDiag):
    mt0_A/mt0.mt0 含真实 PrimeSim HSPICE V-2023.12-SP1-1 linux64 export banner + 55 列 dfqd1 three-method schema,
    但 desc 显式 "合成 HSPICE .mt0（忠实复刻 dfqd1 three-method 结构...)" ⇒ 合成 (faithful format reproduction, not real content).
    "忠实复刻" 格式重建声明 (与 r810 ManualSectionExtract "自包含合成" 同型); desc 显式 "合成" 覆盖 real export banner.
  - "按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）" desc 显式合成 → synth_data (Mt0FolderAggStat):
    core1103/ 24 个 .mt0 desc 显式 "按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）" + prompt.txt "A-faithful" (指 prompt verbatim)
    ⇒ track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 .mt0 已被集群清理), synth_data.
  - 假 .mt0 header + 非标准 control line → synth_data (Mt0GroupedStatsGen):
    measurement.mt0 header "$ HSPICE measurement data - monte carlo sweep" + ".measuremt0_file" (非真实 HSPICE .mt0 语法, 真实应为 $DATA1 SOURCE='HSPICE' banner)
    + 数据值手动录入 (0.15/-0.2466 简单浮点) + spec.json 合成规格文档 + 资产路径非标准 (assets/Mt0GroupedStatsGen-001/ 无 EDA-Eval-DesignFlow- 前缀)
    ⇒ synth_data (合成 .mt0 with fake header, 非 real export banner).
  - 假 FineSimPro header + Python-random 数据 → synth_data (Mt0MeasureStat):
    sample_A.mt0 header "$ FineSimPro measurement data" + "$ circuit: a8_Vfsrdb_and_FsLatch_SIM" + "$ monte-carlo run"
    (非真实 FineSimPro $DATA1 banner, 与 Mt0PvrefAbsGroupStat 真实 FineSimPro V-2023.12-1 banner 反向)
    + 数据值 Python-random 生成 (0.7461058299869286 等 16 位小数, random.random() 特征)
    + task_context.md "样例... 不参与判分" ⇒ synth_data (合成 .mt0 with fake header + Python-random 数据).

A-faithful 5/12=42% (累计 52/132=39%); synth_data 7/12=58%.
强信号新增 1 类: "Real content from" + "elided for brevity" 双信号族 (MrrTaskSignatureExtract).
"decoy" 添加 distractor 首例 (MrSelfClearExpDiag, fabrication vs elision 判别线实证).
"portable mirror" 显式合成信号新增 (MonteMt0Stats).
"逐字"+"原始" desc 标注族新增 (MosDcGuiTool).
track≠asset_provenance 本批 2 例 (累计 18→20): MonteMt0Stats (track=faithful 记 prompt verbatim + asset=portable mirror 合成) /
  Mt0FolderAggStat (track=faithful 记 prompt verbatim + asset=合成 .mt0 已被集群清理).
A-faithful 累计 52/132=39% (r801-r810 累计 47/120=39% + 本批 5/12=42%).
"""

import json
import os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-MonteCarloDeckGen-001": (
        "A-faithful",
        "sim_driver_x20_adj.sp = 真实 FineSim XDec driver 仿真 deck (3900 字节/约 90 行, header '*********** Finesim simulation basic setting  ************' + "
        "真实 FineSim options: .option finesim_mode = spicexd / finesim_prbport = 0 / finesim_maxicout = 0 / finesim_vdd = 3.5v + "
        "真实内网 .inc 路径 '/proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/ddgoa_cmos_work_test_Idd_XDec_7Section_schematic_ALPS/ddgoa_cmos_work_test_Idd_XDec_7Section_schematic.netlist' + "
        "'/proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/sim_xdecg_driver_test/sweep_x20_size_op/XdecG_driver_x20_adj.netlist' + "
        "'/proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/sim_diode_pvt/input_idd0.sp' (stimulus) + "
        "真实 .lib '/proj/ddgoa/V0/model/current/model.sp' (pre_sim/FF/FF_Array/TT/TT_Array/SS/SS_Array) + "
        "真实 .lib '/proj/ddgoa/V0/model/current/incFile_lp' (bjt_tt/res_tt/nicap_tt/diode_tt) + "
        "真实 .inc '/proj/ddgoa/V0/workdir/kerwind/simulation/sa_control_vwlp/hspice0.94v.voltage' + "
        "真实 PVT corner 块 (.if pcor_ff==1/pcor_tt==1/pcor_ss==1, .temp 45c/25c/-40c, .param ptemp) + "
        ".param sigmaflag=1.36 + Cthin/Cthick/CapO/Cgatein Vcap 参数 + .tran 1p 2us + .probe v(*) i(v*) isub(*.inh_*) + "
        ".alter G4B_CIP 注释块含真实 /proj/shdc/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t07 路径 + .end); "
        "task_brief.md = 交付接口 (gen_monte_carlo.py 打包为 outputs/submit.zip); track=faithful (与 asset 一致); reframe=None; layer=L1; "
        "无 stub/synthetic/auto-generated/示例/合成 标记 (grep 实测 0 命中); task_brief 仅称 'FineSim 仿真 deck' (用户原始 deck); "
        "真实 FineSim deck (真实 /proj/ddgoa 内网 .inc/.lib/.model 路径群 + 真实 FineSim options + 真实 PVT corner 块 + 真实 XDec driver 上下文), "
        "无 stub/synthetic 标记 ⇒ file-verbatim (A-faithful, 真实 FineSim deck verbatim 首例 of batch11)",
    ),
    "EDA-Eval-DesignFlow-MonteMt0Stats-001": (
        "synth_data",
        "1_run_A = 合成 monte 仿真提交脚本 portable mirror (790 字节/22 行, 首行注释显式 '# 1_run_A - monte simulation submission loop (portable mirror of real 1_run)' + "
        "合成 BASE_DIR/TEMPLATE_SP/MONTE_SP_DIR/RESULT_DIR 路径 + for i in seq 1 3 循环 + sed 替换 .param fromnum/endnum + bsub -q lacaa_sram hspice); "
        "result_A/ = 合成 .mt0 输出目录 (3 子目录 io_d0_template_1_4/5_8/9_12, 每目录 1 .mt0 文件); "
        "io_d0_template_1_4.mt0 = 合成 .mt0 (684 字节/9 行, header 含真实 PrimeSim HSPICE V-2023.12 linux64 export banner '$DATA1 SOURCE=\\'PrimeSim HSPICE\\' VERSION=\\'V-2023.12 linux64\\' PARAM_COUNT=1' + "
        "$OPTION MEASFORM=1 + 列 index/t_outb_r/v_blb_fall1/v_bl_fall1/v_dv/v_df_sat_sac/v_df_bl_blb/v_df_b_s/temper/alter# + 4 行数据, 每文件仅 1 行 monte-carlo 样本 — 真实 monte 通常是 1 文件 × N 行 非 N 文件 × 1 行); "
        "prompt.txt = verbatim 用户原话 '我发给你的两个文件，一是1_run...统计mt0结果文件中index后七个参数的平均值和标准差(正态分布)...生成montesum.mt0'; task_brief.md = 交付接口 (montesum.py); "
        "track=faithful (指 prompt verbatim); reframe=None; layer=L1; "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 portable mirror); "
        "合成 monte sim 脚本 portable mirror (首行注释显式 'portable mirror of real 1_run', 与 r810 'auto-generated stub' 同列合成信号族) + "
        "合成 .mt0 (虽含真实 PrimeSim HSPICE export banner 但每文件 1 行数据 = portable mirror 最小重建, 与 r810 McLisSnmExtractor '示例 .lis 无 export banner' 形成对照) "
        "⇒ synth_data (合成 .mt0 仿真输出数据 + 合成 portable mirror 脚本; 'portable mirror' 显式合成信号新增)",
    ),
    "EDA-Eval-DesignFlow-MosDcGuiTool-001": (
        "A-faithful",
        "example_nmos_dc.sp = 真实 HSPICE NMOS DC bench (1089 字节, desc 显式 '原始 NMOS DC bench 示例(003_nmos_dc.sp 逐字, param_modfiy: temp/vcc/vg_l/vg_h/step/w/l/nf, .dc vd sweep vg + .dc vref -vcc vcc + .print LX7/1-LX8/abs(i(vvdd))/LX82)' + "
        "真实内网 .inc '/proj/drgqa/V0/workdir/haojianh/simulation/003_Control/SP/hspice.sp' + 真实 .lib '/proj/drgqa/V0/model/current_D5_v0d9_t05/model.sp' tt + "
        "*********************option***********************/*********************param_modfiy********************* 等 section 分隔注释 + "
        ".param temp=25/vcc=1.1/vg_l=0.5/vg_h=vcc/step=0.2/w=1.6e-6 l=0.24e-6 nf=1 + .temp temp + XMMN0 VDD VGG VSS VBB ntn_lvio w='w*nf' l='l' nf='nf' 器件实例); "
        "example_pmos_dc.sp = 真实 HSPICE PMOS DC bench (1143 字节, desc 显式 '原始 PMOS DC bench 示例(004_pmos_dc.sp 逐字, .dc vds sweep vgs + .dc vref 0 2*vcc 0.01 + .print LX82(XMMP1))'); "
        "simdir/ = 合成 HSPICE .printsw 输出样例 (config.json + nmos.printsw0/.printsw1 + pmos.printsw0/.printsw1, desc 显式 'A 可见输入：合成 HSPICE .printsw0(Id/gm/Rout vs Vds，外层 vg 扫描)/.printsw1(LX82 C-V vs vref) nmos+pmos 样例 + config.json(ntn_lvio/ptn_lvio, vcc=1.1)。按 trace 文档化格式与量级合成'); "
        "prompt.txt = 真实用户原话 verbatim (desc 显式 '真实用户原话（A-faithful，zanezang @ hfeg0plg57，trace 1793942454477_whc3n U#0-U#12 逐字）'); task_brief.md = 交付接口 (mos_dc_tool.py --gen-bench/--parse); "
        "track=faithful; reframe=None; layer=None; "
        "主资产 example_*.sp = 真实 HSPICE bench verbatim (desc 显式 '逐字' + '原始' + 真实 /proj/drgqa 内网 .inc/.lib 路径 + 真实 ntn_lvio 器件实例 + 无 stub/synthetic 标记); "
        "子资产 simdir/ = 合成 .printsw 样例 (desc 显式 '合成 HSPICE .printsw... 按 trace 文档化格式与量级合成') — 主资产 verbatim, 子资产 synth_data, 案件按主资产标; "
        "desc 显式 '逐字' + '原始' 标注族 (与 r810 ModelQaRefactorAnalyze task_spec verbatim 标注同型) + 真实 /proj/drgqa 内网路径 ⇒ file-verbatim (A-faithful, '逐字'+'原始' desc 标注首例 of batch11)",
    ),
    "EDA-Eval-DesignFlow-MrSelfClearExpDiag-001": (
        "synth_data",
        "A_specdef.sv = constructed SV fixture (2661 字节, header '// A_ddr6_specdef.sv -- DDR6 vecgen mode register field definitions (excerpt, trace-time)' + "
        "'// Source: /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/ddr6_specdef.sv' + "
        "'// Lines 283-315 (MR7 ZQ control register block) + decoy MR1/MR4 definitions' + 'A_ONLY_MARKER_mrselfclearexpdiag' + "
        "body 含真实 MR7 ZQ control register block (MA_zq_upd_flag/OP_zq_upd_flag_BITS/En/Dis, MA_zq_init 等 parameter bit 定义) + decoy MR1/MR4 distractor 添加); "
        "A_test.sv = constructed SV fixture (1963 字节, header '// A_ddr6_test.sv -- DDR6 vecgen testbench (excerpt, trace-time)' + 'Source: /proj/dscqa/.../ddr6_test.sv' + "
        "'Lines ~2520-2560 (functional_mode_enable self-clear block) + decoy task' + body 含 functional_mode_enable task); "
        "A_timing_load.sv = constructed SV fixture (3021 字节, header '// A_timing_load.sv -- MRSetting / MRSettingDirect task definitions (excerpt, trace-time)' + "
        "'Source: /proj/dscqa/.../timing_load.sv' + 'Lines ~2079-2140 (MRSetting task) + 2313-2350 (MRSettingDirect)' + body 含 MRSetting task); "
        "prompt.txt = 真实用户原话 verbatim (tongfanl @ hfhds201, '/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local 帮我看下，在Load_Mode MR7 的 OP2后，一段时间后该位的exp值是什么值？'); task_brief.md = 交付接口; "
        "track=faithful; reframe='DDR6 Load_Mode MR7 OP2 self-clear exp 静态诊断器->produce-tool (Q&A/diag->produce-tool 诊断器 reframe, §4 有牙必要, r743 spotcheck batch21)'; layer=L1; "
        "constructed SV fixture (真实 MR7 段 excerpt + 'decoy MR1/MR4 definitions' 添加 distractor ⇒ 含 fabrication; 'trace-time' 措辞弱于 'Real content from'/'逐字'/'reproduced faithfully'; "
        "无显式 user@host trace marker 在文件 header; 与 r810 MdMaskBeatZeroDiag (合成 SV fixture 无 user@host trace marker) 同型; "
        "'decoy' 添加 distractor 是 fabrication 信号 ⇒ 非 pure verbatim excerpt ⇒ synth_data (合成 SV fixture with decoy distractor, 'decoy' 添加 distractor 首例 of batch11)",
    ),
    "EDA-Eval-DesignFlow-MrrTaskSignatureExtract-001": (
        "A-faithful",
        "A_test.sv = 真实 DDR6 vecgen testbench verbatim excerpt (5856 字节, header 显式 '// Excerpt of ddr6_test.sv (DDR6 vecgen_local testbench)' + "
        "'// Real content from /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/ddr6_test.sv' (显式 'Real content from' verbatim 声明) + "
        "'// Contains the MRR (Mode Register Read) task definition (originally around line 2823)' (file:line 标注) + "
        "'// Middle of the task body (CA-bus drive, compare, multi-cycle handling) elided for brevity' (faithful compact/trimmed representation 节选标记); "
        "body 含真实生产 SV 代码: task MRR(reg[MODEMA_BITS-1:0] ma, bit termit=0, bit cw=0, reg [MODEOP_BITS-1:0] mrr_exp = 0, ...) + "
        "真实工程师注释 '// TODO: ca43 is not used!!!!!' + '// valley added for temperature' + '//TODO: For FSP MRs, MRR is read from FSP_WR registers.' + '//lichi 0428' + "
        "真实 mr_direct_fsp_flag/mr_direct_mark/ShareDRIVER.mr_direct 调用 + sim_addr.ma <= #(toffset) ma + sem_cmd.get(1)/put(1) + "
        "'// ... (MRR task body elided: CA-bus 4-cycle command drive, exp-value assembly into val[], load_exp_fifo, DQ/DQS drive, compare, multi-cycle MCME handling. ~1500 lines omitted.) ...' (faithful compact 节选标记, ~1500 行省略); "
        "prompt.txt = 真实用户原话 verbatim (tongfanl @ hfhds201, '/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local 分析一下上述路径，告诉我task MRR的书写逻辑'); track_brief.md = 交付接口; "
        "track=faithful; reframe='DDR6 task MRR 签名/结构提取->produce-tool (portability+explain->produce-tool 提取器 reframe, §4 有牙必要, r736 spotcheck batch14)'; layer=L1; "
        "真实 DDR6 vecgen testbench verbatim excerpt (文件 header 显式 'Real content from /proj/dscqa/.../ddr6_test.sv' verbatim 声明 + 'elided for brevity' 忠实节选标记 + "
        "file:line ('around line 2823') + body 含真实生产 SV 代码 + 真实工程师注释 (valley/lichi/TODO) + '~1500 lines omitted' 忠实节选, 无 fabrication/decoy 添加) "
        "⇒ file-verbatim (A-faithful, 'Real content from' + 'elided for brevity' 双信号族首例 of batch11; 与 r810 ModelQaRefactorAnalyze task_spec verbatim 标注 + r805 'reproduced faithfully' 同型, "
        "新增 'Real content from' + 'elided for brevity' 双信号族)",
    ),
    "EDA-Eval-DesignFlow-Mt0AggMinMax-001": (
        "synth_data",
        "a51_coreA_rerun#{1..12}.mt0 = 12 个合成 FineSimPro .mt0 文件 (每文件 226-230 字节/4 行, header 含真实 FineSimPro V-2023.12-1 export banner '$DATA1 SOURCE=\\'FineSimPro\\' VERSION=\\'V-2023.12-1\\' PARAM_COUNT=0' + "
        ".title 'typ'/'ff'/'ss'/'' + 列 i_vfsbln/i_vwlp_fsbln/ieff./temper/alter# + 每文件仅 1 行数据 (12 文件 × 1 行 = 12 measurements, 真实 .mt0 通常 1 文件 × N 行 — portable mirror 最小重建模式, 与 MonteMt0Stats 同型); "
        "config.json = 合成 format spec (331 字节, format/columns/units_note/params_of_interest/header_markers/data_line_cols/A_TO_mA); "
        "example_output_A.txt = 合成 example 输出 (2664 字节, header '.mt0 文件数据汇总 来源目录: assets/EDA-Eval-DesignFlow-Mt0AggMinMax-001 文件总数: 12，成功解析: 12 单位说明: 原始值 A (安培); 绝对值 mA (毫安) = |A| × 1000' + min/max 表); "
        "prompt.txt = 真实用户原话 verbatim (declanzh @ hfeg0plg97, 真实 /rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103 内网路径 + "
        "verbatim '你是 declanzh...你在 hfeg0plg97 上跑完了一轮 HSPICE/FineSim 仿真...该目录下有几十个 .mt0 文件（FineSimPro 测量输出）...其中 i_vfsbln 是 Vfsbln 支路电流...ieff. 是电流效率'); task_brief.md = 交付接口; "
        "track=faithful; reframe=None; layer=None; "
        "合成 .mt0 (虽含真实 FineSimPro export banner + 真实列名 + PVT 风格数据变化, 但 task_brief 显式 '12 个示例 .mt0 文件（FineSimPro 测量输出格式）可供参考格式' ('示例' 标记) + "
        "每文件 1 行 portable mirror 最小重建模式 + config.json/example_output_A.txt 合成) ⇒ synth_data "
        "(合成 .mt0 with real export banner + '示例' task_brief 标记覆盖 export banner; 与 r810 McLisSnmExtractor '示例 .lis 无 export banner' 形成 '示例 .lis/.mt0 有 export banner' 中间态对照)",
    ),
    "EDA-Eval-DesignFlow-Mt0FolderAggStat-001": (
        "synth_data",
        "core1103/ = 24 个合成 HSPICE .mt0 文件 (desc 显式 'A 可见输入：24 个 HSPICE .mt0 文件（每个一行 5 列 i_vfsbln/i_vwlp_fsbln/ieff./temper/alter#，A=安培，°C），温度 -40/85/130；"
        "按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）' — 显式 '合成' + '真实 .mt0 已被集群清理' 说明); "
        "prompt.txt = 真实用户原话 verbatim (desc 显式 '真实用户原话（A-faithful，declanzh @ hfeg0plg97，trace 1793947529316_ie8du U#3-U#6 逐字）:汇总 core1103 文件夹下 .mt0 到一个文档+每参数 max/min，按绝对值/mA，ieff 百分比，文件列只保留#数字，2位小数，去掉温度栏'); task_brief.md = 交付接口; "
        "track=faithful (指 prompt verbatim); reframe=None; layer=None; "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 .mt0 '真实 .mt0 已被集群清理' — 累计 track≠asset_provenance +1); "
        "合成 .mt0 (desc 显式 '按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）', 真实 .mt0 已被集群清理 ⇒ 合成最小重建) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-Mt0GroupedStatsGen-001": (
        "synth_data",
        "measurement.mt0 = 合成 HSPICE .mt0 (header '$ HSPICE measurement data - monte carlo sweep' + '.measuremt0_file' (非真实 HSPICE .mt0 语法, 真实应为 $DATA1 SOURCE='HSPICE' banner — fake header) + "
        "列名行 'pvref voffset_vout_d_mv voffset_vout_u_mv temper alter#' + 30 行数据 (3 pvref 组 0.15/0.35/0.55 × 10 行, 数据值手动录入简单浮点如 -0.2466/-0.2307/-0.2417)); "
        "spec.json = 合成 format spec (列定义 column_indices/group_by=pvref/measurements/metadata_columns=temper,alter#/header_prefixes/header_line_starts_with/output_format); "
        "desc = 'HSpice .mt0 测量数据文件（Input A），含 3 个 pvref 组（0.15/0.35/0.55），每组 10 行数据，列为 pvref/voffset_vout_d_mv/voffset_vout_u_mv/temper/alter#' + '规格说明：列定义...输出 JSON 格式定义'; "
        "资产路径非标准 (assets/Mt0GroupedStatsGen-001/, 无 EDA-Eval-DesignFlow- 前缀, 与其他 case 异常); "
        "prompt = 'declanzh 的原始需求:帮我把这个文件夹下后缀为.mt0的文件数据汇总到一个文档，并给出每个参数的最大/最小值 — 后续细化要求按 pvref 分组，每组内计算各测量参数的绝对值 min/max' (case 合成 prompt, 非 verbatim 用户原话); "
        "track=None; reframe=None; layer=L2; "
        "合成 .mt0 (fake header '$ HSPICE measurement data' + 非标准 control line '.measuremt0_file' + 手动录入简单浮点数据 + 合成 spec.json + 资产路径非标准 + case 合成 prompt 非 verbatim) "
        "⇒ synth_data (合成 .mt0 with fake header, 非 real export banner, 与 Mt0PvrefAbsGroupStat 真实 FineSimPro V-2023.12-1 banner 反向)",
    ),
    "EDA-Eval-DesignFlow-Mt0MeasureStat-001": (
        "synth_data",
        "sample_A.mt0 = 合成 HSPICE/FineSimPro .mt0 (header '$ FineSimPro measurement data' + '$ circuit: a8_Vfsrdb_and_FsLatch_SIM' + '$ monte-carlo run' (非真实 FineSimPro $DATA1 banner — fake header, 与 Mt0PvrefAbsGroupStat 真实 FineSimPro V-2023.12-1 banner 反向) + "
        ".title a8_Vfsrdb_and_FsLatch_rerun + 列 mc_index/v_facompout/v_faout/res_r1/sensetime_comp_ns/sensetime_falatch_ns/res_vfsrdb/vvfsrdb/vvfsrdcompgt/v_vfsrdbref/temper/alter# + "
        "数据值 Python-random 生成特征 (0.7461058299869286 等 16 位小数, random.random() 输出特征, 非真实 HSPICE 测量值) + 部分 'error' 字符串 sensetime_comp_ns 失败格子); "
        "task_context.md = 合成 task context (含 'trace-faithful 用户原话' + '附件 sample_A.mt0 是一条结构相同的样例（9 组 × 30 MC，仅供你理解格式和本地调试，不参与判分）' — '样例' 显式合成标记); "
        "prompt.md = 合成 prompt (基于 trace 用户原话 + .mt0 格式说明 + 评判要点); desc = 'Input A: Vfsrdb+FsLatch sense-amp MC 仿真 .mt0 样例...格式参考 + 本地调试；不参与判分' + 'Input A: 完整任务上下文（.mt0 格式、CLI 契约、_stats.json schema、已知陷阱、trace-faithful 用户原话、评判要点）'; "
        "track=None; reframe=None; layer=None; "
        "合成 .mt0 (fake header '$ FineSimPro measurement data' 非 $DATA1 banner + Python-random 数据值 16 位小数 + task_context '样例...不参与判分' 显式合成标记) "
        "⇒ synth_data (合成 .mt0 with fake header + Python-random 数据, 与 Mt0PvrefAbsGroupStat 真实 FineSimPro banner + 真实 276 行数据 反向)",
    ),
    "EDA-Eval-DesignFlow-Mt0MetastabDiag-001": (
        "synth_data",
        "mt0_A/mt0.mt0 = 合成 HSPICE .mt0 (header 含真实 PrimeSim HSPICE V-2023.12-SP1-1 linux64 export banner '$DATA1 SOURCE=\\'PrimeSim HSPICE\\' VERSION=\\'V-2023.12-SP1-1 linux64\\' PARAM_COUNT=0' + "
        ".TITLE 'dfqd1 manual three-method v20261014: shared rising-data sanity run' + 55 列真实 dfqd1 three-method schema: clk50/d50/delta_obs/q50/tcq/q_imin/q_imax/q_start/q_dead/q_end/q_pm/q_probe/q_pp/q_raw_min/q_raw_max/q_dw_min/q_dw_max/q_post_min/q_post_max/ax_imin/ax_imax/ax_start/ax_dead/ax_end/ax_pm/ax_probe/ax_pp/ax_raw_min/ax_raw_max/ax_dw_min/ax_dw_max/ax_post_min/ax_post_max/b_*/temper/alter# + "
        "19 $DATA1 块, 15 块含 failed (tcq=12/q50=13) -> 亚稳态 TRUE; "
        "desc 显式 '可见 A：合成 HSPICE .mt0（忠实复刻 dfqd1 three-method 结构，55 列真实 schema...）' — 显式 '合成' + '忠实复刻' 格式重建声明); "
        "prompt.txt = 真实用户原话 verbatim (desc 显式 '真实用户原话（A-faithful，e0029495 @ hfeg0pkn002，trace 1792399658249_w4b6q U#1 逐字）：分析 mt0 文件，判断是否发生亚稳态'); task_brief.md = 交付接口; "
        "track=faithful; reframe='HSPICE .mt0 亚稳态检测诊断器->produce-tool (analysis/Q&A->produce-tool 诊断器+out.json reframe, §4 有牙必要, r743 spotcheck batch21)'; layer=None; "
        "合成 HSPICE .mt0 (desc 显式 '合成' + '忠实复刻 dfqd1 three-method 结构' = faithful format reproduction, not real content — 虽含真实 PrimeSim HSPICE export banner + 55 列真实 schema, 但 desc '合成' 覆盖 export banner) "
        "⇒ synth_data (合成 .mt0 with real export banner + '忠实复刻' 格式重建声明; '忠实复刻' 与 r810 ManualSectionExtract '自包含合成' 同型)",
    ),
    "EDA-Eval-DesignFlow-Mt0ParseFix-001": (
        "A-faithful",
        "results/w100_l42_lv_FF_0.61V_130C.mt0 + w100_l42_lvio_TT_0.8V_25C.mt0 + w117_l46_lvio_FF_0.61V_130C.mt0 + w100_l42_lvio_SS_0.83V_-40C.mt0 = 4 个真实 FineSim .mt0 量测文件 (desc 显式 '4 个真实 FineSim .mt0 量测文件（A 可见输入：w100_l42_lv_FF_0.61V_130C / w100_l42_lvio_TT_0.8V_25C / w117_l46_lvio_FF_0.61V_130C / w100_l42_lvio_SS_0.83V_-40C，13 列：t_delay/i_dyn_read_vcc/i_dyn_read_vccz/...）'; "
        "每 .mt0 含真实 FineSimPro V-2023.12-1 export banner '$DATA1 SOURCE=\\'FineSimPro\\' VERSION=\\'V-2023.12-1\\' PARAM_COUNT=0' + .TITLE '** w100_l42_lv FF_0.61V_130C' + 真实 13 列 t_delay/i_dyn_read_vcc/i_dyn_read_vccz/i_dyn_write_vcc/i_dyn_write_vccz/i_static_vcc/i_static_vccz/i_peak_read_vcc/i_peak_read_vccz/i_peak_write_vcc/i_peak_write_vccz/temper/alter# + 真实测量值 5.7824e-10/5.1124e-05 等); "
        "parse_results.py = 真实待修复脚本 (含真实内网路径 O = r'/proj/ddgoa/V0/workdir/yifansun/simulation/ddgoa_cmos_pc40_DPmux8_PN1p76_PC60_length46_schematic_ALPS/AI' + 真实 PVT corner set TT_0.8V_25C/FF_0.74V_130C/FF_0.82V_-40C/SS_0.85V_130C/SS_0.9V_-40C + 5x6x2=60 variants × 10 PVT corners = 600 仿真任务); "
        "session_record.md = 真实 session 记录 (含真实用户 yifansun + 真实项目 ddgoa V0 + 真实设计 DpMuxTop_2/Abus_tCCDs_Plsprotect + 60 variants × 10 PVT corners = 600 仿真任务); "
        "prompt.txt = 真实用户原话 verbatim (desc 显式 '真实用户原话（A-faithful，yifansun @ hfeg0pkn001，trace 1794202410355_ps4q9 U#0 逐字）：量测结果没抓出来，只调 parse_results.py' + "
        "verbatim '/home/yifansun/session_record.md 读取这个文件，继续进行这段工作，现在的问题是：result里量侧结果似乎没有抓出来，我们不许要动其他文件，只调整parse_results.py即可'); task_brief.md = 交付接口; "
        "track=faithful; reframe=None; layer=None; "
        "真实 FineSim .mt0 (真实 FineSimPro V-2023.12-1 export banner + 真实 13 列测量数据 + desc 显式 '4 个真实 FineSim .mt0 量测文件') + 真实 parse_results.py (真实 /proj/ddgoa 内网路径) + "
        "真实 session_record.md (真实用户 yifansun + 真实项目 ddgoa V0) + prompt.txt desc 显式 'A-faithful' + verbatim 用户原话 ⇒ file-verbatim (A-faithful, 真实 FineSim .mt0 + 真实 parse_results.py verbatim)",
    ),
    "EDA-Eval-DesignFlow-Mt0PvrefAbsGroupStat-001": (
        "A-faithful",
        "a7_AG_ThinFsComp_rerun.mt0 = 真实 FineSim .mt0 量测文件 (276 行, header 含真实 FineSimPro V-2023.12-1 export banner '$DATA1 SOURCE=\\'FineSimPro\\' VERSION=\\'V-2023.12-1\\' PARAM_COUNT=1' + "
        ".TITLE '' + 真实 5 列 pvref/voffset_vout_d_mv/voffset_vout_u_mv/temper/alter# + 真实 pvref=0.15/0.35/0.55 三组共 273 行数据 + 真实 PVT 数据 (pvref 0.15: -1.4982e-01/-1.5101e-01/85C/alter#1, pvref 0.55: -6.7946e-01/-6.8102e-01/85C/alter#1, 多 alter# 多温度 -40/85 等); "
        "desc 显式 'A-faithful 资产：FineSim .mt0 量测文件（Fscomp_vth，pvref/voffset_vout_d_mv/voffset_vout_u_mv/temper/alter# 五列，pvref=0.15/0.35/0.55 三组共273行）。来自 trace declanzh@hfeg0pkn002 yez2i 真实附件' — 显式 'A-faithful 资产' + '真实附件' 标注); "
        "task_brief.md = 交付接口 (处理脚本接受 .mt0 路径为 argv[1], 在同目录写 <name>_grouped.txt); "
        "prompt = verbatim 用户原话 '/rundata/drcpa/V0/simdir/hspice/declanzh/a7_ThinFsComp_SIM/All_run/vcap/Fscomp_vth/a7_AG_ThinFsComp_rerun.mt0 帮我把相同的pvref归类...'; "
        "track=faithful; reframe='FineSim .mt0 pvref 归类+abs min/max 处理器->produce-tool (harness produce-action file->produce-tool mt0 parser reframe, §4 有牙必要, r750 spotcheck batch28)'; layer=L1; "
        "真实 FineSim .mt0 (真实 FineSimPro V-2023.12-1 export banner + 真实 276 行 pvref 数据 + desc 显式 'A-faithful 资产' + '真实附件' + '来自 trace declanzh@hfeg0pkn002 yez2i') "
        "⇒ file-verbatim (A-faithful, 真实 FineSim .mt0 + desc 显式 'A-faithful 资产' 标注)",
    ),
}


def main():
    applied = []
    skipped = []
    before = 0

    # pre-count
    for fname in sorted(os.listdir(CASES_B)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CASES_B, fname), encoding="utf-8") as f:
            d = json.load(f)
        if d.get("metadata", {}).get("asset_fidelity") is not None:
            before += 1

    for cid, (val, _rationale) in BATCH.items():
        fpath = os.path.join(CASES_B, cid + ".json")
        if not os.path.exists(fpath):
            skipped.append((cid, "file not found"))
            continue
        with open(fpath, encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "asset_fidelity" in md:
            skipped.append((cid, "already has asset_fidelity=%r" % md["asset_fidelity"]))
            continue
        # append asset_fidelity as 末位 key (preserve key order)
        md["asset_fidelity"] = val
        d["metadata"] = md
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        applied.append((cid, val))

    print("=== 档2 asset_fidelity backfill r811 batch11 ===")
    print("to apply:", len(BATCH), "| applied:", len(applied), "| skipped:", len(skipped))
    print("coverage: before=%d -> after=%d (delta=+%d)" % (before, before + len(applied), len(applied)))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-58s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIPPED  %-58s : %s" % (cid, reason))

    dist = Counter(v for _, v in applied)
    print("\n--- value distribution ---")
    for v, c in sorted(dist.items()):
        print("  %-14s : %d" % (v, c))

    # write manifest
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r811_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r811_manifest.tsv — r811 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch11 (12 cases, alphabetical next 12 missing after r810 batch10 ModelQaRefactorAnalyze: MonteCarloDeckGen..Mt0PvrefAbsGroupStat, M 段尾部)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r810 档2 batch1-10 (+120, 106→226) done. 本轮 r811 档2 batch11.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'原始'/'Real content from'/'elided for brevity' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / 'portable mirror' / '示例' / '样例' / '合成' / '忠实复刻' / 'decoy' distractor 添加 / fake header / placeholder foundry 名 / 无 verbatim 标注\n")
        f.write("# 关键发现: 'Real content from' + 'elided for brevity' 双信号族首例 (MrrTaskSignatureExtract, A-faithful, 与 r810 ModelQaRefactorAnalyze task_spec verbatim + r805 'reproduced faithfully' 同型) / 'decoy' 添加 distractor 首例 (MrSelfClearExpDiag, synth_data, fabrication vs elision 判别线实证: MrrTaskSignatureExtract 'elided for brevity' 无 fabrication=A-faithful vs MrSelfClearExpDiag 'decoy MR1/MR4' 有 fabrication=synth_data) / 'portable mirror' 显式合成信号新增 (MonteMt0Stats, 与 'auto-generated stub' 同列) / '逐字'+'原始' desc 标注族新增 (MosDcGuiTool example_*.sp) / 'A-faithful 资产... 真实附件' desc 标注 (Mt0PvrefAbsGroupStat) / '4 个真实 FineSim .mt0' + prompt.txt 'A-faithful' desc 标注 (Mt0ParseFix) / 真实 FineSim deck 无合成标记 (MonteCarloDeckGen) / '示例' task_brief 覆盖 real export banner (Mt0AggMinMax, 与 r810 McLisSnmExtractor '示例 .lis 无 export banner' 形成 '示例 .mt0 有 export banner' 中间态) / '忠实复刻' 格式重建声明 + desc '合成' 覆盖 real export banner (Mt0MetastabDiag) / '按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）' desc 显式合成 (Mt0FolderAggStat) / fake header + Python-random 数据 (Mt0MeasureStat) / fake header + 非标准 control line + 资产路径非标准 (Mt0GroupedStatsGen) / track≠asset_provenance 本批 2 例 (累计 18→20: MonteMt0Stats track=faithful 记 prompt verbatim + asset=portable mirror 合成 / Mt0FolderAggStat track=faithful 记 prompt verbatim + asset=合成 .mt0 已被集群清理) / A-faithful 5/12=42% 累计 52/132=39% / 强信号新增 1 类 ('Real content from' + 'elided for brevity' 双信号族)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 226->238 (cases/B 238==B.jsonl 238 ✓); miss 169->157\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
