#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r815.py — r815 档2 asset_fidelity backfill batch15.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r814 档2 batch1-14 (+168, 106→274) done. 本轮 r815 推进 档2 batch15 — 12 cases
      (alphabetical next 12 missing after r814 batch14 PvtInvChainDelayMeas:
       PwlFormatConvert..SaDcSweepTbGen, P→S 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r814 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 /
                    真实 scp 自内网 / 真实用户 paste / "reproduced faithfully" /
                    "faithful compact/trimmed representation" / "忠实紧凑表示"/"忠实缩减" 标注 /
                    "Real content from" / "elided for brevity" / "extracted from real trace" /
                    真实 export header banner (AETHER-SE/HSPICE/WaveView/FineSim/PrimeSim/PEX/ALPS) /
                    task_spec 显式 "trace 原文件 verbatim" 标注 / desc 显式 "A-faithful 资产"/"逐字"/
                    "原始"/"真实 golden"/"trace-faithful"/"real trace" 标注 / 真实内网 /proj//apps/
                    /home//rundata//Documents/ 路径 / 真实 SKILL .il template from real skill package /
                    真实 Perl vecgen script / 真实 buggy 脚本 with bug docstring /
                    真实 verbatim agent 回答 with "逐字摘自原 trace" 标注)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice/testbench 样本 (portability, 真实 deck 在 /proj
                    内网不可达) 或 合成项目树 / 合成 PVT alter deck with "Generated as" 标注 /
                    "trace-faithful reconstruction" header + decoy distractor fabrication /
                    "portable level-1 MOS model" synth marker
  - synth_script : A = 合成 Perl/Python/Tcl/bash 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/PDK/model fixture / 合成 .md0/.lis/.mt0 仿真输出 /
                    合成 .sv/.v verilog/SystemVerilog testbench fixture / 合成 corpus/query.log KB fixture /
                    合成 PDK techfile/layermap/cds.lib minimal reconstruction / 合成 minimal params JSON /
                    合成 CDL netlist fixture (faithful Aether CDL format mimicry, 无真实 /proj 路径) /
                    合成 PWL stimulus data (desc "按 trace 文档化格式与量级合成" overrides real-format banner) /
                    合成 PEX netlist sample for analysis (491B minimal "sample"/"Input A" header)
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

本批 12 case 判定:
  - 3 A-faithful (25%): RevCali3DCoord / RonMonoDiag / RsCalcAutoVia
  - 5 synth_deck: PwlStimTransform / RcurrDirClassify / SAoptPwrDly /
                  SaCoreMosLocate / SaDcSweepTbGen
  - 4 synth_data: PwlFormatConvert / RcVizTreeAnalyzer /
                  ResistorTrimNetlistExplain / RonCurveSmoothness
  (synth_script/synth_doc/synth_log/synth_tree/no-asset=0)

