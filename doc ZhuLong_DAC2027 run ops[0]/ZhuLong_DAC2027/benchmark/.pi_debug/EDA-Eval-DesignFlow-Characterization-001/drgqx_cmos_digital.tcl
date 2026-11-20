# SiliconSmart characterization flow: drgqx_cmos_digital (180 cells)
source ./sisregular/configure.tcl

set lib   drgqx_cmos_digital
set cells { invx1 invx2 nand2x1 nor2x1 and2x1 or2x1 xor2x1 xnor2x1 mux2x1 }

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