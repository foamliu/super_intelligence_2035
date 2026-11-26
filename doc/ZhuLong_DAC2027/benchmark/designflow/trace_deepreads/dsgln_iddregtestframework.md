# Deepread: 1790145190560_dsgln (chengk @ hfeg0plg96, mc=29)

**Source**: summary.tsv scan 20261109_224902, session `/home/chengk/.cline/data/sessions/1790145190560_dsgln/1790145190560_dsgln.messages.json`
**141 messages**, 3 user turns, schematic_netlist domain.

## User intent (msg 0, original):
> 需要构建回归测试用例，参照这三个文件，希望python实现一个通用的测试函数，支持对这三个模块增加测试用例，通过connfig 配置增加测试用例的输入文件地址和输入代码，以及输出位置，以及需要对比的文件位置，python 代码直接写到/home/chengk/work/code/IddFlowCode/test/test_case/

Attached: run_getiddtreemap (0.6KB), run_iddprobe (0.9KB), run_iddrun (1.2KB)

## Three reference shell scripts (the modules to test):

### run_getiddtreemap (getIddTreeMap module):
- Golden: `cd .../getiddtreemap_golden/ && bsub -Is -q fqueue3 getIddTreeMap --railmap railMapAll.pkl`
- Test: `cd .../getiddtreemap_test/`, symlink hier.pkl/instMap.pkl/railMapAll.pkl from golden, run getIddTreeMap (test binary)
- Compare: rail-specific CSV output files (golden vs test)

### run_iddprobe (iddprobe module):
- `module load ds/primesim_reliability/U-2023.03-SP1-1`
- Copy netlist to test/golden dirs
- `bsub -Is -q fqueue2h iddprobe -proj drcoa -version V0 -top AG_VrChgTrig -rundir .`
- Compare `measAvg.file` (golden vs test, gvimdiff)

### run_iddrun (runidd module):
- `module load 2025/primesim/2023.12-SP2-3`
- Symlink netlist dirs, copy simselect_6400.csv
- `bsub -Is -q fqueue2h runidd -P drcoa -V V0 -N Netlists_iddprobe_test_kc -S ./simselect_6400.csv -D`
- Compare hspice.sim output files

## Common test pattern (all 3 modules):
SETUP (ensure dirs, symlink/copy files) → RUN_GOLDEN (reference binary) → RUN_TEST (candidate binary) → COMPARE (output files: CSV / measAvg.file / hspice.sim) → REPORT (pass/fail)

## Assistant behavior (141 msgs):
- msg 1-15: read 3 scripts, existing python_packages (RunIdd.py, getidd.py, genMap.py), idd binaries, run_demo files. Understood the 3-module golden/test/compare pattern.
- msg 16: designed framework — config-driven JSON, generic runner, SETUP→RUN_GOLDEN→RUN_TEST→COMPARE→REPORT. Tried to write `__init__.py` + `test_cases.json` to test_case dir → DENIED (outside writableRoots, only `/home/chengk/.cline/scripts/data` writable).
- msg 23-26: wrote `regression_test.py` to writable root, but editor 6000-char limit forced chunked inserts → file got CORRUPTED (duplicate headers, broken methods, misplaced code from line-number shifts).
- msg 27: user asks "是否已经完成这个任务" → assistant: "还没有完成"
- msg 28-49: kept inserting method chunks (_run_command, _setup_test_case, _run_golden, _compare_results, _compare_file_list, _is_text_file, _compare_text_files, run_single_test, main). Each insert shifted line numbers → corruption compounded.
- msg 50-51: tried `run_approved_command rm` → DENIED (uid mismatch)
- msg 52-109: extensive struggle to fix corrupted file with editor (old_text matching failed due to corruption, insert_line added MORE duplicates). File reached ~1060 lines of scrambled code.
- msg 110: user "继续完成"
- msg 111-140: still trying to fix; inserted clean comparison helpers at line 95, but file still has duplicated old content (lines 200+). Session ends mid-struggle (msg 140 = tool rejection error).

## Key deliverable components (what a correct solution needs):
1. **regression_test.py**: config-driven regression test framework
   - `TestResult` class (test_id, module, status, logs, errors, diffs, timing)
   - `RegressionTestRunner` class:
     - `__init__(config_path)`: load JSON config
     - `_resolve_path(path, tc)`: resolve `{golden_dir}`, `{test_dir}`, `{test_case_dir}` placeholders
     - `_run_command(workdir, command, shell_prefix, env, timeout)`: subprocess with timeout, log capture
     - `_setup(tc, result)`: execute setup actions (ensure_dir, symlink, copy, remove)
     - `_run_golden(tc, result)`: run golden command, log stdout/stderr
     - `_run_test(tc, result)`: run test command, log stdout/stderr
     - `_compare_results(tc, result)`: dispatch by compare type
     - `_compare_dir_diff(tc, result, patterns, ignore, tol)`: glob golden dir, compare each matching file
     - `_compare_file_list(tc, result, files, ignore, tol)`: explicit file pairs
     - `_compare_text_files(g, t, label, ignore, tol)`: line-by-line with regex ignore + numeric tolerance
     - `_is_text_file(path)`: null-byte check
     - `_compare_binary_files(g, t, label)`: filecmp.cmp shallow=False
     - `run_single_test(tc)`: setup→golden→test→compare, set status PASSED/FAILED
     - `run_all()`: iterate enabled test_cases, optional stop_on_failure
     - `_print_summary()`: total/passed/failed/errors counts
     - `save_report(path)`: JSON report
   - `main()`: argparse CLI (--config, --list, --test ID, --stop-on-failure, --verbose, --generate-template)
2. **test_cases.json**: config with settings + test_cases array (3 entries: getIddTreeMap_basic, iddprobe_basic, iddrun_basic)

## Why B-grade synthesized:
- Real paths (`/rundata/drcoa/V0/simdir/finesim/...`) are private, not accessible
- Real EDA binaries (getIddTreeMap, iddprobe, runidd, bsub, FineSim/PrimeSim) not available in judge
- Synthesize A (visible) + B (hidden) with same structure, different module names/paths/compare targets
- check.py tests framework logic with mock commands (no real EDA execution)

## Domain: schematic_netlist (IDD flow netlist/simulation regression testing)
## Level: L2 (Python framework orchestrating EDA simulation commands)
