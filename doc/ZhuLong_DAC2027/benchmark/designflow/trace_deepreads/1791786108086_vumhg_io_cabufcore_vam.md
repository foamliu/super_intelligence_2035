# Deepread — 1791786108086_vumhg (e03179 / hfeg0plg90, mc=251) — IO_CABufCore Verilog-AMS modeling (analog_context)

## Trace provenance
- session: `1791786108086_vumhg.messages.json` — 1.18 MB, 319 msgs (167 tool_use), agent=`lead` (zhulong **vam-agent** skill).
- user: `e03179`  host: `hfeg0plg90`  mc=251  domain: **analog_context**
- live file (now cleaned from disk): `/home/e03179/.cline/data/sessions/1791786108086_vumhg/1791786108086_vumhg.messages.json`
- snapshot 2026-11-02 12:33. Fetched to .75 sandbox this round.
- claimed shard-D 2026-11-03 08:3x (domain=analog_context, 7→8 target).

## What the user actually asked (faithful user turns)
1. **msg[0] (only substantive user turn)** — verbatim:
   `[vam-agent] 帮我建模 IO_CABufCore，netlist 在 /home/e03179/IO_CABufCoreTT092V25C/netlist`
   = "build a model for IO_CABufCore; the netlist is at <path>". A single broad
   characterization/modeling request. No root-cause / no fix proposed by user ⇒
   compliant A-档 faithful T0 (verbatim usable as prompt).
- (remaining user msgs are tool_result wrappers — no further instructions.)

## Assistant tool chain (167 tool_use)
editor 68 · run_approved_command 41 · read_files 40 · list_allowed_files 12 ·
search_codebase 3 · skills 1.
- Skill invoked: `vam-agent` (Verilog-AMS behavioral modeling agent).
- Pipeline built in TOP=`/home/e03179/IO_CABufCoreTT092V25C`:
  - `vam_step0_inspect.py` (read-only): locate `.SUBCKT IO_CABufCore` in netlist,
    print netlist tail (top-level testbench), X-instance lines of IO_CABufCore,
    fsdb inventory by mtime, newest finesim/primesim `*fp.log`, `ip_library` dirs,
    `input_cosim.sp` key lines (verilogams/.include/.tran/.probe/.temp/pvdd).
  - …(step1 characterization)…
  - `vam_iter2.py` — iterate model fitting against cosim timing data.
  - `vam_doc.py` — documentation.
  - `vam_finalize.py` — produce final `.va` model + report.
- `run_approved_command` profile=`python-runner` executes each vam_*.py.

## File structure (TOP = /home/e03179/IO_CABufCoreTT092V25C)
- `netlist` (symlink → `netlist.presim`) — SPICE netlist of IO_CABufCore (CMOS IO
  buffer core). Contains `.SUBCKT IO_CABufCore …` + transistor instances.
- `input.sp` — base SPICE stimulus deck.
- `input_cosim.sp` — cosim deck: `.include` verilogams model + `.tran/.probe/.temp/pvdd`.
- `cosim_def.va` — Verilog-AMS behavioral model definition (the artifact being calibrated).
- `stimulus`, `run_cosim.sh` — cosim driver.
- `write_model.py`, `run_sim_clean.py` — model writer + clean-sim runner.
- `cosim_timing_param/IO_CABufCore/{TT_dr0,TT_df0,TT_tr0,TT_tf0}.dat` —
  characterization data: drive rise (dr0) / drive fall (df0) / tristate-rise (tr0)
  / tristate-fall (tf0) timing tables at TT/0.92V/25C.
- `*.fsdb` (waveforms), `*fp.log` (finesim/primesim logs), `ip_library/`.
- **PVT corner**: TT / 0.92V / 25C (typical, low-voltage IO).

## Sub-skill (reproducible)
**Verilog-AMS behavioral model building for an IO buffer cell via SPICE–cosim
characterization.** Given a SPICE netlist + cosim harness, characterize the
drive/tristate path timing (rise/fall delays → TT_dr0/df0/tr0/tf0) and calibrate a
`.va` behavioral model to match the SPICE netlist across the corner; produce the
model + a characterization report.

Distinct from existing shard-D cases (opamp sim, bandgap, PFD, SRAM SNM, etc.) —
this is the **IO-cell behavioral-modeling / characterization** sub-skill (L2/L3).

