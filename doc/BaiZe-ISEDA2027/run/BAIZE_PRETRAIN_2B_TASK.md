# BAIZE_PRETRAIN_2B_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_PRETRAIN.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_PRETRAIN_2B.md` / `daily-memories/` / `EXPERIMENTS_*`）。本节为「无」时按下方 Round 2 默认顺序推进。

### 🆕 运维指令 · 2026-10-05（深夜 · ✅ **sglang 可用 → 用 `.29` GPU0–1 做「BaiZe（Mamba2-hybrid 2B） vs MiniCPM5-2B」推理对比（框架 = sglang）**）· 高优先 · **已批准**

> **用户拍板（2026-10-05 深夜）**：「既然 sglang ✅ 可用，那可以用 `.29` **GPU0–1 空**进行对比测试（**推理延迟、吞吐量、显存占用**等）。」
> ⚠️ **口径更正（运维 2026-10-05 深夜）**：本项**不是「mcore vs sglang」的栈对比** —— 而是 **sglang 作为（同一个）推理框架，对比两个架构**：**BaiZe = Mamba2-hybrid 2.220B** ⚔ **MiniCPM5-2B = dense GPT 2.512B**。

**目标**：用**生产推理栈 sglang** 复测/量化**项目核心论点** —— **Mamba2-hybrid（BaiZe）相对 MiniCPM5-2B 在长上下文下的推理优势**（Round 1 S3 曾在 mcore 上量到 decode **10.3×**，但那是**旧 ckpt（已删）+ 非生产栈**，须在 sglang 上重新量一遍并标注口径）。

