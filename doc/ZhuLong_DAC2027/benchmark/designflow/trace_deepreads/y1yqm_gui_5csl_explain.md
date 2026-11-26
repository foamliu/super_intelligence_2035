# Deepread — y1yqm · GUI_5csl.py code-explain Q&A

- **session**: `1794361270744_y1yqm`
- **user / host**: e0039120 @ hfeg0plg99 (10.129.8.231)
- **match_count**: 12 · **domain**: schematic_netlist
- **trace size**: 58 msgs / 283360 B (messages.json)
- **case_id**: `EDA-Eval-DesignFlow-GuiScriptExplainQA-001`
- **round**: r789 (2026-11-17), 11-15 revival mandate fifth wave
- **prior status**: parked 2026-11-14 as "weak / code-parse" → revived per 11-15 mandate as code-grounded file-explain Q&A

## 1. Trace shape

| idx | role | content (gist) |
|-----|------|----------------|
| 0  | user | 「请帮我解析一下GUI_5csl.py这个文件」 |
| 1-12 | assistant + tool | read_files GUI_5csl.py (743 lines, 30542 B) from `/home/e0039120/Documents/99-ForAITest/GUI_5csl.py` |
| 13 | assistant | **gold** — 9103-char 7-section structured analysis of GUI_5csl.py |
| 14 | user | 「帮我再看看dspf这pl脚本在干啥」 (pivot to a *different* file — out of scope for this case) |
| 15-57 | … | continued conversation about `dspf_run_for_ddgoa_msaq.pl`, `.inc` sweep optimize, `blasec28<552>` meaning, `delvtobl 40` derivation |

**Take**: U#0 is a clean, self-contained code-explain request. The gold (msg 13) is a fully-structured 7-section analysis (文件概览 / 领域背景 / 文件结构总览 / 详细模块分析 / 使用场景 / 代码质量评价 / 改进建议) — exactly the "explain this file" Q&A pattern. The downstream msgs (14+) pivot to a different file and are **not** part of this case.

## 2. Asset A — GUI_5csl.py (visible)

Reconstructed verbatim from the trace's `read_files` tool_results (the original file was deleted from 10.129.8.231's disk). 743 lines / 30542 bytes, AST-parse clean.

Structure:
- L1-7 imports (tkinter, scrolledtext, messagebox, os, re)
- L9 `SCRIPT_DIR`
- L11-24 `DELVTOBL_D0` / `DELVTOBL_D1` — per-corner Vt-offset tables (4 variants: `mixb`/`mixw`/`senb`/`senw`, ±26.2mv / ±28.6mv)
- L27-31 `idx_to_kct(gidx)` — maps global tap index -8..31 → `KCT{A-H}_YS{0-4}`
- L33-737 `SPGeneratorGUI` class — 16 methods:
  - `__init__` (880×900 tkinter GUI)
  - helpers: `_auto_group_name`, `_parse` (BL[ab]N regex), `_group_dir`
  - model replace: `_detect_defaults`, `apply_model_replace`
  - temperature: `apply_temperature`
  - pattern: `apply_pattern`
  - **core**: `_calc_kct` (40-position circular tap ring; 8-tap window centered on target BL; TG pattern drives window, BG pattern fills remaining 32)
  - build: `_build_bl_params`, `_build_sp` (FineSim .sp deck), `_invert`, `_apply_dv`
  - emit: `_write_run`, `generate`, `preview`
  - batch: `batch`, `regen_overwrite`, `_generate_total_run_script`, `_do_batch`
- L739-743 main entry

Domain: **DDR memory CSL (Column Select Line) read characterization**. Generates **FineSim** .sp netlists. KCT/KCBG = TG/BG control-signal patterns. BL = BLa/BLb (12 each, 24 total). Measure node `blasec28<552+bl_num>`.

## 3. Hidden B — GUI_wl_generator.py

Structurally-similar but **token-disjoint** Python tkinter GUI script, hand-authored to share the architectural pattern (tkinter GUI + param table + circular-tap pattern engine + batch state-0/state-1 generation + run-script writer) while using a completely different domain vocabulary:

- Class `WLGenApp` (vs `SPGeneratorGUI`)
- Domain **LPDDR4 Write-Leveling** (vs DDR Bitline)
- Output **HSPICE** .sp decks (vs FineSim)
- `WLOFFSET_D0` / `WLOFFSET_D1` tables, corners `fast`/`slow`/`typ`/`wk` (vs `DELVTOBL_*`, `mixb`/`mixw`/`senb`/`senw`)
- `idx_to_wldly(gidx)` → `WLDLY{A-H}_RP{0-4}` (vs `idx_to_kct` → `KCT*_YS*`)
- `WLDBG` (vs `KCBG`)
- Measure `wlsec16<200+wl_num>` (vs `blasec28<552+bl_num>`)
- Filenames `WLd0.sp` / `WLd1.sp` (vs `BLa0.sp`)
- Window 900×820 (vs 880×900)
- `pvwlh` drive voltage (vs `pvblh`)
- `wloffset` (vs `delvtobl`)
- Methods renamed with `_wl` suffix

