#!/usr/bin/env python3
"""SWE-bench Verified full-500 orchestrator (R548, 2026-10-28).

Operator directive (2026-10-28 07:1x): "跑完整的 SWE-bench Verified 全量 500 题".
  * Gate  : 10 problems x 7 harnesses (usability gate before full run)
  * Full  : 500 problems x passing harnesses

Reuses PROVEN pilot infrastructure (run_single.py predict + swebench v5.0.2
docker eval) with improvements per operator directive:
  1. git fetch timeout fix: partial clone (--filter=blob:none) + 1800s timeout
  2. Checkpoint resume: skip instances with existing valid predictions
  3. Progress file: progress_{harness}.json updated after each instance
  4. Infra failures classified separately, not counted as model failure
  5. All 7 harnesses supported

Report naming: write "cline" (not "cline-patched") per naming convention.
"""
from __future__ import annotations
import argparse, json, os, subprocess, sys, time, threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
RUN_SINGLE = HARNESS_DIR / "run_single.py"
ENRICHED = HERE / "enriched_500.json"
IDS_FILE = HERE / "verified_500_ids.txt"
# Env-var overrides for multi-model support (backward-compatible defaults).
# 2026-11-07 audit: default changed kimi-k2.6-cloud → glm-5.3-flash.
MODEL_SUFFIX = os.environ.get("MODEL_SUFFIX", "glm-5.3-flash")
RUN_ID_PREFIX = os.environ.get("RUN_ID_PREFIX", "verified_full")
EVAL_TAG = os.environ.get("EVAL_TAG", "")          # e.g. "glm53_" → eval_glm53_<h>.json
PRED_SUBDIR = os.environ.get("PRED_SUBDIR", "predictions")
WORKDIR_TAG = os.environ.get("WORKDIR_TAG", "")     # e.g. "_glm53" → separate workdirs
PRED_DIR = HERE / PRED_SUBDIR
REPORT_DIR = HERE / "reports"
LOG_DIR = HERE / "logs"
INSTANCE_DIR = HERE / "instances"
WORKDIRS = Path(f"/dev/shm/harness_verified_full{WORKDIR_TAG}/workdirs")
PROXY = "http://172.19.92.25:13128"
TIMEOUT_RUN = 1800
TIMEOUT_EVAL = 1800
EVAL_LOG_ROOT = HERE / "logs" / "run_evaluation"

ALL_HARNESSES = [
    "cline-patched", "codex", "opencode", "pi",
    "claude-code", "hermes", "deepseek-harness", "zhulong",
]
DISPLAY = {"cline-patched": "cline"}


def disp(h: str) -> str:
    return DISPLAY.get(h, h)


def log(msg: str):
    print(f"[verified-full {time.strftime('%H:%M:%S')}] {msg}", flush=True)


# ---------------------------------------------------------------------------
# Parallel-predict helpers (2026-11-24: parallelize PREDICT, 429 adaptive backoff)
# ---------------------------------------------------------------------------
DATA_DIRS = Path(f"/dev/shm/harness_verified_full{WORKDIR_TAG}/cline_data")

_repo_locks: dict[str, threading.Lock] = {}
_repo_locks_guard = threading.Lock()


def _get_repo_lock(repo: str) -> threading.Lock:
    """Serialize same-repo instances sharing one git workdir (checkout/reset race)."""
    with _repo_locks_guard:
        lk = _repo_locks.get(repo)
        if lk is None:
            lk = threading.Lock()
            _repo_locks[repo] = lk
        return lk


