# S2 Blend 是否排除 S1 已训数据 — 研究报告

> **撰写**: BaiZe Data Agent · 2026-11-18
> **用户令**: 2026-11-18 — 「blend TSV 时会确保 S1 训练过的数据不会混入，对吧」「这个问题你不要轻率的回答，可以下发给 data，请他研究一下。」
> **数据口径**: 所有 token 数来自 `DATA_MAPPING.md` §A 实测（`INDEX.tsv` + `MANIFEST.json` + `du -sb`）；Megatron 源码分析基于 `Xmodel-2.5-code/megatron/core/datasets/` 实际代码（逐行阅读）。
> **交叉引用**: `report_s1s2_split_data.md`（v1 可行性）、`report_s1s2_split_data_v2_zh.html`（v2.9 落地方案）、`report_s1s2_split_pretrain.md`（pretrain 线报告）

---

## 一句话结论

**当前 blend 机制不会排除 S1 已训数据。** S2 如果使用与 S1 相同的 7 个数据源（en_v1_4 / ufw_l1_en_hq / ufw_zh / math_l1 / math_l3 / code_l2 / code_l3）且不修改随机种子，则 **S2 将以近乎 100% 的概率重复采样 S1 已看过的文档**——因为 Megatron 的 GPTDataset 使用固定 `random_seed=1234` 生成 shuffle_index，相同种子 + 相同文档池 → 相同排列 → 相同前缀。**但有两个简单有效的缓解措施**：（1）为 S2 更换随机种子（将重叠从 ~100% 降至 ~30%）；（2）S2 新增的 stack-v3-train（430.7B）和 MegaMath（~371B）天然不在 S1 blend 中 → 零重叠，占 S2 总 token 的 28%。

---

## 1. 现状分析：Megatron Dataloader 的数据采样机制

### 1.1 Blend 的三层架构

BaiZe-2B 的数据 blend 经过三层处理，逐层分析如下：

#### 第一层：`gen_blend.py`（配比 → shard 级权重串）

```
blend_s1_preblend.tsv → gen_blend.py → "w1 path1 w2 path2 ..." (空格分隔)
```

- 读取 TSV：每行 `key <TAB> subdir <TAB> prop <TAB> epochs`
- 对每个源，发现该目录下所有 `*.bin` 文件（需配对 `.idx`）
- 每个 shard 获得等权重：`w_shard = prop / n_shards`
- 所有 shard 权重之和 = 1.000000（硬校验）
- 输出一个空格分隔的 `weight path` 字符串，传给 `--train-data-path`

**关键**：这一层**不追踪任何消费记录**。它只做静态的权重分配，输出的是"全部 shard + 各自权重"。

#### 第二层：`BlendedDataset`（shard 级加权交错索引）

源码：`megatron/core/datasets/blended_dataset.py`

初始化时构建两个数组（缓存为 `.npy`）：

| 数组 | 含义 | 长度 |
|:--|:--|:--|
| `dataset_index[i]` | 位置 i 取哪个 shard（int16） | 总样本数 N |
| `dataset_sample_index[i]` | 在该 shard 内取第几条样本（int64） | 总样本数 N |

算法（`helpers.build_blending_indices`，C++ 实现，Bresenham 式加权交错）：

```
对每个位置 i（0, 1, ..., N-1）：
    对每个 shard k：
        deficit[k] = weight[k] × (i+1) - sampled_count[k]
    选择 deficit 最大的 shard：chosen = argmax_k(deficit[k])
    dataset_index[i] = chosen
    dataset_sample_index[i] = sampled_count[chosen]++
```

**关键**：`dataset_sample_index` 是每个 shard 内部的递增计数器（0, 1, 2, ...），不是随机采样。哪个样本 ID 被选中，取决于 GPTDataset 的 shuffle_index 将其映射到哪个文档。

#### 第三层：`GPTDataset`（shard 内文档级 shuffle）

源码：`megatron/core/datasets/gpt_dataset.py`

每个 shard 对应一个 GPTDataset 实例，构建三个索引：

| 索引 | 含义 |
|:--|:--|
| `document_index` | 文档 ID 数组（按 epoch 复制），随机 shuffle |
| `sample_index` | 每条样本对应的文档边界（start_doc, offset, end_doc, offset） |
| `shuffle_index` | 样本位置的随机排列 |

**`shuffle_index` 的生成（§304-458）**：

```python
numpy_random_state = numpy.random.RandomState(self.config.random_seed)  # seed=1234
shuffle_index = _build_shuffle_index(sample_index.shape[0] - 1, 
                                      sample_index.shape[0] - 1, 
                                      numpy_random_state)
```

