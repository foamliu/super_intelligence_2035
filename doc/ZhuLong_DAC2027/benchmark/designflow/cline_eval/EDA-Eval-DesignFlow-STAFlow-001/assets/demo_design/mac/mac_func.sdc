# mac_func.sdc — functional-mode SDC for the demo design "mac"
create_clock -name clk -period 10.0 [get_ports clk]
set_input_delay  2.0 -clock clk [all_inputs]
set_output_delay 2.0 -clock clk [all_outputs]
set_clock_latency 0.5 [get_clocks clk]
set_clock_uncertainty 0.2 [get_clocks clk]
set_drive 0.1 [all_inputs]
set_load 0.05 [all_outputs]