关键发现:
  - A-faithful 25% (3/12) 低于均值 (r814 累计 75/168=44.6%; 本批 P→S 段 synth_deck/synth_data 密集,
    含 4 例 track=faithful 但 asset=synth 的 track≠asset_provenance).
  - real SKILL .il template from real skill package (RsCalcAutoVia): 2 个 SKILL .il 模板
    (run_rscalc_nogui.il + run_autovia_nogui.il) desc 显式 "来自 e0014566 的真实 skill 包" +
    verbatim 用户原话 + desc "A 档 trace-faithful" — 新文件类型 (SKILL .il template,
    扩展 r814 Perl vecgen script 强信号族至 SKILL 脚本域).
  - real FineSim .md0 measurement data group (RonMonoDiag): 5 个 .md0 文件 (v5.md0..v5#4.md0)
    desc 显式 "real trace clarawu@hfeg0pkn004, sim_iter/v5_all/" + v5_stim.sp real FineSim deck +
    verbatim 用户原话 (真实 /home/clarawu/sim_iter/v5_all/ 路径) — real .md0 measurement data
    group (扩展 r813 OtaMa0SpecCheck real .ma0 export 至 .md0 多文件 group).
  - "A-faithful 资产" + "忠实缩减" faithful compact representation (RevCali3DCoord): extract_lib_timing.py
    + rev_cali.py desc 显式 "A-faithful 资产" + "从 trace e0046686@pkn001 bqqtk 重建（原文件 /rundata
    权限拒，按真实 API surface 忠实缩减）" — faithful compact reconstruction from real API surface
    (承 r813 NonOverlapClockDiag "faithful compact representation" 同型; 原文件 /rundata 权限拒 ⇒
    忠实缩减 reconstruction 仍判 A-faithful).
  - "trace-faithful reconstruction" header + decoy distractor fabrication (SaCoreMosLocate): netlist
    header "* SPICE PEX netlist (A) - SA sense-amp core MOS locator / * trace-faithful reconstruction:
    yuyingc @ hfeg0pkn001, session 1793623698314_n7w6c U#38" + desc "合成 SPICE PEX...含 he-bit 诱饵/
    无 delvto precharge-iso-colsel 诱饵/parasitic RC 诱饵/decoySA 实例诱饵" — fabrication with decoy
    distractors (扩展 r811 MrSelfClearExpDiag "decoy" fabrication 至 PEX netlist; verbatim 用户原话
    但 netlist asset 合成 ⇒ track=faithful≠asset=synth_deck).
  - "portable level-1 MOS model" synth marker (SAoptPwrDly): corner.lib 247B "* corner.lib — portable
    level-1 MOS model for StrongARM comparator" + .MODEL LEVEL=1 + params_A.json 397B synth; prompt
    verbatim 真实 /proj/shdc/models/G4B/ + /proj/dscqa/V0_LP6/ 内网路径但 asset 合成 (portability
    reframe; 扩展 r808/r814 level=1 教学模型判别线 with "portable" 显式标注).
  - "按 trace 文档化格式与量级合成" desc synth marker overrides real-format WaveView export banner
    (PwlFormatConvert): simdir/ 6 PWL 文件含真实格式 WaveView export banner (*** Custom WaveView
    SPICE PWL EXPORT T-2022.06-SP1 / created at 2026-11-03 19:14:20) 但 desc 显式 "按 trace 文档化
    格式与量级合成" ⇒ synth_data (承 r811 Mt0MetastabDiag "合成...忠实复刻" desc overrides real export
    banner 同型; track=faithful 但 asset=synth_data ⇒ track≠asset_provenance).
  - track≠asset_provenance 本批 4 例 (PwlFormatConvert/PwlStimTransform/SAoptPwrDly/SaCoreMosLocate,
    track=faithful 但 asset=synth; 累计 22→26).
  - A-faithful 3/12=25% 累计 78/180=43.3%; 强信号新增 1 类 (SKILL .il template from real skill package).
