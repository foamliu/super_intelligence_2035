#!/usr/bin/env python3
"""Build EDA-Eval-DesignFlow-DqReadPathWaveDebug-001 (shard D, waveform, B-grade synthesized L2)."""
import os, json, csv, io, zipfile, hashlib, random, re, shutil, subprocess, sys

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "DqReadPathWaveDebug-001"
ADIR = os.path.join(BASE, "assets", CASE)
HDIR = os.path.join(ADIR, "hidden")
RDIR = os.path.join(BASE, "reference", CASE)
NEGDIR = os.path.join(RDIR, "negative")
for d in (ADIR, HDIR, RDIR, NEGDIR):
    os.makedirs(d, exist_ok=True)

# ---------- A (visible) ----------
# 16-bit dq_exp, UPDQP=dq_exp[15:8], LPDQPad=dq_exp[7:0], rd_en, burst_id[1:0]
# bug: fix_disable_b2=1'b1 -> rd_en_gate=rd_en & ~(burst_id==2 & 1) -> output 0 on burst_id==2 & rd_en=1
random.seed(4242)
N_A = 20
A_cycles = []
for c in range(N_A):
    dq = (0x5a5a + c * 0x1113) & 0xFFFF
    rd_en = 0 if c < 2 else 1
    bid = c % 4
    dqs_stb = 1 if rd_en else 0
    A_cycles.append(dict(cycle=c, dq_exp=dq, rd_en=rd_en, burst_id=bid, dqs_stb=dqs_stb))

def gold_out_a(dq, rd_en, bid):
    # golden: fix_disable=0 -> gate=rd_en
    g = rd_en
    up = (dq >> 8) & 0xFF if g else 0
    lp = dq & 0xFF if g else 0
    return up, lp

def act_out_a(dq, rd_en, bid):
    # actual: fix_disable=1 -> gate=rd_en & ~(bid==2)
    g = rd_en & (0 if bid == 2 else 1)
    up = (dq >> 8) & 0xFF if g else 0
    lp = dq & 0xFF if g else 0
    return up, lp

HEX_COLS_A = {"dq_exp", "UPDQP", "LPDQPad"}
HEX_COLS_B = {"dq_data", "HI_DQ", "LO_DQ"}
_WIDTH = {"dq_exp": 16, "UPDQP": 8, "LPDQPad": 8, "dq_data": 32, "HI_DQ": 16, "LO_DQ": 16}

