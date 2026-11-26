# global SiliconSmart configure (sourced by each export/*.tcl)
set_config_opt -param VDD   1.2
set_config_opt -param VSS   0.0
set_config_opt -param VDDIO 2.5

# vssFoot param definition
set_config_opt -param vssFoot {0.0}

set_config_opcond __default__ -voltage { vdd 1.2 vss 0.0 }
set_config_opt -opcond __default__ -- temperature 25

# duplicate vssFoot definition (bug: PARA configure.tcl dup) - removed
# set_config_opt -param vssFoot {0.0}