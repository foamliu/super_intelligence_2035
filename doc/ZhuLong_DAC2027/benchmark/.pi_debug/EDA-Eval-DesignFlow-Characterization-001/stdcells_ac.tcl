# SiliconSmart characterization flow: stdcells_ac (678 cells, AC characterization)
source ./sisregular/configure.tcl

set lib   stdcells_ac
set cells { invx1_ac nand2x1_ac nor2x1_ac dffx1_ac }

# --- library qualification via lc_shell ---
# set_config_opt qualification_lc_shell "-lc_shell_path /tools/synopsys/lc_shell/bin/lc_shell"
# qualify_library $lib

# --- device modeling ---
model -create_new_model -timing $cells

# --- characterize each cell ---
foreach c $cells {
    source ./sisregular/$lib/control/$c.inst
}
characterize -cells $cells