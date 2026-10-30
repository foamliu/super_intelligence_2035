# EXPERIMENTS — Design-Flow Benchmark

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
