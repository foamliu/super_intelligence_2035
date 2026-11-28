# Deepread: j0q3u — ivyli Dangling DRC Deck Generator

**Session**: `1789483238511_j0q3u.messages.json`
**User**: ivyli @ hfeg0plg79
**mc**: 339, domain: physical_verify
**Size**: 1.1MB, 227 msgs
**Keywords**: drc:1380, calibre:340, pyaether:138, cellview:54, .gds:25, aether:10

## Real task (user intent)

ivyli maintains a SKILL+Python pair (`generate_dangling_drc_deck.il` + `.py`)
that generates a per-net "dangling (DL) + line-end pin-margin" Calibre DRC deck.
The SKILL side parses the runset file (`utRunset.sh`) for the `*drcRulesFile:`
path, collects signal-port names (terminals NOT ending in `!`), writes them to
a temp `--terms-file`, and calls the Python deck generator with all parameters
(`--ut-deck/--out/--metal-list/--terms-file/--project`). The Python side builds
the deck text, writes it to `--out`, and prints `OUTPUT_FILE: <path>` so the
SKILL can capture the marker.

The 227-msg session is a multi-step iterative build (9 distinct edit cycles):

1. **msg0**: initial ask — modify `.il` to pass parameters to python + get rule
   file from runset + print output file path.
2. **msg53**: "modify the python script under 0915 to get output file path" →
   add `OUTPUT_FILE:` marker to python `__main__`.
3. **msg76**: "Remove stdout temp, define output file path in skill and directly
   check if file generated after python run end" → SKILL defines `outFile`,
   verifies `isFile(outFile)` after `shell(cmd)`.
4. **msg84**: analysis-only of a walrus-operator SyntaxError on Python 2 (`m :=`
   in list comprehension) → msg90: rewrite without walrus.
5. **msg96/98**: debug "python prints success but terminal didn't get file" →
   ut-deck path had trailing `"` (quoting bug); user fixed.
6. **msg102**: `update cxmt_layout_dl_body` — when project is `degpa`, remap
   step1→50, step2→100, step3→200, step4→500.
7. **msg146/154**: `update cxmt_layout_build_deck` for degpa via map
   (M4net-T2M1net BY T2V1, T2M1net-T2M2net BY T2V2, T2M3net-T2M2net BY T2V3)
   PLUS keep standard M4-M3-M2-M1 via V3/V2/V1.
8. **msg160**: debug "DL_M1_01_r still has step1 in degpa deck" → apply remap
   to UT-deck-provided expressions too (`_remap_step`).
9. **msg170**: `update cxmt_layout_line_end_op` for all metals use INSIDE;
   params behind INSIDE as `Mxnet` instead of `Mx`.
10. **msg185/193**: add DRC control header (LAYOUT PATH/PRIMARY/SYSTEM,
    DRC RESULTS DATABASE, VIRTUAL CONNECT block) — user clarifies "0916/ not
    0915/"; msg203: "roll back 0915" (cp from parent).
11. **msg215**: "modify skill script under 0916/ to add all local parameters
    into `prog((...))`".

## Final deliverable (0916/)

- `generate_dangling_drc_deck.py` (510 lines): `cxmt_layout_build_deck` +
  `cxmt_layout_dl_body` + `cxmt_layout_discover_dl_variants` +
  `cxmt_layout_line_end_op` (returns "INSIDE") + CLI `cxmt_layout_DLpinCheck`
  with `--ut-deck/--terms/--terms-file/--metal-list/--out/--project`.
- `generate_dangling_drc_deck.il` (187 lines): SKILL `cxmt_layout_generateDLcheck`
  prog((...)) — parse runset, collect terms, write terms-file, build cmd, run,
  verify outFile, stream out GDS, run calibre DRC, open rve.

## Case design decision

**Deliverable**: the Python deck-generator module `dangling_deck_gen.py` only
(the SKILL side is environment-bound: needs live Virtuoso cellView, runset,
LSF queue, calibre license — not shippable). The Python core is the
substantive intellectual content and is fully self-contained.

**Abstraction**: faithful to the real `.py` — same function names, same
project-aware step remap (degpa: 50/100/200/500), same T2 via pairing, same
INSIDE line-end op, same DL variant discovery from UT deck, same DRC header,
same `OUTPUT_FILE:` marker. Trimmed ~510→~250 lines (dropped pyAether
design-reading, GDS stream-out, rve — those are SKILL-side concerns).

**Judge layers**: `[L0, L1]` LIVE-NA — static judgement (no live EDA). The
check runs the candidate CLI on hidden B (subprocess), parses the generated
deck, asserts structural content. Hidden B = different UT deck variants
(M2/M5), different metals/terms, degpa project → forces step remap + T2 vias.
Anti-hardcode cross-input guard runs candidate on visible A (default project,
M1/M2/M3) and requires the A deck to differ (stepN not 50/100, no T2 vias,
M3net present).

**Q2 stub-test (not fooled)**:
- empty_stub (contentless deck) → fails c3 header
- print_only (no file written) → fails c2 file-exists
- core_deleted (degpa T2 omitted) → fails c7 connectivity
- hardcode_a (hardcoded A deck) → fails c6 INCLUDE path (caught early)
4 negatives, 4 distinct fail tags, §4.9 trio 3-distinct (c3/c2/c7).

## Not-collision argument

No existing C case covers dangling-pin deck generation:
- DrcWaiveDeckGen-001 = waiver-check SVRF deck (different: waive mark vs error
  region intersection).
- DrcDeckOptimize-001 / DrcDeckPrune-001 = DRC deck pruning/closure (different:
  text-level pruning, not deck generation from scratch).
- ImplantFillDeckGen-001 = fill deck (different: metal fill, not dangling pin).
This case = generate per-net dangling+pin-margin deck from signal terms +
metal list + UT deck, project-aware. Distinct.
