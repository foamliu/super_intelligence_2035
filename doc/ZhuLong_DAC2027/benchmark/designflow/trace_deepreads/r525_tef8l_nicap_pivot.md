# trace_deepread r525 — 1794395853966_tef8l (yinyus@hfeg0plg66, mc=894)

**Session**: 1794395853966_tef8l, user=yinyus, host=hfeg0plg66, mc=894
**Status**: failed, 534 msgs, 2.1MB messages.json
**Domain**: layout_aether (Aether schematic netlist export + parsing)
**Keywords**: netlist:2255; schematic:2111; aether:1926; drc:1676; analog:417; pyaether:369; hspice:356

## USER#0 (task)
"帮我批量抽取网表，在/proj/drcpa/V0/workdir/yinyus/yinyus_nicap_block目录下的所有项目的schematic都抽取"
→ Batch extract netlists from all schematic projects in a directory.

## Task flow (27 user turns)
1. **USER#1**: Batch netlist extraction via Aether (pyAether dmExportNetlist / aeExportNetlistCDLShow). Assistant spent ~150 msgs searching APIs, wrote batch_export_netlist.sh using emy2netl. 9 cells: AG_CapYdecBOT_center_normal, AG_CapYdecBotLNormal, AG_CapYdecBotRNormal, AG_CapYdecTopCenterNormal, AG_CapYdecTopCenterTop, AG_CapYdecTopLNormal, AG_CapYdecTopLTop, AG_CapYdecTopRNormal, AG_CapYdecTopRTop.
2. **USER#2**: Parse one netlist (AG_CapYdecTopRTop), find `<**TopDesStart>`, extract elements into table (4 per row → 4 columns), output CSV.
3. **USER#3-4**: "每四行作一列" (4 rows per column); then merge cols 2+3 with "-", drop col1, col4→col2.
4. **USER#5-6**: Re-extract all; search for "drcoa" keyword (none found).
5. **USER#7-15**: Iterative CSV transforms: sort, count duplicates (col3=count), pivot/cross-tab (rows=subcell, cols=net_combo, vals=count, 0 if absent), swap row/col headers, corner cell=netlist name.
6. **USER#16**: Apply full pipeline to all 9 netlists → nicap.csv (vertical concat of _3 tables).
7. **USER#17-24**: Fix concat (vertical stack, don't change content), reorder columns by specific net order, delete AG_CXcap2S* rows.
8. **USER#25**: Read note text from schematics (separate sub-task).
9. **USER#26-27**: Re-extract netlists and redo full pipeline.

## Netlist format (Aether CDL export)
```
* Aether CDL Netlist Export
.SUBCKT <cellname>
**TopDesStart
<inst> <net1> <net2> <subcell>    ← 4 tokens per line
...
**TopDesEnd
.ENDS
```
Example: `XI_AG_CXcap1S151x167_1 vss! vncsg! AG_CXcap1S151x167`
- inst = XI_AG_CXcap1S151x167_1
- net1 = vss!, net2 = vncsg!
- subcell = AG_CXcap1S151x167

## Pipeline (core testable deliverable)
1. Parse: find **TopDesStart, extract instance lines (4 tokens each)
2. _2: drop inst, merge net1+"-"+net2 → net_combo, keep subcell
3. Count: occurrences of each (net_combo, subcell)
4. Pivot _3: rows=unique subcell (sorted), cols=unique net_combo (sorted), vals=count (0 if absent), corner=cell name
5. Aggregate: concat all _3 tables vertically → nicap.csv
6. Filter: delete rows where col1 starts with "AG_CXcap2S"

## Case design
- **Case ID**: EDA-Eval-DesignFlow-NicapNetlistPivot-001
- **Domain**: layout_aether, L2 (parse real Aether CDL tool output)
- **A (visible)**: 3 netlists (AG_CapYdecTopRTop, AG_CapYdecBOT_center_normal, AG_CapYdecTopLTop)
- **B (hidden)**: 3 netlists (AG_CapYdecBotRNormal, AG_CapYdecTopCenterTop, AG_CapYdecTopRNormal) — different cells, different nets (vkb!, viso!)
- **check.py**: 14 conditions (a-n), GOLD PASS, 5 negatives NEG_RC=0
- **trace_source**: real user request, real Aether tool, real netlist format

## r523 high-mc peek 盲区 refutation (continued)
r523 delivered DrcQaAutoPipe-001 (mku3e mc=603). r524 delivers tef8l mc=894 — second high-mc produce-task case from the [500+) bin. Confirms r523 thesis: high-mc segment is productive, r404-r522 92连0-case was peek选段偏差 (all peek落 low-mc段).
