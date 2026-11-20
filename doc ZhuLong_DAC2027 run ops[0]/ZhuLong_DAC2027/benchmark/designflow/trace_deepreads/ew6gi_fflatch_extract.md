# 深读笔记: 1789634625396_ew6gi (rongjiez @ 10.129.2.11, mc=53)

- **user**: rongjiez, **host**: 10.129.2.11, **session**: 1789634625396_ew6gi
- **keywords**: dbopencv:150;pyaether:127;schematic:110;cellview:81;dbget:29;aether:14;dbopencellviewbytype:13;virtuoso:5
- **size**: 247150 bytes, 54 msgs, 3 user turns

## 用户原话（逐字）

- U#0: "@cxmt_getLatchFFCellList.il @cxmt_getLatchFFCellList.py cxmt_getLatchFFCellList.il是virtuoso的一个脚本，实现了获取电路中可能的FF/Latch cell list，cxmt_getLatchFFCellList.py是把这个skill脚本翻译成aether的pyaether脚本，但是现在pyaether脚本跑出来的结果和skill的结果不一样，甚至有时会直接报'NoneType' object is not iterable，输出文件是空的，请你帮我看下问题出在哪里，先不要直接修改我的文件"
- U#1: "你知道怎么对aether的pyaether脚本进行debug吗"
- U#2: "用这些调试方法在你的脚本里加上调试代码来验证上一轮分析的 bug"

## 真实任务

AICAD 团队脚本 `cxmt_getLatchFFCellList.il` (Virtuoso SKILL)：打开 schematic
cellview，遍历所有 instance 及其 instTerms（按 input/output 端子方向），通过
反馈环路检测获取电路中「可能的 FF/Latch cell list」。翻译成 pyAether 版本
`cxmt_getLatchFFCellList.py` 后结果与 SKILL 不一致、报 NoneType 崩溃、输出空。

## assistant 诊断（5 个 bug）

1. **对 None 迭代崩溃**（关键）：`etMakeTable` 默认 None，SKILL 的 `foreach` 对
   nil no-op，Python `for x in None` 抛 TypeError。`inputNet1List`/`outputNet1List`
   在某 inst 只有输入或只有输出端子时为 None → 崩溃在写文件前 → 空输出。
2. **`list(string)` 拆字符**（关键）：SKILL `list(x)` 造单元素表，Python
   `list("CK")` → `['C','K']`。`instPinNet_table[instId]["input"]=list(net.name)`
   把首个网络名拆成字符，`ae.member` 永不匹配 → 反馈环路检测失效 → flatLatch 空。
3. **`dbOpenCV` viewType 默认 layout 非 schematic**：SKILL
   `dbOpenCellViewByType(lib cell "schematic" "schematic" "r")`，Python
   `ae.dbOpenCV(lib,cell,"schematic","r")` 的 viewType 默认 "layout" → 找不到
   cellview → 内容未被检查。修复：用 `dbOpenCVByType` 显式传 viewType。
