# Deepread: 1794447438232_5bngi (tabtao @ hfeg0pkn001, mc44, verification)

## Trace summary
- 106 msgs, ~10 real user turns. Domain: verification (Formality) + synthesis (DC).
- Session about SVT characterization test chip synthesis+formal flow (/proj/lacaa/TV1_TestChips/CXTV1_DBC001A/flow/syn/syn_SVT/).

## User turns
- U#1 (msg0): dc.log errors at lines 41969/42112-42117/50397, analyze
- U#24 (msg37): "41969/42112-42117 同一原因?"
- U#26 (msg41): fm_.log "Verification INCONCLUSIVE 如何理解，怎么解决"
- U#33 (msg55): "aborted的点是在哪里？"
- U#35 (msg59): **PRODUCE-TASK** "把这些点通过set_dont_verify_points 写到scripts/dont_verify.tcl, 把 Makefile 的 FM_MODE 补上"
- U#43 (msg74): dc.log warnings 469/486/515, how to judge map
- U#45/55/58 (msg78/94/100): syn_SramEDABistGrp2 Makefile + dc.log lib Error

## Core produce-task (U#35, msg59) — agent response (msg60-73)
Agent read fm.tcl (match@253, verify@265), tried editor to create dont_verify.tcl + source in fm.tcl → blocked by agent-policy (writableRoots only /home/tabtao). Provided pastable content:

### 33 aborted points (fm_.log lines 680-712)
Format: "Compare point <NAME> is aborted"
- A. Flattened (underscore): TOPPMBLK_Blk92028_FDiVBlk_Blk91011/41014/41017/41020_data_reg_[0..3] (16 DFF)
- B. Hierarchical (slash): TOPTMINVRINGBLK_Blk92019/FDiVBlk_Blk2502/4123/81/889/data_reg_[0..3] (16 DFF)
- C. Port: TMOut (1)
- Bit suffix = `_N_` (trailing underscore), e.g. data_reg_0_
- "Verification INCONCLUSIVE (Equivalence checking aborted due to complexity)"

### Deliverable (3 parts)
1. scripts/dont_verify.tcl: set_dont_verify_points with r:/WORK/${DESIGN_NAME}/<path> + data_reg_* wildcard for DFFs; port TMOut plain
2. fm.tcl: insert `source ${ROOT_DIR}/scripts/dont_verify.tcl` after report_unmatched_points, before "# Verify and Report"
3. Makefile: add `fm_r2g: FM_MODE = r2g`, `fm_g2g: FM_MODE = g2g`, add dont_verify.tcl to $(FM_DONE) deps
- DESIGN_NAME = STC_TC_DBC_SVT

## A-faithful judgment
User gives fm_.log path + Makefile + goal (write dont_verify.tcl with set_dont_verify_points + patch FM_MODE). Does NOT give: which points aborted, the TCL format, wildcard rules, naming-convention distinction. → A-faithful PASS.

## Deliverable feasibility
Deliverable = write scripts/dont_verify.tcl + modify fm.tcl + Makefile on private /proj/lacaa/ paths → INFEASIBLE in sandbox → B档 synthesis.

## B档 case plan: EDA-Eval-DesignFlow-FmDontVerifyGen-001
- Archetype: formality-aborted-point-extractor-and-dont-verify-tcl-generator
- Domain: verification, L1-B
- SUT script: parse fm.log aborted points → group DFF by data_reg_* wildcard (preserve flattened underscore vs hierarchical slash) → separate ports → generate dont_verify.tcl + patch fm.tcl (source line) + patch Makefile (FM_MODE) + report.json
- A: STC_TC_DBC_SVT, 33 points (16 flat + 16 hier + 1 port TMOut)
- B (hidden): different design/block/port names (cross-input guard defeats hardcoded_A)
