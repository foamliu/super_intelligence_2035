# peek: xlym9 — SPICE netlist → IBIS conversion method how-to Q&A

**session**: `1794481759263_xlym9` · user `alleng` · host `hfeg0pkn002(10.129.2.11)` · mc=12 · domain=schematic_netlist
**fetched**: 54649B messages.json · 11 msgs (6 user / 5 assistant) · agent=lead
**revival**: r570 parked「'spice网表转ibis方法' = how-to Q&A; mc12」→ 11-15 reaudit 判 `可造(需原型)` · r927 revival-from-park re-peek under new standard
**选轮合规**: U#0 = msg0 = 首条 user turn (`<user_input mode="act">`)，提出需求 pattern (非给根因/非给修复方案) → A 档选轮规则① 合规

## trace 全 11 msg

- **U#0** (verbatim): `spice网表转ibis方法` — 提出需求（SPICE netlist → IBIS 转换方法 how-to Q&A）
- A#1: invoke skills `ask-eda` + `aether-tool-qa`（双 skill 并发查知识库）
- U#2/U#3: command-name `ask-eda` / `aether-tool-qa` 触发（skill spec 注入）
- A#4: `run_approved_command` python-runner `ask_eda.py ask --query "SPICE网表转IBIS方法 ... step by step"`
- U#5: python-runner **FAILED** (`Fatal Python error: initfsencoding: Unable to get the locale encoding / ModuleNotFoundError: No module named 'encodings'` — SIGABRT，locale 环境坏)
- A#6: `list_allowed_files /home/alleng/Desktop`（找本地 grounding 资源）
- U#7: dir listing（1.csv / cdsLibMgr.il / display.drf / libManager.log / open_par*.tcl / sxcmd.log — 无 IBIS 相关文档）
- **A#8** (GOLD): assistant 基于 skill 知识库 + 自身知识，给出完整 SPICE→IBIS 转换方法指南（见下）
- **U#9** (verbatim): `bit(a,n)='int(a/(2**n)-2*int(a/(2**(n+1))))' 具体计算解释` — 独立子任务（bit 提取公式解释，与 IBIS 无关）
- A#10: bit 公式逐位推导（右移 n 位 → 取 LSB，等价 `(a>>n)&1`，用于 SPICE/Verilog-A/SKILL/Excel 无位运算符环境）

## A#8 GOLD 内容（SPICE→IBIS 转换方法，将作 grounding 知识源）

**概述**: IBIS = 行为级 I/O 缓冲器建模规范，将 SPICE 晶体管电路抽象为 **I/V 曲线**（Pullup/Pulldown/Power Clamp/GND Clamp）+ **V/T 曲线**（Ramp/上升下降边沿），不含晶体管级细节 → 保护 IP。

**方法一：EDA 工具自动提取**
| 工具 | 流程 | 关键 |
|---|---|---|
| Cadence Virtuoso/Spectre | I/O 测试电路 → Spectre DC+Trans → **ibisgen / ModelWriter** 提取 → .ibs | DC sweep Pullup/Pulldown/Clamp + Transient Ramp/V/T + Corner(Typ/Min/Max)+温度 |
| Synopsys HSPICE/FineSim | `.IBIS` 控制语句 或 `hspice -ibis` 或 **FineSim IBIS Model Utility** | HSPICE 原生支持 .IBIS |
| 华大九天 Aether | MDE / pyAether 脚本辅助提取 I/V V/T → 手动组装 .ibs（无一键导出） | DC/Trans 仿真 → 导出 → 按 IBIS 规范整理 |
| 其他 | IBIS-AMI Builder(SerDes) / Sisoft IBIS Editor(手动编辑+校验) / GoldenGate(ADS) | — |

**方法二：手动提取流程（通用）**
- Step 1: IBIS 文件结构（[IBIS Ver]/[Component]/[Manufacturer]/[Package] R_pkg L_pkg C_pkg/[Pin]/[Model] Model_type/[Temperature Range]/[Voltage Range]/[Pullup]/[Pulldown]/[Power Clamp]/[GND Clamp]/[Ramp] dV/dt_r dV/dt_f/[Test Data]/[End]）
- Step 2: I/V 曲线仿真设置表
  | 曲线 | 仿真设置 | 测量条件 |
  |---|---|---|
  | Pulldown | 输出→VDD 固定，扫描 Vout 0→VDD | 测流入输出电流 |
  | Pullup | 输出→GND 固定，扫描 Vout 0→VDD | 测从 VDD 流出电流（符号取反）|
  | Power Clamp | Vout 扫描 VDD→VDD+1V | Vout>VDD 钳位电流 |
  | GND Clamp | Vout 扫描 -1V→0V | Vout<GND 钳位电流 |

