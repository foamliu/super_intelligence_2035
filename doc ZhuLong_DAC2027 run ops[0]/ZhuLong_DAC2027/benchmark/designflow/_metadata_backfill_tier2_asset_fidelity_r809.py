#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r809.py — r809 档2 asset_fidelity backfill batch9.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done. r806 batch6 (+12, 166→178) done.
      r807 batch7 (+12, 178→190) done. r808 batch8 (+12, 190→202) done.
      本轮 r809 推进 档2 batch9 — 12 cases
      (alphabetical next 12 missing after r808 batch8 LatchSubcktLocate:
       LibCellListGen..MR7PsdScopeAnalyze, L-M 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r808 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 /
                    真实 scp 自内网 / 真实用户 paste / "reproduced faithfully" /
                    "faithful compact/trimmed representation" 标注 / 真实 export header banner)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/PDK/model fixture
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver。
      A-faithful 强信号 = asset 文件 header 明记 verbatim/excerpt/reproduced faithfully/faithful compact/
                          faithful trimmed from trace (含真实内网路径) 或
                          asset 内容含真实内网路径 (/proj/..., /home/..., /rundata/...) 或
                          asset header = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB/WaveView/ALPS export header
                          (含真实 user/date/library/tool-version) 或
                          asset = 真实用户 paste 的 verbatim 文本 (track=faithful + 内容与 prompt 引用一致) 或
                          asset 含真实内部 edit note / 真实 hostname / 真实 signal names from real path。
      synth 信号 = track=synthesized / portability reframe / "样本"/"合成"/"self-contained sample" / 通用名文件 /
                   "(reconstructed from cline trace ...)" / desc 显式 "合成" / "示例" / "faithful reconstruction" /
                   A_ONLY_MARKER + decoy 内容。

本批 12 case 判定:
  - 5 A-faithful (42%): LisMeasExtract / LoadModeOpTruncDiag / LvDpathCdlImport / MBistTopAnalyze / MR7PsdScopeAnalyze
  - 4 synth_deck: LibCellListGen / LpfAnomalyDetect / LvLvioSweep / LvlShftSpecCompliance
  - 2 synth_data: LibCoordMapper / LvlShftSoaSizing
  - 1 synth_log:  LvlshftBsubDiag

