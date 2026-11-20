# r263 深读 — j5z4v (shanksw@hfhds201) — cm1 testmode 电压域计数

- **trace**: `1793864789160_j5z4v` · user `shanksw` @ `hfhds201` (10.129.32.75 域) · mc=121
- **keywords**: aether:997 netlist:177 schematic:98 cmos:73 analog:62 verilog:36 hspice:12
- **session**: 204 msgs, 6 real user turns, 987KB
- **NEW user** (shanksw 首个 shard C case)
- **agent**: lead, 工具链 = list_allowed_files / read_files / run_approved_command(python-runner) / editor / run_commands — 未用 pyAether/dbGet，全程用 Python regex 离线解析 flat SPICE presim 网表 `/home/shanksw/netlist.presim~`

## 用户真实意图（U0 idx=0，提出需求，未给根因/未给方案）
> 「你好，请问可以数一下在 DDGOA 在 WOWTOP 中的 CMLeft 里，从 CMLeft 里面出来的 cm1 的 testmode，一共有多少个吗？」

U1/U2/U3/U4/U5 = 同一需求的细化/重复（U2 明确定义「cm1 testmode = 所有在 WOWTOP 里从 CMLeft 出来的、信号名前三个字符是 'cm1' 的信号」；并要求分类接向 vdd2h 电压域 vs vintcore 电压域的电路各有多少）。

## grounding（agent 真实产物路径与逻辑）
- 设计：DDGOA (DDR5 DRAM), V0_20261029_DFT；层次 DDGOA → WOWTOP → **ChanEdgeL** → **XI_CMLeft_712 (CMLeft, lib ddgoa_cmos_esd/digital)**
- 网表文件：`/home/shanksw/netlist.presim~`（flat SPICE presim，~200MB，DDR5 私有，对 e0031982 在 pyAether sandbox 不可访问）
- CMLeft 总端口 990，cm1_* 相关端口 704
- agent 写了 ~25 个迭代 Python 脚本 (search_netlist.py / search_hier.py / search_cm1_v1..v13 / trace_cm1_domain / trace_v2/v3/v4 / trace_final / trace_s1..)，最终用 `trace_v3a` 思路：
  1. `.SUBCKT CMLeft <ports...>` 取端口列表（含 `+` 续行）
  2. 过滤端口名 `startswith('cm1')`
  3. 在父级里找例化语句 `XI_CMLeft_712 <conns...> CMLeft`，按位置 port→conn
  4. `determine_domain(conn, parent_body, parent_ports, port)` 判定电压域：
     - `inh_vdd2h` → vdd2h；`inh_vintcore`/`inh_vintcoredq` → vintcore；`inh_vdd1` → vdd1；`inh_vss` → vss
     - conn 是父级端口 → parent_port
     - `'vdd2h' in conn.lower()` → vdd2h；`'vintcore' in conn.lower()` → vintcore
     - 否则 search parent body / unknown
  5. group = 端口名第 2 个下划线 token (cm1_ag_*/cm1_ts_*/cm1_fc_*)
- 最终答案（msg#199，用户接受）：**从 CMLeft 出来的 cm1 testmode = 98 个** → vdd2h 域 **79**（全部 cm1_ag_*：3 显式 Test + 48 Trim 校准 + 34 温度传感器）+ vintcore 域 **19**（13 cm1_ts_* 测试设置 + 6 cm1_fc_* 精细控制）。经 ChanEdgeL 转接各自电压域。

## 为何 B 档重定义为离线解析器
真实 netlist.presim~（DDR5 私有 200MB）对 e0031982 不可访问，无法取真实网表作 A 输入；但 trace grounding 价值在「flat SPICE 网表 → 子电路端口提取 → 前缀过滤 → 父级例化位置映射 → 连接 net 电压域分类」的规范提取。故重定义为离线 stdlib 命令行工具 `cm_testmode_count.py <netlist> --subckt <name> [--instance <inst>] --prefix <prefix> -o <out.json>`，合成小规模 SPICE 网表作 A/B/B2。

## DISTINCT from 现有 layout_aether 系
r222 SchOaInventoryExtract（OA 库 inventory）/ r238 LayoutFloorplanGen（floorplan 生成）/ r252 LayStructExtract（layout 结构提取）/ r226 PcellPatternGeoDiag（pcell 几何诊断）/ r253 PinListPortOrderExtract（pin 端口顺序）/ r254 EmyCdlNetlistExtract（CDL netlist body）—— 本 case 是 **flat SPICE 网表子电路端口前缀过滤 + 父级例化位置映射 + 连接 net 电压域分类计数**，非 OA inventory / floorplan / layout 结构 / pcell / pin 顺序 / CDL body。首次 ground on「testmode 信号按连接 net 追踪电压域」。

## case 产物
- assets/A: spice_A.sp (CMLeftA/ChanEdgeL_A, 19 cm1: vdd2h=9 vintcore=8 parent_port=1 unknown=1) + prompt + task_brief
- hidden: spice_B.sp (CMLeftB, 23 cm1: vdd2h=13 vintcore=8 parent_port=1 unknown=1, 含 ag→vintcore trick port) + spice_B2.sp (CMLeftB2, 18 cm1: vdd2h=11 vintcore=6 unknown=1) + expected_B/B2.json + hidden_manifest
- reference: golden_solution.py + golden_A/B/B2.json + check.py (15 条件 a-o) + 4 negative{empty_shell, print_expected, no_parent_trace, port_name_classifier} + negative_selftest.py + reference_submit.zip
- 自验：ref 15/15 PASS ✓；negative 4/4 全 FAIL (NEG_RC=0) ✓；§4.9 三假 (empty_shell/print_expected/no_parent_trace) 全 FAIL ✓；3-run sha256 一致 ✓；test==disk check.py 12221B ✓
- 断言闸门：k_rationale=15=k_check(a-o)≥8 ✓
- domain: layout_aether · tier: L1（离线 SPICE 网表解析，无 EDA 工具实跑，忠实真实 agent 行为）
