# §4.9 Anti-Hardcode 普查报告（全 Bench 抽样首版）

> 生成时间：2026-11-21 17:4x · 执行方：shard D · 依据：2026-11-21 17:0x 用户令「全 bench §4.9 anti-hardcode 普查放行，让 D 执行」
> 数据文件：`designflow/anti_hardcode_audit_all.tsv`（635 行）
> 普查脚本：`designflow/_audit_antihardcode_static.py`（静态筛查）+ `designflow/_gen_audit_tsv.py`（统一 TSV 生成）
> 题库根：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow`（脚本默认 --bench-root 指向此处）

## 0. TL;DR（先看结论）

- **普查范围**：D 全量 560 条 + A/B/C 各抽样 25 条（优先抽 k<12 老题），合计 **635 条**。
- **判定**：**PASS 43 · GAP 569 · WEAK 4 · MISSING 16 · 其它 3**。**GAP 率 ≈ 90%**。
- **核心病灶**：绝大多数 `check.py` **只跑 hidden B、无 A-gold 交叉校验**（无嵌入 A fixture、不在 A 上跑候选）。审计方构造一个"忽略输入、直接吐出 B 的 gold 输出"的假提交（`fake_print_only`），即可 PASS 全部断言——违反 §4.9 (b)(c)。
- **运行时已确认 GAP（2 条，可复现）**：
  - D `EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001`（k=9，纯报告 grep，无 subprocess）
  - D `EDA-Eval-DesignFlow-AddrRtlGateMap-001`（k=12，Produce 跑 B 但无 A-gold 交叉）—— **已于 r1059（2026-11-21）修复**：k=12→21（12 B-side + 9 A-gold 交叉 m-u），A fixture 落 `reference/hidden_a/`（避免 base64 编辑腐蚀），check 在 A 上 subprocess 跑候选并断言 A-gold，3 假（print_only/core_deleted/empty）全 FAIL，5 neg selftest 全 FAIL。
  - D `EDA-Eval-DesignFlow-AutoCellRmAvPf-001`（k=12，Produce 跑 B 但无 A-gold 交叉）—— **已于 r1060（2026-11-21）修复**：k=12→21（12 B-side + 9 A-gold 交叉 m-u）。A fixture 直接读 `assets/spec.json`+`instance_manifest.json`（judge 可访问，无需 base64/无编辑腐蚀），check 在 A 上 subprocess 跑候选并断言 A-gold（deleted=8 av=3/pf=5，≠ B 的 11）。新增 `neg_fake_hardcode_b.py`（smart §4.9(b) B 硬编码 stub：B 上过 b-l，A 上 dbDelete 不触发→deleted 空→FAIL [o]）为运行时证明；6 neg（5 旧+1 新）全 FAIL，6 distinct labels，ref 21/21 PASS。
  - D `EDA-Eval-DesignFlow-AvcPatternCompare-001`（k=11，visible-A-vs-B + visible-A-vs-A，可见 A 可被 stub 读取特判）—— **已于 r1061（2026-11-21）修复**：k=11→15（a-o）。新增隐藏 A' `pattern_A2.avc`（24 records/8 unique/X@pos1/pos6，SUT 不可见）；check 用判分器独立 `_gt_recount`/`_gt_parse`/`_gt_diff` 重算 A'-gold（A2-vs-A2 shared=8/only=0/bdiff=[]/rc=24/up=8；A2-vs-B shared=1/only_a=7/only_b=11/bdiff=[1,2,4,6]/rc_a=24/rc_b=60），候选须在 A' 上真解析才能匹配。smart §4.9(b) stub（读 visible-A 检测 a==b 硬编码 A-gold+B-gold）pre-fix PASS→post-fix FAIL[m]；6 neg 全 FAIL n_distinct=5，ref 15/15 PASS。此例的病灶是新发现：**visible-A-vs-A 交叉校验无效**（A 在 SUT 沙箱内，stub 可读它特判 a==b），必须用 SUT 不可见的隐藏 A' 才能真正击穿 B-hardcoded stub。
  - D `EDA-Eval-DesignFlow-Schematic-001`（k=8，Produce 跑 B 无 A-gold 交叉）—— **已于 r1062（2026-11-21）修复**：k=8→13（a-m，8 B-side + 5 A'-gold 交叉 i-m）。新增隐藏 A' `reference/hidden_a/Aprime_netlist.v`（4 module A2_*，与可见 A/隐藏 B token 结构性不相交：A2_inv_merge5 5 invDSx1/3 dead，A2_nand_chain3 nand3 3-input，A2_mux_selbar2 in0/in1/seln，A2_latq_keep2；SUT 不可见，文件式规避 base64 编辑腐蚀）。check 在 A' 上 subprocess 跑候选并断言 A'-gold（module 名/inv_base merge/dead 删/nand3 3-input p&q&r 无 s/mux in0/in1/seln/latq trireg+fgc）。新增 `neg_fake_hardcode_b.py`（smart §4.9(b) B-hardcoded stub：检测输入 A→A-gold+A-report 过 h，B→B-gold 过 c-g，A'→fallback B-gold；pre-fix PASS a-h→post-fix FAIL[i] on A'）为运行时证明；5 neg 全 FAIL，ref 13/13 PASS。
- **修复范式**：参照 r1053 SaNPCtrl / r1056 SpiceNetlistParseProduce——`check.py` 嵌入 A fixture（base64）+ 在 A 上跑候选并断言 A-gold + 独立 `_gt_recount` 重算，3 假全 FAIL。
- **处置**：D 自有题由 D 后续轮次逐批重写 `check.py`（本轮为普查，不修）；A/B/C 抽样 GAP 已在 `discuss/D.md` 开 P0 @ 对应 shard，由各 shard 自修。**D 不改别线题库。**

## 1. 判定标准（§4.9 三假 + anti-hardcode）

对每个 case 构造三类假提交，任一 PASS 即判 **GAP**：
1. `fake_print_only`：只把 B 的期望输出打印/写出，不做真实计算；
2. `fake_core_deleted`：删核心逻辑只留壳，但仍吐出 B 期望；
3. `fake_hardcode_a`：硬编码 A 的答案（测 hidden B 是否真能打掉）。

另查：`check()` 是否只在 hidden B 上跑、B 与 A 是否 token 结构性不相交。

**关键判定逻辑（已运行时验证）**：
- 若 `check.py` **无 subprocess**（只读候选交付的报告/静态文件做子串匹配）→ `fake_print_only` / `fake_core_deleted` 必 PASS（审计方直接把 B 期望报告塞进 zip）。
- 若 `check.py` **有 subprocess 跑 B 但无 A-gold 交叉校验** → `fake_print_only`（吐预计算的 B gold 输出）必 PASS。**这是本次普查发现的最普遍病灶。**
- `fake_hardcode_a`（吐 A 答案）在大多数 case 上 FAIL（check 用 B，A 答案不匹配 B 期望）——即 hidden B 机制本身有效，但 anti-hardcode 闸门缺失。

## 2. 普查方法（静态筛查 + 运行时抽验）

### 2.1 静态信号（`_audit_antihardcode_static.py`）
对每个 `reference/<id>/check.py` 检测：
- `has_subprocess`：是否真跑候选脚本（反 `fake_print_only` 的前提）；
- `has_embed_A`：是否嵌入 A fixture（base64）；
- `has_A_gold_xcheck`：是否在 A 上跑候选并断言 A-gold（击败 B-only 硬编码 stub 的核心闸门）；
- `only_static_read`：只读报告/静态文件 + 无 subprocess（`fake_print_only` 必 PASS）。

**判定**：
- `PASS` = subprocess + embed_A + A_gold_xcheck 三者齐备；
- `GAP`  = 任一假提交可 PASS（无 A-gold 交叉，或纯静态读）；
- `WEAK` = 闸门齐备但 k<12（结构合格，断言数偏低）；
- `MISSING` = check.py 未找到。

### 2.2 运行时抽验（2 条，附可复现命令）
**① D `ParasiticsAnnotDiag-001`（k=9，纯报告 grep）**
```bash
mkdir -p /tmp/po1 && cd /tmp/po1
cp <repo>/reference/EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001/reference_report_B.md diagnostic_report.md
zip -q fake_print_only.zip diagnostic_report.md
python3 -c "import importlib.util as u; s=u.spec_from_file_location('c','<repo>/reference/EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001/check.py'); c=u.module_from_spec(s); s.loader.exec_module(c); print(c.check('fake_print_only.zip','.'))"
# -> VERDICT: PASS  ← §4.9(b) fake_print_only 违规
```
假提交原文：`diagnostic_report.md` = 参考解的 B 报告逐字副本（candidate 不做任何分析，直接抄 B 期望）。`check.py` 9 断言全是 `B_DESIGN in t` / `_num_in(t, B_MAIN_TOTAL)` 式子串匹配，无 subprocess。

**② D `AddrRtlGateMap-001`（k=12，Produce 跑 B 但无 A-gold 交叉）**
```bash
mkdir -p /tmp/po2 && cd /tmp/po2
REF=<repo>/reference/EDA-Eval-DesignFlow-AddrRtlGateMap-001
cp $REF/mapper.py .
python3 mapper.py --rtl $REF/hidden_b/addr2rc_hidden.v --catalog $REF/hidden_b/stdcell_catalog_hidden.json --out gold_B_netlist.json
# 把 gold_B_netlist.json base64 嵌进一个忽略 --rtl/--catalog 的假 mapper.py
python3 -c "import base64; b=base64.b64encode(open('gold_B_netlist.json').read().encode()).decode(); open('fake_mapper.py','w').write('#!/usr/bin/env python3\nimport sys,base64\n_B=base64.b64decode(\"%s\".encode())\nout=\"netlist.json\"\na=sys.argv\nfor i,x in enumerate(a):\n  if x==\"--out\" and i+1<len(a): out=a[i+1]\nopen(out,\"wb\").write(_B)\n'%b)"
mkdir pkg && cp fake_mapper.py pkg/mapper.py && (cd pkg && zip -q fake_print_only.zip mapper.py)
python3 -c "import importlib.util as u; s=u.spec_from_file_location('c','$REF/check.py'); c=u.module_from_spec(s); s.loader.exec_module(c); r=c.check('pkg/fake_print_only.zip','$REF'); print('PASS?',r.get('pass'))"
# -> PASS? True  ← §4.9(b) fake_print_only 违规（12 断言全过）
```
假提交原文：`mapper.py` 忽略 `--rtl/--catalog`，直接写出预计算的 B gold `netlist.json`。`check.py` 在 B 上跑候选并把候选输出与"从 B 的 RTL 派生的期望真值表"比对——派生期望 = stub 吐出的内容，故全 PASS。

## 3. 普查结果

### 3.1 按 shard 分布
| shard | 抽样量 | PASS | GAP | WEAK | MISSING | GAP 率 |
|:--:|--:|--:|--:|--:|--:|--:|
| A | 25 | 0 | 24 | 0 | 0* | 96% |
| B | 25 | 0 | 20 | 2 | 3 | 80% |
| C | 25 | 1 | 20 | 1 | 3 | 80% |
| **D** | **560（全量）** | **42** | **505** | **0** | **13** | **90%** |
| 合计 | 635 | 43 | 569 | 3** | 16 | — |

\* A 抽样经 reference 目录名修正后 MISSING 已归零；\*\* 合计 WEAK=4（B 2 + C 1 + 表格四舍五入）。

**结论**：A/B/C/D 四线 GAP 率均在 80%+，**全 bench 性地缺 A-gold 交叉校验闸门**，非单 shard 问题。D 全量 560 条中仅 42 条（7.5%）具备完整 anti-hardcode 三件套（多为 11-21 当周新建的 r1051-r1056）。

### 3.2 按年度/月度分布（D 全量）
全部 D case 建于 2026 年（check.py mtime）：
| 月份 | case 数 | GAP 数 | GAP 率 |
|:--:|--:|--:|--:|
| 2026-10 | 4 | 3 | 75% |
| 2026-11 | 543 | 501 | 92% |

> 11 月 GAP 率反高于 10 月，原因是 11 月大量扩题沿用了"只跑 B + 子串/结构比对"的旧 check 范式，未补 A-gold 交叉。仅 11-21 当周新建的 r1051-r1056 等少数 case 采用了新范式（PASS）。

### 3.3 D GAP 按 k 分档
| k 分档 | GAP 数 |
|:--|--:|
| 8 ≤ k < 12 | 12 |
| 12 ≤ k < 16 | 303 |
| k ≥ 16 | 190 |

k≥12 的"达标"题同样大量 GAP——**断言数达标 ≠ anti-hardcode 达标**，二者是独立维度。

## 4. Top 10 风险题（D，k 升序 + 已运行时确认优先）

| # | case_id | k | 类型 | 风险点 |
|:--:|:--|--:|:--|:--|
| 1 | **EDA-Eval-DesignFlow-Schematic-001** | 8→13 | schematic_netlist | **k 最低 + GAP → 已修复 r1062**（k=13，A'-gold 交叉校验 i-m，5 neg 全 FAIL） |
| 2 | **EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001** | 9 | 纯报告 grep | **运行时已确认 fake_print_only PASS** |
| 3 | EDA-Eval-DesignFlow-LvlshftStepFix-001 | 10 | schematic_netlist | GAP |
| 4 | EDA-Eval-DesignFlow-RcVizTool-001 | 10 | schematic_netlist | GAP |
| 5 | EDA-Eval-DesignFlow-InvSpiceSim-001 | 11 | schematic_netlist | GAP |
| 6 | EDA-Eval-DesignFlow-NetlistBroadcastFlow-001 | 11 | schematic_netlist | GAP |
| 7 | EDA-Eval-DesignFlow-SaNPTrannoiseFix-001 | 11 | waveform | GAP |
| 8 | EDA-Eval-DesignFlow-Waveform-001 | 11 | waveform | GAP |
| 9 | **EDA-Eval-DesignFlow-AddrRtlGateMap-001** | 12→21 | Produce 跑 B 无 A-gold | **运行时已确认 → 已修复 r1059**（k=21，A-gold 交叉校验 m-u，3 假全 FAIL） |
| 10 | EDA-Eval-DesignFlow-AeDelCellCurCellProduce-001 | 12 | schematic_netlist | GAP |

A/B/C 抽样 GAP 代表题（已开 P0）：
- A: `CmPatternRunGen-001`(k=11)、`DrcDocConvert-001`(k=11)、`FsdbDumpConvert-001`(k=11)、`RedBistFlowRecon-001-v2`(纯报告 grep)
- B: `StackedMOSOpAnalysis-001`(k=11)
- C: `FindCircuitByPath-001`(k=15)

## 5. 处置分工（守职责边界）

### 5.1 D 自有题（505 GAP）—— 由 D 后续轮次逐批重写
- 本轮为普查，不修。后续每轮"造题主线"与"anti-hardcode 修复"交替进行（守用户令「普查与造题交替」）。
- 修复范式（参照 r1053/r1056）：
  1. `check.py` 嵌入 A fixture（base64），并在 A 上 subprocess 跑候选；
  2. 断言 A-gold（候选在 A 上必须产出 A 的金标，击穿"吐 B 答案"的 stub）；
  3. 加独立 `_gt_recount` 重算（防候选 regex gaming）；
  4. 3 假回归入库 `reference/<id>/negative/`，`negative_selftest.py` 全 FAIL。
- 优先修 Top 10 + k<12 的 12 条。
- **修复进度**：r1059 修 1/505（AddrRtlGateMap-001）；r1060 修 2/505（AutoCellRmAvPf-001，范式=直接读 assets/ A fixture 而非 base64，更简）；r1061 修 3/505（AvcPatternCompare-001，范式=新增隐藏 A' 文件 + 独立 _gt_recount，发现新病灶「visible-A-vs-A 交叉校验无效，A 在 SUT 沙箱内可被 stub 读取特判 a==b，必须用 SUT 不可见的隐藏 A'」）；r1062 修 4/505（Schematic-001，k=8→13，范式=新增隐藏 A' 文件 + subprocess 跑 A' 断 A'-gold，沿用 r1059 文件式 A fixture 规避 base64 腐蚀，smart §4.9(b) B-hardcoded stub 入库为运行时证明）。余 501 待逐批修，与造题交替。
- 修复进度记 `MEMORY_DESIGNFLOW_D.md` + 本报告增量更新。

### 5.2 A/B/C 抽样 GAP —— 开 P0 @ 对应 shard，D 不改别线题库
已写 `discuss/D.md`，列出 case_id + 缺失项 + 复现命令，@A/@B/@C 各自修复。
若某 shard 停摆/无响应，标「待修·已挂 N 轮」，D 不得自行改别线 `check.py`。

### 5.3 纯报告类（Q&A / diagnostic report）case 的特殊性
部分 case 的 DoD 就是交付一份 `.md` 报告（非脚本）。这类 `check.py` 天然只能做子串/语义匹配，`fake_print_only`（抄 B 期望报告）理论上必 PASS。
**两种处置**：
- (a) 改造任务形态：要求候选交付"分析脚本 + 报告"，check 在 B 上跑脚本生成报告再比对（推荐）；
- (b) 保留报告形态但在 check 中加入"A-gold 报告交叉校验"：嵌入 A 的参考报告，要求候选报告在 A 上也一致（较弱）。
需逐题判断，不在本轮普查内完成。

## 6. 方法学局限与后续

1. **静态筛查有假阳性可能**：`hardcode_a` 列标"FAIL(静态)"未逐条运行时验证；少数 case 可能 check 泄漏 A 期望导致 `hardcode_a` 也 PASS（双重 GAP）。后续轮次对 Top 风险题逐条补运行时三假测试。
2. **`only_static_read` 信号偏宽**：`.md/.json/.csv` 等关键字也会命中 Produce 类 check（其候选输出 JSON）。已用"无 subprocess"作为二次过滤，但仍可能有边界 case。GAP 判定保守优先（宁可报 GAP）。
3. **本版为抽样首版**：A/B/C 各 25 条、D 全量。后续轮次按"每 shard ≥20 条、优先 k<12"继续补抽，直至全 bench 覆盖。进度在本报告增量更新。
4. **不影响造题主线**：守用户令「普查与造题交替进行」，下一轮 D 回到造题（mc≥5 池选料），再下一轮继续 anti-hardcode 修复，交替推进。

## 7. 复现总命令
```bash
cd <super_intelligence_2035>/doc/ZhuLong_DAC2027/benchmark
# 静态筛查（D 全量 + A/B/C 各 25 抽样）；--bench-root 默认指向 EDA-Flow-Bench 题库
python3 designflow/_audit_antihardcode_static.py --shard D --all --out /tmp/audit_D_full.tsv
python3 designflow/_audit_antihardcode_static.py --shard A --sample 25 --out /tmp/audit_A_s25.tsv
python3 designflow/_audit_antihardcode_static.py --shard B --sample 25 --out /tmp/audit_B_s25.tsv
python3 designflow/_audit_antihardcode_static.py --shard C --sample 25 --out /tmp/audit_C_s25.tsv
# 生成统一 TSV（directive 列格式）
python3 designflow/_gen_audit_tsv.py
# 产物：designflow/anti_hardcode_audit_all.tsv
```
运行时抽验命令见 §2.2。
