# Deepread: 1793061831395_wgl5g — VAMAgent fullchip DDR6 finesim.prof cell 推荐

## Trace metadata
- **session**: 1793061831395_wgl5g
- **user**: e03179 @ hfeg0plg15 (172.16.8.191)
- **mc**: 20 (analog:180; netlist:116; transistor:103; lvs:66; waveview:19; verilog:18; aether:10)
- **domain**: analog_context (pure-D)
- **agent**: Cline (vam-agent skill)
- **msgs**: 18, 247KB
- **tier**: A (trace-faithful, prompt=verbatim U#0)

## User intent (verbatim U#0)
「帮我哪些cell可以仿真加速，日志路径为.../finesim.prof」
- 经 vam-agent 技能入口；用户对 fullchip DDR6 PrimeSim/FineSim profile 做仿真加速 cell 推荐

## Agent 行为
- 调用 `profile_analyzer.py` 解析 finesim.prof
- 对 fullchip DDR6 全片 4718 个 subckt 按 solving_cost 排序 + 8 类分类
- 产出推荐报告：25 个推荐模拟 cell（VAMAgent 可建模）+ 120 个数字 wrapper（gen_bnk_va PWL 建模）
- top PWL 占比: array16g_psd0 69.69% / bnkgtopx1 65.72% / r_rasbnklogic 51.32%
- top 模拟 cell: rndiff_3t_ckt 2.39%

## 8 类分类规则（从 profile_analyzer.py 提取）
1. parasitic_rc — 名含 `parasiticrc`，跳过
2. trim — 名含 `tr`/`trim`，跳过
3. MOS 原子 — 名含 {ntn,ptn,ntn_lv,ptn_lv,ntn_m,ptn_m,ntk,ptk,nfet,pfet,rn}，前缀 `ntk_`/`ptk_`
4. pass gate — 名含 `passgt`
5. 数字锁存/门 — 名含 `lat`（latch）/`and3` 等
6. 数字标准单元 — 名含 inv/nand/nor/buf/aoi/oai/mx/mxi/dlyg/or2/and2/xor/xnor/dlybias/d_
7. 数字 wrapper — device 占比 Dev% = device_solving_cost/subckt_solving_cost < 2% 且子实例 > 5
8. 推荐模拟 — 不属 1-7，按 solving_cost 降序推荐

## 关键障碍
- raw finesim.prof 在 .75 上跨用户权限拒绝（e03179 own）→ 无法直读
- 解决: 用 trace gold_report.txt 真实 top-cell 名/数值 + 从 skill dir scp profile_analyzer.py 学 prof 格式 + 分类规则 → 合成自包含 finesim.prof (A=31 subckt)

## Case 产出
- **case_id**: EDA-Eval-DesignFlow-VamCellReco-001
- SUT 写 `cell_recommender.py` 复现 8 类分类 → `cell_reco_report.json`
- check.py 35 断言 (B×16 + B2×16 + anti-hardcode A_TOKENS + submit/sut)
- hidden B=29 subckt (6 reco/8 std/2 MOS/3 gate/1 pass/4 wrapper/4 trim/1 rc)
- anti-hardcode B2=24 subckt (4/5/4/1/3/3/2/2)
- 自验: ref PASS 35/35；3 neg FAIL NEG_RC=0；3 退化 FAIL；A_TOKENS 13 个 ref 源 0 泄漏
- k_rationale=k_check=35≥8

## 资产
- A (visible): finesim.prof (31 subckt, 真实 top-cell 名)
- B (hidden): hidden/finesim.prof (29 subckt, 系统变换)
- B2 (anti-hardcode): hidden/finesim_b2.prof (24 subckt, 全参异化)
