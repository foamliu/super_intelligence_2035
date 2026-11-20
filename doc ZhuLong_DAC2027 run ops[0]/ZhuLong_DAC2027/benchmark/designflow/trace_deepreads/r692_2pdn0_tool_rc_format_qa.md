# r692 deepread — 2pdn0 (e0045128@hfeg0pkn001) tool→RC-format mapping Q&A

> **round**: r692 (2026-11-17) · **slug**: 2pdn0 · **session**: 1791940499909_2pdn0 ·
> **user**: e0045128 · **host**: hfeg0pkn001 (10.129.2.10) · **mc**: 34 · **domain**: eda_other ·
> **trace path** (remote, EXISTS nested subdir): `/home/e0045128/.cline/data/sessions/1791940499909_2pdn0/1791940499909_2pdn0.messages.json` ·
> **NMSG**: 20 · **tools used**: search_codebase(1), RAG_MCP_Server__search_apis(3) — pure knowledge Q&A, 0 run_approved_command, 0 read_files, 0 editor.
> **status**: r691 pool_reaudit marked 可造 (revived: analysis-Q&A). r692 peek + full assistant-answer extraction. **DEBT 1 → r693 synthesize.**

## 一、用户真实意图（verbatim, 6 user turns）

逐字从 trace 抽取（`<user_input mode="act">` 标签内原文）：

- **U#0**: `genus physical synthesis的时候需要吃哪些文件`
- **U#8**: `中文回答`
- **U#10**: `genus 是吃TLUPlus还是QRC 文件`
- **U#12**: `DC是吃QRC 还是TLUPlus`
- **U#14**: `starRC是吃TLU plus还是QRC`
- **U#16**: `milkway 和 TLUplus 的文件后缀是什么样的`
- **U#18**: `DC 做physical synthesis必须吃milkway吗`

**意图归纳**：用户在做 genus/DC 物理综合时，想搞清楚各 EDA 工具（genus/DC/starRC）与寄生参数格式（TLUPlus/QRC）的对应关系 + 库文件（milkyway/TLUplus）后缀 + DC 物理综合是否必须吃 milkyway。**纯知识咨询 Q&A，无项目文件依赖**（用户只问概念，agent 用 RAG/search_codebase 答，无 read_files/run_approved_command）。

## 二、助手答案核心事实（verbatim, 用于 check() gold-facts）

### 2.1 工具 → 寄生参数格式映射（A#11/A#13/A#15）

| 工具 | 厂商 | 吃 TLUPlus | 吃 QRC TechFile | 角色 | 读取命令 |
|---|---|---|---|---|---|
| **Genus** | Cadence | ✅ 兼容 (`-tluplus` 标志) | ✅ **原生推荐** | consumer | `read_parasitic_tech [-tluplus] <file>` |
| **DC** (Design Compiler) | Synopsys | ✅ **原生** | ❌ 不支持 | consumer | `set_tlu_plus_files -itf_lib1 ... -tluplus_file ...` |
| **StarRC** | Synopsys | ✅ **生成** (从 ITF/nxtgrd) | ❌ | **extractor** (生成 TLUPlus) | `StarXtract -clean rcbest.itf -o rcbest.tluplus` |
| **Quantus** | Cadence | ❌ | ✅ **生成** | extractor (生成 QRC) | — |

**关键判别点**（check 牙）：
- Genus 两吃但推荐 QRC（Cadence 自家）；TLUPlus 走 `read_parasitic_tech -tluplus`，QRC 走 `read_parasitic_tech <file>`（无标志）。
- DC 只吃 TLUPlus（Synopsys 自家），**不吃 QRC**。
- StarRC **不是 consumer**，是 **extractor**，从 ITF/nxtgrd **生成** TLUPlus 供 DC/ICC2/PrimeTime 用。
- 厂商对应：Synopsys→TLUPlus，Cadence→QRC。

### 2.2 文件后缀（A#17）

| 格式 | 后缀 | 说明 |
|---|---|---|
| **TLUPlus** | `.tluplus` | 单个二进制文件（StarXtract 从 `.itf`/`.nxtgrd` 生成） |
| **TLUPlus 源** | `.itf` / `.nxtgrd` | 工艺厂原始 interconnect tech format |
| **Milkyway** | **目录**（非单文件）；引用时 `.mw` | 内部 `.mw`/`.dat`/`.str`/`.ref`/`.prt`/`.wif`；reference library 是目录树 |
| **QRC TechFile** | `.qrcTechFile` | Cadence Quantus 格式 |

**关键判别点**：Milkyway 是**目录结构**不是单文件（区分于 TLUPlus 的单二进制文件）；`.mw` 是引用后缀非文件后缀。

### 2.3 DC 物理综合是否必须吃 Milkyway（A#19）

- **DC 逻辑综合（线负载估算）** → ❌ **不需要** Milkyway（只用 `.lib`+RTL+SDC + wire load model）。
- **DC Ultra / DC Physical / DC-Topographical**（真物理步骤）→ ✅ **需要** Milkyway（物理版图信息 + TLUPlus 做 real 线长 RC + 顶部物理库 TOP 放置单元）。

