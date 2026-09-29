# BaiZe 1B 架构与超参搜索记录

## ✅ 最终收敛状态（2026-09-29 converged，架构类型维度扫描完成）

任务收官：**胜出配置 = MiniCPM5-1B（24层 / GQA KV2 / 嵌入 off(untied) / AdamW / Stable LR 3e-4 / WSD 10% / Batch 1024 / SeqLen 4096 / micro_batch 1 / μP）**，验证 loss **4.9690@160**（优于基线 LR 6e-4 的 5.0861，**−0.117**）。可复现训练命令：`cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027 && bash train_s4_01.sh`（详见下方「胜出配置」）。

架构类型维度（MiniCPM5-1B / Nemotron / Hymba）扫描完成：megatron-core 虽原生含 Mamba/SSM-hybrid（`mamba_hybrid_layer_allocation`）与 Nemotron 支持，但均无 1B 变体（最小 hybrid 8B、最小 Nemotron/NemotronH 4B、最接近纯 Mamba2 1.3B 无 attention），swift 层亦未暴露可训练 1B 配置 → **无可运行的 1B 替代架构，MiniCPM5-1B 保持唯一胜出**。本轮（架构兼容性验证轮）BUDGET_USED=0/20 GPU·h，无新实验。

## S2.5 架构扩展结论（2026-09-28 22:03 experiment_plan 收官）

**目标**：验证非 Llama 架构（Nemotron / Hymba）在 Megatron-SWIFT v4.5.3 上的兼容性，作为 1B 架构备选。**结论：两者均不可用，MiniCPM5-1B（LlamaForCausalLM 标准 GQA）保持唯一架构胜出**，S1~S4 胜出配置不变。

| 架构 | 框架注册情况 | 判定 | 依据 |
|:---|:---|:---|:---|
| MiniCPM5-1B | ✅ swift `llama` + mcore_bridge `gpt` | ✅ 可用（胜出） | S1~S4 已完整验证 |
| NemotronH | ⚠️ swift `nemotron_h`(nvidia.py) + mcore_bridge `gpts/nemotron_h.py` 均已注册 | ❌ NOT_SUPPORTED | 仅注册 30B-A3B MoE（`NVIDIA-Nemotron-3.5-Lightning-30B-A3B`），无 1B 稠密变体；`requires=['transformers>=5.0', ...]`，实际 4.56.1 不满足；`model_arch=None` |
| Nemotron(70B) | ⚠️ swift llama.py 注册 `Llama-3.1-Nemotron-70B-Instruct-HF` | ❌ NOT_SUPPORTED(1B) | 仅 70B，且是 Llama 架构微调（非新架构） |
| Hymba | ❌ swift / mcore_bridge 全库 0 处注册 | ❌ NOT_SUPPORTED | 无 model type / template / loader 任何引用 |

> MLA（multi-latent attention）维度：megatron core 有 `MLASelfAttention`，但 swift 未对 Llama/MiniCPM5 暴露 `--attention_backend mla`（仅 flash/fused/unfused/local/auto），需自建 MLA 模型变体，实现风险高（与上一轮「暂不测 MLA」一致），不纳入本轮。

**结论**：架构类型维度（MiniCPM5-1B / Nemotron / Hymba）扫描完成，仅 MiniCPM5-1B 框架可用。无新实验、无预算消耗（本轮 BUDGET_USED 保持 0/20 GPU·h）。胜出配置及可复现命令保持不变（见下方「胜出配置」）。

## S2.5 架构判定修正（2026-09-29 data_preprocess 收官，先查 megatron-core）

> ⚠️ **更正 2026-09-28 的「NOT_SUPPORTED」结论**：上一轮判定顺序有误（只查 swift 注册表就下结论）。本轮按正确顺序（先 megatron-core 模型库 → 再 swift 注册表）重查，修正结论：megatron-core **原生支持** Mamba/SSM-hybrid 与 Nemotron，但**均无 1B 变体**，故仍无可运行的 1B 替代架构，MiniCPM5-1B 保持唯一胜出。

