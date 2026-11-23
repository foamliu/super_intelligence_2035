# Deep-read: 1794830783269_mj3pw — jzeng PG via auto-generation

- **user/host**: jzeng @ hfeg0pkn002 (172.16.x, drcpaw group)
- **match_count**: 263; **domain**: pg_layout / physical_verify
- **session_file**: `/home/jzeng/.cline/data/sessions/1794830783269_mj3pw/1794830783269_mj3pw.messages.json` (717 KB, 185 msgs, 103 user / 82 assistant)
- **trace_source**: real cline trace, 2 user text turns + 101 tool_results

## Real task summary (user 原话)

> 参考 `/proj/drcpa/V0/agentdir/jzeng/IMCleAutoVia.py`，写一个脚本，在相同 power 的 M4 M5 之间生成 V4，M4 M5 宽度为 0.55um，长度较长，M4 M5 可能为 path pathseg rect 等，需要先在连到同一个 power 的 M4 M5 交叠处生成 2um x 2um 的 M4 M5，使其生成 V4 时没有 DRC。

第二句：「生成的 ell」(=cell，要求把生成结果落到 cell 里)。

## Agent 工具链

- read_files (22): 读参考脚本 `IMCleAutoVia.py`（分段读 777/1185/1245/1293/1370/1440/1500/1583 行）、`v4_gen.py`、`search_viadef_api.py`
- RAG_MCP_Server__search_apis (19) + get_api_details (2): 搜 `dbCrtVia` / `emyShapeGetNetName` / `techFindViaDefByName` / `emyPathGetWidth` / `emyPathSegGetWidth` / `dbGetTrueOverlapsEx` / `dbCrtRect` / `emyShapeAddToNet` / `dbAddFigToNet` / `dbFindNetByName` / `emyBoxF` / `dbGetInstTransform` / `techGetTechLib` 等
- editor (43): 反复写/改 `gen_v4_between_power_m4m5.py`（多次因 editor 行号错位 corrupt，最终用 python helper `_w.py` 一次生成）
- run_approved_command (13): py_compile 语法校验 + 试运行

## 最终脚本 `gen_v4_between_power_m4m5.py` 算法

| 步骤 | 操作 |
|------|------|
| 1. 收集 M4/M5 图形 | 遍历当前 layout 所有 `M4.drawing`/`M5.drawing`，bbox 最小维度 ≈ 0.55µm（容差 0.02）保留；支持 path/pathSeg/rect/polygon，含 top-level + hierarchy instance 内部图形（`dbGetMaster`+`dbGetInstTransform` 做坐标变换）|
| 2. 查找同 net 交叠 | 同一 power net（`emyShapeGetNetName` 取名）的 M4 与 M5 求 bbox 交集，取交集中心点 |
| 3. 去重 + 间距过滤 | 去除距离 < 0.001µm 的重复点；过滤间距 < 2.1µm 的候选点（避免 pad 互相交叠）|
| 4. 生成 2µm×2µm pad | 每个交点中心创建 2µm×2µm `M4.drawing`+`M5.drawing` 矩形，`dbFindNetByName`+`dbAddFigToNet` 连到原 net（保证 LVS 不断路）|
| 5. 放置 V4 via | `dbCrtVia` 参数化（1 行 1 列，enclosure -0.01，跟 IMCleAutoVia 一致），失败回落简单方式；via 名 `V4_V`（自动回落 V4_L_V/V4_m_V/V4_A_V/V4）|

## 关键参数

| 参数 | 值 |
|------|-----|
| TARGET_WIDTH | 0.55 µm |
| WIDTH_TOL | 0.02 µm |
| PAD_SIZE | 2.0 µm |
| MIN_PAD_GAP | 2.1 µm |
| via_name | V4_V (fallback chain) |

## 设计特点（agent 自述）

1. **形状无关性** — 用 `.bbox` 最小维度判宽度，不关心 objType
2. **层次化支持** — instance 内部图形经 transform 读出
3. **Net 保留** — pad 矩形 `dbAddFigToNet` 连原 net，保 LVS
4. **DRC 安全** — 2µm×2µm pad 对 V4 单 cut (~0.26µm) 有 ~0.87µm enclosure
5. **via 放置参数** — 与 IMCleAutoVia 一致的 -0.01 enclosure

## case 化抽象（design_flow）

- 把 layout 抽象成 JSON（shapes: rect/path/pathSeg/polygon，layer+net+几何），脚本读 layout.json 写 vias.json
- 纯 Python 实现（不依赖 pyAether），subprocess 跑 `python3 pg_via_gen.py <layout> <out>`
- check.py 独立 oracle 重算 overlap 中心 + dedup + min_gap，断言 ≥10 条
- A: 0.55µm/V4_V/2.0 pad/2.1 gap，rect+path+pathSeg
- B (hidden): 0.40µm/V5_V/1.8 pad/1.9 gap，加 polygon + hierarchical instance，坐标尺度不同
