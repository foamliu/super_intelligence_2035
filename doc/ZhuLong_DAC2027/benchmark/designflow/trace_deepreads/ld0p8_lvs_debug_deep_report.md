# Deepread — 1789913077711_ld0p8 (ziyuny / hfeg0pkn002, mc=477)

**Domain**: physical_verify (Argus LVS deep-report analyzer / lvs-debuger skill authoring) — shard C
**Session**: 261 msgs, 1.9 MB messages.json
**Case built**: EDA-Eval-DesignFlow-LvsDeepReportAnalyzer-001 (L1-boundary, B-档 synthesized)

## 用户意图流
1. msg0: 工作目录转到 /home/ziyuny/lvsdebug（setup）
2. msg2（意图轮 / skill 作者轮）: 要求按 lvs-debuger 模板写一个 LVS 深度诊断报告生成 skill — 给定一个 LVS run 目录，自动产出「结论先行」的中文 markdown 深度报告（seed-promotion 判定 / P-G 短路子项 / hcell 一对多核查 / 数据路径附录）+ 结构化证据
3. msg50（skill 调用轮）: 在真实 LVS run `/rundata/ieda_agent_test/pv/lvs/Ary_1BK_2piece_WLx448_add_device_layer` 上调用刚写好的 skill，验证深度报告输出
4. 多个 editor 工具轮：assistant 在 editor 里连续产出 10 个 lvs_sample_1..10.py 分析器脚本（逐步迭代解析逻辑），最终汇成 skill 主体

## assistant 工具链
- ls / read 探 `/rundata/ieda_agent_test/pv/lvs/Ary_1BK_2piece_WLx448_add_device_layer`（含 lvs.log / Ary_1BK_2piece_WLx448.lvs.rep / .lvs.rep.shorts / hcells / run.sh / calibreLVS.rule）
- 解析 `lvs.log`：`# RunDir:/# Layout GDS:/# Source CDL:/# LVS Rule:/# HCELL:` 注释头 → data_paths；`LVS Total Time = <n> seconds`；`Done: LVS FAIL.`/`====end====` → terminal_state/abnormal_exit；`PENDING <n>` 序列 → pending_peak
- 解析 `<cell>.lvs.rep`：`TOTAL ERRORS AND WARNINGS` 段逐条置位 error_signature（ports/nets/instances not_equal、connectivity_errors、ambiguity_warning、property_errors）；`HCELL SUMMARY` 段统计 PASS/FAIL 行 → hcell_summary{pass_count,fail_count,fail_cells}；`LVS RULE PARAMETERS` 段 `lvs_power:`/`lvs_ground:` → power_nets/ground_nets（以 `!` 结尾，保序）；`NUMBERS OF OBJECTS AFTER TRANSFORMATION` → object_statistics
- 解析 `<cell>.lvs.rep.shorts`：每条 `NET <id> SHORT <n>: <netA> - <netB> in cell <c>`，按 power/ground/internal 分类累计 pg_shorts（power_ground_direct / power_power / ground_internal / internal_internal / total / ground_nets_in_short）
- 解析 `hcells`：每行 `<layout> <source>`，按 source 聚合，多 layout → hcell_one_to_many（variants_in_summary = 变体是否出现在 HCELL SUMMARY cell 名集合）
- seed_promotion 判定：leaf 全 PASS + 中间/顶层 FAIL + ports/nets/instances 三 not_equal 同时真 → confirmed
- 写 markdown 深度报告（结论先行 + Fix actions 表 + Improvements + Data info 附录）

## 用户接受产物
lvs-debuger skill + 在 Ary_1BK_2piece_WLx448_add_device_layer 上的深度报告（seed-promotion confirmed，ground short 4016 条，无 P-G 直接短路，hcell 一对多 Ary_10sec_WLx488_scheme1 + _m 变体）。

## 案例合成
- 子任务：抽「parse 单个 LVS run 目录 → 结构化 JSON 摘要 + 中文 markdown 深度报告」重构为通用 CLI `lvs_debug_report.py`
- A（可见）= 合成 Ary_1BK_2piece_WLx448 seed-promo run（真实 cell 名 / 真实 run 路径风格，10 leaf PASS / 5 FAIL，无 P-G 直接短路，ambiguity warning True）
- B（隐藏/graded）= 合成 MemCol_256x64_TOP seed-promo run（**不同** cell / 不同 power-ground 网名 / 8 leaf PASS / 3 FAIL / **3 条 P-G 直接短路** / 无 ambiguity）→ 强制通用、非硬编码
- 判分 17 条（a–q）：含 P-G 直接短路（B=3 vs A=0，关键差异化）、hcell 一对多、seed-promotion confirmed、跨输入守卫（A≠B）、确定性
- ref PASS 17/17 + 5 neg 全 FAIL（空壳/only-print/core-deleted/hardcode-A/wrong-regex）+ §4.9 三假全 FAIL
- 闸门 k_rationale=17 == k_check=17 ≥ 8 PASS；check.py 自包含（A+B 由内嵌 builder 重建，18727B）；test==disk sha 1448761b roundtrip OK
