#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r817.py — r817 档2 asset_fidelity backfill batch17.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done.
      r801-r816 档2 batch1-16 (+180, 106→298) done. 本轮 r817 推进 档2 batch17 — 12 cases
      (alphabetical next 12 missing after r816 batch16 SimConfigEditReport/SiOutWarnDiag/SiInpTokenRm:
       SimExitMatrixDiag..SimlibMatchAnalyze, Sim→Siml 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立, r804-r816 扩展):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 真实 scp /
                    真实 export header banner / desc 显式 "A-faithful"/"real trace"/"逐字" 标注 /
                    真实内网 /proj//apps//home//rundata 路径 / 真实 SKILL .il template / 真实 Perl
                    vecgen / 真实 buggy 脚本 with bug docstring / 真实 verbatim agent 回答 /
                    真实生产代码 with 详细 docstring / 真实 sim env config 文件 / 真实 script
                    author/email/timestamp header)
  - synth_deck   : A = 合成 SPICE deck/stim/cell/sdevice/testbench/FineSim-input 样本 (portability,
                    真实 deck 在 /proj 内网不可达) / "trace-faithful reconstruction" header + decoy
  - synth_script : A = 合成 Perl/Python/Tcl/bash/shell 脚本 fixture
  - synth_data   : A = 合成 JSON/state/config/data/PDK/model/.lis/.mt0/.ma0/.mc0/.bisec_mt0 仿真
                    输出 fixture / 合成 spec/params fixture / 合成 lib list / 合成 result-file
                    fixtures (zzresult stubs) / 合成 .lis 仿真输出 (Chinese synth header + real
                    /proj path embedded) / 合成 measurement data (real-format HSPICE banner + real
                    column names 但 data 线性 progression synth)
  - synth_log    : A = 合成仿真器错误日志/输出日志 fixture (含 real-format export banner faithful
                    mimicry; NanoSpice/FineSim/PrimeSim HSPICE sim-output-log)
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture (multi-project Applications_Library tree)
  - no-asset     : 0 attachment (Q&A)

本批 12 case 判定:
  - 5 A-faithful (42%) — Sim→Siml 段 real-trace 资产密集 (r816 累计 78/192=40.6%; 本批 5/12=42%,
    累计 83/204=40.7%). 5 例:
      * SimModelMismatchDiag (real PrimeSim HSPICE export header in run.log + real user e0024852
        + real /proj/lacaa + /rundata/lacaa + /apps/synopsys paths + verbatim trace user/bitcell
        info in stimulus.sp)
      * SimProgressCheck (real PrimeSim HSPICE export header in .lis + real user shanmei + real
        license server 12000@hfds4 + real /rundata/lagat + /apps/synopsys paths; .sp 4-line
        minimal stubs 因 progress-check 仅需文件存在非内容)
      * SimResultDirRestruct (real scripts run_group123.py + run.py with verbatim trace author
        "xuelian fan" + real email xuelian.fan@cxmt.com + real Modified Time timestamps)
      * SimSetupExplainQA (real LPDDR6 DECQA sim_setup files: common.env_LP6 real dejoa header +
        real .param, paramen.inc, finesim_option/ real finesim options, post_sim/SPF/ real SPF
        module names CkRcvGutM6/CaIOM6, project_info.json real /home/coverage path; reframe_note
        显式 'sim_setup/ 真实文件作可见 A')
      * SimlibMatchAnalyze (real production code simlib_ref_db.py 296 lines + real simlib.sv 104
        lines SV modules + real targets.json matching config; tb_family/ are synth stubs 但 family
        gating 仅用 filename; reframe_note 'real-from-trace' = real files, track 缺标应 faithful)
  - 1 synth_deck: SimExpl (合成 SPICE decks baseline_a.sp/bloated_a.sp for portable 小尺度电路
    reproduction, real /proj/shdc/models path in .lib, track=synthesized)
  - 3 synth_log: SimExitMatrixDiag / SimIncMissingDiag / SimStatusMonitor
  - 3 synth_data: SimResultGrep / SimSavedCornerComplete / SimSpecJudge

