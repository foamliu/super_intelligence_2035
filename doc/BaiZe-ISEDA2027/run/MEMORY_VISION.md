# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | S3（长地平线 running：OpenVision2✅2 塔 done，MambaEye ~step2100/5000，MoE-ViE ⏳排队，10.239.2.12 GPU0-5） |
| WAITING | 1 |
| ERROR_COUNT | 0 |
| BUDGET_USED | ~8 GPU·h（S0-S3 已完部分为主，S3 尾段 mambaeye+moevie 未计） |
| 更新 | 2026-09-30 13:42 |
| WINNER | OpenVision2（S3 长地平线 loss 4.4540@10k + 训练 2139/推理 153.7 img/s，双指标最优；DeepEncoderV2 4.4662@5k 紧随） |

## 等待说明（WAITING=1）

- 等待：S3 长地平线训练（后台，运行于 **10.239.2.12** GPU0-5）。
- ⚠️ 判断结束改用 **`out/S3_<tower>/train.log`**（rank0 直写、实时 flush）：`/tmp/s3_main.log` 因 `grep|tee` 管道缓冲**严重滞后**（13:08 时 main.log 停在 step5600，但 train.log 已 step7200）。4 个塔的 `out/S3_<tower>/train.log` 各出现 `[done]` 即 S3 结束（或 `pgrep -af 'train.py --tower'` 无本项目进程）。
- 结束后：WAITING 置 0，用 `python3 vision/analyze_s3.py` 汇总 loss 曲线 → 判断 loss 排名是否翻转 → S4 多种子（脚本 `vision/run_s4.sh` 已备好，用新 train.py 存 full ckpt）。

> ⚠️ 重要：本环境 `run_commands` 只能执行**单 token 无参**命令（`ls`/`find`/`nvidia-smi` 可用，`ls -la` 这类带参必报 “Executable not found”）。**跑带参命令请用 shell-exec 队友**：`team_spawn_teammate(agentId=shell-exec)` 后 `team_run_task(agentId=shell-exec, task=<完整 bash 命令>)`（队友 shell 正常、可 ssh 多参）。每次唤醒需重新 spawn。

## 当前状态

S0 冒烟 + S1 主训练（1000 步×4）+ S2 推理基准 全部完成，**胜出架构 OpenVision2**（训练 1491 img/s / 推理 153.7 img/s，均最优；loss 6.7342 四者并列）。详见 EXPERIMENTS_VISION.md。
代码落地于 `run/vision/`：models.py（四架构）、data.py（webdataset 加载）、train.py（torchrun DDP + SigLIP/CLIP + 固定 text tower）、prep_data.py（parquet→tar）、bench.py（S2 推理基准）、run_train.sh / run_s1.sh / run_s2.sh。
数据：LLaVA-OneVision imagenet/EN 500K 已切 webdataset tar（`/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar`，25 shard）。
S1 权重落盘 `out/S1_<tower>/vision.pt`（四架构）。

## 下一步

- **当前**：S3 长地平线 running（OpenVision2 10k 步 + 另 3 架构各 5k 步，10.239.2.12 GPU0-5）。S3 完成后用 `vision/analyze_s3.py` 看 loss 曲线是否在 5k–10k 步突破 6.7342 平台、架构间排名是否翻转。
- **随后**：S4 多种子（前 2 架构 × 3 seed × 1000 步，脚本 `vision/run_s4.sh`）→ S5 下游代理（zero-shot/linear-probe）→ S6 分辨率/patch 消融（`vision/run_s6.sh`）→ S7 目标函数/数据 → 收敛报告 + HTML + 回填 tex。

> 节点拓扑：本 agent 常驻 **10.239.2.29**（whag0pgpuap29，8 卡全被 `nemo_experiments` mamba2 占用）；本项目训练在 **10.239.2.12**（whag0pgpuap12）GPU0-5（空闲），用 `ssh 10.239.2.12 '...'` 提交。 代码/数据/权重均在 NFS `/nas_train`，两节点共享。

## 操作流水

