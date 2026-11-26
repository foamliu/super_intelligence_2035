###############################################################################
# common_setup.tcl
# Shared design / path variables for the PrimeTime post-route STA signoff flow.
# Sourced by tcl/pt_sta.tcl. Parameterized so the same flow can be re-run on a
# different design / corner / library by editing only this file.
###############################################################################

# Top module name and compiled library (cell) name.
set DESIGN   addr_to_rowcol_v7
set LIB_NAME SS_0p98_m40c

# Inputs (paths are relative to the run directory).
set NETLIST  data/postroute.v
set SPEF     data/routed.spef
set SDC      data/mapped.sdc
set DB       data/ss_text.db

# Directory that receives the generated signoff reports.
set OUT_DIR  data