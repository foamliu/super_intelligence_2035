proc cdl_lib_coverage_check {lib_path cdl_dir} {
    set lib_cells {}
    if {[file exists $lib_path]} {
        set f [open $lib_path r]
        while {[gets $f line] >= 0} {
            if {[regexp {^\s*cell\s*\(\s*"?([^"()\s]+)"?\s*\)} $line -> name]} {
                lappend lib_cells $name
            }
        }
        close $f
    }
    set lib_cells [lsort -unique $lib_cells]

    set cdl_cells {}
    foreach f [glob -nocomplain -directory $cdl_dir -type f -- *.cdl] {
        lappend cdl_cells [regsub {\.cdl$} [file tail $f] {}]
    }
    set cdl_cells [lsort -unique $cdl_cells]

    set missing {}
    foreach c $lib_cells {
        if {[lsearch -exact $cdl_cells $c] < 0} {
            lappend missing $c
        }
    }
    set extra {}
    foreach c $cdl_cells {
        if {[lsearch -exact $lib_cells $c] < 0} {
            lappend extra $c
        }
    }

    set tokens [list lib_cell_count [llength $lib_cells] \
        cdl_cell_count [llength $cdl_cells] \
        missing_count [llength $missing] \
        extra_count [llength $extra] \
        missing_in_cdl]
    lappend tokens {*}$missing
    lappend tokens extra_in_cdl
    lappend tokens {*}$extra
    return "[join $tokens " "] "
}