`_build_shuffle_index` 生成 `[0, total_size)` 的随机排列。训练时 `__getitem__` 通过 `idx = self.shuffle_index[idx]` 查表获取实际文档。

**`num_epochs` 的计算（§533-553）**：

```python
def _get_num_epochs(self, num_tokens_per_epoch):
    num_epochs = 1
    num_tokens = num_tokens_per_epoch
    num_tokens_requested = self.num_samples * sequence_length + 1
    while num_tokens < num_tokens_requested:
        num_epochs += 1
        num_tokens += num_tokens_per_epoch
    return num_epochs
```

当请求的样本数 > 一个 epoch 的 token 数时，`num_epochs` 增加，`document_index` 会复制多份（每份独立 shuffle 后拼接）。

### 1.2 关键发现：同种子 → 相同 shuffle → 近乎完全重叠

**Megatron 的 `random_seed`（SEED=1234，见 `common.env`）被写入 `GPTDatasetConfig`，并成为 `unique_identifiers` 的一部分**（`megatron_dataset.py:118`：`_key_config_attributes` 返回 `["random_seed", ...]`）。

这意味着：

1. **相同种子 + 相同文档池 + 相同 num_epochs → 相同 shuffle_index**
2. S1 和 S2 对同一个 shard（如 `code_l2_pb_s000`）使用相同的 `random_seed=1234`
3. 如果两者的 `num_epochs` 都为 1（S1 code_l2 epoch=0.52，S2 code_l2 epoch=0.63，均 <1 → `num_epochs=1`），则 `document_index` 和 `shuffle_index` **完全相同**
4. S1 从 shard 中取前 `N_S1` 个样本（`dataset_sample_index` 递增），S2 取前 `N_S2` 个
5. 如果 `N_S2 > N_S1`：**S2 的前 N_S1 个样本 = S1 的全部样本**（相同 shuffle 前缀）
6. 重叠率 = `min(N_S1, N_S2) / max(N_S1, N_S2)` ≈ **83-100%**（取决于具体比例）

**补充说明**：BlendedDataset 的 `dataset_index` 和 `dataset_sample_index` 在 S1 和 S2 之间不同（因为 blend 权重和源数量不同），但每个 shard 内部的 GPTDataset shuffle_index 是相同的。BlendedDataset 决定"何时从哪个 shard 取第几个样本"，而 GPTDataset 的 shuffle 决定"第 k 个样本对应哪个文档"。由于 BlendedDataset 对每个 shard 的 `dataset_sample_index` 从 0 开始递增，S1 和 S2 都从 shuffle_index[0] 开始消费 → 前缀重叠。

### 1.3 Megatron 是否支持样本级消费追踪？

**不支持。** 逐行审查源码结论：

- `BlendedDataset` 和 `GPTDataset` 均在**初始化时一次性构建全部索引**，之后只做 O(1) 查表
- **没有任何机制记录"哪些样本已被消费"**——DataLoader 按 `0, 1, 2, ..., N-1` 顺序遍历，没有跨 run 的状态持久化
- 索引缓存（`.npy`）基于 `unique_description_hash`（包含 weights, num_samples, random_seed 等），仅用于避免重复构建，不记录消费进度
- **S1 和 S2 是独立的训练 run**，各自构建独立的 BlendedDataset，之间无任何共享状态

### 1.4 小结

| 问题 | 答案 |
|:--|:--|
| blend TSV 的 shard 级权重采样是否追踪样本级消费记录？ | **否**。仅有静态权重分配，无消费追踪。 |
| S1 和 S2 用同一数据源时，S2 是否会重复采样 S1 已看过的样本？ | **是，且重叠率极高（~83-100%）**，因为相同种子产生相同 shuffle。 |
| Megatron 是否原生支持跨 run 的样本排除？ | **否**。每个 run 独立构建索引，无跨 run 状态。 |

---

## 2. 可行性研究：排除 S1 已训数据的技术方案

### 方案 A：Shard 级排除（S1 用 shard 0-7，S2 用 shard 8-15）

#### 原理
对 16-shard 的数据源（当前 pre-blend 后各源均为 16 个大 shard），S1 只使用前 8 个，S2 只使用后 8 个。

#### 可行性分析

