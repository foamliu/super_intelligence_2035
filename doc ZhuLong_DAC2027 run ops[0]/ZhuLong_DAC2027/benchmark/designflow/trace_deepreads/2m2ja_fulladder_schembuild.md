# 深读笔记 — 2m2ja (sinanz / hfeg0pkn005) — FullAdder 原理图构建

**trace_source**: user=sinanz, host=hfeg0pkn005 (10.129.2.14), session_file=1793862562240_2m2ja.messages.json, match_count=197
**keywords**: schematic:304;cellview:233;pyaether:184;aether:149;rtl:104;dbcreateinst:93;lvs:74;dbopencv:73
**tools**: 221 schematic, 141 pyAether, 93 dbCreateInst, 33 "lang": "pyAether", 20 cellview, 2 netlist
**规模**: 119 msgs, 1 user turn（其余为 tool_result）, agent 25 个 assistant turn

## 用户意图（U#0 原文）
> 你好，现在你是一个资深的全定制电路设计工程师。接下来你需要学习 `/ai_sandbox/trgqa/V0_die2/agentdir/sinanz/Skills` 放置的 2 个 skill（查看分析 Aether 电路 + 自主编辑构建新电路），然后在个人工作路径 `/proj/trgqa/V0_die2/workdir/sinanz/Test_ZSN` 下生成一个名为 `FullAdder_3` 的单 bit 全加器电路。可调用公共库 `/proj/trgqa/V0_die2/libs`，基本逻辑单元在 `stdcells_ac`，**绝对不能改动公共库**。stdcell 命名规则：前缀=基本功能，紧接数字=输入端口个数，L/G/C/LV=管子类型，x1/x2/x4/x8=管子尺寸（例：or2Lx1=OR门 2 输入 L 管 x1 尺寸）。

## 真实工具链（agent 实跑）
- `SandBox_MCP_Server__run_code`（pyAether 沙盒）→ `import pyAether as ae`
- `RAG_MCP_Server__search_apis` / `get_api_details`（查 API 签名：dbCrtSchWireName, emyDMDestroyCellView, aeDelCell）
- `read_files` / `list_allowed_files` / `get_agent_policy_status`

## 关键 API 模式（从 agent 脚本提取）
- `ae.emyInitAether("-adv")`；`ae.emyString(s)` 包装字符串
- `ae.dbOpenCVByType(lib, cell, view, viewtype, "r"|"w")` 打开 cellview
- `ae.dbNewCellView(lib, cell, view, viewtype)` 新建
- `ae.aeOpenDesign(lib, cell, view, mode="edit")` + `ae.aeGetCurDesign()` → editable design handle `cur`
- `ae.aeDesignIsEditable(cur)` 校验可编辑
- `ae.dbCreateInst(cellView=cur, master=<symbol cv>, name=nm, point=(x,y), orient="R0")` 放 instance
- `ae.dbCrtNet(cur, name)` 建网；`inst.instTerms` 遍历端子；`term.net = netobj` 连接
- `ae.dbCrtTerm(net=, name=, dir=)` 建端子；`ae.dbCrtPinByNet(net=, name=, term=)` 建引脚
- `ae.aeCrtWireLabelsAndPins(instTerm=, isCrtLabels=, isCrtPins=)` 自动生成引线/标签
- `ae.aeSaveDesign()` 保存

## FullAdder_2 参照结构（agent msg18 读出，金标准）
- instances: IXOR1/IXOR2 master xor2Lx1, IAND1/IAND2 master and2Lx1, IOR1 master or2Lx1
- 拓扑：SUM = A^B^CIN；COUT = A·B + (A^B)·CIN
- term→net：
  - IXOR1: A→A, B→B, Y→n_ab_xor
  - IXOR2: A→n_ab_xor, B→CIN, Y→SUM
  - IAND1: A→A, B→B, Y→n_ab_and
  - IAND2: A→n_ab_xor, B→CIN, Y→n_cin_xor
  - IOR1: A→n_ab_and, B→n_cin_xor, Y→COUT
- 电源：vcc→vcc!, vss→vss!, vbp→vbp!, vbn→vbn!（每 instance 4 个电源端子全连）
- IO terminals: A/B/CIN=input, SUM/COUT=output
- 15 条引线（emyLine）+ 15 个标签（emyText，绑定真实网名）
- 12 个 net（5 信号 + 4 电源 + A/B/CIN/SUM/COUT 其余）

## agent 迭代历程（关键修正点）
1. msg20 首建：autopin 在 connect 之前 → 引线/标签未绑定真实网，电源端子未连（显示 ?）
2. msg24-30：补电源网 vcc!/vss!/vbp!/vbn! + 清残留 Y 网/端子
3. msg32-53：发现标签质量问题（FullAdder_2 标签绑定真实网名，自己的未绑定）→ 关键洞察：**正确顺序=先建网并连 t.net，再做 autopin**
4. msg55-68：aeDelCell 删除重建失败（锁文件/dbNewCellView 返回 None）→ 改「就地清空内容再重建」
5. msg68 最终构建：clear（destroy instances/shapes/nets）→ place 5 gates → dbCrtNet 建所有网 → connect signal term.net → connect power term.net → aeSaveDesign
6. msg75 finalize：删孤立 emyText 标签 + 删 spurious Y net/term + aeCrtWireLabelsAndPins(isCrtPins=False) 重建标签 + setText(真实网名) + 清 P__ pins + aeSaveDesign
7. msg70 验证：5 instances 正确，nets 含 vcc!/vss!/vbp!/vbn!/n_ab_*/SUM/COUT/A/B/CIN

## 合成决策（B-grade synthesized L1）
- 真实 produce = pyAether 脚本构建 FullAdder_3（需 Aether + Test_ZSN 库 + stdcells_ac 公共库，均在 /proj/trgqa 项目受限路径，.75 不可达 → 无法 L2 真跑）
- B 档重构：交付 = **spec-driven pyAether 构建脚本** `build_schem.py`，读 `spec.json`（cell 名 / gates[name,master,x,y] / termnet / io / power 映射）→ 用 pyAether API 构建原理图
- 提供 `pyAether_mock.py`（录制 stub）作 asset，check.py 用 subprocess `python3 build_schem.py` 跑候选脚本（mock 录制 dbCreateInst/dbCrtNet/term.net=/dbCrtTerm/aeSaveDesign 调用）→ 断言录制结构
- 隐藏 B = 2-to-1 Mux（gates: 2×and2Lx1 + 1×or2Lx1 + 1×invx1；Y=(I0·~S)+(I1·S)），与 A（全加器）拓扑/网名/门集完全不同 → 反硬编码
- L1 离线可验（subprocess 跑 mock，无 Aether 依赖），满足 §4.2 真跑候选（subprocess 执行候选脚本断言输出结构）
- 16 条件 a-p，对应 16 条断言

## 反硬编码设计
- 脚本必须 spec-driven（读 spec.json），不许硬编码 FullAdder_3 门表
- check.py 只跑 B（mux spec），A-spec 仅给 SUT 看作示例（在 prompt/assets）
- B 与 A：不同 cell 名（FullAdder_3 vs Mux2to1）、不同门集（xor2Lx1+and2Lx1+or2Lx1 vs and2Lx1+or2Lx1+invx1）、不同网名（n_ab_xor/n_cin_xor vs n_s_i0/n_sbar_i1）、不同 IO（A/B/CIN/SUM/COUT vs S/I0/I1/Y）
