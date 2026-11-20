# 2r0by — deck-grounded parameter-sweep-extraction Q&A

## trace source
- session: `1793340943310_2r0by` (ghyang@10.129.8.225, mc=60)
- 55 msgs, 4 substantive user turns (USER#1-#4 是 4 个不同子任务)
- 本 case 聚焦 **USER#1**（deck-grounded 列表提取），USER#2/#3/#4（改网表引用/写激励/换 .inc 路径）属 produce-task 另案，不进本 case prompt

## USER#1 verbatim（逐字保留）
> /proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_corner/在这个路径下有15个sim*.sp文件，里面分成了5种工艺角，并且每个文件中扫描了5种温度，我需要你拉一个列表，列出五种工艺角下sim*.sp中定义的电压值，以及在五种温度下的变化情况。引用的文件也看一下，这部分就只列举变化项就行

## 助手真实工作流
1. `list_allowed_files` 列 3 个目录（Yiotwist_corner / Yiotwist_case5 / test_sim）
2. `read_files` 批量读 15 个 sim*.sp + 引用文件（yioloading/wr_common.sp/Pattern_Power_CRG.sp/stimulus_*.sp）
3. 分析：3 pattern group (p1pl3/p1a3_pl3/p2a4_pl3) × 5 corner (tt/ff/fs/sf/ss) = 15 文件；每文件 `.alter` 扫 5 温度 (-40/25/45/98/130)
4. 最终答案（idx 54）：corner 间变化 pvintcore (tt=0.8/ff=0.77/fs=sf=ss=0.9) + pvdd2h (tt=0.94/ff=1.25/fs=sf=ss=0.9)；常量 pvcc=0.9/pvcsl=0.88/pvint=0.65/pvintzYsa=0.65；温度相关（来自 Pattern_Power_CRG.sp ternary）pvwlp(-40=2.8/其他=2.6)/pvmwln(2.4/2.2)/pviso(1.44/1.36)/pvblh(0.9/pvcc-0.1)

## 源可达性
- `/proj/ddgoa/V0/workdir/ghyang/DDGOA/Yiotwist_corner/` 对 eda_agent (uid 200450) **Permission denied**
- 但 trace 内 thinking block（idx 12/16）+ 最终答案（idx 54）完整保留了真实标识符与数值
- → deck_A 按 trace 证据 focused 重建（同 l2vvy/0vmow 范式），真实参数名/corner 名/温度点/电压值全保留

## case 设计（套 6sxh5 DeckFileExplainQA-001 deck-grounded answer-extraction pattern）
- 候选写 `deck_param_sweep.py` 读 deck_dir → 解析 sim*.sp（.param 数值提取 + corner 分组 + .alter 温度）+ CRG 文件（ternary temp-dep 解析）→ 结构化 JSON
- **第 17 sub-type**: deck-grounded parameter-sweep-extraction（区别 6sxh5=file-catalog, 1tymw=deck-diagnosis, 本例=parameter-sweep voltage 表）
- B 变体反硬编码：B1(2 group×5 corner, pvcc=0.95, temps -20~110, 不同 corner 值)/B2(3 group×5 corner, pvcc=1.0, temps -55~125)/B3(退化: 全 corner 同值, 2 temps)
- check.py 15 cond a-o：zip 含 py / py_compile / B1 JSON+7 键 / B1 分组 / B1 pvintcore / B1 pvdd2h / B1 常量(且 ptemp 排除) / B1 温度 / B1 pvwlp temp-dep / B1 pvmwln+pviso / B1 引用文件含 CRG / B2 corner 值 / B3 优雅降级 / 反硬编码 A 专属 / 3-seed 确定性

## 自验
- REF PASS 15/15 ✓（3 B 全正确）
- NEG_RC=1（neg1 硬编码A 4/15 / neg2 stub 5/15 / neg3 print-only 4/15 / §4.9a empty 0/15 / §4.9c core-deleted 5/15，全 FAIL overall）✓
- k_rationale == k_check == 15 ≥ 8 ✓
- test field == disk check.py roundtrip ✓
- 26 attachments 无 hidden 泄漏 ✓

## 交付记录
- r737: case 落库 EDA-Eval-DesignFlow-DeckParamSweepQA-001（D.jsonl 422→423）
- 台账 mark 1793340943310_2r0by → case
- pool_reaudit_D.tsv 2r0by 行标 DELIVERED r737
- prototype-proven 17/24 已交付（2r0by deck-grounded parameter-sweep 新 sub-type）
