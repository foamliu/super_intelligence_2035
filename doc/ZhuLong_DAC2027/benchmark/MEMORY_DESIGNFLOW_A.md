WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: shard A 断言闸门整改阶段。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：rewrite_queue 优先（断言闸门），清零后 trace_ledger.py --shard A next → claim → 深读 → 合成
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard A stats
- 🎯 通过率: 0/0（A 档尚未实跑；先清断言债）
- 🧾 断言: k_rationale=k_check=17 ✓（今日 2/4 达标）· 队列剩 2/4（Digital-022/023 待整改）

### 2026-11-02 shard A 轮 2：Digital-021 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-021`（digital, PrimeTime 时序报告负 slack 路径提取, L1 离线 Python）标 `incomplete`：jsonl test 字段是旧 1568B 弱判分（4 packed 条件），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-021/check.py` 从 4 packed 条件 → 17 独立标签 (a)-(q)：
  (a)zip2files / (b)py_compile / (c)print-token-TOTAL/NEG/WORST_SLACK/WORST_ENDPOINT / (d)A-exit0 / (e)A-TOTAL=12 / (f)A-NEG=5 / (g)A-WORST_SLACK=-1.957 / (h)A-WORST_ENDPOINT=test_so[25] / (i)A-rerun-rpt-7fields / (j)A-rerun-rpt-test_so[25] / (k)A-rerun-rpt-(-1.957) / (l)A-rerun-rpt-exactly-5-Path-headers(no-MET) / (m)B-exit0 跨输入守护 / (n)B-TOTAL=9 / (o)B-NEG=4 / (p)B-WORST_SLACK=-2.483 / (q)B-WORST_ENDPOINT=wb_dat[5]
- 隐藏 B 附件 `assets/.../hidden/pt_reg2out_B.tarpt`：9 paths / 4 VIOLATED / worst -2.483 @ wb_dat[5] / func_ss_m125c_cbest_T + shift_tt_25c_cworst_T 视角，与 A(12/5/-1.957/test_so[25]) 结构性不同；B 不进 SUT 沙箱，check() 内嵌字符串。
- 参考解 `reference/extract_neg_slack.py` + `neg_slack.rpt` + `reference_submit.zip`；A 实跑 stdout `TOTAL=12 NEG=5 WORST_SLACK=-1.957 WORST_ENDPOINT=test_so[25]`，B 实跑 `TOTAL=9 NEG=4 WORST_SLACK=-2.483 WORST_ENDPOINT=wb_dat[5]`。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→b / fake_print_expected→i / fake_core_deleted→l / naive_wrong_neg→f / naive_hardcode_a→n），NEG_RC=0 全 FAIL，5 个不同标签。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 1568→14221B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-021 → done；剩 Digital-022/023 待整改（下轮第一件事）。
