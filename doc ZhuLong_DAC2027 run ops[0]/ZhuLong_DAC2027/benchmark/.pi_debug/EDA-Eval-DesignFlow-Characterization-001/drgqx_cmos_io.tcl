# SiliconSmart characterization flow: drgqx_cmos_io (154 cells)
source ./sisregular/configure.tcl

set lib   drgqx_cmos_io
set cells { ffrqIOLVx2_pc60_odt nor3IOLVIOx1_DQS invYx2_CoM IO_TX_LOCAL_DCA_DQS IO_capbuf_vrefdq_anti_kb }

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