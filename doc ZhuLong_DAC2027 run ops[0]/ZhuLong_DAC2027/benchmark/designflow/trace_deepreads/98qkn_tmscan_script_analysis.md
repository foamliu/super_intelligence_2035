# deepread: 98qkn — pyAether TM-Scan auto-check script analysis Q&A

- **session**: `1793945136541_98qkn` · user `e0039102` · host `10.129.2.10` (= hfeg0pkn005, on .75 local as e0039102/guest) · mc=48 · domain schematic_netlist
- **trace file**: `/home/e0039102/.cline/data/sessions/1793945136541_98qkn/1793945136541_98qkn.messages.json` (355 KB, 73 msgs, world-readable on .75)
- **scan keywords**: `netlist:54;schematic:47;verilog:45;lvs:43;dbget:31;cmos:22;aether:128;pyaether:73`

## User intent (verbatim U[0])
```
>>> load("/home/zixuguo/AutoTMScan/CXMTAutoTMScan_V10.py")
>>> CXMTseAutoTMCheck_GUI()
你帮我看看这好像是处理文件的脚本，处理哪个文件？
```
**Translation**: "Help me look — this seems like a file-processing script. What file does it process?"

The user was given a script path by a colleague and wants to understand what the script does and what files it takes as input.

## Real trace shape (multi-turn code-grounded script-analysis Q&A)

| msg | role | content |
|---|---|---|
| 0 | user | verbatim question above |
| 1–20 | assistant | `get_agent_policy_status`, `list_allowed_files`, `read_files` (script is 1158 lines, read in chunks), `search_codebase` |
| 21 | assistant | **gold-standard analysis (2373 chars)**: V10 doesn't exist at the load path (only V0/V1 in `AutoTMScan/`); the script is a pyAether TM-Scan auto-check tool for CM cells; input files = `HierPathFile` (critical, format `CM_Block 层次路径`), design DB schematics via `ae.dbOpenCV(lib, cell, "schematic")` (T_Cm*Latch / Cm*Latch, top cell `ddgoa_cmos_top/LP5TOP`), `/proj/{proj}/V0/setup/aether.rc.cdl` (emp-short-cell-list), Step 5 verilog netlist (`/rundata/ddgoa/V0/.../V0_WOWTOP_2026Oct15.193816/netlist`, `-top WOWTOP`); intermediate products Step0–Step4 + out_files/; data flow HierPathFile + CM schematic → Step1 MA addr → Step2 hier path → Step3 top net trace → Step4 CSV → Step5 DDV check; hardcoded points (project names ddgoa/drgpa/…, top cell LP5TOP, Step 5 verilog path + `-top WOWTOP` at line ~151) |
| 22–26 | user | "我刚刚给你的是自动检查工具对吗？检查对象这里没有吗？" / "检查对象需要我提供吗？" / re-asks the original question with more context |
| 23–25 | assistant | explains **check objects** = GUI "CM Cells" field, default 7 CM blocks for ddgoa (CMAryA, CMCenterR, CMCenterL, CMDqL, CMDqR, CMRight, CMLeft), auto-scan `^CM[a-zA-Z]*$` for other projects; **5 error types** ERROR1–5 (same MA→different testmode / same testmode←different MA / net MA vs label CmAdr/MA<n>< / CmOp port / MA duplicate); only `HierPathFile` must be user-provided |
| 27–37 | assistant | locates V10 at `/home/zixuguo/testmode/CXMTAutoTMScan_V10.py`; finds `HierPathFile` already configured there with 7 CM blocks; **warns V10 is a debug version** (Step 2 logic commented out, only sed first 10 lines for test) |
| 38–52 | user/assistant | "这个必需图形界面操作吗？" → assistant: GUI not required but Aether env required; pyAether bridge service down; delivers NoGUI wrapper `/home/e0039102/CXMTAutoTMScan_NoGUI.py` |
| 53–54 | user/assistant | "这属于数字还算模拟前端还是后端" → assistant: **custom-digital frontend verification** (pre-tapeout check), between circuit design and netlist freeze |
| 55–72 | user/assistant | user confirms with colleague to use V1; assistant delivers final execution manual + one-line command |

## Asset reachability
- Real script `/home/zixuguo/AutoTMScan/CXMTAutoTMScan_V1.py` (1158 lines) and `/home/zixuguo/testmode/CXMTAutoTMScan_V10.py` (1158 lines) are **world-readable on .75 local**.
- Real `HierPathFile` at `/home/zixuguo/testmode/HierPathFile` (14 lines, 7 CM blocks) is readable.
- **Decision**: B档 (synthesized) — reconstruct a faithful archetype (~190 lines) using the real trace identifiers (ddgoa, CMAryA, LP5TOP, WOWTOP, CXMTse…, Step1_allCMAdr_MAandOP, HierPathFile, ERROR1–5, aether.rc.cdl, /rundata/ddgoa/…). The archetype captures the full structure (GUI fields, Step0–5 pipeline, 5 error checks, dbOpenCV, hardcoded paths, cell list). Hidden B = identifier-renamed (CXMT→BMXT, ddgoa→ddgob, CM→BM, LP5TOP→TP5BOT, WOWTOP→WOWBOT, MA→MB, 2026Oct15→2026Nov15, HierPathFile→HierPathCfg, …) with **zero A-only token leakage** (word-boundary verified).

## Sub-type
**code-grounded pyAether-script analysis Q&A** (schematic_netlist). User asks "what file does this script process?"; gold standard = static analysis of the script extracting tool purpose, input/output files, hardcoded paths, GUI fields, functions, error codes, step files, cell names, EDA API calls, top cell, data flow. Distinct from r806 (bash-script analysis) and r807 (SV/Tcl sim-env analysis) — this is a **pyAether/Aether Python tool** with EDA-specific API calls (`ae.dbOpenCV`, `ae.aeCreateComboField`, `ae.geCreateStringField`).

## Case design
- **case_id**: `EDA-Eval-DesignFlow-TmScanScriptAnalysisQA-001`
- **A档 prompt**: verbatim U[0] (red-line #2: 不脱敏, 原文)
- **asset A**: `CXMTAutoTMScan_V10.py` (archetype, real trace identifiers) + `HierPathFile` (14-line config)
- **hidden B**: `BMXTAutoTMScan_V10.py` + `HierPathCfg` (renamed, in `assets/<id>/hidden/` + `reference/<id>/hidden_B/`)
- **candidate_ref.py**: general static Python-script analyzer → JSON with 14 top-level keys (tool_purpose, input_files, output_files, hardcoded_paths, gui_fields, function_names, error_codes, step_files, other_files, cell_names, api_calls, dbopen_cells, top_cell, data_flow, cited_identifiers). CLI `python3 candidate.py <asset_dir>`. No hardcoded identifiers.
- **check.py**: 15 conds (a–o). Runs SUT candidate on B, verifies B ground-truth (HierPathCfg, /rundata/ddgob/…WOWBOT…, BMXTseAutoTMScan_main, ERROR1–5, Step1_allBMAdr_MBandOP/Step3/Step4, ≥4 of 7 BM cells, top_cell=TP5BOT/ddgob_cmos_top, ≥3 gui fields with BM prompt), anti-hardcode (zero A-only tokens in B output, word-boundary), 3-run md5 determinism.
- **self-verify**: ref 15/15 PASS · 5 negatives (empty/print_only/core_deleted/naive_hardcode_a/naive_partial) all FAIL · NEG_RC=0 · 3-run md5 stable · A≠B confirmed (candidate on A yields ddgoa/CMAryA/LP5TOP, on B yields ddgob/BMAryA/TP5BOT).
