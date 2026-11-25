#!/usr/bin/env python3
"""baize_posttrain_llamacpp_speed_probe_load.py -- stdlib-only load generator and
result assembler for the llama.cpp x Qwen3.5-2B CPU speed probe.

WHY: the A5 arm (Qwen3.5-2B) is blocked on serving throughput. wake744 measured
~40 tok/s AGGREGATE on the self-written HF server and 93.75% of tasks produced
empty code because per-agent rate (~5 tok/s) hit the 2500s task timeout. This
tool answers NOT "what is single-stream decode speed" but "what is the
AGGREGATE rate at 8 concurrent agents" -- the only number that decides
feasibility (see the directive in BAIZE_POSTTRAIN_TASK.md §0).

Two modes:
  load      -- fire C concurrent /v1/chat/completions, sample llama.cpp
               /metrics before/after, report server-side prefill + decode
               tokens/s (authoritative) plus client-side latencies.
  assemble  -- merge env.json + bench.json + load_*.json into one result JSON,
               evaluate the pre-registered gates, print a verdict table.

EVIDENCE CONTRACT (doc/AGENTS.md §1): every number carries its file path and
the command that produced it. This script writes only JSON + logs.
"""
import argparse
import glob
import json
import os
import statistics
import sys
import threading
import time
import urllib.request

FILLER = (
    "Read the following electronic design automation project note and then "
    "produce the requested script. Keep the answer short and deterministic. "
)

# 5-run budget anchors (baseline_A0_base_5run_summary / A0 run1 pertask):
MEAN_OUTPUT_TOKENS_PER_TASK = 12453
TOTAL_TASKS = 158
RUNS = 5
TASK_TIMEOUT_S = 2500
PARALLEL = 8


