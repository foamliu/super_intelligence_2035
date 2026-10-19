"""Claude-Code adapter for Terminal-Bench 2.0.

Preserves the native Claude-Code tool loop (shell / file edits / multi-turn).
Uses bun to run the Claude-Code CLI from source, same as SWE-bench
ClaudeCodeDriver.

Install: clone + bun install (or npm install -g @anthropic-ai/claude-code)
Run:     claude --print --dangerously-skip-permissions --model kimi-k2.6-cloud \
             --max-turns 50 <instruction>
"""

from __future__ import annotations

import shlex
from typing import Annotated, Any, Literal, override

from pydantic import Field

from harbor.agents.options import Cli, Env, InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from terminalbench.agents._base import (
    TBBaseAgent,
    TB_AGENT_TIMEOUT,
    TB_DUMMY_KEY,
    TB_GW_PROXY_BASE,
    TB_GW_PROXY_URL,
    TB_MODEL,
)


class ClaudeCodeTBOptions(InstalledAgentOptions):
    """Options for the Claude-Code Terminal-Bench adapter."""

    max_turns: Annotated[
        int | None,
        Cli("--max-turns", fallback="CLAUDE_CODE_TB_MAX_TURNS"),
    ] = Field(
        default=50,
        description="Maximum agent turns.",
    )
    permission_mode: Annotated[
        Literal["default", "acceptEdits", "plan", "auto", "bypassPermissions"] | None,
        Cli("--permission-mode"),
    ] = Field(
        default="bypassPermissions",
        description="Claude-Code permission mode.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="CLAUDE_CODE_TB_TIMEOUT"),
    ] = Field(default=None, description="Claude-Code timeout in seconds.")


class ClaudeCodeTB(TBBaseAgent):
    """Claude-Code harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Claude-Code's --print mode iterates through
    tool calls (bash, file edit, search) autonomously.
    Telemetry and auto-updater are disabled for reproducibility.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(ClaudeCodeTBOptions, kwargs)
        self._max_turns = opts.max_turns or 50
        self._permission_mode = opts.permission_mode or "bypassPermissions"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "claude-code"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Claude-Code CLI inside the Docker container via npm."""
        await self._install_node(environment)
        await self.exec_as_root(
            environment,
            command="npm install -g @anthropic-ai/claude-code 2>&1 | tail -5",
        )
        result = await environment.exec(command="claude --version 2>&1 || true")
        self._version = result.stdout.strip() or "unknown"

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Claude-Code headlessly with the task instruction."""
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")
        cmd = (
            f"cd {shlex.quote(cwd)} && "
            f"claude --print "
            f"--dangerously-skip-permissions "
            f"--model {shlex.quote(self._tb_model)} "
            f"--max-turns {self._max_turns} "
            f"--permission-mode {shlex.quote(self._permission_mode)} "
            f"{shlex.quote(instruction)}"
        )
        # Route through the local gw_proxy: claude-code speaks the Anthropic
        # protocol (/v1/messages); gw_proxy translates Anthropic->OpenAI chat,
        # rewrites developer->system, and injects the real key.  ANTHROPIC_BASE_URL
        # is the proxy HOST root (no /v1) — the SDK appends /v1/messages itself.
        env = self._env_for_harness(extra={
            "ANTHROPIC_BASE_URL": TB_GW_PROXY_BASE,
            "ANTHROPIC_API_KEY": TB_DUMMY_KEY,
            "OPENAI_API_KEY": TB_DUMMY_KEY,
            "OPENAI_BASE_URL": TB_GW_PROXY_URL,
            "CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC": "1",
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
            "DISABLE_AUTOUPDATER": "1",
            "DISABLE_BUG_COMMAND": "1",
            "DISABLE_NON_ESSENTIAL_MODEL_CALLS": "1",
            "CLAUDE_CODE_ENABLE_TELEMETRY": "0",
            "OTEL_METRICS_EXPORTER": "none",
            "OTEL_LOGS_EXPORTER": "none",
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
                f"Claude-Code exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
