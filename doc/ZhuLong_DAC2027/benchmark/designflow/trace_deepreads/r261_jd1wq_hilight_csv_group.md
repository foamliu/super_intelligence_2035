# 深读笔记 · r261 · jd1wq · HilightCsvGroupGen

- **trace**: `1793688752516_jd1wq` · user `e0045488` @ `hfeg0pkn004` · mc=64 · agent=lead · 248 msgs · 17 real user turns
- **domain**: layout_virtuoso (B-synthesized, L1)
- **case**: `EDA-Eval-DesignFlow-HilightCsvGroupGen-001` (k=17 a-q)
- **ledger**: 454→455 (case 251)

## 用户真实意图（按轮）

- **U1 (idx=0, Context summary/goal)**: Generate a Virtuoso SKILL script that highlights bounding boxes from a CSV, grouped by layer names (M0, bmetal, nsd/psd), each group with its own label and distinct highlight style. (已完成: parse `unidirectional_resistor_segments_across_all_arcs.csv` → 20 valid bboxes → `/home/e0045488/skills_test/vir_hilight_grouped.il` via `geCreateHilightSet`/`geAddHilightRectangle`/`geAddHilightLabel`/`geSetHilightSetHaloParameters`)
- **U2 (idx=10)**: paste TECH-2000192 / GE-2143 warnings — `geCreateHilightSet` invalid layer/purpose `("y5" "blank")`, `nil` hilight Id → 根因反馈(用户指出错误现象,非新需求)
- **U3 (idx=28)**: "it works now. please set the yellow mark also as halo" — 给修复方案(halo on yellow group)
- **U4 (idx=38)**: "shapes of M0 seems too thin compared to the other two groups" — 视觉反馈
- **U5 (idx=48)**: "can you show me what you have done for me so far" — 查询
- **U6 (idx=52, 提出需求, 未给根因)**: "i want to make gen_hilight.py more general. Please read this file /proj/lacaa/V0/workdir/e0045488/FIT/sim/tools/layer_group_label_names. The word before colon means the label to use for highlight. The string after colon means the layer name inside .csv file matching them. ... star symbol means wildcast here." — **generalize**: rules-file-driven 分组(label:pattern, `*` 前缀通配)
- **U7 (idx=98, 提出需求)**: "the gen_hilight.py does not take .csv as an argument. Please fix this problem." — CLI: csv 位置参数
- **U8 (idx=110)**: paste `--csv` unrecognized arguments error — 根因反馈
- **U9 (idx=116)**: "i need to clean all the highlights before load next .il, tell me how" — 清高亮需求
- **U10 (idx=122)**: "please do 1" — 选方案
- **U11 (idx=132)**: paste `geGetHiSet` undefined function error — 根因反馈
- **U12 (idx=150)**: paste `hilightSets` unbound variable error — 根因反馈
- **U13 (idx=166)**: "can I run a single command to clean all the highlights?" — 清高亮需求
- **U14 (idx=168, 提出需求)**: "i need you to run a batch job for me with gen_hilight.py. take in a path as an argument, a cell-name as the second argument. Now search in the path with naming pattern like `single_direction_resistor_method2_*.csv`. ... Name the output file as `<cell-name>-<when-condition>-highlights.il`" — batch runner
- **U15 (idx=224)**: "i don't need you to cope with `single_direction_resistor_method2_combined.csv` ... did you modify gen_hilight.py?" — 查询+排除
- **U16 (idx=232, 提出需求)**: "please refine run_batch_hilight.py, to take arguments with `--file-path --cell-name`" — batch CLI refine
- **U17 (idx=244, 提出需求)**: "how can I disable highlighting of all the groups except M1?" — 查询(选择性使能)

**选料判断**: U6 (generalize via rules file) + U7 (csv arg) + U9/U13 (clear highlights) 是核心 organic 需求,未给根因/未给修复方案(仅给目标)。U1 的 goal 是 SKILL 高亮 bboxes 分组。综合 → **gen_hilight.py 离线生成器**(规则文件驱动分组 + 自动嗅探 CSV 格式 + 生成带清高亮逻辑的 .il)。

## grounding(真实产物)

