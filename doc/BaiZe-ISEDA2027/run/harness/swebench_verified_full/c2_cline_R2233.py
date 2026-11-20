#!/usr/bin/env python3
"""C2 failure classification for cline (10:10 order) - R2233 manual wake.
7 categories: 适配器/网关额度429/上游5xx/能力/超时/格式不可解析/环境依赖.
Redline: 429/5xx/timeout/adapter=infra(NOT capability); real-patch-tests-fail=capability.
"""
import json, glob, os
from collections import Counter, defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
PRED = os.path.join(BASE, "predictions_glm53")
EVAL = os.path.join(BASE, "reports", "eval_glm53_cline-patched.json")
PROG = os.path.join(BASE, "reports", "progress_glm53_cline-patched.json")
OUT = os.path.join(BASE, "cline_c2_classification_R2233.json")

ev = json.load(open(EVAL))
resolved = set(ev.get("resolved", [])); failed = set(ev.get("failed", []))
infra = set(ev.get("infra_or_quota", []))
prog = json.load(open(PROG))
pm = {r["instance_id"]: r for r in prog.get("results", prog) if "instance_id" in r}

files = sorted(glob.glob(os.path.join(PRED, "cline-patched__*.json")))
attempted = []; real_set = set(); empty_set = set()
for f in files:
    d = json.load(open(f)); item = d[0] if isinstance(d, list) else d
    iid = item["instance_id"]; attempted.append(iid)
    if (item.get("model_patch", "") or "").strip(): real_set.add(iid)
    else: empty_set.add(iid)

def classify_empty(iid):
    r = pm.get(iid, {}); comb = r.get("stdout_tail", "") + r.get("stderr_tail", "")
    cl = comb.lower(); wall = r.get("wall_s", 0) or 0
    if r.get("quota_blocked") or "429" in cl or "额度" in comb or "quota" in cl or "rate limit" in cl or "too many" in cl:
        return "网关额度429"
    if any(k in cl for k in ["500","502","503","504","internal server","bad gateway","service unavail"]):
        return "上游5xx"
    if any(k in cl for k in ["forbidden","403","401","unauthorized","api_key","api key"]):
        return "适配器"
    if r.get("timeout") or "timeout" in cl or "timed out" in cl or "deadline" in cl or wall >= 1799:
        return "超时"
    if any(k in cl for k in ["parse","unparse","no diff","invalid diff","could not extract","no edit"]):
        return "格式不可解析"
    if any(k in cl for k in ["modulenotfound","importerror","no module","command not found","pip install","dependency"]):
        return "环境依赖"
    return "能力"

cats = Counter(); samples = defaultdict(list); detail = []
for iid in attempted:
    if iid in resolved: continue
    r = pm.get(iid, {}); wall = r.get("wall_s", 0) or 0
    st = r.get("stdout_tail", ""); se = r.get("stderr_tail", "")
    if iid in failed:
        cat = "能力"; reason = "real patch produced, eval tests FAILED (capability)"
    elif iid in empty_set:
        cat = classify_empty(iid); reason = "empty patch -> " + cat
    elif iid in infra:
        cat = "网关额度429"; reason = "eval infra_or_quota flag"
    else:
        # real patch, not resolved, not failed, not empty = pending eval (NOT a failure yet)
        detail.append({"instance_id": iid, "category": "pending_eval", "wall_s": wall, "reason": "real patch pending eval"})
        continue
    cats[cat] += 1
    samples[cat].append({"instance_id": iid, "wall_s": wall, "returncode": r.get("returncode"),
                         "stdout_tail": st[-500:], "stderr_tail": se[-500:], "reason": reason})
    detail.append({"instance_id": iid, "category": cat, "wall_s": wall, "reason": reason})

total = sum(cats.values())
top3 = {c: sorted(lst, key=lambda x: x["wall_s"], reverse=True)[:3] for c, lst in samples.items()}
out = {
    "report": "cline C2 failure classification (10:10)", "round": "R2233-manual",
    "generated": "2026-11-12", "source_eval": EVAL, "source_progress": PROG,
    "totals": {"attempted": len(attempted), "real_patches": len(real_set),
               "empty_patches": len(empty_set), "evaluated": ev.get("n", 0),
               "resolved": len(resolved), "failed_real_patch": len(failed),
               "infra_or_quota_eval": len(infra), "total_failures": total},
    "category_counts": dict(cats.most_common()),
    "category_pct": {c: round(n/total*100, 1) for c, n in cats.most_common()},
    "top3_samples": top3,
    "redline_note": "429/5xx/timeout/adapter=infra(NOT capability). real-patch-tests-fail=capability. empty+额度=网关429 infra.",
}
json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=2)
print("Written:", OUT)
print("Total failures:", total, "sum=", sum(cats.values()))
for c, n in cats.most_common():
    print("  %-12s %3d  (%.1f%%)" % (c, n, n/total*100))
print("\nAmbiguous 能力 samples:")
for s in top3.get("能力", [])[:3]:
    print("  ", s["instance_id"], "wall=", s["wall_s"], "rc=", s["returncode"])
    print("   stdout[-160]:", repr(s["stdout_tail"][-160:]))
    print("   stderr[-200]:", repr(s["stderr_tail"][-200:]))
