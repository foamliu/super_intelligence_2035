#!/usr/bin/env python3
"""7-way infra/ability/pending classification for SWE-bench Verified.

Generalises c2_cline_R2233.py to all 7 routes.  For every NON-resolved case we
classify into:
  - infra_failed  : empty (or real) patch with infra signals (429/quota/rate-limit,
                    timeout, upstream 5xx, auth 401/403/forbidden/adapter, or the
                    progress quota_blocked/timeout flags).  => RERUN.
  - ability_failed: real patch produced, apply+test FAILED (in eval ``failed`` set).
                    => DO NOT rerun (capability).
  - pending       : empty patch without clear infra signals (rc=0 clean exit, or
                    non-infra error).  => needs transcript; cheap rerun OK.
  - pending_eval  : real patch produced but not yet evaluated (not in resolved /
                    failed / empty).  => needs eval, NOT re-predict.

Redline (unchanged): 429/5xx/timeout/auth = infra (NOT capability).
                      real-patch-tests-fail = capability.
"""
import json, glob, os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(BASE, "predictions_glm53")
REP = os.path.join(BASE, "reports")
OUT_JSON = os.path.join(BASE, "infra_rerun_classify_7way.json")

ROUTES = [
    "cline-patched", "codex", "opencode", "claude-code",
    "pi", "hermes", "deepseek-harness",
]

INFRA_KW_QUOTA = ["429", "额度", "quota", "rate limit", "rate-limit",
                  "too many requests", "too many", "token额度", "ratelimit"]
INFRA_KW_5XX = ["500", "502", "503", "504", "internal server", "bad gateway",
                "service unavail", "service unavailable", "gateway timeout"]
INFRA_KW_AUTH = ["forbidden", "403", "401", "unauthorized", "api_key",
                 "api key", "apikey", "invalid key", "permission denied"]
INFRA_KW_TIMEOUT = ["timeout", "timed out", "time out", "deadline",
                    "deadlineexceeded", "deadline exceeded"]
WALL_TIMEOUT_THRESH = 1799


def has_any(text_lower, kws):
    return any(k in text_lower for k in kws)


def classify_instance(iid, r, is_empty, in_failed, in_infra_eval):
    """Return (bucket, sub_reason)."""
    st = (r.get("stdout_tail") or "")
    se = (r.get("stderr_tail") or "")
    comb = st + "\n" + se
    cl = comb.lower()
    wall = r.get("wall_s", 0) or 0
    rc = r.get("returncode")
    qb = bool(r.get("quota_blocked"))
    to = bool(r.get("timeout"))
    pcls = r.get("classification", "")

    if not is_empty:
        if in_infra_eval:
            return "infra_failed", "real patch flagged infra_or_quota by eval"
        if in_failed:
            return "ability_failed", "real patch produced, eval tests FAILED (capability)"
        return "pending_eval", "real patch produced, not yet evaluated"

    if qb or pcls == "quota-blocked" or has_any(cl, INFRA_KW_QUOTA):
        return "infra_failed", "额度429/quota/rate-limit"
    if to or pcls == "timeout" or has_any(cl, INFRA_KW_TIMEOUT) or wall >= WALL_TIMEOUT_THRESH:
        return "infra_failed", "超时 (timeout flag/keyword/wall>=%ds)" % WALL_TIMEOUT_THRESH
    if has_any(cl, INFRA_KW_5XX):
        return "infra_failed", "上游5xx"
    if has_any(cl, INFRA_KW_AUTH):
        return "infra_failed", "鉴权401/403/forbidden/adapter"

    if rc == 0 and not comb.strip():
        return "pending", "空patch rc=0 无输出 (需transcript)"
    if rc == 0 and comb.strip():
        return "pending", "空patch rc=0 有脚手架输出无diff (需transcript)"
    return "pending", "空patch rc=%s 有非infra信号 (需transcript)" % rc


