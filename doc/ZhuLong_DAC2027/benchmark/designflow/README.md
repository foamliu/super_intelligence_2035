# Design-Flow Benchmark — Unified Entry (v0.12, updated through v0.49)

真实场景设计流 Benchmark，基于本机 EDA 服务器上真实 cline 用户交互轨迹（脱敏）构建。
本文件是整个 `designflow/` 工作树的**统一入口索引**，把 v0.1–v0.49 四十八个版本目录
串成一条可导航、可复现、可发布的链路。新增用户请先读本文件，再按"推荐入口"进入。

> v0.12 = 统一入口层（本文件 + 索引）。不产生新数据，零 `/home` 访问，纯静态导航文档；
> 旨在闭环 v0.1–v0.11 各版本目录"各自有 README、缺一个聚合入口"的可发现性缺口。
> **v0.22 增补**：状态/弃用维度见顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)
> （v0.22 整合层再生，机器可验证：v0.17 已 SUPERSEDED by v0.19；v0.21 已纳入索引）。
> **v0.23 增补**：冻结 lineage 完整性全扫——见 [`bench_v0.23/`](bench_v0.23/)，
> 把 v0.22 的单锚点 freeze-integrity 推广为全树 124 锚点穷举校验（全 PASS）；
> v0.23 为完整性审计层（非整合层），按 v0.21 先例把 RELEASE_INDEX 再生推到下一整合层。
> **v0.24 增补**：发布索引再生 + DATA_CARD addendum §H 整合层——见 [`bench_v0.24/`](bench_v0.24/)，
> 把 v0.23 纳入 RELEASE_INDEX（23 版本 / 22 ACTIVE / 1 SUPERSEDED）+ 把 v0.23 全树完整性审计
> 回写进 v0.16 DATA_CARD addendum 作为 §H；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.24 视图。
> **v0.25 增补**：per-user 公平性审计层——见 [`bench_v0.25/`](bench_v0.25/)，把 v0.16 §E「single-machine
> source / 用户集中」定性局限升级为**量化**：consensus 块 11 用户 Gini=0.5654/HHI=0.1951（2.14× 集中），
> top-3 占 70.3%，但 **LOUO |Δ|max=0.0486 < 0.05 → headline accuracy IS user-robust**；**然而 8/9 类
> ≥0.5 单用户垄断**（3/9 ==1.0）→ per-class P/R/F1 对尾类实质是 per-user metric。audit 层（非整合层），
> 不重算 RELEASE_INDEX，按 v0.21/v0.23 先例推到下一整合层再生。
> **v0.26 增补**：user-stratified re-split 构造层——见 [`bench_v0.26/`](bench_v0.26/)，直接闭环 v0.25
> 「per-class 单用户垄断 → 构造 user-stratified re-split [v1.x 构造候选]」。对冻结 v0.15 共识 219 项
> 按用户分层重切：每类主用户进 train，其余用户进 held-out test，测 baseline 对**未见该标签的用户**
> 的泛化。**user-strat acc=0.5882 vs headline 0.8174 → gap=−0.2291**——证实存在 headline 掩盖的
> 未见用户泛化缺口；3 类 IMPOSSIBLE 单用户类（17 项）无法分层（源硬限）。构造层（非整合层），
> 不重算 RELEASE_INDEX，按 v0.21/v0.23/v0.25 先例推到下一整合层再生。
> **v0.27 增补**：发布索引再生 + DATA_CARD addendum §I 整合层——见 [`bench_v0.27/`](bench_v0.27/)，
> 在单一整合步骤中吸收 v0.25（per-user 公平性审计）+ v0.26（user-stratified re-split 构造）：把两层
> 纳入 RELEASE_INDEX（26 版本 / 25 ACTIVE / 1 SUPERSEDED）+ 把 v0.25「headline user-robust 但 per-class
> 单用户垄断」+ v0.26「未见用户泛化 gap=−0.2291」回写进 v0.16 DATA_CARD addendum 作为 §I；机器验证 v0.25
> （4 锚点 match disk + cross_check MATCH）+ v0.26（freeze_integrity PASS + cross_check PASS）freeze-integrity；
> 顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.27 视图。
> **v0.28 增补**：user-balanced re-split 构造层（v1.x 候选）——见 [`bench_v0.28/`](bench_v0.28/)，闭环
> v0.26 下一步候选「据 gap=−0.2291 构造 user-balanced re-split [强制每类多用户，扔掉 IMPOSSIBLE 单用户类]」。
> 新增**多用户 train** 约束（top-2 用户/类）+ 严格资格规则（≥3 用户且 top-2 之外项数 ≥2）：**仅 2/9 类合格**
> （code_dev / other）——诚实的源硬限。受控实验在 2 类 core 上固定 17 项未见用户 test，对比 TRAIN-S（单用户/类，
> v0.26 式）vs TRAIN-M（2 用户/类，**matched count 177==177**）→ **dZ=−0.1176，多用户 train 反而更差**，
> 证伪「收集更多用户即可缩小 gap」的乐观假设：gap 是该特征空间下标签识别的内禀难度。构造层（非整合层），
> 不重算 RELEASE_INDEX，按 v0.21/v0.23/v0.25/v0.26 先例推到下一整合层再生。
> **v0.29 增补**：发布索引再生 + DATA_CARD addendum §J 整合层——见 [`bench_v0.29/`](bench_v0.29/)，
> 把 v0.28（user-balanced re-split 构造层）纳入 RELEASE_INDEX（28 版本 / 27 ACTIVE / 1 SUPERSEDED）
> + 把 v0.28「2/9 类 Tier-A + dZ=−0.1176 多用户 train 反而更差 → 证伪『多用户即缩 gap』」回写进 v0.16
> DATA_CARD addendum 作为 §J；机器验证 v0.28 freeze-integrity（status PASS + cross_check PASS + 公共
> v0.15 锚点 5dd43df6… 跨层独立重算 + 2 provenance 锚点 match disk）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)
> 已再生为 v0.29 视图。
> **v0.30 增补**：冻结 lineage 完整性 **RE-sweep**（subsumes v0.23）——见 [`bench_v0.30/`](bench_v0.30/)，
> 把 v0.23 的全树审计（21 版本 / 124 锚点）重跑到现已冻结的 **28 版本 / 69 manifest / 151 锚点**（108 unique，
> 147 PASS + 4 LIVING_FILE_BYDESIGN），新增 **drift_vs_v023 回归校验**（94/94 v0.23 frozen 锚点仍 bit-intact，
> 排除 1 个 v0.23 误验的顶层 living RELEASE_INDEX.md）+ **frozen per-version RELEASE_INDEX copies 交叉校验**
> (4/4 PASS)。**发现并建模 v0.23 latent bug**：v0.23 把 `outputs[].RELEASE_INDEX.md`（bare name）解析到顶层
> living 文件（按设计被 v0.24→v0.27→v0.29 覆盖），仅因 v0.23 时刻顶层 == v0.22 冻结副本而巧合 PASS；
> v0.30 把 living 文件正确标为 LIVING_FILE_BYDESIGN，真冻结的是各 `bench_v0.XX/out/RELEASE_INDEX.md` 副本。
> 13 net-new anchors since v0.23（v0.24–v0.29 新 provenance 链接）。audit 层非整合层，不重算 RELEASE_INDEX，
> 按 v0.21/v0.23 先例推到下一整合层再生。DETERMINISM PASS（3/3）、leak 0。
> **v0.32 增补**：stronger-model gap-shrink **构造层**（v1.x 候选）——见 [`bench_v0.32/`](bench_v0.32/)，
> 闭环 v0.28 **命名但未测试**的开放结论「缩 v0.26 unseen-user gap=−0.2291 需更强模型/更富特征」。在
> **冻结 v0.26 split 逐位复用**（168/51，受控对比——唯一变量是模型/特征）上：CONTROL 重跑 nearest-centroid
> 复现 0.588235 ✅；TREATMENT B 换成 softmax 回归（**同** TF-IDF+tools 特征）→ acc=**0.8039** gap=**−0.0134**
> shrink=**+0.2157**，**几乎闭合 gap**（fully-unseen 0.667→0.929）；TREATMENT C 加粗 meta 特征反扩大 gap
> （0.3137，meta 编码用户风格非标签语义）。**修订 v0.28 结论**：gap 主要不是「特征空间内禀难度」而是
> **weak-model（最近质心）artifact**——同特征上换成线性判别模型即缩 +0.216。构造层非整合层，不重算
> RELEASE_INDEX，按 v0.26/v0.28 先例推到下一整合层再生。DETERMINISM PASS（7/7）、FREEZE-INTEGRITY PASS、leak 0。
> **v0.33 增补**：发布索引再生 + DATA_CARD addendum **§L** 整合层——见 [`bench_v0.33/`](bench_v0.33/)，
> 把 v0.32（stronger-model gap-shrink 构造层）纳入 RELEASE_INDEX（**32 版本 / 31 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.32「同特征换 softmax 缩 gap +0.2157 几乎闭合 → gap 是 weak-model artifact 非内禀难度」回写进
> v0.16 DATA_CARD addendum 作为 **§L**——**修订 v0.28 §J 的「内禀难度」定性**为「weak-model artifact 主项
> + 薄类源硬限残项」。机器验证 v0.32 freeze-integrity（manifest PASS + v0.15 锚点 5dd43df6… + v0.26 split
> 逐位复用 + CONTROL 复现 0.588235 + 4 个 v0.26 split 文件跨层独立重算 match v0.32 声明 AND v0.26 自身 manifest
> + v0.32 输出 gap_shrink.json match）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.33 视图。
> **v0.34 增补**：冻结 lineage 完整性 **RE-sweep**（subsumes v0.30）——见 [`bench_v0.34/`](bench_v0.34/)，
> 把 v0.30 的全树审计（28 版本 / 151 锚点）重跑到现已冻结的 **32 版本 / 77 manifest / 170 锚点**（118 unique，
> 164 PASS + 6 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING），新增 **drift_vs_v030 回归校验**（104/104 v0.30
> frozen 锚点仍 bit-intact，排除 4 个 living RELEASE_INDEX.md）+ frozen per-version RELEASE_INDEX copies
> 交叉校验（6/6 PASS，现含 v0.31/v0.33 consolidation）。10 net-new anchors since v0.30（v0.31–v0.33 新
> provenance 链接）。**drift_vs_v030 传递式 subsumes v0.30 自身的 drift_vs_v023**（v0.30 锚点集 ⊇ v0.23
> 锚点集），故显式 v0.23 recheck 省略无损。audit 层非整合层，不重算 RELEASE_INDEX，按 v0.30 先例推到
> 下一整合层（v0.35）再生。DETERMINISM PASS（3/3 字节一致）、leak 0。
> **v0.35 增补**：发布索引再生 + DATA_CARD addendum **§M** 整合层——见 [`bench_v0.35/`](bench_v0.35/)，
> 把 v0.34（冻结 lineage RE-sweep 构造/审计层，subsumes v0.30）纳入 RELEASE_INDEX（**34 版本 / 33 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.34「32 版本 / 77 manifest / 170 锚点 → 164 PASS + 6 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v030 104/104
> 0 回归 + 10 net-new provenance links since v0.30 全 bit-intact + frozen per-version RELEASE_INDEX copies 6/6」回写进
> v0.16 DATA_CARD addendum 作为 **§M**（记录 v0.23→v0.30→v0.34 完整性审计 cadence）。机器验证 v0.34 freeze-integrity
> （manifest PASS + audit overall_verdict PASS + 锚点计数 164/6/0/0 over 170 [118u]/77 manifest/32 版本 + drift_vs_v030 104/104
> 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 6/6 + 跨层独立重算 v0.34 输出 lineage_audit_v034.json match 其自身 manifest
> + 公共 v0.15 锚点 5dd43df6…）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.35 视图。DETERMINISM PASS（5/5 字节一致）、leak 0。
> **v0.36 增补**：meta-feature **scaling-artifact 消融**构造层——见 [`bench_v0.36/`](bench_v0.36/)，
> 诊断 v0.32 TREATMENT C 的**未解释负结果**（acc 0.3137 比 CONTROL 0.5882 还差）并**修正（不推翻）§L**
> 的「粗 meta 为负」子结论。在冻结 v0.26 split（逐位复用 v0.32）上：特征量级分析揭示 z-scored meta 块
> 占 rich 向量 norm² 的 **79.5%**（TF-IDF 块范数 1.0 vs meta 块 2.23），C 退化成 ~meta-only
> （C=0.3137 ≈ meta-only E=0.2941）；TREATMENT D（meta 块重缩放匹配 TF-IDF 范数）acc=0.5294 / TREATMENT F
> （整行 L2 归一）acc=0.5490 大幅回升 → **C 的崩溃是特征缩放伪影，非粗 meta 本质为负**；逐特征留一证无单
> 一毒性特征。**修正 §L**：粗 meta 缩放后是「温和偏负」非「戏剧性为负」；**§L 主结论不变**（B 缩 gap +0.2157
> → weak-model artifact）；§L「需语义级特征缩 gap」方向**成立**（D/F 也不缩 gap）。cross-check vs v0.32
> CONTROL/B/C 逐位复现 + v0.32 gap_shrink.json on-disk match manifest；DETERMINISM PASS（7/7 字节一致）、leak 0。
> 构造层非整合层，不重算 RELEASE_INDEX（按 v0.32 先例推到下一整合层）。
> **v0.37 增补**：发布索引再生 + DATA_CARD addendum **§N** 整合层——见 [`bench_v0.37/`](bench_v0.37/)，
> 把 v0.36（meta-feature scaling-artifact 消融构造层）纳入 RELEASE_INDEX（**36 版本 / 35 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.36「C 崩溃是特征缩放伪影（z-scored meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；
> D/F 重缩放回升到 0.5294/0.5490 但不缩 gap）→ 修正 §L「粗 meta 戏剧性为负」为「缩放后温和偏负」，
> §L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立」回写进
> v0.16 DATA_CARD addendum 作为 **§N**。机器验证 v0.36 freeze-integrity（manifest PASS + cross_check_vs_v032
> PASS [CONTROL/B/C 0.588235/0.803922/0.313725 逐位复现] + v0.32 gap_shrink.json on-disk sha match + 跨层独立重算
> v0.36 输出 meta_ablate.json match 其自身 manifest + v0.32 gap_shrink.json match v0.36 provenance + 公共 v0.15
> 锚点 5dd43df6… + v0.26 split 4 文件 match v0.36 provenance）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)
> 已再生为 v0.37 视图。DETERMINISM PASS（5/5 字节一致）、leak 0。
> **v0.38 增补**：gap-shrink **bootstrap CI** 构造层——见 [`bench_v0.38/`](bench_v0.38/)，
> 把 v0.32 的 §L/§N 核心结论（B 缩 gap +0.2157 → weak-model artifact）从**点估计**升级为**置信区间**。
> v0.32 自陈 n=51/n=42「高方差，方向可靠但 magnitude 不可靠」，v0.21 只给过 v0.15 *诊断* split 的 bootstrap CI，
> 从未给过 v0.26/v0.32 *unseen-user* gap 的 CI。本层用**配对**非参数 percentile bootstrap（10000 次，
> `numpy default_rng(seed=0)`，对 CONTROL/B/C 用同一 resample 索引向量→配对对比正确）测三个关键声明：
> (1) B 缩 gap over CONTROL：n=51 95% CI **[0.0980, 0.3529]** p=0.0005 / n=42 CI **[0.1429, 0.4048]** p=0.0
> → **显著**，§L weak-model-artifact 主轴**对重采样稳健**非小样本偶然；(2) B 残余 gap vs headline（−0.0134）：
> n=51 95% CI **[−0.1311, 0.0846]** **含 0** p=0.4478 → **统计上闭合**（B 把 gap 关到易类天花板噪声内），
> **强化** §L（gap 可被更强但仍是浅层线性模型闭合）；(3) C 崩溃 vs CONTROL（−0.2745）：n=51 95% CI
> **[−0.4118, −0.1373]** p=0.0 → **显著**，v0.36 缩放伪影诊断是**真实效应**非 n=51 错觉。cross-check vs v0.32
> 9/9 点估计 MATCH；freeze-integrity PASS（v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha
> match v0.32 manifest）；DETERMINISM PASS（字节一致）、leak 0。构造层非整合层，不重算 RELEASE_INDEX
> （按 v0.32/v0.36 先例推到下一整合层）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。
> **v0.39 增补**：发布索引再生 + DATA_CARD addendum **§O** 整合层——见 [`bench_v0.39/`](bench_v0.39/)，
> 把 v0.38（gap-shrink bootstrap CI 构造层）纳入 RELEASE_INDEX（**38 版本 / 37 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.38「§L/§N 核心结论从点估计升级为置信区间——B 缩 gap over CONTROL +0.2157 显著 [n=51 95% CI
> 0.0980,0.3529 p=0.0005 / n=42 CI 0.1429,0.4048 p=0.0] → §L weak-model-artifact 主轴对重采样稳健非小样本偶然；
> B 残余 gap vs headline −0.0134 含 0 [n=51 CI −0.1311,0.0846 p=0.4478] → 统计上闭合（关到易类天花板噪声内）→ 强化 §L；
> C 崩溃 vs CONTROL −0.2745 显著 [n=51 CI −0.4118,−0.1373 p=0.0] → v0.36 缩放伪影诊断是真实效应非 n=51 错觉 → 证实 §N；
> §L 主结论 + §N 子结论不变，二者现均 CI-backed；§L「magnitude 不可靠」caveat 退役（CI 已报告，虽宽）；
> 首个 unseen-user gap CI」回写进 v0.16 DATA_CARD addendum 作为 **§O**。机器验证 v0.38 freeze-integrity
> （manifest PASS + all_match + cross_check_vs_v032 MATCH 9/9 [rounding tolerance] + 跨层独立重算 v0.38 输出
> gap_shrink_ci.json/gap_shrink_ci_characterization.md match 其自身 manifest + 公共 v0.15 锚点 5dd43df6… +
> v0.26 split 3 文件 + v0.32 submission+gap_shrink 4 文件 match v0.38 inputs）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)
> 已再生为 v0.39 视图。DETERMINISM PASS（5/5 字节一致）、leak 0。
> **v0.40 增补**：冻结 lineage 完整性 **RE-sweep**（subsumes v0.34，构造层）——见 [`bench_v0.40/`](bench_v0.40/)，
> 闭环 v0.39 下一步候选（v0.38 产新 manifest 锚点→解锁 lineage RE-sweep，承 v0.23→v0.30→v0.34 cadence）。
> 把 v0.34 全树审计（32 版本 / 170 锚点）重跑到现已冻结的 **38 版本 / 89 manifest / 206 锚点**（135 unique，
> 197 PASS + 9 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v034 回归校验**——112/112 v0.34
> frozen 锚点仍 bit-intact（排除 6 个 v0.34 标记的顶层 living RELEASE_INDEX.md），证 v0.35–v0.39 build-out
> 未静默漂移任一冻结输入；**17 net-new anchors** since v0.34。**drift_vs_v034 传递式 subsumes v0.34 自身的
> drift_vs_v030**（v0.34 锚点集 ⊇ v0.30 锚点集 ⊇ v0.23），故显式 v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40
> 回归链全 bit-intact。frozen per-version RELEASE_INDEX copies 交叉校验 **9/9 PASS**（含 v0.35/v0.37/v0.39）。
> drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX
> （按 v0.30/v0.34 先例推到下一整合层 v0.41）；纯元数据不改冻结层（v0.1–v0.39 untouched）；DETERMINISM PASS（3/3 字节一致）、leak 0。
> **v0.41 增补**：发布索引再生 + DATA_CARD addendum **§P** 整合层——见 [`bench_v0.41/`](bench_v0.41/)，
> 把 v0.40（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.34）纳入 RELEASE_INDEX（**40 版本 / 39 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.40「38 版本 / 89 manifest / 206 锚点 [135 unique] → 197 PASS + 9 LIVING_FILE_BYDESIGN + 0 broken +
> drift_vs_v034 112/112 0 回归 + 17 net-new since v0.34 全 bit-intact + frozen per-version RELEASE_INDEX copies 9/9 +
> v0.23→v0.30→v0.34→v0.40 RE-sweep cadence」回写进 v0.16 DATA_CARD addendum 作为 **§P**——**扩展 §M 覆盖窗口**
> 从 32 版本（v0.34）到 38 版本（v0.40），不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。
> 机器验证 v0.40 freeze-integrity（manifest PASS + headline overall PASS + drift_vs_v034 112/112 0 回归 +
> drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 9/9 + 跨层独立重算 v0.40 输出 lineage_audit_v040.json match
> 其自身 manifest + v0.13 manifest 输入 + v0.34 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；顶层
> [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.41 视图。DETERMINISM PASS（5/5 字节一致）、leak 0。
> **v0.42 增补**：**per-class gap-shrink bootstrap CI** 构造层——见 [`bench_v0.42/`](bench_v0.42/)，
> 闭环 v0.38 characterization 显式留的「per-class contrasts not computed」开放问题。v0.38 给了首个
> **treatment-level**（headline）unseen-user gap CI（B 缩 gap over CONTROL 显著 [0.0980,0.3529] p=0.0005），
> v0.42 把它**定位到具体类**：per-class paired bootstrap（10000 次，`numpy default_rng(seed=0)`，within-class
> one shared resample vector，n≥MIN_CI_N=10 报 CI，n<10 仅点估计因 bootstrap 退化）。**`other`**（n=15/14）
> B−CONTROL shrink +0.667/+0.714 95% CI **[0.4,0.867]/[0.5,0.929]** p=0.0 → **两子集均显著**——这正是 v0.18/v0.32
> 识别的 `other`↔`code_dev` disputed 边界（弱最近质心崩 CTRL 0.27，softmax 修好 B 0.93-1.0），§L weak-model-artifact
> **定位到此类**。**`code_dev`**（n=27/25，最大类）shrink +0.074/+0.040 CI 含 0 ns——CTRL 已 0.89/0.96 在弱模型天花板，
> B 几无改进，是「已解决」类非 gap 源。薄类（n≤4）仅点估计（eda_virtuoso_schematic CTRL=B=0 两模型全败，源硬限）——
> 这是 v0.28/v0.32「薄类源硬限残项」的 per-class-CI 证据。**净结论**：+0.2157 headline shrink 几乎全来自 `other` 的
> 边界修复，非均匀提升；**精化（不推翻）§L/§O**——weak-model artifact 真实显著但其 locus 是 `other` disputed 边界非全类。
> 下游含义：语义级 treatment（LLM-gated）须帮 code_dev 突破弱模型天花板 + 解决薄类，而非仅重修 softmax 已修的 `other` 边界。
> 两个 freeze-integrity cross-check：vs v0.32 9/9 点估计 MATCH + vs v0.38 headline n=51 B−CONTROL CI 逐位相等
> [0.098039,0.352941]（证 v0.42 在与 v0.38 完全相同的 item 集上分区，subsumes v0.38 headline）。freeze-integrity PASS
> （v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha match v0.32 manifest）；构造层非整合层不重算
> RELEASE_INDEX（按 v0.32/v0.36/v0.38 先例推到下一整合层）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。
> DETERMINISM PASS（字节一致）、leak 0。
> **v0.43 增补**：发布索引再生 + DATA_CARD addendum **§Q** 整合层——见 [`bench_v0.43/`](bench_v0.43/)，
> 把 v0.42（per-class gap-shrink bootstrap CI 构造层）纳入 RELEASE_INDEX（**42 版本 / 41 ACTIVE / 1 SUPERSEDED**）
> + 把 v0.42「§L weak-model-artifact 定位到 `other` disputed 边界：`other` n=15/14 shrink +0.667/+0.714
> CI [0.4,0.867]/[0.5,0.929] p=0.0 两子集均显著；`code_dev` n=27/25 CI 含 0 ns＝弱模型天花板；薄类 n<10 仅点估计＝源硬限残项」
> 回写进 v0.16 DATA_CARD addendum 作为 **§Q**——**精化（不推翻）§L/§O**，把 gap-attribution cadence
> （§I→§J→§L→§N→§O→**§Q per-class**）推到 per-class 闭环。机器验证 v0.42 freeze-integrity（manifest PASS +
> cross-check vs v0.32 9/9 点估计 MATCH + cross-check vs v0.38 headline CI 逐位相等 [0.098039,0.352941] +
> 跨层独立重算 v0.42 输出 gap_shrink_perclass_ci.json/characterization.md match 其自身 manifest + 公共 v0.15 锚点 5dd43df6 +
> v0.26 split 3 + v0.32 submission 4 on-disk sha match）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.43 视图。
> 承 v0.38→v0.39 / v0.40→v0.41 构造→整合 cadence。DETERMINISM PASS（5/5 字节一致）、leak 0。
> **v0.44 增补**：冻结 lineage 完整性 **RE-sweep**（subsumes v0.40，构造层）——见 [`bench_v0.44/`](bench_v0.44/)，
> 把 v0.40 全树审计（38 版本 / 89 manifest / 206 锚点）重跑到现已冻结的 **42 版本 / 97 manifest / 228 锚点**
> （144 unique，217 PASS + 11 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v040 回归校验**——
> 126/126 v0.40 frozen 锚点仍 bit-intact（排除 9 个 v0.40 标记的顶层 living RELEASE_INDEX.md），证 v0.41–v0.43 build-out
> 未静默漂移任一冻结输入；**9 net-new anchors** since v0.40（v0.40 audit 自身 + v0.41/v0.43 consolidation outputs +
> v0.42 per-class CI outputs；v0.42 的 input 锚点已被 v0.38 manifest 声明、由 v0.40 校验，故非 net-new 而在 drift_vs_v040 重验证）。
> **drift_vs_v040 传递式 subsumes v0.40 自身的 drift_vs_v034**（v0.40 锚点集 ⊇ v0.34 锚点集 ⊇ v0.30 ⊇ v0.23），故显式
> v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→**v0.44** RE-sweep cadence。frozen per-version
> RELEASE_INDEX copies 交叉校验 **11/11 PASS**（现含 v0.41/v0.43 consolidation）。drift vs v0.13 PASS 73/73。公共 v0.15
> 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40 先例推到下一整合层，
> 承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence）；纯元数据不改冻结层（v0.1–v0.43 untouched）；
> 产新 manifest 锚点（lineage_audit_v044.json sha256）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.44 后解锁；
> DETERMINISM PASS（3/3 字节一致）、leak 0。
> **v0.45 增补**：发布索引再生 + DATA_CARD addendum **§R** 整合层——见 [`bench_v0.45/`](bench_v0.45/)，
> 把 v0.44（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.40——5th whole-tree audit）纳入下一整合层再生
> RELEASE_INDEX（v0.44 明确推到下一整合层，承 v0.30/v0.34/v0.40 审计层先例 + v0.38→v0.39 / v0.40→v0.41 /
> v0.42→v0.43 构造→整合 cadence）+ 把 v0.44「42 版本 / 97 manifest / 228 锚点 [144 unique] → 217 PASS +
> 11 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v040 126/126 0 回归 + 9 net-new since v0.40 全 bit-intact +
> frozen per-version RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44 RE-sweep cadence」回写进
> v0.16 DATA_CARD addendum 作为 **§R**——**扩展 §P 覆盖窗口**从 38 版本（v0.40）到 42 版本（v0.44），
> 不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.44 freeze-integrity
> （manifest PASS + audit overall PASS + headline 计数 42/97/228/144/217/11/0/0 + drift_vs_v040 126/126 0 回归 +
> drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.44 输出 lineage_audit_v044.json match
> 其自身 manifest + v0.13 manifest 输入 + v0.40 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；
> **44 版本 / 43 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.44 untouched）；
> DETERMINISM PASS（5/5 字节一致）、leak 0；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.45 视图。
> **v0.46 增补**：冻结 lineage 完整性 RE-sweep 构造层——见 [`bench_v0.46/`](bench_v0.46/)，
> subsumes v0.44（传递式 v0.40/v0.34/v0.30/v0.23）——把 v0.44 全树审计（42 版本 / 97 manifest / 228 锚点）
> 重跑到现已冻结的 **44 版本 / 101 manifest / 231 锚点**（145 unique，220 PASS + 11 LIVING_FILE_BYDESIGN，
> 0 MISMATCH/MISSING）。新增 **drift_vs_v044 回归校验**——133/133 v0.44 frozen 锚点仍 bit-intact
> （排除 11 个 v0.44 标记的顶层 living RELEASE_INDEX.md），证 v0.45 build-out 未静默漂移任一冻结输入；
> **1 net-new anchor** since v0.44（v0.44 自身 lineage_audit_v044.json 输出，v0.44 扫描时作 OWN_OUT_REL 排除，
> 现为冻结输入；v0.45 manifest 的 sha 链接均在 integrity/provenance 段非 anchor schema → 0 可验证锚点）。
> **drift_vs_v044 传递式 subsumes v0.44 自身的 drift_vs_v040**（v0.44 锚点集 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），
> 故显式 v0.40/v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→v0.44→**v0.46** RE-sweep cadence
> 第 6 次全树审计。frozen per-version RELEASE_INDEX copies 交叉校验 **11/11 PASS**（v0.45 consolidation 无 outputs
> key 故不计入，其 frozen 副本仍由 full_tree_manifest 覆盖）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点
> 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40/v0.44 先例推到下一整合层，
> 承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 / v0.44→v0.45 构造→整合 cadence）；纯元数据不改冻结层（v0.1–v0.45 untouched）；
> 产新 manifest 锚点（lineage_audit_v046.json sha256 `33e881a3…`）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.46 后解锁；
> DETERMINISM PASS（3/3 字节一致）、leak 0。
> **v0.47 增补**：发布索引再生 + DATA_CARD addendum **§S** 整合层——见 [`bench_v0.47/`](bench_v0.47/)，
> 在单一整合步骤中吸收 v0.46（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.44——6th whole-tree audit）：
> 把 v0.46 纳入 RELEASE_INDEX（46 版本 / 45 ACTIVE / 1 SUPERSEDED）+ 把 v0.46「44 版本 / 101 manifest / 231 锚点
> [145 unique] → 220 PASS + 11 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v044 133/133 0 回归 + 1 net-new since v0.44 +
> frozen per-version RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 RE-sweep cadence 第 6 次全树审计」
> 回写进 v0.16 DATA_CARD addendum 作为 **§S**——**扩展 §R 覆盖窗口**从 42 版本（v0.44）到 44 版本（v0.46），
> 不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.46 freeze-integrity
> （manifest PASS + audit overall PASS + headline 计数 44/101/231/145/220/11/0/0 + drift_vs_v044 133/133 0 回归 +
> drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.46 输出 lineage_audit_v046.json match
> 其自身 manifest + v0.13 manifest 输入 + v0.44 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；
> **46 版本 / 45 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.46 untouched）；
> DETERMINISM PASS（5/5 字节一致）、leak 0；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.47 视图。
> **v0.48 增补**：冻结 lineage 完整性 RE-sweep 构造层——见 [`bench_v0.48/`](bench_v0.48/)，
> subsumes v0.46（传递式 v0.44/v0.40/v0.34/v0.30/v0.23——**7th whole-tree audit**）：把 v0.46 全树审计
> （44 版本 / 101 manifest / 231 锚点）重跑到现已冻结的 **46 版本 / 105 manifest / 234 锚点**
> （146 unique，223 PASS + 11 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v046 回归校验**——
> 134/134 v0.46 frozen 锚点仍 bit-intact（排除 11 个 v0.46 标记的顶层 living RELEASE_INDEX.md），证 v0.47 build-out
> 未静默漂移任一冻结输入；**1 net-new anchor** since v0.46（v0.46 自身 lineage_audit_v046.json 输出，v0.46 扫描时作
> OWN_OUT_REL 排除，现为冻结输入；v0.47 manifest 的 sha 链接均在 integrity/provenance 段非 anchor schema → 0 可验证锚点）。
> **drift_vs_v046 传递式 subsumes v0.46 自身的 drift_vs_v044**（v0.46 锚点集 ⊇ v0.44 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），
> 故显式 v0.44/v0.40/v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→**v0.48** RE-sweep cadence
> 第 7 次全树审计。frozen per-version RELEASE_INDEX copies 交叉校验 **11/11 PASS**（v0.45/v0.47 consolidation 无 outputs key
> 故不计入）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX
> （按 v0.30/v0.34/v0.40/v0.44/v0.46 先例推到下一整合层，承 v0.44→v0.45 / v0.46→v0.47 构造→整合 cadence）；
> 纯元数据不改冻结层（v0.1–v0.47 untouched）；产新 manifest 锚点（lineage_audit_v048.json sha256 `08553f86…`）→下一全树 lineage
> RE-sweep 在下一整合层吸收 v0.48 后解锁；DETERMINISM PASS（3/3 字节一致）；leak 0。
> **v0.49 增补**：发布索引再生 + DATA_CARD addendum **§T** 整合层——见 [`bench_v0.49/`](bench_v0.49/)，
> 闭环 v0.48 下一步候选（v0.48 明确推到下一整合层，承 v0.30/v0.34/v0.40/v0.44/v0.46 审计层先例 + v0.46→v0.47
> 构造→整合 cadence）：把 v0.48（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.46——7th whole-tree audit）
> 纳入 RELEASE_INDEX 再生 + 把 v0.48「46 版本 / 105 manifest / 234 锚点 [146 unique] → 223 PASS + 11
> LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v046 134/134 0 回归 + 1 net-new since v0.46 + frozen per-version
> RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→v0.48 RE-sweep cadence 第 7 次全树审计」
> 回写进 v0.16 DATA_CARD addendum 作为 **§T**——**扩展 §S 覆盖窗口**从 44 版本（v0.46）到 46 版本（v0.48），
> 不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.48 freeze-integrity（manifest PASS
> + audit overall PASS + headline 计数 46/105/234/146/223/11/0/0 + drift_vs_v046 134/134 0 回归 + drift_vs_v013
> 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.48 输出 lineage_audit_v048.json match 其自身
> manifest + v0.13 manifest 输入 + v0.46 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；**48 版本 / 47 ACTIVE
> / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.48 untouched）；顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)
> 已再生为 v0.49 视图；
> DETERMINISM PASS（5/5 字节一致）、leak 0。