def _post(url, payload, timeout):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_json(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def _get_text(url, timeout=30):
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def scrape_metrics(port):
    """Return {metric_name: float} from llama.cpp /metrics (prometheus text)."""
    txt = _get_text("http://127.0.0.1:%d/metrics" % port)
    out = {}
    for line in txt.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.rsplit(" ", 1)
        if len(parts) != 2:
            continue
        try:
            out[parts[0]] = float(parts[1])
        except ValueError:
            continue
    return out


def metric_delta(before, after, suffix):
    """Sum every metric whose name ends with `suffix` (llama.cpp has a few)."""
    total = 0.0
    found = []
    for k, v in after.items():
        if k.endswith(suffix):
            total += max(0.0, v - before.get(k, 0.0))
            found.append(k)
    return total, found


def build_prompt(words):
    """Approximate a prompt of `words` words (1 token ~ 0.75 word)."""
    if words <= 0:
        return "Reply with the single word: OK."
    reps = max(1, words // len(FILLER.split()))
    return (FILLER * reps) + "\n\nNow reply with the single word: OK."


def max_repeated_ngram(text, n=8):
    """Cheap repetition-loop detector (the BaiZe SSM-bug failure signature)."""
    toks = text.split()
    if len(toks) < n:
        return 1
    counts = {}
    best = 1
    for i in range(len(toks) - n + 1):
        g = " ".join(toks[i:i + n])
        counts[g] = counts.get(g, 0) + 1
        if counts[g] > best:
            best = counts[g]
    return best

def run_load(args):
    model = "unknown"
    try:
        models = _get_json("http://127.0.0.1:%d/v1/models" % args.port)
        model = models["data"][0]["id"]
    except Exception as exc:  # noqa: BLE001
        print("[load] WARN /v1/models failed: %s" % exc, file=sys.stderr)

    prompt = build_prompt(args.prompt_words)
    results = []
    for rnd in range(args.rounds):
        before = scrape_metrics(args.port)
        lat, comp_tokens, prompt_tokens, reps, errs = [], [], [], [], []
        lock = threading.Lock()

        def worker(idx):
            body = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": args.max_tokens,
                "temperature": 0,
                "top_k": 1,
                "seed": 1234,
                "stream": False,
            }
            t0 = time.time()
            try:
                resp = _post(
                    "http://127.0.0.1:%d/v1/chat/completions" % args.port,
                    body,
                    args.timeout,
                )
                dt = time.time() - t0
                usage = resp.get("usage", {}) or {}
                choice = (resp.get("choices") or [{}])[0]
                txt = (choice.get("message", {}) or {}).get("content", "") or ""
                with lock:
                    lat.append(dt)
                    comp_tokens.append(int(usage.get("completion_tokens", 0)))
                    prompt_tokens.append(int(usage.get("prompt_tokens", 0)))
                    reps.append(max_repeated_ngram(txt))
            except Exception as exc:  # noqa: BLE001
                dt = time.time() - t0
                with lock:
                    errs.append({"worker": idx, "err": repr(exc)[:300], "dt": dt})

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(args.concurrency)]
        wall0 = time.time()
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        wall = time.time() - wall0
        after = scrape_metrics(args.port)

        prefill_tok, prefill_keys = metric_delta(before, after, "prompt_tokens_total")
        decode_tok, decode_keys = metric_delta(before, after, "tokens_predicted_total")

        row = {
            "round": rnd + 1,
            "concurrency": args.concurrency,
            "max_tokens": args.max_tokens,
            "prompt_words": args.prompt_words,
            "wall_s": round(wall, 3),
            "requests_ok": len(lat),
            "errors": errs,
            "server_prompt_tokens": prefill_tok,
            "server_decode_tokens": decode_tok,
            "prefill_tok_s": round(prefill_tok / wall, 2) if wall > 0 else None,
            "decode_tok_s_aggregate": round(decode_tok / wall, 2) if wall > 0 else None,
            "client_completion_tokens_sum": sum(comp_tokens),
            "client_prompt_tokens_sum": sum(prompt_tokens),
            "latency_s": {
                "min": round(min(lat), 3) if lat else None,
                "median": round(statistics.median(lat), 3) if lat else None,
                "max": round(max(lat), 3) if lat else None,
                "mean": round(statistics.mean(lat), 3) if lat else None,
            },
            "per_agent_decode_tok_s": (
                round(decode_tok / wall / max(1, len(lat)), 2) if wall > 0 and lat else None
            ),
            "max_repeated_8gram": max(reps) if reps else None,
            "metric_keys_used": {"prefill": prefill_keys[:3], "decode": decode_keys[:3]},
        }
        if comp_tokens and decode_tok:
            row["counter_vs_usage_ratio"] = round(decode_tok / max(1, sum(comp_tokens)), 3)
        results.append(row)
        print(json.dumps(row, ensure_ascii=False))

    out = {
        "mode": "load",
        "port": args.port,
        "model": model,
        "concurrency": args.concurrency,
        "rounds": results,
    }
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        print("[load] wrote %s" % args.out)
    return 0



def _load(path):
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def _median_decode(load_json):
    vals = [
        r["decode_tok_s_aggregate"]
        for r in load_json.get("rounds", [])
        if r.get("decode_tok_s_aggregate")
    ]
    return statistics.median(vals) if vals else None


