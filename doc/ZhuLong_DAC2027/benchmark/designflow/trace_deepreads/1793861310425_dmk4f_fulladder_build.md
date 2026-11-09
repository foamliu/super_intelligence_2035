# Deep-read: 1793861310425_dmk4f (sinanz @ hfeg0pkn005)

- **sid**: 1793861310425_dmk4f
- **user/host**: sinanz / hfeg0pkn005
- **mc**: 100 (keywords: lvs:678; schematic:240; aether:150; pyaether:140; cellview:79; dbopencv:51; cmos:44; verilog:27)
- **tools**: SandBox_MCP_Server__run_code ×14 (pyAether), list_allowed_files ×11, read_files ×5, RAG search/get_api ×4
- **msgs**: 66 (38 user=mostly tool_results, 28 assistant, 37 tool_uses)
- **agent**: lead (zhulong)
- **domain**: schematic_netlist (D-shard)
- **grade**: B-grade synthesized（私有 /proj/trgqa + pyAether 沙盒不可复刻）

## 真实任务（U0，唯一一条用户文本轮）

用户在 `/ai_sandbox/trgqa/V0_die2/agentdir/sinanz/Skills` 放了 2 个 skill（ReadSchematic.md 读取/分析电路、SchematicEdit.md 创建/编辑原理图），要求：
1. 先学习这 2 个 skill
2. 在个人工作路径 `/proj/trgqa/V0_die2/workdir/sinanz/Test_ZSN` 下生成名为 `FullAdder_2` 的单 bit 全加器电路
3. 调用公共库 `/proj/trgqa/V0_die2/libs/stdcells_ac` 的单元（基本逻辑单元在 stdcells_ac），绝对不能改动它们
4. 教了命名规则：前缀=功能、数字=输入端口数、L/G/C/LV=管子类型、xN=管子尺寸（例 or2Lx1、nand3LVx16）

## Agent 工作流

1. **学 skill**：read_files 读 ReadSchematic.md + SchematicEdit.md + 两个 demo 脚本（demo_stdcell.py、read_sch.py）；读 SchematicEdit.md 中段（84-238 行）
2. **探环境**：list_allowed_files 探 `/ai_sandbox/trgqa/.../sinanz`、`/proj/trgqa/V0_die2`、workdir/sinanz、libs/stdcells_ac；read_files 读 cds.lib + README
3. **看参考**：发现 Test_ZSN 下已有 `FullAdder` 和 `FullAdder_1b` 两个参考 cell；pyAether 打开 FullAdder_1b（空，0 instance）；打开 FullAdder（5 instance）→ 用 str() cast 解析 emyString 属性，得到完整网表：
   - IXOR1 xor2Lx1: A→A, B→B, Y→n_ab_xor
   - IAND1 and2Lx1: A→A, B→B, Y→n_ab_and
   - IXOR2 xor2Lx1: A→n_ab_xor, B→CIN, Y→SUM
   - IAND2 and2Lx1: A→n_ab_xor, B→CIN, Y→n_cin_xor
   - IOR1 or2Lx1: A→n_ab_and, B→n_cin_xor, Y→COUT
   - SUM = A⊕B⊕CIN, COUT = (A·B)+((A⊕B)·CIN)
4. **查 API**：RAG search_apis 查 dbCrtNet/dbCrtTerm/dbCrtPinByNet/aeCrtWireLabelsAndPins/dbCreateInst/dbNewCellView；get_api_details 确认签名；查 emyShapeGetNetName/aeSaveDesign/aeGetCurDesign/dbOpenCVByType
5. **建电路**：dbNewCellView 建 FullAdder_2/schematic；dbCreateInst 放 5 门（2 xor2Lx1 + 2 and2Lx1 + 1 or2Lx1，同参考 FullAdder 拓扑）；dbCrtNet 建网络 + t.net 绑定；aeCrtWireLabelsAndPins 自动打引线；dbCrtTerm 建 I/O 端子；aeSaveDesign 保存
6. **验证 + 清理**：fresh process 重开验证连通性正确（15 条 emyLine wire）；发现 4 个问题：①15 个 autopin 残留 pin（basic/ipin/opin）②stray net Y ③I/O terms 用错访问器（cv.terms 不存在，应 cv.terminals）④emyText label 显示端子名而非网络名。修正：发现 cv.terminals 才是对的（A/B/CIN input, SUM/COUT output 都在）；删 15 个 autopin pin + stray term/net Y；用 dbuOrigin 解析 emyPoint 重 label 15 个网络名；aeSaveDesign 持久化
7. **最终验证**：fresh process 重开 → 5 门 / 5 I/O / 12 nets / 15 wires / 15 labels，无残留 pin/net/term；list_allowed_files 确认 sch.oa/master.tag/thumbnail/backup 在盘；检查 .cdslck 锁 PID 57215 属于活跃 Aether GUI 进程（与 FullAdder/FullAdder_1b 共享），合法不动
8. **交付总结**：学习要点 + 完成电路（路径、5 门、连通性、I/O、网表）+ stdcells_ac 未改动确认

## 选题理由

clean produce task：用户给一个明确目标（搭 FullAdder_2 单 bit 全加器）+ 约束（用 stdcells_ac 公共库、不能改、按命名规则选门）。Agent 全程自主完成（37 tool_uses，单条用户指令）。D-domain schematic_netlist。私有资产（/proj/trgqa、pyAether 沙盒、Aether GUI、2 个 skill 文件）不可在 eval 沙盒复刻 → B-grade synthesized。

## B-grade synthesized 设计

核心可自包含化：把「用 pyAether 在 Aether OA 库里搭原理图」抽象成「读 stdcell 库 JSON + 电路规格 JSON → 综合门级网表(CDL) + 真值表自验证」。

- **A（公开）**：一位全加器，L-class x1 单元（xor2Lx1/and2Lx1/or2Lx1/...），ports A,B,CIN→SUM,COUT，SUM=A^B^CIN, COUT=(A&B)|((A^B)&CIN)，5 门
- **B（隐藏）**：一位全减器，G-class x2 单元（xor2Gx2/and2Gx2/or2Gx2/invGx2/...），ports A,B,BIN→DIFF,BOUT，DIFF=A^B^BIN, BOUT=((~A)&B)|(BIN&(~(A^B)))，7 门（多 2 个 inv）
- **反硬编码**：A/B 函数不同（加 vs 减）、端口名不同（CIN/COUT vs BIN/BOUT）、单元名不同（L vs G class）、门数不同（5 vs 7）→ 硬编码 A 全加器网表在 B 上必败
- **判分**：check.py 独立解析 netlist.cdl + 独立重仿真真值表（不信任 verify.json），12 条 a-l 断言

## 自验

- ref solution: A PASS(5门) + B PASS(7门) ✓
- check() ref submit.zip → PASS 12/12 ✓
- 3 neg（empty/hardcode_a/wrong_logic）全 FAIL ✓
- §4.9 三假（empty_zip/print_expected/core_deleted）全 FAIL ✓
- NEG_RC=0 ✓
