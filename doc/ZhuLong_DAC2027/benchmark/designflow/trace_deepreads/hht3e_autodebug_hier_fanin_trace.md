# Deepread: 1788241882830_hht3e — wellesc AutoDebug (FSDB hierarchy fallback + fanin trace)

- **trace**: wellesc @ hfeg0plg17, mc=826, 2406 msgs (1233 user / 1173 assistant), 5.9MB
- **continuation**: this session continues 1787659708187_6l1c8 ("读一下这个会话的上下文，帮我继续完成任务")
- **real intent**: build an AutoDebug agent that compares a **reference (passing) FSDB** vs a **failing FSDB** waveform, then traces the gate-level netlist hierarchy backward from a divergent net to the **earliest divergence point** (source gate: inputs all EQUIVALENT, output DIFFERENT). Final deliverable asked = detailed handoff design doc (agent stalled at the very end writing it).

## Core technical challenges (real user pain points)
1. **Equivalent-net hierarchy fallback for FSDB probing** (the key novel insight, U#11/U#12/U#14): the same physical net has many hierarchy paths (`abusbg0_sc0_0<0>` root → `xi_array32gtop.abusbg0_sc0_0<0>` → deeper). FSDB stores only some. When the netlist trace arrives at a hierarchy with NO_DATA, must fall back to an **equivalent hierarchy** (bare-name fallback) that FSDB does store. `xi_array32gtop.abusbg0_sc0_0<0> ✅ → bare-name fallback 复用 abusbg0_sc0_0<0> 的数据`.
2. **Depth-first trace to std_cell leaves** (U#15/U#16): stop drilling at std_cell libs (TECHLIB / stdcells_am / decqa_stdcells); don't descend into leaf libraries.
3. **Source-gate identification**: leaf-most driver whose all upstream (fanin) nets are EQUIVALENT but whose driven output net is DIFFERENT → that net = earliest divergence.
4. **Probe-window no-data ⇒ level constant** (U#26): when a probe window has no transitions, scan back to a changing time window before continuing trace.
5. **Report must name both sim dirs + earliest-divergence net hierarchy** (U#51/U#52).
6. Agent dead-loop reading net hierarchy (U#43) → must not re-probe the same net forever (visited set).

## Project artifacts (editor ops, not on disk at /proj/dbcoa path — reconstructed from trace)
`/proj/dbcoa/V0/workdir/wellesc/AutoDebugWithPassRef_V0/AutoDebug_Project/src/`:
- `netlist_indexer.py` (17 edits, most-touched): `resolve_net_aliases`, `get_fanin` (returns `upstream_nets` as `[{net, pin, pin_dir, probe_alt}]`), `trace_to_leaf` (depth-first to leaf), `is_leaf_cell` (lib in std_cell libs OR no X-instances), `_build_fanin_dag`, `_bare_name`, `EARLIEST_DIVERGENCE_TERMINAL`.
- `waveview_adapter.py` (7 edits): `_bare_name`, `_normalize_sig`, `batch_get_waveforms` (pass-2 bare-name fallback), `_run_waveview` (per-signal sx_signal).
- `agent.py` (7 edits): LLM agent loop, `_parse_conclusion` (fail_net/earliest_divergence/source_gate/root_cause), terminal-nudge on EARLIEST_DIVERGENCE_TERMINAL, duplicate-call guard.
- `comparator_tool.py`, `report_generator.py`, `prompts.py`, `tools.py`, `waveform_tool.py`.
- `rules/skills/{fscript-probe,waveview-probe}/SKILL.md`.
- `handoff_docs/AutoDebug_Design_20260904.md` (final handoff, incomplete — agent stalled).

## Case reframe (LIVE-NA, judge_layers=[L0,L1])
Synthesized-reframe of the **netlist_indexer core** (resolve_net_aliases + trace_to_leaf + find_source_gate) into a spec-JSON-driven pure-graph tracer `hier_fanin_tracer.py(spec)->report.json` + hidden-B anti-hardcode. The FSDB-available set + per-net verdicts are given in the spec (no real WaveView/FSDB binary needed → LIVE-NA). check.py independently recomputes aliases / leaf / source_gate / earliest_divergence (17 conds). A = ChipTop→Array32GTop→Array16G→DQPadM6→invx1 (leaf, source gate: din EQUIVALENT + dout DIFFERENT, bare-name fallback abusbg0_sc0_0<0>). B = PDMCtrl→PDMPreamp→PDMTrimDac→PDMDriver→nr2x1 (leaf, source: vin/vss EQUIVALENT + vout DIFFERENT, bare-name fallback cmp_out) — token-structurally different.

task_id = EDA-Eval-DesignFlow-FsdbHierFaninTrace-001
