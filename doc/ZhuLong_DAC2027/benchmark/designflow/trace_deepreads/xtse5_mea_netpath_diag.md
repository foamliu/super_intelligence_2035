# 深读笔记 · 1793234226913_xtse5 · shanliny @ hfeg0pkn001 (10.129.2.10) · spice_sim A-档候选

## trace 元信息
- session: 1793234226913_xtse5 (56 msgs, 3.5MB — 含 3MB DSPF 内嵌附件, >2MB ⇒ 本轮深读 + DEBT:1 合成)
- user: shanliny (pkn001, 10.129.2.10)
- mc=43, spice tools: hspice 6 / netlist 7 / schematic (ratio .462)
- trace_source: {user: shanliny, host: hfeg0pkn001, session_file: 1793234226913_xtse5.messages.json, match_count: 43}
- 工具调用: run_approved_command 21, editor 5, search_codebase 1, run_commands 1

## 用户原话（A-档任务说明 = 首轮逐字原文）
> 为什么我sp文件中的mea语句没法提取相应的数值？
> --- Attached files ---
> [io_d0_template.sp → .../uploads/io_d0_template.sp]
> [HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.dspf.TYPICAL_25 → .../uploads/...dspf.TYPICAL_25]

后续用户轮：
- msg20「继续啊」(催促, 非需求)
- msg30「但是我看后仿文件中确实是xxsa呀」(用户反驳, 指出后仿文件里是双 x, 但**未给根因/修复** ⇒ 仍是 CLEAN A-档)

