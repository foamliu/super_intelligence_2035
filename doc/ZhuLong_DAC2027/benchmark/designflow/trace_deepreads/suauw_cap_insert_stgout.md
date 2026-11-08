# 深读笔记 · suauw · cap_insert_stgout

- **session**: 1793932002608_suauw.messages.json
- **user/host**: jiangbaol @ hfeg0pkn001 (mc=290, netlist:112/hspice:94/schematic)
- **domain**: schematic_netlist (SPICE testbench 编辑)
- **claim**: 2026-11-09 07:07, schematic_netlist

## 用户轮（5 轮，逐字原文）
- U#1: `/proj/dscqa/V0_LP6/.../004_onlySlicer_delay_dejoa_test_cm.sp` 该.sp已添加了共模电流与共模电压，在此基础上添加差模电流及差模电压
- U#2: compact
- **U#3（目标轮，提需求/表达目标，未指出根因、未给修复方案）**: `/proj/dscqa/V0_LP6/.../004_onlySlicer_delay_dejoa_test_cmdm.sp` 帮我在这个.sp中比较器out_stg1两端添加电容，value设置为参数，在.paramter中定义该值，生成的结果以新.sp形式呈现
- U#4: 降低 block:DqIb_strongarm_pmos 中 M17,MP0,MN23,MN5 阈值电压 0.1mV（不同任务）

## U#3 assistant 工具链 + 产物（gold）
1. read_files 读 .sp（/rundata/dscqa/... 私有路径，本机不可读 → DEBT④，B-grade synthesized）
2. 定位比较器实例层级路径：`XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outp_stg1` / `outn_stg1`（顶层 strongarm 实例 → 内部 DqIbSADoubleTailM6 实例 → stage-1 差分输出端口）
3. 定位 .param 块末尾（line 63，`.param cthin` 之后）+ 定位 `.end`（line 313）
4. 生成新文件 `004_onlySlicer_delay_dejoa_test_capout1.sp`（312→318 行，**不覆盖原文件**）：
   - 插入 `.param Cout_stg1 = 1f`（在原 .param 块末尾之后）
   - 在 `.end` 前插入：
     ```
     * ---- Output caps on out_stg1 (differential load) ----
     * value parameterized by Cout_stg1 (defined in .param)
     Coutp_stg1  XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outp_stg1  vss!  'Cout_stg1'
     Coutn_stg1  XI_dqib_2stg_dfem6v2_strongarm_1.xi_dqibsadoubletail_12.outn_stg1  vss!  'Cout_stg1'
     ```
5. 验证：Cout_stg1 出现 4 次；两个电容对称（各从差分端到地 vss!，值引用参数 `Cout_stg1`）

## 关键技术点（合成 case 复刻要点）
- **比较器 out_stg1 两端** = StrongArm 双尾比较器（DqIbSADoubleTailM6）的 stage-1 差分输出端口 outp_stg1 / outn_stg1，经两层实例层级访问
- **添加电容** = 在两端各接一个到地电容（对称差分负载），不是单个跨接电容
- **value 参数化** = 电容值引用 `.param` 定义的参数名（HSPICE 单引号 `'param'` 包裹）
- **新 .sp 形式呈现** = 写新文件不覆盖原文件
- **陷阱**：`.end`（仿真结束）vs `.ends`（子电路结束）vs `.endl`（.alter 块结束）— 电容块必须插在顶层 `.end` 前，不能插在 `.endl` 前或 `.subckt` 内；`.param` 必须插在顶层 .param 块，不能插进 `.subckt` 内

## A/B 设计
- **A**（SUT 可见）: `slice_cap_A.sp` — 两层层级（XI7 → XIsa_0 → SADoubleTailA.outp_stg1/outn_stg1），.param 块含 delvto/cthin/VVDD，.global 含 vss!/gnd!/vcc!，含 .alter/.endl 块（陷阱）
- **隐藏 B**: `slice_cap_B.sp` — **一层层级**（XIcmp_0 → SADoubleTailB.sa_outp/sa_outn，直接顶层实例化），不同 subckt/实例/端口/参数名/值/地网，迫使候选泛化层级深度与命名
- 候选 `cap_inserter.py --input --output --subckt --net-pos --net-neg --cap-param --cap-value --ground`：解析 .sp subckt/X 实例 → 解析目标 subckt 的层级实例链到顶层 → 拼全路径 → 顶层 .param 块插参数 → 顶层 .end 前插电容块 → 写新文件
