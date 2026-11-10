# EXPERIMENTS — Design-Flow Benchmark

## EXP-DG1 analysis-only trace → diagnosis-generator reframe（2026-11-10 r312，acaey PIVOT）

**背景**：r295/r296/r299/r300/r309/r311 连续 6 次确认 shard A fresh digital 池里 clean A-faithful **produce-task** 稀缺（verilog keyword 计数 = READ 活动，非 produce）。acaey (stevenh, verification, mc110) = 典型 analysis-only trace：USER#0 让分析 xmelab `*E,CUVUNF` elaboration 错误，agent 48msgs 全 read_files/search_codebase(0 writes)，产出 prose 根因报告，fix 由 USER 提出。按常规 produce-task 判定 = analysis-only，r311 parked。

**PIVOT**：把 analysis-only trace 经 **spec-driven diagnosis-generator** reframe 成 viable case（匹配 r310 SignalXrefBuilder 模式）。deliverable = `gen_hier_diag.py`（生成器）→ emit `diag_hier_ref.py`（读 spec.json + 结构化 codebase: modules/include_chain/blocks/call_chain，**静态推导**根因：找出错块→推导作用域→判断 hier_name 是否 module→推导 include 位置→扫 bind 块按 references 前缀匹配(排除 distractor)→分类根因→找修复目标）→ 输出 `root_cause.json`(19 派生字段) + `diag_report.md`。check.py 15 conds a-o（独立 recompute 比对），gold PASS 15/15 + 8 negatives 全 FAIL。

**结论**：analysis-only trace 不再是 dead-end——diagnosis-generator reframe 把"agent 无代码产出"的 trace 也纳入造题，是 analysis-dominated fresh 池的破局模板。clean produce scarcity 第 7 次确认，但 scarcity 不再阻塞 case 交付。后续同类 analysis-only verification trace（如 4q4w1 how-to、i555n FM log 诊断）均可照此 reframe。

## EXP-FR1 全量 trace 重扫 + mc 阈值下调评估（2026-11-09 r292，用户直令）

**背景**：r268-r291 连续 17 轮管理轮判定 shard A digital produce-task 候选池 EXHAUSTED，全部依赖 11/05 的 `ssh_eda_search_20261105_192825/summary.tsv`（42 hosts / 3896 sessions / mc30=1511）。用户直令：对目标机群执行全量重扫，评估 mc 阈值下调可行性。

**方法**：
- 在 .75 经 eda_flow run_commands 跑 `probe_remote.sh` over 全 698 IPs（`/home/t0002965/ssh_auth_ok.txt`），`xargs -P 50 -n1 bash -c '... exit 0'`，每 host 300s timeout。
- **关键修复**：每 host `exit 0` 强制返回 0，防止 xargs 在首个 ssh status-255（不可达 host）时 abort。
- 输出落 `/home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv`（7-col：ip host user session_file match_count keywords tools）。
- mc 阈值表：本地 `threshold_analysis_pool.py` 读 shard A pool（3089 dedup sessions，放宽 filter）× 4-shard ledger（excl=2492），按 mc≥30/25/20/15/10/5 统计 sessions/unique_users/un_ledgered/digital_strong/strong_unledgered。
- 可行性 peek：ssh 读 top-14 un-ledgered strong-digital sessions（按 mc 降序）首 1-2 条 user message，人工分类 clean-produce / borderline / analysis-only / wrong-shard / trivial。

**结果**：
1. **全量重扫覆盖**：696/698 hosts reported（vs 11/05 的 42），38082 rows，dedup_sessions=5999（+2103），users=512（+244），mc30=2247（+736），new_sessions_vs_1105=2164。
2. **根因**：11/05 扫描 + `daily_eda_scan.sh` 的 xargs **无 `exit 0`**，ssh 遇不可达 host 返 255 → xargs 立即 abort，覆盖截到 ~42 hosts（abort 前的并行窗口）。此前 17 轮"EXHAUSTED"是 **42-host 覆盖假象**，非真枯竭。
3. **mc 阈值表**（shard A pool 3089 sess）：

| mc≥ | sessions | unique_users | un_ledgered | digital_strong | strong_unledgered |
|----|----|----|----|----|----|
| 30 | 1944 | 376 | 924 | 139 | 26 |
| 25 | 2041 | 388 | 988 | 139 | 26 |
| 20 | 2148 | 396 | 1077 | 150 | 32 |
| 15 | 2279 | 409 | 1191 | 160 | 38 |
| 10 | 2428 | 420 | 1313 | 173 | 44 |
| 5 | 2637 | 444 | 1496 | 186 | 54 |

4. **可行性 peek（n=14）**：clean produce-task=0(0%)，borderline=3(21%)，analysis-only=2(14%)，wrong-shard=8(57%)，trivial=2(14%)。borderline 候选：0ekf9(mc352, testMax DFT demo)、qxaiv/5ze4m(Perl 脚本优化)。wrong-shard 主因：strong-digital marker（verdi/vcs/innovus）噪声大——calibre/virtuoso/SPICE/AMS 会话顺带提 innovus/vcs（wb03t mc698=SpiceAgent CTLE 模拟，l36g5=同，zg8vo/nd56k=virtuoso layout，hfv5q/7z9re=calibre DRC，8uaii=lib PG/LVS，kqelc=ADE/AMS sim）。

