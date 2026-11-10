# Deepread: nj8q4 — Netlist Static Check (R1-R4)

- **session**: `1794220525700_nj8q4.messages.json`
- **user/host**: tongni @ hfeg0pkn004
- **match_count**: 150 (85 user)
- **domain**: spice_sim (shard B)
- **status**: case → `EDA-Eval-DesignFlow-NetlistStaticCheck-001`
- **layer**: L1 (纯 Python 静态分析，无仿真器/EDA 沙盒 subprocess)

## 真实任务

tongni 在一颗 CXMT 混合信号设计网表上做 R1-R4 静态规则检查：
- **R1** 顶层设计单元电压域枚举
- **R2** 跨电压域直驱风险（低域逻辑直接驱动高域逻辑 / 反向，中间无 level-shifter）
- **R3** stdcell 输出扇出 >4 告警
- **R4** spare 逻辑单元充足性（每类型 spare ≥ 设计用量 40%）

agent 用 editor 反复写三个独立脚本 + 一个统一 runner：
- `r1r2_report.py` (475 行) — R1 顶层单元域 + R2 跨域直驱（层级、scope-aware、pin-方向敏感、switch_close union-find、level-shifter 豁免）
- `r3_fanout_report.py` (178 行) — R3 扇出，阈值 >4，stdcell 末信号 net = output Y 约定
- `r4_spare_report.py` (212 行) — R4 spare 充足性 ≥40%/type，`n_spare = spare/inst × n_spare_instances`，domain rollup，`R4_EXCLUDE_CELLS={'ag_lvlshftvcc2vdd1gut'}`
- `run_netlist_checks.py` (2.2KB) — 统一 CLI runner（importlib 加载三模块）

## 真实网表报告（gold）

- R1 = 8 顶层单元含电压域
- R2 = net027 跨域双向直驱：invLx8(@2563, VCC) ↔ invMx2(@2570, MEDIUM)，双向均检出
- R3 = 无违规（2 stdcell / 29 top inst）
- R4 = 17 条 SHORT（VDD1 域 40/442 vs req≥176 等）

## stdcell 约定（从脚本提取）

- 命名正则 `^([a-z]+?)(\d*)([lstfvywbnm]?)x(\d+)$` → 后缀域 {l/t/f/s:VCC, v:VDD1, y/w:VWLP, b/n:NEG, m:MEDIUM}
- 电源 net 正则 `vcc!|vdd1!|vwlp!|vss!|vdrv!|vneg!|inh_vss|inh_vcc|inh_vdd1|inh_vbn|inh_vbp`
- pin 序 `<inputs...> <Y> <inh_vbn> <inh_vbp> <rail> <inh_vss>`
- level-shifter 检测：name 含 `lvlshft`/`level`/`shft`/`vcc2vdd1`/`vdd12v`

## Case 设计（B-synthesized L1）

真实网表在 `/proj/dscqa/...` 下，e0031982 无读取权限 → 按 tongni 脚本记录的结构合成代表性 netlist：

- **asset A** `sample.netlist`：6 AG_* 顶层单元跨 VCC/VDD1/VWLP，顶层 stdcell 链含跨域 net027/net002 双向，AG_VtScrSpare ×2，扇出≤4，R4=11 SHORT
- **hidden B1** `hidden_b1.netlist`：8 AG_* 单元，跨域 cd_net1/cd_n2，扇出违规 fan_net0(Load#=5)，AG_SparePool ×3，R4=9 SHORT（VWLP SHORT）
- **hidden B2** `hidden_b2.netlist`：4 AG_* 单元，无 VWLP，跨域 xd_net9，AG_SpareBank ×1，R4=8 SHORT（VCC+VDD1 SHORT，无 VWLP）→ anti-hardcode 与 B1/A 互异

**gold standard** = 三真实脚本的检查逻辑，合并成自包含 `netlist_static_check_ref.py`（无 importlib，stdlib only）。

## 判分

`check.py` 15 条断言：① zip 含 netlist_static_check.py ② py_compile ③ B1 exit0+报告 ④ R1 三域枚举 ⑤ R2 低→高 cd_net1 ⑥ R2 高→低 cd_n2 ⑦ R3 fan_net0 Load#=5 ⑧ R4 ALERTS(9) ⑨ R4 SHORT invLx8 ⑩ R4 SHORT [domain:VWLP] ⑪ anti-hardcode B2 R4=8≠9 ⑫ B2 xd_net9≠cd_net1 + 无VWLP ⑬ 跨输入 guard A R4=11≠9/8 + net027 ⑭ 3x 确定性 ⑮ negative_selftest 7 负样本全 FAIL。

负样本：3 naive（naive_empty/hardcoded_a/only_print→其实4个含no_r2）+ §4.9 三假（empty_shell/print_expected/ref_core_deleted）。

## 自验结果（local, 2026-11-10）

- reference 15/15 PASS
- 7 负样本全 FAIL（§4.9 三假在列）
- jsonl B 241→242，test 字段与 on-disk check.py sha256 字节同步
