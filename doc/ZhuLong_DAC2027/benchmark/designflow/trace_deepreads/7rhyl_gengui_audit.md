# 7rhyl — junlingw finesim GENGUI codebase audit (DEBT deepread, r1012)

**trace**: 1795137528730_7rhyl.messages.json · junlingw · hfeg0pkn005 · mc216 · spice_sim
**size**: 2.7MB, 833 msgs, 372 tool_use · **claimed r1012, synthesis deferred (DEBT)**

## 用户意图（原话）
- U1: `/proj/drvqa/V0/workdir/junlingw/GENGUI/ 这是GENGUI的路径，你看看学一下`
- U2: 我看不懂英文，你用中文输出和思考，然后继续
- U3: 修复后的finesim_gui.py和现在的finesim_tb_generator.py还有finesim_tb_gui.py有什么区别
- U4: 哪些文件是和finesim_tb_generator.py相关的，哪些不相关
- U7: 语法坏的那个文件他是想实现什么样的功能？能修吗
- U8: 再检查一遍哪些文件有用哪些文件没用，有用的文件有没有问题

**真实意图**: 研究 finesim testbench generator GENGUI 代码库 → 识别哪些文件与 finesim_tb_generator.py 相关 → 找出语法错误文件并修复 → 审计哪些文件有用/没用、有用的有没有问题。Phase 1 = 代码库审计 (msgs 0-~115); Phase 2 = GUI tab 改造 (msgs ~116-833, 合并 Analysis+Output tab, 加 _tout 方法) — **case 取 Phase 1**。

## GENGUI 代码库结构（从 trace tool_result 提取，23 .py 文件）
| file | lines | compile | local imports |
|---|---|---|---|
| fgrammar.py | 276 | OK | — (定义 G.PROCESSES=16, G.OPTGROUPS=7) |
| fengine.py | 139 | OK | — (TBGenerator.generate() → 13 lines, ends .end) |
| finesim_tb_generator.py | 706 | OK | fengine, fgrammar (class App, __main__, methods _topt/_preview_waveform/_apply_process/_opt_preset) |
| finesim_gui.py | 69 | OK | fengine, fgrammar |
| check_all.py | 29 | OK | fgrammar |
| finesim_grammar.py | 20 | OK | — (orphan) |
| finesim_engine.py | 131 | OK | — (orphan) |
| builder_p1.py | 65 | OK | — |
| builder_p2.py | 56 | OK | — |
| builder_p3.py | 94 | OK | — |
| gen_pin_from_net.py | 233 | **FAIL:40** | — (unclosed triple-quote docstring) |
| gen_spice_tb.py | 299 | OK | — |
| gen_spice_tb_v2.py | 273 | OK | — |
| gen_tb.py | 82 | OK | — |
| gengui.py | 87 | OK | — (OUT=finesim_gui.py) |
| build_gui.py | 126 | OK | — (TARGET=finesim_gui.py) |
| assemble_gui.py | 28 | OK | — (TARGET=finesim_tb_gui.py) |
| build_tb_gui.py | 33 | OK | — |
| write_tb_gui.py | 39 | OK | — (TARGET=finesim_tb_generator.py) |
| check_syntax.py | 10 | OK | — |
| explore_g5_models.py | 59 | OK | — |
| fix_indent.py | 35 | OK | — |
| test_preview.py | 122 | OK | — |
| non-py: G5_testbench.sp (1767B), spice_testbench.sp (9598B) |

**依赖图**: 仅 3 文件有本地 import — check_all→[fgrammar], finesim_gui→[fengine,fgrammar], finesim_tb_generator→[fengine,fgrammar]。fgrammar 被 3 文件 import, fengine 被 2 文件 import, finesim_grammar/finesim_engine 被 0 文件 import (orphans)。20/23 文件是 orphan (不被任何 sibling import)。

## gen_pin_from_net.py 语法错误
line 40: triple-quote docstring `"""` 未闭合 — docstring 内容（Script/Purpose/Usage/Modes/Direction）后直接接 `def get_net_name_str(net_or_fig):`，缺少闭合 `"""`。agent fix (msg 67 `_pin_fixed.py`): 在 `Direction: All pins are created as "inputOutput" by default.` 后补 `"""` 闭合。

## agent 交付的 3 个审计脚本（从 trace editor calls 提取）
1. **_scan_imports.py** (msg 34, 1376 chars): regex `^\s*(?:import|from)\s+([\w.]+)` 扫所有 .py 的 import 语句 → 本地模块依赖图 + 反向依赖 (who imports target)
2. **_verify.py** (msg 50, 1926 chars): py_compile 全部 .py (doraise=True) → OK/FAIL + 功能测试 (import fgrammar/fengine, TBGenerator.generate()) + artifact 检查 + GUI entry 检查
3. **_audit.py** (msg 79, 3497 chars): 综合 — A) fgrammar/fengine import+generate, B) finesim_tb_generator App methods, C) builders/checkers target path, D) orphans (imported by no sibling)

## case 合成计划（r1013 ETA）
- **form**: `audit_codebase.py <dir> [--report <path>]` — 参数化 Python 代码库审计工具 (produce, L1, 纯 Python 无 EDA 二进制)
- **功能**: ① 扫目录 .py 文件列表 ② regex 提取 import/from → 本地模块依赖图 ③ py_compile 每个文件 → OK/FAIL+error line ④ 反向依赖 (who imports each module) ⑤ 分类 useful (被≥1 sibling import) vs orphan ⑥ 输出 JSON report {files, dependencies, syntax, orphans, useful, reverse_deps}
- **A**: 从 trace 重建 GENGUI 结构 ~12 .py 文件 (fgrammar/fengine/finesim_tb_generator/finesim_gui/check_all/builder_p1/gen_pin_from_net[语法错]/+几 orphan)，忠实 line counts + import 结构
- **hidden B**: 不同合成代码库 ~12 .py (不同文件名/不同 import 结构/不同语法错误位置)
- **check.py 12 条**: ①zip+py_compile+size ②跑B exit0+valid JSON ③file list 全 ④import edges 正确 ⑤语法错文件 flagged FAIL+line ⑥OK 文件 flagged OK ⑦orphan 分类正确 ⑧useful 分类正确 ⑨reverse_deps 正确 ⑩anti-hardcode-A markers 无 ⑪3-seed determinism ⑫report 结构完整 (files/deps/syntax/orphans/useful/reverse_deps 全有)
- **核心齿**: ⑤语法错必须检出 (反 naive all-OK) + ⑦orphan 必须正确 (反 naive all-useful) + ④import edges 精确 (反 naive 无边)
- **3 negs**: empty (size0), print_only (打固定 JSON 不跑), core_removed (删 py_compile 逻辑)
- **blocker**: GENGUI 实际文件 permission-denied (e0031982 ≠ junlingw) → A 需从 trace tool_result 重建（trace 含各文件 read_files 结果，可提取内容）；或合成忠实结构（line counts + import 关系已知，内容可仿造）

## distinct vs 现存 case
- vs r1006 SpLibIncTokenRewrite (.lib token + .inc spf 替换): 完全不同 — 本 case = 代码库审计 (import 依赖+语法检查+orphan 分类)
- vs r983 SpDeckModelStripMigrate: 不同
- vs 任何现存 B case: 无代码库审计类 case, distinct ✓
