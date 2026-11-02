WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: loop 任务卡 case 合成。本轮按 loop 卡合成第 11 条 case（A 档 trace-faithful 试点 +1）。
- ✅ **本轮交付 case**：`EDA-Eval-DesignFlow-InnovusAudit-001`（pnr_signoff，L1-boundary，A 档 faithful，trace 1792489769571_ch2cw / johnl / hfeg0plg49 / mc=255 / innovus=233 主导）。A jsonl 现 11 条。
- ✅ DEBT 已清零。
- 📊 trace 覆盖率：10/1001 = 1.0%（covered=10 · touched=11 · parked=1；A jsonl 11 条）
- 🎯 通过率: 本条 case 未 pi/cline 实跑（"未跑"）；cline 存量重跑 0/1（Verification-001 FAIL·L1/hook 限制）· B 档目标 20–30%；A 档本轮只报数不设目标
- 🧾 断言: 本轮 InnovusAudit-001 k_rationale=k_check=14 ≥8 ✓（日报 14/14/✓）；存量全达标
- 📦 体积：TASK≈17KB / MEMORY≈待测
- 🔒 泄漏隔离: check.py/reference/hidden 不进 SUT workdir；判分独立跑（隐藏 B 上 subprocess，check.py 不进 cline cwd）

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

### 2026-11-02 shard A 轮 10：CoreTimingSig-001 交付 ✓（case 合成，WAITING: 0）
- 选 trace：trace_ledger.py --shard A next → 候选 mc≥300 多为 calibre/hspice（shard C 域）；按 §3 domain 覆盖 + 工具匹配，挑 `1793087996513_u78sz`（hengbow/hfeg0plg49/mc=407，netlist 668 + innovus 18 + hspice 63，verification 域）claim → mark case。
- 深读：511 msgs/2.14MB；真实任务 = DDR5 fullchip coretiming 仿真验证，用 WaveView 看 finesim.fsdb，把 array 中开启地址对应的 WL/BL/coretiming 关键信号写成 .sig（用户反复强调 wv 只认小写、要基于真实 netlist 层次不要猜）。最终接受 `coretiming_signals.sig`（中心宏 `xictop.xi_array8g_t.xi_array1g_bgab01.xi_m512meg_0` 真实层次；WL=`s<Nm<M>wle[U/L]/wlo[U/L]`；dummywl；BL/BLB 在 SA 单元 `xi_lwdrq_msaq_5455.xi_msaq_2sec_0001.xi_msax256_cp00.xi_cxsa_1x16_cbcc_1c2a_1`）。真实 gold 与 sig_demo.sig 均从 .75 `/home/hengbow/zl_job/turboWave/fsdb/` 取到（/proj 公共目录权限拒）。
- 合成（L1-boundary，B档 synthesized，verification）：交付 = `gen_coretiming_sig.py`（读 netlist manifest → 选 coretiming 信号 → 转小写 → 写 WaveView .sig，对任意同结构 manifest 通用）。asset A = `netlist_manifest_A.txt`（中心阵列宏实例+信号名，CamelCase 原始拼写）+ `sig_demo.sig`（格式示例）+ `task_brief.md`。hidden B = `netlist_manifest_B.txt`（结构不同：根 `xdramtop.xi_mem8g_t.xi_bank3.xi_m256meg_1`、WL 前缀 `t<Nm<M>` 非 A 的 `s`、SA/BL 单元下标不同、BL 下标 <5> 非 <11>、dummywl _b3）。
- check.py 14 条独立断言 (a)-(n)：(a)zip 含脚本 (b)py_compile exit0 (c)候选在 hidden B 跑 exit0+产出 (d)≥10 活跃行 (e)WaveView 格式 `signal=<path>.v(<name>)` (f)全小写无 A-Z (g)路径∈manifest_B (h)信号名@路径∈manifest_B (i)四类 WL/dummyWL/BL/SA 各≥1 (j)无重复 (k)跨输入守护 有 B 根无 A 根 (l)选择性 不含 vcc/vss/dataout/addrbus/ck_t/cs_n 诱饵 (m)B 专用 t-前缀 WL (n)B 专用 BL<5>。check 只跑 hidden B（§4.1）。
- 自验：ref check() PASS（14/14）+ 5 negative 全 FAIL（NEG_RC=0：fake_empty→c / fake_print_expected→g / fake_core_deleted→d / naive_hardcode_a→g / naive_dump_all→l）+ §4.9 (a)(b)(c) 三假 FAIL。
- 断言闸门：k_rationale=14 == k_check=14 ≥8 ✓。追加 EDA-Eval-DesignFlow_A.jsonl（A jsonl 现 10 条，test==disk check.py roundtrip OK）。merge_shards → 主 jsonl 55 cases。日报 report_benchmark_11_02.html 55 cases，本条 k(断言)/k(check)/一致 = 14/14/✓。
- ⬜ 下轮：trace_ledger.py --shard A next 选新 trace 开第 11 条 case（或按运维令 §四.3 挑一条 L2 shard-A PASS case 用 cline+hook 重跑验真实通过率）。

