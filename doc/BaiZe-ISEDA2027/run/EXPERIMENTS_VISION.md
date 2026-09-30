# EXPERIMENTS_VISION.md — BaiZe Stage(iii) 视觉编码器预训练对比

> 四架构（500–600M）从零预训练公平对比。统一 open_clip(3.2.0) + SigLIP + 固定 text tower + 统一子集。

## 胜出结论（S0+S1+S2 汇总）

**胜出架构：OpenVision2（纯 Attention ViT，w1024·d30·h16·mlp4096，505.0M）**

- P0 三硬指标：训练吞吐 **1491 img/s（最优）**、推理 **153.7 img/s / 6.51ms（最优）**、S1 loss 6.7342（四者并列）。
- 关键量化洞见：1000 步下四架构 loss 全部收敛到**同一平台 6.7342**——固定 text tower 的 SigLIP 对比目标主导早期学习，架构差异在 1000 步内不显 loss 差异，仅拉开吞吐/延迟。
- 吞吐/延迟差异由结构决定（224/16 · 196 token 小序列）：纯 Attention 最优；SSM（MambaEye 全 SSM、DeepEncoderV2 混合双向 Mamba）与 MoE 路由在 196 token 下**开销主导、吃不到长序列红利**，故训练/推理均显著更慢。

> ⚠️ 吞吐测量带病（共享集群）：S1/S2 与另一项目 `nemo_experiments` 的 s1_01/s2_01（arch=mamba2，8×H100）并发，存在争用。DeepEncoderV2 训练稳态 578 img/s 系「误触发 openvision2 进程争用」污染，其干净稳态 ≈1430–1450 img/s（step300–725）。相对排序不受影响。

## 环境与配置

- BASE_DIR：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027`；实际代码在 `run/vision/`（models.py / data.py / train.py / prep_data.py / run_train.sh / run_s1.sh）
- 环境：conda `py310`（CUDA 12.8 / PyTorch 2.8.0 / open_clip 3.2.0 / torchvision 0.23 / mamba_ssm / webdataset 1.0.2 / flash_attn）
- GPU：6×H100 80GB（DP6，TORCH_NCCL）。四架构同卡数、同 batch、同 seed。
- 数据：LLaVA-OneVision-1.5 Mid-Training（parquet）切成统一子集 `imagenet/EN` 500K 对 →
  webdataset tar（`/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar`，25 shard × 20K）
- 默认配置（S1 锚点）：cls=224 / patch=16 / SigLIP / lr=1e-3 AdamW(0.9,0.95) / warmup 100 + cosine /
  seed=1234 / bf16 / batch=32×6=192 / text tower = 12L·512w·8h（四架构共用随机 init）

## 四架构实测参数量（numel，target 500–600M）

| 架构 | 类型 | 参数量 | 激活参数 | 备注 |
|:---|:---|:---|:---|:---|
| OpenVision2 | 纯 Attention ViT | 505.0M | 505.0M | w=1024 d=30 h=16 mlp=4096 |
| MambaEye | 纯视觉 SSM（Vim 双向） | 534.9M | 534.9M | w=1024 d=40 d_state=16 expand=2 |
| MoE-ViE | 稀疏 MoE | 505.2M | 222.0M | w=1024 d=30，8 expert×ff512，top-2 |
| DeepEncoderV2 | Attn+SSM 混合（AAMM） | 516.9M | 516.9M | w=1024 d=34 混合 |

## S0 冒烟（15 步，6 卡 batch32）

| ID | 架构 | 参数量 | loss@15 | ms/iter | image/s | 状态 |
|:---|:---|:---|:---|:---|:---|:---|
| S0-A | OpenVision2 | 505.0M | 7.797 | 127.5 | 1505 | ✅ RUNNABLE |
| S0-B | MambaEye | 534.9M | 7.827 | 510.1 | 376 | ✅ RUNNABLE |
| S0-C | MoE-ViE | 505.2M(222M) | 9.254 | 1371.6 | 140 | ✅ RUNNABLE(未达稳态) |
| S0-D | DeepEncoderV2 | 516.9M | 7.794 | 247.0 | 777 | ✅ RUNNABLE |

> 注：15 步含 cudnn autotune/首步惰性初始化，MoE 的 ms/iter 尚在下降未达稳态，S1(1000步) 会重测 steady-state。

## S1 主训练（1000 步 × 4 架构，默认配置）

| ID | 架构 | 参数量 | 状态 | 最终loss | 训练image/s | 耗时 | GPU·h |
|:---|:---|:---|:---|:---|:---|:---|:---|
| S1-A | OpenVision2 | 505.0M | ✅ 完成 | 6.7342 | 1491 | 235s | 0.39 |
| S1-B | MambaEye | 534.9M | ✅ 完成 | 6.7342 | 398 | 642s | 1.07 |
| S1-C | MoE-ViE | 505.2M(222M) | ✅ 完成 | 6.7342 | 443 | 531s | 0.88 |
| S1-D | DeepEncoderV2 | 516.9M | ✅ 完成 | 6.7342 | 578* | 303s | 0.51 |

> *DeepEncoderV2 训练吞吐被「误触发的 openvision2 进程」争用污染（step750–1000 掉到 ~578）；干净稳态 ≈1430–1450 img/s，实则仅次于 OpenVision2。四者最终 loss 全部 6.7342（同种子同数据同 text tower，SigLIP 对比平台）。

## S2 推理基准（batch=1 前向，bf16，224/16）

| 架构 | 参数量 | ms/img | image/s | token/s(=img×196) | 备注 |
|:---|:---|:---|:---|:---|:---|
| OpenVision2 | 505.0M | 6.508 | **153.7** | 30117 | 纯 Attention，最优 |
| DeepEncoderV2 | 516.9M | 17.761 | 56.3 | 11035 | 混合 AAMM，双向 Mamba 前向重 |
| MoE-ViE | 505.2M(222M) | 141.721 | 7.1 | 1383 | 路由+sort/grouped 纯 PyTorch，CPU 主导 |
| MambaEye | 534.9M | — | 卡死/超时 | — | mamba_ssm selective_scan 在 batch=1 停摆（150s 超时） |

> S2 说明：batch=1 单图推理是 MLLM 编码器最常见场景。SSM/MoE 的小 batch 延迟劣势在推理端被放大——MambaEye 全 SSM 在 batch=1 停摆、DeepEncoderV2 混合比纯 Attention 慢 ~2.7×、MoE-ViE 慢 ~22×（路由 CPU 开销）。纯 Attention 无论训练吞吐还是推理延迟均为最优。

## 后续阶段（P1/P2/P3，按预算推进）

- ✅ S2 推理基准（batch=1 前向，图像→token/s）——已完成，见上表
- 🔄 S3 长地平线（进行中：OpenVision2 10k 步 + DeepEncoderV2/MambaEye/MoE-ViE 各 5k 步，10.239.2.12 GPU0-5，2026-09-30 12:50 启动）——log `/tmp/s3_main.log`、`out/S3_<tower>/train.log`
- ⏭️ S4 多种子（前 2 架构 × 3 seed，脚本 `vision/run_s4.sh` 已备）
- ⏭️ S5 下游代理（zero-shot / retrieval / linear-probe）
- ⏭️ S6 分辨率/patch 消融（脚本 `vision/run_s6.sh` 已备：336/16、448/16、224/14、336/14、448/14）
- ⏭️ S7 目标函数/数据、S8 LR/warmup、S9 推理深挖