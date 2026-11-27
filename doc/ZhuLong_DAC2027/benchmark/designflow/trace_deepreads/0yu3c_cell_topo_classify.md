# Deep-read: 1794819070733_0yu3c — topology-based analog cell classifier for timing-path tracer

## Trace provenance
- session: `1794819070733_0yu3c` (harrywu @ hfeg0plg49, mc=265, domain=analog_context)
- 791 msgs, 2.04 MB; claimed r1616 (shard D, 2026-11-27)
- trace file retrieved via live per-session path `/home/harrywu/.cline/data/sessions/0yu3c/1794819070733_0yu3c.messages.json` (cline per-session subdir format, confirmed working — no snapshot needed)
- top of fresh D-domain candidate pool (544 fresh cands after 4-shard ledger dedup; this trace mc=265 dominant analog:971)

## User real intent
User (analog/timing engineer on DRAM sensing-path timing analysis) is building `trace_rigorous.py`, a tool that walks a timing path backward from a target signal to its trigger, hopping data-path cell-by-cell. At each cell it must decide:
- **"drill in"** (treat cell internal nets as independent hops, grab edges per internal net), or
- **"cross-level"** (treat cell as black box, take only In↔Out end-to-end delay).

The early implementation used a **cell-name whitelist** to pick cross-level cells, but cell names vary endlessly and can't be enumerated — the algorithm kept drilling into analog delay chains. User decides to replace the whitelist with a **topology classifier**: read the cell's SPICE subckt internal device structure (MOS transistors / logic gates) and auto-classify by device connection pattern, NOT by name.

The classifier must distinguish:
1. **analog_delay** — analog delay cell (cross-level): current mirror (≥2 same-polarity MOS sharing a non-supply bias gate) / analog charge-discharge node (a net that is both a PMOS drain and an NMOS drain with the two driving gates being different analog signals) / trim width select (≥2 parallel legs of the same MOS primitive subckt with identical d/g/s/b but differing w).
2. **level_converter** — digital level-shift cell (cross-level): cross-coupled PMOS pair (A gate→B drain, B gate→A drain) AND (differential NMOS pair: two NMOS common-source non-ground with different gates / multi power domain: PMOS sources on ≥2 distinct high-voltage rails).
3. **gate_delay** — ≥2 logic-gate stages chained as delay line, no analog features, no cross-coupling (cross-level).
4. **pure_gate** — single combinational gate (drill in).

## Deliverable (what user accepted)
A `classify_cell.py` exposing `classify_cell(cell) -> {"type":..., "features":{...}}`. The user iterated the detection rules with the assistant to avoid false-positives: cross-coupled latch nodes excluded from current_mirror / charge_discharge; trim requires parallel legs (identical d/g/s/b, differing w); multi_power uses PMOS sources ending in `!` excluding ground.

## Case synthesis (this round, done)
- **task_id**: `EDA-Eval-DesignFlow-CellTopoClassify-001` (shard D, analog_context)
- **reframe**: synthesized-reframe — real user intent (topology cell classifier) re-framed as generic `classify_cell(cell)->{type,features}` with hidden-B anti-hardcode. deliverable = `outputs/submit.zip`(classify_cell.py).
- **A (visible)**: spec_A.json with 5 sample cells (one per type + trim variant) — R_asVdbiasDly(current_mirror) / R_lvlshftVccToVdly(cross-coupled + diff pair) / R_invChainDly(3-inverter chain) / NAND2x1(single gate) / R_trimbuf(trim width select).
- **hidden B** (token-structurally different): 6 cells with completely different names/nets/counts/widths — AmpBiasGen(current_mirror) / LvShftCore(cross-coupled+diff+multi-power) / GateDlyBuffer(4-inverter chain) / OR2x2(single gate) / RchrgDlyCell(charge-discharge) / LvShftSimple(cross-coupled+multi-power, no diff pair). Each B cell exercises a distinct detection path so hardcoding one path can't satisfy another.
- **check.py 13 conds (a..m)**: a zip has classify_cell.py / b py_compile / c A-runs return type+features dict (A档可用性) / d B-runs return dict / e B1 AmpBiasGen type==analog_delay / f B1 current_mirror==True & trim==False / g B2 LvShftCore type==level_converter / h B2 cross_coupled_pmos==True & diff_nmos_pair==True / i B3 GateDlyBuffer type==gate_delay / j B4 OR2x2 type==pure_gate / k B5 RchrgDlyCell type==analog_delay & analog_charge_discharge==True & current_mirror==False / l B6 LvShftSimple cross_coupled==True & multi_power==True & diff_nmos_pair==False / m anti-hardcode (A-only tokens absent from classify_cell.py source).
- **LIVE-NA**: input is parsed JSON (structural topology checks), no real EDA tool output dependency ⇒ judge_layers=[L0,L1], no check_live.
- **negatives** (5, all FAIL distinct first-fail): empty→c / print_only→e / core_deleted→e / features_false→f / charge_discharge_broken→k. §4.9 trio full (empty/print_only/core_deleted) + 2 extra.

## Self-verify (all green)
- ref check.py on reference_submit.zip → **PASS**
- negative_selftest: 5 neg ALL-FAIL, distinct first-fail {c,e,e,f,k}
- 3-way sha sync: disk check.py == JSON test field == metadata.check_sha256 = `442d9dbe88d7029386123f18cdfd1ac5f87e3900deb0627d1baa9a654e5b42cc` (size 8893)
- SKIP_RUN=1 eval/run_one.sh CellTopoClassify-001 --shard D: workdir leak self-check PASS (no check.py/reference/hidden in SUT workdir), case deploys correctly from rebuilt jsonl
- k_check = 13 = k_rationale = 13
- case 进 D jsonl (587 cases)

## Status
- **case complete r1616** — built + self-verified + ledger marked.
- 台账: `1794819070733_0yu3c → case (EDA-Eval-DesignFlow-CellTopoClassify-001)`.
- 544 fresh D-domain cands remain on .75 (top alternatives: 1795071241845_e1gmg mc=427 / 1788916632467_soebd mc=400 / 1794970604490_f1olf mc=318 / 1795412906029_j7652 mc=317 / 1795159951898_jaay4 mc=305) — re-derive next loop after session close.
