#!/usr/bin/env python3
"""uploader_dff.py -- push DFF calibration files to .75 via eda_flow MCP HTTP, run char_gen, fetch results."""
import json, urllib.request, sys, os, re, base64

URL = "http://127.0.0.1:18891/mcp"

def call(method, params):
    req = urllib.request.Request(URL, data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),
                                 headers={"Content-Type":"application/json","Accept":"application/json, text/event-stream"})
    return json.loads(urllib.request.urlopen(req, timeout=300).read())

def call_tool(n, a): return call("tools/call", {"name": n, "arguments": a})

def get_text(res):
    c = res.get("result", {}).get("content") or res.get("content") or res
    if isinstance(c, list): return "\n".join(x.get("text","") for x in c if isinstance(x,dict))
    if isinstance(c, dict): return c.get("text", json.dumps(c))
    return str(c)

WD_FILE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/.tmp_dff_calib/workdir.txt"
if os.path.exists(WD_FILE):
    workdir = open(WD_FILE).read().strip()
    print("reusing workdir:", workdir)
else:
    res = call_tool("open_session", {"task_id": "dff_calib", "eval_id": "shardB"})
    txt = get_text(res)
    print("open_session:", txt[:400])
    m = re.search(r'(/[\w/\.\-]+workdir[\w/\.\-]*)', txt) or re.search(r'(/[\w/\.\-]+)', txt)
    workdir = m.group(1) if m else "/proj/train/AI/workdir/t0002997_1"
    open(WD_FILE,"w").write(workdir)
    print("workdir:", workdir)

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
files = {
    "char_gen_ref.py": f"{BASE}/reference/EDA-Eval-DesignFlow-DffSetupHoldChar-001/char_gen_ref.py",
    "A/dff.sp":        f"{BASE}/assets/EDA-Eval-DesignFlow-DffSetupHoldChar-001/dff_A.sp",
    "A/params.json":   f"{BASE}/assets/EDA-Eval-DesignFlow-DffSetupHoldChar-001/params_A.json",
    "B/dff.sp":        f"{BASE}/assets/EDA-Eval-DesignFlow-DffSetupHoldChar-001/hidden/dff_B.sp",
    "B/params.json":   f"{BASE}/assets/EDA-Eval-DesignFlow-DffSetupHoldChar-001/hidden/params_B.json",
}
# clean old run dirs
call_tool("run_commands", {"workdir": workdir, "commands": [f"rm -rf {workdir}/dff_calib && mkdir -p {workdir}/dff_calib"]})
for rel, local in files.items():
    content = open(local).read()
    if rel.endswith(".json"):
        b64 = base64.b64encode(content.encode()).decode()
        r = call_tool("run_commands", {"workdir": workdir, "commands": [f"echo {b64} | base64 -d > {workdir}/dff_calib/{rel}"]})
    else:
        r = call_tool("write_file", {"path": f"{workdir}/dff_calib/{rel}", "content": content})
    print(f"write {rel}: ok")

# verify
r = call_tool("run_commands", {"workdir": workdir, "commands": [
    f"cd {workdir}/dff_calib && python3 -c \"import json;print('A tclk',json.load(open('A/params.json'))['tclk'],'Cs1 sweep',len(json.load(open('A/params.json'))['tsu_sweep']));print('B tclk',json.load(open('B/params.json'))['tclk'])\"",
    f"grep Cs1 {workdir}/dff_calib/A/dff.sp {workdir}/dff_calib/B/dff.sp",
]})
print("verify:", get_text(r)[:400])

# run A
r = call_tool("run_commands", {"workdir": workdir, "commands": [
    f"cd {workdir}/dff_calib && rm -rf runA runB && python3 char_gen_ref.py A/dff.sp A/params.json runA 2>&1 | tail -25"
]})
print("=== RUN A ==="); print(get_text(r)[:2500])

r = call_tool("run_commands", {"workdir": workdir, "commands": [
    f"cd {workdir}/dff_calib && python3 char_gen_ref.py B/dff.sp B/params.json runB 2>&1 | tail -25"
]})
print("=== RUN B ==="); print(get_text(r)[:2500])

for tag in ("A","B"):
    r = call_tool("read_file", {"path": f"{workdir}/dff_calib/run{tag}/result.json"})
    print(f"=== result {tag} ==="); print(get_text(r)[:1800])
