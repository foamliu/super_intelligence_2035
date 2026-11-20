# fmdbz — spaceUponWidthPass DRCW_mark1 shield-gap add (layout_virtuoso)

**session**: 1794878796288_fmdbz · yzwang @ hfeg0plg06 (10.129.8.13) · mc=87 · 63 msgs / 1 real user_input · 303 KB

## 用户原话 (trace verbatim, U#0)

> 我在/home/pdk/yzwang/06_AI_workspace/test9放了一个文件叫spaceUponWidthPass.il的脚本，这个pcell会生成两排pattern，其中第一排和第二排的倒数第二个pattern是两个矩形中间隔着一段距离，我现在希望在这个space上画上一层DRCW_mark1这层，请帮我作业。

(原文有口误 "我在我在/home/pdk我在/home/pdk" — 保留逐字)

## 助手 gold 链

1. `list_allowed_files` /home/pdk/yzwang/06_AI_workspace/test9 → 3 files: spaceUponWidthPassFail_OPC01_patched.il, spaceUponWidthFail.il, spaceUponWidthPass.il
2. `read_files` spaceUponWidthPass.il (598 行, 分段读完) — 完整映射脚本结构: pcDefinePCell, 2 排 pattern (part1 lengthLower / part2 lengthUpper), 每排末尾 shield pattern (3 矩形: 底部大矩形 basex:basey ~ basex+3w:basey+w, 顶部窄条, 右上角小矩形 basex+2.5w:basey+w+space-grid ~ basex+3w:basey+2w+space-grid)
3. `ask_question` 确认 "倒数第二个 pattern" = shield pattern (3 矩形那组) — user 回答 "每排严格倒数第二个（shield pattern，3 个矩形附近）"
4. `read_files` TechFile/tech.tf → 查证 DRCW_mark1 = layer "DRCW", purpose "mark1" (GDS 321/51, calibre LAYER DRCW_mark1 8880), SKILL 中 `list("DRCW" "mark1")`
5. policy.writableRoots 拒写 /home/pdk/... → `run_approved_command` cp 原文件到 /home/yzwang/spaceUponWidthPass_patched.il
6. `editor` 3 处编辑:
   - **edit 1** (line 39 后): 加 `;DRCW mark1 layer = (DRCW, mark1)` 注释 + `lppDRCWmark = list("DRCW" "mark1")` 变量定义
   - **edit 2** (part1 [pattern10] shield 的第 3 个 dbCreateRect 后, line 269 后): 加 `;DRCW mark1 on the space (gap)` + `dbCreateRect(cv lppDRCWmark list(basex + 2.5*width : basey + width, basex + 3*width : basey + width + space - grid))`
   - **edit 3** (part2 [pattern12-1] shield 的第 3 个 dbCreateRect 后, line 510 后): 同 edit 2 结构
7. `run_approved_command` wc -l + grep DRCW 验证: 610 行, DRCW 出现 3 处 (1 变量定义 + 2 dbCreateRect), lppDRCWmark 在 line 41 (首次使用前定义)
8. `run_approved_command` diff 原文件 vs patched → 3 处 +additions (39a40,41 / 269a272,276 / 510a518,522)

## 关键 gold 事实

- **DRCW_mark1 层映射**: layer="DRCW", purpose="mark1" (查证 TechFile/tech.tf line 99: `( mark1 51 mark1 )`, calibre layer map 8880)
- **mark rect 坐标** (两处相同结构):
  - x1 = `basex + 2.5*width` (右上角小矩形 x 起点, 即 shield 大矩形与右上角小矩形的 X 重叠区起点)
  - y1 = `basey + width` (大矩形顶部, 即 space gap 底部)
  - x2 = `basex + 3*width` (shield 右边界)
  - y2 = `basey + width + space - grid` (space gap 顶部, 即右上角小矩形底部)
  - ⇒ mark 矩形坐落在「大矩形顶 ↑ 右上角小矩形底」之间的垂直 space 上, X 方向覆盖两矩形的重叠段
- **变量表达式**: 坐标全部用 `basex`/`width`/`space`/`grid` 表达式, 非字面量 — 因 pattern 位置随 PCELL 参数 (lengthLower/lengthUpper/space) 动态变化
- **lppDRCWmark 定义位置**: line 41 (在 part1/pattern 之前), 首次使用在 line 273 — SKILL let-binding 作用域内合法

## reframe 设计 (档 B)

真实 gold = live Virtuoso PCELL 跑 patched .il (依赖 live Virtuoso + PDK TechFile, 不可沙盒复现) → reframe 为 **静态源码结构校验** (承 TapPcellBot-001 / GdsRailLabelRestore-001 范式):

- **A visible**: 原 spaceUponWidthPass.il (598 行, 随附件提供) + 用户原话 prompt
- **候选交付**: patched .il (修改后的完整文件)
- **check.py**: 静态解析候选 .il, 验 15 teeth (a-o): zip/pcDefinePCell/lppDRCWmark 变量/层赋值/2 处 dbCreateRect/坐标含 basex+width/2.5*width/space-grid/shield 后位置/行数>598/用变量非内联/≥3 模式变量/反 B 禁字面量/3-seed/定义 1 次+不同行+[pattern11] 保留
- **hidden B**: anti-cheat 禁字面量 (DFM/mark2/lppDFMmark/3.5*width/OPC1_mark) 嵌 check.py, 候选 .il 不得含 B 字面量 (B = 不同 mark 层的假 fixture)
- **anti-hardcode**: mark rect 坐标必须是 `basex`/`width`/`space`/`grid` 表达式 (≥3 个变量名), 非纯字面量 — 防候选硬编具体数值

## 自验

- ref check.py → 15/15 PASS
- 4 neg 全 FAIL **distinct**: empty_stub(a,c,d,e,...) / print_only(e,f,g,h,k,l,o) / literal_coords(f,g,h,l) / wrong_layer(c,d,e,...,m)
- §4.9 三假 (empty_stub/print_only/literal_coords) 全 FAIL distinct (a / e / f,g,h,l)
- roundtrip jsonl test field == disk check.py sha256[:16] = 79cb12a3e093099b ✓
- JUDGE-tree 独立 dir PASS 15/15 ✓ (check.py 自包含, 零路径依赖)

## 意图审计

**keep** — yzwang 真实意图 (在 spaceUponWidthPass.il 的每排 shield pattern 的 space gap 上补画 DRCW_mark1 层) 完整保留, reframe 是 grounding (live Virtuoso PCELL → 静态源码结构等价校验, 离线化) 非加难:
- DRCW_mark1 层映射 (DRCW/mark1) 直出 TechFile 查证, 非虚构
- mark rect 坐标表达式 (basex+2.5*width / space-grid) 直出 gold 的 dbCreateRect, 非合成
- "倒数第二个 pattern = shield pattern" 由 ask_question user 确认, 非臆测
- 2026-11-15 reaudit 后 produce/modify-SKILL 类合法第 N 例 (与 TapPcellBot generate-SKILL 正交: 本案 = modify existing PCELL add-mark-layer, TapPcellBot = generate new PCELL from spec)
