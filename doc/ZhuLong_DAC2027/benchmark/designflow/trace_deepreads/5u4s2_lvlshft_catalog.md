# 深读笔记: 5u4s2 — Level Shifter 模拟电路生成 (analog_context)

## trace
- session: `1782800756855_5u4s2`
- user: e0025730 @ 10.129.8.86 (mc=52)
- size: 314KB / 78 msgs / 2 user turns (U#0「启动业务场景: 模拟电路生成」+ U#70「/lvlshft」)
- tools: netlist:222;analog:57;waveview:21;schematic:55;virtuoso:45;pyaether:8;hspice:7

## 用户意图
U#0 触发 lvlshft skill「启动业务场景: 模拟电路生成」，U#70 重触发「/lvlshft」。意图 = 启动电平转换器电路设计优化工具链并呈现当前状态。

## assistant 工具链
1. `run_commands`(ls/pwd/find) 探 /home/e0025730/lvlshft + /home/e0025730/devops/eda_data_bridge
2. `skills`(lvlshft) 调用 skill，获得 SKILL.md 指令(工作目录 /home/e0025730/devops/eda_data_bridge/bundle/lvlshft/lvlshft_optimize/01_lvlshft_spec)
3. 探 Python 环境：openpyxl 不可装(无网)，pyyaml 可用，选 /usr/bin/python3.6
4. `read_files`(lvlshft.py / spec_config.yaml / run_pipeline.py / soa_selector.py / run_test_only.py / netlist_defaults.yaml / sp_defaults.yaml / sizing/voltage_table.yaml)
5. `run_commands`(python3.6 lvlshft.py list/status/result) 跑通 CLI，获得 23 拓扑/6 Case/Case2 Vcc2Vdleq 最优参数 + PVT 验证
6. `SandBox_MCP_Server__run_code`(pyAether) 失败(ip/port 未配)
7. 汇报业务场景状态

## 关键产物（用户接受的结果）
**Level Shifter 拓扑目录 + 尺寸/验收状态**：
- 模块: LevelShifter, 当前设计: Case 2 Vcc2Vdleq (VCC→VDLEQ 电平转换)
- 23 拓扑 / 6 Case:
  - Case 1 (正向, 6): Vcc2Vdd1/Vcc2Vwlp/Vcc2Vpcsg/Vcc2Vcslp/Vint2Vwlp/Vint2Vpcsg — 输入nMOS+保护nMOS×2+前馈pMOS+上拉pMOS
  - Case 2 (正向, 11): Vcc2Vdleq/Vcc2Vdiv/Vcc2Vdly/Vint2Vdleq/Vint2Vcc/Vdd12Vcc/Vwlp2Vcc/Vwlp2Vdd1/Vcc2Vdiv2/Vcc2Vdly2/Vint2Vdleq2 — 输入nMOS+保护nMOS+上拉pMOS
  - Case 3 (负压, 2): Vss2VkbVcc/Vss2VncsgnVintAry — 负压泵
  - Case 4 (负压, 1): Vss2VkbVdd1 — 负压泵
  - Case 5 (高压, 1): Vdd12Vwlp — 高压电平转换
  - Case 6 (特殊, 2): Vint2VdleqAryA/Vint2VdleqAryG — 特殊输入阵列
- 最优参数: beta1=70, S=0.05, L=1.30um, W=1.00
- PVT 验证(全 PASS): Rise 0.573<=0.694ns / Fall 0.304<=0.31ns / Ioff 1.588<=5nA / Aging 7.42<=20%

## A-faithful 判定
**不可行**：真实 lvlshft bundle + SPICE 仿真结果在 /home/e0025730 私有不可附加；live SPICE 不可移植；openpyxl 缺失使原工具链在沙盒不可跑。→ **B 档 synthesized**。

## 合成 plan
facet = **电平转换器拓扑目录 + 尺寸/验收报告生成器**(`gen_lvlshft_catalog.py --spec --outdir`)
- 输入: spec JSON {module, design, cases[*].{case_id,class,topologies[*].{name,structure}}, current, sizing, verification[*].{metric,measured,spec,unit,op,corner}}
- 按 op(<=,>=,==,!=,<,>) 真实计算 PASS/FAIL（反 always-pass）
- 产出: topology_catalog.md(Case/拓扑/结构表 + Total 汇总) + sizing_report.md(尺寸参数表 + 验收表 PASS/FAIL + Overall) + manifest.json(11 键: n_cases/n_topologies/n_pass/n_fail/overall/files 等)
- check 验结构/计数/PASS-FAIL 计算/反硬编码/跨输入 B2/确定性

### 反硬编码五轴
1. design 名全不同(A=Vcc2Vdleq / B=Hvdd12Vwlp_HV / B2=NgVss2VkbVcc_Neg)
2. case 数不同(A=6 / B=4 / B2=3) → n_topologies 不同(23/15/8)
3. sizing 值不同(A beta1=70,S=0.05 / B beta1=45,S=0.08 / B2 beta1=55)
4. PASS/FAIL 组合不同(A 全 PASS / B 3PASS2FAIL / B2 2PASS2FAIL) → overall 不同(ALL_PASS/HAS_FAIL/HAS_FAIL)
5. B 用 op `>=`(DC Margin 0.18>=0.20→FAIL) 测运算符处理；A/B2 全 `<=`

### check 16 条件 a-p
a zip+compile+script / b B-run exit0+3files / c manifest 11 keys / d n_cases==4 n_topo==15 / e catalog 全15 B拓扑名 / f catalog 含结构串 / g Total 15 across 4 / h report 全 B sizing 值 / i report 全5指标 / j n_pass==3 n_fail==2(计算) / k Rise Delay 标 FAIL / l overall==HAS_FAIL / m 反硬编码源码+A23+B2(3/2/design) / n DC Margin op>= FAIL / o 3x确定性 / p 无 A 拓扑名泄漏

### 自验
- ref PASS 16/16 a-p
- 5 negatives 全 FAIL(empty_shell→b / hardcode_a→d / print_expected→b / ref_core_deleted→j / naive_stub→d) 各 distinct first_fail
- §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL
- 断言闸门 k_rationale=k_check=16 ✓

## 教训
1. **lvlshft skill 触发式 trace 是 B 档 L1 好范式**：skill 调用产出的「拓扑目录+尺寸+验收」天然结构化，spec→报告映射明确(op→PASS/FAIL 是强反硬编码轴)，16 条件天然丰富(结构/计数/运算符/跨输入/确定性)。
2. **op `>=` 是额外反硬编码轴**：B 的 DC Margin 用 `>=`(0.18>=0.20→FAIL)，naive 只处理 `<=` 者 n 上 FAIL；ref_core_deleted(全 PASS) 在 j/k/l 上 FAIL。
3. **PASS/FAIL 不能写死**：A 全 PASS / B 3-2 / B2 2-2，hardcode_a(全 PASS A 档) 在 d/j 上 FAIL。
4. **fresh 池 mc>=30 clean produce 确实稀缺**：本轮 peek 16 候选(2批×8)，仅 5u4s2 是干净 D-domain produce；其余为 skill-setup / simdiag 软件工程 / DRC 规则解析(shard C) / auto-via(layout) / NO_FILE。验证 MEMORY「中等 mc 池 Q&A/debug/skill 占主导」结论。已 park 13 weak 候选清理池。