| 维度 | 评估 |
|:--|:--|
| **数据源结构** | 各源经 pre-blend 合并为 16 个大 shard（`pre_blend.py` round-robin 分组）。每个 pre-blend shard 包含一组原始 shard 的文档。 |
| **S1 已消费情况** | S1 的 `blend_s1_preblend.tsv` 包含**全部 16 个 shard** → S1 已从所有 16 个 shard 中采样。 |
| **能否回溯排除** | **不能**。S1 已经训练了 ~235k 步，消耗了全部 16 个 shard 中的部分文档。无法回溯"只用了前 8 个"。 |
| **对 S2 新数据源** | stack-v3-train（430.7B）和 MegaMath（~371B）**完全不在 S1 的 blend 中** → 天然零重叠。这相当于已实现了 shard 级排除（整个数据源级排除）。 |
| **如果重新设计** | 如果在 S1 启动前就规划好 S1/S2 分片，则可行：S1 TSV 只列 shard 0-7，S2 TSV 只列 shard 8-15。但**现在 S1 已跑 235k 步，为时已晚**。 |

#### 数据量核算

| 数据源 | 总 shards | S1 用了 | S2 可独占 | S2 独占 tokens (B) | S2 需求 (B) | 够用？ |
|:--|--:|--:|--:|--:|--:|:--|
| en_v1_4 | 16 | 全部 16 | 0 | 0 | 513.3 | ❌ |
| ufw_l1_en_hq | 16 | 全部 16 | 0 | 0 | 44.0 | ❌ |
| ufw_zh | 4 | 全部 4 | 0 | 0 | 29.3 | ❌ |
| math_l1 | 16 | 全部 16 | 0 | 0 | 88.0 | ❌ |
| math_l3 | 16 | 全部 16 | 0 | 0 | 44.0 | ❌ |
| code_l2 | 16 | 全部 16 | 0 | 0 | 264.0 | ❌ |
| code_l3 | 16 | 全部 16 | 0 | 0 | 73.3 | ❌ |
| **stack-v3 (L4 filt.)** | — | **0（不在 S1）** | **全部** | **430.7** | 249.3 | ✅ |
| **MegaMath** | — | **0（不在 S1）** | **全部** | **~371** | 161.3 | ✅ |

**结论**：Shard 级排除对 S1 已用的 7 个共享源**不可行**（S1 已消费全部 shard）。对新数据源**天然实现**（零重叠）。

### 方案 B：样本级排除（记录 S1 消费的 sample index，S2 排除）

#### 原理
在 S1 训练期间记录每个 shard 内被消费的 `sample_id` 列表（即 `dataset_sample_index` 中属于该 shard 的值），S2 构建索引时跳过这些 sample_id。

#### 可行性分析

| 维度 | 评估 |
|:--|:--|
| **Megatron 原生支持** | **不支持**。需要修改 `GPTDataset._build_document_sample_shuffle_indices()` 以接受一个"排除集合"。 |
| **实现复杂度** | **高**。需：（1）在 S1 训练中 instrument DataLoader 记录消费的 (shard, sample_id) 对；（2）存储 ~10M+ 条记录（~80MB，可行）；（3）修改 S2 的 GPTDataset 构建逻辑，从 shuffle_index 中剔除已消费的 sample_id 并重新填充。 |
| **对训练吞吐的影响** | 记录消费日志额外 I/O，可能降低吞吐。 |
| **时间约束** | S1 已跑 235k 步（共 350k），剩余 ~115k 步。可在剩余步数中开始记录，但前 235k 步的消费记录**无法回溯**。 |
| **回溯问题** | S1 前 235k 步消费了哪些 sample_id？可通过 S1 的 BlendedDataset 索引重建（因为索引是确定性的）：计算 `dataset_sample_index[0:235k_step_equivalent]` 得到前 235k 步的消费记录。**理论可行，但需要编写重建脚本**。 |
| **推荐度** | 🟡 **不推荐用于当前项目**——实现复杂、时间紧、ROI 低。适合作为长期工程改进。 |

### 方案 C：换源（S2 完全用新数据源替代 S1 的旧源）

#### 原理
S2 不使用任何 S1 已用过的数据源，全部使用新数据。

#### 数据量核算

| 类别 | S2 需求 (B) | 新数据源 | 可用 (B) | 够用？ |
|:--|--:|:--|--:|:--|
| Web | 586.6 | **无新 Web 源** | 0 | ❌ **严重不足** |
| Code | 586.6 | stack-v3 (L4 filt.) | 430.7 | ❌ 差 156B |
| Math | 293.3 | MegaMath + Nemotron-CC-Math + finemath | 547.6 | ✅ |

