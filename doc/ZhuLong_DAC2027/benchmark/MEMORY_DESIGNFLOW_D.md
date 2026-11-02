WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

- **PHASE**: 🆕 shard D 启动，从主 loop 分片而来。负责 domain: analog_context, schematic_netlist, waveform
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- **本轮任务**：trace_ledger.py --shard D next 取候选，建第一条 case
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard D stats
- 🎯 通过率: 0/0（刚启动）
