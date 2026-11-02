WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 回 §3 合成新 case（运维令 §四.3 cline 重跑样本已扩 3 条，本轮按任务卡回合成路径）。本轮交付 `EDA-Eval-DesignFlow-InnovusLaunchDiag-001`（eda_other / L2 / B 档）—— 真实 trace `1792491091764_qk0vo`（pdong / 10.129.8.230 / mc=49）：innovus 2231 在 RHEL8 登录节点 module avail 有却 `-version` 报 `libssl.so.10` 缺失；真因双重（RHEL8 无 openssl1.0 兼容库 + eda-agent LD_LIBRARY_PATH 污染 libstdc++ GLIBCXX_3.4.26）；修复 = bsub 切 CentOS7 节点 / 装 compat-openssl10 + `env -u LD_LIBRARY_PATH`。case = 写启动就绪诊断脚本 `check_launch.py`，读证据目录 fixture 输出结构化 JSON 报告。
- ✅ **本轮交付**：`InnovusLaunchDiag-001` 合成 ✓ —— assets/InnovusLaunchDiag-001/（prompt.txt + task_brief.md + evidence/ 10 个真实 A fixture + hidden/B_evidence 结构不同场景 calibre 2024.4/RHEL9.3/libncurses.so.5/无污染 + hidden_manifest.json）+ reference/InnovusLaunchDiag-001/（check.py 17 条断言 a–q 自包含嵌入 B 证据 + reference_submit/check_launch.py 参考解 + negative/ 3 个错解 + negative_selftest.py）。自验全过：ref check.py 跑 ref_submit.zip = PASS；negative_selftest 3 错解全 FAIL；断言闸门 k_rationale==k_check==17≥8 ✓；日报三列 17/17/✓。
- ✅ DEBT 已清零。
- 📊 trace 覆盖率：20/1001 = 2.0%（covered=20 · touched=22 · parked=2；A jsonl 现 21 条）
- 🎯 通过率: cline+hook 存量重跑仍 **1/3**（本轮无 cline 重跑，纯合成）；新 case 未跑 pi/cline，标「未跑」
- 🧾 断言: k_rationale=k_check=17 ✓（今日 1/1 新 case 达标；存量全达标）
- 📦 体积：TASK≈23.8KB / MEMORY_A≈13.5KB
- 🔒 泄漏隔离: check.py/reference/hidden 不进 SUT workdir；判分独立跑（check.py 自包含嵌入 B 证据，无外部路径依赖；SUT 只见 assets/evidence/ A 场景）
- ⚠️ 运维令进度（跨 shard ops）：cline_eval_status.jsonl 仍 3 行（上轮 PwrGlobals-001 后未新增 cline 重跑）。**待办**：下轮可继续 cline L2 重跑（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001 / InnovusLaunchDiag-001）或继续合成（trace_ledger --shard A next）。


