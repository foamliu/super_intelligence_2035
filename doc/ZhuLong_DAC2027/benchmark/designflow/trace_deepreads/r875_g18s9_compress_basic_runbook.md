# Deepread r875 — g18s9 (sfeng@hfeg0pkn005, mc225, digital/verification)

## Trace sourcing
- session: `1794808558058_g18s9` (scp'd from 10.129.2.14:/home/sfeng/.cline/data/sessions/1794808558058_g18s9/)
- 185 msgs / 96 user / 89 assistant; model deepseek-v4-flash; status failed (stale_session_reconciler external exit, NOT task failure — agent answered all 11 questions)
- A-pure: keywords verilog:1133 dominant (A-keyword sum 1137 > C-keyword 438); domain = digital/verification (LPDDR6 verilog regression)
- NOT in any skip list: not edc1w, not t0002965, not chuanqiz/rose3wang cluster. FRESH (cross-checked vs all_touched_sids_r875_v2.txt).

## Real task (user questions, verbatim)
- U#0: "analyze .../Regressions/ directory, how do compress_basic.inc and compress_basic.run work?"
- U#42: "如果我想跑compress_basic这个case, 我该如何执行命令，参考bin/vsim脚本，需要加什么样的define？"
- (U#40,58,91,111,121,159,165,179 are follow-up sub-questions — DUT I/O, Load_TestMode timing, bufLx12_H netlist search, task def locations, comp_tdq_delaytrim, CompWrite/Read_TM. Out of scope for this case to keep self-contained.)

## Case scope (chosen)
Deliverable = `compress_basic_runbook.md` answering U#0 + U#42:
1. How compress_basic.inc / compress_basic.run work (structure + vsim build flow)
2. The exact vsim run command + the 5 defines + variant macros (SCSWAP/PRAC/EYECHECK/NOCHIP)

## Ground-truth facts (from trace final answers ans39/ans57, verifiable against assets)
### Q1 (inc/run structure)
- F1: `Regressions/` holds paired `NAME.run` / `NAME.inc` (optional `NAME.def`); `compress_basic` = LPDDR6 compress / 3-key CMD mode regression.
- F2: `compress_basic.run` is the test stimulus; injected into `lpddr6_test.sv` pattern-execution block → NOT a standalone module/initial, just a list of statements.
- F3: `compress_basic.inc` is a compile-time manifest of `` `include `` directives pulling task definitions from `patterns/cmds_testmode/cmds_compress/*.v`.
- F4: vsim build flow: `<name>.run` → `A_Pattern_Sim.v` (runtime stimulus); `<name>.inc` → `Pattern_tasks.v` (compiled task library); both `include`d in `lpddr6_test.sv`.
- F5: `.run` calls scenario tasks: `basic_wrrd()`, `basic_wrrd_bl8()`, `comp_prac()`, `comp_multibnk()`, `comp_errcode()`, `comp_ecctest()`, ... `comp_rlset()`.
- F6: filename↔task-name mismatch example: `comp_ca89.v` defines `task comp_ca78` (called by .run).

### Q2 (run command + defines)
- F7: run command: `cd lp6_final && ./bin/vsim -sr compress_basic -d "LocalPower USESDF NO_RAND_SC SEFF COMP" -q vbatch -l log`
- F8: `COMP` = core compress/3-key mode enable macro; forces `cm1_cl_RdDlyAbus[1]=1` (top.sv:753) + widens DQ compare window `comp_delta` to 700 (timing_load.sv:370).
- F9: `NO_RAND_SC` = disables random BC/SC sub-channel (`$urandom_range`) in lpddr6_test.sv:514 — compress needs deterministic SC.
- F10: `SEFF` = single-channel mode (default when `ifndef DEFF`); `USESDF` = SDF timing back-annotation; `LocalPower` = baseline define from run_all_regression.
- F11: `NOCHIP` must NOT be added — `compress_basic.run` uses `ifndef NOCHIP` to gate `compare_enable("all")`; adding it disables data comparison.
- F12: variant macros in .run: `SCSWAP` (SC0↔SC1 naming swap, or use dedicated `compress_basic_sc1` regression), `PRAC` (only `comp_ap_change()`), `EYECHECK` (eye-check task subset); PRAC & EYECHECK mutually exclusive, neither = full main compress sequence.

## Assets (self-contained, in assets/EDA-Eval-DesignFlow-CompressBasicRunbookQA-001/)
- `compress_basic.run` (verbatim from trace read_files msg#3, 80 lines)
- `compress_basic.inc` (verbatim, 26 include lines)
- `vsim_sim_branch.txt` (bin/vsim simulation branch ~lines 897-991, excerpt)
- `run_tapeout_dft_refs.txt` (historical commented reference commands lines 63-68,147)
- `defines_context.md` (top.sv:745-765 / timing_load.sv:360-378 / lpddr6_test.sv:510-520 excerpts)

## Hidden input B
- `compress_basic_B.run` / `compress_basic_B.inc`: isomorphic renamed variant (rename regression `compress_basic`→`compress_basicB`, swap task call order, rename a define-gated branch). Judge-only anti-leak; SUT never sees B. check.py derives B-only identifiers and asserts SUT report does NOT leak them.

## check.py plan (k_check = k_rationale = 12)
- Parse SUT `compress_basic_runbook.md`.
- 12 assertions (F1..F12 above), each a regex/keyword check on real content.
- B-leak guard: assert no B-only identifiers (`compress_basicB`, renamed tasks) appear.
- §4.9 degenerate: empty / non-markdown / placeholder / copy-of-prompt / ascii-art-only → all FAIL.

## Quality gates
- k_check = k_rationale = 12 ≥ 8 ✓
- hidden input B ✓
- 3 negative samples (truncated, wrong-command, define-omitted) all FAIL ✓
- §4.9 three degenerate submissions all FAIL ✓
- real trace sourcing ✓ ; A档 trace-faithful (assets verbatim from trace tool_results) ✓
