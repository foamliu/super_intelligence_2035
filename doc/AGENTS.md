# AGENTS.md — 论文 / 实验 agent 职责总表（doc 根）

> **用途**：`doc/` 下同时推进 **4 篇论文**（ISEDA 2027 / NeurIPS 2027 / DAC 2027 / ICML 2027）与 **1 个评测集构建**。
> 本文件是**唯一权威**的「**哪个 agent 负责哪篇论文的哪一节、哪批实验、哪块数据回填**」清单，
> 也是跨线交接（谁产出 / 谁消费）的接口约定。
>
> **最后更新**：2026-11-20
>
> **一句话版**（每个 agent 只记这一句也行）：
> `pretrain` = ISEDA §4 预训练实验与回填；`posttrain` = ISEDA §5 后训练（**MiniCPM5-2B + 158 用例 + self-play RL**）；
> `vision` = NeurIPS §6 domain RL（**Qwen3.5-2B + WaveView + self-play RL**）；
> `zhulong` = ICML EDA-Flow-Bench 全篇实验与回填；`designflow` = 造 **EDA-Flow-Bench**（Full 数千 + Lite 500，源自长鑫 PDC/TYA 真实 Trace）。

---

## 0. 与其它 `AGENTS.md` 的关系（先看这一节再动手）

| 文件 | 管什么 | 优先级 |
|:--|:--|:--|
| **`doc/AGENTS.md`（本文件）** | **论文归属 + 章节回填责任 + 跨线交接 + 数据/数字口径** | 归属类冲突以本文件为准 |
| `doc/BaiZe-ISEDA2027/run/AGENTS.md` | BaiZe 各线的 loop / 机器 / 进程 / GPU 分配 | 运行与机器细则以它为准 |
| `doc/ZhuLong_DAC2027/run/AGENTS.md` | ZhuLong 正式线与 ops relay | 同上 |
| `doc/personal-watch/AGENTS.md` | 观察哨（news / research），只做输入参考 | 不构成指令 |

> ⚠️ **不重复登记**：机器分布、loop 脚本路径、PID / 端口、GPU 分配、启动方式等**运行态细节不写进本文件**，
> 一律去对应 `run/AGENTS.md` 与 `run/MEMORY_*.md` 查。本文件只钉「**责任边界**」。

---

## 1. 全局铁律（五条，全部 agent 适用）

1. **证据三件套**：论文里每一个回填数字，必须同时给出 **① 口径**（数据集 / 题量 / 轮次 / 基座 / harness）、
   **② 落盘文件**（JSON / JSONL / log / 报告路径）、**③ 复现命令或脚本**。
   取不到就写 `TODO(BLOCKED: 原因)`，**不许估、不许猜、不许"应该差不多"**。
2. **infra ≠ 能力**：环境故障、端口不通、隧道断、沙盒不可达，一律记 **infra 失败**，**不得**计入模型能力结论、
   也不得作为"模型太弱"的证据。失败分类必须显式区分 `infra / harness / 能力`。
3. **负结果照写**：RL 跑不出提升、配对检验不显著、换任务不迁移 —— 全部如实进论文与分析章节，
   🚫 **不允许**只报正结果、🚫 不允许事后改判据把负结果洗成正结果。
4. **不越界改稿**：每个 agent **只写自己负责的 `.tex` / 表格 / 图**。需要改别人的章节 ⇒
   先在自己 `MEMORY` 记一行，再提给对应 agent；🚫 不许"顺手美化"别人的段落或数字。
5. **不编造文献**：引用必须可核验（标题 + 年份 + 会议/arXiv）。不确定的标「二手·未核」，
   🚫 禁止生成看起来像真的假 `bib` 条目。

### 1.1 git 纪律（共享工作副本，血泪条款）

- 各线**共用同一个 NFS 工作副本**；陌生人未提交的改动 = **别线在途文件**。
- 🚫 **不 `git add -A`**：一律 `git add -- <明确路径>`（本线文件）。
- 🚫 **不 `git clean` / `git reset --hard` / 不删别线 stash**。
- 推送冲突常用解法：`git worktree add --detach /tmp/gitpush_<line> origin/main` → 只 add 本线路径 →
  commit → `git push origin HEAD:main`（**隔离 index，不动共享工作树**）。
