#!/usr/bin/env python3
"""rerun_tb21_7way_quota.py — TB-2.1 七路「额度耗尽 / synthetic 假结果」失败重跑编排器

用户令 (2026-11-14 08:0x):
  「安排 harness 查一下，cline 和其他 harness 是否仍然有（网关 token 额度耗尽）
   导致失败的 Case，有则重跑。现在是周末。」

本脚本是 B 部分 (重跑)。它从 audit JSON (A 部分产物) 读取每路的 rerun_targets,
逐路调用 rerun_tb21_cline_quota.py (已参数化为支持任意 harness via --task-list)。

流程:
  1. 读 reports/tb21_quota_audit_7way_<tag>.json
  2. 对每路 (有 rerun_targets > 0 的): 写 task-list → 调 rerun --launch
  3. 跑完后: 逐路 --merge → REGEN 双报告

用法:
  python3 rerun_tb21_7way_quota.py --audit <json>    # 打印计划
  python3 rerun_tb21_7way_quota.py --audit <json> --launch  # 执行重跑 (逐路串行)
  python3 rerun_tb21_7way_quota.py --audit <json> --merge-all  # 逐路 merge
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
DOC_DIR = HERE.parent.parent.parent
REPORTS = DOC_DIR / "reports"

HARNESS_AGENT = {
    "cline-patched":    "terminalbench.agents.cline_patched:ClinePatched",
    "codex":            "terminalbench.agents.codex:CodexTB",
    "hermes":           "terminalbench.agents.hermes:HermesTB",
    "opencode":         "terminalbench.agents.opencode:OpenCodeTB",
    "claude-code":      "terminalbench.agents.claude_code:ClaudeCodeTB",
    "deepseek-harness": "terminalbench.agents.deepseek_harness:DeepseekHarnessTB",
    "pi":               "terminalbench.agents.pi:PiTB",
}
DISP = {"cline-patched": "cline", "codex": "codex", "opencode": "opencode",
        "claude-code": "claude-code", "pi": "pi", "hermes": "hermes",
        "deepseek-harness": "deepseek"}

def load_audit(audit_path):
    """Load audit JSON and extract rerun_targets per harness."""
    data = json.loads(Path(audit_path).read_text())
    plan = {}
    for h, info in data.get("harnesses", {}).items():
        s = info["summary"]
        targets = sorted(set(s.get("rerun_targets", [])))
        if targets:
            plan[h] = targets
    return plan, data


def write_task_list(harness, tasks, tag):
    """Write a task-list file for the rerun script."""
    out = HERE / "manifests" / f"tb21_7way_rerun_{harness}_{tag}.txt"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(tasks) + "\n")
    return out


def launch_route(harness, tasks, tag, timeout=3600):
    """Launch rerun for a single harness via rerun_tb21_cline_quota.py --task-list."""
    task_file = write_task_list(harness, tasks, tag)
    agent = HARNESS_AGENT.get(harness, "")
    print(f"\n{'='*60}")
    print(f"[rerun-7way] {DISP[harness]}: {len(tasks)} tasks, agent={agent}")
    print(f"[rerun-7way] task-list: {task_file}")
    cmd = [
        sys.executable, str(HERE / "rerun_tb21_cline_quota.py"),
        "--task-list", str(task_file),
        "--launch",
        "--timeout", str(timeout),
        "--n-concurrent", "1",
    ]
    env = dict(os.environ)
    env["RERUN_TAG"] = f"7way_{tag}_{harness}"
    print(f"[rerun-7way] cmd: {' '.join(cmd)}")
    r = subprocess.run(cmd, env=env)
    return r.returncode


def merge_route(harness, tag):
    """Merge rerun results for a single harness."""
    jobs_dir = Path("/tmp/tb21_glm53_jobs") / f"{harness}_rerun_7way_{tag}_{harness}"
    if not jobs_dir.exists():
        print(f"[merge-7way] {DISP[harness]}: no rerun dir {jobs_dir}")
        return
    cmd = [
        sys.executable, str(HERE / "rerun_tb21_cline_quota.py"),
        "--merge", str(jobs_dir),
    ]
    env = dict(os.environ)
    env["RERUN_TAG"] = f"7way_{tag}_{harness}"
    print(f"[merge-7way] {DISP[harness]}: {jobs_dir}")
    r = subprocess.run(cmd, env=env)
    return r.returncode


def regen_reports():
    """Regenerate both reports after all merges."""
    print("\n[regen] regenerating TB-2.1 7way report...")
    subprocess.run([sys.executable, str(HERE / "gen_report_tb21_7way.py")])
    print("[regen] regenerating cline special report...")
    subprocess.run([sys.executable, str(HERE.parent / "gen_cline_special.py")])


def main():
    ap = argparse.ArgumentParser(description="TB-2.1 七路额度/synthetic 失败重跑编排器")
    ap.add_argument("--audit", required=True, help="audit JSON path")
    ap.add_argument("--launch", action="store_true", help="逐路串行重跑")
    ap.add_argument("--merge-all", action="store_true", help="逐路 merge + regen")
    ap.add_argument("--timeout", type=int, default=3600, help="单题超时秒")
    ap.add_argument("--routes", nargs="*", default=None,
                    help="只重跑指定路 (如 cline-patched opencode)")
    args = ap.parse_args()

    tag = time.strftime("%Y%m%d_%H%M")
    plan, data = load_audit(args.audit)

    print(f"[rerun-7way] audit: {args.audit}")
    print(f"[rerun-7way] total rerun_targets per route:")
    total = 0
    for h in HARNESS_AGENT:
        if h not in plan:
            continue
        if args.routes and h not in args.routes:
            continue
        n = len(plan[h])
        total += n
        print(f"  {DISP[h]:16s}: {n:3d} rerun_targets")
    print(f"[rerun-7way] total: {total}")

    if args.launch:
        for h in HARNESS_AGENT:
            if h not in plan:
                continue
            if args.routes and h not in args.routes:
                continue
            rc = launch_route(h, plan[h], tag, timeout=args.timeout)
            if rc != 0:
                print(f"[rerun-7way] WARNING: {DISP[h]} rc={rc}, continuing...")

    if args.merge_all:
        for h in HARNESS_AGENT:
            if h not in plan:
                continue
            if args.routes and h not in args.routes:
                continue
            merge_route(h, tag)
        regen_reports()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
