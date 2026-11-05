# dc_setup_filenames.tcl -- file path variables (59 lines)
# NOTE: FINAL_UPF is defined here but dc.tcl hardcodes ${DESIGN_NAME}_dc.upf
#       in save_upf -- FINAL_UPF is never referenced (latent inconsistency).
set DESIGN_NAME      hl22_porting_test_chip_v1
set SETUP_DIR        ./synth/scripts
set RTL_SOURCE_FILES [glob ./rtl_power/*.v]
set SDC_FILE         ./sdc/hl22.mapped.sdc
set RESULTS_DIR      ./synth/results/dc_2026-10-30-20.08.51
set REPORTS_DIR      ./synth/reports/dc_2026-10-30-20.08.51
set TARGET_LIBRARY_FILES [glob ./pdk/stdcells_ssg.lib]
set LINK_LIBRARY_FILES   [glob ./pdk/stdcells_ssg.lib]
set WIRE_LOAD_MODEL  "smic18_wl10"
set CLOCK_NAME       clk
set CLOCK_PORT       clk
set CLOCK_PERIOD     5.0
set VDD_VOLTAGE      0.72
set VSS_VOLTAGE      0.0
set UPF_FILE         ./upf/test_chip_power.upf
set FINAL_UPF        ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf
set SEARCH_PATH      "./pdk ./rtl_power ./sdc ./upf"