- 提交信息前缀统一：`<agent>: <动作>`，例如
  `pretrain #2744: ...` · `posttrain wake645: ...` · `designflow shard B #934: ...`。

### 1.2 记忆与体积

- 各线 `MEMORY_*.md` 与任务书 **各自 ≤ 32 KB**（40 KB 硬上限），超限把**已闭合**整块原文搬进
  `ARCHIVE_*.md` / `daily-memories-*/` 并留 1 行指针。
- `WAITING:` 行**只在文件顶部出现一次**；正文与流水里不得再出现以 `WAITING:` 开头的行。

---

## 2. Agent 总表

| Agent | 目标论文（本地路径） | 负责章节 / 交付物 | 机器 | 任务书 | 记忆 |
|:--|:--|:--|:--|:--|:--|
| **pretrain** | `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/` | `ISEDA2027/4_llm_pretrain.tex` + 相关表/图 | `10.239.2.29` | `run/BAIZE_PRETRAIN_2B_TASK.md` | `run/MEMORY_PRETRAIN_2B.md` |
| **posttrain** | `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/` | `ISEDA2027/5_llm_posttrain.tex` + 相关表/图 | `10.252.32.17`（GPU 4-5） | `run/BAIZE_POSTTRAIN_TASK.md` | `run/MEMORY_POSTTRAIN.md` |
| **vision** | `doc/BaiZe-ISEDA2027/BaiZe-NeurIPS2027/` | `NeurIPS2027/6_domain_rl.tex` + 表 `tab:domain-rl` | `10.252.32.17`（GPU 6-7） | `run/BAIZE_VISION_TASK.md` | `run/MEMORY_VISION.md` |
| **zhulong** | `doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/` | 全篇实验数字（`sections/6_experiments.tex`、`7_analysis.tex`、`appendix/B_*`） | `10.251.36.15` | `run/ZHULONG_TASK.md` | `run/MEMORY_ZHULONG.md` |
| **designflow** | `doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/`（供数） | **评测集本体** EDA-Flow-Bench（Full + Lite 500） | `10.251.36.15`（4 个 shard） | `benchmark/BAIZE_DESIGNFLOW_BENCH_TASK_{,A,B,C,D}.md` | `benchmark/MEMORY_DESIGNFLOW*.md` |

> 补充：`doc/BaiZe-ISEDA2027/run/` 另有 **data / harness** 两条线（数据准备与 agentic harness 横评）。
> 它们**不为上述任一论文直接署名**，但为 pretrain/posttrain 供数与供 harness 结论 —— 需要时由对应论文线引用，
> 本文件不为其分配论文章节。
>
> 📁 **路径约定**：表中 `run/...` 与 `benchmark/...` 均相对各自项目根 ——
> BaiZe 线 = `doc/BaiZe-ISEDA2027/run/`；ZhuLong 线 = `doc/ZhuLong_DAC2027/run/` 与 `doc/ZhuLong_DAC2027/benchmark/`。
> 论文路径均写全，不再缩写。

---

## 3. pretrain

### 3.1 职责

**ISEDA 2027（LLM 主线）第 (i) 阶段：预训练。** 只对 `ISEDA2027/4_llm_pretrain.tex` 负责。

| 范围 | 具体内容 |
|:--|:--|
| ✅ 归你 | 架构选型对比数据（hybrid vs dense）、WSD 学习率调度与预算、S1/S2/Decay 三阶段数据配方与配比图、吞吐（tok/s）、长上下文（32K→64K→128K）阶梯结果、污染控制（13-gram 黑名单）口径、**L1/L2/L3 评测**（语言建模 / 常识推理 / 复杂推理 / Agentic 基准） |
| ❌ 不归你 | **L4 领域评测（EDA-Eval-PyAether 158 / EDA-Flow-Bench）→ 已移交 posttrain**（2026-11-12 用户令）；多模态章节（已迁 NeurIPS）；SFT / RL（posttrain） |

### 3.2 论文回填对象

- `ISEDA2027/4_llm_pretrain.tex`：`sec:arch-rationale` / `sec:framework` / `sec:llm-data` / `fig:data-mix` / 配置表 `tab:config`。
- `ISEDA2027/0_abstract.tex` 与 `9_conclusion.tex` 中与预训练相关的数字：**由 pretrain 提供证据**，
  但**改动需与 posttrain 对齐**（同一模型同一口径，避免两节数字打架）。

