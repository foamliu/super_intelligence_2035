# BAIZE_VISION_TASK.md

# ══════════════ ROUND 6 · 第六轮任务（**文本塔上下文 与 数据切换 的裁定** · 纯 CPU · ≤1.5h）══════════════

## R6.0 定位与顺序

> ### ⚠️ 现状更新（2026-10-01 深夜）：**R5 的 P0 已经在跑了**
> R5 的 P0（4 架构 × 3000 步）**已启动**，数据用的是**已打包的 `en500k`**。
> 因此 **R6 不再阻塞 R5** —— 请在 **R5 的 GPU 训练进行期间，并行做 R6**（R6 是纯 CPU，**不占卡**）。
>
> **R6 的结论用于**：
> ① R5 的 **P1 / P2**（是否在余量内补一条 GPIC 臂 —— 加分项，非必需）；
> ② **正式训练（Stage (iv) 之前的编码器训练）的数据与文本塔决策** ← **这才是 R6 的主要目的**。
>
> ⚠️ **不要中断已跑的 R5 P0。** 若 R6 判定"R5 也该换 GPIC"，也**等 P0 跑完**，
> 把 P0 留作 en500k 臂的对照，在 P1/P2 里加 GPIC 臂即可。

`PHASE` → `R6_probe`（**可与 R5 的 `R5_active` 并存**，在记忆里注明）；**不要重跑 R3 / R4**。

> ## 🚫 本任务的铁律：**绝对不许猜**
> 三个问题**必须从「源码 / 模型 config / 实测」里取证**，并**把看到的原文贴出来**。
> 每条结论都要标证据出处（文件路径 + 行号 / config 字段名 / 命令与输出）。
> **凡是没有证据的表述，一律视为未完成。**
>
> 💡 **一条已知线索（请核实并纳入）**：现有 R5 代码 `run/vision/r5_train.py:57-59` 用的是
> **`transformers.CLIPTokenizer`**，且 **`max_length=77, truncation=True` 是显式写死的** ——
> 也就是说 **R5 里根本没有用 open_clip 的 `SimpleTokenizer`**。
> 请据此重新审视 R6.2 的问法：「是 open_clip 的默认设置吗」这个前提**可能不成立**。

---

## R6.1 问题 1 —— 后续实验数据是否切换为 **GPIC**？

### 结论必须三选一（🚫 不许"视情况"）
### → **切 / 不切 / 分阶段切（写明哪一阶段用哪个）**

**先取证这四个事实（要实测，不要引用旧结论）**

1. **GPIC 在盘上的真实规模**
   - 路径：`/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train`
   - 当前只有 **≈430–439 个 tar（全量 8000）** → **抽 5–10 个 tar 实测**：每个 tar 里有多少个 `{key}.json` + 图像？
   - **→ 必须给出：现有 tar 一共能提供多少「图文对」。**
   - ⚠️ **硬约束检查**：R5 需要 4 架构 × 3000 步 × bs64 ≈ **19.2 万对/架构**。
     **现有量够不够？** 不够就是**硬约束** → 要么等下载、要么 R5 先用现有量并在报告显式注明"数据量不足"。
2. **caption 质量对比**（**用 R4 的 `r4_gpic.py`，同一段代码、同一口径**）
   - 长度分布 + **77 截断率**（R4 已测：GPIC `short`=20 token/0%；LLaVA=99.7–100%）
   - **区分度**：same-tower off-diag 余弦（R4 测过 GPIC short 0.245 最分散）
   - **抽样 20–30 条 GPIC `short` 原文贴出来** —— 让运维能直接看它是否真的可区分
3. **与 Stage (iv) 的关系**：GPIC 能不能顺带服务 MLLM 对齐？还是纯 CLIP 式短 caption？
4. **代价**：切 GPIC 要下多少、多久、`/nas_train`（只剩 **32T**）放得下吗。

### 🔴 必须算清的一笔账
**切 GPIC 后，R5 的架构对比还能和 R1/R2 的历史数字比吗？**
（初判：不能，因为数据变了。**但 R1/R2 已因坍缩作废，所以不构成阻碍。**）
→ **请独立确认这个推理**，并额外说明：**"数据全换了"会不会影响 R5 表格内部各格子之间的可比性？**

### 与 R5 的联动（**必须写进 `MEMORY_VISION.md`**）
- 若结论 = **切** → R5 默认数据（GPIC `short`）**不变**，但报告里要写明"依据来自 R6"。
- 若结论 = **不切** → **立刻改 R5 的数据选择**，并标注原因。

---

## R6.2 问题 2 —— 77 截断的原因是什么？**是 open_clip 的默认设置吗？**

### 逐条取证（**每条都要贴原文**）

1. **open_clip 源码**：`open_clip.tokenizer.SimpleTokenizer` 的 `context_length` **默认值**是多少？
   - 贴 `__init__` 签名 + 默认值（**文件路径 + 行号**）。
   - 同文件里 `HFTokenizer` / `SigLIPTokenizer` 等其他类的默认值呢？
     **SigLIP 的默认 context 是多少？**（这关系到"换成 SigLIP 会不会更糟"）
2. **实际调用处**：`run/vision/train.py` **到底怎么构造 tokenizer 的**？
   - 是**用了默认值**，还是**显式传了 `context_length=77`**？**把那几行代码贴出来。**
3. **⭐ 真正的根因（重点查这个）**：
   77 是「**open_clip 随便定的默认**」，还是「**继承了 CLIP 文本塔自身的结构限制**」？
   - 查 `openai/clip-vit-large-patch14-336` 的 HF `config.json` →
     **`text_config.max_position_embeddings` = ?**
   - 该文本塔的**位置编码表是不是正好 77 行**？**把那个字段贴出来。**
   - **→ 必须明确回答**：根因是 **(a) open_clip 的默认** / **(b) CLIP 文本塔的位置编码表大小（继承自 OpenAI CLIP 原始设计）** / **(c) 两者巧合一致**。
   - ⚠️ 若答案是 (b) → **说明即使把 open_clip 的参数改大也没用**，因为**塔本身装不下**。
     这一点**必须写清楚**，它直接决定 R6.3 的答案。
4. **确认 R4 的 `sem_clip` recipe 用的是哪种塔**：是不是 `clip-vit-large-patch14-336` 的
   **text tower（冻结）**？它在哪被加载、`max_position_embeddings` 是多少？

---

## R6.3 问题 3 —— 正式训练时，**这个数值可以变长吗？**

> 必须**分开回答**「**技术上能不能**」和「**该不该**」。**两问都要答，缺一不算完成。**

### A. 技术上能不能（**在当前的 R4 recipe 前提下**）

- 当前文本塔是**冻结的预训练 `clip-vit-large-patch14-336` text tower**，它的 `max_position_embeddings` 是多少？
- **超过它会怎样**？（位置编码越界报错 / 静默截断 / 输出错乱）—— **从代码或实测确认，不要猜。**
- **→ 给出明确判定**：在**保持冻结塔**的前提下，77 **能不能**变长？**最多能到多少？**

### B. 若要变长，有哪些路？（**逐条给代价 + 风险，最后推荐一条**）