def load_predictions(route):
    out = {}
    for f in glob.glob(os.path.join(PRED, "%s__*.json" % route)):
        try:
            d = json.load(open(f))
        except Exception:
            continue
        item = d[0] if isinstance(d, list) else d
        if isinstance(item, dict) and "instance_id" in item:
            out[item["instance_id"]] = item.get("model_patch", "") or ""
    return out


def main():
    all_routes = {}
    grand = Counter()
    for route in ROUTES:
        ev = json.load(open(os.path.join(REP, "eval_glm53_%s.json" % route)))
        pr = json.load(open(os.path.join(REP, "progress_glm53_%s.json" % route)))
        res = pr.get("results", pr) if isinstance(pr, dict) else pr
        pm = {r["instance_id"]: r for r in res if "instance_id" in r}
        preds = load_predictions(route)
        resolved = set(ev.get("resolved", []))
        failed = set(ev.get("failed", []))
        infra_eval = set(ev.get("infra_or_quota", []))
        empty_eval = set(ev.get("empty_patch", []))
        buckets = defaultdict(list)
        for iid, r in pm.items():
            if iid in resolved:
                continue
            patch = preds.get(iid, "")
            is_empty = (not patch.strip()) and ((r.get("model_patch_len", 0) or 0) == 0)
            if patch.strip():
                is_empty = False
            bucket, reason = classify_instance(iid, r, is_empty, iid in failed, iid in infra_eval)
            buckets[bucket].append({
                "instance_id": iid, "wall_s": r.get("wall_s", 0) or 0,
                "returncode": r.get("returncode"), "classification": r.get("classification"),
                "quota_blocked": r.get("quota_blocked"), "timeout": r.get("timeout"),
                "model_patch_len": r.get("model_patch_len", 0) or 0, "reason": reason,
                "stdout_tail": (r.get("stdout_tail") or "")[-400:],
                "stderr_tail": (r.get("stderr_tail") or "")[-400:],
            })
            grand[bucket] += 1
        for b in buckets:
            buckets[b].sort(key=lambda x: x["wall_s"], reverse=True)
        all_routes[route] = {
            "eval_n": ev.get("n", 0), "resolved": len(resolved),
            "failed_total": len(failed), "empty_patch_eval": len(empty_eval),
            "infra_or_quota_eval": len(infra_eval),
            "total_predictions": ev.get("total_predictions", len(pm)),
            "counts": {b: len(v) for b, v in buckets.items()}, "buckets": dict(buckets),
        }
    out = {
        "report": "7-way infra/ability/pending classification (2026-11-23 order)",
        "generated": "2026-11-23",
        "source": "eval_glm53_*.json + progress_glm53_*.json + predictions_glm53/",
        "routes": all_routes, "grand_totals": dict(grand),
        "redline": "429/5xx/timeout/auth=infra(NOT capability). real-patch-tests-fail=capability. empty+no-infra-signal=pending(needs transcript).",
    }
    json.dump(out, open(OUT_JSON, "w"), ensure_ascii=False, indent=2)
    print("=== 7-way infra/ability/pending classification ===")
    print("%-18s %5s %5s %5s %6s %6s %6s %6s" % (
        "route", "eval", "resv", "infra", "abil", "pend", "peval", "rerun"))
    rerun_order = []
    for route in ROUTES:
        d = all_routes[route]; c = d["counts"]
        infra = c.get("infra_failed", 0); pend = c.get("pending", 0); rerun = infra + pend
        print("%-18s %5d %5d %5d %6d %6d %6d %6d" % (
            route, d["eval_n"], d["resolved"], infra,
            c.get("ability_failed", 0), pend, c.get("pending_eval", 0), rerun))
        rerun_order.append((route, rerun, infra, pend))
    print("\nRerun order (by infra+pending desc):")
    for route, rerun, infra, pend in sorted(rerun_order, key=lambda x: x[1], reverse=True):
        print("  %-18s rerun=%d (infra=%d + pending=%d)" % (route, rerun, infra, pend))
    print("\nWritten:", OUT_JSON)


if __name__ == "__main__":
    main()

