# Deepread: of070 · jzeng · V4 pad between same-power M4/M5

**Trace**: `1794831480408_of070.messages.json` (jzeng @ hfeg0plg85, mc=446, 1.03MB / 304 msgs / 164 user · 140 assistant)
**Snapshot**: 2026-11-19, ssh hfeg0plg85 → /home/jzeng/.cline/data/sessions/1794831480408_of070/1794831480408_of070.messages.json (scp OK, subdirectory path correct per r818 fix)
**Domain**: layout_aether (pyAether script-writing)
**子型**: pyaether-via-pad-generator (same-power metal overlap → 2um×2um pad + via placement)

## User intent (verbatim, 3 real user inputs)

- **U#0 (msg0)**: `参考/proj/drcpa/V0/agentdir/jzeng/IMCleAutoVia.py,写一个脚本，在相同power的M4 M5之间生成V4，M4 M5宽度为0.55um，长度较长，M4 M5可能为path pathseg rect等，需要先在连到同一个power的M4 M5交叠处生成2um x 2um的M4 M5，使其生成V4时没有DRC`
  - Intent: Write a pyAether script that, for M4/M5 wires (~0.55um wide) on the **same power net**, (1) finds overlap locations, (2) creates **2um×2um M4+M5 pads** at each overlap (to make V4 via DRC-clean), (3) places V4 vias. Shapes may be path/pathSeg/rect/polygon.
- **U#1 (msg184)**: `生成的cell需要在auto_via库`
  - Constraint: the generated via-pad cell must be placed in the `auto_via` library.
- **U#2 (msg296)**: `无法生成V4`
  - Bug report: V4 via generation failed (drove further iteration).

## Assistant trajectory

- 73 `editor` writes (heavy iteration), 37 `read_files`, 22 `RAG_MCP_Server__search_apis` (pyAether API lookup), 22 `run_approved_command`, 4 `list_allowed_files`.
- Files produced: `gen_v4_between_power_m4m5.py` (main, 31 versions, final msg279 3202 chars), `_w.py` (15 v), `_build_v4pad.py` (8 v), `build_v4pad.py` (1 v, 6469 chars), `_write_gen_v4.py` (6 v), `b.py` (5 v), `_build_final.py` (4 v), `_check_syntax.py` / `_check_syn.py` (syntax check helpers).
- Reference `/proj/drcpa/V0/agentdir/jzeng/IMCleAutoVia.py` — not accessible to e0031982 (Permission denied); assistant read it via `run_approved_command` (jzeng-approved sandbox).

## Final algorithm (extracted from `gen_v4_between_power_m4m5.py` msg279)

```
TW=0.55 (target width), WT=0.02 (width tolerance), PS=2.0 (pad size),
HP=PS/2.0=1.0 (pad half-size), MG=PS+0.1=2.1 (dedup merge gap),
LH=0.05, BY=0.047 (via params).

1. cv = aeGetCurDesign(); lib, cel = cv.libName, cv.cellName
2. tech lookup: try ae.techGetTechLib(lib) → techGetTechFile; fallback TECHLIB
3. via name resolution: try "V4_V" → fallback ["V4_L_V","V4_m_V","V4_A_V","V4"]
4. m4 = _cl(cv, "M4.drawing", TW, WT)  # collect M4 shapes with width≈0.55±0.02
   m5 = _cl(cv, "M5.drawing", TW, WT)
5. overlap detection:
   for (b4,n4) in m4, (b5,n5) in m5:
     if n5 != n4: continue          # SAME-NET only
     xl=max(b4.l,b5.l); xr=min(b4.r,b5.r)
     yb=max(b4.b,b5.b); yt=min(b4.t,b5.t)
     if xl<xr and yb<yt: ra.append(((xl+xr)/2, (yb+yt)/2, n4))   # overlap center
6. dedup: ra = _dp(ra)  (deduplicate centers)
7. filtered: keep a center if no already-kept center within MG=2.1um
8. create auto_via lib + V4PAD_CELL (cel+"_V4PAD_CELL"):
     dbCreateLib("auto_via"); techSetTechLibName; dbNewCellView / dbOpenCV w + dbDeleteAll
     _cell(td, vn, ocv, HP, LH, BY)  # build via cell content
     dbComputeBBox; dbSaveCV; dbCloseCV
9. place in top cell (if writable):
     for (cx,cy,nm) in fi:
       dbCrtInst(tcv, cellName=OC, libName="auto_via", point=(cx,cy), orient="R0")
       b = emyBoxF(cx-HP, cy-HP, cx+HP, cy+HP)   # 2um×2um pad box
       r4 = dbCrtRect(tcv, b, "M4", "drawing")
       r5 = dbCrtRect(tcv, b, "M5", "drawing")
       no = dbFindNetByName(tcv, nm); dbAddFigToNet(r4, no); dbAddFigToNet(r5, no)
```

