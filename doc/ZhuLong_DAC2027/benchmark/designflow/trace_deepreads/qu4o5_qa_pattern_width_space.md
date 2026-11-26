# deep-read: qu4o5 — joyc @ hfeg0plg16, mc=156 (physical_verify, QA pattern generation)

**session**: 1794539053522_qu4o5, 160 msgs, 45 editor / 13 read_files / 15 run_approved_command.
**user**: joyc (NEW, not in known-reject set). host hfeg0plg16.

## user intent (A档 produce-task author-new-script)

U#0 (原话): "M2_20261109.gds 是你需要生成的 QA PATTERN gds，是依据 M2.rules 这个 csv file 作为输入件，第一列是 rule name，第二列是 description 以及 rule 的约束条件和 check value。优先覆盖 width、space 这类直观简单 rule 的 QA pattern 绘制，通过读取 csv file 生成对应 good/bad 测试 pattern，无需一开始覆盖复杂规则。请使用 python 生成对应 rule 类型的 pattern 脚本，以便固定同类型rule的pattern生成模式。同时根据 csv file生成仅有 rule name 的 rule_list"

U#1 = U#0 (dup). U#2 给 techfile/display/layermap 路径（Virtuoso QA pattern 配置参考）。U#3 解释 enclosure upper/lower metal 连接性判断（但 pass 1 不覆盖）。

= **A档合格 produce-task author-new-script**（提需求未给根因/方案；"优先覆盖 width/space...无需一开始覆盖复杂规则" ⇒ pass 1 = width/space only, enclosure deferred）。

## assistant 交付 (qa_pattern_gen.py, 6632+ chars, 多版迭代)

核心算法（pass 1: width & space）：
- parse M2.rules CSV (rule_name, description) → classify by keyword: "width"→width, "space"→space, else→other (skipped in pass 1)
- parse_direction: "Vertical"→vertical, else→horizontal
- parse_value: regex `=\s*([0-9]+\.?[0-9]*)` 提 check value (um)
- **width rule**: good = wire with width==value; bad = wire with width < value (too narrow, violates min width)
  - horizontal wire: runs in x (length L=1.0), width in y == value → rect(0,0,L,value); bad width = value*0.8
  - vertical wire: runs in y, width in x == value → rect(0,0,value,L); bad width = value*0.8
- **space rule**: good = two parallel wires gap==value; bad = gap < value (too close, violates min space)
  - horizontal space (gap in x): two vertical wires separated in x by value; bad gap = value*0.8
  - vertical space (gap in y): two horizontal wires separated in y by value; bad gap = value*0.8
- output: GDS cells (<rule>_bad / <rule>_good) + rule_list (rule names) + coverage report
- BAD_FACTOR = 0.8 (bad = 80% of value → violates min)
- geometry helpers: rect / wire_h / wire_v / diag_wire (45°), datatype 651 (M2 color A) / 652 (color B)

## case modeling (B档 synthesized mock-behavioral)

把"live gdspy GDS QA pattern 生成"重构为纯 Python CSV fixture（核心 classify + direction + value 解析 + good/bad 几何生成算法不变，mock gdspy/GDS → JSON patterns.json + rule_list.json 确定性输出）：
- visible A: M2_rules_A.csv (2 width + 2 space + 1 enclosure-skipped) + original_qa_pattern_gen.py.txt + input_spec.json + task_brief.md
- hidden B: M2_rules_B.csv (2 width + 2 space + 1 enclosure, different values/names)
- hidden B2: M2_rules_B2.csv (1 width + 1 space + 1 enclosure, different layer M3, different counts — anti-hardcode)

**15 条件 a-o**：结构2(a:zip含.py / b:py_compile exit0) + 运行1(c:跑B exit0+patterns.json+rule_list.json) + rule_list/skipped 2(d:count==oracle / e:enclosure skipped) + width 4(f:horizontal good y-extent==value / g:horizontal bad y-extent==value*0.8 / h:vertical good/bad x-extent==value/value*0.8 + l:bad<good) + space 4(i:horizontal good gap_x==value / j:horizontal bad gap_x==value*0.8 / k:vertical good/bad gap_y + l:bad<good) + layer 1(m:layer==oracle) + B2 anti-hardcode 1(n:B2!=B + B2==oracle) + determinism 1(o:rerun B byte-identical)

**自验**：ref GOLD PASS 15/15 ✓；4 neg(naive_empty→c / print_expected→c / core_deleted→d / naive_no_bad→j[bad gap==good])全 FAIL ✓；§4.9 三假(空壳=naive_empty / 只print=print_expected / 删核心=core_deleted)全 FAIL ✓；NEGATIVE_SELFTEST ALL-FAIL=True ✓；k_rationale==k_check==15≥8 ✓。

**谱系**：produce-task author-new-script 第N子型 qa-pattern-width-space-gen（physical_verify 域，QA pattern 生成），anti-hardcode dual-hidden-rules-csv（B 4 gen vs B2 2 gen, 不同 layer/value/names）。

r527 动词法：qu4o5 U#0 "请使用 python 生成...脚本" = produce-task author-new-script（提需求未给根因 ⇒ A档）。