**关键判别点**：分两种情况，"必须"取决于 DC 物理综合的具体类型（线负载 vs topographical）。

## 三、可造性判定（11-15 新标准）

| 判据 | 结论 |
|---|---|
| 有真实 trace 可溯源 | ✅ e0045128@hfeg0pkn001, session_file + verbatim U/A |
| 用户真实意图 | ✅ 工具-RC-格式映射咨询（eda_other，A-domain 合法） |
| 写得出有牙 check() | ✅ 见下 §四 合成计划（tool→format 映射可结构化判分） |
| 域归属 | ✅ eda_other（genus/DC/starRC 物理综合配置咨询） |

**判定：可造**（C-A analysis-Q&A，A-faithful verbatim Q&A，B-档合成变体 anti-hardcode）。
**旧筛子误判**：旧 r37 survey 标 "pure Q&A (genus/DC/starRC eat TLUPlus or QRC, milkyway suffix). 20 msgs, no delivery" → 按旧规则 "no delivery artifact = weak" 判 parked。**11-15 新标准作废该判据**：analysis-Q&A 合法，deliverable=结构化映射报告，check() 验映射正确性。

## 四、合成计划（DEBT 1 → r693 落地）

- **case_id**: `EDA-Eval-DesignFlow-ToolRcFormatMapQa-001`
- **domain**: eda_other
- **task form**: C-A analysis-Q&A / tool-config knowledge-table
- **A 档**（SUT 可见）: 6 verbatim Q&A 对（genus/DC/starRC × TLUPlus/QRC + milkyway/TLUplus 后缀 + DC-physical-must-milkyway），用 trace 原话作 prompt。**A 档不可行做 live 复现**（无项目文件，纯知识）→ 用 verbatim Q&A 作 prompt + 内嵌 A 的 gold-mapping 作 anti-hardcode 对照。
- **B 档**（hidden, 不进 SUT）: **不同工具集**强制 anti-hardcode。问 **Innovus / Tempus / ICC2 / PrimeTime** × **QRC / nxtgrd / TLUPlus / TechFile** + **NDM / TechFile** 后缀 + **Innovus 是否必须吃 NDM**。B 的正确映射：
  - Innovus (Cadence) → QRC TechFile 原生 + TLUPlus 兼容；`read_parasitic_tech`
  - Tempus (Cadence STA) → QRC + TLUPlus
  - ICC2 (Synopsys PnR) → TLUPlus + nxtgrd
  - PrimeTime (Synopsys STA) → TLUPlus（signoff）
  - NDM (Innovus library) → 目录，`.ndm`
  - Innovus → 必须 NDM（reference library + tech lef）
  - B 工具/格式/后缀 ≥10 维全异于 A
- **交付物**: `analyze_tool_rc_format_mapping(tool_config.json)` 通用函数 — 读 B 的 tool_config.json（列出 B 工具 + 角色 + 厂商）→ 输出 `tool_rc_mapping_report.json`（结构化：tool→{rc_formats, read_cmd, role, suffix, must_eat}）。
- **check.py k≥10 断言**（逐条独立可 FAIL）:
  ① report 是 dict + 函数执行返回结构化 JSON
  ② Innovus RC-format 映射正确（QRC 原生 + TLUPlus 兼容）
  ③ Tempus 映射正确
  ④ ICC2 映射正确（TLUPlus + nxtgrd）
  ⑤ PrimeTime 映射正确（TLUPlus signoff）
  ⑥ 厂商↔格式对应正确（Cadence→QRC, Synopsys→TLUPlus/nxtgrd）
  ⑦ extractor vs consumer 角色判定正确（Quantus/StarRC=extractor, 其余=consumer）
  ⑧ read-command 语法正确（带/不带 `-tluplus` 标志区分）
  ⑨ NDM 后缀 + 目录结构判定正确（非单文件）
  ⑩ Innovus-must-eat-NDM 判定正确（是）
  ⑪ anti-hardcode: B 报告 ≠ A 的映射（A=genus/DC/starRC, B=Innovus/Tempus/ICC2/PT，工具名集合不同）
  ⑫ 3-seed 确定性
- **negatives (≥2)**: neg_wrong_mapping（Innovus↔Synopsys 格式互换）→ ②⑥ FAIL; neg_hardcoded_A（输出 A 的 genus/DC/starRC 映射）→ ②③④⑤⑪ FAIL; neg_stub（缺键）→ ① FAIL; neg_print_expected（硬编 B 期望串）→ ⑪ anti-hardcode FAIL.
- **§4.9 三假**: empty-shell → ① FAIL; print-expected → ⑪ FAIL; core-deleted → ②-⑩ FAIL.
- **§4.2 subprocess**: check 在独立 tmpdir 解 zip，subprocess 跑 candidate `analyze_tool_rc_format_mapping.py` on B's `tool_config.json`，解析输出 JSON 结构（非文本相似）。
- **自验**: ref 10+/10+ PASS + 4 neg 全 FAIL + §4.9 三假全 FAIL + negative_selftest + e2e jsonl round-trip.

