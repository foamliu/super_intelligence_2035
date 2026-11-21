# r924 deepread: 15 fresh mc≥15 C-keyword candidates peeked → 15 REJECT (keyword vs operation-domain mismatch)

**Round**: r924 (2026-11-21 23:27 loop card, 40-min/2700s budget)
**Verdict**: 0-case 流程纠偏轮 (r912 precedent). mc≥5 fresh pool quality-depleted for real C-domain tasks.
**Ledger impact**: 15 candidates parked (parked 796→811). covered=583 unchanged.
**trace 覆盖率**: 583/2072=28.1% (mc≥5, key=mc5, +0 case)

## Selection method
- Local filter `candidates_mc5.tsv` × cross-shard ledger exclusion × 4-shard jsonl `trace_source.session_file` cased-set exclusion (4047 sids)
- C-domain keyword score filter: `c_score = drc + calibre + lvs + aether + virtuoso + pex + dbCreate* >= 80` AND (`dbCreate*>=5 OR dbOpenCellViewByType>=15 OR drc>=50 OR calibre>=30 OR lvs>=20 OR pex>=15`)
- Exclude `junxu` only (r923 confirmed depleted)
- 36 fresh candidates passed filter; peeked 15 top + representative ones

## The 15 peeked candidates (all REJECT)

| sid | user | host | mc | c_score | verdict |
|---|---|---|---|---|---|
| 1791177518604_fywl4 | adminai | 10.129.2.13 | 45 | 300 | REJECT wrong-domain: CI/CD pipeline + Portal DB project_name matching. 395 msgs. |
| 1794451618037_ncasl | steveny | 10.129.32.189 | 44 | 718(layout) | REJECT wrong-domain + collision: workspace.md sync + agents.md path audit. 75 msgs. Overlaps CadToolCliRefactorAudit-001 (same steveny, same test_layout_rscalc_flow_19). |
| 1793278856018_2qqsy | mwxi | 10.129.32.112 | 33 | 160 | REJECT wrong-domain: CXDS-291 AI-driven EDA storage trend report writing. 114 msgs. |
| 1792393900566_jdpmg | e0029495 | 10.129.2.10 | 31 | 222 | REJECT too short: U#1='/anasimpro-gui-start' slash command. 30 msgs, 1 user input. |
| 1788424592759_xmffg | jason17w | 10.129.32.190 | 52 | 718 | REJECT wrong-domain: VPS retry-tasks skill creation. 30 msgs. verification/skill-routing. |
| 1791345143791_zwj1e | adminai | 10.129.2.13 | 22 | 127 | REJECT wrong-domain: Portal storage volume 'unassociated' event P-20261007-01. 120 msgs. |
| 1791855423397_es8nr | thomasz | 10.129.33.184 | 21 | 99 | REJECT too short: 'log 这里面提到的DEF/LEF是啥' Q&A. 15 msgs. |
| 1790054706640_uv0eo | shaoyou | 10.129.2.13 | 26 | 65 | REJECT wrong-domain: 'generate Perl script printing hello world'. 21 msgs. |
| 1783417148043_e9cd7 | e0014566 | 10.129.35.82 | 21 | 544 | REJECT semantic-collision: AutoVia SKILL sandbox debug. C-domain BUT e0014566 has 7+ AutoVia cases (AutoViaAgentGen/DeGui/StrcatTypeFix/PwrFillCellRemove/PFAudit/ConfigReport/Gen/BatchLogMon/LayoutMerge/NameGen/RunnerPrep). 21 msgs. |
| 1791424106945_zp1c8 | kenwang | 172.16.8.192 | 30 | 190 | REJECT wrong-domain: '/home/kenwang/zl files disappeared' env-config. 58 msgs. |
| 1793083231525_hy256 | ellawu | 10.129.2.10 | 28 | 176 | REJECT too short + collision: '整理一下flow' + IMCleFillImplantDrc.py. 7 msgs. Overlaps ImplantFillDeckGen-001. |
| 1790162177197_lmn7f | xinqiaoz | 10.129.2.11 | 53 | 520 | REJECT semantic-collision: DRC deck compile switch + derived layer in DrcInfo/DrcValueCheck. C-domain BUT collides with MVVarNamingAudit-001 (same files) + DeriveLayerFractureTruthConsistency-001 + DrcUnusedVarClassify-001. 30 msgs. |
| 1789717600830_iclsp | xinqiaoz | 10.129.2.11 | 31 | 1033 | REJECT too short: 'PDK_QA issue 0918_zhaowei base env setup'. 9 msgs. env-config. |
| 1790229141278_gxf18 | xinqiaoz | 10.129.2.11 | 49 | 177 | REJECT wrong-domain + collision: globalState.json workspaceRoots migration. 53 msgs. Overlaps ClineWorkdirDiagnose-001. |
| 1788917814838_yd21d | xinqiaoz | 10.129.2.11 | 50 | 307 | REJECT too short: 'do we have global instruction doc' Q&A. 18 msgs. |

