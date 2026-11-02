WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: A-faithful 接口根因修复 = **完成（待 cline 重跑验证）**。运维令 21:3x §③判据：cline+hook 存量重跑 8 条中 ①+④ 类失败 3/8=37.5% **破 30% 阈值** → 需"先修接口与判分"。**根因**：`run_one.sh` 建 workdir 时用硬编码通用模板覆盖 `task_brief.md`，丢弃 `assets/<task_id>/task_bief.md` 的 case 专属交付件清单 → cline 看不到文件结构契约 → ①交付形态/④判分歧义 失败。**修复**：① run_one.sh 改为优先 `shutil.copy(assets/task_brief.md → workdir/)`，无则回退通用模板；② SynLintFlow-001 brief 重写为完整 9 文件 syn/ + 5 文件 lint/ 树（删悬空 ref_syn_prj 引用）；③ STAFlow-001 brief 增列 sta_main+10 编号步骤+2 csh+setup/common_setup 文件树；④ TLEFRules-001 brief 已充分不改。3 case workdir-build 隔离模拟全过（case-specific brief 送达 / leak CLEAN）。详见 EXPERIMENTS EXP-51。
- ✅ **本轮交付**：A-faithful 接口修复（run_one.sh bug fix + 3 case brief 补全），直接对应运维令"先修接口"最高优先。**未新增 case、未跑 cline**（40min 预算不足跑 3×1500s 重跑）。A.jsonl 仍 27 条 / 台账 covered=26。
- 📊 trace 覆盖率：26/1001 = 2.6%（covered=26 · touched=33 · parked=7；A jsonl 27 条，未变）
- 🎯 通过率: cline+hook 存量重跑 2/8 = 25.0%（未本轮新增 cline 跑；①+④=3/8=37.5% 破阈已修接口，待重跑验证降阈）
- 🧾 断言: 本轮无新 case（接口修复轮）；存量 27 条全达标
- 📦 体积：TASK≈23.8KB / MEMORY_A≈12.9KB（轮 28–31 已归档 → MEMORY_A_archive.md 归档批次 1）
- 🔒 泄漏隔离: 本轮仅改 run_one.sh + assets/task_brief.md（附件），不涉 check.py/reference/hidden；brief 只列文件位置不写内容（运维令 21:3x §①3 允许），内容断言留 check.py 测能力 → 难度未稀释
- ⚠️ 运维令进度：A-faithful 接口修复完成（待验证）。**待办**：①cline 重跑 STAFlow/TLEFRules/SynLintFlow 验 ①+④ 降阈（优先，下轮第一件事）；②继续合成（A 档试点 2/10，候选池薄）；③A-faithful ①+④ 占比破阈已修接口，重跑后重算。


