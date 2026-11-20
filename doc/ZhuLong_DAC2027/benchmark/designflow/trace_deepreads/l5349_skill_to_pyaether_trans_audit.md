# 深读笔记 — l5349 (rongjiez @ hfeg0pkn005, mc=137, layout_aether)

- **session**: `1789629651143_l5349.messages.json`（935KB, 95 msgs: 57 user / 38 assistant）
- **用户**: rongjiez（NEW user，shard C 台账无历史）
- **真实工具**: 309 pyAether + 103 schematic + 85 netlist + 31 dbGet + 26 cellview + 22 hspice + 12 calibre（pyAether 为主，layout_aether 域）
- **match_count**: 137

## 用户意图（3 个真实需求轮，其余为 tool_result 回填）

- **U#1 (msg#0)**: 提供 `cxmt_getLatchFFCellList.il`（Virtuoso SKILL，获取电路中可能的 FF/Latch cell list，含 flatten 结构检测）+ `cxmt_getLatchFFCellList.py`（手工翻译的 pyAether 版）。反馈：pyAether 版结果与 SKILL 不一致，**有时直接抛 `'NoneType' object is not iterable`，输出文件为空**。明确要求「**先不要直接修改我的文件**」，即只要诊断、不要改文件。
- **U#2 (msg#14)**: 问「你知道怎么对 aether 的 pyaether 脚本进行 debug 吗」——调试方法咨询。
- **U#3 (msg#24)**: 问能否在 VSCode 下 debug pyAether（点 Aether 菜单触发脚本时自动停在 VSCode 断点），要求在当前目录配置好。

## assistant 产物

- **msg#13（核心诊断，4307 字）**: 静态对照 SKILL 与 pyAether 源码，定位 **5 个 bug**，给出每个 bug 的文件/行号、SKILL 语义、pyAether 实际行为、影响、修复方案，并给总结表：
  1. **Bug 1（critical, L88-104）对 None 迭代** —— `etMakeTable` 默认 `None`，子表 `["input"]/["output"]` 在实例只有输入或只有输出端子时保持 `None`；SKILL `foreach(nil)` 是 no-op，Python `for x in None` 抛 `TypeError: 'NoneType' object is not iterable`。崩溃发生在写文件之前 → 输出文件空。修复：`if inputNet1List:` 守卫或默认 `[]`。
  2. **Bug 2（critical, L78/L84）`list(string)` 拆字符** —— `list(instTermId.net.name)` 在 SKILL 造单元素列表，Python 把网名拆成单字符（`list("CK")`→`['C','K']`），后续 `ae.member` 网名比较永不到位 → 反馈环路检测失败 → flatLatch 为空。修复：`[instTermId.net.name]`。
  3. **Bug 3（critical, L63/L127）`dbOpenCV` 参数顺序错位** —— SKILL `dbOpenCellViewByType(lib cell view viewType mode)` 5 参；pyAether `ae.dbOpenCV(lib, cell, view="layout", mode="a", viewType="layout")` 第 4 位置参是 `mode`，`viewType` 默认 `"layout"`。移植成 `ae.dbOpenCV(lib, cell, "schematic", "r")` 实际用 `viewType="layout"` 打开 → 拿不到 schematic cellview → 无实例数据 → 结果空。修复：`ae.dbOpenCVByType(...)` 或显式传 `viewType="schematic"`。
  4. **Bug 4（medium, L35-36）`str.upper()` 结果被丢弃** —— `cellNameUC = str(cellName); cellNameUC.upper()` 是裸语句，`.upper()` 返回新串不赋值，`cellNameUC` 仍是原大小写 → 小写/混合大小写 latch cell 名漏匹配 `re.search(r"LAT", ...)`。修复：`cellNameUC = str(cellName).upper()`。
  5. **Bug 5（minor, L103/L105）`ae.member(x, None)` 未守卫** —— `ae.member(inputNet1, outputNet2List)` / `ae.member(outputNet1, inputNet2List)` 第二参可能为 None（同 Bug 1 原因），未加守卫。修复：`if outputNet2List and ae.member(...)`。
- **msg#23（4024 字）**: pyAether 调试方法介绍（`ae.etPrintf`/`ae.etPprint`、`ae.cmdIsPrint(True)`、`ae.etInstallDebugger()` 等）—— prose Q&A，非可运行交付。
- **msg#72 / msg#94**: VSCode debugpy attach 配置（`.vscode/launch.json`、`settings.json`、`debug_attach.py`、`README_DEBUG.md`，定位 Aether 自带 Python 3.9 路径并 `pip install debugpy`）—— env-config 交付，本轮**不取作 case**（取最可形式化的 Bug 1-5 静态诊断）。

## 选料判断

