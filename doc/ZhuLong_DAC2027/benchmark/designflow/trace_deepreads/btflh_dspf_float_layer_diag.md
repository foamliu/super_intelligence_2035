# btflh — dspf floating-layer diagnosis 深读

**trace**: 1794225375454_btflh · e0024852@pkn004 · 56 msgs · 346KB · kw=16 (dspf/寄生/spice)
**shard**: B (spice_sim) · track A-faithful · level L1 · case = EDA-Eval-DesignFlow-DspfFloatLayerDiag-001

## 用户轮（3）
- **U#1 (msg 0)**「you can see /rundata/.../hd_CH252_bitcell.dspf 我观察到这个dspf 文件生成的并不全 我想知道寄生电路来自那一层 以及这一层的位置 帮我修改现有的命令」→ produce-task，提需求未给根因 → **A-faithful 合格** ✓（本轮任务说明取此轮逐字原文）
- U#2 (msg 23)「tell me in chinese」→ 语言偏好，trivial
- U#3 (msg 50)「我觉得我缺的是 metal 层 和 那个尺寸的过孔把 我主要是改这个减少寄生」→ 用户给出自己的根因假设（disqualify for A，不进 prompt）

## agent 工具链（msgs 1-49，phase 1 完整闭环）
list_allowed_files → read_files(gxrc 命令 / dspf / tran.map / cmd_param.log / query_cmd / lvs / cc.rep / gex 日志 / open_short.rpt / all_PG_nets.rpt / execute_cmd / pin_file / CCI_DB.GDS_MAP) → editor(analyze_layers.py/sh, 写到 /home/e0024852 因 /rundata 只读) → run_approved_command(python-runner/shell-runner) → editor(gxrc_cci_cmd_fix.txt 写修复说明) → 最终结论 msg49。

## 金标准（msg47 fix 文件 + msg49 结论）
1. **dspf *LAYER_MAP 实际贡献寄生的层**：via1/V0D/V0G/M0G/BV0/M0_CONT/M1/M2/bmetal1/poly/diffusion，抽取停在 **M2 + BM1**。
2. **无内部 via/接触层缺失**：via2-15/bvia2-4 在 tran.map 定义但单 bitcell 只走 M1/M2+BM1，停在 M2/BM1 正常自洽。
3. **根因**：gex 日志 `gex.hfeg0plg76_49437.log` 报 `TRIO-0218 Found open/short nets`；`open_short.rpt` 显示 VSS/VDD 与 floating 网 **ncr_14/ncr_15/ncr_16/ncr_17** 经 **bmetal1 / BV0N_SRAM / BV0P** 短路；命令 `REMOVE_FLOATING YES` 在 "Remove Floating" 步骤把这段 floating tap 寄生丢掉 → dspf 不全。
4. **缺失寄生层 + 位置**：**BV0（BV0N_SRAM/BV0P）背面通孔 + bmetal1（BM1）背侧金属**，垂直 stack **最底部 backside**（well/衬底 tap → BV0 → bmetal1，buried power）。
5. **命令修改**：[19] REMOVE_FLOATING YES→NO（核心）；[33] COUPLE_TO_GROUND MODE NO→YES（补接地电容，可选）；[45] FLOATING_HANDLING FLOATING 保留。

## trace 末尾
msg54 agent 在 phase 2（U#3 后）查 GDS_MAP 确认 cell 无 M3+，问 ask_question → msg55 `code_sidecar_sigterm`（会话中断）。phase 1 (msgs 0-49) 对 U#1 是完整交付（用户未拒绝，U#3 是相关 follow-up 隐含接受）。

## 资产（faithful，从 trace tool_results 重建）
- gxrc_cci_cmd_V0d1_Rev06（85 行，原始命令，line 19/33/45 关键）
- hd_CH252_bitcell.dspf（头部 *LAYER_MAP，70 行摘录）
- 35H_DBC_PEX_GloryEX_V0d1_Rev06_tran.map（层映射 + VIA 段）
- gex.hfeg0plg76_49437.log（TRIO-0218 / Remove Floating）
- open_short.rpt（VSS/VDD vs ncr_14-17 floating）
- CCI_DB.GDS_MAP（GDS 0-38，无 M3+）

## case 设计
- 可见 A：prompt=U#1 逐字 + 6 assets + task_brief
- 隐藏 B：3 变体（B1 hd_CH253/ncr_24-27, B2 hd_CH254/ncr_34-37, B3 hd_CH255/ncr_44-47），命令结构 shifted（插入注释行，REMOVE_FLOATING/COUPLE_TO_GROUND 行号位移），缺失层/根因/修复不变
- 交付：outputs/submit.zip = gxrc_cci_cmd_patched + diagnosis_report.md
- check.py：17 条独立断言（a-q），option-name regex 泛化 A→B，subprocess 选项校验器，3-seed 稳定
- 自验：ref PASS 17/17（3 seed）+ 6 neg（含 §4.9 三假）全 FAIL + byte-sync sha 733e1e59...
