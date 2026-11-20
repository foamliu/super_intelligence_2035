# Deepread: 1794377141256_03wfm (shanliny@hfeg0pkn005)

- **Session**: 1794377141256_03wfm
- **User**: shanliny
- **Host**: hfeg0pkn005 (10.129.2.14)
- **Messages**: 75 (user 40 / assistant 35)
- **Match count**: 34
- **Keywords**: netlist/analog/schematic (D-purity high)
- **Selected for**: r779, case `EDA-Eval-DesignFlow-RcNetVizRcalc-001` (schematic_netlist, A档 trace-faithful)

## Real Task

用户 shanliny 附 `test.netlist`（StarRC/Calibre PEX 后仿抽取段），先问 (U#1) `XBKB.XBK_CNT.XXDEC0.SHARE` 在整条 rc net 中与底下几个晶体管的位置关系，以及一个仿真现象：只留 XBC 的 p 管 + FCK[0] 的 p 管时 FCK[0] p 管 s 极 = 0V，加上 FCK[1..3] 的 p 管后 FCK[0]/[1] p 管 s 极出现 200mV（pwr=1.02V）——根因是共享 rc 走线寄生电阻在多管并联时形成分压/耦合。随后 (U#25/idx=25) 明确交付请求：**「写一个能将这根 rc 连线、net xxx 和底下几根晶体管位置关系可视化的脚本，同时能快速估算指定两点之间的电阻」**。

## Assistant Tool Chain

`get_agent_policy_status` → `list_allowed_files` → `read_files(test.netlist)` → `editor(rc_analysis_share.py)` + `run_approved_command` 迭代分析 → 后段转 `editor(rc_viz_tool.py)` 多轮迭代（26→58 多次 editor + run_approved_command 验证），最终交付 `rc_viz_tool.py`（281 行，11738 B，仍在主机 /home/shanliny/rc_viz_tool.py）。

## Gold Deliverable

`rc_viz_tool.py`：
- 解析 `*|S (NET:k x y)` 走线节点坐标 / `*|I (dev:term dev term B 0 x y)` 晶体管端子接触点 / `Rxxxx n1 n2 r` 电阻 / `Cg|Cc` 寄生电容（忽略）。
- 构图 → 连通分量（seed = `-n` net 名）→ 器件分类（XBC / FCK / CT / OTHER）。
- 等效电阻：节点分析（nb 接地、na 注入 1A，V(na)=R），`np.linalg.solve`，处理并联/网格（非简单串加）。
- CLI：`<netlist> [-n NET] [-r A B] [--nodraw] [-o OUT.png]`；matplotlib 可视化走线（log10(R) 着色）+ 器件端子标注 + 高亮电阻两端。

## A 资产 / B 隐藏

- **A**（可见）：真实 test.netlist，net XBKB.XBK_CNT.XXDEC0.SHARE，94 节点 / 109 R / 16 晶体管端子（FCK[0..3].MIMP0/@2 + MPM_XBC/@2/@3 + ncr_X755.X63 接触）/ 78 *|S / 16 *|I。oracle R(MPM_XBC:d → FCK[0].MIMP0:s) = 339.228 Ω。
- **B**（隐藏，同拓扑变换）：hierarchy XBKB→XBKB2 / XXDEC0→XXDEC1 / ncr_X755.X63→X64，R 按 1+0.13*(idx%5) 非均匀缩放（1.0/1.13/1.26/1.39/1.52）；oracle R = 447.313 Ω。反硬码：B 输出不得含 A 独有串（XBKB.XBK_CNT.XXDEC0 / ncr_X755.X63）或 A 的 R 值 339.228。

## check() 12 条断言 (a–l)

a zip 含 rc_viz_tool.py ② py_compile ③ B 上 --json -r exit0 + JSON + 4 顶层键 ④ resistors==109 ⑤ dev_terminals==16 ⑥ component.nodes==94 ⑦ 16 条 transistor_terminals 结构+kind ⑧ R∈447.313±2.0 ⑨ 反硬码名 ⑩ 反硬码值 ⑪ 交叉验证 A 上 R∈339.228±2.0 ⑫ 3 次确定性。

## 自验

reference PASS 12/12（R_B=447.3132, R_A=339.2275, anti-hardcode clean, deterministic）；3 negatives（empty/print_only/deleted_core）全 FAIL；negative_selftest exit 0。

## Infra note (r779)

r774–r778 INFRA-BLOCK 根因 = `eda_flow.open_session` 需强制 `task_id`/`eval_id` 参数（旧调用缺参 → "task_id/eval_id missing"）；read_file/list_files 需 session workdir 内路径。r779 传 `task_id=DesignFlowD-r779, eval_id=20261116-run01, user=shardD` → open_session OK，run_commands 以 **e0031982** 身份在 hfhds201 执行，ssh 到 698 台机免密全通 → INFRA-BLOCK 解除。pyAether 通道（t0002997 身份）ssh 远端仍 publickey 拒，但 eda_flow run_commands(e0031982) 可用，足够取 trace。
