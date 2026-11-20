#!/bin/csh -f
###############################################################################
# run_pt.csh
# C-shell launcher for the PrimeTime post-route STA signoff flow.
#
#   - Sets the Synopsys license environment variables.
#   - Strips a polluted LD_PRELOAD via `env -u LD_PRELOAD` before starting
#     pt_shell (a polluted LD_PRELOAD breaks PT/StarRC startup).
#   - Runs the parameterized STA script tcl/pt_sta.tcl.
###############################################################################

# License setup
setenv SNPSLMD_LICENSE_FILE 27000@hfds4:12000@hfds4
setenv LM_LICENSE_FILE 27000@hfds4:12000@hfds4

# Launch PrimeTime with a clean LD_PRELOAD environment.
env -u LD_PRELOAD pt_shell -file tcl/pt_sta.tcl