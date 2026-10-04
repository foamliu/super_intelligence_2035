#!/usr/bin/env python3
"""R1 evaluation adapter — run SWE-bench-Lite WITHOUT Docker.

Reuses the official swebench harness's docker-independent scoring/spec code
*by import* (not copy), and swaps only the docker execution layer
(``create_container`` / ``container.exec_run``) for a local ``unshare`` sandbox
whose per-instance ``rootfs`` lives on ``/nas_train`` (not shared docker storage).

Reuse points (source-verified @ upstream commit 02e7a74):
  make_test_spec()         swebench/harness/utils.py:251
  parse_eval_script()      swebench/harness/utils.py:213
  record_test_exit_code()  swebench/harness/utils.py:222
  get_predictions_from_file() swebench/harness/utils.py:37
  get_eval_report()        swebench/harness/grading.py:329
  GIT_APPLY_CMDS           swebench/harness/run_evaluation.py:54-59
  constants                swebench/harness/constants/__init__.py
  CONTAINER_USER/WORKDIR   swebench/image_builder/constants/__init__.py:6-7

Replaced (docker-bound):
  create_container()       swebench/harness/run_evaluation.py:72
  exec_run_with_timeout()  swebench/harness/docker_utils.py:128
  copy_to_container()      swebench/harness/docker_utils.py:16

Dependencies to import the official package (all pure-python client libs;
verified 2026-10-03 against the current py310 env — only missing pieces)::
    pip install docker modal unidiff ghapi

Example (step 2, single repo end-to-end)::
    python r1_eval.py --instance django__django-10914 \\
        --predictions predictions.json \\
        --rootfs /nas_train/app.e0031982/harness_work/rootfs/django__django-10914 \\
        --run-id R1_SMOKE --sandbox unshare

Honesty notes:
  * The sandbox executor pins a believable ``unshare`` invocation (mirrors
    R1_ADAPTER_DESIGN.md §5, whose flags were validated in batch-5 step-1), but
    the exact rootfs layout + working flags MUST be validated end-to-end in
    step 2 (a real django rootfs) before scaling to 300×5.
  * ``--sandbox native`` runs with NO isolation (debug only) and assumes the
    rootfs is laid out under ``/``. NEVER use native against model patches.
"""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
import time
from pathlib import Path

from swebench.harness.utils import make_test_spec, get_predictions_from_file
from swebench.harness.grading import get_eval_report
from swebench.harness.constants import (
    APPLY_PATCH_PASS,
    LOG_REPORT,
    LOG_TEST_OUTPUT,
)
from swebench.image_builder.constants import CONTAINER_WORKDIR  # "/testbed"

# Mirror of swebench/harness/run_evaluation.py:54-59 (the 4 patch strategies).
GIT_APPLY_CMDS = [
    "git apply --verbose",
    "git apply --verbose --3way",
    "git apply --verbose --reject",
    "patch --batch --forward --fuzz=5 -p1 -i",
]

# Patch file lives at the rootfs ROOT (NOT /tmp): the sandbox mounts a fresh
# tmpfs over /tmp, which would hide a patch the host wrote under rootfs/tmp.
PATCH_FILE = "/patch.diff"


# ---------------------------------------------------------------------------
# Sandbox executors
# ---------------------------------------------------------------------------
class Sandbox:
    """Run a command inside an instance's rootfs, isolated from the host.

    ``rootfs`` is a directory that, when used as ``/``, contains the instance's
    environment at the same absolute paths the official eval script assumes::

        /testbed                     repo @ base_commit
        /opt/miniconda3/envs/testbed conda env (built in step 2)
        /bin/bash + base system      (debootstrap-ish, also step 2)
    """

    def __init__(self, rootfs: Path, timeout: int):
        self.rootfs = Path(rootfs)
        self.timeout = timeout

    def run(self, cmd: str, workdir: str | None = None):
        """Return ``(output, exit_code, timed_out, seconds)``.

        ``exit_code`` is ``None`` on timeout. ``workdir`` is an absolute path
        *inside* the rootfs (typically ``/testbed``).
        """
        raise NotImplementedError


