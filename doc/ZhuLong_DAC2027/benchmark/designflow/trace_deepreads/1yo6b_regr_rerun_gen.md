# 1yo6b — jkxu / DDR5 drcpa verilog regression rerun script generator

- session: `1792842218809_1yo6b` (jkxu / hfhds209 / mc173 / verilog:3738 dominant / a=3738 c=1792 b=0 n=37)
- 333 msgs / 1.66 MB / 17 user turns / Oct 24 19:43–20:25
- refined-A filter r424: top fresh strict-A (a>2c/b/n, a≥5, top_tool=verilog), new user jkxu
- shard A digital (verification regression rerun)

## User intent (A-faithful produce-task QUALIFIES — user gives requirement, not root cause / not implementation)

- U#1–4: 看正在 run 的 bsub jobs / job 目录在哪 / vsim_report 工作逻辑 + log.reg.1022 job 情况 / xrun.log `*E` = 错误 job (analysis / context-gathering)
- **U#5 (key produce-task)**: 「生成这些失败 case 的重跑脚本，可以参考 bin/vsim_report --genrerun 时的生成逻辑」— user asks to GENERATE rerun scripts for failed cases, referencing vsim_report --genrerun format. User does NOT give the implementation, only the requirement + a reference format to mimic.
- U#6–9: 修好了吗 / rerun 脚本的脚本是什么 / 怎么使用 / make_rerun.py 如何使用 (follow-up)
- **U#10 (enhance)**: 「不能指定目录路吗，然后检查 xrun.log 中是否有 *E 错误 以及 检查 A_Summary.rpt 中是否有 Failed Pattern > 0 在生成的 rerun 中区分下」— add `-d <dir>` arg + distinguish COMPILE_ERROR (*E) vs SIM_FAIL (Failed Pattern>0)
- U#11: 把 [COMPILE_ERROR] 和 [SIM_FAIL] 分两个段落，不用每条都单独加上去 (two sections, not per-line tags)
- U#12: 会统计正在进行的 job 吗 (add RUNNING count)
- U#14: 改成英文输出把 (English output)
- U#15: emoji 图标不显示 → 换 ASCII
- **U#16 (final)**: 「加 -rerun 才生成 rerun 脚本」— add `--rerun` flag (scan-only by default, generate only with flag)

## Agent work (deepseek-lead)

- read_files × ~15: vsim_report (genrerun logic), simulation.cfg, existing *_rerun files, log.reg.1022 tree
- run_approved_command × ~12: check_bsub_jobs.py (scan), python-runner (test make_rerun/gen_rerun)
- editor × ~25: iterative construction of gen_rerun.py (started as gen_rerun_scripts.py → make_rerun.py → gen_rerun.py final)
- key bugs fixed: double-quote nesting in -d/-b values (cfg read with quotes, script added another layer → `""x4""`), f-string editor replace issues, Chinese→English output, emoji→ASCII, add --rerun flag

## Final deliverable: /home/jkxu/gen_rerun.py (8847 bytes, 230 lines, pure stdlib)

**Interface**: `python3 gen_rerun.py [-d <log_dir>] [--rerun]` (or positional `<log_dir>`)

**Core functions**:
1. `read_cfg(cfg_path)` — parse `Word(short): value` lines → dict keyed by short
2. `build_cmd(cfg, case_name)` — build `./bin/vsim` command from cfg:
   - `--msierun --local` if '16Gb' in `-l` value, else `--cov`
   - `-sr -q -l -d -f -b -o -g` params, `-d`/`-b` single-quoted (strip nested `"`/`'`)
   - trailing ` & sleep 10s`
3. `classify_case(cdir)` — 5-state classification:
   - check xrun.log for `xrun: *E,` / `xmvlog: *E,` / `xmelab: *E,` / `xmSIM: *E,` → has_compile_err
   - A_Summary.rpt exists + `Failed Pattern : N` lines → if sum(N)>0: **SIM_FAIL** (precedence over *E); else COMPILE_ERROR if has_compile_err else PASS
   - rpt exists, no Failed Pattern line → COMPILE_ERROR if has_compile_err else INCOMPLETE
   - no rpt → COMPILE_ERROR if has_compile_err else RUNNING
   - **SIM_FAIL precedence**: case with both *E AND Failed Pattern>0 → SIM_FAIL (not COMPILE_ERROR)
4. `write_rerun(log_dir, cap, ttype, entries)` — write `{log_dir}/{cap}/{ttype}_rerun`:
   - header: `# Failed Simulation Commands for {ttype}` + timestamp + `# ====...`
   - module load: 16Gb → `module load  ds/xcelium/2023.09`; else → unload xcelium 2023.09 + incisive + load vmanager 22.03 + xcelium 22.03
   - Section 1: `# COMPILE_ERROR SIMULATIONS RERUN COMMANDS` + `# Total: N` + commands
   - Section 2: `# SIM_FAIL SIMULATIONS RERUN COMMANDS` + `# Total: N` + commands
   - chmod 755
