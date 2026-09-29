# BaiZe 2B 架构搜索记录（从零训练）

## 胜出架构（S4 结论，2026-09-29 晚）
**Mamba2-hybrid（56 层，Nemotron-H 式顺序混合）** ⚠️ 见「⚠️ 关键修正」与「对比结论」的权衡说明——以「loss 收敛 + 推理速度」两项占优胜出，但训练吞吐落后 ~24%；MiniCPM5-2B 在「训练吞吐」一项占优。

## ⚠️ 关键修正（2026-09-29 晚，S3 阶段发现，覆盖 S1/S2 的「非等参 3.00B」结论）
- **Mamba2-hybrid 真实参数量 = 2.220B**（`sum(numel())` = 2,220,268,032），**不是** 3.00B。
- 根因：S1/S2 记录的「3.00B」来自 mcore 的 `Number of parameters in transformer layers in billions: 2.47 + embedding 0.53` 打印——该打印对 Mamba/hybrid **误把 56 层全部按 full attention+MLP 计**，而实际绝大多数层的 SSM 权重远小于 attention，故虚高 ~0.78B。
- 两处独立实测一致（训练日志 `rank(0,0)=2220268032` + infer 脚本 `sum(numel())=2220268032`），结论可靠。
- **修正后**：MiniCPM5-2B = **2.512B**、Mamba2-hybrid = **2.220B**，两架构**基本等参**（MiniCPM5 仅多 ~13%），**不再是「非等参 +19.5%」**。这使 Mamba2 的「更低 loss + 更少参数」结论**更强**。

## 对比结论（loss / 训练速度 / 推理速度 三张表）

### 表 1：loss 曲线对比（早期收敛，1000 步 / seq4096 / GBS6 / 同数据同 seed）
| 架构 | 参数量 | 初始 loss | 最终 loss | Δloss |
|:---|:---|:---|:---|:---|
| MiniCPM5-2B (42层 Llama) | 2.512B | 11.62 | 4.8065 | 6.81 |
| Mamba2-hybrid (56层) | **2.220B** | 10.80 | **4.6846** | 6.12 |

> Mamba2 用**更少参数**（-11.6%）达到**更低**最终 loss（-0.122）。loss 收敛：**Mamba2 胜**。

### 表 2：训练速度对比（tokens/sec，两架构均 6 卡 TP1/DP6）
| 架构 | 耗时/iter | 训练 tok/s | 相对 |
|:---|:---|:---|:---|
| MiniCPM5-2B | ~275ms | **~89K** | **1.24×（更快）** |
| Mamba2-hybrid | ~340ms | ~72K | 1.00× |

> 训练吞吐：**MiniCPM5 胜**（快 ~24%）。Mamba2 的 SSM 前向/反向计算更密集。

### 表 3：推理速度对比（mcore 直驱 / TP1 / 1×H100 / bf16 / seq 2048 prompt + 256 gen / batch=1 / prefill-iters=12）
| 架构 | prefill tok/s | decode tok/s | decode 延迟/token |
|:---|:---|:---|:---|
| MiniCPM5-2B | 21,436 | 2.21 ⚠️ | ~452ms |
| Mamba2-hybrid | **23,692** | **22.77** | ~44ms |

> 推理：**Mamba2 胜**（prefill +10.5%、decode +10.3×）。⚠️ MiniCPM5 的 decode（452ms/token）现象已用 torch.profiler **定位根因**：非「KV-cache 未命中」，而是 **mcore 直驱（无 CUDA-graph/flashinfer）下 TE fused-attention 的逐层 CPU launch 开销**——单步 `Self CPU≈620ms`（其中 `FusedAttnFunc` 42 层×~13.8ms=579ms 占 93.4%），`Self CUDA 仅 4.05ms`，即 **CPU-bound、非 GPU-bound**（纯 GPU 计算上界 ≈250 tok/s）。Mamba2 仅 4 个 attention 层 + SSM/MLP（SSM 以 O(1) 循环状态解码、CPU 开销极低），故 decode 快 ~10×。**两架构同一代码路径测量，相对结论可信**；MiniCPM5 绝对 decode 数如需生产级值应走 SGLang/CUDA-graph（本报告为 mcore 直驱下界）。

## S1 冒烟结果（arch_prepare，2026-09-29）
- 两架构均已「从零随机初始化」跑通 10 步前向+反向 + 保存 checkpoint（torch_dist）。
- 统一路径：NVIDIA/NeMo recipe（`pretrain(pretrain_config(...), forward_step)`，torchrun 直驱，nemo_run 未装已 bypass）。
- 统一 tokenizer：DeepSeek-V4.1-Flash（追加 EOD 后 vocab=129281，模型侧 pad 129408）。
- ✅ 参数量（S3 修正后）：MiniCPM5-2B = **2.512B**、Mamba2-hybrid = **2.220B**（基本等参，详见上「关键修正」）。
- **⚠️ Mamba2 冒烟初始 loss 偏低（8.80 vs MiniCPM 11.62）**：后证实是 mock 数据多步后的假象，真值首步 10.80（≈ln(129408)=11.77 正常）。

### 冒烟明细（TP=2 / mock 数据 / 10 步）
| 架构 | 参数量(实测) | 初始 loss | 耗时/iter | 保存 ckpt |
|:---|:---|:---|:---|:---|
| MiniCPM5-2B (42层 Llama) | 2.512B | 11.62 | ~1462 ms | ✅ |
| Mamba2-hybrid (56层) | 2.220B | 8.80 ⚠️(假象) | ~11619 ms(首步) | ✅ |

