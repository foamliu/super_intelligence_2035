#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-PowerNoiseInject-001 (shard B, spice_sim, B-synthesized, L1-boundary).
Trace: 1790580241881_fbdaa (joeyl @ hfeg0plg74, mc=10).
Sub-skill: VSS power supply noise PWL generation from spec + injection into FineSim .sp deck
(replace existing sine Vsource on supply net with VPWL noise source).
"""
import json, os, math, hashlib, zipfile, io, base64, tempfile, subprocess, sys, shutil, importlib.util

CASE_ID = "EDA-Eval-DesignFlow-PowerNoiseInject-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
AST = f"{BENCH}/assets/{CASE_ID}"
REF = f"{BENCH}/reference/{CASE_ID}"
NEG = f"{REF}/negative"
JSONL_B = f"{BENCH}/EDA-Eval-DesignFlow_B.jsonl"

for d in [AST, f"{AST}/hidden", REF, NEG]:
    os.makedirs(d, exist_ok=True)

# ---------- noise spec A ----------
spec_A = {
    "target_net": "vss!",
    "amplitude_mv": 15.0,
    "freq_components": [[200e6, 1.0], [400e6, 0.5]],
    "dc_offset_mv": 0.0,
    "jitter_mv_rms": 0.0,
    "duration_ns": 16.5,
    "timestep_ps": 10,
}
with open(f"{AST}/noise_spec_A.json", "w") as f:
    json.dump(spec_A, f, indent=2)

# ---------- target_tb_A.sp ----------
tb_A = """* FineSim testbench — VSS noise injection target (A)
.TITLE 'vss_noise_inject_A'
.option post=1
.GLOBAL vss!
.tran 10ps 16.5ns
* circuit: 4-stage inverter chain
xinv1 in n1 vdd vss! inv
xinv2 n1 n2 vdd vss! inv
xinv3 n2 n3 vdd vss! inv
xinv4 n3 out vdd vss! inv
vvdd vdd 0 1.2
vvss vss! 0 sin(0 15m 2e8hz 0 0 0)
vin in 0 pwl 0n 0 1n 0 1.01n 1.2 16.5n 1.2
.subckt inv a y vp vn
mp a vp y mp pn w=1u l=90n
mn a vn y mn nn w=0.5u l=90n
.ends
.model pn pmos level=1
.model nn nmos level=1
.END
"""
with open(f"{AST}/target_tb_A.sp", "w") as f:
    f.write(tb_A)

# ---------- hidden B ----------
spec_B = {
    "target_net": "gnd!",
    "amplitude_mv": 25.0,
    "freq_components": [[150e6, 1.0], [300e6, 0.3], [600e6, 0.2]],
    "dc_offset_mv": 0.0,
    "jitter_mv_rms": 0.0,
    "duration_ns": 12.0,
    "timestep_ps": 5,
}
with open(f"{AST}/hidden/noise_spec_B.json", "w") as f:
    json.dump(spec_B, f, indent=2)

tb_B = """* FineSim testbench — VSS noise injection target (B)
.TITLE 'gnd_noise_inject_B'
.option post=1
.GLOBAL gnd!
.tran 5ps 12ns
* circuit: 3-stage nand chain
xnand1 a b y1 vdd gnd! nand2
xnand2 y1 c y2 vdd gnd! nand2
xnand3 y2 d out vdd gnd! nand2
vvdd vdd 0 1.5
vgnd gnd! 0 sin(0 25m 150e6hz 0 0 0)
va a 0 pwl 0n 0 2n 0 2.01n 1.5 12n 1.5
vb b 0 1.5
vc c 0 0
vd d 0 1.5
.subckt nand2 a b y vp vn
m1 a a n1 vp pmod w=1u l=90n
m2 b b n1 vp pmod w=1u l=90n
m3 n1 vn y vn nmod w=0.5u l=90n
.ends
.model pmod pmos level=1
.model nmod nmos level=1
.END
"""
with open(f"{AST}/hidden/target_tb_B.sp", "w") as f:
    f.write(tb_B)

manifest = {"hidden_inputs": ["noise_spec_B.json", "target_tb_B.sp"],
            "note": "B: different net(gnd!), amplitude(25mV), freqs(150/300/600MHz), duration(12ns), ts(5ps), circuit(nand2 chain)"}
with open(f"{AST}/hidden/hidden_manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)

# ---------- reference solution ----------
ref_code = r'''#!/usr/bin/env python3
"""noise_inject_ref.py — Generate VSS power noise PWL from spec + inject into FineSim .sp deck.
Usage: python3 noise_inject_ref.py <spec.json> <tb.sp> <out.sp>
"""
import json, sys, math, re

def gen_noise(spec):
    """Generate PWL noise samples from spec."""
    dur = spec["duration_ns"] * 1e-9
    ts  = spec["timestep_ps"] * 1e-12
    amp = spec["amplitude_mv"] * 1e-3  # V
    dc  = spec.get("dc_offset_mv", 0.0) * 1e-3
    comps = spec["freq_components"]  # [[freq, weight], ...]
    npts = int(round(dur / ts)) + 1
    pts = []
    for i in range(npts):
        t = i * ts
        v = dc
        for freq, w in comps:
            v += amp * w * math.sin(2 * math.pi * freq * t)
        pts.append((t, v))
    return pts

def inject(tb_text, spec, pts):
    """Replace Vsource on target_net with VPWL."""
    net = spec["target_net"]
    lines = tb_text.split("\n")
    out_lines = []
    injected = False
    # Build PWL value string
    pwl_str = " ".join(f"{t:.12e} {v:.6e}" for t, v in pts)
    for line in lines:
        # Match a Vsource driving target_net:  vxxx  net  0  sin(...)  or  vxxx net 0 pwl(...)
        # Pattern: starts with v/V, then whitespace, then target_net as 2nd token, then 0 as 3rd token
        m = re.match(r'^([vV]\w+)\s+' + re.escape(net) + r'\s+0\s+', line)
        if m:
            if not injected:
                vname = m.group(1)
                out_lines.append(f"{vname} {net} 0 PWL {pwl_str}")
                injected = True
            # skip original (don't append)
        else:
            out_lines.append(line)
    if not injected:
        # net not found — append VPWL before .END
        vname = "v" + re.sub(r'[^a-zA-Z0-9]', '', net).lower() + "noise"
        for i, line in enumerate(out_lines):
            if line.strip().upper().startswith(".END"):
                out_lines.insert(i, f"{vname} {net} 0 PWL {pwl_str}")
                injected = True
                break
    return "\n".join(out_lines)

def main():
    if len(sys.argv) != 4:
        print("Usage: noise_inject_ref.py <spec.json> <tb.sp> <out.sp>", file=sys.stderr)
        sys.exit(2)
    spec_path, tb_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(spec_path) as f:
        spec = json.load(f)
    with open(tb_path) as f:
        tb_text = f.read()
    pts = gen_noise(spec)
    out_text = inject(tb_text, spec, pts)
    with open(out_path, "w") as f:
        f.write(out_text)

if __name__ == "__main__":
    main()
'''
with open(f"{REF}/noise_inject_ref.py", "w") as f:
    f.write(ref_code)

# ---------- check.py ----------
check_code = r'''#!/usr/bin/env python3
"""check.py for EDA-Eval-DesignFlow-PowerNoiseInject-001
12 conditions a-l. check(deliverable, workdir) -> pass/raise.
"""
import json, os, sys, math, re, zipfile, tempfile, subprocess, hashlib

def _run_cand(deliverable, workdir, spec_path, deck_path, out_name):
    """Extract candidate, run on (spec, deck), return out.sp path."""
    tmp = tempfile.mkdtemp(dir=workdir)
    with zipfile.ZipFile(deliverable) as z:
        z.extractall(tmp)
    cand = os.path.join(tmp, "noise_inject.py")
    out = os.path.join(tmp, out_name)
    r = subprocess.run([sys.executable, cand, spec_path, deck_path, out],
                       capture_output=True, text=True, timeout=60)
    return tmp, cand, out, r

def _parse_pwl_line(text, net):
    """Find VPWL line on net, return list of (t, v) floats, or None."""
    for line in text.split("\n"):
        m = re.match(r'^[vV]\w+\s+' + re.escape(net) + r'\s+0\s+PWL\s+(.*)', line, re.IGNORECASE)
        if m:
            toks = m.group(1).split()
            pts = []
            for i in range(0, len(toks)-1, 2):
                try:
                    pts.append((float(toks[i]), float(toks[i+1])))
                except ValueError:
                    pass
            return pts if pts else None
    return None

def _has_vsource(text, net, exclude_pwl=True):
    """Check if there's a non-PWL Vsource on net (the original sine)."""
    for line in text.split("\n"):
        m = re.match(r'^[vV]\w+\s+' + re.escape(net) + r'\s+0\s+', line)
        if m:
            if exclude_pwl and re.search(r'PWL', line, re.IGNORECASE):
                continue
            return True
    return False

