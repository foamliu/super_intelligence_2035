# Deepread: 1794970604490_f1olf — 2-step Sense-Adj Temp-Control 门级网表重构

- trace_source: user=dsgao, host=hfhds201 (also hfeg0pkn001/003/plg58/87/08/96 round-robin), session=1794970604490_f1olf, match_count=318
- domain: schematic_netlist (D) — netlist:726 / schematic:504 / verilog:400 / rtl:153 / synthesis:98 (含 drc:1188 但主导意图=网表重构非 DRC)
- keywords: drc:1188;netlist:726;schematic:504;aether:408;verilog:400;rtl:153;synthesis:98;lvs:63
- ledger: claimed r1617 (status=claimed, synthesis pending — DEBT next round)
- trace: 241 msgs / 909KB, per-session path `/home/dsgao/.cline/data/sessions/1794970604490_f1olf/1794970604490_f1olf.messages.json` (.75 本地直读，无需 ssh round-robin)

## 用户真实意图（原话脉络）
1. `分析一下这个电路功能` — R_2stepSenseAdjTempCtrl_0822.netlist
2. `做真值表自动化验证`
3. `手动切LT -> LT 怎么理解` / `检测到LT，那无论SW是否使能，输出什么code` / `SW有什么实质的作用`
4. `我想把default的输出为LT code, 有什么优化建议` （注：最终保留默认 HT，仅讨论）
5. `把方案A直接改写成一份新的净表形式（gate-level连线版本）`
6. `输出那种可以导入到aether可以生成电路的网表` ← **核心交付意图**
7. n2s（netlist-to-schematic）命令跑 cdl2emy 报错（手写网表太乱、自创 stdcell）
8. `还是乱，你生成RTL代码我综合成门级的verilog netlist再导入进去` ← **流程转向：RTL→DC综合→干净门级网表→n2s**
9. `给我RTL代码` / `在这个路径生成RTL，~/drcpa/rtl`
10. `~/drcpa/scripts/dc/run_synth.tcl 依照这个写一个相应的综合脚本`
11. `约束一下，要求standcell用的最少` / `可用MUX` / `禁用aoi门`
12. DC 综合报错迭代（set_dont_use -reset 语法、target lib 缺 NOR/AND、AOI 禁用）
13. `cm1_ro_2StepSenseAdj_HT<5:0>,..._LT<5:0> 这是总线，用MUX进行二选一总线，怎么设置`
14. 贴出综合后 netlist（nand2Lx1+invLx1 版；后 nor2Lx1+invLx2 版）
15. `查了一下，叫mx2Lx1有这个standcell` / `修改综合脚本，我再综合` → 最终 netlist（invLx2+nor2Lx1 实现 2:1 mux）

**真实交付**：把一个 2-step sense 温度自适应调节码选择器电路，从乱网表重构为「RTL → Synopsys DC 综合 → 干净门级 verilog netlist（受限 stdcell 集、最小化/禁 AOI/用 MUX）→ 可导入 Aether n2s 生成 schematic」。核心可判分对象 = **门级 netlist 的逻辑正确性 + 结构合规性**。

## 电路功能（assistant 已推导 + 真值表自动验证 16 组全 PASS）
**顶层**：`R_2stepSenseAdjTempCtrl_0822`（DRAM 数字控制，2-step sense amplifier 温度补偿调节控制 = 6 位温控 mux）

**端口**：
| 端口 | 方向 | 含义 |
|------|------|------|
| Ts_HT / Ts_LT | in | 高/低温温度传感器标志 |
| cm1_ro_SenseTempEn (SE) | in | 感测温度调节总使能 |
| cm1_ro_SenseLTHTSw (SW) | in | LT/HT 手动切换开关 |
| cm1_ro_2StepSenseAdj_HT[5:0] | in | 高温模式 6 位调节码 |
| cm1_ro_2StepSenseAdj_LT[5:0] | in | 低温模式 6 位调节码 |
| cm1_ro_2StepSenseAdjo[5:0] | out | 选出的 6 位调节码 |

**核心逻辑**（化简 + 门级模型双路验证一致）：
```
HT_option = SE ? (Ts_HT | ~(Ts_LT | SW)) : 1   # SE=0 → 默认 HT（失效安全）
Adjo[i]   = HT_option ? HT[i] : LT[i]           # 6 位逐位 2:1 mux
```

**真值表**（SE,Ts_HT,Ts_LT,SW → 选中档）：
- SE=0, * → HT（默认）
- SE=1, Ts_HT=1, * → HT（高温优先）
- SE=1, Ts_HT=0, Ts_LT=1, * → LT
- SE=1, Ts_HT=0, Ts_LT=0, SW=1 → LT（手动切 LT）
- SE=1, Ts_HT=0, Ts_LT=0, SW=0 → HT（无温度标志+未切换）

**原网表 stdcell**：invLx1/invLx4, nor2Lx2/nor2CSx1, nand2CSx1, mxi2LVx2（2:1 mux = 两 tristate 反相器）
**用户期望综合 netlist stdcell**：受限集 — inv / nor2 / nand2 / mx2Lx1（2:1 MUX）；禁 AOI；最小化数量
**最终综合 netlist**：invLx2 + nor2Lx1（用 nor+inv 实现 2:1 mux 逻辑）