---

## 资产盘点（三个口径数字 · 第47轮现查 2026-10-29）

| 口径 | 数值 | 说明 |
|---|---|---|
| 目标机 | **1** | 本机 `hfeg0tedaap02` (10.251.36.15)，只读扫描 `/home/*/.cline/data/sessions/` |
| cline 用户目录 | **20** | 拥有 `.cline/data/sessions/` 的目录数（19 有数据 + 1 空目录） |
| 会话轨迹 | **3487** session dirs / **3479** `*.messages.json` | 与冻结快照 `a1cd058a…` 完全对齐，0 漂移（冻结快照内为 2258 任务） |

> ⚠️ 任务书假设的"经 8092 MCP → `.75` → SSH 内网"链路**仍不通**：8092 MCP 实为
> `RESEARCH-MCP-SERVER`（仅 web search/fetch/vqa/image，无命令执行）；`.75` 第50轮 ping 0% loss
> 但 SSH `Permission denied`（连续 50 轮，已上报待运维决断）。本机自身即目标 EDA 服务器，
> 满足构建需求；多机扇出在授权前阻塞，单机脱敏集不阻塞演进。
> （第17轮曾现负向漂移 19/18/3478，第18–34轮已恢复回 20/19/3487——证实为 transient，
> 冻结快照 `a1cd058a…` 仍有效。第33轮用与 extract.py 一致的只读逻辑复核 session-dir 计数=3487，
> 与冻结快照逐位对齐；早期 `find /home -name '*.messages.json'` 的 5101 是把 sessions 路径之外的
> 非 canonical `.messages.json` 算进来的计数伪影。）

---

## 推荐入口（按角色）

| 你是… | 先看这里 | 一条命令跑通 |
|---|---|---|
| **评估者**（想拿数据测自己的分类器） | [`bench_v0.10/`](bench_v0.10/) (v1.0-rc1 数据集) + [`bench_v0.9/`](bench_v0.9/) (`eval_submission.py`) | `cd bench_v0.11 && bash run_example.sh` |
| **复现者**（想逐比特复现全链路） | [`bench_v0.7/`](bench_v0.7/) (逐比特可复现性) + [`bench_v0.8/`](bench_v0.8/) (跨主机可复现性) | `cd bench_v0.7 && bash reproduce.sh` |
| **扩展者**（想扩增样本/加标注者） | [`bench_v0.1/`](bench_v0.1/) (`RESCAN=1` 扩增路径) + [`bench_v0.5/`](bench_v0.5/) (`--llm` 第3标注者) | `RESCAN=1 bash bench_v0.1/reproduce.sh` |
| **发布审查者** | [`bench_v0.10/out/RELEASE_CHECKLIST.md`](bench_v0.10/out/RELEASE_CHECKLIST.md) + [`bench_v0.10/out/DATA_CARD.md`](bench_v0.10/out/DATA_CARD.md) | — |

---

## 版本索引（v0.1 → v0.49）

每一行 = 一个版本目录；点链接进各自 README 看细节。状态/弃用维度见
[`RELEASE_INDEX.md`](RELEASE_INDEX.md)（v0.49 整合层再生，机器可验证；含 v0.48 freeze-integrity 校验；v0.48/v0.49 已纳入索引；48 版本 / 47 ACTIVE / 1 SUPERSEDED）。

