# Deepread: enh4y — RsCalc+AutoVia+PowerFill 收敛循环编排器

- **session**: `1786615396051_enh4y.messages.json` (548 msgs / 1.7MB / 2026-11-03)
- **user**: e0014566 @ hfeg0pkn001 (also seen as hfeg0plg58 / 10.129.35.82)
- **match_count**: 690 (C key=mc5; also parked in D ledger mc=690)
- **domain**: pg_layout (resistance-reduction flow on power grid)
- **status**: r938 revival (11-15 reaudit: run-existing no longer excluded) → case `EDA-Eval-DesignFlow-RsCalcConvLoopOrchestrator-001`
- **cross-shard note**: appears in BOTH C ledger (parked layout_virtuoso mc=511, note "run-existing rscalc flow") and D ledger (parked mc=690, "r538 peek REJECT run-existing"). r938 `mark --status claimed --force` then `mark --status case --force` cross-shard revival in C. Domain reassigned pg_layout (rscalc = power-grid resistance, not layout_virtuoso).

## 真实意图（trace 验证）

e0014566 构建一个 **RsCalc+AutoVia+PowerFill 电阻缩减迭代流**（Resistance-Reduction Flow）：

1. **RsCalc** 测 baseline 电阻（读 `*.rvn` 文件：col3-6 = `net_layer_x_y` key, col12 = R）
2. **AutoVia** 插通孔（cell-name 链式：`<orig>_via<i>`）
3. **PowerFill** 填电源轨（cell-name：`<orig>_opt<i>`）
4. **RsCalc 复测**，循环直到每个 check point 电阻降幅 ≥ `targetReduction` 或达 `maxIterations`

收敛判据（trace U# 多轮）：`R_i(p) <= R_0(p) * (1 - target)` 全点达标 → 整体收敛。

配置文件 4 个：`common.config`（targetReduction / maxIterations / origCellName）/ `rscalc.config`（runDir / pwrNets / metalOption）/ `run_autovia_config.il`（outLibName / coreNum）/ `run_powerfill_config.il`（workDir / runMode / speedMode）。

用户追问 RTEXT / RNODE / checkPoints 在 RsCalc 数据流中的作用（trace 中段）。

## Reframe（档 B fixture-driven）

agent 写 `rscalc_conv_orchestrator.py`：
- 解析 4 个配置文件 + `*.rvn` 电阻文件
- 逐轮评估收敛（per-checkpoint `R_i(p) <= R_0(p)*(1-target)`）
- 识别每轮 worst point（最慢收敛点）
- 判定 overall convergence / termination（converged 或 maxIterations_reached）
- emit JSON 报告 `{config_summary, baseline, iterations[], overall_converged, convergence_iter, final_cell, termination_reason}`

真实 EDA 工具（virtuoso / RsCalc / AutoVia / PowerFill）仅出现在 trace 叙事和 prompt_flow.md 中，grade 时不跑——纯文本解析 + 逻辑判定。

## env_A / hidden B 差异化

| 维度 | env_A (testa/austin_rscalc2) | hidden B (topb/austin_rscalc3) |
|---|---|---|
| nets | vdd1/vss1 (2) | vdd2/vss2 (2) |
| checkpoints | 5 | 4 |
| layers | M4/M5/M6 | M3/M5 |
| targetReduction | 0.5 | 0.4 |
| maxIterations | 5 | 3 |
| 收敛轮 | opt3 (53% reduction) | opt2 (45% reduction) |
| origCellName | testa | topb |

via 名集合、层名、net 名、cell 名全异——反硬编。

## k=12 断言

①config_summary ②rscalc.config ③autovia config ④powerfill config ⑤baseline checkpoints/max_R ⑥cell-name 链式 ⑦worst_point+converged 标志 ⑧overall_converged ⑨convergence_iter ⑩termination_reason ⑪checkpoints_converged 计数 ⑫顶层键 + final_cell

## 自验

- ref solve.py PASS 12/12 on env_A + hidden B
- 3 negatives: naive_empty → no-stdout 结构断言 (空输出), naive_print_A → tooth ①(A config 不匹配 B), neg_delete_core → tooth ⑤(baseline checkpoint count 0 vs 8) — 3 neg FAIL distinct teeth
- §4.9(a)(b)(c) 三假全 FAIL
- 3-seed sha256 deterministic `daabb98611126b11`

## 落库

- C.jsonl 576 → 577
- ledger_C enh4y: claimed → case (--force cross-shard)
- trace 覆盖率 596 → 597/2072
