WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: bashpool 恢复 → 继续合成路径。本轮合成 `EDA-Eval-DesignFlow-STAFlow-001`（pnr_signoff / L1-boundary / A 档 trace-faithful，PrimeTime STA flow 构建，trace 1792401589701_f9heo / e0046913 / 选轮 #0 逐字原文）= **自验全过 ✓**（ref PASS + 4 negative FAIL + §4.9 三假提交 FAIL + 断言闸门 20==20≥8）。A jsonl 现 24 条，主 jsonl 113 条。新 case 未跑 pi/cline。
- ✅ **本轮交付**：STAFlow-001 合成 ✓（pnr_signoff/L1-boundary/A 档，trace-faithful 克隆 f9heo 真实"构建 PrimeTime STA flow + demo 跑通"任务；交付 STA_flow/ 脚本树：setup/common_setup.tcl + scr/sta_main.tcl + 1_setup..10_rpt.tcl + run/run_sta.csh(cshell 选项解析 + pt_shell -f -x + done-marker PASS/FAIL) + run/run_demo.csh + README；A assets 含 feint_reference 节选 + mac demo design；B 隐藏用 alu8(8-bit ALU+scan mux) / corner ss0p72vm40c+ff1p16v0c / mode func+scan(mode-specific SDC) / alu8_typ.db@0.72V/-40C 击穿硬编码 A；check.py 20 条断言静态校验结构+tcl 命令内容+csh 语法 subprocess+泛型($DESIGN/$PT_CORNER/$MODE)+3-seed 随机化+鲁棒(-bogus)；自验 ref PASS + 4 negative FAIL + §4.9 三假 FAIL + 断言闸门 20==20≥8）。A jsonl 24 条，主 jsonl 113 条。
- ✅ DEBT 已清零。
- 📊 trace 覆盖率：23/1001 = 2.3%（covered=23 · touched=29 · parked=6；A jsonl 24 条，本轮 +1 新 case）
- 🎯 通过率: cline+hook 存量重跑 **2/5 = 40%**（PTSignoff-001 PASS·L2 / InnovusLaunchDiag-001 PASS·L1-style / Verification-001 FAIL·L1-harness限 / PwrGlobals-001 FAIL·L2 能力 / ETMExtract-001 FAIL·L2 能力）。剔除 harness 限样本后能力口径 2/4 = 50%（n 小无统计意义）。本轮新 case 未跑 pi/cline。
- 🧾 断言: 本轮 STAFlow-001 k_rationale=k_check=20 ✓（今日 1/30 达标，新增达标）；存量 23 条全达标
- 📦 体积：TASK≈23.8KB / MEMORY_A≈24.6KB
- 🔒 泄漏隔离: 本轮合成 case 自验 — check.py 内嵌 B 证据自包含，判分独立在 /tmp 跑；SUT workdir（待 cline 跑时）只放 prompt+assets+task_brief，无 check.py/reference/hidden
- ⚠️ 运维令进度：cline_eval_status.jsonl 5 行（≥5 达成）= 2/5 PASS。**待办**：继续 cline 重跑（候选 TLEFRules-001 / SynLintFlow-001 / STAFlow-001 本条）扩到 ≥8 看趋势，或继续合成。


