# Deepread — sid_1788918895118_cp5wk (xinqiaoz / hfeg0plg76, mc=364, physical_verify)

## trace source
- host: hfeg0plg76, user: xinqiaoz, session_file: 1788918895118_cp5wk.messages.json
- match_count: 364 (tools field: "72 calibre")
- cwd: /home/xinqiaoz/PDK_QA/pdkQaSystem
- model: glm-5.2, status: failed (stale_session_reconciler), 156 msgs
- real task: maintain pdkQaSystem (a PDK QA system that drives calibre DRC) — clean Windows residuals + expired Phase refs from migration docs, migrate 3 rules to Linux, git commit

## user turns (verbatim intent, A-档 candidate selection)
1. msg0: "请回答以下 3 个问题：pdkQaSystem 项目的代码分哪三层？你与用户对话应该用什么语言？DRC/__init__.py 导入链有什么常见陷阱？" — Q&A, no deliverable → not design_flow
2. msg2: "project-conventions.md（项目级全局指令）中有大量 Windows 残留和过期的 Phase 引用，需要逐一清理。" — **goal-proposing, no root-cause/fix given** → A-档 eligible
3. msg37: "project-conventions.md 已清理完成。但其他迁移文件中仍带有 Windows 残留或不合理的内容，需要全面检查和清理。" — continuation, depends on prior state
4. msg131: "现在补充 3 条尚未迁移的规则到 rules/ 目录。Windows AI 已提供了原始内容，你需要为 Linux 环境做适配后安装。" — goal + references external content ("Windows AI 已提供")
5. msg144: "git commit this round of modification." — ops, not a produce task

## selected angle (B-档 synthesized, L1)
- A-档 turn2 verbatim is about a generic .md cleanup — weak EDA specificity. Promote to B-档: adapt the real intent (Windows residual + expired Phase cleanup of a PDK-QA artifact) to a **calibre DRC rule deck (SVRF)**, which is the actual physical_verify artifact the pdkQaSystem drives.
- Deliverable: a Python cleaner that takes an SVRF deck, removes Windows drive paths / backslash separators / .bat wrapper invocations / PowerShell $env: vars / expired Phase N: markers, preserves 3-layer architecture + SVRF command count, and emits a structured cleanup report JSON.
- L1 (offline static text processing, no calibre run). Matches shard C established L1 pattern (parse EDA artifacts offline).

## gold (what cleaning rules the ref solution implements)
1. Windows drive paths `[A-Z]:\` → `/` (strip drive letter + leading backslash)
2. Backslash path separators inside quoted strings → `/`
3. `.bat` wrapper invocation lines → removed entirely
4. PowerShell `$env:VAR` → `$VAR`
5. Expired `Phase N:` markers → strip the `Phase N:` prefix (keep category text)
6. Preserve: 3-layer comments (Input/Rule/Report Layer), SVRF command count (LAYOUT PATH/PRIMARY/SYSTEM/ERROR FORMAT, DRC WIDTH/SPACING/AREA/DENSITY/RESULTS/SUMMARY/MAXIMUM, INCLUDE)

## 12-assertion spec (k=12, maps to check.py labels a-l)
- a: zip exactly 1 file (clean_deck.py) + py_compile
- b: run on hidden B → exit0 + writes cleaned_deck.svrf + cleanup_report.json + stdout JSON valid + top-level keys present
- c: cleaned B has no `[A-Z]:\` drive paths
- d: cleaned B has no backslash inside quoted paths
- e: cleaned B has no `.bat`
- f: cleaned B has no `$env:`
- g: cleaned B has no `Phase [0-9]` markers
- h: cleaned B preserves 3-layer comments (Input Layer / Rule Layer / Report Layer)
- i: cleaned B SVRF command count == raw B SVRF command count (independent re-derive)
- j: report B windows_paths_removed count == raw B `[A-Z]:\` occurrence count (independent re-derive, ±0)
- k: report B phase_markers_updated count == raw B `Phase [0-9]` count (independent) + determinism (3× md5 of cleaned B + report identical)
- l: cross-input B2 (drives G:/H:, Phase 6/7, different SVRF cmd set) → exit0 + no drive paths + no Phase + SVRF count preserved (defeats hardcoding A)

## candidate filtering record
- awk on .75 summary.tsv (mc≥100, shard-C tools filter, 169 excluded) → top: cp5wk mc=364 (xinqiaoz, calibre), 5e6p2 mc=359 (xinqiaoz, calibre+schematic). Both are xinqiaoz pdkQaSystem. Picked cp5wk (highest mc). 5e6p2 same project/user → parked for diversity.
