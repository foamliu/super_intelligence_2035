#!/usr/bin/env python3
"""PrimeTime install-tree recon for STA-flow version selection.

Usage:
    python3 pt_version_recon.py <install_root>

Behaviour
---------
* Enumerate the top-level entries of <install_root>.
* Distinguish genuine install directories from symbolic links.
* For every entry, parse its install.log for product / version / installer.
* Check the presence of bin/pt_shell and bin/primetime.
* For symbolic links, resolve readlink / realpath and flag links whose
  destination escapes the install_root tree.

Output
------
A single JSON document printed to stdout containing:

    install_root     canonical absolute path that was scanned
    versions         list of per-entry records (see below)
    recommendation   name of the latest genuine "pts" (PrimeTime) install
                     directory, i.e. the one recommended for STA-flow debugging

Each ``versions`` record has these keys:

    name        top-level directory entry name
    is_symlink  True when the entry is a symbolic link
    readlink    raw symlink target (None for real directories)
    realpath    fully resolved path
    external    True when the entry resolves outside the install_root tree
    product     STANDALONE product token from install.log (e.g. "pts", "prime")
    version     version token from install.log ("... version." line)
    installer   Synopsys Installer version from install.log
    pt_shell    True when <entry>/bin/pt_shell exists
    primetime   True when <entry>/bin/primetime exists
"""

import json
import os
import re
import sys


def natural_key(value):
    """Order strings naturally so L<...<O<...<P<...<U<...<V<...<W."""
    parts = re.split(r"(\d+)", value)
    return [int(p) if p.isdigit() else p.lower() for p in parts]


def parse_install_log(entry_path):
    """Return (product, version, installer) parsed from ``install.log``.

    Returns ``None`` for any field that cannot be determined.
    """
    product = version = installer = None
    log_path = os.path.join(entry_path, "install.log")
    try:
        with open(log_path, "r", errors="replace") as fh:
            for raw in fh:
                line = raw.strip()
                if line.startswith("Synopsys Installer:") and installer is None:
                    installer = line.split(":", 1)[1].strip()
                elif line.startswith("STANDALONE") and product is None:
                    m = re.match(r"STANDALONE\s*:\s*(\S+)", line)
                    if m:
                        product = m.group(1)
                elif line.startswith("INSTALLING") and version is None:
                    m = re.match(
                        r"INSTALLING\s+\S+\s+product,\s+common package,\s+"
                        r"(\S+)\s+version",
                        line,
                    )
                    if m:
                        version = m.group(1)
    except OSError:
        pass
    return product, version, installer


def is_within(path, root):
    """Return True when ``path`` lies inside the ``root`` tree."""
    try:
        path_r = os.path.realpath(path)
        root_r = os.path.realpath(root)
        return os.path.commonpath([root_r, path_r]) == root_r
    except (OSError, ValueError):
        return False


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: python3 pt_version_recon.py <install_root>\n")
        return 2

    install_root = os.path.abspath(argv[1])
    if not os.path.isdir(install_root):
        sys.stderr.write("error: not a directory: {}\n".format(argv[1]))
        return 1

    names = sorted(os.listdir(install_root), key=natural_key)

    versions = []
    for name in names:
        path = os.path.join(install_root, name)
        is_link = os.path.islink(path)
        if not (is_link or os.path.isdir(path)):
            # Skip ordinary files and other non-directory entries.
            continue

        real = os.path.realpath(path)
        link_target = os.readlink(path) if is_link else None
        product, version, installer = parse_install_log(real)
        pt_shell = os.path.isfile(os.path.join(real, "bin", "pt_shell"))
        primetime = os.path.isfile(os.path.join(real, "bin", "primetime"))
        external = not is_within(real, install_root)

        versions.append({
            "name": name,
            "is_symlink": is_link,
            "readlink": link_target,
            "realpath": real,
            "external": external,
            "product": product,
            "version": version,
            "installer": installer,
            "pt_shell": pt_shell,
            "primetime": primetime,
        })

    # Recommendation: the latest genuine (non-symlink) "pts" install version.
    pts = [v for v in versions if not v["is_symlink"] and v["product"] == "pts"]
    recommendation = None
    if pts:
        latest = max(pts, key=lambda v: natural_key(v["version"] or v["name"]))
        recommendation = latest["name"]

    result = {
        "install_root": install_root,
        "versions": versions,
        "recommendation": recommendation,
    }
    sys.stdout.write(json.dumps(result, indent=2))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))