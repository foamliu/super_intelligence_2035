# rr6qb deepread — shushengz 统计 DoutFIFOTopM6 schematic 管子类型/数量/尺寸

- **session**: 1795411956334_rr6qb.messages.json
- **user/host**: shushengz @ hfeg0plg93 (also plg78/06/05, pkn004)
- **mc**: 306 (schematic:1107; cellview:780; analog:390; cmos:339; dbget:92; virtuoso:71)
- **nmsgs**: 318, file 975KB
- **domain**: schematic_netlist (D)
- **date**: 2026-11-23

## 用户真实意图
"统计一下这个 /proj/dejoa/V0/libs/dejoa_digital/DoutFIFOTopM6/schematic block 内使用 ntn_m/ptn_m 和 ntk/ptk 管子类型 和数量和尺寸"

即：对 DoutFIFOTopM6 这一个 schematic block，遍历所有 instance，按 MOS master cell 名（ntn_m / ptn_m / ntk / ptk）分类，统计**每类数量**与**W/L 尺寸**，输出统计表 + FINAL COUNTS 汇总。

## agent 工具链
1. `list_allowed_files` 探目录 → 看到 DoutFIFOTopM6 有 schematic view (OA)
2. `RAG_MCP_Server__search_apis`/`get_api_details` 大量检索 SKILL API（dbOpenCellViewByType / cv~>instances / inst~>master~>cellName / vfoGetParam w l / dbInstQuery …）
3. `editor` 写 SKILL 脚本 `analyze_block_v2.il`：procedure `analyzeDevices(lib cell view)` → dbOpenCellViewByType → 递归 `_traversePath` 遍历 hierarchy → 按 master cellName 匹配 ntn_m/ptn_m/ntk/ptk → 打印 `hier_path  type  W=..  L=..` 表 + FINAL COUNTS（ntn_m/ptn_m/ntk/ptk 计数 + TOTAL）
4. 修 bug：初始调用参数顺序错（`_traversePath(topCv lib cell 0)` → `_traversePath(topCv 0 sprintf(nil "%s/%s" lib cell))`）
5. 尝试 `SandBox_MCP_Server__run_code` (skill + pyAether) 自跑 → **两个沙箱都 Connection refused** (172.16.8.13:45892 / 172.16.8.190:26205)
6. 转而请用户在 Virtuoso CIW 手动 `load("analyze_block_v2.il"); analyzeDevices("dejoa_top" "LP6TOP" "schematic")`
7. 用户回 "自己运行" → 沙箱仍 down → agent 给出预期输出格式（含示例 `ntn_m: 6 ... TOTAL: 6`）

## 交付物
SKILL 脚本 `analyze_block_v2.il`（hierarchy 遍历 + 类型分类 + W/L 抽取 + 统计表 + FINAL COUNTS）。**但真实统计结果从未产出**（沙箱整轮 down，用户也未贴回 CIW 输出）。

## 可判分内核
"解析 schematic instance dump（层次路径 + master cell + W/L）→ 按 ntn_m/ptn_m/ntk/ptk 分类计数 + 列 W/L" — 离线可判分（L1 Python 解析 dump 文本）。

## 为何 parked（not weak，not 造题）
- **真实意图 = produce**（非 Q&A）：用户明确要统计真实 schematic 的管子，agent 写了完整 SKILL 脚本。非 weak。
- **但真实输入数据不可得**：
  - 真实 schematic = OA cellview (`/proj/dejoa/V0/libs/dejoa_digital/DoutFIFOTopM6/schematic`)，离线不可解析；trace 内沙箱 down，agent 从未跑出真实 instance dump。
  - eda_flow virtuoso sandbox 是另一套环境，不含 /proj/dejoa 库路径，无法重跑 SKILL 取真实数据。
  - 合成 A（假 instance dump）违反 §1 红线"真实输入文件"+ 任务初衷"真实性=唯一来源"。
- **L2 真跑** 需 Virtuoso sandbox 含真实 DoutFIFOTopM6 cellview — 不可行。
- 结论：真实 produce 意图但真实输入数据不可提取 → **parked**，非 weak 排除。若未来能访问 /proj/dejoa OA 库导出真实 instance dump，可复用此 trace 造 L1 case。

## 复现
```bash
# .75 上 ssh 到 hfeg0plg93 取 session
ssh -o BatchMode=yes -o ConnectTimeout=8 hfeg0plg93 'python3 -c "import json;d=json.load(open(\"/home/shushengz/.cline/data/sessions/1795411956334_rr6qb/1795411956334_rr6qb.messages.json\"));print(len(d[\"messages\"]))"'
```