**① 对象（两个已核验在位的 ckpt，均在 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`）**

| 模型 | = | ckpt | 参数 |
|:--|:--|:--|:--|
| **BaiZe（本项目）** | Mamba2-hybrid | **`p3_hybrid/iter_0005000`** | 2.220B |
| **对照** | MiniCPM5-2B（dense GPT） | **`p3_dense/iter_0005000`** | 2.512B |

- **前置（真正的坑）**：两者都要 **mcore distcp → HF**：hybrid → **`nemotron_h`**（sglang 原生支持）；dense → `gpt`/`minicpm` 兼容结构。**手写权重映射**，脚本隔离在独立目录，🚫 不动共享 `py310`。
- ⚠️ **口径标注**：P-3 = 5000 步 / 123M token（与已删的 S3=1000 步/24.6M 不同）⇒ **旧 10.3× 与本轮数字不得直接相减**，两者并列、各标栈与权重。

**② 测试矩阵（同一 sglang、两模型逐格对齐）**：context ∈ {4K,16K,64K,128K}（可加 256K）× batch ∈ {1,8}（**OOM 就如实记 OOM，🚫 不许偷偷降 context**），gen_len=64。

**③ 采集指标（每格）**：**TTFT · prefill 吞吐(tok/s) · decode 吞吐(tok/s) · 端到端延迟 · 峰值显存**；**逐格算 hybrid vs dense 的比值**；并与 P-9.10② 的 **mcore eager 下界**并列成一张表（标注框架差异）。

**④ 关键问题**
- **decode 优势是否随 ctx 增长**（SSM O(n) vs attn O(n²)）？—— Round 1 在 mcore 上量到 ~10.3×，**sglang 生产栈下是多少**？（P-9.10② eager 下因 launch 开销只量到 ~1.6× 恒定、H2 未翻正 ⇒ **生产栈正是用来验证/翻正这一点**）
- **显存**：hybrid 的 SSM state 恒定、attn KV 随 ctx 线性 ⇒ 长 ctx 显存优势多大？
- prefill 长 ctx 加速比。

**⑤ 边界与铁律**
- **只用 `.29` GPU0–1**（GPU2–7 是 data 配比实验）；🚫 **不 kill data 进程**；要更多卡按 `run/GPU29_ALLOC.md`「申请区」走。
- **不改 P-5b recipe / 不回训 / 不存新训练 ckpt**；🚫 **绝不 kill watchdog loop**。
- sglang 起服**必须用 `vllm` conda env**（已在位：sglang 0.5.9 + vllm 0.14.1 + flashinfer 0.6.3 + lm_eval 0.4.13），🚫 不碰共享 `py310`。
- 外网命令**显式带 proxy**。

**⑥ 产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 新增「**P-9.11 · sglang 生产栈 —— BaiZe(Mamba2-hybrid 2B) vs MiniCPM5-2B 推理对比**」节（**命令 + 原始输出 + 逐格表 + 每格比值** + 与 Round-1 mcore 数字并列并标口径）。

> ✅ 本块生效即视为已批准；**P-9.10②（eager 下界）已完成**，本块为「生产栈复测架构对比」，**不阻塞** P-6② / P-8。

### 🆕 运维指令 · 2026-10-05（晚 · ① `sglang` 改用 **conda 环境**从头装（先查 `.12` 现成的 sglang/vllm env）② 「外网命令带 proxy」口径同步 ③ 环境隔离纪律）· 高优先

> **用户拍板（2026-10-05 晚）**：「**P-9.10 与 sglang A/B：我在 `2.12` 已经装过 sglang 的**，你可以看看有没有 conda 环境叫 `sglang` 或 `vllm` 的。**如果没有，自己新开个 conda 环境，叫 `sglang`，从头装一下**，记得设置 `https_proxy` 和国内的（比如阿里腾讯）pip 源，**可以装的**。」

**① 先查现成 conda 环境（`.12` 为主，`.29` 也查）**
```bash
conda env list | grep -Ei 'sglang|vllm'          # 两台机都查（.12 是用户说装过的那台）
# 命中后在该 env 里验证：
conda run -n sglang python -c "import sglang, torch; print(sglang.__version__, torch.__version__, torch.cuda.is_available())"
```
- 找到**版本/依赖可用**的 env ⇒ **直接复用**（记清 env 名 + 版本 + `conda env list` 原文）。
- ⚠️ `.12` 的 env 是**本机 conda**（若两机不共享 conda 路径则不能直接给 `.29` 用）⇒ 若 P-9.10 在 `.29` 跑，**在 `.29` 上另建同名 env 或确认 conda 路径共享**；两机都要给出核验原文。

**② 没有就新建 `sglang` 环境从头装（显式带 proxy + 国内源）**
```bash
export http_proxy=http://172.19.92.25:13128 https_proxy=http://172.19.92.25:13128
conda create -y -n sglang python=3.10
conda run -n sglang python -m pip install -U pip -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
conda run -n sglang python -m pip install sglang \
  -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com \
  --extra-index-url https://pypi.tuna.tsinghua.edu.cn/simple      # 阿里不通换腾讯 https://mirrors.cloud.tencent.com/pypi/simple
```
- 🚫 **绝不在共享 `py310` 里装**（隔离在 `sglang` env 内）；🚫 不要 `--no-deps`。
- 记录**确切输出**（成功 → `sglang --version` + `import` 通过；失败 → 贴原始报错）。
- 若 `cuda-tile`（仅 `pypi.nvidia.com`）仍 SSL EOF ⇒ 试国内镜像的同名/nvidia wheel 或 conda 源；**仍失败**才回落到已定的 **`mcore + CUDA-graph`**，✅ **不阻塞 P-9.10 ②**（到点照起；sglang 只为「抬上界」）。

**③ 「外网命令带 proxy」口径同步到本线（与 data / harness / vision 一致）**
- 你的 shell 被 loop 剥了 `*_PROXY`（内网网关鉴权用，**不能改**）⇒ 凡访问外网的那条命令**自己显式带**：`P=http://172.19.92.25:13128`；`https_proxy=$P http_proxy=$P <cmd>`；pip 加 `--proxy $P` + 国内索引。
- 🔑 **`Errno 101 / http 000` = shell 没带 proxy，不是集群禁网/镜像被墙**（本轮 sglang A/B 已实测证实：带 proxy → 阿里云 200）。

**④ 环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；**`sglang` 托管大模型 = `sglang` conda env**；**harness 大量装包 = 另起新 conda env**。三者互不污染。

> ✅ 本块生效即视为已批准。**时序不变**：P-9.10 ② 照常在 GPU0–1 起；P-9.9 已收官（tensorwise FAIL → **P-8 沿用 delayed FP8**）。


