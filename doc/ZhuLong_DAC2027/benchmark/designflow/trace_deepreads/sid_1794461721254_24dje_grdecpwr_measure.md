# Deepread · 24dje · GrDecPwr 波形 ACT/PRE 边沿测量

- **session**: 1794461721254_24dje.messages.json
- **user / host**: dsgao @ 10.129.2.10
- **match_count**: 183 (kw cmos/analog/fsdb/waveview/netlist; waveform 域)
- **size**: 1.17 MB / 316 msgs / 10 user turns
- **trace 来源**: r636 peek 56 候选命中，留作 r637 B-track 合成候选；本轮 r637 scp + 合成落库
- **case_id**: EDA-Eval-DesignFlow-GrDecPwrMeasure-001（domain=waveform）

## 用户意图（逐轮）
- **U0**：`/rundata/.../drcpa_work_Rasim_XDec_2section_schematic{,_2}_ALPS/Sim/` 下各有 3 个 PVT corner 仿真，从波形文件抓 GrDecPwr：起始值（0.1*idle → 0.9*vwlp 上升时间 = ACT），再测 GrDecPwr 从 vwlp 释放到稳定电压的时间 + 稳定电压值（= PRE）。
- **U1**：信号是 `xi_r_xdecg0_0.xi_r_grdecx174g0.v(grdecpwr)`。
- **U2**：**修正 ACT 定义**——不是 0.1*idle→0.9*vwlp；是 grdecpwr **从 idle 电压上升到 vwlp 这个沿的 tr**。
- **U3**：PRE 后 grdecpwr **从 vwlp 下降到稳定电压台阶**的下降沿时间 tf。
- **U4**：schematic 和 schematic_2 两电路 ACT 后都拉到 vwlp，**同 corner 的 vwlp 应一致**。
- **U5/U6**：重新抓波形，给起始 idle 电位 + ACT tr + PRE 后稳定电压 + tf。
- **U7**：增加测量 PRE 后从 vwlp 到稳定的**真时间**（= t_stable − t_vwlp）。
- **U8**：数据整理成 *.csv。
- **U9**：重跑了 schematic_2 的仿真，再抓一版数据。

## 助手工具链
list_allowed_files 探 Sim 目录 → search_codebase/run_commands(grep GrDecPwr/vwlp) 被 agent-policy 拦 → read_files input.sp/stimu.sp 找信号层次 → editor 写 find_grdecpwr{1..7}.py/find_grdecpath2.py 追 R_GrDecX174G0 → R_XDecG0 → R_PhDecX4_UV 层次链 → skills(finesim-fsdb-reader) → probe_env 探 fscript/wv → fscript_probe/help/sig{1..5} 探信号枚举（`*GrDecPwr*` depth=0 命中 0，深层次需 depth）→ grdec_dump{1..3}/grdec_span/grdec_profile 用 fscript `signal`/`dlist` 抓 `v(xi_r_xdecg0_0.xi_r_grdecx174g0.grdecpwr)` 时间-电压样本 → fsdb_tools.py(run_dump) 封装 → analyze_full.py/analyze_coarse.py 粗扫 → **act_tr.py**(ACT 上升 tr 10-90% swing) + **pre_tf.py/pre_tf2.py**(PRE 下降 tf 90-10% swing) → **grdec_stats.py/grdec_single.py** 合并测量(idle/vwlp/stable/tr/tf/t_vwlp/t_stable/PRE_total) → editor 写 **GrDecPwr_measurements.csv**(2 design × 3 corner = 6 行) → U9 后重抓 schematic_2 → 最终 CSV。

## 关键产物（真实值）
列：`design,corner,idle_V,vwlp_V,ACT_tr_ns,PRE_stable_V,PRE_tf_us,t_vwlp_us,t_stable_us,PRE_total_us`
- schematic: FF idle2.6990/vwlp3.4000/tr2.701ns/stable2.7022/tf11524us；SS 2.5413/2.9200/4.442/2.5112/12237；TT 2.6277/3.2000/3.316/2.6159/16953
- schematic_2(最终): FF 2.1969/3.4006/2.824/2.2916/1407.5；SS 1.6335/2.9201/4.903/1.7467/2949.3；TT 2.0116/3.2000/3.499/2.1177/2609.9

