# Deepread: r248 yb57q SPF RC Aggregate Audit (zongjiuh@hfhds234)

## Trace metadata
- session: 1793756182967_yb57q
- user: zongjiuh (NEW user, first case)
- host: hfeg0pkn004 / 10.129.32.234 (hfhds234)
- mc: 14, kw: 10pyAether+3calibre
- agent: lead, 317 msgs, updated 2026-11-04
- domain: physical_verify (SPF/PEX RC analysis)

## User real intent (organic, 提出需求, no root cause given)
**U#1 (idx=0)**: "我这有一份SPF文件，路径是/proj/ddgoa/V0/workdir/zongjiuh/simulation/20261103_SPF_RC/YIO/m512Meg_U.spf.TYP_98_RCC，里面会记录一些net的RC值。文件中包含类似于'*|NET YioSelTop 0.000809724PF'这种语句，表示YioSelTop这根net的电容值是0.000809724PF. 我现在需要从spf文件中，Yio0Msaq00<15:0> ～Yio15Msaq00<15:0> 这共计256根net的电容值，并根据256根电容值的偏差情况，确定有无异常"

**U#2 (later)**: "现在需要额外统计多个section的Yio0Msaq00 表示 section0，Yio0Msaq28 表示section28，Yio0Msaq55表示section55，同一个bit，不同section本质上是同一根线，所以需要将Yio0Msaq00～Yio0Msaq55 按照bit位，将电容值累加后比较。现在SPF中确实不包含Yio8~Yio15Msaq，忽略它。并将数据和脚本以及脚本使用到/proj/ddgoa/V0/workdir/zongjiuh/simulation/20261103_SPF_RC/YIO 目录下"

**U#3**: "更新需求，在比较各bit电容时，需要的是按着各个Yio的比较结果，而不是所有yio在一起比较。"

**U#4**: "补充需求：现在除了要分析电容以外，还需要分析电阻。电阻在spf中是在，例如'*|NET YioTopN 0.000462661PF'后，下面会对应有'R13_1 YioTopN YioTopN:5 0.001'若干行，再往下是R13_2 * * ..."

## SPF format (from trace)
- `*|NET <netname> <cap_value>PF` — net total capacitance
- After each NET line: `R<id> <node1> <node2> <resistance>` rows (resistance elements)
- Net naming: `Yio<group>Msaq<section><<bit>>` where group∈{0..15}, section∈{00,28,55}, bit∈{0..15}
- 39GB file (too large to read directly, must use grep/streaming)

## Agent actions (key tool calls)
- run_approved_command: head/grep on SPF file to understand structure
- read_files: failed (39GB too large)
- Created Python script to parse SPF with grep + aggregate
- Generated per-Yio comparison data and anomaly detection
- Saved scripts and data to /proj/ddgoa/V0/workdir/zongjiuh/simulation/20261103_SPF_RC/YIO

## Why B-synthesized (not A-faithful)
- Original SPF file is 39GB (cannot include in assets)
- Net names and values are baked-in (A/B cannot differ on same file)
- Redefine as parameterized SPF RC parser: `spf_rc_audit.py <spf_file> <config.json> -o <output.json>`
- A = Yio*Msaq* pattern (8 groups × 2 sections × 8 bits = 128 nets)
- Hidden B = Dq*Sa* pattern (6 groups × 2 sections × 6 bits = 72 nets, different values/anomalies)
- B2 = 退化 (single section, no R rows)
- B3 = empty SPF (headers only)

## DISTINCT from existing physical_verify系
- r246 LefFromPinList (LEF generation), r245 RectAspectRuleCheck (DRC aspect ratio), r243 VssPunchRuleGen (DFM deck), r242 SaqpIntAngleEqSplit (SVRF ANGLE), r241 SvrfPvrsRuleTranslate (SVRF→PVRS), r240 WlAdjacentPairParse (.rep PAIR), r239 DrcRuleTimeRank (log timing), r237 DrcLogTeardownReport (log teardown)
- 本案**首次 ground on SPF/PEX parasitic RC 提取与聚合分析**（parse *|NET cap + R-rows, group by net pattern, aggregate across sections, anomaly detection）

## Case design (k=14 conditions a-n)
- spf_rc_audit.py (CLI, stdlib only): parse SPF, extract C+R, group by pattern, aggregate across sections per bit, detect anomalies (|cap-mean|>k*std), output JSON
- 14 条件: (a)zip+py (b)stdlib-only (c)B exit0+JSON (d)B nets_parsed count (e)B group structure (f)B aggregated_cap matches golden (g)B resistance parsing (h)B anomaly detection (i)B2退化 (j)B3 empty (k)cross-input A!=B (l)missing input→nonzero (m)3-seed determinism (n)A matches golden_A
