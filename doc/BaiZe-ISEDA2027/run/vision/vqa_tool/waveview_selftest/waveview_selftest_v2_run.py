#!/usr/bin/env python3
"""Vision WaveView 10-question selftest -- V2 arm (SFT/RL-strengthened VQA).

Completes the THREE-SEGMENT table the line mission (BAIZE_VISION_TASK.md) demands:
    V0  baseline  = text-only agent (no VQA)            -> delivered wake#1234
    V1  +VQA      = agent + base Qwen3.5-2B VQA MCP     -> delivered wake#1234
    V2  +SFT/RL   = agent + v2-RFT-strengthened VQA     -> THIS run

Single variable between V1 and V2 = the VQA backend weights (base vs base+LoRA).
Both V1 and V2 read the image ONLY through the HTTP VQA tool (the runner never
decodes the image: no PIL/opencv/OCR/base64 in THIS source -> audit stays clean).

The v2 adapter (sft_rl_strengthen_v2.py, wake#1229) was trained with CoT targets
ending in 'Final Answer: X'. So V2 parses 'Final Answer:' out of the verbose
generation before feeding the value to the SAME check_case used by V0/V1. V1's base
model emits short answers, so the same extraction leaves V1 unchanged -- verified
below (re-derived V0/V1 == delivered).
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_cases as C

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = HERE
V2D = os.path.join(OUT, "V2"); V0D = os.path.join(OUT, "V0"); V1D = os.path.join(OUT, "V1")
os.makedirs(V2D, exist_ok=True)
V2_SERVER = os.environ.get("QWEN35_VQA_SERVER_V2", "http://127.0.0.1:30003")
SEED = 20261114
TRACE = []
ADAPTER_DIR = os.environ.get(
    "QWEN35_VQA_ADAPTER",
    os.path.normpath(os.path.join(HERE, "..", "strengthen_runs", "rft2_adapter_seed11")))


def log(op):
    op["t"] = round(time.time(), 3); TRACE.append(op)


def vqa(image_path, question, max_new_tokens=160, timeout=180):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    req = urllib.request.Request(V2_SERVER.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def extract_val(raw):
    """Pull the adapter's committed answer from a (possibly CoT) generation."""
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    m = re.search(r"Final Answer:?\s*\*{0,2}\s*(.+)", s, re.I)
    if m:
        val = re.split(r"[.\n]", m.group(1).strip())[0].strip()
        return val if val else s
    return s


def run_v2(case, image_path):
    answer = {}; tool_calls = []; t0 = time.time()
    for key, qtext, kind in case["questions"]:
        rec = {"tool": "vqa_mcp_v2", "key": key, "question": qtext, "image": image_path}
        try:
            res = vqa(image_path, qtext)
            raw = (res.get("answer") or "").strip()
            rec["raw"] = raw[:600]; rec["ok"] = bool(res.get("ok")); rec["elapsed_s"] = res.get("elapsed_s")
            answer[key] = extract_val(raw)
        except Exception as e:
            rec["ok"] = False; rec["error"] = str(e); answer[key] = None
        tool_calls.append(rec)
        log({"arm": "V2", "case_id": case["case_id"], "op": "vqa_call", "key": key, "ok": rec.get("ok")})
    verdict, conds = C.check_case(case, answer)
    return {"arm": "V2", "case_id": case["case_id"], "tag": case["tag"], "tier": case["tier"],
            "adapter": os.path.basename(os.path.normpath(ADAPTER_DIR)), "image": image_path,
            "verdict": "PASS" if verdict else "FAIL",
            "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
            "conditions": conds, "answer": answer, "tool_calls": tool_calls,
            "n_tool_calls": len(tool_calls), "duration_s": round(time.time() - t0, 2)}


