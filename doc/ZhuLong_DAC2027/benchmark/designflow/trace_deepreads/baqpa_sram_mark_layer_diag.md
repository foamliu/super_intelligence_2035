# deepread: baqpa — SRAM device-recognition mark-layer diff diagnostic

- **session**: `1795076455054_baqpa` · user `e0049141` @ `hfeg0plg54` (10.129.35.73) · mc=83
- **domain**: physical_verify (kw lvs:995 / .spi:376 / pdk:227 / .gds:49 — clean)
- **nmsgs**: 47 / 2 real user_input turns
- **trace_source**: real, ledger claimed r875

## User intent (verbatim)

**U#0** (the primary task — clean single-turn diagnostic):
> `/rundata/lacaa/TV1_DBC/ALS_PDK/lvs/wzliao/lvsqa/ALSQA_LVS_V0.5a_20261117/data/sample_check/CDL/ 在当前路径下，比较8T_HC2P_SRAM_CH_378.gds和8T_HDB2P_SRAM_CH_420.gds这两个gds文件有什吗区别，为什么同一份lvs deck，前面的gds可以抽出器件，而后一份不行？`

意图：同一份 LVS deck，为什么能从 GDS_A (8T_HC2P_SRAM_CH_378) 抽出器件，却不能从 GDS_B (8T_HDB2P_SRAM_CH_420) 抽出？→ SRAM device-recognition mark-layer 差异诊断。

**U#37** (second independent task — not used in this case):
> `/rundata/.../GDS_to_SPI/spi_out 帮我检查一下这里面的spi文件，网表最下面的器件，有SCNNECT的报错的spi文件有多少？帮我列出一个器件的清单。`

## Assistant gold chain (idx 1–34, for U#0)

assistant 写了 7 个 Python 诊断脚本（纯 stdlib GDSII 二进制解析 + deck 文本 grep）：

1. **gds_compare.py** (idx 8) — GDSII 结构比较：cells / layer/datatype usage / texts / srefs / DIFF SUMMARY。
2. **gds_deck_probe.py** (idx 12) — grep LVS deck 找 hdb2p/hc2p recognition + 632/1110/1145/1286/301/AMD/SAAT 关键层 + dump GDS key-layer geometry。
3. **deck_sram_probe.py** (idx 16) — `show_around(SRAM_HDB2P|SRAM_HC2P|SRAMID|sram_pu/pd/pg|AMD_drawing)` 打印 deck 命中块。
4. **deck_sram_probe2.py** (idx 20) — 用 internal layer number (10745/10766/10752/10747) 反查 device formation code。
5. **deck_structure_probe.py** (idx 24) — deck 整体结构：line count / ascii-printable ratio / LAYER MAP 块结束位置 / 采样 / 关键字命中。
6. **deck_filler_probe.py** (idx 28) — `LAYER MAP 0/1104/1136/1106/1286/301/632` + Filler 关键字。
7. **gds_mark_dump.py** (idx 32) — **核心 gold**：dump 632.x SRAM mark geometry + 1104/54 + AMN for both GDS。定义 NAMES 表 {(632,51):SRAMID, (632,53):SRAM_PG, (632,58):SRAM_HC2P, (632,77):SRAM_HDB2P, (632,68):SRAM_11, (632,72):SRAM_RP, (1104,54):GFW_4, (1106,0):AMN, (1136,601):VT_NS, (1136,607):VT_PS, (1110,0):AMD}，解析 GDSII BOUNDARY，per (layer,dtype) polygon count + bbox。

## Key diagnostic finding (gds_mark_dump.py run output, idx 34)

```
A(378 HC2P):
  SRAMID(632,51)    1 poly  bbox x=0..1020  y=-250..3530
  SRAM_PG(632,53)   2 polys
  SRAM_HC2P(632,58) 1 poly  bbox x=0..1020  y=-250..3530   ← present
  SRAM_HDB2P(632,77) 0 polys                                ← absent
  SRAM_11(632,68)   1 poly
  SRAM_RP(632,72)   1 poly
  AMD(1110,0)       2 polys                                  ← present
  VT_NS / VT_PS    0 polys

B(420 HDB2P):
  SRAMID(632,51)    1 poly  bbox x=0..1020  y=-220..3980
  SRAM_PG(632,53)   2 polys
  SRAM_HC2P(632,58) 0 polys                                  ← absent
  SRAM_HDB2P(632,77) 1 poly  bbox x=0..1020  y=-220..3980   ← present
  SRAM_11(632,68)   1 poly
  SRAM_RP(632,72)   1 poly
  AMD(1110,0)       0 polys                                  ← absent
  VT_NS(1136,601)   3 polys                                  ← present
  VT_PS(1136,607)   1 poly                                   ← present
  GFW_4/AMN         5 polys (vs 1 in A)
```

