"""Terminal-Bench 7-harness agent adapters.

Uses lazy imports so that individual modules (e.g. ``terminalbench.agents._base``)
can be imported without triggering all 7 adapter imports (which require harbor).
"""

import importlib
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from terminalbench.agents.cline_patched import ClinePatched
    from terminalbench.agents.codex import CodexTB
    from terminalbench.agents.hermes import HermesTB
    from terminalbench.agents.opencode import OpenCodeTB
    from terminalbench.agents.claude_code import ClaudeCodeTB
    from terminalbench.agents.deepseek_harness import DeepseekHarnessTB
    from terminalbench.agents.pi import PiTB

_LAZY_NAMES = {
    "ClinePatched": "terminalbench.agents.cline_patched",
    "CodexTB": "terminalbench.agents.codex",
    "HermesTB": "terminalbench.agents.hermes",
    "OpenCodeTB": "terminalbench.agents.opencode",
    "ClaudeCodeTB": "terminalbench.agents.claude_code",
    "DeepseekHarnessTB": "terminalbench.agents.deepseek_harness",
    "PiTB": "terminalbench.agents.pi",
}

_HARNESS_MAP = {
    "cline-patched": "ClinePatched",
    "codex": "CodexTB",
    "hermes": "HermesTB",
    "opencode": "OpenCodeTB",
    "claude-code": "ClaudeCodeTB",
    "deepseek-harness": "DeepseekHarnessTB",
    "pi": "PiTB",
}


def __getattr__(name: str) -> Any:
    """Lazy-load adapter classes on first access (avoids importing harbor at package init)."""
    if name in _LAZY_NAMES:
        mod = importlib.import_module(_LAZY_NAMES[name])
        cls = getattr(mod, name)
        globals()[name] = cls  # cache for subsequent accesses
        return cls
    if name == "ALL_AGENTS":
        return {h: getattr(importlib.import_module(_LAZY_NAMES[c]), c)
                for h, c in _HARNESS_MAP.items()}
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "ClinePatched", "CodexTB", "HermesTB", "OpenCodeTB",
    "ClaudeCodeTB", "DeepseekHarnessTB", "PiTB",
    "ALL_AGENTS",
]