**结论与建议**：
- **最低可用阈值=mc≥15（保持现状）**。降到 mc≥10/5 仅 +1313/+1496 un-ledgered 但质量递减（更多 trivial/analysis）。
- **瓶颈不在 mc 阈值，在 filter 质量**：strong-digital marker 57% wrong-shard。应排除纯 calibre/virtuoso/spice/AMS 即使提 innovus/vcs，优先 verilog/rtl/sdc/systemverilog/synthesis 为 DOMINANT keyword 的会话。
- **预计新增 case=10-20**（mc≥15 的 1191 un-ledgered × ~1-2% deepread yield；3/14 borderline ≈ 21% × 62 strong_unledgered ≈ 13 borderline，~半数成 case ≈ 6；加上非 strong 的放宽 filter pool 有 verilog/rtl/tcl produce-task 未触 strong marker）。
- **运维行动**：把 `exit 0` 修复应用到 `/home/t0002965/log/daily_eda_scan.sh` 的 xargs，让 daily cron 覆盖全 698 hosts（当前被 abort-on-255 截到 ~42）。

**交付**：`summary_stats.json.scansync.r292`（含 scan_stats / threshold_table_shardA / feasibility_peek / recommendation）+ scan_path/mc30=2247/hosts=696 更新；MEMORY_DESIGNFLOW_A.md r292 心跳；本节。🚫 不新建 HTML 报告（报告纪律）。

---

## 已归档（→ ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 1，2026-10-28 第10轮）
- EXP-01 8092 MCP 协议探查 → 8092=RESEARCH-MCP-SERVER，无 exec/ssh。
- EXP-02 .75 SSH 连通性 → ping 通但 Permission denied，无免密。
- EXP-03 本机 cline 资产盘点（只读）→ 1 机/19 用户/3487 session 目录。
- EXP-04 bench_v0.1 脱敏与评分管线 → 2258 任务，leak check 通过。
- EXP-05 第2轮复探 8092/.75 → 仍无 exec/凭证。
- EXP-06 bench_v0.2 细化分类+TF-IDF 聚类 → 兜底桶 837→384。
- EXP-07 PII 残留人名发现与修复 → shiwei/zhulong scrub，重跑 0 残留。
- EXP-08 第3轮复探 → .75 恶化不可达，🔔 连续3轮卡点触发上报。
- EXP-09 第4轮复探+bench_v0.3 → CJK 修复+人工策展+监督基线 acc=0.8248。
- EXP-10(first) 第5轮复探+bench_v0.4 → LLM-judge 标注层，v3/v4 一致率 0.5914。


## EXP-06 (2026-10-28) bench_v0.5 多标注者共识 gold + 裁决脚手架
→ 已归档批次 2（原文搬入 ARCHIVE_OPERATOR_DESIGNFLOW.md，第14轮体积维护）。要点：2-annotator consensus gold 269/splits 861；分歧热点 code_dev→other 174 / code_dev→noise_toy_test 146；发现 146 重复 session_id（v0.6 修复）。

## EXP-07 (2026-10-28) bench_v0.6 session_id 去重 + global_id 消歧 + PII 泄漏修复
→ 已归档批次 2。要点：2258→2112（146 跨用户 dup 折叠）；gold 247→246 / splits 954→850；修 Cxmt@202608/svc.edaagent PII（extract.py +3 正则，重跑全链路 0 残留）。

## EXP-08 (2026-10-28) bench_v0.7 逐比特可复现性验证 + 发现并修复两处真实可复现性隐患
→ 已归档批次 2。要点：VERDICT PASS 73/73；修 4×datetime.now()→_now_iso() + PYTHONHASHSEED=0（hash 随机化是 v0.5 漂移真根因，非"种子"）。acceptance #4 闭环。

## EXP-09 (2026-10-28) 第9轮复探 + bench_v0.8 源快照冻结 + 跨主机可复现性
→ 已归档批次 2。要点：3487→3478 漂移证据；freeze.py 源 manifest（snapshot_id a1cd058a…）；freeze-by-default；cross_time VERDICT PASS 40/40（零 /home 访问）。

## EXP-10 (2026-10-28) 第10轮复探 + bench_v0.9 规范发布 bundle + 提交评估器
→ 已归档批次 2。要点：装配 tasks/gold/few_shot/test_set 4 发布文件；split integrity PASS（global_id/session_id 交集=0）；eval_submission.py 评估器；EVAL_SELFTEST majority baseline acc=0.2146。

---

## EXP-11 (2026-10-28) bench_v0.10 v1.0-rc1 发布候选打包层
→ 已归档批次 5。要点：v0.9 data→v0.10 releasable dataset（DATA_CARD/LICENSE/CITATION/BASELINE_MODEL_CARD/RELEASE_CHECKLIST）；4 数据文件 vs v0.9 frozen sha 逐一对齐；internal_shippable=True，final v1.0 仅 3 运维 gate 未关。

## EXP-12 (2026-10-28) bench_v0.11 worked example submission 层
→ 已归档批次 5。要点：仅用冻结 few_shot[27] 训练 TF-IDF+CJK-bigram+tools+nearest-centroid→预测 test_set[219]→eval acc=0.8174/macroF1=0.7239/coverage=1.0；split-integrity guard 无标签泄漏；修 build-host 路径嵌入账号名→相对路径。

