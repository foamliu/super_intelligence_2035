"""Pi adapter for Terminal-Bench 2.0.

Preserves the native Pi coding-agent tool loop (shell / file edits /
multi-turn).  Uses ``pi -p`` print mode via bun, same as SWE-bench
PiDriver.

Install: npm install -g @fleetagent/pi-coding-agent (requires Node >=22)
Run:     pi -p --provider gw --model kimi-k2.6-cloud --api-key <key> <instruction>
"""

from __future__ import annotations

import shlex
from typing import Annotated, Any, override

from pydantic import Field

from harbor.agents.options import Cli, InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

from terminalbench.agents._base import TBBaseAgent, TB_AGENT_TIMEOUT, TB_MODEL


class PiTBOptions(InstalledAgentOptions):
    """Options for the Pi Terminal-Bench adapter."""

    pi_version: Annotated[
        str | None,
        Cli("--pi-version", fallback="PI_TB_VERSION"),
    ] = Field(
        default=None,
        description="npm version of @fleetagent/pi-coding-agent.",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="PI_TB_TIMEOUT"),
    ] = Field(default=None, description="Pi timeout in seconds.")


class PiTB(TBBaseAgent):
    """Pi harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Pi's print mode (-p) processes the prompt
    and iterates through tool calls autonomously, then exits.
    Provider/model come from ~/.pi/agent/models.json (gw provider → gateway).
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(PiTBOptions, kwargs)
        self._pi_version = opts.pi_version or "latest"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "pi"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Pi coding-agent inside the Docker container via npm."""
        await self._install_node(environment)
        await self.exec_as_root(
            environment,
            command=(
                f"npm install -g --ignore-scripts "
                f"@fleetagent/pi-coding-agent@{self._pi_version} 2>&1 | tail -5"
            ),
        )
        result = await environment.exec(
            command="pi --version 2>&1 || node $(npm root -g)/@fleetagent/pi-coding-agent/dist/cli.js --version 2>&1 || true"
        )
        self._version = result.stdout.strip() or "unknown"

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Pi headlessly with the task instruction."""
        cwd = str(environment.default_working_dir or "/root")

        # Write models.json with gw provider pointing at the gateway
        models_config = (
            f'{{\n'
            f'  "providers": {{\n'
            f'    "gw": {{\n'
            f'      "baseURL": "{self._tb_base_url}",\n'
            f'      "api": "openai-completions",\n'
            f'      "compat": {{ "supportsDeveloperRole": false }}\n'
            f'    }}\n'
            f'  }}\n'
            f'}}\n'
        )
        from pathlib import Path
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix="_models.json", delete=False) as f:
            f.write(models_config)
            config_local = Path(f.name)
        await environment.upload_file(config_local, "/root/.pi/agent/models.json")

        # Try pi directly, fall back to node cli.js
        cmd = (
            f"cd {shlex.quote(cwd)} && "
            f"(pi -p --provider gw --model {shlex.quote(self._tb_model)} "
            f"--api-key {shlex.quote(self._tb_api_key)} "
            f"{shlex.quote(instruction)}) || "
            f"(node $(npm root -g)/@fleetagent/pi-coding-agent/dist/cli.js "
            f"-p --provider gw --model {shlex.quote(self._tb_model)} "
            f"--api-key {shlex.quote(self._tb_api_key)} "
            f"{shlex.quote(instruction)})"
        )
        env = self._env_for_harness(extra={
            "PI_OFFLINE": "1",
            "PI_SKIP_VERSION_CHECK": "1",
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
                f"Pi exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
