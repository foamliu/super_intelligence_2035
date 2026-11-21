# Deepread: 26n1l_pumpcore_aging_deck (ryanren @ hfeg0pfn120, B shard, r980)

## Trace provenance
- session: `1795225607049_26n1l` (ryanren @ hfeg0pfn120 / 10.129.33.246)
- scan: `ssh_eda_search_20261121_151844/summary.tsv`, mc=251 (spice_kw=2096, hspice-dominant)
- domain: spice_sim (B-pure)
- FRESH check: NOT in any of 4 shard ledgers A/B/C/D (suffix-normalized sid dedup, 5619 touched sids)
- downloaded via `ssh 10.129.33.246 cat /home/ryanren/.cline/data/sessions/1795225607049_26n1l/1795225607049_26n1l.messages.json` (1093365 bytes, 160 msgs)

## User intent (8 user turns)
- U[1]: find aging vdbias dlycell `.sp` files under `rundata/dscqa/V0/simdir/hspice/zhukaic` and analyze.
- U[2] (main produce-task): add aging sim statements to user's pumpcore files at `/rundata/.../ryanren/pumpcore_sim/tb`, create new folder `pumpcore_sim_aging` mirroring `pumpcore_sim` structure with stress+aging `.sp` for 4 conditions (HTOL/LTOL/RDBI/THB).
- U[3-8]: iterative fixes — `.sp` vs bash script confusion, voltage node renaming, `suffix of PrimeSim stress vector .eage not .eageba` error, `.option radegfile='./finesim.eageba*'` path fix, final fix based on user-edited files.

## Assistant tool chain
list_allowed_files → read_files (zhukaic aging reference: step1_stress/step2_aging/tran_HTOL_*) → read user's pumpcore_sim/tb (00_pvt.sp, 01_stimulus.sp, 02_rerun.sp) → read corner files → read MOSRA model `G5_CIP_Model_D5_v0d9_rev01_relia` → editor: created `setup_pumpcore_aging.py` Python generator → ran it → multiple fix iterations (`fix_steps.py`, `fix_paths.py`, `fix_final.py`) → final output to `/home/ryanren/pumpcore_sim_aging_fixed/tb/`.

## Reference aging structure (zhukaic pattern user asked to follow)
Located at `/rundata/dscqa/V0/simdir/hspice/zhukaic/4_vdbiasref/4_aging_sim/tt_sim/`:
- `tran_HTOL_stress.sp` / `tran_HTOL_aging.sp` (per-condition stress+aging pair)
- `step1_stress.sp` / `step2_aging.sp` (bash submission scripts — NOTE: zhukaic named them `.sp` but they're bash; user U[5] objected and asked for no-extension bash names)
- `tran_nomal.sp` (baseline non-aging tran sim for comparison)

## Two real trace bug-fixes (became check teeth)
1. **`.option radegfile` suffix bug (U[7])**: PrimeSim stress phase outputs file named `aging_<C>_stress.eageba@ra=<time>` (e.g. `eageba@ra=3.6288e+06`), NOT `.eage`. Agent initially wrote `radegfile='./<C>_sim/.../<C>_stress.eage'` → PrimeSim error. Fix: use `.eageba` (absolute path or wildcard `*.eageba*`).
2. **`-o` trailing-slash bug (U[7])**: `primesim -o ./<C>_sim/<C>_stress/` (trailing `/`) made PrimeSim internally concatenate to `././<C>_sim/...` double-path. Fix: drop trailing `/`.

Plus structural fix:
3. **`.sp` vs bash naming (U[5])**: `step1_stress.sp` / `step2_aging.sp` were bash scripts but had `.sp` extension, confusing the user (whose real `.sp` HSPICE files showed green in editor). Fix: rename to `step1_stress` / `step2_aging` (no extension).

## Final deliverable form (trace-faithful)
Python generator that, given (cell name, netlist path, hspiceconfig path, pvt/stimulus templates, MOSRA model path, 4 conditions with temp+voltage table, stress/aging durations, agethreshold), produces in `<out>/<sim_root>/tb/`:
- `aging_setup.sp` (MOSRA model `.LIB` includes)
- `00_pvt.sp` / `01_stimulus.sp` (base templates)
- per-condition `<C>_stress.sp` (simmode=0) + `<C>_aging.sp` (simmode=1, `.option radegfile='...eageba...'`)
- `step1_stress` / `step2_aging` (bash, `bsub primesim -spice ... -o ...` no trailing `/`)
- `run` (overall runner)
- empty sim output dirs `<C>_sim/<C>_stress/` + `<C>_sim/<C>_aging/`

## Reframe (harness-for-teeth)
trace 原意图=写 one-off Python 生成器为 pumpcore 生成 4 条件 aging deck. A 档 trace-faithful (用 ryanren 原话 U[1]/U[2]/U[5]/U[7]/U[8]). 判分有牙需参数化通用 CLI (任意 cell/model/条件/电压/温度), 故 reframe 成 produce 参数化 `pumpcore_aging_deckgen.py --config <json> --out <dir>`; hidden B 异 cell (vdlycore vs pumpcore) + 异 model (v1d0_rev02 vs v0d9_rev01) + 异时长 (2000hr vs 1008hr) + 异电压/温度 (2.1V/150C vs 1.98V/130C) 验通用性与反硬编码 A. 两个 trace bug-fix (radegfile eageba / -o no trailing /) 转为 check 齿 (⑥⑦). 3-seed 确定性 (禁时间戳) 转为 check 齿 (⑫).

## Case artifact map
- assets/EDA-Eval-DesignFlow-PumpcoreAgingDeckGen-001/visible/{config_A.json, 00_pvt.sp, 01_stimulus.sp} — A input
- assets/.../task_brief.md — SUT-visible task spec
- assets/.../hidden/hidden_B/config_B.json — B config (vdlycore/v1d0_rev02/2000hr/2.1V/150C)
- assets/.../hidden/hidden_manifest.json — B manifest
- reference/.../pumpcore_aging_deckgen_ref.py — reference solution
- reference/.../check.py — 12-assertion checker
- reference/.../negative/{neg_empty.py, neg_print.py, neg_core.py} + negative_selftest.py — 3 neg samples

## Self-verify result
NEG_RC=3/3, REF_PASS=True, ALL GOOD (deterministic, anti-hardcode-A enforced).