## 五、r678 audit 修正（本 round 附带发现）

r691 MEMORY 称 "r678 列出的 18 条 fresh truly-A 候选全在远程主机... 远程 A-domain fresh 在 mc≥5 口径下尚未重审"。r692 复核 r678 的 11 unique slugs 的 **keyword profile**（来自 summary.tsv）：

| slug | user@host | mc | dominant keywords | 域判定 |
|---|---|---|---|---|
| v593e | t0002614@hfeg0pkn004 | 82 | aether:346 netlist:295 schematic:114 mixed-signal:51 verilog:41 | **C** (aether/layout) |
| hasla | zqzhan@hfeg0pkn002 | 41 | drc:2662 netlist:2246 analog:24 hspice:17 verilog:6 | **C** (DRC) |
| jr0o3 | ronghu@hfeg0pkn005 | 44 | netlist:90 transistor:36 .cdl:33 lvs:27 schematic:21 synopsys:17 | **C** (LVS/schematic) |
| bih9j | thomasz@hfeg0pfn058/002 | 99 | drc:583 analog:172 netlist:127 .gds:25 transistor:17 lvs:14 | **C** (DRC/GDS) |
| i0cnz | mwxi@hfeg0pkn003 | 13 | calibre:84 verilog:47 drc:44 analog:10 virtuoso:9 innovus:8 | **C** (calibre/DRC) innovus 弱 |
| fdrqq | zxtu@hfeg0pkn001 | 10 | netlist:79 synopsys:16 hspice:5 pyaether:3 calibre:2 | C/B (netlist/hspice) |
| f1pj5 | jingc@hfeg0pkn001 | 27 | aether:144 mixed-signal:18 floorplan:18 pyaether:16 schematic:15 | **C** (aether/pyAether) |
| 1e0xa | sagequan@hfeg0pkn001 | 23 | analog:30 calibre:16 hspice:15 rtl:10 aether:7 synopsys:5 | C/B (analog/calibre) rtl 弱 |
| cn4bl | steveny@hfeg0pkn001 | 13 | pyaether:97 virtuoso:20 aether:10 pdk:2 dbcreateinst:2 | **C** (pyAether/virtuoso) |
| kubzy | zhililu@hfeg0plg52/040 | 29 | netlist:178 aether:167 schematic:83 transistor:48 lvs:31 pdk:29 pex:20 | **C** (aether/LVS/pex) |
| ibwba | zhililu@hfeg0plg52/040 | 48 | netlist:604 spectre:210 maestro:202 virtuoso:190 analog:118 pex:106 | **B/C** (spectre/maestro) |

**结论**: r678 的 11 slugs（18 含多 host 出现）**全部 C/B 域主导**（aether/netlist/schematic/drc/virtuoso/lvs/pex/spectre），A 关键词（verilog/rtl/synopsys/innovus）只是**弱噪声**（verilog:6/41/47, synopsys:5/16, innovus:8, rtl:10）。`trace_ledger next` 的 shard-A 关键词过滤器在这些弱信号上误触发了 "A-domain" 归属。**r678/r691 "远程 fresh truly-A" 的定性不准确**——它们是 C/B 域 session 混入弱 A 关键词，**非真 A-domain 候选**。

**对 auto-stop 的影响**: r691 称 "auto-stop 不触发因远程 A-domain fresh 未审"。r692 已审：远程 r678 的 11 slugs 全 C/B 域，**远程 mc≥5 r678-list 在 faithful-A-domain 口径下 0 viable**。叠加 r691 的 hfhds201 本机 mc5-9 0/18 viable + r689 mc≥10 0 fresh → **mc≥5 全可达池在 "能忠实还原 A-domain 意图 + 可判分" 口径下确证耗尽**。

**但**: parked_reaudit_A.tsv 有 69 条 EXISTS 复活队列（11-15 新标准 revival，含 2pdn0/0yyhj/78z8d 等），其中多条 A-domain + trace EXISTS + 可判分（如 2pdn0 本 deepread 确证可造）→ **池在 revival 口径下未耗尽**，应继续从 parked_reaudit EXISTS 队列造题，**不触发 auto-stop**，shard_mc.A 维持。

## 六、下轮 r693 建议

1. **优先兑现 DEBT 1**: 按 §四 合成计划落地 `ToolRcFormatMapQa-001`（A.jsonl 350→351）。
2. 备选: 若 2pdn0 合成遇阻，转 0yyhj（188 msgs, opene902 RTL/synthesis/harden/verdi, digital, 需 /proj/lacaa 远程文件 fetch 进 workdir 深读子片 U#72/U#86/U#88）。
3. 继续从 parked_reaudit EXISTS 队列选料（69 条，多 A-domain）。