### 2026-11-02 shard A 轮 11：InnovusAudit-001 交付 ✓（A 档 trace-faithful / pnr_signoff，WAITING: 0）
- 选 trace：trace_ledger.py --shard A next → mc≥300 候选多为 calibre/hspice（shard C 域）；按 innovus/verification 工具计数排序挑 `1792489769571_ch2cw`（johnl/hfeg0plg49/mc=255/innovus=233 主导/pnr_signoff）claim → mark case。cline v3 目录式 session（`<sid>/<sid>.messages.json`，949KB/158 msgs）。
- 深读：仅 2 条真实用户轮（#0 全文审计提示词、#135「继续」）→ 符合 A 档选轮规则（提出需求，未指出根因/给修复）。真实任务 = 全定制环境下用 Innovus 做 addr_to_rowcol_v7（纯组合/107 实例/18 个 *LVSx 单元）完整数字后端能力审计（只调查、不实现）。金标准 = `.75:/home/johnl/.../dc_addr_to_region/out/innovus_audit/AUDIT_REPORT.md`（仍存，5762B）：Innovus v23.32-s091_1 真实启动验证 OK、SS_0p98_m40c_lvs.db 可读、唯一硬缺口=tech.lef+单元 abstract LEF（须 genlef/ski-genlef 从 OA layout 生成）、纯组合→CTS 不适用、明确未进行正式实现。深读笔记 `designflow/trace_deepreads/1792489769571_ch2cw_innovus_audit.md`。
- 合成（A 档 trace-faithful / L1-boundary / pnr_signoff）：prompt.txt = 用户原话逐字（无脱敏，路径/用户名/SPICE 原文保留）；交付 = `run_audit.py`（参数化 --netlist/--manifest/--outdir → AUDIT_REPORT.md，对任意同族电路通用）；A = mapped.v（v7/107/SS/min 缺）+ mapped.sdc + lib_manifest.json + task_brief.md；隐藏 B = mapped.v（v6/91/FF/min 具/含 and2LVSx1，不含 nand3LVSx1/nand3LVSx2/oai211LVSx1/invLVSx6）+ B manifest —— 来自同批 dc_addr_to_region_36rtl/v01_baseline（真实兄弟电路，同 PDK 同单元族，结构不同）。gold「真跑商业工具」= Innovus v23.32 启动验证在金标准创建期于 .75 完成；check.py 本地静态 + subprocess 跨输入守护（与本 bench L1-boundary 惯例一致）。
- check.py 14 条独立断言 (a)-(n)：(a)zip 含 run_audit.py (b)B 上跑出 AUDIT_REPORT.md (c)顶层=v6 且无 v7 (d)端口 N/row/col/valid (e)实例=91 且无 107 (f)含 B 专用 and2LVSx1 (g)不含 A 专属 nand3LVSx1/nand3LVSx2/oai211LVSx1/invLVSx6 (h)纯组合+CTS 不适用 (i)三分类 已具备/缺失/需注意 (j)阶段表 ≥8 (k)角=FF/1.1V/25C 且无 SS/0.98V/-40C (l)min 库已具备且无暂缺 (m)审计纪律 未进行正式实现 (n)LEF 硬缺口 tech.lef 缺失+genlef。其中 (c)(e)(f)(g)(k)(l) 为 6 条跨输入守护（反硬编码 A）。
- 自验：ref check() PASS（14/14）+ 5 negative 全 FAIL（NEG_RC=0：fake_empty→b / fake_print_expected→c/e/g/k/l / fake_core_deleted→j / naive_hardcode_a→c/e/g/k/l / naive_no_classify→h/i）+ §4.9 (a)空 zip FAIL / (b)fake_print_expected FAIL / (c)fake_core_deleted FAIL。test==disk check.py roundtrip OK。
- 断言闸门：k_rationale=14 == k_check=14 ≥8 ✓。追加 EDA-Eval-DesignFlow_A.jsonl（A jsonl 现 11 条）。mark case 1792489769571_ch2cw（johnl/hfeg0plg49/pnr_signoff/mc=255）。merge_shards → 主 jsonl 59 cases。日报 report_benchmark_11_02.html 59 cases，本条 k(断言)/k(check)/一致 = 14/14/✓。
- A 档试点记账：本条 track=faithful，未 pi/cline 实跑（"未跑"），待 cline+hook 重跑验真实通过率。失败归因预设：①交付形态/位置错→(a)(b)；③能力不足（硬编码 A）→(c)(e)(f)(g)(k)(l)；④判分歧义（对事实严格匹配，不对措辞）。
- ⬜ 下轮：trace_ledger.py --shard A next 选新 trace 开第 12 条 case（或按运维令 §四.3 挑一条 L2 shard-A PASS case 用 cline+hook 重跑）。
