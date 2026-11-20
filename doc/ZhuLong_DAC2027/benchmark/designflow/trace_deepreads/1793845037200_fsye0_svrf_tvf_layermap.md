# Deepread: 1793845037200_fsye0 (wei3wei @ hfeg0pkn004) — SVRF/TVF Layer Mapping Framework

- trace: `/home/wei3wei/.cline/data/sessions/1793845037200_fsye0/1793845037200_fsye0.messages.json` (10.129.2.13 = hfeg0pkn004)
- mc=74; keywords drc:398;gdsii:97;calibre:89;.gds:50;lvs:21;pex:1; NEW user (wei3wei)
- 144 msgs; workspace `/home/wei3wei/Dummy_Insert/` (real calibre dummy-fill rule-deck project)
- domain: **physical_verify** (Calibre SVRF/TVF rule-deck framework authoring)

## User intent (2 sequential requests, verbatim)

- msg#0: `编写一段有layer mapping datatype input 与 output的svrf 语言框架`
  → write an SVRF framework template with layer-mapping datatype INPUT (GDS→internal) and OUTPUT (internal→GDS)
- msg#56: `把这段svrf 转化为可 tcl+svrf 语言，其中有 if else endif 等判断和 一些循环语句，另存为一个.tvf 文件`
  → convert the SVRF to TVF (Tcl+SVRF) with if/else/endif conditionals + loop statements, save as .tvf

## Assistant tool chain (real, grounded)

