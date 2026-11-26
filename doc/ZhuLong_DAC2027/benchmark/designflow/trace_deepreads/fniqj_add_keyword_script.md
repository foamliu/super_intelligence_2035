# Deepread: 1789975587201_fniqj — add_keyword.py file-insertion utility

**trace**: 1789975587201_fniqj (alanji @ hfeg0pjn100, mc36, digital)
**date**: 2026-11-15 (r571 fresh-deepread)
**size**: 366KB / 74 msgs / agent=lead

## User intent (原话)

- **U#0 (msg[0])**: `write a python script handle the file to add the a key word`
- **U#1 (msg[4], via ask_question answer)**: "Add/insert a keyword at a specific position in a text file (e.g., after line 10, or at a marker)"
- **U#2 (msg[6], via ask_question answer)**: "Add a keyword after a specific line number (e.g., after line 10)"
- **U#3 (msg[56])**: `分析这两版网表的差异` (netlist diff analysis — second task, not produce-task)

**First-turn = produce-task**: user asked to write a Python script that inserts a keyword at a specific position in a text file. Agent delivered `add_keyword.py` (8389 bytes) through interactive requirement clarification (ask_question x2) + 6 editor iterations.

## Agent deliverable

**File**: `/home/alanji/.cline/scripts/data/add_keyword.py` (writableRoots constraint, not ~/python/)

**Script capabilities** (6 insertion modes + error handling):
1. `--after-line N`: insert after line N (1-based)
2. `--before-line N`: insert before line N (1-based)
3. `--after-marker TEXT`: insert after first line containing TEXT
4. `--before-marker TEXT`: insert before first line containing TEXT
5. `--at-start`: insert at beginning of file
6. `--at-end`: insert at end of file
7. `--in-place`: modify original file
8. `--output PATH`: write to specified path (else stdout preview)
9. Error: out-of-range line → exit 1 + stderr message
10. Error: marker not found → exit 1 + stderr message
11. Error: no position specified → exit 1 + stderr message

**CLI**: `python add_keyword.py <input_file> --keyword "..." [--after-line N | --before-line N | --after-marker TEXT | --before-marker TEXT | --at-start | --at-end] [--in-place | --output PATH]`

**Tool calls**: list_allowed_files=12, read_files=14, editor=6, ask_question=2, search_codebase=2, SandBox_MCP_Server__run_code=1 (failed: connection refused), run_commands=1 (disabled by policy)

## B档合成计划

**Capability**: file keyword insertion utility (6 position modes + 3 error modes)
**A档不可行**: agent went through interactive clarification (ask_question x2) — the A prompt alone doesn't specify the full requirements; B档 = synthesize the full spec from the clarified requirements + the delivered script.

**A (visible to SUT)**:
- Task prompt: user's request + clarified requirements (insert keyword at specific position, support after-line/before-line/after-marker/before-marker/at-start/at-end, CLI with argparse)
- Example A: input_A.v (small verilog file) + expected_A_after_line.txt (keyword inserted after line 5)

**B (hidden, not in SUT sandbox)**:
- input_B1.sv: different verilog content, 20+ lines
- input_B2.txt: text file with markers
- input_B3.v: empty-ish edge case file
- hidden_manifest.json: maps test cases to B files + insertion params + expected outputs

**check() assertions (14)**:
① zip contains add_keyword.py
② add_keyword.py py_compile passes
③ --after-line N on B1: keyword at correct position, all original lines preserved
④ --before-line N on B1: keyword at correct position
⑤ --after-marker on B2: keyword after first matching line
⑥ --before-marker on B2: keyword before first matching line
⑦ --at-start on B1: keyword at line 1
⑧ --at-end on B1: keyword at last line
⑨ --output writes to file (not stdout), file content correct
⑩ --in-place modifies original file
⑪ out-of-range --after-line (line > total): exit code 1
⑫ marker-not-found --after-marker: exit code 1
⑬ no-position-specified: exit code 1
⑭ keyword inserted exactly once (count == 1 in output)

**Negatives (4)**: naive_empty (empty script → FAIL ③), print_expected (just prints expected output → FAIL ③/⑨), core_deleted (insertion logic removed → FAIL ③), hardcoded_A (hardcodes A expected output → FAIL ③ on B)

## Viability

- ✅ Single-focused capability (type a): one script, one purpose (file keyword insertion)
- ✅ Self-contained: no private file dependencies (synthesized A/B files)
- ✅ check() has teeth: 14 independent assertions, 3 error-mode assertions, hidden B prevents hardcoding
- ✅ Real trace: user原话 + agent delivered working script (verified on .75)
- ✅ No duplicate: grep A.jsonl for keyword/addkey/fileinsert/insertline = 0 hits
