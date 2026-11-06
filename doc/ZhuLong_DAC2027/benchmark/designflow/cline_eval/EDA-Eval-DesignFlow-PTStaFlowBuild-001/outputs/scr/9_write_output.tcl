#===============================================================================
# FILE    : 9_write_output.tcl
# PURPOSE : Emit the generated output files:
#             * sdc/     -> a generated .sdc snapshot (write_sdc)
#             * session/ -> an interactive pt_shell session snapshot (save_session)
#             * rpt/     -> optional SDF (write_sdf) for downstream signoff
#===============================================================================
puts "RM-Info: [info script] : writing outputs"

# Generated SDC: captures all constraints currently effective on the design
# (this is what the sdc/ directory is meant to hold).
set gen_sdc [file join $SDC_DIR "${REPORT_TAG}.sdc"]
write_sdc -version 2.1 $gen_sdc
puts "RM-Info: generated SDC -> $gen_sdc"

# Save an interactive session so the flow can be resumed interactively in
# pt_shell (this is what the session/ directory is meant to hold).
set session_name [file join $SES_DIR $REPORT_TAG]
save_session $session_name
puts "RM-Info: saved session -> $session_name"

# Optional timing (SDF) back-annotation output for downstream tools.
if {[info exists WRITE_SDF] && $WRITE_SDF} {
    set gen_sdf [file join $RPT_DIR "${REPORT_TAG}.sdf"]
    write_sdf -version 3.0 $gen_sdf
    puts "RM-Info: generated SDF -> $gen_sdf"
}

puts "RM-Info: [info script] completed"