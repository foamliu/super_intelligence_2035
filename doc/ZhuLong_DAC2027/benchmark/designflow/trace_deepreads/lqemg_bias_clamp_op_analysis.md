# Deepread: 1794557759031_lqemg (joeyl @ hfeg0pkn004, mc=138)

## 用户意图
DDR4 DQSIb bias 电路 5-corner 电流变异性优化。biasn/biasp 电流在 5 corner 下 ~2x 摆动（tt=114µA, max/min=1.914），目标 100-150µA。VibCom 固定 0.2V。

两个问题：
1. vfb 为什么没有钳位？opamp 没有作用吗？
2. 最大 iref 与最小 iref 之间管子工作状态是否不同？

后续指令：「1,3都需要更改，请帮我试试吧」→ 改 opamp 钳位 + 改输出头程。

## 工具链
- FineSim (HSPICE 兼容 SPICE 仿真器), 5-corner .alter
- .op operating point 分析, .mt0 measurement 解析
- Python 分析脚本 (zhulong agent 写 _explore_op.py, _op_focus.py, _op_gain.py, _regions.py 等)
- 36 editor, 33 run_approved_command, 11 read_files

## 关键发现（实测 5-corner .op）
1. **opamp 增益 ~1**: 差分对 XM9(gate=VibCom) 全 5 corner Linear (|Vds|=0.002-0.006V, 压塌), XM10(gate=vfb) 全 5 corner Subthreshold。差分级增益 gm·Rout = 0.26-1.97×。
2. **vfb 漂移 0.267-0.340V** (目标 0.2V, 偏掉 +33%~+70%)。
3. **根因**: 差分对输入共模不匹配 — vcm≈0.42-0.53V (尾管+二极管顶住), 两输入栅 0.2/0.27-0.34V, PMOS 差分对源需 ≈ 输入+|Vtp| 才进饱和。
4. **Q2 答案**: max/min iref 两端管子工作状态**无本质不同**。

## 实验迭代
- e2_len (差分加长): vfb 反而升高 → 印证 collapse 是根因
- e4_loaddn (加大二极管/镜像负载 XM13/XM14): vfb 下降 0.316→0.294, max/min 1.914→1.851 ✓
- e5_ldn_len (负载+差分加长): vfb 0.249-0.278, max/min 1.798 ✓ (但 biasn 降到 96.7µA)
- e6 (clamp+R→12u): vfb 0.224-0.235, max/min 1.899
- e7 (更强 clamp, R→12u): vfb 0.213-0.218 (几乎恒等 0.2!), max/min 1.929
- **关键结论**: 钳住 vfb 后 max/min 仍 ~1.9× → 摆动是 **rndif_3t 电阻散布 bound**, 不是 clamp bound
- Task 3 (头程): xpm19/xpm22 加倍尺寸**无效** — Vds 由节点电压(BiasP)决定, 非器件 vdsat

## 交付物
- `netlist_clamp_r12.sp` (e6): R=12u, diff l=250n, loads w=24u/nf=8 → vfb 0.224-0.235, tt=111µA
- `netlist_clampstrong_r12.sp` (e7): loads w=48u/nf=16 → vfb 0.213-0.218, tt=104µA
- `HANDOFF_bias_questions.md` + `HANDOFF_bias_try_clamp_headroom.md`

## 造题方向
L2 spice_sim: 写 Python .op 分析器 → 解析 5-corner operating points → 识别 opamp collapse → 计算增益 → 诊断 vfb 漂移根因 → 提出网表修改（加大负载压低 vbn）→ 输出结构化报告 + 修改后网表。
