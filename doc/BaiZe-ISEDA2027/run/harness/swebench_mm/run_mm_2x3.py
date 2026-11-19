#!/usr/bin/env python3
"""SWE-bench Multimodal 2×3 evaluation orchestrator (user order 2026-11-19).

6 routes: 2 harnesses (cline, opencode) × 3 LLMs (DeepSeek-V4-flash, Kimi-K2.6, Doubao)

Predict phase:
  - cline routes: images embedded as markdown base64 in prompt text → mm_proxy
    converts to OpenAI image_url content parts before forwarding to gateway.
  - opencode routes: images passed via -f flag (native multimodal support).
  - Each route connects to its own gateway URL with its own API key.

Eval phase:
  - swebench.harness.run_evaluation with MM dataset (Docker containers).

Usage:
  python3 run_mm_2x3.py predict --route cline__kimi-k2.6 [--max-n 5]
  python3 run_mm_2x3.py predict --all [--max-n 5]
  python3 run_mm_2x3.py eval --route cline__kimi-k2.6
  python3 run_mm_2x3.py smoke --route cline__kimi-k2.6   # 1 instance smoke test
"""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, time, signal
from pathlib import Path
from urllib.parse import urlparse

HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent
CONFIG_PATH = HERE / "mm_2x3_config.json"
INSTANCE_DIR = HERE / "instances"
PRED_DIR = HERE / "predictions_2x3"
PROGRESS_DIR = HERE / "progress_2x3"
IMAGE_CACHE = HERE / "images"
WORKDIR_BASE = Path("/dev/shm/harness_mm_2x3/workdirs")
LOG_DIR = HERE / "logs_2x3"
DATASET_JSON = HERE / "mm_test.json"

CLINE_BIN = shutil.which("cline") or "/home/app.e0031982/.bun/bin/cline"
OPENCODE_BIN = shutil.which("opencode") or "/home/app.e0031982/.local/bin/opencode"
OPENCODE_CONFIG = Path.home() / ".config" / "opencode" / "opencode.json"
PROXY = "http://172.19.92.25:13128"
TIMEOUT_RUN = 1800
TIMEOUT_GIT = 1800
MM_PROXY_BASE_PORT = 9095

sys.path.insert(0, str(HERE))
from mm_image_handler import ImageHandler


def log(msg: str):
    print(f"[mm_2x3 {time.strftime('%H:%M:%S')}] {msg}", flush=True)


def load_config() -> dict:
    return json.loads(CONFIG_PATH.read_text())


def load_instances() -> dict[str, dict]:
    """Load all 480 instances from mm_test.json."""
    rows = json.loads(DATASET_JSON.read_text())
    return {r["instance_id"]: r for r in rows}


def get_route(config: dict, route_id: str) -> dict:
    for r in config["routes"]:
        if r["id"] == route_id:
            return r
    raise ValueError(f"route {route_id} not found in config")


def run(cmd, cwd=None, timeout=300, with_proxy=True, env=None):
    """Run subprocess with proxy control."""
    e = os.environ.copy()
    if env:
        e.update(env)
    if with_proxy:
        e.setdefault("https_proxy", PROXY)
        e.setdefault("http_proxy", PROXY)
        e.setdefault("no_proxy", "127.0.0.1,localhost,agi-gateway.cxmt.com")
    else:
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            e.pop(k, None)
        e["no_proxy"] = "*"
        e["NO_PROXY"] = "*"
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       timeout=timeout, env=e)
    return p.stdout, p.stderr, p.returncode


def git_clone_or_fetch(repo: str, base_commit: str, workdir: Path) -> tuple[bool, str]:
    """Shallow fetch of base_commit (reuses proven logic from run_verified_full.py)."""
    url = f"https://github.com/{repo}.git"
    if (workdir / ".git").exists():
        for lock in (workdir / ".git").glob("*.lock"):
            try: lock.unlink()
            except OSError: pass
        _, _, rc_chk = run(["git", "cat-file", "-e", f"{base_commit}^{{commit}}"],
                           workdir, timeout=30, with_proxy=False)
        if rc_chk != 0:
            _, _, rc_f = run(["git", "fetch", "--depth=1", "origin", base_commit],
                             workdir, timeout=TIMEOUT_GIT)
            if rc_f != 0:
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
                    workdir, timeout=TIMEOUT_GIT)
    if rc != 0:
        _, _, rc_co = run(["git", "checkout", "-f", base_commit],
                           workdir, timeout=120)
        if rc_co == 0:
            return True, "fetch errored but checkout succeeded (NFS race)"
        return False, "git fetch base_commit failed (shallow)"
    _, _, rc = run(["git", "checkout", "-f", base_commit], workdir, timeout=120)
    return rc == 0, "init+shallow fetch"


