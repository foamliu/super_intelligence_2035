# innovus_fp.tcl -- original (pre-fix) power routing for test_chip_v1
# Unconditional globalNetConnect: no generation probe, no VERIFY distinction.
globalNetConnect VDD_PM -instanceBasename PMRowBLK_* -netType power
globalNetConnect VDD -instanceBasename * -netType power
globalNetConnect VSS -instanceBasename * -netType power
addStripe -net VDD_PM -layer M4 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
addStripe -net VDD -layer M5 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
addStripe -net VSS -layer M5 -start_offset 5.0 -spacing 1.2 -width 0.8 -set_to_set_distance 40
sroute -nets VDD_PM
sroute -nets VDD
sroute -nets VSS
exit 0
