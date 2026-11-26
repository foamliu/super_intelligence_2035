# r606 deepread — xxchen ebctc (WaiveParamMultiParse-001)

- **session**: `1794645596542_ebctc.messages.json` (hfeg0plg19, 1.10 MB, 265 msgs / 136 user / 129 assistant)
- **user**: xxchen (C 域已知 produce-task 用户：r545 PgRailLabelReplace / r587 AutoViaEncFix / r594 DeckRuleParseExtract 同作者群)
- **mc**: 318 · **domain**: physical_verify (DRC pattern QA tool 开发)
- **ledger 旧判**：`r573: xxchen known-reject user drc/.gds modify-existing` → **B 类误杀**（2026-11-15 令：modify-existing 现合法）。pool_reaudit_C.tsv r590 新判 **可造**。r606 revive: parked→claimed→case。

## 用户意图（trace 原话 thread）

UI#1「阅读 AGENTS.md / 阅读 PROJECT.md」→ agent 加载 DRC_pattern_tool 项目上下文。
UI#2 (idx23) **核心 produce-task**：
> ### QA pattern debug: PW_S_017_00_p
> QACELL  PW_S_017_00_p  prl_space  PWx  4.6  {lengthLower 492.188} {width 10.0} {waive bad 6,7}
> 当前 waive bad 参数不支持指定多个 pattern 列表，我希望用 `,` 隔开代表同时 waive 6 和 7。修改工具支持该特性。

UI#3 (idx131)：
> ### QA pattern debug: PW_S_016_00_p
> QACELL  PW_S_016_00_p  prl_space  PWx  3.0  {lengthLower 123.046} {lengthUpper 246.094} {width 10.0}  {waive bad 6,7 good 3}
> 当前还需要同时 waive 掉 good pattern 3, bad 和 good 的出现顺序可交换。修改工具支持该特性。

UI#4 (idx175)：
> ### 优化功能： waiveMark
> QACELL  PW_S_016_00_p  prl_space  PWx  3.0  {...}  {waive bad 6,7 good 3,5} {waive_shape good 6,7}
> 再新增加一种 waive 方式，waive_shape 对 good pattern 6,7 waiveMark 只覆盖在 layer1 和 layer2 的图形上，保持和 layer1 及 layer2 的 shape 图形一致。修改工具支持该特性。

## agent 工具链（124 assistant turns）

`run_approved_command`(47, profile=python-runner/shell-runner) + `read_files`(26) + `editor`(53, old_text/new_text) + `edit_code`(1)。

关键改动文件：
- `QA_Pattern_tool/script/config_parser.py` `_normalize_pattern_set`（idx37/41/184/247）——核心
- `QA_Pattern_tool/script/pattern_compare*.py`（idx186-196，waive_shape 渲染逻辑）
- `manual/script.md`（idx113/115/168/249）——文档同步
- `PROJECT.md` + `update_history.md`（idx121/123/170/253/255）——变更记录
- 临时验证脚本：`test_waive_comma.py` / `verify_pw017_waive*.py` / `verify_pw016_waive.py` / `verify_pw016_shape*.py` / `make_cfg_pw0*.py` / `grep_*.py`

## 核心算法（_normalize_pattern_set 字符串分支，idx37 NEW）

`_parse_braced_params` 先把 `{waive bad 6,7}` 按空格 tokenize 成 `["bad", "6,7"]`（"6,7" 是字符串，无法转数字）。旧 `_normalize_pattern_set` 把字符串一律当 type 关键字 → "6,7" 被误当 type → waive 集合为空（6、7 都没被 waive）。

**修复**（idx37 NEW）：字符串 item 若是「逗号分隔的 \d+ 串」（每段 `re.fullmatch(r"\d+", p)`）→ 视为当前 type 的 pattern 列表 → `result[current_type].update(nums)`；否则才当 type 关键字。
- 兼容带空格 `{waive bad 6, 7}` → tokenize `["bad","6,","7"]`，"6," 去空格并入、7 走同一分支 → `{6,7}`。
- 同一函数服务 `deletePattern`/`waivePattern`/`waive`（向后兼容超集）。

**waive_shape**（idx184 NEW）：在 normalize 调用处新增 `_normalize_pattern_set(options, "waive_shape", line_num)`，使 `{waive_shape good 6,7}` 成为一级 pattern-set 键。

**bad/good 顺序可交换**：循环逐 token 设 `current_type`，数字并入 `current_type` 集合 → `{waive bad 6,7 good 3}` 与 `{waive good 3 bad 6,7}` 同结果 `{"bad":{6,7},"good":{3}}`（单元测试已验证，idx130 文本确认「无需再改代码」）。

## 验证（agent 自验，trace 原文 idx130/166）

- `{waive bad 6,7}` → `{bad:{6,7}}` ✓
- `{waive bad 6, 7}` → `{bad:{6,7}}` ✓
- `{waive bad 3 6,7}` → `{bad:{3,6,7}}` ✓
- `{waive bad 6,7 good 3}` 端到端：good cell 1 个 waive 矩形（仅 pattern 3）/ bad cell 2 个矩形（pattern 6、7）✓
- waive_shape：waiveMark 只覆盖 layer1/layer2 shape ✓（verify_pw016_shape_match 跑通）

## B 档 mock-behavioral reframe（承 r593-r605 模式）

源代码在 xxchen 私有 workdir `/home/xxchen/workspace/DRC_pattern_tool/`（沙盒不可达）→ asset_fidelity=synth。把「扩展 QACELL config 解析器的 waive 参数语法」参数化为纯 Python3 `waive_param_parser.py <config.txt> <out_report.json>`（stdlib only）：
- 解析 QACELL 行 → 提取 cell/function + 4 个 pattern-set 键（waive/waive_shape/deletePattern/waivePattern）
- normalize 到 `{"bad":[sorted int], "good":[sorted int]}`，支持逗号列表 / 空格+逗号混合 / bad-good 任意顺序 / waive_shape 独立键
- 非 pattern-set 参数（lengthLower/width/layer2_device/auxRegion/enclose_side1/w/l）忽略
- 确定性 JSON 输出（sort_keys + indent=2）

输入 A（6 行，可见）+ 隐藏 B（9 行，cell/数字与 A 全异）+ 隐藏 B2（8 行，与 B 全异，反硬编）。

## check() 数据驱动

check.py 自带独立 oracle（`_truth` + `_norm`，与 ref 分开实现）解析 B/B2 算 ground truth，再断言 SUT 输出忠实反映 B/B2。15 条 a-o：结构 2(a:zip+b:py_compile) + B 运行 1(c) + B 结构 1(d) + B 语法 7(e-k: 逗号/混合空格逗号/顺序交换/waive_shape 与 waive 分离/waive_shape-only 不泄漏/deletePattern/waivePattern) + 反硬编 A 1(l) + B2 ground truth + 反硬编 B 1(m) + 确定性 1(n) + 鲁棒性 1(o)。

自验：ref 15/15 PASS ✓；3 neg(naive_empty/print_expected_A/deleted_core)全 FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓；§4.9 (a)(b)(c) 三假全 FAIL ✓。k=15≥8 ✓。
