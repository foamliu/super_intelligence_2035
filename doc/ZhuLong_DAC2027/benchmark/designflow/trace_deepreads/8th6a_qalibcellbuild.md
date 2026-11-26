# Deepread — 1790235770906_8th6a (kenwang @ hfeg0pkn004, mc=407)

**Source**: cline session `/home/kenwang/.cline/data/sessions/1790235770906_8th6a/1790235770906_8th6a.messages.json`
**nmsgs**: 387, 13 user turns. **Domain**: schematic_netlist (library/cellview build via SKILL).
**Tool chain**: Virtuoso IC617 + SKILL (dbCreateRect, dbOpenCVByType, dbNewCellView, strmOut), GDS I/O.

## User intent (turn 0, 提出需求)
> 请访问 /home/kenwang/.cline/scripts/data/autoPattern.md … 现在需要继续针对遇到的问题进行 debug，暂时支持 6.17 版本，就在 617 版本中绘制 QA pattern，需要将 techfile 做相应更新吗，我们创建的 gds pattern 不在 35H_DBC library 中，我们创建一个新的 library，只用一个 techfile，取 library name 为 35H_DBC_QA.

Goal: create a NEW Virtuoso library `35H_DBC_QA` with a single techfile, and draw DRC QA pattern cells (good/bad GDS patterns) in IC617.

## Flow (assistant tool chain)
1. Read autoPattern.md (project doc: DRC QA pattern auto-generation, Phase 1 design-rule parse done, GDS generator dev-in-progress).
2. Explore AutoPattern project structure (`/home/kenwang/workplace/AutoPattern/QA_pattern_auto/DRQA_Phase1_Release_v0.3/`).
3. Generate SKILL script to create library + attach techfile + create cells + draw rects (dbCreateRect on layout views) + stream-out GDS.
4. Iterate debugging SKILL errors reported by user:
   - `*Error* if: too many arguments (missing then?)` — SKILL if-syntax bug
   - `*Error* eval: undefined function - strmOut` — strmOut not available in IC617 (use strmOutSourcing or dbWriteGDS)
   - `*Error* DRQA: refusing to modify existing cellview 35H_DBC_QA/AA_W_1_good/layout` — must delete existing CV before recreate
   - step2 ran with no error but no GDS output, no library created → script not actually loaded/run
5. User feedback on produced patterns (turn 254): bad pattern missing bad-marking layer; need more shape variety; patterns must be side-by-side (not diagonal).
6. User asks to read reference GDS `/rundata/lacaa/TV1_DBC/ALS_PDK/drc/qa_pattern/DBC/4.5.8_AA/AA_DBC.gds` for the W_1 drawing recipe.
7. Final: user asks to summarize the conversation into `Auto_pattern_AA.md`.

## Key produce structure (extracted for B-grade synthesis)
- **dbCrtLib**(libName) → create new library
- **aeAttachTech**(lib, techfilePath) → attach techfile
- Per cell: **dbNewCellView**(lib, cell, "layout", "maskLayout") or aeOpenDesign(edit) → **dbCreateRect**(cv, layer, bBox) to draw patterns → save
- GDS stream-out (strmOut) — IC617 lacks strmOut, worked around

## B-grade synthesized case (QaLibCellBuild-001)
The trace's core produce = "create new library + techfile + multiple pattern cells via EDA API + save each". Synthesized as a **pyAether** schematic-build case (mock-stub offline judging, per #390 pattern):
- Candidate writes `build_lib.py` that reads `spec.json` (lib/techfile/cells[]), calls `dbCrtLib` + `aeAttachTech`, then per cell: `aeOpenDesign`→`dbCreateInst` (stdcell masters)→`dbCrtNet`→wire term.net→`dbCrtTerm` IO→`aeSaveDesign`.
- Hidden B spec (QA_Lib_B: Buf2x=2×invx1 chain, AndOr1=and2Lx1+or2Lx1 tree) differs from visible A (QA_Lib_A: Buf3x=3×invx1, NandTie=nand2Lx1) → anti-hardcode.
- Mock (`pyAether_mock.py`) records per-cell structure to `__recording__.json`; check.py asserts 16 conditions (a-p).

## Faithfulness note
Trace used SKILL/dbCreateRect on LAYOUT views (DRC QA GDS patterns). Synthesized case uses pyAether on SCHEMATIC views (stdcell instance placement + net wiring) — same *structural pattern* (new lib + techfile + multi-cell build + save) but different view-type/API. This is B-grade synthesized (spec-driven, structure-faithful, not literal trace). .75→local file transfer unreliable (per #382) so mock-stub offline judging (not real Aether run).
