# Deepread · tk1gr · 模拟电路优化·二次执行

- **session**: 1788427145336_tk1gr · **user**: e0044979 · **host**: hfeg0pkn001 · **match_count**: 175
- **domain**: characterization · **track**: synthesized (A-faithful 不可行：USER#0 是「启动业务场景: 模拟电路优化·二次执行」元触发，无真实工程输入/spec，agent 自造电路配置 → 自然语言 prompt 太泛不能作忠实任务说明)
- **nmsgs**: 94（单 user prompt 闭环，其后全 tool_use/result）
- **tool mix**: run_commands:27, editor:8, RAG_MCP search_apis:6, read_files:5, search_codebase:2, SandBox run_code:2, skills:1, get_api_details:1

## USER#0（逐字）
`<user_input mode="act">启动业务场景: 模拟电路优化·二次执行</user_input>`

## Agent 产出（真实文件，/home/e0044979/analog_circuit_optimization/，e0031982 guest 可读）
- `config/circuit_config.json` (2185B)：cs_amplifier, CMOS 0.18um, vdd=1.8, devices M1(nmos w10u l0.5u nf4)/M2(pmos w20u)/R1(1k)/C1(1p)，optimization: simulated_annealing, max_iterations=100, convergence_threshold=0.001, random_seed=42, initial_temperature=10, objectives gain(40dB,1.0)/bandwidth(100MHz,0.8)/power(1mW,0.6), design_variables M1_w[2u,50u]/M1_l[0.18u,2u]/M2_w[4u,100u]/M2_l[0.18u,2u]/R1[100,10k]
- `scripts/run_optimization.py` (17965B)：SA 主引擎
- `scripts/run_optimization.il` (3042B)：Cadence Virtuoso SKILL 桥接
- `results/run_002/optimization_results.json` (8059B)：status=completed, total_iterations=100, initial_cost=0.489519, **best_cost=0.489519（=initial，cost_improvement=0.0，SA 未改善卡在初值作 best）**, best_design_variables {M1_w=5e-05,M1_l=8.578e-07,M2_w=4e-06,M2_l=1.695e-06,R1=2403.36}, best_metrics {gain_db=14.49,bandwidth_hz=6.78e7,power_w=4.48e-4,phase_margin_deg=62,gm1=0.002266,rout=2349,id1_A=2.45e-4}, cost_details per obj {value/target/error/cost}, history_summary {iterations_sampled=21, best_iteration=100}, history[] sampled {iteration,temperature,current_cost,best_cost,current/best gain_db/bw_hz/power_w}
- `results/run_002/summary.json` + `best_design_variables.json` + `optimization_report.txt`

## Case 设计（EDA-Eval-DesignFlow-AnalogOptPipeline-001, synthesized/L1, k=16）
- **deliverable**: run_optimization.py CLI `<config.json> <output_dir>`，纯 stdlib，SA + 一阶 gm/Id 代理模型，写 optimization_results.json + summary.json + best_design_variables.json
- **资产 A**（SUT 可见）: circuit_config_A.json（trace 真实 CS amp 配置）+ example_results_A.json（trace 真实结果，schema 样例，勿照抄数值）+ task_brief.md
- **隐藏 B**: circuit_config_B.json（**folded-cascode OTA**，CMOS 0.18um vdd=3.3，6 设计变量 Win/Lin/Wcas/Lcas/Itail/Cc，max_iterations=**80**, seed=**7**, 4 objectives gain/bandwidth/power/phase_margin）+ hidden_manifest.json
- **check.py 16 断言 (a-p)**: zip 含 run_optimization.py(a) / py_compile(b) / B 上 exit0+results.json(c) / 必需顶层键齐全(d) / status==completed(e) / total_iterations==80(f) / best_dv 键集恰={Win,Lin,Wcas,Lcas,Itail,Cc}(g) / 各 best_dv 在 [min,max](h) / best_metrics 含 gain_db/bw/power(i) / cost_details 对 4 obj 各一项含 value/target/error/cost(j) / history>=10 条含 iter/T/cur/best_cost(k) / best_cost<=initial(l) / history best_cost 单调非增(m) / T 递减首>末(n) / 二次运行 best_cost 完全一致(确定性, seed 被用)(o) / summary+best_dv.json 存在且与 results 一致(p)
- **判分口径**: 只验**结构 + 不变量**（schema/上下界/单调性/退火/确定性），不验具体数值（代理模型可不同）→ 避免过拟合 ref
- **自验**: ref 16/16 PASS · negative_selftest 4 neg(empty/print_only/hardcode_a/core_deleted) 全 FAIL NEG_RC=0 · §4.9 三假(empty/print/core_deleted) 全 FAIL
- **与既有 char case 区分**: OtaAutoTune=5T OTA HSPICE .LSTB 真跑调参(L2 faithful)；本 case=SA 优化引擎+代理模型离线 pipeline(L1 synthesized)，判结构不变量非真跑，distinct

## 同源候选（一并 parked）
peek 8 fresh 候选：cwq7f/1wvdl/f6x1i(e02141, 全同「study sentaurus TCAD deck examples & summarize」doc-summarization, reject) · qrmvt(rongjiez Perl openWave.pl waveview 脚本改, shard D 倾向) · rp39a(rongjiez Qt mainwindow.cpp probe 按钮+aether skill, 非 spice) · f1rqc(hbpeng tcl→skill 代码转换, skill-authoring 非 spice) · o5xjq(e0014566 eda_agent skill_instructions, 23 msgs Q&A) · u0mwh/y6liq(t0002614 同「analyze and explain netlist structure」Q&A, 非 produce) — 仅 tk1gr CLEAN。
