# Deep-read: 1789384598319_agzjb — DRC CWD race evidence scan

- session_file: `1789384598319_agzjb.messages.json`
- user/host: xinqiaoz @ 10.129.2.11
- match_count: 413 (drc:8178 / calibre:1470 / pdk:1160 / lvs:156, tool_total=11148)
- domain: physical_verify
- 造出 case: `EDA-Eval-DesignFlow-DrcCwdRaceEvidence-001` (2026-11-17 r723)

## Trace 概要（179 msgs, 3 user phases）

### Phase 1（U#1–U#112）：DrcPatternCheck.py 代码评审 + 修复方案讨论
- 用户把 `DRC/pattern/DrcPatternCheck.py` 全文贴进来，问并发跑 calibre drc 时
  出现的 `Density: Bad Missing=-1, Good Existing=-1` 怪值根因。
- 助手逐函数分析：`parseDensityFirstResult` 不认 PRINT 格式只认 RDB（-1 根因）；
  `drcWithPatternCheck` 里每个 cell 用 `os.chdir(cellDir)` 切 process-global CWD，
  多线程并发时 CWD 互相抢，导致 SR_V2_ENC_01 的 calibre 在 `CWD=AM_F_01/bad` 下
  启动，其 `drc.summary`（相对路径）写进了 AM_F_01/bad 目录。
- 这阶段是 **代码级推断**，不是 issue 目录证据。

### Phase 2（U#113）：issue 目录层面的 CWD 竞争证据（本 case 的 reframe 目标）
- U#113 明确要求：**不要从代码推断，从 issue 目录层面把 CWD 竞争证据扫出来**。
- 助手遍历 `work/<cell>/{good,bad}/drc.summary`，解析每个文件的
  `Rule File Pathname` / `Layout Primary Cell` / `Current Directory` /
  `DRC Results Database` 四个头字段。
- 关键发现：`work/AM_F_01/bad/drc.summary` 的三个字段全是 SR_V2_ENC_01 的
  （Rule File Pathname = `.../SR_V2_ENC_01.drc`，Layout Primary Cell =
  `SR_V2_ENC_01_F`，DRC Results Database 指向 SR_V2_ENC_01 的 rdb）——
  即路径在 AM_F_01 下、内容跑的却是 SR_V2_ENC_01 的 deck，铁证 CWD 串扰。

### Phase 3（U#114–U#179）：修复方案落地 + 后续 density rule 处理
- 讨论 `os.chdir` 改 subprocess cwd 参数、PRINT 格式解析、density rule 三态判定。
- 这阶段回到代码修复，与本 case 无关。

## Case reframe：`drc-cwd-race-evidence`

把 U#113 的"issue 目录层面 CWD 竞争证据扫描"抽成 mock-behavioral 纯 stdlib 任务：

- **输入**：`<issue_dir>/work/<cellName>/{good,bad}/drc.summary`（A demo 4 cells
  × 2 = 8 子目录；B 隐藏 5 cells × 2 = 10 子目录，cell 名/数量/cross 模式全异 A）。
- **任务**：遍历每个 `drc.summary`，解析 4 个头字段，取 `Rule File Pathname`
  basename 去后缀得 `reported_cell`，按 `reported_cell` vs 目录 `<cellName>`
  分类 `missing` / `matches` / `cross_contaminated`，输出 JSON 报告（overview
  计数 + per_cell 明细 + verdict）。
- **反硬编码**：B 与 A 完全 disjoint（cell 名、数量、cross 模式都不同）；check.py
  condition o 对隐藏 A 参考目录再跑一遍 solver，验证得 total_cells=4 /
  cross_contaminated=1 / summaries_missing=3（硬编码 B 值的 solver 在此失败）。

## 与已覆盖 C domain case 的区分

- `DrcDensityParseJudge-001`：DRC **results** 文件解析 + density rule 三态判定
  （PRINT/RDB 格式分流、chip 行数计数、judge 三态）。本 case 解析的是
  **drc.summary 头信息**（Rule File Pathname / Layout Cell / Results DB），
  做 **CWD 竞争证据分类**，不碰 density 计数也不碰 results 格式。
- `DrcDeckOptimize` 类：DRC rule deck 修改优化。本 case 不改 deck，只读 summary。
- 无重复：本 case 的 `cross_contaminated` 分类（reported_cell ≠ dir cell）是
  本 trace 独有的判定维度，其他 C case 没有这个概念。

## check.py 16 条断言 a-p

①zip含solve.py ②py_compile ③B运行+合法JSON+三顶层键 ④total_cells=5
⑤total_dirs=10 ⑥summaries_found=8 ⑦summaries_missing=2 ⑧matches=6
⑨cross_contaminated=2 ⑩per_cell长度+shape+排序 ⑪cross条目reported_cell≠cell+
evidence_file非空+总数=evidence_count ⑫cwd_race_detected=True
⑬affected_cells=[SR_S_01,VIA_M2_M3] ⑭evidence_count=2 ⑮反硬编码A参考目录
(4/1/3) ⑯确定性md5

3 negative stubs：naive_empty→c, print_expected(硬编码A值)→d, deleted_core
(overview cross计数被删,per_cell正确)→i。

## 验证

- reference solve.py on B: 16/16 PASS
- reference solve.py on A_ref: total_cells=4, cross_contaminated=1,
  summaries_missing=3 ✓（condition o 通过）
- negative selftest: 3/3 distinct first_fail (c/d/i) ✓
- §4.9 degenerate submissions: empty/print-expected/delete-core 全 FAIL ✓
- round-trip: 从 C.jsonl 提取 test 字段 → check.py → 对 reference submit.zip
  PASS ✓
