#!/usr/bin/env python3
"""Serial per-harness runner — kimi-k2.6-cloud cross-eval (2026-10-05 directive).

Key differences from run_pilot_batch.py:
  1. Runs ONE harness across ALL instances (not all harnesses per instance).
  2. Concurrency = 1 (strictly serial, one instance at a time).
  3. Saves to kimi_pilot_results.json — no mixing with old deepseek results.
  4. Three-column reporting: resolved / patch-but-failed / quota-blocked.
  5. Quota discipline: on 429, PAUSE and wait for window reset.
"""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_WORK = Path("/nas_train/app.e0031982/harness_work")
INSTANCES_DIR = HARNESS_WORK / "instances"
WORKDIRS = Path("/dev/shm/harness_work/workdirs")
ROOTFS_DIR = HARNESS_WORK / "rootfs"
LOGS_EVAL = HARNESS_WORK / "logs_eval"
SUMMARY_PATH = HERE / "kimi_pilot_results.json"

ROOTFS_TEMPLATES = {
    "django/django":              ROOTFS_DIR / "django__django-10914",
    "sympy/sympy":                ROOTFS_DIR / "sympy__sympy-11400",
    "matplotlib/matplotlib":      ROOTFS_DIR / "matplotlib__matplotlib-18869",
    "scikit-learn/scikit-learn":  ROOTFS_DIR / "scikit-learn__scikit-learn-10297",
    "pytest-dev/pytest":          ROOTFS_DIR / "pytest-dev__pytest-11143",
    "sphinx-doc/sphinx":          ROOTFS_DIR / "sphinx-doc__sphinx-10325",
    "astropy/astropy":            ROOTFS_DIR / "astropy__astropy-12907",
    "psf/requests":               ROOTFS_DIR / "psf__requests-1963",
    "pylint-dev/pylint":          ROOTFS_DIR / "pylint-dev__pylint-5859",
    "pydata/xarray":              ROOTFS_DIR / "pydata__xarray-3364",
    "mwaskom/seaborn":            ROOTFS_DIR / "mwaskom__seaborn-2848",
    "pallets/flask":              ROOTFS_DIR / "pallets__flask-4045",
}
ALL_HARNESSES = ["cline-patched", "codex", "opencode", "claude-code", "deepseek-harness"]
TIMEOUT_RUN = 1800
TIMEOUT_EVAL = 1800
PROXY = "http://172.19.92.25:13128"
MODEL_NAME = os.environ.get("HARNESS_MODEL", "kimi-k2.6-cloud")
MAX_QUOTA_RETRIES = 3



def detect_quota_error(output: str) -> int | None:
    """Parse quota exhaustion messages. Returns wait_seconds or None."""
    m = re.search(r"请等待(\d+)分钟(\d+)秒", output)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + 60
    m = re.search(r"请等待(\d+)秒", output)
    if m:
        return int(m.group(1)) + 60
    if "Too Many Requests" in output or "429" in output:
        return 300
    if "本次Token额度已用完" in output:
        return 300
    return None


def run(cmd, cwd=None, timeout=300, env=None):
    e = os.environ.copy()
    e.setdefault("https_proxy", PROXY)
    e.setdefault("http_proxy", PROXY)
    e.setdefault("no_proxy", "127.0.0.1,localhost")
    if env:
        e.update(env)
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, timeout=timeout, env=e)
        return (p.stdout + p.stderr).decode(errors="replace"), p.returncode
    except subprocess.TimeoutExpired as ex:
        out = ((ex.stdout or b"") + (ex.stderr or b"")).decode(errors="replace")
        return out + "\n[TIMEOUT]", -1


def git_fetch_retry(workdir, base_commit, max_retries=3, timeout=300):
    """Git fetch with retry — addresses 65.7% block rate from 120s timeout."""
    for attempt in range(1, max_retries + 1):
        # Clean stale .lock files before each attempt
        for lock in Path(workdir / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=workdir, timeout=timeout)
        if rc == 0:
            return True, out
        if attempt < max_retries:
            print(f"  [FETCH RETRY {attempt}/{max_retries}] timeout={timeout}s, waiting 10s...")
            time.sleep(10)
    return False, out