| # | 路径 | 需要查什么 | 代价 / 风险 |
|:--|:--|:--|:--|
| 1 | **位置编码插值/扩展** | 对 pos-embed 做插值是否可行？ | 会破坏"纯冻结预训练"前提吗？需多少微调？ |
| 2 | **换文本塔** | SigLIP 的默认 context（**更短**）？长上下文文本编码器（LongCLIP / LM 系，2K–32K）？ | 换塔 = 换语义空间，R4 的 C1–C4 要**重新验证** |
| 3 | **自己训文本塔** | —— | 🚫 **R3/R4 已证明这条路会坍缩** → **明确标注为不推荐** |
| 4 | **分块 + 聚合**（chunked pooling） | 长 caption 切段分别编码再池化 | 可行性？会不会引入新的池化偏差？ |
| 5 | **不放开，改用短 caption** | = R6.1 的 GPIC `short` | **成本最低** |

### C. ⭐ **该不该** —— 必须结合 R4 的既有结论回答

- R4 已用决定性实验**证伪**了"截断是坍缩主因"：
  **被丢弃的尾部（off-diag 0.372）比保留的头部（0.295）更相似** →
  截断是**背景事实**，不是坍缩推手。
  → **请独立确认这个推理**：**"放开 77"是不是修复坍缩的必要条件？**（初判：不是）
- 那么 **放开 77 的真实收益**是什么？**在什么场景下才真的需要它？**
  （提示：① 若坚持吃 LLaVA 长 recaption；② Stage (iv) 要保留长描述能力）
- **→ 给出可执行结论**：正式训练时选 **保持 77 / 放开到 N / 换塔** 中的**一个**，写清理由与代价。

---

## R6.4 交付物

1. **`run/EXPERIMENTS_VISION_ROUND6.md`**（新文件），**必须**包含：
   - **一张裁定表**（三行），每行 = **结论 + 证据出处**：

     | 问题 | 结论 | 证据出处 |
     |:--|:--|:--|
     | 后续数据是否切 GPIC | 切 / 不切 / 分阶段 | |
     | 77 的根因 | (a) / (b) / (c) | |
     | 正式训练能否变长 | 能（到 N）/ 不能 / 换塔 | |

   - **所有取证的原文摘录**：源码行、`config.json` 字段、命令与输出、抽样的 GPIC `short` caption。
   - **论文回填建议**：`6_vision_encoder.tex` 该不该写 context length 与数据来源；若写，写什么。
2. 更新 `MEMORY_VISION.md` + `daily-memories-vision/`。
3. git commit + push（走既有同步规则）。
4. 🚫 **不修改任何 `*.tex`**（论文由外部统一回填）。

## R6.5 约束

- **纯 CPU，≤ 1.5 小时**。**不占 GPU**、**不下载大数据**（除非确认必须，且先报磁盘与带宽）。
- 🚫 **不许猜**：查不到就写「**查不到 + 我查了哪些地方**」，**但仍要给出你的倾向与理由**（不许只用"查不到"收尾）。
- 🚫 不碰其他 agent 的文件（pretrain / data / ops relay）。
- ⚠️ 本任务**不改变 R5 的 recipe 本身**（text 塔仍冻结 CLIP + InfoNCE）—— 它只回答"该不该动"。

---



# ══════════════ ROUND 5 · 第五轮任务（**用修复 recipe 重跑架构/分辨率对比**）══════════════
> ## ⚠️ 次序（**2026-10-01 深夜更新**）
> **R5 的 P0 已在跑**（4 架构 × 3000 步，数据 = 已打包 `en500k`）。
> **R6 改为并行**（纯 CPU，不占卡）—— **R6 不再阻塞 R5**。
> R6 的结论用于：① R5 的 **P1/P2**（是否补 GPIC 臂）；② **正式训练**的数据与文本塔决策。
> ⚠️ 若 R6 判定"R5 也该换 GPIC"，**不要中断已跑的 P0**（跑完留作 en500k 臂的对照），在 P1/P2 里加 GPIC 臂即可。



## R5.0 状态切换（**先做**）

`PHASE` → `R5_active`；`WAITING` → `0`；流水追加"R5 启动"。
**R3 的坍缩判定、R4 的根因归因与修复 recipe 全部保留**，作为 R5 的**既定前提**，不要重跑 R4。

> **R5 的定位**：R4 已**解决**核心阻塞（C1–C4 全过），但 **R1/R2 的全部 loss 类结论已因坍缩作废**。
> **R5 = 用修好的 recipe 重跑一遍架构/分辨率对比，这是 Stage (iii) 恢复有效产出的唯一路径。**
> 不做 R5，`tab:visarch` / `tab:visres` / `tab:visobj` 三张表都无处可取。

## R5.1 固定 recipe（**R4 已验证，不要改动，除非单变量做消融**）

| 项 | 取值 |
|:--|:--|
| **文本塔** | `openai/clip-vit-large-patch14-336` 的 text tower（**768 维，全参数冻结**，`local_files_only=True` 加载）<br>路径：`/nas_train/app.e0031982/models/openai/clip-vit-large-patch14-336` |
| **目标函数** | `open_clip.loss.ClipLoss`（**CLIP InfoNCE**，`local_loss=False`）—— **无 `logit_bias`**，只学 `logit_scale`（温度） |
| **vision 读出头** | 把 `embed_dim` 改成 **768** 以对齐 CLIP 文本维 |
| **数据** | 优先 **GPIC `short`**（20 token、**0% 截断**、off-diag 0.245 最分散）；`medium` 次选。<br>⚠️ **LLaVA 长 recaption 不推荐**（100% 截断、通篇公式化，"the image" 占 30%）——<br>但**必须**保留一组 LLaVA-长caption 作**对照臂**，以佐证"换 caption 是加分项而非必需项" |
| **训练** | lr **3e-3**、warmup 20 步、batch **尽量大**（显存允许内，必要时跨卡 gather 负样本，目标 512–1024 负样本） |
| **参数量** | 四架构仍须落 **500–600M**（读出头改 768 维后请**重新实测参数量**并记录） |

## R5.2 待判据（**全程监控 C1–C4，沿用 R4.1**）

| # | 判据 | 阈值 | 🚨 熔断线（**触发即中止该 run**） |
|:--|:--|:--|:--|
| **C1** | same-tower off-diag 余弦 | < 0.9 | **> 0.95 @ 300 步** |
| **C2** | cross `diag−offdiag` 正间隙 | > 0 | **≈ 0 @ 300 步** |
| **C4** | loss 持续下降 | 非平台 | **300 步内 loss 未降** |

- **每 300 步**打一次 C1 / C2 / C4（省 GPU：只对 1 个 batch 做前向）。
- **熔断即中止并如实记录**——不要为了"跑完"而继续烧卡。
- C3（下游 R@1）只在**最优配置**上补测。

## R5.3 实验矩阵（按优先级，超时逆序裁剪）

**P0 —— 架构对比（必做）**：4 架构 × **3000 步** @ 锚点 **224/16**，8 卡 TP1/DP8，**batch 一致**。
- 架构：OpenVision2 / DeepEncoderV2 / MambaEye / MoE-ViE（同 R1 的四架构）。
- 产出：**架构排名**（loss 轨迹 + 训练 img/s + C1/C2/C4）+ **参数量**。
- 🔑 这是**唯一**能回答"架构到底有没有区别"的实验（R1/R2 因坍缩答不了）。

