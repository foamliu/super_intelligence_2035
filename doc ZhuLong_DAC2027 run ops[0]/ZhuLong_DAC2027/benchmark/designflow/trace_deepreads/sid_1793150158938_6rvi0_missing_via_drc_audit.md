# Deepread: 1793150158938_6rvi0 (michael1l / hfeg0pkn003) — Missing-Via DRC + DRC Report IP-Level Audit

## Trace source
- user: michael1l, host: hfeg0pkn003, session: 1793150158938_6rvi0
- match_count: 188, tools: 559 calibre + 26 virtuoso + 22 spectre + 16 hspice + 15 pyAether + 10 schematic + 3 netlist + 1 cellview
- msgs: 217 (118 user / 99 assistant), 1.233 MB, NEW 用户 (michael1l 未在 ledger 出现过)
- agent: lead, 2026-10-28 → 2026-10-30

## 用户意图（逐字原文，A-档 seed 候选）
- USER#1 (idx=0): `有检查漏孔的吗`  ← 提出需求/目标，未给根因/修复 = **A-档 seed**
- USER#2 (idx=16): `根据当前项目的pdk写一个`  ← 给方向（写一个），仍属提出目标
- USER#3 (idx=191): `hi`
- USER#4 (idx=192): `/proj/lacaa/TV1_FS/ver/drc/lacaa_hd1p/HD1P_CXN4S1P1024X72M4B1C1R1W1BW1RE1/HD1P_CXN4S1P1024X72M4B1C1R1W1BW1RE1.drc.resultS`
- USER#5/#6 (idx=193/194): `/proj/lacaa/TV1_FS/ver/drc/lacaa_hd1p/HD1P_CXN4S1P1024X72M4B1C1R1W1BW1RE1/HD1P_CXN4S1P1024X72M4B1C1R1W1BW1RE1.drc.results` + `分析一下这个drc report 看看结果哪些还需要在IP级修改`  ← 提出分析目标

## 助手工具链
- skills×5, search_codebase×5, read_files×34, list_allowed_files×15, run_commands×1, run_approved_command×26, editor×24, ask_question×1
- 探查 PDK：read_files calibre.layer / DRC rule deck → 定位 CXMT 10G5_HK DRAM (1p4m1x2y1z)
- 层定义：M1=88/0→8501, V1=90/0→8528, M2=91/0→8541, V2=92/0→8564, M3=93/0→8577, V3=94/0→8602, M4=95/0→8613, V4=102/0→8659, CT=85/0→8475
- Via 尺寸: V1/TM4=0.19×0.38, V3/TM4=0.25×0.70
- Enclosure 值: V1 enc M1=0.0275(core)/0.03(peri), V2 enc M2=0.03, V2 enc M3=0.055, V3 enc M3=0.055, V3 enc M4=0.15, V4 enc M4=0.15, CT enc M1=0.03

## 产物（gold 候选）
### 1. check_missing_via.drc (Calibre SVRF rule deck, supplementary missing-via check)
9 类规则：
1. Layer definitions (LAYER MAP 9 层)
2. Run control (PRECISION 4000, DRC RESULTS DATABASE ASCII GDSII)
3. Missing-Via 连通性: MISSING_VIA_M1M2/M2M3/M3M4 = (M(n)AND M(n+1) NOT V) WITH AREA > 0.01
4. Via enclosure: V1_ENC_M1/M2, V2_ENC_M2/M3, V3_ENC_M3/M4, V4_ENC_M4, CT_ENC_M1 (ENC V M < threshold)
5. Single via in large overlap (EM): SINGLE_V?_LARGE = (overlap WITH AREA>1.0) INTERACT (V==1)
6. Wide-metal via count: WIDE_V?_COUNT = (M wide AND M wide) INTERACT (V<2)
7. Via off-grid: V?_OFFGRID = OFFGRID V
8. GROUP 结果: MISSING_VIA / VIA_ENC / SINGLE_VIA / WIDE_VIA / OFFGRID_VIA

### 2. gen_missing_via_drc.py (Python 生成器, 5860 chars)
- header + body 拼接，写出 check_missing_via.drc
- 参数化的 PDK 值（layer map / enclosure / via size）

### 3. analyze_drc_results.sh (DRC 报告分析脚本)
- grep -oE 提取唯一规则名前缀 (CB_/AA_/M[0-9]/Mn_Dum/Mxa/Mxb/Mya/SRAM/LUP/TPA/TPZ/PTM/PTZ/...)
- sort | uniq -c | sort -rn 统计违规计数
- sort -u 全规则名列表

