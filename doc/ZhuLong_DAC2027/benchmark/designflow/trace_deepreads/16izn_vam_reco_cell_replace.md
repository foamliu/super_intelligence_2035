# trace deepread — 1793080793153_16izn (e03179 @ hfeg0plg15) — VAM 可替换 cell 分析

## trace 元信息
- sid: 1793080793153_16izn.messages.json  (目录 /home/e03179/.cline/data/sessions/1793080793153_16izn/)
- user/host: e03179 / hfeg0plg15 (10.129.2.11)
- mc=78 (keywords: netlist/analog/transistor/waveview/aether/cmos/pyaether/pdk)
- 66 msgs / 2 user turns / spice 工具计数 3163
- 06:4x peek 标 CLEAN A-faithful（U#1 提需求无根因）；本轮交付

## 用户轮（A-faithful 选轮）
- U#0 (msg_idx=0): `<skill_instructions name="vam-agent">` 自动注入技能上下文（非用户目标，不计入 prompt；关键节选作 vam_agent_skill.txt 资产）
- **U#1 (msg_idx=2) = 任务说明逐字原文**：
  「方案二的仿真路径是/proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_DDR6TOP/primesim.Golden008_Perbank_ActWrRd_Dqtoogle_SC0_WPre_4s4t_WPst_4p5_RPre_4s4t_RPst_0p5_RPs_2_CAParity_ENA_CMDBLK_ENA_MD_16b_tCH50_2b16g_BLs_11600_FF_ZERO_PAD.X2P3_11600.FF1.23V-40C.X2P3，帮我查看下哪些cell可以直接替换」
  - 提出需求（查哪些 cell 可直接替换），未指出根因/未给修复方案 → A-faithful ✓

## assistant 工具链 & 金标准
1. A#1 解释方案一(模拟 cell Verilog-AMS)/方案二(数字 block 波形回放 gen_bnk_va)
2. U#1 后：assistant 读 `/home/e03179/.cline/skills/vam_reco_Golden008.json`（profile_analyzer 产物，对应路径中 Golden008 run）
3. A#21 中间结论：CRC 判定（路径不含 CRC_01/10/11 也不含 CRC_00 → CRC 关闭 → D_CRCR10_CRCTop 静态可建模为常量）+ 数字 wrapper 候选表（6 行）
4. 用户经 ask_question 选 D_CRCR10_CRCTop；assistant 尝试定位 DSIM 产物失败
5. 用户「先只留结论，不生成模型」
6. **A#65 最终用户接受结论**：
   - CRC：路径不含 CRC_01/10/11、不含 CRC_00 → CRC 关闭 → D_CRCR10_CRCTop 输出静态 → 可建模为常量
   - 数字 wrapper（方案二 gen_bnk_va 可直接替换，来自 wrapper_skipped_top，按 eval% 排序）：
     array16g_psd0(1,50.93,69.69) / chanpsd0(2,30.95,29.46) / controller(2,21.65,29.28) /
     r_rasbase_lv(32,11.51,17.07) / r_sacntrlbnk_lv(32,10.90,16.41) / r_rowctrl(2,7.26,10.55)
     （assistant 展示 6 行；wrapper_skipped_top 实有 10 条，本案金标准取完整 10 条的确定性数据）

## 真实 profile 数据（vam_reco_Golden008.json, 69KB/2808 行）
- wrapper_skipped_count=120, wrapper_skipped_top=10（见上 + bnkgtopx1/r_rasbnklogic/channel/r_refrsaok_ctrl）
- summary: total_subckts=4718, recommended_count=9, wrapper_count=120, digital_count=1953
- recommended (方案一 distractor): r_lvlshftvcc2sc2vdly / io_cabufcore / ...
- digital_skipped_top (distractor): d_banklogic / ntn_lv / ...

## 案例合成（EDA-Eval-DesignFlow-VamRecoCellReplace-001）
- domain=spice_sim, track=faithful(A), level=L1
- prompt=U#1 逐字原文
- task_brief=接口说明（--profile/--sim-path/--output + JSON schema）
- A 资产: vam_agent_skill.txt（skill 关键节选原文）+ vam_reco_Golden008.json（profile，含真实 wrapper 值+distractor）+ sim_path.txt + prompt.txt + task_brief.md
- hidden B: vam_reco_profile_B.json（8 个不同 wrapper：digtop_a0...dlygen_h7，不同 usage/eval/solve + 不同 summary）+ sim_path_B.txt（含 CRC_01 → CRC on/dynamic，与 A 结构反转）
- 金标准逻辑: crc_status 从路径判（含 CRC_01/10/11→on else off）；crc_block=D_CRCR10_CRCTop（DSCQA，从 skill 推断）；modeling=constant(off)/dynamic(on)；digital_wrappers=wrapper_skipped_top 抽 4 字段按 eval_pct 降序
- ref: vam_reco_ref.py；check.py 14 断言(a-n) + 4 negative + negative_selftest
- 自验: ref PASS 14/14 ✓ + 4 negative 全 FAIL(distinct) ✓ + §4.9 三假(empty FAIL a / print-expected FAIL b / naive FAIL d)全 FAIL ✓ + 断言闸门 14==14≥8 ✓ + jsonl test sha==disk ✓
- 追加 EDA-Eval-DesignFlow_B.jsonl(198→199) + mark ledger(200→201 covered, spice_sim 158→159)
