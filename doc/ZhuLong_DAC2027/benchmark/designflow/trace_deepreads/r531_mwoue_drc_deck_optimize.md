# Deepread r531 — mwoue DRC Deck Optimize

## Trace
- **session**: 1791444783469_mwoue
- **user**: miccao @ hfeg0plg92
- **mc**: 726 (drc:10032;calibre:4899;lvs:199;.gds:171;aether:96;gdsii:85;pyaether:54;pdk:52)
- **domain**: physical_verify
- **msgs**: 497
- **USER#0**: "根据/home/miccao/zl/rep/DRC_Log_Analysis_DDR5TOP_DFM0909.txt这份报告，将deck进行修改，只修改报告里的优化内容，然后将新deck放到/home/miccao/drc下，新deck叫newdeck"

## Task Analysis
Produce-task: user provides a DRC log analysis report + an original Calibre DRC deck (calibreDFM.rule), asks assistant to apply the report's optimization recommendations to produce a new deck (newdeck).

**Report structure** (3 optimization suggestions):
1. **建议1 (P0)**: R_C_MT2_F_01_M — A0 = M0C_Total WITH WIDTH < 0.102 takes 16853s (83.4% of run). Fix: spatial pre-filtering with SIZE MT2_CORE BY 0.35 edge band → M0C_sub → A0 = M0C_sub WITH WIDTH. Expected 84-94% reduction.
2. **建议2 (P1)**: R_C_M0C_ENC_01_H / ENC_02_H / PCU_S_06_H — M0C_Total INTERACT PC_Total creates 3.57B FGC intermediate layer. Fix: pre-filter with SIZE PC_Total BY 0.1 (or SIZE PCU_CORE BY 0.1) buffer. Report shows 改前/改后 for ENC_02_H only; assistant inferred pattern for ENC_01_H (uses M0_Final, not M0C_Total) and PCU_S_06_H (uses PCU_CORE, not PC_Total).
3. **建议3 (P2)**: Architecture-level hierarchy preservation — no deck changes.

**Assistant's actual modifications** (diff calibreDFM.rule → newdeck, 17 changed lines):
- ENC_01_H line 655: `A1 = COPY M0_Final` → `A1 = M0_Final INTERACT (SIZE PC_Total BY 0.1 UNDEROVER)`
- ENC_02_H line 665: `A1 = COPY M0C_Total` → `A1 = M0C_Total INTERACT (SIZE PC_Total BY 0.1 UNDEROVER)`
- MT2_F_01_M line 777: `A0 = M0C_Total WITH WIDTH < 0.102` → 5 lines (mt2_outer/inner/edge/M0C_sub) + `A0 = M0C_sub WITH WIDTH < 0.102`
- PCU_S_06_H lines 841-845: Added `M0C_near_PCU = M0C_Total INTERACT (SIZE PCU_CORE BY 0.1 UNDEROVER)` + 3 replacements of `M0C_Total INTERACT PCU_CORE` → `M0C_near_PCU INTERACT PCU_CORE`

## Synthesis
**Case**: EDA-Eval-DesignFlow-DrcDeckOptimize-001 (physical_verify, L2 offline boundary, k=15 a-o)

**Design**: Python script `drc_deck_optimizer.py <deck> <report> <out>` that:
1. Reads DRC deck (Calibre SVRF format) and report
2. Finds rules by name (R_C_MT2_F_01_M, R_C_M0C_ENC_01_H, R_C_M0C_ENC_02_H, R_C_PCU_S_06_H)
3. Applies 4 modifications:
   - MT2_F_01_M: insert mt2_outer/inner/edge/M0C_sub pre-filter, change A0 input
   - ENC_01_H/02_H: replace `COPY <var>` with `<var> INTERACT (SIZE PC_Total BY 0.1 UNDEROVER)` (dynamic var extraction)
   - PCU_S_06_H: insert M0C_near_PCU pre-filter, replace M0C_Total INTERACT PCU_CORE references
4. Writes modified deck

**A-side** (visible): deck_A (M0_Final variable, original rule order) + report_A (all 4 rules' 改前/改後 explicit)
**B-side** (hidden): deck_B (M0C_Remain variable, reordered rules + noise rules) — tests generalization

**Anti-hardcode guard** (cond o): B's ENC_01_H uses M0C_Remain (not M0_Final). If script hardcodes "M0_Final INTERACT ...", B output would be wrong. Correct behavior: extract variable from COPY statement dynamically.

## Self-Verification
- GOLD PASS: 15/15 ✓
- NEG1 (no modifications): 10 conditions fail ✓
- NEG2 (hardcoded M0_Final): 4 conditions fail (k,l,m,o) ✓
- NEG3 (wrong SIZE 0.5): 8 conditions fail ✓
- §4.9 Fake1 (empty zip): cond a fail ✓
- §4.9 Fake2 (wrong filename): cond a fail ✓
- §4.9 Fake3 (deck as script): cond c fail ✓

## Selection
120 candidates (mc≥10 + C keyword filter) → 23 unique sessions → 10 fresh (excluded 735 ledger entries) → peek 4 USER#0:
- aneeo (mc=1348): "sync checkPoints from config A to config B" → config sync, REJECT
- mwoue (mc=726): "根据DRC报告修改deck...新deck叫newdeck" → PRODUCE-TASK ✓
- itvhk (mc=760): "请完整跑一下prompt_flow.md整个过程" → run-existing, REJECT
- ukkn7 (mc=1627): "基于run_all.sh对数据文件跑完所有follow" → run-existing, REJECT

Per r527 discuss lesson: read USER#0 to distinguish produce-task (写/生成/修改/建) vs codebase-inflation/review/infra. mwoue has clear produce verb "修改...将新deck放到" = modify deck + produce newdeck.