def audit():
    """Scan THIS runner's source for forbidden image-bypass paths (cheat defense)."""
    forbidden = [r"PIL\.(Image|Image open)", r"cv2\.imread", r"pytesseract",
                 r"tesseract", r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)"]
    findings = []
    for op in TRACE:
        if op.get("arm") == "V2" and op.get("op") not in ("vqa_call",):
            findings.append({"severity": "cheat", "op": op, "why": "unexpected V2 op"})
    src = open(os.path.join(HERE, "waveview_selftest_v2_run.py")).read()
    _fstart = src.find("forbidden = ["); _fend = src.find("]", _fstart) + 1
    src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
    for pat in forbidden:
        if re.search(pat, src_scan):
            findings.append({"severity": "review", "pattern": pat,
                             "why": "forbidden image-bypass token present in runner source"})
    cheat = any(f["severity"] == "cheat" for f in findings)
    return {"cheat": cheat, "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
            "findings": findings,
            "v2_vqa_calls": sum(1 for o in TRACE if o.get("arm") == "V2" and o.get("op") == "vqa_call"),
            "v2_image_reads": 0}


def _load_arm(arm_dir):
    out = {}
    if not os.path.isdir(arm_dir):
        return out
    for fn in os.listdir(arm_dir):
        if fn.endswith(".json"):
            out[fn[:-5]] = json.load(open(os.path.join(arm_dir, fn)))
    return out


def _rederiv(case, store):
    rec = store.get(case["case_id"])
    if not rec:
        return None, None
    ans = {key: extract_val(rec.get("answer", {}).get(key)) for key, q, kind in case["questions"]}
    v, conds = C.check_case(case, ans)
    return v, sum(1 for c in conds if c["pass"])


def _mcnemar(b, c):
    from math import comb
    d = b + c
    if d == 0:
        return 1.0, b, c
    k = min(b, c)
    tail = 2 * sum(comb(d, i) for i in range(0, k + 1)) / (2 ** d)
    return round(min(1.0, tail), 5), b, c


