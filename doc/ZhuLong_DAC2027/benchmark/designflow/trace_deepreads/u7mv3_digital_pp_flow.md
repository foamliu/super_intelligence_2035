# Deepread: 1793760774987_u7mv3 (alan3zh @ hfeg0pkn001, mc324)

**Trace**: cline session (agent=lead), 511 msgs (317 user / 194 assistant), 11/04.
**Tools used**: editor(161) / run_approved_command(56) / read_files(52) / list_allowed_files(20).
**Keywords**: innovus:1191, lvs:694, dbget:651, netlist:539, pdk:533, calibre:498, verilog:299, floorplan:270, synthesis, formality(fm), starrc(pe), primetime(signoff), redhawk(pp), ptpx(pp).

## Project context
`test_chip_v1` = hl22 porting test chip, TOP=`hl22_porting_test_chip_v1`, Au22_1P7M PDK, full digital impl flow:
synth(DC) → fm(Formality) → apr(Innovus) → pe(StarRC) → signoff(PrimeTime STA→SDF) → pp/ptpx(PrimePower) → pp/redhawk(IR drop).
Prior APR correction done; this session continued fm+pe correction, then signoff + pp porting, APR floorplan error fixes, and a DC_RESULT_DIR switcher tool.

## User rounds (real human asks, A-faithful candidates)
- **#3 (idx21)**: "create directory pp/ptpx for power analysis... pp/redhawk for IR drop analysis, create related scripts." → L2 (PTPX/Redhawk Tcl+gen_inputs.py+Makefiles). Gold extracted: ptpx.tcl, redhawk.tcl, gen_inputs.py (runnable on DEF), Makefiles. **Reserved for next-round L2 case.**
- **#7 (idx117)**: update test_chip_power.md with key file dirs. (L1)
- **#8 (idx137)**: **DC_RESULT_DIR switcher** — add ../tools/ python file: (1) replace DC_RESULT_DIR in flow Makefiles; (2) reanchor SDF in rtl_power/<TOP>.vf. + top-level Makefile with `scan` (newest synth/results/dc_*) and `replace DC_RESULT_DIR=<dir>` targets. → **A-faithful, fully judgeable (subprocess on fixture). Selected this round.**
- #5/#6/#10/#11/#12: APR floorplan error diagnosis (VDD_PM IMPDB-1216, IMPSR-1253) — user gives root-cause/fix-plan → NOT A-faithful (hints only).

## Gold deliverables (extracted to .75 workdir gold/)
- `tools/set_dc_result_dir.py` (7064B): argparse CLI (positional dc_result_dir, --project, --dry-run, --backup); replaces DC_RESULT_DIR/POWER_RES_DIR lines (MK_LINE_RE, dc_ token) in */Makefile + pp/*/Makefile; replaces fm/fm.tcl `set dflt [file join $PRJ_ROOT synth results dc_...]`; repoints rtl_power/*.vf `$sdf_annotate("...")` path. DEFAULT_DC_RESULT_DIR fallback. Project root via --project / PROJECT_ROOT / ../test_chip_v1.
- `test_chip_v1/Makefile` (1972B): `scan` (NEWEST_DC = newest dc_* by mtime via ls -1dt) → calls script; `replace DC_RESULT_DIR=<dir>` → calls script; EXTRA=--dry-run/--backup passthrough.

## Case plan
- **DCDirSwitch-001** (digital, A-faithful, L1-flow-tooling): USER#8 verbatim. Assets = mini project skeleton (flow Makefiles + fm.tcl + rtl_power/<TOP>.vf + synth/results/dc_OLD + dc_NEW). Hidden B = different TOP/dirs/dummy Makefile. check.py 15 conds (a-o): zip/py_compile/CLI/--project/Makefile-replace/fm.tcl/.vf-sdf/dummy-untouched/idempotency/scan/replace/dry-run/error-exit/randomized-anti-hardcode. §4.2 subprocess ✓, §4.5 3-seed ✓, §4.9 3 negatives ✓.
- **§5 note**: L1 (no EDA tool exec); A档 pilot "本轮不设目标、只报数" permits. Next round: build L2 PTPX/Redhawk case from same trace (gold already extracted).
