# =============================================================================
# Design Compiler synthesis flow for a purely-combinational block
# (top: addr_to_rowcol_region).
#
# Inputs are supplied through environment variables by run_dc.sh:
#   TARGET_DB         -> target/link library (.db)
#   TOP_DESIGN        -> top-level module name
#   RTL_FILE          -> Verilog RTL source
#   SDC_FILE          -> input SDC constraints
#   OUTPUT_DIR        -> output directory for reports / netlist / mapped SDC
#   COMB_MAX_DELAY_NS -> (optional) combinational max-delay, default 3.0 ns
# =============================================================================

# ---- Required environment variables ----------------------------------------
foreach ev {TARGET_DB TOP_DESIGN RTL_FILE SDC_FILE OUTPUT_DIR} {
    if {![info exists ::env($ev)] || $::env($ev) eq ""} {
        error "ERROR: environment variable '$ev' is not set"
    }
}

set TOP_DESIGN $::env(TOP_DESIGN)
set RTL_FILE   $::env(RTL_FILE)
set SDC_FILE   $::env(SDC_FILE)
set TARGET_DB  $::env(TARGET_DB)
set OUTPUT_DIR $::env(OUTPUT_DIR)

# ---- Library setup ---------------------------------------------------------
set_app_var search_path    [list . [file dirname $TARGET_DB] [file dirname $RTL_FILE]]
set_app_var target_library [list $TARGET_DB]
set_app_var link_library   [concat "*" $target_library]

file mkdir $OUTPUT_DIR
file mkdir $OUTPUT_DIR/work
define_design_lib WORK -path $OUTPUT_DIR/work

# ---- Read RTL / elaborate / link -------------------------------------------
analyze -format verilog $RTL_FILE
elaborate $TOP_DESIGN
current_design $TOP_DESIGN
link

# ---- Apply input constraints -----------------------------------------------
# Note: the input SDC contains clock-related constraints (virtual clock vclk
# on RA).  They are loaded here so the flow keeps working unchanged; the
# post-processing step below strips them from the *written* mapped SDC.
source $SDC_FILE

# ---- Compile / map ---------------------------------------------------------
compile_ultra

# ---- Write outputs ---------------------------------------------------------
change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output $OUTPUT_DIR/${TOP_DESIGN}_mapped.v
write -format ddc     -hierarchy -output $OUTPUT_DIR/${TOP_DESIGN}_mapped.ddc
write_sdc $OUTPUT_DIR/${TOP_DESIGN}_mapped.sdc

# =============================================================================
# Post-processing: this design is purely combinational, so the clock-related
# constraints that write_sdc just wrote (create_clock, set_clock_latency,
# set_clock_uncertainty, set_clock_transition, set_input_delay,
# set_output_delay) are meaningless and would mislead downstream STA.
#
# Scan the freshly written mapped SDC line by line, drop every clock-related
# command (including multi-line backslash continuations), then append a single
# generic combinational max-delay constraint in their place.
#
#   * set_max_delay defaults to 3.0 ns and can be overridden through the
#     COMB_MAX_DELAY_NS environment variable.
#   * [all_inputs] / [all_outputs] keep this step generic: it applies to any
#     purely-combinational module with no port-name hardcoding.
# =============================================================================
set COMB_MAX_DELAY_NS 3.0
if {[info exists ::env(COMB_MAX_DELAY_NS)] && $::env(COMB_MAX_DELAY_NS) ne ""} {
    set COMB_MAX_DELAY_NS $::env(COMB_MAX_DELAY_NS)
}

set CLK_CMD_RE {^\s*(create_clock|set_clock_latency|set_clock_uncertainty|set_clock_transition|set_input_delay|set_output_delay)(\s|$)}

set MAPPED_SDC $OUTPUT_DIR/${TOP_DESIGN}_mapped.sdc
set sdc_fh [open $MAPPED_SDC r]
set sdc_lines [split [read $sdc_fh] "\n"]
close $sdc_fh
# Drop a single trailing empty element produced by a trailing newline so that
# we do not introduce a stray blank line before the appended set_max_delay.
if {[llength $sdc_lines] > 0 && [lindex $sdc_lines end] eq ""} {
    set sdc_lines [lrange $sdc_lines 0 end-1]
}

set sdc_fh [open $MAPPED_SDC w]
set in_drop 0
foreach line $sdc_lines {
    if {$in_drop} {
        # Still inside a multi-line command that is being deleted.
        if {![regexp {\\\s*$} $line]} {
            set in_drop 0
        }
        continue
    }
    if {[regexp $CLK_CMD_RE $line]} {
        set in_drop 1
        if {![regexp {\\\s*$} $line]} {
            set in_drop 0
        }
        continue
    }
    puts $sdc_fh $line
}
puts $sdc_fh "set_max_delay ${COMB_MAX_DELAY_NS} -from \[all_inputs\] -to \[all_outputs\]"
close $sdc_fh

puts "INFO: stripped clock-related constraints from $MAPPED_SDC"
puts "INFO: added: set_max_delay ${COMB_MAX_DELAY_NS} -from \[all_inputs\] -to \[all_outputs\]"

quit