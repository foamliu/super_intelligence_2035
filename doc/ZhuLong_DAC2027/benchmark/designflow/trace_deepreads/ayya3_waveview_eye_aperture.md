# Deepread: 1794199386873_ayya3 (e0023936@hfhds201)

- session: `1794199386873_ayya3.messages.json` · user e0023936 · host hfhds201
- match_count: 120 · d_frac: 0.67 · waveview: 246 (D-dominant, waveform domain)
- claimed in ledger_D → case EDA-Eval-DesignFlow-EyeApertureSelect-001 (#483)

## Trace arc (190 msgs / 8 user turns)

WaveView dataeye-measure pipeline for DDR/LPDRAM eye-diagram VREF sweep:

1. USER requests Synopsys WaveView CLI measure on waveform `sslvht_10667` (10667 Mbps),
   sweeping VREF 0–190 mV in steps; each VREF records `max_width_ps`, `skew_ps`, `eye_height_mV`
   into a `.rep` report.
2. Assistant builds the WaveView dataeye-measure command pipeline, iterates on waveform load +
   measurement window setup, produces the sweep report.
3. Final collector parses the `.rep`, reads thresholds from header comments
   (`skew_threshold_ps`, `height_threshold_mV`), filters rows where skew<=thr AND height>=thr
   (rejecting edge false-peaks: high-skew, low-height rows at sweep boundaries),
   then selects the row with max `max_width_ps` (tie-break: skew min → vref min) as the
   optimal eye aperture / VREF. Writes a summary table.

Key insight: raw global-max of `max_width_ps` is unreliable — it lands on VREF-edge false-peaks
(skew huge, eye height low). The threshold filter + max selection is the real algorithm.

## Why B-grade synthesized

Private assets not reproducible in SUT sandbox:
- WaveView CLI install + license + waveform library
- `/home/e0023936` project dir + DDR6 simulation run dir
- Real waveform `sslvht_10667` data

→ Synthesize a self-contained `.rep` text format carrying the same algorithmic structure
(parse header → threshold filter → max-select → sentinel on empty → CSV output).

## Synthesized A / B / allinvalid

- A (visible): `sslvht_10667`, thresholds 15.0/100, false-peak at VREF=60 (width 68.33, skew 35.12, height 90 — rejected by both thresholds), optimal VREF=100 (width 56.99, skew 5.38, height 180).
- B (hidden): `polht_8567`, thresholds 12.0/110, false-peak at VREF=220 (width 72.55, skew 38.60, height 95 — rejected), optimal VREF=120 (width 61.40, skew 5.90, height 185). VREF range 0–260 step 20, structurally distinct from A.
- allinvalid: `badhost_3200`, thresholds 10.0/120, all rows exceed thresholds → sentinel row (-1/-1/-1) tests no-crash + empty-valid path.

A∩B name/value sets disjoint (anti-hardcode). B's optimal VREF (120) != raw-max VREF (220) —
check.py condition (g) defeats naive raw-max implementations.

## check.py 14 conditions (a)-(n)

Independent oracle embedded (A, B, allinvalid values hard-coded in check, NOT imported from ref):
a zip+pycompile · b no-forbidden-runtime · c run-B-exit0-csv · d 5-col header · e B name ·
f B corner · g B vref=120 (not 220) · h B aperture=61.40 · i B skew=5.90 ·
j cross-input A vref=100 (defeats hardcode-B + raw-max=60) · k A aperture+skew ·
l allinvalid sentinel -1 · m 3-seed determinism · n anti-hardcode source tokens.

Self-verify: ref PASS 14/14; 3 fake + 2 naive negatives all FAIL (NEG_RC=0, distinct c/j/g/e).