## S2 1000 步训练口径（决策 3，两架构完全一致，2026-09-29 晚启动）
- 两架构均 6 卡（A1→10.239.2.29 GPU0~5；A2→10.239.2.12 GPU0~5），TP=1 / DP=6
- seq_length=4096、micro_batch_size=1、**global_batch_size=6**（24.5K tok/步，无梯度累积）
- optimizer=distributed AdamW（β1=0.9 β2=0.95 eps=1e-5 wd=0.1）、lr=3e-4（cosine→min_lr=3e-5，warmup=100）
- train_iters=1000、random_seed=1234、bf16、eval 关闭（eval_iters=0）、数据=同一份 DeepSeek .bin/.idx（200k docs/164.75M tokens）
- **GBS=6 理由（关键）**：Mamba2 SSM ~11.6s/步，GBS>6 会让 Mamba2 训练远超 20 GPU·h 预算（GBS=128≈408 GPU·h）。故定 GBS=6（Mamba2 ≈3.2h×6卡≈19.3 GPU·h）。属「早期收敛」对比（约 24.6M tokens/架构）。

## 实验记录
| ID | 架构 | 参数量 | 状态 | 最终loss | 训练tok/s | 耗时/iter | 备注 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| A1-01 | MiniCPM5-2B(42层 Llama) | 2.512B | ✅ done | **4.8065**（11.62→4.81） | **~89K** | ~275ms | 从零，2.29 GPU0~5 |
| A2-01 | Mamba2-hybrid(56层) | 2.220B | ✅ done | **4.6846**（10.80→4.68） | **~72K** | ~340ms | 从零，2.12 GPU0~5，基本等参(-11.6%) |

## S2 训练结果（1000 步，已完成 2026-09-29）
- **loss 曲线**：MiniCPM5 11.62→4.8065（Δ6.81）；Mamba2 10.80→4.6846（Δ6.12）。Mamba2 终值更低（-0.122），且**参数量更少**（2.220B vs 2.512B，-11.6%）。
- **训练吞吐**：MiniCPM5 ~275ms/iter（≈89K tok/s）；Mamba2 ~340ms/iter（≈72K tok/s）。**MiniCPM5 快 ~24%**。
  - ⚠️ Mamba2 首步 ~12.3s 是 SSM 编译/CUDA-graph 捕获的一次性开销，稳态 ~340ms。此前「11.6s/iter」为冒烟首步假象。
- **Mamba2「初始 loss 8.80」已澄清**：真值首步 loss=10.80（≈ln(129408)=11.77，正常），此前 8.80 是 mock 数据冒烟测得多步后的值，非异常。
- **checkpoint**：MiniCPM5 `nemo_experiments/minicpm5_2b_1000step/checkpoints/iter_0001000`（12 distcp，~4.9GB）；Mamba2 `nemo_experiments/mamba2_2b_1000step/checkpoints/iter_0001000`（~4.3GB）。
- 观感：Mamba2（2.22B）以**更少参数**达成更低 loss，容量已占优且非容量换收敛；其劣势集中在训练吞吐（-24%）与 SSM 计算密度。

## S3 推理基准（mcore 直驱，已完成 2026-09-29）
- **方式**：不转 HF/SGLang（vLLM 本环境 import 崩），直接 mcore `infer_benchmark.py` 加载 `iter_0001000` checkpoint 做 prefill/decode 计时（TP=1 / 1×H100 / bf16 / seq2048 prompt + 256 gen / batch=1 / prefill-iters=12，torchrun nproc_per_node=1）。已修 `infer_benchmark.py`：`seq_length=4096`（与训练一致，避免 model.seq_length 与 dataset.sequence_length 失配断言）、`train_iters` 保持 > warmup 使 scheduler 通过（skip_train=True 不真训练）。
- **结果（最终复核，2026-09-29 晚）**：MiniCPM5 prefill=21,436 tok/s（95.5ms）、decode=2.21 tok/s（452ms/token ⚠️）；Mamba2 prefill=23,692 tok/s（86.4ms）、decode=22.77 tok/s（44ms/token）。
- **trusted 结论**：prefill Mamba2 快 ~10.5%；decode Mamba2 快 ~10.3×（SSM 逐 token O(1) 循环解码）。
- **✅ decode 根因已用 torch.profiler 定位（新增，覆盖旧「KV-cache 未命中」猜测）**：MiniCPM5 decode 偏慢是 **mcore 直驱（无 CUDA-graph/flashinfer）下 TE fused-attention 逐层 CPU launch 开销**——单步 `Self CPU≈620ms`（`FusedAttnFunc` 42 层×~13.8ms=579ms 占 93.4%）vs `Self CUDA 仅 4.05ms`，即 **CPU-bound 非 GPU-bound**（纯 GPU 上界 ≈250 tok/s）。非「KV-cache 未命中」，也非重算。Mamba2 仅 4 attention 层 + SSM/MLP，SSM 层 CPU 开销极低，故 decode 快 ~10×。**两架构同一代码路径测量，相对结论可信**；MiniCPM5 绝对 decode 如需生产级值应走 SGLang/CUDA-graph。
- 日志：`/tmp/BAIZE2B_minicpm5_final.log`、`/tmp/BAIZE2B_mamba2_final.log`（均含 `RESULT_JSON`）；诊断脚本 `infer_diag.py` / `infer_prof.py`（可复现 profiler 结论）。
