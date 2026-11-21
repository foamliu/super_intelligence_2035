# trace_deepread: p1c7e (hongl @ hfeg0plg79) — Aether Layer-Purpose Pair Explainer

- **session**: `1794797985155_p1c7e.messages.json`
- **user / host**: hongl @ hfeg0plg79 (10.129.8.122)
- **mc / keywords**: 83 — aether:886; schematic:100; verilog:38; netlist:36; pdk:28; mixed-signal:24; virtuoso:22; floorplan:20; pyaether:13; cellview:13; drc:10; lvs:8; pex:6; … (C-dominant: aether-heavy)
- **size**: 451 KB / 1104 lines / 39 msgs (20 user / 19 assistant) — small Q&A session
- **agent**: zhulong (lead), system_prompt mentions coding + Aether skill
- **session window**: 2026-11-16 10:59 – 11:04 (~5 min, 3 typed user turns)

## Real user intent (3 progressive Q&A turns)

1. **msg#0** `<user_input mode="act">` "DGX是什么？" → assistant answered generically (NVIDIA DGX AI supercomputer).
2. **msg#2** "版图里的DGX是什么" → assistant searched Aether reference manual (5926 pages), 交流群问答 KB, 快捷键速查表 — all came back empty for "DGX". Gave 3 possible interpretations: (a) PDK-specific layer name (DG = Dummy Gate / Deep Guard Ring, DGX = extension), (b) project/module/cell naming, (c) misspelling (DGC / DFX / DC). Asked user to clarify context (LSW / cell name / tech file / menu / other).
3. **msg#25** "DGX DRAWING代表什么" → assistant read Aether manual **Part IX Tools → Chapter 97.3.3 Purpose** and explained:
   - **DRAWING** = one of 11 predefined Aether Purposes (constant `oavPurposeNumberDrawing`, immutable/non-deletable), marks the main designer-drawn physical geometry (vs fill/slot/annotation).
   - **DGX** = Layer Name defined by PDK; Aether manual doesn't define its physical meaning — must consult PDK Layer Map / GDS Layer Mapping Table.
   - **Lookup steps**: Tools → Technology Manager → Layer page → find DGX → read Layer Number & Display Resource.
   - **DGX abbrev candidates**: DG=Dummy Gate, DG=Deep Guard Ring, DGX=Dummy Gate eXtension, DGX=Deep N-well Guard Ring X.

## Assistant tool chain (19 assistant msgs)

- `skills(aether-tool-qa, ...)` — invoke Aether doc-search skill
- `cimi-kb-search(...)` — **rejected by harness** (tool not available)
- `read_files(...)` — read Aether manual part files (part_II, part_IX, part_V_...) × 8
- `run_approved_command(profile='shell-runner'/'python-runner', filePath=...)` — **failed** (profile requires filePath that doesn't exist)
- `SandBox_MCP_Server__run_code(...)` — **connection refused** (pyAether sandbox down)
- `list_allowed_files(...)` — enumerate allowed reference files
- `skills(ask-eda, ...)` — invoke AskEDA KB
- Final answer in msg#38 (text block): structured Layer-Purpose Pair explanation with manual citation + lookup steps + abbrev table.

## Deliverable (the gold answer in msg#38)

A structured explanation of `DGX DRAWING` as a Layer-Purpose Pair:
- structure: `LAYER` + `PURPOSE` = Layer-Purpose Pair
- purpose = "drawing" (one of 11 predefined, `oavPurposeNumberDrawing`, immutable)
- layer = "DGX" (Layer Name from PDK)
- manual citation: Part IX Tools → Chapter 97.3.3 Purpose
- lookup: Tools → Technology Manager → Layer page
- abbrev candidates: DG/DGX with possible full names

## Reframe decision (A vs B tier)

- **A-tier infeasible**: live Aether install + PDK + Technology Manager GUI + license not in SUT sandbox. The trace is purely doc-search Q&A — no script artifact was produced by the user; the "deliverable" is the assistant's textual answer.
- **B-tier reframe ACCEPT**: synthesize a structured "Aether Layer-Purpose Pair Explainer" tool. Given an Aether manual JSON + PDK layer definitions JSON + a query (layer name + purpose), produce a structured `report.json` explaining the layer-purpose pair with manual citations. Fully static, offline-judgeable.
- Anti-hardcode: env_A traces the real hongl case (layer DGX, Part IX Ch 97 § 97.3.3, PDK CXMT_28nm_A). env_B (hidden) uses layer POX, Part VII Ch 88 § 88.2.1, PDK CXMT_40nm_B — different layer name, different manual edition numbering, different PDK abbrev candidates.

## Case artifact mapping

- `assets/AetherLayerPurposeExplainer-001/env_A.tar.gz` (visible to SUT): aether_manual_A.json + pdk_layers_A.json + query_A.json (DGX) + spec.json
- `reference/AetherLayerPurposeExplainer-001/env_B.tar.gz` (hidden): aether_manual_B.json + pdk_layers_B.json + query_B.json (POX) + spec.json
- `reference/AetherLayerPurposeExplainer-001/check.py` — 20 teeth (a..t), runs SUT only on env_B, anti-hardcode teeth (g/o/p/t) verify SUT read env_B
- `reference/AetherLayerPurposeExplainer-001/solve.py` — ref solve, env-agnostic, derives everything from input files
- `reference/AetherLayerPurposeExplainer-001/negatives/solve_*.py` — 7 negatives (only_print/hardcode_A/empty_report/copy_manual/empty_stub/print_only/delete_core), all FAIL distinct
- `reference/AetherLayerPurposeExplainer-001/negative_selftest.py` — runs all 7 negatives through check.py, asserts all FAIL

## Self-verification results

- ref solve.py PASS 20/20 on env_A and env_B (env_A: DGX/Part IX/§97.3.3, env_B: POX/Part VII/§88.2.1)
- 7 negatives all FAIL-OK distinct (e/g/f/g/e/e/n)
- §4.9 (a) empty_stub → (e), (b) print_only → (e), (c) delete_core → (n) — all FAIL
- 3-seed determinism tooth (s) PASS: report.json sha256 identical across seeds 11/37/99
- Roundtrip: disk check.py sha256 == jsonl test.check_code sha256 = `4c703b6032e9fd1acbb9863f6a2bd3724e63369a8884b02bf2aedd52abbdca2b`
- k_check == k_rationale == 20 (≥8 ✓)
- C.jsonl 571 → 572
- ledger mark p1c7e → case (AetherLayerPurposeExplainer-001); stats: case 577 → 578

## Lessons

- **doc-search Q&A is a legitimate real intent** (per 11-15 audit). The user genuinely wanted to understand "DGX DRAWING"; the assistant's manual lookup + structured explanation is the real deliverable. Reframing it as a structured-JSON-explainer tool preserves the intent (parse manual → explain layer-purpose pair → cite manual) while making it offline-judgeable.
- **anti-hardcode via env-B edition swap**: instead of just changing the queried layer name, also change the manual Part/Chapter numbering (Edition A: Part IX/97.3.3 vs Edition B: Part VII/88.2.1) — forces the solver to actually parse the manual structure rather than hardcode the citation.
- **tooth-(b) candidate exclusion**: must exclude `negative_*` (negative_selftest.py) AND must NOT exclude `solve_*` (the negatives/ convention names negatives as `solve_*.py` — they ARE the candidate when packaged as submit.zip). First version excluded `solve_*` and all negatives trivially failed at tooth (b).
