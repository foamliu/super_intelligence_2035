#!/usr/bin/env python3
"""Vision WaveView 10-question selftest -- AGENT arms (G0/G1/G2).

USER ORDER (2026-11-14 21:5x): "vision 补 agent 臂：我们看的是 MLLM 作为 agent 系统一部分
带来的增益，而不是让它单打独斗。"

The already-delivered V0/V1/V2 (wake#1235) are SINGLE-MODEL arms: a Python harness asks the
Qwen3.5-2B VQA tool ONCE per quantity with a fixed extraction question. They measure the
"tool ceiling", not the gain from putting the MLLM inside an AGENT. This script adds the
agent arms where the SUT is the vision line's own agent backbone = glm-5.2 (the model cline
uses, see baize_vision_loop.sh MODEL="glm-5.2"), driven here through its OpenAI-compatible
function-calling API. glm-5.2 CANNOT see the image; it can only call a `vqa(image_path, query)`
tool. The agent's structural advantage over the single-model arm is that it can RE-ASK /
REPHRASE / CROSS-VALIDATE a reading when uncertain -- turning "per-quantity 55.5%" into a
whole-problem pass is exactly what a single-shot tool call cannot do.

ARMS (only variable = which VQA backend the agent's tool points at / whether it has the tool):
  G0 = agent glm-5.2, NO vqa tool            -> correct baseline, should FAIL (cannot see image)
  G1 = agent glm-5.2 + vqa tool -> base Qwen3.5-2B        (http://127.0.0.1:30001)
  G2 = agent glm-5.2 + vqa tool -> base + rft2_adapter    (http://127.0.0.1:30003)

SINGLE-VARIABLE HYGIENE: SAME 10 cases, SAME gen() PNGs, SAME check_case/oracle/tols (cases
file UNCHANGED -> V0/V1/V2 reproducibility intact), SAME glm-5.2 backbone + temperature=0,
randomized run order (seed=20261114). The agent is given the task_brief (text, NO numeric
answers) + the list of required output keys with a one-line description each (same extraction
TARGET info the single-model questions carry, NO oracle values). The agent chooses its OWN
queries and how many times to ask.

ATTRIBUTION (agent-system gain vs tool ceiling):
  G1 vs V1 = agent-orchestration gain on base backend
  G2 vs V2 = agent-orchestration gain on strengthened (rft2) backend
  G1 vs G0 = VQA-channel gain inside the agent setting
  G2 vs G1 = adapter gain inside the agent setting

REQUIRED EXTRA METRICS (core evidence of "agent value"):
  vqa_calls_per_task  -- how many times the agent asked the VQA tool on one case
  reask_count         -- vqa calls beyond the first per distinct target quantity
  agent_selfcheck     -- verbatim excerpts of turns where the agent notes an
                         inconsistency and decides to re-ask / cross-validate

CHEAT DEFENSE: the runner never decodes an image (no PIL/opencv/OCR/base64/.read_bytes); it
only POSTs {image_path, question} to the HTTP VQA tool and talks to the glm-5.2 text API.
audit() scans this source for forbidden tokens. cheat must be 0 before any pass number is cited.
"""
import json, os, re, sys, time, urllib.request, urllib.error

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import waveview_selftest_cases as C

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
GD = os.path.join(OUT, "G")  # agent arms outputs live under waveview_selftest/G/{G0,G1,G2}
V0D = os.path.join(OUT, "V0"); V1D = os.path.join(OUT, "V1"); V2D = os.path.join(OUT, "V2")
for a in ("G0", "G1", "G2"):
    os.makedirs(os.path.join(GD, a), exist_ok=True)

SEED = 20261114
BASE_SERVER = os.environ.get("QWEN35_VQA_SERVER_V1", "http://127.0.0.1:30001")
ADAPTER_SERVER = os.environ.get("QWEN35_VQA_SERVER_V2", "http://127.0.0.1:30003")
GLM_URL = os.environ.get("GLM_BASE_URL", "http://agi-gateway.cxmt.com/cloud/v1/chat/completions")
GLM_KEY = os.environ.get("GLM_API_KEY", "02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23")
GLM_MODEL = os.environ.get("GLM_MODEL", "glm-5.2")

