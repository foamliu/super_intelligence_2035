#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build EDA-Eval-DesignFlow-XProbeHierGen-001 (shard D, schematic_netlist, B-grade synthesized L1).
Trace: ftu9v (xiwang@hfeg0pkn002, mc=497) — CrossProbe CSV generation from schematic hierarchy map.
User goal (U#4, i=117): regenerate CSV with hierPath truncated at parent circuit level (drop device instance segment).
Candidate: xprobe_hier_gen.py --fullmap <json> --seed <cell> --mode <leaf|parent> --out <csv>
"""
import json, os, csv, io, zipfile, shutil, subprocess, sys, re, hashlib, random

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-XProbeHierGen-001"
ASETS = os.path.join(BASE, "assets", CASE)
HIDDEN = os.path.join(ASETS, "hidden")
REF = os.path.join(BASE, "reference", CASE)
NEG = os.path.join(REF, "negative")
for d in [ASETS, HIDDEN, REF, NEG]:
    os.makedirs(d, exist_ok=True)

# ---------- fullmap generator ----------
def build_fullmap_A():
    """Synthesized A: root=ddgoa_top|WOWTOP, seed=ptn_lvio, ~20 cells, 6 direct seed parents,
    VblhDigDrvIPTop instantiated twice (multiple paths to same child)."""
    fm = {}
    fm["ddgoa_top|WOWTOP"] = {
        "LP5TOP": ["I_C_Top|ddgoa_cmos_top"],
        "LP5TOP_ArrayDie": ["I_A_Top|ddgoa_array_core"],
    }
    fm["ddgoa_array_core|LP5TOP_ArrayDie"] = {
        "ArrayDieBlk": ["I_ArrayDieBlk|ddgoa_array_core"],
    }
    fm["ddgoa_array_core|ArrayDieBlk"] = {}  # leaf, no seed
    fm["ddgoa_cmos_top|LP5TOP"] = {
        "Array16GTop": ["I_Array16GTop|ddgoa_cmos_core"],
        "VblhXdecTopE": ["I_VblhXdecTopE|commonIP"],
        "DqTxP2sM6": ["I_DqTx|commonIP"],
        "VintComp": ["I_VintComp|commonIP"],
    }
    fm["ddgoa_cmos_core|Array16GTop"] = {
        "Array8G_E": ["I_Array8G_E|ddgoa_cmos_core"],
        "Array8G_W": ["I_Array8G_W|ddgoa_cmos_core"],
    }
    fm["ddgoa_cmos_core|Array8G_W"] = {
        "Array1GBK0": ["I_Array1GBK0|ddgoa_cmos_core"],
    }
    fm["ddgoa_cmos_core|Array1GBK0"] = {}  # leaf, no seed
    fm["ddgoa_cmos_core|Array8G_E"] = {
        "Array1GBK1": ["I_Array1GBK1|ddgoa_cmos_core"],
        "VblhDigDrvIPTop": ["I_VblhDigDrvIPTop|commonIP"],
    }
    fm["ddgoa_cmos_core|Array1GBK1"] = {
        "VblhDigDrvIPTop": ["I_VblhDigDrvIPTop_1|commonIP"],
    }
    fm["commonIP|VblhDigDrvIPTop"] = {
        "VblhDigDrvCmpIP": ["I_VblhDigDrvCmpIP_2|commonIP"],
    }
    fm["commonIP|VblhDigDrvCmpIP"] = {
        "ptn_lvio": ["XMP0<3:0>|TECHLIB", "XMP1|TECHLIB"],
    }
    fm["commonIP|VblhXdecTopE"] = {
        "ptn_lvio": ["XMP5|TECHLIB"],
        "VblhXdecDrv": ["I_VblhXdecDrv|commonIP"],
    }
    fm["commonIP|VblhXdecDrv"] = {
        "ptn_lvio": ["XMP0<1:0>|TECHLIB"],
    }
    fm["commonIP|DqTxP2sM6"] = {
        "ptn_lvio": ["XMP0<1:0>|TECHLIB", "XMP2|TECHLIB"],
    }
    fm["commonIP|VintComp"] = {
        "ptn_lvio": ["XMP3|TECHLIB"],
        "VintAmp": ["I_VintAmp|commonIP"],
    }
    fm["commonIP|VintAmp"] = {
        "ptn_lvio": ["XMP4|TECHLIB"],
    }
    fm["TECHLIB|ptn_lvio"] = {}  # leaf device
    return fm, "ptn_lvio", "ddgoa_top|WOWTOP"


def build_fullmap_B():
    """Synthesized B: root=ddgoa_cmos_top|CHIP_TOP, seed=ptn_lv, different structure,
    more cells, different bus patterns, WckOsc branch with deeper nesting."""
    fm = {}
    fm["ddgoa_cmos_top|CHIP_TOP"] = {
        "CoreTop": ["I_CoreTop|ddgoa_cmos_core"],
        "IoTop": ["I_IoTop|ddgoa_cmos_io"],
    }
    fm["ddgoa_cmos_core|CoreTop"] = {
        "RowDecTop": ["I_RowDecTop|ddgoa_cmos_digital"],
        "SaArrayTop": ["I_SaArrayTop|ddgoa_cmos_core"],
        "VblhBiasGen": ["I_VblhBiasGen|commonIP"],
    }
    fm["ddgoa_cmos_io|IoTop"] = {
        "WckOscTop": ["I_WckOscTop|ddgoa_cmos_io"],
        "DqBufTop": ["I_DqBufTop|ddgoa_cmos_io"],
    }
    fm["ddgoa_cmos_digital|RowDecTop"] = {
        "RowDecDrv": ["I_RowDecDrv|ddgoa_cmos_digital"],
        "XdecGate": ["I_XdecGate|ddgoa_cmos_stdcells"],
    }
    fm["ddgoa_cmos_digital|RowDecDrv"] = {
        "ptn_lv": ["XMP0<7:0>|TECHLIB", "XMP1<3:0>|TECHLIB"],
    }
    fm["ddgoa_cmos_stdcells|XdecGate"] = {
        "ptn_lv": ["XMP2|TECHLIB"],
        "XdecInv": ["I_XdecInv|ddgoa_cmos_stdcells"],
    }
    fm["ddgoa_cmos_stdcells|XdecInv"] = {
        "ptn_lv": ["XMP0<1:0>|TECHLIB"],
    }
    fm["ddgoa_cmos_core|SaArrayTop"] = {
        "SaCmpTop": ["I_SaCmpTop|commonIP"],
        "SaClkTop": ["I_SaClkTop|ddgoa_cmos_digital"],
    }
    fm["commonIP|SaCmpTop"] = {
        "ptn_lv": ["XMP0<5:0>|TECHLIB"],
        "SaAmp": ["I_SaAmp|commonIP"],
    }
    fm["commonIP|SaAmp"] = {
        "ptn_lv": ["XMP3|TECHLIB"],
    }
    fm["ddgoa_cmos_digital|SaClkTop"] = {
        "ptn_lv": ["XMP4|TECHLIB"],
        "ClkDrv": ["I_ClkDrv|ddgoa_cmos_digital"],
    }
    fm["ddgoa_cmos_digital|ClkDrv"] = {
        "ptn_lv": ["XMP0<2:0>|TECHLIB"],
    }
    fm["commonIP|VblhBiasGen"] = {
        "ptn_lv": ["XMP0|TECHLIB"],
        "VblhAmp": ["I_VblhAmp|commonIP"],
    }
    fm["commonIP|VblhAmp"] = {
        "ptn_lv": ["XMP1<1:0>|TECHLIB"],
    }
    fm["ddgoa_cmos_io|WckOscTop"] = {
        "WckOscCore": ["I_WckOscCore|ddgoa_cmos_io"],
        "ptn_lv": ["XMP5|TECHLIB"],
    }
    fm["ddgoa_cmos_io|WckOscCore"] = {
        "ptn_lv": ["XMP0<15:0>|TECHLIB"],
    }
    fm["ddgoa_cmos_io|DqBufTop"] = {
        "DqDrv": ["I_DqDrv|ddgoa_cmos_io"],
        "DqRcv": ["I_DqRcv|ddgoa_cmos_io"],
    }
    fm["ddgoa_cmos_io|DqDrv"] = {
        "ptn_lv": ["XMP0<3:0>|TECHLIB"],
    }
    fm["ddgoa_cmos_io|DqRcv"] = {
        "ptn_lv": ["XMP6|TECHLIB"],
    }
    fm["TECHLIB|ptn_lv"] = {}  # leaf device
    return fm, "ptn_lv", "ddgoa_cmos_top|CHIP_TOP"


# ---------- reference candidate ----------
REF_CANDIDATE = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""xprobe_hier_gen.py - CrossProbe hierarchy CSV generator.

Reads a schematic hierarchy map (fullmap.json) and emits CrossProbe CSV rows
for every instance of a target device cell reachable from the root.

Modes:
  leaf   - one row per device instance (bus-expanded), hierPath includes device segment
  parent - one row per parent circuit instance (deduped), hierPath truncated at parent

CLI: python3 xprobe_hier_gen.py --fullmap <json> --seed <cell> --mode <leaf|parent> --out <csv>
"""
import argparse, csv, json, re, sys

HEADER = ["item", "hierPath", "dbType", "instName", "libName", "cellName",
          "viewName", "propertyName", "propertyValue", "findByProperty"]

def bus_expand(name):
    """Expand Verilog-style bus instance names.
    MP0<3:0> -> [MP0<0>, MP0<1>, MP0<2>, MP0<3>]
    MP0<1:0> -> [MP0<0>, MP0<1>]
    MP0<5>   -> [MP0<5>]
    MP1      -> [MP1]
    """
    m = re.match(r'^(.+)<(\d+):(\d+)>$', name)
    if m:
        base, hi, lo = m.group(1), int(m.group(2)), int(m.group(3))
        if hi >= lo:
            return ["%s<%d>" % (base, i) for i in range(lo, hi + 1)]
        else:
            return ["%s<%d>" % (base, i) for i in range(hi, lo + 1)]
    return [name]

def find_root(fullmap):
    """Root = cell not appearing as a child of any other cell."""
    child_cells = set()
    for pk, children in fullmap.items():
        for childcell in children:
            child_cells.add(childcell)
    for pk in fullmap:
        lib, cell = pk.split("|", 1)
        if cell not in child_cells:
            return pk
    return None

def build_ancestor_set(fullmap, seed):
    """Set of cell names that transitively contain seed."""
    child_to_parents = {}
    for pk, children in fullmap.items():
        lib_p, cell_p = pk.split("|", 1)
        for childcell in children:
            child_to_parents.setdefault(childcell, set()).add((lib_p, cell_p))
    direct = set()
    for pk, children in fullmap.items():
        if seed in children:
            lib_p, cell_p = pk.split("|", 1)
            direct.add(cell_p)
    ancestors = set(direct)
    queue = list(direct)
    while queue:
        cell = queue.pop()
        for (lib_p, cell_p) in child_to_parents.get(cell, set()):
            if cell_p not in ancestors:
                ancestors.add(cell_p)
                queue.append(cell_p)
    return ancestors

def dfs(fullmap, root_key, seed, ancestors, mode):
    rows = []
    def recurse(cell_key, path):
        lib_cur, cell_cur = cell_key.split("|", 1)
        children = fullmap.get(cell_key, {})
        for childcell, entries in children.items():
            if childcell == seed:
                for entry in entries:
                    if "|" in entry:
                        instname, childlib = entry.rsplit("|", 1)
                    else:
                        instname, childlib = entry, ""
                    if mode == "leaf":
                        for bn in bus_expand(instname):
                            hp = "/" + ".".join(["X" + s for s in path + [bn]])
                            rows.append((hp, "X" + bn, childlib, seed))
                    elif mode == "parent":
                        if not path:
                            continue
                        hp = "/" + ".".join(["X" + s for s in path])
                        rows.append((hp, "X" + path[-1], lib_cur, cell_cur))
            elif childcell in ancestors:
                for entry in entries:
                    if "|" in entry:
                        instname, childlib = entry.rsplit("|", 1)
                    else:
                        instname, childlib = entry, ""
                    child_key = childlib + "|" + childcell
                    recurse(child_key, path + [instname])
    recurse(root_key, [])
    if mode == "parent":
        seen = set(); uniq = []
        for r in rows:
            if r[0] not in seen:
                seen.add(r[0]); uniq.append(r)
        rows = uniq
    return rows

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fullmap", required=True)
    ap.add_argument("--seed", required=True)
    ap.add_argument("--mode", required=True, choices=["leaf", "parent"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    with open(args.fullmap) as f:
        fullmap = json.load(f)
    root_key = find_root(fullmap)
    if not root_key:
        sys.exit("ERROR: no root found")
    ancestors = build_ancestor_set(fullmap, args.seed)
    rows = dfs(fullmap, root_key, args.seed, ancestors, args.mode)
    with open(args.out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for i, (hp, inst, lib, cell) in enumerate(rows):
            w.writerow([i, hp, "inst", inst, lib, cell, "schematic",
                        "cellName", cell, "FindinstByCellName"])

if __name__ == "__main__":
    main()
'''

# ---------- check.py ----------
CHECK_PY = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""check.py for EDA-Eval-DesignFlow-XProbeHierGen-001.
Grades the candidate's xprobe_hier_gen.py on hidden fullmap_B.json.
15 independent conditions (a-o).
"""
import csv, io, json, os, re, shutil, subprocess, sys, tempfile, zipfile

CASE_ID = "EDA-Eval-DesignFlow-XProbeHierGen-001"
HEADER = ["item", "hierPath", "dbType", "instName", "libName", "cellName",
          "viewName", "propertyName", "propertyValue", "findByProperty"]

def _cond(label, ok, detail=""):
    if not ok:
        raise AssertionError("COND %s FAIL: %s" % (label, detail))

def _find_script(extract_dir):
    for root, _, files in os.walk(extract_dir):
        for fn in files:
            if fn.endswith(".py") and "xprobe" in fn.lower():
                return os.path.join(root, fn)
    # fallback: any .py
    for root, _, files in os.walk(extract_dir):
        for fn in files:
            if fn.endswith(".py"):
                return os.path.join(root, fn)
    return None

def _run_script(script, fullmap, seed, mode, out):
    return subprocess.run(
        [sys.executable, script, "--fullmap", fullmap, "--seed", seed,
         "--mode", mode, "--out", out],
        capture_output=True, text=True, timeout=120)

def _read_csv(path):
    with open(path, newline="") as f:
        rd = csv.reader(f)
        head = next(rd)
        rows = list(rd)
    return head, rows

def check(deliverable, workdir):
    # locate hidden B and A manifests relative to this check.py
    here = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.normpath(os.path.join(here, "..", "..", "assets", CASE_ID))
    fullmap_B = os.path.join(assets_dir, "hidden", "fullmap_B.json")
    fullmap_A = os.path.join(assets_dir, "fullmap_A.json")
    manifest_B = os.path.join(assets_dir, "hidden", "hidden_manifest.json")
    with open(manifest_B) as f:
        manifest = json.load(f)
    seed_B = manifest["seed_B"]
    seed_A = manifest["seed_A"]

    tmp = tempfile.mkdtemp(prefix="chk_xprobe_")
    try:
        # (a) deliverable is a valid zip with >=1 .py script
        _cond("a", zipfile.is_zipfile(deliverable), "not a zip")
        with zipfile.ZipFile(deliverable) as z:
            names = z.namelist()
            _cond("a", len(names) >= 1, "zip empty")
            z.extractall(tmp)
        script = _find_script(tmp)
        _cond("a", script is not None, "no .py script in zip")

        # (b) py_compile passes
        r = subprocess.run([sys.executable, "-m", "py_compile", script],
                           capture_output=True, text=True, timeout=60)
        _cond("b", r.returncode == 0, "py_compile failed: %s" % r.stderr)

        # (c) leaf mode subprocess exits 0 on B
        out_leaf_B = os.path.join(tmp, "leaf_B.csv")
        r = _run_script(script, fullmap_B, seed_B, "leaf", out_leaf_B)
        _cond("c", r.returncode == 0 and os.path.exists(out_leaf_B),
              "leaf B run rc=%d stderr=%s" % (r.returncode, r.stderr[:400]))

        head, rows = _read_csv(out_leaf_B)
        # (d) header exact 10 cols
        _cond("d", head == HEADER, "header mismatch: %s" % head)

        # (e) leaf B row count == expected (bus-expanded)
        expected_leaf_B = manifest["expected_leaf_B"]
        _cond("e", len(rows) == expected_leaf_B,
              "leaf B rows=%d expected=%d" % (len(rows), expected_leaf_B))

        # (f) every hierPath starts with / and every segment starts with X
        bad_hp = 0
        for row in rows:
            hp = row[1]
            if not hp.startswith("/"):
                bad_hp += 1; continue
            segs = hp.strip("/").split(".")
            if any(not s.startswith("X") for s in segs):
                bad_hp += 1
        _cond("f", bad_hp == 0, "%d bad hierPath rows" % bad_hp)

        # (g) leaf instName == last hierPath segment (X-prefixed)
        mism = 0
        for row in rows:
            hp = row[1]; inst = row[3]
            last = hp.strip("/").split(".")[-1]
            if inst != last:
                mism += 1
        _cond("g", mism == 0, "%d instName!=lastSeg rows" % mism)

        # (h) leaf all rows have cellName == seed_B and libName == TECHLIB
        bad_cell = 0
        for row in rows:
            if row[4] != "TECHLIB" or row[5] != seed_B:
                bad_cell += 1
        _cond("h", bad_cell == 0, "%d rows cellName/libName wrong" % bad_cell)

        # (i) bus expansion: leaf B contains expanded bus bits (e.g. <0>,<1>,...)
        bus_bits = set()
        for row in rows:
            m = re.search(r'<(\d+)>', row[3])
            if m:
                bus_bits.add((re.sub(r'<\d+>$', '', row[3]), m.group(1)))
        _cond("i", len(bus_bits) >= 8,
              "bus expansion too few distinct bits=%d" % len(bus_bits))

        # (j) parent mode subprocess exits 0 on B
        out_par_B = os.path.join(tmp, "parent_B.csv")
        r = _run_script(script, fullmap_B, seed_B, "parent", out_par_B)
        _cond("j", r.returncode == 0 and os.path.exists(out_par_B),
              "parent B run rc=%d stderr=%s" % (r.returncode, r.stderr[:400]))

        headp, rowsp = _read_csv(out_par_B)
        # (k) parent B row count < leaf B row count (deduped)
        _cond("k", len(rowsp) < len(rows),
              "parent=%d not < leaf=%d" % (len(rowsp), len(rows)))
        expected_par_B = manifest["expected_parent_B"]
        _cond("k", len(rowsp) == expected_par_B,
              "parent B rows=%d expected=%d" % (len(rowsp), expected_par_B))

        # (l) parent hierPath never ends with a bus/bit device segment:
        # the last segment must be a circuit instance (XI_...), not a device (XMP...)
        bad_parent_end = 0
        for row in rowsp:
            last = row[1].strip("/").split(".")[-1]
            # device segments look like XMP<...> or XMPn; circuit segments look like XI_...
            if not last.startswith("XI_"):
                bad_parent_end += 1
        _cond("l", bad_parent_end == 0, "%d parent rows end with device seg" % bad_parent_end)

        # (m) parent instName == last hierPath segment
        mism_p = 0
        for row in rowsp:
            last = row[1].strip("/").split(".")[-1]
            if row[3] != last:
                mism_p += 1
        _cond("m", mism_p == 0, "%d parent instName!=lastSeg" % mism_p)

        # (n) parent cellName != seed_B (it is the parent circuit cell name)
        bad_pc = 0
        for row in rowsp:
            if row[5] == seed_B:
                bad_pc += 1
        _cond("n", bad_pc == 0, "%d parent rows have cellName==seed" % bad_pc)

        # (o) cross-input guard + 3-seed determinism:
        # run on A with seed_A -> results differ from B (not hardcoded to B);
        # 3 runs of B leaf identical
        out_leaf_A = os.path.join(tmp, "leaf_A.csv")
        r = _run_script(script, fullmap_A, seed_A, "leaf", out_leaf_A)
        _cond("o", r.returncode == 0 and os.path.exists(out_leaf_A),
              "leaf A run rc=%d" % r.returncode)
        _, rowsA = _read_csv(out_leaf_A)
        expected_leaf_A = manifest["expected_leaf_A"]
        _cond("o", len(rowsA) == expected_leaf_A,
              "leaf A rows=%d expected=%d (hardcoded to B?)" % (len(rowsA), expected_leaf_A))
        # determinism: 3 runs of B leaf with shuffled temp paths
        hashes = set()
        for trial in range(3):
            out_det = os.path.join(tmp, "det_%d.csv" % trial)
            r = _run_script(script, fullmap_B, seed_B, "leaf", out_det)
            _cond("o", r.returncode == 0, "det run %d rc=%d" % (trial, r.returncode))
            with open(out_det, "rb") as f:
                hashes.add(hashlib.md5(f.read()).hexdigest())
        _cond("o", len(hashes) == 1, "3-seed determinism: %d distinct hashes" % len(hashes))

        return {"status": "PASS", "conditions": 15,
                "leaf_B_rows": len(rows), "parent_B_rows": len(rowsp)}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        result = check(sys.argv[1], sys.argv[2])
        print(json.dumps(result, indent=2))
    else:
        print("usage: check.py <deliverable.zip> <workdir>")
'''

# ---------- negatives ----------
NEG_HARDCODE_A = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""neg_hardcode_A: hardcodes A's seed/structure, fails on B."""
import argparse, csv, json, sys
HEADER = ["item","hierPath","dbType","instName","libName","cellName","viewName","propertyName","propertyValue","findByProperty"]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fullmap",required=True); ap.add_argument("--seed",required=True)
    ap.add_argument("--mode",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    # ignore args, hardcode A's tree output (ptn_lvio, 18 leaf rows)
    rows=[
        ("/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<0>","XMP0<0>","TECHLIB","ptn_lvio"),
        ("/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<1>","XMP0<1>","TECHLIB","ptn_lvio"),
        ("/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<2>","XMP0<2>","TECHLIB","ptn_lvio"),
        ("/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP0<3>","XMP0<3>","TECHLIB","ptn_lvio"),
        ("/XI_C_Top.XI_Array16GTop.XI_Array8G_E.XI_VblhDigDrvIPTop.XI_VblhDigDrvCmpIP_2.XMP1","XMP1","TECHLIB","ptn_lvio"),
    ]
    with open(args.out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(HEADER)
        for i,(hp,inst,lib,cell) in enumerate(rows):
            w.writerow([i,hp,"inst",inst,lib,cell,"schematic","cellName",cell,"FindinstByCellName"])
if __name__=="__main__": main()
'''

NEG_DROP_PARENT = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""neg_drop_parent: parent mode just truncates last segment but keeps device cellName."""
import argparse, csv, json, re, sys
HEADER = ["item","hierPath","dbType","instName","libName","cellName","viewName","propertyName","propertyValue","findByProperty"]
def bus_expand(n):
    m=re.match(r'^(.+)<(\d+):(\d+)>$',n)
    if m:
        b,hi,lo=m.group(1),int(m.group(2)),int(m.group(3))
        return ["%s<%d>"%(b,i) for i in (range(lo,hi+1) if hi>=lo else range(hi,lo+1))]
    return [n]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fullmap",required=True); ap.add_argument("--seed",required=True)
    ap.add_argument("--mode",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    fm=json.load(open(args.fullmap))
    # find root
    child=set()
    for pk,ch in fm.items():
        for c in ch: child.add(c)
    root=None
    for pk in fm:
        if pk.split("|",1)[1] not in child: root=pk
    # ancestor set
    c2p={}
    for pk,ch in fm.items():
        lp,cp=pk.split("|",1)
        for c in ch: c2p.setdefault(c,set()).add((lp,cp))
    direct=set()
    for pk,ch in fm.items():
        if args.seed in ch: direct.add(pk.split("|",1)[1])
    anc=set(direct); q=list(direct)
    while q:
        c=q.pop()
        for (lp,cp) in c2p.get(c,set()):
            if cp not in anc: anc.add(cp); q.append(cp)
    rows=[]
    def rec(ck,path):
        lc,cc=ck.split("|",1)
        for ch,entries in fm.get(ck,{}).items():
            if ch==args.seed:
                for e in entries:
                    iname,cl=e.rsplit("|",1)
                    if args.mode=="leaf":
                        for bn in bus_expand(iname):
                            hp="/"+ ".".join(["X"+s for s in path+[bn]])
                            rows.append((hp,"X"+bn,cl,args.seed))
                    else:
                        hp="/"+ ".".join(["X"+s for s in path])
                        # BUG: keeps seed as cellName (should be parent circuit cell)
                        rows.append((hp,"X"+path[-1] if path else "XROOT",cl,args.seed))
            elif ch in anc:
                for e in entries:
                    iname,cl=e.rsplit("|",1)
                    rec(cl+"|"+ch, path+[iname])
    rec(root,[])
    if args.mode=="parent":
        seen=set(); uniq=[]
        for r in rows:
            if r[0] not in seen: seen.add(r[0]); uniq.append(r)
        rows=uniq
    with open(args.out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(HEADER)
        for i,(hp,inst,lib,cell) in enumerate(rows):
            w.writerow([i,hp,"inst",inst,lib,cell,"schematic","cellName",cell,"FindinstByCellName"])
if __name__=="__main__": main()
'''

NEG_PRINT_ONLY = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""neg_print_only: prints expected-looking CSV but ignores input fullmap entirely."""
import argparse, csv, sys
HEADER = ["item","hierPath","dbType","instName","libName","cellName","viewName","propertyName","propertyValue","findByProperty"]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fullmap",required=True); ap.add_argument("--seed",required=True)
    ap.add_argument("--mode",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    # always print a plausible-looking 3-row leaf CSV regardless of input
    rows=[
        ("/XI_Fake.XI_Block.XMP0<0>","XMP0<0>","TECHLIB",args.seed),
        ("/XI_Fake.XI_Block.XMP0<1>","XMP0<1>","TECHLIB",args.seed),
        ("/XI_Fake.XI_Block.XMP1","XMP1","TECHLIB",args.seed),
    ]
    with open(args.out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(HEADER)
        for i,(hp,inst,lib,cell) in enumerate(rows):
            w.writerow([i,hp,"inst",inst,lib,cell,"schematic","cellName",cell,"FindinstByCellName"])
if __name__=="__main__": main()
'''

NEG_EMPTY = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""neg_empty: writes only the header, no data rows."""
import argparse, csv, sys
HEADER = ["item","hierPath","dbType","instName","libName","cellName","viewName","propertyName","propertyValue","findByProperty"]
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--fullmap",required=True); ap.add_argument("--seed",required=True)
    ap.add_argument("--mode",required=True); ap.add_argument("--out",required=True)
    args=ap.parse_args()
    with open(args.out,"w",newline="") as f:
        w=csv.writer(f); w.writerow(HEADER)
if __name__=="__main__": main()
'''

NEG_SELTEST = r'''#!/usr/bin/env python3
# -*- coding: ascii -*-
"""negative_selftest.py — run check.py against all negatives + 3 fakes; expect ALL FAIL."""
import json, os, shutil, subprocess, sys, tempfile, zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_ID = "EDA-Eval-DesignFlow-XProbeHierGen-001"
REF_DIR = os.path.normpath(os.path.join(HERE, ".."))
CHECK = os.path.join(REF_DIR, "check.py")
ASSETS = os.path.normpath(os.path.join(REF_DIR, "..", "..", "assets", CASE_ID))

def make_zip(script_path, tmp):
    z = os.path.join(tmp, "submit.zip")
    with zipfile.ZipFile(z, "w") as zf:
        zf.write(script_path, os.path.basename(script_path))
    return z

def run_check(submit_zip):
    workdir = tempfile.mkdtemp(prefix="negtest_")
    try:
        r = subprocess.run([sys.executable, CHECK, submit_zip, workdir],
                           capture_output=True, text=True, timeout=180)
        return r.returncode, r.stdout, r.stderr
    finally:
        shutil.rmtree(workdir, ignore_errors=True)

def main():
    results = {}
    # negatives
    for fn in sorted(os.listdir(HERE)):
        if fn.startswith("neg_") and fn.endswith(".py") and fn != "negative_selftest.py":
            tmp = tempfile.mkdtemp(prefix="neg_%s_" % fn)
            try:
                z = make_zip(os.path.join(HERE, fn), tmp)
                rc, out, err = run_check(z)
                results[fn] = (rc != 0)
            finally:
                shutil.rmtree(tmp, ignore_errors=True)
    # 3 fakes
    fakes = {"fake_empty.py": None, "fake_print_only.py": None, "fake_core_deleted.py": None}
    for fk in fakes:
        p = os.path.join(HERE, fk)
        if not os.path.exists(p):
            continue
        tmp = tempfile.mkdtemp(prefix="fake_%s_" % fk)
        try:
            z = make_zip(p, tmp)
            rc, out, err = run_check(z)
            results[fk] = (rc != 0)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    all_fail = all(v for v in results.values())
    print("NEG_RESULTS:", json.dumps(results, indent=2))
    print("ALL_FAIL:", all_fail)
    if not all_fail:
        sys.exit(1)

if __name__ == "__main__":
    main()
'''

TASK_BRIEF = """# CrossProbe 层级 CSV 生成器

## 交付接口
- 入口：`outputs/submit.zip`（内含你的 `xprobe_hier_gen.py` 脚本）
- 脚本 CLI：`python3 xprobe_hier_gen.py --fullmap <fullmap.json> --seed <cell> --mode <leaf|parent> --out <out.csv>`

## 输入
- `assets/fullmap_A.json`：原理图层级映射（示例），格式 `{"lib|parentcell": {"childcell": ["instname|childlib", ...]}}`
  - 器件实例名可能含 Verilog 总线区间（如 `MP0<3:0>` → 4 位展开）
- 隐藏输入 B 结构与 A 不同（不同 root / seed / 层级 / 总线），判分只跑 B

## 输出 CSV（10 列，表头原样）
`item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty`

## 两种模式
- `leaf`：每个器件实例一行（总线逐位展开），hierPath 含器件实例段，cellName=器件名
- `parent`：每个直接例化器件的父电路实例一行（同父实例多器件去重），hierPath 截止父电路实例，cellName=父电路名

## hierPath 规则
- 以 `/` 开头，每段为 `X` + 实例名（如实例 `I_C_Top` → 段 `XI_C_Top`）
- 段间用 `.` 连接
- leaf：末段为器件实例（`XMP0<0>`）；parent：末段为父电路实例（`XI_VblhDigDrvCmpIP_2`），不含器件段
"""


def compute_expected(fm, seed, mode):
    """Run the reference logic to compute expected row count."""
    sys.path.insert(0, "/tmp/_xprobe_ref")
    # inline the reference logic
    import re
    def bus_expand(name):
        m = re.match(r'^(.+)<(\d+):(\d+)>$', name)
        if m:
            base, hi, lo = m.group(1), int(m.group(2)), int(m.group(3))
            if hi >= lo:
                return ["%s<%d>" % (base, i) for i in range(lo, hi + 1)]
            else:
                return ["%s<%d>" % (base, i) for i in range(hi, lo + 1)]
        return [name]
    child_cells = set()
    for pk, ch in fm.items():
        for c in ch:
            child_cells.add(c)
    root = None
    for pk in fm:
        if pk.split("|", 1)[1] not in child_cells:
            root = pk; break
    c2p = {}
    for pk, ch in fm.items():
        lp, cp = pk.split("|", 1)
        for c in ch:
            c2p.setdefault(c, set()).add((lp, cp))
    direct = set()
    for pk, ch in fm.items():
        if seed in ch:
            direct.add(pk.split("|", 1)[1])
    anc = set(direct); q = list(direct)
    while q:
        c = q.pop()
        for (lp, cp) in c2p.get(c, set()):
            if cp not in anc:
                anc.add(cp); q.append(cp)
    rows = []
    def rec(ck, path):
        lc, cc = ck.split("|", 1)
        for ch, entries in fm.get(ck, {}).items():
            if ch == seed:
                for e in entries:
                    iname, cl = e.rsplit("|", 1)
                    if mode == "leaf":
                        for bn in bus_expand(iname):
                            hp = "/" + ".".join(["X" + s for s in path + [bn]])
                            rows.append((hp, "X" + bn, cl, seed))
                    else:
                        if not path:
                            continue
                        hp = "/" + ".".join(["X" + s for s in path])
                        rows.append((hp, "X" + path[-1], lc, cc))
            elif ch in anc:
                for e in entries:
                    iname, cl = e.rsplit("|", 1)
                    rec(cl + "|" + ch, path + [iname])
    rec(root, [])
    if mode == "parent":
        seen = set(); uniq = []
        for r in rows:
            if r[0] not in seen:
                seen.add(r[0]); uniq.append(r)
        rows = uniq
    return rows


def main():
    fmA, seedA, rootA = build_fullmap_A()
    fmB, seedB, rootB = build_fullmap_B()
    leafA = compute_expected(fmA, seedA, "leaf")
    parA = compute_expected(fmA, seedA, "parent")
    leafB = compute_expected(fmB, seedB, "leaf")
    parB = compute_expected(fmB, seedB, "parent")
    print("A: leaf=%d parent=%d  B: leaf=%d parent=%d" % (
        len(leafA), len(parA), len(leafB), len(parB)))

    # write assets
    with open(os.path.join(ASETS, "fullmap_A.json"), "w") as f:
        json.dump(fmA, f, indent=1, ensure_ascii=False)
    with open(os.path.join(HIDDEN, "fullmap_B.json"), "w") as f:
        json.dump(fmB, f, indent=1, ensure_ascii=False)
    manifest = {
        "seed_A": seedA, "root_A": rootA,
        "seed_B": seedB, "root_B": rootB,
        "expected_leaf_A": len(leafA), "expected_parent_A": len(parA),
        "expected_leaf_B": len(leafB), "expected_parent_B": len(parB),
    }
    with open(os.path.join(HIDDEN, "hidden_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2)
    with open(os.path.join(ASETS, "task_brief.md"), "w") as f:
        f.write(TASK_BRIEF)

    # write reference candidate + check + negatives
    with open(os.path.join(REF, "xprobe_hier_gen_ref.py"), "w") as f:
        f.write(REF_CANDIDATE)
    with open(os.path.join(REF, "check.py"), "w") as f:
        f.write(CHECK_PY)
    for fn, content in [
        ("neg_hardcode_a.py", NEG_HARDCODE_A),
        ("neg_drop_parent.py", NEG_DROP_PARENT),
        ("neg_print_only.py", NEG_PRINT_ONLY),
        ("neg_empty.py", NEG_EMPTY),
        ("negative_selftest.py", NEG_SELTEST),
    ]:
        with open(os.path.join(NEG, fn), "w") as f:
            f.write(content)

    # 3 fakes (§4.9): empty, print-only, core-deleted
    # fake_empty = neg_empty (same effect); write separate copies
    shutil.copy(os.path.join(NEG, "neg_empty.py"), os.path.join(NEG, "fake_empty.py"))
    shutil.copy(os.path.join(NEG, "neg_print_only.py"), os.path.join(NEG, "fake_print_only.py"))
    # fake_core_deleted: ref with DFS emission stripped (no rows ever emitted)
    core_del = REF_CANDIDATE.replace(
        'rows.append((hp, "X" + bn, childlib, seed))',
        'pass  # core deleted: no leaf emission'
    ).replace(
        'rows.append((hp, "X" + path[-1], lib_cur, cell_cur))',
        'pass  # core deleted: no parent emission'
    )
    with open(os.path.join(NEG, "fake_core_deleted.py"), "w") as f:
        f.write(core_del)

    # build reference_submit.zip
    ref_script = os.path.join(REF, "xprobe_hier_gen_ref.py")
    zip_path = os.path.join(REF, "reference_submit.zip")
    if os.path.exists(zip_path):
        os.remove(zip_path)
    with zipfile.ZipFile(zip_path, "w") as z:
        z.write(ref_script, "xprobe_hier_gen.py")

    print("Wrote assets to", ASETS)
    print("Wrote reference to", REF)
    print("manifest:", json.dumps(manifest))


if __name__ == "__main__":
    main()