### 📉 记忆维护规程（2026-10-03 运维新增，**硬性**）
> 理由：`MEMORY_*.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。当前 `MEMORY_PRETRAIN_2B.md` ≈ **243KB（严重超标）**。
- **上限**：本线 `MEMORY_PRETRAIN_2B.md` 控制在 **≤ 32KB**；**下次唤醒立即执行一次滚动归档**。
- **滚动**：把**较早的流水条目**（保留最近 ~20 条）**追加**到 `daily-memories/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 /「进度快照」③ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变（正文/流水/快照里**不得**再出现以 `WAITING:` 开头的行）。

---



# ══════════════ ROUND 2 · **现行部分**（只保留仍未完成/仍有效的）══════════════

> R2.0/R2.1/R2.2 清单 · R9.0-bis · P-4R · P-5a 与 **Round 1（S0–S5）** 均已**完成并归档** →
> **`run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md`**（**需要时再去读，不要把整份读进上下文**）。

**P-6 细节 —— lm_eval 评测（第 1 步：8 集零样本摸底；第 2 步：**scaling law 曲线 + 外推**）**

> **目的**：Stage (i) 的定位是**通用模型**，**本任务不做 EDA-Eval**。
> 唯一目标是**摸底训练效果**——让 Stage (i) 的结论**不只是 loss 数字**。
>
> **口径严格对齐 Xmodel-2 论文**（`doc/BaiZe-ISEDA2027/Xmodel-2/xmodel-2.tex:198,207`）：
> - Harness：**EleutherAI Language Model Evaluation Harness（lm-eval）**
> - **zero-shot**、**raw accuracy**
> - **8 个评测集**（与 Table 2 的 8 列一致），另报 **Avg**：
>   `ARC-Challenge` · `ARC-Easy` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`
> - ⚠️ 论文正文还提到 **TriviaQA**，但 **Table 2 里没有这一列** → **以表为准，只跑这 8 个**，并在报告里注明此差异。

**第 1 步（最便宜，先做）：评测现有的 20000 步 checkpoint**
- 它就是 Stage (i) 的最终产物；**先拿到它的 8 集分数**，立刻就有"摸底"数据。

**第 2 步（最有价值）⭐ —— 与 P-5b 结合 → 「能力 vs token」<u>scaling law 曲线 + 外推</u>**

> ## 🎯 运维 2026-10-02 明确要求
> 「**希望画出 scaling law 曲线，估计常识推理 8 任务和复杂推理 6 任务要达到更高的水平需要多少训练数据。**」
>
> **两条口径澄清（运维 2026-10-02，务必照做）**：
> 1. 🔧 **全部走 `lm_eval`，<u>不要换框架</u>** ——
>    Xmodel-2 是 **2 年前的论文**，当年 HumanEval/MBPP 要另配 `bigcode-evaluation-harness`；
>    **现在 `lm_eval` 已原生支持**，**无需引入第二套框架**。
> 2. 🔢 **n-shot 的 n 就用 `lm_eval` 的<u>默认值</u>** ——
>    **不必**去对齐 Xmodel-2 的 5/4/3/0-shot。

### (1) 数据点：P-5b 的 6 个 checkpoint
在 **655M / 1.3B / 2.6B / 5.2B / 10.5B / 20B token** 各跑一遍**下面两套**评测。

### (2) 两套指标（**都用 `lm_eval`**，n-shot 用默认值）

| 集 | 任务 | 说明 |
|:--|:--|:--|
| **常识推理（8）** | `ARC-C` `ARC-E` `BoolQ` `HellaSwag` `OpenBookQA` `PiQA` `SciQ` `Winogrande` | 与 **P-6 第 1 步同一套**（已跑通，Avg **0.4395**）→ **直接可比** |
| **复杂推理（6）** | `GSM8K` `MATH` `BBH` `MMLU` `HumanEval` `MBPP` | **`lm_eval` 原生支持全部 6 个**；⚠️ HumanEval/MBPP **需代码执行**（`lm_eval` 自带沙箱，按其文档开执行开关即可，**不要另起框架**）|

- ⚠️ **论文正文提到 TriviaQA 但 Table 2 表里没有** → **以表为准**（8 个），报告注明。
- ⚠️ **报绝对值时要标 harness 版本与 shot 数**（因为与 Xmodel-2 的口径不同）。

### (3) ⭐ **参照线**（Xmodel-2 论文的公开数值，供"更高水平"定位）

> ⚠️ **口径不可严格比**（shot 数、harness 版本、模型规模均不同）→ **只作"量级参照"，必须标注**。

**常识推理 Avg（zero-shot）：**
| 模型 | Avg |
|:--|--:|
| TinyLLaMA1.1-1.1B | 55.24 |
| Llama-3.2-1B | 57.70 |
| OpenELM-1.1B | 56.95 |
| MiniCPM-1.2B | 59.45 |
| **Xmodel-2-1.2B** | **61.79** ← 同类论文直接对标 |
| Qwen2.5-1.5B | 63.14 |
| Phi-1.5-1.3B | **65.68** ← 强标杆 |

**我们起点**：**P-6 第 1 步已测 Avg = 0.4395（43.95%）** @ 20k 步 / **655M token**。
→ **距最弱的 1B 级（55.24）差 11.3 个点；距 Xmodel-2-1.2B（61.79）差 17.8 个点。**

**复杂推理 Avg：**
| 模型 | GSM8K | MATH | BBH | MMLU | HE | MBPP | **Avg** |
|:--|--:|--:|--:|--:|--:|--:|--:|
| OpenELM-1.1B | 0.45 | 1.06 | 6.62 | 25.52 | 8.54 | 6.80 | **8.16** |
| OLMo-1B | 2.35 | 1.46 | 25.60 | 24.46 | 5.49 | 0.20 | **9.93** |
| TinyLLaMA1.1-1.1B | 2.50 | 1.48 | 25.57 | 25.35 | 1.83 | 3.40 | **10.02** |

> 🚨 **预期校准（必须写进报告）**：**1B 级模型在这 6 个任务上基本贴地板** ——
> GSM8K **0.45–2.5%**、MATH **~1%**、MMLU **~25%（≈chance）**、BBH **~25%（≈chance）**。
> → **我们 2.2B / ≤20B token 跑出来很可能<u>全程贴地板</u>**。
> **若确实全程贴地板 → 「量不出斜率」本身就是结论**（说明复杂推理在**更晚**才涌现，
> 需要远超 20B 的训练量）—— **如实写，不要硬拟合**。

### (4) ⭐⭐ **画 scaling law 曲线**

- **x 轴：训练 token（log 轴）**；**y 轴：各集分数 + Avg**。
- **常识 8 集**：画 **1 张图**（8 条细线 + **Avg 粗线**），**叠加上述参照线**（虚线）。
- **复杂 6 集**：同一格式；若贴地板就**如实呈现**。
- **拟合**：对 **常识 Avg** 拟合幂律 `acc = a − b·N^(−c)` 或对数 `acc = a + b·log10(N)`，**报 R²**。
- **同时记** loss / grad norm / img/s，以对照"loss 曲线"与"能力曲线"的**不同饱和点**。

### (5) ⭐⭐ **外推**（决策价值所在）

1. 用拟合曲线外推：**常识 Avg 达到 50% / 55% / 60% 各需要多少训练 token？**
2. **对照我们的算力**：按实测 ~83K tok/s（P-7 修正后），
   **这些 token 预算分别要跑多少天**（8×H100）？
3. **一句话结论**：
   - 若在**可接受的天数内**可达 → 给"**需 X 万亿 token / Y 天**"，直接作为 **P-8 的 token 预算依据**
   - 若**远超可承受范围** → 明确写"**在当前算力窗口内达不到 55%（或 60%）**"
4. **如实报外推不确定性**（**用 ≤6 个点外推**，且我们处在曲线**陡升段**，误差会很大）。



**执行路径（⚠️ 以你们**自己已查证过的结论**为准，不要另起炉灶）**

> 你们在 **2026-09-29** 已经查清过这条路
> （`run/daily-memories/2026-09-29.md:201,207,223` 与 `run/BAIZE_2B_ARCH_SEARCH_TASK.md:218`）：
> - **既定路径就是「ckpt → HF → SGLang 起服」**；当时的阻碍只是 **vLLM（`_C.abi3.so` 崩）与 `sglang`（未装）**，
>   于是退到 mcore 直驱，并明确注明那是**下界测量**（"如需精确 decode 数后续 SGLang 起服复核"）。
> - 那次也写明：**真正的坑是「mcore 分布式 ckpt → HF 格式转换」**（无现成 bridge，需把
>   `NVIDIAMambaHybridModelProvider2B` 权重映射到 **Nemotron-H / Llama HF 结构** + DeepSeek tokenizer）；
>   **mcore 手写前向只是 fallback**。
> - **SGLang 原生支持 `nemotron_h`**（`--mamba-ssm-dtype float32` / `--mamba-full-memory-ratio`）——
>   这正是当初选 SGLang 的原因。

**推荐路径（标准做法；不需要写自定义 lm_eval model 类）**

1. **转 HF**：mcore 分布式 ckpt → **Nemotron-H HF 结构**（含 DeepSeek-V4.1-Flash tokenizer）。
2. **SGLang 起服**（若 `sglang` 未装，先 `pip install sglang`）：
   `python -m sglang.launch_server --model-path <hf> --port 30000 --mamba-ssm-dtype float32 --mamba-full-memory-ratio <按需>`
3. **lm_eval 用内置模型类型直连，无需改接口**：
   `lm_eval --model local-completions --model_args base_url=http://localhost:30000/v1,model=<name>,tokenizer=<hf> --tasks arc_challenge,arc_easy,boolq,hellaswag,openbookqa,piqa,sciq,winogrande --num_fewshot 0`
   （`local-completions` / `local-chat-completions` 可接**任何 OpenAI 兼容服务**——这是标准用法。）

