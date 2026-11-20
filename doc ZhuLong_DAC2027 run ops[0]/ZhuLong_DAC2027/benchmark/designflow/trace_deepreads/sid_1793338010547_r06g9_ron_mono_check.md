# Deepread — sid 1793338010547_r06g9 (clarawu RON 单调性检查 + 电路优化)

- trace_source: user=clarawu, host=hfeg0pkn004 (10.129.2.13), session=1793338010547_r06g9.messages.json, match_count=461, mc keywords=hspice:2091/netlist:1761/pdk:1737/synopsys:458/schematic:315, tools col=`2089 hspice 1739 netlist 315 schematic`, spice_ratio=0.504
- N=607 msgs; agent cline lead; tool-use: editor:136, run_approved_command:120, read_files:36, list_allowed_files:9, search_codebase:4
- 真实输入 .md0 文件（FineSimPro V-2023.12-1 测量输出）位于 `/home/clarawu/sim_iter/v5_all/`: v5.md0, v5#1.md0..v5#4.md0 (5 corners, 各 ~21KB, 64 data rows)

## USER#0 原文（A-档任务说明，唯一意图轮 — 用户只给目标，不给根因/修复）
`检查刚仿真出来的RON曲线：@/home/clarawu/sim_iter/v5_all/v5.md0、v5#1.md0、v5#2.md0、v5#3.md0、v5#4.md0，rpd_50随zqcode变化的单调性，如果不单调，就优化电路`
> 选轮理由：用户提出需求（检查 RON 曲线 rpd_50 随 zqcode 的单调性，不单调则优化电路），未指出根因/未给修复方案。符合 A-档 ①.2。后续轮 (U@85 学习参考 stim、U@187 mismatch<4%、U@326 线性+mismatch、U@568 L=30nm 等) 是迭代优化目标，不进 prompt。

## .md0 文件格式（真实 FineSimPro 输出）
- Line1: `$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=7`
- Line2: `.TITLE '...'`
- Line3 (列头): `index zq5 zq4 zq3 zq2 zq1 zq0 zqdec rpu_20 rpu_50 rpu_75 rpd_20 rpd_50 rpd_75 rpu_lin20 rpu_lin50 rpu_lin75 rpd_lin20 rpd_lin50 rpd_lin75 temper alter#`
- 数据行: 每行 = 一个 zqcode 设置；`zqdec`=十进制码(0..63)，`rpd_50`=PD 端 50% 点 on-resistance(Ω)
- 5 个 corner: v5(temper=25,alter#=1), v5s1(-40,2), v5s2(110,3), v5s3(-40,4), v5s4(110,5)

## 金标准（trace 末尾用户实际接受的结果 + 工具真实产物，人工复核）
rpd_50 应随 zqdec 单调递减（更多 PD 器件导通 → 电阻下降）。实际 5 个 corner **均非单调**，各有 **3 处违反**，发生在主 bit 边界 zqdec 跳变处:
| corner | rpd50@zq0 | rpd50@zq63 | min | max | 违反 transitions (from→to, Δrpd50↑) |
|---|---|---|---|---|---|
| v5(25°) | 296.37 | 122.8 | 122.8 | 296.37 | 15→16(+5.67), 31→32(+21.14), 47→48(+2.56) |
| v5s1(-40°) | 250.04 | 99.694 | 99.694 | 250.04 | 15→16(+3.90), 31→32(+18.38), 47→48(+1.63) |
| v5s2(110°) | 271.08 | 108.96 | 108.96 | 271.08 | 15→16(+3.35), 31→32(+19.21), 47→48(+1.42) |
| v5s3(-40°) | 341.98 | 147.51 | 147.51 | 341.98 | 15→16(+9.11), 31→32(+23.80), 47→48(+4.40) |
| v5s4(110°) | 367.84 | 160.56 | 160.56 | 367.84 | 15→16(+10.43), 31→32(+25.72), 47→48(+5.02) |
- 31→32 是最大违反（zq5 主 bit 翻转，PD 主支路接入电阻跳变大）
- 用户后续 607 轮迭代优化电路（mismatch<4%、L=30nm 不动、PU 单调性），最终接受带 `_main` 常开主开关 + 串联堆叠码位管的拓扑（见末条 assistant 解释 XMN_pdzq0/_main）

## case 合成（EDA-Eval-DesignFlow-RonMonoCheck-001，characterization A-faithful L1/L2）
- prompt = USER#0 原文逐字（A-档，不脱敏；@路径保留原值）
- assets A (可见) = 5 个真实 .md0 文件 verbatim
- hidden B = 5 个同格式合成 .md0：zqdec 0..63，rpd_50 用不同 scale（~80-200Ω），注入 **4 处违反** 在不同 transitions {7→8, 23→24, 39→40, 55→56}（≠ A 的 3 处 {15→16,31→32,47→48}），强制真解析防硬编码
- reference = `ron_monotonic_check.py`（解析 .md0 列头 + 数据行 → rpd_50 vs zqdec 序列 → 单调递减检查 → JSON 报告）
- check.py k=15 断言：zip 入口/py_compile/exit0+JSON/8 字段全/n_rows==64/zqdec_range[0,63]/rpd50_first 匹配 B 实际(≠A 296.37)/rpd50_last 匹配 B(≠A 122.8)/n_violations==B 实际(4≠3)/violations transitions 集合匹配 B{7→8,23→24,39→40,55→56}(≠A)/每条 delta>0/rpd50_min/max 匹配 B/跨输入 guard(B 输出不含 A 专属 token)/确定性(3 seed 一致)/§4.9 三假提交全 FAIL
- 判分：candidate script 经 subprocess 在 hidden B 上真跑，独立解析 hidden_manifest 取 expected，逐字段比对；B 与 A 在规模/取值/违反结构上均不同

## 选 trace 理由
- A-档 clean 目标轮（USER#0 只给"检查单调性+不单调则优化"目标，不给答案）
- characterization 域（RON on-resistance 曲线分析），spice 主导 (hspice 2089/4143=50%)
- 真 FineSimPro .md0 测量文件，自包含可判分（解析+单调性检查，确定性）
- clarawu 用户 diversify（前 case 多为 ronghu/xinqiaoz/tongni）
