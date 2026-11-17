"""Codex adapter for Terminal-Bench 2.0.

Preserves the native Codex CLI tool loop (shell / file edits / multi-turn).
Uses ``codex exec`` for headless execution, same as SWE-bench CodexDriver.

Install: npm install -g @openai/codex@0.94.0 (pinned for chat API compat)
Run:     codex exec --cd <cwd> --model kimi-k2.6-cloud \
             --sandbox danger-full-access --skip-git-repo-check --json <instruction>
"""

from __future__ import annotations

import asyncio
import json
import re
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


class CodexTBOptions(InstalledAgentOptions):
    """Options for the Codex Terminal-Bench adapter."""

    codex_version: Annotated[
        str | None,
        Cli("--codex-version", fallback="CODEX_TB_VERSION"),
    ] = Field(
        default="0.94.0",
        description="npm version of @openai/codex (pinned for chat API compat).",
    )
    sandbox: Annotated[
        str | None,
        Cli("--sandbox"),
    ] = Field(
        default="danger-full-access",
        description="Codex sandbox mode (danger-full-access: no bwrap, Docker is the sandbox).",
    )
    timeout: Annotated[
        int | None,
        Cli("--timeout", fallback="CODEX_TB_TIMEOUT"),
    ] = Field(default=None, description="Codex timeout in seconds.")