## EXP-13 (2026-10-28) bench_v0.12 统一入口 README 聚合层
→ 已归档批次 5。要点：designflow/README.md 静态导航（角色入口表+版本索引+DAG）；leak check 抓修 2 处 PII 再引入（账号绝对路径+服务密码明文）。

## EXP-14 (2026-10-28) bench_v0.13 版本演进 diff 层
→ 已归档批次 5。要点：version_diff.py 扫 11 版本 out/ 算 sha256 manifest+相邻 delta；修 v0.7 out/_repro_tmp scratch 污染（73 artifacts）；DETERMINISM PASS。

---

## EXP-15..EXP-16 — 已归档（→ ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 14，2026-10-29 第32轮体积维护）
- EXP-15 v0.14 统计严谨性层 / EXP-16 v0.15 去偏 split + 双标注者评分层——2 个已闭合块原文搬入 ARCHIVE 批次 14。要点：v0.14 三审计（κ=0.4496 / selection_bias BIAS_PRESENT[test 0/219 disputed vs 语料 40.5%] / bootstrap 95% CI acc[0.767,0.868]）；v0.15 修复 easy-only 偏倚（debiased 368=219 consensus+149 disputed，disputed 分率 0→0.405），gap=+0.5087 定量化"选择偏倚放大 accuracy"，双标注者 disputed 无 gold 用 agreement 而非伪造。

## EXP-17..EXP-20 — 已归档（→ ARCHIVE_OPERATOR_DESIGNFLOW.md 归档批次 7，2026-10-28 第23轮体积维护）
- EXP-17 v0.17 诊断发布 bundle / EXP-18 v0.18 disputed 项机理性刻画 / EXP-19 v0.19 诊断 split 自包含发布包 / EXP-20 v0.20 发布整合/弃用层——4 个已闭合块原文搬入 ARCHIVE 批次 7。要点：v0.17 打包去偏 split 成诊断 bundle（v0.20 判 SUPERSEDED by v0.19）；v0.18 6 维度刻画 +0.51 gap 机理（code_dev↔other↔noise 边界模糊/短 prompt d=−0.33/top-3 用户占 54.4%）；v0.19 融合 v0.17+v0.18 + blinded/answer-key 分离 + 独立 CLI 评估器（规范诊断发布）；v0.20 机器验证 v0.17→v0.19 超集 5/5 + 标 v0.17 SUPERSEDED + 顶层 RELEASE_INDEX。

## EXP-21 — v0.21 诊断 split bootstrap CI + gap 显著性层（第22轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 9（2026-10-28 第26轮体积维护）。要点见本节标题 + MEMORY 流水。

## EXP-22 — v0.22 发布索引再生 + DATA_CARD addendum §G 整合层（第23轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 9（2026-10-28 第26轮体积维护）。要点见本节标题 + MEMORY 流水。

## EXP-23 — v0.23 冻结 lineage 完整性全扫层（第24轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 9（2026-10-28 第26轮体积维护）。要点见本节标题 + MEMORY 流水。

## EXP-24 — v0.24 发布索引再生 + DATA_CARD addendum §H 整合层（第25轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 12（2026-10-29 第29轮体积维护）。要点：纳入 v0.23 全树完整性审计 + 回写 §H 到 v0.16 addendum，23 版本/22 ACTIVE/1 SUPERSEDED，机器验证 v0.23 freeze-integrity 四项全过。要点见本节标题 + MEMORY 流水。

## EXP-25 — v0.25 per-user 公平性审计层（第26轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 12（2026-10-29 第29轮体积维护）。要点：consensus 11 用户 Gini0.5654/top-3 70.3%，**LOUO |Δ|max=0.0486<0.05 headline IS user-robust**，但 8/9 类单用户垄断→per-class 尾类==per-user metric。要点见本节标题 + MEMORY 流水。

## EXP-26 — v0.26 user-stratified re-split 构造层（第27轮，2026-10-28）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 12（2026-10-29 第29轮体积维护）。要点：首个主动构造未见用户 held-out test 的层，**user-strat acc=0.5882 vs headline 0.8174 → gap=−0.2291**，3 类 IMPOSSIBLE 源硬限。要点见本节标题 + MEMORY 流水。



## EXP-27 — v0.27 发布索引再生 + DATA_CARD addendum §I 整合层（第28轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 16（2026-10-29 第33轮体积维护）。要点：纳入 v0.25+v0.26，索引 23→26 版本，§I 两轴量化（user-robust ✅ / unseen-user gap −0.23 ❌），机器验证 v0.25/v0.26 freeze-integrity 全过。要点见本节标题 + MEMORY 流水。

## EXP-28 — v0.28 user-balanced re-split 构造层（v1.x 候选）（第29轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 16（2026-10-29 第33轮体积维护）。要点：多用户 train + 资格规则，仅 2/9 类 Tier-A，matched-count 177==177 dZ=−0.1176 证伪「多用户即缩 gap」，gap 是内禀难度。要点见本节标题 + MEMORY 流水。

## EXP-29 — v0.29 发布索引再生 + DATA_CARD addendum §J 整合层（第30轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 16（2026-10-29 第33轮体积维护）。要点：纳入 v0.28，索引 26→28 版本，§J 用 matched-count 实验回答 v0.27 §I 开放问题（gap 是内禀难度，加用户正交于缩 gap）。要点见本节标题 + MEMORY 流水。

