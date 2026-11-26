# r534 deepread — 1794535376790_xbcoz (xxchen@10.129.2.10, mc=373)

## trace 一句话
DRC QA Pattern Tool `prl_space` 函数缺陷修复（physical_verify produce-task，optimize-modify 子型）：工程师 QA 调试 `PW_S_016_02` 报告 3 缺陷，assistant 读 prl_space.py / pattern_common.py / 7 good_pattern / bad_pattern/2 / qa_config / layer.map / LDR.json → 定位根因 → 改代码 → 跑 gdspy 生成 GDS 验证 → 改文档/history/manual_html。276 msgs / 1.28MB。

## USER 轮（真实需求，已剔 setup/compact）
- **USER#4**（seed task）："QA pattern debug: PW_S_016_02 QACELL prl_space PWx 2.016 {lengthLower 123.046} {lengthUpper 246.094} {width 10.0} {auxRegion SA} 该function问题有点多分析如下：1）good pattern 1: 标注为 BORD:drawing-1-width 的pattern 报错了…Minwidth 宽度约束并未启用…需要把Minwidth 置为 no。修改这个function，实现该参数功能。另外pattern 1 的几个pattern 在Y方向上的距离过近，label 标签都重叠到了其他 pattern上去了…调整Y方向的距离，确保下一个pattern 不能覆盖住当前pattern的标签。"
- **USER[156]**："这个label 标签： BORD：drawing-1-ltUpper ，是违反了 space value，为什么不改成： BORD：drawing-1-space 更合理？" → standard 行 label 后缀 ltUpper→space 改名
- **USER[216]**："2） bad pattern 2:  PRL （并行走线长度) 没有满足 rule的 lengthLower的要求。" → dislocated PRL 修复

## 3 缺陷根因 + 修复（assistant 分析）
1. **Minwidth 未实现**：good pattern 每行画 standard/lengthLower/width 三行。`-width` 行宽度=layer_width-grid、PRL=lengthLower 边界（≥lengthLower 规则适用）、间距=space-grid（<space）→ 真违规。但 rule 无 `{Minwidth}`（默认 no=无宽度约束）→ 旧代码恒画此列 → 伪真误报。修复：`has_width_row = min_width_mode in ("single","both")`；draw_variant_column 过滤 width 行。
2. **Y 行距过近**：行间距固定 `bord_space_y`(=10)，但 label 高度=row_h(=w+s+w2≈22)，label 跨度 [y1+0.1, y1+0.1+row_h] 超出 10 → 被下行几何覆盖。修复：常量 `ROW_LABEL_CLEARANCE=0.5`；y = max(y1+gap, y1+0.1+row_h+ROW_LABEL_CLEARANCE)。
3. **bad pattern 2 dislocated PRL**：dislocated 几何上条水平错位 w，实测 PRL=drawn_base−w；旧 drawn_base=run_length → PRL=lengthLower−w < lengthLower → 规则不适用 → bad 不违规。修复：`dislocated_base(run,off)=snap(run+off)`，good_pattern/2 与 bad_pattern/2 各 row 改用之。

## assistant 工具链（关键）
read_files(prl_space.py/pattern_common.py/7 good_pattern/bad_pattern/2/qa_config_device.txt/layer.map/LDR.json) → editor 改 prl_space.py + 7 good_pattern + bad_pattern/2 + manual md + manual_html + update_history → run_approved_command(python-runner: py_compile + 跑 qa_pattern_tool.py 生成 QA.gds + gdspy verify_prl_gds.py 验证 label/几何 + skill_config 回归) → final_combined.py 全绿。

## 合成（B 档 synthesized）
- case: **EDA-Eval-DesignFlow-PrlSpaceQaFix-001**（physical_verify，L2-boundary，纯 Python+桩 离线验证）。
- 资产 A（SUT 可见）：buggy prl_space.py（撤销 3 修复）+ pattern_common.py 桩 + function_common.py 桩 + task_brief.md（QA 报告 3 缺陷）。
- 交付：SUT 提交修复后的 prl_space.py 进 submit.zip。
- 隐藏 B：B 规则参数（space/lengthLower/lengthUpper/width 与 A 的 PW_S_016_02 全不同）+ B1/B2 dislocated_base probe（312.0,6.0 / 375.5,8.0）防硬编 A 常数。
- check.py：14 条件 a-n。静态 7（c-g：ROW_LABEL_CLEARANCE/has_width_row/dislocated_base/width 过滤/Y 间距 max）+ 动态 7（h-n：桩导入 PrlSpaceContext 构造，验 has_width_row/width2/upper_limit/dislocated_base/确定性/防硬编）。注入 stub gdspy/pattern_common/function_common 离线导入。
- 自验：ref PASS 14/14 ✓；5 neg（empty/print_expected/core_deleted[硬编129.046]/hardcode_a[硬编123.046+10]/no_clearance）NEG_RC=0 ALL-FAIL ✓；§4.9 三假全 FAIL ✓；k_rationale=k_check=14≥8 ✓。

## 谱系
physical_verify produce-task 第六子型 **bug-fix-gate**（读 QA 报告→改既有 context 类→产修复版）：与 r531 optimize-modify（改 deck）互补——r531 改 SVRF deck 数据，r534 改 Python 代码逻辑。防硬编 (n) 属命名空间泛化族（B 参数与 A 不同，dislocated_base 须按参数计算非硬编 A 常数）。

## 选料
11/13 池 4-shard fresh 883 候选→top C-dominant peek 6（l4tre release-note REJECT / qvnvw setup-only / xbcoz HIT / 3hw3m run-existing REJECT / cydnq doc-QA REJECT / dr7mm test-script ambiguous-REJECT）。r527 kw-source 归因法 6/6 正确分类（1 produce / 5 non-produce）。xbcoz USER#4 动词=修改+实现+调整 → produce-task。
