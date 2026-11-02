WAITING: 0
SHARD: B (spice_char)
DOMAINS: characterization, spice_sim

- **PHASE**: 🆕 shard B 启动，从主 loop 分片而来。负责 domain: characterization, spice_sim
- 每轮做 1 条 case：trace_ledger.py --shard B next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_B.jsonl → 日报
- **本轮任务**：trace_ledger.py --shard B next 取候选，建第一条 case
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard B stats
- 🎯 通过率: 0/0（刚启动）
