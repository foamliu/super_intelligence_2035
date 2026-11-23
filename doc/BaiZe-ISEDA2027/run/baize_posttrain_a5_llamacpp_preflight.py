#!/usr/bin/env python3
"""baize_posttrain_a5_llamacpp_preflight.py -- gate the A5 llama.cpp Q4_K_M run.

WHY: the 19:53 speed probe only proved throughput (132.52 tok/s aggregate) and
that the server STARTS with --jinja. It did NOT prove cline can actually use it:
tool_calls parsing, streaming tool deltas, and batch-level determinism are all
unverified. Running 158 tasks (~5h) without these gates risks another silent
93.75%-empty-code contamination, which must never be reported as a capability
number (doc/AGENTS.md 铁律 2).

Gates (all must pass; exit 0 only if all pass):
  P0 identity    /v1/models id == expected alias (B1 身份四证 part 1)
  P1 tool        non-stream: finish_reason=tool_calls + function.name/args parse
  P2 tool        stream=true: tool_calls arrive (delta or final chunk)
  P3 roundtrip   tool result fed back -> model returns a final text answer
  P4 determinism 10 prompts x 3 repeats at temp 0 -> zero content flips
  P5 thinking    a trivial prompt returns a SHORT answer (no leaked long CoT)

Usage:
  python3 baize_posttrain_a5_llamacpp_preflight.py --port 8095 \
      --expected qwen3.5-2b-a5 --out run/a5_llamacpp_preflight_<ts>.json
"""
import argparse
import hashlib
import json
import sys
import time
import urllib.request

TOOLS = [{
    "type": "function",
    "function": {
        "name": "calc",
        "description": "Evaluate a simple arithmetic expression and return its value.",
        "parameters": {
            "type": "object",
            "properties": {"expr": {"type": "string", "description": "e.g. 2+2"}},
            "required": ["expr"],
        },
    },
}]


def post(url, payload, timeout=600, stream=False):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req, timeout=timeout)
    if not stream:
        return json.loads(resp.read().decode("utf-8")), None
    return None, resp


def get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def collect_stream(resp):
    """Return (content, tool_calls, finish_reason) from an OpenAI SSE stream."""
    content, calls, finish = [], {}, None
    for raw in resp:
        line = raw.decode("utf-8", "replace").strip()
        if not line or not line.startswith("data:"):
            continue
        data = line[5:].strip()
        if data == "[DONE]":
            break
        try:
            obj = json.loads(data)
        except Exception:  # noqa: BLE001
            continue
        for ch in obj.get("choices", []) or []:
            delta = ch.get("delta") or {}
            if delta.get("content"):
                content.append(delta["content"])
            for tc in delta.get("tool_calls") or []:
                idx = tc.get("index", 0)
                slot = calls.setdefault(idx, {"name": "", "args": ""})
                fn = tc.get("function") or {}
                if fn.get("name"):
                    slot["name"] += fn["name"]
                if fn.get("arguments"):
                    slot["args"] += fn["arguments"]
            if ch.get("finish_reason"):
                finish = ch["finish_reason"]
    out = []
    for idx in sorted(calls):
        out.append({"name": calls[idx]["name"], "arguments": calls[idx]["args"]})
    return "".join(content), out, finish


def parse_args_ok(raw):
    if isinstance(raw, dict):
        return True, raw
    try:
        return True, json.loads(raw or "{}")
    except Exception:  # noqa: BLE001
        return False, {}


