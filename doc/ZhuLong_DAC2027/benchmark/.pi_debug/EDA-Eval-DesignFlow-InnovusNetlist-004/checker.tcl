# assert shim: the runtime Tcl has no native 'assert' command.
proc assert {cond msg} {
    set ok [uplevel 1 [list expr $cond]]
    if {!$ok} { error "ASSERT FAIL: $cond -- $msg" }
}
# helper: compare a dict-list value to an expected sorted list (via join).
proc lcmp {actual expected} {
    set a [join [lsort $actual] ","]
    set e [join [lsort $expected] ","]
    return [expr {$a eq $e}]
}

proc check {candidate} {
    # ---- Case A: baseline -- connected / single-pin / unconnected / power-by-pattern ----
    set nA "- n1
  ( I1 A )
  ( I2 B )
  ;
- n2
  ( I1 Z )
  ;
- n3
  ;
- VDD
  ( I1 VDD )
  ;"
    set sA ""
    set d [$candidate $nA $sA]
    assert {[dict get $d total_nets] == 4} "A total_nets=4"
    assert {[lcmp [dict get $d power_nets] {VDD}]} "A power_nets={VDD}"
    assert {[dict get $d signal_nets_count] == 3} "A signal_nets_count=3"
    assert {[dict get $d connected_count] == 1} "A connected_count=1 (n1)"
    assert {[lcmp [dict get $d single_pin_signal] {n2}]} "A single_pin_signal={n2}"
    assert {[lcmp [dict get $d unconnected_signal] {n3}]} "A unconnected_signal={n3}"
    assert {[dict get $d duplicate_connections] == 0} "A duplicate_connections=0"
    assert {[dict get $d verdict] eq "dangling"} "A verdict=dangling"

    # ---- Case B: USE-POWER trap -- clk_buf USE POWER is power even with non-power name ----
    set nB "- clk_buf USE POWER
  ( I1 A )
  ;
- data_net USE SIGNAL
  ( I1 A )
  ( I2 B )
  ;"
    set sB ""
    set d [$candidate $nB $sB]
    assert {[dict get $d total_nets] == 2} "B total_nets=2"
    assert {[lcmp [dict get $d power_nets] {clk_buf}]} "B power_nets={clk_buf} (USE POWER wins over name)"
    assert {[dict get $d signal_nets_count] == 1} "B signal_nets_count=1"
    assert {[dict get $d connected_count] == 1} "B connected_count=1 (data_net)"
    assert {[lcmp [dict get $d single_pin_signal] {}]} "B single_pin_signal empty (clk_buf is power, not dangling)"
    assert {[dict get $d verdict] eq "clean"} "B verdict=clean"

    # ---- Case C: SPECIALNETS-highest trap -- VDD in NETS with USE SIGNAL, but VDD also
    #      declared in SPECIALNETS -> power (SPECIALNETS wins over USE SIGNAL) ----
    set nC "- VDD USE SIGNAL
  ( I1 A )
  ;
- n_sig
  ( I1 A )
  ( I2 B )
  ;"
    set sC "- VDD
  ( I1 VDD )
  ;"
    set d [$candidate $nC $sC]
    assert {[dict get $d total_nets] == 2} "C total_nets=2"
    assert {[lcmp [dict get $d power_nets] {VDD}]} "C power_nets={VDD} (SPECIALNETS wins over USE SIGNAL)"
    assert {[dict get $d signal_nets_count] == 1} "C signal_nets_count=1"
    assert {[dict get $d connected_count] == 1} "C connected_count=1 (n_sig)"
    assert {[lcmp [dict get $d single_pin_signal] {}]} "C single_pin_signal empty (VDD is power via SPECIALNETS)"
    assert {[dict get $d verdict] eq "clean"} "C verdict=clean"

    # ---- Case D: duplicate-connection trap -- 3x (I1 A) -> 1 unique, 2 duplicates ----
    set nD "- n_dup
  ( I1 A )
  ( I1 A )
  ( I1 A )
  ;
- n_ok
  ( I1 B )
  ( I2 C )
  ;"
    set sD ""
    set d [$candidate $nD $sD]
    assert {[dict get $d total_nets] == 2} "D total_nets=2"
    assert {[dict get $d signal_nets_count] == 2} "D signal_nets_count=2"
    assert {[dict get $d connected_count] == 1} "D connected_count=1 (n_ok only; n_dup has 1 unique)"
    assert {[lcmp [dict get $d single_pin_signal] {n_dup}]} "D single_pin_signal={n_dup} (1 unique pin)"
    assert {[dict get $d duplicate_connections] == 2} "D duplicate_connections=2"
    assert {[dict get $d verdict] eq "dangling"} "D verdict=dangling"

    # ---- Case E: USE-SIGNAL-overrides-pattern trap -- VSS USE SIGNAL is signal;
    #      GND with no USE is power by pattern ----
    set nE "- VSS USE SIGNAL
  ( I1 A )
  ( I2 B )
  ;
- GND
  ( I1 A )
  ;"
    set sE ""
    set d [$candidate $nE $sE]
    assert {[dict get $d total_nets] == 2} "E total_nets=2"
    assert {[lcmp [dict get $d power_nets] {GND}]} "E power_nets={GND} (VSS USE SIGNAL is signal, not power)"
    assert {[dict get $d signal_nets_count] == 1} "E signal_nets_count=1 (VSS only)"
    assert {[dict get $d connected_count] == 1} "E connected_count=1 (VSS)"
    assert {[lcmp [dict get $d single_pin_signal] {}]} "E single_pin_signal empty (GND power, VSS connected)"
    assert {[dict get $d verdict] eq "clean"} "E verdict=clean"

    # ---- Case F: empty / invariant ----
    set d [$candidate "" ""]
    assert {[dict get $d total_nets] == 0} "F total_nets=0"
    assert {[lcmp [dict get $d power_nets] {}]} "F power_nets empty"
    assert {[dict get $d signal_nets_count] == 0} "F signal_nets_count=0"
    assert {[dict get $d connected_count] == 0} "F connected_count=0"
    assert {[lcmp [dict get $d single_pin_signal] {}]} "F single_pin_signal empty"
    assert {[lcmp [dict get $d unconnected_signal] {}]} "F unconnected_signal empty"
    assert {[dict get $d duplicate_connections] == 0} "F duplicate_connections=0"
    assert {[dict get $d verdict] eq "clean"} "F verdict=clean"

    puts "RESULT:ALL_ASSERTS_PASS"
}
