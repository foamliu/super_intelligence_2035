# 深读笔记 · qcuvw (alexcui @ hfeg0plg09, mc=86, spice_sim)

**session**: 1795057341901_qcuvw.messages.json (44 msgs, 10 user turns)
**trace_source**: 11/20 reconstructed snapshot; B-kw fresh, 4-shard ledger clean.
**scan**: ssh_eda_search_20261121_005100/summary.tsv → summary_1120_reconstructed.tsv

## 用户真实意图（主线交付）
alexcui 在做 Bandgap_chx 的 VerilogA 仿真（Spectre 23.10.305），需要写一个三相非交叠时钟
发生器 `clk_nonoverlap_3phase`，给 Bandgap 电路提供时钟。10 条 user 消息的主线演进：

- **U[0]** (原话): "wirte a verilogA code for clock signal phi2 160ns period phi1 80ns period
  phi0 80ns period all non-overlap" — 3 个非交叠时钟：phi2(160ns)、phi1(80ns)、phi0(80ns)。
- **U[12]**: 贴出 Spectre AHDL compile 报错：① VACOMP-1147 `$realtime` 非便携 → 改 `$abstime`；
  ② VACOMP-2143 `transition()` 嵌在 if/else 条件语句里不支持 → 必须先把值算好，再在
  **无条件**贡献语句里调一次 `transition()`。
- **U[20]** (原话): "for phi2 build another signal name phi2E it is <7:0> that means when first
  rise of phi2 comes so it phi2E<0> and when it falls so it phi2E<0> when the second rise of
  phi2 comes so is phi2E<1> so on and so on until phi2E<7> then it is phi2E<0>again also make
  it the same stragy of phi0 the signal is phi0<7:0>" — 加两条 8-bit 旋转总线 phi2E[7:0] /
  phi0E[7:0]：每个 phi2/phi0 上升沿推进到下一 bit，active bit 跟随父时钟脉冲，到 [7] 后
  回 [0]。
- **U[32]**: 贴出第二轮 Spectre 报错：① VACOMP-1192 `V(phi2E[i])` 用变量下标访问 analog
  signal vector 不支持 → 必须用常量下标；② VACOMP-2143/2384/2439 `transition()`/contribution
  嵌在 for 循环 / initial_step 块里不支持 → 16 个 bit 必须全部展开成显式常量下标语句。
- **U[38..43]**: 用户把最终修正版代码反复贴回（确认/再迭代），末条为 plan 模式。

## 真实交付物
`clk_nonoverlap_3phase.va` — Spectre-compliant VerilogA 模块，含：
- 3 个标量非交叠时钟输出：phi2(period_phi2=160ns)、phi1(period_phi1=80ns)、phi0(period_phi0=80ns)
- 2 条 8-bit 旋转总线输出：phi2E[7:0]（每个 phi2 上升沿推进 active bit）、phi0E[7:0]（同策略，
  每个 phi0 上升沿推进）
- 参数：period_phi2/phi1/phi0、pw_phi2、pw、non_overlap、vhigh、vlow（全 `parameter real`）
- Spectre 合规：`$abstime`（非 `$realtime`）；`transition()` 全部在 analog 块顶层无条件
  调用（先在 if/else 里算好 *_val，再 `V(x) <+ transition(val, 0, tr, tf)` 一次）；16 个 bus
  bit 全部用常量下标 `V(phi2E[0])..V(phi2E[7])`、`V(phi0E[0])..V(phi0E[7])` 显式展开（无 for
  循环包 contribution、无变量下标）。

## 非交叠时序（参数化 spec）
frame = period_phi2；sub = period_phi1 = period_phi0（trace 中 = frame/2）。每 frame 内：
- phi2: [0, pw_phi2)
- phi1 #1: [pw_phi2+non_overlap, +pw)
- phi0 #1: [pw_phi2+2*non_overlap+pw, +2pw)  (即 ...+2*non_overlap+2*pw)
- phi1 #2: [sub+non_overlap, +pw)
- phi0 #2: [sub+2*non_overlap+pw, +2pw)
约束: pw_phi2+2*non_overlap+2*pw <= sub；sub+2*non_overlap+2*pw+non_overlap <= frame。
trace 默认 (pw_phi2=30,pw=15,non_overlap=5,sub=80,frame=160) 全部满足。

## 旋转总线 spec
- phi2E: cycle c = floor(t/frame)；active = c mod 8；phi2E[active] 跟随 phi2 脉冲（phi2 高时高），
  其余 bit 恒低。8 frame 一轮。
- phi0E: cycle c = floor(t/sub)（phi0 每 sub 一脉冲）；active = c mod 8；phi0E[active] 跟随 phi0
  脉冲。8 sub 一轮。

## 造题方向（A-faithful intent, B-synthesized deliverable form for checkability）
真实交付是 .va 文件本身。为给 check() 装牙（隐藏 B 参数化 + 真跑候选逻辑），要求 SUT 交付
Python 生成器 `clk_va_gen.py`：① CLI 接受参数 config → 喷出 clk_nonoverlap_3phase.va；
② 暴露 `simulate(params)->dict` 返回波形（与 .va 逻辑一致）。check 用隐藏 B 参数跑生成器 +
调用 simulate(B) 与独立参考模型比对（periods/non-overlap/rotating-bus）+ 静态验 .va 的
Spectre 合规与参数化（anti-hardcode-A：B 参数 ≠ A，硬编码 A 字面量则 B 波形错）。

## 域匹配
spice_sim（VerilogA 行为级建模，Spectre 仿真用）。alexcui 新用户，4-shard ledger fresh。
非 near-dup（既有 B case 无 VerilogA 时钟发生器/旋转总线主题）。
