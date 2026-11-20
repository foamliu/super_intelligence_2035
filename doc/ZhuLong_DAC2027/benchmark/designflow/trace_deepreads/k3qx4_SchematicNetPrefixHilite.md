# trace_deepread — k3qx4 (SchematicNetPrefixHilite)

- session: `1784267301134_k3qx4`
- user/host: `e0014566 @ 10.129.35.82`
- match_count: 34 → domain `schematic_netlist`
- ledger status: claimed (r829) → case `EDA-Eval-DesignFlow-SchematicNetPrefixHilite-001`
- agent: lead (Cline v3.0.x), 38 messages, ~07-17 05:57 UTC
- outcome: **stalled mid-thinking** — the agent did 16 RAG API searches and produced a long
  thinking block planning the SKILL code, but **never emitted a final SKILL deliverable** as a
  text block. The session ended with msg[37] = assistant `thinking` only (15984 chars), no
  `text` block, no `run_code` tool_use with `lang=skill`. So there is no agent-produced
  artifact to mirror verbatim; the case is built from the **verbatim user intent** + the
  **API surface the agent actually explored**.

## Verbatim user turn (msg[0])

```
<user_input mode="act">在Schematic中,帮我高亮当前打开的设计图中所有名称以"net"开头的线
要求:建指定类型的探针标记颜色为红色,高亮必须在屏幕上可见
注意:你要使用skill代码实现和执行</user_input>
```

Single user turn. Mode = `act` (tool-action-deliverable). No follow-up turns.

## Agent API exploration (RAG_MCP_Server__search_apis / get_api_details, lang=skill)

The agent ran 16 RAG queries (msg 3-36). The API surface it converged on (visible in
msg[37] thinking + the search query strings):

| category | APIs the agent actually retrieved |
|---|---|
| net enumeration | `cv->nets`, `dbFindNetByName`, `dbStartGenNet`, `dbGetSigNameMemNets` |
| prefix / name match | (planned in thinking) `prefix("net" net->name)`, `setof` |
| highlight set | `geCreateHilightSet`, `geCreateWindowHilightSet`, `geGetCurrentHilightSet`, `geAddHilightFig`, `gePushHilightStack`, `geEnableHilightSet`, `geDeleteHilightSet` |
| net probe (the "指定类型的探针" part) | `geAddNetProbe`, `geAddNetProbeFromTo`, `geEnterAddNetProbe`, `geMakeProbeWithColor`, `geMakeProbeWithoutColor`, `geSetTCProbeDisplayStyle` |
| color / packet (the "红色" part) | `geCreatePacket`, `hiSetTextHighlightColor` |
| window / cellview | `hiGetCurrentWindow`, `geGetEditCellView`, `geGetWindowCellView` |
| redraw (visibility) | `hiRedraw`, `hiDrawHilightSet` |
| mark net (alt approach, rejected) | `leMarkNet`, `leHiMarkNet`, `leUnmarkNet`, `leSaveMarkNet` |

The agent's thinking (msg[37]) explicitly converged on this plan:

```
win = hiGetCurrentWindow()
cv = geGetEditCellView(win)
geCreatePacket(win "redHlPkt" "solid" "solid" "red" "red" 3 nil)
hlSet = geCreateWindowHilightSet(win "redHlPkt" t)   ; non-global so we can push
allNets = cv->nets
matchedNets = setof(net allNets prefix("net" net->name))
foreach(net matchedNets
    foreach(fig net->figs  geAddHilightFig(hlSet fig) )
)
gePushHilightStack(hlSet)
hiRedraw()
```

It wrestled with the global-vs-nonglobal highlight-set semantics and the
"must enable + push to be visible" detail (the visibility requirement in the
user prompt: "高亮必须在屏幕上可见"). It also considered the probe+color route
(`geAddNetProbe` / `geMakeProbeWithColor` with a red LPP) to satisfy the
"建指定类型的探针标记颜色为红色" clause, but never finalized.

## Case framing (5th reframe pattern: tool-action-deliverable → portable-stdlib reframe)

Same shape as r828 `SchematicMOSHilite-001`:

- **Original deliverable** (trace): a Virtuoso SKILL script the user can run in CIW to
  highlight nets whose name starts with "net" using a red probe, visible on screen.
- **Reframed deliverable** (bench): a Python tool `hilite_net_prefix.py` with two subcommands:
  - `--classify <fixture.json> [-o report.json]`: portable-stdlib classification of a
    schematic net list by name prefix (default "net"), emits JSON
    `{matched_count, matched_nets, non_matched_count, non_matched_nets, total, prefix, color, probe_type}`.
    Pure `json`/`argparse`/`str.startswith` — no EDA tool needed.
  - `--generate-skill [-o hilite_net.il]`: emits the Virtuoso SKILL script (the agent's
    converged plan) that uses `hiGetCurrentWindow` / `geGetEditCellView` / `geCreatePacket`
    (red) / `geCreateWindowHilightSet` / `geAddHilightFig` / `geAddNetProbe` (red LPP) /
    `gePushHilightStack` / `hiRedraw`, with graceful no-window handling.
