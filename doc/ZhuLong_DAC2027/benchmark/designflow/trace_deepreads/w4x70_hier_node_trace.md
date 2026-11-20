# trace_deepread: 1798172501150_w4x70 — HierNodeConnTraceProduce

- **user/host**: haoyut @ hfeg0plg15 (also hfeg0plg101)
- **session**: 1788172501150_w4x70.messages.json (3.0 MB, 1181 msgs)
- **keywords**: verilog:3222 netlist:1394 cmos:269 virtuoso:214 analog:171 schematic:94 transistor:62 ... (D-pure, netlist/verilog/schematic/analog dominant, low drc/lvs/calibre)
- **match_count**: 1576

## 用户意图（D-pure schematic_netlist）

用户在 `/proj/iejoad/V0/simdir/verilog/haoyut/verilog.pim.iejoad.AIagent/AI_spef` 下研究 PrimeTime 反标（annotation）失败的 pin/net。真实工作流：读 cvps (SPEF) + netlist_pt (门级 Verilog) + 反标报告，提取未反标的 pin/net，对比 SPEF 与 netlist 的 hierarchy，针对不同反标 error 给不同分析。

## A-faithful 选轮：U#253（纯需求轮，无根因/无方案）

> 通过netlist_pt 我只给出一个节点的名称，能还原出它前后的连接关系给我吗 例如 I_Array16GTop/I_Array8G_SC1/I_Array2GB_SC1/I_ArrayCtrlX2B23/I_BankTopX2/I_CMAryB_222/I34_1_

用户给出一个层级实例路径，要求还原其前后连接关系（前级 driver + 后级 load）。符合 A 档选轮规则：提出需求、未给根因、未给修复方案。

## 后续澄清轮（不进 prompt，作设计参考）

- U#287: 换例子 + 说明搜索方法 + 改善树形显示（`I_Array16GTop/.../I_ColCtrlBnkA23New_B/net040 (driver: pin .../I183/Y)`）
- U#441: 从上到下竖着的树形层级图，给叶子看 n 级相连节点，前后都要看
- U#331: 树形显示不要中文，多样化抽样
- U#1112: 输入需完整 hierarchy

## 助手真实产出

`net_tree_v5.py` / `net_tree_v6.py` / `net_trace.py`：解析门级 Verilog → 1770 modules → 按 `--net "RowRedComp64/net016" --depth 5` 追踪连接 → 树形/横排/JSON 输出。最终演化出 `hier_node_trace` 风格：driver（前级 cell output pin）+ load（后级 cell input pin）递归到 depth N。

## synthesized-reframe

真实 netlist_pt = 148MB+ NFS 文件（顶层 DRAMTOP，1770+ modules，foundry-bound），不可入沙盒。reframe 为紧凑门级 Verilog fixture，保留真实 DRAM 层级 + 真实标准单元名（nor2GFLx4 / invGFDx4 / nor2GFLx1 / nor3GFLx1 / invGFLx4 / nand2PFLx2）+ 真实 net 命名（net017/net014/net016）。

## 造的 case

**EDA-Eval-DesignFlow-HierNodeConnTraceProduce-001** (schematic_netlist, 14 断言 a-n, k_check=k_rationale=14>=8 GATE PASS)
- A: DRAMTOP/.../I_CMAryB_222/I34_1_ (nor2GFLx4), driver I35(invGFDx4)/I28(nor2GFLx1), loads I11/I16/I40(nor3GFLx1), depth-2 load I50(invGFLx4)
- B (hidden, 完全不相交 token): SRAMTOP/.../I_SenseAry_42/I12_3_ (Nor2YLx4), driver I47(InvYLd4)/I29(Nor2YLx1), loads I14/I18/I33(Nor3YLx1), depth-2 load I51(InvYLg4)
- check.py 14 断言：独立 _gt_parse（line-based）+ _gt_find_driver/_gt_find_loads 重算 B 真值；反硬编码 A-only token 零泄漏；3-seed md5 确定性；A report 匹配 A 金标准
- 自验：ref 14/14 PASS on B + 3 neg (empty/print_only/core_deleted) 全 FAIL NEG_RC=0 + §4.9 三假全 FAIL

## 与已有 case 的区分

- r1017 SignalConnCheckProduce: 全部信号的扁平 driver/load 列表（表形，ND/MD/NL/OK 状态）
- 本 case: 单层级节点的 depth-N 前后连接关系递归追溯（树形，driver→driver / load→load 递归）
- 互补非重复。
