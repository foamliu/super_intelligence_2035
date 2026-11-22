# r1039 scout — 1794889513594_j1o1i (junxu @ hfeg0pkn005) → FALSE POSITIVE (parked)

**Round**: r1039 (0-case scout)  **Date**: 2026-11-22  **Verdict**: FALSE POSITIVE, parked

## Trace metadata
- session: `1789721894372_j1o1i.messages.json` (815KB / 233 msgs)
- user/host: junxu @ hfeg0pkn004 (IP 10.129.2.14)
- scan keywords: `hspice:211; netlist:282; waveview:287; virtuoso:619; schematic:112; analog:38`
- mc=235, spice_score=211 (ranked #1 fresh-all after 4-shard ledger cross-diff)

## Why it looked like spice_sim/characterization
High hspice + netlist + waveview keyword counts; junxu is a known characterization user; mc235 solid.

## Why it is a FALSE POSITIVE (deepread)
U0 (first user turn):
> 调用 brainstorming 和 writing-for-agents 这两个 skill / custom_design_skill 是我开发的一套 skills，请你全面检查这一套 skill，指出不完善/可优化的地方

The entire session is junxu **reviewing and optimizing his self-developed `custom_design_skill` skill suite** (sub-skills: `block-design`, `block-sim`, `wv-cli`, `find-python`, `sim-view`). The agent reads SKILL.md files, edits them, reorganizes references, and refines the skill graph. **No spice simulation is run, no circuit is characterized, no netlist is generated for sim.**

The hspice/netlist/waveview keywords are **incidental** — they appear inside the skill SKILL.md / reference documents that *describe* sim flows (the skills are about running sims, so their docs mention hspice/netlist/waveview). The scan's keyword counter picked these up from the skill text loaded into the conversation, not from actual sim commands.

## Decision
`trace_ledger.py --shard B mark --status parked --note "FALSE POSITIVE: junxu custom_design_skill review/optimization ... NOT spice_char"`

## Pool finding (r1039 scout)
- 698 spice candidates (mc≥5, spice≥20) on summary_20261122_172249.tsv → 128 fresh after 4-shard ledger cross-diff
- j1o1i deepread = false positive (this note)
- remaining 127 fresh: all false-positives (skill-dev / layout / DRC-PEX / digital-STA / aether-tooling) or cross-shard dups (shard D/A/C)
- lowered to mc≥3 + spice≥100: 12 more, ALL already in some shard ledger
- **Conclusion**: fresh clean spice_sim/characterization pool EXHAUSTED at current scan snapshot (20261122_172249)
