# r965 triage deepread — 5 fresh spice candidates peeked (0-case 质量闸门)

**日期**: 2026-11-21 r965
**快照**: summary_1120_reconstructed.tsv, mc≥10 pool=2072 fresh=287→283 (park 4)
**结论**: 0-case 质量闸门（非池枯竭）。5 个 fresh spice 候选 peek 后全 non-viable for self-contained case。

## 选料方法
- 4-shard ledger 排除后，从 summary_1120_reconstructed.tsv 直接 awk spice_kw 过滤（mc≥10, spice_count≥15）
- fresh spice-heavy 候选 171 条；top 按 spice_count/spice_ratio 排序
- 经 eda_flow open_session + scp messages.json 到 workdir + python3 peek.py 解析对话流

## 5 候选 peek 结果

### 1. lpsj7 (renfengc, hfhds234, mc79, spice=684/946=0.72) — ❌ PARKED
- 用户原话: "@/proj/dscqa/.../finesim.fsdb 基于这个结果测量单个CAPad0...在100s-500ns的平均动态工作电流与静态电流，并计算如果CAPad0在clock信号不切换的时间区间下也不切换，CAPad0的平均工作电流可以减少百分之多少"
- 形态: FSDB 波形读取 + 电流测量分析（spice_sim/WaveView）
- 不可造原因: 需要 880MB finesim.mt0 + 生产 FSDB v6.3 资产；trace agent 自身被 "FSDB version 6.3 newer than reader 6.1" 阻塞，未产出参考交付物。无法物化成 self-contained case。
- park note: "FSDB reader: needs 880MB finesim.mt0/prod FSDB v6.3 asset, not packageable"

### 2. 5qv7f (hao23c, hfeahpc505, mc89, spice=397/412=0.96) — ❌ PARKED
- 用户原话: "你能看到当前打开的waveview视图吗" / "能找出哪个信号执行了测量命令吗"
- 形态: interactive WaveView GUI 会话（"看到我打开的波形/probe了哪些信号"）
- 不可造原因: 任务本质是交互式 GUI 探查（live WaveView session + 用户已打开的 .tr0），无独立交付物；SUT 沙盒无法复刻"用户当前打开的 GUI 状态"。check() 写不出有牙断言。
- park note: "interactive WaveView GUI session: 'see my open waveforms/find measured signal' needs live GUI, not self-contained"

### 3. peemu (gallopc, hfeg0plg80, mc86, spice=248/488=0.51) — ⏸ 未深读（880K，留下一轮）
- 关键词 netlist:2323/schematic:776/waveview:443/hspice:68，混合域，未完成 peek

### 4. jubda (fanglei, hfeg0plg64, mc46, spice=250/259=0.97) — ❌ PARKED
- 用户原话: "能看到我打开的这几个波形吗" / "可以查看到我probe了哪些信号波形吗？"
- 形态: interactive WaveView GUI 会话（同 5qv7f 模式）
- 不可造原因: 同 5qv7f；trace agent 反复调 sx_wdf_info/sx_first_wdf 导致 bridge 30s 超时卡死，未产出交付物。
- park note: "interactive WaveView GUI: 'see open waveforms/probed signals' bridge timeout, not self-contained"

### 5. izf3q (ericw, hfeg0pfn034, mc94, netlist=1091/hspice=34) — ❌ PARKED
- 用户原话: "/rundata/drdxq/.../primesim.Perbank001_ActWrRdPre_WPre_2_tCH_50_BL16_4b8g_B0_100_TT.X4.TT0.98V25C.X4 分析这里si.out的报错"
- 形态: si.out 报错分析（debug-Q&A，spice_sim/PrimeSim）
- 不可造原因: 需 269035 行生产 incFile_T1_HKMG 模型文件 + 生产 netlist（confidential IP + 巨大），无法物化进 assets/；check() 无法在 B 上独立复刻报错诊断。
- park note: "si.out debug-Q&A: needs 269K-line prod incFile_T1_HKMG model+netlist (confidential/huge), not packageable"

## 模式观察（B 域 fresh 池结构性问题）
top spice-ratio fresh 候选集中在三类难物化形态：
1. **FSDB/waveform 读取**（lpsj7 类）: 需生产 FSDB（百 MB~GB），版本兼容性问题
2. **interactive WaveView GUI**（5qv7f/jubda 类）: 任务是"看我现在打开的波形/probe"，本质依赖 live GUI session
3. **生产 sim 输出 debug-Q&A**（izf3q 类）: 需生产 model/netlist 文件（十万行级，confidential）

joeyl cluster（~15 个 near-identical netlist:1102/hspice:93/opamp:24 session）是同任务重复，near-dup-of-prior，应批量 park。

## 下一步建议
- 下一轮优先 peek **deck-generation / netlist-edit / measurement-script** 类候选（非 waveform/debug）：从 fresh 池按 netlist+hspice+.spi 关键词 + 排除 waveview/fsdb 过滤
- joeyl near-dup cluster 批量 park（1 个深读代表即可）
- peemu (gallopc) 下一轮优先深读（混合域，未判定）

## 证据链
- mc-matrix: `python3 designflow/trace_ledger.py --shard B mc-matrix --src designflow/summary_1120_reconstructed.tsv` → mc≥10 pool=2072 touched=1785→1789 fresh=287→**283**
- 4 parked: lpsj7/5qv7f/jubda/izf3q（claim+mark --status parked，note 见上）
- 5 peeked via eda_flow open_session + scp + python3 peek.py（messages.json 全文解析）
