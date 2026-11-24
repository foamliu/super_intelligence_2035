# Deepread: 1795426299983_t99ng — Virtuoso SKILL PCell tap_p/_SKILL refactor

## Trace source
- session: 1795426299983_t99ng
- user: hktklin
- host: hfeg0plg87
- mc: 142 (virtuoso:193;cellview:184;dbcreaterect:111;ddgetobj:83;dbget:72;dbcreatepath:28)
- domain: layout_virtuoso
- messages: 91

## Real task summary
User repeatedly asks (6x for L20, 1x for L54): in directory
`/proj/lacaa/TV1_FS_Virtuoso/workdir/hktklin/skl/L{54,20}/AMN3P/`
replace file **content** `tap_p` -> `lacaa_common` and remove `_SKILL`
from cell names. Filenames must stay unchanged (keep `_SKILL` suffix).

The `.il` files are Virtuoso SKILL `pcDefinePCell` PCell definitions.
Header pattern:
```
pcDefinePCell(list(ddGetObj("tap_p") "common_AMN_L54_pcell_SKILL" "layout")
```
After fix:
```
pcDefinePCell(list(ddGetObj("lacaa_common") "common_AMN_L54_pcell" "layout")
```

## File inventory
### L54/AMN3P (8 files = 7 .il + readme)
- common_AMN_L54_pcell_SKILL.il — NEEDS FIX (has tap_p + _SKILL)
- common_tap_L54_H_pcell_SKILL.il — already correct
- common_tap_L54_coner_pcell_SKILL.il — already correct
- common_tap_L54_edge_V_pcell_SKILL.il — already correct
- common_tap_L54_edge_coner_pcell_SKILL.il — already correct
- common_tap_L54_edge_lr_fin2_pcell_SKILL.il — already correct
- common_tap_L54_lr_fin2_pcell_SKILL.il — already correct
- readme — load script (unchanged)

### L20/AMN3P (10 files = 9 .il + readme)
- common_AMN_L20_pcell_SKILL.il — already correct
- common_tap_L20_H_pcell_SKILL.il — already correct
- common_tap_L20_coner_pcell_SKILL.il — NEEDS FIX (reverts between runs)
- common_tap_L20_edge_V_pcell_SKILL.il — already correct
- common_tap_L20_edge_coner_pcell_SKILL.il — already correct
- common_tap_L20_edge_lr_fin2_pcell_SKILL.il — already correct
- common_tap_L20_edge_lr_fin4_pcell_SKILL.il — NEEDS FIX (added later)
- common_tap_L20_lr_fin2_pcell_SKILL.il — NEEDS FIX (reverts)
- common_tap_L20_lr_fin4_pcell_SKILL.il — NEEDS FIX (reverts)
- readme

## Fix algorithm (from fix_AMN3P_tap.py / fix_tap_p_v2.py)
```python
content = content.replace("tap_p", "lacaa_common")
content = content.replace("_SKILL", "")
# write back; filename unchanged
```

## Verification (from verify_AMN3P_content.py)
Scan all files; assert no "tap_p" or "_SKILL" in any line of any file.

## Case design (PcellSkillRefactor-001)
- Sample A = L54/AMN3P (7 .il + readme, 1 needs fix)
- Hidden B = L20/AMN3P (9 .il + readme, 4 need fix) — different scale/files
- check.py: 10 independent conditions (zip valid, file count, no tap_p,
  no _SKILL, ddGetObj lacaa_common, cell name no _SKILL, filenames unchanged,
  readme preserved, pcDefinePCell 3-elem list, "layout" view preserved,
  subprocess grep)
