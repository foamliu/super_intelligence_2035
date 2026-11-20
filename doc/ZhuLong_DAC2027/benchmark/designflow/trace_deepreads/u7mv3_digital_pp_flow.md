# Deepread: 1793760774987_u7mv3 (alan3zh @ hfeg0pkn001, mc324)

**Trace**: cline session (agent=lead), 511 msgs (317 user / 194 assistant), 11/04.
**Tools used**: editor(161) / run_approved_command(56) / read_files(52) / list_allowed_files(20).
**Keywords**: innovus:1191, lvs:694, dbget:651, netlist:539, pdk:533, calibre:498, verilog:299, floorplan:270, synthesis, formality(fm), starrc(pe), primetime(signoff), redhawk(pp), ptpx(pp).

## Project context
`test_chip_v1` = hl22 porting test chip, TOP=`hl22_porting_test_chip_v1`, Au22_1P7M PDK, full digital impl flow:
synth(DC) → fm(Formality) → apr(Innovus) → pe(StarRC) → signoff(PrimeTime STA→SDF) → pp/ptpx(PrimePower) → pp/redhawk(IR drop).
Prior APR correction done; this session continued fm+pe correction, then signoff + pp porting, APR floorplan error fixes, and a DC_RESULT_DIR switcher tool.

## User rounds (real human asks, A-faithful candidates)
- **#3 (idx21)**: ~~"create directory pp/ptpx for power analysis... pp/redhawk for IR drop analysis, create related scripts."~~ **r157 CORRECTION (2026-11-06): false claim.** Re-extracted full trace (174 msgs / 6 top-level keys, 109 user+65 assistant; deepread's "511 msgs" counted content blocks). NO ptpx.tcl/redhawk.tcl/gen_inputs.py creation exists in this trace — the keywords appear only in the idx0 context summary, not as actual assistant deliverables. Trace content = APR floorplan fix (innovus_fp/pr.tcl) + CDL conversion (v2lvs, cdl/Makefile + check_cdl.py). **ptpx/redhawk L2 case plan ABANDONED.**
- **#7 (idx117)**: update test_chip_power.md with key file dirs. (L1)
- **#8 (idx137)**: **DC_RESULT_DIR switcher** — add ../tools/ python file: (1) replace DC_RESULT_DIR in flow Makefiles; (2) reanchor SDF in rtl_power/<TOP>.vf. + top-level Makefile with `scan` (newest synth/results/dc_*) and `replace DC_RESULT_DIR=<dir>` targets. → **A-faithful, fully judgeable (subprocess on fixture). Selected this round.**
- #5/#6/#10/#11/#12: APR floorplan error diagnosis (VDD_PM IMPDB-1216, IMPSR-1253) — user gives root-cause/fix-plan → NOT A-faithful (hints only).

## Gold deliverables (r157 re-extracted 2026-11-06, verified present in trace)
- `cdl/Makefile` (idx124 first-create, 3768B): full v2lvs conversion Makefile. `cdl` target: `USE_CALIBRE_VCO=$(VCO) $(V2LVS) -v $(NETLIST) -o $(CDL_OUT) -s $(PDK_SPI) -log $(LOG) -w $(V2LVS_WARN)`. `check` target: `$(PYTHON3) $(CHECK_PY) --cdl $(CDL_OUT) --netlist $(NETLIST) --log $(LOG) --spi $(PDK_SPI) --top $(TOP)`. Vars: TOP/DC_RESULT_DIR/NETLIST/PDK_SPI/VCO/V2LVS/V2LVS_WARN/WORK_DIR/CDL_OUT/LOG/CHECK_PY/PYTHON3. (idx157 later added `cdl-virt` -i -lsp variant for idx152 "No module declaration" fix — NOT part of USER#82.)
- `cdl/check_cdl.py` (idx137 first-create, 6944B): validates v2lvs CDL vs Verilog netlist. 8 checks: (1) CDL non-empty + log no ERROR (2) .INCLUDE present + target exists (3) .SUBCKT count == verilog module count (4) top .SUBCKT + ports match (5) leaf masters in PDK spi (6) instance count CDL == verilog (7) per-master counts identical (8) power: VDD=/VSS= named counts match + PMRowBLK_* on VDD_PM. CLI: --cdl --netlist --log --spi --top. **NOTE**: check (8) hardcodes `len(pm)==441` (test_chip_v1 design-specific) — generalized to `== verilog PMRowBLK_* count` for mini-fixture case. Pure Python (regex), no EDA binary needed → judgeable via subprocess locally.
- `tools/set_dc_result_dir.py` + root Makefile: r156 DCDirSwitch-001 (committed).

## Case plan
- **DCDirSwitch-001** (digital, A-faithful, L1-flow-tooling): r156 delivered. USER#8 verbatim.
- **V2lvsCdlCheck-001** (eda_other, A-faithful, L2-static): r157 delivered. USER#82 verbatim "create ./cdl folder, use v2lvs tool, convert netlist to cdl file, write releated scripts to ./cdl/". Gold = cdl/Makefile (idx124) + check_cdl.py (idx137, generalized PMRowBLK count). Assets A = mini netlist.v + pdk.spi + good.cdl + v2lvs.log (candidate tests check_cdl.py). Hidden B = different netlist/spi + good_b.cdl + 3 bad variants (count-mismatch/missing-leaf/wrong-X-form). check.py 14 conds (a-n): static Makefile v2lvs recipe (b-g) + check_cdl.py CLI/compile (h-i) + L2 subprocess good→exit0 (j) + bad variants→non-zero (k-m) + 3-seed random consistency (n). Pure-Python subprocess, no EDA binary.