### 2026-11-03 shard A 轮 23：InnovusLaunchDiag-001 合成 ✓（eda_other / L2 / B 档，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。`trace_ledger.py --shard A next` 取候选 → 在 .75 上按 shard-A 工具过滤（innovus/pt_shell/dc_shell/verdi 等）排序，挑 digital-dominant 候选 `1792491091764_qk0vo`（pdong / 10.129.8.230 / mc=49 / innovus 359 主导，analog 工具极少）→ claim（domain=eda_other）。
- **深读**：scp `1792491091764_qk0vo.messages.json`（90KB / 33 msgs）到 .75 workdir 解析。真实任务：用户在 RHEL8 登录节点 `module avail` 有 innovus 多版本，`module load 2231_s119_os7` 后 `innovus -version` 报 `libssl.so.10: cannot open`。agent 先误判「不需 bsub」(#11)，用户「你确定吗」(#12) → 重测发现：①RHEL8 系统只有 libssl.so.1.1（openssl 1.1），无 libssl.so.10（openssl 1.0/CentOS7 代际）；②ldd 揭示更多缺失（libjvm/libmlpack/libarmadillo/libfvengine/libzmq）+ **libstdc++ 污染**（eda-agent 自带 libstdc++.so.6 经 LD_LIBRARY_PATH 抢占，GLIBCXX_3.4.26 not found）。最终结论：需 bsub 切 CentOS7 节点或装 compat-openssl10 + `env -u LD_LIBRARY_PATH`。深读笔记落 `designflow/trace_deepreads/1792491091764_qk0vo_innovus_launch_diag.md`。
- **合成**（EDA-Eval-DesignFlow-InnovusLaunchDiag-001，B 档 / eda_other / L2）：交付 `outputs/submit.zip` 内 `check_launch.py` —— 启动就绪诊断脚本，接口 `--evidence-dir <dir> --module <name> --version <ver>`，读 10 个固定文件名证据 fixture（module_avail/bin_path/exec_stdout/exec_rc/ldd_out/os_release/lib_search/env_ldpath/module_show/exec_stderr），输出结构化 JSON（module_avail/module_load_ok/binary_path/exec_ok/missing_libs/os/lib_provider_mismatch/ldpath_pollution/verdict/recommended_action 等）。
  - **A（SUT 可见）**：`assets/InnovusLaunchDiag-001/evidence/` = qk0vo 真实证据（innovus 2231 / RHEL8 / libssl.so.10 缺失 / libstdc++ GLIBCXX 污染）。
  - **B（隐藏）**：`assets/InnovusLaunchDiag-001/hidden/B_evidence/` = 结构不同场景（calibre 2024.4_u2024.10 / RHEL 9.3 / libncurses.so.5 缺失 / 系统只有 libncurses.so.6 / **无** LD 污染）—— check.py 只跑 B。
  - **check.py**（17 条断言 a–q）：自包含嵌入 B 证据（无外部路径依赖，判分独立可跑）；subprocess 执行候选 → 解析 JSON → 断言 module_avail 含目标版本 / module_load_ok / binary_path 含 calibre / exec_ok==false / missing_libs 含 libncurses.so.5 / lib_provider_mismatch==true / ldpath_pollution==false / os.version 以 9 起头 / verdict==not_launchable_on_this_node / recommended_action 含 bsub|centos|rhel7|compat / 3-seed 随机化 verdict+mismatch+pollution 一致 / 退化回归（变体证据 libreadline.so.6 必被检出且 libncurses.so.5 消失，击穿硬编码）。
- **自验全过**：①ref check.py 跑 ref_submit.zip = **PASS**；②negative_selftest：naive_always_launchable / stub_hardcode_A / print_B_expected 三错解 **全 FAIL**；③断言闸门 k_rationale==k_check==17≥8 ✓；④日报三列 17/17/✓（修了 check.py 标签格式以匹配 gen_daily_report._k_check 的 `# (x)` 注释模式）。
- 台账 `mark --status case --case-id EDA-Eval-DesignFlow-InnovusLaunchDiag-001`。merge_shards → 主 jsonl 99 条 → 日报 regen。新 case 未跑 pi/cline（标「未跑」）。
- ⬜ 下轮：①cline L2 重跑扩样本（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001 / InnovusLaunchDiag-001 本条）；或 ②继续合成（trace_ledger --shard A next）。

### 2026-11-03 shard A 轮 22：PwrGlobals-001 cline+hook 重跑 = FAIL（能力不足·L2，WAITING: 0）
- 运维令 §四.3「逐步把存量 case 用 cline 重跑」继续。挑 shard-A L2 case `EDA-Eval-DesignFlow-PwrGlobals-001`（pnr_signoff / Innovus init-globals：合成 gui/power.globals + setup/common_setup.tcl + README.md 三文件 Tcl 流程，check.py 20 条断言 (a)-(t) 含 tclsh stub 跨输入守护）。
- **重跑**：`bash run_one.sh EDA-Eval-DesignFlow-PwrGlobals-001`（harness 轮 21 修复版：cline 用 write_to_file 写 outputs/，harness 打包 submit.zip）。cline exit=超时（CLINE_TIMEOUT=1500s，实际 wall 1873s——cline --timeout 未硬杀，run_one.sh 被 outer shell 30min timeout 终止；status 由我手动补录）。
- **cline 行为分析**（session jsonl 9.5MB）：47 iterations / 27657 content_start events（大量 reasoning token 生成）/ 188 MCP-named tool ref / **0 次 write_to_file 到 outputs/**。卡死根因：① cline 调 `spawn_agent`/`team_spawn_teammate` 子代理工具 3 次全报错（`undefined is not an object (evaluating 'e.trim')` / `Unrecognized key: "files"` / `Invalid input: expected string, received undefined at agentId`）；② iter 38 触发 auto-compaction（115618→38293 tokens, 77→15 msgs, triggerTokens=115200/maxInput=128000）——上下文爆炸后压缩，循环往复但无产出。outputs/ 目录空，harness 3b 步无可打包文件。
- **失败归因 ③能力不足**（非 ①交付形态/位置错、非 ④判分歧义、非 hook/泄漏）：cline 在「合成多文件 Innovus Tcl 流程」这类需要长程规划+多文件协同的任务上 thrash；对照 PTSignoff-001（单文件 pt_sta.tcl + 复用附件 setup）cline 237s 一次过——cline 能力曲线对任务复杂度敏感。**对评测集是正向信号**：PwrGlobals-001 在 pi 下通过、cline 下 FAIL，符合「难度校准到通过率 20–30%」目标方向。
- **防泄题自验**：grep cline_session.jsonl 命中 `check.py`/`_reference_check.py`/`reference_submit.zip`/`hidden_manifest.json`/`reference`/`hidden` = **0 次**；hook 未触发（cline 0 次 run_commands，全走 MCP+思考+子代理 spawn）；workdir leak 自检通过。判分独立：outputs 空 → 直接判 FAIL（no submit.zip），check.py 未进 cline cwd。
- status jsonl 追加第 3 行（failure_class=③capability-insufficient）。cline_eval_status.jsonl：Verification-001 FAIL·L1·hook / PTSignoff-001 PASS·L2 / PwrGlobals-001 FAIL·L2·能力 = **1/3**。
- ⬜ 下轮：①继续 cline L2 重跑（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001，扩样本到 ≥5 再看通过率趋势）；或 ②回 §3 trace_ledger --shard A next 合成第 21 条新 case（需先 next/claim）。本轮 40min 预算耗尽于 cline 1500s 跑空，未开新 case。

<!-- 已归档轮 8-13 → ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 49（体积闸门）。指针： -->
<!-- 2026-11-02 shard A 轮 13：PwrGlobals-001 交付 ✓（A 档 trace-faithful / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 49 -->
<!-- 2026-11-02 shard A 轮 12：PTSignoff-001 交付 ✓（case 合成，WAITING: 0） → 已归档 ARCHIVE 批次 49 -->
<!-- 2026-11-02 shard A 轮 8：TimingECO-001 交付 ✓（DEBT 清零，WAITING: 0） → 已归档 ARCHIVE 批次 49 -->
<!-- 2026-11-02 shard A 轮 9：cline 迁移 run_one.sh + Verification-001 cline 重跑（运维令 §四 执行） → 已归档 ARCHIVE 批次 49 -->
<!-- 2026-11-02 shard A 轮 10：CoreTimingSig-001 交付 ✓（case 合成，WAITING: 0） → 已归档 ARCHIVE 批次 49 -->
<!-- 2026-11-02 shard A 轮 11：InnovusAudit-001 交付 ✓（A 档 trace-faithful / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 49 -->

### 2026-11-02 shard A 轮 21：PTSignoff-001 cline+hook 重跑 = PASS ✓（运维令 §四 执行·L2 防泄题验证，WAITING: 0）
- 运维令「被测换 cline + PreToolUse hook」§四.2「拿一条 PASS case 用 cline+hook 重跑验证」执行。挑 shard-A 唯一 pi-PASS 且判 L2（pnr_signoff / PrimeTime STA 签核，真跑 pt_shell on .75 金标准）的 `EDA-Eval-DesignFlow-PTSignoff-001`。
- **harness 修复（run_one.sh，shard-A 专用文件，不动 run_one_C/D.sh）**：
  - ① **cline 无法自建 submit.zip 的根因**：PreToolUse hook 把所有内置 `run_commands`/`bash`/`shell` redirect 成一条 echo NOTICE（防泄题：阻止 cline 跑本地 shell 接触仓库敏感区/判分器）。但 cline 交付 zip 必须跑 `zip` 命令 → 被拦 → Verification-001 因此无 submit.zip 而 FAIL。**修复**：改 prompt 让 cline **用 write_to_file 工具直接把交付件写到 `outputs/<内部路径>/`**（write 工具在 hook 白名单内、workspace 内放行），cline 不打包；run_one.sh 在 cline 退出后 **新增 step 3b** 由 harness `zip -r outputs/submit.zip .` 打包。防泄题不破：cline 全程不接触 check.py/reference（判分仍独立在 /tmp/judge 跑），只是把"建包"职责从 cline 移到 harness。
  - ② **attachments 复制 bug**：jsonl 的 `attachments[].source` 写的是 `assets/<task_id>/<name>` 全路径，原 python 复制逻辑又拼一次 `ASSETS_SRC` → 路径错、复制 0 个附件（dry-run 实测 `attachments copied: []`）。**修复**：改按 `attachments[].name` 在 `ASSETS_SRC` 内取文件。修复后 dry-run 复制 5/5 附件 OK。同步修了 judge 端附件复制循环（同样 bug，print source 改 print name）。
- **重跑结果**：`bash run_one.sh EDA-Eval-DesignFlow-PTSignoff-001` → cline exit=0 / dur=237s / 4 个交付件写齐（tcl/pt_sta.tcl + setup/common_setup.tcl + run_pt.csh + README.md，内部目录结构正确）→ harness 打包 submit.zip → 独立判分 `/tmp/judge_*/` check() = **PASS (True)**。
- **防泄题自验**：grep cline_session.jsonl 中 `check.py`/`_reference_check.py`/`reference_submit.zip`/`hidden_manifest.json`/`reference`/`hidden` 命中 **0 次**（cline 从未尝试读判分器/答案）；session 日志含 7 次 hook redirect 记录（run_commands→echo NOTICE 生效，cline 收到 NOTICE 后改用 write 工具 + MCP 工具）。workdir leak 自检通过（find 无 check.py/reference/hidden）。
- **判分独立性**：check.py 从 `benchmarks/EDA-Eval-DesignFlow/reference/PTSignoff-001/check.py` 复制到 `/tmp/judge_*/`（cline workdir 外），A 附件同复制，python 独立进程跑 `check('submit.zip','.')`。判分器**绝不进 cline cwd**。
- status jsonl 追加：`{"ts":"2026-11-02T15:22:39Z","task_id":"EDA-Eval-DesignFlow-PTSignoff-001","harness":"cline","model":"deepseek-v4-pro-cloud","thinking":"medium","dur_sec":237,"cline_exit":0,"verdict":"PASS","reason":"True","hook":"PreToolUse"}`。cline_eval_status.jsonl 现 2 行（Verification-001 FAIL + PTSignoff-001 PASS）。
- ⚠️ 运维令进度：「被测换 cline + PreToolUse 防泄题 hook」**§四.2 验证通过**——hook 生效（cline 读 workdir 外文件被拦、run_commands→echo）、cline 看不到 check.py（0 泄漏尝试）、判分独立跑结果真实（L2 PASS）。**§四.3 待办**：逐步把存量 case 用 cline 重跑（L2 case 现已不被 harness 阻塞；L1/offline case 仍受 hook 的 run_commands→echo 限制，需单独决策是否为 L1 放行 in-workspace run_commands，或保持 L1 只用 pi 评）。
- ⬜ 下轮：①继续挑 shard-A L2 case 用 cline+hook 重跑（候选：ETMExtract-001 / TLEFRules-001 / PwrGlobals-001 / SynLintFlow-001 / CosimSetup-001 等，扩大 cline 通过率样本）；或 ②trace_ledger.py --shard A next 开第 21 条新 case 合成。

### 2026-11-02 shard A 轮 20：CovFMFlow-001 交付 ✓（A 档 trace-faithful / digital·verification，WAITING: 0）
- 选 trace：trace_ledger.py --shard A next → mc≥300 候选多为 calibre/hspice（shard C 域）。Python 评分按 digital-tool 主导 + analog 反向过滤（dig>ana, dig≥5），挑纯数字会话 `1792395564570_r3gb7`（lorikx/hfeg0pkn005/mc=203/netlist=242 synthesis=74 innovus=4 → digital/verification，400 msgs/1.4MB）claim → mark case。lorikx 已在轮 14 (SynLintFlow-001/lond8) 出现但本会话 r3gb7 是同项目不同 session 不同任务（cov+fm 流程），复用用户可接受。
- 深读：400 msgs；8 条 user text 轮。A档选轮 #222 逐字原文『再开两个文件夹，一个做覆盖率检查，另一个做形式验证，老样子还是参考那个文件夹内的内容去做』—— 纯「提出需求」无根因/修复 → 合 A档选轮规则。真实任务 = 在 freq_calibration_model (cfreq_ctrl VCO 校准模块) 项目新建 cov/ (VCS Code Coverage line+cond+fsm+tgl+branch + URG) 与 fm/ (Synopsys Formality RTL-vs-DC网表 LEC) 两套独立流程目录，参考 syn/ Makefile+setup 模式。从 .75:/home/lorikx/freq_calibration_model/ 取回真实金标准 10 文件（fm/{Makefile,README,SourceMe,data/filelist_fm.f,scripts/fm.tcl,setup/common_setup.tcl} + cov/{Makefile,README,SourceMe,data/filelist_cov.f}）。FM 实跑 Verification SUCCEEDED (88 比较点 6 Port+82 DFF 全等效/16s)；cov 流程结构正确但覆盖率数据记录受 VCSTools_Net/VT_CoverageURG license 限制（真实调试: 运行时 -cm_dir 重复传入致 No VCS Code Coverage Metrics monitored, 修复为 run target 不传运行时 -cm_dir）。用户接受（#355 转向新任务 verdi 网表查看）。inline 深读，未单写笔记文件。注意 .75 ssh 到 hfeg0pkn005 是 login-node pool 有 NFS 挂载抖动，需重试 + 用正确子目录路径 sessions/<sid>/<sid>.messages.json。
- 合成（A 档 / L1-boundary / digital·verification）：prompt.txt = #222 逐字原文；task_brief.md ≤3 行只写交付接口。金标准 = 真实 10 文件入 reference_submit.zip（fm/+cov/ 结构 verbatim）。资产 A = rtl_synth/cfreq_ctrl.v (真实 RTL 358 行) + sim/tb_cfreq_ctrl_synth.v + sim/vco_fb_model.v + syn/setup/common_setup.tcl + syn/Makefile (真实模式参考) + workspace_listing.txt + prompt + task_brief，无说明性注解。隐藏 B = hidden/common_setup_B.tcl (design=dco_trim_top/tech=SMIC28/PDK=/apps/pdk/SMIC28/corner=ss_0p9v_m40c) + filelist_fm_B.f + hidden_manifest.json，结构全异于 A。
- check.py 24 条独立断言 (a)-(x)：静态结构 (a)zip恰含10文件 (b)fm.tcl source common_setup (c)synopsys_auto_setup true (d)set_svf $SVF_FILE+file exists守护 (e)read_db -technology_library (f)read_sverilog -r -vcs $RTL_FILELIST参数化 (g)read_verilog -i $IMPL_NETLIST参数化 (h)set_top r:/WORK/$DESIGN_NAME (i)set_top i:/WORK/$DESIGN_NAME (j)match+verify (k)report_unmatched_points (l)failing/aborted/analyze调试报告 (m)fm/Makefile fm_r2g目标 (n)USE_LSF开关+bsub (o)cov:compile run report一条龙+分步 (p)-cm line+cond+fsm+tgl+branch五类 (q)-cm_dir+-cm_name (r)urg -dir $(VDB) -report (s)run target simv_cov无运行时-cm_dir(真实bug修复) (t)cov filelist≥3源文件；跨输入守护 (u)tclsh stub 跑 fm.tcl 带 B 环境(模拟 Makefile -x) set_top 流过 B 设计 dco_trim_top (v)stub read_sverilog -r 用 B filelist + read_verilog -i 用 B 网表 (w)A 字面量 cfreq_ctrl 不出现在 stub 记录命令 (x)make -n cov/Makefile 带 B DESIGN/TOP 显示 B 且 A 字面量缺席。check.py 内嵌 B common_setup+filelist 自包含，tclsh stub (lsearch 检测 -r/-i，redirect/file mkdir/source 原生) 真跑候选 fm.tcl on B + GNU make -n 干跑 cov/Makefile on B。
- 自验：gold reference_submit.zip check() PASS（24/24）+ 5 negative 全 FAIL（NEG_RC=0，5 distinct labels：fake_empty→a / fake_print_expected→a / fake_core_deleted→j / naive_hardcode_a→h,i,u,w / naive_runtime_cmdir→s）+ §4.9 (a)(b)(c) 三假 FAIL。
- 断言闸门：k_rationale=24 == k_check=24 ≥8 ✓（gate_triple 24/24/✓）。追加 EDA-Eval-DesignFlow_A.jsonl（A jsonl 现 20 条，test==disk roundtrip OK，14753B）。mark case 1792395564570_r3gb7（lorikx/hfeg0pkn005/digital/mc=203）。merge_shards → 主 jsonl 93 cases。日报 report_benchmark_11_02.html 93 cases，本条 24/24/✓。
- A 档试点记账：track=faithful，未 pi/cline 实跑（"未跑"），待 cline+hook 重跑。失败归因预设：①交付形态/位置错→(a) / ②结构缺件/反模式缺位→(b)-(t) / ③能力不足（硬编码 A 字面量）→(w)+(x) / ④判分歧义（对事实严格匹配）→(u)+(v)。
- ⚠️ 运维令进度：同上（待办挑 L2 PASS case cline+hook 重跑）。
- ⬜ 下轮：trace_ledger.py --shard A next 开第 21 条 case；或优先挑一条 L2 shard-A PASS case 用 cline+hook 重跑。

<!-- 已归档轮 14-19 → ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 50（体积闸门）。指针： -->
<!-- 2026-11-02 shard A 轮 19：FlowGuide-001 交付 ✓（A 档 / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 18：SdfWarnFilter-001 交付 ✓（A 档 / verification，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 17：ETMExtract-001 交付 ✓（A 档 / pnr_signoff·PT ETM，L2，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 16：WLMMultibit-001 交付 ✓（A 档 / digital·synthesis，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 15：TLEFRules-001 交付 ✓（A 档 / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 14：SynLintFlow-001 交付 ✓（A 档 / digital·synthesis，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->

