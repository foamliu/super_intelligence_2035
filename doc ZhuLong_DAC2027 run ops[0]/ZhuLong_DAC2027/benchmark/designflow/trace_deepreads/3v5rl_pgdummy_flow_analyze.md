# 深读笔记 · 3v5rl · ellawu · pg_layout horizontal-dummy 插入原理 + 脚本 bug 诊断

## trace 元信息
- session: `1792742868238_3v5rl`（ellawu / 10.129.2.14 hfeg0pkn005 / 2026-10-23..10-29）
- model: deepseek-v4-flash (cxmt-deepseek-flash) / desktop interactive
- match_count: 14（keywords: .gds:351 drc:309 calibre:126 aether:16 techfile:3 ...）
- phys_score=1408，pg_layout heavy（PG dummy fill 流水线编排脚本）
- 终态: `failed_external_process_exit`（stale_session_reconciler 标，非任务失败；助手 msg[10] 已完整交付）
- 附件: `genPGDummy_for_Logic_G5CIP_LP.py` (725 行 / 47KB) — 真实生产 PG/AA dummy 自动生成 GUI 脚本
- prompt（用户轮逐字原文）:
  - U#0: `水平dummy是怎么插入的`
  - U#1: `Boolean_AT4.gds not found, please check Boolean_AT4 DRC!` + 上传 genPGDummy_for_Logic_G5CIP_LP.py

## 用户真实意图（按 2026-11-15 §二 reaudit · explain/debug-Q&A 合法 user 意图）
1. 解释脚本中"水平 dummy"（= AT4 dummy）是如何插入的（**explain 类**）
2. 诊断 `Boolean_AT4.gds not found` 的根因（**debug-Q&A 类**）

两类在旧规则下都会被判为 weak/不可造，按 2026-11-15 §二 recovery 全部恢复为可造 → 合法 case。

## 助手真实交付（trace-end gold · msg[10] text block）
markdown 分析报告，分两部分：

### A. 水平 dummy（AT4 dummy）插入流程详解（5 阶段流水线）
```
Step 1: Stream Out (asOut/strmout → topCell.gds)
Step 2: Boolean_AT4 DRC (复制 calibre_PreAAdum.rule → 改 LAYOUT PATH → calibre -drc → Boolean_AT4.gds → mergeGDS 合并回 topCell.gds)
Step 3: PG Dummy (AA_PG_dummy_fill rule → AA_PG_DUM_Logic.gds) [Run_Type 2/3]
Step 4: STI CMP Fill (AT4_DUMMY2 via calibreSTIcmp.rule → STIcmp.gds + Boolean_HK.gds) [Run_Type 1/3]
Step 5: Merge + Stream In (mergeGDS → strmIn/asIn → auto_pgdm library)
```
**核心**：dummy 图形不是脚本直接画，而是通过编排 Calibre DRC rule deck 的布尔运算自动生成。

### B. `Boolean_AT4.gds not found` 根因 = 4 个脚本 bug
- 🐛 Bug 1（第 246 行 · 运算符优先级）：`if projName == "decqa" or projName == "ddcpc" and Run_Type.get() in [1, 3]:` 缺括号，`and` 优先于 `or`，导致 `decqa` 项目无论 Run_Type 都强制进 Boolean_AT4 流程
- 🐛 Bug 2（第 271 行 · grep 模式不匹配）：grep `"DRC RuleCheck boolean_out COMPLETED"` 与期望标记 `"DRC RuleCheck Boolean_AT4_Out COMPLETED"` 不匹配——`boolean_out` 不是 `boolean_at4_out` 的子串（中间有 `_at4_`），误判 DRC 成功
- 🐛 Bug 3（第 286 行 · 空 GDS 检查逻辑错）：`if at4_size > 0:` 应为 `> 68`（空 GDS 文件头 = 68 字节），导致 68 字节空 GDS 被当作非空去 merge，merge 失败
- 🐛 Bug 4（第 248 行 · 硬编码 rule deck 路径）：`deck_BooleanAT4 = "/apps/imctf/runset/calibre/cxmtG5_CIP/current/common/LP_PreAA/calibre_PreAAdum.rule"` 硬编码 cxmtG5_CIP 工艺，跨工艺不可移植；rule 中 `DRC RESULTS DATABASE` 文件名可能不是 `Boolean_AT4.gds`

## 档 B reframe（A 档 free-text markdown 报告无 ≥8 硬断言牙，承 r810 TvfDeckAnalyzeReport-001 路径）
A 档 gold = free-text markdown 分析报告，check() 无法在 free-text 上做 ≥8 独立可失败断言；print-only stub 打印报告即 PASS（违反 §4.3/§4.9）。

