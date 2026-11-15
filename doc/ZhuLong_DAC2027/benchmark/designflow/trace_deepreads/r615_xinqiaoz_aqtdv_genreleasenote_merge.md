# Deepread — 1794010590146_aqtdv (xinqiaoz @ hfeg0plg56, mc=358)

- session: `1794010590146_aqtdv.messages.json` (1.3MB, 325 msgs, 14 real user_input)
- user: xinqiaoz (pdkQaSystem 开发者，已知 produce-task 作者)
- host: hfeg0plg56 (10.129.x), domain: physical_verify (keywords pdk:1067;drc:253;calibre:50;rtl:40)
- 旧判定: r419 parked "PDK-QA genReleaseNote refactor (merge 3 scripts/emails/excel-sheets, 7-day window, HTML restructure) — handoff-resume continuation, weak EDA affinity"
- 新判定 (2026-11-15 令重审): **可造** — 真实用户意图（报表流水线合并重构），旧"weak EDA affinity"属 B 类误杀口径，按任务初衷合法

## 用户意图演进（user_input 核心）
- UI#1: handoff RESUME（从 HANDOFF_20261107_081442.md 恢复上下文）
- **UI#2**: 保留 3 份脚本原件，在 genReleaseNote 新建子目录放重构后代码
- **UI#3 (核心 produce-task)**: refactored/ 改名 tools/；3 份脚本有公共代码，两思路：① 提公共到单独文件保留 3 份 ② 合成 1 份；测算方案二行数
- **UI#4**: 后续要 3 邮件合并成 1 封、excel 合并成 1 个多 sheet；重新测算
- UI#5: 3 邮件合并后内容太长，想精简
- UI#6: 发信给我看样式
- UI#7: "7 天窗(B) vs 2 个月窗(A)" 是什么概念？
- **UI#8 (口径定案)**: 2 个月不合适，全部改 7 天视窗；网页格式要求：① 总览不要"窗口"tile ② 每域一表（平台作字段，不同颜色区分平台）③ 全量打包/部分更新 保留旧版字体颜色
- **UI#9**: 总览参照旧脚本"各平台更新数汇总"：第一部分汇总表，第二部分更新详情
- UI#10: 参照 genReleaseNote_runset.py 样式
- UI#11: 各平台更新数汇总沿用 runset 的表格样式，不必和详情一样
- UI#12: 第一部分不是深蓝表头
- **UI#13 (真实数据)**: 样式用 v5、内容用 v3：Runset DH2/G4B1/G4B_CIP5/G4C4/G4plus1/G4plus_HBM2/G6_1C2A6/LDDB9/TSI0/V2B4/V3 1=小计35；StarRC cxmtG4B_CIP1/cxmtG4C2/cxmtG5_CIP1/cxmtV2B1/cxmtV3 1=小计6；TechLib DH1/TYA1/cxmt10G5_CIP1/cxmt14SF1/cxmtG4B_CIP1/cxmtG4C2=小计7；合计 48

## agent 产物
本会话产出：结构分析（3 份脚本 Parser×3/Scanner×3 真异构）、方案二测算（~1540 行）、v6 邮件样式定案、交接单 HANDOFF_20261107_100222.md（85 行 7 节）。`tools/` 正式实现列为 next step（本会话未落代码）。

## case 合成（B档 mock-behavioral reframe）
源 workdir `~/PDK_QA/pdkQaSystem` 沙盒不可达 → asset_fidelity=synth。参数化纯 Python `gen_release_note.py <entries.json> <out.html>`（stdlib only）：解析 entries(window_days/entries[domain,platform,new_version,days_since,type,detail]) → 7 天窗过滤 → 产 HTML 报表（各平台更新数汇总：每域一表+平台作列+按平台着色+`<域> 小计`+`合计`；更新详情：窗内每条一条，全量打包红/部分更新绿）→ 确定性输出（排序后字节稳定）。
- 输入 A：真实 Runset/StarRC/TechLib 合计 48（UI#13 原数据）
- 隐藏 B：LVS/DRC/PEX，含超窗 drc_old99(days_since=15) 应排除，小计 LVS10/DRC10/PEX3 合计 23
- 隐藏 B2：ERC/ANTN，含超窗 erc_old77(days_since=20) 应排除，合计 16

## 14 条断言 (a-n)
a zip+py_compile / b B exit0+<html>+<table> / c 汇总段+summary 表 / d 详情段 / e 7天窗(drc_old99不出现,drc_x9出现) / f 各域小计(LVS10/DRC10/PEX3) / g 合计23 / h 平台着色≥2色 / i 全量打包红+部分更新绿 / j 平台作列(<th>含平台) / k 反硬编A(cxmtG5_CIP/G4plus_HBM/LDDB不漏) / l B2反硬编(ant_q2在,drc_x9不漏,合计16) / m 确定性 / n 详情含全窗内平台不含超窗

## 自验
- ref 14/14 PASS ✓
- 3 neg(naive_empty→b / print_expected→e / deleted_core→e)全 FAIL ✓ NEGATIVE_SELFTEST ALL-FAIL-OK ✓
- §4.9 (a)空壳/(b)只print/(c)删核心 三假全 FAIL ✓
- embedded test==disk check.py roundtrip ✓ (jsonl test field 跑 check PASS)
- bool(check)=True ✓；k=14≥8 ✓
- C.jsonl 380→381；mark case ✓（covered 381→382）

## same_trace_group / distinct
`aqtdv-genreleasenote-merge` (cap-1)。新子型 release-note-merge-report（PDK-QA 报表流水线合并重构）。与 RscalcHandoffDocGen-001 (stuck-flow 交接单) distinct：输入=entries.json(平台更新条目表) vs flow_state.json；输出=HTML release-note 报表 vs markdown 交接单。
