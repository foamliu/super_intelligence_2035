# Deepread: 1794902730841_w7iht — GT NOT MGC resistance endpoint extraction

- **session**: 1794902730841_w7iht.messages.json
- **user/host**: eric9zhu @ hfeg0plg54 (10.129.32.75)
- **mc**: 188; keywords: virtuoso:257;skipper:235;cellview:232;techfile:118;drc:44;aether:43;dbcreatepolygon:25
- **domain**: layout_virtuoso (C-shard)
- **NMSG**: 271

## User intent (msg 0 and 96 — refined)
- 工艺库: `/apps/imctf/cad/techlib/als/lacaa/0.2.9/fs_vir/35HFS`
- 布局: `/proj/lacaa/TV1_FS_Virtuoso/workdir/eric9zhu/ownlib_deck_evaluation/test/layout`
- 需求:
  1. 取得 **没有和 AA overlap 的 GT** (poly 不与 active 重叠的部分)
  2. 用这个 GT NOT MGC → 得到 GT_CHECK
  3. 获取 GT_CHECK **首尾中心点坐标** (为后续 skipper P2P 电阻量测使用)

## 关键技术发现
- 35HFS techfile.tf 中层定义:
  - GT (poly): line 665, list("GT" "drawing")
  - AA (active/OD): line 627, layer 1104, list("AA" "drawing")
  - MGC (Metal Gate Contact): line 831, layer 1153, list("MGC" "drawing")
- 已有脚本 `checkGtJumper.il` 提供了 GT-overlap-AA 检测的范本 (用 dbGetOverlaps)
- skipper = GDS 编辑器，从终端启动，有 P2P (point-to-point) 电阻量测功能

## Agent 工作流
1. list_allowed_files / read_files: 探索目录、读 layermap、techfile.tf
2. search_codebase / RAG search_apis: 找 SKILL API (leLayerAndNot, dbGetOverlaps, dbCopyFig, dbDeleteObject, shape~>points)
3. ask_question: 询问 skipper P2P 用法
4. run_approved_command: 用 python-runner 多次生成/重写 SKILL 脚本
5. editor / insert_line: 尝试直接编辑文件 (多次失败/重试)
6. 最终交付: `/home/eric9zhu/checkGtResistance.il` + README + Python 生成器 `gen_gt_check.py`/`write_gt_check_resistance.py`

## 关键 SKILL API / 算法
- `leLayerAndNot(cv lpp_src lpp_sub lpp_dst)` — 几何 NOT 操作
- `dbGetOverlaps(cv bbox lpp ...)` — 检测 GT 与 AA 的 overlap
- 路径端点: `pts=shape~>points; car(pts)` (首点), `last(pts)` (尾点)
- 矩形端点: 用 bBox 角点取中心
- 临时层清理: `dbDeleteObject(sh)` 遍历
- 输出: `outfile`/`fprintf`/`close` 写入坐标文件

## 案例 case 化方向
- **case_id**: EDA-Eval-DesignFlow-GtCheckResistanceSkill-001
- **交付**: Python 生成器 `gt_check_skillgen.py`，输入 layermap.tf + test_layout.json，输出 SKILL 脚本 checkGtResistance.il 并模拟算法得到 GT_CHECK 端点坐标
- **A/B 变体**: 不同 layer number 的 layermap (B 隐藏)
- **≥10 断言**: layer 解析正确、leLayerAndNot 使用、dbGetOverlaps 使用、端点 car/last 提取、bBox center、临时层清理、fprintf 输出、SKILL 语法平衡、算法模拟正确、参数化
