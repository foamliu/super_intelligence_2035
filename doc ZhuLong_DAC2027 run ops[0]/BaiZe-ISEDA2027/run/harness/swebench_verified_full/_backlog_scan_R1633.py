#!/usr/bin/env python3
"""Genuine backlog scan R1615: find predictions with patch_len>0 NOT yet eval'd.
Eval files: reports/eval_<harness>.json with resolved/failed/infra_or_quota/no_patch lists.
Prediction files: predictions/<harness>__<instance>.json (list of dicts with model_patch).
"""
import json, os, glob

PRED_DIR = "predictions"
EVAL_DIR = "reports"
harnesses = ["cline-patched", "codex", "opencode", "pi", "claude-code",
             "hermes", "deepseek-harness"]

def load_eval(h):
    f = os.path.join(EVAL_DIR, f"eval_{h}.json")
    if not os.path.isfile(f):
        return set()
    try:
        d = json.load(open(f))
    except Exception:
        return set()
    seen = set()
    for k in ("resolved", "failed", "infra_or_quota", "no_patch"):
        seen.update(d.get(k, []))
    return seen

def patch_len_of(f):
    try:
        d = json.load(open(f))
    except Exception:
        return -1
    if isinstance(d, list):
        if not d:
            return 0
        d = d[0]
    if not isinstance(d, dict):
        return -1
    patch = d.get("model_patch") or d.get("patch") or ""
    return len(patch.strip()) if isinstance(patch, str) else 0

print("=== GENUINE BACKLOG (patch_len>0, not in eval file) ===")
total_backlog = 0
for h in harnesses:
    ev = load_eval(h)
    backlog = []
    n_patch = 0
    n_total = 0
    for f in sorted(glob.glob(f"{PRED_DIR}/{h}__*.json")):
        n_total += 1
        inst = os.path.basename(f).replace(f"{h}__", "").replace(".json", "")
        pl = patch_len_of(f)
        if pl > 0:
            n_patch += 1
            if inst not in ev:
                backlog.append((inst, pl))
    total_backlog += len(backlog)
    print(f"  {h}: preds={n_total} patch_preds={n_patch} eval_seen={len(ev)} backlog={len(backlog)}")
    for inst, pl in backlog[:12]:
        print(f"      BACKLOG {inst} plen={pl}")
print(f"\nTOTAL BACKLOG (all harnesses) = {total_backlog}")
