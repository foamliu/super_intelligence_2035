# Deep-read: sid_1786710801484_wsi93 (pg_layout, r191)

- shard C · domain pg_layout · user e0014566 · host hfeg0pkn005 · mc=143 · 149 msgs
- selected for r191 (fresh, lowest-coverage domain). Distinct from r190 (rundir defaults).

## A-档 user intent (msg#0, verbatim)
请你识别到 Library: auto_austin_case1,  cell: BCenterL_rscalc , 中 layout 的布局，识别出  autovia 和 powerfill 生成的cell, 并把这些 cell 去除。

## Assistant product (real)
- 用 SKILL sandbox (dbOpenCellViewByType) 探索 BCenterL_rscalc layout：顶层 166 instances / 40 unique master cells；层次 2–3 层。
- 按 **cell 名称模式** 分类 autovia / powerfill / keep。
- 删除 5 个 instance：顶层 3 (BCenterL_rscalc 166→163) + BCenterL_rt_all 子层 2 (25→23)。
- 写出 remove_autovia_powerfill.il 脚本；AFTER 验证 autovia/powerfill remaining = 0。

## Classification rule (assistant reasoned — the GOLD)
- autovia（去除）= 名称含 "VIA"/"via" 且**不是**标准 via（标准 via = `Via_<n>_<n>` 小叶子 cell，如 Via_34_1/Via_34_2，assistant 明确 reasoning "small standard via cells, not autovia-generated"）。
- powerfill（去除）= 名称含 "fill" 或 "power_improve"。
- keep = 其余，包括：
  - 电源 routing：`BCenterL_M3_power`（含 "power" 但非 power_improve/fill）、`L_Pwr_line`（"Pwr" 缩写）
  - "au_to_pg" routing（BCenterL_au_to_pg = auto to power ground）
  - AutoCap / CAP_rt_xlk / plug / plug_std_vbn / spacer / brknet / switch_open/close / RDV
  - stdcells (invLx4/16, nor2Lx6, bufLx32/48)
  - IO pads (IO_BCenterLTopPad/BotPad, BcenterL_pad)
  - 标准 Via_N_N
- 删除实际用的 SKILL regex：`rexMatchp("via" lowerName) || rexMatchp("fill" lowerName) || rexMatchp("power_improve" lowerName)`（注：raw regex 会命中 Via_34_1/2，但它们在 level-2 不在 2 层删除范围内；assistant 的 *意图* 分类排除标准 via → gold 采用 reasoned 版本，作 anti-hardcode 判别）。

## Real cells (top-40 unique masters, from tool result)
zlib/BCenterL_PCUCT_auto_pc1, zlib/BCenterL_au_to_pg, zlib/BCenterL_20250425_VIA_TOP[AV],
TECHLIB/plug, zlib/BCenterL_CAP_rt_xlk, zlib/power_improve_hyx[PF], stdcells_ac/bufLx48,
TECHLIB/spacer, zlib/BCenterL_buf_xlk, drjqa_analog/BCenterL_AutoCap_1S, zlib/BCenterL_WEAK_CT,
zlib/BCenterL_rt_all, zlib/plug_std_vbn, drjqa_io/IO_BCenterLTopPad, drjqa_io/IO_BCenterLBotPad,
stdcells_ac/invLx16, stdcells_ac/nor2Lx6, zlib/D_RepeaterL_rt_tex32, TECHLIB/switch_open,
drjqa_digital/AF_AllTop, TECHLIB/brknet, zlib/BcenterL_pad, drjqa_digital/T_BlComMdPupPdn,
stdcells_ac/bufLx32, drjqa_digital/T_RevBitSerialOut, zlib/BCenterL_nw_fill[PF], TECHLIB/RDV,
stdcells_ac/invLx4, drjqa_analog/AG_AnalogChLSub, drjqa_digital/AF_BcCnt, drjqa_analog/AG_CapBCenterL,
drjqa_digital/D_RepeaterL, drjqa_digital/T_CMLeft_L1, drjqa_digital/T_RingOscReadSig2,
TECHLIB/switch_close, drjqa_digital/T_IsmTop, zlib/BCL_RDL, drjqa_digital/T_CMLeft_R1,
zlib/L_Pwr_line[KEEP-PWR], drjqa_digital/T_RingOscReadSig1
([AV]=autovia remove, [PF]=powerfill remove, [KEEP-PWR]=power routing keep)

## Removed instances (gold output)
- L0 BCenterL_rscalc: I2→BCenterL_nw_fill(PF), I_power_improve_hyx_155→power_improve_hyx(PF), I30→BCenterL_20250425_VIA_TOP(AV)
- L1 BCenterL_rt_all: I_BCL_power_improve_wf_10→BCL_power_improve_wf(PF), I9→BCenterL_20250611_VIA_TOP(AV)
- Total 5. After: 166→163, 25→23, remaining PG=0.

## Standard vias (KEEP, anti-hardcode)
Via_34_1, Via_34_2 — 3 shapes each, `Via_<n>_<n>` pattern, NOT autovia-generated.

## L1 boundary
纯 stdlib Python 分类器 `classify(name)->"autovia"|"powerfill"|"keep"`，无需 EDA 工具；可离线验证。
