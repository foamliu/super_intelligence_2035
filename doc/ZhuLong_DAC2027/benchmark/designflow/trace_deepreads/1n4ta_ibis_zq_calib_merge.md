# Deepread: 1795005201890_1n4ta — IBIS ZQ calibration skill merge (hspice end-to-end)

- **session**: 1795005201890_1n4ta
- **user**: alan17z @ hfeg0plg10 (10.129.35.10; file accessible locally on .75)
- **match_count**: 243 (keywords: hspice:838; netlist:474; waveview:36; synopsys:36; aether:14; schematic:4; pyaether:4)
- **domain**: characterization (IBIS I/O buffer model extraction = ZQ calibration)
- **scan**: 1118_230537 (FRESH, not in 1115; first deepread r847 2026-11-19)
- **size**: 1.3MB, 389 msgs, 41 tool_use (first 40 shown)

## User intent (real task)

User has 3 separate cline skills for IBIS model extraction:
1. `ibis-t2b-gen` — generate t2b (touchstone-to-IBIS) files
2. `ibis-zq-calib` — ZQ calibration merge logic (`merge_zq.py`)
3. `ibis-zq-sim-gen` — generate ZQ calibration hspice decks (`gen_zq_decks.py`)

**User's request (msg #4, verbatim)**:
> 现在我希望你把这个skill合并成1个，因为现在ai已经布置在可以仿真的服务器了，不需要我把数据拷贝出来，你应该可以直接调用hspice等仿真软件运行，所以我想把这三个skill合并成一个

= merge the 3 skills into 1 unified `ibis-extract` skill that calls hspice directly on the server (end-to-end: generate decks → run hspice → merge ZQ results), instead of the old workflow where user had to manually export data.

## What the agent did (tool chain)

1. Read the 3 existing SKILL.md + scripts (gen_zq_decks.py, merge_zq.py, gen_top.py)
2. Asked user how hspice/t2b are invoked on server (ask_question)
3. Created `ibis-extract` merged skill: copied 5 scripts, wrote `run_sims.py` (wraps hspice subprocess)
4. Built test fixtures: `corner.txt` (`.temp 50` + `.lib` tt/ff/ss corners), `stimulus.txt` (VPUPMOSENN/PuPmosEnN etc. ZQ pad stimulus)
5. Ran `gen_zq_decks.py --corner corner.txt --stimulus stimulus.txt` → generated tt.sp/ff.sp/ss.sp
6. Ran `check_decks.py` to validate deck structure
7. Ran `run_sims.py --dry-run` (no real hspice license in test)
8. Built `gen_all6.py` to synthesize hspice `$DATA1` results (6 PU+PD pairs) for testing merge WITHOUT real hspice
9. Ran `merge_zq.py --gen-corners` → merged ZQ values across corners
10. Scanned real source tree `/rundata/SIPI/alanzhang/SI/1_IBIS_extract/AI_try/source/`:
    - `finesim.TT1.0V25c.for_netlist_IBIS_IBIS_model/stimulus` + `model.sp` + `incFile_lp`
    - `netlist_IBIS/netlistHeader` + `netlistFooter`
11. Refined `gen_zq_decks.py` gen_sweep_deck (PU pullup / PD pulldown sweep)

## Key source files (on .75, real user data)

- `/home/alan17z/_ibis_test/corner.txt` — corner config (.temp, .lib tt/ff/ss, incFile_lp bjt/res/nicap/pmos)
- `/home/alan17z/_ibis_test/stimulus.txt` — ZQ pad stimulus (VPUPMOSENN, VPUNMOSENN, VPDPMOSENN, VPDNMOSENN, VSWEN, pvwlp)
- `/rundata/SIPI/alanzhang/SI/1_IBIS_extract/AI_try/source/netlist_IBIS/netlistHeader` + `netlistFooter`
- `/rundata/SIPI/alanzhang/SI/1_IBIS_extract/AI_try/source/finesim.TT1.0V25c.for_netlist_IBIS_IBIS_model/model.sp` + `incFile_lp`
- Scripts: `gen_zq_decks.py` (gen PU/PD sweep decks), `run_sims.py` (hspice wrapper), `merge_zq.py` (merge ZQ results), `check_decks.py` (deck validation)

## Case design idea (for next round)

**Domain**: characterization (IBIS ZQ calibration)
**Layer**: L1 (offline Python: generate decks + merge synthetic hspice output; no real hspice needed — trace itself uses --dry-run + synthetic $DATA1)
**Task**: Given corner.txt + stimulus.txt + netlistHeader/Footer + model.sp, write a script that (a) generates ZQ PU/PD sweep hspice decks for tt/ff/ss corners, (b) merges synthetic hspice $DATA1 results into ZQ resistance values per corner.
**Deliverable**: submit.zip with gen_zq_decks.py + merge_zq.py + generated tt.sp/ff.sp/ss.sp
**Hidden B**: different corner set (e.g. tt/ff only, different .temp), different stimulus pad names, different netlist → structurally different decks + ZQ values
**check() assertions (≥8)**:
① zip contains gen_zq_decks.py + merge_zq.py + ≥3 deck files (tt/ff/ss)
② deck has correct .include order (netlistHeader → model → stimulus → netlistFooter)
③ deck has PU sweep (VPU sweep voltage 0→vcc, .dc param) and PD sweep
④ deck references correct corner (.lib tt/ff/ss)
⑤ deck has ZQ pad stimulus nodes (PuPmosEnN etc.)
⑥ merge_zq.py reads $DATA1 format and outputs ZQ Rpu/Rpd per corner
⑦ merge output has tt/ff/ss corner keys with numeric Rpu/Rpd
⑧ cross-input guard: B's decks use B's pad names (not A's), B's ZQ values differ from A's
⑨ §4.9: empty/printf/core-deleted all FAIL
**Negative samples**: naive (hardcode A's deck text), stub (always output Rpu=48 Rpd=48), core-deleted (merge_zq returns empty)

## Status
- DEBT: 1 deepread not yet synthesized (r847 time budget consumed by 1118 scan discovery)
- Next round: extract source files from .75, build A/B assets, write check.py, self-verify, append jsonl