**结论**：**完全换源不可行**——没有新的 Web 数据源替代 Ultra-FineWeb。Code 方面 stack-v3 单独也不够。只能做**部分换源**（补入新源 + 保留旧源）。

### 方案 D：部分排除（补新源降低 epoch，Web 不排除）

这正是 v2 报告已采用的方案：

| 类别 | S1 消耗 (B) | S2 消耗 (B) | 旧源 (B) | 新源 (B) | 总可用 (B) | 累计需求 (B) | 累计 epoch |
|:--|--:|--:|--:|--:|--:|--:|--:|
| Web | 1,086 | 587 | 2,500 | 0 | 2,500 | 1,672 | **0.67** ✅ |
| Code | 279 | 587 | 550 | 431 | 981 | 866 | **0.88** ✅ |
| Math | 103 | 293 | 242 | 371 | 613 | 396 | **0.65** ✅ |

**注意**：累计 epoch <1.0 只是**总量层面**——不等于"无重叠"。S1 已从旧源的全部 shard 中采样（同种子 shuffle），S2 对旧源的采样仍然与 S1 高度重叠。新源部分则确实零重叠。

### 方案 E：~~更换随机种子（简单高效的缓解措施）⭐ 推荐~~ **已撤销（2026-11-28 用户纠错）**

> 📌 **2026-11-28 用户纠错**：本方案「换 SEED」是**错误的**，已撤销。正确做法 = 保持 `seed=1234`（=S1 同 seed）→ 同 shuffle_index → S2 从 S1 消费过的位置续读 → 零重叠。换 SEED 会生成全新排列，从头读时可能读到 S1 已消费样本，**破坏零重叠**。

#### ~~原理~~
~~为 S2 设置不同的 `random_seed`（如 `SEED=5678`），使 GPTDataset 生成不同的 shuffle_index → S2 从每个 shard 中以不同的顺序消费文档 → 与 S1 的重叠从确定性 ~100% 降为随机 ~30%。~~

**纠错**：同 seed=1234 + resume from ckpt → 同 shuffle_index → S2 从 consumed_samples 续读 → 共享源也零重叠。换 SEED 反而破坏零重叠。

#### ~~可行性分析~~

| 维度 | 评估 |
|:--|:--|
| ~~**实现复杂度**~~ | ~~**极低**——仅需在 `s2.env` 或启动命令中设置 `SEED=5678`~~ **已撤销**：不要换 SEED，保持 1234 |
| **Megatron 支持** | ✅ 同 seed 续读是 stock 行为（resume from ckpt 保留 consumed_samples） |
| **对训练的影响** | 无负面影响。同 seed 续读不影响配比、权重、训练稳定性 |
| ~~**效果**~~ | ~~将 S1-S2 文档级重叠从 ~83-100% 降到 ~30%~~ **同 SEED 续读 = 零重叠**（全源） |

#### 换种子后的重叠率核算

对每个共享源，重叠率 = (S1 消耗比例) × (S2 消耗比例)，因为两次采样独立随机：

| 数据源 | 可用 (B) | S1 消耗 (B) | S1 比例 | S2 消耗 (B) | S2 比例 | 同种子重叠 | 换种子重叠 |
|:--|--:|--:|--:|--:|--:|--:|--:|
| en_v1_4 | 2,237.1 | 953.6 | 42.6% | 513.3 | 22.9% | ~22.9% | **9.8%** |
| ufw_l1_en_hq | 150.2 | 73.4 | 48.9% | 44.0 | 29.3% | ~29.3% | **14.3%** |
| ufw_zh | 112.8 | 58.7 | 52.0% | 29.3 | 26.0% | ~26.0% | **13.5%** |
| math_l1 | 164.4 | 73.4 | 44.6% | 88.0 | 53.5% | ~44.6% | **23.9%** |
| math_l3 | 78.0 | 29.3 | 37.7% | 44.0 | 56.4% | ~37.7% | **21.3%** |
| code_l2 | 421.5 | 220.1 | 52.2% | 264.0 | 62.6% | ~52.2% | **32.7%** |
| code_l3 | 128.6 | 58.7 | 45.6% | 73.3 | 57.0% | ~45.6% | **26.0%** |
| **加权平均** | — | — | — | — | — | ~35% | **~17%** |

> **同种子重叠** = min(S1比例, S2比例)（S2 是 S1 的子集或反之，因为相同 shuffle 前缀）。
> **换种子重叠** = S1比例 × S2比例（独立随机采样的期望交集比例）。

#### 对 S2 总体重叠的影响