def check(deliverable, workdir):
    asset_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "EDA-Eval-DesignFlow-PowerNoiseInject-001")
    b_spec = os.path.join(asset_dir, "hidden", "noise_spec_B.json")
    b_deck = os.path.join(asset_dir, "hidden", "target_tb_B.sp")
    a_spec = os.path.join(asset_dir, "noise_spec_A.json")
    a_deck = os.path.join(asset_dir, "target_tb_A.sp")
    with open(b_spec) as f: spec_B = json.load(f)
    with open(a_spec) as f: spec_A = json.load(f)

    # (a) zip + noise_inject.py + py_compile
    with zipfile.ZipFile(deliverable) as z:
        names = z.namelist()
        assert "noise_inject.py" in names, "(a) zip missing noise_inject.py"
        src = z.read("noise_inject.py").decode("utf-8", "replace")
    assert len(src.strip()) > 20, "(a) noise_inject.py too short (empty shell?)"
    try:
        compile(src, "noise_inject.py", "exec")
    except SyntaxError as e:
        raise AssertionError(f"(a) noise_inject.py py_compile failed: {e}")

    # (b) candidate runs on B, exit 0, out.sp exists
    tmpB, candB, outB, rb = _run_cand(deliverable, workdir, b_spec, b_deck, "out_B.sp")
    assert rb.returncode == 0, f"(b) candidate failed on B: {rb.stderr[:200]}"
    assert os.path.exists(outB), "(b) out_B.sp not produced"
    outB_text = open(outB).read()

    # (c) out.sp has VPWL on B target_net
    netB = spec_B["target_net"]
    pwlB = _parse_pwl_line(outB_text, netB)
    assert pwlB is not None and len(pwlB) > 2, f"(c) no VPWL on {netB} in out_B.sp"

    # (d) original sine source on B target_net removed
    assert not _has_vsource(outB_text, netB, exclude_pwl=True), f"(d) original non-PWL Vsource on {netB} still present"

    # (e) PWL point count = duration/timestep + 1
    exp_npts = int(round(spec_B["duration_ns"]*1e-9 / (spec_B["timestep_ps"]*1e-12))) + 1
    assert len(pwlB) == exp_npts, f"(e) PWL point count {len(pwlB)} != expected {exp_npts}"

    # (f) PWL times span [0, duration]
    dur_B = spec_B["duration_ns"] * 1e-9
    ts_B = spec_B["timestep_ps"] * 1e-12
    assert abs(pwlB[0][0]) < ts_B*0.1, f"(f) first time {pwlB[0][0]} != 0"
    assert abs(pwlB[-1][0] - dur_B) < ts_B*0.5, f"(f) last time {pwlB[-1][0]} != {dur_B}"

    # (g) PWL amplitudes within spec bounds
    amp_B = spec_B["amplitude_mv"] * 1e-3
    total_w = sum(w for _, w in spec_B["freq_components"])
    max_exp = amp_B * total_w * 1.2  # 20% tolerance for numerical
    vs = [v for _, v in pwlB]
    assert max(abs(v) for v in vs) <= max_exp, f"(g) max |V| {max(abs(v) for v in vs):.4e} > bound {max_exp:.4e}"

    # (h) .tran preserved
    assert re.search(r'\.tran\b', outB_text, re.IGNORECASE), "(h) .tran statement missing in out_B.sp"

    # (i) deck integrity — other elements preserved (check .subckt and .END present)
    assert re.search(r'\.subckt\b', outB_text, re.IGNORECASE), "(i) .subckt missing in out_B.sp"
    assert re.search(r'\.END\b', outB_text, re.IGNORECASE), "(i) .END missing in out_B.sp"
    # inv/nand2 instances preserved
    assert re.search(r'^x\w+', outB_text, re.MULTILINE), "(i) no x-instance lines in out_B.sp"

    # (j) cross-input guard: re-run on A, A PWL != B PWL (different params)
    tmpA, candA, outA, ra = _run_cand(deliverable, workdir, a_spec, a_deck, "out_A.sp")
    assert ra.returncode == 0, f"(j) candidate failed on A: {ra.stderr[:200]}"
    outA_text = open(outA).read()
    netA = spec_A["target_net"]
    pwlA = _parse_pwl_line(outA_text, netA)
    assert pwlA is not None, "(j) no VPWL on A target_net"
    # A and B must differ (different amplitude/duration/net)
    assert pwlA[-1][0] != pwlB[-1][0] or abs(pwlA[len(pwlA)//2][1] - pwlB[len(pwlB)//2][1]) > 1e-6, "(j) A and B PWL identical (hardcoded?)"

    # (k) determinism: re-run B, sha256 identical
    tmpB2, _, outB2, _ = _run_cand(deliverable, workdir, b_spec, b_deck, "out_B2.sp")
    h1 = hashlib.sha256(open(outB).read().encode()).hexdigest()
    h2 = hashlib.sha256(open(outB2).read().encode()).hexdigest()
    assert h1 == h2, "(k) non-deterministic output (sha256 differs on re-run)"

    # (l) no duplicate VPWL/PWL source on target_net
    pwl_count = 0
    for line in outB_text.split("\n"):
        if re.match(r'^[vV]\w+\s+' + re.escape(netB) + r'\s+0\s+', line):
            pwl_count += 1
    assert pwl_count == 1, f"(l) {pwl_count} Vsource lines on {netB} (expected 1, no duplicate)"

    return True
'''
with open(f"{REF}/check.py", "w") as f:
    f.write(check_code)

# ---------- negatives ----------
neg_empty = "def (\n"  # syntax error
with open(f"{NEG}/naive_empty.py", "w") as f:
    f.write(neg_empty)

neg_print = '''#!/usr/bin/env python3
import sys
# print expected but don't produce real output
print("injected")
sys.exit(0)
'''
with open(f"{NEG}/naive_print_expected.py", "w") as f:
    f.write(neg_print)

neg_copy = r'''#!/usr/bin/env python3
"""fake_core_deleted: copies deck unchanged (no PWL injection)."""
import sys, shutil
if len(sys.argv) != 4:
    sys.exit(2)
shutil.copy(sys.argv[2], sys.argv[3])
'''
with open(f"{NEG}/fake_core_deleted.py", "w") as f:
    f.write(neg_copy)

neg_hardcode_a = r'''#!/usr/bin/env python3
"""naive_hardcode_a: hardcodes A params, ignores B spec."""
import sys, math
# Hardcoded A values
NET = "vss!"
AMP = 15e-3
FREQS = [[200e6, 1.0], [400e6, 0.5]]
DUR = 16.5e-9
TS = 10e-12
def main():
    if len(sys.argv) != 4:
        sys.exit(2)
    spec_p, tb_p, out_p = sys.argv[1], sys.argv[2], sys.argv[3]
    # IGNORE spec_p, always use A params
    npts = int(round(DUR/TS))+1
    pts = []
    for i in range(npts):
        t = i*TS
        v = sum(AMP*w*math.sin(2*math.pi*f*t) for f,w in FREQS)
        pts.append((t, v))
    import re
    text = open(tb_p).read()
    lines = text.split("\n")
    out = []
    inj = False
    pwl = " ".join(f"{t:.12e} {v:.6e}" for t,v in pts)
    for line in lines:
        m = re.match(r'^[vV]\w+\s+' + re.escape(NET) + r'\s+0\s+', line)
        if m:
            if not inj:
                out.append(f"{m.group(1)} {NET} 0 PWL {pwl}")
                inj = True
        else:
            out.append(line)
    # If net not found (B uses gnd!), append before .END
    if not inj:
        for i, line in enumerate(out):
            if line.strip().upper().startswith(".END"):
                out.insert(i, f"vnoise {NET} 0 PWL {pwl}")
                break
    open(out_p, "w").write("\n".join(out))
main()
'''
with open(f"{NEG}/naive_hardcode_a.py", "w") as f:
    f.write(neg_hardcode_a)

# ---------- negative_selftest.py ----------
neg_selftest = r'''#!/usr/bin/env python3
"""negative_selftest.py — all negatives must FAIL check()."""
import json, os, sys, tempfile, zipfile, subprocess, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.join(HERE, "..")  # reference/EDA-Eval-DesignFlow-PowerNoiseInject-001
CHECK = os.path.join(REF_DIR, "check.py")

def load_check():
    spec = importlib.util.spec_from_file_location("check_mod", CHECK)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def make_zip(neg_path):
    """Zip a negative as noise_inject.py."""
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False, dir="/tmp")
    with zipfile.ZipFile(tmp.name, "w") as z:
        z.write(neg_path, "noise_inject.py")
    return tmp.name

def run_neg(name):
    neg = os.path.join(HERE, name)
    zpath = make_zip(neg)
    chk = load_check()
    workdir = tempfile.mkdtemp(dir="/tmp")
    try:
        chk.check(zpath, workdir)
        return "PASS"  # BAD — neg should fail
    except Exception as e:
        return f"FAIL({str(e)[:30]})"
    finally:
        os.unlink(zpath)

if __name__ == "__main__":
    negs = ["naive_empty.py", "naive_print_expected.py", "fake_core_deleted.py", "naive_hardcode_a.py"]
    results = {}
    all_fail = True
    for n in negs:
        r = run_neg(n)
        results[n] = r
        if r == "PASS":
            all_fail = False
    for n, r in results.items():
        print(f"  {n}: {r}")
    if all_fail:
        print("ALL_NEGS_FAIL: OK")
    else:
        print("SOME_NEG_PASSED: BAD")
        sys.exit(1)
'''
with open(f"{NEG}/negative_selftest.py", "w") as f:
    f.write(neg_selftest)

# ---------- selftest ----------
print("=== SELFTEST ===")
workdir = tempfile.mkdtemp(dir="/tmp")

# 1. ref PASS
ref_zip = tempfile.NamedTemporaryFile(suffix=".zip", delete=False, dir="/tmp")
with zipfile.ZipFile(ref_zip.name, "w") as z:
    z.write(f"{REF}/noise_inject_ref.py", "noise_inject.py")

spec_c = importlib.util.spec_from_file_location("check_mod", f"{REF}/check.py")
chk = importlib.util.module_from_spec(spec_c)
spec_c.loader.exec_module(chk)

try:
    chk.check(ref_zip.name, workdir)
    print("REF: PASS (all 12 conditions)")
except Exception as e:
    print(f"REF: FAIL — {e}")
    sys.exit(1)
finally:
    os.unlink(ref_zip.name)

# 2. negatives all FAIL — run as subprocess
r_ns = subprocess.run([sys.executable, f"{NEG}/negative_selftest.py"], capture_output=True, text=True)
print(r_ns.stdout)
if r_ns.returncode != 0:
    print(f"NEG SELFTEST FAILED:\n{r_ns.stderr}")
    sys.exit(1)

# ---------- append jsonl ----------
rationale = "12 条断言：①zip含noise_inject.py且py_compile通过 ②候选在B(spec+deck)上exit 0并产出out.sp ③out.sp含VPWL源在B目标net上 ④B目标net原sine源已移除 ⑤PWL点数=duration/timestep+1 ⑥PWL时间值覆盖[0,duration] ⑦PWL幅度在spec界限内 ⑧.tran语句保留不变 ⑨其他电路元件保留(deck完整性) ⑩跨输入守卫:A的PWL≠B的PWL(参数驱动非硬编码) ⑪确定性:重跑B sha256一致 ⑫目标net无重复源"

entry = {
    "task_id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": "这里是噪声生成项目的位置：/home/joeyl/noise_generator/ 我想请你帮我生成vss!的电源噪声，并将其注入到仿真testbench .sp文件中。noise_spec.json给出了噪声参数（目标net、幅度、频率分量、时长、步长），target_tb.sp是待注入的FineSim testbench（其vss!节点当前由一个sine源驱动）。请编写一个Python工具noise_inject.py，读取noise_spec.json生成PWL电源噪声数据，并将target_tb.sp中目标net上的原sine源替换为VPWL噪声源，输出修改后的完整deck。",
    "attachments": [f"assets/{CASE_ID}/noise_spec_A.json", f"assets/{CASE_ID}/target_tb_A.sp"],
    "test": check_code,
    "metadata": {
        "trace_source": {
            "user": "joeyl",
            "host": "hfeg0plg74",
            "session_file": "1790580241881_fbdaa.messages.json",
            "match_count": 10,
            "real_task_summary": "VSS power supply noise generation + injection into FineSim .sp testbench (replace sine Vsource with VPWL noise)"
        },
        "domain": "spice_sim",
        "track": "synthesized",
        "test_rationale": rationale,
    }
}

with open(JSONL_B, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify test field matches disk check.py
with open(f"{REF}/check.py") as f:
    disk_check = f.read()
assert entry["test"] == disk_check, "test field != disk check.py"
chk_md5 = hashlib.md5(disk_check.encode()).hexdigest()
print(f"\n=== DONE ===")
print(f"case_id: {CASE_ID}")
print(f"check.py md5: {chk_md5}, size: {len(disk_check)}B")
print(f"jsonl_B appended")
# count lines
with open(JSONL_B) as f:
    n = sum(1 for _ in f)
print(f"jsonl_B lines: {n}")
print(f"k_rationale=k_check=12 >= 8: GATE PASS")