- **gen_hilight.py** (/home/e0045488/skills_test/gen_hilight.py, 6.5KB, stdlib only):
  - `parse_rows(path)`: 自动嗅探 comma vs whitespace 格式。comma `single_direction`: 表头 `arc,res,dir,layer,llx,lly,urx,ury,...`,按表头定位列。whitespace `unidirectional`: `res R l w a llx lly urx ury layer dir ...`,`layer = " ".join(head[9:])` 可含内部空格。`'-'` 坐标行跳过,非数值行跳过。
  - `read_rules(path)`: `Label: pattern1, pattern2` 每行一行;`#`/`;`/`/` 注释;pattern 末尾 `*` = 前缀通配,否则 `base_layer(layer)==pat` 精确匹配(`base_layer` 去 ` (N)` 后缀取首 token);首条匹配胜出;unmatched 不进组。
  - `PALETTE` y0..y9 (yellow/red/green/magenta/cyan/purple/orange/darkyellow/lightblue/lightgreen),按组循环 `color_idx % 10`。
  - `HALOS` 5 组 (over/plain/thick/0 / over/plain/normal/30 / over/fadeout/normal/10 / over/smooth/normal/20 / over/plain/thin/40),按组循环。
  - `var_name(label)` sanitize 非字母数字为 `_`,`unique_key` 去重 → `hs_<key>`。
  - `nice(x)`: `repr(float)` 去尾零(`0.5765` 非 `0.57650`,`-0.065` 保留,`0` 非 `0.0`)。
  - `.il` 生成: header(`;====` + basename + Rules file + Group 注释 + Source + Load 提示) + `cv = geGetEditCellView()` + `unless(cv error(...) return(nil))` + 清高亮块(`when(boundp('hilightSets) foreach(hiSet hilightSets when(hiSet hiSet~>enable=nil when(fboundp('geDeleteHilightSet) geDeleteHilightSet(hiSet))))` + `hilightSets = nil`) + 每组(`hs_<key>=geCreateHilightSet(cv list("<yN>" "drawing"))` + `hilightSets=cons(...)` + 每 bbox `geAddHilightRectangle(hs_<key> list(list(llx lly) list(urx ury)))  ; <res> [<layer>]` + `geAddHilightLabel(hs_<key> list(<cx> <cy>) "<label>" "lowerLeft" "R0" "stick" 0.02 nil)` 标签放该组首 bbox 中心 + `hs_<key>~>enable=t` + `geSetHilightSetHaloParameters(...)`) + 末行 `printf("Grouped bbox highlights applied.\n")`。
  - CLI: 位置 `csv`(可选) + `--csv`(可选,覆盖位置) + `--groups` + `--out`;两者都没给 ⇒ exit 2。
- **layer_group_label_names** (/proj/lacaa, permission denied): 从 .il 输出反推 3 条规则 `M0: M0*` / `nsd/psd: nsd, psd` / `BM1: bmetal*`。
- **.il 样例** (DFF-CP_to_Q_whenD-highlights.il, 4251B): 3 组 M0(14 bboxes,y0/yellow,halo thick/0)/nsd_psd(4 bboxes,y1/red,halo normal/30)/BM1(2 bboxes,y2/green,halo fadeout/normal/10)。

## B 档重定义(为何离线生成器)

真实 Virtuoso/cellview/CSV/rules 在 .75 对 e0031982 部分不可访问(/proj/lacaa permission denied,但 /home/e0045488/skills_test/ 可读 → 拿到真实 gen_hilight.py + .il 样例)。trace grounding 价值在「CSV 格式嗅探 + 规则文件分组 + SKILL .il 结构规范提取」。故重定义为 `gen_hilight.py <csv> --groups <rules> --out <out.il>`(stdlib only)。判分用隐藏 B(逗码格式,layer/rules vocab 与 A 不同)真跑候选 → 解析 .il 结构。

## DISTINCT from 现有 layout_virtuoso 系

- r236 SkillBindkeyFlattenMakeCell(bindkey 触发 flatten/makeCell)
- r233 InstM0ShapePinIdentify(识别 M0 图形+pin)
- r232 SkillM1ShapeDeleteAudit(SKILL 删 M1 图形审计)
- r229 DiffNetConnLayerSelect(跨层连接 net 选择)
- r226 PcellPatternGeoDiag(pcell pattern 几何诊断)

本 case 是 **CSV bbox → 分组高亮 .il 生成器**(规则文件驱动 + 格式自动嗅探 + 调色板/halo 循环 + 清高亮逻辑),非 bindkey/shape 删除/pin 识别/连接选择/pcell 几何。

## case 结构

- **assets/A** (可见): config_A.csv(whitespace,6 valid bboxes + 1 无 bbox) + rules_A.txt(`M0: M0*`/`nsd/psd: nsd, psd`/`BM1: bmetal*`) + prompt.txt + task_brief.md
- **hidden/B** (逗码格式): config_B.csv(8 parsed → 7 valid,含 unknown_lay unmatched + R9p 无 bbox) + rules_B.txt(`M1: metal1*`/`ND/PD: ndiff, pdiff`/`M2: m2*`) + hidden_manifest.json
- **reference**: golden_solution.py(忠实于真实 gen_hilight.py) + golden_A.il + golden_B.il + check.py(17 条 a-q) + 6 negative(empty_shell/print_expected/hardcoded_A/core_deleted/stub_no_clear/stub_no_halo) + negative_selftest.py + reference_submit.zip

## 自验

- golden 17/17 PASS ✓
- 6 negative 全 FAIL ✓(empty_shell→e, print_expected→i, hardcoded_A→d, core_deleted→h, stub_no_clear→g, stub_no_halo→k)
- §4.9 三假(empty_shell/print_expected/core_deleted)全 FAIL ✓
- test==disk check.py byte-equal ✓(11638B)
- 3-run determinism sha256 一致 ✓(同 --out 路径)
- 断言闸门 k_rationale=17=k_check(a-q)≥8 ✓

**DEBT: 0**。
