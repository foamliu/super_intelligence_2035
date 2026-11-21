import os, sys, zipfile, tempfile, io, csv, re
REF='/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/Ddr5ClDelayPivot-001'
sys.path.insert(0, REF)
from check import _oracle, _expected_csv, check

B_GOLD = [
 ("TS_"+str(9500),18.95,16.00,15.16,0.211),
 ("TS_"+str(9200),20.00,16.09,15.22,0.217),
 ("TS_"+str(8600),19.53,17.21,17.21,0.233),
 ("TS_"+str(8400),20.00,17.14,17.14,0.238),
 ("TS_"+str(8200),20.00,17.56,17.56,0.244),
 ("TS_"+str(7600),19.47,17.89,17.89,0.263),
 ("TS_"+str(6800),20.59,18.24,18.24,0.294),
 ("TS_"+str(6720),19.64,16.67,16.67,0.298),
 ("TS_"+str(6000),21.33,18.00,18.00,0.333),
 ("TS_"+str(5200),21.54,17.69,17.69,0.385),
 ("TS_"+str(4400),21.82,18.18,18.18,0.455),
 ("TS_"+str(3600),22.22,17.78,17.78,0.556),
 ("TS_"+str(1600),32.50,27.50,27.50,1.250),
]

FAKE_PRINT_ONLY = (
"import sys, csv, io\n"
"def main(inp, out):\n"
"    rows = %r\n"
"    s=io.StringIO(); w=csv.writer(s)\n"
"    w.writerow(['Speed Grade','SS (ns)','TT (ns)','FF (ns)','tCK (ns)'])\n"
"    for nm,ss,tt,ff,tck in rows:\n"
"        w.writerow([nm,'%%.2f'%%ss,'%%.2f'%%tt,'%%.2f'%%ff,'%%.3f'%%tck])\n"
"    open(out,'w').write(s.getvalue())\n"
"main(sys.argv[1], sys.argv[2])\n"
) % (B_GOLD,)

FAKE_CORE_DELETED = (
"import sys\n"
"def main(inp, out):\n"
"    open(inp).read()\n"
"    open(out,'w').write('Speed Grade,SS (ns),TT (ns),FF (ns),tCK (ns)\\n')\n"
"main(sys.argv[1], sys.argv[2])\n"
)

AV=REF+'/../../assets/EDA-Eval-DesignFlow-Ddr5ClDelayPivot-001/inputs_A/Task4FSM_A.v'
oa=_oracle(open(AV).read())
A_GOLD=[(r[0],r[1],r[2],r[3],r[4]) for r in oa]
FAKE_HARDCODE_A = (
"import sys, csv, io\n"
"def main(inp, out):\n"
"    rows = %r\n"
"    s=io.StringIO(); w=csv.writer(s)\n"
"    w.writerow(['Speed Grade','SS (ns)','TT (ns)','FF (ns)','tCK (ns)'])\n"
"    for nm,ss,tt,ff,tck in rows:\n"
"        w.writerow([nm,'%%.2f'%%ss,'%%.2f'%%tt,'%%.2f'%%ff,'%%.3f'%%tck])\n"
"    open(out,'w').write(s.getvalue())\n"
"main(sys.argv[1], sys.argv[2])\n"
) % (A_GOLD,)

SMART_STUB = r'''
import sys, re, csv, io
B_SIG = "TS_" + "9500"
B_GOLD = [
 ("TS_"+str(9500),18.95,16.00,15.16,0.211),
 ("TS_"+str(9200),20.00,16.09,15.22,0.217),
 ("TS_"+str(8600),19.53,17.21,17.21,0.233),
 ("TS_"+str(8400),20.00,17.14,17.14,0.238),
 ("TS_"+str(8200),20.00,17.56,17.56,0.244),
 ("TS_"+str(7600),19.47,17.89,17.89,0.263),
 ("TS_"+str(6800),20.59,18.24,18.24,0.294),
 ("TS_"+str(6720),19.64,16.67,16.67,0.298),
 ("TS_"+str(6000),21.33,18.00,18.00,0.333),
 ("TS_"+str(5200),21.54,17.69,17.69,0.385),
 ("TS_"+str(4400),21.82,18.18,18.18,0.455),
 ("TS_"+str(3600),22.22,17.78,17.78,0.556),
 ("TS_"+str(1600),32.50,27.50,27.50,1.250),
]
def real_oracle(text):
    rows=[]; cur=None; pending=None
    for line in text.splitlines():
        m=re.search(r'"TS_(\d+)":\s*begin', line)
        if m:
            if cur is not None: rows.append(cur)
            cur={"name":"TS_"+m.group(1),"dr":int(m.group(1)),"FF":None,"TT":None,"SS":None}; pending=None; continue
        if cur is None: continue
        if "endcase" in line: rows.append(cur); cur=None; continue
        if re.search(r"`ifdef\s+FF\b", line): pending="FF"; continue
        if re.search(r"`elsif\s+TT\b", line): pending="TT"; continue
        if re.search(r"`elsif\s+SS\b", line): pending="SS"; continue
        if re.search(r"`else\b", line): pending="else"; continue
        if pending in ("FF","TT","SS") and cur[pending] is None:
            cm=re.search(r"CL_(\d+)tCK", line)
            if cm: cur[pending]=int(cm.group(1)); pending=None
    out=[]
    for g in rows:
        tck=2000.0/g["dr"]
        out.append((g["name"],round(g["SS"]*tck,2),round(g["TT"]*tck,2),round(g["FF"]*tck,2),round(tck,3)))
    return out
def main(inp, out):
    text=open(inp).read()
    if B_SIG in text:
        rows=B_GOLD
    else:
        rows=real_oracle(text)
    s=io.StringIO(); w=csv.writer(s)
    w.writerow(["Speed Grade","SS (ns)","TT (ns)","FF (ns)","tCK (ns)"])
    for nm,ss,tt,ff,tck in rows:
        w.writerow([nm,"%.2f"%ss,"%.2f"%tt,"%.2f"%ff,"%.3f"%tck])
    open(out,"w").write(s.getvalue())
main(sys.argv[1], sys.argv[2])
'''

fakes = {
 "fake_print_only": FAKE_PRINT_ONLY,
 "fake_core_deleted": FAKE_CORE_DELETED,
 "fake_hardcode_a": FAKE_HARDCODE_A,
 "fake_smart_hardcode_b": SMART_STUB,
}
for name, code in fakes.items():
    td=tempfile.mkdtemp(prefix=name+"_")
    sut=os.path.join(td,"ddr5_cl_delay_pivot.py")
    open(sut,"w").write(code)
    zp=os.path.join(td,"submit.zip")
    with zipfile.ZipFile(zp,"w") as zf: zf.write(sut,"ddr5_cl_delay_pivot.py")
    try:
        r=check(zp, REF)
        print(f"  [{name}] => PASS  <-- GAP!")
    except AssertionError as e:
        print(f"  [{name}] => FAIL: {str(e)[:140]}")
    except Exception as e:
        print(f"  [{name}] => ERROR: {type(e).__name__}: {str(e)[:140]}")