| 版本 | 角色 | 关键产物 | 一句话 |
|---|---|---|---|
| [v0.1](bench_v0.1/README.md) | 资产盘点 + 脱敏基线 | `tasks.jsonl` (2258, sha256=`a1cd058a…`) | 探明本机即目标，脱敏 + 五维评分 + HTML |
| [v0.2](bench_v0.2/README.md) | 细化分类 + TF-IDF 聚类 | `clusters.json` | 兜底桶 837→384；暴露残留人名 → scrub 修复 |
| [v0.3](bench_v0.3/README.md) | 人工策展 + 监督基线 | `supervised_metrics.json` | 5-fold CV acc=0.825；CJK bigram 分词修复盲区 |
| [v0.4](bench_v0.4/README.md) | LLM-judge 标注层 | `judge_prompt_template.txt` | rule/llm 双后端；揭示 `code_dev` 标签噪声 |
| [v0.5](bench_v0.5/README.md) | 多标注者共识 gold | `gold.jsonl` / `splits.jsonl` | 2-annotator consensus + 可插拔第3 LLM 2-of-3 |
| [v0.6](bench_v0.6/README.md) | session_id 去重 + global_id | `tasks_v6.jsonl` (2112, 0 重复) | 折叠 146 跨用户 dup；修服务密码/服务账号 PII 泄漏 |
| [v0.7](bench_v0.7/README.md) | 逐比特可复现性 | `repro_verdict.json` (PASS 78/78) | 修 4× `datetime.now()` + `PYTHONHASHSEED=0` |
| [v0.8](bench_v0.8/README.md) | 源快照冻结 + 跨主机 | `cross_time_verdict.json` (PASS 40/40) | freeze-by-default；零 `/home` 访问仍逐比特一致 |
| [v0.9](bench_v0.9/README.md) | 规范发布 bundle | `tasks/gold/few_shot/test_set` + manifest | 第三方提交评估器；split-integrity guard |
| [v0.10](bench_v0.10/README.md) | v1.0-rc1 发布候选 | `DATA_CARD/LICENSE/CITATION/BASELINE` | 内部可发布 `internal_shippable=True` |
| [v0.11](bench_v0.11/README.md) | worked example 提交演示 | `example_submission.jsonl` | few-shot 训练→预测→打分 acc=0.817 闭环 |
| **v0.12** | **统一入口（本文件）** | `designflow/README.md` | 聚合 11 版本为可导航整体 |
| [v0.13](bench_v0.13/README.md) | 版本演进 diff 层 | `version_diff.json` / `version_manifest.json` | 脚本算出相邻版本 artifact added/removed/sha-changed 表 |
| [v0.14](bench_v0.14/README.md) | 统计严谨性层 | `agreement.json` / `selection_bias.json` / `bootstrap_ci.json` | Cohen's κ=0.45；test_set 0/219 disputed→选择偏倚；bootstrap 95% CI acc[0.767,0.868] |
| **v0.15** | **去偏 test split + 双标注者评分** | `debiased_test_set.jsonl` (368) / `debiased_eval.json` / `bias_correction.json` | 闭环 v0.14 BIAS_PRESENT：disputed 分率 0.0→0.405=语料；consensus acc 0.817 vs disputed robustness 0.309 |
| **v0.16** | **DATA_CARD 增补层（统计有效性 addendum）** | `DATA_CARD_ADDENDUM.md` / `datacard_enrich.json` | 不改冻结 v0.10 DATA_CARD，层叠 v0.14/v0.15 统计证据（κ/bias/CI/去偏）+ 字段级 provenance |
| **v0.17** | **诊断发布 bundle（去偏 split 可对外打包）** ⚠️ SUPERSEDED by v0.19 | `diagnostic_test_set.jsonl` (368) / `diagnostic_release_manifest.json` / `eval_diagnostic.py` | 闭环 v0.15/v0.16：把去偏 split 从散件打包为可对外发布的诊断 bundle + 双标注者第三方评估接口。**v0.20 判定被 v0.19 超集替代**（test_set 含标签非严格 blinded、无 characterization）；保留作 provenance，新评测请用 v0.19 |
| **v0.18** | **disputed 项机理性刻画** | `dispute_analysis.json` / `dispute_characterization.md` | 闭环 v0.15/v0.16/v0.17：解释 +0.51 gap 的机理——code_dev↔other↔noise 边界模糊、disputed 项 prompt 更短(d=−0.33)、top-3 用户占 54.4% |
| **v0.19** | **诊断 split 自包含发布包（v0.17 bundle + v0.18 characterization 融合）** | `diagnostic_test_set.jsonl`(blinded) / `diagnostic_answers.jsonl`(key) / `diagnostic_eval.py` / `diagnostic_characterization.md` / `report_v19.html` | 闭环候选(4)：把 v0.18 机理性结论并入诊断 split；blinded/answer-key 分离 + 独立 CLI 评估器；自检 baseline 复现 v0.15 (acc0.8174/rob0.3087/gap+0.5086)；DETERMINISM PASS；不改冻结层。**规范诊断发布** |
| **v0.20** | **发布整合 / 弃用层（顶层 RELEASE_INDEX）** | `RELEASE_INDEX.md` / `deprecation_map.json` / `release_index.json` / `report_v20.html` | 闭环 v0.19 下一步候选(4)：机器验证 v0.17→v0.19 超集关系（5 项完整性全过）+ 标 v0.17 SUPERSEDED + 顶层 `designflow/RELEASE_INDEX.md` 给外部消费者一张版本状态图；纯元数据，不改冻结层；DETERMINISM PASS |
| **v0.21** | **诊断 split bootstrap CI + gap 显著性层** | `diagnostic_ci.json` / `diagnostic_ci_manifest.json` / `report_v21.html` | 闭环 v0.19 headline 只有点估计无 CI：对规范诊断 split 的 gap(+0.5086)/robustness(0.3087) 加分层 bootstrap 95% CI + one-sided 显著性检验。gap CI [0.445,0.573] 排除 0 → 统计显著（p=0.0）；consensus acc CI 复现 v0.14 [0.767,0.868] 互证；CROSS-CHECK vs v0.15 6/6 MATCH；不改冻结层 |
| **v0.22** | **发布索引再生 + DATA_CARD addendum §G（整合层）** | `release_index_v0.22.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.22.md` / `report_v22.html` | 闭环 v0.21 下一步候选：把 v0.21 纳入 RELEASE_INDEX 再生（v0.21 明确推到下一整合层）+ 把 v0.21 CI 回写进 v0.16 DATA_CARD addendum 作为 §G（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.21 freeze-integrity（sha256 match + cross_check 6/6 + gap CI 排除 0）；纯元数据，不改冻结层；DETERMINISM PASS |
| **v0.23** | **冻结 lineage 完整性全扫层** | `lineage_audit.json` / `lineage_audit_manifest.json` / `report_v23.html` | 闭环 v0.22 单锚点缺口：把 v0.22 只验 1 个锚点（v0.15 debiased_test_set）推广为全树穷举——扫所有 `bench_v0.*/out/*.json` manifest，提取每个声明 (path, sha256) 锚点，对盘上文件逐个校验。124 锚点全 PASS（95 unique 路径），drift vs v0.13 PASS 73/73；lineage 图 8 版本声明的输入全 bit-intact；零 /home 零 LLM；DETERMINISM PASS。v0.23 为审计层非整合层，按 v0.21 先例把 RELEASE_INDEX 再生推到下一整合层 |
| **v0.24** | **发布索引再生 + DATA_CARD addendum §H（整合层）** | `release_index_v0.24.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.24.md` / `report_v24.html` | 闭环 v0.23 下一步候选：把 v0.23 纳入 RELEASE_INDEX 再生（v0.23 明确推到下一整合层，承 v0.21 审计层先例）+ 把 v0.23 全树完整性审计回写进 v0.16 DATA_CARD addendum 作为 §H（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.23 freeze-integrity（overall PASS + 124 锚点全 PASS + drift 73/73 + v0.22 单锚点 5dd43df6… 在 v0.23 穷举列表里再验证 PASS → subsumes v0.22）；23 版本 / 22 ACTIVE / 1 SUPERSEDED；纯元数据，不改冻结层；DETERMINISM PASS |
| **v0.25** | **per-user 公平性审计层** | `fairness_audit.json` / `fairness_characterization.md` / `report_v25.html` | 闭环 v0.18「disputed 用户集中 → 指向 per-user 公平性审计」v1.x 路径 + v0.16 §E 定性局限量化。读冻结 v0.15 debiased split + baseline + v0.6 tasks，测 accuracy 在用户维度的稳健性。consensus 块 11 用户 Gini=0.5654/HHI=0.1951（2.14× 集中），top-3 占 70.3%；**LOUO \|Δ\|max=0.0486 < 0.05 → headline accuracy IS user-robust**（非单用户伪迹）；**但 8/9 类 ≥0.5 单用户垄断**（3/9 ==1.0）→ per-class 尾类 P/R/F1 实质是 per-user metric。disputed 块 13 用户 top-3=54.4% 复现 v0.18。CROSS-CHECK vs v0.15 6/6 MATCH；audit 层非整合层，不重算 RELEASE_INDEX |
| **v0.26** | **user-stratified re-split 构造层** | `user_resplit.json` / `resplit_characterization.md` / `user_strat_train.jsonl`(168) / `user_strat_test.jsonl`(51,blinded) / `user_strat_answers.jsonl` / `user_strat_submission.jsonl` / `report_v26.html` | 闭环 v0.25 下一步候选：据 v0.25 per-class 单用户垄断构造 user-stratified re-split [v1.x 构造候选]。对冻结 v0.15 共识 219 项按用户分层重切——每类主用户进 train，其余用户进 held-out test，测 baseline 对**未见该标签的用户**的泛化。**user-strat acc=0.5882 vs headline 0.8174 → gap=−0.2291**——证实存在 headline 掩盖的未见用户泛化缺口（other 0.267 / eda_virtuoso_schematic 0.0 不迁移；code_dev 0.889 迁移好）；3 类 IMPOSSIBLE 单用户类（eda_innovus 14/eda_timing_power 2/eda_drc_lvs 1，共 17 项）无法分层（源硬限，仅更多用户/机器可解）。FREEZE-INTEGRITY PASS（v0.15 anchor 5dd43df6…）；CROSS-CHECK vs v0.15 PASS；构造层非整合层，不重算 RELEASE_INDEX（按 v0.21/v0.23/v0.25 先例推到下一整合层）；DETERMINISM PASS；leak 0 |
| **v0.27** | **发布索引再生 + DATA_CARD addendum §I（整合层）** | `release_index_v0.27.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.27.md` / `consolidation_report_v0.27.json` / `report_v27.html` | 闭环 v0.26 下一步候选：把 v0.25+v0.26 纳入下一整合层再生 RELEASE_INDEX（两层都明确推到下一整合层，承 v0.21/v0.23 审计/构造层先例）+ 把 v0.25「headline user-robust 但 per-class 单用户垄断」+ v0.26「未见用户泛化 gap=−0.2291」回写进 v0.16 DATA_CARD addendum 作为 §I（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.25 freeze-integrity（4 锚点全 match disk + cross_check MATCH）+ v0.26 freeze-integrity（status PASS + cross_check PASS）+ 公共 v0.15 锚点 5dd43df6… 跨层独立重算一致；26 版本 / 25 ACTIVE / 1 SUPERSEDED；纯元数据，不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.28** | **user-balanced re-split 构造层（v1.x 候选）** | `user_balance.json` / `balance_characterization.md` / `core_train_S.jsonl`(177) / `core_train_M.jsonl`(177,matched) / `core_test.jsonl`(17,blinded) / `core_answers.jsonl` / `core_submission_S.jsonl` / `core_submission_M.jsonl` / `report_v28.html` | 闭环 v0.26 下一步候选：据 gap=−0.2291 构造 user-balanced re-split [强制每类多用户，扔掉 IMPOSSIBLE 单用户类] 作 v1.x 候选。新增**多用户 train**（top-2 用户/类，v0.26→v0.28 增量）+ 严格资格规则（≥3 用户且 top-2 之外项数 ≥2）：**仅 2/9 类合格**（code_dev/other）——诚实源硬限（7 类不可：3 IMPOSSIBLE + 4 薄类 top-2 外 <2 项）。受控实验固定 17 项未见用户 core test，对比 TRAIN-S（单用户/类，v0.26 式）vs TRAIN-M（2 用户/类，**matched count 177==177，唯一差异是 52 core train 项来自 1 vs 2 用户**）→ **dZ_matched=−0.1176，多用户 train 反而更差**：证伪「收集更多用户即可缩小 gap」的乐观假设，gap 是该特征空间下标签识别的内禀难度。次要 TRAIN-M-all（202 项，混淆规模）dZ_all=−0.0588 仍不优于 S。阈值扫描表量化源代价。FREEZE-INTEGRITY PASS（v0.15 anchor 5dd43df6…）；CROSS-CHECK vs v0.15 PASS；MATCHED-COUNT INVARIANT PASS；构造层非整合层，不重算 RELEASE_INDEX（按 v0.21/v0.23/v0.25/v0.26 先例推到下一整合层）；DETERMINISM PASS（10/10 字节一致）；leak 0 |
| **v0.29** | **发布索引再生 + DATA_CARD addendum §J（整合层）** | `release_index_v0.29.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.29.md` / `consolidation_report_v0.29.json` / `report_v29.html` | 闭环 v0.28 下一步候选：把 v0.28 纳入下一整合层再生 RELEASE_INDEX（v0.28 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26 构造层先例）+ 把 v0.28「2/9 类 Tier-A + dZ=−0.1176 多用户 train 反而更差 → 证伪『多用户即缩 gap』，gap 是特征空间内禀难度」回写进 v0.16 DATA_CARD addendum 作为 §J（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.28 freeze-integrity（status PASS + cross_check vs v0.15 PASS + 公共 v0.15 锚点 5dd43df6… 跨层独立重算 + 2 provenance 锚点 [v0.15 debiased_eval + v0.26 user_resplit] match disk）；28 版本 / 27 ACTIVE / 1 SUPERSEDED；纯元数据，不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.30** | **冻结 lineage 完整性 RE-sweep（subsumes v0.23）** | `lineage_audit_v030.json` / `lineage_audit_manifest.json` / `report_v30.html` | 闭环 v0.23 下一步候选（全树 lineage 再扫纳入 v0.28/v0.29 锚点，subsumes v0.23）：把 v0.23 全树审计（21 版本 / 124 锚点）重跑到现已冻结的 **28 版本 / 69 manifest / 151 锚点**（108 unique，147 PASS + 4 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v023 回归校验**——94/94 v0.23 frozen 锚点仍 bit-intact（排除 1 个 v0.23 误验的顶层 living RELEASE_INDEX.md），证 v0.24–v0.29 build-out 未静默漂移任一冻结输入；13 net-new anchors since v0.23（v0.24/v0.25/v0.26/v0.28/v0.29 新 provenance 链接）。**发现并建模 v0.23 latent bug**：v0.23 把 consolidation 报告的 `outputs[].RELEASE_INDEX.md`（bare name）解析到顶层 living 文件（按设计被各整合层覆盖），仅因 v0.23 时刻顶层 == v0.22 冻结副本而巧合 PASS；v0.30 把 living 文件正确标为 LIVING_FILE_BYDESIGN，并加 **frozen per-version RELEASE_INDEX copies 交叉校验**（4/4 PASS，真冻结的是各 `bench_v0.XX/out/RELEASE_INDEX.md`）。drift vs v0.13 PASS 73/73。audit 层非整合层，不重算 RELEASE_INDEX（按 v0.21/v0.23 先例推到下一整合层）；纯元数据不改冻结层；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.31** | **发布索引再生 + DATA_CARD addendum §K（整合层）** | `release_index_v0.31.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.31.md` / `consolidation_report_v0.31.json` / `report_v31.html` | 闭环 v0.30 下一步候选：把 v0.30 纳入下一整合层再生 RELEASE_INDEX（v0.30 明确推到下一整合层，承 v0.21/v0.23 审计层先例）+ 把 v0.30「冻结 lineage RE-sweep subsumes v0.23 + 建模 v0.23 latent living-file bug」回写进 v0.16 DATA_CARD addendum 作为 §K（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.30 freeze-integrity（overall PASS + 147 PASS + 4 LIVING == 151 [0 mismatch/missing] + drift_vs_v013 PASS 73/73 + drift_vs_v023 PASS 94/94 [0 regression, 13 net-new] + frozen_release_index_copies PASS 4/4 + 公共 v0.15 锚点 5dd43df6… 在 v0.30 穷举列表里再验证 PASS → subsumes v0.29 + 跨层独立重算 v0.15 锚点 / v0.30 输出 / v0.23 基线 3 项全 match disk）；30 版本 / 29 ACTIVE / 1 SUPERSEDED；纯元数据不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.32** | **stronger-model gap-shrink 构造层（v1.x 候选）** | `gap_shrink.json` / `gap_shrink_characterization.md` / `sub_control_nearestcentroid.jsonl` / `sub_softmax_tfidf.jsonl` / `sub_softmax_rich.jsonl` / `gap_shrink_manifest.json` / `report_v32.html` | 闭环 v0.28 **命名但未测试**的开放结论「缩 v0.26 unseen-user gap=−0.2291 需更强模型/更富特征」。在**冻结 v0.26 split 逐位复用**（168 train / 51 test，受控对比——唯一变量是模型/特征）上：CONTROL 重跑 v0.11 nearest-centroid 复现 0.588235 ✅；TREATMENT B 把最近心换成 multinomial softmax 回归（**同** TF-IDF+tools 特征）→ acc=**0.8039** gap=**−0.0134** shrink=**+0.2157**（几乎**闭合** gap！fully-unseen n=42 acc 0.667→0.929）；TREATMENT C 加标准化 meta 特征（长度/token/工具数/has-chinese）→ acc=0.3137 反而**扩大** gap（meta 编码用户风格非标签语义）。**结论修订 v0.28**：gap 主要不是「特征空间内禀难度」而是 **weak-model（最近质心）artifact**——同特征上换成线性判别模型即缩 +0.216；「更富特征」药方在此为**负**（粗 meta 伤跨用户泛化）。per-class：B 修好 v0.18 记录的 other↔code_dev disputed 边界（other 0.267→0.933），薄类 eda_virtuoso_schematic/eda_aether_layout 仍 0（v0.26 已标不迁移）。构造层非整合层不重算 RELEASE_INDEX（承 v0.26/v0.28 先例推到下一整合层）；不改冻结 v0.1–v0.31 out/；DETERMINISM PASS（7/7 字节一致，zero-init softmax 无 RNG + 单线程 BLAS）；FREEZE-INTEGRITY PASS（v0.15 锚点 5dd43df6… + v0.26 split 文件 match manifest）；cross-check vs v0.26 PASS（control 复现 0.588235）；leak 0 |
| **v0.33** | **发布索引再生 + DATA_CARD addendum §L（整合层）** | `release_index_v0.33.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.33.md` / `consolidation_report_v0.33.json` / `report_v33.html` | 闭环 v0.32 下一步候选：把 v0.32 纳入下一整合层再生 RELEASE_INDEX（v0.32 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28 构造层先例）+ 把 v0.32「同特征换 softmax 缩 gap +0.2157 几乎闭合 → gap 是 weak-model artifact 非内禀难度」回写进 v0.16 DATA_CARD addendum 作为 **§L**——**修订 v0.28 §J 的「内禀难度」定性**为「weak-model artifact 主项 + 薄类源硬限残项」（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.32 freeze-integrity（manifest PASS + v0.15 锚点 5dd43df6… + v0.26 split 逐位复用 + CONTROL 复现 0.588235 + 3 个 split 文件 matches_v026_manifest + 4 个 v0.26 split 文件跨层独立重算 match v0.32 声明 AND v0.26 自身 manifest + v0.32 输出 gap_shrink.json match disk + gap_shrink.json self-agrees manifest）；**32 版本 / 31 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.34** | **冻结 lineage 完整性 RE-sweep（subsumes v0.30）** | `lineage_audit_v034.json` / `lineage_audit_manifest.json` / `report_v34.html` | 闭环 v0.30 下一步候选（全树 lineage 再扫纳入 v0.31/v0.32/v0.33 锚点，subsumes v0.30）：把 v0.30 全树审计（28 版本 / 151 锚点）重跑到现已冻结的 **32 版本 / 77 manifest / 170 锚点**（118 unique，164 PASS + 6 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v030 回归校验**——104/104 v0.30 frozen 锚点仍 bit-intact（排除 4 个 v0.30 标记的顶层 living RELEASE_INDEX.md），证 v0.31–v0.33 build-out 未静默漂移任一冻结输入；10 net-new anchors since v0.30（v0.31/v0.32/v0.33 新 provenance 链接：v0.32→v0.26 split files，v0.31/v0.33 consolidation→各自 outputs）。**drift_vs_v030 传递式 subsumes v0.30 自身的 drift_vs_v023**（v0.30 锚点集 ⊇ v0.23 锚点集），故显式 v0.23 recheck 省略无损。frozen per-version RELEASE_INDEX copies 交叉校验 **6/6 PASS**（现含 v0.31/v0.33 consolidation）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。audit 层非整合层，不重算 RELEASE_INDEX（按 v0.30 先例推到下一整合层 v0.35）；纯元数据不改冻结层；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.35** | **发布索引再生 + DATA_CARD addendum §M（整合层）** | `release_index_v0.35.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.35.md` / `consolidation_report_v0.35.json` / `report_v35.html` | 闭环 v0.34 下一步候选：把 v0.34 纳入下一整合层再生 RELEASE_INDEX（v0.34 明确推到下一整合层，承 v0.21/v0.23/v0.30 审计层先例）+ 把 v0.34「32 版本 / 77 manifest / 170 锚点 → 164 PASS + 6 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v030 104/104 0 回归 + 10 net-new provenance links since v0.30 全 bit-intact + frozen per-version RELEASE_INDEX copies 6/6」回写进 v0.16 DATA_CARD addendum 作为 **§M**（记录 v0.23→v0.30→v0.34 完整性审计 cadence；§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.34 freeze-integrity（manifest PASS + audit overall_verdict PASS + 锚点计数 164/6/0/0 over 170 [118u]/77 manifest/32 版本 + drift_vs_v030 104/104 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 6/6 + 跨层独立重算 v0.34 输出 lineage_audit_v034.json match 其自身 manifest + 公共 v0.15 锚点 5dd43df6…）；**34 版本 / 33 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.36** | **meta-feature scaling-artifact 消融（构造层）** | `meta_ablate.json` / `meta_ablate_characterization.md` / `sub_softmax_metaonly.jsonl` / `sub_softmax_meta_rescaled.jsonl` / `sub_softmax_rich_rownormalized.jsonl` / `meta_ablate_manifest.json` / `report_v36.html` | 诊断 v0.32 TREATMENT C 的**未解释负结果**（acc 0.3137 比 CONTROL 0.5882 还差）并**修正（不推翻）§L**「粗 meta 为负」子结论。冻结 v0.26 split 逐位复用 v0.32，cross-check CONTROL/B/C 逐位复现 + v0.32 gap_shrink.json on-disk match manifest。特征量级分析：z-scored meta 块占 rich 向量 norm² **79.5%**（TF-IDF 范数 1.0 vs meta 2.23）→ C 退化成 ~meta-only（C=0.3137 ≈ meta-only E=0.2941）。TREATMENT D（meta 块重缩放匹配 TF-IDF 范数）acc=0.5294 / TREATMENT F（整行 L2 归一）acc=0.5490 大幅回升 → **C 崩溃是特征缩放伪影非粗 meta 本质为负**；逐特征留一证无单一毒性特征。**修正 §L**：粗 meta 缩放后「温和偏负」非「戏剧性为负」；**§L 主结论不变**（B 缩 gap +0.2157 → weak-model artifact）；§L「需语义级特征缩 gap」方向**成立**（D/F 也不缩 gap）。构造层非整合层不重算 RELEASE_INDEX（按 v0.32 先例推到下一整合层）；DETERMINISM PASS（7/7 字节一致）；leak 0 |
| **v0.37** | **发布索引再生 + DATA_CARD addendum §N（整合层）** | `release_index_v0.37.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.37.md` / `consolidation_report_v0.37.json` / `report_v37.html` | 闭环 v0.36 下一步候选：把 v0.36（meta-feature scaling-artifact 消融构造层）纳入下一整合层再生 RELEASE_INDEX（v0.36 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32 构造层先例）+ 把 v0.36「C 崩溃是特征缩放伪影（z-scored meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；D 重缩放 acc 0.5294 / F 整行归一 acc 0.5490 回升但不缩 gap）→ 修正 §L「粗 meta 戏剧性为负」为「缩放后温和偏负」，§L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立」回写进 v0.16 DATA_CARD addendum 作为 **§N**（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.36 freeze-integrity（manifest PASS + cross_check_vs_v032 PASS [CONTROL/B/C 0.588235/0.803922/0.313725 逐位复现] + v0.32 gap_shrink.json on-disk sha match + 跨层独立重算 v0.36 输出 meta_ablate.json match 其自身 manifest + v0.32 gap_shrink.json match v0.36 provenance + 公共 v0.15 锚点 5dd43df6… + v0.26 split 4 文件 match v0.36 provenance）；**36 版本 / 35 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.38** | **gap-shrink bootstrap CI（构造层）** | `gap_shrink_ci.json` / `gap_shrink_ci_characterization.md` / `gap_shrink_ci_manifest.json` / `report_v38.html` | 把 v0.32 的 §L/§N 核心结论（B 缩 gap +0.2157 → weak-model artifact）从**点估计**升级为**置信区间**——v0.32 自陈 n=51/n=42「高方差，方向可靠但 magnitude 不可靠」，v0.21 只给过 v0.15 *诊断* split 的 bootstrap CI，从未给过 v0.26/v0.32 *unseen-user* gap 的 CI。**配对**非参数 percentile bootstrap（10000 次，`numpy default_rng(seed=0)`，对 CONTROL/B/C 用同一 resample 索引向量→配对对比正确）：(1) B 缩 gap over CONTROL n=51 95% CI **[0.0980,0.3529]** p=0.0005 / n=42 CI **[0.1429,0.4048]** p=0.0 → **显著**，§L weak-model-artifact 主轴**对重采样稳健**非小样本偶然；(2) B 残余 gap vs headline（−0.0134）n=51 95% CI **[−0.1311,0.0846]** **含 0** p=0.4478 → **统计上闭合**（B 把 gap 关到易类天花板噪声内）→ **强化** §L；(3) C 崩溃 vs CONTROL（−0.2745）n=51 95% CI **[−0.4118,−0.1373]** p=0.0 → **显著**，v0.36 缩放伪影诊断是**真实效应**非 n=51 错觉。cross-check vs v0.32 9/9 点估计 MATCH；freeze-integrity PASS（v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha match v0.32 manifest）；构造层非整合层不重算 RELEASE_INDEX（按 v0.32/v0.36 先例）；DETERMINISM PASS（字节一致）；leak 0 |
| **v0.39** | **发布索引再生 + DATA_CARD addendum §O（整合层）** | `release_index_v0.39.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.39.md` / `consolidation_report_v0.39.json` / `report_v39.html` | 闭环 v0.38 下一步候选：把 v0.38（gap-shrink bootstrap CI 构造层）纳入下一整合层再生 RELEASE_INDEX（v0.38 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32/v0.36 构造层先例）+ 把 v0.38「§L/§N 核心结论从点估计升级为置信区间——B 缩 gap over CONTROL +0.2157 显著 [n=51 95% CI 0.0980,0.3529 p=0.0005 / n=42 CI 0.1429,0.4048 p=0.0] → §L weak-model-artifact 主轴对重采样稳健；B 残余 gap −0.0134 含 0 [n=51 CI −0.1311,0.0846 p=0.4478] → 统计上闭合 → 强化 §L；C 崩溃 −0.2745 显著 [n=51 CI −0.4118,−0.1373 p=0.0] → v0.36 缩放伪影真实 → 证实 §N；§L 主结论 + §N 子结论不变均 CI-backed；§L「magnitude 不可靠」caveat 退役；首个 unseen-user gap CI」回写进 v0.16 DATA_CARD addendum 作为 **§O**（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.38 freeze-integrity（manifest PASS + all_match + cross_check_vs_v032 MATCH 9/9 [rounding tolerance：b_shrink_vs_v026 0.215686 vs v0.32-recorded 0.215687 末位 float 舍入] + 跨层独立重算 v0.38 输出 gap_shrink_ci.json/gap_shrink_ci_characterization.md match 其自身 manifest + 公共 v0.15 锚点 5dd43df6… + v0.26 split 3 文件 + v0.32 submission+gap_shrink 4 文件 match v0.38 inputs）；**38 版本 / 37 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.38 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.40** | **冻结 lineage 完整性 RE-sweep（subsumes v0.34，构造层）** | `lineage_audit_v040.json` / `lineage_audit_manifest.json` / `report_v40.html` | 闭环 v0.39 下一步候选（v0.38 产新 manifest 锚点→解锁 lineage RE-sweep，承 v0.23→v0.30→v0.34 cadence）：把 v0.34 全树审计（32 版本 / 170 锚点）重跑到现已冻结的 **38 版本 / 89 manifest / 206 锚点**（135 unique，197 PASS + 9 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v034 回归校验**——112/112 v0.34 frozen 锚点仍 bit-intact（排除 6 个 v0.34 标记的顶层 living RELEASE_INDEX.md），证 v0.35–v0.39 build-out 未静默漂移任一冻结输入；**17 net-new anchors** since v0.34（v0.35/v0.36/v0.37/v0.38/v0.39 新 provenance 链接：v0.36→v0.26 split + v0.15 anchor；v0.38→v0.26 split + v0.32 gap_shrink + v0.15 anchor；各 consolidation→各自 outputs）。**drift_vs_v034 传递式 subsumes v0.34 自身的 drift_vs_v030**（v0.34 锚点集 ⊇ v0.30 锚点集），故显式 v0.30 recheck 省略无损。frozen per-version RELEASE_INDEX copies 交叉校验 **9/9 PASS**（现含 v0.35/v0.37/v0.39 consolidation）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34 先例推到下一整合层 v0.41）；纯元数据不改冻结层（v0.1–v0.39 untouched）；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.41** | **发布索引再生 + DATA_CARD addendum §P（整合层）** | `release_index_v0.41.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.41.md` / `consolidation_report_v0.41.json` / `report_v41.html` | 闭环 v0.40 下一步候选：把 v0.40（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.34）纳入下一整合层再生 RELEASE_INDEX（v0.40 明确推到下一整合层，承 v0.30/v0.34 审计层先例 + v0.34→v0.35 / v0.38→v0.39 构造→整合 cadence）+ 把 v0.40「38 版本 / 89 manifest / 206 锚点 [135 unique] → 197 PASS + 9 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v034 112/112 0 回归 + 17 net-new since v0.34 全 bit-intact + frozen per-version RELEASE_INDEX copies 9/9 + v0.23→v0.30→v0.34→v0.40 RE-sweep cadence」回写进 v0.16 DATA_CARD addendum 作为 **§P**——**扩展 §M 覆盖窗口**从 32 版本（v0.34）到 38 版本（v0.40），不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.40 freeze-integrity（manifest PASS + headline overall PASS + drift_vs_v034 112/112 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 9/9 + 跨层独立重算 v0.40 输出 lineage_audit_v040.json match 其自身 manifest + v0.13 manifest 输入 + v0.34 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；**40 版本 / 39 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.40 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.42** | **per-class gap-shrink bootstrap CI（构造层）** | `gap_shrink_perclass_ci.json` / `gap_shrink_perclass_ci_characterization.md` / `gap_shrink_perclass_ci_manifest.json` / `report_v42.html` | 闭环 v0.38 characterization 显式留的「per-class contrasts not computed」开放问题——把 v0.38 首个 **treatment-level**（headline）unseen-user gap CI **定位到具体类**。per-class paired bootstrap（10000 次，`numpy default_rng(seed=0)`，within-class one shared resample vector；n≥MIN_CI_N=10 报 CI，n<10 仅点估计因 bootstrap 退化）。**`other`**（n=15/14）B−CONTROL shrink +0.667/+0.714 95% CI **[0.4,0.867]/[0.5,0.929]** p=0.0 → **两子集均显著**——v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界（弱最近质心崩 CTRL 0.27，softmax 修好 B 0.93-1.0），§L weak-model-artifact **定位到此类**。**`code_dev`**（n=27/25 最大类）shrink +0.074/+0.040 CI 含 0 ns——CTRL 已 0.89/0.96 在弱模型天花板，B 几无改进，「已解决」类非 gap 源。薄类（n≤4）仅点估计（eda_virtuoso_schematic CTRL=B=0 两模型全败，源硬限）= v0.28/v0.32「薄类源硬限残项」的 per-class-CI 证据。**净结论**：+0.2157 headline shrink 几乎全来自 `other` 边界修复非均匀提升；**精化（不推翻）§L/§O**——weak-model artifact 真实显著但 locus 是 `other` disputed 边界非全类。下游含义：语义级 treatment（LLM-gated）须帮 code_dev 突破弱模型天花板 + 解决薄类。两 freeze-integrity cross-check：vs v0.32 9/9 点估计 MATCH + vs v0.38 headline n=51 B−CONTROL CI 逐位相等 [0.098039,0.352941]（subsumes v0.38 headline，同 item 集分区）；freeze-integrity PASS（v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission on-disk sha match v0.32 manifest）；构造层非整合层不重算 RELEASE_INDEX（按 v0.32/v0.36/v0.38 先例推到下一整合层）；产新 manifest 锚点→解锁延后的 lineage RE-sweep；DETERMINISM PASS（字节一致）；leak 0 |
| **v0.43** | **发布索引再生 + DATA_CARD addendum §Q（整合层）** | `release_index_v0.43.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.43.md` / `consolidation_report_v0.43.json` / `report_v43.html` | 闭环 v0.42 下一步候选：把 v0.42（per-class gap-shrink bootstrap CI 构造层）纳入下一整合层再生 RELEASE_INDEX（v0.42 明确推到下一整合层，承 v0.32/v0.36/v0.38 构造层先例 + v0.38→v0.39 / v0.40→v0.41 构造→整合 cadence）+ 把 v0.42「§L weak-model-artifact 定位到 `other` disputed 边界：`other` n=15/14 B−CONTROL shrink +0.667/+0.714 95% CI [0.4,0.867]/[0.5,0.929] p=0.0 两子集均显著（CTRL 0.27→B 0.93-1.0）＝v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界现 CI-backed；`code_dev` n=27/25 最大类 CI 含 0 ns＝弱模型天花板非 gap 源；薄类 n<10 仅点估计＝v0.28/v0.32 薄类源硬限残项的 per-class-CI 证据」回写进 v0.16 DATA_CARD addendum 作为 **§Q**——**精化（不推翻）§L/§O**，gap-attribution cadence（§I→§J→§L→§N→§O→**§Q per-class**）推到 per-class 闭环。机器验证 v0.42 freeze-integrity（manifest PASS + cross-check vs v0.32 9/9 点估计 MATCH + cross-check vs v0.38 headline CI 逐位相等 [0.098039,0.352941] ＝同 item 集分区 + 跨层独立重算 v0.42 输出 gap_shrink_perclass_ci.json/characterization.md match 其自身 manifest + 公共 v0.15 锚点 5dd43df6 + v0.26 split 3 + v0.32 submission 4 on-disk sha match）；**42 版本 / 41 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.42 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.44** | **冻结 lineage 完整性 RE-sweep（subsumes v0.40，构造层）** | `lineage_audit_v044.json` / `lineage_audit_manifest.json` / `report_v44.html` | 闭环 v0.43 下一步候选（v0.42 产新 manifest 锚点→解锁 lineage RE-sweep，承 v0.23→v0.30→v0.34→v0.40 cadence）：把 v0.40 全树审计（38 版本 / 89 manifest / 206 锚点）重跑到现已冻结的 **42 版本 / 97 manifest / 228 锚点**（144 unique，217 PASS + 11 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v040 回归校验**——126/126 v0.40 frozen 锚点仍 bit-intact（排除 9 个 v0.40 标记的顶层 living RELEASE_INDEX.md），证 v0.41–v0.43 build-out 未静默漂移任一冻结输入；**9 net-new anchors** since v0.40（v0.40 audit 自身 1 + v0.41 consolidation outputs 3 + v0.42 per-class CI outputs 2 + v0.43 consolidation outputs 3；v0.42 的 input 锚点[v0.26 split/v0.32 gap_shrink/v0.15/v0.8 source_manifest/v0.38 gap_shrink_ci]已被 v0.38 manifest 声明、由 v0.40 校验，故非 net-new 而在 drift_vs_v040 重验证）。**drift_vs_v040 传递式 subsumes v0.40 自身的 drift_vs_v034**（v0.40 锚点集 ⊇ v0.34 锚点集 ⊇ v0.30 ⊇ v0.23），故显式 v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→**v0.44** RE-sweep cadence。frozen per-version RELEASE_INDEX copies 交叉校验 **11/11 PASS**（现含 v0.41/v0.43 consolidation）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40 先例推到下一整合层，承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence）；纯元数据不改冻结层（v0.1–v0.43 untouched）；产新 manifest 锚点（lineage_audit_v044.json sha256）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.44 后解锁；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.45** | **发布索引再生 + DATA_CARD addendum §R（整合层）** | `release_index_v0.45.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.45.md` / `consolidation_report_v0.45.json` / `report_v45.html` | 闭环 v0.44 下一步候选：把 v0.44（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.40——5th whole-tree audit）纳入下一整合层再生 RELEASE_INDEX（v0.44 明确推到下一整合层，承 v0.30/v0.34/v0.40 审计层先例 + v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence）+ 把 v0.44「42 版本 / 97 manifest / 228 锚点 [144 unique] → 217 PASS + 11 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v040 126/126 0 回归 + 9 net-new since v0.40 全 bit-intact + frozen per-version RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44 RE-sweep cadence」回写进 v0.16 DATA_CARD addendum 作为 **§R**——**扩展 §P 覆盖窗口**从 38 版本（v0.40）到 42 版本（v0.44），不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.44 freeze-integrity（manifest PASS + audit overall PASS + headline 计数 42/97/228/144/217/11/0/0 + drift_vs_v040 126/126 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.44 输出 lineage_audit_v044.json match 其自身 manifest + v0.13 manifest 输入 + v0.40 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；**44 版本 / 43 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.44 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.46** | **冻结 lineage 完整性 RE-sweep（subsumes v0.44，构造层）** | `lineage_audit_v046.json` / `lineage_audit_manifest.json` / `report_v46.html` | 闭环 v0.45 下一步候选（v0.44 产新 manifest 锚点→解锁 lineage RE-sweep，承 v0.23→v0.30→v0.34→v0.40→v0.44 cadence）：把 v0.44 全树审计（42 版本 / 97 manifest / 228 锚点）重跑到现已冻结的 **44 版本 / 101 manifest / 231 锚点**（145 unique，220 PASS + 11 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v044 回归校验**——133/133 v0.44 frozen 锚点仍 bit-intact（排除 11 个 v0.44 标记的顶层 living RELEASE_INDEX.md），证 v0.45 build-out 未静默漂移任一冻结输入；**1 net-new anchor** since v0.44（v0.44 自身 lineage_audit_v044.json 输出，v0.44 扫描时作 OWN_OUT_REL 排除，现为冻结输入；v0.45 manifest 的 sha 链接均在 integrity/provenance 段非 anchor schema → 0 可验证锚点）。**drift_vs_v044 传递式 subsumes v0.44 自身的 drift_vs_v040**（v0.44 锚点集 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），故显式 v0.40/v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→v0.44→**v0.46** RE-sweep cadence 第 6 次全树审计。frozen per-version RELEASE_INDEX copies 交叉校验 **11/11 PASS**（v0.45 consolidation 无 outputs key 故不计入，其 frozen 副本仍由 full_tree_manifest 覆盖）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40/v0.44 先例推到下一整合层，承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 / v0.44→v0.45 构造→整合 cadence）；纯元数据不改冻结层（v0.1–v0.45 untouched）；产新 manifest 锚点（lineage_audit_v046.json sha256 `33e881a3…`）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.46 后解锁；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.47** | **发布索引再生 + DATA_CARD addendum §S（整合层）** | `release_index_v0.47.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.47.md` / `consolidation_report_v0.47.json` / `report_v47.html` | 闭环 v0.46 下一步候选：把 v0.46（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.44——6th whole-tree audit）纳入下一整合层再生 RELEASE_INDEX（v0.46 明确推到下一整合层，承 v0.30/v0.34/v0.40/v0.44 审计层先例 + v0.44→v0.45 构造→整合 cadence）+ 把 v0.46「44 版本 / 101 manifest / 231 锚点 [145 unique] → 220 PASS + 11 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v044 133/133 0 回归 + 1 net-new since v0.44 + frozen per-version RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 RE-sweep cadence 第 6 次全树审计」回写进 v0.16 DATA_CARD addendum 作为 **§S**——**扩展 §R 覆盖窗口**从 42 版本（v0.44）到 44 版本（v0.46），不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.46 freeze-integrity（manifest PASS + audit overall PASS + headline 计数 44/101/231/145/220/11/0/0 + drift_vs_v044 133/133 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.46 输出 lineage_audit_v046.json match 其自身 manifest + v0.13 manifest 输入 + v0.44 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；**46 版本 / 45 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.46 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |
| **v0.48** | **冻结 lineage 完整性 RE-sweep（subsumes v0.46，构造层）** | `lineage_audit_v048.json` / `lineage_audit_manifest.json` / `report_v48.html` | 闭环 v0.47 下一步候选（v0.46 产新 manifest 锚点→解锁 lineage RE-sweep，承 v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 cadence）：把 v0.46 全树审计（44 版本 / 101 manifest / 231 锚点）重跑到现已冻结的 **46 版本 / 105 manifest / 234 锚点**（146 unique，223 PASS + 11 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v046 回归校验**——134/134 v0.46 frozen 锚点仍 bit-intact（排除 11 个 v0.46 标记的顶层 living RELEASE_INDEX.md），证 v0.47 build-out 未静默漂移任一冻结输入；**1 net-new anchor** since v0.46（v0.46 自身 lineage_audit_v046.json 输出，v0.46 扫描时作 OWN_OUT_REL 排除，现为冻结输入；v0.47 manifest 的 sha 链接均在 integrity/provenance 段非 anchor schema → 0 可验证锚点）。**drift_vs_v046 传递式 subsumes v0.46 自身的 drift_vs_v044**（v0.46 锚点集 ⊇ v0.44 ⊇ v0.40 ⊇ v0.34 ⊇ v0.30 ⊇ v0.23），故显式 v0.44/v0.40/v0.34/v0.30/v0.23 recheck 省略无损——v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→**v0.48** RE-sweep cadence 第 7 次全树审计。frozen per-version RELEASE_INDEX copies 交叉校验 **11/11 PASS**（v0.45/v0.47 consolidation 无 outputs key 故不计入，其 frozen 副本仍由 full_tree_manifest 覆盖）。drift vs v0.13 PASS 73/73。公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40/v0.44/v0.46 先例推到下一整合层，承 v0.44→v0.45 / v0.46→v0.47 构造→整合 cadence）；纯元数据不改冻结层（v0.1–v0.47 untouched）；产新 manifest 锚点（lineage_audit_v048.json sha256 `08553f86…`）→下一全树 lineage RE-sweep 在下一整合层吸收 v0.48 后解锁；DETERMINISM PASS（3/3 字节一致）；leak 0 |
| **v0.49** | **发布索引再生 + DATA_CARD addendum §T（整合层）** | `release_index_v0.49.json` / `RELEASE_INDEX.md` / `DATA_CARD_ADDENDUM_v0.49.md` / `consolidation_report_v0.49.json` / `report_v49.html` | 闭环 v0.48 下一步候选：把 v0.48（冻结 lineage 完整性 RE-sweep 构造层，subsumes v0.46——7th whole-tree audit）纳入下一整合层再生 RELEASE_INDEX（v0.48 明确推到下一整合层，承 v0.30/v0.34/v0.40/v0.44/v0.46 审计层先例 + v0.46→v0.47 构造→整合 cadence）+ 把 v0.48「46 版本 / 105 manifest / 234 锚点 [146 unique] → 223 PASS + 11 LIVING_FILE_BYDESIGN + 0 broken + drift_vs_v046 134/134 0 回归 + 1 net-new since v0.46 + frozen per-version RELEASE_INDEX copies 11/11 + v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→v0.48 RE-sweep cadence 第 7 次全树审计」回写进 v0.16 DATA_CARD addendum 作为 **§T**——**扩展 §S 覆盖窗口**从 44 版本（v0.46）到 46 版本（v0.48），不推翻任何前完整性结论（§F 预留 3 标注者 Fleiss κ，gate 阻塞）。机器验证 v0.48 freeze-integrity（manifest PASS + audit overall PASS + headline 计数 46/105/234/146/223/11/0/0 + drift_vs_v046 134/134 0 回归 + drift_vs_v013 73/73 + frozen RELEASE_INDEX copies 11/11 + 跨层独立重算 v0.48 输出 lineage_audit_v048.json match 其自身 manifest + v0.13 manifest 输入 + v0.46 audit 回归基线输入 + 公共 v0.15 锚点 5dd43df6…）；**48 版本 / 47 ACTIVE / 1 SUPERSEDED**；纯元数据不改冻结层（v0.16/v0.20–v0.48 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0 |