**⚠️ 先验证一件事（成败所系，第一步就做）**
这 8 个任务里 **7 个是 multiple-choice**，lm_eval 的 `local-completions` 靠 **`loglikelihood`** 打分，
即需要服务端在 `/v1/completions` 上支持 **`echo=True` 且返回 prompt 的 `logprobs`**。
→ **先用一个最小请求验证这一点**；若不支持，再考虑 `local-chat-completions`，
**最后**才回退到自定义 model 类包 mcore 前向。

**时间盒**：转换 + 起服 **≤ 2 小时**；超时就记录卡点并转 fallback，不要无限调试。

**产出**：`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加一节；
并给出**论文回填建议**（§4 是否加一张"通用能力零样本"表）。

**P-7 细节 —— 训练吞吐幅度核查（P-3 的补充，**必须查明**）**

> **问题**：论文 `tab:archcomp` 写 **dense 89K vs hybrid 72K（dense +24%）**；
> 而 **P-3 在同一口径下**（6 卡 / TP1/DP6 / GBS=6 / seq 4096）实测
> **dense 89.7K vs hybrid 85.6K（dense 仅 +4.8%）**。
> - dense 侧几乎一致（89K → 89.7K）✅
> - **是 hybrid 从 72K 涨到 85.6K（+19%）**，即 ms/iter 由 ~340 降到 ~287。
>
> **为什么必须查明**：**训练吞吐代价是 hybrid 论证里唯一的「成本侧」数字**。
> 若真值接近 +5% 而非 +24%，hybrid 的性价比论证会**明显更强**；
> 反之若是 Round 1 的测量本身有问题，论文里那个 `+24%` 就**站不住**。两种情况都直接决定 `tab:archcomp` 怎么写。

**要做的核查**
1. **先算一笔账**：Round 1 是 **1000 步**短跑；若把 SSM 首步编译开销（记录中的 **~12.3s**）摊进平均，
   相对稳态只抬高约 **3.6%**（12.3s ÷ (1000 × 0.34s)）——**不足以解释 340ms → 287ms 的 16%**。
   → 因此**一定还有别的原因**，继续查。
2. **比对两次测量的差异项**：micro-batch / gradient-accumulation 设置、`--recompute` 档位、并行度、
   mcore / `transformer_engine` / 容器版本、以及**当时的集群争用状态**——是同一套配置吗？**逐项列出**。
3. **在同一环境、同一配置下重测一遍** hybrid 与 dense 的**稳态** ms/iter（各 ≥300 步，**剔除首步**），
   得到可复现的干净数字；记录 **GPU 独占核验原文**（沿用 R2-4 做法）。
4. **给结论**：`tab:archcomp` 的 "Training tok/s" 一列应写**哪两个值**、差距**百分之几**；
   并说明 Round 1 的 72K 究竟属于「含首步开销的短跑均值」还是「另一环境下的值」。

**产出**：写入 `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 的 P-3 节 + 更新「论文回填建议」，
明确指出 `tab:archcomp` 该改成什么。**时间盒 ≤1h。**

