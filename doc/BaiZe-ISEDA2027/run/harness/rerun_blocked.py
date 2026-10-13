#!/usr/bin/env python3
"""P1-2: Re-run blocked(50) + no-patch(4) entries with precloned repos.

Uses /dev/shm/repos/ bare clones as local git origin to avoid GitHub 503 errors.
Runs the same 7 harnesses + kimi-k2.6-cloud model.
Excludes 14 quota-blocked entries (all django__django-16873, API quota issue).

Usage:
  HF_HUB_OFFLINE=1 python3 rerun_blocked.py [--harness cline-patched] [--resume] [--limit 5]
"""
from __future__ import annotations
import argparse, fcntl, json, os, subprocess, sys, time, traceback
from pathlib import Path
from collections import Counter, defaultdict

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("HF_DATASETS_OFFLINE", "1")

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from run_serial_kimi import (
    HARNESS_WORK, INSTANCES_DIR, WORKDIRS, ROOTFS_DIR, LOGS_EVAL,
    ROOTFS_TEMPLATES, ROOTFS_LOCK_PATH, ALL_HARNESSES,
    TIMEOUT_RUN, TIMEOUT_EVAL, PROXY, MODEL_NAME,
    run, git_fetch_retry, setup_rootfs, run_harness_serial,
    eval_instance, classify_result,
)

ORIG_JSON = HERE / "kimi_pilot_results.json"
RERUN_JSON = HERE / "kimi_pilot_results.rerun.json"
RERUN_LOGS = HARNESS_WORK / "logs_rerun_blocked"
PRECLONE_DIR = Path("/dev/shm/repos")


def _try_fetch_and_checkout(workdir, base_commit, origin_url, use_local):
    """Try fetch+checkout from given origin. Returns (ok, msg)."""
    timeout = 300 if use_local else 120
    ok, out = git_fetch_retry(workdir, base_commit, max_retries=3, timeout=timeout)
    if not ok:
        out2, rc2 = run(["git", "checkout", "-f", base_commit], cwd=workdir, timeout=60)
        if rc2 == 0: return True, f"fetch errored but checkout ok (local={use_local})"
        return False, f"fetch failed (local={use_local}): {out[:200]}"
    out, rc = run(["git", "checkout", "-f", base_commit], cwd=workdir, timeout=60)
    if rc != 0: return False, f"checkout failed: {out[:200]}"
    return True, f"ok (local={use_local})"


def git_clone_or_fetch_local(repo, base_commit, workdir):
    """Like git_clone_or_fetch but uses precloned bare repo as origin, with github fallback."""
    workdir = Path(workdir)
    repo_name = repo.split("/")[-1]
    local_bare = PRECLONE_DIR / repo_name
    github_url = f"https://github.com/{repo}"
    # Determine origin: local bare clone if available, else github
    if local_bare.exists() and (local_bare / "HEAD").exists():
        origin_url = str(local_bare)
        use_local = True
    else:
        origin_url = github_url
        use_local = False
    if workdir.exists() and (workdir / ".git").exists():
        for lock in (workdir / ".git").glob("*.lock"):
            try: lock.unlink()
            except OSError: pass
        run(["git", "remote", "set-url", "origin", origin_url], cwd=workdir, timeout=30)
        run(["git", "reset", "--hard", "HEAD"], cwd=workdir, timeout=60)
        run(["git", "clean", "-fd"], cwd=workdir, timeout=60)
        ok, msg = _try_fetch_and_checkout(workdir, base_commit, origin_url, use_local)
        if ok: return True, f"existing workdir updated ({msg})"
        # Fallback to github if local failed
        if use_local:
            run(["git", "remote", "set-url", "origin", github_url], cwd=workdir, timeout=30)
            ok2, msg2 = _try_fetch_and_checkout(workdir, base_commit, github_url, False)
            if ok2: return True, f"existing workdir via github fallback ({msg2})"
            return False, f"both local and github failed: local={msg}; github={msg2}"
        return False, msg
    else:
        workdir.mkdir(parents=True, exist_ok=True)
        run(["git", "init", "-q"], cwd=workdir, timeout=30)
        run(["git", "remote", "add", "origin", origin_url], cwd=workdir, timeout=30)
        ok, msg = _try_fetch_and_checkout(workdir, base_commit, origin_url, use_local)
        if ok: return True, f"init+fetch ({msg})"
        # Fallback to github if local failed
        if use_local:
            run(["git", "remote", "set-url", "origin", github_url], cwd=workdir, timeout=30)
            ok2, msg2 = _try_fetch_and_checkout(workdir, base_commit, github_url, False)
            if ok2: return True, f"init+fetch via github fallback ({msg2})"
            return False, f"both local and github failed: local={msg}; github={msg2}"
        return False, msg


