# trace_deepread · 1789699043373_y91i6 · ericw@hfhds201 · shard B characterization

## trace 元信息
- session: `1789699043373_y91i6`（ericw, hfhds201/.75, 50 msgs, 1.2MB, 2026-09-21）
- match_count: 34（spice_kw 命中：spice/simulator/finesim 等，来自 hfhds201 local spice-dom 重建）
- 域：characterization（DDR5 drcpa aicov 覆盖率 dump 分析）
- 真实附件路径：`/rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/cov_work/scope/html_18-09-2026_10~26~40/table1.json`（.75 上 permission-denied，内容从 trace tool_result 还原）

## 用户轮（逐字，A-档选轮）
- **U#0（msg#0，任务说明轮，逐字作 prompt）**：
  `/rundata/drcpa_sim/V0/simdir/finesim/workdir/ericw/verilog.ddr5.drcpa.aicov/cov_work/scope/html_18-09-2026_10~26~40/table1.json`
  `总结里面cg_t 没有命中meet_exactly的bin`
  → 提出需求（总结 cg_t 未命中 meet_exactly 的 bin），无根因/修复方向 → **符合 A-档选轮**
- U#22（msg#43）：「给我做一个表格 并且把VrefCA VrefCS SRX REF RFM 相关得去除」= 表格过滤澄清轮（不入 prompt）
- U#23/24（msg#45/46）：「就只有这么多吗 把你筛选掉的也写出来」= 补全澄清轮（不入 prompt）
- U#25（msg#48）：「把SRE相关的也去除 并全部列出来」= 追加过滤轮（不入 prompt）

## assistant 工具链
1. `read_files` table1.json（分批 32 次 line-range 读，1079 covergroup）→ 每个 covergroup 有 `items_json` 指向 `table2/item*.json`
2. `read_files` table2/item*.json（142 个 coverpoint，title=`cp_delta_min_vs_constraint_min`）→ 每个有 `items_json` 指向 `table2/table3/item*.json`
3. `read_files` table2/table3/item*.json（137 个 bin 文件，每个含 3 bin：`meet_exactly`/`safe_within_half`/`safe_beyond_half`，各带 `All Cov` 如 `1 / 1 (100%)`=HIT / `0 / 1 (0%)`=MISS）
4. `search_codebase`（cg_t，超时失败）· `run_commands`（disabled）· `editor`（写 outside policy 失败）→ 最终在对话内文本输出
5. 收集 **134 条** cg_t covergroup 其 meet_exactly bin 未命中（0/1）

## 层级 schema（从 trace 还原，真实）
```
table1.json = [ {title:"coverage_model::cg_t_*", All Cov, items_json:"table2/itemN.json"}, ... ]
table2/itemN.json = [ {title:"cp_delta_min_vs_constraint_min", All Cov, items_json:"table2/table3/itemM.json"} ]
table2/table3/itemM.json = [ {title:"meet_exactly", All Cov:"1 / 1 (100%)"|"0 / 1 (0%)"}, {title:"safe_within_half",...}, {title:"safe_beyond_half",...} ]
```

## 金标准（assistant 实际产物）
- 134 条 cg_t meet_exactly 未命中 covergroup（名+覆盖率），逐字记录于 msg#49 完整表格（含 VrefCA/VrefCS/SRX/REF/RFM/SRE 过滤标注）
- 可复用子流：按 table1.json `cg_t` title 过滤 → 沿 `items_json` 下钻 table2→table3 → 找 `title=="meet_exactly"` bin → `All Cov` 非 100% 即未命中

## 通用化 case
EDA-Eval-DesignFlow-CgMeetExactlyMissWalk-001 (characterization A-faithful L1, k=14)
- 脚本 `find_cg_t_meet_exactly_miss.py` 读 cov_dir → `out.json`[{covergroup, meet_exactly_cov, covergroup_cov}]
- A：14 covergroup（6 cg_t miss 含 TRAPg[table1 100% 但 meet_exactly 0/1] + 4 cg_t hit 含 TRAPh[table1 1/3 但 meet_exactly 1/1] + 1 cg_x_miss[title 非 cg_t 诱饵] + 3 nontiming[CMD_cov/MR0_cov/speed_grade_cov 无 meet_exactly bin]）+ table2/table3 完整层级；真实 covergroup 名（VrefCA_TO_MPC_ZQCal_Start/REFab_TO_MRW_tRFC2_Table_22/WR_TO_PDE_CWL_WBL_2_WRLegacy_1_tCK_Table_358/MRR_TO_MPC_ZQCal_Latch/VrefCA_TO_SRE 等，逐字来自 trace msg49）
- hidden B：10 covergroup（4 cg_t miss 含 TRAPg_B + 3 cg_t hit 含 TRAPh_B + cg_x_voltage + MR2/MR3）不同名/不同命中模式
- check.py 14 断言(a-n)：zip/script/py_compile/B exit0+JSON list/miss set 相等/不含 HIT/不含 non-cg_t/TRAPg 必在/TRAPh 必不在/层级下钻证明/meet_exactly_cov 字段正确/3 次幂等/非空/A 泛化/无 A 标记泄漏
- 4 negative（naive_table1_only/naive_substring_cg/naive_any_meet_exactly/always_empty）全 FAIL · §4.9 三假（空壳/打印期望/删核心）全 FAIL
- 断言闸门 k_rationale=14 == k_check=14 ≥ 8 ✓
- 自验 ref PASS 14/14 ✓

## 选轮合规
- 仅 U#0 入 prompt（提出需求，无根因/修复方向）；U#22/23/25 表格过滤/补全/追加澄清轮均不入 prompt
- 不脱敏：真实 user=ericw, host=hfhds201, session=y91i6, 路径 /rundata/.../ericw/... 一律保留
