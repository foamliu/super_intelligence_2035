# 深读笔记 · cwq7f · Sentaurus TCAD deck setup 学习总结

- **session**: 1793268873755_cwq7f.messages.json (3,177,693 B, 617 msgs)
- **user / host**: e02141 @ hfeg0pkn001 (mc=698, domain=characterization)
- **审计来源**: r618 pool_reaudit_B.tsv 第 mc698 复活候选（旧判 parked "sentaurus-tcad-deck-study-QA-not-B-produce"，r435 peeked）
- **新标准判定**: 11-15 用户令——explain/study Q&A 是真实用户意图，全部恢复可造

## 真实用户意图（USER#1，原话）

> please study sentaurus deck examples under the folder: /apps/synopsys/sentaurus/V-2023.12/tcad/V-2023.12/Applications_Library, summarize the common files that are necessary for new deck setup

这是 49 个真实用户轮中的第一个、也是最自包含的一个：让 agent 学习 Applications_Library 下的 Sentaurus TCAD deck 示例，总结新 deck setup 所需的常见文件。

## 助手在 trace 中的真实做法（idx 1-28）

1. 列 Applications_Library → 16 个应用类别；判定 GettingStarted / Templates 最相关
2. 读 Templates/ (NMOS, LDMOS, HBT_SiGe)、FinFET/ (FinFET_10nm/22nm, TriGateNMOS_InGaAs)、GettingStarted/ (sdevice, sprocess, sde)
3. 检查 SWB 项目结构 + standalone deck (device-only / process-only / SDE)
4. 验证 SDE deck、.prf、.par、project readme、无 GDS 的 process deck、datexcodes.txt
5. 存参考文档到 `/home/e02141/devops/sentaurus_deck_setup_notes.md`，给出 6 类总结

## 助手产出的 6 类「新 deck setup 常见文件」总结（idx 28 原文）

1. **SWB 项目管理文件**（每个项目都有）: gtree.dat / gtooldb.tcl / gcomments.dat / greadme.html/.pdf
2. **工具输入 deck**: sprocess_fps.cmd (Process) / *_des.cmd (Device, 必含 File/Electrode/Physics/Plot/Math/Solve) / *_dvs.cmd (Structure Editor) / *_vis.tcl (Visual)
3. **工具偏好文件 *.prf**: Tcl 片段，每个工具前运行
4. **参数文件**: sdevice.par / common.par / 材料 .par / datexcodes.txt (DATEX2.1)
5. **几何/版图输入** (layout-driven 时): *.gds / *_lyt.mac / *_mkp.mac / Model.fps
6. **可选**: 编译自定义模型 .C/.o/.so (如 BALMob mobility DLL)

工具链: sprocess → sdevice → svisual，SWB 用 @...@ 占位符管理参数与节点展开。

## 操作化（造题）

- **形态**: characterization / L1 便携 analysis-explain（offline Python 扫目录树 → 结构化 JSON 总结）
- **A 档 trace-faithful**: 保留真实用户名 e02141 / host hfeg0pkn001 / Applications_Library 路径 / 6 类分类 / 真实文件名 (gtree.dat, gtooldb.tcl, *_des.cmd, *_dvs.cmd, *_vis.tcl, *.prf, *.par, datexcodes.txt, *.gds, *_lyt.mac, Model.fps, BALMob.C) / 真实工具链 sprocess→sdevice→svisual / SWB @...@ 占位符
- **任务**: 写 summarize_deck_setup.py(workdir, out_json) 扫 workdir/Applications_Library/ 识别 SWB 项目、分类所有文件、解析 *_des.cmd 必备 6 段 (File/Electrode/Physics/Plot/Math/Solve)、推 tool_chain、算 common_files（出现在所有项目的精确 basename 交集），产 deck_setup_summary.json，打包 submit.zip
- **hidden B 跨输入守卫**: B 用偏移项目 (GettingStarted/sprocess/SP, Templates/LDMOS, FinFET/TriGateNMOS_InGaAs) + 偏移 *_des.cmd basename (SP_des.cmd/LDMOS_des.cmd/TriGate_des.cmd) + _InGaAs.par (B 独有) + Model.fps 位置不同 → naive_hardcode_a 必在 l/m FAIL
- **新形态标记**: reaudit「study+summarize→结构化讲解报告」操作化首例 + Sentaurus TCAD deck-setup 域首例 + SWB-project-marker(gtree.dat) 扫描首例 + sdevice-mandatory-6-section 解析首例 + common-files-intersection 首例

## 后续用户轮（仅记录，不造题）

USER#2-49 是后续学习/调试/导出请求（学 tcl 规则、读 manual、debug GAA_FET、配 swb-python-api、加 sdevice/SVisual 工具、导 CSV、学 sprocess、24 课存档、最后 USER#49「从零 setup 一个 DRAM array MOS vertical GAA 仿真」）。本轮只操作化 USER#1（最自包含、最契合「summarize common files」意图）。
