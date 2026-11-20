# jjg2c 深读 — stdcell-from-netlist schematic/symbol 构建 (L2 Aether)

## trace_source
- session: `1794897784136_jjg2c` (jiashengz@hfeg0pkn002, mc=99)
- keywords: schematic:260;netlist:179;pyaether:137;aether:111;cellview:104;dbopencv:62;drc:41;lvs:27
- D-pure: D-score=439 (schematic+netlist+pyaether+aether+cellview) >> C-score=68 (drc+lvs)
- 42 msgs / 24 user turns (多为 tool_result 回执); 368KB messages.json
- 真实路径: `/home/jiashengz/.cline/data/sessions/1794897784136_jjg2c/` (含 .messages.json + .json)
- ledger: r979 claim (schematic_netlist, D-pure fresh 候选)

## 用户意图 (verbatim, A-faithful 候选)
- 用户调用 slash-command `stdcell-from-netlist`，skill args（=用户原话）：
  > 「在 R1b3 库中画出 D_KD145 及其子模块 LATCH05C、BUF2X6 以及标准单元 NOT、TRI_NOTAD 的电路（schematic/symbol），依据给定的网表和 layout guide。不要操作其他库，禁止探测和读取 R1b 和 R1b2。」
- U#0 = skill 输入：60KB 标准单元网表 guide，含 **12 个 .SUBCKT** 定义 + 尺寸参数 + pin 定义 + 拓扑说明 + 画图 guide：
  - 6× NOT 变体 (NOT_W03_W05_L005 / _L008 / NOT_W05_W10_L005 / _L008 / NOT_W05x2_W10x2_L008 / NOT_W05x6_W10x6_L008)
  - 3× TRI_NOTAD 变体 (tristateable inverter, AD variant, 4-pin QN/AD/B/C)
  - BUF2X6 (2× cascaded NOT, 2-pin IN/OUT)
  - LATCH05C (latch, 4-pin CK/D/Q/Qn)
  - D_KD145 (顶层, 10-pin ADD_TS1_L3/CK0-3/OS0-3/RDAP_BA_LT_TS0)
- 用户明确：「不要操作其他库，禁止探测和读取 R1b 和 R1b2」= 只在 R1b3 建库

## assistant 工具链 (L2 真跑 pyAether)
1. **context gathering**: list_allowed_files → read AGENT_CONTINUATION.md + build_R1b2_leaf.py + skill_stdcell_from_netlist.md + SKILL_WiringByNetlist.md + README_stdcells_TECHLIB 识别报告
2. **env probe**: `ae.emyInitAether("-adv")` + `ae.emyInitDb()` → dbGetAllCells(R1b3)=[] (fresh) → dbGetAllLibs 不含 R1b3
3. **API search**: RAG search_apis("create library") → dbCreateLib / dbNewCellView / dbOpenCV / dbCrtInst / dbCrtSchWire / dbCrtNet / aeCreatePin
4. **Stage 1 — 6 NOT 叶子**: dbCreateLib(R1b3) → 逐 cell 建 symbol+schematic (PMOS+NMOS instance + wire + pin)
5. **Stage 2 — 3 TRI_NOTAD 叶子**: 2×ptn + 2×ntn series stack (tristate)
6. **Stage 3 — BUF2X6**: 2 cascaded NOT instances → 遇 `inst.instTerms["A"]` bug (instTerms 是 iterable 非 dict) → 修迭代
7. **Stage 4 — LATCH05C / D_KD145**: 层次化构建（上层实例化下层）
- 多个 pyAether API 坑：instTerms dict-keying / dbNewCV 返回 False (leftover state) / transient caching / getAllShapes 不存在

## gold standard
- R1b3 库内建成 12 个 cell，每个含 symbol + schematic 两个 view
- symbol: pin shapes + rect + 正确 pin 名/位置
- schematic: transistor instances (PMOS/NMOS) + wire 连接 + 正确 net 拓扑
- 叶子 cell (NOT/TRI_NOTAD): 直接 transistor; 复合 cell (BUF2X6/LATCH05C/D_KD145): 实例化下层 cell

