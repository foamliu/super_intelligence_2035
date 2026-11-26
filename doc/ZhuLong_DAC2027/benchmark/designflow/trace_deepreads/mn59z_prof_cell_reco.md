# trace_deepread: 1793167500635_mn59z (mn59z) — vam-agent prof cell recommendation

- **session**: `1793167500635_mn59z.messages.json` · user `e03179` · host `hfeg0pkn002` · mc=28
- **domain**: schematic_netlist (finesim.prof 分析 → 模拟 cell 建模推荐)
- **case_id**: EDA-Eval-DesignFlow-ProfCellReco-001 (A 档 trace-faithful, L1-boundary)
- **trace size**: 36 msgs, 1 user text turn (single-shot task)

## 用户原话（U#1，逐字，A 档任务说明）
```
[vam-agent] 根据这个prof文件看下哪些cell适合重新建模/proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20260907PM_DDR6TOP_Test_profile/primesim.Golden008_Perbank_ActWrRd_Dqtoogle_SC0_WPre_4s4t_WPst_4p5_RPre_4s4t_RPst_0p5_RPs_2_CAParity_ENA_CMDBLK_ENA_MD_16b_tCH50_2b16g_BLs_11600_TT_ZERO_PAD.X2P3_11600.TT0.92V25C.X2P3/finesim.prof
```
- 选轮规则：U#1 是「提出需求」轮（用户给 prof 路径，要 cell 建模推荐），未给根因/修复方案 → 合格 A 档任务说明。

## agent 工具链（trace 重建）
1. `skills(vam-agent)` → 拿到 skill 说明（VAMAgent fullchip 仿真加速，两场景路由）
2. `get_agent_policy_status` + `list_allowed_files(/home/e03179, depth=2)` → 探 workspace
3. `run_commands` 被 policy 禁用 → `read_files(/home/e03179/.cline/plugins/agent-policy.json)` → 发现 python-runner profile
4. `list_allowed_files(/proj/dscqa/.../primesim.Golden008_..., depth=1)` → 文件存在（resolve 到 /rundata/dscqa_sim/...）
5. `list_allowed_files(/home/e03179/.cline/skills, depth=1)` + `list_allowed_files(vam-agent, depth=3)` → 找到 skill assets
6. `read_files(/home/e03179/.cline/skills/vam_reco_Golden008.json)` (prior analysis) + `read_files(vam-agent/assets/profile_analyzer.py)` → 检查 analyzer 接口
7. `run_approved_command(profile=python-runner, filePath=profile_analyzer.py, args=[simpath])` → 跑出 reco（exitCode=0，stdout 截断）
8. `read_files(/home/e03179/vamagent_tmp/reco_Golden008.json, lines 3-40, 1-330)` → 读完整 reco JSON
9. A#35 总结报告：总 subckt 4718，推荐纯模拟 11 个（占 3.09%），排除数字标准单元 1967、数字 wrapper 120、trim 53、寄生 RC 2。Top: rndiff_3t_ckt（41215 用量/2.39%）/ r_lvlshftvcc2sc2vdly（512/0.37%）/ ag_vdbiasact / io_cabufcore / ...
10. `ask_question`（让用户选先建哪个 cell）→ trace 末尾，用户隐含接受（reco JSON 已落盘 = 用户实际接受的工具产物）。

## 金标准（profile_analyzer.py v1.2.0，ssh cat 全量复刻）
- **prof 格式**：
  ```
  .subckt <name> <usage> <eval_cost> (<eval_pct>%) <solving_cost> (<solve_pct>%)
     <inst_name> <child_subckt> <eval_cost> (<pct>%) <solving_cost> (<pct>%)
     <N> devices <eval_count> <eval_cost> (<pct>%) <solving_cost> (<pct>%)
  .ends
  ```
- **分类口径**（无 --netlist，纯名字分类）：
  - `is_digital(name)`：DIGITAL_EXACT / DIGITAL_EXACT_PREFIXES(`d_`,`ntk_`,`ptk_`...) / DIGITAL_PREFIXES(`inv`,`nand`,`nor`,`buf`,`dlyg`,`aoi`,`oai`,`mx`...) → digital_skipped
  - `is_mos_primitive_by_name(name)`：MOS_PRIMITIVE_PREFIXES(`ntn_`,`ptn_`,`ntnlv_`,`ptnlv_`,`ntn`,`ptn`,`ntk_`,`ptk_`) → mos_skipped（注意：`ntn`/`ptn` 是前缀匹配，会吃掉 `ntnlv`/`ptnlv`）
  - `is_trim_cell(name)`：名字含 `trim` → trim_skipped
  - `is_parasitic_cell(name)`：`parasitic`/`parasiticrc`/`parasiticcc`/`forcedummybl`/`d_pwdnw_ckt` 前缀 → parasitic_skipped
  - `is_digital_gate(name)`：`latsq`/`latrsq`/`and3`/`nor2`/`nand2`/`and2`/`or2`/`xor`/`xnor`/`aoi21`/`oai21`/`aoi22`/`oai22` 前缀（很多与 DIGITAL_PREFIXES 重叠，`latsq` 不重叠 → 漏到 digital_gate）
  - `is_digital_wrapper(info)`：device_pct<2% 且 children>5 → wrapper_skipped
  - leaf-analog = has_devices 且 not is_digital → recommended（按 solving_cost 降序）
  - min_pct 过滤：solve_pct < 0.001（在 is_digital 之后、trim/parasitic/mos 之前）→ 静默丢弃（不计入任何 skip）
  - wrapper（无 devices、children<=5）→ 静默丢弃（不计入任何 skip）