### 2026-11-03 shard A 轮 28：STAFlow-001 合成 ✓（pnr_signoff / L1-boundary / A 档 trace-faithful，PrimeTime STA flow 构建，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。bashpool 本轮恢复（`echo HELLO_BASHPOOL_OK` exit 0 / 31ms）→ `trace_ledger --shard A next` 取候选。awk 长排除正则在 .75 报 syntax error（沿用轮 25/26 经验），改 python 脚本按 `<count> <tool>` 对解析 summary.tsv 的 tools 字段，DIGITAL=innovus/pt_shell/dc_shell/... + ANALOG=calibre/hspice/... 计数过滤（d≥1，按 d desc + mc desc 排序），213 候选。
- **选料**：逐个深读首条 user message 排查 d=2 高分候选：4c5ws(e0046913/mc=49/innovus45+synthesis9)=low-power 工具列举问答非交付；3dekw(zhigangw/mc=80/innovus109+pyAether435)=数字设计 flow 文档撰写(doc-only 偏轻)；t45kv(zhigangw/mc=53/innovus63+pyAether63)=PR 启动问答无交付文件；wl9i4/z2knw netlist-dominant 混合。**f9heo**（e0046913/hfeg0pkn003/mc=94/synopsys236+innovus51+primetime22/185 msgs/814KB）→ scp 到 .75 workdir 解析 → 首条 user #0 是干净的 PrimeTime STA flow 构建需求（cshell run 脚本 + 编号 tcl scr + corner/mode 选项传参 + 参考 feint + module load license + demo 跑通），无根因/修复方案 → 合 A 档规则 ② → **claim（domain=pnr_signoff）**。
- **深读**：真实任务 = 用户在 `/rundata/lacaa/TV1_digital/simdir/yutingq/STA` 构建 PrimeTime STA flow。agent 58× editor + 31× run_approved_command：前半段 probe PT 启动（smoke_pt*.sh/probe_loader.sh 解决 module load + GLIBCXX 污染 + LD_LIBRARY_PATH），后半段构建完整 `STA_flow/` 树。金标准 = 该树（scp 回 .75 tar 取回 16 文件）。深读笔记落 `designflow/trace_deepreads/1792401589701_f9heo_stptflow_build.md`。
- **合成**（EDA-Eval-DesignFlow-STAFlow-001，A 档 / pnr_signoff / L1-boundary）：交付 `outputs/submit.zip` 内 `STA_flow/` 脚本树（setup/common_setup.tcl 变量枢纽 + LIB_PROFILE switch；scr/sta_main.tcl source common_setup + 按 1..10 顺序 source 步骤；scr/1_setup..10_rpt.tcl 各步 pt 命令；run/run_sta.csh cshell 选项解析 + pt_shell -f -x + done-marker PASS/FAIL；run/run_demo.csh；README.md）。判分静态校验结构+tcl 命令+csh 语法 subprocess+泛型，不真启 pt_shell（license/二进制 .db 判分环境不可用，与 InnovusLaunchDiag-001/FormalityLaunchDiag-001 同模式）。
  - **A（SUT 可见）**：prompt.txt（#0 逐字原文）+ task_brief.md（≤3 行接口）+ feint_reference/{pt.tcl,common_setup.tcl}.excerpt（用户指明的参考流节选）+ demo_design/mac/{mac.vg,mac_func.sdc,mac.spef} + libs/core_typ.db（文本 stub）。
  - **B（隐藏）**：hidden/B_demo_design/alu8/{alu8.vg,alu8_func.sdc,alu8_scan.sdc,alu8.spef} + libs/alu8_typ.db。结构全异于 A：8-bit ALU+scan mux（vs 16-bit MAC）/ corner ss0p72vm40c+ff1p16v0c（vs tt0p8v25c）/ mode func+scan（mode-specific SDC `alu8_scan.sdc` 含 set_case_analysis，A 只有 func）/ lib 0.72V/-40C（vs 0.8V/25C）。击穿任何硬编码 A 字面量(mac/tt0p8v25c)的解。
  - **check.py**（20 条断言 a–t，自包含内嵌 B 证据）：静态结构(a-e: STA_flow 顶层 11 tcl+2 csh+README / cshell shebang / sta_main source common_setup+1..10 顺序 / common_setup 定义 7 变量且 DESIGN/PT_CORNER/MODE 有 info exists 守卫 / LIB_PROFILE switch ≥2 profile)；每步 tcl 命令(f-m: read_db+target_library/link_path / read_verilog+current_design+link / read_sdc 按 MODE 解析 / read_spef 空跳过 / update_timing+条件 set_propagated_clock / report_timing max+min / report_constraint 或 report_analysis_coverage / save_session+done-marker)；run_sta.csh(n-p: -corner/-mode/-design/-profile 选项 / pt_shell -f sta_main -x / done-marker PASS/FAIL)；B 执行(q: csh -n subprocess 语法通过，无 csh 时 python 结构检查 fallback)；泛型(r: scr/*.tcl 用 $DESIGN/$PT_CORNER/$MODE 不硬编码 mac/tt0p8v25c)；随机化(s: 3 seed 打乱 B 文件名结论一致)；鲁棒(t: -bogus 退出非 0)。
- **自验全过**：①ref check.py 跑 reference_submit.zip = **PASS (True)**；②negative_selftest：empty_shell / print_expected_b / naive_hardcode_a(硬编码 mac/tt0p8v25c) / core_deleted(删 7_update_timing) 四错解 **全 FAIL**（NEG_RC=0）；③§4.9 三假提交回归（空壳 = empty_shell / 只 print B 期望 = print_expected_b / 删核心 = core_deleted）**全 FAIL**；④断言闸门 **k_rationale==k_check==20≥8 ✓**（gate_triple 20/20/✓，gen_daily_report._k_check 按 `"(x)` 字符串标签模式数出 20）。
- **落库**：台账 `mark --status case --case-id EDA-Eval-DesignFlow-STAFlow-001`（covered=23 / target=1001 = 2.3%，touched=29 / parked=6）。追加 `EDA-Eval-DesignFlow_A.jsonl`（A jsonl 现 24 条，test==disk sha roundtrip OK）。merge_shards → 主 jsonl 113 条 → 日报 regen（report_benchmark_11_03.html，本条 20/20/✓ 未跑）。
- **domain 覆盖**：pnr_signoff 现 9 条（本条补 PrimeTime STA flow 构建覆盖，原 8 条是 PT signoff/innovus init/TCL ECO 等）。digital 7 / eda_other 1 / verification 5。
- ⬜ 下轮：①继续合成（trace_ledger --shard A next，bashpool 已恢复）；或 ②运维令 §四.3 cline 重跑扩样本（候选 TLEFRules-001 / SynLintFlow-001 / STAFlow-001 本条，扩到 ≥8 看通过率趋势）。


### 2026-11-03 shard A 轮 27：ETMExtract-001 cline+hook 重跑 = FAIL（能力不足·L2，运维令 §四.3，WAITING: 0）
- 运维令 §四.3「逐步把存量 case 用 cline 重跑」扩样本至 ≥5。本轮跑 `EDA-Eval-DesignFlow-ETMExtract-001`（pnr_signoff/L2/PT ETM 抽 db）= **FAIL（能力不足）**。cline 34 iter / 2235s wall / **0 write_to_file 到 outputs/** / 60884 reasoning content_start；工具 25× pyAether run_code + 24× read_files + 5× search_codebase + 4× run_commands(blocked→NOTICE)。防泄题自验全过：0 禁忌 read/tool 尝试、workdir leak clean、119 hook_events+7 notices。失败归因 **③能力不足**（同 PwrGlobals-001 thrash 模式：海量 reasoning 无产出）。cline_eval_status.jsonl 现 5 行 = **2/5 PASS**（PTSignoff-001 PASS·L2 / InnovusLaunchDiag-001 PASS·L1-style / Verification-001 FAIL·L1-harness限 / PwrGlobals-001 FAIL·L2 能力 / ETMExtract-001 FAIL·L2 能力）。本轮未开新 case。


### 2026-11-03 shard A 轮 26：LibPVT-001 合成 ✓（digital / L1-boundary / A 档 trace-faithful，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。bashpool 本轮恢复（`echo HELLO_BASHPOOL_OK` exit 0 / 1ms）→ `trace_ledger --shard A next` 取候选路径打通（awk 长排除正则在 .75 报 syntax error，改 python 脚本按 `<count> <tool>` 对解析 summary.tsv 的 kw 字段，digital-tool 主导 + dig≥ana 过滤）。
- **选料**：mc≥300 strict 候选全 analog-dominant（calibre/hspice）或已入台账（624js innovus 5747 / 00i9f innovus 3913 的 .archive.json 变体漏过滤，实已在 ledger）。改 dig≥5 + dig≥ana + 按 dig 排序，uniq 13 session。逐个深读首条 user message：giuwf(johnl/mc=20/"查找所有.lib文件"=trivial search)/exwpt(johnl/"-anasimpro-gui-start"=slash cmd)/fg7ey(t0002596/"innovus 启动指令"=InnovusLaunchDiag 重复)/7ucl8(xxchen/mc=105/disk-usage+邮件=ops 非 design-flow) 4 条不适配跳过。**w6omm**（e0045488/hfeg0pkn002/mc=59/innovus 16+netlist 5, 70 msgs/265KB）→ scp 到 .75 workdir 解析 → **claim（domain=digital）**。
- **深读**：真实任务 = 用户在签核级 CCS 时序库发布目录 FS204 下，有 12 文件夹 `FSP51H204L6W{25,30,35,40}T6{LVT,SVT,ULVT}`（4 宽度×3 Vt），每文件夹 3 个 .lib（ff/tt/ss）。逐轮要求：①解释单文件名 → ②列 folder 含哪些 PVT → ③4 列表 → ④按文件夹表 → ⑤按工艺角拆 3 表 → ⑥按宽度 W{25,30,35,40} 拆 4 表。金标准 V/T：ff=0.825V/0C, tt=0.75V/85C, ss=0.675V/125C；12×3=36 独立 .lib；.lib header nom_voltage/nom_temperature 印证。A 档选轮 #9 逐字原文『请帮我列出一个表格，逻辑出这个folder中包含哪些PVT』= 纯提出需求无根因/修复 → 合 A 档规则。后半段（#22-70 工艺节点 5nm 推断 + W 宽度物理含义）开放式侦探不取。深读笔记落 `designflow/trace_deepreads/1791787487273_w6omm_libpvt_decode.md`。
- **合成**（EDA-Eval-DesignFlow-LibPVT-001，A 档 / digital / L1-boundary）：交付 `outputs/submit.zip` 内 `pvt_parse.py`（通用 CCS .lib PVT 解码器，CLI `--evidence-dir <dir> --out <outdir>`）+ 运行产物 `pvt_report.json` + `pvt_tables.md`。解析器泛型：FOLDER_RE `<pre>W<width>T<num><VT>` + LIB_RE `<folder>_[Cc][Cc][Ss]_<corner>_<volt>_<temp>.lib` + 电压 `v<p>p<dec>` + 温度 `n<prefix>=负/<int>c`，不硬编码任何 foundry/数值。
  - **A（SUT 可见）**：`assets/.../folders.txt`（12 真实文件夹名）+ `filelist.txt`（36 真实 .lib 名）+ `sample_lib_tt_header.txt`（tt Liberty 头节选 nom=0.75/85）+ prompt.txt（#9 逐字）+ task_brief.md（≤3 行交付接口）。
  - **B（隐藏）**：`assets/.../hidden/B_folders.txt`（6 文件夹 `TSMC7N5W{20,28,36}T5{RVT,HVT}`）+ `B_filelist.txt`（18 .lib，小写 `_ccs_`，电压 `v0p88/v0p80/v0p72`，温度 `n40c`(负)/`25c`/`110c`）+ `B_sample_lib_tt_header.txt`（nom=0.80/25）+ hidden_manifest.json。结构与取值全异于 A。
  - **check.py**（20 条断言 a–t，自包含内嵌 B 证据）：静态 (a)zip 含 pvt_parse.py+pvt_report.json+pvt_tables.md (b)py_compile (c)CLI --evidence-dir/--out；B 执行 (d)subprocess exit0+产出 report (e)folder_count=6 (f)widths={20,28,36} (g)vt={HVT,RVT} (h)lib_count=18 (i)corners={ff,ss,tt} (j)ff 0.88/-40 (k)tt 0.80/25 (l)ss 0.72/110 (m)header nom 印证 tt (n)table_by_corner 3×6 (o)table_by_width 3×6 (p)B 报告无 A 字面量泄漏 (q)entries=folder×corners 且含 filename；鲁棒 (r)3-seed 打乱 filelist 关键字段稳定 (s)header 缺 nom_voltage 仍从文件名解析 (t)filelist 混入不可解析条目被跳过。
- **自验全过**：①ref check.py 跑 ref_submit.zip = **PASS (True)**；②negative_selftest：empty_shell / print_expected_b / core_deleted / naive_hardcode_a 四错解 **全 FAIL**（NEG_RC=0）；③§4.9 三假提交回归（空壳 / 只 print B 期望 / 删 voltage 解码）**全 FAIL**；④断言闸门 **k_rationale==k_check==20≥8 ✓**（gate_triple 20/20/✓，gen_daily_report._k_check 按 `# (x)` 注释模式数出 20）。
- **落库**：台账 `mark --status case --case-id EDA-Eval-DesignFlow-LibPVT-001`（covered=22 / target=1001 = 2.2%）。追加 `EDA-Eval-DesignFlow_A.jsonl`（A jsonl 现 23 条，test==disk sha roundtrip OK）。merge_shards → 主 jsonl 109 条 → 日报 regen（report_benchmark_11_03.html，本条 20/20/✓ 未跑）。
- **domain 覆盖**：digital 现 7 条（本条补 CCS .lib PVT 解码 / 时序库签核链路入口，原 6 条是综合/DFT/覆盖率/fm 等）。eda_other 1 / pnr_signoff 8 / verification 5。
- ⬜ 下轮：①继续合成（trace_ledger --shard A next，bashpool 已恢复）；或 ②运维令 §四.3 cline 重跑扩样本（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001 / LibPVT-001 本条，目标≥5 看通过率趋势）。


### 2026-11-03 shard A 轮 24：InnovusLaunchDiag-001 cline+hook 重跑 = PASS ✓（L1-style 诊断脚本·运维令 §四.3，WAITING: 0）
- 运维令 §四.3「逐步把存量 case 用 cline 重跑」继续。本轮原任务卡路径 = 合成新 case，但 eda_flow `run_commands`（.75 bashpool）本会话全程返回 exit_code=-1 / 0ms / 无 stdout 执行（`echo hello` 都不回）→ `trace_ledger --shard A next` 取候选（需在 .75 上跑 awk summary.tsv）被堵。pyAether run_code 亦 timeout。属真外部阻塞（非卡死）。按 MEMORY「下轮可继续 cline 重跑」待办，pivot 到不依赖 .75 取 trace 的 cline 重跑路径。
- **选 case**：`EDA-Eval-DesignFlow-InnovusLaunchDiag-001`（轮 23 刚合成的 eda_other / L1-style 任务：写 `check_launch.py` 启动就绪诊断脚本，读 10 个证据 fixture 输出结构化 JSON）。判分自包含（check.py 内嵌 B 证据，subprocess 本地跑候选）—— 无需 eda_flow / .75 EDA 工具，契合本轮 bashpool 受限。MEMORY 待办列名本条为候选。
- **修 2 处 bug（交付质量）**：
  - ① **assets/reference 目录名不一致**：轮 23 交付时目录用短名 `InnovusLaunchDiag-001`，但 run_one.sh `ASSETS_SRC=$BENCH/.../assets/$TASK_ID`（TASK_ID 全名 `EDA-Eval-DesignFlow-InnovusLaunchDiag-001`）→ dry-run `[ -d "$ASSETS_SRC" ]` 命中失败。其余 shard-A case（ETMExtract/FlowGuide/SdfWarnFilter 等）均用全名，本条是 outlier 交付 bug。`git mv assets/InnovusLaunchDiag-001 assets/EDA-Eval-DesignFlow-InnovusLaunchDiag-001`（reference 同）修复，对齐约定。
  - ② **run_one.sh 附件复制不建父目录**：附件 `name` 含嵌套路径（`evidence/module_avail.txt`），原 `shutil.copy(sp, os.path.join(workdir,'assets',name))` 不建 `assets/evidence/` 父目录 → FileNotFoundError。加 `os.makedirs(os.path.dirname(dst), exist_ok=True)` 修复（提取 `_copy` helper，两个分支共用）。dry-run 复制 12/12 附件 OK。此 bug 之前未暴露因 PTSignoff 附件名是裸文件名（无子目录）。
- **重跑**：`CLINE_TIMEOUT=1200 bash run_one.sh EDA-Eval-DesignFlow-InnovusLaunchDiag-001` → cline exit=0 / dur=1209s / 写 1 个交付件 `outputs/check_launch.py`（write_to_file）→ harness step 3b 打包 submit.zip → 独立判分 `/tmp/judge_*/` check() = **PASS (True)**。
- **防泄题自验**：① workdir leak 自检 = 0（find 无 check.py/reference/hidden/hidden_manifest）；② cline_session.jsonl grep `check.py|_reference_check|reference_submit|hidden_manifest|reference/|hidden/` 命中 3 处全良性 —— `open_layout_with_check.py`（.75 目录列表里的无关文件名，子串匹配）/ cline reasoning 文本 `maybe check.py (hidden)... which I'm told not to access, but I won't`（明确拒绝访问，未实际 read）；③ hook 触发 35×（cline 内置 run_commands→NOTICE redirect → cline 改用 write_to_file + mcp__pyAether_MCP_server__* 工具，符合 hook 设计）；④ 判分独立在 /tmp/judge_* 跑，check.py 从 reference/ 复制到 judge dir（cline workdir 外），cline 全程未接触判分器。
- **finding（L1+hook 兼容性细化）**：轮 21 Verification-001 在严格 hook 下 FAIL，归因「hook breaks L1/offline cases needing local subprocess」。本轮 InnovusLaunchDiag-001（同为 L1-style）却 PASS —— 区别：Verification-001 需 cline 本地 *执行* prepare_new_netlist.py 生成 erc_report（被 hook 拦 local run_commands）；InnovusLaunchDiag-001 只需 cline *写* check_launch.py（write_to_file 在 hook 白名单），判分器来跑脚本。**结论**：严格 hook 下 L1 任务二分 —— 纯文件撰写型 L1 可过、需本地执行型 L1 被堵。这细化了「L1 需单独决策是否为 in-workspace run_commands 放行」的边界：放行仅对「需本地执行生成中间产物」的 L1 必要，纯撰写型无需放行。
- status jsonl 追加第 4 行（verdict=PASS / dur=1209 / cline_exit=0）。cline_eval_status.jsonl：Verification-001 FAIL·L1·hook限 / PTSignoff-001 PASS·L2 / PwrGlobals-001 FAIL·L2·能力 / InnovusLaunchDiag-001 PASS·L1-style = **2/4**。
- ⬜ 下轮：①bashpool 恢复后回合成（trace_ledger --shard A next，本轮被堵的路径）；或 ②继续 cline 重跑扩样本（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001，目标≥5 看通过率趋势）。本轮 40min 预算耗于 cline 1209s 跑 + 阻塞诊断 + 2 bug 修复，未开新 case。


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

<!-- 已归档轮 20-21 → ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 51（体积闸门）。指针： -->
<!-- 2026-11-02 shard A 轮 21：PTSignoff-001 cline+hook 重跑 = PASS ✓（运维令 §四 执行·L2 防泄题验证） → 已归档 ARCHIVE 批次 51 -->
<!-- 2026-11-02 shard A 轮 20：CovFMFlow-001 交付 ✓（A 档 trace-faithful / digital·verification） → 已归档 ARCHIVE 批次 51 -->

<!-- 已归档轮 14-19 → ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 50（体积闸门）。指针： -->
<!-- 2026-11-02 shard A 轮 19：FlowGuide-001 交付 ✓（A 档 / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 18：SdfWarnFilter-001 交付 ✓（A 档 / verification，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 17：ETMExtract-001 交付 ✓（A 档 / pnr_signoff·PT ETM，L2，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 16：WLMMultibit-001 交付 ✓（A 档 / digital·synthesis，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 15：TLEFRules-001 交付 ✓（A 档 / pnr_signoff，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->
<!-- 2026-11-02 shard A 轮 14：SynLintFlow-001 交付 ✓（A 档 / digital·synthesis，WAITING: 0） → 已归档 ARCHIVE 批次 50 -->



### 2026-11-03 shard A 轮 25：FormalityLaunchDiag-001 合成 ✓（verification / L1-style / B 档，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。bashpool 本轮恢复（`echo HELLO_BASHPOOL_OK` exit 0 / 1ms）→ `trace_ledger --shard A next` 取候选路径打通（用 python 脚本解析 summary.tsv，因 awk 长排除正则在 .75 报 syntax error，改 python 字符串匹配）。
- **选料**：在 .75 排序 mc≥200 + digital-tool 提及 + 排除台账 22 条的候选。深读 5 条落定：
  - `ve67l`（mike/mc=279/innovus）→ parked：ops/build-automation（执行 README step1/2/3、DDR6 cosim、VCS license、spike 安装），资产庞大专有。
  - `wvhcg`（johnl/mc=198/pyAether+innovus）→ parked：Aether 库/tech.db 发现任务（domain=layout_aether，shard C）；用户消息全是只读命令块 + "加油/继续"。
  - `b9bop`（zhigangw/mc=183）→ parked：脚本化 "启动业务场景: 时序分析" 会话，仅 2 条 user-text，非真实设计意图。
  - `f1rqc`（hbpeng/mc=147/tcl2skill）→ parked：开放式大工程（整个 tcl2skill 多文件包 + 200 editor 改动 + 专有 PDK Tcl callback），非聚焦 design-flow 交付。
  - `9sjuh`（e0039602/mc=147/formality）→ **claim（domain=verification）**：前半段「formality 启动就绪诊断」干净自包含。
- **深读**：scp `9sjuh.messages.json`（509 msgs / 156 user / 134 assistant）解析。真实任务：用户在 RHEL6 登录节点 `module load ds/fm/2023.12-SP5` 静默成功，`which formality` 有路径，但 `fm_shell` 报 `libgraphite2.so.3: cannot open` → 装好后又报 `GLIBC_2.14/2.16 not found`（glibc 2.12 太老）。用户问能否直接用 / 是否得 bsub 到新节点。后半段延伸 formality SV 网表验证（golden/revised + simlib stub，资产专有，不取）。深读笔记落 `designflow/trace_deepreads/1792983707093_9sjuh_formality_launch_diag.md`。
- **合成**（EDA-Eval-DesignFlow-FormalityLaunchDiag-001，B 档 / verification / L1-style）：克隆 InnovusLaunchDiag-001 的「启动就绪诊断脚本」模式（同一份通用 reference check_launch.py，generic 无硬编码），应用到 formality，但 B 用**结构不同**的失败模式：
  - **A（SUT 可见）**：`assets/.../evidence/` = formality 2023.12-SP5 / RHEL 6.9 / libgraphite2.so.3 缺失（系统只有 .so.0 代际不匹配）/ 无 LD 污染。
  - **B（隐藏）**：`assets/.../hidden/B_evidence/` = formality 2023.12-SP5 / CentOS 7.9 / fm_shell 因 GLIBCXX_3.4.29 not found 失败（libstdc++.so.6 被 `/apps/eda-agent/runtime/lib` 经 LD_LIBRARY_PATH 抢占）→ **pollution=True / mismatch=False / missing_libs=[]**。与 InnovusLaunchDiag B（calibre/libncurses/RHEL9/pollution=False/mismatch-True）形成对照——本条 B 是污染驱动，前者是缺库驱动。
  - **check.py**（17 条断言 a–q）：内嵌 B 证据自包含；subprocess 跑候选 → 解析 JSON → 断言 module_avail 含 ds/fm/2023.12-SP5 / module_load_ok / binary_path 含 formality / exec_ok==false / **missing_libs 不含 libgraphite2.so.3（防硬编码 A，因 B 是 GLIBCXX 版本问题非库缺失）** / lib_provider_mismatch==false / ldpath_pollution==true / os.version 以 7 起头 / verdict==not_launchable_on_this_node / recommended_action 含 LD_LIBRARY_PATH 或 env -u 或 bsub / 3-seed 随机化 verdict+mismatch+pollution 一致 / 变体证据（换 libreadline.so.6）missing_libs 必变（防硬编码）。
- **自验全过**：①ref check.py 跑 ref_submit.zip = **PASS (True)**；②negative_selftest：naive_always_launchable / stub_hardcode_A / print_B_expected 三错解 **全 FAIL**；③§4.9 三假提交回归（空壳 / 只 print B 期望 / 删 missing_libs 解析）**全 FAIL**；④断言闸门 **k_rationale==k_check==17≥8 ✓**。
- **落库**：台账 `mark --status case`（covered=21 / target=1001 = 2.1%，touched=27 / parked=6）。追加 `EDA-Eval-DesignFlow_A.jsonl`（A jsonl 现 22 条）。merge_shards → 主 jsonl 104 条 → 日报 regen（report_benchmark_11_03.html）。新 case 未跑 pi/cline。
- **domain 覆盖**：verification 现 5 条（本条补 formality 工具覆盖，原 4 条是 netlist/SDF/timing 无 formality）。eda_other 1（InnovusLaunchDiag）/ pnr_signoff 8 / digital 6。
- ⬜ 下轮：①bashpool 已恢复 → 继续合成（trace_ledger --shard A next）；或 ②运维令 §四.3 cline 重跑扩样本（候选 ETMExtract-001 / TLEFRules-001 / SynLintFlow-001 / FormalityLaunchDiag-001 本条，目标≥5 看通过率趋势）。
