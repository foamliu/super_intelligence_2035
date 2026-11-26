# Combined: source ref_impl + checker, run check on layout_pgmesh_audit
source ref_impl.tcl
source checker.tcl
set r [check layout_pgmesh_audit]
puts "RESULT:$r"
if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
