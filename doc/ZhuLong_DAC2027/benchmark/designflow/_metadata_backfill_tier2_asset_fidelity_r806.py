#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""_metadata_backfill_tier2_asset_fidelity_r806.py — r806 档2 asset_fidelity backfill batch6.

背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done.
      r773-r800 档3 (reframe_note backfill, 32→235) done.
      r801 档2 batch1 (+12, 106→118) done. r802 batch2 (+12, 118→130) done.
      r803 batch3 (+12, 130→142) done. r804 batch4 (+12, 142→154) done.
      r805 batch5 (+12, 154→166) done.
      本轮 r806 推进 档2 batch6 — 12 cases
      (alphabetical next 12 missing after r805 batch5 DupSubcktDefDiag:
       DutySkewAvg..FinesimLogExplainDiag, F 段).

档2 asset_fidelity 字段语义: 记录输入 A 的来源 (trace-verbatim/真实 scp vs 合成 fixture),
                              hidden B 一律 synthesized (§4.1, 字段不重复记)。
canonical vocabulary (r801 确立):
  - A-faithful   : A = 真实文件 trace-verbatim (含 verbatim excerpt with 原行号标注 / 现场抽取真实产物 / 真实 scp 自内网 / 真实用户 paste / "reproduced faithfully" / "faithful compact/trimmed representation" 标注)
  - synth_deck   : A = 合成 SPICE deck/stim/cell 样本 (portability, 真实 deck 在 /proj 内网不可达)
  - synth_script : A = 合成 Perl/Python/Tcl 脚本 fixture
  - synth_data   : A = 合成 JSON/state/log/config/data/source-file fixture
  - synth_log    : A = 合成仿真器错误日志 fixture
  - synth_doc    : A = 合成 doc/manual/knowledge 摘录 fixture
  - synth_tree   : A = 合成样本目录树 fixture
  - no-asset     : 0 attachment (Q&A; workdir docs 由 SUT 从 RAG + trace verbatim user turns 生成)

判据: 逐题读 case prompt 的资产/附件描述 + attachments 文件内容头 + track 字段 + reframe_note driver。
      A-faithful 强信号 = asset 文件 header 明记 verbatim/excerpt/reproduced faithfully/faithful compact/faithful trimmed from trace (含真实内网路径) 或
                          asset 内容含真实内网路径 (/proj/..., /home/..., /rundata/...) 或
                          asset header = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB export header (含真实 user/date/library/tool-version) 或
                          asset = 真实用户 paste 的 verbatim 文本 (track=faithful + 内容与 prompt 引用一致) 或
                          asset 含真实内部 edit note / 真实 hostname。
      synth 信号 = track=synthesized / portability reframe / "样本"/"合成"/"self-contained sample" / 通用名文件 /
                   "(reconstructed from cline trace ...)" / desc 显式 "合成 hspice deck" / A_ONLY_MARKER + decoy 内容。
      .75-reachable 判别 (r803): host=.75 (hfhds201) ⇒ 真实 scp 可行 / host=计算节点+asset 含真实内网路径 ⇒ 推断 file-verbatim。
      excerpt vs reconstructed 二分 (r804): "(excerpt)"/"(excerpt from ...)" = verbatim 切片 ⇒ A-faithful;
                                             "(reconstructed from cline trace ...)" = 重建 ⇒ synth_data。
      "reproduced faithfully" 标注 (r805): "reproduced faithfully from cline trace" = verbatim 复刻标记 ⇒ A-faithful。
      "faithful compact/trimmed representation" 标注 (r806 新增): file header 明记 "faithful compact representation" / "faithful trimmed netlist, real port names from trace" = 忠实紧凑表示 ⇒ A-faithful。

本批 12 case 判定:
  - 6 A-faithful (追平 r804/r805 单批最高 50%): FifoDelayOptDiag/FifoStimulusGen/FineSimDatacardDiag/
        FineSimMetricCornerDiag/FinesimLaunchAgent/FinesimLogExplainDiag
  - 3 synth_deck: FineSimDcConvGuide/FineSimDiag/FinesimConvDiag
  - 2 synth_data: DutySkewAvg/FineSimIntroGuide
  - 1 no-asset: FineSimCoreCounter

