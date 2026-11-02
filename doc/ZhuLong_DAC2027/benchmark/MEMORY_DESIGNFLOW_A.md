WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 🆕 shard A 启动，从主 loop 分片而来。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：trace_ledger.py --shard A next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_A.jsonl → 日报
- **本轮任务**：trace_ledger.py --shard A next 取候选，建第一条 case
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard A stats
- 🎯 通过率: 0/0（刚启动）
