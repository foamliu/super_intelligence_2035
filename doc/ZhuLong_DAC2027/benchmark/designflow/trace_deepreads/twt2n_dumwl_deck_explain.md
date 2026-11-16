# trace_deepread: 1794280510073_twt2n (yuyingc@hfeg0plg93)

- session: 1794280510073_twt2n.messages.json (15 msgs, mc=20, keywords netlist:29/hspice:15/schematic:11/mosfet:2/analog:2)
- host: hfeg0plg93 = 10.129.8.225, user: yuyingc
- domain: schematic_netlist (Finesim/HSPICE deck-grounded)

## 用户意图（逐字原文）
- U#0: 「帮我解释下这个脚本：/rundata/sim_cloud/CRG/mingyang/G5/DumWL_DRV/1bank.sp」
- U#11: 追问 — 粘贴 deck 的 vccz/vssz/VForceDummy + .param 块 + .data mydata 行，问「这些是啥意思」

两轮均为「提出需求/求解释」型（A 档选轮 ✓，非"已给根因/修复方案"轮）。

## 助手实际做了什么
1. list_allowed_files + read_files 读 1bank.sp（93 行）+ netlist.sp（377 行，cm0_ts_DumEdgeWL_Drv 电路）
2. 分块解释：工艺模型库(SS/bjt_tt/res_tt/nicap_tt/diode_tt) / Finesim 选项 / 电压文件 .inc(0.94v-40c) / netlist.sp / 电源 vccz+vssz / 激励 VForceDummy pwl / .param 块(pvcc=pvdd2h=0.94V, pvad2=pvblh*0.5) / .data mydata 2 行 sweep / .temp -40c / .Tran 10p 100ns / .probe level=10
3. 追问轮逐段解释电源(power=0 不计功耗)、激励源(pwl 时序)、直流参数(pvcc=pvdd2h 解析)、.data 扫描表(nf_P/nf_N1/nf_N2, 2 行 28-28-28/36-42-42)

## 源文件恢复
- 1bank.sp: /rundata/sim_cloud/CRG/mingyang/G5/DumWL_DRV/1bank.sp（.75 可直读，93 行/2337B，md5 7ec23a3ccd5ac4eeed1eb48d45f8d8dd）→ verbatim 作 asset A
- netlist.sp: 同目录 377 行（电路网表，cm0_ts_DumEdgeWL_Drv）— 本 case 不需（deck 解析只处理 1bank.sp 顶层结构）
- 电压文件 hspice0.94v-40c.voltage: /proj 权限拒绝、/rundata 映射不存在；assistant 解释 pvss 来自此文件(≈0V)。deck 中 pvss 未定义是 faithful 事实，parser 报告为"未在 deck 定义(.inc'd voltage 文件)"即可

## 合成 case
- case_id: EDA-Eval-DesignFlow-DumWLDeckExplainQA-001
- 形态: A 档 trace-faithful deck-grounded produce（写 deck_analyze.py 解析 deck → 结构化 JSON）
- 隐藏 B: FF 角/125C/0.88V，源名 vccc/vsss/VDummyForce，pwl 20/20.1/60.1/60.2ns，参数值全换+重命名(pvad2o→pvad2out, pvap2→pvap3)，.data sweep_tbl 4 列 3 行，.Tran 20p 200ns，.probe level=5 + 额外 p(*)
- check: 16 条独立条件，自验 16/16 PASS，5 负样本 + 退化(deleted-core)全 FAIL