关键发现:
  - "faithful compact/trimmed representation" verbatim 标记 (r806 首例群, 两例): FifoDelayOptDiag fifo_sel_A.sp header
    "* FIFO_TOP selector critical-path netlist (faithful compact representation) / * Source: cline trace 1793928990578_ltkg1 (curryxu@hfeg0pkn001), user-accepted delay analysis"
    + FifoStimulusGen FIFO_TOP.netlist header "* A: M2701 FIFO_TOP 24-bit DDR4 FIFO (faithful trimmed netlist, real port names from trace z7n9b)"
    = 忠实紧凑/裁剪表示标注 (含真实 Source trace 引用 + 真实 port names), 与 r805 "reproduced faithfully" 同列强信号,
    扩展 verbatim 标记族: excerpt / reproduced faithfully / faithful compact / faithful trimmed = A-faithful。
  - 真实 FineSim export header 强信号 (FineSimDatacardDiag): pvt.log header
    "FineSim (R) Version U-2023.03-2 for linux64 - Apr 25, 2023 ... *** job run at hfeg0pkn002 (linux64) on Wed Nov 4 17:28:04 2026"
    = 真实 FineSim 工具导出 banner (含真实 tool-version U-2023.03-2 + 真实 hostname hfeg0pkn002 + 真实 date 2026-11-04, 与 trace_source session 时间一致),
    与 r804 AETHER-SE / r805 PEX export header 同列强信号, 新增 FineSim export header 类型。
    stimulus_IPWM_FFE_wiCH.sp header "Owner: alieenwu (run by thomasz for debug) / Date: 2026-11-04 / Testbench: SIM_P2S_TX_FFE_IPWM_CH"
    = 真实 owner + 真实 testbench 名 + 真实 date, 强化 file-verbatim 信号。
  - 真实 /rundata 内网路径信号 (FineSimMetricCornerDiag + FinesimLogExplainDiag):
    FineSimMetricCornerDiag stimulus_*.sp ".include '/rundata/lacaa/V0/simdir/finesim/wo..." + "* User: e0024852 Bitcell: hd_CH252" 真实用户+真实 bitcell 名,
    FinesimLogExplainDiag SS1.06V-40C.log "# Path: /rundata/drgqa/V0/simdir/finesim/workdir/alrenc/REVC_CoreTiming/Final_0831/..." 真实 /rundata 路径
    + lsf_job_error.log "FSDB Reader, Release Verdi_T-2022.06-Beta0 ... 09/07/2026 / 11/04/2026 / 11/09/2026" 真实 FSDB Reader banner (真实多日期),
    = 真实 /rundata 内网路径 + 真实 FSDB Reader banner + 真实 measurement names (tWLon/tSAon) ⇒ file-verbatim。
  - 真实 /proj 内网路径信号 (FinesimLaunchAgent): config_A.json
    "stim_file: /proj/drvqa/V0/workdir/zjqiao/verilog.ddr5.drvqa.vecgn_1019/vec_20261109/sim.saved" 真实 /proj/drvqa 路径 + 真实 user zjqiao + 真实 netlist 名
    "Netlist_Vcap_20261112PM_Fullchip_Compress", TASK.md 含真实用户原话 verbatim (zjqiao DDR finesim 仿真启动 agent 需求),
    host=hfhds206 计算节点 + 真实 /proj 内网路径 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)。
  - track≠asset_provenance 再证 (FifoStimulusGen): track=synthesized (prompt 重构为 produce-tool generator 接口) 但 asset=A-faithful
    (FIFO_TOP.netlist "faithful trimmed netlist, real port names from trace z7n9b" + example_stimulus.sp "作者: curryxu 日期: 2026-11-03" 真实用户+真实日期),
    累计 r801-r806 共 7 例 track≠asset_provenance (BatchHspiceSubmit/AgingScriptAnalyze/CellLeakageIvPlot/ClampPwrStateExtract/CmlBwExtensionHandbook + r806 FifoStimulusGen),
    两字段独立再证: track 记 prompt 忠实度, asset_fidelity 记输入 A 文件来源。
  - 1 no-asset 首例 in batch6 (FineSimCoreCounter): attachments=[] (Q&A-which/analysis → produce-report-tool reframe,
    SUT 从 workdir 下的 methodology.md + lsf_server_list.csv 由 RAG/trace verbatim 生成, 0 attachment 入 A)。
  - 3 synth_deck 均 reframe_note 显式 "asset_fidelity=synth_deck" (FineSimDcConvGuide "用自包含合成 FineSim doc corpus" /
    FineSimDiag "用自包含合成 5 报错日志" / FinesimConvDiag "用自包含合成 error_log.txt/run_cmd.txt/netlist_snippet.sp/option_finesim.sp"),
    portability reframe (真实 /proj /apps doc/log SUT 沙盒不可达)。
  - 2 synth_data: DutySkewAvg track=synthesized + asset CSV/JSON 数据 fixture 无 in-file provenance marker (无真实路径/hostname/header) ⇒ default synth_data;
    FineSimIntroGuide reframe_note 显式 "asset_fidelity=synth_data" (corpus.jsonl 合成知识语料)。
  - A-faithful 6/12=50% 追平 r804/r805 单批最高 (r801=3, r802=3, r803=4, r804=6, r805=6, r806=6):
    本批覆盖 F 段 FineSim-family + FIFO 域 case, 真实 .sp/.log/.csv/.json/.md/.netlist 文件 verbatim/excerpt/faithful-compact 自 trace。

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
    "EDA-Eval-DesignFlow-DutySkewAvg-001": (
        "synth_data",
        "edges_A.csv = 合成 edge-time 数据 fixture (4069B, 列 sig/dir/idx/time, out0..out3 + dut 信号, time 含 'error' 字面量占位, "
        "无真实 user/path/hostname header); cfg_A.json = 合成 task 配置 fixture (245B, delay/tstop/number/duty/vth/edge/skew/wrap_period, 通用字段); "
        "prompt.txt = 真实用户原话 verbatim 含真实 '/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/003_gain/002_wckdiff_gain_tran.sp' 内网路径 (prompt 非 asset); "
        "track=synthesized; reframe=FineSim edge-time duty/skew 平均器->produce-tool (analysis->produce-tool parser+calculator); "
        "asset CSV/JSON 数据 fixture 无 in-file A-faithful 强信号 (无真实路径/hostname/header/excerpt marker) ⇒ default synth_data (r804 strict rule)",
    ),
    "EDA-Eval-DesignFlow-FifoDelayOptDiag-001": (
        "A-faithful",
        "fifo_sel_A.sp = 真实 FIFO_TOP 选择器 HSPICE 网表 verbatim (header '* FIFO_TOP selector critical-path netlist (faithful compact representation) / "
        "* Source: cline trace 1793928990578_ltkg1 (curryxu@hfeg0pkn001), user-accepted delay analysis' 即 'faithful compact representation' 忠实紧凑表示标注 (r806 首例), "
        "含真实子电路名 invFx1_sub_Fifo/invFx2_sub_Fifo/invFx4_sub_Fifo/nand2Tx1_Fifo/invenTx4_sub/passgtFx1_sub_Fifo(W=100n 最弱) + 真实信号名 Nibble_Sel0/Sel<5:0>/DNNER/DNNOF/DNNEF/DNNOR + 真实 .param VDD=0.75V); "
        "task_brief.md = 任务框架; track=faithful; attachment desc 显式 'A-faithful 资产：FIFO_TOP 选择器 HSPICE 网表...来自 trace curryxu@hfeg0pkn001 ltkg1 真实电路（忠实紧凑表示，保留真实信号名/子电路名/实例名）'; "
        "'faithful compact representation' + 真实 Source trace 引用 + 真实子电路/信号名 ⇒ file-verbatim (r806 verbatim 标记族扩展首例); "
        "reframe_note=FIFO 关键路径延迟优化诊断 Q&A->produce (§4 有牙必要, r726 spotcheck batch6); reframe 由 Q&A-driver 非配额驱动",
    ),
    "EDA-Eval-DesignFlow-FifoStimulusGen-001": (
        "A-faithful",
        "netlist/FIFO_TOP.netlist = 真实 FIFO_TOP 24-bit DDR4 FIFO 网表 verbatim 裁剪 (header '* A: M2701 FIFO_TOP 24-bit DDR4 FIFO (faithful trimmed netlist, real port names from trace z7n9b)' 即 'faithful trimmed netlist, real port names from trace' 忠实裁剪表示标注 (r806 首例群第二例), "
        "含真实 @ports_in/out/supply 端口清单 CLK_Sample/D<0..23>/Nibble_Sel0..2/Dout<*>/Sel<*>/vcc!/vss! 等 + .subckt FIFO_TOP 真实子电路头); "
        "example_stimulus.sp = 真实 13-Section testbench 激励 verbatim (7637B, header '作者: curryxu / 日期: 2026-11-03 / 项目: m2701 (HL22 22ULL)' 真实用户+真实日期+真实项目); "
        "task_brief.md = 任务框架; track=synthesized; reframe_note=HSPICE FIFO_TOP 24-bit DDR4 TB 激励生成器->produce-tool (harness produce-action TB-stim file->produce-tool tb-stim generator reframe, §4 有牙必要, r749 spotcheck batch27); "
        "'faithful trimmed netlist, real port names from trace' + 真实用户 curryxu + 真实日期 2026-11-03 + 真实项目 m2701 ⇒ file-verbatim; "
        "track=synthesized 但 asset=A-faithful ⇒ track≠asset_provenance 再证 (r801-r806 累计 7 例, track 记 prompt 忠实度 asset 记输入 A 文件来源, 两字段独立); "
        "reframe 由 harness-driver (hidden-B cross-input 牙齿驱动, TB stim file→generator script for 不同 netlist ports) 非配额驱动",
    ),
    "EDA-Eval-DesignFlow-FineSimCoreCounter-001": (
        "no-asset",
        "attachments = [] (0 attachment); track=None; reframe_note=FineSim 总核数统计报告器->produce-tool (Q&A-which/analysis->produce-report-tool reframe, §4 有牙必要, r754 spotcheck batch32); "
        "trace mwxi@hfhds228 问「给我现在 finesim 的总核数」, case 收敛为 produce-tool (finesim_core_counter.py 真跑读 CSV 产 JSON 报告); "
        "workdir 下 methodology.md + lsf_server_list.csv 由 SUT 从 RAG + trace verbatim user turns 生成 (非 attachment 入 A); "
        "0 attachment ⇒ no-asset (Q&A-which/analysis 域 case, 与 canonical vocab no-asset 定义一致); batch6 首例 no-asset",
    ),
    "EDA-Eval-DesignFlow-FineSimDatacardDiag-001": (
        "A-faithful",
        "pvt.log = 真实 FineSim 仿真日志 verbatim (header 'FineSim (R) Version U-2023.03-2 for linux64 - Apr 25, 2023 ... *** job run at hfeg0pkn002 (linux64) on Wed Nov 4 17:28:04 2026 ... using 8 cpus' 即真实 FineSim export banner 含真实 tool-version U-2023.03-2 + 真实 hostname hfeg0pkn002 + 真实 date 2026-11-04 (与 trace_source session 1793843108682 时间一致), r806 FineSim export header 强信号首例); "
        "stimulus_IPWM_FFE_wiCH.sp = 真实 FineSim stimulus verbatim (header '* Testbench: SIM_P2S_TX_FFE_IPWM_CH (DDR PHY TX FFE IPWM DqIoTop) / * Simulator target: FineSim (spicead mode) / * Model: V2B HKMG / * Owner: alieenwu (run by thomasz for debug) / * Date: 2026-11-04' 真实 testbench 名 + 真实 owner + 真实 date); "
        "model_include_summary.txt + task_brief.md + scenario.txt + requirements.json = 任务框架; track=None; "
        "reframe_note=diagnose Q&A->produce (§4 有牙必要, r720 spotcheck batch2); reframe 由 Q&A/diag-driver 非配额驱动; "
        "真实 FineSim export banner (tool-version + hostname + date) + 真实 testbench 名 + 真实 owner ⇒ file-verbatim (与 r804 AETHER-SE / r805 PEX export header 同列强信号, r806 新增 FineSim export header 类型); "
        "host=hfeg0pkn002 计算节点 + asset 含真实 hostname hfeg0pkn002 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-FineSimDcConvGuide-001": (
        "synth_deck",
        "sim/run.log = 合成 FineSim DC 不收敛仿真日志 fixture (reframe_note 显式 '用自包含合成 FineSim doc corpus 保留真实任务结构(asset_fidelity=synth_deck)'); "
        "sim/netlist.sp = 合成 hspice netlist fixture; sim/doc_ref.json = 合成 doc 引用 fixture; task_spec.json = 合成 task 规格; "
        "track=None; reframe_note=FineSim DC 不收敛原因/方案查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11); "
        "真实 /apps/synopsys FineSim doc corpus SUT 沙盒无 license/路径不可达 ⇒ asset 为合成 doc corpus 供 guide generator 开发",
    ),
    "EDA-Eval-DesignFlow-FineSimDiag-001": (
        "synth_deck",
        "run_prohd.sh + netlist.sp + tailor.sp + macro_ports.txt + error_logs/{stage1,detect_prep,xa}.log + detect/{racing.vec,racing.inc,detect.sp} = 合成 5 报错日志 + dspf-tool 表征流脚本 fixture (reframe_note 显式 '用自包含合成 5 报错日志保留真实任务结构(asset_fidelity=synth_deck)'); "
        "track=None; reframe_note=FineSim 5 连报错诊断->produce (portability+Q&A->produce reframe, §4 有牙必要, r731 spotcheck batch10); "
        "真实 FineSim/PrimeSim 报错日志来自 /rundata 内网 + XA license 不可沙盒复刻 ⇒ asset 为合成 5 报错日志 + 表征流脚本供 diagnose_finesim_errors.py 开发",
    ),
    "EDA-Eval-DesignFlow-FineSimIntroGuide-001": (
        "synth_data",
        "doc/corpus.jsonl = 合成 FineSim 知识语料 fixture (每行 JSON 对象 id/source/topic/content, topic ∈ {what_is, function, characteristic, advantage, summary}, reframe_note 显式 '用自包含合成 corpus.jsonl 保留真实任务结构(asset_fidelity=synth_data)'); "
        "doc/query.log = 合成查询日志 fixture (key: value 行格式, query/query_normalized/simulator_name/kb_hit_status/kb_note); task_spec.json = 合成 task 规格; "
        "track=None; reframe_note=FineSim 介绍查询->produce (portability+Q&A->produce candidate reframe, §4 有牙必要, r732 spotcheck batch11); "
        "真实 ask-eda KB (/apps 知识库) SUT 沙盒不可达 ⇒ asset 为合成 corpus.jsonl 供 simulator_intro_guide.py 开发",
    ),
    "EDA-Eval-DesignFlow-FineSimMetricCornerDiag-001": (
        "A-faithful",
        "sim/stimulus_pex_rev06_model_rev04_presim.sp = 真实 FineSim post-PE stimulus verbatim (header '* FineSim post-PE stimulus for hd_CH252_bitcell (PEX rev06 / model rev04) / * User: e0024852  Bitcell: hd_CH252  Corner: TT only (no .alter sweep)' 真实用户 e0024852 + 真实 bitcell 名 hd_CH252 + 真实 PEX rev06/model rev04, 含 .include '/rundata/lacaa/V0/simdir/finesim/wo...' 真实 /rundata/lacaa 内网路径); "
        "sim/stimulus_*.log = 真实 FineSim log verbatim (header '* FineSim log (V-2023.12-1) / * start: 02-NOV-2026 13:14:22' 真实 FineSim tool-version V-2023.12-1 + 真实 date 02-NOV-2026); "
        "sim/stimulus_*.md0 = 真实 FineSim measure dump verbatim (header '* FineSim measure dump (V-2023.12-1) / * corner: tt_sram_dbc VVDD=0.75 TEMP=25 / * bitcell: hd_CH252 (no .alter blocks -> single run)' 真实 corner + 真实 bitcell + 真实 measure 数据 iread/ileak/iwrite/wnm_1/wnm_2); "
        "sim/35H_DBCFS_Model_SRAM_v0d1_Rev04.lib = 真实 SRAM bitcell model library verbatim (header '* 35H_DBCFS_Model_SRAM_v0d1_Rev04.lib / * SRAM bitcell model library (35H DBCFS process, rev04)' 真实 model lib 名 + 真实 35H DBCFS process + .lib tt_sram_dbc/.MODEL hd_pu_dbc/hd_pg_dbc/hd_pd_dbc 真实 model 名); "
        "task_spec.json = 任务框架; track=None; reframe_note=None; "
        "真实用户 e0024852 + 真实 /rundata/lacaa 内网路径 + 真实 FineSim tool-version V-2023.12-1 + 真实 bitcell hd_CH252 + 真实 model lib 35H_DBCFS_Model_SRAM_v0d1_Rev04 ⇒ file-verbatim; "
        "host=hfeg0pkn002 计算节点 + asset 含真实 /rundata 内网路径 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-FinesimConvDiag-001": (
        "synth_deck",
        "doc/error_log.txt + run_cmd.txt + netlist_snippet.sp + option_finesim.sp = 合成 FineSim 瞬态不收敛报错日志 + 仿真命令 + 网表片段 + option 设置 fixture (reframe_note 显式 '用自包含合成 error_log.txt/run_cmd.txt/netlist_snippet.sp/option_finesim.sp 保留真实任务结构(asset_fidelity=synth_deck)'); "
        "task_spec.json = 合成 task 规格; track=B; "
        "reframe_note=FineSim 瞬态不收敛根因诊断->produce (portability+Q&A/diag->produce candidate reframe, §4 有牙必要, r733 spotcheck batch12); "
        "真实 /proj 工程 + FineSim 环境 SUT 沙盒不可达 ⇒ asset 为合成报错日志+网表片段+option 供 finesim_conv_diag 报告器开发",
    ),
    "EDA-Eval-DesignFlow-FinesimLaunchAgent-001": (
        "A-faithful",
        "config_A.json = 真实 matrixrun 仿真配置 verbatim (539B, 'project: drvqa / version: V0 / stim_file: /proj/drvqa/V0/workdir/zjqiao/verilog.ddr5.drvqa.vecgn_1019/vec_20261109/sim.saved' 真实 /proj/drvqa 内网路径 + 真实 user zjqiao + 真实 vecgn_1019/vec_20261109 日期目录, 'netlist_file: Netlist_Vcap_20261112PM_Fullchip_Compress' 真实 netlist 名, 'queue: fqueue3_drvqa / control: control.finesim_promd_vcap / matrixrun / sim_cpu: 16 / sim_simulator: primesim / sim_simver: 2025 / opt_array: true / opt_tdv: true' 真实 matrixrun 配置字段); "
        "TASK.md = 真实任务说明 verbatim (含真实用户原话 'zjqiao 的真实需求（finesim 仿真）：这个代码是我进行 finesim 仿真的代码，现在我希望你能创建一个 agent...' + matrixrun 命令 schema + --dry-run 输出格式); "
        "track=None; reframe_note=None; trace_source zjqiao@hfhds206 sess 1794474782925_5ityn mc404; "
        "真实 /proj/drvqa 内网路径 + 真实 user zjqiao + 真实 netlist 名 Netlist_Vcap_20261112PM_Fullchip_Compress + 真实用户原话 verbatim ⇒ file-verbatim; "
        "host=hfhds206 计算节点 + asset 含真实 /proj 内网路径 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
    ),
    "EDA-Eval-DesignFlow-FinesimLogExplainDiag-001": (
        "A-faithful",
        "doc/SS1.06V-40C.log = 真实 FineSim CRG Core Timing measurement report verbatim (header '# Path: /rundata/drgqa/V0/simdir/finesim/workdir/alrenc/REVC_CoreTiming/Final_0831/Result/SS1.06V-40C.log' 真实 /rundata/drgqa 内网路径 + '# Corner: SS (Slow-Slow) / 1.06V / -40C' 真实 corner + 44 MEASURE 语句含真实 measurement 名 pvpcsg/pvcc/pvwlp/tWLon=failed/tSAon=failed/tWL/tCS/tSEN/tRCD/tRAS/tRP/tWR 真实 CRG Core Timing 指标名); "
        "doc/lsf_job_error.log = 真实 LSF job error log verbatim (header '# Path: /rundata/drgqa/...' 真实 /rundata/drgqa 内网路径 + 'FSDB Reader, Release Verdi_T-2022.06-Beta0, RH Linux x86_64/64bit, 09/07/2026 / 11/04/2026 / 11/09/2026' 真实 FSDB Reader banner 含真实多日期); "
        "doc/scenario.txt = 任务框架; track=None; reframe_note=diagnose Q&A->produce (§4 有牙必要, r720 spotcheck batch2); "
        "真实 /rundata/drgqa 内网路径 + 真实 FSDB Reader banner (真实多日期 09/07/11/04/11/09) + 真实 measurement names (tWLon/tSAon + CRG Core Timing 指标) ⇒ file-verbatim; "
        "host=hfeg0pkn005 计算节点 + asset 含真实 /rundata 内网路径 ⇒ 推断 file-verbatim (r803 .75-reachable 判别)",
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

    print("=== 档2 asset_fidelity backfill r806 batch6 ===")
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
    manifest_path = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/metadata_backfill_tier2_r806_manifest.tsv"
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write("case_id\tasset_fidelity\trationale\n")
        f.write("# metadata_backfill_tier2_asset_fidelity_r806_manifest.tsv — r806 (2026-11-18) metadata-debt backfill 档2 (asset_fidelity) apply, batch6 (12 cases, alphabetical next 12 missing after r805 batch5 DupSubcktDefDiag: DutySkewAvg..FinesimLogExplainDiag, F 段)\n")
        f.write("# 背景: r771 bounded queue spec 档1→档3→档2. r772 档1 (level→layer 160 cases) done. r773-r800 档3 (reframe_note 32→235) done. r801-r805 档2 batch1-5 (+60, 106→166) done. 本轮 r806 档2 batch6.\n")
        f.write("# 档2 asset_fidelity 字段语义: 输入 A 来源 (A-faithful=真实 trace-verbatim/真实 paste/真实 scp / synth_*=合成 fixture / no-asset=0 附件 Q&A); hidden B 一律 synthesized (§4.1, 不重复记)\n")
        f.write("# 判据: 逐题读 prompt 资产/附件描述 + attachments 文件 header + track 字段 + reframe_note driver; A-faithful 强信号 = 真实 AETHER-SE/VCS/HSPICE/PEX/FineSim/FSDB export header (含真实 user/date/library/tool-version) / 真实内网路径 .inc/.lib/.spf / verbatim excerpt '(excerpt from ...)' / 'reproduced faithfully from cline trace' / 'faithful compact/trimmed representation' 标注 / 真实 hostname / 真实内部 edit note; synth 信号 = track=synthesized / '(reconstructed from cline trace ...)' / desc 显式 '合成' / 通用名文件 / A_ONLY_MARKER + decoy\n")
        f.write("# 关键发现: 'faithful compact/trimmed representation' verbatim 标记族扩展首例群 (FifoDelayOptDiag 'faithful compact representation' + FifoStimulusGen 'faithful trimmed netlist, real port names from trace', 与 r805 'reproduced faithfully' 同列) / 真实 FineSim export header 强信号首例 (FineSimDatacardDiag pvt.log 'FineSim (R) Version U-2023.03-2 ... job run at hfeg0pkn002 ... Wed Nov 4 17:28:04 2026' 真实 tool-version+hostname+date, 新增 FineSim export header 类型, 与 r804 AETHER-SE / r805 PEX 同列) / 真实 /rundata 内网路径信号 (FineSimMetricCornerDiag .include '/rundata/lacaa/...' + FinesimLogExplainDiag '# Path: /rundata/drgqa/...' + 真实 FSDB Reader banner 多日期) / 真实 /proj 内网路径信号 (FinesimLaunchAgent config_A.json /proj/drvqa/V0/workdir/zjqiao/...) / track≠asset_provenance 再证 (FifoStimulusGen track=synthesized 但 asset=A-faithful, r801-r806 累计 7 例) / A-faithful 6/12=50% 追平 r804/r805 单批最高 (r801=3,r802=3,r803=4,r804=6,r805=6,r806=6) / 1 no-asset 首例 in batch6 (FineSimCoreCounter attachments=[] Q&A-which/analysis) / 3 synth_deck 均 reframe_note 显式 / 2 synth_data (DutySkewAvg default + FineSimIntroGuide 显式)\n")
        f.write("# apply: cases/B/<case>.json metadata 末位 key; 双存储同步 build_jsonl.py --shard B rebuild; asset_fidelity 166→178 (cases/B 178==B.jsonl 178 ✓); miss 229→217\n")
        for cid, (val, rationale) in BATCH.items():
            f.write("%s\t%s\t%s\n" % (cid, val, rationale))
    print("\nmanifest written:", manifest_path)


if __name__ == "__main__":
    main()
