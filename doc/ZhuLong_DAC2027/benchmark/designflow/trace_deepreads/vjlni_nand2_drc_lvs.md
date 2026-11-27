# Deepread: vjlni — NAND2 cell create + schematic + layout + DRC + LVS

**trace_source**: user=e0020134, host=hfeg0plg86, session=1789550083559_vjlni.messages.json, match_count=1164, domain=layout_aether (+physical_verify)
**fetched via**: .75 eda_flow run_commands ssh + scp (PATH-FIX 子目录路径 `/home/e0020134/.cline/data/sessions/<epoch_id>/<epoch_id>.messages.json`), 1.4MB / 655 msgs
**claim round**: r1477 (2026-11-28). ledger mark=deepread. **DEBT: 下轮合成 case** (655 msgs > 600, TASK §3 允许拆轮).

> 与 m60gy (→ AetherBridgeClient-001) 关系：同一用户/同一天/同 Fast Channel 通道。m60gy 只做 ping/env 探测；**vjlni 是其后续：建 cell + 画 schematic/layout + 跑 DRC/LVS**，是 distinct 的 layout_aether+physical_verify produce-task。Fast Channel 协议部分不重复造题（已被 AetherBridgeClient-001 覆盖）。

## 1. 真实用户意图（user 原话，pinyin）

- msg0: 「按 AGENTS.md 方式 A2（Fast Channel）操作 Aether：写 chan_req（首行 REQ <序号>，后面一行 Python），每 1 秒轮询 chan_out... 发 REQ v1 内容 ping() 验证连通，然后 print(env()) 报告 Aether API 状态。」
- msg43: 「xinjianyige cell, zaishangmian hua yige nand」= **新建一个 cell，在上面画一个 nand**
- msg477: 「jixu, xuyao neng tongguo drc he lvs, xuyao ni qidong zheliangge yanzhen」= **继续，需要能通过 DRC 和 LVS，需要你启动这两个验证**
- msg625: 「jian cha, gaosuwo jieguo」= 检查，告诉我结果
- msg654: 「jixu」= 继续（trace 在此截断，LVS 仍 INCORRECT 待修）

**真实任务**：在 Aether 里通过 Fast Channel 文件桥，新建 NAND2 标准单元（schematic + layout），跑 Calibre DRC + LVS，目标是 DRC clean + LVS CORRECT。

## 2. 环境侦察（Phase 0, msgs 44-92）

- 目标库 `hrz_test`，技术库 `TECHLIB`（1154 层）
- NMOS pcell = `ntn`（TECHLIB），CDF 参数 `w=0.82u, l=0.176u, nf=1, mostype=nmos`
- PMOS pcell = `ptn`（TECHLIB），同参数，`mostype=pmos`
- 已有 NAND 示例 `Spnand2CSx1`（schematic+layout，用 `stdcells_am/nand2CSx1` 实例），宽约 4.2µm
- 关键层（drawing purpose）：`NW, PW, NSD, PSD, PC(poly), CT(contact), CPP, M1, M2, V1, V2`
- ntn 端子 = S/G/D/B；symbol pin 位置（master 坐标）：G=(0,0), S=(0.25,-0.1875), B=(0.25,0), D=(0.25,0.1875)
- ptn 端子同 ntn

## 3. Schematic 构建（Phase 1, msgs 93-291）

**NAND2 逻辑**：Y = !(A & B)
- PMOS 并联：MP1(G=A)+MP2(G=B)，S→VDD，D→Y
- NMOS 串联：MN1(G=A, D=Y, S=net1)，MN2(G=B, D=net1, S=VSS)

**API 用法（实测）**：
- `dbOpenCV(lib, cell, view, mode='a')` 开 cellview
- `dbCrtInst(cv, master, name, x, y)` 放 pcell 实例
- `dbCreateSchPinEx` / pin 符号（ipin/opin/vdd/gnd from TECHLIB）放引脚
- `dbCrtSchWire(cv, layer, points, width)` → 返回 emyLine tuple；**`emyLine.addToNet(net)`** 设网络（关键发现，msg 275/283）
- schematic wire layer = `'wire'`
- `dbSave`/`dbCloseCV`

**踩坑**：连线初版 19 个自动 net（未连到端子）→ 需精确触端子坐标 + addToNet；editor 的 insert_line 会残留旧内容导致 chan_req 多行语法错；Fast Channel 去重（同 REQ id 不重处理）→ 每次用新 id。

**最终 schematic 连接（msg 476 验证通过）**：
| 信号 | 连接 |
|---|---|
| A | PIN0 → MN1.G, MP1.G |
| B | PIN1 → MN2.G, MP2.G |
| Y | MN1.D, MP1.D, MP2.D → PIN2 |
| VDD | PIN3 → MP1.S, MP2.S, MP1.B, MP2.B |
| VSS | PIN4 → MN2.S, MN1.B, MN2.B |

