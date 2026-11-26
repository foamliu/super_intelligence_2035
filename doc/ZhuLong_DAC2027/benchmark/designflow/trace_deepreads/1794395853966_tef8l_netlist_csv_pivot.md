# Deep-read: 1794395853966_tef8l (yinyus @ hfeg0plg66, mc894)

**Selected round**: r479 (shard A). **Domain**: digital (netlist text parsing + CSV pivot/transform, L1-B B档).
**scan source**: ssh_eda_search_20261113_131349. **keywords**: netlist:2255;schematic:2111;aether:1926;drc:1676;analog:417;pyaether:369;hspice:356;verilog:337.
**file**: 2,115,112 bytes / 534 msgs / 27 real user turns. **A-domain-primary** (first keyword netlist, dominant).

## User intent (real_task_summary)
批量抽取 `yinyus_nicap_block` 下所有 schematic 的网表，并对每个网表做一套多步 CSV 变换，最终汇总成 `nicap.csv`：
1. **抽取网表**（U#1）：批量 schematic → netlist（HSPICE/CDL），agent 用 aether/pyAether + batch_export_netlist.sh 完成（EDA 工具部分）。
2. **元素抽取+4列网格**（U#2/U#3/U#8）：读网表 `<**TopDesStart>` 后内容，把每个连贯元素（如 `<XI_AG_CXcap1S295x191_0<1>>`）按空格拆成独立 token，**每 4 个 token 一行**（4 列）写 CSV，文件名=网表名。
3. **列合并 `_2`**（U#4/U#9/U#10）：丢第 1 列，第 2 列+"-"+第 3 列 → 新第 1 列，第 4 列 → 新第 2 列（2 列），行数不变，后缀 `_2`。
4. **去重计数**（U#12）：(新第1列, 新第2列) 重复对合并，第 3 列写重复个数。
5. **透视 `_3`**（U#13/U#14/U#15）：第 1 列唯一值→行标题，第 2 列唯一值→列标题，交叉位填第 3 列数据（无则 0），左上角第一格=网表名，后缀 `_3`；后修正行列标题交换。
6. **汇总 `nicap.csv`**（U#16/U#17/U#18）：9 个网表的 `_3` 文件**按行拼接**（不改内容，行链接）成 `nicap.csv`。
7. **元素改写**（U#20）：`vss!-xx` → `xx-vss!`（以 `vss!` 开头的元素把 vss! 移到末尾）。
8. **列重排**（U#21/U#22）：按指定顺序 `ad2o!-vss!, vwln!-vss!, ...` 排列列标题（数据跟随列一起动），无对应元素的列跳过。
9. **拼接顺序**（U#23）：9 网表按指定顺序拼接。
10. **行过滤**（U#24）：删除第 1 列以 `AG_CXcap2S` 为前缀的所有数据行。

## Agent 实现（关键 tool_use）
- TU#1-91: 大量 RAG_MCP_Server__search_apis/get_api_details 查 aether netlist export API（dmExportNetlist / seExportNetlist / emy2netlist），读 aether 文档；list_allowed_files/read_files 探 yinyus_nicap_block 目录结构与已有仿真网表。
- TU#92-95: editor 写 `batch_export_netlist.sh`（HSPICE 批量抽取），被 agent-policy writableRoots 拦→改写 /ai_sandbox/ 路径。
- TU#96-109: run_approved_command 跑批量抽取，读产出的 netlist 文件（如 AG_CapYdecTopRTop_schematic.netlist）。
- TU#113-120+: editor 写 `parse_netlist_to_csv.py`（纯 Python stdlib）：找 `**TopDesStart` → split tokens → 4 列/行 → 列合并 → ... 多轮 editor 迭代修正（4列→2列合并→_2→_3 透视）。
- 后续: nicap.csv 汇总、vss! 改写、列重排、AG_CXcap2S 过滤等迭代。

## A-faithful 判定
**合格**。用户给：网表路径 + 输出目录 + 一步步变换规则（4列网格/列合并/去重/透视/拼接/改写/重排/过滤）。用户**未给**：token 拆分正则实现、`**TopDesStart` 定位算法、4-per-row chunking 实现、列合并 "-" 拼接实现、pivot 交叉填充算法、vss! 前后缀交换实现、列重排稳定排序实现。算法空间充分。

## Deliverable / .75 可行性
deliverable = 写私有 `/proj/drcpa/V0/simdir/hspice/yinyus/nicap_block/` + 读私有 `/proj/drcpa/` → **.75 SUT 沙盒 INFEASIBLE**（Permission denied）→ **B 档合成**。

## 合成计划（B 档）
**archetype**: `netlist-element-extract-multi-step-csv-pivot`（新，区别于 NetlistIncludeRewrite[include改写]/NetlistPadDriverTrace[信号追踪]/NetlistHierModuleExtract[模块提取]/StdcellFamilyRefMatch[名字匹配]）。
- SUT 交 `netlist_csv_transform.py`（纯 stdlib CLI）：输入 netlist 文件目录 + 输出目录，对每个 netlist 跑：①找 `**TopDesStart` 抽 token ②4-per-row 网格 ③列合并(drop c1, c2+"-"+c3→c1, c4→c2) ④去重计数 ⑤pivot(行=c1unique, 列=c2unique, 格=c3 or 0, 左上=netlist名) ⑥汇总拼接 ⑦vss! 前后缀交换 ⑧列重排(按指定order) ⑨AG_CXcap2S 前缀行过滤 → 输出 nicap.csv + 每网表 _3.csv + report.json。
- A (visible): 3 netlist 文件，token 模式 `<XI_..._0<1>>`，vss!/vcc! 元素，AG_CXcap2S 诱饵行。
- B (hidden): 4 netlist 文件，零名重叠，不同 token 模式/元素/列序/过滤前缀（如 AG_CXcap3S）。
- check.py ≥12 条件：a zip+py b stdlib c CLI exit0 d TopDesStart 定位 e 4-per-row 网格 f 列合并 g 去重计数 h pivot 结构 i 左上=netlist名 j vss!交换 k 列重排 l AG_CXcap2S过滤 m 汇总拼接行数 n 跨输入守卫 o 3-seed 稳定。
- 负样本 + §4.9 三假提交。

## DEBT 状态
**DEBT: 1 deepread 未合成**（r479）。本轮选料耗时（strict A-dominant 池 11x 枯竭 + 3 leftover REJECT + 3 top C-domain 跳过，方寻得 tef8l），余时间不足以完成 ≥8 条件 check.py + 自验 + 负样本 + 假提交回归。**下一轮第一件事 = 合成 tef8l case**（本笔记已含完整算法，可直接合成），修完才准开新 case。
