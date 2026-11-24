#!/usr/bin/env python3
"""P5 synthetic-SFT adapter -> REAL WaveView PNG transfer eval (P5.3 second part).

Evaluates whether the adapter trained on SYNTHETIC waveform images transfers to
REAL designflow WaveView PNGs (10 cases, sha256-verified local copies).

Arms (single variable = VQA backend):
    BASE   = base Qwen3.5-2B VQA (:30001)        reads REAL png
    P5SFT  = base + p5 SFT LoRA adapter (:30004) reads REAL png

Grading = local waveview_selftest_cases.check_case (questions + oracle + tols),
NO 36.15 check.py needed, NO image decoding in this script (VQA HTTP only).
"""
import json, os, re, sys, time, urllib.request
from math import comb

HERE = os.path.dirname(os.path.abspath(__file__))
WVST = os.path.normpath(os.path.join(HERE, "..", "waveview_selftest"))
sys.path.insert(0, WVST)
import waveview_selftest_cases as C

RUN_ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))  # .../run
INDEX = os.path.join(RUN_ROOT, "vision", "real_waveview_index.json")
BASE_SERVER = os.environ.get("BASE_SERVER", "http://127.0.0.1:30001")
P5SFT_SERVER = os.environ.get("P5SFT_SERVER", "http://127.0.0.1:30004")
TRACE = []


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
            "verdict": "PASS" if verdict else "FAIL",
            "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
            "conditions": conds, "answer": answer, "tool_calls": tool_calls,
            "n_tool_calls": len(tool_calls), "duration_s": round(time.time() - t0, 2)}


def mcnemar(a, b):
    n10 = sum(1 for x, y in zip(a, b) if (not x) and y)
    n01 = sum(1 for x, y in zip(a, b) if x and (not y))
    n = n10 + n01
    if n == 0:
        return n10, n01, 1.0
    k = min(n10, n01)
    p_one = sum(comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    p = min(1.0, 2 * p_one)
    return n10, n01, p


def main():
    pngmap = real_png_map()
    cases = C.get_cases()
    print(f"[transfer] {len(cases)} cases | BASE={BASE_SERVER} | P5SFT={P5SFT_SERVER}", flush=True)
    rows_base = []; rows_p5 = []
    for i, case in enumerate(cases):
        cid = case["case_id"]
        info = pngmap.get(cid)
        if not info:
            print(f"[transfer] SKIP {cid}: no real png mapping", flush=True); continue
        img = info["path"]
        if not os.path.exists(img):
            print(f"[transfer] SKIP {cid}: png missing {img}", flush=True); continue
        print(f"[transfer] ({i+1}/{len(cases)}) {cid} tag={case['tag']} img={img}", flush=True)
        rb = run_arm("BASE", BASE_SERVER, case, img)
        rp = run_arm("P5SFT", P5SFT_SERVER, case, img)
        rows_base.append(rb); rows_p5.append(rp)
        print(f"    BASE  verdict={rb['verdict']} k={rb['k_pass']}/{rb['k_total']}", flush=True)
        print(f"    P5SFT verdict={rp['verdict']} k={rp['k_pass']}/{rp['k_total']}", flush=True)

    n = len(rows_base)
    base_pass = [r["verdict"] == "PASS" for r in rows_base]
    p5_pass = [r["verdict"] == "PASS" for r in rows_p5]
    base_n = sum(base_pass); p5_n = sum(p5_pass)
    n10, n01, p = mcnemar(base_pass, p5_pass)
    base_acc = base_n / n if n else 0.0
    p5_acc = p5_n / n if n else 0.0
    delta = p5_acc - base_acc
    both_pass = sum(1 for a, b in zip(base_pass, p5_pass) if a and b)
    both_fail = sum(1 for a, b in zip(base_pass, p5_pass) if (not a) and (not b))

    summary = {
        "task": "P5 SFT adapter transfer to REAL WaveView PNGs",
        "n_cases": n,
        "base": {"server": BASE_SERVER, "pass": base_n, "acc": round(base_acc, 4),
                 "per_case": [{"case_id": r["case_id"], "tag": r["tag"], "verdict": r["verdict"],
                               "k_pass": r["k_pass"], "k_total": r["k_total"]} for r in rows_base]},
        "p5sft": {"server": P5SFT_SERVER, "adapter": "sft_p5_adapter_seed11",
                  "pass": p5_n, "acc": round(p5_acc, 4),
                  "per_case": [{"case_id": r["case_id"], "tag": r["tag"], "verdict": r["verdict"],
                                "k_pass": r["k_pass"], "k_total": r["k_total"]} for r in rows_p5]},
        "delta_acc": round(delta, 4),
        "mcnemar": {"n10_basefail_p5pass": n10, "n01_basepass_p5fail": n01,
                    "n_discordant": n10 + n01, "p_value": round(p, 6)},
        "both_pass": both_pass, "both_fail": both_fail,
        "verdict": "P5 SFT transfer > base" if (delta > 0 and p < 0.05) else
                   ("P5 SFT transfer == base" if delta == 0 else "not significant / negative"),
    }
    out = os.path.join(HERE, "p5_real_waveview_transfer_eval.json")
    with open(out, "w") as f:
        json.dump({"summary": summary, "rows_base": rows_base, "rows_p5": rows_p5,
                   "trace": TRACE}, f, ensure_ascii=False, indent=2)
    print("\n=== TRANSFER EVAL SUMMARY ===", flush=True)
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    print(f"\n[transfer] written -> {out}", flush=True)


if __name__ == "__main__":
    main()