**A-档合规判定 (规则 #2)**：用户只给症状(mea 提不出数值)+反问, 未指出根因、未给修复方案 ⇒ CLEAN ✓

## 附件（真实原文, 不脱敏）
1. **io_d0_template.sp** (2698B) — HSPICE/FineSim SRAM sense-amp (SA) characterization testbench
   - `.lib '/proj/lacaa/V0/model/current_PF_v0d1_Rev03/hspice/model.lib' ss_mos_varactor_fs`
   - `.inc 'HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.dspf.TYPICAL_25'`
   - `.temp -40`, `.param high=0.675 diff=0.1`
   - SAEB/DLPCHB/BLPCHB pulse 激励, BL_D/BL_T/BLB_D/BLB_T 位线 PWL
   - **6 条 .measure tran**:
     - `t_outb_r when v(gbl[1]) val='high*0.9' rise=1`
     - `v_blb_fall1 find v(xtop.xxsa[1].mpmyrc:s) at=t_outb_r`  ← **双 x, 小写**
     - `v_bl_fall1 find v(xtop.xxsa[1].mpmyrt:s) at=t_outb_r`
     - `v_dv param='v_blb_fall1 - v_bl_fall1'`
     - `v_df_sat_sac find v(xtop.xxsa[1].mnmsac:d,xtop.xxsa[1].mnmsat:d) at='t_outb_r-100p'`
     - `v_df_bl_blb find v(xtop.xxsa[1].mpmyrt:s,xtop.xxsa[1].mpmyrc:s) at='t_outb_r-100p'`
     - `v_df_b_s param='v_df_bl_blb - v_df_sat_sac'`
   - `.tran 0.1n 2100n`
2. **HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.dspf.TYPICAL_25** (3.0MB) — DSPF 提取网表
3. **0_run** (2058B) — bsub finesim 运行脚本 (`bsub -n 32 -R "span[hosts=1]" -q lacaa_sram "finesim io_d0_template.sp -o io_d0_template/ -np 32"`)
4. **check_mea.py / check_dspf.py / check_dspf2.py / check_dspf3.py** — 用户让助手写的排查脚本

## 根因（助手最终结论 msg49/53/55）
DSPF 文件**同时存在两种命名**：
| 位置 | 实例名 | 举例 |
|---|---|---|
| **器件实例行** (文件末尾 L49626+ 器件定义) | `XXSA[1]` (双 x) | `XXSA[1].MPMYRC` `XXSA[1].MNMSAC` |
| **网表连接行** (`*|I` 节点/互连定义) | `XSA[1]` (单 x) | `XSA[1].MPMYRC:s` `XSA[1].MNMSAC:d` |

- DSPF 中 **net 的正式名字是 `XSA[1].MPMYRC:s` (单 x)** (定义在 `*|I` 连接行)
- 器件实例用了 `XXSA[1].MPMYRC` (双 x) (定义在器件行)
- 用户 .sp 的 .measure `find v(xtop.xxsa[1].mpmyrc:s)` 用**双 x** = 器件实例路径, **不是 net 名**
- `.measure find v()` 查的是 **net/node 名称**, 而非器件实例名 ⇒ 名字不匹配 ⇒ 提不出数值

## 修复（金标准 = 修正后的 .sp）
将 6 条 .measure 的节点路径从**双 x 器件实例路径**改为**单 x net 名路径**：
- `v(xtop.xxsa[1].mpmyrc:s)` → `v(xtop.xsa[1].mpmyrc:s)`
- `v(xtop.xxsa[1].mpmyrt:s)` → `v(xtop.xsa[1].mpmyrt:s)`
- `v(xtop.xxsa[1].mnmsac:d,xtop.xxsa[1].mnmsat:d)` → `v(xtop.xsa[1].mnmsac:d,xtop.xsa[1].mnmsat:d)`
- `v(xtop.xxsa[1].mpmyrt:s,xtop.xxsa[1].mpmyrc:s)` → `v(xtop.xsa[1].mpmyrt:s,xtop.xsa[1].mpmyrc:s)`
- 保留所有 .measure 的 param 算术 (v_dv, v_df_b_s) 与 when/find/at 结构不变

## 合成计划（下轮 DEBT:1 合成）
- **case_id**: EDA-Eval-DesignFlow-MeaNetPathDiag-001
- **domain**: spice_sim (A-faithful, L1 — 离线解析 DSPF net 名 + 修正 .sp .mea 路径)
- **prompt** (A-档): 用户原话逐字「为什么我sp文件中的mea语句没法提取相应的数值？」+ task_brief(3 行接口)
- **交付 (DoD)**: `outputs/submit.zip` 含 `io_d0_template_fixed.sp` (修正后) + `diagnosis.md` (根因说明)
- **assets A**: io_d0_template.sp (broken, 双 x .mea) + dspf_fragment.sp (重建的 DSPF 片段, 含 `*|I` 单 x net 定义 + 末尾双 x 器件行, 覆盖 xsa[1].mpmyrc:s / xsa[1].mpmyrt:s / xsa[1].mnmsac:d / xsa[1].mnmsat:d 等节点)
- **hidden B**: 不同实例名 (如 `xxsb[2]`/`xsb[2]`, net `BLB_T[3]` 等) + 不同 .mea 数量/算术, A≠B
- **check.py k≥8 断言** (逐条对应):
  ① zip 含 io_d0_template_fixed.sp + diagnosis.md 两文件齐全
  ② fixed.sp 保留原 .measure tran 的 6 条结构 (t_outb_r / v_blb_fall1 / v_bl_fall1 / v_dv / v_df_sat_sac / v_df_bl_blb / v_df_b_s)
  ③ fixed.sp 的 .mea 节点路径**不含双 x** `xxsa[1]` (器件实例路径)
  ④ fixed.sp 的 .mea 节点路径用**单 x** `xsa[1].mpmyrc:s` 等 net 名
  ⑤ 每个 .mea 引用的 net 名**在 DSPF `*|I` 连接行中存在** (真跑候选: 解析 dspf_fragment 的 `*|I` 行做名字匹配)
  ⑥ .measure 的 param 算术 (v_dv = v_blb_fall1 - v_bl_fall1; v_df_b_s = v_df_bl_blb - v_df_sat_sac) 保持不变
  ⑦ .tran/.temp/.param/.lib/.inc 语句保持不变 (只改 .mea 路径)
  ⑧ diagnosis.md 明确指出根因 = .mea 用器件实例路径(双x) 而非 net 名(单x), DSPF `*|I` 行定义单 x net
  ⑨ (随机化) 在 B 上随机抽 3 个 .mea 节点, 3 seed 验证 net 名匹配结论一致
  ⑩ 负样本: empty_stub / print_only / core_deleted(保留双x不改) 全 FAIL
- **negative/**: empty_stub (空 .sp), print_only (只打印诊断不改 .sp), keep_doublex (保留双 x 不修) + negative_selftest.py
- **§4.9 三假提交**: empty_zip / print_only / ref_core_deleted 全 FAIL

## 深读完成时间: 2026-11-07 17:4x · DEBT:1 合成待下轮
