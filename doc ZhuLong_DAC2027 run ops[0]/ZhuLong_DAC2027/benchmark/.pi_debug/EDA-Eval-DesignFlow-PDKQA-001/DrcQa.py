# DrcQa.py -- PDK QA System, DRC entry point.
# Migrated Windows->Linux. 17 registered checkers (supportFuncnames).
# DO NOT modify supportFuncnames (user requirement: problems recorded, not fixed).
import os, sys, importlib

SUPPORT_FUNCNAMES = [
    "ldr", "drcSyntax", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "patternDeviceLayer", "patternLayerVsFracture",
    "emptyDeriveLayer", "drcWithPattern",
    "patternLayerVsDesignRuleLayerChange", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]

# dead code (NOT registered, keep as-is): drcRuleContainsDeriveLayer

# Checker category map (text = no Calibre run; pattern = needs calibre/calibredrv)
TEXT_CHECKERS = [
    "ldr", "drcLayerMap", "drcValue", "drcOption", "drcPowerList",
    "drcDeriveLayerVsFracture", "drcDeriveLayerVsFractureAndTruthOverall",
    "uselessDeriveLayer", "drcConsistencyWithChangedLdr",
    "drcCountWithinOption", "antMetalThk",
]
PATTERN_CHECKERS = [
    "drcSyntax", "emptyDeriveLayer", "patternDeviceLayer",
    "patternLayerVsFracture", "patternLayerVsDesignRuleLayerChange",
    "drcWithPattern",
]


class DrcQa:
    """Main DRC QA driver. Dispatches to per-checker modules in DRC/text/ and
    DRC/pattern/."""

    def __init__(self, case_dir, deck="calibre"):
        self.case_dir = case_dir
        self.deck = deck  # "calibre" or "svrf"
        self.results = {}

    def run(self, names=None):
        names = names or SUPPORT_FUNCNAMES
        for fn in names:
            if fn in TEXT_CHECKERS:
                self.results[fn] = self._run_text(fn)
            elif fn in PATTERN_CHECKERS:
                self.results[fn] = self._run_pattern(fn)
            else:
                self.results[fn] = {"status": "unknown", "reason": "not registered"}
        return self.results

    def _run_text(self, name):
        mod = importlib.import_module("DRC.text." + name)
        return mod.check(self.case_dir, self.deck)

    def _run_pattern(self, name):
        # needs calibre / calibredrv; environment must be set up first
        import test_env
        ok, msg = test_env.check_calibre_env()
        if not ok:
            return {"status": "SKIP", "reason": msg}
        mod = importlib.import_module("DRC.pattern." + name)
        return mod.check(self.case_dir, self.deck)


if __name__ == "__main__":
    print("registered:", len(SUPPORT_FUNCNAMES))