4-5. (其余 bug 见 MSG#13，结构类似)

## 关键 API

`dbOpenCV`/`dbOpenCVByType` (开 cellview)、`aeGetCurDesign` (当前设计)、
`etMakeTable` (建表，默认 None)、`ae.cons`/`ae.member`/`ae.car`/`ae.cadr`
(Lisp 列表操作)、`etOutFile`/`etFprintf` (写文件)、`etSort` (排序)。

## A-faithful 判定

U#0 是**调试请求**（"帮我看下问题出在哪里，先不要直接修改"），非「提出需求/表达
目标」produce 轮 → A-faithful 不适用。且 live schematic cellview + instTerms 不可
附加/不可移植 → **B 级 synthesized**。

## 合成 plan（B 档 facet = FF/Latch cell list 提取器）

取可移植 facet = **结构化网表 → FF/Latch 候选提取器**
(`gen_ff_latch_extract.py --netlist <file> --outdir <dir>`)：

- **网表格式**：`# design: <NAME>` 头 + 每行 `INSTANCE <inst> <cell> <pin>:<dir>:<net> ...`，dir∈{in,out,inout}（schematic instTerms 方向的可移植表征）。
- **self_loop Latch**：某 inst 的 output 网同时是其自身 input 网（直接自反馈）。
- **cross_coupled Latch**：两 inst A,B 互耦——A 驱动的网被 B 读且 B 驱动的网被 A 读（经典 NOR/NAND 交叉耦合 SR 锁存）。
- **master_slave FF**：两个 cross_coupled 锁存对，master 对被时钟网 CK 驱动、slave 对被互补时钟网 CKB 驱动，且 master 某输出网被 slave 某 inst 读取（级联）。构成 FF 的 4 个 inst 从 latch 候选移除，单独归入 ff 候选。
- 既无自反馈也不参与任何锁存/FF 的 inst 归 combinational。
- **输出**：`ff_latch_list.json`（9 顶层键 design/n_instances/latch_candidates/ff_candidates/feedback_paths/n_latch/n_ff/combinational_cells/n_combinational）+ `report.md`（## Summary + 每 latch `## Latch:` + 每 ff `## FF:`）。

### 三输入设计（A/B/B2 全不相交）

| 输入 | design | n_inst | n_latch | n_ff | n_comb | 结构 |
|---|---|---|---|---|---|---|
| A (visible) | SYNC_CORE_A | 8 | 2 | 1 | 2 | SRN1/SRN2 NOR2 SR 锁存 + MF1/MF2 NAND2 master(clk) + SF1/SF2 NAND3 slave(clkb) FF + CINV1 INV/CAND1 AND |
| B (hidden) | SEQ_BLK_B | 12 | 5 | 1 | 3 | L3a/b + L4a/b 两 cross-coupled NAND2 锁存 + L5a/b NAND2 master(CK)+L6a/b NAND3 slave(CKB) FF + BS1 NOR2 self-loop(FB) + BX1 BUF/BX2 XOR2/BX3 OR2 |
| B2 (hidden) | LATCH_ONLY_B2 | 5 | 3 | 0 | 2 | BR1/BR2 NOR2 cross-coupled + BS2 NAND2 self-loop(FB2) + BC1 INV/BC2 NAND3（无时钟网→无 FF） |

反硬编码五轴：design 名 / inst 名(SRN1 vs L3a vs BR1) / net 名(QBAR vs QB_N vs Q2N) / group 数(2/5/3 latch) / n_ff(1/1/0，B2 无 FF) 全不相交；源码禁 10 个 A 字面量(SYNC_CORE_A/SRN1/SRN2/MF1/MF2/SF1/SF2/QBAR/clkb/MF1Q)；A-run design==SYNC_CORE_A。

### check 16 条件 a-p

a(zip 防泄漏+py_compile)/b(B-run exit0+2 文件)/c(9 顶层键)/d(design==SEQ_BLK_B)/e(n_inst==12)/f(n_latch==5)/g(n_ff==1)/h(n_comb==3)/i(latch 5 字段)/j(method∈{self_loop,cross_coupled})/k(cross_coupled 存在 partner≠inst 且 loop_nets≥2)/l(self_loop 存在 loop_nets≥1)/m(ff master_slave+master_insts2+slave_insts2+clock_nets2)/n(BX1 在 comb 且不在 latch)/o(report Summary+每 latch/ff 节)/p(反硬编码源码无 A 字面量+A-run design==SYNC_CORE_A+跨输入 B2 n_latch3/n_ff0/design==LATCH_ONLY_B2+3x sha256 一致)。

### 自验结果

ref PASS 16/16；5 negatives 全 FAIL（empty_shell→b / hardcode_a→d / print_expected→p / ref_core_deleted→f / naive_stub→j，5 distinct first_fail）；§4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL。断言闸门 k_rationale=k_check=16 ✓。

### 教训

1. **FF/Latch 反馈环路检测是 schematic_netlist L1 可验好范式**：self_loop/cross_coupled/master_slave 三类检测 + inst/net 方向 → 16 条件天然丰富（计数/类型枚举/字段/互耦/自反馈/FF 结构/组合隔离/反硬编码/跨输入/确定性），与 AnalogGroupRoleInfer-001(@group 注释)/LvsRuleAudit-001(SVRF 模块) facet 不同无重复。
2. **时钟网检测正则须兼容 clk/ck 两种拼写**：`(?i)c[l]?k` 匹配 clk(c-l-k) 与 ck(c-k) 及 clkb/CKB；原 `ck` 漏 clk 致 A 的 FF 漏检。
3. **确定性须排序 set/dict 迭代**：Python hash 随机化致 set 迭代序跨进程不同 → JSON 字段序变 → sha256 不一致；`sorted(all_nets)` + `sorted(edge_map.keys())` 修复。
4. **anti-hardcode 字面量勿出现在 ref 源码注释**：「clkb」作为文档示例写进 `_is_clk_net` 注释 → 误命中 A_LITERALS 子串检查 → 改用「complementary clock bar」描述。
5. **L1/L2 比例债仍存**：本 case 亦 L1（纯离线 Python 解析网表），fresh 池 mc≥40 顶部 peek 12 候选仅 ew6gi 可用(L1 facet)，印证 #317/#332/#345-348 连续 6 轮「clean L2 produce 稀缺」结论。下轮继续优先 L2/L3（可降 mc 阈值到 ≥10 或扩 peek 到 mc 15-40 区段）。
