#!/usr/bin/env python3
"""Vision WaveView 10-question selftest -- V3 arm (unit/scale-aware CoT prompting ablation).

The wake#1235 three-segment result (V0 text / V1 base-VQA / V2 base+rft2_adapter-VQA)
delivered 0/10 whole-question PASS but per-quantity 30.9%->38.2%->55.5%. The closest
case b11 (SimFailFsdbProbe) sat at 10/12; its 2 misses (fail_time, window_start) were
UNIT/SCALE errors: matplotlib renders the ps axis as mantissa 1.340..1.375 with a hidden
'x1e6' offset, and the VQA read the mantissa but dropped the scale factor (answered
1363 / 1.340 instead of 1,363,000 / 1,340,000 ps).
V3 tests a GENERAL fix -- a unit/scale-aware CoT suffix appended to every TIME-quantity
extraction question, telling the VQA to read the axis scale/offset and multiply it out.
This is the 'CoT dusuli tuijilian' the line mission names; it is a PROMPT lever, not a
weight lever, applied UNIFORMLY to all time questions across all 10 cases (not tuned to gold).

SINGLE-VARIABLE HYGIENE: SAME PNGs (cases.gen() unchanged), SAME check_case/oracle/tols
(cases file UNCHANGED -- V0/V1/V2 reproducibility intact), SAME two VQA backends.
The ONLY changed variable = the VQA extraction-question text for time quantities.
We run the CoT prompt on BOTH backends for attribution:
  V1c = base Qwen3.5-2B VQA + unit-CoT  (vs delivered V1 = base, no CoT)
  V2c = base+rft2_adapter   + unit-CoT  (vs delivered V2 = adapter, no CoT)
  V2c-vs-V2 = CoT-prompt gain on the strengthened model
  V1c-vs-V1 = CoT-prompt gain on the base model
  V2c-vs-V1c = adapter gain UNDER the CoT prompt

CHEAT DEFENSE: the runner never decodes an image (no PIL/opencv/OCR/base64/.read_bytes);
it only POSTs {image_path, question} to the HTTP VQA tool and parses text. audit() scans
this source for forbidden tokens. cheat must be 0 before any pass number is cited.
"""
import json, os, re, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_cases as C

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = HERE
V3D = os.path.join(OUT, "V3")
V0D = os.path.join(OUT, "V0"); V1D = os.path.join(OUT, "V1"); V2D = os.path.join(OUT, "V2")
os.makedirs(os.path.join(V3D, "V1c"), exist_ok=True)
os.makedirs(os.path.join(V3D, "V2c"), exist_ok=True)
BASE_SERVER = os.environ.get("QWEN35_VQA_SERVER_V1", "http://127.0.0.1:30001")
ADAPTER_SERVER = os.environ.get("QWEN35_VQA_SERVER_V2", "http://127.0.0.1:30003")
SEED = 20261114
TRACE = []
ADAPTER_DIR = os.environ.get(
    "QWEN35_VQA_ADAPTER",
    os.path.normpath(os.path.join(HERE, "..", "strengthen_runs", "rft2_adapter_seed11")))

TIME_COT = (
    " Look very carefully at the x-axis: near the axis label there is often a SMALL scale or "
    "offset marker such as 'x1e6', '1e6', 'x10^6', or '+1e6'. Reason step by step: "
    "(1) state the x-axis unit; (2) state the scale factor shown (if there is none, the scale is 1); "
    "(3) read the tick mantissa closest to the requested point; "
    "(4) full_value = mantissa x scale_factor; (5) if the question asks a different unit, convert full_value. "
    "End your reply with exactly one line 'Final Answer: <number>' where <number> is in the unit the question asked."
)

_TIME_RE = re.compile(r"(time|\bps\b|\bns\b|\bus\b|us|window)", re.I)


def is_time_question(qtext, key):
    return bool(_TIME_RE.search(qtext) or _TIME_RE.search(str(key)))


def with_cot(qtext, key, kind):
    if kind == "num" and is_time_question(qtext, key):
        return qtext + TIME_COT
    return qtext


def log(op):
    op["t"] = round(time.time(), 3); TRACE.append(op)


