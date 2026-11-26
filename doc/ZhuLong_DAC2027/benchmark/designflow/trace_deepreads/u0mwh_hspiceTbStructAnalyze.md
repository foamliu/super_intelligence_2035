# 深读笔记 · u0mwh · HSPICE testbench 结构分析

## trace 来源
- user: t0002614 @ hfeg0pkn001 (10.129.2.10)
- session: 1793681040407_u0mwh.messages.json (1.0 MB, 150 msgs, 6 user turns)
- match_count: 165 (kw: 851 netlist 142 schematic 14 hspice 7 pyAether 5 calibre 1 synthesis 1 lang:tcl)
- domain: eda_other (netlist 结构分析, L1-static)
- 上传 session: 1793065763835_y6liq (附件 .sp 实存于该 session uploads/)

## A档选轮（10/31 运维令 ②）
- **USER#1 (idx 0)** = A档任务说明（逐字原文）：
  > `analyze and detailed explain the structure of the netlist`
  > Attached: `TPC_Case1_Group1_BL4_28_D0_SenB_toc_1n.sp`
- ✅ 纯目标轮（提出需求，未给根因/未给方案）→ A档 eligible
- USER#2 = 扩展访问权限（grant /rundata dir）→ 不作任务说明（不是需求轮，是补充访问）
- USER#3-5 = 后续 bug-fix 轮（已给方向 "fix the bugs"）→ 不作 A档（B 档可用，本轮不做）
- USER#6 = 无关小问题（waveviewer rename）→ 不用

## 金标准（trace 末尾用户接受的结果）
- assistant A#45 完整结构分析（file-verified，基于真实读取 /rundata 全部依赖文件）
- 但 A档 faithful 仅用 USER#1 的附件 .sp 作为资产 → gold 取 A#4（仅基于 .sp 文件的结构分析，所有结论可由解析 .sp 单文件得出）
- A#4 关键结构事实（均可由 .sp 解析得出）：
  1. file_type = **testbench**（非 device netlist；含 .tran/.measure/.model/.lib/.inc，无器件实例）
  2. simulator = **FineSim**（`.option finesim_mode=spicead` + `.option finesim_bisection_output=1` + `.inc finesim_option`）
  3. syntax = **HSPICE-compatible**
  4. PVT: process=[ss, ss_Array], temp=-40, vcc=0.98；model_corners=[bjt_tt,res_tt,nicap_tt,diode_tt,tdv]
  5. analysis = **tran + bisection optimize sweep**：`.tran 10p 80n sweep Optimize=Opt1 Result=MaxVout Model=OptMod`
  6. tran: duration=80n, step=10p
  7. optimizer: variable=VTarget, method=Bisection, max_iter=12(Itropt), range=[0.0,1.0], model=OptMod
  8. measure: name=MaxVout, goal=0.7, window=[44n,57n], active_target=`xi_msaq_fbcc_28.xi_msaq_0.xi_msax256_cp00.xi_cxsa_1x4_0<63>.bla_local<2>`（48 条 .MEASURE 中唯一未注释的 1 条）
  9. includes: 11 个 .inc（netlistHeader/netlist/netlistFooter/msaq_plan4_5.spf_RCC/mblx528_edge_T1.spf_CC/tRAS_PWL/Pattern_Power/BG_ys_SLD1/G1_E_D0_TPC/ArrayRcSetting/D0_SenB）+ 7 个 .lib（模型库）
  10. key_params: toc=1.9n, pstrap=170, pvcc=0.98, ptemp=-40, ORG=4, pvblh=0.93v, pvad2=pvblh/2
  11. voltage_sources: [vad2 vad2! 0 dc=pvad2 power=0]（唯一真实器件元素）
  12. application_domain = **DRAM sense-amplifier margin**（msaq/fbcc/bla_local/blb_local/cxsa + VTarget bisection 命名）

## 合成计划
- task_id: `EDA-Eval-DesignFlow-HspiceTbStructAnalyze-001`
- 交付: `outputs/submit.zip` 含 `analyze_netlist.py` + `analysis.json`
- 接口: `analyze_netlist.py` 读 `config.json{"netlist_file": "<path>"}` → 解析 .sp testbench → 写 `analysis.json`（结构化 JSON）
- A（SUT 看）: 真实 `TPC_Case1_Group1_BL4_28_D0_SenB_toc_1n.sp`（156 行, 9.6KB）
- 隐藏 B: 合成的结构对立 testbench（ff/ff_Array, 125°C, VCC=1.1, tran 120n/5p, optimizer Vmargin/Bisection/Itropt=15/range[0,0.5], measure MinVout/goal 0.6/window[60n,80n]/target fbcc_30/cp01/cxsa_1x4_0<0>/blb_local<3>, 8 .inc）— B 的值在 f/g/h/j/k/l/m/n 8 条上全异于 A → 反硬编码
- gold = `analyze_netlist.py` config 驱动，泛化解析任意 HSPICE testbench（不硬编码 A 的值）
- check.py: 14 conds a-n，全部在 B 上 subprocess 真跑候选脚本后校验 B 的 JSON
- L1-static + subprocess（§4.2 真跑候选）

## 14 conds (a-n)
- a: zip 含 analyze_netlist.py + analysis.json
- b: py_compile analyze_netlist.py OK
- c: [B] subprocess 跑候选 exit0 + 合法 JSON（含顶层 keys: file_type/simulator/pvt/analysis_type/tran/optimizer/measure）
- d: [B] file_type == "testbench"
- e: [B] simulator == "finesim"
- f: [B] pvt.process 含 "ff"（非 A 的 ss）
- g: [B] pvt.temp == 125（非 -40）
- h: [B] pvt.vcc == 1.1（非 0.98）
- i: [B] analysis_type 含 "tran" + optimizer/measure 存在
- j: [B] tran.duration == "120n"（非 80n）
- k: [B] optimizer.variable == "Vmargin"（非 VTarget）
- l: [B] optimizer.method == "Bisection" + max_iter == 15（非 12）
- m: [B] measure.goal == 0.6 + window == [60n,80n]（非 0.7/44n-57n）
- n: [B] measure.active_target 含 "fbcc_30" + "blb_local<3>"（非 fbcc_28/bla_local<2>）+ active_count==1

## negatives (≥2 + selftest)
- naive_noop: 空实现 → fail 12 conds
- print_expected: 硬编码 A 的期望值 → 在 B 上 fail 8 conds (f,g,h,j,k,l,m,n)
- core_deleted: 删 measure/optimizer 解析器 → fail 6 conds (i,j,k,l,m,n)
- distinct failsets: {12, 8, 6} = 3 distinct ✓

## §4.9 三假提交
- (a) 空壳 analyze_netlist.py → fail b,c,all
- (b) 只 print 期望串（print_expected）→ fail 8
- (c) 参考解删核心（core_deleted）→ fail 6