### 4. DRC 报告分析结论（idx=216, 5736 chars, gold）
分析 HD1P_CXN4S1P1024X72M4B1C1R1W1BW1RE1.drc.results (258482 行):
**违规分类**：
- 🟢 Chip 级（IP 不改）: CB_W_3, CB_E_4_2, CB_E_6_1, CB_E_6_2_2, CB_E_7_4, CB_E_8, CB_R_2_1_FS, BM1_DN_1_FS, BM1_DN_4_RCM_FS, BM1_R_3_FS (10 条)
- 🟡 IP 级需修改:
  - AA: AA_A_9, AA_A_9_0_1, AA_EN_1 (3)
  - Metal spacing/width: M0_R_13/26/39, M0C_R_9/17_1/17_2, M0G_S_8, M1_R_17, M1_W_20_1, M2_R_17/19, M2_CS_0_2/3_4, M4_R_17, M7~M12_R_17, M7~M12_W_20_1, Mxa/Mxb/Mya_R_17/W_20_1 (~40)
  - Metal density: M2_DN_3_3, M7~M12_DN_*, Mxb_DN_*, Mya_DN_* (~28)
  - Mn_Dum_R_1_M1~M12 (24 dummy 填充)
  - SRAM: SRAM_AMD_S_1, SRAM_AMD_W_1_1/1_2, SRAM_M2J_EN_3 (4)
  - Latch-up: LUP_1, LUP_1_0_2, LUP_2, LUP_3_0_0, LUP_5_0_0 (5)
  - TSV/Pad: TSV_DN_1_FS, TPA_DN_1_HB, TPA_R_3_HB, TPZ_FC_DN_1, TPZ_R_1_HB, PTM_DN_1, PTM_R_3, PTM_D, PTZ_R_1 (9)
  - Via: VIAxa_W_1, VIAxb_W_1 (2)
  - 其他: EGT_R_2, AMN_S_2_3, ARV_R_5, PSR_R_3, SRW_R_1, MOM_R_2, SDB_D_1, HLP_D_1_FS (8)

**实际违规计数**（来自 tool_result idx=215, grep uniq -c）：
- 24 Mn_Dum, 16 Mxb_, 14 Mya_, 14 M9_, 14 M8_, 14 M7_, 12 M2_, 8 SRAM_, 6 PTM_, 6 M0C, 6 M0_, 6 BM1_, 4 TPZ_, 4 TPA_, 4 Mxa_, 4 M1_, 2 VIAxb_, 2 VIAxa_, 2 SRW_, 2 PTZ_, 2 PSR_, 2 M4_, 2 M0G, 2 EGT_R_2, 2×7 CB_*, 2 ARV_R_5, 2 AMN_S_2_3, 2 AA_EN_1, 2 AA_A_9_0_1, 2 AA_A_9

**优先级建议**：
- 🔴 高: Metal spacing/width (M1-M12), Metal density (补 dummy), Latch-up, Via 尺寸
- 🟡 中: AA, SRAM, TSV/Pad
- 🟢 低/Chip: CB_*, BM1_*

## A/B 档判定
- gold 依赖 live `/proj/lacaa/TV1_FS/ver/drc/...drc.results` (258482 行真实报告) + live PDK calibre.layer + live calibre
- .75 沙盒 (e0031982) 对 `/rundata/lacaa/...` **Permission denied** → 不可达
- → **A-disqualified → B-档 synthesized L1-boundary**
- 合成方向：把 DRC 报告固化为文本文件（真实规则名 + 违规计数 + 描述），把 PDK 层定义固化为 layer_map.json，候选做**离线 DRC 报告分类审计**：解析报告 → 按规则名前缀分类 → 区分 Chip 级 vs IP 级 → 优先级分级 → 输出结构化 JSON{chip_level_rules, ip_level_rules, by_category, priority, counts, verdict}

## 与已有 case 区别
- r80 DRCSpecGen = spec→SVRF 生成
- r81 MVValueCmp = LDR 值比对
- r84 FillImplantFlowAudit = AST 静态审查 flow 脚本
- 本案 = **DRC 报告解析 + 规则分类 + IP/Chip 归属判定 + 优先级分级**（报告分析类，非生成类、非比对类）
