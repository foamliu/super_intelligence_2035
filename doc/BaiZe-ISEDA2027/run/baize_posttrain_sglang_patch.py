#!/usr/bin/env python3
"""baize_posttrain_sglang_patch.py — Standalone MiniCPM5 XML tool-call parser patch for SGLang.

R53 (2026-11-08): Resolves R-009 (Ray worker monkey-patch propagation).

Problem:
  baize_posttrain_verl_wrapper.py registers a MiniCPM5XMLDetector into
  sglang's ToolCallParserEnum. But when verl uses Ray for distributed
  training, Ray workers are separate Python processes that import sglang
  independently — the in-process monkey-patch does NOT propagate.

Solution:
  This module is auto-imported by ALL Python processes in the venv via a
  .pth file in site-packages (installed by baize_posttrain_install_ray_patch.sh).
  The .pth file checks for env var BAIZE_SGLANG_PATCH=1 before importing
  this module, so processes that don't need the parser are unaffected.

⚠️ Surrogate RL results are NOT transferable to BaiZe.
"""
import os
import re
import json
import sys
from typing import List

_PATCH_APPLIED = False
_PATCH_ERROR = None


def apply_patch() -> bool:
    """Register MiniCPM5XMLDetector into SGLang's ToolCallParserEnum."""
    global _PATCH_APPLIED, _PATCH_ERROR

    if _PATCH_APPLIED:
        return True

    try:
        from sglang.srt.function_call_parser import (
            FunctionCallParser, BaseFormatDetector,
            StreamingParseResult, ToolCallItem,
        )
        from sglang.srt.openai_api.protocol import Tool

        class MiniCPM5XMLDetector(BaseFormatDetector):
            """Detector for MiniCPM5-2B XML-format tool calls."""
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
                        tool_index=0, name=func_name,
                        parameters=json.dumps(params),
                    ))
                normal = re.sub(pattern, "", text, flags=re.DOTALL).strip()
                return StreamingParseResult(normal_text=normal, calls=calls)

            def structure_info(self):
                from sglang.srt.function_call_parser import StructureInfo
                return lambda name: StructureInfo(
                    begin=f'<function name="{name}">',
                    end="</function>", trigger="<function",
                )

        FunctionCallParser.ToolCallParserEnum["minicpm5"] = MiniCPM5XMLDetector
        _PATCH_APPLIED = True
        return True
    except ImportError as e:
        _PATCH_ERROR = f"ImportError: {e}"
        return False
    except Exception as e:
        _PATCH_ERROR = f"Exception: {e}"
        return False


def is_applied() -> bool:
    """Check if the patch has been applied."""
    return _PATCH_APPLIED


def get_error() -> str:
    """Get the last error message if patch failed."""
    return _PATCH_ERROR or ""


def self_test() -> dict:
    """Run a self-test: apply patch, parse a sample tool call, return result."""
    result = {"patch_applied": False, "parser_registered": False,
              "parse_test": None, "error": ""}
    if not apply_patch():
        result["error"] = get_error()
        return result
    result["patch_applied"] = True
    try:
        from sglang.srt.function_call_parser import FunctionCallParser
        if "minicpm5" in FunctionCallParser.ToolCallParserEnum:
            result["parser_registered"] = True
        else:
            result["error"] = "minicpm5 not found in ToolCallParserEnum"
            return result
        from sglang.srt.openai_api.protocol import Tool, Function
        sample_text = (
            '<function name="get_weather">\n'
            '  <param name="city"><![CDATA[北京]]></param>\n'
            '</function>'
        )
        tools = [Tool(type="function", function=Function(
            name="get_weather", description="Get weather",
            parameters={"type": "object",
                        "properties": {"city": {"type": "string"}}}))]
        parser = FunctionCallParser(tool_call_parser="minicpm5", tools=tools)
        parse_result = parser.parse_non_stream(sample_text)
        # parse_non_stream returns an object with normal_text and tool_call_parts
        calls = getattr(parse_result, "tool_call_parts", [])
        normal = getattr(parse_result, "normal_text", "")
        result["parse_test"] = {
            "calls_count": len(calls) if calls else 0,
            "first_call_name": calls[0].name if calls else None,
            "normal_text_length": len(normal) if normal else 0,
        }
    except Exception as e:
        result["error"] = f"Self-test exception: {e}"
    return result


# === Auto-apply on import if BAIZE_SGLANG_PATCH=1 ===
if os.environ.get("BAIZE_SGLANG_PATCH") == "1":
    _auto = apply_patch()
    if _auto:
        print(f"[sglang_patch] Auto-applied MiniCPM5 XML parser "
              f"(pid={os.getpid()}, BAIZE_SGLANG_PATCH=1)", flush=True)
    else:
        print(f"[sglang_patch] Auto-apply FAILED: {_PATCH_ERROR} "
              f"(pid={os.getpid()})", flush=True)
