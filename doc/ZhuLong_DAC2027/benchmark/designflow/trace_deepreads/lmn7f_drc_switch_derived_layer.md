# Deepread — 1790162177197_lmn7f (DRC deck compile-switch derived-layer check)

- **session**: 1790162177197_lmn7f
- **user/host**: xinqiaoz @ hfeg0plg56
- **mc**: 53 (physical_verify: drc:518;pdk:190;assembler:9;calibre:2)
- **scanned**: 2026-11-26 r1222, mc 5-100 fresh pool (319 fresh / 1787 dedup)

## User intent (real task)

xinqiaoz maintains a PDK-QA system (`/home/xinqiaoz/PDK_QA/pdkQaSystem/`) that
validates DRC rule decks for a foundry PDK. The session resumes from a handoff
(`HANDOFF_phase5_b2_ready.md`) — phase 5 batch B2 of a `sync_to_stable` release
pipeline (snapshots of DrcValueCheck.py + DrcInfo.py, letter.txt, manifest.yaml,
baseline md5s).

After verifying the B2 batch state (git HEAD `64684bb`, 7 snapshots, terminal
state 5/5, B2-B4 sandbox PASS), the user raises a **reviewer (领导) feedback**:

> 「我们的 deck 文件，实际上是有类似 C++ 的编译开关的。我们的 DrcInfo 解析
> 也会区分有开关和无开关。DrcValueCheck 使用的忽略开关，在这种情况下，
> derived layer 可能在不同开关下有不同的定义。所以这里是有问题的，
> derived layer 的检查应当使用开关。」

i.e. DRC decks carry C++-style compile switches (`#ifdef`/`#ifndef`/`#else`/
`#endif`); `DrcInfo` parses in with-switch and ignore-switch modes;
`DrcValueCheck` used ignore-switch, but a **derived layer** can have different
definitions under different switch states — so the ignore-switch check silently
misses inconsistencies. The fix: derived-layer checking must **respect compile
switches**.

## Assistant actions

1. RESUME-mode handoff verification: read handoff doc, git log/status/diff,
   manifest.yaml, sync_state.yaml, B2 letter.txt, snapshots; re-ran
   `generate_snapshots.py --generate` (7 snapshots, py_compile 7/7, B2-B4 PASS,
   B5 FAIL pre-existing env, terminal 5/5, baseline md5 5/5 match).
2. Investigated the switch issue: `search_codebase` for derivedLayer / switch /
   ifdef / DrcInfo / DrcValueCheck; read `DRC/text/DrcValueCheck.py` and
   `common/deckInfo/DrcInfo.py`. Session ends mid-investigation (30 msgs) — the
   actual code fix continues in a later session.

## Case abstraction

Produce-tool (档 B, mock L0/L1): write `drc_switch_check.py` — a CLI that parses
a DRC deck with compile switches, enumerates all 2^N switch states, resolves the
active derived-layer definition per state, and flags derived layers whose
definition differs across states (inconsistent). Pure Python (deck parsing +
switch-state enumeration), no EDA tool runtime → judge_layers=[L0,L1].

### A/B anti-hardcode

- **A** (visible, `deck_A.drc`): switches CHIP_A/CHIP_B; layers m1_active
  (inconsistent: geomAND vs geomOR across CHIP_A), gate_poly (consistent,
  identical both branches), m2_power (consistent, unconditional), merged
  (inconsistent: geomOR vs geomAND across CHIP_B under CHIP_A). total=4,
  inconsistent=[m1_active, merged].
- **B** (hidden, `deck_B.drc`): switches LOWPOWER/PROCESS; layers nwell_act
  (inconsistent), hdr_gate (consistent), vdd_m3 (consistent), stack_dev
  (inconsistent), const_layer (consistent). total=5, inconsistent=[nwell_act,
  stack_dev]. Different switches/names/values from A.

### check.py (14 conditions a–n)

a: ast.parse compiles · b: CLI on B exit 0 + output · c: 5 top-level keys ·
d: switches==[LOWPOWER,PROCESS] · e: num_states==4 · f: nwell_act inconsistent
distinct=2 · g: hdr_gate consistent distinct=1 · h: stack_dev inconsistent
distinct=2 · i: const_layer consistent (unconditional) · j:
inconsistent_layers==[nwell_act,stack_dev] · k: summary 5/3/2 · l: determinism
3-run md5 · m: A!=B antihardcode (A → [m1_active,merged] total=4) · n: no-switch
edge (num_states==1, layer consistent).

### Negatives (4, all FAIL, first-fail labels b/m/f/e distinct; §4.9 trio 3-distinct)

- empty (b) · print-expected (m, hardcodes B answer → fails on A) ·
  core-deleted (f, always consistent=true) · nostates (e, num_states=0).

## Self-verify

- ref drc_switch_check.py: deck_A → inconsistent [m1_active, merged] total 4 ✓;
  deck_B → [nwell_act, stack_dev] total 5 ✓.
- check.py on ref submit.zip: **PASS** (14/14).
- negative_selftest: 4/4 FAIL, labels [b,m,f,e], trio (b,m,f) 3-distinct ✓.
- harness SKIP_RUN=1: case loads, workdir leak CLEAN, attachments copied ✓.
