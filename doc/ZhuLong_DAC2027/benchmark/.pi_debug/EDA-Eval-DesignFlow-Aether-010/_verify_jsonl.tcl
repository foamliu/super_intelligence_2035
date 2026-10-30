source ref_impl.tcl
source _jsonl_test.tcl
set r [check layout_pgshort_audit]
puts "RESULT:$r"
if {$r eq "ALL_ASSERTS_PASS"} { puts "DESIGN_FLOW_VERDICT=PASS" } else { puts "DESIGN_FLOW_VERDICT=FAIL" }
