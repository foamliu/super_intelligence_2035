# trace_deepread: 1793524556149_f86ll — SchPinAnalyze-001 (layout_aether, A-档 faithful)

- **trace**: `1793524556149_f86ll` (sinanz @ hfeg0pkn005, mc=655, 740 msgs / 3.1MB)
- **case**: `EDA-Eval-DesignFlow-SchPinAnalyze-001` (L1-boundary, A-faithful)
- **选料理由**: layout_aether 域从 fresh pool(1457 行 mc≥30, 排除 322 跨 shard ledger'd)按 A-档 pure-intent 单轮 seed 选 f86ll(sinanz, layout_aether 44→45, 单焦点"打开原理图+列 pin+分析功能", USER#2 确认接受=单轮闭环, L1-boundary=CDL 静态解析离线可验)。

## 用户原话逐字 (msg#0, 单轮纯 intent A-档 seed，未指根因未给修复)
> 请帮我打开以下路径下的电路原理图，列出这个电路的input和output pin名称，并尝试分析这个电路的功能： /proj/dscqa/V0/workdir/sinanz/Test_ZSN_DLUTFull_2/CNT_COM_PRAC_new

## assistant 真实工具链 (msg#1–#56)
1. `list_allowed_files` 探目录 → Aether OA 设计库 (schematic/sch.oa + symbol + data.dm)
2. `read_files` 读 data.dm (二进制, 提到 terminal 顺序 ("AC2<12:0>" "AC<12:0>" "out<1:0>"))
3. `RAG_MCP_Server__search_apis` / `get_api_details` 查 pyAether API (dbOpenCVByType, aeGetCurDesign, emyFigGroupGetAllPinNets, ...)
4. `editor` 写 `/ai_sandbox/dscqa/V0/agentdir/sinanz/read_sch.py` (pyAether 脚本)
5. `SandBox_MCP_Server__run_code` 多轮执行 pyAether:
   - `ae.emyInitAether("-adv")` + `ae.dbOpenCVByType(lib, cell, view, "schematic", "r")` 打开 CNT_COM_PRAC_new schematic
   - 遍历 `cv.terms` / `cv.terminals` / `cv.instances` / `cv.shapes` → 124 shapes, 3 terminals, 22 signal instances
6. msg#56 整理完整分析报告 (USER#2 ts=1793525205225 确认"刚才的电路分析很正确")

## 真实产物 (gold, msg#56 报告 — USER#2 确认正确)
- **设计**: lib=Test_ZSN_DLUTFull_2 / cell=CNT_COM_PRAC_new / view=schematic (Aether 22.60.047)
- **顶层 I/O pin** (cv.terminals):
  - input: `AC<12:0>` (13-bit BusTerm), `AC2<12:0>` (13-bit BusTerm)
  - output: `out` (1-bit scalar Term)
  - (电源/体: vcc!/vss!/vbp!/vbn! 隐式连接，不计顶层 signal pin)
- **电路功能**: 13-bit 数值比较器 (Magnitude Comparator)
  - out = 1 当 AC[12:0] > AC2[12:0]；out = 0 当 AC ≤ AC2
  - 实际只比较 bit[11:0] (12 位)，bit 12 未参与连接
  - 原理图标注 Shape[108]: "AC large = 1 / AC2 large or same = 0"
- **结构**: 3 组级联比较 (HBits[11:8] / MBits[7:4] / LBits[3:0])，每组从 MSB→LSB 级联 CNT_COM_PRAC 2-bit 比较器
  - **9 个 CNT_COM_PRAC** (I_CNT_COM_PRAC_1,2,3 / 4,5,6 / 13,14,15)
  - **13 个标准逻辑门**: nand2×4 (I0,I14,I18,I35) + inv×5 (I2,I6,I7,I8,I17) + xor2×2 (I3,I10) + oai21×1 (I1) + and2×1 (I34)
  - 最终输出: `out = oai21(A=net2, B=HBitsSameN, C=HBitsACLargeN)`；net2 = AND(net59, MBitsACLargeN)；net59 = NAND(MBitsSame, LBitsACLarge)
- **22 个 signal 实例** (9 sub + 13 gate；另 3 个 PIN 实例为 I/O 标记不计入 signal)

## L1-boundary 设计 (CDL 静态解析，无需 live Aether)
- **候选** = `analyze_circuit.py` (仅标准库)，CLI `python3 analyze_circuit.py <netlist.cdl>`，stdout 输出 JSON
- **资产 A (可见)** = `CNT_COM_PRAC_new.cdl`：按 msg#56 报告手工重建的忠实 CDL 网表 (.SUBCKT 头 + .PININFO 方向 + 9 XCNT_COM_PRAC + 13 标准门 X 实例 + .ENDS)，网表连接与报告逐一致
- **隐藏 B** = `hidden/CNT_COM_EQ8.cdl`：8-bit 相等比较器 (8 xnor2 + 7 and2 级联归约)，结构与 A 完全不同 (无 CNT_COM_PRAC，无 oai21；pin A<7:0>/B<7:0>/eq；function=equality_comparator)
- **JSON 字段**: cell / input_pins / output_pins / n_instances / n_comparators / n_std_gates / gate_types / function_class / comparison_bits
- check.py 在 A 与隐藏 B 上各跑候选，断言 14 条独立条件 (a–n)

## 判分 14 条 ①–⑭ (a–n)
(a) zip+py_compile+不硬编码 A/B cell 名字面量  (b) A 运行 exit0 合法 JSON  (c) A input_pins={AC<12:0>,AC2<12:0>}  (d) A output_pins={out}  (e) A n_comparators=9  (f) A n_std_gates=13  (g) A gate_types={nand2:4,inv:5,xor2:2,oai21:1,and2:1}  (h) A function_class=magnitude_comparator  (i) A comparison_bits=13  (j) B 运行 exit0 合法 JSON 且 input_pins={A<7:0>,B<7:0>}(跨输入护栏)  (k) B output_pins={eq}  (l) B function_class=equality_comparator(异于 A)  (m) B n_comparators=0/n_std_gates=15/gate_types={xnor2:8,and2:7}(B 结构异于 A)  (n) 3x sha256 一致(确定性)+源码用 sys.argv(无硬编码路径)

## 自验
- ref `analyze_circuit.py` 跑 A → 14/14 PASS；跑 B → equality_comparator 正确
- check.py vs reference_submit.zip → 14/14 PASS
- 5 negatives (fake_empty→b / fake_print_expected→a / fake_core_deleted→e / naive_only_inv→b / naive_pin_only→e) ALL FAIL，NEG_RC=0
- §4.9 三假 (空壳/print-expected/删核心) 全 FAIL
- k_rationale=14=k_check=14≥8 GATE PASS
- jsonl 嵌入 test 抽出再跑 ref → 14/14 PASS

coverage 188→189 / 1511 = 12.5%