5. `main()` — parse args (`-d`, `--rerun`, positional), scan `{log_dir}/{cap}/{ttype}/{case}/` tree, classify each case, accumulate stats per (cap,ttype), print stats table (Group|Total|PASS|FAIL|ERROR|Running|Incompl. + TOTAL row), if `--rerun` write rerun files for groups with failures

## Data formats (authentic from trace)

- **case dir**: `log.reg.1022/{16Gb|24Gb}/{Legacy|PRAC}/{case_name}.{bus}_{freq}/`
  - `xrun.log` (compile/elab/sim log, `*E,` = error)
  - `A_Summary.rpt` (sim result, `Failed Pattern : N` line)
  - `simulation.cfg` (`Simulation(sr): name`, `Queue(q): vbatch`, `Level(l): path`, `Define(d): ...`, `Freq(f): 8000`, `Bus(b): x4`, `Option(o): ...`, `Seed(g): ...`)
- **real error signatures**: `xrun: *E,ELBERR` (elaboration fail), `xrun: *E,PRENOP` (/tmp file gone), `xmvlog: *E,COFILX` (include file missing), `xrun: *E,VLGERR` (parse error)
- **real case names**: avl_ca_odt_1_cai=1_mir=1.x4_8000 (PASS), catm_three_deep_cai=x_mir=x.x4_8000 (ELBERR), csgeardown_crc.x4_8000 (COFILX), ecc_loop_2err_ecscomp.x4_8000 (SIM_FAIL), basic_allbank_bl16_cai=x_mir=x.x4_8000, basic_BurstOrderLengthType_...x4_8000 (INCOMPLETE)
- **vsim cmd format**: `./bin/vsim --msierun --local -sr avl_ca_odt_1_cai=1_mir=1 -q vbatch -l 16Gb/Legacy -d "DDR5_x16" -f 8000 -b "x4" -o ... -g 12345 & sleep 10s`

## Synthesis plan → RegrRerunScriptGen-001 (digital L2, A档 trace-faithful)

- **deliverable**: `gen_rerun.py` (pure stdlib, the agent's actual code, parameterized via `-d` so not bound to /rundata)
- **A inputs** (visible): small log_tree_A/ (16Gb/Legacy 4 cases: PASS/COMPILE_ERROR/SIM_FAIL/INCOMPLETE; 24Gb/PRAC 3 cases: PASS/COMPILE_ERROR/RUNNING)
- **B inputs** (hidden): log_tree_B/ with different case names + edge cases:
  - 16Gb/Legacy 6 cases (incl. csgeardown_crc-equivalent with BOTH *E AND Failed Pattern>0 → SIM_FAIL precedence; INCOMPLETE; RUNNING)
  - 24Gb/Legacy 4 cases (incl. RUNNING)
  - 24Gb/PRAC 3 cases
  - 16Gb/PRAC 1 PASS case → no rerun file generated (group with no failures)
- **check.py** (~15 conditions): run `gen_rerun.py -d <B> --rerun`, parse stats stdout + rerun files, assert:
  a. exit 0; b. 3 rerun files exist (16Gb/Legacy, 24Gb/Legacy, 24Gb/PRAC); c. 16Gb/PRAC_rerun does NOT exist (no-failure group); d. stats TOTAL row correct; e. per-group 16Gb/Legacy stats; f. per-group 24Gb/Legacy stats; g. COMPILE_ERROR section count; h. SIM_FAIL section count; i. **SIM_FAIL precedence** (csgeardown-equiv in SIM_FAIL not COMPILE_ERROR); j. 16Gb cmds start `--msierun --local`; k. 24Gb cmds start `--cov`; l. cmds end `& sleep 10s`; m. -sr matches cfg; n. -b single-quoted; o. 16Gb module-load header; p. 24Gb module-load header; q. 3 random dir-order shuffles → rerun command SET stable
- **negatives**: naive_empty (exit≠0/no output), print_only (stats but no files), core_removed (drop SIM_FAIL precedence → fails i + h count), hardcoded_A (hardcode A case names → fails on B)
- **k_rationale = k_check = 17** (≥8 ✓)
- **TFC**: A档 (deliverable = agent's actual gen_rerun.py, trace-faithful by construction) — TFC not applicable

## Decision: A档 (not B档)

User U#5 explicitly asks to produce a rerun-script generator (deliverable), and the agent actually built `gen_rerun.py`. The deliverable is the agent's real output, parameterized via `-d` so it works on any log tree (not bound to /rundata). A-faithful produce-task = the deliverable comes from the trace's actual agent work. No synthesis needed (B档 would be if user only asked Q&A and we synthesized a deliverable).
