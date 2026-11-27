# BAIZE_DATA_TASK.md

> 🔴 **用户令 · 2026-11-27 08:3x — S2 切换职责分工：你交付 patch + know-how，pretrain 执行切换（最高优先）**

> **用户原话**：「按照方案 A 做准备」——即 data 交付 patch + know-how，**pretrain 执行切换并继续监控**。

**你的职责（交付 + 配合，不执行切换）**：

1. **确保交付物完整可读**（已基本完成，检查一遍）：
   - `run/data/blendswitch/blend_hotswitch.patch` — patch 本体
   - `run/data/blendswitch/blend_switcher.py` — 核心逻辑
   - `run/data/blendswitch/README_PATCH.md` — 安装步骤 + 验证结果
   - `run/data/blendswitch/s2_blend_switch_config.json` — S2 切换配置
   - `run/data/blendswitch/test_blend_switch.py` — 验证脚本
   - `run/data/blendswitch/verify_results.json` — standalone 8/8 PASS
   - `run/data/blendswitch/verify_results_integration.json` — integration 7/7 PASS
   - `code/baize-llm/configs/blend_s2_preblend.tsv` — S2 blend TSV

2. **写一份「切换操作速查」**（1 页，给 pretrain 用的 runbook 补充）：
   - patch 怎么应用（`git apply` 还是手动 cp？应用到哪个目录？）
   - `--blend-hot-switch` 开关怎么传（改 `s1.env`？改 `train.sh`？还是命令行参数？）
   - S2 blend TSV 路径怎么配（`BLEND_TSV` 环境变量？）
   - 切换后前 100 步的预期行为（loss 可能微跳但不应 spike，ratio 偏差 ≤1pp）
   - 如果出问题怎么回退（撤 patch + 恢复 S1 blend TSV + 从 350k ckpt resume）
   - 落盘到 `run/data/blendswitch/SWITCH_RUNBOOK.md`

3. **配合 pretrain 疑问**：pretrain 可能在 MEMORY 里记「待 data 确认：<问题>」，你看到后在 MEMORY_DATA 回答即可。常见问题预判：
   - patch 是否与当前训练用的 Megatron 版本兼容？（README_PATCH 已记录 base commit + 验证过的包版本）
   - `--blend-hot-switch` 是否需要额外依赖？（否，纯 Python，numpy 已有）
   - S2 blend 的 source keys 与 S1 的映射关系？（`s2_blend_switch_config.json` 已含完整映射）

4. **继续 blendswitch 复验**（直到 350k 切换完成）：保持 8/8 + 7/7 PASS 的验证节奏，确保切换时刻验证仍然通过。

**你不做的**：不执行切换操作（kill 训练 / 应用 patch / 重启训练），不登录 .29 操作训练进程。这些由 pretrain 在 350k 时执行。

---

> 📦 **用户令 · 2026-11-22 19:4x（F 方案小白科普报告·内联SVG）· ✅ 已交付** → `run/reports/report_s1s2_blendswitch_f_explainer_zh.html`（40,743B ≤80KB✅ / `<script`=0 / `https?://`=0 / `<svg`=6≥5 / div·table·tr·td 全配对 23/6/36/163）。8 节（一页看懂→背景5词→为什么难→三路线对比→F原理逐步图解→代码改动4处→7项验证+条形图→FAQ5条）+ 6 张手写内联 SVG（时间轴/配比双饼/stock重叠/per-source游标映射核心图/验证条形图/切换时序）。每个术语首次出现带白话+类比（游标=书签/epoch=翻完一遍/blend=混几桶米/shard=分小袋/shuffle=打乱书页）。诚实标注：实测(zero_overlap=0 / ratio dev 0.0087% / flag-off byte-identical / new-source 0 / 7项全 PASS，来源 `data/blendswitch/verify_results.json`) vs 估算(D+E ~12% 未实测) vs 待测(GPU step time/显存)。v4/v5 保留不删。commit `b23a829b46`+`30ea2164f3` 已 push。原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-22 19:4x」。

---