**P-8 细节 —— 🏁 Stage (i) 完整训练（正式预训练）**

> ## ⏸ **运维 2026-10-02 指令：P-8 暂缓启动**
>
> **原话**：「**测数据配比需要时间，下载 base 也需要时间…因此 P-8 暂缓启动，先做配比实验和下载 base。**」
>
> **原因（两条前置都未就绪）**：
> 1. **`Ultra-FineWeb`(base) 还在下载**（115/64624，2.99 TB）—— 而它是 **stable 段的主力数据**；
> 2. **WSD 双阶段配比实验还没做**（见 `BAIZE_DATA_TASK.md` §0.6）—— **P-8 吃什么配比是它要定的**。
>
> **→ 所以：不要因为"P-5b 快跑完了"就顺手启动 P-8。** 前置未齐之前，P-8 不启动。
> **→ 本唤醒及后续唤醒：做完 P-4R / 恢复 P-5b 之后，仍然等 data agent 的配比方案 + base 就绪。**

> ## 🎯 这是 Stage (i) 的**本体**
> **Stage (i) 的 scope 不变 = LLM 预训练（from scratch）。**
> P-1…P-7 全部只是**前置选型实验**（token 量级 164M–655M，合计 ~85 GPU·h）。
> **P-8 才是真正把 2.22B hybrid 训出来**，作为 Stage (ii)–(v) 的基座。
> 🚫 **不要**因为"实验都做完了"就把 Stage (i) 标成完成。

