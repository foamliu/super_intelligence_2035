# Deepread — sid 1785498030478_eduxu (e0014566 @ hfeg0plg58, mc306, layout_virtuoso)

## Trace
- session: `1785498030478_eduxu` (253 msgs, 507KB messages.json)
- user: e0014566, host: hfeg0plg58
- tools命中: virtuoso 161, calibre 75, cellview 12, skill 8, schematic 6, pyAether 3
- 用户逐字首轮: `read the prompt_flow.md and do the job in it.`
- 真实工作目录: `/home/e0014566/test_layout_rscalc_flow/`
- 真实 flow workDir (Virtuoso产物): `/proj/train/AI_Virtuoso/ver/rscalc_flow/e0030265`

## 真实任务
执行 **Layout Resistance Optimization Workflow**（prompt_flow.md，10699B，原文资产）：
RsCalc(基线) → AutoVia(加 via) → PowerFill(电源填充) → RsCalc(复测) → Compare & Iterate。
config: `layout_rscalc_flow.config` — process=cxmt10G4plus, libName=austin_rscalc2, cellName=testa,
pwrNets="M1 vdd vbb", **target_reduction_pct=30, max_iterations=3**, useExistGds=Yes.
真实 .rvn: rscalc/testa/RSDB_{M1,vdd,vbb}/*.rvn（vdd 4 check points: 16.716/14.028/11.592/7.224；M1/vbb 仅 header 无行）；rscalc_verify/testa 同结构。真实复测 .rvn 与基线数值相同（0% reduction → 真实未达标）。

## gold 7 块
- G1 任务：read prompt_flow.md → 执行 5 步流程编排
- G2 config 解析：flow_control.config → target_reduction_pct, max_iterations, cellName
- G3 .rvn 解析：LV+RSView:NodeList,3 header + CSV 行，电阻在第 12 列
- G4 reduction 数学：reduction = (baseline - optimized)/baseline*100
- G5 迭代判定：all_meet→SUCCEEDED 停；非 all_meet 且 iter<max→ITERATE；非 all_meet 且 iter==max→STOPPED
- G6 baseline 不变量：每轮 baseline 始终用第1步原始基线（不得用上轮 optimized 替代）
- G7 best_iteration：平均 reduction 最高的那一轮

## 合成决策（B-档 synthesized）
真实 .rvn 只 vdd 有行且 verify==baseline（0% reduction，场景过窄）。为覆盖 SUCCEEDED/ITERATE/STOPPED 三分支，合成 3 nets（vdd/vss/vbb）多 check point 多轮 .rvn fixtures：
- A (target30/max3): iter1 vdd10%/vss40%/vbb5%→ITERATE, iter2 25/55/20→ITERATE, iter3 35/60/32→SUCCEEDED(best3)
- B (target40/max2): iter1 30/40/30→ITERATE, iter2 38/42/38→STOPPED(best2) [hidden, 判分用]
- B2 (target20/max2): iter1 25/30/25→SUCCEEDED(best1) [hidden, 击穿 always-STOPPED]

## 交付
- EDA-Eval-DesignFlow-RsCalcFlowOrch-001 (layout_virtuoso, L3, B-档)
- 交付件: rscalc_flow_orchestrator.py (CLI: <flow_dir> → JSON)
- check.py: 12 条断言 (a-l), k=12=k_check≥8 GATE PASS
- 自验: ref PASS 12/12 ✓; 4 neg(empty/print_expected/always_succeeded/reset_baseline)全 FAIL ✓; §4.9(a)(b)(c)全 FAIL ✓; test==disk roundtrip 10100B ✓
