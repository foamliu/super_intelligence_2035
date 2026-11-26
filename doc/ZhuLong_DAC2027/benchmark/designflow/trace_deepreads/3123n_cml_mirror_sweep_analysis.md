# Deepread · 3123n · CML 电流镜 sweep 分析

- **session**: 1793669959152_3123n (ledger 旧记 1793263785862_3123n, slug=3123n)
- **user/host**: lvyy @ hfeg0pkn005 (10.129.2.14), 亦在 hfeg0pkn002/hfeg0pfn118/hfeg0pgn093 复制
- **mc**: 576 · keywords: netlist:2079 hspice:1436 schematic:657 synopsys:266 transistor:240 mosfet:86 bandgap:12
- **size**: 3.25MB, 447 msgs (239 user/208 ast), 42 真实用户轮
- **trace 源文件**: .75 ssh 10.129.2.14 /home/lvyy/.cline/data/sessions/1793669959152_3123n/1793669959152_3123n.messages.json

## 用户真实意图

用户搭了一个 CML (Current-Mode Logic) 差分放大器电路，偏置用电流镜 (XPM6 二极管 + XPM2/XPM3 尾管)，目标 I6=100µA。围绕「扫输入管/电流镜管尺寸 W/L/multi → 电流为什么差这么多 → 怎么选 W/L」做深度咨询 + 仿真结果分析。核心可操作化线程 = **#17-#19 sweep 结果分析**：

- #0「为什么扫输入管 mp5 的尺寸会导致电流差这么多」(激励 /proj/m2701/V0_DDR4/workdir/lvyy/simulation/LP6/small_schematic/cml_tran.sp)
- #17「tran_5 固定 W=2.5u 扫 L，tran_6 固定 L=50n 扫 W，tran_7 固定 L=100n 扫 W，这些结果能说明什么？」
- #18「为什么 tran_5/tran_7 电流稳定在 120uA，而 tran_6 在 100uA？比例固定电流不应该一样吗？」
- #19「现在两个管子 multi 都是 1 了，tran_8 固定 W 扫 L，tran_9 固定 L 扫 W，怎么选 W/L」

## 助手分析 (msg 233/237/241) — 真实数据 + 结论

### 关键发现 1：multi 比没动 → 理想电流=150µA 非 100µA
tran_5/6/7 中 W、L 统一了，但 XPM6 multi=2 / XPM2,XPM3 multi=3 没动 → 有效几何比 = (3×W/L)/(2×W/L) = 1.5 → I_ideal = 100µA×1.5 = 150µA。三组实验电流 101~122µA = 150µA × η。

### sweep 数据 (真实)

**tran_6** (fixed L=50n, sweep W, ratio=1.5):
| W | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 µ |
| id | 101.3 | 101.7 | 101.8 | 102.0 | 102.2 | 102.5 µA |
| η | 0.675 | 0.678 | 0.679 | 0.680 | 0.681 | 0.683 |
→ 比例固定时电流几乎不动(±0.6%)，镜相电流由 I6+比例决定与绝对尺寸无关。η=0.68 被 **DIBL** 钳制(L=50n 太短，二极管 Vds=0.45V vs 尾管 0.19V 失配)。

**tran_7** (fixed L=100n, sweep W, ratio=1.5):
| W | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 µ |
| id | 107.9 | 114.2 | 116.9 | 118.3 | 119.3 | 119.9 µA |
| η | 0.719 | 0.761 | 0.779 | 0.789 | 0.795 | 0.799 |
→ 小 W 端 w=0.5µ 尾管 region=Linear (Vds=172.5mV < Vdsat=188.1mV)。大 W 端 DIBL。

**tran_5** (fixed W=2.5µ, sweep L, ratio=1.5):
| L | 50 | 80 | 100 | 120 | 150 | 200 | 300 n |
| id | 102 | ~117 | 120 | 122 | 121 | 120 | 119 µA |
| η | 0.68 | ~0.78 | 0.80 | 0.81 | 0.81 | 0.80 | 0.79 |
→ 小 L 端 DIBL；大 L 端(L=300n)尾管进线性区 (Vds=153mV < Vdsat=213mV)。

**tran_8** (fixed W=2.0µ, sweep L, multi=1:1, ratio=1, I_ideal=100µA):
| L | 50 | 80 | 100 | 120 | 150 | 200 | 300 n |
| id | 73.2 | 80.8 | 82.6 | 83.1 | 82.6 | 80.9 | 77.3 µA |
| η | 0.732 | 0.808 | 0.826 | 0.831 | 0.826 | 0.809 | 0.773 |
→ **η 在 L=120n 达峰(0.831)，峰顶极平**(L=110~130n 差异<0.2%)。

**tran_9** (fixed L=120n, sweep W, multi=1:1, ratio=1):
| W | 0.5 | 1.0 | 1.5 | 2.0 | 2.5 | 3.0 µ |
| id | 70.5 | 78.5 | 82.0 | 83.1 | 84.0 | 84.8 µA |
| η | 0.705 | 0.785 | 0.820 | 0.831 | 0.840 | 0.848 |
→ η 随 W 单调上升，**W≥2µ 进入平坦区**(每 0.5µ 仅+0.8%)。交叉点自洽: tran_8(L=120n)=tran_9(W=2.0µ)=83.11µA ✓

### 关键结论
1. **η<1 是结构性的**: 二极管 Vds=Vsg(自偏置最大) > 尾管 Vds(~0.18V) → DIBL 使二极管 |Vth| 低 ~7mV → 1:1 复制天然衰减 ~15%。
2. **L=120n 最优**: η 峰顶平坦 → 对 L 系统性漂移一阶不敏感。
3. **W≥2µ 平坦区**起点(L=120n 时)。
4. **1:1 + 同 W/L 下 100µA 不可达**(max 84.8µA@W=3µ) → 必须 ratio>1 预补偿。
5. **三方案达 100µA**: A(multi=1:1, w0=2.4µ/w1=2.85µ, ratio 1.19) / B(η=0.840=1.19) / C(multi=5:6 最稳, 余量 65mV)。

## 造题形态
spice_sim L1 便携 analysis/Q&A → 写 `analyze_mirror_sweep.py(workdir,out_dir)` 解析 5 个 sweep 数据文件，算 η、识别钳制机制(DIBL/linear-region/density)、找 η 最优 L + 平坦 W 区、判定 1:1 可达性 + 算 ratio_needed，产 `mirror_sweep_report.json` 打包 submit.zip。A 档 trace-faithful 保留真实用户/数值/circuit 名/η 曲线。hidden B 不同 target I6=80µA + 不同 multi 比 + 不同 η 曲线(峰在 L=100n) + 不同可达性结论 → cross-input guard。