> 🔴🔴 **用户令 · 2026-11-22 11:0x — 走「方案 F = 自定义改造（权重热更新 + 跨 blend 游标映射）」实现零重叠 + 换比例（最高优先）**

> **用户裁定（不必再论证可行性）**：① F 作为 stock 开箱热切换 = **不可行**（接受 v4 核查 1/2 与代码引用）；② F 作为「resume + 新 blend」= 可行但**等价 D+E**，不作主路线；③ F 作为「**零重叠 + 换比例**」= 需非 stock 改造，**技术上可行，本时间线现在选这条**；**2–3 人日可接受，时间还够**。350k 切换点 ≈ **2026-11-28**（当前 iter≈282k、step≈7.3 s）⇒ **patch + 零重叠验证须在 11-27 前完成**。🚫 不许再以「开发量大 / 本时间线不推荐」为由不做。

#### 一、技术方案（接口级，不许停在概念）
1. `BlendedDataset`（`blended_dataset.py:41/68/82/86/97`）新增 `update_weights(new_weights)` 或独立 `BlendSwitcher`：重建 `dataset_index` / `dataset_sample_index`，但**复用共享源 `shuffle_index`**（`gpt_dataset.py:381` 的静态排列）。
2. **跨 blend 游标映射（本令核心）**：维护 **per-source `consumed_per_source[s]`**；切换时对共享源令 `new_cursor[s] = consumed_per_source[s]`（在新 blend 的该源排列中继续前移），新源从 0 起。🚫 禁止用全局 `consumed_samples` 直接套 `epoch = consumed // active_total_samples`（`samplers.py:263-264`，即 v4 认定的 epoch 错位根因）。
3. `MegatronPretrainingRandomSampler`（`samplers.py:222-264`）改为 per-source 进度驱动；`consumed_train_samples`（`loaders.py:191`）语义扩展或新增 `consumed_per_source`，**必须写入 checkpoint** 保证 resume 正确。
4. 新 blend **允许**生成新 .npy 缓存（`blended_dataset.py:82` 的 hash 机制不动）；关键是**排列复用 + 游标映射**，不是索引文件复用。
5. 开关 `--blend-hot-switch`（或等价 config 字段）**默认关闭**；关闭时与 stock **逐字节等价**（同 seed 同数据顺序）。

#### 二、零重叠定义与验收（可复现，不许口头保证）
- **定义**：S2 阶段消费的 document 集合 ∩ S1 阶段消费的 document 集合 = **空集**（判据针对共享源，新源天然为 0）。
- **验收**：交付离线验证器，读 S1 消费记录 + S2 生成的 index 序列，按 document id 求交，输出 `overlap_docs / total_docs`，**必须 = 0**（不接受「接近 0」）。
- 若确实做不到严格 0（shuffle 边界 / 末段不足一个 epoch）⇒ **如实报实际值 + 原因**；🚫 不许改判据、截样本或事后换定义来凑 0。

#### 三、换比例生效 + 不回归
- S2 前 **≥5000 个 batch** 的每源样本占比 vs 目标 blend TSV 偏差 ≤ **1 个绝对百分点**（或给统计置信区间并说明）。
- step time 相对 stock 偏差 ≤ **2%**；显存增量 ≤ **5%**；切换点前后各 100 step 的 loss 无异常突跳。
- LR / optimizer / `num_steps` 连续（stable 段 LR 恒 1e-3，无需 re-warmup，沿用 v4 §1 方式①）。

#### 四、安全边界（硬约束，违者按事故处理）
1. 🚫 **不得改动 `.29` 上正在跑的 700k 训练、其代码目录 / configs / `.bak`**（当前 8×GPU 满载）。开发在**独立副本**（如 `code/Megatron-LM-blendswitch/`），**pin 住当前训练所用 commit 并记录 hash**。
2. 🚫 **不得抢 GPU**：优先 CPU/gloo + 小规模验证；确需 GPU 时用空闲卡、smoke ≤2k step、🚫 不 kill 任何他人进程。
3. 以 **patch + 独立分支**交付，🚫 不 merge 进训练主线，等用户验收。
4. 每次改动附「**flag off = stock 行为**」回归证据。