808 lines, AST-parse clean. **Verified zero overlap** with all 20 A-only forbidden tokens.

## 4. Task pattern — code-grounded file-explain Q&A (candidate.py)

Unlike the r788 Aether KB-Q&A case (candidate reads a *KB dir* of markdown), this case has the candidate read a *single Python script file* and emit a 7-key JSON explanation. The candidate must use **AST + keyword scanning** to analyze whatever script it is given — not hardcode any particular script's identifiers.

CLI: `python3 candidate.py <script_path>` → JSON on stdout with keys:
`question / script_summary / purpose / key_components / workflow_steps / cited_identifiers / overall_function`

The reference `gui_explainer_ref.py` uses `ast.parse` to extract class names, method names, module-level functions/constants, and imports, then synthesizes the 7-key JSON from that structural information plus keyword scanning (detect `tkinter`/`tk.Tk()` for GUI framework, `.sp`/`spice`/`netlist`/`.tran`/`.MEASURE` for SPICE-deck purpose). `cited_identifiers` is ordered class → module_consts → module_funcs → methods so distinctive domain constants (e.g. `WLOFFSET_D0`, `idx_to_wldly`) surface before the long method list fills the cap.

## 5. check.py — 12 assertions (a-l)

| # | label | check |
|---|-------|-------|
| ① | a | submit.zip contains candidate.py |
| ② | b | candidate.py py_compile passes |
| ③ | c | stdout is valid JSON with 7 required top-level keys |
| ④ | d | script_summary non-empty string, len ≥ 30 |
| ⑤ | e | purpose mentions GUI framework (tkinter/GUI) AND SPICE/.sp netlist generation |
| ⑥ | f | key_components is a list of ≥ 3 dicts (name+role), every `name` appears in B source |
| ⑦ | g | workflow_steps is a list of ≥ 4 strings covering init→build→generate→batch |
| ⑧ | h | cited_identifiers is a list of ≥ 5 strings, every one appears in B source |
| ⑨ | i | overall_function non-empty, mentions SPICE/.sp netlist |
| ⑩ | j | B-grounding: output contains ≥ 1 B-only token (WLGenApp/WLOFFSET_D0/idx_to_wldly/WLDLY/wlsec/hspice/Write-Leveling/WLDBG/wloffset/pvwlh/WLd0/WLd1) |
| ⑪ | k | anti-hardcode: output contains NO A-only token (GUI_5csl/SPGeneratorGUI/DELVTOBL_D0/idx_to_kct/KCTA_YS0/blasec28/552/pvblh/finesim/mixb/mixw/senb/senw/BLa0.sp//proj/ddgoa/delvtobl/sec28) |
| ⑫ | l | determinism: 3 runs produce byte-identical JSON |

k_rationale == k_check == 12 ≥ 8 GATE PASS.

## 6. Self-verify results

- **ref**: 12/12 PASS (gui_explainer_ref.py on hidden B)
- **5 negatives** all FAIL with **distinct** assertion labels:
  - `empty_zip` → assertion_a (no candidate.py)
  - `fake_empty` (broken syntax) → assertion_b (py_compile)
  - `fake_print_only` (non-JSON) → assertion_c (invalid JSON)
  - `fake_core_deleted` (key_components=[]) → assertion_f (core content)
  - `fake_print_expected` (A-leak) → assertion_k (anti-hardcode)
- NEG_RC = 0 (no negative passed)
- §4.9 three degenerate submissions (empty / print-only / core-deleted) all FAIL ✓
- **generalization**: candidate on A produces A-specific identifiers (SPGeneratorGUI/DELVTOBL_D0/idx_to_kct) — different output from B, proving the candidate genuinely analyzes the input rather than printing a canned answer ✓
- **determinism**: 3 runs on B → identical md5 (87ae1b64c9619c28880c590c0327c005) ✓
- **byte-sync**: jsonl `test` field == disk `check.py` (15183 B) ✓
- **SUT-sandbox safety**: attachments = [GUI_5csl.py, task_brief.md] only; no reference/ or hidden/ leak ✓

## 7. Ledger / coverage

- ledger: `1794361270744_y1yqm` → `case` (EDA-Eval-DesignFlow-GuiScriptExplainQA-001)
- D.jsonl: 450 → 451
- coverage: 436 → **437 / 2907 mc≥10 = 15.0%**

## 8. Notes

- This is the **fifth** case under the 2026-11-15 revival mandate (reviving previously-parked "weak/Q&A/analysis/doc-search" candidates as legitimate code-grounded Q&A). The y1yqm candidate was parked 2026-11-14 as "weak/code-parse"; revived because it has a real trace, a real file attachment (reconstructed), and a writable check() with ≥8 independent conditions.
- Pattern proven across cases: visible-A = real script the user asked about; hidden-B = hand-authored token-disjoint variant of the same architectural pattern; candidate = generic AST analyzer; check = structure + B-grounding + anti-hardcode + determinism.