## EXP-30 — 已归档（v0.30 冻结 lineage 完整性 RE-sweep subsumes v0.23，第31轮 → ARCHIVE 归档批次 18；28 版本/151 锚点 147 PASS+4 LIVING，drift_vs_v023 94/94，建模 v0.23 latent living-file bug；DETERMINISM 3/3 + leak 0）

## EXP-31 — 已归档（v0.31 发布索引再生 + §K 整合层，第32轮 → ARCHIVE 归档批次 18；纳入 v0.30，30 版本/29 ACTIVE/1 SUPERSEDED，机器验证 v0.30 freeze-integrity 7 项全过，§K 回写 v0.23 latent bug 建模；DETERMINISM 5/5 + leak 0）


## EXP-32 — 已归档（v0.32 stronger-model gap-shrink 构造层 v1.x 候选，第33轮 → ARCHIVE 归档批次 19；逐位复用冻结 v0.26 split 三 arm 受控对比：CONTROL 复现 0.588235 / TREATMENT B softmax 同特征 acc 0.8039 gap −0.0134 shrink +0.2157 几乎闭合 / TREATMENT C softmax+粗 meta acc 0.3137 反扩大 gap；verdict gap 主项=weak-model artifact 非内禀难度，残项=薄类源硬限；修订 v0.28 §J；DETERMINISM 7/7 + leak 0）

## EXP-33 — 已归档（v0.33 发布索引再生 + §L 整合层，第34轮 → ARCHIVE 归档批次 19；纳入 v0.32，32 版本/31 ACTIVE/1 SUPERSEDED，§L 修订 v0.28 §J「内禀难度」为「weak-model artifact 主项 + 薄类源硬限残项」，机器验证 v0.32 freeze-integrity 全过 [含 4 v0.26 split 文件跨层独立重算 match v0.32 声明 AND v0.26 自身 manifest]；DETERMINISM 5/5 + leak 0）


## EXP-35 — 已归档（v0.34 冻结 lineage 完整性 RE-sweep 构造层 subsumes v0.30，第35轮 → ARCHIVE 第49轮 EXP 体积维护；已被 v0.40/v0.44/v0.46/v0.48 RE-sweep 传递式 subsumes）

## EXP-36 — 已归档（v0.35 发布索引再生 + §M 整合层，第36轮 → ARCHIVE 第49轮 EXP 体积维护；已被 v0.41/v0.43/v0.45/v0.47 §N/§P/§R/§S 整合层扩展覆盖）

## EXP-37 — 已归档（v0.36 meta-feature scaling-artifact 消融构造层，第37轮 → ARCHIVE 第49轮 EXP 体积维护；已被 v0.38/v0.42 CI 构造层 + 后续整合层覆盖）

## EXP-38 — v0.37 发布索引再生 + DATA_CARD addendum §N 整合层（第38轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 22（2026-10-29 第39轮体积维护）。要点：纳入 v0.36，36 版本/35 ACTIVE/1 SUPERSEDED，§N 修正 §L「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」，§L 主结论 + 缩 gap 方向不变；DETERMINISM 5/5 + leak 0。要点见本节标题 + MEMORY 流水。

## EXP-39 — v0.38 gap-shrink bootstrap CI 构造层（第39轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 27（2026-10-29 第43轮体积维护）。要点：v0.38 给首个 unseen-user gap 置信区间——配对 percentile bootstrap n=51/n=42：B 缩 gap over CONTROL +0.2157 显著 [0.0980,0.3529] p=0.0005（§L weak-model-artifact 主轴对重采样稳健）；B 残余 gap −0.0134 含 0 [−0.1311,0.0846] p=0.4478（统计上闭合，强化 §L）；C 崩溃 −0.2745 显著 [−0.4118,−0.1373] p=0.0（v0.36 缩放伪影真实）。cross-check vs v0.32 9/9 点估计 MATCH；DETERMINISM + freeze-integrity + leak 0。已被 §O(v0.39) 整合 + v0.40 lineage RE-sweep 覆盖 + v0.42 per-class CI cross-check 其 headline。要点见本节标题 + MEMORY 流水。


## EXP-40 — v0.39 发布索引再生 + DATA_CARD addendum §O 整合层（第40轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 28（2026-10-29 第44轮体积维护）。要点：纳入 v0.38，38 版本/37 ACTIVE/1 SUPERSEDED，§O 把 §L/§N 核心结论从点估计升级为 CI（B 缩 gap [0.0980,0.3529] p=0.0005 对重采样稳健，退役 magnitude caveat；C 崩溃 [−0.4118,−0.1373] p=0.0 确认缩放伪影真实；B 残余 gap 含 0 统计上闭合强化 §L），首个 unseen-user gap CI；机器验证 v0.38 freeze-integrity 全过；DETERMINISM 5/5 + leak 0。要点见本节标题 + MEMORY 流水。

## EXP-41 — v0.41 发布索引再生 + DATA_CARD addendum §P 整合层（第42轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 28（2026-10-29 第44轮体积维护）。要点：纳入 v0.40，40 版本/39 ACTIVE/1 SUPERSEDED，§P 把全树冻结完整性证据覆盖窗口从 §M 的 32 版本（v0.34）扩展到 38 版本（v0.40）——v0.40 扫 38 版本/89 manifest/206 锚点→197 PASS + 9 LIVING，drift_vs_v034 112/112 0 回归，17 net-new；不推翻 §H/§K/§M，记录 §H→§K→§M→§P RE-sweep cadence 第 4 次全树审计；机器验证 v0.40 freeze-integrity 全过；DETERMINISM 5/5 + leak 0。要点见本节标题 + MEMORY 流水。

