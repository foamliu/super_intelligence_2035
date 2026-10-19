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
        """Install DeepSeek-Harness SDK inside the Docker container via pip."""
        await self.exec_as_root(
            environment,
            command=(
                "pip install --break-system-packages deepseek-harness-sdk 2>&1 | tail -5"
            ),
        )
        # Verify import
        result = await environment.exec(
            command='python3 -c "import deepseek_harness; print(deepseek_harness.__version__)" 2>&1 || true'
        )
        self._version = result.stdout.strip() or "unknown"
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

        # Write a runner script that uses the SDK
        runner_script = f'''
import sys
from deepseek_harness import DeepSeekHarness

harness = DeepSeekHarness(
    provider="deepseek-official",
    model={shlex.quote(self._tb_model)},
    base_url={shlex.quote(TB_GW_DSH_URL)},
    api_key={shlex.quote(TB_DUMMY_KEY)},
    cwd={shlex.quote(cwd)},
    dsh_home={shlex.quote(self._dsh_home)},
    profile={shlex.quote(self._profile)},
    request_timeout_seconds=float({self._timeout}),
    initialize_timeout_seconds=60.0,
)
with harness:
    result = harness.run({shlex.quote(instruction)}, session_id="tb-deepseek")
    print(getattr(result, "final_response", "") or "")
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
