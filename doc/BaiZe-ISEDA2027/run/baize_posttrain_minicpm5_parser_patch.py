#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monkey-patch to register MiniCPM5FunctionDetector in SGLang for MiniCPM5-2B.

Usage: import this module BEFORE verl initializes SGLang rollout:
    import baize_posttrain_minicpm5_parser_patch  # noqa: F401

Two actions:
1. Register MiniCPM5FunctionDetector in SGLang's ToolCallParserEnum["minicpm5"]
2. Patch verl's get_tool_call_parser_type to prefer minicpm5 when <function in vocab

Safety: only activates when <function token is in tokenizer vocab.
"""

import json
import logging
import re

logger = logging.getLogger(__name__)


def apply_minicpm5_parser_patch():
    """Register MiniCPM5FunctionDetector in SGLang and patch verl."""
    from sglang.srt.function_call_parser import (
        BaseFormatDetector, StreamingParseResult, ToolCallItem,
        StructureInfo, FunctionCallParser, _GetInfoFunc,
    )
    from sglang.srt.openai_api.protocol import Tool
    from typing import List

    class MiniCPM5FunctionDetector(BaseFormatDetector):
        """Detector for MiniCPM5-2B XML tool call format."""

        def __init__(self):
            super().__init__()
            self.bot_token = "<function"
            self.eot_token = "</function>"
            self._func_re = re.compile(
                r'<function\s+name="([^"]+)">(.*?)</function>', re.DOTALL)
            self._param_re = re.compile(
                r'<param\s+name="([^"]+)">(.*?)</param>', re.DOTALL)

        def has_tool_call(self, text):
            return self.bot_token in text

        def detect_and_parse(self, text, tools):
            idx = text.find(self.bot_token)
            normal_text = text[:idx].strip() if idx != -1 else text
            if self.bot_token not in text:
                return StreamingParseResult(normal_text=normal_text, calls=[])
            matches = self._func_re.findall(text)
            if not matches:
                return StreamingParseResult(normal_text=normal_text, calls=[])
            calls = []
            for func_name, params_xml in matches:
                params = {}
                for pn, pv in self._param_re.findall(params_xml):
                    pv = pv.strip()
                    if pv.startswith("<![CDATA[") and pv.endswith("]]>"):
                        pv = pv[9:-3]
                    params[pn] = pv
                tool_index = 0
                for i, tool in enumerate(tools):
                    if tool.function and tool.function.name == func_name:
                        tool_index = i
                        break
                calls.append(ToolCallItem(
                    tool_index=tool_index, name=func_name,
                    parameters=json.dumps(params)))
            return StreamingParseResult(normal_text=normal_text, calls=calls)

        def parse_streaming_increment(self, new_text, tools):
            self._buffer += new_text
            current = self._buffer
            if self.bot_token not in current:
                self._buffer = ""
                return StreamingParseResult(normal_text=new_text)
            if self.eot_token not in current:
                return StreamingParseResult(normal_text="")
            result = self.detect_and_parse(current, tools)
            self._buffer = ""
            return result

        def structure_info(self):
            return lambda name: StructureInfo(
                begin='<function name="' + name + '">',
                end="</function>", trigger="<function")

    FunctionCallParser.ToolCallParserEnum["minicpm5"] = MiniCPM5FunctionDetector
    logger.info("Registered MiniCPM5FunctionDetector as 'minicpm5'")

    try:
        import verl.workers.rollout.sglang_rollout.sglang_rollout as rollout_mod
        _orig = rollout_mod.get_tool_call_parser_type

        def patched(tokenizer):
            vocab = tokenizer.get_vocab()
            if "<function" in vocab:
                logger.info("MiniCPM5-2B detected, using minicpm5 parser")
                return "minicpm5"
            return _orig(tokenizer)

        rollout_mod.get_tool_call_parser_type = patched
        logger.info("Patched verl get_tool_call_parser_type")
    except ImportError:
        logger.warning("Could not patch verl rollout (import failed)")


apply_minicpm5_parser_patch()
