# 深读笔记 — sid 1788172501150_w4x70 (haoyut @ hfeg0pkn003, mc=764)

- **trace_source**: user=haoyut, host=hfeg0pkn003, session_file=1788172501150_w4x70.messages.json, match_count=764
- **域判定**: physical_verify（PrimeTime read_parasitics 反标 / SPEF / 网表连接关系回溯 / 反标失败 net 调试）
- **规模**: 1181 msgs / 596 user / 585 assistant；工具 run_commands×446 / read_files×54 / editor×51
- **trace 路径**: /home/haoyut/.cline/data/sessions/1788172501150_w4x70/1788172501150_w4x70.messages.json（3.1MB）
- **业务路径**: /proj/iejoad/V0/simdir/verilog/haoyut/verilog.pim.iejoad.AIagent/AI_spef（写盘到 /rundata/iejoad/...）

## 用户意图流（关键 UI）

- **UI#0（逐字，纯需求 A-档 seed）**：「你研究怎么样通过读取cvps文件和netlist/中的pt_dir下的网表和 怎么样能结合当前这个脚本 通过提取反标报告中的未反标的pin 或者net 来提取出对应的spef信息 以及提取对应的netlist信息 把它们的hierarchy结构用同样的方法表现出来 并且最后形成对比 针对不同的反标error能有不同的分析结果 你可以复制需要的cvps 和netlist 和反标报告到这个AI_spef下 ... 允许你最多尝试至今天的22点」
- UI#160：问 parasitics command log 报错类型编号（前 100 条带类型，后 10000+ 仅层级+driver，与反标失败总数对得上）
- UI#253：「通过netlist_pt 我只给出一个节点的名称，能还原出它前后的连接关系给我吗」+ 实例路径例子
- UI#267：细化——给定未反标 net + driver pin，列出前后 5 级节点，工具化，「你想下只通过SPEF文件可以怎么做」
- UI#281/287/307/309：树形显示迭代
- UI#331：net_tracer 优化，图形更好看，**树形打印不要中文**，从 log 第三段随机抽样
- UI#355：给出竖直树形对齐范例（I183/Y → net040 ...）
- UI#441：「从上到下竖着的树形层级图，给个叶子能看到 n 级内相连节点，给树杈时前后都要看」
- UI#491/507：跑 `net_tree_v5.py --net "RowRedComp64/net016" --depth 5`，**真实接受输出**：I26(nor3GFLx1).Y→net_37→I23(nand3PFLx2).Y→net_62→I25(invGFLx4).Y→RRH12N[1]→I163(nand2PFLx2).Y→net017→I1(nor2GFLx4).Y→net016(TARGET)
- UI#517：问「通过spef还是netlist pt回溯」
- UI#717：粘贴 net_trace.py（重写版，from __future__ annotations，解析 structural Verilog）
- UI#791：net_trace.py 在老 python 上 SyntaxError（future annotations）
- UI#822：期望输出格式 `.B(Mn1[2]) --> .A(Mn1[0]) --> I26(nor3GFLx1).Y --> [net_37] --> ...`（带分支）
- UI#842/874：要 SPEF 版本 + SPEF/netlist 连接对得上（关注连接不是 RC）
- UI#902/924：用 Virtuoso 打开 view + probe net016
- UI#1112：完整 hierarchy `DRAMTOP/I_Array16GTop/.../I_RowRedComp64_17/net016`，「工具需要对应完整 hierarchy」
- UI#1128：「输入给的就需要是完整的 hierarchy」
- UI#1158（末轮）：「现在你选一个在 LOGICTOP 中出现的反标失败」——**未结束，继续迭代**

## 金标准判定

- trace 末尾（UI#1158）仍在迭代（选 LOGICTOP 反标失败样例），**无单一工具的干净最终接受**。
- 反复被用户运行并接受中间输出的核心工具 = `net_tree_v5/v6.py`：structural Verilog 网表 → 给定完整 hierarchy net 路径 + depth N → 输出 N 级前后（driver 侧上游 + load 侧下游）连接树。
- **A-档 disqualified**（无 trace 末尾干净接受产物）→ **B-档 synthesized**：按 UI#0/UI#441/UI#822 表达的需求 + UI#507 真实输出形态合成 gold = Python structural-Verilog 层级连接回溯器。
- **L1-boundary**：纯离线 Python 解析 structural Verilog 文本 + 图遍历，判分机无需 PrimeTime/SPEF/Virtuoso（§4.2 subprocess 真跑候选 ✓）。

## 与既有 case 区别

- shard C 既有：DRConnTiming/DRCTimeStats/DRCSFCompare = calibre rule/log 文本解析；CCKDriverFind = cck 网表实例层次遍历+端口方向分类+驱动 inst 定位（拓扑遍历，但单 parent 内、无 port-crossing 到 parent net、无 depth-bounded 双向 BFS 树）。
- 本案 = structural Verilog 多模块层级 + port-crossing（子模块 output port → 父 net）+ depth-bounded 双向 BFS 连接树 + ASCII 树 + JSON 结构化输出。主题独立（反标失败 net 连接回溯调试）。

## 踩坑（trace 真实）

- 老 python 不支持 `from __future__ import annotations` → gold 用兼容写法（不用未来注解）。
- 树形带中文被用户否 → gold 树形纯 ASCII。
- 用户要「完整 hierarchy」输入，不是单 module 内 net 名 → gold 接受 fullpath 并解析层级链。
