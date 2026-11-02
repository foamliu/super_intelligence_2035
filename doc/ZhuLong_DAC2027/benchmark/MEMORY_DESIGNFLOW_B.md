WAITING: 0
SHARD: B (spice_char)
DOMAINS: characterization, spice_sim

- **PHASE**: shard B 在跑。每轮 1 条 case：trace_ledger.py --shard B next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_B.jsonl → 日报
- **基线**：10 条 proper（characterization×2, spice_sim×8）· 已跑 0 条（未 pi 实跑）· 断言清单 10/10 达标 · 目标通过率（B 档）20–30%
- 📊 trace 覆盖率：covered=9 / mc300=1001 ≈ 0.9%（见 designflow/trace_ledger.py --shard B stats）
- 🎯 通过率: 0/0（shard B 暂未 pi 实跑；A/B 分档后首次实跑再报）
- 🧾 断言: k_rationale=k_check=n ✓（今日 10/10 达标；新条 ProbeTrim-001 = 14 条）

## 流水
- 2026-11-02 shard B #3：建 `EDA-Eval-DesignFlow-ProbeTrim-001`（spice_sim, L2, B 档）。trace=1789713740053_1fgo2（ynbai/hfhds206, mc=179, PrimeSim DRAM fullchip 瞬态签核仿真慢诊断 + probe 裁剪/.tran 分段/tolerance 加速）。子任务=probe 裁剪：把 `.probe v(*)` 改成只留 `.measure` 所需信号（in/out），真跑 FineSim 验证 probed-signal 数下降而 .measure 不变（对应 trace 中 probe 8.44M→4.19M、输出准备 312s→67s、measure 保持）。小尺度复现：5 级 CMOS clkbuf 驱动 3 级 RC 阶梯；full=`.probe v(*)`(74 probed) vs trimmed=`.probe v(in) v(out)`(2 probed)；FineSim 真跑取 GT——`# probed signals` 74→2、`# time points` 2209 不变、tpd 6.541e-11 / vout_hi 3.4054e-08 / vout_lo 1.05 完全保持。A(3 级/2 RC/47 probed)≠B(5 级/3 RC/74 probed) 跨输入防硬编码。check 14 条件 a–n；ref 14/14 PASS（.75 自验）；3 negs(naive_copy/always_pass/ref_no_core) 全 FAIL（naive FAIL g/h/m、always FAIL j、no_core FAIL e/f/g/i/m）；§4.9 三假提交由 negatives 覆盖。断言闸门 k_rationale=k_check=14≥8 ✓。已追加 EDA-Eval-DesignFlow_B.jsonl 第 10 行，mark --status case。备注：sandbox FineSim V-2023.12 不支持多 .tran 分段（`ERROR! no signal to print or probe`）、relax reltol 在小尺度不改 `# time points`，故选 probe-trim 子任务（最可复现判分）。
- 2026-11-02 shard B #2：建 `EDA-Eval-DesignFlow-SimExpl-001`（spice_sim, L2, B 档）。trace=1792031875998_68gc9（kli/hfeahpc501, mc=424, FineSim DRAM fullchip 仿真时间/内存爆炸诊断：对比 si.out 找多出来的 .ic 节点 / 寄生 R/C 节点）。小尺度复现：CMOS 时钟 buffer 链驱动寄生 RC 阶梯，baseline(6 .ic/12 RC) vs bloated(120 .ic/120 RC)；FineSim 真跑取 GT——bloated 的 `# signals with .IC` 6→120、`# Resistor/Capacitor` 12→120、vout_final 5.3283e-08→2.9659e-05。check 14 条件 a–n；ref 14/14 PASS；3 negs + §4.9 三假提交全 FAIL。断言闸门 k_rationale=k_check=14≥8 ✓。已追加 EDA-Eval-DesignFlow_B.jsonl 第 9 行，mark --status case。
- 2026-11-02 shard B #1：建 `EDA-Eval-DesignFlow-ClkBufTran-001`（spice_sim, L2, B 档）。trace=1793147699495_as67p（easont/hfhds211, mc=786, finesim cosim 时钟分布）。DUT=2 级反相器时钟 buffer 链 .tran 表征，10 条 .meas（tpd_rise/fall/avg, trise/tfall, voh/vol, idd_avg, tpd_2nd_rise/v_after→failed→not_met）。真跑 FineSim -spice 在 .75 取 GT：B(m=2,C=200f) tpd_rise=90.249ps / A(m=4,C=50f) 59.241ps。check 12 条件 a–l；ref 12/12 PASS；3 negs + §4.9 三假提交全 FAIL。断言闸门 k_rationale=k_check=12≥8 ✓。已追加 EDA-Eval-DesignFlow_B.jsonl 第 8 行，mark --status case。
- 📦 体积：TASK≈17KB / MEMORY≈1KB
