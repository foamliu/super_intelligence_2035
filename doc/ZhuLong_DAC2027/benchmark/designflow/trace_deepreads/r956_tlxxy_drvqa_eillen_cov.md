# r956 deepread — tlxxy (ethanw@hfeg0plg92) ncsim EILLEN illegal coverpoint diagnosis

## trace
- session: `1795076330770_tlxxy.messages.json` (mc163, verilog:1010 主导, A-pure digital/verification)
- host: hfeg0plg92, user: ethanw, workdir: /proj/drvqa/V0/setup/sim/sim_vector/verilog.ddr5.drvqa.coverage_spf
- 79 msgs, 642KB. 5 user intents: U#0 ncelab DLCSMD checksum / U#5 ncsim EILLEN / U#11 cfg SS-split / U#33 vec_training reformat / U#57 runstimulus 补全

## 选定单意图: U#5 (analysis-Q&A, 最干净自洽)
- 用户原话(逐字): `ncsim: *E,EILLEN: ...(constraint_timing_coverage.sv, Line: 6509)...Sampled value (-1) for coverpoint (...cp_delta_min_vs_constraint_min) is an illegal value.` (17 行 EILLEN, 多个 covergroup: cg_t_ACT_TO_WR_tRCD_Table_283_314@6509 / cg_t_WR_TO_PREab_CWL_BL_2_tWR_Table_22@3704 / cg_t_PREab_TO_MRR_tRP@4193 / cg_t_ACT_TO_RD_tRCD_Table_283_314@6455 / cg_t_PREpb_TO_MRR_tRP@4301)
- assistant: read_files constraint_timing_coverage.sv 1-120 + 6380-6560 → 诊断

## ground-truth (来自 trace msg#10 诊断, 非硬编码期望串)
- 错误性质: 功能覆盖率 illegal_bins 命中 (非编译/缓存问题, 与 U#0 DLCSMD 无关)
- coverpoint 表达式: `E1 = longint'(delta_min/tCK) - longint'(((constraint_min*997)/tCK + 1000)/1000)`; 三元 `E1<0 ? E1 : E1==0 ? 0 : E1<=0.5*constraint_min/tCK ? 1 : 2`
- illegal_bins `illegal = {[-100000000:-1]}` — E1<0 时 coverpoint 值=负 → 命中非法区间 → Cadence 报 *E,EILLEN (按 Error)
- `-1` 语义 = delta_min(nCK) - constraint_min(nCK) == -1: 实测最小延迟比约束少 1 nCK
- *997/1000 四舍五入: constraint_min 转 nCK 时的 rounding
- iff guard: `constraint_min != 0`
- bins: meet_exactly={0} / safe_within_half={1} / safe_beyond_half={2}
- 两种可能: 真违例(修时序数据) vs 误报(初始化期 delta_min 无效占位 -1)
- 时序集中: 0.9µs–1.7µs 上电/初始化阶段
- 文件自动生成 (coverage/DDR5_2026-11-05/ 日期目录) — 须改模板非手改
- 解决: ① 加强 guard `iff (constraint_min != 0 && delta_min >= 0)` (推荐) ② illegal_bins→ignore_bins (放弃负裕量报警)

## case 设计
- ID: EDA-Eval-DesignFlow-CovEillenIllegalBinsAnalyzeQA-001
- domain: digital (verification/coverage)
- A fixture: constraint_timing_coverage.sv 片段 (6380-6560, 含 cg_t_ACT_TO_PREsb/RD/WR 三个 covergroup) + ncsim_error.log (用户 EILLEN paste)
- hidden B (inlined): 同构异值 — B covergroup `cg_t_RD_TO_PREab_tRP_Table_221_248`, illegal value -2, var delta_obs/constraint_lo, illegal_bins [-2e8:-2], rounding *995, iff guard `>0`, pkg cov_model_pkg, bins exact_match/within_margin/beyond_margin
- check.py: 14 断言 (a-n) report-based + §4.2 subprocess 解析 fixture 提取 illegal_bins 范围/coverpoint 名/三元结构 + anti-leak + refuse-to-hallucinate + §4.9
- negatives: empty / print-only / core-deleted / wrong_root_cause (说成编译问题) / hallucinated (用 B 标识符)

## ledger
- claimed: tlxxy (digital) → mark case EDA-Eval-DesignFlow-CovEillenIllegalBinsAnalyzeQA-001
