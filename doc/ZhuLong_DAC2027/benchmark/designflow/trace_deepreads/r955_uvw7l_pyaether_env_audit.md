# r955 deepread — uvw7l pyAether env audit (PyCharm runnability check)

**Session**: 1795056449150_uvw7l.messages.json
**User/Host**: laryu @ hfeg0plg77 (10.129.8.121)
**mc**: 274 (layout_aether, kw: aether:1135/pyaether:539/pdk:31/schematic:24/dbopencv:22/synopsys:13/binary:12/skipper:10)
**Ledger**: C claimed r955 (fresh; not in any of 4 shard ledgers after normalized slug check; 4-shard union)
**Msgs**: 158 total (81 user / 77 assistant), agent=lead, model=deepseek-v4-flash
**Status**: deepread done → synth (1-case target this round)

## Real task (single user msg)

> 我先在写了一段代码，/home/laryu/pycharm/pullPin.py，我想直接在pycharm里面运行，帮我看看环境是否支持

User wrote `pullPin.py` (uses `import pyAether as pyScript`) that opens a schematic cellview via `dbOpenCVByType` and dumps pin/net info (instName/innerPinName/outerPinName). They want to run it directly in PyCharm and ask whether the env supports it.

## Assistant work chain (env-config probe)

1. read `/home/laryu/pycharm/pullPin.py` — confirmed `import pyAether`
2. `run_approved_command` profile=shell-runner with several `.sh` probes:
   - `which python3` → `/usr/bin/python3` 3.6.8 — **cannot `import pyAether`** (no module)
   - try SandBox_MCP_Server__run_code → connection refused (remote pyAether sandbox not running)
   - narrow `find` for pyAether under /apps/imctf, /apps/empyrean — found Aether install at `/apps/empyrean`
3. Inspect Aether launcher + settings:
   - `aether_bak.rc` / `aether_bak.ini` — Aether config (PANDA_HOME/data/aether.ini, Py Script bindkey.py)
   - `aether_py3.9_2024.09.tmp12_linux-x86_64_rhel6_20240831/` — Aether-bundled Python 3.9 package
4. Find env vars already loaded in current shell (login shell sourced aether env):
   - `AETHER_ROOT=/apps/empyrean/tools/aether_new`
   - `AETHER_HOME=/apps/empyrean/tools/aether_new/tools/aether`
   - `PYAETHER_HOME=/apps/empyrean/tools/aether_new/tools/pyaether`
   - `PYAE_VER=3.9`, `PYPLATFORM=linux26-x86_64`, `PYAETHER_PYTHONPATH=1`
5. Map pyAether module location: `aether_new/tools/pyaether/3.9/linux26-x86_64/lib/pyAether/` (has __init__.py, setup.py, pyaecb.py, _pyaecb.so, libpyaeutil.so)
6. Map bundled python3.9: `aether_py3.9_.../tools/python/3.9/linux26-x86_64/bin/python` (Python 3.9.0)
7. Map platform libs:
   - Aether platform: `aether_new/tools/aether/platform/linux26-x86_64/lib` (libemy2netlist.so, libemyVCell.so)
   - Third-party boost: `aether_py3.9_.../tools/platform/linux26-x86_64/lib` (libboost_*.so)
8. Repeatedly try to manually assemble LD_LIBRARY_PATH + PYTHONPATH and `import pyAether` — keeps hitting missing .so chain (libpyaeutil.so, libboost_*.so, libemyVCell.so, libpyaeutil.so, …) → conclude manual config fragile
9. Inspect `pythone` launcher content — conclude **pythone is Aether's official Python launcher** that auto-injects env+LD at runtime (PYAETHER_PYTHONPATH=1 hints runtime injection)
10. Final answer: **Yes, can run in PyCharm** — must configure PyCharm interpreter to Aether's bundled Python 3.9 (not system 3.6.8) OR use pythone launcher; set env vars (AETHER_ROOT, PYAETHER_HOME, PYAE_VER, PYPLATFORM); LD_LIBRARY_PATH auto-handled by pythone.

## Key artifacts (for fixture)

