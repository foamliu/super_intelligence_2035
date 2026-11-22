# deepread: ce72v — finesim SRAM-char pigz resolution debug → PigzResolverProduce-001

**session**: `1794799663514_ce72v.messages.json` (e0044979 @ hfeg0pkn034, mc27, characterization)
**scan**: `ssh_eda_search_20261121_151844/summary.tsv` (spice-dom: sp25, virt20, sch3)
**nmsg**: 95 (944KB), 2 sub-tasks

## Real user intent (verbatim)

- U0: "I got error from this python script to find pigz executable file:
  `/rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0044979/Python/VOP_full_20261115/backend/dspf/storage.py`.
  The run script is at: `.../SRAM_tailor/CXN4HC2PS1024X72_8Tbitcell_NOpower_202610/` …"
- U1 (after pigz resolved): "now pigz issue solved. I got the error for tailor_plan
  and the log file is at: `.../shm_version1/.../tailor_plan_..._FS.log` check the reason"

This is a **debug-Q&A** session in a finesim SRAM-characterization DSPF flow. The
case takes **sub-task 1** (pigz resolution), which is portable / structurally
checkable. Sub-task 2 (tailor_plan log diagnosis) is pure log-reading Q&A, not
portable → not used.

## Agent's diagnosis (msgs 23-64)

- Real `storage.py` lives at `dspf-tool/backend/dspf/storage.py` (user's path
  missed the `dspf-tool` component; no top-level `backend` exists).
- `Pigz.__init__` (lines 118-121): `default = os.environ.get("DSPF_PIGZ") or
  ("pigz" if os.name=="nt" else "/bin/pigz"); self.executable = executable or
  default`. Launched via `subprocess.Popen` in `_run()`; `FileNotFoundError`
  caught at 154-159 → `StorageError: pigz executable not found: <path>`.
- Run script `tools/run_two_stage_test.sh` line 40 sets
  `DSPF_PIGZ=/apps/rscalc/lvplus-13.0.1/bin/pigz` but never `export`s it →
  Python sees `DSPF_PIGZ=None` → falls back to hard-coded `/bin/pigz`.
- On the failing node `/bin/pigz` was absent → `pigz executable not found:
  /bin/pigz`.
- `/apps/rscalc/lvplus-13.0.1/bin/pigz` is a **relative symlink** →
  `../module/linux-x86_64/bin/pigz`; on some nodes the target is missing
  (dangling) → even exporting `DSPF_PIGZ` would fail there.
- Agent could not patch `/rundata` (policy writableRoots = `/home/e0044979`
  only); delivered a diagnosis + a `export DSPF_PIGZ=...` workaround + a
  proposed hardening of `Pigz` to discover a working pigz across several known
  locations.

## Reframe → EDA-Eval-DesignFlow-PigzResolverProduce-001 (produce, L1, pure Python)

The user's underlying need = a working pigz resolution that doesn't hard-fail.
The hardened resolver `storage.py` should use is the deliverable.

**Form**: `pigz_resolver.py --env <env.json> --candidates-dir <dir> [--report <path>]`
- env.json: `{DSPF_PIGZ, PATH, fallbacks}` (paths relative to candidates-dir)
- Resolution order: DSPF_PIGZ → PATH dirs (`<dir>/pigz`) → fallbacks
- Validate each: `os.path.realpath` (follow symlinks), reject dangling symlinks
  (`os.path.exists` False for dangling), require regular file + `os.access(X_OK)`
- First valid wins; source tags `env:DSPF_PIGZ` / `path:<dir>` / `fallback:<path>`
- Report: `{resolved_path, source, checked:[{candidate,source,realpath,exists,executable,valid}], error}`

**A** (assets/PigzResolverProduce-001/dir_A): env_A (DSPF_PIGZ=valid relative
symlink → module/.../pigz, executable) → env wins. fs_manifest_A (symlink chain
+ 2 exec scripts). spec_A (expected_source=env:DSPF_PIGZ). README + prompt.
**hidden B** (hidden/dir_B): env_B (DSPF_PIGZ=dangling symlink → REJECTED),
PATH=good/bin:noexec/bin (good/bin/pigz valid exec → WINS, source=path:good/bin),
fallbacks=[fallback/pigz_real, missing/pigz, sym_good(valid symlink)]. fs_manifest_B
(dangling symlink + exec + non-exec + valid symlink + missing). spec_B.
Five-way anti-hardcode vs A (env path, PATH dirs, fallback names, winner, source
all differ).

**check.py 12 条 (a-l, k_check=k_rationale=12)**:
①(a)zip+py_compile+size>200 ②(b)B exit0+report.json ③(c)4 顶层键恰好
④(d)resolved_path==good/bin/pigz ⑤(e)source==path:good/bin
⑥(f)dangling/dspf_pigz valid==false ⑦(g)noexec/bin/pigz valid==false
⑧(h)sym_good valid==true+realpath ⑨(i)missing/pigz valid==false+exists==false
⑩(j)error==null ⑪(k)anti-hardcode A 缺席+B 在场 ⑫(l)3-seed 确定性.
**核心齿**: ⑥dangling 拒绝(反 naive 接受所有)+ ④PATH 胜者(反硬编码 A 的 env 胜者)
+ ⑧valid symlink 接受(反 naive 拒所有 symlink)+ ⑪anti-hardcode.

**3 negs**: neg_empty(空→a size0) / neg_print_only(硬编码 A 报告→d+e+k A 泄漏)
/ neg_core_removed(验证 stub 全 valid=True→d 选 dangling 胜者). §4.9 三假全 FAIL ✓.

**自验**: ref pigz_resolver_ref.py → check.py PASS 12/12 ✓;
negative_selftest 3/3 FAIL-as-expected ✓; 3-seed 确定性 ✓.

**distinct**: vs QuadClkSkewMeasDeckGen(HSPICE .measure deck)/BatchFinesimRunner
(bsub 批量提交)/FinesimTbCodebaseAudit(Python 代码库审计)/ZqSimRunner(单 deck)
— 本 case=pigz 可执行文件 robust 解析器(env/PATH/fallback + 符号链接验证),
无重复 ✓.

## Trace provenance
- user: e0044979 (real, unmasked)
- host: hfeg0pkn034 (10.129.41.48)
- session: 1794799663514_ce72v.messages.json (nested path confirmed: `<slug>/<slug>.messages.json` AND flat both exist)
- match_count: 27 (spice keywords hspice/spectre/finesim incidental; characterization context = finesim SRAM DSPF flow)
- real_task_summary: pigz executable resolution debug in finesim SRAM-char DSPF flow
