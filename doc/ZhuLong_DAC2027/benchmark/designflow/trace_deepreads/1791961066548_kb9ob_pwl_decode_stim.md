# Deepread — 1791961066548_kb9ob (junlingw @ hfeg0plg99)

**Round**: D #523 | **Claimed**: 2026-11-11 | **mc**: 11 | **Domain**: schematic_netlist/waveform

## Trace Source
- **User**: junlingw (fresh — not in D.jsonl 155 users)
- **Host**: hfeg0plg99
- **Session**: 1791961066548_kb9ob (31 messages, 119KB)
- **Keywords**: netlist:46;analog:16;spectre:8;pyaether:5;hspice:3;cadence:3;synopsys:2;pex:2

## Task Summary (real)

junlingw 在做 DRAM rdlatency 外部激励（stimulus）调试，涉及两个子任务：

### 子任务 1: PWL 译码激励生成 (U#1, U#16, U#18, A#17, A#19)
- **背景**: `clmnm8<5:0>` 共 6 个激励，做 shift TCK 的译码。译码结果看 700ns 后各 bit 的稳态电平。
- **输入**: 用户粘贴了 `clmnm8<5>` 的 PWL 波形（"0" bit 模板），对应译码 `000101` = 5tck。
  - 5tck 6 位译码: b5=0 b4=0 b3=0 b2=1 b1=0 b0=1
  - clmnm8<5> (MSB) 700ns 后为 0，与 b5=0 一致
- **目标**: 生成 **1tck (000001)** 译码激励:
  - 除了 clmnm8<0> 在 700ns 后为高(1)外，其余 clmnm8<5:1> 均为低(0)
- **补充约束** (U#18): 逻辑 1 = 1.0V
- **助手方案** (A#19):
  - 5 个低 bit (decode=0) 复用模板波形 (只改网名)
  - clmnm8<0> (decode=1) 取模板上升沿，scale 到 1.0V 并保持
  - scale factor = VDD / template_peak ≈ 1.0/0.804 ≈ 1.244

### 子任务 2: .inc vs .option finesim_spf 语义 (U#22-30)
- 用户问 "inc网表再option spfrcc 和 直接inc spfrcc 有什么区别"
- 实际网表: `.option finesim_spf='.../IO_OdtCtrl.spf_RCC'` (Finesim SPF 寄生反标) vs `.inc '.../IO_OdtCtrl.spf_RCC'`
- 助手解释: `option finesim_spf=` 让 Finesim 专门按 SPF 寄生文件解析+反标; 直接 `.inc` 把 SPF 当普通 SPICE 网表插入，不做 SPF 专属处理

## Case Synthesis Decision

**选用子任务 1** (PWL 译码激励生成) — 原因:
- 有具体 I/O (模板 PWL → 6 路 PWL 输出)
- 转换规则清晰可验证 (bit mapping + voltage scaling)
- 自包含 (PWL 数据 inline，不依赖 /proj 路径)
- 可独立 oracle 验证 (V_peak, scale factor, bit assignment)

**放弃子任务 2** — 原因: 纯解释性 Q&A，难以转为 ≥8 条独立代码断言

## Synthesized Case Design

- **Case ID**: EDA-Eval-DesignFlow-PwlDecodeStimGen-001
- **Domain**: schematic_netlist
- **Difficulty**: L2
- **k_check**: 12

### 核心规则
1. 输入: 模板 PWL (非负，代表 "0" bit 的 analog 脉冲形状) + VDD + 6-bit decode
2. V_peak = max(template values)
3. scale = VDD / V_peak
4. decode[i]=1 → PWL values = template * scale (峰值 = VDD)
5. decode[i]=0 → PWL values = template verbatim
6. bit mapping: decode[0]=LSB=clmnm8<0>, decode[5]=MSB=clmnm8<5>
7. 输出: stim_output.sp (6 个 Vclmnm8<i> PWL 源) + stim_summary.json

### A/B/C 三路 (不相交)
- A (public): decode=000101 (5tck), VDD=1.0V, 13-point pulse template
- B (hidden): decode=000011 (3tck), VDD=1.2V, 15-point different template
- C (embedded anti-hardcode): decode=000110 (6tck), VDD=0.9V, 11-point template

## Self-Verify Checklist
- [ ] ref_sut PASS on A, B, C
- [ ] k_rationale == k_check == 12 ≥ 8
- [ ] §4.9 three false-submit FAIL (empty_shell, print_only, hardcode_a, core_deleted)
- [ ] negative_selftest all FAIL
- [ ] 3-seed sha256 consistent
- [ ] jsonl round-trip