### 2026-11-03 shard A 轮 32：SynLintFlow-001 cline+hook 重跑 = FAIL·①+④ A-faithful（运维令 §四.3，①+④ 破 30% 阈值，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。trace_ledger --shard A next 取候选：awk 长排除正则仍报 syntax error，改 python 脚本按 `<count> <tool>` 对解析 summary.tsv tools 字段 + keywords `kw:count` 对。digital 候选池薄：topdig≥10 仅 5 条（z2knw/4xt0p/b7y8t/awgyg/748ox 全 analog-heavy 或 pyAether schematic 主导）；按 dc_shell/pt_shell/formality/vcs/verdi/genus keyword score 排序得 21 条，逐个 SSH 读首 user msg 排查。
- **选料排查**：poxvz（johnl/dc_shell:154）= run_dc.sh 调试任务（"你看下我这个运行失败什么原因"）→ A 档规则 ② 命中（用户指出根因=运行失败）→ B 档候选但金标准=debug 后的 synth.tcl 修复，模糊。m1cve（johnl/mc=61/synthesis+dc_shell）= VCS+DC 链 A-档合规（#0 "请编写一个verilog 脚本 并用本地的vcs验证 然后yongdc综合"）但深读发现用户在 VCS+DC 交付前 pivot 到 token-plan 测试（#16 "全部失败"后转去测 token API），**金标准模糊**（用户未接受 VCS+DC 结果）→ 不宜作 A 档。k5jti（e0046913/primetime:36）= PT 版本选择 Q&A → 非 delivery。gavk7（xxchen/primetime:21）= nxtgrd 文件对比分析 → 非 design_flow。
- **pivot 到 cline 重跑**（运维令 §四.3「逐步把存量 case 用 cline 重跑」，轮 30 待办：「若 SynLintFlow-001 也 ①+④ → 占比破 30% → 需修接口」）：选 `EDA-Eval-DesignFlow-SynLintFlow-001`（A 档 trace-faithful / digital / 26 断言，SpyGlass lint + DC 综合 flow 构建）。ref check.py 独立 dry-run：发现 hidden/ 未复制到 judge dir → v-z 断言 21/26 FAIL；修复后 26/26 PASS。
- **bug fix（run_one.sh）**：judge 步骤漏复制 hidden/ 进 $JUDGE/ → 加 `cp -r $ASSETS_SRC/hidden $JUDGE/hidden`（fallback `$REF_DIR/hidden`）。影响所有 hidden-依赖 case 的判分正确性。修复后 ref 26/26 PASS 验证通过。
- **重跑**：`CLINE_TIMEOUT=1400 bash run_one.sh EDA-Eval-DesignFlow-SynLintFlow-001 deepseek-v4-pro-cloud medium` → hook 部署 + workdir 建（2 附件: rtl_synth/cfreq_ctrl.v + workspace_listing.txt，leak 自检 clean）→ cline 跑 1640s / exit 0 / 31 iter / 2 auto-compaction → 4 文件（lint/spyglass_lint.prj 1.6KB + spyglass_constraints.sgdc 0.8KB + syn/dc_synth.tcl 3.6KB + syn/.synopsys_dc.setup 1.1KB）→ harness 打包 submit.zip → 独立判分 `/tmp/judge_*/` check() = **FAIL 0/26**（assertion a: 0/9 key syn files）。
- **失败归因 ①+④（A-faithful judge-spec-mismatch）**：cline **有产出**——4 文件结构合理（SpyGlass lint project + SGDC constraints + DC synth tcl + .synopsys_dc.setup），**字面满足** prompt "做个lint的项目文件，以及综合的流程"。**但** check.py 要求特定 9 文件 DC flow（syn_filelist + Makefile with USE_LSF/bsub/dcnxt_shell + DC_XARGS -x 变量透传 + dc_setup.tcl HL22/Au22 ulvt+lvt ssg ccs + link_library dw_foundation + set_svf before elaborate + compile_ultra -gate_clock + report qor/timing/area/power/clock_gating + ${cur_date} 标签）。cline reasoning 明确写道 "reference solution checked by check.py which I must not access" → 它**知道**看不到判分标准，按 prompt 字面产通用 DC flow。**这正是 A-faithful 试点要测的**：合成 README 把 9 文件结构写明 → cline 按要求产 → PASS；faithful prompt 只给用户原话 → cline 产 4 通用文件 → 形态不匹配 → FAIL。
- **防泄题自验全过**：① workdir leak 自检 = 0；② 35 forbidden-mention 全 benign reasoning（"check.py I must not access" / "reference/ I was told NOT to access"，0 实际 read）；③ hook 36 tool_call events（built-in run_commands 2× → NOTICE → cline 改用 24× pyAether MCP run_code + 12× editor + 26× read_files + 6× search_codebase）；④ 判分独立 /tmp/judge_*/，check.py + hidden/ 从 reference/assets 复制（cline workdir 外），cline 全程未接触判分器。
- **finding（A-faithful ①+④ 破阈）**：本轮是第 8 条 cline+hook 重跑。①+④ 类失败（STAFlow① + TLEFRules①+④ + SynLintFlow①+④）= **3/8 = 37.5% > 30% 阈值**，**轮 30 预测命中**。运维令 21:3x §③判据：「①+④ 占比 ≤30% 才不修接口」→ 现破阈 → **需修接口**。三类 ①+④ 根因：STAFlow = 多文件树顶层 wrapper 缺失（prompt 隐含目录契约）；TLEFRules = 解析器脚本缺失（prompt 字面只要求报告）；SynLintFlow = 9 文件 DC flow 结构缺失（prompt 字面只要求"综合的流程"）。**改进方向**：① task_brief.md 加 1 行交付件格式/结构要求（但稀释 A-faithful 难度，需权衡）；或 ② check.py 放宽接受通用 DC flow（但降难度）；或 ③ A 档任务说明仍逐字原文但 task_brief 列出交付件清单（接口契约 ≠ 改意图，运维令 21:3x §①3 允许"task_brief 只写交付接口与文件位置"）。暂记 EXPERIMENTS，下轮逐条评估修哪端。
- status jsonl 追加第 8 行（verdict=FAIL / dur=1640 / cline_exit=0 / failure_class=①+④ A-faithful judge-spec-mismatch）。cline_eval_status.jsonl 8 行 = **2/8 PASS = 25.0%**（目标 20–30% ✓ 在带）；①+④=3/8=37.5%（破 30% 阈值）。
- ⬜ 下轮：①修 A-faithful 接口（STAFlow/TLEFRules/SynLintFlow 三条 ①+④ 逐条评估，优先方案 ③ task_brief 列交付件清单）；或 ②继续合成（A 档试点 1/10，候选池薄需扩大搜索）；或 ③FormalityLaunchDiag-001 cline 重跑（B 档对照 A/B）。

