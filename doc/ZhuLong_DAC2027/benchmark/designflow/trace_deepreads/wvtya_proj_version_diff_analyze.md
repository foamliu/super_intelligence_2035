# wvtya — version-diff analysis-Q&A (ProjVersionDiffAnalyze-001)

**trace**: e0039602 @ hfeg0pkn005, session `1794206891160_wvtya.messages.json`
(195 KB, 27 msgs, 1 user turn). domain = digital.

## USER intent (verbatim)
> `verilog_lib_trans_v2.2copy/ verilog_lib_trans_v2.3/ verilog_lib_trans_v2.3.1/出去日志输入输出相关的文件，你看看这三个版本的项目有什么不同`

User wants a **structured comparison of 3 project versions**, **excluding**
log/input/output run-artifact dirs, reporting what code differs.

## trace agent behavior
- 1 user turn, 13 assistant tool calls: `list_allowed_files` (7×) + `editor` (4×) + `run_approved_command` (3×).
- Wrote 3 helper scripts in `v2.3/`: `compare_versions.py` (recursive md5 diff),
  `gen_diff.py` (unified diff of changed files), `gen_diff_io.py` (diff of excluded dirs).
- Final report: claimed **v2.3 ≡ v2.3.1** (byte-identical source) and **v2.2→v2.3 only 3 changed files**
  (extract_converted_sv.py TIMEOUT-skip, simlib_drcoa_stdcells.sv +725 lines, parallel_worker.py +1 line).

## TRUE diff (independently re-derived with md5 manifests)

### v23 vs v231 (excluding log/inputs/outputs)
| file | v23 | v231 |
|------|-----|------|
| src/family_names.txt | present | MISSING |
| outputs/gen.sv | present | MISSING (excluded) |

=> v23 and v231 differ ONLY in `src/family_names.txt` (present in v23, missing in v231).
   **Agent was WRONG** to claim "byte-identical source" — family_names.txt is a code difference.

### v22 → v23 (excluding log/inputs/outputs)
| file | change |
|------|--------|
| extract_converted_sv.py | modified (TIMEOUT-skip handling: returns (dict, timeout_skipped_list), skips [TIMEOUT] placeholder modules) |
| simlib_drcoa_stdcells.sv | modified (appended celldefine block with new cells C_latsq2_ParityOpLat/C_dfrbp_ParityOpLat/C_mux4_ParityOpLat + $width/$hold/$setup timing, +842 lines) |
| src/parallel_worker.py | modified (+1 anti-hallucination prompt line: 幻觉/CLBK) |
| src/family_names.txt | added (NEW file listing cell families) |

Unchanged (8 files): config.yaml, run.py, simlib_base.sv, src/netlist_parser.py,
src/rules_prompt.py, src/simlib_ref_db.py, docs/README.md, test/test_basic.py.

**Agent was WRONG**: it missed `src/family_names.txt` (new file) and claimed only 3 changed files.
(Also: real trace had more changed files — rules_prompt.py, rules_prompt02.py, simlib_ref_db.py —
which the mini A trees deliberately keep unchanged to produce a clean, verifiable 4-file diff.)

## A档 feasibility
A-faithful NOT feasible: real `simlib_drcoa_stdcells.sv` is 2.4 MB / 80 K lines (too large to ship
in a benchmark asset); real trace contains agent-created temp scripts (compare_versions.py,
gen_diff.py, gen_diff_io.py, tb_or4.sv) that contaminate the diff. → B档 mini trees
(vlib_trans_v22/v23/v231, ~14 files each) that faithfully mirror the real structure with clean,
verifiable differences.

## B (hidden) design
Project "svgen" v30/v31/v32 (≥8 dimensions different from A):
- project name: svgen vs vlib_trans
- version names: v30/v31/v32 vs v22/v23/v231
- changed files: convert_sv.py/simlib_cells.sv/src/cell_groups.txt vs extract_converted_sv.py/simlib_drcoa_stdcells.sv/src/family_names.txt
- change types: validation (validate_sv_syntax) vs TIMEOUT-skip
- v31-v32 pattern: modified llm_worker.py (retry-on-empty) vs v23-v231 presence family_names.txt
- #changed v30→v31: 3 vs v22→v23: 4
- excluded dirs: logs/input/output/cache vs log/inputs/outputs
- unchanged set: different file names

## Case design
- **C-A analysis-Q&A / version-diff template** (cf. SocProjStructAnalyze-001-v2).
- Deliverable: `version_diff_analysis_report.json` containing:
  - `analyze_version_diff_fn`: GENERAL Python function `fn(v22_root, v23_root, v231_root, exclude_dirs=None)` that diffs any 3 trees (not hardcoded to A).
  - `analysis`: static structured analysis of the visible A trees.
  - `evidence`: verbatim tokens from real A files (proves the SUT read A).
  - `reasoning`, `summary`.
- check.py: **fully self-contained** (A file contents + B trees base64-inlined; no disk reads of
  assets/ at judge time — judge scratch dir flattens A files by basename).
- 18 independent conditions (a-r): structure + fn-execs + fn-on-B correctness (v31-v32, v30-v31,
  exclusion) + static A analysis correctness (v23-v231, v22-v23, unchanged, exclusion, change
  descriptions for TIMEOUT/celldefine/幻觉) + evidence-verification + B judge-self-check (≥6 dims
  anti-hardcode) + 3-seed determinism + summary/reasoning.
- **Anti-memorization**: check judges the CORRECT diff (independently re-derived), so a SUT that
  merely echoes the trace agent's inaccurate report (v23≡v231, 3 files) FAILS — see neg_wrong.
- k_check = k_rationale = 18.
- Self-verified: ref PASS + 3 negatives (naive/stub/wrong) + 3 §4.9 fakes (empty/print-expected/
  core-deleted) all FAIL + e2e jsonl flat-dir judge PASS.