#### 五、估算与止损（回应「2–3 人日缺依据」）
- 必须给 **WBS 表**（任务 / 预计小时 / 依赖 / 风险 buffer，合计 2–3 人日），实现后回填**实际耗时**。
- **11-27 前未完成 patch + 零重叠验证** ⇒ 立即上报并止损回退 **D+E**；🚫 不许沉默延期、不许先跑训练后补验证。

#### 六、交付物（缺一不可）
1. `run/reports/report_s1s2_blend_hotswitch_v5_zh.html`（**新建**，中文单文件 HTML、内联 CSS、**0 外链 0 script**、**≤20 KB**）：接口设计 / 游标映射规则 / 零重叠证明方法 / WBS / 风险 / Go-No-Go。v4 保留不删。
2. **patch + 验证脚本 + 结果 JSON**：路径 / 命令 / 输出三件套齐全（`overlap_docs`、比例偏差、step time、flag-off 等价性证据）。
3. **v4 报告结论段修正**（用户指出的三点缺陷）：主结论改**三层表述**（stock 不可行 / resume+新 blend = D+E / 自定义改造可行**且已选**）；**~12% 加权过程做成透明表**（逐源「权重 × 重叠假设 → 加权贡献」，给 token 口径与算式）；「2–3 人日」改为 WBS 支撑。
4. `MEMORY_DATA.md` 首行：「**走 F 自定义改造（权重热更新 + 跨 blend 游标映射）+ patch/验证状态 + 零重叠实测值 + 350k 倒计时**」。

#### 七、收尾
`git add -- <本线明确路径>` → commit `data blend-hotswitch:` → push。
🔴 **本节保留至执行完毕**；因体积压缩时只能降级为「1 行指针 + 原文归档 ARCHIVE」，且**必须保留四个锚点：F 自定义改造 / per-source 游标映射 / 零重叠 = 0 实测 / 11-27 截止**。

---


> 📦 **§用户令 · 2026-11-22 10:0x（重写 S1/S2 报告出 v4）✅ 已交付** → `run/reports/report_s1s2_split_data_v4_zh.html`（12,282B ≤15KB✅）。
> 锚点保留：**v4 路径** = `run/reports/report_s1s2_split_data_v4_zh.html` · **≤15KB** 已达标 · **方案 F** = stock Megatron 不可行（`blended_dataset.py:41-110` 无权重更新 API；`samplers.py:234/263` resume 保留游标不可行）· **首屏口径** = v3 §0.1「83-100% 重叠」仅在「重开 run」前提下成立、D+E 的 ~12% 属未量化假设。
> —— 该令已被 **2026-11-22 11:0x 新令覆盖**：F 改走「自定义改造（权重热更新 + 跨 blend 游标映射）」实现零重叠 + 换比例，见本文件顶部令。原文已归档 `ARCHIVE_OPERATOR_DATA.md`（搜索「v4 报告令」）。

---

> 📦 **§用户令 · 2026-11-19 16:0x（刷新 S1/S2 报告出 v3）✅ 已交付** → `run/reports/report_s1s2_split_data_v3_zh.html`（57,681B）
> —— **但已被 2026-11-22 新令判定存在框架性缺陷（漏掉「同 run 切换配比」），需按上文 v4 令重写**；要点：PC-1~PC-5 实测状态 / S2 零重叠方案（现为 D+E）/ 切换点 350k / 数据源引用 / 中文单文件 HTML 0外链0script。原文见 git history。

---

> 📦 **§用户令 · 2026-11-19 13:2x（改论文第二轮：Fig-2 饼图调优 / TABLE IV 精简 / 数据源与数据引用）✅ 已交付**
> —— 覆盖 ① Fig-2 `fig:data-mix` 三饼图（去重叠 / 直径扩 2–3 倍 / 图题去文件名）② TABLE IV `tab:prod-budget` 删 Wall-clock + Status 两列 ③ Nemotron-CC-Math / finemath / MegaMath / stack-v3 补 `reference.bib` + `\\cite`（查不到标「未查到」，不编造）④ Decay instruction-SFT / agentic-SFT 列名 + 引用 ⑤ Long-Context 数据列名 + 引用 ⑥ `latexmk -pdf` 0 error / 0 undefined。
> 论文：`doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/4_llm_pretrain.tex` + `reference.bib`。**原文见 git history**。