- **输出 JSON schema**：`top_solving_cost`/`recommended[]`(top_n)/`recommended_count`/`recommended_total_solve_pct`/`{digital,mos,trim,parasitic,no_ports,digital_gate,pass_gate,wrapper}_skipped_count`+`_top`(top10)/`summary{total_subckts, recommended_count, ..., *_count}`
- **CLI**：`profile_analyzer.py <prof> --json <out> --top 30`（无 --netlist）

## 合成（trace-faithful，真实 prof 已无法访问）
- **prof_A**（SUT 可见，assets/finesim.prof）：15 subckt
  - 5 leaf-analog（recommended）：rndiff_3t_ckt(41215,2.39%,6dev,child d_npw_ckt) / r_lvlshftvcc2sc2vdly(512,0.37%,5dev,children ptn_lv+ntn_lv) / ag_vdbiasact(8,0.15%,10dev) / io_cabufcore(96,0.08%,4dev) / t_cmf_sa_latch(1024,0.05%,8dev)
  - 4 digital：invx1/nand2x1/dlyg2s2_gut2/bufx1
  - 2 MOS：ntn_lv_pc60/ptn_lv_pc60
  - 1 trim：vref_trim_ctl
  - 1 parasitic：parasiticrc_a_dec（用 `parasitic` 前缀，非 `d_`，避免被 is_digital 的 `d_` 前缀吃掉）
  - 1 wrapper（4 children<=5 → 静默丢弃）：wrap_top_logic
  - 1 min_pct-dropped（solve_pct=0.0005<0.001 → 静默丢弃）：tiny_aux
  - expected_A summary: total=15, rec=5, digital=4, mos=2, trim=1, parasitic=1, gate=0, pass=0, wrapper=0, rec_total_pct=3.04
- **prof_B**（hidden，名空间与 A 完全不相交）：15 subckt
  - 6 leaf-analog：rndiff_5t_cko/r_lvlshftvdd2sc2vsp/ag_vsenseamp/io_dccalibuf/t_ras_rowamp/af_fusectrl
  - 3 digital：invlx2/nor2lvx1/dlyg4of8s2_ut
  - 2 MOS：ntn_hv_pc40/ptn_hv_pc40
  - 1 trim：clk_trim_div
  - 1 parasitic：parasiticrc_net
  - 1 digital_gate（`latsq` 不在 DIGITAL_PREFIXES，漏到 digital_gate）：latsq_dpram
  - 1 wrapper（6 children>5, device_pct=0<2% → wrapper_skipped）：wrap_bnk_logic
  - expected_B summary: total=15, rec=6, digital=3, mos=2, trim=1, parasitic=1, gate=1, pass=0, wrapper=1, rec_total_pct=2.42
- **deliverable**：submit.zip 含 `cell_reco.py`（`python3 cell_reco.py <prof> --json <out>`，复刻 profile_analyzer.py 分类口径）
- **check.py**：16 条件 a-p（zip 含脚本/py_compile/跑 B exit0+JSON/顶层键/recommended 名序列/recommended_count/total_subckts/digital/mos/trim/parasitic/digital_gate/wrapper 计数/跨输入护栏/3 跑语义一致/total_solve_pct）；独立用 profile_analyzer_ref.py 在 B 上算期望逐条比对；3 假（empty→c / print_fixed_A→n[leak A names]+h / core_deleted→i/j/k[零计数]）全 FAIL distinct ✓；4 negatives ALL-FAIL ✓
- **资产**：A=finesim.prof+profile_analyzer.py(技能工具,提供给SUT)+prompt.txt(U#1逐字)+task_brief.md；hidden B=finesim.prof+hidden_manifest.json(expected B recommended ordered+summary+A-only cross_guard token)

## 教训
1. `is_digital` 的 `d_` 前缀会吃掉 `d_pwdnw_ckt`（本应 parasitic）→ A 档 parasitic cell 命名必须用 `parasitic` 开头，不能用 `d_pwdnw_`。
2. `latsq`/`latrsq` 不在 DIGITAL_PREFIXES → 会漏到 digital_gate_skipped（B 用来测该分类路径）。
3. `passgt` 在 DIGITAL_PREFIXES → pass_gate 名字分类永不触发（无 --netlist 时 pass_gate_count 恒 0）。
4. `list(set(children))` 跨进程 hash 随机化 → check.py 的 determinism 必须语义比对（recommended 名序列+summary），不能 raw sha256。
5. profile_analyzer.py 本身是 config-driven 的纯 Python 工具 → 天然 L1-boundary 金标（无需降级二进制）。
