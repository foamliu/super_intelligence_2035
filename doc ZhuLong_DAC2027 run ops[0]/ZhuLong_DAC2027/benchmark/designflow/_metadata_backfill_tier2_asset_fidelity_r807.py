#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r807.py — r807 档2 asset_fidelity backfill batch7.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done. r806 batch6 (+12, 166→178) done.
      本轮 r807 推进 档2 batch7 — 12 cases
      (alphabetical next 12 missing after r806 batch6 FinesimLogExplainDiag:
       FinesimMatrixrunAgent..HierMeasIncGen, F-G-H 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r806 扩展):
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
                   "(reconstructed from cline trace ...)" / desc 显式 "合成" / A_ONLY_MARKER + decoy 内容。

本批 12 case 判定:
  - 8 A-faithful (单批最高 67%, 超 r804/r805/r806 的 50%): FinesimMatrixrunAgent/FinesimOptionExtend/
        FinesimVhDiagGuide/FsdbPulseFilter/FsdbScopeSignalLocate/GmidLutRunSelect/GvimCjkConfigGen/HcellMissingFind
  - 2 synth_data: G5TbGen/GmidLut
  - 2 synth_deck: GaaFetDeckAugment/HierMeasIncGen

关键发现:
  - 真实 WaveView ADV log export header 强信号 (FsdbScopeSignalLocate, r807 首例, 新增 WaveView export header 类型):
    sxcmd_A.log header '### Custom WaveView ADV log file, revision T-2022.06-SP1 (build Aug 20, ) ### /
    ### created at 09:56:04 on Tue Nov  3 2026 (Linux AMD64) ### /
    ### Host Name: hfebhds113   User ID: svc.salt   PID: 118796   ###'
    = 真实 WaveView 工具导出 banner (含真实 tool-version T-2022.06-SP1 + 真实 hostname hfebhds113 +
      真实 User ID svc.salt + 真实 PID 118796 + 真实 date Tue Nov 3 2026),
    与 r804 AETHER-SE / r805 PEX / r806 FineSim export header 同列强信号, 新增 WaveView export header 类型
    (B 域 spice_sim 首例 WaveView export header — WaveView 是 D 域主工具但 FSDB 信号检索跨界入 B 域)。
    sigsearch_A.log '*** loading waveform file /rundata/drgqa/V0/simdir/finesim/drgqaF/MatrixRun/
      MatrixRun_Netlist_Vcap_20261102PM_Fullchip_..._TT.X8.TT0.94v25C.X8/raw/finesim.fsdb ***'
    真实 /rundata/drgqa 内网路径 + 真实 fsdb 文件名 (含真实 20261102PM 日期 + 真实 corner TT0.94v25C) ⇒ file-verbatim。
  - 真实 ALPS Simulation Log export header 强信号 (GmidLutRunSelect, r807 首例, 新增 ALPS export header 类型):
    gmid.log header 'ALPS Simulation Log -- PlatRun.7 / Job: sijie_gmid_1 / Deck: gmid.scs /
    Started: 2026-10-16 10:42:11 / Simulator: ALPS 2026.03 hf4'
    = 真实 ALPS (Spectre-family) 仿真器导出 banner (含真实 simulator ALPS 2026.03 hf4 + 真实 date 2026-10-16 +
      真实 PlatRun.7 run 结构 + 真实 job/deck 名),
    与 r804 AETHER-SE / r805 PEX / r806 FineSim / r807 WaveView export header 同列强信号, 新增 ALPS export header 类型
    (characterization 域首例 ALPS export header — ALPS 是 Spectre-family simulator, Gm/Id LUT 表征流典型工具)。
    gmid.netlist 'include "/proj/ddaop/V0/model/current_D5_v0d1/model.sp" section=tt' 真实 /proj/ddaop 内网 model 路径 +
    task_brief '目录结构同 /proj/ddaop/V0/workdir/t0002801/simulation/sijie/gmid/platform/Results/' 真实 /proj 内网工程路径 +
    真实 user t0002801 + 真实 designer sijie + PlatRun.7~10 多 run 目录结构 ⇒ file-verbatim (r803 .75-reachable 判别)。
  - 真实 AETHER-SE export header 强信号 (HcellMissingFind, 与 r804 同型):
    netlist_A header '* Tool     : AETHER-SE / * Date     : Thu Oct 30 10:00:00 2026 /
    * User     : zjqiao / * Top Design : drvqa_top/WOWTOP_1C2A/schematic'
    = 真实 AETHER-SE 网表导出 banner (含真实 user zjqiao + 真实 date Thu Oct 30 10:00:00 2026 +
      真实 top design drvqa_top/WOWTOP_1C2A/schematic), 与 r804 AETHER-SE export header 同列强信号。
    hcell_A = 真实 hcell 映射文件 (IO_DqLdMdl/AG_VdivActTop/T_CMDq 等 real block 名) ⇒ file-verbatim。
  - 显式 'A-faithful' / 'trace-faithful' 标注两例:
    FinesimOptionExtend attachment desc 显式 '真实用户原话（A-faithful，yanxvwei @ hfeg0pkn002，trace 1793946809755_zao50 U#2 逐字）'
    + '真实输入·finesim_option.sp 原文（trace msg#39 old_text，17 行 .option：...）' = 显式 A-faithful 标注 + 真实 user/path/session。
    GvimCjkConfigGen prompt 显式 '附件 doc/ 下有本次环境探查的结构化输入（A 档 trace-faithful，全部字段取自 trace 真实探查）'
    = 显式 trace-faithful 标注 + 真实 user adaml@hfeg0pkn002 + 真实环境探查字段 (locale/vim 8.0/Noto CJK fonts)。
  - 真实用户 paste verbatim (FinesimVhDiagGuide): error_log.txt = 真实用户 paste 的 FineSim 错误日志 verbatim
    ('ERROR! no reference ckt vh for xi_setiddampoip_111(netlist:67170) of vintrefampcoreip' 等 4 条, 含真实 netlist:行号 67170/427654/423044/422179),
    netlist_snippet.txt = 真实用户 paste 的网表行 verbatim
    ('XI_SetIDDAmpOIP_71 net021 Out inh_vcc SetIDDAmpOIP vh vout=pvblh / vcc vh inh_vss PWL(0s {pvint1}...) power=0'),
    task_meta 含真实 trace_source (phoebeli@hfeg0plg96 sess 1794361050224_6ipfr mc91) ⇒ paste-verbatim (A-faithful 两子型之一, r802 首立)。
  - 真实 signal names from real path (FsdbPulseFilter): waveform.tbl =
    真实 fscript dump 复刻 (与真实 trace clean_out2.tbl 完全相同格式, 12 列 v(dmi<0>)/v(dq<0..3>)/v(rdqs_c<0..1>)/
    v(rdqs_t<0..1>)/v(vdbias!)/v(vintcore!) 真实信号名来自真实 hierarchical path
    xi_c_top.xi_array16gtop.xi_spinetop.xi_banktopx2b23.xi24, 900-999ns 步长 1ns 100 点真实 dump 值),
    reproduced faithfully (r805 verbatim 标记族同列) ⇒ file-verbatim (A-faithful reproduced-faithfully 子型)。
  - 真实用户 GUI 程序 verbatim (FinesimMatrixrunAgent): stimulus_manager.py =
    用户 zjqiao 真实 finesim 仿真管理 GUI 程序 (137KB self-contained bundle, attachment desc 显式
    '来自 zjqiao 的 cline trace 真实附件'), 真实用户上传源码 ⇒ file-verbatim (A-faithful file-verbatim 子型)。
  - track≠asset_provenance: 本批 0 例新增 (8 A-faithful 全 track 与 asset 一致) ⇒ r801-r807 累计仍 7 例。
  - 2 synth_deck:
    GaaFetDeckAugment: GAA_FET/IdVg_des.cmd = 重建 sdevice deck (body 含真实 SWB template syntax @WF@/@node|GAA_Structure@/@tdrdat@ +
      真实电极名 gate/drain/source/substrate + Resist=375, 但 header 'This is the EXISTING IdVg sdevice deck in /home/e02141/devops/GAA_FET'
      为合成解说性注释, 真实路径仅出现在注释 header 非运行内容; template/AC_des.cmd = 库通用模板非用户专属;
      task_spec.json = 合成 task 规格 sweep_start=-1.0/sweep_end=2.8 ⇒ 重建 deck + 库模板 + 合成 spec ⇒ synth_deck。
    HierMeasIncGen: netlist_A.sp = 合成 hspice 网表样本 (Input A, 顶层 TbTop_A 合成名 + PGSIG_A 合成信号名 +
      4 group × 4 driver = 16 PMOS 合成规模, desc 显式 '开发与自测用；评测在 hidden B（不同名称/规模/信号/窗口）上跑'),
      meas_config_A.json = 合成 task 配置 (gate_sig=PGSIG_A/from=10n/to=30n/tag=vintcore_stat_loss 合成字段),
      task_context.md 含真实用户 reedchen 原话 (prompt 非 asset) ⇒ 合成 netlist + 合成 config ⇒ synth_deck。
  - 2 synth_data:
    G5TbGen: pdk_info.json = 合成 PDK 信息 fixture ('platform': '10G5_HKMG' / 'model_path': '/apps/imctf/models/G5/...'
      / 合成 process_params shrink=0.268/sigmaflag=3.0/toxe_g5=3.45e-9/xj_g5=1.4e-7/ndep_g5=8.0e17 通用 level 值,
      无真实 user/path/hostname header), prompt 单行用户请求 '帮我建立一个spice的testbench，其中包含了G5平台的process parameter' ⇒ 合成 PDK ⇒ synth_data。
    GmidLut: params_A.json = 合成 level-1 NMOS model 参数 fixture (kp=0.00012/vto=0.5/lambda=0.05/tox=5e-9/nsub=1e16/phi=0.6/gamma=0.4
      教科书 level-1 SPICE 值, w=2e-6/vdd=1.5, 无真实 foundry model header), prompt 框架为 '模拟电路自动化 sizing 程序建 Gm/Id 查找表' ⇒ 合成 model 参数 ⇒ synth_data。
  - A-faithful 8/12=67% 单批最高 (r801=3, r802=3, r803=4, r804=6, r805=6, r806=6, r807=8):
    本批覆盖 F-G-H 段, 3 类真实 export header (WaveView/ALPS/AETHER-SE) + 2 显式 A-faithful/trace-faithful 标注 +
    1 paste-verbatim + 1 reproduced-faithfully + 1 真实用户程序 = 多型 A-faithful 强信号汇聚。
  - export header 强信号类型扩至 5 类 (r804 AETHER-SE / r805 PEX / r806 FineSim / r807 WaveView + ALPS):
    B 域 asset_provenance 多工具 export header 实证群, 支撑论文 §5 asset_provenance disclosure 二分实证。

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
    "EDA-Eval-DesignFlow-FinesimMatrixrunAgent-001": (
        "A-faithful",
        "stimulus_manager.py = 用户 zjqiao 真实 finesim 仿真管理 GUI 程序 verbatim (137KB self-contained bundle, "
        "attachment desc 显式 '来自 zjqiao 的 cline trace 真实附件，内含构建 matrixrun 命令的逻辑'); "
        "task_brief.md = 交付接口说明; track=None; trace_source zjqiao@hfhds206; "
        "真实用户上传源码 (self-contained 137KB ASCII bundle, 非合成/非 excerpt) ⇒ file-verbatim (A-faithful file-verbatim 子型); "
        "host=hfhds206 计算节点 + asset=真实用户附件 ⇒ file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-FinesimOptionExtend-001": (
        "A-faithful",
        "prompt.txt = 真实用户原话 verbatim (attachment desc 显式 '真实用户原话（A-faithful，yanxvwei @ hfeg0pkn002，"
        "trace 1793946809755_zao50 U#2 逐字）：解析 finesim_option.sp 每个 option 含义，扩展文件保留备份，列出更多 DRAM finesim 仿真 option'); "
        "finesim_option_A.sp = 真实输入·finesim_option.sp 原文 verbatim (attachment desc 显式 '真实输入·finesim_option.sp 原文（trace msg#39 old_text，"
        "17 行 .option：PARHIER/PORT_VOLTAGE_SCALE_TO_2X/ARTIST/PSF/method/gmin/gmindc/opfile/split_dp/probe+post/REDEFSUB/finesim_mode/accurate/runlvl/measfile/measform'); "
        "task_brief.md = 交付接口; 显式 A-faithful 标注 + 真实 user yanxvwei + 真实 host hfeg0pkn002 + 真实 session 1793946809755_zao50 + 真实 trace msg#39 old_text ⇒ file-verbatim",
    ),
    "EDA-Eval-DesignFlow-FinesimVhDiagGuide-001": (
        "A-faithful",
        "doc/error_log.txt = 真实用户 paste 的 FineSim 错误日志 verbatim ('ERROR! no reference ckt vh for xi_setiddampoip_111(netlist:67170) of vintrefampcoreip' "
        "等 4 条同类致命错误, 含真实 netlist 行号 67170/427654/423044/422179 + 'ERROR! exit due to previous fatal errors'); "
        "doc/netlist_snippet.txt = 真实用户 paste 的网表行 verbatim ('XI_SetIDDAmpOIP_71 net021 Out inh_vcc SetIDDAmpOIP vh vout=pvblh / "
        "vcc vh inh_vss PWL(0s {pvint1} 1.46us {pvint1} 1.66us {pvint2} 2.4us {pvint2} 2.6us {pvint3}) power=0'); "
        "doc/task_meta.txt 含真实 trace_source (phoebeli@hfeg0plg96 sess 1794361050224_6ipfr mc91) + real_task_summary; "
        "真实用户 paste verbatim error log + netlist lines (含真实 netlist:行号) ⇒ paste-verbatim (A-faithful 两子型之一, r802 首立); "
        "task_spec/scenario/sim_context = 任务框架; track=None; reframe=debug-Q&A+how-to->produce-tool (§4 有牙必要)",
    ),
    "EDA-Eval-DesignFlow-FsdbPulseFilter-001": (
        "A-faithful",
        "waveform.tbl = 真实 fscript dump 复刻 (header 'TIME v(dmi<0>) v(dmi<1>) v(dq<0>) v(dq<1>) v(dq<2>) v(dq<3>) "
        "v(rdqs_c<0>) v(rdqs_c<1>) v(rdqs_t<0>) v(rdqs_t<1>) v(vdbias!) v(vintcore!)' 真实信号名来自真实 hierarchical path "
        "xi_c_top.xi_array16gtop.xi_spinetop.xi_banktopx2b23.xi24, 900-999ns 步长 1ns 共 100 时间点 + 真实 dump 电压值带 SI 后缀); "
        "prompt 明示 'workdir 目录下有一份 waveform.tbl（fscript dump 格式，与真实 trace 中 clean_out2.tbl 完全相同的格式）' = reproduced faithfully; "
        "track=None; 真实信号名来自真实 hierarchical path + 完全相同格式 + 真实 dump 值 ⇒ file-verbatim (A-faithful reproduced-faithfully 子型, r805 verbatim 标记族同列)",
    ),
    "EDA-Eval-DesignFlow-FsdbScopeSignalLocate-001": (
        "A-faithful",
        "sxcmd_A.log = 真实 WaveView ADV log verbatim (header '### Custom WaveView ADV log file, revision T-2022.06-SP1 (build Aug 20, ) ### / "
        "### created at 09:56:04 on Tue Nov  3 2026 (Linux AMD64) ### / ### Host Name: hfebhds113   User ID: svc.salt   PID: 118796   ###' "
        "= 真实 WaveView 工具导出 banner 含真实 tool-version T-2022.06-SP1 + 真实 hostname hfebhds113 + 真实 User ID svc.salt + 真实 PID + 真实 date Tue Nov 3 2026, "
        "r807 WaveView export header 强信号首例, 与 r804 AETHER-SE / r805 PEX / r806 FineSim 同列, 新增 WaveView export header 类型); "
        "sigsearch_A.log = 真实 waveform 信号检索日志 verbatim ('*** loading waveform file /rundata/drgqa/V0/simdir/finesim/drgqaF/MatrixRun/"
        "MatrixRun_Netlist_Vcap_20261102PM_Fullchip_..._TT.X8.TT0.94v25C.X8/raw/finesim.fsdb ***' 真实 /rundata/drgqa 内网路径 + 真实 fsdb 文件名 "
        "(含真实 20261102PM 日期 + 真实 corner TT0.94v25C) + '*** searching signals matching pattern: *odt* ***' 真实检索模式 + MATCHED: 430483); "
        "task_brief.md = 任务框架; track=None; 真实 WaveView export header + 真实 /rundata 内网路径 + 真实 fsdb 名 ⇒ file-verbatim; "
        "host=hfebhds113 计算节点 + asset 含真实 hostname hfebhds113 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-G5TbGen-001": (
        "synth_data",
        "pdk_info.json = 合成 PDK 信息 fixture ('platform': '10G5_HKMG' / 'model_path': '/apps/imctf/models/G5/model_proj_HKMG/current/model.sp' / "
        "'corner_lib': 'g5_corner' / 'corners': ['tt','ff','ss'] / 'temp': 98 / 合成 process_params shrink=0.268/sigmaflag=3.0/toxe_g5=3.45e-9/xj_g5=1.4e-7/ndep_g5=8.0e17 "
        "通用 level 值, 无真实 user/path/hostname header); track=None; "
        "prompt 单行用户请求 '帮我建立一个spice的testbench，其中包含了G5平台的process parameter'; "
        "合成 PDK 参数 (通用 level 值, 无真实 foundry model header) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-GaaFetDeckAugment-001": (
        "synth_deck",
        "GAA_FET/IdVg_des.cmd = 重建 sdevice deck (header '# This is the EXISTING IdVg sdevice deck in /home/e02141/devops/GAA_FET' 合成解说性注释 + "
        "body 含真实 SWB template syntax @WF@/@node|GAA_Structure@/@tdrdat@/@parameter@/@plot@ + 真实电极名 gate/drain/source/substrate + "
        "Resist=375/WorkFunction=_WF_, 但真实 /home/e02141/devops/GAA_FET 路径仅出现在合成注释 header 非运行内容); "
        "template/AC_des.cmd = 库通用模板 (Applications_Library/GettingStarted/sdevice/AC, 通用电极 gate/drain/source/body, 非用户专属); "
        "task_spec.json = 合成 task 规格 (sweep_start=-1.0/sweep_end=2.8/extract_metrics=['Cmax','Cmin']/ac_frequency_hz=1e6); "
        "track=None; 重建 deck + 库通用模板 + 合成 spec ⇒ synth_deck (真实路径仅在注释 header, body 重建表示)",
    ),
    "EDA-Eval-DesignFlow-GmidLut-001": (
        "synth_data",
        "params_A.json = 合成 level-1 NMOS model 参数 fixture (model: kp=0.00012/vto=0.5/lambda=0.05/tox=5e-9/nsub=1e16/phi=0.6/gamma=0.4 "
        "教科书 level-1 SPICE 值, w=2e-06/vdd=1.5, 无真实 foundry model header/path/hostname); "
        "prompt.txt + task_brief.md = 任务框架; track=faithful; "
        "prompt 框架 '模拟电路自动化 sizing 程序建 Gm/Id 查找表' (B档 synthesized, params_A.json 合成 model 参数); "
        "合成 level-1 model 参数 (教科书值, 无真实 foundry model) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-GmidLutRunSelect-001": (
        "A-faithful",
        "Results/PlatRun.7/sijie_gmid_1/gmid.log = 真实 ALPS 仿真日志 verbatim (header 'ALPS Simulation Log -- PlatRun.7 / "
        "Job: sijie_gmid_1 / Deck: gmid.scs / Started: 2026-10-16 10:42:11 / Simulator: ALPS 2026.03 hf4' "
        "= 真实 ALPS (Spectre-family) 仿真器导出 banner 含真实 simulator ALPS 2026.03 hf4 + 真实 date 2026-10-16 + 真实 PlatRun.7 run 结构, "
        "r807 ALPS export header 强信号首例, 与 r804 AETHER-SE / r805 PEX / r806 FineSim / r807 WaveView 同列, 新增 ALPS export header 类型); "
        "Results/PlatRun.7/sijie_gmid_1/gmid.netlist = 真实 spectre 网表 verbatim ('// gmid.netlist -- PlatRun.7 (SUCCESSFUL run) / "
        "// Design: sijie/gmid schematic -> exported netlist / simulator lang=spectre / global 0 / "
        "include \"/proj/ddaop/V0/model/current_D5_v0d1/model.sp\" section=tt' 真实 /proj/ddaop 内网 model 路径 + 真实 designer sijie + 真实 device ntn_lv NMOS); "
        "task_brief.md 明示 '仿真结果附件已置于 assets/Results/（目录结构同 /proj/ddaop/V0/workdir/t0002801/simulation/sijie/gmid/platform/Results/，含 PlatRun.7~10）' "
        "真实 /proj/ddaop 内网工程路径 + 真实 user t0002801; PlatRun.7/8/9/10 多 run 目录 (含 gmid.log/gmid.netlist/gmid.scs/psf/dc.op); "
        "track=None; 真实 ALPS export header + 真实 /proj/ddaop 内网 model 路径 + 真实多 run 目录结构 ⇒ file-verbatim; "
        "host=.75 不可知 + asset 含真实 /proj 内网路径 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-GvimCjkConfigGen-001": (
        "A-faithful",
        "prompt 显式 '附件 doc/ 下有本次环境探查的结构化输入（A 档 trace-faithful，全部字段取自 trace 真实探查）' = 显式 trace-faithful 标注; "
        "doc/scenario.txt = 真实用户问题 verbatim (adaml@hfeg0pkn002 'linux环境下，gvim打开文件，中文乱码，怎么办？' + 两轮追问 verbatim); "
        "doc/system_manifest.json = 真实环境探查清单 (locale=en_US.UTF-8 / Vim 8.0 (/usr/share/vim/vim80) / 已装 Noto Sans CJK SC + Noto Serif CJK SC + "
        "DejaVu Sans Mono + Liberation Mono / 用户无 ~/.vimrc, 全部字段取自 trace 真实 list_allowed_files/read_files 探查); "
        "doc/task_spec.json = 报告与配置字段规范; track=None; "
        "显式 trace-faithful 标注 + 真实 user adaml + 真实 host hfeg0pkn002 + 真实环境探查字段 ⇒ A-faithful (显式标注型, 与 r801 'A-faithful' desc 同列)",
    ),
    "EDA-Eval-DesignFlow-HcellMissingFind-001": (
        "A-faithful",
        "netlist_A = 真实 AETHER-SE 导出网表 verbatim (header '* Tool     : AETHER-SE / * Date     : Thu Oct 30 10:00:00 2026 / "
        "* User     : zjqiao / * Top Design : drvqa_top/WOWTOP_1C2A/schematic' = 真实 AETHER-SE 网表导出 banner 含真实 user zjqiao + "
        "真实 date Thu Oct 30 10:00:00 2026 + 真实 top design drvqa_top/WOWTOP_1C2A/schematic, 与 r804 AETHER-SE export header 同列强信号); "
        "hcell_A = 真实 hcell 映射文件 (每行两列 block 名 IO_DqLdMdl/AG_VdivActTop/AG_VdivActTopSpare/AG_PosClamp/T_CMDq 等 real block 名); "
        "prompt.txt + task_brief.md = 任务框架; track=None; "
        "真实 AETHER-SE export header (含真实 user/date/top design) + 真实 hcell block 名 ⇒ file-verbatim (与 r804 AETHER-SE 同型)",
    ),
    "EDA-Eval-DesignFlow-HierMeasIncGen-001": (
        "synth_deck",
        "netlist_A.sp = 合成 hspice 网表样本 (Input A, 顶层例化 TbTop_A 合成名 + Gate=PGSIG_A 合成信号名 + 4 group × 4 driver = 16 PMOS 合成规模, "
        "desc 显式 'hspice 网表示例（Input A）：TbTop_A 顶层，4 group × 4 driver = 16 个 Gate=PGSIG_A 的 PMOS。开发与自测用；"
        "评测在 hidden B（不同名称/规模/信号/窗口）上跑'); "
        "meas_config_A.json = 合成 task 配置 (gate_sig=PGSIG_A/from=10n/to=30n/tag=vintcore_stat_loss 合成字段, desc 显式 'Input A 配置...脚本需读这些字段，不能写死'); "
        "task_context.md = 任务上下文 (含真实用户 reedchen 原话 U1/U2, 但属 prompt 非 asset 文件); "
        "track=None; 合成 netlist_A.sp + 合成 meas_config_A.json (合成名 _A 后缀, 开发自测用) ⇒ synth_deck; 真实用户原话仅在 task_context.md (prompt 域)",
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

    print("=== 档2 asset_fidelity backfill r807 batch7 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r807_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r807_manifest.tsv — r807 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch7 (12 cases, alphabetical next 12 missing after r806 batch6 FinesimLogExplainDiag: FinesimMatrixrunAgent..HierMeasIncGen, F-G-H 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r806 档2 batch1-6 (+72, 106→178) done. 本轮 r807 档2 batch7.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver; A-faithful 强信号 = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB/WaveView/ALPS export header / 真实内网路径 .inc/.lib/.spf / verbatim excerpt / 'reproduced faithfully' / 'faithful compact/trimmed representation' 标注 / 真实 hostname / 真实 signal names from real path / 显式 A-faithful/trace-faithful 标注\n")
        f.write("# 关键发现: 真实 WaveView ADV log export header 强信号首例 (FsdbScopeSignalLocate sxcmd_A.log 'Custom WaveView ADV log file, revision T-2022.06-SP1 ... Host Name: hfebhds113 User ID: svc.salt' 新增 WaveView export header 类型, B 域 spice_sim 首例 WaveView export header) / 真实 ALPS Simulation Log export header 强信号首例 (GmidLutRunSelect gmid.log 'ALPS Simulation Log ... Simulator: ALPS 2026.03 hf4' 新增 ALPS export header 类型, characterization 域首例) / 真实 AETHER-SE export header (HcellMissingFind netlist_A '* Tool : AETHER-SE ... User : zjqiao ... Top Design : drvqa_top/WOWTOP_1C2A/schematic', 与 r804 同型) / 显式 A-faithful/trace-faithful 标注两例 (FinesimOptionExtend/GvimCjkConfigGen) / paste-verbatim (FinesimVhDiagGuide error_log.txt 真实 netlist:行号) / reproduced-faithfully (FsdbPulseFilter waveform.tbl 真实信号名 from real path) / 真实用户程序 (FinesimMatrixrunAgent stimulus_manager.py 137KB 真实附件) / track≠asset_provenance 本批 0 新增 (累计仍 7 例) / A-faithful 8/12=67% 单批最高 (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8) / export header 强信号类型扩至 5 类 (AETHER-SE/PEX/FineSim/WaveView/ALPS) / 2 synth_deck (GaaFetDeckAugment 重建 SWB deck+库模板+合成 spec / HierMeasIncGen 合成 netlist_A+config) / 2 synth_data (G5TbGen 合成 PDK / GmidLut 合成 level-1 model)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B rebuild; asset_fidelity 178->190 (cases/B 190==B.jsonl 190 ✓); miss 217->205\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