## 4. Layout 构建（Phase 2, msgs 293-476）

- 在 layout view 上画矩形（dbCrtRect）于各层：OD/PC/CT/M1/M2/V1 等
- 14 个 via（V1）
- prBoundary/boundary、y0/drawing、M1/pin + text label（dbCrtLabel）
- 参考现有 Spnand2CSx1 的层用法

## 5. DRC + LVS（Phase 3, msgs 477-655）

**验证环境**：
- Calibre + Argus 都可用（env vars `MGC_CALIBRE_DRC_RUNSET_FILE` / `MGC_CALIBRE_LVS_RUNSET_FILE`）
- `leGuiRunCalibreDRC` / `aeSetVerificatonConf` API
- DRC/LVS 提交到 **LSF 集群队列 `pv`**（`cmnRunHostType: remotelsf`），非同步
- 输出路径：`/proj/drcqa/V0_AIRouting/ver/{drc,lvs}/<lib>/<cell>/`（rundrc.log / runlvs.log）

**LVS 结果 = INCORRECT**（msg 638/652）。提取的 layout 网表：
```
.SUBCKT zhulong_nand2 VSS VDD     ← 只提取出 2 个端口！
X0 3 ptn_cdns_subMaster_1 ...      ← pcell 子模块只有 1 个端子（衬底）
X1 3 ptn_cdns_subMaster_1
X2 4 ntn_cdns_subMaster_1
X3 4 ntn_cdns_subMaster_1
```
**三类问题**（msg 652）：
1. **端口缺失** — A/B/Y 没被识别（pin label 没对准 M1 金属 / text 与 shape 不关联）
2. **pcell 不被识别** — `LVS RECOGNIZE GATE` 失败，pcell 退化成黑盒子电路（只 1 端子=衬底）
3. **device 认不出** — ntn/ptn pcell 在 LVS 里没展开成 MOS

trace 在 msg 654「jixu」处截断，LVS 修复未完成（DEBT 状态：真实任务未收敛）。

## 6. Case 设计候选（下轮合成）

### 候选 A（推荐，L0/L1 LIVE-NA）：NAND2 LVS 诊断报告生成器
- **意图**：给定 LVS INCORRECT 报告 + 提取的 layout netlist + schematic netlist，生成结构化 mismatch 诊断（端口缺失/pcell 未识别/device 未展开 三类），输出 fix-list（加 pin label 对齐 M1 / 设 LVS RECOGNIZE GATE / pcell 展开）。
- **抽象**：纯 Python，输入=JSON（layout netlist + sch netlist + LVS rules），输出=结构化诊断 dict。自包含 representative netlist（NAND2，4 device，5 port）。check 独立重实现诊断逻辑比对。
- **判分**：≥12 断言（端口集比对 / device 展开检测 / net 连接拓扑比对 / fix-list 正确性），hidden B 不同 netlist（NOR2 或不同 mismatch 模式），4-5 negative。
- **风险**：偏 analysis/Q&A（任务初衷允许），但 produce 结构化报告仍是 deliverable。

### 候选 B（L0/L1 LIVE-NA）：NAND2 layout DRC rule checker
- **意图**：给定 NAND2 layout spec（JSON 矩形按层分组）+ DRC rule 集（各层 width/spacing/enclosure），跑几何 DRC 输出 violations 报告。
- **抽象**：同 ViaMetalOptGdsGen 风格，纯 Python 几何 DRC。但 DRC rule 值需从真实 PDK 抽 representative 数值（trace 未给具体值，需编代表值，faithfulness 风险）。

### 候选 C（L2.live）：真跑 pyAether 建 NAND2 + DRC/LVS
- 最忠实但 .75 实跑复杂（需 LSF 队列、Calibre 许可、pcell 展开），check_live 难写，预算/确定性风险高。不推荐首取。

**下轮取候选 A**（最自包含、判分有牙、faithful 于真实 LVS 诊断意图）。trace 已深读，下轮直接合成。

## 7. 不撞已有 case 论证
- AetherBridgeClient-001（m60gy）：Fast Channel 协议客户端，不涉 cell/layout/DRC/LVS ⇒ 不撞
- SpacePlugMerge-001（56vki）：DRC pattern tool space 函数合并 ⇒ 不撞（vjlni 是标准单元建库+验证）
- SchematicStripeFix-001（4iv57）：DRC pattern tool schematic 示意图修复 ⇒ 不撞（vjlni 是真 NAND2 cell）
- CalibreRuleSuffixXform-001（xza9c）：Calibre rule 文件后缀转换 ⇒ 不撞
- DrcDeckPrune-001（24ap1）：DRC deck 裁剪 ⇒ 不撞
- ERCFilter-001（ukkn7）：ERC filter ⇒ 不撞