### 构建顺序依赖

```
v0.1 (脱敏源) ──► v0.2 (聚类) ──► v0.3 (策展/监督) ──► v0.4 (judge)
                                                       │
v0.5 (共识 gold) ◄─────────────────────────────────────┘
   │
v0.6 (去重/global_id) ──► v0.7 (逐比特) ──► v0.8 (冻结/跨主机)
                                                │
v0.9 (发布 bundle) ◄───────────────────────────┘
   │
v0.10 (rc1 文档) ──► v0.11 (worked example)
                          │
v0.12 (统一入口 ◄─────────┘  本文件)
                          │
v0.13 (版本演进 diff ◄─────┘  bench_v0.13/)
                           │
v0.14 (统计严谨性 ◄─────────┘  bench_v0.14/)
                           │
v0.15 (去偏 split + 双标注者 ◄──┘  bench_v0.15/)
                           │
v0.16 (DATA_CARD 增补 ◄─────┘  bench_v0.16/)
                           │
v0.17 (诊断发布 bundle ◄────┘  bench_v0.17/)
                           │
v0.18 (disputed 项刻画 ◄────┘  bench_v0.18/)
   │
   ▼
v0.19 (诊断 split 自包含包 ◄────┘  bench_v0.19/  融合 v0.17 bundle + v0.18 characterization)
    │
    ▼
v0.20 (发布整合/弃用 ◄────┘  bench_v0.20/  验证 v0.17→v0.19 超集 + 顶层 RELEASE_INDEX)
    │
    ▼
v0.21 (诊断 split bootstrap CI ◄────┘  bench_v0.21/  对 v0.19 headline gap/robustness 加 95% CI + 显著性检验)
     │
     ▼
v0.22 (发布索引再生 + §G ◄────┘  bench_v0.22/  纳入 v0.21 + 回写 §G 到 v0.16 addendum，整合层)
      │
      ▼
v0.23 (冻结 lineage 完整性全扫 ◄────┘  bench_v0.23/  把 v0.22 单锚点推广为全树 124 锚点穷举校验)
     │
     ▼
v0.24 (发布索引再生 + §H ◄────┘  bench_v0.24/  纳入 v0.23 + 回写 §H 到 v0.16 addendum，整合层)
     │
     ▼
v0.25 (per-user 公平性审计 ◄────┘  bench_v0.25/  量化 v0.16 §E 用户集中局限 + LOUO user-robustness)
      │
      ▼
v0.26 (user-stratified re-split 构造 ◄────┘  bench_v0.26/  闭环 v0.25：构造未见用户 held-out test，gap=−0.2291)
      │
      ▼
v0.27 (发布索引再生 + §I ◄────┘  bench_v0.27/  纳入 v0.25+v0.26 + 回写 §I 到 v0.16 addendum，整合层)
      │
      ▼
v0.28 (user-balanced re-split 构造 ◄────┘  bench_v0.28/  闭环 v0.26：多用户 train + 资格规则，2/9 类合格，dZ=−0.1176 证伪「多用户即缩 gap」)
       │
       ▼
v0.29 (发布索引再生 + §J ◄────┘  bench_v0.29/  纳入 v0.28 + 回写 §J 到 v0.16 addendum，整合层)
        │
        ▼
v0.30 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.30/  subsumes v0.23：28 版本 151 锚点全 PASS + drift_vs_v023 回归 + frozen RELEASE_INDEX 副本交叉校验，建模 v0.23 latent living-file bug)
         │
         ▼
v0.31 (发布索引再生 + §K ◄────┘  bench_v0.31/  纳入 v0.30 + 回写 §K 到 v0.16 addendum，整合层)
          │
          ▼
v0.32 (stronger-model gap-shrink 构造 ◄────┘  bench_v0.32/  闭环 v0.28 命名未测的「更强模型/更富特征」药方：冻结 v0.26 split 逐位复用，softmax 同特征 acc 0.5882→0.8039 缩 gap +0.2157 几乎闭合 → gap 是 weak-model artifact 非内禀难度；粗 meta 特征反扩大 gap)
           │
           ▼
v0.33 (发布索引再生 + §L ◄────┘  bench_v0.33/  纳入 v0.32 + 回写 §L 到 v0.16 addendum，整合层——修订 v0.28 §J「内禀难度」为「weak-model artifact 主项 + 薄类源硬限残项」)
              │
              ▼
v0.34 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.34/  subsumes v0.30：32 版本 170 锚点 164 PASS + 6 LIVING + drift_vs_v030 回归 104/104 + frozen RELEASE_INDEX 副本 6/6，传递式 subsumes v0.30 的 drift_vs_v023)
              │
              ▼
v0.35 (发布索引再生 + §M ◄────┘  bench_v0.35/  纳入 v0.34 + 回写 §M 到 v0.16 addendum，整合层——记录 v0.23→v0.30→v0.34 完整性审计 cadence：32 版本 170 锚点 164 PASS + 6 LIVING + drift_vs_v030 104/104 0 回归 + 10 net-new since v0.30)
               │
               ▼
v0.36 (meta-feature scaling-artifact 消融 ◄────┘  bench_v0.36/  诊断 v0.32 TREATMENT C 负结果：meta 块占 rich norm² 79.5% → C≈meta-only 0.2941；D 重缩放 acc 0.5294 / F 整行归一 acc 0.5490 回升 → C 崩溃是缩放伪影；修正 §L「粗 meta 为负」为「缩放后温和偏负」，§L 主结论不变)
                │
                ▼
v0.37 (发布索引再生 + §N ◄────┘  bench_v0.37/  纳入 v0.36 + 回写 §N 到 v0.16 addendum，整合层——修正 §L「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」，§L 主结论 + 缩 gap 方向不变)
                │
                ▼
v0.38 (gap-shrink bootstrap CI 构造 ◄────┘  bench_v0.38/  把 v0.32 §L/§N 核心结论从点估计升级为置信区间：配对 percentile bootstrap n=51/n=42——B 缩 gap over CONTROL 显著 [0.0980,0.3529] p=0.0005（§L weak-model-artifact 主轴对重采样稳健）；B 残余 gap 含 0 p=0.4478（统计上闭合，强化 §L）；C 崩溃显著 [−0.4118,−0.1373] p=0.0（v0.36 缩放伪影是真实效应）；首个 unseen-user gap CI)
                 │
                 ▼
v0.39 (发布索引再生 + §O ◄────┘  bench_v0.39/  纳入 v0.38 + 回写 §O 到 v0.16 addendum，整合层——把 §L/§N 核心结论从点估计升级为置信区间：B 缩 gap 显著（§L 主轴对重采样稳健）；B 残余 gap 含 0（统计上闭合，强化 §L）；C 崩溃显著（v0.36 缩放伪影真实，证实 §N）；§L 主结论 + §N 子结论不变均 CI-backed，§L「magnitude 不可靠」caveat 退役；首个 unseen-user gap CI)
                 │
                 ▼
v0.40 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.40/  subsumes v0.34（传递式 v0.30/v0.23）：38 版本 89 manifest 206 锚点 197 PASS + 9 LIVING + drift_vs_v034 112/112 0 回归 + 17 net-new since v0.34 + frozen RELEASE_INDEX 副本 9/9，传递式 subsumes v0.34 的 drift_vs_v030)
                 │
                 ▼
v0.41 (发布索引再生 + §P ◄────┘  bench_v0.41/  纳入 v0.40 + 回写 §P 到 v0.16 addendum，整合层——扩展 §M 覆盖窗口从 32 版本（v0.34）到 38 版本（v0.40），不推翻任何前完整性结论：38 版本 206 锚点 197 PASS + 9 LIVING + drift_vs_v034 112/112 0 回归 + v0.23→v0.30→v0.34→v0.40 RE-sweep cadence)
                  │
                  ▼
v0.42 (per-class gap-shrink bootstrap CI 构造 ◄────┘  bench_v0.42/  闭环 v0.38「per-class contrasts not computed」：per-class paired bootstrap 定位 §L weak-model-artifact——`other` n=15/14 shrink +0.667/+0.714 CI [0.4,0.867]/[0.5,0.929] p=0.0 两子集均显著（disputed 边界修复）；`code_dev` n=27/25 shrink +0.074/+0.040 CI 含 0 ns（已在弱模型天花板）；薄类 n≤4 仅点估计=源硬限残项证据；cross-check vs v0.38 headline CI 逐位相等；精化 §L/§O 不推翻)
                   │
                   ▼
 v0.43 (发布索引再生 + §Q ◄────┘  bench_v0.43/  纳入 v0.42 + 回写 §Q 到 v0.16 addendum，整合层——精化 §L/§O：§L weak-model-artifact 定位到 `other` disputed 边界（CI-backed），`code_dev` 在弱模型天花板 ns，薄类源硬限点估计；gap-attribution cadence §I→§J→§L→§N→§O→§Q per-class 闭环；42 版本 / 41 ACTIVE / 1 SUPERSEDED；机器验证 v0.42 freeze-integrity 全过)
                    │
                    ▼
 v0.44 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.44/  subsumes v0.40（传递式 v0.34/v0.30/v0.23）：42 版本 97 manifest 228 锚点 217 PASS + 11 LIVING + drift_vs_v040 126/126 0 回归 + 9 net-new since v0.40 + frozen RELEASE_INDEX 副本 11/11，传递式 subsumes v0.40 的 drift_vs_v034；构造层不重算 RELEASE_INDEX，产新 manifest 锚点→下一整合层吸收后下一 RE-sweep 解锁)
                     │
                     ▼
  v0.45 (发布索引再生 + §R ◄────┘  bench_v0.45/  纳入 v0.44 + 回写 §R 到 v0.16 addendum，整合层——扩展 §P 覆盖窗口从 38 版本（v0.40）到 42 版本（v0.44），不推翻任何前完整性结论：42 版本 228 锚点 217 PASS + 11 LIVING + drift_vs_v040 126/126 0 回归 + v0.23→v0.30→v0.34→v0.40→v0.44 RE-sweep cadence 第 5 次全树审计)
                     │
                     ▼
 v0.46 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.46/  subsumes v0.44（传递式 v0.40/v0.34/v0.30/v0.23）：44 版本 101 manifest 231 锚点 220 PASS + 11 LIVING + drift_vs_v044 133/133 0 回归 + 1 net-new since v0.44 + frozen RELEASE_INDEX 副本 11/11，传递式 subsumes v0.44 的 drift_vs_v040；构造层不重算 RELEASE_INDEX，产新 manifest 锚点 lineage_audit_v046.json sha256 33e881a3…→下一整合层吸收后下一 RE-sweep 解锁)
                     │
                     ▼
  v0.47 (发布索引再生 + §S ◄────┘  bench_v0.47/  纳入 v0.46 + 回写 §S 到 v0.16 addendum，整合层——扩展 §R 覆盖窗口从 42 版本（v0.44）到 44 版本（v0.46），不推翻任何前完整性结论：44 版本 231 锚点 220 PASS + 11 LIVING + drift_vs_v044 133/133 0 回归 + v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 RE-sweep cadence 第 6 次全树审计)
                      │
                      ▼
  v0.48 (冻结 lineage 完整性 RE-sweep ◄────┘  bench_v0.48/  subsumes v0.46（传递式 v0.44/v0.40/v0.34/v0.30/v0.23）：46 版本 105 manifest 234 锚点 223 PASS + 11 LIVING + drift_vs_v046 134/134 0 回归 + 1 net-new since v0.46 + frozen RELEASE_INDEX 副本 11/11，传递式 subsumes v0.46 的 drift_vs_v044；构造层不重算 RELEASE_INDEX，产新 manifest 锚点 lineage_audit_v048.json sha256 08553f86…→下一整合层吸收后下一 RE-sweep 解锁，第 7 次全树审计)
                    │
                    ▼
  v0.49 (发布索引再生 + §T ◄────┘  bench_v0.49/  纳入 v0.48 + 回写 §T 到 v0.16 addendum，整合层——扩展 §S 覆盖窗口从 44 版本（v0.46）到 46 版本（v0.48），不推翻任何前完整性结论：46 版本 234 锚点 223 PASS + 11 LIVING + drift_vs_v046 134/134 0 回归 + 1 net-new + frozen RELEASE_INDEX 副本 11/11，传递式 subsumes v0.46 的 drift_vs_v044；48 版本 / 47 ACTIVE / 1 SUPERSEDED；机器验证 v0.48 freeze-integrity 全过)
```

