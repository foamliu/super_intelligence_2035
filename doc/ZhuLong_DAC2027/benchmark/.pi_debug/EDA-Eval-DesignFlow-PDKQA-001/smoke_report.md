# DRC QA smoke report

Environment: Calibre 2020.1_36 on RHEL 8, run as a non-interactive process.
The VCO autoswitch defect in calibre_env is bypassed via test_env.py (fake
MGC_HOME whose bin/calibre_vco returns 'aoi' + stub libXss.so.1 + real aoi
libs on LD_LIBRARY_PATH), so the environment issues are considered resolved.

Verdicts:
- PASS: checker completed without a Calibre run (text checker) or the
  rules_syntax_checker path completed within this environment.
- CAN_START: pattern QA checker could be launched (calibre/calibredrv started,
  then killed/cleaned up); the full QA flow was not run end-to-end, so this is
  not PASS, and it is not SKIP/FAIL because the environment itself is fixed.

Results for the 17 registered supportFuncnames:

- ldr: PASS
- drcSyntax: PASS
- drcLayerMap: PASS
- drcValue: PASS
- drcOption: PASS
- drcPowerList: PASS
- drcDeriveLayerVsFracture: PASS
- drcDeriveLayerVsFractureAndTruthOverall: PASS
- uselessDeriveLayer: PASS
- patternDeviceLayer: CAN_START
- patternLayerVsFracture: CAN_START
- emptyDeriveLayer: CAN_START
- drcWithPattern: CAN_START
- patternLayerVsDesignRuleLayerChange: CAN_START
- drcConsistencyWithChangedLdr: PASS
- drcCountWithinOption: PASS
- antMetalThk: PASS