class NativeSandbox(Sandbox):
    """DEBUG ONLY — runs with no namespace/chroot isolation.

    Pretends ``self.rootfs`` is ``/``; only works when ``/testbed`` and
    ``/opt/miniconda3`` actually exist on the host. Do not use against model
    patches.
    """

    def run(self, cmd: str, workdir: str | None = None):
        full = f"cd {workdir} && {cmd}" if workdir else cmd
        t0 = time.time()
        try:
            p = subprocess.run(
                ["/bin/bash", "-c", full],
                capture_output=True,
                timeout=self.timeout,
            )
            out = (p.stdout + p.stderr).decode(errors="replace")
            return out, p.returncode, False, time.time() - t0
        except subprocess.TimeoutExpired as e:
            out = ((e.stdout or b"") + (e.stderr or b"")).decode(errors="replace")
            return out, None, True, time.time() - t0


class UnshareSandbox(Sandbox):
    """Production sandbox — user+mount namespace then chroot into rootfs.

    Mirrors the mount sequence proven end-to-end in step 2
    (``harness_work/run_eval_sandbox.sh``, ``django__django-10914`` resolved=True):
    bind host ``/usr`` (base system), bind the writable locale archive, mount a
    tmpfs on ``/tmp``, then ``chroot``. ``--pid`` is dropped to match the proven
    script (a chroot PID-1 without init can mis-clean child daemons). Guest env
    pins the intra-net proxy + aliyun PyPI so ``pip install -e .`` reaches wheels.
    """

    def run(self, cmd: str, workdir: str | None = None):
        full = f"cd {workdir} && {cmd}" if workdir else cmd
        r = str(self.rootfs)
        inner = (
            f"mount --bind /usr {r}/usr || exit 11; "
            f"mount --bind {r}/.locale {r}/usr/lib/locale || exit 12; "
            f"mount -t tmpfs tmpfs {r}/tmp || exit 13; "
            f"chroot {r} /usr/bin/env HOME=/tmp TMPDIR=/tmp PIP_NO_INPUT=1 "
            f"http_proxy=http://172.19.92.25:13128 "
            f"https_proxy=http://172.19.92.25:13128 "
            f"PIP_INDEX_URL=https://mirrors.aliyun.com/pypi/simple/ "
            f"/bin/bash -c {shlex.quote(full)}"
        )
        argv = ["unshare", "--user", "--map-root-user", "--mount", "--fork",
                "bash", "-c", inner]
        t0 = time.time()
        try:
            p = subprocess.run(argv, capture_output=True, timeout=self.timeout)
            out = (p.stdout + p.stderr).decode(errors="replace")
            return out, p.returncode, False, time.time() - t0
        except subprocess.TimeoutExpired as e:
            out = ((e.stdout or b"") + (e.stderr or b"")).decode(errors="replace")
            return out, None, True, time.time() - t0


SANDYBOXES = {"native": NativeSandbox, "unshare": UnshareSandbox}


