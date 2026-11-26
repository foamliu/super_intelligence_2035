# Deepread: 1791797822968_mxaca — Aether Pin-Error QA-KB Extraction

## Trace Meta
- **session_file**: `1791797822968_mxaca`
- **user**: lizwen
- **host**: 10.129.2.12 (hfeg0plg76)
- **match_count**: 42 (mc≥10 pool, snapshot 2026-11-18)
- **domain**: layout_aether
- **shard**: C
- **case_id**: EDA-Eval-DesignFlow-AetherPinErrorQa-001
- **round**: r743

## User Intent (U#0 verbatim)
> 启用aether-tool-qa skill,aether-tool-qa 打pin报错

Single clean debug-Q&A intent: user activates the aether-tool-qa skill and reports a pin-creation error ("打pin报错"). User gives no root cause or fix → valid A档 (select "提出需求/表达目标" user turn).

## Trace Summary
- 20 messages: 11 user / 9 assistant
- U#0 is the only real user-text turn (subsequent turns are tool_result echoes / approval)
- assistant searches the Aether tool-qa knowledge base (`/home/lizwen/.cline/skills/aether-tool-qa/references/aether_tool_qa.md`, 5188 lines, 455 QA blocks) via skill RAG
- assistant classifies pin errors into 6 categories (msg 19):
  1. scalar net `xxx<>` already exists → delete net in navigator
  2. bus net with base name `xxx` already exists → find and rename
  3. same-name pin direction mismatch → change pin Type
  4. Layer xxx is invisible (generate select) → select pin layer in lsw first
  5. alt+f / ctrl+3 flypin
  6. ctrl+p create pin normal flow

## Reframe: ③evidence-only mock-stdlib
- **Why reframe**: Real Aether tool-qa KB is path-dependent (needs live Aether + license + skill KB on .75). Reframe as ③evidence-only mock-stdlib: SUT reads a fixed `aether_tool_qa.md` excerpt (curated from real KB), extracts pin-error-related Q&A facts to structured JSON report with evidence (source doc + exact line).
- **P-006 r618 (C)-(A) split**: analysis-Q&A on fixed artifact (no process to re-run on B) → SUT produces report only; B/B2 serve as judge-self-check (check.py independently re-derives gold).
- **Reframe class**: `③evidence-only(mock-behavioral,debug-Q&A)`

## Asset A Composition
- Curated excerpt of real `aether_tool_qa.md` (455 QA blocks total):
  - ALL 45 pin-mentioning blocks (containing "pin" keyword, excluding false positives like "mapping")
  - Every 7th distractor block (35 blocks, non-pin topics: deselect all, align, nomachine, crash, etc.)
  - Total: 80 blocks, 1244 lines, ~16308 chars UTF-8
- Format: `## 提问` / `**回复：**` / `---` block separators

## Hidden B Design
- Mock Aether tool-qa KB (20 QA blocks, 10 pin-related)
- **Primary pin error**: bus_net_exists (vs A's scalar_net primary)
- **Different bindkeys**: ctrl+r (create pin), ctrl+f2/alt+f (fly pin), ctrl+l (pin list), shift+m (move pin) — vs A's ctrl+p/ctrl 3/alt+f/ctrl 1/win+m
- **Different fix wording** for all 6 facts (layer_invisible, scalar_net, bus_net, direction_mismatch, create_pin, fly_pin)
- **pin_qa_count**: 10 (vs A's 39)

## Hidden B2 Design (cross-input guard)
- Minimal mock KB (8 QA blocks, 4 pin-related)
- **Bindkeys**: ctrl+q (create pin), ctrl+g (fly pin) — disjoint from both A and B
- **Null facts**: scalar_net_fix and direction_mismatch_fix are null (B2 has no such blocks) — anti-hardcode: A and B both have non-null
- **pin_qa_count**: 4

## Extraction Schema (9 top-level keys)
```
pin_qa_count          : int (count of pin-related QA blocks)
pin_bindkeys          : sorted list of unique bindkeys in pin blocks
layer_invisible_cause : exact line from KB (or null)
scalar_net_fix        : exact line from KB (or null)
bus_net_fix           : exact line from KB (or null)
direction_mismatch_fix: exact line from KB (or null)
create_pin_bindkey    : exact line from KB (or null)
fly_pin_bindkey       : exact line from KB (or null)
evidence              : per-fact {doc, line} map
```

## Anti-Hardcode Verification
- A pin_qa_count=39, B=10, B2=4 → all differ ✓
- A pin_bindkeys={alt+f,ctrl 1,ctrl 3,ctrl+alt,ctrl+d,ctrl+n,ctrl+p,ctrl+w,shift+ctrl,shift+q,win+m,win+x} (12 keys)
- B pin_bindkeys={alt+f,ctrl+f2,ctrl+l,ctrl+r,shift+m} (5 keys, only alt+f overlaps with A)
- B2 pin_bindkeys={ctrl+g,ctrl+q} (2 keys, disjoint from both A and B)
- All 6 fix/cause lines differ across A/B/B2 ✓
- B2 has 2 null facts (scalar_net, direction) that A/B have non-null ✓

## check.py: 16 Assertions (a-p)
- a) zip valid, solve.py extracted
- b) B non-empty JSON report
- c) B has all 9 required top-level keys
- d) B pin_qa_count == 10 (NOT A's 39)
- e) B pin_bindkeys set == B truth (NOT A's 12-key set)
- f) B layer_invisible_cause == B truth (NOT A's M1.text line)
- g) B scalar_net_fix == B truth (NOT A's navigator line)
- h) B bus_net_fix == B truth (NOT A's 找到改掉 line)
- i) B direction_mismatch_fix == B truth (NOT A's 更改pin Type line)
- j) B create_pin_bindkey == B truth ctrl+r (NOT A's ctrl+p)
- k) B fly_pin_bindkey == B truth ctrl+f2 (NOT A's alt+f/ctrl 3)
- l) B evidence: all entries cite real lines in B's KB
- m) B2 cross-input guard (pin_qa_count=4, ctrl+q, ctrl+g, bindkey set)
- n) B2 evidence: all entries cite real lines in B2's KB
- o) B2 null-field guard (scalar_net_fix and direction_mismatch_fix are null)
- p) anti-stub + determinism (empty dir → all-None; B 3 reruns byte-identical)

## Self-Verify Results
- reference solve.py: **16/16 PASS** ✓
- 3 negatives all FAIL distinct:
  - solve_empty → 15 FAIL (a passes, b-p blocked)
  - solve_print_gold → 13 FAIL (d-k content wrong, l/n evidence fake, m B2 wrong)
  - solve_no_evidence → 10 FAIL (l/n evidence missing, plus content missing)
- Determinism: B 3 reruns byte-identical ✓

## Distinctness vs r741 AetherRepeatCopyHowto
- r741: ref-manual + cheatsheet doc-extraction (official Aether reference docs, .txt format, howto-Q&A)
- r743: community Q&A knowledge base extraction (群问答KB, .md format, debug-Q&A, `## 提问`/`**回复：**` block parsing)
- Different source format, different question type (howto vs debug), different extraction logic (chapter/bindkey/Tcl params vs error-categories/fix-lines/bindkey-collection)

## Discipline
- SUT sandbox contains only sample_input/docs + prompt.txt + task_brief.md
- hidden/ + reference/ do NOT enter SUT ✓
- No masking (user=lizwen, host=10.129.2.12, session_file=1791797822968_mxaca — real values) ✓
- Only C shard files modified ✓
- check.py hidden path resolution via workdir/hidden/{b,b2}/docs (NOT __file__ dir) ✓
