###############################################################################
# pt_sta.tcl
# PrimeTime (U-2022.12-SP5) post-route static timing signoff flow.
#
# Design / path variables ($DESIGN/$NETLIST/$SPEF/$SDC/$DB/$LIB_NAME/$OUT_DIR)
# are sourced from setup/common_setup.tcl, so this script is fully
# parameterized and can be re-run on a different design / corner by editing
# only setup/common_setup.tcl.
###############################################################################

source setup/common_setup.tcl

# 1. Load the precompiled timing library (.db).
#    Use read_db, NOT read_liberty (read_liberty is unavailable in this PT).
read_db $DB

# 2. link_path must be the library name (SS_0p98_m40c).
#    Do NOT use "*": link_path "*" + read_db fails here (LNK-049 / LNK-005).
set_app_var link_path $LIB_NAME

# 3. Read the post-route netlist (no-PG version; the PG version fails LNK-042).
read_verilog $NETLIST

# 4. Set the top-level design.
current_design $DESIGN

# 5. Link the design against the loaded library.
link_design

# 6. Read the timing constraints.
read_sdc $SDC

# 7. Back-annotate StarRC-extracted parasitics (IEEE 1481-1999 SPEF).
read_parasitics -format spef $SPEF

# 8. Report parasitic annotation coverage.
report_annotated_parasitics

# 9. Global timing summary (setup/hold WNS/TNS/NUM).
report_global_timing > $OUT_DIR/pt_global.rpt

# 10. Worst paths (>=5), full cell/net delay breakdown.
report_timing -max_paths 5 -input_pins -path_type full > $OUT_DIR/pt_timing.rpt

# 11. Single worst critical path, fully expanded with nets.
report_timing -max_paths 1 -path_type full_clock_expanded -nets > $OUT_DIR/pt_crit_path.rpt

# 12. Design summary (design / corner / constraint attributes).
report_design > $OUT_DIR/pt_design.rpt

# 13. All max-delay constraint violators with slack.
report_constraint -all_violators -max_delay > $OUT_DIR/pt_viol.rpt

exit