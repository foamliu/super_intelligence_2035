# 深读：1793346704557_4j4es（jinsongl @ hfeg0pkn005）— ERC schMark net dump

## 元信息
- session: `1793346704557_4j4es`，user=jinsongl，host=hfeg0pkn005，mc=72
- 工具画像：235 dbGet + 65 netlist + 14 hspice + 4 schematic（lead agent, 212 msgs, 17 real user turns）
- 域：physical_verify（ERC = Electrical Rule Check，电压等级 / marker 一致性检查）
- **NEW user** jinsongl（ledger 中 0 prior case）

## 用户真实意图（U#6 idx=144，提出需求，未给根因/修复）
> 「帮我写一个单独的函数 功能是可以抓取出所有含有schMark属性的net，并且输出该节点的hierachy路径 schMark和voltMark」

U#7（idx 随后）跟进细化（可作 hint，不进 A 档 prompt）：
> 「对于schMark或者voltMark中含有多个marker的使用逗号分隔」

## grounding（agent 真实产物 dumpNetMark.tcl，从 trace editor edits 重建）
路径：`/home/jinsongl/ERC_AI/script/erc/ercScript/tclPackage/dumpNetMark.tcl`（独立新文件，仿 `dumpNetVolt.tcl`，不改原文件）

逻辑（TCL，CCK/udb 框架原语）：
- `dumpNetMark::dumpNetMarkProc {nodeHdl}`：`cckSearchNode` 的回调
  - `if {[udbCheckNodeProp $nodeHdl "schMark"] == 1}` → 节点带 schMark 属性才处理
  - `nodeName = [cckGetNodeFullName $nodeHdl]`（绝对层级路径）
  - `schMark = [join [udbGetNodeProp $nodeHdl "schMark"] ","]`（多 marker 逗号连接，U#7 细化）
  - `voltMark`：若 `udbCheckNodeProp "voltMark" == 1` → `join ... ","`，否则 `"-"`
  - `puts $fileHdl "$nodeName\t$schMark\t$voltMark"`（TAB 分隔三字段）
  - `return $::CCK_FALSE`（继续遍历，不中断）
- `dumpNetMark::dumpNetMark {outFile}`：`open outFile w` → `cckSearchNode -proc dumpNetMarkProc` → `flush` → `close`；stdout 打印 `Dumping all nets with schMark to $outFile`

输出格式：纯 TAB 分隔行 `hierarchy_path\tschMark\tvoltMark`，**仅含带 schMark 的节点**，**无表头/无尾注**，遍历顺序 = cckSearchNode 框架顺序。多 marker 逗号连接（`SVP,NVP`），单 marker 无逗号；无 voltMark → `-`。

涉及的 ERC 框架原语：`cckSearchNode`（遍历所有节点）、`cckGetNodeFullName`（层级路径）、`udbCheckNodeProp`（属性存在性）、`udbGetNodeProp`（取属性值=列表）、`$::CCK_FALSE`（回调继续遍历）。

## 为何 B 档重定义为离线生成器
真实 ERC 框架（CCK/udb TCL 包）+ 用户私有项目（`/home/jinsongl/ERC_AI/...`，DDR6 top 电路 + initRailParam_v1p4.tcl + markDict）对 e0031982 在 pyAether sandbox 不可访问（TCL 框架 + 私有 udb 数据库），无法取真实 net/mark 数据作 A 输入。
但 trace 的 grounding 价值在「规范提取」——把 `dumpNetMark` 的「遍历节点 → 过滤带 schMark → 输出 路径/schMark/voltMark（逗号连接多 marker，缺 voltMark 补 -）」抽象成可参数化的离线生成契约。

## B 档重定义
`dump_net_mark.py <net_mark.json> -o <out.list>`（stdlib only）：
- 解析 JSON `{design, generated, nodes:[{name, props:{schMark?:[...], voltMark?:[...], ...}}]}`
- 对每个 node：若 props 含 `schMark` 且非空列表 →
  - schMark = `",".join(props["schMark"])`
  - voltMark = `",".join(props["voltMark"])` 若 props 含 voltMark 且非空，否则 `"-"`
  - 输出 `name\tschMark\tvoltMark`
- 遍历顺序 = nodes 列表顺序（对应 cckSearchNode 顺序）
- stdout：`Dumping all nets with schMark to <outFile>`（+ 收尾 `Dumped N nets`）
- **无 schMark 的节点排除**（含：无 schMark key / schMark=[] / 仅有 voltMark）

## DISTINCT from 现有 physical_verify 系
- r250 HcellPairGen（LVS Hcell 配对）/ r251 LvsAmbiguityDiag（LVS 歧义诊断）/ r254 EmyCdlNetlistExtract（CDL netlist 提取）/ r255 CmMaOpTableGen（CM/MA op 表）/ r256 LdrSvrfRuleGen（LDR→SVRF 规则生成）/ r257 GloryRcFlowSetup（RC flow 编排）/ r258 ConnChkSummaryGen（DRC 连通性 sum.rep 报告）/ r259 DrcConnectGraphGen（DRC 连通图 HTML 渲染）
- 本 case：**ERC marker 一致性检查**域——遍历电路节点，按 schMark 属性过滤，输出 `层级路径\tschMark\tvoltMark` 标记报告（多 marker 逗号连接、缺 voltMark 补 -）。是「节点属性过滤 + 标记报告生成」，非 LVS 配对/歧义、非 DRC 规则/连通图、非 netlist/RC flow。

## case 结构
- assets/A：config_A.json（6 nodes，markers SVP/NOM/VHV+NVP 多 marker，含无 schMark/空 schMark/仅 voltMark 排除样例）+ prompt.txt + task_brief.md
- assets/hidden：config_B.json（8 nodes，深嵌套层级，marker vocab SUV/HOV/SVP/VHV+HOV，不同排除模式）+ config_B2.json（5 nodes，含 voltMark 多 marker、schMark 单/多混合）+ hidden_manifest.json
- reference：golden_solution.py + golden_A/B/B2.list + check.py（14 条件 a-n）+ 6 negative + negative_selftest.py + reference_submit.zip