class CodexTB(TBBaseAgent):
    """Codex harness adapter for Terminal-Bench 2.0.

    Native tool loop preserved: Codex's exec mode iterates through
    shell commands and file edits autonomously.
    """

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        opts = self._opts(CodexTBOptions, kwargs)
        self._codex_version = opts.codex_version or "0.94.0"
        self._sandbox = opts.sandbox or "danger-full-access"
        self._timeout = opts.timeout or TB_AGENT_TIMEOUT

    @staticmethod
    @override
    def name() -> str:
        return "codex"

    @override
    async def install(self, environment: BaseEnvironment) -> None:
        """Install Codex CLI inside the Docker container.

        Priority 1 — use a pre-mounted @openai/codex npm package at
        ``/opt/codex-modules/@openai/codex`` (read-only volume from the host's
        npm-global, injected by the Docker overlay).  codex.js is a Node.js ES
        module that needs only the already-mounted /opt/node.  We symlink it to
        /usr/local/bin/codex and set NODE_PATH so codex.js can resolve its
        bundled node_modules.  This avoids the 6+ min npm install timeout.

        Priority 2 — fall back to ``npm install -g @openai/codex@<version>``
        (slow, may time out via MITM proxy).
        """
        await self._install_node(environment)

        # Fast path: overlay already mounted the codex npm package.
        check = await environment.exec(
            command="test -f /opt/codex-modules/@openai/codex/bin/codex.js && echo yes || echo no"
        )
        if check.return_code == 0 and "yes" in (check.stdout or ""):
            await self.exec_as_root(
                environment,
                command=(
                    "ln -sf /opt/codex-modules/@openai/codex/bin/codex.js /usr/local/bin/codex && "
                    # codex.js is already executable from the npm install; the NFS
                    # mount is read-only so chmod +x would fail with EROFS.
                    "codex --version"
                ),
            )
            result = await environment.exec(command="codex --version")
            if result.return_code != 0:
                raise RuntimeError(f"Codex pre-mounted install failed: {result.stderr}")
            self._version = result.stdout.strip()

            # Write ~/.codex/config.toml so codex routes through the local
            # gw_proxy instead of api.openai.com.  Pinned codex 0.94.0 supports
            # wire_api="chat" (the gateway only speaks /v1/chat/completions).
            # The gw_proxy rewrites role:"developer"->"system" and injects the
            # real API key.  supports_websockets=false because the gw_proxy is
            # plain HTTP (no WebSocket).
            # 2026-11-07 FIX: TB4 container has newer codex that rejects
            # wire_api="chat" ("no longer supported" error).  Reverted to
            # wire_api="responses" — the gw_proxy at 9092 translates
            # /v1/responses → /v1/chat/completions (same as SWE-bench
            # CodexDriver which works fine).
            config_toml = (
                f'model = "{TB_MODEL}"\n'
                'model_provider = "gw_proxy"\n'
                "\n"
                "[model_providers.gw_proxy]\n"
                'name = "Local gw_proxy (responses API)"\n'
                f'base_url = "{TB_GW_PROXY_URL}"\n'
                'wire_api = "responses"\n'
                'env_key = "OPENAI_API_KEY"\n'
                "requires_openai_auth = false\n"
                "supports_websockets = false\n"
            )
            await self.exec_as_root(
                environment,
                command=(
                    f"mkdir -p /root/.codex && cat > /root/.codex/config.toml <<'CODEX_EOF'\n"
                    f"{config_toml}"
                    "CODEX_EOF"
                ),
            )
            return

        # Fallback: npm install (slow, may time out).
        await self.exec_as_root(
            environment,
            command=f"npm install -g @openai/codex@{self._codex_version} 2>&1 | tail -5",
        )
        result = await environment.exec(command="codex --version")
        if result.return_code != 0:
            raise RuntimeError(f"Codex install failed: {result.stderr}")
        self._version = result.stdout.strip()

    @override
    async def run(
        self,
        instruction: str,
        environment: BaseEnvironment,
        context: AgentContext,
    ) -> None:
        """Run Codex headlessly with the task instruction."""
        _task_cfg = getattr(environment, "task_env_config", None)
        cwd = str(getattr(_task_cfg, "workdir", None) or "/root")
        cmd = (
            f"codex exec --cd {shlex.quote(cwd)} "
            f"--model {shlex.quote(self._tb_model)} "
            f"--sandbox {shlex.quote(self._sandbox)} "
            f"--skip-git-repo-check --json "
            f"{shlex.quote(instruction)}"
        )
        # Route through the local gw_proxy (127.0.0.1:9090/v1): it rewrites
        # codex's `role:"developer"` -> `system` (gateway 422s on developer) and
        # injects the real key.  Mirrors SWE-bench CodexDriver (run_harness.py).
        env = self._env_for_harness(extra={
            "OPENAI_API_KEY": TB_DUMMY_KEY,
            "OPENAI_BASE_URL": TB_GW_PROXY_URL,
        })

        # 2026-11-17 FIX (用户令 14:5x): codex 走 wire_api="responses" 经
        # gw_proxy 翻译，其请求模式触发上游 429 后 codex 内部 retry 耗尽 →
        # turn.failed → exit 1 → 原逻辑直接 raise RuntimeError → reward=0
        # 且 verifier 根本没跑 → 被误判为「能力失败」(假低分)。
        # 实测 87/88 失败题 = 429/rate_limit/exceeded retry（infra，非能力）。
        #
        # 修复 ② (429 退避重试): 检测 stdout/stderr 含 429 / rate limit /
        # exceeded retry → 指数退避 (2/4/8/16s) 重试整次 codex exec，上限 4 次。
        # 注意 429 出现在 codex 的 JSON 事件 stdout（非 stderr），故两路都查。
        #
        # 修复 ① (exit code 非 0 不再误杀): codex 用 --json 输出完整 NDJSON 事件流。
        # 应从 stdout 的 JSON 事件判断 agent 是否真的在工作（turn.started /
        # agent_message / command_execution / turn.completed），而不是看 shell
        # exit code。若 stdout 里有正常的 agent 事件（agent 确实在跑），exit code
        # 非 0 不作为失败依据 —— 不 raise，让 verifier 照常运行判分。
        # 只有「agent 从未开始工作」（stdout 无任何 agent 事件）且 exit code 非 0
        # 才 raise RuntimeError（真正的 agent 崩溃/启动失败）。
        # turn.failed 事件单独记录到 metadata.codex_turn_failed，供 audit 归因。
        _RATE_LIMIT_RE = re.compile(
            r"429|rate[ _-]?limit|Too Many Requests|exceeded.{0,12}retry|"
            r"retry.{0,12}exceeded|retries? exceeded",
            re.I,
        )
        # agent 活动事件类型 —— 出现任一即证明 codex 确实在跑（非启动崩溃）
        _AGENT_ACTIVITY_TYPES = {
            "turn.started", "turn.completed", "turn.failed",
            "agent_message", "command_execution", "file_change",
            "reasoning",
        }
        backoff_delays = [2, 4, 8, 16]  # 上限 4 次重试
        result = None
        attempts = 0
        last_rate_limit = False
        while True:
            attempts += 1
            result = await environment.exec(
                command=cmd,
                env=env,
                timeout_sec=self._timeout,
            )
            combined = f"{result.stdout or ''}\n{result.stderr or ''}"
            hit_rate_limit = bool(_RATE_LIMIT_RE.search(combined))
            if result.return_code == 0:
                break  # 干净跑完
            if not hit_rate_limit:
                break  # 非 429 错误 → 不重试，走下面的 exit-code 判定
            last_rate_limit = True
            if attempts > len(backoff_delays):
                break  # 退避上限耗尽 → 走下面的 exit-code 判定
            delay = backoff_delays[attempts - 1]
            # 退避：让网关从 429 恢复后再重试整次 codex exec
            await asyncio.sleep(delay)

        # 解析 stdout NDJSON 事件流，判断 agent 是否真的在工作
        stdout_text = result.stdout or ""
        agent_worked = False
        turn_failed = False
        turn_failed_msg = ""
        for _line in stdout_text.splitlines():
            _line = _line.strip()
            if not _line or not _line.startswith("{"):
                continue
            try:
                _evt = json.loads(_line)
            except Exception:
                continue
            _etype = _evt.get("type", "")
            # 顶层 turn.* 事件
            if _etype in _AGENT_ACTIVITY_TYPES:
                agent_worked = True
            if _etype == "turn.failed":
                turn_failed = True
                _err = _evt.get("error") or {}
                turn_failed_msg = _err.get("message", "")
            # item.completed 内嵌的 item.type
            _item = _evt.get("item") or {}
            _itype = _item.get("type", "")
            if _itype in _AGENT_ACTIVITY_TYPES:
                agent_worked = True

        context.metadata = {
            "stdout": stdout_text,
            "stderr": result.stderr or "",
            "exit_code": result.return_code,
            "codex_429_retries": attempts - 1,
            "codex_agent_worked": agent_worked,
            "codex_turn_failed": turn_failed,
            "codex_turn_failed_msg": turn_failed_msg[:300],
        }

        if result.return_code != 0:
            if agent_worked:
                # 修复 ① 核心：agent 确实在跑（stdout 有 agent 事件），exit code
                # 非 0 不作为失败依据 —— 不 raise，让 verifier 照常运行判分。
                # turn.failed(429) 退避耗尽的情况也走这里：agent 部分工作了，
                # verifier 会判分（很可能 0 分），audit 据 metadata 归为
                # rate_limit/infra 而非 ability —— 不再产生「假低分=能力」误判。
                pass
            else:
                # agent 从未开始工作（stdout 无任何 agent 事件）→ 真正的启动
                # 崩溃 / CLI 故障 → raise，让 harness 记为 exception。
                tag = " (gateway 429/rate-limit, backoff exhausted)" if last_rate_limit else ""
                raise RuntimeError(
                    f"Codex exited with code {result.return_code}{tag} "
                    f"and produced no agent activity: "
                    f"{(result.stderr or '')[:500]}"
                )