### megatron-core 原生模型库（mcore 层）
- `bridge/models/mamba/mamba_provider.py`：`MambaModelProvider` 支持 `hybrid_attention_ratio` / `hybrid_mlp_ratio` / `hybrid_override_pattern`（即 Hymba 式 attention+SSM hybrid 能力）。现有 provider 规模：130M / 370M / 780M / **1.3B（`MambaModelProvider1P3B`，48 层 hidden 2048，override `"M"*48` = 纯 Mamba2、无 attention）** / 2.7B / 8B / **hybrid_8B**。→ **无 ~1B 的 attention+SSM hybrid，唯一 hybrid 是 8B**。
- `bridge/models/nemotron/nemotron_provider.py`：`Nemotron3ModelProvider4B`(32 层/hidden 3072) / 8B / 22B，`Nemotron4` 15B/340B。最小 **4B**。
- `bridge/models/nemotronh/nemotron_h_provider.py`：`NemotronHModelProvider`（继承 MambaModelProvider = mamba+attention hybrid）4B / 8B / 47B / 56B / nano 9B/12B。最小 **4B**。
- `core/ssm/mamba_hybrid_layer_allocation.py`：`allocate_layers`（`Symbols`: M=SSM / *=attention / -=MLP / E=MoE）= hybrid 层分配实现。

### swift 层（bridge 注册）
- `swift/model/models/mamba.py`：仅注册 classic Mamba1 HF（`state-spaces/mamba-*` 130m~2.8b），`architectures=['MambaForCausalLM']`、`model_arch=None`（无 mcore bridge 转换路径，非 mcore Mamba2/hybrid）。
- `swift/model/models/nvidia.py`：仅注册 `NemotronHForCausalLM` **30B-A3B MoE**，`requires=['transformers>=5.0','mamba-ssm','causal-conv1d>=1.2.0']`、`model_arch=None`。
- `grep -rni hymba swift/` = **空**（swift 0 处注册 Hymba，与上轮一致；但「0 处注册」≠「mcore 不支持」）。

### 修正后判定
| 架构 | mcore 层 | swift 层 | 修正判定 |
|:---|:---|:---|:---|
| Hymba (~1B) | ✅ 有 hybrid 能力（`hybrid_attention_ratio`），但最小 hybrid recipe = `mamba2_hybrid_8b`(8B)，无 1B hybrid | ❌ 0 处注册 | ⚠️ **NOT_EXPOSED / 无 1B 变体**（非「不存在」；需手动搭 1B hybrid 层规格 + 桥接，风险高） |
| Nemotron/NemotronH (~1B) | ✅ `nemotron` 最小 Nemotron3-4B、`nemotronh` 最小 4B | ⚠️ 仅 30B-A3B MoE / `transformers>=5.0` | ⚠️ **NOT_EXPOSED / 无 1B 变体**（最小 4B，无 1B 稠密） |

> **修正结论**：架构类型维度确认完成——megatron-core 虽原生支持 Mamba/SSM-hybrid、Nemotron，但均无 1B 规模 recipe/provider（最小 hybrid 8B、最小 Nemotron/NemotronH 4B，最接近 1B 的纯 Mamba2 为 1.3B 且无 attention）。swift 层未暴露任何 mcore hybrid/nemotron 为可训练 1B 配置。**无可运行的 1B 替代架构，MiniCPM5-1B 保持唯一胜出**，无新实验、无预算消耗（BUDGET_USED 0/20 GPU·h）。

## 胜出配置（✅ S4 收敛验证完成，2026-09-25 18:36）

**架构**（MiniCPM5-1B / LlamaForCausalLM 标准架构，~1.038B 参数，μP 最大更新参数化）
- 层数 **24** / hidden 1536 / 中间层 8960 / 头数 16 / **GQA KV 头 2** / 头维 96 / 嵌入 **off(untied)**
- 注意力：标准 GQA（`--attention_backend fused`，TE 融合注意力，无 flash 依赖）

**超参**
- 优化器 **AdamW**（`--optimizer adam`），权重衰减 **0.1**
- 调度 **WSD**：Stable LR **3e-4**（`--lr 3e-4`）、`--min_lr 3e-5`、`--lr_warmup_iters 10`、`--lr_wsd_decay_iters 16`（=10%）、`--lr_wsd_decay_style exponential`
- 全局 Batch Size **1024**（micro_batch 1 × accum 1024）、SeqLen **4096**（~4M tokens/step）

**最终结果**
- S4-01 从零训 160 step：final loss **4.9690**（对照基线 Stable LR 6e-4 同 step = 5.0861 → **−0.117**）；吞吐 ~37.8s/it ≈ **~111K tok/s**；显存 17.51 GiB/卡
- 检查点：`output/S4-01/v0-20260925-165341/checkpoint-160`

