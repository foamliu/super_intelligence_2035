# r259 deepread — 1792733394521_26h7a (xxchen @ hfeg0pkn002, mc=262, physical_verify)

## trace facts
- session: drcConnect small tool, dir `/home/xxchen/workspace/small_tool/drcConnect/0.2/`
- user intent (A-faithful): U#3 idx=55 "我在project/V2下面放了一份新的expand后的文档：calibreDRC3d_expand.rule 用工具把这份文档的连接图绘制出来。"
- followups U#4/5/6: layer order top→bottom per stated stack; one band per layer (no shared bands); no bus notation (each via drawn individually); branches get extra layer box; band box order TMAarr2→M1Aarr2→M2Aarr2.

## tool chain (assistant)
- `tasks/build_graphV2.py` — builds connectivity graph from calibre DRC rule deck.
  - CONN edge tuple format `(kind, upper, lower, "by-label", [rule_lines])`, kind ∈ {via, direct, soft}.
  - layers parsed top→bottom; one band per layer.
- `tasks/drawConnect/query.py` — `shield_pairs()`:
  - `CTUnet = ((CT NOT TCP_ARRAY) ...)` → CT shields M0U (label shieldCT).
  - `ND_SD = NDIFF NOT (PG ...)` → PG shields AT4/NDnet (label shieldPC).
- renderer: SVG banded HTML — one horizontal band per layer top→bottom; via lines between bands;
  shield = dashed arrow + red arrowhead + label (shieldCT/shieldPC).
- `verify_graphV2.py` — counts bands / boxes / conns / statements.

## B-synthesized redefinition (r259)
- real deck `calibreDRC3d_expand.rule` + tool source inaccessible on .75 to e0031982 → redefined as offline
  connectivity-graph HTML renderer fed a synthetic rule-deck JSON dump.
- distinct from r258 ConnChkSummaryGen (text path/shield report per run): this case renders an
  **HTML/SVG banded cross-section** (one band per layer top→bottom, via lines, dashed shield arrows).
- contract: `drc_connect_graph.py <rule_deck.json> -o <out.html>` (stdlib only).
- input schema: {design, generated, layers[{name,alias}] top→bottom, edges[{kind:via|direct|soft,
  via?, upper, lower}], shields[{via, target, label}]}.
- hidden B/B2 differ from A in layer stack + edge set + shields (branching, spanning edges).

## encoded user-feedback constraints in check.py
- one band per layer (no shared/duplicate bands) → cond i.
- top→bottom band order matches layers list → cond h.
- band y-positions strictly increasing top→bottom → cond n.
- each via/direct/soft edge drawn individually (no bus grouping) → cond j/k/l (per-edge count+attrs).
- shield dashed arrows with labels shieldCT/shieldPC-style → cond m.
