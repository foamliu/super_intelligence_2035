# Deepread: r239 — yzwang kxqt7 — DRC per-rule time ranking

## Trace
- session: `1791967362296_kxqt7` (yzwang@hfeg0pkn001/10.129.2.10, mc=177)
- keywords: drc:662 pdk:306 calibre:298 analog:67 .def:27 pyaether:5 cmos:5 .gds:5
- 108 msgs (58 user / 50 assistant), agent=lead, model=deepseek-v4-flash, status=failed (policy blocked execution)
- NEW user (yzwang not in prior shard-C cases)
- session.json title: "/home/pdk/yzwang/06_AI_workspace/test6/rundrc.log，这是一个drc的详细过程，请帮我统计每条"
- real log: /home/pdk/yzwang/06_AI_workspace/test6/rundrc.log (20.3MB, 323380 lines, Calibre DRC-H, 32-core, ~16h)

## User real intent (single-turn need, evolved through 11 corrections)
U#0: "rundrc.log 是一个drc的详细过程，请帮我统计每条rule所花的时间，并根据时间长短由长到短总结一份文件给我。"
→ parse DRC log, per-rule time, sort long→short, output file.
U#2: corrected — calibrelogview GUI shows CPU Total per rule step;统计每条rule所用总时间.
U#3: **the spec** — find all "CPU TIME = X  REAL TIME = Y" lines; if PREVIOUS line has a variable with ≥2 underscores, variable name = before the colon; aggregate total CPU/REAL per prefix.
U#4: **the 2 key pitfalls** — (1) variable name truncated at FIRST `::` (DNW_CL_015_00::check_CaveWidth_StepWidth<1>::X → DNW_CL_015_00); (2) the 9 variants of DNW_CL_015_00 must all aggregate to one entry.

## Assistant journey (108 steps)
- Read log by slices (read_files 30×), discovered file is 323380 lines (not 50k); rule-exec phase ~210k→end.
- Wrote parse_rule_time.py via `editor` tool (8 edits), iterated through user's 2 corrections.
- Policy (agent-policy-engine hello_world profile, owner-mismatch) BLOCKED execution → could not run script; status=failed. Final script delivered to /home/yzwang/parse_rule_time.py.
- Final script logic: cpu_real_re + var_re=`(\S+?)::\S+\s+\(HIER` (NON-GREEDY after U#4 fix), pending_vars collected since last CPU TIME line, ≥2-underscore filter, equal-split multi-var, sort by REAL desc.

## Real golden (from /home/yzwang/rule_time_summary.txt, 201KB)
- 2235 rules (≥2 underscores), TOTAL CPU=650742s REAL=59303s
- top-1: DNW_CL_015_00 (CPU=9.0, REAL=27082.0, Ops=9) — the colon-truncation test case
- top-2: NW_CL_019_00 (REAL=27024, 9 ops), top-3: NW_F_023_00 (REAL=26915, 1 op)

## DISTINCT from r237 DrcLogTeardownReport
- r237: module-level 4-section teardown (totals/modules/cumulative/connects/redundancy/top_ops/vhc_f_ratio/optimization) — phase timing + redundancy + VHC compression.
- r239 (this): rule-level prefix aggregation of CPU/REAL time, sorted desc — colon-truncation + ≥2-underscore filter + multi-var equal-split.
- Different parse target (rule op lines w/ ≥2 underscores, truncate at first `::`), different output (sorted prefix→CPU/REAL/ops ranked list vs multi-section report). Genuinely complementary.

## Log format (rule execution phase)
```
<RULE>::<substep> (HIER TYP=1 CFG=1 HGC=0 FGC=0 HEC=0 FEC=0 IGC=0 VHC=F VPC=F)
CPU TIME = <int>  REAL TIME = <int>  LVHEAP = ...  SHARED = ...  OPS COMPLETE = ...  ELAPSED TIME = <int>
DRC RuleCheck <RULE> COMPLETED. Number of Results = <int> (<int>)
```
Deep-suffix: `DNW_CL_015_00::check_CaveWidth_StepWidth<1>::X (HIER ...)` → prefix `DNW_CL_015_00`.
Multi-var: 2 consecutive HIER lines then 1 CPU TIME line → equal split.
Module lines (no HIER var): `--- MODULE COMPLETED. CPU TIME = X REAL TIME = Y` → other bucket.
Non-rule vars: `vintcore.M1` (0 `_`), `M1_layer` (1 `_`) → other bucket.

## Design (B-synthesized)
- A_log (trace-grounded): real rule prefixes (DNW_CL_015_00 w/ 9 deep-suffix variants, NW_CL_019_00, NW_F_023_00, PCU_ENC_016_00_Auto, PG_S_085_01, CT_F_021_01, M1_S_030_00_vfsbln_vintbus) + non-rule (vintcore.M1, M1_layer) + multi-var (M4_S_030/031) + module lines. A top-1 = DNW_CL_015_00 (REAL 27082, matches real golden).
- Hidden B (kills hardcode): DIFFERENT rule names (AA_BB_001_00, CC_DD_002_00, EE_FF_003_00, GG_HH_004_00_Auto, II_JJ_005_01, KK_LL_006_00_c) + non-rule (vvcore.M2, M2_layer) + multi-var (NN_OO/PP_QQ). B top-1 = AA_BB_001_00 (REAL 35000) ≠ A top-1.
- B2 (degraded): B with 2 ops' HIER lines losing `::` → those ops fall to other bucket; SUT must handle gracefully.
- B3 (empty): header only → SUT exits 0, 0 rows, no traceback.
- SUT deliverable: parse_rule_time.py (stdlib only, argv[1]=log path, prints ranked table to stdout). MUST generalize to B (different rules).
- check.py: embedded reference parser (non-greedy var_re, ≥2-underscore filter, equal-split multi-var), recomputes golden from B/B2/B3 logs; 16 conditions (a-p).

## 16 conditions (a-p)
(a) zip+1py≥300B UTF-8 no-NUL (b) py_compile+stdlib-only (c) exit0+nonempty table on B (d) row count==goldenB (e) var set==goldenB (f) per-rule cpu/real≈goldenB (g) sorted REAL desc (h) no `::` in vars (colon-truncate) (i) non-rule vars excluded (≥2-underscore filter) (j) multi-var equal split (k) anti-hardcode top1=B not A (l) ops count per rule (m) B2 degraded handled (n) B3 empty exit0 no traceback (o) 3-seed sha256 stable (p) missing path exits nonzero.

## Self-verify
- golden_solution.py: 16/16 PASS (cond k: sut=AA_BB_001_00 gB=AA_BB_001_00 gA=DNW_CL_015_00 ✓)
- 5 negatives all FAIL (empty_shell/print_expected/core_deleted/naive_hardcode_a/greedy_regex); §4.9 three-fakes all FAIL; ALL_NEG_FAIL=True.
- k_check=16=k_rationale≥8 ✓.
