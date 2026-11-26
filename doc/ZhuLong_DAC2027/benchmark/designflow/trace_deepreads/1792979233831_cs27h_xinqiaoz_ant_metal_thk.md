# trace_deepreads/1792979233831_cs27h_xinqiaoz_ant_metal_thk.md — r335 deepread

## meta
- session: `1792979233831_cs27h`（xinqiaoz @ hfeg0pkn005，mc=44，physical_verify/Calibre DRC PDK_QA）
- model: glm-5.3-flash，cwd `/home/xinqiaoz/PDK_QA/pdkQaSystem`
- status: completed（10-26 01:47 → 10-29 03:15），50 msgs（27 user / 23 assistant）
- title: antMetalThk bug fix
- 档位：**B-档 synthesized**（U#1 用户已指出根因症状 → A-档 DISQUALIFY per §A rule 2「凡用户已指出根因或给出修复方案的轮，一律不得用作 A 档任务说明」）

## 用户意图（逐字原文）
U#1（提出需求 + 指出根因症状）：
> antMetalThk 这个检查有几个 bug，请帮忙看一下，
> 1. 如果在 config.ini 中同时写了 drc 和 ant，那么在 AntMetalThk 的检查报告中，ant 的路径最终会变成 drc 的路径，ldr 和 edr 的路径没有问题。
> 2. 需要QA的ldrsheet选择为LDR_CMOS,LDR_ARRAY，但是QA会报出LDR_YDC sheet的内容。换句话说，就是 ldrSheet 这个 config 对 AntMetalThk 这个检查没有生效。
> 请先定位原因，最好能设计 case 自己复现。

U#2：好的，我们先 按上面的方案建 issue 目录复现并进入修复流程。修复方案我们后续再考虑。

## assistant 工具链 + 关键产物
1. `issue-handler` skill 启动 → read rules/index.md + docs/checkers/ant_metal_thk_check_detail.md → search AntMetalThk/ldrSheet
2. read `DRC/text/AntMetalThkCheck.py`(L1-140) + `DRC/DrcQa.py`(L500-900) → 定位 dispatch 分支
3. read `DrcQa.py`(L100-220, L560-717) + `common/designManual/LdrInfo.py`(L1-200) → 确认 LdrInfo 构造
4. read `DRC/report/DrcQaReport.py` → 确认报告两轮迭代落盘
5. search effectiveSheetNames/extractInfo → 确认 LdrInfo.extractInfoCsv L759 过滤逻辑
6. read `DRC/tests/antMetalThk/run_test.py` + test_env.py + list tests/shared/case_ant_dh → 评估复用数据
7. shell_generic_pdkqa 跑 head/grep 检查 case_ant_dh LDR CSV 内容
8. **产出：根因定位报告（prose）**，未执行复现（U#2 后才建 issue 目录复现）

## 根因（assistant 定位，精确到行号）

### Bug 1：config 同时写 drc 和 ant 时，报告中 ant 路径变成 drc 路径
- `DrcQa.py` L516 `supportFuncnames=[..., 'antMetalThk']` → antMetalThk 进 drcCheckItems
- L530 `antSupportQaItems=[..., 'antMetalThk']` → 同时进 antCheckItems
- L677 `allCheckItems={"drc="+str(drc): drcCheckItems, "ant_"+str(ant): antCheckItems}` → config 有 drc+ant 时主循环跑两轮
- L678-681 `deckType=deck[:3]; deck=deck[4:]` → 第1轮 deckType=drc/deck=drc路径，第2轮 deckType=ant/deck=ant路径
- L765-767 `check=AntMetalThkCheck(antPath=deck, ldrPath=ldr, edrPath=edr)` → **不区分 deckType，直接把当前轮 deck 当 antPath**
- `AntMetalThkCheck.py` L370 `consoleOutput += f"ant={self.antPath}\n"` → 报告 ant 行打印 antPath
- **后果**：drc 轮（第1轮）也执行 antMetalThk，antPath=<drc路径>，drcQa_*.report 的 antMetalThk 模块 ant= 显示 drc 路径；ant 轮（第2轮）antQa_*.report 路径其实是对的
- **语义**：antMetalThk 是 ANT 专用检查（校验 ANT deck <Metal>_THK 变量 vs LDR sidewall vs EDR），drc 轮的执行本不该发生

### Bug 2：ldrSheet 配置对 antMetalThk 不生效
- dispatch 对比：L711 DrcCountWithOptionCheck(...,ldrSheet=ldrSheet,...) 传了；L715 DrcValueCheck(...,ldrSheet=ldrSheet,...) 传了；**L765-767 AntMetalThkCheck(antPath=deck, ldrPath=ldr, edrPath=edr) 没传！**
- `AntMetalThkCheck.__init__(self, antPath, ldrPath, edrPath)` L63 **无 ldrSheet 参数**
- `check()` 里 `LdrInfo(self.ldrPath)` L94 没带 sheet → `LdrInfo.__init__(ldrPath, sheet="")` 的 effectiveSheetNames=[]
- `LdrInfo.extractInfoCsv()` L759 过滤条件 `if sheet and len(self.effectiveSheetNames)>0 and not sheet in self.effectiveSheetNames: continue`，列表空时不过滤 → 所有 sheet（含 LDR_YDC）全加载

## 修复方向（assistant 给出）
- Bug 1：drc 轮（deckType=="drc"）跳过 antMetalThk（dispatch 分支按 deckType 过滤，报告体现 notExecuted），或在构建 drcCheckItems 时剔除
- Bug 2：`AntMetalThkCheck.__init__` 增加 `ldrSheet: str=""` 参数并保存；`check()` 改 `LdrInfo(self.ldrPath, self.ldrSheet)`；dispatch L767 补传 `ldrSheet=ldrSheet`

## case 改造（B-档 synthesized L1 code-fix）
- 把「诊断 bug + 写复现 case」转成「实现正确的 antMetalThk 路径分离 + ldrSheet 传递逻辑」
- 可见 A：合成 buggy `pdkqa_dispatch.py`（含两个 bug）+ config_A.ini（drc+ant+ldrSheet=LDR_CMOS,LDR_ARRAY）+ LDR_A.csv（3 sheet：CMOS/ARRAY/YDC，YDC 放 M7 sidewall）
- 隐藏 B：B1（drc+ant，ldrSheet=LDR_LOGIC,LDR_IO，LDR 含 LOGIC/IO/RF/ANALOG 4 sheet）、B2（仅 drc 无 ant）、B3（仅 ant 无 drc，ldrSheet 不同）
- check.py 11 条件 a-k：zip/compile/dispatch 存在 + Bug1 drc 跳过 + Bug1 ant 路径正确 + Bug2 ldrSheet 过滤 + B2/B3 边界 + 非硬编码
- 3 negatives（empty_shell/print_expected/ref_core_deleted）+ hardcode_a，全 FAIL

## 金标准
trace 末尾用户接受 assistant 的根因报告 + 复现方案设计（U#2 进入复现流程）。本 case 金标准 = 修复后的 dispatch 逻辑（assistant 给出的修复方向，落成可运行代码）。
