# Deepread: 4koby (xrxiong@10.129.2.10 mc85) — pyRHR doc-retrieval + skill-install

**Session**: 1794395067104_4koby.messages.json (501167 B, 91 msgs / 61 user) @ 10.129.2.10
**Date**: 2026-11-19 r905 triage (fresh untouched mc≥10 D-pure candidate)
**Verdict**: ❌ NOT造-able as quality D-domain case — meta/setup task, high kw from skill-file reads not real EDA produce

## Trace flow
- **U1**: "pyRHR" — user asks about pyRHR (a pyAether-related library/tool)
- **U3-U46**: agent does cimi-kb-search / ask-eda / read skill files (eda_agent/00_INDEX.md, aether-tool-qa/SKILL.md, part_XII_Python_Script.md, case_001_move_origin_clear_highlights.md) to find pyRHR docs; many RAGFlow failures ("API Key 未配置"); AskEDA (U46) returns pyRHR info
- **U48**: "安装这个pyrhr-copilot skill" — user asks to INSTALL a pyrhr-copilot skill
- **U49-U61**: agent reads skill-creator/SKILL.md, lists .cline/skills/, reads cline_mcp_settings.json, various skill SKILL.md files (qualib-qa, grill-me) — installing/configuring a skill

## Domain judgment
- Keywords: pyaether:294 / aether:189 / waveview:79 / virtuoso:29 / schematic:22 / netlist:1
- High kw comes from agent **reading skill files and docs** (eda_agent skills, aether-tool-qa references, pyAether Python Script chapter) to answer "what is pyRHR" — NOT from real EDA produce work (no netlist generated, no schematic edited, no waveform analyzed)
- Real task = doc-retrieval ("what is pyRHR") + skill-install ("install pyrhr-copilot skill") = meta/setup/config task
- Per 2026-11-15 reaudit, setup类 IS造-able, BUT design_flow fit weak (measures cline-skill-install / doc-retrieval, not EDA推理/produce of netlist-schematic-waveform-analog artifact)

## Why not造-able (this round)
1. **No EDA produce artifact**: user never opened a design / ran pyAether on a real cell / produced netlist-schematic-waveform; deliverable would be a cline-skill file (config), not an EDA artifact
2. **Cross-shard**: already parked by shard C (2026-11-15) — cross-shard mutex, D cannot claim
3. **Weak check() teeth**: a "install skill" task's check() would verify skill-file format/structure — falsifiable but not EDA-substance (L1 text/config, not L2+ EDA)
4. **Budget**: not worth synthesizing given weak design_flow fit + cross-shard

## Disposition
- NOT added to D ledger (cross-shard mutex: C already parked 2026-11-15)
- Triage documented here; fresh D-pure filter (pyaether+aether+waveview kw) produces false positives when kw comes from agent skill-file reads — same分型 as r896 el8uc (meta/explore chat) and r904 w4ghz (kw from log content)
- Lesson: D-pure keyword filter needs a "kw-from-agent-tool-reads" negative signal (high kw but user turns are short doc/config requests with no design/cell/netlist/sim references)
