#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_check.py - generate self-contained check.py with embedded A/B/B2 netlists."""
import os, json, hashlib, textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/assets/EDA-Eval-DesignFlow-FarthestCellPick-001"

def read(p):
    with open(p) as f:
        return f.read()

NETLIST_A  = read(os.path.join(ASSETS, "netlist.sp"))
NETLIST_B  = read(os.path.join(ASSETS, "hidden", "netlist_B.sp"))
NETLIST_B2 = read(os.path.join(ASSETS, "hidden", "netlist_B2.sp"))

CHECK = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""check.py - judge for EDA-Eval-DesignFlow-FarthestCellPick-001.

check(deliverable, workdir) -> True if the submitted analyzer correctly
identifies the farthest cell for tCS/WR_Time on the HIDDEN B netlist, with
anti-hardcoding (A) and cross-input (B2) guards.

14 conditions a-n (each independently FAIL-able):
  a  zip structure + no forbidden imports/refs/paths
  b  py_compile of submitted analyzer
  c  candidate runs on B -> exit 0 + non-empty report
  d  report identifies the correct farthest cell instance (B)
  e  report states the correct cumulative BL resistance value (B, within tol)
  f  report states the correct farthest cell subckt type kcellx1mdl_<tier> (B)
  g  report states the correct measurement node (CC, B)
  h  report states the correct WL trigger net (B)
  i  report states the correct column (near/far, B)
  j  report does NOT name any RC-load decoy as farthest (B)
  k  anti-hardcode A: rerun on A -> farthest != B; source has no A-cell literals
  l  cross-input B2: rerun on B2 -> farthest != B and != A; source has no B2-cell literals; B2 farthest correct
  m  CLI: source uses sys.argv or argparse; no hardcoded input filename
  n  determinism: 3 runs on B -> identical report sha256