### 2026-11-03 shard A 轮 33：SPFCoupling-001 合成 ✓（eda_other / L1 / A 档 trace-faithful，SPF coupling→CSV 解析，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。eda_flow open_session → run_commands 在 .75 解析 summary.tsv。
- **选料**：长 awk 排除正则在 .75 报 syntax error（已知坑），改 python 脚本按 `kw:count` 解析 keywords 字段 DIG 信号（verdi/vcs/dc_shell/primetime/formality/spyglass/innovus/.def/.sdc/...）+ ANA 反向过滤（hspice/spectre/virtuoso/waveview/...），strong≥5 且 ana≤strong，mc≥30，排除台账 32 条，得 11 候选。逐个 scp+解析首 user msg：
  - poxvz(johnl/mc=73,dc_shell)=DC run_dc.sh 调试（依赖失败状态，②前提缺失风险）→ 备选；
  - m1cve(johnl/mc=61,synthesis+dc_shell,416msgs)=VCS+DC 但用户中途 pivot 到 tokenplan API 测试 + agent 框架开发，多任务混杂非聚焦 → skip；
  - k5jti(e0046913/mc=45,primetime)=PT 版本选择 Q&A（非交付）→ skip；
  - gavk7(xxchen/mc=97)=nxtgrd 文件对比报告（physical，非 digital）→ skip；
  - 8u3iw(thomasz/mc=61)=ESD dir 数据量对比报告（非 design_flow 交付）→ skip；
  - 1f34q(johnl/mc=35)=复制旧会话非任务 → skip；
  - **5pv45**（ray1lei/hfeg0pkn004/10.129.2.13/mc=32，.def:69）→ scp 926KB messages.json（144 msgs / 84 user）→ 首条 user #0 = "转化为排版规律的csv文件或excel文件...SPF工具抽出来的signal之间的coupling数据...每个空白行后的第一行都是这个信号的总coupling" + #5 格式示例（DSPF 1.3 *|NET 块 + 耦合行）+ #15 详细 23 列规范。
