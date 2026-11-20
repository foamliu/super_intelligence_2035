source /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/Virtuoso-Flow-004/ref.tcl
# Instrument: re-define with debug by patching - instead just test parsing of one artifact line
set line {artifact = /out/rscalc/rscalc.csv|4096|a1b2c3|false}
regexp {^([^=]+?)=(.*)$} $line -> rawk rawv
set k [string trim $rawk]
set v [string trim $rawv]
puts "k=($k) v=($v)"
set parts [split $v "|"]
puts "parts len=[llength $parts]: $parts"
lassign $parts path size checksum signoff
puts "path=($path) size=($size) checksum=($checksum) signoff=($signoff)"
set lastslash [string last "/" $path]
puts "lastslash=$lastslash"
if {$lastslash >= 0} {
    set base [string range $path [expr {$lastslash + 1}] end]
} else {
    set base $path
}
puts "base=($base)"