**可复现训练命令**
```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
bash train_s4_01.sh
# 核心 = megatron pt --model models/MiniCPM5-1B --model_type llama --template minicpm5 \
#   --dataset .../Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa --streaming true --packing true --packing_length 4096 \
#   --micro_batch_size 1 --global_batch_size 1024 --train_iters 160 --finetune true \
#   --optimizer adam --lr 3e-4 --min_lr 3e-5 --lr_warmup_iters 10 --lr_decay_style WSD --lr_wsd_decay_iters 16 \
#   --lr_wsd_decay_style exponential --weight_decay 0.1 --attention_backend fused --output_dir output/S4-01
```

## 累计预算消耗
~82.4 GPU·小时（预算 84 GPU·小时；S1-01 26.6 + S2-01 7.0 + S2-02 7.35 + S2-03 6.9 + S2-04 6.9 + S3-01 7.0 + S3-02 7.0 + S4-01 13.7，剩余 ~1.6 GPU·小时；全部 4 阶段已完成）

## S2 单变量扫描结论（2026-09-25 09:05 收官）
4 个高优维度（LR / 层数 / KV头 / 嵌入共享）单变量全部完成，**基线 S1-01（24层 / GQA KV2 / 嵌入 off(untied) / AdamW / LR 6e-4 / Batch 1024 / SeqLen 4096）在 loss@80 上全部胜出**：

| 维度 | 胜出值 | 依据（loss@80 vs 基线 5.962） |
|:---|:---|:---|
| Stable LR | **3e-4** | 3e-4(5.908, S3-01) < 6e-4(5.962) < 1e-3(6.019) → LR 下界 3e-4 最优 |
| 层数 | **24** | 24(5.962) < 28(6.119) |
| KV头 | **2** | KV2(5.962) ≲ KV4(5.979)，KV4 增参 ~14M 无收益 |
| 嵌入共享 | **off(untied)** | untied(5.962) < tied(6.030)，tied 省 ~200M 但无 loss 收益 |

→ 架构/主超参不宜偏离基线。剩余 ~29.3 GPU·h 进入 **S3 组合优化**（低优维度补测：WSD 衰减比例 / Batch / 优化器Muon / MLA，或小组合微调）+ S4 收敛验证。

## S2 单变量扫描计划（2026-09-24 23:17 规划）
基线 S1-01（24层 / GQA KV=2 / 嵌入 off / AdamW / LR 6e-4 / batch 1024 / seq 4096）loss 3.587@300。
预算紧张（剩余 ~57.4 GPU·h），S2 先跑 **4 组高优先级单变量**，每组 **80 steps**（~7~8 GPU·h），候选维度按优先级：
1. S2-01 Stable LR 6e-4→**1e-3**（纯超参，无模型改动，最便宜，LR 效应短程即可见）
2. S2-02 层数 24→**28**（hidden 1536 不变 → ~1.2B，测深度）
3. S2-03 KV头 2→**4**（测 GQA 比例）
4. S2-04 嵌入共享 off→**on(tied)**（~0.84B，测 200M 嵌入参数是否值得）

> 执行时优先尝试 `--micro_batch_size 2`（grad_accum 128→64）提速；OOM 则 fallback 到 1。
> 低优先级维度（LR 3e-4、层数 32、KV头 8、MLA、Muon、WSD 衰减比例、batch/seqLen）视预算余量在 S3 前后补测。

**👉 本轮选定（2026-09-25 07:23 规划 → 2026-09-25 08:13 已启动）：S2-04 嵌入共享 on(tied)**（其余同基线：24层 / GQA KV2 / 嵌入 tied / 头维96 / AdamW / LR 6e-4 / Batch 1024 / SeqLen 4096 / micro_batch=1 / 80 steps）。模型 `models/MiniCPM5-1B-TIED/`（`gen_model_variant.py --tie_word_embeddings true`，~0.84B，省 ~200M 独立输出嵌入），脚本 `train_s2_04.sh`（复制 train_s2_03.sh，必带 `--model_type llama --template minicpm5`），预期 ~7.0 GPU·h。预算 47.8/84 GPU·h，剩余 ~36.2。S2-04 完成后 S2 单变量扫描（LR/层数/KV头/嵌入共享 4 个高优先维度）收官，转 S3 组合优化。

