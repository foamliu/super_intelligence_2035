#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r816.py — r816 档2 asset_fidelity backfill batch16.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r815 档2 batch1-15 (+168, 106→286) done. 本轮 r816 推进 档2 batch16 — 12 cases
      (alphabetical next 12 missing after r815 batch15 SaDcSweepTbGen:
       SaNPsimDiag..SimConfigEditReport, S→Sim 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r815 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 真实 scp /
                    真实 export header banner / desc 显式 "A-faithful"/"real trace"/"逐字" 标注 /
                    真实内网 /proj//apps//home//rundata 路径 / 真实 SKILL .il template / 真实 Perl
                    vecgen / 真实 buggy 脚本 with bug docstring / 真实 verbatim agent 回答)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice/testbench/FineSim-input 样本 (portability,
                    真实 deck 在 /proj 内网不可达) / "trace-faithful reconstruction" header + decoy
  - synth_script : A = 合成 Perl/Python/Tcl/bash/shell 脚本 fixture
  - synth_data   : A = 合成 JSON/state/config/data/PDK/model/.lis/.mt0/.bisec_mt0 仿真输出 fixture /
                    合成 spec/params fixture (deck 为 OUTPUT 时 spec 为输入) / 合成 lib list /
                    合成 .lis 仿真输出 (Chinese synth header + real /proj path embedded)
  - synth_log    : A = 合成仿真器错误日志/输出日志 fixture (含 real-format export banner faithful mimicry)
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture (multi-project Applications_Library tree)
  - no-asset     : 0 attachment (Q&A)

本批 12 case 判定:
  - 0 A-faithful (0%) — S→Sim 段 synth-heavy, 全 12 case asset 合成, 无真实 trace-verbatim 资产
  - 2 synth_deck: ShrinkExtract / SiInpTokenRm
  - 1 synth_script: SetNetlistParam
  - 1 synth_tree: SentaurusDeckSetupSummary
  - 2 synth_log: SaNPsimDiag / SiOutWarnDiag
  - 6 synth_data: SarAdc8bNetlistGen / SenseMarginAnalysis / SharedLibDeployFix /
                  ShmooCfgParser / SimCapLisParse / SimConfigEditReport

关键发现:
  - A-faithful 0% (0/12) 单批最低 (r815 累计 78/180=43.3%; 本批 S→Sim 段全 synth, 无真实
    trace-verbatim 资产). 累计 78/192=40.6%.
  - synth_tree 1 例 (SentaurusDeckSetupSummary): 合成 Applications_Library 多项目目录树
    (GettingStarted/sdevice/AC + Templates/NMOS + FinFET/FinFET_10nm 3 项目类, 含 _des.cmd
    sdevice decks + _vis.tcl + .par + .prf + gtree.dat); reframe_note 原标 synth_deck 但 asset
    是多项目目录树 ⇒ synth_tree 更精确 (tree contains sdevice decks but asset is the tree
    structure being summarized; 扩展 r801 synth_tree vocab).
  - synth_script 1 例 (SetNetlistParam): 合成 Run_Compress_Netlist shell 脚本 (testdir_A/).
  - real-format export banner faithful format mimicry 2 例:
    * SaNPsimDiag sanp_result_A.log real FineSim banner "FineSim (R) Version V-2023.12-1"
    * SiOutWarnDiag si_A.out real PrimeSim banner "PrimeSim Version X-2025.06-SP2-2"
    (both synth per reframe_note portability reframe; 扩展 r811/r815 export banner 强信号族
     至 FineSim+PrimeSim sim-output-log faithful mimicry).
  - track≠asset_provenance 5 例 (累计 26→31): SetNetlistParam/SharedLibDeployFix/ShrinkExtract/
    SiInpTokenRm/SiOutWarnDiag (all track=faithful prompt verbatim 但 asset synth; portability
    reframe 真实 FineSim/HSPICE/SKILL/Perl/model 环境不可达).
  - FineSim input deck 子型 (SiInpTokenRm): si.inp with .option finesim_ignore line, 8 subdir
    matrix_run_A/runA_000..007 — FineSim MatrixRun 多子目录结构 (合成 FineSim deck).
  - decoy comment trap (ShrinkExtract): incFile_A "* SHRINK = 9.999 ... must SKIP it" decoy
    comment (扩展 r811 decoy distractor 至 SPICE include file comment).
  - real /proj path embedded in synth .lis (SimCapLisParse): result_wibls.lis 真实
    /proj/drdxp/V0/model/current_PF_v0d1_Rev06/model.sp 路径 但 Chinese synth header
    "****** HSPICE仿真结果  result_wibls ******" (faithful structure mimicry, 非 real HSPICE
    export banner).
  - real P010/P004 lib 结构合成 (SharedLibDeployFix): needed_libs.txt reframe_note 'real-from-trace'
    = 结构来自 trace P010/P004 但文件合成 with decoy libfoo1-4 + glibc 系统库.
