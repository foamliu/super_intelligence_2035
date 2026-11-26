# r264 deep-read — 1793363087693_d0ild (xiwang@hfeg0pkn005, mc=520)

- session: 1793363087693_d0ild.messages.json (10.129.2.14, nested path), 441 msgs, agent=lead, model=deepseek-v4-flash, 12 real user turns.
- keywords: 472 schematic, 201 pyAether, 163 dbGet, 38 netlist, 10 cellview (+ 1 calibre). OA/Aether db exploration of DDGOA V0 design.
- tool counts: editor(73), run_approved_command(74), SandBox_MCP_Server__run_code(36 pyAether), read_files(15), list_allowed_files(8).

## User intent evolution (real turns)
- U1 (提出需求, 未给根因): DDGOA V0 中, SCmosDataDPCtrlNew_DDGOA_add 与 SCmosConTopVdd2h 是常见 SCMOS 电路, 按类似结构找出 DDGOA V0 中所有 SCMOS 电路, 列出路径 hierarchy。
- U2: 结果存文件, 格式 item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty (给举例)。
- U3: 要精确的 instName 而非 cellName。
- U4: hierPath 是从 Top 到该 instance 的完整 hierarchy 路径 (例 XI_C_Top.XI_Channel.XI_ChanMid.XI674)。
- U5: 给正确范例 0,/XI_C_Top.XI_Channel.XI_ChanMid.XI674,inst,XI674,ddgoa_cmos_digital,SCmosConTopVdd2h,schematic,cellName,4phas_SCmos,FindinstByCellName。
- U6: 问 hierarchy 最前缀 xinwei_twck2dqi 含义。
- U7: 从 ddgoa_top 的 WOWTOP 范围往下查, 顶层应为 I_C_Top。
- U8: 每层必须是实例名 (I_C_Top.I_Channel.I_ChanMid.I185.I_ScmosEnBufNewP200 正确; 不是 I_C_Top.I_Channel.I_ChanMid.Idd_RingOsc_All2.I_ScmosEnBufNewP200)。
- U9 (3 修复): (1) 不需要 LP5TOP 这一层; (2) 每层实例名前加 X; (3) 文件加标题行。
- U10 (根因举例): XI_C_Top.XI_Channel.XI_ChanRight.XI_DPHalfHi.XI_SCmosDataDPHalfAll.XI_ScmosEnBufNewP4000_7 实际是 XI17<0> 和 XI17<1> (总线按位展开)。
- U11: 第 513/520 个也是同样问题, 全部检查更新。
- U12 (提出需求): 把找电路+格式化文件功能形成 skill, 名字 FindCir4CrossProbe_wx。

## Grounding (agent 真实产物)
- scan_parents.py (pyAether 沙箱): 读父 cell 任务列表 (lib|cell), 逐个 dbOpenCVByType(lib,cell,"schematic") + emyGetAllInstHeaders(cv, EMY_GET_INST_HEADER_TYPE_ALL, holder, emyString("x")), 取 h.cellName + it.name, 输出 fullmap.json {lib|parent: {childCell: [instNames]}}, 分块 ≤~200/调用 (NFS 慢/30s 超时)。
- build_records.py (本地 stdlib): 读 fullmap.json → pm[parent]={child:[instNames]} (dedup) → lib_of[cell]=lib + seeds(名字匹配 scmos) 从 scmos_master.txt(lib/cell 行) → BFS 从 chip-root(LP5TOP): prev[child]=parent, instOf[child]=names[0], ROOT 排除出 chain → 对每 parent 的 seed child, 逐 raw inst 名: numbered_only 过滤(LEAF_RE ^I\d+(<(\d+):(\d+)>)?$, 丢 CDF I_ 与 buf) + bus_expand(I17<1:0>→I17<0>,I17<1>, a>=b 从 b 到 a 否则从 a 到 b) → hierPath="/X"+top_instance+"."+".".join(["X"+x for chain]+["X"+leaf]) → row(item, hierPath, inst, X+leaf, lib, cell, schematic, cellName, cell, FindinstByCellName) → sort by hierPath → re-index item → 写 CSV with header。
- 关键坑: aeOpenDesign 只返回 bool (用 dbOpenCVByType 取句柄); emyGetAllInstHeaders holder 类型; CDF 自动名 vs 编号式名 (numbered_only 过滤); 总线未展开 (bus_expand); 实例名挂错父 (按 pm[parent][child] 关联, 禁跨父); cell 名充当实例名 (取不到就丢路径); LP5TOP 层丢弃 + I_C_Top 硬编码为顶层标签; 默认 python 损坏 (用 python3.11)。
- 最终: 705 行, 69 distinct SCMOS cells, sha256 一致; skill 化 FindCir4CrossProbe_wx (SKILL.md + scan_parents.py + build_records.py)。

## B 档重定义
真实 OA 库 /proj/ddgoa/V0 (NFS, e0031982 不可访问) 不可达, 但 build_records 组装步骤是纯 stdlib。故重定义为离线 stdlib build_records.py: 读 fullmap.json + scmos_master.txt + 参数, BFS 拼路径, 产 cross-probe CSV。合成小规模 fullmap 作 A/B/B2。
- DISTINCT from 现有 layout_aether 系: r222 SchOaInventoryExtract(OA 库 inventory 统计) / r238 LayoutFloorplanGen(floorplan) / r252 LayStructExtract(layout 结构) / r254 EmyCdlNetlistExtract(CDL body) / r253 PinListPortOrderExtract(pin 顺序) / r263 CmTestmodeDomainCount(flat SPICE testmode 计数) — 本案首次 ground on "OA 实例图 → 按电路族名找种子 → 从顶层 BFS 拼真实实例名 hierarchy cross-probe CSV (numbered_only 过滤 CDF/buf + 总线按位展开 + X 前缀 + 丢层 + 排序)"。

## Case
EDA-Eval-DesignFlow-ScmosCrossProbeCsvGen-001 (layout_aether, B-synthesized, L1, k=16 a-p)。assets/A(fullmap_A.json 11 行层级 + scmos_master_A.txt 6 cell + prompt + task_brief) + hidden(fullmap_B.json 16 行层级含 2-bit bus + SCmosOnlyCdf 仅 CDF→0 行 + expected golden_B + manifest) + reference(golden_solution.py + golden_A/B.csv + check.py 16 条 + 5 negative{empty_shell,print_expected,no_bus_expand,keep_cdf,core_deleted} + negative_selftest + reference_submit.zip)。自验: golden 16/16 PASS ✓; negative 5/5 全 FAIL ✓; §4.9 三假(empty_shell/print_expected/core_deleted)全 FAIL ✓; 3-run sha256 一致 ✓; test==disk ✓。
