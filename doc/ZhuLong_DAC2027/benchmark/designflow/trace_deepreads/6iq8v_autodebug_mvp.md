# Deepread: 1788229172489_6iq8v (wellesc@hfeg0pkn004, mc=716)

> r1640 候选开采 → 深读 → **parked (overlap)**

## 来源
- summary.tsv: `1788229172489_6iq8v` wellesc@hfeg0pkn004, mc=716, waveview:1203+netlist:1104+synopsys:67+hspice:66+mosfet:37 主导
- FRESH (4-shard 台账 4641 slug 无命中), D 域 waveform
- 与 hht3e(r1631)/6l1c8/1qva5 同属 wellesc **AutoDebug agent** 项目链 (6l1c8→6iq8v→…→hht3e)

## trace 体量
- 3.42MB, 1157 msgs (605 user / 552 assistant), model glm-5.2
- U#1 = 续作请求 ("读 6l1c8 上下文继续完成任务")

## 用户真实任务
wellesc 完成 **DRAM FineSim Fail Case AutoDebug MVP**（有 pass 参考端到端）:
对比 reference vs failing FSDB 波形(WaveView/fscript probe)，沿门级 netlist hierarchy fan-in 回溯找**最早分歧点**(源门=输入全 EQUIVALENT+输出 DIFFERENT)，LLM 根因分析→结构化报告。

## 核心组件 (msg#262 总结)
1. **waveview_adapter.py** — `wv -ace_no_gui` ACE Tcl 后端替代 fscript:
   - 多信号提取修复(WaveView `sx_signal {a}{b}{c}` 静默丢弃未找到信号→逐个获取句柄过滤空句柄统一导出)
   - 信号路径归一化 `_normalize_sig`(tbl header 把 `v(xi_channel.net92)` 重写成 `xi_channel.v(net92)`→还原)
   - **bare-name fallback 两轮提取**(根作用域网如 `aboi_flagdnsc0` 在 FSDB 以裸名存→先试完整路径, 未找到用裸名重试)
   - NFS 等待 + 随机时间戳避冲突
2. **comparator_tool.py** — backend 参数(waveview/direct_fscript/fscript); **空波形→NO_DATA**(原误判 EQUIVALENT 常量0V)
3. **netlist_indexer.py** — get_fanin 终端检测: 根作用域无内部驱动网加 `EARLIEST_DIVERGENCE_TERMINAL` note + `connected_instances`; 全 input 端口=最早分歧终端
4. **agent.py** — terminal nudge(get_fanin 返回 TERMINAL 时注入强力 nudge 让 LLM 立即出结论); 结论解析器支持 Markdown(`**field:**`/`- `/反引号)
5. **prompts.py** — 网络路径语义: upstream_nets 已是完整 FSDB 路径不要加 driver 前缀; 裸名=根作用域, 带点=内部网

## 关键用户痛点 (HU 序列)
- HU#11-12: `xi_array32gtop.abusbg0_sc0_0<0>` NO_DATA → bare-name fallback 复用 `abusbg0_sc0_0<0>` 数据 ✓
- HU#14: 同一 net 多 hierarchy 表示, FSDB 压缩到其一 → trace 到 NO_DATA hierarchy 须找等效裸名
- HU#15-16: trace 策略改 depth-first 到 std_cell 叶(TECHLIB/stdcells_am/decqa_stdcells 停), 再 fan-in 溯源
- HU#25: 到叶后仍需 fanin 找最早分歧
- HU#26-29(重复4×): **probe 窗口无数据=电平恒定, 须向前扫波形变化时间区间再继续追**
- msg#191: `xi_channel.net92` 常量信号(~24μV)仅 t=0/t=1003ns 有数据, 都在 838n-842n 窗外→NO_DATA(对 debug OK, 常量非分歧点)

## 与既有 case 的 overlap 判定 (parked 依据)
| 子任务 | 既有 case 覆盖 |
|---|---|
| hier trace / bare-name fallback / get_fanin / earliest_divergence / source_gate | **FsdbHierFaninTrace-001 (r1631 hht3e)** — spec 驱动 hier_fanin_tracer, fsdb_available+verdicts 在 spec 内给定, 17 conds 独立复算 |
| 波形 stable-window 聚类 / tr-tf 测量 / glitch 检测 / 低摆幅跳过 / 违例排序 | **FsdbTrTfGlitchExtract-001 (r1624 peemu)** — spec+tbl 驱动 fsdb_trtf_glitch, 13 conds |
| 空波形→NO_DATA 分类 / 多信号提取 / 信号路径归一化 | 属 WaveView 适配器实现细节, 强依赖真实 FSDB 二进制, 不易 spec 化 |
| **probe no-data → scan-forward 找变化区间** (HU#26-29) | 唯一未被覆盖的 distinct 角度, **但太薄**: 本质=1D 时间区间扫描, 与 FsdbTrTfGlitchExtract 的 stable-window 聚类+向前扫变化区间逻辑高度重叠; 单独造 ≥8 cond 独立 case 会与 r1624 重复 |

**结论**: 6iq8v 所有可合成子任务均被 hht3e/r1631 或 peemu/r1624 覆盖; 唯一 distinct 角度(scan-forward)不足以撑起独立 ≥8-cond case 而不与 r1624 重复。**parked**。

## r1640 候选池饱和观察
- summary.tsv(ssh_eda_search_20261128_014416) D 域 top80 (mc≥400) 仅 **6 fresh**, 全为 overlap:
  - wellesc AutoDebug 链: 6l1c8(mc780,netlist 主导,hht3e 前作)/6iq8v(mc716,本条)/1qva5(mc639,waveview)
  - e0048306 碎片化(=ci2w1 r1636 用户): i1k7x(mc475)/6ksw6(mc435)
  - e0020134(=trd1c r1635 用户): g5fp7(mc475)
- mc≥400 池已饱和; 下轮应采 **mc 50-400 mid-range + 新用户** 候选(r1637 找到 taodu/3690n, r1636 找到 e0048306/ci2w1 均为新用户 mid-range)
