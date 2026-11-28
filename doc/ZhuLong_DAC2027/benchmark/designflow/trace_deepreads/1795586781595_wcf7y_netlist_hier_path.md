# wcf7y deepread — SPICE flat-netlist hierarchy path resolver

- **trace**: 1795586781595_wcf7y · e0044131 @ hfeg0pkn001 · mc202 (hspice:1167/waveview:521/netlist:211/.def:200)
- **session**: 305 msgs / 161 user / 144 asst · agent=lead · 7 `<user_input mode=act>` blocks
- **date**: 2026-11-28 r1407

## 用户真实意图

SRAM 2048×40 M16 B2 宏 `CXN4HCSPS2048X40M16B2C1R1W1BW1RE1_FS` presim 功能仿真验证。用户从上一会话交接（handoff summary），本会话核心诉求（msg #3/#5/#6/#7）：

> 「之前电路q输出波形异常，导师说当时定位到nand那里，we没问题，就肯定是xd的问题了。…帮我找一下nand和we和xd在哪个路径」
> 「我只想知道nand在aether里的哪一层可以找到，还有we和xd在waveview中的路径」
> 「你详细找一下XD的路径，我从这个路径里找了个v(xd)，是一个只有一个下降沿z字的波形，这对吗？」
> 「导师说的定位到nand哪里，we没问题，肯定是xd的问题，这实际上…是排除法」

即：在扁平 SRAM netlist + func5.fsdb 里**定位 nand/we/xd 三个信号节点的层级路径**（aether 层级 + waveview dotted path），用于 Q 输出异常调试。

## 助手工具链（produce 方向）

助手写了 4 个 Python 脚本逐层 grep 扁平 netlist (`CXN4HCSPS2048X40M16B2C1R1W1BW1RE1_FS.netlist` ~889KB)：

1. **find_sig_paths.py** — grep `.SUBCKT` 名 + SA/WA/dl 关键字，定位叶子 cell 名
2. **dump_lio_sa_wa.py** — dump 指定 `.SUBCKT` body（HCSP_LEAF_SA_MUX16 / HCSP_LIOX40 / HCSP_LIO_T）的实例行
3. **dump_top_region.py** — dump `**TopDesStart..TopDesEnd` 扁平顶层实例区（XIGIO/XIBK6/XILIO[3]/XI0）
4. **grep_q_nand.py / grep_gio_qpath.py / dump_din_dout.py** — grep NAND/WE/XD 在 GIO DIN→DOUT→Q 路径上的门

并用 waveview-fsdb-readerV2-2 skill（bsub wv_queue）在 func5.fsdb 实测候选路径可读性。

## 可移植核心算法（叙事高潮）

**SPICE 扁平 netlist 层级路径解析器**：

1. 解析所有 `.SUBCKT <name> <ports...> ... .ENDS` 块 → cell 定义
2. 解析每个 cell body 内的 X-实例行 `X<inst> <nets...> <cellname>`（cellname 是**最后**一个 token，instname 是 X 后第一个 token）
3. **扁平顶层检测**：netlist 末尾 `**TopDesStart..TopDesEnd` 标记区（无包装 `.SUBCKT TOP`）内的顶层 X-实例 → 根实例
4. **总线数组实例展开**：`XISA[0..19] <nets> HCSP_LEAF_SA_MUX16` 一行代表 20 个实例，展开成 `xisa[0]..xisa[19]`
5. DFS 从每个顶层实例向下，累积 dotted 路径（小写、点分隔、方括号索引），找到所有到达目标叶子 cell 的路径
6. 输出 waveview 风格路径：`xilio[3].xilio_l.xisa[0].sae`

## 关键 gotcha（可移植核心，造题显性化）

- **G1 扁平顶层 vs 嵌套 .SUBCKT**：netlist 无顶层 `.SUBCKT TOP` 包装，顶层实例在 `**TopDesStart..TopDesEnd` 标记区。朴素「只扫 .SUBCKT body」会漏掉根实例。
- **G2 总线数组实例语法**：`XISA[0..19]` / `XISA[19:0]` 一行 = N 个实例。朴素行级解析当成 1 个实例 → 路径数错。
- **G3 X-实例 cellname 是最后 token**：`X<inst> <net1>...<netN> <cellname>`。取错字段（如 tokens[1]）会拿到 net 名当 cell 名。
- **G4 waveview 路径约定**：小写 + 点分隔 + 方括号索引保留 `xisa[0]`。大写保留或分隔符错（`xisa/0` 或 `XISA.0`）判错。
- **G5 多路径枚举**：同一叶子 cell 被实例化多次（40 个 SA：20 left + 20 right），须枚举全部路径，不能只返第一个。

## 可移植判定

原 deliverable 依赖专有 SRAM netlist (`/proj/lacaa/.../CXN4HCSPS2048X40M16B2C1R1W1BW1RE1_FS.netlist` 889KB，用户私有宏) + func5.fsdb + waveview license → 不可直接移植。

**可移植抽象** = 纯 Python SPICE netlist 层级路径解析器：输入合成 netlist (含 .SUBCKT 多层 + 扁平顶层标记区 + 总线数组实例) + 目标叶子 cell 名 → 输出所有 waveview 风格 dotted 路径。无 EDA 二进制 / PDK / 项目库依赖。

## 与既有 case 区分（避免 dup）

- **CdlInstReportGen-001** (r1403): 列出**单个** .subckt body 内的实例（X/M/C/R/L 分类），**不跨层遍历**。本 case = **多层**层级路径解析 + 扁平顶层 + 总线数组展开 + dotted 路径输出，算法正交。
- **HierFlattenCSV-001** (r1406): Virtuoso OA schematic 树展平→CSV（数据源是 cellview JSON，非 SPICE netlist）。本 case 数据源 = SPICE 文本 netlist。
- **CdlPvtDeckGen-001** (r1402): CDL→HSPICE PVT deck 生成器（生成 deck，非解析层级）。
- 无既有「SPICE netlist 多层 hierarchy path resolve」类 case。

## 造题计划

**case EDA-Eval-DesignFlow-NetlistHierPathResolve-001** (spice_sim, L1 judge-run, LIVE-NA, judge=[L0,L1])。

- candidate `hier_path.py <netlist.sp> <target_cell> <out_dir>`：parse .SUBCKT + 扁平顶层区 + 总线数组展开 → DFS 枚举所有到达 target_cell 的 waveview dotted 路径 → paths.json + summary.txt
- A/B 双输入：合成 SRAM-ish netlist，A (XIGIO/XIBK[0..3]/XILIO[1]→GIO/LIO/BK→LEAF_SA) vs B (XDRC/XARRAY[0..7]→DEC/ARRAY→LEAF_WL)，拓扑/名/深度/总线宽度全不同
- check.py ≥16 断言 (a,b,sa 静态 + c..n L1 judge-run on hidden B)
- §4.9 negatives 4 个 first-fail distinct
- LIVE-NA: 纯 Python 无 EDA 二进制，不入 live_eval_changes.tsv