**输入（全部来自前序任务，不要自行改动）**

| 项 | 来自 |
|:--|:--|
| **GBS** | P-5a 的 GBS×LR 扫描结论（若无右移则沿用 GBS=8；若 P-5a 指向更优大 GBS 则采用并注明） |
| **LR / 调度 / 退火配比** | Round 1 胜出配置（LR 1e-3 / WSD / warmup 250 / decay 500 / min_lr 1e-5 / L3(86%)+code(10%)+math(4%)）；若 P-5a 给出新 LR 则改用并注明 |
| **token 预算** | ⭐ **由 P-5b 的 loss-vs-tokens 曲线决定**（曲线何时变平 → 就在那附近取预算） |
| **精度** | 若 P-4 证明 FP8 对本架构确有加速且**不劣化 loss**，可用 FP8；否则 bf16。**必须记录采用与否及理由** |

**token 预算的三档参照（按实测吞吐 8×H100 ≈ 92.6K tok/s 折算）**

| 档位 | token | 墙钟 | GPU·h | 说明 |
|:--|:--|:--|:--|:--|
| **下限** | **44 B** | **≈5.5 天** | ≈1056 | Chinchilla 最优（2.22B × 20）。**低于此不足以称为"训练好的模型"** |
| **推荐** | **100 B** | **≈12.5 天** | ≈2400 | 超 Chinchilla ≈2.3×；契合论文**推理效率**卖点（推理最优需过训练） |
| **上限** | 200 B | ≈25 天 | ≈4800 | 仅在预算与时间都宽裕时 |
| ⚠️ 不计入 | 690 B（真实全语料） | **≈86 天** | ≈16560 | **2027-02-01 前不可能** + `/nas_train` 只剩 32T，**不要定这个档** |

> **默认按「推荐档 100B」准备**；**P-5b 曲线出来后，若曲线在更早处变平，就下调**（省钱省时）。
> ⚠️ **最终 token 预算定下后，必须在 `MEMORY_PRETRAIN_2B.md` 里写明并上报**，再启动长跑。