---

## 已发布 bundle（v0.10 = v1.0-rc1）

第三方拿到 [`bench_v0.10/out/`](bench_v0.10/out/) 一个目录即含数据 + 许可证 + datasheet + 引用 + 基线 + 清单：

| 文件 | 内容 |
|---|---|
| `tasks.jsonl` | 2112 条 canonical 任务（无 gold label，评估语料） |
| `gold.jsonl` | 246 条共识 gold answer key |
| `few_shot.jsonl` | 27 条分层 ≤3/类（带标签，供提交者 few-shot） |
| `test_set.jsonl` | 219 条盲测集（无标签） |
| `LICENSE` / `CITATION.cff` / `DATA_CARD.md` | 发布就绪文档 |
| `BASELINE_MODEL_CARD.md` | majority baseline acc=0.2146 / macroF1=0.0393（参考地板） |
| `RELEASE_CHECKLIST.md` | 15 项发布就绪清单（12/15 done） |
| `RC_MANIFEST.json` | 全 bundle checksums + `internal_shippable=True` |

**端到端一条命令验证"如何提交"**：
```bash
cd designflow/bench_v0.11 && bash run_example.sh
# 仅用 few_shot (27) 训练 → 预测 test_set (219) → 冻结 v0.9 评估器打分
# acc=0.8174 / macroF1=0.7239 / coverage=1.0（远高于 majority 0.2146/0.0393）
```

