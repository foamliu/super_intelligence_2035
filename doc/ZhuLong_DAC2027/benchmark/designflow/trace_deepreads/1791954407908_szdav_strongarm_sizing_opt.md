# 深读 1791954407908_szdav — StrongARM slicer 约束 sizing 优化器

- trace: 1791954407908_szdav.messages.json (jiangbaol @ hfeg0pkn002, mc=55, 151 msgs, 400KB)
- keywords: hspice:125 (sim-dominant, virt=0) → characterization
- 选料: shard B 候选按 sim-dominant (hspice+spectre+finesim, virt<sim*2) 重排，szdav sim=125 纯 hspice
- ledger: claimed 2026-11-04 21:4x → status deepread

## 真实流（逐字 U0，A 档选轮合规：纯需求，无根因/修复）
> /proj/dscqa/V0_LP6/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa.sp 根据该.sp调节 pmoswidth/pmosfinger/nmoswidth/nmosfinger/itailwidth/itailwidthfinger/inwidth/inwidthfinger 使 Cur_slicer_latch_avg 在 TT_1V_45 corner 下最大不超过 380uA，使 slicer2nd_dly_r0/slicer2nd_dly_r1 最小，工作过程文件可放在 .../SA_opt

(U0 重复 5 次 = 客户端重试；后续无新用户轮；用户**未明确接受**任何结果 → A 档金标准不可用 → B 档 synthesized)

## agent 工具链
1. read_files .sp + .mt0.csv → search_codebase 找 4 个 width 参数锚点
2. run_approved_command(shell-runner) 探 finesim/bsub 可用性 → 探 LSF env (source /apps/lsf/conf/profile.lsf)
3. editor 写 sa_submit.sh (patch .sp width + bsub finesim) / sa_wait.sh / sa_collect.sh / sa_inspect.sh / sa_finalize.sh
4. run_approved_command 跑参数扫描: runs 000-006 变 pmosw(12/16)·nmosw(1/2)·itailw(24/28/32)·inw(28/34)
5. **阻塞**: FineSim FSPRO license daemon down → 所有新 finesim job 120s 后 `daemon is down / exit due to license problem` 失败 → 无法完成扫描/测最优 sizing

## 关键技术事实（agent 实测/读 .mt0.csv 得出）
- 器件→参数映射 (netlist_without_1st_reset_130n):
  - pmoswidth(+finger) → 2 级交叉耦合 NMOS 锁存 XMMP0/XMM17 (LDFEdata/LDFEdataN)
  - nmoswidth(+finger) → 2 级交叉耦合 NMOS XMMN5/XMMN23
  - itailwidth(+finger) → 尾管 PMOS XMMP1 (主电流驱动)
  - inwidth(+finger) → 1 级输入对 XMMP16/XMMN2 (DqIb/Vref)
  - finger = width/den (e.g. pmosfinger=pmoswidth/6u)