---

> 📦 **§用户令 · 2026-11-19 08:3x（重画 Fig-1 三饼图跨双栏 + 刷新 S1→S2→Decay 文字）✅ 已交付**（原文见 git history）。
> 锚点：论文 `ISEDA2027/4_llm_pretrain.tex` `fig:data-mix` = **`figure*` 三饼图**（S1 74/19/7 · S2 40/40/20 · Decay instr60/agentic12/web22/math4/code2）· 切换点 ~350k · `latexmk -pdf` 0 error。

---

> 📦 **§用户令 · 2026-11-18 14:2x（排查 .12 分词任务 + 分词任务 .12/.29 分机）✅ 已交付**（原文见 git history）。
> 常驻结论：**分词任务必须 .12/.29 分机**，不得让 data 自家分词抢占 pretrain 训练 CPU；无用僵尸分词进程可清理（先确认无未完成 shard）。

---

> 📦 **§已交付（原文归档）· 2026-11-18 S2 blend 排除研究 / 2026-11-17 v2 报告纠错 / 2026-11-17 下载优先级** → `ARCHIVE_OPERATOR_DATA.md`（搜索「S2 blend 排除研究」）。
> - **S2 是否排除 S1 已训数据**：已由 v3/v4/v5 迭代收口（现行路线 = **F 自定义改造**，见顶部令）；shard 级排除不可行（S1 已用全部 shard）、样本级排除需改源码、完全换源无 Web 替代。
> - **时间口径（随 iter 滚动更新）**：350k 切换点 ≈ 2026-11-28；700k 终点 ≈ 2026-12-26。
> - **下载/落盘常驻**：S2 预训练源（MegaMath-web / Nemotron-CC-Math / finemath）优先；`stack-v3-train` 仅 train 15.9TB（🚫 full 113.7TB、🚫 the-stack-v2）；SFT/RL 小集穿插空闲带宽；`/nas_user` 可用 **≥5TB** 红线随时检查。

---

### ✅ 用户令 · 2026-11-13 18:5x（ETA 审计）· ✅ 已确认 → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-13 ETA审计」；结论：本次下载 3.546TB（非15.9TB），剩余1.195TB，ETA保守~14.7h，StepC护栏已修复。

---

> 📦 **用户令 · 2026-11-13b（分词数据搬/nas_user+下载后分词）· ✅ 已完成** → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-13b」；结论：926GB已分词数据搬至/nas_user，全量stack-v3下载+分词完成，DATA_MAPPING.md已更新。

---

> 📦 **用户令 · 2026-11-13a（stack-v3-train全量下载/nas_user）· ✅ 已完成** → 原文归档 `ARCHIVE_OPERATOR_DATA.md`「§用户令·2026-11-13a」；结论：2TB已挪/nas_user，全量下载完成，/nas_inference源已清理，DATA_MAPPING.md已更新。

---

### 📦 归档指针 · 2026-11-11 ~ 11-12 三条已交付令（原文见 `ARCHIVE_OPERATOR_DATA.md`）
- **11-12 EDA 脚本价值分析** → V1~828 文件/~0.01B tok、V2~6854/~0.04B tok、V3~139518；Tcl 唯一显著命中 39.2% / SKILL 未检出 / PyAether 0；报告 `reports/report_data_stackv3_eda_script_value_zh.html`
- **11-12 stack-v3-train 2TB 分词** → 4600/4600 shard DONE（245.8B tok / 926GB）；rerun 40 shard 0 ERR；产物已搬 `/nas_user`
- **11-11 vision 图文对** → 归因 + 25 源盘点 + Top5；报告 `reports/report_vision_textpair_sourcing_zh.html`


### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