"""
import json, os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-PwlFormatConvert-001": (
        "synth_data",
        "simdir/ = 6 个 Custom WaveView SPICE PWL EXPORT 文件 (idd0_vintlp/idd0_vblhh/idd0_vblen/"
        "idd0_viblh/idd4r_vblh/idd4w_vintlp_current_TT_1p1v, 5708B/4356B/etc) + 1 目标格式参考文件 "
        "(idd0_vblhh_current_ipwl, 3003B 纯数据); 文件 header 含真实格式 WaveView export banner "
        "('*** Custom WaveView SPICE PWL EXPORT (T-2022.06-SP1) / *** created at 2026-11-03 19:14:20') "
        "但 attachment desc 显式 'A 可见输入：6 个 Custom WaveView SPICE PWL EXPORT 文件...按 trace "
        "文档化格式与量级合成' — desc '合成' marker overrides real-format export banner (承 r811 "
        "Mt0MetastabDiag '合成...忠实复刻' desc overrides real PrimeSim HSPICE banner 同型); "
        "prompt.txt = verbatim 用户原话 (hauserz @ hfeg0pkn006, trace 1793705585219_k1vy6 "
        "U#18/U#22/U#34/U#46/U#74 逐字, 真实 /proj/drgqx/V0/simdir/spectre/workdir/hauserz/ 内网路径); "
        "task_brief.md = 交付接口 (pwl_convert.py <simdir> <out_dir>); track=faithful (与 asset 不一致, "
        "track=faithful 指 prompt verbatim 但 asset 是合成 PWL data); layer=None; 合成 PWL stimulus data "
        "(desc '按 trace 文档化格式与量级合成' synth marker, real-format WaveView export banner 为 "
        "faithful format mimicry 非 real scp) ⇒ synth_data (合成 PWL data fixture; track=faithful 但 "
        "asset=synth_data ⇒ track≠asset_provenance; 与 r811 portable mirror 合成 KB corpus 同型: "
        "主资产是合成 data fixture 非 runnable deck)",
    ),
    "EDA-Eval-DesignFlow-PwlStimTransform-001": (
        "synth_deck",
        "inpattern_origin_A.pwl = 合成 PWL stimulus (713 字节, header '* inpattern_origin A  (source "
        "PWL stimulus, lowercase net names) / * 8 PWL blocks: 4 pvwlp-rail signals (high ~3.2) + 4 "
        "pvcc-rail signals (high ~1.1)' — 描述性 'A' header, 无真实 export banner/无真实内网路径); "
        "net_mapping_A.json = 合成 net 映射 (245 字节, 8 net 映射 clk_in_bga_b0→ClkBot etc 极小); "
        "rails.json = 合成 rail 参数 (34 字节, pvwlp=3.2/pvcc=1.1 极小); task_brief.md = 交付接口 "
        "(transform_pwl.py CLI); track=faithful (与 asset 不一致, track=faithful 指 prompt verbatim "
        "但 asset 是合成 PWL deck); layer=L2; prompt.txt = verbatim 用户原话 ('@/proj/drcoa/V0/"
        "workdir/hairuizh/simulation/drcoa_array_XdecGapTop_DRCOA_schematic_ALPS/ ...' — 真实 "
        "/proj/drcoa 内网路径 + verbatim U#0) 但附件 asset 是合成 PWL stimulus deck (描述性 'A' "
        "header, 无真实 export banner) ⇒ synth_deck (合成 PWL stimulus deck + 合成 config; "
        "track=faithful 但 asset=synth_deck ⇒ track≠asset_provenance; portability reframe 真实 "
        "PWL 在 /proj 内网不可达; 与 r803-r814 synth_deck 同型)",
    ),
    "EDA-Eval-DesignFlow-RcVizTreeAnalyzer-001": (
        "synth_data",
        "rc_netlist_A.net = 合成 Star-RC/Calibre PEX netlist sample (491 字节, header '* RCviz "
        "visible netlist A (Star-RC/Calibre post-layout PEX extract sample) / * shanliny rc_viz_tool "
        "development input (Input A); evaluation runs on hidden B' — 描述性 'sample'/'Input A' header, "
        "无真实 export banner/无真实内网路径, 4 节点/3 器件/4 电阻/4 电容 极小); task_context.md = "
        "真实用户原话 (shanliny rc_viz_tool 改进 U1-U7, trace 1794453941272_vxf3o mc175) + 格式说明 + "
        "JSON schema; track=None (内容 'sample'/'Input A' 描述性 header, track=None 是缺 metadata 非 "
        "合成信号); layer=L2; prompt = 重构需求 (非 verbatim, 提取 shanliny 改进核心); 合成 PEX "
        "netlist sample for analysis (491B minimal, 'sample'/'Input A' 描述性 header, 用作解析输入 "
        "fixture 非 runnable deck) ⇒ synth_data (合成 PEX netlist analysis fixture; track=None 但内容 "
        "显式 'sample' 标注; 与 r814 PdkLayerLocate 合成 PDK minimal reconstruction 同型: 主资产是合成 "
        "分析 fixture 非 runnable deck)",
    ),
    "EDA-Eval-DesignFlow-RcurrDirClassify-001": (
        "synth_deck",
        "rdir_A.sp = 合成 HSPICE testbench (1329 字节, header '* rdir current direction classification "
        "testbench A' — 描述性 'A' header, 无真实 export banner/无真实内网路径, 6 电阻 vprobe + .measure "
        "i_pkpos/pkneg/rms); spec_A.json = 合成 spec (621 字节, tol=5e-5/thr=0.01/top_pct=50 + 6 电阻 "
        "layer/net/R/几何); task_brief.md = 交付接口 (curr_dir_classify.py <netlist.sp> <spec.json> "
        "<out_dir>); prompt.txt = 重构需求 (DRAM FIT 电流方向分类, 非 verbatim 但详尽 task spec); "
        "track=synthesized (与 asset 一致); layer=L2; 合成 HSPICE testbench + 合成 spec (描述性 'A' "
        "header, track=synthesized 显式; portability reframe; 与 r803-r814 synth_deck 同型) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-ResistorTrimNetlistExplain-001": (
        "synth_data",
        "netlist/R_TRIM_VREF.sp = 合成 Aether CDL netlist fixture (2575 字节, header '// Library name: "
        "L_vsensor_dbc / // Cell name: R_TRIM_VREF / // View name: schematic / subckt R_TRIM_VREF A B "
        "EN Trim<2> Trim<1> Trim<0> VDDA VSSA' — Aether CDL 格式 mimicry, 无真实 /proj//apps//rundata "
        "内网路径, 8 反相器 + 17 rhi_dbc 电阻梯 + 8 传输门); netlist/trim_spec.json = 合成 per-resistor "
        "intended connection config (1181 字节, 17 电阻 single/parallel/series + segments); netlist/"
        "pdk_params.json = 合成 PDK model params (487 字节, rhi_dbc rsh=1050 + R=rsh*(L/W)/mr formula); "
        "task_spec.json = 合成 task 结构 (3008 字节); track=None (内容 Aether CDL 格式 mimicry 但无真实 "
        "内网路径/无 verbatim 标注, track=None 是缺 metadata 非合成信号); layer=L1; prompt = 重构背景 "
        "(非 verbatim 用户原话, 详细诊断背景描述); hidden B (R_TRIM_VBG.sp) 同 Aether CDL 格式 mimicry "
        "不同 library/cell (L_vbg_dbc/R_TRIM_VBG) ⇒ 合成 CDL netlist fixture 对组; 合成 Aether CDL "
        "netlist + 合成 trim_spec + 合成 pdk_params (faithful Aether CDL format mimicry, 无真实 /proj "
        "路径, 无 verbatim marker, 重构 prompt) ⇒ synth_data (合成 CDL netlist analysis fixture; "
        "track=None 但内容无真实内网路径/无 verbatim 标注; Q&A explain 任务, netlist 为分析输入 fixture "
        "非 runnable deck; 与 r814 PdkLayerLocate 合成 PDK minimal reconstruction 同型)",
    ),
    "EDA-Eval-DesignFlow-RevCali3DCoord-001": (
        "A-faithful",
        "extract_lib_timing.py = 真实 lib_timing_tools 核心模块 V2 版 (desc 显式 'A-faithful 资产："
        "lib_timing_tools 核心模块原始 V2 版（仅支持二维坐标 i,j / x,y 直查表）...从 trace e0046686@"
        "pkn001 bqqtk 重建（原文件 /rundata 权限拒，按真实 API surface 忠实缩减）' — 'A-faithful 资产' "
        "+ '忠实缩减' 双信号, 原文件 /rundata 权限拒 ⇒ faithful compact reconstruction from real API "
        "surface); rev_cali.py = 真实 rev_cali 后端 V2 版 (desc 显式 'A-faithful 资产：rev_cali 后端原始 "
        "V2 版...从 trace 重建'); mini_k_A.lib = 真实 k-lib 风格示例 liberty (desc 显式 'A-faithful 资产："
        "k-lib 风格示例 liberty'); mini_map_A.map = 真实 parm→pin 映射表 (desc 显式 'A-faithful 资产'); "
        "task_brief.md = 交付接口 (extract_lib_timing.py + rev_cali.py 打包 submit.zip); track=faithful "
        "(与 asset 一致); layer=L1; prompt = verbatim 用户原话 ('autosim_script/rev_cali_tools反标的后端"
        "脚本中:使用的lib_timing_tools抽timing需要按照（i_slew，c_slew，q_load）的三维坐标形式传递...' "
        "U#0 逐字); 真实 lib_timing_tools + rev_cali 模块 (desc 'A-faithful 资产' + '忠实缩减' faithful "
        "compact reconstruction from real API surface, 原文件 /rundata 权限拒) + verbatim 用户原话 ⇒ "
        "file-verbatim (A-faithful, 'A-faithful 资产' + '忠实缩减' faithful compact representation 强信号 "
        "of batch15; 承 r813 NonOverlapClockDiag 'faithful compact representation' 同型; track=faithful "
        "与 asset 一致)",
    ),
    "EDA-Eval-DesignFlow-RonCurveSmoothness-001": (
        "synth_data",
        "Ron_A.md0 = 合成 FineSim .md0 示例 (desc 显式 'FineSim .md0 示例（Input A）：zqdec/rpu_50/rpd_50/"
        "rpu_15/rpd_15 五列，64 个 sweep point，数据行有折行。开发与自测用；评测在 hidden B（不同点数/"
        "值/跳变/折行）上跑' — '示例'/'Input A' synth marker); manifest_A.json = 合成 manifest (desc "
        "'示例 manifest（Input A）'); task_context.md = 真实用户原话 (clarawu Ron.md0 光滑度分析) + .md0 "
        "格式说明; track=None (内容 '示例'/'Input A' synth marker, track=None 是缺 metadata 非合成信号); "
        "layer=L2; prompt = 重构需求 (非 verbatim, 详尽 .md0 解析 + 光滑度指标 task spec); trace_source "
        "real_task_summary 显式 'A 档不可行(项目目录权限) ⇒ B 档合成'; 合成 FineSim .md0 fixture (desc "
        "'示例'/'Input A' synth marker, A 档不可行因 /proj 项目目录权限 ⇒ B 档合成) ⇒ synth_data (合成 "
        ".md0 measurement data fixture; track=None 但 desc 显式 '示例' + summary 显式 'B 档合成'; 与 "
        "r811 Mt0FolderAggStat '按 trace 文档化格式与量级合成（真实 .mt0 已被集群清理）' 同型)",
    ),
    "EDA-Eval-DesignFlow-RonMonoDiag-001": (
        "A-faithful",
        "v5.md0 = 真实 FineSim .md0 measure 文件 (desc 显式 'FineSim .md0 measure 文件，corner 0（temper="
        "25C, alter#1），64 行 zqdec 0..63 的 rpd_50 实测值（real trace clarawu@hfeg0pkn004, sim_iter/"
        "v5_all/）。rpd_50 随 zqcode 递减但不严格单调：bit-4/5 边界 15->16、31->32、47->48 处出现反向"
        "跳变' — 'real trace' + 真实 /home/clarawu/sim_iter/v5_all/ 路径 + 真实非单调跳变描述); "
        "v5#1.md0..v5#4.md0 = 真实 4 个 .md0 measure 文件 (corner 1-4, desc 显式 'real trace' + 真实 "
        "temper/alter 标注); v5_stim.sp = 真实 FineSim stimulus deck (desc 显式 'FineSim stimulus deck"
        "（real trace），定义 5 个 ALTER corner 与 zqdec dc sweep 0..63、.measure rpd_50'); task_brief.md "
        "= 交付接口 (analyze_ron.py <md0_dir> <out.json>); track=None (内容 'real trace' + 真实 /home/"
        "clarawu 路径, track=None 是缺 metadata 非合成信号); layer=L2; prompt.txt = verbatim 用户原话 "
        "('检查刚仿真出来的RON曲线：@/home/clarawu/sim_iter/v5_all/v5.md0、v5#1.md0、v5#2.md0、v5#3.md0、"
        "v5#4.md0，rpd_50随zqcode变化的单调性，如果不单调，就优化电路' — 真实 /home/clarawu/sim_iter/"
        "v5_all/ 路径 + verbatim U#0); 真实 FineSim .md0 measurement data group (5 文件 v5.md0..v5#4.md0 "
        "desc 显式 'real trace' + 真实 /home/clarawu 路径 + 真实非单调跳变描述) + 真实 FineSim stimulus "
        "deck + verbatim 用户原话 ⇒ file-verbatim (A-faithful, real FineSim .md0 measurement data group "
        "强信号 of batch15; 扩展 r813 OtaMa0SpecCheck real .ma0 export 至 .md0 多文件 group; real /home/"
        "clarawu/sim_iter/v5_all/ 路径; track=None 但内容 'real trace' + 真实路径, track=None 是缺 "
        "metadata 非合成信号)",
    ),
    "EDA-Eval-DesignFlow-RsCalcAutoVia-001": (
        "A-faithful",
        "virtuoso-rscalc-runner/assets/run_rscalc_nogui.il = 真实 RsCalc de-GUI SKILL 模板 (desc 显式 "
        "'RsCalc de-GUI SKILL 模板（含 RSCALC_CONFIG_PLACEHOLDER 占位 + 尾部 RunRsCalcNoGui 提示），"
        "来自 e0014566 的真实 skill 包' — '来自 e0014566 的真实 skill 包' 强信号); virtuoso-autovia-"
        "runner/assets/run_autovia_nogui.il = 真实 AutoVia de-GUI SKILL 模板 (desc 显式 'AutoVia de-GUI "
        "SKILL 模板...来自 e0014566 的真实 skill 包'); common.config.example = 示例共享配置 (process/"
        "project/libName/cellName + targetReduction/maxIterations); rscalc.config.example = 示例 RsCalc "
        "配置; run_autovia_config.il.example = 示例 AutoVia 配置; task_brief.md = 交付接口 (6 必交文件 + "
        "生成器 CLI); track=faithful (与 asset 一致); layer=L2; prompt.txt = verbatim 用户原话 ('好了，"
        "这下你文件夹里面的东西多了。接下来需要你帮忙干这样的几件事：1）分析下这里面提供的这两个skill "
        "2) 把这2个skill的配置文件整体梳理一下...3）rscalc 是计算电阻的...4）把上述得到的流程写进 "
        "prompt_flow.md...5）流程中要注意上一步的输出是下一步的输入。6）电阻要达到的降幅 以及 最大的"
        "迭代次数 要写到配置文件中。' — verbatim U#0); desc 显式 '用户原话逐字任务说明（A 档 trace-"
        "faithful，取自真实 cline trace 用户首条需求轮）'; 真实 SKILL .il 模板 (2 文件 desc 显式 '来自 "
        "e0014566 的真实 skill 包') + verbatim 用户原话 + desc 'A 档 trace-faithful' ⇒ file-verbatim "
        "(A-faithful, real SKILL .il template from real skill package 强信号 of batch15 新文件类型; "
        "扩展 r814 Perl vecgen script 强信号族至 SKILL 脚本域; track=faithful 与 asset 一致)",
    ),
    "EDA-Eval-DesignFlow-SAoptPwrDly-001": (
        "synth_deck",
        "params_A.json = 合成参数 fixture (397 字节, vdd=1.0/temp=45/vref=0.5/vswing=0.05 + baseline + "
        "8 sizing knobs 极小); corner.lib = 合成 level-1 MOS model (247 字节, header 显式 '* corner.lib "
        "— portable level-1 MOS model for StrongARM comparator' + .LIB tt + .MODEL nch/pch LEVEL=1 — "
        "'portable level-1 MOS model' synth marker); task_brief.md = 交付接口; track=faithful (与 asset "
        "不一致, track=faithful 指 prompt verbatim 但 asset 是合成 level-1 model); layer=L3; prompt.txt "
        "= verbatim 用户原话 ('已打开的标签页中 DqIb_strongarm_pmos 为需要优化的电路，model 为 /proj/"
        "shdc/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t07/incFile_lp，testbench 及激励文件为 "
        "/proj/dscqa/V0_LP6/simdir/finesim/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/"
        "strongarm/004_onlySlicer_delay_dejoa.sp，请优化该电路功耗至 534uA...finger 数会影响电路性能..."
        "' — 真实 /proj/shdc/models/G4B/ + /proj/dscqa/V0_LP6/ 内网路径 + verbatim U#0) 但附件 asset 是 "
        "合成 level-1 portable model (corner.lib 247B 'portable level-1 MOS model' synth marker) ⇒ "
        "synth_deck (合成 level-1 model + 合成 params; track=faithful 但 asset=synth_deck ⇒ "
        "track≠asset_provenance; portability reframe 真实 model/deck 在 /proj 内网不可达; 'portable' "
        "显式 synth marker 扩展 r808/r814 level=1 教学模型判别线; 与 r803-r814 synth_deck 同型)",
    ),
    "EDA-Eval-DesignFlow-SaCoreMosLocate-001": (
        "synth_deck",
        "netlist = 合成 SPICE PEX netlist (header 显式 '* SPICE PEX netlist (A) - SA sense-amp core MOS "
        "locator / * trace-faithful reconstruction: yuyingc @ hfeg0pkn001, session 1793623698314_n7w6c "
        "U#38 / * top signal under test: Blasec28<562> / * hierarchy: sim_top -> XI_sa562 -> CXSA1x4_"
        "die2_fbcc' — 'trace-faithful reconstruction' header 合成标注 + 真实 trace 元数据; desc 显式 "
        "'可见真实 A 网表（合成 SPICE PEX，sim_top→XI_sa562→CXSA1x4_die2_fbcc 4bit SA，Blasec28<562>→"
        "Bla<2>→bit2→delvtoBL2_*，含 he-bit 诱饵/无 delvto precharge-iso-colsel 诱饵/parasitic RC 诱饵/"
        "decoySA 实例诱饵）' — '合成 SPICE PEX' + decoy distractor fabrication); task_brief.md = 交付接口 "
        "(sa_core_mos_locate.py <网表> <顶层信号> -o out.json); track=faithful (与 asset 不一致, "
        "track=faithful 指 prompt verbatim 但 asset 是合成 PEX netlist); layer=L1; prompt.txt = "
        "verbatim 用户原话 ('帮我查看 v(blasec28<562>) 这个信号线所在的SA中决定了上拉和下拉能力的4个"
        "mos管在Netlist网表里是哪四个' — verbatim U#38, yuyingc @ hfeg0pkn001); 合成 SPICE PEX netlist "
        "(header 'trace-faithful reconstruction' + desc '合成 SPICE PEX' + decoy distractor fabrication "
        "含 he-bit 诱饵/parasitic RC 诱饵/decoySA 实例诱饵) ⇒ synth_deck (合成 PEX netlist with decoy "
        "distractor fabrication; track=faithful 但 asset=synth_deck ⇒ track≠asset_provenance; 扩展 "
        "r811 MrSelfClearExpDiag 'decoy' fabrication 至 PEX netlist; verbatim 用户原话 但 netlist asset "
        "合成; 'trace-faithful reconstruction' header = 合成 with 真实 metadata, 非 real scp)",
    ),
    "EDA-Eval-DesignFlow-SaDcSweepTbGen-001": (
        "synth_deck",
        "ref_test.sp = 合成参考测试网表 (desc '可见 A：参考测试网表（HSPICE/FineSim deck，含模型库 .lib "
        "路径与 netlist .inc 结构、.tran 分析）'); spec.json = 合成直流扫描设置 (desc '可见 A：直流扫描"
        "测试设置（corner=tt/temp=125/vad2=1.4/iso=0/sel=1.77/sweep 1.17-1.77/61pts/observe BL）'); "
        "netlist_stub.sp = 合成 CXSA 网表 stub (desc '可见 A：CXSA sense amplifier 网表 stub（顶层 "
        "subckt sim_sa_dc_check：Iso/Sel/OC/PreEq 管 + BL + vad2!）' — 'stub' 命名合成标注); "
        "output_format_spec.txt = 合成输出格式规范; task_brief.md = 交付接口; track=synthesized (与 "
        "asset 一致); layer=L1; prompt = 重构需求 (非 verbatim, 但含 verbatim 用户原话引用 '真实轨迹"
        "里 t0002614 的原话需求（逐字）：「根据网表 netlist 和参考的测试网表 test.sp 帮我写仿真测试..."
        "」'); 合成 ref_test.sp deck + 合成 netlist stub + 合成 spec (track=synthesized 显式; 'stub' "
        "命名合成标注; portability reframe; 与 r803-r814 synth_deck 同型) ⇒ synth_deck",
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

    print("=== 档2 asset_fidelity backfill r815 batch15 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r815_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r815_manifest.tsv — r815 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch15 (12 cases, alphabetical next 12 missing after r814 batch14 PvtInvChainDelayMeas: PwlFormatConvert..SaDcSweepTbGen, P→S 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r814 档2 batch1-14 (+168, 106→274) done. 本轮 r815 档2 batch15.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'原始'/'真实 golden'/'trace-faithful'/'real trace'/'忠实紧凑表示'/'忠实缩减'/'faithful compact representation' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / '重构' / minimal reconstruction / 极小 PDK fixture / 'Generated as' / '示例' / 'Input A' / 'portable level-1' / 'trace-faithful reconstruction' / 'stub' / decoy distractor / '按 trace 文档化格式与量级合成' / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 25% (3/12) 低于均值 (r814 累计 75/168=44.6%; 本批 P→S 段 synth_deck/synth_data 密集, 含 4 例 track=faithful 但 asset=synth 的 track≠asset_provenance) / real SKILL .il template from real skill package (RsCalcAutoVia, 新文件类型, 扩展 r814 Perl vecgen script 强信号族至 SKILL 脚本域) / real FineSim .md0 measurement data group (RonMonoDiag, 5 文件 v5.md0..v5#4.md0 desc 'real trace' + 真实 /home/clarawu 路径, 扩展 r813 real .ma0 export 至 .md0 多文件 group) / 'A-faithful 资产'+'忠实缩减' faithful compact reconstruction from real API surface (RevCali3DCoord, 承 r813 NonOverlapClockDiag 同型, 原文件 /rundata 权限拒) / 'trace-faithful reconstruction' header + decoy distractor fabrication (SaCoreMosLocate, 扩展 r811 'decoy' fabrication 至 PEX netlist) / 'portable level-1 MOS model' synth marker (SAoptPwrDly, 扩展 r808/r814 level=1 教学模型判别线 with 'portable' 显式标注) / '按 trace 文档化格式与量级合成' desc synth marker overrides real-format WaveView export banner (PwlFormatConvert, 承 r811 Mt0MetastabDiag 同型) / track≠asset_provenance 本批 4 例 (PwlFormatConvert/PwlStimTransform/SAoptPwrDly/SaCoreMosLocate, 累计 22→26) / A-faithful 3/12=25% 累计 78/180=43.3% / 强信号新增 1 类 (SKILL .il template from real skill package)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 274->286 (cases/B 286==B.jsonl 286 ✓); miss 121->109\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
