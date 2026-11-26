# Deepread · 1788937019731_ccgt1 · jiaqis · DRC enclosure-rule extractor

> shard C candidate (r389 selection round). SEED picked, deepread complete.
> 下轮（r390）基于本 deepread 合成 case：`DrcEnclosureTripleExtract-001`（physical_verify, faithful A档 候选）。

## trace_source

- session_file: `1788937019731_ccgt1.messages.json`
- user: jiaqis (e0023936 同人？— r319 DrcVsDrmRuleAudit-001 也是 jiaqis/tro04，jiaqis 是 DRC deck developer 常客)
- host: hfeg0plg76 (10.129.8.124 也存)
- mc: 251 (mc≥10 口径, 11/09 snapshot)
- keywords: `drc:1207;calibre:18;.def:8;gdsii:1` — drc 关键词 1207 来自 V05_coding/*.drc/*.rules 文件内容（true-positive，本次 trace 真在解析 DRC deck）
- match_count: 251
- 6 user turns, 42 tool_uses (39 run_commands + 2 read_files + 1 search_codebase), 94 messages total

## real_task_summary

用户在 `/home/jiaqis/work/DRC/zlworking/` 工作，要求把 `../V05_coding/` 目录里的 **Calibre SVRF DRC deck**（`.drc` + `.rules` 文件，61 个）中所有 **enclosure 规则**整理出来，并按 **ID + Description + Coding 三维度交叉判断**（而非单看 coding）筛选真正的 enclosure 规则，输出一个汇总文档。

**关键对话节点**：
- turn 0 (plan): scan `../V05_coding` folder
- turn 1 (plan): 切换中文
- turn 2 (act): 复制 V05_coding 到工作目录
- turn 3 (act): 仅读取当前项目目录下文件
- turn 4 (plan): 「读取这些 DRC 的 deck 把其中所有关于 enclosure rule 的规则给我整理一下」← **主任务**
- turn 5 (plan): 「你这个是怎么判断他是 enclosure 命令的，通过 ID+description+coding，还是单 coding，我需要你结合三者判断。同时将这些 rule+deck 摘出来，放在一个文档里面」← **三维度判定要求的来源**

## agent 实际产出（deliverable）

agent 产出 3 个文件，落在 `/home/jiaqis/work/DRC/zlworking/`：

| 文件 | 大小 | 说明 |
|---|---|---|
| `V05_coding_enclosure_rules.md` | 850 KB / 20,339 行 | 主文档：1238 个 enclosure 规则块完整内容（ID + Description + 完整代码体），按文件分组，每块标注三维度匹配状态 |
| `enclosure_blocks.json` | 956 KB | JSON 结构化数据，便于程序化处理 |
| `extract_enclosure.py` | — | Python 3 提取脚本（核心逻辑） |

**主文档 4 章节**：① 统计概览 ② 判断标准 ③ 按文件分布 ④ 按文件分组的完整规则块。

## 三维度判定算法（核心 — 这是 case 的 hard part）

| 维度 | 说明 | 匹配模式 |
|---|---|---|
| **ID（规则名）** | 规则块名中含 enclosure 缩写 | `_EN_\d`, `_ENC_\d`, `_E_\d`, `.EN.` 等 |
| **Description（描述行）** | `@` 描述行中含 enclosure/enclosed/enclose | 不区分大小写 |
| **Coding（代码体）** | 代码中使用 `ENC` 命令（Calibre SVRF ENCLOSURE 缩写） | `ENC <layer> <layer>`, `ENC (<expr>) <layer>`, `BY ENC` |

**筛选规则**：三项中至少两项匹配，OR Description 单独匹配，OR Coding+ID 同时匹配。

## 统计结果

| 指标 | 数量 |
|---|---|
| 解析的规则块总数 | 17,038 |
| **Enclosure 规则块（三者交叉判断）** | **1,238** |
| 三项全部匹配 (ID✓ + Desc✓ + Code✓) | 703 |
| 两项匹配 | 461 |
| 仅一项匹配 | 74 |

两项匹配细分：
- ID✓ + Desc✓ (Code✗): 448 — 使用替代方法（INT/EXT/EXPAND EDGE 角点检查）验证 enclosure
- Desc✓ + Code✓ (ID✗): 13 — 规则名不含 EN 缩写但描述和代码都明确是 enclosure
- ID✓ + Code✓ (Desc✗): 0

一项匹配细分：
- 仅 Desc✓: 74 — 主要是 "Enclosed area" 类规则（HOLES/AREA 检查包围面积）

**按文件分布 Top 10**：
| 文件 | 规则块数 | 模块 |
|---|---|---|
| 4_5_53_Vy.rules | 220 | Vy 通孔 |
| 6_5_OCOL_rules.drc | 109 | OCOL dummy |
| 4_8_5_SRW_rules.drc | 94 | Sealring SRW |
| 4_5_45_M1.rules | 93 | M1 金属层 |
| 4_8_7_CSS_rules.drc | 82 | Sealring CSS |
| 4_8_2_3_6_Sealring_SRC_CSR_rules.drc | 45 | Sealring |

## tool mix

39 run_commands（grep/awk/sed/cat/cp/python3 执行 + extract_enclosure.py 编写与迭代）+ 2 read_files（初探 1_1_environment.drc / 1_3_variable.drc / ts_auto）+ 1 search_codebase（enclosure 正则多模式查询）。**run_commands 占 92.9%** — 典型 DRC deck parse 任务，hard part 是 grep/awk 模式设计与 python extractor 迭代，不是驱动 Calibre 二进制。

## shard C 域分类

**physical_verify** — DRC deck 静态解析（rule block 分类 + enclosure 命令识别），不调 Calibre 跑实际 DRC，但产出物是 DRC deck 审计报告。与已有 case 同域：
- `DrcDeckCmpGen-001` (r323, kenwang/xnk5l) — DRC deck 对比
- `DrcVsDrmRuleAudit-001` (r319, jiaqis/tro04) — DRC vs DRM 规则审计（同 user jiaqis）
- `DrcExactWaiver-001` (r321, sherlock/6widi) — DRC exact waiver
- `DrcBad2gridLshape-001` (r322, e0023936/uxowi) — DRC bad2grid L-shape

## case 合成计划（r390 执行）

**case_id**: `EDA-Eval-DesignFlow-DrcEnclosureTripleExtract-001`
**档位**: A档 faithful（用户明确给三维度判定要求，agent 实现忠实复刻 — 不是 synthesized）
**mode**: design_flow
**entry_point**: `outputs/submit.zip`（含 V05_coding_enclosure_rules.md + enclosure_blocks.json + extract_enclosure.py）

### 资产（visible A / hidden B）

- **visible A**：V05_coding/ 目录的 **subset**（选 3-5 个 .drc/.rules 文件，含已知 enclosure 规则的样例 + 至少 1 个不含 enclosure 的对照文件），以及任务 prompt（用户 turn 4 + turn 5 合并）
- **hidden B**：V05_coding/ 的 **另一 subset**（不同 3-5 个文件，agent 未见过），用于 check() 验证 extractor 的泛化性 — 这是 hidden input 的关键

> 注意：V05_coding/ 在 .75 的 hfeg0plg76:/home/jiaqis/work/DRC/V05_coding/ — 下轮需 scp 几个文件到本地，构造资产包。资产大小控制：每个 .rules/.drc 选 < 100KB 的，total < 500KB。

### check() 双参签名

`check(deliverable, workdir)` — 解压 submit.zip，对 hidden B 的 deck 跑 agent 提交的 extract_enclosure.py，验证：

1. submit.zip 解压成功 + 3 个核心文件齐全
2. extract_enclosure.py 可执行（python3 + LD_LIBRARY_PATH 处理）
3. 在 hidden B 上跑 extractor，输出规则块数 == 预期（hidden B 的 ground truth 由 ref 预先跑出）
4. 主文档章节结构完整（4 章节齐）
5. 三维度判定逻辑正确：抽查 1 个 triple-match 规则块，验证 ID+Desc+Code 三标志位
6. 抽查 1 个 ID✓+Desc✓+Code✗ 规则块，验证替代方法（INT/EXT/EXPAND EDGE）确实出现
7. 抽查 1 个仅 Desc✓ 规则块，验证是 HOLES/AREA enclosed-area 类
8. JSON 结构化数据可 parse，且 enclosure_blocks.json 的规则块数 == md 文档计数
9. （可选）按文件分布表 Top 3 与 ground truth 一致

**断言闸门**：k_rationale == k_check ≥ 8。预计 k = 9-12。

### subprocess 真跑条件

check() 必须 ≥1 subprocess 真跑：在 hidden B 上执行 `python3 extract_enclosure.py`（agent 提交的脚本），比对输出与 ref ground truth。这是「真跑条件」满足点。

### negative samples (≥2)

- **neg1 (empty_shell)**：submit.zip 内 extract_enclosure.py 是空壳（仅 print），跑出 0 规则 → check() assert 3 (规则块数==预期) FAIL
- **neg2 (hardcode_a)**：extract_enclosure.py 硬编码 visible A 的规则块数（如 1238），跑 hidden B 也输出 1238 → assert 3 FAIL
- **neg3 (omit_desc_check)**：extract_enclosure.py 删掉 Description 维度，只看 ID+Code → 74 个仅 Desc✓ 规则被漏掉 → assert 5 (三维度逻辑) FAIL
- **neg4 (omit_json)**：submit 缺 enclosure_blocks.json → assert 8 FAIL
- **neg5 (wrong_section)**：md 文档只有 1 章节 → assert 4 FAIL

### omission-negative (可选，r390 评估)

cond 候选：**cond (s) = omit triple-criteria fallback rule**（"至少两项匹配 OR Desc 单独 OR Coding+ID" 的 fallback 分支）。删掉 fallback → 边界 case（仅 Desc✓ 的 74 个 + ID✓+Code✓ 的 0 个）漏掉 → assert 5 FAIL。但需 survey 确认 cond (s) 是否被 on-disk physical_verify 14 条覆盖；若已覆盖则换 cond。

### 风险与注意

1. **资产构造工作量大**：需 scp V05_coding/ 的几个文件、预跑 ref extractor 得 ground truth。下轮 r390 budget 需预留 15 min 给资产构造。
2. **extract_enclosure.py 依赖 LD_LIBRARY_PATH=/apps/local/python/python-3.7.1/x86_64/lib** — SUT 沙箱需有 python3 + 该库路径（或换用系统 python3，验证脚本兼容性）。check() subprocess 真跑需复现此环境。
3. **hidden B 选择**：必须选 agent trace 中**未读取过**的文件（trace 中 agent read 了 1_1_environment.drc, 1_3_variable.drc, ts_auto, 4_5_14_Psub.rules, 4_5_11_DNW.drc, 4_5_64_UTV.rules — 这些不能作 hidden B）。候选 hidden B：4_5_53_Vy.rules / 6_5_OCOL_rules.drc / 4_8_5_SRW_rules.drc / 4_5_45_M1.rules / 4_8_7_CSS_rules.drc（Top 5 文件，trace 中 agent 只统计过未细读）。
4. **r389 DEBT: 1** — 本轮 selection+deepread，0 case。r390 必交付 DrcEnclosureTripleExtract-001。

## 引用

- 原 trace: `1788937019731_ccgt1.messages.json` (jiaqis, hfeg0plg76, 94 msgs, 701KB? — 实际未量, 但 42 tool_uses + 6 user turns)
- 同 user 历史 case: `DrcVsDrmRuleAudit-001` (r319, jiaqis/tro04, physical_verify)
- 同域邻接 case: `DrcDeckCmpGen-001` (r323), `DrcExactWaiver-001` (r321), `DrcBad2gridLshape-001` (r322)
- scan source: `.75:/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv` 行 `172.16.8.175 hfeg0plg09 jiaqis 1788937019731_ccgt1.messages.json 251 drc:1207;calibre:18;.def:8;gdsii:1`