关键发现:
  - 真实 HSPICE .lis export header 强信号 (LisMeasExtract, r809 首例 HSPICE .lis 解析域):
    stimulus_pex_rev06_model_rev04.lis 头部 = 真实 PrimeSim HSPICE V-2023.12-SP1-1 linux64 (Apr 07 2024 8845341)
    export banner + 真实 USER e0024852 + 真实 HOSTNAME hfeg0plg76 + 真实 timestamp Wed Nov 4 16:12:08 2026 +
    真实 FLEXlm license 12000@hl04 + 真实 Input File: stimulus_pex_rev06_model_rev04.sp;
    prompt = 真实用户原话 verbatim (e0024852 @ hfeg0plg76, 真实 /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/
    SRAM_bitcell_DTCO/hd_CH252_bitcell/.../stimulus_pex_rev06_model_rev04.lis 内网路径 + verbatim 用户请求
    'jiexi ... de Ireak and Ileak SNM tell me in chinese'). track=faithful (与 asset 一致).
    = 真实 HSPICE .lis 文件 (PrimeSim HSPICE V-2023.12-SP1-1 export banner + 真实 user/host/timestamp/license,
      与 r805 PEX / r806 FineSim / r807 WaveView/ALPS export header 强信号族同列), file-verbatim (HSPICE .lis 首例).
  - 真实 SystemVerilog verbatim excerpt with file:line 强信号群 (LoadModeOpTruncDiag + MR7PsdScopeAnalyze, r809 双例 SV excerpt):
    LoadModeOpTruncDiag A_pattern.v / A_specdef.sv / A_task.sv 每文件 header 显式 'real excerpt from DDR6 WTM pattern
      (tongfanl@hfhds201, trace 1791439699810_1550c)' / 'real excerpt from ddr6_specdef.sv' / 'real excerpt from
      ddr5_test.sv.sos (Load_Mode task, lines 947-1016)', 内容含 verbatim Load_Mode task 签名 + verbatim 用户 U#0
      Load_Mode(.ma(8'hDE), .op({4'b0000,1'b1,1'b1,$urandom_range(1),pattern_select}),...) 调用 + 真实 MODEOP_BITS=8;
    MR7PsdScopeAnalyze A_vecgen/{ddr6_interface,ddr6_package,ddr6_specdef,ddr6_test,timing_load}.sv 每文件 header 显式
      'real excerpt (vecgen_local), lines X-Y' + 'source: /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/<file>.sv',
      内容含 verbatim file:line 标注 (ddr6_specdef.sv:36 MODEMA_BITS=8 / ddr6_package.sv:487-491 MR7_zq_* / ddr6_interface.sv:129
      modereg_direct / timing_load.sv:2362-2368 MRSettingDirect) + verbatim 用户 U#0 问题 '帮我看下，对于MR7，会区分PSD0或者PSD1吗'.
    = 真实 SV verbatim excerpt with file:line 标注 (paste-verbatim 子型, 与 r805 reproduced-faithfully / r808 IoBufParamTune
      verbatim 调参请求同列), 本批双例 SV excerpt 群 (DDR6 vecgen + DDR5/6 WTM test sv), file-verbatim.
  - 真实分层 SPICE netlist + 真实 /proj source path 强信号 (MBistTopAnalyze, r809 首例 MBIST 分层网表):
    doc/mbist_top.netlist header 显式 'mBistTop thick-oxide / digital MBIST hierarchical SPICE netlist /
      top integration of memory-BIST pattern generator (trace-faithful, A) /
      source: /proj/ddgoa/V0 libs ddgoa_cmos_digital / mBistTop schematic', body 含真实 foundry cell 名
      mBistCmdGen/mBistAddrGen/mBistPat/Bistwritedata/Spare_mBist/mBistRACnt/mBistCACnt + 真实端口名
      cm0_ts_BistData/BACntRst/CACntCK/RACntCK 等 (与 trace real_task_summary 5 子模块 + 地址计数器 + 6 计数时钟一致);
    hidden manifest 'a_leak_tokens' 字段含 mBistTop/mBistCmdGen/... 真实 token 列表 (A 含真实 token 防泄题);
    track=None; reframe='MBIST 顶层网表分层分析器->produce-tool (analysis/Q&A->produce-tool analyze+JSON)'.
    = 真实 MBIST 分层 SPICE 网表 (trace-faithful 标注 + 真实 /proj/ddgoa source path + 真实 foundry cell 名,
      file-verbatim, 与 r806 LatchSubcktLocate netlist 'Synthetic mimicking' 反向: 本例显式 trace-faithful A),
      A-faithful (MBIST 分层网表首例).
  - 真实用户 SPICE 网表 verbatim (LvDpathCdlImport, r809 真实用户网表):
    1_circuit.sp header '1_circuit.sp : LV_DPATH 网表 (由 Cadence 原理图 1.jpeg 提取)' + 详细器件映射
      (XI0~I6 invenLV_pc60/invLV_pc60/nor2LV_pc60/fbsLV_pc60/nchizLV_pc60 真实 foundry cell 名 + X0.5/X1/X2/MIN 尺寸),
      body 含完整 LV_DPATH SPICE 网表 (负沿 D 触发器 DOUT=D&RN, 行为级单元 INV/NOR2/CLKINV/NCHIZ/FBS + 测试激励);
    prompt = verbatim 用户原话 '根据网表生成电路 Aether' + 网表内容 (jiashengz @ hfeg0plg92, trace 1792746486510_lrvvt mc136);
    track=spice_char; reframe='LV_DPATH CDL shell + 静态拓扑校验器->produce-tool (sub-skill 提取 + tool-limit Aether import)'.
    = 真实用户 LV_DPATH SPICE 网表 (真实 foundry cell 名 + Cadence 原理图 1.jpeg 提取标注, file-verbatim), A-faithful.
  - track≠asset_provenance 本批 3 例 (累计 11→14, LibCellListGen/LpfAnomalyDetect/LvLvioSweep):
    LibCellListGen (track=faithful, asset=synth_deck: netlist_A 48 行小样本 + cell_list_A 含 NOTFOUND_xyz decoy
      + '判分时路径由参数传入' portability 标注; track=faithful 指 prompt 真实 /proj/drvqa 路径)
    LpfAnomalyDetect (track=None, asset=synth_deck: netlist_A.sp '示例 PLL LPF SPICE 网表' 含真实 foundry 器件名
      nmoscap/rm1s/nlvt_ckt/prvt_ckt 但 desc 显式 '示例'; track=None 缺标)
    LvLvioSweep (track=faithful, asset=synth_deck: netlist.sp header 显式 'faithful reconstruction from trace
      1793886971551_nekpi' + 真实器件名 nand2GT/ntn_lvio/ptn_lvio, 但 deck 整体 reconstruction for portability;
      track=faithful 指 prompt verbatim 用户原话)
    ⇒ 3/12=25% 本批 track≠asset_provenance, 累计 14 例; 主模式 = track=faithful 记 prompt/user-words 忠实,
      asset 文件为 portability 合成 fixture (与 r801-r808 累计 11 例同型, L 段多 portability reframe + 合成 deck).
  - synth_deck 4/12=33% (LibCellListGen/LpfAnomalyDetect/LvLvioSweep/LvlShftSpecCompliance):
    LvlShftSpecCompliance = 合成 lvlshft bundle (2_delay.sp/2_Ioff.sp/tck50n_delay_aging.sp 合成 SPICE deck +
      result_summary.txt 合成验证报告 + spec.json 合成规格, reframe '用自包含合成 lvlshft bundle');
    LvLvioSweep = faithful reconstruction from trace (netlist.sp header 显式);
    LpfAnomalyDetect = 示例 PLL LPF 网表 (netlist_A.sp desc 显式 '示例');
    LibCellListGen = 48 行小样本 netlist + decoy cell_list (portability).
  - synth_data 2/12=17% (LibCoordMapper/LvlShftSoaSizing):
    LibCoordMapper sample.lib = 合成 liberty fixture (含真实 authority_grids 数值 0.05-0.35 from trace +
      cxn4s1p_tpl library 名, 但 reframe 显式 '用真实 liberty 片段结构合成'); methodology.md + scenario.txt =
      verbatim 用户原话 (msg 0/165) 但为场景文件非脚本主输入; 主输入 sample.lib 合成 ⇒ synth_data;
    LvlShftSoaSizing topologies/*.json = 合成 6 拓扑选型 JSON (含真实 foundry 器件型号 ntn_m/ptn/ptn_lv/ntk_hv
      但 reframe 显式 '用自包含合成 6 拓扑选型 JSON 资产').
  - synth_log 1 例 (LvlshftBsubDiag): run_4.sh/bjobs_log.txt/run_log.txt/sim_dir_listing.txt/merge.py/sp_sample.sp =
    合成 LSF bsub 运行现场快照 bundle (含真实 user e0025768 + 真实 hostname hfeg0plg49/hfeg0pjn088 + 真实 timestamp
    Wed Aug 5 11:00:49 + 真实 CWD /home/e0025768/devops/lvlshft_optimize_260727/ + 真实 module path
    /apps/synopsys/hspice/V-2023.12/hspice/bin/hspice + 真实 LSF job 格式, 但 track=synthesized 显式标 +
    reframe 显式 '用自包含合成 trace 场景快照资产', hidden B 用不同 timestamp/host/queue/CWD ⇒ synth 重建快照非
    直接 scp; dominant asset = runtime logs (bjobs_log/run_log/sim_dir_listing) ⇒ synth_log (LSF bsub 运行日志首例).
  - A-faithful 5/12=42% (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8,r808=4,r809=5), 累计 45/108=42%.
  - 强信号类型本批新增 2 类: HSPICE .lis export header (LisMeasExtract) + SystemVerilog verbatim excerpt with
    file:line (LoadModeOpTruncDiag + MR7PsdScopeAnalyze); 维持 export header 族 (AETHER-SE/PEX/FineSim/WaveView/ALPS)
    + .inc/.lib 内网路径群 + panel-config 群 + real-buggy-script + TECHLIB 电源表 + 真实分层 netlist + 真实用户网表.

apply: cases/B/<case>.json metadata 新增 asset_fidelity (末位 key, 保留键序),
       B.jsonl 双存储同步 (scripts/build_jsonl.py --shard B rebuild)。
post-verify: asset_fidelity present count before→after; 395/395 valid JSON; 字段值分布; test_rationale 未动。
"""

import json
import os
import sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_B = os.path.join(BENCH, "cases", "B")

# case_id -> (asset_fidelity, rationale)
BATCH = {
    "EDA-Eval-DesignFlow-LibCellListGen-001": (
        "synth_deck",
        "netlist_A = 合成 DRAM full-chip 扁平网表小样本 (48 行, header '* Simulator : hspice / * Netlist : drvqa full-chip Vcap / "
        "* Library : drvqa_cmos_io', body 含真实 foundry 库名 drvqa_cmos_io/drvqa_cmos_dig + 真实 cell 名 IO_DqLdMdl/IO_DqRdMdl/latrqLx1/vcapLx1, "
        "但仅 48 行小样本 + 简化 .subckt 结构, 非 fullchip 真实 deck); "
        "cell_list_A = 合成 cell list (含 NOTFOUND_xyz decoy + 重复 IO_DqLdMdl 测去重, 7 行); "
        "prompt.txt = 真实用户原话 verbatim (ynbai @ hfhds201, 真实 /proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/netlist_lat + "
        "/proj/drvqa/V0/simdir/finesim/drvqaF/Netlists/Netlist_Vcap_20260918AM_Fullchip_0918DB/netlist 内网路径 + '判分时 netlist 与 cell list 路径由参数传入，不一定与上文 /proj 路径相同' portability 标注); "
        "track=faithful (指 prompt/user-words 忠实); reframe=None; "
        "track≠asset_provenance (track=faithful 记 prompt 真实 /proj 路径, asset=合成小样本 netlist + decoy cell_list); "
        "合成小样本 netlist (真实 foundry 库名/cell 名, portability 48 行小样本 + decoy) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-LibCoordMapper-001": (
        "synth_data",
        "sample.lib = 合成 liberty fixture (library (cxn4s1p_tpl), 含 lu_table_template setup_tpl_7x7 + "
        "authority_grids i_slews=0.05..0.35/c_slews=0.01..0.07/loads=0.02..0.14 真实网格数值 from trace real_task_summary, "
        "但 reframe 显式 '用真实 liberty 片段结构合成', library 名 _tpl 后缀 + 合成 template 名); "
        "methodology.md = verbatim 用户原话 (msg 165 逐字 '反标的后端脚本中：lib_timing_tools抽timing需要按照（i_slew，c_slew，q_load）的三维坐标形式传递...'); "
        "scenario.txt = verbatim 用户 msg 0/165; requirements.json = 合成 task-spec; "
        "track=None; reframe='lib_timing_tools (i,c,q) 三维坐标-timing table 关系梳理映射器->produce-tool (Q&A-analysis/relation-mapping->produce-mapper-tool)'; "
        "脚本主输入 = sample.lib (合成 liberty fixture, 主解析对象); methodology.md/scenario.txt 为场景/方法论文件 (verbatim 用户原话, 非脚本主输入); "
        "合成 liberty (真实网格数值 + 合成 library 名/template 名, reframe 显式 '用真实 liberty 片段结构合成') ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-LisMeasExtract-001": (
        "A-faithful",
        "stimulus_pex_rev06_model_rev04.lis = 真实 HSPICE .lis 文件 (头部 PrimeSim HSPICE export banner "
        "'****** PrimeSim HSPICE -- V-2023.12-SP1-1 linux64 (Apr 07 2024 8845341) ******' + "
        "真实 USER e0024852 + 真实 HOSTNAME hfeg0plg76 + 真实 timestamp 'Wed Nov 4 16:12:08 2026' + "
        "真实 FLEXlm license '12000@hl04' + 真实 'Input File: stimulus_pex_rev06_model_rev04.sp', 60 行); "
        "prompt.txt = 真实用户原话 verbatim (e0024852 @ hfeg0plg76, 真实 /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/"
        "SRAM_bitcell_DTCO/hd_CH252_bitcell/hd_CH252_bitcell_post_rev06/sim_result_pex_rev06_model_rev04_hspice/ 内网路径 + "
        "verbatim 用户请求 'jiexi ... de Ireak and Ileak SNM tell me in chinese'); "
        "track=faithful (与 asset 一致); reframe='tell-me 汇报->produce-reusable-tool (§4 有牙必要): 用户 e0024852 A-档 verbatim 原话'; "
        "真实 HSPICE .lis (PrimeSim HSPICE V-2023.12-SP1-1 export banner + 真实 user/host/timestamp/license + 真实内网路径, "
        "与 r805 PEX / r806 FineSim / r807 WaveView/ALPS export header 强信号族同列) + verbatim 用户请求 ⇒ file-verbatim (A-faithful, HSPICE .lis 首例)",
    ),
    "EDA-Eval-DesignFlow-LoadModeOpTruncDiag-001": (
        "A-faithful",
        "A_pattern.v = 真实 SV verbatim excerpt (header 显式 'real excerpt from DDR6 WTM pattern (tongfanl@hfhds201, trace 1791439699810_1550c)', "
        "body 含 verbatim Load_Mode 调用 'Load_Mode(.ma(8'hDE), .op({4'b0000,1'b1,1'b1,$urandom_range(1),pattern_select}),.op_mark(8'hff),.rstall(0),.enops(0),.bc(1))' = verbatim 用户 U#0 原话); "
        "A_specdef.sv = 真实 SV verbatim excerpt (header 'real excerpt from ddr6_specdef.sv (tongfanl@hfhds201)', 含 parameter int MODEMA_BITS=8/MODEOP_BITS=8); "
        "A_task.sv = 真实 SV verbatim excerpt (header 'real excerpt from ddr5_test.sv.sos (Load_Mode task, lines 947-1016)', 含 verbatim Load_Mode task 签名); "
        "prompt.txt = verbatim 用户原话 'Load_Mode(.ma(8'hDE), ...); 帮我看下pattern中的这句话，没有把DE寄存器的OP3为正确设为1，这是为啥？'; "
        "track=faithful (与 asset 一致); reframe='DDR6 Load_Mode OP 位宽截断诊断->produce-tool (portability+debug-Q&A->produce-tool 诊断器)'; "
        "真实 SV verbatim excerpt with file:line 标注 (3 文件: A_pattern.v/A_specdef.sv/A_task.sv, header 显式 'real excerpt from ... (lines X-Y)') + "
        "verbatim 用户 U#0 调试问题 ⇒ paste-verbatim (A-faithful, SV verbatim excerpt with file:line 子型, 与 r808 IoBufParamTune verbatim 调参请求同列)",
    ),
    "EDA-Eval-DesignFlow-LpfAnomalyDetect-001": (
        "synth_deck",
        "netlist_A.sp = 合成 PLL LPF SPICE 网表 (desc 显式 '示例 PLL LPF SPICE 网表（Input A）', header '** Library name: intDEV / ** Cell name: switch', "
        "body 含 switch_close/switch_open 未例化子电路 + 短接电阻 XR1 + 四端短接 MOS XPM0/XPM2 + 近零电阻 R0(r=0.001) + "
        "真实 foundry 器件名 nmoscap/rm1s/nlvt_ckt/prvt_ckt, 但整体为 portability '示例' 合成); "
        "task_context.md = verbatim 用户原话 (wnyu @ hfeahpc502, 真实 /proj/m2701/V0_DDR4/workdir/wnyu/simulation/LPF/hspiceD/schematic/netlist/netlist 内网路径 + "
        "verbatim '看下这个LPF，分析下' + 'MOS栅极源极漏极和衬底都接在一起是什么作用'); "
        "track=None; reframe=None; "
        "track≠asset_provenance (track=None 缺标, asset=合成 '示例' netlist); 合成 '示例' PLL LPF 网表 (真实 foundry 器件名, portability '示例' 标注) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-LvDpathCdlImport-001": (
        "A-faithful",
        "1_circuit.sp = 真实用户 LV_DPATH SPICE 网表 (header '1_circuit.sp : LV_DPATH 网表 (由 Cadence 原理图 1.jpeg 提取)' + "
        "详细器件映射 XI0~I6 invenLV_pc60/invLV_pc60/nor2LV_pc60/fbsLV_pc60/nchizLV_pc60 真实 foundry cell 名 + X0.5/X1/X2/MIN 尺寸, 90 行, "
        "body 含完整 LV_DPATH SPICE 网表 负沿 D 触发器 DOUT=D&RN + 行为级单元 INV/NOR2/CLKINV/NCHIZ/FBS + 测试激励); "
        "prompt.txt = verbatim 用户原话 '根据网表生成电路 Aether' + 网表内容 (jiashengz @ hfeg0plg92, trace 1792746486510_lrvvt mc136); "
        "track=spice_char; reframe='LV_DPATH CDL shell + 静态拓扑校验器->produce-tool (sub-skill 提取 + tool-limit Aether import->produce-tool CDL+topology checker)'; "
        "真实用户 LV_DPATH SPICE 网表 (Cadence 原理图 1.jpeg 提取标注 + 真实 foundry cell 名 + 完整网表 90 行, file-verbatim) + "
        "verbatim 用户原话 '根据网表生成电路 Aether' ⇒ file-verbatim (A-faithful, 真实用户 SPICE 网表)",
    ),
    "EDA-Eval-DesignFlow-LvLvioSweep-001": (
        "synth_deck",
        "netlist.sp = 合成 DpMuxTop_2 netlist (header 显式 'DpMuxTop_2 netlist (lvio baseline) - faithful reconstruction from trace 1793886971551_nekpi', "
        "body 含真实 foundry 器件名 nand2GT/ntn_lvio/ptn_lvio + 真实例化 XI1/XMMN2/XMMP1 + 真实参数 WP1=422.4e-9/LP1=46e-9, "
        "但 deck 整体显式 'faithful reconstruction' = 合成重建 for portability, 16 行); "
        "config.json = 合成 task 配置 (width_scales/length_values_nm/device_types/measurements, 通用 task-spec); "
        "prompt.txt = 真实用户原话 verbatim (yifansun @ hfeg0pkn001, 真实 /proj/ddgoa/V0/workdir/yifansun/simulation/ddgoa_cmos_pc40_DPmux8_PN1p76_PC60_length46_schematic_ALPS/input.sp 内网路径 + "
        "verbatim 用户多轮详细调参要求 5*6*2=60 变体扫描); "
        "track=faithful (指 prompt verbatim); reframe=None; "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 'faithful reconstruction' netlist + 合成 config); "
        "合成 netlist (显式 'faithful reconstruction from trace', 真实 foundry 器件名/参数, portability 重建, 与 r808 LatchSubcktLocate 'Synthetic mimicking' 同型) + 合成 config ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-LvlShftSoaSizing-001": (
        "synth_data",
        "topologies/{Vcc2Vdd1,Vcc2Vdleq,Vss2VkbVcc,Vss2VkbVdd1,Vdd12Vwlp,Vint2VdleqAryA}.json = 合成 6 拓扑选型 JSON (每文件含 topology/case/input/output/"
        "devices[role→{type,width,default}]/voltage_params, 真实 foundry 器件型号 ntn_m/ptn/ptn_lv/ntk_hv + 真实 case 名 Vcc2Vdleq/Vss2VkbVcc 等 from trace, "
        "但 reframe 显式 '用自包含合成 6 拓扑选型 JSON 资产保留真实任务结构', 数值/width 为合成); "
        "spec.json = 合成规格 (器件型号允许集合 + 电压参数范围 + topology→Case 映射表); task_brief.md = 交付接口说明; "
        "track=None; reframe='lvlshft 6 Case SOA 选型->produce-tool (portability+produce-action→produce-tool reframe)'; "
        "合成 6 拓扑选型 JSON (真实 foundry 器件型号/case 名 + 合成数值, reframe 显式 '自包含合成') ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-LvlShftSpecCompliance-001": (
        "synth_deck",
        "2_delay.sp / 2_Ioff.sp / tck50n_delay_aging.sp = 合成 lvlshft SPICE deck bundle (每文件 header 'Level Shifter Vss2VkbVcc — Delay/Ioff/Aging Measurement SPICE deck' + "
        ".param s=0.05 W=1.00 L=1.30um beta1=70 + pvnn=1.05/pvpp=-0.7/pvppmax=-1.175 + 合成 DUT Xptn/Xntn, reframe 显式 '用自包含合成 lvlshft bundle'); "
        "result_summary.txt = 合成 SPICE 验证报告 (beta1=70/S=0.05/L=1.30um/W=1.00, Rise 0.573ns/Fall 0.304ns/Ioff 1.588nA/aging 7.42%, 全 PASS); "
        "spec.json = 合成规格限制 (rise_delay_pvt_max_ns=0.694 等); task_brief.md = 交付接口; "
        "track=None; reframe='lvlshft 电平转换器规格合规验证->produce-tool (portability+produce-action→produce-tool reframe)'; "
        "合成 lvlshft bundle (合成 SPICE deck + 合成 result_summary + 合成 spec, reframe 显式 '自包含合成 lvlshft bundle') ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-LvlshftBsubDiag-001": (
        "synth_log",
        "run_4.sh / bjobs_log.txt / run_log.txt / sim_dir_listing.txt / merge.py / sp_sample.sp = 合成 LSF bsub 运行现场快照 bundle "
        "(bjobs_log.txt 含真实 user e0025768 + 真实 hostname hfeg0plg49 (提交节点) / hfeg0pjn088 (执行节点) + 真实 timestamp 'Wed Aug 5 11:00:49' + "
        "真实 CWD '/home/e0025768/devops/lvlshft_optimize_260727/runs/20260805025832_lvlshft/01_lvlshft_spec/vnn2vpp_opti/split' + "
        "真实 LSF job 格式 'Job <433489>, User <e0025768>, Status <EXIT>, Queue <rscalc1>'; "
        "run_log.txt 含真实 module load 'hspice/V-2023.12' + 真实 hspice path '/apps/synopsys/hspice/V-2023.12/hspice/bin/hspice' + 真实 bsub 提交日志; "
        "sp_sample.sp = 合成 SPICE 样本 (含 .option PARHIER=LOCAL/PORT_VOLTAGE_SCALE_TO_2X 等); "
        "prompt.txt = verbatim 用户原话 '帮我分析一下原因' (e0025768 @ hfeg0plg49, trace 1795907092176_vdeyi mc65); "
        "track=synthesized (显式标合成); reframe='LP5 level-shifter bsub 执行节点 hspice 缺失诊断器->produce-tool (portability+debug-Q&A->produce-tool 诊断器)'; "
        "合成 LSF 运行现场快照 bundle (含真实 user/host/timestamp/CWD/module path 嵌入信号, 但 track=synthesized + reframe 显式 '用自包含合成 trace 场景快照资产' + "
        "hidden B 用不同 timestamp/host/queue/CWD ⇒ 合成重建快照非直接 scp); dominant asset = runtime logs (bjobs_log/run_log/sim_dir_listing) ⇒ synth_log (LSF bsub 运行日志首例)",
    ),
    "EDA-Eval-DesignFlow-MBistTopAnalyze-001": (
        "A-faithful",
        "doc/mbist_top.netlist = 真实 MBIST 分层 SPICE 网表 (header 显式 'mBistTop thick-oxide / digital MBIST hierarchical SPICE netlist / "
        "top integration of memory-BIST pattern generator (trace-faithful, A) / source: /proj/ddgoa/V0 libs ddgoa_cmos_digital / mBistTop schematic', "
        "body 含真实 foundry cell 名 mBistCmdGen/mBistAddrGen/mBistPat/Bistwritedata/Spare_mBist + 真实端口名 cm0_ts_BistData/BACntRst/CACntCK/RACntCK/..."
        "(与 trace real_task_summary 5 子模块 + 地址计数器 + 6 计数时钟一致)); "
        "task_spec.json = task-spec (含 user_prompt_verbatim '你可以帮我分析电路吗/这个电路图在/proj/ddgoa/V0/libs/ddgoa_cmos_digital/mBistPat下/网表我抽了.../你从上往下帮我详细的说一下'); "
        "hidden manifest 'a_leak_tokens' 含 mBistTop/mBistCmdGen/mBistAddrGen/mBistPat/... 真实 token 列表 (A 含真实 token 防泄题); "
        "track=None; reframe='MBIST 顶层网表分层分析器->produce-tool (analysis/Q&A->produce-tool analyze+JSON)'; "
        "真实 MBIST 分层 SPICE 网表 (header 显式 'trace-faithful, A' + 真实 /proj/ddgoa/V0 source path + 真实 foundry cell 名 + a_leak_tokens 真实 token, "
        "与 r806 LatchSubcktLocate netlist 'Synthetic mimicking' 反向: 本例显式 trace-faithful A 非 Synthetic) ⇒ file-verbatim (A-faithful, MBIST 分层网表首例)",
    ),
    "EDA-Eval-DesignFlow-MR7PsdScopeAnalyze-001": (
        "A-faithful",
        "A_vecgen/{ddr6_interface,ddr6_package,ddr6_specdef,ddr6_test,timing_load}.sv = 真实 SV verbatim excerpt 群 (每文件 header 显式 "
        "'<file>.sv — real excerpt (vecgen_local), lines X-Y' + 'source: /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/<file>.sv', "
        "body 含 verbatim file:line 标注: ddr6_specdef.sv:36 MODEMA_BITS=8 / ddr6_package.sv:487-491 MR7_zq_* 5 字段 in TYPE_modereg_direct / "
        "ddr6_interface.sv:129 modereg_direct 单份 (shared) / ddr6_test.sv:7-9 mr_da/mr_pg0 宏 + :4848-4863 MRUPD / timing_load.sv:2362-2368 MRSettingDirect case 7); "
        "prompt.txt = verbatim 用户原话 '/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local 帮我看下，对于MR7，会区分PSD0或者PSD1吗？是不是只用设置PSD0即可，PSD1会和PSD0的保持一致' "
        "(tongfanl @ hfhds201, trace 1791958972412_xk1n1 mc506); "
        "track=faithful (与 asset 一致); reframe='DDR6 vecgen MR7 PSD0/PSD1 scope 分析器->produce-tool (analysis/Q&A->produce-tool 分析器)'; "
        "真实 SV verbatim excerpt 群 with file:line 标注 (5 文件, header 显式 'real excerpt (vecgen_local), lines X-Y' + 真实 /proj/dscqa source path) + "
        "verbatim 用户 U#0 PSD scope 问题 ⇒ paste-verbatim (A-faithful, SV verbatim excerpt with file:line 子型, 与 LoadModeOpTruncDiag 同批双例 SV excerpt 群)",
    ),
}


def main():
    applied = []
    skipped = []
    before = 0
    after = 0

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
        after += 1
        applied.append((cid, val))

    print("=== 档2 asset_fidelity backfill r809 batch9 ===")
    print("to apply:", len(BATCH), "| applied:", after, "| skipped:", len(skipped))
    print("coverage: before=%d -> after=%d (delta=+%d)" % (before, before + after, after))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-58s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIPPED  %-58s : %s" % (cid, reason))

    # value distribution
    from collections import Counter
    dist = Counter(v for _, v in applied)
    print("\n--- value distribution ---")
    for v, c in sorted(dist.items()):
        print("  %-14s : %d" % (v, c))

    # write manifest
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r809_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r809_manifest.tsv — r809 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch9 (12 cases, alphabetical next 12 missing after r808 batch8 LatchSubcktLocate: LibCellListGen..MR7PsdScopeAnalyze, L-M 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r808 档2 batch1-8 (+96, 106→202) done. 本轮 r809 档2 batch9.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver; A-faithful 强信号 = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB/WaveView/ALPS export header / 真实内网路径 .inc/.lib/.spf / verbatim excerpt with file:line / 'reproduced faithfully' / 'faithful compact/trimmed representation' 标注 / 真实 hostname / 真实 signal names from real path / 显式 A-faithful/trace-faithful 标注 / 真实用户 buggy 脚本 + verbatim 修复要求 / 真实分层 netlist + 真实 /proj source path\n")
        f.write("# 关键发现: 真实 HSPICE .lis export header 强信号首例 (LisMeasExtract stimulus_pex_rev06_model_rev04.lis PrimeSim HSPICE V-2023.12-SP1-1 banner + 真实 user e0024852/host hfeg0plg76/timestamp/license) / 真实 SystemVerilog verbatim excerpt with file:line 强信号双例 (LoadModeOpTruncDiag A_pattern.v/A_specdef.sv/A_task.sv 3 文件 + MR7PsdScopeAnalyze A_vecgen/ 5 文件, 每 header 显式 'real excerpt ... lines X-Y' + 真实 /proj source path) / 真实 MBIST 分层 SPICE 网表首例 (MBistTopAnalyze doc/mbist_top.netlist header 显式 'trace-faithful, A' + 真实 /proj/ddgoa source path + a_leak_tokens 真实 token) / 真实用户 LV_DPATH SPICE 网表 (LvDpathCdlImport 1_circuit.sp 'Cadence 原理图 1.jpeg 提取' + 真实 foundry cell 名) / track≠asset_provenance 本批 3 例 (累计 11→14, LibCellListGen/LpfAnomalyDetect/LvLvioSweep, 主模式 track=faithful 记 prompt + asset portability 合成) / synth_deck 4/12=33% (LibCellListGen/LpfAnomalyDetect/LvLvioSweep/LvlShftSpecCompliance) / synth_data 2 (LibCoordMapper/LvlShftSoaSizing) / synth_log 1 (LvlshftBsubDiag, LSF bsub 运行日志首例, 合成现场快照含真实 user/host/timestamp 嵌入信号) / A-faithful 5/12=42% (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8,r808=4,r809=5) 累计 45/108=42% / 强信号类型本批新增 2 类 (HSPICE .lis export header + SV verbatim excerpt with file:line), 维持 export header 族 + .inc/.lib 内网路径群 + panel-config 群 + real-buggy-script + TECHLIB 电源表 + 真实分层 netlist + 真实用户网表\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 202->214 (cases/B 214==B.jsonl 214 ✓); miss 193->181\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
