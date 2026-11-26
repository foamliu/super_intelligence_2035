# Deepread — sid `1786613295407_a9ta2` (autovia + powerfill cell removal)

- User: e0014566  · Host: hfeg0pkn005  · match_count: 131  · 101 msgs · ~680 KB
- Domain: **layout_virtuoso** (Virtuoso SKILL)
- Source turn (U0, verbatim):
  > 请你识别到 Library: auto_austin_case1, cell: BCenterR_rscalc, 中 layout 的布局，识别出 autovia 和 powerfill 生成的cell, 并把这些 cell 去除。
- Case built: `EDA-Eval-DesignFlow-AutoViaPwrFillCellRemove-001` (round 185, shard C).
- A-档 fitness: U0 is a pure "提出需求/表达目标" turn — user names the library/cell and the goal (identify+remove auto-generated autovia & powerfill cells); user does NOT supply root cause or fix. ✅ faithful.

## What the trace actually did

Target cellview: `auto_austin_case1/BCenterR_rscalc` (layout view). 25 top-level instances. The assistant's SKILL flow:

1. `geOpenLib` + `geOpenCellView` on the cell.
2. `dbGetq` over top-level instances (`cv~>instances`), collected `inst_name`/`lib`/`cell`/xy/transform for all 25 (`I0`–`I_BCR_power_improve_wf_1`).
3. For each instance, opened its master cellview and dumped discriminators:
   - **sub_cells** (`master~>cellView~>instances`): nested auto sub-cells.
   - **LPPs/purposes** (`shapes~>purpose`, `lpp`): drawing vs DUMMY.
   - **viaHeaders / via arrays** (`figs~>viaHeader`): TECHLIB auto-via markers.
   - **cvProps** (`cellView~>prop~>name/value`): CatenaDesignType / auto-gen flags.
4. Classification logic actually used by the assistant (paraphrased from the SKILL reasoning in the trace):
   - **autovia** = instance whose master has ≥1 sub-cell whose **cell name matches a `*_VIA_TOP` / `*_auto_pc` pattern** AND whose shapes are *via-only* (no metal drawing LPP). Concretely in A: `BCenterR_2025069_VIA_TOP` (17 VIA-only sub-cells) and `BCenterR_PCUCT_20250702_auto_pc` (13375 vias, `TECHLIB`/`PCU_N_P` viaHeader) → instances **I4, I6**.
   - **powerfill** = instance whose master is dominated by **non-drawing-purpose shapes** (purpose=DUMMY / DUMMY2) AND/OR PG-style LPPs (`AT4`/DUMMY2). Concretely in A: `BCenterR_auto_pgdm` (PG/DUMMY + AT4/DUMMY2 LPPs) and `BCR_power_improve_wf` (156 non-drawing-purpose shapes) → instances **I5, I_BCR_power_improve_wf_1**.
   - **Kept (traps)**: `BCenterR_Power` (CatenaDesignType=asic, M3LANE/drawing — *real* metal LPP, name misleading), `Pump_power_R` (M5/pin — real), `Bcenter_R_rt_wf` (16 switch sub-insts, `wf` name misleading but real), top-level `BCenterR_RT`/`T_SealRingDet`/`AG_AnalogChRPowers` (top-level inst is real even though sub-cells are auto).
5. `dbDeleteObject` on the 4 identified instances → `dbSave` → re-query top-level → **21 remaining** (25 − 4). Confirmed by counting `cv~>instances` again post-delete.

## Inventory extracted from real SKILL tool_result `print_log` fields

Saved to `benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-AutoViaPwrFillCellRemove-001/inventory_A.json` (25 insts). Each entry carries: `inst_name`, `lib`, `cell`, `xy`, `transform`, `sub_cells[]` (with their cell name + lpp/purpose summary), `lpp_count`, `purposes[]`, `via_count`, `viaHeaders[]`, `cvProps{}`. Verified against msgs 53/57/63/65/67/71/73/75/77/81/83/85/93/97.

