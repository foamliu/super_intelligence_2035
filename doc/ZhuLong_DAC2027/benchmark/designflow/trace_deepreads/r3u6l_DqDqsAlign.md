# 深读笔记 · r3u6l · DqDqsAlignCheck

## trace_source
- session: 1794375819662_r3u6l
- user: yunfat (drvqaw 组)
- host: hfeg0plg94 (10.129.8.226)
- match_count: 35
- keywords: waveview:259;analog:28;netlist:18;schematic:10;synopsys:9;cmos:7;pyaether:6
- scan: ssh_eda_search_20261113_131349
- shard: D (waveform)
- messages.json: 191KB / 30 msgs

## 用户原话（U#0=U#1，act 模式，逐字）
`/proj/drvqa/V0/simdir/finesim/workdir/yunfat/raw/finesim.fsdb 查看这个波形的DQ 和DQS 是否对齐，过程文件放在/proj/drvqa/V0/simdir/finesim/workdir/yunfat/raw 这里。`

## 意图判读
- 纯目标轮（A-eligible）：用户提出目标（查 DQ/DQS 是否对齐）+ 指定过程文件落点；未给根因、未给修复方案。
- DDR 语义：DQ 数据、DQS 选通；"对齐" = DQS 边沿是否正确采样 DQ（center-aligned 读 / edge-aligned 写）。
- 真实工具链：finesim FSDB → WaveView ACE Tcl（waveview-fsdb-readerV2-2 skill）。

## assistant 工具链（trace 全程）
1. get_agent_policy_status / skills(waveview-fsdb-readerV2-2)
2. list_allowed_files(workdir + skill dir)
3. read_files(skill .py + base reader waveview_fsdb_reader.py)
4. skills(finesim-fsdb-reader) → 发现 python3.7 broken / 需 /usr/bin/python3.11
5. editor(apilist.sh) 探 WaveView ACE Tcl API 信号列举命令
6. run_approved_command(apilist.sh) → trace 在此中断（[29] USER 空）

## 金标准判读
- trace 末尾无用户接受结果（session 在探 API 阶段中断，无对齐报告产物）。
- ⇒ 无 trace 末尾金标准 ⇒ 不能做 A 档（A 档要求金标准=trace 末尾用户接受产物）。
- ⇒ 本条做 **B 档（synthesized reframe）**：保留用户真实意图（DQ/DQS 对齐检查）+ 真实路径/用户名，合成波形数据 + 合成金标准。
- 档位：B；难度层：L1（候选写 Python 脚本分析文本波形 dump，非真跑 WaveView FSDB —— FSDB 二进制无法在沙盒复刻，同 r656 DqTrtfMeasure 模式）。

## 合成方案
- 资产 A：`dq_dqs_A.txt` —— 文本波形 dump（time_ns, dq, dqs 三列方波采样 0.05ns），DQ 脉冲窗 + DQS 选通边沿，center-aligned（aligned=True）。
- 隐藏 B：`dq_dqs_B.txt` —— 同构异值，DQS 边沿落在 DQ 转换处（edge-aligned，aligned=True，alignment_type 不同）。
- 隐藏 C：`dq_dqs_C.txt` —— misaligned（DQS 边沿落在转换与中心之间，aligned=False）—— 反硬编码第二证物。
- 候选交付：`outputs/submit.zip` 含 `align_check.py`（接口 `python3 align_check.py <waveform> <out_json>`）+ `report.json`（在 A 上跑）+ `report.md`。
- check.py：16 条件，subprocess 真跑候选脚本在 B/C 上，与 reference_solution 在 B/C 上的 oracle 逐字段比对 + 反硬编码 + 跨字段自洽 + 退化全 FAIL + 随机抽 DQS 边沿子集 3 seed 一致。

## 域归属
- waveform（DQS 选通 / DQ 数据 / 时序对齐）—— shard D 专属。
