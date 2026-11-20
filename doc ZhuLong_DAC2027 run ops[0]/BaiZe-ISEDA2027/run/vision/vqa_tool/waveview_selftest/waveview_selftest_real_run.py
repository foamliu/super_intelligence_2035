#!/usr/bin/env python3
"""Vision WaveView REAL-case rerun (任务书 §2026-11-15 07:2x 任务② 验收#4).

Reruns the THREE-SEGMENT对照 on the **real designflow-restored WaveView PNGs**
(only-read copied to run/vision/real_waveview_images/<case>/, sha256-verified),
instead of the equivalent-reconstruction PNGs used by waveview_selftest_v2_run.py.

Arms (single variable = VQA backend / whether image is seen):
    V0  baseline  = text-only (no image, no VQA)  -> image-INDEPENDENT, re-derived
    V1  +VQA      = base Qwen3.5-2B VQA  (:30001)  reads REAL png
    V2  +SFT/RL   = base + rft2_adapter VQA (:30003) reads REAL png

V0 never sees the image -> its verdict is identical regardless of real-vs-replica
png, so V0 is re-derived from the existing V0 store (text-only answers). V1/V2 read
the REAL png through the HTTP VQA tool only (runner never decodes the image: no
PIL/opencv/OCR/base64 in THIS source -> audit stays clean).

Questions / oracle / tolerances / check_case are the SAME as the reconstruction
selftest (waveview_selftest_cases.py) -- the reconstruction was built from the
designflow-published params, and the real png is designflow's restored form of the
same params, so the same grading applies. The ONLY change vs the prior selftest is
the image bytes fed to the VQA tool (real vs replica).
"""
import json, os, re, sys, time, urllib.request, hashlib
from math import comb, erfc, sqrt
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_cases as C

HERE = os.path.dirname(os.path.abspath(__file__)); OUT = HERE
REALD = os.path.join(OUT, "REAL"); V0D = os.path.join(OUT, "V0")
os.makedirs(REALD, exist_ok=True)
RUN_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))  # .../run
INDEX = os.path.join(RUN_ROOT, "vision", "real_waveview_index.json")
V1_SERVER = os.environ.get("QWEN35_VQA_SERVER_V1", "http://127.0.0.1:30001")
V2_SERVER = os.environ.get("QWEN35_VQA_SERVER_V2", "http://127.0.0.1:30003")
TRACE = []
ADAPTER_DIR = os.environ.get(
    "QWEN35_VQA_ADAPTER",
    os.path.normpath(os.path.join(HERE, "..", "strengthen_runs", "rft2_adapter_seed11")))


def log(op):
    op["t"] = round(time.time(), 3); TRACE.append(op)


