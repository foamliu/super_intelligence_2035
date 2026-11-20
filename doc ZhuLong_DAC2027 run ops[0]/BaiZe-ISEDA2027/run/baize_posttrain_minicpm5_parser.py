#!/usr/bin/env python3
"""baize_posttrain_minicpm5_parser.py — MiniCPM5-2B XML tool-call parser for verl.

R16 (2026-11-07): CRITICAL BREAKTHROUGH — verl has its OWN ToolParser layer
(verl/experimental/agent_loop/tool_parser.py) that is SEPARATE from SGLang's
tool-call parser. verl parses tool calls from model output text itself;
SGLang just generates text. This means:

  ✅ SGLang's minicpm5 parser is NOT needed
  ✅ No dependency on unreleased PR #25600
  ✅ No CUDA 13.x requirement for tool parsing
  ✅ Works with any SGLang pip release (0.5.6.post3 etc.)

MiniCPM5-2B uses XML-format tool calls (from chat_template.jinja):
  <function name="get_weather">
    <param name="city">北京</param>
  </function>

Parameter values containing <, & or newline are wrapped in CDATA:
  <param name="code"><![CDATA[import pyAether\nprint("hello")]]></param>

This parser registers as "minicpm5" in verl's ToolParser registry.
Usage in verl config YAML:
  rollout:
    multi_turn:
      format: minicpm5

Import this module BEFORE verl starts training to register the parser:
  import baize_posttrain_minicpm5_parser  # registers "minicpm5" parser
"""
from __future__ import annotations

import ast
import json
import logging
import os
import re
from typing import Any, Optional

logger = logging.getLogger(__file__)
logger.setLevel(os.getenv("VERL_LOGGING_LEVEL", "WARN"))

# --- verl imports (with fallback stubs for syntax checking without verl) ---
try:
    from verl.experimental.agent_loop.tool_parser import ToolParser, FunctionCall
    from verl.tools.schemas import OpenAIFunctionToolSchema
    HAS_VERL = True
except ImportError:
    logger.warning("verl not installed — using stubs for syntax check / dry-run")
    HAS_VERL = False
    from abc import ABC, abstractmethod
    from pydantic import BaseModel

    class FunctionCall(BaseModel):
        arguments: str
        name: str
        tool_call_id: Optional[str] = None

    class OpenAIFunctionToolSchema(BaseModel):
        pass

    class ToolParser(ABC):
        _registry: dict[str, type["ToolParser"]] = {}

        def __init__(self, tokenizer) -> None:
            self.tokenizer = tokenizer

        @property
        def stop_token_ids(self) -> list[int]:
            return []

        @abstractmethod
        async def extract_tool_calls(
            self, responses_ids: list[int], tools: list[Any] = None
        ) -> tuple[str, list[FunctionCall]]:
            raise NotImplementedError

        @classmethod
        def get_tool_parser(cls, name: str, tokenizer):
            if name not in cls._registry:
                raise ValueError(f"Unknown tool parser: {name}")
            return cls._registry[name](tokenizer)

        @classmethod
        def register(cls, name: str):
            def decorator(subclass):
                cls._registry[name] = subclass
                return subclass
            return decorator


# --- MiniCPM5 XML format constants ---
IM_END_TOKEN = "<|im_end|>"

# <function name="func_name"> ... </function>
FUNCTION_CALL_REGEX = re.compile(
    r'<function\s+name="([^"]+)">(.+?)</function>',
    re.DOTALL
)

# <param name="param_name">value</param>  (also handles CDATA)
PARAM_REGEX = re.compile(
    r'<param\s+name="([^"]+)">(\s*<!\[CDATA\[(.*?)\]\]>\s*|(.*?))</param>',
    re.DOTALL
)


def _convert_param_value(
    raw_value: str,
    param_name: str,
    param_type: Optional[str] = None,
    func_name: str = "?",
) -> Any:
    """Convert a raw string parameter value to the appropriate Python type."""
    raw_value = raw_value.strip()
    if raw_value.startswith("\n"):
        raw_value = raw_value[1:]
    if raw_value.endswith("\n"):
        raw_value = raw_value[:-1]

    if not param_type:
        if raw_value.lower() in ("true", "false"):
            return raw_value.lower() == "true"
        try:
            return int(raw_value)
        except ValueError:
            pass
        try:
            return float(raw_value)
        except ValueError:
            pass
        if raw_value.startswith(("{", "[")):
            try:
                return json.loads(raw_value)
            except json.JSONDecodeError:
                pass
        try:
            return ast.literal_eval(raw_value)
        except (ValueError, SyntaxError):
            pass
        return raw_value

    if param_type in ("string", "str"):
        return raw_value
    if param_type in ("boolean", "bool"):
        return raw_value.lower() == "true"
    if param_type in ("integer", "int"):
        try:
            return int(raw_value)
        except ValueError:
            return 0
    if param_type in ("number", "float"):
        try:
            return float(raw_value)
        except ValueError:
            return 0.0
    if param_type in ("object", "array") or param_type.startswith(("dict", "list")):
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(raw_value)
            except (ValueError, SyntaxError):
                return raw_value
    return raw_value


