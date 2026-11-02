WAITING: 0
SHARD: C (physical_layout)
DOMAINS: layout_aether, layout_virtuoso, pg_layout, physical_verify

- **PHASE**: 🆕 shard C 启动，从主 loop 分片而来。负责 domain: layout_aether, layout_virtuoso, pg_layout, physical_verify
- 每轮做 1 条 case：trace_ledger.py --shard C next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_C.jsonl → 日报
- **本轮任务**：trace_ledger.py --shard C next 取候选，建第一条 case
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard C stats
- 🎯 通过率: 0/0（刚启动）
