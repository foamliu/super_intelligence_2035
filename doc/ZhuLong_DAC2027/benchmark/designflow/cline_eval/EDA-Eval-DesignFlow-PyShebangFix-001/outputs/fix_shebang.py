#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fix_shebang.py

Diagnose and repair a hardcoded Python shebang that conflicts with a
module-managed Python environment configured in a shell startup file
(e.g. ``.bashrc``).

The crash being fixed is the classic:

    Fatal Python error: initfsencoding: unable to load the file system codec
    ModuleNotFoundError: No module named 'encodings'

which occurs when a launcher declares a hardcoded absolute-path shebang
(e.g. ``#!/apps/local/bin/python3``) while ``module switch python/3.11.9`` in
``.bashrc`` has exported ``PYTHONHOME`` / ``PYTHONPATH`` / ``LD_LIBRARY_PATH``
for a *different* Python build. The hardcoded interpreter is then launched
under a mismatched Python environment and cannot locate its own standard
library.

Usage:
    python3 fix_shebang.py <drc_auto_py> <bashrc> <output_py>

    <drc_auto_py>   input launcher whose first-line shebang may be hardcoded
    <bashrc>        shell startup file whose module setup selects Python
    <output_py>     path to write the repaired launcher (all other bytes
                    preserved byte-for-byte)

On success the script exits with status 0 and also writes ``diagnose.json``
into the current working directory.
"""

import json
import re
import sys

ENV_SHEBANG = "#!/usr/bin/env python3"
ENV_SHEBANG_BYTES = ENV_SHEBANG.encode("utf-8")

# Environment variables typically (re)exported by `module switch python/...`
# that poison a hardcoded interpreter's stdlib discovery at startup.
MODULE_ENV_VARS = ("PYTHONHOME", "PYTHONPATH", "LD_LIBRARY_PATH")


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def read_text(path):
    with open(path, "r", encoding="utf-8") as fh:
        return fh.read()


def write_bytes(path, data):
    with open(path, "wb") as fh:
        fh.write(data)


def fix_shebang(raw):
    """Repair a hardcoded first-line shebang, byte-for-byte otherwise.

    Returns (shebang_before, shebang_after, fixed_bytes, changed).
    """
    if not raw.startswith(b"#!"):
        return "", "", raw, False

    newline = raw.find(b"\n")
    if newline == -1:
        first_line = raw
        rest = b""
    else:
        first_line = raw[:newline]
        rest = raw[newline:]

    shebang_before = first_line.decode("utf-8", "replace")

    # Already the portable form -- nothing to do.
    if first_line == ENV_SHEBANG_BYTES:
        return shebang_before, ENV_SHEBANG, raw, False

    fixed = ENV_SHEBANG_BYTES + rest
    return shebang_before, ENV_SHEBANG, fixed, True


def parse_bashrc(bashrc_text):
    """Extract the module-selected Python version and conflicting env vars."""
    module_python_version = ""
    version_re = re.compile(
        r"module\s+(?:switch|load|add)\s+(?:python/)?([0-9]+\.[0-9]+(?:\.[0-9]+)?)",
        re.IGNORECASE,
    )
    for line in bashrc_text.splitlines():
        match = version_re.search(line)
        if match and not module_python_version:
            module_python_version = match.group(1)

    env_vars_conflict = [v for v in MODULE_ENV_VARS if v in bashrc_text]
    return module_python_version, env_vars_conflict


def build_diagnosis(shebang_before, shebang_after, module_python_version,
                    env_vars_conflict):
    env_join = ", ".join(env_vars_conflict)
    root_cause = (
        "drc_auto.py carries a hardcoded shebang '" + shebang_before + "' "
        "that launches a system interpreter, while .bashrc runs "
        "'module switch python/" + module_python_version + "' and exports "
        + env_join +
        " for the module-managed Python. The hardcoded interpreter is thus "
        "executed under a mismatched Python environment and cannot find its "
        "own standard library, aborting with 'initfsencoding: unable to load "
        "the file system codec / ModuleNotFoundError: No module named encodings'."
    )
    fix_summary = (
        "Rewrote the shebang from '" + shebang_before + "' to '" + shebang_after +
        "' so the launcher resolves python3 via PATH (the module-selected "
        "Python " + module_python_version + ") and inherits a consistent "
        + "/".join(env_vars_conflict) + ". All other file content was preserved."
    )
    return {
        "root_cause": root_cause,
        "shebang_before": shebang_before,
        "shebang_after": shebang_after,
        "module_python_version": module_python_version,
        "env_vars_conflict": env_vars_conflict,
        "fix_summary": fix_summary,
    }


def main(argv):
    if len(argv) != 4:
        sys.stderr.write(
            "usage: python3 fix_shebang.py <drc_auto_py> <bashrc> <output_py>\n"
        )
        return 2

    drc_auto_py, bashrc, output_py = argv[1], argv[2], argv[3]

    raw = read_bytes(drc_auto_py)
    shebang_before, shebang_after, fixed, _changed = fix_shebang(raw)

    bashrc_text = read_text(bashrc)
    module_python_version, env_vars_conflict = parse_bashrc(bashrc_text)

    write_bytes(output_py, fixed)

    diagnosis = build_diagnosis(shebang_before, shebang_after,
                                module_python_version, env_vars_conflict)
    try:
        with open("diagnose.json", "w", encoding="utf-8") as fh:
            json.dump(diagnosis, fh, ensure_ascii=False, indent=2)
            fh.write("\n")
    except OSError as exc:
        sys.stderr.write("warning: could not write diagnose.json: %s\n" % exc)

    print(json.dumps(diagnosis, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))