# Deepread: 1789895350779_hoh52 (shard D #292)

- **user/host/mc**: e0039602 / 10.129.8.136 / mc=64
- **domain**: waveform
- **session**: `/home/e0039602/.cline/data/sessions/1789895350779_hoh52/1789895350779_hoh52.messages.json` (64 msgs, 35 user / 29 asst)
- **real user_input**: only U#0 is a real user turn (the other 34 "user" msgs are tool results):
  > 请你阅读skill目录，找到这两个阅读波形的skill，请你修改waveview-fsdb-reader再写一个waveview-fsdb-readerV2.py，让他可以像finesim-fsdb-reader一样对读出的信号生成一个简单的分析报告
  - Pure produce-task; user proposes goal (write V2 with analysis report like finesim-fsdb-reader), gives NO root cause / fix → **A-faithful**.

## Tool chain (assistant)
1. `run_commands` find skill dirs; `list_allowed_files` /home/e0039602 + /
2. `read_files` the two skills: `waveview_fsdb_reader.py` (wv -ace_no_gui backend, returns `{sig:[(t,v)...]}`) and `fsdb_reader.py` (fscript + `analyze_signal`: digital edge/pulse, analog stats + zero-crossings)
3. `editor` (write_to_file) → `/home/e0039602/Documents/waveview-fsdb-reader/waveview-fsdb-readerV2.py`, then iteratively → `/home/e0039602/.cline/scripts/data/waveview-fsdb-readerV2.py` (final deliverable, 395 lines)
4. `read_files` to re-verify; final summary

## Deliverable (gold)
`waveview-fsdb-readerV2.py`:
- imports `WaveViewReader, parse_time_str, normalize_sig_name` from `waveview_fsdb_reader`
- `detect_signal_type` (digital = dwells at 2 levels; analog = single level + spike)
- digital: `detect_edges` (rise/fall crossing thresh, t_curr), `detect_pulses` (start,end,width)
- analog: `analog_stats` (n_points, t_start/end, duration, v_min/max/mean, v_min/max_at, first, last), `zero_crossings` (linear interp, rising/falling)
- `analyze_signal` / `analyze_signals` / `read_and_analyze` (reader + analysis)
- `format_time` / `format_value` / `format_report` / `format_all_reports`
- CLI `main` (argparse: fsdb_path, signals, step, t_start, t_end, --direct, --thresh; auto-wrap bare names in v())

## Why B-grade synthesized
Real `.fsdb` / `test.fsdb` (symlink → /proj/drcpa/...) is permission-denied on .75 and not attachable; the wv binary / bsub queue can't run in the check. So:
- **Assets (A, given to SUT)**: faithful reconstructions of `waveview_fsdb_reader.py` + `fsdb_reader.py` (the two skills the user points to) + their SKILL.md docs + prompt + task_brief.
- **Hidden B**: synthetic waveform data — a digital clock (0↔1 toggling) and an analog current (baseline + two negative Gaussian dips, crosses 0). The check imports the SUT's V2 with a **stub** `waveview_fsdb_reader` (so no real wv/FSDB needed) and runs the pure analysis functions on B, comparing to an independent reimplementation of the reference algorithm.
- B2 (anti-hardcoding): different toggle period, dip centers/depth, signal names.

## Case
`EDA-Eval-DesignFlow-WvFsdbReaderV2Gen-001` (waveform, A-faithful, B-grade synthesized, L1, 14 conditions a-n).
