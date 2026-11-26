# PHASE2_REPORT.md -- DRC test environment: environment problem analysis

## 1. Python: libpython3.7m.so.1.0 missing

- Symptom: `ImportError: libpython3.7m.so.1.0: cannot open shared object file`
  when the DRC tests start in a non-interactive process.
- Root cause: the non-interactive shell does not source `.bashrc`, so the
  usual Python environment setup (including the library search path) never
  runs.  The python-3.7.1 x86_64 lib directory is not on `LD_LIBRARY_PATH`.
- Fix: test_env.py appends `/apps/local/python/python-3.7.1/x86_64/lib` to
  `LD_LIBRARY_PATH` at import time.

## 2. Calibre VCO autoswitch defect (K10)

### 2.1 Symptom

`calibre -batch` (and calibredrv / rules_syntax_checker) fails with:

    ERROR: VCO aok not supported by autoswitch; no matching tree

The host OS reports `aok` (RHEL 8) but the installed Calibre 2020.1_36 tree
is `aoi`.  The user's interactive terminal works only because `.bashrc` runs
`module load calibre`.

### 2.2 Root cause: shell variable-name resolution bug in calibre_env

Inside calibre_env, the autoswitch test is:

    echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'

Because the variable names are written with a trailing underscore, bash
parses them as the (nonexistent) variables `$SW_WKSTN_` and `$MGC_VCO_`
instead of `$SW_WKSTN` and `$MGC_VCO` followed by a literal `_`.  Those
names are unset, so both expand to the empty string and the echo becomes
`"__"`.  The grep `_ao[j-z]_` therefore never matches, autoswitch is never
enabled, and the code falls through to the error path.

The intended expression would be:

    echo "_${SW_WKSTN}_${MGC_VCO}_" | grep -q '_ao[j-z]_'

which would expand to `_<wkstn>_aok_` and match.  This is an environment /
infrastructure defect in the vendor script, not something fixable inside the
DRC QA application code.

Note: `CALIBRE_SKIP_OS_CHECKS=1` does **not** skip this VCO autoswitch logic.

### 2.3 Regular fix attempted and shown ineffective

The "regular" approach was tried: set `CALIBRE_HOME` to the installed aoi
tree and put `$CALIBRE_HOME/bin` on `PATH` and the aoi shared libs on
`LD_LIBRARY_PATH`.  This **still failed** with the same
`VCO aok not supported by autoswitch; no matching tree` error.

Reason: calibre_env runs `calibre_vco` **unconditionally** -- even when
`CALIBRE_HOME` is already set -- and the buggy autoswitch grep still fires.
So setting CALIBRE_HOME alone is ineffective and cannot be the fix.

Additionally, the box is missing the `libXss.so.1` (X screen-saver)
dependency.

### 2.4 Workaround restored (test-env only)

The accepted workaround, implemented in test_env.py and applied automatically
at module import time:

1. Build a fake `MGC_HOME` at `/tmp/calibre_fake_home` whose
   `bin/calibre_vco` stub script returns `aoi`.  This makes calibre_env's
   autoswitch logic see the installed aoi tree instead of the OS-reported
   `aok`.
2. Create a stub library `/tmp/libXss.so.1` to satisfy the missing X
   dependency.
3. Point `LD_LIBRARY_PATH` at the real aoi library directory
   (`.../aoi_cal_2020.1_36.18/shared/lib`) and at `/tmp` (for the libXss
   stub).
4. Put the fake `bin` directory first on `PATH` so `calibre_vco` resolves to
   the stub.

Because `/tmp` may be cleaned between sessions, the stubs are **auto-rebuilt
at import**: test_env.py checks whether `/tmp/calibre_fake_home` and
`/tmp/libXss.so.1` exist at import time and recreates them if missing, then
re-establishes the environment.

## 3. Conclusion

- Root cause pinned: calibre_env uses `$SW_WKSTN_` / `$MGC_VCO_` (trailing
  underscore) variable names, which bash resolves to empty strings, breaking
  the VCO autoswitch grep.
- Confirmed: the "set CALIBRE_HOME only" regular approach was attempted and
  did not fix the problem because calibre_env unconditionally runs
  calibre_vco.
- Restored workaround: fake MGC_HOME + `calibre_vco` stub returning `aoi` +
  stub `libXss.so.1` + `LD_LIBRARY_PATH` to the real aoi libs, rebuilt at
  import time.
- Impact on smoke results: text checkers and drcSyntax PASS; the 5 pattern QA
  checkers report CAN_START because the tool can now launch and the
  environment is resolved, but the end-to-end QA flow was not completed in
  this sandbox.