#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-PDKQA-001 (proper design_flow case).
Source: trace_deepreads/x4b0p_pdkqa_drc_calibre_vco.md (PDK QA DRC migration,
Calibre VCO aok/aoi autoswitch bug; naive "only CALIBRE_HOME" FAILS, hacky
fake-MGC_HOME + stub-libXss + auto-rebuild PASSES).

Produces:
  assets/EDA-Eval-DesignFlow-PDKQA-001/<files>
  reference/EDA-Eval-DesignFlow-PDKQA-001/<reference_submit.zip + check.py + assets>
  appends 1 line to EDA-Eval-DesignFlow.jsonl
  proves teeth: CORRECT PASS / BUGGY FAIL / 7 per-condition isolated FAIL
"""
import json, os, re, shutil, zipfile, sys

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = os.path.join(ROOT, "assets", "EDA-Eval-DesignFlow-PDKQA-001")
REF_DIR   = os.path.join(ROOT, "reference", "EDA-Eval-DesignFlow-PDKQA-001")
JSONL     = os.path.join(ROOT, "EDA-Eval-DesignFlow.jsonl")
TID       = "EDA-Eval-DesignFlow-PDKQA-001"

SUPPORT_FUNCNAMES = [
    "ldr", "drcSyntax", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
    "emptyDeriveLayer", "drcWithPattern",
    "patternLayerVsDesignRuleLayerChange", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]
TEXT_CHECKERS = [
    "ldr", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]
PATTERN_CHECKERS_CANSTART = [
    "emptyDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
    "patternLayerVsDesignRuleLayerChange", "drcWithPattern",
]
DRCSYNTAX = "drcSyntax"

# ----------------------------------------------------------------------------
# 1. ASSET FILES
# ----------------------------------------------------------------------------

DRCQA_PY = '''# DrcQa.py -- PDK QA System, DRC entry point.
# Migrated Windows->Linux. 17 registered checkers (supportFuncnames).
# DO NOT modify supportFuncnames (user requirement: problems recorded, not fixed).
import os, sys, importlib

SUPPORT_FUNCNAMES = [
    "ldr", "drcSyntax", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
    "emptyDeriveLayer", "drcWithPattern",
    "patternLayerVsDesignRuleLayerChange", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]

# dead code (NOT registered, keep as-is): drcRuleContainsDeriveLayer

# Checker category map (text = no Calibre run; pattern = needs calibre/calibredrv)
TEXT_CHECKERS = [
    "ldr", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]
PATTERN_CHECKERS = [
    "drcSyntax", "emptyDeriveLayer", "patternDeviceLayer",
    "patternLayerVsFracture", "patternLayerVsDesignRuleLayerChange",
    "drcWithPattern",
]


class DrcQa:
    """Main DRC QA driver. Dispatches to per-checker modules in DRC/text/ and
    DRC/pattern/."""

    def __init__(self, case_dir, deck="calibre"):
        self.case_dir = case_dir
        self.deck = deck  # "calibre" or "svrf"
        self.results = {}

    def run(self, names=None):
        names = names or SUPPORT_FUNCNAMES
        for fn in names:
            if fn in TEXT_CHECKERS:
                self.results[fn] = self._run_text(fn)
            elif fn in PATTERN_CHECKERS:
                self.results[fn] = self._run_pattern(fn)
            else:
                self.results[fn] = {"status": "unknown", "reason": "not registered"}
        return self.results

    def _run_text(self, name):
        mod = importlib.import_module("DRC.text." + name)
        return mod.check(self.case_dir, self.deck)

    def _run_pattern(self, name):
        # needs calibre / calibredrv; environment must be set up first
        import test_env
        ok, msg = test_env.check_calibre_env()
        if not ok:
            return {"status": "SKIP", "reason": msg}
        mod = importlib.import_module("DRC.pattern." + name)
        return mod.check(self.case_dir, self.deck)


if __name__ == "__main__":
    print("registered:", len(SUPPORT_FUNCNAMES))
'''

CALIBRE_ENV_EXCERPT = '''# calibre_env_excerpt.sh -- excerpt of Calibre 2020.1_36 calibre_env script.
# Shows the VCO autoswitch logic that fails on RHEL 8 (VCO=aok) when run as a
# non-interactive process (no .bashrc -> no module load -> CALIBRE_HOME unset).
#
# Bug: the grep below uses shell variable names that bash parses as
#   $SW_WKSTN_  and  $MGC_VCO_   (names WITH trailing underscore -> empty)
# instead of   $SW_WKSTN + "_"  and  $MGC_VCO + "_".
# So the grep almost never matches -> autoswitch not enabled -> aok tree not
# found -> error.  CALIBRE_SKIP_OS_CHECKS=1 does NOT skip this.

MGC_VCO_REAL=aok            # OS reports aok (RHEL 8)
INSTALLED_TREE=aoi          # installed Calibre tree is aoi

# --- calibre_env (excerpt) ---
# unconditional VCO detection (runs even if CALIBRE_HOME is set):
MGC_VCO=$(/opt/mentor/bin/calibre_vco)        # returns 'aok'

# autoswitch grep (BUGGY):
echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'
# bash sees  $SW_WKSTN_  (empty) and  $MGC_VCO_  (empty)  ->  echo "__"  -> no match
# intended:  echo "_${SW_WKSTN}_${MGC_VCO}_"  ->  echo "_<wkstn>_aok_"  -> match

if [ $? -ne 0 ]; then
    echo "ERROR: VCO $MGC_VCO not supported by autoswitch; no matching tree" >&2
    exit 1
fi
'''

ENV_SYMPTOMS = '''# env_symptoms.txt -- observed environment failures when running DRC QA tests
# as a non-interactive process on hfeg0pkn004 (RHEL 8).

[1] Python:
    $ python3 DRC/tests/run_all_tests.py
    ImportError: libpython3.7m.so.1.0: cannot open shared object file: No such file
    -> python-3.7.1 x86_64 lib not on LD_LIBRARY_PATH for non-interactive shells.

[2] Calibre VCO:
    $ calibre -batch
    ERROR: VCO aok not supported by autoswitch; no matching tree
    -> machine OS=RHEL8 -> calibre_vco returns 'aok', but installed tree is 'aoi'.

[3] Non-interactive shell:
    $ ssh host "calibre -batch"
    (same VCO error)  -- but the user's interactive terminal runs calibre fine.
    Reason: non-interactive process does NOT source .bashrc -> no `module load
    calibre` -> CALIBRE_HOME unset -> calibre_env runs calibre_vco -> autoswitch
    bug triggers.

[4] "Regular" fix attempted (set CALIBRE_HOME only):
    CALIBRE_HOME=/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18
    PATH=$CALIBRE_HOME/bin:$PATH  LD_LIBRARY_PATH=$CALIBRE_HOME/shared/lib:...
    $ calibre -batch
    ERROR: VCO aok not supported by autoswitch; no matching tree
    -> SETTING CALIBRE_HOME ALONE DOES NOT HELP: calibre_env UNCONDITIONALLY
       runs calibre_vco and the autoswitch grep bug still fires.
    -> Also missing: libXss.so.1 (X scrnSaver) dependency not on the box.

[5] Conclusion:
    The autoswitch bug is in calibre_env (shell variable name resolution), an
    environment/infrastructure defect, NOT application-fixable.  A test-env
    workaround is required: fake MGC_HOME whose bin/calibre_vco returns 'aoi'
    (so calibre_env's autoswitch sees the installed tree) + a stub libXss.so.1
    + LD_LIBRARY_PATH pointing at the real aoi libs.  The workaround must
    auto-rebuild at import (the /tmp stubs may be cleaned).
'''

KNOWN_ISSUES = '''# known_issues.md -- PDK QA migration, known issues

## K10: Calibre 2020.1_36 VCO autoswitch bug on RHEL 8
- Symptom: calibre/calibredrv/rules_syntax_checker fail with
  "VCO aok not supported by autoswitch" in non-interactive processes.
- Root cause: calibre_env script grep
    echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'
  uses shell variable names with a trailing underscore (parsed as empty),
  so autoswitch never matches the aok tree.
- Setting CALIBRE_HOME alone does NOT fix it (calibre_env runs calibre_vco
  unconditionally).
- Workaround (test-env only): fake MGC_HOME + bin/calibre_vco stub returning
  'aoi' + stub libXss.so.1 + LD_LIBRARY_PATH to real aoi libs; auto-rebuild
  at import.  Classified as environment infrastructure bug, not project
  responsibility.
- (placeholder -- detail to be filled in PHASE2_REPORT.md)
'''

RUN_ALL_TESTS = '''# run_all_tests.py -- smoke-test runner for the 17 registered DRC checkers.
import os, sys, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
import test_env

import DrcQa
from DrcQa import SUPPORT_FUNCNAMES, TEXT_CHECKERS, PATTERN_CHECKERS


def main():
    case_dir = os.environ.get("CASE_DIR", os.path.join(os.getcwd(), "shared", "0806_zhaowei"))
    qa = DrcQa.DrcQa(case_dir, deck="calibre")
    results = qa.run()
    lines = []
    for name in SUPPORT_FUNCNAMES:
        r = results.get(name, {})
        status = r.get("status", "?")
        lines.append(f"- {name}: {status}")
    report = "# DRC QA smoke report\\n\\n" + "\\n".join(lines) + "\\n"
    with open("smoke_report.md", "w") as f:
        f.write(report)
    print(report)


if __name__ == "__main__":
    main()
'''

def _run_test_skeleton(name):
    return f'''# tests/{name}/run_test.py -- smoke test skeleton for checker '{name}'.
import os, sys, importlib, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
import test_env
import DrcQa

def run():
    case_dir = os.environ.get("CASE_DIR", os.getcwd())
    qa = DrcQa.DrcQa(case_dir, deck="calibre")
    try:
        r = qa.run(["{name}"])
        print("[{0}] {{}}".format(r.get("{name}", {{}}).get("status", "?")))
    except Exception as e:
        traceback.print_exc()

if __name__ == "__main__":
    run()
'''

# ----------------------------------------------------------------------------
# 2. CORRECT reference solution
# ----------------------------------------------------------------------------

CORRECT_TEST_ENV = '''# test_env.py -- Shared test environment setup for DRC QA tests.
# Replicates .bashrc + `module load calibre` for non-interactive processes.
# Infrastructure note: Calibre 2020.1_36's calibre_env has a shell variable-name
# resolution bug on RHEL 8 (VCO=aok). The workaround below (fake MGC_HOME with a
# bin/calibre_vco stub returning 'aoi' + a stub libXss.so.1, auto-rebuilt at
# import) is a test-environment adaptation, NOT a source-code fix.
import os, sys

_REAL_CALIBRE = "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18"
_PY_LIB = "/apps/local/python/python-3.7.1/x86_64/lib"

# 1. Python: fix libpython3.7m.so.1.0 not found
if _PY_LIB not in os.environ.get("LD_LIBRARY_PATH", ""):
    os.environ["LD_LIBRARY_PATH"] = _PY_LIB + ":" + os.environ.get("LD_LIBRARY_PATH", "")

_LIB_PATHS = [
    _REAL_CALIBRE + "/pkgs/mgls.aoi/lib",
    _REAL_CALIBRE + "/shared/lib",
    os.path.join(os.path.dirname(os.path.realpath(__file__)), "lib"),
    "/tmp",
]

_FAKE_HOME = "/tmp/calibre_fake_home"
_LIBXSS = "/tmp/libXss.so.1"


def _setup_calibre_env():
    """Calibre VCO bypass: fake MGC_HOME whose bin/calibre_vco returns 'aoi',
    plus a stub libXss.so.1. Auto-rebuild at import if the stubs are missing."""
    # auto-rebuild: check both stubs exist, rebuild if either is missing
    need_rebuild = (not os.path.isdir(_FAKE_HOME)) or (not os.path.exists(_LIBXSS))
    if need_rebuild:
        os.makedirs(os.path.join(_FAKE_HOME, "bin"), exist_ok=True)
        vco = os.path.join(_FAKE_HOME, "bin", "calibre_vco")
        with open(vco, "w") as f:
            f.write("#!/bin/sh\\necho aoi\\n")
        os.chmod(vco, 0o755)
        with open(_LIBXSS, "w") as f:
            f.write("")  # stub shared object
    os.environ["MGC_HOME"] = _FAKE_HOME
    os.environ["CALIBRE_HOME"] = _REAL_CALIBRE
    for lp in _LIB_PATHS:
        if lp not in os.environ.get("LD_LIBRARY_PATH", ""):
            os.environ["LD_LIBRARY_PATH"] = lp + ":" + os.environ.get("LD_LIBRARY_PATH", "")


def check_calibre_env():
    """Returns (ok, msg). Sets up the VCO bypass first."""
    _setup_calibre_env()
    ok = os.path.isdir(_FAKE_HOME) and os.path.exists(_LIBXSS)
    return (ok, "VCO bypass active" if ok else "VCO bypass missing")


def get_real_path(case, fname):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "shared", case, fname)


def chdir_to_data_dir(path):
    """Linux DrcInfo.readDrc() uses CWD to resolve INCLUDE relative paths."""
    os.chdir(path)


def print_result(name, ok, msg):
    print("[{}] {} {}".format(name, "PASS" if ok else "FAIL", msg))


# auto-rebuild at import
_setup_calibre_env()
'''

CORRECT_SMOKE_REPORT = '''# DRC QA smoke report

17 registered checkers (supportFuncnames), run on case 0806_zhaowei (deck=calibre).

## text checkers (no Calibre run) -- 11 PASS
- ldr: PASS
- drcLayerMap: PASS
- drcValue: PASS
- drcOption: PASS
- drcPowerList: PASS
- drcDeriveLayerVsFracture: PASS
- drcDeriveLayerVsFractureAndTruthOverall: PASS
- uselessDeriveLayer: PASS
- drcConsistencyWithChangedLdr: PASS
- drcCountWithinOption: PASS
- antMetalThk: PASS

## pattern QA checkers (need Calibre) -- VCO bypass active
- drcSyntax: PASS  (rules_syntax_checker 8s, completed, status=False on test data -- syntax check ran)
- emptyDeriveLayer: CAN_START  (calibredrv started then killed+cleaned; VCO resolved)
- patternDeviceLayer: CAN_START
- patternLayerVsFracture: CAN_START
- patternLayerVsDesignRuleLayerChange: CAN_START
- drcWithPattern: CAN_START

## summary
- text PASS: 11
- drcSyntax PASS: 1
- pattern CAN_START (VCO bypass resolved, no full run in smoke): 5
- FAIL/SKIP (env-not-resolved): 0
'''

CORRECT_PHASE2_REPORT = '''# PHASE2_REPORT.md -- DRC QA test-environment establishment

## 1. Environment problems solved

### 1.1 Python libpython3.7m.so.1.0 missing
Non-interactive shells do not load .bashrc, so the python-3.7.1 lib path is not
on LD_LIBRARY_PATH.  Fixed in test_env.py by prepending
/apps/local/python/python-3.7.1/x86_64/lib to LD_LIBRARY_PATH.

### 1.2 Calibre VCO aok/aoi autoswitch failure
- Machine OS = RHEL 8 -> calibre_vco returns 'aok'.
- Installed Calibre 2020.1_36 tree = 'aoi'.
- calibre_env runs calibre_vco UNCONDITIONALLY and then an autoswitch grep:
      echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'
  BUG: bash parses `$SW_WKSTN_` and `$MGC_VCO_` as variable names WITH a
  trailing underscore (both empty), instead of `$SW_WKSTN` + "_" and
  `$MGC_VCO` + "_".  The echo therefore emits "__" and the grep never matches,
  so autoswitch is not enabled and the aok tree is not found -> error exit.
  CALIBRE_SKIP_OS_CHECKS=1 does NOT skip this.

### 1.3 "Regular" approach (set CALIBRE_HOME only) -- TRIED AND FAILED
Following the architecture team's suggestion, test_env.py was changed to set
only CALIBRE_HOME + PATH + LD_LIBRARY_PATH (no fake home).  Re-tested:
calibre -batch STILL fails with the same VCO error, because calibre_env runs
calibre_vco unconditionally regardless of CALIBRE_HOME.  Confirmed this is an
environment/infrastructure bug in calibre_env, NOT application-fixable.

### 1.4 Workaround (restored) -- fake MGC_HOME + stub libXss
test_env.py now builds a fake MGC_HOME at /tmp/calibre_fake_home with
bin/calibre_vco returning 'aoi' (so calibre_env's autoswitch sees the aoi
tree) + a stub libXss.so.1 (missing X scrnSaver dep) + LD_LIBRARY_PATH to the
real aoi libs.  The stubs auto-rebuild at import if /tmp has been cleaned.
Classified as environment infrastructure bug (known_issues.md K10), not
project responsibility.

## 2. Smoke results
- 11 text checkers: PASS
- drcSyntax: PASS (rules_syntax_checker completed)
- 5 pattern QA: CAN_START (calibre/calibredrv started then killed+cleaned;
  VCO bypass resolved the startup, full run deferred)

## 3. Key findings for architecture review
- INCLUDE relative paths: DrcInfo.readDrc() uses CWD -> tests must chdir to the
  data dir first (test_env.chdir_to_data_dir).
- drcValue on real data: 30-60s (1663 LDR lines vs 2647 DRC rules).
- drcCountWithinOption: returns 'notCheck' when no multi-sheet/option.
- EdrInfo.py `import attr` is dead code (uses stdlib dataclasses); removing it
  would drop the attrs dependency and let antMetalThk run, but per user
  requirement source code is NOT modified -- recorded only.
'''

# ----------------------------------------------------------------------------
# 3. BUGGY solution (naive "regular approach": only CALIBRE_HOME) -- must FAIL
# ----------------------------------------------------------------------------

BUGGY_TEST_ENV = '''# test_env.py -- regular approach: set CALIBRE_HOME only (per architecture team)
import os, sys

_REAL_CALIBRE = "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18"
_PY_LIB = "/apps/local/python/python-3.7.1/x86_64/lib"

if _PY_LIB not in os.environ.get("LD_LIBRARY_PATH", ""):
    os.environ["LD_LIBRARY_PATH"] = _PY_LIB + ":" + os.environ.get("LD_LIBRARY_PATH", "")

os.environ["CALIBRE_HOME"] = _REAL_CALIBRE
os.environ["PATH"] = _REAL_CALIBRE + "/bin:" + os.environ.get("PATH", "")
os.environ["LD_LIBRARY_PATH"] = (_REAL_CALIBRE + "/shared/lib:" +
                                 os.environ.get("LD_LIBRARY_PATH", ""))


def check_calibre_env():
    return (True, "CALIBRE_HOME set")


def get_real_path(case, fname):
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "shared", case, fname)


def chdir_to_data_dir(path):
    os.chdir(path)


def print_result(name, ok, msg):
    print("[{}] {} {}".format(name, "PASS" if ok else "FAIL", msg))
'''

BUGGY_SMOKE_REPORT = '''# DRC QA smoke report

All 17 checkers run on case 0806_zhaowei (deck=calibre), CALIBRE_HOME set.

- ldr: PASS
- drcSyntax: PASS
- drcLayerMap: PASS
- drcValue: PASS
- drcOption: PASS
- drcPowerList: PASS
- drcDeriveLayerVsFracture: PASS
- drcDeriveLayerVsFractureAndTruthOverall: PASS
- uselessDeriveLayer: PASS
- patternDeviceLayer: PASS
- patternLayerVsFracture: PASS
- emptyDeriveLayer: PASS
- drcWithPattern: PASS
- patternLayerVsDesignRuleLayerChange: PASS
- drcConsistencyWithChangedLdr: PASS
- drcCountWithinOption: PASS
- antMetalThk: PASS
'''

BUGGY_PHASE2_REPORT = '''# PHASE2_REPORT.md

Set CALIBRE_HOME to the installed aoi tree and added its lib paths.  All 17
checkers pass.  No VCO issues observed.
'''

# ----------------------------------------------------------------------------
# 4. CHECK FUNCTION (7 conditions a-g, with teeth)
# ----------------------------------------------------------------------------

CHECK_SRC = r'''def check(deliverable, workdir):
    """PDK-QA DRC test-environment deliverable checker.

    deliverable: path to submit.zip (relative to workdir), e.g. "outputs/submit.zip"
    workdir:     session workdir (attachments placed here at session open).

    7 independent conditions (a)-(g). All-static Python (no Calibre run needed).
    TEETH: a naive "only CALIBRE_HOME" solution FAILS (c)+(d)+(g); the correct
    fake-MGC_HOME + stub-libXss + auto-rebuild solution PASSES.
    """
    import os, re, zipfile

    p = os.path.join(workdir, deliverable)
    if not os.path.isfile(p):
        raise FileNotFoundError("deliverable not found: " + deliverable)

    need = ["test_env.py", "smoke_report.md", "PHASE2_REPORT.md"]
    with zipfile.ZipFile(p) as z:
        bmap = {}
        for n in z.namelist():
            if n.endswith("/"):
                continue
            bmap[os.path.basename(n)] = n
        missing = [b for b in need if b not in bmap]
        if missing:
            raise AssertionError("submit.zip missing: " + ", ".join(missing))
        env_txt   = z.read(bmap["test_env.py"]).decode("utf-8", "ignore")
        smoke_txt = z.read(bmap["smoke_report.md"]).decode("utf-8", "ignore")
        rep_txt   = z.read(bmap["PHASE2_REPORT.md"]).decode("utf-8", "ignore")

    SUPPORT = [
        "ldr", "drcSyntax", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
        "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
        "uselessDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
        "emptyDeriveLayer", "drcWithPattern",
        "patternLayerVsDesignRuleLayerChange", "drcConsistencyWithChangedLdr",
        "drcCountWithinOption", "antMetalThk",
    ]
    TEXT = [
        "ldr", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
        "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
        "uselessDeriveLayer", "drcConsistencyWithChangedLdr",
        "drcCountWithinOption", "antMetalThk",
    ]
    PATTERN_CANSTART = [
        "emptyDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
        "patternLayerVsDesignRuleLayerChange", "drcWithPattern",
    ]

    # (a) zip contains the 3 deliverables
    assert len(missing) == 0, "(a) missing deliverables: " + str(missing)

    # (b) test_env.py fixes libpython3.7 by putting python-3.7.1 lib on LD_LIBRARY_PATH
    assert "python-3.7.1/x86_64/lib" in env_txt, \
        "(b) test_env.py does not add python-3.7.1/x86_64/lib to LD_LIBRARY_PATH"

    # (c) Calibre VCO bypass: fake MGC_HOME assigned + fake-home tmp path + stub libXss + calibre_vco stub
    #     TEETH: "only CALIBRE_HOME" has none of these -> FAIL.
    has_mgc_assign = re.search(r'MGC_HOME["\']?\]?\s*=\s*', env_txt) is not None
    has_fake_home  = ("calibre_fake_home" in env_txt) or (re.search(r'fake[_\s]*home', env_txt, re.I) is not None)
    has_libxss     = "libXss" in env_txt
    has_vco_stub   = "calibre_vco" in env_txt
    assert has_mgc_assign and has_fake_home and has_libxss and has_vco_stub, \
        "(c) no fake-MGC_HOME + stub-libXss + calibre_vco bypass (got mgc=%s fakehome=%s xss=%s vco=%s)" \
        % (has_mgc_assign, has_fake_home, has_libxss, has_vco_stub)

    # (d) auto-rebuild at import: existence check of BOTH stub paths + rebuild-if-missing
    #     + a module-level invocation of the setup.
    #     TEETH: bypass defined but only called lazily / always-recreate / no import call -> FAIL.
    has_fakehome_path = "/tmp/calibre_fake_home" in env_txt
    has_libxss_path   = "/tmp/libXss.so.1" in env_txt
    has_existence_check = re.search(
        r'not\s+os\.path\.(isdir|exists)\s*\(\s*_FAKE_HOME\s*\)|'
        r'not\s+os\.path\.(isdir|exists)\s*\(\s*_LIBXSS\s*\)|'
        r'need_rebuild|rebuild\s*=|if.*missing', env_txt) is not None
    has_import_call = re.search(r'^_setup_calibre_env\(\)\s*$',
                                env_txt, re.MULTILINE) is not None
    assert has_fakehome_path and has_libxss_path and has_existence_check and has_import_call, \
        "(d) no auto-rebuild-at-import (paths=%s/%s existence=%s importcall=%s)" \
        % (has_fakehome_path, has_libxss_path, has_existence_check, has_import_call)

    # (e) check_calibre_env() returns a (ok, msg) tuple
    m = re.search(r'def\s+check_calibre_env\s*\([^)]*\)\s*:.*?(?=\n(?:def\s|\Z))',
                  env_txt, re.DOTALL)
    assert m is not None, "(e) no check_calibre_env() definition"
    body = m.group(0)
    assert re.search(r'return\s*\(\s*\w+\s*,\s*[^)]*\s*\)|return\s+\w+\s*,\s*',
                      body) is not None, \
        "(e) check_calibre_env() does not return a (ok, msg) tuple"

    # (f) smoke_report lists all 17 supportFuncnames with correct verdicts:
    #     11 text -> PASS, drcSyntax -> PASS, 5 pattern -> CAN_START (not PASS, not SKIP/FAIL)
    for name in SUPPORT:
        assert name in smoke_txt, "(f) smoke_report missing checker: " + name
    for name in TEXT:
        line = re.search(r'^\s*[-*]\s*' + re.escape(name) + r'\s*:\s*(\w+)',
                         smoke_txt, re.MULTILINE)
        assert line and line.group(1).upper() == "PASS", \
            "(f) text checker %s not PASS (got %s)" % (name, line.group(1) if line else None)
    ds = re.search(r'^\s*[-*]\s*drcSyntax\s*:\s*(\w+)', smoke_txt, re.MULTILINE)
    assert ds and ds.group(1).upper() == "PASS", \
        "(f) drcSyntax not PASS (got %s)" % (ds.group(1) if ds else None)
    for name in PATTERN_CANSTART:
        line = re.search(r'^\s*[-*]\s*' + re.escape(name) + r'\s*:\s*(\w+)',
                         smoke_txt, re.MULTILINE)
        assert line and line.group(1).upper() == "CAN_START", \
            "(f) pattern checker %s not CAN_START (got %s) -- VCO was resolved, " \
            "pattern QA can start; marking PASS is wrong, SKIP/FAIL is wrong." \
            % (name, line.group(1) if line else None)

    # (g) PHASE2_REPORT pinpoints the calibre_env variable-name bug AND records
    #     that the CALIBRE_HOME-only regular approach was tried and failed AND
    #     the hacky workaround was restored.
    #     TEETH: a report that says "set CALIBRE_HOME, all pass" -> FAIL.
    has_varbug = (re.search(r'SW_WKSTN|MGC_VCO_', rep_txt) is not None and
                  re.search(r'(variable|var|underscore|\$SW|shell)', rep_txt, re.I) is not None)
    has_regular_fail = bool(re.search(
        r'CALIBRE_HOME.*?(fail|did not|does not|still|ineffective|unconditional|'
        r'unconditionnally|tried.{0,12}fail)', rep_txt, re.I | re.DOTALL))
    has_hacky_restore = bool(re.search(
        r'(restor|fake\s+MGC_HOME|stub\s+libXss|workaround)', rep_txt, re.I))
    assert has_varbug, "(g) PHASE2_REPORT does not pinpoint the calibre_env variable-name bug"
    assert has_regular_fail, \
        "(g) PHASE2_REPORT does not record that CALIBRE_HOME-only failed"
    assert has_hacky_restore, \
        "(g) PHASE2_REPORT does not describe the restored hacky workaround"

    return True
'''

# ----------------------------------------------------------------------------
# 5. BUILD ASSETS + REFERENCE + JSONL ENTRY
# ----------------------------------------------------------------------------

def write_assets():
    os.makedirs(ASSET_DIR, exist_ok=True)
    files = {
        "DrcQa.py": DRCQA_PY,
        "calibre_env_excerpt.sh": CALIBRE_ENV_EXCERPT,
        "env_symptoms.txt": ENV_SYMPTOMS,
        "known_issues.md": KNOWN_ISSUES,
        "run_all_tests.py": RUN_ALL_TESTS,
    }
    for k, v in files.items():
        with open(os.path.join(ASSET_DIR, k), "w") as f:
            f.write(v)
    tdir = os.path.join(ASSET_DIR, "tests_skeleton")
    os.makedirs(tdir, exist_ok=True)
    for name in SUPPORT_FUNCNAMES:
        sub = os.path.join(tdir, name)
        os.makedirs(sub, exist_ok=True)
        with open(os.path.join(sub, "run_test.py"), "w") as f:
            f.write(_run_test_skeleton(name))
    with open(os.path.join(tdir, "run_all_tests.py"), "w") as f:
        f.write(RUN_ALL_TESTS)
    with open(os.path.join(ASSET_DIR, "_check.py"), "w") as f:
        f.write(CHECK_SRC)
    print("[assets] wrote", ASSET_DIR)

def make_zip(env_py, smoke_md, phase_md, zip_path, extra=None):
    os.makedirs(os.path.dirname(zip_path), exist_ok=True)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("test_env.py", env_py)
        z.writestr("smoke_report.md", smoke_md)
        z.writestr("PHASE2_REPORT.md", phase_md)
        if extra:
            for n, c in extra.items():
                z.writestr(n, c)
    return zip_path

def write_reference():
    os.makedirs(REF_DIR, exist_ok=True)
    for fn in ["DrcQa.py", "calibre_env_excerpt.sh", "env_symptoms.txt",
               "known_issues.md"]:
        shutil.copy(os.path.join(ASSET_DIR, fn), os.path.join(REF_DIR, fn))
    with open(os.path.join(REF_DIR, "check.py"), "w") as f:
        f.write(CHECK_SRC)
    make_zip(CORRECT_TEST_ENV, CORRECT_SMOKE_REPORT, CORRECT_PHASE2_REPORT,
             os.path.join(REF_DIR, "reference_submit.zip"))
    print("[reference] wrote", REF_DIR)

def append_jsonl():
    attachments = [
        {"name": "DrcQa.py", "source": "DrcQa.py",
         "desc": "PDK QA DRC entry point; defines 17 registered supportFuncnames + text/pattern checker split"},
        {"name": "calibre_env_excerpt.sh", "source": "calibre_env_excerpt.sh",
         "desc": "Excerpt of Calibre 2020.1_36 calibre_env with the buggy autoswitch grep line"},
        {"name": "env_symptoms.txt", "source": "env_symptoms.txt",
         "desc": "Observed env failures: libpython3.7 missing, VCO aok error, CALIBRE_HOME-alone still fails"},
        {"name": "known_issues.md", "source": "known_issues.md",
         "desc": "Known issues log; K10 = Calibre VCO autoswitch bug (placeholder detail)"},
        {"name": "tests_skeleton/run_all_tests.py", "source": "tests_skeleton/run_all_tests.py",
         "desc": "Smoke-test runner skeleton iterating the 17 supportFuncnames"},
    ]
    prompt = (
        "这是一个 PDK QA System 的 DRC 测试环境建立任务（真实 trace 来源：pdkQaSystem "
        "Windows→Linux 迁移 Phase 2，主机 hfeg0pkn004 / RHEL 8 / Calibre 2020.1_36）。\n\n"
        "附件是迁移包的关键文件：\n"
        "- DrcQa.py：DRC 主入口，定义了 17 个已注册 checker（supportFuncnames），并按 text（不依赖 "
        "Calibre 运行）/ pattern（依赖 calibre/calibredrv 运行）分类；\n"
        "- calibre_env_excerpt.sh：Calibre 自带 calibre_env 脚本的节选，含 VCO autoswitch 的 grep 逻辑；\n"
        "- env_symptoms.txt：在非交互进程里跑 DRC 测试时观察到的环境故障（libpython3.7m.so.1.0 缺失、"
        "VCO=aok 报错、非交互不加载 .bashrc、只设 CALIBRE_HOME 仍报错）；\n"
        "- known_issues.md：已知问题记录（K10 占位）；\n"
        "- tests_skeleton/run_all_tests.py：17 checker 冒烟测试运行器骨架。\n\n"
        "任务（多步，须在一次会话里完成并交付）：\n"
        "为这 17 个 checker 建立可在非交互进程中跑通冒烟测试的环境，产出三份交付件打包成 "
        "outputs/submit.zip：\n"
        "1. test_env.py —— 共享测试环境建立模块。必须解决两个环境问题：\n"
        "   (1) Python libpython3.7m.so.1.0 缺失：把 /apps/local/python/python-3.7.1/x86_64/lib "
        "加到 LD_LIBRARY_PATH；\n"
        "   (2) Calibre VCO aok/aoi autoswitch 失败：先读 calibre_env_excerpt.sh 和 env_symptoms.txt "
        "定位根因。注意：**只设 CALIBRE_HOME 是无效的**（calibre_env 会无条件运行 calibre_vco，"
        "autoswitch 的 grep bug 仍会触发）。必须实现绕过方案：在 /tmp 建一个假的 MGC_HOME，"
        "其 bin/calibre_vco 桩脚本返回 'aoi'（让 autoswitch 认到已安装的 aoi 树）+ 一个桩 "
        "libXss.so.1（机器缺这个依赖）+ LD_LIBRARY_PATH 指向真实 aoi lib。该绕过桩要在导入时"
        "**自动重建**（检查 /tmp/calibre_fake_home 与 /tmp/libXss.so.1 是否存在，缺失则重建，"
        "因为 /tmp 可能被清理）。模块还要提供 check_calibre_env()->(ok,msg)、get_real_path、"
        "chdir_to_data_dir、print_result 等辅助函数。\n"
        "2. smoke_report.md —— 17 个 checker 的冒烟结果。text checker（11 个）应 PASS；"
        "drcSyntax 应 PASS（rules_syntax_checker 能完成）；其余 5 个 pattern QA checker 在本环境"
        "下只能验证\"能启动\"（calibre/calibredrv 启动后 kill+清理，VCO 已被绕过解决），结果记 "
        "CAN_START，不要记 PASS（未跑完整流程）也不要记 SKIP/FAIL（环境已解决）。\n"
        "3. PHASE2_REPORT.md —— 环境问题分析。必须定位 Calibre VCO 根因（calibre_env 里 "
        "$SW_WKSTN_ / $MGC_VCO_ 这类带下划线的 shell 变量名解析 bug），并明确记录\"只设 "
        "CALIBRE_HOME 的正规方案已尝试且无效（calibre_env 无条件运行 calibre_vco）\"，以及最终"
        "恢复的假 MGC_HOME + 桩 libXss 绕过方案。\n\n"
        "约束：\n"
        "- 不改 DrcQa.py 的 supportFuncnames（17 个已注册 checker 清单不变）；\n"
        "- 沙盒里没有真实 Calibre 安装，方案要能被静态校验（test 只读 zip 内文件内容判分，不实跑 "
        "Calibre）；\n"
        "- 真实用户名/路径脱敏（附件已脱敏，交付件里不要出现真实用户名）。\n"
        "- 交付件打包成 outputs/submit.zip，内含 test_env.py / smoke_report.md / PHASE2_REPORT.md。"
    )
    entry = {
        "task_id": TID,
        "mode": "design_flow",
        "prompt": prompt,
        "attachments": attachments,
        "entry_point": "outputs/submit.zip",
        "expected_artifacts": ["test_env.py", "smoke_report.md", "PHASE2_REPORT.md"],
        "test": CHECK_SRC,
        "budget": {"max_turns": 40, "wall_time_sec": 1800, "max_tool_calls": 120},
        "metadata": {
            "domain": "physical_verify",
            "task_name": "PDK QA DRC 测试环境建立 (Calibre VCO aok/aoi autoswitch bug 绕过)",
            "scenario": "真实 PDK QA System Windows→Linux 迁移 Phase 2: 为 17 个 DRC checker 建立非交互进程可跑的测试环境, 核心卡点 Calibre VCO autoswitch bug 以假 MGC_HOME+桩 libXss 绕过",
            "direction": "physical_verify",
            "layer": "drc_test_env_setup",
            "topic": "Calibre 2020.1_36 VCO autoswitch / calibre_env shell var bug / fake MGC_HOME / stub libXss / auto-rebuild",
            "difficulty": "hard",
            "design": "pdkQaSystem DRC QA flow (17 supportFuncnames)",
            "tcr_refs": [],
            "heavy": False,
            "wall_time_sec": 1800,
            "trace_source": {
                "host": "hfeg0pkn004",
                "user_hash": "7fa3eec75ddd",
                "session_file": "1788770994295_x4b0p",
                "session_msgs": 537,
                "match_count": 1367,
                "real_task_summary": "PDK QA DRC 框架 Windows→Linux 迁移, Calibre VCO aok/aoi autoswitch bug 以假 MGC_HOME+stub libXss 绕过, 17 checker 测试建立",
            },
            "legacy_source_file": None,
        },
    }
    kept = []
    if os.path.exists(JSONL):
        with open(JSONL) as f:
            for l in f:
                if l.strip():
                    try:
                        d = json.loads(l)
                        if d.get("task_id") == TID:
                            continue
                    except Exception:
                        pass
                    kept.append(l.rstrip("\n"))
    with open(JSONL, "w") as f:
        for l in kept:
            f.write(l + "\n")
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print("[jsonl] appended", TID, "rows now =", len(kept) + 1)

# ----------------------------------------------------------------------------
# 6. TEETH VALIDATION
# ----------------------------------------------------------------------------

def _load_check():
    local = {}
    exec(CHECK_SRC, local)
    return local["check"]

def _run(check, env_py, smoke_md, phase_md, label, tmpdir):
    zp = os.path.join(tmpdir, label + ".zip")
    make_zip(env_py, smoke_md, phase_md, zp)
    try:
        check(os.path.basename(zp), tmpdir)
        return ("PASS", None)
    except AssertionError as e:
        return ("FAIL", str(e))
    except Exception as e:
        return ("ERR", repr(e))

def validate_teeth():
    check = _load_check()
    tmpdir = "/tmp/pdkqa_teeth_" + str(os.getpid())
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    os.makedirs(tmpdir, exist_ok=True)
    results = {}

    results["CORRECT"] = _run(check, CORRECT_TEST_ENV, CORRECT_SMOKE_REPORT,
                              CORRECT_PHASE2_REPORT, "correct", tmpdir)
    results["BUGGY_regular"] = _run(check, BUGGY_TEST_ENV, BUGGY_SMOKE_REPORT,
                                    BUGGY_PHASE2_REPORT, "buggy", tmpdir)

    # (a) break: drop a deliverable
    def run_a():
        zp = os.path.join(tmpdir, "fail_a.zip")
        with zipfile.ZipFile(zp, "w") as z:
            z.writestr("test_env.py", CORRECT_TEST_ENV)
            z.writestr("smoke_report.md", CORRECT_SMOKE_REPORT)
        try:
            check(os.path.basename(zp), tmpdir); return ("PASS", None)
        except (AssertionError, Exception) as e: return ("FAIL/ERR", str(e))
    results["isolated_a_missing_deliverable"] = run_a()

    # (b) break: remove python-3.7.1 lib line
    bad_env_b = CORRECT_TEST_ENV.replace(
        '_PY_LIB = "/apps/local/python/python-3.7.1/x86_64/lib"',
        '_PY_LIB = "/apps/local/python/x86_64/lib"')
    results["isolated_b_no_pylib"] = _run(check, bad_env_b, CORRECT_SMOKE_REPORT,
                                          CORRECT_PHASE2_REPORT, "fail_b", tmpdir)

    # (c) break: remove the bypass (only CALIBRE_HOME) but keep auto-rebuild scaffolding
    bad_env_c = CORRECT_TEST_ENV.replace(
        'os.environ["MGC_HOME"] = _FAKE_HOME',
        'os.environ["CALIBRE_HOME"] = _REAL_CALIBRE  # no fake mgc home'
    ).replace('with open(_LIBXSS, "w")', 'with open("/tmp/_disabled", "w")'
    ).replace('"libXss"', '"_xss_disabled_"')
    results["isolated_c_no_bypass"] = _run(check, bad_env_c, CORRECT_SMOKE_REPORT,
                                           CORRECT_PHASE2_REPORT, "fail_c", tmpdir)

    # (d) break: bypass present but no auto-rebuild (no existence check, no import call)
    bad_env_d = CORRECT_TEST_ENV.replace(
        "    # auto-rebuild: check both stubs exist, rebuild if either is missing\n"
        "    need_rebuild = (not os.path.isdir(_FAKE_HOME)) or (not os.path.exists(_LIBXSS))\n"
        "    if need_rebuild:\n",
        "    if True:\n"
    ).replace("# auto-rebuild at import\n_setup_calibre_env()\n",
              "# no import-time setup\n")
    results["isolated_d_no_autorebuild"] = _run(check, bad_env_d, CORRECT_SMOKE_REPORT,
                                                CORRECT_PHASE2_REPORT, "fail_d", tmpdir)

    # (e) break: check_calibre_env returns bool not tuple
    bad_env_e = CORRECT_TEST_ENV.replace(
        '    return (ok, "VCO bypass active" if ok else "VCO bypass missing")',
        '    return ok')
    results["isolated_e_no_tuple"] = _run(check, bad_env_e, CORRECT_SMOKE_REPORT,
                                          CORRECT_PHASE2_REPORT, "fail_e", tmpdir)

    # (f) break: mark all 17 PASS (wrong for pattern)
    bad_smoke_f = CORRECT_SMOKE_REPORT.replace("CAN_START", "PASS")
    results["isolated_f_pattern_as_pass"] = _run(check, CORRECT_TEST_ENV, bad_smoke_f,
                                                 CORRECT_PHASE2_REPORT, "fail_f", tmpdir)
    bad_smoke_f2 = CORRECT_SMOKE_REPORT.replace("CAN_START", "SKIP")
    results["isolated_f2_pattern_as_skip"] = _run(check, CORRECT_TEST_ENV, bad_smoke_f2,
                                                  CORRECT_PHASE2_REPORT, "fail_f2", tmpdir)
    bad_smoke_f3 = CORRECT_SMOKE_REPORT.replace("- antMetalThk: PASS\n", "")
    results["isolated_f3_missing_checker"] = _run(check, CORRECT_TEST_ENV, bad_smoke_f3,
                                                  CORRECT_PHASE2_REPORT, "fail_f3", tmpdir)

    # (g) break: naive report
    results["isolated_g_naive_report"] = _run(check, CORRECT_TEST_ENV, CORRECT_SMOKE_REPORT,
                                              BUGGY_PHASE2_REPORT, "fail_g", tmpdir)

    print("\n=== TEETH RESULTS ===")
    ok = True
    for k, (v, msg) in results.items():
        flag = "OK" if (k == "CORRECT" and v == "PASS") or \
                       (k != "CORRECT" and v in ("FAIL", "FAIL/ERR", "ERR")) else "BAD"
        if flag == "BAD":
            ok = False
        print(f"  [{flag}] {k}: {v}  {msg or ''}")
    print("=== ALL TEETH OK ===" if ok else "=== TEETH MISMATCH ===")
    shutil.rmtree(tmpdir, ignore_errors=True)
    return ok

if __name__ == "__main__":
    write_assets()
    write_reference()
    append_jsonl()
    ok = validate_teeth()
    with open(JSONL) as f:
        rows = [json.loads(l) for l in f if l.strip()]
    assert len(set(r["task_id"] for r in rows)) == len(rows), "duplicate task_id"
    print(f"[round-trip] {len(rows)} rows, {len(set(r['task_id'] for r in rows))} unique ids")
    sys.exit(0 if ok else 1)
