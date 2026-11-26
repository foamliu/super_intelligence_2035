# r710 deepread — fx2mf (FineSim MatrixRun dir explain Q&A)

## Trace
- session: `1793672369557_fx2mf` (subdir `1793672369557_fx2mf/`)
- user: `johnl` @ `10.129.2.10` (`hfeg0pkn001`), mc=39 (1115_081559 快照) / mc=104 (旧 1105 池)
- domain: spice_sim (characterization matrix-run flow)
- keywords: netlist:665; drc:500; waveview:45; hspice:7; synopsys:4
- trace: 318KB / 34 msgs / agent=lead / 1 substantive user turn (session cut off by code_sidecar_sigterm at msg[33] before final text delivery)

## User turns (verbatim)
- U#0: `/rundata/drcoa/V0/simdir/finesim/drcoaF/MatrixRun/MatrixRun_Netlist_SpfBA_20260807PM_mBist 你看下这些文件什么意思`

## Directory (real, from trace list_allowed_files + python-runner categorization)
- root: `/rundata/drcoa/V0/simdir/finesim/drcoaF/MatrixRun/MatrixRun_Netlist_SpfBA_20260807PM_mBist`
- TOTAL entries: 294 · SUBDIRS: 13 · top-level files: 197
- 8 flow scripts (pipeline 01→05):
  - `01_gen_measures.py` — parse waveview, gen SPICE measure statements (D0/D1/LP/LN threshold crossing), output measure.sp. COMPANY CXMT / DE-DDR DDT1 / AUTHOR johnlee / REVISION FINAL_CONT_V2. threshold_multiplier default 0.5.
  - `01_gen_signal_measure_trtf_duty.py` — signal measure (trtf = transition/rise-fall, duty)
  - `02_measure_fscript_gen.py` — for each corner measure.sp + raw/*.fsdb → generate fscript job `fsdb_measure_NNNN.sp` (40 lines, full verbatim in trace)
  - `02_signal_runsp_gen_trtf_duty.py` — signal runsp gen
  - `03_measure_run.sh` — run measure jobs
  - `04_margin_measure.py` — process .mt0/.pmt, calc min setup/hold time margin. FILE_PATTERN regex `[._]?[Tt](\d+)_(d0|d1|lp|ln)[_.]`, MARGIN_PATTERN SS/FF corner. parse_time_with_unit (ps/ns/us/ms→ns). HAS_PANDAS optional.
  - `04_signal_measure_report_trtf_duty.py` — signal measure report
  - `05_format_split.py` — split/format results (produces a_part_aa..az + aa..bz split fragments)
- 13 subdirs: margin_result, meas_log, minimal_patches, signal_result + 9 corner sim dirs:
  - `primesim.DFT_mBist_CPF_CheckerBoard_WPst_0P5_tCH_50_BL16_4b8g_B0M_8240_{FF,SS,TT}_NODLLK.x8.{FF1.3V-40C,FF1.3V110C,SS0.94V-40C,SS0.94V110C,TT1.1V25C}.X8`
  - CPF pattern: 4 corners (FF×2, SS×2); RF pattern: 5 corners (FF×2, SS×2, TT×1) = 9 total
- extension counts: sp:10, py:8, sh:5, log:2, bash_history:1, swp:1, presim:1, tmp:1, +大量无扩展名 split 碎片(a_part_aa..a_part_az, aa..bz)
- corner dir 内部 (msg[17]/[21]): finesim.elog(397KB), finesim.mt0(18KB), glitch_meas.*.pmt(2161 个, P1_S1..S7 × cm0 × ts_ismsel × FDEVHIGH/LOW/LOGICHIGH/LOW/MID/RDEV...), meas.*(581), raw/(0 fsdb 已删), ihnl/(0), netlist/netlistHeader/netlistFooter, runscript, control, force_power.inc, BiasTrimAccuracy, config_Alert/config_pincheck, crc_alert_chk.rpt

## Assistant behavior
- list_allowed_files(depth=2,limit=200) → 197 top-level files
- read_files: 01_gen_measures.py, 02_measure_fscript_gen.py, 04_margin_measure.py, 01_gen_signal_measure_trtf_duty.py
- 写 _categorize.py 用 python-runner 跑: 统计 294 entries/13 subdirs/extension counts/corner dir 内部结构
- 分析完整，但 **最终解释文本未交付**（msg[33] code_sidecar_sigterm，session 在清理临时脚本时被终止）
- THINK 中完整结论: corner dirs 含 raw/(fsdb 已删)/ihnl/, glitch_meas.pmt 2161 个, 5 PVT corners, CPF/RF 两 pattern

## Reframe (analysis-Q&A→produce, per 11-15 令 + r619-r709 family)
- 真实交付物 = 口头解释"这些文件什么意思"；reframe = 纯 stdlib `matrixrun_dir_explainer.py` 产结构化 JSON 讲解报告
- 解析 dir_manifest.json(目录清单) + flow_scripts/*.py(docstring/pipeline stage) + corner_sample.txt(corner dir 文件) + methodology.md(agent 流程理解) → explanation_report.json 6 sections
- Output: file_inventory / flow_pipeline / corner_matrix / measurement_semantics / flow_summary / stats, sort_keys=True, indent=2, deterministic
- **Distinct vs** r709 SrefOscTranFlow=tran.sp 仿真流程解析 / r708 PrbsTmSimOpt=电路+仿真分析 / r706 FineSimCoreCounter=LSF 核数统计 = **本例 MatrixRun characterization 目录结构化讲解（pipeline 01→05 + 9 PVT corners + 2 patterns + measure 语义）**

## Asset A (visible, real)
- A/dir_manifest.json (real: 294 entries, 13 subdirs, 9 corner dirs 真名, extension counts, 8 flow scripts 真名)
- A/flow_scripts/01_gen_measures.py (verbatim header + key: D0/D1/LP/LN, threshold_multiplier, measure.sp output)
- A/flow_scripts/02_measure_fscript_gen.py (verbatim full 40 lines)
- A/flow_scripts/04_margin_measure.py (verbatim header + key: mt0/pmt, setup/hold, FILE_PATTERN, parse_time_with_unit)
- A/flow_scripts/03_measure_run.sh (representative shell runner)
- A/flow_scripts/05_format_split.py (representative split)
- A/corner_sample.txt (real corner dir listing from trace: finesim.elog/mt0, glitch_meas.pmt, meas.*, raw/, ihnl/)
- A/methodology.md (agent 流程理解 verbatim: pipeline 01→05, CPF/RF, 9 PVT, glitch_meas 结构)
- A/task_brief.md + scenario.txt + requirements.json

## Hidden B (anti-hardcode, fully disjoint from A)
- B/dir_manifest_b.json: 产品 drcoh(≠drcoa), 版本 V2, 路径 MatrixRun_Netlist_SpfCD_20270115AM, 178 entries(≠294), 11 subdirs(≠13)
- B/flow_scripts_b/: stepNN_ 命名(≠NN_), step01_gen_meas.py/step02_meas_fscript_gen.py/step03_meas_run.sh/step04_margin_calc.py/step05_format_merge.py, 6 py(≠8)/4 sh(≠5)/8 sp(≠10)
- B/corner_sample_b.txt: primesim.elog/mt0, setup_meas.*.pmt/hold_meas.*(≠glitch_meas), raw/, inp/(≠ihnl)
- B corner dirs: primesim.DFT_mBist_MARCH_2N_WalkPath_0P4_tCL_40_BL8_2b4g_B1M_4120_{FF,SS,TT}_NODLLK.x4.{FF1.2V-40C,SS0.9V125C,TT1.0V85C}.X4 — pattern MARCH_2N/WalkPath(≠CheckerBoard), 7 corners(≠9), PVT 1.2V/0.9V/1.0V(≠1.3V/0.94V/1.1V), x4(≠x8)
- names ∩ A = ∅; values ∩ A = ∅

## 断言规划 (k=16, a0-a15)
a0 zip+A files · a1 py_compile · a2 entry(workdir,out_dir) · a3 B output valid JSON+6 keys · a4 B file_inventory.total_entries==B · a5 B extension_counts match B · a6 B flow_pipeline stages parsed (stepNN + roles) · a7 B corner_matrix N corners parsed (pattern/pvt/voltage/temp) · a8 B pattern==MARCH_2N(≠CheckerBoard A-leak) · a9 B measurement_semantics key concepts · a10 A-leak (B output 无 drcoa/CheckerBoard/01_gen_measures/FF1.3V) · a11 cross-input guard (A-out vs B-out differ: total/pattern/script-names/corner-count) · a12 A-grounding (A-out total==294, pattern CheckerBoard, 9 corners) · a13 determinism (B twice identical) · a14 flow_summary non-empty · a15 stats aggregated · 4 stubs FAIL (empty/print_only/hardcode_a/deleted_core)
