# 深读笔记 — b1w28 (tongfanl@10.129.35.69, mc143, n=222)

- session: 1791796775106_b1w28.messages.json (2.49MB, 222 msgs)
- domain: schematic_netlist (verilog sim-vector write-task DQ->PSD mapping)
- shard: D

## U#0（逐字原文，4 次重复同一句）
> /proj/dscqa/V0/setup/sim/sim_vector/verilog.ddr6.dscqa.vecgen_local，帮我整理一个表格，当没有定义DQSEL_LH时，write task中的传入参数和PSD0DQ[5:0]、PSD1DQ[5:0]的mapping关系，分成1P12、1P6、2P6、2P3.分别说明。

A-faithful 判定：✅ 纯提需求（整理 mapping 表），🚫 未给根因/修复。U#0=本 prompt。

## trace 演化（assistant 工具链）
- list_allowed_files /proj/dscqa/.../verilog.ddr6.dscqa.vecgen_local → read ddr6_tasks.sv / ddr6_genvector.sv
- search_codebase: PSD0DQ/PSD1DQ/DQSEL_LH/1P12/1P6/2P6/2P3/write task
- read ddr6_test.sv 多段（line 539/810/995/1064/1262/1500/1800/2000/2500/3200/4400/9500/10000...）
- 定位 `task Write(...)` @ ddr6_test.sv:839，签名 `task Write(reg[BG_BITS-1:0] bg, reg[BK_BITS-1:0] ba, reg[COL_ADDR_BITS-1:0] col, bit ae_psd=0, reg[MAX_DQ_BITS-1:0] dq='0, bit ap=0, bit termit=0, ...)`
  - MAX_DQ_BITS=144（非 X1P12：24 bursts × 6 DQ bits）/ 288（X1P12：24 bursts × 12 DQ bits）
- 找到 `wr_reorganize_dq` / genvector 中 dq_burst[5:0] -> PSD0DQ/PSD1DQ 的逐 burst 赋值（按 prefetch mode ifdef 分支）
- #90 出第一版「综合映射总结表」（!DQSEL_LH 分 PSD0/PSD1 per burst per mode）

## 后续轮（不进 prompt，记录演化）
- U#91: 「未定义 DQSEL_LH且定义DQSELH时...二者放在一起」→ #102 出 Case A(!DQSEL_LH & !DQSELH) vs Case B(!DQSEL_LH & DQSELH) 对比表
- U#103: 「MRSetting psd_mr=0 访问 PSD0？会因主 PSD 变化而变？」→ search MRSetting/psd_mr（Q&A，非本 prompt）

## 真实产物
- Markdown 表：dq_burst[5:0] -> PSD0DQ[5:0]/PSD1DQ[5:0] per burst per prefetch mode（1P12/1P6/2P6/2P3），条件 !DQSEL_LH

## 资产可附加性
- 🚫 真实 /proj/dscqa/.../vecgen_local 目录不可附加（多文件 + /proj 权限/路径）
- → **B-grade synthesized**：合成一个 `write_task_A.sv`，忠实 mimicking Write task 结构（input [5:0] dq_b* 参数 + `ifndef DQSEL_LH` 包裹 + 4 个 `ifdef <mode>` 分支内 PSD0DQ/PSD1DQ 赋值，含 concat 位切片），金标 = 通用 verilog parser 提取 param->PSD bit 映射表 JSON

## 金标 & check 设计
- 金标 psd_mapping_ref.py：解析 verilog → 找 `task Write`→提 input params→在 `ifndef DQSEL_LH` true 分支内找每个 `ifdef <mode>` 块→提 PSD0DQ/PSD1DQ 赋值 RHS（单切片 p[msb:lsb] 或 concat {p1[a:b],p2[c:d],...}）→JSON{task,condition,params,psd_width,modes{mode:{PSD0DQ:[slices],PSD1DQ:[slices]}}}
- 隐藏 B: write_task_B.sv 不同 param 名(d0..d4 5 个)、不同位切片组合、不同 task 内 `ifndef DQSEL_LH/else` decoy（else 分支 decoy 赋值须被忽略）
- check 14 条件 a-n（含 anti-hardcode A 重跑 + A-only token 检 + DQSEL_LH decoy + 确定性）

## 教训
- 真实 ddr6 mapping 极复杂（24 burst/144bit/多 PSD），合成版简化为 4-5 param × 6-bit PSD 保留「param->PSD bit 映射 per mode」语义核心
- `ifndef DQSEL_LH` + `else` decoy 是判分关键：测候选是否正确 scope（不只 grep PSD0DQ=）
