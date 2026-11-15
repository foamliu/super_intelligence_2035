# Deepread — 1793857356226_kubzy (resistor TRIM netlist "parallel not reflected" explain)

- session: `1793857356226_kubzy.messages.json` (138 KB, 21 msgs: 2 real user turns + 1 tool-result-heavy assistant diag)
- user: zhililu | host: hfeg0pkn002 (10.129.2.11) | model: lead | match_count: 169
- domain: spice_sim | shard: B | layer: L1 | track: revival-pool (reaudit r618 误杀复活 #12)
- case: **EDA-Eval-DesignFlow-ResistorTrimNetlistExplain-001** (round #630)

## 真实任务
用户在 Aether 设计电阻 TRIM 基准电路 `R_TRIM_VREF`（3-8 译码器 DEC_3T8_svt_dbc_x1 +
8 反相器 INV_2X_SVT + 17 个 rhi_dbc 电阻梯 + 8 传输门 TGATE_SVT_TRIM）。她对若干电阻
（如 R20）在 pcell 里设 `segment=2` / `connection=parallel`，期望阻值减半，但导出的
CDL 网表里这些电阻仍是 `rhi_dbc w=1u l=1.65u mr=1` 单根，和普通单根尺寸一样——
「并联减半」没体现在网表里。

## trace 行为
- U#0（中文，粘完整 R_TRIM_VREF 网表）：「为什么我有的电阻选择的parallel的连接方式，阻值减半，
  但在网表中尺寸和单根一样，比如R20」
- U#1：「但是R20里的segment我选择的2呀，connection选择的parallel」
- 助手：先给结论（网表忠实反映 schematic 对象/属性，R20 是单根 mr=1）；再查 Aether 手册
  （aether-tool-qa skill → grep references → read part_IX_Tools.md Chapter 106 VCell Resistor）；
  最终根因：`segments`/`connection` 是 VCell/版图绘制域参数，只影响版图画法与仿真有效阻值
  （`effW = 2×segW` → R/2），但**未被该 PDK 的 Device Define 映射进 CDL 网表的 w/mr 字段**。
  CDL 只映射 `w=segW`、`l=segL`、`mr=multiplier m`。修复：把 m(mr) 设成 2 或画两根并联实例，
  否则版图(两段并联 R/2)与 CDL(单根 mr=1 R) LVS 不匹配(2:1)。
- tools: skills(aether-tool-qa) + run_approved_command(python-runner grep) + read_files + editor；
  无 run_code 写产物，全程诊断/解释。

## 真实网表结构（trace U#0 原文，A 档 trace-faithful）
- subckt R_TRIM_VREF A B EN Trim<2> Trim<1> Trim<0> VDDA VSSA（8 端口）
- 8 × I_INV_2X_SVT_19<N>（cell INV_2X_SVT）
- 1 × I_DEC_3T8_svt_dbc_x1_18（cell DEC_3T8_svt_dbc_x1，行续符 `\`）
- 17 电阻 rhi_dbc：R22/R21/R19/R5/R4/R6/R7/R10/R9/R20/R18/R17/R25(w=1.5u)/R16/R24/R11/R8(w=500n l=26.4u)
- 8 × I_TGATE_SVT_TRIM_*（cell TGATE_SVT_TRIM）
- 全部 mr=1（trace 原状，无一真并联）→ 解释核心 = 意图(parallel) vs 网表(mr=1 单根) 的 gap

## 合成 case 设计（A 档 trace-faithful L1 explain/analysis）
- **可见 A**：真实 R_TRIM_VREF.sp（trace 原文）+ trim_spec.json（每电阻意图连接；R20/R4=parallel seg2、
  R7=series seg2、其余 single）+ pdk_params.json（rhi_dbc rsh=1050 Ω/□，公式 R=rsh*(L/W)/mr）
- **隐藏 B**：合成 R_TRIM_VBG（4-16 译码器 + 16 反相器 + 12 电阻 + 4 传输门，rsh=850）——结构全异：
  2 个真 mr=2 并联(R1/R7 matched) + R3 parallel seg3 异常 + R5 series seg2 异常
- **SUT 任务**：写 `analyze_trim_netlist.py(workdir,out_dir)` 解析网表(处理行续符 `\` + `\<N\>` 转义)、
  分类实例、算 unit/effective R、逐电阻交叉核对意图 vs 网表(mr+实例数)、产 trim_report.json 打包 submit.zip
- **check.py**：独立 oracle(regex 单遍，与 ref 续行 join+结构解析 实现不同) + 13 断言 a-m 含 cross-input guard

## check.py 13 断言 a-m
a zip 两件 / b exit0+11 字段齐 / c subckt+8 端口 / d 17R/8inv/1dec/8tg / e decoder_cell /
f R22 unit=rsh*(L/W)=1732.5 验公式 / g R22 eff=unit/mr / h matched 14 集合 / i R20 异常 parallel/seg2/mr1 /
j R4+R7 并联+串联双检测 / k R20 should_be=unit/2=866.25 且 R7=unit*2=3465 方向 / l key_concepts 4 词 /
m 隐藏 B==oracle_B 且 A!=B(subckt/电阻数/异常名)

## 自验
- ref analyze_trim_netlist_ref.py → check() 13/13 PASS（A 全 PASS + hidden B 全 PASS，check 自包含独立 oracle）
- 4 negs：naive_hardcode_a→[m](cross-input guard 有牙) / always_empty→[c] / print_only→[b] / core_deleted→[h] 全 FAIL
- §4.9 degenerate(空壳/print/删核心)全 FAIL + negative_selftest ALL GREEN(ref PASS + 4 neg FAIL)
- k=13 ✓ k_check==k_rationale==13 ≥8 ✓
- no-leakage：attachments 仅 netlist/+task_spec.json，不含 reference/hidden/jsonl/test ✓

## 覆盖分子
spice_sim 域 + 电阻 TRIM 网表意图诊断（pcell segment/connection vs CDL mr 映射 gap）。
B 档 explain/analysis 首例——"电阻并联意图未体现"根因 + LVS 一致性。复活池变现 #12。
