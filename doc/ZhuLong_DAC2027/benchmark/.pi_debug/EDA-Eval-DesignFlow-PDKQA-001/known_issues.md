# known_issues.md -- PDK QA migration, known issues

## K10: Calibre 2020.1_36 VCO autoswitch bug on RHEL 8
- Symptom: calibre/calibredrv/rules_syntax_checker fail with
  "VCO aok not supported by autoswitch" in non-interactive processes.
- Root cause: calibre_env script grep
    echo "_$SW_WKSTN_$MGC_VCO_" | grep -q '_ao[j-z]_'
  uses shell variable names with a trailing underscore (parsed as empty),
  so autoswitch never matches the aok tree.
- Setting CALIBRE_HOME alone does NOT fix it (calibre_env runs calibre_vco
  unconditionally).
- Workaround (test-env only): fake MGC_HOME + bin/calibre_vco stub returning
  'aoi' + stub libXss.so.1 + LD_LIBRARY_PATH to real aoi libs; auto-rebuild
  at import.  Classified as environment infrastructure bug, not project
  responsibility.
- (placeholder -- detail to be filled in PHASE2_REPORT.md)
