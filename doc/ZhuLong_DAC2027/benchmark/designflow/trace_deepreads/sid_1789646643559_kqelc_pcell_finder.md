# Deepread — sid 1789646643559_kqelc (hbpeng @ hfeg0pkn005, mc=130, 316 msgs/1.4MB, deepseek-v4-flash)

**Source**: `.75` ssh → `hfeg0pkn005:/home/hbpeng/.cline/data/sessions/1789646643559_kqelc/1789646643559_kqelc.messages.json` (1.47MB, 316 msgs). Archive also present (`.messages.archive.json` 3.7MB).

## Session shape
- USER#0 (msg 0): context-summary auto-turn ("check current state of both files … comparison tool from scratch") — inherited from a prior techcmp.py editing thread.
- USER#3 (msg 6): **「请基于pyaether开发一个脚本，找出一个topcell里用到所有pcell」** ← pure intent, no root-cause/fix given → **A-faithful qualified seed** (layout_aether).
- USER#4 (msg 78): 「基于ANTLR4实现tcl代码转skill代码」 — separate SE task (not EDA-tool, not used).

## Real tool chain (USER#3 sub-thread, msgs 6–77)
Assistant did **25 RAG_MCP_Server__search_apis** + **7 get_api_details** calls querying pyAether APIs, then wrote `/home/hbpeng/find_pcells.py` (4136 bytes) via editor. API discovery progression:
1. `aeGetCurDesign` / `mdeGetCurrentLibCellView` / `dbOpenCellViewByType` — get current design + lib/cell/view.
2. `design.block` (emyBlock) / `block.getInsts()` (emyCollection_emyInst_emyBlock) — enumerate instances.
3. `emyCollection` python iteration (`for inst in collection`).
4. `dbCheckIsPCell(inst=inst)` — **the** pcell predicate.
5. `inst.name` / `inst.cellName` / `inst.libName` / `inst.viewName` — instance/master properties.

## Gold deliverable (find_pcells.py, msg 73 editor write)
```python
design = pya.aeGetCurDesign()
block  = design.block
insts  = block.getInsts()
for inst in insts:
    if pya.dbCheckIsPCell(inst=inst):
        pcell_found.append((inst.name, inst.libName, inst.cellName, inst.viewName))
# prints: total_insts, pcell count, table(实例名称|Master Lib|Master Cell|Master View), summary
```
Assistant summary (msg 77): "脚本基于 pyAether API … 找出一个 top cell 中所有用到的 Pcell 实例" — user accepted (no further correction in thread).

## Case synthesis decision
- **Track**: B-档 synthesized, **layer L1-boundary** (same口径 as r146 OALibReadinessReport / r149 SchDigitalAnalogClassify).
- **Why not A-faithful full / L2**: SUT sandbox has no live pyAether / RAG_MCP_Server / opened Aether cellview (Aether probe on .75 timed out twice during this round — license/init). Faithful reproduction impossible. Bundle the `block.getInsts()` + `dbCheckIsPCell()` result as an instance-inventory JSON (`is_pcell` field = dbCheckIsPCell result); SUT writes `find_pcells.py` that parses the bundle + emits `pcell_report.md`.
- **Crux (anti-naive)**: pcell decided **only** by `is_pcell` field, NOT by lib/cell name — `TECHLIB` contains a non-pcell hard macro `io_pad`; `analogLib` contains a pcell `rnpoly`. Defeats `naive_libonly` and `naive_nameguess`.
- **Hidden inputs** (base64-embedded in check.py, NOT in SUT sandbox): B1 = `ioLib/ldo_top` (33 insts, 15 pcells: ntn_m/ptk/bjtpnp10a36/cpoly), B2 = `rfLib/rf_amp` (21 insts, 9 pcells, cross-input guard), B3 = malformed (exit1).

## Verification (local offline, no .75 needed)
- REF `check()` PASS 14/14 (a–n).
- `negative_selftest` NEG_RC=0 (5/5 fakes FAIL): fake_empty→(b), fake_print_expected→(d), fake_core_deleted→(f), naive_libonly→(f), naive_hardcode_a_masters→(f).
- §4.9 three fakes (empty / print-expected / core-deleted) all FAIL ✓.
- REF-on-A: `Cell=analogLib/amp_top Total=16 Pcell=6 NonPcell=10` ✓.
- test==disk check.py md5 match.

## k-assertion gate
k_rationale = k_check = 14 ≥ 8 ✓ (labels a–n).
