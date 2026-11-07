#!/usr/bin/env python3
"""baize_posttrain_verl_wrapper.py — Wrapper to register MiniCPM5 parser THEN launch verl.

R21 (2026-11-07): CRITICAL FIX — baize_posttrain_rl_grpo.sh previously ran the parser
import in a SEPARATE process (`python -c "import baize_posttrain_minicpm5_parser"`),
which registered the parser in that throwaway process. When verl training started
in a different process, the "minicpm5" parser was NOT registered → tool calls
would not be parsed → multi-turn RL would silently degrade to single-turn.

This wrapper ensures the parser is registered IN THE SAME PROCESS as verl training.
Usage:
    python baize_posttrain_verl_wrapper.py [verl_args...]

It does:
    1. import baize_posttrain_minicpm5_parser  (registers "minicpm5" in ToolParser)
    2. from verl.trainer.main_ppo import main; main()
"""
import sys
import os

# Step 1: Register MiniCPM5 tool parser BEFORE verl imports it
# The parser module registers itself in ToolParser._registry on import
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

try:
    import baize_posttrain_minicpm5_parser
    print(f"[wrapper] MiniCPM5 ToolParser registered: 'minicpm5' in registry = "
          f"{'minicpm5' in baize_posttrain_minicpm5_parser.ToolParser._registry}",
          flush=True)
except Exception as e:
    print(f"[wrapper] WARNING: Failed to import MiniCPM5 parser: {e}", flush=True)
    print("[wrapper] Tool calls will NOT be parsed — multi-turn RL will not work!", flush=True)

# Step 2: Launch verl's main_ppo entry point with remaining args
try:
    from verl.trainer.main_ppo import main as verl_main
    print(f"[wrapper] Launching verl.trainer.main_ppo with args: {sys.argv[1:]}", flush=True)
    verl_main()
except ImportError as e:
    print(f"[wrapper] ERROR: Cannot import verl.trainer.main_ppo: {e}", flush=True)
    print("[wrapper] Make sure verl is installed in this venv.", flush=True)
    sys.exit(1)
except Exception as e:
    print(f"[wrapper] verl training exited with error: {e}", flush=True)
    raise
