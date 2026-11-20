# trace_deepread: 1792415342141_bzxqd (DummyConfigCheck)

- **user/host**: xinqiaoz / hfeg0plg76 (mc=308, keywords calibre:288)
- **msgs**: 196 (user 113 / assistant 94); tools: editor×67, run_approved_command×16, read_files×11, search_codebase×2, list_allowed_files×2
- **edited files**: `DUMMY/text/DummyConfigCheck.py` (23 edits), `DUMMY/tests/dummyConfigCheck/run_test.py` (10 edits), SHELL_CMD_AGENT.txt (9), PYTHON_CMD_AGENT.txt (6)
- **real task**: PDK QA Dummy 模块第 4 个文本检查器 `DummyConfigCheck`（注册名 `dummyConfigCheck`），对 TVF 源文件 `calibreDummy.rule` 做静态检查，1 个 checker / 4 个子检查（gdsType / suffix / script_DEBUG / OUTGDS_HIER）。

## 关键用户意图轮（A-档 seed 候选）
- **U0** (context handoff 笔记): 命名/粒度/4 子检查已锁定。
- **U5** (核心方法决策，逐字): "我有一个想法，就是我们可以考虑直接调用 tcl 指令，source 文件之后，puts 这 4 个变量，这样不管它们在文件里面怎么写，我都可以知道它们的最终值，甚至不用自己去匹配。我觉得这个方法是最安全的。" —— **tclsh source + puts 取最终值**，规避正则文本匹配在注释/重复 set/if-else/缩进下的误判。这是本案的核心失败模式。
- **U6** (逐字): "1. 只看最终 4 个变量的值，不看写法 2. init.tcl 不执行 3. 完全替换现有的逻辑，整体重写代码"
- **U8** (逐字, gdsType 一致性决策): "我认为无需管 gdsType 的 config 值是什么？也无需管它在 dummy.rule 文件中的值是什么。只要它们一致就行了。其他的我都认可。"
- **U12** (逐字, 报告格式): "************************dummyConfigCheck***************************** / dummyType = xxx, / directory = xxx, / dummyConfig = xxx / [info] gdsType = frame / [error] suffix = _rev02 / [error] script_DEBUG = True / [error] OUTGDS_HIER = <UNSET> / 直接不要写理由。"

## 4 子检查规则（从代码 + 用户拍板还原）
1. **gdsType**: rule 最终值 == config 期望值 → pass（一致性，U8）；rule 里重复 `set GDS_TYPE` → 后写覆盖；注释行 `#set GDS_TYPE overlay` 不计。
2. **suffix**: rule 最终值 == config 期望值 → pass；B 里 `if {0}{set suffix _wrong}else{set suffix _rev02}` → tclsh 求值=_rev02。
3. **script_DEBUG**: rule 最终值 == "False" → pass；注释 `#set script_DEBUG "True"` 忽略，活动 `set script_DEBUG "False"` 生效。
4. **OUTGDS_HIER**: rule 最终值 == "False" → pass；若从未 set → `<UNSET>` → fail。

## gold 磁盘产物
- `DUMMY/text/DummyConfigCheck.py`（23 次编辑）：tclsh source + puts 4 变量 + 4 子检查 + 固定格式报告（[info]/[error]，无理由）。
- `DUMMY/tests/dummyConfigCheck/run_test.py`（10 次编辑）。

## 失败模式 / 教学点
- **正则文本匹配的陷阱**：注释行、重复 set、if/else 分支、缩进都会让正则误判最终值 → 必须真跑 tclsh source 取最终值。
- **gdsType 一致性 vs 绝对值**：用户决策为一致性（rule==config），不强制 chip/frame 绝对值。
- **unset 检测**：TCL 未 set 的变量 `puts $VAR` 会抛错 → catch → `<UNSET>`。
- **报告格式极简**：[info]/[error] 两态，无理由文本，固定表头 + 3 上下文行 + 4 变量行。

## A-档可行性
- A-档不可行：gold 依赖 live PDK_QA 代码库（/home/xinqiaoz/PDK_QA 内网）+ live calibre 环境，沙盒不可达；且 gold 是多文件协同（DummyConfigCheck.py + run_test.py + 注册到 checker 体系）。
- → B-档 synthesized L1-boundary：单文件 `dummy_config_check.py`，tclsh source 取 4 变量最终值，行为场景嵌入 check.py。

## 选料注
- 本轮 (r129) 候选池 mc≥30 shard-C 过滤后 807 可用。先选 wiait (mc=321) 但发现与已有 DrcLegacyFallback-001 (i4c8d) 重复（同一 xinqiaoz DRC pattern legacy-fallback 主题）→ parked。再扫 bzxqd/8lf0t/pet0x：8lf0t 是 deepseek vs glm5.3 agent 评测（meta，非 physical_verify 代码）；pet0x 又是 DrcPatternCheck goodExisting 改动（与 DrcLegacyFallback 同主题）；bzxqd = DummyConfigCheck（TVF rule 4 变量 tclsh-source 验证）= 全新子主题，与已有 DummyDeck-001 / DummyGeoVerify-001（geometry）正交，当选。
