# trace_deepread — 1792140744683_z5ett (jessegao @ 10.129.2.14, mc=137)

**domain**: analog_context (LDO 稳压器 SPICE 设计 + 测试台)
**source tools**: aether:512; transistor:224; pdk:169; netlist:129; schematic:99; pyaether:91; calibre:37

## 用户轮（逐字）
- **U#0** (A-faithful 提需求，未给根因): 「帮我生成一个LDO电路上电压域为1.1V，输出为0.9V，要求其静态功耗10uA以内，PSRR=-20dB @0~100kHz，DC gain大于40db，PHASE MARGIN 大于40度」
- **U#1** (澄清): 「声明一下，这里的psrr为负值」
- **U#2/U#3** (产出需求): 「帮我输出一份电路图及验证报告」
- **U#4-U#8**: 文件打开/查看/操作引导（非 produce）

## agent 行为
51 次 editor 写入（cline editor: {path, new_text, old_text, insert_line} 增量编辑），落地 9 个产物文件：
- `dut_ldo_v1.sp` — LDO subckt（5 次 editor，增量构建）
- `tb_ldo_v1_ac.sp` (11 次) — AC 增益 + 相位裕度测试台
- `tb_ldo_v1_psrr.sp` (2 次) — PSRR 测试台
- `tb_ldo_v1_linereg.sp` (1) — 线调整
- `tb_ldo_v1_loadreg.sp` (1) — 负载调整
- `spec.md` (11 次) — 规格 + 验收指标
- `design-report.md`、`circuit_diagram_and_verification_report.md`、`pre-design.md`、`state.json`、`clean_spec.py`、`verify_psrr.py` 等
- 上游生成器 `gen_ldo_v1_scheme_aether.py`（Spice_Agent/aether 流，live pyaether）

## A-faithful 决策
- U#0 是纯指标驱动 produce-demand，**未给根因/修复** → A 档规则 ② 不禁止。
- 但真实流程依赖 **Spice_Agent / pyAether + PDK 模型**（live，不可附加），dut.sp 中的 MOS 模型/model include 与 `/home/jessegao/Spice_Agent` 路径均不可离线复现 → **B 档 synthesized**：服务用户真实目标（按指标生成 LDO 设计 + SPICE 测试台），做成离线可验的配置驱动 Python 生成器。

## 合成（B 档）
- **真实 specs (A)**: vin=1.1, vout=0.9, vref=0.6, iload=10mA, iq_max=10uA, psrr=-20dB, gain=40dB, pm=40°（逐字取自 U#0 + U#1 澄清 psrr 负值）。
- **gen_ldo_design.py**: `--specs <specs.json> --outdir <dir>`；读 8 字段，emit dut.sp(.subckt ldo vdd vout gnd + PMOS pass + VCVS 误差放大 + **R1/R2 反馈分压 R1/R2=vout/vref-1** + Vref + Cc + Rq) + 4 测试台(.AC gain/pm、Vdd AC 注入 .measure PSRR、.DC Vdd、.DC Iload + .measure) + spec.md(7 label:value)。
- **hidden B**: vin=1.2/vout=0.8/vref=0.5/iload=20mA/iq=5uA/psrr=-30/gain=50/pm=55（与 A 全不相交，反硬编码）。
- **hidden B2 (跨输入)**: vin=3.3/vout=1.8/vref=0.9/iload=50mA（更大电压域，反硬编码分压比 + spec.md）。
- **反硬编码三轴**: A/B/B2 vout 与 vref 全不相交 → R1/R2 比 (0.5/0.6/1.0) 全不同；spec.md 数值随输入变；Vdd 源值随 vin 变。

## check.py (16 条件 a-p)
解 zip(防泄漏) → py_compile → B 真跑 subprocess → dut.sp subckt 端口 + R1/R2 比(2% 容差) → tb_ac .AC+.measure gain/pm → tb_psrr Vdd AC+.measure PSRR → tb_linereg .DC Vdd → tb_loadreg .DC Iload+.measure → spec.md 7 值数值匹配 → B2 跨输入 spec.md Vout + R1/R2 比 → B 测试台 Vdd==vin → 3 次确定性 sha256。

## 自验
- ref PASS 16/16 a-p ✓
- 4 negatives(empty/hardcode_a/no_divider/no_ac) 全 FAIL ✓
- §4.9 三假(empty/print_expected/ref_core_deleted) 全 FAIL ✓
- 3 次确定性 sha256 一致(3a1d4d304f8150d5) ✓
- **断言闸门** k_rationale=k_check=16 ✓

## 教训
(1) cline editor 工具用 `{path, new_text, old_text, insert_line}` 增量编辑（非 write_to_file），深读提取产物内容需按序应用 edit 链或看 run_approved_command 的 cat 输出；本轮只取 user turns + 产物文件名 + U#0 specs 即足以合成。
(2) shard D 池 high-mc(>100) 仍以 skill搭建/live pyaether/Q&A/TCAD-MCP 开发为主，clean 离线可验 produce 密度低；LDO 这种「指标→SPICE deck 生成」是 analog_context L1 可验好范式（结构 + 规格驱动分压比天然 16 条件）。
(3) 生成类任务用「隐藏 B 换规格」反硬编码可行：判分跑候选生成器于 B/B2 specs，校验分压比与 spec.md 数值随输入变。
(4) `.subckt` 端口名与 R1/R2 命名须在 prompt 里固定，否则结构断言无法确定性比对。
