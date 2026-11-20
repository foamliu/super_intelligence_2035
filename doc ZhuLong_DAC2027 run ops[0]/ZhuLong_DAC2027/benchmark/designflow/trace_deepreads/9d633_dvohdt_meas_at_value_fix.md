# 9d633 — clarawu dVOHdT .meas at= 序号→取值修正 (deepread)

## trace 来源
- session: `1795052486611_9d633` (clarawu / hfeg0pkn005 / 10.129.2.14, mc177)
- scan: ssh_eda_search_20261120_145529 → summary_1120_reconstructed.tsv
- 4-shard cross-dedup: 9d633 仅 B ledger 未动（fresh），spice_sim 域（hspice:704 synopsys:1042 netlist:456）
- size: 979KB / 184 msg / agent=lead / 2026-11-19

## 用户真实意图 (msg0 原话)
> 帮我修改/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_FinalDrv_Ron_cio_leakage_versionD/hspiceD/schematic/netlist/stimulus_file_for_metrics/dVOHdT/stimulus_dVOHdT_M40C.sp，我想要measure temp='Tref-1'和'Tref'和'Tref+1'时的v(DQ_VOH)

经 spice_tb_stimulus skill 触发。skill 定义占 msg0 前 13KB，真实任务在尾部 `</command-instructions>` 之后。

## 原始 .sp 关键行 (msg2 read_files)
```
.param Tref=-40
.temp 'Tref'
.dc temp list 'Tref-1' 'Tref' 'Tref+1'    # 扫 3 温度点（值已对）
.meas dc VOH_Tref_minus1 find v(DQ_VOH) at=1   # BUG: at=1 是序号
.meas dc VOH_Tref_0      find v(DQ_VOH) at=2
.meas dc VOH_Tref_plus1  find v(DQ_VOH) at=3
.lib '../zqcode_75pvt.sp' ZQCODE_FF/TT/SS_M40C_0P85V_0P5V
```
**bug**：HSPICE/FineSim `.meas ... at=<value>` 期望扫描变量取值（`'Tref-1'`），不是 1 起始序号。`at=1` 测错点（找 temp=1，不在 sweep 里）。

## agent 工具链 (184 msg 节选)
- msg1: read_files 目标 .sp + skill references (template_measure.sp / model_libraries.md / builtin_analysis.md)
- msg4-17: 探 sibling 目录 dRONdT/dRONdV2/dRONdVQ/stimulus_Ron_tt.sp 学约定（nested DC sweep + .meas when/find at= 模式）
- msg20-25: get_agent_policy_status + 写 _grep_measure_at.py 查 HSPICE manual
- msg34-36: read `/apps/synopsys/hspice/S-2021.09-SP2-2/hspice/docs_help/hspice_14/measure_find_when.htm` 确认 `at=SweepValue` 语义
- **msg48 (核心 edit)**: `at=1/2/3` → `at='Tref-1'/'Tref'/'Tref+1'` (old_text/new_text 逐行)
- msg52+: 多轮迭代 `.dc` 形态（list→POI 3→嵌套 sweep→回 POI 3）、`.meas` 命名（3 条命名→单条 VOH→回 3 条命名）
- msg96-154: 反复 read 验证，最终落 `.dc temp POI 3 'Tref-1' 'Tref' 'Tref+1'` + 3 条 `at='Tref±1'`
- msg176-183: 后续子任务——extract_dVOHdT.py MAX 行加 %/C 百分比列，cp 到 /proj

## 合成的 case
`EDA-Eval-DesignFlow-MeasAtValueFix-001` (spice_sim, L1, A 档 trace-faithful)
- 聚焦 msg0 的 `.meas at=` 序号→取值修正子任务
- 交付 `meas_at_fix.py`（纯 Python），解析 `.dc` temp 扫换取值列表（list/POI/嵌套 sweep 三形态），把未注释 `.meas ... at=<int>` 改成 `at='<对应取值>'`
- hidden B: 3 sweep 形态 + no-target/already-fixed/非 .sp，扫描增量/结果名/节点/corner 均异于 A anti-hardcode
- check.py k=12 (a-l), ref PASS 12/12, NEG 4/4 FAIL (naive_empty/print_only/core_removed/hardcode_a), 3-seed 确定性

## 后续候选（同 session，不取避免 case 膨胀）
- msg176: extract_dVOHdT.py MAX 行加 %/C 百分比列（独立子任务，可造）
- msg52-100: `.dc` 形态迭代（list↔POI↔嵌套）——形态探索，非用户明确要求，不造
