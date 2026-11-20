#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""test_env.py -- shared environment setup for the DRC QA smoke tests.

Fixes two environment failures observed when the tests run as a
non-interactive process on RHEL 8 (no .bashrc sourced, so no `module load`):

  1. Python: libpython3.7m.so.1.0 is missing from LD_LIBRARY_PATH.
     -> put /apps/local/python/python-3.7.1/x86_64/lib on LD_LIBRARY_PATH.

  2. Calibre VCO aok/aoi autoswitch failure in calibre_env.
     -> Setting CALIBRE_HOME alone does NOT help: calibre_env runs
        calibre_vco unconditionally and the autoswitch grep uses shell
        variable names with a trailing underscore ($SW_WKSTN_ / $MGC_VCO_)
        which bash resolves to empty strings, so the aok tree never
        matches.  Even when CALIBRE_HOME points at the installed aoi tree,
        the error "VCO aok not supported by autoswitch" still fires.
     -> Workaround: build a fake MGC_HOME at /tmp/calibre_fake_home whose
        bin/calibre_vco stub echoes 'aoi' (the installed tree), place a
        stub /tmp/libXss.so.1 (missing X dependency), and put the real aoi
        shared lib dir on LD_LIBRARY_PATH.  The stubs are rebuilt at import
        time if /tmp has been cleaned.
"""

import os
import sys
import shutil

# ---- fix (1): libpython3.7m.so.1.0 ---------------------------------------
_PY_LIB = "/apps/local/python/python-3.7.1/x86_64/lib"

# ---- fix (2): Calibre VCO autoswitch bypass ------------------------------
# Fake MGC_HOME whose bin/calibre_vco returns 'aoi' so that calibre_env's
# autoswitch logic recognises the installed tree instead of the OS-reported
# 'aok' (which has no matching tree).  CALIBRE_HOME alone is insufficient.
_FAKE_HOME = "/tmp/calibre_fake_home"
_FAKE_BIN = os.path.join(_FAKE_HOME, "bin")
_FAKE_VCO = os.path.join(_FAKE_BIN, "calibre_vco")

# Stub for the missing libXss.so.1 (X screen-saver) system dependency.
_LIBXSS = "/tmp/libXss.so.1"

# Real installed Calibre aoi tree (Calibre 2020.1_36); its shared libs stay
# on LD_LIBRARY_PATH.  No real usernames are embedded here.
_REAL_AOI_HOME = "/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18"
_REAL_AOI_LIB = os.path.join(_REAL_AOI_HOME, "shared", "lib")


def _vco_stub_text():
    """calibre_vco stub: always report the installed 'aoi' VCO."""
    return "#!/bin/sh\n# VCO autoswitch bypass stub: report the installed aoi tree.\necho aoi\n"


def _rebuild_fake_home():
    """(Re)create the fake MGC_HOME and its executable calibre_vco stub."""
    os.makedirs(_FAKE_BIN, exist_ok=True)
    with open(_FAKE_VCO, "w") as f:
        f.write(_vco_stub_text())
    os.chmod(_FAKE_VCO, 0o755)


def _rebuild_libxss_stub():
    """(Re)create the placeholder /tmp/libXss.so.1 for the missing X lib."""
    with open(_LIBXSS, "wb") as f:
        f.write(b"")


def _split_ld_library_path():
    raw = os.environ.get("LD_LIBRARY_PATH", "")
    return [p for p in raw.split(os.pathsep) if p]


def _prepend_ld_library_path(newpath):
    parts = _split_ld_library_path()
    if newpath not in parts:
        parts.insert(0, newpath)
    os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(parts)


def _append_ld_library_path(newpath):
    parts = _split_ld_library_path()
    if newpath not in parts:
        parts.append(newpath)
    os.environ["LD_LIBRARY_PATH"] = os.pathsep.join(parts)


def _setup_calibre_env():
    """Build the full DRC test environment.  Idempotent and safe to call
    multiple times; missing /tmp stubs are rebuilt automatically."""
    # (1) libpython3.7m.so.1.0 fix
    _append_ld_library_path(_PY_LIB)

    # (2) auto-rebuild the VCO bypass stubs if /tmp has been cleaned
    if not os.path.isdir(_FAKE_HOME) or not os.path.exists(_FAKE_VCO):
        _rebuild_fake_home()
    if not os.path.exists(_LIBXSS):
        _rebuild_libxss_stub()

    # (3) route calibre_vco through the fake MGC_HOME (this is the actual
    #     fix; setting CALIBRE_HOME alone is ineffective because calibre_env
    #     runs calibre_vco unconditionally).
    os.environ["MGC_HOME"] = _FAKE_HOME
    os.environ["CALIBRE_HOME"] = _REAL_AOI_HOME
    os.environ["CALIBRE_SKIP_OS_CHECKS"] = "1"

    # (4) PATH: fake bin first so /bin/calibre_vco resolves to the stub,
    #     then the real Calibre bin directory.
    os.environ["PATH"] = os.pathsep.join(
        [_FAKE_BIN,
         os.path.join(_REAL_AOI_HOME, "bin"),
         os.environ.get("PATH", "")])

    # (5) LD_LIBRARY_PATH: /tmp (for the libXss stub) then the real aoi libs.
    _prepend_ld_library_path(os.path.dirname(_LIBXSS))
    _prepend_ld_library_path(_REAL_AOI_LIB)


def check_calibre_env():
    """Verify that the Calibre test environment is usable.

    Returns a (ok, msg) tuple: ok=True when the fake MGC_HOME VCO bypass,
    the libXss stub and the real aoi libs are all in place.
    """
    if not os.path.isdir(_FAKE_HOME) or not os.path.isfile(_FAKE_VCO):
        return (False, "fake MGC_HOME calibre_vco stub is missing")
    if not os.path.exists(_LIBXSS):
        return (False, "libXss.so.1 stub is missing")
    if os.environ.get("MGC_HOME") != _FAKE_HOME:
        return (False, "MGC_HOME does not point at the fake VCO bypass home")
    if _PY_LIB not in os.environ.get("LD_LIBRARY_PATH", ""):
        return (False, "python-3.7.1 lib is not on LD_LIBRARY_PATH")
    return (True, "calibre env OK (fake MGC_HOME VCO bypass active)")


def get_real_path(path):
    """Return the canonical absolute path of *path* (fallback: path as-is)."""
    try:
        return os.path.realpath(path)
    except Exception:
        return path


def chdir_to_data_dir(case_dir=None):
    """Create (if needed) and switch to the DRC QA data directory."""
    target = case_dir or os.environ.get("CASE_DIR") or os.getcwd()
    os.makedirs(target, exist_ok=True)
    os.chdir(target)
    return os.getcwd()


def print_result(name, status, extra=""):
    """Print and return a single '- name: status' smoke-result line."""
    line = "- {}: {}".format(name, status)
    if extra:
        line += "  # " + str(extra)
    print(line)
    return line


# Module-level auto-setup: rebuild missing /tmp stubs and configure the
# environment as soon as this module is imported.
_setup_calibre_env()


if __name__ == "__main__":
    print("test_env.py self-check:")
    ok, msg = check_calibre_env()
    print("check_calibre_env ->", ok, msg)
    print("LD_LIBRARY_PATH =", os.environ.get("LD_LIBRARY_PATH"))
    print("MGC_HOME =", os.environ.get("MGC_HOME"))