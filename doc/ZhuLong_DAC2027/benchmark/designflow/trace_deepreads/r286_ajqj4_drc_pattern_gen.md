# Deepread — r284 / ajqj4 (lizwen@hfeg0pkn003)

- session: `1789960398048_ajqj4` (512 msgs, 1.99 MB)
- host: hfeg0pkn003 (10.129.2.12)
- user: lizwen  (NOT in avoid list)
- domain: layout_aether (DRC testpattern generation)
- cron markers: 455 pyAether, 263 cellview, 112 calibre, 82 dbGet, 26 schematic

## Real user intent (consolidated across iterative turns)

Build a DRC **testpattern** generator driven by a rule query:

1. Load a DRC deck (text `test_deck_new`) + structured `drc_rules_spec.json`
   (49 rules, W/S/A/E categories) + `derived_layer_map.json`
   (physical_layer_map: gds_layer / dt / calibre_num).
2. User issues a **query** — exact rule_id (`DNW_W_000_00`), wildcard
   (`DNW*`, `*enc*`), case-insensitive, multiple queries unioned.
3. For each matched rule, generate a **PASS** and **FAIL** testpattern:
   - PASS geometry satisfies the rule threshold (width/spacing/enclosure >= min);
   - FAIL geometry violates it (< min).
   - Coordinates come from `pattern_constraints.{pass,fail}_case.coordinates_hint`
     (e.g. `Rect1: (0,0,100,100), Rect2: (0,109.30,100,209.30) -> spacing=9.30`).
4. Resolve each shape's layer through `derived_layer_map` → gds_layer/dt/calibre_num.
5. Snap to grid (0.001 um), Cartesian, bottom-left origin.
6. Naming convention: `TP_{rule_id}_PASS` / `TP_{rule_id}_FAIL`, cell_prefix `TP_`.
7. Region markers: peri rules need PERI, core rules need CORE.
8. `--list` mode: list all deck rules, no generation.
9. No-match query → clean empty result.
10. Final render target originally `.oa` via pyAether (dbCrtRect / dbCrtLabel /
    dbNewCV / dbSaveCV); techfile `techfile.tf` attached so layers display.

## Pain points hit in trace (realism signal)

- path error `home/...` vs `/home/...` on ae.load
- UnicodeDecodeError (ascii codec) loading non-ascii script → must read utf-8
- "This design has no technology" creating rects/labels → techfile not attached
- SandBox service not started → fallback to direct pythone
- skill slash-command `/drc-pattern` not registered → installation friction
- bjobs/bkill queue cleanup, modulefile `empyrean/alps` missing
- iterative deletion of intermediate scripts; user wanted minimal artifacts
- pattern .oa not produced initially (empty drcPatterns dir)

## Reframed deliverable (offline-checkable)

The .oa rendering needs Aether runtime (check.py cannot run Aether). The
**core intellectual work** is offline-checkable: parse deck → resolve query →
look up spec → parse coordinates → map layers → snap grid → emit structured
`pattern_package.json` with PASS/FAIL entries. So the SUT produces a pure-Python
`drc_pattern_pkg.py` whose output JSON encodes exactly what would be drawn.

## Key data shapes

- `drc_rules_spec.json`: keys spec_version, rule_count, rule_categories,
  layer_definitions, region_definitions, rules[], pass_fail_margin
  {pass_margin:0.01, fail_margin:0.05, note...},
  pattern_naming_convention {pass_case, fail_case, cell_prefix},
  coordinate_system {type:Cartesian, origin:bottom-left, unit:um, grid:0.001}.
- rule: rule_id, rule_type (width/spacing/enclosure/extension/...),
  layers[], layer_relation, region (peri|core|both), parameters{min_*},
  svrf_raw, pattern_constraints{pass_case, fail_case}
  {geometry, required_layers[], coordinates_hint, expectation}.
- `derived_layer_map.json`: physical_layer_map {NAME: {gds_layer, dt,
  calibre_num, desc}}, marker_layers (PERI/CORE), derived_layer_chain.

## Case plan (r284)

- id: `EDA-Eval-DesignFlow-DrcPatternPkgGen-001`
- A (visible): trimmed spec (12 rules, all types) + layer_map subset +
  test_deck_new (matching) + task_brief.md.
- B (hidden): DIFFERENT spec/layer_map/deck (different ids/values/layers) +
  different queries (exact, wildcard, case-fold, no-match, union, --list).
- golden.py: correct resolver + geometry + layer-map + grid-snap + naming.
- check.py: ≥12 independent conditions (query resolution, geometry math,
  layer mapping on B, pass/fail DRC correctness, grid snap, naming, region
  marker, --list, no-match, union dedup, schema, coordinate parse).
- negatives: ≥2 (wrong layer mapping; ignores margin/pass-fail inversion).
- §4.9 fakes: empty zip / non-runner / wrong-output-name → FAIL.
