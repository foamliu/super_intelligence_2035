# BLOCKER.md — DffSetupHoldChar-001 synthesis attempt (2026-11-04, shard B)

## Status: NOT delivered. Calibration blocked. NOT in jsonl (quality gate).
Deepread: `designflow/trace_deepreads/1792386804961_6tiy7_dff_setup_hold_char.md`

## What was built (reusable next round — all in this dir)
- `char_gen_ref.py` — sweep-based DFF setup/hold/tCQ char generator. CLI
  `<dff.sp> <params.json> <out>`. Generates setup-sweep (D-to-CLK lead `tsu_lead`)
  + hold-sweep (D-return-after-CLK `th_lag`) + tCQ testbenches, runs HSPICE
  `.tran` per point, parses `.measure` with SI-suffix parser, writes `result.json`
  `{tSU,tH,tCQ,hspice_ran,...}`. **Two independent sweep vars** (not seesaw),
  **hold obs window = t_clk4 + obs_hold_offset** (inside CLK=1, < next edge).
  Includes `.ic` to break SR-latch DC metastability. ABSOLUTE paths fixed.
- `uploader_dff.py` — pushes files to .75 via eda_flow MCP HTTP
  (127.0.0.1:18891), runs char_gen, fetches results. JSON files sent via
  `base64 -d` (write_file auto-deserializes JSON-looking content; heredoc
  breaks on embedded double-quotes). Reuses saved workdir.
- `dff_A.sp` / `dff_B.sp` — NAND-based master-slave DFF (nd2 + dlat + dff
  subckts), level-1 Shichman-Hodges. A/B differ in sizing/corner/load.
- `params_A.json` / `params_B.json` — vdd/tclk/sweeps/obs/threshold.

## The blocker (specific, with data)
Goal: tSU/tH/tCQ all positive, measurable (tens of ps), Q swings rail-to-rail,
so the check.py traps (hold-window-bug → fake tH=0, seesaw, cross-input,
SI-suffix, name-agnostic) discriminate by VALUE.

**Problem: level-1 MOS DFF does not produce rail-to-rail Q under the loadings
needed to make tSU/tH measurable.** Three topologies tried on .75 (HSPICE
V-2023.12-SP1-1, `hspice` bin):

1. **TG master-slave (first attempt)** — WRONG latch feedback (tg2 shorted
   s1b→s1, fighting inv1). Fixed → proper 2-inverter cross-coupled feedback
   (forward inv1 s1→s1b, feedback inv_fbm s1b→s1fb, tg2 s1fb→s1). Symptom
   resolved, but:
2. **TG DFF with Cs1=8fF** — s1 rises too slowly (τ~400ps, reaches only
   0.46V at CLK↑ for tsu=250p) → never captures D=1. Reducing Cs1=3fF →
   still s1~0.30V at 2.1ns. TG nmos body-effect threshold drop + weak PMOS
   pass → marginal. Also output was inverted (Q=NOT D) — fixed with
   2-inverter output buffer (q1→Qb→Q).
3. **NAND master-slave (current dff_*.sp)** — fully boolean, no TG threshold
   drop. With Cqm load → Qm too slow (0.697V at CLK↑, below slave NAND
   threshold ~0.75). Removed Cqm, added Cclkb=10-15fF on clk_b to slow
   master EN (raise tSU, widen tH aperture). **Result: Q stuck mid-rail
   (A max 0.335V @ tsu=450p; B max 0.384V @ tsu=560p) — never reaches
   0.7*vdd.** The clk_b inverter driving 10-15fF is too slow → master barely
   transparent → Qm/Q marginal. Hold sweep: Q rises monotonically with th
   (0.02→0.23V) but never crosses threshold → tH not extractable either.

Root cause: level=1 Shichman-Hodges with small W/L (0.5-1.2u / 0.13-0.15u)
and kp=20-80u gives weak, marginal logic that doesn't swing rail-to-rail
once you add enough capacitance to make tSU/tH land in a sweep-measurable
range. It's a fundamental tension: fast (rail-to-rail but tSU/tH~0,
degenerate) vs slow (measurable tSU/tH but marginal logic levels).

## Concrete next-round path (pick one)
**A (recommended): precharacterized robust DFF.** Use a SAFE level-1 sizing
that swings rail-to-rail with NO extra internal caps — accept that natural
tSU/tH are small (~20-40ps) and use a FINE sub-ps sweep (tsu in
[0,5,10,15,20,30,40,60,80]ps; th similar) with .measure resolution. Verify
Q swings 0→vdd cleanly first (debug deck: D=1 captured at tsu=200p → Q must
= vdd ±5%). Only then sweep. tH>0 needs the master turn-off aperture — for
NAND DFF this is ~1 NAND delay; probe with a D-glitch test, observe Q during
CLK=1 phase. If tH genuinely ~0 for the chosen topology, switch trap (o)
from value-based to SOURCE-INSPECTION (regex: char_gen.py must derive hold
obs from tclk with explicit upper bound, not a fixed large literal).

**B: foundry-cell DFF via eda_flow.** Pull a real .subckt DFF from a PDK
on .75 (portable as a black-box .subckt with .model), characterize IT.
Higher fidelity to the trace (kaixuanx used a real TSPC DFF). Risk: PDK
cells may need corner files / process libs.

**C: drop tH, keep tSU+tCQ.** Reduce to 2 metrics; weaken the trap set but
still distinct (no other B case does DFF timing). Only if A/B infeasible.

## Artifacts NOT committed to official assets/reference
The half-built `assets/EDA-Eval-DesignFlow-DffSetupHoldChar-001/` and
`reference/EDA-Eval-DesignFlow-DffSetupHoldChar-001/` were REMOVED from
EDA-Flow-Bench (so they don't look like a finalized case). WIP lives here.
No jsonl entry. Ledger 6tiy7 stays `deepread` (NOT `case`).

## Pipeline validated this round (reusable)
- eda_flow MCP HTTP reachable from local shell via curl/urllib (Accept:
  application/json, text/event-stream). open_session needs task_id+eval_id.
- HSPICE on .75: `/apps/synopsys/SRB/hspice_V-2023.12-SP1-1/hspice/bin/hspice`,
  in PATH. `hspice -i deck -o out` → out.lis/out.mt0. Success marker
  `***** hspice job concluded`. `.meas` results in .lis as `name = value(SI)`.
- Subckt internal nodes accessible in .print/.meas via hierarchical `xdff.node`.
- write_file corrupts JSON-looking content (auto-deserializes) → use
  `echo <b64> | base64 -d > path` in run_commands for .json.
- char_gen subprocess must use ABSOLUTE deck path (relative deck + subdir cwd
  → hspice "input not found").