- **Why this reframe**: the SUT sandbox has no Virtuoso, so the SKILL cannot be executed to
  verify on-screen visibility. The reframe splits the verifiable part (deterministic name-prefix
  classification, checkable on a hidden fixture B) from the un-verifiable part (actual on-screen
  highlight), which becomes a structurally-graded SKILL artifact.

## Asset fidelity

- A = `schematic_fixture_A.json`: trace-faithful fixture — a schematic net list with names
  some of which start with "net" and some don't (vdd/vss/a0/b0 don't). The "starts with net"
  criterion comes straight from the verbatim user prompt.
- B = `schematic_fixture_B.json` (hidden): synthesized net list with **zero name overlap**
  with A, different cellview/window, different prefix-hit ratio (A: 5/9, B: 6/10) so a
  hardcoded A answer fails on B.
- Both fixtures are JSON net lists (no real cellview object), so the classifier runs anywhere.

## Test contract (check.py, 14 assertions a-n, k_rationale == k_check == 14)

The grader runs the candidate's `--classify` on the **hidden B** via subprocess and asserts:

a. submit.zip is a valid zip and contains ≥1 `.py` tool
b. the tool passes `ast.parse` (valid Python)
c. `--classify <B> -o report.json` exits 0 and writes a non-empty JSON report
d. `report.matched_count == 6`  (B ground truth)
e. `report.matched_nets` set == `{net_x, net_y, net_clk, net_fb, net_out, net_pgd}`
f. `report.non_matched_nets` set == `{avdd, agnd, ibias, vref}`
g. `report.total == 10`
h. `--generate-skill -o hilite_net.il` exits 0 and produces non-empty SKILL text
i. SKILL defines a net-prefix classifier procedure (`hiIsNetPrefix` / `*NetPrefix*`) and
   uses a prefix-match primitive (`prefix(` or `strncmp` or `strncmppcre`)
j. SKILL references a Virtuoso highlight API
   (`geAddHilightFig` / `geCreateWindowHilightSet` / `geCreateHilightSet` / `geAddHilightObject`)
k. SKILL references current-window / edit-cellview access
   (`hiGetCurrentWindow` / `geGetEditCellView` / `geGetWindowCellView`)
l. SKILL iterates nets (`cv~>nets` / `geGetSelSet` / `net~>name`)
m. SKILL handles the no-window case gracefully (`unless( win` / `when( win` / `return( 0 )` /
   explicit "no current window" message)
n. anti-hardcode: no A or B net name appears as a quoted string literal in the tool source
   (the tool must classify from the fixture, not by name)

§4.9 degradations (must all FAIL):
- empty zip → a FAIL
- print-only (fixed report to stdout, no `-o` file) → c FAIL
- copy-A (hardcode A's matched set) → d/e FAIL + n FAIL (A names hardcoded)

## Anti-hardcode name set (union of A & B net names, 19 names)

A: `net0, net1, netclk, netout, netbias, vdd, vss, a0, b0` (9)
B: `net_x, net_y, net_clk, avdd, agnd, net_fb, net_out, ibias, vref, net_pgd` (10)

Note: the prefix literal `"net"` is intentionally NOT in this set — the tool MUST contain
`"net"` as the prefix, and the anti-hardcode regex matches full quoted tokens, so `"net"`
does not collide with `"net0"` etc.

## Negatives

- `neg_hardcode_a.py` — returns A's matched set regardless of fixture; FAILs d/e + n.
- `neg_name_substr.py` — classifies by `"net" in name` (substring, not prefix); matches
  `ibias`? no — substring "net" is not in "ibias". Actually a substring classifier would
  match `net*` AND would also match e.g. a net named "kenneth" — but on B, `ibias`/`avdd`/
  `agnd`/`vref` don't contain "net", so substring coincidentally gives the same B answer.
  To make this negative actually FAIL on B, it instead classifies by `name.startswith("net")
  == False` inverted, or by a wrong prefix `"ne"`. Simplest: classify by prefix `"netx"`
  (wrong prefix) → 0 matched on B → d/e FAIL. Or: classify by `name.endswith("net")`
  (suffix, not prefix) → 0 matched on B → d/e FAIL. I'll use the suffix variant — it's the
  most semantically-tempting wrong criterion and clearly FAILs on B.
- `neg_print_only.py` — prints a fixed B-shaped report to stdout, never writes the `-o` file;
  FAILs c.

## Self-verify plan

- ref `hilite_net_prefix.py` packaged as submit.zip → 14/14 PASS
- each negative packaged → FAIL (different assertion per negative)
- §4.9: empty zip → a FAIL; print-only = neg_print_only → c FAIL; copy-A = neg_hardcode_a → d/e/n FAIL
- k_rationale == k_check == 14 ≥ 8 ✓
