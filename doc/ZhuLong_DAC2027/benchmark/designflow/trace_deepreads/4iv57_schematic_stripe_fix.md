# 4iv57 — DRC pattern tool schematic 示意图修复（stripe_deg + 4 fix batch）

## trace_source
- session_file: `1795745321483_4iv57.messages.json`
- user: xxchen · host: hfeg0plg56 · match_count: 1229
- keywords: drc:4860; schematic:990; rtl:73; pdk:35; calibre:19; .gds:17; .def:2; lvs:1
- domain: physical_verify (DRC pattern tool / QA schematic)
- msgs: 1036 total / 544 user turns（>600 ⇒ 本轮 deepread + DEBT，下轮合成）
- ledger: claimed r1472 (covered 567→568)

## 真实用户意图（原话，USER 3）
> ### 优化QA pattern GUI: 选择function页面
> 以下是我找出的问题，逐一进行修复：
> 1）ORTHOGONAL_45DEGREE：只绘制一个错误的pattern 非45°斜边即可，红线高亮这个图形边框。
> 2）DUMBBEL_SHAPE：红线应该被分成两部分…
> 3）SPACE_UPON_WIDTH：为什么上面length 字符，删除该字符，然后调整图形比例适应工作框。
> 4）LINE_END_SPACE：两个图形的 lineEnd 需要正对对齐。
> 5）SPACE_DIFFERENT_DIRECTION: 蓝色图形长短边反了…缩小蓝色图形为竖直方向的长方形…
> 6）VIA_AROUND_VIA_SPACE：黄色图形代表VIA，大小需要一致…
> 7）MUST_COVER: 蓝色条纹透明图形应该再黄色图形上方…
> 8）NO_OVERLAP：蓝色图形应该用条纹+透明的配置…

用户随后收敛到 4 条核心修复（agent 最终报告「4 点全部修复」）：SPACE_DIFFERENT_DIRECTION / SPACE_UPON_WIDTH / MUST_COVER / NO_OVERLAP。

## agent 真实产物（最终报告 + grep 实证）
工作目录 `/home/xxchen/workspace/DRC_pattern_tool/0.7/drcpv_develop/drcpv/gui/schematic/`，纯 Python（无 Qt 依赖，renderer 在归一化 0–100 坐标空间画 primitive dict）。

### Fix 1 — SPACE_DIFFERENT_DIRECTION（_common/space.py）
- 规则语义「长边不得正对短边」，via 短边 = 竖直边（宽 0.08）
- 蓝色中心保持横放长条（长边 60 水平）；4 个黄邻居统一为**竖条 8×15**（短边=宽 8），尺寸完全一致
- 上方邻居短边正对中心长边（红箭头 50,33→50,38）；左右同尺寸旋转放置；下方长-长不计

### Fix 2 — SPACE_UPON_WIDTH（_common/space.py）
- `width` 标签原在 (80,2) 高悬；挪到 bar 右端(94) 与黄箭头(91) 通道里、与箭头垂直居中 → `TEXT(66, 28)`
- 判据：放进 (92) 会越出卡片（92+6.4 > 94，inside=False）

### Fix 3 — MUST_COVER（_common/check.py）
- 高亮框原 x62..88（宽 26）压到蓝右边界 62 ⇒ 读作「蓝盖住红框」
- 修后：高亮 = 露出部分本身 x62..75（宽 13）；高亮**画在蓝之后**（最上层）；移除粉色 wash，保留 layer2 橙填充 + 深红外框

### Fix 4 — NO_OVERLAP + renderer 增强（_common/check.py + _prims.py + renderer.py）
- layer2 `stripe_deg=45`（"/"），layer1 `stripe_deg=135`（"\"）→ overlap 一目了然
- **renderer 原先不支持第二种 stripe 角度** ⇒ 新增 `stripe_deg` 参数，同步到 rect/poly/ring **三个** stripe 函数
- SVG 预览的 pattern 键从 `layer` 改为 `(layer, deg)`

### stripe_deg 实证（grep _prims.py / renderer.py）
```
_prims.py:52  def RECT(x, y, w, h, layer, alpha=None, stripe=None, stripe_deg=45):
_prims.py:67      if float(stripe_deg) != 45.0: p["stripe_deg"] = float(stripe_deg)
_prims.py:72  def POLY(pts, layer, alpha=None, stripe=None, stripe_deg=45):
_prims.py:82      if float(stripe_deg) != 45.0: p["stripe_deg"] = float(stripe_deg)
_prims.py:87  def RING(x, y, w, h, band, layer, alpha=None, stripe=None, stripe_deg=45):
_prims.py:99      if float(stripe_deg) != 45.0: p["stripe_deg"] = float(stripe_deg)
renderer.py:356  p.get("stripe_deg", 45)   # rect stripe path
renderer.py:416  p.get("stripe_deg", 45)   # poly stripe path
renderer.py:472  p.get("stripe_deg", 45)   # ring stripe path
```

