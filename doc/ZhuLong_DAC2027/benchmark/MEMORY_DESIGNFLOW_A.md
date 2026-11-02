WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 2026-11-02 运维令（用户直令·最高优先）= 被测换 cline + PreToolUse 防泄题 hook。本轮执行该令 §四：建 run_one.sh + 拿 PASS case 用 cline+hook 重跑验证。
- ⚠️ **本轮未新增 case**（按顶部运维令优先于 loop 任务卡的 case 合成）。run_one.sh 已建并验证；Verification-001 cline 重跑 = FAIL（L1/hook 限制，非模型失败，详见下方流水）。
- ✅ DEBT 已清零：`EDA-Eval-DesignFlow-TimingECO-001` 上轮交付（check.py 14 断言）。
- 📊 trace 覆盖率：8/1001 = 0.8%（covered=8 · touched=9 · parked=1；A jsonl 9 条，本轮无新增）
- 🎯 通过率: cline 重跑 0/1（Verification-001 FAIL·L1/hook 限制）· B 档目标 20–30%
- 🧾 断言: 存量全达标；本轮无新 case 故无新断言
- 📦 体积：TASK≈17KB / MEMORY≈待测
- 🔒 泄漏隔离: cline workdir 不含 check.py/reference/hidden（run_one.sh 自检通过）；判分独立跑在 /tmp/judge（check.py 不进 cline cwd）

### 2026-11-02 shard A 轮 8：TimingECO-001 交付 ✓（DEBT 清零，WAITING: 0）
- 交付 `EDA-Eval-DesignFlow-TimingECO-001`（domain=verification，L2，track=faithful，trace 1792572733650_pfubi / e0046913 / hfeg0plg52 / mc=153）。
- gold flow（reference_submit.zip）：run/run_demo.csh（3 阶段 signoff→eco→resignoff 自检，条件化 PASS）+ run/run_eco.csh（参数化 launcher，-design/-corner/-mode/-stage/-eco_types/-buffer/-profile）+ scr/main_eco.tcl + scr/1_setup..10_rpt.tcl（10 编号 tcl）+ setup/common_setup.tcl（DESIGN/CORNER/MODE/ECO_STAGE/ECO_BUFFER_LIST/LIB_PROFILE 变量化，core_typ.db）+ README.md（三阶段 + ICC2 handoff）。
- check.py 14 条独立断言 a-n：(a) zip 15 文件齐全 (b) run_demo.csh cshell+三阶段 (c) 编号 tcl 1..10+main (d) 8_eco.tcl `fix_eco_timing -type hold` 真引擎 (e) run_eco.csh 含 pt_shell + run_demo.csh 条件化 PASS（exit 1 在 PASS 之前）(f) 7_signoff.tcl 写 SETUP_VIOL=/HOLD_VIOL= summary (g) 8_eco.tcl eco_changes+ADDITION+eco_applied.flag (h) 9_resignoff.tcl post.summary (i) **跨输入守护 B**：tclsh 子进程 source common_setup.tcl with DESIGN=eco_demo_B/PT_CORNER=ss0p7v125c → OUT_PREFIX=eco_demo_B_ss0p7v125c_func_signoff（非 A 的 tt0p8v25c）(j) common_setup.tcl 引用 core_typ.db + 变量化 (k) ${OUT_PREFIX} 命名 (l) run_eco.csh switch -design/-corner/-mode/-stage (m) README 三阶段+ICC2 (n) eco_changes.icc2tcl insert_buffer。
- L1-boundary grader（与本 bench 现有 L2 case 同惯例：真 pt_shell 跑在 GOLD 标准创建期，已 .75 真实验证 A HOLD=4→插 4×clk1a27→post HOLD=0；B HOLD=6→插 9×clk1a27→post HOLD=0）；check.py 本地静态 + tclsh 子进程跨输入守护（§4.2 subprocess on B）。
- 自验：gold check() PASS（14/14）+ 5 negative 全 FAIL（fake_empty→a, fake_print_expected→e, fake_core_deleted→d, naive_hardcode_a→i/l, naive_no_eco_engine→d/g）+ §4.9 (a)(b)(c) 三假 FAIL。NEG_RC=0。
- 断言闸门：k_rationale=14 == k_check=14 ≥ 8 ✓。追加 EDA-Eval-DesignFlow_A.jsonl（A jsonl 现 9 条）。mark case 1792572733650_pfubi（补全 user=e0046913/host=hfeg0plg52/domain=verification/match=153）。日报 report_benchmark_11_02.html 50 cases，k(断言)/k(check)/一致 = 14/14/✓。
- ⬜ 下轮：trace_ledger.py --shard A next 选新 trace 开第 10 条 case。

