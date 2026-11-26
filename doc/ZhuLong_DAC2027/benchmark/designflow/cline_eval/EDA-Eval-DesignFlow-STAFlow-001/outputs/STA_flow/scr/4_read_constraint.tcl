###############################################################################
# 4_read_constraint.tcl -- 读入时序约束(.sdc / .tcl)
###############################################################################
puts "RM-Info: 4_read_constraint: reading constraints ..."

set _sdcs $CONSTRAINT_FILES
if {[string length $_sdcs] == 0} {
    set _sdcs [sta_find_files $DATA_DIR {*.sdc *.tcl}]
}
puts "RM-Info: 4_read_constraint: constraint files = $_sdcs"

foreach _c $_sdcs {
    set _ext [string tolower [file extension $_c]]
    if {$_ext eq ".sdc"} {
        puts "RM-Info: 4_read_constraint: read_sdc -echo $_c"
        read_sdc -echo $_c
    } else {
        puts "RM-Info: 4_read_constraint: source -echo $_c"
        source -echo $_c
    }
}