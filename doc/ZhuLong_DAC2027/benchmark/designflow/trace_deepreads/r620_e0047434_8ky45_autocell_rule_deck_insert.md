# Deepread: e0047434 / 1792742027783_8ky45 — AutoCell Rule Deck Insert

**Session**: `1792742027783_8ky45.messages.json`
**User**: e0047434
**Host**: hfeg0pnd001 (10.129.32.189)
**MC**: 242 (drc:635;lvs:694;calibre:330;.cdl:176;.gds:169;schematic:435;netlist:428)
**Domain**: physical_verify
**Date**: 2026-10-23
**Size**: 1.4MB, 200 msgs, ~30 user_text messages
**Round**: r620

## User Intent

e0047434 is a standard cell engineer using **AutoCell** (Primarius Technologies
standard cell compiler v1.26.9) to automatically generate cell layouts. The
session covers:

1. **Q&A about AutoCell** (USER#31-54): reading docs, understanding kit TCL files,
   understanding the mismatch between `sch.cdl` and `placement.json` / `R.tcl`.
2. **Kit TCL annotation** (USER#72): generate `R_H204_000_explain.tcl` with
   per-line comments — a produce-task but annotation-only.
3. **Design rule Q&A** (USER#79-89): how AutoCell describes design rules
   (min space, double pattern, PRL), who provides tech.tcl/p51h204l6.tcl/options.tcl.
4. **LVS/DRC rule deck configuration** (USER#90-107): THE CORE PRODUCE-TASK.
   - User asks about PDK rule deck paths (`tv1_fs` vs `tv1_dbc`, front/back-side
     power).
   - Can't input `.rule` files in AutoCell GUI (extension filter expects `.drc`/`.lvs`).
   - Agent diagnoses: GUI extension filter, proposes Solution A (copy+rename) or
     Solution B (TCL `set_external_engine`).
   - **USER#107**: "我选方案B...生成一个 R_H204_000_rule.tcl 文件，在这里面加上
     rule相关的配置" — generate a new kit variant with engine config.
   - **USER#111-113**: "R_H204_000_rule.tcl 文件里不要写注释，请重新生成" —
     regenerate without comments.

## Key Produce-Task (USER#107)

**Input**: `R_H204_000.tcl` (original kit TCL) + rule deck paths
**Output**: `R_H204_000_rule.tcl` (new kit variant)

**Transformation**:
1. Remove all comment lines (lines starting with `#`)
2. Insert `tech default_tech set_external_engine` block after last `source` line,
   before `option` section:
   ```tcl
   tech default_tech set_external_engine \
       -bin calibre \
       -drc_deck /apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_DRC_FS.rule \
       -lvs_deck /apps/imctf/cad/runset/lacaa/tv1_fs/current/calibre_LVS_FS.rule \
       -timeout 600
   ```
3. Preserve all original code lines unchanged in order
4. Tech name (`default_tech`) extracted from `cell ${cell_name} -tech default_tech ...`

## Original Files (from .75 via SSH to 10.129.32.189)

### R_H204_000.tcl (original, 25 lines)
```tcl
# AutoCell Layout Generator TCL, Version 1.26.7.56db6cb
source ${tcl_script_dir}/../params.tcl
set layout_spec "p51h204l6"
source ${tcl_script_dir}/../layout_spec/${layout_spec}.tcl
source ${tcl_script_dir}/../prepr.tcl
option router 1
option router_method 2
option router_solver_optimize_mode 0
option lvs_check 1
option lvs_dont_compare_bulk 1
set_constraint PVS 0
set_constraint PVBS 0
set_constraint FPVB 0
set_constraint TTS 1
set_constraint VVA 1
schematic ${cell_name} -pmos_classes p51h204l6:${pmos_type} -nmos_classes p51h204l6:${nmos_type} -spice_path ${netlist_path}
cell ${cell_name} -tech default_tech -schematic ${cell_name} -boundary p51h204l6:boundary_template -dummy p51h204l6:dummy_template
cell ${cell_name} set_placer -templates { p51h204l6:match_template p51h204l6:nmos p51h204l6:pmos p51h204l6:unmatch }
cell ${cell_name} set_router -grid_map [ dict create GT poly M0 m0 M1 m1 M2 m2] -vss_connector p51h204l6:vss -vdd_connector p51h204l6:vdd -pin_template p51h204l6:pin
cell ${cell_name} read_placement -file ${tcl_script_dir}/../../${cell_name}/layout/placement.json -file_type json -ignore_missing_device
cell ${cell_name} generate_layout
write_layout -cells [ list ${cell_name} ] -type gds -file ${gds_path}
```

### R_H204_000_rule.tcl (generated, no comments + engine config)
- Comment removed
- `tech default_tech set_external_engine` block inserted after `source prepr.tcl`
- All original code lines preserved

## Case Synthesis: AutoCellRuleDeckInsert-001

**B档 mock-behavioral reframe**: AutoCell tool not in sandbox → reframe as pure
Python text-transformation script.

- **Input A**: `kit_a.tcl` (based on R_H204_000.tcl) + `config_a.json` (calibre/tv1_fs)
- **Hidden B**: `kit_b.tcl` (tech=dbc_tech_88, 3 source lines, mb2sdfsnqd1 cell) +
  `config_b.json` (qv engine, tv1_dbc decks, timeout=900)
- **Hidden B2**: `kit_b2.tcl` (tech=advanced_tech_v2, 2 source lines, minimal) +
  `config_b2.json` (calibre, g5_cip decks, timeout=300) — anti-hardcode

**14 assertions a-n**: structure(2) + no-comments(1) + line-preservation(1) +
engine-block(1) + tech-name(1) + drc-deck(1) + lvs-deck(1) + engine-bin(1) +
timeout(1) + insertion-position(1) + no-duplicates(1) + deterministic(1) +
B2-anti-hardcode(1)

Self-verify: ref 14/14 PASS ✓; 3 neg (naive_empty/print_expected/deleted_core)
all FAIL ✓; NEGATIVE_SELFTEST ALL-FAIL-OK ✓; §4.9 three-fake ALL-FAIL ✓;
embedded test==disk roundtrip ✓; bool(check)=True ✓; k=14≥8 ✓.

C.jsonl 384→385; mark case ✓ (pv 166→167, ledger_C case 385→386).
