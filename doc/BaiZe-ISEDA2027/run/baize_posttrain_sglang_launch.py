#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper to launch SGLang server with MiniCPM5-2B XML tool call parser patch.

Usage:
  CUDA_VISIBLE_DEVICES=4 python baize_posttrain_sglang_launch.py [sglang args...]

This script:
1. Applies the MiniCPM5FunctionDetector patch to SGLang's ToolCallParserEnum
2. Launches sglang.launch_server with --tool-call-parser minicpm5
"""

import sys
import os

# Add this directory to path so we can import the patch
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

# Apply the MiniCPM5 parser patch BEFORE SGLang starts
try:
    import baize_posttrain_minicpm5_parser_patch  # noqa: F401
    print("[baize_sglang_launch] MiniCPM5 parser patch applied successfully")
except Exception as e:
    print(f"[baize_sglang_launch] WARNING: Could not apply parser patch: {e}")
    print("[baize_sglang_launch] Continuing without tool call parser...")

# Now launch SGLang server
from sglang.launch_server import main

if __name__ == "__main__":
    main()
