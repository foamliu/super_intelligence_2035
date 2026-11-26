# Deepread: o2192 — TVF .ev deck VIA-enclosure QA audit

**Session**: `1794475261629_o2192` · **User**: kenwang · **Host**: hfeg0plg16 (10.129.32.47)
**mc**: 41 · **Keywords**: `drc:78;calibre:68;pyaether:7` · **Domain**: physical_verify
**Fetched**: 2026-11-17 (messages.json 771KB, 73 msgs, agent=lead)

## User intent (verbatim)

**U#1** (the actual task — msg index 1 in messages array):
> `~/zl/4_5_53_Vy.ev 文件，请帮我QA一下针对 rule 中 的 写法是否存在问题，在该文件中，修改了原来的检查方法，现在的检查方法是参考 /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/Ref/calibre_n7.drc 文件的 VIA6.EN.1__VIA6.EN.6 及后续的rule ，参数及描述几乎相同，所以写法参考的它的写法，现在我需要你判断一下是否存在写法及数值上的error`

**U#0** (context summary from previous session — compacted):
> 对 `/home/kenwang/zl/6_3_BEOD_dummy_rules.ev` 进行 QA 检查，验证规则描述中"This check is only applied to"的允许金属层，确保规则名称末尾的实际检查层（如 `Mn_Dum_S_1_1_M5`）不包含意外的金属...

This is a **continuation session** — U#0 is a compacted summary of prior work on a different .ev file (6_3_BEOD_dummy_rules.ev), U#1 is the new task on 4_5_53_Vy.ev.

## Agent flow (73 msgs)

1. **list_allowed_files** /home/kenwang/zl/ → found 4_5_53_Vy.ev + 6_3_BEOL_dummy_rules.ev + other files
2. **read_files** 4_5_53_Vy.ev (1517 lines, TVF format with `#loop` directives, VIA enclosure rules)
3. **read_files** /rundata/lacaa/V0/.../calibre_n7.drc (reference deck, 81K+ lines) — VIA6.EN.1__VIA6.EN.6 rules at lines 79602-79741
4. **shell-runner** wrote extraction script to grep VIA6.EN.* rule blocks from reference deck
5. **read_files** reference deck context: derived layer definitions (M6, VIA6_M6_P76L1, SVIA6_38_M6_P76L2, VIA6i)
6. Multi-round comparison: .ev vs reference deck — found copy-paste errors where upper-metal-half rules accidentally reference lower metal (M#-1 instead of M#)
7. **write_file** qa_vy_report.md (160 lines, A-F 6 sections)

## Agent's QA findings (from final msg #72)

**7 deterministic errors (A1-A7, copy-paste class, must fix)**:
- A1 L348 EN_1_4 M# half: `RECTANGLE ENCLOSURE SVIA#-1_38_M#_CHK M#-1` — via selected by upper M# (0.076) but enclosure measured on **lower M#-1**, should be `M#`
- A2 L505 EN_2_1 M# half: `SQR_VIA#-1i_58 INTERACT VIA#-1_M#-1_CHK` — used lower-metal bucket, should be `VIA#-1_M#_CHK`
- A3 L559 EN_2_5 M# half: same as A1, enclosure `M#-1` should be `M#`
- A4 L584 EN_2_11_2 M# half: `NOT INTERACT (M#-1 WITH WIDTH < 0.06)` should be `M#`
- A5 L750 EN_6_2 M# half: `ENC VIA_CHK M#` should be `VIA_CHK_1` (suffix typo)
- A6 L769 EN_6_*: similar pattern
- A7: another copy-paste variant

**2 numerical/naming issues + 6 systemic differences** (need confirmation).

## Error patterns abstracted

Three classes of copy-paste errors detected:
1. **METAL_WRONG**: upper-metal-half rule (selector `M#_CHK`) whose `ENCLOSURE`/`ENC` measurement target is `M#-1` (should be `M#`)
2. **SUFFIX_TYPO**: bare token `VIA_CHK` (without `_<digit>` suffix) — convention is `VIA_CHK_1`
3. **WIDTH_FILTER_WRONG**: upper-metal-half rule with `M#-1 WITH WIDTH` filter (should be `M#`)

## Reframe (mock-behavioral)

Real .ev deck (1517 lines) + calibre_n7.drc (81K+ lines) are path-dependent (require .75 + license). Reframe to pure stdlib: synthetic mini TVF deck (~15 lines) with `#loop`/`#endloop` directives, EN rules with embedded copy-paste errors. Candidate parses deck, classifies EN rule halves, detects 3 error classes via regex, outputs deterministic JSON.

**New sub-type**: `tvf-ev-deck-via-enclosure-qa-audit` — distinct from:
- r713 NwDerivedLayerRuleExtract (SVRF deck derived-layer closure + rule extraction)
- r710 DrcRunStatusAnalyze (DRC log status parsing)
- r704 DrcDeckRuleUpdClassify (deck-block update classification)

## 11-15 task初衷 B类复活

This is a QA/analysis task. Under old rules, "QA explain" might be judged weak/analysis-only. Under new standard (11-15), analysis/Q&A/explain are legitimate user intentions → revived.

## Case built

- **Case ID**: EDA-Eval-DesignFlow-VyEnclosureQaAudit-001
- **Domain**: physical_verify · **Tier**: L1 · **档位**: B (synthesized)
- **k_rationale = k_check = 25** (≥8 GATE PASS)
- **Asset A**: vy_deck_A.ev (14 lines, 8 rules, 3 violations)
- **Hidden B**: vy_deck_B.ev (21 lines, 10 rules, 4 violations at lines 14/15/17/19 — all disjoint from A's 9/10/11)
- **Hidden B2**: vy_deck_B2.ev (5 lines, 1 rule, 0 violations — minimal edge)
- **3 negatives**: empty (→c fail) / print_expected (→f fail) / delete_core (→h fail) — all FAIL with distinct first_fail
- **Self-verify**: reference 25/25 PASS, negatives all FAIL, determinism 2x, anti-hardcode A∩B disjoint ✓
