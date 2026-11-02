WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: 运维令「被测换 cline + PreToolUse 防泄题 hook」§四 执行 —— L2 存量 case cline+hook 重跑验证。本轮挑 shard-A L2 PASS case `PTSignoff-001`（pnr_signoff）用 cline+hook 重跑，**结果 PASS**，并修复 run_one.sh harness 的两处阻塞（见轮 21）。
- ✅ **本轮交付**：`PTSignoff-001` cline+hook 重跑 = **PASS**（首条 L2 shard-A case 在防泄题 hook 下 PASS，237s/cline exit 0/独立判分 True）。harness 修复：①run_one.sh prompt 改为「cline 用 write 工具写交付件到 outputs/，harness 退出后打包成 submit.zip」（原 hook 把 run_commands→echo 阻断 cline 自建 zip，所有 case 都卡这）；②attachments 复制 bug（source 含 `assets/<id>/` 前缀，原逻辑再拼一次 ASSETS_SRC 致路径错、复制 0 个附件）→ 改按 `name` 在 ASSETS_SRC 取文件。防泄题自验：cline 0 次尝试读 check.py/reference/hidden（session 日志 grep 命中 0），hook 7 次 run_commands→echo redirect 生效。
- ✅ DEBT 已清零。
- 📊 trace 覆盖率：19/1001 = 1.9%（covered=19 · touched=21 · parked=2；A jsonl 20 条不变，本轮无新 case）
- 🎯 通过率: cline+hook 存量重跑 **1/2 = 50%**（PTSignoff-001 PASS / Verification-001 FAIL·L1/hook 限制）· 样本太小不报百分比 · B 档目标 20–30%（待更多 cline 重跑样本）
- 🧾 断言: 本轮无新 case；存量全达标（PTSignoff-001 check.py 23 条断言 (a)-(w) 在 cline 产出上独立判分 PASS）
- 📦 体积：TASK≈23.8KB / MEMORY_A≈13.2KB（轮 14-19 已归档 ARCHIVE 批次 50）
- 🔒 泄漏隔离: check.py/reference/hidden 不进 SUT workdir；判分独立跑（check.py 24 条断言 (a)-(x)：静态结构 (a)-(t) on fm/+cov/ + tclsh stub 跨输入守护 (u)-(w) 在内嵌隐藏 B common_setup_B.tcl+filelist_fm_B.f 上真跑候选 fm.tcl 校验 B 设计流过 set_top/read_sverilog/read_verilog 且 A 字面量 cfreq_ctrl 缺席 + make -n 干跑 (x) on cov/Makefile 带 B DESIGN/TOP 校验 B 出现 A 缺席；check.py 内嵌 B 输入自包含，不进 cline cwd）
- ⚠️ 运维令进度（最高优先·跨 shard ops）：2026-11-02「被测换 cline + PreToolUse 防泄题 hook」**已在轮 9 启动**——run_one.sh 已建、hook 已部署、Verification-001(L1) cline 重跑 = FAIL（hook 把 run_commands override 成 echo，阻断 L1/offline 本地执行；L2/EDA-via-MCP 不受影响）。**待办**：挑一条 L2 shard-A PASS case 用 cline+hook 重跑验真实通过率（L2 不被 hook 拦）。本轮新交付 CovFMFlow-001 是 L1-boundary，重跑也会被 hook 拦。本轮 shard-A 1-case 40min 预算未启动 L2 重跑；下轮第一件事评估启动。


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

