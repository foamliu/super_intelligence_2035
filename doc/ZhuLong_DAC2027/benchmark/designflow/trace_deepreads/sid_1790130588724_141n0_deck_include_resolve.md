# 深读笔记 — sid 1790130588724_141n0 (xinqiaoz / hfeg0pkn004, mc=915)

- **session**: `/home/xinqiaoz/.cline/data/sessions/1790130588724_141n0/1790130588724_141n0.messages.json` (1.16MB, 352 msgs)
- **tools 主导** (summary.tsv): 915 calibre → 域 = **physical_verify**（Calibre SVRF DRC deck 依赖解析 + ldr rule 分类 QA）
- **库/case**: `pdkQaSystem/DRC/issues/0922_zhaowei2/base/`（G5_CIP 节点 DRC deck QA case），顶层 deck `calibreDRC_DDR5.rule`

## 用户意图流（关键 user_input）
- idx=0 逐字『阅读 /home/xinqiaoz/PDK_QA/pdkQaSystem/DRC/issues/0922_zhaowei2/base/calibreDRC_DDR5.rule，这个 drc deck 文件中使用很多 INCLUDE，也就是说它引用了其他的 rule 文件。我需要你把它引用的 rule 文件也放到这个 base 目录里面。』 ← **纯需求 A-档 seed 候选**（用户只给目标：把 INCLUDE 引用的 rule 文件复制到 base 目录，未给方法/根因/修复）
- idx=27 详细需求：从 ldr 提取 DEF/SDG DEFINITION/3D definition variable 三类 rule，与 DRC deck 交叉匹配 → 多轮迭代分类（_extract_ldr_rules / _extract_variable_defs / _filter_real_ids / _filter_derived_layers / _classify_remaining）→ 写 README 规范
- idx=333 末轮 = handoff 交接（任务暂停）

## A-档判定 → disqualified → B-档 synthesized
- idx=0 是纯需求 seed，但 agent 的产物 `_copy_includes.py` = **硬编码 SOURCES 列表**（手抄 15 条 INCLUDE 路径），非程序化解析；且真实 deck/被引文件在 `/home/pdk/weizhao/` 与 xinqiaoz 私有 base 目录下，sandbox 无权读取（e0031982 在 10.129.2.13 上 `Permission denied`），无法取真实附件 → A-档 disqualified（无干净可程序化金标准 + 真实资产不可获取）。
- idx=27+ 的 ldr 分类流程强状态依赖（用户逐轮给分类规则，多脚本 + README 迭代），非单一可交付件 → disqualified。
- → **B-档 synthesized**：把 idx=0 的「解析 SVRF deck 的 INCLUDE 依赖链」合成成离线 Python 工具 `include_resolver.py`（程序化解析，agent 本应写出的通用解）。

## 真实 INCLUDE 结构（来自 agent idx=10 硬编码 SOURCES 注释）
顶层 `calibreDRC_DDR5.rule` 的 INCLUDE 链：
- 无条件：`calibre.layer`、`calibreDRC_deflpp.rule`、`calibreDRC_main.rule`、`calibreDRC_singlevia.rule`、`calibreDRC_customer.rule`、`calibreDRC_internal.rule`、`calibreDRC_sealring.rule`
- `#IFDEF LPDRC_CHECK`（**未定义**，referenced but not defined）：`calibreDRC_devicelayer_LP.rule`、`calibreDRC_ports_LP6.rule`、`calibreDRC_voltage_decqa.rule`
- `#IFDEF DDR_CHECK`（**已定义**）：`calibreDRC_devicelayer_DDR.rule`
- `#IFDEF DDR5_CHECK`（**已定义**）：`calibreDRC_ports_DDR5.rule`、`calibreDRC_voltage_drcoa.rule`
- `#IFDEF DDR6_CHECK`（**未定义**，referenced but not defined）：`calibreDRC_ports_DDR6.rule`、`calibreDRC_voltage_dscqa.rule`

agent 把**所有**（含未定义分支）都复制了。正确通用解应：程序化解析 INCLUDE（含 `#DEFINE`/`#IFDEF`/`#IFNDEF`/`#ELSE`/`#ENDIF` 条件块 + 嵌套 include + 相对/绝对路径），按 DEFINE 状态分类 active vs conditional-skipped，检出 missing 与 duplicate，递归求闭包。

## gold（合成的程序化通用解）
`include_resolver.py`（Python3 纯 stdlib，ASCII）：
- CLI: `python3 include_resolver.py --deck <top.rule> --out <report.json>`
- 解析 SVRF：`INCLUDE "path"`/`INCLUDE path`（大小写不敏感，去 `//` 行注释后识别）、`#DEFINE KEY [VALUE]`、`#IFDEF KEY`/`#IFNDEF KEY`/`#ELSE`/`#ENDIF`
- 维护条件栈 + DEFINE 状态（in-file `#DEFINE`，inactive 分支内的 `#DEFINE` 不生效）
- 递归 follow included 文件（active 才下钻；conditional-skipped 不下钻）
- 路径解析：绝对路径 → 相对 tree_root（去前导 `/`）；相对路径 → 相对 including file 的 dir
- 分类：active（含无条件 + 已定义分支）/ conditional_skipped（未定义分支内的 include，不查存在性）/ missing（active 但文件不存在）
- 去重（canonical path），报 duplicates（同文件被多次 active include）
- 输出 JSON：top_deck / defines / resolved[] / conditional_skipped[] / missing[] / duplicates[] / total_* / max_depth

## 难度与独立性
- L1-boundary（离线 SVRF 文本解析，check.py 内嵌 hidden B 目录树，subprocess 真跑候选，判分机无需 live calibre，§4.2 ✓）
- 与既有 physical_verify case 区别：DRConnTiming/DRCTimeStats/DRCSFCompare=DRC log 分析；DummyDeck/DummyMeas/DummyQA=dummy deck 生成诊断；LVSLogFilter/LVSDiag=LVS log/rep；ERCFilter=ERC csv 过滤；本案 = **SVRF deck INCLUDE 依赖闭包解析 + 条件编译分类**，主题/断言独立。
- 关键难度点：①条件编译 #IFDEF 状态求值（active vs conditional）②递归下钻（active 才下钻，conditional 不下钻）③绝对/相对路径解析④missing 检出（active 但不存在）⑤duplicate 去重⑥inactive 分支内 #DEFINE 不生效。

## hidden B 设计
- B = `deck_B/`（结构全不同）：顶层 `topRule.rule`，无条件 include 2 个 + 嵌套 3 层深（a→b→c）+ `#IFDEF AAA`（已定义，active，含 1 include）+ `#IFDEF BBB`（未定义，conditional，含 2 include）+ `#IFNDEF CCC`（CCC 未定义 → active，含 1 include）+ 1 missing active include（路径不在树里）+ 1 duplicate（同一文件被两个不同文件 active include）。
- B2 = `deck_B2/`（cross-input guard，B 的 6-include 子集，重随机化）。
- A 与 B 规模/取值/结构全不同（§4.1 ✓）。