class AdaptiveConcurrency:
    """429-aware slot limiter: start at cap, halve on 429 (floor), ramp +1 per clean window.

    Ladder per user directive (2026-11-24): 8 -> 4 -> 2 on 429; recover +1 after a
    clean window (default 15 min) up to cap.
    """
    def __init__(self, cap: int, floor: int = 2, ramp_clean_s: float = 900.0):
        self.cap = max(floor, cap)
        self.floor = floor
        self.limit = self.cap
        self._cv = threading.Condition()
        self._active = 0
        self._last_429 = None
        self._last_change = time.time()
        self.ramp_clean_s = ramp_clean_s

    def acquire(self):
        with self._cv:
            while self._active >= self.limit:
                self._cv.wait(timeout=5.0)
            self._active += 1

    def release(self, rate_limited: bool = False):
        with self._cv:
            self._active -= 1
            if rate_limited:
                self._last_429 = time.time()
                self._last_change = time.time()
                new = max(self.floor, self.limit // 2)
                if new != self.limit:
                    log(f"  [adaptive] 429 -> concurrency {self.limit} -> {new}")
                    self.limit = new
            else:
                self._maybe_ramp()
            self._cv.notify_all()

    def _maybe_ramp(self):
        if self.limit >= self.cap or self._last_429 is None:
            return
        if time.time() - self._last_429 < self.ramp_clean_s:
            return
        if time.time() - self._last_change < self.ramp_clean_s:
            return
        self.limit += 1
        self._last_change = time.time()
        log(f"  [adaptive] clean ramp -> concurrency {self.limit}")


def load_ids(max_n: int | None, offset: int = 0, ids_file: Path | None = None) -> list[str]:
    src = ids_file or IDS_FILE
    ids = src.read_text().split()
    if max_n:
        ids = ids[offset:offset + max_n]
    return ids


def load_instances() -> dict[str, dict]:
    rows = json.loads(ENRICHED.read_text())
    return {r["instance_id"]: r for r in rows}


def ensure_instance_json(iid: str, insts: dict[str, dict]):
    """Write minimal per-instance JSON (for run_single.py predict phase)."""
    f = INSTANCE_DIR / f"{iid}.json"
    if f.exists() and f.stat().st_size > 30:
        return
    inst = insts[iid]
    minimal = {
        "instance_id": inst["instance_id"],
        "repo": inst["repo"],
        "base_commit": inst["base_commit"],
        "problem_statement": inst["problem_statement"],
    }
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    f.write_text(json.dumps(minimal, ensure_ascii=False))


def run(cmd, cwd=None, timeout=300, with_proxy=True, extra_env=None):
    """Run subprocess with proxy control (mirrors pilot's run())."""
    e = os.environ.copy()
    if with_proxy:
        e.setdefault("https_proxy", PROXY)
        e.setdefault("http_proxy", PROXY)
        e.setdefault("no_proxy", "127.0.0.1,localhost")
    else:
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY",
                  "all_proxy", "ALL_PROXY"):
            e.pop(k, None)
        e["no_proxy"] = "*"
        e["NO_PROXY"] = "*"
    if extra_env:
        e.update(extra_env)
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       timeout=timeout, env=e)
    return p.stdout, p.stderr, p.returncode


def git_clone_or_fetch(repo: str, base_commit: str, workdir: Path) -> tuple[bool, str]:
    """Shallow fetch of base_commit ONLY (PROVEN pilot logic, run_pilot_batch.py).

    R548 root-cause (2026-10-28): the previous impl fell back to a FULL
    `git fetch origin` when the shallow fetch failed — for astropy (huge repo)
    that downloads gigabytes of history through the proxy, and with 6 harnesses
    doing it concurrently the first fetch timed out, leaving a broken workdir
    that all 9 subsequent same-repo instances silently reused ("existing
    workdir updated" -> 0 agents ran).  Fix: NO full-fetch fallback; shallow
    fetch only; NFS-race resilient (try checkout even if fetch reports a
    tmp_pack error, because on NFS objects may actually be downloaded); clean
    stale lock files from previous failed fetches.
    """
    url = f"https://github.com/{repo}.git"
    if (workdir / ".git").exists():
        # Clean stale lock files from previous failed fetches
        for lock in (workdir / ".git").glob("*.lock"):
            try:
                lock.unlink()
            except OSError:
                pass
        # Check if commit already local (common: same repo reused across instances)
        _, _, rc_chk = run(["git", "cat-file", "-e", f"{base_commit}^{{commit}}"],
                           workdir, timeout=30, with_proxy=False)
        if rc_chk != 0:
            _, _, rc_f = run(["git", "fetch", "--depth=1", "origin", base_commit],
                             workdir, timeout=1800)
            if rc_f != 0:
                # NFS resilience: try checkout anyway (fetch may report tmp_pack
                # error while objects are actually downloaded)
                _, _, rc_co = run(["git", "checkout", "-f", base_commit],
                                  workdir, timeout=120)
                if rc_co == 0:
                    return True, "fetch errored but checkout succeeded (NFS race)"
                return False, "git fetch base_commit failed (shallow)"
        _, _, rc2 = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
        return rc2 == 0, "existing workdir updated"
    workdir.mkdir(parents=True, exist_ok=True)
    run(["git", "init", "-q"], workdir, timeout=30, with_proxy=False)
    run(["git", "remote", "add", "origin", url], workdir, timeout=30, with_proxy=False)
    _, _, rc = run(["git", "fetch", "--depth=1", "origin", base_commit],
                   workdir, timeout=1800)
    if rc != 0:
        # NFS resilience: try checkout anyway
        _, _, rc_co = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
        if rc_co == 0:
            return True, "fetch errored but checkout succeeded (NFS race)"
        return False, "git fetch base_commit failed (shallow)"
    _, _, rc = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
    return rc == 0, "init+shallow fetch"


