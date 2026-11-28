# 300nu deepread — ellawu@hfeg0plg83 ella2 implant-fill deck gen (DUPLICATE)

- session: `1795761954530_300nu.messages.json` (PATH-FIX subdir), 168 msgs / 693KB
- user: ellawu @ hfeg0plg83, mc188, keywords: calibre:1490+drc:712+virtuoso:240+.gds:162+aether:101+pyaether:71+lvs:42
- domain: physical_verify (implant fill)

## User intent (real, design_flow produce-task)
- U0: "使用 /home/ellawu/Desktop/agent/implant_fill_skill/SKILL.md 给当前打开的版图生成flatten的implant"
- U21: target path `/proj/drvqa/V0/workdir/ellawu/stdcells_ella/ella2`
- U53 ask_spacing → user picks KGX spacing 0.667
- U151: "生成了吗"

## Real tool chain
1. read SKILL.md (implant_fill_skill) → mandatory inputs: proj/ver/lib/cell/层→间距
2. RAG search_apis → run_code pyAether `mdeGetCurrentLibCellView` (isolated from GUI, returns ())
3. ask_question for path → user gives ella2
4. read project.table → (drvqa,V0)→Process=cxmtV2B
5. pyAether probe ella2 layout → implant layer = **KGX (122/0)** (NOT ella1's NCH3=14/0); ella2 has no prior implantFlag fill
6. diag script grep deck `cxmt10G7_fillImpDRC.rul` → confirms `FILL_IMPLANT_KGX` macro + KGX_gap/KGX_hole supported
7. read ella1 prior successful run artifacts (runFillImplant.rule, ella1.drc.results)
8. ask_question spacing → 0.667
9. **STEP1 asOut export** ella2→ella2.gds (size 2048) + **generate_deck()** modifies template:
   - inject `VARIABLE SPACE_VALUE_KGX 0.667`
   - `CMACRO FILL_IMPLANT_KGX SPACE_VALUE_KGX KGX_gap KGX_hole`
   - `KGXhole = FLATTEN KGX_hole` / `KGXgap = FLATTEN KGX_gap`
   - `FILL_DFM_RDB{ DFM RDB GDS implantFill_flatten.gds KGXhole 122 0 KGXgap 122 0 APPEND _auto_fill}`
   - rewrite LAYOUT PATH/PRIMARY/DRC RESULTS/SUMMARY
   → workdir `/proj/drvqa/V0/workdir/ellawu/auto_implant_run/ella2_20261127_150705`
10. **STEP2 calibre fill** → BLOCKED: sandbox host hfeg0pkn002 is VCO=aok, only aoi/neutral calibre trees run but all fail `DRC(Hierarchical)`+`DFM Non-Nodal RDB` license. ella1 succeeded on hfeg0plg107 (VCO=aoi) with 2022.3. Agent tries many calibre trees × license servers, strict_vco_check=no, bsub, ssh design host (host key denied) — all blocked. Fill GDS never generated.

## generate_deck() algorithm (faithful, portable core)
Template markers: `//VARIABLE SPACE_VALUE`, `//CMACRO`, `//FLATTEN`, `//DFM`, `LAYER OPERATION`.
- replace/insert `VARIABLE SPACE_VALUE_<key> <spacing>` for keys in layerDict
- derive CMACRO from DMACRO (D→C prefix, strip `{`, SPACE_VALUE→SPACE_VALUE_<key>); insert if missing
- filter: drop VARIABLE/CMACRO for layers not in dict; drop lines with `= FLATTEN`
- after `//FLATTEN`: insert `<key>gap = FLATTEN <key>_gap` / `<key>hole = FLATTEN <key>_hole`
- after `//DFM`: insert `FILL_DFM_RDB{` + `DFM RDB GDS implantFill_flatten.gds` + `<key>gap\t<num>\t0` / `<key>hole\t<num>\t0` (num from layerFile lookup of `<key>_drawing` prev line parts[2]/parts[4]) + `APPEND _auto_fill}`

## Verdict: DUPLICATE — parked, no case
- Existing case `EDA-Eval-DesignFlow-ImplantFillDeckGen-001` (vmvz6, ellawu@hfeg0pkn005, mc285) already covers the SAME algorithm (same user ellawu, same IMCleFillImplantDrc generate_deck codebase, same deck-gen-from-template task).
- 300nu is a different session/cell (ella2/KGX vs ella3) but identical underlying produce-task → weak duplicate, not a new case.
- LIVE-NA: calibre fill can't ship (license/VCO/GDS); only deck-gen algorithm portable (pure Python text manipulation, statically checkable) — already covered by existing case.
