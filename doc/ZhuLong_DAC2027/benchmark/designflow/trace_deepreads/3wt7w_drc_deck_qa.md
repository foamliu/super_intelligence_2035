# trace_deepread: 3wt7w — Calibre SVRF DRC deck read-only QA

- **session**: `1793602560932_3wt7w`
- **user / host**: kenwang / 172.16.8.192 (hfeg0plg16)
- **agent**: lead
- **match_count**: 24 (keywords calibre:104; drc:100)
- **domain**: physical_verify (Calibre SVRF DRC deck QA)
- **deck under QA**: `/home/kenwang/zl/SAQP_M1.rules` (2376 lines, 122647 bytes, CXMT SAQP M1 metal layer)
- **size**: 446644 bytes / 44 messages (single deep QA session, 2026-11-04 → 2026-11-05)
- **ledger history**: parked in shard D ledger (r270, 2026-11-05) under old "Q&A unfit" rule (note: "peek_D270 unfit (Q&A/doc/root-cause/mid-conv/skill-scaffold/NOFILE/boilerplate)"); revived by shard C r814 via `mark --force` after 2026-11-15 §二 reaudit restored Q&A/analysis classes as buildable.

## User intent (real, from trace)

Single substantive task: **read-only QA of a Calibre SVRF DRC deck — find errors, do not modify the file.** Two passes:
1. First pass: "读 SAQP_M1.rules，按 drc-rule-dev skill 验收标准做 read-only QA，找错误" (msg 0 context summary + msg 11 skill instructions).
2. Re-QA after user edits: "用户改完后让 re-QA 看哪些 error 修了、哪些还在、有没有新引入的问题" (msg 12 thinking + msg 27 "go on").

User's literal spoken turns are mostly "go on" / skill-instruction re-injection; the substantive intent is the QA task itself (auto-injected context summary in msg 0 is harness-prepared, not free-form user text — so this is a 档 B synthesized case, not 档 A trace-faithful).

## What the assistant actually did

Wrote a series of **read-only bash/grep/awk QA scripts** and ran them via `run_approved_command` (shell-runner profile), then read the outputs via `read_files` and compiled a structured findings list:

- `qa_m1.sh` — curated layer-def check + cross-file duplicate check
- `qa_m1b.sh` — brace location + EXTENT/EXTENTS checks + broad layer presence
- `qa_m1c.sh` — reference-deck lookups (n7 / 35H / target) + WITH WIDTH attestation
- `qa_m1d.sh` — WITH WIDTH prefix form attestation
- `qa_recheck1.sh` — file-state + A1 REGIO / A8 M1_DN_7 DENSITY params / A9 M1_DN_10 / A12 M0_NOT_M0Ci
- `qa_recheck2.sh` — operator-name mismatch + bracket checks
- `qa_recheck3.sh` — DN VARIABLE definitions + M1_DN_3_E cross-reference
- `qa_recheck4.sh` — tab-aware undefined-token scan (the definitive one, msg 38)
- `qa_recheck5.sh` — M1_DN_7 DENSITY + M1_DN_10 X1/X2 attestation

Reference decks used for attestation: `calibre_n7.drc`, `35H_DR...`, target deck (in `~/.cline/skills/drc-rule-dev/references/decks`).

## Findings the assistant produced (categorized)

The assistant's final findings list (from msg 4/10/23/26/31/34/37/43 thinking blocks) used categories A1-A17, B18-B20, C21-C26, D27-D28, E. After the re-QA, each was marked FIXED / NOT FIXED / RESOLVED. Concrete errors confirmed STILL OPEN in the deck (post-user-edit, 2376-line version):

| # | category | line | detail |
|---|---|---|---|
| A8 | density_low_operands | 1980 | `DENSITY M1_CHECK M2_CHECK M3_CHECK CHIP_CHECK >0` — 4 layer operands; EV2 reference has 5 (with OCCD_FM) |
| A14 | operator_name_mismatch | 2299 | `M1_CA_GE60 = ... < 0.060` — name says GE60 (>=0.060) but body uses `<` |
| A16 | missing_enc_v0r_side | ~1134 | `M1_EN_3_1_2` block has `ENC V0G_Check1_SIDE` + `ENC V0D_Check1_SIDE` but NO `ENC V0R_Check1_SIDE` |
| A17 | unquoted_dotted_filename | 1874 | `PRINT M1.DN.2.3.density RDB M1.DN.2.3.RDB.density` — bareword with dots, other lines use quoted `"./DENSITY_RDB/..."` |
| C21 | extents_typo | 2332 | `EXTENTS ALL_M1` — should be `EXTENT` (L2320/L2347 use correct `EXTENT`) |
| C22 | undefined_token | 2332 | `CHIP_EDGE_a` used but never defined (correct token is `CHIP` per L2320) |

FIXED after user edit: A1 REGIO typo, A2 empty body M1_W_1_1_3, A3 junk v/h lines, A4 `< M1_S_5`, A5 missing VARIABLE triplets, A13 M1_R_19.

## Reframe (档 B)

A 档 gold = the free-text markdown QA findings report the assistant produced (msg 4/10/23/26/31/34/37). This has **no ≥8 hard-assertion teeth** — a print-only stub printing the same-shaped markdown would PASS, violating §4.9 退化提交回归.

**Reframe**: extract the assistant's actual scanning algorithm (read deck → run multi-category structural scans → emit findings with line+snippet) into a pure-stdlib Python tool `drc_deck_qa_scanner.py` with 9 detection categories:
1. `regio_typo` — `REGIO` not part of `REGION`
2. `extents_typo` — `EXTENTS` (correct: `EXTENT`)
3. `empty_body_block` — `NAME { }` with only `@` comments
4. `unquoted_dotted_filename` — bareword `X.N.N.Y` outside quotes
5. `operator_name_mismatch` — assignment name suffix `_GE/_LE/_GT/_LT<n>` vs operator on the line
6. `lt_rule_name` — `< UPPERCASE_IDENT` (RHS is a rule name, not a number)
7. `undefined_token` — identifier used after INTERACT/COIN/INT/EXT/ENC, never defined
8. `density_low_operands` — `DENSITY ... <cmp> N` with <5 layer operands
9. `missing_enc_v0r_side` — `*_EN_3_*` block with V<n>G SIDE ENC but no V<n>R SIDE ENC

Hidden B = synthetic ST22 deck (structurally different: ST22 process, V1G/V1D/V1R vias, DN.5.7, CHIP_XY, ST22_CA_GE80, ST22_EN_3_4_5). 17 assertions (a-q), anti-hardcode on 11 A-specific literals.

## Case

`EDA-Eval-DesignFlow-DrcDeckQaScan-001` → `EDA-Eval-DesignFlow_C.jsonl` (503→504). k_check=17 (labeled a-q). Ref PASS 17/17; 4 negatives FAIL at distinct points (b/q/j/i); §4.9 (a)(b)(c) 三假全 FAIL; determinism 2x byte-identical; negative_selftest ALL_NEG_FAIL=True.

This is C 域档 B reframe 第 8 例 (after LvsConfigReport/Mt2FillDecision/AutoViaAgentGen/TvfDeckAnalyzeReport/PgDummyFlowAnalyze/TvfDeckOutputVarTrace/VirtuosoErrorDiag), and the first **multi-category QA scanner** reframe (prior 7 were single-algorithm extractions).
