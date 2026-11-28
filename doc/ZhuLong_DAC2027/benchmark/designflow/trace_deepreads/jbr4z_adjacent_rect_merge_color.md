# jbr4z — Virtuoso SKILL mergeAdjacentAA adjacent-rect merge (color-preservation bug)

**session**: `1795505164479_jbr4z.messages.json` (539 msgs, 1.9MB)
**user**: e0029495 @ hfeg0pkn003 (replica hosts: pkn003/plg64/plg101/plg104)
**match_count**: 643 (virtuoso:937 + dbget:441 + dbcreaterect:115 + cellview:94 + dbopencellviewbytype:71 + lvs:21 + drc:18)
**domain**: layout_virtuoso
**fetched via**: .75 eda_flow scp from pkn003 (PATH-FIX subdir `<slug>/<slug>.messages.json`)

## Real user intent

e0029495 has a SKILL tool `mergeAdjacentAA.il`
(`/proj/lacaa/V0_Virtuoso/workdir/e0029495/mergeAdjacentAA.il`) that merges
adjacent same-layer AA rectangles into single rects. They asked the agent to:
read the script, generate a test layout per its usage scenarios, and test it
in the `test_merge_1124` library (35HDBC tech). The user ran the test in
their own Virtuoso session (SKILL sandbox bridge couldn't connect from the
agent node) and pasted output back for iterative debug.

## The real bug (the tooth of the case)

After merging same-color M2 rects the merged rect **DEGRADED to `grayColor`**
with the lock state grayed-out / unselectable — i.e. the MPT/DPT color and
lock were silently lost. Root cause: `maaCreateMergedRect(cv lpp bb color
rodName @optional locked)` created the new rect without re-applying
`dbSetShapeColor(newRect color)` / `dbSetShapeColorLocked(newRect t)`. The
fix reads the source group's color+lock via `dbGetShapeColor` /
`dbIsShapeColorLocked(car(group))` and writes them back onto the merged rect.

User quotes confirming the bug:
- "t2_merge_chain在有color的情况下merge后丢失color了"
- "我是自己加了color，想测试在相同color下的merge情况"
- "real MPT coloring is set via the Properties panel as color=mask1color,
  state=lock, and after merge it degrades to only graycolor"

## Test scenarios (cells in test_merge_1124)

| cell            | rects | colors                | expected after merge            |
|-----------------|-------|-----------------------|---------------------------------|
| t1_merge_basic  | 2     | none                  | merge into 1 (no color)         |
| t2_merge_chain  | 3     | all mask1Color, locked| merge into 1, KEEP color + lock |
| t3_lshape       | 2     | none                  | keep 2 (L-shape, not a rect)    |
| t4_color_diff   | 2     | mask1 vs mask2        | keep 2 + colorWarn              |

Expected-results table (from `test_merge_aa_test.il`):
```
list("t1_merge_basic"  2 1 nil)
list("t2_merge_chain"  3 1 "mask1Color")  ; NEW rect MUST keep mask1Color
list("t3_lshape"       2 2 nil)
list("t4_color_diff"   2 2 nil)           ; mask1 vs mask2 -> keep 2, checked separately
```

## Merge algorithm (faithful encoding)

1. Group rects by (lpp, color, locked). Different color/lock → different groups, never merge.
2. Within a group, build edge-adjacency (shared edge segment OR overlap; corner-only touch excluded).
3. Connected components: merge into ONE rect iff members exactly tile the union bbox (union area == sum of member areas AND no interior overlap) — i.e. the component is itself an axis-aligned rectangle. L-shapes/gaps/interior-overlaps → keep all members separate.
4. Merged rect: bbox = union bbox; color/locked preserved from group; net preserved if all members share same net else None.
5. colorWarn: for ORIGINAL rects that are edge-adjacent, share lpp + net, but have DIFFERENT color → emit warning (flags likely coloring mistake).

## Case design

- **Case ID**: EDA-Eval-DesignFlow-AdjacentRectMergeColor-001
- **Domain**: layout_virtuoso
- **judge_layers**: [L0, L1] (LIVE-NA — pure-Python, no real EDA needed)
- **Deliverable**: `rect_merge.py` with `merge_layout(layout)` → `{"cells":[...], "warnings":[...]}`
- **Abstraction**: real Virtuoso cellView needs live session + techfile + license → abstracted to pure-Python layout-merge engine (JSON layout in/out), algorithm/semantics/defaults faithful to real SKILL.
- **check.py**: 13 independent conditions, independent recompute of expected merge (no import of reference), hidden B embedded (NOT shipped), A cross-input guard.
  - B (main judge): b_basic(2→1), b_chain(4→1 keep mask2Color+lock), b_lshape(2→2), b_colordiff(2→2+colorWarn)
  - A (cross-input): a_chain(3→1 keep mask1Color — B uses mask2Color so hardcode-B fails), a_lshape(2→2 different coords)
- **Q2 not cheatable**: stub dropping color fails c7/c8; stub merging L-shapes fails c9; stub hardcoding B fails c12 (A color mismatch); stub returning input fails c4.
- **negatives (6, distinct first-fail)**: empty_stub→c2, print_only→c3, core_deleted→c4, naive_no_color→c7, merge_lshape→c9, hardcode_b→c12. §4.9 trio (c2/c3/c4) distinct.
- **check_sha**: 2ffcf53a (16161 bytes)

## Self-verify (all green)

- REF check.py self-test: PASS (13/13)
- negative_selftest: OVERALL_RC=0 (6 neg all FAIL distinct, §4.9 trio c2/c3/c4 distinct)
- §4.9 trio (空壳/print-only/参考解删核心): all FAIL distinct
- SKIP_RUN eval/run_one.sh: framework accepted (attachments deployed, workdir leak check passed, judge ran, no infra_fail)
- build_jsonl.py --shard C: 645 active, case included
- ledger mark jbr4z→case (covered 576→577)