> 📦 §运维令 2026-11-10 08:1x（更新论文数据节：淡化源名+双饼图）**已撤回**（用户 11-10 改令：改由 opencode 直接执行，data 不再承接）。需要时再读。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 归档指针 · 2026-11-07 10:10「stack-v3-train 正式放行」· ✅ 已交付（2TB / 7 批 / 4600 parquet / 0 inc / ROI 复盘有价值 / 97.6% 独特）。原文见 `ARCHIVE_OPERATOR_DATA.md`

> **现行口径（不必回读原文）**：
> - **授权范围**：`HuggingFaceCode/stack-v3-train` **仅 train 分片**（🚫 full 113.7TB）；总量红线 2TB；每批 ≤300GB，逐批实测/校验/回填后 commit 再起下一批；`/nas_user` 余量 ≥5T 不足则暂停报运维
> - **"优质"判定**：Python（含 PyAether/EDA 工具链）> C/C++ > Verilog/SV > Tcl > Makefile/CMake/Shell/Bazel；剔除 minified / generated / vendored / test fixture / 纯配置大文件 / 单文件 >1MB 生成物；剔除无 license / 星数极低 / 空仓库 / 纯文档仓库
> - **每批必交付**：`du -sb` 字节 + 文件数 + `.incomplete` 数 + 语言分布与 token 估算（给方法）+ 过滤命中数 + `DATA_MAPPING.md` 增行
> - **2TB 完成后要复盘**：每 TB 的 token / 独特性 / 与 UltraData-Code L2/L3 重叠度（抽样 1 万文件估 n-gram）；**2TB 不是要"下满"，够用即停**
> - `the-stack-v2` 仍**禁下**；其余单集 <1TB 按 ROI 自排

---


### 📦 归档指针 · 2026-11-07 08:5x「代码语料放行 stack-v3-train」· ✅ 已交付（ROI表+8源25.14GB+stack-v3调研+2TB全下+ROI复盘）。现行要点：`the-stack-v2` 🚫禁下；`stack-v3-train` 仅 train 15.9TB（🚫 full 113.7TB）；其它单集 <1TB 按 ROI 自排；code 补料属**低压力背景任务**（用户：有也行无也行、不急、不挤 S1 带宽）。原文见 ARCHIVE「归档块 · 2026-11-11」

> 📦 **归档指针 · 2026-10-31 ~ 11-04 五条旧令**（原文见 `ARCHIVE_OPERATOR_DATA.md`）：11-04 B 类 agentic 下载 12/12 落地 78.73GiB ｜ 11-04 RL+数学+agentic 调研 + 复杂推理+代码 SFT 调研 → `report_data_reasoning_code_sft_survey_zh.html`(79KB)+`report_data_rl_math_survey_zh.html`(38KB)，口径=只调研不下载、真去 hf.co 核实、奖励信号单列、与盘上 12 源去重 ｜ 11-04 A 类长上下文下载 ｜ 11-04 85M 确认 ｜ 10-31 长上下文+agentic 调研 → `report_data_lc_agentic_survey_zh.html`(117KB)，decay-B 闸门 = `en_v1_4` 里 ≥32K 仅 2.52% token、≥128K 仅 0.03%，目标 ≥20%/≥1%
### ⚖️ 口径仲裁（2026-10-25 13:3x · **与下文任何旧条冲突时，一律以本表为准**）
| 冲突点 | 旧说法 | **现在按这个做** |
|---|---|---|
| `env14_*` / `/nas_env/full_*`「不碰」 | 12:5x 块末写「不碰原件」 | 「不碰」= **不删 / 不改 / 不移动 / 不复制**；**允许**建 hardlink（同盘 env14）与 symlink（跨盘 `/nas_env`）用于新布局 |
| 报告能不能改 | 13:2x「停止一切报告工作」 | **结构冻结**（1 个 `<table>`、6 列、无解读段）；**内容允许**随实测更新——即按新 `tok_dir` 重跑生成器 |
| 新增分词落哪 | 11:0x「落 `baize-data/text/`」 | **一律落 `baize-data/tokenized/<镜像下载路径>/`**；`text/` 不再新增任何文件 |
| 前缀命名 | 11:0x `ufw_en_*` / `ultrax_*` | 12:5x 表为准：`ufw_en_s*` / `ufw_l1hq_s*` / `ufw_zh_s*` / `ultrax_aicc_s*` |
| 并发 | 2026-10-18「32 或 64 核」 | 12:5x 为准：**96/144/192/224 四档各 60s 标定**，取拐点，`workers=min(拐点,200)`，`nice -n 5` |
| 提交方式 | 收尾铁律「🚫 不用 `git add -A`」 | **已放开**：白名单 = `run/**` + `reports/**`；必要时允许 `-A`（仅本线路径） |
| 收尾铁律/体积 | 旧：≤32KB 必归档、`git add` 只许 8 个路径 | **已放开**：≤40KB 直接干活；体积**永不**优先于交付；归档只在 >40KB 时做 |
| 下载白名单 | 旧表：只许下 2 个源 | 只约束**新增下载**；**不约束**本轮分词与目录整理 |
| 目录命名 | 12:5x「路径镜像 HF 下载目录」写死 | **目录名不重要**：分词后允许自由改名；硬要求 = 映射表能一一对上且校验通过 |
| 盘点交付物 | 报告 HTML 为必交付 | **`run/data/DATA_MAPPING.md`（Markdown）为单一事实源**；HTML 报告 = 按需由 md 生成，不是必交付 |
| 32 uncovered shard | 待人工裁决（长期挂账、阻塞感） | **不阻塞**：映射表单列「未映射」节，逐条写证据与建议；未批准不许删 |