测量语义（与助手实现一致）：
- idle = 首采样点；vwlp = max；stable = 末采样点
- tr = t(idle+0.9·swing) − t(idle+0.1·swing)，swing=vwlp−idle，**线性插值**取上升沿过零
- tf = t(stable+0.1·swing_f) − t(vwlp−0.1·swing_f)，swing_f=vwlp−stable，下降沿插值
- t_vwlp = 上升沿首次到达 vwlp；t_stable = 下降沿首次到达 stable；PRE_total = t_stable−t_vwlp
- 单位：tr=ns，其余=us
- vwlp 每 corner 一致(FF3.4/SS2.92/TT3.2，pvcc0.94)；idle/stable 跨 design 不同

## 可移植化（B-track 合成）
真实输入是 FineSim `.fsdb` 二进制（非便携，且依赖 /rundata 私有目录 + fscript license）。**合成 text-CSV**：把每个 (design,corner) 的 GrDecPwr 电压波形导成两列 `time_s,voltage_V`，结构 idle 平台→线性上升→vwlp 平台→线性下降→stable 平台，**非均匀采样**（使过零时刻落在采样点之间，强制线性插值）。

SUT 产通用 `grdecpwr_measure.py`（纯 stdlib CLI `<input_dir> <out_csv>`，walk `<design>/<corner>.csv` 树）。

## gotcha（check 设计依据）
1. **swing-relative 阈值**：v10=idle+0.1·(vwlp−idle)、v90=idle+0.9·(vwlp−idle)，**非**字面 0.1*idle / 0.9*vwlp（U0 字面读法被 U2 修正）。idle 远离 0 时两者差很大。
2. **线性插值取过零时刻**：非均匀采样使最近采样点与插值结果差 ~0.1-0.2ns，tol=1e-3ns 拦截最近采样点实现（core_removed 实测 tr 2.43 vs oracle 2.52 FAIL）。
3. **上升沿 vs 下降沿方向**：rise_cross `v[i-1]≤th≤v[i] & v[i-1]<v[i]`；fall_cross `v[i-1]≥th≥v[i] & v[i-1]>v[i]`。混淆方向 tf 全错。
4. **tf 用下降摆幅(vwlp→stable)的 90-10%**，基线是 stable 不是 idle；v_hi=vwlp−0.1·swing_f、v_lo=stable+0.1·swing_f。
5. **idle=首点 / vwlp=max / stable=末点**（平台语义，非 min/mean）。
6. **t_vwlp=上升沿首达 vwlp / t_stable=下降沿首达 stable / PRE_total=t_stable−t_vwlp**。
7. **单位**：tr×1e9(ns)，其余×1e6(us)。
8. **per-(design,corner) 分组 + 输出列序 + 字典序排序**。

## 三档输入
- visible_A：schematic/schematic_2 × FF/SS/TT（6 文件），idle/stable/rise/fall 接近真实量级。
- hidden_B：同 design/corner 标签，**idle 远离 0**（强摆幅相对阈值 gotcha）+ 不同时序，反硬编码 A。
- hidden_C：design 名换 designX/designY + 全不同数值，跨输入反硬编码 A/B（C 的 (design,corner) 集合≠A/B）。

## check.py
14 条独立条件 a-n：a zip+1py+py_compile；b py_compile；c 反硬编码 A 字面量(2.656/2.256/3.92/5.76/2.16/1.12)；d B 运行+表头；e B 行集合==oracle；f idle_V；g vwlp_V；h ACT_tr_ns(插值,拦截最近点/字面阈值)；i PRE_stable_V；j PRE_tf_us(下降摆幅)；k t_vwlp_us；l t_stable_us+PRE_total_us；m C 运行+行集合(designX/designY 反硬编码)；n C 全 8 字段==oracle。oracle 独立重读隐藏 CSV 自算，非文本相似、无硬编码期望串。

## 自验
- ref PASS 14/14
- 4 neg ALL FAIL **distinct labels**：empty→d / print_only(硬编码 B csv)→m(C 集合不符) / hardcode_a(硬编码 A csv 含 2.656)→c / core_removed(最近采样点)→h(tr 2.43≠2.52)
- §4.9 三假(empty/print/core)全 FAIL
- post-append 抽末行 check.py == reference check.py（无腐蚀），fresh ref PASS
- k_rationale = k_check = 14 ≥ 8 ✓

## 难度
B-track（synthesized text-CSV），waveform 域边沿测量子类（tr/tf + 平台检测 idle/vwlp/stable），与 r634 OLS 拟合 / r629 CSV 过滤 / r633 .md0 分析 / r630 DSPF 聚合 正交的新子类。L1（离线 stdlib on text-CSV），但 check 真跑候选(subprocess on B/C) + 独立 oracle + 反硬编码。