def git_patch(workdir: Path) -> str:
    """Extract git diff as model_patch."""
    out, _, _ = run(["git", "diff"], workdir, timeout=30, with_proxy=False)
    # Also check for staged changes
    out2, _, _ = run(["git", "diff", "--cached"], workdir, timeout=30, with_proxy=False)
    patch = out + out2
    return patch.strip()


def reset_workdir(workdir: Path, base_commit: str):
    run(["git", "reset", "--hard", base_commit], workdir, timeout=120, with_proxy=False)
    run(["git", "clean", "-fdq"], workdir, timeout=120, with_proxy=False)


def setup_opencode_providers(routes: list[dict]):
    """Add MM-specific providers to opencode config (merge, don't overwrite)."""
    config = {}
    if OPENCODE_CONFIG.exists():
        try:
            config = json.loads(OPENCODE_CONFIG.read_text())
        except Exception:
            pass
    providers = config.setdefault("provider", {})
    for r in routes:
        if r["harness"] != "opencode":
            continue
        pid = f"mm-{r['llm']}"
        if pid not in providers:
            providers[pid] = {
                "npm": "@ai-sdk/openai-compatible",
                "name": f"MM {r['llm']} (direct gateway)",
                "options": {
                    "baseURL": r["base_url"],
                    "apiKey": r["api_key"],
                },
                "models": {
                    r["model"]: {
                        "name": r["model"],
                        "tool_call": True,
                    }
                }
            }
            log(f"  opencode provider added: {pid}/{r['model']}")
    OPENCODE_CONFIG.parent.mkdir(parents=True, exist_ok=True)
    OPENCODE_CONFIG.write_text(json.dumps(config, indent=2, ensure_ascii=False))


def build_prompt_with_images(problem_statement: str, image_infos: list[dict],
                             proxy_port: int = 9095) -> str:
    """Build prompt text with short proxy image URLs (for cline via mm_proxy).

    Uses http://127.0.0.1:<port>/mm_image/<filename> references instead of inline
    base64 data: URLs, because the base64 payload exceeds the 128 KB single-argument
    limit (MAX_ARG_STRLEN) when passed as a cline positional prompt argument.
    mm_proxy resolves these URLs by reading the file from --image-dir.
    """
    if not image_infos:
        return problem_statement
    img_md = "\n\n".join(
        f"![screenshot_{i+1}](http://127.0.0.1:{proxy_port}/mm_image/{Path(info['path']).name})"
        for i, info in enumerate(image_infos)
    )
    return (f"The following screenshots are related to this issue:\n\n"
            f"{img_md}\n\n---\n\n{problem_statement}")


def download_instance_images(instance: dict, img_handler: ImageHandler) -> list[dict]:
    """Download all problem_statement images for an instance. Returns list of info dicts."""
    ia = instance.get("image_assets", {})
    urls = ia.get("problem_statement", [])
    if not urls:
        return []
    infos = []
    for url in urls:
        info = img_handler.get_info(url)
        if info:
            infos.append(info)
        else:
            log(f"  WARN: image download failed: {url}")
    return infos


def start_mm_proxy(route: dict, port: int) -> subprocess.Popen:
    """Start mm_proxy for a cline route (with --image-dir for /mm_image/ proxy URLs)."""
    # Verify port is free first (stale proxy from a previous run would cause
    # the new one to silently fail to bind, and cline would hit the old proxy).
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.bind(("127.0.0.1", port))
        s.close()
    except OSError:
        log(f"  ⚠️ port {port} still in use — killing stale mm_proxy")
        subprocess.run(["pkill", "-f", f"mm_proxy.py --port {port}"],
                       capture_output=True)
        time.sleep(2)
    cmd = [sys.executable, str(HERE / "mm_proxy.py"),
           "--port", str(port),
           "--upstream", route["base_url"],
           "--api-key", route["api_key"],
           "--image-dir", str(IMAGE_CACHE)]
    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL,
                            stderr=open(f"/tmp/mm_proxy_{port}.log", "a"))
    # Wait until the proxy actually accepts connections (readiness probe).
    ready = False
    for _ in range(30):  # up to ~6s
        if proc.poll() is not None:
            break
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.2):
                ready = True
                break
        except OSError:
            time.sleep(0.2)
    if not ready or proc.poll() is not None:
        log(f"  ❌ mm_proxy failed to start on port {port} (rc={proc.returncode})!")
    else:
        log(f"  mm_proxy started on port {port} (pid={proc.pid}) → {route['base_url']} "
            f"(image_dir={IMAGE_CACHE})")
    return proc


