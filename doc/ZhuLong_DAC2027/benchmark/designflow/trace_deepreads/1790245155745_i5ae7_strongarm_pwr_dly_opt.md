# Deepread: 1790245155745_i5ae7 — StrongARM comparator power-constrained delay optimization

## Trace meta
- **user**: jiangbaol @ hfeg0pkn002
- **session**: 1790245155745_i5ae7 (543 msgs, 2.2MB)
- **match_count**: 119 (hspice=314, netlist=472, schematic=169)
- **agent**: lead (cline)
- **tool freq**: 85 read_files, 85 editor, 70 run_approved_command, 23 list_allowed_files

## User intent (A-档 faithful, 纯需求轮)
- U#1 (idx=0): "已打开的标签页中DqIb_strongarm_pmos为需要优化的电路...请优化该电路功耗至534uA，同时delay最小"
- U#2 (idx=158): "现在需要将总功耗控制在460uA，并最小化输出delay"
- U#3 (idx=212): "finger数会影响电路性能，考虑finger后给出最佳参数"
- U#5 (idx=306): "调节pmoswidth/pmosfinger/nmoswidth/nmosfinger/itailwidth/itailwidthfinger/inwidth/inwidthfinger使Cur_slicer_latch_avg在TT_1V_45 corner下最大不超过380uA，使slicer2nd_dly_r0/slicer2nd_dly_r1最小"

## Real workflow
1. jiangbaol 给 testbench `004_onlySlicer_delay_dejoa.sp`（foundry G4B PDK + FineSim/HSPICE, double-tail StrongARM comparator）
2. Baseline params: pmoswidth=12u/nf=6, nmoswidth=2u/nf=2, itailwidth=36u/nf=9, inwidth=28u/nf=7
3. Sweep itailwidth → I_total 仍 >534uA even at min → 需联合缩减 all params
4. gen_opt_bench.py 生成 opt deck (pmos=8u, itail=10u, in=16u, nmos=4u) + sweep
5. 多轮迭代: 534→460→380uA target，逐步收紧功率约束
6. 最终 rank1 Cur_slicer_latch_avg ≈ 363uA，继续优化至 380uA min delay

## Circuit (double-tail StrongARM comparator)
- 输入对管 (M1/M2, inwidth) + 尾管 (Mt1, itailwidth, clk-gated)
- 再生负载: PMOS 交叉耦合 (M3/M4, pmoswidth)
- 复位: PMOS precharge (M6/M7, clk-gated)
- 2nd stage: SR latch (nmoswidth)
- Measure: Cur_slicer_latch_avg (功率), slicer2nd_dly_r0/r1 (delay, clk→output cross vdd/2)

## Portable slice (case EDA-Eval-DesignFlow-SAoptPwrDly-001)
- **Foundry PDK 不可移植** → level-1 Shichman-Hodges MOS (kp/vto/lambda/gamma)
- **8 knobs → 4 width knobs** (inwidth/itailwidth/pmoswidth/nmoswidth, fingers fixed M=4)
- **单次 clk 脉冲** (clk low 0-2n → high 2n-30n, eval phase)
- **30mV overdrive** (vinp=vref+vswing, vswing=0.05)
- **100fF load** → delay ~30-50ps (realistic, measurable)
- **Measure**: cur_avg=AVG i(Vdd) 2n-30n, dly=TRIG clk RISE=1 → TARG outpb RISE=1
- **Power target A=80uA, B=220uA** (different vdd/temp/vref/grid)

## Ground truth (.75 HSPICE V-2023.12-SP1-1)
- A (vdd=1.0, temp=45, vref=0.5, vswing=0.05, target=80uA, 4×6×4×3=288 grid):
  best dly=31.7ps, cur=76.5uA, params={inwidth=2u, itailwidth=12u, pmoswidth=8u, nmoswidth=4u}
- B (vdd=1.1, temp=85, vref=0.55, vswing=0.04, target=220uA, 4×6×4×3=288 grid):
  best dly=19.8ps, cur=215.0uA, params={inwidth=2u, itailwidth=11u, pmoswidth=3u, nmoswidth=5u}
- A-best ≠ B-best ✓ (跨输入守卫成立: itail 12u→11u, pmos 8u→3u, nmos 4u→5u)

## Core traps baked into check.py
1. **功率达标** (e/h): 独立复跑 HSPICE 验证 best params 的 cur ≤ target (防 print-expected 造假)
2. **近似最优** (f/i): best dly 在 check.py 独立 Pareto 最优 60% 以内 (防 core-deleted 返回 baseline)
3. **跨输入守卫** (j): A-best ≠ B-best (防 hardcode-a: 不同 baseline/target → 不同 optimum)
4. **搜索证据** (k/l): n_designs ≥ 20 + distinct combos ≥ 20 (防 single-run 只跑 1 点)

## Distinct vs existing B cases
- TaperBufOpt=CMOS buffer chain DOE PDP, VihTripTune=DC trip 4-width tune, CTLEtranChar=瞬态眼图
- 本条=**StrongARM comparator power-constrained delay optimization (4-knob grid search + Pareto)**
  (comparator-optimization-to-power-target 子技能, shard B 首个 L3 multi-knob optimization case)

## Case files
- assets/: params_A.json + corner.lib + prompt.txt + task_brief.md
- hidden/: params_B.json + hidden_manifest.json
- reference/: sa_opt.py + check.py (12 条 a-l) + 5 negatives + negative_selftest.py + reference_submit.zip
- jsonl: EDA-Eval-DesignFlow_B.jsonl line 38
