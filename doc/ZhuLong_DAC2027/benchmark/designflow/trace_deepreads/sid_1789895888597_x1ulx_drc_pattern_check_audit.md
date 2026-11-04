# trace_deepread — sid 1789895888597_x1ulx (DrcPatternCheck good/bad split audit)

- **session**: `1789895888597_x1ulx.messages.json` (xinqiaoz @ hfeg0plg76, 990 KB, 171 msgs / 92 user / 79 assistant)
- **match_count**: 330 (440 calibre) → domain **physical_verify**
- **tools used**: read_files×27, run_approved_command×21, editor×20, list_allowed_files×5, search_codebase×2, skills×1
- **real_task_summary**: PDK_QA `DrcPatternCheck.py` (calibre DRC pattern good/bad cell pair check) — RESUME from handoff doc → 审核 `01_drc_pattern_check_good_bad_split.md` 与代码交叉对齐，修复 4 处文档-代码不匹配 + 讨论 os.chdir() ThreadPoolExecutor 竞态 / DRC SUMMARY REPORT 相对路径问题。

## 用户意图（逐字，A-档 seed 候选）
- **UI#1 (msg 0)** 逐字：「请使用 handoff 技能，从以下交接文档恢复上下文并继续之前的工作：/home/xinqiaoz/PDK_QA/pdkQaSystem/.tmp/HANDOFF_drc_pattern_check_legacy.md」= A-档 seed（提出目标=恢复+继续，未给根因/修复；但目标体在 handoff doc 内）。
- UI#2 (msg 16)「完成之后请重新审核一下 01_drc_pattern_check_good_bad_split.md 这篇文档，看看有没有和当前代码不匹配的地方…有的话就修复它」= 给方向（审核文档）。
- UI#5/6/7/8/9/10/11/12/13/14 = 围绕 os.chdir 竞态 / drcSelectCheck / DRC SUMMARY REPORT 相对路径的追问（用户在探究根因，**不进 prompt**，可作 hint）。

## 关键技术内容（gold 块）
- **G1 matchKey 正则**：`[0-9A-Za-z]+_[a-zA-Z]+_[0-9]+_[0-9]+.*`（LAYER_TYPE_NUM_NUM 命名规范）；fallback 配对只对该正则通过的 matchKey 生效（DrcPatternCheck.py L804）。
- **G2 oas 层映射参数化**：error=100/0；OPC01 层（默认 4001/51）=reference；DRCW 层（默认 321/51）=waive mark；OPC02 层（默认 4002/51）=boundary。从 deck `layerMapInfo` 动态提取，缺省回退默认值（L168/L587/L601）。
- **G3 resultTable**：4 列 drc/badCell/goodCell/result；result ∈ {`error`(calibre/e2p64 异常), `pass`, `waive`, fail-复合串 `Good Existing=N, Bad Missing=N, Incomplete=N`}（L261/L1405）。
- **G4 SVRF deck**：`LAYER MAP {opc02Layer} DATATYPE {opc02Dt} 90005` + `OPC02_mark1 {COPY OPC02_mark1_auto}` + `DRC CHECK MAP OPC02_mark1 OASIS {opc02Layer} {opc02Dt}`。
- **G5 drcSelectCheck**（L528-608）：calibre select check 执行；DRC SUMMARY REPORT 路径相对 cwd；新代码注入 `DRC SUMMARY REPORT "{ruleDir}/drc.summary" HIER`。
- **G6 os.chdir() 竞态**：ThreadPoolExecutor 并发跑 drcSelectCheck 时 os.chdir 改的是进程全局 cwd → summary 相对路径漂移；属"脏"问题（不影响最终结果，只影响日志文件）。
- **G7 report 8 计数**：total/pass/waive/fail/error/goodExisting/badMissing/incomplete。
- **G8 文档对齐 4 处修复**：§2.3 层号参数化、§2.6 result 列补 error、§2.7 OPC02 SVRF 参数化、§4.1 Step 2 补 fallback 正则过滤 + 变更记录追加 2026-09-21 条目。

## A-disqualified 判定
gold = 对 live `DrcPatternCheck.py`（/home/xinqiaoz/PDK_QA/pdkQaSystem 内网）的文档对齐 + 代码讨论；依赖 live PDK_QA 仓库 + live calibre。.75 沙盒（e0031982）对 /home/xinqiaoz 不可达 → **A-disqualified → B-档 synthesized L1-boundary**（纯离线 manifest 审计）。

## B-档合成方案
**case id**: `EDA-Eval-DesignFlow-DrcPatCheckAudit-001`
- **候选**: `drc_pattern_check_audit.py`（Python3 标准库 only）读 `drc_pattern_check_manifest.json` → 审计 pair 匹配 / oas 层映射（含默认回退）/ result 分类 / report 计数一致性 / SVRF deck 健壮性 → `audit_report.json`。
- **资产 A**：忠实复刻真实 DrcPatternCheck（M1/M2/M3 spacing+width，5 规则，layerMapInfo 4001/321/4002，clean verdict OK）。
- **隐藏 B**：M4/M5/M6，非默认 opc01/drcw，opc02 缺省→默认 4002/51 但 SVRF 用 4005/51（layer mismatch）；invalid matchKey `weird_cell`；orphan bad M7_orphan_9_9；goodCell NOT_A_CELL；invalid result `unknown_status`；duplicate rule；reportCounts mismatch → verdict HAS_ISSUES。
- **B2**：单 M7 金属，非默认 opc02=4029/61 + 匹配 SVRF，clean → OK（防硬编码 A 的层映射）。
- **B3**：V1/V2 via 层，全合法，计数一致，SVRF 一致 → OK（防 always-FAIL）。
- **check.py 14 条断言 a..n**（独立 oracle 重推 B/B2/B3/A）。
- **与既有 case 正交**：r80 DRCSpecGen（生成 spec→SVRF）/r81 MVValueCmp（值比对）/r84 FillImplantFlowAudit（AST 审查）/r86 DRCReportIpAudit（报告解析）——本案是 **DRC pattern good/bad 配对 + 层映射 + result 分类 + 计数一致性审计**。