## Reframe rationale (A档 → B档)

- **A档 gold** = the pyAether script (`gen_v4_between_power_m4m5.py` main()): uses `ae.db*` / `ae.tech*` / `ae.emy*` APIs that require a **live Aether session** — cannot run in offline sandbox → no `subprocess`-executable candidate → no teeth (§4.2 fails).
- **B档 reframe** = pure-Python `v4_pad_gen.py` (stdlib only) that captures the **same algorithmic core** on JSON geometry input:
  - Input `<shapes.json>`: list of `{id, layer:"M4"|"M5", net, type:"rect"|"path"|"pathseg"|"polygon", bbox:[xl,yb,xr,yt], width}`.
  - Algorithm: width-filter (0.55±0.02) → same-net M4∩M5 overlap centers → dedup (merge gap 2.1um) → emit 2um×2um pads + via instances in `auto_via` lib.
  - Output JSON: `{stats:{m4_count,m5_count,width_filtered_m4,width_filtered_m5,overlap_count,filtered_count,pad_count,via_count}, pads:[{cx,cy,net,xl,yb,xr,yt,size}], vias:[{cx,cy,cell_name,lib_name,net}], via_cell:{lib:"auto_via",cell:"<top>_V4PAD_CELL"}, config:{TW,WT,PS,HP,MG}}`.
  - `sort_keys=True` for determinism.
- **Visible A** = synthetic M4/M5 geometry (3 nets, ~8 shapes, 4 overlaps, 3 dedup survivors) — derived from trace intent (0.55um M4/M5 same-power).
- **Hidden B** = different geometry (5 nets, ~14 shapes, 6 overlaps, 4 survivors; different nets/coords/counts) — structural anti-hardcode.

## Check.py ≥8 teeth (planned: 16 conditions a-p)

a. zip valid + contains `v4_pad_gen.py`
b. `py_compile` exit 0
c. hidden B run exit 0 + stdout valid JSON
d. B output has top-level keys `stats/pads/vias/via_cell/config`
e. B `stats.m4_count`/`m5_count` match B input (anti-hardcode A counts)
f. B `stats.width_filtered_*` match expected B-specific counts (width filter 0.55±0.02)
g. B `stats.overlap_count` == expected same-net overlap count (B-specific)
h. B `stats.filtered_count` == expected dedup survivors (B-specific, MG=2.1)
i. B `pads` count == `stats.pad_count` == `stats.filtered_count`
j. B each pad `size` == 2.0 (PS=2um×2um)
k. B each pad bbox == [cx-1, cy-1, cx+1, cy+1] (HP=1.0)
l. B each pad `net` == the M4/M5 same-net at that overlap (no cross-net)
m. B `vias` count == `pads` count (one via per pad)
n. B `via_cell.lib` == "auto_via" AND `via_cell.cell` ends with "_V4PAD_CELL"
o. B output contains no A-specific literals (A net names / A coords) — anti-hardcode
p. determinism: 2x runs byte-identical (md5)
q. missing-input: exit≠0 when shapes file absent

## §4.9 三假提交 (must all FAIL)

- (a) empty stub: solve.py with `pass` → fail at (b) py_compile? No, pass compiles. → fail at (c) no JSON output.
- (b) print-only: prints expected JSON string but doesn't compute → fail at (o) anti-hardcode (A literals absent? it prints A-literals → but B expects B-literals → fail at (d)/(e)/(f)).
- (c) core-deleted: width-filter or overlap-detection neutered → fail at (f)/(g)/(h).

## Trace-source metadata

- `user`: jzeng
- `host`: hfeg0plg85
- `session_file`: 1794831480408_of070.messages.json
- `match_count`: 446
- `real_task_summary`: "写一个 pyAether 脚本，在相同 power net 的 M4/M5（~0.55um 宽）交叠处生成 2um×2um M4+M5 pad + V4 via，输出到 auto_via 库；支持 path/pathSeg/rect/polygon；目标 DRC-clean。trace 内 304 msgs/73 editor 迭代，最终脚本 gen_v4_between_power_m4m5.py main()。"
