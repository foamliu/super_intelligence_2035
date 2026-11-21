# trace_deepread: 1794879740388_dfl7k (gallopc / hfeg0plg80, mc47, spice_sim)

## 用户意图 (msg1 逐字)
> /proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/sim_eqloc_zpower/
> 这个路径下有我的仿真sp文件，里面有netlist网表和input.sp激励，里面是一个zpower结构的反相器，请帮我重新生成一个新的inputnew.sp激励文件，用于测试所有可能出现问题的情况和时序，打个比方，要测试到：上电过程中vcczloc_eq还未上升到额定值，LVT管因为Vth低，低电源下就已经满足导通条件，此时输入EqLoc为固定电平会导致输出出现毛刺，后级无隔离逻辑的话会采样到错误值这种情况

## 电路结构 (agent 分析结论, msg17)
- `EqLoc → XI25(invLVx8_XDec_zpwr, LVT 管 ptn_lv/ntn_lv, 虚电源轨 vcczloc_eq) → EqLocN → XI1/XI2(常规管, vcc! 常开供电) → EqLocN2g → EqLocN3g`
- `vcczloc_eq` 由 `XMMP1`(ptn, 栅=SecN) 从 `vcc!` 充电; SecN=0 充电, SecN=高 关断 (之后虚轨只能泄漏放电)
- vcc! = 1.12V
- 原网表虚轨只有几 fF 器件电容, 上电 ps 级完成

## 原 input.sp (msg15 解析)
- 1470 行, 两个 PWL 源:
  - `Veqlocn eqlocn 0 PWL(...)` 728 点, 0..7.27e-7s, **加在输出节点 eqlocn 上** (输入 EqLoc 悬空!)
  - `Vsecn secn 0 PWL(...)` 736 点, SecN 开关控制
- 跳变 >50mV @ 5.68e-7 / 6.16e-7 / 6.30e-7 / 6.78e-7

## 关键风险机理 (agent msg17)
LVT 管 Vth 低, 虚轨只有零点几伏时 PMOS_lv/NMOS_lv 就导通 → 输出跟随虚轨出现无效中间电平(假高)/摆幅不足; 后级 XI1/XI2 由常开 vcc! 供电, 会把无效电平放大成满摆幅错误逻辑值. 原激励把 PWL 加输出 + 输入悬空, 无法复现"上电过程中"毛刺场景.

## agent 产出 (msg40/52)
- `inputnew.sp` (ASCII 注释): 用 `Veqloc`(驱动输入 EqLoc) + `Vsecn`(驱动开关 SecN) 两个 PWL 源, 6 阶段 (慢上电+固定低 / 快上下电+固定低 / 虚轨慢斜坡中翻转 / 慢上电+固定高对照 / 泄漏掉假高 / 屏蔽验证+baseline), `.tran 0.1p 7u`, `.option finesim_mode=spicexd`. 不再加 PWL 到输出节点.
- 因 sandbox 策略收紧, 最终通过 `/home/gallopc/zhulong_gen_inputnew.py` python-runner 落盘.

## 本 case 物化
form = 参数化 zpower-glitch 压力激励生成器 (Python 解析 netlist+config → emit inputnew.sp). A=netlist_A.sp(重建结构)+input_A.sp(原 PWL 头样本). hidden B=EqRst/SecM/vcczloc_rst, vcc=0.9V, invLVx4 size (anti-hardcode-A). check.py 17 条 a-q.
