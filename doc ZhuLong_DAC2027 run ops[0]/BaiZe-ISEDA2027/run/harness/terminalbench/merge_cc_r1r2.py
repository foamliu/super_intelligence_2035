#!/usr/bin/env python3
"""Merge claude-code TB-2.1 R1 (rerun 20261114-15) + R2 (round2 20261117) results.

For each of the 89 TB-2.1 tasks:
  - If R1 PASS -> PASS (no need to check R2)
  - If R1 FAIL/NA and task in R2 manifest:
      - If R2 PASS -> PASS
      - If R2 ability-FAIL (reward=0, model ran) -> ability-FAIL
      - If R2 INFRA (502/503/ConnRefused, model never ran, iters=0) -> INFRA
      - If R2 timeout -> NA/timeout
      - If R2 still running -> RUNNING (not counted)
  - If R1 FAIL/NA and NOT in R2 -> keep R1 attribution
"""
import json, os, sys

R1_DIRS = [
    "/tmp/tb21_glm53_jobs/claude-code_rerun_20261114_0951",
    "/tmp/tb21_glm53_jobs/claude-code_rerun_20261114_1251",
    "/tmp/tb21_glm53_jobs/claude-code_rerun_20261115_0348",
]
R2_DIR = "/tmp/tb21_glm53_jobs/claude-code_rerun_20261117_0003"
R2_MANIFEST = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench/manifests/tb21_cc_round2_rerun_20261116.txt"
TB21_TASKS_FILE = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench/manifests/tb21_cline_quota_rerun_ids_20261116_0144.txt"
OUT_PATH = "/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/terminalbench/manifests/cc_r1r2_merged.json"


def load_task_list(path):
    if not os.path.isfile(path):
        return []
    return [l.strip() for l in open(path) if l.strip()]


def scan_results(base_dirs):
    """Scan result.json, prefer PASS (best result) across multiple dirs."""
    results = {}
    for base in base_dirs:
        if not os.path.isdir(base):
            continue
        for root, dirs, files in os.walk(base):
            if "result.json" not in files:
                continue
            bn = os.path.basename(root)
            if "__" not in bn:
                continue
            tname = bn.split("__")[0]
            if tname.startswith("2026-"):
                continue
            rj = os.path.join(root, "result.json")
            try:
                r = json.load(open(rj))
            except Exception:
                continue
            # Prefer PASS: if existing result is PASS, keep it
            if tname in results:
                vr_old = results[tname].get("verifier_result") or {}
                rw_old = vr_old.get("rewards") or {} if isinstance(vr_old, dict) else {}
                old_reward = rw_old.get("reward") if isinstance(rw_old, dict) else None
                if old_reward in (1.0, 1):
                    continue  # keep existing PASS
            results[tname] = r
    return results


def classify(r):
    """Classify result.json into PASS/FAIL/INFRA/NA/RUNNING."""
    if r is None:
        return ("RUNNING", "no result.json yet")
    vr = r.get("verifier_result") or {}
    rewards = vr.get("rewards") or {} if isinstance(vr, dict) else {}
    reward = rewards.get("reward") if isinstance(rewards, dict) else None
    ei = r.get("exception_info") or {}
    exc_msg = str(ei.get("exception_message", "") if isinstance(ei, dict) else "")
    ar = r.get("agent_result") or {}
    metadata = ar.get("metadata") or {}
    stdout = str(metadata.get("stdout", "") if isinstance(metadata, dict) else "")
    iters = len(r.get("step_results") or [])

    if reward in (1.0, 1):
        return ("PASS", f"reward=1.0 iters={iters}")
    infra_markers = ["ConnectionRefused", "502", "503", "Service Unavailable",
                     "no_available_workers", "Connection reset by peer"]
    if iters == 0 and any(m in stdout for m in infra_markers):
        marker = next(m for m in infra_markers if m in stdout)
        return ("INFRA", f"iters=0 stdout={marker} (model never ran)")
    if "timed out" in exc_msg.lower() or "timeout" in exc_msg.lower():
        return ("NA", f"timeout: {exc_msg[:80]}")
    if reward in (0.0, 0):
        detail = f"reward=0 iters={iters}"
        if "max turns" in stdout.lower():
            detail += " (max turns reached)"
        return ("FAIL", detail)
    if reward is None:
        if iters == 0 and not stdout:
            return ("INFRA", "no_run: reward=None iters=0 no_stdout")
        return ("FAIL", f"reward=None iters={iters} stdout={len(stdout)}c")
    return ("FAIL", f"reward={reward}")


