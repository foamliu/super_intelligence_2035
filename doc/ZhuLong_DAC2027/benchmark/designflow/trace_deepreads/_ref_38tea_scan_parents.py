#!/usr/bin/env python3
# -*- coding: ascii -*-
"""scan_parents.py (Run inside the pyAether sandbox ONLY)

Read a parent-cell task list and, for each, open its schematic and dump
header cell -> [instance names] into fullmap.json (incremental merge).

Input task list: lines of "lib|cell" (the parent cells we care about),
or a JSON array of [lib, cell].
Usage:
  python3 scan_parents.py tasks.txt [start] [end] [fullmap.json]

Chunking [start:end] keeps each pyAether invocation under the 30s sandbox limit
(batch ~200 cells / call). Merge is incremental, so call repeatedly over ranges.
"""
import os, sys, json

def load_tasks(path):
    if path.endswith(".json"):
        data = json.load(open(path))
        return [ (x[0], x[1]) for x in data ]
    tasks = []
    for ln in open(path):
        ln = ln.strip()
        if not ln:
            continue
        if "|" in ln:
            lib, cell = ln.split("|", 1)
            tasks.append((lib, cell))
        elif "/" in ln:
            lib, cell = ln.split("/", 1)
            tasks.append((lib, cell))
    return tasks

def extract_inst_names(cv, seeds=None):
    import pyAether as ae
    holder = ae.emyArray_p_emyInstHeader()
    if not cv:
        return {}
    try:
        ae.emyGetAllInstHeaders(cv, ae.EMY_GET_INST_HEADER_TYPE_ALL, holder, ae.emyString("x"))
    except Exception:
        return {}
    m = {}
    for i in range(len(holder)):
        h = holder[i]
        try:
            cl = str(getattr(h, "cellName", None) or "")
        except Exception:
            continue
        if not cl:
            continue
        if seeds and cl not in seeds:
            continue
        names = []
        try:
            insts = h.getInsts()
        except Exception:
            insts = []
        for it in (insts or []):
            nm = getattr(it, "name", None)
            if nm is None:
                for mk in ("getName", "getInstName"):
                    if hasattr(it, mk):
                        try:
                            nm = getattr(it, mk)(); break
                        except Exception:
                            pass
            if nm:
                names.append(str(nm))
        if names:
            m.setdefault(cl, []).extend(names)
    return m

def main():
    import pyAether as ae
    taskfile = sys.argv[1]
    start = int(sys.argv[2]) if len(sys.argv) > 2 else 0
    end = int(sys.argv[3]) if len(sys.argv) > 3 else 10 ** 9
    out = sys.argv[4] if len(sys.argv) > 4 else "fullmap.json"
    tasks = load_tasks(taskfile)
    res = json.load(open(out)) if os.path.isfile(out) else {}
    added = 0
    for lib, parent in tasks[start:end]:
        try:
            cv = ae.dbOpenCVByType(lib, parent, "schematic")
        except Exception:
            continue
        m = extract_inst_names(cv)
        tm = {c: v for c, v in m.items() if c != parent}
        if tm:
            res[lib + "|" + parent] = tm
            added += 1
    json.dump(res, open(out, "w"))
    print("scan [%d:%d] added=%d  total_keys=%d" % (start, end, added, len(res)))

if __name__ == "__main__":
    main()