**P1 —— 分辨率对比（必做）**：**P0 胜出架构** × `{224/16, 336/14, 448/14}` × **3000 步**。
- ⚠️ **必须匹配 batch**（放不下就**全部降 bs=16** 或开 grad-ckpt）；batch 不一致的格子**标注不可比**。
- 产出：`tab:visres` 的 `loss` 列（**R2 那版是坍缩读数，已作废**）。

**P2 —— 长地平线 + 下游（选做，时间允许再做）**：胜出架构 × **10000 步**，在 3000/6000/10000 步记 **eval5k 的 R@1/5/10（i2t 与 t2i）** + loss。
- 产出：**「训练步数 → 下游检索能力」曲线** → 同时回答"Stage (iv) 该训多久"。

**P3 —— 稳健性（选做）**：胜出架构 3 seed × 1000 步，看排名是否翻转。

## R5.4 交付物

1. **`run/EXPERIMENTS_VISION_ROUND5.md`**（新文件），必含：
   - **架构对比表**：4 架构 × (loss@1k/2k/3k + 训练 img/s + 推理 ms/img + 参数量 + C1/C2)
   - **分辨率对比表**：3 分辨率 × (loss + token 数 + batch + C1/C2)，**显式标注 batch 是否匹配**
   - **C1–C4 监控轨迹**（每 300 步），含任何**熔断记录**
   - **胜出架构 + 完整可复现命令**（放文件顶部）
   - **「论文回填建议」**：⚠️ **必须明确写出 `tab:visarch_res` 要回滚/重写**（R2 那版是坍缩读数），
     并给出 `tab:visarch` / `tab:visres` / `tab:visobj` 三表该用什么数
   - 若 P2 做了：**训练步数 → 下游能力**曲线
2. 更新/新建 ROUND5 HTML（自包含，与既有报告同风格）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` —— 论文由外部统一回填。
4. 正常更新 `MEMORY_VISION.md` + `daily-memories-vision/`；git commit + push（走既有同步规则）。

## R5.5 约束

- **总预算：R5 墙钟 ≤ 6 小时**。优先级 **P0 > P1 > P2 > P3**；超时按此逆序裁剪，并在报告记录。
- **GPU**：只用 `10.239.2.12`（全部 8 卡）；**绝不杀他人进程**。
  ⚠️ **pretrain（`10.239.2.29`）正在跑 P-5a**，与你这台**共享同一块 `/nas_train` NFS**：
  启动重 I/O（GPIC 解包 / webdataset 打包）前先读 `run/MEMORY_PRETRAIN_2B.md` 看它在做什么，
  **尽量避免重叠**；无法避免则在报告中注明。
- **每次测量记录 GPU 独占核验 + NFS 并发核验的原文**（沿用 R2-4 做法）。
- 🚫 不碰 data agent（`baize_data_loop.sh`）/ ops relay（`ops_relay.sh`）/ pretrain 的文件。
- ⚠️ **绝不要为了"看起来收敛"而调参掩盖坍缩**。若某架构仍坍缩，**如实记录** ——
  **本任务的价值在于给出真相，不在于给出好看的数**。
- ⚠️ **若某架构在 300 步就触及熔断线**，说明该架构在本 recipe 下仍不稳 ——
  **这正是有价值的发现**，如实写，不要重试到它"看起来好"为止。

---

# ══════════════ ROUND 4 · 第四轮任务（**✅ 已完成**，结论见 `EXPERIMENTS_VISION_ROUND4.md`）══════════════
# 已交付：6 条怀疑逐一裁定（S5 随机文本塔 = #1 主因）；LLaVA vs GPIC 对比；
#         4 档单变量修复实验（sem_clip 通过 C1–C4）；路线裁定（固定 recipe，放大到 R5）。

## R4.0 状态切换（**先做**）

`PHASE` → `R4_active`；`WAITING` → `0`；流水追加"R4 启动"。
**R1/R2/R3 的结论全部保留**（尤其 R3 的坍缩判定，它是 R4 的起点）。

> **R4 的定位**：**这不是"再加固结论"，而是"解决阻塞"**。
> 现在的状态是——**从零训练视觉编码器根本训不起来（表征坍缩），因此无任何有效产出**。
> **不解决它，Stage (iii)/(iv) 无法前进。** 请把 R4 当成最高优先级、单线程推进。

## R4.1 "有效训练"的可判定标准（**R4 全程用这四条**）

"不收敛 / 没效果"必须变成可判定命题，否则无法验收：

| # | 判据 | 阈值 | 当前实测 |
|:--|:--|:--|:--|
| **C1** | **不坍缩** | 双塔 same-tower off-diagonal 余弦 **< 0.9** | ≈ **1.0000** ❌ |
| **C2** | **有区分度** | cross 的 `diag − offdiag` 有**明确正间隙** | ≈ 0 ❌ |
| **C3** | **下游有效** | `eval5k` R@1 **显著高于** 1/5000 | = 1/5000（精确 chance）❌ |
| **C4** | **loss 真在降** | 训练过程 loss **持续下降**，非钉在平台 | 钉在 **4.45** ❌ |

→ **四条全过才算"解决"**。任何一条不过，都不算。

## R4.2 步骤 A —— 落实运维提出的 6 条怀疑（**便宜，先做**）

> 这 6 条是运维审阅代码后提出的，**逐条给结论**（证实 / 排除 / 影响多大）。全部 CPU 级，不需要 GPU。

**S1 ⭐ 77-token 截断（最可疑）**
- 事实：`train.py` 用 `open_clip.tokenizer.SimpleTokenizer`（**vocab 49408，上下文长度 77，会截断**）。
- 核查：抽样 1 万条 caption，统计 **CLIP token 长度分布**与**被 77 截断的比例**。
- 🔑 **决定性实验**：对同一批样本，比较「**完整 caption 的文本嵌入**」与「**截断到 77 后的嵌入**」两两余弦分布 —— **若截断后显著更集中，则直接证实"截断助推坍缩"**。
- 背景假设：`LLaVA-OneVision-1.5 **Mid-Training**` 是**长 recaption**（为 MLLM 对齐设计），77 token 只装得下前 ~60 词；而长 recaption 的开头常是公式化场景描述，**区分性细节在后半段** → 截断后不同样本的文本互相更像 → 对比任务的"负样本"失去区分度。

**S2 空 / 极短 caption**
- `prep_data.py:55` 写的是 `(caps[j] or '').encode('utf-8')` —— `None` 会变成**空串**。
- 核查：统计空串与极短（<3 词）caption 的**占比**；若有可观比例，视为**数据缺陷**，给出过滤方案。

**S3 负样本质量（ImageNet 类内相似）**
- 只用 `imagenet/EN` 子集 → 1000 类、每类约 500 张 → **batch 内可能含同类样本**，"负样本"语义上近乎正样本。
- 核查：从 metadata 取类标签（若有），统计 **batch=32 时同 batch 内同类对的出现率**；或退而统计 batch 内 caption 两两余弦的分布。

**S4 text tower 未按设计冻结**（已确认）
- 任务书原意是「**固定 text tower，只动 vision**」，但 `train.py:117` 遍历的是 `model.named_parameters()`，**text 塔进了 optimizer**。
- ⚠️ 但 R3 探针已证：**仅冻结不够**（冻结随机 text 塔后 vision 仍坍缩到 0.9965）→ 修复要连 **S5** 一起做。

**S5 随机初始化文本塔本身无语义**
- R3 已实测：`[FRESH-RANDOM] TEXT same-tower offdiag mean = 0.6792` —— **随机文本塔的"不同文本"余弦已高达 0.68**，任务近乎退化。
- 核查：把 text 塔换成**有语义的**编码器（见 R4.4）后，该值是否显著下降。

**S6 数据规模 vs 对比学习需求**
- 500K 对 vs CLIP 的 400M 对（**800×**）；batch 32–64 vs 上千负样本。
- 核查：给出"在 500K/小 batch 下，对比学习是否本质可行"的判断，并**列出需要什么条件才可行**。

## R4.3 步骤 B —— 数据集对比：LLaVA vs **Stanford GPIC**

> 运维指出：图文对除了 LLaVA 85M，盘上**还有 Stanford GPIC**。请对比两者，回答"**用哪份数据、用哪种 caption 更适合对比学习**"。

- GPIC 路径（实测背景见 `DATA_LEDGER.md` / 任务书 §1.1）：
  `/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/`（含 `train` / `test` / `reference_stats`；
  tar 内 `{key}.json` + `{key}.jpg|png`，**caption 分 `tag` / `short` / `medium` / `long` 四种**）。

**对比维度（逐项列表 + 明确结论）**

| 维度 | 要回答什么 |
|:---|:---|
| 规模 | 图像数 / 对数；tar 数；总字节 |
| **caption 变体** | `tag` / `short` / `medium` / `long` 各自的长度分布 —— **哪一档最贴合 77-token 对比学习？** |
| 图像域 | 与 `imagenet/EN` 相比，领域分布是更集中还是更分散（影响负样本质量） |
| 数据-任务匹配 | 面向 CLIP 式短文本对比，还是面向 captioning / MLLM |
| 许可 | 能否入库、能否随论文发布 |
| 与 Stage (iv) 的关系 | 是否也能服务于 MLLM 对齐（避免两份数据重复投入） |

**核心假设（请验证或推翻）**：`LLaVA-OneVision Mid-Training` 的长 recaption **天然不适合** 77-token 对比学习；
而 **GPIC 的 `tag` / `short` caption 可能正好合适**。
→ 若成立，**换数据（或换 caption 档位）本身可能就解决大半问题**，不必换目标函数。

## R4.4 步骤 C —— 最小可行修复 + 判定实验（**R4 的核心产出**）

**在最小规模上**验证"修复能否让 C1–C4 通过"，**不要一上来就全量重训**。

**修复清单（逐项单独 + 组合验证，单变量优先）**
1. **冻结 text 塔**（修回设计意图）—— 已知单独不够，但必须做
2. **text 塔换成"有语义的"编码器**（关键）：
   - 优先：用**预训练语义文本编码器**（如现成的 CLIP/SigLIP text tower 或可用的小型预训练 LM）
   - 或：**把 text 塔与 vision 联合训练但给足规模与数据**（即回到 open_clip 标准配方）
3. **冻结 / 约束 `logit_scale` 与 `logit_bias`**（R3 已证：它们是"梯度饥饿"的吸收入口；固定 bias=0 单独不够，要与 2 合用）
4. **加大负样本**：batch ↑（显存允许内尽量大）+ 必要时跨卡 gather
5. **换数据或换 caption 档位**（按 R4.3 结论）
6. **丢弃空 / 极短 caption**（按 S2 结论）

**判定实验（每条 ~300 步、单卡或 2 卡，便宜）**
- 每配置独立跑 **300 步**，量 **C1 / C2 / C4**；对**最优 1–2 个配置**再补 **C3**（eval5k R@1）。
- 对照基线：**现状配置**（应复现坍缩，作为负对照）。
- ⚠️ 必须**单变量逐步加**，否则无法归因。逐条记录"加了什么 → C1–C4 各变了多少"。

## R4.5 步骤 D —— 路线裁定（按实验证据，不预设）

| 若 | 则 |
|:---|:---|
| **存在某组合让 C1–C4 全过** | → **固定该 recipe**，给出放大到全量（3000–10000 步 / 4 架构）的预算与命令，作为 R5 的输入 |
| **组合后仍坍缩** | → 明确写"**在 500K–85M 量级、从零、对比学习不可行**"，并给出**替代路线**的评估：<br>① **改目标为重构型（MAE/MIM）** —— 无 text 塔、无对比、无坍缩，**且完整保留"从零对比架构"的科学性**；<br>② **改用现成预训练视觉编码器** —— Stage (iii) 从"从零训练"改为"选型评估" |

> 运维倾向：**优先 ①（MAE）**，因为它不牺牲 Stage (iii) 的核心贡献。**但一切以 R4.4 的实验证据为准**。

---


## R4.6 交付物

1. **`run/EXPERIMENTS_VISION_ROUND4.md`**（新文件），必含四块：
   - **S1–S6 六条怀疑的逐条结论**（证实 / 排除 / 影响多大）
   - **LLaVA vs Stanford GPIC 数据集对比表** + 明确推荐（用哪份、用哪档 caption）
   - **修复实验结果表**：每配置 → C1 / C2 / C4；对最优 1–2 个配置补 **C3（eval5k R@1）**
   - **路线裁定**：若已有配置全过 → 给出放大重跑（4 架构 × 3000–10000 步）的预算与命令；
     若仍坍缩 → 给出 MAE / 现成编码器两条替代路线的评估与建议
   - 末尾附 **「论文回填建议」**（§6 该怎么写，含是否要把"坍缩"写成发现）
2. 新建/更新 ROUND4 HTML（自包含，与既有报告同风格）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` —— 论文由外部统一回填。
4. 正常更新 `MEMORY_VISION.md` + `daily-memories-vision/`；git commit + push（走既有同步规则）。

