# SiliconSmart characterization flow: drgqx_cmos_analog (33 cells)
source ./sisregular/configure.tcl

set lib   drgqx_cmos_analog
set cells { invx1 invx2 nand2x1 nor2x1 nand3x1 nor3x1 invx4 oai21x1 aoi21x1 }

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