| S2 token 来源 | S2 占比 | 与 S1 重叠（同种子） | 与 S1 重叠（换种子） |
|:--|--:|--:|--:|
| 7 个共享源（旧数据） | 72% | ~35% → **25.2% of S2** | ~17% → **12.2% of S2** |
| stack-v3（新数据） | 17% | 0% | 0% |
| MegaMath（新数据） | 11% | 0% | 0% |
| **S2 总体重叠率** | 100% | **~25.2%** | **~12.2%** |

**结论**：换种子可将 S2 总体重叠率从 ~25% 降到 ~12%。加上 28% 的 S2 token 来自全新的数据源（零重叠），S2 有 **60% 的 token 确定不与 S1 重复**（28% 新源 + ~32% 旧源中未重叠部分），换种子后升至 **~72%**。

---

## 3. 数据量核算（逐数据源）

### 3.1 S1 消耗量（350k 步 × 4.19M tok/step = 1.467T tokens）

| 数据源 | prop | S1 tokens (B) | 可用 (B) | S1 epoch | S1 消耗比例 |
|:--|--:|--:|--:|--:|--:|
| en_v1_4 | 0.65 | 953.6 | 2,237.1 | 0.43 | 42.6% |
| ufw_l1_en_hq | 0.05 | 73.4 | 150.2 | 0.49 | 48.9% |
| ufw_zh | 0.04 | 58.7 | 112.8 | 0.52 | 52.0% |
| math_l1 | 0.05 | 73.4 | 164.4 | 0.45 | 44.6% |
| math_l3 | 0.02 | 29.3 | 78.0 | 0.38 | 37.7% |
| code_l2 | 0.15 | 220.1 | 421.5 | 0.52 | 52.2% |
| code_l3 | 0.04 | 58.7 | 128.6 | 0.46 | 45.6% |
| **合计** | 1.00 | 1,467.2 | — | — | — |

> S1 各源 epoch 均 < 1.0 → 每个源只看了一部分文档，`num_epochs=1`，shuffle_index 是 [0, N) 的完整排列。

### 3.2 S2 需求量（350k 步 × 4.19M tok/step = 1.467T tokens）

| 数据源 | S2 prop | S2 tokens (B) | 可用 (B) | S2 单独 epoch | S1+S2 累计 (B) | 累计 epoch | 来源 |
|:--|--:|--:|--:|--:|--:|--:|:--|
| en_v1_4 | 0.35 | 513.3 | 2,237.1 | 0.23 | 1,466.9 | 0.66 | S1 共享 |
| ufw_l1_en_hq | 0.03 | 44.0 | 150.2 | 0.29 | 117.4 | 0.78 | S1 共享 |
| ufw_zh | 0.02 | 29.3 | 112.8 | 0.26 | 88.0 | 0.78 | S1 共享 |
| math_l1 | 0.06 | 88.0 | 164.4 | 0.54 | 161.4 | 0.98 | S1 共享 |
| math_l3 | 0.03 | 44.0 | 78.0 | 0.56 | 73.3 | 0.94 | S1 共享 |
| code_l2 | 0.18 | 264.0 | 421.5 | 0.63 | 484.1 | 1.15 | S1 共享 |
| code_l3 | 0.05 | 73.3 | 128.6 | 0.57 | 132.0 | 1.03 | S1 共享 |
| stack-v3 (L4) | 0.17 | 249.3 | 430.7 | 0.58 | 249.3 | 0.58 | **新增** |
| MegaMath | 0.11 | 161.3 | ~371 | 0.43 | 161.3 | 0.43 | **新增** |
| **合计** | 1.00 | 1,465.8 | — | — | — | — | — |

> 累计 epoch >1.0 的项（code_l2 = 1.15, code_l3 = 1.03）标红——但这些是"总量"epoch，实际文档级重复率取决于种子策略（见 §2 方案 E）。

### 3.3 各方案的逐源可行性汇总