def predict_one(harness: str, inst: dict, workdir: Path, data_dir: Path | None = None) -> dict:
    iid = inst["instance_id"]
    bc = inst["base_commit"]
    extra_env = None
    if data_dir is not None:
        data_dir.mkdir(parents=True, exist_ok=True)
        extra_env = {"CLINE_DATA_DIR": str(data_dir)}
    try:
        ok, msg = git_clone_or_fetch(inst["repo"], bc, workdir)
    except subprocess.TimeoutExpired:
        return {"instance_id": iid, "harness": harness, "blocked": "git-fetch-timeout",
                "classification": "infra", "model_patch_len": 0}
    if not ok:
        return {"instance_id": iid, "harness": harness, "blocked": msg,
                "classification": "blocked", "model_patch_len": 0}
    inst_json = INSTANCE_DIR / f"{iid}.json"
    pred_out = PRED_DIR / f"{harness}__{iid}.json"
    cmd = [sys.executable, str(RUN_SINGLE), "--harness", harness,
           "--instance-json", str(inst_json), "--workdir", str(workdir),
           "--base-commit", bc, "--timeout", str(TIMEOUT_RUN),
           "--out-predictions", str(pred_out),
           "--model-name", f"{disp(harness)}-{MODEL_SUFFIX}"]
    t0 = time.time()
    timed_out = False
    try:
        out, err, rc = run(cmd, workdir, timeout=TIMEOUT_RUN + 120,
                           with_proxy=False, extra_env=extra_env)
    except subprocess.TimeoutExpired:
        out, err, rc = f"[agent TIMEOUT after {TIMEOUT_RUN + 120}s]", "", -1
        timed_out = True
    wall = time.time() - t0
    patch_len = 0
    if pred_out.exists():
        try:
            preds = json.loads(pred_out.read_text())
            if preds:
                patch_len = len(preds[0].get("model_patch", ""))
        except Exception:
            pass

    # Fix #3 (2026-11-04 per trace analysis): retry on silent exit.
    # cline CLI can exit rc=0 in ~1-2s with empty patch when it hits an
    # API error or startup crash it swallows.  Re-running once often succeeds
    # because gw_proxy re-establishes the connection.  Only retry when:
    #   rc == 0  (not a crash/timeout)
    #   patch_len == 0  (no patch produced)
    #   wall < 10  (silent exit, not a long run that simply failed)
    #   not timed_out  (don't retry actual timeouts)
    retried = False
    if rc == 0 and patch_len == 0 and wall < 10 and not timed_out:
        log(f"  -> silent exit (rc=0, patch=0, wall={wall:.1f}s), retrying once...")
        retried = True
        if pred_out.exists():
            try:
                pred_out.unlink()
            except OSError:
                pass
        t0r = time.time()
        try:
            out, err, rc = run(cmd, workdir, timeout=TIMEOUT_RUN + 120,
                               with_proxy=False, extra_env=extra_env)
        except subprocess.TimeoutExpired:
            out, err, rc = f"[agent TIMEOUT after {TIMEOUT_RUN + 120}s]", "", -1
            timed_out = True
        wall = time.time() - t0r
        patch_len = 0
        if pred_out.exists():
            try:
                preds = json.loads(pred_out.read_text())
                if preds:
                    patch_len = len(preds[0].get("model_patch", ""))
            except Exception:
                pass

    blocked = ("quota" in out.lower() or "429" in out or "forbidden" in out.lower())
    rate_limited = ("429" in out or "rate limit" in out.lower()
                    or "too many" in out.lower())
    input_tokens = output_tokens = None
    if pred_out.exists():
        try:
            preds = json.loads(pred_out.read_text())
            if preds:
                u = preds[0].get("usage", {}) or {}
                if isinstance(u.get("input_tokens"), (int, float)):
                    input_tokens = int(u["input_tokens"])
                if isinstance(u.get("output_tokens"), (int, float)):
                    output_tokens = int(u["output_tokens"])
        except Exception:
            pass
    return {"instance_id": iid, "harness": harness, "returncode": rc,
            "wall_s": round(wall, 1), "model_patch_len": patch_len,
            "quota_blocked": blocked, "rate_limited": rate_limited,
            "input_tokens": input_tokens, "output_tokens": output_tokens,
            "timeout": timed_out,
            "retried": retried,
            "stdout_tail": out[-400:], "stderr_tail": err[-400:] if err else "",
            "predictions_file": str(pred_out)}


