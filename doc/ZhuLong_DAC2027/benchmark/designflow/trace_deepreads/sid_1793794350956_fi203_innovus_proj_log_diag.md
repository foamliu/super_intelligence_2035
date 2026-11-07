# 深读笔记 — sid 1793794350956_fi203 (chengleiy @ hfeg0pkn005, mc=274, pg_layout)

- **session**: 155 msgs, 870KB, 2 user turns, 59 assistant text turns
- **user**: chengleiy (NEW — ledger_C 96 用户中无), host hfeg0pkn005, model glm-5.3-flash
- **tool signals**: innovus:2286 + netlist:29 + calibre:29 + pyAether:3 + synthesis:2 + cellview:2 + dbGet:1

## 用户原话（2 轮）

1. msg#0: `"/home/pdk/chengleiy/e_innovus 这个项目下是我做的innovus文件的项目，请你分别分析这些文件，给我整理出每个项目的情况，其中我也做了一些测试，请你根据log结果，帮我看一下，现在项目中，还存在什么问题"`
2. msg#110: `"/home/pdk/chengleiy/e_innovus/from_out/linux/apr 这个路径下是innovus的一些manual还有实战，请你仔细阅读manual，并形成自己的skill，以后回答我的问题，先基于手册"` (skill-formation follow-up, 非主任务)

## 项目结构（e_innovus/，3 大类）

| 目录 | 性质 | 内容 |
|------|------|------|
| `QA/lddb_ls8/{test_backside, test_backside_logic}` | 自测 QA | LDDB LS8 背面工艺 Innovus 布线验证（buffer b2b + logic b2f） |
| `QA/lddb_ls9/{test_backside, test_backside_logic, test_backside20260804}` | 自测 QA | LDDB LS9 背面工艺 |
| `QA/tsi/` | 自测 QA | TSI 硅互连工艺 |
| `from_ae/` | AE 参考 | 3DIC RAK 文档、hefeiTestFile_20260818/20260918、innovus_test_20260831 |
| `releaseFile/{LDDB_LS8,LDDB_LS9,TSI/tsi1.0/{v0.9_Rev11,v0.9_Rev12,v0d1_Rev13}}` | 发布文件 | tech LEF/cell LEF/layerMap |

各 QA 测试流程一致：`init_design` → 摆 die_inst + 100 TSV/bump → `setDesignMode` 背面/正面 → `globalDetailRoute` → `verify_drc`/`verifyConnectivity` → `streamOut` GDS。

## 各项目状态（assistant msg#109 最终报告 + 日志实证）

### 1. QA/lddb_ls8/test_backside（LS8 b2b buffer 背面）— ⚠️ error
- innovus.log: `**ERROR: (IMPLF-3)` tlef 处理错; `IMPSYT-16013` x4 LEF 加载中止; `IMPOGDS-55` merge file `./TSV_CELL.gds` 不存在; `IMPLF-53` x3 layer BFHLP 在 pin pin_0 macro CHIP_DIE 未定义; `IMPSYT-16038` x2 文件 invs_buffer_b2f_2M_0918_realsize_backside.tlef 找不到(误用); `IMPLF-26` x4 首个 LEF 无 tech info
- warns: `IMPLF-122` BFTLM 方向同; `IMPRM-157` 只一个布线层 skip auto via; `NRIG-125` VIA_BFTSV_1 非布线 via; `NRAG-44` track pitch 太小; `IMPVFG-1198` CPU 32 > verify_drc 1
- **Message Summary: 386 warning(s), 18 error(s)**
- Innovus `top.drc.rpt`: `No DRC violations were found`
- Calibre `drc_logic/top.drc.summary` (v2020.1_36.18): RULECHECK `LTSV_F_2a_NC` TOTAL=1, `LTSV_F_3a_NC` TOTAL=2 → **Calibre 3 violations 而 Innovus 报干净 → cross-check discrepancy**
- Calibre `drc/top.drc.summary` (物理背面): BFTSV_drawing SKEW edges; SR_D6* = 0, SR_D7* NOT EXECUTED