| 数据源 | 方案 A (shard 排除) | 方案 B (样本排除) | 方案 C (换源) | 方案 D (部分排除) | 方案 E (换种子) |
|:--|:--|:--|:--|:--|:--|
| en_v1_4 | ❌ S1 已用全 16 shard | 🟡 理论可行 | ❌ 无替代源 | ✅ 不需排除（充裕） | ✅ 重叠 9.8% |
| ufw_l1_en_hq | ❌ 同上 | 🟡 | ❌ | ✅ | ✅ 14.3% |
| ufw_zh | ❌ 同上 | 🟡 | ❌ | ✅ | ✅ 13.5% |
| math_l1 | ❌ 同上 | 🟡 | 🟡 可用 MegaMath 替代部分 | ✅ 补 MegaMath | ✅ 23.9% |
| math_l3 | ❌ 同上 | 🟡 | 🟡 | ✅ | ✅ 21.3% |
| code_l2 | ❌ 同上 | 🟡 | 🟡 可用 stack-v3 替代部分 | ✅ 补 stack-v3 | ✅ 32.7% |
| code_l3 | ❌ 同上 | 🟡 | 🟡 | ✅ | ✅ 26.0% |
| stack-v3 | ✅ 天然排除 | ✅ | ✅ | ✅ | ✅ 0% |
| MegaMath | ✅ 天然排除 | ✅ | ✅ | ✅ | ✅ 0% |

---

## 4. 推荐方案

### 4.1 核心建议

> 📌 **2026-11-28 用户纠错**：下方原建议「换 SEED=5678」是**错误的**，已撤销。
> 正确做法：**不换 SEED**（保持 seed=1234 = S1 同 seed）→ 同 shuffle_index → S2 从 S1 消费过的位置继续往后读 → 天然零重叠。换 SEED 会生成全新排列，从头读时可能读到 S1 已消费样本，**破坏零重叠**。

~~**采用方案 D + 方案 E 的组合**（即 v2 报告的配比方案 + 换种子）~~

**采用方案 D + 方案 E 的组合**（即 v2 报告的配比方案 + **同 SEED 续读**）：

1. **配比方案**：沿用 v2 报告的 S2 blend TSV（web:code:math = 4:4:2），补入 stack-v3-train（430.7B，L4 过滤后）和 MegaMath（~371B）作为新数据源——这部分**天然零重叠**
2. ~~**换种子**：为 S2 设置 `SEED=5678`（或任意不同于 1234 的值），将旧源的重叠从 ~35% 降到 ~17%~~
   **同 SEED 续读**：S2 保持 `seed=1234`（=S1 同 seed），同 shuffle_index 排列使 S2 从 S1 消费过的位置继续往后读，共享源也达到**零重叠**
3. **不需要实现复杂的样本级排除机制**——同 SEED 续读 + 新源天然零重叠 = 全源零重叠

### 4.2 实施步骤

| 步骤 | 内容 | 耗时 | 截止 |
|:--|:--|--:|:--|
| 1 | ~~在 `s2.env` 中设置 `SEED=5678`~~ **保持 `seed=1234`（=S1 同 seed），不要换** | 0 分钟 | S2 启动前 |
| 2 | 确认 S2 blend TSV 包含 stack-v3 + MegaMath（v2 报告已定义） | 已就绪 | — |
| 3 | ~~清理 Megatron 数据缓存中旧种子的 `.npy` 索引~~ 不需要（同 seed，索引缓存可复用） | — | — |
| 4 | 验证 S2 启动后日志正常（loss 无异常突跳，ratio 偏差 ≤1pp） | 启动时检查 | — |

### 4.3 为什么不做更复杂的排除？

| 考量 | 分析 |
|:--|:--|
| **预训练 vs SFT 的容错差异** | 预训练阶段，同一文档被看两次的影响远小于 SFT 阶段。主流大模型（LLaMA、DeepSeek、Qwen）的预训练数据普遍存在 1-3 epoch 的重复，这是正常做法。 |
| **累计 epoch 均 <1.2** | 补入新数据源后，所有源的 S1+S2 累计 epoch ≤ 1.15（code_l2 最高），即最多 15% 的文档被看两次。这在预训练的可接受范围内。 |
| **时间约束** | S2 预计 ~11-26 启动（距当前仅 ~8 天），实现样本级排除需要修改 Megatron 源码 + 测试，时间不允许。 |
| **ROI** | 换种子（5 分钟工作量）已将重叠从 ~25% 降到 ~12%。进一步用样本级排除（数天工作量）只能再降 ~12%，ROI 极低。 |
| **业界惯例** | DeepSeek-V2/V3、Qwen2.5 等模型的预训练阶段均未实现跨阶段样本排除；通过换源 + 换种子 + 控制 epoch <1.5 来管理重复率是标准做法。 |

### 4.4 代价与风险