## R4.7 约束

- **总预算：R4 墙钟 ≤ 6 小时**。优先级 **A（6 条怀疑）> B（数据集对比）> C（修复实验）> D（裁定）** ——
  **A/B 都是 CPU 级、很快，先把便宜的事做完再动 GPU**；超时按此逆序裁剪。
- **GPU**：只用 `10.239.2.12`；**绝不杀他人进程**。
  ⚠️ **pretrain 任务（`10.239.2.29`）正在跑 P-3 / P-4**，与你这台**共享同一块 `/nas_train` NFS**：
  启动重 I/O 前先读 `run/MEMORY_PRETRAIN_2B.md` 看它在做什么，尽量避免重叠；无法避免则在报告中注明。
- **每次测量记录 GPU 独占核验 + NFS 并发核验的原文**（沿用 R2-4 的做法）。
- 🚫 不碰 data agent（`baize_data_loop.sh`）/ ops relay（`ops_relay.sh`）/ pretrain 的文件。
- ⚠️ **绝不要为了"看起来收敛"而调参掩盖坍缩**。若某配置仍坍缩，**如实记录**。
  **本任务的价值在于给出真相，不在于给出好看的数。**
- ⚠️ 若 A/B 阶段就发现"根因确凿且修复明确"，**可直接跳到 C**，不必机械走完清单。

---



# ══════════════ ROUND 3 · 第三轮任务（**已完成**，结论见 `EXPERIMENTS_VISION_ROUND3.md`）══════════════


## R3.0 状态切换（**先做**）

**MODE 已从 Round 2 切换为 Round 3。** 你在 `MEMORY_VISION.md` 里看到的
`PHASE=R2_complete` / `WAITING: 1` 是 **Round 2 的终态**，现已作废。

