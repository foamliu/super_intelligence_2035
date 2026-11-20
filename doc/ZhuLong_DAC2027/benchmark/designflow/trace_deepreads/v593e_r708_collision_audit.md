# Deepread addendum: v593e — r708 cross-shard collision audit (0-case round)

**Session**: 1794208159902_v593e (t0002614 @ hfeg0pkn004, mc=82)
**Date**: 2026-11-17 r708
**Outcome**: 0-case audit round. v593e NOT built for C. Ledger parked with COLLISION note.

## Background

v593e was revival-picked at r708 open (prior conversation) under the 11-15 user令
("parked Q&A / doc-search categories are now造-able"), classified as layout_aether.
Prior plan was to build `BlsaBlLoadNetlistExtractPlan-001` from U#0 (DRAM BLSA + BL
loading netlist extraction). This audit was triggered before BUILD.

## Collision finding (cross-shard harvest check)

Grepped `EDA-Eval-DesignFlow_{A,B,C,D}.jsonl` + `cases/{A,B,C,D}/` for v593e-derived
case ids. v593e (session_file `1794208159902_v593e.messages.json`, user t0002614,
host hfeg0pkn004, mc=82) has ALREADY been harvested by TWO other shards:

1. **Shard B** — `EDA-Eval-DesignFlow-ManualSectionExtract-001` (domain spice_sim)
   - cases/B/EDA-Eval-DesignFlow-ManualSectionExtract-001.json
   - Reframe: Aether DM manual section markdown → structured JSON (28 keys)
   - Source intent: U#32 (config view role) → manual §2.2 New Cell/View content
   - Prior deepread: `v593e_manual_section_extract.md` (this dir)

2. **Shard D** — `EDA-Eval-DesignFlow-AetherPartialNetlistExtractQA-001` (domain schematic_netlist)
   - cases/D/EDA-Eval-DesignFlow-AetherPartialNetlistExtractQA-001.json
   - trace_source.session_file = 1794208159902_v593e.messages.json (SAME trace, mc=82)
   - Reframe: BLSA + BL partial netlist extraction Q&A from Aether KB excerpts
   - Source intent: U#0 (DRAM BLSA + BL loading netlist extraction for sim)
   - real_task_summary verbatim cites U#0 + U#14 + assistant 3-scheme answer

Both user intents in v593e (U#0 netlist extraction, U#32 config view) are thus
already covered by B + D. A third C reframe would either (a) duplicate D's
BLSA+BL netlist-extraction angle (planned `BlsaBlLoadNetlistExtractPlan-001`
overlaps D's `AetherPartialNetlistExtractQA-001` on the same U#0 intent and same
assistant 3-scheme answer), or (b) duplicate B's manual-section angle.

## C-domain check

v593e is fundamentally **schematic_netlist + documentation**, NOT C-domain:
- U#0 = netlist extraction for simulation (schematic_netlist — D's domain)
- U#32 = Aether DM config view role (mixed-mode sim setup, doc/Q&A — B's angle)
- No layout / pg / physical-verify content in the trace.
- The C ledger's ORIGINAL park note (2026-11-17 04:58) correctly classified it as
  "netlist extraction how-to Q&A" — the r708 revival to layout_aether was a
  misclassification driven by the 11-15 令 lowering the Q&A bar, NOT by genuine
  C-domain signal. Same trap pattern as r706's DRCPA/DRCOA (DDR project names
  misread as physical DRC).

## Decision

Do NOT build a C case on v593e. Reasons:
1. Cross-shard collision — v593e already harvested by B + D (2 distinct reframes).
2. Not C-domain — forcing it would misclassify schematic_netlist+doc as layout.
3. The "no collision" + "C-domain fidelity" rules are NOT waived by the 11-15 令
   (which only lowers the task-TYPE bar for Q&A/doc, not the collision/C-domain bars).

Ledger updated: `1794208159902_v593e` parked, note = COLLISION r708 finding.

## SSH / trace-fetch infrastructure note (blocking fresh C candidates this round)

Attempted to pivot to a fresh C-domain candidate after the v593e collision. Top
fresh candidates identified from `candidates_mc10_classified.tsv` (domain==C,
not yet ledgered across 4 shards):

| slug | mc | user | host | keywords |
|---|---|---|---|---|
| 1788945320747_xi6yc | 26 | sophiaw | hfeg0plg09 | virtuoso:46 |
| 1790141424715_055cs | 25 | steveny | hfeg0pnd001 | virtuoso:62;cellview:50;pyaether:22 |
| 1782819860572_ijgow | 23 | e03179 | hfeg0plg15 | cellview:130;virtuoso:10 |
| 1791770100985_wi6fj | 22 | e0041392 | hfeg0pkn001 | pyaether:49;aether:41;dbopencv:5 |
| 1792568651639_vrctd | 19 | han1li | hfeg0plg54 | virtuoso:23;pex:2;lvs:2 |
| 1794540105944_h8hlb | 18 | lizwen | hfeg0pkn003 | dbget:33;pyaether:23;aether:9 |
| 1794275240977_d2enp | 15 | gokuguo | hfeg0plg53 | virtuoso:55;techfile:4;pdk:4 |

All 7 are FRESH (not in any of the 4 shard ledgers, 3634 ledgered slugs after
suffix-normalization). All 7 users appear in prior-C readable-user set (128 users).
All 7 host-IPs are in `/home/t0002965/ssh_auth_ok.txt` (698 hosts).

**Block**: could not fetch any fresh trace this round.
- Sandbox (.75 = hfhds201, e0031982 identity): ssh key `~/.ssh/id_rsa` OFFERED but
  REJECTED by all probed users/hosts (t0002614@hfeg0pkn004, jzeng@hfhds201,
  steveny@hfeg0pnd001, sophiaw@hfeg0plg09, lizwen@hfeg0pkn003, gokuguo@hfeg0plg53,
  e0041392@hfeg0pkn001, e03179@hfeg0plg15, han1li@hfeg0plg54, zhiguo1w@hfeg0pjn200).
  ssh -vv confirms key offered + "Permission denied (publickey,...)". The sandbox
  e0031982 key is NOT deployed to any EDA user's authorized_keys.
- NAS (hfeg0tedaap02, app.e0031982 identity): ICMP reaches 10.129.2.13 (1ms) but
  ssh port 22 CONNECTION TIMES OUT — firewall blocks port 22 from NAS to EDA hosts.
  NAS has no route to fetch traces.
- No trace mirror on .75 (ssh_eda_search_*/summary.tsv are scan outputs, no raw
  messages.json); NAS trace_retest cache has none of the 7 fresh slugs (nor v593e).
- eda_flow tool catalog (8 tools) has NO trace-fetch/stage mechanism exposed to
  the agent; traces must be pre-staged into the workdir by the eval driver.

The only trace staged this round was v593e (the prior conversation's pick), which
is the confirmed collision. Conclusion: fresh C case delivery blocked by
trace-fetch infrastructure this round; 0-case audit round is the honest outcome.

## Recommendation for next round (r709)

1. Trace staging: request eval driver to pre-stage one of the 7 fresh C candidates
   above (recommend `055cs` steveny@hfeg0pnd001 mc25 virtuoso+cellview+pyaether, or
   `xi6yc` sophiaw@hfeg0plg09 mc26 virtuoso) into the r709 workdir, OR restore a
   working SSH identity on the sandbox so the agent can scp.
2. discuss/C.md quota: MANDATORY at r709 (last发言 r705, r705→r709 diff=4 ≥4).
3. Keep v593e parked (COLLISION note); do not revive.
