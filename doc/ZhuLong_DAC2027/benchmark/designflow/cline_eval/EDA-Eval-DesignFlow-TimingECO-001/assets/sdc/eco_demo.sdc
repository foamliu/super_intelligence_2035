# eco_demo timing constraints (TUTORIAL library, ideal-clock demo)
# - period chosen generously long so the hold-fix buffers do not break setup
# - hold uncertainty of 0.5ns deliberately creates a NETLIST-LEVEL reg-to-reg
#   hold violation (short path) that PrimeTime ECO must fix by inserting a
#   delay / buffer cell on the data path.
# - input/output delays chosen so only the REG->REG path is the violating one
create_clock -name clk -period 6.000 [get_ports clk]
set_clock_uncertainty -setup 0.05 [get_clocks clk]
set_clock_uncertainty -hold  0.50 [get_clocks clk]
set_input_delay  1.00 -clock clk [get_ports din]
set_output_delay 0.20 -clock clk [get_ports dout]