### 3.3 交付判据

1. 训练曲线 / 吞吐 / loss 的每个数字都能追到 **`.29` 上的训练日志或 eval JSON**（路径 + 行号/字段）。
2. 数据配比图与正文**逐百分比一致**（图中 74/19/7、40/40/20 等必须与 `sec:llm-data` 文本同源）。
3. 任何未跑完的格子写 `TODO(BLOCKED: 等 ckpt / 等 eval)`，🚫 不填推测值。

### 3.4 当前状态（2026-11-20，仅供排期参考，不写进论文）

- 主线训练在 `.29`，iter ≈ **262k / 700k**，step ≈ **7.0–7.1 s**，ETA ≈ **2026-12-25**。（2026-11-26 实测：iter 334k，step 7.4–8.1 s，视 eval 负载波动）
- **L1 评测节奏 = 每 10k step 一个点**（2026-11-26 用户令，覆盖原 2k 节奏；已评的 56 个 2k 点保留不删，报告需标注「≤328k 为 2k 密度、≥330k 起为 10k 密度」；下一个点 340k）。
- **pretrain ckpt 是 posttrain 正式训练的硬前置**（见 §4.4）。

---

## 4. posttrain

### 4.1 职责

**ISEDA 2027（LLM 主线）第 (ii) 阶段：领域适配。** 只对 `ISEDA2027/5_llm_posttrain.tex` 负责。

| 范围 | 具体内容 |
|:--|:--|
| ✅ 归你 | 领域退火（EDA 文本继续预训练）、SFT（agentic + 通用 + PyAether 合成）、RLVR/GRPO、奖励变体表 `tab:reward`、ACI 修复、冻结评测协议 `sec:posttrain-eval`、**L4 领域评测数字** |
| ❌ 不归你 | 预训练配方与吞吐（pretrain）；造题 / 写 `check.py`（designflow）；多模态波形（vision） |

### 4.2 用户令主线（2026-11-14 起，最高优先）

> **目标（一句话）**：把 **2B 基模在 EDA 脚本任务上的通过率，用后训练做显著提升**，
> 从而**探索出一条有效的后训练方法**。

**四步，一步一拍，每步单独测：**

1. **基模 = `MiniCPM5-2B`**（`doc/BaiZe-ISEDA2027/MiniCPM5-2B.config.json`）。
   2026-11-12 用户令已**解除对 BaiZe 预训练 ckpt 的依赖**——预训练没跑完也能开工。
2. **测基线**：`EDA-Eval-PyAether` **158 用例**，`Pass@1`，**≥5 run** 报 mean ± std。
3. **自适应**：SFT（agentic 轨迹）→ RL（可验证奖励，GRPO），**每步用同一套冻结协议重测**。
4. **交付判据**：**同测法下** post-SFT / post-RL 相对基线**显著提升**（**预注册判据 + 配对检验**，
   McNemar / paired bootstrap），并出中文 HTML 报告。

**Self-play / 环境内 RL 的口径**（这是"探索有效后训练方法"的核心手段）：

- RL 的 rollout 必须在**真实 EDA 环境**跑（沙盒 MCP + 真实工具链 + `check.py` 判分），
  不是离线打分的伪环境；奖励来自可验证执行结果。
- **反作弊常开**：每次 RL 运行都报 `cheat rate`；奖励若可被策略直接瞄准，必须保留 anti-cheat hook。
- **预注册**：臂（A/B/C/D）与判据**先写进 `MEMORY_POSTTRAIN.md` 再跑**，跑完不许改判据。

### 4.3 已知基线（数字必须带口径，混用即错）

| 口径 | 数字 | 说明 |
|:--|:--|:--|
| `.17` 起评（旧口径） | **3.04% ± 0.83%**（5 run） | 无 RAG / 无沙盒 MCP，**只能标注为「.17 口径」**，不可当能力结论 |
| **`36.15` + zhulong 口径**（现行） | **6.84% ± 6.12%**（n=5，`rca_status=CLEAN`） | 有 RAG + 沙盒 MCP + PreToolUse 白名单；vs 旧口径 McNemar p<0.001 |
| 大模型参照（**不可与 2B 比较**） | `deepseek-v4-pro-cloud` 82.1% ± 3.0% | 仅作"环境能给出高分"的对照 |