def text_completion(base, model, prompt, max_tokens=64):
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0,
        "top_k": 1,
        "seed": 1234,
        "stream": False,
    }
    obj, _ = post(base + "/chat/completions", body)
    ch = (obj.get("choices") or [{}])[0]
    msg = ch.get("message") or {}
    return (msg.get("content") or ""), ch.get("finish_reason"), obj


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8095)
    ap.add_argument("--expected", default="qwen3.5-2b-a5")
    ap.add_argument("--out", default="")
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--timeout", type=int, default=900)
    a = ap.parse_args()

    base = "http://127.0.0.1:%d/v1" % a.port
    res = {"port": a.port, "expected": a.expected, "gates": {}, "details": {}}
    ok = True

    # P0 identity
    try:
        models = get_json(base + "/models")
        served = [m.get("id") for m in models.get("data", [])]
        res["details"]["served_ids"] = served
        p0 = a.expected in served
    except Exception as exc:  # noqa: BLE001
        res["details"]["identity_error"] = repr(exc)
        p0 = False
    res["gates"]["P0_identity"] = p0
    ok = ok and p0
    if not p0:
        _write(a, res, ok)
        return 1

    model = a.expected
    tool_msg = {"role": "user",
                "content": "Use the calc tool to compute 17*23. Do not answer directly."}

    # P1 non-stream tool call
    try:
        obj, _ = post(base + "/chat/completions", {
            "model": model, "messages": [tool_msg], "tools": TOOLS,
            "tool_choice": "auto", "temperature": 0, "top_k": 1, "seed": 1234,
            "max_tokens": 256, "stream": False,
        }, timeout=a.timeout)
        ch = (obj.get("choices") or [{}])[0]
        calls = (ch.get("message") or {}).get("tool_calls") or []
        if calls:
            args_ok, args = parse_args_ok((calls[0].get("function") or {}).get("arguments"))
        else:
            args_ok, args = False, {}
        p1 = bool(calls) and ch.get("finish_reason") == "tool_calls" and args_ok
        res["details"]["p1"] = {"finish": ch.get("finish_reason"), "n_calls": len(calls),
                                "args_ok": args_ok, "args": args}
    except Exception as exc:  # noqa: BLE001
        p1 = False
        res["details"]["p1_error"] = repr(exc)
    res["gates"]["P1_tool_nonstream"] = p1
    ok = ok and p1

    # P2 streaming tool call
    scalls = []
    try:
        _, resp = post(base + "/chat/completions", {
            "model": model, "messages": [tool_msg], "tools": TOOLS,
            "tool_choice": "auto", "temperature": 0, "top_k": 1, "seed": 1234,
            "max_tokens": 256, "stream": True,
        }, timeout=a.timeout, stream=True)
        content, scalls, finish = collect_stream(resp)
        p2 = bool(scalls) and bool(scalls[0].get("name")) \
            and parse_args_ok(scalls[0].get("arguments"))[0]
        res["details"]["p2"] = {"content_len": len(content), "calls": scalls, "finish": finish}
    except Exception as exc:  # noqa: BLE001
        p2 = False
        res["details"]["p2_error"] = repr(exc)
    res["gates"]["P2_tool_stream"] = p2
    ok = ok and p2

    # P3 round-trip with tool result
    p3 = False
    try:
        if p2:
            call = scalls[0]
            msgs = [tool_msg,
                    {"role": "assistant", "content": "", "tool_calls": [{
                        "id": "call_0", "type": "function",
                        "function": {"name": call["name"], "arguments": call["arguments"]}}]},
                    {"role": "tool", "tool_call_id": "call_0", "content": "391"}]
            obj, _ = post(base + "/chat/completions", {
                "model": model, "messages": msgs, "tools": TOOLS,
                "temperature": 0, "top_k": 1, "seed": 1234,
                "max_tokens": 128, "stream": False,
            }, timeout=a.timeout)
            ch = (obj.get("choices") or [{}])[0]
            txt = ((ch.get("message") or {}).get("content") or "")
            p3 = ("391" in txt) and ch.get("finish_reason") == "stop"
            res["details"]["p3"] = {"finish": ch.get("finish_reason"), "content": txt[:200]}
    except Exception as exc:  # noqa: BLE001
        res["details"]["p3_error"] = repr(exc)
    res["gates"]["P3_roundtrip"] = p3
    ok = ok and p3


    # P4 determinism (batch composition must not flip greedy outputs)
    prompts = ["Reply with exactly: OK", "What is 3+4? Answer with the number only.",
               "Name the capital of France.", "Output the word: alpha",
               "Write one line: print(1+1)", "Return 7.", "Say yes.",
               "List two colors.", "Repeat: done", "Give a single digit."]
    hashes, flips, samples = [], 0, []
    for p in prompts:
        seen = []
        for _ in range(a.repeats):
            txt, _, _ = text_completion(base, model, p, 64)
            seen.append(hashlib.md5(txt.encode("utf-8")).hexdigest())
            samples.append({"prompt": p, "len": len(txt), "head": txt[:80]})
        if len(set(seen)) > 1:
            flips += 1
        hashes.append(seen)
    p4 = flips == 0
    res["gates"]["P4_determinism"] = p4
    res["details"]["p4"] = {"prompts": len(prompts), "repeats": a.repeats,
                            "flipped_prompts": flips, "hashes": hashes,
                            "samples": samples[:10]}

    # P5 thinking leak: a trivial prompt must answer briefly
    try:
        txt, finish, _ = text_completion(base, model, "Reply with exactly one word: OK", 64)
        p5 = len(txt.strip()) <= 40
        res["details"]["p5"] = {"len": len(txt), "content": txt[:160], "finish": finish}
    except Exception as exc:  # noqa: BLE001
        p5 = False
        res["details"]["p5_error"] = repr(exc)
    res["gates"]["P5_no_thinking_leak"] = p5
    ok = ok and p5

    res["all_pass"] = ok
    _write(a, res, ok)
    return 0 if ok else 1


def _write(a, res, ok):
    res["generated_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    res["verdict"] = "PASS" if ok else "FAIL"
    if a.out:
        with open(a.out, "w", encoding="utf-8") as fh:
            json.dump(res, fh, ensure_ascii=False, indent=2)
    print(json.dumps({"verdict": res["verdict"], "gates": res["gates"],
                      "details": {k: v for k, v in res["details"].items()
                                  if k in ("p1", "p2", "p4", "p5")}},
                     ensure_ascii=False))


if __name__ == "__main__":
    sys.exit(main())

