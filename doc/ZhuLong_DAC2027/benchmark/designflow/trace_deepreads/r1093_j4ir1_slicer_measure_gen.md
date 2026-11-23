# r1093 深读 · j4ir1 (jiangbaol@hfeg0plg99, mc46, characterization)

**trace_source**: user=jiangbaol, host=hfeg0plg99, session_file=1794817983296_j4ir1, match_count=46, real_task_summary=FineSim DDR4 DFE slicer (doubletail_nmoslatch) characterization: .sp testbench debug + .measure 生成 + 多轮 sizing sweep (M1/M2/MP1/MN11/MN12/MN17/MP0/MN18) 最小化 FOM=CK2Q_DFE_T_F*Cur_slicer_latch_avg

**访问**: .75 ssh 到 hfeg0plg99 通 (e0031982 免密)。session 嵌套 sessions/<sid>/<sid>.messages.{json,archive.json}。archive 1.5MB/362msgs(archivedAt 1793601381931) + live 190KB/446msgs 总。cross-shard ledger 4-shard 检查：本 sid 仅 B claim ✓。

**会话主线** (16 个真实 user_input，446 msgs):
- U#1 (msg0): duplicated subckt `DqIb_2stg_DfeM6V2` 报错 → `.option redefsub` 解答 (Q&A)
- U#2 (msg~): hspice option 输出每层级所有 net 信号 (Q&A)
- U#3 (msg~): .sp 无法 probe slicer_out/slicer1st_out → 诊断层级路径 + 大小写 (DqSampN vs DQSampN) + 加 .probe TRAN
- **U#4 (msg33): ⭐ 干净 L1 复刻目标** — 在 .sp 添加 .measure 实现 3 功能
- U#5-#16: 多轮 sizing sweep (L3 真跑 Finesim) — 需真实仿真，不适合作 L1 case

---

## ⭐ U#4 reframe 候选 (本轮选中，下轮合成)

**用户原话 (msg33)**:
> /proj/m2701/V0_DDR4/simdir/finesim/workdir/jiangbaol/simulation/001_slicer/Slicer_testbench/004_onlySlicer_delay_m2701.sp
> 在该.sp中添加measure语句，实现如下功能：
> 1.测量XI7整体电源功耗,采样时间与.sp内其他功耗时间一致;
> 2.测量1.53后，ldfedata第一个下降沿达到vvdd-0.36的时刻；
> 3.测量2.时刻时outn_stg1与outp_stg1的电压
> 生成的.sp放在原.sp路径下

**assistant 产出的 measure 块 (msg54, 插入 Cur_slicer_latch_avg 之后, 原第222行后)** — 真实参考解:
```spice
.probe XI7_vcc_cur = 'isub(XI7.inh_vcc)'
.meas tran I_XI7_vcc_avg  AVG  XI7_vcc_cur           From='5n-32*UI'  TO='5n'     ; [1] XI7 平均电源电流
.meas tran P_XI7_vcc_avg  AVG  'VVDD*XI7_vcc_cur'    From='5n-32*UI'  TO='5n'     ; [1] XI7 平均电源功耗
.meas tran t_ldfe_first_fall  WHEN  v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n ; [2] ldfedata 第一个下降沿到 vvdd-0.36 的时刻
.meas tran V_outn_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outn_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n ; [3]
.meas tran V_outp_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outp_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n ; [3]
```

**关键 .sp 上下文 (assistant read 出)**:
- `.tran 1p 5n` (sim end=5n)
- 已有功耗均值窗: `From='5n-32*UI' TO='5n'` (line 219-222, Cur_slicer_latch_avg 等)
- `vcc!` 由 `vvcc` 源提供 VVDD (line 182)
- XI7 实例化 `DqIb_2stg_DfeM6V2IP_DT` (line 336), 电源脚 `inh_vcc` ← `vcc!`
- XI7.XI_DqIbSAHFM6IP 实例化 `doubletail_nmoslatch` (line 326)
- 层级: `XI7.XI_DqIbSAHFM6IP.outp_stg1` / `.outn_stg1` (第一级输出, 已被 line 217 .probe TRAN 保存)
- ldfedata = `LDFEDataEr` (真值数据输出); VVDD−0.36 阈值; FALL=1; FROM=1.53n

**reframe (L1 纯 Python, 无 EDA 依赖)**: `slicer_measure_gen.py <spec.json> <out.txt>`
- spec 描述: power{inst_pin, vdd_param, win_from, win_to}, crossing{signal, threshold_expr, edge, from_time}, find_voltages[{alias, hier_path}]
- 输出 .probe + .meas tran 语句块, 严格按 FineSim 语法 (AVG/WHEN/FIND, From=/TO=/FROM=, 单引号 threshold)
- 参考 = 上述真实块 (A 用 jiangbaol 真实参数)

