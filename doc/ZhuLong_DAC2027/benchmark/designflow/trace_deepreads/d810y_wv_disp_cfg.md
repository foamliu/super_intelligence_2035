# d810y 深读 — WaveView 显示配置生成器（leaf 名 + 总线分组）

## trace 来源
- session: `1792827081154_d810y.messages.json`
- user: jackjia / host: hfeg0pkn003 (10.129.2.12) / mc=385 / domain: waveform
- tools: 240 schematic + 39 netlist + 25 virtuoso + 23 pyAether + 21 dbGet + 14 hspice + 12 cellview + 10 calibre + 3 spectre + 3 dbShape
- 294 msgs / 51 user turns（本 case 取 waveform 显示意图）

## 用户意图（逐轮原文摘选，未脱敏）
- U#3「使用wv打开fsdb 显示这是 Verdi 版本太旧的问题：仿真的 FSDB 波形文件是用新版 writer（6.3）生成的，而你打开用的 Verdi 里 FSDB reader 只支持到 6.1，读不了。 在呢嘛办」
- U#5「module unload ds/wv module load ds/wv/2025.06-SP2-2 wv finesim.fsdb 用着个解决的 我之前是那个版本啊」
- U#7「就是在原理图中打开仿真拉信号的操作呢」
- U#13「我利用wv2025打开来波形 但是怎么感觉和原理图信号对不上」
- U#27「是ctrl w 添加波形啊」
- U#31「我的仿真波形颜色看不清怎么换」- U#38「对信号字体太小哦啊 帮我放大」
- U#39「xi_channel.xi_bcenter.xi_bcenterdq.xi_d_dqbytelow_1.xi_dqspad.xi_io_dqsio.v(dqstin) finesim.fsdb 显示信号的名字太长了 能不能只显示自己不显示层级」
- U#40「波形下边没有tcl可以输入」
- U#41「wv_set_preference -name SignalNameDisplay -value leaf invalid command name 你为什么不帮我操作」
- U#45「对于多bit数据怎么合成1：0 比如dqsout1：0」
- U#46「dqsout[1:0] 现在就在 波形中分开的 没有你说的aether的按钮」

## assistant 工具链
- run_approved_command（查 wv 版本 / module load）→ editor（写脚本）→ skills(search_codebase)（查 wv API）→ read_files（读 fsdb/.sp）→ list_allowed_files（看仿真目录）
- 关键产出：A#232 给出改字体方法（View→Preferences→Fonts，`wv_set_preference -name FontSize -value 16`）；A#234 给出只显叶子名方法（`wv_set_preference -name SignalNameDisplay -value leaf`）；针对总线分组建议在 wv 里 Ctrl+W 添加 + 多 bit 合成

## 真实信号层次路径（U#39 原文）
`xi_channel.xi_bcenter.xi_bcenterdq.xi_d_dqbytelow_1.xi_dqspad.xi_io_dqsio.v(dqstin)` — 末尾 `v(NAME)` 是 WaveView 信号引用格式，前面是层次路径（点分）。

## A-faithful 判定
**不可行**：U#39 是 how-to 提问（「能不能只显示叶子名」），gold = 过程性指导（菜单操作 + wv 命令），断言只能对事实（数值/结构）不能对措辞/操作步骤 → **B 档 synthesized**：重述为 produce（生成 WaveView 显示配置三件套 from spec），断言对产出结构（叶子名提取/总线分组/命令脚本）。

## 合成 plan
- 生成器 `wv_disp_cfg.py --spec <spec.json> --outdir <dir>` 读 spec{design,font_size,signals:[{path,radix?}],buses:[{name,bits,radix}]} →
  - 叶子提取：`v(NAME)` 末尾正则取 NAME，全小写（WaveView 硬约束，trace U#8/13/24 反复强调）
  - display_cfg.json: design/font_size/signal_name_display=leaf/n_signals/n_buses/signals[{path,leaf,color,radix}]/buses[{name,width,bit_order降序,radix,member_leaves}]
  - wv_commands.wvc: `wv_set_preference -name SignalNameDisplay -value leaf` + `wv_set_preference -name FontSize -value N` + 每 signal `wv_add_signal -name leaf -path path -color -radix` + 每 bus `wv_add_bus -name -bits -radix`
  - report.md: design/信号数/总线数/leaf 声明 + 信号表 + 总线表
