#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""build_negatives.py - generate negative stubs + negative_selftest.py for
EDA-Eval-DesignFlow-FarthestCellPick-001. Each negative must FAIL check();
the selftest asserts all negatives FAIL and the reference PASSes."""
import os, textwrap, subprocess, sys, importlib.util

NEG_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-FarthestCellPick-001/negative"
os.makedirs(NEG_DIR, exist_ok=True)

# --- reference expected (B/A/B2) literals, for crafting negatives ---
# A: Xfar_B / CC_far_B / WL_far_B / cumR=35 / tier B / far
# B: Xnear_M / CC_near_M / WL_near_M / cumR=46 / tier M / near
# B2: Xfar_T / CC_far_T / WL_far_T / cumR=44 / tier T / far

negatives = {}

negatives["empty_shell.py"] = '''#!/usr/bin/env python3
import sys
# does nothing
pass
'''

negatives["syntax_err.py"] = '''#!/usr/bin/env python3
def broken(
    # syntax error
'''

negatives["no_output.py"] = '''#!/usr/bin/env python3
import sys
def main():
    pass
if __name__ == "__main__":
    main()
'''

negatives["print_a.py"] = '''#!/usr/bin/env python3
# hardcoded A answer regardless of input -> fails on B (B inst missing) + k (A literal in source)
import sys
report = """Farthest-Cell Analysis Report
instance        : Xfar_B
subckt          : kcellx1mdl_B
tier            : B
column          : far
cumulative BL R : 35
measurement node: CC_far_B
WL trigger net  : WL_far_B
"""
if len(sys.argv) > 2 and sys.argv[2] == "--out":
    with open(sys.argv[3], "w") as f:
        f.write(report)
else:
    sys.stdout.write(report)
'''

negatives["hardcode_b.py"] = '''#!/usr/bin/env python3
# hardcoded B answer -> fails k (A inst missing) and l (B2 wrong) ; source has B2-free but B literal? B inst Xnear_M not in source banned list (only A/B2 cc/wl/inst banned) -> still fails k because A inst Xfar_B not in A report
import sys
report = """Farthest-Cell Analysis Report
instance        : Xnear_M
subckt          : kcellx1mdl_M
tier            : M
column          : near
cumulative BL R : 46
measurement node: CC_near_M
WL trigger net  : WL_near_M
"""
if len(sys.argv) > 2 and sys.argv[2] == "--out":
    with open(sys.argv[3], "w") as f:
        f.write(report)
else:
    sys.stdout.write(report)
'''

negatives["static_last.py"] = '''#!/usr/bin/env python3
# picks the LAST target-cell line textually (no cumulative R computation) -> fails e/d on B
import sys, re
def main(nl, out):
    with open(nl) as f:
        lines = f.readlines()
    last = None
    for line in lines:
        if re.match(r"^X\\w+\\s+", line) and "kcellx1mdl_" in line:
            parts = line.split()
            last = parts
    if last is None:
        return
    inst = last[0]; subckt = last[-1]; ports = last[1:-1]
    rep = "instance: %s\\nsubckt: %s\\ntier: %s\\ncumulative BL R: 999\\nmeasurement node: %s\\nWL trigger net: %s\\ncolumn: far\\n" % (
        inst, subckt, subckt.replace("kcellx1mdl_",""), ports[2] if len(ports)>2 else "?", ports[1] if len(ports)>1 else "?")
    if out:
        with open(out, "w") as f: f.write(rep)
    else:
        sys.stdout.write(rep)
if __name__ == "__main__":
    args = sys.argv
    nl = args[1]; out = None
    if "--out" in args: out = args[args.index("--out")+1]
    main(nl, out)
'''

negatives["pick_load.py"] = '''#!/usr/bin/env python3
# names an RC-load decoy as farthest -> fails j
import sys, re
def main(nl, out):
    with open(nl) as f:
        text = f.read()
    m = re.search(r"^(Xload\\d+)\\s+", text, re.M)
    inst = m.group(1) if m else "Xload0"
    rep = "Farthest cell: %s\\ncumulative BL R: 100\\nmeasurement node: CC_load\\nWL trigger net: WL_load\\ncolumn: far\\nsubckt: kcellx32BGmdl_Load\\n" % inst
    if out:
        with open(out, "w") as f: f.write(rep)
    else:
        sys.stdout.write(rep)
if __name__ == "__main__":
    args = sys.argv; nl = args[1]; out = None
    if "--out" in args: out = args[args.index("--out")+1]
    main(nl, out)
'''

negatives["ref_core_deleted.py"] = '''#!/usr/bin/env python3
# gold structure but cumulative-R BFS removed -> picks FIRST target cell -> fails d/e on B
import sys, re
def main(nl, out):
    with open(nl) as f:
        text = f.read()
    first = None
    for line in text.splitlines():
        if line.startswith("X") and "kcellx1mdl_" in line:
            parts = line.split()
            first = parts; break
    if first is None: return
    inst = first[0]; subckt = first[-1]; ports = first[1:-1]
    tier = subckt.replace("kcellx1mdl_","")
    col = "near" if "near" in inst.lower() else "far"
    rep = "instance: %s\\nsubckt: %s\\ntier: %s\\ncumulative BL R: 1\\nmeasurement node: %s\\nWL trigger net: %s\\ncolumn: %s\\n" % (
        inst, subckt, tier, ports[2], ports[1], col)
    if out:
        with open(out, "w") as f: f.write(rep)
    else:
        sys.stdout.write(rep)
if __name__ == "__main__":
    args = sys.argv; nl = args[1]; out = None
    if "--out" in args: out = args[args.index("--out")+1]
    main(nl, out)
'''

negatives["hardcoded_path.py"] = '''#!/usr/bin/env python3
# hardcodes "netlist.sp" input filename -> fails m
import sys
def main():
    with open("netlist.sp") as f:
        text = f.read()
    rep = "instance: Xfar_B\\ncumulative BL R: 35\\nmeasurement node: CC_far_B\\nWL trigger net: WL_far_B\\ncolumn: far\\nsubckt: kcellx1mdl_B\\n"
    sys.stdout.write(rep)
if __name__ == "__main__":
    main()
'''

negatives["wrong_node.py"] = '''#!/usr/bin/env python3
# computes correct farthest but reports WRONG measurement node -> fails g
import sys, re, collections
def rval(t):
    m=re.match(r"^([0-9.]+)$", t.strip())
    return float(m.group(1)) if m else 0.0
def main(nl, out):
    with open(nl) as f: text=f.read()
    sa=None; edges=[]; targets=[]
    in_sub=False
    for raw in text.splitlines():
        line=raw.strip()
        if not line or line.startswith("*"): continue
        up=line.upper()
        if up.startswith(".SUBCKT"): in_sub=True; continue
        if up.startswith(".ENDS"): in_sub=False; continue
        if in_sub: continue
        if line.startswith("X") and re.match(r"^X\\w+",line):
            parts=line.split(); subckt=parts[-1]; ports=parts[1:-1]
            if subckt=="SA_unit" and sa is None and ports: sa=ports[0]
            elif subckt.startswith("kcellx1mdl_"):
                targets.append(dict(inst=parts[0],bl=ports[0],wl=ports[1],cc=ports[2],subckt=subckt,tier=subckt.replace("kcellx1mdl_","")))
            continue
        if line.startswith("R") and re.match(r"^R\\w+",line):
            parts=line.split()
            if len(parts)>=4: edges.append((parts[1],parts[2],rval(parts[3])))
    adj=collections.defaultdict(list)
    for n1,n2,v in edges: adj[n1].append((n2,v)); adj[n2].append((n1,v))
    cum={sa:0.0}; q=collections.deque([sa])
    while q:
        n=q.popleft()
        for nb,v in adj[n]:
            if nb not in cum: cum[nb]=cum[n]+v; q.append(nb)
    best=None
    for c in targets:
        c["cumR"]=cum.get(c["bl"],-1)
        if best is None or c["cumR"]>best["cumR"]: best=c
    col="near" if "near" in best["inst"].lower() else "far"
    # WRONG measurement node: report a different CC
    wrong_cc = "CC_WRONG_NODE"
    rep="instance: %s\\nsubckt: %s\\ntier: %s\\ncumulative BL R: %g\\nmeasurement node: %s\\nWL trigger net: %s\\ncolumn: %s\\n" % (
        best["inst"], best["subckt"], best["tier"], best["cumR"], wrong_cc, best["wl"], col)
    if out:
        with open(out,"w") as f: f.write(rep)
    else: sys.stdout.write(rep)
if __name__=="__main__":
    args=sys.argv; nl=args[1]; out=None
    if "--out" in args: out=args[args.index("--out")+1]
    main(nl,out)
'''

negatives["non_data_driven.py"] = '''#!/usr/bin/env python3
# returns a fixed plausible report regardless of input -> fails k/l (A/B2 wrong)
import sys
rep = """instance: Xnear_T
subckt: kcellx1mdl_T
tier: T
cumulative BL R: 33
measurement node: CC_near_T
WL trigger net: WL_near_T
column: near
"""
if len(sys.argv) > 2 and sys.argv[2] == "--out":
    with open(sys.argv[3], "w") as f: f.write(rep)
else:
    sys.stdout.write(rep)
'''

negatives["no_cli.py"] = '''#!/usr/bin/env python3
# no sys.argv/argparse, ignores input, writes a fixed report to a fixed file -> fails m/c
report = "instance: Xfar_B\\ncumulative BL R: 35\\n"
with open("/tmp/fc_report.txt","w") as f: f.write(report)
'''

for name, content in negatives.items():
    with open(os.path.join(NEG_DIR, name), "w") as f:
        f.write(content)
print("wrote %d negatives" % len(negatives))

# --- negative_selftest.py ---
SELFTEST = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""negative_selftest.py - assert every negative FAILS check() and reference PASSes.
Usage: python3 negative_selftest.py"""
import os, sys, zipfile, importlib.util, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_REF = os.path.dirname(HERE)
CHK = os.path.join(CASE_REF, "check.py")
REF = os.path.join(CASE_REF, "gen_farthest_cell_report_ref.py")