def git_clone_or_fetch(repo, base_commit, workdir):
    workdir = Path(workdir)
    url = f"https://github.com/{repo}"
    if workdir.exists() and (workdir / ".git").exists():
        for lock in (workdir / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        ok, out = git_fetch_retry(workdir, base_commit, max_retries=3, timeout=300)
        if not ok:
            out2, rc2 = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
            if rc2 == 0:
                return True, f"fetch errored but checkout ok: {out[:80]}"
            return False, f"git fetch failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "existing workdir updated"
    else:
        workdir.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q"], cwd=workdir, timeout=30)
        run(["git", "remote", "add", "origin", url], cwd=workdir, timeout=30)
        ok, out = git_fetch_retry(workdir, base_commit, max_retries=3, timeout=300)
        if not ok:
            out2, rc2 = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
            if rc2 == 0:
                return True, f"fetch errored but checkout ok: {out[:80]}"
            return False, f"git fetch base_commit failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "init+shallow fetch"


def setup_rootfs(instance, rootfs_path):
    repo = instance["repo"]
    template = ROOTFS_TEMPLATES.get(repo)
    if not template or not Path(template).exists():
        return False, f"no rootfs template for {repo}"
    testbed = template / "testbed"
    if not testbed.exists():
        return False, f"template testbed missing: {testbed}"
    base_commit = instance["base_commit"]
    out, rc = run(["git", "cat-file", "-t", base_commit], cwd=testbed, timeout=10)
    if rc != 0 or "commit" not in out:
        import glob
        for tmp in glob.glob(str(testbed / ".git" / "objects" / "pack" / "tmp_*")):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        # Clean stale .lock files left by previous timed-out git fetches
        # (same pattern as git_clone_or_fetch; prevents "shallow.lock: File exists")
        for lock in (testbed / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        ok, out = git_fetch_retry(testbed, base_commit, max_retries=3, timeout=300)
        if not ok:
            return False, f"base_commit fetch failed: {out[:200]}"
    return True, f"using template {template.name}"


def run_harness_serial(harness, instance_json, workdir, predictions_out):
    """Run a single harness with quota backoff. Returns (ok, result_dict)."""
    cmd = [sys.executable, str(HERE / "run_single.py"),
           "--harness", harness, "--instance-json", str(instance_json),
           "--workdir", str(workdir), "--timeout", str(TIMEOUT_RUN),
           "--out-predictions", str(predictions_out),
           "--model-name", f"{harness}-{MODEL_NAME}"]
    for attempt in range(1, MAX_QUOTA_RETRIES + 1):
        t0 = time.time()
        out, rc = run(cmd, timeout=TIMEOUT_RUN + 120)
        wall = time.time() - t0
        wait = detect_quota_error(out)
        if wait and attempt < MAX_QUOTA_RETRIES:
            print(f"  [QUOTA] {harness}: quota exhausted, waiting {wait}s (retry {attempt+1}/{MAX_QUOTA_RETRIES})...")
            time.sleep(wait)
            continue
        return rc == 0, {"harness": harness, "returncode": rc, "wall_s": round(wall, 1),
                         "predictions_file": str(predictions_out), "stdout_tail": out[-500:],
                         "quota_blocked": wait is not None,
                         "quota_retry": attempt if attempt > 1 else None}
    return False, {"harness": harness, "returncode": rc, "wall_s": round(wall, 1),
                   "predictions_file": str(predictions_out), "stdout_tail": out[-500:],
                   "quota_blocked": True, "quota_exhausted": True}


def eval_instance(instance_id, predictions_file, rootfs_path, run_id):
    cmd = [sys.executable, str(HERE / "r1_eval.py"),
           "--instance", instance_id, "--predictions", str(predictions_file),
           "--rootfs", str(rootfs_path), "--run-id", run_id,
           "--log-dir", str(LOGS_EVAL), "--sandbox", "unshare", "--timeout", str(TIMEOUT_EVAL)]
    out, rc = run(cmd, timeout=TIMEOUT_EVAL + 120)
    (LOGS_EVAL / f"eval_{run_id}.log").write_text(out)
    result = {"eval_rc": rc}
    report_dir = LOGS_EVAL / run_id
    report_jsons = list(report_dir.rglob("report.json"))
    if report_jsons:
        try:
            report = json.loads(report_jsons[0].read_text())
            inst_report = report.get(instance_id, report) if isinstance(report, dict) else {}
            result["resolved"] = inst_report.get("resolved", False)
            result["patch_applied"] = inst_report.get("patch_successfully_applied", False)
            ts = inst_report.get("tests_status", {})
            f2p = ts.get("FAIL_TO_PASS", {})
            p2p = ts.get("PASS_TO_PASS", {})
            result["f2p_pass"] = len(f2p.get("success", []))
            result["f2p_total"] = len(f2p.get("success", [])) + len(f2p.get("failure", []))
            result["p2p_pass"] = len(p2p.get("success", []))
            result["p2p_total"] = len(p2p.get("success", [])) + len(p2p.get("failure", []))
        except Exception as e:
            result["report_error"] = str(e)
    return rc == 0, result


def classify_result(hres):
    """Classify: resolved / patch-but-failed / quota-blocked / no-patch / blocked."""
    if "blocked" in hres:
        return "blocked"
    hr = hres.get("harness_result", hres)
    if hr.get("quota_blocked"):
        return "quota-blocked"
    ev = hr.get("eval", {})
    if ev.get("resolved"):
        return "resolved"
    if ev.get("skipped"):
        return "no-patch"
    return "patch-but-failed"


def process_instance_for_harness(instance_id, harness, do_setup=True, do_run=True, do_eval=True):
    inst_json = INSTANCES_DIR / f"{instance_id}.json"
    if not inst_json.exists():
        return {"instance_id": instance_id, "harness": harness, "error": "instance JSON not found"}
    instance = json.loads(inst_json.read_text())
    results = {"instance_id": instance_id, "repo": instance["repo"],
               "harness": harness, "model": MODEL_NAME}
    workdir = WORKDIRS / instance["repo"].replace("/", "_")
    rootfs_path = ROOTFS_TEMPLATES.get(instance["repo"], ROOTFS_DIR / instance_id)

    if do_setup:
        print(f"\n{'='*60}\n[SETUP] {instance_id} for {harness}")
        ok, msg = git_clone_or_fetch(instance["repo"], instance["base_commit"], workdir)
        results["workdir_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = msg
            results["classification"] = "blocked"
            return results
        ok, msg = setup_rootfs(instance, rootfs_path)
        results["rootfs_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = f"rootfs: {msg}"
            results["classification"] = "blocked"
            return results

    if do_run:
        print(f"\n[RUN] {harness} on {instance_id} ...")
        pred_file = WORKDIRS / f"predictions_kimi_{harness.replace('-', '_')}_{instance_id}.json"
        ok, hres = run_harness_serial(harness, inst_json, workdir, pred_file)
        if do_eval:
            has_patch = pred_file.exists() and pred_file.stat().st_size > 50
            if has_patch:
                run_id = f"R1_KIMI_{harness.replace('-', '_').upper()}_{instance_id.replace('-', '_')}"
                print(f"  [EVAL] {harness} on {instance_id} ...")
                eok, eres = eval_instance(instance_id, pred_file, rootfs_path, run_id)
                hres["eval"] = eres
            else:
                hres["eval"] = {"skipped": "no patch produced"}
        results["harness_result"] = hres
        results["classification"] = classify_result(results)
    return results


def load_results():
    """Load results under a shared lock (concurrent-safe with save_results)."""
    import fcntl
    lock_path = SUMMARY_PATH.with_suffix(".lock")
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_SH)
        try:
            if SUMMARY_PATH.exists():
                try:
                    return json.loads(SUMMARY_PATH.read_text())
                except Exception:
                    return []
            return []
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def save_results(results, harness=None):
    """Read-merge-write under exclusive lock for concurrent multi-harness safety.

    When *harness* is given, only entries whose ``harness`` field matches are
    written to disk; entries for *other* harnesses are preserved from the
    on-disk copy (preventing a stale in-memory list from clobbering a
    concurrent process's newer results).
    """
    import fcntl
    lock_path = SUMMARY_PATH.with_suffix(".lock")
    with open(lock_path, "w") as lf:
        fcntl.flock(lf, fcntl.LOCK_EX)
        try:
            current = []
            if SUMMARY_PATH.exists():
                try:
                    current = json.loads(SUMMARY_PATH.read_text())
                except Exception:
                    current = []
            idx = {}
            for i, r in enumerate(current):
                idx[(r.get("instance_id"), r.get("harness"))] = i
            for r in results:
                if harness and r.get("harness") != harness:
                    continue
                key = (r.get("instance_id"), r.get("harness"))
                if key in idx:
                    current[idx[key]] = r
                else:
                    idx[key] = len(current)
                    current.append(r)
            SUMMARY_PATH.write_text(json.dumps(current, indent=2, default=str))
        finally:
            fcntl.flock(lf, fcntl.LOCK_UN)


def main():
    ap = argparse.ArgumentParser(description="Serial per-harness kimi cross-eval runner")
    ap.add_argument("--harness", required=True, choices=ALL_HARNESSES)
    ap.add_argument("--instances", nargs="+")
    ap.add_argument("--all-prepared", action="store_true")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--run-only", action="store_true")
    ap.add_argument("--eval-only", action="store_false", dest="do_eval")
    ap.add_argument("--resume", action="store_true")
    args = ap.parse_args()

    if args.all_prepared:
        instance_ids = sorted(f.stem for f in INSTANCES_DIR.glob("*.json"))
    elif args.instances:
        instance_ids = args.instances
    else:
        ap.error("Must specify --instances or --all-prepared")

    do_setup = not args.run_only
    do_run = not args.setup_only
    all_results = load_results()

    skip_ids = set()
    if args.resume:
        for r in all_results:
            if r.get("harness") == args.harness and r.get("classification") in (
                    "resolved", "patch-but-failed"):
                skip_ids.add(r["instance_id"])
        print(f"  [RESUME] Skipping {len(skip_ids)} completed for {args.harness}")

    pending = [iid for iid in instance_ids if iid not in skip_ids]
    print(f"Serial kimi eval: harness={args.harness} model={MODEL_NAME}")
    print(f"  Total={len(instance_ids)} Pending={len(pending)} Skip={len(skip_ids)} Concurrency=1")

    for idx, iid in enumerate(pending, 1):
        print(f"\n{'#'*60}\n# [{idx}/{len(pending)}] {args.harness} x {iid}\n{'#'*60}")
        res = process_instance_for_harness(iid, args.harness, do_setup, do_run, args.do_eval)
        found = False
        for i, r in enumerate(all_results):
            if r.get("instance_id") == iid and r.get("harness") == args.harness:
                all_results[i] = res
                found = True
                break
        if not found:
            all_results.append(res)
        save_results(all_results, harness=args.harness)
        cls = res.get("classification", "?")
        print(f"  => {iid} | {args.harness} | {cls}")

    print(f"\n{'='*60}\nSUMMARY: {args.harness} x {MODEL_NAME}\n{'='*60}")
    counts = {"resolved": 0, "patch-but-failed": 0, "quota-blocked": 0, "no-patch": 0, "blocked": 0}
    for r in all_results:
        if r.get("harness") != args.harness:
            continue
        cls = r.get("classification", "blocked")
        counts[cls] = counts.get(cls, 0) + 1
    total = sum(counts.values())
    for k, v in counts.items():
        if v > 0:
            print(f"  {k}: {v}/{total} ({100*v/max(total,1):.1f}%)")
    return 0


if __name__ == "__main__":
    sys.exit(main())