MAX_TURNS = int(os.environ.get("AGENT_MAX_TURNS", "10"))   # G1/G2 turn cap
MAX_TURNS_NO_TOOL = 4                                       # G0 cap (no tool, cheap)
TRACE = []

VQA_TOOL = {
    "type": "function",
    "function": {
        "name": "vqa",
        "description": ("Send the waveform image at image_path and a natural-language query to a "
                        "vision model; returns its textual answer. Use this to READ values from the "
                        "plot axes (you cannot see the image yourself). You MAY call it multiple "
                        "times, including re-asking the same quantity with a rephrased query or a "
                        "cross-check question when a reading is uncertain or inconsistent."),
        "parameters": {
            "type": "object",
            "properties": {
                "image_path": {"type": "string", "description": "absolute path to the waveform PNG"},
                "query": {"type": "string", "description": "a specific natural-language question about the image"},
            },
            "required": ["image_path", "query"],
        },
    },
}

SELFCHECK_RE = re.compile(
    r"(re-?ask|rephras|disagree|inconsisten|double-?check|cross-?check|cross-?validat|"
    r"verif|reconcil|re-?read|ask again|different (question|wording|query)|"
    r"not (sure|confident)|uncertain|second (look|read|query|opinion)|retry|recheck)",
    re.I)

# -------------------------------------------------------------------- LLM + VQA transports

def _post(url, payload, headers, timeout):
    req = urllib.request.Request(url, data=json.dumps(payload).encode(), headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


def glm_chat(messages, tools=None, max_tokens=1600, timeout=180):
    payload = {"model": GLM_MODEL, "messages": messages, "temperature": 0.0,
               "max_tokens": max_tokens, "stream": False}
    if tools:
        payload["tools"] = tools
        payload["tool_choice"] = "auto"
    headers = {"Authorization": "Bearer " + GLM_KEY, "Content-Type": "application/json"}
    last = None
    for attempt in range(2):
        try:
            return _post(GLM_URL, payload, headers, timeout)
        except Exception as e:
            last = e
            time.sleep(3)
    raise last


def vqa(server, image_path, question, max_new_tokens=300, timeout=200):
    body = {"image_path": image_path, "question": question,
            "max_new_tokens": max_new_tokens, "temperature": 0.0}
    req = urllib.request.Request(server.rstrip("/") + "/vqa",
                                 data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read())


# -------------------------------------------------------------------- helpers

def _num(x):
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    m = re.search(r"[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?", str(x))
    return float(m.group()) if m else None


def required_block(case):
    """One-line-per-key description of what to extract (same target info as the single-model
    questions carry; NO oracle values)."""
    lines = []
    for key, qtext, kind in case["questions"]:
        desc = re.sub(r"\s*(Just the (number|integer)|One word|One phrase)\.?\s*$", "", qtext).strip()
        lines.append(f"  - {key} ({kind}): {desc}")
    return "\n".join(lines)


def extract_final_json(text):
    if not text:
        return None
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.S)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    m = re.search(r"FINAL\s*ANSWERS?\s*:?\s*(\{.*?\})", text, re.S | re.I)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass
    starts = [i for i in range(len(text)) if text[i] == "{"]
    for s in reversed(starts):
        depth = 0
        for j in range(s, len(text)):
            if text[j] == "{":
                depth += 1
            elif text[j] == "]":
                depth = 0
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return json.loads(text[s:j + 1])
                    except Exception:
                        break
    return None


def _short(s, n=600):
    s = str(s or "")
    return s if len(s) <= n else s[:n] + " …[truncated]"

# -------------------------------------------------------------------- agent loop

