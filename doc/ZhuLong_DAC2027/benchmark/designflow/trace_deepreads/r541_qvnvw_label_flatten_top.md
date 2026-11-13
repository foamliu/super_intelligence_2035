# r540 deepread — qvnvw (xxchen, 10.129.35.69, mc=427, layout_aether)

**session**: `1794389800331_qvnvw.messages.json` (322 msgs, 2.0 MB), user `xxchen` @ `10.129.35.69` (hfeg0plg53).
**keywords**: drc:1348; .gds:217; pdk:6; pex:5; dbcreatelabel:3; gdsii:2; cadence:2; waveview:1; tool dbCreatePath.
**tools used**: editor×80, run_approved_command×36, read_files×30, list_allowed_files×12, ask_question×3.

## 用户意图（动词法分类 → produce-task author-new-flow）
- USER#0: "阅读AGENTS.md 阅读PROJECT.md"（bootstrap，非任务）
- USER#12: brainstorming skill（设计阶段，HARD-GATE 先设计后实现）
- USER#62: "开始编写吧"（批准设计，转入实现）
- **USER#220（核心需求轮，A档可用）**: "### 新增流程：复制label到最顶层。示例: QACELL PW_S_014_00_c space_var。我看到产生的label在子cell内部，顶层cell：PW_S_014_00_c中并没有label。创建一个新的流程，在所有的cell放置完毕后，执行该流程。实现功能：把底层cell中的label 都复制到顶层cell上面。"
  - 动词法：提出需求（"创建一个新的流程…实现功能：把…复制到…"），未给根因/修复方案 ⇒ A档合格轮。
- **USER#286（细化/反馈轮）**: "这不是我想要的，需要排除掉 label 描述 pin TOOL TECH textLayer 230;0 修改并优化" —— 用户指出前一版把描述类 label 也复制了，要求排除 textLayer 230;0 上的描述文字。此轮给出修复方向 ⇒ 不作 A档任务说明（作 hint）。

## assistant 工具链与产物
- 路径：`/home/xxchen/workspace/DRC_pattern_tool/0.5/device_rule1/QA_Pattern_tool/script/label_flatten.py`
- editor 分片写入 label_flatten.py（IDX 231 初始写，239/256/265/267/273/279/281/283 增补，287-297 排除逻辑改写，313/315 文档更新）。
- 离线自检：run_approved_command 跑 py_compile + group 校验(91/91) + 几何校验(13/13) + 全 PW 回归 26 cells 全绿。

## 交付件算法（gold = label_flatten.py，基于 gdspy）
1. `_translation_only(ref)`：判纯平移（rot≈0, mag≈1, 无 x_reflection）。
2. `_copy_single_label(root, lb, off_x, off_y)`：复制 label 到 root，保留 layer/texttype/anchor/rotation/magnification，position += offset。
3. `_walk(root, cell, off_x, off_y, path, exclude)`：环路保护(path set)→跳过 exclude (layer,texttype)→复制 label→沿 references 递归(累加 origin)，非纯平移发 warning 但仍处理。
4. `copy_descendant_labels_to_roots(lib, exclude=None)`：root = 不被任何 cell 引用的 cell；对每个 root 从自身 _walk；返回 root 名列表。
- 排除：textLayer 230;0 上的描述类 label（规则描述大文字 + pattern 编号）不提升到顶层，只提升真正的信号 label（pin 层）。

## 合成决策（B档 synthesized，mock-behavioral check mode）
- **为什么 mock-behavioral**：gold 真 drive gdspy（GDS 库/cellview/label 遍历），但 gdspy 不在判分环境（本地 python 无 gdspy，仅 .75 有）。沿用 FreeTrackFinder-001（r539）/Gds2Lef-001（r528）/DbusMetalFlowReport-001（r530）第三 check mode (c)：剥离 live license/gdspy 依赖，保留算法正确性验证——把 gdspy 库重构为纯 Python JSON fixture（cells/labels/references/exclude），判分跑候选脚本于隐藏 fixture，断言扁平化算法逻辑（root 识别/offset 累加/exclude/环路保护/非平移告警/属性保留/多放置/确定性）。
- **anti-hardcode dual-hidden**：B（8 cells，含环/非平移/多放置/第二 root ORPHAN，exclude 230;0）+ B2（5 cells，3 级深层次 R→A→B，exclude 99;1，无环无非平移）。两套 cell 名/坐标/层次/exclude 层全不同，硬编 B 答案必在 B2 失败。
- **判分升级**：从 data-validation 升级到 code-execution-validation（subprocess 跑候选脚本于 fixture，断言数值输出）——承 r539 第八子型 author-new-script，本例为 produce-task 第九子型 label-flatten-flow（标签扁平化）。
- **A档可用性**：USER#220 是合格 A档任务说明轮（提出需求未给方案）；本轮按既有 B档 synthesized 落库（与 r523-r539 一致），A档试点另跟踪。

## 16 条件 a-p（k_rationale == k_check == 16 ≥ 8）
- a zip+py_compile / b B 运行 exit0+report / c B roots=[ORPHAN,TOP] / d B TOP 计数=7 / e B ORPHAN 计数=1 / f B top_pin@(0,0) 自身 label / g B leaf_pin@(112,223)+@(312,423) 多放置 / h B mid_pin@(11,21) 中间层 offset / i B TOP 无 layer-230(exclude) / j B nt_pin@(7,8) 非平移仍处理 / k B warnings 含 non-translation / l B cycA_pin@(1,1)+cycB_pin@(3,3) 环路保护 / m B2 roots=[R,R2] / n B2 R 计数=3+R2=1 / o B2 bpin@(1017,2028) 3 级深 offset + 无 layer-99/tt1 / p 确定性重跑一致。

## 自验
- ref GOLD B+B2 PASS 16/16 ✓；4 neg(naive_empty/print_expected/naive_wrong_algo/core_deleted) NEG all-FAIL NEG_RC=4/4 ✓；§4.9 三假(空壳/print期望/删核心)全 FAIL ✓；k_rationale==k_check==16≥8 ✓；test==disk check.py roundtrip ✓。
