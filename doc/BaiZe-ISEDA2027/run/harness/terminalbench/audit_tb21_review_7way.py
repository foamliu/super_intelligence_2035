#!/usr/bin/env python3
"""audit_tb21_review_7way.py — TB-2.1 七路失败归因复核（merged original+rerun）

用户令 (2026-11-17 08:5x):
  「结果再复核一遍，看失败的 Case 是否均为能力不足，而非 infra 问题」

用户令 (2026-11-17 10:2x) — 纠正归因口径:
  「有 x 未真跑，那举措不应该是重跑吗？你把分直接加上去算什么？」
  → 撤回「修正后 Pass% = passed / (89 − pure_infra)」(它把未真跑题从分母剔除，
     等价于假设这些题真跑就能通过 = 凭空抬分)。未真跑题的处置只有一个正解:
     重跑拿真实结果。真正的可对外引用成绩只有 passed / 89 (分母恒 89)。
     BLOCKED(infra) 题单列, 不误算为通过, 剔除时必须显式注明原因。

扫描 original + 所有 rerun 目录，按 task_name 合并（PASS 优先），
对合并后仍失败的题做四桶归因：ability / quota / conn_refused / synthetic。
真实 Pass% = passed / 89 (分母恒 89, 唯一可对外引用口径)。
infra 桶 (quota/conn_refused/synthetic) = 待重跑, 不从分母剔除。
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
        # §2026-11-17 10:2x: 真实 Pass% = passed / 89 (分母恒 89).
        # 不再计算 corrected_pass_pct = passed/(89-pure_infra) — 那是凭空抬分.
        # infra 桶 (quota/conn_refused/synthetic) = 待重跑, 重跑后 pass 就 +1, fail 计失败.
        real_pct = passed / total * 100
        bc = {"ability": len(buckets["ability"]), "quota": len(buckets["quota"]),
              "conn_refused": len(buckets["conn_refused"]),
              "synthetic": len(buckets["synthetic"]),
              "not_evaluated": len(buckets["not_evaluated"])}
        result["harnesses"][h] = {
            "display": DISP[h], "evaluated": len(task_data), "passed": passed,
            "real_pass_pct": round(real_pct, 1), "buckets": buckets,
            "bucket_counts": bc, "pending_rerun": pure_infra,
            "detail": detail}
        print(f"[review] {DISP[h]:16s}: pass={passed:2d}/{total} "
              f"({real_pct:.1f}%) | ability={bc['ability']:2d} "
              f"quota={bc['quota']:2d} conn_ref={bc['conn_refused']:2d} "
              f"synthetic={bc['synthetic']:2d} not_eval={bc['not_evaluated']:2d} "
              f"| 待重跑(infra)={pure_infra} (重跑完成后重算真实 Pass%)")
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    out = MANIFESTS / f"tb21_review_7way_{time.strftime('%Y%m%d_%H%M')}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[review] written: {out} ({out.stat().st_size} bytes)")
    parts = []
    for h in HARNESSES:
        r = result["harnesses"][h]
        parts.append(f"{DISP[h]}:{r['passed']}/{total}={r['real_pass_pct']}%"
                     f"(待重跑={r['pending_rerun']})")
    print("[review] MEMORY line: " + " | ".join(parts))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
