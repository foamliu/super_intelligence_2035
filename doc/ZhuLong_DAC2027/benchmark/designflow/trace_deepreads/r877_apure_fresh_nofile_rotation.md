# deepread: r877 — A-pure fresh candidates rotation-evaporated (11-20 snapshot reconfirm)

- **round**: r877 (2026-11-21, 0-case governance)
- **scan source**: `summary_stats.json.scan_path` = `ssh_eda_search_20261120_145529/summary.tsv` (11-20 14:55, 5457 dedup)
- **touched-sids source**: `all_touched_sids_r875_v2.txt` (4066 4-shard union, mixed long/short form: 3900 long + 166 short)

## What was checked

Local A-pure candidate pool `_a_pure_cands_r875_full.tsv` (200 entries, A-domain keyword dominant, mc≥30) cross-checked against touched-sids → **16 truly fresh** after fixing the long/short sid-form lookup bug (initial filter wrongly reported 180 fresh because short-form sids were not matched against long-form touched entries).

## ALIVE check (13 of 16 fresh, top by mc)

Cross-host `test -f` on each candidate's primary host + secondary hosts:

| mc | sid | user | host | status |
|---|---|---|---|---|
| 268 | 1795142758542_ggoyv | e0014036 | hfeg0plg103 | NOFILE |
| 225 | 1794808558058_g18s9 | sfeng | hfeg0pkn005 | NOFILE |
| 219 | 1795056127241_edc1w | johnl | hfeg0pfn120 | NOFILE |
| 214 | 1794986612091_pm8zt | chuanqiz | hfeg0pnd001 | NOFILE |
| 206 | 1794905326109_smsiw | chuanqiz | hfeg0pnd001 | NOFILE |
| 194 | 1794832618722_nqtif | chuanqiz | hfeg0pnd001 | NOFILE |
| 191 | 1794905310620_zo3k4 | chuanqiz | hfeg0pnd001 | NOFILE |
| 184 | 1794905317697_2n2tp | chuanqiz | hfeg0pnd001 | NOFILE |
| 181 | 1795077186517_plk7n | lein | hfeg0pgn145 | NOFILE |
| 167 | 1794971015849_bxlhe | rose3wang | hfeg0plg56 | NOFILE |
| 165 | 1794989160663_uhnxn | rose3wang | hfeg0plg56 | NOFILE |
| 164 | 1794983590823_7ykhf | rose3wang | hfeg0plg56 | NOFILE |
| 164 | 1794967327345_t5h98 | krisluo | hfeahpc502 | NOFILE |

**13/13 NOFILE across 7 distinct hosts** (plg103/pkn005/pfn120/pnd001/pgn145/plg56/eahpc502).

## Key evidence: g18s9 post-r875 rotation

`g18s9` was synthesized into a case at **r875** (EDA-Eval-DesignFlow-CompressBasicRunbookQA-001, sfeng@hfeg0pkn005) — its `messages.json` was scp'd successfully at r875. It is now NOFILE on pkn005. This **times the rotation to after r875** (r875 ≈ 2026-11-20 ~23:00, r877 = 2026-11-21). The 11-20 snapshot's A-pure fresh pool has been wholesale rotation-evaporated in the ~hours since.

## Conclusion

This is the **same r528 pattern** (95 fresh → all NOFILE) reconfirmed on the 11-20 snapshot, not a filtering artifact:
- The A-pure strict-filter pool's fresh high-mc candidates are **gone from disk**.
- This is **not** the "A-pure exhausted" filtering假象 of r867/r831 (those were about keyword-filter dropping real intent). Here the files physically do not exist — no deepread possible, no synthesis possible.
- Per 11-15 order stop-loss criterion ("viable candidates that faithfully restore user intent + writable check()"): **NO** for the 11-20 snapshot — the candidate files are unavailable.

## Path forward (not executed this round — out of time budget)

1. **New full `ssh_eda_search` scan** (per 11-14 ops order, A is authorized ≤1/day). The 11-20 snapshot is stale w.r.t. on-disk state; a fresh scan captures currently-ALIVE sessions. Daily cap: last scan 11-20 14:55 → 11-21 scan permitted.
2. After fresh scan → refresh `summary_stats.json` → recompute A-pure fresh pool → ALIVE-check before deepread (avoid repeating r528/r877 NOFILE waste).
3. The 13 NOFILE sids parked in ledger A (parked 286→299) so future rounds skip them.

## Discipline notes

- No case produced (0-case round). Budget consumed by NOFILE discovery across 13 candidates/7 hosts.
- Did NOT touch the staged `SramMarkLayerDiag-001` files in EDA-Flow-Bench (physical_verify = shard C domain; in-flight, not mine).
- SYNC BLOCKER on super_intelligence_2035 persists (origin/main path corruption, ops not yet fixed) → MEMORY/ledger commits local-only, push deferred.
