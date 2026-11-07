# 深读笔记 · cynthiaz 1790229492123_m7hxu @ hfeg0pkn005 · 2026-11-07 20:2x

## trace 来源
- session: `1790229492123_m7hxu` (cynthiaz @ hfeg0pkn005, mc=409, sp=36, tot=409, ratio=0.088)
- spice 工具构成: 23 spectre, 18 lang:pyAether, 105 pyAether, 67 netlist, 172 schematic → characterization/spice_sim 域（deck 生成 + sizing）
- trace 大小: 296KB / 96 msgs
- 获取: scp 10.129.2.14:/home/cynthiaz/.cline/data/sessions/1790229492123_m7hxu/1790229492123_m7hxu.messages.json

## 用户意图（原话逐字）
- U1: `design` （单字菜单触发）
- U2: `design a double-tail slicer,meet target data rate 2.9Ghz` （**目标轮，A-档任务说明用此**）
- 之后无更多用户轮（用户未给出根因/修复方案，纯目标型 → 符合 A-档 §①.2 选轮规则）

## assistant 工具链（关键产物）
1. list_allowed_files / get_agent_policy_status 探查 workspace（Desktop 几乎空）
2. RAG_MCP_Server__search_apis 多轮检索 pyAether 建图 API（dbNewCellView/dbCrtInst/dbSetInstParam/dbCrtSchWire/leGuiCrtTransistor/seGuiRunSimulation/emyInitAether ...）
3. SandBox_MCP_Server__run_code (pyAether + skill) → **sandbox 离线**（10.129.8.231:23935 connection refused）
4. editor 写 4 个产物文件到 `/home/cynthiaz/Desktop/double_tail_slicer/`（多次 insert 因 editor 6000 字符上限拆段）：
   - `double_tail_slicer_schematic.py` (250 行) — pyAether 建图脚本
   - `double_tail_slicer_testbench.sp` (155 行) — **SPICE netlist + testbench**（金标准核心）
   - `double_tail_slicer_testbench.scs` (119 行) — Spectre 兼容版
   - `README.md` (156 行) — 设计文档 + sizing 表 + 性能目标
5. list_allowed_files / read_files 复核 4 文件齐全
6. 末轮（msg 96）汇总交付

## 金标准（人工复核 = assistant 真实产物）
**SPICE deck 关键结构**（double_tail_slicer_testbench.sp，5288B）：
- `.subckt double_tail_slicer INP INN CLK VOP VON VDD VSS`（7 端口）
- 11 个 MOS 器件 M1-M11：
  - M1/M2 NMOS w=6.0u l=0.1u — 输入差分对 (INP/INN → VX/VY)
  - M3 NMOS w=4.0u l=0.1u — 尾电流 (CLK 控制)
  - M4/M5 PMOS w=2.0u l=0.1u — 1 级二极管负载
  - M6/M7 NMOS w=3.0u l=0.1u — 2 级再生 NMOS 对
  - M8/M9 PMOS w=6.0u l=0.1u — 2 级交叉耦合 PMOS 对
  - M10/M11 PMOS w=1.0u l=0.1u — 复位开关 (CLK 低预充)
  - Rbleed VRSN VSS 1e12
- 内联 PTM 45nm BSIM4 模型 (.model nmos1/pmos1)
- testbench: VDD=1.0V, VSS=0, VCLK pulse(0 1.0 50p 20p 20p 150p **344.8p**) — **周期 344.8ps = 1/2.9GHz**
- VINP/VINN pwl 差分 NRZ @ 2.9Gb/s, 100mVppd, Vcm=0.5V
- CLOADP/CLOADN 3fF, `.tran 1p 3n 0`
- `.measure tran t_setup/t_delay/v_swing/avg_power`
- `.print`/`.probe`

**README sizing 表**: M1-M11 各列 W/L/M/Role；性能目标表（Data Rate 2.9Gb/s, VDD 1.0V, 决策时间 <100ps ...）

## 根因 / 任务本质
用户给出高层设计目标（double-tail slicer @ 2.9GHz），assistant 从零设计并产出完整 SPICE deck + sizing + 文档。**本质 = 参数化 SPICE deck 生成**：给定目标速率，生成 double-tail (StrongARM) slicer 的 .subckt + testbench + sizing + README。

## case 合成方向（A-档 spice_sim L1）
- **交付**: 通用脚本 `gen_slicer_deck.py <target_ghz> <outdir>` → `slicer.sp` + `sizing.json` + `README.md`
- **A (SUT 看)**: prompt=用户原话 U2 + task_brief（交付接口 ≤3 行）；无 attachments（用户未给）
- **hidden B**: target_ghz=4.5（≠ A 的 2.9），check 只跑 B
- **check.py k=12 断言**: zip 4 文件 / py_compile / 无参非零 / B exit0+3 文件 / .subckt 7 端口 / ≥8 MOS 器件 / .tran / CLK 周期≈1/4.5GHz(222ps±15ps, 非 345ps) / 差分输入对 / sizing.json W/L/M 合法 ≥8 器件 / README 含 4.5GHz+sizing 表(非 2.9 硬编码) / 幂等
- **金标准来源**: assistant 真实 deck（golden_m7hxu/double_tail_slicer_testbench.sp），参数化为 target_ghz
- **断言只对事实**（结构 / 周期数值 / 器件计数 / 幂等），🚫 不对措辞

## 自验计划
- ref gen_slicer_deck.py 跑 B(4.5) → check 12/12 PASS
- 3 negatives (empty_stub / print_expected / hardcoded_2.9) 全 FAIL
- §4.9 (a)(b)(c) 三假全 FAIL
- 断言闸门 k_rationale == k_check == 12 ≥ 8 ✓