## EXP-42 — v0.42 per-class gap-shrink bootstrap CI 构造层（第43轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 29（2026-10-29 第45轮体积维护）。要点：v0.42 闭环 v0.38 显式留的「per-class contrasts not computed」——把 §L/§O weak-model-artifact **定位到具体类**。per-class paired bootstrap（10000 次，`numpy default_rng(seed=0)`，within-class shared resample；n≥10 报 CI，n<10 仅点估计）。**`other`**（n=15/14）B−CONTROL shrink +0.6667/+0.7143 95% CI [0.4,0.8667]/[0.5,0.9286] p=0.0 两子集均显著（CTRL 0.267/0.286→B 0.933/1.000）＝v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界现 CI-backed，§L weak-model-artifact 定位到此类；`code_dev`（n=27/25 最大类）shrink +0.0741/+0.04 CI 含 0 ns＝弱模型天花板非 gap 源；薄类 n≤4 仅点估计＝v0.28/v0.32 薄类源硬限残项的 per-class-CI 证据。**精化（不推翻）§L/§O**；gap-attribution cadence §I→§J→§L→§N→§O→per-class 闭环。cross-check vs v0.32 9/9 + vs v0.38 headline CI 逐位相等 [0.098039,0.352941]；DETERMINISM 4/4 + freeze-integrity + leak 0。已被 §Q(v0.43) 整合 + v0.44 lineage RE-sweep 覆盖其 freeze-integrity。要点见本节标题 + MEMORY 流水。

## EXP-43 — v0.43 发布索引再生 + DATA_CARD addendum §Q 整合层（第44轮，2026-10-29）
→ **原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 30**（留指针；已被 v0.44 lineage RE-sweep[drift_vs_v040 126/126 重验证 v0.41–v0.43 frozen 锚点] + v0.45 §R 整合层[机器验证 v0.44 freeze-integrity 全过]覆盖其 freeze-integrity）。要点：把 v0.42 per-class gap-shrink CI 纳入 RELEASE_INDEX（42 版本/41 ACTIVE/1 SUPERSEDED），§Q 精化 §L/§O 把 weak-model-artifact 定位到 `other` disputed 边界（CI-backed）；gap-attribution cadence §I→§J→§L→§N→§O→§Q per-class 闭环。DETERMINISM 5/5 + leak 0。

## EXP-44 — 已归档（v0.44 冻结 lineage 完整性 RE-sweep 构造层 subsumes v0.40，第45轮 → ARCHIVE 归档批次 31；42 版本/97 manifest/228 锚点[144 unique]→217 PASS+11 LIVING+0 broken；drift_vs_v040 126/126 0 回归+9 net-new；DETERMINISM 3/3+leak 0；产 lineage_audit_v044.json sha256 `f9a7e77b…`；已被 v0.46 RE-sweep subsumes、v0.47 §S 整合覆盖）

## EXP-45 — 已归档（v0.45 发布索引再生 + DATA_CARD addendum §R 整合层，第46轮 → ARCHIVE 归档批次 31；纳入 v0.44，44 版本/43 ACTIVE/1 SUPERSEDED，机器验证 v0.44 freeze-integrity 全过[headline 42/97/228/144/217/11/0/0+drift_vs_v040 126/126+独立重算 v0.44 输出/v0.13/v0.40/v0.15 锚点]，§R 扩展 §P 覆盖窗口 38→42 版本不推翻 §H/§K/§M/§P；DETERMINISM 5/5+leak 0；已被 v0.47 §S 扩展覆盖窗口到 44 版本）

## EXP-46 — v0.46 冻结 lineage 完整性 RE-sweep 构造层（第47轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 35（第57轮体积维护）。要点：第 6 次全树审计（承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence），44 版本/101 manifest/231 锚点[145 unique]→220 PASS+11 LIVING+0 broken，drift_vs_v044 133/133 0 回归+1 net-new（v0.44 audit output 自身），传递式 subsumes v0.44 的 drift_vs_v040；产 lineage_audit_v046.json sha256 33e881a3…；DETERMINISM 3/3+leak 0+不改冻结 v0.1–v0.45 out/。已被 v0.47 §S 整合层纳入 RELEASE_INDEX（46 版本/45 ACTIVE/1 SUPERSEDED）。

## EXP-47 — v0.47 发布索引再生 + DATA_CARD addendum §S 整合层（第48轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 35（第57轮体积维护）。要点：metadata_integration——`integrate.py` 加载冻结 v0.45 index[44 版本]为基线，机器验证 v0.46 freeze-integrity 全过（headline 44/101/231/145/220/11/0/0 + drift_vs_v044 133/133 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.46 输出 33e881a3… + v0.13 manifest c83ea686… + v0.44 audit 回归基线 f9a7e77b… + v0.15 锚点 5dd43df6）；append v0.46+v0.47→46 版本/45 ACTIVE/1 SUPERSEDED；回写 §S（不推翻 §H/§K/§M/§P/§R，覆盖窗口 42→44 版本，第 6 次全树审计 cadence，living-file 模型 UNCHANGED 11 LIVING）；DETERMINISM 5/5+leak 0+不改冻结 v0.1–v0.46 out/。已被 v0.49 §T 整合层进一步扩展覆盖到 46 版本。

