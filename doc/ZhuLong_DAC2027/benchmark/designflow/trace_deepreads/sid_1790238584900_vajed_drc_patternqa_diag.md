# deepread: sid 1790238584900_vajed — pdkQaSystem DRC pattern-QA all-error diagnosis

- **trace**: xinqiaoz @ hfeg0pkn004 (10.129.2.13), session `1790238584900_vajed.messages.json`, mc=307, 133 msgs / 1.28 MB, agent=lead
- **keywords**: pdk:1632; calibre:1628; .gds:533; cmos:46; virtuoso:15; gdsii:11; skipper:6; netlist:1
- **shard/domain**: C / physical_verify

## 用户意图（A-档 seed = USER#0 逐字，提出目标未给根因）
> 使用 issue-handler skill，问题目录是 /home/xinqiaoz/PDK_QA/pdkQaSystem/DRC/issues/0924_yifan。提出人的问题： pattern qa 结果全部是 error，也就是没有正确运行 calibre 或者其他原因。

## follow-up（hint，不进 prompt）
- USER#89: 「先不用创建 README.md，我在 /home/pdk/xinqiaoz/base 下有一份 pdkQa.log 文件，直接帮我分析一下这几条 rule error 的原因。」→ 指向 log 分析
- USER#113: 「以其中一条 rule 为例，log 文件中的哪些行可以作为证据？」→ 指向 per-rule evidence chain

## assistant 工具链（10 步 issue-handler 流程）
1. skills(issue-handler) → list_allowed_files(issue dir) → read_files(config.ini / report / DrcPatternCheck.py / CalibreRunner.py)
2. search_codebase(DrcWithPatternCheck / PatternQaResult / CalibreLayoutHandler) → 理解 error/pass/fail 判定逻辑
3. run_approved_command(profile=shell_generic_pdkqa)：mkdir base/；cp -rL patternqa/* base/；查 drc 路径可访问性；ls work/*/ 子目录、统计 second_check 文件有无
4. **关键发现 A（work 目录）**：drcWithPattern report = errorCount=49, passCount=0, failCount=0, patternNotFoundCount=2065；对比 09-23 aa.gds report = passCount=175, errorCount=0 → 代码逻辑没问题；work/ 下每个 rule 子目录只有第一次 calibre 产物（.oas、AAAAA.drc.results），缺 `_expand.oas` + `second_check.drc.summary` → Round 1 e2p64 展平失败、第二次 calibre 未跑
5. run_approved_command：`calibre -cel bb.gds` → bb.gds 几乎不含可用 pattern cell；`calibre -cel aa.gds` → 有完整 cell 层次
6. run_approved_command：统计 0 字节 .oas → 49 个 rule 的 .oas = 0 字节（第一次 calibre 失败）；19 个非零 .oas 是 09-23 aa.gds + calibreDRC_ac.rule 残留
7. read_files(pdkQa.log @ /home/pdk/xinqiaoz/base/pdkQa.log, 35000+ 行) + grep `error occur in cmd` / `calibre -drc` / `referenced but not defined` / `cell=None`
8. **关键发现 B（log 根因，#112）**：
   - bb.gds cell 名是 pcell 引用格式（`Metal3DEncloseOneSideLand_F_CDNS_7902372385210` 等），match `DrcPatternCheck.py:869` 正则 `.+_CDNS_\d{6,}` → 244 个 cell 全被过滤器剔除 → 2065 patternNotFound（`rule=<R>,cell=None`）
   - 49 条 rule 大小写不敏感匹配到 cell（rule `CELL_BL_L_001_00` ↔ cell `Cell_BL_L_001_00`）但 calibre 报 `ERROR: Cell d_pnw_esd_1 is referenced but not defined.`（d_pnw_esd_1 / d_npw_esd_1 / d_pnw_1 / d_npw）→ 非零退出 → errorRules 分支
   - aa.gds 基线正常 → 非 DrcPatternCheck 代码 bug，是 bb.gds（没完全 flatten + pcell 引用 + 缺子 cell 定义）的问题
9. **#132 per-rule 证据链（CELL_BL_L_001_00）**：
   - line 695 `:703 [START] ThreadPoolExecutor-0_4 处理 rule=CELL_BL_L_001_00`
   - line 718 `:718 rule=CELL_BL_L_001_00,cell=Cell_BL_L_001_00`（大小写不敏感）
   - line 885 `:730 rule=CELL_BL_L_001_00,ruleDir=...work/CELL_BL_L_001_00`
   - calibre `Cell d_pnw_esd_1 is referenced but not defined.`；`:737 error occur in cmd`

## gold / 合成方向
- 依赖 live pdkQa.log（35000+ 行）+ live issue 目录 → A-档 faithful 不可行（log 太大、行号脆弱）→ **B-档 synthesized L1-boundary**：合成紧凑 pdkQa.log（保留真实标记行 :703/:718/:730/:737/:869/:820 + `referenced but not defined` + `filter cell ... (pcell ref)`）+ report.json，交付 `diagnose_drc_patternqa.py`（离线 log+report 分析器，stdlib-only，确定性）
- 隐藏 B/B2：不同 gds 名 / 不同计数 / 不同 pcell cell / 不同未定义子 cell / 不同待查 rule / 不同行号 → 防硬编
- 正交于现有 DRC shard-C case（deck compare/synthesis/pattern-gen/time-stats/manifest/dummy-deck-diag）：本 case = post-run 全-error 根因 log 诊断（pcell-filter + undefined-subcell 机制 + per-rule 证据链行号）

## 产物落库
- case_id: EDA-Eval-DesignFlow-DrcPatQaDiag-001 (physical_verify, B-档 synthesized, L1-boundary)
- k_rationale = k_check = 10（≥8 ✓）；ref PASS + 3 假提交 FAIL + 4 negative 全 FAIL ✓
