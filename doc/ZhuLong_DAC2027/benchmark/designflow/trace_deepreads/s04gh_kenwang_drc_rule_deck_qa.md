# Deepread — 1794900596465_s04gh (kenwang @ hfeg0pkn004) — Calibre DRC deck rule QA

## meta
- session: `1794900596465_s04gh.messages.json` · user `kenwang` · host `hfeg0pkn004` (10.129.2.13) · mc=58
- fetched: r844 via eda_flow ssh .75→hfeg0pkn004 scp 524KB / 60 msgs / 5 user turns
- domain: **physical_verify** (Calibre SVRF DRC rule deck QA — `drc:1122; calibre:791`)
- model: glm-5.3-flash, cwd `/home/kenwang`
- track: **B-synthesized** (A-档 gold = prose QA report，free-text 无 ≥8 硬断言牙；reframe 为脚本化 lint 报告)

## 用户意图（逐字原文）
**U#1（唯一真实需求轮，干净 A-档 seed）**:
```
[drc-rule-dev] 我更新了一些文件 路径 /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/updateCode/v01/Rev14_S1_1115/ ，更新的rule name在 update_log 文件中记录，其中 ARH 指全部rule 的更新，请帮我QA 一下，是否存在问题，重要检查语法及数值是否正确，参考路径文件 /rundata/lacaa/V0/workdir/kenwang/Calibre_DRC/updateCode/v01/Rev13_S12_1030/V05_coding_rebuild
```
真实意图 = **对自研 Calibre DRC deck 一批更新（Rev14_S1_1115）做 QA**：以 Rev13_S12_1030/V05_coding_rebuild 为参考，按 update_log 列出的更新 rule 名（含 ARH=全部 rule）逐条检查 **语法 + 数值** 是否正确。

**U#2/U#3** = "go on"（agent 编辑器反复丢 path 参数）。

**U#4（用户补规则，hint 不进 prompt）**：
> 如果是 PRL>0 um, 用命令 OPPOSITE 即可, 不需要 PROJ >0, 如果是 > 比0 大的数值, 需要用命令 PROJ

**U#5（同上）**：
> go on 如果是 PRL> 负值, 则 需要增加命令 OPPOSITE EXTEND value

→ 用户把内部 PRL/OPPOSITE/PROJ/EXTEND 命令使用规约补全，作为 QA 的判定依据。这两轮是规则补全，不是提出新需求，按 A-档规则不进 prompt，作为 check.py 的判定逻辑嵌入。

## assistant 工具链 + 关键产物
1. skills (drc-rule-dev) → list_allowed_files × 2 → read_files update_log
2. 解析 update_log → 12 条更新项：DBC_H180_CM1A_W_5、DBC_H180_CM1B_S_3_2、AA_R_14、AA_R_31、AMN_L_2_1、ARV_R_5、ARV_R_9、ARH（全部 rule）、MGC_A_1、SDB_S_4、SDB_L_3、SDB_R_13
3. 文件映射：7 个 .ev 文件 + 1 个 global layer 文件
4. 写 diff 脚本（python-runner → shell-runner 切换因 locale）对比新旧 .ev 提取变更 rule 块
5. 6 类待验证问题清单：未定义层引用 / 新增层引用 / TOUCH INSIDE EDGE 语法 / PRECISION 换算 / include 顺序 / 顶层同步
6. 应用 PRL/OPPOSITE/PROJ/EXTEND 规约做 command-usage audit

## gold 产物
- markdown QA 报告（问题清单 + 修复建议），具体值依赖 /rundata 真实 deck（受限不可读，e0031982 ssh 实证 Permission denied）
- 7 个 .ev 文件 diff 摘要 + 中间证据文件

## case 合成（DrcDeckRuleQa-001，档 B reframe）
真实 /rundata deck 不可达（权限）→ **合成 SVRF deck A/B 镜像 trace 模式**（rule 命名风格 / update_log / .ev 结构 / PRL 命令规约 全部忠实重建）。

**A 资产**：
- `deck_A_old.ev`（参考 Rev13）+ `deck_A_new.ev`（更新 Rev14，含 seeded issues）+ `update_log_A.txt`（12 条更新项）
- seeded issues：未定义层引用 / 数值不一致 / PRL 命令使用违规（PRL>0 用 PROJ、PRL<负值 未 EXTEND）/ 语法（不平衡 brace）

**隐藏 B**：不同 rule 名 / 不同 PRL 值 / 不同 seeded errors，防硬编码 A 答案。

**candidate**：`drc_deck_rule_qa.py <deck_old> <deck_new> <update_log> [-o out.json]`
- 解析 .ev rule 块（`<RULE_NAME> { ... }` 嵌套 brace）
- per_rule_diff：仅对 update_log 列出的 rule 计算 added/removed/modified + 变更点
- syntax_issues：不平衡 brace / 未定义层引用（@ 层引用前未 DRC CHECK TEXT 或 LAYER 定义）
- numerical_issues：description 数值 vs 代码数值不一致 / PRECISION 换算错误
- command_usage_issues：按 PRL 命令规约 audit（PRL>0 → OPPOSITE；PRL>非零正值 → PROJ；PRL<负值 → OPPOSITE EXTEND value）
- 输出结构化 JSON

**check.py** k_check=14（a-n），subprocess 真跑候选 on B，断言 14 条独立条件；3-seed 确定性 + missing-path 非零退出 + anti-hardcode A。

## 意图审计
**keep**：kenwang 真实意图（QA 自研 DRC deck 更新的语法 + 数值正确性）完全保留；reframe 把「读 deck→diff→QA→写报告」抽离成纯 stdlib lint 脚本是 grounding 非加难（free-text QA 报告无 ≥8 硬断言牙，脚本化 JSON 输出可逐项断言）。
2026-11-15 reaudit 后 analysis-Q&A / flow-driving / setup 类全部合法 —— 本案 = physical_verify deck-rule-QA analysis 合法第八例。

## 访问方式
- hfeg0pkn004 (10.129.2.13) e0031982 免密 OK
- /home/kenwang/.cline/data/sessions/<sid>/<sid>.messages.json 子目录结构
- /rundata/lacaa/... 真实 deck e0031982 不可读（Permission denied）
