# Deepread · 1789545236143_3uubi (kenwang @ hfeg0plg07, mc=312, physical_verify)

**Session**: `1789545236143_3uubi.messages.json` · 213 msgs · 1.8 MB · agent=lead · 2026-09-16
**Domain**: physical_verify (DRC automation template engine) · kw: drc:677;calibre:209;.def:24;pyaether:3;aether:3
**Tool mix**: read_files:56 / editor:31 / list_allowed_files:3 / ask_question:3 / run_commands:3 / search_codebase:3

## 用户意图（produce-demand，A-档 seed）

USER#2 (msg[2], ts=1789540042218) 原话：
> /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/metalOption/test/ 在当前路径下面有2个文件
> drc_auto.py ts_auto.sh ,这是一个拆分metal option的脚本,可以根据 不同的metal option
> 分配 x或者 y，或者yy 等 字母对用的metal 层, 现在我遇到一个问题，当我有一条 rule ，
> 他是包含所有的metal 层的时候，但是每一个metal option对应的又不是同样多的metal 数量，
> 我如何修改这个脚本，可以让它在不同的metal option 中通用呢

USER#4 (msg[168]) 追加验证：4_5_54_My.rules 的 My_R_4_RCM rule 在不同 metal option（y 最高 M11）时如何调整。
USER#212 (msg[212]) 同事建议调 macro —— 证实是 produce-task（多轮迭代修改脚本），非 Q&A。

**核心需求**：drc_auto.py 是 Python 模板引擎（.rules `#loop`/`$<var>` → .drc，按 metal option
x/y/yy/z 分配 metal 层）。一条覆盖所有 metal 层的 rule，每个 option 的 metal 数量不同
（y:7-11=5 层，z:14-15=2 层），固定 `#loop($<y_start>,$<y_end>)` 模板无法用一个循环覆盖
不同长度的 option 区间。需通用化：让一条 rule 在不同 metal option 下自动正确展开。

## agent 解法（13 次 editor 演化）

加 `OPT_MAP` (metal_number → option_suffix) + 三个核心函数：

1. **parse_opt_map(opt_map_str)**: `"3:xa,4:x,7-11:y,14-15:z"` → `{3:'xa',4:'x',7:'y',...,11:'y',14:'z',15:'z'}`
   - 支持 `metal:suffix` 单条 + `start-end:suffix` 区间（闭区间）
   - 非法条目跳过（不报错退出）
2. **build_opt_map_from_vars(vars_dict)**: 从 `y_start=7,y_end=11` 对自动推导 `{7..11:'y'}`（`_start`/`_end` 前缀作 suffix）
3. **$<opt> / $<layer> 模板变量**: `#loop($<M_start>,$<M_end>)` 内每个 metal 自动套后缀 `M{m}_{opt_map[m]}`

最终 drc_auto.py (msg[41] editor new_text, 23551 B) 含：parse_opt_map / build_opt_map_from_vars /
parse_args(input_file, bottom, top, var=val; 特殊 var 'opt_map') / #var() 指令 / @[/key/] comment 指令 /
load_comment_file / process_comment_directive。

## 本案合成（B-档 L1 synthesized）

抽「metal-option 通用展开段」做成纯 stdlib `metal_opt_rule_expander.py`：
- `parse_opt_map` + `build_opt_map_from_vars`（reserved M/bottom/top 排除，不当 option）
- `#var` / `#loop` / `#endloop` 模板解析 + `$<mnum>`/`$<opt>`/`$<layer>`/`$<M_start>`/`$<M_end>` 替换
- 不在 opt_map 的 metal 跳过（covered_metals / skipped_metals）
- 双输入模式：`--opt-map` 显式 / `--vars-file` 自动推导
- 输出 JSON：opt_map / per_option_counts / expanded_lines / total_lines / covered_metals / skipped_metals

**visible A** = 真实 opt_map `3:xa,4:x,5:xb,6:ya,7-11:y,12-13:yy,14-15:z` + 真实 .rules 模板结构（rule_name=My_R_4_RCM/SPACING/0.14）
**hidden B** = opt_map `1:m,2-3:my,4-6:mx,7-9:mz,10:mzr`（不同 option 集/范围/rule 名 DRC_B_GUARD/ENCLOSURE/0.08）
**hidden B2** = opt_map `2:a,3:a,5:b,6:b,9:c`（gap 4/7/8 测 skip）
**hidden A_vars** = vars a_start=2/a_end=4/b_start=7/b_end=9（测 build_opt_map_from_vars + skip 5/6）

check.py k=14 a-n（6 条交叉输入 guard：c/d/e/f/g/i/j）。ref 14/14 PASS，4 negatives（empty/print_expected/core_deleted/hardcode_a）全 FAIL。

## 与 kenwang 既有 9 case 的正交性

| 既有 case | 主题 | vs 本案 |
|---|---|---|
| DrcPyEnvDiag-001 | drc_auto.py **解释器 env**（shebang/glibc）| 正交（env 非 splitting 逻辑）|
| DRCSpecGen / QaWidthPatternGen / DrcQaWidthTypeGeom / DrcPatternGeomGen | DRC **pattern 几何生成** | 正交（pattern 几何非 option 通用展开）|
| DrcDeckCmpGen | deck **对比** | 正交 |
| DRCPatPlan / DRQAPlan2Skill | QA pattern **规划** | 正交 |
| DRCPatGenAudit | pattern gen **审计** | 正交 |

→ MetalOptRuleExpand-001 是 kenwang 首条「metal-option rule 通用展开」主题，非 near-dup。

## 复用价值

- `parse_opt_map` 区间语法 + `build_opt_map_from_vars` 自动推导 = 通用「编号→后缀映射」模式，适合所有
  metal/layer-option 驱动的 DRC deck 生成 trace
- `#loop` + `$<var>` 模板展开 + skip-gap = 通用「模板引擎通用化」合成模板
- 双输入模式（显式 map / vars 自动推导）= 防 hardcode 的交叉输入 guard 设计范本
