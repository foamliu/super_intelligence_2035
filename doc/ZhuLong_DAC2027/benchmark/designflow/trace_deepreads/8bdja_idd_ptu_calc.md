# Deepread: 8bdja — IDD PTU Power Budget Calculation (Aether UI)

- session: `1795241697250_8bdja` (chengk @ 10.129.8.224, mc=37, 49 msgs / 253KB)
- domain: analog_context (IDD leakage / PTU power budgeting for multi-die-stack DRAM)
- trace_source keywords: aether:229;netlist:56;pyaether:37;rtl:34

## 真实用户意图
chengk 是 CXMT 工艺/测试工程师，要把已有的 SKILL IDD PTU 计算工具（`cxmt_IDD_PTUCalculation.il`，原作者 Peipei Tang 2025-12-26，Empyrean Lijk 2026-05-14 转 python3）重做成一个**自包含、可 `ae.load()` 运行的 pyAether PyQt5 QMainWindow 脚本**，并让参数框（PTU_target / die_stack / Channel）可编辑（原版 editable=False）。

## agent 工具链
brainstorming 探索 → read_files 读 `cxmt_IDD_PTUCalculation.py` + `designer_test/Ui_MainWindow.py`+`PTU_cal_test2.py` → 呈现设计获批准 → editor 写 `IDD_PTU_Calculation.py` + `IDD_PTU_Calculation_spec.md` → run_approved_command `py_compile` 校验 → 用真实 config 验证计算公式（0.9203/13.0727%, 0.5114/7.2636%, 0.4474/6.3545%, -0.6746/-9.5818%）→ parse_config 验证（22 数据行 + Total = 23 行，默认 7.04/16/4）→ 清理临时脚本。

## 交付物（`/home/chengk/work/ZL_work/IDD_PTU/skill_test/`）
- `IDD_PTU_Calculation.py`（12680B，pyAether QMainWindow，入口 `cxmt_IDD_PTUCalculation_GUI`）
- `IDD_PTU_Calculation_spec.md`（设计规格）

## config 格式（`IDD_PTUconfigFile`，645B）
- `*` 前缀行 → key: value（PTU_title / PTU_target(W) / die_stack / Channel / Text）
- `#` 注释行
- 数据行 3 列：`IDD_name  idddata  DOU_Index`（DOU_Index 即 PTU_Index，可为负）
- A: PTU_target=7.04, die_stack=16, Channel=4, 22 行（IDD01..IDD62l）

## 计算内核（离线可判分）
- `PTU_gain(W) = PTU_Index * IDD(mA) * die_stack * Channel / 1000`
- `PTU_gain(100%) = PTU_gain(W) / PTU_target * 100`（PTU_target=0 → 0）
- Total 行：IDD(mA) / PTU_gain(W) / PTU_gain(100%) 各列对数据行求和
- 仅当 IDD(mA) 与 PTU_Index 均为有效数字才计入；空/非法跳过
- `_fmt`：整数去小数点；非整数 `%.4f` 去尾零

验证样例：IDD01 PTU_Index=14.38, IDD=1, die_stack=16, Channel=4 → 14.38*1*16*4/1000=0.92032≈0.9203；0.92032/7.04*100=13.0727% ✔

## case 设计（EDA-Eval-DesignFlow-IDDPTUPowerBudgetCalc-001）
- 抽离离线判分内核：给定 config + 每行 IDD(mA) 值，产出 JSON 报告（每行 PTU_gain(W)/PTU_gain(100%) + Total）
- A（SUT 可见）：chengk 真实 config_A + idd_values_A
- B（hidden）：不同结构（PTU_target=9.5, die_stack=8, Channel=2, 14 行，含正/负/零 PTU_Index）+ 不同 IDD 值
- check() 独立重算公式比对 + 3 随机子集一致性 + 退化提交 FAIL
- k_check ≥ 10
