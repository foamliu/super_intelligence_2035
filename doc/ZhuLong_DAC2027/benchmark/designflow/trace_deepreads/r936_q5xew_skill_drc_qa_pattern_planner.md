# Deepread: q5xew — kenwang SKILL DRC QA pattern generation library refactor

**Session**: `1790584988596_q5xew.messages.json`
**User**: kenwang @ hfeg0plg16 (also on hfeg0pkn004)
**Dates**: 2026-09-29 to 2026-10-09 (371 messages, 1.3 MB)
**Match count**: 198 (drc:380; dbcreaterect:187; cellview:45; dbopencellviewbytype:40; ddgetobj:37; dbcreatepolygon:37; virtuoso:4; lib.defs:4; pdk:2; mosfet:2; .lef:2; cadence:1)
**Domain**: physical_verify (DRC QA pattern generation for Cadence Virtuoso layout) — crossover with layout_virtuoso (SKILL/dbCreateRect/dbCreatePolygon).
**Prior ledger state**: parked 2026-11-14 as "kenwang known-reject r547 context-summary" — r547 only saw msg 0 which is a context-continuation summary, not the user's first real turn. Full deepread shows a substantial multi-turn design task.

## Real task (user intent, multi-turn)

kenwang is building a **SKILL-based DRC QA pattern generation library** (`DRQA_Phase1_Release_v0.3`) for Cadence Virtuoso. The library generates DRC test patterns (geometry on M1/M1_mark1 layer pairs) to validate spacing rules. The session covers a full refactor cycle:

1. **msg 0–20**: `M1_S_20.il` is corrupted — lines 64–67 contain residual `fprintf(out ...` generator code (not executable SKILL), lines 78/82 use undeclared `x, y, T, L` variables. User wants direct file edits, not regenerate.

2. **msg 21 (KEY TURN)**: User rejects the hardcoded-coordinate approach as a **bad design** — wants **generic parameterized topology functions** reusable across layers/rules. Quote: *"使用具体的数值的方式是非常糟糕的一种设计方法，因为这种不可以使用在每一组Pattern中...生成各种Pattern的模块，直接调用的方式来生成Pattern"*. Still has undefined `x`. → Assistant designs `drqa_topology.il` with 10 generic `drqaTopo_V1..V10(cv lp1 lp2 x y g pid cls tv ev ru ca br)` functions.

3. **msg 113**: User reports Virtuoso error `*Error* eval: undefined function - drqaTP` — the refactor deleted inline helpers (`drqaTP`, `drqaPP`, `drqaSetShapeColor`, `drqaMB`) that every topology function calls. → Assistant makes `drqa_topology.il` self-contained by adding the helpers at the end.

4. **msg 133**: User reports **all patterns overlap** at `x0=0, y0=0` — *"所有的Pattern都在原始坐标。几个Pattern都摞在一块了"*. → Assistant adds `pitch=3.0` and `x0=N*pitch` per topology group so each group is independently placeable.

5. **msg 181**: User wants **per-group DRC_BAD mark1 layer** (independent boxes per bad pattern, not one giant box), and provides a hand-edited `M1_S_20_bad_dump.il` dump for V10 reference showing the corrected diamond offset.

6. **msg 253 (KEY TURN)**: User wants **GOOD = 2 gap values** (boundary 0.14 = B + boundary+grid 0.1401 = P), **BAD = 1 gap value** (boundary-grid 0.1399 = F) + per-group mark. Asks if the hardcoded mark coordinates violate the "generic pattern" goal: *"per-group DRC_BAD marks for BAD cells 这一组的内容依然存在很多坐标，这是否是根据dump出来的问题生成的呢，如果是这有违反了我们期初设定的目标，即设定一些通用的Pattern，不可以用具体坐标表示"*. → Assistant adds 10 `drqaTopo_V{N}_mark(cv ml x y g)` functions computing mark boxes from geometry params (W/H/dx/dy/margin/gap), no hardcoded absolute coords.

7. **msg 351**: User asks to summarize the conversation into `space_pattern.md` design doc. → Assistant writes the doc.

## Trace gold (assistant deliverables)

1. **`drqa_topology.il`** — generic parameterized topology library:
   - 10 topology functions `drqaTopo_V1..V10(cv lp1 lp2 x y g pid cls tv ev ru ca br)` — each draws a BOUNDARY/FAIL_LOW/PASS_HIGH pattern pair with gap `g` at origin `(x, y)`.
   - 10 mark functions `drqaTopo_V{N}_mark(cv ml x y g)` — each computes a per-group DRC_BAD mark box from geometry params (no hardcoded absolute coords).
   - 4 shared helpers: `drqaSetShapeColor`, `drqaTP` (create rect with props+color), `drqaPP` (create polygon with props+color), `drqaMB` (mark box helper).