### 真实验证（agent 跑通的脚本，全部 PASS）
- `_verify_browse_logic.py` → 1478 PASS
- `_verify_svg_stripes.py`（第二条渲染路径）→ 12 PASS
- `_check_stripe_pixels.py`（PNG 像素级）→ 9 PASS（"/"=29、"\"=27 条 hatch；must_cover 本体蓝 1492/橙 0、露出条橙 0/3192）
- `_trace_label_boxes.py`（真实字体 380×300）→ label problems: 0
- `_verify_fig_rules`/`_verify_space_schematic`/`_check_pkg_integrity`/`_lint`/GUI smoke/py_compile → 77/39/0/0/27/全绿
- A3a 占空间：space_different_direction 96×100%、space_upon_width 100×100%、must_cover 84×100%、no_overlap 88×100%
- 全量渲染 42 张：0 异常

## case 设计草案（下轮 r1473 合成）
- **task_id**: `EDA-Eval-DesignFlow-SchematicStripeFix-001`
- **domain**: physical_verify
- **mode**: design_flow · entry_point: `outputs/submit.zip`
- **judge_layers**: `[L0,L1]`（纯 Python primitive/renderer，无 calibre/Qt 依赖 ⇒ 静态可验，不需 L2.live）
- **prompt**: 自然语言写 xxchen 真实场景——给 DRC pattern tool 的 schematic 模块修 4 个示意图 bug（SPACE_DIFFERENT_DIRECTION 长短边反转 / SPACE_UPON_WIDTH 标签越界 / MUST_COVER 高亮盖错位 / NO_OVERLAP 需双方向条纹），其中 NO_OVERLAP 需要 renderer 支持 `stripe_deg`（rect/poly/ring 三处 stripe 路径）
- **representative input A**（assets/）: pre-fix `_prims.py`（284 行，无 stripe_deg）+ `renderer.py`（3 处 stripe 路径无 stripe_deg）+ `_common/space.py`（SPACE_DIFFERENT_DIRECTION/SPACE_UPON_WIDTH 旧几何）+ `_common/check.py`（MUST_COVER/NO_OVERLAP 旧几何）+ 一个 driver 脚本 `gen_schematic.py` 调用上述模块产出 primitive list + SVG
- **hidden B**（assets/hidden/）: 不同几何（不同坐标/尺寸/layer 名，例如 via 短边改水平方向、must_cover 露出宽度改 18、no_overlap 用 90°/0° 条纹组合），验证候选不是 hardcode A 的坐标
- **reference 解**: 改编自 xxchen 真实 post-fix 文件（加 stripe_deg 到 RECT/POLY/RING + renderer 3 处 + 4 示意图几何修正）
- **check.py 断言（≥8，subprocess 跑候选脚本解析输出）**:
  1. zip 结构 + py_compile 全过
  2. `RECT(...,stripe='x',stripe_deg=135)` 产出的 primitive dict 含 `"stripe_deg":135.0` 键
  3. `RECT(...,stripe_deg=45)`（默认）primitive dict **不含** stripe_deg 键（默认不写）
  4. `POLY` + `RING` 同样支持 stripe_deg（三处一致，不能只改 rect）
  5. renderer 对 stripe_deg=135 产出与 45 不同的 hatch 路径（解析 SVG path / 像素方向）
  6. SPACE_DIFFERENT_DIRECTION：4 个黄邻居尺寸一致（竖条 8×15），上方邻居短边正对中心长边（红箭头坐标校验）
  7. SPACE_UPON_WIDTH：width 标签 inside 卡片（x+w ≤ 94），不越界
  8. MUST_COVER：高亮 = 露出部分（宽度 < 蓝总宽），且画在蓝之后（primitive 顺序索引）
  9. NO_OVERLAP：两块条纹 stripe_deg 不同（45 vs 135），overlap 区域 hatch 方向不同
  10. 跨输入 B 守卫：B 用不同坐标，候选不能 hardcode A 的具体数值
  11. 行数/结构一致性（未删核心 primitive 类型）
  12. 无双重 stripe_deg（不重复写键）
- **negatives（≥3 distinct + live-neg 不适用 L1）**: empty_stub（无 stripe_deg，c2/c3/c4/c5 FAIL）/ print_only（只 print 期望 SVG 串，c6/c7 FAIL）/ naive_sed（只 sed 加 stripe_deg 到 RECT 漏 POLY/RING/renderer，c4/c5 FAIL）/ hardcode_a（stripe_deg + 几何全 hardcode A 坐标，c10 FAIL）
- **§4.9 trio 3-distinct**: empty→c2, print→c6, core→c4 各独有
- **自验**: REF on B PASS + negative_selftest RC=0 + SKIP_RUN eval/run_one.sh clean + judge pipeline E2E
- **真实溯源**: metadata.trace_source = {user:xxchen, host:hfeg0plg56, session_file:1795745321483_4iv57.messages.json, match_count:1229, real_task_summary:"DRC pattern tool schematic 示意图修复（stripe_deg renderer 增强 + 4 fix batch）"}

## 注意
- 与已有 case 不撞：SpacePlugMerge-001（r1468，drcpv space.py forbidden_inside）改 space.py 函数逻辑；本 case 改 schematic/examples 子模块（_prims.py/renderer.py/_common/*.py 的示意图 primitive），不同模块不同意图
- 与 CalibreRuleSuffixXform-001（r1471，calibre rule 文本变换）完全不同
- 纯 Python ⇒ 不需 .75 真工具，L1 静态即可（stripe_deg primitive dict 结构 + SVG/几何解析可纯 Python 验）
- 下轮交付 ETA: r1473