"""
import os, sys, re, json, zipfile, subprocess, tempfile, hashlib, collections, py_compile, io

NETLIST_A = __NETLIST_A__
NETLIST_B = __NETLIST_B__
NETLIST_B2 = __NETLIST_B2__

FORBIDDEN_IMPORTS = ("socket", "urllib", "requests", "pty", "http", "ftp", "telnet", "smtp", "subprocess")
FORBIDDEN_REFS = ("gen_farthest_cell_report_ref", "check", "reference", "_ref")
FORBIDDEN_PATHS = ("/proj/", "/rundata/", "/home/")

def _rval(tok):
    t = tok.strip()
    m = re.match(r"^([0-9.]+)\\s*([kKmMgGuUnNpPfF]?)$", t)
    if not m:
        try: return float(t)
        except: return 0.0
    val = float(m.group(1)); unit = m.group(2).lower()
    mul = {"":1.0,"k":1e3,"m":1e-3,"g":1e9,"u":1e-6,"n":1e-9,"p":1e-12,"f":1e-15}
    return val * mul.get(unit, 1.0)

def compute_farthest(text):
    """Reference computation: returns dict(inst, tier, cumR, cc, wl, column, subckt)."""
    sa = None; edges = []; targets = []; loads = []
    in_sub = False
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("*"): continue
        up = line.upper()
        if up.startswith(".SUBCKT"): in_sub = True; continue
        if up.startswith(".ENDS"): in_sub = False; continue
        if in_sub: continue
        if line.startswith("X") and re.match(r"^X\\w+", line):
            parts = line.split()
            if len(parts) < 2: continue
            inst = parts[0]; subckt = parts[-1]; ports = parts[1:-1]
            if subckt == "SA_unit" and len(ports) >= 1:
                if sa is None: sa = ports[0]
            elif subckt.startswith("kcellx1mdl_"):
                tier = subckt[len("kcellx1mdl_"):]
                if len(ports) >= 4:
                    targets.append(dict(inst=inst, bl=ports[0], wl=ports[1], cc=ports[2], vsn=ports[3], subckt=subckt, tier=tier))
            elif subckt == "kcellx32BGmdl_Load":
                loads.append(inst)
            continue
        if line.startswith("R") and re.match(r"^R\\w+", line):
            parts = line.split()
            if len(parts) >= 4:
                edges.append((parts[1], parts[2], _rval(parts[3])))
            continue
    adj = collections.defaultdict(list)
    for n1, n2, v in edges:
        adj[n1].append((n2, v)); adj[n2].append((n1, v))
    cum = {sa: 0.0}; q = collections.deque([sa])
    while q:
        n = q.popleft()
        for nb, v in adj[n]:
            if nb not in cum:
                cum[nb] = cum[n] + v; q.append(nb)
    best = None
    for c in targets:
        c["cumR"] = cum.get(c["bl"], -1.0)
        if best is None or c["cumR"] > best["cumR"]:
            best = c
    if best is None: return None
    col = "near" if "near" in best["inst"].lower() else ("far" if "far" in best["inst"].lower() else "unknown")
    return dict(inst=best["inst"], tier=best["tier"], cumR=best["cumR"], cc=best["cc"], wl=best["wl"], column=col, subckt=best["subckt"], loads=loads)

EXP = {
    "A":  compute_farthest(NETLIST_A),
    "B":  compute_farthest(NETLIST_B),
    "B2": compute_farthest(NETLIST_B2),
}

def _read_source(zip_path):
    src = None
    with zipfile.ZipFile(zip_path) as z:
        names = z.namelist()
        cand = [n for n in names if n.endswith("gen_farthest_cell_report.py")]
        if cand:
            src = z.read(cand[0]).decode("utf-8", "replace")
        return src, names

def _import_ok(line):
    """Return True if line is an import statement importing a forbidden module."""
    m = re.match(r"^\\s*(?:import|from)\\s+([\\w.]+)", line)
    return bool(m and any(m.group(1).split(".")[0] == fi for fi in FORBIDDEN_IMPORTS))

def _forbidden_ref_in_source(src):
    # match import statements referencing forbidden refs (not bare substrings -> avoid docstring false positives)
    for line in src.splitlines():
        if re.match(r"^\\s*(?:import|from)\\s+", line):
            for fr in FORBIDDEN_REFS:
                if fr in line:
                    return True
    return False

def _run_candidate(src, workdir, netlist_text, tag):
    """Write src + netlist to workdir, run, return (rc, report_text)."""
    with tempfile.TemporaryDirectory() as td:
        sp = os.path.join(td, "gen_farthest_cell_report.py")
        with open(sp, "w") as f:
            f.write(src)
        nl = os.path.join(td, "netlist_%s.sp" % tag)
        with open(nl, "w") as f:
            f.write(netlist_text)
        rep = os.path.join(td, "report_%s.txt" % tag)
        try:
            p = subprocess.run([sys.executable, sp, nl, "--out", rep],
                               capture_output=True, text=True, timeout=60)
            rc = p.returncode
        except Exception:
            return -1, ""
        txt = ""
        if os.path.exists(rep):
            with open(rep, "r", errors="replace") as f:
                txt = f.read()
        return rc, txt

def check(deliverable, workdir):
    """Return True iff all 14 conditions pass; raise AssertionError(msg) on first fail."""
    # locate the submitted zip
    zpath = deliverable
    if not os.path.exists(zpath):
        # try under workdir
        c = os.path.join(workdir, deliverable) if deliverable else None
        if c and os.path.exists(c):
            zpath = c
    if not zpath or not os.path.exists(zpath):
        raise AssertionError("a: deliverable zip not found: %s" % deliverable)
    src, names = _read_source(zpath)
    if src is None:
        raise AssertionError("a: zip missing gen_farthest_cell_report.py (got %s)" % names)
    # (a) structure + forbidden
    for line in src.splitlines():
        if _import_ok(line):
            raise AssertionError("a: forbidden import: %s" % line.strip())
    if _forbidden_ref_in_source(src):
        raise AssertionError("a: forbidden ref imported in source")
    for fp in FORBIDDEN_PATHS:
        if fp in src:
            raise AssertionError("a: forbidden path literal in source: %s" % fp)
    # (b) py_compile
    try:
        py_compile.compile(src.encode("utf-8"), doraise=True)
    except Exception as e:
        raise AssertionError("b: py_compile failed: %s" % e)
    expB = EXP["B"]; expA = EXP["A"]; expB2 = EXP["B2"]
    # (c) run on B
    rcB, repB = _run_candidate(src, workdir, NETLIST_B, "B")
    if rcB != 0 or not repB.strip():
        raise AssertionError("c: B run rc=%d report_empty=%s" % (rcB, not repB.strip()))
    repBl = repB.lower()
    # (d) farthest instance name (B)
    if expB["inst"].lower() not in repBl:
        raise AssertionError("d: B report missing farthest instance %s" % expB["inst"])
    # (e) cumulative R value (B, within tol)
    m = re.search(r"cum\\s*R\\s*:?\\s*([0-9]+(?:\\.[0-9]+)?)", repB, re.I)
    if not m:
        raise AssertionError("e: B report missing cumulative R value")
    if abs(float(m.group(1)) - expB["cumR"]) > 0.5:
        raise AssertionError("e: B cumulative R %s != expected %g" % (m.group(1), expB["cumR"]))
    # (f) subckt type kcellx1mdl_<tier> (B)
    if expB["subckt"].lower() not in repBl:
        raise AssertionError("f: B report missing subckt %s" % expB["subckt"])
    # (g) measurement node CC (B)
    if expB["cc"].lower() not in repBl:
        raise AssertionError("g: B report missing measurement node %s" % expB["cc"])
    # (h) WL trigger net (B)
    if expB["wl"].lower() not in repBl:
        raise AssertionError("h: B report missing WL trigger net %s" % expB["wl"])
    # (i) column (B)
    if expB["column"] not in repBl:
        raise AssertionError("i: B report missing column %s" % expB["column"])
    # (j) no load decoy named as farthest
    for ld in expB["loads"]:
        # load decoy may appear in a "decoys excluded" list - that's fine; ensure no "farthest ... <load>" pattern
        if re.search(r"farthest[^\\n]{0,40}%s" % re.escape(ld), repB, re.I):
            raise AssertionError("j: B report names load decoy %s as farthest" % ld)
    # (k) anti-hardcode A
    rcA, repA = _run_candidate(src, workdir, NETLIST_A, "A")
    if rcA != 0 or not repA.strip():
        raise AssertionError("k: A run failed rc=%d" % rcA)
    if expA["inst"].lower() not in repA.lower():
        raise AssertionError("k: A report missing farthest instance %s" % expA["inst"])
    if expA["inst"] == expB["inst"]:
        raise AssertionError("k: A and B farthest instance identical (no anti-hardcode)")
    # source must not contain A-specific cell-name literals (cc/wl/inst)
    for tok in (expA["inst"], expA["cc"], expA["wl"]):
        if tok in src:
            raise AssertionError("k: source contains A-specific literal %s" % tok)
    # (l) cross-input B2
    rcB2, repB2 = _run_candidate(src, workdir, NETLIST_B2, "B2")
    if rcB2 != 0 or not repB2.strip():
        raise AssertionError("l: B2 run failed rc=%d" % rcB2)
    if expB2["inst"].lower() not in repB2.lower():
        raise AssertionError("l: B2 report missing farthest instance %s" % expB2["inst"])
    if expB2["inst"] == expB["inst"] or expB2["inst"] == expA["inst"]:
        raise AssertionError("l: B2 farthest collides with A or B")
    for tok in (expB2["inst"], expB2["cc"], expB2["wl"]):
        if tok in src:
            raise AssertionError("l: source contains B2-specific literal %s" % tok)
    # (m) CLI
    if "sys.argv" not in src and "argparse" not in src:
        raise AssertionError("m: source does not use sys.argv/argparse")
    if re.search(r"open\\s*\\(\\s*['\\\"]netlist", src):
        raise AssertionError("m: source hardcodes input filename")
    # (n) determinism
    h = hashlib.sha256(repB.encode()).hexdigest()
    for _ in range(2):
        rc2, rep2 = _run_candidate(src, workdir, NETLIST_B, "B")
        if hashlib.sha256(rep2.encode()).hexdigest() != h:
            raise AssertionError("n: non-deterministic report across runs")
    return True

if __name__ == "__main__":
    # self-test: run reference solution against A/B/B2 -> all expected
    for tag, txt, exp in (("A", NETLIST_A, EXP["A"]), ("B", NETLIST_B, EXP["B"]), ("B2", NETLIST_B2, EXP["B2"])):
        assert exp is not None, "%s expected None" % tag
        print("%s farthest: %s cumR=%g tier=%s col=%s" % (tag, exp["inst"], exp["cumR"], exp["tier"], exp["column"]))
    print("EXP computed OK")
'''

CHECK = CHECK.replace("__NETLIST_A__", repr(NETLIST_A)).replace("__NETLIST_B__", repr(NETLIST_B)).replace("__NETLIST_B2__", repr(NETLIST_B2))

OUT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-FarthestCellPick-001/check.py"
with open(OUT, "w") as f:
    f.write(CHECK)
print("wrote", OUT, len(CHECK), "bytes")
# sanity: import and run self-test
import importlib.util
spec = importlib.util.spec_from_file_location("chk", OUT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("EXP:", {k: v["inst"] for k, v in m.EXP.items()})
