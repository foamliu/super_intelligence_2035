# 深读笔记 — 6tiy7 · DFF setup/hold 时间表征

## trace_source
- session_file: `1792386804961_6tiy7.messages.json`
- user: kaixuanx · host: hfeg0pkn001 · mc=250 · 369 msgs · 1.27 MB
- 工具命中：schematic:1541 / netlist:740 / hspice:38 / finesim（FineSim ALPS）/ waveview:1
- domain: **characterization**（DFF 建立时间 tSU / 保持时间 tH 表征，timing char 子技能）
- ledger: shard B，已 claim → status=deepread（synthesis DEBT next round）

## 真实用户意图流（逐字原话要点）
- T0（U#0）: context summary 指向 `4PGen_Sleep_Static_TSPC_DFF_schematic_ALPS/results`，分析 TSPC DFF 的 setup/hold 仿真结果。
- U#9「这里的保持时间为什么还是 0ps，是不是分析错数据了」+ 给出重跑命令（`SIM=finesim -i TSPC_DFF_sh_combined.sp`）。
- U#75「我的意思是之前你给的 combine 仿真跑完了，为什么不能计算建立和保持时间，我要球放在一个 testbench 里跑」。
- 后续多轮围绕：单 testbench 同时测 tSU/tH、独立扫 setup/hold 边界、修正测量窗口。

**A 档候选原话（提出需求轮，未给根因/修复）**：
- U#9「这里的保持时间为什么还是 0ps，是不是分析错数据了」← 提出问题，未给方案 ✓ 可作 A 档任务说明。
- U#75「为什么不能计算建立和保持时间，我要放在一个 testbench 里跑」← 提出目标 ✓。

## 真实子技能（distinct check vs 已有 B case）
- 已有：InvTripDelay=inverter tpd/vtrip；NetlistTranDeck=NAND tpd tran deck 生成；TxRonSize=IO driver Ron 线性区；CtleAcChar=CTLE 频域 .ac；ButterflyCurve=SRAM SNM DC；FineSimModelScopeFix/NoRefCktFix/BistOscRccReorder=FineSim elaboration 错误修复。
- **本条 = DFF setup/hold 时间表征**：扫 D-to-CLK skew → 测 tSU（D 提前 CLK 的最小余量，Q 仍正确捕获）+ tH（D 延后 CLK 的最小余量，Q 不误翻）+ tCQ（CLK→Q 传播延迟）。**shard B 首个 setup/hold timing char case**，distinct 子技能 ✓。

## 真实设计参数（便携化锚点）
- 工艺：45nm LP（ntn_lv_pc60 / ptn_lv_pc60）— foundry PDK 不可移植 .75
- 工作条件：VDD=1.1V，2.4GHz（CLK 周期 Tclk=416.7ps），tt_25_1p1 corner
- 负载：3fF（fan-out 4）
- 实测（.75 不可直接复现，但作 GT 量级参考）：tCQ≈44ps(orig)/42ps(opt)，tSU≈25/24ps，tH<60ps

## 便携化方案（level-1 Shichman-Hodges + FineSim/HSPICE .tran）
- DFF 拓扑：取**静态 master-slave DFF**（2 个锁存器 + 2 反相时钟）或 **TSPC DFF**。便携选 master-slave（8-10 个 level-1 MOS，行为可预期）。
- level-1 NMOS/PMOS：`.model nch nmos level=1 kp=50u vto=0.7 lambda=0.05` / `.model pch pmos level=1 kp=20u vto=-0.7 lambda=0.05`（A）；B 用不同 kp/vto/lambda + 不同 W/L + 不同 VDD/Tclk/CL。
- testbench：CLK 方波（Tclk），D 在指定 CLK#4 沿前/后带可变 skew 翻转，`.tran`，`.measure` 测 Q 是否在该 CLK 沿正确捕获 D。
- setup 扫描：D 下降沿相对 CLK#4 提前 t_skew_setup（从大到小扫），找 Q 仍能稳定到 D 新值的临界 tSU。
- hold 扫描：D 在 CLK#4 后延迟 t_skew_hold 翻回（从大到小扫），找 Q 在**下一个 CLK 沿之前**不误翻的临界 tH。

