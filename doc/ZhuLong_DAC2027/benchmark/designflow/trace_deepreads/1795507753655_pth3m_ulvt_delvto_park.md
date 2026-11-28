# Deepread: 1795507753655_pth3m (joeyl @ hfeg0plg80, mc269, spice_sim)

**Source**: trace_ledger --shard B next → .75 summary.tsv awk 精筛 hspice-dominant non-joeyl... 实际选了 joeyl opamp 族 pth3m (mc269, netlist:1153 hspice:102 opamp:24)。
**Fetched**: scp hfeg0plg80:/home/joeyl/.cline/data/sessions/1795507753655_pth3m/... → 698999B / 178 msgs / 15 user msgs。

## 真实用户意图
joeyl 用现成工具 `/home/joeyl/ulvt_delvto/reduce_vth.py` + `config.cfg` 给 DDR4 V0 多张 FineSim/HSPICE netlist (Bias/CML_C2C/Solo_Divider/WCKTop/Divider_and_C2C) 里 pulvt_ckt(PMOS)/nulvt_ckt(NMOS) 两个 ULVT 模型的实例语句末尾追加 `_delvto=<值>` 改 Vth。迭代多轮: vth=-0.2 → -0.1 → 0.05，每次重抽 netlist 都再替换。

## 关键物理 gotcha (msg 89)
用户中途纠正「发现个非常关键的问题，对 pmos，Vth 应该 +0.2!」—— HSPICE Vth 符号约定: PMOS Vth 本身负值，要降 |Vth| 须加 **正** delvto；NMOS Vth 正值，要降 Vth 须加 **负** delvto。修复后工具用 `delvto_by_model: nulvt_ckt:-0.2, pulvt_ckt:+0.2`（PMOS+/NMOS- 异号）。

## 工具机制 (reduce_vth.py, 已 .75 取回完整源码)
扫描 netlist → 找 X 开头实例语句(支持 + 续行) → 语句 token 命中 pulvt_ckt/nulvt_ckt → 末尾追加 `_delvto=<值>`(已有则替换数值, 幂等) → 跳过 .subckt 定义/注释/非 X 行 → 行尾 $/// 注释前插入。非 ULVT 模型(nlvt/plvt/nrvt_ckt)不动。

## 判 parked 不合成 (本 shard 已 6+ 同族 case)
**已落库同族 case**（同 user joeyl / 同 reduce_vth.py 工具 / 同 PMOS+/NMOS- 符号 gotcha）:
1. `EDA-Eval-DesignFlow-DelvtoPmosNmosSignPatch-001` (session 914l2) — **完全相同 PMOS/NMOS 符号 gotcha**
2. `EDA-Eval-DesignFlow-DelvtoNetlistMod-001` (w8iq4) — summary 明含「关键纠正 msg 89: 对 PMOS Vth 应 +0.2, NMOS 才 -0.2」
3. `EDA-Eval-DesignFlow-DelvtoNetlistShift-001` (nld2d) — prompt 明含「关键：PMO...」同 gotcha
4. `EDA-Eval-DesignFlow-DelvtoInjector-001` (i7nlb, joeyl) — 同工具 reduce_vth.py
5. `EDA-Eval-DesignFlow-DelvtoNetlistModifier-001` (6pm3i, joeyl) — 同工具
6. `EDA-Eval-DesignFlow-ULVTDelvtoNetlistMod-001` (mhqy7, joeyl) — 同工具

本 trace pth3m = 同 user / 同工具 / 同 PMOS+/NMOS- 符号 gotcha，**与 #1/#2/#3 高度重叠**。按「不凑 weak case」纪律 park，避免 duplicate。

## 状态
台账 `mark parked` (note: dup_of_joeyl_delvto_family)。无新 case 交付。DEBT:0。