## Hidden B / B2 (synthesized from same trace, different values/structure)

- `inventory_B.json` — `TCenterL_rscalc`, 24 insts. Gold removed: autovia `[I7, I9]`, powerfill `[I8, I_TCR_power_improve_wf_2]`. Same SKILL discrimination rules; cell/inst names rotated; trap cells kept (T_BCR_power-style real LPP, T_PumpPower-style pin, T_rt_wf sub-insts).
- `inventory_B2.json` — `TopR_rscalc`, 12 insts (edge variant). Traps: a **hand-designed** VIA-named cell `AG_AnalogChRBuf_VIA_manual_hand` (cell name matches `*VIA*` but its sub-cells are NOT VIA-named and it has real metal drawing LPPs) must be **kept**; a power-named `TopR_power_improve_wf` carrying DUMMY-LPP auto fill must be **removed** as powerfill. Gold removed: autovia `[I3, I5]`, powerfill `[I_auto_powerfill_wfill_2, I_TopR_power_improve_wf_1]`.

## L1-boundary framing (why this is L1 not L0)

A live SKILL sandbox in the eda_flow session loaded Virtuoso then "ARGUS will close server" — stdout capture failed; pyAether sandbox also connection-refused. So the deliverable is a **pure-stdlib classifier script** operating on the extracted inventory JSON (the same data the assistant's SKILL actually inspected), producing a `removal_manifest.json` of `{removed:[{inst_name,lib,cell,category,reason}], summary:{...}}`. This tests the *discrimination logic* (the L1-relevant skill) without requiring a live EDA daemon — matches §3 L1-boundary definition.

## check.py gate (14 conditions, k=14)

- ①(a) deliverable submit.zip contains `classify_autovia_powerfill.py` ≥200B, py_compile OK, pure stdlib (no pyAether/socket/urllib/requests), no B/B2 gold literals hardcoded.
- ②(b) runs on B → exit 0 + valid `removal_manifest.json`.
- ③(c) manifest schema: `removed`(list)+`summary`; each item has `inst_name`/`cell`/`category`/`reason`; `category∈{autovia,powerfill}`.
- ④(d) B autovia set == gold {I7, I9}.
- ⑤(e) B powerfill set == gold {I8, I_TCR_power_improve_wf_2}.
- ⑥(f) B no false positives (kept insts unmarked).
- ⑦(g) B no false negatives (all gold removals present).
- ⑧(h) B per-item category label correct (autovia↔powerfill not swapped).
- ⑨(i) B total removed count == 4.
- ⑩(j) B2: hand-designed VIA-named cell `AG_AnalogChRBuf_VIA_manual_hand` (sub-cell not VIA-named) kept — trap survives.
- ⑪(k) B2: power-named DUMMY-LPP fill flagged powerfill; B2 autovia+powerfill sets == gold.
- ⑫(l) A run matches A gold (autovia=[I4,I6], powerfill=[I5,I_BCR_power_improve_wf_1]).
- ⑬(m) determinism: 3× rerun on B → manifest sha256 identical.
- ⑭(n) each `reason` non-empty and references a real content feature (LPP/DUMMY/via/VIA/sub/shape/PCU/TECHLIB/purpose/header).

Self-test: ref solution PASS (exit 0); 5 negatives (empty, print_expected, core_deleted, hardcode_b, naive_name_only) all FAIL; §4.9 (a)(b)(c) three-false all FAIL.

## Files

- `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_C.jsonl` (line 180) — case entry.
- `benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-AutoViaPwrFillCellRemove-001/` — `prompt.txt`, `task_brief.md`, `inventory_A.json`, `hidden/inventory_B.json`, `hidden/inventory_B2.json`, `hidden_manifest.json`.
- `benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-AutoViaPwrFillCellRemove-001/` — `check.py` (sha `3cb30e254648a17c`), `classify_autovia_powerfill.py` (ref), `negative/` (5 negs + selftest).
