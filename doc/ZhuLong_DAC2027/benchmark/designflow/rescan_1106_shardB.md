# Shard B rescan 2026-11-06 — trace source refresh (operator order 2026-11-05 19:2x)

## Verdict: "shard B spice_char real trace 池枯竭" conclusion VOID. 54 fresh spice candidates available.

## ① New snapshot
- Path: `.75:/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv`
- Lines: **5823** (header + 5822 rows); columns `ip host user session_file match_count keywords tools` (same as old).
- Generated: 2026-11-05 19:28–19:30 (in direct response to the 19:2x order).
- Scan method: parallel ssh probe of 698 hosts from .75 (daily_eda_scan.sh / probe_remote.sh, xargs -P20 -n1, 300s/host). stderr.log only host-key warnings + 1 unreachable (10.129.32.209 No route to host).
- Companion files: `spice_candidates.tsv` (141 spice-filtered), `spice_candidates_NEW.tsv` (108 new vs 10-28 snapshot), `raw.tsv`.

## ② Old vs new diff
- Old snapshot: `/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv` — 24085 rows, **3899 unique session_files**.
- New snapshot: `ssh_eda_search_20261105_192825/summary.tsv` — 5823 rows, **3896 unique session_files** (fewer rows = daily cron keeps only EDA-runtime-trace-worthy sessions since 10-29; the 11-05 rescan is a full re-probe).
- Daily cron `eda_trace_YYYYMMDD.log` running since 10-29 (qualifying sessions/day): 10-29:14370, 10-30:2641, 10-31:13994, 11-01:14047, 11-02:13890, 11-03:14448, 11-04:2724, 11-05:2958, 11-06:2895 → **new traces continuously written across 698 machines**.
- spice_candidates_NEW.tsv: **108 new spice candidates** (filter: spice_count≥10 AND spice_ratio = spice_count/tool_total ≥ 0.35) NOT present in the 10-28 spice_candidates set.
- Session ts range (ms epoch): oldest 1788412903933, newest 1793868970979 → all within 2026-10 (≥ 2026-10-28 window ✓), many from 11-01..11-04.

## ③ Candidate rebuild (spice-dominant filter) + ledger diff
- 108 new spice candidates → 85 unique base-ids (dedup .messages.json/.archive.json/.json variants).
- Cross-check vs `trace_ledger_B.tsv` (178 sessions: 98 case, 1 claimed, 79 parked) by base-id:
  - `comm -23 new_bases ledger_bases` → **54 fresh NEW spice candidates NOT yet in ledger** (available for case-making).
- 31 of the 108 already in ledger (covered/parked) — confirms ledger is tracking the spice pool.
- Scanned hosts: 698 / 2 reachable candidates verified on .75 + via ssh to workstation IPs.

## Fresh candidate list (54, top by spice_count) — user·host·session_file·match_count
(NEW = in 11-05 spice_candidates_NEW.tsv, not in trace_ledger_B)
- e0029308 · hfeg0pkn001 · 1793600858808_la00c · mc=339 (spice=1053,r=0.877, hspice+netlist)
- wnyu · hfeg0pkn004 · 1792119838262_chbpp · mc=629 (spice=1615,r=0.736, hspice+netlist+schematic) ← CLAIMED this round (deepread done)
- qiang3xu · hfeg0pkn005 · 1793792759786_ujw1y · mc=133 (spice=1089,r=0.373)
- wnyu · hfeg0pkn004 · 1792133910648_645nk · mc=1 (spice=1031,r=0.367)
- tongni · hfeg0pkn001 · 1793345773037_65daa · mc=299 (spice=1287,r=0.496)
- tongni · hfeg0pkn001 · 1793257968522_mp3us · mc=164 (spice=1213,r=0.752)
- e0030760 · hfeg0pkn004 · 1793184645122_t1epq · mc=48 (spice=702,r=0.905)
- tongni · hfeg0pkn001 · 1793326532932_fxfox · mc=209 (spice=496,r=0.433)
- shanliny · hfeg0pkn001 · 1793757463114_zd8iu · mc=54 (spice=460,r=1.000, pure hspice)
- tongni · hfeg0pkn001 · 1793243641918_xcuds · mc=92 (spice=413,r=0.466)
- chapinc · hfeg0pkn002 · 1793270732926_ebmf3 · mc=97 (spice=339,r=0.902)
- lvyy · hfeg0pkn004 · 1793856196029_7at4j · mc=69 (spice=341,r=0.713)
- e0024852 · hfeg0pkn002 · 1793777902964_ah9my · mc=213 (spice=305,r=0.862)
- adaml · hfeg0pkn002 · 1793598804317_2swgt · mc=37 (spice=228,r=0.848)
- ronghu · hfeg0pkn005 · 1793692406403_lcg3v · mc=27 (spice=159,r=0.668)
- (39 more lower-spice fresh candidates in fresh_new.txt on .75 workdir)

## Access note (operational)
- Session files on workstations are in **nested dirs**: `/home/<user>/.cline/data/sessions/<base>/<base>.messages.json` (NOT flat `<base>.messages.json`); the summary.tsv records basename only — path reconstruction must add the `<base>/` dir.
- Active users (e.g. tongni) DELETE old sessions → some 11-05-scan hits gone by 11-06 (p7jfx parked: file deleted). Verify file exists before claim.
- .75 (hfhds201) only mounts its own local users' homes + a few NFS homes; most workstation users' /home require ssh to the workstation IP. e0031982 has passwordless ssh to 697/698 hosts.
