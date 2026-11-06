# Deepread: 0kv56 — jascperc pattern-speed statistics (verification)

- **Trace**: jascperc @ hfeg0pkn001 (ip 10.129.2.10), session `1793172758983_0kv56.messages.json`, mc=160, keywords `verilog:3287;cadence:25`.
- **Size**: 1.77 MB, 462 msgs (242 user / 220 assistant). 2 real user_input turns (rest are tool_results).
- **Tool chain**: list_allowed_files×37, run_approved_command×58, editor×81, read_files×59 — agent explored dvprog trees, wrote `/home/jascperc/pattern_analysis.py` (651 lines, multiple iterative rewrites), produced `/home/jascperc/pattern_report/pattern_speed_report.{html,md}`.

## User intent (verbatim, A-faithful)
- **U#0 (msg 0)**: "分别对 .../PTE_20260624_1/dvprog/ 和 .../PTE_20260624/dvprog/ 两个路径下的 pattern 统计下验证了哪些 speed，每个 speed 多少支。pattern 的 speed 是 avc 文件的倒数第二个字段，比如 pattern_simulation_16Gb_LP6_Fix_10667_011.avc 的频率是 10667。按文件新建时间按周统计，每周多少只，给图例(折线/柱状)，周序号按实际 MCU 周。输出 html 和 md。对 avc 匹配的文件夹也要检索，文件夹里只有 irun.log 的排除，不算合法 pattern。"
- **U#2 (msg 346)**: refinement — "包含 A_Compare.txt、ncsim.shm 的是有效的 pattern 文件。把有效的按不同频率统计，按周统计，给图例，周序号按实际 MCU 周。"
- U#0 = clean A-faithful need (proposes goal + spec). U#2 gives validity criteria (treated as spec refinement, folded into B-track synthesis).

## Real accepted result
- `/home/jascperc/pattern_report/pattern_speed_report.md`: Total Valid=146, Total AVC=1152, Unique Speeds=1 (10667), Week Span=3 (W42/W43/W44-2026), Skipped: no_folder=6, only_irunlog=1000. Ref script `folder_valid` = lenient (folder has ≥1 non-irun.log non-hidden file) — this is the user-accepted rule. Report sections: Overview / Speed Overview / Weekly Summary / Per-Speed Weekly Breakdown / Skipped-Invalid.
- Real /rundata dirs are jascperc-host-owned; not extractable into sandbox (e0031982 on .75 cannot scp them; assistant accessed via run_approved_command as jascperc). ⇒ **B-track synthesized** (synthetic dvprog_A / hidden_B trees, same structure).

## Case decision: EDA-Eval-DesignFlow-PatStatSpeed-001
- domain=verification, track=B (synthesized; trace-faithful prompt), level=L1-static (pure-python analysis, no EDA tool).
- Deliverable: `pattern_analysis.py <dir1> <dir2> <output_dir>` → `pattern_speed_report.html` + `.md` + `stats.json` (machine-readable for robust grading).
- check.py: 17 conds (a-q); re-runs candidate on hidden_B, compares stats.json to independent gold analyzer. Anti-hardcode via A≠B (A: 33 valid/1 speed W43-45; B: 48 valid/4 speeds W38-42). Anti-stub (os.listdir/walk + split('_') + open/write). §4.9 three fakes + 3 negatives all FAIL; ref PASS.
- k_rationale = k_check = 17 ≥ 8 gate PASS.
