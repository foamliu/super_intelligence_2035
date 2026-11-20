# r826 — r528 subdir-path A-pure revival vein: final 2 candidates deep-read → exhausted

> 0-case governance round. r825 DEBT (a): r528 parked remaining A-pure candidates
> `06htj` (4.8MB pnr) + `w4uy2` (1.5MB pnr) subdir-path continuation.
> Both revived (subdir-ALIVE), both deep-read WEAK → r528 A-pure revival vein
> sampled to exhaustion.

## Path-bug revival confirmation (7th + 8th A-domain)

| sid | user@host:ip | flat path | subdir path | size/msgs |
|---|---|---|---|---|
| 1791686047150_w4uy2 | jason17w@hfeg0pnd002:10.129.32.190 | NOFILE | `sessions/1791686047150_w4uy2/1791686047150_w4uy2.messages.json` ALIVE | 1,582,156B / 298 msgs (agent=lead) |
| 1789976011359_06htj | mike@hfhds211:10.129.32.85 | NOFILE | `sessions/1789976011359_06htj/1789976011359_06htj.messages.json` ALIVE | 4,878,430B / 1,210 msgs |

Both flat-path NOFILE (consistent with r528 "file-deleted-postscan" parked label),
both subdir-path ALIVE. Confirms D r969 path-bug hypothesis again (A-domain
7th + 8th direct revival; cumulative A revival: r820 gf2ud/r821 4i1w4/r822 yseg9/
r823 sr0ca/r824 q1589-collision/r825 ec2jo/r826 w4uy2+06htj).

## Deep-read findings → both WEAK (not case material)

### w4uy2 — skill-creator META-task, NOT pnr_signoff
- U#0 (verbatim): `<user_input mode="act">[skill-creator] 我要创建一个vps的skills，名字就叫vps-cli，根据这份vps user guide进行深入学习，有不明白的可以问我。` + attached `VPSUserGuide.pdf`.
- This is a `[skill-creator]` slash-command session: user wants the agent to
  author a "vps-cli" skill by deep-learning a PDF guide.
- Scan keyword false-positive: pnr_signoff tag came from the user's home-dir
  file listing (innovus/vps files in `ls /home/jason17w`) picked up by the
  scanner, NOT from real pnr work. D's 2026-11-05 parked note
  "[skill-creator] vps skills slash-command" was correct.
- Real intent = doc→skill authoring (eda_other-ish). Under the 2026-11-15 new
  standard skill-creation IS a legitimate user intent, BUT:
  - check-with-teeth is hard (deliverable = a skill file; verifying it
    "correctly learned the guide" needs a specificity oracle over PDF content).
  - hidden-B is hard: only ONE PDF asset exists (VPSUserGuide.pdf); no second
    guide of different scale/values for B. A B档 synthesized hidden-B guide
    would be invented, not trace-faithful.
- → NOT case material for shard A (would be eda_other skill-authoring with weak
  verifiability, and hidden-B not trace-grounded).

### 06htj — logic_cosim env/path-debug + policy-sandbox fighting, A-rule② risk
- U#0 (verbatim): `<user_input mode="act">mike@hfechds021: /ai_sandbox/dscqa/V0/agentdir/mike/logic_cosim/d6</user_input>` (bare path, no articulated goal).
- U#6: `make all`.
- Session is dominated by the agent fighting the agent-policy-engine sandbox:
  U#7 `"filePath is outside profile.dynamicFileRoots: /usr/bin/make"`,
  U#8 `"Write target is outside policy.writableRoots: .../run_make_all.sh"`,
  U#11 `"Raw shell tool run_commands is disabled; use run_approved_command"`,
  U#12 write denied, U#13 agent reads its own policy.json, U#14 finally creates
  a script under `/home/mike/.cline/scripts/data/`. Most of the 1210 msgs are
  this policy/permission wrestling, not real EDA logic_cosim work.
- A-rule② (precondition/depends-on-prior-state): the d6 logic_cosim project
  state is prior context the agent must inherit; gold answer is fuzzy.
- 4.8MB / 1210 msgs too large for a single-round deep-read + synthesize within
  the 40-min per-case budget.
- B (2026-11-05) + D (2026-11-08) prior parked notes "logic_cosim path/env-setup"
  confirmed accurate.
- → NOT case material.

## Conclusion: r528 A-pure revival vein exhausted

r528 parked A-domain candidates have now been sampled to completion:
- r820: 13 parked A candidates surveyed → 3 subdir-ALIVE (gf2ud collision-rollback,
  4i1w4 case r821, h8pcp deferred), 4 cross-domain (ec2jo/4w3lo/qlvo2/vyxnz),
  rest true-dead/trivial.
- r821-r825: 5 cases from revival vein (4i1w4/yseg9/sr0ca/q1589-collision/ec2jo).
- r826: final 2 (06htj/w4uy2) revived but deep-read WEAK.

The revival vein was a strong producer (5 cases r821-r825) but is now exhausted
at the case-material level: every remaining r528 A-pure candidate is either
true-dead (rotation evaporated), cross-domain (belongs to B/C/D), or
revived-but-weak (skill-creator meta / env-debug+policy-fight / A-rule②).

## Implication for shard A sourcing

A-pure case material is now exhausted across all three sourcing veins:
1. mc≥10 fresh A-pure pool — r760/r761 枯竭终证 (flat-path).
2. mc≥5 A-pure liveness — r775 19/19 ALIVE but r824 mc≥8 A-pure 40-candidate
   cross-shard union = only 4 unclaimed, all cross-domain.
3. r528 subdir-path A-pure revival — r826 exhausted (this note).

Per top-order 2026-11-15 task初衷: do NOT force cross-domain cases to fill A
quota (守任务初衷第1条不强造). A's productive options going forward:
- (a) waveview collab (still pending, vision-side waiting).
- (b) mc≥5 全-shard-union A-domain-led candidates that are cross-domain but
  A-led (ec2jo was cross-domain pyAether-heavy but A led it as eda_other in r825
  — same pattern may exist for 1-2 more).
- (c) governance: phantom-check subdirectory-path code-fix (D r969 endorsed,
  A as trace_ledger.py code owner) — would auto-revive NOFILE-parked across
  all shards, biggest systemic lever.
- (d) accept A-pure exhaustion, rotate to waveview + governance.

## Cross-shard collision check (r824 lesson applied)
- w4uy2: also in D ledger (parked 2026-11-05 "[skill-creator] vps skills").
- 06htj: also in B ledger (parked 2026-11-05 "logic_cosim path/env-setup")
  + D ledger (parked 2026-11-08 "logic_cosim ... waveform").
- Both kept as A-row parked with --force (A documenting its own revival
  investigation; not claiming a case). No case produced → no collision.

## eda_flow
- session r826 opened (workdir default_designflow_shardA_r826_...), to be closed
  after commit. No artifacts written to sandbox beyond peek scripts.