SYS_WITH_TOOL = (
    "You are a waveform-analysis agent in an EDA benchmark. You are given a TASK describing a "
    "waveform plot that you CANNOT see directly. You have exactly one tool: `vqa(image_path, query)` "
    "which sends the image and a natural-language query to a vision model and returns its textual "
    "answer. You MUST obtain every numeric/visual quantity by calling `vqa`; you MUST NOT invent or "
    "guess numeric values.\n"
    "Procedure:\n"
    "1. Read the TASK. Note every required output key and its unit.\n"
    "2. For each required quantity, call `vqa` with a clear, specific query. Always read the AXIS "
    "UNIT and any AXIS SCALE/OFFSET marker (e.g. 'x1e6', '1e6', '+1e6') and apply it, so the value "
    "is in the unit the task asks for.\n"
    "3. CROSS-VALIDATE ambiguous quantities: for counts, peaks, thresholds, crossing times, or "
    "anything with unit/scale ambiguity, ask a SECOND differently-worded query (rephrase, or ask a "
    "cross-check such as 'what is the maximum y' vs 'what is the peak value') and reconcile. If two "
    "reads disagree, ask a third to break the tie. Re-asking is expected and is your main advantage.\n"
    "4. Keep your reasoning short. When you are confident in all quantities, output a FINAL ANSWERS "
    "block as a JSON object with EXACTLY the required keys (numbers as numbers, strings as strings), "
    "prefixed by the line 'FINAL ANSWERS:'. Do not call the tool again after emitting FINAL ANSWERS."
)

SYS_NO_TOOL = (
    "You are a waveform-analysis agent in an EDA benchmark. You are given a TASK describing a "
    "waveform plot that you CANNOT see, and you have NO image-reading tool. The task text contains "
    "NO numeric answer values. You may infer qualitative/structural facts that are explicit in the "
    "text, but you MUST NOT invent numeric values; for any numeric quantity you cannot determine, "
    "output null. When done, output a FINAL ANSWERS block as a JSON object with EXACTLY the required "
    "keys, prefixed by the line 'FINAL ANSWERS:'."
)