- ✅ [2026-09-30 11:29] S0 data_check：确认 LLaVA-OneVision parquet schema（id/image{bytes,path}/caption）、选 imagenet/EN 子集；open_clip 3.2.0 + mamba_ssm + webdataset 1.0.2 可 import；GPU 0–5 空闲。
- ✅ [2026-09-30 11:31] 修复 webdataset 1.0.2 TarWriter.write(dict) 签名 + nodesplitter 默认 single_node_only 报错 + 空 shard→worker 报错（num_workers=2 + 12 shard）。
- ✅ [2026-09-30 11:35] 落地四架构（models.py），实测参数量 OpenVision2 505M / MambaEye 535M / MoE-ViE 505M(active222M) / DeepEncoderV2 517M。
- ✅ [2026-09-30 11:40] S0 冒烟（15 步）四架构全 RUNNABLE，吞吐基线 OpenVision2≈1505 / DeepEncoderV2≈777 / MambaEye≈376 / MoE-ViE≈140 image/s。
- ✅ [2026-09-30 11:41] MoE forward 优化（per-expert nonzero→sort+grouped），GPU 算力 35ms/CPU 274ms 诊断，fwd+bwd 降到 ~363ms；S1 将取稳态吞吐。
- ✅ [2026-09-30 11:45] 启动 S1：4 架构 × 1000 步（en500k，batch32×6，seed1234，SigLIP）。日志 /tmp/s1_main.log。
- ✅ [2026-09-30 ~12:20] S1 完成：四架构 loss 全 6.7342；训练吞吐 OpenVision2 1491 / DeepEncoderV2 ~1445*(578 受污染) / MoE-ViE 443 / MambaEye 398 img/s。
- ✅ [2026-09-30 ~12:33] S2 推理基准（batch=1 bf16 224/16）完成：OpenVision2 153.7 / DeepEncoderV2 56.3 / MoE-ViE 7.1 img/s；MambaEye batch=1 停摆(150s 超时)。→ 结论：**OpenVision2 胜出**。
- ⚠️ 误触发：agent 测试 shell 执行时重复 `./vision/run_s1.sh`，触发重复 openvision2 训练，已 pkill 回收（污染 DeepEncoderV2 后半段吞吐 + 误记 GPU·h ~0.39）。
- ✅ [2026-09-30 12:44] 唤醒恢复：确认本 agent 在 10.239.2.29，本项目 GPU 在 10.239.2.12（GPU0-5 空闲，GPU6-7 他人占 ~72GB）。搭 shell-exec 队友绕过 run_commands 单-token 限制。
- ✅ [2026-09-30 12:47] 落地 `vision/run_s3.sh`（S3 长地平线：OpenVision2 10k + DeepEncoderV2/MambaEye/MoE-ViE 各 5k 步）。
- ✅ [2026-09-30 12:48] 修复 `run_train.sh`/`run_s2.sh` 的 `LD_LIBRARY_PATH` unbound variable（非交互 ssh 环境下未设 → `set -u` 报错），改 `${LD_LIBRARY_PATH:-}`。
- ✅ [2026-09-30 12:50] S3 启动于 10.239.2.12 GPU0-5（setsid nohup）。干净吞吐 OpenVision2 ~1950 img/s（比 S1 的 1491 高，无争用）；step550 loss 已 6.7342。
- ✅ [2026-09-30 ~12:57] S3 进度巡检（shell-exec 队友）：OpenVision2 推进到 step2550/10000，loss=4.47（持续跌破 S1 的 6.7342 平台，长地平线确有信息量）；其余 3 塔（deepencoder_v2/mambaeye/moevie）排队中，待 openvision2 先跑完串行续跑。ETA 整轮 S3 ≈1.6–1.7h（openvision2 10k ≈16min + 3 塔各 5k ≈11/40/36min）。
- ✅ [2026-09-30 ~12:59] S5 下游 infra 落地（非阻塞 prep，S3 running 期间）：① train.py 改为保存**完整模型**（vision+text+logit_scale+logit_bias），S4+ 起 checkpoint 含 text tower；② 新增 `vision/eval_downstream.py`（text↔image 双向检索 R@1/5/10，通用 full/vision-only ckpt）；③ 新增 `vision/run_s5.sh`（从 laioncn/EN 挖 held-out 5k eval set，不同源→真 zero-shot）。语法检查通过。
- ⚠️ 关键 caveat：S1/S3 的 checkpoint 是**旧 train.py 只存 vision**（无 text），检索需 joint text；S4（多种子，用新 train.py）起才有 full ckpt。S5 检索将用 S4 full ckpt（或胜出架构跑一轮 short joint 补 text）。无 ImageNet val/类标签 → 「zero-shot top-1 / linear-probe」不可行，S5 只做检索 R@K。
 - ✅ [2026-09-30 13:09] S3 运行期间非阻塞 prep（WAITING 保持 1）：① 落地 `vision/run_s7.sh`（SigLIP vs CLIP InfoNCE 消融）、`run_s8.sh`（lr∈{1e-3,3e-3,5e-3}+warmup 档）、`run_s9.sh`（batch∈{1,8,32}+多分辨率 bench），bash -n 通过；② 预切 S5 检索 held-out 评估集 `eval5k`（laioncn/EN 5000 对，1 shard，与训练源 imagenet/EN 不同→真 zero-shot）；③ 关键观测：`/tmp/s3_main.log` 因 grep|tee 缓冲滞后 ~40min，改用 `out/S3_<tower>/train.log` 判断完成。
