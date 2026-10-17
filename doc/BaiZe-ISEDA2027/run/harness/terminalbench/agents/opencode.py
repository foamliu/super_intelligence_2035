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

from terminalbench.agents._base import TBBaseAgent, TB_AGENT_TIMEOUT, TB_MODEL


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
        opts = OpenCodeTBOptions.model_validate(kwargs) if kwargs else OpenCodeTBOptions()
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
        """Install OpenCode binary inside the Docker container."""
        # OpenCode is a single binary; download from GitHub releases
        await self.exec_as_root(
            environment,
            command=(
                f"curl -fsSL https://opencode.ai/install | bash 2>&1 | tail -5"
            ),
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
        cwd = str(environment.default_working_dir or "/root")

        # Write opencode config with gw provider pointing at the gateway
        config_content = (
            f'{{\n'
            f'  "provider": {{\n'
            f'    "gw": {{\n'
            f'      "type": "openai-compatible",\n'
            f'      "baseURL": "{self._tb_base_url}",\n'
            f'      "models": {{\n'
            f'        "{self._tb_model}": {{ "name": "{self._tb_model}" }}\n'
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
        env = self._env_for_harness()
        env_str = " ".join(f"{k}={shlex.quote(v)}" for k, v in env.items())

        result = await environment.exec(
            command=f"{env_str} {cmd}",
            timeout=self._timeout,
        )

        context.trajectory_stdout = result.stdout or ""
        context.trajectory_stderr = result.stderr or ""
        context.exit_code = result.return_code

        if result.return_code != 0:
            raise RuntimeError(
                f"OpenCode exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
