"""Hermes adapter for Terminal-Bench 2.0.

Preserves the native Hermes-agent tool loop (shell / file ops / multi-turn).
Uses ``hermes -z <prompt>`` oneshot mode, same as SWE-bench HermesDriver.

Install: uv pip install hermes-agent (from NousResearch/hermes-agent)
Run:     hermes -z<instruction> --provider kimi-proxy --model kimi-k2.6-cloud --yolo

R457 (2026-10-19) — ROOT CAUSE FIX for "Unknown provider kimi-proxy":
    hermes-agent does NOT read custom providers from ``~/.hermes/config.yaml``.
    Providers are **plugins**: ``$HERMES_HOME/plugins/model-providers/<name>/``
    each containing ``__init__.py`` (which calls ``register_provider(profile)``)
    and ``plugin.yaml`` (manifest).  Writing ``provider: kimi-proxy: {...}`` into
    config.yaml is silently ignored => ``--provider kimi-proxy`` fails with
    ``Unknown provider kimi-proxy`` on all 5 trials.
    Ref: plugins/model-providers/README.md in NousResearch/hermes-agent.

    Fix: install a provider plugin into the container before running hermes, and
    point it straight at the internal gateway with the REAL key (the gateway is
    OpenAI-compatible; no gw_proxy hop needed, which also avoids the
    role:developer rewrite issue).
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

#: Name of the provider plugin we register inside the container.
HERMES_PROVIDER_NAME = "kimi-proxy"

#: Where hermes looks for user plugins (see plugins/model-providers/README.md).
HERMES_PROVIDER_PLUGIN_DIR = (
    "/root/.hermes/plugins/model-providers/" + HERMES_PROVIDER_NAME
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
        """Install hermes-agent + register the kimi-proxy provider plugin (R457)."""
        # 1) install hermes-agent.
        # FIX (2026-10-25, R492): the old `pip install ...` flaked on task images
        # where `pip` is not on PATH (36/50 trials → "hermes: command not found",
        # exit 127, 0 pass).  Use `python3 -m pip` (always available with python3),
        # make PATH explicit, then VERIFY `hermes` is callable and raise loudly if
        # not — a silent missing CLI produced 0% with no exception in install().
        await self.exec_as_root(
            environment,
            command=(
                "export PATH=/usr/local/bin:/usr/bin:$PATH && "
                "python3 -m pip install --break-system-packages hermes-agent 2>&1 | tail -5"
            ),
            timeout=900,
        )
        # Verify the console script is on PATH; retry once if missing.
        check = await environment.exec(
            command="command -v hermes || ls /usr/local/bin/hermes /usr/bin/hermes 2>/dev/null"
        )
        if "hermes" not in (check.stdout or ""):
            # Fallback: re-install with --force-reinstall and ensure console script.
            await self.exec_as_root(
                environment,
                command=(
                    "export PATH=/usr/local/bin:/usr/bin:$PATH && "
                    "python3 -m pip install --break-system-packages --force-reinstall "
                    "hermes-agent 2>&1 | tail -5"
                ),
                timeout=900,
            )
            check2 = await environment.exec(command="command -v hermes 2>&1")
            if "hermes" not in (check2.stdout or ""):
                raise RuntimeError(
                    f"Hermes CLI not found on PATH after install: "
                    f"{(check2.stdout or '')[:300]}"
                )
        result = await environment.exec(
            command="export PATH=/usr/local/bin:/usr/bin:$PATH && hermes --version 2>&1 || true"
        )
        self._version = result.stdout.strip() or "unknown"

        # 2) R457: providers must be PLUGINS, config.yaml is not read for them
        await self._install_provider_plugin(environment)

    async def _install_provider_plugin(self, environment: BaseEnvironment) -> None:
        """Write $HERMES_HOME/plugins/model-providers/kimi-proxy/{__init__.py,plugin.yaml}.

        Per plugins/model-providers/README.md, each subdirectory is a
        self-contained provider profile plugin; __init__.py must call
        register_provider(Profile).  We point straight at the internal
        OpenAI-compatible gateway with the real key.
        """
        base_url = self._tb_base_url

        init_py = (
            "from providers import register_provider\n"
            "from providers.base import ProviderProfile\n"
            "\n"
            "kimi_proxy = ProviderProfile(\n"
            f"    name={HERMES_PROVIDER_NAME!r},\n"
            "    aliases=('kimi', 'kimi-cloud'),\n"
            "    display_name='Kimi (internal gateway)',\n"
            "    description='Internal agi-gateway OpenAI-compatible endpoint',\n"
            "    env_vars=('HERMES_KIMI_API_KEY', 'HERMES_KIMI_BASE_URL'),\n"
            f"    base_url={base_url!r},\n"
            ")\n"
            "register_provider(kimi_proxy)\n"
        )
        plugin_yaml = (
            f"name: {HERMES_PROVIDER_NAME}\n"
            "kind: model-provider\n"
            "version: 1.0.0\n"
            "description: Internal agi-gateway provider for the TB 7-way benchmark\n"
            "author: BaiZe harness\n"
        )

        await environment.exec(
            command=f"mkdir -p {shlex.quote(HERMES_PROVIDER_PLUGIN_DIR)}"
        )
        await self._upload_agent_config(
            environment, init_py,
            f"{HERMES_PROVIDER_PLUGIN_DIR}/__init__.py", "provider_init.py",
        )
        await self._upload_agent_config(
            environment, plugin_yaml,
            f"{HERMES_PROVIDER_PLUGIN_DIR}/plugin.yaml", "plugin.yaml",
        )

        # non-fatal diagnostic: prove the files landed
        check = await environment.exec(
            command=f"ls -l {shlex.quote(HERMES_PROVIDER_PLUGIN_DIR)} 2>&1 | tail -4"
        )
        print(f"[hermes] provider plugin installed:\n{check.stdout or ''}")

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

        # Minimal config.yaml — providers live in the plugin dir now (R457).
        # (Writing a `provider:` block here is silently ignored by hermes-agent.)
        config_content = (
            "agent:\n"
            f"  max_turns: {self._max_turns}\n"
        )
        await self._upload_agent_config(
            environment, config_content, "/root/.hermes/config.yaml", "config.yaml"
        )

        # -z must immediately precede the prompt (no space)
        # FIX (2026-10-25, R492): export PATH so the console script (installed to
        # /usr/local/bin) is found even when the container's default PATH omits it.
        cmd = (
            f"export PATH=/usr/local/bin:/usr/bin:$PATH && "
            f"cd {shlex.quote(cwd)} && "
            f"hermes -z{shlex.quote(instruction)} "
            f"--provider {HERMES_PROVIDER_NAME} --model {shlex.quote(self._tb_model)} "
            f"--yolo"
        )
        _key = self._tb_api_key or TB_DUMMY_KEY
        # FIX (2026-10-25, R492): DO NOT override no_proxy/NO_PROXY here.  The old
        # override ("127.0.0.1,localhost,10.239.*,172.19.*") DROPPED the gateway
        # hostname agi-gateway.cxmt.com that _base._env_for_harness() adds, so
        # hermes's model requests were routed through the MITM proxy →
        # "HTTP 503 — The requested URL could not be retrieved" on 51/50 trials.
        # Leaving no_proxy unset lets _env_for_harness's correct value (which
        # includes the gateway host) win.
        env = self._env_for_harness(extra={
            # Plugin reads these (see env_vars in the ProviderProfile, R457).
            "HERMES_KIMI_API_KEY": _key,
            "HERMES_KIMI_BASE_URL": self._tb_base_url,
            # Keep OPENAI_* consistent in case hermes falls back to them.
            "OPENAI_API_KEY": _key,
            "OPENAI_BASE_URL": self._tb_base_url,
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
