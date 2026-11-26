# Deep-read: 1792133398859_0t5o9 (claire1l @ hfeg0pkn004)

- **session**: `/home/claire1l/.cline/data/sessions/1792133398859_0t5o9/1792133398859_0t5o9.messages.json`
- **size**: 636 KB / 98 msgs (55 user / 43 assistant) · mc=143
- **keywords**: synopsys:2992; netlist:179; dbget:96; calibre:69; gdsii:24; techfile:19; schematic:17; primetime:8
- **tools-counted**: 96 dbGet, 21 calibre, 2 dbCreateRect, 2 dbCreatePath, 1 schematic, 1 pyAether
- **domain**: eda_other (StarRC LPE / ITF QA) — shard A

## 用户意图（逐轮，A-faithful 选轮）

- **U#0 (idx 0)**: 给出 5 份 StarRC ITF 路径（TSI1.0 OL/NL Rev06、TSI2.0a staircase NL Rev03、TSI2.0b isc OL/NL），「读取并分析对比这五份itf，将他们的共同点和差异点总结成表格」。**= 提出需求，未给根因/方案 → 符合 A 档规则②**。本 case 任务说明取此轮原文。
- U#4: 「比较下5个itf中TSV的参数，将TSV关键参数汇总成表格」
- U#6: 再给 5 份 star_cmd 路径，要对比 star_cmd
- U#10: 读 starrc man 文档，把 star_cmd 命令含义并表
- U#71: advanced options 三条命令详解
- U#84: 对比 5 份 starrc_mapping
- U#88: 对比 5 份 qrc.ccl，与 star_cmd 一一对应
- U#94: 更新第 5 份 qrc.ccl 路径

## 助手工具链
read_files 并行读取 5 份 ITF → 逐块解析（TECHNOLOGY / GLOBAL_TEMPERATURE / DIELECTRIC / CONDUCTOR / VIA / TSV）→ 产出 markdown 共同点+差异点表 → 用户继续追问 TSV/star_cmd/mapping/qrc.ccl，助手各产表。无 write 产物（纯分析/表格输出在对话里）。

## ITF 文件结构（解析口径）
- `TECHNOLOGY = <name>` · `GLOBAL_TEMPERATURE = <n>`
- `DIELECTRIC <name> {THICKNESS ER [SW_T TW_T MEASURED_FROM]}`
- `CONDUCTOR <name> {SIDE_TANGENT THICKNESS WMIN SMIN RPSQ CRT1 CRT2}`
- `VIA <name> {FROM TO AREA RPV CRT1 CRT2}`
- `TSV TSV {FROM TO AREA RHO THICKNESS INSULATION_THICKNESS INSULATION_ER}` — **可跨多行** `{ ... }`，解析需合并到 `}`
- 注释：`$...` 与 `#beginHide/#endHide`

## A（可见，用户给的 5 份 TYP）
| # | TECHNOLOGY | PAS2_1 | PAS1_2 | ILD1 | TSV 格式 | TSV RHO |
|---|---|---|---|---|---|---|
| ① TSI1.0 OL | cxmttsi1.0_6m5y1rdl_98C_TYP | 0.4 | 0.7 | 0.7100 | 三行折行 | 0.02825 |
| ② TSI1.0 NL | cxmttsi1.0_6m5y1rdl_98C_TYP | 0.4 | 0.7 | 0.7100 | 三行折行 | 0.02825 |
| ③ TSI2.0a staircase | cxmttsi_staircase_6m5y1rdl_98C_TYP | 1.2 | 0.8 | 0.65 | 单行紧凑 | 0.02825 |
| ④ TSI2.0b OL isc | cxmttsi_isc_6m5y1rdl_98C_TYP | 0.4 | 0.7 | 1.8800 | 两行折行 | 0.02825 |
| ⑤ TSI2.0b NL isc | cxmttsi_isc_6m5y1rdl_98C_TYP | 0.4 | 0.7 | 1.8800 | 两行折行 | 0.02825 |

A 共同：GLOBAL_TEMP=98、所有 M5/M4/M3/M2 RPSQ=0.010、V1 RPV=0.290、TSV AREA=113/THICKNESS=100.0/INSULATION_THICKNESS=0.46/INSULATION_ER=4.2、PAS2_2=0.55。
A 差异：TECHNOLOGY 名、PAS2_1、PAS1_2、ILD1、TSV 排版格式。

## B（隐藏，5 份不同 ITF — 跨输入守卫）
| # | 文件 | TECHNOLOGY | TSV RHO | TSV AREA | ILD1 | M5 RPSQ | V1 RPV | 结构特点 |
|---|---|---|---|---|---|---|---|---|
| b1 | TSI1.0 rev05 CMAX | cxmttsi1.0_..._CMAX | 0.01695 | 113 | 0.639 | 0.008 | 0.130 | corner |
| b2 | TSI1.0 rev05 CMIN | cxmttsi1.0_..._CMIN | 0.02373 | 113 | 0.781 | 0.012 | 0.450 | corner |
| b3 | singleDTC typ | CXMT_TSI_singleDTC_..._typ | 0.02034 | 113 | 0.079 | 0.010 | 0.190 | **+DTC_TP/DTC_BP 导体 +CT_BP/CT_TP 通孔** |
| b4 | singleDTC cmax | CXMT_TSI_singleDTC_..._cmax | 0.01695 | 113 | 0.0711 | 0.008 | 0.130 | **+DTC_TP/DTC_BP +CT_BP/CT_TP** |
| b5 | doubleDTC typ | CXMT_TSI_doubleDTC_..._typ | 0.02034 | **113.09** | 0.985 | 0.012 | 0.075 | PAS2_2 ER=8.1 |

B 与 A 在 TECHNOLOGY 名、TSV RHO/AREA/INSULATION_THICKNESS(0.5)、ILD1、M5 RPSQ、V1 RPV、层集（b3/b4 多 DTC 层）上全异 → 硬编 A 必败。

## 合成决定
- **case**: EDA-Eval-DesignFlow-ItfCompare-001
- **domain**: eda_other · **level**: L2（subprocess 在 B 上重跑候选生成器 + 独立 oracle 校验）· **track**: faithful（U#0 原文）
- **交付**: submit.zip 含 `compare_itf.py`（通用 ITF 比较器，CLI `compare_itf.py <dir>`）+ 对可见 A 产出的 `comparison.json` + `comparison.md`
- **判分**: check.py 在隐藏 B 上重跑 compare_itf.py，用独立 oracle 解析器校验 14 条 a–n（结构键/TECHNOLOGY/GLOBAL_TEMP/TSV 7 参数/ILD1/M5.RPSQ/V1.RPV/commonalities/differences/DTC 层存在性/跨输入守卫）
- **自验**: ref PASS 14/14；4 negatives（fake_empty/fake_print_expected/naive_hardcode_a/fake_delete_core）全 FAIL；§4.9 三假（空壳/只print/删核心）全 FAIL；inline-exec 路径 PASS

## 备注
- 这是 L1-结构化（离线 Python 解析真实 EDA 文件格式）但带 subprocess 重跑 + 跨输入 B + 独立 oracle，符合 shard A 在 L2-真跑不可行时的退化口径（同 CdlVbnBulkRemap-001 先例：StarRC 实跑环境脆弱不纳入判分）。
- 用户后续轮（TSV/star_cmd/mapping/qrc.ccl）未纳入本 case，避免多交付件耦合；首轮流已足以构成可判定子任务。
