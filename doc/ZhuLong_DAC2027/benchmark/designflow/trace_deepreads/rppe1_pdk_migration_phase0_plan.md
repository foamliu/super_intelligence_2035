# rppe1 深读笔记 — shard C r797 选料

**session**: 1788770427214_rppe1
**user/host**: xinqiaoz @ 10.129.2.14 (hfeg0pkn005)
**mc**: 61, keywords: drc:215;pdk:144;calibre:40;lvs:6;pex:5
**agent**: lead, 12 msgs (6 user / 6 assistant), 2026-09-07
**status**: idle (session ended after planning, no execution)

## 用户真实意图（逐字）

- U#0: "From now on, I will speak to you in English, but you must reply to me in Chinese."
- U#2 (主任务): "Read the file at /home/xinqiaoz/PDK_QA/pdkQaSystem/migration_package/README.md, then follow the instructions in /home/xinqiaoz/PDK_QA/pdkQaSystem/migration_package/MIGRATION_SOP.md to complete the task. Now let's start phase 0. Don't carry out the tasks yet. First, present the plan. I'll confirm it and then proceed with the execution."

## trace-end-gold

助手最终产出 Phase 0 执行计划 markdown（环境现状分析表 + 文件放置方案 + 7 步执行步骤 + 重要说明）。用户未确认执行——trace 在计划呈现后结束。

## 关键事实（来自助手环境检查）

- 代码仓库: /home/xinqiaoz/PDK_QA/pdkQaSystem/ (单一 git 仓库)
- DRC/ 存在含 DrcQa.py（主入口）+ pattern/ + text/ + report/
- common/ 存在；IMCP/ 符号链接 → /apps/imctf/cad/script/SplitMask/splitMask/script/IMCP/
- Calibre 可用: /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibre
- 无 CLAUDE.md / .opencode/ / .claude/
- 无 docs/ / rules/ / business_background/
- 非 DRC 代码目录 LPE/ LVS/ PCELL/ bin/ conf/ tools/（已在 .gitignore）

## Phase 0 SOP 内容（来自 MIGRATION_SOP.md）

Phase 0 = 环境建立：
1. 创建 CLAUDE.md（phase1/INSTRUCTIONS.md → 项目根 CLAUDE.md）
2. 创建 rules/（phase1/rules/ 7 文件）
3. 创建 docs/（phase1/docs/ 全部含 architecture/ conventions/ checkers/ 子目录）
4. 创建 business_background/（phase1/business_background/ 3 文件）
5. 确认环境
6. 确认中文回复规则
7. 产出 PHASE0_REPORT.md

约束：Phase 0 不修改代码、不 git commit。

## 造题判定

- 意图合法性: 2026-11-15 §二 reaudit setup/env-config 合法
- trace-faithful A 档不可行: trace 末尾无用户实际接受结果（计划未确认执行）
- 档 B reframe: 将 Phase 0 规划 reframe 为 Phase 0 setup 执行脚本（用户底层意图=建立 AI 协作基础设施）
- 判分有牙: 14 条断言 subprocess 真跑于隐藏 B，校验文件系统状态
- 子型: pdk-migration-phase0-setup-script
- 对照 r796 PdkDummyScaffold-001 同模式（manifest-driven stdlib 脚本 + 隐藏 B + base64 inline）
