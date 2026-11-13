#!/usr/bin/env python3
"""rerun_tb21_cline_quota.py — TB-2.1 cline「网关 Token 额度耗尽」失败重跑

背景（R2386 根因，2026-11-13）：
  TB-2.1 cline 89 题里 10 passed（11.2%），80 个失败 trial 中 **65 个（81%）** 的失败
  原因是网关 Token 额度耗尽（stdout 含「本次Token额度已用完」/「Token额度」，
  iterations=1 / 0 tokens = 零工作），不是模型能力；公平通过率 10/25 = 40%。
  ⇒ 用户令（2026-11-13 18:2x）：回顾 cline 失败 case，额度耗尽的就重跑。

判定口径（与 gen_report_tb21_7way.py::_cline_attrtribution 完全一致）：
  job 目录 ：/tmp/tb21_glm53_jobs/cline-patched/<date>/<task>__<id>/result.json
  reward    ：result["verifier_result"]["rewards"]["reward"] == 1.0 ⇒ passed
  stdout    ：result["agent_result"]["metadata"]["stdout"]
  quota     ：「额度已用完」in stdout or 「Token额度」in stdout
  task 级   ：best_reward < 1.0 且 **全部** trial 都是 quota ⇒ quota_lost（重跑目标）
              只要有一个 trial 不是 quota ⇒ 不重跑（可能含能力/超时/parse 因素）

用法：
  python3 rerun_tb21_cline_quota.py                  # dry-run：统计 + 写清单（默认）
  python3 rerun_tb21_cline_quota.py --launch         # symlink 子数据集 + harbor 重跑
  python3 rerun_tb21_cline_quota.py --merge <dir>    # 重跑结果并入官方 jobs-dir
  python3 rerun_tb21_cline_quota.py --task-list f    # 手动指定 task（每行一个）

产物：
  reports/tb21_cline_quota_rerun_<tag>.json   逐题证据 + 汇总
  reports/tb21_cline_quota_rerun_ids.txt      待重跑 task 名（每行一个）
  traces/tb21_cline_quota_rerun_<tag>.log     --launch 的 harbor 原始输出

注意：
  * 只读 /tmp/tb21_glm53_jobs 现有结果，不改动原 trial 目录（merge 除外，且只搬 rerun 产物）；
  * 必须先确认网关 200（gw_proxy 9092）；429 状态下重跑只会再造一批空 patch；
  * 重跑按 unique task 计分，同一题多 trial 不重复计数（与 7way 报告口径一致）。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent                      # run/harness
REPO_LINE_DIR = HARNESS_DIR.parent             # run/
DOC_DIR = REPO_LINE_DIR.parent                 # doc/BaiZe-ISEDA2027
REPORTS = DOC_DIR / "reports"
TRACES = HERE / "traces"

JOBS = Path("/tmp/tb21_glm53_jobs")
HARNESS = "cline-patched"
AGENT = "terminalbench.agents.cline_patched:ClinePatched"
TB_DATASET = Path(os.path.expanduser("~/terminal-bench"))
OVERLAY = HERE / "overlay-network-host.yml"
LAUNCH_SCRIPT = HERE / "launch_tb21_glm53_7way.sh"   # 只为复用其中已登记的 key/env
GW_MODELS = "http://127.0.0.1:9092/v1/models"

# ---------------------------------------------------------------------------
# 1. 扫描 + 归因
# ---------------------------------------------------------------------------

def _iter_result_files(root: Path):
    """只取 dated job 子目录里的 result.json（与报告口径 '/20' 过滤一致）。"""
    if not root.exists():
        return
    for f in root.rglob("result.json"):
        if "/20" in str(f).replace("\\", "/"):
            yield f


def scan_trials(root: Path = None):
    """返回 task -> [trial dict]；trial 字段与 R2386 归因脚本同口径。"""
    root = root or (JOBS / HARNESS)
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
        task = str(f.parent.name).split("__")[0]
        task_data.setdefault(task, []).append({
            "dir": str(f.parent),
            "reward": reward,
            "quota": quota,
            "iterations": int(m.group(1)) if m else -1,
            "exc_type": ei.get("exception_type", ""),
            "exit_code": meta.get("exit_code"),
            "has_run_result": '"run_result"' in stdout,
            "stdout_len": len(stdout),
        })
    return task_data


def classify(task_data):
    """返回 (summary, quota_lost_tasks, detail)。"""
    passed, quota_lost, other_failed = [], [], []
    detail = {}
    for task, trials in sorted(task_data.items()):
        best = max(t["reward"] for t in trials)
        if best == 1.0:
            passed.append(task)
            continue
        all_quota = all(t["quota"] for t in trials)
        (quota_lost if all_quota else other_failed).append(task)
        detail[task] = {
            "category": "quota_exhausted" if all_quota else "non_quota",
            "best_reward": best,
            "trials": trials,
        }
    summary = {
        "unique_tasks": len(task_data),
        "trials_total": sum(len(v) for v in task_data.values()),
        "passed": len(passed),
        "failed": len(task_data) - len(passed),
        "quota_lost_tasks": len(quota_lost),
        "non_quota_failed_tasks": len(other_failed),
        "pass_rate": round(len(passed) / max(len(task_data), 1), 4),
    }
    return summary, quota_lost, detail


# ---------------------------------------------------------------------------
# 2. 清单落盘
# ---------------------------------------------------------------------------

def write_manifest(summary, quota_lost, detail, tag):
    REPORTS.mkdir(parents=True, exist_ok=True)
    out_json = REPORTS / f"tb21_cline_quota_rerun_{tag}.json"
    out_ids = REPORTS / "tb21_cline_quota_rerun_ids.txt"
    payload = {
        "round": "rerun-cline-quota",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source_jobs": str(JOBS / HARNESS),
        "rule": "best_reward<1.0 AND all trials stdout contains 额度已用完/Token额度",
        "summary": summary,
        "rerun_tasks": quota_lost,
        "detail": detail,
    }
    out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2))
    out_ids.write_text("\n".join(quota_lost) + ("\n" if quota_lost else ""))
    return out_json, out_ids


# ---------------------------------------------------------------------------
# 3. 重跑（harbor 子集）
# ---------------------------------------------------------------------------

def _api_key():
    """优先 env，其次从既有 launch 脚本里取（不新增明文副本）。"""
    for k in ("TB_API_KEY", "GLM53_KEY"):
        if os.environ.get(k):
            return os.environ[k]
    if LAUNCH_SCRIPT.exists():
        m = re.search(r'GLM53_KEY="([^"]+)"', LAUNCH_SCRIPT.read_text(errors="replace"))
        if m:
            return m.group(1)
    return ""


def _gateway_ok(timeout=6):
    try:
        with urllib.request.urlopen(GW_MODELS, timeout=timeout) as r:
            return r.status == 200
    except Exception:
        return False


def launch(tasks, tag, n_concurrent=1, timeout_s=3600, dry=False):
    if not tasks:
        print("[launch] 无 quota_lost 题，跳过")
        return None
    if not TB_DATASET.exists():
        print(f"[launch] FATAL: dataset 不存在 {TB_DATASET}", file=sys.stderr)
        return None
    key = _api_key()
    if not key:
        print("[launch] FATAL: 取不到 TB_API_KEY（env 或 launch 脚本）", file=sys.stderr)
        return None
    if not _gateway_ok():
        print(f"[launch] FATAL: 网关未就绪 {GW_MODELS}（429/断网时重跑无意义）", file=sys.stderr)
        return None

    subset = Path(tempfile.mkdtemp(prefix="tb21_cline_quota_"))
    missing = []
    for t in tasks:
        src = TB_DATASET / t
        if src.exists():
            (subset / t).symlink_to(src)
        else:
            missing.append(t)
    if missing:
        print(f"[launch] WARNING: 数据集缺 {len(missing)} 题: {missing[:5]}...", file=sys.stderr)

    jobs_dir = JOBS / f"{HARNESS}_rerun_{tag}"
    jobs_dir.mkdir(parents=True, exist_ok=True)
    TRACES.mkdir(parents=True, exist_ok=True)
    log = TRACES / f"tb21_cline_quota_rerun_{tag}.log"

    env = dict(os.environ)
    home = os.path.expanduser("~")
    env.update({
        "TB_MODEL": "glm-5.3-flash",
        "TB_API_KEY": key,
        "TB_BASE_URL": "http://agi-gateway.cxmt.com/v1",
        "TB_GW_PROXY_URL": "http://127.0.0.1:9092/v1",
        "TB_GW_PROXY_BASE": "http://127.0.0.1:9092",
        "TB_AGENT_TIMEOUT": str(timeout_s),
        "PYTHONPATH": f"{HARNESS_DIR}:{env.get('PYTHONPATH', '')}",
        "PATH": f"{home}/.bun/bin:{home}/.local/bin:{env.get('PATH', '')}",
        "no_proxy": "127.0.0.1,localhost,agi-gateway.cxmt.com",
        "NO_PROXY": "127.0.0.1,localhost,agi-gateway.cxmt.com",
        "PYTHONUNBUFFERED": "1",
    })
    for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
        env.pop(k, None)

    cmd = [
        "nice", "-n", "19", "harbor", "run", "-p", str(subset),
        "--agent", AGENT, "-k", "1", "--n-concurrent", str(n_concurrent),
        "--extra-docker-compose", str(OVERLAY), "--jobs-dir", str(jobs_dir),
    ]
    print(f"[launch] tasks={len(tasks)} jobs_dir={jobs_dir}")
    print("[launch] " + " ".join(cmd))
    if dry:
        return jobs_dir

    with log.open("w") as fh:
        fh.write(f"# {time.strftime('%F %T')} {' '.join(cmd)}\n")
        fh.flush()
        p = subprocess.Popen(cmd, env=env, stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT, text=True, bufsize=1)
        for line in p.stdout:
            fh.write(line)
            fh.flush()
            sys.stdout.write(line)
        p.wait()
    print(f"[launch] harbor rc={p.returncode} log={log}")
    return jobs_dir


# ---------------------------------------------------------------------------
# 4. 并入官方 jobs-dir（让既有报告自动吃到重跑结果）
# ---------------------------------------------------------------------------

def merge(rerun_jobs, tag):
    dst_root = JOBS / HARNESS
    dst_root.mkdir(parents=True, exist_ok=True)
    moved = 0
    for dated in sorted(p for p in rerun_jobs.iterdir() if p.is_dir()):
        dst_dir = dst_root / f"{dated.name}_rerun_{tag}"
        dst_dir.mkdir(parents=True, exist_ok=True)
        for trial in sorted(p for p in dated.iterdir() if p.is_dir()):
            task = trial.name.split("__")[0]
            dst = dst_dir / f"{task}__rerun_{tag}"
            if dst.exists():          # 幂等：已搬过就跳过
                continue
            shutil.move(str(trial), str(dst))
            moved += 1
    print(f"[merge] moved {moved} trials -> {dst_root}")
    return moved


# ---------------------------------------------------------------------------

def main():
    global JOBS
    ap = argparse.ArgumentParser(description="TB-2.1 cline 额度耗尽失败重跑")
    ap.add_argument("--launch", action="store_true", help="真跑（默认 dry-run）")
    ap.add_argument("--merge", metavar="RERUN_JOBS_DIR", default=None,
                    help="把重跑 jobs-dir 并入 /tmp/tb21_glm53_jobs/cline-patched")
    ap.add_argument("--task-list", default=None, help="手动指定 task 列表文件")
    ap.add_argument("--n-concurrent", type=int, default=1)
    ap.add_argument("--timeout", type=int, default=3600, help="单题 agent 超时秒")
    ap.add_argument("--jobs-root", default=str(JOBS), help="job 根目录（默认 /tmp/tb21_glm53_jobs）")
    ap.add_argument("--dry-run", action="store_true", help="只打印 harbor 命令，不执行")
    args = ap.parse_args()

    JOBS = Path(args.jobs_root)
    tag = os.environ.get("RERUN_TAG") or time.strftime("%Y%m%d_%H%M")

    if args.merge:
        merge(Path(args.merge), tag)
        return 0

    if args.task_list:
        tasks = [ln.strip() for ln in Path(args.task_list).read_text().splitlines() if ln.strip()]
        print(f"[scan] 手动 task-list: {len(tasks)}")
        summary = {"unique_tasks": len(tasks), "trials_total": 0, "passed": 0,
                   "failed": len(tasks), "quota_lost_tasks": len(tasks),
                   "non_quota_failed_tasks": 0, "pass_rate": 0.0}
        detail = {t: {"category": "manual", "best_reward": None, "trials": []} for t in tasks}
    else:
        task_data = scan_trials(JOBS / HARNESS)
        if not task_data:
            print(f"[scan] FATAL: 读不到结果 {JOBS / HARNESS}", file=sys.stderr)
            return 2
        summary, tasks, detail = classify(task_data)
        print("[scan] " + json.dumps(summary, ensure_ascii=False))

    out_json, out_ids = write_manifest(summary, tasks, detail, tag)
    print(f"[scan] quota_lost={len(tasks)} -> {out_json}")
    print(f"[scan] ids -> {out_ids}")
    for t in tasks[:10]:
        print(f"  - {t}")
    if len(tasks) > 10:
        print(f"  ... (+{len(tasks) - 10})")

    if args.launch:
        jobs_dir = launch(tasks, tag, args.n_concurrent, args.timeout, dry=args.dry_run)
        if jobs_dir:
            print(f"\n[next] 跑完执行：python3 {Path(__file__).name} --merge {jobs_dir}")
            print("[next] 然后重新生成双报告：python3 gen_report_tb21_7way.py && "
                  "python3 ../gen_cline_special.py")
    return 0


if __name__ == "__main__":
    sys.exit(main())