### 2026-11-02 shard A 轮 9：cline 迁移 run_one.sh + Verification-001 cline 重跑（运维令 §四 执行）
- **背景**：顶部运维令（用户直令·最高优先）要求被测 pi→cline + PreToolUse 防泄题 hook。本轮执行 §四.1（建 run_one.sh）+ §四.2（拿 PASS case 用 cline+hook 重跑验证）。优先于 loop 任务卡的 case 合成。
- **交付 `designflow/cline_eval/run_one.sh`**（ops 令 §四.1 唯一硬交付）：部署 hook → 建 workdir（只放 prompt+assets+task_brief，🚫 不放 check.py/reference/hidden）→ headless 跑 cline（`-P openai -m deepseek-v4-pro-cloud --auto-approve true --json --thinking medium`）→ 独立判分（/tmp/judge，check.py 不进 cline cwd）→ 记 `cline_eval_status.jsonl`（harness=cline）。
- **防泄题验证（PASS）**：
  - PreToolUse hook 部署到 `~/.cline/hooks/PreToolUse` + `hook_scope.txt`（本批次根）。
  - 冒烟测试：cline 试图读 scope 外 `/tmp/_leak_secret.txt` → `read_files`/`run_commands` 被 overrideInput 改写为 `/dev/null`/echo，secret 文件完好。**hook 生效确认**。
  - workdir 泄漏自检：`find` 确认无 `check.py/_check.py/reference_submit.zip/hidden` 进 workdir。**cline 看不到 check.py 确认**。
  - cline provider/model headless 跑通：`deepseek-v4-pro-cloud` exit 0。
- **Verification-001 cline 重跑 = FAIL（harness 限制，非模型失败）**：
  - Verification-001 是 **L1/offline** case（需本地跑 `prepare_new_netlist.py` 生成 csv）。
  - PreToolUse hook 把 `run_commands` 一律 override 成 echo（注释：强制走 MCP `mcp__pyAether__run_code` 在 .75 跑 EDA）。对 L2（EDA-via-MCP）case 正确；对 L1/offline case **阻断本地执行**。
  - cline 实测：`run_commands` 2×（被拦）+ `pyAether_MCP_server__run_code` 5×（试图在 EDA 服务器跑离线 python，错场地）+ `read_files`/`search_codebase` 若干；**无 submit.zip 产出**，跑了 ~20min 被 kill。pi 之前用无限制 bash 通过此 case。
  - **结论/findings**：当前 hook 配置只适合 L2；L1/offline case 需改 hook（允许 workspace 内 `run_commands`，或 L1 case 不挂 run_commands→echo 重定向）。已记 `cline_eval_status.jsonl`。
- **并发 hazard（需运维知会）**：本轮发现 shard B（spice_char）并发跑 Schematic-001 于 `~/.cache/cline_eval/`，shard D 在共享 `designflow/cline_eval/` 写了 `run_one_D.sh`。多 shard 同时建 cline harness → **争抢共享 `~/.cline/hooks/hook_scope.txt`**（互相覆写 scope）+ cline_eval/ 目录冲突。已把 scope 文件恢复为两路径共存。建议运维分配每 shard 独立 workdir 根 + 独立 scope 行。
- ⬜ 下轮：若运维令 cline 迁移继续，挑一条 **L2**（EDA-via-MCP）shard-A PASS case 用 cline+hook 重跑（L2 不受 hook 限制，能验真实通过率）；否则回 case 合成开第 10 条。
