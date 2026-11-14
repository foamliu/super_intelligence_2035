#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""bpt_attribution_p0_dev_compare.py - P0 补丁 dev 前后对比 + McNemar 配对检验。
输入两个 final_report.json（baseline_dev / p0_dev，rescue 后落盘），对指定 task
子集（默认 dev 79 题）逐题取 pass/fail，算 Pass@1 / delta_pp / McNemar 精确检验 /
submit 报错率(best-effort) / 预注册判据(POSTTRAIN_PLAN_NEXT.md §1②)。
也可用于 ablation 40 子集（--task-ids-key sampled_task_ids）。
"""
import argparse, json, math, os, re, sys

REJECTION_MARKERS = [
    "missing-required-field", "missing_required_field",
    "string-not-array", "string_not_array",
    "wrong-type-boolean", "wrong_type_boolean",
    "other-type-error", "other_type_error",
    "unavailable-tool", "unavailable_tool",
]


def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_task_ids(path, key):
    d = load_json(path)
    if key in d:
        return d[key]
    if "sampled_task_ids" in d:
        return d["sampled_task_ids"]
    raise SystemExit("[ERR] task-ids key '%s' not found in %s (keys=%s)" % (key, path, list(d.keys())))


def per_task_pass(details, task_ids):
    out = {}
    for tid in task_ids:
        rec = details.get(tid)
        if rec is None:
            out[tid] = False
            continue
        nc = rec.get("num_correct", 0) or 0
        out[tid] = (nc >= 1)
    return out


def pass_rate(pass_map):
    n = len(pass_map)
    if n == 0:
        return 0.0, 0, 0
    c = sum(1 for v in pass_map.values() if v)
    return c / n, c, n


def mcnemar_exact(baseline_pass, patch_pass):
    n00 = n01 = n10 = n11 = 0
    for tid in baseline_pass:
        b_pass = baseline_pass[tid]
        p_pass = patch_pass.get(tid, False)
        if b_pass and p_pass:
            n11 += 1
        elif (not b_pass) and (not p_pass):
            n00 += 1
        elif (not b_pass) and p_pass:
            n01 += 1
        else:
            n10 += 1
    b, c = n01, n10
    n = b + c
    if n == 0:
        p_value = 1.0
    else:
        def binom_cdf(k, nn, p=0.5):
            return sum(math.comb(nn, i) * (p ** i) * ((1 - p) ** (nn - i)) for i in range(0, k + 1))
        cdf_b = binom_cdf(b, n)
        sf_b = 1.0 - binom_cdf(b - 1, n) if b > 0 else 1.0
        p_value = min(1.0, 2.0 * min(cdf_b, sf_b))
    return {"n11_both_pass": n11, "n00_both_fail": n00, "n01_b_fix": b, "n10_c_break": c,
            "discordant": n, "p_value_two_sided": p_value}


def count_rejections(log_path):
    if not log_path or not os.path.exists(log_path):
        return None, {}
    try:
        with open(log_path, "rb") as f:
            raw = f.read().decode("utf-8", "replace")
    except Exception:
        return None, {}
    by_reason = {}
    total = 0
    for m in REJECTION_MARKERS:
        cnt = len(re.findall(re.escape(m), raw))
        if cnt:
            by_reason[m] = cnt
            total += cnt
    return total, by_reason


def gen_stats(rep):
    s = rep.get("summary", {}).get("generation_statistics", {}) or {}
    return {"success": s.get("success"), "fail": s.get("fail"),
            "failure": s.get("failure"), "timeout": s.get("timeout"),
            "gen_success_rate": rep.get("summary", {}).get("generation_success_rate")}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--baseline-report", required=True)
    ap.add_argument("--patch-report", required=True)
    ap.add_argument("--task-ids-file", default="attribution_traindev_split.json")
    ap.add_argument("--task-ids-key", default="dev_ids")
    ap.add_argument("--baseline-label", default="baseline_dev")
    ap.add_argument("--patch-label", default="p0_dev")
    ap.add_argument("--baseline-log", default=None)
    ap.add_argument("--patch-log", default=None)
    ap.add_argument("--delta-threshold-pp", type=float, default=3.0)
    ap.add_argument("--rej-reduction-threshold-pp", type=float, default=10.0)
    ap.add_argument("--output", default=None)
    args = ap.parse_args()

    task_ids = load_task_ids(args.task_ids_file, args.task_ids_key)
    base = load_json(args.baseline_report)
    patch = load_json(args.patch_report)
    base_pass = per_task_pass(base.get("details_per_task", {}), task_ids)
    patch_pass = per_task_pass(patch.get("details_per_task", {}), task_ids)
    base_pr, base_c, base_n = pass_rate(base_pass)
    patch_pr, patch_c, patch_n = pass_rate(patch_pass)
    delta_pp = (patch_pr - base_pr) * 100.0
    mc = mcnemar_exact(base_pass, patch_pass)

    base_rej_total, base_rej_by = count_rejections(args.baseline_log)
    patch_rej_total, patch_rej_by = count_rejections(args.patch_log)
    rej_reduction_pp = None
    if base_rej_total is not None and patch_rej_total is not None:
        base_attempt = sum(v for v in [gen_stats(base).get("success"), gen_stats(base).get("fail"),
                                       gen_stats(base).get("timeout")] if isinstance(v, (int, float)))
        patch_attempt = sum(v for v in [gen_stats(patch).get("success"), gen_stats(patch).get("fail"),
                                        gen_stats(patch).get("timeout")] if isinstance(v, (int, float)))
        base_rate = (base_rej_total / base_attempt * 100.0) if base_attempt else None
        patch_rate = (patch_rej_total / patch_attempt * 100.0) if patch_attempt else None
        if base_rate is not None and patch_rate is not None:
            rej_reduction_pp = base_rate - patch_rate

    delta_ok = delta_pp >= args.delta_threshold_pp
    rej_ok = (rej_reduction_pp is not None and rej_reduction_pp >= args.rej_reduction_threshold_pp)
    if rej_reduction_pp is None:
        criterion = "INCONCLUSIVE_NO_REJ_DATA"
        passed = delta_ok
    else:
        criterion = "PASS" if (delta_ok and rej_ok) else "FAIL_THRESHOLD"
        passed = delta_ok and rej_ok

    result = {
        "baseline_label": args.baseline_label, "patch_label": args.patch_label,
        "task_ids_file": args.task_ids_file, "task_ids_key": args.task_ids_key, "n_tasks": len(task_ids),
        "baseline": {"pass_rate": base_pr, "correct": base_c, "attempted": base_n,
                     "gen_stats": gen_stats(base), "model_name": base.get("model_name"),
                     "rejections_total": base_rej_total, "rejections_by_reason": base_rej_by},
        "patch": {"pass_rate": patch_pr, "correct": patch_c, "attempted": patch_n,
                  "gen_stats": gen_stats(patch), "model_name": patch.get("model_name"),
                  "rejections_total": patch_rej_total, "rejections_by_reason": patch_rej_by},
        "delta_pp": round(delta_pp, 4), "mcnemar": mc,
        "submit_error_rate_reduction_pp": (round(rej_reduction_pp, 4) if rej_reduction_pp is not None else None),
        "preregistered_criterion": {
            "delta_threshold_pp": args.delta_threshold_pp,
            "rej_reduction_threshold_pp": args.rej_reduction_threshold_pp,
            "delta_ok": delta_ok, "rej_ok": rej_ok, "verdict": criterion, "passed": passed,
            "note": "预注册判据(POSTTRAIN_PLAN_NEXT.md §1②): delta_pp>=+3 且 submit 报错率降幅>=10pp => PASS 进累积组合; 否则不达门槛, 记负结果, 不事后调门槛。"},
        "caveat": "数字来自 path-bug rescue 后复算(cline 写错路径无法自验, 可能扰动多轮行为) => 下界/可能混淆, 需 path-fix 干净重跑去混淆。model_name=zhulong_deepseek_v32 为 config 陈旧标签, 实际模型=minicpm5-2b-sft-v39-final(经反向隧道 18096 curl 核实)。"
    }
    out = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
        print("[OK] written -> %s" % args.output)
    print("=" * 70)
    print("P0 dev 前后对比 · %s vs %s (n=%d)" % (args.baseline_label, args.patch_label, len(task_ids)))
    print("-" * 70)
    print("baseline Pass@1 = %d/%d = %.4f  (gen: %s)" % (base_c, base_n, base_pr, gen_stats(base)))
    print("patch    Pass@1 = %d/%d = %.4f  (gen: %s)" % (patch_c, patch_n, patch_pr, gen_stats(patch)))
    print("delta_pp = %+.4f  (阈值 >= +%.1f => %s)" % (delta_pp, args.delta_threshold_pp, "OK" if delta_ok else "NO"))
    print("McNemar: n01(b fix)=%d  n10(c break)=%d  discordant=%d  p=%.4f" % (mc["n01_b_fix"], mc["n10_c_break"], mc["discordant"], mc["p_value_two_sided"]))
    if rej_reduction_pp is None:
        print("submit 报错率降幅 = N/A (无 codegen.log 或无拒绝标记) => %s" % criterion)
    else:
        print("submit 报错率降幅 = %.4f pp (阈值 >= %.1f => %s)" % (rej_reduction_pp, args.rej_reduction_threshold_pp, "OK" if rej_ok else "NO"))
    print("预注册判定 = %s  (passed=%s)" % (criterion, passed))
    print("=" * 70)
    if not args.output:
        print(out)


if __name__ == "__main__":
    main()