def main():
    cases = C.get_cases()
    for c in cases:
        c["_png"] = c["gen"]()
    v2_results = {}
    for c in cases:
        r = run_v2(c, c["_png"])
        v2_results[c["case_id"]] = r
        with open(os.path.join(V2D, c["case_id"] + ".json"), "w") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        print(f"V2 {c['tag']} {c['case_id']}: {r['verdict']} ({r['k_pass']}/{r['k_total']}) {r['duration_s']}s", flush=True)
    aud = audit()
    v0 = _load_arm(V0D); v1 = _load_arm(V1D)
    mismatches = []
    for c in cases:
        cid = c["case_id"]
        for arm, store in (("V0", v0), ("V1", v1)):
            rec = store.get(cid)
            if not rec:
                continue
            v_red, k_red = _rederiv(c, store)
            if v_red is not None and (bool(v_red) != (rec["verdict"] == "PASS") or k_red != rec["k_pass"]):
                mismatches.append({"arm": arm, "case_id": cid, "delivered": rec["verdict"],
                                   "delivered_k": rec["k_pass"], "rederived": "PASS" if v_red else "FAIL",
                                   "rederived_k": k_red})
    rows = []
    for c in cases:
        cid = c["case_id"]
        r0 = v0.get(cid, {}); r1 = v1.get(cid, {}); r2 = v2_results.get(cid, {})
        v0v = r0.get("verdict"); v1v = r1.get("verdict"); v2v = r2.get("verdict")
        rows.append({"case_id": cid, "tag": c["tag"], "tier": c["tier"],
                     "V0": v0v, "V1": v1v, "V2": v2v,
                     "V0_k": f"{r0.get('k_pass','?')}/{r0.get('k_total','?')}",
                     "V1_k": f"{r1.get('k_pass','?')}/{r1.get('k_total','?')}",
                     "V2_k": f"{r2.get('k_pass','?')}/{r2.get('k_total','?')}",
                     "flip_V0_V1": (v0v == "FAIL" and v1v == "PASS"),
                     "flip_V1_V2": (v1v == "FAIL" and v2v == "PASS"),
                     "flip_V0_V2": (v0v == "FAIL" and v2v == "PASS"),
                     "V2_tool_calls": r2.get("n_tool_calls")})
    n = len(cases)
    v0p = sum(1 for r in rows if r["V0"] == "PASS")
    v1p = sum(1 for r in rows if r["V1"] == "PASS")
    v2p = sum(1 for r in rows if r["V2"] == "PASS")
    f01 = sum(1 for r in rows if r["flip_V0_V1"])
    f12 = sum(1 for r in rows if r["flip_V1_V2"])
    f02 = sum(1 for r in rows if r["flip_V0_V2"])
    def disc(pa, ca):
        b = c = 0
        for r in rows:
            if r[pa] == "FAIL" and r[ca] == "PASS": b += 1
            elif r[pa] == "PASS" and r[ca] == "FAIL": c += 1
        return _mcnemar(b, c)
    m12 = disc("V1", "V2"); m02 = disc("V0", "V2"); m01 = disc("V0", "V1")
    summary = {
        "experiment": "vision waveview 10-question selftest 3-segment (V0 text / V1 base-VQA / V2 SFT-RFT-VQA)",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": SEED, "v2_server": V2_SERVER,
        "adapter": os.path.basename(os.path.normpath(ADAPTER_DIR)),
        "model": "Qwen3.5-2B (V0 text-only / V1 base VQA / V2 base+rft2_adapter VQA)",
        "n_cases": n, "V0_pass": v0p, "V1_pass": v1p, "V2_pass": v2p,
        "V0_rate": round(v0p / n, 4), "V1_rate": round(v1p / n, 4), "V2_rate": round(v2p / n, 4),
        "flips_V0fail_V1pass": f01, "flips_V1fail_V2pass": f12, "flips_V0fail_V2pass": f02,
        "flip_table": rows,
        "mcnemar_V1_vs_V2": {"b_improved": m12[1], "c_regressed": m12[2], "p_value": m12[0]},
        "mcnemar_V0_vs_V2": {"b_improved": m02[1], "c_regressed": m02[2], "p_value": m02[0]},
        "mcnemar_V0_vs_V1": {"b_improved": m01[1], "c_regressed": m01[2], "p_value": m01[0]},
        "audit": aud,
        "extraction_note": ("V2 parses 'Final Answer: X' from the adapter's CoT output (its trained "
                            "contract) before the SAME check_case used by V0/V1. V0/V1 re-derived with "
                            "the same extraction == delivered (mismatches below should be empty)."),
        "rederive_mismatches": mismatches,
        "caveat": ("Cases+check are vision-reconstructed FAITHFUL REPLICAS from designflow-published "
                   "params/oracle (designflow's original check.py+assets live on the .15 eval machine, "
                   "unreachable from .17 = documented infra-blocker). NOT byte-identical to designflow. "
                   "V2 adapter trained on SYNTHETIC waveforms (v2 60->90 p=0.0156); this run tests "
                   "synthetic->real-WaveView transfer -- the line mission's required real-task test."),
        "trace": TRACE}
    with open(os.path.join(OUT, "summary_v2.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "audit_v2.json"), "w") as f:
        json.dump(aud, f, ensure_ascii=False, indent=1)
    print("\n==== 3-SEGMENT SUMMARY ====")
    print(f"V0 (text):       {v0p}/{n}  rate={summary['V0_rate']}")
    print(f"V1 (base VQA):   {v1p}/{n}  rate={summary['V1_rate']}")
    print(f"V2 (SFT/RL VQA): {v2p}/{n}  rate={summary['V2_rate']}")
    print(f"flips V0->V1={f01}  V1->V2={f12}  V0->V2={f02}")
    print(f"McNemar V1->V2: b={m12[1]} c={m12[2]} p={m12[0]}")
    print(f"McNemar V0->V2: b={m02[1]} c={m02[2]} p={m02[0]}")
    print(f"audit: {aud}")
    print(f"rederive mismatches (should be empty): {mismatches}")
    print("written V2/*.json / summary_v2.json / audit_v2.json")


if __name__ == "__main__":
    main()