**case ID 候选**: `EDA-Eval-DesignFlow-SlicerMeasureGen-001`

**A (真实)**: inst_pin=XI7.inh_vcc, vdd=VVDD, win=(5n-32*UI, 5n), signal=LDFEDataEr, thr=vvdd-0.36, edge=FALL=1, from=1.53n, finds=[(V_outn_stg1_at, XI7.XI_DqIbSAHFM6IP.outn_stg1), (V_outp_stg1_at, XI7.XI_DqIbSAHFM6IP.outp_stg1)]

**hidden B (五重 anti-hardcode 候选)**: ①inst_pin=XI3.vdda ②vdd=VDDA ③win=(10n-64*UI, 10n) ④signal=CLKOutEr / thr=vdda-0.5 / edge=RISE=1 / from=2.1n ⑤finds=[(V_clkp_at, XI3.XI_clkbuf.clkp), (V_clkn_at, XI3.XI_clkbuf.clkn), (V_mid_at, XI3.XI_clkbuf.mid)] — 3 个 FIND 反 A 的 2 个

**check.py k≥12 条候选**:
1. zip+py_compile+size>200
2. B exit0+非空 out.txt
3. `.probe <cur_alias> = 'isub(<inst_pin>)'` 存在且 inst_pin==B spec
4. I_<alias>_avg measure: AVG <cur_alias> + From=<win_from> + TO=<win_to> 匹配 B
5. P_<alias>_avg measure: AVG '<vdd>*<cur_alias>' + window 匹配 B
6. t_<cross_alias>: WHEN v(<signal>)='<thr>' <EDGE>=1 FROM=<from> 匹配 B (signal/thr/edge/from 四齿)
7. 每 find_voltage: FIND v(<hier_path>) WHEN v(<signal>)='<thr>' <EDGE>=1 FROM=<from>
8. find alias 集合==B spec (3 个, 反 A 2 个)
9. hier_path 集合==B spec
10. measure 名无 A 残留 (anti-hardcode)
11. 语法: 每条 .meas tran 开头; threshold 带单引号; From=/TO=/FROM= 大小写区分 (From= 用于 AVG 窗, FROM= 用于 WHEN 起始 — 真实写法)
12. 3-seed sha256 确定性
13. (可选) 注释 ; [n] 标号存在

**3 neg 候选**: empty(→1/2) / print_only(硬编 A measure 块→3/4/6/8/10) / core_removed(真解析 B 但 WHEN 用 RISE 反 edge + 硬编 A win→4/5/6/7)

---

## 其它 sub-task (本轮不选, 留档)

- U#3 probe 诊断: analysis-only, weak
- U#5-16 sizing sweep: L3 真跑 Finesim 迭代, 需 /proj/m2701 model 文件 + Finesim license; 真实但 check 难脱机化 (需跑 sim)。可考虑作 L2 case (assets 含 .sp + netlist, check 跑 Finesim 解析 .mt0) 但本 host Finesim 启动需清 LD_LIBRARY_PATH (trace msg67 验证), 复杂度高, 留后续。

---

## 本轮结论

**0-case 深读轮**。j4ir1 (446 msgs/1.6MB) U#4 measure-gen 子任务深读完成, reframe 清晰 (L1 纯 Python slicer_measure_gen.py), 真实参考解 + .sp 上下文已从 trace 提取。**DEBT: 1 deepread 未合成** → r1094 直接合成 SlicerMeasureGen-001 (ETA 下轮)。本轮因预算(40min 硬限)耗尽于选料+深读, 未能完成 case 落库。j4ir1 已 claim, 下轮 mark case。

**.75 访问 OK**: eda_flow session(default_designflow-loopB_shardB-r1093-probe_0) open+ssh 通 hfeg0plg92/hfeg0plg72/hfeg0plg99/hfeg0plg93。scan 仍 ssh_eda_search_20261123_064315。

**选料过程**: fresh_b_spice_r1090_fresh.tsv(90 行) 按 spice-purity 排序。cixxj 已 case'd(CellFamilyExtractGen-001) 跳过; 7xh6n=Q&A 杂项跳过; lnki5=digital timing viz→cross-shard A 跳过; 5qlyc=output.ic 后仿加速 Q&A weak; **j4ir1(jiangbaol mc46 characterization FineSim slicer) 选定** — 干净 B 域 + U#4 干净 L1 子任务。
