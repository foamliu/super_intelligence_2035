; step3 verify — VIRTUOSO flow (DEPRECATED: this project is an AETHER project).
; This .il must be REWRITTEN as an aether flow (vir -> aetherLE/aetherSE).
;
; Known issues with the virtuoso path on this project:
;   - virtuoso cannot start (LD_LIBRARY_PATH / libstdc / CXXABI version conflict,
;     IC617 ISR23 / IC618 ISR11 / oa_v22.60.036 mismatch);
;   - the project libraries are defined for aether (Empyrean), not Cadence cds.lib.

; --- virtuoso direct invocation (TO BE REMOVED in the aether rewrite) ---
virtuoso -nograph -replay <<'SKILL_EOF'
lib = "drcpa_top"
cell = "ddr5top"
view = "schematic"
cv = dbOpenCellViewByType(lib cell view nil "r")
printf("opened %s/%s/%s\n" lib cell view)
; load cds.lib for Cadence library definitions
cds.lib
; run ERC verification hooks on the opened schematic
ercVerifyCV(cv)
SKILL_EOF
