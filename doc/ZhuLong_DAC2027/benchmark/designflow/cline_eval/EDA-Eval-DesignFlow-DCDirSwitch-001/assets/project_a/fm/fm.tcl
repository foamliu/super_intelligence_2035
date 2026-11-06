# fm.tcl -- Formality setup
set PRJ_ROOT [file dirname [file dirname [file normalize [info script]]]]
set dflt [file join $PRJ_ROOT synth results dc_2026-10-29-19.16.52]
if {[info exists ::env(DC_RESULT_DIR)]} {
    set dc_dir $::env(DC_RESULT_DIR)
} else {
    set dc_dir $dflt
}
read_db -path [file join $dc_dir stdcell.db]
read_verilog -container r -01 [file join $dc_dir top_a_postsyn.v]
