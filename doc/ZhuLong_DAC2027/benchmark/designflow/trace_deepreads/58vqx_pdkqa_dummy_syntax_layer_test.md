# 深读笔记 — 58vqx（physical_verify 域 · PDK QA Dummy 语法/层冲突测试）

## 元数据
- session: `1791790886127_58vqx.messages.json` · user `xinqiaoz` · host `hfeg0plg76`
- match_count 831（pdk:3140 / calibre:1456，11 类中 physical_verify 域）
- 472 msgs（251 user / 221 assistant）· 285 tool_use：editor 107 / read_files 61 / run_approved_command 46 / list_allowed_files 25 / run_commands 4 / search_codebase 2
- 真实场景：CXMT pdkQaSystem 项目 Dummy QA 模块测试。Windows AI 已实现两个检查器（DummySyntaxCheck / LayerDuplicatesCheck），Linux AI（cline）在 Linux 环境做测试与改进。

## 6 条 substantive user msg（5 阶段）
1. **[0]** 读 `.tmp/dummy_qa_linux_handoff_prompt.md` 了解背景。
2. **[24]** rules_syntax_checker 存在但需 ssh 到本地环境；给真实测试数据目录 `/home/pdk/peiyaoz/00_Dummy/deck/DYT4E_WHCFP_LHCRP_DHCFP/`（只读探索）；检查数据是否完整、能否支持后续开发测试。
3. **[51]** 测试当前两个检查器：test case 放 tests 目录（暂不与已有 DRC test 混）；要 good case + bad case 充分验证；可微调已有数据文件；执行 DummyQa.py 生成的 report 暂存；测试数据目录只读，修改须先复制出来。
4. **[357]** 不建议直接改 dummySyntaxCheck 源码，用完整路径；用 **monkey-patch** 理念在 test 脚本中修改。
5. **[421]** 报告文件不放 /tmp，改放项目 .tmp 目录。
6. **[443]** 写 HANDOFF 交接文档到 `.tmp/HANDOFF_<后缀>.md`。

## 项目结构（pdkQaSystem）
- `DUMMY/DummyQa.py` 主入口：DummyQaConfig 读 config.ini（dummyType/dummySvrf/dummyLayerInfo/...）；supportFuncnames=[dummySyntaxCheck, layerDuplicatesCheck]；按 deckType（chip/frame，可从 svrf 文件名自动探测）逐 deck 跑 checkItems，每 deck 生成独立 report（genDeckReportPath 把 `dummy` 前缀换成 deckType）。
- `DUMMY/text/DummySyntaxCheck.py`（继承 Checker）：SVRF 语法 + 开关组合爆炸检查。
- `DUMMY/text/LayerDuplicatesCheck.py`（继承 Checker）：LAYER MAP / LAYER 冲突检测。
- DRC 参考实现：`DRC/text/DrcSyntaxCheck.py`、`DRC/text/DrcLayerMapCheck.py`、`DRC/DrcQa.py`。
- 依赖 IMCP.file.FileUtil / IMCP.log.LoggerUtil / common.Checker / common.deckInfo.DrcInfo / common.PdkQaMain（非自包含）。

## 核心算法 1 — DummySyntaxCheck（开关组合爆炸）
- `getSwitch(lines)`：扫 `#DEFINE ` / `//#DEFINE `（去注释后）/ `#IFDEF` / `#IFNDEF` 行。
- `addSwitch(line, switchs)`：**`len(switchs.keys()) > 12` ⇒ 跳过该行**（上限保护，防组合爆炸）；3 列 ⇒ key+value，value 累积成 set；2 列 ⇒ key 配 `['ON','OFF']`（仅当 key 不存在时插入）。
- `genCombination()`：`itertools.product(*switchs.values())` 笛卡尔积；每组合：OFF ⇒ `//#DEFINE {key}`，ON ⇒ `#DEFINE {key}`，其他 value ⇒ `#DEFINE {key} {value}`；combineName = `"__".join(combineKeys)`（各 switch 的 value 依次拼接）。
- `genCombinationsSvrf()`：把组合的 #DEFINE 行 + 原始 rule 内容（#DEFINE 已被注释成 //#DEFINE）写入 workDir/{combineName}。
- `checkSvrf(svrfPath)`：`os.system(f"rules_syntax_checker {svrfPath} > /dev/null")` 返回 code==0 为通过。**真实外部 Calibre 工具**。
- `check()`：先查原文件（mainStatus）；**原文件失败 ⇒ 立即 return status=False（不生成组合）**；否则生成所有组合逐个 checkSvrf，统计 combinationCount/success/failed；failedCount==0 ⇒ status=True。

