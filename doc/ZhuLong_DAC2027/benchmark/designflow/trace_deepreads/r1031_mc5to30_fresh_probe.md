# r1031 mc 5-30 fresh pool probe (2026-11-24)

## 背景
r1029 报高-mc(≥30) C-domain fresh 池 effectively exhausted；r1030 用 phys-dominant filter 挖到 g6vwv 1 case。本轮按 r1029 建议 (a) 下沉 mc 5-30 段选料。

## 方法
.75 summary_20261123 上 awk C-domain keywords + mc 5-30 → sort -rn → dedup by session_file → top 80。
本地 anti-join 全 4 shard ledger 并集 (6122 行) → 8 fresh：
hvt59 / 6jzy6 / zcg5s / j36z8 / b089y / ty5vg / wtxsx / acz79

## 逐条深读结论

| sid | user@host | mc | keywords | 结论 | 处置 |
|---|---|---|---|---|---|
| j36z8 | kenwang@hfeg0plg16 | 29 | drc:125;calibre:63 | debug-Q&A：用户问 gvim diff 两个 Calibre DRC .rules 文件时 Gdk-CRITICAL 错误原因+解决；deliverable=纯 prose 解释，check() 无法满足 §4.2 subprocess-on-B + §4.3 结构断言（会退化成 substring grading）；16msgs/46KB | parked |
| 6jzy6 | xinqiaoz@hfeg0plg56 | 30 | pdk:117;drc:12;calibre:9 | 用户要实现第 4 个 checker（calibreDummy.rule 静态检查：GDS_TYPE/suffix/Debug/Hier）；**trace 在用户请求处截断，无 delivered 解决方案**；源 /home/xinqiaoz/PDK_QA/pdkQaSystem/ 对 e0031982 permission-denied（scp Permission denied, find 空），calibreDummy.rule 格式 + qa_workspace data 目录结构不可达 → 无法建准确 ref 解；xinqiaoz 与既有 DummyDeck/DummyDeckMaskDiag/DummyDeckStructDiff 高 dup-risk | parked |
| wtxsx | t0002962@hfeg0plg90 | 28 | pyaether:65;drc:28;aether:27 | env-config：用户问 "check run_pyaether policy valid" + "aether path is X find environment yourself"；调试 agent-policy.json + run_approved_command profile，无 design-flow 交付件 | parked |
| acz79 | t0002962@hfeg0plg90 | 28 | (同 wtxsx) | wtxsx 的 dup（同 user/host，keyword 计数完全一致） | parked |
| ty5vg | steveny@hfeg0pnd001 | 28 | netlist:182;pyaether:54;virtuoso:40;aether:27 | incomplete flow-driving：用户要 export-netlist，但 session 在 agent ask_question 澄清平台处结束，无交付件；17msgs/60KB | parked |
| hvt59 | yohannw@hfeg0pnd001 | 30 | analog:79;pyaether:15;waveview:11 | analog/sim 主导，非 C 域（交 D/B） | 未 claim（跨域） |
| zcg5s | xavierw@hfeg0plg92 | 29 | pex:236;netlist:83;schematic:47 | pex/schematic 主导，非 C 域（交 B/D） | 未 claim（跨域） |
| b089y | alexli@hfeg0plg101 | 28 | netlist:79;pex:6;aether:6 | netlist/sim 主导，非 C 域（交 B/D） | 未 claim（跨域） |

## 结论
mc 5-30 段 C-domain fresh 池本轮挖到的 8 条里：5 条深读后全部 weak（debug-Q&A / env-config / incomplete / source-inaccessible），3 条跨域（analog/pex/netlist 主导，属 B/D）。
**无合格 case 产出**。j36z8/wtxsx/acz79/ty5vg/6jzy6 已 claim+parked，下轮不会再捡。

## 下轮建议
1. 继续下沉 mc 5-15 段（本轮只挖 mc 28-30 的 8 条 fresh，更低 mc 段未探）。
2. 复活 parked 中 source-reachable 的中-mc 候选（如 ukkn7 e0031668 ERC flow rewrite virtuoso→aether，源在 hfhds201 本机可达，mc=1627）。
3. §4.9 anti-hardcode 自查 / test_rationale 断言清单补全（不依赖新候选的产出）。