def vqa(server, image_path, question, max_new_tokens=300, timeout=180):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    req = urllib.request.Request(server.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def extract_val(raw):
    if raw is None:
        return None
    s = str(raw).strip()
    if not s:
        return None
    matches = list(re.finditer(r"Final Answer:?\s*\*{0,2}\s*([-+]?[\d.,eE]+)", s, re.I))
    if matches:
        val = matches[-1].group(1).strip().rstrip(".")
        return val if val else s
    nums = re.findall(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", s)
    return nums[-1] if nums else s


def run_arm(arm, server, cases):
    out_dir = os.path.join(V3D, arm)
    results = {}
    for case in cases:
        image_path = case["_png"]
        answer = {}; tool_calls = []; t0 = time.time()
        for key, qtext, kind in case["questions"]:
            q = with_cot(qtext, key, kind)
            rec = {"tool": "vqa_mcp_v3", "key": key, "question": q, "cot_applied": (q != qtext),
                   "image": image_path}
            try:
                res = vqa(server, image_path, q)
                raw = (res.get("answer") or "").strip()
                rec["raw"] = raw[:800]; rec["ok"] = bool(res.get("ok")); rec["elapsed_s"] = res.get("elapsed_s")
                answer[key] = extract_val(raw)
            except Exception as e:
                rec["ok"] = False; rec["error"] = str(e); answer[key] = None
            tool_calls.append(rec)
            log({"arm": arm, "case_id": case["case_id"], "op": "vqa_call", "key": key, "ok": rec.get("ok")})
        verdict, conds = C.check_case(case, answer)
        r = {"arm": arm, "case_id": case["case_id"], "tag": case["tag"], "tier": case["tier"],
             "adapter": ("rft2_adapter_seed11" if arm == "V2c" else "none(base)"),
             "image": image_path, "verdict": "PASS" if verdict else "FAIL",
             "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
             "conditions": conds, "answer": answer, "tool_calls": tool_calls,
             "n_tool_calls": len(tool_calls), "duration_s": round(time.time() - t0, 2)}
        results[case["case_id"]] = r
        with open(os.path.join(out_dir, case["case_id"] + ".json"), "w") as f:
            json.dump(r, f, ensure_ascii=False, indent=1)
        print(f"{arm} {case['tag']} {case['case_id']}: {r['verdict']} ({r['k_pass']}/{r['k_total']}) {r['duration_s']}s", flush=True)
    return results


_CASES = []


def audit():
    forbidden = [r"PIL\.(Image|Image open)", r"cv2\.imread", r"pytesseract",
                 r"tesseract", r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)"]
    findings = []
    for op in TRACE:
        if op.get("op") not in ("vqa_call",):
            findings.append({"severity": "cheat", "op": op, "why": "unexpected op"})
    src = open(os.path.join(HERE, "waveview_selftest_v3_run.py")).read()
    _fstart = src.find("forbidden = ["); _fend = src.find("]", _fstart) + 1
    src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
    for pat in forbidden:
        if re.search(pat, src_scan):
            findings.append({"severity": "review", "pattern": pat,
                             "why": "forbidden image-bypass token present in runner source"})
    cheat = any(f["severity"] == "cheat" for f in findings)
    return {"cheat": cheat, "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
            "findings": findings,
            "v3_vqa_calls": sum(1 for o in TRACE if o.get("op") == "vqa_call"),
            "v3_image_reads": 0,
            "time_questions_with_cot": sum(1 for c in _CASES for k, q, kd in c["questions"]
                                           if is_time_question(q, k))}


def _load_arm(arm_dir):
    out = {}
    if not os.path.isdir(arm_dir):
        return out
    for fn in os.listdir(arm_dir):
        if fn.endswith(".json"):
            out[fn[:-5]] = json.load(open(os.path.join(arm_dir, fn)))
    return out


def _mcnemar(b, c):
    from math import comb
    d = b + c
    if d == 0:
        return 1.0, b, c
    k = min(b, c)
    tail = 2 * sum(comb(d, i) for i in range(0, k + 1)) / (2 ** d)
    return round(min(1.0, tail), 5), b, c


def main():
    global _CASES
    cases = C.get_cases()
    for c in cases:
        c["_png"] = c["gen"]()
    _CASES = cases
    print(f"== V3 unit/scale-aware CoT ablation: {len(cases)} cases ==", flush=True)
    v1c = run_arm("V1c", BASE_SERVER, cases)
    v2c = run_arm("V2c", ADAPTER_SERVER, cases)
    aud = audit()
    v0 = _load_arm(V0D); v1 = _load_arm(V1D); v2 = _load_arm(V2D)
    rows = []
    for c in cases:
        cid = c["case_id"]
        r0 = v0.get(cid, {}); r1 = v1.get(cid, {}); r2 = v2.get(cid, {})
        r1c = v1c.get(cid, {}); r2c = v2c.get(cid, {})
        rows.append({"case_id": cid, "tag": c["tag"], "tier": c["tier"],
                     "V0": r0.get("verdict"), "V1": r1.get("verdict"), "V2": r2.get("verdict"),
                     "V1c": r1c.get("verdict"), "V2c": r2c.get("verdict"),
                     "V1_k": f"{r1.get('k_pass','?')}/{r1.get('k_total','?')}",
                     "V2_k": f"{r2.get('k_pass','?')}/{r2.get('k_total','?')}",
                     "V1c_k": f"{r1c.get('k_pass','?')}/{r1c.get('k_total','?')}",
                     "V2c_k": f"{r2c.get('k_pass','?')}/{r2c.get('k_total','?')}",
                     "flip_V1_V1c": (r1.get("verdict") == "FAIL" and r1c.get("verdict") == "PASS"),
                     "flip_V2_V2c": (r2.get("verdict") == "FAIL" and r2c.get("verdict") == "PASS"),
                     "flip_V0_V1c": (r0.get("verdict") == "FAIL" and r1c.get("verdict") == "PASS"),
                     "flip_V0_V2c": (r0.get("verdict") == "FAIL" and r2c.get("verdict") == "PASS")})
    n = len(cases)
    def passes(field):
        return sum(1 for r in rows if r[field] == "PASS")
    def flips(f):
        return sum(1 for r in rows if r[f])
    def disc(pa, ca):
        b = c = 0
        for r in rows:
            if r[pa] == "FAIL" and r[ca] == "PASS": b += 1
            elif r[pa] == "PASS" and r[ca] == "FAIL": c += 1
        return _mcnemar(b, c)
    summary = {
        "experiment": "vision waveview 10-question selftest V3 (unit/scale-aware CoT prompting ablation)",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": SEED,
        "base_server": BASE_SERVER, "adapter_server": ADAPTER_SERVER,
        "adapter": os.path.basename(os.path.normpath(ADAPTER_DIR)),
        "model": "Qwen3.5-2B (V1c = base+CoT / V2c = base+rft2_adapter+CoT)",
        "n_cases": n,
        "V0_pass": passes("V0"), "V1_pass": passes("V1"), "V2_pass": passes("V2"),
        "V1c_pass": passes("V1c"), "V2c_pass": passes("V2c"),
        "flips_V1_to_V1c": flips("flip_V1_V1c"),
        "flips_V2_to_V2c": flips("flip_V2_V2c"),
        "flips_V0_to_V1c": flips("flip_V0_V1c"),
        "flips_V0_to_V2c": flips("flip_V0_V2c"),
        "mcnemar_V2_vs_V2c": dict(zip(["p_value", "b_improved", "c_regressed"], disc("V2", "V2c"))),
        "mcnemar_V1_vs_V1c": dict(zip(["p_value", "b_improved", "c_regressed"], disc("V1", "V1c"))),
        "mcnemar_V1c_vs_V2c": dict(zip(["p_value", "b_improved", "c_regressed"], disc("V1c", "V2c"))),
        "flip_table": rows, "audit": aud,
        "design_note": ("Single changed variable vs delivered V1/V2 = VQA extraction-question text for TIME "
                        "quantities (unit/scale-aware CoT suffix). PNGs, check_case, oracle, tols, backends UNCHANGED."),
        "caveat": ("Cases+check are vision-reconstructed FAITHFUL REPLICAS from designflow-published params/oracle "
                   "(designflow's original check.py+assets live on .15, unreachable = infra-blocker). NOT byte-identical. "
                   "V3 measures a PROMPT lever (CoT) on real WaveView-replica cases; does not change check/oracle/assets."),
        "trace": TRACE}
    with open(os.path.join(OUT, "summary_v3.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "audit_v3.json"), "w") as f:
        json.dump(aud, f, ensure_ascii=False, indent=1)
    print("\n==== V3 (unit/scale-aware CoT) SUMMARY ====")
    print(f"V0  (text):        {passes('V0')}/{n}")
    print(f"V1  (base):        {passes('V1')}/{n}   V1c (base+CoT):   {passes('V1c')}/{n}")
    print(f"V2  (adapter):     {passes('V2')}/{n}   V2c (adapter+CoT):{passes('V2c')}/{n}")
    print(f"flips V1->V1c={flips('flip_V1_V1c')}  V2->V2c={flips('flip_V2_V2c')}  V0->V1c={flips('flip_V0_V1c')}  V0->V2c={flips('flip_V0_V2c')}")
    print(f"McNemar V2->V2c: {summary['mcnemar_V2_vs_V2c']}")
    print(f"McNemar V1->V1c: {summary['mcnemar_V1_vs_V1c']}")
    print(f"audit: {aud}")
    print("written V3/V1c/*.json V3/V2c/*.json summary_v3.json audit_v3.json")


if __name__ == "__main__":
    main()
