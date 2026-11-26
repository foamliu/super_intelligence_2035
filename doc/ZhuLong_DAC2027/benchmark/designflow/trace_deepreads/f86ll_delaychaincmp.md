# Deep-read: f86ll (1793524556149_f86ll) — sinanz / hfeg0pkn005 — mc=655

## Trace source
- user: sinanz, host: hfeg0pkn005, session: 1793524556149_f86ll.messages.json
- 740 msgs, tools: schematic 1286 / pyAether 633 / dbCreateInst 167 / netlist 92 / cellview 71 / dbGet 39 / hspice 22 / calibre 13 / spectre 7

## User intent (the produce turn — U#57)
> 「刚才的电路分析很正确。…接下来请分别检查电路 CNT_COM_PRAC 和电路 CNT_COM_PRAC_new，比较他们从输入pin到输出pin信号延迟链，每经过一级逻辑门，都认为会带来200ps的延迟即可。」

即：给定两个电路（原理图/网表），从输入 pin 到输出 pin 求信号延迟链，每经过一级逻辑门记 200ps 延迟，比较两电路。

## 选轮判定
- U#0 = 提需求（列 pin + 分析功能）✅ 可作 A 档任务说明候选
- U#57 = 提需求（延迟链比较 200ps/gate）✅ **本轮采用** —— 比 U#0 更适合 ≥8 断言（两电路 × 多路径 × 比较）
- U#71 = 给方案（优化 6ACs）🚫 不用作 A 档
- 后续轮 = 调试 pyAether 生成 / skill 创建 🚫

## Assistant 工具链（U#57 之后）
read_files (data.dm/sch.hist/master.tag) → RAG search_apis (pyAether sch/db/emy APIs) → list_allowed_files (case_studies) → run_code pyAether (read_sch.py 提取 instance/net/terminal) → 对两电路分别跑 → 人工数逻辑门级数 × 200ps → 出比较报告。

真实产物：read_sch.py（pyAether 读 sch.oa → instances/nets/terms）+ 延迟链手算报告。

## A-faithful 可行性
🚫 不可行：真实电路在 `/proj/dscqa/V0/workdir/sinanz/...` 私有路径，且需 live pyAether 读 sch.oa（OA 二进制），不可移植到 .75 沙盒。
→ **B 档 synthesized**：用结构化 Verilog 网表（叶级门 INV/BUF/NAND2/NOR2/AND2/OR2/XOR2）代替 sch.oa，facet = 离线 Python 解析 Verilog + 最长路径门数 × 200ps。子技能忠实于 U#57 的「数逻辑门级数 × 200ps 比较」意图。

## Facet 设计
- `delay_chain_cmp.py --netlist-a <v> --netlist-b <v> --gate-delay 200 --outdir <d>`
  → `comparison.json`：两电路各列 input/output pins、每条 in→out 路径的 gate_count + delay_ps + gate_chain、critical_path、max/min delay；comparison (faster_circuit / reduction_ps / reduction_pct)。
- 逻辑：解析 Verilog (module 端口/线网/实例 .PIN(net)) → 建 net→driver/consumers 图（用门库知 output pin）→ DAG 最长路径（拓扑序 DP，检测组合环）→ delay = gate_count × gate_delay。

## 契约
- mode=design_flow, entry=outputs/submit.zip, test=check(deliverable, workdir) 双参
- A: assets circuit_a1.v (serial 8-gate chain, critical 1600ps) + circuit_a2.v (parallel 3-gate, 600ps)
- hidden B: circuit_b1.v + circuit_b2.v (不同门类型/信号名/结构) → check 只跑 B
- hidden B2: circuit_b2b_1.v + circuit_b2b_2.v (B≠B2 结构断言)
- 反硬编码：A 字面量（模块名 sigpath_serial/sigpath_parallel、信号 w1..w7/u1/u2、延迟 1600/600/1000/62.5、pin a/y1）禁源码；B2 与 B 结构不同但可同/异 delay