def setup_cline_mm_data_dir(route: dict, proxy_port: int, route_id: str) -> str:
    """Create a per-route cline data-dir with providers.json pre-configured.

    cline persists provider settings (including baseUrl) in its data-dir and
    IGNORES the OPENAI_BASE_URL env var.  If we reuse the shared data-dir, a
    stale baseUrl from a previous run (e.g. port 9092) causes cline to connect
    to a dead proxy → 'Forbidden'.  Using a per-route data-dir with a freshly
    written providers.json guarantees the correct mm_proxy baseUrl.
    """
    import datetime
    data_dir = Path(f"/dev/shm/harness_mm_2x3/cline_data/{route_id}")
    settings_dir = data_dir / "settings"
    settings_dir.mkdir(parents=True, exist_ok=True)

    upstream_path = urlparse(route["base_url"]).path or "/v1"
    base_url = f"http://127.0.0.1:{proxy_port}{upstream_path}"

    providers = {
        "version": 1,
        "lastUsedProvider": "openai-compatible",
        "modes": {},
        "providers": {
            "openai-compatible": {
                "settings": {
                    "provider": "openai-compatible",
                    "apiKey": route["api_key"],
                    "model": route["model"],
                    "baseUrl": base_url,
                },
                "updatedAt": datetime.datetime.utcnow().isoformat() + "Z",
                "tokenSource": "migration",
            }
        },
    }
    (settings_dir / "providers.json").write_text(json.dumps(providers, indent=2))
    # secrets.json: cline expects this for the openai provider key
    secrets = {"openAiApiKey": route["api_key"]}
    (data_dir / "secrets.json").write_text(json.dumps(secrets, indent=2))
    return str(data_dir)


def sanitize_cline_prompt(text: str) -> str:
    """Escape @mentions in prompt text so cline doesn't interpret them as file mentions.

    cline (bun/Node CLI) treats ``@word`` as a file-mention: it tries to read a
    file named *word*, fails, and **silently exits with rc=0 and zero output**.
    GitHub issue text routinely contains ``@username`` mentions which trigger
    this.  We escape by inserting a zero-width space (U+200B) after the ``@``
    so the mention is no longer parsed, while remaining visually identical.
    Already-escaped ``@`` (inside backticks or followed by space/``@``) is left
    as-is.
    """
    import re
    # Match @ followed by a word char, but NOT inside backticks or already
    # followed by space/another @.  We do a simple pass: replace @word → @\u200bword
    # when @ is at start-of-token (preceded by whitespace, start-of-line, or
    # non-word char that isn't a backtick).
    return re.sub(r'(?<!`)@(?=[A-Za-z0-9_])', '@\u200b', text)


