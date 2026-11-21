# r985 triage — shard B, 0-case (dedup walls + sim-checkability barriers)

**Date**: 2026-11-22 00:5x (shard B, r985)
**Snapshot**: real scan `ssh_eda_search_20261121_151844/summary.tsv` (correct ip+host, 610 deduped-by-sid B-domain cands after spice≥10/mc≥5/not-non-B/not-layout/pex-lvs/a-dom filters) cross-checked vs 4-shard touched (4221 sids, suffix-normalized) → fresh pool.
**Coverage**: mc≥5 pool=2174 touched=1853 fresh=321 / mc≥10 pool=2072 touched=1815 fresh=257.
**Outcome**: 0 case. NOT pool exhaustion (fresh=321/257). 7 fresh B-pure candidates peeked via .75 (eda_flow open_session + read messages.json); 3 parked as near-dup, 2 deferred as sim-checkability-blocked L2/L3, 2 thin. Quality gate, not external block.

## Peek method (reusable)
- `eda_flow.open_session(task_id,eval_id,user)` works without eval-driver creds (contra r975 note) → workdir on .75.
- Session files live at `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json` (subdir, NOT flat) — r984/r973 used flat path; fix.
- zjqiao/joeyl/willz/jeoteanl/e0039786 home dirs are NFS-synced across hosts; reading from .75 `/home/<user>` works for live sessions; cleaned sessions need `.snapshot/hourly-new.*` recovery (r984 pattern).
- Real ip+host come from the LIVE `summary.tsv` on .75 (`/home/t0002965/log/...`), NOT `summary_1120_reconstructed.tsv` (which has ip=0.0.0.0 + wrong host). Always grep the live summary for correct SSH targets.

## 7 peeked candidates

| sid | user@host | mc | kw profile | U0 intent | verdict |
|---|---|---|---|---|---|
| 1795154624230_10atu | jeoteanl@hfeg0pkn005 | 81 | hspice:138;netlist:270 | copy mt0_parser.py + templates, then **debug step1 IDDQ 75-case fail** (`ERROR! no reference ckt nrvt_ckt/prvt_ckt`) | **PARKED near-dup** — core "no reference ckt" diagnostic already covered by **FineSimNoRefCktFix-001** (rongtaoy, missing-subckt+fix) AND **SimErrSubcktRefDiag-001** (ericw, naming-inconsistency vs true-missing). 10atu's extra twist (`.lib entry <section> not found` 2nd form + stale-process DEFAULT_LIB) insufficient to differentiate the core no-ref-ckt diagnostic shape. Also MissingRefDiagnose-001 (t0002607/r974) built but unshipped. 3rd no-ref-ckt case = over-coverage. |
| 1794810067969_jsutr | willz@hfeahpc501 | 60 | hspice:101;netlist:205 | "copy duty/sensitivity/RJ .sp from sim_result_251202 to sim_result_261112" | **PARKED near-dup** — identical sim_result_251202→261112 paths + same sessionId `1794475206189_lbrbv` in agent-policy as r983 **SpDeckModelStripMigrate-001** (willz FineSim deck 4-pass migrate). Sibling/continuation of the cased task. |
| 1794889513594_yd89p | joeyl@hfeg0pkn004 | 196 | netlist:711;hspice:370;pdk:354 | 2_TRAN.sp CML前三级 vdb tuning (identical U0 wording to fresh 11voz) | **already in shard D ledger** (status=deepread, 2026-11-19) — claim REFUSED cross-shard. Near-dup of fresh 11voz anyway. |
| 1794893672653_11voz | joeyl@hfeg0pkn004 | 116 | netlist:272;hspice:243;pdk:223;opamp:69 | 2_TRAN.sp CML前三级 tune for vdb(outn,outp)>1 @8.8G, 5 corners, keep sat | **DEFERRED (left fresh)** — genuine PRODUCE analog-sizing task, NOT near-dup of CmlDivOscDiag-001 (divider osc debug) or CmlSweepHeadroomDiag-001 (sweep-current diagnostic). BUT checkability needs real AC/tran sim to verify vdb>1 + saturation; equation-only check is weak. L2/L3 sim-backed case — re-evaluate when a round has budget to build FineSim/HSPICE-on-.75 reference + hidden-B sim verification (≥8 assertions). joeyl over-used (5 prior cases) — concentration risk. |
| 1794900549189_dibsj | joeyl@hfeg0pkn004 | 186 | synopsys:518;netlist:462;hspice:271;pdk:224 | 1_AC.sp tune stage-2 active inductor (R len, MOS W/L/finger) for max BW @5corner, output BW-3dB + AC/DC gain | **DEFERRED (left fresh)** — CML BW-tuning PRODUCE, distinct from 11voz (AC/BW vs tran/vdb) and existing CML cases. Same sim-checkability barrier as 11voz. joeyl concentration risk. |
| 1795073056270_n488u | willz@hfeahpc501 | 63 | hspice:77;netlist:299 | multi-turn FineSim deck edits (strip dup temp rows, rewrite .inc netlist/spf paths, append PVT model corners, gen ffm1/ffm2 by copy, change vdd2c source) | **skip** — deck-edit sequence overlaps r983 SpDeckModelStripMigrate form; willz over-used (r964/r983). Some turns (U2 psub job status, U7 bkill) are thin/interactive. |
| 1794815686198_4w3lo | e0039786@hfeg0pkn005 | 58 | hspice:74;netlist:90 | "动态功耗扫描" + "我的cell在Virtuoso里" + Ring_OSC layout path | **skip** — 49 msgs, layout+pyaether dynamic-power-scan, needs Virtuoso/EDA binary, thin & not self-contained. |

## Other fresh candidates noted (not peeked, lower priority)
- `1794900549189_dibsj`-class joeyl CML cluster (yd89p/11voz/dibsj all 4_WCKTOP/*_TRAN.sp/1_AC.sp CML tasks) — 3 fresh siblings, all sim-backed L2/L3.
- `1794970973210_fve2x` irene1li (mc=113, hspice:302;waveview:90) — "看采样margin" D-latch setup/hold of 24to1 mux — analysis task, sim-backed, new user. Deferred.
- `1794815222258_pofwk` reedchen (mc=127) — schematic:494 dominant, hspice:15 thin → likely C/D-domain, skip.
- `1795080052098_faqqt` zjqiao (mc=105, netlist:687;analog:329;hspice:88) — live session cleaned, needs .snapshot recovery; zjqiao new user. Not peeked (recovery cost).

## Conclusion
B shard is **mature** (499 cases / 665 ledger, 20+ diagnostic cases covering most FineSim error forms). Fresh pool (321/257) is real but skews to: (a) joeyl/willz over-concentration, (b) sim-backed L2/L3 analog tasks (CML tuning, setup/hold margin) that need real-sim verification I couldn't build in the 40-min budget, (c) near-dups of the heavily-covered "no reference ckt" / deck-edit diagnostic families. 0-case = quality gate (no weak/dup case forced), NOT pool exhaustion. Next round: either (1) commit to a sim-backed L2 case (11voz/dibsj/fve2x) with full FineSim-on-.75 reference+hidden-B verification, or (2) recover zjqiao faqqt from .snapshot for a new-user candidate.
