#!/usr/bin/env python3
"""baize_posttrain_eda_tool_v2.py — Corrected EDA Sandbox Tool for verl 0.4.0.

R69 (2026-11-09): Source-level audit found 3 CRITICAL API mismatches in v1:
  F01: __init__ missing tool_schema param
  F02: create() returns tuple, verl expects str
  F03: execute() returns Dict, verl expects str (JSON-serialized)
This v2 fixes all 3 issues. ⚠️ Surrogate RL results NOT transferable to BaiZe.
"""
from __future__ import annotations
import asyncio, json, logging, time
from typing import Any, Dict, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)
try:
    from verl.tools.base_tool import BaseTool
    from verl.tools.schemas import OpenAIFunctionToolSchema
    HAS_VERL = True
except ImportError:
    HAS_VERL = False
    class OpenAIFunctionToolSchema: pass
    class BaseTool:
        def __init__(self, config, tool_schema):
            self.config = config; self.name = "stub"; self.tool_schema = tool_schema


class EDASandboxToolV2(BaseTool):
    """EDA Sandbox Tool v2 — matches verl 0.4.0 BaseTool API contract."""

    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self.sandbox_endpoint = config.get("sandbox_endpoint", "tier3")
        self.sandbox_hosts = config.get("sandbox_hosts", [
            "pyAether", "aether", "skill_virtuoso", "tcl_innovus", "tcl_waveview"])
        self.max_code_length = config.get("max_code_length", 5000)
        self.timeout = config.get("timeout", 60)
        self.tier = config.get("tier", 3)
        self._instance_dict: Dict[str, Dict[str, Any]] = {}

    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "response": "", "reward": 0.0, "tool_call_count": 0}
        logger.info("EDASandboxToolV2[%s]: created (tier=%d)", instance_id, self.tier)
        return instance_id

    async def execute(self, instance_id: str, parameters: dict[str, Any],
                      **kwargs) -> Tuple[str, float, dict]:
        code = parameters.get("code", "")
        host = parameters.get("host", "pyAether")
        if host not in self.sandbox_hosts:
            return json.dumps({"error": f"Unknown host: {host}"}), 0.0, {"error": "unknown_host"}
        if len(code) > self.max_code_length:
            return json.dumps({"error": "Code too long"}), 0.0, {"error": "code_too_long"}
        if instance_id in self._instance_dict:
            self._instance_dict[instance_id]["tool_call_count"] += 1
        start = time.time()
        try:
            if self.tier == 3:
                result = self._static_analysis(code)
            else:
                result = {"response": "", "error_log": "Not implemented"}
            return (json.dumps(result, ensure_ascii=False), 0.0,
                    {"host": host, "elapsed_s": round(time.time()-start, 3), "tier": self.tier})
        except Exception as e:
            return json.dumps({"error": str(e)}), 0.0, {"error": str(e)}

    def _static_analysis(self, code: str) -> dict:
        result = {"response": "", "error_log": "", "print_log": "", "result": None}
        try:
            compile(code, "<sandbox>", "exec")
            result["response"] = "[static] Syntax OK"
        except SyntaxError as e:
            result["error_log"] = f"SyntaxError: {e}"
            result["response"] = f"[static] SyntaxError at line {e.lineno}"
        return result

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        return self._instance_dict.get(instance_id, {}).get("reward", 0.0)

    async def release(self, instance_id: str, **kwargs) -> None:
        self._instance_dict.pop(instance_id, None)
        logger.info("EDASandboxToolV2[%s]: released", instance_id)


if __name__ == "__main__":
    async def dry_run():
        schema = OpenAIFunctionToolSchema.model_validate({
            "type": "function", "function": {
                "name": "eda_sandbox", "description": "EDA sandbox",
                "parameters": {"type": "object",
                    "properties": {"code": {"type": "string"}},
                    "required": ["code"]}}}) if HAS_VERL else None
        tool = EDASandboxToolV2({"tier": 3, "timeout": 30}, schema)
        iid = await tool.create(instance_id="test-001")
        print(f"create() -> {iid} (type={type(iid).__name__})")
        resp, reward, meta = await tool.execute(iid, {"code": "print('hi')", "host": "pyAether"})
        print(f"execute() -> resp type={type(resp).__name__}, reward={reward}")
        print(f"  resp={resp[:200]}\n  meta={meta}")
        print(f"calc_reward() -> {await tool.calc_reward(iid)}")
        await tool.release(iid)
        print("Dry-run complete")
    asyncio.run(dry_run())