## 核心算法 2 — LayerDuplicatesCheck（6 类层冲突）
解析 `DrcInfo.instance(svrfPath)` 得 layerMaps（每项 `[layer, datatype, targetLayer, targetDatatype, (DATATYPE|TEXTTYPE)]`）+ layerStatements（`[name, layer, datatype?]`）。6 类冲突（appendToHashList 建 key→[value] 多值表，len>1 即冲突）：
1. `layerMap2_1`：同一 source `layer_datatype` → 多个 target。报告 `{tgtLayer}: LAYER MAP {srcLayer} DATATYPE {srcDt} {tgtLayer}`。
2. `layerMap1_2`：同一 target layer → 多个 source。报告 `{tgtLayer}: LAYER MAP {srcLayer} DATATYPE {srcDt} {tgtLayer}`。
3. `layerTextMap2_1`：同 source（TEXTTYPE）→ 多 target。
4. `layerTextMap1_2`：同 target（TEXTTYPE）→ 多 source。
5. `layerToName`：同 layer name → 多 layer number。报告 `{name}: LAYER  {layer}   {name}`（注：源码 valueSplits[1]=name, valueSplits[0]=layer）。
6. `nameToLayer`：同 layer number → 多 name。报告 `{name}: LAYER  {layer}   {name}`。
- exceptionCount>0 ⇒ status=False，报告头 `********************dummy layer duplicates check***************` + conflict list；否则 status=True，`there is no layer map conflict`。

## 真实测试数据（agent 写入 tests/data/）
- `good_layer.svrf`：4 个 LAYER MAP（88/570 × DT 0/16）+ 4 个 LAYER，无冲突。
- `bad_layer.svrf`：含 5 类冲突标注（layerMap2_1: 88_0→1001/1003；layerMap1_2: 1001←88_0/570_0；layerTextMap2_1: 88_1→1004/1005；nameToLayer: M1→1001/2001；layerToName: 1001→M1/N1）。
- `good_syntax.svrf`：layers + VARIABLE + DRC（注：DRC 语句形式 `DRC M1_01 M1 WIDTH < 0.1` 实测 rules_syntax_checker 报 INP7 incomplete，agent 数据 imperfect）。
- `bad_syntax.svrf`：含 INVALID_COMMAND / `WIDTH < < 0.1` / UNKNOWN_STATEMENT。
- `many_switches.svrf`：13 个 #DEFINE（SW01-SW13，SW06=VALUE_A/SW08=VALUE_B），测 >12 上限；agent 注释掉 SW03-SW13 防爆炸。
- `config.ini` / `config_bad.ini`：dummyType=chip，dummySvrf 指向 good/bad layer。

## rules_syntax_checker 实测（.75 sandbox，2026-10-31）
- 路径 `/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/rules_syntax_checker`，env `MGC_HOME`/`CALIBRE_HOME` 指向同目录，`MGC_VCO=aoi VCO=aoi`。
- 纯 LAYER MAP + LAYER 的合法 SVRF ⇒ exit 0（"Successful compilation"）。
- 含 `INVALID_COMMAND` ⇒ exit 1（"Error INP1 ... superfluous or invalid input object"）。
- 单次 ~200ms。**可作 L2 真跑工具**（candidate harness 经 subprocess 驱动，grader 在 .75 上复跑核对）。

## case 合成方向（EDA-Eval-DesignFlow-DummyQA-001，physical_verify 扩量#2，L2）
- 交付件：自包含 `dummy_qa_harness.py`（纯标准库 ASCII），复刻两检查器核心逻辑（不依赖 IMCP/common），syntax check 经 subprocess 真跑 `rules_syntax_checker`。
- asset A：真实 DummySyntaxCheck.py / LayerDuplicatesCheck.py 源码 + 真实 5 个 .svrf 测试数据 + task_brief（含 rules_syntax_checker 路径/env、monkey-patch 理念、只读数据规则）。
- hidden B：不同层号/不同开关（ON/OFF/value 混合、≤12 ⇒ 已知组合数）/ 部分冲突（仅 3/6 类）的 .svrf，规模/取值/结构与 A 不同。
- check()：subprocess 跑候选 harness 在 B 上，并**独立复跑 rules_syntax_checker**核对 verdict（L2 真跑）；≥11 条件 a-k；3 seed 随机化子集；3 naive 负样本（always-pass / syntax-only-no-combos / layer-counter-only）全 FAIL。
