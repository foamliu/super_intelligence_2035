# r614 deepread — z9yjw rscalc-handoff-doc (e0014566@hfeg0plg58)

- **session**: `1790133815976_z9yjw.messages.json` (e0014566 @ hfeg0plg58 / 10.129.35.82, mc=430)
- **domain**: layout_virtuoso (keywords: virtuoso:2204 drc:746 cadence:384 cellview:200 .gds:196 dbopencellviewbytype:186 calibre:182)
- **size**: 540 msgs / 27 real user_inputs / 2.7MB
- **ledger**: was parked (r47, note "UI hello/runme 太薄元任务") → 2026-11-15 intent-audit reaudited 可造 (thin/doc-gen legal under new rules) → r614 revive → case

## 用户真实意图（UI#19 = 核心 produce-task）

UI#1 是用户自己写的"新开对话开工指令"（继续 BCenterCA 降阻迭代 RsCalc→AutoVia→PowerFill 流，RsCalc baseline 已跑通，AutoVia 卡住）。UI#3-18 是环境/license/权限调试对话（CDS_LIC_FILE 空、PROJ_NAME/Ver 空、目录权限、主机选择）。UI#19 是**核心 produce-task**：

> "请你把这段『RsCalc baseline 已完成、AutoVia 经历两个阻塞点后跑通』的会话记录整理成一份**可追溯、可复现、可自动化、可交接的技术备份 + 续跑交接单**。重点：AutoVia 这一步经历了哪些阻塞点、每个卡在哪、怎么修的、AutoVia 最后跑到哪（via cell/merged cell/运行时长/在哪台机上跑通）、新会话从哪里接着跑（RsCalc 复测 → PowerFill 衔接的配置改动）、收敛判据。不要展开 PowerFill 详细执行，但结尾说明 RsCalc 复测与 PowerFill 衔接点。"

UI#20-27 是后续 Q&A/summary（"AutoVia 进展如何"/"帮我总结对话"）—— thin，不取。

## assistant 真实交付（msg 526，gold 参考）

15977 字结构化 markdown 交接单，章节：
1. 执行摘要（cell/4 网列表/22 RNODE/vss! 5.24~21.49Ω/2 个阻塞点/merged BCenterCA_via1/下一步）
2. 范围与目标（衔接点 common.config cellName BCenterCA→BCenterCA_via1 / 收敛 R_i(p)<=R_0(p)*(1-0.3)）
3. 环境与路径清单（**三套**环境表：hfeg0plg55 RHEL6 终端 / hfeg0pkn005 RHEL8 AI shell license 空 / hfhds201 RHEL7 历史成功主机）
4. 卡点与修复
   - B1 license 假象：CDS_LIC_FILE 空 → DB-320001 checkout 111 → 改到 hfeg0plg55/hfhds201 跑
   - B2 CXMT 触发器 CXMTutDuplicateCellChk 读 PROJ_NAME/Ver 空 → strcat(nil) → ddCreateObj cancelled → 启动补 PROJ_NAME=train Ver=V0_Austin 修复
5. AutoVia 结果（run_host hfhds201 / 4 via cell BCenterCA_V2AV1AV5V4V3V2V1CT_{net}_VIA / merged BCenterCA_via1 / 15.6 min）
6. 下一步（RsCalc 复测 + PowerFill 衔接配置改动）

关键事实密度高：lib=auto_qx_case1, cell=BCenterCA, 4 网 vcc!/vss!/vdd1!/vbn!, 22 RNODE, vss! 5.24~21.49Ω, 两阻塞点 cause+fix, 三主机, via 命名 pattern, merged cell, 15.6 min, targetReduction=0.3。

## B档 mock-behavioral reframe（承 r602-r613 模式）

源 workdir 沙盒不可达 → asset_fidelity=synth。把"从会话记录产交接单"参数化为纯 Python `rscalc_handoff_doc_gen.py <flow_state.json> <out.md>`（stdlib only）：解析结构化 flow_state（metadata/baseline_rscalc/blockers/environments/autovia/next_step）→ 产 ≥6 ## 章节交接单 markdown，内容从输入提取（cell/net/blocker cause&fix/hostnames/via 命名/merged cell/运行时长/收敛判据/target_reduction），不硬编码。

- **输入 A**（可见）：BCenterCA 流（真实 trace 还原）
- **隐藏 B**：ACenterCA 流（dbOpenCellViewByType OA 权限 + layer.map METAL6 阻塞，hfeg0plg99 跑通，via ACenterCA_V3AV2AV6V5V4V3V2V1CT，merged ACenterCA_via2，22.4 min，target 0.35）
- **隐藏 B2**：XCenterCA 流（display.drf VIA1 阻塞，hfeg0plg77，merged XCenterCA_via1，2 网）

## 判分（16 条 a-p，k=16≥8）

a:zip+py_compile / b:B exit0+#H1 / c:B lib / d:B cell / e:B 全部 4 网名 / f:B blocker cause dbOpenCellViewByType / g:B fix cds.lib / h:B run_host / i:B via prefix / j:B merged_cell / k:B run_time 22.4 / l:≥6 ## / m:B target 0.35 / n:反硬编 A(不含 BCenterCA/PROJ_NAME/hfhds201) / o:B2 反硬编(含 XCenterCA+hfeg0plg77+XCenterCA_via1 且不含 A/B cell) / p:确定性两跑字节一致

## 自验

- ref 16/16 PASS ✓
- 3 neg（naive_empty/print_expected/deleted_core）全 FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 (a)(b)(c) 三假全 FAIL ✓
- embedded test == disk check.py roundtrip ✓
- B 输出 0 处 A-leak（BCenterCA/PROJ_NAME/hfhds201 全无）✓，6 个 ## ✓
- bool(check)=True ✓

## 同 trace group / distinctness

- **same_trace_group `z9yjw-rscalc-handoff-doc`** (cap-1)
- **distinct vs RscalcFlowDocGen-001 (r599)**：RscalcFlowDocGen 输入=prompt_flow.md+configs（流程说明文档），输出=流程描述 doc；本 case 输入=flow_state.json（卡点/修复/环境表/autovia 结果），输出=续跑交接单（执行摘要/环境/卡点修复/AutoVia 结果/下一步）。不同子型。
- 新子型 **rscalc-handoff-doc-gen**（stuck-flow 状态交接单），C L1-portable-script 形态空间第 13 子型（承 r602 extraction / r603 diagnostic / r604 planner / r605 compute / r606 config-parser-extend / r607 hierarchical-resolve / r608 constraint-pattern-gen / r609 requirements-doc-gen / r610 corner-space-pattern-gen / r611 ssh-profile-builder / r612 virtual-not-layer-gen / r613 drc-pcell-batch-convert → r614 rscalc-handoff-doc-gen）
