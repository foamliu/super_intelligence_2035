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
        self._max_turns = opts.max_turns or 80  # FIX R492: was 50 → 18/34 trials hit "Reached max turns (50)"; bump to 80.
        self._permission_mode = opts.permission_mode or "bypassPermissions"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "claude-code"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Claude-Code CLI inside the Docker container.

        Priority 1 — use a pre-mounted @anthropic-ai/claude-code npm package at
        ``/opt/claude-modules/@anthropic-ai/claude-code`` (read-only volume from
        the host's npm-global, injected by the Docker overlay).  claude.exe is a
        native ELF binary (245 MB, needs only glibc — no Node.js required).  We
        symlink it to /usr/local/bin/claude.  This avoids the npm install
        timeout that blocked Gen5 (R458, 2026-10-19).

        Priority 2 — fall back to ``npm install -g @anthropic-ai/claude-code``
        (slow, may time out via MITM proxy).

        Also creates a non-root user ``agent``: Claude-Code refuses
        ``--dangerously-skip-permissions`` when run as root/sudo ("cannot be used
        with root/sudo privileges" — Gen4 root cause, 2026-10-19).  ``run()``
        then executes the CLI as that user via ``environment.exec(user=...)``
        (harbor BaseEnvironment.exec supports ``user=`` — confirmed
        harbor/environments/base.py:1186).
        """
        await self._install_node(environment)

        # Fast path: overlay already mounted the claude-code npm package.
        check = await environment.exec(
            command="test -f /opt/claude-modules/@anthropic-ai/claude-code/bin/claude.exe && echo yes || echo no"
        )
        if check.return_code == 0 and "yes" in (check.stdout or ""):
            await self.exec_as_root(
                environment,
                command=(
                    "ln -sf /opt/claude-modules/@anthropic-ai/claude-code/bin/claude.exe /usr/local/bin/claude && "
                    # claude.exe is already executable from the npm install; the NFS
                    # mount is read-only so chmod +x would fail with EROFS.
                    "claude --version 2>&1 || true"
                ),
            )
            result = await environment.exec(command="claude --version 2>&1 || true")
            self._version = result.stdout.strip() or "unknown"
        else:
            # Fallback: npm install (slow, may time out).
            await self.exec_as_root(
                environment,
                command="npm install -g @anthropic-ai/claude-code 2>&1 | tail -5",
            )
            result = await environment.exec(command="claude --version 2>&1 || true")
            self._version = result.stdout.strip() or "unknown"

        # Create a non-root user for running claude (idempotent).  -m creates
        # /home/agent so HOME is a real writable dir for claude's config/cache.
        await self.exec_as_root(
            environment,
            command="useradd -m -s /bin/bash agent 2>/dev/null || true",
        )

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Claude-Code headlessly with the task instruction.

        Runs as the non-root ``agent`` user (created in ``install``): Claude-Code
        refuses ``--dangerously-skip-permissions`` under root/sudo.  The task
        workdir is chowned to ``agent`` first so claude's bash/file tools can
        read & write the repo, then the CLI is invoked via
        ``environment.exec(user="agent")``.
        """
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")
        # Grant the non-root agent user ownership of the workdir so claude's
        # bash/edit tools can operate on the task repo (otherwise cd/edits fail
        # with EACCES).  Best-effort: if the path doesn't exist yet, claude will
        # create what it needs under /home/agent.
        # FIX (2026-10-25, R492): also chown/chmod /app — many TB tasks require
        # the solution to be written to /app/<file>, but /app is root-owned and
        # claude runs as the non-root `agent` user → "permission issue writing
        # to /app/" on 13/34 exit-0 trials (model reasoned correctly but could
        # not produce the deliverable → 0 pass).  Make /app writable by agent.
        await self.exec_as_root(
            environment,
            command=(
                f"chown -R agent {shlex.quote(cwd)} 2>/dev/null || true; "
                f"chown -R agent /app 2>/dev/null || true; "
                f"chmod -R a+rwX /app 2>/dev/null || true"
            ),
        )
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
            # claude runs as user "agent" -> its $HOME is /home/agent (created by
            # useradd -m in install).  Pin HOME so config/cache land there.
            "HOME": "/home/agent",
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
            user="agent",
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