**结论**：两个 GDS 携带不同的 SRAM mark 层 — A 带 SRAM_HC2P (632,58)，B 带 SRAM_HDB2P (632,77)。deck (line 2118-2119 / 2146-2147) 同时定义了 SRAM_HC2P 与 SRAM_HDB2P 的 `LAYER MAP 632 DATATYPE 58/77`，故同一 deck 能识别两种 mark。B 抽不出器件的根因在更深的 device-formation 依赖（B 有 VT_NS/VT_PS 但无 AMD；A 有 AMD 但无 VT_NS）— 本 case 聚焦可复刻的「mark 层差异诊断」部分。

## deck LAYER MAP 632 block (real, lines 2104-2149)

```
LAYER MAP 632 DATATYPE 51    10745
LAYER SRAMID 10745 //SRAM mark layer for all type
LAYER MAP 632 DATATYPE 53    10747
LAYER SRAM_PG 10747 //Define Pass-gate transistors mark layer
LAYER MAP 632 DATATYPE 58    10752
LAYER SRAM_HC2P 10752 //Define two port 8TSRAM CH378 high current mark layer
LAYER MAP 632 DATATYPE 68    10761
LAYER SRAM_11 10761 //Define SRAM bitcell mark layer
LAYER MAP 632 DATATYPE 72    10763
LAYER SRAM_RP 10763 //Define SRAM RP mark layer
LAYER MAP 632 DATATYPE 77    10766
LAYER SRAM_HDB2P 10766 //Define two port backup 8TSRAM CH420 high density mark layer
```
格式：`LAYER MAP 632 DATATYPE N  <internal>` 紧跟 `LAYER <name> <internal> //comment` → (632, N) 映射到 name。

## Case 设计（档 B reframe · fixture-driven judge）

真实 gold 依赖 397×19MB .spf + 1.3MB 加密 deck + 真实 GDS（不可沙盒复现）→ reframe 为 **fixture 驱动 SRAM mark-layer 差异诊断器**：

- **A 可见**：合成小 GDSII `gds_A.gds`/`gds_B.gds`（带 632.x SRAM mark 层 + 几个 extra 层）+ `deck.lvs`（LAYER MAP 632 block）+ task_brief.md
- **B 隐藏**（嵌 check.py）：不同 libname/cell/mark 层 dtype/name/几何 → 反硬编码
- **交付**：`sram_mark_diag.py <gdsA> <gdsB> <deck> [-o out.json]` — 解析 deck `LAYER MAP 632 DATATYPE N`→name 映射 + 解析两 GDSII 的 (632,d) polygon count/bbox + 报告每文件 mark 层 present + diff(only_in_A/only_in_B/common) → JSON
- **判分**：check.py 独立解析 deck2 + GDS_A2/B2，15 条独立断言（a-o）：exit0 / JSON 可解析 / 顶层键 / deck_sram_layers 条数+字段+(632,d)→name 映射 / files.A/B libname+cells / mark_layers 名称集合 / poly_count / diff 三集合 + 反硬编码 A 守卫 + 3-seed + §4.9 三假 + ≥2 negative。

**C 域 physical_verify SRAM device-recognition mark-layer 差异诊断 reframe 子型首例**，与 GdsDirCmpDeepDive(文件级目录比较)/SpfLayerCoupleCapAnalyze(寄生耦合)/LvsSvdbRepDirStat(.rep 目录统计)/LvsPinCaseMismatchDiag(pin mismatch) 正交：本案=对两 GDS 的 SRAM mark 层(632.x)差异 + deck LAYER MAP 映射做结构化诊断的离线复刻。