## buildable 判定

✅ **真实 trace**: xlym9 alleng@hfeg0pkn002，11 msgs，A#8 = 用户实际接受的 GOLD 答案（完整方法指南）
✅ **D-domain**: schematic_netlist（SPICE netlist → IBIS，netlist grounding；IBIS 是 I/O 缓冲器网表行为模型）
✅ **A 档选轮合规**: U#0 = msg0 = 提出需求（非给根因/修复）→ trace-faithful A 档
✅ **k≥8 有牙 check**: manual-grounded how-to produce-task reframe（套 aihrj r711 AetherNetHighlightQA-001 pattern，D 域第 N 例 manual-grounded howto）：
  - candidate 读 knowledge doc + 问题 → 结构化操作指南 JSON（method/methods[]/steps[]/tools[]/prerequisites[]/cited_sections[]/overall）
  - check() 真跑候选 subprocess on hidden B（不同 IBIS 子主题 / 不同手册章节 / 不同问题），断言：
    ① zip+cand.py+fix_report.json 齐全 ② 编译 ③ A JSON 合法 + 键齐全 ④ B subprocess stdout 合法 JSON ⑤ B methods 覆盖 EDA-tool-auto + manual-extract 两类 ⑥ B steps 非空且含 I/V 曲线仿真步骤 ⑦ B tools 含 ≥2 具体工具名（ibisgen/hspice -ibis/FineSim IBIS Utility/MDE 等）⑧ B cited_sections 引用段名真实存在于 B doc ⑨ B 反硬编码（B 输出 0 个 A-only token）⑩ B report.txt 含 method+step+tool 关键词 …（≥10 断言 a-j）
  - 退化提交 (空壳/print-only/core-deleted) 全 FAIL
✅ **资产 synthesized-reframe**: knowledge doc A 从 A#8 内容合成（自包含，无 /proj 依赖）；hidden B 平行场景（不同 IBIS 子主题，如 DDR4 ODT IBIS / LVDS IBIS / 不同手册章节，反硬编码 A-only token）
✅ **无 /proj 依赖**: manual-grounded，资产是合成的知识文档，非 /proj 私有网表 → P-002 D 不可达问题不适用

## 拟造（defer synth to r928）

- **case_id**: `EDA-Eval-DesignFlow-SpiceIbisConvMethodQA-001`
- **domain**: schematic_netlist · **grade**: A (trace-faithful) · **l1_subgrade**: L1-realrun-python · **asset_fidelity**: synthesized-reframe
- **资产 A**: `ibis_conv_method_A.md`（从 A#8 合成的知识文档：概述 + 方法一 EDA 工具表 + 方法二手动流程 + IBIS 文件结构 + I/V 曲线仿真设置表）+ `question_A.txt`（verbatim U#0「spice网表转ibis方法」）
- **hidden B**: `ibis_conv_method_B.md`（平行场景：不同 IBIS 子主题，如 DDR4 ODT buffer IBIS 提取 / 不同工具组合 / 不同 I/V 曲线细节，反硬编码 A-only token{ibisgen, ModelWriter, hspice -ibis, FineSim IBIS Model Utility, MDE, pyAether, Pulldown, Pullup, Power Clamp, GND Clamp, Ramp, dV/dt_r}）+ `question_B.txt`（不同 but 同类问题）+ `hidden_manifest.json`
- **candidate_ref.py**: 解析 knowledge doc（markdown 结构：## 概述 / ## 方法一 / ## 方法二 / Step / 表格）+ 问题 → 结构化 JSON（methods[{name,tools[],steps[],prerequisites[]}]/file_structure/iv_curve_table[{curve,setup,measure}]/cited_sections[]/overall）+ report.txt + stdout JSON 摘要
- **check.py**: ≥10 断言 a-j（见上）
- **0-case 合规**: peek-only（synth ~25-30min + 本轮选料 forensics ~15min 超 40min 预算，拆 peek+synth 两轮，承 r921/r923/r925 范式）

## 下轮 r928

1. 首选 xlym9 synth（peek 已铺好）
2. r928 非 discuss mandatory（r926 清付→r930 due）
3. hk622/cydnq dedup/D.jsonl 入 git 三 DEBT 待 A 厘清
4. D-keyword .cdl/.spi/.sp 20 轮 overdue 待 @A r927 五催（r926 四催未兑现）
5. MEMORY_D 体积 ~30KB，r928 若 synth 须视体积归档
