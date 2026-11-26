# 37j9u — CML sweep headroom starvation diagnosis

## trace
- user: lvyy, host: hfeg0pkn004, session: 1793763989902_37j9u
- 409 msgs, 2.7MB, mtime Nov 4 18:12
- match_count: 2396 (spice dominant)

## U#0 (A-faithful 任务说明轮, 逐字)
「我搭了一个电路，电路路径在激励文件/proj/m2701/V0_DDR4/workdir/lvyy/simulation/LP6/small_schematic/cml_tran.sp中，为什么扫输入管mp5的尺寸会导致电流差这么多」
- 提出需求, 无根因/修复 → 符合 A-档选轮 ✓

## 电路结构 (netlist cml_1, lines 18-37)
PMOS CML 差分对, 两路独立尾电流源:
- XPM6: CMLBias CMLBias vdd2d! vdd2d! plvt_ckt w='w0*1' l=l0 → 二极管连接偏置管 (D=G=CMLBias), w0=1.5u l0=50n
- XPM5: CkTo CKT net8 vdd2d! plvt_ckt w='winput*1' l=linput → 输入对管 (CKT 侧), winput 扫参
- XPM4: CkCo CKC net9 vdd2d! plvt_ckt w='winput*1' l=linput → 输入对管 (CKC 侧), winput 扫参
- XPM3: net9 CMLBias vdd2d! vdd2d! plvt_ckt w='w1*1' l=l1 → 尾电流源 (net9 支路), w1=2.6u l1=50n
- XPM2: net8 CMLBias vdd2d! vdd2d! plvt_ckt w='w1*1' l=l1 → 尾电流源 (net8 支路, **被测器件**), w1=2.6u l1=50n
- R1 CkCo vss! res (2.9k), R2 CkTo vss! res (2.9k) → 负载电阻
- I6 CMLBias vss! DC=100e-6 → 偏置电流源 100µA

## .sp 关键参数
- VDD2D=0.875, CMLBias=0.341, w1=2.6u, l1=50n, Winput=1.3u, linput=50n, res=2.9k, w0=1.5u, l0=50n
- .tran 20p 15ns sweep winput 0.5u 3u 0.5u (6 点)
- .meas id avg isub(xpm2.s) from=3n to=15n

## 金标准 (assistant msg#15)
测量数据 (tran_9/cml_tran.mt0.csv):
| winput (µm) | id=isub(xpm2.s) (A) |
| 0.5 | 7.216e-05 (72.2µA) |
| 1.0 | 9.527e-05 (95.3µA) |
| 1.5 | 1.061e-04 (106.1µA) |
| 2.0 | 1.128e-04 (112.9µA) |
| 2.5 | 1.174e-04 (117.4µA) |
| 3.0 | 1.206e-04 (120.6µA) |

变化: +67% (72.2µA → 120.6µA), 单调递增

根因: **Headroom Starvation** — 增大输入对管 winput → 输入对管过驱动电流需求增大 → 侵占尾电流源 XPM2 的 Vds 电压余度 → XPM2 工作点漂移 → isub(xpm2.s) 显著变化

## 合成
- case: EDA-Eval-DesignFlow-CmlSweepHeadroomDiag-001 (spice_sim A-faithful L1, k=14)
- A: cml_tran_A.sp (真实) + netlist_A (清洗保留器件连接+w/l) + cml_tran_A.mt0.csv (真实 6 点)
- hidden B: cml_tran_B.sp (sweep linput, meas isub(xpm3.s)) + netlist_B (XPM2=diode, XPM6=tail, neta/netb) + cml_tran_B.mt0.csv (4 点递减)
- reference: analyze_cml_sweep_ref.py (解析 .sp sweep/measure + netlist 器件分类 + CSV 统计)
- check: 14 断言 (a-n) 含交叉输入守卫(k,l) + A-only 泄漏闸门(m) + 3 次幂等(n)