def is_predicted(harness: str, iid: str) -> bool:
    """Check if instance already has a valid prediction (checkpoint resume)."""
    f = PRED_DIR / f"{harness}__{iid}.json"
    if not f.exists() or f.stat().st_size < 30:
        return False
    try:
        preds = json.loads(f.read_text())
        return bool(preds) and bool(preds[0].get("model_patch", "").strip())
    except Exception:
        return False


def write_progress(harness: str, results: list[dict], total: int):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    done = len(results)
    patches = sum(1 for r in results if r.get("model_patch_len", 0) > 0)
    infra = sum(1 for r in results if r.get("classification") in ("infra", "blocked"))
    timeouts = sum(1 for r in results if r.get("timeout"))
    quota = sum(1 for r in results if r.get("quota_blocked"))
    progress = {
        "harness": disp(harness), "harness_code": harness,
        "done": done, "total": total,
        "patch_produced": patches, "infra": infra,
        "timeout": timeouts, "quota_blocked": quota,
        "no_patch": done - patches - infra - timeouts - quota,
        "last_update": time.strftime("%Y-%m-%d %H:%M:%S"),
        "results": results,
    }
    (REPORT_DIR / f"progress_{EVAL_TAG}{harness}.json").write_text(
        json.dumps(progress, indent=2, ensure_ascii=False))


def merge_predictions(harness: str, ids: list[str]) -> Path:
    merged = PRED_DIR / f"predictions_{harness}.json"
    all_preds = []
    for iid in ids:
        f = PRED_DIR / f"{harness}__{iid}.json"
        if f.exists() and f.stat().st_size > 30:
            try:
                preds = json.loads(f.read_text())
                preds = [p for p in preds if p.get("model_patch", "").strip()]
                all_preds.extend(preds)
            except Exception:
                pass
    merged.write_text(json.dumps(all_preds, indent=2))
    log(f"merged {len(all_preds)}/{len(ids)} predictions -> {merged}")
    return merged


def _record_result(harness: str, results: list[dict], r: dict):
    cls = ("infra" if r.get("classification") == "infra"
           else "blocked" if r.get("classification") == "blocked"
           else "timeout" if r.get("timeout")
           else "quota-blocked" if r.get("quota_blocked")
           else "no-patch" if r["model_patch_len"] == 0
           else "patch-produced")
    r["classification"] = cls
    log(f"  -> {cls} (patch={r['model_patch_len']}B wall={r.get('wall_s')}s)")
    idx = next((j for j, rr in enumerate(results) if rr["instance_id"] == r["instance_id"]), None)
    if idx is not None:
        results[idx] = r
    else:
        results.append(r)


