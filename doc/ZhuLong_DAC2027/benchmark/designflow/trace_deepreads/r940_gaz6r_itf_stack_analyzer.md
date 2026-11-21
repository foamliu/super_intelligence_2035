# Deepread — 1791964484349_gaz6r (jaceyx @ hfeg0plg90, mc=86, layout_aether→physical_verify)

**11-15 §二 revival**: pre-11-15 r? parked "Q&A session, 0 write ops, no deliverable" → revived (doc-search/Q&A legal per 11-15).

## Trace skeleton (77 msgs, 49 user / 28 assistant, 545KB)
- agent: lead; sessionId 1791964484349_gaz6r; cwd /home/jaceyx
- Two Q&A threads (pure doc-search, no writes):
  1. **U#0 "怎么书写ITF"** (how to write ITF) — assistant RAG-searches pyAether/SKILL APIs (`RAG_MCP_Server__search_apis` ×8, `get_api_details` ×2), reads PDK files on Desktop (readme, layer.map, libInit.ils, mos/ntk.il, mos/ptn.il, example.txt, t1, tes, tet.rule._CL_), searches codebase ×6, fetches Cadence QRC tech-file PDF. **Gold answer msg[62]**: ITF = Interconnect Technology File for parasitic extraction (StarRC/lpe_star), 4 core sections — Technology / ConductingLayer / ViaLayer / DielectricLayer — with full syntax for each, plus a minimal M1/M2/V1 stack example and a Python auto-gen script.
  2. **U#63 "啥是inline data"** → U#69 "你这么说不对" → U#71 "不对，我想了解什么是inline，以及inline data 和 其他data有啥区别" → U#73 "你只从英文方面去了解 是不对的" → U#75 "inline data 和 short loop 跑出来的data有啥区别". Assistant iterates: msg[68] ITF-context inline (CouplingModel tables) → msg[70] SVRF LAYER inline → msg[72] general "in-line" concept → **msg[74] correct**: inline data = in-line metrology data (产线在线测量数据: film thickness, sheet resistance, CD, dielectric constant, via resistance). msg[76]: inline data = measured on product wafer during full flow; short loop data = test wafer running partial process modules.

## Gold reference (msg[62]) — ITF 4 sections
- **Technology** (file header): `Technology: legend, TopDielectric: <num>, Substrate: <num>, condMin: <num>, minPerfSize: <num>, Truncate: no`
- **ConductingLayer** (metal/poly): `Name`, `Unit: MICRON`, `Thickness`, `Bottom/Top` (Z coords), `ResultUnits`, `Resistance { Unit: SQUARE MaxTemp: <n> Capacity: TEMP_C(<rs> ohm/sq, REL_TOL(<x>), T1(...), T2(...)) }`, optional `Capacitance { Factor, CouplingModel { Width/Spacing tables, Area/Perimeter } }`
- **ViaLayer** (via): `Name`, `Bottom: <cond_name>`, `Top: <cond_name>` (referential), `Thickness`, `Bottom/Top` Z coords, `Type: <name> { ResistanceFactor, Resistance { Unit: OHM Capacity: TEMP_C(<r> ohm, REL_TOL) }, point: <x> <y> ×4 }`
- **DielectricLayer** (inter-metal dielectric): `Name`, `Bottom: <cond_name>`, `Top: <cond_name>` (referential), `Thickness`, `Bottom/Top` Z coords, `eps: <k>`, `PGE: 0, PES: 0`, `Capacitance { Factor, model { Name, eps, Width/Spacing tables } }`

## Key consistency rules (assistant articulated msg[62] "书写 ITF 的通用步骤")
1. ConductingLayer Name globally unique; Bottom < Top; Z monotonic increasing upward.
2. ViaLayer/DielectricLayer Bottom/Top must reference valid ConductingLayer Names (not numbers).
3. Top - Bottom == Thickness (or tool uses Top-Bottom).
4. Unit/ResultUnits: MICRON; Resistance Unit: SQUARE (conductor) or OHM (via).
5. Every inter-metal gap needs a DielectricLayer.
6. Layer names must match starrc_mapping/lpe_star mapping.

## Reframe: `itf_stack_analyzer` (fixture-driven, doc-search/Q&A revival, C 域首例 ITF 解析)
- **Real task**: user wants to understand ITF structure → agent explains 4 sections + syntax + consistency rules (gold msg[62]).
- **Mock reframe (track B, L1)**: solver writes `itf_analyzer.py` reading an ITF file → parses 4 section types → extracts structured fields (Technology header, ConductingLayer{Name,Thickness,Bottom,Top,sheet_resistance}, ViaLayer{Name,Bottom,Top,Resistance,points}, DielectricLayer{Name,Bottom,Top,Thickness,eps}) → validates referential integrity (via/dielec Bottom/Top ∈ ConductingLayer names) + Z-continuity → emits JSON report.
- **env_A (visible)**: CXMT-memory-style ITF (3 conductors M1/M2/M3, 2 vias V1/V2, 3 dielectrics D1/D2/D3, Technology header), faithful to trace PDK context (M1~M5/V1Cut~V5Cut) and msg[62] syntax.
- **hidden B**: 28nm-logic-style ITF (4 conductors MT1-MT4, 3 vias VA1-VA3, 4 dielectrics DI1-DI4, different Technology header values, different thickness/eps/resistance values, different Z coordinates) — names + numbers fully disjoint from A (anti-hardcode).
- **hidden B2**: minimal 1-conductor ITF (edge case: 0 vias, 0 dielectrics) — graceful handling guard.
- **k=14 teeth** (≥8 GATE): [a]zip+py_compile [b]--help/no-arg no traceback [c]B exit0+JSON [d]B Technology fields match [e]B ConductingLayer count [f]B ConductingLayer Name+Thickness+sheet_resistance per layer [g]B ConductingLayer Bottom/Top extracted + Top>Bottom [h]B ViaLayer count [i]B ViaLayer Bottom/Top refer to valid ConductingLayer names [j]B ViaLayer resistance (ohm) extracted [k]B DielectricLayer count [l]B DielectricLayer eps extracted [m]B DielectricLayer Bottom/Top refer to valid ConductingLayer names [n]B2 minimal ITF exit0+empty via/dielec lists.
- **Negatives**: naive_empty→tooth-c (no stdout); naive_print_A→tooth-d/e (B values differ); neg_delete_core→tooth-e/h/k (counts 0).

## Distinct vs prior C cases
- r934 DrcSvrfSetlayerExplain = single SVRF LAYER rule parser; this = ITF 4-section stack parser (different format, referential integrity, Z-continuity).
- r936 SpacePatternPlanner = SKILL DRC space-pattern planner; this = ITF structure extraction.
- r937 ViaLayerMapExtract = LVS deck via→layer map; this = ITF stack (ConductingLayer/ViaLayer/DielectricLayer) parser with referential integrity.
- **C 域首例 ITF (Interconnect Technology File) 解析 case**.