关键发现:
  - A-faithful 42% (5/12) — Sim→Siml 段 real-trace 资产回弹 (r816 累计 78/192=40.6%; 本批 5/12=42%,
    累计 83/204=40.7%). 5 例 real-trace 资产: 2 real PrimeSim HSPICE export header (SimModelMismatchDiag
    run.log + SimProgressCheck .lis, 承 r813 real PrimeSim HSPICE .ma0 export 群) + 1 real Python
    script with verbatim author/email/timestamp header (SimResultDirRestruct, 新信号族: real script
    author header) + 1 real sim env config files (SimSetupExplainQA LPDDR6 DECQA sim_setup, 新信号族:
    real sim env config) + 1 real production code (SimlibMatchAnalyze simlib_ref_db.py 296 lines
    detailed docstring, 新信号族: real production code).
  - real PrimeSim HSPICE export header 群 2 例 (SimModelMismatchDiag + SimProgressCheck, 承 r813
    real PrimeSim HSPICE .ma0 export 群至 .lis/run.log sim-output-log).
  - 新信号族 3 类:
    * real script author header (SimResultDirRestruct run_group123.py 'Author: xuelian fan /
      mail: xuelian.fan@cxmt.com / Modified Time:Fri Oct 23 16:16:25 2026' verbatim trace author
      header, 扩展 r814 agent-response-verbatim 至 script author header)
    * real sim env config files (SimSetupExplainQA LPDDR6 DECQA sim_setup/ 真实 dejoa header +
      real .param delvto + real finesim_option + real SPF module names, 新 asset 类: sim env
      config files)
    * real production code (SimlibMatchAnalyze simlib_ref_db.py 296 lines detailed docstring +
      real _cell_part/_family_letters/_family_digit logic, 新 asset 类: production code with
      detailed docstring)
  - track≠asset_provenance 5 例 (累计 31→36): SimExitMatrixDiag/SimIncMissingDiag/SimResultGrep/
    SimSavedCornerComplete/SimSpecJudge (all track=faithful prompt verbatim 但 asset synth;
    portability reframe 真实 NanoSpice/FineSim/HSPICE/sim.saved.total 环境不可达).
  - synth_log 3 例: SimExitMatrixDiag (合成 NanoSpice matrix_run_A 17 子目录 si.out sim logs,
    real-format NanoSpice Pro banner faithful mimicry) + SimIncMissingDiag (合成 sim result_post/
    9 子目录 sim logs + Setting.sp, real-from-trace 结构合成, reframe_note '用真实 Setting.sp/
    sim log 结构合成') + SimStatusMonitor (合成 rundir_A case_A001..A005 finesim.log, real-format
    FineSimPro banner faithful mimicry, track=synthesized).
  - synth_data 3 例: SimResultGrep (合成 zzresult stubs in testdir_A directory tree, grep tool
    scans paths) + SimSavedCornerComplete (合成 sim.saved.total text file with real /proj/drvqa
    paths + real PVT corners, desc '示例仿真输入文件 A', real-from-trace 结构) + SimSpecJudge
    (合成 .mt0/.ma0/.mc0 measurement data, real-format HSPICE J-2024.09-SP1 banner + real Vcc2sc
    column names 但 data 线性 progression synth, reduced from real 121 PVT to 8 alters).
  - synth_deck 1 例 (SimExpl): 合成 baseline_a.sp/bloated_a.sp 小尺度 CMOS clock buffer + RC 阶梯
    deck for portable FineSim reproduction (real /proj/shdc/models path in .lib, track=synthesized
    与 asset 一致).
  - .sp minimal stubs as faithful elision (SimProgressCheck): .sp 4-line stubs 因 progress-check
    task 仅需文件存在非内容, .lis real PrimeSim banner 为真实诊断输入; 非 synth 信号 (内容
    elision 因 task-irrelevant, 承 r811 'elision=A-faithful' 判别线).
