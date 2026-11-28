# in0l4 deepread — chengk@hfeg0pkn002, MOS W-by-layer export

session: 1795694511383_in0l4.messages.json (1.15MB, 214 msgs, 120 user / 94 asst)
user: chengk, host: hfeg0pkn002, mc=283, domain: schematic_netlist (cellview:475+schematic:321+pyaether:318+netlist:94 主导)
agent: lead (pyAether 代码工程师 system_prompt)

## 真实任务
用户写 `mos_w_export.py`：从当前激活 schematic cellview 出发，递归往下 3 层，按 master cellName 关键字识别 MOS（nmos/pmos/nch/pch + 工艺命名 ptn/ptk/ntn/ntk），逐 MOS 读 W 宽度，按 Layer0–Layer3 分组写出 `/home/chengk/Desktop/layout/mos_w_by_layer.txt`。

## 核心技术链路（已核实 API）
- `aeGetCurDesign()` → emyDesign；`aeDesignIsSchematic(cv)` 校验
- `emyDesign.instances` 属性 → 该设计所有 emyInst 的 tuple
- `emyInst.getCellName/getLibName/getViewName/getName`：**out-param 方法**（传 emyScalarName 填充），非属性
- `emyDesign.open(lib, cell, view, mode)` 打开子设计 schematic view 下钻
- `emyInstGetParam(inst, emyString("W"), param)` 读 W（paramName 是 emyString 类型）
- `inst.cdfParameter` 属性 → tuple of ParamDef（含 w 参数 Value/DefValue/mostype/model）

## 关键踩坑（判分要点）
1. **`emyScalarName(ns)` 空构造失败**——必须 `emyScalarName(ns, "*")` 占位；`str(scalarName)` 返回 `(name)` 带括号须清洗。
2. **`emyInstGetParam("W")` 抛 `SystemError: Invalid parameterized design`**——未参数化 pcell 读不到 W；须回退 `inst.cdfParameter` 解析小写 `w` 参数，`Value` 是 `pPar("WP")` 符号时取 `DefValue`（0.82u）。
3. **工艺库 MOS 命名 ptn/ptk(PMOS) 与 ntn/ntk(NMOS)**，非 nmos/pmos——关键字集须覆盖工艺命名，否则抓 0 行。
4. **`emyVectorInst.getName` 不接受 emyScalarName**——须 `.name` 属性回退（scalarInst 与 vectorInst 共用 `.name`）。
5. **`emyDesign.open` 须 emyScalarName 参数**非裸字符串；mode 用 char `'r'`。
6. **环检测 per-path**（visited 集合递归返回时移除），非全局去重——同一 cell 经不同兄弟分支到达仍各自展开。
7. `emyDesign` 有便捷属性 `libName/cellName/viewName` 直接返回名称串。

## 真实沙盒运行结果
沙盒有激活设计 `drcqa_digital/AF_AryTop`（schematic，74 顶层实例，全 scalarInst）。递归下钻：AF_AryTop→AF_AryHalfTop(91)→AF_LvfsblnBuf→AF_FswellGen 等。MOS 只在 Layer3 出现（深层 device）。最终跑出 **664 条 MOS 行**（全 Layer3），W 值真实解析：ptk_lv=12.38u、ntk=62.75u、ptn/ntn_m=0.82u、dlyrc_gut 的 ptn=2.762u/ntn_m=1.534u/1.3u 等。unique cells: ptn(178)/ntn_m(178)/ntk(132)/ptk_lv(88)/ptk(88)。

## case 设计（task_id=MosWByLayerProduce-001, LIVE-NA, judge_layers=[L0,L1]）
synthesized-reframe: live Aether GUI + aeGetCurDesign + emyInstGetParam/cdfParameter 不可沙盒 → spec 驱动层次遍历器 `mos_w_layer_plan.py`（纯 stdlib）。
- **A**(visible) spec_A.json: ChipTop 7 设计层次，含 ptn/ntn_m/ptk_lv/ptk/ntk 工艺 MOS、pPar("WP") 符号 W(Mtop→defvalue 0.82u)、Mn4 无 w 字段→<not-found>、CycA↔CycB 环(CycB→CycA 阻塞)、inv 超 max_depth=3 不下钻(其 MP0/MN0 不收集)。gold: total=7, per_layer{0:1,1:2,2:2,3:2}, unique_cells=[ntk,ptk_lv,ntn_m,ptk,ptn]
- **hidden B**(token-structurally 不同) spec_B.json: AnaTop 模拟树, max_depth=2, MOS cell nch/pch/pmos, W 4.0u/1.2u(pPar→defvalue)/0.6u/0.9u, mimcap 非 MOS 负闸门。gold: total=4, unique_cells={nch,pch,pmos} → A 硬编码器全错
- **reference** mos_w_layer_plan_ref.py: spec 驱动通用实现(is_mos_cell 子串匹配 + _strip_symbolic pPar 回退 + collect_layer 递归 per-path visited + build_report)
- **check.py 15 conds(a-o)**: a zip 含 py ②b py_compile ③c 反空壳 ④d report_A 字段齐全 ⑤e A total==gold(独立 stack-DFS 复算) ⑥f per_layer==gold ⑦g W pPar 回退(Mtop→0.82u)+Mn4→<not-found> ⑧h 工艺关键字 5 cell 齐全 ⑨i max_depth 截断(无 layer>3, inv MP0/MN0 不出现) ⑩j 环检测(有限+Mb 存在+无 CycA 两次) ⑪k output_txt 格式 ⑫l 负闸门(非 MOS cell 不收) ⑬m B total==gold_B(4) ⑭n B unique_cells 集合==gold_B+B top=AnaTop ⑮o <not-found> 处理
- **negatives**(3): print_expected(硬编码 A，B total 7≠4 → fail m) / core_deleted(空 report，A total=0 → fail e) / w_symbolic_wrong(W 不回退 defvalue，Mtop='pPar("WP")' → fail g) — first-fail distinct(m/e/g), negative_selftest 全 FAIL
- **自验**: ref PASS(15 conds) + 3 neg 全 FAIL distinct + SKIP_RUN=1 案例加载/workdir leak 自检通过(D jsonl 613 cases)
