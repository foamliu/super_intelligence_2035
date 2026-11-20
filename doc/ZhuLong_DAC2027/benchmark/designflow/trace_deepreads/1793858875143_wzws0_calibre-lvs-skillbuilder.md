# wzws0 deepread — adaml calibre-lvs skill-builder multi-task session (REJECT)

- session: `1793858875143_wzws0` (adaml@hfeg0pkn002, 10.129.2.11)
- scan: summary.tsv 20261109_224902 — **mc=2/3/4 (match_count col)**, NOT 5542
  - ledger mc=5542 was a **misread of the keywords column** (lvs:7477;calibre:4445;...)
  - real match_count well below mc≥30 threshold; found via fresh-trace-log top80 NEW, not standard filter
- meta: started 2026-11-05 06:07, ended 2026-11-06 07:26, status=completed, exit_code=0
  - terminal_marker = `failed_external_process_exit` (stale_session_reconciler)
  - model deepseek-v4-flash, cwd /ai_sandbox/m2701/V0_DDR4/agentdir/adaml
- files: .json 17KB / messages.json 8.3KB (tail compaction) / **messages.archive.json 4.2MB (990 msgs in 4 chunks)**

## Why REJECT (5 reasons)

1. **adaml = AVOID_USER (confirmed)** — skill-builder who iterates a "calibre-lvs" skill across many
   cells; sessions are long multi-task skill-building, NOT clean single produce-tasks.
2. **990-message multi-task session** — interleaves: CDL extract (blcnand3GFx1) / LVS run
   (bufGSx64_RasToXdec, bufGFLx24) / skill optimize / how-to Q&A / manual research / /compact.
   No single clean produce-task with one accepted gold (§A rule 4 fail).
3. **§A rule 2 fail** — many user rounds give root-cause/fix (U#122 CIW log, U#191 netlist-export
   docs, U#366 "lesson learn optimize skill") not clean 提出需求 rounds.
4. **Gold dilution** — the calibre-lvs skill is FULLY documented in the prompt's
   `<skill_instructions>` block (runset, env, LSF, known traps, run_lvs.py reference impl).
   The "answer" is handed to the agent in the prompt → not 20-30% difficulty target.
5. **Non-portable gold** — produce-tasks (CDL/LVS on specific cells) depend on m2701 OA library
   on .75 (/proj/m2701/V0_DDR4/...); assets would need the actual GDS/CDL/cell data, not portable.

## User turn progression (U# = user_input rounds, skill_instructions stripped)

- U#0:  blcnand3GFx1 抽cdl，用EDA工具不要用脚本 (original — CDL extract produce-task)
- U#122: paste CIW log (root-cause for CDL extraction)
- U#160: 我们目前没有办法通过ciw访问SI吗？ (how-to Q&A)
- U#191: paste netlist-export docs (context)
- U#240: 根据上面的对话，帮我优化skill，打通全链条 (skill-building)
- U#254: Accept
- U#281: 介绍一下我这个lvs的skill (Q&A)
- U#283: bufGSx64_RasToXdec 帮我做lvs (DIFFERENT cell, produce-task)
- U#366: lvs流程问题作为lesson learn沉淀优化skill (skill-building)
- U#370: 接受修改
- U#434: bufGFLx24 做lvs，对比标准lvs结果 (DIFFERENT cell)
- U#559: 深度思考优化lvs skill (skill-building)
- U#578: [optimizer] read calibre manual, give optimization plan (skill-building)
- U#879: 不用了，到此为止 (stop)
- U#881: bufGSx64_RasToXdec 这个cell做lvs (repeat)
- U#920: calibre lvs 4模式(Hier/Flat/CB/Autowaiver)查询手册记录进skill (research→skill)

## Trace末尾 (compaction summary)
bufGSx64_RasToXdec LVS CORRECT (8 ports/9 nets, job 1857977) + calibre-lvs skill 1.6.0→1.7.0
(4-mode research written). This is the LAST task, NOT the original blcnand3GFx1 CDL task →
gold mismatch confirms multi-task nature.

## Verdict
REJECT / parked. adaml AVOID confirmed. Do NOT re-pick wzws0 or adaml sessions.