**诊断 bundle（v0.19 = 去偏 v1.x split，规范诊断发布）**：[`bench_v0.19/out/`](bench_v0.19/out/)
含 `diagnostic_test_set.jsonl`（368=219 consensus + 149 disputed，**blinded 无标签**）+
`diagnostic_answers.jsonl`（评估器持有的 answer key，disputed 项 `gold_label=null` + `label_v3`/`label_v4`）+
`diagnostic_characterization.md`（v0.18 机理性刻画并入，使 bundle 自包含）+
`bench_v0.19/diagnostic_eval.py`（独立 CLI 双标注者评估器：consensus gold acc + disputed v3/v4 agreement
+ mean robustness + headline gap）。第三方 `--submission your.jsonl` 直接调评估器。
> ⚠️ v0.17 同名 bundle 已 SUPERSEDED by v0.19（v0.20 机器验证：v0.17 test_set 含标签非严格 blinded、
> 无 characterization；保留作 provenance，新评测请用 v0.19）。状态图见 [`RELEASE_INDEX.md`](RELEASE_INDEX.md)。

**诊断不确定性（CI / 显著性，v0.21）**：[`bench_v0.21/out/diagnostic_ci.json`](bench_v0.21/out/diagnostic_ci.json)
对 v0.19 headline gap(+0.5086)/robustness(0.3087) 加分层 bootstrap 95% CI + one-sided 显著性检验
（gap CI [0.445,0.573] 排除 0 → p=0.0）。统计有效性 addendum 的完整当前图景 = v0.16 §A–§E
（[`bench_v0.16/out/DATA_CARD_ADDENDUM.md`](bench_v0.16/out/DATA_CARD_ADDENDUM.md)）**+** v0.22 §G
（[`bench_v0.22/out/DATA_CARD_ADDENDUM_v0.22.md`](bench_v0.22/out/DATA_CARD_ADDENDUM_v0.22.md)，gap 显著性 CI）
**+** v0.24 §H（[`bench_v0.24/out/DATA_CARD_ADDENDUM_v0.24.md`](bench_v0.24/out/DATA_CARD_ADDENDUM_v0.24.md)，冻结 lineage 完整性审计）
**+** v0.27 §I（[`bench_v0.27/out/DATA_CARD_ADDENDUM_v0.27.md`](bench_v0.27/out/DATA_CARD_ADDENDUM_v0.27.md)，per-user 公平性 + user-stratified 泛化 gap）
**+** v0.29 §J（[`bench_v0.29/out/DATA_CARD_ADDENDUM_v0.29.md`](bench_v0.29/out/DATA_CARD_ADDENDUM_v0.29.md)，user-balanced re-split + 证伪「多用户即缩 gap」）
**+** v0.31 §K（[`bench_v0.31/out/DATA_CARD_ADDENDUM_v0.31.md`](bench_v0.31/out/DATA_CARD_ADDENDUM_v0.31.md)，冻结 lineage 完整性 RE-sweep + v0.23 latent living-file bug 建模）。
**+** v0.33 §L（[`bench_v0.33/out/DATA_CARD_ADDENDUM_v0.33.md`](bench_v0.33/out/DATA_CARD_ADDENDUM_v0.33.md)，stronger-model gap-shrink + **修订 v0.28 §J「内禀难度」**为「weak-model artifact 主项 + 薄类源硬限残项」）。
**+** v0.35 §M（[`bench_v0.35/out/DATA_CARD_ADDENDUM_v0.35.md`](bench_v0.35/out/DATA_CARD_ADDENDUM_v0.35.md)，冻结 lineage 完整性 RE-sweep subsumes v0.30：32 版本 / 77 manifest / 170 锚点 164 PASS + 6 LIVING + drift_vs_v030 104/104 0 回归 + 10 net-new since v0.30 + frozen per-version RELEASE_INDEX 副本 6/6；记录 v0.23→v0.30→v0.34 审计 cadence）。
**+** v0.37 §N（[`bench_v0.37/out/DATA_CARD_ADDENDUM_v0.37.md`](bench_v0.37/out/DATA_CARD_ADDENDUM_v0.37.md)，meta-feature scaling-artifact：C 崩溃是特征缩放伪影（meta 块占 rich norm² 79.5% → C≈meta-only）→ **修正 §L「粗 meta 戏剧性为负」**为「缩放后温和偏负」；§L 主结论（B 缩 gap +0.2157 → weak-model artifact）不变、§L「需语义级特征缩 gap」方向成立）。
**+** v0.39 §O（[`bench_v0.39/out/DATA_CARD_ADDENDUM_v0.39.md`](bench_v0.39/out/DATA_CARD_ADDENDUM_v0.39.md)，gap-shrink bootstrap CI：把 §L/§N 核心结论从**点估计升级为置信区间**——B 缩 gap over CONTROL +0.2157 显著 [n=51 95% CI 0.0980,0.3529 p=0.0005 / n=42 CI 0.1429,0.4048 p=0.0] → §L weak-model-artifact 主轴对重采样稳健非小样本偶然；B 残余 gap −0.0134 含 0 [n=51 CI −0.1311,0.0846 p=0.4478] → 统计上闭合 → 强化 §L；C 崩溃 −0.2745 显著 [n=51 CI −0.4118,−0.1373 p=0.0] → v0.36 缩放伪影是真实效应非 n=51 错觉 → 证实 §N；§L 主结论 + §N 子结论不变均 CI-backed，§L「magnitude 不可靠」caveat 退役；**首个 unseen-user gap CI**）。

**冻结 lineage 完整性（v0.23）**：[`bench_v0.23/out/lineage_audit.json`](bench_v0.23/out/lineage_audit.json)
把 v0.22 的单锚点 freeze-integrity（v0.15 debiased_test_set）推广为**全树穷举**——扫所有
`bench_v0.*/out/*.json` manifest，提取每个声明 `(path, sha256)` 锚点，对盘上文件逐个校验。
124 锚点全 PASS（95 unique 路径），drift vs v0.13 manifest PASS 73/73，lineage 图 8 版本声明的
输入全 bit-intact。**意义**：若任一冻结输入静默漂移，下游所有结论失效——v0.23 是首个能全局
捕获此漂移的检查。v0.24 整合层已把此审计回写进 v0.16 DATA_CARD addendum 作为 **§H**
（[`bench_v0.24/out/DATA_CARD_ADDENDUM_v0.24.md`](bench_v0.24/out/DATA_CARD_ADDENDUM_v0.24.md)）。

**Per-user 公平性（v0.25）**：[`bench_v0.25/out/fairness_audit.json`](bench_v0.25/out/fairness_audit.json)
把 v0.16 §E「single-machine source / 用户集中」定性局限升级为**量化**。consensus 块（n=219）跨 11
用户，Gini=0.5654 / HHI=0.1951（even baseline 0.0909 → **2.14× 集中**），top-3 用户占 70.3%。
**Leave-one-user-out |Δ|max = 0.0486 < 0.05 → headline accuracy IS user-robust**——即使 3 个用户
占 70%，去掉任一用户 headline 也只在小范围漂移，不是单用户伪迹。**然而 8/9 类 ≥0.5 单用户垄断**
（3/9 ==1.0；eda_aether_layout max-share 0.9787），所以 per-class P/R/F1 对尾类实质是 per-user
metric，泛化到未见用户未测。**净结论**：headline 经受用户分层考验，per-class 拆分没有——
这是 DATA_CARD「single-machine source」局限背后的具体证据，motivates user-stratified re-split
作为 v1.x 构造候选。audit 层非整合层，不重算 RELEASE_INDEX。

**User-stratified re-split 构造（v0.26）**：[`bench_v0.26/out/user_resplit.json`](bench_v0.26/out/user_resplit.json)
直接闭环 v0.25 的「v1.x 构造候选」——对冻结 v0.15 共识 219 项按用户分层重切：每类主用户进 train，
其余用户进 held-out test，测 baseline 对**未见该标签的用户**的泛化能力。**user-strat acc=0.5882
（n_test=51）vs headline 0.8174 → gap=−0.2291**——证实存在 headline 掩盖的未见用户泛化缺口：`code_dev`
迁移好（0.889），但 `other`（0.267）和 `eda_virtuoso_schematic`（0.0）的主用户标签签名不迁移。
3 类 IMPOSSIBLE 单用户类（eda_innovus 14 / eda_timing_power 2 / eda_drc_lvs 1，共 17 项）无法
分层——源硬限，仅更多用户/机器可解。fully-unseen-user 子集 n=42 acc=0.6667。构造层非整合层，
不重算 RELEASE_INDEX（按 v0.21/v0.23/v0.25 先例推到下一整合层）。FREEZE-INTEGRITY PASS、
DETERMINISM PASS、leak 0。

**发布索引再生 + §I 整合层（v0.27）**：[`bench_v0.27/out/`](bench_v0.27/out/)
在单一整合步骤吸收 v0.25 + v0.26——把两层纳入 RELEASE_INDEX（26 版本 / 25 ACTIVE / 1 SUPERSEDED）
+ 把 v0.25「headline user-robust 但 per-class 单用户垄断」+ v0.26「未见用户泛化 gap=−0.2291」回写进
v0.16 DATA_CARD addendum 作为 **§I**（[`bench_v0.27/out/DATA_CARD_ADDENDUM_v0.27.md`](bench_v0.27/out/DATA_CARD_ADDENDUM_v0.27.md)）。
机器验证 v0.25（4 锚点全 match disk + cross_check MATCH）+ v0.26（freeze_integrity PASS + cross_check PASS）
+ 公共 v0.15 锚点 5dd43df6… 跨层独立重算一致。纯元数据整合层，不改任何冻结 `out/`；DETERMINISM PASS
（5/5 字节一致）；leak 0。顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.27 视图。

**user-balanced re-split 构造层（v0.28，v1.x 候选）**：[`bench_v0.28/out/`](bench_v0.28/out/)
闭环 v0.26 下一步候选「据 gap=−0.2291 构造 user-balanced re-split [强制每类多用户，扔掉 IMPOSSIBLE 单用户类]」。
新增 v0.26→v0.28 的关键增量——**多用户 train**（top-2 用户/类，v0.26 的 train 是单主导用户）+ 严格**资格规则**
（≥3 用户且 top-2 之外项数 ≥2，保证 multi-user train + 未见用户 test 有非平凡支持）：**仅 2/9 类合格**
（code_dev / other），7 类不可（3 IMPOSSIBLE 单用户 + 4 薄类 top-2 外 <2 项）——这是诚实的源硬限，仅更多
用户/机器可解。受控实验在 2 类 core 上固定 17 项未见用户 test，对比 TRAIN-S（单用户/类，v0.26 式）vs
TRAIN-M（2 用户/类，**matched count 177==177**，唯一差异是 52 core train 项来自 1 vs 2 用户）→
**dZ_matched=−0.1176，多用户 train 反而更差**——证伪「收集更多用户即可缩小 gap」的乐观假设：v0.26 的
unseen-user gap 是该特征空间下标签识别的**内禀难度**，非单用户 train 伪影；要缩小需更强模型/更富特征，
而非单纯加用户。次要 TRAIN-M-all（202 项，混淆规模）dZ_all=−0.0588 仍不优于 S。阈值扫描表量化源代价。
构造层非整合层，不重算 RELEASE_INDEX（按 v0.21/v0.23/v0.25/v0.26 先例推到下一整合层）。FREEZE-INTEGRITY PASS
（v0.15 anchor 5dd43df6…）、CROSS-CHECK vs v0.15 PASS、MATCHED-COUNT INVARIANT PASS、DETERMINISM PASS
（10/10 字节一致）、leak 0。

**发布索引再生 + §J 整合层（v0.29）**：[`bench_v0.29/out/`](bench_v0.29/out/)
把 v0.28（user-balanced re-split 构造层）纳入 RELEASE_INDEX（28 版本 / 27 ACTIVE / 1 SUPERSEDED）
+ 把 v0.28「2/9 类 Tier-A + dZ=−0.1176 多用户 train 反而更差 → 证伪『多用户即缩 gap』，gap 是
该特征空间下标签识别的内禀难度」回写进 v0.16 DATA_CARD addendum 作为 **§J**
（[`bench_v0.29/out/DATA_CARD_ADDENDUM_v0.29.md`](bench_v0.29/out/DATA_CARD_ADDENDUM_v0.29.md)）。
机器验证 v0.28 freeze-integrity（status PASS + cross_check vs v0.15 PASS + 公共 v0.15 锚点 5dd43df6…
跨层独立重算一致 + 2 provenance 锚点 [v0.15 debiased_eval + v0.26 user_resplit] match disk）。
**净结论**：v0.27 §I 留的开放问题「v0.26 unseen-user gap=−0.2291 是单用户 train 伪影还是内禀
难度？」被 v0.28+v0.29 回答——matched-count 受控实验（177==177，唯一差异是用户多样性）
dZ=−0.1176 < 0，多用户 train 不缩 gap 反而更差 → **gap 是内禀难度**。「收集更多用户」的药方仍真
但**正交**：lift 覆盖（把 IMPOSSIBLE/Tier-B 类提升到 Tier-A 使其可多用户测试），不缩已覆盖类的
gap（缩 gap 需更强模型/更富特征）。纯元数据整合层，不改任何冻结 `out/`；DETERMINISM PASS
（5/5 字节一致）；leak 0。顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.29 视图。

**冻结 lineage 完整性 RE-sweep（v0.30，subsumes v0.23）**：[`bench_v0.30/out/lineage_audit_v030.json`](bench_v0.30/out/lineage_audit_v030.json)
把 v0.23 的全树审计（21 版本 / 124 锚点）重跑到现已冻结的 **28 版本 / 69 manifest / 151 锚点**（108 unique，
147 PASS + 4 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v023 回归校验**——加载冻结
`bench_v0.23/out/lineage_audit.json`，重验其 94 个 frozen 锚点仍 bit-intact（排除 1 个 v0.23 误验的顶层
living RELEASE_INDEX.md），证 v0.24–v0.29 build-out 未静默漂移任一冻结输入；13 net-new anchors since v0.23
（v0.24/v0.25/v0.26/v0.28/v0.29 新 provenance 链接）。**发现并建模 v0.23 latent bug**：v0.23 把 consolidation
报告的 `outputs[].RELEASE_INDEX.md`（bare name）解析到顶层 living 文件（按设计被各整合层覆盖），仅因 v0.23
时刻顶层 == v0.22 冻结副本而巧合 PASS；v0.30 把 living 文件正确标为 LIVING_FILE_BYDESIGN，并加 **frozen
per-version RELEASE_INDEX copies 交叉校验**（4/4 PASS——真冻结的是各 `bench_v0.XX/out/RELEASE_INDEX.md` 副本，
顶层 `designflow/RELEASE_INDEX.md` 是 living 导航图）。drift vs v0.13 manifest PASS 73/73。**意义**：v0.23 只覆盖
到 v0.22；v0.30 把全树完整性证据推进到 v0.29，确保 v0.19 诊断发布 / v0.21 gap CI / v0.28 matched-count 实验 /
v0.29 §J 解释全部建立在 bit-intact 的冻结依赖图上。audit 层非整合层，不重算 RELEASE_INDEX（按 v0.21/v0.23
先例推到下一整合层）；纯元数据不改冻结层；DETERMINISM PASS（3/3 字节一致）；leak 0。

**发布索引再生 + §K 整合层（v0.31）**：[`bench_v0.31/out/`](bench_v0.31/out/)
闭环 v0.30 下一步候选——把 v0.30（冻结 lineage RE-sweep，subsumes v0.23）纳入下一整合层再生
RELEASE_INDEX（v0.30 明确推到下一整合层，承 v0.21/v0.23 审计层先例），并把 v0.30 的全树完整性
RE-sweep + v0.23 latent living-file bug 建模回写进 v0.16 DATA_CARD addendum 作为 **§K**
（[`bench_v0.31/out/DATA_CARD_ADDENDUM_v0.31.md`](bench_v0.31/out/DATA_CARD_ADDENDUM_v0.31.md)）。
机器验证 v0.30 freeze-integrity：overall PASS + 147 PASS + 4 LIVING_FILE_BYDESIGN == 151（0 mismatch/
missing/err）+ drift_vs_v013 PASS 73/73 + drift_vs_v023 PASS 94/94（0 regression，13 net-new）+
frozen_release_index_copies PASS 4/4 + 公共 v0.15 锚点 `5dd43df6…` 在 v0.30 穷举锚点列表里再验证 PASS
（subsumes v0.29）+ 跨层独立重算 v0.15 锚点 / v0.30 输出 `lineage_audit_v030.json` / v0.23 审计基线 3 项全
match disk。30 版本 / 29 ACTIVE / 1 SUPERSEDED；canonical releases（v0.10 / v0.19）不变；纯元数据不改冻结层；
DETERMINISM PASS（5/5 字节一致）；leak 0。顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.31 视图。

**发布索引再生 + §L 整合层（v0.33）**：[`bench_v0.33/out/`](bench_v0.33/out/)
闭环 v0.32 下一步候选——把 v0.32（stronger-model gap-shrink 构造层，v1.x 候选）纳入下一整合层再生
RELEASE_INDEX（v0.32 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28 构造层先例），并把 v0.32
的「同特征换 softmax 缩 gap +0.2157 几乎闭合 → gap 是 weak-model artifact」结论回写进 v0.16 DATA_CARD
addendum 作为 **§L**（[`bench_v0.33/out/DATA_CARD_ADDENDUM_v0.33.md`](bench_v0.33/out/DATA_CARD_ADDENDUM_v0.33.md)）。
**§L 修订 v0.28 §J 的「内禀难度」定性**为更精确的两项分解：unseen-user gap = (weak-model artifact
**主项**——同 TF-IDF+tools 特征，最近质心换 softmax 即缩 +0.216 几乎闭合，fully-unseen 0.667→0.929；
若 gap 是特征空间内禀难度，同特征换模型不可能缩它) + (薄类源硬限**残项**——3 类 n≤4 单用户源，
按构造不可测未见用户泛化，仅更多用户/机器可解，正交于模型轴)。v0.28「更强模型」药方**方向正确但
严重低估效果**（以为边际改善，实际几乎闭合）；「更富特征」药方对**粗 meta 为负**（编码用户风格伤
跨用户泛化，需**语义级** embeddings/code-AST，LLM-gated）。闭合 v0.25→v0.26→v0.28→v0.32 完整闭环。
机器验证 v0.32 freeze-integrity：manifest PASS + v0.15 锚点 5dd43df6… + v0.26 split 逐位复用
（v0.26_split_files_match_manifest）+ CONTROL 复现 v0.26 0.588235（cross_check PASS）+ 3 个 split 文件
matches_v026_manifest + 4 个 v0.26 split 文件跨层独立重算 match v0.32 声明 AND v0.26 自身 frozen manifest
（证 v0.32 未误声明其冻结输入）+ v0.32 输出 gap_shrink.json match disk + gap_shrink.json self-agrees
manifest（Form A）。**32 版本 / 31 ACTIVE / 1 SUPERSEDED**；canonical releases（v0.10 / v0.19）不变；
纯元数据整合层，不改任何冻结 `out/`（v0.16/v0.20–v0.32 untouched）；DETERMINISM PASS（5/5 字节一致）；
leak 0。顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.33 视图。

