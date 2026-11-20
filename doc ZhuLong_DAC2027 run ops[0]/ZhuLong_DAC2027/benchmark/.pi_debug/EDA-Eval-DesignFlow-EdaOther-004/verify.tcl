# Verification harness: run reference impl on 6 cases, print outputs.
source reference.tcl

# ---- Case A: baseline mirroring real cliu session ----
set plistA "avl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\nmbist_three_deep\n# this is a comment\n\ntm_multirow\ntm_pretest\nmbist_three_deep"
set repA "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\nGlobal_Seed : 100\n-----------------\navl_ca_odt\nbasic_BurstOrderLengthType\nbasic_allbank_bc8\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 200\n-----------------\nmbist_three_deep\ntm_multirow\n=== misc.x16 ===\nTotal Pattern : 2\n Failed Pattern: 0\nGlobal_Seed : 300\n-----------------\ntm_pretest\nextra_pattern_x"
puts "CASE A: [vsim_pattern_coverage_audit $repA $plistA]"

# ---- Case B: colon-spacing tooth (both forms) + cross-rpt dup ----
set plistB "p1\np2\np3\np4\np5\np6"
set repB "=== r1.x4 ===\nTotal Pattern : 4\n Failed Pattern: 2\n-----------------\np1\np2\np3\np4\n=== r2.x8 ===\nTotal Pattern: 3\n  Failed Pattern: 1\n-----------------\np1\np5\np6"
puts "CASE B: [vsim_pattern_coverage_audit $repB $plistB]"

# ---- Case C: reference-list hygiene tooth (dup + comment + blank + CR + trailing space) ----
set plistC "p1\np2\n# comment line\n\np3\r\np2\np4  "
set repC "=== only.x4 ===\nTotal Pattern : 5\n Failed Pattern: 0\n-----------------\np1\np2\np3\np4\np5"
puts "CASE C: [vsim_pattern_coverage_audit $repC $plistC]"

# ---- Case D: bytemode/regression extraction tooth (.rerun suffix, nosuffix) ----
set plistD "pa\npb\npc"
set repD "=== basic.x4.rerun ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npa\n=== misc.x16 ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npb\n=== nosuffix ===\nTotal Pattern : 1\n Failed Pattern: 0\n-----------------\npc"
puts "CASE D: [vsim_pattern_coverage_audit $repD $plistD]"

# ---- Case E: header-vs-list mismatch + separator/header-exclusion tooth ----
set plistE "pa\npb\npc\npd\npe\npf"
set repE "=== r1.x4 ===\nTotal Pattern : 5\n Failed Pattern: 1\nGlobal_Seed : 42\n-----------------\npa\npb\npc\npd\n=== r2.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\npe\npf"
puts "CASE E: [vsim_pattern_coverage_audit $repE $plistE]"

# ---- Case F: comprehensive + dup-within-rpt + missing_and_extra + invariant ----
set plistF "avl_ca_odt\nbasic_allbank_bc8\ntm_multirow\ntm_pretest\n# dup below\ntm_pretest"
set repF "=== basic.x4 ===\nTotal Pattern : 3\n Failed Pattern: 1\n-----------------\navl_ca_odt\nbasic_allbank_bc8\navl_ca_odt\n=== checkin.x8 ===\nTotal Pattern : 2\n Failed Pattern: 0\n-----------------\ntm_multirow\nghost_pattern"
puts "CASE F: [vsim_pattern_coverage_audit $repF $plistF]"
