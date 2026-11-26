# Deepread: 1784254184878_zd84z — net highlight probe (schematic_netlist)

- **session**: `1784254184878_zd84z` · user `e0014566` · host `hfeg0plg58` · mc=28 · nmsg=23
- **domain**: schematic_netlist (A-faithful, L1-boundary)
- **selected round**: U#0 (msg 0) — clean 提需求轮 (提出目标, no rootcause/fix from user)

## User intent (U#0 逐字)
```
在Schematic中,帮我高亮当前打开的设计图中所有名称以"net 开头的线
要求:建指定类型的探针标记颜色为红色,高亮必须在屏幕上可见
注意:你要使用skill代码实现和执行
```

## Agent flow
1. RAG search_apis: `get current schematic cellview`, `highlight net probe mark`, `get all nets in schematic` → found `geAddNetProbe`, `geAddNetProbeFromTo`, `dbStartGenNet`.
2. get_api_details on those + further search → found `geMakeProbeWithColor`, `geMakeProbeWithoutColor`, `geGetEditCellView`, `geSetProbeUserLPP`.
3. More search: `geDeleteAllProbe`, `hiRedraw`, `hiGetCurrentWindow`, `geSetTCProbeDisplayStyle`.
4. editor (msg 20): wrote SKILL `let` block — `hiGetCurrentWindow()` → win; `geGetEditCellView(win)` → cv; `cv~>nets` → netList; foreach net: `net~>name`, `rexMatchp("^net" netName)` filter; `geMakeProbeWithColor(?window win ?name strcat("netHighlight_" netName) ?object net ?color list("hilite" "drawing7") ?probeType "net" ?displayStyle "object")`; `when(probeObj geSetTCProbeDisplayStyle(probeObj t t))`; `hiRedraw(win)`.
5. SandBox run_code (lang=skill) executed it.
6. msg 22: report — current cellview `AbusTriVDrv`; highlighted `net15`, `net16` (2 nets) with red hilite/drawing7 probe. User implicitly accepted (trace ends, no rejection).

## Gold
The SKILL code (msg 20 run_code input) is the full gold. Real Aether GUI execution is non-deterministic, so for an offline L1 benchmark we degrade "execute SKILL in Aether" → "emit the SKILL script + a selection plan from a config". Generator `gen_net_highlight.py` is config-driven (cell_name / nets / prefix / color / probe_type / display_style) and reproduces the exact SKILL structure + prefix-selection logic.

## Why A-faithful
- Task说明 = U#0 逐字 (no rewrite, no synthesized brief of "what to do").
- User only states the goal; does NOT point at root cause or give a fix.
- Gold = the agent's actually-produced & accepted SKILL code (real tool artifact).
- Hidden B = different cell (LvlShftOutBuf_B) + disjoint net namespace + bus-bit + substring-not-prefix edge cases, structurally different from A.

## Case
`EDA-Eval-DesignFlow-NetHighlightProbe-001` · L1-boundary schematic_netlist
- assets A: prompt.txt (U#0 逐字) + task_brief.md + config_A.json (AbusTriVDrv, 10 nets, 2 match net15/net16)
- hidden B: config_B.json (LvlShftOutBuf_B, 14 nets, 5 match incl bus bits net_data[0]/[1]; substring-not-prefix my_net1/vinet/xnet must be excluded) + hidden_manifest.json
- check.py: 15 条件 a-o (zip/py_compile/run/4 SKILL-API-structure/4 plan-selection/cross-guard/determinism+§4.9-fakes)
- negatives: fake_empty (→c) / fake_print_fixed_A (→i) / fake_core_deleted (→i/j/m) / naive_substring (→f) / naive_no_prefix (→f)
- self-verify: ref PASS 15/15 · 5 neg ALL-FAIL · §4.9 三假 distinct {c,i,j,k,m,n} ≥3 ✓ · k_rationale==k_check==15 ✓
