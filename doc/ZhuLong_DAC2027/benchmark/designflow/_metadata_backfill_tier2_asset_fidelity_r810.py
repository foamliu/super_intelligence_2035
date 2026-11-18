#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r810.py — r810 档2 asset_fidelity backfill batch10.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done. r806 batch6 (+12, 166→178) done.
      r807 batch7 (+12, 178→190) done. r808 batch8 (+12, 190→202) done.
      r809 batch9 (+12, 202→214) done.
      本轮 r810 推进 档2 batch10 — 12 cases
      (alphabetical next 12 missing after r809 batch9 MR7PsdScopeAnalyze:
       ManualSectionExtract..ModelQaRefactorAnalyze, M 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r809 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 /
                    真实 scp 自内网 / 真实用户 paste / "reproduced faithfully" /
                    "faithful compact/trimmed representation" 标注 / 真实 export header banner /
                    task_spec 显式 "trace 原文件 verbatim" 标注 / 真实内网 /proj//apps//home//rundata/ 路径)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/PDK/model fixture / 合成 .md0/.lis/.mt0 仿真输出数据 /
                    合成 .sv/.v verilog/SystemVerilog testbench fixture (precedent: CbrForceMechanismExplain/CovBinMetaExtract)
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver +
      task_spec verbatim 标注。A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized /
      portability reframe / "样本"/"合成"/"self-contained sample" / "auto-generated stub" / "示例" /
      "(reconstructed from cline trace ...)" / desc 显式 "合成" / "示例" / placeholder foundry 名 / 无 verbatim 标注。

本批 12 case 判定:
  - 2 A-faithful (17%): MeaNetPathDiag / ModelQaRefactorAnalyze
  - 5 synth_deck: ManualSectionExtract(synth_doc)→见下 / MatrixRunDirExplain(synth_data)→见下 / McFailModeDiag /
                  McPvtVmEval / McVthSpVariantGen / MinpulseRewriteRun
  - 4 synth_data: McLisSnmExtractor / Md0MeasureExtract / MdMaskBeatZeroDiag / ModelLibVerDiff
  - 1 synth_doc:  ManualSectionExtract
  (详见 BATCH rationale; 实际分布: A-faithful=2, synth_deck=4, synth_data=4, synth_doc=1, synth_script=1 待校正)
  实际: A-faithful=2 / synth_deck=4 (McFailModeDiag,McPvtVmEval,McVthSpVariantGen,MinpulseRewriteRun) /
        synth_data=4 (McLisSnmExtractor,Md0MeasureExtract,MdMaskBeatZeroDiag,ModelLibVerDiff) /
        synth_doc=1 (ManualSectionExtract) / synth_script=0 / MatrixRunDirExplain=synth_data ⇒ synth_data=5
  最终分布: A-faithful=2 / synth_deck=4 / synth_data=5 / synth_doc=1 (合计 12)

关键发现:
  - task_spec 显式 "trace 原文件 verbatim" 标注首例 (ModelQaRefactorAnalyze):
    task_spec.json 字段 doc/runModelQA.pl = "真实旧脚本 (3042 行, 137700 字节) — trace 原文件 verbatim" +
    doc/runModelQA_new.pl = "真实新脚本 (1630 行, 60390 字节) — trace 原文件 verbatim"; 两份 Perl 生产脚本
    含真实内部 /apps/imctf/cad/script/Frontend/mqv/cxmt_spiceMeasurementDataConvert.pm require 路径 +
    真实 version history (Frank 2019 / Yao Yao 2019-2020 / Lulu 2021-2022); reframe 原标 "合成 Perl fixture"
    被 task_spec verbatim 标注 + 真实 /apps 内网路径证伪 ⇒ 改判 A-faithful (file-verbatim, Perl 生产脚本首例)。
    本例证: reframe_note 的 "合成/便携化" 措辞不可单独采信, 须交叉 task_spec verbatim 标注 + 文件内真实内网路径。
  - 真实 DSPF fragment + 真实 foundry SRAM compiler 名强信号 (MeaNetPathDiag):
    io_d0_template.sp 含真实 /proj/lacaa/V0/model/current_PF_v0d1_Rev03/hspice/model.lib 内网路径 +
    真实节点名 SAEB/DLPCHB/BLPCHB/BL_D/BL_T; dspf_fragment.sp header 含真实 foundry SRAM compiler 实例名
    HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1 (CXN 高密度 1-port SRAM compiler) + 真实 DSPF *|I 单 x net 名;
    track=faithful (与 asset 一致); 无 stub/synthetic 标记 ⇒ A-faithful (file-verbatim, 真实 DSPF + .sp 首例)。
  - placeholder foundry 名 "DBCFS" 证伪 reframe verbatim 标注首例 (ModelLibVerDiff):
    reframe 原标 "A=trace-verbatim(.lib)"; 但 rev05_old.lib/rev06_new.lib header 均含 placeholder foundry 名
    "DBCFS" (非真实 CXMT/TSMC) + 902 字节极小 (真实 PDK model.lib 通常 KB-MB, 含数十 .model) ⇒ 合成最小重建
    for PDK 保密/portability ⇒ 改判 synth_data (refinement over reframe)。本例证: reframe "trace-verbatim" 标注
    须用文件实际内容 (placeholder 名 / 文件体积 / .model 数) 交叉验证。
  - "auto-generated stub" 显式合成标记 + 真实 /proj 路径嵌入 (MinpulseRewriteRun):
    minpulse_*.sp header 显式 "* auto-generated stub for model-path rewrite exercise", body 含真实 /proj/ddgoa/V0/model/current/
    路径 (待替换串) + 合成 RC 电路 (vsrc/r1/c1, model-free); local_model.sp = 57 字节 "* local empty model stub";
    track=faithful (指 prompt verbatim 用户原话), asset=合成 stub ⇒ track≠asset_provenance (累计 14→15, 同 r809 LibCellListGen
    主模式 track=faithful 记 prompt + asset portability 合成); synth_deck (合成 SPICE deck stub)。
  - 合成 HSPICE .lis (无 export banner) vs 真实 HSPICE .lis (有 PrimeSim export banner) 二分 (McLisSnmExtractor):
    mc_sim_A.lis header 仅 "* HSPICE Monte Carlo simulation output (6T SRAM bitcell)" 注释, 无 PrimeSim HSPICE V-2023.12
    export banner + 无真实 user/host/timestamp/license (与 r809 LisMeasExtract 真实 .lis export header 反向);
    desc 显式 "示例 HSPICE MC .lis" ⇒ synth_data (合成 .lis 仿真输出数据, 与 r809 LisMeasExtract A-faithful 形成对照)。
  - 合成 SystemVerilog testbench fixture 沿用 synth_data (precedent) (MdMaskBeatZeroDiag):
    ddr6_tasks.sv header "// ddr6_tasks.sv (excerpt) — DDR6 DSCQA vecgen testbench task library" + 真实 /proj/dscqa
    source path, 但无 (user@host, trace) marker (与 r809 LoadModeOpTruncDiag A-faithful "real excerpt from ... (tongfanl@hfhds201, trace ...)" 反向);
    reframe 显式 "合成 sv fixture"; 沿用既有 precedent (CbrForceMechanismExplain proj_monitors.sv = synth_data /
    CovBinMetaExtract constraint_timing_coverage.sv = synth_data) ⇒ synth_data (合成 SV testbench, 非 synth_script)。
  - 合成 Aether 手册章节 (synth_doc 首例 of batch10) (ManualSectionExtract):
    doc/section.md 含真实 Aether 手册结构 "Aether Reference Manual, 2025.09.sp1.hf7" + page 264-265 + OCR ligature ﬁ/ﬂ,
    但 track=synthesized + reframe 显式 "真实 Aether DM 手册(内网 OCR 片段) SUT 沙盒不可达 -> 用自包含合成 section.md"
    ⇒ 合成手册章节重建 (reframe 原标 synth_data, refined to synth_doc per canonical vocabulary "合成 doc/manual/knowledge 摘录")。
  - 合成 FineSimPro .md0 measure 输出 (Md0MeasureExtract):
    md0_A = 12 个 .md0 文件 (6 measure x 2 devkey), reframe 显式 "用自包含合成真实 .md0 measure 文件资产"; .md0 = measure
    输出数据 (非 error log) ⇒ synth_data (合成 .md0 measure 数据, 与 r809 LisMeasExtract .lis 解析同域不同格式)。
  - 合成 MC run 输出 bundle + 合成 stub deck (McFailModeDiag):
    mc_runs_A = 8 run 子目录 (run.log/result.mt0/status.json) 合成 MC run 输出 + summary_A.json 合成聚合 (故意不一致 Bug#1) +
    deck_A.sp = 237 字节合成 stub "tt_-40_0.675.sp"; reframe 标 synth_deck; 主输入 = MC run data, deck 为 "仅供参考" context;
    按 reframe 判 synth_deck (deck 是 EDA artifact, run data 配套)。
  - 合成 SPICE deck template + 合成 vm_target.csv (McPvtVmEval):
    template.sp 合成 deck 模板 + vm_target.csv 合成 PVT 角目标表; reframe 显式 "私有 template.sp + netlist 在 .75 不可便携"
    + "asset_fidelity 缺标应 synth_deck" ⇒ synth_deck (合成 SPICE deck template)。
  - 合成 sense-amp deck + 合成 MC vth 数据 (McVthSpVariantGen):
    base.sp 合成 DRGQA BL10 sense-amp deck + vth.mt0 合成 MC vth 数据 (100 行); track=synthesized ⇒ synth_deck (合成 SPICE deck)。
  - 合成 sim 目录树 JSON bundle (MatrixRunDirExplain):
    sim/{dir_listing,corner_listing,script_summaries,split_meta}.json + map_define.txt 合成 MatrixRun 目录结构数据;
    reframe 显式 "用自包含合成 dir_listing.json/corner_listing.json 保留真实任务结构(asset_fidelity=synth_data)" ⇒ synth_data
    (合成目录树 JSON bundle)。
  - track≠asset_provenance 本批 2 例 (累计 14→16): MinpulseRewriteRun (track=faithful 记 prompt verbatim / asset=合成 stub) +
    ManualSectionExtract (track=synthesized 记 asset 合成 / prompt=真实用户原话 verbatim t0002614@hfeg0pkn004 — 反向, track 记 asset)
  - A-faithful 2/12=17% (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6,r807=8,r808=4,r809=5,r810=2) 累计 47/120=39%
  - 强信号类型本批新增 1 类 (task_spec "trace 原文件 verbatim" 显式标注), 维持 export header 族 + 真实 DSPF + 真实 foundry SRAM compiler 名 +
    真实内网 /proj//apps/ 路径群 + placeholder foundry 证伪 + auto-generated stub 标记
"""
import json
import os

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-ManualSectionExtract-001": (
        "synth_doc",
        "doc/section.md = 合成 Aether Reference Manual 手册章节重建 (含真实 Aether 手册结构 'Aether Reference Manual, "
        "2025.09.sp1.hf7' + page 264-265 + OCR ligature ﬁ/ﬂ + Figure 2.4/Example 2.3 + ChargePump/cp_amp 示例 + view types 列表, "
        "6607 字节/41 行); section_meta.txt = 合成 manual_name/source_file/tool_name 元数据; task_spec.json = 合成 task-spec; "
        "track=synthesized (显式标合成); reframe='Aether 手册网表抽取章节提取->produce (portability+Q&A-how-to->produce-script "
        "reframe, §4 有牙必要, r733)': '真实 Aether DM 手册(内网 OCR 片段) SUT 沙盒不可达 -> 用自包含合成 section.md 保留真实任务结构"
        "(asset_fidelity=synth_data, 待 @A apply 标)'; "
        "prompt.txt = 真实用户原话 verbatim (t0002614 @ hfeg0pkn004, '我想从DRAM的design中抽取一个BLSA和BL上的loading出来做仿真，怎样抽取网表最方便' + "
        "'Aether中在DM界面查看view，其中config view的作用是什么'); "
        "track≠asset_provenance (track=synthesized 记 asset 合成, prompt=真实用户原话 verbatim — 反向: track 记 asset 非 prompt); "
        "合成 Aether 手册章节重建 (真实手册结构 + reframe 显式 '自包含合成 section.md', 内网 OCR 不可达) ⇒ synth_doc "
        "(refinement over reframe synth_data → synth_doc per canonical vocabulary '合成 doc/manual/knowledge 摘录 fixture', Aether 手册首例)",
    ),
    "EDA-Eval-DesignFlow-MatrixRunDirExplain-001": (
        "synth_data",
        "sim/dir_listing.json / corner_listing.json / script_summaries.json / split_meta.json = 合成 MatrixRun 目录结构数据 bundle "
        "(dir_listing=根目录 294 entries, corner_listing=primesim.* corner 子目录文件清单, script_summaries=01_-05_ 编号流程脚本 docstring, "
        "split_meta=裸 split 碎片 size/head); map_define.txt = 合成 map define; task_spec.json = 合成 task-spec; "
        "track=None; reframe='MatrixRun 目录文件解释->produce (portability+Q&A->produce reframe, §4 有牙必要, r732)': "
        "'真实 /rundata MatrixRun 目录 SUT 沙盒不可达 -> 用自包含合成 dir_listing.json/corner_listing.json 保留真实任务结构(asset_fidelity=synth_data)'; "
        "prompt.txt = 真实用户原话 verbatim (johnl @ hfeg0pkn001, 真实 /rundata/drcoa/V0/simdir/finesim/drcoaF/MatrixRun/MatrixRun_Netlist_SpfBA_20260807PM_mBist 内网路径 + "
        "verbatim '你看下这些文件什么意思'); "
        "合成 MatrixRun 目录结构 JSON bundle (reframe 显式 '自包含合成', 真实 /rundata 目录不可达) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-McFailModeDiag-001": (
        "synth_deck",
        "mc_runs_A = 合成 8 MC/corner run 子目录 (arun_01..arun_08, 每条 run.log/result.mt0/status.json, 本批 A per-run 全 failed 多种模式, "
        "summary_A 报 yield=inf/n_pass=8 = trace Bug#1 状态/聚合不一致); summary_A.json = 合成聚合结果 (与 per-run 故意不一致); "
        "deck_A.sp = 合成 stub deck (237 字节/10 行, '* tt_-40_0.675.sp TT corner -40C VVDD=0.825' + .include option_hspice.sp/pwr.sp/switch.sp/"
        "sram_bitcell_netlist.sp + .DC sweep monte=1, desc 显式 'A testbench 上下文（仅供参考）'); prompt.txt = 真实用户原话 verbatim; task_brief.md = 交付接口; "
        "track=synthesized (显式标合成); reframe='Monte Carlo 失败模式 + 状态聚合一致性诊断器->produce-tool (analysis/Q&A->produce-tool, r742)': "
        "'asset_fidelity 缺标应 synth_deck (B 档 synthesized run fixtures, 待 @A apply 档2)'; "
        "合成 MC run fixtures + 合成 stub deck (reframe 标 synth_deck, deck 是 EDA artifact, run data 配套; track=synthesized) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-McLisSnmExtractor-001": (
        "synth_data",
        "mc_sim_A.lis = 合成 HSPICE MC .lis 仿真输出 (117827 字节, header 仅 '* HSPICE Monte Carlo simulation output (6T SRAM bitcell) / "
        "* DC butterfly sweep for RSNM/HSNM, 6 MC samples' 注释, 无 PrimeSim HSPICE export banner + 无真实 user/host/timestamp/license — "
        "与 r809 LisMeasExtract 真实 .lis PrimeSim HSPICE V-2023.12-SP1-1 export banner 反向; desc 显式 '示例 HSPICE MC .lis（Input A）：6T SRAM bitcell DC butterfly sweep，6 个 MC 样本'); "
        "task_context.md = 真实场景用户原话 (e0030760 5000-MC HSPICE .lis 蝶形分析 + bootstrap 死锁 fix) + .lis 格式说明 + SNM Seevinck 定义; "
        "track=None; reframe=None; layer=L2; "
        "合成 HSPICE .lis (无 export banner + desc 显式 '示例', 与 r809 LisMeasExtract A-faithful 真实 .lis 形成对照) ⇒ synth_data (合成 .lis 仿真输出数据)",
    ),
    "EDA-Eval-DesignFlow-McPvtVmEval-001": (
        "synth_deck",
        "template.sp = 合成 SPICE deck 模板 (含 .inc netlist / .measure VMLH_rst0/VMHL_rst0 / .param ptemp/pvcc/pvintbus/mis_flag/sigmaflag / "
        ".lib model.sp corner / .tran / .data data_scan 块); vm_target.csv = 合成 PVT 角目标表 (5 corner: TT 0.8V/25C, SS 0.83V/-40C, SS 0.9V/-40C, "
        "FF 0.61V/130C, FF 0.74V/130C, 列 corner/voltage/temp/vm_min/vm_max/vmhl_shift); task_brief.md = 交付接口; output_format_spec.txt = 输出格式规范; "
        "track=None; reframe='PVT 蒙卡 Vm 评估 deck 生成器->produce-tool (portability produce-action->produce-tool, r742)': "
        "'私有 template.sp + netlist 在 .75 不可便携 -> case 抽取 synth template + 按 vm_target.csv 生成 mc_<tag>.sp deck ... asset_fidelity 缺标应 synth_deck'; "
        "prompt.txt = 真实用户原话 verbatim (reedchen @ hfeg0plg93, 真实 /proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_work_TB_domino_Receiver_rst0_stephens_schematic_ALPS/ 内网路径 + "
        "verbatim '我现在希望你在这个目录下帮我跑多个 PVT 的蒙卡仿真，并且收集 Vm 数据评估达标成果'); "
        "合成 SPICE deck template + 合成 vm_target.csv (reframe 显式 '私有 template.sp 不可便携', portability 合成) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-McVthSpVariantGen-001": (
        "synth_deck",
        "base.sp = 合成 DRGQA BL10 sense-amp HSPICE 仿真 deck (d0_bl10_m0.sp, 含 4 条 .param delvtoBL0_{NsL,NsR,PsL,PsR} 失配量 + "
        ".inc 网表/模型 + .tran/.measure/.print); vth.mt0 = 合成 Monte-Carlo vth 数据 (前 3 行头注释 + 第 4 行起 100 行, cols index/vth_NsL/vth_NsR/vth_PsL/vth_PsR); "
        "output_format_spec.txt = 输出格式说明; task_brief.md = 交付接口; "
        "track=synthesized (显式标合成); reframe=None; "
        "合成 sense-amp SPICE deck + 合成 MC vth 数据 (track=synthesized, portability 合成) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-Md0MeasureExtract-001": (
        "synth_data",
        "md0_A = 合成 FineSimPro .md0 measure 输出测试树 (6 子目录 vtgm/vtsat/vtlin/idsat/idlin/ioff x 2 devkey ntn/ptn = 12 个 .md0 文件, "
        "来自 rongjiez cline trace, desc 显式 '需解析提取 measure 值并按类型计算 normalized'); task_brief.md = 交付接口 (脚本打进 outputs/submit.zip, "
        "运行 python3 <脚本>.py <md0_dir> <output_csv>, 输出 CSV 列 devkey/corner/temp/vdd/type/total/normalized); "
        "track=faithful (指 prompt verbatim); reframe='ModelQA .md0 measure 解析扩展->produce-tool (portability+produce-action→produce-tool, r734)': "
        "'真实 Perl 生产脚本+HSPICE .md0 输出 SUT 沙盒不可达 -> 用自包含合成真实 .md0 measure 文件资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2)'; "
        "prompt.txt = 真实用户原话 verbatim (rongjiez @ hfhds201, 真实 /home/rongjiez/jira_dev/mpqa/mp_1/scripts/runModelQA_new.pl 内网路径 + "
        "verbatim Perl 代码修改请求 vtgm/vtsat/vtlin/idsat/idlin/ioff + normalized 公式); "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 .md0); "
        "合成 FineSimPro .md0 measure 输出 (reframe 显式 '自包含合成真实 .md0 measure 文件', 真实 .md0 不可达; .md0 = measure 数据非 error log) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-MdMaskBeatZeroDiag-001": (
        "synth_data",
        "ddr6_tasks.sv = 合成 DDR6 DSCQA vecgen testbench task library (7632 字节/148 行, header '// ddr6_tasks.sv (excerpt) — DDR6 DSCQA vecgen testbench task library / "
        "// Source: /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen/ddr6_tasks.sv' + 真实 /proj/dscqa source path, 但无 (user@host, trace) marker — "
        "与 r809 LoadModeOpTruncDiag A-faithful 'real excerpt from DDR6 WTM pattern (tongfanl@hfhds201, trace ...)' 反向; "
        "body 含 write_mem_arr (with md_mask defs) / read_mem_arr / wr_reorganize_dq / rd_reorganize_dq tasks, params X1P6 mode DQ_BITS=6/MAX_BURST_LEN=24/bl=24); "
        "task_brief.md = 交付接口; "
        "track=faithful (指 prompt verbatim); reframe='DDR6 DSCQA vecgen md_mask beats 16-23 期望 0 解析器->produce-tool (portability+debug-Q&A->produce-tool, r739)': "
        "'真实 vecgen 代码生产文件 SUT 沙盒不可达 -> 用真实场景便携化的合成 sv fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2)'; "
        "prompt.txt = verbatim 用户原话 '帮我解析下ddr6_test.sv文件，告诉我为啥在CRC没开的时候+MD_8b+1P6时，PSD0的dq5的D16-D23位期望值是0？' (dandans @ hfhds201); "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 sv fixture); "
        "合成 SystemVerilog testbench fixture (reframe 显式 '合成 sv fixture', 无 verbatim marker; 沿用 precedent CbrForceMechanismExplain proj_monitors.sv = synth_data / "
        "CovBinMetaExtract constraint_timing_coverage.sv = synth_data, 合成 .sv/.v → synth_data 非 synth_script) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-MeaNetPathDiag-001": (
        "A-faithful",
        "io_d0_template_A/io_d0_template.sp = 真实用户 SPICE testbench (1241 字节/32 行, header '* SRAM sense-amp characterization testbench (A) / "
        "* io_d0_template.sp (broken: .measure node paths use double-x instance path)' + 真实内网路径 .lib '/proj/lacaa/V0/model/current_PF_v0d1_Rev03/hspice/model.lib' ss_mos_varactor_fs + "
        ".inc 'dspf_fragment.sp' + .temp -40 + .param high=0.675 diff=0.1 + 真实节点名 vsacp SAEB/vsacn DLPCHB/vblp BLPCHB/vbl_d BL_D/vbl_t BL_T + .measure v(xtop.xxsa[1].mpmyrc:s) 双 x 实例路径 (broken bug)); "
        "io_d0_template_A/dspf_fragment.sp = 真实 DSPF fragment (header '* DSPF extraction fragment (A) / * HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.dspf.TYPICAL_25' + "
        "真实 foundry SRAM compiler 实例名 HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1 (CXN 高密度 1-port SRAM compiler) + 真实 DSPF *|I 单 x net 名 XTOP.XSA[1].MPMYRC:s/MPMYRT:s/MNMSAC:d/MNMSAT:d/XTOP.GBL[1]/XTOP.SAEB/DLPCHB/BLPCHB); "
        "prompt.txt = verbatim 用户原话 '为什么我sp文件中的mea语句没法提取相应的数值？' (shanliny @ hfeg0pkn001, sess 1793234226913_xtse5 mc43); task_brief.md = 交付接口; "
        "track=faithful (与 asset 一致); reframe='.meas 节点路径器件实例名 vs net 名错配诊断器->produce-tool (Q&A debug-Q&A->produce-tool, r747)': 'asset_fidelity 缺标应 A=trace-verbatim(.sp+.dspf)+B=synth'; "
        "真实用户 .sp (真实 /proj/lacaa 内网路径 + 真实 foundry model.lib reference + 真实节点名) + 真实 DSPF fragment (真实 foundry SRAM compiler 名 + 真实 DSPF *|I net 名), 无 stub/synthetic 标记 ⇒ file-verbatim (A-faithful, 真实 DSPF + .sp 首例)",
    ),
    "EDA-Eval-DesignFlow-MinpulseRewriteRun-001": (
        "synth_deck",
        "rc_delay/Dlyrc_{Pre,r1c,vdly,vint_Pre}/minpulse_spf/minpulse_{01..08}.sp = 合成 SPICE deck stub 群 (每文件 header 显式 '* minpulse_spf deck: minpulse_XX.sp / "
        "* auto-generated stub for model-path rewrite exercise', body 含真实 /proj/ddgoa/V0/model/current/{model.sp,incFile_lp,param.sp,corner/typical.sp,corner/ss.sp} 路径 (待替换串) + "
        "合成 RC 电路 vsrc/r1 1k/c1 1p + .tran 1n 100n + .measure tran vpk/tpd + .end, model-free); local_model.sp = 合成 stub (57 字节 '* local empty model stub (no devices needed for RC deck)'); "
        "prompt.txt = verbatim 用户原话 (berylwu, 真实 /proj/commonIP/analog/v1_hl/lp5/v0/simdir/anasim/berylwu/ddgoa/rc_delay 内网路径 + verbatim 'Dlyrc开头的几个文件夹下的minpulse_spf目录下的sp文件，替换里面的Old string ... New string ... 并直接run所有替换后的激励'); task_brief.md = 交付接口 (replace_and_run.py 递归扫描 + 替换 + submit.sh + replace_report.json); "
        "track=faithful (指 prompt verbatim); reframe=None; layer=L2; "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 'auto-generated stub' deck, 真实 /proj 路径嵌入待替换串); "
        "合成 SPICE deck stub 群 (header 显式 'auto-generated stub', 真实 /proj 路径作待替换串嵌入, 与 r809 LibCellListGen track≠asset_provenance 同型) ⇒ synth_deck",
    ),
    "EDA-Eval-DesignFlow-ModelLibVerDiff-001": (
        "synth_data",
        "model_libs_A/rev05_old.lib = 合成 PDK HSPICE model library 重建 (902 字节/20 行, header '* PDK 35H_DBCFS Model Library / * Version: v0d1_Rev05 / * Date: 2026-06-15 / "
        "* Foundry: DBCFS / * Process: 35nm / * Corner: TT' + placeholder foundry 名 'DBCFS' (非真实 CXMT/TSMC, 35nm) + 4 .model nch_core/pch_core/nch_rf/pch_rf + IO 5.0V nio_5p0, 极小); "
        "model_libs_A/rev06_new.lib = 合成 PDK HSPICE model library 重建 (header '* Version: v0d01_Rev06 / * Date: 2026-09-20 / * Foundry: DBCFS' + nch_core vth0=0.44 微调); "
        "track=faithful (指 prompt verbatim); reframe='PDK HSPICE model.lib 版本结构化 diff 报告器->produce-tool (Q&A explain-Q&A->produce-tool, r747)': 'asset_fidelity 缺标应 A=trace-verbatim(.lib)+B=synth'; "
        "prompt = verbatim 用户原话 'ev06（新）与 Rev05（旧）的区别在那里 就是具体的区别 参数变了 还是什么更改了' (e0024852 @ hfeg0plg79, sess 1792653194974_s2f9d mc294); "
        "track≠asset_provenance (track=faithful 记 prompt verbatim, asset=合成 .lib 重建); "
        "合成 PDK model library 重建 (placeholder foundry 名 'DBCFS' 证伪 reframe 'trace-verbatim' 标注 + 902 字节极小 — 真实 PDK model.lib 通常 KB-MB 含数十 .model, "
        "PDK 保密/portability 合成最小重建; refinement over reframe A=trace-verbatim → synth_data, placeholder foundry 证伪首例) ⇒ synth_data",
    ),
    "EDA-Eval-DesignFlow-ModelQaRefactorAnalyze-001": (
        "A-faithful",
        "doc/runModelQA.pl = 真实生产 Perl 脚本 verbatim (137700 字节/3042 行, #!/apps/local/bin/perl + 真实 version history Frank 2019-01-31 / Yao Yao 2019-04-25/2020-05-12/2020-05-19 / "
        "Lulu 2021-02-25/2022-05-25 + use warnings/strict/POSIX/Getopt::Long/Term::ANSIColor; task_spec.json 显式 '真实旧脚本 (3042 行, 137700 字节) — trace 原文件 verbatim'); "
        "doc/runModelQA_new.pl = 真实生产 Perl 脚本 verbatim (60390 字节/1630 行, #!/apps/local/bin/perl + 真实内网 require '/apps/imctf/cad/script/Frontend/mqv/cxmt_spiceMeasurementDataConvert.pm' + "
        "use Excel::Writer::XLSX/Data::Dumper/Cwd + $simulator='finesim' + 全局变量 cfg/runDir/runMethod/model 等; task_spec.json 显式 '真实新脚本 (1630 行, 60390 字节) — trace 原文件 verbatim'); "
        "task_spec.json = task-spec (含 verbatim 标注); "
        "track=None; reframe='runModelQA.pl 旧/新重构六维创新分析器->produce-tool (portability+analysis/Q&A->produce-tool, r739)': '真实 runModelQA.pl 生产文件 SUT 沙盒不可达 -> "
        "用真实场景便携化的合成 Perl fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2)'; "
        "prompt = 真实用户原话 verbatim (rongjiez @ hfeg0pkn005, 'runModelQA_new.pl 是我对原始代码 runModelQA.pl 进行重构得到的新代码，请你仔细分析这两个文件，给出我的新代码的技术突破与创新...'); "
        "真实生产 Perl 脚本 verbatim (task_spec 显式 'trace 原文件 verbatim' 标注 + 真实内网 /apps/imctf require 路径 + 真实 version history, "
        "reframe 原标 '合成 Perl fixture' 被 task_spec verbatim 标注 + 真实 /apps 内网路径证伪 ⇒ 改判 A-faithful; refinement over reframe synth_script → A-faithful, "
        "task_spec verbatim 标注交叉验证首例) ⇒ file-verbatim (A-faithful, Perl 生产脚本 verbatim 首例)",
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

    print("=== 档2 asset_fidelity backfill r810 batch10 ===")
    print("to apply:", len(BATCH), "| applied:", len(applied), "| skipped:", len(skipped))
    print("coverage: before=%d -> after=%d (delta=+%d)" % (before, before + len(applied), len(applied)))
    print("\n--- applied ---")
    for cid, val in applied:
        print("  APPLIED  %-58s -> %s" % (cid, val))
    if skipped:
        print("\n--- skipped ---")
        for cid, reason in skipped:
            print("  SKIPPED  %-58s : %s" % (cid, reason))

    from collections import Counter
    dist = Counter(v for _, v in applied)
    print("\n--- value distribution ---")
    for v, c in sorted(dist.items()):
        print("  %-14s : %d" % (v, c))

    # write manifest
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r810_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r810_manifest.tsv — r810 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch10 (12 cases, alphabetical next 12 missing after r809 batch9 MR7PsdScopeAnalyze: ManualSectionExtract..ModelQaRefactorAnalyze, M 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r809 档2 batch1-9 (+108, 106→214) done. 本轮 r810 档2 batch10.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注; A-faithful 强信号 = 真实 export header / 真实内网路径 / task_spec 显式 'trace 原文件 verbatim' / 真实 foundry SRAM compiler 名 / verbatim excerpt with file:line / 无 stub/synthetic 标记\n")
        f.write("# 关键发现: task_spec 显式 'trace 原文件 verbatim' 标注首例 (ModelQaRefactorAnalyze, 改判 A-faithful, reframe '合成' 证伪) / 真实 DSPF fragment + 真实 foundry SRAM compiler 名 (MeaNetPathDiag, A-faithful) / placeholder foundry 名 'DBCFS' 证伪 reframe verbatim 首例 (ModelLibVerDiff, 改判 synth_data) / 'auto-generated stub' + 真实 /proj 路径嵌入 (MinpulseRewriteRun, synth_deck) / 合成 .lis 无 export banner vs 真实 .lis (McLisSnmExtractor, synth_data, 与 r809 LisMeasExtract A-faithful 对照) / 合成 .sv 沿用 synth_data precedent (MdMaskBeatZeroDiag) / synth_doc 首例 of batch10 (ManualSectionExtract, Aether 手册重建) / track≠asset_provenance 本批 4 例 (累计 14→18: MinpulseRewriteRun/Md0MeasureExtract/MdMaskBeatZeroDiag/ModelLibVerDiff 均 track=faithful 记 prompt verbatim + asset 合成) + 1 反向 (ManualSectionExtract track=synthesized 记 asset 合成 + prompt verbatim, 累计 reverse 1) / A-faithful 2/12=17% 累计 47/120=39% / 强信号新增 1 类 (task_spec verbatim 标注)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 214->226 (cases/B 226==B.jsonl 226 ✓); miss 181->169\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