- `pullPin.py` header: `import pyAether as pyScript`, `dbOpenCVByType(lib, cell, view, mode="r")`, iter terminals→pins
- Aether layout: aether_root symlink → versioned py3.9 package; pyaether lib has __init__.py + _pyaecb.so + libpyaeutil.so
- Required env vars: AETHER_ROOT, PYAETHER_HOME, PYAE_VER, PYPLATFORM (+ PYAETHER_PYTHONPATH=1 marker)
- LD lib dirs (3): aether platform lib, pyaether pylib dir, third-party boost lib
- pythone launcher = official entrypoint that auto-resolves env+LD
- Verdict tree: sys_py_ok? → supported_direct ; else bundled_py39_ok + pythone_ok + env_ok? → supported_via_pythone ; else bundled_py39_ok + env_ok + ld_ok → supported_via_manual_config ; else → unsupported_missing_*

## Cross-shard / duplicate check

- 4-shard ledger: uvw7l only C (fresh, now claimed r955)
- 4-shard jsonl: no uvw9l/uvw7l trace_source
- Same domain (layout_aether) existing cases (GtJumperPathAnalyzer / StdcellLibFifoSuitClassifier / VirtuosoDaemonReviewFix / AetherLayerPurpose / GdsLayoutDirCleanupAnalyzer / etc.) — all orthogonal:
  - those cases are layout/schematic/runtime ops via pyAether API; THIS case is **environment-config audit** (does the install layout support running a pyAether script in a non-Aether-shell IDE?)
- Sub-type `pyaether_env_runnability_audit` — **first case** of this kind (env-config / install-layout verdict)

## Synth direction (reframe 档 B, offline pure-stdlib)

**Sub-type**: `pyaether_env_runnability_audit` (first case)
**Agent writes**: `pyaether_env_audit.py` (pure stdlib) reads a JSON layout manifest describing a hypothetical Aether install + system Python + bundled Python + pyAether module + env vars + LD lib dirs + pythone launcher; emits a structured audit JSON with verdict + reason + recommendations.

**Verdict decision tree** (oracle):
```
sys_py_ok = (sys_py.version >= "3.9.0") AND sys_py.pyaether_importable
bundled_py39_ok = bundled.exists AND bundled.version >= "3.9.0"
pyaether_ok = pyaether.exists AND has {__init__.py, _pyaecb.so, libpyaeutil.so}
env_ok = required_env_vars ⊆ env_vars present
ld_ok = required_ld_lib_dirs all exist
pythone_ok = pythone launcher exists

if not pyaether_ok: verdict = "unsupported_missing_pyaether"
elif sys_py_ok AND env_ok AND ld_ok: verdict = "supported_direct"
elif sys_py_ok AND env_ok AND not ld_ok: verdict = "unsupported_missing_ld"
elif sys_py_ok AND not env_ok: verdict = "unsupported_missing_env"
elif not bundled_py39_ok: verdict = "unsupported_missing_python39"
elif pythone_ok AND env_ok: verdict = "supported_via_pythone"
elif pythone_ok AND not env_ok: verdict = "unsupported_missing_env"
elif env_ok AND ld_ok: verdict = "supported_via_manual_config"
elif not env_ok: verdict = "unsupported_missing_env"
else: verdict = "unsupported_missing_ld"
```

**Visible env_A (laryu-style)**:
- design=`laryu_pycharm_pyaether_probe`, user_script=`pullPin.py`
- system_python: /usr/bin/python3, version=3.6.8, pyaether_importable=false → sys_py_ok=false
- aether_root: /apps/empyrean/tools/aether_new (symlink → aether_py3.9_2024.09.tmp12_..._20240831)
- bundled_python39: aether_py3.9_.../tools/python/3.9/linux26-x86_64/bin/python, version=3.9.0, exists=true
- pyaether_module: aether_new/tools/pyaether/3.9/linux26-x86_64/lib/pyAether, contents=[__init__.py,setup.py,pyaecb.py,_pyaecb.so,libpyaeutil.so] → complete=true
- pythone: aether_new/bin/pythone, exists=true
- env_vars: {AETHER_ROOT,PYAETHER_HOME,PYAE_VER=3.9,PYPLATFORM=linux26-x86_64,PYAETHER_PYTHONPATH=1} — all 4 required set
- ld_lib_dirs (3): all present
- Expected verdict: **supported_via_pythone** (sys_py not ok, bundled ok, pythone ok, env ok)

