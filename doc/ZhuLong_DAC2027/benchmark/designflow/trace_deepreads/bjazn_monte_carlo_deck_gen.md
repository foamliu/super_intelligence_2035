# 深读笔记 · bjazn · MonteCarloDeckGen (spice_sim A-档)
trace_source: user=gallopc host=hfeg0pkn005 (10.129.2.14) session_file=1793790756982_bjazn.messages.json mc=296 sp=61
trace size: messages.json 1.85MB / 296 msgs / uploads 12 files
date: 2026-11-04 ~ 11-06 (user uploads 11-04, last activity 11-06)

## 用户原始意图（A-档 task = 提需求轮，逐字原文）
USER#1 (mode=act): `怎么把这个文件修改成一个蒙特卡罗仿真` + attachment `sim_driver_x20_adj.sp` (3927B FineSim XDec driver deck)
USER#3 (mode=act): `帮我把改之后的存储到路径下，然后你的蒙特卡罗给予的随机量是什么，如果我想仿真把温度工艺和电压都随机呢`
→ 纯需求：把一个 FineSim PVT corner deck 改成蒙特卡罗仿真，且要把温度/工艺/电压都随机化。未给根因/未给修复方案 ⇒ A-档合格。

## 错误轮（不可作 A-档 prompt，但示根因）
USER#4: `报错：ERROR! incomplete or unsupported sweep statement '200' (sim_driver_x20_adj_mc.sp:55)` → FineSim 不支持 `.dc var gauss ...` 语法（HSPICE 写法）
USER#6: `现在这个蒙卡仿真随机了那些值，sigamaflag的值有哪些，决定什么，200这个数值设置的意思是什么`

## assistant 工具链 / 关键产物
1. 读 sim_driver_x20_adj.sp（PVT 三 corner FF/TT/SS via `.if pcor_*==1`，sigmaflag=1.36 固定，.tran 1p 2us，netlist/stimulus/measure 全 .inc）
2. **首版（错误）**：用 `.dc mc_sigmaflag gauss 0 1 200` 做 MC → FineSim 报 `incomplete or unsupported sweep statement`（.dc gauss 是 HSPICE 写法，FineSim 不支持）
3. 查 `finesim_ug.txt` (1.2MB FineSim user guide 第11章) → FineSim MC 正确写法 = `AGAUSS(mean,sigma,limit)` 参数分布 + `.tran ... SWEEP MONTE=N`
4. **终版 `_gen_mc_final.py`** 产两个正确 MC deck：
   - `sim_driver_x20_adj_mc.sp` (mcA): TT corner base + 3 AGAUSS 随机参量 (mc_sigma→sigmaflag 工艺, mc_temp→ptemp 温度, mc_pvint→pvintmc 电压) + `.tran 1p 2us SWEEP MONTE=200`
   - `sim_driver_x20_adj_mc_var.sp` (mcB): `.Variation` 块 (`.Global_Variation` / `Temp temp=...AGAUSS` / `Parameter sigmaflag=Perturb(...)`) + `.tran ... SWEEP MONTE=200`
5. 写入 `/proj/ddgoa/V0/simdir/.../sim_driver_x20_adj_mc.sp` + `_mc_var.sp`

## 金标准（用户实际接受）
= `_gen_mc_final.py` 产出的 mcA (AGAUSS + SWEEP MONTE) + mcB (.Variation + SWEEP MONTE)。核心正确性：FineSim MC 必须用 AGAUSS/Perturb + `[SWEEP MONTE=N]`，不能用 `.dc gauss`。

## case 设计
- case_id: EDA-Eval-DesignFlow-MonteCarloDeckGen-001
- domain: spice_sim / track: A-faithful / level: L1（离线 Python 复刻，不真跑 finesim）
- 交付: 通用 `gen_monte_carlo.py <input.sp> <outdir>` → 产 `<base>_mc.sp` (AGAUSS) + `<base>_mc_var.sp` (.Variation) + `diagnosis.md`
- A=真实 sim_driver_x20_adj.sp；hidden B=sim_driver_alt_b.sp（FF primary, 不同 netlist/sigmaflag=2.10/.tran 2p 5us/电压）
- check.py 12 条独立断言(a-l)：真跑候选 on B，解析产出的 .sp 结构
