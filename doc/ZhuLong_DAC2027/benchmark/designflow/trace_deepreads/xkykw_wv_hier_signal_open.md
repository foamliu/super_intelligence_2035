# Deepread: 1794386871675_xkykw (WvHierSignalOpen-001)

- **session**: 1794386871675_xkykw
- **user/host**: ypzheng / hfeg0pkn003
- **mc**: 46 (waveview domain)
- **msgs**: 58 / 4 substantive user turns (act mode)
- **domain**: waveform (WaveView ACE Tcl hierarchical signal resolve + display)

## User turns
- U#0: "找一下net1069这个信号，在波形中打开"
- U#1: "没看到打开啊"
- U#2: "打开v(cs)"
- U#3: "根本没打开啊 cs信号没有probe出来"

## Key trace insights (the "lesson")
1. **Hierarchical signal**: `net1069` is an internal hierarchical node; its full name is `xi_c_top.xi_array16gtop.v(net1069)` with 51 variants under bank submodules. Using the simple name directly fails.
2. **NULL return**: `sx_find_wave_in_all_files` returns the string `"NULL"` (not empty `""`) when a signal is not found. Must check both.
3. **sx_display unreliable**: `sx_display <name>` (by string name) "executes" but doesn't actually probe/display the signal — the waveform window remains empty.
4. **sx_display_wave reliable**: `sx_display_wave $wv $wave -auto_new_wv` (by object handle: waveview obj + wave_obj from sx_find_wave_in_all_files) actually adds the signal to a new panel and displays it. Must follow with `sx_update_wv $wv` to refresh.
5. **Slow-path resolution**: When simple name fails, scan opened files via `sx_wdf_info opened` → `sx_wdf_info $fh -waveforms` → `lsearch -glob` for names containing the keyword → pick the **shortest** (shallowest hierarchy) match.
6. **Performance**: `sx_wdf_info $fh -waveforms` on a file with 1M+ signals times out the 30s sandbox. Must iterate file-by-file, stop at first hit (don't concat all files' lists).

## Final deliverable (open_signal proc)
```tcl
proc open_signal {name {filepath ""}} {
    # ... filepath open ...
    set fullname $name
    set wave [sx_find_wave_in_all_files $fullname]
    if {$wave == "" || $wave == "NULL"} {
        # slow path: scan files, prefer shortest match
        set fullname ""
        foreach fh [sx_wdf_info opened] {
            set names [sx_wdf_info $fh -waveforms]
            set hit [lsearch -all -inline -glob $names "*${name}*"]
            if {[llength $hit] > 0} {
                set fullname [lindex $hit 0]
                foreach h $hit {
                    if {[string length $h] < [string length $fullname]} {
                        set fullname $h
                    }
                }
                break
            }
        }
        if {$fullname eq ""} { error "Signal not found" }
        set wave [sx_find_wave_in_all_files $fullname]
    }
    set wv [sx_current_wv]
    sx_display_wave $wv $wave -auto_new_wv
    sx_update_wv $wv
    return $fullname
}
```

## B-grade synthesized reframe
- Original FSDB private binary not reproducible → synthesize WaveView ACE Tcl mock shim
- Mock simulates sx_* APIs with hidden B/B2/B3 waveform databases
- L2: tclsh runs candidate's open_signal.tcl through mock, check.py verifies call sequence + waveview state
- B (hidden): target=net2077, hierarchy=tb.clk_div.v(net2077), longer matches placed first to test shortest-match logic
- B2 (robustness): target=GONE_SIGNAL (not found → must error)
- B3 (fast path): target=v(vref) (top-level, direct hit)
- Anti-hardcode: A-side names (net1069/xi_c_top/xi_array16gtop/v(cs)/...) forbidden in candidate source

## check.py: 14 conditions (a-n)
a) valid zip + open_signal.tcl
b) source signal_spec.tcl
c) B exits 0
d) sx_find_wave_in_all_files called
e) sx_display_wave called
f) sx_update_wv called
g) sx_display NOT called (unreliable API)
h) resolved B-side hierarchical name (anti-hardcode)
i) displayed wave_obj is valid WAVE_* handle (not string/NULL)
j) shortest match (WAVE_2077a, not longer variants)
k) B2 robustness (error raised, exit non-zero)
l) anti-hardcode source (no A-side identifiers)
m) B3 fast-path (exit 0 + WAVE_vref)
n) deterministic re-run

Self-verify: REF PASS 14/14 ✓ / 9 negatives all FAIL ✓ / §4.9 degenerate all FAIL ✓ / 9 distinct labels ✓