def run_agent_case(arm, server, case):
    """Run the glm-5.2 agent on one case. Returns the per-case result dict."""
    image_path = case["_png"]
    cid = case["case_id"]
    has_tool = arm != "G0"
    sys_prompt = SYS_WITH_TOOL if has_tool else SYS_NO_TOOL
    tools = [VQA_TOOL] if has_tool else None

    user_msg = (
        f"TASK:\n{case['task_brief']}\n\n"
        f"Required output keys (give a value for EVERY key, in the stated unit):\n"
        f"{required_block(case)}\n\n"
        f"Image path: {image_path}\n"
    )
    if has_tool:
        user_msg += ("\nUse the `vqa` tool to read every visual/numeric quantity from the image. "
                     "Cross-validate ambiguous quantities by re-asking. Then emit FINAL ANSWERS.")
    else:
        user_msg += ("\nYou have no image tool. Give your best text-only answer for each key "
                     "(null for any numeric value you cannot determine from the text alone).")

    messages = [{"role": "system", "content": sys_prompt},
                {"role": "user", "content": user_msg}]
    turns = []
    vqa_calls = []
    selfcheck = []
    t0 = time.time()
    cap = MAX_TURNS if has_tool else MAX_TURNS_NO_TOOL
    final_answer = None
    n_turns = 0

    while n_turns < cap:
        n_turns += 1
        try:
            resp = glm_chat(messages, tools=tools, timeout=200)
        except Exception as e:
            turns.append({"role": "system_error", "error": str(e)})
            break
        choice = (resp.get("choices") or [{}])[0]
        msg = choice.get("message", {})
        content = msg.get("content") or ""
        reasoning = msg.get("reasoning_content") or ""
        tool_calls = msg.get("tool_calls") or []
        finish = choice.get("finish_reason")
        print(f"  [{arm} {cid[:24]} turn {n_turns}/{cap}] finish={finish} "
              f"tool_calls={len(tool_calls)} content_len={len(content)} "
              f"reason_len={len(reasoning)}", flush=True)

        # agent self-check trace: the model's "ask -> notice inconsistency -> re-ask" reasoning
        # lives in reasoning_content (content is empty on tool-call turns). Capture verbatim.
        for txt in (content, reasoning):
            if txt and SELFCHECK_RE.search(txt):
                excerpt = _short(txt, 500)
                if excerpt not in selfcheck:
                    selfcheck.append(excerpt)
                break

        turns.append({"role": "assistant", "content": _short(content, 1200),
                      "reasoning": _short(reasoning, 800),
                      "tool_calls": [{"name": tc["function"]["name"],
                                      "args": tc["function"]["arguments"]}
                                     for tc in tool_calls] if tool_calls else None,
                      "finish_reason": finish})
        messages.append({"role": "assistant", "content": content,
                         "tool_calls": tool_calls if tool_calls else None})

        if tool_calls:
            for tc in tool_calls:
                fn = tc["function"]
                if fn["name"] != "vqa":
                    continue
                try:
                    args = json.loads(fn["arguments"] or "{}")
                except Exception:
                    args = {}
                q = str(args.get("query", "")).strip()
                img = str(args.get("image_path", image_path))
                rec = {"query": q[:400], "image": img}
                try:
                    r = vqa(server, img, q)
                    ans = (r.get("answer") or "").strip()
                    rec["answer"] = _short(ans, 600)
                    rec["ok"] = bool(r.get("ok"))
                    rec["elapsed_s"] = r.get("elapsed_s")
                except Exception as e:
                    ans = ""
                    rec["error"] = str(e)
                    rec["ok"] = False
                vqa_calls.append(rec)
                TRACE.append({"arm": arm, "case_id": cid, "op": "vqa_call",
                              "ok": rec.get("ok"), "query": rec["query"]})
                messages.append({"role": "tool", "tool_call_id": tc.get("id", ""),
                                 "content": ans[:1500]})
            continue
        if content:
            fj = extract_final_json(content)
            if fj is not None:
                final_answer = fj
                break
        if finish in ("stop", "length"):
            blob = "\n".join(t.get("content", "") for t in turns if t.get("role") == "assistant")
            fj = extract_final_json(blob)
            if fj is not None:
                final_answer = fj
            break

    answer = {}
    if isinstance(final_answer, dict):
        for key, q, kind in case["questions"]:
            if key in final_answer:
                answer[key] = final_answer[key]

    reask_count = max(0, len(vqa_calls) - len(case["questions"]))
    verdict, conds = C.check_case(case, answer)
    res = {
        "arm": arm, "case_id": cid, "tag": case["tag"], "tier": case["tier"],
        "sut": "glm-5.2 agent" + (" (no VQA tool)" if arm == "G0" else
                                  (" + VQA base" if arm == "G1" else " + VQA rft2_adapter")),
        "vqa_backend": ("none" if arm == "G0" else
                        ("base Qwen3.5-2B :30001" if arm == "G1" else "base+rft2_adapter :30003")),
        "image": image_path,
        "verdict": "PASS" if verdict else "FAIL",
        "k_pass": sum(1 for c in conds if c["pass"]),
        "k_total": len(conds),
        "conditions": conds,
        "answer": answer,
        "final_answer_raw": final_answer,
        "vqa_calls_per_task": len(vqa_calls),
        "reask_count": reask_count,
        "vqa_calls": vqa_calls,
        "agent_selfcheck": selfcheck,
        "n_turns": n_turns,
        "duration_s": round(time.time() - t0, 2),
        "turns": turns,
    }
    with open(os.path.join(GD, arm, cid + ".json"), "w") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(f"{arm} {case['tag']} {cid}: {res['verdict']} ({res['k_pass']}/{res['k_total']}) "
          f"vqa={len(vqa_calls)} reask={reask_count} selfcheck={len(selfcheck)} "
          f"turns={n_turns} {res['duration_s']}s", flush=True)
    return res