**训练要求**

1. **从零开始**（不加载任何预训练权重），**真实语料**（`Ultra-FineWeb-L3` 全量 en 子集 + code + math 退火配比），
   **不是** `ultrafineweb_l3_qa_700m` 那个 742M 小分片 —— **本次必须跑真正的全量语料**。
2. **WSD 完整走完**：warmup 250 → stable → **decay 尾段必须真的吃到退火混合**（这是 Stage (i) 的核心配方之一）。
3. **checkpoint 规划**：至少保留 `final` + **每 10% 一个**（供 Stage (ii) 选起点、供 P-6 画能力曲线）。
   ⚠️ 每个 ckpt（2.22B 含 AdamW 状态）≈ **~30 GB**；**`/nas_train` 只剩 32T**，先算好 ckpt 留存策略与清理时机。
4. **训练中每 500 步**记 `train loss` / `val loss` / `grad norm` / `tok/s` / **GPU 独占核验**。
5. **禁止在 P-8 期间叠加其它重 I/O 或抢卡任务**（vision / data 侧要避让）。
6. **失败即如实记录**：NaN / 发散 / OOM 一律记录**并保留当时的 ckpt 与日志**，不要静默重启掩盖。

**产出**

1. **Stage (i) 最终 checkpoint**（Stage (ii)–(v) 的基座）—— 这是本项目**最关键的单个产物**。
2. `EXPERIMENTS_PRETRAIN_2B_ROUND2.md` 追加 **P-8 节**：完整 loss 曲线、实际 token 数、实际 GPU·h、
   最终 `val loss`、与 P-5b 曲线预测值的对照（**预测量 vs 实测量**，这是对 scaling 曲线的一次真检验）。
3. **论文回填建议**：§4 应写清 **实际训练 token 数 / GPU·h / 最终 loss**，
   把"从零训练一个 2.22B hybrid"的**规模与代价如实写出来**（并处理 §6 #13 的 1.8T 误读问题）。
4. `BAIZE_PRETRAIN_RESULT.html` 更新为**含 P-8 的最终版**。
5. git commit + push（**只提交文本**；checkpoint 不入库）。

**时间盒**：**下限 5.5 天 / 推荐 12.5 天**（按 token 预算）。**超时或连续失败不要硬撑**，
记录卡点并上报 —— 但**除非运维叫停，P-8 应跑到底**。


## R2.3 交付物

1. **`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`**（新文件）：P-1/P-2/P-3 全部结果表 +
   每条可复现命令 + 与 Round 1 的差异说明 + **「论文回填建议」段落**（给出精确数值与文字建议，
   特别是「最优点是否在边界」「Δ 是否在噪声内」这两个结论该怎么写）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_PRETRAIN_RESULT.html` 或新建 `BAIZE_PRETRAIN_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——
   论文已由外部统一重构并推送，回填由外部完成。你只在报告里给「回填建议」。
4. 正常更新 `MEMORY_PRETRAIN_2B.md` 与 `daily-memories/`。
5. **git commit + push，并严格走本文件顶部的「git 同步规则」**（fetch → 必要时 `pull --rebase` → push → 确认 0/0）。

## R2.4 约束

