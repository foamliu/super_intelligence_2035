# Deep-read — r238 / 0j59o / pyAether 版图规划脚本生成

- **shard**: C (physical_layout / layout_aether)
- **session**: `1785899794656_0j59o.messages.json`
- **user / host**: michael1l (NEW user, not in saturation list) / hfeg0pkn003 (10.129.2.12)
- **match_count**: 143 (aether:88·layout:42·pdk:38·cellview:31·pyaether:28·dbCrtInst:12·aeOpenDesign:9)
- **agent**: lead, 71 msgs
- **case_id**: `EDA-Eval-DesignFlow-LayoutFloorplanGen-001` (L1, B-synthesized, 18 条断言)

## 用户真实意图

michael1l 单轮需求 U#0「启动场景，版图规划」。项目根目录 `/proj/lacaa/TV1_FS_Virtuoso/workdir/michael1l`，库 `FS_H204_LIB`（35HFS / 35H DBCFS 工艺），已有 cell INV/INV_v1/inv_test（均有 layout view）、TEST/temp_michael.gds。用户要一个**pyAether 版图规划脚本**：初始化 Aether → 新建/打开 cellview → 画边界 → 放置 instance → 显示环境，覆盖"新建规划"和"打开已有"两条入口。

## assistant 工具链

assistant 71 步：路由 eda_agent skill → 读 pyAether 文档/API → 用 `editor` 通过增量 `cat >> heredoc` 写出 `layout_planning.py`（8 函数 + main）。无用户附件，cellview 未在 trace 中实际打开（脚本生成任务，非实跑）→ B 档 synthesized。

## 8 函数 + pyAether API（trace-grounded）

| 函数 | pyAether API | 关键签名/陷阱 |
|---|---|---|
| `init_aether(mode="-adv")` | `emyInitAether(flag)` | 必须带 `"-adv"` 高级模式标志 |
| `new_layout(lib, cell)` | `aeCreateDesign`/`aeOpenDesign` | 新建 cellview |
| `open_cellview(lib, cell, view, mode)` | `aeOpenDesign(lib, cell, view, mode)` | 4 参数顺序：lib, cell, view, mode（mode="new"/"edit"） |
| `create_boundary(l, b, r, t)` | `emyBoxF(l,b,r,t)` + `aeCreateRect(box, layer, purpose)` | 先 emyBoxF 构造 box，再 aeCreateRect 落层 |
| `place_inst(lib, cell, x, y, inst_name, orient, view)` | `aeGetCurDesign()` + `emyPointF(x,y)` + `dbCrtInst(cv=, point=, lib=, cell=, view=, inst=, orient=)` | 必须先取当前 cv，emyPointF 造点，dbCrtInst 用关键字参数 |
| `start_plan_new(lib, cell, w, h)` | 编排 init + new + boundary | "新建规划"入口 |
| `open_existing_cellview(lib, cell)` | 编排 init + open(edit) | "打开已有"入口（edit 模式） |
| `show_env()` | `aeGetCurDesign()` + print | 显示当前 cellview |
| `main()` | 调 start_plan_new + place_inst + show_env | 主入口 |

## 合成资产设计

真实 trace 只有一份硬编码 FS_H204_LIB/CHIP_TOP 的 `layout_planning.py`（lib/cell/dims/inst 全写死）。为机器校验 + 杀硬编码，抽象为**manifest 驱动生成器**：`python3 layout_planning.py <manifest.json> -o <out_script.py>`，读 manifest{lib, cell, view, mode, init_flag, boundary, boundary_layer, instances[]}，生成含 8 函数 + main 的 pyAether 脚本。

- **A** (manifest_A.json, trace-grounded): FS_H204_LIB / CHIP_TOP / layout / new / boundary 1000×800 / 2× INV (R0)
- **B** (manifest_B.json, 隐藏, 反硬编码): MEM_LIB / MEM_TOP / 2000×1500 / 3× NAND2/NOR2/BUF (R90/R180/MY) — lib/cell/dims/insts 全不同
- **B2** (manifest_B2.json, 隐藏, edit 模式): IO_LIB / IO_PAD / mode="edit" — 验 open_existing_cellview 路径
- **B3** (manifest_B3.json, 隐藏, 不同 orient): RF_LIB / RF_AMP / CAP orient=MX — 验 orient 反映

## 交付接口

SUT 交付 `submit.zip`（含 `layout_planning.py` 生成器，stdlib only）。check.py 解压 → 在 A/B/B2/B3 四份 manifest 上跑生成器 → 解析输出脚本验证 8 函数 + 7 个 pyAether API 名 + manifest 驱动（边界坐标/inst 坐标/orient 从 manifest 读非硬编码）+ 缺失路径报错退出 + 3-seed 确定性，18 条独立断言。

## 自验

- golden.py 通过 check.py --self：18 条全 PASS
- 5 个 negative 全 FAIL
- §4.9 三假全 FAIL
- 断言闸门：test_rationale 以"18 条断言：①"开头，①..⑲ 共 18 个圆圈 == k_check=18 ≥ 8