**冻结 lineage 完整性 RE-sweep（v0.34，subsumes v0.30）**：[`bench_v0.34/out/lineage_audit_v034.json`](bench_v0.34/out/lineage_audit_v034.json)
把 v0.30 的全树审计（28 版本 / 151 锚点）重跑到现已冻结的 **32 版本 / 77 manifest / 170 锚点**（118 unique，
164 PASS + 6 LIVING_FILE_BYDESIGN，0 MISMATCH/MISSING）。新增 **drift_vs_v030 回归校验**——加载冻结
`bench_v0.30/out/lineage_audit_v030.json`，重验其 104 个 frozen 锚点仍 bit-intact（排除 4 个 v0.30 已标记的
顶层 living RELEASE_INDEX.md），证 v0.31–v0.33 build-out 未静默漂移任一冻结输入；10 net-new anchors since v0.30
（v0.31/v0.32/v0.33 新 provenance 链接：v0.32 `gap_shrink_manifest` → v0.26 split files / v0.15 锚点；v0.31/v0.33
consolidation → 各自 outputs）。**drift_vs_v030 传递式 subsumes v0.30 自身的 drift_vs_v023**——v0.30 锚点集 ⊇ v0.23
锚点集（v0.30 扫了含 v0.23 21 版本在内的 28 版本），重验 v0.30 锚点即重验 v0.23 锚点的超集，故显式 v0.23 recheck
省略无损。frozen per-version RELEASE_INDEX copies 交叉校验 **6/6 PASS**（现含 v0.22/v0.24/v0.27/v0.29/v0.31/v0.33
consolidation）。drift vs v0.13 manifest PASS 73/73。公共 v0.15 锚点 `5dd43df6…` 再验证 PASS。**意义**：v0.30 把
完整性证据推进到 v0.29；v0.34 推进到 v0.33，确保 v0.19 诊断发布 / v0.21 gap CI / v0.28 matched-count 实验 /
v0.29 §J / v0.32 gap-shrink 实验 / v0.33 §L 修订全部建立在 bit-intact 的冻结依赖图上。audit 层非整合层，不重算
RELEASE_INDEX（按 v0.30 先例推到下一整合层 v0.35）；纯元数据不改冻结层；DETERMINISM PASS（3/3 字节一致）；leak 0。

