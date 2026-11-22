# Deepread: 1794885230899_lpsj7 (renfengc @ hfeg0pfn131, mc=79)

**trace_source**: user=renfengc, host=hfeg0pfn131 (10.129.35.96), session_file=1794885230899_lpsj7.messages.json, match_count=79, keywords=waveview:681;netlist:179;analog:42;synopsys:31;pyaether:5;hspice:3;verilog:2;rtl:1
**domain**: waveform (waveview 主导，D 域)
**session 大小**: 240734 B (47 msgs: 24 user / 23 assistant) — 可读 tractable
**扫描来源**: /home/t0002965/log/ssh_eda_search_20261122_172249/summary.tsv

## 用户真实意图（msg[0] 原文）
> @/proj/dscqa/V0/simdir/finesim/dscqaF/MatrixRun_Netlist_IDD_Vcap_20261030PM_DDR6TOP/idd2nx1p6-11600.160.FF1.025v85c.current/raw/finesim.fsdb 基于这个结果测量单个CAPad0（xi_ddr6top_r.xi_channel.xi_chanpsd0.xi_capadtier.xi_io_capad0.isub(inh_vss) ）在100s-500ns的平均动态工作电流与静态电流，并计算如果CAPad0在clock（clk_0）信号不切换的时间区间下也不切换，CAPad0的平均工作电流可以减少百分之多少

**意图拆解**（真实 waveform 分析任务，clock-gating 节能分析）：
1. 从 FSDB 波形读取 `xi_ddr6top_r.xi_channel.xi_chanpsd0.xi_capadtier.xi_io_capad0.isub(inh_vss)`（CAPad0 衬底电流）时序
2. 在 100ns–500ns 窗口（原文"100s-500ns"系笔误，按 ns 解）算平均动态工作电流
3. 算静态电流
4. 读取 clk_0 切换时序，找出 clk_0 不切换（static）的时间区间
5. 反事实计算：若 CAPad0 在 clk_0 不切换的区间也不切换（即 gate 掉），CAPad0 平均工作电流减少百分之多少

## assistant 工具链（trace 流向）
1. skills: waveview-fsdb-readerV2-2 / finesim-fsdb-reader（两个 .cline skill）
2. read_files skill 脚本 → run_approved_command(python-runner) 跑 fsdb_reader.py
3. 反复尝试信号名 `xi_ddr6top_r.xi_channel.xi_chanpsd0.xi_capadtier.xi_io_capad0.isub(inh_vss)`，多种时间步长 0.1n/10n、多种时间窗 0-500n/100n-500n
4. **全部失败**：FSDB version 6.3（PrimeSim X-2025.06-SP2-2 创建）> 可用 fscript V-2023.12-1 / WaveView X-2025.06-SP2 reader（仅支持 6.1）
5. 探索 /rundata/.../sxcmd.log、finesim.mt0、simrun.log 寻替代数据源，未果
6. session 以未交付结束（assistant 始终未能读取 FSDB）

## 失败根因（用户令 §四「失败层」逐层区分）
- **infra 层（非 .75 不可达）**：fscript/primesim_2023.03 在 .75 上存在（/apps/synopsys/SRB/primesim_2023.03-SP1/bin/fscript），但版本 2023.03 < FSDB 创建版本 2025.06，读不了 v6.3
- **权限层**：原 FSDB `/proj/dscqa/.../finesim.fsdb` 与 `/rundata/dscqa/.../` 对 e0031982 **Permission denied**（属 renfengc / dscqa project）
- **资产可打包性**：FSDB 880MB+ 且权限受限，无法作为 case attachment 落 SUT 沙盒
- 结论：.75 可达(MCP OK)，trace 可读(messages.json 已 scp 解析)，但**真实波形数据不可提取** → 无法造可运行 case

## 跨 shard 备注（重要）
- 本 trace **已在 shard B 台账**（status=parked, 2026-11-21 13:24, note="FSDB reader: needs 880MB finesim.mt0/prod FSDB v6.3 asset, not packageable"）
- **B 误判 domain**：B 标 spice_sim，但 keywords waveview:681 主导 = **waveform (D 域)**；B 的 park 理由（FSDB 不可打包）与 D 复测一致
- D 不 reclaim（同 blocker 再 park 是 churn）；记录供 B 修正 domain 标注

## 造题可行性评估
- ✅ 意图真实、有价值（waveform current measurement + clock-gating power savings %）
- ✅ trace 溯源完整（user/host/session_file/match_count/real_task_summary 齐全）
- ❌ **真实波形数据不可访问**（权限 + 版本双重阻塞）→ 无法满足 §4.1 hidden B「真跑候选」+ §4.2「subprocess 在 B 上执行候选脚本断言输出结构」
- 复活路径：找到一条**可读 FSDB**（fscript 可读版本 ≤6.1）或**已提取的 current 文本波形**（time,current CSV）的同型 trace，把此意图套上去

## 状态
- **parked**（已在 B 台账，D 不重复 claim；D 侧记录 deepread 完成）
- 下一轮：从本轮 candidate scan 的 fresh D-pure 候选（508od/sjzm0/sstk3/ijh76/fbz0w/sroz5，均 schematic_netlist，ledger_D 0 hit）选 1 条深读+合成
