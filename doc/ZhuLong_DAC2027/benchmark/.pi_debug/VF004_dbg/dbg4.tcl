set steps {}
dict set steps rscalc [dict create status "PASS" artifacts [list]]
set val [list /out/rscalc/rscalc.csv 4096 a1b2c3 false]
puts "val=$val"
dict lappend steps rscalc artifacts $val
set val2 [list /out/pe/pe.log 2048 d4e5f6 false]
dict lappend steps rscalc artifacts $val2
set info [dict get $steps rscalc]
set arts [dict get $info artifacts]
puts "arts=$arts"
puts "llength arts=[llength $arts]"
foreach a $arts {
    puts "  a=$a llength=[llength $a]"
}
