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

import json
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
        opts = self._opts(ClinePatchedOptions, kwargs)
        self._cline_version = opts.cline_version or "latest"
        self._data_dir = opts.data_dir or "/tmp/cline_tb_data"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "cline-patched"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Cline CLI inside the Docker container.

        Priority 1 — use a pre-mounted Cline at ``/opt/cline-modules`` (read-only
        volume from the host's ``~/.bun/install/global/node_modules``, injected
        by the Docker overlay).  The platform-specific ELF binary at
        ``@cline/cli-linux-x64/bin/cline`` has Bun embedded and only needs
        glibc, so no Node.js or npm install is required.  This avoids the
        6+ minute npm dependency-tree download inside the container.

        Priority 2 — fall back to ``npm install -g cline`` (slow, ~6 min).
        Uses a LOCAL cache (``/tmp/npm-cache-cline``) to avoid cross-device
        hardlink (EXDEV) failures on NFS-mounted ``/root/.npm/_cacache``.
        """
        await self._install_node(environment)

        # Fast path: overlay already mounted cline at /opt/cline-modules.
        check = await environment.exec(
            command=(
                "test -f /opt/cline-modules/@cline/cli-linux-x64/bin/cline "
                "&& echo yes || echo no"
            ),
        )
        if check.return_code == 0 and "yes" in (check.stdout or ""):
            await self.exec_as_root(
                environment,
                command=(
                    "ln -sf /opt/cline-modules/@cline/cli-linux-x64/bin/cline "
                    "/usr/local/bin/cline && "
                    "cline --version"
                ),
            )
            result = await environment.exec(command="cline --version")
            if result.return_code != 0:
                raise RuntimeError(
                    f"Cline pre-mount check failed: {result.stderr}"
                )
            self._version = result.stdout.strip()
            return

        # Fallback: npm install (slow, ~6 min).
        # npm package is unscoped "cline" (NOT "@anthropic-ai/cline" which
        # does not exist on npm).  Cline Bot Inc. publishes as "cline".
        ver = self._cline_version
        await self.exec_as_root(
            environment,
            command=(
                f"echo '--- npm config ---' && "
                f"npm config get registry && "
                f"npm config get strict-ssl && "
                f"echo '--- env proxy ---' && "
                f"env | grep -iE 'proxy|npm_config' | head -10 && "
                f"npm install -g cline@{ver} --cache /tmp/npm-cache-cline 2>&1 || "
                f"  (echo '=== NPM DEBUG LOG ===' && "
                f"   cat /root/.npm/_logs/*debug*.log 2>/dev/null | tail -40 && "
                f"   exit 1)"
            ),
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
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")

        # Pre-create providers.json with baseUrl so cline's openai-compatible
        # provider knows where to send API requests.  Cline does NOT read
        # OPENAI_BASE_URL from env (confirmed: 0 occurrences in source).
        # Without baseUrl in providers.json, cline defaults to api.openai.com
        # or api.cline.bot, which fails with our kimi-k2.6-cloud key.
        providers_json = json.dumps({
            "version": 1,
            "lastUsedProvider": "openai-compatible",
            "modes": {},
            "providers": {
                "openai-compatible": {
                    "settings": {
                        "provider": "openai-compatible",
                        "apiKey": self._tb_api_key,
                        "model": self._tb_model,
                        "baseUrl": self._tb_base_url,
                    },
                    "tokenSource": "manual",
                },
            },
        })
        setup_cmd = (
            f"mkdir -p {shlex.quote(self._data_dir)}/settings && "
            f"printf '%s' {shlex.quote(providers_json)} > "
            f"{shlex.quote(self._data_dir)}/settings/providers.json"
        )
        await environment.exec(command=setup_cmd)

        cmd = (
            f"cline -c {shlex.quote(cwd)} "
            f"--data-dir {shlex.quote(self._data_dir)} "
            f"-P openai -m {shlex.quote(self._tb_model)} "
            f"-k {shlex.quote(self._tb_api_key)} "
            f"--auto-approve true --json "
            f"{shlex.quote(instruction)}"
        )
        env = self._env_for_harness()

        result = await environment.exec(
            command=cmd,
            env=env,
            timeout_sec=self._timeout,
        )

        # Populate context with results
        context.metadata = {
            "stdout": result.stdout or "",
            "stderr": result.stderr or "",
            "exit_code": result.return_code,
        }

        if result.return_code != 0:
            raise RuntimeError(
                f"Cline-patched exited with code {result.return_code}: "
                f"{(result.stderr or '')[:500]}"
            )
