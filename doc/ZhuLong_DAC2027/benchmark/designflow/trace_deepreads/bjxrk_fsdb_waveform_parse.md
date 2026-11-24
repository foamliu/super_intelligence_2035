# deepread: 1792387840615_bjxrk — finesim-fsdb-reader (waveform)

- session: 1792387840615_bjxrk.messages.json
- user: colinxu @ hfeg0pgn041 (mc=8, domain=waveform)
- size: 16 msgs / 87KB
- trace_source: real cline session, fresh (not in any shard ledger before r1243)

## 真实意图
用户触发 `finesim-fsdb-reader` skill（skill_instructions 注入），目标是：
1. 用 `fscript` 从 finesim `.fsdb` 波形文件 dump 指定 hierarchy 信号采样值
2. 把 fscript 表格输出解析为 `{signal_name: [(time, value), ...]}`
3. 自动判定数字/模拟信号，分别做边沿/脉冲计数 或 过零/统计
4. 提供采样、边沿检测、脉冲检测、过零分析

skill 参考实现: `/home/colinxu/workspace/start_vscode_cc/system_config/skills/finesim-fsdb-reader/fsdb_reader.py`
测试 FSDB: `/home/wellesc/fsdbreader/finesim.fsdb`

## agent 行为
- msg0: skill_instructions (finesim-fsdb-reader) + "do it"
- msg1-10: 查 policy engine、定位 fsdb_reader.py、读参考实现、确认测试 FSDB 可读
- msg12-15: 写 probe_env.py 探测 fscript/bsub 可用性 → trace 在 probe 执行后被截断

agent 未完成完整分析流（停在环境探测），但**任务意图完整且可离线化**：判分内核 = 解析层+分析层，不依赖 fscript/FSDB 实际运行。

## 抽离的判分内核（L1 离线 Python）
- 输入：fscript dump 表（文本）
- 输出：`{signal: report}` JSON，digital 含 edges/pulses，analog 含 stats/zero_crossings
- fscript 表格式：首行 `TIME v(sig1) v(sig2) ...`；行 `<时间> <值> ...`；时间 ns/us/ps 后缀→秒；值 m/u/n/k/M/G 后缀→float

## case 合成
- task_id: EDA-Eval-DesignFlow-FsdbWaveformParseAnalyzeProduce-001
- A (visible): fsdb_dump_A.tbl — 4 信号(clk/precmd digital, writecmdall analog, sineout), 40 点, 0..3.9n
- B (hidden): fsdb_dump_B.tbl — 5 信号(clk/actcmd/csn digital, iread/vramp analog), 50 点, 0..4.9n — 与 A 结构性不相交（不同信号名/数量/时间范围/数字-模拟配比；vramp 双极性模拟带过零，csn 活动低电平）
- check: 10 断言（结构+正确性+确定性+随机化 3 种子），3 negative 全 FAIL，selftest ref PASS
- k_check=10 (≥8 ✓), §4.9 三假 FAIL ✓

## 与已有 D case 不相交
- 不涉及 netlist 层次/SPICE 激励（lorih/dqbus 类）、不涉及 MCP SSE 文档（au4qn 类）、不涉及 SPF/PEX（xinfv/pex 类）。纯波形 dump 解析+分析，waveform 域。