- **A/B 档判定**：#0+#15 = 纯目标表达（解析 SPF → SABL CSV），用户未指出根因/未给修复 → **A 档规则 ② 合规 → A 档 trace-faithful**（prompt = #0+#5+#15 逐字原文）。
- **深读**：真实任务 = 用户在 /ai_sandbox/drgqx/V0/agentdir/ray1lei 解析 StarRC DSPF 1.3 SPF 文件 msaq_E.spf_CC（37MB/41万行/20818 NET），提取 SABL（sense-amplifier bit-line）信号 XI_msax*_cp*.XI_CXSA_*.Sa_BLa/b<bit> 的耦合汇总。agent 经多轮调试（regex 反斜杠双转义 → 改纯字符串操作；pracL 无 <idx> 实例名边界 → 加无序号分支），最终 sabl_summary.py（384 行纯字符串操作）产出 4496 行 CSV。金标准 = sabl_summary.py + CSV（23 列：idx/CP/SA_sort/Sa_BLa + a 侧 8 类耦合 + Sa_BLb + b 侧 8 类耦合 + 空列 + ab_samegroup）。
- **合成**（EDA-Eval-DesignFlow-SPFCoupling-001，A 档 / eda_other / L1，离线 Python 静态判分不启 EDA 工具）：
  - **A（SUT 可见）**：prompt.txt（#0+#5+#15 逐字原文）+ task_brief.md（≤3 行接口：sabl_summary.py CLI + 23 列 CSV）+ msaq_E_sample.spf_CC（合成 DSPF 1.3，10 CPs × 2 cells × 2 bits = 40 行，含 Sa_BLa/b + PreEq0 + cn09bla/blb + Cslin + IoN + Yio + pracL 无 <idx> 边界 + 2 decoy 非 Sa_BL net）。
  - **reference**：ref_solution/sabl_summary.py（金标纯字符串操作解析器）+ run_sabl.sh + sabl_coupling_summary_A.csv + reference_submit.zip。
  - **B（隐藏）**：hidden/B_msaq_E.spf_CC（10 CPs 但用 XI_msax512_*/XI_msax514_*/pracR，val_scale=2.7 使值全异于 A，40 行）+ hidden_manifest.json + 镜像 reference/hidden/。B 不进 SUT 沙箱：B 内嵌 gzip+b64（9.4KB）于 check.py + 镜像 reference/hidden/，判分在 /tmp/judge_* 独立跑。
  - **check.py 16 条断言 a–p**：(a)zip 含 sabl_summary.py (b)py_compile (c)B 上 exit 0 产 CSV (d)23 列表头 (e)行数==期望 (f)CP 含 B 不含 A（跨输入护栏）(g)CP 排序 cp00-06<pracR<cp08+ (h)SA_sort <idx>/裸形式 (i)Sa_BLa/Sa_BLb 同前缀+bit (j)a_bl 累加 (k)a_Cslin 累加 (l)a_PreEq (m)a_power (n)a_total (o)ab_samegroup 非零 (p)鲁棒性缺文件 exit 非零。内嵌紧凑 reference parser 计算期望值，相对容差 1e-9。
  - **negative/**：5 个（fake_empty/fake_print_expected/fake_core_deleted/naive_hardcode_a/naive_no_accumulate）+ negative_selftest.py，**NEG_RC=0/5 全 FAIL**。fake_print_expected→(f) CP 硬编码泄漏（跨输入护栏）；fake_core_deleted→(k) cslin 累加值 0≠期望（cslin 断言有牙）；naive_hardcode_a→(f)。
  - **自验**：ref reference_submit.zip check() PASS；§4.9 三假提交（fake_empty/fake_print_expected/fake_core_deleted）全 FAIL；negative_selftest NEG_RC=0；jsonl test 字段 == 磁盘 check.py（sha 4b58f907 一致）；gate k_rationale=k_check=16≥8 ✓。
- **落库**：append EDA-Eval-DesignFlow_A.jsonl（27 条 / 27 unique ids）→ mark trace_ledger_A 5pv45 case（covered=26/1001=2.6%，touched=33/parked=7）→ 收尾提交双仓。
- **domain 覆盖**：eda_other 1→2（补牙，本条新增 SPF 数据处理）。digital 9 / pnr_signoff 9 / verification 5。
- ⬜ 下轮：①SPFCoupling-001 cline+hook 重跑验 A-faithful 真实通过率（L1 数据处理，预期形态①风险低）；或 ②继续合成（A 档试点 2/10，候选池薄需扩大搜索到 verification/formality）；或 ③修 A-faithful ①+④ 破阈接口。

### 2026-11-03 shard A 轮 34：A-faithful 接口根因修复 = 完成（run_one.sh task_brief 覆盖 bug + 3 case 交付件清单补全，待 cline 重跑验证，WAITING: 0）
- 任务卡本轮路径 = 合成 1 条新 case。但轮 32 收尾遗留**运维令 21:3x §③硬判据 breach**：cline+hook 存量重跑 8 条中 ①+④ 类失败 3/8=37.5% > 30% 阈值 → 运维令"先修接口与判分，不许把格式失败当难度"为最高优先。本轮选**修接口**（合成新 case 会重蹈 ①+④ 覆辙，先修更有价值）。
- **根因调查**：读 `run_one.sh` workdir-build python 块发现——建 workdir 时用**硬编码通用模板**写 `task_brief.md`（"工作目录/输入/交付"4 行），**完全忽略** `assets/<task_id>/task_brief.md` 里精心写好的 case 专属交付件清单。三条 ①+④ 失败（STAFlow 漏 STA_flow/ wrapper + setup/，TLEFRules 漏 lef_rules.py，SynLintFlow 漏 9 文件 DC flow）全部由此 bug 导致：cline 只看到通用 brief + 逐字 prompt，不知交付件目录契约 → 按字面产通用文件 → ①形态/④分歧义 FAIL。**非模型能力不足**。
- **修复① run_one.sh**（`designflow/cline_eval/run_one.sh`）：python 块改为 `if os.path.isfile(assets_src/task_brief.md): shutil.copy(...→workdir/task_brief.md) else 通用模板`。heredoc python 语法 ast.parse 校验通过。注释标明根因 + 运维令 21:3x §①3 依据。
- **修复② 3 case brief 补全**（运维令 21:3x §①3 允许"task_brief 只写交付接口与文件位置，不写要做什么"）：
  - **SynLintFlow-001**：原 brief 仅"lint/ 与 syn/ 两个文件夹" + 悬空引用 `ref_syn_prj/lagat_flow_ref/`（assets 中不存在 → cline 困惑）→ 重写：完整 9 文件 syn/ 树（Makefile/SourceMe/README.md/setup common_setup.tcl/scripts {dc,dc_setup,dc_setup_filenames}.tcl/sdc cfreq_ctrl.sdc/data syn_filelist.f）+ 5 文件 lint/ 树（work {Makefile,design_rtl.list,cfreq_ctrl.prj}/config {cdc_sdc,rdc_sdc}.sdc），删悬空引用。**只列文件位置，内容断言（USE_LSF/HL22/set_svf/compile_ultra -gate_clock/report qor...）留 check.py 测能力**。
  - **STAFlow-001**：原 brief 仅"STA_flow/ + setup/scr/run/README.md"顶层子目录 → 增列具体文件树：sta_main.tcl + 10 编号步骤（1_setup..10_rpt）+ run_sta.csh/run_demo.csh + setup/common_setup.tcl + README.md。feint_reference/ 引用保留（合法 attachment）。
  - **TLEFRules-001**：原 brief 已充分（lef_rules.py + rules_report_A.md + README.md + JSON schema）→ 不改。run_one.sh 修复后该 brief 终能送达 cline（此前被通用模板覆盖）。
- **隔离验证**（不部署 hook / 不跑 cline，避免干扰其他 shard）：python 模拟 run_one.sh workdir-build 逻辑跑 3 case → 全部 brief_src=case-specific / leak CLEAN / attachments 正确复制。STAFlow brief 496B / TLEFRules 407B / SynLintFlow 502B。
- **难度保留论证**：brief 只补"文件位置"（① 形态契约，运维令允许）；**内容断言**（c–p：USE_LSF/bsub/dcnxt_shell、HL22/Au22 ulvt+lvt ssg ccs、set_svf before elaborate、compile_ultra -gate_clock、report qor/timing/area/power/clock_gating、cur_date tag、create_clock REFCLK/FBCLK async、set_false_path RST_N、sc_target.mk include…）仍由 check.py 测，模型须凭 verbatim prompt + 自身知识写正确 flow → 真实难度未稀释。这正是 A-faithful 与 B-synthesized 的区别：B 档 README 写明内容结构 → 形态+内容都给；A 档 brief 只给文件位置 → 形态给、内容考能力。
- **影响范围**：run_one.sh 修复惠及**所有未来 cline 重跑**（不止这 3 条）——任何写了 case 专属 brief 的 case 此前都被通用模板覆盖。EXP-51 落 EXPERIMENTS。
- ⬜ 下轮：①cline 重跑 STAFlow/TLEFRules/SynLintFlow 验 ①+④ 降阈（优先，每条 ~1500s，需单独轮次）；或 ②继续合成（A 档试点 2/10，候选池薄需扩大搜索）；或 ③FormalityLaunchDiag-001 cline 重跑（B 档对照 A/B）。
