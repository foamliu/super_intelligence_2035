"""Hermes adapter for Terminal-Bench 2.0.

Preserves the native Hermes-agent tool loop (shell / file ops / multi-turn).
Uses ``hermes -z <prompt>`` oneshot mode, same as SWE-bench HermesDriver.

Install: uv pip install hermes-agent (from NousResearch/hermes-agent)
Run:     hermes -z<instruction> --provider kimi-proxy --model kimi-k2.6-cloud --yolo
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


class HermesTBOptions(InstalledAgentOptions):
    """Options for the Hermes Terminal-Bench adapter."""

    max_turns: Annotated[
        int | None,
        Cli("--max-turns", fallback="HERMES_TB_MAX_TURNS"),
    ] = Field(
        default=50,
        description="Maximum agent turns for Hermes.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="HERMES_TB_TIMEOUT"),
    ] = Field(default=None, description="Hermes timeout in seconds.")


class HermesTB(TBBaseAgent):
    """Hermes harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Hermes's oneshot mode iterates through
    tool calls (shell, file edit) autonomously until done or max_turns.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(HermesTBOptions, kwargs)
        self._max_turns = opts.max_turns or 50
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "hermes"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Hermes-agent inside the Docker container via pip."""
        # Install Python 3.12+ if not present, then hermes-agent
        await self.exec_as_root(
            environment,
            command=(
                "pip install --break-system-packages hermes-agent 2>&1 | tail -5"
            ),
        )
        result = await environment.exec(command="hermes --version 2>&1 || true")
        self._version = result.stdout.strip() or "unknown"

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Hermes headlessly with the task instruction.

        Uses -z (oneshot) mode: the prompt immediately follows -z with no
        space, so argparse does not swallow subsequent flags.
        """
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")
        # Write a config file for the kimi provider, routed through the local
        # gw_proxy (rewrites developer->system, injects the real key).
        config_content = (
            f"provider:\n"
            f"  kimi-proxy:\n"
            f"    base_url: {TB_GW_PROXY_URL}\n"
            f"    api_key: {TB_DUMMY_KEY}\n"
            f"    api_mode: chat_completions\n"
            f"agent:\n"
            f"  max_turns: {self._max_turns}\n"
        )
        await self._upload_agent_config(
            environment, config_content, "/root/.hermes/config.yaml", "config.yaml"
        )

        # -z must immediately precede the prompt (no space)
        cmd = (
            f"cd {shlex.quote(cwd)} && "
            f"hermes -z{shlex.quote(instruction)} "
            f"--provider kimi-proxy --model {shlex.quote(self._tb_model)} "
            f"--yolo"
        )
        env = self._env_for_harness(extra={
            # Route through the local gw_proxy: rewrites developer->system and
            # injects the real key.  hermes may read OPENAI_* env in addition to
            # the config file, so point both at the proxy.
            "OPENAI_API_KEY": TB_DUMMY_KEY,
            "OPENAI_BASE_URL": TB_GW_PROXY_URL,
            "no_proxy": "127.0.0.1,localhost",
            "NO_PROXY": "127.0.0.1,localhost",
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
                f"Hermes exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )

    async def _upload_agent_config(
        self,
        environment: BaseEnvironment,
        content: str,
        remote_path: str,
        filename: str,
    ) -> None:
        """Upload a config file into the container."""
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=f"_{filename}", delete=False) as f:
            f.write(content)
            local_path = Path(f.name)
        await environment.upload_file(local_path, remote_path)
