# 7q6sq 深读 — junlingw GENGUI Monte Carlo mismatch + CCO

**trace**: 1795154837993_7q6sq / junlingw @ hfeg0pkn005 / mc=200 / 785 msgs / 2.5MB
**scan**: ssh_eda_search_20261123_064315 / keywords .lef:504;netlist:290;synopsys:77;hspice:74;pyaether:44;aether:39
**project**: /proj/drvqa/V0/workdir/junlingw/GENGUI/ — FineSim testbench tkinter GUI generator (finesim_tb_generator.py + fengine.py engine). 同 y9bh6 项目延续。

## 任务流（按 msg，节选与本 case 相关段）

1. msg 0-130: 学习 GENGUI 代码, 删无用文件, 修语法坏文件, 列保留清单, 删 Devices tab 末段.
2. msg 246-535: UI 排版/Source/Analysis/Options/Devices 多轮调整.
3. **msg 552-615** ★ **Monte Carlo mismatch + CCO** (本 case 选题):
   - U554 让 assistant 学 /apps/synopsys/SRB/finesim/V-2023.12-1/tutorial/MonteCarlo 库, 找 mismatch flag 和 CCO flag.
   - Assistant 全目录 grep: 无 "mismatch" flag, 无 "CCO" flag. 失配 = .local_variation; 全局漂移 = .global_variation.
   - U568/570 问 mismatch flag; U572 让把 MC mismatch + CCO 做成勾选放在 Process 页, 勾选输出对应 SPICE 语言.
   - Assistant ask_question: CCO 是什么? U574 答: "CCO 就是失配本身, 实际只要一个开关 (输出 .local_variation 失配块)".
   - 但 assistant 最终实现 **两个独立勾选**: Mismatch(local) + CCO(global). U598 确认 "两个".
   - msg 583 fengine.py 第一版 _mcmismatch (单 flag mc_mismatch, 同时输出 global+local).
   - msg 601 fengine.py 第二版 _mcvar (双 flag mc_mismatch + mc_global, 分别独立输出):
     ```python
     def _mcvar(self,L):
         mm=self.data.get("mc_mismatch",False); gg=self.data.get("mc_global",False)
         if not (mm or gg): return
         n=self.data.get("mc_mos_n","snps20N"); p=self.data.get("mc_mos_p","snps20P")
         L.append("* === MONTE CARLO VARIATION ==="); L.append("")
         L.append(".variation")
         if gg:
             L.append("  .global_variation")
             L.append(f"    nmos {n} vth0=0.03 u0=5 %")
             L.append(f"    pmos {p} vth0=0.03 u0=5 %")
             L.append("  .end_global_variation")
         if mm:
             L.append("  .local_variation")
             L.append(f"    nmos {n} vth0='1.2e-9/sqrt(get_E(W)*get_E(L)*get_E(M))'")
             L.append(f"+           u0='2.3e-6/sqrt(get_E(W)*get_E(L)*get_E(M))' %")
             L.append(f"    pmos {p} vth0='1.2e-9/sqrt(get_E(W)*get_E(L)*get_E(M))'")
             L.append(f"+           u0='2.3e-6/sqrt(get_E(W)*get_E(L)*get_E(M))' %")
             L.append("  .end_local_variation")
         L.append(".end_variation")
         L.append("")
     ```
   - msg 611 verify: 4 组合实测 — Mismatch only / CCO only / Both / Neither (none) 全部正确.
4. msg 616-636: Power 页 Type 列加下拉 (point/list/range).
5. msg 637-672: Corners topic 重构 — **同 y9bh6 case 已做, 跳过**.
6. msg 674-784: Netlist topic + stimulus 文件对话框.

## 选题: Monte Carlo variation block emitter

**reframe**: mc_variation_block_gen.py <spec.json> <out.txt> — 读 spec (mc_mismatch bool, mc_global bool, nmos_model, pmos_model, vth0_global, u0_global, vth0_local_sigma, u0_local_sigma, include_header) 输出 FineSim .variation 块:
- neither flag → 空
- only mismatch → .variation 包 .local_variation (每器件独立随机, 1/sqrt(W*L*M) 缩放)
- only global → .variation 包 .global_variation (工艺漂移 vth0/u0 固定值 %)
- both → .variation 包 .global_variation 在前 + .local_variation 在后

**near-dup 自查**:
- CornerBlockGenProduce-001 (y9bh6 同项目, corner 块 .lib/.alter/.temp/.param vvdd) — 不同输出/结构.
- MonteCarloDeckGen-001 (PVT deck 改 MC, AGAUSS + .tran SWEEP MONTE=N) — 不同方法.
- McVthSpVariantGen-001 (HSPICE .param delvto 替换) / McRonMismatch-001 (.md0 解析) / VtscMcDeckExplain-001 (deck 讲解) — 全不同.
无 near-dup ✓.

**case = EDA-Eval-DesignFlow-McVariationBlockGenProduce-001** (L1 纯 Python, k=14)
