# Deepread: 1791509106344_8zuer (adaml / hfeg0pkn001, mc240)

## 选料
- shard D 候选 cand_207b.py top 25；8zuer(adaml/hfeg0pkn001/mc240) score23, schematic:625 netlist:289 cmos:177 hspice:58 opamp:14 → 强 schematic_netlist/analog_context 信号
- 80 msgs / 45 user。首轮 infra(ls 目录)，**U#4 idx32「查看电路网表文件，学习其电路拓扑，生成一套仿真激励。」= 干净 A-faithful 提出需求轮**（提出目标：生成仿真激励；非根因/非修复）。U#5 idx33 是同义复述。

## Trace 流（agent 真实工具链）
- U#1 ls /proj/drvsa/V0/workdir/adaml/simulation → 2 子目录(DQ_TX / DQS_TX schematic_ALPS)
- U#2/U#3 让 agent 访问 sp 文件、学习组织结构、总结方案 → agent 用 cline `list_allowed_files`/`read_files` 读 drvsa_TxTBs_sim_DQ_TX_schematic_ALPS 与 drgqa_simulation/Lbx_sim_DQ_TX_schematic_ALPS/Postsim 下 sp/pwr/measure/run（netlist 太大 read_files timeout，改读 netlistHeader/Footer + search_codebase 找 top-level testbench sim_DQ_TX 在 netlist 第 5104-5131 行）
- **U#4 idx32 提出需求** → agent 读 netlist 子电路定义、定位 top-level testbench `sim_DQ_TX`，理清拓扑：
  - 顶层 Testbench `Lbx/sim_DQ_TX/schematic`：4 相时钟 CLK0/90/180/270 (PULSE, tck=434p, DR=9.2Gbps)，串行数据 DS，DEMUX1TO4 (1:4 串转并) → D0/D1/D2/D3，IO_DqIoTop(=IO_P2sTopCoreV2→IO_P2sTopUnit→IO_DqTx→IO_TxZqcode/IO_DrvAll/IO_MainDrvPu×7/IO_MainDrvPd×7/IO_MainDrvPdPreEm/IO_TX_FFE_PATH) → DQ_Pad 输出，R=50Ω/C=100fF 负载
  - FFE 路径：ffe_en/FFE0/FFE1/FFE2 tap weights
- agent 用 cline `editor` 写出 4 个文件到 `/home/adaml/eWavePDK/HL22nm/`：
  - `stimulus_dq_tx.sp` (95 行, 4120B) — 基础激励，7 段式：option(.inc option_finesim.sp/.option finesim_mode=spicehd/post=1) → pwr/switch .inc → .param(pvcc=1.1/pvssdll/pvdll/pvdpg/pvdd1/pvwlp, tr=tf=60p, DR=9.2E9, tck=434p, duty=0.5, pw, UI=tck/4, CLK_DEL1/DATA_DEL/CLK_DEL, ffe_en/ls_en/FFE2/1/0, CL_near=100f, vcap_thin/thick) → .include './netlist' → .tran 1p 50n → .probe v(DQ_Pad)/v(CLK0)/v(CLK90)/v(D0..D3)/v(DS) → .inc measure_tx.sp → .lib ZQCODE_TTT_25_1.1 → .end
  - `measure_tx.sp` (53 行) — DQ 输出眼图测量：slew_rise/fall(20%-80%), VOH/VOL/Vswing, tCLK2DQ_rise/fall, DQ_pw_rise/fall, I_avg_1v1/vddq, P_avg
  - `stimulus_dq_tx_sweep_ffe.sp` (66 行) — FFE 8-code .data 表 + .tran sweep
  - `README_simulation.md` (141 行) — 拓扑图 + 文件清单 + 7 段式模板
- U#45 无显式接受语，但**用户未再要求修改**（trace 末尾 agent 给完整分析报告，无后续用户轮）→ 隐含接受。golden = 上述 4 文件真实产物（已 ssh cat 全文读取，adaml home 可读）。

## 金标准来源
- `/home/adaml/eWavePDK/HL22nm/stimulus_dq_tx.sp` (95 行) = golden stimulus（全文已读）
- `/home/adaml/eWavePDK/HL22nm/measure_tx.sp` (53 行) = golden measure
- `/home/adaml/eWavePDK/HL22nm/stimulus_dq_tx_sweep_ffe.sp` (66 行) = golden FFE sweep
- netlist 本体 (`/proj/drvsa/.../netlist`, ~5000 行) e0031982 不可读 (permission denied)，但拓扑来自 trace agent 总结 + README 图。

## A-faithful 合成策略
- prompt = U#4 逐字原文：「查看电路网表文件，学习其电路拓扑，生成一套仿真激励。」
- A 资产 = 忠实复刻该 DQ TX 拓扑的 testbench netlist (sim_DQ_TX / 4 相 PULSE 时钟 CLK0-270 / VDS 数据 / DEMUX1TO4 / IO_DqIoTop DUT / DQ_Pad 输出 / pvcc=1.1 / tck=434p)
- hidden B = 不同 TX 拓扑：DQS_TX, 2 相时钟 (CLK0/CLK180), DEMUX1TO2, IO_DqsTop, DQS_Pad 输出, pvcc=1.2, tck=500p（跨输入护栏：信号名/拓扑/供电全不同）
- 交付 = `gen_stimulus.py`（参数化 generator，读 netlist 提取 top subckt/时钟网/数据网/输出 pad/PULSE 幅值与周期 → 输出 stimulus.sp 到 stdout），task_brief ≤3 行只写接口
- check.py 只跑 B：14 条件 a-n，断言 generator 对 B 输出结构正确且不泄漏 A 专属名
- domain = schematic_netlist (+ waveform)，track=faithful，L1-boundary（真 SPICE deck 结构生成）
