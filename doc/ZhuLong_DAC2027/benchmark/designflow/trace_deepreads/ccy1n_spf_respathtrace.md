# Deep-read: 1793435397635_ccy1n (xxchen @ hfeg0plg53, mc=40)

**Session**: `1793435397635_ccy1n.messages.json` — xxchen @ hfeg0plg53
**Domain**: analog_context (SPF/DSPF resistance extraction)
**Keywords**: analog:129; netlist:37; lvs:15; cmos:4; transistor:2; mosfet:1
**mc**: 40

## Tool
`/home/xxchen/workspace/small_tool/traceSPFresNode/traceSPFresNode.py` (40732 B, 1057 lines)
- From a StarRC DSPF file, extract the resistor network around one target node → `traceNetRes.rep`.
- CLI: `python3 traceSPFresNode.py <spf> <target> [-o rep] [--mode path|full] --selftest`
- **phase1**: streaming scan to locate the `*|NET` section containing the target node (divider/delimiter normalization, exact-then-suffix match, byte-offset recorded, early exit).
- **phase2**: parse only that net section → ports (`*|P`), pins (`*|I`), resistors (`R` lines), build adjacency graph.
- **path mode (default)**: Dijkstra from target → net-head node (the `*|NET` name), weight = resistance, tie-break = fewer hops; dangling wire ends (degree-1 non-pin/non-port) on path nodes excluded & annotated. Falls back to nearest port/pin if net-head unreachable.
- **full mode**: BFS whole connected component.
- Handles `*|LAYER_MAP` ($lvl= annotation), `*|DIVIDER`/`*|DELIMITER` normalization (.  ≡ /, pin `:`), 50 GB streaming (chunked, never loads whole file).
- Built-in `--selftest` (12 checks: normalization, dangling rule, path replication of Channel_clips.spf vdd2dq! net, stub on path, layer-map entry parsing).

## Test data (on host)
- `Channel_clips.spf` (3142 B) — small fixture, net `vdd2dq!` with 7 resistors (R1_1..R1_7), M1:SRC target.
- `test_divider.spf`, `test_sd_short.spf`, `test_true_short.spf` — additional fixtures.
- Expected path-mode output for `M1:SRC` on Channel_clips.spf:
  ```
  R1_4  M1:SRC   vdd2dq!:7  265.683
  R1_2  vdd2dq!  vdd2dq!:7  0.001
  ```
  (path M1:SRC → vdd2dq!:7 → vdd2dq!, total 265.684, 0 stubs)

## User intent (compaction summary = continuation)
First message is a context-compaction summary (session is a continuation of a
multi-turn v2 refactor).  The produce is the `traceSPFresNode.py` tool itself.
v2 change: default `--mode path` (Dijkstra target→net-head) instead of v1 full
BFS.  6 editor patches applied (4+2, all succeeded).

## B-grade synthesized abstraction
Real tool streams 50 GB files with byte-offset seek — not reproducible in a
sandbox.  Abstraction: a self-contained single-file CLI `spf_res_trace.py`
that parses a small StarRC DSPF/SPF file (in-memory), locates the target net,
builds the resistor graph, and reports the minimum-resistance path (Dijkstra,
tie-break fewer hops) from target to net-head, with dangling-stub exclusion.
Mechanism preserved: `*|NET`/`*|P`/`*|I`/`R` parsing, divider/delimiter
normalization, Dijkstra min-resistance + hop tiebreak, degree-1 dangling
detection on path nodes.

## A/B fixtures (disjoint, anti-hardcode)
- **A (visible)**: `net_A.spf` — design `SenseAmp_A`, net `vcc_ring!`, target
  `M3:DRN`.  Two competing paths (8.003 via Ra1+Ra2+Ra3 vs 8.001 via
  Ra4+Ra5+Ra3); Dijkstra picks 8.001.  Stub `vcc_ring!:9` (via Ra7) on path
  node `vcc_ring!:4`.  Plus 2 distractor nets (sa_bl, 22).
- **B (hidden)**: `net_B.spf` — design `DQPad_B`, net `vss_arm!`, target
  `MP5:GATE`.  Two paths with EQUAL total 13.001 (3-hop Rb1+Rb2+Rb3 vs 2-hop
  Rb4+Rb5); tie-break fewer hops → 2-hop.  Stub `vss_arm!:12` (via Rb8) on
  path node `vss_arm!:9`.  Plus 2 distractor nets (vdd_io!, 17).
- A/B net names, node names, resistor names, designs all completely disjoint.
- A tests min-resistance selection; B tests hop tiebreak — complementary.

## check.py (14 conditions a-n)
Independent oracle = DFS all-simple-paths + min-resistance (structurally
different from reference Dijkstra).  Subprocess-runs SUT on hidden B.
a: zip+no-forbidden-imports/exec/ref/path  b: py_compile  c: B runs exit0 nonempty
d: required header fields  e: matched_net==vss_arm!  f: terminal+kind+status
g: path_resistors count  h: path resistor name set  i: path_total (1e-6)
j: path nodes order  k: stubs set+via  l: no A/B-only literals (anti-hardcode)
m: cross-input A structural match  n: 3-seed md5 determinism
§4.9 three-fake (empty/wrong-name/non-zip) → REJECTED at top.
