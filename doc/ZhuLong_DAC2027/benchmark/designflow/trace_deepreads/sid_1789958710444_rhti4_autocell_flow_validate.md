# 深读笔记 — sid_1789958710444_rhti4 (miccao / hfeg0plg92, mc=163)

- **trace**: `/home/miccao/.cline/data/sessions/1789958710444_rhti4/` (1.07MB, 177 msgs, 102 user turns)。tools 列：1021 calibre / 144 netlist / 92 schematic / 7 cellview / 6 hspice / 3 pyAether / 2 virtuoso（calibre 主导 + AutoCell 标准单元布局生成）。
- **skill 调用**：`autocell-tcl-flow-generator`（cline 自定义 skill，MSG1）。
- **UI#0 逐字原文（A-档 seed 候选）**：长篇 AutoCell TCL Flow Generator 规范（8 文件 flow：run/layers/layer_functions/viades/globals/rules/place/route.tcl；new-flow 硬约束 8 条 + 引用/命名约束 + 参数溯源 + validate_flow.py）+ 末尾真实请求：「`/home/miccao/autocell/ddcpc/netlist/.../blcnand2PF47x1.cdl` 这是网表路径，依据 `.../cell_constraints_template.txt` 里面的设置，生成 gds，放到 `.../black/gds_drc` 下面，`.../autocell` 这是 autocell 的安装包。请迭代 DRC，同时 autocell 需要打印 log 给每一个 cell。」= **提出需求 + 目标（生成 GDS + 迭代 DRC + 每 cell log），未给根因/修复 → A-档 seed 合规 ✓**。
- **后续用户轮**：UI#27「继续」；UI#124「检查当前环境的 calibre 是否可以正常调用」；UI#133「hello」。均非新需求，无 A-档 seed 价值。
- **agent 行为**：43 次 editor（多写 inspect_drc*.sh 检查脚本 + 改 flow TCL）、23 次 run_approved_command（真跑 autocell + calibre DRC）、19 次 read_files、10 次 list_allowed_files。在 `/home/miccao/autocell.1.2026.7/g5_ddcpc/` 现有 flow 上修改 run.tcl 等，迭代 calibre DRC。
- **结尾状态**：MSG175「严重情况：`/home/miccao/autocell/black/` 被整体清空——8 文件 flow、flat CDL、上次的 GDS 全部消失。需要重建。」→ trace 未达成干净可接受的 gold，环境被外部清空。
- **A-档 disqualified 判定**：gold = agent 修改并真跑 AutoCell flow + calibre DRC 迭代，依赖私有 autocell 安装（`/home/miccao/autocell/software/data/autocell`）+ calibre 2020.1 + 私有 PDK + `g5_ddcpc` flow + blcnand2PF47x1 网表，e0031982 无权访问、沙盒不可复现 → **A-档 disqualified → B-档 synthesized L1-boundary**。
- **合成锚点**：UI#0 规范本身定义了 `scripts/validate_flow.py <flow_directory>` 静态校验器（检查 8 文件齐全 / source 顺序 / tech 创建位置 / via 分离 / placement 模式 / GDS 输出路径 / router 契约 / grid_map / 层先声明后引用 / via 引用解析 / 无 TODO）。合成离线 Python 校验器：解析 8-TCL-file inventory 文本 → 按 new-flow 硬约束 + 引用/命名约束审计 → 输出结构化 JSON 报告。**与既有 case 区别**：MVVarNamingAudit/DeckIncludeResolve=calibre SVRF deck 审计；PFMergeAudit=layout figure merge；RNodeCovAudit=RsCalc 探针覆盖；本案=**AutoCell TCL flow 8-文件依赖 + new-flow 硬约束结构校验**，主题/断言独立。
- **domain**：layout_virtuoso（AutoCell = TCL 驱动标准单元布局生成 flow；TCL flow + cell layout）。coverage 11→12。
