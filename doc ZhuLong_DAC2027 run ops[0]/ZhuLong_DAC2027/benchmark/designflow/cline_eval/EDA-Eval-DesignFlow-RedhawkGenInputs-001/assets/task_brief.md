# EDA-Eval-DesignFlow-RedhawkGenInputs-001 — RedHawk IR-drop flow scripts

## 交付接口（仅此 3 行说明接口，不写"怎么做"）
交付 `outputs/submit.zip`，解压后须含目录树 `pp/redhawk/`，内含 4 个文件：
`gen_inputs.py`、`Makefile`、`redhawk.tcl`、`probe.tcl`。判分器会把你的
`gen_inputs.py` 拷到独立临时目录，用**隐藏的 B 工程**的 DEF/上下文（通过
`RH_*` 环境变量）运行它，校验产出的 `*.gsr`（RedHawk Grid Setup Resource）
与 `*.ploc`（理想电源点）是否对 B 正确——因此 `gen_inputs.py` **必须从
`RH_*` 环境变量读取所有工程参数**（TOP/DEF/POWER_NET/GROUND_NET/VDD_NOMINAL
/FREQ/TOGGLE_RATE/SPEF/FSDB/TECH_FILE/SIM_INSTANCE/GSR/PLOC 等），不得硬编码。

## gen_inputs.py 行为规格（来自真实 trace，RedHawk classic GSR/PLOC 生成器）
`gen_inputs.py` 渲染 RedHawk（classic）两份输入：
1. **PLOC**：解析 DEF `SPECIALNETS` 段，定位 `RH_POWER_NET` / `RH_GROUND_NET`
   两条 power ring 的坐标，在每条 ring 的 bbox 边界上选理想电压源点，
   输出 `<net> <x_um> <y_um>`（坐标除以 `DATABASE MICRONS` 转微米）。
2. **GSR**：按 RedHawk GSR 关键字输出 `TECH_FILE / LEF_FILES / DEF_FILES /
   LIB_FILES / CELL_RC_FILE(SPEF) / PAD_FILES / VDD_NETS(含名义电压) /
   GND_NETS / FREQ / TOGGLE_RATE`，动态模式下再追加 `VCD_FILE` 块
   （`FILE_TYPE FSDB` + `FRONT_PATH` = `RH_SIM_INSTANCE`）。

可见的 A 工程上下文见 `ctx_A.txt`、DEF 见 `def_A.def`（仅作开发参考；
判分只用隐藏 B）。`RH_RUN_DYNAMIC=1` 时 GSR 须含 `VCD_FILE` 块且校验
`RH_SPEF`/`RH_FSDB` 文件存在（不存在则非零退出）。
