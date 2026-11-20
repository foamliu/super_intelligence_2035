# 深读笔记 — sid 1793760774987_u7mv3 (alan3zh @ hfeg0pkn001, mc=324, pg_layout)

- **session**: 174 msgs, ~1.6MB, 多轮用户追问（单主任务: Innovus floorplan log 诊断）
- **user**: alan3zh (NEW — ledger_C 中此前无此 user), host hfeg0pkn001
- **真实文件**: `/home/alan3zh/workspace/test_chip/test_chip_v1/apr/logs/inv_fp.log`（1431 行, 242KB, LSF Job 1079733）
- **工具信号**: innovus:floorplan 主线 + LSF batch 头解析 + make wrapper 逻辑推断

## 用户原话（主任务）

用户在 Innovus 里跑 test_chip_v1 的 APR floorplan，make 报 `innovus floorplan FAILED`，指向 `apr/logs/inv_fp.log`，且 logs 目录里**没有 route 的 log**（说明 fp 这步没过、make 没往下走）。但打开 inv_fp.log 看：

- LSF 头写着 `Successfully completed`
- 结尾有 `INNOVUS FP DONE : hl22_porting_test_chip_v1`

Innovus 自己像是跑完了 —— 跟 make 报的 FAILED **对不上**。用户要搞清这次 fp 到底是什么状况：Innovus 自身成没成 / 报了哪些 ERROR·WARN（按 code 归类计数）/ 各段 Message Summary 累计共多少 warning·error / dominant error 是哪个 / "make FAILED 但 Innovus Successfully completed" 这个矛盾能否从 log 解释清楚。

## 真实日志实证（inv_fp.log, LSF Job 1079733）

### LSF 头
- `Subject: Job 1079733:`，`submitted from host <hfeg0plg76> by user <alan3zh>`
- `executed on host(s) <8*hfednd078>`，`in queue <verilog>`
- `Started at Wed Nov  4 14:08:36 2026` / `Terminated at Wed Nov  4 14:09:44 2026`
- `Run time : 68.0 sec` / `CPU time : 112.18 sec` / `Max Memory : 2283 MB`
- 命令: `innovus -no_gui -files /home/alan3zh/workspace/test_chip/test_chip_v1/apr/innovus_fp.tcl`
- **`Successfully completed`** ← LSF 视角成功

### Innovus 版本
- `Version: v23.32-s091_1, built Tue Jul 30 17:21:26 PDT 2024`

### ERROR codes（按 code 计数, 从 `**ERROR: (CODE-NNNN):` 行）
| code | 计数 | 含义 |
|------|------|------|
| IMPDBTCL-206 | 6 | dbTcl 错（dominant）|
| IMPTCM-48 | 4 | timing constraint 处理 |
| DMMMC-271 | 3 | MMMC 相关 |

### WARN codes（部分, 从 `**WARN: (CODE-NNNN):` 行）
- TECHLIB-302 x3, IMPEXT-2776 x2, IMPEXT-2766 x2, IMPFP-3961 x3, IMPFP-4026 x2, IMPFP-9996 x2, IMPFP-10137 x2, IMPDBTCL-204 x3, IMPDB-1280 x2, IMPPP-354 x2, EMS-27 x2, IMPLF-200 x1, IMPEXT-2773 x1, IMPFP-325 x1, TCLCMD-1461/1013/1142 x1 each, TA-976 x1

### Message Summary（3 行, 有序）
1. `40 warning(s), 3 error(s)` （初始 summary 表）
2. `0 warning(s), 0 error(s)` （某个子段）
3. `8279 warning(s), 13 error(s)` ← **末项 = 本次 run 累计总账**

注意：累计 13 error 与 `**ERROR` 打印行数 6+4+3=13 巧合一致，但**正确取值应取 message_summaries 末项**（Innovus 内部累计口径），而非把打印行数相加（B 用例 18 vs 8+5+3+2=18 也巧合一致，但这是 Innovus 设计上的口径差异，不能依赖）。

### FP DONE 标记
- `INNOVUS FP DONE : hl22_porting_test_chip_v1` ← Innovus 自身认为 fp 完成

## make FAILED vs Innovus Successfully completed 矛盾解释

Innovus LSF `Successfully completed` + `INNOVUS FP DONE` marker 都在 → Innovus 自身**完成了** fp 流程，只是带着 13 个非致命 error（IMPDBTCL-206/IMPTCM-48/DMMMC-271 都不是 FATAL）。make wrapper 比 Innovus 更严：只要 Message Summary 累计 error>0 就判 FAILED（且 logs/ 里无 route log 佐证 make 没继续）。所以 `make_failure_explained = True`（lsf successfully_completed ∧ fp_done ∧ n_errors_total>0）—— make 的 FAILED 是 wrapper 的更严判定，能从 log 解释。

## trace 性质 → B-synthesized

trace 末尾仍**在调试**（用户在追问 log 字段含义、assistant 在解释 error code / Message Summary 口径），**没有用户接受的最终 artifact**（没有 `innovus_fp_log_diag.py` 落地）。因此本 case 取 `track: synthesized`：把用户的真实诊断需求**抽成可复用诊断器**，SUT 写 `innovus_fp_log_diag.py`。

## 案例（EDA-Eval-DesignFlow-InnovusFpLogDiag-001）

- **SUT**: `innovus_fp_log_diag.py`（纯标准库, CLI 1 参 `<fp_log_file>`, JSON 到 stdout）
- **资产 A** = 忠实裁剪的真实 log（同 error codes/计数/version/job/Message Summary）
- **隐藏 B** = 重参数化: Job 2088442, user brianzh, v23.40-s102_3, top_cell `ddr5_phy_top_x32`, error_codes `IMPVL-902x8/IMPFP-4026x5/IMPTRN-1101x3/DMMMC-271x2`, Message Summary `52/4 → 0/0 → 9432w/18e`（杀硬编码 A）
- **隐藏 B_broken** = 崩溃: lsf `Exited`, 无 INNOVUS FP DONE, `IMPSYT-7328` FATAL + `IMPRM-132x5`, verdict=crashed, make_failure_explained=False（A/B 不覆盖的路径）
- **16 条断言 (a)-(p)**: zip 合法+py / py_compile+stdlib / B exit0+JSON / 12 顶层键 / B lsf 字段 / B version / B error_codes / B warn_codes / B message_summaries / B n_errors+n_warnings / B fp_done+top_cell / B dominant / B verdict / B make_failure_explained / 跨输入 A 守卫 / B_broken crashed 哨兵
- **k_check = k_rationale = 16 ≥ 8** 通过
- **3 fake 全 FAIL**（empty_shell / print_expected / core_deleted）
- **2 negative 全 FAIL**（neg_hardcode_A 硬编码 A 值 → B lsf.job_id 错; neg_crash_on_broken 在 B_broken 上 AttributeError → (p) 崩溃哨兵捕获）
- **3-seed 确定性**: ref md5 稳定, check PASS 稳定
