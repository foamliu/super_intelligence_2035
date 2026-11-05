# ============================================================================
# SDC timing constraints - addr_to_rowcol_region
# ============================================================================
# Combinational decode block (no on-chip clock/register). A virtual clock is
# created to budget the combinational datapath so that
#     input_delay + datapath_delay + output_delay  <=  CLK_PERIOD
# Parameters CLK_PERIOD / INPUT_DELAY / OUTPUT_DELAY / OUTPUT_LOAD are defined
# by the synthesis script before "source"-ing this file; the guarded defaults
# below make this file self-contained as well.
# ============================================================================

if { ![info exists CLK_PERIOD] }   { set CLK_PERIOD   2.0 }
if { ![info exists INPUT_DELAY] }  { set INPUT_DELAY  0.5 }
if { ![info exists OUTPUT_DELAY] } { set OUTPUT_DELAY 0.5 }
if { ![info exists OUTPUT_LOAD] }  { set OUTPUT_LOAD  0.05 }

# ---- virtual clock ---------------------------------------------------------
create_clock -name VCLK -period $CLK_PERIOD

# ---- input timing ----------------------------------------------------------
set_input_delay  -clock VCLK -max $INPUT_DELAY  [all_inputs]
set_input_delay  -clock VCLK -min 0.0           [all_inputs]

# ---- output timing ---------------------------------------------------------
set_output_delay -clock VCLK -max $OUTPUT_DELAY [all_outputs]
set_output_delay -clock VCLK -min 0.0           [all_outputs]

# ---- explicit combinational datapath budget --------------------------------
set MAX_COMB_DELAY [expr {$CLK_PERIOD - $INPUT_DELAY - $OUTPUT_DELAY}]
set_max_delay $MAX_COMB_DELAY -from [all_inputs] -to [all_outputs]

# ---- loading / drive-strength model (library: stdcells_ac_FF_1p3_m40c) -----
set_load          $OUTPUT_LOAD              [all_outputs]
set_driving_cell  -lib_cell invLx1 -pin Y   [all_inputs]

# ---- design-rule / area constraints ----------------------------------------
set_max_area 0
set_max_transition 0.5  [current_design]
set_max_capacitance 0.2 [current_design]