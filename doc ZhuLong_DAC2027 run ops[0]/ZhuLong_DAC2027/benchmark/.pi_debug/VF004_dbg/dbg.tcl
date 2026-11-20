source /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/Virtuoso-Flow-004/ref.tcl
set cA {[declared_outputs]
rscalc = /out/rscalc/
pe = /out/pe/
autovia = /out/autovia/
[step:rscalc]
status = PASS
artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false
[step:pe]
status = PASS
artifact = /out/pe/pe.log|2048|d4e5f6|false
[step:autovia]
status = PASS
artifact = /out/autovia/autovia.gds|8192|9a8b7c|true
}
set d [vflow_manifest_audit $cA]
puts "name_collisions: [dict get $d name_collisions]"
puts "total: [dict get $d total_steps]"
