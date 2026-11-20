# Deep-read: 1794972210149_x0lhk (e0024852 @ hfeg0plg78)

- **User**: e0024852 @ hfeg0plg78 (spice_sim SRAM bitcell DTCO)
- **mc**: 190; keywords: pex:516 hspice:295 ratio 0.62; tools: editor 88 / run_approved_command 48 / read_files 26
- **NMSG**: 381 msgs / 196 user turns
- **Trace host**: hfeg0plg78 (summary.tsv lists hfeg0pkn005 but session file found on hfeg0plg78 via NFS)

## User intent (U[0] original)
> /rundata/lacaa/TV1_FS/simdir/finesim/workdir/e0024852/SRAM_bitcell_DTCO/Bitcell_FS/CH252_FS_guojing 之前的指标里面只有DC 指标 我改了寄生效应之后 结果并不发生变化 我想加一些瞬态效应的结果比如SNM 指标 SNM 的计算方式 [贴了 extract_HSNM.py 脚本: 从 HSPICE .lis 提取 .print DC 蝴蝶图数据, 算 HSNM 最大内接正方形边长]

## Task arc
- U[0]: 加瞬态指标 (SNM) 到既有 DC 流程；给了 extract_HSNM.py 参考 (蝴蝶图 max-inscribed-square)
- M[67]: agent 跑通 39 variant 静态 SNM: HSNM=319.66mV RSNM=129.06mV, 全 variant 一致 (DC 量对寄生电容免疫)
- M[95]: 交付 extract_snm_all.py (静态 SNM) + stimulus_tran.sp (瞬态 testbench) + parse_tran_ms0.py + sim_tran.sh + merge_summaries.py
- U[128]: 先跑过孔dspf的这个瞬态效应把
- M[163]: 4 via variant 瞬态 t_read 结果: v01_sz012_ox000 (C高0.0638fF) t_read=4.33ps t_read_diff=1.23ps t_write=9.78ps; v02_sz016_ox000 (C低0.0532fF) t_read=3.92ps
- M[183]: 74 via variant 瞬态读时序精确分两族, 与 BLB 电容一一对应 (C高20% → t_read 快 21%, t∝C 物理自洽)
- M[253]: M1 variant 连瞬态都完全一样 (PEX 输入问题, 非 cell 问题)

## Core produce (what the agent actually built)
1. **extract_snm_all.py**: 解析 .lis DC transfer 区 (s_rsnm/sb_rsnm/s_hsnm/sb_hsnm), 算 HSNM+RSNM 蝴蝶图/最大内接正方形, 按 variant 汇总 CSV
2. **parse_tran_ms0.py**: 解析 .mt0/.ms0 .meas tran (t_read/t_read_diff/t_write/t_write_sb) → ps
3. **sim_tran2.sh / sim_tran3.sh**: bsub+hspice 循环 runner, 逐 variant 替换 <DSPF_NAME>, 跑仿真+解析, 写 _tran_summary.csv
4. **merge_summaries.py**: 把 DC + SNM + RC + tran 按 variant 合并成一张表

## Case reframe (B 档 synthesized → A 档 trace-faithful)
真实 trace 的核心 produce 是「参数化 HSPICE .lis/.mt0 解析器 + max-inscribed-square HSNM + 合并 CSV」。
本 case 取该核心 produce 做成 A 档 trace-faithful: 用户原话 U[0] + 真 .lis/.mt0 格式 + 真 DC/tran 数值,
agent 交付 metrics_extractor.py (合并 extract_snm_all.py + parse_tran_ms0.py + merge_summaries.py 的功能)。

## Numerical ground truth (from trace)
- DC corner tt_25C: Iread=25.887 uA, Ilead=35.026 pA, WNM_1=285.671 mV, WNM_2=285.671 mV, Vsnm=0.000 mV
- HSNM (L1225 all 39 variant): 319.66 mV; RSNM: 129.06 mV (全一致, DC 量)
- tran (v01_sz012_ox000 C高): t_read=4.33 ps, t_read_diff=1.23 ps, t_write=9.78 ps, t_write_sb=15.58 ps
- tran (v02_sz016_ox000 C低): t_read=3.92 ps, t_read_diff=1.02 ps, t_write=9.76 ps, t_write_sb=15.53 ps

## Asset design
- A: 3 variant × 2 corner, HSNM=214.86 RSNM=100.22 (合成 VTC, 比真实 319/129 小但比例合理), tran 取真实 4.33/3.92
- B (hidden): 4 variant × 3 corner, 异名 varB_sram_cell_7t_*, 异 VTC (HSNM 207.73/225.00 RSNM 90.64/119.52), 异 tran (5.81/5.22/5.51), delta variant 无 .mt0 (容错测试)
