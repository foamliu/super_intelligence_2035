# Trace Deepread — aneeo (e0014566 / hfeg0plg58)

- **session**: `1787742497412_aneeo.messages.json` — 1605 msgs, 4.51 MB
- **match_count**: 826 (virtuoso:1215 / .gds:469 / netlist:229 / calibre:120 / cellview:92 / dbOpenCellViewByType:78 / ddGetObj:46 / pdk:24)
- **tools used**: run_commands×680, SandBox_MCP_Server__run_code×55, editor×29, read_files×23
- **domain**: analog_context（版图电源网络电阻分布报告生成；与 m2vah RsCalcFlow 同用户同主机，是其后续会话）
- **真实跑批**：run_commands 680 次绝大多数是 `sleep 25 && bjobs 381956 && ls ...rvn` 轮询 RsCalc bsub 作业（一次 baseline RsCalc 跑 ~5.2h，一次优化后 ~5.5h）

## 与 m2vah 的关系
m2vah（1785810906841）= 构建 rscalc→autovia→powerfill 编排器 + prompt_flow.md（已出 case RsCalcFlow-001）。
aneeo = **执行该 flow 后，用 RsCalc 产物生成 5 份英文电阻分布报告**。互补、不重复。

## 用户意图演进（user 轮，非 continue）
1. **msg#0**：把 test_RScalc/test_skills_8/rscalc.config 的 checkPoints 同步到当前配置。
2. **msg#19（核心需求）**：「read the prompt_flow.md and do the job in it. 基线的电阻分布一定要重新算，不要用已有的。出 5 个报告：1)优化前基线电阻分布完整报告（英文，无乱码）2)优化后电阻分布完整报告 3)优化后 layout vs 原始输入 layout(Array16G_B\layout) 比较 4)优化后 vs 优化前电阻分布比较 5)优化后 vs 原始输入 layout 电阻分布比较。」
3. msg#1188：「最优的结果 layout，增加了几个 cell」
4. msg#1194：「检查下生成的 5 个报告的数据是否正确，是否跟整体流程的真实情况保持一致」← **用户发现报告数据有误**
5. msg#1234：「为什么会有这个问题？就是说流程跑的不对吗？」
6. msg#1244：「哪个环节没对？为什么没有及时修复？后续如何避免，需要修改参数吗」
7. msg#1260：「修改 1,2,4,5，其中 1 的并行数设置为 64」
8. msg#1304：「把已经在跑的这个流程再检查一下，把没跑的数据补齐，再重新生成报告」
9. msg#1459：「上面这个为啥优化效果不明显。是该去的 autovia powerfill cell 没去除，还是新增的有问题，排查下」
10. msg#1491：「先把旧的 autovia cell 和 powerfill cell 删除干净，再重新跑一遍优化流程，再更新报告」

## 金标准（trace 末尾用户接受的结果）
工作目录 `/home/e0014566/test_layout_rscalc_flow_18/`，5 份报告（Report_1..Report_5 *.md，msg 1173-1181 初版 → 1209-1229 修正版）+ 3 份电阻数据 CSV：
- **baseline_rpoints.csv**（24 点，2 net × 12 点，format `"vcc!"_"M4"_x_y,r`）
- **optimized_rpoints.csv**（24 点，同 key）
- **original_input_rpoints.csv**（24 点，msg#227 生成，unquoted format `vcc!_M4_x_y,r`，= test_RScalc/test_skills_8 旧 RsCalc 结果）

报告结构（5 份）：
- **Report_1_Baseline_Resistance.md**：Overall Status / Power Net Setup / 每网 Resistance Results 表（# / Layer / Check Point(x,y) / R to Pad）+ 每网 Summary Statistics（min/max/avg/median + worst point）
- **Report_2_Optimized_Resistance.md**：同结构 + Optimization Applied（AutoVia/PowerFill step + output cell）
- **Report_3_Layout_Comparison.md**：Layout Lineage 链 / Structural Differences（via insertion + power fill）/ File Size / Key Differences
- **Report_4_Baseline_vs_Optimized_Comparison.md**：每点 per-point 表（Baseline R / Optimized R / Change / Reduction% / Converged?）+ Summary Stats 对比 + Convergence Analysis（targetReduction=0.3，converged = R_opt ≤ R_base×(1−0.3)）
- **Report_5_Optimized_vs_Original_Input_Comparison.md**：每点 per-point 表（Original Input R / Optimized R / Change / Reduction%）+ Summary Stats 对比

**真实陷阱**：初版报告 Report_2 把 vss! optimized 全部写成 0.000（与 optimized_rpoints.csv 实际非零值矛盾），用户 msg#1194 当场抓出「数据是否正确」→ 修正版用真实 CSV 值。这是 case 判分的关键：报告数字必须与 RsCalc CSV 重算一致，不能编造。

**优化效果（真实）**：vcc! 大部分点降幅 <1%（几乎没优化下去）；vss! M4 降幅 ~15-23%（仍不达 30% target）。故 all_converged=False、converged 点数≈0 是真实答案。

## B 档 case 设计（EDA-Eval-DesignFlow-ResReport-001）
真实 RsCalc/bsub 跑不了 → 提供 3 份真实 rpoints.csv + cell_manifest.json + flow_config.json 作为输入。候选交付 `gen_reports.py`（CLI 读数据目录，纯标准库）+ 5 份 .md + `stats.json`（机器可读统计，供 check 精确校验）。check 重算全部统计与 stats.json 对账（per-net count/min/max/mean/median/worst_point、layout_diff、baseline_vs_optimized per-point reduction/improved-worsened-unchanged/mean_reduction_pct/converged count/all_converged、optimized_vs_original 同结构）；真跑候选于 hidden B（不同 net/metal/值/target），跨输入反硬编码；3 随机行序确定性。

level=L1（Python 报告生成，编码真实 RsCalc 电阻分布报告语义）；track=B；domain=analog_context；k_check=15（a-o）。
