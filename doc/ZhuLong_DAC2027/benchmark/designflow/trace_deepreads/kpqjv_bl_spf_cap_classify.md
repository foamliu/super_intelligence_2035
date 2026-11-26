# trace deepread: 1794294098670_kpqjv — BlSpfCapClassify-001

## 元数据
- session_id: `1794294098670_kpqjv`
- user/host: mhyu@hfeg0plg49
- mc: 0 (本 sid 来自 11-05 rescan 11-11 07:15 一轮的 plg 主机扫，非历史 mc 排序池；mc 通道未覆盖此 sid)
- size: ~single-round produce-task (clean)
- shard: B (characterization)
- status: claimed r997 → case `EDA-Eval-DesignFlow-BlSpfCapClassify-001`

## 11-05 rescan 出处
- 扫描主机：12 plg spice-active 候选 (hfeg0plg49/100/102/20/93/07/78/103/101/06/99/74)
- 扫描窗口：mtime >= 2026-11-10 00:00
- 扫描结果：283 sessions / 207 unique sids / 73 un-ledgered (vs ledger_B 996 sids)
- kpqjv 来自 hfeg0plg49，未被旧池 ledger 覆盖 → rescan 新发现

## 任务真实意图（逐字 user turn）
> 目前在/proj/x0s0f/V0/ver/pex/mhyu目录下有BL_routing_E1、BL_routing_E1_case2_t04、BL_routing_E2...六种BL routing的结果...创建routing_analysis文件夹...复制BL_routing_cap.py、spf_bl_extract_fixed.py这两个数据处理脚本...使用python3 spf_bl_extract_fixed.py BL_routing_E1.spf.TYP_-40_RCC --range 0-71 --output BL_routing.spf_BL_capacitance_classified.csv处理一遍数据结果...

真实意图：对 BL routing 的 StarRC SPF 提寄生输出做"按 BL 索引范围提取并分类寄生电容"后处理，分类对地/耦合/总计，输出 CSV。属于 characterization 后端特征化脚本工程。

## B-synthesized 合规性
- 单轮 produce-task，无 debug/无根因修复 → L1
- 用户名 mhyu 用原始（不 hash），仅 mask 路径中的非必要 token；trace_source 字段忠实记录 user/host/session_file/match_count/real_task_summary
- 重建为 synthesized L1：保留真实 CLI 接口 (`<spf> --range <start-end> --output <csv>`) 与真实目录意图，资产为脱敏重建（sample.spf 仅含 16 BL，真实为 72 BL）
- 为何 synthesized 而非 faithful：原 trace 仅 1 个 user turn + assistant 复制脚本即终止，无实质多步工具调用可锚定 A-faithful 行为序列；为可判分性重建为 B-synthesized L1，保留真实任务语义

## A 资产重建
- sample.spf (16 BL: BL0..BL15 + /BL0..//BL15 + VDD/VSS/WL0..WL7 等)，StarRC SPF 1.5 格式
- config.json: range "0-15"，5 列输出
- example_output_A.csv: 对 sample.spf 跑 --range 0-15 的期望 CSV (前若干行)
- task_brief.md: 交付接口说明

## 隐藏 B 合成（结构性对立于 A）
- hidden_b1.spf: 24 BL (BL0..BL23 + /BL0..//BL23)，比 A 多 8 根 BL；ground/coupling 数值与 A 不同 → 检验 candidate 是否真解析 SPF 而非硬编码 A 真值
- hidden_b2.spf: 12 BL (BL0..BL11)，且 BL0 ground 值与 b1 BL0 ground 差 >0.1 pF → 断言 ⑪ 反硬编码
- B1 跑 `--range 0-23` (48 ground rows = 24 BL + 24 /BL)；B2 跑 `--range 0-11` (24 ground rows)，断言 ⑫ 验证 range 被遵守

## 12 条断言（k_rationale = k_check = 12 ≥ 8 ✓）
① zip 内含且仅含 1 个 .py ② py_compile 通过 ③ B1 CLI exit 0 ④ B1 CSV 非空 ⑤ CSV 表头正确 ⑥ B1 有 48 ground 行 ⑦ B1 BL0 ground 容差 ±1e-3 ⑧ B1 BL0->/BL0 coupling 容差 ±1e-3 ⑨ B1 total = ground + sum(coupling) (BL0//BL0/BL5//BL5) ⑩ 无负值 ⑪ 反硬编码 B2 BL0 ground ≠ B1 (diff >0.1) ⑫ B2 仅含 BL 0-11

## 自验证
- ref PASS: 12/12 ✓ (`python3 check.py reference_submit.zip` → True)
- 6 negatives ALL FAIL ✓ (naive_empty / only_print / empty_shell / hardcoded_a / ref_core_deleted / no_total)
- §4.9 three fakes FAIL ✓

## 交付
- append 到 `EDA-Eval-DesignFlow_B.jsonl` (line 254)
- ledger_B: kpqjv marked `case` w/ case-id
- commit: EDA-Flow-Bench (master) + super_intelligence_2035 (main) `designflow shard B #N: BlSpfCapClassify-001`