## 核心陷阱（烤进 check.py ≥8 条独立条件）
1. **hold 测量窗口跨越下一个 CLK 沿 → 假 tH=0**（trace 的主 bug）：
   - 错：`Q_peak = MAX V(Q) from=t_clk4 to=t_clk4+500p`，但 Tclk=416.7ps ⇒ 窗口包含 CLK#5，Q 被 CLK#5 正确捕获 ⇒ 永不违例 ⇒ tH=0（假）。
   - 对：窗口 `to=t_clk4+Tclk-50p`（CLK#5 之前）。
   - check.py 断言：候选 measure 脚本的 hold 窗口上界 < t_clk4+Tclk（不含下一沿）；判分器独立重跑用正确窗口得 tH>0 且匹配 ref。
2. **单 tskew 联动 setup+hold 边沿（跷跷板）→ 两边界都够不着**：
   - `setup_margin + hold_margin = const` ⇒ 一次扫描无法同时逼近两临界点。
   - check.py 断言：候选 testbench 用**两个独立参数** tsetup/thold（不联动）；setup 扫描能逼近 tSU 临界、hold 扫描能逼近 tH 临界。
3. **setup 窗口/方向**：tSU = D 提前 CLK 的最小时间（D 在 CLK 前变），Q 仍捕获。check.py 断言 setup 扫描方向正确 + tSU 匹配 ref ±容差。
4. **tCQ 传播延迟**：CLK→Q 延迟匹配 ref ±容差。
5. **跨输入守卫 A/B**：A 与 B 的 tSU/tH/tCQ 不同（不同 VDD/Tclk/W/L/CL），naive_hardcode_a 硬编 A 值在 B 击穿。
6. **真跑候选**：判分器独立重跑 FineSim/HSPICE 于 B，解析 .mt0/.lis，断言输出结构（tSU/tH/tCQ 字段）。
7. **SI 后缀解析**（.measure 数值带 f/p/n 后缀），naive_raw_float bare float() 错数量级击穿。
8. **name-agnostic**：候选脚本不含 A/B 特定节点名字面量。

## 候选交付物（reference 解）
- `char_gen.py`（CLI `<params.json> <dff.netlist> <out_dir>`）：读 params（VDD/Tclk/skew 范围/CL）+ netlist → 生成 setup 扫描 testbench + hold 扫描 testbench（独立参数 + 正确窗口）→ 跑 FineSim `.tran` → 解析 `.mt0`/`.lis` 的 .measure（SI 后缀 parser）→ 写 `result.json`{tSU, tH, tCQ, hspice_ran, ...}。
- `check.py`：独立临时目录解 submit.zip → 校验 char_gen.py 结构（窗口/独立参数/name-agnostic）→ 独立重跑 B → 解析 → ≥8 条 a-? 断言。

## A/B GT（待 .75 真跑标定）
- A：VDD=1.1V, Tclk=416.7ps(2.4GHz), Wn=0.5u/Wp=1u, Ln=Lp=0.13u, CL=3fF, kp_n=50u/kp_p=20u/vto=0.7。
- B：VDD=1.0V, Tclk=500ps(2.0GHz), Wn=0.8u/Wp=1.2u, Ln=Lp=0.15u, CL=5fF, kp_n=80u/kp_p=30u/vto=0.6/lambda=0.04（跨输入 diff 显著，tSU/tH/tCQ 均不同）。
- 真 GT 数值须 .75 端到端跑出后填入 check.py（容差 ±5-10%）。