## EXP-48 — v0.48 冻结 lineage 完整性 RE-sweep 构造层（subsumes v0.46）（第49轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 33（第50轮体积维护，已被 v0.49 §T 整合层 subsume）。要点：v0.48 subsumes v0.46 第 7 次全树审计，46 版本/105 manifest/234 锚点[146 unique]→223 PASS+11 LIVING+0 broken，drift_vs_v046 134/134 0 回归+1 net-new（v0.46 audit output 自身），drift_vs_v046 传递式 subsumes v0.46 的 drift_vs_v044，frozen RELEASE_INDEX copies 11/11，drift_vs_v013 73/73，v0.15 锚点 5dd43df6；产 lineage_audit_v048.json sha256 08553f86…；DETERMINISM 3/3+leak 0+不改冻结 v0.1–v0.47 out/。已被 v0.49 §T 整合层纳入 RELEASE_INDEX（48 版本/47 ACTIVE/1 SUPERSEDED）。

## EXP-49 — v0.49 发布索引再生 + §T 整合层 + .75 eda_flow MCP 解锁（第50轮，2026-10-29）

> 原文已归档至 `ARCHIVE_OPERATOR_DESIGNFLOW.md` 归档批次 35（第57轮体积维护）。要点：integration layer + 环境能力解锁——`integrate.py` 加载冻结 v0.47 index[46 版本]为基线，机器验证 v0.48 freeze-integrity 全过（headline 46/105/234/146/223/11/0/0 + drift_vs_v046 134/134 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.48 输出 08553f86… + v0.13 manifest c83ea686… + v0.46 audit 基线 33e881a3… + v0.15 锚点 5dd43df6）；append v0.48+v0.49→48 版本/47 ACTIVE/1 SUPERSEDED；回写 §T（不推翻 §S，覆盖窗口 44→46 版本，第 7 次全树审计 cadence，living-file 模型 UNCHANGED 11 LIVING）；DETERMINISM 5/5+leak 0。**🆕 .75 eda_flow MCP 解锁**：连续 50 轮「.75 SSH 拒」卡点实质解决（eda_flow MCP 提供 open_session/run_commands→.75 read-only 命令执行）；只读探查 .75=第二个 cline 主机（hostname hfhds201，16 用户/192 session dirs/192 messages.json，格式同本机）。3 口径更新=2 机/3679 轨迹/3671 messages（本机 3487 + .75 192）。v0.50 候选=.75 多机扩源构造层（高价值，新解锁）。

## EXP-50（2026-10-29 第51轮）v0.50 多机扩样层 — 经 eda_flow MCP 从 .75 只读构建
- **目的**：执行运维增补 II——停止 lineage 自审计空转，基于沈佳成 698 机落盘扫描结果构建首个多机版 benchmark。
- **方法**：eda_flow.open_session + run_commands 只读拉 .75 上 `ssh_eda_search_20261028_174426/{scan.tsv,summary.tsv,probe_remote.sh}`；python3 在 .75 上分类(summary.tsv 24085 命中→11 类,categorize() 按 probe_remote.sh RE1/RE2 marker 优先级)+脱敏(sha1[:12])；close_session；本地 build.py(PYTHONHASHSEED=0) 生成 out/ 9 产物。
- **三口径**：698 机 / 2850 用户 / 52698 会话文件 / 24085 IC/EDA 命中 / 384 命中用户。
- **11 类分布**：layout_aether 14534 · layout_virtuoso 2496 · schematic_netlist 2362 · physical_verify 1295 · analog_context 1167 · spice_sim 1027 · pnr_signoff 503 · waveform 368 · logic_synth 167 · eda_other 159 · skipper 7。
- **评分口径**：weighted_coverage = Σ weight_c·pass_c（weight = 实测频率）；generalization_gap = held-out user/host 加权覆盖 − in-distribution（cf. v0.26 gap=−0.2291）。
- **分布诊断**：per-host matched Gini=0.8036 / per-user matched Gini=0.7738 / top-1 user share=8.7% → 高集中度，in-distribution accuracy 不足，需 user-stratified held-out。
- **质量门**：DETERMINISM PASS（reproduce.sh 双跑 sha256 一致）；PII leak PASS（committed 文件 0 raw IP/email/真实用户名/路径/token；hash 字段 12-hex 校验过；scan.tsv 原始 IP 入 .gitignore 不入库；provenance .75 IP + 扫描属主用户名脱敏）。
- **结论**：v0.50 = multi_machine_expansion_layer（非审计层/非 §X 递归），是 51 轮来首个真实多机扇出的 benchmark 版本；v0.1–v0.49 lineage 审计系列 halt；v0.1 单机集作废（RSI 污染）。
- **局限**：task-distribution/coverage benchmark（session 元数据），per-task gold 需按需深挖单会话（red line 限不批量）；单次扫描快照（2026-10-28），用户持续增长→后续版本重扫扩展。