# ---------------------------------------------------------------------------
# Instance runner (mirrors run_evaluation.run_instance, sans docker)
# ---------------------------------------------------------------------------
def r1_run_instance(test_spec, pred, rootfs: Path, sandbox_cls, timeout: int,
                    inst_log_dir: Path, skip_patch: bool = False,
                    base_commit: str = ""):
    """Run one instance and return the report dict (mirrors run_instance)."""
    instance_id = test_spec.instance_id
    inst_log_dir.mkdir(parents=True, exist_ok=True)
    sb = sandbox_cls(rootfs, timeout)

    # -- 1) apply model patch (mirror run_evaluation.py:288-337) ------------
    if not skip_patch:
        patch = pred.get("model_patch") or ""
        (inst_log_dir / "patch.diff").write_text(patch)
        dst = rootfs / PATCH_FILE.lstrip("/")
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(patch)

        # Reset the REUSED rootfs testbed to a clean base before applying.  The
        # official docker harness gets a fresh container per instance, but R1
        # reuses one rootfs dir across runs (and across harnesses in the 300x5
        # sweep) -- a previous run's applied patch + `git apply --reject`
        # `.rej` files + `--3way` `UU` merge state leak into the next run and
        # make its patch spuriously fail to apply (observed 2026-10-04: codex's
        # applied patch + .rej/.UU residue made opencode's patch report
        # patch_successfully_applied=false until the testbed was reset; after
        # reset, opencode resolved=true).  A plain `git checkout -- .` is NOT
        # enough -- it refuses on `UU` unmerged paths -- so force `reset --hard`
        # back to base_commit and drop stray files.
        base = base_commit or getattr(test_spec, "base_commit", None)
        reset_cmd = f"git reset --hard {base}" if base else "git reset --hard HEAD"
        sb.run(f"{reset_cmd} ; git clean -fdq", workdir=CONTAINER_WORKDIR)

        applied = False
        last_out = ""
        for attempt, git_apply_cmd in enumerate(GIT_APPLY_CMDS):
            if attempt:
                sb.run("git reset --hard HEAD ; git clean -fdq", workdir=CONTAINER_WORKDIR)
            out, code, _, _ = sb.run(
                f"{git_apply_cmd} {PATCH_FILE}", workdir=CONTAINER_WORKDIR
            )
            if code == 0:
                applied = True
                break
            last_out = out
        if not applied:
            _, code, _, _ = sb.run(
                f"git apply --check --reverse {PATCH_FILE}",
                workdir=CONTAINER_WORKDIR,
            )
            if code == 0:
                applied = True
        if not applied:
            (inst_log_dir / LOG_TEST_OUTPUT).write_text(
                f">>>>> Patch Apply Failed\n{last_out}\n"
            )
            report = get_eval_report(
                test_spec=test_spec,
                prediction=pred,
                test_log_path=inst_log_dir / LOG_TEST_OUTPUT,
                include_tests_status=True,
            )
            (inst_log_dir / LOG_REPORT).write_text(json.dumps(report, indent=4))
            return report

    # -- 2) write eval.sh into rootfs, run it, capture output ----------------
    eval_script = test_spec.eval_script
    (inst_log_dir / "eval.sh").write_text(eval_script)
    (rootfs / "eval.sh").write_text(eval_script)

    out, _, timed_out, _runtime = sb.run("/bin/bash /eval.sh")
    test_output_path = inst_log_dir / LOG_TEST_OUTPUT
    with open(test_output_path, "w") as f:
        f.write(out)
        if timed_out:
            f.write(f"\n\nTimeout error: {timeout} seconds exceeded.\n")

    # -- 3) grade with the official scorer --------------------------------
    report = get_eval_report(
        test_spec=test_spec,
        prediction=pred,
        test_log_path=test_output_path,
        include_tests_status=True,
    )
    (inst_log_dir / LOG_REPORT).write_text(json.dumps(report, indent=4))
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="R1 (no-docker) SWE-bench evaluator")
    ap.add_argument("--instance", required=True,
                    help="instance_id, e.g. django__django-10914")
    ap.add_argument("--predictions", default=None,
                    help="predictions.json/jsonl (official format; required unless --spec-only)")
    ap.add_argument("--rootfs", default=None,
                    help="per-instance rootfs dir on /nas_train; required unless --spec-only")
    ap.add_argument("--run-id", default="R1")
    ap.add_argument("--sandbox", choices=list(SANDYBOXES), default="unshare")
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--skip-patch", action="store_true")
    ap.add_argument("--dataset", default="SWE-bench/SWE-bench_Lite")
    ap.add_argument("--split", default="test")
    ap.add_argument("--log-dir", default="logs/evaluation")
    ap.add_argument("--spec-only", action="store_true",
                    help="print the TestSpec and exit (no execution)")
    args = ap.parse_args()

    from datasets import load_dataset
    ds = load_dataset(args.dataset, split=args.split)
    row = next(x for x in ds if x["instance_id"] == args.instance)
    test_spec = make_test_spec(row)

    if args.spec_only:
        print("== TestSpec ==")
        for i, ln in enumerate(test_spec.eval_script_list):
            print(f"  [{i}] {ln}")
        print("log_parser:", test_spec.log_parser, "| eval_type:", test_spec.eval_type)
        print("FAIL_TO_PASS:", test_spec.FAIL_TO_PASS)
        print("PASS_TO_PASS:", test_spec.PASS_TO_PASS)
        return

    if not args.predictions or not args.rootfs:
        sys.exit("--predictions and --rootfs are required (unless --spec-only)")

    preds = get_predictions_from_file(args.predictions, args.dataset, args.split)
    pred = next(p for p in preds if p["instance_id"] == args.instance)

    model = pred.get("model_name_or_path", "None").replace("/", "__")
    inst_log_dir = Path(args.log_dir) / args.run_id / model / args.instance

    report = r1_run_instance(
        test_spec=test_spec,
        pred=pred,
        rootfs=Path(args.rootfs),
        sandbox_cls=SANDYBOXES[args.sandbox],
        timeout=args.timeout,
        inst_log_dir=inst_log_dir,
        skip_patch=args.skip_patch,
        base_commit=row.get("base_commit", ""),
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()