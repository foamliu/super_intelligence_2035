#!/usr/bin/env python3
"""Vision WaveView 10-question selftest runner: V0 (no VQA MCP) vs V1 (with VQA MCP).

V0 arm = agent (Qwen3.5-2B, TEXT-ONLY, no image) receives only the task_brief (which
  contains NO numeric answer values) and produces a JSON answer. Same base model as the
  VQA backend => the ONLY variable between arms is image access via the VQA MCP tool.
  Expected: FAIL (text-only cannot read the waveform figure). This is the correct
  no-multimodal baseline (matches designflow's r650-r658 text-only = all FAIL).
V1 arm = agent calls the Qwen3.5-2B VQA MCP tool (HTTP /vqa backend of
  qwen35_vqa_mcp_server.py) with generic extraction questions per case, assembles the
  JSON answer. The agent NEVER decodes the image itself (no PIL/opencv/OCR/base64) --
  image reading happens ONLY through the VQA tool.

Judging: vision-reimplemented check (k conditions, PASS<=>all pass) from the
designflow-PUBLISHED oracle + tolerances. designflow's original check.py lives on the
.15 eval machine (unreachable from .17 -> documented infra-blocker); vision reconstructed
an equivalent local check. Cases+PNGs are faithful replicas from published params, NOT
byte-identical to designflow's. See report for the full caveat.
"""
import json, os, re, sys, time, random, urllib.request
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_cases as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
V0D = os.path.join(OUT, "V0"); V1D = os.path.join(OUT, "V1")
os.makedirs(V0D, exist_ok=True); os.makedirs(V1D, exist_ok=True)
VQA_SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")
MODEL_PATH = os.environ.get("QWEN35_VQA_MODEL", "/nas_data/app.e0031982/models/Qwen3.5-2B")
SEED = 20261114
TRACE = []  # global audit trace of agent operations


def log(op):
    op["t"] = round(time.time(), 3)
    TRACE.append(op)


def vqa(image_path, question, max_new_tokens=64, timeout=180):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    req = urllib.request.Request(VQA_SERVER.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


# ---------- V1 arm: agent uses the VQA MCP tool (image read ONLY via /vqa) ----------
def run_v1(case, image_path):
    answer = {}
    tool_calls = []
    t0 = time.time()
    for key, qtext, kind in case["questions"]:
        rec = {"tool": "vqa_mcp", "key": key, "question": qtext, "image": image_path}
        try:
            res = vqa(image_path, qtext)
            rec["answer"] = (res.get("answer") or "").strip()
            rec["ok"] = bool(res.get("ok"))
            rec["elapsed_s"] = res.get("elapsed_s")
            answer[key] = rec["answer"]
        except Exception as e:
            rec["ok"] = False; rec["error"] = str(e); answer[key] = None
        tool_calls.append(rec)
        log({"arm": "V1", "case_id": case["case_id"], "op": "vqa_call",
             "key": key, "ok": rec.get("ok")})
    verdict, conds = C.check_case(case, answer)
    return {"arm": "V1", "case_id": case["case_id"], "tag": case["tag"], "tier": case["tier"],
            "image": image_path, "verdict": "PASS" if verdict else "FAIL",
            "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
            "conditions": conds, "answer": answer, "tool_calls": tool_calls,
            "n_tool_calls": len(tool_calls), "duration_s": round(time.time() - t0, 2)}


# ---------- V0 arm: agent TEXT-ONLY (no image, no VQA tool) ----------
_TEXT_MODEL = None


def _load_text_model():
    global _TEXT_MODEL
    if _TEXT_MODEL is not None:
        return _TEXT_MODEL
    import torch
    from transformers import AutoProcessor, Qwen3_5ForConditionalGeneration
    t0 = time.time()
    proc = AutoProcessor.from_pretrained(MODEL_PATH, trust_remote_code=True)
    model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_PATH, torch_dtype=torch.bfloat16, device_map="cuda:0", trust_remote_code=True)
    model.eval()
    _TEXT_MODEL = (proc, model)
    log({"arm": "V0", "op": "load_text_model", "model": MODEL_PATH,
         "load_s": round(time.time() - t0, 1)})
    return _TEXT_MODEL


def text_only_answer(prompt, max_new_tokens=300):
    import torch
    proc, model = _load_text_model()
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    text = proc.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = proc(text=[text], return_tensors="pt").to(model.device)
    with torch.inference_mode():
        out = model.generate(**inputs, max_new_tokens=int(max_new_tokens), do_sample=False)
    return proc.decode(out[0][inputs.input_ids.shape[1]:], skip_special_tokens=True).strip()


def _extract_json(s):
    if not s:
        return {}
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group())
    except Exception:
        try:
            return json.loads(re.sub(r"'\s*:s*", '": ', m.group()).replace("'", '"'))
        except Exception:
            return {}


def run_v0(case):
    keys = [k for k, _, _ in case["questions"]]
    prompt = (case["task_brief"] + "\n\nReturn ONLY a JSON object with exactly these keys: "
              + json.dumps(keys) + ". Fill each from the waveform figure. No explanation.")
    t0 = time.time()
    rec = {"tool": "text_only_model", "prompt": prompt}
    raw = ""
    try:
        raw = text_only_answer(prompt)
        rec["ok"] = True
    except Exception as e:
        rec["ok"] = False; rec["error"] = repr(e)
    rec["raw"] = raw[:1500]
    answer = _extract_json(raw)
    # explicit: V0 did NOT read the image and did NOT call /vqa (audit-enforced)
    log({"arm": "V0", "case_id": case["case_id"], "op": "text_only_call",
         "image_read": False, "vqa_called": False})
    verdict, conds = C.check_case(case, answer)
    return {"arm": "V0", "case_id": case["case_id"], "tag": case["tag"], "tier": case["tier"],
            "verdict": "PASS" if verdict else "FAIL",
            "k_pass": sum(1 for c in conds if c["pass"]), "k_total": len(conds),
            "conditions": conds, "answer": answer, "tool_calls": [rec],
            "n_tool_calls": 1, "duration_s": round(time.time() - t0, 2),
            "note": "text-only; image NOT read; VQA NOT called (no VQA MCP in V0)"}


