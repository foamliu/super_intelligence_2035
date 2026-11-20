# Deepread: bhcla — SPF Coupling Data → CSV Parser Skill (ray1lei)

- **session**: `1794190176104_bhcla.messages.json` (ray1lei@hfeg0pkn004 / 10.129.2.13)
- **mc**: 111 (scan keywords: pex:174, .def:99, waveview:18, aether:14, pyAether:12, lvs:7, analog:6, calibre:4)
- **size**: 2.75MB / 314 msgs / 25 real user turns / 98 assistant turns
- **found via**: r304 fresh-window scan (post-r292-scan, eda_flow recovered after r301-r303 outage); un-ledgered across all 4 shards
- **domain**: eda_other (PEX / parasitic extraction post-processing; SPF Standard Parasitic Format coupling data parsing)
- **track**: A-faithful produce-task ✓ (USER#1 proposes goal, asks clarifying Qs; does NOT give root cause/fix)
- **claim**: r304 claimed (mc=0 in ledger because post-scan; real mc=111)

## User intent (verbatim key turns)

- **USER#1** (the task proposal — A-faithful source): 「帮助我去处理一部分数据，转化为排版规律的csv文件或excel文件，这部分是通过SPF工具抽出来的signal之间的coupling数据，每个空白行后的第一行都是这个信号的总coupling,之后是该signal和其他signal之间的coupling,最后一行则是该信号和power之间的coupling…除了上述表述外，还有什么是你想在正式处理数据之前想了解的？」
- **USER#2** (format clarification + example): explains space-separated fields; gives concrete SPF block example:
  ```
  *|NET cn09bla<34> 0.000852709PF
  C209_1 cn09bla<34> cn09bla<24> 1.0195e-18
  C209_2 cn09bla<34> cn09blb<24> 3.32513e-18
  ...
  Cg209_6 cn09bla<34> 0 4.73601e-16
  ```
  → `*|NET <signal> <total_coupling>PF` (total, no coupling target); `C<n> <src> <tgt> <val>` (signal-signal); `Cg<n> <src> 0 <val>` (power coupling, target="0")
- **USER#4**: confirms CSV output (clipboard-copy constraint), asks for a SCRIPT: 「是你来处理这些数据更好还是你根据描述写个脚本给我然后我自己丢脚本更好呢？」
- **USER#5**: gives real file `/proj/drgqx/V0/ver/pex/ray1lei/msaq_E/1027/lpe/msaq/msaq_E.spf_CC`; requests SABL coupling summary CSV with explicit column layout: 行数计数 / CP数(XI_msax256_cp10; XI_msax196_pracL/R after CP07) / SA排序(XI_CXSA_1x4_0<39> → 39) / Sa_BLa / coupling-to-PreEq0 / coupling-to-bl(cn09bla<34>, sum multiples) / coupling-to-IO / -ION / -Cslin (sum) / ...
- **USER#7**: add columns for PCS0/NCS0/PCHa0/PCHb0/BLen0
- **USER#8-13**: process more SPF versions (1028, 1029_POR, 1030, 1102, 1105) same rules
- **USER#9/#14/#22**: delta analysis between versions (mean/max/std-dev, attribute changes; e.g. 1105 added power-fill around BL)
- **USER#10**: request separate BL CSV (BL-to-PreEq/IO/ION/YIO/saBl/csl/PCS/NCS/PCHa/PCHb/blen/power/total + same-group BLa-BLb coupling); **two CSVs: one SaBL, one BL**
- **USER#15-16**: BL layout规律 (24 BL/column, cn00-cn07 then ce00/cc00 then cn08-cn15; 7 mats with gap boundaries at specific columns); HB=hybrid bonding top metal
- **USER#23** (skill packaging request): 「你能将自己处理SPF数据的功能package成一个或多个可以复用的skill嘛…正确读取SPF文件，对信号coupling按要求进行sorting，输出规范的csv文件。注意目的和自检手段的规范性」
- **USER#24-25**: 「skill完成了嘛」/「请继续」

## Assistant deliverable (accepted, USER accepted by not objecting + skill packaging)

Final (A#98): **skill `spf-coupling-summary`** under `/home/ray1lei/.cline/skills/spf-coupling-summary/`:
```
SKILL.md                      # goal/boundary/acceptance/output-spec/8 real pitfalls
scripts/
├── sabl_summary.py           # ① SaBL 33-column summary
├── bl_summary.py             # ② BL 35-column summary
├── bl_delta_compare.py       # ③ BL two-version delta attribution
├── sabl_delta_compare.py     # ④ SaBL two-version delta attribution
└── selftest.sh               # ⑤ one-shot self-check
```
All 5 verified: SABL_IDENTICAL / BL_IDENTICAL / DELTA_ROWS_IDENTICAL / EXIT 0 / SELFTEST PASS.

## Core parsing logic (reverse-engineered from trace)

1. **Read SPF text**; skip non-data header lines (file-start noise per USER#2 "文件开头确实存在这些非数据行，请注意甄别并忽略")
2. **Parse `*|NET <signal> <total>PF`** → marks a new signal block; `<total>` is the signal's total coupling in PF (no coupling target field → identifiable as the total row)
3. **Parse `C<n> <src> <tgt> <val>`** → signal-to-signal coupling (scientific notation value, e.g. 1.0195e-18)
4. **Parse `Cg<n> <src> 0 <val>`** → power coupling (target field == "0")
5. **Blank line** separates signal blocks
6. **Classify coupling targets** by name pattern into categories (bl/IO/ION/Cslin/PreEq/PCS/NCS/PCHa/PCHb/BLen/power/saBl/YIO/...); **sum multiple couplings per category** (USER#5 "有多个请累加求和")
7. **Signal hierarchy parsing**: `XI_msax256_cp10.XI_CXSA_1x4_0<39>.Sa_BLb<0>` → CP=msax256_cp10, SA=CXSA_1x4_0 index 39, Sa_BLa/Sa_BLb index 0
8. **Output CSV** with specified column order; **two separate CSVs** (SaBL + BL)

## Case design (spec-driven-generator + static-verification, matches CkmuxXlsxExport-001/BankskewVecgenCfg-001)

- **deliverable**: `gen_spf_coupling_parser.py` (stdlib generator) + `spec_a.json`
- **check.py**: runs generator on hidden `spec_b.json` → emits `parse_spf_cc.py`; py_compile (no execution of imports); runs emitted parser on hidden SPF sample B → validates output CSV structure + values
- **A (spec_a)**: faithful — SPF format (*|NET/C/Cg), signal naming (XI_msax<N>_cp<M>.XI_CXSA_1x4_0<K>.Sa_BLa<J> / cn<N>bla<K>), SABL column set (行数/CP/SA排序/Sa_BLa/PreEq0/bl/IO/ION/Cslin/PCS/NCS/PCHa/PCHb/BLen/total), real PF/e-18 magnitudes
- **hidden B (spec_b)**: isomorphic — different SPF sample (different CP count, different SA indices, different signal prefixes, different coupling categories subset, different values); ensures generator is parameterized not hardcoded
- **conditions (≥8)**: a) zip+generator run emits parse_spf_cc.py b) py_compile PASS c) emitted parser defines parse_spf+summarize+sabl_columns fns d) parser correctly skips header non-data lines e) parser correctly parses *|NET total / C signal-signal / Cg power f) category classification + sum-by-category correct (recompute from B SPF) g) output CSV has spec_b column set in order h) row count == number of SABL signals in B i) values match recompute (within float tolerance) j) anti-hardcode-A (spec_a signal names absent in B output) k) cross-input-B present l) 3-seed determinism m) anti-trivial (empty/print stubs FAIL)

## Scarcity context

r304 = 7th scarcity confirmation (r295/r296/r299/r300/r302/r303/r304): ALL 31 digital-dominant (dig≥50, dig>ana, mc≥15) r292-scan candidates LEDGERED; .75-local digital un-ledgered pool mined (r303 delivered last clean produce 5fpod); fresh-window remote scan (pkn001-005 + .75, 11/08+) found 5 un-ledgered, only bhcla is clean produce (ouzip=DRC shardC resumed, nbcav/z1924=Windows PowerShell non-EDA dup, uxowi=layout shardC 11MB). bhcla found via eda_flow RECOVERY (was down r301-r303).

## DEBT

r304 = deepread + design complete; **DEBT:1 → r305 build case** (trace >2MB qualifies §3 exception; MUST build next round, no consecutive deepread-only).
