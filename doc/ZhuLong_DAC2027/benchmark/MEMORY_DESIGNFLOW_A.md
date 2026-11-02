WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: shard A 新 case 合成阶段。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：trace_ledger.py --shard A next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_A.jsonl → 日报
- ✅ DEBT 已清零：`EDA-Eval-DesignFlow-TimingECO-001` 本轮交付（check.py 14 断言 + reference + 5 negative + self-verify 全过）。
- 📊 trace 覆盖率：8/1001 = 0.8%（covered=8 · touched=9 · parked=1；A jsonl 9 条）
- 🎯 通过率: 0/0（A 档尚未实跑）· B 档目标 20–30%
- 🧾 断言: k_rationale=k_check 达标（断言债已清零，存量全达标；本轮 TimingECO-001 k=14）
- 📦 体积：TASK≈17KB / MEMORY≈待测

### 2026-11-02 shard A 轮 8：TimingECO-001 交付 ✓（DEBT 清零，WAITING: 0）
- 交付 `EDA-Eval-DesignFlow-TimingECO-001`（domain=verification，L2，track=faithful，trace 1792572733650_pfubi / e0046913 / hfeg0plg52 / mc=153）。
- gold flow（reference_submit.zip）：run/run_demo.csh（3 阶段 signoff→eco→resignoff 自检，条件化 PASS）+ run/run_eco.csh（参数化 launcher，-design/-corner/-mode/-stage/-eco_types/-buffer/-profile）+ scr/main_eco.tcl + scr/1_setup..10_rpt.tcl（10 编号 tcl）+ setup/common_setup.tcl（DESIGN/CORNER/MODE/ECO_STAGE/ECO_BUFFER_LIST/LIB_PROFILE 变量化，core_typ.db）+ README.md（三阶段 + ICC2 handoff）。
- check.py 14 条独立断言 a-n：(a) zip 15 文件齐全 (b) run_demo.csh cshell+三阶段 (c) 编号 tcl 1..10+main (d) 8_eco.tcl `fix_eco_timing -type hold` 真引擎 (e) run_eco.csh 含 pt_shell + run_demo.csh 条件化 PASS（exit 1 在 PASS 之前）(f) 7_signoff.tcl 写 SETUP_VIOL=/HOLD_VIOL= summary (g) 8_eco.tcl eco_changes+ADDITION+eco_applied.flag (h) 9_resignoff.tcl post.summary (i) **跨输入守护 B**：tclsh 子进程 source common_setup.tcl with DESIGN=eco_demo_B/PT_CORNER=ss0p7v125c → OUT_PREFIX=eco_demo_B_ss0p7v125c_func_signoff（非 A 的 tt0p8v25c）(j) common_setup.tcl 引用 core_typ.db + 变量化 (k) ${OUT_PREFIX} 命名 (l) run_eco.csh switch -design/-corner/-mode/-stage (m) README 三阶段+ICC2 (n) eco_changes.icc2tcl insert_buffer。
- L1-boundary grader（与本 bench 现有 L2 case 同惯例：真 pt_shell 跑在 GOLD 标准创建期，已 .75 真实验证 A HOLD=4→插 4×clk1a27→post HOLD=0；B HOLD=6→插 9×clk1a27→post HOLD=0）；check.py 本地静态 + tclsh 子进程跨输入守护（§4.2 subprocess on B）。
- 自验：gold check() PASS（14/14）+ 5 negative 全 FAIL（fake_empty→a, fake_print_expected→e, fake_core_deleted→d, naive_hardcode_a→i/l, naive_no_eco_engine→d/g）+ §4.9 (a)(b)(c) 三假 FAIL。NEG_RC=0。
- 断言闸门：k_rationale=14 == k_check=14 ≥ 8 ✓。追加 EDA-Eval-DesignFlow_A.jsonl（A jsonl 现 9 条）。mark case 1792572733650_pfubi（补全 user=e0046913/host=hfeg0plg52/domain=verification/match=153）。日报 report_benchmark_11_02.html 50 cases，k(断言)/k(check)/一致 = 14/14/✓。
- ⬜ 下轮：trace_ledger.py --shard A next 选新 trace 开第 10 条 case。