def fmt(v, col):
    if col in _WIDTH:
        w = _WIDTH[col]
        return "0x" + format(v & ((1 << w) - 1), "0%dx" % ((w + 3) // 4))
    return v

def write_trace(path, rows, cols, hexcols):
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for r in rows:
            w.writerow([fmt(r[c], c) if c in hexcols else r[c] for c in cols])

COLS_A = ["cycle", "dq_exp", "rd_en", "burst_id", "dqs_stb", "UPDQP", "LPDQPad"]
grows, arows = [], []
for r in A_cycles:
    up, lp = gold_out_a(r["dq_exp"], r["rd_en"], r["burst_id"])
    grows.append({**r, "UPDQP": up, "LPDQPad": lp})
    up2, lp2 = act_out_a(r["dq_exp"], r["rd_en"], r["burst_id"])
    arows.append({**r, "UPDQP": up2, "LPDQPad": lp2})
write_trace(os.path.join(ADIR, "golden_trace_A.csv"), grows, COLS_A, HEX_COLS_A)
write_trace(os.path.join(ADIR, "actual_trace_A.csv"), arows, COLS_A, HEX_COLS_A)

NETLIST_A = """module dq_readpath_A(
  input  [15:0] dq_exp,
  input         rd_en,
  input  [1:0]  burst_id,
  input         dqs_stb,
  output [7:0]  UPDQP,
  output [7:0]  LPDQPad
);
  wire [15:0] dq_buf = dq_exp;                                        // stage: pattern_buf
  wire fix_disable_b2 = 1'b1;                                         // stage: rd_gate culprit:fix_disable_b2
  wire burst2_sel = (burst_id == 2'd2);
  wire rd_en_gate = rd_en & ~(burst2_sel & fix_disable_b2);
  wire [7:0]  up_mux = rd_en_gate ? dq_buf[15:8] : 8'h00;             // stage: read_mux
  wire [7:0]  lp_mux = rd_en_gate ? dq_buf[7:0]  : 8'h00;
  assign UPDQP   = up_mux;                                            // stage: pad_driver
  assign LPDQPad = lp_mux;
endmodule
"""
open(os.path.join(ADIR, "dq_readpath_A.v"), "w").write(NETLIST_A)

# ---------- B (hidden, anti-hardcode) ----------
# 32-bit dq_data, HI_DQ=dq_data[31:16], LO_DQ=dq_data[15:0], read_valid, beat_id[2:0]
# bug: slice_swap_sel=1'b1 -> HI_DQ=dq_data[15:0], LO_DQ=dq_data[31:16] (swapped)
random.seed(7777)
N_B = 24
B_cycles = []
for c in range(N_B):
    dq = (0x12340000 + c * 0x00231007) & 0xFFFFFFFF  # ensure hi!=lo generally
    if (dq >> 16) & 0xFFFF == dq & 0xFFFF:
        dq ^= 0xFFFF0000  # force halves differ
    rv = 0 if c < 3 else 1
    bid = c % 8
    B_cycles.append(dict(cycle=c, dq_data=dq, read_valid=rv, beat_id=bid))

COLS_B = ["cycle", "dq_data", "read_valid", "beat_id", "HI_DQ", "LO_DQ"]
def gold_out_b(dq, rv):
    hi = (dq >> 16) & 0xFFFF if rv else 0
    lo = dq & 0xFFFF if rv else 0
    return hi, lo
def act_out_b(dq, rv):
    # swapped
    hi = (dq & 0xFFFF) if rv else 0
    lo = ((dq >> 16) & 0xFFFF) if rv else 0
    return hi, lo

growsB, arowsB = [], []
for r in B_cycles:
    hi, lo = gold_out_b(r["dq_data"], r["read_valid"])
    growsB.append({**r, "HI_DQ": hi, "LO_DQ": lo})
    hi2, lo2 = act_out_b(r["dq_data"], r["read_valid"])
    arowsB.append({**r, "HI_DQ": hi2, "LO_DQ": lo2})
write_trace(os.path.join(HDIR, "golden_trace_B.csv"), growsB, COLS_B, HEX_COLS_B)
write_trace(os.path.join(HDIR, "actual_trace_B.csv"), arowsB, COLS_B, HEX_COLS_B)

NETLIST_B = """module dq_readpath_B(
  input  [31:0] dq_data,
  input         read_valid,
  input  [2:0]  beat_id,
  output [15:0] HI_DQ,
  output [15:0] LO_DQ
);
  wire [31:0] dq_latch = dq_data;                                     // stage: exp_latch
  wire slice_swap_sel = 1'b1;                                         // stage: slice_mux culprit:slice_swap_sel
  wire [15:0] hi_mux = read_valid ? (slice_swap_sel ? dq_latch[15:0]  : dq_latch[31:16]) : 16'h0000;
  wire [15:0] lo_mux = read_valid ? (slice_swap_sel ? dq_latch[31:16] : dq_latch[15:0])  : 16'h0000;
  assign HI_DQ = hi_mux;                                              // stage: io_pad
  assign LO_DQ = lo_mux;
endmodule
"""
open(os.path.join(HDIR, "dq_readpath_B.v"), "w").write(NETLIST_B)

manifest = {"hidden_inputs": ["golden_trace_B.csv", "actual_trace_B.csv", "dq_readpath_B.v"],
            "note": "structurally different from A: 32-bit bus, swapped slices, different signal names"}
open(os.path.join(HDIR, "hidden_manifest.json"), "w").write(json.dumps(manifest, indent=2))

# expected B diagnosis
B_exp_first_fail = next(c["cycle"] for c in growsB if c["HI_DQ"] != arowsB[c["cycle"]]["HI_DQ"] and c["read_valid"] == 1)
B_exp_mismatch = [c["cycle"] for c, a in zip(growsB, arowsB) if c["HI_DQ"] != a["HI_DQ"] or c["LO_DQ"] != a["LO_DQ"]]
B_DIAG = dict(
    root_cause_signal="slice_swap_sel",
    root_cause_kind="bit_swap",
    failing_stage="slice_mux",
    first_fail_cycle=B_exp_first_fail,
    mismatch_cycles=B_exp_mismatch,
    expected_signal="dq_data",
    output_signals=["HI_DQ", "LO_DQ"],
    enable_signal="read_valid",
    data_intact=True,
)
open(os.path.join(HDIR, "expected_diagnosis_B.json"), "w").write(json.dumps(B_DIAG, indent=2))

# ---------- reference candidate ----------
REF = r'''#!/usr/bin/env python3
import sys, json, csv, re, argparse, os

def parse_trace(path):
    rows = []
    with open(path) as f:
        for r in csv.DictReader(f):
            row = {}
            for k, v in r.items():
                k = k.strip(); v = v.strip()
                if v.startswith("0x") or v.startswith("0X"):
                    row[k] = int(v, 16)
                elif re.fullmatch(r"[0-9]+", v):
                    row[k] = int(v)
                else:
                    row[k] = v
            rows.append(row)
    return rows

def parse_netlist(path):
    txt = open(path).read()
    m = re.search(r"module\s+(\w+)\s*\((.*?)\)\s*;", txt, re.S)
    module = m.group(1) if m else "unknown"
    inputs, outputs = [], []
    for mm in re.finditer(r"(input|output)\s+(?:\[(\d+):(\d+)\]\s+)?(\w+)", txt):
        d, hi, lo, name = mm.group(1), mm.group(2), mm.group(3), mm.group(4)
        width = (int(hi) - int(lo) + 1) if hi is not None else 1
        (inputs if d == "input" else outputs).append((name, width))
    # culprit constant wires: wire NAME = 1'b1 ;  with optional stage/culprit comment
    constants = {}
    culprit_lines = []
    for mm in re.finditer(r"wire\s+(\w+)\s*=\s*(1'b[01]|0|1)\s*;[^\n]*", txt):
        name = mm.group(1); val = mm.group(2)
        constants[name] = val
        line = mm.group(0)
        cm = re.search(r"stage:\s*(\w+)", line)
        cl = re.search(r"culprit:(\w+)", line)
        if cl and cl.group(1) == name:
            culprit_lines.append((name, cm.group(1) if cm else "unknown"))
    stages = re.findall(r"//\s*stage:\s*(\w+)", txt)
    return {"module": module, "inputs": inputs, "outputs": outputs,
            "constants": constants, "culprit_lines": culprit_lines, "stages": stages, "text": txt}

def to_hex(v, w):
    return format(v & ((1 << w) - 1), "0%dx" % ((w + 3) // 4))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--golden", required=True)
    ap.add_argument("--actual", required=True)
    ap.add_argument("--netlist", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    g = parse_trace(args.golden)
    a = parse_trace(args.actual)
    nl = parse_netlist(args.netlist)
    # expected = widest input
    exp_sig = max(nl["inputs"], key=lambda t: t[1])[0]
    out_sigs = [n for n, w in nl["outputs"]]
    # enable = 1-bit input that is not exp_sig
    enable_sig = None
    for n, w in nl["inputs"]:
        if w == 1 and n != exp_sig:
            # prefer a name like rd_en/read_valid/enable
            if re.search(r"en|valid|stb", n, re.I):
                enable_sig = n; break
    if enable_sig is None:
        for n, w in nl["inputs"]:
            if w == 1 and n != exp_sig:
                enable_sig = n; break
    # data integrity: exp_sig identical golden vs actual
    data_intact = all(gr.get(exp_sig) == ar.get(exp_sig) for gr, ar in zip(g, a))
    # mismatch cycles: outputs differ, exp same
    mismatch = []
    for i, (gr, ar) in enumerate(zip(g, a)):
        if gr.get(exp_sig) != ar.get(exp_sig):
            continue
        diff = any(gr.get(o) != ar.get(o) for o in out_sigs)
        if diff:
            mismatch.append(gr.get("cycle", i))
    first_fail = min(mismatch) if mismatch else None
    # active cycles (enable=1)
    active = [gr.get("cycle", i) for i, gr in enumerate(g) if enable_sig and gr.get(enable_sig) == 1]
    # determine bug kind
    # gate_disable: mismatch is a strict subset of active (conditional disable)
    # bit_swap: mismatch covers (nearly) all active cycles where halves differ
    kind = "unknown"
    if mismatch and active:
        mset, aset = set(mismatch), set(active)
        if mset <= aset and len(mset) < len(aset):
            kind = "gate_disable"
        elif mset == aset or len(mset & aset) >= 0.8 * len(aset):
            kind = "bit_swap"
        else:
            kind = "gate_disable" if len(mset) < len(aset) else "bit_swap"
    # culprit
    culprit = nl["culprit_lines"][0] if nl["culprit_lines"] else ("unknown", "unknown")
    root_cause_signal = culprit[0]
    failing_stage = culprit[1]
    # bit analysis: for each output, compare golden vs actual at first_fail
    bit_analysis = {}
    if first_fail is not None:
        gr = next(x for x in g if x.get("cycle") == first_fail)
        ar = next(x for x in a if x.get("cycle") == first_fail)
        for o in out_sigs:
            bit_analysis[o] = {"golden": gr.get(o), "actual": ar.get(o)}
    diag = {
        "module": nl["module"],
        "expected_signal": exp_sig,
        "output_signals": out_sigs,
        "enable_signal": enable_sig,
        "data_intact": data_intact,
        "mismatch_cycles": mismatch,
        "first_fail_cycle": first_fail,
        "root_cause_signal": root_cause_signal,
        "root_cause_kind": kind,
        "failing_stage": failing_stage,
        "stages": nl["stages"],
        "bit_analysis": bit_analysis,
    }
    with open(args.out, "w") as f:
        json.dump(diag, f, indent=2)
    print(json.dumps(diag))

if __name__ == "__main__":
    main()
'''
REF_NAME = "dq_waveform_debug.py"
open(os.path.join(RDIR, REF_NAME), "w").write(REF)

# ---------- check.py ----------
CHECK = r'''import json, os, sys, zipfile, io, subprocess, tempfile, shutil, re, random

CASE = "DqReadPathWaveDebug-001"
HIDDEN_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "assets", CASE, "hidden")

CONDITIONS = [
    ("a", "submit.zip 解压含候选脚本 + diagnosis.json"),
    ("b", "候选脚本 py_compile 通过"),
    ("c", "subprocess 在隐藏 B 上跑通候选并产 diagnosis.json"),
    ("d", "diagnosis.json 可解析且含必需键"),
    ("e", "data_intact==True: 候选正确判定期望数据 golden==actual 一致"),
    ("f", "first_fail_cycle == B 首个 mismatch cycle"),
    ("g", "root_cause_signal == B 的 culprit 信号 slice_swap_sel"),
    ("h", "root_cause_kind == bit_swap（非 gate_disable，反 A 的 bug 类）"),
    ("i", "failing_stage == slice_mux（反 A 的 rd_gate）"),
    ("j", "mismatch_cycles 集合 == B 实际 mismatch cycle 集合"),
    ("k", "expected_signal == dq_data（反 A 的 dq_exp）"),
    ("l", "output_signals == [HI_DQ, LO_DQ]（反 A 的 UPDQP/LPDQPad，反硬编码）"),
    ("m", "enable_signal == read_valid（反 A 的 rd_en）"),
    ("n", "bit_analysis 含 HI_DQ/LO_DQ 的 golden/actual 值且 != 对方"),
    ("o", "3-seed 随机 shuffle 行序后 first_fail/root_cause_signal/root_cause_kind 不变（确定性）"),
]

def _cond(label, ok, detail=""):
    return (label, bool(ok), detail)

def check(deliverable, workdir):
    results = []
    tmp = tempfile.mkdtemp(prefix="chk_dq_")
    try:
        if isinstance(deliverable, (bytes, bytearray)):
            zdata = deliverable
        elif isinstance(deliverable, str) and os.path.isfile(deliverable):
            zdata = open(deliverable, "rb").read()
        else:
            zdata = deliverable
        try:
            zf = zipfile.ZipFile(io.BytesIO(zdata))
            names = zf.namelist()
        except Exception as ex:
            return {"pass": False, "error": "not a zip: %s" % ex, "conditions": []}
        # a: contains script + diagnosis.json
        has_script = any(n.endswith("dq_waveform_debug.py") for n in names)
        has_diag = any(n.endswith("diagnosis.json") for n in names)
        results.append(_cond("a", has_script and has_diag, "names=%s" % names[:10]))
        # extract script
        script_path = None
        for n in names:
            if n.endswith("dq_waveform_debug.py"):
                script_path = os.path.join(tmp, os.path.basename(n))
                open(script_path, "wb").write(zf.read(n))
        if not script_path:
            script_path = os.path.join(tmp, "dq_waveform_debug.py")
        # b: py_compile
        try:
            import py_compile
            py_compile.compile(script_path, doraise=True)
            results.append(_cond("b", True))
        except Exception as ex:
            results.append(_cond("b", False, str(ex)))
        # c: run on B
        gold = os.path.join(HIDDEN_DIR, "golden_trace_B.csv")
        act = os.path.join(HIDDEN_DIR, "actual_trace_B.csv")
        net = os.path.join(HIDDEN_DIR, "dq_readpath_B.v")
        out = os.path.join(tmp, "diag_B.json")
        try:
            r = subprocess.run([sys.executable, script_path, "--golden", gold, "--actual", act,
                                "--netlist", net, "--out", out], capture_output=True, text=True, timeout=120)
            ran = (r.returncode == 0) and os.path.exists(out)
            results.append(_cond("c", ran, "rc=%d stderr=%s" % (r.returncode, r.stderr[:300])))
        except Exception as ex:
            ran = False
            results.append(_cond("c", False, str(ex)))
        diag = {}
        if ran:
            try:
                diag = json.load(open(out))
                results.append(_cond("d", all(k in diag for k in
                    ["expected_signal","output_signals","enable_signal","data_intact",
                     "mismatch_cycles","first_fail_cycle","root_cause_signal",
                     "root_cause_kind","failing_stage","bit_analysis"])))
            except Exception as ex:
                results.append(_cond("d", False, str(ex)))
        else:
            results.append(_cond("d", False, "no diag"))
        if diag:
            results.append(_cond("e", diag.get("data_intact") is True, str(diag.get("data_intact"))))
            exp_first = json.load(open(os.path.join(HIDDEN_DIR, "expected_diagnosis_B.json")))["first_fail_cycle"]
            results.append(_cond("f", diag.get("first_fail_cycle") == exp_first, "got=%s exp=%s" % (diag.get("first_fail_cycle"), exp_first)))
            results.append(_cond("g", diag.get("root_cause_signal") == "slice_swap_sel", str(diag.get("root_cause_signal"))))
            results.append(_cond("h", diag.get("root_cause_kind") == "bit_swap", str(diag.get("root_cause_kind"))))
            results.append(_cond("i", diag.get("failing_stage") == "slice_mux", str(diag.get("failing_stage"))))
            exp_mm = set(json.load(open(os.path.join(HIDDEN_DIR, "expected_diagnosis_B.json")))["mismatch_cycles"])
            got_mm = set(diag.get("mismatch_cycles", []))
            results.append(_cond("j", got_mm == exp_mm, "got=%s exp=%s" % (sorted(got_mm), sorted(exp_mm))))
            results.append(_cond("k", diag.get("expected_signal") == "dq_data", str(diag.get("expected_signal"))))
            results.append(_cond("l", diag.get("output_signals") == ["HI_DQ", "LO_DQ"], str(diag.get("output_signals"))))
            results.append(_cond("m", diag.get("enable_signal") == "read_valid", str(diag.get("enable_signal"))))
            ba = diag.get("bit_analysis", {})
            ba_ok = isinstance(ba, dict) and "HI_DQ" in ba and "LO_DQ" in ba and \
                    ba["HI_DQ"].get("golden") != ba["HI_DQ"].get("actual") and \
                    ba["LO_DQ"].get("golden") != ba["LO_DQ"].get("actual")
            results.append(_cond("n", ba_ok, str(ba)))
        else:
            for lbl in ("e","f","g","h","i","j","k","l","m","n"):
                results.append(_cond(lbl, False, "no diag"))
        # o: 3-seed determinism: shuffle trace rows, re-run, first_fail/cause/kind stable
        det_ok = False
        if ran and diag:
            det_ok = True
            import csv as _csv
            for seed in (1, 2, 3):
                rnd = random.Random(seed)
                g_rows = list(_csv.DictReader(open(os.path.join(HIDDEN_DIR, "golden_trace_B.csv"))))
                a_rows = list(_csv.DictReader(open(os.path.join(HIDDEN_DIR, "actual_trace_B.csv"))))
                order = list(range(len(g_rows))); rnd.shuffle(order)
                g_shuf = [g_rows[i] for i in order]
                a_shuf = [a_rows[i] for i in order]
                gp = os.path.join(tmp, "shuf_%d_golden.csv" % seed)
                ap = os.path.join(tmp, "shuf_%d_actual.csv" % seed)
                with open(gp, "w", newline="") as f2:
                    w2 = _csv.DictWriter(f2, fieldnames=g_rows[0].keys()); w2.writeheader(); w2.writerows(g_shuf)
                with open(ap, "w", newline="") as f3:
                    w3 = _csv.DictWriter(f3, fieldnames=a_rows[0].keys()); w3.writeheader(); w3.writerows(a_shuf)
                out2 = os.path.join(tmp, "diag_shuf_%d.json" % seed)
                rr = subprocess.run([sys.executable, script_path,
                                     "--golden", gp, "--actual", ap,
                                     "--netlist", net, "--out", out2], capture_output=True, text=True, timeout=120)
                if rr.returncode != 0:
                    det_ok = False; break
                d2 = json.load(open(out2))
                if (d2.get("root_cause_signal") != diag.get("root_cause_signal") or
                    d2.get("root_cause_kind") != diag.get("root_cause_kind") or
                    d2.get("first_fail_cycle") != diag.get("first_fail_cycle")):
                    det_ok = False; break
        results.append(_cond("o", det_ok, "determinism"))
        passed = all(ok for _, ok, _ in results)
        return {"pass": passed, "conditions": [{"label": l, "ok": ok, "detail": d} for l, ok, d in results]}
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    import sys
    zpath = sys.argv[1] if len(sys.argv) > 1 else None
    print(json.dumps(check(zpath, "."), indent=2))
'''
open(os.path.join(RDIR, "check.py"), "w").write(CHECK)

# ---------- reference_submit.zip ----------
ref_zip = os.path.join(RDIR, "reference_submit.zip")
with zipfile.ZipFile(ref_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(os.path.join(RDIR, REF_NAME), REF_NAME)
    # generate reference diagnosis on B
    out_diag = os.path.join(RDIR, "diagnosis.json")
    subprocess.run([sys.executable, os.path.join(RDIR, REF_NAME), "--golden",
                    os.path.join(HDIR, "golden_trace_B.csv"), "--actual",
                    os.path.join(HDIR, "actual_trace_B.csv"), "--netlist",
                    os.path.join(HDIR, "dq_readpath_B.v"), "--out", out_diag], check=True,
                   capture_output=True)
    z.write(out_diag, "diagnosis.json")

# ---------- negatives ----------
def make_neg(name, script_body, diag_body=None):
    p = os.path.join(NEGDIR, name)
    open(p, "w").write(script_body)
    # build a submit zip for this neg
    zpath = os.path.join(NEGDIR, name.replace(".py", "_submit.zip"))
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(p, "dq_waveform_debug.py")
        if diag_body is not None:
            dp = os.path.join(NEGDIR, name.replace(".py", "_diagnosis.json"))
            open(dp, "w").write(diag_body)
            z.write(dp, "diagnosis.json")

# neg 1: empty stub
make_neg("neg_empty.py", "# empty\n", "{}")
# neg 2: print only expected (hardcode A names) -> fails on B
make_neg("neg_print_only.py",
    'import sys,json\nprint(json.dumps({"expected_signal":"dq_exp","output_signals":["UPDQP","LPDQPad"],"enable_signal":"rd_en","data_intact":True,"mismatch_cycles":[2,6,10,14,18],"first_fail_cycle":2,"root_cause_signal":"fix_disable_b2","root_cause_kind":"gate_disable","failing_stage":"rd_gate","bit_analysis":{}}))\nopen(sys.argv[sys.argv.index("--out")+1],"w").write("{}")\n',
    json.dumps({"expected_signal":"dq_exp","output_signals":["UPDQP","LPDQPad"],"enable_signal":"rd_en","data_intact":True,"mismatch_cycles":[2,6,10,14,18],"first_fail_cycle":2,"root_cause_signal":"fix_disable_b2","root_cause_kind":"gate_disable","failing_stage":"rd_gate","bit_analysis":{}}))
# neg 3: core deleted (parses but outputs wrong kind)
make_neg("neg_core_deleted.py",
    'import sys,json\nout=sys.argv[sys.argv.index("--out")+1]\njson.dump({"expected_signal":"dq_data","output_signals":["HI_DQ","LO_DQ"],"enable_signal":"read_valid","data_intact":True,"mismatch_cycles":[],"first_fail_cycle":None,"root_cause_signal":"unknown","root_cause_kind":"unknown","failing_stage":"unknown","bit_analysis":{}}, open(out,"w"))\n')
# neg 4: hardcode A (always returns A diagnosis) -> fails l/k/m/g/h/i/j
make_neg("neg_hardcode_a.py",
    'import sys,json\nout=sys.argv[sys.argv.index("--out")+1]\njson.dump({"expected_signal":"dq_exp","output_signals":["UPDQP","LPDQPad"],"enable_signal":"rd_en","data_intact":True,"mismatch_cycles":[2,6,10,14,18],"first_fail_cycle":2,"root_cause_signal":"fix_disable_b2","root_cause_kind":"gate_disable","failing_stage":"rd_gate","stages":["pattern_buf","rd_gate","read_mux","pad_driver"],"bit_analysis":{"UPDQP":{"golden":1,"actual":0},"LPDQPad":{"golden":1,"actual":0}}}, open(out,"w"))\n')
# neg 5: always bit_swap but wrong signal
make_neg("neg_wrong_signal.py",
    'import sys,json\nout=sys.argv[sys.argv.index("--out")+1]\njson.dump({"expected_signal":"dq_data","output_signals":["HI_DQ","LO_DQ"],"enable_signal":"read_valid","data_intact":True,"mismatch_cycles":[3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23],"first_fail_cycle":3,"root_cause_signal":"WRONG_SIG","root_cause_kind":"bit_swap","failing_stage":"WRONG_STAGE","bit_analysis":{"HI_DQ":{"golden":1,"actual":2},"LO_DQ":{"golden":2,"actual":1}}}, open(out,"w"))\n')

# ---------- negative_selftest.py ----------
SELFTEST = r'''import json, os, sys, importlib.util

NEG = os.path.join(os.path.dirname(__file__))
CHECK_PARENT = os.path.dirname(NEG)
sys.path.insert(0, CHECK_PARENT)
import check as chk

negs = ["neg_empty_submit.zip", "neg_print_only_submit.zip", "neg_core_deleted_submit.zip",
        "neg_hardcode_a_submit.zip", "neg_wrong_signal_submit.zip"]
results = {}
for n in negs:
    p = os.path.join(NEG, n)
    if not os.path.exists(p):
        results[n] = "MISSING"; continue
    r = chk.check(p, ".")
    results[n] = {"pass": r["pass"], "failed": [c["label"] for c in r.get("conditions", []) if not c["ok"]]}
all_fail = all(not v.get("pass", False) if isinstance(v, dict) else False for v in results.values())
print(json.dumps({"results": results, "ALL_NEG_FAIL": all_fail, "NEG_RC": sum(1 for v in results.values() if isinstance(v,dict) and v.get("pass"))}, indent=2))
sys.exit(0 if all_fail else 1)
'''
open(os.path.join(NEGDIR, "negative_selftest.py"), "w").write(SELFTEST)

# ---------- task_brief + prompt ----------
TASK_BRIEF = """交付接口：把调试脚本与诊断结果打成 outputs/submit.zip（含 dq_waveform_debug.py + diagnosis.json）。
脚本 CLI：--golden <trace.csv> --actual <trace.csv> --netlist <netlist.v> --out <diagnosis.json>
"""
open(os.path.join(ADIR, "task_brief.md"), "w").write(TASK_BRIEF)

PROMPT = """你是 DDR5 设计验证工程师。现有一份 DDR5 write-pattern 读数据路径的仿真调试任务：

理想（golden）波形在 /rundata/drgqx/V0/simdir/verilog/bin1y/verilog.ddr5.drgqx.move_test/debugtt_1019_2/write_pattern_basic.x16_9200/xcelium.shm/xcelium.trn；
出错（actual）波形在 /rundata/drgqx/V0/simdir/verilog/jinhaoli/gqx_cp/write_pattern_basic_new/write_pattern_basic.x16_9200/xcelium.shm/xcelium.trn。
actual 里 read 出来的期望数据 dq_exp[15:0] 与总线读出来的数据 UPDQP[7:0]、LPDQPad[7:0] 对不上。请帮忙查找电路里哪里出现了问题。

由于原始波形/网表在内网私有路径无法直接读取，附件已把该次仿真的关键产物以文本形式导出：
- assets/golden_trace_A.csv：golden run 的逐 cycle 信号取值表（cycle, dq_exp, rd_en, burst_id, dqs_stb, UPDQP, LPDQPad）
- assets/actual_trace_A.csv：actual run 的逐 cycle 信号取值表（同上）
- assets/dq_readpath_A.v：DQ 读数据路径的网表（pattern_buf → rd_gate → read_mux → pad_driver，输出 UPDQP[7:0]/LPDQPad[7:0]）

请编写一个调试脚本 dq_waveform_debug.py，它接收 golden/actual 两份 CSV 波形表与一份网表，自动完成：
1. 校验期望数据 dq_exp 在 golden 与 actual 之间是否一致（数据完整性）；
2. 逐 cycle 比对输出总线 UPDQP/LPDQPad，找出所有 mismatch 的 cycle 与首个出错 cycle；
3. 解析网表，沿数据路径定位电路里导致 mismatch 的根因信号、出错阶段、bug 类别（如门控使能被常量禁用 / 位切片反转 等）；
4. 输出 diagnosis.json（含 expected_signal、output_signals、enable_signal、data_intact、mismatch_cycles、first_fail_cycle、root_cause_signal、root_cause_kind、failing_stage、stages、bit_analysis）。

脚本须为通用的：信号名从网表端口推导，不得硬编码 A 的具体信号名。把脚本与在附件 A 上跑出的 diagnosis.json 一起打成 outputs/submit.zip 提交。
"""
open(os.path.join(ADIR, "prompt.txt"), "w").write(PROMPT)

print("built", CASE)
print("A mismatch cycles:", [c["cycle"] for c, a in zip(grows, arows) if c["UPDQP"] != a["UPDQP"] or c["LPDQPad"] != a["LPDQPad"]])
print("B mismatch cycles:", B_exp_mismatch, "first:", B_exp_first_fail)
print("B diag expected:", B_DIAG)