## case 合成 plan（下轮交付，task_id = TwoStepSenseAdjNetlistProduce-001）

**形态**：synthesized-reframe — 真实用户意图（温控 mux 门级网表重构）reframe 为通用 `produce_gate_netlist(spec)->verilog` + hidden-B 反硬编码。deliverable=outputs/submit.zip(gen_netlist.py + 对 spec_A 的 .v)。**LIVE-NA**（门级 netlist = 文本交付，check.py 解析 netlist + 逐门逻辑仿真对真值表 + 结构约束校验，无真实 EDA 工具二进制依赖；n2s/aether 不在 .75，不强求 L2.live）。judge_layers=[L0,L1]，无 check_live。

**A (visible)** spec_A.json：
- 6 位总线，端口名同原电路（HT/LT/Adjo/SE/SW/Ts_HT/Ts_LT）
- 逻辑：HT_option = SE ? (Ts_HT | ~(Ts_LT|SW)) : 1，默认 HT
- 允许 cell 集：{inv, nor2, nand2, mx2(2:1 MUX)}；禁 AOI/OAI
- 约束：最小化 cell 数

**hidden B**（token-structurally 不同，反硬编码）：
- 8 位总线（A=6）；端口名全换（TempHot/TempCold/EnCode/SelOverride/CodeHot/CodeCold/CodeOut）
- 逻辑变体：默认 **LT**（A=HT），**LT 优先**（A=HT 优先），enable 低有效（A=高有效）
- ⇒ A 的硬编码 netlist 在 B 上真值表全错

**check.py ≥12 conds**（逐条可独立 FAIL）：
- a zip 含 gen_netlist.py + .v
- b py_compile gen_netlist.py
- c gen 在 spec_A 产 .v 含 module 声明 + 全端口（A 档可用性）
- d .v 只用允许 cell 集（无 AOI/OAI/禁用门）
- e .v 结构合法（每 gate 例化端口连接完整、无悬空、wire 声明齐）
- f 门级逻辑仿真：对 spec_A 全 16 输入组合 (SE,Ts_HT,Ts_LT,SW) 逐位仿真，输出==真值表期望（核心逻辑正确性）
- g 真值表行：SE=0 → 默认档（HT）
- h 真值表行：SE=1,Ts_HT=1 → HT 优先
- i 真值表行：SE=1,Ts_LT=1 → LT
- j 真值表行：SW=1 → LT override
- k 输出位宽==6
- l 反硬编码：B 运行 — gen 在 hidden spec_B 产 .v，门级仿真对 B 真值表（8 位/默认 LT/LT 优先/低有效 en）全对
- m 反硬编码：B .v cell/结构与 A 不只是改名（B 用不同位宽/不同 mux 拓扑）

**负样本**（≥3 + selftest 全 FAIL）：
- empty：空 zip / 无 .v → fail c
- print_only：gen 直接 echo 一份固定 netlist 串（A 真值表碰巧过，B 全错）→ fail l
- core_deleted：gen 产结构合法但 mux 永远选 HT（删 LT 路径）→ fail i/j
- hardcode_a：把 A 答案 netlist 硬编码常量串 → B fail l

**test_rationale** = `13 条断言：①zip含gen_netlist.py+.v ②py_compile ③A档module+端口齐全 ④只用允许cell集 ⑤结构合法无悬空 ⑥A全16输入组合门级仿真==真值表 ⑦SE=0默认HT ⑧SE=1&Ts_HT=1→HT优先 ⑨SE=1&Ts_LT=1→LT ⑩SW=1→LT override ⑪输出位宽==6 ⑫B运行门级仿真==B真值表 ⑬B非仅改名`

**trace_source metadata**：{user:"dsgao", host:"hfhds201", session_file:"1794970604490_f1olf.messages.json", match_count:318, real_task_summary:"2-step sense 温度自适应调节码选择器门级网表重构：分析电路功能+真值表验证，再 RTL→Synopsys DC 综合→受限 stdcell 干净门级 verilog netlist（禁 AOI/用 MUX/最小化）导入 Aether n2s"}

**自验**：ref gen 产 A .v → check.py 门级仿真 PASS 16/16；§4.9 trio (empty/print_only/core_deleted) + hardcode_a 全 FAIL；negative_selftest 全 FAIL；SKIP_RUN=1 workdir 无泄漏；3-way sha sync；k_check=13=k_rationale=13。

## 备注
- 域归属：D（schematic_netlist）。虽含 drc:1188，但主导意图=网表重构/综合非 DRC 校验；netlist+schematic+verilog 主导。✓ D 线。
- .75 可达：本会话 open_session 秒级、f1olf trace 本地直读 /home/dsgao/.cline/sessions/（无 ssh round-robin 摩擦，比 r1614 的 0yu3c/eig3b 顺畅）。
- 本轮预算耗于候选 grep + trace 取回 + 深读 → **DEBT: 1 deepread 未合成**，下轮按本 plan 合成 TwoStepSenseAdjNetlistProduce-001。
