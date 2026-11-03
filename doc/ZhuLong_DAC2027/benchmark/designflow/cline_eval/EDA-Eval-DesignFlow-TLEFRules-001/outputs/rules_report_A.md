# 布线规则汇总报告 — tech_thk2d0_m5.lef

> 本报告汇总 `tech_thk2d0_m5.lef`（VERSION 5.7，`DATABASE MICRONS 4000`，即 1 LEF 单位 = 1 µm）
> 中每一层**走线层（TYPE ROUTING）**与**通孔/切割层（TYPE CUT）**的布线规则，
> 以及其中的过孔定义（`VIA`）与生成式过孔规则（`VIARULE`）。
> 机器可读的结构化汇总见 `lef_rules.py` 的 stdout JSON 输出。

## 1. 走线层（routing layers）

| 层名 | 方向 DIRECTION | 线宽 WIDTH | PITCH | OFFSET | MAXWIDTH | AREA | 间距规则 |
|------|----------------|------------|-------|--------|----------|------|----------|
| C4_bump | VERTICAL | 15.0 | 20.0 | — | — | — | SPACING 9.0 |
| M1 | HORIZONTAL | 8.88 | 9.76 / 9.76 | 0.88 / 0.88 | 12 | 4 | SPACINGTABLE |
| M2 | VERTICAL | 8.88 | 9.76 / 9.76 | 0.88 / 0.88 | 12 | 4 | SPACINGTABLE |
| M3 | HORIZONTAL | 0.88 | 1.76 / 1.76 | 0.88 / 0.88 | 12 | 4 | SPACINGTABLE |
| M4 | VERTICAL | 0.88 | 1.76 / 1.76 | 0.88 / 0.88 | 12 | 4 | SPACINGTABLE |
| M5 | HORIZONTAL | 0.88 | 1.76 / 1.76 | 0.88 / 0.88 | 12 | 4 | SPACINGTABLE |
| RDL | VERTICAL | 3 | 6 | 2 | — | — | SPACING 3 |

- M1/M2 为**厚金属**（WIDTH 8.88，PITCH 9.76），M3/M4/M5 为**细金属**（WIDTH 0.88，PITCH 1.76）。
- M1–M5 的 SPACINGTABLE 内容相同：

```
  PARALLELRUNLENGTH 0.00  1.50  4.50
    WIDTH 0.00   0.88  0.88  0.88
    WIDTH 1.50   1.00  1.00  1.00
    WIDTH 4.50   1.80  1.80  1.80
```

  即：平行走线长度阈值为 0.00 / 1.50 / 4.50 µm；同层线宽 0~1.5 时线距 0.88，线宽 1.5~4.5 时线距 1.00，
  线宽 ≥4.5 时线距 1.80。
- C4_bump（凸点层）与 RDL（再分布层）只定义了单一 `SPACING`，无 `SPACINGTABLE`。

## 2. 通孔 / 切割层（cut layers）

| 层名 | SPACING | 相邻孔距（ADJACENTCUTS） | 其它规则 |
|------|---------|--------------------------|----------|
| TSV | 8.0（到 OVERLAP） | — | M1 与 C4_bump 之间的硅通孔 |
| V1 | 0.68 | 1.08（ADJACENTCUTS 3 WITHIN 1.1） | ENCLOSURE BELOW/ABOVE 0.08；WIDTH 5.0 时 0.37 |
| V2 | 0.68 | 1.08（ADJACENTCUTS 3 WITHIN 1.1） | ENCLOSURE BELOW/ABOVE 0.08；WIDTH 5.0 时 0.37 |
| V3 | 0.68 | 1.08（ADJACENTCUTS 3 WITHIN 1.1） | ENCLOSURE BELOW/ABOVE 0.08；WIDTH 5.0 时 0.37 |
| V4 | 0.68 | 1.08（ADJACENTCUTS 3 WITHIN 1.1） | ENCLOSURE BELOW/ABOVE 0.08；WIDTH 5.0 时 0.37 |
| RDV | 2.0 | — | M5 与 RDL 之间的通孔 |
| PA2 | 52 | — | 钝化层（LEF58_TYPE PASSIVATION） |
| uBump | 52 | — | 钝化层（LEF58_TYPE PASSIVATION） |

## 3. 过孔定义（vias）

| VIA | 孔数 cuts | 电阻 resistance | 层 layers |
|-----|-----------|-----------------|-----------|
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

## 4. 生成式过孔规则（viarules）

| name | layers | has_spacing | enclosures | width_range |
|------|--------|-------------|------------|-------------|
| GENV1 | M1, M2, V1 | false | M1: 0.37×0.37, M2: 0.08×0.08 | M1: "0.88 TO 14" |
| GENV2 | M2, M3, V2 | true（SPACING 1.4 BY 1.4） | M2: 0.08×0.08, M3: 0.08×0.08 | — |
| GENV3 | M3, M4, V3 | true（SPACING 1.4 BY 1.4） | M3: 0.08×0.08, M4: 0.08×0.08 | — |
| GENV4 | M4, M5, V4 | true（SPACING 1.4 BY 1.4） | M4: 0.08×0.08, M5: 0.08×0.08 | — |
| GENRDV | M5, RDL, RDV | true（SPACING 5 BY 5） | M5: 0.5×0.5, RDL: 0.5×0.5 | — |

## 5. 说明

- 单位：`UNITS DATABASE MICRONS 4000`，制造栅格 `MANUFACTURINGGRID 0.00025` µm。
- 本文件仅为技术库（techlef），仅含工艺布线规则与过孔定义，不含具体单元（MACRO）。
- 走线层共 7 层（C4_bump / M1–M5 / RDL）；通孔切割层共 8 层（TSV / V1–V4 / RDV / PA2 / uBump）。