def run_cline_mm(route, instance, workdir, image_infos, proxy_port, timeout,
                 route_id: str):
    """Run cline with multimodal prompt via mm_proxy. Returns (patch, stdout, stderr, rc)."""
    if route.get("text_only"):
        # Non-multimodal model: pass plain text problem_statement (no image
        # injection). mm_proxy still forwards but finds no markdown image tags
        # → no image_url conversion → gateway gets a text-only request.
        prompt = instance["problem_statement"]
    else:
        prompt = build_prompt_with_images(instance["problem_statement"], image_infos,
                                          proxy_port)
    # Escape @mentions — cline treats @word as file mention and silently exits
    # with 0 output when the "file" doesn't exist (confirmed 2026-11-19).
    prompt = sanitize_cline_prompt(prompt)
    # cline persists provider config in its data-dir and ignores OPENAI_BASE_URL.
    # Use a per-route data-dir with providers.json pre-written to point at mm_proxy.
    data_dir = setup_cline_mm_data_dir(route, proxy_port, route_id)
    # Health-check the proxy right before invoking cline — it may have died
    # during the (potentially lengthy) image-download phase.
    import socket as _sock
    proxy_ok = False
    try:
        with _sock.create_connection(("127.0.0.1", proxy_port), timeout=1):
            proxy_ok = True
    except OSError:
        proxy_ok = False
    if not proxy_ok:
        log(f"  ⚠️ mm_proxy on port {proxy_port} died before cline — restarting")
        # Re-start proxy (the Popen object from start_mm_proxy is not accessible
        # here, so we spawn a fresh one that will be cleaned up by predict_route).
        subprocess.Popen([sys.executable, str(HERE / "mm_proxy.py"),
                          "--port", str(proxy_port),
                          "--upstream", route["base_url"],
                          "--api-key", route["api_key"],
                          "--image-dir", str(IMAGE_CACHE)],
                         stdout=subprocess.DEVNULL,
                         stderr=open(f"/tmp/mm_proxy_{proxy_port}.log", "a"))
        for _ in range(30):
            try:
                with _sock.create_connection(("127.0.0.1", proxy_port), timeout=0.2):
                    break
            except OSError:
                time.sleep(0.2)
    cmd = [CLINE_BIN, "-c", str(workdir),
           "--data-dir", data_dir,
           "-P", "openai-compatible", "-m", route["model"], "-k", route["api_key"],
           "--auto-approve", "true", "--json", prompt]
    env = {
        "OPENAI_API_KEY": route["api_key"],
        "OPENAI_BASE_URL": f"http://127.0.0.1:{proxy_port}{urlparse(route['base_url']).path or '/v1'}",
        "PATH": os.environ.get("PATH", ""),
    }
    # cline (bun/Node.js) produces zero output when stdout is a pipe
    # (capture_output=True).  Redirect to temp files instead and read back.
    import tempfile
    out_fd, out_path = tempfile.mkstemp(suffix=".out", prefix="cline_")
    err_fd, err_path = tempfile.mkstemp(suffix=".err", prefix="cline_")
    os.close(out_fd); os.close(err_fd)
    try:
        e = os.environ.copy()
        if env:
            e.update(env)
        for k in ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY"):
            e.pop(k, None)
        e["no_proxy"] = "*"; e["NO_PROXY"] = "*"
        # Debug: verify cline can produce output in this context
        try:
            _v_out, _v_err, _v_rc = subprocess.run(
                [CLINE_BIN, "--version"], capture_output=True, text=True, timeout=10, env=e)
            log(f"    cline --version: rc={_v_rc} out={_v_out.strip()!r} err={_v_err[:100]!r}")
        except Exception as _ve:
            log(f"    cline --version FAILED: {_ve}")
        log(f"    cline cmd: {[str(c)[:80] for c in cmd[:3]]}... prompt_len={len(str(prompt))}")
        with open(out_path, "w") as outf, open(err_path, "w") as errf:
            p = subprocess.run(cmd, cwd=str(workdir), stdout=outf, stderr=errf,
                               timeout=timeout + 120, env=e)
        out = Path(out_path).read_text() if Path(out_path).exists() else ""
        err = Path(err_path).read_text() if Path(err_path).exists() else ""
        rc = p.returncode
    except subprocess.TimeoutExpired:
        out, err, rc = f"[agent TIMEOUT after {timeout + 120}s]", "", -1
    finally:
        try: os.unlink(out_path); os.unlink(err_path)
        except OSError: pass
    # Debug: log cline output length and first/last 300 chars (helps diagnose
    # silent-exit issues where cline produces no output).
    log(f"    cline rc={rc} stdout_len={len(out)} stderr_len={len(err)}")
    if len(out) < 500:
        log(f"    cline STDOUT: {out!r}")
    if len(err) < 500:
        log(f"    cline STDERR: {err!r}")
    patch = git_patch(workdir)
    return patch, out, err, rc


def run_opencode_mm(route, instance, workdir, image_infos, timeout):
    """Run opencode with images via -f flag (native multimodal). Returns (patch, out, err, rc)."""
    prompt = instance["problem_statement"]
    provider_model = f"mm-{route['llm']}/{route['model']}"
    # NOTE: prompt must come BEFORE -f flags (yargs array flag consumes subsequent args)
    cmd = [OPENCODE_BIN, "run", "--dir", str(workdir),
           "--model", provider_model, "--auto", prompt]
    # Attach image files via -f (absolute paths, after prompt).
    # Skip for text-only (non-multimodal) routes — model cannot process images.
    if not route.get("text_only"):
        for info in image_infos:
            cmd.extend(["-f", info["path"]])
    env = {
        "PATH": os.environ.get("PATH", ""),
    }
    try:
        out, err, rc = run(cmd, workdir, timeout=timeout + 120, with_proxy=False, env=env)
    except subprocess.TimeoutExpired:
        out, err, rc = f"[agent TIMEOUT after {timeout + 120}s]", "", -1
    patch = git_patch(workdir)
    return patch, out, err, rc


