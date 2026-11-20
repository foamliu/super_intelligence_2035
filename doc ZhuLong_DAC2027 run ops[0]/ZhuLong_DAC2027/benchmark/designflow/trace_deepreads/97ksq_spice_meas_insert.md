# 97ksq 深读 — SPICE .meas 语句插入（schematic_netlist）

## 元信息
- session: `1793849641832_97ksq.messages.json`
- user: jiangbaol @ hfeg0pkn001 (10.129.2.10)
- mc=636, tools: netlist 144 / schematic 113 / hspice 6 / calibre 5 / pyAether 5 / cellview 1
- size: 1,035,030 B, 198 msgs, 7 user turns
- 资产权限: /proj/m2701/V0_DDR4/simdir/finesim/workdir/jiangbaol/... → e0031982 **无读权限**（Permission denied）→ B-grade synthesized

## 用户轮（逐字原文，仅掩 key/token）
- U#0 (msg#0): `**error** (/proj/dejoa/V0/.../DqIb_2stg_DfeM6V2.spf.TYP_98_RCC:25) duplicated subckt definition 'DqIb_2stg_DfeM6V2'. Please refer to option 'redefsub' if you prefer simulator to treat this as a warning rather than error. 该报错应该如何修改` → Q&A（用户已贴根因，**不用作 A 档任务说明**）
- U#1 (msg#2): `如何设置option可以实现hspice仿真输出波形中每个层级包含该层级所有net的信号` → Q&A
- U#2 (msg#7): `/proj/m2701/.../004_onlySlicer_delay_m2701.sp 帮我检查下这个.sp为什么无法probe slicer_out以及slicer1st_out，并改正` → 改正任务（用户已指出根因方向）
- **U#3 (msg#33) [本 case 选用]**: `/proj/m2701/V0_DDR4/simdir/finesim/workdir/jiangbaol/simulation/001_slicer/Slicer_testbench/004_onlySlicer_delay_m2701.sp 在该.sp中添加measure语句，实现如下功能： 1.测量XI7整体电源功耗,采样时间与.sp内其他功耗时间一致; 2.测量1.53后，ldfedata第一个下降沿达到vvdd-0.36的时刻； 3.测量2.时刻时outn_stg1与outp_stg1的电压 生成的.sp放在原.sp路径下，若产生过程文件或仿真文件放在/proj/m2701/V0_DDR4/simdir/finesim/workdir/jiangbaol/simulation/001_slicer/Slicer_testbench/010_ZL_process` → **提出需求轮**（用户只描述目标，未给根因或修复方案）✓ A 档可用
- U#4 (msg#55): `... 调节该.sp中double tail slicer输入管M1,M2及第一级尾电流管MP1尺寸...使t_ldfe_first_fall时刻，V_outn_stg1_at与V_outp_stg1_at的最大值不超过480mV...给出满足所述需求并使该时刻ldfe_dm绝对值最大的输入管及尾电流管尺寸，并仿真核验迭代出最佳方案` → 复杂 sweep 优化（L3，依赖 U#3 的 measure）
- U#5 (msg#148): `在原需求基础上，重新sweep...将条件ldfe_dm绝对值最大改为slicer1st_out绝对值最大`
- U#6 (msg#163): `将输入管类型由pulvt_ckt替换为plvt_ckt，再sweep,目标与最近一次需求相同`

## U#3 assistant 工具链（msg#34–54）
1. msg#34 `run_approved_command` python-runner grep .sp 内已有 measure/power 行 + XI7 pin map
2. msg#35 [TOOL_RES] 列出 .inc / .probe Cur_slicer1st='i(XI7.XI_DqIbSAHFM6IP.xmp2.main)' 等
3. msg#36–38 `read_files` 读取 .sp 第 210–285 / 155–210 行，定位已有 power-avg 窗口 `From='5n-32*UI' TO='5n'`、`.tran 1p 5n`、vcc! 由 vvcc 驱动、XI7 supply pin = inh_vcc
4. msg#40–43 `editor` + `run_approved_command` shell-runner: cp 原 .sp → `/home/jiangbaol/004_onlySlicer_delay_m2701.sp`（281 行，沙盒策略禁写 /proj）
5. msg#44–45 `editor` 在第 222 行后插入 `* ZL-added measure block`（lines 224–242）
6. msg#50–51 `editor` refine power measure 为 probe-alias + AVG 惯用式（与 Cur_slicer_* 一致）
7. msg#54 [TEXT] 给出 cp 命令把生成 .sp 拷回 /proj 原路径（沙盒禁写 /proj）

