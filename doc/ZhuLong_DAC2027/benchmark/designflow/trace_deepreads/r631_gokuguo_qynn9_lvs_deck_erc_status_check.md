# r631 deepread: gokuguo qynn9 LVS deck ERC status check

- **session**: 1792111662812_qynn9.messages.json
- **user/host**: gokuguo @ hfeg0plg55 (10.129.35.74)
- **mc**: 47 (lvs:296;calibre:45;virtuoso:21;pex:18;.gds:11;netlist:10;.cdl:10)
- **domain**: physical_verify
- **trace**: 48 msgs, 3 real user turns, session file in subdir `<sid>/<sid>.messages.json`

## User intent (verbatim)

U#0: `帮我检查一下：/home/gokuguo/Desktop/vir_setup_cant_remove/Batch_LVS/35H_1P18M_18F1xa1x1xb1ya6y2yy2yx2z_LVS_Cal_V0d1_Rev06_Test07.lvs 这个文件，是否有ERC`

U#1: `可是现在的ERC`

U#2: `可是我看脚本，ERC部分不是被注释掉的吗？`

## Deck ERC structure (real file, 11171 lines, Calibre v2023.3_14.8 SVRF)

**Header #DEFINE switches (lines 22-64):**
- L28: `#DEFINE ERC_CHECK TRUE  //{TRUE/FALSE}` — master ERC switch ON
- L37: `#DEFINE ERC_PATHCHK TRUE   //{TRUE/FALSE}` — ERC path check ON
- L46: `#DEFINE NWELL_FLOATING_CHECK TRUE` — floating NWELL check ON
- L55: `#DEFINE NWELL_NOT_TO_POWER_CHECK TRUE` — NWELL-not-to-power ON
- L64: `#DEFINE PWELL_NOT_TO_GROUND_CHECK TRUE` — PWELL-not-to-ground ON

**ERC output config (lines 447-449):**
- L447: `ERC RESULTS DATABASE "erc.db"` — active (not commented)
- L448: `ERC SUMMARY REPORT "erc.rep"` — active (not commented)
- L449: `//ERC MAXIMUM RESULTS ALL` — **COMMENTED** (the line user noticed)

**Footer guards (lines 11026-11045):**
- `#IFNDEF ERC_CHECK TRUE` / `#IFNDEF ERC_CHECK FALSE` / `SVRF ERROR "...ERC_CHECK...wrong"` / `#ENDIF` x2
- Same pattern for ERC_PATHCHK, NWELL_FLOATING_CHECK, NWELL_NOT_TO_POWER_CHECK, PWELL_NOT_TO_GROUND_CHECK

## Gold analysis (agent's conclusion)

1. ERC IS enabled: `ERC_CHECK TRUE` at line 28
2. ERC_PATHCHK TRUE, all 3 NWELL/PWELL sub-rules TRUE
3. ERC output: RESULTS DATABASE + SUMMARY REPORT both active; only MAXIMUM RESULTS (line 449) commented
4. The commented line 449 does NOT disable ERC — it only sets the max-results limit
5. `batch_lvs.py` only does path substitution (LAYOUT/SOURCE, VIRTUAL CONNECT), does NOT modify ERC lines

## B档 reframe (grounded-extraction-tool)

deliverable = `lvs_erc_check.py <deck.lvs> <output.json>`: parse Calibre SVRF LVS deck → structured JSON
(erc_check/erc_pathchk/nwell_rules/erc_output/commented_erc_lines/footer_guards/verdict).

- asset A: lvs_deck_a.lvs (compact 185-line deck, ERC_CHECK TRUE, ERC_PATHCHK TRUE, output 2 active 1 commented)
- hidden B: lvs_deck_b.lvs (175 lines, ERC_CHECK FALSE, ERC_PATHCHK FALSE, results_database commented, summary_report+maximum_results active, verdict erc_disabled)
- hidden B2: lvs_deck_b2.lvs (172 lines, ERC_CHECK TRUE, ERC_PATHCHK FALSE, all 3 output active, verdict erc_enabled — anti-hardcode cross-check)
- check.py: 17 conditions (a-q), runs on B, all independently failable
- 3 negatives (naive_empty/print_expected_A/deleted_core) all FAIL