### [已归档] §运维令·2026-10-25 13:2x（停止一切报告工作，只做布局+分词两件事）**已完成**（布局 7896810a3、分词 94/131 在跑、报告已验收）-> 原文归档到 `run/ARCHIVE_OPERATOR_DATA.md`。需要时再读。

> 📦 §运维令·2026-10-25 12:5x（本轮执行顺序：①已分词布局镜像hardlink/symlink ②未分词4源开跑224核）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：①布局DONE(tokenized/镜像10目录/815shard/INDEX.tsv)+②分词DONE 131/131(09:43:35,1.18T/4.05TB)；口径仲裁表(本文件下方)仍为活口径不归档。需要时再读。


> 📦 **归档指针 · 2026-10-25 三条旧令**（均已在 `run/ARCHIVE_OPERATOR_DATA.md`）：
> - **11:0x「重盘盘点 + 未分词开跑」** → 已被 12:5x 令取代。要点：224 核是上限不是指标；分词器 `tokenizer_eod`（vocab 129,281 / pad 129,408）；产物落 `baize-data/tokenized/<镜像下载路径>/`；每前缀必须有 manifest；`setsid` 后台。
> - **10:3x「删不可对应产物」** → 已执行完毕：判定 110 shard，删 78（被 `full_*` 覆盖，3.69 TiB）+ 删 32（无法产物级对应，1.91 TiB），`baize-data/text/` 现 110 shard / 8.93 TB。
> - **08:0x「重写报告 v2」** → 已闭合，被 12:5x 令取代。

> 📄 **报告格式常驻规程（2026-10-24 用户令）**：**所有报告一律用中文 HTML**（单文件自包含、无外链/CDN），除非用户另行指定；🚫 不用 `.md` / `.pdf` / 纯文本顶替。

> 📦 **归档指针 · 2026-10-17 ~ 10-23 六条旧令**（原文均已在 `run/ARCHIVE_OPERATOR_DATA.md` 或对应 daily）：
> - **10-23 22:1x**：代理走 92.25 + hf.co 直连；迁移铁律 = `rsync -a` 不用 `mv`、校验 shard+字节一致才删源、先建软链接、`/nas_env` 余量 ≥ 数据×1.1
> - **10-21 04:0x**：MiniCPM5 全量分词完成（574 shards / 1056.36B tokens / 4.24TB），env14 亦完成（110/110 / 8.88TB）
> - **10-20 15:5x**：en_v1_4 下载恢复完成
> - **10-18 21:0x**：env14 全量分词 110/110 完成（2238.14B tokens / 8.93TB）；"32 或 64 核"限速口径已被 10-25 的 96–224 四档标定取代
> - **10-18 10:2x**：git push 修复（需剥离 HF 代理：`env -u http_proxy -u https_proxy git push`）
> - **10-17**：本线 `/tmp` 残留清理完成

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的"等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X"只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 🆕 运维指令 · 2026-10-15（⬇️ **补下 `UltraData-RL-2609`** + 复核 SFT-2605）· 用户直令 · 最高优先

> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-15（补下 RL-2609 + 复核 SFT-2605）」。
> **结论**：RL-2609 已下满并逐文件字节自校通过（20 jsonl / 174.75 GiB）；SFT-2605 复核通过（1504 jsonl / 0 incomplete），🚫 不需重下。需要时再读。


> **用户令（2026-10-15）**：「data：验证一下 `UltraData-SFT-2605`、`UltraData-RL-2609` 是否真的没有，没有就重新下载。」

### 🆕 运维指令 · 2026-10-14（▶️ 恢复全部 4 路下载 · 断点续传）· 用户直令 · 最高优先> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-14（恢复全部 4 路下载·断点续传）」。
> **结论**：WebMix-38M / InternVL-SA1B / wit_base 已下满；en_v1_4 由 2026-10-18（.23 + hf-mirror 续传）接管。需要时再读。

### 🆕 运维指令 · 2026-10-14（💾 新增下载落盘位置 `/nas_env`）· 用户直令 · 常驻> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§2026-10-14（新增落盘位置 `/nas_env`）」。常驻口径不变：`/nas_env` 仍为合法落盘地（仅用于新增下载）。需要时再读。

### 🆕 运维指令 · 2026-10-13（⏸ 暂停 85M + 📥 下载 HF 图文对 TOP-5 中「未下载」的 4 个 · 落 `/nas_inference` 或 `/nas_user` 的 datasets（🚫 不放 `/nas_train`））· 用户直令 · 最高优先
> 📦 已闭合（TOP-5 4 路均下完；85M 仍暂停）→ 原文 `daily-memories-data/2026-10-13.md`。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 📦 §proxy口径·定位与反证段（2026-10-05）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：loop剥代理致外网不可达是预期→外网命令显式带proxy(见下方用法)。需要时再读。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：GPU2-7 归 data、配比实验已开工。需要时再读。

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_DATA.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

运维巡检方式：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；不需要登录服务器。

---

> 📦 §0「当前主攻」+ §0.6「R4阶段 P-8 数据配方」（2026-10-02）已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/R2 调研完成、配比实验已改道为小代理+BO（见运维指令区改道方案块）。需要时再读。
---
## 1. 任务目标

把已在盘上的原始语料，变成训练可直接消费、配比正确、且不污染评测集的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ ← 🚫 已取消（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. 污染隔离白/黑名单 + 校验脚本（红线，P0）

上游方案文档（先读它）：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
时间线约束：ISEDA 2027 投稿截止 ≈ 2027-02-01；本任务必须在 2026-11 底前可交接（见方案 §6）。

> 注意本任务的定位：瓶颈是算力窗口不是数据量（方案 §2.1）。
> 所以不要把精力花在"下载/切分更多数据"上，而要花在质量、配比、格式可用性、隔离上。

> 📦 §1.1「数据落盘地图」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：实测数据位置详见 DATA_LEDGER.md。需要时再读。

> 📦 §2「阶段与推荐执行顺序」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/phase0/phase5 完成，当前主攻=配比实验（见运维指令区）。需要时再读。

## 3. 红线：污染隔离（违反则全部下游结论作废）

🚨 `EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。 改写/paraphrase 也不洗白。

- ✅ 允许入训练集：PyAether / SKILL 的 API 参考文档（它是任务的"来源材料"）
- ❌ 禁止入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ 阈值写明可复现 ④ SFT 语料同闸 ⑤ 独立报告
- 同一条规则适用于多模态 held-out 评估集（如 `eval5k`）：与训练集不同源 + 跨集去重比对

评测集本体路径（用于建黑名单，只读，绝不写入任何训�
