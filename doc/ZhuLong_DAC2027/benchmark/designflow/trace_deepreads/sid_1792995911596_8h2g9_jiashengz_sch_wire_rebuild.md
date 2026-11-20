# Deepread — sid 1792995911596_8h2g9 (jiashengz @ hfeg0plg92 / 10.129.8.224)

- **session**: `1792995911596_8h2g9.messages.json` (mc=362) + `messages.archive.json` (12.05MB, 10 chunks, 3330 msgs)
- **tools**: aether:415 pyaether:362 schematic:329 netlist:78 .lef:72 dbget:47 dbCreateInst:2; archive: schematic:2632 pyAether:669 netlist:482 dbCreateInst:97 dbGet:62 cellview:51 hspice:34 calibre:2 dbCreateRect:1
- **domain**: layout_virtuoso (Virtuoso SKILL schematic wire-drawing + net-binding) — precedent: r66 SchPinPlanAudit, r67 NetDelSaveAudit (schematic SKILL under layout_virtuoso)

## 真实任务（USER 逐字）

- USER#1 (chunk0, 16304 chars): 贴入完整 SPICE 网表 `fig_5_8_1.sp`（来源 Rice 16Gb 1b nm DDR5 SDRAM Circuit Analysis.pdf 第877页, SK HYNIX H5CG48BHBD-X030, TECHINSIGHTS D_KD149, Fig 5.8.1 WRITE AUTO-PRECHARGE LATENCY BLOCK 顶层网表；11 子图实例 + 2 反相器延迟链 + 2 输出反相器；总线按位展开）。
- **USER#2 (chunk0, A-档 seed, 提出目标未给根因/修复)**: `<command-args>根据给定的 SPICE 网表 fig_5_8_1.sp 在 Aether (pyAether) 中构建 WRAP_LATENCY_BLOCK 电路：为各子模块创建仅含接口(pin)的 symbol，再搭建顶层 schematic 并生成网表</command-args>`
- 后续 USER 多为工具回显（list_files / search_apis / run_code 结果 JSON），少有新指令。
- live session (recent.json, 6 msgs) 末态：在 Virtuoso 重建 `R1bSTD/D_KD145/schematic`（35 instances, 31 nets, 62/62 instTerm→net），用 SKILL 画可见 wire figures。

## A-档资格判定：disqualified → B-档 synthesized L1-boundary

1. gold 依赖 live Aether（pyAether `aeGenSymbolAndSchematicByVerilog` / `dbNewCellView`）+ live Virtuoso（`schCreateWire` / `schCreateWireLabel` 真实图形落库）+ live OA 库 `R1b`（/proj/drcpa/V0/workdir/jiashengz/R1b，3653 cells）。.75 沙盒不可达 → tooling disqualified。
2. USER#1 给的是完整 SPICE 网表（输入资产），USER#2 是规整需求型指令（已被 eda_agent skill 模板包装），非"提出目标未给根因"的纯净 A seed；且 gold 的可验证内核（SKILL wire-drawing 程序的结构正确性）可离线静态校验 → 取 B-档 synthesized。

## gold（真实产物，已 scp 验证）

### 1. rebuild_DKD145_wire_full.il（5417B, 100 行, 最终权威版）
路径 `/home/jiashengz/agentdir/train/V0_NCG_HF_Virtuoso/rebuild_DKD145_wire_full.il`。核心知识：
- **net-binding 方法 = endpoint-on-pin auto-bind**：`w = car( schCreateWire( geGetEditCellView() "draw" "full" list(x1:y1 x2:y2) 0.0625 0.0625 0.0 ) )`，每根 wire 端点恰好落在 pin 上，Virtuoso 自动把 wire 绑到该 pin 的 net。**不使用 `schCreateWireLabel`**（该 Virtuoso build 不可用）。
- **单顶层 `let( (w) ... )` 块**，所有 wire 在同一作用域。
- **拒绝不可靠的 manual `w~>net = netmap[...]` 方法**（早期 `rebuild_DKD145_wire.il` 用 evalstring + foreach w~>net=，被 full 版废弃）。
- 40 根 wire，10 组（按 `;=== group ===` 注释分组）：
  - LATCH Qn→TRI AD (4) / OS port→OS NOT A (4) / OS NOT QN→TRI B (4) / OS port→TRI C (4) / TRI QN→BUF (2) / BUF OUT (1) / ADD_TS1_L3→I898.A (1) / top NOT chain cascade (11) / CK ports→LATCH CK (4) / D data bus (5=1 trunk+4 stubs)