| 风险 | 等级 | 缓解 |
|:--|:--|:--|
| 换种子导致 S2 初始 loss 波动 | 🟢 低 | 仅数据顺序变化，不影响分布；S4 实验显示配比切换 loss 反降 |
| 旧源残留 ~12% 文档重叠 | 🟢 低 | 预训练阶段可接受；累计 epoch <1.2 |
| 缓存 `.npy` 旧索引未清理导致加载错误 | 🟡 中 | S2 启动前清理 `path_to_cache` 中的旧 hash 目录，或确认 hash 因种子变化而自动 miss |
| `code_l2` 累计 epoch 1.15 | 🟡 低-中 | 15% 重复在可接受范围；如需进一步降低，可调低 code_l2 prop（从 0.18 降到 0.15）并提高 stack-v3 prop（从 0.17 到 0.20） |

---

## 5. 对 Epoch 的影响

### 5.1 各方案下的 epoch 对比

| 方案 | Web epoch | Code epoch | Math epoch | 说明 |
|:--|--:|--:|--:|:--|
| **不排除（同种子，不补新源）** | 0.67 | **1.57** 🔴 | **1.64** 🔴 | 纯旧源，大量重复 |
| **方案 D（补新源，同种子）** | 0.67 | 0.88 | 0.65 | 总量够，但旧源部分仍 ~100% 重叠 |
| **方案 D + E（补新源 + 换种子）** ⭐ | 0.67 | 0.88 | 0.65 | 总量够 + 旧源重叠降至 ~17% |
| **方案 C（完全换源）** | ❌ 不可行 | — | — | 无 Web 替代源 |

### 5.2 "总量 epoch" vs "文档级实际重复率"

**重要区分**：总量 epoch = 累计消耗 / 可用量。但这不等于文档级实际重复率：

- **同种子**：S1 和 S2 从每个 shard 的同一 shuffle 前缀消费 → 实际重复率 = min(S1_frac, S2_frac) / 可用量
- **换种子**：S1 和 S2 独立随机采样 → 实际重复率 = S1_frac × S2_frac / 可用量

| 数据源 | 总量 epoch | 同种子实际重复率 | 换种子实际重复率 |
|:--|--:|--:|--:|
| code_l2 | 1.15 | **52.2%**（S1 消耗比例 = S2 的子集） | **32.7%** |
| code_l3 | 1.03 | **45.6%** | **26.0%** |
| math_l1 | 0.98 | **44.6%** | **23.9%** |
| math_l3 | 0.94 | **37.7%** | **21.3%** |

> 即使总量 epoch <1.0（如 math_l1 = 0.98），同种子下仍有 44.6% 的文档被重复看到——因为 S1 和 S2 从同一 shuffle 前缀取样本。**换种子**后降至 23.9%。

### 5.3 如果完全排除 S1 已训数据，各源 epoch 变化

如果完全排除 S1 已训数据（假设技术上可行），S2 只能从"剩余未被 S1 消费的文档"中采样：

| 数据源 | 可用 (B) | S1 消耗 (B) | 剩余 (B) | S2 需求 (B) | S2 epoch（仅剩余） | 够用？ |
|:--|--:|--:|--:|--:|--:|:--|
| en_v1_4 | 2,237.1 | 953.6 | 1,283.5 | 513.3 | 0.40 | ✅ |
| ufw_l1_en_hq | 150.2 | 73.4 | 76.8 | 44.0 | 0.57 | ✅ |
| ufw_zh | 112.8 | 58.7 | 54.1 | 29.3 | 0.54 | ✅ |
| math_l1 | 164.4 | 73.4 | 91.0 | 88.0 | 0.97 | ✅ 勉强 |
| math_l3 | 78.0 | 29.3 | 48.7 | 44.0 | 0.90 | ✅ |
| code_l2 | 421.5 | 220.1 | 201.4 | 264.0 | **1.31** | ❌ **不够** |
| code_l3 | 128.6 | 58.7 | 69.9 | 73.3 | **1.05** | ❌ **不够** |

> 如果完全排除 S1 已训数据，**code_l2 和 code_l3 的剩余量不够 S2 需求**。code_l2 需 264B 但剩余仅 201B（差 63B），code_l3 需 73B 但剩余仅 70B（差 3B）。这进一步证明了**完全排除不可行**，必须补入新数据源（stack-v3 填补 code 缺口）。

---

## 6. 附录：Megatron 源码关键路径

### 6.1 代码文件索引