def merge():
    all_tasks = load_task_list(TB21_TASKS_FILE)
    r2_manifest = load_task_list(R2_MANIFEST)
    r2_set = set(r2_manifest)
    r1_results = scan_results(R1_DIRS)
    r2_results = scan_results([R2_DIR])

    task_set = set(all_tasks) | set(r1_results.keys()) | set(r2_results.keys())
    task_set = {t for t in task_set if not t.startswith("2026-")}

    merged = {}
    counts = {"PASS": 0, "FAIL": 0, "INFRA": 0, "NA": 0, "RUNNING": 0}

    for t in sorted(task_set):
        r1_cat, r1_det = classify(r1_results.get(t))
        r2_present = t in r2_set
        r2_cat, r2_det = classify(r2_results.get(t)) if r2_present else ("ABSENT", "not in R2")

        if r1_cat == "PASS":
            fc, fd = "PASS", f"R1 PASS ({r1_det})"
        elif r2_present and r2_cat == "PASS":
            fc, fd = "PASS", f"R2 PASS ({r2_det}) [R1={r1_cat}]"
        elif r2_present and r2_cat == "RUNNING":
            fc, fd = "RUNNING", f"R2 running [R1={r1_cat}: {r1_det}]"
        elif r2_present and r2_cat == "INFRA":
            fc, fd = "INFRA", f"R2 INFRA ({r2_det}) [R1={r1_cat}]"
        elif r2_present and r2_cat == "NA":
            fc, fd = "NA", f"R2 NA ({r2_det}) [R1={r1_cat}]"
        elif r2_present and r2_cat == "FAIL":
            fc, fd = "FAIL", f"R2 FAIL ({r2_det}) [R1={r1_cat}]"
        elif r2_present and r2_cat == "ABSENT":
            fc, fd = r1_cat, f"R1 {r1_cat} ({r1_det}) [R2 manifest missing]"
        else:
            fc, fd = r1_cat, f"R1 {r1_cat} ({r1_det})"

        merged[t] = {"final": fc, "detail": fd, "r1": r1_cat, "r1_detail": r1_det,
                     "r2": r2_cat if r2_present else "ABSENT",
                     "r2_detail": r2_det if r2_present else "not in R2"}
        counts[fc] = counts.get(fc, 0) + 1

    total = len(merged)
    evaluated = total - counts["RUNNING"] - counts["INFRA"]
    summary = {
        "total_tasks": total, "PASS": counts["PASS"], "FAIL_ability": counts["FAIL"],
        "INFRA": counts["INFRA"], "NA_timeout": counts["NA"], "RUNNING": counts["RUNNING"],
        "evaluated": evaluated,
        "pass_pct_of_89": f"{100*counts['PASS']/total:.1f}%" if total else "N/A",
        "pass_pct_of_evaluated": f"{100*counts['PASS']/evaluated:.1f}%" if evaluated else "N/A",
        "conn_refused": sum(1 for t, v in merged.items()
                            if "ConnectionRefused" in v.get("r2_detail", "") or
                            "ConnectionRefused" in v.get("r1_detail", "")),
    }
    return {"summary": summary, "per_task": merged, "r2_manifest": r2_manifest,
            "r2_completed": len(r2_results), "r2_running": counts["RUNNING"]}


if __name__ == "__main__":
    result = merge()
    s = result["summary"]
    print(f"=== CC TB-2.1 MERGED R1+R2 ===")
    print(f"Total:     {s['total_tasks']}")
    print(f"PASS:      {s['PASS']}")
    print(f"FAIL:      {s['FAIL_ability']}")
    print(f"INFRA:     {s['INFRA']}")
    print(f"NA/timeout:{s['NA_timeout']}")
    print(f"RUNNING:   {s['RUNNING']}")
    print(f"ConnRefused:{s['conn_refused']}")
    print(f"Pass%(89): {s['pass_pct_of_89']}")
    print(f"Pass%(eval):{s['pass_pct_of_evaluated']}")
    if s["RUNNING"] > 0:
        rt = [t for t, v in result["per_task"].items() if v["final"] == "RUNNING"]
        print(f"\nSTILL RUNNING ({len(rt)}): {rt}")
        print("WARNING: Round2 not complete - merge is partial.")
    with open(OUT_PATH, "w") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"\nSaved: {OUT_PATH}")
