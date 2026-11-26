# r618 deepread — xinqiaoz @ hfeg0pkn002, session 1794192534501_fju0e

**trace**: 200 msgs / 114 user turns / 86 assistant turns / 1.3MB
**user**: xinqiaoz (PDK_QA/pdkQaSystem 维护者，已知 produce-task 作者)
**host**: hfeg0pkn002 (10.129.32.?)
**mc**: 400 (drc:6282; pdk:1457; calibre:654; pex:47; lvs:37; .gds:29 — DRC-dominant)
**domain**: physical_verify
**ledger**: r298 parked "idle-handoff" → r618 revive → case (DrcDensityParseJudge-001)

## 真实任务（来自 handoff 文档 HANDOFF_20261109_094000.md）

issue 1026_liping：drcWithPattern 的 `CTB_DenMax_014_00` 这条 density rule（**PRINT 格式**输出）report 报 `Density: Bad Missing=-1, Good Existing=-1` 不合理（liping 反馈）。根因已定论：旧 `parseDensityFirstResult` 不认 PRINT 格式 + 并发 cwd 串扰让 chip 文件落到了别的进程目录。

本会话是 **handoff-continuation**：用户只说了一句"请使用 handoff 技能，从以下交接文档恢复上下文并继续之前的工作：HANDOFF_20261109_094000.md"，agent 自主读取 handoff、验证漂移、继续完成 report 格式收尾（§6 重构 +23 行 → 198 行总），最后写了新 handoff HANDOFF_20261109_114500.md（7 节 71 行）。

## 核心算法（从 DrcPatternCheck.py L82-188 逐字提取，gold fix）

### isDensityRule (L82-90)
按 `_` 拆分 rule 名（大写），从右往左找 `DEN/DENMIN/DENMAX` token 且其后紧跟纯数字 token。
- `CTB_DenMax_014_00` → True；`CTB_S_005_02` → False

### parseDensityFirstResult (L92-162)
按 results 段分流：
- **PRINT** (`DENSITY_PRINT_FILES` 段)：跳过 timestamp 头行（以数字开头），剩下的非空行是输出文件名；对每个文件名在 `cellDir` 下找 chip 文件，数非空行求和。声明文件全缺失且 total==0 → -1；至少一个存在 → 返回行数和。段内无文件名 → 0。
- **RDB**（无 PRINT 段）：扫描全文件找含 `.chip` 的行，取最后一个 token 转 int；找不到 → -1。
- 文件不存在 → -1。

### judgeDensityResult (L165-188) 三态
- bad 或 good 为 None/-1 → `error`（状态未知）
- good>0 → `fail`（good pattern 误触发）
- bad==0 → `fail`（漏检）
- bad>0 且 good==0 → `pass`

### report 格式（用户主动要求）
-1 全部归 errorCount，表格不显示 error 行，另加 `error(n):` 名单节。

## B档 mock-behavioral reframe

源 workdir `~/PDK_QA/pdkQaSystem` 沙盒不可达 → asset_fidelity=synth。把"calibre DRC density rule 解析+判定+报告"重构为纯 Python（stdlib only）模块 `drc_density_check.py`，4 个函数：
1. `is_density_rule(rule_name) -> bool`
2. `parse_density_result(results_path, cell_dir="") -> int`
3. `judge_density_result(bad, good) -> str`
4. `format_density_report({rule: (bad,good)}) -> str`（error 排除出 pass/fail + error(n) 节 + 确定性排序）

输入A（示例）：PRINT bad(6行)/good(0行)/RDB bad(3)/missing-chip/rule_list(7 names)
隐藏B（不同规模/取值）：PRINT bad2(4行 SVRF_88)/good2(0)/RDB fail(5)/RDB good(0)/missing-file/rule_list_B(7 names 不同)

## case: DrcDensityParseJudge-001
- **k=14 a-n**：结构1(a:zip+py_compile+4函数) + is_density_rule1(b:7规则) + parse6(c-h:PRINT bad2/good2/RDB fail/good/missing-file/missing-chip) + judge5(i-m:pass/fail-good/fail-missed/error-1/error-None) + format1(n:error排除+error(3)节+total+确定性)
- 自验：ref 14/14 PASS ✓；3 neg(naive_empty/print_expected/deleted_core)全FAIL ✓；§4.9三假FAIL ✓；embedded test==disk roundtrip ✓；bool(check)=True ✓；k=14≥8 ✓
- C.jsonl 382→383；mark case ✓（pv 167→168）
- same_trace_group: fju0e-drc-density-parse-judge (cap-1)
- 新子型：drc-density-rule-parse-judge（density rule PRINT/RDB 解析 + 三态判定 + error-section 报告）
