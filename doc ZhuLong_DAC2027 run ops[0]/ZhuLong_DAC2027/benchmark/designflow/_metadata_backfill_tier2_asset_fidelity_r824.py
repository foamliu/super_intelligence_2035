#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r824.py — r824 档2 asset_fidelity backfill batch24 (FINAL).

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r823 档2 batch1-23 (+276, 106→382) done. 本轮 r824 档2 batch24 — 13 cases
      (alphabetical final 13 missing after r823 batch23: Wtm..Z 段).
      这是 档2 asset_fidelity backfill 的收口批次 (miss 13→0, 全 395 case 标完)。

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r823 扩展): A-faithful=真实 trace-verbatim/真实 scp 资产
                              (real export header / real 作者 header / real /proj|/home|/rundata|/apps
                               路径 / 'verbatim'/'real excerpt'/'逐字'/'real trace'/'SPICE 行来自真实 trace'
                               标注 / real tool banner 无 synth comment header);
                              synth_deck=合成 SPICE/Verilog/TCL deck/netlist/source (portable reconstruction
                               / 'faithful reconstruction' / '自包含合成' / level-1 MOS 模型 / stdcell
                               black-box / Chinese synth header / reframe self-declares synth);
                              synth_data=合成 log/manifest/structured-data fixtures (重建 terminal-log /
                               curated manifest / 重建 env-config+error-log / excerpted .v with omission
                               markers + reconstructed log);
                              no-asset=0 附件 Q&A.

