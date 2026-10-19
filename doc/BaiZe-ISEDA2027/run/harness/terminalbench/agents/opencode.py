"""OpenCode adapter for Terminal-Bench 2.0.

Preserves the native OpenCode tool loop (shell / file edits / multi-turn).
Uses ``opencode run`` headless mode, same as SWE-bench OpencodeDriver.

Install: download opencode binary (v1.18.27 or latest)
Run:     opencode run --dir <cwd> --model gw/kimi-k2.6-cloud --auto <instruction>
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


class OpenCodeTBOptions(InstalledAgentOptions):
    """Options for the OpenCode Terminal-Bench adapter."""

    opencode_version: Annotated[
        str | None,
        Cli("--opencode-version", fallback="OPENCODE_TB_VERSION"),
    ] = Field(
        default=None,
        description="OpenCode binary version to install.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="OPENCODE_TB_TIMEOUT"),
    ] = Field(default=None, description="OpenCode timeout in seconds.")


class OpenCodeTB(TBBaseAgent):
    """OpenCode harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: OpenCode's run mode iterates through
    tool calls autonomously with --auto flag for non-interactive approval.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(OpenCodeTBOptions, kwargs)
        self._opencode_version = opts.opencode_version or "latest"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT
        # Provider/model format: gw/<model> per opencode.json convention
        self._opencode_model = f"gw/{self._tb_model}"

    @staticmethod
    @override
    def name() -> str:
        return "opencode"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install OpenCode inside the Docker container via npm.

        The official install script (curl | bash) downloads a binary from
        GitHub releases (github.com/anomalyco/opencode/releases), which fails
        through the MITM proxy with exit 56 (NetworkConnectionError).
        npm install -g opencode-ai is the fallback path in the official script
        and works reliably with the npmmirror registry + writable prefix set
        by _install_node.
        """
        await self._install_node(environment)
        await self.exec_as_root(
            environment,
            command="npm install -g opencode-ai 2>&1 | tail -5",
        )
        result = await environment.exec(command="opencode version 2>&1 || true")
        self._version = result.stdout.strip() or "unknown"

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run OpenCode headlessly with the task instruction."""
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")

        # Write opencode config with a `gw` provider pointing at the local
        # gw_proxy.  Schema mirrors the proven ~/.config/opencode/opencode.json
        # used by the SWE-bench 7x300 (npm @ai-sdk/openai-compatible + options).
        # gw_proxy rewrites developer->system and injects the real key.
        config_content = (
            f'{{\n'
            f'  "$schema": "https://opencode.ai/config.json",\n'
            f'  "provider": {{\n'
            f'    "gw": {{\n'
            f'      "npm": "@ai-sdk/openai-compatible",\n'
            f'      "name": "gw_proxy",\n'
            f'      "options": {{\n'
            f'        "baseURL": "{TB_GW_PROXY_URL}",\n'
            f'        "apiKey": "{TB_DUMMY_KEY}"\n'
            f'      }},\n'
            f'      "models": {{\n'
            f'        "{self._tb_model}": {{ "name": "{self._tb_model}", "tool_call": true }}\n'
            f'      }}\n'
            f'    }}\n'
            f'  }}\n'
            f'}}\n'
        )
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix="_opencode.json", delete=False) as f:
            f.write(config_content)
            config_local = Path(f.name)
        await environment.upload_file(config_local, "/root/.config/opencode/opencode.json")

        cmd = (
            f"opencode run "
            f"--dir {shlex.quote(cwd)} "
            f"--model {shlex.quote(self._opencode_model)} "
            f"--auto "
            f"{shlex.quote(instruction)}"
        )
        # Route through the local gw_proxy (developer->system rewrite + key inject).
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
                f"OpenCode exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
