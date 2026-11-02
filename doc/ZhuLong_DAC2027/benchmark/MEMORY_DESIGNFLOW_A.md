WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: shard A 断言闸门整改阶段。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：rewrite_queue 优先（断言闸门），清零后 trace_ledger.py --shard A next → claim → 深读 → 合成
- 📊 trace 覆盖率：见 designflow/trace_ledger.py --shard A stats
- 🎯 通过率: 0/0（A 档尚未实跑；先清断言债）
- 🧾 断言: k_rationale=k_check 达标（今日 2/4 达标：Digital-010 k=19 / Digital-021 k=17）· 队列剩 2/4（Digital-022/023 待整改）

### 2026-11-02 shard A 轮 2：Digital-021 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-021`（digital, PrimeTime 时序报告负 slack 路径提取, L1 离线 Python）标 `incomplete`：jsonl test 字段是旧 1568B 弱判分（4 packed 条件），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-021/check.py` 从 4 packed 条件 → 17 独立标签 (a)-(q)：
  (a)zip2files / (b)py_compile / (c)print-token-TOTAL/NEG/WORST_SLACK/WORST_ENDPOINT / (d)A-exit0 / (e)A-TOTAL=12 / (f)A-NEG=5 / (g)A-WORST_SLACK=-1.957 / (h)A-WORST_ENDPOINT=test_so[25] / (i)A-rerun-rpt-7fields / (j)A-rerun-rpt-test_so[25] / (k)A-rerun-rpt-(-1.957) / (l)A-rerun-rpt-exactly-5-Path-headers(no-MET) / (m)B-exit0 跨输入守护 / (n)B-TOTAL=9 / (o)B-NEG=4 / (p)B-WORST_SLACK=-2.483 / (q)B-WORST_ENDPOINT=wb_dat[5]
- 隐藏 B 附件 `assets/.../hidden/pt_reg2out_B.tarpt`：9 paths / 4 VIOLATED / worst -2.483 @ wb_dat[5] / func_ss_m125c_cbest_T + shift_tt_25c_cworst_T 视角，与 A(12/5/-1.957/test_so[25]) 结构性不同；B 不进 SUT 沙箱，check() 内嵌字符串。
- 参考解 `reference/extract_neg_slack.py` + `neg_slack.rpt` + `reference_submit.zip`；A 实跑 stdout `TOTAL=12 NEG=5 WORST_SLACK=-1.957 WORST_ENDPOINT=test_so[25]`，B 实跑 `TOTAL=9 NEG=4 WORST_SLACK=-2.483 WORST_ENDPOINT=wb_dat[5]`。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→b / fake_print_expected→i / fake_core_deleted→l / naive_wrong_neg→f / naive_hardcode_a→n），NEG_RC=0 全 FAIL，5 个不同标签。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 1568→14221B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-021 → done；剩 Digital-022/023 待整改（下轮第一件事）。

### 2026-11-02 shard A 轮 3：Digital-010 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-010`（digital, 4 通道 16-bit 带饱和乘累加器 MAC RTL + VCS 功能仿真, L2 真跑 VCS）标 `incomplete`：jsonl test 字段是旧 1123B 弱判分（k_check=0，substring-only），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-010/check.py` 从 0 实质条件 → 19 独立标签 (a)-(s)：
  (a)zip5files / (b)module-mac4 / (c)endmodule / (d)acc0-3 / (e)pos-sat-7fffffff / (f)neg-sat-80000000 / (g)wide-intermediate-longint / (h)submit-log-PASS / (i)submit-log-no-FAIL / (j)vcd-structure(>200B+$timescale/$enddefinitions/$var) / (k)VCS-A-compile-run / (l)A-PASS / (m)A-no-FAIL / (n)VCS-B-compile-run / (o)B-PASS / (p)B-no-FAIL / (q)checkpointB1-asym(7fffffff 80000000 0000002b 00000032) / (r)checkpointB6-neg-sat(80000000 x4) / (s)checkpointB7-post-reset-small(000f4240 x4)
- TRUE L2 grader：check() 在 .75 上用 VCS R-2020.12 重跑候选 mac4.v 对 (1) 原始可见 tb A（从 workdir 附件读，非提交件，防篡改）+ (2) 内嵌隐藏 tb B（结构性不同：非对称 per-lane / en=0 hold / 中途 reset / 负饱和 / 复位后小正值）。仅打印假日志或硬编码 A 向量者无法过 B 重跑。golden sat32 用 sized 64-bit 字面量（VCS R-2020.12 安全）。
- 隐藏 B 内嵌 check.py 字符串 `_TB_MAC4_B`（不进 SUT 沙箱）；经验值 B1=7fffffff 80000000 0000002b 00000032 / B6=80000000 x4 / B7=000f4240 x4。
- 参考解 `reference/mac4.v`（longint 中间量 + sized-literal sat32）+ `reference_submit.zip`；A 实跑 5 checkpoint 全 PASS(7fffffff/00000000/c0008000/80010000/80000000)，B 实跑 7 checkpoint 全 PASS。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→d / fake_print_expected→l(fresh-VCS-A-run 检测 acc=0≠golden, 击败 log-fake 攻击) / fake_core_deleted→e / naive_no_wide→g / naive_never_saturate→e），NEG_RC=0 全 FAIL，5 个不同标签。fake_print_expected 结构合法(过 b-j)仅在全新 VCS 重跑(l)失败——真正测试 L2 log-faking 防御。
- 闸门：k_rationale=19=k_check=19≥8 ✓；jsonl test 1123→13297B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- .75 sandbox 会话 `shardA_20261102-...Digital-010-rebuild_0`：declare_done + close_session(keep=false) 已清理。
- 队列 `rewrite_queue.tsv` Digital-010 → done；与 Digital-021 共计今日 2/4 达标，剩 Digital-022/023 待整改。
