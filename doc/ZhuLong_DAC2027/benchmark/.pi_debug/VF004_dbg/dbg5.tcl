# Test plain lappend vs dict lappend
set L [list]
set val [list a b c]
lappend L $val
puts "lappend single arg: L=$L llength=[llength $L]"
set L2 [list]
dict set D k [list]
dict lappend D k $val
puts "dict lappend: D(k)=[dict get $D k] llength=[llength [dict get $D k]]"
# nested
set D2 {}
dict set D2 s [dict create arts [list]]
dict lappend D2 s arts $val
puts "dict lappend nested: arts=[dict get $D2 s arts] llength=[llength [dict get $D2 s arts]]"
