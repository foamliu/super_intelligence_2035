#!/usr/bin/env python3
"""baize_posttrain_verl_wrapper.py — Wrapper to launch verl GRPO training.

R47 (2026-11-08): CRITICAL REWRITE — R21 assumed verl had a ToolParser registry
(verl.experimental.agent_loop.tool_parser.ToolParser._registry). Source code audit
of verl 0.4.0 found this module DOES NOT EXIST. The old wrapper would fail with
AttributeError on ToolParser._registry.

R47 findings:
  - verl 0.4.0 has NO `experimental/` directory, NO `agent_loop`, NO `tool_parser`
  - Tool call parsing is handled by sglang's FunctionCallParser (4 built-in parsers:
    llama3, qwen25, mistral, deepseekv3) — NONE match MiniCPM5's XML format
  - For single-turn RL (R0 smoke test), no tool parser is needed
  - For multi-turn RL (Phase 2), must monkey-patch sglang's ToolCallParserEnum

This wrapper now:
    1. Optionally monkey-patches sglang for MiniCPM5 XML parser (if --enable-multi-turn)
    2. Launches verl.trainer.main_ppo.main()
"""
import sys
import os
import re
import json
from typing import List, Tuple

script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

ENABLE_MULTI_TURN = "--enable-multi-turn" in sys.argv
if ENABLE_MULTI_TURN:
    sys.argv.remove("--enable-multi-turn")

# === Phase 2: Monkey-patch sglang for MiniCPM5 XML tool calls ===
if ENABLE_MULTI_TURN:
    try:
        from sglang.srt.function_call_parser import (
            FunctionCallParser, BaseFormatDetector,
            StreamingParseResult, ToolCallItem,
        )
        from sglang.srt.openai_api.protocol import Tool

        class MiniCPM5XMLDetector(BaseFormatDetector):
            """Detector for MiniCPM5-2B XML-format tool calls.

            MiniCPM5 uses:
              <function name="get_weather">
                <param name="city">北京</param>
              </function>
            """
            def __init__(self):
                super().__init__()
                self.bot_token = "<function"
                self.eot_token = "</function>"

            def has_tool_call(self, text: str) -> bool:
                return "<function name=" in text

            def detect_and_parse(self, text: str, tools: List[Tool]) -> StreamingParseResult:
                if "<function name=" not in text:
                    return StreamingParseResult(normal_text=text, calls=[])
                pattern = r'<function\s+name="([^"]+)">(.*?)</function>'
                matches = re.findall(pattern, text, re.DOTALL)
                calls = []
                for func_name, body in matches:
                    params = {}
                    param_pattern = r'<param\s+name="([^"]+)">(.*?)</param>'
                    for pname, pval in re.findall(param_pattern, body, re.DOTALL):
                        if pval.strip().startswith("<![CDATA["):
                            pval = pval.strip()[9:-3]
                        params[pname] = pval.strip()
                    calls.append(ToolCallItem(
                        tool_index=0,
                        name=func_name,
                        parameters=json.dumps(params),  # R50 FIX: field is `parameters` not `arguments` (Pydantic BaseModel)
                    ))
                normal = re.sub(pattern, '', text, flags=re.DOTALL).strip()
                return StreamingParseResult(normal_text=normal, calls=calls)

            def structure_info(self):
                from sglang.srt.function_call_parser import StructureInfo
                return lambda name: StructureInfo(
                    begin=f'<function name="{name}">',
                    end="</function>",
                    trigger="<function",
                )

        # Register in sglang's enum
        FunctionCallParser.ToolCallParserEnum["minicpm5"] = MiniCPM5XMLDetector
        print(f"[wrapper] MiniCPM5 XML parser registered in sglang ToolCallParserEnum",
              flush=True)
    except Exception as e:
        print(f"[wrapper] WARNING: Failed to register MiniCPM5 parser: {e}", flush=True)
        print("[wrapper] Multi-turn tool calls will not work!", flush=True)
else:
    print("[wrapper] Single-turn mode (R0 skeleton, no tool parser needed)", flush=True)

# === Launch verl's main_ppo entry point ===
try:
    from verl.trainer.main_ppo import main as verl_main
    print(f"[wrapper] Launching verl.trainer.main_ppo with args: {sys.argv[1:]}",
          flush=True)
    verl_main()
except ImportError as e:
    print(f"[wrapper] ERROR: Cannot import verl.trainer.main_ppo: {e}", flush=True)
    print("[wrapper] Make sure verl is installed in this venv.", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"[wrapper] verl training exited with error: {e}", flush=True)
    raise
