# r640 deepread: minjiex dn6lx — Calibre SVRF DFM property conditional-assignment rule interpretation

**session**: `1794465375311_dn6lx.messages.json` (subdir layout, flat file inside `1794465375311_dn6lx/`)
**user**: minjiex @ hfeg0plg90 (10.129.8.222)
**mc**: 12 (keywords: calibre:70; drc:13; aether:3; pdk:2; pyaether:1 — calibre dominant, strong C-signal, new user not in any known cluster)
**size**: 7 msgs / 1 real user turn (the other 3 "user" entries are ask_question reply + tool_result wrappers)
**domain**: physical_verify (Calibre SVRF DRC/DFM rule interpretation Q&A)

## User turn (verbatim, U#0)

```
A1 = (NET AREA RATIO PACT_PN PTR_SD_TO_IOPAD_n > 0) NOT INSIDE
A2 = DFM PROPERTY A1 RLESD_mark1  OVERLAP MULTI [-= (PERIMETER(A1) > 0) ? 1 : 0]  == 1
这两句DRC什么意思
```

User pastes 2 Calibre SVRF statements and asks "what do these two DRC statements mean". Single-turn conceptual analysis Q&A (no files, no execution). When agent asked for clarification (ask_question), user replied: "这是Calibre SVRF格式的DFM规则，来自某工艺代工厂" (Calibre SVRF DFM rule from a foundry).

## Gold (agent's structured explanation, ASST#6)

### Line 1 — `A1 = (NET AREA RATIO PACT_PN PTR_SD_TO_IOPAD_n > 0) NOT INSIDE`
| fragment | meaning |
|---|---|
| `NET AREA RATIO` | network-area-ratio op: per net, ratio of area on layer1 (PACT_PN) to area on layer2 (PTR_SD_TO_IOPAD_n); result is a derived layer carrying the ratio attribute |
| `PACT_PN` | active region (_PN distinguishes PMOS/NMOS) |
| `PTR_SD_TO_IOPAD_n` | source/drain marker layer connecting to I/O pad |
| `> 0` | filter: keep geometries whose net area ratio > 0 (net has active on both layers) |
| `NOT INSIDE` | binary boolean op; **incomplete** — missing second operand (would be syntax error in Calibre) |

### Line 2 — `A2 = DFM PROPERTY A1 RLESD_mark1 OVERLAP MULTI [-= (PERIMETER(A1) > 0) ? 1 : 0] == 1`
| fragment | meaning |
|---|---|
| `DFM PROPERTY` | DFM (Design for Manufacturing) attribute check construct |
| `A1` | input layer (the derived layer from line 1) |
| `RLESD_mark1` | ESD marker layer (foundry DFM auxiliary layer; RLESD = Rule ESD) |
| `OVERLAP MULTI` | check mode: overlap, multi-region |
| `[-= (PERIMETER(A1) > 0) ? 1 : 0]` | conditional property-assignment block: `[-= ...]` assigns per-overlap attribute; ternary `(PERIMETER(A1) > 0) ? 1 : 0` → 1 if perimeter>0 else 0 (effectively always 1 for real geometries) |
| `== 1` | final filter: keep only results with attribute value == 1 |

### Business intent
Foundry ESD DFM coverage check: line 1 locates active-area nets connected to I/O pad; line 2 checks those regions overlap the ESD protection marker layer. If A2 is empty → I/O active area lacks ESD protection → DRC violation.

### Agent's caveats
1. `NOT INSIDE` incomplete (likely excerpt omission, e.g. `NOT INSIDE PSUB`/`NWELL`).
2. `(PERIMETER(A1) > 0)` is tautologically true for any valid polygon → equivalent to `[-= 1]`.

## New-standard assessment (2026-11-15 intent audit)

Under OLD rules this would be REJECT as "analysis-Q&A thin, no produce-task, weak". Under NEW standard (2026-11-15 顶置初衷): analysis-Q&A is a legitimate user intent. The 2 statements contain a rich, distinct SVRF construct set:
- `NET AREA RATIO` (network-level area-ratio derived layer with layer-pair + comparison)
- `DFM PROPERTY` with `OVERLAP MULTI` mode
- conditional property-assignment block `[-= (FUNC(input) OP thresh) ? tv : fv]` with ternary
- cross-statement dependency (A2 references A1)
- trailing boolean op (`NOT INSIDE`, possibly incomplete)

**distinct vs r635 PgSvrfRuleAnalyze** (PG single-value edge-op rule, no DFM PROPERTY, no conditional assignment, no waive) and **r639 DrcSvrfRuleWaiveExtract** (waive-clause rule with edge bands). This is a **new sub-type**: `svrf-dfm-property-conditional-assignment-structured-extract`.

## Reframe (B档 mock-behavioral grounded-extraction-tool)

deliverable = `svrf_dfm_rule_analyzer.py <rule.svrf> <output.json>` — pure stdlib text parser (does not execute Calibre) → structured JSON extracting:
- per-statement: target / operation (NET AREA RATIO | DFM PROPERTY) / layer1,layer2 / comparison op+value / trailing op + operand + completeness / input_layer / property_layer / overlap_mode / assignment_op / condition{function,input,operator,threshold} / true_value / false_value / final_filter_op+value
- cross-statement dependency (A2->A1)
- layers_used / operations_used / counts

asset A = verbatim trace 2 statements (PACT_PN/PTR_SD_TO_IOPAD_n >0 NOT INSIDE [incomplete]; DFM PROPERTY RLESD_mark1 OVERLAP MULTI PERIMETER>0 ?1:0 ==1).
hidden B = S1/S2 (DIFF_NW/NPLUS_DIFF >0.5 NOT INSIDE NWELL [complete]; DFM PROPERTY DFM_antenna_mark2 OVERLAP SINGLE AREA>0.1 ?2:0 ==2) — 9 fields differ from A.
hidden B2 = T1/T2 (MET1_PAD/MET2_VIA >=0.2 INSIDE CORE; DFM PROPERTY DFM_density_mark3 OVERLAP MULTI COUNT>=3 ?1:0 ==1) — assignment_op `+=`, condition COUNT, operator `>=`, trailing INSIDE — distinct from both A and B for anti-hardcode.

26 conditions (a-z minus... actually a through z = 26): structure 2 + B run 1 + B schema 1 + B stmt1 6 (target/op/layer1/layer2/cmp/trailing) + B stmt2 8 (target/op/input/property/overlap/assign/cond/true_false_filter) + B cross_ref 1 + B anti-hardcode layers 1 + B2 run 1 + B2 anti-hardcode 3 (layer1/trailing/overlap+assign+cond) + determinism 1.