### 2. QA/lddb_ls8/test_backside_logic（LS8 b2f logic 背面）— ✅ clean
- innovus.log: 0 error; warns `IMPLF-108` no overlap layer, `IMPRM-157` one routing layer, `IMPFP-3961` techSite CORE 无 std cell
- **Message Summary: 8 warning(s), 0 error(s)**
- `top.drc.rpt`: `No DRC violations were found`; verifyConnectivity `Found no problems or warnings`

### 3. QA/lddb_ls9/test_backside（LS9 b2b 背面）— ❌ incomplete
- innovus.log 1.9KB: 08/03 启动后 `**INFO (INTERRUPT): One more Ctrl-C to exit Innovus ...` 手动中断，CPU 仅 3:30
- run.tcl 第 54-55 行拼写错误 `setGenerateViaMode -auto` (未完成)

### 4. QA/lddb_ls9/test_backside_logic（LS9 b2f logic）— ❌ error
- innovus.log: `IMPLF-53` layer LBM2 在 pin pin_0 macro CHIP_DIE 未定义; `IMPLF-3` die.lef 处理错; `IMPSYT-16013` LEF 加载中止; `IMPLF-223` VIA_LHLV_1 重复定义; `IMPVL-209` x20 Verilog undefined instance port; `IMPVL-356` x20 macro CHIP_DIE pin_1 netlist 未定义于 LEF; `IMPVL-902` Failed to read netlist top.v
- warns: `IMPLF-122` LBM1/LTLM 方向同; `IMPLF-108` no overlap; `IMPLF-119` LHLP/LHLV/LBM1 重复
- **Message Summary: 110 warning(s), 203 error(s)**

### 5. QA/tsi（TSI 硅互连）— ❌ crashed (SEGV)
- innovus.log (128.2KB): `IMPRM-132` x4 Missing VIARULE GENERATE definition between M1/M2; `IMPSYT-7329` init_design 后 design 已在内存; `IMPSYT-7328` x6 physical-only mode; `IMPTRN-1101` x6 power-rail GNDOnBtm; `IMPFP-3961` x12+x12 techSite CORE/cxm3site; `NRDB-914` x5 masterslice TSV/OVERLAP spacing unsupported
- **Message Summary: 60 warning(s), 5 error(s)**
- `core.89873` 文件存在 → SEGV core dump (CLASS CORE 宏导致 SEGV, stack 停在 lfiMacroSiteHandle)

## 关键 error code 清单（真实, grounded）

| code | 含义 | 出现项目 | 计数 |
|------|------|---------|------|
| IMPLF-3 | LEF 文件处理错 | ls8/test_backside, ls9/test_backside_logic | 1, 1 |
| IMPLF-26 | 首个 LEF 无 tech info | ls8/test_backside | 4 |
| IMPLF-53 | layer 在 pin 未定义 | ls8/test_backside(BFHLP), ls9/test_backside_logic(LBM2) | 3, 1 |
| IMPLF-108 | no overlap layer | ls8/test_backside_logic, ls9/test_backside_logic | 1, 1 |
| IMPLF-119 | layer 重复 | ls9/test_backside_logic | 3 |
| IMPLF-122 | layer 方向同上层 | ls8/test_backside(BFTLM), ls9/test_backside_logic(LBM1/LTLM) | 4, 2 |
| IMPLF-223 | VIA 重复定义 | ls9/test_backside_logic | 1 |
| IMPRM-132 | Missing VIARULE GENERATE M1/M2 | tsi | 4 |
| IMPRM-157 | 只一个布线层 skip auto via | ls8/test_backside, ls8/test_backside_logic | 5, 1 |
| IMPSYT-7328 | physical-only mode | tsi, ls8, ls9 | 6, 5, 1 |
| IMPSYT-7329 | init_design 后 design 已在内存 | tsi | 1 |
| IMPSYT-16013 | LEF 加载失败中止 | ls8/test_backside, ls9/test_backside_logic | 4, 1 |
| IMPSYT-16038 | 指定文件找不到 | ls8/test_backside | 2 |
| IMPVL-209 | Verilog undefined instance port | ls9/test_backside_logic | 20 |
| IMPVL-356 | macro pin netlist 未定义于 LEF | ls9/test_backside_logic | 20 |
| IMPVL-902 | Failed to read netlist | ls9/test_backside_logic | 1 |
| IMPOGDS-55 | merge file 不存在 | ls8/test_backside | 1 |
| IMPFP-3961 | techSite 无 std cell | tsi, ls8, ls9 | 24, 10, 2 |
| IMPTRN-1101 | power-rail GNDOnBtm | tsi, ls8, ls9 | 6, 5, 1 |
| NRDB-914 | masterslice spacing unsupported | tsi | 5 |
| NRIG-125 | non-routing via in rule | ls8/test_backside | 4 |
| NRAG-44 | track pitch too small | ls8/test_backside | 5 |
| IMPVFG-1198 | CPU 32 > verify_drc 1 | ls8/test_backside | 4 |