## EXP-51（2026-11-03 shard A 轮 33）A-faithful 接口根因修复 — run_one.sh task_brief 覆盖 bug + 3 case 交付件清单补全
- **背景**：运维令 21:3x §③判据「A 档 ①+④ 类失败占比 ≤30%」。cline+hook 存量重跑 8 条中 STAFlow-001 / TLEFRules-001 / SynLintFlow-001 三条 ①+④ 失败 = 3/8 = 37.5%，**破 30% 阈值** → 需"先修接口与判分，不许把格式失败当难度"。
- **根因（关键发现）**：`designflow/cline_eval/run_one.sh` 建 workdir 时用**硬编码通用模板**覆盖 `task_brief.md`（"工作目录/输入/交付"4 行），**完全丢弃** `assets/<task_id>/task_brief.md` 里精心写好的 case 专属交付件清单。cline 只看到通用 brief + 逐字 prompt → 不知道交付件目录契约 → 按字面产通用文件 → ①交付形态/④判分歧义 失败。**三条 ①+④ 全部由此 bug 导致**，非模型能力不足。
- **修复① run_one.sh**：改为优先 `shutil.copy(assets_src/task_brief.md → workdir/task_brief.md)`，无则回退通用模板。嵌入 heredoc 的 python 语法校验通过；3 case workdir-build 隔离模拟全过（brief_src=case-specific / leak CLEAN / attachments 正确复制）。
- **修复② 3 case brief 补全（运维令 21:3x §①3 允许"task_brief 只写交付接口与文件位置"，不改意图）**：
  - **SynLintFlow-001**：原 brief 仅"lint/ 与 syn/ 两个文件夹" + 悬空引用 `ref_syn_prj/lagat_flow_ref/`（assets 中不存在）→ 重写为完整 9 文件 syn/ 树（Makefile/SourceMe/README.md/setup common_setup/scripts {dc,dc_setup,dc_setup_filenames}.tcl/sdc/data syn_filelist.f）+ 5 文件 lint/ 树（work {Makefile,design_rtl.list,cfreq_ctrl.prj}/config {cdc_sdc,rdc_sdc} .sdc），删除悬空引用。**只列文件位置，不写内容**（USE_LSF/HL22/set_svf/compile_ultra 等内容断言留在 check.py 测能力）。
  - **STAFlow-001**：原 brief 仅"STA_flow/ + setup/scr/run/README.md"（顶层+子目录）→ 增列具体文件树（sta_main.tcl + 10 编号步骤 1_setup..10_rpt + run_sta.csh/run_demo.csh + setup/common_setup.tcl + README.md）。feint_reference/ 引用保留（是合法 attachment）。
  - **TLEFRules-001**：原 brief 已充分（lef_rules.py + rules_report_A.md + README.md + JSON schema）→ 不改。run_one.sh 修复后该 brief 终能送达 cline。
- **难度保留**：brief 只补"文件位置"（① 形态契约），**内容断言**（c–p：USE_LSF/bsub/dcnxt_shell、HL22/Au22 ulvt+lvt ssg ccs、set_svf before elaborate、compile_ultra -gate_clock、report qor/timing/area/power、cur_date tag、create_clock REFCLK/FBCLK async、set_false_path RST_N…）仍由 check.py 测，模型须凭 verbatim prompt + 自身知识写出正确 flow → 真实难度未稀释。
- **待验证**：修复需 cline 重跑确认 ①+④ 降阈（本轮 40 min 预算不足跑 3×1500s 重跑，留下一轮）。预期：brief 送达后 cline 产对文件树 → ① 形态断言过 → 剩余内容断言测能力 → 真实通过率应低于旧 ①+④ 表观失败率。
- **影响范围**：run_one.sh 修复惠及**所有未来 cline 重跑**（不止这 3 条）——任何写了 case 专属 brief 的 case 此前都被通用模板覆盖。

## EXP-52 (2026-11-03 shard A 轮35): TLEFRules-001 cline+hook 重跑 — ①消除验证 + ④width_range schema bug 定位修复
**背景**：EXP-51（轮34）修了 run_one.sh task_brief 覆盖 bug + 3 case brief 补全，但未跑 cline 验证。运维令 21:3x §③判据：①+④ 占比 ≤30% 才不修接口；轮32 8 条 ①+④=3/8=37.5% 破阈。本轮验轮34修复是否真降 ①。

**.75 宕机**：本轮 eda_flow run_commands 全 exit -1 / duration 0 / stdout 只回显 bashpool wrapper（3 次重试+换 session 都一样），run_code pyAether MCP timeout，ssh 10.129.32.75 Connection timed out → 拿不到 summary.tsv 候选 → 合成路径阻塞。pivot 到本地 cline 重跑（不需 .75）。

**TLEFRules-001 重跑**（701s/exit0/5iter）：
- 旧跑（266s，轮32）：cline 只写 summary.md → FAIL (a) lef_rules.py missing → ①+④
- 新跑（701s，brief 修复后）：cline 产 lef_rules.py(10.4KB)+rules_report_A.md(3.8KB)+README.md(3.1KB) → FAIL 前移到 (j)(t) width_range 格式 → **① 消除，仅剩 ④narrow**
- ④ 根因：brief `width_range{}` 被 cline 解为嵌套 dict {min,max}；check.py 要 `{"M1":"0.88 TO 14"}` 字符串值 → brief/check schema 不一致（我的 bug）
- 修复：brief → `width_range{<layer>:"<min> TO <max>"}` + 明示值是字符串非嵌套 dict；check.py 不动