## Reproducibility & real-artifact recovery
- Real workdir `/home/e03179/IO_CABufCoreTT092V25C/` is **gone from disk**
  (cleaned after task). ⇒ real artifacts MUST be recovered from
  `vumhg.messages.json` tool_results (read_files/editor new_text).
- Confirmed recoverable: `IO_CABufCore` appears 478× in messages; `SUBCKT
  IO_CABufCore` present; `TT_dr0.dat` etc. present. Next round: extract netlist
  body, input.sp, cosim_def.va, TT_*.dat tables, vam_*.py from tool_results
  (read_files content is stored — likely as list-of-{type:text,text:…}; the
  netlist read_files result for path `…/netlist` carries the subckt body).

## Synthesis plan — `EDA-Eval-DesignFlow-IOCABufModel-001` (analog_context, L2, B档)
Two viable tracks (decide next round after recovering real netlist):

**Track A (faithful L2/L3, preferred if .75 supports verilogams cosim)**:
self-contained CMOS IO buffer (tri-state driver: predriver + final-stage
pull-up/pull-down + enable) at level-1 MOS; cosim harness = SPICE netlist vs a
parametric `.va` behavioral model; characterize drive/tristate rise/fall timing
across a PVT corner; deliver `io_cabuf_model.py` (builds netlist + .va + runs
cosim char + writes model + report) + `model.va` + `char_report.json`.

**Track B (deterministic upstream, if cosim/verilogams not reachable on .75)**:
"netlist-driven IO timing characterization driver" — parse a SPICE IO-buffer
netlist → set up drive-rise/drive-fall/tristate-rise/tristate-fall `.measure`
tran sims (stimulus from a template) → run HSPICE on .75 → extract
TT_dr0/df0/tr0/tf0 delay tables → write `char_report.json` (per-arc delay,
slew, monotonicity, enable-effect). Real L2 (subprocess HSPICE on B).

**Visible A**: IO_CABufCore, TT/0.92V/25C, drive strength N=8, load 50fF.
**Hidden B**: IO_CABufCore_B, SS/0.88V/-40C, drive strength N=4, load 30fF
  (different corner + different drive ⇒ different TT_dr0/df0/tr0/tf0 ⇒ defeats
  hardcoded constants; cross-input guard on extracted delays).

**Check conditions (≥8, target ~14)** — draft:
  a. submit.zip contains non-empty `io_cabuf_model.py` + `char_report.json`
  b. `io_cabuf_model.py` py_compile passes
  c. on hidden B, script runs HSPICE (subprocess exit 0) and report.sim_ok=True
  d. report schema valid (cell, corner, arcs[dr0/df0/tr0/tf0]→{delay,slew}, n_arcs)
  e. B n_arcs == 4 (dr0/df0/tr0/tf0)
  f. B each arc delay > 0 AND < sim window
  g. B drive-rise delay ≠ drive-fall delay (real asymmetry, not stub)
  h. B tristate delays > drive delays (enable path longer)
  i. B slew within plausible range (ps-scale, corner-dependent)
  j. **cross-input guard**: B delays ≠ A delays AND ratio tracks PVT/drive-strength
     ratio (defeats hardcode-expected fake — §4.9 critical)
  k. B report arcs monotone in load (if multi-load sweep) / consistent across seeds
  l. negatives (3错解) all FAIL
  m. §4.9 three-fake-submission (empty/print-expected/ref-no-core) all FAIL
  n. randomization: 3 seeds ⇒ same verdict

**Deliverable contract**: `outputs/submit.zip` containing `io_cabuf_model.py` +
`char_report.json` (+ any helper .sp/.va). entry_point `outputs/submit.zip`.

## Verdict / status
- Strong analog_context L2 candidate; faithful to a real, hard, reproducible
  sub-skill (IO-cell behavioral modeling / timing characterization). Distinct
  from all 7 existing analog_context cases + 16 schematic_netlist + 5 waveform.
- **Status: DEEPREAD DONE 2026-11-03 08:4x; case NOT yet synthesized.**
  DEBT: 1 deepread pending synthesis. Next round (shard D) MUST deliver this case
  first (recover real artifacts from messages.json → build assets/reference/
  hidden/negatives → self-verify → append D.jsonl → mark case).