def _get_param_type(
    func_name: str,
    param_name: str,
    tools: list[Any] = None,
) -> Optional[str]:
    """Look up the expected type of a parameter from the tool schema."""
    if not tools:
        return None
    for tool in tools:
        schema = None
        if hasattr(tool, "function"):
            schema = tool.function
        elif isinstance(tool, dict) and "function" in tool:
            schema = tool["function"]
        if schema is None:
            continue
        name = getattr(schema, "name", None)
        if name is None and isinstance(schema, dict):
            name = schema.get("name")
        if name != func_name:
            continue
        params = getattr(schema, "parameters", None)
        if params is None and isinstance(schema, dict):
            params = schema.get("parameters")
        if not params:
            continue
        properties = getattr(params, "properties", None)
        if properties is None and isinstance(params, dict):
            properties = params.get("properties")
        if not properties:
            continue
        prop = properties.get(param_name) if isinstance(properties, dict) else None
        if prop and isinstance(prop, dict):
            return prop.get("type")
    return None


def parse_minicpm5_tool_calls(
    model_output: str,
    tools: list[Any] = None,
) -> tuple[str, list[FunctionCall]]:
    """Parse MiniCPM5-2B XML-format tool calls from model output text."""
    function_calls: list[FunctionCall] = []
    content_parts: list[str] = []

    last_end = 0
    for match in FUNCTION_CALL_REGEX.finditer(model_output):
        if match.start() > last_end:
            content_parts.append(model_output[last_end:match.start()])

        func_name = match.group(1)
        func_body = match.group(2)

        param_dict: dict[str, Any] = {}
        for param_match in PARAM_REGEX.finditer(func_body):
            p_name = param_match.group(1)
            p_value = param_match.group(3) if param_match.group(3) is not None else param_match.group(4)
            if p_value is None:
                p_value = ""
            p_type = _get_param_type(func_name, p_name, tools)
            param_dict[p_name] = _convert_param_value(p_value, p_name, p_type, func_name)

        function_calls.append(
            FunctionCall(
                name=func_name,
                arguments=json.dumps(param_dict, ensure_ascii=False),
                tool_call_id=f"minicpm5_{func_name}_{len(function_calls)}",
            )
        )
        last_end = match.end()

    if last_end < len(model_output):
        content_parts.append(model_output[last_end:])

    content = "".join(content_parts).strip()
    return content, function_calls


@ToolParser.register("minicpm5")
class MiniCPM5ToolParser(ToolParser):
    """Tool parser for MiniCPM5-2B XML-format function calls.

    MiniCPM5-2B uses XML tags for tool calling (defined in chat_template.jinja):
      <function name="function_name">
        <param name="param_name">param_value</param>
      </function>

    Parameter values with special characters (<, &, newline) are CDATA-wrapped.
    The model emits <|im_end|> (EOS) after completing its turn.

    Register name: "minicpm5"
    Config: rollout.multi_turn.format: minicpm5
    """

    def __init__(self, tokenizer) -> None:
        super().__init__(tokenizer)

    @property
    def stop_token_ids(self) -> list[int]:
        """MiniCPM5 emits <|im_end|> as EOS after tool calls."""
        return []

    async def extract_tool_calls(
        self,
        responses_ids: list[int],
        tools: list[Any] = None,
    ) -> tuple[str, list[FunctionCall]]:
        """Extract tool calls from MiniCPM5-2B response token IDs."""
        text = self.tokenizer.decode(responses_ids, skip_special_tokens=False)

        # Strip trailing <|im_end|> if present
        if IM_END_TOKEN in text:
            text = text.split(IM_END_TOKEN)[0]

        content, function_calls = parse_minicpm5_tool_calls(text, tools)

        if function_calls:
            logger.info(
                f"MiniCPM5ToolParser: extracted {len(function_calls)} tool call(s): "
                f"{[fc.name for fc in function_calls]}"
            )

        return content, function_calls