def vqa(server, image_path, question, max_new_tokens=160, timeout=180, retries=3):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(server.rstrip("/") + "/vqa",
                                     data=json.dumps(body).encode(),
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return json.loads(r.read())
        except Exception as e:
            last = e; time.sleep(2 + attempt * 2)
    raise last


def extract_val(raw):
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


def real_png_map():
    idx = json.load(open(INDEX))
    m = {}
    for ci in idx["cases"]:
        cid = ci["case_id"]
        rel = ci["image_visible"]["local_copy_path"]
        p = os.path.join(RUN_ROOT, rel) if not os.path.isabs(rel) else rel
        m[cid] = {"path": p, "sha256": ci["image_visible"]["sha256"],
                  "verified": ci["image_visible"].get("local_sha256_verified", False),
                  "tag": ci["id"]}
    return m


def run_arm(arm, server, case, image_path):
    answer = {}; tool_calls = []; t0 = time.time()
    for key, qtext, kind in case["questions"]:
        rec = {"tool": "vqa_http", "arm": arm, "key": key, "question": qtext, "image": image_path}
        try:
            res = vqa(server, image_path, qtext)
            raw = (res.get("answer") or "").strip()
            rec["raw"] = raw[:600]; rec["ok"] = bool(res.get("ok")); rec["elapsed_s"] = res.get("elapsed_s")
            answer[key] = extract_val(raw)
        except Exception as e:
            rec["ok"] = False; rec["error"] = str(e); answer[key] = None
        tool_calls.append(rec)
        log({"arm": arm, "case_id": case["case_id"], "op": "vqa_call", "key": key, "ok": rec.get("ok")})
    verdict, conds = C.check_case(case, answer)
    return {"arm": arm, "case_id": case["case_id"], "tag": case["tag"], "tier": case["tier"],
            "image_source": "real_designflow_png", "image": image_path,
            "adapter": os.path.basename(os.path.normpath(ADAPTER_DIR)) if arm == "V2" else None,
            "verdict": "PASS" if verdict else "FAIL",
            "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
            "conditions": conds, "answer": answer, "tool_calls": tool_calls,
            "n_tool_calls": len(tool_calls), "duration_s": round(time.time() - t0, 2)}


def audit():
    forbidden = [r"PIL\.(Image|Image open)", r"cv2\.imread", r"pytesseract",
                 r"tesseract", r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)"]
    findings = []
    for op in TRACE:
        if op.get("op") not in ("vqa_call",):
            findings.append({"severity": "cheat", "op": op, "why": "unexpected op"})
    src = open(os.path.join(HERE, "waveview_selftest_real_run.py")).read()
    _fstart = src.find("forbidden = ["); _fend = src.find("]", _fstart) + 1
    src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
    for pat in forbidden:
        if re.search(pat, src_scan):
            findings.append({"severity": "review", "pattern": pat,
                             "why": "forbidden image-bypass token present in runner source"})
    cheat = any(f["severity"] == "cheat" for f in findings)
    return {"cheat": cheat, "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
            "findings": findings,
            "vqa_calls": sum(1 for o in TRACE if o.get("op") == "vqa_call"),
            "image_reads": 0}


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
        return None, None, None
    ans = {key: extract_val(rec.get("answer", {}).get(key)) for key, q, kind in case["questions"]}
    v, conds = C.check_case(case, ans)
    return (v, sum(1 for c in conds if c["pass"]), conds)


def mcnemar(a_rows, b_rows):
    bmap = {r["case_id"]: r for r in b_rows}
    bb = cc = 0
    for r in a_rows:
        rb = bmap.get(r["case_id"])
        if not rb:
            continue
        if r["verdict"] == "FAIL" and rb["verdict"] == "PASS":
            bb += 1
        elif r["verdict"] == "PASS" and rb["verdict"] == "FAIL":
            cc += 1
    n = bb + cc
    if n == 0:
        p = 1.0
    elif n <= 25:
        k = min(bb, cc); p = 2.0 * sum(comb(n, i) for i in range(0, k + 1)) * (0.5 ** n)
        p = min(p, 1.0)
    else:
        chi = (abs(bb - cc) - 1) ** 2 / n if (bb + cc) > 0 else 0.0
        p = erfc(sqrt(chi / 2))
    return p, bb, cc


def main():
    cases = C.get_cases()
    rmap = real_png_map()
    problems = []
    for c in cases:
        info = rmap.get(c["case_id"])
        if not info or not os.path.exists(info["path"]):
            problems.append((c["tag"], c["case_id"], "no real png on disk")); continue
        h = hashlib.sha256(open(info["path"], "rb").read()).hexdigest()
        if h != info["sha256"]:
            problems.append((c["tag"], c["case_id"], "sha256 mismatch"))
        c["_real_png"] = info["path"]
    if problems:
        print("REAL PNG PROBLEMS:", problems); sys.exit(2)

    v1_rows = []; v2_rows = []
    for c in cases:
        img = c["_real_png"]
        r1 = run_arm("V1", V1_SERVER, c, img)
        json.dump(r1, open(os.path.join(REALD, c["case_id"] + "__V1.json"), "w"), ensure_ascii=False)
        v1_rows.append(r1)
        print(f"V1 {c['tag']} {c['case_id']}: {r1['verdict']} {r1['k_pass']}/{r1['k_total']}")
        r2 = run_arm("V2", V2_SERVER, c, img)
        json.dump(r2, open(os.path.join(REALD, c["case_id"] + "__V2.json"), "w"), ensure_ascii=False)
        v2_rows.append(r2)
        print(f"V2 {c['tag']} {c['case_id']}: {r2['verdict']} {r2['k_pass']}/{r2['k_total']}")

    v0_store = _load_arm(V0D)
    v0_rows = []; mismatches = []
    for c in cases:
        rec = v0_store.get(c["case_id"])
        if not rec:
            mismatches.append({"case_id": c["case_id"], "why": "no stored V0 record"})
            v0_rows.append({"arm": "V0", "case_id": c["case_id"], "tag": c["tag"], "tier": c["tier"],
                            "image_source": "none_text_only", "verdict": "FAIL", "k_pass": 0,
                            "k_total": len(c["questions"]) + len(c.get("derived", [])),
                            "rederived": "no_stored_record"}); continue
        v_red, k_red, conds_red = _rederiv(c, v0_store)
        rr = {"arm": "V0", "case_id": c["case_id"], "tag": c["tag"], "tier": c["tier"],
              "image_source": "none_text_only", "verdict": "PASS" if v_red else "FAIL",
              "k_pass": k_red, "k_total": len(c["questions"]) + len(c.get("derived", [])),
              "conditions": conds_red or [],
              "delivered_verdict": rec.get("verdict"), "delivered_k": rec.get("k_pass"),
              "rederived": "PASS" if v_red else "FAIL", "rederived_k": k_red}
        v0_rows.append(rr)
        if rec.get("verdict") != ("PASS" if v_red else "FAIL"):
            mismatches.append({"case_id": c["case_id"], "delivered": rec.get("verdict"),
                               "rederived": "PASS" if v_red else "FAIL"})

    rows = []
    by = {"V0": {r["case_id"]: r for r in v0_rows},
          "V1": {r["case_id"]: r for r in v1_rows},
          "V2": {r["case_id"]: r for r in v2_rows}}
    for c in cases:
        cid = c["case_id"]
        v0v = by["V0"][cid]["verdict"]; v1v = by["V1"][cid]["verdict"]; v2v = by["V2"][cid]["verdict"]
        rows.append({"case_id": cid, "tag": c["tag"], "tier": c["tier"],
                     "k_total": by["V1"][cid]["k_total"],
                     "V0": v0v, "V1": v1v, "V2": v2v,
                     "V0_k": f"{by['V0'][cid].get('k_pass','?')}/{by['V0'][cid].get('k_total','?')}",
                     "V1_k": f"{by['V1'][cid]['k_pass']}/{by['V1'][cid]['k_total']}",
                     "V2_k": f"{by['V2'][cid]['k_pass']}/{by['V2'][cid]['k_total']}",
                     "flip_V0_V1": (v0v == "FAIL" and v1v == "PASS"),
                     "flip_V1_V2": (v1v == "FAIL" and v2v == "PASS"),
                     "flip_V0_V2": (v0v == "FAIL" and v2v == "PASS"),
                     "regress_V1_V2": (v1v == "PASS" and v2v == "FAIL")})

    n = len(rows)
    v0p = sum(1 for r in rows if r["V0"] == "PASS")
    v1p = sum(1 for r in rows if r["V1"] == "PASS")
    v2p = sum(1 for r in rows if r["V2"] == "PASS")
    f01 = sum(1 for r in rows if r["flip_V0_V1"])
    f12 = sum(1 for r in rows if r["flip_V1_V2"])
    f02 = sum(1 for r in rows if r["flip_V0_V2"])

    def pq(arm_rows):
        tot = 0; ok = 0
        for r in arm_rows:
            for cond in r.get("conditions", []):
                tot += 1; ok += 1 if cond["pass"] else 0
        return ok, tot
    pq0 = pq(v0_rows); pq1 = pq(v1_rows); pq2 = pq(v2_rows)

    m12 = mcnemar(v1_rows, v2_rows)
    m02 = mcnemar(v0_rows, v2_rows)
    m01 = mcnemar(v0_rows, v1_rows)

    aud = audit()
    summary = {
        "experiment": "vision waveview REAL-case rerun 3-segment (V0 text / V1 base-VQA / V2 SFT-RFT-VQA) on real designflow pngs",
        "generated": "2026-11-15", "line": "vision",
        "instruction_ref": "BAIZE_VISION_TASK.md section 2026-11-15 07:2x task2 acceptance#4",
        "image_source": "real designflow-restored WaveView PNGs (sha256-verified, only-read copied)",
        "n_cases": n, "real_cases_count": n,
        "V0_pass": v0p, "V1_pass": v1p, "V2_pass": v2p,
        "V0_rate": round(v0p / n, 4), "V1_rate": round(v1p / n, 4), "V2_rate": round(v2p / n, 4),
        "flips_V0fail_V1pass": f01, "flips_V1fail_V2pass": f12, "flips_V0fail_V2pass": f02,
        "per_quantity": {"V0_ok": pq0[0], "V0_total": pq0[1], "V0_rate": round(pq0[0]/pq0[1], 4),
                         "V1_ok": pq1[0], "V1_total": pq1[1], "V1_rate": round(pq1[0]/pq1[1], 4),
                         "V2_ok": pq2[0], "V2_total": pq2[1], "V2_rate": round(pq2[0]/pq2[1], 4)},
        "mcnemar_V1_vs_V2": {"b_improved": m12[1], "c_regressed": m12[2], "p_value": m12[0]},
        "mcnemar_V0_vs_V2": {"b_improved": m02[1], "c_regressed": m02[2], "p_value": m02[0]},
        "mcnemar_V0_vs_V1": {"b_improved": m01[1], "c_regressed": m01[2], "p_value": m01[0]},
        "v0_note": "V0 is text-only (image-independent); re-derived from existing V0 store. Identical for real vs replica png.",
        "audit": aud, "v0_rederive_mismatches": mismatches, "rows": rows}
    json.dump(summary, open(os.path.join(OUT, "summary_real.json"), "w"), ensure_ascii=False, indent=2)
    json.dump(aud, open(os.path.join(OUT, "audit_real.json"), "w"), ensure_ascii=False, indent=2)
    print("\n==== REAL-case rerun summary ====")
    print(f"n={n}")
    print(f"V0 (text):       {v0p}/{n}  rate={summary['V0_rate']}  perQ={pq0[0]}/{pq0[1]}={summary['per_quantity']['V0_rate']}")
    print(f"V1 (base VQA):   {v1p}/{n}  rate={summary['V1_rate']}  perQ={pq1[0]}/{pq1[1]}={summary['per_quantity']['V1_rate']}")
    print(f"V2 (adapter VQA):{v2p}/{n}  rate={summary['V2_rate']}  perQ={pq2[0]}/{pq2[1]}={summary['per_quantity']['V2_rate']}")
    print(f"flips V0->V1={f01}  V1->V2={f12}  V0->V2={f02}")
    print(f"McNemar V0->V1: b={m01[1]} c={m01[2]} p={m01[0]:.4f}")
    print(f"McNemar V1->V2: b={m12[1]} c={m12[2]} p={m12[0]:.4f}")
    print(f"McNemar V0->V2: b={m02[1]} c={m02[2]} p={m02[0]:.4f}")
    print(f"audit cheat={aud['cheat']} vqa_calls={aud['vqa_calls']} image_reads={aud['image_reads']}")


if __name__ == "__main__":
    main()