"""
import json, os
from collections import Counter

CASES_B = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

BATCH = {
    "EDA-Eval-DesignFlow-SimExitMatrixDiag-001": (
        "synth_log",
        "matrix_run_A = 合成 NanoSpice matrix-run 目录 (17 子目录 nanospice.perbank_Sec28WL0CSL0_"
        "ypzhengcoretiming_*_A101..A112, 每个含 si.out; si.out header 含真实格式 NanoSpice Pro "
        "banner 'Copyright (c) 2010-2025 Primarius Tech / NanoSpice Pro version 2024.12.1 ("
        "linux64) / License: Primarius NanoSpice (node-locked)' 但 desc 显式 '合成 NanoSpice run "
        "目录' + '_A' 后缀 ⇒ real-format NanoSpice banner 为 faithful format mimicry 非 real scp); "
        "prompt.txt = verbatim 用户原话 (ypzheng @ hfeg0pkn003, trace 1793667622298_rh3ek U#0 逐字 "
        "'去这个目录，看看仿真exit的原因是什么，应该怎么解决', 真实 /proj/ddgoa/V0/simdir/finesim/"
        "workdir/ypzheng/ddgoaF/MatrixRun_Netlist_SpfBa_20261031PM_wisteria 路径); task_brief.md = "
        "交付接口 (sim_exit_diag.py <matrix_run_dir> -o out.json); track=faithful (与 asset 不一致, "
        "track=faithful 指 prompt verbatim 用户原话 但 asset 是合成 NanoSpice run 目录); layer=None; "
        "合成 sim-output logs group (17 子目录 si.out 主导诊断输入) ⇒ synth_log (合成仿真器输出日志 "
        "fixture in matrix-run 目录; real-format NanoSpice Pro banner faithful mimicry; track=faithful "
        "但 asset=synth_log ⇒ track≠asset_provenance; portability reframe 真实 NanoSpice matrix-run "
        "不可达; 与 r816 SaNPsimDiag real FineSim banner 但 synth 同型; 与 SimStatusMonitor 本批 "
        "real-format FineSimPro banner 同型)",
    ),
    "EDA-Eval-DesignFlow-SimExpl-001": (
        "synth_deck",
        "baseline_a.sp = 合成 SPICE deck (4-stage CMOS clock buffer 链 inva/clkbuf + 少量寄生 RC "
        "节点 + 少量 .ic, .lib '/proj/shdc/models/cl028hkn/cl028hkn_1d05_1d8_v1d1a/hspice/model.sp' "
        "TOP_TT_TYP — real /proj/shdc/models path in .lib 但 deck 合成 小尺度便携复现); bloated_a.sp "
        "= 合成 SPICE deck (同结构但大量寄生 R/C 节点 + 每节点 .ic v(...)=0, state 变量爆炸); "
        "spec_a.json = 合成 spec; task_brief.md 显式 '本 case 用同一机制在可跑的小尺度电路上复现' — "
        "portable 小尺度 reconstruction; track=synthesized (与 asset 一致); layer=L2; reframe_note "
        "显式 '重构为产 sim_diag.py(诊断工具, 在 .75 沙盒小尺度电路上复现该诊断流程)'; prompt = 重构 "
        "需求 (kli@hfeahpc501 trace 1792031875998_68gc9 mc424 DRAM Fullchip primesim 仿真爆炸诊断); "
        "合成 SPICE decks (小尺度便携复现, real /proj path in .lib 为 faithful structure mimicry) ⇒ "
        "synth_deck (合成 SPICE deck fixture for portable reproduction; track=synthesized 与 asset "
        "一致; 与 r815 SaDcSweepTbGen 合成 HSPICE deck 同型)",
    ),
    "EDA-Eval-DesignFlow-SimIncMissingDiag-001": (
        "synth_log",
        "A_sim_post = 合成 sim 目录 (result_post/ 9 仿真子目录 1_pvt_130/1_pvt_m40/2_mc_130/2_mc_m40/"
        "3_ac/4_ioff_130/4_ioff_m40/5_ADcomp_130/5_ADcomp_m40 + A_Setting.sp + A_netlist.presim); "
        "A_Setting.sp = 合成 SPICE deck (含 .inc 相对路径引用两个 PEX .spf_RCC 寄生网表但文件项目内不"
        "存在); sim logs = 合成仿真输出日志 (unable to read file .inc 错误); reframe_note 显式 "
        "'asset_fidelity 缺标应 real-from-trace(用真实 Setting.sp/sim log 结构合成)' — 结构来自 trace "
        "但文件合成; task_brief.md = 交付接口 (diagnose_sim_inc_missing.py <result_post_dir> "
        "<setting_sp> <netlist_presim> -o out.json); track=faithful (与 asset 不一致, track=faithful "
        "指 prompt verbatim yanghao 原话 但 asset 合成); layer=L1; prompt.txt = verbatim 用户原话 "
        "(yanghao @ hfhds201, trace 1794105806205_mah5p mc72 U#0 逐字 '/proj/commonIP/analog/v1/"
        "lp5x/v0/simdir/anasim/yanghao/2_TsComp_post/result_post 下面的仿真为什么报错了'); 合成 sim "
        "logs group (9 子目录 sim logs 主导诊断输入 + Setting.sp 辅助 root cause 上下文) ⇒ synth_log "
        "(合成仿真器输出日志 fixture; real-from-trace 结构合成; track=faithful 但 asset=synth_log ⇒ "
        "track≠asset_provenance; reframe_note '用真实 Setting.sp/sim log 结构合成'; 与 r816 SaNPsimDiag "
        "sim logs + deck supporting 同型)",
    ),
    "EDA-Eval-DesignFlow-SimModelMismatchDiag-001": (
        "A-faithful",
        "sim/run.log = 真实 PrimeSim HSPICE 仿真日志 (header 'PrimeSim HSPICE -- V-2023.12-SP1-1 "
        "linux64 (Apr 07 2024 8845341) / Copyright (c) 1986 - 2026 by Synopsys, Inc.' 真实 PrimeSim "
        "HSPICE export banner + lic USER: e0024852 HOSTNAME: hfeg0pkn063 + real license server "
        "12000@hl04 + real **warning** (/proj/lacaa/V0/workdir/e0018590/model_file/option_hspice.sp:11) "
        "+ real **error** CH336_bitcell_FS.netlist model not found); sim/stimulus.sp = 真实 SPICE "
        "stimulus (header '* CH336_FS post-PE simulation stimulus (rev06 / model rev04) / User: "
        "e0024852 Bitcell: CH336 (migrated from CH252, width -> 40nm)' verbatim trace user/bitcell "
        "info + .include '/rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/"
        "Bitcell_FS/CH336_FS_guojing/CH336_bitcell_FS.netlist' 真实 /rundata/lacaa 路径 + .LIB '/proj/"
        "lacaa/V0_Virtuoso/model/current_SRAM_v0d1_Rev06/hspice/35H_DBCFS_Model_SRAM_v0d1_Rev06.lib' "
        "真实 /proj/lacaa path); sim/pf_model.lib + sram_model.lib = 真实 model lib; sim/CH336_HC_"
        "Bitcell_FS_PIN.dspf = 真实 DSPF 寄生网表; track=None (缺 metadata 非 synth 信号); layer=L1; "
        "reframe_note 空; prompt = verbatim 重构 (e0024852 @ hfeg0pkn005, IP 10.129.2.14, '运行 "
        "stimulus_pex_rev06_model_rev04.sp 但仿真出来的结果跟 252 一样'); 真实 PrimeSim HSPICE export "
        "header + real user e0024852 + real /proj/lacaa + /rundata/lacaa + /apps/synopsys 路径群 + "
        "verbatim trace user/bitcell info ⇒ A-faithful (real PrimeSim HSPICE sim-output-log + real "
        "SPICE stimulus + real model lib + real DSPF; 承 r813 real PrimeSim HSPICE .ma0 export 群至 "
        "run.log sim-output-log; track=None 但强 real 信号群)",
    ),
    "EDA-Eval-DesignFlow-SimProgressCheck-001": (
        "A-faithful",
        "corner_stb_A/result/*.lis = 真实 PrimeSim HSPICE 仿真 listing (header 'PrimeSim HSPICE -- "
        "V-2023.12-SP1-1 linux64 (Apr 07 2024 8845341) / Copyright (c) 1986 - 2026 by Synopsys, Inc.' "
        "真实 PrimeSim HSPICE export banner + lic USER: shanmei HOSTNAME: hfeg0pgn022 + real license "
        "server 12000@hfds4 + real **error** (stb_iloadnear_-1m_vin_0.3_corner_tt_temp_25_vcc_0.95."
        "sp:43) unable to open file '/rundata/lagat/V0/simdir/finesim/workdir/shanmei/simulation/"
        "tb_OTA_stb_farcap/hspiceD/schematic/hspice/netlist/netlist' 真实 /rundata/lagat 路径 + real "
        "Command line options /apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/linux64/hspice 真实 "
        "/apps/synopsys 路径); corner_stb_A/*.sp = 真实 .sp 仿真作业 minimal stubs (4 行: comment + "
        ".option probe + .tran 1n 100n + .end — 内容 elision 因 progress-check task 仅需文件存在非"
        "内容, 非 synth 信号, 承 r811 'elision=A-faithful' 判别线); desc 显式 '真实 corner_stb 仿真"
        "目录（A 资产，trace zns2p shanmei@hfeg0plg53 原文路径结构）'; track=faithful; layer=L1; "
        "prompt.txt = verbatim 用户原话 (shanmei @ hfeg0plg53, trace 1793775649853_zns2p U#0 逐字 "
        "'我的目录下有一个tb_OTA_stb_farcap的子目录，请在下面corner_stb文件夹中执行check_sim指令，"
        "查看仿真完成进度'); 真实 PrimeSim HSPICE export header in .lis + real user shanmei + real "
        "license server 12000@hfds4 + real /rundata/lagat + /apps/synopsys 路径群 + desc 'A 资产' + "
        ".sp minimal stubs 为 task-irrelevant elision ⇒ A-faithful (real PrimeSim HSPICE sim-output"
        "-log; 承 r813 real PrimeSim HSPICE .ma0 export 群至 .lis; track=faithful 与 asset 一致)",
    ),
    "EDA-Eval-DesignFlow-SimResultDirRestruct-001": (
        "A-faithful",
        "run_group123.py = 真实 Python 脚本 (header 'File Name: run_group123.py / Author: xuelian "
        "fan / mail: xuelian.fan@cxmt.com / Modified Time:Fri Oct 23 16:16:25 2026 / Modified Time:"
        "Sat Nov  7 10:19:14 2026 / Description:' verbatim trace author/email/timestamps header + "
        "pathlib 绝对路径 + bsub 无 -n/-R + GROUPS=[group1,group2] + 输出散落 all_sim_result_D0 "
        "平层); run.py = 真实 Python 脚本 (header 'Modified Time:Thu 10 Sep 2026 06:52:43 PM CST' + "
        "QUEUE_NAME='fqueueAry2' + NP_NUM=16 + DRY_RUN=False + os.chdir+相对路径 + bsub -n 16 -R "
        "span[hosts=1] + shutil.rmtree); desc 显式 '文件1·待修改脚本（原始版）' + '文件2·参考脚本'; "
        "track=faithful; layer=L1; reframe_note 显式 'A-faithful' + 'trace 金标准 13 msgs run_group123."
        "py 输出目录生成方式改成像 run.py'; prompt.txt = verbatim 用户原话 (xuelianf @ hfeg0pkn002, "
        "trace 1794187811534_0218t U#0+U#2 逐字 '请按照文件2生成输出文件夹的方式修改文件1的程序...以D0"
        "为例...文件2生成的输出文件会在文件夹all_sim_result_D0内再生成一层各自的文件夹' + 真实 /rundata/"
        "sim_cloud/CRG 路径); 真实 Python scripts with verbatim trace author 'xuelian fan' + real "
        "email xuelian.fan@cxmt.com + real Modified Time timestamps ⇒ A-faithful (real script author "
        "header, 新信号族: real script author/email/timestamp verbatim; 扩展 r814 agent-response-"
        "verbatim 至 script author header; track=faithful 与 asset 一致)",
    ),
    "EDA-Eval-DesignFlow-SimResultGrep-001": (
        "synth_data",
        "testdir_A = 合成 result-grep 测试目录 (MatrixRun_Netlist_Vcap_20260601AM/zzresult_001.lis "
        "内容 'pass' 1 行 + MatrixRun_MMSIM_20260601AM/zzresult_a.txt + zzresult_b.txt 内容 'a-"
        "result' 1 行 + MatrixRun_Other_20260501PM/notes.txt + scratch/tmp.log + readme.txt 内容 "
        "'hi' 1 行 — 全 zzresult/result files 为极小 synth stubs); task_brief.md 显式 '判分时脚本会"
        "被解压后在独立的合成测试目录上运行' — 合成测试目录; track=faithful (与 asset 不一致, "
        "track=faithful 指 prompt verbatim 用户原话 但 asset 是合成 result-file fixtures); layer=L1; "
        "prompt.txt = verbatim 用户原话 ('写一个脚本实现仿真路径下到结果抓取...脚本放在/proj/drcpa/V0/"
        "simdir/finesim/drcpaF/MatrixRun 路径下，起名叫result_grep...-result选项 抓取当前path下所有"
        "folder内的zzresult*文件...-path 选项，抓取当前path下的所有MatrixRun* folder' + 真实 /proj/"
        "drcpa 路径); 合成 zzresult stubs in directory tree (grep tool scans paths 非 content) ⇒ "
        "synth_data (合成 result-file fixtures in directory tree; track=faithful 但 asset=synth_data "
        "⇒ track≠asset_provenance; portability reframe 真实 MatrixRun 目录不可达; task_brief '合成"
        "测试目录' 显式 synth; 与 r816 SimCapLisParse 合成 .lis 对比: 本 case zzresult stubs 极小)",
    ),
    "EDA-Eval-DesignFlow-SimSavedCornerComplete-001": (
        "synth_data",
        "sim.saved.total = 合成仿真输入清单 text file (17 行, 每行 <base_path>_<FF|TT|SS>.X4 <PVT_TAG> "
        "X4, 含真实 /proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL/"
        "vec_golden/3600_X4_BC8_OTF/Golden005_Multi4bank_redundancy_combine_WPre_4_CRC_00_1_tCH_50_BC8_"
        "OTF_4b8g_Bcd08_3600_FF.X4 FF1.3v110C X4 路径 + real PVT corners FF1.3v110C/FF1.3v-40C/TT0.94v25C/"
        "SS0.94v110C/SS0.94v-40C, 部分 case 缺 corner); desc 显式 '示例仿真输入文件 A(可见)...来自 ynbai "
        "的 cline trace,需识别缺失 corner 并补全' — '示例' 标记 synth; task_brief.md 显式 '判分用隐藏"
        "输入运行，不依赖 prompt 中的真实路径'; track=faithful (与 asset 不一致, track=faithful 指 "
        "prompt verbatim ynbai 原话 但 asset 是合成 sim.saved.total); layer=L1; prompt.txt = verbatim "
        "用户原话 ('识别/proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.vecgen/log_20260908_newWL"
        "下的sim.saved.total文件...内容例如...FF1.3v110C X4' + 真实 /proj/drvqa 路径); 合成 sim.saved."
        "total text file with real /proj/drvqa paths + real PVT corners (real-from-trace 结构合成, "
        "desc '示例' 标记) ⇒ synth_data (合成 text-file fixture with real /proj path embedded; "
        "track=faithful 但 asset=synth_data ⇒ track≠asset_provenance; 与 r816 SimCapLisParse real "
        "/proj path embedded in synth .lis 同型)",
    ),
    "EDA-Eval-DesignFlow-SimSetupExplainQA-001": (
        "A-faithful",
        "sim_setup/ = 真实 LPDDR6 DECQA sim_setup 文件群: voltagefile/common.env_LP6 (187 行, header "
        "'** dejoa(lpddr6): common.env **' 真实 dejoa LPDDR6 header + real .param pvcsl/pvdd1/pvdd2h/"
        "pvdd2c/pvdd2d + real vdd1/vdd2h/vdd2l/vdd2c/vdd2d voltage sources) + voltagefile/paramen.inc "
        "(91 行, header '**kangw cp from ddjoc for dejoa G4B' + real .param delvto_Ns/delvto_Ps/"
        "delvto_Ysa/delvtoBL0/1 真实 LPDDR6 process params) + finesim_option/spfba (18 行, real .option "
        "PARHIER/SCALE/finesim_mode=promd/finesim_prbport/finesim_maxicout/finesim_vdd=3.5v/finesim_"
        "pwrloadmodel/finesim_output=fsdb) + finesim_option/spf_block + vcap + vcap_block + post_sim/"
        "SPF/no_vcap (35 行, real SPF module names CkRcvGutM6/CaIOM6/CaDlyAdj/CADlyAdjPre/CADlyAdjPst/"
        "CsIOM6/CsSetHld2/CsDlyAdjG); project_info.json = real project metadata (project=LP6, qa_module"
        "=DECQA, dram_generation=LPDDR6, sim_setup_path=/home/coverage/LPDDR6/DECQA/sim_setup 真实 "
        "/home/coverage 路径); reframe_note 显式 'asset_fidelity 缺标应 real-from-trace (sim_setup/ "
        "真实文件作可见 A)' — 真实文件作可见 A; track=None (缺 metadata 非合成信号); layer=None; "
        "prompt = verbatim 用户原话 (t0002965 @ hfhds201, trace 1791875313313_ztoza mc142 U#190 逐字 "
        "'分析LPDDR6/DECQA/sim_setup下面的文件是干什么的？' + U#197 '能不能找到finesim仿真相关的文件"
        "目录'); 真实 LPDDR6 DECQA sim_setup 文件群 (real dejoa header + real .param delvto + real "
        "finesim_option + real SPF module names + real /home/coverage path; reframe_note '真实文件作"
        "可见 A') ⇒ A-faithful (real sim env config files, 新信号族: real sim env config; track=None "
        "但强 real 信号群)",
    ),
    "EDA-Eval-DesignFlow-SimSpecJudge-001": (
        "synth_data",
        "SPEC.sp = 合成 SPEC 文件 (Vcc2sc_Gain_load1mA >40dB;Vcc<0.92 dont care + ac/ac_load/tran/"
        "dc_capbi/tran_mc 类别 Vcc2sc metrics — real Vcc2sc column names from trace 但 SPEC 阈值合成); "
        "measure/tran.mt0 = 合成 HSPICE measurement data (header '$DATA1 SOURCE=\\'HSPICE\\' VERSION="
        "\\'J-2024.09-SP1\\' TITLE=\\'Vcc2scAct_tran\\' 真实格式 HSPICE export banner + real Vcc2sc "
        "column names vcc2sc_unload/vcc2sc_load1ma/vcc2sc_undershot/... 但 data 线性 progression "
        "8.956100e-01→8.964082e-01→8.972064e-01 (uniform +0.007982 increment) synth, alter# 1-8 "
        "with temper -40,-40,0,0,25,25,85,85 synth PVT corners — reduced from real 121 PVT + 500 MC "
        "to portable 8 alters); measure/ac.ma0 = 合成 HSPICE measurement (同 real-format HSPICE "
        "banner + real Vcc2sc columns 但 data 线性 1.800000e+01→1.827273e+01 线性 synth); measure/"
        "tran_mc.mc0 = 合成 MC measurement; task_brief.md = 交付接口 (judge_sim_vs_spec.py <measure_"
        "dir> <spec_file> <out_json>); track=faithful (与 asset 不一致, track=faithful 指 prompt "
        "verbatim tongni 原话 但 asset 合成 measurement data); layer=None; reframe_note 显式 'A 不可"
        "行原因=produce-action 真跑 121 PVT+500 MC 不可便携 .75 -> case 抽取「解析 .mt0/.ma0/.mc0 + "
        "比对 SPEC 产合规判定」子技能' + 'A 档 verbatim 合规' (指 prompt verbatim 非 asset); prompt "
        "= verbatim 用户原话 (tongni @ hfeg0pkn001, trace 1793266803039_g89xb mc224 U#0 逐字 "
        "'[sim-sp-gen] /home/tongni/Desktop/1_Vcc2sc_stdby/Vcc2scAct_sim_sp/ 路径下给出了对应的网表和"
        "SPEC 根据此跑对应的仿真'); 合成 measurement data (real-format HSPICE J-2024.09-SP1 banner + "
        "real Vcc2sc column names 但 data 线性 progression synth, reduced 121 PVT→8 alters portable) "
        "⇒ synth_data (合成 .mt0/.ma0/.mc0 measurement data fixture with real-format HSPICE banner "
        "faithful mimicry; track=faithful 但 asset=synth_data ⇒ track≠asset_provenance; portability "
        "reframe 真跑 121 PVT+500 MC 不可便携; 与 r813 OtaMa0SpecCheck real .ma0 A-faithful 对比: "
        "本 case data 线性 synth)",
    ),
    "EDA-Eval-DesignFlow-SimStatusMonitor-001": (
        "synth_log",
        "rundir_A = 合成 FineSim MatrixRun 批量仿真目录 (case_A001..A005 子目录, 每个含 finesim.log + "
        ".mt0/.tr0/.pt0 仿真产出 + .lock 锁文件 for running case; finesim.log header 'FineSimPro "
        "Version V-2023.12-1 linux64 / Reading netlist file : case_A001.sp / Starting transient "
        "analysis / transient analysis completed / ires= 0 / Completed / job CPU time = 12.34 s' — "
        "real-format FineSimPro banner faithful mimicry 但 case_A00x 合成 case 名); track=synthesized "
        "(与 asset 一致); layer=None; reframe_note 空; prompt 显式 '附件 rundir_A 是一个 FineSim "
        "MatrixRun 批量仿真目录' — 合成附件; 合成 sim-output logs group (case_A001..A005 finesim.log "
        "主导诊断输入 + .mt0/.tr0/.pt0/.lock 辅助状态判定) ⇒ synth_log (合成仿真器输出日志 fixture in "
        "rundir; real-format FineSimPro banner faithful mimicry; track=synthesized 与 asset 一致; "
        "与 r816 SaNPsimDiag real FineSim banner 但 synth 同型; 与 SimExitMatrixDiag 本批 real-format "
        "NanoSpice banner 同型)",
    ),
    "EDA-Eval-DesignFlow-SimlibMatchAnalyze-001": (
        "A-faithful",
        "simlib_ref_db.py = 真实生产代码 (296 行, 详细 docstring 'simlib 参考索引库（reference "
        "database）/ simlib_drcoa_stdcells.sv (config ref_simlib 指定) 是 schematic netlist 转换完成"
        "后的黄金结果/参考库' + real CLI usage + real _IDENT_RE regex + real _cell_part/_family_letters/"
        "_family_digit/_family_token helper functions with detailed docstrings '去掉开头单字母 role "
        "前缀 R_/B_/Y_/Q_...名字内部的 _ 是变体后缀必须保留' + real SimlibRefDB class — real production "
        "code with detailed docstring); simlib.sv = 真实 SystemVerilog module 库 (104 行, `celldefine "
        "module or2GSx2 (output z, input a, input b); or (z, a, b); endmodule `endcelldefine + "
        "or3GSx1/and2/and3/nand2/nor2/inv/buf/mx2/mx3 real cell definitions); targets.json = 真实 "
        "matching config (targets [or2GSx2,or4GSx2,or4FSSx1,and3X2,nand5X1,nor2CSx1,mx2X1,xor2X1] + "
        "matching limit/cutoff/exact_match_priority/digit_preference/family_gating real config); "
        "tb_family/ = synth stub testbenches (tb_or2.sv/tb_or3.sv/tb_or4.sv/... 内容 'stub testbench "
        "— family gating only uses this filename' — synth stubs 但 family gating 仅用 filename 非 "
        "content, 承 r811 'elision=A-faithful' 判别线; tb_family/ stubs 为 supporting 非 主导资产); "
        "reframe_note 显式 'asset_fidelity 缺标应 real-from-trace' + 'track 缺标应 faithful' — real "
        "files from trace; track=None (缺 metadata 非合成信号); layer=L1; prompt = verbatim 用户原话 "
        "(e0039602 @ hfeg0pkn005, trace 1794362790365_5kysh U#0 多轮逐字 '请你检查一下这里面这个相似"
        "model匹配的一个逻辑，并告诉我 or4GSx2 会在我们的库里匹配到哪个相似 model' + 真实 /home/wellesc/"
        "StdCellTB_Skill/StdCellTBSkill_V0 路径); 真实生产代码 simlib_ref_db.py (296 行 detailed "
        "docstring) + real simlib.sv (104 行 real SV modules) + real targets.json (real matching "
        "config) ⇒ A-faithful (real production code with detailed docstring, 新信号族: real "
        "production code; tb_family/ synth stubs 为 task-irrelevant elision; track=None 但强 real "
        "信号群; reframe_note 'real-from-trace' = real files, track 缺标应 faithful)",
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

    print("=== 档2 asset_fidelity backfill r817 batch17 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r817_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r817_manifest.tsv — r817 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch17 (12 cases, alphabetical next 12 missing after r816 batch16 SimConfigEditReport/SiOutWarnDiag/SiInpTokenRm: SimExitMatrixDiag..SimlibMatchAnalyze, Sim→Siml 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 done. r773-r800 档3 done. r801-r816 档2 batch1-16 (+180, 106→298) done. 本轮 r817 档2 batch17.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver + task_spec verbatim 标注 + desc 'A-faithful'/'逐字'/'real trace'/'忠实缩减' 标注; A-faithful 强信号见 canonical vocabulary; synth 信号 = track=synthesized / portability reframe / '重构' / minimal reconstruction / 'Generated as' / '示例' / 'Input A' / 'visible input A' / Chinese synth header / decoy comment / real-format export banner faithful mimicry / 无 verbatim 标注\n")
        f.write("# 关键发现: A-faithful 42% (5/12) — Sim→Siml 段 real-trace 资产回弹 (r816 累计 78/192=40.6%; 本批 5/12=42%, 累计 83/204=40.7%) / real PrimeSim HSPICE export header 群 2 例 (SimModelMismatchDiag run.log + SimProgressCheck .lis, 承 r813 real PrimeSim HSPICE .ma0 export 群至 sim-output-log) / 新信号族 3 类 (real script author header SimResultDirRestruct 'Author: xuelian fan / mail: xuelian.fan@cxmt.com' verbatim trace author header + real sim env config files SimSetupExplainQA LPDDR6 DECQA sim_setup dejoa header + real production code SimlibMatchAnalyze simlib_ref_db.py 296 lines detailed docstring) / track≠asset_provenance 5 例 (SimExitMatrixDiag/SimIncMissingDiag/SimResultGrep/SimSavedCornerComplete/SimSpecJudge, all track=faithful prompt verbatim 但 asset synth, 累计 31→36) / synth_log 3 例 (SimExitMatrixDiag NanoSpice matrix_run_A + SimIncMissingDiag sim result_post/ + SimStatusMonitor rundir_A, real-format NanoSpice/FineSimPro banner faithful mimicry) / synth_data 3 例 (SimResultGrep zzresult stubs + SimSavedCornerComplete sim.saved.total real /proj path + SimSpecJudge .mt0/.ma0 real-format HSPICE banner 但 data 线性 synth) / synth_deck 1 例 (SimExpl 小尺度便携复现) / .sp minimal stubs as faithful elision (SimProgressCheck .sp 4-line stubs 因 task-irrelevant, 承 r811 elision=A-faithful 判别线)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B; asset_fidelity 298->310 (cases/B 310==B.jsonl 310 ✓); miss 97->85\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
