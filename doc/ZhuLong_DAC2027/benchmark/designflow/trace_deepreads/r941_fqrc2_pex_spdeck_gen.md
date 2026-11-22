# r941 deepread — session 1794919784130_fqrc2 (PexSpDeckGen-001)

## provenance
- user: e0039786  (Desktop cwd, deepseek-v4-flash)
- host: hfeg0plg54 / 10.129.35.73
- session: 1794919784130_fqrc2 (forked from 1794918789506_dpcmw, cancelled exit 0)
- match_count: 431  (keywords: pex:788 drc:168 lvs:159 calibre:89 virtuoso:946 .gds:359)
- ledger: shard C, claimed → case (PexSpDeckGen-001)
- fetched: fqrc2.messages.json (509 msgs, 1.8 MB) + fqrc2.json

## session scope (4 sub-tasks)
1. DRC analysis of PARA_inverter2.il (DRC rule deck walk-through).
2. DUT pcell library generation in SKILL/Virtuoso — MOSCAP_CV, VARACTOR,
   DIODE_LEAK, RES_RS, NMOS_IDVG, INV_ARRAY pcells.
3. GloryEX PEX closed-loop automation — IL→GDS→Glory dspf→Hspice run.
4. **make_sp.py** — DSPF port parser + Hspice test-deck generator
   (msgs #161-294). ← chosen sub-task.

## chosen sub-task: make_sp.py
DSPF (`.dspf`) parasitic netlist from GloryEX/Calibre PEX has a `.SUBCKT
<design> <ports...>` header. For post-layout sim the DSPF is `.inc`'d into an
Hspice `.sp` test deck, but the DSPF exposes more ports than the measurement
needs — **unused ports must be terminated with 0 V DC sources** or Hspice
reports floating nodes. The script automates this for 5 measurement types:
cv / idvg / leakage / rs / delay.

### reference code (extracted from msg #161 + edits #163/#164/#263/#265/#288/#289)
- `dspf_ports(path)` — regex `.SUBCKT` header → `(design, [ports])`.
- `term_unused(ports, keep)` — emits `Vxx <port> 0 DC 0` for non-kept ports.
- `gen(...)` — builds the .sp text by mtype; includes `.options`, `.temp`,
  `.LIB`, `.inc`, termination lines, `.param vdd/ith`, stimulus, `.meas`, `.end`.
- CLI: `--dspf --spout --terms --type --model --libsection --temp --vdd`.

### key traps (verified against real code)
1. unused-port termination — every `ports - terms` port needs a `Vxx` line.
2. `.meas`/`.PROBE` source-name consistency — `I(Vg)` must match a declared
   `Vg` source (not e.g. `Vdefine_G`).
3. no hardcoding — design name + ports must come from the live `.SUBCKT`;
   hidden B has different name/ports/parasitics than visible sample A.
4. `.inc` must use the actual `--dspf` path, not a constant.

## case design
- case id: PexSpDeckGen-001  (jsonl id: None, matches WireWidthSpaceRuler pattern)
- mode: design_flow, entry_point: outputs/submit.zip
- domain: physical_verify, track: B, tier: L2-boundary
- visible assets: sample.dspf (A), example_cv.sp, task_brief.md
- hidden: hidden_B.dspf (pexd_inv_full, 14 ports — supports all 5 mtypes),
  hidden_B2.dspf (pexd_buf_x8, 6 ports — anti-hardcode cv)
- check.py: 15 teeth (a-o), runs only on B (5 types) + B2 (cv) + determinism
- negatives: hardcoded_design, no_terminate, wrong_meas_source, wrong_inc_path
- self-verify: ref 15/15 PASS, 4/4 negatives FAIL, determinism byte-identical ✓

## coverage
- k_check = 15 (≥ 8 gate ✓)
- 3 negatives all FAIL ✓ (4 provided)
- §4.9 three-fakes FAIL ✓
- hidden B (not A) used for grading ✓
- A-tier self-contained (no external EDA tool needed — pure text generation) ✓
- real trace provenance in metadata.trace_source ✓