- **总预算**（分三档）：
  - **P-1 / P-2 / P-3 / P-4 / P-6 / P-7**：短程实验，≤ 5 小时墙钟（P-6 视加载路径难度可到 6 h；P-7 ≤1h）。
  - ⭐ **P-5 是独立长任务，≤ 8 天墙钟**（P-5a 4–5 h + P-5b 20B token ≈ 2.5 天；预算允许可延到 60B ≈ 7.5 天）。
  - 超时按 **P-5a > P-6 第 1 步（现有 ckpt 的 8 集）> P-1/P-2 > P-4 > P-5b > P-6 第 2 步** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.29` 的 **GPU 0–7**（8 卡）。**绝不杀他人进程**。
  ⚠️ 另有 vision 任务在 **`10.239.2.12`**（另一台机器）跑——**与你无关，不要去动那台**。
- **每次启动训练前后都要记录 GPU 占用核验结果**（`nvidia-smi --query-compute-apps=...`）。
- ⚠️ **NFS 与 vision 任务共享（重要）**：两台 GPU 节点用的是**同一块 `/nas_train` 盘**。
  vision 任务的 **R2-4 需要"无争用的干净吞吐测量"**，而你启动训练同样会打这块盘。
  → **启动 P-1 之前**，先读 `run/MEMORY_VISION.md`（共享盘，你直接可见）看它的 R2 进度：
  - 若 **R2-4 尚未完成**：先做**不占 GPU** 的准备工作（代码/数据核对、P-3 的 Round 1 基线复核、脚本落地），
    **每轮唤醒重查一次**它的进度；
  - **最多等 2 小时**；超过 2 小时则照常启动 P-1，并在报告里注明"当时 vision 任务在并发"。
  → 你的**每次测量都要记录"当时 vision 任务在跑什么"**。
- 数据：P-1/P-2 沿用现有 200k docs / 165M token 即可（5000 步 ≈ 164M）；
  **P-3 若需更长的数据覆盖，先核对再启动**，不要中途断数据。
- **收尾不杀 loop（关键）**：R2 的 P-1/P-2/P-3 全部完成（或按预算裁剪到只剩需等待的项）后，把结果写进报告并 git push，然后**停在原地**：`MEMORY_PRETRAIN_2B.md` 的 `PHASE` 置 `converged`、`WAITING` 置 `1`（30 分钟长轮询）；🚫 **绝不 kill / pkill `baize_pretrain_loop.sh`**。loop 必须持续运行，以便运维远程下发新任务（会改写本任务书，下次唤醒即按新指令执行）。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入 `MEMORY_PRETRAIN_2B.md`、`EXPERIMENTS_PRETRAIN_2B.md` 和 `daily-memories/`。

你是推进 **BaiZe Stage(i) LLM 预训练**（Mamba2-hybrid 2B 从零 + 24h 预算高置信度超参搜索）的自动化 agent（Cline），被唤醒时按 `MEMORY_PRETRAIN_2B.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

## ⚠️ git 同步规则（**必读，2026-10-01 新增，每次唤醒都要走**）

### 前提：这是一个**共享工作副本**

vision 任务的 agent 与本任务**共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

**因此：**
- **只需一个人 pull，另一个立刻看到**：vision agent 拉取后，你读到的 `$TASK_MD` 与所有文件都会同步更新。
  **不要重复 pull**，也不要因为"工作区里出现了别的任务的改动"而困惑。
- 工作区里**陌生的未提交改动很可能是 vision 任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉另一个任务的成果。
- 两个 loop 每 5 小时各自 `git add -A && commit && push`，**会互相把对方在途的文件一起提交**。
  这是既有设计的已知副作用，**不要试图"修正"它**。

### 但 loop 本身**只 push 不 pull**

`baize_pretrain_loop.sh` 的 `git_push_if_needed()` 只做 `add → commit → push`。
一旦远端被别人推进，它的 push 会 `! [rejected] (fetch first)` 失败、每 5 小时重试一次、永远失败。
**所以 pull 必须由你（agent）来做。**

**每次唤醒按顺序执行：**

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_PRETRAIN_2B.md EXPERIMENTS_PRETRAIN_2B_ROUND2.md daily-memories/`
   🚫 **不要用 `git add -A`**——那会把 vision 任务的在途文件卷进你的提交。
3. 若显示 **behind / diverged**：`git pull --rebase origin main`。
   - 报 `cannot rebase: You have unstaged changes` → 是**双方的在途改动**：
     先把你自己要提交的文件 commit 掉再 rebase；🚫 不要 stash / 丢弃别人的改动。
   - 报 `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：
     等 30–60 秒重试（最多 3 次）；仍失败就记一行流水并**跳过本次 git 操作**，下次唤醒再试。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` **无 ahead/behind** 才算闭环。
5. 流水记一行 git 结果（沿用你已有格式）。

> 参照实现：vision 任务的 agent 在 `daily-memories-vision/2026-10-01.md:198` 已按同样方式
> `git pull --rebase` 合并远端后 push 成功——**沿用同一做法**。

---


---