本唤醒请：把 `PHASE` 改为 `R3_active`、`WAITING` 改为 `0`，流水追加一条"R3 启动"。
**Round 1 / Round 2 的结论全部保留作基线，不要重跑。**

## R3.1 要解决的问题

R2-2 实测：`eval5k` 检索 **R@1/5/10 = 0.0002 / 0.0010 / 0.0020**，也就是
**恰好 1/5000、5/5000、10/5000**——**三个数精确等于随机水平**。

⚠️ 这不正常，且有两种完全不同的解释：

| 解释 | 预期表现 | 应对 |
|:---|:---|:---|
| **A. 训练不足**（从零、只训 3000 步） | 通常在随机**之上**一点（如 0.001~0.01），而非精确 1/5000 | 延长训练 horizon |
| **B. 评测坏了**（排序完全随机） | **精确等于 chance** ← 目前观察到的正是这个 | 修评测，重跑 R2-2 |

**因此 R3 的第一件事不是加训练，而是先判定是 A 还是 B。** 步骤 A 很便宜（~30min），
且**可能直接给出答案**，不要跳过它直接跑 20k。

## R3.2 步骤 A —— 评测自查（**先做，便宜**）

> 目标：判定 eval5k 检索是否**真的在测东西**。

1. **对照训练期指标**：从胜出配置的训练日志里取**同一 ckpt** 的 **in-batch 对比准确率**
   （open_clip 训练时会记录 `image_acc`/`text_acc`/`clip_acc` 一类指标）。
   - 若训练期 in-batch 准确率**明显高于** `1/batch`（如 >10%），而 eval5k R@1 = 1/5000 →
     **强烈指向评测坏了（B）**
   - 若训练期 in-batch 准确率也≈随机 → 指向训练不足（A）
2. **自检索 sanity**：用**同一张图与其自身 caption** 做检索，预期应≈100%。
   若自检索都不是 100% → **特征/配对有 bug**。
3. **特征一致性核验**：确认 eval 用的是**该 ckpt 的 vision + text 两塔**（不是随机 init 的 text），
   且图像 preprocess（resize/crop/normalize）与训练**逐字一致**。
   - ⚠️ 特别注意：本设置下 **text tower 是"冻结 + 随机初始化"** 的，四架构共用。
     若 eval 时**重新 init 了 text tower** 或用了不同的 text 塔 → 检索必然随机。
4. **打乱对照**：把 image↔text 配对**随机打乱**后再检索，结果应≈chance；若与未打乱时**一样**，
   说明检索对配对不敏感 → 评测坏了。
5. **若判定为 B**：**修复评测脚本后重跑 R2-2 的两臂**（SigLIP / CLIP InfoNCE），
   用**修好的** R@K 更新 `tab:visobj` 的回填建议。

## R3.3 步骤 B —— 若判定为 A：延长 horizon

- 胜出架构 **OpenVision2**，R2 锚点不变（224/16 / lr=3e-3 / SigLIP / en500k / seed1234 / bs 32×6）。
- 训练延长到 **20000 步**，在 **5000 / 10000 / 20000 步**各记一次 `eval5k` 的 **R@1/5/10（t2i 与 i2t）** + loss。
- **产出「训练步数 → 下游检索能力」曲线**——这同时回答两件事：
  ① 检索退化是否只是训练量问题；② **Stage (iv) 该把编码器训多久**。

## R3.4 步骤 C —— 若 B 后仍≈chance：换口径

- 试**同源 held-out**：从 `imagenet/EN` 里切 5k（与训练所用 shard **不相交**）作为 held-out，
  而不是跨源的 `laioncn/EN`。跨源检索对从零小模型可能过难。
- 报告两种口径的对比，并给出「哪个适合当论文的代理指标」的结论。

## R3.5 交付物

1. `run/EXPERIMENTS_VISION_ROUND3.md`（新文件）：步骤 A/B/C 的结果 + 结论 + 可复现命令 +
   **「论文回填建议」**（`tab:visobj` 该用什么指标，或如实写"无有效代理指标"）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT_ROUND2.html` 或新建 ROUND3 HTML（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` —— 论文由外部统一回填。
4. 正常更新 `MEMORY_VISION.md` + `daily-memories-vision/`；git commit + push（走本任务既有的同步规则）。

## R3.6 约束

- **总预算：R3 墙钟 ≤ 5 小时**。优先级 **A > B > C**；超时按此逆序裁剪，并在报告记录。
- **GPU**：只用 `10.239.2.12`。**绝不杀他人进程**。
  ⚠️ **pretrain 任务（`10.239.2.29`）正在跑 R2 的 P-2/P-3**——两台机器共享同一块 `/nas_train` NFS，
  启动重 I/O 前先读 `run/MEMORY_PRETRAIN_2B.md` 看它是否在训练，**尽量避免重叠**；若无法避免则在报告中注明。
- **每次测量都要记录 GPU 独占核验 + NFS 并发核验的原文**（沿用 R2-4 的做法）。
- 🚫 **不要碰** data agent（`baize_data_loop.sh`）与 ops relay（`ops_relay.sh`）。

---


# ══════════════ ROUND 2 · 第二轮任务（2026-10-01 生效，**优先于下方 Round 1**）══════════════

## R2.0 状态切换（**先做**）

**MODE 已从 Round 1 切换为 Round 2。**
- `MEMORY_VISION.md` 中的 `PHASE=converged` / `WAITING=1` / "任务终结" 是 **Round 1 的终态，现已作废**。
- 本唤醒请：把 `MEMORY_VISION.md` 的 `PHASE` 改为 `R2_active`、第 3 行 `WAITING: 1` 改为 `WAITING: 0`，并在流水追加一条"R2 启动"。
- **Round 1 的结论仍然有效，作为 R2 的对照基线，不要重跑 S0–S9。**

## R2.1 为什么要做第二轮（三个硬伤）

Round 1 的 S0–S9 结果里有三处**让论文 §6 站不住**的问题，全部可以用**现有数据/代码/checkpoint**重跑修复：

1. **`tab:visres`（分辨率/patch）六个格子的 loss 完全相同（全是 4.9962）** —— 这是 `lr=1e-3` 在 3000 步 cosine 下把 LR 衰减到 min、把 loss 钉在地板造成的**伪影**。该表**零信息量**，论文正文也自认如此。
2. **`tab:visobj`（SigLIP vs CLIP）的 loss 不可跨目标比较**（4.9962 vs 2.8941 量纲不同），论文自认 "not directly comparable"。这是审稿人的现成靶子。
3. **"loss 与架构无关"这个结论是在 196 token 下得到的** —— 而那恰恰是论文自己论证"SSM/MoE 无法摊薄开销"的区间，**结论自证**。换个 token 预算重测，无论结果如何都更有说服力。

## R2.2 实验清单（按优先级，全部基于现有数据 `en500k` / `eval5k` 与现有代码）

> **统一锚点改动（R2 全局）**：把 learning rate 从 Round 1 的 `1e-3` 改为 **`3e-3`**。
> 依据：Round 1 的 S8 已实测 `3e-3 → loss 4.4562`，显著优于 `1e-3 → 4.9962`，即 1e-3 在 3000 步下是**退化配置**。
> 其余锚点不变：SigLIP / AdamW(0.9,0.95) / warmup 100 + cosine / seed 1234 / bf16 / batch 32×8 / en500k / steps 3000。

