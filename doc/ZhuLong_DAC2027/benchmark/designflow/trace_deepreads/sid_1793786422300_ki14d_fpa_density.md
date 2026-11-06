# 深读笔记 — sid 1793786422300_ki14d (FPA density check, WOWTOP)

- **trace**: 1793786422300_ki14d.messages.json · aristaw @ hfeg0plg37 · mc=274 · 225 msgs · 1.18MB
- **domain**: layout_aether (pyAether 1171 / dbGet 455 / schematic 72)
- **用户原话逐字（A-档 seed, 纯需求, 未指根因）**:
  - U1 `check the FPA density of WOWTOP layout`
  - U2 (重复) `check the FPA density of WOWTOP layout`
  - U3 `检查layout中FPA`
  - U201 (聚焦) `检查当前cell WOWTOP_20260130_vap2 layout中 FPA/drawing层的密度。`
- **项目**: drgqa V0 (DBRChk), WOWTOP top-level layout 在 `/proj/drgqa/V0/libs/drgqa_top/WOWTOP/layout`；当前 cell `auto_pgnet/WOWTOP_20260130_vap2/layout`。
- **FPA 层定义** (layer.map): FPA/pin=557:251, FPA/drawing=557:0, FPA/blockage=557:230。
- **assistant 工具链**: list_allowed_files / run_approved_command(shell+python runner) / read_files / search_codebase / RAG_MCP_Server__search_apis → 找到 `dbArea` API；SandBox_MCP_Server__run_code (pyAether) 跑 `dbGetTrueOverlapsEx`；editor 写 `check_fpa_density.py`。
- **关键认知弯路（本题难度核心）**:
  1. 初版用 **bbox 面积** 算 polygon → 密度 **185%**（超过 cell 总面积，明显错）。
  2. 发现 FPA/drawing 是 **20 个 Polygon + 1 Rect**，polygon 的 bbox 严重高估实际面积（大覆盖区中间镂空）。
  3. FPA shapes 实际在 `FPA/pin` purpose（早期空），后定位 `FPA/drawing` 有 21 个。
  4. 修正：用 **`ae.dbArea(fig_objs)`** 计算 polygon **真实面积**（shoelace），而非 bbox。
- **真实产物（用户接受, msg 224）**:
  - Cell: `auto_pgnet/WOWTOP_20260130_vap2/layout`
  - Cell 面积: **70,730,429.53 sq.um**
  - FPA/drawing: **21 shapes** (20 Polygon + 1 Rect), 实际面积 **3,134,347.49 sq.um**
  - FPA/pin: 2 shapes, 0.01 sq.um
  - Total FPA: 23 shapes, 3,134,347.50 sq.um
  - **FPA density: 4.431399%**（bbox 算法曾得 185%，差 ~42×）
- **gold 脚本** `/home/aristaw/check_fpa_density.py` (pyAether):
  - `compute_fpa_density(cv)`: cell_area 优先 prBoundary.area，否则 bbox；遍历 14 个 FPA purposes；`dbGetTrueOverlapsEx(cv, cv.bbox, "FPA", purp, 0, 0)` 取 figs；`fig_objs=[fd.object]`；`ae.dbArea(fig_objs)` 算真实面积（fallback bbox）；density=total/cell_area*100。
  - 返回 dict: cell, cell_area, fpa_area, fpa_density_pct, fpa_shape_count, fpa_by_purpose{purp:{count,area}}。
  - `print_report(result)`: 文本报告。
- **L2 阻塞**: live pyAether + WOWTOP OA cell 在 .75 沙盒不可复现 → **L1-boundary**：把 layout 抽象成 JSON（cell bbox / prBoundary / FPA shapes{type=polygon|rect, points|bbox, purpose}），候选用纯 stdlib 算真实面积（polygon shoelace, rect 宽×高），产密度报告。**关键判分点：polygon 必须用 shoelace 真实面积，bbox-stub 必 FAIL**（复刻 185% vs 4.43% 的认知坑）。
- **A (可见)** = WOWTOP-like layout_A.json（~21 FPA/drawing shapes, 大 polygon 中间镂空, cell bbox 大）；**隐藏 B** = 不同 cell（C-frame + L-shape + triangle + rect, prBoundary 优先, density ~9.54%, bbox-stub 会得 ~29.23%）；**B2** = 极简（少量 rect, 无 polygon, 验 rect-only 路径）。
- **断言 k=14 a–n**（与 check.py 一一对应）。
