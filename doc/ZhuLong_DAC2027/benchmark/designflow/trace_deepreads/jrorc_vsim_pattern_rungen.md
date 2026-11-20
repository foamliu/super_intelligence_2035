# Deepread: jrorc (jkxu) — DDR5 vsim pattern + run-script generator

**Session**: 1794651030659_jrorc.messages.json
**User**: jkxu | **Host**: 10.129.2.12 (hfeg0pkn003) | **mc**: 85 | **Domain**: verification
**Layout**: subdir (sessions/<sid>/<sid>.messages.json), 388KB, ALIVE
**Msgs**: 148 total, 68 tool_use, 9 real user inputs

## Real user inputs (trace-faithful)

- **R0** (MSG 0): "gen_pattern_files.py 这个脚本review 下" — review existing script
- **R1** (MSG 7): "生成的及run 脚本按照这种格式输出吧" — **PRODUCE-TASK**: generate run scripts in vsim format. Pasted 18 vsim command examples: `vsim --msierun --local -sr tm_priority2 -q vbatch_drcoa -l TM_CHECK/P2 -d "POST USESDFX   SHORTSIM USETF" -f 9200 -b "x16" -o +cm0_fc_PowerDownEn & sleep 10s`
- **R2** (MSG 69): more format examples (tm_priority3, sverilog queue), "直接这样平铺就好，不用很复杂加option传入"
- **R3** (MSG 102): "POST USESDFX   SHORTSIM USETF 这个换成 POST USESDFX USETF" — remove SHORTSIM
- **R4** (MSG 106): "改成这种格式" — use variables: `date="TM_CHECK/P3"`, `queue=vbatch_drcoa`, `frequency=9200`, then `vsim ... -q ${queue} -l ${date} -d "POST USESDFX USETF" -f ${frequency} ...`
- **R5** (MSG 116/118): paste SystemVerilog task code (tmrandload/tmload) for analysis — "分析下"
- **R6** (MSG 120/122): "with比较大的时候是不是循环次数太多来" / "哪里和width关联起来的" — analysis Q&A
- **R7** (MSG 124): "run_random 这个改成shell 脚本" — convert to shell script

## Agent work

- Reads gen_pattern_files.py (original), cm1.list, test.run, run_script_gen
- Iteratively rewrites gen_pattern_files.py (20+ editor calls, MSG 20-90)
- Key functions:
  1. `parse_and_count(lines)`: dedup signal names, count bit widths (handles `<N>` suffix or `name width` pairs)
  2. `gen_test_run(blocks, path)`: generates SV `if ($test$plusargs("sig")) begin tmload(.tm("sig"), .width(W)); end` blocks
  3. `gen_run_script(blocks, path)`: generates bash script with vsim commands, one per signal, using variables
- MSG 103: fix SHORTSIM → remove (format: `-d "POST USESDFX USETF"`)
- MSG 107: rewrite gen_run_script with variables (date/queue/frequency)
- MSG 125-145: create run_random.sh (random load test, for loop with vsim)

## Deliverable (produce-task)

**gen_pattern_files.py**: Python script that:
1. Reads a signal name list file (one signal per line, optional width: `name` or `name width`)
2. Deduplicates and counts bit widths
3. Generates **test.run**: SystemVerilog plusargs blocks (`if ($test$plusargs("sig")) begin tmload(.tm("sig"), .width(W)); end`)
4. Generates **run script**: bash script with vsim commands using variables, one per signal:
   ```
   #!/bin/bash
   module load ds/xcelium/2023.09
   date="TM_CHECK/P3"
   queue=vbatch_drcoa
   frequency=9200
   /proj/.../vsim --msierun --local -sr tm_priority3 -q ${queue} -l ${date} -d "POST USESDFX USETF" -f ${frequency} -b "x16" -o +sig & sleep 10s
   ```

## Case design

- **archetype**: ddr5-verification-pattern-runscript-generator
- **A档** (trace-faithful): real DDR5 signal names + real vsim format from jkxu's session
- **L1** (offline Python)
- Visible A: signals_A.txt (12 signals) + task_brief.md (format spec from R4)
- Hidden B: signals_B.txt (10 different signals, different widths) + hidden_manifest.json
- Reference: gen_pattern_files.py (generalized, count-agnostic)
- check.py: ≥8 assertions (zip valid, test.run structure, plusargs count/names/widths, run script format/variables/no-SHORTSIM, determinism, non-hardcoded)
