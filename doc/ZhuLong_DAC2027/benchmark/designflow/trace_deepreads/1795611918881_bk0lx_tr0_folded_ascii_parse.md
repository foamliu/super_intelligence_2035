# Deepread: 1795611918881_bk0lx (adaml @ hfeg0plg05)

## Trace metadata
- user: adaml, host: hfeg0plg05 (10.129.8.139), mc=296
- keywords: netlist:537; hspice:404; schematic:189; aether:189; virtuoso:170; pdk:170; lvs:67; synopsys:56
- session: 526 msgs (274 user / 252 assistant), agent=lead
- 2 real user_input blocks

## User intent (msg #0, verbatim)
> 抽取TSPC_RVT的网表（/proj/m2701/V0_DDR4/workdir/adaml/Test/TSPC_RVT），撰写激励仿真这个电路tSetup,tHold,tCK2Q, 复位时间。而且要求采0采1时的tCK2Q要匹配。同时也要关注功耗和mismatch variation。电压范围0.85～0.92V，温度区间-40~130摄氏度。然后迭代修改schmatic，直到最优。

## Assistant tool chain
1. Explored project structure, found netlist at sim/TSPC_RVT/02_netlist/pre/TSPC_RVT.pre.sp
2. Fixed netlist: 17 `ivdd`→`vdd` substitutions (Aether sense node → power) via fix_netlist.py
3. Built HSPICE testbench, ran DC + transient (vdd=0.88V)
4. **20+ iterations parsing HSPICE post=1 folded-ASCII .tr0 output** (msgs 303-427):
   - Tried fixed-width slicing (15, 16 chars), regex extraction, various line-width computations
   - Discovered: fields are 15 chars right-justified, lines wrap at ~78-80 chars, records span 2-3 lines
   - Discovered: marker line `$&%#` with bogus values `-9992007E-210` pollutes regex parsing
   - Discovered: form-feed `\f` between pages contaminates last field
   - Discovered: `i(vvdd)` current interleaved with time column (TIME is LAST column, not first)
   - Discovered: header names wrap at 80 cols (`v(ck` / `k)`)
   - Eventually switched to `.measure` CSV output for reliable results (msg 425+)
5. Found circuit doesn't switch (Q only swings 0.957→0.762V, not rail-to-rail)
6. Diagnosed root cause: sch.oa check report shows ALL 20 transistors have floating D/B/G pins - schematic was never connected
7. Connected to Aether bridge on hfeg0plg05:56981, opened schematic (35 instances, 15 nets, 4 ports)

## 6 format gotchas extracted (verbatim from trace struggle)
- G1: trailing space stripped → variable line lengths, can't compute field width from line length
- G2: one time point's data spans multiple lines (5 fields per line × ceil(N/5) lines)
- G3: marker line `$&%#` + bogus values `-9.992007E-204` → regex/float eats them as data
- G4: form-feed `\f` between pages → contaminates last field
- G5: TIME is LAST column (not first) → HSPICE puts time after all signal values
- G6: header names span multiple lines (5 per line, 15 chars each) → must concatenate before splitting

## Portability assessment
- Original deliverable depends on: /proj/m2701/V0_DDR4/ project files, HSPICE, Aether/Virtuoso, WaveView
- NOT directly portable (project-private files + EDA tools)
- Portable abstraction: pure Python .tr0 folded-ASCII parser (no EDA binary dependency)

## Case: EDA-Eval-DesignFlow-Tr0FoldedAsciiParse-001
- domain: spice_sim, L1 judge-run, LIVE-NA (judge_layers=[L0,L1])
- candidate: tr0_parse.py <input.tr0> <out_dir> → signals.csv + summary.json
- A/B token-structurally disjoint: A=7sig/30pts/15-page, B=9sig/40pts/20-page
- 15 assertions (a,sa static + c..p L1 judge-run on hidden B)
- 4 negatives first-fail distinct: empty→a, print_gold→sa, no_marker_skip→g, no_reorder→f
- trio {empty, print_gold, no_marker_skip} 3-distinct