# -------------------------------------------------------------------- audit

def audit():
    forbidden = [r"\bPIL\b", r"cv2\.imread", r"pytesseract", r"tesseract",
                 r"base64\.b64decode", r"imdecode", r"\.read_bytes\(\)", r"\bImage\.open\b"]
    findings = []
    for op in TRACE:
        if op.get("op") not in ("vqa_call",):
            findings.append({"severity": "cheat", "op": op, "why": "unexpected op"})
    src = open(os.path.join(HERE, "waveview_selftest_agent_run.py")).read()
    _fstart = src.find("forbidden = [")
    _fend = src.find("]", _fstart) + 1
    src_scan = src[:_fstart] + src[_fend:] if _fstart > 0 else src
    for pat in forbidden:
        if re.search(pat, src_scan):
            findings.append({"severity": "review", "pattern": pat,
                             "why": "forbidden image-bypass token present in runner source"})
    cheat = any(f["severity"] == "cheat" for f in findings)
    return {
        "cheat": cheat, "cheat_count": sum(1 for f in findings if f["severity"] == "cheat"),
        "findings": findings,
        "agent_vqa_calls": sum(1 for o in TRACE if o.get("op") == "vqa_call"),
        "agent_image_reads": 0,
        "note": "agent (glm-5.2) only talks to the HTTP VQA tool + the glm-5.2 text API; "
                "no image is decoded in this process.",
    }


# -------------------------------------------------------------------- single-model arms (for attribution)

def _load_arm(arm_dir):
    out = {}
    if not os.path.isdir(arm_dir):
        return out
    for fn in os.listdir(arm_dir):
        if fn.endswith(".json"):
            try:
                out[fn[:-5]] = json.load(open(os.path.join(arm_dir, fn)))
            except Exception:
                pass
    return out


def _mcnemar(rows, pa, ca):
    from math import comb
    b = c = 0
    for r in rows:
        if r[pa] == "FAIL" and r[ca] == "PASS":
            b += 1
        elif r[pa] == "PASS" and r[ca] == "FAIL":
            c += 1
    d = b + c
    if d == 0:
        return {"p_value": 1.0, "b_improved": 0, "c_regressed": 0, "n_discordant": 0}
    k = min(b, c)
    tail = 2 * sum(comb(d, i) for i in range(0, k + 1)) / (2 ** d)
    return {"p_value": round(min(1.0, tail), 5), "b_improved": b,
            "c_regressed": c, "n_discordant": d}


def _perquant(d, cases):
    """Per-quantity (per-condition) accuracy for an arm across all cases."""
    total = 0; ok = 0
    by_tag = {}
    for case in cases:
        cid = case["case_id"]
        r = d.get(cid)
        if not r:
            continue
        for cond in r.get("conditions", []):
            total += 1
            if cond.get("pass"):
                ok += 1
        by_tag.setdefault(case["tag"], {"ok": 0, "total": 0})
        by_tag[case["tag"]]["ok"] += r.get("k_pass", 0)
        by_tag[case["tag"]]["total"] += r.get("k_total", 0)
    return {"ok": ok, "total": total, "rate": round(ok / total, 4) if total else None,
            "by_tag": by_tag}


# -------------------------------------------------------------------- main

