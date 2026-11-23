# Deepread — wvtff (weiyue @ hfeg0plg78, mc=471)

**Session**: `1795341648818_wvtff.messages.json` (nested under `sessions/1795341648818_wvtff/`), 667 msgs total across two files — `.messages.json` (6 active msgs) + `.messages.archive.json` (542 msgs), ~2.65 MB merged. Retrieved via `scp e0031982@hfeg0plg78:.../1795341648818_wvtff/1795341648818_wvtff.messages{,.archive}.json` (`.75` → hfeg0plg78 免密 ssh 通，e0031982 身份).

**User**: weiyue. G5CIP HSPICE device-characterization sweep runner author. Pure spice_sim/characterization domain — `hspice` keyword 1447 hits + `netlist` 307 hits, no PNR/layout/verification leakage. Cross-4-shard dedup (4544 sessions across A/B/C/D ledgers) → NONE matched ⇒ 真 fresh.

**Why r1089 unblocked r1088**: r1088 reported "fresh 池耗尽" but its `fresh_b_spice_local.tsv` cross-shard dedup was stale. r1089 rebuilt `fresh_b_spice_r1089_uniq.tsv` (1376 unique sessions, mc≥5 spice keywords) and re-ran cross-dedup against all 4 shard ledgers → **153 真 fresh** candidates. wvtff is the top candidate (mc=471, pure HSPICE char, no near-dup).

**Trace evolution** (667 msgs): 磁盘管理 → 版本化目录 `00_streams_<ver>/` → run all / watch / stop 命令 → watch 单行实时进度 → per-device 参数摘要 → watch v1→v12 (解决 `\r` / `ocrnl` / 单行 / finished 截断 bug) → 对齐数据。weiyue 开发 `run_cells.py` (每器件 14364 AC + 3564 DC points, bsub hspice).

**Key observed watch_line** (trace msg 517, 实测):
```
{netlist=DC 3564/3564} {submit=11880/11880} {sim(done)=11746/11880} | current=ptn_lvl finished=ntn,ntn_m,ntn_lv,ntn_lvi
```
This is the ground-truth rendering the case asks the SUT to reproduce from the two source files.

**Source-file formats** (scp'd `run_cells.py` / watch / run / stop / `readme_bsub.md`):
- `.progress` file: sorted `key=value` lines — keys `current` / `phase` / `net` / `sub` / `sim` / `done` / `extract`. Throttled 0.3 s writes.
- `run_all` log: device banner `=== <name> (<pol>/<thick>) ===` (wrapped in ANSI `\033[1m...\033[0m`), `gen (AC|DC) X/Y`, `submit=X/Y`, `done=X/Y`.

**Reframe** (case = `EDA-Eval-DesignFlow-HspiceSweepWatchRender-001`): standalone Python script `hspice_watch.py <progress> <log> <out.json>` — L1, stdlib only. 双源解析 → 结构化 JSON 进度报告 + `watch_line` 渲染串. The `watch_line` is the single-line human progress string weiyue's `run_cells.py` prints during a sweep (the thing the user actually `watch`ed).

**Anti-hardcode hidden B** (5-axis distinct from A):
1. **不同器件族**: B = `sntn` / `sntn_hvt` / `ntn_hvt` / `pt` (4 devices) vs A = `ntn` 族 (`ntn` / `ntn_m` / `ntn_lv` / `ntn_lvi` / `ptn_lvl`, 5 devices).
2. **不同数值**: B = 11280 AC points vs A = 14364 AC points.
3. **phase 语义不同**: B `phase=extract result` (post-sim extraction phase) vs A `phase=submit` (mid-sweep submission phase).
4. **B 含 extract 字段**: B `.progress` has `extract=AC 8/14` (8 of 14 extractions done); A has no `extract=` key.
5. **器件数 + 版本异**: B 4 devices / `v0d94 Rev05` vs A 5 devices / `v0d9 Rev04`.

**check.py — 16 teeth (a–p)**:
- (a) zip valid + compile + size stub
- (b) B exit 0 + non-empty JSON out
- (c) top-level 15 keys all present
- (d) `current_device == "sntn_hvt"`
- (e) `phase == "extract result"`
- (f) `netlist == None` (B has no `net=` line)
- (g) `submit == (9824, 9824)`
- (h) `sim == (9824, 9824)`
- (i) `extract == ("AC", 8, 14)`
- (j) `finished_devices == ["sntn","sntn_hvt","ntn_hvt"]`
- (k) `devices_started == ["sntn","sntn_hvt","ntn_hvt","pt"]` (order + per-device counts)
- (l) `last_gen == ("DC",1410,2820)` + `last_submit` + `last_simdone`
- (m) `pct == 100.0`
- (n) `watch_line` format + `{netlist=--}` token + values
- (o) **anti-hardcode**: A device names exact-member absent from B output; A value strings absent from `watch_line`; A `pct != 98.87` (uses exact-member match — `"ntn"` is a substring of `"ntn_hvt"`, so naive `in` would false-positive; check.py uses set membership)
- (p) 3-seed sha256 deterministic

**3 negatives** (each FAILs on a different tooth family):
- `neg_empty.py` → (a)/(b) out_B.json missing/empty
- `neg_print_only.py` — hardcodes A's report → (d) `current_device='ptn_lvl'` (A's value) vs expected `sntn_hvt`; also trips (e)/(f)/(g)/(h)/(i)/(j)/(k)/(l)/(m)/(n)
- `neg_core_removed.py` — really parses B but fixes `watch_line` to A's + injects `ntn` + `pct=98.87` → (j) `finished_devices` includes A's `ntn` / (n) wrong `watch_line` / (o) anti-hardcode trip

§4.9 三假 (empty shell / print-only / core-removed) 全 FAIL ✓.

**Self-verify**: REF 16/16 PASS ✓; `negative_selftest.py` 3/3 FAIL-as-expected ✓; 3-seed sha256 一致 ✓ (tooth p); A `watch_line` 与 trace msg 517 完全一致 ✓.

**Ledger**: `trace_ledger_B.tsv` claim wvtff → mark case `EDA-Eval-DesignFlow-HspiceSweepWatchRender-001` (2026-11-23 14:52).

**Deliverables**: `cases/B/EDA-Eval-DesignFlow-HspiceSweepWatchRender-001.json` + `reference/…/` (check.py, hspice_watch_ref.py, negative/{neg_empty,neg_print_only,neg_core_removed}.py, negative_selftest.py) + `assets/…/A/` (progress_A.txt, run_all_A.log, expected_A.json, task_brief.md) + `assets/…/hidden/` (progress_B.txt, run_all_B.log, hidden_manifest.json). `.log` files force-added (`*.log` gitignored; 268 precedent .log assets in repo).

**Metrics**: trace coverage covered=567 / target=4398 = 12.9% (mc≥10, +1 this round). k_rationale=16 == k_check=16 ✓. MEMORY_B < 32 KB ✓. DEBT: 1 (r1057 campaign "55 legacy 缺 selftest" 余 53).

**Next-round pool**: `fresh_b_spice_r1089_dedup` 余 152 fresh. Top candidates: 2m9z2 / xkwxk (junlingw GENGUI — near-dup risk, check first), 5ew0s (wendy1w mc147), samw8 (jason1t mc126), ofbxi (guangmingz mc107), tuh6e (devonma mc104), 5z9ge (han1liu mc102).
