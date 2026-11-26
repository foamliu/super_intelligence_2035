# deepread: 1795012706443_fc55b — stdcell layout methodology (legendd)

- **trace**: `1795012706443_fc55b.messages.json` (1.67MB, 492 msgs)
- **user**: legendd @ hfeg0pkn001 (10.129.2.10) · mc=588 · 268 user / 224 assistant
- **domain**: layout_aether (pyAether-dominant: 1276 pyAether tool calls)
- **keywords**: pyaether:1530; schematic:612; aether:275; netlist:170; dbget:116; drc:87; transistor:76; cellview:62
- **claim**: r822 C-shard, layout_aether

## Real task (verbatim, msg#0)

> 我现在要和你一起画一个stdcell 的layout，我会给你一个示例告诉你怎么画，你要总结出方法，画出其他所有stdcell，准备好了吗

用户以「示例教学 → 总结方法 → 复用到所有 stdcell」为骨架，多轮手把手带 assistant 走完一个 INV stdcell 的版图绘制全流程，并在过程中沉淀方法论知识库。

## 多轮流程（用户指令 → assistant 工具链 → 用户确认）

| # | 用户指令要点 | assistant pyAether 操作 | 用户确认 |
|---|---|---|---|
| 0 | 画 stdcell layout，总结方法 | (准备) | — |
| 2-20 | schematic 已打开，先理解原理图（除 Legendd 库外只读） | emyGetCurDesign / 读 schematic | — |
| 51 | 顶层 pin vss/vcc/vbn/vbp 后面 `!` = 全局 pin | 列出 pin，识别 `!` | — |
| 53 | 6 个 pin 的 Input/Output/InputOutput 属性 | dbGet pin direction | — |
| 85 | 进入 TECHLIB/invLV_pc60 pcell 取结构/尺寸 | dbOpenCellViewByType → 进 pcell | — |
| 117-119 | 分析这是什么 cell、功能；LN/LP 实例化值也有 | 读 LN/LP 参数 | 「对的」 |
| 137-152 | SDL → Start SDL → 改 library name 为 legendd → 开 layout view | emySDLStart | 「这次对了」(after retry) |
| 173 | SDL → Generate All From Schematic（调入 device） | emyGenerateAllFromSchematic | — |
| 183 | 调入 TECHLIB/spacer/layout 作参考 cell | dbCreateInst spacer | — |
| 194 | spacer 高/宽由 prboundary 定义，取尺寸 | 读 prboundary bbox | 「做的不错」 |
| 211 | annotate:drawing3 = metal track, annotate:drawing8 = PG track（**PG = poly layer，非电源**）；path 宽度由 width 属性决定，长度由 points 累加 | 读 track figs | — |
| 232-234 | 纠正：PG = poly layer；PG:DUMMY = dummy poly，计数 | 数 dummy poly | — |
| 242-244 | 当前 level 操作限制；align api 可省计算 | — | — |
| 331 | mos 左 dummy poly 中心线 ↔ spacer prboundary 左边对齐 | align api | — |
| 342-348 | LL X 不是 0.29 → 修正 | 重做 align，LL X=0 | 「这次对了」 |
| 350 | PMOS dummy PG 下边距 spacer 第2条 PG track 上边 0.234；NMOS dummy PG 上边距第1条 PG track 下边 0.234 | move + 偏移计算 | 「做的不错」 |
| 358-382 | INV 宽度 = mos 两边 dummy PG 中线间距 → 改 spacer width | 改 spacer width | 「做的不错」 |
| 384-395 | 用户误操作 → 重跑 step2-6；完成后 redraw | 重做 | — |
| 401-403 | 规则：spacer 上方 M1/M0U/MT2/CT = 电源，下方 = 地 | — | — |
| 409 | 分析 technology trace rule（routing layer 连接关系） | techFindLayer / emyGetViaDefByLayer | — |
| 466 | M0U ↔ MT2 的 via 是哪层？ | emyGetViaDefByLayer(M0U,MT2) | 「对的 是 PCU」 |
| 474 | PMOS 有源区 AT4:PCH 栅 PG:PCH；NMOS AT4:NCH 栅 PG:NCH；与 MT2 通孔连接 | emyGetViaDefByLayer(AT4,MT2) / (PG,MT2) | 「做的不错，连接关系理清了」 |
| 485 | (assistant 自沉淀) stdcell 版图标准 & 知识库 | — | — |
| 486-489 | spacer TYPE 属性（现值 CH）其他值？ | cdfGetCDF → cdfFindParamByName(tpType) → 14 个 choices | — |
| 490-491 | 我提供文件 spacer TYPE → MOS TYPE 对应关系，你能读吗 | (assistant 待读文件) | **会话结束** |

