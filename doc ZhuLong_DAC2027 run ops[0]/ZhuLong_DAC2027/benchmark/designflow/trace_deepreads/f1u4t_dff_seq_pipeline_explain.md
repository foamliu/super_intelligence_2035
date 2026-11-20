# deepread — f1u4t (chentong@hfeg0plg76, mc13, spice_sim)

- session_file: `1793350875865_f1u4t.messages.json`
- host: hfeg0plg76 = 10.129.8.124 (chentong)
- shard: B (spice_sim)
- reaudit verdict: 可造 (explain/介绍 Q&A)
- revival: r689 #68 → case `EDA-Eval-DesignFlow-DffSeqTestPipelineExplain-001`
- trace path on host: `/home/chentong/.cline/data/sessions/1793350875865_f1u4t/1793350875865_f1u4t.messages.json`
- scp 已落到 .75 workdir `f1u4t.json`

## 用户真实意图（3 轮，A 档选轮 ✓）

1. 把 7 个脚本作为附件丢进会话，原话「依次读取这些脚本，这是仿真时序电路的 给我讲解」。
2. 追问「需要再详细认真讲解，用大白话」。
3. 追问「这四种功能类型的测试，是否可以覆盖时序电路」。

3 轮都是「求解释」型，无 produce-task，旧规则判为不可造；reaudit 改判可造 —— 把 explain-Q&A 造为「写脚本解析 pipeline → 结构化 JSON 报告」，保留真实用户意图。

## 真实 pipeline（A 输入）

7 个脚本，全部从 trace user[0] file block 完整提取（~25KB）：

| 脚本 | 角色 | 关键 token |
|---|---|---|
| 2_DFF_Truth_table_classify_cells_cdl.py | CDL 单元分类器 | `if 'DF' not in cell_name.upper()` filter；output pins Z/ZN/CO/Q/QN；ignored VDD/VSS/VDD!/VSS!/NEG/POS；PININFO 验证；VDD/VSS 必须 B；输出 `DFF_pin_statistics.txt` |
| 3_DFF_Truth_table_hspice.py | HSPICE 输入生成 | `time_points = [0.45, 0.5625, 0.6875, 0.8125, 0.9375]`；glob 含 'DF' 的 .cdl；输出 `DFF_Hspice_inputs.txt` |
| 4_DFF_Hold_sim.sp | Hold deck | 1 .alter；V5 D / V6 DA 等 |
| 4_DFF_Reset_sim.sp | Reset deck | 1 .alter；V2 C 等 |
| 4_DFF_Scan_sim.sp | Scan deck | 1 .alter；V11 SE / V12 SI |
| 4_DFF_Trigger_sim.sp | Trigger deck | 2 .alter (Trigger + EN)；V5 D / V6 DA 等 |
| 6_DFF_Trigger.py | Trigger 分析 | get_edge_type: `0->1` 异步触发 / `2->3` 上升沿 / `1->2` 下降沿 / else 未知；无变化 → 无触发；输出 `Trigger_DFF.txt` |

## 造法（cross-input guard + A-leak + B-grounding）

**hidden B** = 平行 LAT (latch) pipeline，结构同 A 但参数不同：

| 维度 | A (DFF) | B (LAT) |
|---|---|---|
| cell filter | DF | LAT |
| time_points | [0.45,0.5625,0.6875,0.8125,0.9375] | [0.3,0.45,0.6,0.75,0.9] |
| sim types | Hold/Reset/Scan/Trigger | Setup/Recovery/Scan/Power |
| edge rising | 2->3 | 1->2 |
| edge falling | 1->2 | 3->4 |
| edge async | 0->1 | 0->1 |
| 输出文件 | DFF_pin_statistics / DFF_Hspice_inputs / Trigger_DFF | LAT_pin_statistics / LAT_Hspice_inputs / LAT_Trigger |

check.py 独立 oracle 解析 B_scripts 得期望值，跑 3 次提交脚本，验 sha256 一致 + 18 条断言 (a0–a17)。10 个 A 专属 token (DFF_Hspice_inputs / Trigger_DFF / 0.5625 / Hold_sim 等) 任一出现即判 fail (硬编码 A guard)。7 个 B 专属 token 至少 4 个出现 (B-grounding)。

## 4 个 negative stub 全部 FAIL ✓

- stub_empty.py → a5 missing top-level keys
- stub_print_only.py → a3_run0 no report
- stub_hardcode_a.py → a6 missing sim decks (A 文件名不在 B pipeline_order)
- stub_delete_core.py → a6 missing sim decks

## 自验

- REF_CHECK_RESULT: PASS（reference_solution/dff_pipeline_explain.py 在 .75 + 本地均过）
- NEGATIVE_SELFTEST: ALL FAIL OK
- 确定性: 3 次重跑 sha256 一致

## 落盘

- EDA-Flow-Bench `EDA-Eval-DesignFlow_B.jsonl` 第 388 行 (r689)
- assets/EDA-Eval-DesignFlow-DffSeqTestPipelineExplain-001/{scripts/, hidden/B_scripts/, requirements.json, scenario.txt, task_brief.md, hidden/hidden_manifest.json}
- reference/EDA-Eval-DesignFlow-DffSeqTestPipelineExplain-001/{check.py, negative_selftest.py, negative/, reference_solution/dff_pipeline_explain.py}
- ledger: `trace_ledger_B.tsv` f1u4t → case
