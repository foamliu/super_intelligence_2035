"""Codex adapter for Terminal-Bench 2.0.

Preserves the native Codex CLI tool loop (shell / file edits / multi-turn).
Uses ``codex exec`` for headless execution, same as SWE-bench CodexDriver.

Install: npm install -g @openai/codex@0.94.0 (pinned for chat API compat)
Run:     codex exec --cd <cwd> --model kimi-k2.6-cloud \
             --sandbox workspace-write --skip-git-repo-check --json <instruction>
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
    TB_GW_PROXY_URL,
    TB_MODEL,
)


class CodexTBOptions(InstalledAgentOptions):
    """Options for the Codex Terminal-Bench adapter."""

    codex_version: Annotated[
        str | None,
        Cli("--codex-version", fallback="CODEX_TB_VERSION"),
    ] = Field(
        default="0.94.0",
        description="npm version of @openai/codex (pinned for chat API compat).",
    )
    sandbox: Annotated[
        str | None,
        Cli("--sandbox"),
    ] = Field(
        default="workspace-write",
        description="Codex sandbox mode.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="CODEX_TB_TIMEOUT"),
    ] = Field(default=None, description="Codex timeout in seconds.")


class CodexTB(TBBaseAgent):
    """Codex harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Codex's exec mode iterates through
    shell commands and file edits autonomously.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(CodexTBOptions, kwargs)
        self._codex_version = opts.codex_version or "0.94.0"
        self._sandbox = opts.sandbox or "workspace-write"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "codex"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Codex CLI inside the Docker container via npm."""
        await self._install_node(environment)
        await self.exec_as_root(
            environment,
            command=f"npm install -g @openai/codex@{self._codex_version} 2>&1 | tail -5",
        )
        result = await environment.exec(command="codex --version")
        if result.return_code != 0:
            raise RuntimeError(f"Codex install failed: {result.stderr}")
        self._version = result.stdout.strip()

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Codex headlessly with the task instruction."""
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")
        cmd = (
            f"codex exec --cd {shlex.quote(cwd)} "
            f"--model {shlex.quote(self._tb_model)} "
            f"--sandbox {shlex.quote(self._sandbox)} "
            f"--skip-git-repo-check --json "
            f"{shlex.quote(instruction)}"
        )
        # Route through the local gw_proxy (127.0.0.1:9090/v1): it rewrites
        # codex's `role:"developer"` -> `system` (gateway 422s on developer) and
        # injects the real key.  Mirrors SWE-bench CodexDriver (run_harness.py).
        env = self._env_for_harness(extra={
            "OPENAI_API_KEY": TB_DUMMY_KEY,
            "OPENAI_BASE_URL": TB_GW_PROXY_URL,
        })

        result = await environment.exec(
            command=cmd,
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
                f"Codex exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
