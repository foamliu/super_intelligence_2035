WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 🆕 shard A 启动，从主 loop 分片而来。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：trace_ledger.py --shard A next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_A.jsonl → 日报
- **本轮任务**：rewrite_queue 队首 EDA-Eval-DesignFlow-Digital-010 断言闸门整改（已完成）
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard A stats
- 🎯 通过率: 0/0（刚启动）
- 🧾 断言: k_rationale=k_check=19 ✓（今日 1/4 达标）· 队列剩 3/4（Digital-021/022/023 待整改）

### 2026-11-02 shard A 轮 1：Digital-010 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-010`（digital）标 `incomplete`：jsonl test 字段是旧 1123B 弱判分，rationale 是散文。
- 磁盘 `check.py` 上一轮已重建为 19 条独立标签 (a)-(s)（zip5文件/module/endmodule/acc0-3/正饱和7fffffff/负饱和80000000/>32bit中间位宽/提交log-PASS/提交log-no-FAIL/VCD结构/VCS-A编译运行/A-PASS/A-no-FAIL/VCS-B编译运行/B-PASS/B-no-FAIL/checkpointB1非对称/checkpointB6负饱和/checkpointB7复位后小正值），真跑 VCS R-2020.12 L2。
- 本轮做：①jsonl `test` 字段同步到磁盘 check.py（1123→13297B，test==disk roundtrip OK）；②`test_rationale` 散文→`19 条断言：①…⑲`（k=19）。
- .75 沙盒实测（VCS R-2020.12）：negative_selftest NEG_RC=0（5 个假提交全 FAIL：fake_empty→d / fake_print_expected→e / fake_core_deleted→e / naive_no_wide→g / naive_never_saturate→e）；ref `reference_submit.zip` check() PASS（真跑 VCS A+B，21s）。
- 闸门：k_rationale=19=k_check=19≥8 ✓；jsonl 7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-010 → done；剩 Digital-021/022/023 待整改（下轮第一件事）。