## Distribution of REJECT reasons
- **Wrong-domain** (real task is env-config/doc-search/CI-CD/Portal/verification not C-layout/physical_verify): 9/15 (60%)
  - adminai fywl4+zwj1e = Portal DB / CI-CD pipeline
  - mwxi qqsy = project report writing
  - jason17w xmffg = VPS retry skill (verification)
  - kenwang zp1c8 = files-disappeared env-config
  - xinqiaoz gxf18 = globalState.json workspaceRoots migration
  - steveny ncasl = workspace.md sync (doc-maintenance)
  - shaoyou uv0eo = Perl hello world
- **Too short** (<20 msgs, single-turn Q&A, no proper case material): 4/15 (27%)
  - jdpmg 30 msgs/1 user input, es8nr 15 msgs, hy256 7 msgs, iclsp 9 msgs, yd21d 18 msgs
- **C-domain but semantic-collision** with existing case: 2/15 (13%)
  - e9cd7 (AutoVia sandbox debug) collides with 7+ AutoVia cases
  - lmn7f (DRC compile switch + derived layer) collides with MVVarNamingAudit + DeriveLayerFractureTruthConsistency + DrcUnusedVarClassify

## Root cause: keyword-based candidate filter has <15% hit rate

The C-keyword score in summary.tsv counts ALL text occurrences in session file scan, including:
- editor file reads (the user reads C-domain files for context but task is something else)
- tool_result content (long file dumps inflate keyword counts)
- incidental mentions in conversation

This means **keyword-dominant != operation-domain**. r923 lesson "trace 域归属要按操作域而非 keyword 域" applies BROADLY: not just junxu pool, but the entire mc≥5 fresh C-keyword pool. **The mc≥5扩池实测无效 verdict for shard C is now confirmed with 15-candidate sample (0/15 viable).**

## Lessons

(a) **Keyword filter is necessary but not sufficient** — must deepread first 5 user inputs + first 3 editor targets BEFORE claim, not after. r923 lesson was correct but underestimated scope: applies to ALL fresh candidates, not just junxu.

(b) **mc>=5扩池 was effective for pool QUANTITY (36 fresh passed filter) but NOT for pool QUALITY (0/15 viable)**. This matches the r382 threshold_eval_shardA finding "fresh=289 at mc≥10 is quality-exhausted, not quantity-exhausted" — same pattern now observed in shard C at mc≥5.

(c) **Over-covered users (xinqiaoz 56/e0014566 86/ellawu 25/steveny 10) have FRESH sessions but they cluster on ALREADY-CASED TOPICS** — xinqiaoz fresh sessions are mostly pdkQaSystem maintenance variants; e0014566 fresh sessions are mostly AutoVia/PowerFill variants; ellawu fresh sessions are mostly Calibre TVF/dummy-fill variants. Domain archetype saturation reached.

(d) **r912 precedent applies**: 0-case flow-correction round legitimate when (1) ≥10 fresh candidates actually peeked with first-5-user-input + tools check, (2) all REJECT with documented reasons, (3) ledger parked to avoid re-peek. Quality gate (k≥8 + no-collision) > 1-case count.

## Next-round recommendation

- **Pivot to revival pool**: r907 `pool_reaudit_C.tsv` 374 revival candidates (11-15 令 parked-without-deepread) — these were parked before r923 deepread methodology was enforced, may contain viable C-domain cases that were mis-parked under old weak-case/Q&A rules (now legal per 11-15 令)
- **OR pivot to archetype expansion**: build C-domain cases from non-pool sources (e.g. ask eda_flow to run a real Virtuoso/Aether flow and capture the trace as a synthetic case)
- **OR accept saturation**: shard C holds at 583 covered / 2072 target (28.1%), redirect capacity to A/B/D shards where fresh pool may be less quality-depleted
- **DO NOT** continue random peek of remaining 21 fresh candidates — same keyword-vs-operation-domain mismatch expected (>85% REJECT rate projected)