def run_assemble(args):
    d = args.dir
    env_path = os.path.join(d, "env.json")
    bench_path = os.path.join(d, "bench.json")
    env = _load(env_path) if os.path.exists(env_path) else {}
    bench = _load(bench_path) if os.path.exists(bench_path) else {}

    loads = {}
    for path in sorted(glob.glob(os.path.join(d, "load_*.json"))):
        name = os.path.basename(path)[len("load_"):-len(".json")]
        loads[name] = _load(path)

    c1 = loads.get("c1")
    c8 = loads.get("c8")
    c8_long = loads.get("c8_long")

    single_stream = None
    best_threads = None
    for row in bench.get("rows", []):
        tg = row.get("tg128_tok_s")
        if tg and (single_stream is None or tg > single_stream):
            single_stream = tg
            best_threads = row.get("threads")

    agg8 = _median_decode(c8) if c8 else None
    agg1 = _median_decode(c1) if c1 else None
    agg8_long = _median_decode(c8_long) if c8_long else None
    batching_gain = round(agg8 / agg1, 2) if agg8 and agg1 else None

    gates = {}
    gates["G0_convert_ok"] = bool(env.get("gguf_f16_exists") or env.get("convert_ok"))
    gates["G1_server_up"] = bool(env.get("server_up"))
    gates["G2_aggregate_8way_tok_s"] = agg8
    if agg8 is None:
        gates["G2_verdict"] = "UNKNOWN"
    elif agg8 >= 100:
        gates["G2_verdict"] = "PASS"
    elif agg8 >= 64:
        gates["G2_verdict"] = "CONDITIONAL"
    else:
        gates["G2_verdict"] = "FAIL"

    max_rep = None
    for lj in (c8, c8_long):
        if not lj:
            continue
        for r in lj.get("rounds", []):
            v = r.get("max_repeated_8gram")
            if v is not None:
                max_rep = v if max_rep is None else max(max_rep, v)
    gates["G4_max_repeated_8gram"] = max_rep
    gates["G4_repetition_ok"] = bool(max_rep is not None and max_rep <= 5)

    projected = None
    if agg8:
        total_tokens = MEAN_OUTPUT_TOKENS_PER_TASK * TOTAL_TASKS * RUNS
        per_agent = agg8 / PARALLEL
        projected = {
            "total_output_tokens_5run": total_tokens,
            "hours_5run": round(total_tokens / agg8 / 3600.0, 1),
            "per_agent_tok_s": round(per_agent, 2),
            "mean_task_decode_s": round(MEAN_OUTPUT_TOKENS_PER_TASK / per_agent, 0),
            "timeout_headroom_ratio": round(
                (MEAN_OUTPUT_TOKENS_PER_TASK / per_agent) / TASK_TIMEOUT_S, 3
            ),
        }

    if not gates["G0_convert_ok"] or not gates["G1_server_up"]:
        verdict = "BLOCKED"
    elif gates["G2_verdict"] == "FAIL":
        verdict = "NOT_FEASIBLE"
    elif gates["G2_verdict"] == "CONDITIONAL":
        verdict = "CONDITIONAL"
    elif not gates["G4_repetition_ok"]:
        verdict = "NOT_FEASIBLE_REPETITION"
    else:
        verdict = "FEASIBLE"

    out = {
        "mode": "assemble",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "env": env,
        "bench": bench,
        "loads": {k: os.path.join(d, "load_%s.json" % k) for k in loads},
        "single_stream_tok_s": single_stream,
        "best_threads": best_threads,
        "aggregate_8way_tok_s": agg8,
        "aggregate_8way_longprompt_tok_s": agg8_long,
        "batching_gain": batching_gain,
        "gates": gates,
        "projection": projected,
        "verdict": verdict,
    }
    out_path = args.out or os.path.join(d, "llamacpp_speed_probe_result.json")
    parent = os.path.dirname(os.path.abspath(out_path))
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)

    print("")
    print("=== llama.cpp x Qwen3.5-2B speed probe ===")
    print("host            : %s  nproc=%s" % (env.get("hostname"), env.get("nproc")))
    print("llama.cpp       : %s @ %s" % (env.get("llama_dir"), env.get("llama_rev")))
    print("quant           : %s" % env.get("quant_file"))
    print("single-stream   : %s tok/s (best -t %s)" % (single_stream, best_threads))
    print("8-way aggregate : %s tok/s (long-prompt %s)" % (agg8, agg8_long))
    print("batching gain   : %sx" % batching_gain)
    print("gates           : %s" % json.dumps(gates, ensure_ascii=False))
    if projected:
        print("projection      : %s" % json.dumps(projected, ensure_ascii=False))
    print("VERDICT         : %s" % verdict)
    print("[assemble] wrote %s" % out_path)
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="mode", required=True)

    lp = sub.add_parser("load")
    lp.add_argument("--port", type=int, default=18097)
    lp.add_argument("--concurrency", type=int, default=8)
    lp.add_argument("--max-tokens", type=int, default=256)
    lp.add_argument("--rounds", type=int, default=3)
    lp.add_argument("--prompt-words", type=int, default=800)
    lp.add_argument("--timeout", type=int, default=900)
    lp.add_argument("--out", default="")

    ap_ = sub.add_parser("assemble")
    ap_.add_argument("--dir", required=True)
    ap_.add_argument("--out", default="")

    args = ap.parse_args()
    if args.mode == "load":
        return run_load(args)
    return run_assemble(args)


if __name__ == "__main__":
    sys.exit(main())