- ✅ [2026-09-30 13:42] S3 巡检 + 🔑**关键诊断**：openvision2(10k)✅ done loss 4.4540/2139img/s、deepencoder_v2(5k)✅ done 4.4662/1458、mambaeye🔄 ~step2100/5000(4.64↓,800img/s)、moevie⏳排队。**发现 S1「6.7342 平台」= cosine LR 坍缩伪影（`--steps 1000` 令 cosine 过早衰减 LR→~1e-5@1000 步，loss 卡死），非架构等价**：train.py/data.py 在 S1/S3 间无 diff，唯一变量 `--steps` 改变 cosine 跨度；S1 step100=7.6147 ≈ S3 step100=7.6082（同轨迹），step600 后分叉（S1 卡 6.7342、S3 续降至 5.92@1k→4.45@5k）。→ 结论修正：loss 排名 OpenVision2≈DeepEncoderV2<MambaEye，loss 差 <0.012@5k，但吞吐/延迟差巨大确定。S6/S7/S8 若仍 1000 步会落入 LR 坍缩区间，已权衡是否提 2000-3000 步；S5 检索 R@K 是真实区分信号。已跑通 `analyze_s3.py`。eval5k(.png/.txt) + prep_data 参数 + tex 路径均已核。

## 备注 / 风险

- MoE-ViE 吞吐在 15 步冒烟中未达稳态（1371ms/iter 尚在降），且为纯 PyTorch expert-loop + sort 路由（未用 fused MoE kernel），1000 步后会重测；若仍显著慢，报告注明「路由开销为主，非 FLOPs 上限」。
- 数据/网络盘 `/nas_train` 为 NFS（10.239.23.31），tar 读取带宽 ~60MB/s；训练数据加载非瓶颈（openvision2 1505 image/s 可证）。
- MoE-ViE 稳态训练 443 img/s、推理 7.1 img/s：纯 PyTorch expert-loop + sort 路由，CPU 路由开销主导（非 FLOPs 上限）。若后续需 MoE 路线，需 fused MoE kernel（如 megablocks/TRT-MoE）。
- **MambaEye 全 SSM 在 batch=1 推理停摆**（mamba_ssm selective_scan kernel 卡死，150s 超时）；同塔在训练（batch=32×6）正常（398 img/s）。小 batch SSM 延迟为已知痛点，需专门排查 batch=1 路径。
- 共享集群争用：S1/S2 与另一项目 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments`（arch=mamba2，s1_01→s2_01，8×H100）并发，吞吐测量含争用；GPU 6-7 亦曾被他人占用。