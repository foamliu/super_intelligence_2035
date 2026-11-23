# mxct2 深读笔记 — junxu block-sim FineSim LSF 提交流（r1077 选料）

- **session**: `1791533874882_mxct2`（junxu @ hfeg0pkn005, mc=150, forked from atqf4）
- **title**: 调用 block-sim skill 对 cli_test lib fifo3x8 进行仿真
- **cwd**: `/home/junxu/Agents/custom_design_skill`，model deepseek-v4-flash
- **size**: 146 msgs / 705KB（嵌套路径 `sessions/1791533874882_mxct2/1791533874882_mxct2.messages.json`）
- **terminal**: `failed_external_process_exit`

## 对话流（user 意图 → assistant 工具链）

- **U0/title**: 调用 `/home/junxu/.cline/skills/block-sim` 对 `cli_test_lib / fifo_3x8` 仿真。
- msg 18-70: assistant 探环境（`list_allowed_files` / `read_files`），发现 `train/iejoad_test` 项目、Virtuoso bridge 在 `hfeg0plg17:59759`、`fifo_3x8` 已有历史仿真（Sep 15 2026）。`extract_results.py` 打印 5 corner 测量表（tt_25c_0.9v / ss_-40c_0.88v / ss_130c_0.88v / ff_130c_1.15v / ff_-40c_1.15v），含 `error` 与 FF corner 负延迟异常。
- **U71「重新仿真」**: assistant 跑 `extract_netlist.py --lib cli_test_lib --cell fifo_3x8 --ip 172.16.8.162 --port 59759`（msg 76）→ 成功：`is_flat=true`, `check.errors=0`, `nlchk_report` 12 项全 Pass, `foregnd_log` 含 "End netlisting Sep 30 09:31:33 2026"（msg 77）。
- **U87「确认提交仿真」**: `run_simulation.py --sim-dir ... --sp si.inp --timeout 600`（msg 88）→ **失败**：`Result: {'success': False, 'error': 'Failed to submit or track job (done)'}`（msg 89）。
- msg 90-100: 排查 `bsub`：`/apps/lsf/10.1/linux2.6-glibc2.3-x86_64/bin/bsub` 在 PATH，但 `bsub -K` 模式解析问题。读 `runscript_v3.sh` / `lsf_v3.out`（历史成功提交，无 `-K`）。
- msg 116: `check_lsf2.py` — LSF env vars 空，`/etc/lsf.conf` NOT FOUND，`/apps/lsf/10.1/conf/` NOT FOUND。
- msg 120: `submit_sim2.py` 设 `LSF_ENVDIR=/apps/lsf/conf` `LSF_TOP` `LSF_MACHDEP` → `bsub` 仍失败：`lsb_init: Failed in an LSF library call: Bad configuration environment, something missing in lsf.conf?. Job not submitted.`（returncode 255）
- **U112「你如何判定 LSF 没有配置」**: assistant 复查。
- msg 124: `debug_lsf.py` — hostname 实为 `hfeg0pkn003`（非 daemon 提示的 hfeg0plg17），`/apps/lsf/conf/lsf.conf` 存在且配置完整（LSB_SHAREDIR/LSF_CONFDIR/...）。
- msg 128: `debug_lsf2.py` — `lsf.cluster.HFDESIGN` 第 1666 行 `hfeg0pkn003  !  !  1  ()`，主机已登记。
- msg 132: `submit_sim3.py` **`source /apps/lsf/conf/profile.lsf` 后提交** → 成功：`Job <883793> is submitted to queue <normal>.`，轮询 `[10s] RUN` → `[30s] EXIT`，`=== Job 883793 finished: EXIT ===` + `✅ FineSim Successfully Completed!`（bjobs 显示 EXIT 但仿真成功）。结果表 5 corner，含 error 与 FF 负延迟。
- msg 133: 最终报告 — 5 阶段管线状态 + 结果表 + 已知问题（SS_-40 error、FF 负延迟、FF tfull_assert error）。
- **U134「wv-cli 重启一下」/ U138「参考 block-sim 仿真」/ U139「YIO R 对比」/ U143「不要把文件放到 work 区」**: 后续 wv-cli / 文件放置问题，与本 case 无关。

## reframe 选择（与 r1071 区分）

r1071 (`57i4y` FinesimMt0ParserProduce) 已把 `extract_results.py` 的 .mt0.csv 解析占走。mxct2 的**独特子任务**是 msg 89-132 的 **LSF 提交环境诊断 + bsub 输出解析**：`bsub` 因 `LSF_ENVDIR` 未导出而 `lsb_init` 失败 → `source profile.lsf` 修复 → `Job <883793>` 成功 + 轮询 RUN→EXIT + FineSim success 标记。

**reframe**: `lsf_submit_diag.py <env_probe.json> <bsub_log.txt> <out.json>` —
1. 环境诊断：`lsf_ready`（`LSF_ENVDIR` 设置 **或** `profile_lsf_candidates` 非空，且 hostname 在 cluster）+ `missing_config` 列表 + `recommended_fix`（`source <profile.lsf>`）。核心齿 = profile.lsf 救回缺 LSF_ENVDIR 的 rescue 分支。
2. bsub 日志解析：`job_id` / `queue` / `submit_status` / `error_message` / `poll_events` / `final_status` / `sim_success` / `n_corners` / `n_error_corners` / `n_negative_measurements`。

**case = EDA-Eval-DesignFlow-LsfSubmitDiagProduce-001**（k=17 a-q, L1 纯 Python 无 EDA 依赖）。
- **A**: 真实 env_probe_A（hostname hfeg0pkn003, LSF_ENVDIR=/apps/lsf/conf, /etc/lsf.conf missing, profile /apps/lsf/conf/profile.lsf）+ bsub_log_A（msg 132 原文：Job 883793, queue normal, RUN@10s→EXIT@30s, FineSim success, 5 corner 含 error/负延迟）。
- **hidden B**: 异主机 hfeg0plg042 / env_vars 空（LSF_ENVDIR 未设置，测 rescue 分支）/ profile /opt/lsf/conf/profile.lsf / Job 774512 / queue long / RUN@15s→DONE@45s / 4 corner (typ/wcl/lt/ht) / 1 error corner / 2 负 temper。B 全值异 A。
- **check 17 条**: a(zip+compile+size) b(3-seed exit0+非空) c(顶层键) d(lsf_ready true rescue) e(missing_config 精确 2 项) f(fix 含 /opt 路径) g(job 774512) h(queue long) i(submit success) j(final DONE 异 A EXIT) k(sim_success true) l(poll_events) m(n_corners 4) n(n_error_corners 1) o(n_negative 2 异 A 6) p(anti-hardcode 5 维) q(3-seed sha256)。
- **3 negs**: neg_empty(→a/b) / neg_print_only(硬编 A 5 值→g/h/f/j/m/p) / neg_core_removed(删 profile.lsf rescue→lsf_ready false + missing 1 项→d/e)。
- **自验**: REF 17/17 PASS ✓; A oracle(corners5/err3/neg6/EXIT/883793) ✓; B oracle(corners4/err1/neg2/DONE/774512/ready/missing2/fix/opt) ✓; negative_selftest 3/3 FAIL ✓; §4.9 三假齐 ✓。
