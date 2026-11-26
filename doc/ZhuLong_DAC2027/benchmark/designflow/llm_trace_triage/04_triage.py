#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""04_triage.py — 用 llama-server(Q8_0) 对 trace 做语义预筛。

用法:
  python3 04_triage.py --input triage_input.jsonl --out labels.jsonl \
      [--base-url http://127.0.0.1:18081] [--parallel 2] [--limit N] [--resume]

输入行: {sid, host, user, session_file, mc, keywords, tools, text, needs_fetch}
输出行: 原行 + {label:{...}, ok, latency, error}
"""
import argparse
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

DOMAINS = [
    "digital", "analog", "layout_virtuoso", "layout_aether", "pg_layout",
    "verification", "spice_sim", "pnr_signoff", "schematic_netlist",
    "physical_verify", "characterization", "eda_other", "none",
]

SCHEMA = {
    "type": "object",
    "properties": {
        "is_eda_workflow": {"type": "boolean"},
        "domain": {"type": "string", "enum": DOMAINS},
        "task_type": {"type": "string"},
        "tools": {"type": "array", "items": {"type": "string"}},
        "stage": {"type": "string", "enum": ["setup", "run", "debug", "signoff", "analysis", "unknown"]},
        "evidence": {"type": "array", "items": {"type": "string"}},
        "confidence": {"type": "number"},
    },
    "required": ["is_eda_workflow", "domain", "task_type", "tools", "stage", "evidence", "confidence"],
}

PROMPT_HEAD = """You are triaging real terminal sessions from a semiconductor company.
Decide if the session is a GENUINE EDA (chip design) workflow trace:
running EDA/CAD tools, writing or debugging flow scripts, fixing tool errors,
analyzing waveforms/netlists/layout, or preparing signoff data.
It is NOT an EDA workflow if it is general software work, IT ops, browsing,
documentation-only, or merely mentions a tool name without using it.

Return JSON only, with keys:
is_eda_workflow (bool), domain (one of %s), task_type (<=12 words),
tools (array), stage (setup|run|debug|signoff|analysis|unknown),
evidence (2-4 verbatim short phrases from the text), confidence (0-1).

Example A (positive):
INPUT: [cmd] cmd: innovus -files flow.tcl ; [user] fix setup hold violation on block top
OUTPUT: {"is_eda_workflow":true,"domain":"pnr_signoff","task_type":"fix setup/hold violations in place-and-route","tools":["innovus"],"stage":"debug","evidence":["innovus -files flow.tcl","setup hold violation"],"confidence":0.9}

Example B (negative):
INPUT: [cmd] file: ~/notes/weekly_report.xlsx ; [user] update the team vacation calendar
OUTPUT: {"is_eda_workflow":false,"domain":"none","task_type":"office administration","tools":[],"stage":"unknown","evidence":["weekly_report.xlsx","vacation calendar"],"confidence":0.95}

INPUT:
""" % (",".join(DOMAINS))


class Client:
    def __init__(self, base_url, timeout=300):
        self.base = base_url.rstrip("/")
        self.timeout = timeout
        self.local = threading.local()

    def session(self):
        s = getattr(self.local, "s", None)
        if s is None:
            s = requests.Session()
            self.local.s = s
        return s

    def post(self, path, payload, retries=2):
        url = self.base + path
        last = None
        for i in range(retries):
            try:
                r = self.session().post(url, json=payload, timeout=self.timeout)
                if r.status_code >= 400:
                    raise RuntimeError(f"HTTP {r.status_code}: {r.text[:300]}")
                return r.json()
            except Exception as e:  # noqa: BLE001
                last = e
                if i == retries - 1:
                    break
                time.sleep(1.5)
        raise RuntimeError(str(last))

    def complete(self, prompt, slot, max_tokens=200, use_schema=True):
        payload = {
            "prompt": prompt,
            "n_predict": max_tokens,
            "temperature": 0.0,
            "top_k": 1,
            "top_p": 1.0,
            "min_p": 0.0,
            "cache_prompt": True,
            "id_slot": int(slot),
            "stream": False,
            "stop": ["\n\n\n"],
        }
        if use_schema:
            payload["json_schema"] = json.dumps(SCHEMA, ensure_ascii=False)
        try:
            return self.post("/completion", payload)
        except RuntimeError as e:
            if use_schema and "HTTP 400" in str(e):
                payload.pop("json_schema", None)
                return self.post("/completion", payload)
            raise

def build_prompt(row):
    meta = (
        f"metadata: mc={row.get('mc')} keywords={str(row.get('keywords',''))[:120]} "
        f"tools_hint={str(row.get('tools',''))[:120]}\n"
    )
    return PROMPT_HEAD + meta + str(row.get("text", ""))[:6000] + "\nOUTPUT:"


def parse_json(s):
    s = (s or "").strip()
    s = re.sub(r"^```(?:json)?|```$", "", s, flags=re.M).strip()
    i, j = s.find("{"), s.rfind("}")
    if i < 0 or j <= i:
        raise ValueError("no json object")
    return json.loads(s[i:j + 1])


def normalize(obj):
    out = {}
    out["is_eda_workflow"] = bool(obj.get("is_eda_workflow"))
    d = str(obj.get("domain") or "none")
    out["domain"] = d if d in DOMAINS else "eda_other"
    out["task_type"] = str(obj.get("task_type") or "")[:120]
    tools = obj.get("tools") or []
    out["tools"] = [str(t)[:40] for t in tools if isinstance(t, (str, int, float))][:8]
    st = str(obj.get("stage") or "unknown")
    out["stage"] = st if st in ("setup", "run", "debug", "signoff", "analysis", "unknown") else "unknown"
    ev = obj.get("evidence") or []
    out["evidence"] = [str(e)[:160] for e in ev if isinstance(e, (str, int, float))][:5]
    try:
        c = float(obj.get("confidence"))
    except (TypeError, ValueError):
        c = 0.0
    out["confidence"] = max(0.0, min(1.0, c))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--base-url", default="http://127.0.0.1:18081")
    ap.add_argument("--parallel", type=int, default=2)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--max-tokens", type=int, default=200)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(args.input, encoding="utf-8") if l.strip()]
    if args.limit:
        rows = rows[: args.limit]
    done = set()
    if args.resume and os.path.isfile(args.out):
        for l in open(args.out, encoding="utf-8"):
            try:
                d = json.loads(l)
                if d.get("ok"):
                    done.add(d["sid"])
            except Exception:
                pass
        rows = [r for r in rows if r["sid"] not in done]
    print(f"[triage] todo={len(rows)} done={len(done)} parallel={args.parallel}")

    cli = Client(args.base_url)
    lock = threading.Lock()
    fout = open(args.out, "a", encoding="utf-8")

    def work(idx_row):
        idx, row = idx_row
        if row.get("needs_fetch") or not row.get("text"):
            return {**row, "ok": False, "error": "needs_fetch"}
        t0 = time.time()
        try:
            resp = cli.complete(build_prompt(row), slot=idx % args.parallel, max_tokens=args.max_tokens)
            label = normalize(parse_json(resp.get("content") or ""))
            return {**row, "label": label, "ok": True, "latency": round(time.time() - t0, 2)}
        except Exception as e:  # noqa: BLE001
            return {**row, "ok": False, "error": str(e)[:300], "latency": round(time.time() - t0, 2)}

    ok = err = 0
    with ThreadPoolExecutor(max_workers=max(1, args.parallel)) as ex:
        futs = {ex.submit(work, (i, r)): r["sid"] for i, r in enumerate(rows)}
        for k, fut in enumerate(as_completed(futs), 1):
            d = fut.result()
            with lock:
                fout.write(json.dumps(d, ensure_ascii=False) + "\n")
                fout.flush()
            ok += 1 if d.get("ok") else 0
            err += 0 if d.get("ok") else 1
            if k % 10 == 0 or k == len(futs):
                print(f"[triage] {k}/{len(futs)} ok={ok} err={err}", flush=True)
    fout.close()
    print(f"[triage] DONE ok={ok} err={err} -> {args.out}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())

