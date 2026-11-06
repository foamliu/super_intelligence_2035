# 深读笔记 — sid 1793877524011_cu3nb (sinanz @ hfeg0pkn005, mc=345)

## trace 概况
- 文件: `/home/sinanz/.cline/data/sessions/1793877524011_cu3nb.messages.json` (1,603,205 B, 320 msgs, 166 user / 154 assistant)
- 来源: snapshot `hourly-new.2026-11-06_1800`（live 文件已 rotate；ssh+cat 取回 .75 workdir）
- 工具分布(keywords): schematic:719 netlist:504 lvs:264 aether:251 pyaether:249 cellview:176 cmos:140 verilog:99
- 工具列: 674 schematic 452 netlist 184 pyAether 60 "lang":"pyAether" 47 dbCreateInst 43 cellview 11 hspice 4 virtuoso
- domain: layout_aether（pyAether schematic 构建）

## 用户意图（两轮需求）
- **U#1 (idx=0) "提需求"**：资深全定制电路设计工程师角色；学 `/ai_sandbox/trgqa/V0_die2/agentdir/sinanz/Skills` 下的 2 个 skill（查看/分析 Aether 电路 + 自主编辑构建新电路）；在 `/proj/trgqa/V0_die2/workdir/sinanz/Test_ZSN` 下生成 `FullAdder_4` 单 bit 全加器；可调公共库 `/proj/trgqa/V0_die2/libs`（基本逻辑单元在 `stdcells_ac`，**绝不改动公共库**）；讲解 stdcell 命名规则（前缀=逻辑类型，数字=输入端口数，L/G/C/LV=管子类型，xN=栅宽/驱动尺寸）。→ **A 档可用轮**（纯需求，未给根因/方案）。
- **U#33 (idx=56) "提需求"**：「太强了，你竟然一次做对了！接下来，你试着再做一个 4-16 译码器电路。」→ 第二个需求轮。

## assistant 工具链（FullAdder_4 部分，idx 0–55）
1. list_allowed_files (agentdir / workdir / libs) + get_agent_policy_status
2. read_files Skills/ReadSchematic.md + SchematicEdit.md
3. list_allowed_files stdcells_ac / Test_ZSN（含 FullAdder_2 / FullAdder_1b 既有 cell）
4. read_files cds.lib + ...
5. **SandBox_MCP_Server__run_code** (pyAether) emyInitAether("-adv") 探活
6. **editor** 写 `build_full_adder4.py`（6215B）→ 编辑修正 → read 复核
   - 逻辑: SUM=A^B^CIN, COUT=(A&B)|((A^B)&CIN)
   - 门: 2×xor2Lx1 (IXOR1/IXOR2), 2×and2Lx1 (IAND1/IAND2), 1×or2Lx1 (IOR1)
   - nets(12): A B CIN SUM COUT n_ab_xor n_ab_and n_cin_xor vcc! vss! vbp! vbn!
   - terminals(5): A/B/CIN=input, SUM/COUT=output
   - 流程: dbNewCellView → aeOpenDesign(edit) → dbCreateInst(摆门) → dbCrtNet(建 net) → instTerm.net=连接(signal+pwr) → dbCrtTerm+dbCrtPinByNet(顶层端口) → aeCrtWireLabelsAndPins(走线标签) → 删 ipin/opin 短路实例 → 删 spurious Y net/term → 清 P__ pinfigs → setText 真实 net 名 → aeSaveDesign
7. run_code 执行 build → **SAVED | nets:12 terminals:5** (placed: IXOR1/IXOR2/IAND1/IAND2/IOR1)
8. **editor** 写 `verify_full_adder4.py` → run_code 验证:
   - NETS count=12 exact match, missing=NONE extra=NONE
   - TERMINALS ['A','B','CIN','COUT','SUM'] exact
   - 每 instance conn_ok=True pwr_ok=True（A/B/Y→正确 net, vcc/vss/vbp/vbn→电源 net）
   - **FINAL: PASS**
9. cleanup_full_adder4.py (清 lock/backup) → run_approved_command

用户 U#33 反馈「一次做对了」→ FullAdder_4 任务验收通过。

## 后续（4-16 译码器，idx 56+，本 case 不用）
build_decoder_4_16 v1/v2/v3 + 3-8 子 decoder + CDL netlist 导出(dmExportNetlist/cdlOut) + finesim 仿真提交/监控/调试。多轮迭代。

## 抽取的确定性核心（本 case）
「逻辑表达式 → 门级原理图网表」综合：给定 CELL spec（PORTS/POWER/GATELIB/EXPR 嵌套布尔表达式）+ stdcell catalog，每个 EXPR 内部节点(AND/OR/XOR/NAND/NOR/NOT/BUF)→一个 gate 实例（master 按 func 从 catalog 选），叶子=输入端口，门输入引脚按子节点 net 连、输出引脚连本节点 net(中间 n1/n2.., 根→输出端口)，电源引脚连电源 net，顶层端口建 terminal → 结构化 JSON。纯离线 Python(stdlib)，不调 pyAether。

## case 设计
- id: EDA-Eval-DesignFlow-CombCellNetlistSyn-001
- domain: layout_aether, track: B-synthesized, layer: L1-boundary
- A(可见): FullAdder_4 spec + stdcells_ac catalog(6 master)
- 隐藏 B: Mux2to1 spec(Y=OR(AND(A,S),AND(B,NOT(S)))) + catalog(7 master, 含 and2Lx2)
  → B 用 NOT/invx1 + and2 + or2 (4门), A 用 xor2+and2+or2 (6门, XOR(A,B)两处不共享) → 不同门数/不同 master mix/不同端口数 → 杀硬编码
- 判分 14 条(a–n): ①zip+py_compile+stdlib ②--help/no-arg ③B 跑+JSON keys ④B master 在 catalog ⑤B terminals==spec ports ⑥B used net 都声明 ⑦B 电源 net 齐+门电源引脚连电源 ⑧B **门级仿真==spec 表达式真值表**(核心功能性断言) ⑨B 每输出被门驱动 ⑩B 无悬空信号引脚 ⑪跨输入守卫 A 仿真正确+A≠B 结构 ⑫确定性 sha256 ⑬B 门数==表达式内部节点数 ⑭B 输出不与输入同名+无两门驱动同一 net
- 自验: ref PASS 14/14; 5 negative(empty/print-expected/core-deleted/hardcode-B/naive-onegate)全 FAIL(NEG_RC=5/5); §4.9 (a)(b)(c) 三假全 FAIL; test==disk roundtrip sha=dcb4f4eb; check.py 自包含(A/B 内嵌字面量, 无路径依赖); 泄漏隔离: SUT wd 仅 submit.zip + spec_A/catalog_A/task_brief, 无 reference/check.py/jsonl/hidden/B
- 断言闸门: k_rationale=k_check=14>=8 GATE PASS ✓