## S3 组合优化计划（2026-09-25 10:02 规划）
S2 单变量扫描 4 维度（LR/层数/KV头/嵌入共享）全部基线胜出（24层/KV2/untied/LR6e-4）。S3 补测剩余低优维度 + 小组合，每组 80 steps ≈ ~7 GPU·h，用剩余 ~29.3 GPU·h，之后 S4 收敛验证。

| ID | 维度 | 变更点 | 目的 | 预期 GPU·h |
|:---|:---|:---|:---|:---|
| S3-01 | Stable LR 下界 | ✅ LR 6e-4→**3e-4**（min_lr 6e-5→3e-5），其余同基线 | **胜出**：loss 5.908@80 < 基线 5.962@80 → Stable LR **3e-4** | ~7 done |
| S3-02 | WSD 衰减比例 | ✅ 衰减 10%→**20%**（lr_wsd_decay_iters 8→16），**带胜出 LR 3e-4**（min_lr 3e-5），其余同基线 | **无优势**：loss 5.917@80 vs S3-01(WSD10%) 5.908@80 → 持平(略差+0.009)，**保留 WSD10%** | ~7 done |
| S3-03 | ~~优化器/Muon/Batch512~~ | 已取消（省预算给 S4） | ~~组合微调或低优维度补测~~ | 0 |

> S3 总预算收敛为 ~14 GPU·h（S3-01 ~7 + S3-02 ~7）。S3-03（Muon dist_muon / Batch512）因预算紧张且低信号/有实现风险取消，剩余 ~15 GPU·h 全部留给 S4 收敛验证（胜出配置 ~170~200 step）。MLA/层数32/KV8/seqLen 因 S2 已显示基线胜出或有实现风险，暂不测。

## S3 组合优化结论（2026-09-25 14:48 收官）

| ID | 维度 | 结果（loss@80） | 结论 |
|:---|:---|:---|:---|
| S3-01 | Stable LR 下界 3e-4 | **5.908**（WSD10%） | **胜出**：3e-4(5.908) < 6e-4(5.962) < 1e-3(6.019) → **Stable LR 3e-4** |
| S3-02 | WSD 衰减比例 20% | **5.917** | 无优势：vs WSD10% 5.908 持平(略差+0.009，噪声内) → **保留 WSD 10%** |
| S3-03 | Muon/Batch512 | — | 已取消（省预算给 S4） |

→ **S3 胜出配置（进入 S4）**：24层 / GQA KV2 / 嵌入 off(untied) / AdamW / Stable LR **3e-4** / WSD **10%** / Batch 1024 / SeqLen 4096 / micro_batch 1 / μP。基线唯一改动 = **Stable LR 6e-4 → 3e-4**。

## S4 收敛验证计划（2026-09-25 15:52 规划）

确认 S3 胜出配置，跑较长步数验证收敛，产出最终可复现训练命令。剩余预算 ~15.3 GPU·h（~175 step @ ~37.6s/it × 8 卡）。

| ID | 维度 | 配置 | 目的 | 预期 GPU·h |
|:---|:---|:---|:---|:---|
| S4-01 | 胜出配置长步收敛 | 24层 / GQA KV2 / 嵌入 off(untied) / AdamW / Stable LR **3e-4** / WSD **10%**(lr_wsd_decay_iters 16) / Batch 1024 / SeqLen 4096 / micro_batch 1 / μP，train_iters **160** | 胜出配置（基线唯一改动 = LR 6e-4→3e-4）从零训练 160 step，验证收敛趋势，对照 S1-01(LR 6e-4) 同 step | ~13.4 |

> S4-01 纯超参改动、无模型变更：直接复用基线模型 `models/MiniCPM5-1B`（untied），脚本在 `train_s3_01.sh` 基础上改 `--train_iters 160` / `--lr_wsd_decay_iters 16` / `--output_dir output/S4-01`（lr 3e-4 / min_lr 3e-5 不变）。
> 完成后提取 @160 loss 与 S1-01（LR 6e-4，300 step 内同 step）对照 → converged，输出胜出配置 + 可复现训练命令。

## S4 收敛验证结论（2026-09-25 18:36 收官）

| ID | 维度 | 结果 | 结论 |
|:---|:---|:---|:---|
| S4-01 | 胜出配置长步验证（LR 3e-4） | **4.9690**@160 | **胜出验证通过**：4.9690 < 基线(LR 6e-4) 5.0861@160 → **−0.117**（较 80 步 −0.054 扩大）|

