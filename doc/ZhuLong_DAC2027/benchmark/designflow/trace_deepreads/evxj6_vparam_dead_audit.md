# evxj6 deepread — Verilog parameter dead/effective audit

**trace**: `1793605487158_evxj6.messages.json` | xuluo@hfeg0pkn001 | mc=333 | 293 msgs / 1.83MB
**domain**: schematic_netlist (Verilog RTL param analysis) | **tier**: L2 | **grade**: B (synthesized)
**claimed**: 2026-11-09 #438

## 用户意图脉络（30 user turns）

U#0 「/proj/dbcoa/V0/simdir/verilog/tsq/regression/cyclic_xyz/ 分析这个目录下的代码，这是python下对应的参数，告诉我两者参数有何不同 {tREFI:3900, tRFC:380, tRC:60, ...}」—— **提需求：Python 行为模型 (PyRHR) 参数 vs Verilog RTL 仿真参数对比**（未指根因 → A 候选）
U#1 「列个表对比所有python中提到的参数」→ 表格化
U#5 「同时列出python的每个参数在verilog对应的文件」→ 加 SV 源定位
U#6-#11：深入 under2 (DiscardUnder2) 功能——用户问「RTL 中没有而 PYTHON 中有？」→ agent 最初误判，后在 netlist L4484-4495 找到门级链，**纠正**：RTL 有 under2，极性 `cm1_ro_DisUnder2=1`→保护开
U#12-#15：rhr_parameter.pkg 时序核查——**关键发现**：`tRFC=280000` 是死参数（全目录零引用，仅注释 `//tRFC=280ns; 380ns`），`tRC=63` 只在 `loop_time` 扣 3ns 余量；**实际生效时序全部由 `rhr_driver.sv` 硬编码延时实施**（33×11.52ns≈380.16ns ref，10 条延时和=60.0ns act）
U#16-#27：xyz 组合机制（SV 侧 z 是预算反推因变量；1/169/3 vs 1/1/255 hammer 行走方式不同）
U#28：用户贴 `gen_paralist_sv_aligned.py` 生成器代码（枚举 xyz_normal_xnum×ynum×znum 写 CSV）
U#29 「你修改这里的代码，使得xyz逻辑和sv一样」→ **produce 任务**（修改生成器让 xyz 枚举对齐 SV 逻辑）
U#30 「总结我们的对话」→ agent 输出十几轮核查总结

## 用户实际接受的结果

- `para_compare_dbcoa_v2.csv`（python vs SV 参数对比表，含 SV 源文件列）——U#5 后多次迭代
- `under2_behavioral_desc.sv`（under2 行为级 SV 描述）
- `gen_paralist_sv_aligned.py`（xyz 对齐 SV 的参数枚举器，agent 末尾报告「生成成功 4408 行 = 4336 实测 + 72 SV 逻辑尾部」）——U#29 produce 完成，用户未 reject，转 U#30 求总结 → 隐式接受

## 为何做 B-grade synthesized（不做 A-faithful）

- A 候选 U#0 的金标准 = 完整对比表，但 SV 源树庞大/私有（`/proj/dbcoa/.../regression/cyclic_xyz/` 含 rhr_driver.sv/rhr_parameter.pkg/...），无法在沙盒内复刻真值
- U#29 produce 的生成器对齐 SV xyz 逻辑——需要完整理解 SV 侧 z 反推算法，深度过高，单轮 40min 不可控
- **B 档主题迁移**：把 trace 核心发现「**Verilog parameter 声明但死引用 + 硬编码延时shadow**」抽成自包含单文件审计任务

## B-grade synthesized 设计

**候选** `vparam_audit.py <vfile> <out.json>`：解析单 Verilog 文件，输出 JSON：
- `params[]`：每个 `parameter`/`localparam` 声明 {name, value, line, refs(剔除声明行), classification(used/dead)}
- `hardcoded_delays[]`：所有 `#<num>` 字面量 {value, line, context}
- `value_shadows[]`：硬编码字面量值 == 某 param 值（提示「应改用 param」）{param, literal, delay_line, decl_line}
- `summary`：{n_params, n_dead, n_used, n_hardcoded_delays, n_value_shadows}

**A（可见）** `rhr_top_a.v`：10 params (2 dead: T_RFC_A, NOISE_A) / 8 used / 4 hardcoded_delays / 1 shadow (#860==OSC_T_A)
**隐藏 B** `rhr_top_b.v`：9 params (2 dead: tRFC_B, tRC_B) / 7 used / 5 hardcoded_delays / 1 shadow (#60==ACT_PERIOD_B) —— 名字/值/计数/结构全不同反硬编码

**判分** L2 subprocess 真跑候选于隐藏 B + 14 条 a-n 结构化字段断言（含特定 dead/used param 条目 + 特定 #11.52 delay context + 特定 shadow 链 + 反硬编码 A-only 名字不泄入 + 3-seed md5 一致）

## 与已有 case 非重复

- HierNetTrace（SPICE net 追踪）/ VconnConsistCheck（Verilog 模块例化端口连线比对）/ NetlistStructDiff（HSPICE 网表 diff）—— 本 case 操作维度 = **Verilog parameter 声明引用审计 + 硬编码延时 shadow 检测**，文件格式（单 .v + package）+ 操作（refs 计数/classification/value shadow）均不同
