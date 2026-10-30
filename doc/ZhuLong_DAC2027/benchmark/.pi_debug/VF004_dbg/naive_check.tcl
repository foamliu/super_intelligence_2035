source /nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/.pi_debug/VF004_dbg/naive.tcl
proc assert {cond msg} { set ok [uplevel 1 [list expr $cond]]; if {!$ok} { error "ASSERT FAIL: $cond -- $msg" } }
proc dget {d k} { return [dict get $d $k] }
proc llist {d k} { return [dict get $d $k] }
# Case D: per-step dup should NOT be collision; naive flags pe.log
set cD {[declared_outputs]
rscalc = /out/rscalc/
pe = /out/pe/
autovia = /out/autovia/
[step:rscalc]
status = PASS
artifact = /out/rscalc/result.gds|100|aa|false
[step:pe]
status = PASS
artifact = /out/pe/pe.log|10|bb|false
artifact = /out/pe/pe.log|10|bb|false
[step:autovia]
status = PASS
artifact = /out/autovia/result.gds|200|cc|true
}
set dD [vflow_manifest_audit $cD]
puts "naive D name_collisions: [dict get $dD name_collisions]"
catch { assert {[llist $dD name_collisions] eq {result.gds}} "D" } err
puts "naive D expected {result.gds}, got {[llist $dD name_collisions]} -> TEETH: $err"
# Case E: last-wins -> first-block artifact discarded; naive merges -> ghost
set cE {[declared_outputs]
rscalc = /out/rscalc/
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
[step:rscalc]
status = FAIL
}
set dE [vflow_manifest_audit $cE]
puts "naive E ghost_artifacts: [dict get $dE ghost_artifacts]"
catch { assert {[llength [llist $dE ghost_artifacts]]==0} "E" } err2
puts "naive E expected no ghost, got {[llist $dE ghost_artifacts]} -> TEETH: $err2"
# Case F1: ghost alone -> dirty; naive verdict=clean (only missing gates)
set cF1 {[declared_outputs]
rscalc = /out/rscalc/
[step:rscalc]
status = FAIL
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
}
set dF1 [vflow_manifest_audit $cF1]
puts "naive F1 verdict: [dict get $dF1 verdict]"
catch { assert {[string equal [dget $dF1 verdict] "dirty"]} "F1" } err3
puts "naive F1 expected dirty, got {[dget $dF1 verdict]} -> TEETH: $err3"
