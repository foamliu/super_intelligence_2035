# trace_deepread — sid 1793070839598_nud8i (DummyQa CLI no-config + single check item)

- **user/host**: xinqiaoz / hfeg0pkn004 (10.129.2.13), mc=389, domain physical_verify (PDK QA / dummy deck checks)
- **session**: 1793070839598_nud8i.messages.json (1.22MB, 217 msgs, 11 real user turns), cwd `/home/xinqiaoz/PDK_QA/pdkQaSystem`
- **model**: glm-5.3-flash (xqzhou-glm)

## UI 轮次（逐字要点）
- **UI#0** (idx 0, verbatim): `我们当前的 DummyQa.py 可以不通过 -c config.ini，并且只检查某个特定的检查项吗？` — 纯需求 A-档 seed（只问可行性，未给根因/修复）。
- UI#1 (idx 32): 想让不带 -c 成为正式用法，`DummyQa.py -dummySvrf xxx.rule -ci dummySyntax` 直传参数跑单项/全部。请给方案。
- UI#2 (idx 44): 三元组缺省策略选 A（占位+warning）；顺带修单项报告名后缀。
- UI#3 (idx 45): `我已经自己实现了你的方案，你只要验证、测试与配套就行了。` — **用户自实现**，agent 职责=验证/测试/文档。
- UI#4 (idx 131): 不应修改 DUMMY 目录外的文件，即使有 bug，请回退。
- UI#5 (idx 132): 文档不用回退，代码修改不许动 DUMMY 以外。
- UI#6 (idx 165): 你刚才修复了哪些 bug？主要动了哪几个文件？
- UI#7 (idx 167): 这几个 bug 你都是怎么修复的？
- UI#8 (idx 169): 把因本次修改 bug 而改动的代码里的注释去掉，先整理再删。
- UI#9 (idx 173): 好的，请删除这些注释。
- UI#10 (idx 194): 现在请提交 DUMMY 目录的所有代码变更。
- UI#11 (idx 215): 继续。

## 真实迭代
1. agent 读 DummyQa.py / PdkQaMain.py / rules → 定位 `os.path.abspath(config)` 在 config=None 时崩溃；`onlyOneCheckItem` 机制已存在但报告名后缀依赖 PdkQaMain 模块全局。
2. 给方案（自包含 DummyQaConfig，仿 DrcQaConfig；CLI override config；三元组 NA 占位；单项报告名后缀）。
3. 用户自实现后 agent 验证：T1 纯 CLI 单项 / T2 纯 CLI 无输入全跑 / T3 混合 override / T4 回归 config / T5 dummyConfigCheck 无 version。发现并修 bug（configPath 置空避免 phantom path；svrfDependentChecks 丢弃逻辑；单项后缀从 PdkQaMain 移回 DummyQa.py）。
4. 用户约束：代码只许动 DUMMY → 回退 common/PdkQaMain.py，把报告名后缀逻辑移进 DUMMY/DummyQa.py。
5. 清理 agent 添加的 4 处 7 行注释；提交 DUMMY/ 7 文件（commit `feat: support CLI direct args for DummyQa and add DummyLayerInfo parser`）。

## 关键代码逻辑（忠实复刻源）
- **DummyQaConfig.__init__**：默认 process/product/version/dummyConfig/dummyType/dummySvrf/dummyLayerInfo 全 ""；若 configPath 存在则 configparser 读 [settings] 各键；CLI `valueOverWrite(current, high)`：high 非空则覆盖。
- **三元组 NA**：`if hasBlank(process,product,version): 逐个 blank 填 "NA"`（无显式 warning 代码，但设计意图是占位+warning，本 case 在 JSON warnings 里补 warning）。
- **workDir/reportPath 默认**：workDir blank → `<cwd>/dummyQA_<p>_<pr>_<v>_<user>`（**大写 QA**）；reportPath blank → `<cwd>/dummyQa_<p>_<pr>_<v>_<user>_<date>.report`（**小写 Qa**）。
- **deckTypes**：dummyType 非空 → `[t.strip() for t in dummyType.split(",")]`；否则从 `os.path.basename(dummySvrf).lower()` 自动探测：含 "chip" 加 chip，含 "frame" 加 frame，都没有默认 `["chip"]`。
- **checkItems**：supportFuncnames = [dummySyntaxCheck, layerDuplicatesCheck, **dummyMaskVsFracture**（无 Check 后缀）, dummyConfigCheck]；-ci 解析后按 supportFuncnames 顺序过滤；空且未指定 -ci → 全跑；空但指定了不支持的 → exit 1。
- **onlyOneCheckItem**：len(checkItemStrs)==1 时设该项。
- **svrfDependentChecks** = (dummySyntaxCheck, layerDuplicatesCheck)。
- **per-deck dispatch**：svrfPath 空/不存在 → deckCheckItems = [c for c in checkItems if c not in svrfDependentChecks]；全空则跳过 deck；否则保留非 svrf 依赖项 + warning。
- **deckReportPath** = reportPath（genDeckReportPath 原样返回）；onlyOneCheckItem 时 `deckReportPath = f"{deckReportPath}_{onlyOneCheckItem}"`。

## A-档判定
gold = 用户最终接受的 DummyQa.py + 6 个 DUMMY 文件改动（commit）。但依赖整套 PDK_QA 私有代码（PdkQaMain / DummySyntaxCheck / LayerDuplicatesCheck / DummyMaskVsFractureCheck / DummyConfigCheck / FileUtil）+ 真跑 calibre dummy 检查，沙盒不可复现 → **A-档 disqualified → B-档 synthesized**。真 L2（live PDK_QA + calibre）不可沙盒复现 → **L1-boundary**：把可验证的编排核心（CLI 直传 + config 合并 + deckTypes + 单项 + svrf 依赖丢弃 + 报告路径）合成成离线 `dummyqa_cli.py`（纯 Python3 标准库），输出确定性 run-plan JSON。

## 核心 difficulty（bug-prone 点）
1. CLI-over-config 合并优先级（valueOverWrite：CLI 非空才覆盖，否则保留 config 值）。
2. 三元组 NA 占位 + warning（无 config 无 CLI 时）。
3. deckTypes 自动探测（svrf 文件名含 chip/frame；都没有默认 chip）vs 显式 -dummyType 逗号拆分。
4. checkItems 顺序保持 supportFuncnames 序；`dummyMaskVsFracture` 无 Check 后缀（陷阱）。
5. svrf 依赖丢弃：svrf 空/不存在时**只丢** dummySyntaxCheck+layerDuplicatesCheck，保留 dummyMaskVsFracture+dummyConfigCheck；全空才跳 deck。
6. 报告路径小写 `dummyQa`（不是大写 QA）；单项追加 `_<检查项>` 后缀。
7. configSource = config|cli 区分。
