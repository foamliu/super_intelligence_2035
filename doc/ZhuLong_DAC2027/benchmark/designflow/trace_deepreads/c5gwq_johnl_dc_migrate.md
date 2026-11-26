# Deepread: 1793932600947_c5gwq (johnl @ hfeg0pkn001 / 10.129.2.10, mc=306)

> scanned from daily eda_trace_20261109.log (NOT in 11/05 summary — newer session).
> tools: 137 netlist / 130 synthesis / 20 innovus / 13 schematic / 6 hspice → digital-front (DC synthesis) dominant. ✓ shard A.
> messages: 174 msgs, 685837 B. agent=lead. 2026-11-06.

## User turns (verbatim, mode="act")

- **MSG#0** (intent / pure goal — A-faithful candidate task statement):
  `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/run_dc.sh`
  `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/synth.tcl`
  `/home/johnl/.cline/scripts/data/primelib_char_T_IsmTop/dc_addr_to_region/T_mBistTopNew.sdc`
  "这几个是在本机之前跑通过的dc脚本。后面带copy的是其他环境迁移过来的脚本 我现在要跑迁移过来的在本机，你需要帮我修改迁移过来的脚本以便能在本机运行，库要换一下"
  3 libs (absolute paths) + RTL `rtl/rowred_behavioral.restored.v`.
  "请进行修改 修改后diff 检查修改前后的必要性和准确性 然后跑dc ，你要在 /home/johnl/.cline/scripts/data/ 下单独建立一个工程目录并且 所有用到的文件复制到这个目录里 不能引用其他目录到文件你懂我意思吗"
- **MSG#66** (correction / gives fix direction → NOT usable as A-faithful task statement):
  "你要看原来脚本是怎么综合的 要提交到队列 fqueue3_analog"
- **MSG#119** (correction / gives fix direction):
  "你改一下综合检查 所有库里的都可以用"
- **MSG#172/173** (clarifying Q, no answer recorded): "你用的哪个dc版本"

