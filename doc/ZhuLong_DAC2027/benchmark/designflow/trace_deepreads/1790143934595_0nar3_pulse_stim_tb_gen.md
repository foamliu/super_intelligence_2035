# trace deepread — 0nar3 (PulseStimTbGen-001)

- **trace**: `1790143934595_0nar3.messages.json` (qiong1w @ hfeg0plg101, mc=41, 36 msgs, 305KB)
- **keywords**: netlist:104; spectre:60; aether:18; schematic:16; pdk:11; hspice:5; pyaether:4
- **session**: zhulong/zl agent (`agent: lead`), agent-policy-engine enforcing (writableRoot=/home/qifanli/.cline/scripts/data)

## 用户轮（逐字原文，红线 #2 不脱敏）
1. `<user_input mode="act">` + 贴一段 Spectre 网表片段（switch_close / switch_open / .GLOBAL vcc! vss! / inv_20260922: XMMN0 OUT IN vss! vss! ntn w=150e-9 l=36e-9 / XMMP0 OUT IN vcc! vcc! ptn w=150e-9 l=36e-9）—— 环境探索轮（贴上下文，未提需求）。
2. **「add 1v pulse signal to the above inverter, pulse width 1us,period 2us,and transient simulation time 10us」** —— 真正需求轮（提出目标，未给根因/修复，符合 A 档选轮规则）。

## assistant 工具链（关键节点）
- msg1/3: agent 解析网表片段（识别 switch_close/switch_open/inv_20260922 inverter，ntn/ptn 模型，W=150nm L=36nm）。
- msg5-16: `list_allowed_files` 探 `/home/qifanli/simulation/qifanli/ldo_qifanli/sim_inv/platform/Results/PlatRun.1/ldo_qifanli_sim_inv_1/` 找既有 netlist/scs。
- msg17-22: `read_files` 读 `sim_inv.netlist`(Spectre, subckt switch_close/switch_open/inv_20260922) + `Nominal/sim_inv.scs`(top-level: include model.lib + include sim_inv.netlist + simulatorOptions + pulse Vin + tran) + runSimulation。
- msg23-32: **`editor` 写 inv_20260922_tb.scs + run_inv_20260922.scs** 到 `/home/qifanli/.cline/scripts/data/`（policy 限制，原 simdir 不可写）。testbench 含：simulator lang=spectre + switch subckts + inv_20260922 subckt + Vvcc (vcc! 0 1.2V) + Vss (vss! 0 0) + Vin pulse (IN 0 pulse(0 1V 0 1n 1n 1u 2u)) + Cload (OUT 0 1f) + X1 IN OUT vcc! vss! inv_20260922 + tran stop=10u。
- msg35: agent 给总结表（files created + stimulus params + how to run `alps -mdespectre ...`），**未真跑仿真**（只生成 deck）。
- **用户未明确接受结果**（无 acceptance turn）→ 本 trace 无干净 acceptance 点 → 取 **B 档 synthesized**（子技能忠实于用户需求，金标准由我方在 .75 上标定）。

## 子技能（可移植化）
**subckt DUT + 脉冲激励 spec → 完整瞬态 testbench deck 生成器**（name-agnostic，pulse vsource + supply vsource + enable-bias vsource + load cap + DUT 实例化 + .tran + .measure vhigh/vlow/period）。
便携化：trace 原 Spectre .scs + foundry PDK(ntn/ptn) 不可便携 .75（无 Spectre）→ 取 HSPICE .sp + level-1 Shichman-Hodges MOS（nsub=1e16 u0=600 tpg=1 防 nsub<=ni abort，已验证）。候选只 GENERATES deck（忠实 trace：用户只要求"add pulse + tran"），judge 独立 rerun HSPICE = anti-fake rerun guard（同 NocalOffsetDeck 模式）。

## distinct vs 已有 B spice_sim case
NetlistTranDeck(j8vf6)=网表+.measure 静态拼接(无 spec-driven pulse 生成)·StimPWL=PWL from waveform(非参数化 pulse spec)·Vcc2scTranGen=vcc2sc 特定拓扑·CmdEdgeMeasGen=.measure deck(无 stimulus 生成)·StimLoopComplianceFix=stimulus loop 合规修复·Tr0TrTfMeas=tr/tf 测量·InvTripDelay=inverter trip+delay(给定 deck)·NocalOffsetDeck=calibration control rewrite —— 本条=**spec-driven 参数化 pulse stimulus testbench deck 生成器(多输入门 enable-bias trap + name-agnostic 跨 DUT)**，shard B 首个「pulse-stimulus testbench generator」case，distinct ✓。

## trap（关键）
多输入门(NAND2)的「使能输入必须 DC 偏置」陷阱：NAND2 输入 b 必须 tied vdd 才能让 a 上的脉冲在 out 上翻转；若候选把 b 接 0 或悬空 → out 恒高(NAND2 b=0⇒out=1)，period/vhigh/vlow 全错。反 naive_no_enable。

## 金标准（.75 HSPICE V-2023.12-SP1-1 标定，待实测）
- A (inv_a 单输入, vdd=1.2, pulse 1.2V width=1us period=2us tran=10us, load=1f): out 翻转 0↔1.2, vhigh≈1.2, vlow≈0, period=2us
- B (nand2_b 双输入, vdd=1.5, pulse 1.5V width=0.5us period=1us tran=5us, load=2f, **enable b=vdd**): out 翻转, vhigh≈1.5, vlow≈0, period=1us
- 跨输入：拓扑(inv vs NAND2)/vdd(1.2 vs 1.5)/pulse(1us/2us/10us vs 0.5us/1us/5us)/enable(无 vs b=vdd)/load(1f vs 2f)/model(nmos vs nmosb)/vto(0.7 vs 0.6) 全不同 ✓
