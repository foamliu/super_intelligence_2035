# Deepread: r240 — ziyuny zdwid — SVRF→PVRS rule-deck translation

## Trace
- session: `1793017242561_zdwid` (ziyuny@hfeg0pkn005/10.129.2.14, mc=141)
- keywords (semantic): lvs:2964 drc:1191 netlist:335 calibre:168 schematic:103 gdsii:47 pex:26 analog:17
- tools: pyAether:237 schematic:122 netlist:99 calibre:18 virtuoso:5 (tools col); read_files:44 editor:26 list_allowed_files:12 run_commands:1 SandBox run_code:1 skills:1
- 157 msgs (91 user / 66 assistant), agent=lead, model=deepseek-v4-flash, status=completed (exit 0)
- cwd: /home/ziyuny/ggSkill; session.json title: "svrf2pvrs你能读到这个工具吗"
- NEW-ish user (ziyuny 7 prior shard-C ledger entries — not saturated)
- source tool: Empyrean Argus `svrf2pvrs` (Calibre SVRF/TVF → Argus PVRS/TRS converter)
  at `/apps/empyrean/argus/pvconvertor/lnx26_x86.64_20250211/pvconvertor/src/rcsSynPvrsConvertor.cpp`

## User real intent (5-turn, capability Q → reference-doc extraction → specific translation + bug)
- U0: "svrf2pvrs 你能读到这个工具吗" (can you read this tool?)
- U1: "这个工具是 svrf→pvrs 转换器，你能通过工具知道它的转换原理吗？" (figure out the conversion logic)
- U2: "把所有字段转换规则整理给我，放在 /home/ziyuny/pvConventor" (organize ALL field conversion rules → pvConventor/)
- U3: "svrf 中 edge_select = ENC M2_ICOVLV1M2 ICOVLDMY REGION == 0.465 对应到 pvrs 应该是什么？" (specific translation)
- U4: "编译报错 ... edge_select = extension ( M2_ICOVLV1M2 ICOVLDMY == 0.465 region )" (debug the converted output's compile error)

## Assistant journey (157 steps)
- Explored `/apps/empyrean/argus/pvconvertor/.../src/` (read_files 44): found `rcsSynPvrsConvertor.cpp` (15300+ lines).
- Reverse-engineered the conversion mechanism:
  1. **词法级映射**: giant switch at `:2050-2453` (`replaceKeywordsInComment`) maps each SVRF KEY_TYPE → PVRS text.
  2. **语法级重写** (`convCheckSpaceCmd` `:15351-16314`): layer-op assignments emit PVRS `cmd ( ... )`:
     - ENC/ENCLOSURE → `extension (`, INTERNAL → `width (`, EXTERNAL → `space (`
     - REGION → `region` (emitted in pass 2, `:16099-16102`)
  3. **词形归一**: YES/ENABLE→yes, NO/DISABLE→no, SAME ORDER→in_order, etc.
  4. 873 PVRS reserved words; prefix detection (`DRC_`/`ERC_`/`LAYOUT_`/`GEOM_`/`LVS_`/`DFM_`/`FPD_`).
- Produced 9-doc reference at `/home/ziyuny/pvConventor/` (editor 26 writes):
  README, 01_几何与层操作映射, 02_DRC_ERC映射, 03_LVS与SPICE映射, 04_布局与原理图IO映射, 05_杂项, 06_规格语句结构转换, 07_结构重写, 08_SVRF关键词枚举, 09_PVRS保留字表.
- For U3/U4: traced `convCheckSpaceCmd` to confirm ENC→`extension (` (NOT the word-level `enc`), REGION→`region` reorder. Investigated the compile error (parameter order/syntax). Status completed.

## Real conversion rules extracted (trace-grounded, with source line numbers)
Word-level (`rcsSynPvrsConvertor.cpp:2050-2453`):
- AND→GEOM_AND, OR→GEOM_OR, NOT→NOT, XOR→XOR, CUT→GEOM_CUT, SIZE→GEOM_SIZE, ENCLOSURE→enc, INTERACT→geom_interact, INSIDE→GEOM_INSIDE, OUTSIDE→GEOM_OUTSIDE, MERGE→geom_merge, MAGNIFY→geom_magnify
- DRC RESULTS DATABASE→drc_result db, DRC SUMMARY REPORT→drc_summary, DRC MAXIMUM RESULTS→drc_max_result, DRC KEEP EMPTY→drc_output_empty, DRC TOLERANCE FACTOR→drc_tolerance distance, DRC CHECK MAP→drc_rule_map
- LVS REPORT→lvs_report db, LVS ISOLATE SHORTS→erc_find_short, LVS ISOLATE OPENS→erc_find_open, LVS REDUCE PARALLEL MOS→device_merge parallel_mos, LVS REDUCE SERIES CAPACITORS→device_merge series_cap, LVS POWER NAME→lvs_power, LVS GROUND NAME→lvs_ground
Operation-level (`convCheckSpaceCmd :15351-16314`):
- ENC/ENCLOSURE→`extension (`, INTERNAL→`width (`, EXTERNAL→`space (`; REGION→`region`
Real A statement: `edge_select = ENC M2_ICOVLV1M2 ICOVLDMY REGION == 0.465` → `edge_select = extension ( M2_ICOVLV1M2 ICOVLDMY == 0.465 region )`

## Case synthesized: EDA-Eval-DesignFlow-SvrfPvrsRuleTranslate-001
- SUT: `svrf2pvrs_translate.py` (stdlib only), argv[1]=SVRF file → PVRS stdout, 1:1 per line.
- A (visible, trace-grounded): real edge_select ENC statement + DRC/LVS/boolean keywords.
- B (hidden, anti-hardcode): DISJOINT keywords/ops — INTERNAL/EXTERNAL (→width/space), OR/CUT/INTERACT/OUTSIDE/MERGE, DRC TOLERANCE FACTOR/DRC CHECK MAP, LVS ISOLATE OPENS/SERIES CAP/PARALLEL CAP; NO→no normalization.
- B2 (degraded): 2 unknown-keyword lines (UNKNOWN_DRC_CMD, BOGUS_LVS_OP) passed through unchanged.
- B3: empty file → exit 0, empty stdout.
- 16 conditions (a-p), each independently FAIL-able; 5 negatives all FAIL; §4.9 three-fakes all FAIL.
- Anti-hardcode: A uses ENC→extension (A-only); B uses INTERNAL→width + EXTERNAL→space (B-only); disjoint → SUT must implement all 3 ops.

## DISTINCT from prior shard-C SVRF cases
- SvrfFragMerge / SvrfHandbookPaginate / SvrfRuleExplain / SVRFDepAudit / SVRFDeckCatalog: those are SVRF deck *management* (fragment merge, handbook pagination, rule explanation, dependency audit, deck catalog).
- This case: SVRF→PVRS *keyword/operation translation* (language conversion with ENC→extension/INTERNAL→width/EXTERNAL→space + REGION→region reorder + word-form normalization). Genuinely complementary — no overlap in SUT deliverable (a translator script vs deck-merge/paginate/explain/audit/catalog tools).