def predict_one(route, instance, img_handler, proxy_port) -> dict:
    """Run predict for a single instance on a single route. Returns result dict."""
    iid = instance["instance_id"]
    bc = instance["base_commit"]
    repo = instance["repo"]
    harness = route["harness"]
    route_id = route["id"]
    workdir = WORKDIR_BASE / route_id / repo.replace("/", "_")

    try:
        ok, msg = git_clone_or_fetch(repo, bc, workdir)
    except subprocess.TimeoutExpired:
        return {"instance_id": iid, "route": route_id, "blocked": "git-fetch-timeout",
                "classification": "infra", "model_patch_len": 0}
    if not ok:
        return {"instance_id": iid, "route": route_id, "blocked": msg,
                "classification": "blocked", "model_patch_len": 0}

    if route.get("text_only"):
        image_infos = []
        n_img_urls = len(instance.get("image_assets", {}).get("problem_statement", []))
        log(f"  {iid}: TEXT-ONLY mode — {n_img_urls} image URL(s) NOT injected (model non-multimodal)")
    else:
        image_infos = download_instance_images(instance, img_handler)
        log(f"  {iid}: {len(image_infos)} images downloaded")

    t0 = time.time()
    if harness == "cline":
        patch, out, err, rc = run_cline_mm(route, instance, workdir, image_infos,
                                            proxy_port, TIMEOUT_RUN, route_id)
    else:
        patch, out, err, rc = run_opencode_mm(route, instance, workdir, image_infos,
                                               TIMEOUT_RUN)
    wall = time.time() - t0

    if bc:
        try: reset_workdir(workdir, bc)
        except Exception: pass

    pred_out = PRED_DIR / f"{route_id}__{iid}.json"
    pred = {"instance_id": iid, "model_name_or_path": route["model"],
            "model_patch": patch}
    pred_out.parent.mkdir(parents=True, exist_ok=True)
    pred_out.write_text(json.dumps([pred], indent=2))

    result = {"instance_id": iid, "route": route_id, "harness": harness,
              "model": route["model"], "wall_s": round(wall, 1),
              "rc": rc, "model_patch_len": len(patch),
              "n_images": len(image_infos),
              "text_only": bool(route.get("text_only"))}
    if rc != 0 and not patch:
        result["classification"] = "infra" if "TIMEOUT" in str(out) else "failed"
    elif not patch:
        result["classification"] = "empty_patch"
    else:
        result["classification"] = "has_patch"
    if out: result["stdout_tail"] = out[-200:]
    if err: result["stderr_tail"] = err[-200:]
    return result


def predict_route(route, instances, max_n=None, smoke=False) -> list[dict]:
    """Run predict for all instances on a single route."""
    route_id = route["id"]
    harness = route["harness"]
    PRED_DIR.mkdir(parents=True, exist_ok=True)
    PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

    img_handler = ImageHandler(cache_dir=IMAGE_CACHE, proxy=PROXY)
    proxy_proc = None
    proxy_port = MM_PROXY_BASE_PORT
    if harness == "cline":
        # Per-route port so concurrent cline routes don't collide on 9095.
        cline_routes = [r for r in load_config()["routes"] if r["harness"] == "cline"]
        cline_idx = next((i for i, r in enumerate(cline_routes) if r["id"] == route_id), 0)
        proxy_port = MM_PROXY_BASE_PORT + cline_idx
        proxy_proc = start_mm_proxy(route, proxy_port)
    if harness == "opencode":
        setup_opencode_providers(load_config()["routes"])

    ids = list(instances.keys())
    if smoke:
        for iid in ids:
            ia = instances[iid].get("image_assets", {})
            if ia.get("problem_statement"):
                ids = [iid]; break
        else:
            ids = [ids[0]]
    elif max_n:
        ids = ids[:max_n]

    progress_path = PROGRESS_DIR / f"{route_id}.json"
    progress = {}
    if progress_path.exists():
        try: progress = json.loads(progress_path.read_text())
        except Exception: pass

    log(f"=== PREDICT {route_id} ({harness}×{route['model']}) {len(ids)} instances ===")
    results = []
    for idx, iid in enumerate(ids):
        pred_path = PRED_DIR / f"{route_id}__{iid}.json"
        if pred_path.exists() and pred_path.stat().st_size > 30 and iid in progress:
            log(f"  [{idx+1}/{len(ids)}] {iid} — SKIP (already done)")
            results.append(progress[iid]); continue
        log(f"  [{idx+1}/{len(ids)}] {iid}")
        try:
            result = predict_one(route, instances[iid], img_handler, proxy_port)
        except Exception as e:
            result = {"instance_id": iid, "route": route_id,
                       "classification": "error", "error": str(e),
                       "model_patch_len": 0}
            log(f"    ERROR: {e}")
        results.append(result)
        progress[iid] = result
        progress_path.write_text(json.dumps(progress, indent=2, ensure_ascii=False))
        cls = result.get("classification", "?")
        plen = result.get("model_patch_len", 0)
        wall = result.get("wall_s", 0)
        log(f"    → {cls} patch={plen}B wall={wall}s")

    if proxy_proc:
        proxy_proc.terminate()
        proxy_proc.wait(timeout=5)
        log(f"  mm_proxy stopped (port {proxy_port})")

    n_has = sum(1 for r in results if r.get("classification") == "has_patch")
    n_empty = sum(1 for r in results if r.get("classification") == "empty_patch")
    n_infra = sum(1 for r in results if r.get("classification") == "infra")
    log(f"=== {route_id} DONE: {len(results)} instances, "
        f"has_patch={n_has} empty={n_empty} infra={n_infra} ===")
    return results


