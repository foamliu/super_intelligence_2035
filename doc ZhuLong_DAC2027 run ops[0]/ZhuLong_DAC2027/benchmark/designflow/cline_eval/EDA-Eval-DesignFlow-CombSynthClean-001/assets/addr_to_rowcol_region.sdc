# =============================================================================
# SDC constraints for addr_to_rowcol_region
#
# The design is purely combinational (no sequential elements).  A virtual
# clock "vclk" is created so that input/output delay, max_transition and
# load constraints can be expressed in a standard synthesis flow.
#
# Corner: FF 1.3V -40C  (matches stdcells_ac_FF_1p3_m40c.db, lib name FF_1p3_m40c)
# =============================================================================

# ---------------------------------------------------------------------------
# Virtual clock — period 5.0 ns gives the optimizer ample slack for a
# small combinational datapath.  Adjust CLOCK_PERIOD_NS in run_dc.sh to
# tighten or relax the target.
# ---------------------------------------------------------------------------
create_clock -name vclk -period 5.0 [get_ports RA]
set_clock_latency      0.0  [get_clocks vclk]
set_clock_transition   0.05 [get_clocks vclk]
set_clock_uncertainty -hold  0.10 [get_clocks vclk]
set_clock_uncertainty -setup 0.20 [get_clocks vclk]

# ---------------------------------------------------------------------------
# Input / output delays (expressed relative to vclk)
# ---------------------------------------------------------------------------
set_input_delay  -max 0.50 -clock vclk [get_ports RA]
set_input_delay  -min 0.05 -clock vclk [get_ports RA]
set_output_delay -max 0.50 -clock vclk [get_ports {row[*] col[*] region[*] valid}]
set_output_delay -min 0.05 -clock vclk [get_ports {row[*] col[*] region[*] valid}]

# ---------------------------------------------------------------------------
# Drive strength and load
#   invLx1 is confirmed present in library FF_1p3_m40c.
# ---------------------------------------------------------------------------
set_driving_cell -lib_cell invLx1 -pin Y [get_ports RA]
set_load  0.05 [get_ports {row[*] col[*] region[*] valid}]
set_input_transition 0.05 [get_ports RA]

# ---------------------------------------------------------------------------
# Design-rule constraints
# ---------------------------------------------------------------------------
set_max_transition  0.50 [current_design]
set_max_capacitance 0.25 [current_design]
set_max_fanout      30   [current_design]

# ---------------------------------------------------------------------------
# Multicycle / false paths
#   The design has only one combinational path group (vclk -> vclk).
#   No multicycle or false-path exceptions are required.
# ---------------------------------------------------------------------------
