# Deep-read: 1783650805189_y20nc — Virtuoso AutoVia merge + cellview preservation audit

- **session**: `1783650805189_y20nc.messages.json` (e0014566 @ hfeg0plg98, mc=201)
- **size**: 564 KB, 195 messages, 4 user turns (deepseek-v4-?)
- **domain**: layout_virtuoso (Virtuoso SKILL + dbOpenCellViewByType + dbCopyCellView)
- **tools hits**: virtuoso 48 / cellview 36 / dbCreateInst 24 / calibre 21 / schematic / spectre

## User intent (verbatim, A-档-eligible seed)

- USER#1 (idx 0): `read the prompt_autovia.md and do the job in it.`
- USER#2 (idx 38): `你看看layout_austin7 这个，就是我手动将layout_austin6 复制了一份，然后手动将你生成的auto via cell 加了进去。我希望你merge得到的layout就是这样的。你比较下你生成的新的layout, 跟这个有什么 区别`  ← **核心意图：比较 merged 与 manual reference 的差异**
- USER#3 (idx 46): `yes`
- USER#4 (idx 188): `很好，你修改过后的逻辑中碰到目标路径已经存在，怎么办？`  ← **dbCopyCellView 目标已存在处理**

## Real task & assistant tool chain

User runs the `virtuoso-autovia-runner` skill (gen_autovia_agent.py + run_autovia_nogui.il)
to generate via cells and merge them into a copy of `austin/layout_austin6` →
`austin/layout_austin6_autovia` via `dbCopyCellView`. Then asks the assistant to compare
the auto-merged layout against a hand-built reference `layout_austin7`.

Assistant's SKILL probe chain (SandBox_MCP_Server run_code, lang=skill):
1. `CompareLayouts(lib1,cell1,lib2,cell2)` — `dbOpenCellViewByType` both, compare
   `~>instances` names, `~>shapes`, report onlyIn1/onlyIn2/common.
2. `CompareShapes(lib1,cell1,lib2,cell2)` — per-lpp shape diff.
3. `CheckTextDisplays()` — open `layout_austin6` (source) vs `layout_austin6_autovia`
   (merged), enumerate `~>shapes` where `objType=="textDisplay"`, compare
   `bBox/lpp/label/parentType`. **Finding: textDisplays LOST in merged.**
4. `CheckMergedPins()` — enumerate pin shapes (`lpp` cadr `"pin"`), check pin→net
   assignment. **Finding: pin shapes / pin-net lost in merged.**
5. `dbCopyCellView` API probing (isCallable / getFnArgs / TestDbCopyCellView /
   TestOverwrite / TestPurgeAndCopy / TestDdPurge / TestVMCache) — discovers
   `dbCopyCellView` fails / silently no-ops when destination already in VM cache
   (DB-170007 "already in VM"), and that textDisplays + pins are NOT preserved by a
   plain copy → must recreate textDisplays (`dbCreateTextDisplay`) and reassign
   pin→net (`dbAddFigToNet`) after the copy.
6. Edits `run_autovia_nogui.il` (editor) to add: purge-destination-before-copy guard +
   textDisplay/pin recreate block; re-runs the agent; re-compares → merged now matches
   `layout_austin7`.

## Orthogonal sub-theme taken for the case

NOT the AutoVia generation itself (already covered by AutoViaLayoutMerge-001 /
AutoViaNameGen-001 / AutoViaPwrFillRemove-001 / AutoViaGen-001). The orthogonal sub-task
is the **cellview-preservation auditor**: given two structural cellview dumps (source +
merged), report whether `textDisplays` / `pins` / `instances` / `nets` were preserved
during the `dbCopyCellView` merge, and emit a PASS/FAIL verdict. This is exactly what
`CheckTextDisplays` + `CheckMergedPins` + `CompareLayouts` compute in SKILL, but here
done offline on a JSON structural bundle (no live Virtuoso, consistent with r148/r150
L1-boundary cadence; .75 Aether/Virtuoso probe not used).

## Gold / case shape

- A (visible): `austin/layout_austin5` → `layout_austin5_autovia`, clean merge (PASS,
  4 tds/pins preserved, +3 vias).
- B1 (hidden, FAIL, mirrors trace finding): `austin/layout_austin6` →
  `layout_austin6_autovia`, **2 textDisplays lost (CLK, RST)** + **1 pin lost (CLK)**,
  +3 vias → `VERDICT: FAIL`.
- B2 (hidden, PASS, cross-input guard): `rfLib/rf_amp` → `rf_amp_merged`, all preserved,
  +2 vias, disjoint tokens (no austin/CLK/RST).
- B3 (malformed): missing `merged` → exit 1 + stderr + no output.

Reference solver `audit_cv_preserve_ref.py` keys textDisplays by `(label,lpp)`, pins by
`(net,lpp)`, instances by `name`; renders Markdown with Shape counts table (TOTAL row +
by-lpp delta), TextDisplay/Pin/Instance audit (preserved/lost/extra), Net count, and a
`VERDICT:` line. check.py = 14 independent conditions (a–n) on B1/B2/B3 + determinism +
cross-input guard + malformed. k_rationale = k_check = 14 ≥ 8 GATE ✓.

## Self-verify

REF check() PASS 14/14 ; negative_selftest NEG_RC=0 (5 fakes all FAIL) ; §4.9 three
fakes (empty/print-expected/core-deleted) all FAIL ✓ ; test==disk md5 roundtrip OK.