**结论**：
1. **轮34 接口修复生效**（硬证据）：case-specific brief 送达后 cline 真产对交付件树 → ①交付形态断言消除。run_one.sh `shutil.copy(assets/task_brief.md→workdir/)` 修复惠及所有有 case-specific brief 的 case。
2. **①+④ 重算 9 条**：3 PASS/9=33.3%；①+④=3/9=33.3%（STAFlow① + SynLintFlow①+④ + TLEFRules-rerun④narrow）。① 分量已降（TLEFRules ①→④）。待 STAFlow/SynLintFlow 重跑确认 ① 进一步消除。
3. **④narrow 是 fixable interface bug**（brief/check schema 对齐），非难度稀释——修复后 cline 应能 PASS 或 fail 在更深的 content 断言（测能力）。
4. **难度保留**：brief 只补"文件位置+格式契约"（运维令 21:3x §①3 允许），content 断言（routing/cut/via/viarule 解析正确性、跨输入 B 护栏）仍由 check.py 测。

**待验证**（下轮）：STAFlow-001/SynLintFlow-001 重跑（brief 已修）验 ① 消除；TLEFRules-001 第 2 次重跑验 ④→PASS。

## EXP-53 (2026-11-03 shard B 轮36): zr9dt VIH 翻转点调优 — 便携 NMOS-diff-amp 电路 90% 就绪(0 交付, DEBT:1)
**背景**：本轮选 zr9dt (jasminej/hfeahpc505, mc=180, 764 hspice) —— 真 L2/L3 VIH DC 扫频翻转点调优(trace T0: 改 4 PMOS 尺寸使 CSV 0→1(>0.8) 翻转点落 vih=170 + 3 alter 翻转点尽量接近)。distinct 子技能=optimization-to-target-with-closeness-constraint，shard B 首见。

**.75 HSPICE 便携电路迭代**：
1. PMOS-input diff pair + NMOS diode load：vih≈VDD/2 区 PMOS 不在工作点 → neta/netb 常值、out 钉死 → 弃。
2. NMOS-input diff pair + PMOS mirror load, vbias=0.30：MNb Vgs<Vto(0.5) 截止→无尾电流→死锁 → 弃。
3. 同结构 vbias=0.70：✅收敛，尾电流≈0.27mA，sharp 翻转 alter1 trip≈0.525(out high→low @ vih↑)。
- level-1 model 缺 nsub → "nsub <= ni" abort；补 `nsub=1e16 phi=0.6 gamma=0.4 cj=0 cjsw=0 js=0` 解决。
- V/I source value 用 `{param}` → syntax error；改裸参数名 `W=wp28 L=lp`、`idfe neta 0 idfe`、V 源直接常量。
- `rm -f slice_A.*` 连 .sp 删 → "No valid input file"；只 rm out_*。

**待修(下轮 ~10min)**：(1) 输出极性 netA(falling)→netB→2inv(rising 0→1)；(2) measure `when v(out)=0.8 rise=1`→`cross=1`；(3) idfe 注入 netB 或限幅防 neta 越界 -95mV。修后取 A/B GT → check.py(12+ 断言 a-n) + 6 negative + selftest → B.jsonl。

**物理验证**：trip≈vref(0.5)，随 idfe 平移；spread=idfe_range/gm，gm∝√(Itail·W/L) → wn28/wn23 控 spread、wp10/wp3+wnb 控绝对 trip。center-vs-spread 耦合优化结构成立(可独立调控) → case 难度结构 OK。

**结论**：本轮 0 交付(zr9dt 仍 claimed/in-progress, DEBT:1)，🚫 未落 jsonl/未计通过率。下轮第一件事=继续 zr9dt 交付(不 next 新 trace)。深读+完整 case 计划存 designflow/trace_deepreads/1792143054616_zr9dt_vih_trip_tune.md。

## EXP-54 (2026-11-05 shard B 轮): summary.tsv keyword 列语义 — targeted sub-skill keyword scout 不可行
- **发现**：`/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv` 的 keyword 列($6) = **文件扩展名/工具命中计数**（如 `.cdl:1105;netlist:12;hspice:27;synopsys:19`），**不是用户意图关键词**；tools 列($7) = 命中工具名+lang 标记。原扫描词表只索引文件类型扩展名 + 工具名（hspice/finesim/spectre/calibre/synopsys/cadence/virtuoso/aether/pyaether...），**不索引子技能术语**。
- **后果**：按已识别子技能缺口（noise / fft / thd / distortion / eye / pole-zero / s-parameter / harmonic / snr / sndr / sfdr / onoise / inoise / power-integration）在 summary.tsv 上搜 → **0 候选**（这些词不在扫描词表里）。⇒ **targeted sub-skill keyword scouting via summary.tsv 结构上不可能**。
- **唯一可行路径**：要找特定子技能的 real trace，只能 ssh peek 逐条 messages.json 读 user 首轮原话（成本高，无法批量预筛）。
- **对 scouting 策略影响**：summary.tsv 只能按「spice 工具命中」(hspice/finesim/spectre) + mc 阈值过滤，不能按子技能过滤；shard B 跨全 mc 段(≥30/30-260/15-29/10-14) 4 轮 spice-keyword scouting 已穷尽，干净 distinct spice_char real trace 池 = 枯竭。后续若要补 noise/THD/FFT/eye/PZ 等真子技能缺口 case，需运维放行「无 real trace 的合成 L2」(红线 #1 例外) 或接受 L1 补牙 park-reframe（本 SimStatusMonitor-001 路径）。
- **本轮交付**：EDA-Eval-DesignFlow-SimStatusMonitor-001（mf0l3 park→case，L1 补牙，k=15，ref 15/15 PASS，5 neg distinct FAIL）。ledger case 77→78.
