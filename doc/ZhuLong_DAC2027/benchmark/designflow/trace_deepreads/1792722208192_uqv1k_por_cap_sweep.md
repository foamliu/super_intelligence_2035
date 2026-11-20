# Trace 深读：1792722208192_uqv1k — POR cap-sweep仿真 pattern 生成

## Trace 元数据
- **session**: 1792722208192_uqv1k.messages.json
- **user**: karlwang @ hfeg0plg71
- **match_count**: 312 (hspice 密度 312/113 msgs)
- **agent**: lead (cline-style)
- **size**: 311936 bytes, 108 msgs
- **domain**: spice_sim
- **case_id**: EDA-Eval-DesignFlow-PorCapSweep-001 (track=faithful, level=L2)

## 用户原始请求 (A-档合规 — 纯需求轮)
- **T0 (idx=2)**: 「给我生成一个仿真nicap值对上电速度影响的parttern」
- **澄清 (idx=19, 回答 ask_question)**: 「MIM/MOM 电容或其它类型的电容，想研究容值对 POR（Power-On Reset）电路延迟的影响」
- 无用户给出根因/修复方案的轮 → A-档合规。

## 真实工具链 (assistant)
1. list_allowed_files / read_files 探 workspace (/home/karlwang/Desktop)
2. cimi-kb-search + RAG_MCP_Server__search_apis 查 "nicap 电容 仿真 pattern"
3. ask_question 让用户选 NICAP 类型（MOSCAP / native NMOS / MIM-MOM-POR）
4. editor 写 README.md / por_testbench.sp / por_testbench_advanced.sp / run_simulation.sh / analyze_results.py / run_simulation.tcl / expected_results.md
5. run_approved_command 跑 run_simulation.sh / test_hspice.sh / test_minimal.sh
6. 多轮调试 HSPICE 兼容性

## 真实结果 (trace 末态)
- **por_testbench_simple.sp** 用行为 B 源三目比较器 `Bcomp por_out 0 V='V(vcap) > vref ? vdd_val : 0'` → HSPICE 报:
  - `warning: Keyword table not supported for E(VCVS)`
  - `error: internal timestep too small in transient analysis`
  - `error: tran autoconvergence failure`
  - `***** job aborted` (所有 7 个 .alter case 全 abort)
  - por_out 节点 nonconvergent: 3.35e+12 ↔ -9.14e+12
- **minimal_test.sp** (纯 RC, 无比较器) → `hspice job concluded`, 产 minimal_test.tr0 ✓
- **结论**: trace 中 agent 的完整 cap-sweep pattern 从未成功跑通；只有 minimal RC 测试通过。用户未明确接受终态（会话在 minimal test 后结束）。

## 核心陷阱 (烤进 check.py)
**行为 B 源三目比较器 (`V='cond ? a : b'`) 造成 HSPICE timestep collapse**：
- 三目比较器在阈值处是**硬不连续**（0 ↔ vdd 跳变）
- HSPICE transient 分析在跳变处 timestep 反复减半直至 `internal timestep too small` → abort
- 真实 trace 中 agent 卡在此陷阱，反复重写 testbench 均未解决

**正确解法 (本 case 金标准)**：
- 纯 RC 电路 (Vvdd PULSE → Rpor → Cload → 0)
- `.measure tran t_trip WHEN V(vcap)='vref' RISE=1` **直接测 Vcap 越过阈值的时间**，无需比较器
- POR 延迟 = RC 时间常数 τ=R*C，t_trip = -τ*ln(1-Vth/Vdd)
- `.alter` 扫 7 个 cap 值，每个产 .mtN，解析得 t_trip vs cap

## 便携化
- 无 foundry PDK 依赖：纯 RC + 理想源，HSPICE V-2023.12-SP1-1 直接跑
- A: vdd=1.8, R=100k, vref=1.26 (0.7*Vdd), caps=[100f,200f,500f,1p,2p,5p,10p], t_stop=20u
- B (hidden): vdd=1.2, R=50k, vref=0.72 (0.6*Vdd), caps=[50f,150f,400f,800f,1.5p,3p,8p], t_stop=10u
- 跨输入守卫: A t_trip @100f=12.17ns vs B @50f=2.33ns (完全不同尺度)

## .75 HSPICE GT (V-2023.12-SP1-1)
| cap (A) | t_trip (A) | theory | cap (B) | t_trip (B) | theory |
|---|---|---|---|---|---|
| 100f | 12.17ns | 12.04ns | 50f | 2.33ns | 2.29ns |
| 200f | 24.27ns | 24.08ns | 150f | 6.88ns | 6.87ns |
| 500f | 60.57ns | 60.20ns | 400f | 18.19ns | 18.33ns |
| 1p | 120.7ns | 120.4ns | 800f | 36.46ns | 36.65ns |
| 2p | 241.6ns | 240.8ns | 1.5p | 69.03ns | 68.72ns |
| 5p | 604.5ns | 602ns | 3p | 138.3ns | 137.4ns |
| 10p | 1.198us | 1.204us | 8p | 367.0ns | 366.5ns |

## check.py 14 条断言 (a-n)
a zip含gen+repA · b py_compile · c gen在B exit0产json · d deck含.measure tran t_trip测V(vcap) · e 无行为B源三目比较器(陷阱) · f B≥5非null t_trip · g B单调递增 · h B与RC理论<5% · i B必需字段 · j 跨输入守卫(B≠A) · k HSPICE真跑(.mtN+源码含hspice) · l A与GT<5% · m B与GT<5% · n 参数化(B deck用B参数)

## distinct vs 已有 B case
- NmosAgeChar=单管 Vtlin/Idlin/Idsat · VihTripTune=DC翻转点调优 · OtaAcReport=WaveView AC · TaperBufOpt=buffer DOE · CTLEtranChar=瞬态眼图 · SiOutDiag=si.out日志诊断 · LvlshftBsubDiag=LSF bsub env失败诊断 · Vcc2scActDeckGen=tran deck参数化生成
- **本条 = POR cap-sweep testbench 生成 + 行为源收敛陷阱**（testbench-generation 子技能 + convergence-trap 烤入，shard B 首个"收敛失败陷阱"case）

## negative_selftest (.75 端到端, 4.8s)
- ref **PASS 14/14** + 5 neg 全 FAIL 互异条件集 (c/d/e/h/j):
  - naive_empty→c · naive_hardcode_a→j · naive_behavioral→e(行为源陷阱) · naive_theory→d · naive_print_expected→h
- §4.9 三假(空壳/print-expected/掏空hspice)全 FAIL
- test 字段==disk check.py md5 9f2dc365c6e11286adc3f66ed7941f3b roundtrip OK

## 教训
1. HSPICE 行为 B 源 (`Bname n+ n- V='...'`) 中的三目 `? :` 或 `if` 表达式在阈值处硬不连续 → timestep collapse；需用平滑函数 (tanh) 或避免行为源（直接 .measure WHEN）
2. PULSE 源的 pulse width 必须 ≥ t_stop，否则 VDD 在仿真中途回落（C=10p 时 t_trip=1.2u > 1u pulse width → measure failed）；用 `PULSE(0 vdd 0 1p 1p t_stop 2*t_stop)`
3. `.alter case=X: .param ...` 内联语法不生效（所有 case 同值）；正确：`.alter` 单独行 + 下一行 `.param load_cap=...`
4. gen.py 子进程 cwd=out_dir 时，`-o out_prefix` 须用相对路径（相对 cwd），sp 用相对名，否则输出落到 nested 子目录