def process_rerun_entry(instance_id, harness, instance, do_eval=True):
    """Re-run a single blocked/no-patch entry through harness + eval."""
    results = {"instance_id": instance_id, "repo": instance["repo"],
               "harness": harness, "model": MODEL_NAME, "rerun": True}
    workdir = WORKDIRS / "rerun" / harness / instance_id
    rootfs_path = ROOTFS_TEMPLATES.get(instance["repo"], ROOTFS_DIR / instance_id)
    # Step 1: Setup workdir with local precloned repo
    print(f"  [SETUP] {instance_id} for {harness}")
    ok, msg = git_clone_or_fetch_local(instance["repo"], instance["base_commit"], workdir)
    results["workdir_setup"] = {"ok": ok, "msg": msg}
    if not ok:
        results["blocked"] = msg
        results["classification"] = "blocked"
        return results
    # Step 2: Setup rootfs (shared template, needs flock)
    with open(ROOTFS_LOCK_PATH, "w") as lockf:
        fcntl.flock(lockf, fcntl.LOCK_EX)
        try: ok, msg = setup_rootfs(instance, rootfs_path)
        finally: fcntl.flock(lockf, fcntl.LOCK_UN)
    results["rootfs_setup"] = {"ok": ok, "msg": msg}
    if not ok:
        results["blocked"] = f"rootfs: {msg}"
        results["classification"] = "blocked"
        return results
    # Step 3: Run harness (agent generates patch)
    print(f"  [RUN] {harness} on {instance_id} ...")
    pred_file = WORKDIRS / "rerun" / f"predictions_{harness.replace('-', '_')}_{instance_id}.json"
    ok, hres = run_harness_serial(harness, INSTANCES_DIR / f"{instance_id}.json", workdir, pred_file)
    # Step 4: Eval patch
    if do_eval:
        has_patch = pred_file.exists() and pred_file.stat().st_size > 50
        if has_patch:
            run_id = f"RERUN_{harness.replace('-', '_').upper()}_{instance_id.replace('-', '_')}"
            print(f"  [EVAL] {harness} on {instance_id} ...")
            with open(ROOTFS_LOCK_PATH, "w") as lockf:
                fcntl.flock(lockf, fcntl.LOCK_EX)
                try: eok, eres = eval_instance(instance_id, pred_file, rootfs_path, run_id)
                finally: fcntl.flock(lockf, fcntl.LOCK_UN)
            hres["eval"] = eres
        else:
            hres["eval"] = {"skipped": "no patch produced"}
    results["harness_result"] = hres
    results["classification"] = classify_result(results)
    return results


def main():
    ap = argparse.ArgumentParser(description="Re-run blocked + no-patch entries (P1-2)")
    ap.add_argument("--harness", choices=ALL_HARNESSES, help="Only run this harness")
    ap.add_argument("--resume", action="store_true")
    ap.add_argument("--limit", type=int, help="Only run N entries")
    ap.add_argument("--no-eval", action="store_true")
    args = ap.parse_args()
    orig = json.loads(ORIG_JSON.read_text())
    targets = [x for x in orig if x.get("classification") in ("blocked", "no-patch")]
    blk = sum(1 for t in targets if t["classification"] == "blocked")
    nop = sum(1 for t in targets if t["classification"] == "no-patch")
    print(f"=== P1-2 RERUN: {len(targets)} entries (blocked={blk}, no-patch={nop}) ===")
    by_harness = defaultdict(list)
    for t in targets:
        by_harness[t["harness"]].append(t)
    for h in ALL_HARNESSES:
        if h in by_harness:
            print(f"  {h}: {len(by_harness[h])} entries")
    if args.harness:
        by_harness = {h: by_harness[h] for h in [args.harness] if h in by_harness}
        if not by_harness:
            print(f"No blocked/no-patch entries for harness={args.harness}")
            return
    existing = {}
    if args.resume and RERUN_JSON.exists():
        for r in json.loads(RERUN_JSON.read_text()):
            existing[(r.get("instance_id"), r.get("harness"))] = r
        print(f"  [RESUME] {len(existing)} entries already in rerun JSON")
    available = [d.name for d in PRECLONE_DIR.iterdir() if d.is_dir() and (d / "HEAD").exists()] if PRECLONE_DIR.exists() else []
    print(f"  [PRECLONE] Available: {available or 'NONE'}")
    RERUN_LOGS.mkdir(parents=True, exist_ok=True)
    new_results = []; done = 0; skipped = 0; failed = 0; resolved_new = 0
    t_start = time.time()
    for harness in ALL_HARNESSES:
        if harness not in by_harness: continue
        entries = by_harness[harness]
        if args.limit: entries = entries[:args.limit]
        for entry in entries:
            iid = entry["instance_id"]; key = (iid, harness)
            if args.resume and key in existing:
                skipped += 1; continue
            inst_json = INSTANCES_DIR / f"{iid}.json"
            if not inst_json.exists():
                print(f"  SKIP {iid} — not found"); failed += 1; continue
            instance = json.loads(inst_json.read_text())
            elapsed = time.time() - t_start
            eta = (elapsed / max(done, 1)) * (len(targets) - done - skipped) if done > 0 else 0
            print(f"\n{'='*60}\n  [{done+skipped+failed+1}/{len(targets)}] {harness} x {iid} (elapsed={elapsed:.0f}s eta={eta:.0f}s)")
            try:
                res = process_rerun_entry(iid, harness, instance, do_eval=not args.no_eval)
                new_results.append(res); done += 1
                cls = res.get("classification", "?")
                if cls == "resolved": resolved_new += 1
                print(f"  => {iid} | {harness} | {cls}")
            except Exception as e:
                print(f"  => ERROR: {e}"); traceback.print_exc(); failed += 1
                new_results.append({"instance_id": iid, "harness": harness, "error": str(e), "rerun": True})
            all_combined = list(existing.values()) + new_results
            with open(RERUN_JSON, "w") as f:
                json.dump(all_combined, f, indent=2, default=str)
    elapsed = time.time() - t_start
    print(f"\n{'='*60}\n=== P1-2 RERUN COMPLETE ===")
    print(f"  Done: {done}, Skipped: {skipped}, Failed: {failed}, Resolved: {resolved_new}")
    print(f"  Time: {elapsed:.0f}s ({elapsed/60:.1f}min)")
    print(f"  Results: {RERUN_JSON}")
    all_combined = list(existing.values()) + new_results
    counts = Counter()
    for r in all_combined:
        counts[(r.get("harness", "?"), r.get("classification", "?"))] += 1
    for (h, cls), n in sorted(counts.items()):
        print(f"    {h} | {cls}: {n}")


if __name__ == "__main__":
    main()
