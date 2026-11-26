# 深读笔记 — 1795002165385_19znu（DBUS TB I319 buffer 删除+短接 · L1 schematic_netlist）

- **trace**: `/home/reedchen/.cline/data/sessions/1795002165385_19znu/1795002165385_19znu.messages.json`（reedchen @ hfeg0pkn004=10.129.2.13, mc=159, 100 msgs / 58 user / 42 assistant, 524KB）
- **来源**: r944 fresh D-pure 候选 → r966 选中
- **keywords**: schematic_netlist 域（pyAether emyDesign/emyInst/emyNet 网表编辑，buffer 删除+net merge）
- **domain**: schematic_netlist（原理图实例删除 + 网络合并保存）

## 用户意图轮（U#22 = msg 22，A档合规：提出需求✓ 未给根因/修复✗）

> 「我现在想修改下ReedChenWork TB_Dbus_tb_0810_1010_write这个cell，请你先理解这个cell，然后帮我把I319这个buffer删掉」

注：U#0 是 meta「告诉我你的工作目录」(81ch)，非任务轮；U#22 才是真实 cell-editing 需求。

## assistant 工具链（42 assistant msgs）

- `RAG_MCP_Server__search_apis` / `get_api_details` 检索 emyDesign/emyInst/emyNet/emyInstDestroy API 族
- `SandBox_MCP_Server__run_code` (pyAether) 执行：
  - `dbOpenCV(ReedChenWork/TB_Dbus_tb_0810_1010_write/schematic)` → 顶层仅 7 实例（I0=子电路 + 6 pin）
  - 深入子电路 `ddgoa_cmos_work/Dbus_tb_0810_1010_write/schematic`（787 实例）枚举定位 I319
  - 内省 `inst.instTerms` / `getTermName` / `getNet` / `net.name` 确认 I319 端子连接
  - `net_in.merge(net_out)` 短接 net460→net462，`emyInstDestroy(i319)` 删 buffer
  - `cv.save()` 落盘 + 反向验证（instCount 787→786，net460 销毁，net462 保留 2 端子）
- `editor` 写交付脚本 `remove_dbus_tb_i319_buffer.py`
- `ask_question` 与用户确认短接方案（用户选「先短接再删」）

## GOLD（msg 99，assistant 最终交付）

### cell 结构理解
- ReedChenWork 顶层 `TB_Dbus_tb_0810_1010_write`（testbench）仅 7 实例；I319 实际在其唯一子电路 `I0 = ddgoa_cmos_work/Dbus_tb_0810_1010_write`（schematic, 787 实例）内
- **I319**: master=`stdcells_am/bufPFx24`（24x buffer），端子 `A→net462`(输入), `Y→net460`(输出), vbp/vbn/vcc/vccz/vss/vssz 接电源/体偏
- net462 由 `I_switch_54/z` 驱动；net460 接负载 `I316/A`

### 执行操作（已落盘）
1. **短接**：`net460(Y)` merge 进 `net462(A)`（net460 销毁，net462 保留为合并节点）
2. **删除**：`emyInstDestroy(I319)`，instCount 787→786
3. **保存**：`cv.save()` → `/proj/ddgoa/V0/libs/ddgoa_cmos_work/Dbus_tb_0810_1010_write/schematic/sch.oa`（saveTime 2026-11-18 20:08:32）

### 反向验证（均通过）
- I319 不存在，`bufPFx24` master 已无
- net460 不存在，net462 保留
- 合并后 net462 含 2 端子：`I_switch_54/z`(驱动源) + `I316/A`(原 net460 负载) — 信号直达负载，无悬空

### 交付脚本
`/ai_sandbox/ddgoa/V0/agentdir/reedchen/remove_dbus_tb_i319_buffer.py` — 独立可复现函数 `remove_i319_buffer(lib, cell, view, save)`，打开→定位 I319→捕获 A/Y net→merge(Y into A)→emyInstDestroy→cv.save。

## L1 case 设计（EDA-Eval-DesignFlow-I319BufferDelete-001）

- **input A**（公开，真实 trace 数据）: `cell_desc_A.json` — Dbus_tb_0810_1010_write 子电路的实例/网络描述（I319=bufPFx24, A→net462, Y→net460; driver I_switch_54/z; load I316/A; 787 实例）
- **input B**（hidden，防硬编码）: `cell_desc_B.json` — 平行结构但不同 cell 名/不同 I319 master/不同 net 名（I319=bufPFx12, A→net88, Y→net90; driver I_drv_7/z; load I_rcv_15/A; 642 实例）
- **deliverable**: `outputs/submit.zip` 含 `solution.py`（读 cell 描述 JSON + 目标实例名 → 短接 A/Y net + 删实例 + 写输出 JSON）
- **check.py**: 12 断言（zip 结构 / 非空 / 非纯 print / A: I319 缺失+net460 缺失+net462≥2端子+inst_count=786 / B: I319 缺失+net90 缺失+net88≥2端子 / 反作弊: print-stub FAIL / 删不短接 FAIL）
- **A-faithful**: task prompt = U#22 verbatim；task_brief ≤3 行仅接口
