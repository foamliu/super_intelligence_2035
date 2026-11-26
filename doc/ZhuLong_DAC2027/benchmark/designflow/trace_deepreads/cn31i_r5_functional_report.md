# Deepread: 1794791834453_cn31i — tongni@hfeg0pkn005 — R5 functional report generator

**session**: 1794791834453_cn31i  **user**: tongni  **host**: hfeg0pkn005 (10.129.2.14)  **mc**: 328  **model**: deepseek-v4-flash  **domain**: spice_sim
**msgs**: 399 / **size**: 1.6 MB / **tools**: list_allowed_files(7) run_approved_command(89) read_files(41) editor(58)
**scan**: 1118_230537 (fresh mc>=10, B-kw pool)

## Real task (用户真实意图)

sim-sp-gen skill 已为 AG_Vcc2scALDOAct（Vcc2sc ACT LDO 仿真原理图）生成 Tran/AC/DC/Monte Carlo 的 `.sp` 仿真文件。用户在 R5 功能检查这一步提出（trace 原话）：

- msg[73]：「Vcc2sc2Vcc / Vcc2scActDis / Vcc2scActEn 也要给出真值表，给出一些控制输出的真值表，并且一些信号可以默认其他信号固定 default 然后解释功能」
- msg[111]：「En Dis 2Vcc 这个写的不知道是什么意思，要给好信号名，把对应的输入信号的真值表要列出来」
- msg[385]：「/proj/dscqa/.../r5_report.txt 这个路径下没有报告」

即：从 netlist 推导顶层控制输出（LOGIC 输出）的输入→输出组合逻辑，给出**布尔等式 + 真值表**，信号名用真实名（非 En/Dis/2Vcc 缩写），模拟输出（opamp 驱动）标 ANALOG，报告落 `<netlist_base>_r5_report.txt`。

## Agent 工作链

1. 读 `/proj/dscqa/.../tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist`（permission denied，agent 通过 read_files 间接访问）
2. 迭代开发 `r5_functional_report.py`（58 次 editor 调用）：_analyze_act_ldo_r5 → _write_r5_report(_p2/_p3/_compact/_v2) → _fix_r5_names/_align/_notes/_abbrev/_final/_last/_undo → r5_functional_report.py（最终 836 行）
3. 在 VtscRef_standard_tb netlist 上验证（产 VtscRef_R5_functional_report.txt），再切到 ACT LDO netlist
4. 最终脚本结构：
   - `Netlist` 类：parse `.SUBCKT`，按 `** TopDesStart`/`** TopDesEnd` 块 + signal-net 计分选 top（选 AG_Vcc2scALDOAct 而非内部 AG_ActAmpBiasGenLoc）
   - `Resolver`：回溯 stdcell 驱动链 → 布尔 AST（VAR/NOT/AND/OR/XOR），leaf = 顶层 input port
   - `classify_stdcell`：正则 `^([a-z]+?)(\d*)([lstfvywbnm]?)x(\d+...)` 识 invLx4/nand2Lx1/nand3Lx1/nand4Lx1/bufLx8 等；switch_/lvlshft/ag_/xi_ 非 stdcell
   - `simplify`：QM SOP 化简（≤5 变量）
   - `generate_report`：5 节固定格式 [0] I/O 分类（POWER/POWERON/GLBREF/TESTMODE/CTRL IN/LOGIC/ANALOG）[1] 等式 + PwrOn 门控 [2] 2^N 行真值表 [3] 模拟输出 [4] sim 验收
   - `main`：`python3 r5_functional_report.py <netlist>` → stdout + 落盘 `<base>_r5_report.txt`

## 关键产物（trace-verbatim）

- **r5_functional_report.py**（836 行 / 27063 B）逐字自 `/home/tongni/Desktop/1_Vcc2sc_stdby/r5_functional_report.py` ← 参考解
- **VtscRef_R5_functional_report.txt**（ACT LDO 报告样本，73 行）含 Vcc2sc2Vcc/Vcc2scActDis/Vcc2scActEn 真值表 ← 报告格式参考
- 真值表（VtscRef design，sample report）：
  - Vtsc2Vcc = cm0_ag_ShftVtsc_2 & PwrOn3 & cm0_ag_ShftVtsc_1 & !cm0_ag_ShftVtsc_0（4 变量 16 行）
  - VtscAmpDis = cm0_ag_ShftVtsc_2 & PwrOn3 & cm0_ag_ShftVtsc_1（3 变量 8 行）

## Case 合成（EDA-Eval-DesignFlow-ActLdoR5ReportGen-001）

- **形态**：produce 可复用脚本（参数化 `generate_report(netlist_path)`）
- **A**（SUT 可见）：`act_ldo_r5.netlist` — faithful reconstruction，顶层 AG_Vcc2scALDOAct + TopDesStart 块 + 5 stdcell leaf defs + 3 控制输出 nand/inv 链（Vcc2sc2Vcc = 4-var 16-row, Vcc2scActDis = 3-var 8-row, Vcc2scActEn = 2-var 4-row），analog ActAmpCore opaque
- **hidden B**：`vwlpref_r5_b.netlist` — 结构性差异：AG_VwlpRefB / PwrOn2 / GlbRef085 / cm0_ag_ShftVwlp_1/0 / cm1_ag_RegHbias / EnVwlp / Vwlp2Vcc(3-var 8-row)=cm0_ag_ShftVwlp_1 & PwrOn2 & !cm0_ag_ShftVwlp_0 / VwlpAmpDis(2-var)=cm0_ag_ShftVwlp_1 & PwrOn2 / VwlpActEn(2-var)=PwrOn2 & cm0_ag_ShftVwlp_0 / VwlpRef
- **check**：真跑 SUT 脚本 on B → 14 断言（a zip / b 脚本 / c 运行 / d 5 节 / e POWER / f TESTMODE / g LOGIC / h 等式 / i 真值表行数 / j 真值表输出列独立对账 / k 第二输出 / l 防硬编码A / m analog / n verification），k_check=k_rationale=14
- **§4.9**：5 neg（empty/printf/hardcoded_A/core_deleted/nosim）全 FAIL，ref 14/14 PASS
- **asset_fidelity**：A=trace-verbatim（脚本逐字 + netlist 等式 verbatim 自 trace），hidden B=结构性差异非仅文件名
- **layer**：L1（check 阶段纯 Python 静态解析 + 真跑脚本 on B，无 EDA 二进制）
- **track**：faithful（A 档，真实 trace 用户原话作任务说明）

## 访问约束

- `/proj/dscqa/.../tongni_DSCQA_2nd_sim_AG_Vcc2scALDOAct_sim_schematic.netlist` permission denied（属 tongni:dscqaw，e0031982 身份拒访）→ A netlist 由 trace 中 VtscRef_R5 报告的等式 + stdcell 链 faithful 重建
- `r5_functional_report.py` + `VtscRef_R5_functional_report.txt` 可读（/home/tongni/Desktop/...），已 scp 到 sandbox
- `vwlpref_pwrfix.netlist`（VwlpRef sim，2091 行）可读但无 stdcell 逻辑输出（"No stdcell-driven logic outputs"），仅作格式参考，未用作 case 输入
