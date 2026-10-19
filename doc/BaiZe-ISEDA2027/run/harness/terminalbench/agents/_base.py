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

#: Local gw_proxy base URL (OpenAI chat completions).  gw_proxy
#: (harness_work/gw_proxy.py) sits in front of the harnesses and (1) rewrites
#: ``role:"developer"`` -> ``role:"system"`` — the internal gateway only accepts
#: system/user/assistant and 422s on ``developer`` (codex/opencode/hermes emit
#: it for reasoning models); (2) injects the real gateway key from GW_API_KEY so
#: harnesses hold only a dummy secret; (3) translates Anthropic /v1/messages ->
#: OpenAI chat (for claude-code).  Mirrors the proven SWE-bench 7x300 driver
#: (run_harness.py: CodexDriver/OpenCodeDriver/... all use DUMMY_KEY + 127.0.0.1).
#: Started on the host by launch_tb_7way.sh; TB containers use network_mode:
#: host, so 127.0.0.1:9090 in-container == the host proxy.
TB_GW_PROXY_URL = os.environ.get("TB_GW_PROXY_URL", "http://127.0.0.1:9090/v1")

#: gw_proxy host root (no /v1) — the Anthropic SDK appends /v1/messages itself.
TB_GW_PROXY_BASE = os.environ.get("TB_GW_PROXY_BASE", "http://127.0.0.1:9090")

#: gw_proxy_dsh base URL (port 9091) — additionally strips DeepSeek-specific
#: params (reasoning_effort / thinking / dsh_plugin_packages / ...) that the
#: gateway rejects, and caps max_tokens at 8192.
TB_GW_DSH_URL = os.environ.get("TB_GW_DSH_URL", "http://127.0.0.1:9091/v1")

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
    # harbor 0.24.0 ModelConnectionSpec fields: default_provider, api_key_envs
    # (tuple), base_url_envs (tuple), passthrough.  We use the "openai"
    # provider (OpenAI-compatible gateway) with our custom env names so harbor
    # can locate the key/URL; the adapter's run() also sets OPENAI_API_KEY /
    # OPENAI_BASE_URL explicitly for the harness CLI.
    MODEL_CONNECTION: ClassVar[ModelConnectionSpec | None] = ModelConnectionSpec(
        default_provider="openai",
        api_key_envs=("TB_API_KEY",),
        base_url_envs=("TB_BASE_URL",),
    )

    capabilities: ClassVar[AgentCapabilities] = AgentCapabilities()

    DEFAULT_SETUP_TIMEOUT_SEC: ClassVar[float] = 600.0

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._tb_model = TB_MODEL
        self._tb_base_url = TB_BASE_URL
        self._tb_api_key = TB_API_KEY or TB_DUMMY_KEY
        # Stash extra_env from harbor (model credentials may be injected here)
        # so subclasses can merge them into the harness CLI env if desired.
        self._harbor_extra_env: dict[str, str] = kwargs.get("extra_env") or {}

    @staticmethod
    def _opts(options_cls: type, kwargs: dict[str, Any]):
        """Validate adapter-specific options, ignoring harbor's extra kwargs.

        Harbor passes ``logs_dir``, ``model_name``, ``extra_env``, ``logger``,
        ``config``, ``prompt_template_path`` etc. to ``__init__``.  The pydantic
        Options models forbid extras by default, so we filter to known fields
        before validation.
        """
        if not kwargs:
            return options_cls()
        known = {
            k: v for k, v in kwargs.items() if k in options_cls.model_fields
        }
        return options_cls.model_validate(known)

    # -- Helpers available to subclasses ----------------------------------

    def _env_for_harness(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        """Build the env dict that all harness CLIs need to reach the model.

        The Docker overlay sets HTTP_PROXY/HTTPS_PROXY for apt/npm installs,
        but the model gateway (agi-gateway.cxmt.com) is on the internal network
        (10.128.246.174) and must NOT go through the MITM proxy — the proxy
        corrupts streaming API responses.  We extend NO_PROXY to include the
        gateway hostname so harness CLIs connect directly.
        """
        # Derive the gateway hostname from TB_BASE_URL for NO_PROXY.
        gateway_host = self._tb_base_url
        # Strip scheme
        if "://" in gateway_host:
            gateway_host = gateway_host.split("://", 1)[1]
        # Strip path
        gateway_host = gateway_host.split("/", 1)[0]
        # Strip port
        gateway_host = gateway_host.split(":", 1)[0]

        no_proxy_val = (
            f"localhost,127.0.0.1,10.239.*,172.19.*,{gateway_host}"
        )

        env: dict[str, str] = {
            "OPENAI_API_KEY": self._tb_api_key,
            "OPENAI_BASE_URL": self._tb_base_url,
            "TB_MODEL": self._tb_model,
            "TB_BASE_URL": self._tb_base_url,
            # Bypass the MITM proxy for model API calls (gateway is internal).
            "NO_PROXY": no_proxy_val,
            "no_proxy": no_proxy_val,
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
            timeout_sec=int(timeout or TB_AGENT_TIMEOUT),
        )

    async def _install_node(self, environment: BaseEnvironment) -> None:
        """Make Node.js available inside the Docker container.

        Priority 1 — use a pre-mounted Node.js at ``/opt/node`` (read-only
        volume injected by the Docker overlay, e.g.
        ``/tmp/node-preinstalled/node-v22...:/opt/node:ro``).  This avoids any
        network download and is the fast path used by the TB overlay.

        Priority 2 — fall back to an NVM install (aliyun mirror + MITM proxy
        with ``-k``).  Used when no pre-mounted node is available.
        """
        # Fast path: overlay already mounted node at /opt/node.
        check = await environment.exec(
            command="test -x /opt/node/bin/node && echo yes || echo no"
        )
        if check.return_code == 0 and "yes" in (check.stdout or ""):
            await self.exec_as_root(
                environment,
                command=(
                    "ln -sf /opt/node/bin/node /usr/local/bin/node && "
                    "ln -sf /opt/node/bin/npm /usr/local/bin/npm && "
                    "ln -sf /opt/node/bin/npx /usr/local/bin/npx && "
                    # /opt/node is mounted read-only, so npm install -g (which
                    # writes to /opt/node/lib/node_modules) fails with ENOENT.
                    # Redirect the global prefix to /usr/local (writable).
                    "mkdir -p /usr/local/lib/node_modules && "
                    "npm config set prefix /usr/local && "
                    "node --version && npm --version"
                ),
            )
            return

        # Fallback: NVM install.
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
