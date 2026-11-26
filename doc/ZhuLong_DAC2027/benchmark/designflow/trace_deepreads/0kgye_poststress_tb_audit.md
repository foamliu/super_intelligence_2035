# Deepread · 0kgye · tongfanl@hfhds201 · Poststress/TB correspondence audit

## Trace
- session: 1793842420935_0kgye.messages.json (48 msgs, 392KB, dir-based)
- user: tongfanl, host: hfhds201, match_count=60, spice-dominant (ratio 0.377)
- updated_at: 2026-11-05T02:10:29Z

## User intent (U#0, verbatim — A-faithful task statement)
> 帮我检查下，/home/tongfanl/DDR6/DSCQA/analogsim/Poststress/文件夹下的几个文件与该TB环境/proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local是否对应，能否实现相应的目的。

- 提出需求，无根因/修复方向 → 符合 A-档选轮
- U#39 = "?" (nudge, not a task) → 不入 prompt

## Assistant tool chain (gold standard workflow)
1. list_allowed_files Poststress/ + vecgen_local/ → Poststress/ = 10 .v symlinks + Force/; vecgen_local = full TB env
2. run_approved_command (shell) + read_files Poststress001_Dualbank_Datapath.v (80 lines) + Force/Poststress009.config
3. Wrote check_poststress_links.py (4 versions, iterative): resolve symlinks, parse cfg_Aging, grep d6vecgen, check Include
4. read_files d6vecgen lines 60-130/280-500/791-833 → consumption chain: d6vecgen line 88-95 maps $CoverageDir/analogsim → patterns/analogsim; line 414/433/450/470 @patSeqFile = patterns/analogsim/$funcName/$pattern.v; line 821 getCmdTask $patName(...)
5. Resolved patterns/analogsim/Poststress → /home/coverage/DDR6/DSCQA/analogsim/Poststress
6. samefile: /home/coverage vs /home/tongfanl Poststress dirs = False (independent copies, currently same content); Poststress.inc = True (same file)

## Gold standard (A#47 final answer, user-accepted)
### Correspondence (holds ✅)
1. d6vecgen maps $CoverageDir/analogsim → patterns/analogsim; patterns/analogsim/Poststress → /home/coverage/DDR6/DSCQA/analogsim/Poststress
2. Include/Poststress.inc includes all 10 patterns (001-010) → all exist
3. Poststress/ 10 .v + Force/ = 11 items, all symlinks valid → SOS cache (/home/sosadmin/sos/cache/Coverage.cac/Finesim/...)
4. Force/: Poststress005.inc/008.inc (force stimuli), Poststress009.config (13 PVT corners → .inc, all 13 exist)

### Problem ⚠️ cfg_Aging naming mismatch
- Line 21 ACTIVE: `Poststress001_Perbank_Datapath` → file NOT FOUND (actual = Poststress001_Dualbank_Datapath.v); bank=2b32g_BLs (2-bank) matches Dualbank not Perbank → compile/sim failure
- Lines 22-30 commented (##): Poststress002-010 (new naming, match files but won't run)

### Conclusion
- Files correspond to TB env, CAN achieve Poststress sim coverage purpose
- Need to fix cfg_Aging: rename line 21 to Dualbank, uncomment 002-010
- Minor: Poststress001_Dualbank_Datapath.v internal block name still Poststress001_Perbank_Datapath_task (harmless legacy)

## Key real assets (for case)
- Poststress.inc: 12 include lines (2 Include/ refs + 10 Poststress/*.v refs)
- cfg_Aging: 32 lines; line 1 Aging active; lines 2-6 # commented; lines 8-12 # commented (old); lines 14-18 # commented (TT); line 21 ACTIVE Poststress001_Perbank_Datapath (MISMATCH); lines 22-30 ## commented
- Poststress009.config: 13 corners (FF1.23V130C, FF1.23V-40C, FS1.23V130C, FS1.23V-40C, SF1.23V130C, SF1.23V-40C, SS0.92V130C, SS0.92V-40C, FS0.92V130C, FS0.92V-40C, SF0.92V130C, SF0.92V-40C, TT0.92V25C)
- Poststress001_Dualbank_Datapath.v: task with block name Poststress001_Perbank_Datapath_task (naming legacy), DDR6 pattern with Active/Write/Read/Precharge/MRR/Load_Mode calls
- d6vecgen: Perl script, line 88-95 symlink $CoverageDir/analogsim, line 414/433/450/470 patSeqFile = patterns/analogsim/$funcName/$pattern.v

## Generalized sub-skill
audit_poststress_correspondence.py <poststress_dir> <tb_dir> -o out.json
- Parse Include/Poststress.inc → pattern .v refs → check exists in poststress_dir
- Parse cfg_files/cfg_Aging → entries (active/commented, pattern_name, bank_field, corners, file_exists)
- Parse Force/Poststress009.config → corner→inc mapping → check .inc exists in Force/
- Detect mismatches: active cfg entries whose pattern file doesn't exist
- Bank consistency: active entries' bank_field vs pattern_name (Perbank=1b, Dualbank/Multibank=2b+)
- conclusion: correspondence_holds, can_achieve_purpose, issues[]

## Case plan
- ID: EDA-Eval-DesignFlow-PoststressTbAudit-001
- domain: spice_sim, track: A-faithful, level: L1 (static audit)
- A = real Poststress/ + tb (cfg_Aging with Perbank/Dualbank mismatch, 13 force corners all present)
- hidden B = synthesized Stresspattern/ (8 patterns, 2 active [1 file-not-found + 1 consistent], 10 force corners 1 missing .inc)
- check.py ≥13 assertions on B