> ⚠️ **写论文时**：基线必须写清「哪个口径 + 几 run + 是否含 MCP/RAG」。跨口径比较 = 学术错误。

### 4.4 前置与阻塞

- **正式训练的前置 = pretrain 收敛 ckpt（ETA ≈ 2026-12-25）**；在此之前**用 MiniCPM5-2B 做方法探索**，
  这正是 §4.2 的意义：**在等 ckpt 的时间里把「有效方法」先探出来**。
- GPU：`.17` 的 **GPU 4-5**；🚫 不碰 GPU 0-3（root sglang）与 GPU 6-7（vision）。
- 与 vision **同机不同卡**：共用一份 repo、一份 NFS；git 协议见 §1.1。

### 4.5 论文回填对象

- `ISEDA2027/5_llm_posttrain.tex`：`sec:posttrain-anneal` / `sec:posttrain-sft` / `sec:posttrain-rl` /
  `tab:reward` / `sec:posttrain-eval`。
- 该文件现有 **TBD 占位** 必须由真实实验数据填掉；每条数字附 §1 的「证据三件套」。
- 🚫 **不许**把 `.17` 口径的 3.04% 直接写进论文当主结果（除非同时写清口径与局限）。

---

## 5. vision

### 5.1 职责

**NeurIPS 2027（多模态主线）第 (iii) 阶段：domain RL。** 只对 `BaiZe-NeurIPS2027/NeurIPS2027/6_domain_rl.tex` 负责。

| 范围 | 具体内容 |
|:--|:--|
| ✅ 归你 | 波形理解探针技能、reward 设计与任务重定义、RFT / GRPO 各轮（v5–v11）结果、`tab:domain-rl`、显著性检验、**WaveView 评测基线与提升**、CPU→GPU 迁移后的口径对齐 |
| ❌ 不归你 | 文本/脚本能力（posttrain）；**造题 / 改 `check.py` / 改题面**（designflow）；视觉编码器架构（论文 `4_vision_encoder.tex`） |

### 5.2 用户令主线（2026-11-19/20）

> **在前置条件（BaiZe-MLLM 训完）满足前，不等**：用 **`Qwen3.5-2B`（多模态）** 作为替身基模，
> 先在 **`EDA-Flow-Bench-WaveView`** 评测集上测基线，再用 **self-play（EDA 环境内 RL，专门提升波形图理解）**
> 争取**显著提升**，以**探索出有效的后训练方法**。

**必须遵守的评测形态（用户 2026-11-14 两次强调）：**

1. **不降级题目**：需要看图的题**保持原形态**，让"没有多模态能力"的系统**就该 fail**——
   这是**正确行为**，不是缺陷。
2. **agent 当 SUT**：测的是「**MLLM 作为 agent 系统一部分**」的增益，不是让 2B VLM 单打独斗；
   单模型臂只能标「工具天花板」。
3. **反作弊**：答案就在 PNG 里 ⇒ 禁止 OCR / PIL / base64 / 直连 VQA 端口绕行读图 / 按 `case_id` 反查源码。
   逐题扫 trace，命中即判 `cheat` 并单列，不计入 pass。
4. **同一把尺子**：同一批题、同一 `check.py`、同参数、顺序随机化；**唯一变量** = 有没有 / 用哪个 VQA 通道。

### 5.3 已知数字（必须带口径）

| 口径 | 数字 |
|:--|:--|
| WaveView 子集（**225 行**，可判分子集） | 见 `doc/BaiZe-ISEDA2027/run/vision/EDA-Eval-DesignFlow-WaveView.jsonl` |
| 全队列对比（**546 行**） | **V0 = 11.0% / V1 = 15.4% / V2 = 17.6%**（McNemar V0 vs V2 `p = 0.008`） |
| GPU LoRA 三阶段（held-out 合成波形问答 `n=30`） | base **0.60** → post-SFT（3-seed）**≥0.70** → RFT2 冷启动 **0.90** → post-GRPO **0.8667** |
| GRPO 配对检验 | RFT2 vs post-GRPO：`b=2, c=1, p=1.0` **不显著**（**如实写**：GRPO 自身增益 ≈ −3.3pp） |

