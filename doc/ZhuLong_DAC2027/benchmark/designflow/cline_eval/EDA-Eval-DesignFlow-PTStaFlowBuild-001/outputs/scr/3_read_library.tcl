#===============================================================================
# FILE    : 3_read_library.tcl
# PURPOSE : Submodule library input files reading.
#           Reads the corner-specific submodule Liberty databases (.db) and adds
#           them to the link path so that submodule cells (memory / IO / hard
#           macro) resolve correctly during link_design.
#===============================================================================
puts "RM-Info: [info script] : reading submodule libraries"

if {![info exists DATA_DIR]} { set DATA_DIR [file join $ROOT_DIR data] }
if {![info exists LIB_BASE]} { set LIB_BASE   [file join $DATA_DIR "lib" $PT_CORNER] }

# Submodule Liberty inputs: collected from the corner lib sub-directory and from
# an optional dedicated sub-module library directory.
if {![info exists SUBMODULE_LIB_FILES]} {
    set SUBMODULE_LIB_FILES ""
    set sub_dirs [list \
        [file join $LIB_BASE "sub"] \
        [file join $DATA_DIR "sub_lib" $PT_CORNER] ]
    foreach sub_dir $sub_dirs {
        foreach L [glob -nocomplain [file join $sub_dir "*.db"]] {
            lappend SUBMODULE_LIB_FILES $L
        }
        foreach L [glob -nocomplain [file join $sub_dir "*.lib"]] {
            lappend SUBMODULE_LIB_FILES $L
        }
    }
}
set SUBMODULE_LIB_FILES [string trim $SUBMODULE_LIB_FILES]
puts "RM-Info: SUBMODULE_LIB_FILES = $SUBMODULE_LIB_FILES"

foreach L $SUBMODULE_LIB_FILES {
    if {[string match "*.db" $L]} {
        puts "RM-Info: read_db $L"
        read_db $L
    } else {
        puts "RM-Warning: '$L' is a Liberty source (.lib); compile it into a .db"
        puts "            with Library Compiler (lc_shell) before PT reads it."
    }
}

# Extend the link path so submodule cells resolve at link_design time.
set link_path [concat $link_path $SUBMODULE_LIB_FILES]

puts "RM-Info: [info script] completed"