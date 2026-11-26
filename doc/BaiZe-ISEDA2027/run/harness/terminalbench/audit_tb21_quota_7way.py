#!/usr/bin/env python3
"""audit_tb21_quota_7way.py — TB-2.1 七路「网关 Token 额度耗尽」诊断审计

用户令 (2026-11-14 08:0x):
  「安排 harness 查一下，cline 和其他 harness 是否仍然有（网关 token 额度耗尽）
   导致失败的 Case，有则重跑。现在是周末。」

覆盖全部 7 路, 逐路扫 /tmp/tb21_glm53_jobs/<harness>/ 的 dated 子目录 result.json,
按五桶分类:
  quota_only          — best_reward<1.0 且全部 trial 命中额度 → 重跑目标
  mixed_fail          — best_reward<1.0 且部分 trial 额度、部分非额度 → 不重跑
  ability_fail        — best_reward<1.0 且无额度、有 proper 证据 → 能力
  synthetic_or_never_ran — best_reward<1.0 且无 run_result → 假结果/未真跑 → 重跑目标
  not_evaluated       — 89 题中未出现在任何 result.json → 补跑

判定口径逐字复用 rerun_tb21_cline_quota.py::classify 与
gen_report_tb21_7way.py::_cline_attrtribution。

用法:
  python3 audit_tb21_quota_7way.py            # 诊断 + 落盘 JSON
  python3 audit_tb21_quota_7way.py --verbose  # 额外打印每路逐题明细

产物:
  reports/tb21_quota_audit_7way_<tag>.json  — 七路五桶汇总 + 逐题明细
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
REPO_LINE_DIR = HARNESS_DIR.parent
DOC_DIR = REPO_LINE_DIR.parent
REPORTS = DOC_DIR / "reports"

JOBS = Path("/tmp/tb21_glm53_jobs")
TB_DATASET = Path(os.path.expanduser("~/terminal-bench"))

HARNESSES = ["cline-patched", "codex", "opencode", "claude-code",
             "pi", "hermes", "deepseek-harness"]
DISP = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
        "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
        "deepseek-harness": "deepseek"}

AGENT_MAP = {
    "cline-patched":    "terminalbench.agents.cline_patched:ClinePatched",
    "codex":            "terminalbench.agents.codex:CodexTB",
    "hermes":           "terminalbench.agents.hermes:HermesTB",
    "opencode":         "terminalbench.agents.opencode:OpenCodeTB",
    "claude-code":      "terminalbench.agents.claude_code:ClaudeCodeTB",
    "deepseek-harness": "terminalbench.agents.deepseek_harness:DeepseekHarnessTB",
    "pi":               "terminalbench.agents.pi:PiTB",
}

def _is_dated_dir(name: str) -> bool:
    """判断目录名是否为 dated job 目录 (如 '2026-11-09__19-51-22')。"""
    return bool(re.match(r"^\d{4}-\d{2}-\d{2}__", name))


def _iter_result_files(root: Path):
    """只取 task 级 result.json (跳过 dated job 级 result.json)。

    job 级: .../2026-11-09__19-51-22/result.json  (parent=dated dir → skip)
    task 级: .../2026-11-09__19-51-22/<task>__<id>/result.json  (parent=task dir → keep)
    """
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if "/20" not in str(f).replace("\\", "/"):
            continue
        if _is_dated_dir(f.parent.name):
            continue                        # skip job-level result.json
        yield f


def scan_trials(root: Path):
    """返回 task -> [trial dict]。"""
    task_data = {}
    for f in _iter_result_files(root):
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
        quota = ("额度已用完" in stdout) or ("Token额度" in stdout)
        m = re.search(r'"iterations":(\d+)', stdout)
        econn = "ECONNRESET" in stdout
        task = str(f.parent.name).split("__")[0]
        conn_refused = "ConnectionRefused" in stdout
        cli_bug = ("unknown option" in stdout.lower() and meta.get("exit_code") == 1
                   and '"run_result"' not in stdout)
        task_data.setdefault(task, []).append({
            "dir": str(f.parent),
            "reward": reward,
            "quota": quota,
            "econn": econn,
            "conn_refused": conn_refused,
            "cli_bug": cli_bug,
            "iterations": int(m.group(1)) if m else -1,
            "exc_type": ei.get("exception_type", ""),
            "exit_code": meta.get("exit_code"),
            "has_run_result": '"run_result"' in stdout,
            "stdout_len": len(stdout),
        })
    return task_data


def classify_route(task_data, all_tasks):
    """返回 (buckets_dict, detail_dict)。五桶分类。"""
    buckets = {
        "passed": [],
        "quota_only": [],
        "mixed_fail": [],
        "connection_refused": [],
        "ability_fail": [],
        "synthetic_or_never_ran": [],
        "not_evaluated": [],
    }
    detail = {}
    evaluated = set(task_data.keys())

    for task, trials in sorted(task_data.items()):
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            buckets["passed"].append(task)
            continue

        all_quota = all(t["quota"] for t in trials)
        any_quota = any(t["quota"] for t in trials)
        all_conn_refused = all(t.get("conn_refused") for t in trials)
        any_conn_refused = any(t.get("conn_refused") for t in trials)
        all_synthetic = all(
            (not t["has_run_result"]) and t["stdout_len"] < 50
            for t in trials
        )
        has_cli_bug = any(t.get("cli_bug") for t in trials)
        has_proper_evidence = any(
            t["iterations"] > 1
            or t["has_run_result"]
            or t["exc_type"]
            or t["econn"]
            for t in trials
        )

        if all_conn_refused:
            cat = "connection_refused"
        elif has_cli_bug and not any_quota:
            cat = "connection_refused"  # CLI parse bug = adapter issue, same infra bucket
        elif all_synthetic:
            cat = "synthetic_or_never_ran"
        elif all_quota:
            cat = "quota_only"
        elif any_quota:
            cat = "mixed_fail"
        elif has_proper_evidence:
            cat = "ability_fail"
        else:
            cat = "synthetic_or_never_ran"

        buckets[cat].append(task)
        detail[task] = {
            "category": cat,
            "best_reward": best,
            "n_trials": len(trials),
            "trials": trials,
        }

    for t in sorted(all_tasks):
        if t not in evaluated:
            buckets["not_evaluated"].append(t)

    return buckets, detail

def get_all_tasks():
    """获取 TB-2.1 全部任务名 (89 题)。"""
    if TB_DATASET.exists():
        return sorted(x.name for x in TB_DATASET.iterdir() if x.is_dir())
    return []


def main():
    ap = argparse.ArgumentParser(description="TB-2.1 七路额度耗尽诊断审计")
    ap.add_argument("--verbose", action="store_true", help="打印每路逐题明细")
    ap.add_argument("--tag", default=None, help="输出文件 tag (默认时间戳)")
    args = ap.parse_args()

    tag = args.tag or time.strftime("%Y%m%d_%H%M")
    all_tasks = get_all_tasks()
    total_tasks = len(all_tasks)
    print(f"[audit] TB-2.1 total tasks: {total_tasks}")
    if total_tasks == 0:
        print("[audit] WARNING: dataset not found, using 89 as fallback")
        total_tasks = 89

    result = {
        "round": "audit-tb21-quota-7way",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_tasks": total_tasks,
        "harnesses": {},
    }

    for h in HARNESSES:
        root = JOBS / h
        task_data = scan_trials(root)
        buckets, detail = classify_route(task_data, all_tasks)
        evaluated = len(task_data)
        passed = len(buckets["passed"])

        route_summary = {
            "evaluated": evaluated,
            "not_evaluated": len(buckets["not_evaluated"]),
            "passed": passed,
            "quota_only": len(buckets["quota_only"]),
            "mixed_fail": len(buckets["mixed_fail"]),
            "connection_refused": len(buckets["connection_refused"]),
            "ability_fail": len(buckets["ability_fail"]),
            "synthetic_or_never_ran": len(buckets["synthetic_or_never_ran"]),
            "pass_rate": round(passed / max(evaluated, 1), 4),
            "rerun_targets": sorted(
                set(buckets["quota_only"]) | set(buckets["synthetic_or_never_ran"])
                | set(buckets["connection_refused"])
            ),
            "agent": AGENT_MAP.get(h, ""),
        }
        result["harnesses"][h] = {
            "summary": route_summary,
            "buckets": buckets,
            "detail": detail if args.verbose else None,
        }

        name = DISP[h]
        rrt = route_summary["rerun_targets"]
        print(
            f"[audit] {name:16s}: eval={evaluated:3d}/{total_tasks} "
            f"pass={passed:3d} ({route_summary['pass_rate']*100:.1f}%) | "
            f"quota_only={route_summary['quota_only']:2d} "
            f"mixed={route_summary['mixed_fail']:2d} "
            f"conn_refused={route_summary['connection_refused']:2d} "
            f"ability={route_summary['ability_fail']:2d} "
            f"synthetic={route_summary['synthetic_or_never_ran']:2d} "
            f"not_eval={route_summary['not_evaluated']:2d} "
            f"| rerun_targets={len(rrt)}"
        )
        if args.verbose and rrt:
            for t in rrt[:15]:
                print(f"          - {t}")
            if len(rrt) > 15:
                print(f"          ... (+{len(rrt) - 15})")

    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / f"tb21_quota_audit_7way_{tag}.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2))
    print(f"\n[audit] written: {out} ({out.stat().st_size} bytes)")

    parts = []
    for h in HARNESSES:
        s = result["harnesses"][h]["summary"]
        parts.append(f"{DISP[h]}:Q={s['quota_only']}/S={s['synthetic_or_never_ran']}/CR={s['connection_refused']}/E={s['evaluated']}")
    print("[audit] MEMORY line: " + " | ".join(parts))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