> ⚠️ 上表两组口径（546 行真实题 vs `n=30` 合成题）**不可混比**；写论文必须分别标注。

### 5.4 论文回填对象

- `NeurIPS2027/6_domain_rl.tex`：正文 + `tab:domain-rl` + 「视觉真正能帮上忙的地方」段。
- 凡引用 `v5–v11` 的显著性结论，必须能追到实验存档 JSON（train/eval 种子不相交 ⇒ `cheat rate = 0`）。
- 新增 GPU 阶段结果要**明确标注**「CPU pilot 不迁移 / GPU 结果另计」，🚫 不许把 CPU 试点的相关性吹成 GPU 结论。

---

## 6. zhulong

### 6.1 职责

**ICML 2027 `EDA-Flow-Bench` 论文的全部实验与数据回填**（`doc/ZhuLong_DAC2027/EDA-Flow-Bench_ICML2027/`）。

| 范围 | 具体内容 |
|:--|:--|
| ✅ 归你 | 基线/各臂评测（`eval/run_batch.sh`）、Pass@1 与配对统计、token/时间成本、逐域逐模型结果、失败分类、消融矩阵、`appendix/B_additional_results.tex` 数字、编译验证 |
| ❌ 不归你 | **评测集构建 / 造题 / `check.py`**（designflow）；DAC 2027 ZhuLong 论文（本文件不覆盖该篇，见 `run/AGENTS.md`） |

### 6.2 运行与评测环境

- 评测仓：`/nasdata/app.e0031982/code/EDA-Flow-Bench/`（**独立仓**，不是本 repo 的论文树）。
- 启动（**必须登录 shell + PATH + `https_proxy`**，否则 `env: 'cline': No such file` 静默空转）：
  ```bash
  cd /nasdata/app.e0031982/code/EDA-Flow-Bench
  setsid bash eval/run_batch.sh --workers 16 > eval/run_<时间戳>.log 2>&1 < /dev/null &
  ```
  🚫 **逐字照 README / 用户命令跑，不自加 `--skip-done` 等参数**（曾因此跑出 422/500 口径不符）。
- 跑前自检三件：`~/.cline/data/settings/providers.json`（apiKey / model / baseUrl）、`command -v cline`、
  `https_proxy` 注入。

### 6.3 冻结口径（**不许改**）

| 宏 | 值 | 含义 |
|:--|:--|:--|
| `\LiteSet` | **500** | Lite 集任务数 |
| `\Neval` | **696** | 冻结快照 run 数（Full-set 描述性样本） |
| `\MzeroPass` | **10.0%** | M0 基线 Pass@1 |
| `\ScriptPass` | **76.5%** | 单脚本 EDA 基线 |
| `\FullScale` | `several thousand` | Full 集**只给定性描述**（🚫 正文不出现具体数字） |

- 用户基准：`51/484 = 10.5% Pass@1`（500 cases · 16 workers · ~2:57）；重跑应落 **~10% ± 2pp**。
- 历史 batch `run_batch_20261119_225802` 的 **2.37% 不算数**（起跑时 `providers.json` 仍是旧配置）——
  🚫 **不得引用该数字**，也不得据此下"模型弱"的结论。

### 6.4 交付判据

1. 每轮评测产出：`eval/status.jsonl` + summary log + 中文 HTML 报告（`report_edafb_lite500_<model>_eval_zh.html`）。
2. 回填论文的数字必须带「模型 / thinking / timeout / workers / 任务数 / run 数」六元组。
3. **编译必须 clean compile**：`rm -f main.aux main.bbl ...` → `pdflatex ×2 + bibtex + pdflatex`，
   判据 = round 3 的 `grep -ci 'undefined' main.log` = **0**、`grep -c '^!'` = **0**。
   🚫 不许只跑 1 轮 pdflatex 就报"编译通过"，🚫 不许靠旧 `.aux` 报"0 undefined"。

### 6.5 「体温计」连续循环（2026-11-26 用户令）

> 用户令：「安排 zhulong **不断起 lite-500+doubao-pro 评测**，做 designflow 的『体温计』，需要停止时我会下用户令」。
> 完整规格见 `run/ZHULONG_TASK.md` 顶部「🌡️ 体温计」节。