## 判分牙设计提案 (next round)
- **A 档 trace-faithful**: prompt = 用户 verbatim skill args (slash-command 调用，真实形态); A 资产 = 60KB 网表 guide (jjg2c_stdcell_netlists_A.txt)
- **交付**: `outputs/submit.zip` 含 `build_stdcells.py` (pyAether 脚本，在给定库建 cell 的 symbol+schematic)
- **隐藏 B**: 另一组 stdcell 网表 (NAND2/NOR2/XOR2/AND2/OR2 变体 + 1 个复合 cell 如 AOI21)，token 与 A 不相交；check 只跑 B
- **check.py (≥8 断言)**:
  - (a) zip 含 build_stdcells.py + py_compile 通过
  - (b) 脚本有 dbCreateLib 或等价建库调用
  - (c-f) 在 B 的 fresh 库上真跑脚本 → 每个目标 cell 的 symbol view 存在 (emyDMIsCellViewExist / dbOpenCV)
  - (g) 每个 cell 的 schematic view 存在
  - (h) 叶子 cell 的 schematic 含正确数量 transistor instances (dbGetInst count)
  - (i) 复合 cell 的 schematic 含正确数量下层 cell instances
  - (j) pin 名正确 (aeGetTerms / instTerms)
  - (k) net 拓扑正确 (至少 1 条关键 net 的 source/target inst+pin)
  - (l) 反硬编码: B 库名/cell 名与 A 不相交 (A-only token 词边界 0 泄漏)
  - (m) 反硬编码: B 上 transistor instance type 正确 (PMOS/NMOS by netlist, 非 A 的固定值)
  - (n) 退化提交: 空壳/只 print/删核心 → Aether 建库失败或 cell 缺失 FAIL
- **L2 真跑**: check.py 经 eda_flow run_code(lang=pyAether, host=aether) 在 B 上执行候选脚本; subprocess 验证 cellview/inst/net
- **难点**: 需 .75 Aether 可用 + 设计 B 网表 (5-8 个 stdcell) + 参考 build 脚本 (复用 trace 中 assistant 的 build 逻辑)

## triage 判定
- **可造**: ✓ 真实 trace + ✓ 有牙 check() (L2 Aether 真跑 + 反硬编码 B)
- **形态**: A 档 trace-faithful (slash-command 真实形态) + L2 produce-from-scratch (build script)
- **D 域**: schematic_netlist (schematic 构建 + netlist 解析) ✓
- **deferred 原因**: L2 case 需 ~30min (B 网表设计 + 参考 build 脚本 + check.py Aether 验证 + negatives); r979 时间预算 (40min) 已用于 fresh 池发现 + 本深读
- **next round 第一优先**: 合成 jjg2c case (本深读已完整, netlist A 资产已落盘 designflow/trace_deepreads/jjg2c_stdcell_netlists_A.txt)

## 关键 API (供 next round 参考)
- ae.emyInitAether("-adv") + ae.emyInitDb() — 初始化
- ae.dbCreateLib(libname, path) — 建库
- ae.dbNewCellView(lib, cell, view) / ae.dbOpenCV(lib, cell, view, "w") — 建/开 cellview
- ae.dbCrtInst(cv, lib, cell, view, name, x, y) — 实例化 (下层 cell)
- ae.dbCrtSchWire / ae.dbCrtNet — 连线
- ae.dbCreatePin / ae.dbCrtSymbolPin / ae.dbCrtSymbolRect — symbol pin/图形
- ae.dbChangeLayer(shape, layer) — 改层
- ae.dbGetInst(cv) / inst.instName / inst.instTerms (iterable, 非 dict) — 查询
- ae.dbGetAllCells(lib) / ae.dbGetAllLibs() — 枚举
- 坑: instTerms 是 iterable 非 dict-keyed; dbNewCV 可能因 leftover state 返回 False; getAllShapes 不存在