2. **`M1_S_20.il`** — refactored rule file:
   - `pitch=3.0`, `x0=N*pitch` per topology group (anti-overlap).
   - `if(isGood "BOUNDARY" "FAIL_LOW")` classification switching.
   - `boundary`/`grid` params drive `gap` value (GOOD_B=boundary, GOOD_P=boundary+grid, BAD_F=boundary-grid).
   - GOOD emits 2 patterns (B+P), BAD emits 1 pattern (F) + per-group mark via `drqaTopo_V{N}_mark`.

3. **`space_pattern.md`** — design doc summarizing the architecture, topology function signatures, helper inventory, and how to add new rules.

## Cross-shard collision check

- 4-shard ledger: q5xew only in C (was parked r547, revived r936).
- 4-shard jsonl trace_source: no q5xew.
- Same-domain (physical_verify) already-cased C cases: DrcDeckBlockReformat (block→single-line reformat), DrcRuleFromDesc (rule code dev), DrcDeckRuleUpdClassify (rule update classify), DrcLogAnalyzer/DrcRunStatusAnalyze/DRCLogTeardown (log analysis), DRCPatGen/DrcTestpatternGen/DrcPatternPlan (testpattern layout drawing), CalibreDrcRunsetConfigValidator (runset validate), CalibreDrcLayoutPathBlankDiag (runset path diag), AetherAsoutLibDefsDiscoveryPlanner (asOut command), CoordTransformTrigRefactor (coord trig), HierPathKwClassifier (hier path kw), DrcDeckDescCodeNumAudit (deck desc audit), LvsPcSplitRootCauseAnalyzer (LVS PC split), LvsPinCaseMismatchDiag (LVS pin case), LicHostToIpRewrite (lic host→ip), LdrLiteralEscapeFix (DRC pattern tool regex escape), GxrcCmdParamCrossRef (gxrc param cross-ref), SkillRcPatternDiffAnalyze (SKILL RC pattern diff), VirEnvCancelInitFix (vir env init), SkillScopeMigrate (SKILL scope migrate), VirtuosoDaemonReviewFix (virtuoso daemon review), VirtuosoCliNoInstanceJsonErr (virtuoso CLI json err), LayoutLabelArgOrderFix (layout label arg order), DrcSummaryCountCmp (DRC summary count cmp).
- **All orthogonal** to this case's sub-type "skill_drc_qa_pattern_planner" (Python planner emitting a structured plan for a SKILL DRC QA pattern generator, covering pitch-based placement + per-group geometry-computed mark boxes + helper inventory). **First of this sub-type.**

## Reframe decision (档 B fixture-driven)

Reframe as a **fixture-driven Python planner** task: the agent writes `space_pattern_planner.py` that reads a `rule_spec.json` and emits `plan.json` with:
- per-topology `x0 = N * pitch` placement (anti-overlap)
- 3 gap variants (GOOD_B=boundary, GOOD_P=boundary+grid, BAD_F=boundary-grid) + classifications
- per-topology `mark_box` computed from geometry (W/H/dx/dy/margin/gap) — no hardcoded absolute coords
- `mark_box_relative` (mark_box minus x0,y0) proving geometry-relativity
- `helper_inventory` (shared_helpers + topology_functions + mark_functions) for self-contained SKILL
- `validation` block (no_hardcoded_absolute_coords, good_has_two_patterns, etc.)

**env_A** (visible): M1_S_20, boundary=0.14, grid=0.0001, pitch=3.0, 10 topologies V1-V10 (W=0.2, margin=0.4, varied H/dx/dy).
**hidden B** (for check): M2_S_30, boundary=0.20, grid=0.0005, pitch=5.0, 6 topologies V1-V6 (W=0.3, margin=0.5, varied H/dx/dy). **7+ dimensions differ** (rule_name, layer_pair, boundary, grid, pitch, num_topologies, W/H/dx/dy/margin) — strong anti-hardcode.

## Self-verification (r936)

- Reference planner PASSES check() all 17 teeth ✓
- 3 negative samples FAIL distinct teeth: naive_empty→tooth-b, naive_print_A→tooth-e, neg_delete_core→tooth-k ✓
- §4.9 (a)(b)(c) three-fake-submit: (a) empty shell = naive_empty → FAIL; (b) print expected = naive_print_A → FAIL; (c) delete core = neg_delete_core → FAIL ✓
- 3-seed determinism: byte-identical sha256 across seeds 11/22/33 ✓
- k_check == k_rationale == 17 ✓
- Roundtrip: deliverable zip sha256 stable ✓
