# Deepread — sid 1794447924614_wf6ph · OC time fitter (analog_context)

**Session**: `1794447924614_wf6ph.messages.json` (853 msgs, 2.5 MB)
**User**: xuelianf @ 10.129.33.24 (host hfeg0pbn07), mc=95
**Domain**: analog_context (DDR5 tOC column access time)
**Round**: r634, shard D
**Verdict**: ACCEPT (clean produce-task at U3, iterated U4-U9)

## Trace walkthrough

| Turn | Role | Content | Verdict |
|---|---|---|---|
| U0 | user | layout M1A/M3A coupling Q&A | REJECT (pure Q&A) |
| U1 | user | read group123_byBL_M0A2M0A_coupling_all.sh | REJECT (file-read) |
| U2 | user | read result_summary.csv | REJECT (file-read) |
| **U3** | **user** | **OC_1=1.5ns/OC_2=2.5ns/OC_3=3.5ns. Fit Vtarget vs OC_time for 4 groups (D0_SenW, D1_SenW, D0_SenB, D1_SenB). D0_OC=D0_SenW∩D0_SenB, D1_OC=D1_SenW∩D1_SenB, TPC_BL0_OC=avg(D0_OC,D1_OC)** | **ACCEPT (clean produce-task)** |
| U4 | user | iterate: output 4 cols (组,D1_OC,D0_OC,Avg_OC) appended | format iteration |
| U5 | user | iterate: insert 4 cols at FRONT (two-section CSV), new python program | format iteration |
| U6 | user | optimize: no process output, only missing/done | format iteration |
| U7 | user | add 5th col final_OC(ns) only for BL0 = avg(BL0_Avg,BL1_Avg) | spec refinement |
| U8 | user | uncomputable groups also output condition, values empty | spec refinement |
| U9 | user | complain hardcoded DIRS not flexible | refactor request (out of scope for case) |

## Task essence (U3, the produce round)

Input `result_summary.csv` columns: `directory,OC_1_Vtarget,OC_2_Vtarget,OC_3_Vtarget`.
Directory path regex: `./({condition})/({macro})/({GroupN_BLx})/({signal})` where macro ∈ {TPC,X8C}, signal ∈ {D0_SenW,D1_SenW,D0_SenB,D1_SenB}.

Algorithm:
1. Group rows by (condition, macro, GroupN_BLx). Each group has 4 signals.
2. For each signal: linear-fit V = m·t + c through 3 points (1.5,OC_1),(2.5,OC_2),(3.5,OC_3).
   - Real script uses `numpy.linalg.lstsq` (3-point OLS).
3. D0_OC = time-intersection of D0_SenW and D0_SenB lines: t = (c_SenB−c_SenW)/(m_SenW−m_SenB).
4. D1_OC = time-intersection of D1_SenW and D1_SenB lines.
5. Avg_OC = (D0_OC + D1_OC)/2.
6. final_OC (BL0 only) = (Avg_OC(BL0) + Avg_OC(BL1))/2, paired by same (condition,macro,GroupN).

Output (U5/U7): two-section CSV separated by blank line:
- Front: `condition,group,D1_OC(ns),D0_OC(ns),Avg_OC(ns),final_OC(ns)` — one row per group, final_OC only BL0
- Back: `directory,OC_1_Vtarget,OC_2_Vtarget,OC_3_Vtarget` — all original rows in order

U8: uncomputable groups (missing signals or parallel lines) still output condition+group with empty OC values.

## Gotchas (6)

1. **3-point least-squares** (not 2-point slope): hidden inputs have non-collinear 3 points; OLS vs 2pt-slope differ by ~0.05ns on D0_OC. Real script uses numpy.lstsq.
2. **Intersection formula direction**: t = (c_SenB−c_SenW)/(m_SenW−m_SenB). Swapping numerator/denominator signs → wrong answer.
3. **D0 and D1 both computed**: two independent intersections, can't skip one.
4. **final_OC only BL0 rows**: = (BL0_Avg + BL1_Avg)/2, paired by same condition+macro+GroupN. BL1 rows' final_OC is empty.
5. **Uncomputable groups output empty**: parallel lines (m_SenW==m_SenB) or missing signal → condition/group row emitted with all OC fields empty (per U8).
6. **Back section preserves all original rows** in input order (including unparseable ones).

## Portability

Real script uses numpy.linalg.lstsq + hardcoded 96-entry DIRS array. For SUT: pure stdlib OLS (closed-form m=(n·Sxy−Sx·Sy)/(n·Sxx−Sx²), c=(Sy−m·Sx)/n), read CSV by header, parse directory by regex. No numpy dependency. OC times (1.5/2.5/3.5) are part of task spec (fixed mapping), not sample-specific hardcoding.

## Case artifact

- Case ID: `EDA-Eval-DesignFlow-OcTimeFitter-001`
- Domain: analog_context
- visible_A: 3 conditions × 2 BL groups × 4 signals = 24 rows (collinear, clean intersections)
- hidden_B: 3 conditions × 2 BL groups × 4 signals (NON-collinear, forces 3-pt OLS)
- hidden_C: 3 conditions with parallel-lines group + missing-signal group + normal group
- check.py: 16 conditions (a-p), k_check=k_rationale=16
- Self-verify: REF PASS 16/16; 3 fakes FAIL (d/c/g distinct labels)