## negative 候选（≥2，全 FAIL 互异）
- naive_empty：不跑仿真，result.json 全 None → 击穿真跑断言。
- naive_print_expected：硬编 A 的期望 tSU/tH/tCQ 字符串 → 跨输入 B 击穿 + 真跑断言。
- naive_hardcode_a：硬编 A 数值 → B 击穿（跨输入守卫）。
- naive_window_bug：故意用 t_clk4+500p 窗口（含 CLK#5）→ tH=0 假 → 击穿 hold 窗口断言 + tH>0 断言。
- naive_seesaw：单 tskew 联动两边界 → 两临界够不着 → 击穿独立参数断言。
- naive_raw_float：bare float() 解析 .measure → SI 后缀错数量级 → 击穿数值断言。

## 断言清单预案（k≥8，与 check.py 一一对应）
`k 条断言：① char_gen.py 真调仿真器（hspice_ran/finesim_ran=true，产 .mt0/.lis） ② hold 测量窗口上界 < t_clk4+Tclk（不含下一 CLK 沿，防假 tH=0） ③ setup/hold 用两个独立参数（非单 tskew 跷跷板联动） ④ setup 扫描方向正确（D 提前 CLK） ⑤ tSU 匹配 B 真值 ±容差 ⑥ tH>0 且匹配 B 真值 ±容差 ⑦ tCQ 匹配 B 真值 ±容差 ⑧ SI 后缀 parser 正确（.measure 数值 f/p/n 后缀） ⑨ name-agnostic（不含 A/B 节点名/数值硬编） ⑩ 跨输入守卫 |B-A|/A>5%（naive_hardcode_a 在 B 击穿） ⑪ 判分器独立重跑 B 得 'Successfully Completed' ⑫ result.json 字段结构齐全{tSU,tH,tCQ,...}`

## 下轮第一件事（DEBT:1）
- 用本笔记合成 `EDA-Eval-DesignFlow-DffSetupHoldChar-001`：assets/reference/hidden/negative → .75 端到端自验（ref PASS + §4.9 三假 FAIL + negatives FAIL 互异）→ 追加 `EDA-Eval-DesignFlow_B.jsonl` → `mark --status case --case-id ...` → 日报。
- 优先复用本笔记的陷阱清单写 check.py（hold 窗口 bug + 跷跷板 + 跨输入 + SI 后缀 是 4 个独立的「杀手断言」）。

## 合成尝试日志 (2026-11-04 shard B) — BLOCKED, NOT delivered, NOT in jsonl

本轮进行了实质性合成工作（非 deepread-only），但 DFF 表征在 .75 上未能干净标定，
按质量闸门（ref 必 PASS selftest）**未追加 jsonl，未 mark --status case**。WIP 与
详细阻塞分析见 `designflow/_wip_dff_setup_hold/BLOCKER.md`（含可复用的
char_gen_ref.py / uploader_dff.py / dff_*.sp / params_*.json + 三种 DFF 拓扑的
标定数据 + 下轮具体路径 A/B/C）。

**核心阻塞**：level-1 Shichman-Hodges DFF 存在根本张力——快（Q 满摆但 tSU/tH~0，
退化）vs 慢（加内部电容让 tSU/tH 落在可扫范围，但 Q 只到 0.33-0.38V 中间电平，
从不达到 0.7*vdd，捕获失败）。三种拓扑均试：TG（反馈接错→修→s1 因 Cs1 太慢）；
TG 减 Cs1（s1 仍 0.30V，体效应阈值降）；NAND（无阈值降，但 clk_b 缓冲带 10-15fF
太慢→Q 卡 0.23-0.38V 中间电平）。hold 扫描 Q 随 th 单调上升但不过阈值→tH 亦不可提取。

**下轮第一件事**：按 BLOCKER.md 路径 A（推荐）——用安全 level-1 sizing 让 Q 先干净
满摆（D=1 tsu=200p → Q=vdd±5% 验证），再用 sub-ps 细扫提取 tSU/tH；若 tH 真为 0，
trap(o) 改源码正则检查（非值）。或路径 B（.75 上拉真 PDK DFF .subckt 黑盒表征）。

ledger 6tiy7 维持 `deepread`（未升 case）。DEBT 顺延。
