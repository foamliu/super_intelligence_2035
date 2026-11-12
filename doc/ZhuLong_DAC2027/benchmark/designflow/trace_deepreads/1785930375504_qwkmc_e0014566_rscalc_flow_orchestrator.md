# trace_deepreads/1785930375504_qwkmc_e0014566_rscalc_flow_orchestrator.md

## trace
- slug: `1785930375504_qwkmc`
- user/host: e0014566 / hfeg0pkn001
- mc=166, keywords: virtuoso:373;.gds:125;drc:41
- session: 6 msgs (dict-wrapped, `messages` array), 413KB, agent=lead, model=glm-5.2
- cwd: `/home/e0014566/test_layout_rscalc_flow_5`
- status: failed (terminal_marker=failed_external_process_exit, stale_session_reconciler) — but flow logic fully exercised before exit
- USER turns: **1** — `read the prompt_flow.md and do the job in it.` (single produce-demand)

## task (from prompt_flow.md, fully extracted)
Resistance-Reduction Flow: RsCalc (baseline) → [AutoVia → PowerFill → RsCalc] × maxIterations.
- **RsCalc** (`virtuoso-rscalc-runner`): measures worst-case resistance of current layout; outputs `*.rvn` per net (col #12 = resistance) + GDS via `leoXstreamOut`.
- **AutoVia** (`virtuoso-autovia-runner`): inserts vias, writes via-merged layout `<orig>_via<i>`.
- **PowerFill** (`virtuoso-powerfill-runner`): fills power rails, writes final merged layout `<orig>_opt<i>`.
- Convergence: **every** check point p must satisfy `R_i(p) ≤ R_0(p) × (1 − targetReduction)`. Position key = `net_layer_x_y`.
- Config: `common.config` (shared: process/project/libName/cellName/viewName + flow-control: targetReduction=0.5, maxIterations=5). cellName is the single chaining point (updated each step).
- Each runner: `gen_*_agent.py` reads common.config + tool config + `*_nogui.il` template → inlines → self-contained `.il` → `virtuoso -nograph -replay` batch. Env: `env -u ARGUS_HOME _CXMT_SH_PROJ_WRITE_CHECK=1 OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x LD_PRELOAD=/usr/lib64/libstdc++.so.6`.
- GDS staging: AutoVia's `strmout` fails in batch; reuse the GDS RsCalc streamed out via `leoXstreamOut`. PowerFill streams out itself (no staging needed).

## agent execution (reconstructed from 125 tool_use msgs)
1. read prompt_flow.md → read 4 configs + 3 SKILL.md + 3 gen_*_agent.py
2. **Step 1 baseline**: gen rscalc agent → launch virtuoso → poll DONE! (180s) → parse 18 check points (M1:5, vbb:5, vdd:8) → max R=269.849Ω → stage GDS to AutoVia runDir
3. **Iter 1**: AutoVia (testa→testa_via1, auto-detect vdd!) → PowerFill (testa_via1→testa_opt1) → RsCalc (testa_opt1) → 0/18 converged (resistance byte-identical to baseline; GDS grew 10KB→244KB but fill off measured paths)
4. **Iter 2**: AutoVia (testa_opt1→testa_via2) → PowerFill (testa_via2→testa_opt2, "Nothing has been generated!!" — already filled) → RsCalc (testa_opt2) → 0/18 converged
5. **Iter 3** (in progress when session terminated): AutoVia started, "No via cells generated" for vdd
- bestCell stayed testa_opt1 (all iters failCount=18, no improvement); session ended at iter 3 AutoVia phase (stale session reconciler killed it).

## key technical details (for future case reuse)
- Cell naming: `<orig>_via<i>` (AutoVia out, intermediate) / `<orig>_opt<i>` (PowerFill out, measured by RsCalc). `<i>` from 1.
- Convergence loop control: `bestCell=origCell; bestFailCount=999999`; per iter `if failCount < bestFailCount: bestFailCount=failCount; bestCell=newCell`; `if failCount == 0: break`.
- Real flow depends on: live Virtuoso + OA license + Calibre (AutoVia DRC) + LSF (RsCalc parallel) + real OA library cellviews + GDS stream in/out. **None available in SUT sandbox** → B-synthesized with stub runners.
- Benign errors in batch: `*Error* eval: unbound variable - argus_Menu_Symbol` (.cdsinit), `ld.so: libstdc++.so.6 LD_PRELOAD ignored` — don't affect results.
- The flow-orchestrator archetype (multi-runner loop + cross-iteration state + convergence + early abort) is **distinct** from single-runner agent-generator archetype (PwrViaAgentGen-001 r399 = single AutoVia agent .il generator, no loop).

## case built (r405)
- case_id: `EDA-Eval-DesignFlow-RsCalcFlowOrchestrator-001`
- archetype: flow-orchestrator (B-synthesized, L2)
- gold: `run_rscalc_flow.py` — parse_config + run_rscalc/run_autovia/run_powerfill (subprocess) + check_convergence + main loop
- visible A: common.config(cellName=testa, targetReduction=0.3, maxIterations=3) + flat-resistance stubs (never converges, runs full 3 iters — mirrors real trace outcome)
- hidden B: common.config(cellName=inv_chain, targetReduction=0.4, maxIterations=4) + decreasing-resistance stubs (converges at iter 2, early-abort, total_iters=2)
- check.py k=17 a-q (zip/compile/argparse/AST/subprocess/B-exit0/JSON/keys/baseline/total_iters/converged/iterations/bestCell/bestFailCount/call-counts/cross-input-A/cell-chaining)
- 6 negatives all FAIL (NEG_RC=0): empty_shell(c), print_expected(e), core_deleted(j), hardcode_a(d), no_loop(j), always_converge(j)
- §4.9 three-fake: empty(c)/print(e)/core(j) all FAIL ✓
- ref self-test 17/17 PASS ✓
- jsonl_C 307→308; ledger_C qwkmc claimed→case; pg_layout 37→38