**发布索引再生 + §M 整合层（v0.35）**：[`bench_v0.35/out/`](bench_v0.35/out/)
闭环 v0.34 下一步候选——把 v0.34（冻结 lineage RE-sweep 构造/审计层，subsumes v0.30）纳入下一整合层再生
RELEASE_INDEX（v0.34 明确推到下一整合层，承 v0.21/v0.23/v0.30 审计层先例），并把 v0.34「全树 170 锚点 164 PASS
+ 6 LIVING + 0 broken + drift_vs_v030 104/104 0 回归 + 10 net-new provenance links since v0.30 全 bit-intact +
frozen per-version RELEASE_INDEX copies 6/6」回写进 v0.16 DATA_CARD addendum 作为 **§M**
（[`bench_v0.35/out/DATA_CARD_ADDENDUM_v0.35.md`](bench_v0.35/out/DATA_CARD_ADDENDUM_v0.35.md)）——记录
v0.23 → v0.30 → v0.34 完整性审计 cadence（每轮 build-out 后下一整合层 regen index 前先 RE-sweep）。
机器验证 v0.34 freeze-integrity：manifest PASS + audit overall_verdict PASS + 锚点计数 164 PASS / 6 LIVING /
0 MISMATCH / 0 MISSING over 170 锚点 [118 unique] / 77 manifest / 32 版本 + audit manifest 计数 (77) == manifest
自身声明 input 计数 (77) + drift_vs_v030 PASS 104/104 (4 living excluded, 0 regressions, net_new=10) +
drift_vs_v013 PASS 73/73 + frozen_release_index_copies PASS 6/6 (v0.22/v0.24/v0.27/v0.29/v0.31/v0.33 exact) +
跨层独立重算 v0.34 输出 `lineage_audit_v034.json` match 其自身 manifest 声明的 sha256 + v0.34 manifest 在盘 +
公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6。**意义**：v0.34 闭环了 v0.31–v0.33 build-out 打开的
回归窗口——证 build-out 未静默漂移任一冻结输入；§M 把这一完整性证据回写进 addendum，确保 v0.19 诊断发布 /
v0.21 gap CI / v0.28 matched-count 实验 / v0.29 §J / v0.32 gap-shrink 实验 / v0.33 §L 修订全部建立在 bit-intact
的冻结依赖图上。**34 版本 / 33 ACTIVE / 1 SUPERSEDED**（v0.17 by v0.19）；纯元数据整合层，不改任何冻结 `out/`
（v0.16/v0.20–v0.34 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0。顶层
[`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.35 视图。

**meta-feature scaling-artifact 消融（v0.36）**：[`bench_v0.36/out/`](bench_v0.36/out/)
诊断 v0.32 TREATMENT C 的**未解释负结果**（acc 0.313725 比 CONTROL 0.588235 还差，§L 读作「粗 meta 编码用户
风格伤跨用户泛化」但机制从未诊断）并**修正（不推翻）§L**。冻结 v0.26 split 逐位复用 v0.32，cross-check
CONTROL/B/C 逐位复现（0.588235 / 0.803922 / 0.313725）+ v0.32 `gap_shrink.json` on-disk match 其 manifest。
**特征量级分析**揭示根因：z-scored meta 块（行 L2 范数 2.23）是 L2-归一化 TF-IDF 块（范数 1.0）的 2.2×，
占拼接 rich 向量 norm² 的 **79.5%** → softmax 共享 lr/L2 下 6 个 meta 坐标主导 logits，**C 退化成 ~meta-only**
（C=0.3137 ≈ meta-only E=0.2941）。三消融证伪「粗 meta 本质为负」：TREATMENT D（meta 块重缩放匹配 TF-IDF
范数）acc=**0.5294** / TREATMENT F（整行 L2 归一）acc=**0.5490** 大幅回升（Δ vs C = +0.22 / +0.24）→ **C 的崩溃
是特征缩放伪影**；逐特征留一（max 0.4118 / min 0.3333，无一恢复到 control）证无单一毒性特征，是整块量级主导。
**修正 §L**：粗 meta 缩放后是「温和偏负」（D 0.5294 / F 0.5490 仍 < control 0.5882，不缩 gap）非「戏剧性为负」
（C −0.27）；**§L 主结论不变**——TREATMENT B（更强模型同特征）缩 gap +0.2157 → unseen-user gap 是 weak-model
artifact 非内禀难度；§L「需语义级特征（embeddings/code-AST）缩 gap」方向**成立**（D/F 也不缩 gap）。v0.36 只
精化 meta 子结论，不触碰 §L 的 weak-model-artifact 主轴。构造层非整合层不重算 RELEASE_INDEX（按 v0.32 先例推到
下一整合层）；纯冻结数据不改冻结层（v0.1–v0.35 untouched）；DETERMINISM PASS（7/7 字节一致）；leak 0。

**发布索引再生 + §N 整合层（v0.37）**：[`bench_v0.37/out/`](bench_v0.37/out/)
闭环 v0.36 下一步候选——把 v0.36（meta-feature scaling-artifact 消融构造层）纳入下一整合层再生 RELEASE_INDEX
（v0.36 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32 构造层先例），并把 v0.36「C 崩溃是特征缩放伪影
（meta 块占 rich norm² 79.5% 淹没 TF-IDF → C≈meta-only 0.2941；D/F 重缩放回升到 0.5294/0.5490 但不缩 gap）→
修正 §L「粗 meta 戏剧性为负」为「缩放后温和偏负」」回写进 v0.16 DATA_CARD addendum 作为 **§N**
（[`bench_v0.37/out/DATA_CARD_ADDENDUM_v0.37.md`](bench_v0.37/out/DATA_CARD_ADDENDUM_v0.37.md)）——记录
§I → §J → §L → §N 的 gap-attribution 精化 cadence（每层闭一个开放问题不动已结结论：§N 闭 §L 的机制问题，
保留 §L 主结论 + §J 已修订的 attribution）。**§N 修正 §L 的子结论**：粗 meta 缩放后「温和偏负」非「戏剧性为负」
（C 崩溃是缩放伪影）；**§L 主结论不变**（B 缩 gap +0.2157 → weak-model artifact）；**§L「需语义级特征缩 gap」方向成立**
（D/F 也不缩 gap）。机器验证 v0.36 freeze-integrity：manifest PASS + cross_check_vs_v032 PASS
（CONTROL/B/C 0.588235 / 0.803922 / 0.313725 逐位复现 v0.32）+ v0.32 `gap_shrink.json` on-disk sha match +
跨层独立重算 v0.36 输出 `meta_ablate.json` match 其自身 manifest 声明 + v0.32 `gap_shrink.json` match v0.36
provenance + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算 starts5dd43df6 + v0.26 split 4 文件 match v0.36 provenance。
**36 版本 / 35 ACTIVE / 1 SUPERSEDED**（v0.17 by v0.19）；canonical releases（v0.10 / v0.19）不变；纯元数据整合层，
不改任何冻结 `out/`（v0.16/v0.20–v0.36 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0。顶层
[`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.37 视图。

**gap-shrink bootstrap CI 构造层（v0.38）**：[`bench_v0.38/out/`](bench_v0.38/out/)
闭环 v0.32/v0.36 留的统计严谨性开放问题——§L/§N 核心结论（B 缩 gap +0.2157 → weak-model artifact）
是**点估计** on n=51（fully-unseen n=42），v0.32 自陈「高方差，方向可靠但 magnitude 不可靠」，
v0.21 只给过 v0.15 *诊断* split 的 bootstrap CI，**从未**给过 v0.26/v0.32 *unseen-user* gap 的 CI。
本层用**配对**非参数 percentile bootstrap（10000 次，`numpy default_rng(seed=0)`，对 CONTROL/B/C 用
**同一** resample 索引向量→配对对比正确——within-item contrast B−CONTROL/C−CONTROL 的正确 bootstrap，
非两独立 CI 之差），per-item correctness 从冻结 v0.26 answers + v0.32 submissions 重算（不重训、不换模型），
cross-check 复现 v0.32 全 n=51 + n=42 fully-unseen 9 个点估计（MATCH 9/9）。三个关键声明：
(1) **B 缩 gap over CONTROL** +0.2157：n=51 95% CI **[0.0980, 0.3529]** p(shrink≤0)=0.0005 /
n=42 CI **[0.1429, 0.4048]** p=0.0 → **显著**（两子集均排除 0），§L weak-model-artifact 主轴**对重采样稳健**
非小样本偶然；(2) **B 残余 gap vs headline** −0.0134：n=51 95% CI **[−0.1311, 0.0846]** p(gap≥0)=0.4478
→ **含 0** → 统计上闭合（B 把 gap 关到易类天花板 0.8174 噪声内）→ **强化 §L**（n=42 fully-unseen 子集
CI 正向偏移 [0.0160, 0.1826]，B 在最难项上更好，与 §L 薄类残项一致）；(3) **C 崩溃 vs CONTROL** −0.2745：
n=51 95% CI **[−0.4118, −0.1373]** p=0.0 → **显著**（排除 0），v0.36 缩放伪影诊断是**真实效应**非 n=51 错觉
→ **证实 §N**。**首个 unseen-user gap CI**。§L 主结论 + §N 子结论不变，二者现均 CI-backed。
freeze-integrity PASS（v0.15 锚点 5dd43df6 + v0.26 split 3 文件 + v0.32 submission+gap_shrink 4 文件
on-disk sha match v0.38 manifest）；DETERMINISM PASS（字节一致）；leak 0。构造层非整合层不重算
RELEASE_INDEX（按 v0.32/v0.36 先例推到下一整合层 v0.39）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。

**发布索引再生 + §O 整合层（v0.39）**：[`bench_v0.39/out/`](bench_v0.39/out/)
闭环 v0.38 下一步候选——把 v0.38（gap-shrink bootstrap CI 构造层）纳入下一整合层再生 RELEASE_INDEX
（v0.38 明确推到下一整合层，承 v0.21/v0.23/v0.25/v0.26/v0.28/v0.32/v0.36 构造层先例），并把 v0.38
「§L/§N 核心结论从点估计升级为置信区间——B 缩 gap 显著（n=51 + n=42）、B 残余 gap 含 0（统计上闭合，
强化 §L）、C 崩溃显著（v0.36 缩放伪影真实，证实 §N）；§L 主结论 + §N 子结论不变均 CI-backed；§L
「magnitude 不可靠」caveat 退役；首个 unseen-user gap CI」回写进 v0.16 DATA_CARD addendum 作为 **§O**
（[`bench_v0.39/out/DATA_CARD_ADDENDUM_v0.39.md`](bench_v0.39/out/DATA_CARD_ADDENDUM_v0.39.md)）——记录
§G → §O 的 rigor-closure cadence（每层闭一个开放问题不动已结结论：§O 闭 §L/§N 留的统计严谨性问题，
保留 §L 主结论 + §N 子结论）。**§O 不推翻 §L/§N，只升级其证据地位**：§L 主结论从点估计 → CI-backed
（对重采样稳健，退役「magnitude 不可靠」caveat）；§N 缩放伪影诊断确认为真实效应（非 n=51 错觉）。
机器验证 v0.38 freeze-integrity：manifest PASS + `all_match` true + cross_check_vs_v032 **MATCH (9/9 point
estimates)**（v0.38 manifest 字符串 + 输出 `gap_shrink_ci.json` 的 `cross_check_vs_v0.32.status` == MATCH，
9 项点估计在 rounding tolerance [1e-5] 内全复现——其中 `b_shrink_vs_v026` got 0.215686 vs v0.32-recorded
0.215687 为末位 float 舍入，v0.38 自身记为 MATCH 9/9）+ 跨层独立重算 v0.38 输出 `gap_shrink_ci.json` /
`gap_shrink_ci_characterization.md` match 其自身 manifest 声明 + 公共 v0.15 锚点 `5dd43df6…` 跨层独立重算
starts5dd43df6 + v0.26 split 3 文件 + v0.32 submission+gap_shrink 4 文件 match v0.38 inputs 声明。
**40 版本 / 39 ACTIVE / 1 SUPERSEDED**（v0.17 by v0.19）；canonical releases（v0.10 / v0.19）不变；纯元数据
整合层，不改任何冻结 `out/`（v0.16/v0.20–v0.40 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0。
顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.41 视图。下一构造层产新 manifest 锚点后，全树
lineage RE-sweep（v0.23→v0.30→v0.34→v0.40 cadence）再解锁为构造候选。

**per-class gap-shrink bootstrap CI 构造层（v0.42）**：[`bench_v0.42/out/`](bench_v0.42/out/)
闭环 v0.38 characterization 显式留的「per-class contrasts not computed」开放问题——v0.38 给了首个
**treatment-level**（headline）unseen-user gap CI（B 缩 gap over CONTROL 显著 [0.0980,0.3529] p=0.0005），
v0.42 把它**定位到具体类**。per-class paired bootstrap（10000 次，`numpy default_rng(seed=0)`，within-class
one shared resample vector；n≥MIN_CI_N=10 报 CI，n<10 仅点估计因 bootstrap 退化）。**`other`**（n=15/14）
B−CONTROL shrink +0.667/+0.714，95% CI **[0.4000,0.8667]/[0.5000,0.9286]**，p=0.0 → **两子集均显著**
——这正是 v0.18/v0.32 识别的 `other`↔`code_dev` disputed 边界（弱最近质心崩 CTRL 0.267/0.286，softmax
修好 B 0.933/1.000），§L weak-model-artifact **定位到此类**。**`code_dev`**（n=27/25，最大类）shrink
+0.0741/+0.0400，CI [0,0.1852]/[0,0.12] 含 0，ns——CTRL 已 0.889/0.960 在弱模型天花板，B 几无改进，是
「已解决」类非 gap 源。薄类（n≤4）仅点估计：`eda_virtuoso_schematic` n=4 CTRL=B=0（两模型全败，源硬限）、
`data_analysis` n=2、`file_ops` n=2、`eda_aether_layout` n=1——这是 v0.28/v0.32「薄类源硬限残项」的
per-class-CI 证据。**净结论**：+0.2157 headline shrink 几乎全来自 `other` 的边界修复，非均匀提升；
**精化（不推翻）§L/§O**——weak-model artifact 真实显著但其 locus 是 `other` disputed 边界非全类。
**下游含义**：语义级 treatment（LLM-gated）须帮 `code_dev` 突破弱模型天花板 + 解决薄类，而非仅重修
softmax 已修的 `other` 边界。两个 freeze-integrity cross-check：vs v0.32 9/9 点估计 MATCH + vs v0.38
headline n=51 B−CONTROL CI 逐位相等 [0.098039,0.352941]（证 v0.42 在与 v0.38 完全相同的 item 集上分区，
subsumes v0.38 headline）。freeze-integrity PASS（v0.15 锚点 5dd43df6 + 7/7 v0.26 split + v0.32 submission
on-disk sha match v0.32 manifest）；构造层非整合层不重算 RELEASE_INDEX（按 v0.32/v0.36/v0.38 先例推到
下一整合层）；产新 manifest 锚点→解锁延后的 lineage RE-sweep。DETERMINISM PASS（字节一致）、leak 0。

**发布索引再生 + DATA_CARD addendum §Q 整合层（v0.43）**：[`bench_v0.43/out/`](bench_v0.43/out/)
闭环 v0.42 下一步候选——把 v0.42（per-class gap-shrink bootstrap CI 构造层）纳入下一整合层再生
RELEASE_INDEX（v0.42 明确推到下一整合层，承 v0.32/v0.36/v0.38 构造层先例 + v0.38→v0.39 / v0.40→v0.41
构造→整合 cadence）+ 把 v0.42「§L weak-model-artifact 定位到 `other` disputed 边界（`other` n=15/14
shrink +0.667/+0.714 CI [0.4,0.867]/[0.5,0.929] p=0.0 两子集均显著，CI-backed）；`code_dev` n=27/25
最大类 CI 含 0 ns＝弱模型天花板非 gap 源；薄类 n<10 仅点估计＝v0.28/v0.32 薄类源硬限残项的 per-class-CI
证据」回写进 v0.16 DATA_CARD addendum 作为 **§Q**——**精化（不推翻）§L/§O**，把 gap-attribution cadence
（§I→§J→§L→§N→§O→**§Q per-class**）推到 per-class 闭环。机器验证 v0.42 freeze-integrity（manifest PASS +
cross-check vs v0.32 9/9 点估计 MATCH + cross-check vs v0.38 headline CI 逐位相等 [0.098039,0.352941] ＝同
item 集分区 + 跨层独立重算 v0.42 输出 gap_shrink_perclass_ci.json/characterization.md match 其自身 manifest +
公共 v0.15 锚点 5dd43df6 + v0.26 split 3 + v0.32 submission 4 on-disk sha match）。**42 版本 / 41 ACTIVE / 1 SUPERSEDED**；
纯元数据整合层，不改任何冻结 `out/`（v0.16/v0.20–v0.42 untouched）；DETERMINISM PASS（5/5 字节一致）；leak 0。
顶层 [`RELEASE_INDEX.md`](RELEASE_INDEX.md) 已再生为 v0.43 视图。v0.42 产新 manifest 锚点→下一全树
lineage RE-sweep（v0.23→v0.30→v0.34→v0.40 cadence）已解锁为构造候选。

**冻结 lineage 完整性 RE-sweep 构造层（v0.44）**：[`bench_v0.44/out/`](bench_v0.44/out/)
闭环 v0.43 下一步候选——v0.42 产新 manifest 锚点解锁了延后的全树 lineage RE-sweep（承
v0.23→v0.30→v0.34→v0.40 cadence）。把 v0.40 的全树审计（38 版本 / 89 manifest / 206 锚点 / 135 unique）
重跑到现已冻结的 **42 版本 / 97 manifest / 228 锚点 / 144 unique**（217 PASS + 11 LIVING_FILE_BYDESIGN，
0 MISMATCH/MISSING/ERR）。新增 **drift_vs_v040 回归校验**——加载冻结 `bench_v0.40/out/lineage_audit_v040.json`，
re-verify 其 135 unique 锚点的 126 frozen 子集（排除 9 个 by-design living 顶层 RELEASE_INDEX.md）→
126/126 仍 bit-intact，证 v0.41–v0.43 build-out 未静默漂移任一 v0.40 已校验的冻结输入。**9 net-new anchors**
since v0.40：v0.40 audit 自身（1，现成冻结输入）+ v0.41 consolidation outputs（3）+ v0.42 per-class CI
outputs（2）+ v0.43 consolidation outputs（3）。v0.42 的 *input* 锚点（v0.26 split / v0.32 gap_shrink+sub /
v0.32 manifest / v0.38 gap_shrink_ci / v0.15 anchor / v0.8 source_manifest）已被 v0.38 manifest 声明、由 v0.40
校验，故非 net-new，而在 drift_vs_v040 中重验证。**drift_vs_v040 传递式 subsumes v0.40 自身的 drift_vs_v034**
（v0.40 锚点集 ⊇ v0.34 锚点集 ⊇ v0.30 ⊇ v0.23），故显式 v0.34/v0.30/v0.23 recheck 省略无损——
v0.23→v0.30→v0.34→v0.40→**v0.44** RE-sweep cadence。frozen per-version RELEASE_INDEX copies 交叉校验
**11/11 PASS**（现含 v0.41/v0.43 consolidation，前 9 + 新 2）。drift vs v0.13 PASS 73/73（v0.1–v0.11 覆盖）。
公共 v0.15 锚点 5dd43df6… 再验证 PASS。审计/构造层非整合层，不重算 RELEASE_INDEX（按 v0.30/v0.34/v0.40
先例推到下一整合层，承 v0.38→v0.39 / v0.40→v0.41 / v0.42→v0.43 构造→整合 cadence）；纯元数据不改冻结层
（v0.1–v0.43 untouched）；产新 manifest 锚点（`lineage_audit_v044.json` sha256
`f9a7e77bd080175d69a7a9a754f0018ebba9440e65e930b5a3a1e35b05323cd9`）→下一全树 lineage RE-sweep 在下一整合层
吸收 v0.44 后解锁。DETERMINISM PASS（3/3 字节一致）、leak 0。

## 开放 gate（final v1.0 仅差 3 项，均非构造性）

| Gate | 状态 | 阻塞方 |
|---|---|---|
| 多机扇出（更多 cline 主机） | 阻塞 | `.75` 第50轮可达但 SSH 拒（ping 0% loss，Permission denied，连续 50 轮），待运维 |
| 活 LLM 第3标注者（2-of-3 多数表决） | 阻塞 | 无 live LLM endpoint（8092 MCP 仅 research 工具） |
| 对外正式发布 | 阻塞 | v1.0-rc1 内部优先，待运维签字 |

> 内部发布候选 constructively complete；以上均为外部扩展/对外发布 gate，不依赖 benchmark 构造。

---

## 全链路复现

```bash
# 逐比特复现 v0.1 → v0.6 全链路（零 /home 访问，默认 freeze-by-default）
cd designflow/bench_v0.1 && bash reproduce.sh        # 从冻结源重建派生产物
# 跨主机/跨时间可复现性验证
cd designflow/bench_v0.8 && bash reproduce.sh        # VERDICT PASS 40/40
# 逐比特可复现性（两份独立临时树并行 + sha256 比对）
cd designflow/bench_v0.7 && bash reproduce.sh        # VERDICT PASS 78/78
# 版本演进 diff（扫描已冻结 bench_v0.* out/ 产物）
cd designflow/bench_v0.13 && bash reproduce.sh       # manifest + 相邻 diff + HTML
# 统计严谨性（kappa + 选择偏倚审计 + bootstrap 95% CI）
cd designflow/bench_v0.14 && bash reproduce.sh       # agreement/bias/bootstrap + HTML
# 去偏 test split + 双标注者评分（闭环 v0.14 选择偏倚）
cd designflow/bench_v0.15 && bash reproduce.sh       # debiased split + dual-annotator eval + HTML
# DATA_CARD 增补层（层叠 v0.14/v0.15 统计证据到冻结 rc1 发布元数据，不改冻结 card）
cd designflow/bench_v0.16 && bash reproduce.sh       # DATA_CARD_ADDENDUM + enrich manifest + HTML
# 诊断发布 bundle（把 v0.15 去偏 split 打包为可对外发布的诊断 bundle + 双标注者评估接口）
cd designflow/bench_v0.17 && bash reproduce.sh       # diagnostic bundle + eval selftest + HTML
# disputed 项机理性刻画（解释 +0.51 gap 的机理：标签边界/特征位移/用户集中）
cd designflow/bench_v0.18 && bash reproduce.sh       # dispute_analysis + characterization + HTML
# 诊断 split 自包含发布包（v0.17 bundle + v0.18 characterization 融合 + blinded/answer-key + 独立 CLI 评估器）
cd designflow/bench_v0.19 && bash reproduce.sh       # diagnostic bundle + selftest baseline + HTML
# 发布整合 / 弃用层（机器验证 v0.17→v0.19 超集 + 顶层 RELEASE_INDEX 状态图）
cd designflow/bench_v0.20 && bash reproduce.sh       # deprecation_map + release_index + HTML
# 诊断 split bootstrap CI + gap 显著性层（对 v0.19 headline gap/robustness 加 95% CI + 显著性检验）
cd designflow/bench_v0.21 && bash reproduce.sh       # diagnostic_ci + manifest + HTML
# 发布索引再生 + DATA_CARD addendum §G 整合层（纳入 v0.21 + 回写 §G 到 v0.16 addendum）
cd designflow/bench_v0.22 && bash reproduce.sh       # release_index_v0.22 + §G + HTML
# 冻结 lineage 完整性全扫层（扫所有 manifest 的 sha256 锚点，对盘上文件逐个校验 + drift vs v0.13）
cd designflow/bench_v0.23 && bash reproduce.sh       # lineage_audit + manifest + HTML (DETERMINISM_CHECK=1 加自检)
# 发布索引再生 + DATA_CARD addendum §H 整合层（纳入 v0.23 + 回写 §H 到 v0.16 addendum）
cd designflow/bench_v0.24 && bash reproduce.sh       # release_index_v0.24 + §H + HTML
# per-user 公平性审计层（量化 v0.16 §E 用户集中局限 + LOUO user-robustness + per-class label-support concentration）
cd designflow/bench_v0.25 && bash reproduce.sh       # fairness_audit + characterization + HTML
# user-stratified re-split 构造层（闭环 v0.25：构造未见用户 held-out test，测泛化 gap=−0.2291）
cd designflow/bench_v0.26 && bash reproduce.sh       # user_resplit + new split jsonl + HTML
# 发布索引再生 + DATA_CARD addendum §I 整合层（纳入 v0.25+v0.26 + 回写 §I 到 v0.16 addendum）
cd designflow/bench_v0.27 && bash reproduce.sh       # release_index_v0.27 + §I + HTML
# user-balanced re-split 构造层（v1.x 候选，闭环 v0.26：多用户 train + 资格规则，2/9 类合格，dZ=−0.1176 证伪「多用户即缩 gap」）
cd designflow/bench_v0.28 && bash reproduce.sh       # user_balance + core split jsonl + matched controlled experiment + HTML
# 发布索引再生 + DATA_CARD addendum §J 整合层（纳入 v0.28 + 回写 §J 到 v0.16 addendum）
cd designflow/bench_v0.29 && bash reproduce.sh       # release_index_v0.29 + §J + HTML
# 冻结 lineage 完整性 RE-sweep（subsumes v0.23：28 版本 151 锚点全 PASS + drift_vs_v023 回归 + frozen RELEASE_INDEX 副本交叉校验 + 建模 v0.23 latent living-file bug）
cd designflow/bench_v0.30 && bash reproduce.sh       # lineage_audit_v030 + manifest + HTML (DETERMINISM_CHECK=1 加自检)
# 发布索引再生 + DATA_CARD addendum §K 整合层（纳入 v0.30 + 回写 §K 到 v0.16 addendum）
cd designflow/bench_v0.31 && bash reproduce.sh       # release_index_v0.31 + §K + HTML (DETERMINISM + freeze-integrity + leak 自检)
# stronger-model gap-shrink 构造层（闭环 v0.28 命名未测的「更强模型/更富特征」药方：冻结 v0.26 split 受控对比，softmax 缩 gap +0.2157 几乎闭合 → 修订 v0.28「内禀难度」结论）
cd designflow/bench_v0.32 && bash reproduce.sh       # gap_shrink + 3 submissions + HTML (DETERMINISM + freeze-integrity + cross-check + leak 自检)
# 发布索引再生 + DATA_CARD addendum §L 整合层（纳入 v0.32 + 回写 §L 到 v0.16 addendum——修订 v0.28 §J「内禀难度」为「weak-model artifact 主项 + 薄类源硬限残项」）
cd designflow/bench_v0.33 && bash reproduce.sh       # release_index_v0.33 + §L + HTML (DETERMINISM + freeze-integrity + leak 自检)
# 冻结 lineage 完整性 RE-sweep（subsumes v0.30：32 版本 170 锚点 164 PASS + 6 LIVING + drift_vs_v030 回归 104/104 + frozen RELEASE_INDEX 副本 6/6，传递式 subsumes v0.30 的 drift_vs_v023）
cd designflow/bench_v0.34 && bash reproduce.sh       # lineage_audit_v034 + manifest + HTML (DETERMINISM_CHECK=1 加自检)
# 发布索引再生 + DATA_CARD addendum §M 整合层（纳入 v0.34 + 回写 §M 到 v0.16 addendum——记录 v0.23→v0.30→v0.34 完整性审计 cadence）
cd designflow/bench_v0.35 && bash reproduce.sh       # release_index_v0.35 + §M + HTML (DETERMINISM + freeze-integrity v0.34 + leak 自检)
# meta-feature scaling-artifact 消融构造层（诊断 v0.32 TREATMENT C 负结果：meta 块占 rich norm² 79.5% → C≈meta-only；D 重缩放/F 整行归一回升 → 修正 §L「粗 meta 为负」为「缩放后温和偏负」，§L 主结论不变）
cd designflow/bench_v0.36 && bash reproduce.sh       # meta_ablate + 3 submissions + HTML (DETERMINISM + freeze-integrity v0.15+v0.32 + cross-check vs v0.32 + leak 自检)
# 发布索引再生 + DATA_CARD addendum §N 整合层（纳入 v0.36 + 回写 §N 到 v0.16 addendum——修正 §L「粗 meta 戏剧性为负」为「缩放伪影导致的负 + 缩放后温和偏负」，§L 主结论 + 缩 gap 方向不变）
cd designflow/bench_v0.37 && bash reproduce.sh       # release_index_v0.37 + §N + HTML (DETERMINISM + freeze-integrity v0.36 + leak 自检)
# gap-shrink bootstrap CI 构造层（把 v0.32 §L/§N 核心结论从点估计升级为置信区间：配对 percentile bootstrap n=51/n=42——B 缩 gap 显著 p=0.0005（§L 主轴对重采样稳健）；B 残余 gap 含 0（统计上闭合，强化 §L）；C 崩溃显著 p=0.0（v0.36 缩放伪影真实）；首个 unseen-user gap CI）
cd designflow/bench_v0.38 && bash reproduce.sh       # gap_shrink_ci + characterization + HTML (DETERMINISM + freeze-integrity v0.15+v0.32 + cross-check vs v0.32 + leak 自检)
# 发布索引再生 + DATA_CARD addendum §O 整合层（纳入 v0.38 + 回写 §O 到 v0.16 addendum——把 §L/§N 核心结论从点估计升级为置信区间：B 缩 gap 显著 / B 残余 gap 含 0 强化 §L / C 崩溃显著证实 §N，§L 主结论 + §N 子结论不变均 CI-backed，首个 unseen-user gap CI）
cd designflow/bench_v0.39 && bash reproduce.sh       # release_index_v0.39 + §O + HTML (DETERMINISM + freeze-integrity v0.38 + leak 自检)
# 冻结 lineage 完整性 RE-sweep（subsumes v0.34，传递式 v0.30/v0.23，构造层——闭环 v0.39 下一步候选：38 版本 89 manifest 206 锚点 197 PASS + 9 LIVING + drift_vs_v034 112/112 0 回归 + 17 net-new + frozen RELEASE_INDEX 副本 9/9）
cd designflow/bench_v0.40 && bash reproduce.sh       # lineage_audit_v040 + manifest + HTML (DETERMINISM + leak 自检)
# 发布索引再生 + DATA_CARD addendum §P 整合层（纳入 v0.40 + 回写 §P 到 v0.16 addendum——扩展 §M 覆盖窗口从 32→38 版本，不推翻任何前完整性结论：v0.23→v0.30→v0.34→v0.40 RE-sweep cadence）
cd designflow/bench_v0.41 && bash reproduce.sh       # release_index_v0.41 + §P + HTML (DETERMINISM + freeze-integrity v0.40 + leak 自检)
# per-class gap-shrink bootstrap CI 构造层（闭环 v0.38「per-class contrasts not computed」：per-class paired bootstrap 定位 §L weak-model-artifact——`other` n=15/14 shrink +0.667/+0.714 CI [0.4,0.867]/[0.5,0.929] p=0.0 两子集均显著（disputed 边界修复）；`code_dev` n=27/25 CI 含 0 ns（已在弱模型天花板）；薄类 n≤4 仅点估计=源硬限残项证据；cross-check vs v0.38 headline CI 逐位相等；精化 §L/§O 不推翻）
cd designflow/bench_v0.42 && bash reproduce.sh       # gap_shrink_perclass_ci + characterization + HTML (DETERMINISM + freeze-integrity v0.15+v0.32 + cross-check vs v0.32 + cross-check vs v0.38 + leak 自检)
# 发布索引再生 + DATA_CARD addendum §Q 整合层（纳入 v0.42 + 回写 §Q 到 v0.16 addendum——精化 §L/§O：§L weak-model-artifact 定位到 `other` disputed 边界 CI-backed，`code_dev` 弱模型天花板 ns，薄类源硬限点估计；gap-attribution cadence §I→§J→§L→§N→§O→§Q per-class 闭环）
cd designflow/bench_v0.43 && bash reproduce.sh       # release_index_v0.43 + §Q + HTML (DETERMINISM + freeze-integrity v0.42 + leak 自检)
# 冻结 lineage 完整性 RE-sweep（subsumes v0.40，传递式 v0.34/v0.30/v0.23，构造层——闭环 v0.43 下一步候选：42 版本 97 manifest 228 锚点 217 PASS + 11 LIVING + drift_vs_v040 126/126 0 回归 + 9 net-new + frozen RELEASE_INDEX 副本 11/11）
cd designflow/bench_v0.44 && bash reproduce.sh       # lineage_audit_v044 + manifest + HTML (DETERMINISM + leak 自检)
# 发布索引再生 + DATA_CARD addendum §R 整合层（纳入 v0.44 + 回写 §R 到 v0.16 addendum——扩展 §P 覆盖窗口从 38→42 版本，不推翻任何前完整性结论：v0.23→v0.30→v0.34→v0.40→v0.44 RE-sweep cadence 第 5 次全树审计）
cd designflow/bench_v0.45 && bash reproduce.sh       # release_index_v0.45 + §R + HTML (DETERMINISM + freeze-integrity v0.44 + leak 自检)
# 冻结 lineage 完整性 RE-sweep（subsumes v0.44，传递式 v0.40/v0.34/v0.30/v0.23，构造层——闭环 v0.45 下一步候选：44 版本 101 manifest 231 锚点 220 PASS + 11 LIVING + drift_vs_v044 133/133 0 回归 + 1 net-new + frozen RELEASE_INDEX 副本 11/11，v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 RE-sweep cadence 第 6 次全树审计）
cd designflow/bench_v0.46 && bash reproduce.sh       # lineage_audit_v046 + manifest + HTML (DETERMINISM + leak 自检)
# 发布索引再生 + DATA_CARD addendum §S 整合层（纳入 v0.46 + 回写 §S 到 v0.16 addendum——扩展 §R 覆盖窗口从 42→44 版本，不推翻任何前完整性结论：v0.23→v0.30→v0.34→v0.40→v0.44→v0.46 RE-sweep cadence 第 6 次全树审计）
cd designflow/bench_v0.47 && bash reproduce.sh       # release_index_v0.47 + §S + HTML (DETERMINISM + freeze-integrity v0.46 + leak 自检)
# 冻结 lineage 完整性 RE-sweep（subsumes v0.46，传递式 v0.44/v0.40/v0.34/v0.30/v0.23，构造层——闭环 v0.47 下一步候选：46 版本 105 manifest 234 锚点 223 PASS + 11 LIVING + drift_vs_v046 134/134 0 回归 + 1 net-new + frozen RELEASE_INDEX 副本 11/11，v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→v0.48 RE-sweep cadence 第 7 次全树审计）
cd designflow/bench_v0.48 && bash reproduce.sh       # lineage_audit_v048 + manifest + HTML (DETERMINISM + leak 自检)
# 发布索引再生 + DATA_CARD addendum §T 整合层（纳入 v0.48 + 回写 §T 到 v0.16 addendum——扩展 §S 覆盖窗口从 44→46 版本，不推翻任何前完整性结论：v0.23→v0.30→v0.34→v0.40→v0.44→v0.46→v0.48 RE-sweep cadence 第 7 次全树审计）
cd designflow/bench_v0.49 && bash reproduce.sh       # release_index_v0.49 + §T + HTML (DETERMINISM + freeze-integrity v0.48 + leak 自检)
```

所有 `reproduce.sh` 默认 `export PYTHONHASHSEED=0` 并尊重 `SOURCE_DATE_EPOCH`；
默认不扫 `/home`，仅 `RESCAN=1` 才走只读扩增路径（满足"可复现 + 可扩增"双重要求）。

---

## 限制

1. **单机来源**：当前仅本机 1 台 cline 主机，`user_hash` 跨 split 重叠（6 个）系单机局限，
   `global_id`/`session_id` disjointness 才是评估的有意义泄漏守卫（已 PASS）。
2. **2 标注者 gold**：v0.5 共识基于 v3_supervised + v4_rule 两视图，活 LLM 第3标注者待接入。
3. **样本持续增长但冻结快照固定**：`/home` 实时漂移（增/删），已发布 bundle 锚定
   快照 `a1cd058a…`；漂移不并入已发布产物，需 `RESCAN=1` 重新冻结才纳入。
4. **PII 历史**：git 历史 commit 含未脱敏人名/服务密码（共享仓不擅自 rewrite history），
   当前 HEAD 全产物 leak check 0 残留，待人工决断是否 force-push 重写。
5. **内部优先**：LICENSE 禁再识别、禁训练、内部优先；对外发布待签字。

---

## 出处与红线

- 工作目录：本仓库 `agent_workspace/designflow/`（绝对路径含本机账号，已脱敏省略）
- 任务书：`../BAIZE_DESIGNFLOW_BENCH_TASK.md`（只读指令，agent 禁改）
- 心跳：`../MEMORY_DESIGNFLOW.md`（每轮唤醒更新）
- 红线：SSH 目标机只读；未脱敏样本不入 git；主动扫描须书面授权；本线不用 GPU。
