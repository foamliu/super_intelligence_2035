# 深读笔记 · 3123n · CML 带宽扩展与均衡技术公式手册

## trace 元数据
- session: 1793669959152_3123n  (lvyy @ hfeg0pkn005 = 10.129.2.14)
- mc=576, domain=spice_sim, agent=lead, 447 msgs / 3.25MB
- keywords: netlist:2079; hspice:1436; schematic:657; synopsys:266; transistor:240; mosfet:86; bandgap:12
- 已造 case（同 trace）: CmlPvtAcReport-001 (PVT AC 表征, user#372), CmlMirrorSweepAnalysis-001 (电流镜 sweep, user#218/234)
- 本轮新造: **CmlBwExtensionHandbook-001** (带宽扩展公式手册, user#318) — 与已造两条意图不同, 非重复

## 用户真实意图 (msg#318 verbatim)
「写出以下相关公式: CML电路加上NCE电路的公式；源退化CTLE；gate-bias OTA，求增益带宽和传输函数等各种分析，包括零极点。还有其他什么可以用来提高带宽的方式也列出来。」

= explain-Q&A → 产出一份带零极点/传输函数的"带宽扩展公式手册"。用户在前序多轮已把电路调好（V6f 基准: gm=1.15mS, R=2.9k, ro_in≈7k, CL=26fF, A0=2.34/7.4dB, f3dB=3.0GHz），本轮要的是把三大带宽扩展技术（NCE/源退化CTLE/gate-bias OTA）+ 其他方法的公式系统整理。

## agent 回答要点 (assistant#319, 3975 chars)
按"〇基线 → 一源退化CTLE → 二NCE → 三gate-bias OTA → 四其他 → 五推荐"结构给出:
- 〇基线 CML: A_dm(s)=-gm·(R‖ro)/(1+s(R‖ro)CL); A0=2.34, 主极点3GHz, GBW=7GHz, CMRR=24dB
- 一源退化CTLE (Rs∥Cs): 完整 TF; A0_degen=gm·RL/(1+gmRs); wz=1/(RsCs); wp,deg=(1+gmRs)wz; boost=1+gmRs; **设计: Rs=RL/A0_target−1/gm=425Ω, Cs=1/(2π·Rs·fz)=250fF (fz=1.5GHz), boost=1.49**
- 二NCE: Ceff=Cc(1−Av); Av>1→负电容; **设计: 目标BW×1.5→CL_eff=17.3fF, Cc=8.6fF/(Av−1)=43fF (Av=1.2)**; 稳定性: NCE环路带宽>3×目标BW
- 三gate-bias OTA: Zout(s)=Reff(1+s/ωz)/(1+s/ωp); ωp<ωz→感性; 稳定性: gm_L·A0·Reff<1; 电阻负载需改电流源+CMFB
- 四其他: shunt peaking (m=2/3最大平坦 BW×1.72, 本电路L=146nH不可集成), T-coil (BW×2.83), NIC, feedforward, distributed
- 五推荐: ①CTLE ②NCE ③gate-bias OTA

## 合成方案 (A档 trace-faithful + cross-input guard)
- 任务=写 cml_bw_handbook_generator.py(workdir,out_dir) 读 circuit_context.json 现场计算各技术设计取值 → cml_bw_handbook.json (7 顶层键)
- A=V6f电路 (trace verbatim 参数); hidden B=NMOS diff pair 不同参数 (gm=0.62mS/RL=4.2k/CL=45fF/目标6dB/5.5GHz) → 计算值全异 (Rs 425→492, A0 2.34→1.81, Cs 250fF→147fF, Cc 43fF→80fF)
- check.py 24 断言: a0-a6 前置(zip/compile/hidden/跑/JSON/键) + a7-a9 baseline数值对B + a10-a12 源退化Rs/boost/Cs对B + a13 零点公式 + a14 NCE公式 + a15 Cc对B + a16-a17 OTA稳定性/感性 + a18 shunt peaking m=2/3 + a19 ≥4方法 + a20 ≥3推荐 + a21 A-leak + a22 B-grounding + a23 确定性 + a24 baseline TF
- 自验: ref 24/24 PASS; 4 negs (empty/print_only/hardcode_a/core_deleted) 全 FAIL
- k_rationale == k_check == 24 ✓