| ID | 内容 | 目的 | 估时 |
|:--|:--|:--|:--|
| **R2-0** | **数字核对（零成本，最先做）** | 见下 | 0.2h |
| **R2-1** | **分辨率/patch 消融重跑**：OpenVision2 × 6 组 `{224,336,448}×{14,16}` @ **lr=3e-3** × 3000 步 | **替换 `tab:visres`** | 1.5h |
| **R2-2** | **目标函数消融改用可通约指标**：SigLIP vs CLIP InfoNCE @ lr=3e-3 × 3000 步，**主指标 = eval5k 检索 R@1/5/10** | **替换 `tab:visobj`** | 0.7h |
| **R2-3** | **架构 × 分辨率矩阵**：4 架构 × 3 分辨率（用 **patch=14**：224/14=256 tok、336/14=576、448/14=1024）× 3000 步 @ lr=3e-3 | **新增，最高科学价值** | 2.5h |
| **R2-4** | **干净吞吐复测**：4 架构 × 锚点配置，跑 ≥300 步取稳态 img/s + 推理 ms/img | **消除"共享集群争用"caveat** | 0.7h |
| **R2-5** | **MambaEye batch=1 停摆诊断**（**时间盒 40 分钟**，超时即停） | 替换表格里的 `hang@bs1` | 0.7h |

**R2-0 数字核对（必做，零成本）**
- 核对论文 `tab:visarch` 的 `Loss@5k = 4.456` 到底对应哪个步数：`EXPERIMENTS_VISION.md` 写的是 S3 长跑 **4.4540**（10k 步 @ lr=1e-3），而 S8 的 lr=3e-3 @3000 步是 **4.4562** → **给出四架构的「步数 → loss」映射表**，判定论文标注是否写错。
- 核对 `tab:visarch` 其余数值（2139 / 6.51 / 505.0M / 1459 / 790 / 852 / 141.7）与最新记录是否一致。

**R2-1 细节**
- 6 组：`(224,16) (336,16) (448,16) (224,14) (336,14) (448,14)`，各 3000 步 @ **lr=3e-3**。
- **额外补 1 组 `(224,16) @ lr=1e-3`** 作为「坍缩对照」，用于在报告里**显式证明** Round 1 那张全同表是 LR 伪影。
- 每组记录：**loss@3000、train img/s（稳态）、推理 ms/img（batch=1）、tokens/img、eval5k 检索 R@1/5/10**。
- 注：S8 已有 `(224,16)@lr=3e-3` 的 loss=4.4562，可直接复用做一致性校验，不必重跑该点。

**R2-2 细节**
- 2 臂（SigLIP / CLIP InfoNCE），OpenVision2，lr=3e-3，3000 步，其余同锚点。
- **主指标改用 eval5k 的检索 R@1/5/10**（跨目标函数可通约）；loss 并列展示但**必须标注「不可跨目标比较」**。
- 用 `vision/eval_downstream.py`（需 full ckpt；Round 1 的 S4+ train.py 已保存 full ckpt）。

**R2-3 细节**
- 12 组 = 4 架构 × 3 分辨率；patch 固定 14（token 数 256 / 576 / 1024）。
- 每组记录：loss、train img/s、**推理 ms/img（batch=1 与 batch=8 都测**，因 MambaEye batch=1 停摆）、tokens/img、R@1。
- 🚨 **必须匹配 batch，否则全盘作废**：R2-1 已实测 **`448/14`（1024 token）因 VRAM 约束被自动降 `batch 32→16`，loss 掉到 3.7461**，
  而 **SigLIP loss 对 batch（负样本数）高度敏感**——batch 减半 → 负样本减半 → 可达成 loss 更低。
  因此 **`3.7461` 不能归因于"1024 token 学到更好表示"**。
  → **R2-3 必须让全部 12 组用同一个 batch**（若 1024 token 放不下 bs=32，就**全部降到 bs=16**，
    或启用 grad-ckpt 保持 bs=32）。**任何 batch 不一致的格子都必须在报告里显式标注为不可比**。
- ⚠️ **`eval5k` 检索 R@1/5/10 目前是退化指标**（R@1 = 0.0002 = 1/5000，恰为随机水平）：
  R2-1 已证实它**对 lr 与分支零区分度**。R2-3 的 `R@1` 列**不要当主指标**；
  若它仍是随机水平，就在报告里如实写"该代理指标在本设置下无区分度"，改用 loss + 吞吐 + 收敛轨迹判读。
- **判读**：若在 256→1024 token 区间四架构仍不可区分 → 「架构在 loss 上不可区分」的结论**强度大增**（跨 token 预算稳健）；若出现分化 → **找到了一个真实的架构结论**（这才是论文想要的）。两种结果都可发表。
- ⚠️ 高 token 数会显著变慢（448/14 是 224/16 的 5.2 倍 token），**先跑低 token 再跑高 token**，超预算就只报已完成的格子。

**R2-4 细节**
- **先做 GPU 独占核验**：`ssh 10.239.2.12 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'`，确认 GPU 0–7 无其他项目进程；**把核验结果原文记入报告**（这是这次测量的可信度凭证）。
- ⚠️ **还要查 NFS 并发（关键）**：本任务与 **pretrain 任务**（`baize_pretrain_loop.sh`，训练在 `10.239.2.29`）
  **共用同一块 `/nas_train` 盘**。Round 1 的吞吐正是被这类并发争用污染的，不能重蹈。测量前请额外：
  - 读 `run/MEMORY_PRETRAIN_2B.md`（**共享盘，你直接可见**）确认它当时**有没有在跑训练**；
  - 把"当时 pretrain 任务的运行状态"**原文写进报告**；
  - 若发现它有训练在跑，**先去做其它 R2 项、稍后再回来测 R2-4**
    （pretrain 那边已被要求优先避让你的 R2-4，通常它会主动等待）。
- 4 架构各跑 ≥300 步取稳态 img/s；推理 ms/img 同测。
- 若发现有人在用 GPU 0–7，**报告注明并等待下一轮**，不要与他人争抢。

**R2-5 细节**
- 二分 `batch ∈ {1,2,4,8}` 找停摆阈值；查 `mamba_ssm` 版本 / selective_scan kernel；判断是 kernel 卡死还是代码路径问题。
- **时间盒 40 分钟**，到点即停，报告已查明部分。

## R2.3 交付物

