# ug6lk 深读 — 双速率 PWL 时钟生成器

- trace: `1794450037273_ug6lk.messages.json` (joeyl @ hfeg0pkn004, mc5, hspice:12)
- src scan: `summary_20261121_151844.tsv`
- n_msgs: 36 (含 user_input wrapper), 真实对话 ~18 轮
- size: 134KB

## 真实意图 (U0)
```
/rundata/m2701/V0_DDR4/simdir/finesim/workdir/joeyl/testbench_dqs/m2701/5_DIVIDER/2_TRAN.sp
请看此处的testbench，目前的输入形态wckt/wckc没有满足我的预期，我希望给2次toggle的'1*period'周期，然后再进行'0.5*period'的toggle，有办法实现这样的波形吗？
```

testbench 现状 (line 89-90):
```
V_WCKT  WCKT  0  PAT (VIH VIL 0.2n tr tf 'period*1' b01 RB=1 R=-1)
V_WCKC  WCKC  0  PAT (VIH VIL 0.2n tr tf 'period*1' b10 RB=1 R=-1)
```
- PAT 源：固定单一周期 `period*1`，bit pattern b01/b10 差分互补，每沿间隔 period
- period = 1/HDR = 2/DR，DR=25.2e9 → period≈79.37ps
- VIH=0.65, VIL=0.55, tr=tf=25ps, td=0.2n

## 需求确认 (ask_question → 选项 B)
WCKT/WCKC 先出 **2 个完整方波周期 (4 个沿)，每沿间隔 1*period**，从第 3 周期起切换为 **每沿间隔 0.5*period**，持续到仿真结束 (.tran 10p 6n)。

## assistant 方案
- PAT 只支持单一固定周期，无法"先慢后快" → 改用 **PWL 逐点源**
- 写 Python 生成器 `gen_wckt_pwl.py`：参数 DR/period/tr/tf/VIH/VIL/td，算出 PWL 拐点
- 慢段 4 沿: 0.200, 0.279, 0.359, 0.438 ns (间隔≈79.37ps=period)
- 第 5 沿起切换: 0.478, 0.517, 0.557… (间隔≈39.68ps=0.5*period)
- WCKT 从 VIL(0.55) 起，WCKC 从 VIH(0.65) 起，差分互补
- build_deck.py 把 PAT 两行替换成 PWL，生成 2_TRAN_fast.sp
- validate_pwl.py 校验：时间单调、边沿间隔正确、斜坡(tr/tf)无重叠
- 中途修了一个 bug：慢段切换点多算了一个 period（循环 e 多前进），修正后第 5 沿起 0.5*period 步进

## reframe (L1 纯 Python, 便携可判分)
`dual_rate_pwl_clock_gen.py --spec <spec.json> --out <pwl.inc>`：
- 读 JSON spec {node_p, node_n, vih, vil, period, td, tr, tf, n_slow_cycles, fast_factor, tend}
- 生成差分对 PWL：node_p 起 vil，node_n 起 vih（互补）
- 慢段：2*n_slow_cycles 个沿，首沿 td，间隔 period
- 快段：间隔 fast_factor*period，直到 tend
- 每沿用 ramp-forward 模型：rising (t,vil)(t+tr,vih)，falling (t,vih)(t+tf,vil)
- 输出两条 PWL 源行

## case = EDA-Eval-DesignFlow-DualRatePwlClockGen-001
- k=12 (a-l)，ref 12/12 PASS，NEG 3/3 FAIL (§4.9 三假齐)，3-seed 确定性
- A: dir_A (joeyl 真实参数 WCKT/WCKC, vih=0.65/vil=0.55, period=79.37ps, td=200ps, tr=tf=25ps, n_slow_cycles=2, fast_factor=0.5, tend=6ns)
- hidden B: hidden/dir_B (五重 anti-hardcode: DCKT/DCKC, vih=0.90/vil=0.10, period=120ps, td=150ps, tr=15ps/tf=12ps, n_slow_cycles=3, fast_factor=0.25, tend=4ns)

## 核心"齿" (catch naive/wrong)
- (g)+(h)+(i) 速率切换：反 naive 全慢/全快
- (c)+(e) 差分互补对：反 naive 单节点或两同向节点
- (j) ramp 不重叠：反 naive 忽略 tr/tf
- (k) anti-hardcode：反硬编码 A

## distinct
vs JitterDutyBlockPwlGen-001 (jnhb2): 本 case 变 *边沿间距/速率* (慢→快)，恒 50% 占空，差分对；jnhb2 变 *占空* (block 交替)，恒 period，单节点。核心机制不同 ✓
vs StimPWL/PwlStimTransform/WvCurPwlStimGen/BndGaussPwlGen/DivSelDuty/DutyOffsetAlertMaxProduce/PulseStimTbGen/DcaStimSweepGen/CmlDividerSweepTbGen：均非"双速率慢→快差分 PWL 时钟生成器 + ramp 非重叠校验" ✓