def merge_predictions(route_id) -> Path:
    """Merge all per-instance predictions into a single JSON for swebench eval."""
    preds = []
    for f in sorted(PRED_DIR.glob(f"{route_id}__*.json")):
        try: preds.extend(json.loads(f.read_text()))
        except Exception: pass
    merged_path = PRED_DIR / f"merged_{route_id}.json"
    merged_path.write_text(json.dumps(preds, indent=2))
    log(f"  merged {len(preds)} predictions → {merged_path}")
    return merged_path


def eval_route(route, predictions_path=None):
    """Run swebench eval for a route using Docker containers."""
    route_id = route["id"]
    if predictions_path is None:
        predictions_path = merge_predictions(route_id)
    if not predictions_path.exists():
        log(f"  ERROR: no predictions for {route_id}"); return
    run_id = f"mm_2x3_{route_id}"
    cmd = [sys.executable, "-m", "swebench.harness.run_evaluation",
           "--dataset_name", str(DATASET_JSON), "--split", "test",
           "--predictions_path", str(predictions_path),
           "--max_workers", "1", "--run_id", run_id,
           "--timeout", str(TIMEOUT_RUN)]
    log(f"=== EVAL {route_id} ===")
    out, err, rc = run(cmd, timeout=7200, with_proxy=False)
    log(f"  eval rc={rc}")
    if err: log(f"  stderr tail: {err[-300:]}")
    return rc


def main():
    ap = argparse.ArgumentParser(description="SWE-bench Multimodal 2×3 orchestrator")
    sub = ap.add_subparsers(dest="command")

    p_smoke = sub.add_parser("smoke", help="1-instance smoke test")
    p_smoke.add_argument("--route", required=True)

    p_pred = sub.add_parser("predict", help="Run predict phase")
    p_pred.add_argument("--route", default=None, help="Route ID (or --all)")
    p_pred.add_argument("--all", action="store_true")
    p_pred.add_argument("--max-n", type=int, default=None)

    p_eval = sub.add_parser("eval", help="Run eval phase")
    p_eval.add_argument("--route", required=True)
    p_eval.add_argument("--predictions", default=None)

    p_smoke.add_argument("--max-n", type=int, default=None)
    args = ap.parse_args()

    config = load_config()
    instances = load_instances()

    if args.command == "smoke":
        route = get_route(config, args.route)
        results = predict_route(route, instances, smoke=True)
        log(f"SMOKE TEST COMPLETE: {json.dumps(results, indent=2, ensure_ascii=False)}")

    elif args.command == "predict":
        if args.all:
            routes = config["routes"]
        elif args.route:
            routes = [get_route(config, args.route)]
        else:
            ap.error("--route or --all required")
        for route in routes:
            log(f"--- Starting route {route['id']} ---")
            predict_route(route, instances, max_n=args.max_n)

    elif args.command == "eval":
        route = get_route(config, args.route)
        eval_route(route, predictions_path=Path(args.predictions) if args.predictions else None)

    else:
        ap.print_help()


if __name__ == "__main__":
    main()

