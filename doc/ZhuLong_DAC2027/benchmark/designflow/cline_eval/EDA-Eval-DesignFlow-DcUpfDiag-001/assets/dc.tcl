# dc.tcl -- Design Compiler synthesis driver for hl22_porting_test_chip_v1
# (faithful reconstruction of test_chip_v1/synth/scripts/dc.tcl, 130 lines)
source -echo -verbose ${SETUP_DIR}/common_setup.tcl
source -echo -verbose ${SETUP_DIR}/dc_setup_filenames.tcl

set_app_options -name hdlin.auto_rtl_connect_all_pins -value true
set_app_options -name compile.enable_register_merging -value false

# library search path + target link
set_search_path ${SEARCH_PATH}
set_target_library ${TARGET_LIBRARY_FILES}
set_link_library ${LINK_LIBRARY_FILES}

# read + elaborate RTL
define_design_lib WORK -path ./${DESIGN_NAME}_work
analyze -format sverilog -work WORK ${RTL_SOURCE_FILES}
elaborate ${DESIGN_NAME} -work WORK
current_design ${DESIGN_NAME}
link

# timing / constraints
source -echo -verbose ${SDC_FILE}
set_wire_load_model -name ${WIRE_LOAD_MODEL}
set_wire_load_mode top

# clock
create_clock -name ${CLOCK_NAME} -period ${CLOCK_PERIOD} [get_ports ${CLOCK_PORT}]
set_dont_touch_network [get_clocks ${CLOCK_NAME}]

# --- UPF power intent (loaded AFTER link; see notes) ---
set_app_options -name upf.enable_golden_upf -value true
load_upf ${UPF_FILE}
set_voltage ${VDD_VOLTAGE} -object_list [get_supply_nets VDD]
set_voltage ${VSS_VOLTAGE} -object_list [get_supply_nets VSS]

# multi-voltage + retention checks
check_mv_design -verbose

# compile
compile_ultra -no_autoungroup -gate_clock

# write netlist (note: write -format verilog never emits PG pins)
change_names -rules verilog -hierarchy
write -format verilog -hierarchy -output ${RESULTS_DIR}/${DESIGN_NAME}_postsyn.v

# save upf (supplemental => only writes DELTAS vs golden UPF)
save_upf -supplemental -include_supply_exceptions ${RESULTS_DIR}/${DESIGN_NAME}_dc.upf

# reports
report_area   > ${REPORTS_DIR}/${DESIGN_NAME}.area.rpt
report_timing > ${REPORTS_DIR}/${DESIGN_NAME}.timing.rpt
report_power  > ${REPORTS_DIR}/${DESIGN_NAME}.power.rpt
exit