## 真实文件名（grounded）

- tlef: `invs_buffer_b2b_2M_0913_realsize_backside.tlef`, `invs_buffer_b2b_2M_0918_realsize_backside.tlef`, `invs_logic_b2f_2M_0707_realsize_backside.tlef`, `invs_buffer_b2b_2M_0715_realsize_backside.tlef`
- lef: `die.lef`, `lefFile/celllef/die.lef`, `lefFile/output/die.lef`
- gds: `BFTSV.gds`, `gds_buffer.gds`, `TSV_CELL.gds`, `test20260710.gds`
- 报告: `top.drc.rpt`, `drc_logic/top.drc.summary`, `drc/top.drc.summary`, `streamOut.rpt`, `innovus.cmd`, `innovus.log`, `innovus.logv`, `calibreDRC.rule`, `gdsOut.map`, `run.tcl`
- core: `core.89873`, `core.1184`, `core.53959`, `core.86443`
- Calibre 版本: v2020.1_36.18; Innovus 版本: 23.32-s091_1

## DISTINCT from 既有 pg_layout cases

- InnovusViaCutDiag-001 (r100): 单一 via-cut 诊断, 非多项目目录 inventory
- DigitalDesignFlowSampleGen-001 (r136): digital flow sample, 非 log 健康诊断
- PgRscalcAgentInline-001 (r200): RsCalc agent 内联, 非 Innovus log
- PgDummyDeckInv-001 (r196): calibre deck 单文件, 非 Innovus 项目
- 本案首次 ground on **多项目 Innovus 目录 inventory + log error-code 分类计数 + Innovus verify_drc vs Calibre signoff DRC cross-check discrepancy + 5 状态分类(clean/warning/error/incomplete/crashed)**

## 合成决策

- trace 末尾(msg#110)用户转向"形成 skill"——非诊断报告的明确接受 → 不适用 A-档
- 取 **B-synthesized** grounded on 真实项目结构 + 真实 error codes + 真实 violation counts + 真实文件名
- 合成"Innovus 项目目录 inventory + log 健康诊断器"任务(SUT 写 `innovus_proj_log_diag.py`, CLI `<project_root>`, 扫子项目目录 + 解析 innovus.log*/top.drc.rpt/top.drc.summary/core.* → 结构化 JSON 健康报告 + cross-check discrepancy 列表)
- 资产 A=5 子项目(lddb_ls8/test_backside[error+Calibre discrepancy]/lddb_ls8/test_backside_logic[clean]/lddb_ls9/test_backside[incomplete Ctrl-C]/lddb_ls9/test_backside_logic[error IMPVL x20]/tsi[crashed SEGV])
- 隐藏 B=5 子项目重参数化(LS7/LS10/TSI2, 不同 error codes 计数, 不同 Calibre rule 名, 不同 Message Summary 数)
- L1-boundary: 离线 Python log 解析器(读附件目录写脚本), 不真跑 Innovus/Calibre
