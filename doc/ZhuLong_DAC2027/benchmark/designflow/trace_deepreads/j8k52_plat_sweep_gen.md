# Trace Deepread: j8k52 — plat_lvlshfts 全组合 sweep deck 生成

**Session**: 1794557662253_j8k52
**User**: hairuizh
**Host**: hfeg0pkn001
**mc**: 10 (spice_sim)
**Trace source**: .75 scp `/home/hairuizh/.cline/data/sessions/1794557662253_j8k52/1794557662253_j8k52.messages.json` (37 msgs)
**Pool**: summary_1114.tsv (ssh_eda_search_20261114_184938)

## 真实任务

仿真工程师 hairuizh 在 DDR2 level-shifter pre-sim characterization 流中，需要把 `plat_lvlshfts_base.sp` 从部分覆盖扩成**全组合遍历**：

- `sel_plat ∈ {0,1,2,3}` (原 0,1,2 → 补 3)
- `sel_cond ∈ {0,1,2,7,8,9}` (原 0,1,2 → 补 7,8,9)
- `sel_lvl ∈ {0,1,2}`

通过 HSPICE `.alter` 块实现每个组合一个 alter。

用户原话：「修改 plat_lvlshfts_base.sp，使其中包含 sel_plat=0,1,2,3; sel_cond=0,1,2,7,8,9; sel_lvl=0,1,2」

## Case 泛化

把"改 deck"泛化成"写可复用 sweep 编排脚本 `plat_sweep_harness.py`"，从 L1 (改一份 deck) 升为 L2 (写通用 harness)：

1. 读 runset config (JSON: plats/conds/lvls + DUT + measures + spec)
2. 读 model.sp (按 corner 组织的 .lib)
3. 生成全组合 `.alter` HSPICE deck (cartesian product, baseline + N-1 .alter)
4. 真跑 HSPICE
5. 从 `.lis` 逐 alter 抠测量 (`.mt0` 只存末 alter — 核心陷阱)
6. 产出 per-combo 报告 JSON (verdict/worst_corner/overall_pass)

## 合成 case: EDA-Eval-DesignFlow-PlatSweepGen-001

- **A runset**: 72 combos (4 plats × 6 conds × 3 lvls), spec 8.0ns → overall_pass=True
- **Hidden B**: 24 combos (3 × 4 × 2), spec 1.2ns → overall_pass=False (16 fail/8 pass)
- **Cross-input guard**: A baseline tpdr=0.438ns ≠ B baseline tpdr=0.702ns
- **13 conditions** (a-m): 含静态 deck 检查(m)、cross-input guard(j)、确定性(k)
- **模式仿** PVTalterChar-001 (proven case, multi-.alter + .lis per-alter parse)

## 自验结果 (.75 real HSPICE)

- ref 13/13 PASS
- B: n_alters=24, worst=plat2_cond7_lvl1 (tpdr=7.604ns), 8pass/16fail/0not_met
- A: n_alters=72, overall_pass=True, worst_tpdr=6.43ns
- GT single-corner B combo0 EXACTLY matches harness (tpdf=0.3755117, tpdr=0.7016006)
- 4 negatives all FAIL ≥1 condition
