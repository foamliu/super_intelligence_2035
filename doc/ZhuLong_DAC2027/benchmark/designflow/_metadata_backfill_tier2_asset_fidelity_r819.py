#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r819.py — r819 档2 asset_fidelity backfill batch19.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r818 档2 batch1-18 (+204, 106→322) done. 本轮 r819 推进 档2 batch19 — 12 cases
      (alphabetical next 12 missing after r818 batch18 SpGen:
       SpRcAlterGen..SpiceSim, Sp→Spice 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r818 扩展): 见 r818 script header.

本批 12 case 判定:
  - 4 A-faithful (33%) — Sp→Spice 段 real-trace 资产 (r818 累计 86/216=39.8%; 本批 4/12=33%,
    累计 90/228=39.5%). 4 例:
      * SpRcAlterGen (real DSIM/FineSim testbench export banner sample_base.sp
        'Spice Simulation Testbench Created by DSIM / Design Library Name: VictorQin_Study /
         Design Cell Name: LWL_study_SWDarray / Created On: 2026/04/29 14:25:18 /
         For Simulator: Finesim' + real library VictorQin_Study matching trace user victorq;
        新信号族: real DSIM FineSim testbench export banner)
      * SpTemplateOpt (real FineSim option block control_template_A.sp .option finesim_mode=
        spicehd/finesim_vdd=3.5v/measfile=1 measform=3/finesim_output=fsdb; reframe_note 显式
        'asset_fidelity 缺标应 real-from-trace (control_template.sp 真实模板作可见 A, 待 @A apply 档2)';
        新 sub-type: reframe_note self-declares provenance)
      * SpfAutosimSetup (real terminal PEX run info terminal_pex_info.json project TV1_FS Rev07
        GloryEX_2026.06_P010 + real run_dir /proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/pex/
        pex420/pex1024x72 + real pex_deck_dir/dbc_dir/lvs_rule + real TASK_EXTRA_SPF_M4B4.md
        task with real /proj/lacaa + 廖建文 reference; 新 sub-type: real PEX run metadata JSON)
      * SpfNtsvMissingDiag (real spf_bl_extract.py author header '# author: E0041050' + real SPF
        CXSA_A.spf real LAYER_MAP *16 M1net ITF=M1..*21 M6net; track=faithful; 承 r817 real
        script author header 强信号族)
  - 5 synth_deck: SpiceDeckExplain (track=synthesized + reframe '自包含合成') / SpiceDeckPairDiff
    (generic .inc model_tt.inc/netlist.inc + PULSE stimulus; track≠asset_provenance) /
    SpiceMeasInjector (trimmed testbench, real /home/data08+/proj/m2701 paths embedded) /
    SpiceParamSweepGen (synth template .param defaults, real /proj/drvqa path embedded) /
    SpiceSim (自包含 + level-1 .model portable reconstruction)
  - 2 synth_data: SpfExtractFeasibility (curated env_manifest.json API surface, Q&A capability-query)
    / SpfMeasDiag (DSPF SPF PEX_CASE + FineSim log fixtures, '格式参考；不参与判分')
  - 1 synth_tree: SpiceCfgDirMerge (track=synthesized, shdc_A/apps_A dir trees)

