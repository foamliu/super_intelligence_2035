###############################################################################
# 2_read_lib.tcl -- 读入子模块 lib 输入件，配置 target/link library
# 支持 .lib(读入并编译) 与 .db(直接用于 target/link) 两种输入。
###############################################################################
puts "RM-Info: 2_read_lib: reading library inputs ..."

# 若 -x 未显式给库，则自动在 data/(含 data/lib/) 中发现
set _libs $ANALYSIS_LIBRARY_FILES
if {[string length $_libs] == 0} {
    set _libs [sta_find_files $DATA_DIR {*.lib *.db}]
}
puts "RM-Info: 2_read_lib: library files = $_libs"

set _target_libs {}
foreach _l $_libs {
    # 库所在目录加入 search_path，便于 db 解析子模块引用
    lappend search_path [file dirname $_l]
    set _ext [string tolower [file extension $_l]]
    if {$_ext eq ".lib"} {
        set _lib_obj [read_lib $_l]
        foreach_in_collection _lb $_lib_obj {
            lappend _target_libs [get_object_name $_lb]
        }
    } else {
        lappend _target_libs $_l
    }
}

set target_library [lsort -unique $_target_libs]
set link_path      "* $target_library $ADDITIONAL_LINK_LIB_FILES"

puts "RM-Info: 2_read_lib: target_library = $target_library"
puts "RM-Info: 2_read_lib: link_path      = $link_path"