## 关键事实（assistant 实际产出的硬数据）

### Technology via-chain（msg#475-482，从 Legendd tech lib 提取）

| 层对 (top ↔ bot) | via def 名 | cut layer | cut 尺寸 | 方向 |
|---|---|---|---|---|
| AT4(4) ↔ MT2(65) | `LICON_103X258` | `PC`(51) | 103×258 | MT2→AT4 找到 1 def |
| PG(30) ↔ MT2(65) | `LICONGC_103X258` | `PC`(51) | 103×258 | MT2→PG 找到 1 def |
| M0U(66) ↔ MT2(65) | (via def, name 含 PCU) | `PCU`(52) | — | 双向 |
| AT4 ↔ M0U | 无直接 via | — | — | 0 defs |
| PG ↔ M0U | 无直接 via | — | — | 0 defs |

- 用 `pyAether.emyGetViaDefByLayer(tech, top_num, bot_num, defarr)` 取 via def 数组
- 用 `pyAether.emyGetCustomCutLayer(vd, cut_str)` 取 cut 层名
- 用 `vd.getName(nm)` 取 via def 名
- assistant 反向查询（bot→top）才找到 AT4/PG↔MT2 的 def（顺序敏感）

### Spacer TYPE（msg#487-489，CDF 参数 choices）

`pyAether.cdfGetCDF("TECHLIB","spacer")` → `cdfFindParamByName(cdf,"tpType")` → choices 列表（14 个）：
`CH, CH_m, CHLVP, CH_lvio, mix, CH_mix_m, m_mix_lv, CH_mix_lv, CHK, CHK_lv, PTK_LV_NTK, PTK_NTK_HV, noImplant, noNW`

### 对齐规则（msg#331-358，assistant 实操 + 用户验证）

- mos 左 dummy PG 中心线 → 对齐 spacer prboundary 左边（X=0）
- PMOS dummy PG 下边距 spacer 第2条 PG track 上边 = 0.234 µm
- NMOS dummy PG 上边距 spacer 第1条 PG track 下边 = 0.234 µm
- INV 宽度 = mos 两边 dummy PG 中线间距 → 写入 spacer width 属性

## 会话结局

msg#490 用户：「我会按照这个格式 spacer TYPE --> MOS TYPE 来说明对应关系，我提供一个文件，你可以读取吗」
msg#491 assistant：「当然可以！请把文件路径告诉我」→ **用户未再回复，会话结束**。

**未达成 §A rule 4 trace-end-gold**（用户最后是询问而非接受交付），但 assistant 在 msg#485 已自沉淀出完整 stdcell 版图方法论知识库（层级约定 / 流程 / 对齐规则 / 层次规则），且全过程 14+ 次用户「做的不错/这次对了」确认每一步实操正确。

## 档位判定

- **A 档 gold**（live pyAether 跑 emyGetViaDefByLayer + cdfGetCDF + SDL + align）→ SUT 沙盒无法跑 pyAether，不可直接复用
- **B 档 reframe**（r817-r821 同模式）：抽 assistant 已验证的 **technology via-chain 解析**为纯 stdlib 图遍历核心（via def 既能直接连也能多跳 BFS，cut layer 提取，对称性，hop 上限），hidden B 用不同 tech 名/层名/多跳结构验算法通用性
- **case**: `EDA-Eval-DesignFlow-TechViaChainResolver-001`（layout_aether, track B, L2-boundary）

## 证据索引

- via-chain 解析代码：msg#475, #477, #479, #481（`emyGetViaDefByLayer` + `emyGetCustomCutLayer`）
- via-chain 结果：msg#482（AT4↔MT2=LICON_103X258/PC, PG↔MT2=LICONGC_103X258/PC）
- M0U↔MT2=PCU：msg#466-472
- spacer TYPE CDF：msg#487-489
- 对齐规则实操：msg#331-358
- 自沉淀知识库：msg#485
