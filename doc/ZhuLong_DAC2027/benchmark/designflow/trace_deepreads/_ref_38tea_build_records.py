#!/usr/bin/env python3
# -*- coding: ascii -*-
"""build_records.py - Assembly step (run in normal Python, NOT the pyAether sandbox).

Read fullmap.json (from scan_parents.py) + parameters, then emit the cross-probe CSV:
  item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty

Example:
  python3 build_records.py --fullmap fullmap.json --libs-file scmos_master.txt \
      --name-pattern scmos --chip-root LP5TOP --top-instance I_C_Top \
      --drop-layer LP5TOP --prefix X --inst-policy numbered_only --bus-expand \
      --out DDGOA_V0_SCMOS_records.csv
"""
import os, re, sys, json, argparse
from collections import defaultdict, deque

HEADER = "item,hierPath,dbType,instName,libName,cellName,viewName,propertyName,propertyValue,findByProperty"

def parse_args():
    p = argparse.ArgumentParser(add_help=True)
    p.add_argument("--fullmap", required=True, help="fullmap.json from scan_parents.py")
    p.add_argument("--libs-file", help="file of 'lib/cell' lines; gives seeds + lib mapping")
    p.add_argument("--name-pattern", default="scmos", help="regex for circuit-family seed cell names")
    p.add_argument("--chip-root", default="LP5TOP", help="chip core root cell (scope top)")
    p.add_argument("--top-instance", default="I_C_Top", help="top instance label in hierPath")
    p.add_argument("--drop-layer", help="layer/instance dropped from path (e.g. LP5TOP)")
    p.add_argument("--prefix", default="X", help="prefix prepended to every path instance name")
    p.add_argument("--inst-policy", choices=["numbered_only", "keep_all"], default="keep_all",
                   help="numbered_only: keep only I<digits>/I<digits><bus>, drop CDF I_<cell> & ...buf")
    p.add_argument("--bus-expand", action="store_true", help="expand I<n:a:b> into per-bit instances")
    p.add_argument("--out", required=True, help="output CSV path")
    return p.parse_args()

LEAF_RE = re.compile(r'^I\d+(<(\d+):(\d+)>)?$')

def candidate_names(raw, policy):
    return [raw] if policy != "numbered_only" or LEAF_RE.match(raw) else []

def bus_expand(names):
    out = []
    for nm in names:
        m = re.fullmatch(r'^I(\d+)<(\d+):(\d+)>$', nm)
        if not m:
            out.append(nm); continue
        base = "I" + m.group(1); a = int(m.group(2)); b = int(m.group(3))
        rng = range(b, a + 1) if a >= b else range(a, b + 1)
        out += ["%s<%d>" % (base, v) for v in rng]
    return out

def main():
    a = parse_args()
    fullmap = json.load(open(a.fullmap))

    pm = defaultdict(dict)
    for pk, m in fullmap.items():
        pn = pk.split("|")[1]
        for child, names in m.items():
            pm[pn].setdefault(child, []).extend(names)
    for pn in list(pm):
        for child in list(pm[pn]):
            seen = set(); out = []
            for x in pm[pn][child]:
                if x not in seen:
                    seen.add(x); out.append(x)
            pm[pn][child] = out

    lib_of = {}
    seeds = set()
    pat = re.compile(a.name_pattern, re.I)
    if a.libs_file:
        for ln in open(a.libs_file):
            ln = ln.strip()
            if "/" in ln:
                lib, cell = ln.split("/", 1)
                if cell not in lib_of:
                    lib_of[cell] = lib
                if pat.search(cell):
                    seeds.add(cell)

    ROOT = a.chip_root
    prev = {}; instOf = {}
    prev[ROOT] = None; instOf[ROOT] = ROOT
    q = deque([ROOT])
    while q:
        p = q.popleft()
        for child, names in pm.get(p, {}).items():
            if child == p:
                continue
            if child not in prev:
                prev[child] = p; instOf[child] = names[0]; q.append(child)

    def chain_to(node):
        segs = []; cur = node
        while cur is not None and cur != ROOT:
            segs.append(instOf[cur]); cur = prev.get(cur)
        segs.reverse(); return segs

    def pre(x):
        return (a.prefix + x) if (a.prefix and x) else x

    top = pre(a.top_instance)
    rows = []; seen_paths = set()
    for p in list(pm):
        if p not in prev:
            continue
        anc = chain_to(p)
        if a.drop_layer:
            anc = [s for s in anc if (s != a.drop_layer and s.lstrip(a.prefix or "") != a.drop_layer)]
        for s, names in pm[p].items():
            if s not in seeds:
                continue
            lib = lib_of.get(s, "")
            pool = []
            for raw in names:
                pool += candidate_names(raw, a.inst_policy)
            if a.bus_expand:
                pool = bus_expand(pool)
            for ln in pool:
                hp = "/" + top + "."
                hp += ".".join([pre(x) for x in anc] + [pre(ln)])
                key = (hp, ln, s)
                if key in seen_paths:
                    continue
                seen_paths.add(key)
                rows.append([len(rows), hp, "inst", pre(ln), lib, s,
                             "schematic", "cellName", s, "FindinstByCellName"])

    rows.sort(key=lambda r: r[1])
    rows = [[i] + r[1:] for i, r in enumerate(rows)]

    with open(a.out, "w") as f:
        f.write(HEADER + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")
    print("wrote %s : %d rows, distinct scmos %d" %
          (a.out, len(rows), len(set(r[5] for r in rows))))

if __name__ == "__main__":
    main()