1. **`run/EXPERIMENTS_VISION_ROUND2.md`**（新文件）：R2-0~R2-5 全部结果表 + 每条可复现命令 + 与 Round 1 的差异说明 + **「论文表格回填建议」段落**（给出 `tab:visres` / `tab:visobj` / `tab:visarch` 的建议替换内容，含精确数值）。
2. 更新 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html` 或新建 `BAIZE_VISION_ENCODER_RESULT_ROUND2.html`（自包含）。
3. 🚫 **不要修改** `doc/BaiZe-ISEDA2027/BaiZe-ISEDA2027/ISEDA2027/*.tex` 与 `main.tex`——论文已由外部统一重构并推送，回填由外部完成。你只需在报告里给出「回填建议」。
4. 正常更新 `MEMORY_VISION.md` 与 `daily-memories-vision/`。
5. git commit + push（沿用原规则：只提交 `doc/` 文本与脚本；checkpoint / 图像中间产物不入库）。

## R2.4 约束

- **总预算**：R2 墙钟 **≤ 6 小时**（下次运维介入前）。超时按 **R2-0 > R2-1 > R2-4 > R2-2 > R2-3 > R2-5** 逆序裁剪，并在报告记录裁剪决策。
- **GPU**：只用 `10.239.2.12` 的 **全部 8 卡（GPU 0–7）**；**绝不杀他人进程**。
- **每次测量都必须记录当时的 GPU 占用核验结果**（这是 R2-4 要解决的核心问题，不能重蹈覆辙）。
- 串行优先，卡数/并发对齐，保证可比。

---



> ⚠️ 本文件为只读指令文件，agent **禁止修改**本文件。所有运行时状态写入本任务专属的 `MEMORY_VISION.md`、`EXPERIMENTS_VISION.md` 和 `daily-memories-vision/`（**不要**写入 1B 的 `MEMORY.md`/`EXPERIMENTS.md` 或 2B 的 `MEMORY_2B.md`/`EXPERIMENTS_2B.md`）。

你是推进 **BaiZe Stage(iii) 视觉编码器预训练** 的自动化 research agent（Cline），每次被唤醒后：读 `MEMORY_VISION.md` 恢复状态 → 读 `EXPERIMENTS_VISION.md` 看进展 → 读 `daily-memories-vision/$(date +%F).md` 恢复当日上下文 → 判断下一步 → **连续执行**（无阻塞时一口气做完可立即完成的步骤）→ 更新记忆文件 → 退出。

**持续推进原则（关键，避免「做一小步就睡」）**：
- **无阻塞任务时**：把能立即做完的步骤一口气连续做完（可跨越多个 PHASE），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟），不要做一小步就退出。
- **有异步阻塞任务时**（训练 running 等）：回写记忆并把 `MEMORY_VISION.md` 的 `WAITING` 置为 `1`，记录「等待什么、如何判断结束」，然后退出（loop.sh 据此拉长睡眠省 token）。下次唤醒先检查该任务是否结束，结束后把 `WAITING` 置回 `0` 再继续。

---

## 任务目标（24 小时预算，三层次结论）

在 **24 小时墙钟预算**内，对四个 **500–600M** 候选视觉编码器做**从零预训练**（随机初始化）的公平对比，分三层次产出：

1. **P0 基础（必做）——三组硬指标**：对比 loss 曲线（早期收敛 ~1000 步）、训练吞吐（image/s）、推理吞吐（图像→token/s）。锁定「默认配置 + 胜出架构」。
2. **P1 稳健（优先）——让排名可信**：长地平线（5k–10k 步）、多种子复现、下游代理评估（zero-shot / linear-probe 检索）。
3. **P2 核心自由度（论文重点）**：分辨率 / patch / 对比目标函数 / 数据侧（caption 粒度·规模·中英比例）消融。
4. **P3 训练超参与推理深度（有余量才做）**：LR / warmup 扫描、推理 batch/量化/分辨率深挖、装 SGLang 补生产级推理数据。

最终输出：一份胜出架构 + 完整可复现训练命令 + 多阶段对比报告（写入 `EXPERIMENTS_VISION.md` 顶部）+ HTML 结果报告 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含、可离线打开），并把胜出配置回填论文 `ISEDA2027/6_vision_encoder.tex`。

对应论文 `ISEDA2027/6_vision_encoder.tex`（当前 `[TBD]`）与计划 `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_PRETRAIN_PLAN.html`。

---

## 已定前提（固定，不要更改）

| 项 | 值 |
|:---|:---|
| 规模 | 500–600M / 架构（实测 `numel()`，±10% 内） |
| 四个候选架构 | **OpenVision 2**（纯 Attention）/ **MambaEye**（视觉 SSM）/ **MoE-ViE**（稀疏 MoE）/ **DeepEncoder V2**（Attention+SSM 混合） |
| **BASE_DIR** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` |
| 训练栈 | **OpenCLIP（open_clip 3.2.0）**，SigLIP/CLIP 对比学习，固定 text tower（只动 vision tower）；torchrun 直驱 |
| 训练数据 | LLaVA-OneVision-1.5（parquet）或 GPIC（tar），切一个**统一固定子集**供四架构复用 |
| 环境 | conda env `py310`（CUDA 12.8 / PyTorch 2.8.0 / torchvision 0.23.0 / open_clip 3.2.0 / timm 1.0.3 / mamba_ssm 2.2.6.post3 / flash_attn 2.8.4 / webdataset） |
| GPU | `10.239.2.12` **全部 8 卡（GPU 0–7，已实测空闲）** |
| **预算上限** | **24 小时墙钟**（按 P0 > P1 > P2 > P3 优先级裁剪，见「时间估计」） |

> 数据路径：
> - LLaVA-OneVision：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M/`（子集 imagenet/laioncn/datacomp1b/coyo/mint/obelics × EN/CN，parquet 图像+caption）
> - GPIC：`/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/`（tar 内 `{key}.json`+`{key}.jpg/png`，caption 分 tag/short/medium/long）
---

## 试验矩阵（S0–S9，按 P0→P1→P2→P3 优先级推进）

> **锚点原则（关键）**：先跑完 S0–S2 锁定「默认配置 + 胜出架构」，再以该配置为**锚点**做单变量扫描（S3+），避免过早并行把预算烧在低信息维度。所有新增试验延续「单变量、锚点对照」的公平口径。

### P0 基础（必做）：三项硬指标

| 阶段 | 内容 | 规模 | 产出 |
|:---|:---|:---|:---|
| S0 冒烟 | 4 架构 × 10–20 步 | 10–20 步/架构 | 可跑性 + 实测参数量 + 吞吐基线 |
| S1 主训练 | 4 架构 × 1000 步（默认配置） | 1000 步/架构 | loss 曲线 + image/s |
| S2 推理基准 | 4 架构 | batch=1 前向 | 图像→token/s |

**默认配置（S1 锚点，后续消融的对照基线）**：cls=224、patch=16、SigLIP、统一子集（如 LLaVA-OneVision imagenet-EN 前 100–200 万对 或 GPIC 1–2 tar + medium caption）、text tower=同一 small transformer、lr=1e-3、warmup+cosine、seed=1234、bf16。

### P1 稳健（优先）：让排名可信

| 阶段 | 内容 | 规模 |
|:---|:---|:---|
| S3 长地平线 | **胜出架构**（+可并列次优）延长训练，看 loss 排名是否翻转 | 5000–10000 步 |
| S4 多种子 | **决胜局**（前 2 架构）多 seed 复现 | 3 seed × 1000 步 |
| S5 下游代理 | zero-shot top-1（ImageNet 或适配 val）或 text→image retrieval R@K、linear-probe | 各架构 1 次 |

### P2 核心自由度（论文重点，锚点单变量扫描）

| 阶段 | 变量 | 取值 |
|:---|:---|:---|
| S6 分辨率 + patch | cls / patch | cls ∈ {224, 336, 448}；patch ∈ {14, 16}（各 1000 步） |
| S7 目标函数 + 数据侧 | 对比目标 / caption 粒度 / 规模 / 语言 | SigLIP vs CLIP InfoNCE；GPIC tag/short/medium/long；子集扩到千万级；中英比例 |

### P3 训练超参与推理深度（有余量才做）

| 阶段 | 变量 | 取值 |
|:---|:---|:---|
| S8 训练超参 | LR / warmup | lr ∈ {1e-3, 3e-3, 5e-3}；warmup 档位 |
| S9 推理深挖 | batch / 量化 / 分辨率 / SGLang | batch ∈ {1,8,32}；bf16 vs fp8；多分辨率；装 SGLang 补生产级吞吐 |

`EXPERIMENTS_VISION.md` 建议表头：
`| ID | 阶段 | 架构 | 参数量 | 变量 | 状态 | 最终loss | 训练image/s | 推理token/s | 耗时 | GPU·h | 备注 |`
---

## 四个必须遵守的关键决策

### 决策 1：统一「从零」——四架构均随机初始化
四架构均**随机初始化**，不加载任何 ImageNet/CLIP/SigLIP 上游权重（禁用 timm/open_clip 的 pretrained 入口）。仅对比架构本体。

### 决策 2：统一训练栈与目标函数
- 统一 **open_clip（3.2.0）** 训练栈：自定义 vision tower 注册到 open_clip + 固定 text tower；Mamba/MoE 层需手写模型（mamba_ssm 2.2.6 已装，可直接用）。
- 同一对比目标：**SigLIP**（sigmoid 对比，推荐）或 CLIP InfoNCE（默认选 SigLIP；S7 可做两者 A/B）。
- 同一 text tower（固定同一 small transformer + 同一 BPE，四架构共用，只动 vision tower）。
- 同一分辨率 / patch / 增强（除 S6 显式消融外）。

### 决策 3：参数量对齐 500–600M
四架构实测参数量（`sum(numel())`）须落 500–600M；偏差 >10% 需在报告注明「非等参对比」。MoE 需同时报告「总参数」与「每 token 激活参数」。

### 决策 4：推理基准——SGLang 未装，退化到统一前向 bench
⚠️ **已实测 `sglang` 未装**（`import sglang` ModuleNotFoundError）。**P0 主口径退化为统一前向 benchmark 脚本**（`torch.cuda.Event` / `torch.benchmark`），四架构同一代码路径、同一 batch=1 / 固定分辨率 / bf16 测量图像→token/s。相对结论可信；**S9 阶段可选择性安装 SGLang**（MLLM Stage iv 反正要用）补生产级吞吐，并在报告注明测量栈。
---

## 推进状态机（PHASE，按 S0→S9 顺序，每阶段前核对预算）

- **S0 data_check + smoke**：确认可用数据子集（选 LLaVA-OneVision 一段 或 GPIC 1–2 tar），验证 caption 可读、可切图像-文本对；`conda activate py310` 后确认 open_clip / mamba_ssm / flash_attn / webdataset 可 import、GPU 0–7 可见；落地 4 个 vision tower（open_clip 注册），跑 10–20 步冒烟，记录实测参数量 + 吞吐（image/s），参数量调平到 500–600M。某架构连续 3 次失败标记 `❌ NOT_RUNNABLE` 跳过 → `S1`
- **S1 main**：4 架构 × 1000 步（默认配置），记录 loss + image/s → `S2`
- **S2 infer**：统一前向 bench 测各架构图像→token/s（batch=1、固定分辨率）→ 汇总三指标，**确定胜出架构 + 默认配置锚点** → `S3`
- **S3 long_horizon**：胜出架构（+可并列次优）延长 5000–10000 步，看排名是否翻转 → `S4`
- **S4 multi_seed**：决胜局（前 2 架构）3 seed × 1000 步复现 → `S5`
- **S5 downstream**：zero-shot top-1（open_clip 内置 `/ val-data`）或检索 R@K、linear-probe → `S6`
- **S6 scale_ablation**：cls ∈ {224,336,448}、patch ∈ {14,16}（锚点单变量，各 1000 步）→ `S7`
- **S7 objective_data**：SigLIP vs CLIP；GPIC caption 粒度；子集规模；中英比例 → `S8`
- **S8 hparam**：lr ∈ {1e-3,3e-3,5e-3}、warmup 档位 → `S9`
- **S9 infer_deep**：batch ∈ {1,8,32}、bf16 vs fp8、多分辨率；（可选）装 SGLang 补生产级吞吐 → `converged`
- **converged**：汇总各阶段对比表 + 胜出架构 + 可复现命令到 EXPERIMENTS_VISION.md 顶部；生成 HTML 结果报告；回填 `6_vision_encoder.tex`；git commit + push；停止新实验

> **预算守卫**：每阶段启动前核对 `BUDGET_USED`（≤ 24h）。逼近上限时按 P3 → P2 → P1 逆序裁剪（P0/P1 必保），并在 EXPERIMENTS_VISION.md 注明裁剪决策。
---

## 记忆管理

- `run/MEMORY_VISION.md` — 运行时状态（PHASE/WAITING/ERROR_COUNT/BUDGET_USED/看板/流水）
- `run/EXPERIMENTS_VISION.md` — 实验记录表（核心产出）
- `run/daily-memories-vision/$(date +%F).md` — 当日操作日志

启动恢复：读 MEMORY_VISION → EXPERIMENTS_VISION → 当日日志 → 判断下一步 → 执行 → 回写。

---

## GPU 资源与进程管理

- 主节点 `10.239.2.12`，用 **全部 8 卡（GPU 0–7）**（已实测空闲 0 MiB）。
- 检查占用：`ssh 10.239.2.12 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'`
- 只杀本项目残留（`pgrep -af 'torchrun|open_clip_train|open_clip|pretrain'`），杀前记 PID 到 MEMORY_VISION 流水；**不杀他人进程**。GPU 0–7 全部 8 卡归本项目使用，无他人占用。
- 卡数对齐：四架构须同卡数（8 卡 TP1/DP8），训练 image/s 才可比。

---

## 时间估计（24 小时墙钟，量级 + 以冒烟实测反推）

| 优先级 | 阶段 | 内容 | 估时（串行 8 卡） |
|:---|:---|:---|:---|
| P0 | S0–S2 | 冒烟 + 主训练 + 推理基准（4 架构） | 2–4 h |
| P1 | S3–S5 | 长地平线 + 多种子 + 下游代理 | 3–6 h |
| P2 | S6–S7 | 分辨率/patch + 目标函数/数据 | 4–8 h |
| P3 | S8–S9 | LR/warmup + 推理深挖 + SGLang | 2–6 h |
| — | 余量/重试 | OOM / 报错重跑 / 抖动 | 2–4 h |
| **合计** | S0–S9 | — | **约 13–28 h，上限 24 h** |

> 反推口径：S0 冒烟读 steady-state `ms/iter → image/s → N 步 ETA = N × ms/iter / 1000`。每阶段启动前用实测吞吐校准该阶段 ETA；若逼近 24h 上限，按「预算守卫」裁剪低优先级阶段（P3 → P2 → P1 逆序），并在 EXPERIMENTS_VISION.md 记录。

---

## 验收产出

1. 胜出架构 + 完整可复现训练命令（写 `EXPERIMENTS_VISION.md` 顶部）
2. `doc/BaiZe-ISEDA2027/BAIZE_VISION_ENCODER_RESULT.html`（自包含：四架构 loss/训练/推理对比 + 稳健性 + 消融 + 胜出结论 + 命令）
3. 回填 `ISEDA2027/6_vision_encoder.tex` 的 config/results（表格与文字）
4. git commit + push（只提交 `doc/` 文本 md/html/sh/json；checkpoint/图像中间产物不入库）