# trace_deepread — i1k7x (e0048306 @ hfeg0plg88, mc=475)

**session_file**: `1795682713385_i1k7x.messages.json`
**user/host**: e0048306 / hfeg0plg88  **agent**: lead  **nMsg**: 468 (242 user / 226 assistant)
**keywords**: spectre:861 virtuoso:1195 analog:561 schematic:310 cellview:267 dbopencellviewbytype:218 netlist:159 cadence:111
**domain**: characterization (schematic 实例枚举, 走 spectre/virtuoso skill bridge)

## 用户意图弧
1. 起步：让 cline 用其软链的 virtuoso skill 执行 `getVersion()` —— 环境连通性试探。
2. virtuoso bridge 连不上 (RAMIC Bridge python3.7 encodings module 缺失 / daemon exit state=134)。
3. 转向借 EDA Bridge 的 run_code 跑 SKILL；用户提出**建立稳定工作流约定**管理 5 个软链 skill（search/netlist/virtuoso/spectre/optimizer）+ run_code 执行 SKILL，固化成规则文件。
4. **核心 produce-task (USER #16)**：「走 workflow，帮我写一个 SKILL 脚本，读取库 `lacaa_adc` 下 `ADC_SAR_CDAC` 的 schematic 视图里的所有器件实例，把每个实例的名称、来源单元格、来源库打出来，并且可以 GUI 呈现。然后入库。」
5. 用户反复要求规范化「先 search → 再 run_code」，并要求 GUI 表格化 + hierarchy down 到底层。

## assistant 工具链
- `search_apis` / `get_api_details` 查 `dbOpenCellViewByType` 签名
- `run_code` (SKILL host=virtuoso) 探测库可达性：`ddGetObj("lacaa_adc")` → 找到；`dbOpenCellViewByType("lacaa_adc" "ADC_SAR_CDAC" "schematic" "" "r")` → 打开成功，`cv~>instances` 共 **70 个实例**
- 探测 HI 表单函数：`fboundp 'hiCreateStringField` 等均存在；`hiGetCurrentWindow()` → `window:5`（有窗口，但 `hiIsEnvironmentRunning`/`hiGetWindowType` 未定义，精简运行时）
- 实测 GUI：`hiCreateStringField(?name 'cdinst_txt ?prompt "Instances" ?defValue text)` + `hiCreateAppForm` + `hiDisplayForm ?dontBlock t` → `display returned = t ; visible = t`
- 最终交付 `~/scripts/skill_lib/cd_inst_report.il`，含 `cdInstGather`/`cdInstReport`/`cdInstReportGUI`/`cdInstSelfTest`，并登记 `INDEX.md`

## 关键发现 / gotcha
- 运行时精简：`hiIsEnvironmentRunning`/`hiGetWindowType` 未定义，但 `hiCreateStringField/hiCreateAppForm/hiDisplayForm` 可用；`hiGetCurrentWindow` 返回 window:5
- `hiCreateStringField` 必须**关键字参数**（`?name/?prompt/?defValue`），位置参数报 "extra arguments or keyword missing"
- `hiDisplayForm` 真实 gotcha：返回不可预测、不 dismiss 不返回 → 用 `?dontBlock t`
- 同一定义块里定义 GUI 函数后再跑顶层调用会出现"silent empty print_log"异常（GUI 函数定义似影响后续顶层执行），需分离 GUI 与文本自测
- `mapcar car rows` 报 "unbound variable - car"（SKILL 里需用函数对象，`'car` 显式引用）
- 数据：`lacaa_adc/ADC_SAR_CDAC/schematic` 70 实例 = analogLib.cap(C0..C36 bus) + analogLib.res(R0,R1) + basic.io/in/out 引脚 + lacaa_adc.ADC_SAR_CDAC_SW 子电路

## 可移植性判定
- 原始 deliverable 是 SKILL 脚本，依赖 Virtuoso + 用户私有库 `lacaa_adc/ADC_SAR_CDAC`（SUT 沙箱无此库）→ **不可直接移植**
- **可移植抽象**：schematic 实例枚举的等价物 = 解析 CDL 网表的 `.subckt` body 实例行（X/M/C/R/L），产出 name/type/master/n_pins 报告。纯 Python，无 Virtuoso/PDK 依赖，judge 解析 instances.tsv/summary.txt 结构与内容。
- case: `EDA-Eval-DesignFlow-CdlInstReportGen-001`，A=inv_a (4 ports, 2 mos) / B=nand3_top (6 ports, 6 mos + 1 X subckt + 1 C cap = 8 inst)。L1 judge-run, LIVE-NA, 15 断言 + §4.9 trio。

## 产物
- `benchmarks/EDA-Eval-DesignFlow/cases/B/EDA-Eval-DesignFlow-CdlInstReportGen-001.json`
- `assets/<CID>/`: cell_A.cdl, task_brief.md, hidden/{cell_B.cdl, hidden_manifest.json}
- `reference/<CID>/`: check.py (15 断言), solve.py (ref inst_report.py), negative/{solve_empty,solve_print_gold,solve_no_parse,negative_selftest}.py
- 验证：ref 15/15 PASS, neg_selftest trio distinct FAIL, judge-sim (symlink 树) 15/15 PASS, run_one.sh SKIP_RUN=1 结构接受