spec = importlib.util.spec_from_file_location("chk", CHK)
chk = importlib.util.module_from_spec(spec); spec.loader.exec_module(chk)

def make_zip(py_src):
    td = tempfile.mkdtemp()
    zp = os.path.join(td, "submit.zip")
    with zipfile.ZipFile(zp, "w") as z:
        z.writestr("gen_farthest_cell_report.py", py_src)
    return zp, td

def run_check(src):
    zp, td = make_zip(src)
    try:
        ok = chk.check(zp, td)
        return True, None
    except AssertionError as e:
        return False, str(e)
    except Exception as e:
        return False, "ERR: %s" % e

results = {}
# reference must PASS
with open(REF) as f:
    ref_src = f.read()
ok, msg = run_check(ref_src)
results["__reference__"] = (ok, msg)
if not ok:
    print("FAIL: reference did not PASS: %s" % msg); sys.exit(1)
print("PASS reference")

# negatives must all FAIL
neg_dir = os.path.join(HERE, "negative")
distinct = set()
for fn in sorted(os.listdir(neg_dir)):
    if not fn.endswith(".py"): continue
    with open(os.path.join(neg_dir, fn)) as f:
        src = f.read()
    ok, msg = run_check(src)
    results[fn] = (ok, msg)
    if ok:
        print("FAIL: negative %s unexpectedly PASSED check" % fn); sys.exit(1)
    # first-fail condition label
    label = msg.split(":")[0] if msg else "?"
    distinct.add(label)
    print("PASS neg %s -> FAIL[%s] %s" % (fn, label, msg[:80]))

print("\\nNEG_SELFTEST PASS: %d negatives all FAIL; distinct first-fail labels=%d %s" % (
    len([k for k in results if k!="__reference__"]), len(distinct), sorted(distinct)))
'''
with open(os.path.join(os.path.dirname(NEG_DIR), "negative_selftest.py"), "w") as f:
    f.write(SELFTEST)
print("wrote negative_selftest.py")
