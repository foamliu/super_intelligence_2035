###############################################################################
# 5_read_parasitic.tcl -- 读入寄生参数(SPEF) 反标
###############################################################################
puts "RM-Info: 5_read_parasitic: reading parasitics ..."

set _spefs $PARASITIC_FILES
set _paths $PARASITIC_PATHS

if {[string length $_spefs] == 0} {
    set _spefs [sta_find_files $DATA_DIR {*.spef *.spef.gz *.spf}]
}

if {[llength $_spefs] > 0} {
    puts "RM-Info: 5_read_parasitic: parasitic files = $_spefs"
    # 推荐顺序: 先 block spef, 后 top spef
    if {[llength $_paths] == [llength $_spefs]} {
        foreach _p $_paths _f $_spefs {
            if {[string equal $_p $DESIGN_NAME]} {
                read_parasitics $_f
            } else {
                read_parasitics -path $_p $_f
            }
        }
    } else {
        foreach _f $_spefs {
            puts "RM-Info: 5_read_parasitic: read_parasitics $_f"
            read_parasitics $_f
        }
    }
} else {
    puts "RM-Info: 5_read_parasitic: no parasitic files found; skipping back-annotation."
}