- **种子成立**：U#1 提供完整 SKILL + pyAether 源码 + 明确症状（NoneType 崩溃 + 空输出 + 结果不一致），assistant 产出**结构化 5-bug 静态诊断**（可形式化为审计脚本：读 manifest{skill_source, pyaether_source} → 静态对照 → 输出 diagnosis.json）。属 §4.2/§4.3 可 subprocess 执行的候选（对 pyaether_source 做 AST 静态分析），非 prose。
- **A 档禁用**：U#1 用户已给出修复方向（"NoneType"/"空输出"指明根因方向）→ 按顶部 A/B 档令 §①2 「凡用户已指出根因或给出修复方案的轮，一律不得用作 A 档任务说明」。故做 **B 档 synthesized**：prompt 用真实场景（rongjiez、SKILL/pyAether、NoneType 症状）但交付形态合成（审计脚本 + 结构化 JSON）。
- **域**: layout_aether（pyAether 脚本翻译/调试）。shard C 覆盖 55 → 56。
- **DISTINCT from 历史 case**: r230 VirtuosoStartupDiag（virtuoso 启动 4 层失败链 env 诊断）、r226 PcellPatternGeoDiag（pcell pattern 几何）、r222 SchOaInventoryExtract（OA inventory）、r218b DrcQaWidthTypeGeom（DRC QA width pattern 11-type 几何生成）—— 本案**首次 ground on SKILL→pyAether 语义翻译差异静态审计**（5 类典型陷阱：None 迭代 / list(string) 拆字符 / dbOpenCV 参数顺序 / str.upper() no-op / member(x,None) 未守卫），与历史 case 互补不重叠。

## 设计（B-synthesized, L1-boundary, k=14 a-n）

- **SUT** `skill_to_pyaether_audit.py`（CLI `<manifest.json> -o <diagnosis.json>`，stdlib only：ast+re+json+argparse）。读 manifest{pyaether_source, skill_source}，对 pyaether_source 做 AST 静态分析，5 个 detector 各扫一类陷阱；SKILL 源做轻量 regex 交叉印证（skill_idiom_present）。输出 `{bugs[], categories, summary{total_bugs, total_occurrences, by_category, by_severity, crash_symptoms, empty_result_causes}}`。
  - **Detector 1 none_iteration**: `for x in <var>` 其中 `<var>` 被赋值自 `table[key]["input"|"output"]` 下标（etMakeTable 默认 None），且外层无 `if <var>:` 守卫 → flag。
  - **Detector 2 list_string_charsplit**: `list(<expr>.name)`（list() 作用于 .name 字符串属性）→ flag。
  - **Detector 3 dbopenCV_argorder**: `ae.dbOpenCV(lib,cell,view,mode)` 4 位置参无 viewType kw → flag。
  - **Detector 4 str_upper_noop**: 裸语句 `<expr>.upper()`（Expr 节点，结果丢弃）→ flag。
  - **Detector 5 member_none_unguarded**: `ae.member(x, <var>)` 其中 `<var>` 是 None-able 表下标变量且外层无 `if <var>:` 守卫 → flag。
- **A_run** = trace grounded（真实 cxmt_getLatchFFCellList.il + .py，rongjiez/AICAD-16）。金标 5 类，counts {none_iteration:2, list_string_charsplit:2, dbopenCV_argorder:2, str_upper_noop:1, member_none_unguarded:2}，total_occurrences=9。注：trace 里 Bug 1 描述覆盖 4 个变量（inputNet1/2List + outputNet1/2List），但只有 inputNet1List/outputNet1List 被 `for` 迭代（2 次），另两个 inputNet2List/outputNet2List 进 `ae.member`（归 Bug 5）——审计按实际 AST 语义计 count=2（none_iteration）/ 2（member_none），更精确。
- **隐藏 B** = 合成不同 SKILL/pyAether 对（check_diff_drive），3 类 {none_iteration:1, dbopenCV_argorder:1, str_upper_noop:1}，total_bugs=3（与 A 的 5 类不同，杀「永远 5 类」硬编码）。
- **B2 干净守卫** = 正确翻译（dbOpenCVByType / `if inNets:` 守卫 / `[cvId.name]` / `str(x).upper()` 赋值 / `if inNets and ae.member(...)` 守卫）→ 0 bug，杀 always-detect。
- **B3 重载守卫** = 5 类但 none_iteration count=4（比 A 的 2 多）+ list_string_charsplit count=3 + ... total_occurrences=12，杀「永远 count=2/5」硬编码。
- **14 条 a-n**: (a)zip 合法+1 候选≥300B (b)py_compile+stdlib-only(禁 pyAether/numpy/calibre/skill/virtuoso/cadence/innovus/gdspy) (c)A JSON+3 顶层键{bugs,categories,summary} (d)A 退出 0+写文件 (e)A total_bugs==5 (f)A categories==金标 5 类按序 (g)A none_iteration count==2+critical+impact 含 NoneType/crash (h)A list_string_charsplit count==2+fix 含 `[`/single-element (i)A dbopenCV_argorder count==2+fix 含 dbOpenCVByType/viewType (j)A str_upper_noop count==1+medium (k)A member_none_unguarded count==2+fix 含 guard/None (l)隐藏 B total_bugs==3+categories==金标 B 3 类[反硬编码] (m)B2 干净守卫 0 bug+空 bugs/categories (n)B3 重载守卫 total_bugs==5+none_iteration count==4(≠A 的 2)+3-seed sha256 确定性。k_check=14=k_rationale≥8 ✓。

## 自验

- golden CHECK 14/14 PASS（A 5 类 counts 全对 / B 3 类 / B2 0 / B3 5 类 none_iter=4 / 3-seed STABLE）。
- 5 negative[empty_shell/print_expected/core_deleted/naive_hardcode_a/stub_no_audit] 全部 not-full-pass（ALL_NEG_FAIL=True，naive_hardcode_a 11/14 仅过 a/b/c/d/e/f/g/h/i/j/k 因 l/m/n 击穿硬编码）。
- §4.9 三假提交回归：empty_shell / print_expected / core_deleted 均 FAIL ✓。
- test 字段==disk check.py 字节同步；E2E jsonl test PASS。
