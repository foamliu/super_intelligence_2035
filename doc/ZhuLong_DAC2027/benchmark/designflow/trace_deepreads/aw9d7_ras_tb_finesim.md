# deepread: aw9d7 (dsgao@hfeg0pkn001, mc=740, N=302)

## U#0 (A-faithful prompt, 逐字)
`/proj/drcpa/V0/workdir/dsgao/simulation/drcpa_work_Ras_Tscodecomp_schematic_ALPS/netlist xie yi ge tb qu yanzheng zhe ge dian lu yong finesim fangzhen`
(pinyin: 写一个tb去验证这个电路用finesim仿真)

纯提需求(给 netlist 路径 + 用 finesim 仿真验证)，未给根因/修复 → A 档前提成立。

## trace 演化
- U#0 → agent 探目录 → read netlist + netlistHeader/Footer + .map → read Presim/aether.rc + lib.defs + netlist.log
- → 查 10G5 模型库 /apps/imctf/models/cxmt10G5/v0.1/Model_v0d1_10G5.sp (TT/FF/SS corners, incFile_10G5)
- → 读参考 tb /home/dsgao/script/full_testbench.sp + force_power.inc + measure.sp + spice_cfg.py
- M44 → **analyze_ras.py**: 推导布尔函数。OAI21(A,B,C)=~(C&(A|B)), AOI21(A,B,C)=~(C|(A&B))。逐位推导得 **F(A,C)=(A<C)**。X=(A<C), Y=(B<C), HT=X&Y, LT=~(X|Y), NT=X^Y。verify NT==XOR(X,Y) all 512 → True。
- M52 → **Ras_Tscodecomp_tb.sp** (gold tb): .option finesim_mode=spicead / post / PARHIER=LOCAL / scale=1; .TITLE; .lib Model_v0d1_10G5.sp tt; .temp 25; .param pvcc=1.1 pvss=0 pvh=pvcc pvl=0 tr0=0.2n tf0=0.2n t0=20n; .GLOBAL vbn! vbp! vcc! vss!; .include netlist; VVCC vcc! 0 DC pvcc / VVSS vss! 0 DC 0 / VVBN vbn! 0 DC 0 / VVBP vbp! 0 DC pvcc; 9-bit 二进制计数器 PULSE: VAC2 A<2> width=256*t0 period=512*t0, VAC1 A<1> 128/256, VAC0 A<0> 64/128, VBC2 B<2> 32/64, VBC1 B<1> 16/32, VBC0 B<0> 8/16, VCC2 C<2> 4/8, VCC1 C<1> 2/4, VCC0 C<0> 1/2 (PULSE pvl pvh 0 tr0 tf0 width period); .tran 200p 10240n (=512*t0); .probe v(A<2..0>) v(B<2..0>) v(C<2..0>) v(X) v(Y) v(LT) v(HT) v(NT) v(vcc!) v(vss!) v(vbn!) v(vbp!); .END
- M54 → run_finesim.sh (/apps/synopsys/SRB/finesim/V-2023.12-1/bin/finesim)
- M58-99 → 排障 LD_PRELOAD/libstdc++ GLIBCXX_3.4.26 (env -u LD_PRELOAD + Finesim 自带 gcc-9.5 lib64) + 模型 binning shrink 未定义 (.param shrink=1)
- M115-143 → verify_logic.py 用 fscript 读 FSDB 每 20ns 槽中点采样，512 槽全 PASS mismatch=0。统计: X=0 Y=0→LT=1 (204槽) · X=1 Y=1→HT=1 (140槽) · X≠Y→NT=1 (168槽)
- M151 → 交付总结: Ras_Tscodecomp_tb.sp + run_finesim.sh + verify_logic.py + .fsdb。功能验证通过。
- U#152「在当前网表路径来写tb」→ M157-165 写 tb_Ras_Tscodecomp.sp 到网表目录, .include ./netlist (相对路径) + .param shrink=1, 重跑通过。
- U#166 起新任务(R_2stepOcCtrl 优化) → 非 U#0 范畴。

## 金标
gold = Ras_Tscodecomp_tb.sp (M52 主体, M165 加 shrink=1 + 相对 .include)。核心可验结构:
- Finesim 指令 (.option finesim_mode=spicead)
- .lib 10G5 模型 TT corner
- 供电 VVCC vcc! / VVSS vss! / VVBN vbn! / VVBP vbp! + .GLOBAL
- 9-bit 二进制计数器 PULSE (bit j width=2^(8-j)*t0 period=2^(9-j)*t0, j=0..8) 覆盖 2^9=512 组合
- .tran 200p 10240n (=512*t0) 全覆盖
- .probe 全部输出 X/Y/HT/LT/NT + 输入位 + 供电
- .include netlist

## 资产可达性
真实 netlist /proj/drcpa/... permission-denied (e0031982 不可读 dsgao)。→ B-grade synthesized: 忠实构造 3-bit 比较器 netlist (端口 A<2:0>/B<2:0>/C<2:0>/X/Y/HT/LT/NT + .GLOBAL vcc!/vss!/vbn!/vbp!)。

## case 设计 (RasTbFinesimGen-001, schematic_netlist, B-grade, L1-check)
- prompt = U#0 逐字
- A = netlist_A.sp (3-bit 比较器 .subckt Ras_Tscodecomp, 9 输入位 + 5 输出 + 4 供电)
- hidden B = netlist_B.sp (4-bit 比较器 .subckt RasTscodecomp4b, 12 输入位 A<3:0>/B<3:0>/C<3:0> + 3 输出 GT/LE/EQ, 不同函数不同名 → 反硬编码 + 跨输入)
- gold = gen_tb_ref.py (读 netlist .subckt 头抽端口, bus-bit<>→input PULSE, 无<>→output .probe, v*!→supply; emit Finesim tb: .option finesim_mode / .lib tt / .temp / .param pvcc t0 / .GLOBAL / supplies / 二进制计数器 PULSE (bit i period=2^(i+1)*t0 width=2^i*t0) / .tran 2^m*t0 / .probe / XDUT instantiation / .include / .END)
- check.py 16 条件 a-p
