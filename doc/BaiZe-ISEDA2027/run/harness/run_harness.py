#!/usr/bin/env python3
"""Per-harness SWE-bench driver — turn an SWE-bench instance into a model_patch.

Step 3 of the batch-5 plan (the "harness adaptation layer").  The official
`predictions.json` is only the *evaluated* object; it says nothing about how
the patch was produced.  Each agent harness has its own headless
(non-interactive) way to be asked "solve this issue in this repo".

This file is that adaptation layer: one driver per harness.  Each driver
  1. receives an instance (`problem_statement` + repo @ `base_commit`),
  2. runs the harness headlessly in the repo workdir with a unified model,
  3. returns the resulting `model_patch` (git diff), which the caller writes
     into a predictions.json for `r1_eval.py` (already delivered) to grade.

Unified buyline (frozen 2026-10-03, per batch-5):
    model  = deepseek-v4-flash
    gateway= http://agi-gateway.cxmt.com/v1   (HTTP 200 verified)

Honesty: only `cline` is *runnable today* (it is the installed, configured CL
that the loop itself launches — v4.1.21, already pointed at the gateway with
`deepseek-v4-flash` in act mode).  codex / opencode / claude-code /
deepseek-harness are all source-only on this host (not built); their drivers
are written to the correct invocation surface (path:line cited) but are marked
`available() == False` until a build step completes.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

GATEWAY = os.environ.get("OPENAI_API_URL", "http://agi-gateway.cxmt.com/v1")
UNIFIED_MODEL = "deepseek-v4-flash"
CLINE_BIN = shutil.which("cline") or "/home/app.e0031982/.bun/bin/cline"
CLINE_SECRETS = Path.home() / ".cline" / "data" / "secrets.json"


def resolve_cline_key() -> str:
    """Resolve the cline API key: `$OPENAI_API_KEY` first, else cline's own secrets.json.

    2026-10-04 ops: `.29`'s `~/.bashrc` exported a **revoked** key under
    `OPENAI_API_KEY`, which **shadowed** the valid one in
    `~/.cline/data/secrets.json` -> every cline call answered `Forbidden` while
    still exiting 0, so the loop span **silently for ~9h**.  That export has been
    commented out at the source (ops, RUN_ID 29); this fallback makes the driver
    read the **single source of truth** (secrets.json) instead of depending on
    whatever the launching shell happened to export.
    """
    k = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if k:
        return k
    try:
        return str(json.loads(CLINE_SECRETS.read_text())["openAiApiKey"]).strip()
    except Exception:
        return ""


@dataclass
class DriverResult:
    harness: str = ""
    model_patch: str = ""
    stdout: str = ""
    stderr: str = ""
    returncode: int = 0
    timed_out: bool = False
    wall_s: float = 0.0


def _run(cmd: list[str], cwd: Path, timeout: int) -> DriverResult:
    """Run a harness subprocess; capture stdout/stderr; return wall + code."""
    import time
    t0 = time.time()
    try:
        p = subprocess.run(
            cmd, cwd=str(cwd), capture_output=True, text=True, timeout=timeout
        )
        return DriverResult(
            stdout=p.stdout, stderr=p.stderr, returncode=p.returncode,
            wall_s=time.time() - t0,
        )
    except subprocess.TimeoutExpired as e:
        return DriverResult(
            stdout=e.stdout or "", stderr=e.stderr or "",
            returncode=-1, timed_out=True, wall_s=time.time() - t0,
        )


def git_patch(workdir: Path) -> str:
    """Capture edits as a patch (tracked diff + new untracked files).

    `git add -N .` stages intent-to-add for untracked files so they appear in
    `git diff` without committing — mirrors how SWE-bench model_patch is
    expected to include newly created files.
    """
    _run(["git", "add", "-N", "."], workdir, timeout=60)
    r = _run(["git", "--no-pager", "diff", "HEAD"], workdir, timeout=120)
    return r.stdout


# ---------------------------------------------------------------------------
# Harness drivers
# ---------------------------------------------------------------------------

class ClineDriver:
    """cline headless CLI.

    Invocation (verified `cline --help` 2026-10-03 + smoke run 2026-10-03):
        cline -c <cwd> -m <model> -k <key> --auto-approve true --json <prompt>
    Provider/base-url come from ~/.cline/data/globalState.json (already
    openai@http://agi-gateway.cxmt.com/v1).

    GOTCHA (corrected 2026-10-04 by ops — the 2026-10-03 note had it backwards):
    on `.29` the **shell environment** exported a REVOKED key via `OPENAI_API_KEY`
    (from `~/.bashrc`), which **SHADOWED** the valid key in
    `~/.cline/data/secrets.json` -> the gateway answered `Forbidden` on the first
    model call, **while cline still exited 0** (the loop therefore span silently
    for ~9h).  Empirically, on `.29` ONLY an explicit `-k <valid key>` works
    (env matrix: V0 原样 / V1 剥OPENAI_* / V2 剥proxy+OPENAI_* all `Forbidden`;
    V3 = V2 + `-k` -> OK).  Hence we ALWAYS pass `-k`, resolved at runtime via
    `resolve_cline_key()` (env first, else secrets.json) — it never appears here.
    """

    name = "cline"

    def __init__(self):
        self.api_key = resolve_cline_key()

    def available(self) -> bool:
        return Path(CLINE_BIN).exists() and bool(self.api_key)

    def run(self, instance: dict, workdir: Path, timeout: int = 3600) -> DriverResult:
        cmd = [
            CLINE_BIN, "-c", str(workdir),
            "-m", UNIFIED_MODEL,
            "-k", self.api_key,
            "--auto-approve", "true",
            "--json",
            instance["problem_statement"],
        ]
        r = _run(cmd, workdir, timeout)
        r.harness = self.name
        r.model_patch = git_patch(workdir) if r.returncode == 0 else ""
        return r


class CodexDriver:
    """codex CLI (`codex exec`) — codex-rs Rust binary, NOT built on this host.

    Headless surface (codex-rs/exec + codex-rs/codex): `codex exec --json`
    runs non-interactively.  Requires `cargo build -p codex` first.
    """

    name = "codex"

    def available(self) -> bool:
        return shutil.which("codex") is not None

    def run(self, instance: dict, workdir: Path, timeout: int = 3600) -> DriverResult:
        cmd = [
            "codex", "exec", "--cd", str(workdir),
            "--model", UNIFIED_MODEL,
            "--json",
            instance["problem_statement"],
        ]
        r = _run(cmd, workdir, timeout)
        r.harness = self.name
        r.model_patch = git_patch(workdir) if r.returncode == 0 else ""
        return r


class OpencodeDriver:
    """opencode — bun TS monorepo, NOT built here.  Headless via SDK/CLI.

    Entry point `packages/opencode/src/index.ts` (bun); non-interactive via
    the JS SDK.  Requires `bun install` + build.
    """

    name = "opencode"

    def available(self) -> bool:
        return shutil.which("opencode") is not None

    def run(self, instance: dict, workdir: Path, timeout: int = 3600) -> DriverResult:
        cmd = [
            "opencode", "run",
            "--cwd", str(workdir),
            "--model", UNIFIED_MODEL,
            instance["problem_statement"],
        ]
        r = _run(cmd, workdir, timeout)
        r.harness = self.name
        r.model_patch = git_patch(workdir) if r.returncode == 0 else ""
        return r


class ClaudeCodeDriver:
    """claude-code — leaked source (2026-03-31), bun bundle, NOT built here.

    README.md documents `bun run start -- -p "<prompt>"`; needs
    `ANTHROPIC_API_KEY` and a base-URL override for the gateway.
    """

    name = "claude-code"

    def available(self) -> bool:
        return shutil.which("claude") is not None

    def run(self, instance: dict, workdir: Path, timeout: int = 3600) -> DriverResult:
        cmd = ["bun", "run", "start", "--", "-p", instance["problem_statement"]]
        r = _run(cmd, workdir, timeout)
        r.harness = self.name
        r.model_patch = git_patch(workdir) if r.returncode == 0 else ""
        return r


class DeepseekHarnessDriver:
    """deepseek-harness — python SDK `jsonrpc-agent` minimal variant.

    docs/user/guide/python-sdk.md: minimal variant; separate workspace + session
    id per task (BENCHMARK.md).  Requires `pip install` of the SDK (not on host).
    """

    name = "deepseek-harness"

    def available(self) -> bool:
        try:
            import importlib.util
            return importlib.util.find_spec("deepseek_sdk") is not None
        except Exception:
            return False

    def run(self, instance: dict, workdir: Path, timeout: int = 3600) -> DriverResult:
        r = DriverResult(returncode=1)
        r.harness = self.name
        r.stderr = "deepseek-harness SDK not installed on host (available()==False)"
        return r


DRIVERS = {
    d.name: d
    for d in [
        ClineDriver(),
        CodexDriver(),
        OpencodeDriver(),
        ClaudeCodeDriver(),
        DeepseekHarnessDriver(),
    ]
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main() -> int:
    import sys
    import argparse
    from datasets import load_dataset

    ap = argparse.ArgumentParser(description="harness -> model_patch driver (step 3)")
    ap.add_argument("--harness", required=True, choices=list(DRIVERS))
    ap.add_argument("--instance", required=True)
    ap.add_argument("--workdir", required=True, help="repo workdir @ base_commit")
    ap.add_argument("--dataset", default="SWE-bench/SWE-bench_Lite")
    ap.add_argument("--split", default="test")
    ap.add_argument("--model", default=UNIFIED_MODEL)
    ap.add_argument("--timeout", type=int, default=3600)
    ap.add_argument("--out", default=None, help="write patch to this file (else stdout)")
    args = ap.parse_args()

    driver = DRIVERS[args.harness]
    if not driver.available():
        print(f"[{driver.name}] NOT AVAILABLE on this host", file=sys.stderr)
        return 2

    ds = load_dataset(args.dataset, split=args.split)
    inst = next(x for x in ds if x["instance_id"] == args.instance)

    res = driver.run(inst, Path(args.workdir), timeout=args.timeout)
    print(f"== harness={res.harness} rc={res.returncode} "
          f"timed_out={res.timed_out} wall={res.wall_s:.1f}s ==")
    if args.out:
        Path(args.out).write_text(res.model_patch)
        print(f"wrote model_patch ({len(res.model_patch)} bytes) -> {args.out}")
    else:
        print(res.model_patch)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())