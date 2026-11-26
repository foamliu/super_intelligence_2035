#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r804.py — r804 档2 asset_fidelity backfill batch4.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note backfill, 32→235) done. r801 档2 batch1 (+12, 106→118) done.
      r802 档2 batch2 (+12, 118→130) done. r803 档2 batch3 (+12, 130→142) done.
      本轮 r804 推进 档2 batch4 — 12 cases
      (alphabetical next 12 missing after r803 batch3 CmlMirrorSweepAnalysis:
       CmlSweepHeadroomDiag..DblTailSlicerDeckGen).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 / 真实 scp 自内网 / 真实用户 paste)
  - synth_deck   : A = 合成 SPICE deck/stim/cell 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/source-file fixture
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver。
      A-faithful 强信号 = prompt 显式 "真实"/"verbatim"/"逐字摘录"/"现场抽取的真实产物"/"真实 scp 自" 或
                          asset 文件 header 明记 verbatim from trace (含真实内网路径) 或
                          asset 内容 = 真实用户 paste 的 verbatim 文本 (track=faithful + 内容与 prompt 引用一致) 或
                          asset header = 真实 AETHER-SE/VCS/HSPICE export header (含真实 user/date/library) 或
                          asset = verbatim excerpt (含 "(excerpt)" / "(excerpt from ...)" 标注 + 真实代码内容, 非 reconstructed)。
      synth 信号 = track=synthesized / portability reframe / "样本"/"合成"/"self-contained sample" / 通用名文件 /
                   asset header 明记 "BROKEN VERSION (shipped to SUT as asset)" / "sample" / "fixture" / "synthesized SPICE" /
                   "(reconstructed from cline trace ...)" / "(ORIGINAL, has bug)" 叙事标注 / A_ONLY_MARKER + decoy 内容。
      .75-reachable 判别 (r803 新增): host=.75 (hfhds201) ⇒ 真实 scp 可行 / host=计算节点+asset 含真实内网路径 ⇒ 推断 file-verbatim。
      excerpt vs reconstructed 二分 (r804 新增): "(excerpt)"/"(excerpt from ...)" = verbatim 切片 ⇒ A-faithful;
                                                  "(reconstructed from cline trace ...)" = 重建 ⇒ synth_data。

本批 12 case 判定:
  - 6 A-faithful (单批最高, 超 r803 batch3 的 4): CmlSweepHeadroomDiag/CmpStg1CapAdd/CosimPvintUndefDiag/
        CxsaDcSweepDeckGen/DQSEHFlagNoEffectDiag/DatatPrintOrderDiag
  - 4 synth_data: CovBinMetaExtract/CovMissBinExtract/DOERankBuild/DblTailSlicerDeckGen
  - 1 synth_script: CosimRunBlockOpt
  - 1 no-asset: CosineWaveAnalyze

关键发现:
  - A-faithful 单批 6/12=50% 创新高 (r801=3/12, r802=3/12, r803=4/12): 本批覆盖多个 debug-Q&A 域 case,
    真实 .sp/.sv/.log 文件 verbatim 自 trace (B 域 debug-Q&A 域特性: 用户带真实产物问"为什么")。
  - excerpt vs reconstructed 二分首例: DatatPrintOrderDiag "(excerpt from patterns/analogsim/WTM/)" ⇒ A-faithful,
    对照 CovBinMetaExtract "(reconstructed from cline trace mrmfn, ericw@hfhds201)" ⇒ synth_data。
    两者均含 A_ONLY_MARKER cross-input guard, 但 excerpt=verbatim 切片 vs reconstructed=重建, 语义对立。
  - AETHER-SE export header 强信号 (CxsaDcSweepDeckGen): netlist_A header 含真实 User/Date/Library/Cell
    (t0002614/Tue Nov 10 15:24:03 2026/drgqa_cmos_core/CXSA1x4_1C2A) ⇒ file-verbatim, 不看 host 是否 .75。
  - 真实内部 edit note 信号 (CosimPvintUndefDiag): env_A.txt 含 "**edit by clzhang yifan request" 真实内部协作注释 ⇒ verbatim。
  - synth_script 首例 (CosimRunBlockOpt): runBlock_orig.pl header "(ORIGINAL, has bug)" 叙事标注 ⇒ 合成 Perl 参考,
    对照 track=faithful (prompt mike 原话 verbatim) ⇒ track≠asset_provenance 再证 (累计 r801-r804 六批 6 例)。
  - no-asset 纯生成 (CosineWaveAnalyze): 0 数据 attachment (仅 prompt.txt+task_brief.md 任务框架), 纯 Tcl 生成 Q&A。