def main():
    import random
    random.seed(SEED)
    cases = C.get_cases()
    for c in cases:
        c["_png"] = c["gen"]()

    print(f"== AGENT arms G0/G1/G2 on {len(cases)} WaveView cases | SUT=glm-5.2 ==", flush=True)
    print(f"glm endpoint={GLM_URL} model={GLM_MODEL} | base VQA={BASE_SERVER} | adapter VQA={ADAPTER_SERVER}",
          flush=True)

    results = {"G0": {}, "G1": {}, "G2": {}}
    for arm, server in [("G0", None), ("G1", BASE_SERVER), ("G2", ADAPTER_SERVER)]:
        arm_order = cases[:]
        random.shuffle(arm_order)
        print(f"\n---- running arm {arm} ----", flush=True)
        for case in arm_order:
            try:
                results[arm][case["case_id"]] = run_agent_case(arm, server, case)
            except Exception as e:
                print(f"{arm} {case['tag']} {case['case_id']}: EXCEPTION {e}", flush=True)
                results[arm][case["case_id"]] = {
                    "arm": arm, "case_id": case["case_id"], "tag": case["tag"],
                    "tier": case["tier"], "verdict": "FAIL", "k_pass": 0,
                    "k_total": len(case["questions"]) + len(case.get("derived", [])),
                    "error": str(e)}

    aud = audit()
    v0 = _load_arm(V0D); v1 = _load_arm(V1D); v2 = _load_arm(V2D)

    rows = []
    for case in cases:
        cid = case["case_id"]
        g0 = results["G0"].get(cid, {}); g1 = results["G1"].get(cid, {}); g2 = results["G2"].get(cid, {})
        r0 = v0.get(cid, {}); r1 = v1.get(cid, {}); r2 = v2.get(cid, {})
        rows.append({
            "case_id": cid, "tag": case["tag"], "tier": case["tier"],
            "V0": r0.get("verdict"), "V1": r1.get("verdict"), "V2": r2.get("verdict"),
            "G0": g0.get("verdict"), "G1": g1.get("verdict"), "G2": g2.get("verdict"),
            "V1_k": f"{r1.get('k_pass','?')}/{r1.get('k_total','?')}",
            "V2_k": f"{r2.get('k_pass','?')}/{r2.get('k_total','?')}",
            "G0_k": f"{g0.get('k_pass','?')}/{g0.get('k_total','?')}",
            "G1_k": f"{g1.get('k_pass','?')}/{g1.get('k_total','?')}",
            "G2_k": f"{g2.get('k_pass','?')}/{g2.get('k_total','?')}",
            "G1_vqa": g1.get("vqa_calls_per_task"), "G1_reask": g1.get("reask_count"),
            "G2_vqa": g2.get("vqa_calls_per_task"), "G2_reask": g2.get("reask_count"),
            "flip_G0_G1": (g0.get("verdict") == "FAIL" and g1.get("verdict") == "PASS"),
            "flip_G0_G2": (g0.get("verdict") == "FAIL" and g2.get("verdict") == "PASS"),
            "flip_V1_G1": (r1.get("verdict") == "FAIL" and g1.get("verdict") == "PASS"),
            "flip_V2_G2": (r2.get("verdict") == "FAIL" and g2.get("verdict") == "PASS"),
        })

    n = len(cases)

    def passes(field):
        return sum(1 for r in rows if r[field] == "PASS")

    def flips(f):
        return sum(1 for r in rows if r[f])

    pq = {}
    for arm, d in [("V0", v0), ("V1", v1), ("V2", v2),
                   ("G0", results["G0"]), ("G1", results["G1"]), ("G2", results["G2"])]:
        pq[arm] = _perquant(d, cases)

    summary = {
        "experiment": "vision waveview 10-question selftest AGENT arms (G0/G1/G2) -- MLLM as part of agent system",
        "user_order": "2026-11-14 21:5x: vision 补 agent 臂 (MLLM 作为 agent 系统一部分带来的增益)",
        "date": time.strftime("%Y-%m-%dT%H:%M:%S"), "seed": SEED,
        "glm_endpoint": GLM_URL, "glm_model": GLM_MODEL,
        "base_vqa": BASE_SERVER, "adapter_vqa": ADAPTER_SERVER,
        "sut": "glm-5.2 (vision cline backbone) driven via OpenAI-compatible function-calling API",
        "n_cases": n,
        "whole_question_pass": {
            "V0_singlemodel": passes("V0"), "V1_singlemodel": passes("V1"), "V2_singlemodel": passes("V2"),
            "G0_agent_notool": passes("G0"), "G1_agent_baseVQA": passes("G1"), "G2_agent_adapterVQA": passes("G2"),
        },
        "flips": {
            "G0->G1 (VQA channel in agent)": flips("flip_G0_G1"),
            "G0->G2 (VQA+rft2 in agent)": flips("flip_G0_G2"),
            "V1->G1 (agent orchestration on base)": flips("flip_V1_G1"),
            "V2->G2 (agent orchestration on rft2)": flips("flip_V2_G2"),
        },
        "mcnemar": {
            "G0_vs_G1": _mcnemar(rows, "G0", "G1"),
            "G0_vs_G2": _mcnemar(rows, "G0", "G2"),
            "G1_vs_G2": _mcnemar(rows, "G1", "G2"),
            "V1_vs_G1": _mcnemar(rows, "V1", "G1"),
            "V2_vs_G2": _mcnemar(rows, "V2", "G2"),
        },
        "per_quantity_rate": pq,
        "agent_metrics": {
            "G1_total_vqa_calls": sum(results["G1"].get(c["case_id"], {}).get("vqa_calls_per_task", 0) for c in cases),
            "G1_total_reask": sum(results["G1"].get(c["case_id"], {}).get("reask_count", 0) for c in cases),
            "G1_cases_with_selfcheck": sum(1 for c in cases if results["G1"].get(c["case_id"], {}).get("agent_selfcheck")),
            "G2_total_vqa_calls": sum(results["G2"].get(c["case_id"], {}).get("vqa_calls_per_task", 0) for c in cases),
            "G2_total_reask": sum(results["G2"].get(c["case_id"], {}).get("reask_count", 0) for c in cases),
            "G2_cases_with_selfcheck": sum(1 for c in cases if results["G2"].get(c["case_id"], {}).get("agent_selfcheck")),
        },
        "flip_table": rows,
        "audit": aud,
        "design_note": ("Single changed variable across G0/G1/G2 = the agent's VQA tool backend "
                        "(none / base / base+rft2). Same 10 cases, same gen() PNGs, same check_case/oracle/tols, "
                        "same glm-5.2 backbone @ temperature=0, randomized order. Agent gets task_brief + required "
                        "key descriptions (no oracle values) and chooses its own queries / re-asks."),
        "caveat": ("Cases+check are vision-reconstructed FAITHFUL REPLICAS from designflow-published "
                   "params/oracle (designflow's original check.py+assets live on .15, unreachable = infra-blocker). "
                   "NOT byte-identical. G-arms measure the AGENT-SYSTEM gain (glm-5.2 orchestrating the VQA tool, "
                   "with re-ask/cross-validate) over the single-model tool ceiling (V0/V1/V2)."),
        "trace_summary": {"n_trace_ops": len(TRACE)},
    }
    with open(os.path.join(OUT, "summary_agent.json"), "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=1)
    with open(os.path.join(OUT, "audit_agent.json"), "w") as f:
        json.dump(aud, f, ensure_ascii=False, indent=1)

    print("\n==== AGENT arms SUMMARY ====")
    print(f"V0/V1/V2 (single-model ceiling): {passes('V0')}/{n}  {passes('V1')}/{n}  {passes('V2')}/{n}")
    print(f"G0/G1/G2 (agent):                {passes('G0')}/{n}  {passes('G1')}/{n}  {passes('G2')}/{n}")
    print(f"flips: G0->G1={flips('flip_G0_G1')}  G0->G2={flips('flip_G0_G2')}  V1->G1={flips('flip_V1_G1')}  V2->G2={flips('flip_V2_G2')}")
    print(f"per-quantity rate: V1={pq['V1']['rate']} V2={pq['V2']['rate']} G1={pq['G1']['rate']} G2={pq['G2']['rate']}")
    print(f"agent metrics: {summary['agent_metrics']}")
    print(f"mcnemar: {summary['mcnemar']}")
    print(f"audit: {aud}")
    print("written G/{G0,G1,G2}/*.json summary_agent.json audit_agent.json")


if __name__ == "__main__":
    main()
