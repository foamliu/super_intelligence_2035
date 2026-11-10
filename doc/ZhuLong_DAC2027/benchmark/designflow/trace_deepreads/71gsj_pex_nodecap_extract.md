# Deepread — 1794212194682_71gsj (renfengc@hfeg0plg53)

- trace_source: host=hfeg0plg53, user=renfengc, session_file=1794212194682_71gsj.messages.json
- domain: analog_context (+ schematic_netlist)
- mc profile: opamp:335 pex:99 netlist:16 aether:8 pyaether:6 calibre:6 synopsys:4 cadence:4
- nmsgs: 84

## Real task summary
User asks (Chinese): "linux如何读取后仿网表中特定节点的寄生电容" then pins a real PEX netlist
`/proj/dscqa/V0/ver/pex/renfengc/IO_CAPad/IO_CAPad.spf_RCC` and asks for the total parasitic
capacitance of node `opamp_outn` inside subckt instance `XI_IO_CABufCore`.

## What the agent produced
- Inspected the StarRC DSPF (.spf_RCC) header: `*|DSPF 1.3`, `*|DIVIDER .`, `*|DELIMITER :`,
  `*|GROUND_NET 0`, `.SUBCKT IO_CAPad ... vcc! vdd2ca! vss!`, `*|NET <name> <total>PF`.
- Cap line forms: `Cg1_<i> <node> 0 <value_F>` (grounded), `C928_<i> <node1>:<seg> <node2>:<seg> <value_F>`
  (coupling/distributed), values in Farads (e.g. 2.79647e-18).
- Wrote `/home/renfengc/parse_cap_v2.py` — parses DSPF, sums grounded (to 0/vss!/vdd) + coupling
  (to other nets), skips internal same-net segment caps, reads `*|NET` declared total.
- Key parsing subtleties:
  1. node names carry `:segment` suffix (opamp_outn:293) → must strip suffix to match base net.
  2. must NOT count R (resistance) lines (last field also a float) — only `C`-prefixed lines.
  3. grounded vs coupling decided by whether the partner node is a ground net (0/vss!/vdd) or
     a different signal net; same-base net (different segments) = internal → skip.
  4. `*|NET` declared total is in pF (e.g. `0.00706248PF`).
- Final answer: node `XI_IO_CABuf.XI_IO_CABufDiff.XI_IO_CABufcore.opamp_outn`
  grounded 2.76 fF + coupling 3.92 fF = 6.67 fF computed; `*|NET` declared 7.06 fF.

## B-grade synthesis plan (disjoint names)
- Synthesize a small StarRC DSPF `.spf` for a fictitious design `AmpBiasPad` with a target
  hierarchical node `XI_AmpTop.XI_DiffStg.amp_outp` (disjoint from opamp_outn / IO_CAPad).
- Include: grounded caps (to 0 and to vss!), coupling caps (to other nets incl. a name-sharing
  but distinct net `amp_outn`), an internal same-net segment cap (must skip), an R-line decoy
  (must skip), and decoy caps on other nets.
- Visible A: `AmpBiasPad_pex.spf` + `task.md` (SUT develops script, writes report.json on A).
- Hidden B: `graded_pex.spf` (different node names + cap values) + `expected.json`.
  check.py runs SUT's `extract_node_cap.py` on B and on 3 seeded variants (anti-hardcode).
- Deliverable: `outputs/submit.zip` with `extract_node_cap.py` + `report.json`.
- Script interface: `python3 extract_node_cap.py <spf> <node>` prints JSON to stdout with
  grounded_cap_f / coupling_cap_f / total_cap_f / declared_cap_f / declared_cap_pf.

## check.py conditions (k=10)
1. extract_node_cap.py present
2. report.json present & parses (A)
3. report.json node == A target
4. report.json grounded ≈ A_grounded (±1%)
5. report.json total ≈ A_total (±1%)
6. script runnable on A; stdout total ≈ A_total
7. script on B: grounded ≈ B_grounded (±1%)
8. script on B: coupling ≈ B_coupling (±1%)
9. script on B: total ≈ B_total (±1%)
10. script on B: declared ≈ B_declared (±1%) [reads *|NET]
11. 3-seed variants of B: totals match recomputed reference (anti-hardcode + R-line skip)