apply: cases/B/<case>.json metadata 新增 asset_fidelity (末位 key, 保留键序),
       indent=2 ensure_ascii=False, round-trip identical 验过;
       B.jsonl 双存储同步 (scripts/build_jsonl.py --shard B rebuild)。
post-verify: asset_fidelity present count before→after; 395/395 valid JSON; 字段值分布; test_rationale 未动。
"""
import json, os, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASES_B = os.path.join(BENCH, "cases", "B")

# case_id -> (asset_fidelity, rationale)
BATCH = {
    "EDA-Eval-DesignFlow-CmlSweepHeadroomDiag-001": (
        "A-faithful",
        "cml_tran_A.sp = 真实 HSPICE deck verbatim 自 lvyy @ hfeg0pkn004 trace (含真实 .include '/proj/m2701/V0_DDR4/workdir/lvyy/simulation/hspice_option.sp' 路径 + .inc '/proj/m2701/V0_DDR4/simdir/finesim/workdir/lvyy/...' 路径, lvyy=trace 用户); "
        "netlist_A = 真实 AETHER-SE 导出 verbatim (header '** Library name: A_lvyy / Cell name: cml_1 / View name: schematic', A_lvyy=lvyy 用户库, 含 XPM2/XPM4/XPM5 CML 差分对 + R1/R2 + I6 DC=100e-6 尾电流源); "
        "cml_tran_A.mt0.csv = 真实 HSPICE .measure verbatim (PrimeSim HSPICE V-2023.12, winput 5e-7→3e-6 扫描, id 7.216e-05→1.206e-04 即 72.16uA→120.6uA 与 real_task_summary 金标准 isub 72.2uA→120.6uA +67% 完全吻合); "
        "track=faithful; prompt.txt = lvyy U0 原话 verbatim 含真实 /proj/m2701/V0_DDR4/workdir/lvyy/simulation/LP6/small_schematic/cml_tran.sp 路径; "
        "reframe_note 显式 'asset_fidelity 缺标应 A=trace-verbatim(cml_tran.sp 场景)+B=synth'; host=hfeg0pkn004 计算节点 + asset 含真实 /proj/m2701 内网路径 ⇒ 推断 file-verbatim; reframe=Q&A debug-Q&A why->produce-tool 诊断器",
    ),
    "EDA-Eval-DesignFlow-CmpStg1CapAdd-001": (
        "A-faithful",
        "cmdm.sp = 真实 HSPICE strongarm 比较器 testbench deck verbatim 自 jiangbaol @ hfeg0pkn003 trace (含真实 .inc '/home/data08/V0/simrun/hspice/joewu/1_sim_option/other_option' 路径 + .inc '/home/data08/V0/simrun/hspice/elaine/inc_netlist_model/finesim_option' 路径 + .lib '/proj/shdc/mod...' 真实模型库路径, joewu/elaine=真实用户工程目录); "
        "track=faithful; prompt.txt = jiangbaol U0 原话 verbatim 含真实 /proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa_test_cmdm.sp 路径; "
        "host=hfeg0pkn003 计算节点 + asset 含真实 /home/data08 + /proj/shdc 内网路径 ⇒ 推断 file-verbatim; 无 reframe_note (keep_faithful, 原意图=产 add_outstg1_cap.py 加电容到 .sp, A 档 verbatim 合规)",
    ),
    "EDA-Eval-DesignFlow-CosimPvintUndefDiag-001": (
        "A-faithful",
        "cosim_A.log = 真实 VCS + FineSimPro 联合仿真日志 verbatim 自 easont @ hfeg0pkn004 trace (header 'Chronologic VCS simulator R-2020.12_Full64 / FineSimPro V-2023.12-1', 含真实 'Hostname: hfeg0pgn022, Username: easont' + FINESIM_HOME=/apps/synopsys/SRB/finesim/V-2023.12-1 + LD_LIBRARY_PATH 真实环境); "
        "env_A.txt = 真实 common.env verbatim (header '** dcpna(lpddr5): common.env **', 含真实 '**edit by clzhang yifan request' 内部协作注释 + vdd1/vdd2h/vdd2hs/vdd2l/vint/vbp 真实电源节点 + pvpgint/pvpgintbus 真实参数); "
        "pvt_A.sp + voltage_A.txt = 真实 PVT 仿真 deck + 电压表 verbatim; track=faithful; prompt.txt = easont U0 原话 verbatim 含真实 /proj/ddgoa/V0/workdir/easont/simulation/ddgoa_cmos_digital_RowControl_schematic_ALPS_sim/cosim_check/cosim/1067tt25/cosim.log 路径; "
        "host=hfeg0pkn004 计算节点 + asset 含真实 /apps/synopsys + /proj/ddgoa 内网路径 + 真实内部 edit note ⇒ 推断 file-verbatim; reframe=Q&A debug-Q&A->produce-tool 诊断器",
    ),
    "EDA-Eval-DesignFlow-CosimRunBlockOpt-001": (
        "synth_script",
        "runBlock_orig.pl = 合成 Perl 参考实现 fixture (header 显式叙事标注 'runBlock - ALPS + VCS-AD 数模混合联合仿真环境生成脚本 (ORIGINAL, has bug)', 真实生产脚本不会自标 '(ORIGINAL, has bug)', 合成重构供候选 reimpl 为 gen_cosim.py); "
        "netlist_A.sp = 合成结构网表 fixture (.SUBCKT TopA 通用单元 INVx1/AND2x1/BUFx1/MUX2x1/TGATEx1, 非 SPICE sim deck, portability 重构); "
        "port_in_A.txt / port_io_A.txt / stimulus_A.txt = 合成端口/激励数据 fixture (_A suffix, portability); "
        "track=faithful (prompt.txt = mike U0 原话 verbatim 含真实 /ai_sandbox/dscqa/V0/agentdir/mike/dscqa_array_m0d5G_YS_Bot_sub_schematic_ALPS/runBlock 路径, host=hfhds201=.75, 但 asset 显式合成) ⇒ track≠asset_provenance 再证 (累计 r801-r804 六批 6 例); "
        "reframe=portability+produce gen_cosim.py (真实 /ai_sandbox 项目 huge + runBlock 须 portable reimpl ⇒ synth_script + synth fixture)",
    ),
    "EDA-Eval-DesignFlow-CosineWaveAnalyze-001": (
        "no-asset",
        "0 数据 attachment (仅 prompt.txt = e0023936 U0 原话 verbatim '使用tcl代码，帮我画一个余弦波并计算过零点、估算频率与峰值' + task_brief.md 交付接口说明, 均为任务框架非数据输入); "
        "track=faithful; 纯 Tcl 生成 Q&A, 候选 gen_cosine.tcl 从参数 -freq/-amp/-np/-pts 生成波形 + 计算过零点/频率/峰值, 无外部数据输入; "
        "host=hfhds201=.75; 承 r801 AcSimHowtoGuide / r802 BndGaussPwlGen 惯例, 0 数据 attachment 纯生成任务 ⇒ no-asset; reframe=how-to-Q&A->produce-tool Tcl 脚本生成器",
    ),
    "EDA-Eval-DesignFlow-CovBinMetaExtract-001": (
        "synth_data",
        "A/constraint_timing_coverage.sv = 合成 SystemVerilog coverage 定义 fixture (header 显式 '(reconstructed from cline trace mrmfn, ericw@hfhds201, U#0 target)' 重建非 verbatim 切片 + 'NOTE: A_ONLY_MARKER_cgbin_4m2p appears only in this A file' cross-input guard + 'Decoy 1: unrelated covergroup, no metadata comment header' 合成 decoy 内容); "
        "track=faithful; prompt.txt = ericw U0 原话 verbatim 含真实 /rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/coverage/DDR5_2026-09-11 路径; "
        "host=hfhds201=.75 但 asset 显式 'reconstructed from cline trace' 重建 (非真实文件 scp, 对照 r803 CgMeetExactlyMissWalk 同 ericw 同 .75 但 track=faithful + 真实 31 文件 scp ⇒ A-faithful, 本案 asset 重建 ⇒ synth); "
        "reframe=Q&A analysis->produce-tool covergroup 元数据提取器; excerpt vs reconstructed 二分: reconstructed ⇒ synth_data (对照 DatatPrintOrderDiag excerpt ⇒ A-faithful)",
    ),
    "EDA-Eval-DesignFlow-CovMissBinExtract-001": (
        "synth_data",
        "cov_A/table1.json = 合成 DDR5 aicov coverage dump fixture (covergroup 标题 cg_dq_pad_rx_ddr5_3200/cg_dq_pad_tx_ddr5_3200/cg_dqs_addr_ddr5_3200 等, 结构还原真实 trace 但 track=synthesized 明确合成); "
        "workspace_listing.txt = 合成工作区目录清单 fixture (cov_A/table1.json+table2/+table3/ 结构描述); "
        "track=synthesized (明确); prompt.txt = ericw U0 原话 verbatim 含真实 /rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/cov_work/html_02-11-2026_10~05~53 路径; "
        "host=hfhds201=.75 但 track=synthesized ⇒ asset 合成 (对照 r803 CgMeetExactlyMissWalk 同源 ericw 但 track=faithful + 真实 scp ⇒ A-faithful, 本案 track=synthesized ⇒ synth_data); "
        "reframe=Q&A analysis->produce-tool meet_exactly 未命中 bin 过滤器; track=synthesized 为 asset 合成的权威信号",
    ),
    "EDA-Eval-DesignFlow-CxsaDcSweepDeckGen-001": (
        "A-faithful",
        "netlist_A = 真实 AETHER-SE 导出 netlist verbatim 自 t0002614 trace (header '* Type: hspice / * Tool: AETHER-SE / * Date: Tue Nov 10 15:24:03 2026 / * User: t0002614 / * Top Design: drgqa_cmos_core/CXSA1x4_1C2A/schematic', 含真实用户 t0002614+真实日期+真实库 drgqa_cmos_core+真实单元 CXSA1x4_1C2A + switch_close(r=0.001)/switch_open subckt + XMMN03 SaBla<0> Iso Bla_local<0> 真实 sense amp 器件); "
        "manifest_A.json = 真实 manifest 含真实 .lib '/proj/shdc/models/G6/model_local/V1_HK_Model_D5_v0d5_Rev03_t06/V1_HK_Model_D5_v0d5_Rev03_t06.sp' TT 模型库路径 + incFile_V1_HKMG bjt_tt/res_tt/nicap_tt sections; "
        "track=None; prompt = t0002614 U0 原话 verbatim (task_context.md 标 'trace-faithful，用户 t0002614 原话') 含真实 vad2!=1.4V/Sel=1.77V/Vdleq 1.17→1.77V 扫描参数; "
        "host=10.129.2.13 计算节点 + asset 含真实 AETHER-SE export header (真实 user/date/library) + 真实 /proj/shdc 内网路径 ⇒ 推断 file-verbatim (AETHER-SE export header 强信号, 不看 host 是否 .75); reframe=how-to->produce-tool dc_sweep_deckgen.py 生成器",
    ),
    "EDA-Eval-DesignFlow-DOERankBuild-001": (
        "synth_data",
        "A/cell_library.tsv = 合成单元面积表 fixture (9 行 cell\\tarea: nand2GSx1=1.00/nand2GSx4=2.80/invGSx{1,2,3,4,6,8,16}=0.20×N, 干净逻辑努力模型数值); "
        "A/doe_variants.tsv = 合成 design point 清单 fixture (27 行 D02-D28, variant_id\\tnand_cell\\tinv1/inv2/inv3_cell); "
        "A/doe_measure.lis = 合成 HSPICE .measure 日志 fixture (header '*doe=characterization corner=tt vdd=1.20 temp=25 / * tapered buffer DOE sweep - falling delays (ns) / * model: logical-effort, LOAD=48.0', @variant 块含 .measure f1/f2/f3/fL 干净值 2.00e+00 等); "
        "track=None; prompt = 合成叙事 ('你是 CXMT 的 characterization 工程师 thqu...') 含 thqu U0 原话引用但 wrapper 合成; "
        "host=hfeahpc503; reframe=skill->produce-tool doe_rank.py 排序器 (thqu 原意图 '把这个锥形驱动器的优化流程做成一个 skill' -> 便携 doe_rank.py); 真实 168 design point HSPICE 扫描在 thqu /proj 内网不可达, asset 为合成 27-point fixture 供排序器开发",
    ),
    "EDA-Eval-DesignFlow-DQSEHFlagNoEffectDiag-001": (
        "A-faithful",
        "A_genvector.sv = 真实 SystemVerilog DQ 映射代码 verbatim 自 tongfanl @ hfhds201(.75) trace (无 reconstructed 标注, 直接 `ifdef X1P12/`ifdef SC0/`elsif SC1/`elsif X1P6/`ifdef SK1P6/`ifdef DQSELH 真实生产 ifdef 级联 + A_pin_if.DQ[5:0]/DQ[11:6]/{3'bz, A_pin_if.DQ[5:3]} 真实 DQ 映射逻辑, 对应 prompt 'PSD0 出 DQ543、PSD1 出 DQ210' 现象); "
        "track=faithful; prompt.txt = tongfanl U0 原话 verbatim 含真实 /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local 路径 + './runsti/gen_stimulus_ltf' + '-d \"DQSEH\"' 真实 flag; "
        "host=hfhds201=.75 ⇒ 真实 scp 可行; reframe=Q&A debug-Q&A why->produce-tool diag.py 静态分析器 (-d flag 为何无效); 真实 .sv 在 tongfanl /proj/dscqa 内网但 .75 可达 ⇒ file-verbatim",
    ),
    "EDA-Eval-DesignFlow-DatatPrintOrderDiag-001": (
        "A-faithful",
        "A_wtm/ddr6_tasks.sv = 真实 SystemVerilog task 代码 verbatim excerpt 自 tongfanl @ hfhds201(.75) trace (header '// ddr6_tasks.sv (excerpt)' 即 verbatim 切片非 reconstructed, 含真实 `timescale 1ps/1ps / `define DQ_BITS 6 / `define MAX_BURST_LEN 24 / `define TBDATAFIFODEPTH 64 + loaddq_fifo task 'pack the per-UI write data into dq_fifo so that the DQ pin driver emits UI0 first' 真实 FIFO 加载逻辑); "
        "A_wtm/WTM001_normal_check.v = 真实 Verilog 模式 verbatim excerpt (header '// WTM001_normal_check.v (excerpt from patterns/analogsim/WTM/)' 即 verbatim 切片, 含真实 module WTM001_normal_check + BL=24/DQ_BITS=6/UI_data[0:23]/write_data_array[0:7] + 'A_ONLY_MARKER_DATAT_DESC_4m2p' cross-input guard 注解, 真实 DATAT 打印逻辑); "
        "track=faithful; prompt.txt = tongfanl U0 原话 verbatim 含真实 /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local/log/stimulus_tongfanl/WTM_fsm_1030/WTM004_block_check_SC1_WPre_4s4t_WPst_4p5_RPre_2s6t_RPst_4p5_MD_OFF_CRC_11_tCH50_2b16g_BL02_12800_SS_DQSELH.X2P6_12800 路径; "
        "host=hfhds201=.75 ⇒ 真实 scp 可行; excerpt vs reconstructed 二分: '(excerpt from ...)' = verbatim 切片 ⇒ A-faithful (对照 CovBinMetaExtract '(reconstructed from cline trace)' ⇒ synth_data); r801 canonical vocab 'verbatim excerpt with 原行号标注' 明列 A-faithful; A_ONLY_MARKER 为 cross-input guard 注解非内容合成; reframe=Q&A debug-Q&A why->produce-tool diag_datat_print_order.py 打印顺序诊断器",
    ),
    "EDA-Eval-DesignFlow-DblTailSlicerDeckGen-001": (
        "synth_data",
        "spec_A.txt = 合成设计规格 fixture ('# Spec A (SUT 可见) — double-tail slicer deck generation', target_data_rate_ghz: 2.9 / topology: double-tail (StrongARM) / technology: 45nm CMOS (PTM BSIM4 baseline) / note: 'A 仅作为 SUT 的示例目标率；判分只在隐藏输入 B 上跑'); "
        "track=faithful (prompt.txt = cynthiaz U0 原话 verbatim 'design a double-tail slicer,meet target data rate 2.9Ghz', 但 asset spec_A.txt 合成); "
        "0 真实输入 netlist/deck (纯设计生成任务, 候选 gen_slicer_deck.py 按目标率参数化生成 slicer.sp+sizing.json+README.md); host=hfeg0pkn005; "
        "reframe=design-Q&A->produce-tool deck 生成器; 承 r803 CmdEdgeMeasGen 合成 spec+deck 惯例, spec_A.txt 合成规格 fixture (非真实输入), 1 attachment ⇒ synth_data (非 no-asset, no-asset=0 数据 attachment)",
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

    print("=== 档2 asset_fidelity backfill r804 batch4 ===")
    print("to apply:", len(BATCH), "| applied:", after, "| skipped:", len(skipped))
    print("coverage: before=%d -> after=%d (delta=+%d)" % (before, before + after, after))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-58s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIP     %-58s : %s" % (cid, reason))

    # post-verify: full cases/B asset_fidelity coverage
    print("\n--- post-verify: cases/B full coverage ---")
    have = 0
    miss = 0
    dist = {}
    for fname in sorted(os.listdir(CASES_B)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CASES_B, fname), encoding="utf-8") as f:
            dd = json.load(f)
        af = dd.get("metadata", {}).get("asset_fidelity")
        if af is None:
            miss += 1
        else:
            have += 1
            dist[af] = dist.get(af, 0) + 1
    print("have asset_fidelity: %d / 395 | miss: %d" % (have, miss))
    print("value distribution (canonical short values only):")
    for k, v in sorted(dist.items(), key=lambda x: -x[1]):
        if len(k) <= 40:
            print("  %-40s : %d" % (k, v))
    long_form = sum(v for k, v in dist.items() if len(k) > 40)
    print("  (long-form legacy values total)            : %d" % long_form)

    # post-verify: all 395 valid JSON + test_rationale spotcheck
    print("\n--- post-verify: 395 valid JSON + test_rationale spotcheck ---")
    n_valid = 0
    n_rationale = 0
    for fname in sorted(os.listdir(CASES_B)):
        if not fname.endswith(".json"):
            continue
        with open(os.path.join(CASES_B, fname), encoding="utf-8") as f:
            dd = json.load(f)
        n_valid += 1
        rat = dd.get("metadata", {}).get("test_rationale", "")
        if rat:
            n_rationale += 1
    print("valid JSON: %d / 395 | has test_rationale: %d" % (n_valid, n_rationale))


if __name__ == "__main__":
    main()
