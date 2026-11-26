# Trace deepread — sid_1793867708362_0t51l — NetlistViewSpiceldSwap-001 (spice_sim A-faithful L1)

**source**: hfhds201 local `/home/<u>/.cline/data/sessions/1793867708362_0t51l/1793867708362_0t51l.messages.json` (58 msgs / 172 KB, user=tzuo, mc=58). NOT in 11-05 snapshot (hfhds201 isn't ssh'd to itself) — discovered via 11-07 08:0x hfhds201 local pool rescan (292 unscouted, scout top 25, deeplook).

## 用户意图（verbatim, A-档任务轮 = U4）
> 我想让你帮我写个脚本可以把指定路径下的netlist的Imsaq_1和Imarray_2从spiceld改成schematic，并在代码后面加上***ky_halfdensity方便备注

- 纯需求轮（给目标 + 方法：改视图 spiceld→schematic + 末尾加备注），未给根因/修复 ✓
- U0–U3 为上下文铺垫（mmsim.ini 配置 / netlist 路径 / Imarray_schematic 名单 / GlobalBind LibraryList），非任务轮。
- domain = spice_sim（finesim 网表视图编辑：mmsim.ini 抽网表 + Netlist_SpfBA_*.postsim）。

## trace assistant 真实探索发现（grounding for reference）
1. netlist 是符号链接 → `/rundata/drcpa_sim/V0/simdir/finesim/workdir/tzuo/simulation/Netlist_SpfBA_20261104PM/netlist.postsim`（~35 万行）。
2. **实例带 `X` 前缀**：`XImarray_35 ...`、`XImsaq_33 ...`（按词边界匹配 `Imarray_2` 不命中，因前一字符 `X` 也是词字符）。
3. **多行结构**：实例首行 `X<name> <nodes...>`，续行以 `+` 开头；**model/subckt 引用是最后一个续行（`+` 行）的末尾 token**。
4. **spiceld vs schematic 区分**：spiceld 视图的 model 带 `_spiceld` 后缀（如 `array11Meg_E_CCR_spiceld`、`msaq_E_spiceld`）；schematic 视图不带后缀（`array11Meg_E_CCR`、`msaq_E`）。**spiceld→schematic = 去掉 `_spiceld` 后缀**。
5. **关键歧义**（trace 在此停下问用户）：`Imsaq_1` 实际引用 `msaq_O`（**无** `_spiceld` 后缀），即 Imsaq_1 当前可能并非 spiceld 视图 → assistant 末轮「规律已经摸清，但发现一个关键歧义，需要你确认后再写脚本」，**未产出最终脚本**。
   - 本 case 用**合成 A/B 网表**消除该歧义：所有目标实例的 model 均**明确带** `_spiceld` 后缀，任务良定义。合成网表忠实复刻真实格式（X 前缀 + `+` 续行 + `_spiceld` 后缀 + .SUBCKT/.ENDS 块）。

## 金标准说明
trace 未产出最终脚本（停于歧义确认）；reference 脚本 `change_spiceld_view_ref.py` 基于上述**真实 trace 探索发现**（X 前缀 / `+` 续行 / `_spiceld` 后缀剥离）合成，实现 U4 verbatim 需求，并在合成 A/B 网表上自验 PASS。prompt = U4 逐字原文（A-档 trace-faithful）。

## case 合成
- ID: `EDA-Eval-DesignFlow-NetlistViewSpiceldSwap-001` · spice_sim · A-faithful · L1
- 交付: 通用 `change_spiceld_view.py <netlist> <out> <inst>...`（便携 Python，只做视图编辑+备注追加）
- A = netlist_A.sp（m384_Meg 4 实例：XImsaq_1→msaq_E_spiceld / XImarray_2→array11Meg_O_spiceld 为目标；XImarray_0 schematic 非目标；XImsaq_33→msaq_O_spiceld 非目标）
- hidden B = netlist_B.sp（不同：5 实例 / 不同 model / 不同 node 名 / XImsaq_1→msaq_O_spiceld / XImarray_2→array11Meg_E_Edge_Top_CCR_spiceld）A≠B ✓
- reference + check.py k=13 断言 a-m + negative/ 5 stub