## U#3 金标准（agent 实际产物，已 scp 到 /tmp/gold_sp.sp 303 行）
插入的 measure block（lines 224–242，原 .sp 222 行 `Cur_slicer_latch_avg` 之后）:
```spice
* ============================================================================
* ZL-added measure block
* ----------------------------------------------------------------------------* [1] XI7 overall power-supply consumption (from vcc! / XI7.inh_vcc)
*     sampling window identical to the other power/current avg measures above
.probe XI7_vcc_cur = 'isub(XI7.inh_vcc)'
.meas tran I_XI7_vcc_avg  AVG  XI7_vcc_cur           From='5n-32*UI'  TO='5n'
.meas tran P_XI7_vcc_avg  AVG  'VVDD*XI7_vcc_cur'    From='5n-32*UI'  TO='5n'
*
* [2] time when ldfedata (=LDFEDataEr) first falling edge reaches vvdd-0.36, after 1.53ns
.meas tran t_ldfe_first_fall  WHEN  v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
*
* [3] outn_stg1 / outp_stg1 voltage at the [2] instant
.meas tran V_outn_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outn_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
.meas tran V_outp_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outp_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
* ============================================================================
```

## 关键 .sp 结构（用于 B-grade 复刻 A deck）
- header: `****** HSPICE Default Option for Block Level Simulation`
- .inc / .lib 行（mock 路径）
- params: `VVDD=0.875`, `DR=25.2E9`, `UI=1/DR`, `VREF=0.125`, `SWING=0.020`, `tdly=5n`
- supply: `vvcc vcc! 0 VVDD`, `vVVDD VVDD! 0 VVDD`
- `.tran 1p 5n`
- `.probe TRAN V(*) i(*) isub(*)`
- 已有 probe block 揭示关键信号全路径:
  - `.probe Cur_slicer1st = 'i(XI7.XI_DqIbSAHFM6IP.xmp2.main)'`
  - `.probe Cur_slicer_latch = 'isub(XI7.XI_DqIbSAHFM6IP.inh_vcc)'` ← **揭示 XI7 supply pin = inh_vcc**（实际 agent 用 `isub(XI7.inh_vcc)` 即 XI7 顶层 inh_vcc pin）
  - `.probe TRAN v(XI7.XI_DqIbSAHFM6IP.outp_stg1) v(XI7.XI_DqIbSAHFM6IP.outn_stg1)` ← **揭示 outn/outp_stg1 全路径**
  - `.probe slicer_out = 'v(LDFEDataEr) - v(LDFEDataErN)'` ← **揭示 LDFEDataEr 是顶层 net**
- 已有 .meas block（power-avg 窗口 From='5n-32*UI' TO='5n'）:
  - `.meas tran Cur_slicer1st_avg AVG Cur_slicer1st From='5n-32*UI' TO='5n'`
  - `.meas tran Cur_slicer2nd_avg AVG Cur_slicer2nd From='5n-32*UI' TO='5n'`
  - `.meas tran Cur_slicer_avg AVG 'Cur_slicer1st + Cur_slicer2nd' From='5n-32*UI' TO='5n'`
  - `.meas tran Cur_slicer_latch_avg AVG Cur_slicer_latch From='5n-32*UI' TO='5n'`

## 候选判分要点（与 check.py 条件一一对应）
候选必须产出 NEW .sp（不覆盖原文件），其中:
1. 原文件所有非空非注释行保留（superset）
2. 新增 ≥5 条 .meas tran（I_avg + P_avg + t_first_fall + V_outn_at + V_outp_at）
3. 功耗 measure 用 isub(XI7.inh_vcc) + VVDD 倍乘 + 窗口 = 已有 power-avg 窗口
4. t_first_fall 用 WHEN v(LDFEDataEr)='vvdd-0.36' FALL=1 FROM=1.53n
5. V_outn/outp_at 用 FIND v(<全路径>) WHEN v(LDFEDataEr)='vvdd-0.36' FALL=1 FROM=1.53n
6. 新 block 有注释标记行（`* ZL-added`）
7. 新 .meas 出现在已有 .meas block 之后
8. .meas 名唯一无重复
9. SPICE .meas 语法合法（regex validator）
10. 输出文件名 ≠ 输入文件名（不覆盖）
11. .tran / .end 仍在（deck 完整性）
12. 3-seed 打乱新 .meas 行序 → (name,type,target) 集合不变

## B 档反硬编码（hidden/slice_meas_B.sp）
- VVDD=1.0, DR=20E9, .tran 1p 4n, 窗口 From='4n-16*UI' TO='4n'
- 实例 XSA + 子实例 XI_RxSaHFM6IP，supply pin = ih_vdd
- 信号: SAE_DataN (trigger), diff_p, diff_n（全路径 XSA.XI_RxSaHFM6IP.diff_p/diff_n）
- 阈值 vvdd-0.5, start 2.1n
- 已有 .meas: Cur_sa1st_avg / Cur_sa2nd_avg / Cur_sa_latch_avg（窗口 4n-16*UI / 4n）