def phase_predict(harness: str, ids: list[str], insts: dict[str, dict],
                  workers: int = 1) -> list[dict]:
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    results = []
    prog_file = REPORT_DIR / f"progress_{EVAL_TAG}{harness}.json"
    if prog_file.exists():
        try:
            old = json.loads(prog_file.read_text())
            results = old.get("results", [])
            log(f"resume: loaded {len(results)} existing results")
        except Exception:
            pass

    pending = []
    for i, iid in enumerate(ids):
        if is_predicted(harness, iid):
            existing = next((r for r in results if r["instance_id"] == iid), None)
            if existing:
                log(f"[{i+1}/{len(ids)}] {iid} SKIP (predicted, patch={existing.get('model_patch_len',0)}B)")
            else:
                log(f"[{i+1}/{len(ids)}] {iid} SKIP (prediction file exists)")
                results.append({"instance_id": iid, "harness": harness,
                                "classification": "resumed", "model_patch_len": 1})
                write_progress(harness, results, len(ids))
        else:
            pending.append(iid)

    if not pending:
        (REPORT_DIR / f"predict_{EVAL_TAG}{harness}.json").write_text(json.dumps(results, indent=2))
        merge_predictions(harness, ids)
        return results

    parallel = workers > 1
    pool = AdaptiveConcurrency(cap=workers) if parallel else None
    log(f"predict {harness}: workers={workers} pending={len(pending)} "
        f"({'parallel' if parallel else 'serial'})")

    def _worker(iid):
        inst = insts[iid]
        with _get_repo_lock(inst["repo"]):
            ensure_instance_json(iid, insts)
            workdir = WORKDIRS / harness / inst["repo"].replace("/", "_")
            data_dir = DATA_DIRS / f"{harness}__{iid}" if parallel else None
            if parallel:
                pool.acquire()
            r = None
            try:
                r = predict_one(harness, inst, workdir, data_dir=data_dir)
            finally:
                if parallel:
                    pool.release(rate_limited=bool(r) and bool(r.get("rate_limited", False)))
        return r

    if parallel:
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {ex.submit(_worker, iid): iid for iid in pending}
            for fut in as_completed(futs):
                r = fut.result()
                _record_result(harness, results, r)
                write_progress(harness, results, len(ids))
    else:
        for iid in pending:
            r = _worker(iid)
            _record_result(harness, results, r)
            write_progress(harness, results, len(ids))

    (REPORT_DIR / f"predict_{EVAL_TAG}{harness}.json").write_text(json.dumps(results, indent=2))
    merge_predictions(harness, ids)
    return results


def phase_eval(harness: str, ids: list[str]) -> dict:
    merged = PRED_DIR / f"predictions_{harness}.json"
    if not merged.exists():
        log(f"no merged predictions for {harness}; run predict first")
        return {"error": "no predictions"}
    preds = json.loads(merged.read_text())
    pred_ids = [p["instance_id"] for p in preds if p.get("model_patch", "").strip()]
    eval_ids = [i for i in ids if i in pred_ids]
    if not eval_ids:
        log(f"no patches to eval for {harness}")
        return {"error": "no patches", "eval_ids": []}

    run_id = f"{RUN_ID_PREFIX}_{harness}"
    max_workers = int(os.environ.get("EVAL_MAX_WORKERS", "8"))
    cmd = (f"python3 -m swebench.harness.run_evaluation "
           f"--predictions_path {merged} --dataset_name {ENRICHED} --split test "
           f"--instance_ids {' '.join(eval_ids)} --max_workers {max_workers} "
           f"--run_id {run_id} --timeout {TIMEOUT_EVAL}")
    log(f"EVAL {disp(harness)} on {len(eval_ids)} instances (workers={max_workers})")
    EVAL_LOG_ROOT.mkdir(parents=True, exist_ok=True)
    logf = LOG_DIR / f"eval_{run_id}.log"
    proc = subprocess.run(["sg", "docker", "-c", cmd], cwd=str(HERE),
                          capture_output=True, text=True,
                          timeout=TIMEOUT_EVAL * len(eval_ids) + 600)
    logf.write_text(proc.stdout + "\n[stderr]\n" + proc.stderr)
    log(f"  eval finished rc={proc.returncode}; log -> {logf}")
    return parse_eval(run_id, eval_ids, harness)