**reframe**：抽离助手在 trace 中真实做的"读 genPGDummy 脚本 + 抽 5 阶段流水线结构 + 检测 4 类 bug"算法核心成纯 stdlib 静态分析器 `pgdummy_flow_analyzer.py`：
- CLI: `python3 pgdummy_flow_analyzer.py <script.py> <out.json>`
- 纯 stdlib (ast/re/json/sys/os)
- 输出 JSON: `stages[]`（5 阶段流水线 + 命中行号）/ `bugs[]`（4 类 bug + 行号 + 证据）/ `hardcoded_paths[]` / `deck_filenames[]` / `summary{}`
- 4 类 bug 检测器：operator_precedence（`or...and` 无括号 + `==` 模式）/ grep_pattern_mismatch（grep pattern_core 非 expected_marker 子串）/ empty_gds_check（`if size > 0:` 近 stat/check_output + .gds）/ hardcoded_deck_path（ast.Constant str 以 `/` 开头 `.rule` 结尾，赋给 `deck*` 变量）

## visible A
真实 `genPGDummy_A.py`（725 行，trace 真实附件逐字保留；无 PII/key/token，仅 EDA 工艺参数+脚本）。ship 完整原文。

## hidden B（合成 ST22 工艺 PG dummy 脚本，结构性反 A）
- 不同 project name: `proj_x`/`proj_y` (反 A `decqa`/`ddcpc`)
- 不同 deck 路径: `/pdk/techXYZ/v2/common/LP_PreAA/calibre_PreHKdum.rule` (反 A `cxmtG5_CIP`/`calibre_PreAAdum.rule`)
- 不同 dummy 层名: `Boolean_HK` (反 A `Boolean_AT4`)
- 不同输出文件: `Boolean_HK.gds` (反 A `Boolean_AT4.gds`)
- 不同 cell: `topMod`/`myLib` (反 A `topCell`/`libName`)
- 不同 grep bug pattern: `boolean_hk_done` vs expected `Boolean_HK_Out` (反 A `boolean_out` vs `Boolean_AT4_Out`)
- 不同 turbo: 8 (反 A 4)
- 5 阶段 + 4 bug 结构同 A，标识符全异 → anti-hardcode

## 断言清单（k=16，与 check.py 一一对应）
1. zip 合法含 pgdummy_flow_analyzer.py
2. py_compile 通过
3. 隐藏 B 运行 exit0 + 合法 JSON
4. JSON 5 顶层键齐全 (stages/bugs/hardcoded_paths/deck_filenames/summary)
5. stages 含全部 5 阶段（stream_out/boolean_predummy_drc/pg_dummy_fill/sti_cmp_fill/merge_stream_in）
6. stages 按 5 阶段顺序排列（line 号递增）
7. bugs 含 operator_precedence 类 + 行号
8. bugs 含 grep_pattern_mismatch 类 + 行号
9. bugs 含 empty_gds_check 类 + 行号
10. bugs 含 hardcoded_deck_path 类 + 行号
11. summary.n_stages_detected == 5
12. summary.n_bug_categories == 4
13. hardcoded_paths 含 B 专属 `/pdk/techXYZ/...calibre_PreHKdum.rule` (反 A `/apps/imctf/...calibre_PreAAdum.rule`)
14. anti-hardcode：JSON 输出不含 A 专属值（cxmtG5_CIP / Boolean_AT4 / decqa / ddcpc / calibre_PreAAdum）
15. 幂等：2x 字节一致 (sort_keys)
16. 错误处理：缺失文件 exit≠0

## 负样本
- `_neg_empty.zip` (README-only) → a 缺 pgdummy_flow_analyze.py 0/16
- `_neg_print_only.zip` (只打印期望 JSON 串不跑分析) → c/d/e/f... 后段 fail
- `_neg_hardcode_a.zip` (硬编码 A 的 5 阶段 + 4 bug) → c 跑 B 后 e/f/g/h/i/j/k/l/m/n/o 全 fail（B 标识符全异）
- `_neg_core_deleted.zip` (删 bug 检测器核心) → e/f/g/h/i/j 全 fail

§4.9 三假 (a)空壳 empty (b)只打印 print_only (c)删核心 core_deleted 全 FAIL。

## 备注
- 本 case 是 2026-11-15 §二 reaudit 后 explain/debug-Q&A 类又一例（承 r810 TvfDeckAnalyzeReport-001），证明 explain 类 trace 可造（档 B reframe 抽离分析算法核心）
- 选料来源: `fresh_true_C_r808.tsv` top-2（r808 4-shard 并集修正后 true fresh 池），r810 MEMORY 已点名 r811 选 3v5rl
- C 域 pg_layout 首例 case（之前 C 多 physical_verify，pg_layout 是 shard C 4 域之一覆盖空白）
