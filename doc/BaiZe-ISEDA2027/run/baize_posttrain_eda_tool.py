#!/usr/bin/env python3
"""baize_posttrain_eda_tool.py — EDA Sandbox Tool for verl multi-turn rollout.

R9 (2026-11-07): verl's Tool Agent Loop requires custom tools as BaseTool subclasses.
This tool sends code to the EDA sandbox on 36.15 via SSH tunnel and returns
execution results (response/error_log/print_log/result).

The EDA sandbox is the natural reward signal source — execution success/failure
is objective, unlike LLM self-evaluation.

WARNING: Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import json, logging, subprocess, time
from typing import Any, Dict, Tuple

logger = logging.getLogger(__name__)

try:
    from verl.tools.base_tool import BaseTool
    HAS_VERL = True
except ImportError:
    logger.warning("verl not installed — using BaseTool stub for syntax check")
    HAS_VERL = False
    class BaseTool:  # type: ignore[no-redef]
        def __init__(self, *a, **kw): pass
        async def create(self, *a, **kw): return None
        async def execute(self, *a, **kw): raise NotImplementedError
        async def release(self, *a, **kw): pass


class EDASandboxTool(BaseTool):
    """EDA Sandbox Tool for verl multi-turn RL rollout.

    Sends Python/TCL code to the EDA sandbox (pyAether on 36.15) via SSH tunnel.
    Returns: response, error_log, print_log, result.
    """
    DEFAULT_HOST = "pyAether"
    DEFAULT_TIMEOUT = 60
    MAX_CODE_LENGTH = 5000

    def __init__(self, config: Dict[str, Any] | None = None):
        config = config or {}
        self.sandbox_endpoint = config.get("sandbox_endpoint", "ssh://tunnel-to-36.15")
        self.sandbox_hosts = config.get("sandbox_hosts", [
            "pyAether", "aether", "skill_virtuoso", "tcl_innovus", "tcl_waveview"])
        self.max_code_length = config.get("max_code_length", self.MAX_CODE_LENGTH)
        self.timeout = config.get("timeout", self.DEFAULT_TIMEOUT)
        self._ssh_ready = False

    async def create(self, *args, **kwargs) -> Tuple[str | None, Any]:
        """Establish SSH tunnel to EDA sandbox (called once per rollout episode)."""
        logger.info("EDASandboxTool: establishing SSH tunnel to %s", self.sandbox_endpoint)
        self._ssh_ready = True
        return None, None

    async def execute(self, code: str, host: str | None = None, **kwargs
                      ) -> Tuple[Dict[str, Any], float, Dict[str, Any]]:
        """Execute code in EDA sandbox.
        Returns: (tool_response, reward_signal, metadata)
        """
        host = host or self.DEFAULT_HOST
        if host not in self.sandbox_hosts:
            return ({"response": "", "error_log": f"Unknown host: {host}",
                     "print_log": "", "result": None}, 0.0, {"host": host, "error": "unknown_host"})
        if len(code) > self.max_code_length:
            return ({"response": "", "error_log": f"Code too long: {len(code)} > {self.max_code_length}",
                     "print_log": "", "result": None}, 0.0, {"host": host, "error": "code_too_long"})

        start = time.time()
        # TODO(11/9+): Replace with actual SSH execution to 36.15 run_code
        try:
            exec_result = {"response": "", "error_log": "[skeleton] SSH not yet implemented",
                           "print_log": "", "result": None}
            reward_signal = 0.0
            metadata = {"host": host, "code_length": len(code),
                        "elapsed_s": time.time() - start, "skeleton": True}
        except Exception as e:
            exec_result = {"response": "", "error_log": str(e), "print_log": "", "result": None}
            reward_signal = 0.0
            metadata = {"host": host, "error": str(e), "elapsed_s": time.time() - start}
        return exec_result, reward_signal, metadata

    async def release(self, *args, **kwargs) -> None:
        """Close SSH tunnel (called at end of rollout episode)."""
        logger.info("EDASandboxTool: releasing SSH tunnel")
        self._ssh_ready = False


def compute_r2_reward(exec_result: Dict[str, Any], test_code: str | None) -> float:
    """R2 = exec_success(0.2) + partial_assert(0.2 each) + full_pass(1.0)."""
    if not exec_result:
        return 0.0
    error_log = exec_result.get("error_log", "")
    has_error = bool(error_log and "skeleton" not in error_log.lower())
    if has_error:
        return 0.0
    reward = 0.2  # exec_success base
    # TODO(11/9+): Run test_code and count passed assertions
    return reward


def compute_r3_reward(exec_result, test_code, tool_call_count: int) -> float:
    """R3 = R2 + tool_call_penalty."""
    base = compute_r2_reward(exec_result, test_code)
    penalty = max(0.0, (tool_call_count - 10) * 0.01)
    return max(0.0, base - penalty)


def compute_r4_reward(exec_result, test_code, tool_call_count: int, api_db_path: str | None) -> float:
    """R4 = R3 + API_legality."""
    base = compute_r3_reward(exec_result, test_code, tool_call_count)
    # TODO(11/9+): Check APIs in code against api_database
    return base


if __name__ == "__main__":
    import asyncio
    async def dry_run():
        tool = EDASandboxTool({"sandbox_endpoint": "ssh://tunnel-to-36.15",
                               "sandbox_hosts": ["pyAether", "aether"], "timeout": 30})
        await tool.create()
        result, reward, meta = await tool.execute(code="import pyAether as pyScript\nprint('hello')", host="pyAether")
        print(f"Result: {result}")
        print(f"Reward: {reward}")
        print(f"Meta: {meta}")
        print(f"R2: {compute_r2_reward(result, None)}")
        await tool.release()
        print("Dry-run complete (skeleton mode)")
    asyncio.run(dry_run())
