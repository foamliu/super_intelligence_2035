# Deepread: zdo8r — Aether Transistor Matching Helper

- session: `1793937823141_zdo8r` (dir-based: sessions/zdo8r/zdo8r.messages.json, 1.64MB, 514 msgs)
- user/host: t0002038 @ hfeg0plg86 (also appears on hfeg0plg90, hfeg0plg96)
- mc=585, tools: pyAether(299) dbGet(59) schematic(39) "lang":"pyAether"(29) cellview(18) netlist(12) dbCreateInst(9) calibre(6)
- domain: analog_context (analog layout transistor matching methodology; reads schematic CDF params w/l/finger/m/stack)

## Real user intent (verbatim)
- U#0 (×3 retries): 「你能写一个在aether里面帮助模拟版图直接做管子匹配的脚本吗？我能帮你什么？」
  → write a pyAether script to help with transistor matching directly in analog layout
- U#113: 「如何运行」
- U#115: error — cellview name mismatch `ddgoa_cmos_work/GlbBiasGenNmirUnitIP/physconfig` vs `TT/tt/physconfig`
- U#254: shows running header `Aether Transistor Matching Helper v1.0`, license checkout, Design `ddgoa_cmos_work/VfsygtAmpCoreIP/layout_1`
- U#268: 「! No objects selected! 显示我没有选中任何东西」
- U#380: 「! Found 0 MOS, need >=2」 — debugging MOS detection (db object pointers)
- U#406: dir of `emyScalarInst` — exploring instance API (addToCluster/bbox/cdfParameter/cellName/copy/dbuBox/...)
- U#436: 「我们目前所用到有 ptn ptk_lv ptn_lvio ptn_m这几种，n管类似」 (P-type transistor types used; N similar)
- U#452: SyntaxError `default 'except:' must be last`
- U#460: 「成功了出现了distributed align窗口，如何使用？」 (success — distributed align window appeared)
- U#462: 「先帮我加入快捷键3」 (add hotkey 3)

## Agent tool chain
- RAG_MCP_Server__search_apis (23) + get_api_details (6): looked up pyAether APIs (aeGetSelectedSet, aeEmyInstGetParameter, cdfGetInstCDF, leGuiDeviceMatch, leGuiDistrAlign, aeSetBindKeys)
- read_files (54): read session/instance API docs
- run_approved_command (84): ran check_syntax.py / gen_helper.py / create_full.py / append_p2.py / apply_fix.py / write_final.py — built the script incrementally (ASCII encoding constraints in pyAether env → chunked generation)
- editor (90): edited the helper file
- Final deliverable: `/home/t0002038/Desktop/aether_transistor_match_helper.py` (210 lines, 6710 bytes)

## Real deliverable (aether_transistor_match_helper.py v1.0)
Core functions:
- `gpr(inst,pn,d)` / `gpf(inst,pn,d)`: get CDF param (w/l/finger/m/stack) via `ae.aeEmyInstGetParameter` + fallback `ae.cdfGetInstCDF`
- `gmn(inst)`: get master cell name (getCellName/cellName/getMaster/master)
- `ismos(inst)`: detect MOS by `isDevice()` + master name keyword (nmos/pmos/nch/pch/nmis/pmis/mos/nfet/pfet/fet/ptn/ptk/ntn/ntk/n_/p_)
- `gp(inst)`: extract {w,l,f,m,s,master,name}
- `parse(cv)`: get selected set (aeGetSelectedSet/aeGetSelSet/aeGetObjectSelectedSet, fallback cv.instances), filter to MOS, require >=2
- `anal(cv,mos)`: print table, group by (master,w,l,f,m) then by (master,w,l); suggest match type (2→Diff pair interdigitated/CC, 4→Common Centroid, 8→2x2 ABBA+Dummy, else Array+Dummy)
- `mint(cv,pr)`: interdigitated match for 2 devices → `ae.leGuiDeviceMatch()`
- `mcc(cv,grp)`: common centroid → `ae.leGuiDeviceMatch()`
- `spchk(cv,mos)`: split check (M>1 or F>1 → flag for Split MFactor)
- `dmy(cv,mos,n=2)`: dummy guide (PMOS G→VDD, NMOS G→VSS)
- `aln(cv,mos)`: distributed align → `ae.leGuiDistrAlign()`
- `auto(cv,mode="auto")`: main flow parse→anal→spchk→per-group mint/mcc→aln→dmy, footer "Done!"
- `_hk_int/_hk_cc/_hk_aln`: hotkey handlers
- `main()`: `ae.emyInitAether("-adv")` → `ae.aeGetCurDesign()` → `ae.aeSetBindKeys("layout", [["3",...],["4",...],["5",...],["6",...]])` → `auto(cv,"auto")`

## Private/unreplicable
- Real Aether layout `ddgoa_cmos_work/VfsygtAmpCoreIP/layout_1` (DRAM amp core) — not in SUT sandbox
- Real pyAether runtime / license — not available to SUT or judge
→ B-grade synthesized: mock pyAether module provides synthetic layout cellview + instances; check runs candidate script's main() against hidden mock B via sys.modules injection, asserts stdout structure + recorded API calls (leGuiDeviceMatch / leGuiDistrAlign / aeSetBindKeys).

## Case plan
- ID: EDA-Eval-DesignFlow-TrMatchHelper-001
- domain: analog_context, B-grade synthesized L2
- A (visible): mock_pyAether_A.py (layout A: 2×ptn diff pair + 4×ntn_lv CC + 2×ptk_lv M=2 array + 2 non-MOS) + test_runner_A.py for SUT self-test
- B (hidden): mock_pyAether_B.py (layout B: 2×ptn_lv diff pair + 4×ntn CC + 2×ptn_m M=4 array + 2 non-MOS — different masters/counts/params)
- check.py: subprocess-exec candidate script with mock B in sys.modules, capture stdout + mock call log; 14 conditions a-n (zip含/py_compile/import pyAether/main runs/MOS count==8/group names/diff pair suggestion/CC suggestion/split check M>1/aeSetBindKeys called/leGuiDeviceMatch called/leGuiDistrAlign called/anti-hardcode A-vs-B group names differ/Done footer)
- negatives: empty / print_only / core_deleted / hardcode_A
- 3-seed: shuffle B instance order, assert consistent grouping
