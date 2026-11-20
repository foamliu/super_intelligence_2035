# mwoue — miccao calibre DRC deck 优化 (physical_verify 域, A-档 faithful)

## trace 元数据
- session: `1791444783469_mwoue.messages.json` (miccao / hfeg0plg92, mc=401)
- size: 2118KB, 497 msgs (263 user / 234 assistant; tool_use: run_approved_command 77 / read_files 71 / editor 56 / list_allowed_files 44 / search_codebase 7 / run_commands 4 / check_deck 1)
- 关键字：calibre 3140 / pyAether 15 / schematic 8 / netlist 4
- trace-keyword 域 = physical_verify；实产 case 域 = physical_verify (calibre SVRF deck 文本优化)
- 选择理由：shard C physical_verify 域扩量；miccao 是新用户（用户多样性）；mc=401 中等；trace 是真 calibre DRC deck 优化闭环（读 DRC Log 分析报告 → 改 deck → bsub 跑 DRC 验证），可抽"报告→SVRF 编辑"独立子流。

## 主线（4 条 substantive user turn）
- T0 [idx0]（A-档 目标轮，逐字原文）：「根据/home/miccao/zl/rep/DRC_Log_Analysis_DDR5TOP_DFM0909.txt这份报告，将deck进行修改，只修改报告里的优化内容，然后将新deck放到/home/miccao/drc下，新deck叫newdeck」——提出需求，无根因/无修复方案=合规 A-档。
- T1 [idx156]：「去找对应gds，然后在这个路径下跑这个drc，使用bsub，queue用pv。实际看看有优化么」——跑 DRC 验证优化效果（goal，但属验证轮，非主任务说明）。
- T2 [idx366]：「为什么跑失败了」——根因询问（A-档排除）。
- T3 [idx487]：「跑完了吗」——状态询问（非 goal）。

assistant 主线：read report + calibreDFM.rule → 定位 4 条 rule → editor 改 newdeck（4 条优化）→ bsub 跑 baseline/opt DRC 验证（遇 wrapper _calibreDFM.rule_ SPC1 spec 重复冲突，末段清 wrapper 重跑，CalibreRRLog 显示 DRC 在跑但 trace 结束前未拿到 summary 对比）。

## 关键真实 artifacts（.75 上）
- `/home/miccao/zl/rep/DRC_Log_Analysis_DDR5TOP_DFM0909.txt` — DRC Log 分析报告（236 行 / 15013B）。3 条建议：
  - 建议1 (P0): R_C_MT2_F_01_M `A0 = M0C_Total WITH WIDTH < 0.102` (16853s, 全 run 83.4%) → 用 SIZE MT2_CORE BY 0.35 构造边缘条带预过滤 M0C_Total (mt2_outer/mt2_inner/mt2_edge/M0C_sub)。
  - 建议2 (P1): R_C_M0C_ENC_01_H / ENC_02_H / PCU_S_06_H 族 → SIZE PC_Total BY 0.1 缩小 INTERACT 中间层（FGC 3.57亿→千万级）。
  - 建议3 (P2 治本): M0C_Total/PC_Total 层次保留（架构级，建议在前两条验证后再评估=不在本轮 scope）。
- `/home/miccao/drc/calibreDFM.rule` — 原始 deck（3856 行 / 155188B）。
- `/home/miccao/drc/newdeck` — 金标优化 deck（3861 行 / 155511B，+5 行）。

## 金标 diff（orig → newdeck，4 条 rule）
1. R_C_M0C_ENC_01_H (655): `A1 = COPY M0_Final` → `A1 = M0_Final INTERACT (SIZE PC_Total BY 0.1 UNDEROVER)`
2. R_C_M0C_ENC_02_H (665): `A1 = COPY M0C_Total` → `A1 = M0C_Total INTERACT (SIZE PC_Total BY 0.1 UNDEROVER)`
3. R_C_MT2_F_01_M (777): `A0 = M0C_Total WITH WIDTH < 0.102` → 5 行 (mt2_outer/mt2_inner/mt2_edge/M0C_sub + `A0 = M0C_sub WITH WIDTH < 0.102`)
4. R_C_PCU_S_06_H (845-850): 引入 `M0C_near_PCU = M0C_Total INTERACT (SIZE PCU_CORE BY 0.1 UNDEROVER)`，3 处 `M0C_Total INTERACT PCU_CORE` → `M0C_near_PCU INTERACT PCU_CORE`

关键判别点：建议2 报告只给 ENC_02_H 一个改前/改后示例，但说族含 ENC_01_H + PCU_S_06_H。金标把预过滤推广到全族，按各 rule 的源层(M0_Final/M0C_Total)和缓冲层(PC_Total/PCU_CORE)适配——非字面替换。非目标 R_C_PCU_ENC_01_H (`COPY M0_Final`) 和 R_C_MT2_ENC_02_H 未改。

## 抽取的 case
- `EDA-Eval-DesignFlow-DRCKDeckOpt-001`（physical_verify，A-档 faithful，L1-boundary）
- 交付件 = submit.zip 含 `drc_deck_opt.py`（优化脚本: 读报告+deck→写 newdeck）+ `newdeck`（A 输出）
- 隐藏 B = report_B.txt + deck_B.rule（结构完全不同：层名 M1/M2/PC2/PCM，rule R_C_M1_F_02_M/R_C_M1_ENC_01_H/ENC_02_H/R_C_PCM_S_03_H，尺寸 0.25/0.05，width 0.08；含 2 条非族 rule R_C_M1_ENC_03_H/04_H 必须不改）
- check.py 17 labels (a)-(q)：A 的 4 条 rule 语义编辑(e-n) + 跨输入 B 击穿硬编码(o-q) + 一致性(d)。关键 discriminator：
  - (h)(j) ENC_01_H/PCU_S_06_H 族推广（naive 只改示例 ENC_02_H → fail h/j）
  - (m) 建议3 未应用（naive 应用 FLATTEN PCELL → fail m）
  - (o)(p)(q) 跨输入 B：B 用不相交层名，硬编码 A 的脚本会在 B 输出泄漏 MT2_CORE/M0C_Total/PC_Total BY 0.1 → fail q
- ref 自验：reference drc_deck_opt.py (报告驱动+族推广) out_A == gold（仅 1 行缩进 cosmetic 差），17/17 PASS；5 negatives 全 FAIL NEG_RC=0 (fake_empty→e / fake_print_expected→o / fake_core_deleted→e / naive_a_only_literal→h / naive_apply_suggestion3→m)；§4.9 (a)(b)(c) 三假全 FAIL。
- k_rationale = k_check = 17 ≥ 8 GATE PASS。

## L2/L3 debt
真 L2 需 live calibre DRC + DDR5TOP GDS + bsub pv 队列对 .75 sandbox 可达（GDS/queue 在 /proj/drcoa 集群，sandbox 不可达；单次 DRC 5.6h/16853s 超出 budget）。本轮 L1-boundary 静态校验 SVRF deck 文本变换。后续若开通集群访问可补 L2（跑 baseline vs opt deck 对比 REAL TIME 下降）。
