# Deep-read: 1791611132079_5vmvu — port-text/pin propagation (layout_virtuoso)

- **trace**: `1791611132079_5vmvu` · user `ellawu` · host `hfeg0pkn005` · mc=165 · 310 msgs · 1.3MB
- **domain**: layout_virtuoso (Cadence SKILL, Virtuoso layout)
- **tool profile**: read_files 76, editor 66, run_commands 2, ask_question 1, search_codebase 1, skills 2, RAG search 1
- **session path** (remote): `/home/ellawu/.cline/data/sessions/1791611132079_5vmvu/1791611132079_5vmvu.messages.json` (note: in a per-session **subdirectory**, not directly under sessions/)
- **attachment**: `cxmt_autoPR_generatePortText.il` (CXMT SKILL, 20.7KB) — cline's /tmp copy was cleaned, but full content recovered from the `read_files` tool_result inside messages.json.

## Real task (user turns, verbatim)
1. `fenxiyixiazhegejiaoben` (analyze this script) — attached cxmt_autoPR_generatePortText.il
2. `genjuzhegejiaobenxiugai shidedicengdepinnengfudaodingceng` — modify so bottom-layer pins propagate to top
3. `chuangjiandicengchule vcc vss desuoyou pin` — create every bottom-layer pin except vcc/vss
4. `dubantudicengweizhishizaidaimanagebufentixiande` — the bottom layout position is reflected in the `daimanage` part

Assistant clarified intent as **case B**: every layout instance's pins must be processed — INCLUDING instances that exist only in layout (not in schematic). The original script only processed schematic-present instances and only created pins that traced to a top signal.

## Script structure (from assistant analysis msg[3])
5 functions: `cxmt_generatePortText` (main), `cxmt_generatePortTextInSelectedInst`, `cxmt_autoPR_generatePortText_SpltInst` (bus `<a:b>` via dbProduceMemName), `cxmt_generatePortTextCell` (core: bBox position index dedup, PROJ_NAME font sizing, leCreatePin/dbCreateLabel, sub-cell→top coordinate transform). Edits went to a new file `cxmt_autoPR_generatePortText_v2.il`.

## Extracted verifiable core (case PortTextPinPlan-001, B-synthesized, L1-boundary)
Live Virtuoso SKILL blocked in .75 sandbox → extracted the deterministic, checkable core as a pure-stdlib planner `port_text_pin_plan.py`:
spec JSON → iterate ALL instances (incl. layout-only) → bus `<a:b>` expand (asc/desc, pitch per bit) → skip power nets (vcc/vss) → bBox center + slice origin = top coordinate → top_signal (explicit or net fallback, bus adds `<bit>`) → dedup vs existing_labels / existing_pins → plan JSON.

## Specs
- A (visible) `assets/PortTextPinPlan-001/spec_A.json`: ADC_TOP, I0=INVX1 (A/Z/VDD/VSS), bus I1<0:1>=BUFX2 layout-only pitch[0,100], power vcc/vss, dup label+pin A_sig @ (120,220).
- B (hidden) `reference/.../hidden/spec_B.json`: DAC_BOT, IA=NAND2 (A/B/O/VDD/GND, power vdd/gnd), descending bus IB<2:0>=MUX2 layout-only pitch[100,0], dup NA @ (60,80) — kills hardcode.
- B2 (hidden) `spec_B2.json`: TOP2, single instance, power vcc — cross-input guard.

## Judge (check.py): 15 conditions a–o
a zip+py · b py_compile+stdlib · c run B exit0 · d plan keys · e n_instances (bus+layout-only) · f n_power_skipped (除vcc vss) · g no power-net creation · h layout-only slices present · i coordinate transform · j label dedup · k pin dedup · l descending bus IB<2:0>→3 slices · m top_signal fallback · n determinism+no-leak · o cross-input guard (plan_B2≠plan_B).

## Self-verification
ref PASS 15/15. Negatives (empty/print_fixed/core_deleted) all FAIL. §4.9 three fake submissions (a empty / b print-expected / c core-deleted) all FAIL. sha256 stable across 2 runs. k_rationale=k_check=15≥8 ✓.
