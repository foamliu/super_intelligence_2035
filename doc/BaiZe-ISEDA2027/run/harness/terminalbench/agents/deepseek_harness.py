"""DeepSeek-Harness adapter for Terminal-Bench 2.0.

Preserves the native DeepSeek-Harness SDK tool loop (shell / file edits /
multi-turn).  Uses the Python SDK ``DeepSeekHarness`` class, same as
SWE-bench DeepseekHarnessDriver.

Install: pip install deepseek-harness-sdk
Run:     DeepSeekHarness(provider=..., model=..., base_url=..., cwd=...).run(prompt)
"""

from __future__ import annotations

import shlex
from typing import Annotated, Any, override

from pydantic import Field

from harbor.agents.options import Cli, InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from terminalbench.agents._base import (
    TBBaseAgent,
    TB_AGENT_TIMEOUT,
    TB_DUMMY_KEY,
    TB_GW_DSH_URL,
    TB_MODEL,
)


class DeepseekHarnessTBOptions(InstalledAgentOptions):
    """Options for the DeepSeek-Harness Terminal-Bench adapter."""

    profile: Annotated[
        str | None,
        Cli("--profile", fallback="DSH_TB_PROFILE"),
    ] = Field(
        default="sdk-minimal",
        description="DeepSeek-Harness SDK profile.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="DSH_TB_TIMEOUT"),
    ] = Field(default=None, description="DeepSeek-Harness timeout in seconds.")


class DeepseekHarnessTB(TBBaseAgent):
    """DeepSeek-Harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: the DeepSeek-Harness SDK launches a bundled
    native runtime (``dsh``) as a subprocess over JSON-RPC stdio, which
    iterates through tool calls autonomously.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(DeepseekHarnessTBOptions, kwargs)
        self._profile = opts.profile or "sdk-minimal"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT
        self._dsh_home = "/tmp/dsh_home_tb"

    @staticmethod
    @override
    def name() -> str:
        return "deepseek-harness"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install DeepSeek-Harness SDK inside the Docker container via pip.

        FIX (2026-10-25, R492): the old ``pip install ...`` used the bare ``pip``
        command, which is NOT on PATH on ~36/50 task images
        (``bash: line 1: pip: command not found`` → install silently "succeeds"
        because the adapter never checked the return code, then run() fails with
        NonZeroAgentExitCodeError / empty output → 0 pass).  Use
        ``python3 -m pip`` (always present with python3), VERIFY the import
        succeeds, and raise loudly if it does not.
        """
        install_res = await self.exec_as_root(
            environment,
            command=(
                "python3 -m pip install --break-system-packages "
                "deepseek-harness-sdk 2>&1 | tail -8"
            ),
        )
        # Verify the class used by run() is importable; raise if the SDK did not
        # install (was silently 0% before).  NOTE (R493 fix): the SDK module has
        # NO __version__ attribute — the R492 check `deepseek_harness.__version__`
        # raised AttributeError → RuntimeError on EVERY trial → 0 pass, even
        # though the install itself succeeded.  Import the actual class
        # DeepSeekHarness that run() uses instead.  Also capture stdout (the
        # command uses 2>&1, so stderr is empty; the real error is in stdout).
        result = await environment.exec(
            command='python3 -c "from deepseek_harness import DeepSeekHarness; print(1)" 2>&1'
        )
        if result.return_code != 0:
            raise RuntimeError(
                f"DeepSeek-Harness SDK install failed (python3 -m pip): "
                f"rc={result.return_code} stdout={(result.stdout or '')[:400]} "
                f"install_out={(install_res.stdout or '')[:300]}"
            )
        # The SDK has no __version__; extract the version from pip's
        # "Successfully installed ... deepseek-harness-sdk-X.Y.Z" line if present.
        self._version = "unknown"
        for _line in (install_res.stdout or "").splitlines():
            if "deepseek-harness-sdk-" in _line:
                self._version = _line.strip()
                break
        # Create DSH home
        await environment.exec(command=f"mkdir -p {self._dsh_home}")

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run DeepSeek-Harness headlessly with the task instruction.

        The SDK is invoked via a Python script that creates a DeepSeekHarness
        instance and calls .run() with the problem statement.
        """
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")

        # Write a runner script that uses the SDK.
        #
        # BUG FIX (R452, 2026-10-19): the previous version embedded the
        # instruction and other string args with shlex.quote(), which produces
        # SHELL-safe quoting (single-quotes + `'\''` escapes) — NOT valid Python.
        # For a multi-line instruction containing single quotes this yielded a
        # Python SyntaxError at `harness.run('...` so every trial exited 1
        # (Gen4 deepseek-harness 5/5 RuntimeError).  The proven SWE-bench driver
        # (run_harness.py:DeepseekHarnessDriver.run) passes the problem statement
        # as a Python *variable*; here we generate source, so we embed each value
        # with repr() — repr(str) is always a valid Python string literal.
        # FIX (2026-10-25, R492): the old runner swallowed all exceptions — when
        # the SDK failed to call the model or the native `dsh` runtime did not
        # initialize, harness.run() returned an empty result, the script printed
        # nothing and exited 0 → 52/50 trials "exit 0, empty stdout", 0 pass, with
        # NO error visible.  Now wrap in try/except, print any traceback to stderr,
        # exit non-zero on failure, and emit a loud diagnostic when the agent
        # produced no final response (so the next run reveals the real cause
        # instead of a silent 0%).
        runner_script = f'''
import sys, traceback
try:
    from deepseek_harness import DeepSeekHarness
    harness = DeepSeekHarness(
        provider="deepseek-official",
        model={repr(self._tb_model)},
        base_url={repr(TB_GW_DSH_URL)},
        api_key={repr(TB_DUMMY_KEY)},
        cwd={repr(cwd)},
        dsh_home={repr(self._dsh_home)},
        profile={repr(self._profile)},
        request_timeout_seconds=float({self._timeout}),
        initialize_timeout_seconds=60.0,
    )
    with harness:
        result = harness.run({repr(instruction)}, session_id="tb-deepseek")
        final = getattr(result, "final_response", "") or ""
        print(final)
        if not final:
            # Loud diagnostic: the agent produced no output.  Print whatever
            # the result object exposes so the failure is no longer silent.
            print("=== DSH WARNING: empty final_response ===", file=sys.stderr)
            print("result repr:", repr(result)[:1000], file=sys.stderr)
            sys.exit(2)
except SystemExit:
            raise
except Exception:
            print("=== DSH RUNNER EXCEPTION ===", file=sys.stderr)
            traceback.print_exc()
            sys.exit(1)
'''

        # Write the script to a temp file and execute it
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix="_dsh_runner.py", delete=False) as f:
            f.write(runner_script)
            script_local = Path(f.name)
        script_remote = "/tmp/dsh_runner.py"
        await environment.upload_file(script_local, script_remote)

        # The SDK gets base_url/api_key from the runner script (gw_proxy_dsh).
        # Also point OPENAI_* env at the dsh proxy in case the native `dsh`
        # runtime reads them.
        env = self._env_for_harness(extra={
            "OPENAI_API_KEY": TB_DUMMY_KEY,
            "OPENAI_BASE_URL": TB_GW_DSH_URL,
        })

        result = await environment.exec(
            command=f"python3 {script_remote}",
            env=env,
            timeout_sec=self._timeout,
        )

        context.metadata = {
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "exit_code": result.return_code,
        }

        if result.return_code != 0:
            raise RuntimeError(
                f"DeepSeek-Harness exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
