#!/usr/bin/env python3
"""audit_tb21_review_7way.py — TB-2.1 七路失败归因复核（merged original+rerun）

用户令 (2026-11-17 08:5x):
  「结果再复核一遍，看失败的 Case 是否均为能力不足，而非 infra 问题」

扫描 original + 所有 rerun 目录，按 task_name 合并（PASS 优先），
对合并后仍失败的题做四桶归因：ability / quota / conn_refused / synthetic。
修正后 Pass% = passed / (89 − pure_infra)。
产物落 manifests/（已 gitignore）。
"""
from __future__ import annotations
import json, os, re, time
from pathlib import Path

JOBS = Path("/tmp/tb21_glm53_jobs")
TB_DATASET = Path(os.path.expanduser("~/terminal-bench"))
MANIFESTS = Path("/nas_train/app.e0031982/code/super_intelligence_2035/doc/"
                 "BaiZe-ISEDA2027/run/harness/terminalbench/manifests")
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code",
             "pi", "hermes", "deepseek-harness"]
DISP = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
        "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
        "deepseek-harness": "deepseek"}


def _is_dated(name):
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__", name))


def _iter_task_results(root: Path):
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if "/20" not in str(f).replace("\\", "/"):
            continue
        if _is_dated(f.parent.name):
            continue
        yield f


def get_all_tasks():
    if TB_DATASET.exists():
        return sorted(x.name for x in TB_DATASET.iterdir() if x.is_dir())
    return []


def scan_route_all_dirs(h):
    """扫描 original + 所有 <h>_rerun_* 目录，返回 task -> [trial dict]。"""
    task_data = {}
    scan_dirs = [JOBS / h] if (JOBS / h).exists() else []
    for rd in sorted(JOBS.glob(f"{h}_rerun_*")):
        if rd.is_dir():
            scan_dirs.append(rd)
    for sd in scan_dirs:
        for f in _iter_task_results(sd):
            try:
                r = json.loads(f.read_text())
            except Exception:
                continue
            vr = r.get("verifier_result") or {}
            reward = (vr.get("rewards") or {}).get("reward", 0)
            ei = r.get("exception_info") or {}
            ar = r.get("agent_result") or {}
            meta = ar.get("metadata") or {}
            stdout = meta.get("stdout", "") or ""
            tn = r.get("task_name") or str(f.parent.name).split("__")[0]
            quota = ("额度已用完" in stdout) or ("Token额度" in stdout) or \
                    ("429" in stdout and "rate" in stdout.lower())
            m = re.search(r'"iterations":(\d+)', stdout)
            task_data.setdefault(tn, []).append({
                "dir": str(f.parent),
                "source": "rerun" if "_rerun_" in str(sd) else "original",
                "reward": reward, "quota": quota,
                "conn_refused": "ConnectionRefused" in stdout,
                "cli_bug": ("unknown option" in stdout.lower() and
                            meta.get("exit_code") == 1 and
                            '"run_result"' not in stdout),
                "econn": "ECONNRESET" in stdout,
                "iterations": int(m.group(1)) if m else -1,
                "exc_type": ei.get("exception_type", ""),
                "has_run_result": '"run_result"' in stdout,
                "stdout_len": len(stdout),
            })
    return task_data


def classify_merged(task_data, all_tasks):
    """合并所有 trial 后做四桶归因。PASS 优先。"""
    buckets = {"passed": [], "ability": [], "quota": [],
               "conn_refused": [], "synthetic": [], "not_evaluated": []}
    detail = {}
    for task, trials in sorted(task_data.items()):
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            buckets["passed"].append(task)
            continue
        all_quota = all(t["quota"] for t in trials)
        all_conn = all(t["conn_refused"] or t["cli_bug"] for t in trials)
        all_synthetic = all(
            (not t["has_run_result"]) and t["stdout_len"] < 50 for t in trials)
        has_proper = any(
            t["iterations"] > 1 or t["has_run_result"] or
            t["exc_type"] or t["econn"] for t in trials)
        if has_proper and not all_conn:
            cat = "ability"
        elif all_conn:
            cat = "conn_refused"
        elif all_synthetic:
            cat = "synthetic"
        elif all_quota:
            cat = "quota"
        elif has_proper:
            cat = "ability"
        else:
            cat = "synthetic"
        buckets[cat].append(task)
        detail[task] = {"category": cat, "best_reward": best,
                        "n_trials": len(trials),
                        "sources": sorted(set(t["source"] for t in trials))}
    for t in sorted(all_tasks):
        if t not in task_data:
            buckets["not_evaluated"].append(t)
    return buckets, detail


def main():
    all_tasks = get_all_tasks()
    total = len(all_tasks) or 89
    print(f"[review] TB-2.1 total tasks: {total}")
    result = {"round": "review-tb21-failure-attribution-7way",
              "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
              "total_tasks": total, "harnesses": {}}
    for h in HARNESSES:
        task_data = scan_route_all_dirs(h)
        buckets, detail = classify_merged(task_data, all_tasks)
        passed = len(buckets["passed"])
        pure_infra = (len(buckets["quota"]) + len(buckets["conn_refused"])
                      + len(buckets["synthetic"]))
        real_denom = total - pure_infra
        cur_pct = passed / total * 100
        cor_pct = passed / max(real_denom, 1) * 100
        bc = {"ability": len(buckets["ability"]), "quota": len(buckets["quota"]),
              "conn_refused": len(buckets["conn_refused"]),
              "synthetic": len(buckets["synthetic"]),
              "not_evaluated": len(buckets["not_evaluated"])}
        result["harnesses"][h] = {
            "display": DISP[h], "evaluated": len(task_data), "passed": passed,
            "current_pass_pct": round(cur_pct, 1), "buckets": buckets,
            "bucket_counts": bc, "pure_infra": pure_infra,
            "real_denom": real_denom,
            "corrected_pass_pct": round(cor_pct, 1), "detail": detail}
        print(f"[review] {DISP[h]:16s}: pass={passed:2d}/{total} "
              f"({cur_pct:.1f}%) | ability={bc['ability']:2d} "
              f"quota={bc['quota']:2d} conn_ref={bc['conn_refused']:2d} "
              f"synthetic={bc['synthetic']:2d} not_eval={bc['not_evaluated']:2d} "
              f"| pure_infra={pure_infra} real_denom={real_denom} "
              f"corrected={cor_pct:.1f}%")
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS / f"tb21_review_7way_{time.strftime('%Y%m%d_%H%M')}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[review] written: {out} ({out.stat().st_size} bytes)")
    parts = []
    for h in HARNESSES:
        r = result["harnesses"][h]
        parts.append(f"{DISP[h]}:{r['passed']}/{total}={r['current_pass_pct']}%"
                     f"->cor{r['corrected_pass_pct']}%(inf={r['pure_infra']})")
    print("[review] MEMORY line: " + " | ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
