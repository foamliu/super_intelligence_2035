###################################################################

# Created by write_sdc on Tue Oct 13 19:57:03 2026

###################################################################
set sdc_version 2.1

set_units -time ns -resistance kOhm -capacitance pF -voltage V -current mA
set_max_transition 0.1 [current_design]
set_max_area 0
set_load -pin_load 0.005 [get_ports {row[3]}]
set_load -pin_load 0.005 [get_ports {row[2]}]
set_load -pin_load 0.005 [get_ports {row[1]}]
set_load -pin_load 0.005 [get_ports {row[0]}]
set_load -pin_load 0.005 [get_ports {col[4]}]
set_load -pin_load 0.005 [get_ports {col[3]}]
set_load -pin_load 0.005 [get_ports {col[2]}]
set_load -pin_load 0.005 [get_ports {col[1]}]
set_load -pin_load 0.005 [get_ports {col[0]}]
set_load -pin_load 0.005 [get_ports valid]
set_max_delay 0.5  -from [list [get_ports {N[8]}] [get_ports {N[7]}] [get_ports {N[6]}]          \
[get_ports {N[5]}] [get_ports {N[4]}] [get_ports {N[3]}] [get_ports {N[2]}]    \
[get_ports {N[1]}] [get_ports {N[0]}]]  -to [list [get_ports {row[3]}] [get_ports {row[2]}] [get_ports {row[1]}]      \
[get_ports {row[0]}] [get_ports {col[4]}] [get_ports {col[3]}] [get_ports      \
{col[2]}] [get_ports {col[1]}] [get_ports {col[0]}] [get_ports valid]]
set_input_transition -max 0.02  [get_ports {N[8]}]
set_input_transition -min 0.02  [get_ports {N[8]}]
set_input_transition -max 0.02  [get_ports {N[7]}]
set_input_transition -min 0.02  [get_ports {N[7]}]
set_input_transition -max 0.02  [get_ports {N[6]}]
set_input_transition -min 0.02  [get_ports {N[6]}]
set_input_transition -max 0.02  [get_ports {N[5]}]
set_input_transition -min 0.02  [get_ports {N[5]}]
set_input_transition -max 0.02  [get_ports {N[4]}]
set_input_transition -min 0.02  [get_ports {N[4]}]
set_input_transition -max 0.02  [get_ports {N[3]}]
set_input_transition -min 0.02  [get_ports {N[3]}]
set_input_transition -max 0.02  [get_ports {N[2]}]
set_input_transition -min 0.02  [get_ports {N[2]}]
set_input_transition -max 0.02  [get_ports {N[1]}]
set_input_transition -min 0.02  [get_ports {N[1]}]
set_input_transition -max 0.02  [get_ports {N[0]}]
set_input_transition -min 0.02  [get_ports {N[0]}]