| 项 | 约定 |
|:--|:--|
| **固定量** | model=`doubao-seed-2.0-pro-cloud`（thinking low / `reasoning.enabled=false` / maxTokens=16384）、`workers=4`、500 cases、同一 harness ⇒ **唯一自变量 = EDA-Flow-Bench 的 repo state** |
| **轮级状态** | `CLEAN`（0 FUSE 且本轮期间无判分改动）/ `MIXED`（期间 designflow 改了判分 ⇒ 单列、**不入 3-run**）/ `VOID`（FUSE·额度·熔断 ⇒ 作废重跑，🚫 拼接） |
| **每轮必记** | `repo_commit`（EDA-Flow-Bench HEAD）+ 起跑前 `restart_hub` + strict canary 两证 + 身份四证 |
| **报告** | `run/reports/report_edafb_lite500_thermometer_zh.html`：滚动曲线（Pass@1 + repo_commit + 状态着色）+ 最近 3 个 `CLEAN` 轮 mean±std + `designflow/live_eval_changes.tsv` 时间线叠加 |
| **反馈 designflow** | 每轮 `run/reports/thermo_feedback_r<N>.md`（Pass@1 / 新增 ERROR·FAIL 的 `case_id` / 13 域通过率）→ A 分派到对应 shard |
| 🚫 **入论文** | 体温计轮**一律不入论文 3-run**；论文数字取「**同一 `repo_commit` 下 3 个 `CLEAN` 轮**」 |
| **停止** | **仅用户令**；🚫 agent 自行停 / 降频 / 减题；hub·额度·磁盘故障记 `infra`（铁律 2）并**保持循环** |

---

## 7. designflow

### 7.1 职责

**构建评测集 `EDA-Flow-Bench` 本体**（供 zhulong / vision / posttrain 使用）。
工作区：`doc/ZhuLong_DAC2027/benchmark/`；任务书：`BAIZE_DESIGNFLOW_BENCH_TASK.md` + 4 个 shard 版（`_A/_B/_C/_D`）。

| 范围 | 具体内容 |
|:--|:--|
| ✅ 归你 | 选题 → 从真实轨迹恢复任务形态 → 造 `assets/` → 写 `check.py`（≥8 断言）→ 配 PreToolUse 防泄题 hook → 台账登记 → 合入 Full / Lite |
| ❌ 不归你 | 跑模型评测出分（zhulong / vision / posttrain）；改别人的题面或判分口径 |

### 7.2 数据来源（用户令）

> **基于 EDA Agent「烛龙」在长鑫 PDC / TYA 团队上线后产生的真实 Trace 构建评测用例。**

- 每个用例必须能追到**一条真实会话 trace**（`1-trace-1-case` 互斥，防一料多题重复计分）。
- 选料走**台账正规渠道**（`ledger_*` / `*_dedup*.tsv` / `used_sessions_*`），🚫 不许自己另写一套排重逻辑。
- 跨 shard 去重：`benchmark/designflow/all_shard_sids.txt` / `excl_4shard_v2.txt` 为唯一去重源。

### 7.3 评测集结构（论文口径，**对齐 `\LiteSet=500`**）

| 层级 | 规模 | 用途 |
|:--|:--|:--|
| **Full** | **数千**（论文只写 `several thousand`，定性、持续增长） | 全量池，描述性快照 `\Neval=696` |
| **Lite** | **500**（严格筛选） | 主评测集，受限 token / 时间预算下的通用评测 |

**Lite 筛选原则**（写清即可，不追求"最优"）：

1. 覆盖全部 **13 个 domain**（`verification` 最易、`digital` 最难——分层不能全挑易题）；
2. 按**链长 / 工具链深度**分层（grounding depth 是本论文的核心自变量）；
3. **保留必须看图/多模态的题**——🚫 不因"被测系统做不了"而降级或剔除；
4. 可复跑：`assets/` 齐备、`check.py` 可离线执行、无外网依赖。

### 7.4 造题红线（用户 2026-11-14 · 凌驾于"好造"之上）

1. **用例形态 = 合格 DE 的工作形态**：DE 要看波形图、看眼图、看边沿，agent 也一样；
   🚫 不许把"看图"改成"读 `.rep` / CSV / Tcl"。