- **复现性**：S4-01 @80 loss 5.8995 ≈ S3-01 final 5.908@80（从零重跑，随机波动内）。
- 胜出配置 = 基线唯一改动 **Stable LR 6e-4 → 3e-4**；架构/主超参（24层/KV2/untied/AdamW/WSD10%/Batch1024/SeqLen4096）全部基线胜出。
- 检查点：`output/S4-01/v0-20260925-165341/checkpoint-160`。

## 实验记录

| ID | 阶段 | 层数 | KV头 | 注意力 | 嵌入共享 | 优化器 | LR | Batch | SeqLen | 状态 | 最终Loss | 吞吐(tok/s) | 耗时(h) | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|:---|
| S1-01 | S1 | 24 | 2 | GQA | **off(untied)** | AdamW | 6e-4 | 1024 | 4096 | **done** | **3.587** | **~105K** (39.9s/it) | **3.33** | ✅ 基线完成：loss 12.08→3.587 正常下降，lr 6e-4→6e-5 WSD 衰减收尾，grad_norm→0.072；ckpt `output/S1-01/v5-20260924-190325/checkpoint-300` |
| S2-01 | S2 | 24 | 2 | GQA | off(untied) | AdamW | **1e-3** | 1024 | 4096 | **done** | **6.019** | **~110K** (38.0s/it) | **0.88** | ❌ 无优势：loss 6.019@80 vs 基线(LR 6e-4) 5.962@80 → LR 1e-3 略差，**保留 LR 6e-4**；ckpt `output/S2-01/v1-20260924-235239/checkpoint-80` |
| S2-02 | S2 | **28** | 2 | GQA | off(untied) | AdamW | 6e-4 | 1024 | 4096 | **done** | **6.119** | **~105K** (39.8s/it) | **0.92** | ❌ 无优势：loss 6.119@80 vs 基线(24层) 5.962@80 → 28层短程收敛更慢，**保留 24层**；ckpt `output/S2-02/v0-20260925-020928/checkpoint-80` |
| S2-03 | S2 | 24 | **4** | GQA | off(untied) | AdamW | 6e-4 | 1024 | 4096 | **done** | **5.979** | **~111K** (37.6s/it) | **0.87** | ⚠️ 无优势：loss 5.979@80 vs 基线(KV2) 5.962@80 → 基本持平(+0.017)，KV4 增参~14M(1.052B)无收益，**保留 KV2**；ckpt `output/S2-03/v0-20260925-045918/checkpoint-80` |
| S2-04 | S2 | 24 | 2 | GQA | **on(tied)** | AdamW | 6e-4 | 1024 | 4096 | **done** | **6.030** | **~112K** (37.3s/it) | **0.86** | ❌ 无优势：loss 6.030@80 vs 基线(untied) 5.962@80 → tied 略差(+0.068)，省 ~200M 嵌入参数但无 loss 收益，**保留 off(untied)**；ckpt `output/S2-04/v0-20260925-081356/checkpoint-80` |
| S3-01 | S3 | 24 | 2 | GQA | off(untied) | AdamW | **3e-4** | 1024 | 4096 | **done** | **5.908** | **~111K** (37.6s/it) | **0.87** | ✅ **胜出**：loss 5.908@80 vs 基线(6e-4) 5.962@80 vs 1e-3 6.019@80 → **Stable LR 3e-4 最优**；ckpt `output/S3-01/v0-20260925-105659/checkpoint-80` |
| S3-02 | S3 | 24 | 2 | GQA | off(untied) | AdamW | **3e-4** | 1024 | 4096 | **done** | **5.917** | **~108K** (37.95s/it) | **0.87** | ⚠️ 无优势：loss 5.917@80 vs S3-01(WSD10%) 5.908@80 → WSD 20% 持平(略差+0.009)，**保留 WSD 10%**；ckpt `output/S3-02/v0-20260925-134941/checkpoint-80` |
| S3-03 | S3 | - | - | - | - | - | - | - | - | ~~cancelled~~ | - | - | - | 取消：省预算给 S4 |
| S4-01 | S4 | 24 | 2 | GQA | off(untied) | AdamW | **3e-4** | 1024 | 4096 | **done** | **4.969** | **~111K** (37.8s/it) | **1.71** | ✅ **胜出配置验证通过**：LR 3e-4 从零训 160 step final loss 4.9690 vs 基线(LR 6e-4) 同 step 5.0861 → **−0.117**；✅ 复现 S3-01(80步 5.908) 良好；ckpt `output/S4-01/v0-20260925-165341/checkpoint-160` |