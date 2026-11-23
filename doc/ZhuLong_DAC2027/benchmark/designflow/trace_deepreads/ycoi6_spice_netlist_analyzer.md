# ycoi6 deepread — SPICE netlist fault-injection analyzer

**trace**: 1794882363587_ycoi6 · user=t0003117 · host=hfeg0pkn004 · mc=99 · 66 msgs / 220KB
**session date**: 2026-11-17 · **domain**: spice_sim (shard B)

## 用户意图（真实 trace）

t0003117 在 Virtuoso 里抽取了 ddcpb_array/msagap 单元的 SPICE 网表
(`msagap_20261117_103004/netlist/msagap.sp`, 160 行)，想用
`/home/t0003117/skills_v0.2/netlist_extract/analyze_fault.py` +
`/home/t0003117/fault_inject_V3.py` 做**故障注入目标选择**：
列出所有可注入故障的器件 + 关键信号，供后续 Open/Short/Vth-Shift/Leakage 选择。

## 关键对话流

- **U0-U3**: 让 assistant 读 `SKILL.md`（SPICE netlist extraction + fault injection 工作流）。
- **U4-U33**: 执行 `extract_current_netlist.il` 经 "EDA Agent Bridge" 连 Virtuoso 抽网表。
  bridge 反复崩（`load()` 整脚本时报 "Unknown SKILL error"），assistant 逐步定位：
  `error()` 调用逃逸 `errset` + `geGetEditCellView()` 在 bridge 环境无 GUI 上下文。
  最终用户在 CIW 手动 `load()` 抽出网表（msagap_20261117_103004）。
- **U36-U61**: 分析 `msagap.sp`。assistant 发现 `analyze_fault.py` 硬编了旧网表路径
  (lwdrx8_2d5T)，改路径后跑出分析。**msg 61 给出结构化概览**：
  64 个晶体管（含 4 个 parasiticRC2 误分类）→ 手动归纳为 11 组真实 MOSFET：
  - MM0<0..7>/MM1<0..7> 交叉耦合 PMOS (ptn_lv)
  - MM11<0..7>/MM12<0..7> 预充电 NMOS (ntn_lv)
  - MMN14<0..7>/MMN15<0..7>/MMN17<0..7> 写路径 NMOS
  - MMN0/MM5/MMN7 电源开关 NMOS, MMP6 PMOS 上拉
  - 关键信号: Io0<0..3>/Io1<0..3>/IoN0<0..3>/IoN1<0..3>/EqIo/PreEq/vad2!/net62/vintlp!/vblh!/vkb!/vwlp!
- **U62-U65**: 用户放弃注入，转问 "bridge 到底是什么，为什么天天断"。assistant 给架构图
  (SandBox_MCP_Server → Python Server → Virtuoso SKILL via IPC) + 4 大设计缺陷
  (无进程隔离 / errset 不兜底 / 无心跳 / 错误信息黑洞)。**Q&A 无脚本产物**。

## 选题与 reframe

**选 msg 36-61 的网表分析任务**（故障注入目标选择 = 结构化网表概览），不是 bridge Q&A。
用户真实意图：把 `msagap.sp` 解析成「真实 MOSFET 列表 + bus 分组 + PMOS/NMOS 分类 + net 连接数」
的 JSON 报告，供 fault injection 选目标。

**核心技术齿（判分抓手）**：`fault_inject_V3.py::SpiceParser.MOS_PATTERN`
`^X(\S+) (\S+) (\S+) (\S+) (\S+) (\S+)(.*)` 会把 `XI4<0> net61<0> PhDecDn<0> vss! parasiticRC2 Cov=352.32e-18`
这种 **parasiticRC2 子电路实例**误分类成晶体管（model=Cov=352.32e-18）。
真实 MOSFET 的 model token 是裸模型名（`ptn_lv`/`ntn_lv`，无 `=`）；
陷阱实例的 model token 含 `=`（参数赋值）。**判分要求候选必须过滤 model 含 `=` 的实例**。

## reframe 任务定义

`spice_netlist_fault_analyzer.py <spec.json> <out.json>`：
- spec: `{netlist_path, cell, exclude_global_nets}`
- 解析 SPICE：抽 MOSFET（`^X name D G S B model [params]`，**model token 不含 `=`** 且为合法标识符）
- 抽 R/C（`^[RrCc] name pos neg value`）
- 极性分类：model 首字母 `p/P`→PMOS，`n/N`→NMOS
- bus 分组：剥离 `<...>` 后缀取 base name
- net 连接数：每 net 被多少晶体管 pin + R/C pin 引用
- 排除 global nets（0/gnd!/vss!/vdd!）
- 输出 JSON: `{cell, n_mosfets, n_groups, n_nets, n_resistors, polarity_counts{PMOS,NMOS},
  mosfet_groups[{base,count,model,polarity,instances[]}], nets[{name,n_connections}]}`

## A（trace-faithful，SUT 可见）

- `msagap.sp`（真实网表，160 行）
- `spec_A.json`: `{netlist_path:"msagap.sp", cell:"msagap", exclude_global_nets:["0","gnd!","vss!","vdd!"]}`
- 期望：60 真实 MOSFET (17 PMOS ptn_lv + 43 NMOS ntn_lv)，11 组，43 nets，11 R/C
- 4 个 parasiticRC2 实例 (XI4<0>/XI4<1>/XI6<0>/XI6<1>) 必须被过滤掉

## hidden B（五重 anti-hardcode）

1. cell: `sabuf` vs A `msagap`
2. models: `pch_g9t`/`nch_g9t` vs A `ptn_lv`/`ntn_lv`
3. bus widths: 4/6/2 vs A 8
4. 组名: MP0/MP1/MP2/MPPD/MN0/MN1/MN2/MN3/MNG vs A MM0/MM1/MM11/MM12/MMN14/MMN15/MMN17/MMN0/MM5/MMN7/MMP6
5. net 名: D0<0..3>/D1<0..3>/ClkN/PreB/net42 vs A Io0<0..3>/Io1<0..3>/EqIo/PreEq/net62
6. 极性分布: PMOS=15 NMOS=17 (total 32) vs A PMOS=17 NMOS=43 (total 60)
7. 陷阱: XP0<0>/XP0<1> model=Cov=210e-18 (2 个) vs A 4 个 Cov=352.32e-18/377.94e-18
8. 陷阱 model 值不同 (210e-18 vs 352.32e-18/377.94e-18)

## near-dup 自查

- `SubcktExtract-001`（抽 .SUBCKT 定义）— 不同：本 case 抽 MOSFET 实例 + 过滤陷阱 + bus 分组
- `SarAdc8bNetlistGen-001`（生成 netlist）— 不同：本 case 解析 netlist 输出 JSON
- `SimlibMatchAnalyze-001`（lib 匹配）— 不同
- `R1R4NetlistCheck-001`（netlist 检查）— 不同：本 case 专注 MOSFET 提取 + 极性 + 分组 + net 连接
- 无 near-dup ✓

## trace_source

- user: t0003117 (真实)
- host: hfeg0pkn004
- session_file: 1794882363587_ycoi6.messages.json
- match_count: 99
- real_task_summary: 分析 msagap SPICE 网表，列出所有可故障注入的真实 MOSFET（按 bus base 分组、PMOS/NMOS 分类）和 net 连接数，供 fault_inject_V3.py 选目标
