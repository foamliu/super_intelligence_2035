# Deep-read — r253 · trace 1793671576342_r677h (shaoyou@hfeg0pkn003/10.129.2.12, mc=117)

**Case**: EDA-Eval-DesignFlow-PinListPortOrderExtract-001 (layout_aether, B-synthesized, L1, k=15 a-o)

## Trace facts
- session: `1793671576342_r677h.messages.json`, agent=lead, 87 msgs (52 user-role = mostly tool_results, 35 assistant)
- kw: `120 pyaether + 112 schematic + 87 dbget + 61 cellview + 41 "lang":"pyAether"` → pure pyAether/aether DB, 0 sim kw → clean layout_aether seed
- NEW user **shaoyou** (first case for this user)

## User intent (U#0, 提出需求, 未给根因, A/B qualified)
> 「帮我获取当前电路的所有pin列表， 输出到pin.list文件中」

Only one organic user turn (mode=act auto-injected); remaining 51 user-role msgs are tool_result blocks. User states a goal (get pin list of current circuit → pin.list file), gives no root-cause, no fix → A档 rule2 qualified, B档 qualified seed.

## Agent flow (grounding)
1. `RAG_MCP_Server__search_apis("获取当前电路的所有pin列表", lang=pyAether)` → found `dbSchGetPinOrder`, `emyFigGroupGetAllPinNets`, `aeGetCurDesign`
2. Iterated ~10 search rounds exploring `emyDesign`/`emyBlock`/`emyTerm` methods; settled on `dbSchGetPinOrder(pDesign)` (returns emyStringArray of pin names from portOrder property)
3. `run_approved_command` get-username.sh → `shaoyou`
4. `SandBox_MCP_Server__run_code` test: `emyInitAether("-ADV")` → `aeGetCurDesign()` → `dbSchGetPinOrder(cv)` → tuple of pin names → `[str(p) for p in pin_tuple]` → write one per line
5. Real run result: **1456 pins** written to `pin.list`; first=`LBDQ`, last=`vglbref`; bus names like `YioMatERW_RB0_BGH_rc<15:0>` kept as single lines (dbSchGetPinOrder returns them as single names, NOT bit-expanded)
6. Saved `get_pin_list.py` (function `get_pin_list_and_write()`) to `/ai_sandbox/drgqa/V0/agentdir/shaoyou/get_pin_list.py`; removed `if __name__` test block per code convention
7. Final verification: re-ran end-to-end, PASS (1456 pins, first=LBDQ, last=vglbref)

The cellview is a DDR PHY top (pin names: LBDQ/LBDQS/TDQSPad_C/YioMatERW_RB0_BGH_rc<15:0>/ZQ/vglbref → DDR PHY / IO boundary).

## Why B-synthesized (not A档)
- Real cellview lives in shaoyou's `/ai_sandbox/drgqa/V0/agentdir/` — not accessible to e0031982; cannot take the real 1456-pin pin.list as A-input verbatim.
- A档 rule: task说明 = user原话逐字 (✓ kept verbatim in prompt), 金标准 = trace末尾用户接受的结果. But the accepted result (real pin.list of an inaccessible cellview) cannot be reproduced as a gradable deliverable. → B档 (synthesized representative assets grounded on the same pyAether operation + trace pin-name style).

## B-synthesized reframing
Reframe as `pin_list_extract.py <terms.json> -o <pin.list>` (stdlib only):
- INPUT: JSON dump of cellview terms `{cellview, lib, terms:[{name, direction, portOrder}]}` (the data `dbSchGetPinOrder` would return, plus direction for richer grading)
- OUTPUT: `pin.list` = one pin name per line, in portOrder ascending (terms missing portOrder sorted last by name); faithful to trace (flat names, portOrder, bus names as single lines)
- STDOUT: summary JSON `{cellview, total_pins, direction_counts, bus_pin_count, bus_total_bits}` (bus pin = name ending `<hi:lo>`, bits = `hi-lo+1`)

## DISTINCT from existing layout_aether / pin-related cases
- r246 **LefFromPinList**: pin_list.txt (name+coords) as INPUT → generate LEF. Inverse direction (LEF gen from pins, not pin extraction from cellview).
- r233 **InstM0ShapePinIdentify**: filter shapes on layer M0 that are pins (shape-level, layer filter). r677h enumerates all terms (term-level, no layer filter).
- r222 **SchOaInventoryExtract**: inventory .oa files (file-level). r677h enumerates pins of one cellview (term-level).
- r252 **LayStructExtract**: structural summary of shapes/instHeaders (shape/inst level). r677h enumerates pin/terminal portOrder (term-level).
- → 本案 first ground on **cellview terminal/pin portOrder enumeration** (dbSchGetPinOrder → pin.list in portOrder), distinct operation.

## Case structure
- assets/A: `terms_A.json` (DDRPHY_top, 58 terms, 16 bus pins incl DQ0<7:0>/ADDR<13:0>/YioMsaq0<15:0>/MARGIN<3:0>, dirs inout28/input18/output12) + prompt.txt + task_brief.md
- hidden: `terms_B.json` (ADC_CTRL_top, 33 terms, 8 bus pins, dirs inout16/input10/output7), `terms_B2.json` (BANDGAP_simple, 12 terms, 0 bus), `terms_B3.json` (EMPTY_cell, 0 terms), hidden_manifest.json
- reference: golden_solution.py (stdlib), golden_A/B/B2/B3.pin.list + _summary.json, check.py (15 conds a-o), negative/{empty_shell,print_expected,hardcoded_A,core_deleted,stub_no_parse}.py, negative_selftest.py, reference_submit.zip

## Self-verification
- golden self-test: check.py on reference_submit.zip → **PASS 15/15** ✓
- negative_selftest: 5/5 negatives FAIL as expected (NEG_RC=0) ✓
- §4.9 三假提交 (empty_shell/print_expected/core_deleted) all FAIL ✓
- test field (jsonl) == disk check.py bytes ✓ (9908 B)
- 断言闸门: k_rationale=15=k_check(a-o)≥8 ✓ GATE PASS

## Selection context (this round)
sel_C_r253c: mc≥30 NEW-user (exclude ledger 436 anchors + SAT users incl mwxi/yohannw/hbpeng/jason17w/lvyy/etc), layout-affinity score=ΣLAY_KW − 0.6×ΣSIM_KW, run on .75 summary.tsv → top cand probed:
- 4c5ws (e0046913, mc51, innovus+calibre kw) → env-recon/how-to (view png/install bcompare/check version), innovus/calibre kw from assistant listing install cmds not real EDA → parked
- psbg1 (tongni, mc65, calibre kw) → env-recon/how-to (list skills/how spice_agent built/build agent from scratch/env.json) → parked
- p5x6n (e0023936, mc92, virtuoso kw) → wrong-domain (draw cosine wave via WaveView ACE Tcl = spice_sim/waveview) → parked
- uxwb5 (e0023936, mc64, pyaether+cellview) → wrong-domain (highlight nets in Schematic = schematic highlight skill) → parked
- **r677h (shaoyou, mc117, pyaether+dbget+cellview)** → organic layout_aether seed (get pin list of current circuit via pyAether) → SELECTED
