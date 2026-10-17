"""Cline-patched adapter for Terminal-Bench 2.0.

Preserves the native Cline CLI tool loop (read_file / write_to_file /
execute_command / multi-turn fix).  Uses an independent ``--data-dir`` so
the patched Cline's globalState.json does not collide with the loop's own
Cline instance (same design as SWE-bench run_harness.py:run_cline_patched).

Install: npm install -g @anthropic-ai/cline (or use pre-built tarball)
Run:     cline -c <cwd> --data-dir /tmp/cline_tb_data \
             -P openai -m kimi-k2.6-cloud -k <key> \
             --auto-approve true --json <instruction>
"""

from __future__ import annotations

import shlex
from typing import Annotated, Any, override

from pydantic import Field

from harbor.agents.capabilities import AgentCapabilities
from harbor.agents.options import Cli, InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from terminalbench.agents._base import TBBaseAgent, TB_AGENT_TIMEOUT, TB_MODEL


class ClinePatchedOptions(InstalledAgentOptions):
    """Options for the Cline-patched Terminal-Bench adapter."""

    cline_version: Annotated[
        str | None,
        Cli("--cline-version", fallback="CLINE_TB_VERSION"),
    ] = Field(
        default=None,
        description="npm version of @anthropic-ai/cline to install.",
    )
    data_dir: Annotated[
        str | None,
        Cli("--data-dir"),
    ] = Field(
        default="/tmp/cline_tb_data",
        description="Independent Cline data directory (avoids collision with host Cline).",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="CLINE_TB_TIMEOUT"),
    ] = Field(
        default=None,
        description="Cline CLI timeout in seconds.",
    )


class ClinePatched(TBBaseAgent):
    """Cline-patched harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Cline reads files, writes files, executes
    commands, and iterates on fixes — all via its built-in tool-use cycle.
    """

    capabilities: ClassVar = AgentCapabilities()  # no special capabilities

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = ClinePatchedOptions.model_validate(kwargs) if kwargs else ClinePatchedOptions()
        self._cline_version = opts.cline_version or "latest"
        self._data_dir = opts.data_dir or "/tmp/cline_tb_data"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "cline-patched"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Cline CLI inside the Docker container via npm."""
        await self._install_node(environment)
        ver = self._cline_version
        await self.exec_as_root(
            environment,
            command=f"npm install -g @anthropic-ai/cline@{ver} 2>&1 | tail -5",
        )
        # Verify installation
        result = await environment.exec(command="cline --version")
        if result.return_code != 0:
            raise RuntimeError(f"Cline install failed: {result.stderr}")
        self._version = result.stdout.strip()

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Cline headlessly with the task instruction.

        Preserves native tool loop: Cline's --json mode outputs each tool call
        and result, which we capture into the trajectory.
        """
        cwd = str(environment.default_working_dir or "/root")
        cmd = (
            f"cline -c {shlex.quote(cwd)} "
            f"--data-dir {shlex.quote(self._data_dir)} "
            f"-P openai -m {shlex.quote(self._tb_model)} "
            f"-k {shlex.quote(self._tb_api_key)} "
            f"--auto-approve true --json "
            f"{shlex.quote(instruction)}"
        )
        env = self._env_for_harness()
        env_str = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())

        result = await environment.exec(
            command=f"{env_str} {cmd}",
            timeout=self._timeout,
        )

        # Populate context with results
        context.trajectory_stdout = result.stdout or ""
        context.trajectory_stderr = result.stderr or ""
        context.exit_code = result.return_code

        if result.return_code != 0:
            raise RuntimeError(
                f"Cline-patched exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
