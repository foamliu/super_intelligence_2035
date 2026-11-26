proc uvs_regr_compile_summary_audit {compile_log_text test_list_text} {
    # --- declared testbenches (skip # lines, blanks, CR; first token = name) ---
    set declared_set {}
    foreach raw [split $test_list_text "\n"] {
        set line [string map {"\r" ""} $raw]
        set t [string trim $line]
        if {$t eq ""} continue
        if {[string index $t 0] eq "#"} continue
        set nm [lindex $t 0]
        if {$nm ne ""} { dict set declared_set $nm 1 }
    }

    # --- parse compile log ---
    set tags_compiled 0
    set total_rows 0
    set dup 0
    set cur_tag ""
    set last {}        ;# key "tb\x01tag" -> dict status errors warns elapsed
    set seen_any {}    ;# tb -> 1
    foreach raw [split $compile_log_text "\n"] {
        set line [string map {"\r" ""} $raw]
        set t [string trim $line]
        if {$t eq ""} continue
        # header: # Compile summary for tag <tag>
        if {[regexp -- {^#[[:space:]]+Compile summary for tag[[:space:]]+([^[:space:]]+)$} $t -> tag]} {
            set cur_tag $tag
            incr tags_compiled
            continue
        }
        # row: [STATUS] tb errors=N warns=N elapsed=T
        if {[regexp -- {^\[([A-Z]+)\][[:space:]]+([^[:space:]]+)[[:space:]]+errors=([0-9]+)[[:space:]]+warns=([0-9]+)[[:space:]]+elapsed=([0-9:]+)$} $t -> st tb ne nw el]} {
            incr total_rows
            # normalize elapsed: "<m>:<ss>" -> m*60+ss ; plain int -> int
            if {[string match "*:*" $el]} {
                set parts [split $el ":"]
                set mins [lindex $parts 0]
                set secs [lindex $parts 1]
                set esec [expr {$mins * 60 + $secs}]
            } else {
                set esec [scan $el %d]
            }
            set key "${tb}\x01${cur_tag}"
            if {[dict exists $last $key]} { incr dup }
            dict set last $key [dict create status $st errors $ne warns $nw elapsed $esec]
            dict set seen_any $tb 1
            continue
        }
        # else: ignore unrecognized line
    }

    # --- aggregate over last-wins unique (tb,tag) pairs ---
    set compiled_ok 0; set compile_fail 0; set skipped 0
    set error_total 0; set warn_total 0; set elapsed_total 0
    set tbFAIL {}       ;# tb -> 1 if any tag last-wins FAIL
    set tbOK {}         ;# tb -> 1 if any tag last-wins OK
    dict for {key info} $last {
        set st [dict get $info status]
        set tb [lindex [split $key "\x01"] 0]
        switch -- $st {
            "OK"   { incr compiled_ok;   dict set tbOK   $tb 1 }
            "FAIL" { incr compile_fail;  dict set tbFAIL $tb 1 }
            "SKIP" { incr skipped }
        }
        incr error_total [dict get $info errors]
        incr warn_total  [dict get $info warns]
        incr elapsed_total [dict get $info elapsed]
    }

    # --- recovered: tb with last-wins FAIL in some tag AND OK in another ---
    set recovered {}
    dict for {tb _} $tbFAIL {
        if {[dict exists $tbOK $tb]} { lappend recovered $tb }
    }
    set recovered [lsort $recovered]

    # --- missing: declared but never seen in any tag ---
    set missing {}
    dict for {tb _} $declared_set {
        if {![dict exists $seen_any $tb]} { lappend missing $tb }
    }
    set missing [lsort $missing]

    # --- max_elapsed_tb: per-tb max elapsed across tags, then global max ---
    #     tie -> lexicographically smallest name; "" if no rows.
    set tb_max {}       ;# tb -> max elapsed across its tags
    dict for {key info} $last {
        set tb [lindex [split $key "\x01"] 0]
        set el [dict get $info elapsed]
        if {![dict exists $tb_max $tb] || $el > [dict get $tb_max $tb]} {
            dict set tb_max $tb $el
        }
    }
    set max_el -1
    set max_tb ""
    dict for {tb el} $tb_max {
        if {$el > $max_el || ($el == $max_el && [string compare $tb $max_tb] < 0)} {
            set max_el $el
            set max_tb $tb
        }
    }
    # max_tb stays "" when there are no rows

    # --- verdict (FAIL > INCOMPLETE > PASS) ---
    if {$compile_fail > 0} {
        set verdict "FAIL"
    } elseif {[llength $missing] > 0} {
        set verdict "INCOMPLETE"
    } else {
        set verdict "PASS"
    }

    return [dict create \
        tags_compiled $tags_compiled \
        total_rows $total_rows \
        compiled_ok $compiled_ok \
        compile_fail $compile_fail \
        skipped $skipped \
        error_total $error_total \
        warn_total $warn_total \
        duplicate_compiles $dup \
        missing_compiles $missing \
        recovered_compiles $recovered \
        elapsed_total_sec $elapsed_total \
        max_elapsed_tb $max_tb \
        overall_verdict $verdict]
}
