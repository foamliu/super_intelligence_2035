# Deepread: p3c57 — jiangbaol doubletail slicer sizing sweep

**trace**: 1794540366981_p3c57.messages.json (306 msgs, 1.3MB, 10.129.2.13/hfeg0pkn004)
**user**: jiangbaol | **mc**: 208 | **domain**: spice_sim | **shard**: B

## Session arc (8 user requests)

1. **msg[0]** PEX error: duplicated subckt definition `DqIb_2stg_DfeM6V2` in SPF → Q&A (redefsub option)
2. **msg[2]** HSpice option: waveform per hierarchy level all nets → Q&A (no web access, answered from knowledge)
3. **msg[7]** Fix .sp probe: slicer_out/slicer1st_out not probing → agent reads 004_onlySlicer_delay_m2701.sp, writes tmp_grep.py, identifies net naming issue, writes fix_probes.sp.txt
4. **msg[33]** **Add .measure statements**: ① XI7 power ② ldfedata first fall @vvdd-0.36 ③ outn_stg1/outp_stg1 voltage → agent edits .sp, adds .meas block (Cur_slicer_latch_avg, t_ldfe_first_fall, V_outn_stg1_at, V_outp_stg1_at, CK2Q_DFE_T_F)
5. **msg[55]** **Sizing sweep #1**: adjust M1/M2 (input pair) + MP1 (tail) in doubletail_nmoslatch, constraint max(V_outn,V_outp)≤480mV, maximize |ldfe_dm| → agent writes sweep_batch.sh, runs 10 batches FineSim, parses .mt0.csv, finds best win=0.4u/wtail=1.2u (max=481mV, |ldfe_dm|=196.8mV)
6. **msg[148]** **Sweep #2**: change target to max |slicer1st_out| → same optimum region
7. **msg[163]** **Sweep #3**: change input pair pulvt→prvt, relax max≤600mV → best win=4u/wtail=1.2u (max=548mV, |slicer1st_out|=55.1mV)
8. **msg[207]** **Sweep #4**: target min CK2Q_DFE_T_F, add nf → best win=5u/wtail=2u/nf=4 (CK2Q=22.6ps)
9. **msg[240]** **Sweep #5**: input puhvt_ckt → best win=12u/wtail=2.5u
10. **msg[269]** **Sweep #6**: revert to prvt best, sweep 2nd-stage latch NMOS MN23/MN26, min FOM=Cur_slicer_latch_avg×CK2Q → sweep_fom.sh

## Key data format — FineSim .mt0.csv
```
$DATA1 SOURCE='FineSimPro' VERSION='V-2023.12-1' PARAM_COUNT=0
.TITLE '****** HSPICE Default Option for Block Level Simulation'
 cur_slicer1st_avg,cur_slicer2nd_avg,cur_slicer_avg,cur_slicer_latch_avg,i_xi7_vcc_avg,p_xi7_vcc_avg,t_ldfe_first_fall,v_outn_stg1_at,v_outp_stg1_at,ck2q_dfe_t_f,ck2q_dfe_b_f,temper,alter#
 -2.3869e-04,...,6.4043e-04,...,1.5759e-09,7.1498e-01,6.9976e-01,1.8402e-11,1.8029e-11,4.5000e+01,1.0000e+00
```

## Sweep log format (sweep_batch.sh output)
```
win=4.6u wtail=8u :  -2.4309e-04,...,7.3890e-01,7.2571e-01,...,1.8204e-11,...,4.5000e+01,1.0000e+00
```

## A档可行性: 不可行
- /proj/m2701 项目目录对 e0031982 权限受限
- FineSim 仿真依赖 license + 项目 netlist/model 路径

## B档方案: SlicerSweepFomOpt-001
- **任务**: 写 sweep_fom_optimizer.py — 解析 FineSim sweep 结果(sweep log 格式), 应用约束 max(outn,outp)≤Vth_max, 计算 FOM=power×delay, 找最优尺寸点
- **Input A**: pulvt_ckt sweep 12 points, Vth_max=0.50V
- **Hidden B**: prvt_ckt sweep 15 points, Vth_max=0.60V, 不同列数(测试鲁棒性), 不同最优
- **check.py 13 断言**: zip+compile / subprocess exit0 / JSON keys / 解析点数 / 约束过滤 / FOM复算 / 最优选择 / 全不可行edge / tie确定性 / A≠B / 3 seed确定性 / 列数鲁棒 / 退化输入
