# r116 shard C 深读笔记 — 1787570565957_i41yw (ErcBatchReasonFlow-001)

## trace 元数据
- session: 1787570565957_i41yw.messages.json
- user: e0024597 @ hfeg0pkn005 / 10.129.2.14
- mc=286 (keywords: netlist:1014 / virtuoso:111 / pyAether:14 / schematic:2 / calibre:1)
- 421 msgs / 1.64MB / agent cline / cwd /home/e0024597/work/ERC/erc_218_run
- tools used: run_commands×181, read_files×7, search_codebase×6, editor×3, ask_question×2
- **新用户 e0024597**（ledger 无历史，shard C 首个该用户 trace）

## 用户意图（逐字 A-档 seed，提出目标未给根因）
- USER#1(idx0): 「ERC_AI_CHECK 代码在 ERC/codes下，请基于codes下的run_all.sh，对ERC/drcpa_rules/下的数据文件跑完所有follow，只看erc报错里面的2.1-2.8 的」
- USER#2(idx111): 「ERC AI check step1 需要使用大模型去推理所有的2.1-2.8 的错误」
- USER#3-4: API key 填写（key 已掩码，不入 prompt）
- USER#6(idx234): 「需要有自洽性检查 同时 LLM可以承受100 workers 可能你没设置对 或者调整好」
- USER#9(idx270): 「你可以实时监测 让吞吐率高一些」
- USER#5/7/8/10/11/12: 进度查询 / go on / finish?

## 真实 agent 行为
- read_files 探查 ERC/codes 目录树 + run_all.sh；search_codebase 找 filter_erc_by_section / follow 概念。
- 发现 default python3 broken（缺共享库），run_all.sh auto-fallback /usr/bin/python3 3.6.8。
- Virtuoso 已装但 /proj/drcpa/V0/libs Permission denied → Steps 3-4 (Virtuoso) 跳过。
- editor×3: 改 run_all.sh 把 Step 1 从 `--deterministic` 切到 LLM 模式（`analyze_errors_v1.py --workers $WORKERS`，self-consistency ON）。
- run_commands×181: 建干净 workdir（drcpa_rules/ 自包含），后台启 100-worker 并发 LLM 推理流，实时监测进度（503/retry/throughput/ESTAB）。

## 真实 gold（人工复核 msg#420 进度报告）
- 后台进程 PID 1179387，3h18m，3065/11567 (26.5%) 完成。
- By Chkitem: 2.1_ChkMosVgs 1760/1760 ✅(self-consistency) / 2.2_ChkMosVds 1305/5412 / 2.4 0/3 / 2.6 0/1155 / 2.7 0/2171 / 2.8 0/1066。
- glm-5.2 后端 503 反复，gateway 本身 200/2s，模型后端间歇过载。Large prompt 63796 chars（2.2 复杂错误需 900s timeout）。

## 合成决策（B-档 synthesized, L1-boundary）
- gold 依赖 live LLM API（glm-5.2）+ live ERC 跑批（11,567 错误，28h）→ A-档 faithful 不可行（API key/license/时长）。
- B-档 synthesized L1-boundary：离线 ERC CSV fixture（2.1-2.8 + 3.x）+ run_all.sh + filter_erc_by_section.py（候选读）→ 候选写 erc_batch_reason.py（确定性分类器替代 LLM，stdlib-only，subprocess 跑候选 on hidden B）。
- 忠实保留真实意图的 4 要素：①2.1-2.8 段过滤 ②并发推理（100 workers ThreadPool）③自洽性检查（N=3 全一致）④实时进度监测（progress.log 多 snapshot + by-chkitem bars）。

## 资产 A（忠实原文）
- ERC/drcpa_rules/erc_errors.csv: 2.1-2.8 各 5-9 行 + 3.1/3.4（滤除），列 Chkitem|Dev|Node|Hierarchy|Subinfo|Attributes|Status|Part（沿用 ERCFilter-001 的真实 ERC CSV 表头）。
- run_all.sh: Step0 filter_erc_by_section → Step1 analyze_errors_v1.py --workers → Step2 collect_summary（真实多步流摘录）。
- filter_erc_by_section.py: 真实过滤逻辑（section = leading <maj>.<min>，range 2.1-2.8）。
- prompt: USER#1+#2+#6+#9 逐字（key 掩码）+ 环境注（无外网 LLM → 确定性分类器）。

## hidden B（结构不同，杀硬编码 A）
- erc_errors_B.csv: 仅 2.1/2.2/2.3/2.5（4 个 2.x，A 有 8 个）+ 4.1/4.3（滤除）；不同 net 集（pvdd/dvdd/avdd…）、不同行数。
- 期望：候选 by_chkitem = {2.1,2.2,2.3,2.5}，不得泄漏 A 独有的 2.4/2.6/2.7/2.8。

## check.py 18 条独立断言 (a)-(r)
a zip+py_compile / b exit0 on B / c 产 summary.json+progress.log / d 仅 2.x 段且段集==B / e 各段 total==B / f total==filtered_in==sum / g inference 全键 / h cause_category 非空 / i consistency_n==3 且全一致 / j ThreadPoolExecutor / k --workers 默认 100 / l progress 含 elapsed/completed/total/by-chkitem / m >=3 snapshot / n stdlib-only / o 两次 md5 一致 / p 不泄漏 A 独有段 / q --erc-csv 契约 / r filtered_out==B 非 2.x 行数。

## 自验
- ref PASS 18/18（负 selftest：ref=PASS）。
- 6 negative 全 FAIL 各击穿不同条件：naive_hardcode_a→d/e/p（硬编码 A）｜print_expected_only→b/c/g/h/j/m/o（只打印）｜empty_stub→a/c/e/g/m（空壳）｜no_concurrency→j（串行）｜single_snapshot→m（单 snapshot）｜core_deleted→i（自洽性删 core，consistent 恒 False）。
- §4.9 三假：(a)空壳=empty_stub FAIL ｜ (b)只 print 期望串=print_expected_only FAIL ｜ (c)参考解删核心=core_deleted FAIL。全 FAIL ✓。
- 断言闸门：k_rationale=k_check=18 ≥8 ✓。