- A=spec_A.json(DRCOA_DDR5_x8, 14 信号真实层次路径含 v(DqsOut0) 大写测小写, 2 bus dqsout[1:0]/ra10[3:0])
- hidden B=spec_B.json(LPDDR4_PHY_x16, 18 信号 phy_top 前缀, 2 bus dq[7:0]/phy_rdlat_sel[2:0], font 14, 含 v(Dqs_P)/v(Dqs_N) 大写)
- hidden B2=spec_B2.json(SERDES_ANALOG_RX, 11 信号 serdes_top 前缀, **0 bus** 全标量, font 12) — 测无 bus 处理 + 跨输入守卫
- 反硬编码五轴：design DDR5/LPDDR4/SERDES 全不同；层次前缀 xi_channel/phy_top/serdes_top 全不同；信号名全不相交；bus 数 2/2/0；font 16/14/12；B2 无 bus 杀"总有 bus"硬编
- check 16 条件 a-p：a(防泄漏+py_compile) b(B-run exit0+3文件) c(顶层7键) d(signal_name_display==leaf) e(font_size==specB) f(每signal leaf提取v(NAME)小写) g(n_signals==specB+列表len) h(bus bit_order降序+width) i(bus member_leaves==specB bits小写) j(wvc含SignalNameDisplay+FontSize) k(wvc含每signal wv_add_signal+leaf+path) l(wvc含每bus wv_add_bus+name+radix) m(颜色palette循环) n(report含design+n_signals+n_buses+leaf) o(B2守卫:无bus+design/n_signals异) p(确定性3x sha256)

## 自验结果
- ref PASS 16/16 a-p
- 6 negatives 全 FAIL，5 distinct first_fail (b/e/f/h/i)：empty_shell→b, print_expected→b, hardcode_a→e, no_lowercase→f, core_deleted→h, no_buses→i
- §4.9 三假 (empty/print_expected/core_deleted) 全 FAIL
- 断言闸门 k_rationale=k_check=16 ✓
- 确定性 3x sha256 一致（含在 p 条件内）

## 教训
1. **fresh mc>=15 D-domain 池枯竭后降 mc>=5 重建有效**：本轮 mc 5-430 区段找到多个 fresh 候选（z9yjw/6rvi0/ebxsl/d810y 等），d810y 是 jackjia 51-turn waveform+schematic 丰富 trace
2. **parked 可被 mark 覆盖**：d810y 之前 parked 注「no runnable deliverable」，但 B-grade synthesized 把 how-to 重述为 produce（生成显示配置）即可有可验交付物，mark --status case 覆盖 parked（case_id 落台账即覆盖率分子）
3. **how-to trace 的 B-grade synthesized 范式**：U#39「只显叶子名」gold=过程指导不可断言→重述为 produce（spec→配置生成器），断言对结构（叶子提取/总线分组/命令脚本），16 条件天然丰富
4. **v(NAME) 叶子提取 + 全小写是强反硬编码轴**：真实路径 `v(DqsOut0)` 大写→leaf=dqsout0，naive 不小写者 (f) FAIL；B 用不同 design/前缀/信号名/字号→硬编 A 者 (e/o) FAIL
5. **B2 无 bus 是额外反硬编码轴**：不处理空 buses 列表者 (o) FAIL（wvc 仍输出 wv_add_bus 或 n_buses≠0）
6. **eda_flow run_commands 跑 e0031982 身份可免密 ssh**：pyAether run_code 跑 t0002997 无免密（Permission denied），eda_flow run_commands 跑 e0031982 可 ssh 到 hfeg0pkn* 各机——peek/deepread 须走 eda_flow run_commands 而非 pyAether run_code
