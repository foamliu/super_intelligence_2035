;
; step3_aether.il -- aether (Empyrean) flow rewrite of step3_verify.il.
;
; Entry: aetherLE (layout editor) / aetherSE (schematic editor).  For
; schematic-level ERC verification this script is replayed inside aether
; (entered via aetherSE), opens drcpa_top/ddr5top/schematic with
; dbOpenCellViewByType, and runs the aether ERC verification hook.
;
; The legacy flow entry (nograph replay) and its library definition file
; are not used here.
;
lib = "drcpa_top"
cell = "ddr5top"
view = "schematic"
cv = dbOpenCellViewByType(lib cell view nil "r")
if(cv then
  printf("opened %s/%s/%s\n" lib cell view)
  ; run ERC verification on the opened schematic cell view
  aetherERCVerify(cv)
else
  error("could not open %s/%s/%s\n" lib cell view)
)