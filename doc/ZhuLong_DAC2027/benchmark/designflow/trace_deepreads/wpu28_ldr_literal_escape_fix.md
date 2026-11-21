# Deepread: wpu28 (xxchen @ hfeg0plg19, mc=197, physical_verify)

## Trace source
- user: xxchen, host: hfeg0plg19, session_file: 1795136352856_wpu28.messages.json, match_count: 197
- keywords dominant: drc:970; .gds:71; .spi:61; calibre:6; techfile:4; pdk:4; gdsii:3; .def:3; lvs:1
- session: 156 msgs, 81 tool_calls, 1 typed user input (continuation round 4)

## Real task (intent)
xxchen maintains a **DRC pattern tool** (`/home/xxchen/workspace/DRC_pattern_tool/0.6/device_rule1/`), a Python+PyQt5 tool that converts LDR (Layout Design Rule) descriptions into regexes for auto-filling DRC device rule config. Round 4 of iterative autofill optimization.

The user's round-4 ask (#3): "正则输出字面部分原样不动（不转义 `(` `)`）" — the converted regex's literal parts should keep their literal text, specifically don't escape `(` `)`.

## Evolution (the key insight)
- **Initial (buggy) implementation**: assistant implemented `_literal_token` as `re.escape(tok).replace(r"\(", "(").replace(r"\)", ")")` — escape but then UN-escape parens, per the user's literal ask.
- **Realization & REVERSAL (gold fix)**: the assistant realized keeping `(` `)` unescaped is WRONG — an unescaped `(` opens a capture group, so the regex never matches the literal parenthesis in descriptions like `Area(um²)`, `(80%)`, `2*(W+L)`. The user's "字面部分原样不动" actually means "literal text stays as a literal fragment (NOT turned into a wildcard/capture)", NOT "regex syntax characters stay unescaped".
- **Gold fix (msg 70 NEW)**: `_literal_token` = `return re.escape(tok)` — fully escape all literal tokens so they match verbatim.

## Key files (real workspace, READ-ONLY)
- `drcpv/golden/matcher.py` (585 lines) — the matching engine
  - `_literal_token(tok)`: GOLD = `re.escape(tok)`; BUG = `re.escape(tok).replace(r"\(",...).replace(r"\)",...)`
  - `ldr_to_regex_captures(ldr_text, layer_dict, ...)`: round-4 new fn — builds regex with named capture groups (L<n>/V<n>/P<n>) for layer/value/param slots, KEEPS core:/peri: lines, uses `_literal_token` for literal tokens + number-unit `rest`.
  - `ldr_to_regex_full`: older fn, wildcards layers, drops core/peri, uses `re.escape` directly.
  - `_split_token_number`, `_NUMTOK_RE`, `_is_layer_component`, `strip_core_peri`, `match_captures`, `match_regex`
- `drcpv/ui/autofill_dialog.py` — PyQt5 autofill dialog (caller)
- `drcpv/model/schema.py`, `ldrdeckmap...` — model

## B-tier reframe (A infeasible: live workspace READ-ONLY + remote host)
Reframe to: **fix-the-bug fixture** — given a self-contained `matcher.py` with the BUGGY `_literal_token` (un-escapes parens) + a spec describing round-4 req, deliver a fixed `matcher.py` where `_literal_token` fully escapes literal tokens, + a `report.json` evidencing the fix on test LDR samples.

- env_A (visible): matcher.py (buggy) + spec.json + ldr_samples_A.json + layer_map_A.txt
  - A metachar tokens: `Area(um²)`, `(80%)`, `2*(W+L)`; A layers: M0C, AA, NBT
- env_B (hidden, anti-hardcode): ldr_samples_B.json + layer_map_B.txt
  - B metachar tokens: `Peri(W²)`, `[Stop]`, `3*(W+2L)`, `{Net}` (different bracket types + content)
  - B layers: POD, ENC, GATE, VIA (different from A)
- ref solve.py: applies gold fix (`_literal_token` → `re.escape`), writes fixed matcher.py + report.json
- check.py: imports candidate matcher, runs ldr_to_regex_captures on B samples, ≥8 teeth

## Domain
physical_verify (DRC pattern tool, drc dominant). Distinct from r909 CalibreDrcRunsetConfigValidator (runset config) and r902 SkillRcPatternDiffAnalyze (SKILL RC pattern diff) — this is a Python regex-literal-escaping bug fix in a DRC tool's matcher engine.
