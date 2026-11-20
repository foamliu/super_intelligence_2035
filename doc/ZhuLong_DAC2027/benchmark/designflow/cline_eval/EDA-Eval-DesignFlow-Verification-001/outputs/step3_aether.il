;==============================================================================
; step3_aether.il -- ERC schematic verification for the AETHER project.
;
; PROJECT: drcpa_top (Empyrean Aether project).
;
; ENTRY:   run `vir` and select the drcpa_top project, then enter Aether via
;          aetherLE (layout editor) or aetherSE (schematic editor). For batch
;          replay, run `aether -nograph -replay step3_aether.il`.
;
; WHAT IT DOES:
;   1. Points Aether at the project's aether-ready lib.defs -- which INCLUDEs
;      the aether tool lib.defs and SKIPs amsLib -- then reloads the lib list.
;   2. Opens drcpa_top/ddr5top/schematic with dbOpenCellViewByType.
;   3. Runs the schematic ERC check hooks on the opened cellview and closes it.
;==============================================================================

;------------------------------------------------------------------------------
; tbcload1.7 path pitfall:
;   Aether bundles its own Tcl bytecode loader (tbcload 1.7, surfaced through
;   AETHER_TBCLOAD_LIBRARY). Do NOT prepend a foreign tbcload directory to
;   TCLLIBPATH / auto_path here -- a foreign tbcload would shadow the bundled
;   tbcload1.7 and break the Tcl loader before any SKILL runs. Leave
;   AETHER_TBCLOAD_LIBRARY untouched and let the `vir` -> aetherLE/aetherSE
;   launcher set things up.
;------------------------------------------------------------------------------

; Point Aether at the project's aether-ready lib.defs. That file INCLUDEs the
; aether tool lib.defs and SKIPs amsLib (amsLib is pulled in by the aether tool
; lib.defs but is not usable in this project and would break the aether load).
when(isFile("./lib.defs")
  dmSetForcedLib("./lib.defs")
  dmUpdateLibList()
  printf("[step3_aether] lib.defs loaded (INCLUDE aether lib.defs + SKIP amsLib)\n")
)

libName  = "drcpa_top"
cellName = "ddr5top"
viewName = "schematic"

cv = dbOpenCellViewByType(libName cellName viewName nil "r")

when(null(cv)
  printf("ERROR: cannot open %s/%s/%s\n" libName cellName viewName)
  exit(1)
)

printf("[step3_aether] opened %s/%s/%s\n" libName cellName viewName)

; run the schematic ERC check hooks on the opened cellview
errWarn = dbSeCheckDesign(cv)
printf("[step3_aether] dbSeCheckDesign -> %L\n" errWarn)

; close the cellview
dbClose(cv)
printf("[step3_aether] done\n")