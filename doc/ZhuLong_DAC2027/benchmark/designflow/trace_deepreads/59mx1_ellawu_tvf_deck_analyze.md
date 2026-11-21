# Deepread: 59mx1 — ellawu TVF DRC deck 「分析总结」

**Session**: 1795000168376_59mx1 | **User**: ellawu | **Host**: hfeg0pkn001 | **mc**: 72
**Domain**: physical_verify (DRC TVF deck analysis) | **Track**: B (synthesized reframe)

## Trace Summary
- **User msg 0**: "分析总结" + attached `G5_CIP_AA_PG_dummy_fill_for_Stdcel.rule` (972-line TVF DRC deck)
- **Assistant**: read full deck (972 lines), produced comprehensive Chinese analysis covering:
  - File positioning: Calibre TVF DFM dummy fill deck (not DRC check), CXMT G5 (10G5_CIP)
  - Input config: LAYOUT PATH (CkSplit4En45X2_R22.gds), LAYOUT PRIMARY, INCLUDE calibre.layer, DFM RDB GDS (AA_PG_DUM.gds)
  - Core params: 29 scalar `set VAR` + 5 `[expr]` derived (PRB_ENC_AT4_X, PGATE_MaxW, NGATE_MaxW, B_Region_Width, jog_height)
  - Asymmetric TOP/BOT: PRB_ENC_AT4_Y_{TOP,BOT}, PRB_ENC_PG_Y_{TOP,BOT} (v2.5 change)
  - Processing flow: AA DUMMY2 insertion (A/B/C region decomposition) + PG DUMMY insertion (B/A/C region + DFM JOGCLEAN + SIZE UNDEROVER)
  - Revision history: v1.0(2023/11)→v2.6(2026/02); v2.5 PG_PGDummy_MaxSpace 0.5→0.574 + Top/Bottom asymmetry; v2.6 AC region `<`→`<=`
- **N_msgs**: 10 (user attach → assistant reads → assistant produces summary)

## Case: EDA-Eval-DesignFlow-TvfDeckSpecExtract-001
- **Reframe**: user intent "分析总结" is open-ended markdown summary. Reframe to require a structured JSON spec extraction script (`deck_spec_extractor.py`) that parses any TVF deck and produces `deck_spec.json` (17 fields) + `summary.md`.
- **Deliverable**: `outputs/submit.zip` containing `deck_spec_extractor.py`
- **Script interface**: `python3 deck_spec_extractor.py <deck.tvf> <out_dir>`
- **Hidden B**: modified deck with 10 changed scalar values + changed gds names (R22→R23) + changed output_gds (AA_PG_DUM.gds→AA_PG_DUM_v2.gds). Hardcoding A values fails on B.
- **k_check**: 16 conditions (a-p)
- **Sister-turn check**: yt3zr (r897) was same user ellawu + same deck family, but different deliverable (variable extraction + reverse-lookup script vs full spec sheet extraction). Different judge, different B deck, different output schema. NOT sister-turn duplicate.
- **Self-verify**: ref solve.py PASS 16/16 + 4 negatives FAIL distinct + §4.9(a)(c) FAIL + roundtrip sha256 92408eaa ✓