本批 13 case 判定 (Wtm..Z 段, 收口批):
  - 8 A-faithful (62%) — W..Z 段 real-log/real-excerpt 资产密集 (r823 累计 118/276=42.8%;
    本批 8/13=62%, 累计 126/289=43.6%). 8 例:
      * WtmFileReview (A_wtm1/2/3.v header '// WTM001_normal_check.v (real excerpt, tongfanl,
        /home/tongfanl/DDR6/DSCQA/analogsim/WTM/) // Lines selected from the real file for static
        review analysis.' 真实 .v excerpt + real /home/tongfanl 路径; track=faithful verbatim
        prompt tongfanl)
      * WtmPatternDirReview (A_wtm1-5.v real DDR6 WTM pattern Verilog lines with '// ... (lines
        omitted) ...' elision markers; 可见行 trace-verbatim PDE/PDX/CLK_SYNC/CLK_SYNC_OFF/
        error_write/pattern_name 同 WtmFileReview; track=faithful verbatim prompt tongfanl)
      * WtmWriteArrayScope (A_vecgen/ddr6_test.sv header '// ddr6_test.sv — real excerpt (vecgen),
        Write task array-write gating // source: /proj/dscqa/.../ddr6_test.sv // lines 734, 809,
        1537-1548, 1628 — extracted verbatim from trace tool_results // (read_files /
        run_approved_command grep+sed on /proj/dscqa, trace 1792033394584_xd7ut)' 强信号: 'extracted
        verbatim from trace tool_results' + real /proj 路径 + 行号; track=faithful)
      * XaLogCompare (xa_logs_A/CCK_include_rshort1M_1016.xa.log + 1009.xa.log real FineSim XA
        export log 'FineSim XA Version V-2023.12-SP1-1 2026/10/16 / (c) Synopsys, Inc. / Netlist:
        /rundata/lacaa/.../CCK_include_rshort1M_1016.sp / measure t_ac_q = 1.200e-09 s' real
        FineSim XA banner + real /rundata 路径 + real measure 值, 无 synth comment header;
        real_task_summary 'A-faithful U[32] 逐字')
      * XmelabCuvpomPortDiag (A_xmelab.log real xmelab CUVPOM elaboration error log 'xmelab: *E,
        CUVPOM (./libs/simlib_drcoa_digital.sv,1056|107): Port name vss_ of instance
        BCenterCA.I_T_CMCenterL.I_AF_Lat16g_1778_0_.I0_7_.FwdM is invalid...' real instance
        hierarchy 路径 + real 错误码, 无 synth comment header; track=faithful)
      * XrunLogErrDiag (A_xrun.log real xrun/xmelab error log 'xrun(64): 06.10.2026 13:31:15 /
        xmelab: *E,CUVUNF (./proj_monitor/project_pump_monitor.sv,201|102): Hierarchical name
        component lookup failed for tREFI3P9D' real timestamp + real CUVUNF 错误 + real source
        位置, 无 synth comment header; track=faithful)
      * ZqCodeLinExtract (Ron_global.ms0 real PrimeSim HSPICE export '$DATA1 SOURCE=PrimeSim
        HSPICE VERSION=V-2023.12-SP1-1 linux64 PARAM_COUNT=7 / .TITLE ZQ code linearization Ron
        global sweep - 6bit - 64pt' real .ms0 多行 22 列 measure export + ref_extract_zqcode_lin.py
        real 参考 script; attachments desc '来自 clarawu 的 cline trace'; track=faithful verbatim
        prompt clarawu)
      * ZqPatternTimingAnalyze (A_test.sv header '// Excerpt of ddr6_test.sv (DDR6 vecgen_local
        testbench). // Real content from /proj/dscqa/.../ddr6_test.sv // Contains the
        ZQ001_normal_check pattern task definition (verbatim as pasted by the user).' real .sv
        excerpt + 'verbatim as pasted by the user' 强信号 + real /proj 路径; track=faithful)
  - 4 synth_deck:
      * WtmCrcInjectionAudit (A_wtm_block_check.v header '// A_only_wtm_crc_marker // Faithful
        reconstruction of WTM004_block_check.v (tongfanl@hfhds201, trace iy9oc U#22).' 'Faithful
        reconstruction' 重建 + A_only anti-leak marker; track=faithful 但 asset synth ⇒
        track≠asset_provenance; layer=L1; reframe audit-Q&A→produce-tool)
      * WtmStructReview (WTM001/WTM002_normal_check.v 自包含合成 .v excerpt, 无 comment header
        (直接 task WTM001_normal_check...); reframe_note 显式 self-declares 'A 不可行原因=真实
        WTM001/WTM002 .v 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM001/WTM002 .v excerpt 资产
        保留真实任务结构'; track=faithful 但 asset synth ⇒ track≠asset_provenance; layer=L1;
        reframe_note self-declares provenance, 承 r819 SpTemplateOpt 族)
      * WvFmFreqExtract (wave_A.dat synth WDF binary FM 波形 (WDF 3.01 ACE header, 5001 点,
        载波 2→5Hz 线性扫频) + spec_A.json synth 参数; track=synthesized ⇒ 一致 (非 track≠);
        layer=L2; reframe portability produce-tool→produce-tool 波形便携化, A 不可行原因=真实
        foundry 波形 SUT 沙盒不可达; characterization 域)
      * WvModalPopupTclFix (Zhulong.tcl 重建 buggy TCL context (Chinese synth header '# Zhulong.tcl
        — WaveView 菜单脚本：启动 ZL(zhulong) 页面 / # 现状(有 bug)：弹窗不见了 + 主页面可操作(不模态)'
        + scenario.txt/requirements.json 交付接口; real /home/yanxvwei + /apps/cad 路径 embedded
        in synth asset; track=None; layer=None; reframe harness produce-action debug-fix TCL→
        produce-tool TCL generator; 0 attachments in case json 但 assets/ 有 context 文件)
  - 1 synth_data:
      * WtmDanglingElseMre0Diag (A_xrun.log 重建 xrun.log excerpt (header '// xrun.log excerpt —
        WTM001_normal_check SC0 X2P3 DQSELH simulation // Key evidence: is4phase=0 (2-phase mode),
        Write 9 error injection.' 重建 log 带 comment header) + A_wtm001_normal_check.v 'Faithful
        reconstruction of the stimulus-extraction pattern source' + '// ... (setup / declarations
        omitted for brevity) ...' 重建 .v excerpt; track=faithful 但 asset 重建 ⇒
        track≠asset_provenance; layer=L1; reframe Q&A/diag→produce-tool 诊断器, 重建 log+.v
        fixtures 保留 real WTM 名; 承 r823 VecgenProbeEmptyDiag '重建 terminal-log fixtures' 族)

关键发现:
  - A-faithful 62% (8/13) — W..Z 段 real-log/real-excerpt 资产密集 (r823 累计 118/276=42.8%;
    本批 8/13=62%, 累计 126/289=43.6%). 收口批 A-faithful 比率高于均值 (W..Z 段 X*/Zq* real
    simulation log/data export 集中: FineSim XA log / xmelab CUVPOM log / xrun CUVUNF log /
    PrimeSim HSPICE .ms0 / DDR6 vecgen .sv verbatim excerpt).
  - 新信号族 5 类:
    * real FineSim XA measure log with real /rundata path + real measure values (XaLogCompare
      'FineSim XA Version V-2023.12-SP1-1 2026/10/16 / Netlist: /rundata/lacaa/.../CCK_include_
      rshort1M_1016.sp / measure t_ac_q = 1.200e-09 s', 扩展 r818/r822 FineSim export banner族
      至 XA measure-log 域)
    * real xrun/xmelab elaboration error log with real instance hierarchy + real timestamp
      (XmelabCuvpomPortDiag 'xmelab: *E,CUVPOM Port name vss_ of instance BCenterCA.I_T_CMCenterL.
      I_AF_Lat16g_1778_0_.I0_7_.FwdM' + XrunLogErrDiag 'xrun(64): 06.10.2026 13:31:15 / xmelab:
      *E,CUVUNF Hierarchical name component lookup failed for tREFI3P9D', 新家族: real xrun/xmelab
      elaboration error log, 扩展 export header族至 xrun/xmelab error-log 域)
    * real PrimeSim HSPICE .ms0 multi-row 22-column measure export (ZqCodeLinExtract '$DATA1
      SOURCE=PrimeSim HSPICE VERSION=V-2023.12-SP1-1 linux64 PARAM_COUNT=7 / .TITLE ZQ code
      linearization Ron global sweep - 6bit - 64pt' 32 records zqdec 0-31 5-bit zq 码 22 列跨 7
      物理行, 扩展 r813 PrimeSim HSPICE .ma0族至 .ms0 multi-row domain)
    * real DDR6 WTM training-mode Verilog pattern excerpts (WtmFileReview 'real excerpt, Lines
      selected from the real file' + WtmPatternDirReview real lines with elision markers +
      WtmWriteArrayScope 'extracted verbatim from trace tool_results' + ZqPatternTimingAnalyze
      'verbatim as pasted by the user', 新家族: real DDR6 vecgen/WTM .v pattern excerpts, 扩展
      r822 verilog vecgen族至 WTM pattern-review 域)
    * reframe self-declares provenance (WtmStructReview reframe 显式 '自包含合成 WTM001/WTM002 .v
      excerpt 资产', 承 r819 SpTemplateOpt / r823 WlvlShmooLoopAnalyze 族)
  - track≠asset_provenance 3 例 (累计 51→54): WtmCrcInjectionAudit (track=faithful verbatim
    prompt 但 asset synth_deck 重建 .v) + WtmStructReview (track=faithful 但 asset synth_deck
    自包含合成 .v) + WtmDanglingElseMre0Diag (track=faithful verbatim prompt 但 asset synth_data
    重建 log+.v). (WvFmFreqExtract track=synthesized 与 asset synth_deck 一致, 非 track≠;
    WvModalPopupTclFix track=None, 非 track≠)
  - synth_deck 4 例: WtmCrcInjectionAudit (faithful reconstruction .v + A_only marker) +
    WtmStructReview (自包含合成 .v, reframe self-declares synth) + WvFmFreqExtract (synth WDF FM
    波形, track=synthesized) + WvModalPopupTclFix (重建 buggy TCL context, harness reframe).
  - synth_data 1 例: WtmDanglingElseMre0Diag (重建 xrun.log excerpt + .v faithful reconstruction).
  - 收口: miss 13→0, 全 395 case asset_fidelity 标完 (382+13=395). 档2 asset_fidelity backfill
    全量收口 (r801-r824, 24 batch, +289, 106→395).
"""

import json
import os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-WtmCrcInjectionAudit-001": ("synth_deck",
        "A_wtm_block_check.v = faithful reconstruction 重建 .v (header '// A_only_wtm_crc_marker "
        "// Faithful reconstruction of WTM004_block_check.v (tongfanl@hfhds201, trace iy9oc U#22).' "
        "'Faithful reconstruction' 重建标记 + A_only anti-leak marker; task WTM004_block_check ... "
        "during-WTM injection lines ~95-97 + after-WTM injection lines ~158-161); task_brief.md = "
        "交付接口; reframe_note 'audit-Q&A->produce-tool audit+JSON reframe, §4 有牙必要, r747 "
        "spotcheck batch25: 用户 tongfanl@hfhds201 sess 1793363756811_iy9oc mc154, U0 逐字 帮我看下 "
        "WTM004_block_check.v 文件 95:97 行能实现在 WTM 期间造 CRC 错的目的吗 158 行到 161 行能实现在 "
        "退出 WTM 后造 CRC 错的目的吗, trace 实为静态审计 .v 行能否实现 CRC 错注入目的(无 root cause/"
        "fix); A 不可行原因=纯 audit'; track=faithful (verbatim prompt tongfanl) 但 asset 重建 ⇒ "
        "track≠asset_provenance; layer=L1; real_task_summary tongfanl WTM CRC error-injection "
        "verification audit; 'Faithful reconstruction' 重建 .v + A_only marker ⇒ synth_deck "
        "(faithful reconstruction of .v source, 非 raw scp)"),
    "EDA-Eval-DesignFlow-WtmDanglingElseMre0Diag-001": ("synth_data",
        "A_xrun.log = 重建 xrun.log excerpt (header '// xrun.log excerpt — WTM001_normal_check SC0 "
        "X2P3 DQSELH simulation // Key evidence: is4phase=0 (2-phase mode), Write 9 error injection.' "
        "重建 log 带 comment header + '[WTM Gen Task: gen_wtm_write_data] Input Parameters dq_pattern_"
        "select/err_inject_rand/ui_mask/dq_mask' real WTM 名); A_wtm001_normal_check.v = faithful "
        "reconstruction .v excerpt (header '// WTM001_normal_check.v — DDR6 DSCQA vecgen pattern "
        "(X2P3 / DQSELH / SC0 branch) // Faithful reconstruction of the stimulus-extraction pattern "
        "source. // The task: diagnose why mre0 expdata is all 0 ... // Key section: lines 510-530 "
        "(the X2P3/DQSELH/SC0 2-phase branch with dangling-else).' + '// ... (setup / declarations "
        "omitted for brevity) ...' 重建 .v excerpt); reframe_note 'Q&A/diag->produce-tool 诊断器 "
        "reframe, §4 有牙必要, r742 spotcheck batch20: 用户 tongfanl@hfhds201 原话(msg#26) 帮我看下这个"
        "文件夹下抽出的激励 明明xun.log中gen_wtm_write_data中的dq0 UI1和UI2都有错 为啥mre0的expdata是全0 "
        "(Q&A/diag 问为什么, deepread 1792993730194_cyua2 mc98, 80 msgs), gold-standard(msg#42)=dangling-"
        "else 死代码根因, 未给根因; A 不可行原因=纯 Q&A/diag(问为什么)无 runnable artifact 无 check 牙'; "
        "track=faithful (verbatim prompt tongfanl) 但 asset 重建 ⇒ track≠asset_provenance; layer=L1; "
        "real_task_summary tongfanl WTM001 stimulus extraction mre0 expdata all-0 dangling-else "
        "diagnosis; 重建 xrun.log excerpt + .v faithful reconstruction 保留 real WTM 名 ⇒ synth_data "
        "(重建 log+.v fixtures, 承 r823 VecgenProbeEmptyDiag '重建 terminal-log fixtures' 族)"),
    "EDA-Eval-DesignFlow-WtmFileReview-001": ("A-faithful",
        "A/A_wtm1.v + A_wtm2.v + A_wtm3.v = real .v excerpts (header '// WTM001_normal_check.v "
        "(real excerpt, tongfanl, /home/tongfanl/DDR6/DSCQA/analogsim/WTM/) // Lines selected from "
        "the real file for static review analysis.' 显式 'real excerpt' + real /home/tongfanl 路径; "
        "task WTM001_normal_check ... PDE/PDX/CLK_SYNC real Verilog lines; 3 files WTM001/002/004); "
        "reframe_note 'portability+review->produce-tool 审查器 reframe, §4 有牙必要, r736 spotcheck "
        "batch14: 用户 tongfanl@hfhds201 原话 ll WTM001_normal_check.v WTM002_normal_check.v "
        "WTM004_block_check.v 帮我检查下这三个文件写的有没有问题(纯 review 请求), agent 在 trace 读三"
        "文件给详细报告'; track=faithful (verbatim prompt tongfanl); layer=L1; real_task_summary "
        "tongfanl DDR6 DSCQA analogsim WTM pattern review; 'real excerpt, Lines selected from the "
        "real file' + real /home/tongfanl 路径 + real Verilog lines ⇒ A-faithful (real .v excerpts, "
        "trace-verbatim lines; 新家族: real DDR6 WTM training-mode Verilog pattern excerpts)"),
    "EDA-Eval-DesignFlow-WtmPatternDirReview-001": ("A-faithful",
        "A/A_wtm1.v..A_wtm5.v = real DDR6 WTM pattern Verilog lines with '// ... (lines omitted) "
        "...' elision markers (task WTM001_normal_check ... bit [9:0] error_write = 10'b00_0000_0000 "
        "/ error_write = 10'b00001_00000 / pattern_name=WTM001_normal_check / PDE(.rank(0),.odt(0)) "
        "//CA3=L / PDX() / CLK_SYNC() / CLK_SYNC_OFF() 可见行 trace-verbatim 同 WtmFileReview; 5 "
        "files WTM001-005); prompt.txt = verbatim 用户原话 /home/tongfanl/DDR6/DSCQA/analogsim/WTM/ "
        "帮我看下这里面的pattern有没有问题; task_brief.md = 交付接口 (review_wtm_dir.py); reframe_note "
        "'portability+review->produce-tool 目录审查器 reframe, §4 有牙必要, r736 spotcheck batch14: "
        "用户 tongfanl@hfhds201 原话 帮我看下这里面的pattern有没有问题(纯 review 请求), agent 在 trace "
        "检查 5 符号链接 Verilog pattern 文件(WTM001-005), 找 7 确认问题'; track=faithful (verbatim "
        "prompt tongfanl); layer=L1; real_task_summary tongfanl DDR6 DSCQA analogsim WTM pattern "
        "directory review; 可见行 trace-verbatim real Verilog + elision markers 表示 excerpt 非 "
        "synthesis ⇒ A-faithful (real .v excerpts with elision markers, trace-verbatim lines; "
        "新家族: real DDR6 WTM training-mode Verilog pattern excerpts, 承 WtmFileReview 族)"),
    "EDA-Eval-DesignFlow-WtmStructReview-001": ("synth_deck",
        "A/WTM001_normal_check.v + A/WTM002_normal_check.v = 自包含合成 .v excerpt (无 comment header, "
        "直接 task WTM001_normal_check(reg[GROUP_BITS-1:0] bg0, ...)... begin:WTM001_normal_check ... "
        "bit pattern_select / reg [48*6 -1:0] wtm_wr_data[] / reg [23:0] ui_mask_arr[10] synth .v "
        "结构); prompt.txt + task_brief.md = 交付接口; reframe_note 'portability+review->produce-tool "
        "审查器 reframe, §4 有牙必要, r736 spotcheck batch14: 用户 tongfanl@hfhds201 原话 WTM001_normal_"
        "check.v WTM002_normal_check.v 检查下有没有问题 不要改动(纯 review 请求), agent 在 trace 用 "
        "read_files 读两文件给 8 条结构审查发现(文本答案)未产出结构化审查脚本; A 不可行原因=真实 "
        "WTM001/WTM002 .v 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM001/WTM002 .v excerpt 资产保留真实"
        "任务结构(asset_fidelity 缺标, 待 @A apply 档2)'; reframe_note 显式 self-declares '自包含合成 "
        "WTM001/WTM002 .v excerpt 资产'; track=faithful (verbatim prompt tongfanl) 但 asset synth ⇒ "
        "track≠asset_provenance; layer=L1; real_task_summary tongfanl DDR6 DSCQA analogsim WTM 写训练"
        "模式 stimulus Verilog 文件静态结构审查; 自包含合成 .v excerpt, reframe self-declares synth ⇒ "
        "synth_deck (reframe_note self-declares provenance, 承 r819 SpTemplateOpt / r823 WlvlShmooLoop"
        "Analyze 族)"),
    "EDA-Eval-DesignFlow-WtmWriteArrayScope-001": ("A-faithful",
        "A_vecgen/ddr6_test.sv + ddr6_package.sv + ddr6_specdef.sv = real .sv excerpts (ddr6_test.sv "
        "header '// ddr6_test.sv — real excerpt (vecgen), Write task array-write gating // source: "
        "/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/ddr6_test.sv // lines 734, 809, "
        "1537-1548, 1628 — extracted verbatim from trace tool_results // (read_files / run_approved_"
        "command grep+sed on /proj/dscqa, trace 1792033394584_xd7ut)' 强信号 'extracted verbatim from "
        "trace tool_results' + real /proj/dscqa 路径 + 行号 734/809/1537-1548/1628 + 'distractor: "
        "another task MR5 skip' decoy comment + write_mem_arr guard if(!(`mr_da.MR5_func_mode == "
        "Write_Leveling_Training))); task_brief.md = 交付接口; reframe_note 'analysis/Q&A->produce-"
        "tool 分析器 reframe, §4 有牙必要, r740 spotcheck batch18: 用户 tongfanl@hfhds201 原话 帮我分析"
        "下这个环境 并回答 当进入WTM 模式时 发送write命令 会不会把数据发到array里去(analysis/Q&A 问答案, "
        "trace 金标准 1792033394584_xd7ut mc1379127: WTM 模式下 write 命令会把数据写入 array, 因 write_"
        "mem_arr 的门控 if 只跳过 Write_Leveling_Training 未含 Write_Training_Mode)'; track=faithful "
        "(verbatim prompt tongfanl); layer=L1; real_task_summary tongfanl DDR6 vecgen WTM write-to-"
        "array scope question; 'extracted verbatim from trace tool_results' + real /proj 路径 + 行号 "
        "⇒ A-faithful (real .sv verbatim excerpt with line numbers; 新家族: real DDR6 vecgen .sv "
        "verbatim excerpt with line numbers, 承 r822 TzqlatLocate 'real verilog vecgen .sv env files' "
        "族)"),
    "EDA-Eval-DesignFlow-WvFmFreqExtract-001": ("synth_deck",
        "wave_A.dat = synth WDF binary FM 波形 (WDF 3.01 ACE header 'Saved by ACE', 5001 点, 模拟信号 "
        "wave, FM 调频信号 载波 2→5Hz 线性扫频 幅值 0~3V); spec_A.json = synth 参数 (wave_file wave_A."
        "dat/sig_name wave/v_thr 1.5/carrier_start 2.0/carrier_end 5.0/n_points 5001/t_start 0.0/t_end "
        "1.0/sweep_type linear/sim_cmd wv -ace_no_gui); prompt.txt + task_brief.md = 交付接口 (fm_freq_"
        "vs_t.tcl); reframe_note 'portability produce-tool->produce-tool 波形便携化 reframe, §4 有牙必要, "
        "r742 spotcheck batch20: 用户 e0023936@hfeg0plg52 原话 trace 全程 sandbox run_code lang=tcl 真跑 "
        "WaveView ACE Tcl(produce-tool 写 ACE Tcl 频率提取脚本, deepread 1793095651315_qb1ua mc103), 定义 "
        "f_vs_t(sig,v_thr) -> RISE 扫描+阈值 -> 遍历上升沿 f=1/(t2-t1) -> sx_append_data -> sx_write_open "
        "写 WDF; A 不可行原因=真实 foundry 波形 SUT 沙盒不可达'; track=synthesized (与 asset synth 一致 "
        "⇒ 非 track≠); layer=L2; domain=characterization; real_task_summary e0023936 WaveView ACE Tcl FM "
        "调频信号瞬时频率 vs 时间曲线提取; synth WDF FM 波形 + spec, track=synthesized ⇒ synth_deck "
        "(synth WDF waveform + spec, portable reconstruction, 承 r813 'portable level-1 MOS model' / "
        "synth waveform 族)"),
    "EDA-Eval-DesignFlow-WvModalPopupTclFix-001": ("synth_deck",
        "Zhulong.tcl = 重建 buggy TCL context script (Chinese synth header '# Zhulong.tcl — WaveView "
        "菜单脚本：启动 ZL(zhulong) 页面 / # 现状(有 bug)：弹窗不见了 + 主页面可操作(不模态)' + source "
        "real /home/yanxvwei/Script/Waveview/Zhulong_server.tcl 路径 + exec /bin/bash -lc /apps/cad/"
        "bin/zl real 命令 embedded in synth asset + catch {destroy .} + wm title . zhulong + label ."
        "zl_lbl 'Launching zhulong, please wait...' buggy popup logic); scenario.txt = verbatim 用户"
        "原话三条要求; requirements.json = 场景配置 + 报告 schema; task_brief.md = 交付接口 (wv_modal_"
        "launcher_gen.py); reframe_note 'harness produce-action debug-fix TCL->produce-tool TCL "
        "generator reframe, §4 有牙必要, r749 spotcheck batch27: 用户 yanxvwei@hfeg0pkn002 sess "
        "1793587957934_hupl6 mc8, 多轮 verbatim zl的页面启动之前 弹窗要存在 / 弹窗不见了 查找原因并修改 / "
        "我需要弹窗的时候wv主页面savesignal一样 会无法操作; trace 金标准 8 msgs WaveView TCL Zhulong.tcl "
        "launcher, popup bug(catch{destroy .} 杀根窗口+grab set .+tkwait 卡死)'; track=None; layer=None; "
        "real_task_summary yanxvwei WaveView TCL Zhulong.tcl launcher popup bug (catch{destroy .} 杀根"
        "窗口 + grab set . + tkwait 卡死); 重建 buggy TCL context + Chinese synth header, real 路径 "
        "embedded in synth asset ⇒ synth_deck (重建 buggy TCL context, harness reframe; 承 r816 "
        "SimCapLisParse 'real /proj path embedded in synth .lis' 族)"),
    "EDA-Eval-DesignFlow-XaLogCompare-001": ("A-faithful",
        "xa_logs_A/CCK_include_rshort1M_1016.xa.log + CCK_include_rshort1M_1009.xa.log = real FineSim "
        "XA export logs (header 'FineSim XA Version V-2023.12-SP1-1 2026/10/16 / (c) Synopsys, Inc. / "
        "Netlist: /rundata/lacaa/V0/simdir/finesim/workdir/zilingw/1_simulation/9_post_sim/3_fullinst/"
        "simulation/xa_results/CCK_include_rshort1M_1016/CCK_include_rshort1M_1016.sp / Option: -post "
        "-rshort1M -cpu 16 / measure t_ac_q = 1.200e-09 s' real FineSim XA banner + real /rundata/"
        "lacaa 路径 + real measure 值, 无 synth comment header); reframe_note 'Q&A explain-Q&A->"
        "produce-tool compare CLI reframe, §4 有牙必要, r747 spotcheck batch25: 用户 e0024852@hfeg0"
        "pkn004 sess 1792118523831_f10db mc68, U0 逐字 you compare the result of /rundata/lacaa/.../"
        "CCK_include_rshort1M_1009/xa.log and this log tell me in chinese; trace 实为多轮 XA log/dspf "
        "对比讲解; A 不可行原因=纯 explain-Q&A(对比两份 FineSim XA log)无 runnable artifact 无 check 牙 "
        "⇒ 重构为 xa_log_compare.py compare CLI'; track=faithful; layer=None; real_task_summary "
        "e0024852 'A-faithful U[32] 逐字 you compare the result of .../CCK_include_rshort1M_1009/xa.log "
        "and this log tell me in chinese'; real FineSim XA export log + real /rundata 路径 + real "
        "measure 值, 无 synth marker ⇒ A-faithful (real FineSim XA measure log; 新家族: real FineSim "
        "XA measure log with real /rundata path, 扩展 r818/r822 FineSim export banner族至 XA measure-"
        "log 域)"),
    "EDA-Eval-DesignFlow-XmelabCuvpomPortDiag-001": ("A-faithful",
        "A_xmelab.log = real xmelab CUVPOM elaboration error log (header 'xmelab: *E,CUVPOM (./libs/"
        "simlib_drcoa_digital.sv,1056|107): Port name vss_ of instance BCenterCA.I_T_CMCenterL.I_AF_"
        "Lat16g_1778_0_.I0_7_.FwdM is invalid or has multiple connections and the instantiated module "
        "is defined in file {Name Protected}.' real xmelab CUVPOM 错误码 + real instance hierarchy "
        "BCenterCA.I_T_CMCenterL.I_AF_Lat16g_... 路径 + real 源码位置 1056|107, 无 synth comment "
        "header, {Name Protected} 为源文件名 redaction 非 synthesis); prompt.txt + task_brief.md = "
        "交付接口 (diagnose_xmelab.py); reframe_note 'Q&A/diag->produce (§4 有牙必要, r726 spotcheck "
        "batch6): 用户 e0039602@hfeg0pkn004(mc803) A-档 verbatim 原话 我刚刚跑仿真这个报错是什么意思 "
        "(xmelab CUVPOM 端口错误诊断 Q&A), trace agent 对比 AIout1106(错)/AIout(对)两版 simlib 内联诊"
        "断(未写 reusable .py), 重构为产 diagnose_xmelab.py 输出 out.json(13 keys: cuvpom_count/"
        "invalid_ports/源码列号/去重实例)'; track=faithful; layer=None; real_task_summary e0039602 "
        "xrun/xmelab 仿真日志 CUVPOM 端口错误诊断 (AIout1106 错误版把前向锁存级从传输门 passg_base 改写"
        "成 inven_base FwdM 强接 vcc_/vss_, 而 inven_base 不定义 vcc_/vss_ 端口→CUVPOM); real xmelab "
        "CUVPOM error log + real instance hierarchy, 无 synth marker ⇒ A-faithful (real xmelab "
        "elaboration error log; 新家族: real xrun/xmelab elaboration error log with real instance "
        "hierarchy)"),
    "EDA-Eval-DesignFlow-XrunLogErrDiag-001": ("A-faithful",
        "A_xrun.log = real xrun/xmelab error log (header 'xrun(64): 06.10.2026 13:31:15 / xrun(64): "
        "-compile_script xrun_compile.log / xmvlog: All Module compilation done 0 errors, 0 warnings "
        "/ xmelab: Starting elaboration / xmelab: *E,CUVUNF (./proj_monitor/project_pump_monitor.sv,"
        "201|102): Hierarchical name component lookup failed for tREFI3P9D at TOP.A_pattern_gen.' "
        "real xrun timestamp 06.10.2026 13:31:15 + real CUVUNF 错误码 + real 源码位置 ./proj_monitor/"
        "project_pump_monitor.sv,201|102 + real hierarchical name tREFI3P9D at TOP.A_pattern_gen, "
        "无 synth comment header); prompt.txt + task_brief.md = 交付接口 (check_xrun_log.py); reframe_"
        "note 空; track=faithful; layer=None; real_task_summary e0014036@hfeg0pkn004 xrun/xmelab 仿真"
        "日志错误诊断 (在 /rundata/drcoa/V0/simdir/verilog/e0014036/verilog.ddr5.drcoa.pte.1015/test_"
        "nt/noregression.x8 目录下要求找到 xrun.log 读取内容检测内部报错; 金标准 check_xrun_log.py: "
        "正则 *E,CODE 统计 68 errors CUVUNF=66/ELBERR=1/RUNERR=1, CUVUNF 根因=monitor 引用 3 个接口"
        "字段不存在 tREFI3P9D); real xrun error log + real timestamp + real CUVUNF 错误, 无 synth "
        "marker ⇒ A-faithful (real xrun/xmelab error log; 新家族: real xrun/xmelab elaboration error "
        "log with real timestamp, 承 XmelabCuvpomPortDiag 族)"),
    "EDA-Eval-DesignFlow-ZqCodeLinExtract-001": ("A-faithful",
        "Ron_global.ms0 = real PrimeSim HSPICE .ms0 multi-row measure export (header '$DATA1 SOURCE="
        "PrimeSim HSPICE VERSION=V-2023.12-SP1-1 linux64 PARAM_COUNT=7 / .TITLE ZQ code linearization "
        "Ron global sweep - 6bit - 64pt / index zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpu_20 rpu_50 rpu_75 "
        "rpd_20 rpd_50 rpd_75 rpu_lin20 rpu_lin50 ...' 32 records zqdec 0-31 5-bit zq 码 22 列跨 7 "
        "物理行/记录, real PrimeSim HSPICE export banner + real .TITLE); ref_extract_zqcode_lin.py = "
        "real 参考 script (header '#!/usr/bin/env python3 # extract_zqcode_lin.py - Process HSPICE "
        ".md0 single-line Monte-Carlo output. Find the row with rpu_50 closest to TARGET (for PU) "
        "and rpd_50 closest to TARGET (for PD). Output two files: pu_zqcode_lin and pd_zqcode_lin. "
        "This is the REFERENCE script (single-line .md0 format).'); prompt.txt + task_brief.md = "
        "交付接口 (extract_zqcode_lin_ms0.py); reframe_note 空; track=faithful; layer=L1; real_task_"
        "summary clarawu@hfeg0pkn004 DDR4 Ron 表征 zq-code 提取 (USER#2 原话 @...Ron_global.ms0 帮我写"
        "个脚本 功能和@...extract_zqcode_lin.py一样 — 要求为 PrimeSim HSPICE 多行列式 .ms0 格式(22 列"
        "跨 7 物理行/记录)写功能等同于单行 .md0 版 extract_zqcode_lin.py 的脚本); attachments desc "
        "'来自 clarawu 的 cline trace'; real PrimeSim HSPICE .ms0 export + real ref script + '来自 "
        "clarawu 的 cline trace' ⇒ A-faithful (real PrimeSim HSPICE .ms0 multi-row measure export; "
        "新家族: real PrimeSim HSPICE .ms0 multi-row 22-column measure export, 扩展 r813 PrimeSim "
        "HSPICE .ma0族至 .ms0 multi-row domain)"),
    "EDA-Eval-DesignFlow-ZqPatternTimingAnalyze-001": ("A-faithful",
        "A_test.sv = real .sv excerpt (header '// Excerpt of ddr6_test.sv (DDR6 vecgen_local "
        "testbench). // Real content from /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa."
        "vecgen_local/ddr6_test.sv // Contains the ZQ001_normal_check pattern task definition "
        "(verbatim as pasted by the user). This pattern exercises the ZQ calibration reset / stop / "
        "initiation (ZQUF) flow on MR7 and observes DQ error/pass behaviour.' 强信号 'verbatim as "
        "pasted by the user' + real /proj/dscqa 路径; task ZQ001_normal_check ... pattern_name="
        "ZQ001_normal_check / tbcontrol.timingcal=auto / CLK_SYNC_OFF() / DeselectT / Load_Mode MR6 "
        "ZQCAL_Latch / Active / Write real Verilog lines); reframe_note 'portability+analyze->"
        "produce-tool 分析器 reframe, §4 有牙必要, r736 spotcheck batch14: 用户 tongfanl@hfhds201 原"
        "话粘贴完整 ZQ001_normal_check pattern task + 帮我看下在该环境下 跑pattern(analyze/Q&A), agent "
        "在 trace 拆解 11 步(CLK_SYNC_OFF+250ns DeselectT/ZQCal Latch clear/Active->Write/ZQ Reset "
        "MR7 OP[2]+750ns/MRSetting OP[0]/OP[1] ZQ Initiation/MRR(MR7) 读 ZQUF/Active->Read D)'; track="
        "faithful; layer=L1; real_task_summary tongfanl DDR6 vecgen_local ZQ001_normal_check pattern "
        "timing 关系分析 (11 步 ZQ calibration reset/stop/initiation ZQUF flow); 'verbatim as pasted "
        "by the user' + real /proj 路径 + real Verilog lines ⇒ A-faithful (real .sv verbatim excerpt; "
        "新家族: real DDR6 WTM/ZQ training-mode Verilog pattern excerpts, 承 WtmFileReview/"
        "WtmPatternDirReview/WtmWriteArrayScope 族)"),
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

    print("=== 档2 asset_fidelity backfill r824 batch24 (FINAL) ===")
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

    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r824_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r824_manifest.tsv — r824 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch24 FINAL (13 cases, alphabetical final 13 missing after r823 batch23: Wtm..Z 段, 收口批 miss 13->0)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r823 档2 batch1-23 (+276, 106→382) done. 本轮 r824 档2 batch24 FINAL.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'real trace'/'real excerpt'/'extracted verbatim from trace tool_results'/'verbatim as pasted by the user' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / 'faithful reconstruction' / '自包含合成' / reframe self-declares synth / Chinese synth header / A_only anti-leak marker / real 路径 embedded in synth asset / level-1 MOS 模型 / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 62% (8/13) — W..Z 段 real-log/real-excerpt 资产密集 (r823 累计 118/276=42.8%; 本批 8/13=62%, 累计 126/289=43.6%) 收口批 A-faithful 比率高于均值 (X*/Zq* real simulation log/data export 集中) / 新信号族 5 类 (real FineSim XA measure log with real /rundata path XaLogCompare 扩展 r818/r822 FineSim export banner族至 XA measure-log 域 + real xrun/xmelab elaboration error log with real instance hierarchy+timestamp XmelabCuvpomPortDiag+XrunLogErrDiag 新家族 扩展 export header族至 xrun/xmelab error-log 域 + real PrimeSim HSPICE .ms0 multi-row 22-column measure export ZqCodeLinExtract 扩展 r813 PrimeSim HSPICE .ma0族至 .ms0 multi-row domain + real DDR6 WTM training-mode Verilog pattern excerpts WtmFileReview+WtmPatternDirReview+WtmWriteArrayScope+ZqPatternTimingAnalyze 新家族 扩展 r822 verilog vecgen族至 WTM pattern-review 域 + reframe self-declares provenance WtmStructReview 承 r819 SpTemplateOpt/r823 WlvlShmooLoopAnalyze 族) / track≠asset_provenance 3 例 (累计 51→54: WtmCrcInjectionAudit track=faithful 但 synth_deck 重建 .v + WtmStructReview track=faithful 但 synth_deck 自包含合成 .v + WtmDanglingElseMre0Diag track=faithful 但 synth_data 重建 log+.v; WvFmFreqExtract track=synthesized 与 asset synth_deck 一致 非 track≠; WvModalPopupTclFix track=None 非 track≠) / synth_deck 4 例 (WtmCrcInjectionAudit faithful reconstruction .v+A_only marker + WtmStructReview 自包含合成 .v reframe self-declares synth + WvFmFreqExtract synth WDF FM 波形 track=synthesized + WvModalPopupTclFix 重建 buggy TCL context harness reframe) / synth_data 1 例 (WtmDanglingElseMre0Diag 重建 xrun.log excerpt + .v faithful reconstruction)\n")
        f.write("# 收口: miss 13->0, 全 395 case asset_fidelity 标完 (382+13=395). 档2 asset_fidelity backfill 全量收口 (r801-r824, 24 batch, +289, 106→395)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 382->395 (cases/B 395==B.jsonl 395 ✓); miss 13->0\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
