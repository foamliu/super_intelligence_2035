"""Shared base class for Terminal-Bench 7-harness adapters.

Common configuration:
  - Model: kimi-k2.6-cloud
  - Gateway: http://agi-gateway.cxmt.com/cloud/v1
  - API key: passed via env TB_API_KEY (never hardcoded; sourced from doc/keys.txt)
  - All harnesses run headlessly inside Harbor Docker containers.

Design principles (per BAIZE_HARNESS_TASK.md §②):
  - Each adapter preserves the native tool loop of its harness.
  - NO "one generic shell agent pretending to be 7".
  - NO "just swap system prompt" — each adapter uses the harness's real CLI.
"""

from __future__ import annotations

import os
import shlex
from pathlib import Path, PurePosixPath
from typing import Any, ClassVar, override

from harbor.agents.base import BaseAgent
from harbor.agents.capabilities import AgentCapabilities
from harbor.agents.installed.base import (
    BaseInstalledAgent,
    NonZeroAgentExitCodeError,
)
from harbor.agents.model_connection import (
    ModelConnectionSpec,
    ResolvedModelConnection,
)
from harbor.agents.options import Cli, Env, InstalledAgentOptions
from harbor.environments.base import BaseEnvironment
from harbor.models.agent.context import AgentContext

# ---------------------------------------------------------------------------
# Shared constants
# ---------------------------------------------------------------------------

#: Model name used across all 7 harnesses (same as SWE-bench 7×300).
TB_MODEL = os.environ.get("TB_MODEL", "kimi-k2.6-cloud")

#: Gateway base URL (kimi-k2.6-cloud endpoint per doc/keys.txt).
TB_BASE_URL = os.environ.get("TB_BASE_URL", "http://agi-gateway.cxmt.com/cloud/v1")

#: API key — MUST be set via env (sourced from doc/keys.txt at launch time).
#: Adapters never hardcode the key; reports must not print it.
TB_API_KEY = os.environ.get("TB_API_KEY", "")

#: Dummy key for harnesses that route through a local proxy (proxy injects real key).
TB_DUMMY_KEY = "dummy-key-for-proxy"

#: Harbor agent working directory inside the container (where the task repo lives).
TB_AGENT_CWD = PurePosixPath("/root")

#: Node.js version for harnesses that need it (cline, pi, claude-code, opencode).
TB_NODE_VERSION = "22"

#: Timeout for agent execution inside the container (seconds).
TB_AGENT_TIMEOUT = int(os.environ.get("TB_AGENT_TIMEOUT", "1800"))


class TBBaseAgent(BaseInstalledAgent):
    """Shared base for all 7 Terminal-Bench harness adapters.

    Subclasses MUST override:
      - ``name()`` — static method returning the harness identifier
      - ``install()`` — install the harness CLI inside the Docker container
      - ``run()`` — execute the harness CLI headlessly with the task instruction
    """

    #: All TB adapters share the same model connection spec.
    MODEL_CONNECTION: ClassVar[ModelConnectionSpec | None] = ModelConnectionSpec(
        kind="openai",
        base_url=TB_BASE_URL,
        api_key_env="TB_API_KEY",
        model_name=TB_MODEL,
    )

    capabilities: ClassVar[AgentCapabilities] = AgentCapabilities()

    DEFAULT_SETUP_TIMEOUT_SEC: ClassVar[float] = 600.0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._tb_model = TB_MODEL
        self._tb_base_url = TB_BASE_URL
        self._tb_api_key = TB_API_KEY or TB_DUMMY_KEY

    # -- Helpers available to subclasses ----------------------------------

    def _env_for_harness(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Build the env dict that all harness CLIs need to reach the model."""
        env: dict[str, str] = {
            "OPENAI_API_KEY": self._tb_api_key,
            "OPENAI_BASE_URL": self._tb_base_url,
            "TB_MODEL": self._tb_model,
            "TB_BASE_URL": self._tb_base_url,
            # Disable telemetry / auto-update to keep runs reproducible
            "DISABLE_TELEMETRY": "1",
            "DISABLE_ERROR_REPORTING": "1",
            "DISABLE_AUTOUPDATER": "1",
            "DO_NOT_TRACK": "1",
        }
        if extra:
            env.update(extra)
        return env

    async def _exec_in_container(
        self,
        environment: BaseEnvironment,
        command: str,
        *,
        user: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        """Execute a command inside the Docker container and return the result."""
        return await environment.exec(
            command=command,
            user=user,
            timeout=timeout or TB_AGENT_TIMEOUT,
        )

    async def _install_node(self, environment: BaseEnvironment) -> None:
        """Install Node.js via NVM inside the Docker container.

        Uses the aliyun Node.js mirror (NVM_NODEJS_ORG_MIRROR) and proxy
        env vars set by the Docker overlay (--extra-docker-compose).
        The MITM proxy requires ``-k`` (skip TLS verification).

        Replaces the old nodesource.com approach which is blocked by the
        MITM proxy (302→disable.htm for external apt repos).
        """
        nvm_version = "v0.40.1"
        nvm_url = (
            f"https://raw.githubusercontent.com/nvm-sh/nvm/{nvm_version}/install.sh"
        )
        await self.exec_as_root(
            environment,
            command=(
                f'export NVM_NODEJS_ORG_MIRROR="${{NVM_NODEJS_ORG_MIRROR:-https://mirrors.aliyun.com/nodejs-release}}" && '
                f"curl -kfsSL {nvm_url} | bash && "
                f". /root/.nvm/nvm.sh && "
                f"nvm install {TB_NODE_VERSION} && "
                f"nvm alias default {TB_NODE_VERSION} && "
                f"nvm use default && "
                f'ln -sf "$(which node)" /usr/local/bin/node && '
                f'ln -sf "$(which npm)" /usr/local/bin/npm && '
                f'ln -sf "$(which npx)" /usr/local/bin/npx'
            ),
        )

    async def _install_bun(self, environment: BaseEnvironment) -> None:
        """Install Bun runtime (needed by cline, pi).

        Uses proxy env vars set by the Docker overlay; ``-k`` skips TLS
        verification for the MITM proxy.
        """
        await self.exec_as_agent(
            environment,
            command="curl -kfsSL https://bun.sh/install | bash",
        )

    # -- Abstract methods (subclasses must implement) ---------------------

    @staticmethod
    @override
    def name() -> str:
        raise NotImplementedError("Subclass must implement name()")

    @override
    def version(self) -> str | None:
        return self._version or "skeleton-0.1.0"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        raise NotImplementedError("Subclass must implement install()")

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        raise NotImplementedError("Subclass must implement run()")
