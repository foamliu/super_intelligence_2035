#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r823.py — r823 档2 asset_fidelity backfill batch23.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r822 档2 batch1-22 (+264, 106→370) done. 本轮 r823 推进 档2 batch23 — 12 cases
      (alphabetical next 12 missing after r822 batch22 VcoKvcoChar:
       VecgenProbeEmptyDiag..WriteDqPsdMappingExtract, V→W 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r822 扩展): 见 r819 script header.

本批 12 case 判定:
  - 4 A-faithful (33%) — V→W 段 real-trace 资产 (r822 累计 114/264=43.2%; 本批 4/12=33%,
    累计 118/276=42.8%). 4 例:
      * VrefStepMeasure (real fscript dsignal 导出 .tbl 文本表 waveform_A.tbl 2451 点 27 档
        上升 ~5.47mV/档; desc 显式 'fscript 导出的真实 Vref_DQ 阶梯波文本表'; characterization
        域; 真实 fscript text export)
      * WaveViewPanel (real openWave.pl 作者 header 'Billy.Luo / Billy.Luo@cxmt.com / Last
        modified: 2021-12-09 14:31' + real openSignal.tcl 含 real /home/rongjiez/jira_dev/
        mpqa/mp_2/ModelQA_0924170807/idvd/result/ntn_w2.400u_l0.190u_nf1#N.sw0 路径 +
        real wv_set_size WV1.PANEL{i}:1.HEIGHT 150 WaveView tcl + real waveDir_A_listing
        scan 路径; track=spice_char)
      * WriteDqPsdMappingExtract (real DDR6 vecgen 4 .sv 代码节选 A_ddr6_specdef/interface/
        test/genvector.sv; prompt 显式 '真实代码节选'; track=faithful; verbatim user prompt
        tongfanl@hfhds201 '/proj/dscqa/V0/... 帮我整理一个表格...DQSEL_LH...1P12/1P6/2P6/2P3')
      * VtscMcDeckExplain (real HSPICE MC deck doc/mc_iload.sp 含 '* User: junweix /
        * Date: 2026-10-23' 作者日期 header + .inc './Setting.sp' + .meas vload avg v(vtsc!)
        from 2u to 10u + .dcmatch v(vtsc!) THRESHOLD=1 + mis_flag=1; prompt 显式 'SPICE 行来自
        真实 trace'; faithful compact reconstruction preserving real SPICE lines)
  - 5 synth_deck: VihTripTune (synth params_A.json 含 level-1 MOS 模型参数 kp_n/kp_p/vto_n/
    lambda/gamma/phi/nsub + baseline_widths, portable HSPICE testbench reconstruction;
    track=faithful verbatim prompt 但 asset synth) / VirtuosoSfeLangDiag (自包含合成 input.scs/
    netlist/run.log/netlister.log 保留真实 SFE-868/SFE-1802 错误结构; reframe_note 显式
    'asset_fidelity=synth') / VsimFinesimAdapt (忠实合成 vsim_a.pl ~150 行 vsim-like Perl,
    header 自声明 'A-faithful synthesized asset, derived from mike @ hfeg0plg49 trace 1s79t';
    lpddr4/lpddr5 legacy arch 块 + DBRMA/V0 默认) / VtscRefR5Logic (synth vtsc_ref_netlist_A.sp
    sim-schematic netlist 含 stdcell black-box definitions nand2Lx1 等, 'Visible input A' marker)
    / WlvlShmooLoopAnalyze (自包含合成 shmoo SystemVerilog task 资产保留 real DDR5 write-leveling
    loop 结构; reframe_note 显式 '自包含合成 shmoo C 代码片段资产'; track=faithful verbatim prompt 但
    asset synth)
  - 3 synth_data: VecgenProbeEmptyDiag (重建 terminal-log fixtures A_vecgen_log/ 含 vecgen.rpt
    real WTM corner 名 + vsim_A 'extracted from trace 1791457291368_k7hc6' + A_only_vecgen_marker
    anti-leak marker + 3 TT/FF/SS corner 子目录; reframe driver Q&A/diag→produce-tool 无 runnable
    artifact ⇒ 构建 structured log fixtures; track=faithful 但 asset 重建) / VerdiFsdbLoadDiagnose
    (重建 env-config/error-log fixtures verdi_error_log.txt/bashrc.txt/hf_tool_version.txt/
    modulefile.txt/makefile.txt 保留 real Verdi FSDB *Verdi* banner + real /apps/synopsys/verdi/
    V-2023.12-SP2-3 路径 + synthesized '===== [ERROR-N] =====' 分段 header; reframe driver Q&A
    env-config/debug-Q&A→produce-tool) / VthOverrideHowtoGuide (curated input_manifest.json 构造
    仿真场景 surface {simulator/device_class/vth_param_name/instance_style/model_level/lib_filename/
    lib_reference/corner}; Q&A how-to→produce-tool guide generator reframe; verbatim prompt 在
    scenario.txt 但 asset=curated manifest)

关键发现:
  - A-faithful 33% (4/12) — V→W 段 real-trace 资产 (r822 累计 114/264=43.2%; 本批 4/12=33%,
    累计 118/276=42.8%). 本批 A-faithful 比率略低于均值 (V→W 段 synth_deck 密集 5/12=42%).
  - 新信号族 4 类:
    * real Verdi FSDB dumper error log banner (VerdiFsdbLoadDiagnose '*Verdi* Loading
      libsscore_vcs202312.so / *Verdi* Cannot load libsscore_vcs202312.so from following
      VERDI_HOME or NOVAS_HOME /apps/synopsys/verdi/V-2023.12-SP2-3/bin/verdi/share/PLI/lib/
      LINUXAMD64/ / *Verdi* Failed to load FSDB dumper' + real /apps/synopsys/verdi path, 扩展
      r813 export header 强信号族至 Verdi FSDB error log 域)
    * real fscript dsignal-exported .tbl waveform (VrefStepMeasure waveform_A.tbl 2451 点
      'TIME v(vref_dq<0>)' header + real fscript dsignal text export, 新 sub-type: real fscript
      .tbl 波形文本导出, 扩展 export 族至 Synopsys fscript 文本波形导出域)
    * real WaveView tcl-generation Perl script + tcl output (WaveViewPanel openWave.pl 作者
      header 'Billy.Luo @cxmt.com 2021-12-09' + openSignal.tcl real wv_set_size/sx_open_sim_file
      WaveView tcl + real /home/rongjiez 路径, 扩展 r814 WaveView .sx 族至 tcl-generation
      script+tcl output 双型)
    * real HSPICE deck author/date header (VtscMcDeckExplain mc_iload.sp '* User: junweix /
      * Date: 2026-10-23' + * Type/Tool/Top Function/Circuit HSPICE deck 元 header, 扩展 r813
      export header 族至 HSPICE deck author/date header 域)
  - track≠asset_provenance 3 例 (累计 48→51): VecgenProbeEmptyDiag (track=faithful prompt
    verbatim U#0 但 asset synth_data 重建 log fixtures) + VihTripTune (track=faithful verbatim
    prompt 但 asset synth_deck portable params) + WlvlShmooLoopAnalyze (track=faithful verbatim
    prompt 但 asset synth_deck 自包含合成 .v).
  - synth_deck 5 例: VihTripTune (level-1 MOS params portable) + VirtuosoSfeLangDiag
    (自包含 input.scs/netlist, reframe self-declares synth) + VsimFinesimAdapt ('A-faithful
    synthesized asset' self-declaration 双语) + VtscRefR5Logic (stdcell black-box netlist) +
    WlvlShmooLoopAnalyze (自包含合成 shmoo .v, reframe self-declares synth).
  - synth_data 3 例: VecgenProbeEmptyDiag (重建 terminal-log fixtures real WTM 名) +
    VerdiFsdbLoadDiagnose (重建 env-config/error-log fixtures real Verdi banner) +
    VthOverrideHowtoGuide (curated input_manifest.json 场景 surface, Q&A how-to guide).
  - reframe_note self-declares provenance 2 例: VirtuosoSfeLangDiag (reframe 显式
    'asset_fidelity=synth') + WlvlShmooLoopAnalyze (reframe 显式 '自包含合成 ... 资产'),
    承 r819 SpTemplateOpt 'reframe_note self-declares provenance' 族.
"""

import json
import os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-VecgenProbeEmptyDiag-001": ("synth_data",
        "A_vecgen_log/ = 重建 terminal-log fixtures (vecgen.rpt 含 real WTM corner 名 "
        "WTM001_normal_check_..._2b16g_BL02_12800_TT/FF/SS_DQSELH.X2P3_12800 trace-verbatim + "
        "vsim_A Perl '# vsim - DDR6 vecgen simulation launcher (extracted from trace "
        "1791457291368_k7hc6)' + '# A_only_vecgen_marker_X1P6_12800_FF <-- A-only identifier "
        "(must NOT leak into B output)' anti-leak marker + 3 TT/FF/SS corner 子目录重建终端输出); "
        "reframe_note 'Q&A/diag->produce-tool 诊断器 reframe, 用户 tongfanl@hfhds201 原话粘贴 "
        "./runsti/gen_stimulus_ltf 三 vsim submission(TT/FF/SS) 终端输出 + d6vecgen width==X2P3 "
        "bank array must start with 2b16g warning 问诊断'; A 不可行原因=纯 Q&A/diag(粘贴日志问诊断)"
        "无 runnable artifact 无 check牙 ⇒ case 构建 structured log fixtures; track=faithful "
        "(prompt verbatim U#0 tongfanl) 但 asset 重建 ⇒ track≠asset_provenance; layer=L1; "
        "real_task_summary verbatim tongfanl U#0; 重建 terminal-log fixtures 保留 real WTM 名 + "
        "A_only anti-leak marker ⇒ synth_data (非 raw scp, 构建 structured log fixtures)"),
    "EDA-Eval-DesignFlow-VerdiFsdbLoadDiagnose-001": ("synth_data",
        "verdi_error_log.txt = 重建 Verdi FSDB error log (header '===== [ERROR-1] FSDB dumper "
        "load failure (msg 0, user paste) =====' synthesized 分段 header + real '*Verdi* "
        "WARNING ... will be deprecated in VERDI2024.09' + '*Verdi* Loading libsscore_vcs202312.so' "
        "+ '*Verdi* Cannot load libsscore_vcs202312.so from following VERDI_HOME or NOVAS_HOME "
        "/apps/synopsys/verdi/V-2023.12-SP2-3/bin/verdi/share/PLI/lib/LINUXAMD64/' + '*Verdi* "
        "Failed to load FSDB dumper' real Verdi banner + real /apps/synopsys/verdi path); "
        "bashrc.txt/hf_tool_version.txt/modulefile.txt/makefile.txt = 重建 env-config fixtures; "
        "requirements.json/scenario.txt/task_brief.md = 交付接口; reframe_note 'Q&A env-config/"
        "debug-Q&A->produce-tool diagnose+JSON reframe, 用户 dsgao@hfeg0plg89(=10.129.32.75) "
        "sess 1793189553608_5uqoi mc126, 跑 bsub -I make verdi 遇 Verdi FSDB dumper 加载失败, "
        "trace 金标准 126 msgs 4 级联根因'; track=None; layer=None; real_task_summary dsgao 4 级联 "
        "Verdi 启动失败; 重建 env-config/error-log fixtures 保留 real Verdi *Verdi* banner + real "
        "/apps/synopsys 路径 + synthesized 分段 header ⇒ synth_data (非 raw scp, 重建 env+error "
        "log fixtures; 新信号族: real Verdi FSDB dumper error log banner, 扩展 r813 export header "
        "族至 Verdi FSDB error log 域)"),
    "EDA-Eval-DesignFlow-VihTripTune-001": ("synth_deck",
        "params_A.json = synth portable HSPICE testbench 参数 (vdd 1.0/vref 0.500/kp_n 0.00012/"
        "kp_p 0.00005/vto_n 0.5/vto_p -0.5/lambda 0.05/gamma 0.4/phi 0.6/nsub 1e16 level-1 MOS "
        "模型参数 + LL/itail/idfe_values[0,-5e-7,5e-7]/ramp_v1/v2/td/tr/tf/pw/per/tran_step/"
        "tran_total + baseline_widths wn28/wn23/wp10/wp3); reframe_note 'portability produce-"
        "action->produce-tool 调优器 reframe, 用户 jasminej@hfeahpc505 原话「帮我修改网表中DfeTop6M6V2"
        "网表中MP28/23/10/3的尺寸...翻转点在vih=170上」, trace agent 写 launch_edit.run.sh 跑 exp1 但 "
        "环境反复卡(LD_PRELOAD/libstdc++)'; track=faithful (verbatim prompt jasminej) 但 asset synth "
        "⇒ track≠asset_provenance; layer=L2; real_task_summary HSPICE V-2023.12-SP1-1 DfeTop6M6V2 "
        "VIH trip-point 3 .alter DFE 抽头翻转点扫频; synth level-1 MOS params portable reconstruction "
        "⇒ synth_deck (portable HSPICE testbench 参数, 承 r813 'portable level-1 MOS model' 族)"),
    "EDA-Eval-DesignFlow-VirtuosoSfeLangDiag-001": ("synth_deck",
        "sim/input.scs + sim/netlist/analog/netlist + sim/run.log + sim/netlister.log + sim/"
        "dir_listing.json = 自包含合成 Virtuoso/finesim netlist+error log fixtures 保留真实 SFE-868/"
        "SFE-1802/SFE-1025/SFE-1703 + AMS-1245 错误结构; reframe_note 'portability+Q&A/diag->produce "
        "candidate reframe, 用户 zhililu@hfeg0plg75 用 Virtuoso ADE Maestro 跑 finesim 仿真, 问 "
        "「virtuoso 怎么用已生成的 netlist 仿真」后贴 SFE 报错, 助手定位根因=netlist 文件缺 "
        "simulator lang= 声明; A 不可行原因=真实 /proj 工程目录+finesim 环境 SUT 沙盒不可达 -> 用 "
        "自包含合成 input.scs/netlist error log 保留真实任务结构(asset_fidelity=synth)'; reframe_note "
        "显式 self-declares 'asset_fidelity=synth'; track=None; layer=L1; real_task_summary zhililu "
        "Virtuoso ADE Maestro L_tsensor_dbc.TOP_SIM finesim SFE 错误根因诊断; 自包含合成 netlist+error "
        "log fixtures, reframe self-declares synth ⇒ synth_deck (reframe_note self-declares "
        "provenance, 承 r819 SpTemplateOpt 族)"),
    "EDA-Eval-DesignFlow-VrefStepMeasure-001": ("A-faithful",
        "waveform_A.tbl = 真实 fscript dsignal 导出文本表 (header 'TIME v(vref_dq<0>)' + 2451 点 "
        "0.000n 1.031401 ... 真实 Vref_DQ 阶梯波 27 档上升 0.343→0.485V ~5.47mV/档); step_config_A."
        "json = 真实采样配置 (waveform waveform_A.tbl/start_ns 290/period_ns 150/output vref_steps."
        "json); TASK.md = 任务说明; attachments desc 显式 '可见输入 A：fscript 导出的真实 Vref_DQ 阶梯"
        "波文本表(2451 点, 27 档上升 ~5.47mV/档)，供理解与调试'; reframe_note 空 (无 reframe, A 可直 "
        "跑); track=None; layer=L2; domain=characterization; real_task_summary alenxu 'v(vref_dq<0>) "
        "vrefDQ_linerty.tr0 档位切换曲线 每档 150ns 计算步长 第一个点取 290ns' verbatim; 真实 fscript "
        "dsignal 导出 .tbl 文本波形 ⇒ A-faithful (real fscript text export; 新信号族: real fscript "
        "dsignal-exported .tbl waveform, 扩展 export 族至 Synopsys fscript 文本波形导出域; "
        "characterization 域)"),
    "EDA-Eval-DesignFlow-VsimFinesimAdapt-001": ("synth_deck",
        "vsim_a.pl = 忠实合成 vsim-like Perl 脚本 ~150 行 (header '#!/usr/bin/perl # vsim - verilog "
        "testbench build script (lpddr6_tb) # A-faithful synthesized asset, derived from mike @ "
        "hfeg0plg49 trace 1s79t' 自声明 'A-faithful synthesized asset' + lpddr4/lpddr5 legacy arch "
        "块 + 默认 DBRMA/V0 + 默认 arch lpddr4 + /proj 路径 + help 文本 + 花括号结构); task_brief.md "
        "= 交付接口 (vsim_adapt.py); reframe_note 空; track=None; layer=None; real_task_summary "
        "mike hfeg0plg49 lpddr6 vsim(Perl) TB 构建脚本适配 FineSim 67 工具调用, 本 case 用忠实合成 "
        "~150 行 vsim-like Perl 资产复现; prompt 显式 '从真实 trace 忠实合成的可见 vsim 脚本'; 忠实 "
        "合成 vsim-like Perl, self-declares 'A-faithful synthesized asset' ⇒ synth_deck (faithful "
        "compact reconstruction, 承 r813 'faithful compact representation' 族; 'A-faithful "
        "synthesized' 双语自声明)"),
    "EDA-Eval-DesignFlow-VthOverrideHowtoGuide-001": ("synth_data",
        "input_manifest.json = curated 仿真场景 manifest (simulator hspice/device_class IO Pad/"
        "vth_param_name vth0/instance_style X (subcircuit)/model_level 54/model_type nmos/"
        "lib_filename hlmc_cl022ul_io25_spice_v0p12_0d10_for_vodka_shrink0d855.lib/lib_reference "
        ".lib './v0p12/...lib' tt/corner tt); scenario.txt = verbatim 用户原话 + 场景背景; "
        "task_brief.md/requirements.json = 交付接口; reframe_note 'Q&A how-to Q&A->produce-tool "
        "guide generator reframe, 用户 jasminej@hfeg0plg52 sess 1793264956869_hxfhy mc14, U0 逐字 "
        "「访问这个lib，在.sp中如何才能重新定义阈值电压值？」, trace 金标准 14 msgs HSPICE/FineSim "
        "BSIM4(level 54) IO Pad 模型'; track=None; layer=None; real_task_summary jasminej IO Pad "
        "vth0 阈值覆盖 how-to; curated input_manifest.json 构造仿真场景 surface, Q&A how-to→produce-"
        "tool guide reframe ⇒ synth_data (curated manifest, 承 r819 SpfExtractFeasibility 'curated "
        "env_manifest.json API surface' 族; verbatim prompt 在 scenario.txt 但 asset=curated "
        "manifest)"),
    "EDA-Eval-DesignFlow-VtscMcDeckExplain-001": ("A-faithful",
        "doc/mc_iload.sp = real HSPICE MC deck (header '* Type: HSPICE Deck / * Tool: HSPICE / "
        "* Top Function: VtscAct LoadReg MC / * User: junweix / * Circuit: Vtsc Active buffer "
        "load-regulation Monte Carlo / * Date: 2026-10-23' 真实 HSPICE deck 作者日期 header + "
        ".inc './Setting.sp' + .meas vload avg v(vtsc!) from 2u to 10u + .dcmatch v(vtsc!) "
        "THRESHOLD=1 + mis_flag=1 100 次 MC); doc/task_spec.json + doc/scenario.md + task_meta."
        "json + task_spec.json = 交付接口; reframe_note 'explain-Q&A->produce-tool explainer+JSON "
        "reframe, 用户 junweix@hfeg0pkn002 原话 U0 给路径无附加上下文, 意图=读文件讲解, deepread "
        "1792732271802_olayh mc17, B 档 synthesized 合规'; track=None; layer=L1; real_task_summary "
        "junweix 0_VtscAct_pre/2_mc_iload.sp HSPICE MC 瞬态 Vtsc Active 负载调整率 100 MC; prompt "
        "显式 'SPICE 行来自真实 trace' + real HSPICE deck 作者日期 header + faithful compact "
        "reconstruction preserving real SPICE lines ⇒ A-faithful (real HSPICE deck author/date "
        "header; 新信号族: real HSPICE deck author/date header, 扩展 r813 export header 族至 "
        "HSPICE deck author/date 域; faithful compact reconstruction preserving real SPICE lines)"),
    "EDA-Eval-DesignFlow-VtscRefR5Logic-001": ("synth_deck",
        "vtsc_ref_netlist_A.sp = synth sim-schematic netlist (header '* VtscRef_standard_tb "
        "sim-schematic netlist (zmh_AI_VtscRef_standard_tb) * Visible input A for EDA-Eval-"
        "DesignFlow-VtscRefR5Logic-001 * R5 functional check target: derive logic outputs "
        "Vtsc2Vcc / VtscAmpDis' + stdcell black-box definitions '.SUBCKT nand2Lx1 a b Y' 信号端口"
        "仅 Y=output 黑盒); reframe_note 空; track=None; layer=L2; real_task_summary zmh_AI_"
        "VtscRef_standard_tb R5 功能推导 Vtsc2Vcc/VtscAmpDis 布尔等式真值表 + AG_VnocVdleqVtscRefAmp"
        "Core 运放核拓扑; synth sim-schematic netlist 含 stdcell black-box definitions, 'Visible "
        "input A' marker ⇒ synth_deck (synth netlist with stdcell black-box)"),
    "EDA-Eval-DesignFlow-WaveViewPanel-001": ("A-faithful",
        "openWave.pl = real WaveView tcl-generation Perl 脚本 (header '# Author: Billy.Luo # "
        "Mail: Billy.Luo@cxmt.com # Last modified: 2021-12-09 14:31 # Filename: openWave.pl' "
        "真实作者 header + 扫 waveDir FineSim *#*.sw0/PrimeSim *_wdf/Hspice *.sw*@*/Nanospice "
        "*.output); openSignal.tcl = real WaveView tcl 输出 (real /home/rongjiez/jira_dev/mpqa/"
        "mp_2/ModelQA_0924170807/idvd/result/ntn_w2.400u_l0.190u_nf1#N.sw0 路径 + sx_open_sim_file"
        "_read + sx_display + wv_select_waveview + wv_set_size WV1.PANEL{i}:1.HEIGHT 150); "
        "waveDir_A_listing.txt = real scan 路径清单 (9 FineSim .sw0); reframe_note 空; track="
        "spice_char; layer=L2; real_task_summary rongjiez WaveView panel 高度 bug openWave.pl 9 "
        "panel wv_set_size 150 最后 2 panel 默认矮高度, 终解 update idletasks 后统一设高度; real "
        "openWave.pl 作者 header Billy.Luo + real openSignal.tcl real /home/rongjiez 路径 + real "
        "WaveView tcl ⇒ A-faithful (real WaveView tcl-generation Perl script + tcl output; 新信号"
        "族: real WaveView tcl-generation Perl+tcl 双型, 扩展 r814 WaveView .sx 族至 tcl-generation "
        "script 域; track=spice_char)"),
    "EDA-Eval-DesignFlow-WlvlShmooLoopAnalyze-001": ("synth_deck",
        "Writeleveling001_external_writeleveling_preamble2_shmoo.v = 自包含合成 shmoo SystemVerilog "
        "task 资产 (task ... Writeleveling001_external_writeleveling_preamble2_shmoo + pattern_name "
        "+ tbcontrol.timingcal + if(dutconfig.dqmode==X4) wrptll=1 + for(int i=128*((modereg.c..."
        "保留 real DDR5 write-leveling loop 结构); task_brief.md = 交付接口 (analyze_wlvl_shmoo_"
        "loop.py); reframe_note 'portability+explain->produce-report candidate reframe, 用户 "
        "ericw@hfhds201 做 DDR5 DRCPA write-leveling shmoo loop 分析, 原话「分析这个路径下的这个文件 "
        "里面的循环是干什么的 如何循环的」, A 不可行原因=真实 DDR5 shmoo C 代码片段+FineSim 环境 SUT "
        "沙盒不可达 -> 用自包含合成 shmoo C 代码片段资产保留真实任务结构(asset_fidelity 缺标, 待 @A "
        "apply 档2)'; reframe_note 显式 self-declares '自包含合成 shmoo C 代码片段资产'; track="
        "faithful (verbatim prompt ericw) 但 asset synth ⇒ track≠asset_provenance; layer=L1; "
        "real_task_summary ericw DDR5 DRCPA write-leveling shmoo for-loop 语义分析; 自包含合成 "
        "shmoo .v, reframe self-declares synth ⇒ synth_deck (reframe_note self-declares "
        "provenance, 承 r819 SpTemplateOpt 族)"),
    "EDA-Eval-DesignFlow-WriteDqPsdMappingExtract-001": ("A-faithful",
        "A_ddr6_specdef.sv + A_ddr6_interface.sv + A_ddr6_test.sv + A_ddr6_genvector.sv = real "
        "DDR6 vecgen 4 .sv 代码节选 (specdef '// ddr6_specdef.sv -- DDR6 vecgen mode parameters "
        "(excerpt)' `ifdef X1P12/X1P6/X2P6/X2P3 parameter DQ_BITS/MAX_DQ_BITS + interface DqSelect "
        "+ test Write task+load_fifo+drive_dq + genvector analog vector $fmonitor output); "
        "task_brief.md = 交付接口; reframe_note 空; track=faithful; layer=L1; real_task_summary "
        "DDR6 DSCQA vecgen Write-task dq-param-bit to PSD0DQ/PSD1DQ vector-signal mapping table "
        "extraction under !DQSEL_LH, U#0 verbatim tongfanl; prompt 显式 '附件 4 个 .sv 文件是 DDR6 "
        "vecgen 的真实代码节选（specdef 模式参数 / interface DqSelect / test Write task+drive_dq / "
        "genvector 向量输出）' + verbatim prompt '/proj/dscqa/V0/setup/sim/sim_vector/verilog."
        "ddr6.dscqa.vecgen_local，帮我整理一个表格...DQSEL_LH...1P12/1P6/2P6/2P3'; real DDR6 "
        "vecgen 4 .sv 代码节选 + track=faithful + verbatim prompt ⇒ A-faithful (real DDR6 vecgen "
        ".sv code excerpts, 承 r822 TzqlatLocate 'real verilog vecgen .sv env files' 族)"),
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

    print("=== 档2 asset_fidelity backfill r823 batch23 ===")
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

    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r823_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r823_manifest.tsv — r823 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch23 (12 cases, alphabetical next 12 missing after r822 batch22 VcoKvcoChar: VecgenProbeEmptyDiag..WriteDqPsdMappingExtract, V→W 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r822 档2 batch1-22 (+264, 106→370) done. 本轮 r823 档2 batch23.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'real trace'/'忠实缩减'/'trace-faithful'/'真实代码节选'/'SPICE 行来自真实 trace' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / '重构' / minimal reconstruction / 'Generated as' / '示例' / 'Input A' / 'visible input A' / 'portable, model-free' / Chinese synth header / decoy comment / real-format export banner faithful mimicry / linear data progression / 显式 'stub' marker / level-1 MOS 模型 / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 33% (4/12) — V→W 段 real-trace 资产 (r822 累计 114/264=43.2%; 本批 4/12=33%, 累计 118/276=42.8%) / 新信号族 4 类 (real Verdi FSDB dumper error log banner VerdiFsdbLoadDiagnose '*Verdi* Loading/Cannot load libsscore_vcs202312.so /apps/synopsys/verdi/V-2023.12-SP2-3' 扩展 r813 export header 族至 Verdi FSDB error log 域 + real fscript dsignal-exported .tbl waveform VrefStepMeasure 2451 点 'TIME v(vref_dq<0>)' 扩展 export 族至 Synopsys fscript 文本波形导出域 + real WaveView tcl-generation Perl script+tcl output WaveViewPanel openWave.pl Billy.Luo 作者 + openSignal.tcl real /home/rongjiez 路径 扩展 r814 WaveView .sx 族至 tcl-generation script 域 + real HSPICE deck author/date header VtscMcDeckExplain '* User: junweix / * Date: 2026-10-23' 扩展 r813 export header 族至 HSPICE deck author/date 域) / track≠asset_provenance 3 例 (累计 48→51: VecgenProbeEmptyDiag track=faithful 但 synth_data 重建 log + VihTripTune track=faithful 但 synth_deck portable params + WlvlShmooLoopAnalyze track=faithful 但 synth_deck 自包含合成 .v) / synth_deck 5 例 (VihTripTune level-1 MOS params portable + VirtuosoSfeLangDiag 自包含 input.scs/netlist reframe self-declares synth + VsimFinesimAdapt 'A-faithful synthesized asset' self-declaration + VtscRefR5Logic stdcell black-box netlist + WlvlShmooLoopAnalyze 自包含合成 shmoo .v reframe self-declares synth) / synth_data 3 例 (VecgenProbeEmptyDiag 重建 terminal-log fixtures real WTM 名 + VerdiFsdbLoadDiagnose 重建 env-config/error-log fixtures real Verdi banner + VthOverrideHowtoGuide curated input_manifest.json 场景 surface) / reframe_note self-declares provenance 2 例 (VirtuosoSfeLangDiag + WlvlShmooLoopAnalyze, 承 r819 SpTemplateOpt 族)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 370->382 (cases/B 382==B.jsonl 382 ✓); miss 25->13\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