关键发现:
  - A-faithful 33% (4/12) — Sp→Spice 段 real-trace 资产 (r818 累计 86/216=39.8%; 本批 4/12=33%,
    累计 90/228=39.5%). 本批 A-faithful 比率略低于均值 (Spice 段 synth_deck 密集 5/12=42%).
  - 新信号族 4 类:
    * real DSIM FineSim testbench export banner (SpRcAlterGen 'Spice Simulation Testbench Created
      by DSIM / Design Library Name: VictorQin_Study / Created On: 2026/04/29', 扩展 r813 export
      header 强信号族至 DSIM testbench export 域)
    * reframe_note self-declares provenance (SpTemplateOpt reframe_note 显式 'asset_fidelity 缺标
      应 real-from-trace...待 @A apply 档2', 新 sub-type: reframe_note 自身声明资产来源)
    * real terminal PEX run metadata JSON (SpfAutosimSetup terminal_pex_info.json real project/
      rev/tool_version/run_dir/pex_deck_dir/dbc_dir/lvs_rule, 新 sub-type: real PEX run info JSON)
    * real script author header (SpfNtsvMissingDiag '# author: E0041050', 承 r817 real script
      author header 强信号族至 SPF extractor script)
  - track≠asset_provenance 1 例 (累计 38→39): SpiceDeckPairDiff (track=faithful prompt verbatim
    U#7 'I want to know the difference...' 但 asset synth_deck generic .inc/PULSE fixture;
    real_task_summary 'A-faithful U#7 逐字' 指 prompt 非 asset).
  - synth_deck 5 例: SpiceDeckExplain (track=synthesized + reframe '自包含合成' 双 synth 信号) +
    SpiceDeckPairDiff (generic .inc model_tt.inc/netlist.inc + PULSE 0 1.0 stimulus) +
    SpiceMeasInjector (trimmed testbench real /home/data08+/proj/m2701 paths embedded) +
    SpiceParamSweepGen (synth .param defaults real /proj/drvqa path embedded) +
    SpiceSim (自包含 + level-1 .model portable reconstruction 双 marker).
  - synth_data 2 例: SpfExtractFeasibility (curated env_manifest.json constructed API surface,
    real user/host kailiu but scan manifest 非 raw scp) + SpfMeasDiag (DSPF SPF generic PEX_CASE
    + FineSim log real-format banner mimicry, '格式参考；不参与判分' framing).
  - synth_tree 1 例: SpiceCfgDirMerge (track=synthesized, shdc_A/apps_A dir trees, 承 r816
    SentaurusDeckSetupSummary synth_tree 型).
"""

import json
import os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-SpRcAlterGen-001": ("A-faithful",
        "sample_base.sp = 真实 DSIM/FineSim testbench export (header 'Spice Simulation Testbench "
        "Created by DSIM / Design Library Name: VictorQin_Study / Design Cell Name: "
        "LWL_study_SWDarray / Created On: 2026/04/29 14:25:18 / For Simulator: Finesim' + 'tWL "
        "simulation for IGZO 1SC1LWL structure' 真实 DSIM export banner + real library "
        "VictorQin_Study matching trace user victorq@hfeg0plg96 + real date 2026/04/29 + real "
        ".option finesim_mode=spicehd/PARHIER=LOCAL + 5 .lib + .temp -40 + .param CapO/Cgatein/"
        "Cthick/Cthin/TierNum/RpSC/CpSC/RpC/CpC/CCpC + .tran 10p 600n sweep WL_len 1024 2048 256 "
        "+ 9 .meas tran); rc_config.json = synth supporting config (两段 rc_runs run0_bigSC_smallpC/"
        "run1_smallSC_bigpC + wl_len_sweep start=1024 stop=1536 step=256); task_brief.md = 交付接口 "
        "(sp_rc_alter_gen.py); output_format_spec.txt = synth output format spec; track=None (缺 "
        "metadata 非 synth 信号但 asset real); layer=L1; real_task_summary verbatim victorq U#1 "
        "'帮我改上述激励，SC 的参数和 pC 的参数是联动的...保证 tWL 仿真均一性'; 真实 DSIM/FineSim "
        "testbench export banner + real library matching trace user ⇒ A-faithful (real DSIM "
        "FineSim testbench export, 新信号族: real DSIM testbench export banner; 扩展 r813 export "
        "header 强信号族至 DSIM testbench export 域; rc_config.json synth supporting config)"),
    "EDA-Eval-DesignFlow-SpTemplateOpt-001": ("A-faithful",
        "control_template_A.sp = 真实 FineSim 控制模板 (header '*********************************' "
        "+ .option PARHIER=LOCAL/SCALE=1.00/finesim_mode=spicehd/finesim_prbport=0/finesim_maxicout="
        "0/finesim_vdd=3.5v/measfile=1 measform=3/finesim_output=fsdb + *.option fsdb_out=0/POST=0 "
        "注释 + **.option finesim_fsdb_version=5.4 真实 FineSim option block); prompt.txt = verbatim "
        "用户原话 desc 显式 '真实用户原话（A-faithful，reedchen @ hfeg0pkn002，trace "
        "1791945700744_chg46 U#3 逐字）：分析 control_template.sp 模板优化空间，给优化版本'; "
        "task_brief.md = 交付接口 (optimize_sp_template.py); reframe_note 显式 'asset_fidelity 缺标"
        "应 real-from-trace (control_template.sp 真实模板作可见 A, 待 @A apply 档2)'; track=faithful "
        "(与 asset 一致); layer=None (缺标, reframe_note 注应补 L1); 真实 FineSim control template + "
        "reframe_note 显式声明 real-from-trace + verbatim prompt ⇒ A-faithful (real FineSim control "
        "template; 新 sub-type: reframe_note self-declares provenance; track=faithful 与 asset 一致)"),
    "EDA-Eval-DesignFlow-SpfAutosimSetup-001": ("A-faithful",
        "terminal_pex_info.json = 真实 terminal PEX 运行信息 (project TV1_FS + rev_tag Rev07 + "
        "tool_version GloryEX_2026.06_P010 + run_dir '/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/"
        "pex/pex420/pex1024x72' real /proj/lacaa path + vdd_nominal 0p75v + temperatures m40c/125c "
        "+ corners tt/ff/ss + corner_map_long + pex_deck_dir '/proj/lacaa/TV1_DBC_Virtuoso/workdir/"
        "jianwenl/simulation/current/pex_20261030/35H_PEX_FS_V0d1_Rev07_20261030/...' + dbc_dir "
        "'/rundata/lacaa/TV1_FS/simdir/finesim/workdir/peinie/pex_rule/DBC/' real /rundata path + "
        "lvs_rule '35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test08.lvs'); TASK_EXTRA_"
        "SPF_M4B4.md = 真实任务说明 (header '# TASK_EXTRA_SPF_M4B4.md' + '现有：拿的cad那边发的pex"
        "目录，在terminal跑的抽取2P的M4B4和M4B1在多个pvt下的spf' + real /proj/lacaa run_dir + '廖建文"
        "路径下的lvs runset和PEX deck' + 'GloryEX_2026.06_P010'); spf_extractor_config.json = patch "
        "前模板 (placeholder fs_dir/dbc_dir/lvs_rule, 5 CCI 键无 CCI_Flow_for_CUI/ 前缀); autosim_"
        "param_spec.md = AutoSim 入参规格; track=None; layer=L2; real_task_summary e0046686 "
        "terminal 跑 2P PEX M4B4(1024x72)/M4B1(32x72) 多 PVT SPF 抽取迁移 autosim; 真实 terminal PEX "
        "run info JSON + real /proj/lacaa + /rundata paths + real GloryEX Rev07 tool version + "
        "real task md ⇒ A-faithful (real terminal PEX run metadata, 新 sub-type: real PEX run "
        "info JSON; track=None 但强 real 信号群)"),
    "EDA-Eval-DesignFlow-SpfExtractFeasibility-001": ("synth_data",
        "env_manifest.json = 合成/curated 环境扫描 manifest (header 'scan_id: aether-env-scan-"
        "20261105-kailiu' + cell 'MyLib/INV/layout' + real user kailiu + real host hfeg0plg100 + "
        "workspace root '/ai_sandbox/drcpa/V0/agentdir/kailiu' + 'is_empty: true' note + curated "
        "pyaether_apis 列表 aeGetCurDesign/emyDesignGetName/dbGdsOut/dmExportNetlist/dmDspfIn 非 "
        "raw scp/export 而是 constructed API surface listing); task = Q&A 能力查询 (用户问 '你有抽"
        "一个cell的spf文件的功能吗', 助手扫描 pyAether API/skill/CAD 后发现无直接 SPF 导出 API, "
        "推荐 aeIpcBeginProcess 调外部提取器 StarRC 走 6 步流程产 spf_export.py); track=None; "
        "layer=L1; reframe_note 显式 'SPF 抽取能力查询->produce-different-artifact (portability+"
        "produce-different-artifact borderline reframe, §4 有牙必要, r732 spotcheck batch11)'; "
        "real_task_summary kailiu@hfeg0plg100 Q&A; 合成/curated env manifest fixture (real user/"
        "host kailiu but constructed API surface listing 非 raw scp/export, scan_id 显式 "
        "aether-env-scan 标记) ⇒ synth_data (curated env_manifest.json constructed API surface "
        "fixture; Q&A capability-query task; 承 env-config 类)"),
    "EDA-Eval-DesignFlow-SpfMeasDiag-001": ("synth_data",
        "PEX_CASE_A.spf = 合成 DSPF 1.3 格式 SPF 网表 fixture (header '*|DSPF 1.3 / *|DIVIDER . / "
        "*|DELIMITER : / *|SUBCKT PEX_CASE / .SUBCKT PEX_CASE IN1 IN2 IN3 IN4 IN5 IN6 OUT1 OUT2 "
        "OUT3 OUT4 OUT5 OUT6 VDD VSS + *|I (XI_INV_C.MIMN0:d ...) nsvt_fs w=180n l=40n' 真实 DSPF "
        "1.3 格式 但 generic subckt 名 'PEX_CASE' 非 real design name); tb_A.sp = 合成 FineSim "
        "测试平台 (6 .meas tran INTEGRAL + .option measform=2 + .tran, desc '格式参考；不参与判"
        "分'); sim_A.log = 合成 FineSim 仿真日志 (header 'FineSim(S) Version 2024.1.0 -- Jan 2025' "
        "real-format FineSim banner mimicry + 'Sun Nov 12 10:23:51 2026' + 'input file: sim_inv_"
        "Rev03.sp' + 'title: pex inv cap measurement rev03' 但 desc '格式参考；不参与判分'); "
        "task_context.md = synth 任务上下文 doc; track=None; layer=L2; real_task_summary fan1yang@"
        "hfeg0plg104 FineSim PEX 后仿 inverter 电容测量 .meas 失败诊断; 合成 DSPF SPF + FineSim "
        "testbench + FineSim log fixtures (real-format FineSim banner mimicry; generic PEX_CASE "
        "subckt name 非 real design; 三文件 desc 全 '格式参考；不参与判分' framing) ⇒ synth_data "
        "(合成 DSPF SPF netlist + FineSim testbench + FineSim log fixtures; real-format FineSim "
        "banner faithful mimicry; '格式参考；不参与判分' framing; generic PEX_CASE subckt)"),
    "EDA-Eval-DesignFlow-SpfNtsvMissingDiag-001": ("A-faithful",
        "spf_bl_extract.py = 真实 SPF 抽取脚本 (header '#!/usr/bin/env python3 / # author: E0041050 "
        "/ # spf_bl_extract.py — extract per-layer coupling capacitance from an SPF file. / Usage: "
        "python spf_bl_extract.py <spf_file> --range <lo-hi> --output <csv>' 真实 author header "
        "E0041050 + real script purpose + real argparse/csv/defaultdict import + parse_layer_map "
        "函数); CXSA_A.spf = 真实 SPF (header '*SPF / *LAYER_MAP / *16 M1net ITF=M1 / *17 M2net "
        "ITF=M2 / *18 M3net ITF=M3 / *19 M4net ITF=M4 / *20 M5net ITF=M5 / *21 M6net ITF=M6' real "
        "LAYER_MAP with real layer names); task_brief.md = 交付接口; track=faithful (与 asset 一致); "
        "layer=None; reframe_note 显式 'SPF nTSV $lvl=86 单层 coupling 漏诊断+patched 抽取器->"
        "produce-tool (Q&A debug-Q&A+fix-proposal->produce-tool patched extractor reframe, §4 有牙"
        "必要, r749 spotcheck batch27): 用户 jianilu@hfeg0pkn004 U0 逐字'; real_task_summary "
        "spf_bl_extract.py misses $lvl=86 (nTSV layer) coupling, parse_cap_line only accepts "
        "$lvl1=/$lvl2= paired format; 真实 SPF 抽取脚本 with real author header E0041050 + real SPF "
        "CXSA_A.spf real LAYER_MAP ⇒ A-faithful (real script with real author header + real SPF; "
        "承 r817 real script author header 强信号族至 SPF extractor script; track=faithful 与 "
        "asset 一致)"),
    "EDA-Eval-DesignFlow-SpiceCfgDirMerge-001": ("synth_tree",
        "shdc_A = 合成 spice config 目录树 (shdc_A/projsets/{commonIP,dbcoa,lhiob} 子目录 + shdc_A/"
        "other/file.sp '* file shdc / x1 a y inv' minimal synth content + file2.sp/ws_only.sp/"
        "editor.tmp/old.bak/oldfile~ 合成文件); apps_A = 合成 spice config 目录树 (apps_A/projsets "
        "同型); spec_A.json = 合并 spec; track=synthesized (与 asset 一致, 显式 synth 信号); "
        "layer=None; reframe_note None; real_task_summary chengk@hfeg0pgn022 读取 shdc 与 apps 两"
        "个 spice 配置目录对比差异合并; 合成 spice config 目录树 fixtures (track=synthesized 显式 "
        "synth + minimal synth .sp content '* file shdc / x1 a y inv') ⇒ synth_tree (合成 config "
        "directory tree fixtures shdc_A/apps_A; track=synthesized 与 asset 一致; 承 r816 "
        "SentaurusDeckSetupSummary synth_tree 型)"),
    "EDA-Eval-DesignFlow-SpiceDeckExplain-001": ("synth_deck",
        "doc/netlist.sp = 合成自包含 HSPICE deck (header '***Block1:Hspice Option***' + .inc './"
        "Setting.sp' + '***Block3:Power Defined***' + .param pvdd1=1.8 pvcc=1.05 pvss=0 pvwlp=2.95 "
        "pvtsc=1.17 pvdleq=1.17 + vvdd1/vvcc 真实格式 HSPICE option block 但 deck 合成); doc/"
        "deck_meta.txt = real trace metadata doc (file_name 8_commode.sp / project DDGOA LPDDR5X / "
        "block 0_VtscAct_pre / owner hanhu / user junweix / host hfeg0pkn002 真实 trace 元数据 但 "
        "meta doc 非 asset 主体); task_spec.json = synth task spec; track=synthesized (与 asset "
        "一致, 显式 synth 信号); layer=L1; reframe_note 显式 'spice deck 共模跟踪精度解释->produce "
        "(portability+explain->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12): "
        "用户 junweix@hfeg0pkn002 要解释 8_commode.sp; A 不可行原因=真实 /proj/commonIP 工程目录+"
        "PrimeSim/HSPICE 环境 SUT 沙盒不可达 -> 用自包含合成 8_commode.sp/Setting.sp/.mt0/.log/.pd'; "
        "real_task_summary junweix 解释 8_commode.sp; 合成自包含 HSPICE deck (track=synthesized + "
        "reframe_note 显式 '自包含合成' 双 synth 信号; deck_meta.txt real trace 元数据 but deck "
        "synth; portability reframe real /proj/commonIP 不可达) ⇒ synth_deck (合成 self-contained "
        "HSPICE deck fixture; track=synthesized 与 asset 一致)"),
    "EDA-Eval-DesignFlow-SpiceDeckPairDiff-001": ("synth_deck",
        "deck_ref_A.sp = 合成 FineSim testbench (header '* FineSim testbench - pre-modification "
        "(baseline = _finesim_pre.sp)' 描述性 header + .option POST=1 INK2 RELTOL=1e-6 + .param "
        "vdd=1.0 temp=-40 + .inc model_tt.inc / .inc netlist.inc generic includes + .tran 1n 100n "
        "0 1n + .nodeset + .probe v(clk) v(data) + Vclk clk gnd PULSE 0 1.0 0 1n 1n 4n 10n generic "
        "PULSE stimulus); deck_cmp_A.sp = 同型 合成 FineSim testbench (post-modification variant); "
        "track=faithful (与 asset 不一致, track=faithful 指 prompt verbatim U#7 但 asset 合成 "
        "⇒ track≠asset_provenance 累计 38→39); layer=None; reframe_note 显式 'FineSim deck 配对"
        "结构化 diff 报告器->produce-tool (Q&A explain-Q&A->produce-tool diff CLI reframe, §4 有牙"
        "必要, r747 spotcheck batch25): 用户 e0024852@hfeg0pkn004 U0 逐字'; real_task_summary "
        "'A-faithful U#7 逐字「I want to know the difference of _finesim.sp and _finesim_pre.sp」' "
        "(A-faithful 指 prompt verbatim 非 asset); 合成 FineSim deck pair fixture (generic .inc "
        "model_tt.inc/netlist.inc + generic PULSE stimulus + 描述性 header; track=faithful prompt "
        "verbatim 但 asset synth_deck ⇒ track≠asset_provenance; portability reframe real /proj "
        "decks 不可达) ⇒ synth_deck"),
    "EDA-Eval-DesignFlow-SpiceMeasInjector-001": ("synth_deck",
        "004_onlySlicer_delay_m2701.sp = 合成/trimmed FineSim/HSPICE DDR4 DFE slicer testbench "
        "(header '****** HSPICE Default Option for Block Level Simulation' + .inc '/home/data08/"
        "V0/simrun/hspice/joewu/1_sim_option/other_option' real /home/data08 path embedded + .inc "
        "'/home/data08/V0/simrun/hspice/joewu/1_sim_option/hspice_option' + .lib '/proj/m2701/"
        "V0_DDR4/model/current/model.sp' top_tt real /proj/m2701 path embedded + .temp 45 + .param "
        "VVDD=0.875 VREF=0.125; desc 'Input A: trimmed FineSim/HSpice DDR4 DFE slicer testbench .sp "
        "with existing .probe/.meas statements...开发自测用；评测在 hidden B'); meas_spec.json = "
        "synth JSON measurement spec (power_subckt=XI7/edge_signal=LDFEdataEr/threshold=vvdd-0.36/"
        "from=1.53n); task_context.md = synth context; track=None; layer=L2; real_task_summary "
        "jiangbaol@hfeg0pkn004 DDR4 DFE slicer FineSim 仿真添加 .measure 语句; trimmed/synth "
        "testbench fixture (real /home/data08 + /proj/m2701 paths embedded in trimmed deck 但 "
        "desc 'trimmed...开发自测用' framing; track=None) ⇒ synth_deck (trimmed FineSim/HSPICE "
        "testbench fixture with real /proj paths embedded; 同 r816 SimCapLisParse real /proj path "
        "embedded in synth .lis 型)"),
    "EDA-Eval-DesignFlow-SpiceParamSweepGen-001": ("synth_deck",
        "template.sp = 合成 HSPICE 参数化 sweep 模板 (header '*************************Add finesim "
        "option******************' + .inc '/proj/drvqa/V0/workdir/robinluo/simulation/00_common/"
        "finesimconfig.sp' real /proj/drvqa path embedded + '* Parameter definitions for V1 FBCC "
        "RBL sweep' + .param Sanadj1=1/Sanadj2=1/Sanadj3=1/Sanadj4=1/Sapadj1=1/Sapadj2=1/Sapadj3=1 "
        "default placeholder values synth); spec.json = 合成 sweep 规格 (变量定义 Sanadj/Sapadj 二值 "
        "+ R_BL 列表 + 约束 Sapadj==Sanadj + 文件夹/文件命名 pattern); track=None; layer=L2; "
        "real_task_summary vincentz@10.129.2.13 以 mixbest_V1_RBL_95_no_probe_I.sp 为基础模板生成 "
        "9 变量 240 个参数化 .sp 文件; 合成 HSPICE 参数化 sweep template fixture (real /proj/drvqa "
        "path embedded in .inc 但 .param Sanadj/Sapadj default=1 placeholder values synth; track="
        "None; portability reframe real template 在 /proj 不可达) ⇒ synth_deck (synth HSPICE "
        "parameterized sweep template; real /proj path embedded but .param defaults synth; 同 "
        "r818 SpGen level-1 minimal + real /proj path embedded in synth 型)"),
    "EDA-Eval-DesignFlow-SpiceSim-001": ("synth_deck",
        "netlist.sp = 合成自包含 HSPICE 网表片段 (desc 显式 '自包含 HSPICE 网表片段：4 级非反相 "
        "buffer 链(dq_stg1→dq_stg2→dq_stg3→dq_main)，含 level-1 .model + pulse 激励 + .tran，无 "
        ".end' — '自包含' + 'level-1 .model' 双 portable reconstruction marker); nodes.txt = 合成"
        " 节点清单 (dq_stg1/dq_stg2/dq_stg3/dq_main); spec.txt = 合成测量规格 (vdd=1.8/spec_trtf="
        "100p/duty_lo=0.45/duty_hi=0.55); MEAS_tr.sp.example = 合成 .measure trig/targ 范例; "
        "task_brief.md = 交付接口 (含错解清单 交错/硬编/缺 rise-fall/只 tr/用 0-100%); track=None; "
        "layer=L2; real_task_summary irene1li@hfeg0pkn004 DDR4 P2S predriver TX 链 tr/tf/duty 测量; "
        "合成自包含 HSPICE netlist fixture ('自包含' + 'level-1 .model' 双 synth marker, portable "
        "reconstruction; track=None) ⇒ synth_deck (合成 self-contained HSPICE netlist with level-1 "
        "MOS model portable reconstruction; '自包含' + level-1 双 marker)"),
}


def main():
    before = 0
    applied = []
    skipped = []
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
        md["asset_fidelity"] = val
        d["metadata"] = md
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
            f.write("\n")
        applied.append((cid, val))

    print("=== 档2 asset_fidelity backfill r819 batch19 ===")
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

    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r819_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r819_manifest.tsv — r819 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch19 (12 cases, alphabetical next 12 missing after r818 batch18 SpGen: SpRcAlterGen..SpiceSim, Sp→Spice 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r818 档2 batch1-18 (+204, 106→322) done. 本轮 r819 档2 batch19.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'real trace'/'忠实缩减'/'trace-faithful' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / '重构' / minimal reconstruction / 'Generated as' / '示例' / 'Input A' / 'visible input A' / 'portable, model-free' / Chinese synth header / decoy comment / real-format export banner faithful mimicry / linear data progression / 显式 'stub' marker / level-1 MOS 模型 / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 33% (4/12) — Sp→Spice 段 real-trace 资产 (r818 累计 86/216=39.8%; 本批 4/12=33%, 累计 90/228=39.5%) / 新信号族 4 类 (real DSIM FineSim testbench export banner SpRcAlterGen 'Spice Simulation Testbench Created by DSIM / Design Library Name: VictorQin_Study / Created On: 2026/04/29' + reframe_note self-declares provenance SpTemplateOpt 'asset_fidelity 缺标应 real-from-trace...待 @A apply 档2' + real terminal PEX run metadata JSON SpfAutosimSetup terminal_pex_info.json GloryEX Rev07 + real /proj/lacaa + real script author header SpfNtsvMissingDiag '# author: E0041050') / track≠asset_provenance 1 例 (SpiceDeckPairDiff, track=faithful prompt verbatim U#7 但 asset synth_deck generic .inc/PULSE, 累计 38→39) / synth_deck 5 例 (SpiceDeckExplain track=synthesized+reframe '自包含合成' + SpiceDeckPairDiff generic .inc model_tt.inc/netlist.inc+PULSE + SpiceMeasInjector trimmed testbench real /home/data08+/proj/m2701 paths embedded + SpiceParamSweepGen synth .param defaults real /proj/drvqa path embedded + SpiceSim 自包含+level-1 .model) / synth_data 2 例 (SpfExtractFeasibility curated env_manifest.json API surface + SpfMeasDiag DSPF SPF generic PEX_CASE+FineSim log real-format banner mimicry '格式参考；不参与判分') / synth_tree 1 例 (SpiceCfgDirMerge track=synthesized shdc_A/apps_A dir trees)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 322->334 (cases/B 334==B.jsonl 334 ✓); miss 73->61\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