def parse_eval(run_id: str, eval_ids: list[str], harness: str) -> dict:
    model = f"{disp(harness)}-{MODEL_SUFFIX}"
    summary = {"harness": disp(harness), "harness_code": harness, "run_id": run_id,
               "n": len(eval_ids), "resolved": [], "failed": [], "infra_or_quota": []}
    for iid in eval_ids:
        rj = EVAL_LOG_ROOT / run_id / model / iid / "report.json"
        if not rj.exists():
            cands = list((EVAL_LOG_ROOT / run_id).glob(f"*/{iid}/report.json"))
            rj = cands[0] if cands else None
        if rj is None or not rj.exists():
            summary["infra_or_quota"].append(iid)
            continue
        try:
            rep = json.loads(rj.read_text())
            inst_rep = rep.get(iid, rep) if isinstance(rep, dict) else {}
            resolved = inst_rep.get("resolved", False)
            (summary["resolved"] if resolved else summary["failed"]).append(iid)
        except Exception as e:
            summary["infra_or_quota"].append(f"{iid}({e})")
    (REPORT_DIR / f"eval_{EVAL_TAG}{harness}.json").write_text(json.dumps(summary, indent=2))
    log(f"  resolved={len(summary['resolved'])} failed={len(summary['failed'])} "
        f"infra={len(summary['infra_or_quota'])}")
    return summary


def main():
    ap = argparse.ArgumentParser(description="SWE-bench Verified full-500 orchestrator")
    ap.add_argument("phase", choices=["predict", "eval", "report", "gate", "all"])
    ap.add_argument("--harness", required=True, choices=ALL_HARNESSES)
    ap.add_argument("--max", type=int, default=None, help="cap #instances (gate=10, full=500)")
    ap.add_argument("--offset", type=int, default=0, help="skip first N instances")
    ap.add_argument("--ids-file", default=None, help="custom instance-id list (e.g. gate_10_ids.txt)")
    ap.add_argument("--workers", type=int,
                    default=int(os.environ.get("PREDICT_WORKERS", "1")),
                    help="predict concurrency (>=2 enables parallel + 429 backoff)")
    args = ap.parse_args()

    ids_file = Path(args.ids_file) if args.ids_file else None
    max_n = args.max or (10 if args.phase == "gate" else None)
    ids = load_ids(max_n, args.offset, ids_file)
    insts = load_instances()

    if args.phase in ("predict", "gate", "all"):
        phase_predict(args.harness, ids, insts, workers=args.workers)
    if args.phase in ("eval", "gate", "all"):
        phase_eval(args.harness, ids)
    if args.phase in ("report", "gate"):
        pred_f = REPORT_DIR / f"predict_{EVAL_TAG}{args.harness}.json"
        ev_f = REPORT_DIR / f"eval_{EVAL_TAG}{args.harness}.json"
        pred = json.loads(pred_f.read_text()) if pred_f.exists() else []
        ev = json.loads(ev_f.read_text()) if ev_f.exists() else {}
        resolved = len(ev.get("resolved", []))
        no_patch = sum(1 for r in pred if r.get("model_patch_len", 0) == 0
                       and r.get("classification") not in ("infra", "blocked", "resumed"))
        patch_produced = sum(1 for r in pred if r.get("model_patch_len", 0) > 0)
        passed = resolved >= 1 and no_patch <= 2
        print(f"\n{'='*60}")
        print(f"RESULT: {disp(args.harness)} (n={len(ids)})")
        print(f"  resolved={resolved}  failed={len(ev.get('failed',[]))}  "
              f"infra={len(ev.get('infra_or_quota',[]))}")
        print(f"  patch_produced={patch_produced}  no_patch={no_patch}")
        if args.phase == "gate":
            print(f"  GATE: {'PASS' if passed else 'FAIL'} "
                  f"(criteria: resolved>=1 AND no_patch<=2)")
        print(f"{'='*60}")


if __name__ == "__main__":
    main()