"""
import json, os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-SaNPsimDiag-001": (
        "synth_log",
        "sanp_result_A.log = 合成 FineSim 仿真日志 (header 含真实格式 FineSim export banner "
        "'FineSim (R) / Version V-2023.12-1 for linux64 - Jan 04, 2024 / Copyright (c) 2003 - 2024 "
        "by Synopsys, Inc.' 但 reframe_note 显式 '用自包含合成 sanp_result.log/...资产' — real-format "
        "FineSim banner 为 faithful format mimicry 非 real scp); Check_SaNP_tb_A.sp = 合成 FineSim "
        "testbench deck (header '*\\n**************** Info Reading ****************' .option "
        "PARHIER/REDEFSUB/gmin/DCON/runlvl, 无真实 export banner/无真实内网路径, 含 .trannoise "
        "malformed); Check_SaNP_tb_A.lis = 合成 PrimeSim HSPICE listing (第二次运行); "
        "Check_SaNP_tb_A.st0 = 合成 HSPICE 状态文件 (dcop tot_iter=125); run_A.sh = 合成 提交命令; "
        "task_brief.md = 交付接口 (sanp_diag.py <assets_dir> <out_json>); track=synthesized (与 "
        "asset 一致); layer=L1; prompt = 重构需求 (非 verbatim, 结构化任务描述 '我用 FineSim 跑了 "
        "一个 SRAM sense-amplifier 噪声性能仿真...请帮我分析这次仿真到底出了什么问题'); 合成仿真"
        "日志 group (3 sim-output logs .log/.lis/.st0 主导诊断输入 + 1 deck .sp 辅助上下文, "
        "real-format FineSim banner faithful mimicry) ⇒ synth_log (合成仿真器输出日志 fixture; "
        "诊断目标为 sim logs, .sp deck 为 supporting context; 与 r811 Mt0MetastabDiag real-banner "
        "但 synth 同型; track=synthesized 与 asset 一致)",
    ),
    "EDA-Eval-DesignFlow-SarAdc8bNetlistGen-001": (
        "synth_data",
        "spec.json = 合成 SAR ADC 8bit HSPICE 网表生成 spec (track=synthesized, 无 deck asset — "
        "deck 是 OUTPUT 非 input); task_brief.md = 交付接口; assets 仅 spec.json + task_brief.md "
        "(无 .sp/.netlist 资产, 用户任务=生成 sar_adc_8b.sp); track=synthesized (与 asset 一致); "
        "layer=L1; prompt = 重构需求 (金标准=assistant write_sar_adc.py 生成完整 8 位 SAR ADC "
        "HSPICE 网表); 合成 spec fixture (deck 为 OUTPUT, spec 为合成输入) ⇒ synth_data (合成 "
        "spec/params fixture; 与 r815 SaDcSweepTbGen 合成 spec 同型但本 case 无 deck asset, "
        "spec 是唯一输入)",
    ),
    "EDA-Eval-DesignFlow-SenseMarginAnalysis-001": (
        "synth_data",
        "sm_results.zip = 合成 DRAM Sense Margin 仿真结果集 (960 个 .bisec_mt0 文件, 每个 199B, "
        "目录树 sm_results/bla2/toc_2.0ns/cell0..cell11/D{0..11}_{mixb,mixw,offb,offw,senb,senw,"
        "sldb,sldw}.bisec_mt0 — 合成 .bisec_mt0 measurement data, 极小 199B/文件); task_brief.md "
        "= 交付接口; track=None (内容 合成 .bisec_mt0 measurement data, track=None 是缺 metadata "
        "非合成信号); layer=L2; prompt = 重构需求 (e0025730 SM characterization pipeline, 12 BLs × "
        "5 tOC × 2 cell × 8 pattern = 960 仿真); 合成 .bisec_mt0 measurement data fixture (960 文件 "
        "199B 极小, 量测数据 fixture) ⇒ synth_data (合成 .bisec_mt0 仿真输出 measurement data "
        "fixture; track=None 但内容极小合成; 与 r813 OtaMa0SpecCheck real .ma0 对比: 本 case 全合成)",
    ),
    "EDA-Eval-DesignFlow-SentaurusDeckSetupSummary-001": (
        "synth_tree",
        "Applications_Library/ = 合成 Sentaurus TCAD 多项目目录树 (3 项目类: GettingStarted/"
        "sdevice/AC/ + Templates/NMOS/ + FinFET/FinFET_10nm/, 每类含 _des.cmd sdevice deck + "
        "_vis.tcl + .par + .prf + gtree.dat + gtooldb.tcl + gcomments.dat + greadme.html); 无 "
        "prompt.txt (prompt 在 case json 'prompt' 字段); track=None; layer=L1; reframe_note 显式 "
        "'用自包含合成项目树(3 项目+sdevice_des.cmd+svisual_vis.tcl)保留真实任务结构(asset_fidelity"
        "=synth_deck)' — reframe_note 原标 synth_deck 但 asset 是多项目目录树 (3 top-level 项目类 "
        "GettingStarted/Templates/FinFET) 非 单 deck ⇒ synth_tree 更精确 (tree contains sdevice "
        "decks but the asset is the tree structure being summarized; 任务='总结新建 Sentaurus deck "
        "所需的常见文件' 即 遍历目录树归纳文件类型); prompt = 重构背景 (含 verbatim 用户原话摘录 "
        "'please study sentaurus deck examples under the folder: /apps/synopsys/sentaurus/V-2023.12/"
        "tcad/V-2023.12/Applications_Library, summari...'); 合成 Applications_Library 多项目目录树 "
        "⇒ synth_tree (合成样本目录树 fixture; 扩展 r801 synth_tree vocab; reframe_note 标 synth_deck "
        "但多项目目录树 ⇒ synth_tree 更精确)",
    ),
    "EDA-Eval-DesignFlow-SetNetlistParam-001": (
        "synth_script",
        "testdir_A/Run_Compress_Netlist = 合成 shell 脚本 (reframe_note 显式 '用自包含合成 "
        "Run_Compress_Netlist shell 脚本资产保留真实任务结构'; 用户任务=写 SKILL 修改该 shell 脚本"
        "中 Netlist 参数然后运行); task_brief.md = 交付接口 (set_netlist_param.py); track=faithful "
        "(与 asset 不一致, track=faithful 指 prompt verbatim 用户原话 但 asset 是合成 shell 脚本); "
        "layer=L1; prompt.txt = verbatim 用户原话 ('编写一个skill，用户指定 netlist 名称，SKILL 修改"
        "/rundata/drvqa/.../Run_Compress_Netlist shell 脚本中的 Netlist参数，然后运行该 shell 脚本"
        "执行转换' U#0 逐字, 真实 /rundata/drvqa 内网路径) 但附件 asset 是合成 shell 脚本 ⇒ "
        "synth_script (合成 shell 脚本 fixture; track=faithful 但 asset=synth_script ⇒ "
        "track≠asset_provenance; portability reframe 真实 SKILL/Virtuoso+Run_Compress_Netlist 不可达; "
        "与 r808 real-buggy-script 对比: 本 case 合成 shell 非 real buggy)",
    ),
    "EDA-Eval-DesignFlow-SharedLibDeployFix-001": (
        "synth_data",
        "needed_libs.txt = 合成共享库清单 (libdizo.so/libabseil_dll.so/libamd.so/libcamd.so/"
        "libcholmod.so/libstdc++.so.6/libnetcdf.so + decoy libfoo1-4.so + glibc 系统库 libc.so.6/"
        "ld-linux-x86-64.so.2/libm.so.6/libpthread.so.0; reframe_note 显式 '用真实 P010/P004 lib "
        "结构合成' — 结构来自 trace P010/P004 但文件合成 with decoy libfoo + glibc 系统库); "
        "task_brief.md = 交付接口 (fix_missing_libs.sh+setup_env.sh); track=faithful (与 asset "
        "不一致, track=faithful 指 prompt verbatim e0024852 原话含报错原文+路径 但 asset 是合成 "
        "lib list); layer=L1; prompt.txt = verbatim 用户原话 ('i run gxrc_t ... got error "
        "libdizo.so cannot open ... how to fix it' U0 逐字) 但附件 asset 是合成 lib list ⇒ "
        "synth_data (合成 lib list fixture; track=faithful 但 asset=synth_data ⇒ "
        "track≠asset_provenance; reframe_note 'real-from-trace' 指 lib 结构来自 trace 但文件合成; "
        "与 r815 ResistorTrimNetlistExplain 合成 spec 同型: 主资产是合成 data fixture)",
    ),
    "EDA-Eval-DesignFlow-ShmooCfgParser-001": (
        "synth_data",
        "shmoo.cfg = 合成 2D Shmoo 配置文件 (cxmtGen2DShmooFromWv.pl 流程 cfg); example_parse.json "
        "= 合成解析示例输出; task_brief.md = 交付接口; track=synthesized (与 asset 一致); layer=L1; "
        "prompt = 重构需求 (yanxvwei 2D Shmoo 流程, U#185 '使其能够输入shmoocfg文件', assistant "
        "tr0_to_wvshmoo.py); 合成 config + 合成 example output (track=synthesized 显式) ⇒ synth_data "
        "(合成 config fixture; 与 r815 ShmooCfgParser 同型 config 解析任务; track=synthesized 与 "
        "asset 一致)",
    ),
    "EDA-Eval-DesignFlow-ShrinkExtract-001": (
        "synth_deck",
        "model_A.sp = 合成 SPICE model deck (header '* SPICE model file for MPQA (visible input A)' "
        "— 描述性 'A' header, 无真实 export banner/无真实内网路径, .lib tt + .lib 'incFile_A' "
        "mos_tt + .lib 'incFile_SS' ss + .subckt inv); incFile_A = 合成 include 文件 (header 含 "
        "decoy comment '* SHRINK = 9.999 ... The line above is a SPICE comment decoy: a correct "
        "solution must SKIP it' — decoy comment trap); cfg_A = 合成 cfg; task_brief.md = 交付接口 "
        "(extract_shrink.py); track=faithful (与 asset 不一致, track=faithful 指 prompt verbatim "
        "用户原话 但 asset 是合成 model deck); layer=L1; prompt.txt = verbatim 用户原话 "
        "('@runModelQA_new.pl 我的代码中our $shrink 是从getSSD($cfg);中解析cdg文件获取的...你去要"
        "$model文件中的 .lib tt .lib 'incFile_G5_CIP' mos_tt 中的同级目录下的'incFile_G5_CIP' 文件"
        "...去查找SHRI...' U#0 逐字, 真实 runModelQA_new.pl 内网路径) 但附件 asset 是合成 SPICE "
        "model deck + include 文件 ⇒ synth_deck (合成 SPICE model deck + include file with decoy "
        "comment trap; track=faithful 但 asset=synth_deck ⇒ track≠asset_provenance; portability "
        "reframe 真实 Perl 生产脚本+HSPICE model 不可达; 扩展 r811 decoy distractor 至 SPICE "
        "include file comment; 与 r815 SAoptPwrDly 合成 model 同型)",
    ),
    "EDA-Eval-DesignFlow-SiInpTokenRm-001": (
        "synth_deck",
        "matrix_run_A/runA_000..007/si.inp = 8 个合成 FineSim input deck (每个 header '* FineSim "
        "deck: runA_000' 描述性, 无真实 export banner; 含 .include '/pdk/models/all.mdl' + .param "
        "vdd=0.9 temp=25 + Xtop + filler comments + .option finesim_ignore = 'R_RasEnOsc ... "
        "T_mBistOsc AG_TSOsc ...' + .tran 1n 100n + .meas — FineSim MatrixRun 多子目录结构); "
        "task_brief.md = 交付接口; track=faithful (与 asset 不一致, track=faithful 指 prompt "
        "verbatim pinyin 用户原话 但 asset 是合成 si.inp deck); layer=L1; prompt.txt = verbatim "
        "用户原话 pinyin ('bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan' "
        "= 帮我写个命令我要删掉 si.inp 中 T_mBistOsc 字符串, U#0 逐字) 但附件 asset 是合成 FineSim "
        "input deck (8 子目录 matrix_run) ⇒ synth_deck (合成 FineSim input deck fixture, MatrixRun "
        "多子目录结构; track=faithful 但 asset=synth_deck ⇒ track≠asset_provenance; portability "
        "reframe 真实 FineSim MatrixRun 多子目录不可达; FineSim input deck 子型, 与 r815 SaDcSweepTbGen "
        "合成 HSPICE deck 同型但 FineSim si.inp)",
    ),
    "EDA-Eval-DesignFlow-SiOutWarnDiag-001": (
        "synth_log",
        "si_A.out = 合成 PrimeSim 仿真输出日志 (header 含真实格式 PrimeSim export banner 'PrimeSim "
        "/ Version X-2025.06-SP2-2 for linux64 - Jan 21, 2026 / Copyright (c) 2003 - 2026 by "
        "Synopsys, Inc.' 但 reframe_note 显式 '用真实 si.out 格式场景便携化为合成 fixture' — "
        "real-format PrimeSim banner 为 faithful format mimicry 非 real scp); task_brief.md = "
        "交付接口 (si_out_warn_diag.py <si.out> <out.json>); track=faithful (与 asset 不一致, "
        "track=faithful 指 prompt verbatim 用户原话 但 asset 是合成 si.out log); layer=None; "
        "prompt.txt = verbatim 用户原话 ('分析这个报告的warnning：finesim.golden004_all_perbank_"
        "daily_4b4g_.../si.out' U@0 逐字, 真实 finesim.golden004 路径) 但附件 asset 是合成 PrimeSim "
        "si.out 日志 (real-format PrimeSim export banner faithful mimicry) ⇒ synth_log (合成仿真器"
        "输出日志 fixture; real-format PrimeSim export banner faithful mimicry; track=faithful 但 "
        "asset=synth_log ⇒ track≠asset_provenance; portability reframe+trace-incomplete(agent 从未"
        "读到 si.out) ⇒ B 档合成; 与 r811 Mt0MetastabDiag real-banner 但 synth 同型; 与 SaNPsimDiag "
        "本批 real FineSim banner 同型 pair)",
    ),
    "EDA-Eval-DesignFlow-SimCapLisParse-001": (
        "synth_data",
        "result_wibls.lis = 合成 HSPICE 仿真结果 listing (header '****** HSPICE仿真结果  "
        "result_wibls ******' — Chinese synth header 非 real HSPICE export banner, 但含真实 "
        "/proj/drdxp/V0/model/current_PF_v0d1_Rev06/model.sp 内网路径 + ntk_hwl_m device + "
        "vgs/vds/vth/id/gm/gds 量测行 — faithful structure mimicry with real /proj path embedded); "
        "data_wibls = 合成 .DATA 数据目录; output_format_spec.txt = 合成输出格式规范; "
        "task_brief.md = 交付接口 (sim_cap_lis_parse.py); track=None (内容 Chinese synth header + "
        "real /proj path, track=None 是缺 metadata 非合成信号); layer=L1; reframe_note 显式 "
        "'asset_fidelity 缺标应 A=trace-verbatim(.sp/.lis/.mt0 量测结构)+B=synth' — reframe_note "
        "标 'A=trace-verbatim' 指 .lis 量测结构 trace-faithful 但文件合成 (Chinese synth header "
        "非 real HSPICE banner); prompt = verbatim 用户原话 (yazhuok U#1 '我用这个单管仿真激励跑完"
        "之后的结果在 result_wibls/ 文件夹中，我该如何阅读以及查看我的结果，请把我的结果整理成文本"
        "的形式' + U#2 '把 result_wobls 也一并解析' 逐字); 合成 .lis 仿真输出 (Chinese synth header "
        "+ real /proj path embedded, faithful structure mimicry) ⇒ synth_data (合成 .lis 仿真输出 "
        "fixture; canonical vocab '合成 .lis/.mt0 仿真输出' 归 synth_data; track=None 但 Chinese "
        "synth header; reframe_note 'trace-verbatim' 指结构非文件 provenance; 与 r811 Mt0MetastabDiag "
        "real-banner 但 synth 对比: 本 case Chinese synth header + real path embedded)",
    ),
    "EDA-Eval-DesignFlow-SimConfigEditReport-001": (
        "synth_data",
        "config.yaml = 合成 SPICE 仿真 config (mode transient→dc, vdd 1.2→1.0, duration 100ns→50ns, "
        "temp 25→85); edit_plan.json = 合成参数变更计划; output_format_spec.txt = 合成输出格式规范; "
        "task_brief.md = 交付接口; track=synthesized (与 asset 一致); layer=L1; prompt = 重构需求 "
        "(e0023936 编辑 SPICE 仿真 config.yaml 并产出参数变更审计汇总); 合成 config + 合成 edit_plan "
        "(track=synthesized 显式) ⇒ synth_data (合成 config fixture; 与 r815 ShmooCfgParser 合成 "
        "config 同型; track=synthesized 与 asset 一致)",
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

    print("=== 档2 asset_fidelity backfill r816 batch16 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r816_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r816_manifest.tsv — r816 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch16 (12 cases, alphabetical next 12 missing after r815 batch15 SaDcSweepTbGen: SaNPsimDiag..SimConfigEditReport, S→Sim 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r815 档2 batch1-15 (+168, 106→286) done. 本轮 r816 档2 batch16.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'real trace'/'忠实缩减' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / '重构' / minimal reconstruction / 'Generated as' / '示例' / 'Input A' / 'visible input A' / Chinese synth header / decoy comment / real-format export banner faithful mimicry / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 0% (0/12) 单批最低 (r815 累计 78/180=43.3%; 本批 S→Sim 段全 synth, 无真实 trace-verbatim 资产; 累计 78/192=40.6%) / synth_tree 1 例 (SentaurusDeckSetupSummary 合成 Applications_Library 多项目目录树 GettingStarted/sdevice+Templates/NMOS+FinFET, reframe_note 原标 synth_deck 但多项目目录树 ⇒ synth_tree 更精确, 扩展 r801 synth_tree vocab) / synth_script 1 例 (SetNetlistParam 合成 Run_Compress_Netlist shell 脚本) / real-format export banner faithful format mimicry 2 例 (SaNPsimDiag real FineSim banner in .log + SiOutWarnDiag real PrimeSim banner in si_A.out, both synth per reframe_note, 扩展 r811/r815 export banner 强信号族至 FineSim+PrimeSim sim-output-log) / track≠asset_provenance 5 例 (SetNetlistParam/SharedLibDeployFix/ShrinkExtract/SiInpTokenRm/SiOutWarnDiag, all track=faithful prompt verbatim 但 asset synth, 累计 26→31) / FineSim input deck 子型 (SiInpTokenRm si.inp .option finesim_ignore, 8 subdir MatrixRun 多子目录结构) / decoy comment trap (ShrinkExtract incFile_A '* SHRINK = 9.999 ... must SKIP it' decoy comment, 扩展 r811 decoy distractor 至 SPICE include file comment) / real /proj path embedded in synth .lis (SimCapLisParse result_wibls.lis 真实 /proj/drdxp/V0/model/current_PF_v0d1_Rev06/model.sp 路径 但 Chinese synth header 'HSPICE仿真结果', faithful structure mimicry) / real P010/P004 lib 结构合成 (SharedLibDeployFix needed_libs.txt reframe_note 'real-from-trace' = 结构来自 trace 但文件合成 with decoy libfoo + glibc 系统库)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 286->298 (cases/B 298==B.jsonl 298 ✓); miss 109->97\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