2. **自检一问**：出完题问「**一个不会看波形的 DE，能不能靠纯文本做对？**」——答案是"能" ⇒ 题被降级了，改回去。
3. 🚫 禁止：拆子步骤给提示、放宽阈值、把视觉要求改成数值要求、因为某系统 fail 就删题。
4. ✅ 唯一允许的帮助是**环境层面**（把真实 FSDB 导出成可离线复跑的样本、GUI 操作截图化），
   且**不得**让"不看图也能做对"。

### 7.5 并行与协作

- 4 个 shard（A / B / C / D）**并行造题**，各自写自己的 `MEMORY_DESIGNFLOW_<shard>.md` 与 `daily_<shard>_<date>.md`；
  🚫 不写别人的 MEMORY / daily / `discuss` 文件。
- **0-case 时进讨论区**：`benchmark/designflow/discuss/`（`README.md` 只读、`board.md` 仅 A 写、
  `A/B/C/D.md` 各写各的、`rounds/` 由 A 存档）。发言必须有**本域依据**，🚫 "我同意 / +1" 不算发言。
- 交付给下游时给出**清单**：`case_id / domain / k 断言数 / assets / check 路径 / 台账行`。
### 7.6 Lite-500 逐条「实跑评估」审视（2026-11-26 用户令）

> 用户令：「安排 designflow 4 agent 对 lite-500 中自己的 Case 进行审视，按需进行『实跑评估』改造」。
> 规格：`ZhuLong_DAC2027/benchmark/BAIZE_DESIGNFLOW_LIVE_EVAL_ORDER.md`；名册：`designflow/live_eval_review_<A|B|C|D>.tsv`（116/126/137/121 = 500）。

| 项 | 约定 |
|:--|:--|
| **谁做** | designflow 4 shard **各自只审自己的槽位**（`lite_health_all.tsv` 的 `owner_shard`）；A 兼汇总人（`designflow/live_eval_summary.md`） |
| **三分类** | `LIVE-REQ`（判分实质依赖真实工具产物 → **必须**升 `L2.live`）/ `LIVE-OPT`（可增强非必需）/ `LIVE-NA`（deliverable 本身是文本，保持 `[L0,L1]` 但须写本质问依据） |
| **新增判据** | **mock 桩体检**：自写假工具（`hspice_mock`/`finesim_mock`/伪 tcl 桩）若「按模板造对形状、物理量全错」也能判过 ⇒ 记 `LIVE-REQ`。旧 P4 关键词结论**不作数**，一律复验 |
| **改造手法** | 非侵入包装：原 `check`→`_check_static_impl` 一字不动 + `check_static` 收口 + 新增 `check_live` + `check()` 兼容 + `judge_layers` 加 `L2.live` + test sha 同步 |
| **只增不减** | 断言条数只增不减、阈值不放宽、条件不删；🚫 为「好跑」把 required 降 optional、🚫 把实跑断言包 `try/except: pass` |
| **实跑预算** | A/C/D **≤3 条/轮**；**B ≤6–8 条/轮**（2026-11-26 用户批准，前提：逐条独立自验 / 单轮 wall ≤90 min / `.75` 严格串行 / 单条失败降级不拖批） |
| **主辅关系** | **designflow 为主、zhulong 评测为辅**（2026-11-26 用户裁定）⇒ **不设等待**，随时可改判分；唯一额外动作 = 往 `designflow/live_eval_changes.tsv` 登记一行（`ts/shard/case_id/变更/jl_before/jl_after/commit/reason`） |
| **口径变更** | 任何 `judge_layers` 变更 = **口径变更**（改时登记即可，🚫 不需请示）；zhulong 每轮 run 记 `repo_commit`，跨改动的 run 标 `MIXED` **不入 3-run 统计**；🚫 shard 自行宣布新基线 |
| **infra 纪律** | `.75` 缺工具/许可/超时 ⇒ 记 `infra`（铁律 2），`LIVE-REQ` 降级 `LIVE-OPT` + 写 `BLOCKED: 缺 <具体项>`；🚫 写成能力结论、🚫 伪装 `LIVE-NA` |



---

## 8. 依赖与交接（谁产出 → 谁消费）

