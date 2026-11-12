# SPDX-License-Identifier: Apache-2.0
"""MiniCPM5 XML tool-call parser for vLLM serving endpoint.

MiniCPM5-2B uses XML-format tool calls (from chat_template.jinja):
  <function name="func_name">
    <param name="param_name">param_value</param>
  </function>

CDATA-wrapped values for code with <, & or newlines:
  <param name="code"><![CDATA[import pyAether\nprint("hello")]]></param>

Registered as "minicpm5" in vLLM ToolParserManager.
Usage: --tool-call-parser minicpm5
"""
import json
import re
from typing import Dict, List, Sequence, Union

from vllm.entrypoints.openai.protocol import (
    ChatCompletionRequest, DeltaMessage, DeltaToolCall, DeltaFunctionCall,
    ExtractedToolCallInformation, FunctionCall, ToolCall)
from vllm.entrypoints.openai.tool_parsers.abstract_tool_parser import (
    ToolParser, ToolParserManager)
from vllm.logger import init_logger
from vllm.utils import random_uuid

logger = init_logger(__name__)

FUNCTION_CALL_REGEX = re.compile(
    r'<function\s+name="([^"]+)">(.+?)</function>', re.DOTALL)

PARAM_REGEX = re.compile(
    r'<param\s+name="([^"]+)">(\s*<!\[CDATA\[(.*?)\]\]>\s*|(.*?))</param>',
    re.DOTALL)

THINKING_END_MARKER = "\u56de\u8986"  # 回覆


def _convert_param_value(raw_value: str) -> object:
    raw_value = raw_value.strip()
    if not raw_value:
        return raw_value
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
    return raw_value


def _parse_function_block(func_name: str, body: str) -> Dict[str, object]:
    args: Dict[str, object] = {}
    for match in PARAM_REGEX.finditer(body):
        param_name = match.group(1)
        cdata_content = match.group(3)
        plain_content = match.group(4)
        if cdata_content is not None:
            args[param_name] = cdata_content
        elif plain_content is not None:
            args[param_name] = _convert_param_value(plain_content)
        else:
            args[param_name] = ""
    return args


def _strip_thinking(text: str) -> str:
    if THINKING_END_MARKER in text:
        text = text.split(THINKING_END_MARKER, 1)[-1].strip()
    return text.strip()


@ToolParserManager.register_module("minicpm5")
class MiniCPM5ToolParser(ToolParser):

    def __init__(self, tokenizer):
        super().__init__(tokenizer)
        self.current_tool_id: int = -1

    def extract_tool_calls(
        self,
        model_output: str,
        request: ChatCompletionRequest,
    ) -> ExtractedToolCallInformation:
        if "<function" not in model_output:
            return ExtractedToolCallInformation(
                tools_called=False, tool_calls=[],
                content=model_output if model_output else None)
        try:
            tool_calls: List[ToolCall] = []
            for match in FUNCTION_CALL_REGEX.finditer(model_output):
                func_name = match.group(1)
                func_body = match.group(2)
                args = _parse_function_block(func_name, func_body)
                tool_calls.append(ToolCall(
                    type="function",
                    function=FunctionCall(
                        name=func_name,
                        arguments=json.dumps(args, ensure_ascii=False))))
            if not tool_calls:
                return ExtractedToolCallInformation(
                    tools_called=False, tool_calls=[], content=model_output)
            first_func_pos = model_output.find("<function")
            content_text = model_output[:first_func_pos] if first_func_pos > 0 else ""
            content_text = _strip_thinking(content_text) if content_text else ""
            return ExtractedToolCallInformation(
                tools_called=True, tool_calls=tool_calls,
                content=content_text if content_text else None)
        except Exception:
            logger.exception("Error extracting MiniCPM5 tool calls.")
            return ExtractedToolCallInformation(
                tools_called=False, tool_calls=[], content=model_output)

    def extract_tool_calls_streaming(
        self,
        previous_text: str,
        current_text: str,
        delta_text: str,
        previous_token_ids: Sequence[int],
        current_token_ids: Sequence[int],
        delta_token_ids: Sequence[int],
        request: ChatCompletionRequest,
    ) -> Union[DeltaMessage, None]:
        if "<function" not in current_text:
            return DeltaMessage(content=delta_text)
        if "</function>" in delta_text or current_text.rstrip().endswith("</function>"):
            try:
                tool_calls_raw = []
                for match in FUNCTION_CALL_REGEX.finditer(current_text):
                    func_name = match.group(1)
                    func_body = match.group(2)
                    args = _parse_function_block(func_name, func_body)
                    tool_calls_raw.append({
                        "name": func_name,
                        "arguments": json.dumps(args, ensure_ascii=False)})
                if tool_calls_raw:
                    self.current_tool_id += 1
                    last_call = tool_calls_raw[-1]
                    return DeltaMessage(
                        tool_calls=[DeltaToolCall(
                            index=self.current_tool_id,
                            function=DeltaFunctionCall(
                                name=last_call["name"],
                                arguments=last_call["arguments"]))])
            except Exception:
                logger.debug("Error parsing streaming tool call")
        if "<function" in current_text and "</function>" not in current_text:
            return None
        return DeltaMessage(content=delta_text)
