# Deepread: h5wfp — weizhao — DRC close/open layer swap

- session: 1790564208899_h5wfp
- user: weizhao @ hfeg0pkn004
- mc=42, score=342 (layout-affinity sort, r330)
- domain: physical_verify (calibreDRC.rule manipulation)
- status: completed, exit_code=0, model=glm-5.2
- started: 2026-09-28T02:56:48Z, ended: 2026-10-14T21:33:00Z
- A档 faithful: YES

## User turns (verbatim)

### U#0 (msg 0)
帮我写一个脚本 用于替换calibreDRC.rule中关于 LAYER MAP定义中的 XXX_close XXX_open
案例为
LAYER   MAP   88   DATATYPE   16     8516
LAYER   M1_CLOSE                     8516
LAYER   MAP   88   DATATYPE   17     8517
LAYER   M1_open                      8517变更为
LAYER   MAP   88   DATATYPE   16     8516
LAYER   M1_CLOSE                     8517
LAYER   MAP   88   DATATYPE   17     8517
LAYER   M1_open                      8516

### U#1 (msg 1) — THE TASK (with reference file)
(same as U#0 plus:)
参考文件
/apps/imctf/runset/calibre/cxmtG5_CIP/current/drcoa/G5_CIP_package_drcoa_v0d5_Rev07/calibreDRC.rule

## Assistant tool chain (54 steps)
- run_commands (grep for CLOSE/open in calibreDRC.rule) — failed (shell disabled)
- search_codebase, list_allowed_files — timeouts
- read_files (batched, lines 1-100, 100-700, 700-900, 900-1100, 1100-1300, 1178-1230, 1380-1620, 1460-1545) — found 11 CLOSE/open pairs: CT/M1/V1/V2/M3/M2/V3/M4/M5 etc
- editor: swap_close_open.py (main script, ~150 lines)
- editor: test_input.rule, test_expected.rule, test_swap_close_open.py
- Final deliverable: /home/weizhao/.cline/scripts/data/swap_close_open.py

## Deliverable interface (swap_close_open.py)
- CLI: `python3 swap_close_open.py <input.rule> [output.rule] [--in-place] [--dry-run]`
- Regex: `^(LAYER\s+)(\S+?)_((?:CLOSE)|(?:open))(\s+)(\d+)\s*$` (IGNORECASE)
- Swaps trailing internal layer number between matched XXX_CLOSE / XXX_open pairs
- LAYER MAP lines unchanged; only LAYER <name> <num> lines modified
- Exit: 0=success, 1=error (file not found), 2=no pairs found
- Warns on duplicates and unmatched close/open

## Case synthesis plan (r330)
- A (visible): calibreDRC.rule excerpt with 5-6 CLOSE/open pairs (synthetic numbers, NOT real 8487/8488 etc)
- prompt: U#1 verbatim (with masked ref path → use synthetic path)
- B1/B2/B3 (hidden): 3 different rule files, different pair counts (3, 5, edge cases)
  - B1: 3 pairs, standard
  - B2: 5 pairs, mixed casing (CLOSE/open, close/OPEN)
  - B3: edge — 1 pair + 1 unmatched CLOSE (warning, skip) + non-CLOSE layer lines
- check.py: ≥8 conditions, runs candidate script on all 3 B pairs
- negatives: script that doesn't swap, script that swaps MAP lines too, script that hardcodes
- §4.9 fakes: empty submit, wrong-format submit, non-executable
