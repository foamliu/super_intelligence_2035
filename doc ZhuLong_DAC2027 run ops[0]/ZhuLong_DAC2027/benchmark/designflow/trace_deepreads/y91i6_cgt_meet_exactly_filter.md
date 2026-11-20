# trace_deepread · 1789699043373_y91i6 · ericw@hfhds201 · shard B characterization (第 2 轮, U#22/U#25)

> 同一 trace 的第 1 轮深读见 `y91i6_cg_t_meet_exactly_miss.md`（U#0: 总结 cg_t 未命中 meet_exactly 的 bin → CgMeetExactlyMissWalk-001）。
> 本轮深读同一 trace 的**后续过滤轮**（U#22: 关键词去除做表；U#25: 追加 SRE → hidden B），抽取其"cg_t meet_exactly 未命中集合 + 关键词去除过滤表"可复用子流。

## trace 元信息
- session: `1789699043373_y91i6`（ericw, hfhds201/.75, 50 msgs, 1.2MB, 2026-09-21）
- match_count: 34（spice_kw 命中，来自 hfhds201 local spice-dom 重建）
- 域：characterization（DDR5 drcpa aicov 覆盖率 dump 分析）
- 真实附件路径：`/rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/cov_work/scope/html_18-09-2026_10~26~40/`（.75 permission-denied，内容从 trace tool_result 还原）

## 用户轮（逐字，A-档选轮）
- **U#22（msg#43，任务说明轮，逐字作 prompt）**：
  「给我做一个表格 并且把VrefCA VrefCS SRX REF RFM 相关得去除」
  → 在 U#0 已分析的 cg_t meet_exactly 未命中集合（134 条）基础上，按关键词去除 VrefCA/VrefCS/SRX/REF/RFM 相关项，做过滤表。提出需求、无根因/修复方向 → **符合 A-档选轮**
- U#23/24（msg#45/46）：「就只有这么多吗 把你筛选掉的也写出来」= 补全澄清轮（要求 kept+removed 都列出，不入 prompt）
- **U#25（msg#48，追加过滤轮 → hidden B）**：「把SRE相关的也去除 并全部列出来」= 在 A 的 5 关键词基础上追加 SRE → 本 case 的 hidden B（A kept=29 → B kept=25，4 条仅含 SRE 的行被多去除）
- U#0（msg#0，前序任务轮，第 1 轮已用，不入本 prompt）：总结 cg_t 未命中 meet_exactly 的 bin

## assistant 工具链（U#22-U#25 段）
1. 复用 U#0 段已读取的 table1.json（542 cg_t covergroup）+ table2/table3/item*.json（meet_exactly bin 的 All Cov）
2. 按 meet_exactly bin 的 All Cov 是否 `0 / 1` 判定未命中，结合 table1 的 `N / 3` 覆盖率：
   - `0 / 3` → meet_exactly 必未命中（全 0），直接计入
   - `3 / 3` → meet_exactly 必命中（全 1），排除
   - `1 / 3` / `2 / 3` → 查 table2/table3/item(N+1).json 的 meet_exactly bin All Cov
3. 关键词过滤：title 含 VrefCA/VrefCS/SRX/REF/RFM 任一 → status=removed（filter_keywords 列出命中的）；都不含 → status=kept（filter_keywords 空）
4. 输出 CSV 表（covergroup, coverage, status, filter_keywords），U#22 段 134 行（0/3=61, 1/3=48, 2/3=25；kept=29, removed=105），U#25 追加 SRE 后 kept=25, removed=109

## gold 标准（从 trace tool_result 还原 + 程序化复核）
- gold_A（5 关键词）：134 行，分布 0/3=61 / 1/3=48 / 2/3=25，kept=29 / removed=105
- gold_B（6 关键词 +SRE）：134 行（同一 covergroup 集合），kept=25 / removed=109；B kept ⊂ A kept（差 4 条仅含 SRE 的 cg_t 行），B kept ≠ A kept
- 排除项（不入 gold）：12 条 1/3 meet_exactly 命中 + 15 条 2/3 命中 + 20 条 3/3 + 30 条非 cg_t = 77 条诱饵

## case 合成决策
- **case_id**: EDA-Eval-DesignFlow-CgtMeetExactlyFilter-001
- **域/档/级**: characterization / A-faithful / L1（离线 Python 数据过滤，无需 EDA 工具）
- **prompt**: U#22 逐字「给我做一个表格 并且把VrefCA VrefCS SRX REF RFM 相关得去除」
- **交付**: outputs/submit.zip = cgt_filter.py（通用过滤脚本，CLI: cov_work_dir + filter_config + output_csv）+ cgt_meet_exactly_filter.csv（A 过滤结果）
- **hidden B**: filter_config_B = A 的 5 关键词 + SRE；check.py 在缺 hidden/ 时自动由 filter_config_A + SRE 生成（自包含，SUT 永不接触 SRE）
- **资产自包含**: 211 covergroup（134 gold + 77 诱饵）+ 100 table3 文件，synthetic 但结构与 gold 完全一致（同分布/同 kept-removed 计数/同 SRE 子集关系）
- **check.py**: 16 条独立断言（a-p），含 cross-input guard（n/o/p 在隐藏 B 上 subprocess 重跑），robust 到 eval-driver 的 3 种布局（cov_work/ 根、A/ 子目录、flatten），negative_selftest 3 neg 全 FAIL（distinct tags c/d/n）
- **assertion gate**: k_rationale=16 == k_check=16 ≥ 8 ✓

## 与第 1 轮（CgMeetExactlyMissWalk-001）的关系
- 同 trace、同 cov_work 数据、同 meet_exactly 未命中判定逻辑
- 第 1 轮（U#0）任务=**列出**未命中 covergroup（find_cg_t_meet_exactly_miss.py → out.json）
- 本轮（U#22/U#25）任务=在未命中集合上**关键词去除做表**（cgt_filter.py → CSV，含 kept/removed/status/keywords）
- 两 case 互补：前者考"下层级找未命中"，后者考"过滤+关键词去除+hidden cross-input"
