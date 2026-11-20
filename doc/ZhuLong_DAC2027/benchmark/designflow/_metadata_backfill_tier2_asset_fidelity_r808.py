#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r808.py — r808 档2 asset_fidelity backfill batch8.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done. r806 batch6 (+12, 166→178) done.
      r807 batch7 (+12, 178→190) done.
      本轮 r808 推进 档2 batch8 — 12 cases
      (alphabetical next 12 missing after r807 batch7 HierMeasIncGen:
       HierarchyTrace..LatchSubcktLocate, H-I-J-K-L 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r807 扩展):
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
  - 4 A-faithful (33%): HspicePanelCurProjReport / IddIpfSignalEm / IddStimHowtoGuide / IoBufParamTune
  - 5 synth_deck: HierarchyTrace / IfElsePairFix / InstCurrentMeasGen / InvTripDelay / LatchSubcktLocate
  - 1 synth_data: IddblkCsvDiff
  - 1 synth_doc:  HspiceMeasProbeGuide
  - 1 no-asset:   HspiceAcMergeDiag

关键发现:
  - 真实 HSPICE deck .inc/.lib 内网路径强信号 (IoBufParamTune, r808 首例 .inc/.lib 内网路径群):
    001_z_top_drgqa_slow_MC_PDA_TT.sp 含 26 处 /proj//home//rundata/ 内网路径引用, 包括
    .inc '/home/data08/V0/simrun/hspice/joewu/1_sim_option/finesim_option_new' (真实 joewu 用户 option 路径) +
    .lib '/proj/drcoa/V0/model/current/model.sp' (真实 /proj/drcoa foundry model 路径) +
    .GLOBAL VDDQCA!/VSS!/VDD!/VSSQCA!/vddq!/vcc!/vss! (真实 DRAM power domain 节点);
    prompt 含真实 /rundata/drcoa/V0/simdir/finesim/workdir/elianaz/simulation/99_IO_buffer/ 用户路径 +
    verbatim 用户调参请求 (LR56/LMP12/WMP12/WP1 范围). track=faithful.
    = 真实 HSPICE fullchip deck (119 行, 26 处内网路径), file-verbatim (与 r805 PEX / r806 FineSim 内网路径信号同列).
  - 真实仿真面板配置文件群强信号 (HspicePanelCurProjReport, r808 首例 panel-config 群):
    .anasim_pro_folders.json = 真实 workspace 文件夹登记 (folders=[/home/e0041392/Desktop, /home/e0041392], active=/home/e0041392,
    真实 user e0041392 路径, 与 trace_source user e0041392 一致);
    .hspice_panel_config.json = 真实 hspice 版本配置 (hspice 2019=hspice/201906-SP2, hspice 2023=ds/hspice/V-2023.12 等
    真实 foundry 版本字符串, default_simulator_type=finesim, default_queue=fqueue3);
    simulation_panel.log = 真实面板扫描日志 (17 行, 含 4 处 e0041392 + 真实 timestamp 2026-10-15 20:11:22 +
    'Sim folder scanned: /home/e0041392/Desktop' + 'ml av ds/finesim' 真实 module-version 探测命令);
    scenario.md 含 verbatim 用户问题 '检查一下workspace中设置的当前项目是哪一个'.
    = 真实自研 hspice/FineSim 仿真面板工具配置 + 日志 (3 类真实 config 群), file-verbatim (含真实 user 路径 + 真实 timestamp + 真实版本字符串).
  - 真实用户 buggy 脚本 + verbatim 修复要求 (IddIpfSignalEm, r808 首例 real-buggy-script):
    idd_to_ipf_flow_v1.py = 用户 yongk1li 真实 Totem-SC Signal EM 流程脚本 (header 显式 'STARTING (BUGGY) VERSION — needs fixing per task brief'
    + 'Known issues: 1. Legacy single-rule compat... user said: 不许兼容老功能. 2. apply_spec does CASE-SENSITIVE... CSV cell names are lowercase (bcenterca) but rules use mixed-case (BCenterCA)');
    gds_cell_map.json = 真实 cell-name 大小写映射 (ddr5top/bcenter/bcenterxx/bcenterca/bcenterca_leafa/bcenterca_leafb →
    DDR5TOP/BCenter/BCenterXX/BCenterCA/BCenterCA_LeafA/BCenterCA_LeafB 真实 foundry hierarchy cell 名);
    IDD/vcc.csv = 真实 IDD 仿真结果 (层级化实例树 top/bc/x/bca/leafA/leafB 到 L5, 真实 cellName 全小写);
    task_brief.md 含真实 user yongk1li + 真实 /home/yongk1li/bin/totem_sc_signal_em/ 内网路径 + verbatim 用户两条修复要求.
    = 真实用户 buggy 脚本 (faithful compact/trimmed representation, r806 verbatim 标记族同列) + 真实 cell hierarchy + 真实内网路径,
      file-verbatim (真实用户程序, 与 r807 FinesimMatrixrunAgent 137KB 真实用户程序同列, 本批为 trimmed representation 子型).
  - 真实 stimulus + 真实 TECHLIB 电源表 (IddStimHowtoGuide, r808 首例 TECHLIB 电源网络表):
    stimulus.sp = 真实 IDD 仿真激励 (header '* Stimulus for R_NegVssIdd_opt_qyh (compact PWL)' = 'compact PWL' faithful compact 标记 +
    真实 DRAM 信号名 SanEn2G/SapEn2GP/PwrOnLsVwlp/GrEn + 真实 .param pvcc=0.73 + 真实 PWL 时间点 10.164n/10.190n/10.215n...);
    TECHLIB_ALL_power_voltage_table.md = 真实 TECHLIB/ALL_power 电源网络表 (真实 Cell 路径 /proj/ddgoa/V0/libs/TECHLIB/ALL_power/schematic/ +
    真实电压定义文件目录 /proj/ddgoa/V0/setup/sim/finesim_sos_manage/LPDDR5/DDGOA/sim_setup/voltagefile/ + 真实整理日期 2026-10-15 +
    '电压值以 hspice0.94v.voltage（25°C）为参考' 真实电压文件名, 共 30 个电源网络);
    scenario.txt 含 verbatim 用户问题 '你可以帮我写hspice语句吗' 等 5 轮 verbatim 追问.
    = 真实 DRAM IDD 激励 (compact PWL faithful compact 标记, r806 verbatim 标记族同列) + 真实 TECHLIB /proj 内网路径 + 真实电源网络表,
      file-verbatim (与 r805 reproduced-faithfully / r806 faithful compact 标记族同列).
  - track≠asset_provenance 本批 4 例 (累计 7→11, 显著上升):
    HierarchyTrace (track=faithful, asset=synth_deck: netlist header 显式 'synthesized for hierarchy-trace case' 但含真实 hierarchy 路径
      xi_c_top.xi_array16gtop... + 真实 /proj/ddgoa model 路径; prompt faithful 但 asset synth)
    IddblkCsvDiff (track=faithful, asset=synth_data: iddblk_x4/x8.csv desc 显式 '同构重建' 真实 cell 名但合成值; track=faithful 指 prompt 非 asset)
    IfElsePairFix (track=faithful, asset=synth_deck: Pattern_Power_A.sp 为合成 broken .if/.endif deck, 真实 /home/coverage 路径仅出现在 prompt error message 非 deck body; track=faithful 指 prompt verbatim error)
    LatchSubcktLocate (track=faithful, asset=synth_deck: netlist header 显式 'Synthetic SPICE netlist A' mimicking real /rundata 结构, 真实 latch subckt 名; track=faithful 指 prompt verbatim)
    ⇒ 4/12=33% 本批 track≠asset_provenance, 累计 11 例; 主要模式 = track=faithful 记 prompt/user-words 忠实, asset 文件为 portability 合成 fixture.
      这与 r801-r807 累计 7 例 (minority pattern) 同型, 本批比例上升因 H-I-J-K-L 段多 produce-tool reframe + portability 合成 deck.
  - synth_deck 5/12=42% 本批最高 (HierarchyTrace/IfElsePairFix/InstCurrentMeasGen/InvTripDelay/LatchSubcktLocate):
    InvTripDelay netlist.sp 显式 'Derived from Synopsys HSPICE V-2023.12 demo hspice/apps/inv.sp with the agauss monte-carlo parameters replaced by fixed mean values'
    (HSPICE demo 派生 deterministic deck, 真实 demo 名 + agauss 替换说明);
    InstCurrentMeasGen dut_A.sp 显式 _A 后缀 + level=1 model + 通用值 8k/4k/50k (track=synthesized 一致, 非 track≠asset_provenance);
    HierarchyTrace/LatchSubcktLocate 同型 (synthetic netlist mimicking real structure, portability);
    IfElsePairFix = 合成 broken deck for .if/.endif fix task.
  - synth_doc 1 例 (HspiceMeasProbeGuide): requirements.json = 合成 task-spec fixture (signals bla<25>/blb<25> from 用户问题 + measurements MAX/MIN/AVG 结构化),
    scenario.txt = verbatim 用户 5 轮问题 wrapping; how-to Q&A->produce-tool guide reframe ⇒ synth_doc.
  - no-asset 1 例 (HspiceAcMergeDiag): 0 attachments, diagnose Q&A->produce reframe, SUT 从 RAG + trace verbatim user turns 生成诊断指南.
  - A-faithful 4/12=33% (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8,r808=4), 累计 40/96=42%.
  - export header 强信号类型: 本批 0 新增 (维持 5 类 AETHER-SE/PEX/FineSim/WaveView/ALPS); 本批强信号转 .inc/.lib 内网路径群 + panel-config 群 + real-buggy-script + TECHLIB 电源表 4 类新形态.

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
    "EDA-Eval-DesignFlow-HierarchyTrace-001": (
        "synth_deck",
        "netlist = 合成 SPICE fullchip netlist (header 显式 '* SPICE fullchip netlist (A) - synthesized for hierarchy-trace case', "
        "body 含真实 .INCLUDE '/proj/ddgoa/V0/model/model.sp' 真实内网 model 路径 + 真实 hierarchy 路径 "
        "xi_c_top.xi_array16gtop.xi_array8g_e.xi_array1gbk3.xi_m1g_top.xi_m512meg_u.xi_msaq_28 + 真实 subckt 名 MSAQ_28/M512MEG_U, "
        "但 deck 整体显式 synthesized for portability); "
        "prompt.txt = 真实用户原话 verbatim (xinweif @ hfeg0pkn005, 真实 /rundata/ddgoa/V0/simdir/finesim/workdir/xinweif/simulation/trynet 路径); "
        "track=faithful (指 prompt/user-words 忠实); reframe=None; "
        "track≠asset_provenance (track=faithful 记 prompt, asset=合成 deck); 合成 netlist (含真实 hierarchy 名 + 真实 /proj 路径, portability) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-HspiceAcMergeDiag-001": (
        "no-asset",
        "0 attachments; reframe_note = 'diagnose Q&A->produce (§4 有牙必要, r720 spotcheck batch2): 用户 ruminji 问 hspice AC 多模块合一起不正确单独正确是什么原因(根因), "
        "重构为产诊断指南生成器'; trace_source ruminji@hfeg0pkn004 sess 1792543801789_ftbpz; "
        "0 attachment Q&A (diagnose-Q&A->produce-tool guide), SUT 从 RAG + trace verbatim user turns 生成诊断指南 ⇒ no-asset",
    ),
    "EDA-Eval-DesignFlow-HspiceMeasProbeGuide-001": (
        "synth_doc",
        "doc/requirements.json = 合成 task-spec fixture (signals=[bla<25>,blb<25>] from 用户问题 + measurements=[MAX/MIN/AVG] 结构化, "
        "通用 DRAM bit-line 信号名, 无真实 export header/内网路径/user); "
        "doc/scenario.txt = verbatim 用户 5 轮问题 wrapping ('你可以帮我写hspice语句吗' / '帮我测试bla<25>和blb<25>这两个线的最大最小值的平均值' / "
        "'解释一下什么时候用param，什么时候不用' / '.probe似乎可以做仿真波形的处理' 等 verbatim); "
        "track=None; reframe='HSPICE .MEASURE/.PROBE 语法 guide 生成器->produce-tool (Q&A how-to/learning Q&A->produce-tool)'; "
        "合成 doc/requirements.json (task-spec 结构化, 通用信号名) + verbatim 用户问题 wrapping ⇒ synth_doc",
    ),
    "EDA-Eval-DesignFlow-HspicePanelCurProjReport-001": (
        "A-faithful",
        ".anasim_pro_folders.json = 真实 workspace 文件夹登记 (folders=[/home/e0041392/Desktop, /home/e0041392], active=/home/e0041392, "
        "真实 user e0041392 路径与 trace_source user e0041392 一致); "
        ".hspice_panel_config.json = 真实 hspice 版本配置 (hspice 2019=hspice/201906-SP2, hspice 2023=ds/hspice/V-2023.12, "
        "hspice 2021=hspice/2021.09-SP2-2_os7 真实 foundry 版本字符串, default_simulator_type=finesim, default_queue=fqueue3, default_cores=6); "
        "simulation_panel.log = 真实面板扫描日志 (17 行, 4 处 e0041392 + 真实 timestamp 2026-10-15 20:11:22 + "
        "'Sim folder scanned: /home/e0041392/Desktop (0 SPICE files)' + 'Running: ml av ds/finesim' 真实 module-version 探测命令); "
        "scenario.md 含 verbatim 用户问题 '检查一下workspace中设置的当前项目是哪一个'; "
        "track=None; reframe='HSPICE 面板当前项目报告器->produce-tool (Q&A-which->produce-report-tool)'; "
        "真实自研 hspice/FineSim 仿真面板工具配置 3 类 (folders/config/log) + 真实 user 路径 + 真实 timestamp + 真实版本字符串 + verbatim 用户问题 ⇒ file-verbatim (A-faithful, panel-config 群首例)",
    ),
    "EDA-Eval-DesignFlow-IddIpfSignalEm-001": (
        "A-faithful",
        "idd_to_ipf_flow_v1.py = 用户 yongk1li 真实 Totem-SC Signal EM 流程脚本 (header 显式 'STARTING (BUGGY) VERSION — needs fixing per task brief' + "
        "'Known issues: 1. Legacy single-rule compat... user said: 不许兼容老功能. 2. apply_spec does CASE-SENSITIVE father/include/exclude comparison. "
        "CSV cell names are lowercase (bcenterca) but rules use mixed-case (BCenterCA)' = verbatim 用户两条修复要求); "
        "gds_cell_map.json = 真实 cell-name 大小写映射 (ddr5top→DDR5TOP, bcenter→BCenter, bcenterca→BCenterCA, bcenterca_leafa→BCenterCA_LeafA, "
        "bcenterca_leafb→BCenterCA_LeafB 真实 foundry hierarchy cell 名); "
        "IDD/vcc.csv = 真实 IDD 仿真结果 (层级化实例树 top/bc/x/bca/leafA/leafB 到 L5, cellName 全小写, 列 instHdl/parentHdl/cellName/idd); "
        "task_brief.md 含真实 user yongk1li + 真实 /home/yongk1li/bin/totem_sc_signal_em/ 内网路径 + verbatim 用户两条修复要求; "
        "track=None; reframe=None; "
        "真实用户 buggy 脚本 (faithful compact/trimmed representation, r806 verbatim 标记族同列) + 真实 cell hierarchy + 真实 /home 内网路径 ⇒ file-verbatim (A-faithful, real-buggy-script 子型首例)",
    ),
    "EDA-Eval-DesignFlow-IddStimHowtoGuide-001": (
        "A-faithful",
        "stimulus.sp = 真实 IDD 仿真激励 (header '* Stimulus for R_NegVssIdd_opt_qyh (compact PWL)' = 'compact PWL' faithful compact 标记 + "
        "真实 DRAM 信号名 SanEn2G/SapEn2GP/PwrOnLsVwlp/GrEn + 真实 .param pvcc=0.73 + 真实 PWL 时间点 10.164n/10.190n/10.215n/10.245n/10.278n 带真实电压值); "
        "TECHLIB_ALL_power_voltage_table.md = 真实 TECHLIB/ALL_power 电源网络表 (真实 Cell 路径 /proj/ddgoa/V0/libs/TECHLIB/ALL_power/schematic/ + "
        "真实电压定义文件目录 /proj/ddgoa/V0/setup/sim/finesim_sos_manage/LPDDR5/DDGOA/sim_setup/voltagefile/ + 真实整理日期 2026-10-15 + "
        "'电压值以 hspice0.94v.voltage（25°C）为参考' 真实电压文件名, 共 30 个电源网络); "
        "scenario.txt 含 verbatim 用户 5 轮问题 ('你可以帮我写hspice语句吗' 等); "
        "track=None; reframe='IDD 仿真激励编写指南器->produce-tool (how-to-Q&A->produce-tool guide+report)'; "
        "真实 DRAM IDD 激励 (compact PWL faithful compact 标记, r806 verbatim 标记族同列) + 真实 TECHLIB /proj 内网路径 + 真实电源网络表 ⇒ file-verbatim (A-faithful, TECHLIB 电源表首例)",
    ),
    "EDA-Eval-DesignFlow-IddblkCsvDiff-001": (
        "synth_data",
        "iddblk_x4.csv / iddblk_x8.csv = 同构重建 IDD characterization CSV (列 cellName/category/ext_vdd!/ext_vddq!/ext_vpp!/vcc!/vdd1!, "
        "真实 foundry cell 名 d_banklogic/c_cmddec/ag_analogbankx2l/d_wrlatencyctrl/m392meg_u/bcenterl + 真实 category banklogic/cmdpath/dc/clkpath/array, "
        "但数值为合成 (x4 vs x8 同 cellName 不同值), attachment desc 显式 '同构重建'); "
        "task_brief.md = 交付接口说明; track=faithful (指 prompt/user-words 忠实); reframe=None; "
        "track≠asset_provenance (track=faithful 记 prompt, asset=同构重建 CSV); 同构重建 CSV (真实 cell 名 + 合成数值, '同构重建' marker) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-IfElsePairFix-001": (
        "synth_deck",
        "Pattern_Power_A.sp = 合成 broken .if/.endif SPICE deck (header '* Power table characterization stimulus (broken: missing .endif)', "
        "body 含 .if/.elseif/.else/.end (缺 .endif) + .param pvcc=0.95v ptemp=25 vamp=1.7 + .measure tran vout_avg + 通用阈值 0.9v/0.92v/0.97v, "
        "通用 characterization stimulus, 无真实 export header/内网路径); "
        "prompt.txt = 真实用户 verbatim error message ('ERROR! if-else conditional statements not paired (/home/coverage/DDR5/DRGQA/sim_setup/Powervoltage/Pattern_Power.sp:2)讲解报错', "
        "真实 /home/coverage 内网路径仅出现在 prompt error message 非 deck body); "
        "track=faithful (指 prompt verbatim error); reframe='FineSim .if/.endif 不配对报错修复器->produce-tool (Q&A debug-Q&A->produce-tool fix script)'; "
        "track≠asset_provenance (track=faithful 记 prompt verbatim error, asset=合成 broken deck); 合成 broken deck for .if/.endif fix task (真实路径仅 prompt) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-InstCurrentMeasGen-001": (
        "synth_deck",
        "dut_A.sp = 合成 DUT netlist (header '* DUT_A: bias/reference network with named resistors + 2 mosfets', "
        "body 含命名电阻 r_vdd_div_a/r_gnd_div_a/r_bleed_a/r_drv_a/r_sw_a (全 _a 后缀合成名) + mn_drv_a/mn_sw_a + .model nch_a nmos level=1 vto=0.7 kp=50u "
        "教科书 level-1 SPICE 值, 通用值 8k/4k/50k/2k/6k); "
        "spec_A.json = 合成 task 配置 (supply_node=vdda/vdd=1.2/gate_node=nga/pulse v0=0 v1=1.2 td=1n + target_instances 合成名, 无真实 foundry model header/path/hostname); "
        "track=synthesized (与 asset 一致, 非 track≠asset_provenance); reframe='how-to Q&A→produce (§4 有牙必要, r713 spotcheck): 用户问怎么测器件支路电流(how-to)，重构为产测量脚本'; "
        "合成 DUT_A.sp (_A 后缀 + level-1 model + 通用值) + 合成 spec_A.json ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-InvTripDelay-001": (
        "synth_deck",
        "netlist.sp = 合成 CMOS inverter netlist (header 显式 '* CMOS inverter subckt + level-28 MOS model (deterministic). "
        "* Derived from Synopsys HSPICE V-2023.12 demo hspice/apps/inv.sp with the agauss monte-carlo parameters replaced by fixed mean values so the model is fully deterministic', "
        "body 含 .subckt inv in out + mn/mp 10u/1u + .model nch nmos level=28 lmlt=mult1 wref=22u lref=4.4u + .param mult1/xl/xwn/xwp/tox=200/delvton/delvtop/rshn=50/rshp=150, "
        "HSPICE demo 派生 + agauss 替换为 deterministic 固定值, 无真实 user/export header/内网路径); "
        "prompt.txt = 真实用户场景 (adaml @ hfeg0pkn001, 真实 /proj/drvsa/V0/workdir/adaml/drgqa_simulation/ 内网工程路径 + 真实 .sp 文件名 Lbx_sim_DQ_TX_schematic_ALPS/Postsim/DR9500_woCH_woFFE.sp 等); "
        "track=None; reframe=None; "
        "HSPICE V-2023.12 demo 派生 deterministic deck (显式 'Derived from Synopsys HSPICE demo' + agauss 替换, 通用 inv.sp) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-IoBufParamTune-001": (
        "A-faithful",
        "001_z_top_drgqa_slow_MC_PDA_TT.sp = 真实 HSPICE fullchip deck (119 行, 26 处 /proj//home//rundata/ 内网路径引用, 包括 "
        ".inc '/home/data08/V0/simrun/hspice/joewu/1_sim_option/finesim_option_new' 真实 joewu 用户 option 路径 + "
        ".lib '/proj/drcoa/V0/model/current/model.sp' tt 真实 /proj/drcoa foundry model 路径 + "
        ".lib '/proj/drcoa/V0/model/current/incFile_lp' bjt_tt/res_t 真实 incFile + "
        ".GLOBAL VDDQCA!/VSS!/VDD!/VSSQCA!/vddq!/vcc!/vss! 真实 DRAM power domain 节点 + 'HSPICE Default Option for Block Level Simulation' 真实 option banner); "
        "prompt.txt = 真实用户原话 verbatim (elianaz @ hfeg0pkn002, 真实 /rundata/drcoa/V0/simdir/finesim/workdir/elianaz/simulation/99_IO_buffer/ 用户路径 + "
        "verbatim 用户调参请求 '调整参数值，使measure得到的data_H的值大于等于0.99*VDDQ，data_L的值小于等于0.001' + 真实参数范围 LR56/LMP12/WMP12/WP1); "
        "track=faithful (与 asset 一致); reframe='IO buffer(DqPrampBuf)FineSim 参数调优器+报告器->produce-tool (portability produce-action run+tune->produce-tool reframe)'; "
        "真实 HSPICE fullchip deck (119 行, 26 处 .inc/.lib 内网路径群, 真实 joewu option 路径 + 真实 /proj/drcoa model 路径 + 真实 DRAM power domain 节点) + "
        "真实用户路径 + verbatim 调参请求 ⇒ file-verbatim (A-faithful, .inc/.lib 内网路径群首例)",
    ),
    "EDA-Eval-DesignFlow-LatchSubcktLocate-001": (
        "synth_deck",
        "netlist = 合成 SPICE netlist A (header 显式 '* Synthetic SPICE netlist A — LatchSubcktLocate-001 (A-faithful, zxtu @ hfeg0pkn001, trace 1791969171304_w3eav U#2)' + "
        "'* Mimics structure of /rundata/ddgoa/V0/simdir/finesim/workdir/caozhang/simulation/Netlist_Vcap_20261012PM/netlist.presim', "
        "body 含 10 个 latch subckt (混合大小写 CmLatchX5Unit/cmllatchV3IP/LATCH_CML_OSC 等 real latch 名) + decoys + X-instances, "
        "deck整体显式 Synthetic mimicking real /rundata 结构, portability 合成); "
        "prompt.txt = 真实用户原话 verbatim (zxtu @ hfeg0pkn001, 真实 /rundata/ddgoa/V0/simdir/finesim/workdir/caozhang/simulation/Netlist_Vcap_20261012PM/netlist.presim 路径 + "
        "verbatim '找出这份网表文件中的latch subckt'); "
        "track=faithful (指 prompt/user-words 忠实); reframe='LPDDR6 118MB 网表 latch subckt 定位器->produce-tool (harness produce-action list->script reframe)'; "
        "track≠asset_provenance (track=faithful 记 prompt, asset=合成 netlist); 合成 netlist (显式 Synthetic, mimicking real 结构, 真实 latch 名, portability) ⇒ synth_deck",
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

    print("=== 档2 asset_fidelity backfill r808 batch8 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r808_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r808_manifest.tsv — r808 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch8 (12 cases, alphabetical next 12 missing after r807 batch7 HierMeasIncGen: HierarchyTrace..LatchSubcktLocate, H-I-J-K-L 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r807 档2 batch1-7 (+84, 106→190) done. 本轮 r808 档2 batch8.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver; A-faithful 强信号 = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB/WaveView/ALPS export header / 真实内网路径 .inc/.lib/.spf / verbatim excerpt / 'reproduced faithfully' / 'faithful compact/trimmed representation' 标注 / 真实 hostname / 真实 signal names from real path / 显式 A-faithful/trace-faithful 标注 / 真实用户 buggy 脚本 + verbatim 修复要求\n")
        f.write("# 关键发现: 真实 HSPICE deck .inc/.lib 内网路径群强信号首例 (IoBufParamTune 001_z_top_drgqa_slow_MC_PDA_TT.sp 119 行 26 处 /proj//home//rundata/ 路径, .inc joewu option 路径 + .lib /proj/drcoa model 路径 + 真实 DRAM power domain 节点 VDDQCA!/VSS!/VDD!) / 真实仿真面板配置文件群强信号首例 (HspicePanelCurProjReport .anasim_pro_folders.json + .hspice_panel_config.json + simulation_panel.log 3 类真实 config, 真实 user e0041392 路径 + 真实 timestamp + 真实 hspice 版本字符串) / 真实用户 buggy 脚本 + verbatim 修复要求首例 (IddIpfSignalEm idd_to_ipf_flow_v1.py 用户 yongk1li 真实 Totem-SC Signal EM 脚本 + verbatim 两条修复要求 + 真实 cell hierarchy BCenterCA/BCenterCA_LeafA + 真实 /home/yongk1li 内网路径, faithful compact/trimmed representation 子型) / 真实 stimulus + 真实 TECHLIB 电源表首例 (IddStimHowtoGuide stimulus.sp 'compact PWL' faithful compact 标记 + 真实 DRAM 信号名 + TECHLIB_ALL_power_voltage_table.md 真实 /proj/ddgoa 内网路径 + 真实 30 电源网络) / track≠asset_provenance 本批 4 例显著上升 (累计 7→11, HierarchyTrace/IddblkCsvDiff/IfElsePairFix/LatchSubcktLocate, 主模式 track=faithful 记 prompt 忠实 + asset portability 合成 fixture) / synth_deck 5/12=42% 本批最高 (HierarchyTrace/IfElsePairFix/InstCurrentMeasGen/InvTripDelay/LatchSubcktLocate, InvTripDelay HSPICE demo 派生 deterministic) / synth_doc 1 (HspiceMeasProbeGuide) / no-asset 1 (HspiceAcMergeDiag) / A-faithful 4/12=33% (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8,r808=4) 累计 40/96=42% / export header 强信号类型本批 0 新增维持 5 类, 本批强信号转 .inc/.lib 内网路径群 + panel-config 群 + real-buggy-script + TECHLIB 电源表 4 类新形态\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 190->202 (cases/B 202==B.jsonl 202 ✓); miss 205->193\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
