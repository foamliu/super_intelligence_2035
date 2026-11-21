# trace deepread — r937 jatet (ViaLayerMapExtract-001)

- **trace**: `1793956475658_jatet.messages.json` (e0024852 @ hfeg0pkn004, mc=143, 172 msgs, 618KB)
- **keywords**: pyaether:252; lvs:151; aether:149; drc:103; .gds:54; calibre:50; pex:28
- **session**: e0024852 reviewing 35H 1P18M Calibre LVS deck

## 用户真实意图 (U#88, msg 158, verbatim)
> "V0D/V0G/V0R/V1/Vxa/Vx/Vxb represent which layer to which layer"

用户看了 LVS deck 的 VIA 层定义后，问每个 via 名对应的 from→to 层映射。

## assistant 工具链
- grep LVS deck (`grep_via.sh`/`grep_via2.sh`/`grep_via3.sh`) 找 LAYER name defs + LAYOUT BASE LAYER order + tran.map
- msg 170: grep 得到 V0D/V0G/V0R 注释 ("Via contact hole landing on GT/M0 drawing layer")
- msg 166: grep 得到 V1/V2/V3/V4 定义 ("main pattern drawing layer")
- msg 171: **最终答案** — 完整 via→layer 映射表

## trace gold (msg 171, assistant 最终答案)

| Via | From → To | Purpose | Evidence |
|---|---|---|---|
| V0D | AA(diffusion) → M0 | source/drain contact hole | "Via contact hole landing on M0 drawing layer" (line 748) |
| V0G | GT(Poly) → M0 | gate contact hole | "Via contact hole landing on GT drawing layer" (line 736) |
| V0R | M0 → rail | rail-type contact | "Rail-type Via contact hole landing on M0 drawing layer" (line 746) |
| V1 | M1 ↔ M2 | BEOL Via-1 | V1 between M1 and M2 in LAYOUT BASE LAYER (line 788) |
| V2 | M2 ↔ M3 | BEOL Via-2 | (line 838) |
| V3 | M3 ↔ M4 | BEOL Via-3 | (line 894) |
| Vxa/Vx/Vxb | via variants | mask-split variants | V2_drawing_xa, V3_drawing_x, V4_drawing_xb (same from→to as base) |

## LVS deck 关键行 (从 trace 提取)
- Line 476: `LAYOUT BASE LAYER AA_drawing GT_drawing AMN_drawing M0_drawing V0D_drawing V0G_drawing V0R_drawing NSR_drawing PSR_drawing M1_drawing V1_drawing M2_drawing V2_drawing M3_drawing V3_drawing M4_drawing V4_drawing_xb`
- Line 736: `LAYER V0G_drawing 10060 //Define Via contact hole landing on GT drawing layer`
- Line 746: `LAYER V0R_drawing 10065 //Define Rail-type Via contact hole landing on M0 drawing layer`
- Line 748: `LAYER V0D_drawing 10066 //Define Via contact hole landing on M0 drawing layer`
- Line 788: `LAYER V1_drawing 10086 //main pattern drawing layer`
- Line 838: `LAYER V2_drawing 10111 //main pattern drawing layer only for TV0`
- Line 840: `LAYER V2_drawing_xa 10112 //V2 pattern drawing layer`
- Line 894: `LAYER V3_drawing_x 10139 //V3 main pattern drawing layer`
- Line 922: `LAYER V4_drawing_x 10153 //V4 main pattern drawing layer`
- Line 924: `LAYER V4_drawing_xb 10154 //V4 main pattern drawing layer`

## reframe (r937 build)

**case_id**: EDA-Eval-DesignFlow-ViaLayerMapExtract-001 (physical_verify, L1 fixture-driven)
**子型**: `lvs-deck-via-layer-map-extract` (knowledge-retrieval + structured-extraction)

- **env_A** = lvs_deck_A.svrf (35H 1P18M, 9 vias: V0D/V0G/V0R/V1/V2/V2_xa/V3_x/V4_x/V4_xb)
- **hidden B** = lvs_deck_B.svrf (28H 1P12M, 8 vias: CA/CG/CR/VA1/VA2/VA2_a/VA3_b/VA4, 全异 via 名/层名/注释)
- **hidden B2** = lvs_deck_B2.svrf (22H 1P8M, 0 vias — 退化 fixture)
- **candidate**: via_layer_map.py (stdlib) — 解析 deck, 分类 layer, 输出 JSON {summary, via_map[]}
- **check.py**: 16 独立条件 (a-p)
- **negatives**: 3 (naive_empty→b / naive_print_A→d / neg_delete_core→h), 3 distinct teeth

## 自验结果
- ref PASS 16/16 ✓
- 3 neg FAIL distinct teeth (b/d/h) ✓
- §4.9 (a)(b)(c) 三假全 FAIL ✓
- 3-seed determinism sha256 b488c645... byte-identical ✓
- k_rationale == k_check == 16 ✓

## cross-shard 串台检查
- jatet 在 B ledger parked (wrong-shard, 2026-11-09) — B 识别为 C 域但未造
- C r937 用 --force claim/mark (cross-shard revival per 11-15 reaudit)
- 4-shard jsonl 无 jatet trace_source
- 同 domain (physical_verify) 已落库 case 全正交 (无 via-layer-map-extract 子型)
