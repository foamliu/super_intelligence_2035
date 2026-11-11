# Deepread #524 — mauo7 (zlhou, hfeg0pjn200, mc=39, netlist:262)

## Trace source
- session_file: `1793608573097_mauo7.messages.json` (456KB, 69 msgs, 11 user turns)
- host: 10.129.40.209 (hfeg0pjn200) — scp'd from `/home/zlhou/.cline/data/sessions/1793608573097_mauo7/`
- user: zlhou, workdir: `/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/tiling/tiling_2prf_420`
- domain: schematic_netlist / netlist (D-shard)
- fresh-USER for D (zlhou only in C.jsonl, not D.jsonl)

## Real task summary (11 user turns)
2PRF SRAM tiling generator (`2prf.py`, 1379 lines, `SRAMGenerator` class). User iteratively modifies GIO/LIO leafcell placement to support **A/B alternating** variants, with **M (middle) variant** also participating in A/B, and **MUX=4 special case (no A/B distinction)**.

- **U#0**「现在的工作目录是/proj/lacaa/TV1_FS/workdir/zlhou/2prf_work/tiling/tiling_2prf_420，未经我允许不要修改现有的任何文件，现在先查看一下2prf.py这个文件的内容」→ assistant reads `2prf.py` (1379 lines, `SRAMGenerator(nt, nw, nb, cd, cm, bk, ...)`).
- **U#1**「检查一下哪里用到了LEAFCELL_replace.csv中的内容」→ assistant traces CSV usage: `_load_leafcell_replace_map()` reads CSV, locates `Replace_CMBK`/`end_replace_CMBK` markers, selects column `f"M{CM}B{BK}"`, builds `leafcell_replace_map{default_name: replacement_name}`. Then `_get_leafcell_replace_name(default)` returns map hit or default.
- **U#2**「我现在的leafcell具有修改，GIO除了分为L和R，在其中还分为A和B，左右的AB交替摆放，告诉我应该在哪些地方修改哪些东西」
- **U#3**「GIOL/GIOR 各自独立，从 A 起，中间 M 也参与，同时，当MUX=4时不区分AB，其他情况区分AB，使用CSV中的名称。注意，不能动我的任何文件，直接在这对话框里告诉我怎么改」
- **U#4**「你这样改，输出的gio是怎么排布的？」→ assistant explains: GIOR right side N columns, `y = num_gio_r//2 - 1` is M variant, A/B alternates `i%2==0→A, i%2==1→B`, CM==4 → all `_A`.
- **U#5..U#10**: debugging iterations — f-string missing `f` prefix (`{ab}` literal → KeyError), missing `_` underscore, `_gio_ab_suffix` indentation bug (dead code → returns None), `NameError: name 'ab' is not defined` (forgot to set `ab = self._gio_ab_suffix(i)` in LIO loop), LIO LIOL also needs same fix. Real leafcell netlist `HC2P_AA_ALL_LEAFCELL.netlist` doesn't have A/B variants (only `HC2P_LEAF_GIOR_M4_1B` / `_M` without A/B suffix, prefix `HC2P_` not `HC2PFS_`).

## Extracted spec (for benchmark synthesis)
**Task**: Write a Python SPICE netlist tiling generator `gio_lio_tiling.py` that places GIO (global IO) and LIO (local IO) leafcells for a 2PRF SRAM tiling, with A/B alternation rules.

**Placement rules (verbatim from trace U#3 + assistant U#29/U#31/U#33)**:
1. GIOL and GIOR each **independent** — each side has its own A/B alternation, starting from A at column i=0.
2. **M (middle) variant also participates in A/B** — at column `y = num_gio_r//2 - 1` (for GIOR) the leafcell name has `_M` suffix AND still gets `_A` or `_B` based on y's parity → `_A_M` or `_B_M`.
3. **MUX=4 (CM==4) special case**: NO A/B distinction — all columns use `_A` (no alternation), but M variant still `_A_M`.
4. **Otherwise (CM≠4)**: A/B alternates by `i%2==0→A, i%2==1→B`.
5. **GIOL has NO M variant** — all columns ordinary (no `_M`).
6. **LIO follows same rules as GIO** — LIOR has M variant at `y_lio = num_lio_r//2 - 1`, LIOL has no M variant. LIO leafcell base name differs (`HC2PFS_LEAF_LIO_M4B4_1B` vs GIO `HC2PFS_LEAF_GIO_M4_1B`).
7. **CSV name mapping** — read `leafcell_replace.csv` (markers `Replace_CMBK`/`end_replace_CMBK`, column `f"M{CM}B{BK}"`), build `leafcell_replace_map`, apply via `_get_leafcell_replace_name(default)` (return map hit or default).
8. **Netlist emission** — emit `.SUBCKT` calls via a `call_subckt(name, inst)` interface; output netlist file `gio_lio.netlist` + JSON manifest `placement_manifest.json` listing every placed instance `(inst_name, side, col_idx, variant_ab, is_middle, leafcell_name)`.

## Synthesis plan (B-grade, self-contained)
- **A (visible input)**: `inputs_A/` — `spec_A.json` {num_gio_l:4, num_gio_r:6, num_lio_l:4, num_lio_r:6, CM:2, BK:1, leafcell_csv:"leafcell_replace_A.csv"}, `leafcell_replace_A.csv` (markers + M2B1 column mapping GIO→HC2PFS_LEAF_GIO_M4_1B*, LIO→HC2PFS_LEAF_LIO_M4B4_1B*), `task_brief.md`.
- **B (hidden input)**: `hidden/inputs_B/` — `spec_B.json` {num_gio_l:8, num_gio_r:10, num_lio_l:8, num_lio_r:12, CM:4, BK:1} (CM=4 → no A/B), different CSV mapping, different leafcell name prefix.
- **C (embedded in check.py)**: small inline spec {num_gio_l:3, num_gio_r:5, num_lio_l:3, num_lio_r:5, CM:2} with different CSV names — anti-hardcode.
- A/B/C disjoint on: counts (4/6, 8/10, 3/5), CM (2/4/2), CSV leafcell name prefixes.
- **SUT**: `gio_lio_tiling.py` — pure stdlib (json/csv/re/sys/argparse/os), forbidden: subprocess/socket/urllib/ctypes/eval/exec/numpy/pandas, forbidden: B/C literals.
- **Output**: `gio_lio.netlist` (one `.SUBCKT <leafcell_name> <inst>` per line, in placement order) + `placement_manifest.json` {instances:[{inst, side, col, ab, is_mid, leafcell}], summary:{n_gio_l, n_gio_r, n_lio_l, n_lio_r, n_mid_gio_r, n_mid_lio_r, CM, has_ab}}.
- **check.py ≥8 assertions**: a. zip+imports+no B/C literals; b. py_compile; c. run B exit 0 + output files exist; d. manifest schema; e. total inst count = sum of 4 counts; f. GIOR A/B alternation correct (i%2==0→A); g. GIOR M variant at y_r=num_gio_r//2-1 only, with _M suffix; h. GIOL no M variant; i. LIO follows same rules (LIOR has M, LIOL no M); j. CM==4 → all _A, M still _A_M; k. CSV name substitution applied (HC2PFS_LEAF_ prefix from CSV); l. anti-hardcode C≠B; m. 3-seed sha256. → k=13.
- **difficulty**: L2 (real netlist tiling generation logic — multi-rule placement + CSV mapping + SPICE .SUBCKT emission, not pure text manipulation).
