# Deepread — 1795422908984_dsaf9 (legendd@hfeg0pkn002, mc628, layout_aether)

## Source
- session: `1795422908984_dsaf9.messages.json` (1.70 MB, 330 messages, 39 user text-inputs)
- user: legendd ; host: hfeg0pkn002 ; scan match_count 628
- keywords: pyaether:1501 schematic:458 dbopencv:322 drc:317 aether:193 rtl:154 cellview:91 dbget:68
- fetched via eda_flow .75 ssh (hfeg0pkn002), on-disk (messages.json + .messages.archive.json)

## Real intent
pyAether standard-cell layout generation for the `drcoa_work` / `stdcells_ac`
library.  The engineer drives the agent to draw layouts for a family of
inverter / buffer cells (`invDSx2`, `invDSx4`, `invDSx8`, `invDSx3`,
`invDSx6`, `invDSx24`, `bufCSx16`, plus earlier `invLVx12_pc60`,
`invLVx32`, `invDSx16`) using a fixed methodology:

- **metals**: M0U + MT2 (two-layer routing), MT2 on bottom / M0U on top for
  via layer order.
- **spacer cells**: explicit nf-column spacers (e.g. spacer width 5.14 /
  9.70 / 5.30 um depending on nf count) — the user explicitly asks "spacer
  cell 呢？" when the agent forgets them.
- **vias**: PCU vias, `aeGenerateViasInArea` to confine drain vias inside
  columns; MT2/M0U overlap regions get multiple vias to reduce parasitic
  resistance ("尽量多打孔，减少寄生电阻").
- **routing**: full-path wires (dbCrtWire for source MT2 bridge), pin/label
  placement (centerCenter), track markers.
- **optimizations**: source/drain merge of adjacent MOS with same net (center
  line align) to cut horizontal pitch; M0U->MT2 swap and MT2/M0U stack+via
  for routing/parasitic-R improvement.
- **DRC-aware geometry**: spacer widths, via enclosure, column pitch
  (0.57/0.59 um), boundary checks (0 越界 = no out-of-bounds).

The whole workflow runs against the shared drcoa_social calibreDRC.rule
runset (`/apps/imctf/cad/runset/train/drcoa_social/current/calibreDRC.rule`),
whose MT2/M0U rule values (extracted verbatim from the runset) are:

| layer | min_width | min_spacing | line_end_spacing | enclosure | spacer_layer |
|-------|-----------|-------------|------------------|-----------|--------------|
| MT2   | 0.272     | 0.192       | 0.234            | 0.014     | MT2_SL       |
| M0U   | 0.195     | 0.176       | 0.207            | 0.039     | M0U_SL       |

## Case reframe (DrcSpacerFixPlanner-001, mock L0/L1 produce-tool)

A recurring sub-task in dsaf9 is deciding the **fix action** for each DRC
violation and computing its geometry: relocate a too-close metal (spacing),
widen a too-narrow metal (width), or insert a spacer rectangle (line-end
extension / enclosure extension).  This is generalised into
`drc_spacer_fix_planner.py`:

- input: layout.json (rects on MT2/M0U) + rules.json (per-layer
  min_width/min_spacing/line_end_spacing/enclosure/spacer_layer) +
  violations.json (id/type/layer/rect_ids/actual/required/gap_vector)
- output: plan.json with `spacers` (line_end + enclosure -> spacer rect on
  spacer_layer, gap_filled == required, geometry extends source rect along
  gap_vector by required-actual), `actions` (spacing -> move with
  move_delta=required-actual; width -> resize with resize_delta), `resolved`
  flag, `summary`.
- pure Python, no EDA tool -> judge_layers=[L0,L1].
- A (visible) = MT2 triple; B (hidden) = M0U triple (different coords /
  values / spacer_layer).  Anti-hardcode via A!=B plan diff.

## check.py (16 conditions a-p)
a compile · b CLI runs on B exit0+output · c structure {spacers,actions,
resolved,summary} · d summary.total==#B-violations · e spacing->move (no
spacer) · f width->resize (no spacer) · g line_end->spacer · h enclosure->
spacer · i spacer fields+positive area+correct spacer_layer · j gap_filled==
required · k move/resize delta==required-actual(>0) · l spacer geometry
matches gap_vector extension · m resolved==true · n 3-run determinism · o
anti-hardcode A!=B · p spacer count==line_end+enclosure.

## Self-verify
- reference `drc_spacer_fix_planner.py` -> check.py PASS 16/16.
- negative_selftest: 4 negs (empty/print/core/hardcode) ALL-FAIL, 4 distinct
  first-fail labels {b,j,e,o}, §4.9 trio {empty=b,print=j,core=e} 3-distinct.
- harness SKIP_RUN=1: workdir builds OK, attachments copied (task_context.md
  + layout_A/rules_A/violations_A), workdir-leak self-check PASS (no
  check.py/reference/hidden shipped to SUT).

## ledger
claim + mark case `EDA-Eval-DesignFlow-DrcSpacerFixPlanner-001` on
dsaf9 (legendd@hfeg0pkn002, layout_aether).