- 设计规则（可泛化、可离线校验）：
  - **D data bus trunk 在左侧 x=-0.6**，D stubs 在整数 y（0,3,6,9），CK stubs 在 y+0.25 → **D/CK 不交叉**。
  - **NOT chain cascade**：y=13 恒定，11 段连续衔接（seg[i].x2 == seg[i+1].x1，步进 3.0，从 0.75→33.0）。
  - wire width 恒定 0.0625，draw mode "draw"，route "full"。

### 2. rebuild_DKD145_wire.il（2997B, 早期版，被废弃的方法）
用 `evalstring` + `netmap = makeTable('netmap nil)` + `foreach( w wl w~>net = netmap["D453446"] )` 手动绑 net —— full 版判定此法不可靠，改用 endpoint-on-pin auto-bind。**这是本案判分要 ban 的反例**。

### 3. SPICE→schematic 工具链（build_wrap_latency.py）
`/home/jiashengz/wrap_latency/`：fig_5_8_1.sp（430 行顶层网表）+ build_wrap_latency.py（拆 8 段 sp + 5 段 verilog + verify_*.py）→ 在 Aether 建 symbol + 顶层 schematic + 导网表。属 Aether 路径，本案只取 Virtuoso SKILL wire-drawing 内核做 B-档。

## 合成方案（B-档 synthesized L1-boundary）

**case_id**: EDA-Eval-DesignFlow-SchWireRebuildGen-001
**候选**: `gen_wire_rebuild_il.py`（纯标准库）读 `wire_manifest.json`（style + instances + wire_groups{group,net,wires[(x1,y1,x2,y2)]} + design_rules{d_ck_noncrossing, not_chain, trunk_x} + method）→ 产 `outputs/rebuild_wires.il`（单 let 块、car(schCreateWire...)、按组分注释、endpoint-on-pin auto-bind、禁 manual `~>net=`）+ `outputs/wire_report.json`（counts/groups/method/banned_method_requested，stdout==file）。

**资产 A 忠实**: D_KD145 / R1bSTD，40 wires 10 groups 精确坐标（从 gold full.il 解析），D/CK 非交叉 + NOT chain cascade 规则，method=auto_bind。
**隐藏 B**: 不同设计（D_KD210/WRAP_CTRL_BLOCK，不同 nets/坐标/计数），但**保留** d_ck_noncrossing + not_chain 规则（证规则泛化非硬编码 A）。
**隐藏 B2**: 极简单组 manifest，无 design_rules（测候选处理规则缺失 + 不硬编码 A 拓扑）。
**隐藏 B3**: method="manual_net_assign"（banned）→ 候选仍须产 auto_bind（无 `~>net=`），report.banned_method_requested=True。

## check.py 13 条断言 a-m（k_check=13）
a zip+py_compile / b B exit0+il+report+stdout==file+顶层键 / c schCreateWire 计数==manifest 总线数(独立重数) / d 每根 wire 端点 list 解析==manifest(容差1e-6,按组有序) / e 单顶层 let 块且无 `~>net =` manual 绑定(banned) / f 每调用含 geGetEditCellView() / g 每调用含 "draw"+"full"+width 0.0625 0.0625 0.0 / h B 的 D/CK 非交叉规则(D stubs 整数y, CK stubs y+offset, 无重叠,独立重算) / i B 的 NOT chain cascade 连续衔接(seg[i].x2==seg[i+1].x1 同y,独立重算) / j report.wire_count==计数+group_counts 匹配+method==auto_bind / k 确定性 3×md5 / l B2 结构 guard(计数匹配+无~>net=+cell!=B) / m B3 banned method 仍产 auto_bind+report.banned_method_requested==True+cell!=B

## 与现有 layout_virtuoso case 正交
r87 PowerFillMergeGen(spec→SKILL 合并代码 dbCreateInst/dbSave)、r67 NetDelSaveAudit(net 删除/保存审计)、r66 SchPinPlanAudit(pin plan)、r74/r85 RsCalc(电阻计算)、r61 SkillMenuRoute(菜单路由)——**本案是 schematic wire-figure 生成 + net-binding 方法选择(endpoint-on-pin auto-bind vs banned manual ~net=)**，主题独立。
