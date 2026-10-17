"""Terminal-Bench 2.0 — 7-harness cross-evaluation adapters for Harbor.

This package contains custom Harbor agent adapters for the same 7 harnesses
used in the SWE-bench 7×300 evaluation:
    cline-patched / codex / hermes / opencode / claude-code / deepseek-harness / pi

Each adapter is a ``BaseInstalledAgent`` subclass that preserves the native
tool loop (read / write / execute / multi-turn fix) of its harness.

Model backbone: kimi-k2.6-cloud (http://agi-gateway.cxmt.com/cloud/v1)
"""

# Agent import paths for Harbor --agent
AGENT_IMPORT_PATHS = {
    "cline-patched": "terminalbench.agents.cline_patched:ClinePatched",
    "codex": "terminalbench.agents.codex:CodexTB",
    "hermes": "terminalbench.agents.hermes:HermesTB",
    "opencode": "terminalbench.agents.opencode:OpenCodeTB",
    "claude-code": "terminalbench.agents.claude_code:ClaudeCodeTB",
    "deepseek-harness": "terminalbench.agents.deepseek_harness:DeepseekHarnessTB",
    "pi": "terminalbench.agents.pi:PiTB",
}

__all__ = ["AGENT_IMPORT_PATHS"]
