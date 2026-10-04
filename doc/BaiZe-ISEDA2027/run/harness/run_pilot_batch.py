#!/usr/bin/env python3
"""Batch pilot runner — expand SWE-bench-Lite evaluation to 20-30 instances.

For each instance:
  1. Create a workdir (git clone repo @ base_commit) — needs GitHub.
  2. Create/reuse a rootfs (conda env + repo at base_commit) — needs PyPI.
  3. Run 4 harnesses (cline-patched, codex, opencode, claude-code).
  4. Evaluate each with r1_eval.py (unshare sandbox).
  5. Save results incrementally (per harness, per instance).

Usage:
  python3 run_pilot_batch.py --instances django__django-10924 django__django-11001
  python3 run_pilot_batch.py --all-prepared          # run all in instances/
  python3 run_pilot_batch.py --setup-only django__django-10924  # just workdir+rootfs

Honesty: blocked when GitHub/PyPI unreachable. Reports blocker, skips instance.
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_WORK = Path("/nas_train/app.e0031982/harness_work")
INSTANCES_DIR = HARNESS_WORK / "instances"
WORKDIRS = Path("/dev/shm/harness_work/workdirs")  # tmpfs: avoids NFS+git tmp_pack issues
ROOTFS_DIR = HARNESS_WORK / "rootfs"
LOGS_EVAL = HARNESS_WORK / "logs_eval"

ROOTFS_TEMPLATES = {
    "django/django": ROOTFS_DIR / "django__django-10914",
    "sympy/sympy": ROOTFS_DIR / "sympy__sympy-11400",
}
HARNESSES = ["cline-patched", "codex", "opencode", "claude-code"]
TIMEOUT_RUN = 1800
TIMEOUT_EVAL = 1800
PROXY = "http://172.19.92.25:13128"
INTER_RUN_DELAY = 10  # seconds between harness runs (spread quota usage)
MAX_QUOTA_RETRIES = 3  # max retries per harness on quota exhaustion


def detect_quota_error(output: str) -> int | None:
    """Parse '请等待X分钟Y秒后重试' / '请等待Y秒后重试' from harness output.

    Returns wait_seconds (int) or None if no quota error found.
    Also detects English variants like 'Too Many Requests'.
    """
    # Chinese: 本次Token额度已用完，请等待23分钟22秒后重试
    m = re.search(r"请等待(\d+)分钟(\d+)秒", output)
    if m:
        return int(m.group(1)) * 60 + int(m.group(2)) + 60  # +60s buffer
    m = re.search(r"请等待(\d+)秒", output)
    if m:
        return int(m.group(1)) + 60
    # English: Too Many Requests (without specific wait time)
    if "Too Many Requests" in output or "429" in output:
        return 300  # default 5min wait
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


def git_clone_or_fetch(repo, base_commit, workdir):
    """Shallow-init workdir + fetch only the base_commit (no full clone).

    Uses git init + git remote add + git fetch --depth=1 to avoid downloading
    the entire repo history (django repo is ~1GB; full clone is very slow
    via proxy).  Shared workdirs per repo are used (see process_instance).
    """
    workdir = Path(workdir)
    url = f"https://github.com/{repo}"
    if workdir.exists() and (workdir / ".git").exists():
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=workdir, timeout=120)
        if rc != 0:
            # NFS resilience: try checkout anyway (see new-branch comment above)
            out2, rc2 = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
            if rc2 == 0:
                return True, f"fetch errored but checkout succeeded (NFS race): {out[:100]}"
            return False, f"git fetch failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "existing workdir updated"
    else:
        workdir.mkdir(parents=True, exist_ok=True)
        out, rc = run(["git", "init", "-q"], cwd=workdir, timeout=30)
        if rc != 0:
            return False, f"git init failed: {out[:200]}"
        out, rc = run(["git", "remote", "add", "origin", url], cwd=workdir, timeout=30)
        if rc != 0:
            # remote might already exist
            run(["git", "remote", "set-url", "origin", url], cwd=workdir, timeout=30)
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=workdir, timeout=120)
        if rc != 0:
            # On NFS, git fetch can report errors (tmp_pack) while objects are
            # actually downloaded.  Try checkout anyway — if it works, we're fine.
            out2, rc2 = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
            if rc2 == 0:
                return True, f"fetch errored but checkout succeeded (NFS race): {out[:100]}"
            return False, f"git fetch base_commit failed: {out[:200]}"
        out, rc = run(["git", "checkout", base_commit], cwd=workdir, timeout=60)
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "init+shallow fetch"
        if rc != 0:
            return False, f"git checkout failed: {out[:200]}"
        return True, "cloned fresh"


def setup_rootfs(instance, rootfs_path):
    """Use the shared template rootfs directly (no cp -a).

    The template rootfs has the conda env + repo already set up.
    r1_eval.py does `git reset --hard <base_commit>` + `git clean -fdq`
    before applying each patch, so sharing is safe for sequential runs.
    """
    repo = instance["repo"]
    template = ROOTFS_TEMPLATES.get(repo)
    if not template or not Path(template).exists():
        return False, f"no rootfs template for {repo}"
    testbed = template / "testbed"
    if not testbed.exists():
        return False, f"template testbed missing: {testbed}"
    base_commit = instance["base_commit"]
    # Verify base_commit is available; fetch if needed (via proxy in run())
    out, rc = run(["git", "cat-file", "-t", base_commit], cwd=testbed, timeout=10)
    if rc != 0 or "commit" not in out:
        # Clean stale temp pack files that block git fetch
        import glob
        for tmp in glob.glob(str(testbed / ".git" / "objects" / "pack" / "tmp_*")):
            try:
                os.unlink(tmp)
            except OSError:
                pass
        out, rc = run(["git", "fetch", "--depth=1", "origin", base_commit], cwd=testbed, timeout=120)
        if rc != 0:
            return False, f"base_commit fetch failed: {out[:200]}"
    return True, f"using template {template.name} directly (shared rootfs)"


def run_harness(harness, instance_json, workdir, predictions_out):
    """Run a single harness with token-quota backoff retry.

    If the harness output contains '本次Token额度已用完' / '请等待X分钟Y秒后重试',
    sleep for the specified time + buffer, then retry (up to MAX_QUOTA_RETRIES).
    """
    cmd = [sys.executable, str(HERE / "run_single.py"),
           "--harness", harness, "--instance-json", str(instance_json),
           "--workdir", str(workdir), "--timeout", str(TIMEOUT_RUN),
           "--out-predictions", str(predictions_out)]
    for attempt in range(1, MAX_QUOTA_RETRIES + 1):
        t0 = time.time()
        out, rc = run(cmd, timeout=TIMEOUT_RUN + 120)
        wall = time.time() - t0
        # Check for token quota exhaustion
        wait = detect_quota_error(out)
        if wait and attempt < MAX_QUOTA_RETRIES:
            print(f"  [QUOTA] {harness}: token quota exhausted, waiting {wait}s before retry {attempt+1}/{MAX_QUOTA_RETRIES}...")
            time.sleep(wait)
            continue
        return rc == 0, {"harness": harness, "returncode": rc, "wall_s": round(wall, 1),
                         "predictions_file": str(predictions_out), "stdout_tail": out[-500:],
                         "quota_retry": attempt if attempt > 1 else None}
    # All retries exhausted
    return False, {"harness": harness, "returncode": rc, "wall_s": round(wall, 1),
                   "predictions_file": str(predictions_out), "stdout_tail": out[-500:],
                   "quota_exhausted": True}


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
            # report.json is nested: {"<instance_id>": {"resolved": bool, ...}}
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


def process_instance(instance_id, do_setup=True, do_run=True, do_eval=True, eval_only=False):
    inst_json = INSTANCES_DIR / f"{instance_id}.json"
    if not inst_json.exists():
        return {"instance_id": instance_id, "error": "instance JSON not found"}
    instance = json.loads(inst_json.read_text())
    results = {"instance_id": instance_id, "repo": instance["repo"], "version": instance.get("version", "")}
    # Use shared workdir per repo (not per instance) — run_single.py does git reset --hard before/after
    workdir = WORKDIRS / instance["repo"].replace("/", "_")
    # Use shared template rootfs (not per-instance copy) for eval
    rootfs_path = ROOTFS_TEMPLATES.get(instance["repo"], ROOTFS_DIR / instance_id)
    if eval_only:
        # Eval-only mode: skip setup/run, just re-evaluate existing predictions
        harness_results = {}
        for harness in HARNESSES:
            pred_file = WORKDIRS / f"predictions_{harness.replace('-', '_')}_{instance_id}.json"
            if not pred_file.exists() or pred_file.stat().st_size < 50:
                print(f"  [SKIP] {harness} on {instance_id}: no predictions file")
                harness_results[harness] = {"harness": harness, "eval": {"skipped": "no predictions"}}
                continue
            run_id = f"R1_PILOT_{harness.replace('-', '_').upper()}_{instance_id.replace('-', '_')}"
            print(f"  [EVAL] {harness} on {instance_id} ...")
            eok, eres = eval_instance(instance_id, pred_file, rootfs_path, run_id)
            harness_results[harness] = {"harness": harness, "predictions_file": str(pred_file), "eval": eres}
        results["harnesses"] = harness_results
        return results
    if do_setup:
        print(f"\n{'='*60}\n[SETUP] {instance_id}")
        ok, msg = git_clone_or_fetch(instance["repo"], instance["base_commit"], workdir)
        results["workdir_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = msg
            return results
        ok, msg = setup_rootfs(instance, rootfs_path)
        results["rootfs_setup"] = {"ok": ok, "msg": msg}
        if not ok:
            results["blocked"] = f"rootfs: {msg}"
            return results
    if do_run:
        harness_results = {}
        for i, harness in enumerate(HARNESSES):
            if i > 0:
                print(f"  [DELAY] {INTER_RUN_DELAY}s between runs...")
                time.sleep(INTER_RUN_DELAY)
            print(f"\n[RUN] {harness} on {instance_id} ...")
            pred_file = WORKDIRS / f"predictions_{harness.replace('-', '_')}_{instance_id}.json"
            ok, hres = run_harness(harness, inst_json, workdir, pred_file)
            # Run eval if predictions file has content (not just rc==0,
            # because some harnesses produce patches even with rc=1)
            if do_eval:
                has_patch = pred_file.exists() and pred_file.stat().st_size > 50
                if has_patch:
                    run_id = f"R1_PILOT_{harness.replace('-', '_').upper()}_{instance_id.replace('-', '_')}"
                    eok, eres = eval_instance(instance_id, pred_file, rootfs_path, run_id)
                    hres["eval"] = eres
                else:
                    hres["eval"] = {"skipped": "no patch produced"}
            harness_results[harness] = hres
        results["harnesses"] = harness_results
    return results


def main():
    ap = argparse.ArgumentParser(description="Batch pilot runner for SWE-bench Lite")
    ap.add_argument("--instances", nargs="+")
    ap.add_argument("--all-prepared", action="store_true")
    ap.add_argument("--setup-only", action="store_true")
    ap.add_argument("--run-only", action="store_true")
    ap.add_argument("--eval-only", action="store_true",
                    help="Skip setup/run, just re-evaluate existing predictions")
    ap.add_argument("--resume", action="store_true",
                    help="Skip instances already in out-summary with all 4 harnesses evaluated")
    ap.add_argument("--out-summary", default=None)
    args = ap.parse_args()
    if args.all_prepared:
        instance_ids = [f.stem for f in sorted(INSTANCES_DIR.glob("*.json"))]
    elif args.instances:
        instance_ids = args.instances
    else:
        ap.error("Must specify --instances or --all-prepared")

    summary_path = Path(args.out_summary or HARNESS_WORK / "pilot_results.json")
    eval_only = args.eval_only
    do_setup = not args.run_only and not eval_only
    do_run = not args.setup_only and not eval_only
    do_eval = not args.setup_only
    print(f"Pilot batch: {len(instance_ids)} instances, setup={do_setup}, run={do_run}, eval={do_eval}, eval_only={eval_only}")

    # Resume: load existing results and skip/update completed instances
    all_results = []
    existing_map = {}  # instance_id -> index in all_results
    skip_ids = set()
    if (args.resume or eval_only) and summary_path.exists():
        try:
            all_results = json.loads(summary_path.read_text())
            for idx, res in enumerate(all_results):
                existing_map[res["instance_id"]] = idx
                if args.resume:
                    hs = res.get("harnesses", {})
                    if len(hs) >= len(HARNESSES):
                        all_evald = all(
                            h.get("eval", {}).get("resolved") is not None
                            or h.get("eval", {}).get("skipped")
                            for h in hs.values()
                        )
                        if all_evald:
                            skip_ids.add(res["instance_id"])
            if args.resume:
                print(f"  [RESUME] Skipping {len(skip_ids)} already-completed instances")
        except Exception as e:
            print(f"  [RESUME] Could not load existing results: {e}")

    pending = [iid for iid in instance_ids if iid not in skip_ids]
    print(f"  Pending: {len(pending)} instances")

    for iid in pending:
        res = process_instance(iid, do_setup, do_run, do_eval, eval_only=eval_only)
        if iid in existing_map:
            all_results[existing_map[iid]] = res  # update existing entry
        else:
            all_results.append(res)
        summary_path.write_text(json.dumps(all_results, indent=2, default=str))
    print(f"\n{'='*80}\nPILOT SUMMARY\n{'='*80}")
    for res in all_results:
        iid = res["instance_id"]
        if "blocked" in res:
            print(f"  {iid}: BLOCKED - {res['blocked'][:60]}")
            continue
        for h, hres in res.get("harnesses", {}).items():
            resolved = hres.get("eval", {}).get("resolved", "N/A")
            print(f"  {iid} | {h} | resolved={resolved} | wall={hres.get('wall_s', '?')}s")
    return 0

if __name__ == "__main__":
    sys.exit(main())
