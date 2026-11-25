#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""05_compare_with_hf.py — 同一 ckpt 的 GGUF 结果 vs HF 结果，判定是否可切换。

用法:
  python3 05_compare_with_hf.py <iter> \
      [--results-base /nas_train/.../lm_eval_results] \
      [--hf-s-per-req 16.44] [--tol-pp 1.0] [--min-speedup 5.0]

判定（全部满足才算 PASS）:
  1. 每个任务 |Δacc| <= tol_pp；
  2. 8 集 Avg |Δacc| <= tol_pp；
  3. 速度 >= min_speedup（HF 请求数 x hf_s_per_req / GGUF 实测总时长）。

HF 侧没有保存逐次耗时，这里用换算式估计：
  HF 请求数 = Σ_task (样本数 x 选项数)
  HF 预计耗时 = HF 请求数 x hf_s_per_req（默认 16.44s，来自 2026-11-02 实测）
"""
import argparse
import json
import os
import sys

TASKS = [
    ("arc_challenge", "ARC-C", 4),
    ("arc_easy", "ARC-E", 4),
    ("boolq", "BoolQ", 2),
    ("hellaswag", "HellaSwag", 4),
    ("openbookqa", "OpenBookQA", 4),
    ("piqa", "PIQA", 2),
    ("sciq", "SciQ", 4),
    ("winogrande", "Winogrande", 2),
]

DEFAULT_BASE = "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/lm_eval_results"


def get_acc(task_res):
    for k in ("acc,none", "acc"):
        if k in task_res and task_res[k] is not None:
            return float(task_res[k])
    return None


def get_n(res, task):
    ns = (res.get("n-samples") or {}).get(task) or {}
    for k in ("effective", "original"):
        v = ns.get(k)
        if isinstance(v, (int, float)):
            return int(v)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("iter", type=int)
    ap.add_argument("--results-base", default=DEFAULT_BASE)
    ap.add_argument("--hf-s-per-req", type=float, default=16.44)
    ap.add_argument("--tol-pp", type=float, default=1.0, help="允许的最大绝对偏差（百分点）")
    ap.add_argument("--min-speedup", type=float, default=5.0)
    ap.add_argument("--out", default="", help="comparison.json 输出路径（默认 GGUF 目录下）")
    args = ap.parse_args()

    hf_path = os.path.join(args.results_base, f"hf_iter_{args.iter}", "results.json")
    gg_dir = os.path.join(args.results_base, f"gguf_iter_{args.iter}")
    gg_path = os.path.join(gg_dir, "results.json")
    meta_path = os.path.join(gg_dir, "meta.json")

    for p in (hf_path, gg_path):
        if not os.path.isfile(p):
            print(f"FAIL: 缺 {p}", file=sys.stderr)
            return 2

    hf = json.load(open(hf_path, encoding="utf-8"))
    gg = json.load(open(gg_path, encoding="utf-8"))
    meta = json.load(open(meta_path, encoding="utf-8")) if os.path.isfile(meta_path) else {}

    hf_res, gg_res = hf.get("results", {}), gg.get("results", {})
    hf_limit = (hf.get("config") or {}).get("limit")
    gg_limit = (gg.get("config") or {}).get("limit")
    if hf_limit != gg_limit:
        print(f"WARN: limit 不一致 hf={hf_limit} gguf={gg_limit}，对比仅作参考", file=sys.stderr)

    print("=" * 78)
    print(f"iter_{args.iter}: GGUF vs HF（acc，单位 %）  hf_limit={hf_limit} gguf_limit={gg_limit}")
    print("=" * 78)
    print(f"{'task':<12}{'HF':>8}{'GGUF':>8}{'delta_pp':>10}{'n_hf':>8}{'n_gg':>8}  verdict")
    print("-" * 78)

    rows, bad, max_abs = [], 0, 0.0
    hf_vals, gg_vals = [], []
    for key, name, choices in TASKS:
        hfv = get_acc(hf_res.get(key, {})) if key in hf_res else None
        ggv = get_acc(gg_res.get(key, {})) if key in gg_res else None
        if hfv is None or ggv is None:
            print(f"{name:<12}{'--':>8}{'--':>8}{'--':>10}  (缺结果，跳过)")
            continue
        delta = (ggv - hfv) * 100.0
        n_hf, n_gg = get_n(hf, key), get_n(gg, key)
        ok = abs(delta) <= args.tol_pp
        bad += 0 if ok else 1
        max_abs = max(max_abs, abs(delta))
        hf_vals.append(hfv)
        gg_vals.append(ggv)
        rows.append(
            {"task": key, "hf": hfv, "gguf": ggv, "delta_pp": round(delta, 2),
             "n_hf": n_hf, "n_gg": n_gg, "ok": ok, "choices": choices}
        )
        print(f"{name:<12}{hfv*100:>8.2f}{ggv*100:>8.2f}{delta:>+10.2f}"
              f"{(n_hf if n_hf is not None else '-'):>8}{(n_gg if n_gg is not None else '-'):>8}"
              f"  {'OK' if ok else 'FAIL'}")

    if not rows:
        print("FAIL: 没有任何可对比的任务", file=sys.stderr)
        return 2

    hf_avg = sum(hf_vals) / len(hf_vals)
    gg_avg = sum(gg_vals) / len(gg_vals)
    avg_delta = (gg_avg - hf_avg) * 100.0
    print("-" * 78)
    print(f"{'Avg':<12}{hf_avg*100:>8.2f}{gg_avg*100:>8.2f}{avg_delta:>+10.2f}")

    # 速度：HF 预计 = Σ(样本数 x 选项数) x s/req
    hf_reqs = 0
    for r in rows:
        n = r["n_hf"] or 100
        hf_reqs += int(n) * int(r["choices"])
    hf_time = hf_reqs * args.hf_s_per_req
    gg_time = float(meta.get("elapsed_sec") or 0.0)
    speedup = (hf_time / gg_time) if gg_time > 0 else 0.0

    print("-" * 78)
    print(f"HF 请求数(估)={hf_reqs}  HF 预计={hf_time/3600:.2f}h  "
          f"GGUF 实测={gg_time/3600:.2f}h  加速={speedup:.1f}x")
    print(f"GGUF s/token-request={meta.get('sec_per_token_request')}  "
          f"token_requests={meta.get('n_token_requests')}")

    avg_ok = abs(avg_delta) <= args.tol_pp
    speed_ok = speedup >= args.min_speedup
    verdict = avg_ok and bad == 0 and speed_ok
    print("-" * 78)
    print(f"判据: max|delta_pp|={max_abs:.2f} (<= {args.tol_pp})  "
          f"Avg|delta_pp|={abs(avg_delta):.2f} (<= {args.tol_pp})  "
          f"加速={speedup:.1f}x (>= {args.min_speedup})")
    print(f"VERDICT: {'PASS - 可以切换 GGUF' if verdict else 'FAIL - 不要切换，回退 HF/bf16'}")
    print("=" * 78)

    out = args.out or os.path.join(gg_dir, "comparison.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(
            {
                "iter": args.iter,
                "hf_limit": hf_limit,
                "gguf_limit": gg_limit,
                "rows": rows,
                "hf_avg": hf_avg,
                "gguf_avg": gg_avg,
                "avg_delta_pp": round(avg_delta, 3),
                "max_abs_delta_pp": round(max_abs, 3),
                "hf_requests_est": hf_reqs,
                "hf_seconds_est": round(hf_time, 1),
                "gguf_seconds": gg_time,
                "speedup": round(speedup, 2),
                "tol_pp": args.tol_pp,
                "min_speedup": args.min_speedup,
                "verdict": "PASS" if verdict else "FAIL",
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    print(f"[compare] 写入 {out}")
    return 0 if verdict else 1


if __name__ == "__main__":
    sys.exit(main())