```
designflow ──(EDA-Flow-Bench 用例 + check.py)──┬─→ zhulong   ──(ICML 论文实验数字)
                                              ├─→ vision    ──(WaveView 子集 / 6_domain_rl 数字)
                                              └─→ posttrain ──(L4 领域评测口径)

pretrain ──(收敛 ckpt，ETA≈2026-12-25)───────────→ posttrain ──(正式 SFT / RL)
        └─(L1–L3 评测)───────────────────────────→ ISEDA §4

MiniCPM5-2B ─(替身基模，不等 pretrain)──────────→ posttrain §4.2
Qwen3.5-2B  ─(替身多模态基模，不等 MLLM)────────→ vision    §5.2
```

**交接硬规则：**

1. 下游**只读引用**上游产物，🚫 不改上游的题 / `check.py` / 判分口径。
2. 下游发现题目缺陷 ⇒ 记一行 + 交回 designflow；**不得自行改题后继续出分**。
3. 上游产物变更（换题、改断言）⇒ **必须通知下游重跑**，并在下游 `MEMORY` 记「口径变更」一行。
   **主辅关系（2026-11-26 用户裁定）**：designflow 是主线、zhulong 评测是辅线 ⇒ **上游改判分不等下游**；zhulong 每轮 run 记 `repo_commit`（EDA-Flow-Bench HEAD），跨改动的 run 标 `MIXED` 剔除出 3-run 统计，下一轮自然收敛。
4. 跨口径数字**永不混表**：`.17` vs `36.15`、CPU pilot vs GPU、546 行 vs `n=30`、Lite 500 vs Full 快照。

---

## 9. 论文回填规范（所有 agent 通用 checklist）

回填一类数字前，逐项打勾：

- [ ] **口径完整**：数据集 / 题量 / run 数 / 基座 / harness / 是否含 MCP·RAG / 时间戳。
- [ ] **落盘可追**：给出文件路径（+ 行号或 JSON 字段），不是"报告里写了"。
- [ ] **统计规范**：随机性结论用 **≥3 seed / ≥5 run**，报 mean ± std；对比用**配对检验**（McNemar / bootstrap CI）。
- [ ] **反作弊**：RL 与评测均报 `cheat rate`；`cheat rate > 0` 的结果**不得**当主结果。
- [ ] **负结果显式**：不显著就写"不显著"，不写"趋势向好"。
- [ ] **宏一致**：改数字优先改 `main.tex` 里的宏（`\LiteSet` / `\Neval` / `\MzeroPass` / `\ScriptPass`），
      而不是在正文里改硬编码数字（否则同一数字会分叉）。
- [ ] **编译验证**：clean compile，round 3 `grep -ci 'undefined'` = 0。
- [ ] **不越界**：只动自己那几节；跨节一致性由对应 agent 对齐。

---

## 10. 敏感 / 冻结清单（🚫 不得擅改）

| 项 | 位置 | 约束 |
|:--|:--|:--|
| `\LiteSet=500` / `\Neval=696` / `\MzeroPass=10.0\%` / `\ScriptPass=76.5\%` | `EDA-Flow-Bench_ICML2027/main.tex` | 改需用户/运维裁定，agent 自决不许动 |
| Full 集规模 | 同上（`\FullScale`） | 正文只写定性（`several thousand`），不写具体数 |
| 双盲匿名 | ICML 论文全篇 | pdftotext 自指泄漏 = 0；不承诺开源；无预注册声明 |
| `.17` 旧基线 3.04% | posttrain 报告 / 论文 | 只能用「旧口径」标签出现，不能当主结果 |
| 2.37% batch | zhulong 记忆 | **作废数字**，不得引用 |
| API Key / `providers.json` 凭证 | 全仓 | 🚫 不入库、不写进任务书 / MEMORY / 报告 / 日志 |
| `ops/` 中继目录 | 各 `run/ops/` | agent 只读，🚫 不手改 `inbox` / `outbox` |

---

## 11. 本文件的维护

- **谁改**：只有运维 / 用户可以在本文件**新增 agent、改论文归属、改交接接口**；
  各线 agent 可提"建议修订"，但**不得**自行改写职责边界。
- **何时改**：新增论文 / 新增 agent / 评测集冻结口径变化 / 交接链路变化。
- **改完必须同步**：对应 `run/AGENTS.md` 的任务书列 + 该线 `MEMORY` 的「职责边界」段（1 行指针即可）。
- **体量**：本文件 ≤ 32 KB；超限把「已退役 agent / 历史交接」搬进 `doc/AGENTS_ARCHIVE.md` 并留指针。

