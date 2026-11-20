# verify 3 new innovus cases (Digital-005/006/007) end-to-end in the sandbox.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}

# --- shared setup ---
if {![info exists ::INN_EVAL_SAMPLE_LEF_LOADED]} {
    set _src /apps/cdsmgr/CRB/INNOVUS2231/share/plato/tutorial/sample.lef
    set _fh [open $_src r]; set _d [read $_fh]; close $_fh
    regsub {VERSION 0\.0 ;} $_d {VERSION 5.6 ;} _d
    set _fo [open /tmp/inn_eval_sample.lef w]; puts -nonewline $_fo $_d; close $_fo
    if {[catch {loadLefFile /tmp/inn_eval_sample.lef} _lefmsg]} {
        puts "setup note: loadLefFile error (assuming already loaded): $_lefmsg"
    }
    set ::INN_EVAL_SAMPLE_LEF_LOADED 1
}
if {[dbGet top.name] ne "C1"} {
    loadDefFile /apps/cdsmgr/CRB/INNOVUS2231/share/plato/tutorial/sample.def
}

# --- reference impls (inlined) ---
proc inn_count_nets {} { return [llength [dbGet top.nets.name]] }
proc inn_count_top_terminals {} { return [llength [dbGet top.terms.name]] }
proc inn_count_insts_of_master {master} {
    set r [dbGet top.insts.cell.name $master]
    if {$r eq "0x0"} { return 0 }
    return [llength $r]
}

# --- Digital-005 checks ---
set n5 [inn_count_nets]
assert {[string is integer -strict $n5]} "005: result must be integer, got: $n5"
assert {$n5 == 1917} "005: net count mismatch, got: $n5 (expected 1917)"
assert {$n5 > 0} "005: non-empty design must have >0 nets"
puts "005 OK nets=$n5"

# --- Digital-006 checks ---
set n6 [inn_count_top_terminals]
assert {[string is integer -strict $n6]} "006: result must be integer, got: $n6"
assert {$n6 == 114} "006: top terminal count mismatch, got: $n6 (expected 114)"
assert {$n6 > 0} "006: design must have >0 top terminals"
# independent re-count via distinct
set indep6 [llength [lsort -unique [dbGet top.terms.name]]]
assert {$n6 == $indep6} "006: result ($n6) must equal distinct re-count ($indep6)"
puts "006 OK terms=$n6"

# --- Digital-007 checks ---
set c42 [inn_count_insts_of_master C42]
assert {[string is integer -strict $c42]} "007: C42 result must be integer, got: $c42"
assert {$c42 == 349} "007: C42 instance count mismatch, got: $c42 (expected 349)"
set nosuch [inn_count_insts_of_master NO_SUCH_MASTER_XYZ]
assert {$nosuch == 0} "007: missing master must return 0, got: $nosuch"
# independent iterate for C42
set indep7 0
foreach nm [dbGet top.insts.cell.name] { if {$nm eq "C42"} { incr indep7 } }
assert {$c42 == $indep7} "007: C42 result ($c42) must equal independent iterate ($indep7)"
puts "007 OK C42=$c42 nosuch=$nosuch"

puts "ALL_005_006_007_PASS"
