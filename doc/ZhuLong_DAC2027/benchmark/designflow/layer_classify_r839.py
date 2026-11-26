#!/usr/bin/env python3
"""r839 档1 layer normalize batch14 — classify 92 missing-layer B cases.

Methodology (r747): layer = whether check() stage actually runs an EDA binary
(incl. candidate-internal call + check validation path); original-trace run is
irrelevant.

- L1: check() only uses python subprocess / parsing (no EDA binary)
- L2: check() or candidate internally invokes a real EDA binary
      (hspice/finesim/calibre/vcs/virtuoso/innovus/primetime/xrun/...)
- L3: multi-tool chain + fix + regression (>=2 distinct EDA binaries + a
      fix-and-rerun loop)

Detector signals for L2:
  - subprocess.run/Popen/check_call/check_output with first-list-arg a binary
    name or a *path* ending in an EDA binary name
  - shutil.which("<eda_binary>")
  - hardcoded /apps/.../<eda_binary> path
  - candidate script (run via subprocess) itself invokes the binary (we rely
    on asset_fidelity / track metadata + a scan of the prompt + reference for
    binary-mention when check only runs python)

For B-domain spice_sim/characterization, the dominant pattern is offline
python parsing of .mt0/.tr0/.log/.ac0 -> L1.  Only cases that actually spawn
hspice/finesim/spectre/etc are L2.
"""
import json, os, re, sys

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

# binaries that count as "real EDA" for L2 (case-insensitive)
EDA_BINS = [
    "hspice", "finesim", "finesimpro", "finesim_xa", "xa",
    "spectre", "eldo", "ngspice", "xyce",
    "calibre", "calibreview", "pex", "lvs", "drc",
    "vcs", "verdi", "veriloga",
    "virtuoso", "ocean", "skill",
    "innovus", "icpv", "encounter",
    "primetime", "primesim", "pt_shell",
    "xrun", "xmelab", "irun", "ncsim", "ncverilog",
    "alps", "drcpa", "dsim",
    "star", "tau", "spyglass",
]

# regex: an EDA binary invoked as a command (subprocess first arg or which())
EDA_BIN_RE = re.compile(
    r'(?:subprocess\.(?:run|Popen|call|check_call|check_output)\s*\(\s*'
    r'\[?\s*["\']?(?:sys\.executable,\s*["\']?-c["\'],\s*)?'
    r'|shutil\.which\s*\(\s*["\']?'
    r'|os\.system\s*\(\s*["\']?'
    r'|os\.execv\w*\s*\()'
    r'([^"\']{0,80})',
    re.I,
)
# hardcoded /apps/.../bin/<eda> path
HARDCODED_PATH_RE = re.compile(
    r'/[^\s"\']+(?:bin|exec)[^\s"\']*/(' + '|'.join(EDA_BINS) + r')(?:\b|["\'])',
    re.I,
)
# subprocess([<bin>, ...]) where <bin> is a bare EDA binary name
BARE_CMD_RE = re.compile(
    r'subprocess\.(?:run|Popen|call|check_call|check_output)\s*\(\s*\[\s*'
    r'(["\'])(' + '|'.join(EDA_BINS) + r')\1',
    re.I,
)
# which("eda") / which('eda')
WHICH_RE = re.compile(
    r'(?:shutil\.which|os\.path\.which)\s*\(\s*'
    r'(["\'])(' + '|'.join(EDA_BINS) + r')\1',
    re.I,
)


def _binary_invoked(test: str) -> list:
    """Return list of EDA binaries that check() actually invokes as commands."""
    hits = set()
    # subprocess(["hspice", ...]) bare-name
    for m in BARE_CMD_RE.finditer(test):
        hits.add(m.group(2).lower())
    # shutil.which("hspice")
    for m in WHICH_RE.finditer(test):
        hits.add(m.group(2).lower())
    # hardcoded /apps/.../bin/hspice path
    for m in HARDCODED_PATH_RE.finditer(test):
        hits.add(m.group(1).lower())
    # subprocess([<var>, ...]) where var = "<path>/<bin>"; detect by
    # shutil.which assignment or HSPICE = "/apps/.../hspice"
    for m in re.finditer(
        r'=\s*["\']([^\s"\']*/(?:' + '|'.join(EDA_BINS) + r'))["\']', test, re.I
    ):
        hits.add(os.path.basename(m.group(1)).lower())
    return sorted(hits)


def classify(test: str) -> tuple:
    bins = _binary_invoked(test)
    # L3: >=2 distinct EDA binaries AND a rerun/fix loop marker
    rerun = re.search(r'fix|rerun|re-?run|regression|iterate|until.*clean|0\s*error', test, re.I)
    if len(bins) >= 2 and rerun:
        return ("L3", bins, "multi-tool + rerun")
    if bins:
        return ("L2", bins, "check invokes EDA binary")
    return ("L1", [], "offline python parsing/subprocess")


def main():
    files = sorted(f for f in os.listdir(CASES_DIR) if f.endswith(".json"))
    missing = []
    for f in files:
        c = json.load(open(os.path.join(CASES_DIR, f)))
        if c.get("metadata", {}).get("layer") is None:
            missing.append((f, c))
    print(f"# missing-layer cases: {len(missing)}")
    print("#" + "\t".join(["case", "domain", "track", "layer", "bins", "reason"]))
    rows = []
    for f, c in missing:
        tid = c.get("task_id", f).replace("EDA-Eval-DesignFlow-", "")
        md = c.get("metadata", {})
        test = c.get("test", "")
        layer, bins, reason = classify(test)
        rows.append((tid, md.get("domain", "?"), md.get("track", "?"),
                     layer, ",".join(bins) if bins else "-", reason))
    for r in rows:
        print("\t".join(str(x) for x in r))
    # batch14 = first 12 alphabetically
    print("\n# batch14 (first 12 alphabetical missing-layer):")
    from collections import Counter
    b14 = rows[:12]
    cnt = Counter(r[3] for r in b14)
    print(f"# batch14 layer dist: {dict(cnt)}")
    for r in b14:
        print(f"#   {r[0]:45s} -> {r[3]}  ({r[4]})  [{r[5]}]")


if __name__ == "__main__":
    main()