**Hidden env_B (inline in check.py, structurally different)**:
- design=`fangjie_pycharm_pyaether_check`, user_script=`netlist_dump.py`
- system_python: /usr/local/bin/python3, version=3.9.5, pyaether_importable=true (PYTHONPATH includes pyaether lib) → sys_py_ok=true
- aether_root: /opt/empyrean/aether_pro (NOT symlink — direct dir)
- bundled_python39: /opt/empyrean/aether_pro/tools/python/3.9/bin/python3.9, version=3.9.7, exists=true
- pyaether_module: /opt/empyrean/aether_pro/tools/pyaether/3.9/lib/pyAether, contents=[__init__.py,setup.py,pyaecb.py,_pyaecb.so,libpyaeutil.so] → complete=true
- pythone: /opt/empyrean/aether_pro/bin/pythone, **exists=false** (no launcher shipped)
- env_vars: {AETHER_ROOT,PYAETHER_HOME,PYAE_VER=3.9,PYPLATFORM=linux26-x86_64} — all 4 set
- ld_lib_dirs (3): all present
- Expected verdict: **supported_direct** (sys_py ok + env ok + ld ok, pythone absent doesn't matter)

A/B differ in: design/user_script names, system python version + import flag, aether_root path + symlink-ness, bundled python path/version, pyaether module path, pythone exists, env var values. Same decision-tree rules → different verdict path.

**check.py ≥8 assertions (k=12)**:
① py_compile agent script (no syntax error)
② no-arg run: exit 0 + stdout valid JSON + 4 top-level keys (audit, verdict, verdict_reason, recommendations, summary)
③ anti-hardcode: env_A names (laryu, /apps/empyrean, pullPin.py) NOT in env_B output; env_B names (fangjie, /opt/empyrean, netlist_dump.py) ALL present
④ audit.system_python_version matches env_B manifest
⑤ audit.system_python_supports_pyaether correct (sys_py_ok computed)
⑥ audit.bundled_python39_exists + version correct
⑦ audit.aether_root + aether_root_is_symlink + aether_root_resolved correct (env_B is NOT symlink → resolved == self)
⑧ audit.pyaether_module_complete correct (init + _pyaecb.so + libpyaeutil.so present)
⑨ audit.pythone_launcher_exists correct (env_B: false)
⑩ audit.env_vars_missing correct (env_B: empty)
⑪ audit.ld_lib_dirs_missing correct (env_B: empty)
⑫ verdict code matches oracle's independent decision-tree re-computation (env_B → "supported_direct")
⑬ verdict_reason non-empty + mentions key fact
⑭ recommendations list non-empty + each is actionable string
⑮ summary.verdict_code == verdict, summary fields (system_python_ok/bundled_python_ok/pyaether_module_ok/env_vars_ok/ld_libs_ok/pythone_ok) all correct booleans, issues_count == 0
⑯ anti-delete-core: agent script with main audit logic stripped (always emits supported_via_pythone) → FAIL because env_B expects supported_direct
⑰ 3-seed PYTHONHASHSEED=1/2/3 byte-identical stdout (deterministic)

**Negative samples**:
- `naive_stub.py` → emits `{"verdict":"supported_via_pythone",...}` hardcoded → FAIL (env_B expects supported_direct, fails ⑫)
- `hardcode_enva.py` → emits env_A paths/names hardcoded in audit → FAIL (env_A names leak → ③; env_B expected values mismatch → ⑦⑨)
- `always_unsupported.py` → always emits `verdict: unsupported_missing_pyaether` → FAIL on env_A (verdict wrong, fails ⑫ in reverse-check on env_A) — actually for env_B it also fails ⑫
- For the selftest, run check on env_A AND env_B with each negative; all must FAIL at least one assertion.

**test_rationale (k=17)**: 17 条断言：①py_compile ②no-arg exit0+JSON+5顶层键 ③反硬编码 env-A 名零泄漏+env-B 名全现 ④audit.system_python_version ⑤audit.system_python_supports_pyaether ⑥audit.bundled_python39_exists+version ⑦audit.aether_root+is_symlink+resolved ⑧audit.pyaether_module_complete ⑨audit.pythone_launcher_exists ⑩audit.env_vars_missing ⑪audit.ld_lib_dirs_missing ⑫verdict 与 oracle 决策树一致 ⑬verdict_reason 非空且含关键事实 ⑭recommendations 非空且每条为可执行字符串 ⑮summary.verdict_code 一致 + 6 bool 字段正确 + issues_count 正确 ⑯反 delete-core:删核心后 verdict 永远 supported_via_pythone → env_B 期望 supported_direct 失败 ⑰3-seed PYTHONHASHSEED=1/2/3 字节级一致
