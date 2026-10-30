puts "START"
source ./_combined_ref.tcl
puts "SOURCED"
set r [check layout_via_enclosure_audit]
puts "RESULT:$r"