## Assistant tool chain (82 tool calls)
read_files(orig "copy" scripts + working local scripts) → run_commands(locate dc_shell: `/apps/synopsys/SRB/designcompiler/O-2018.06-SP5-5/bin/dc_shell`; verify 3 libs + RTL exist; RTL top = `R_RowRed1024_full`; `eda-guard` NOT on this machine; port `rrp_SPPRWR` in copy's SDC does NOT exist in RTL) → editor(5 migrated files) → verify_diff.sh → check_regex.sh (caught self-introduced regexp grouping bug: dropped parens around `MET|VIOLATED` alternation → fixed to `slack \((MET|VIOLATED)\)\s+([-0-9.]+)`) → launch_bg.sh (local DC run) → MSG#66 → search_codebase(fqueue3/bsub) → discovered LSF + `fqueue3_analog` queue → rewrote run_dc.sh as bsub wrapper, added run_dc_local.sh → job 1837045 failed (LSF `res` crash: agent `LD_PRELOAD`/`LD_LIBRARY_PATH` injected newer libstdc++ than cluster glibc) → MSG#119 → relaxed cell policy: `get_lib_cells */*` (not `*`), `remove_from_collection ... [get_lib_cells gtech/*]`, ALLOWED_REFS = all lib cells + **logic_0**/**logic_1**, no set_dont_use → run_dc.sh: `env -u LD_PRELOAD -u LD_LIBRARY_PATH bsub ...` → job 1842691 → check_job → verify_result → final_summary → MSG#171 delivery summary.

## Golden result (what user accepted) = `dc_rowred_migrated/` project (self-contained, no external refs):
- `run_dc.sh`: bsub → `fqueue3_analog`, `env -u LD_PRELOAD -u LD_LIBRARY_PATH`, `-R "rusage[mem=8000]"`, `-W 08:00`, `-J rowred_dc`, calls `run_dc_local.sh` on compute node; QUEUE=`${LSF_QUEUE:-fqueue3_analog}`.
- `run_dc_local.sh` (NEW): `module load dc/2023.12-SP5_os7`, `dc_shell -no_gui -f synth.tcl | tee out/dc_console.log`, `test -s out/mapped.v`, prints `ROWRED_DC_LOCAL_DONE`.
- `synth.tcl`: RELATIVE paths (`rtl/rowred_behavioral.restored.v`, `libs/<3 dbs>`); 3 libs (LIB_GS/LIB_ROWRED/LIB_LVS); `get_lib_cells */*`; `remove_from_collection [get_lib_cells */*] [get_lib_cells gtech/*]`; ALLOWED_REFS = all lib cells (gtech excluded) + **logic_0**/**logic_1**; `remove_attribute dont_use/dont_touch` on lib cells (NO set_dont_use — all usable); NO hard count check (orig had 633/239/394); `set_max_delay 2.00` (orig 1.600); check_mapping vs ALLOWED_REFS; regexp `slack \((MET|VIOLATED)\)\s+([-0-9.]+)` (parens intact); TOP `R_RowRed1024_full`.
- `timing_constraints.tcl` (from T_mBistTopNew copy.sdc): `set_max_delay 2.00`; **SPPR/rrp_SPPRWR clock spec REMOVED** (port absent in RTL); only EF0/EF1/FS clocks; case_analysis on rrp_vcc_/rrp_vbp_=1, rrp_vss_/rrp_vbn_=0.
- `setup.sh` (NEW): copies RTL + 3 libs into project `rtl/`+`libs/` (absolute source paths only in setup.sh, not in run scripts).
- `MIGRATION_DIFF.txt`: documents all changes.
- DC run (job 1842691 on fqueue3_analog) completed: `out/mapped.v` generated, 158 usable lib cells (247−89 gtech), all timing paths met (1 setup endpoint 16ps over by design constraint), `ROWRED_DC_COMPLETE`.

## Case-build verdict: PARK (A-档 infeasible under §4.1/§4.2)

- The golden deliverable = **hand-migrated scripts with A-specific values hardcoded** (3 lib filenames, `fqueue3_analog` queue, `R_RowRed1024_full` top, `dc/2023.12-SP5_os7` module, SPPR removal).
- §4.1 requires hidden B (distinct input) and §4.2 requires check() to subprocess-run the candidate on B. The trace golden is NOT parameterized → it would FAIL a B-run (B has different libs/queue/RTL/top). So a faithful (A-档) case cannot satisfy the hidden-B cross-input guard.
- **Options for a future round**:
  1. **B-档 reformulation**: deliverable = a `migrate_dc.py`/`migrate_dc.sh` program taking `(orig_run_dc, orig_synth, orig_sdc, manifest.json)` → emits the 5 migrated scripts parameterized by the manifest. Hidden B = different orig scripts + manifest (different lib names/queue/top/absent-port). check() runs the candidate program on B. Golden program synthesized from this trace's migration logic. This is a strong L1 case but requires writing a real migration program + check.py (≥8 conds) + B + negatives — ~1 full round.
  2. Pick a different shard-A trace whose golden is naturally a parameterized program (fits hidden B directly).
- Parked, not abandoned: the migration logic (5 key changes: LSF bsub+env-strip, run_dc_local.sh module-load, */*  cell policy + gtech exclude, SPPR removal, relative paths) is fully captured here for the B-档 rebuild.

## Files fetched to .75 workdir (for future B-档 rebuild)
`golden/{run_dc.sh,run_dc_local.sh,synth.tcl,timing_constraints.tcl,setup.sh,MIGRATION_DIFF.txt}`,
`orig/{run_dc_copy.sh,synth_copy.tcl,T_mBistTopNew_copy.sdc}`,
`working/{run_dc.sh,synth.tcl,T_mBistTopNew.sdc}`,
`c5gwq.messages.json`, `deepread.txt`.