1. `list_allowed_files /home/wei3wei/Dummy_Insert` → found existing rule files
2. `read_files` calibreBEOL_Dummy.rule (2368 lines, `#! tvf` TVF deck) + calibreFEOL_Dummy.rule (1654 lines) + gds.path + outgds_10292026.path → studied real layer-mapping conventions (`LAYER MAP 1 DATATYPE 1 350`, `LAYER MAP 101 DATATYPE 163 3100`, `tvf::VERBATIM { ... }`, `tvf::set_global_variable`)
3. `search_codebase` for "LAYER OUTPUT MAP", "DRC RESULTS DATABASE LAYER", "DATATYPE", "SVRF" → confirmed patterns
4. `editor` create+append `svrf_layer_mapping_framework.svrf` (335 lines, 7 parts) — split into 6 writes (13770-char first attempt exceeded 6000 limit)
5. `editor` create+append `tvf_layer_mapping_framework.tvf` (504 lines, 7 parts) — Tcl if/elseif/else + foreach + tvf::VERBATIM + tvf::set_global_variable + #IFDEF/#ELSE/#ENDIF reference
6. Fixed stray `BLOCK_BASE_NUM` re-declaration (msg#97-118), verified final file (msg#139-142)

## Accepted artifacts (real, on 10.129.2.13)

### `svrf_layer_mapping_framework.svrf` (335 lines, 14556 B) — static SVRF template
- PART 0 Rule Header & README (run cmd `calibre -drc -hier ...svrf`)
- PART 1 Global Settings: `PRECISION 10000`, `RESOLUTION 50`, `DRC RESULTS DATABASE PRECISION 10000`, `LAYOUT SYSTEM GDSII`, `LAYOUT PATH "./input_layout.gds"`, `LAYOUT PRIMARY "*"`, `DRC RESULTS DATABASE "./output_layout.gds" GDSII`, `DRC SUMMARY REPORT`, `DRC MAXIMUM RESULTS ALL`, `DRC KEEP EMPTY NO`, `LAYOUT ULTRA FLEX YES`
- PART 2 Layer Declarations: `LAYER NW_drawn 3000`, `AA_drawn 350`, `PO_drawn 364`, `CO_drawn 3010`, `M1_drawn 3100`, `M2_drawn 3200`, `V1_drawn 5100`, `ChipBoundary 500`, `DummyFill_M1 3101`, `DummyFill_M2 3201`, `Blockage_M1 15001`, `Blockage_M2 15002`
- PART 3 INPUT Layer Mapping (`LAYER MAP gds DATATYPE dt internal LAYER name`):
  - FEOL: NW `LAYER MAP 5 DATATYPE <=1 3000 LAYER NW_drawn`; AA `LAYER MAP 1 DATATYPE <=1 350` + `DATATYPE 20 350`; PO `LAYER MAP 40 DATATYPE <=1 364` + `DATATYPE 20 364`; CO `LAYER MAP 85 DATATYPE 1 3010`
  - BEOL: M1 `LAYER MAP 101 DATATYPE <=1 3100` + `DATATYPE 20` + `DATATYPE 163`; M2 `LAYER MAP 102 ...3200`; V1 `LAYER MAP 121 ...5100`
  - Blockage: `LAYER MAP 101 DATATYPE 3 15001` + `DATATYPE 5 15001`; M2 blockage 15002
  - Chip boundary: `LAYER MAP 183 DATATYPE 4 500 LAYER ChipBoundary`
- PART 4 OUTPUT Layer Mapping (`LAYER OUTPUT MAP internal DATATYPE dt gds NAME "..."`):
  - FEOL: `LAYER OUTPUT MAP 3000 DATATYPE 0 5 NAME "NW_drawn"`; AA `350 DATATYPE 0 1`; PO `364 DATATYPE 0 40`; CO `3010 DATATYPE 0 85`
  - BEOL: `LAYER OUTPUT MAP 3100 DATATYPE 0 101 NAME "M1_drawn"`; M2 `3200 DATATYPE 0 102`; V1 `5100 DATATYPE 1 121`
  - Dummy fill: `LAYER OUTPUT MAP 3101 DATATYPE 2 101 NAME "DummyFill_M1"`; M2 `3201 DATATYPE 2 102`
  - Blockage: `LAYER OUTPUT MAP 15001 DATATYPE 5 101 NAME "Blockage_M1"`; M2 `15002 DATATYPE 5 102`
  - Chip boundary: `LAYER OUTPUT MAP 500 DATATYPE 4 183 NAME "ChipBoundary"`
- PART 5 Alternative `DRC RESULTS DATABASE LAYER internal DATATYPE dt gds` (12 commented examples)
- PART 6 Shorthand & Special Forms reference (DATATYPE qualifiers `<=n`, `>=n`, `n1-n2`, `*`, `default`; TVF-style; `LAYER OUTPUT MAP TABLE`; OASIS)
- PART 7 Placeholder for DRC/ Dummy Fill operations

### `tvf_layer_mapping_framework.tvf` (504 lines, 20846 B) — TVF (Tcl+SVRF) parameterized
- shebang `#! tvf`
- PART 1 USER CONFIGURATION via `tvf::set_global_variable` (IN_LAYOUT_SYSTEM, IN_LAYOUT_PATH, PRECISION_VAL, RESOLUTION_VAL, FILL_FEOL, FILL_BEOL, FILL_DUMMY_METAL, FILL_DUMMY_VIA, ENABLE_OUTPUT_MAPPING, KEEP_EMPTY_CELLS, USE_ULTRA_FLEX, OUTPUT_FORMAT_OASIS, **METAL_LAYER_LIST {101 102 103 104}**, **VIA_LAYER_LIST {121 122 123 124}**, METAL_BASE_NUM 3100, VIA_BASE_NUM 5100, DUMMY_BASE_NUM 3101)
- PART 2 GLOBAL SETTINGS via Tcl `if/elseif/else` outside `tvf::VERBATIM`:
  - `if {$::env(FILL_BEOL) eq "yes"} { tvf::VERBATIM { RESOLUTION 50 } } else { tvf::VERBATIM { RESOLUTION 1 } }`
  - `if {$::env(KEEP_EMPTY_CELLS) eq "no"} {...} elseif {..."yes"} {...} else {...}` → DRC KEEP EMPTY
  - `if {$::env(USE_ULTRA_FLEX) eq "yes"} {...}` → LAYOUT ULTRA FLEX
  - `if {$::env(OUTPUT_FORMAT_OASIS) eq "yes"} {...}` → OASIS output
  - Alternative `#IFDEF/#ELSE/#ENDIF` preprocessor block (commented reference)
- PART 3 LAYER DECLARATIONS via `foreach`:
  - Static FEOL `tvf::VERBATIM { LAYER NW_drawn 3000 ... }`
  - `foreach gdsLayer $::env(METAL_LAYER_LIST) { set internalNum [expr {$::env(METAL_BASE_NUM) + $idx * 100}]; ... tvf::VERBATIM { LAYER $layerName $internalNum } }` → M0_drawn..M3_drawn, DummyFill_M0..M3, Blockage_M0..M3
  - `foreach gdsLayer $::env(VIA_LAYER_LIST) {...}` → V0_drawn..V3_drawn
- PART 4 INPUT LAYER MAPPING:
  - `if {$::env(FILL_FEOL) eq "yes"} { tvf::VERBATIM { LAYER MAP 5 DATATYPE <=1 3000 LAYER NW_drawn ... } } else { puts "Info: FEOL input mapping skipped" }`
  - `if {$::env(FILL_BEOL) eq "yes"} { foreach gdsLayer $::env(METAL_LAYER_LIST) { tvf::VERBATIM { LAYER MAP $gdsLayer DATATYPE <=1 $drawnNum LAYER $drawnName; LAYER MAP $gdsLayer DATATYPE 2 $dummyNum ...; LAYER MAP $gdsLayer DATATYPE 3 $blockNum ...; DATATYPE 5 ... } } } else { puts "Info: BEOL input mapping skipped" }`
  - Chip boundary `LAYER MAP 183 DATATYPE 4 500 LAYER ChipBoundary`
- PART 5 OUTPUT LAYER MAPPING:
  - `if {$::env(ENABLE_OUTPUT_MAPPING) eq "yes"} { ... foreach ... { tvf::VERBATIM { LAYER OUTPUT MAP $drawnNum DATATYPE 0 $gdsLayer NAME "$drawnName" } if {$::env(FILL_DUMMY_METAL) eq "yes"} { tvf::VERBATIM { LAYER OUTPUT MAP $dummyNum DATATYPE 2 $gdsLayer ...; $blockNum DATATYPE 5 ... } } } } else { puts "Info: Output layer mapping disabled" }`
  - Via foreach output `DATATYPE 1`
  - Alternative `DRC RESULTS DATABASE LAYER` (commented)
- PART 6 REFERENCE: DATATYPE qualifiers, TVF-specific notes, OASIS
- PART 7 PLACEHOLDER for DRC/Dummy Fill operations

## Distinctness vs prior shard-C physical_verify cases

- r218 ErcPathchkTopoDiag (ERC PATHCHK topology diagnose) — report PARSING, not deck AUTHORING
- r217 DrcExtendRuleValidator (DRC pattern rule GDS geometry check) — GDS polygon GEOMETRY validation, not layer-mapping deck
- r216 CalibreLvsRepDiag (LVS run-log parse) — LVS REPORT parsing, not SVRF deck
- r208 DrcUnusedVarClassify (DRC variableUnused classify) — DRC variable USAGE analysis, not deck skeleton
- r172b DrcRuleCellMatch (rule→cell match) — rule-cell matching strategy
- r171 DummyHeaderQaResolver (deck header QA) — header SWITCH QA, not full layer-mapping framework
- **本案首次 ground on SVRF/TVF layer-mapping FRAMEWORK generation**: bidirectional layer mapping (LAYER MAP input + LAYER OUTPUT MAP output + DRC RESULTS DATABASE LAYER) + TVF parameterization (tvf::set_global_variable + foreach $::env(METAL_LAYER_LIST) + if/elseif/else toggles + #IFDEF/#ELSE/#ENDIF). Deck SKELETON authoring ≠ report parsing / GDS geometry / variable classify / header QA.

## Case design (B-synthesized, L1-boundary, physical_verify)

- **Deliverable**: submit.zip = {svrf_layer_mapping_framework.svrf, tvf_layer_mapping_framework.tvf}
- **A (visible)**: prompt.txt (2 verbatim requests) + task_brief.md + calibreBEOL_Dummy.rule + calibreFEOL_Dummy.rule (real grounding)
- **Hidden B**: config_B.json — DIFFERENT METAL_LAYER_LIST {91 92 93}, VIA_LAYER_LIST {131 132}, FILL_FEOL=no, FILL_BEOL=yes, ENABLE_OUTPUT_MAPPING=yes, OUTPUT_FORMAT_OASIS=yes, RESOLUTION_VAL=25 → tests the TVF is PARAMETERIZED (uses $::env, not hardcoded 101/102)
- **B_broken sentinel**: config_B_broken.json — FILL_FEOL=no + FILL_BEOL=no + ENABLE_OUTPUT_MAPPING=no → ALL mapping skipped → tests if/else gating
- **Judge (L1, stdlib only)**: static structural validation of .svrf + .tvf (required statements/constructs) + parameterization checks (TVF uses $::env in foreach/if, NOT hardcoded A literals) + cross-input guard (TVF foreach bodies don't hardcode 101/102/103/104) + B_broken sentinel (TVF has else-branch skip for FILL_FEOL/FILL_BEOL/ENABLE_OUTPUT_MAPPING)
- **14 条断言 (a-n)**: see check.py
