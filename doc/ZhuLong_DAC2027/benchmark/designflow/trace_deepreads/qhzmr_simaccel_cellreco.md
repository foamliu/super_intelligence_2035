# 深读笔记 — qhzmr (e03179 @ hfeg0pkn002, mc=29)

- **session**: `1793081498316_qhzmr` (dir-based: `<sid>/<sid>.messages.json`, 220KB / 36 msgs)
- **user**: e03179, host hfeg0pkn002 (10.129.2.11)
- **domain**: analog_context（vam-agent 模拟 cell 行为建模 / 仿真加速 cell 替换）
- **grade**: B（资产获取权限阻塞 → 合成；prompt 逐字原文）
- **trace_source.real_task_summary**: 用户要求对 PrimeSim Golden008 仿真路径分析哪些 cell 可以直接替换（仿真加速）；助手做 CRC 路径判定 + 解析历史 vam_reco JSON 给出 cell 推荐表。

## 用户轮（逐字）

- **U[0]**：「我有仿真加速的优化需求，你有哪些优化方案」→ meta（问方案，非 build 任务，不采纳为 prompt）
- **U[4]**（采纳为 prompt）：「方案二的仿真路径是/proj/dscqa/V0/simdir/finesim/dscqaF2/MatrixRun/MatrixRun_Netlist_Vcap_20261016PM_DDR6TOP/primesim.Golden008_Perbank_ActWrRd_Dqtoogle_SC0_WPre_4s4t_WPst_4p5_RPre_4s4t_RPst_0p5_RPs_2_CAParity_ENA_CMDBLK_ENA_MD_16b_tCH50_2b16g_BLs_11600_FF_ZERO_PAD.X2P3_11600.FF1.23V-40C.X2P3，帮我查看下哪些cell可以直接替换」
  - ✅ A-grade seed：用户表达目标（查看哪些 cell 可替换），未指出根因、未给修复方案。

## 助手 gold 链

1. **CRC 路径判定**（ASSISTANT[5]）：路径不含 `CRC_01`/`CRC_10`/`CRC_11`（也不含 `CRC_00`）→ **CRC 功能关闭** → `D_CRCR10_CRCTop` 输出静态 → **可直接替换**（gen_bnk_va 生成 PWL/常量）。
   - 判定逻辑：路径含 `CRC_01`/`CRC_10`/`CRC_11` → CRC ON → 不可替换；否则（含 `CRC_00` 或无关键字）→ CRC OFF → 可替换。
2. **finesim.prof 探查**（ASSISTANT[14-20]）：列 run 目录（netlist 符号链接、Golden008*.fsdb、si.inp 等），无 `finesim.prof`、无 `final/` → 无法重新跑耗时分析。
3. **历史 reco 解析**（ASSISTANT[20-26]）：读 `vam_reco_Golden008.json`（历史 Golden008 profiling 推荐）→ 解析为 ranked cell 表（按 solving_cost 排序）：
   | 排名 | 占比 | 用量 | 类型 | Cell |
   |---|---|---|---|---|
   | 1 | 37% | 512x | Analog | R_lvlshftVcc2sc2Vdly |
   | 2 | 8% | 16x | Analog | AG_VdbiasAct |
   | 3 | 6% | 12x | IO | IO_CABufCore |
   | 4 | 5% | 58x | IO | IO_capbuf_LocalDcaCoreVddV2 |
   | 5 | 2% | 14x | IO | IO_P2s |
   | 6 | 2% | 3x | Analog | AG_VibCom |
   | 7 | 1% | 56x | IO | IO_DataSample |
   | 8 | 1% | 2x | IO | IO_CABufCore_CS |
   | 9 | 1% | 16x | IO | IO_CAODT |
4. **用户选定** D_CRCR10_CRCTop → gen_bnk_va 波形回放替换（ASSISTANT[30-34]）。

## 资产获取阻塞

- `/proj/dscqa/V0/simdir/finesim/...` 在 10.129.2.11 上 `Permission denied`（e0031982 无读权限，同 #408 /rundata/drcpa）。
- → 采 B-grade synthesized：trace_source 真实 qhzmr，assets 合成但忠实复刻 trace 结构（CRC 路径判定 + reco JSON ranked cell 表）。

## 合成方案

- **候选任务**：写 `analyze_sim_accel.py` 读 sim_path.txt + config.json + vam_reco.json → 输出 report.json（CRC 判定 + ranked cell 表）。
- **A（可见）**：sim_path 无 CRC 关键字（CRC OFF → crctop 可替换）+ 9 cell reco（忠实 trace 9 cell）+ config DSCQA→D_CRCR10_CRCTop。
- **hidden B**：sim_path 含 `CRC_11`（CRC ON → crctop 不可替换）+ 10 cell reco（不同 cell 名/用量/占比，结构不同）+ config 同 DSCQA。
- **结构差异**：A=9 cell/CRC OFF/top=R_lvlshftVcc2sc2Vdly；B=10 cell/CRC ON/top=R_dly2VddVss（不是换文件名）。
- **check.py 16 条 a-p**：zip 结构 / py_compile / B-run exit0 / 顶层键 / CRC 判定键 / B crc_enabled==True / B crctop_replaceable==False / B crc_block_name / cell 列表长度 / top cell / cell 字段 / rank 递增 / total 一致 / top_cell 一致 / 3-seed md5 / 反硬编码 A≠B。