# --- Self-test / dry-run ---
if __name__ == "__main__":
    import sys

    print("=" * 70)
    print("MiniCPM5ToolParser self-test")
    print("=" * 70)

    tests_passed = 0
    tests_total = 0

    # Test 1: Single function call
    tests_total += 1
    t1 = '<function name="run_eda_code"><param name="code">import pyAether as pyScript\nprint("hello")</param><param name="host">pyAether</param></function>'
    content, calls = parse_minicpm5_tool_calls(t1)
    print(f"\nTest 1: Single function call")
    print(f"  Content: '{content}'")
    print(f"  Calls: {len(calls)}")
    for c in calls:
        print(f"    name={c.name}, args={c.arguments}")
    assert len(calls) == 1, f"Expected 1 call, got {len(calls)}"
    assert calls[0].name == "run_eda_code"
    args = json.loads(calls[0].arguments)
    assert args["host"] == "pyAether"
    assert "import pyAether" in args["code"]
    print("  PASS")
    tests_passed += 1

    # Test 2: CDATA-wrapped parameter
    tests_total += 1
    t2 = '<function name="run_eda_code"><param name="code"><![CDATA[import pyAether as pyScript\nresult = pyScript.get_cell("A1")\nprint(result)]]></param></function>'
    content, calls = parse_minicpm5_tool_calls(t2)
    print(f"\nTest 2: CDATA-wrapped parameter")
    print(f"  Calls: {len(calls)}")
    args = json.loads(calls[0].arguments)
    assert "get_cell" in args["code"], f"CDATA content not extracted: {args['code']}"
    print(f"  Code: {args['code'][:50]}...")
    print("  PASS")
    tests_passed += 1

    # Test 3: No tool call (regular text)
    tests_total += 1
    t3 = "I'll help you with that EDA task. Let me think about the approach..."
    content, calls = parse_minicpm5_tool_calls(t3)
    print(f"\nTest 3: No tool call (regular text)")
    print(f"  Content: '{content[:50]}...'")
    print(f"  Calls: {len(calls)}")
    assert len(calls) == 0
    assert content == t3
    print("  PASS")
    tests_passed += 1

    # Test 4: Text + function call
    tests_total += 1
    t4 = 'Let me check the API first.\n<function name="search_apis"><param name="query">get_cell</param></function>'
    content, calls = parse_minicpm5_tool_calls(t4)
    print(f"\nTest 4: Text + function call")
    print(f"  Content: '{content}'")
    print(f"  Calls: {len(calls)}")
    assert len(calls) == 1
    assert "Let me check" in content
    args = json.loads(calls[0].arguments)
    assert args["query"] == "get_cell"
    print("  PASS")
    tests_passed += 1

    # Test 5: Multiple function calls
    tests_total += 1
    t5 = '<function name="search_apis"><param name="query">cell</param></function>\n<function name="get_api_details"><param name="api_name">get_cell</param></function>'
    content, calls = parse_minicpm5_tool_calls(t5)
    print(f"\nTest 5: Multiple function calls")
    print(f"  Calls: {len(calls)}")
    assert len(calls) == 2
    assert calls[0].name == "search_apis"
    assert calls[1].name == "get_api_details"
    print("  PASS")
    tests_passed += 1

    # Test 6: Integer parameter
    tests_total += 1
    t6 = '<function name="set_timeout"><param name="seconds">30</param></function>'
    content, calls = parse_minicpm5_tool_calls(t6)
    print(f"\nTest 6: Integer parameter")
    args = json.loads(calls[0].arguments)
    print(f"  seconds={args['seconds']} (type={type(args['seconds']).__name__})")
    assert args["seconds"] == 30
    print("  PASS")
    tests_passed += 1

    # Test 7: Boolean parameter
    tests_total += 1
    t7 = '<function name="set_verbose"><param name="enabled">true</param></function>'
    content, calls = parse_minicpm5_tool_calls(t7)
    print(f"\nTest 7: Boolean parameter")
    args = json.loads(calls[0].arguments)
    print(f"  enabled={args['enabled']} (type={type(args['enabled']).__name__})")
    assert args["enabled"] is True
    print("  PASS")
    tests_passed += 1

    # Test 8: Registry check
    tests_total += 1
    print(f"\nTest 8: Registry check")
    print(f"  Registered parsers: {list(ToolParser._registry.keys())}")
    assert "minicpm5" in ToolParser._registry
    print("  PASS: 'minicpm5' registered in ToolParser registry")
    tests_passed += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {tests_passed}/{tests_total} tests PASSED")
    if tests_passed == tests_total:
        print("All tests PASSED")
    else:
        print("SOME TESTS FAILED")
        sys.exit(1)
    print("=" * 70)
