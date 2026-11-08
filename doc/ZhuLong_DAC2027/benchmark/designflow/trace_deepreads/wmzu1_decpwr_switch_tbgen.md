# 深读笔记 · wmzu1 · dsgao@hfhds234 · GrDecPwr 开关 ACT/PRE 上下拉测试台生成

- **trace_source**: user=dsgao, host=hfhds234, session_file=1793935013447_wmzu1.messages.json, mc=1429 (scan3 D-domain: netlist:265 schematic:186 hspice:19 calibre:10 cellview:6), real_task_summary 见下
- **会话规模**: 228 msgs, 762KB messages.json, 模型 glm-5.1-cloud (dir-based 存储 /home/dsgao/.cline/data/sessions/1793935013447_wmzu1/)

## 真实任务（用户原话逐轮）

- USER#0: `@/proj/drcpa/V0/workdir/dsgao/R_GidlAryCtrl_switch.netlist 这个电路有什么`
- USER#1: `在电路 正常 ACT 和 PRE 时，对GRDECPWR 的影响`
- USER#2: `现在我有一个secHV激励 上升沿是act,下降沿是pre,怎么做逻辑可以仿真看到 GrDecPwr 的上拉和下拉的过程中的电位变化`
- USER#3: `用nand将 SecHv 和 cm1_sw_total / cm1sw 做 逻辑 来 模仿 ACT 和 pre 时候 GrDecPWR 的变化`
- USER#4: `cm1_sw_total / cm1sw 在开关有效窗口内是高电平，且是恒定的`（约束确认：cm1 恒定高 → NAND 退化为 NOT(SecHv)）
- USER#5: `@/proj/.../drcpa_work_R_GidlAryCtrl_switch_sim_schematic_ALPS/..._schematic.netlist 写一个验证tb`

## agent 工具链与产物

1. list_allowed_files / read_files 读 R_GidlAryCtrl_switch.netlist（CDL，AETHER-SE 抽取）→ 结构分析（顶层 subckt R_GidlAryCtrl_switch，端口 GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!，PMOS 链 MMP2→MMP1→MMP0→vwlp! 上拉，NMOS MMN0 下拉）
2. 通路分析：通路A（PMOS 耦合到阱 vwlp!，cm1_sw_total/cm1sw 低导通）= ACT 上拉；通路B（NMOS MMN0，cm1_sw_total 高导通）= PRE 下拉
3. 推导 NAND 控制逻辑：`D_total=NAND(secHV,cm1_sw_total)`, `D_cm1sw=NAND(secHV,cm1sw)`；因 cm1 恒定高 → `D=NOT(secHV)`：secHV=1(ACT)→D=0→通路A→上拉；secHV=0(PRE)→D=1→MMN0→下拉
4. editor 写 `/home/dsgao/Desktop/R_GidlAryCtrl_switch_tb.sp`（switch-only 版，行为源 `Edt VALUE={IF(...)}` 实现 NAND + Xswitch 例化 + PULSE secHV + cgr 负载 + .tran/.print/.probe）
5. 读 ALPS 仿真顶层网表 → 发现顶层已含 `nand2Y_Xdecx1` 把 SecHv+cm1sw 做 NAND 得 net0 驱动 cm1_sw_total=cm1sw=net0，GrDecPwr=内部 net2 → 写 `/home/dsgao/Desktop/R_GidlAryCtrl_switch_sim_tb.sp`（含 .lib 模型库、.option finesim_mode=spicead、.GLOBAL vbn!/vss!/vwlp!、vsec PULSE、vcm1sw 恒高、cgr net2 20f、.include ALPS 网表、.tran 100p 100n、.print/.probe v(net2) v(net0)）

## 真实资产可读性

- `/proj/drcpa/V0/workdir/dsgao/R_GidlAryCtrl_switch.netlist` → **Permission denied**（/proj/drcpa 属 dsgao 私有，DEBT④ 同 #413/#416）
- ALPS 仿真顶层网表 → 同样 Permission denied
- agent 在 Desktop 上写的两份 tb.sp → **可读**（/home/dsgao/Desktop/ NFS 共享）→ 拿到完整 subckt 结构（MMP0-4/MMN0-1 + 端口）+ NAND 逻辑 + tb 格式
- 结论：资产私有 → **B-grade synthesized**（依据 trace 真实结构与 tb 格式合成 A/B 两套同结构开关网表 + sim_top）

## case 设计（GrDecPwrSwitchTbGen-001，schematic_netlist，B-grade synthesized，L2，k=12）

- **候选写通用脚本** `dec_pwr_switch_tb_gen.py --netlist --sim-netlist --out`：解析开关 CDL（顶层 subckt/端口/MOSFET），自动识别 DecPwr 端口（PMOS 上拉链漏端 ∩ NMOS 下拉漏端）、阱电源/地端口、PMOS 上拉链实例名、NMOS 下拉管实例名、控制信号（非二极管栅极）；解析 sim_top 的 NAND2 自动识别相位信号（非开关端口/非电源的 NAND 输入）；推导 NAND 逻辑 + 真值表（ACT→D=0→pull_up，PRE→D=1→pull_down）；生成自包含 tb.sp（供电/相位 PULSE/控制恒高/行为源 NAND/负载电容/Xswitch 例化/.tran/.print/.probe）+ analysis.json
- **A（可见）**：R_GidlAryCtrl_switch / GrDecPwr / cm1_sw_total / cm1sw / vss! / vwlp! / MMP0-2 / MMN0 / SecHv（trace 真实名）
- **B（隐藏，check.py 跑）**：R_WlPwrGateSwitch / WlDecPwr / wl_sw_total / wlsw / gnd! / vplz! / M_PU0-2 / M_PD0 / WlPhase（每维度反硬编码：cell/net/MOS/信号/阱电源/相位名全不同，W/L 不同 820n/481n→1.5u/0.45u，多 1 颗 clamp）
- **12 条断言 a-l**：含 b subprocess 真跑 + c/d/e B 名/端口/角色精确 + f/g 上拉链/下拉管实例名 + h/i 控制/相位信号 + j NAND 真值表逻辑 + k tb.sp 结构 + l 3-seed 确定+无 A 名泄露
- **自验**：ref PASS 12/12（A/B 双端）+ §4.9 三假（empty/print-only-hardcodeA/core-deleted）全 FAIL + 3 neg（hardcode_a/empty/always_pullup）全 FAIL + negative_selftest ALL-FAIL-OK + 3-seed 一致
- byte-sync sha a49f1ef2 size 7845
