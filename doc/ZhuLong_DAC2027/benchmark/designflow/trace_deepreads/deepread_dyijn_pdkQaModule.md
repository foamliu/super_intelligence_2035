# Deepread — dyijn (xinqiaoz@hfeg0pkn002, mc69, eda_other)

**session**: `1792108868745_dyijn.messages.json` (28 msgs, PDK QA Dummy 模块知识问答)
**选轮**: U#2 = "DUMMY/ 模块的代码结构是什么样的？和 DRC/ 模块有什么不同？" —— 纯目标，未给根因/未给修复 → A-eligible。
**未取轮**: U#0(读哪些文档)、U#11(dummy 类型)、U#15(括号内外)、U#20(QA 阶段)、U#22(三元素分离)、U#24(检查项汇总)、U#26(calibreDummy.rule 部分) —— 均可作延伸不取。

## 真实工具链
cline 用 `read_files` 读 `/home/xinqiaoz/PDK_QA/pdkQaSystem/` 下文件 + `list_allowed_files` 列 DUMMY/ 与 DRC/ 目录 + `search_codebase`。无 attachments；资产=cline 通过 read_files 读到的文件，全部从 in-session tool_results 完整恢复（`content=[{query:路径, result:" N | 行内容"}]`，去 ` N | ` 前缀）。

## 恢复的资产（A 原文）
- `DUMMY/DummyQa.py` (7.3KB, 完整) — 主入口：`DummyQaConfig(PdkQaConfig)` readConf 读 8 键 `dummyConfig/dummyType/dummySvrf/dummyLayerInfo/drc/fracture/gds/turbo`，`super().__init__(qaType="dummy")`；`supportFuncnames=['dummySyntaxCheck','layerDuplicatesCheck']`；if/elif dispatch；chip/frame 双区（dummyType 或 svrf basename 推断 deckTypes）。
- `DUMMY/text/DummySyntaxCheck.py` — `class DummySyntaxCheck(Checker)`, topic=`dummySyntaxCheck`, `check()` 调 `os.system("rules_syntax_checker ...")` (ext dep `rules_syntax_checker`)。
- `DUMMY/text/LayerDuplicatesCheck.py` — `class LayerDuplicatesCheck(Checker)`, topic=`layerDuplicatesCheck`, `check()` 纯文本正则无外部依赖。
- `DUMMY/__init__.py` (空 docstring)、`DUMMY/index.md`、`docs/architecture/dummy_directory_structure.md` (含「与 DRC/ 模块的对比」表：DrcQa.py / 17 checker / QaConfig / 无 chip-frame)。

## gold（A#10，对 U#2 的回答）
- DUMMY/ 目录树（__init__.py / DummyQa.py / index.md / text/{DummySyntaxCheck,LayerDuplicatesCheck}.py / tests/）
- DummyQaConfig 直接定义在主入口，readConf 8 配置键，qaType="dummy"
- supportFuncnames 注册 + 手写 if/elif dispatch（非反射），异常兜底 check.status="error"
- chip/frame 分发（dummyType 配置 / svrf basename 自动探测）
- 与 DRC 差异：主入口 DrcQa.py vs DummyQa.py；checker 数 17 vs 2；config 类 QaConfig vs DummyQaConfig；chip/frame 无 vs 有；解析器 common/deckInfo 有 vs 无

## 合成（A档 faithful）
- 交付 `analyze_pdkqa_module.py`（config 驱动，读 config.json{module_dir,sibling_summary,report_out}，ast 解析模块主入口+text/检查器，回显 sibling 摘要，算差异，写 JSON 14 键）
- A = 真实 DUMMY 模块（verbatim 恢复）+ sibling_summary.json(DRC: DrcQa.py/17/QaConfig/false) + config_a.json
- 隐藏 B = 合成 LVS 模块（LvsQa.py: LvsQaConfig 6 键/qaType="lvs"/supportFuncnames[lvsNetlistCheck,lvsLayoutCheck]/无 chip-frame；text/LvsNetlistCheck.py ext dep lvs_run；text/LvsLayoutCheck.py 无 ext dep）+ sibling_summary.json(ERC: ErcQa.py/5/ErcQaConfig/false) + config_b.json —— 与 A 在 readConf 键数/检查名/chip-frame/sibling 上全异，交叉守卫
- check.py 14 条件 a-n（zip 含 analyzer / py_compile / 3x 确定性 / 14 键 / module_name=LVS / main_entry=LvsQa.py / config_class+base / qa_type=lvs / readConf_keys 6 项顺序 / registered_checks 2 项 / chip_frame=False / checker_classes 2 项+ext dep / differences 三维且不含 chip_frame / 反硬编码无 A/B 特异字面量）
- 自验：REF 14/14 PASS；3 negs[naive_noop→c, print_expected→n, core_deleted→f] FAIL distinct；§4.9 三假全 FAIL；NEG_RC=0；k=14 闸门 PASS

## 复用结论
A档 faithful，eda_other，L1-static+subprocess。资产全部从 in-session tool_results 恢复（无需 scp，xinqiaoz 家目录权限不影响）。与 r229 PrimeLibFlowAnalyze（同用户 xinqiaoz，PrimeLib K 库流程）域不同（Dummy QA 模块 vs PrimeLib 流程），非 DUP。