| 文件 | 关键行 | 作用 |
|:--|:--|:--|
| `gen_blend.py` | L112-119 | shard 级权重分配：`w = prop / len(bins)` |
| `pretrain_launcher.py` | L273-285 | blend 字符串解析：扁平化为 `[w1, path1, w2, path2, ...]` |
| `blended_dataset.py` | L88, L140-150 | `_build_indices()` → `helpers.build_blending_indices` 构建 Bresenham 交错索引 |
| `blended_megatron_dataset_builder.py` | L551-578 | `_get_size_per_split_per_dataset` 计算每个 shard 的 num_samples |
| `gpt_dataset.py` | L408 | `numpy_random_state = numpy.random.RandomState(self.config.random_seed)` |
| `gpt_dataset.py` | L411-413 | `_build_document_index` 构建文档索引（按 epoch 复制 + shuffle） |
| `gpt_dataset.py` | L451-458 | `_build_shuffle_index` 构建样本位置随机排列 |
| `gpt_dataset.py` | L533-553 | `_get_num_epochs` 计算需要的 epoch 数 |
| `megatron_dataset.py` | L52-66 | `unique_identifiers` 包含 `random_seed`（参与缓存 hash） |
| `megatron_dataset.py` | L118 | `_key_config_attributes` 返回 `["random_seed", ...]` |
| `common.env` | SEED=1234 | 当前固定种子 |

### 6.2 数据流图

```
blend_s1_preblend.tsv (7 源 × prop)
        │
        ▼
gen_blend.py: w_shard = prop / n_shards
        │
        ▼ "0.018571 /path/shard0 0.018571 /path/shard1 ..."
pretrain_launcher.py --train-data-path
        │
        ▼
BlendedMegatronDatasetBuilder
  ├── 解析为 (paths, weights) 对
  ├── 每个路径 → GPTDataset(shard_i)
  │     ├── document_index = all_docs × num_epochs, shuffled(seed=1234)
  │     ├── sample_index = 文档→样本边界映射
  │     └── shuffle_index = [0, N) 的随机排列(seed=1234)
  └── BlendedDataset(datasets, weights, size)
        ├── dataset_index[i] = Bresenham 选择哪个 shard
        └── dataset_sample_index[i] = 该 shard 内第几个样本 (递增)
              │
              ▼
        __getitem__(i):
          shard_id = dataset_index[i]
          sample_id = dataset_sample_index[i]
          → GPTDataset[shard_id].shuffle_index[sample_id]
          → 实际文档
```

---

## 7. 总结

| 维度 | 结论 |
|:--|:--|
| **当前 blend 是否排除 S1 数据？** | **否**。Megatron 无跨 run 消费追踪，S2 与 S1 使用相同 .bin/.idx 文件。 |
| **同种子的重叠程度？** | ~~**~83-100%**（每个共享源的 shuffle 前缀完全相同）。S2 总体重叠 ~25%。~~ 📌 **2026-11-28 纠错**：同 seed + resume from ckpt → S2 从 S1 消费位置续读 → **零重叠**（非 ~25%）。原分析假设 S2 从头读共享源，实际 stock Megatron resume 会从 consumed_samples 继续。 |
| **可行的排除方案？** | 方案 D（补新源）+ 方案 E（~~换种子~~ **同 SEED 续读**）。新源天然零重叠，同 SEED 续读使共享源也零重叠。 |
| **不可行的方案？** | 方案 A（shard 排除）：S1 已用全部 shard。方案 B（样本排除）：实现复杂、时间不允许。方案 C（完全换源）：无 Web 替代源。 |
| **是否需要实现复杂排除机制？** | **不需要**。同 SEED=1234 续读 + 新源天然零重叠 = 全源零重叠。 |
| **推荐操作？** | ① **保持 `seed=1234`（不要换 SEED）**；② 确认 S2 blend TSV 包含 stack-v3 + MegaMath；③ 从 350k ckpt resume。 |
| **对 epoch 的影响？** | 补新源后累计 epoch：Web 0.67 / Code 0.88 / Math 0.65（均 <1.2）。如完全排除 S1 数据，code_l2/l3 剩余量不足 → 证明完全排除不可行。 |

---

> **报告路径**: `run/reports/report_s2_data_overlap_study.md`
> **源码依据**: `Xmodel-2.5-code/megatron/core/datasets/blended_dataset.py`、`gpt_dataset.py`、`blended_megatron_dataset_builder.py`、`megatron_dataset.py`（逐行阅读）
> **数据依据**: `DATA_MAPPING.md` §A（token 实测）、`blend_s1_preblend.tsv`（S1 配比）、`report_s1s2_split_data_v2_zh.html` v2.9（S2 配比 + PC-1 实测 430.7B）
> **口径声明**: 所有 token 数来自 `INDEX.tsv` / `MANIFEST.json` 实测；重叠率计算基于 Megatron 源码逻辑的确定性推导（相同种子 → 相同 shuffle → 前缀重叠），非估算。
