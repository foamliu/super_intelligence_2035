# Trace deepread — 1793875415367_oue4a (eva1wu@hfeg0plg52, mc49, spice_sim)

**source**: `hfeg0plg52:/home/eva1wu/.cline/data/sessions/1793875415367_oue4a/1793875415367_oue4a.messages.json` (31 msgs / 393KB)
**旧判定**: parked r435 "consultation what-is-cm generic"
**新判定 (r618 reaudit)**: 可造 → explain/介绍 Q&A → 结构化讲解报告
**本轮 (r661)**: 复活池变现 #42

## 对话流（4 substantive user turn）

1. `[0]` user: `<user_input mode="act">什么是cm</user_input>`
2. `[1]` assistant: 解释 cm 多义（厘米 / Configuration Management / Configuration Memory 等）
3. `[2]` user: `<user_input mode="act">analysis dft cm and show details</user_input>`
4. `[3-16]` assistant: list_allowed_files Desktop → search_codebase dft/cm → 读 cxmt_paths.json/cxmt_lookup_app_copy.py/lib.defs/MC_script → 无命中 → skills cimi-kb-search + ask-eda 查 "DFT CM 是什么 详解" → ask-eda 返回答案
5. `[17]` user: `<user_input mode="act">你的工作能力和工作范围</user_input>`
6. `[18]` assistant: 介绍 zhulong 工作能力（代码/分析/EDA skill/MCP 等）
7. `[19]` user: `<user_input mode="act">/home/eva1wu/netlist analysis</user_input>`
8. `[20-30]` assistant: list_allowed_files → read_files /home/eva1wu/netlist（711行，分段读 line 1-95, 95-340, 340-580, 172-270, 345-510, 349-436）→ 产出 6126 字结构化分析报告

## 关键产物：`/home/eva1wu/netlist` 分析报告

助手读 AETHER-SE 导出的 HSPICE 网表（711 行 / 34 子电路 / ~6-7k 器件），识别为 **T1_CM = Configuration Memory（DFT/QA 配置存储器）**，输出报告：

1. **文件概况**：HSPICE/CDL，AETHER-SE 导出，2026-11-05 17:19:31，用户 eva1wu，顶层 T1_CM/T1_CM/schematic，711 行 34 subckt
2. **顶层架构**：XI0=T1_CM_Fram_Shift（24bit 移位+保持+WR 单脉冲）+ XI1=T1_CM_MA_Dec（3×3to8 译码 + 64×8=512 锁存阵列）；24bit 配置字 = {OP_Mark<7:0>, OP<7:0>, MA<7:0>} LSB-first 串行移入；输出 MR<511:0>
3. **模块详解**：
   - T1_CM_Fram_Shift：48× ffrqLx1（24 移位+24 保持）+ WR 单脉冲（dlyg6of8×2+dlyg8of8=20 级延迟，MCS_N 上升沿单稳态）
   - T1_CM_MA_Dec：3× T_Cm3to8DecClk（8×nand3Lx1→8×nor2Lx2→8×bufLx24）+ 64× T_CmLatchX8L（512× CM_latsqnLx1 传输门锁存）；CM_8_N 经 switch_close 接地 → 只用 64 字（6bit 地址），MA<7:6> 保留
   - 写数据 = OP & OP_Mark（按位与，OP_Mark 为写掩码）
4. **工作时序**：复位→移位 24 拍→MCS_N↑ 产生 WR_Pulse→保持 DFF 装载+译码使能+锁存透明采样→WR_Pulse 结束保持
5. **关键发现与风险**：
   - ⚠️ 旧地址字写穿竞争（高优先级）：DFF 在 WR↑ 更新，锁存阵列在 WR_Pulse 高电平期间透明，数据比地址关断早 3-5 级到达 → 旧字可能采到新数据
   - 网表不能直接仿真（无 .include/.param/.END，是待 testbench 包裹的子电路片段）
   - CM_8_N 接地只用 64 字，扩 512 字需改开关
6. **建议下一步**：两字连续编程瞬态仿真 / WR 脉宽 vs 译码延迟 PVT 扫描 / 搭 testbench

## 真实用户意图

用户先问概念（什么是cm / dft cm），后给真实网表文件要求 analysis → 最终交付物是**结构化网表分析报告**（文件概况+架构+模块+时序+发现+建议）。这是 spice_sim 域典型的 explain/analysis 任务形态。

## 造题方案

- **case_id**: EDA-Eval-DesignFlow-CfgMemNetlistExplain-001
- **domain**: spice_sim / layer L1 / form explain-analysis-report
- **A 档**: 不可行（真实 /home/eva1wu/netlist 在 hfeg0plg52 内网工程目录，SUT 沙盒无权限不可达）→ B 档 synthesized
- **A** = 真实 T1_CM 网表 verbatim（711 行）+ task_spec.json
- **hidden B** = 合成 T3_PM（Patch Memory）网表：16bit 移位 + 4-to-16 译码 + 16×4=64bit 锁存阵列，不同子电路名/尺寸/信号名，同 archetype
- **任务**: 写 cfg_mem_netlist_analysis.py(workdir, out_dir) 解析网表产 JSON 结构化分析报告
- **check.py**: 跑候选脚本于 B，验证报告反映 B 真实解析值（cross-input guard + A-leak guard + 独立重解析对账 + 真跑 + 确定性 + 退化提交 FAIL）
- **k_check**: ≥8（目标 18）
