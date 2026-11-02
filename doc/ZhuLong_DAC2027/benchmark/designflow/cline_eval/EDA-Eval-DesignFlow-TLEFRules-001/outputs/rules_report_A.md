# 工艺技术文件（Tech LEF）布线规则汇总报告

- 文件：`assets/tech_thk2d0_m5.lef`
- LEF 版本：5.7
- 单位：`DATABASE MICRONS 4000`（文件内尺寸数值单位均为微米 µm），`MANUFACTURINGGRID 0.00025`
- 统计：走线层 7 个，通孔层 8 个，过孔定义 14 个，过孔规则 5 个

---

## 1. 走线层布线规则（Routing Layers, TYPE ROUTING）

| 层 | 方向 | 线宽 (µm) | Pitch (µm) | 最大线宽 (µm) | 最小面积 (µm²) | Offset (µm) | 间距规则 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| C4_bump | VERTICAL | 15.0 | 20.0 | – | – | – | SPACING 9.0 |
| M1 | HORIZONTAL | 8.88 | 9.76 9.76 | 12 | 4 | 0.88 0.88 | SPACINGTABLE |
| M2 | VERTICAL | 8.88 | 9.76 9.76 | 12 | 4 | 0.88 0.88 | SPACINGTABLE |
| M3 | HORIZONTAL | 0.88 | 1.76 1.76 | 12 | 4 | 0.88 0.88 | SPACINGTABLE |
| M4 | VERTICAL | 0.88 | 1.76 1.76 | 12 | 4 | 0.88 0.88 | SPACINGTABLE |
| M5 | HORIZONTAL | 0.88 | 1.76 1.76 | 12 | 4 | 0.88 0.88 | SPACINGTABLE |
| RDL | VERTICAL | 3 | 6 | – | – | 2 | SPACING 3 |

补充：
- M1/M2 节距 9.76 µm，M3/M4/M5 节距 1.76 µm；M1–M5 最小面积均为 4 µm²、最大线宽均为 12 µm。
- 方向交替：M1/M3/M5 为 HORIZONTAL，M2/M4 为 VERTICAL；C4_bump、RDL 为 VERTICAL。
- 各层 `RESISTANCE RPERSQ`：M1–M5 为 0.01，RDL 为 0.012；`THICKNESS`：M1–M5 为 2.0，RDL 为 3.0。

### SPACINGTABLE（M1–M5 一致）

```
PARALLELRUNLENGTH 0.00 1.50 4.50
  WIDTH 0.00   0.88 0.88 0.88
  WIDTH 1.50   1.00 1.00 1.00
  WIDTH 4.50   1.80 1.80 1.80
```

即间距随平行运行长度与线宽分段变化；基准间距 0.88 µm，最长并行段（≥4.50）间距放宽到 1.80 µm。

---

## 2. 通孔层规则（Cut Layers, TYPE CUT）

| 层 | 基本间距 (µm) | 相邻切割规则 (ADJACENTCUTS) |
| --- | --- | --- |
| TSV | 8.0（LAYER OVERLAP） | – |
| V1 | 0.68 | SPACING 1.08 ADJACENTCUTS 3 WITHIN 1.1 |
| V2 | 0.68 | SPACING 1.08 ADJACENTCUTS 3 WITHIN 1.1 |
| V3 | 0.68 | SPACING 1.08 ADJACENTCUTS 3 WITHIN 1.1 |
| V4 | 0.68 | SPACING 1.08 ADJACENTCUTS 3 WITHIN 1.1 |
| RDV | 2.0 | – |
| PA2 | 52 | –（钝化层 passivation） |
| uBump | 52 | –（钝化层 passivation） |

V1–V4 的 ENCLOSURE 规则（包围量）：
- `ENCLOSURE BELOW 0.08 0.08`、`ENCLOSURE ABOVE 0.08 0.08`
- 线宽 ≥5.0 时：`ENCLOSURE BELOW 0.37 0.37 WIDTH 5.0`、`ENCLOSURE ABOVE 0.37 0.37 WIDTH 5.0`

---

## 3. 过孔定义（Vias）

| 名称 | 切割数 | 电阻 (Ω) | 跨接层 |
| --- | --- | --- | --- |
| VIA_TSV | 1 | 0.15 | C4_bump / TSV / M1 |
| VIA1_1cut | 1 | 0.15 | M1 / V1 / M2 |
| VIA1_2cut | 2 | 0.075 | M1 / V1 / M2 |
| VIA1_4cut | 4 | 0.0375 | M1 / V1 / M2 |
| VIA2_1cut | 1 | 0.15 | M2 / V2 / M3 |
| VIA2_2cut | 2 | 0.075 | M2 / V2 / M3 |
| VIA2_4cut | 4 | 0.0375 | M2 / V2 / M3 |
| VIA3_1cut | 1 | 0.15 | M3 / V3 / M4 |
| VIA3_2cut | 2 | 0.075 | M3 / V3 / M4 |
| VIA3_4cut | 4 | 0.0375 | M3 / V3 / M4 |
| VIA4_1cut | 1 | 0.15 | M4 / V4 / M5 |
| VIA4_2cut | 2 | 0.075 | M4 / V4 / M5 |
| VIA4_4cut | 4 | 0.0375 | M4 / V4 / M5 |
| VIA_RDV_1cut | 1 | 0.072 | M5 / RDV / RDL |

---

## 4. 过孔规则（Viarules, GENERATE）

| 名称 | 参与层 | 阵列间距 | 各层包围量 (µm) | 线宽范围（如定义） |
| --- | --- | --- | --- | --- |
| GENV1 | M1 / M2 / V1 | 否 | M1: 0.37×0.37，M2: 0.08×0.08 | M1: 0.88–14 |
| GENV2 | M2 / M3 / V2 | 是 (1.4×1.4) | M2: 0.08×0.08，M3: 0.08×0.08 | – |
| GENV3 | M3 / M4 / V3 | 是 (1.4×1.4) | M3: 0.08×0.08，M4: 0.08×0.08 | – |
| GENV4 | M4 / M5 / V4 | 是 (1.4×1.4) | M4: 0.08×0.08，M5: 0.08×0.08 | – |
| GENRDV | M5 / RDL / RDV | 是 (5×5) | M5: 0.5×0.5，RDL: 0.5×0.5 | – |

切割矩形（cut RECT）：GENV1–GENV4 为 `-0.36 -0.36 0.36 0.36`，GENRDV 为 `-1.5 -1.5 1.5 1.5`。