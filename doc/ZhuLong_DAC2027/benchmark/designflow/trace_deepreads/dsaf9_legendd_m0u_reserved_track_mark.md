# Deepread: dsaf9 — legendd M0U 预留 track 标识 (text:drawing1 path)

- **session**: 1795422908984_dsaf9.messages.json (513 msgs, 2.1MB)
- **user/host**: legendd @ hfeg0pkn002 (10.129.2.11)
- **match_count**: 628 (pyaether:1501; schematic:458; dbopencv:322; drc:317; aether:193; rtl:154; cellview:91; dbget:68)
- **domain**: layout_aether
- **cwd**: legendd Aether layout (inverter cells drcoa_stdcells/invY*, invLV*, drcoa_work/invDS*)

## 本轮选取的子任务 (MSG 1-17)

**用户意图**：输入/输出走纵向 M0U 未走满，剩余区域=预留 track；用 text:drawing1 画 path 标识。规则：中心线对齐 M0U 走线中心、上下端对齐两条 metal track 边、宽 marker_width。

**用户示例 (MSG 1)**：在 x≈2.57 (Y drain M0U) 画了一条 text:drawing1 path 作示例：
- emyPathSeg, bbox x(2.3975 2.7425) y(0.7225 5.9875), w=0.345, cx=2.570
- M0U 条 x2.434..2.706 (宽0.272), y0.836..4.616

**agent 做法 (MSG 6)**：
1. 读 cur.shapes 里 layer==text & purpose==drawing1 的现有 cx → {2.57}
2. Y drain M0U 中心 = [1.05, 2.57, 4.09, 5.61, 7.13, 8.65, 10.17, 11.69] (8 条，间距 1.52)
3. 对每条非 existing 的 cx：`pyAether.dbCrtPath(cv=cur, layer=emyString("text"), points=[(cx,0.7225),(cx,5.9875)], width=0.345, purpose=emyString("drawing1"), style=emyString("truncate"))`
4. save() → 新增 7 条 (扣示例 2.57)

**MSG 9-14**：继续补 A 输入 stub (x0.29, x0.116..0.464 宽0.348, y1.892..3.560) → 同规则 text:drawing1 path (cx=0.29, y0.7225..5.9875, w0.345)。最终 9 条 text:drawing1 centers = [0.29, 1.05, 2.57, 4.09, 5.61, 7.13, 8.65, 10.17, 11.69]。

**MSG 15-17**：「输入的也许要」「做的不错」→ 确认 A 已画，固化进方法论「走线层次与方向规则 / 预留 track 标识 (text:drawing1)」。

## 后续 (MSG 19+) 不纳入本题

整 session 还包括：invLVx12/invLVx32/invLVx24/invYx2_xdec/invDSx* 完整 layout 流程 (布局/连线/打pin/via)、M0U-MT2 通孔、MT2 拉伸、PCU 孔超出 MT2 范围 DRC、MT2/M0U 换 path 不用 rect、pin label centercenter justification、(0.25,6.27) 多余 M0U 删除、(9.3,3.42)/(9.3,2.02) MT2 包边缩回减 PRC、方法论固化等。这些是多 cell 迭代，超出单 case 范围；本题只取 MSG 1-17 的 text:drawing1 预留 track 标识子任务（自包含、有明确几何与规则、可离线复刻）。

## 离线合成

真实 Aether session 不可达，故离线 Python 版本：
- **公开 config_a**：trace 真实几何 (9 条 M0U + track_y 0.7225~5.9875 + width 0.345 + existing{2.57})，预期 8 条新 marker。
- **隐藏 config_b**：invLVx32 风格 (13 条 M0U + track_y 1.05~7.38 + width 0.40 + existing{3.55})，预期 12 条 — 主判分。
- **隐藏 config_c**：invDSx4 风格 (4 条 Y drain, 无 A, track_y 0.50~4.50, width 0.30, 无 existing)，预期 4 条 — cross-input anti-hardcode guard。
- **交付**：mark_tracks.py 读 config 输出 markers.json。
- **判分**：15 条独立断言 (结构/数量/坐标/去重/跳过 existing/覆盖/跨输入泛化/确定性)。
- **negatives**：empty(cond3) / print_only(cond3) / hardcode_a(cond5) / delete_core(cond5) 全 FAIL distinct。

## 与既有 C 域 case 区别 (防 intent-dup)

- 与 ParaInverterArrayPlace-001 (layout_virtuoso, Virtuoso SKILL 参数化反相器阵列 place+verify) 区别：本题为 Aether text:drawing1 标识层 path 生成 (非 place/verify，非几何阵列)，产物是 marker 列表 (cx/y_bot/y_top/width) 非 placement rects，trace 不同 (dsaf9 vs amn6z)，domain 不同 (layout_aether vs layout_virtuoso)。
- 与 SkillPatternDecoordinate / GdsRectGen 等几何脚本 case 区别：本题是"标识层 path 规则化批量生成 + skip-existing 去重"，核心是规则匹配与跳过逻辑，非坐标变换/批量 rect 生成。
