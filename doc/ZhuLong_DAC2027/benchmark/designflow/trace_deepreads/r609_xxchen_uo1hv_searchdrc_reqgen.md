# Deepread: r609 xxchen uo1hv — searchDRC requirements doc generation

## Trace
- session: 1792026663236_uo1hv
- user: xxchen @ hfeg0pkn001 (10.129.x)
- match_count: 106
- domain: physical_verify (DRC tool development)
- msgs: 63, user_input: 3
- agent: lead

## User intent (verbatim)
UI#1: "我需要找团队开发一个用于检索DRC的工具，主要功能我之前有开发一个初版的searchDRC.html 帮我把开发要求梳理出来。另外其他需求我需要和你再讨论下，我希望解决哪些问题：1）输入数据和程序数据分离，开发在外部进行，导入内部后需要替换成内部的数据。2）网站需要有统计使用记录的功能，访问用户，检查次数等。3）LDR并不规则，存在很多相似的rule。4）自动化的正则匹配，通过提前准备好的配置文件，自动识别LDR中的可替换信息，替换成正则表达式。5）另外一种检索方式，只有少量关键词用于 相似LDR表述的检索。"

UI#2: "请再给一份简单明了的功能需求描述。"
UI#3: "能不能用中午来写，英文看不习惯。"

## Agent behavior
- read_files searchDRC.html (716 lines) → analyzed v0.1 baseline
- Identified 7 defects (G1-G7): hardcoded mock data, upload button shell, no search, Chinese garbled, monolithic file, non-functional load button, no statistics
- editor: wrote searchDRC_requirements_v0.2.md (408 lines, 9 chapters): Background, v0.1 baseline analysis, Architecture (data adapter/search engine/statistics layers), FR-0~FR-5 with acceptance criteria, Data interface specs (ldr.json/deck_index.json/regex_config.json/statistics log), Non-functional (intranet/20000 rules/<200ms), Milestones M1-M5 (~6-8 weeks), Open questions Q1-Q8, Risk list
- Produced brief 74-line version (7 functions F1-F7) in Chinese per UI#2/UI#3
- User accepted both deliverables

## Revival rationale
- r323 OLD reject: "requirements-doc task, weak check, deferred"
- 2026-11-15 user令: requirements-doc/analysis 现合法 (B类被误杀该复活)
- xxchen is C-domain known produce-task user (r545 PgRailLabelReplace/r587 AutoViaEncFix/r594 DeckRuleParseExtract/r606 WaiveParamMultiParse/r608 EncloseSide1PatternGen)
- This is a legitimate produce-task: user wants structured requirements doc for DRC search tool

## Case design (B档 mock-behavioral reframe)
- Source: searchDRC.html + produced docs in xxchen private workspace (sandbox unreachable) → asset_fidelity=synth
- Parameterize: `drc_search_req_gen.py <baseline.json> <out_md>` — parse baseline JSON (v0.1 features + defects G1-G7 + 5 requirements with key_points + acceptance_criteria + architecture + non_functional + milestones) → generate 9-chapter structured Markdown requirements spec
- Input A: baseline_A.json (5 FRs: Data and Program Separation / Usage Statistics / Similar Rule Grouping / Config-Driven Regex Generation / Keyword Similar Search)
- Hidden B: baseline_B.json (5 FRs with DIFFERENT titles: Data Program Isolation / Activity Tracking / Rule Family Clustering / Template-Based Pattern Synthesis / Fuzzy Keyword Retrieval)
- Hidden B2: baseline_B2.json (5 FRs with yet DIFFERENT titles: Data Code Decoupling / Usage Analytics / Near-Duplicate Rule Merging / Configurable Pattern Builder / Semantic Keyword Lookup) — anti-hardcoding

## 14 conditions a-n
a: zip contains script + py_compile
b: B run exit 0 + non-empty md
c: >= 9 ## section headers
d: covers ALL B requirement titles
e: >= 5 Acceptance Criteria sections
f: all B defect IDs G1-G7 present
g: Architecture section present
h: Data Interface section present
i: Non-Functional section present
j: all B milestone IDs M1-M5 present
k: anti-hardcoding A (A titles NOT in B output)
l: anti-hardcoding B (B2 titles present, B titles absent in B2 output)
m: determinism (two B runs byte-identical)
n: robustness (empty milestones/defects → exit 0)

## Self-test
- ref 14/14 PASS ✓
- 3 negatives (empty/print_only/deleted_core) ALL FAIL ✓
- NEGATIVE_SELFTEST ALL-FAIL-OK ✓