- 基线 (TT_1V_45#R, 从既有 .mt0.csv): cur_slicer_latch_avg=350.05uA (<380 ✓ 8.5% 余量), slicer2nd_dly_r0=46.11ps, slicer2nd_dly_r1=45.12ps
- corner: TT_1V_45 (typical, 1V, 45°C); .measure 名: cur_slicer_latch_avg / slicer2nd_dly_r0 / slicer2nd_dly_r1

## distinct vs 已有 B characterization case
SizingSensDiag=per-device W 灵敏度排名(诊断, 单目标)·OtaAutoTune=OTA 调谐·TxRonSize=Ron sizing·VihTripTune=ViH·ThoxVthExtract=Vth 提取 —— 本条=**8-knob 约束多目标 sizing 优化器** (current budget ≤380uA + minimize max(dly_r0,dly_r1))，sweep + 可行性过滤 + 选最优，shard B 首个「约束 sizing optimizer」case，distinct ✓

## 便携 reframe（关键）
trace 原走 FineSim + LSF bsub + foundry PDK (TT_1V_45 corner, 具体器件模型) → 不可移植 .75 (无 foundry PDK, FineSim license 不稳定)。
保留「StrongARM slicer 约束 sizing 优化」子技能，DUT = **level-1 Shichman-Hodges StrongARM slicer** (clk-gated NMOS tail + NMOS 输入对 + PMOS 交叉耦合锁存 + 输出 cap)，hspice parametric sweep over 8 knob (wp/wn/witail/win + finger-den)，parse .measure (cur_latch_avg = AVG i(tail) during clk-high; dly_r0/dly_r1 = trig clk↑→targ out crossing vdd/2)，可行性过滤 (cur ≤ budget) → 选 min max(dly) → optimization_report.json + sweep_results.csv + sim_runs.log。

## 候选 slicer_sizing_opt_ref.py（CLI <netlist.sp> <spec.json> <out_dir>）
- 解析 .subckt slicer + 按角色 name-agnostic 识别 4 器件组 (tail/input_pair/latch_p/load)
- sweep 小网格 (每 knob 3 值, 或 1-at-a-time + 几组 combo, ≥9 runs)
- subprocess hspice 每个 patched deck → parse .lis .measure (case-insensitive)
- 可行性: cur ≤ budget (从 spec.json 读)；可行中选 min max(dly_r0,dly_r1)
- 输出: optimization_report.json{baseline,best_run,all_runs[],feasible_count,constraint_budget,objective} + sweep_results.csv{run_id,wp,wn,witail,win,cur,dly_r0,dly_r1,feasible} + sim_runs.log

## check.py ≥14 条 a-n 设计
(a) zip+slicer_sizing_opt.py (b) py_compile (c) subprocess hspice 真跑 (sim_runs.log n_runs≥9) (d) baseline cur+dly measured (e) B best run cur ≤ budget (f) best run cur 数值 (g) best run dly_r0/dly_r1 < baseline (改进) (h) sweep_results.csv ≥9 行 + 列齐全 (i) budget 从 spec_B 读 (反 naive_hardcode_a) (j) name-agnostic B 名出现 A 名不泄 (k) 跨输入守卫: rerun A → cur ≤ A budget (l) judge 独立重跑 B hspice_ran (m) 确定性 rerun B best 2% 内 (n) all_runs 含 infeasible (cur>budget) 项 (证 sweep 探过可行域外, 反 naive_all_feasible)

## A/B GT (.75 HSPICE 标定，待下轮)
A: vdd=1.1, wp=4u/wn=2u/witail=4u/win=3u, budget=380uA → baseline cur~?, best dly~?
B: vdd=1.2, wp=5u/wn=2.5u/witail=5u/win=4u, budget=300uA (更紧), 节点名 sa/sb→out_p/out_n, 器件名 m_*→ms_* 
跨输入: budget/vdd/器件名/节点名/knob 范围 全不同 → 防 hardcode

## 本轮 .75 DUT 可行性 probe（DEBT 根因）
level-1 StrongARM (clk-gated NMOS tail + NMOS 输入对 + PMOS 交叉耦合锁存, .ic sa/sb=vdd) 跑 hspice V-2023.12-SP1-1:
- ✅ job concluded, DC convergence successful (model 须 nsub=1e16 u0=600 tpg=1，gamma=0 会 nsub<=ni abort — 已踩过坑)
- ❌ cur_latch_avg=-3.99nA (尾管几乎不导通) + dly_r0/dly_r1 failed (输出未翻转) → **StrongARM 未再生**
- 根因猜测: .ic sa/sb=vdd 让 PMOS 锁存初始 off; clk↑ 后 tail 拉低 tail 节点但输入对未差分放电 (inp/inm 直流无差分建立时间?); 或 level-1 无 sub-threshold 导致输入对小信号增益不足无法触发再生
- **下轮第一件事**: 调 level-1 StrongARM 使其再生 (尝试: ① inp/inm 用 pulse 在 clk↑ 前建立差分; ② .ic sa=vdd sb=0 破对称触发再生; ③ 加 reset PMOS 预充; ④ 调 sizing 增益; ⑤ 改 2 级 slicer per trace 原 2-stage 结构) → 标定 A/B GT → 合成 SlicerSizingOpt-001 → 自验 → jsonl → mark case → 清 DEBT:1

## 教训
(1) level-1 model 必须 nsub=1e16 u0=600 tpg=1 (gamma=0→nsub=0→abort，MEMORY 反复记录的坑)
(2) level-1 StrongARM 再生不平凡（同 DFF tSU/tH 多轮 saga），须 .ic/pulse/sizing 多迭代
(3) szdav 原 FineSim+LSF+foundry 不可移植，reframe 到 level-1 + hspice 是唯一可行路径
(4) A 档金标准 = trace 末尾用户接受结果；本 trace 用户未接受 (license 阻塞) → 必 B 档