def audit():
    """Scan agent trace + this runner's source for forbidden image-bypass paths."""
    forbidden = [r"PIL\.(Image|Image open)", r"cv2\.imread", r"pytesseract", r"tesseract",
                 r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)"]
    findings = []
    # 1) trace-level: V0 must not call vqa / read image; V1 must only call vqa_call
    for op in TRACE:
        arm = op.get("arm")
        if arm == "V0" and op.get("op") in ("vqa_call", "image_read"):
            findings.append({"severity": "cheat", "op": op, "why": "V0 arm touched image/vqa"})
    # 2) static: grep own source for forbidden tokens (answer-derivation paths).
    #    Exclude THIS audit() function's own forbidden-pattern definition lines
    #    so the regex strings don't self-match (they are patterns, not usage).
    src = open(os.path.join(HERE, "waveview_selftest_run.py")).read()
    _fstart = src.find("forbidden = [")
    _fend = src.find("]", _fstart) + 1
    src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
    for pat in forbidden:
        if re.search(pat, src_scan):
            findings.append({"severity": "review", "pattern": pat,
                             "why": "forbidden image-bypass token present in runner source"})
    cheat = any(f["severity"] == "cheat" for f in findings)
    return {"cheat": cheat, "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
            "findings": findings, "v0_vqa_calls": sum(1 for o in TRACE if o.get("arm") == "V0" and o.get("op") == "vqa_call"),
            "v1_vqa_calls": sum(1 for o in TRACE if o.get("arm") == "V1" and o.get("op") == "vqa_call"),
            "v0_image_reads": sum(1 for o in TRACE if o.get("arm") == "V0" and o.get("op") == "image_read")}


def main():
    cases = C.get_cases()
    # regenerate all faithful PNGs once (asset prep, NOT answer derivation)
    for c in cases:
        c["_png"] = c["gen"]()
    # randomize V0/V1 order per case (seed recorded) to avoid order effects
    rng = random.Random(SEED)
    order = []
    for c in cases:
        seq = ["V0", "V1"]
        rng.shuffle(seq)
        order.append((c, seq))
    results = {"V0": {}, "V1": {}}
    for c, seq in order:
        for arm in seq:
            if arm == "V0":
                r = run_v0(c)
                results["V0"][c["case_id"]] = r
                with open(os.path.join(V0D, c["case_id"] + ".json"), "w") as f:
                    json.dump(r, f, ensure_ascii=False, indent=1)
            else:
                r = run_v1(c, c["_png"])
                results["V1"][c["case_id"]] = r
                with open(os.path.join(V1D, c["case_id"] + ".json"), "w") as f:
                    json.dump(r, f, ensure_ascii=False, indent=1)
            print(f"{arm} {c['tag']} {c['case_id']}: {r['verdict']} ({r['k_pass']}/{r['k_total']}) {r['duration_s']}s", flush=True)
    aud = audit()
    # flip table
    flips = []
    for c in cases:
        cid = c["case_id"]; v0 = results["V0"][cid]; v1 = results["V1"][cid]
        flips.append({"case_id": cid, "tag": c["tag"], "tier": c["tier"],
                      "V0": v0["verdict"], "V1": v1["verdict"],
                      "flipped": (v0["verdict"] == "FAIL" and v1["verdict"] == "PASS"),
                      "V0_k": f"{v0['k_pass']}/{v0['k_total']}",
                      "V1_k": f"{v1['k_pass']}/{v1['k_total']}",
                      "V1_tool_calls": v1["n_tool_calls"]})
    v0_pass = sum(1 for c in cases if results["V0"][c["case_id"]]["verdict"] == "PASS")
    v1_pass = sum(1 for c in cases if results["V1"][c["case_id"]]["verdict"] == "PASS")
    n_flip = sum(1 for fl in flips if fl["flipped"])
    summary = {
        "experiment": "vision waveview 10-question selftest (V0 no-VQA vs V1 with-VQA-MCP)",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": SEED,
        "vqa_server": VQA_SERVER, "text_model": MODEL_PATH,
        "model": "Qwen3.5-2B (same weights both arms; V0 text-only / V1 VL via VQA tool)",
        "n_cases": len(cases), "V0_pass": v0_pass, "V1_pass": v1_pass,
        "V0_rate": round(v0_pass / len(cases), 4), "V1_rate": round(v1_pass / len(cases), 4),
        "flips_V0fail_V1pass": n_flip, "flip_table": flips,
        "audit": aud,
        "caveat": ("Cases+check are vision-reconstructed FAITHFUL REPLICAS from designflow-published "
                   "params/oracle (designflow's original check.py+assets live on the .15 eval machine, "
                   "unreachable from .17 = documented infra-blocker). NOT byte-identical to designflow. "),
        "trace": TRACE}
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "audit.json"), "w") as f:
        json.dump(aud, f, ensure_ascii=False, indent=1)
    print("\n==== SUMMARY ====")
    print(f"V0 (no VQA): {v0_pass}/{len(cases)}  V1 (with VQA MCP): {v1_pass}/{len(cases)}  flips={n_flip}")
    print("audit:", aud)
    print("written summary.json / audit.json / V0/*.json / V1/*.json")


if __name__ == "__main__":
    main()
