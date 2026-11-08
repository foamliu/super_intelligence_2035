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
# R53: Use standalone module baize_posttrain_sglang_patch.py for patch logic.
#   This enables .pth-file-based propagation to Ray workers (R-009 resolution).
#   The .pth file in venv site-packages auto-imports the patch module when
#   BAIZE_SGLANG_PATCH=1 is set. Ray runtime_env propagates this env var.
if ENABLE_MULTI_TURN:
    try:
        import baize_posttrain_sglang_patch as _patch
        if _patch.apply_patch():
            print(f"[wrapper] MiniCPM5 XML parser registered via baize_posttrain_sglang_patch "
                  f"(pid={os.getpid()})", flush=True)
        else:
            print(f"[wrapper] WARNING: Patch failed: {_patch.get_error()}", flush=True)
            print("[wrapper] Multi-turn tool calls will not work!", flush=True)
        # Also set env var so any Ray workers spawned by this process inherit it
        os.environ["BAIZE_SGLANG_PATCH"] = "1"
    except ImportError as e:
        print(f"[wrapper] WARNING: Cannot import baize_posttrain_sglang_patch: {e}", flush=True)
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
