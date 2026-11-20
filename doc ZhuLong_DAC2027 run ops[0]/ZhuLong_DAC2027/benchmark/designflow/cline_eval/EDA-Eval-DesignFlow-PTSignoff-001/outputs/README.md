# PrimeTime Post-Route STA Signoff Flow (`addr_to_rowcol_v7`)

Reusable PrimeTime (U-2022.12-SP5) static timing signoff flow for the small
combinational DRAM module `addr_to_rowcol_v7` (cxmtG5_CIP, 107 instances /
116 nets), routed in Innovus 23.32 and characterized with StarRC W-2024.09 SPEF.

## Files

| File | Purpose |
|------|---------|
| `tcl/pt_sta.tcl` | Parameterized PrimeTime STA main script |
| `setup/common_setup.tcl` | Design / path / library variables (edit only this to re-run on another design/corner) |
| `run_pt.csh` | C-shell launcher (license + clean `LD_PRELOAD` + `pt_shell`) |
| `README.md` | This document |

## Flow

`run_pt.csh` → `pt_shell -file tcl/pt_sta.tcl` →

1. `read_db $DB` (precompiled `.db`, library `SS_0p98_m40c`)
2. `set_app_var link_path $LIB_NAME` (library name, **not** `"*"`)
3. `read_verilog $NETLIST` (no-PG post-route netlist `postroute.v`)
4. `current_design $DESIGN`
5. `link_design`
6. `read_sdc $SDC` (`set_max_delay 0.5 ns` in→out)
7. `read_parasitics -format spef $SPEF` (StarRC `routed.spef`)
8. `report_annotated_parasitics`
9. `report_global_timing` → `data/pt_global.rpt`
10. `report_timing -max_paths 5 -input_pins -path_type full` → `data/pt_timing.rpt`
11. `report_timing -max_paths 1 -path_type full_clock_expanded -nets` → `data/pt_crit_path.rpt`
12. `report_design` → `data/pt_design.rpt`
13. `report_constraint -all_violators -max_delay` → `data/pt_viol.rpt`

## Environment notes

- Library loaded with `read_db` (this PT has no `read_liberty`).
- `link_path` must be the library name `SS_0p98_m40c`; `link_path "*"` fails
  with LNK-049 / LNK-005.
- Launcher strips `LD_PRELOAD` (`env -u LD_PRELOAD`) before `pt_shell`.
- License: `SNPSLMD_LICENSE_FILE` / `LM_LICENSE_FILE` = `27000@hfds4:12000@hfds4`.

## Known issue: extraction / timing-library corner mismatch

The parasitics were extracted with an nxtgrd file at a **TYP 98 C** corner
(`G5CIP_TYP.nxtgrd`, `GLOBAL_TEMPERATURE 98`), whereas the timing Liberty
library `SS_0p98_m40c` is a **slow-slow -40 C** corner. These two corners are
inconsistent, so the numbers in the generated reports should be treated as a
sanity/demo run rather than a physically matched signoff. For a correct signoff
either extract parasitics with a -40 C (SS) nxtgrd, or use a 98 C (TT) timing
library that matches the extraction corner.

## Re-run on another design / corner

Edit `setup/common_setup.tcl` only:

```tcl
set DESIGN   <top_module>
set LIB_NAME <lib_cell_name>
set NETLIST  <path>/postroute.v
set SPEF     <path>/routed.spef
set SDC      <path>/mapped.sdc
set DB       <path>/<corner>.db
set OUT_DIR  <report_dir>
```

Then invoke `./run_pt.csh` (or `pt_shell -file tcl/pt_sta.tcl`).