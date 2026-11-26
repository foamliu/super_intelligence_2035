# r415 peek notes — 11/09 scan mid-mc [40,120] C-dominant by C-affinity (fresh check)

**Round**: r415 (2026-11-12, shard C maintenance + 讨论配额付清)
**Purpose**: r414 closed the 2×2 matrix (scan × mc-segment: 11/05 high+low / 11/09 high+low) with 8 low-mc peek all REJECT. r415 extends with a **new angle**: 11/09 mid-mc [40,120] sorted by **C-keyword affinity (C_sum)**, not by raw mc. This segment was not explicitly covered by r413 (11/09 high-mc top 4 by mc) — r413 sorted by mc, r415 sorts by C_sum, surfacing different candidates.

## Method

1. 11/09 scan, mc∈[40,120], compute C_sum (aether/pyaether/layout/lvs/drc/calibre/pexivirtuoso/virtuoso/.gds/.lef/cellview/dbopencellviewbytype/dbcreaterect/dbcreatelabel/dbopencv/skipper/pdk) and WSKW (verilog/netlist/hspice/spice/finesim/.fsdb/waveview/schematic/.cdl/cmos/analog/systemverilog/.spi/synopsys/rtl).
2. Filter C_sum≥30 AND C_sum≥WSKW (C-dominant).
3. Sort by C_sum desc, head 5 distinct slugs.
4. Cross-check each against 4-shard ledger (2621 slugs).

## Peek results (top 5 by C-affinity, ALL ledgered)

| # | slug | user | mc | C_sum | kw (top) | ledger status |
|---|---|---|--:|--:|---|---|
| 1 | 1793264175600_ocmhu | jkxu | 57 | 9289 | drc:9289;verilog:6795;cadence:39 | **C-ledgered** (line 513). jkxu = r414 lf1ny same user (Q&A dir-review) |
| 2 | 1793152046824_iacrk | zhiguo1w | 117 | 7649 | drc:7521;calibre:97;.gds:31 | **C-ledgered** (line 490) |
| 3 | 1789713772472_fzq12 | xinqiaoz | 117 | 3837 | drc:2274;pdk:1456;calibre:96 | **C-ledgered** (line 138). xinqiaoz = heavy user (x4b0p/58vqx already cased) |
| 4 | 1793586676522_9kzwd | ericw | 78 | 3366 | drc:3363;verilog:1681;pyaether:3 | **C-ledgered** (line 536). ericw = LEF QA user (r414 5avgh near-dup) |
| 5 | 1789520357933_3duob | ellawu | 63 | 3342 | .gds:1905;drc:768;calibre:540;aether:114 | **C-ledgered** (line 137). ellawu = 9-case heavy user (implant-fill archetype) |

**Supplement — high-mc top 12 (mc-sorted, cand2.sh head 60)**: ukkn7/w4x70/x4b0p/aneeo/m2vah/9knot/aftvk/58vqx/7rzyf/as67p/cgqd1/mt7ua. 11/12 C-ledgered; the 1 non-C-ledgered (`as67p` easont netlist:2323) is **wrong-shard** (D-domain netlist/waveform dominant). The 1 non-all-4-ledgered mid-mc C-dominant candidate `38unc` (e0047695 virtuoso:338;aether:173) is **parked by B+D as unfit** (B: "sysadmin: adjust display"; D: "peek_D269_unfit").

## Conclusion

**11/09 mid-mc [40,120] C-affinity segment saturated**: top 5 by C_sum ALL C-ledgered; top 12 by mc ALL C-ledgered except 1 wrong-shard; the only cross-shard-fresh C-dominant candidate (38unc) is already parked unfit by 2 other shards.

**r404-r415 = 10 连续维护轮**，peek 50+ fresh-against-all-4 候选全 REJECT，饱和结论第 10 次独立复验。覆盖矩阵现在 3 维饱和：scan(11/05+11/09) × mc-segment(high+mid+low) × sort-key(mc+C-affinity)。

**binding constraint 确认**（与 shard A r382 / C r414 一致）：C 域 fresh 候选的主题已被现有 308 case 覆盖 —— ellawu implant-fill 4+ case / xinqiaoz drc-calibre-pdk 多 case / ericw LEF QA / zhiguo1w drc-batch。高 C-affinity 候选 100% 是已 ledgered 重用户的新 session（同 archetype 变体）。非重用户的 fresh 低 C-affinity 候选（r414 peek 8）全是 Q&A/debug/env-setup/wrong-shard。

**mc-matrix 凭据**（user 令 rule 4）：`trace_ledger.py --shard C mc-matrix --src designflow/summary_1105.tsv` → mc≥10 fresh=267≠0（不写池耗尽）。池数量未枯竭，但 fresh 候选主题饱和（archetype 覆盖 + 非重用户 fresh 非 produce-task）。

**shard A 尚未换池 11/05→11/09**（`summary_stats.json.mc_matrix.src` 仍 = `designflow/summary_1105.tsv`，r415 复核）。换池是潜在 unblocker（待 A 执行）；本 r415 用 11/09 scan raw summary.tsv 预筛，结论与 11/05 一致（饱和），换池预期不改变 binding constraint。

## Action

0 case。未 claim 新 session（ledger_C 698 不变），jsonl_C 308 不变。不建 assets/reference 目录。本轮交付物 = 讨论配额帖（discuss/C.md r415，2D fixability 轴修正 D r532）。等 shard A 换池 11/05→11/09 后再筛；或等新 archetype 授权；或 C 线 pilot「drive-produce, verify-by-artifact」layout_aether case（r415 帖建议动作 4）。
