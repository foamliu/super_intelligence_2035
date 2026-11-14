# Deepread · 9rqab · floorplan re-block GDS (2026-11-14 r559)

**trace**: `1794483008635_9rqab.messages.json` · junweiw @ hfeg0plg67 · mc=97
**keywords**: floorplan:201;schematic:128;drc:100;cmos:65;.gds:52;.cdl:22;lvs:13;calibre:10
**size**: 386985 bytes · 101 msgs · 6 real user turns
**domain**: layout_aether (GDS floorplan re-block via gdspy/python)
**verdict**: ACCEPT · A档合格 produce-task author-new-GDS (USER#3 提需求未给根因/方案)

## Intent evolution

- **USER#0/msg0** "我给你GDS还有CDL" — minimal handoff, only CDL present (`/home/junweiw/Desktop/CDL/VwlnSGx64_3T_1Mat.cdl`, top `VwlnSGx64_3T_1Mat`, 字线信号产生矩阵 hierarchy). assistant: list_allowed_files Desktop → read CDL → editor find_gds.py (os.walk 找 .gds/.gds2/.oas) → run → 0 hits → ask_question 请放 GDS + 明确要做什么。
- **USER#1/msg13** "GDS路径：/home/junweiw/Desktop/GDS/R_SaCtrol_sub_UV_bot.gds" — provides GDS. assistant: list GDS dir (R_SaCtrol_sub_UV_bot.gds + .cdl) → read CDL → editor inspect_gds.py (gdspy check) → run → gdspy 1.6.13 可用但简易扫描器 0 cell → editor inspect_gds2.py (gdspy.GdsLibrary read_gds + cells + ref_cell) → run → **516 cells** parsed → read CDL 100-1286 + 1076-1286 (顶层 R_SaCtrol_sub_UV_bot = drcpa_array: Common_sub XI0 + IsoOcEn_Burnin_bot XI1, std cells nand2Y/nor2Y/invY/..., devices ptk/ntk/ntk_hv/ntn/ptn, MarkVHV, brknetM1/M2) → ask_question "做什么" (LVS / GDS器件清单 / Calibre deck / **floorplan M2 走线优化**).
- (ask_question response) user 选 "分析现有 layout 的 floorplan，给出如何调整以最节省 M2 signal 走线". assistant: editor floorplan_analysis.py (gdspy extract top references offset/rotation/bbox + port label distribution + block bbox) → run → 顶层两 block **完全重叠** (Common_sub abs(-96.6,23.6)→(-17.6,169.1) 78.9×145.4µm; IsoOcEn_Burnin_bot abs(-102,23.6)→(17.1,169.3) 119×145.7µm; 冲叠 78.9×145.4) → read HLP.rule/display.drf 找 M2 layer 号 → editor grep_layers.py (M2/met2 layer mapping) → run → 分析结论：顶层非并排而是子 cell 叠加，2D 布局+M2 走线在子 block 内部。
- **USER#3/msg61** "顶层俩个大的block需要保留，可以给我一个新的GDS" = **produce-task author-new-GDS**. assistant: editor make_floorplan_gds.py → make_floorplan_gds2.py (gdspy read SRC, 取 Common_sub + IsoOcEn_Burnin_bot 两 cell, **reposition 左右并排非冲叠** Common(0,0)→(78.9,145.4) left / Iso(80.9,0)→(200.x,145.7) right, 保留引用不拍平, 重排顶层 pin label 外围框架 U右/V中/G左/电源底, write OUT R_SaCtrol_sub_UV_bot_M2opt.gds) → run → 2.21MB 516 cell 层级完整 → editor verify_floorplan.py (read-back: 两 block 不重叠/层级保留/顶层构成) → run → 输出表 (Common (0,0)→(78.9,145.4) 78.9×145.4; Iso (80.9,0)→(200,145.7) 119×145.7).
- **USER#4/msg75** "floorplan的骨架还是维持原来的，是特意这么设计的 / 可以翻转 / 给SVG" = clarify (keep original skeleton, allow flip, give SVG). assistant: editor make_svg.py (gdspy draw 2 SVG: floorplan_skeleton.svg 原始骨架 + floorplan_flipIso.svg Iso 水平镜像 U/V 边对换, 端口分组着色 U绿/V红/G紫/电源灰) → run (多版 editor 修 label dedup/phys transform/rect/text) → 2 SVG 生成.
- **USER#5/msg93** "怎么打开这个svg,有工具吗" = how-to Q&A. assistant: 文字答 xdg-open/firefox/eog.
- **USER#6/msg95** "直接帮我打开吧" = run-existing. assistant: editor open_svg.py (xdg-open + DISPLAY check) → run → pid 986320 打开.

## 核心算法 (case 建模对象)

**USER#3 produce-task 的算法核心** = make_floorplan_gds2.py 的 re-floorplan:
1. gdspy read_gds(SRC) → lib.cells dict (516 cells), top = cells[top_name]
2. 取两个"大 block" cell (Common_sub, IsoOcEn_Burnin_bot) — 按 top.references 里指定的两个
3. 算每 block bbox (w×h)
4. **reposition 左右并排非冲叠**: block A origin=(0,0), block B origin=(wA+gap, 0), 同基线, 垂直方向对齐
5. 重排顶层 pin label 外围框架: U 侧 → 右外沿, V 侧 → 中间, G 侧 → 左外沿, 电源/配置 → 底部
6. 保留引用方式 (不拍平), 516 cell 层级完整
7. write_gds(OUT) 新 GDS, 顶层名不变

## case 设计 (B档 synthesized mock-behavioral, 承 r539-r558 族)

**FloorplanReblockGds-001** (layout_aether L2-boundary): 把"live gdspy GDS re-floorplan"重构为纯 Python JSON layout deck fixture (核心 hierarchy parse + 两 block reposition 非冲叠 + pin label 外围重排 + write 算法不变, mock gdspy):
- 读 layout_deck.json (cells{name:{polygons,labels,references}}, top_cell) + floorplan_spec.json (keep_blocks[A,B], placement=side_by_side, gap, pin_grouping{U:right,V:middle,G:left,power:bottom})
- 找 top cell 两 block refs → 算 bbox → reposition A(0,0) B(wA+gap,0) 非冲叠同基线 → pin labels 按 group 重排到对应 periphery → write output deck (sorted keys 确定性)
- 可见 A: original_make_floorplan_gds.py.txt (真实 gdspy 逻辑注释) + layout_deck_A.json + floorplan_spec_A.json + input_spec.json + task_brief.md
- hidden B: 不同 cell 名 + 不同 bbox (两 block 冲叠) + 同 spec 结构 → 验 reposition 正确; B2: 第三变体 (反硬编码)

**条件 (≥8, 每条独立可 FAIL)** — target 16 a-p:
a: zip 含 floorplan_reblock.py 可解压
b: py_compile exit 0
c: B 跑 exit 0 + out_deck_B.json 存在
d: 输出 top_cell 名 == spec.top_cell (保留)
e: 输出含两 block refs (A+B 都在)
f: **两 block 非冲叠** (bbox 交集面积 == 0) — 核心
g: block A origin == (0, 0)
h: block B origin == (wA + gap, 0) (wA 从 deck 实算)
i: 两 block 垂直对齐 (origin y 相等)
j: block bbox 尺寸保留 (w/h 不变, 仅 position 变)
k: U-group pin labels 落右 periphery (x ≥ block B 右沿)
l: V-group pin labels 落中 periphery (x ∈ [block A 右沿, block B 左沿])
m: G-group pin labels 落左 periphery (x ≤ block A 左沿)
n: power-group pin labels 落底 periphery (y ≤ baseline)
o: pin 总数保留 (== 输入 deck pin 数)
p: B2 反硬编码 (B2 block B origin == wA2+gap, ≠ B 的值) + 确定性 (重跑 B byte-identical)

## 自验计划
- ref GOLD: floorplan_reblock_ref.py 跑 B+B2 PASS 16/16
- 4 negative (naive_empty / print_expected / core_deleted / naive_wrong_algo) 全 FAIL
- §4.9 三假 (空壳 / 只 print 期望 / ref 删核心) 全 FAIL
