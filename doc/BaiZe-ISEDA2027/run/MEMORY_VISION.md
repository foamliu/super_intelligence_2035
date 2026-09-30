# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | S1 |
| WAITING | 1 |
| ERROR_COUNT | 0 |
| BUDGET_USED | ~0 GPU·h（S1 进行中） |
| 更新 | 2026-09-30 11:45 |

## 等待说明（WAITING=1）

- 等待：S1 主训练（4 架构 × 1000 步）后台运行。
- 日志：`/tmp/s1_main.log`；各架构子日志 `out/S1_<tower>/train.log`。
- 判断结束：`/tmp/s1_main.log` 出现 `===== S1 ALL DONE =====`（或 4 个 `===== S1 <tower> done` 全部出现）。
- 结束后：把 WAITING 置 0，回填 S1 表（loss/吞吐）→ 进入 S2 推理基准。

## 当前状态

S0 冒烟完成：四架构全部 RUNNABLE、参数量落 500–600M（见 EXPERIMENTS_VISION.md）。
代码落地于 `run/vision/`：models.py（四架构）、data.py（webdataset 加载）、train.py（torchrun DDP + SigLIP/CLIP + 固定 text tower）、prep_data.py（parquet→tar）、run_train.sh / run_s1.sh。
数据：LLaVA-OneVision imagenet/EN 500K 已切 webdataset tar（`/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar`，25 shard）。

## 操作流水

- ✅ [2026-09-30 11:29] S0 data_check：确认 LLaVA-OneVision parquet schema（id/image{bytes,path}/caption）、选 imagenet/EN 子集；open_clip 3.2.0 + mamba_ssm + webdataset 1.0.2 可 import；GPU 0–5 空闲。
- ✅ [2026-09-30 11:31] 修复 webdataset 1.0.2 TarWriter.write(dict) 签名 + nodesplitter 默认 single_node_only 报错 + 空 shard→worker 报错（num_workers=2 + 12 shard）。
- ✅ [2026-09-30 11:35] 落地四架构（models.py），实测参数量 OpenVision2 505M / MambaEye 535M / MoE-ViE 505M(active222M) / DeepEncoderV2 517M。
- ✅ [2026-09-30 11:40] S0 冒烟（15 步）四架构全 RUNNABLE，吞吐基线 OpenVision2≈1505 / DeepEncoderV2≈777 / MambaEye≈376 / MoE-ViE≈140 image/s。
- ✅ [2026-09-30 11:41] MoE forward 优化（per-expert nonzero→sort+grouped），GPU 算力 35ms/CPU 274ms 诊断，fwd+bwd 降到 ~363ms；S1 将取稳态吞吐。
- ⏳ [2026-09-30 11:45] 启动 S1：4 架构 × 1000 步（en500k，batch32×6，seed1234，SigLIP）。日志 /tmp/s1_main.log。

## 备注 / 风险

- MoE-ViE 吞吐在 15 步冒烟中未达稳态（1371ms/iter 尚在降），且为纯 PyTorch expert-loop + sort 路由（未用 fused MoE kernel），1000 步后会重测；若仍显著慢，报告注明「路由开销为主，非 FLOPs 上限」。
- 数据/网络盘 `/nas_train` 为 NFS（10.239.23.31），tar 读取带宽 ~60MB/s；训练数据加载非瓶颈（openvision2 1505 image/s 可证）。