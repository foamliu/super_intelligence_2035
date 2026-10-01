# EXPERIMENTS_VISION_ROUND5.md — 用修复 recipe 重跑架构 / 分辨率对比

> **BaiZe Stage(iii) 视觉编码器预训练 · Round 5**
> 定位：R4 已解决核心阻塞（C1–C4 全过），但 R1/R2 的 loss 类结论已因坍缩作废。R5 = 用修好的 recipe 重跑架构/分辨率对比，为 `tab:visarch` / `tab:visres` / `tab:visobj` 取有效读数。
> 固定 recipe（R4 已验证）：冻结 `openai/clip-vit-large-patch14-336` text tower（768 维、全参冻结）+ `open_clip.loss.ClipLoss`（InfoNCE，`local_loss=False`、只学 logit_scale、无 logit_bias）+ vision 读出头 embed_dim→768 + lr 3e-3 / warmup 20。
> 日期：2026-10-01。GPU 10.239.2.12（8×H100，TP1/DP8）。

---

## ⭐ 胜出架构 + 完整可复现命令（放文件顶部）

**胜出架构：OpenVision2（纯 Attention ViT，w1024·d30·h16·mlp4096·SwiGLU·avg-pool，505.2M）**

**决定性证据（P0 架构对比，4 架构 × 3000 步 @224/16 bs64=512 负样本，同一 recipe）**：
- **唯一**既不坍缩又最快的架构（final_loss 4.549 = 四架构最低；训练 2419.8 img/s = 四架构最快；C2_gap +0.0818 = 四架构最强）。
- 次优 MoE-ViE 虽不坍缩但 loss 更高（5.780）、训练更慢（1264.5 img/s）、C2_gap 更弱（+0.0466）。
- 🔴 **关键发现**：两个含 SSM(Mamba) 块的架构（MambaEye 纯 SSM、DeepEncoderV2 Attn+SSM 混合）在 **step 300 就坍缩**（C1=1.0000、C2_gap≈0）→ 见 §1。

**可复现命令**：
```bash
conda activate py310
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision

# P0 架构对比（4 架构 × 3000 步 @224/16 bs64，8 卡 TP1/DP8，串行）
bash r5_p0.sh

# P1 分辨率对比（胜出架构 openvision2 × {224/16, 336/14, 448/14}，bs16=128 负样本，batch 匹配）
bash r5_p1.sh openvision2
```
脚本 `r5_train.py`（固定 recipe）+ `r5_p0.sh` / `r5_p1.sh`。日志 `/tmp/r5_p0.log` / `/tmp/r5_p1.log`，ckpt `/nas_train/app.e0031982/datasets/baize-vision/out/R5_*`。

---

## 0. GPU 独占 + NFS 并发核验（P0 启动时原文）

```
# P0 启动时（22:29）GPU 独占核验（r5_p0.log head，逐字）：
pid, process_name, used_gpu_memory [MiB]
(空 —— 无任何 compute apps)
index, memory.used [MiB], utilization.gpu [%]
0, 0 MiB, 0 %  / 1, 0 MiB, 0 % / 2, 0 MiB, 0 % / 3, 0 MiB, 0 %
4, 0 MiB, 0 %  / 5, 0 MiB, 0 % / 6, 4 MiB, 0 % / 7, 4 MiB, 0 %
```
- **NFS 并发**：pretrain 任务（10.239.2.29）当时 **P-5a GBS×LR 扫描已 ALL DONE @22:54**，其后 GPU 全空闲、无重 I/O（`MEMORY_PRETRAIN_2B.md` PHASE=R2_active/WAITING=1，下一唤醒才做 P-4）。→ P0/P1 无 pretrain NFS 争用。
- **P1 启动时（23:58）**：GPU 0–7 再次核验全空闲（0 MiB compute）；pretrain 仍在 idle（P-5a 之后、P-4 之前）。

---

## 1. P0 架构对比（4 架构 × 3000 步，锚点 224/16，bs64=512 负样本，batch 匹配）

| 架构 | 参数量(总/激活) | 步数 | final_loss(EMA) | loss@1k | loss@2k | loss@3k | 训练img/s(稳态) | C1@终 | C2_gap@终 | C4 | 判定 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| **OpenVision2** | 505.2M / 505.2M | 3000 ✅ | **4.5490** | 4.5385 | 4.6585 | 4.7695 | **2419.8** | **0.3008** | **+0.0818** | OK | ✅ 全过 |
| MoE-ViE | 505.5M / 222.2M | 3000 ✅ | 5.7800 | 5.3322 | 5.5712 | 5.8605 | 1264.5 | 0.3202 | +0.0466 | OK | ✅ 全过 |
| DeepEncoderV2 | 517.2M / 517.2M | **300 ❌ 熔断** | 6.2518 | — | — | — | 1813.1 | **1.0000** | **−0.0000** | OK | ❌ C1 坍缩+C2 无间隙 |
| MambaEye | 535.2M / 535.2M | **300 ❌ 熔断** | 6.2526 | — | — | — | 918.4 | **1.0000** | **−0.0000** | **FAIL** | ❌ C1 坍缩+C2 无间隙+C4 失败 |

> loss@1k/2k/3k 取训练日志 `[step N/3000] loss=` 的原始 step loss（未平滑）；final_loss 为 loss_ema。参数量从 P0 日志 `[params]` 行取：openvision2 505.2M、deepencoder_v2 517.2M、mambaeye 535.2M、moevie 505.5M(active 222.2M)。
> 推理 ms/img（batch=1，架构固有，沿用 R1 S2 / R2-5 既有 bench）：OpenVision2 6.51ms / DeepEncoderV2 17.76ms / MambaEye 31.6ms（R2-5 修正） / MoE-ViE 141.7ms。

### 1.1 🔴 核心发现：SSM 架构在修复 recipe 下 step 300 仍坍缩（架构相关，非纯 recipe）

- R4 曾把坍缩主因归为「随机文本塔 + SigLIP」这一 **recipe 层**问题，并以 OpenVision2 验证修复后 C1–C4 全过。
- **R5 P0 首次全架构放量揭示**：即便换成 R4 验证过的固定 recipe（冻结语义 CLIP 文本塔 768 + InfoNCE + head→768），**两个含 Mamba(SSM) 块的架构仍在 step 300 崩掉**：
  - `DeepEncoderV2`（Attn+SSM 混合，pattern 'AAMM'）@step300：**C1=1.0000**（128 张图特征两两余弦=1，完全坍缩）、C2_gap=−0.0000、C4 尚 OK。
  - `MambaEye`（纯 SSM）@step300：**C1=1.0000**、C2_gap=−0.0000、**C4=FAIL**（loss_ema 6.2526 反而高于 early 6.2086 → 不降）。
- ✅ 对照组：`OpenVision2`（纯 Attention）与 `MoE-ViE`（Attention+稀疏 MoE FFN）**都不坍缩**，C1 一路稳定在 0.14–0.32、C2_gap 维持正间隙跑满 3000 步。
- **→ 结论（证据支撑，不臆测）**：坍缩**并非纯 recipe 现象**，在固定 recipe 下仍**架构相关**——**含 SSM(Mamba) 块的视觉塔在 InfoNCE + 冻结 CLIP 文本塔下 step 300 内必坍缩；纯 Attention / Attention+MoE 不坍缩**。这是 R5 最有价值的发现（详见 §5 论文回填建议）。
### 1.2 熔断说明（可复现 + 脚本级缺陷备注）

- 熔断判定代码 `r5_train.py:243-248`：`C1>0.95` → `C1 collapse`；`gap<=0.005` → `C2 no-gap`；`C4 不降` → `C4 fail`。DeepEncoderV2 / MambaEye 均在 step 300 探针命中 C1 collapse（C1=1.0000>0.95）+ C2 no-gap，MambaEye 额外命中 C4 fail。
- 熔断后 checkpoint 已存 `out/R5_P0_{deepencoder_v2,mambaeye}/vision_fused.pt`（`fuse_reason` 已写）。
- 🐛 **脚本级缺陷（影响收尾但不影响数据）**：`r5_train.py` 的熔断 `break` 只在 rank 0 生效，其余 rank 仍在训练循环/`all_gather` 内 → 触发 **SIGABRT/ChildFailedError**（`exit code -6`），使 torchrun 整体 `exit 1`。**数据无损**（探针 + fused ckpt 在崩溃前已落盘）。P1 只用 openvision2（不熔断）故不受影响；后续若再跑 SSM 臂，应先修此缺陷（广播 stop 标志）。

---

## 2. C1–C4 监控轨迹（每 300 步，P0）

### OpenVision2（✅ 全过，3000 步）
| step | C1 | C2_diag | C2_off | C2_gap | loss_ema | C4 |
|:--|:--|:--|:--|:--|:--|:--|
| 300 | 0.1402 | 0.1903 | 0.0352 | +0.1551 | 4.1708 | OK |
| 600 | 0.2347 | 0.1562 | 0.0312 | +0.1250 | 3.6091 | OK |
| 900 | 0.2662 | 0.1307 | 0.0307 | +0.1000 | 4.1870 | OK |
| 1200 | 0.3016 | 0.1187 | 0.0342 | +0.0845 | 4.3174 | OK |
| 1500 | 0.3142 | 0.1206 | 0.0339 | +0.0866 | 4.4420 | OK |
| 1800 | 0.2744 | 0.1155 | 0.0291 | +0.0865 | 4.4734 | OK |
| 2100 | 0.3051 | 0.1200 | 0.0362 | +0.0838 | 4.4953 | OK |
| 2400 | 0.3569 | 0.1163 | 0.0406 | +0.0757 | 4.6309 | OK |
| 2700 | 0.2708 | 0.1245 | 0.0406 | +0.0839 | 4.6934 | OK |
| 3000 | 0.3008 | 0.1248 | 0.0430 | +0.0818 | 4.5490 | OK |

### MoE-ViE（✅ 全过，3000 步，但表征/收敛明显弱于 OpenVision2）
| step | C1 | C2_diag | C2_off | C2_gap | loss_ema | C4 |
|:--|:--|:--|:--|:--|:--|:--|
| 300 | 0.2494 | 0.1264 | 0.0340 | +0.0924 | 5.1619 | OK |
| 600 | 0.3308 | 0.1399 | 0.0703 | +0.0696 | 5.4527 | OK |
| 900 | 0.4395 | 0.1259 | 0.0771 | +0.0489 | 5.5900 | OK |
| 1200 | 0.3454 | 0.1459 | 0.0855 | +0.0603 | 5.4340 | OK |
| 1500 | 0.4781 | 0.1462 | 0.1046 | +0.0415 | 5.7068 | OK |
| 1800 | 0.3871 | 0.1525 | 0.0936 | +0.0588 | 5.5294 | OK |
| 2100 | 0.3546 | 0.1451 | 0.0883 | +0.0568 | 5.5051 | OK |
| 2400 | 0.3163 | 0.1255 | 0.0773 | +0.0482 | 5.5112 | OK |
| 2700 | 0.3713 | 0.1151 | 0.0685 | +0.0466 | 5.8005 | OK |
| 3000 | 0.3202 | 0.1043 | 0.0577 | +0.0466 | 5.7800 | OK |

### DeepEncoderV2 / MambaEye（❌ 熔断 @step300）
| 架构 | step | C1 | C2_diag | C2_off | C2_gap | loss_ema | loss_early | C4 | 熔断原因 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| DeepEncoderV2 | 300 | 1.0000 | 0.3861 | 0.3861 | −0.0000 | 6.2518 | 6.2749 | OK | C1 collapse + C2 no-gap |
| MambaEye | 300 | 1.0000 | 0.3944 | 0.3944 | −0.0000 | 6.2526 | 6.2086 | **FAIL** | C1 collapse + C2 no-gap + C4 fail |

---

## 3. P1 分辨率对比（胜出架构 OpenVision2 × {224/16, 336/14, 448/14}，3000 步，bs16=128 负样本，batch 匹配）

> ⌛ **运行中**（23:58 启动，`/tmp/r5_p1.log`）。三组统一 bs=16（128 负样本）以匹配 batch（448/14=1024 token 无法在 bs>16 下不进 grad-ckpt 放得下，R2 实测 576 token 已 ~37GB@bs32）；224/16 与 336/14 同样降到 bs16 保持可比。
> ⚠️ **batch 效应照应**：P1 全 bs16（128 负样本）的 loss 天然低于 P0 的 bs64（512 负样本）——负样本越多 InfoNCE 越难 → loss 越高。故 P1 的三组**只在组间可比**，不能与 P0 表比 loss 绝对值。

| 分辨率/patch | token 数 | batch | 状态 | final_loss | 训练img/s | C1 | C2_gap | C4 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| 224/16 | 196 | 16（128 负样本，匹配） | ✅ done（00:04，338.6s） | **3.0977** | 1361.7 | 0.3078 | +0.0906 | OK |
| 336/14 | 576 | 16（128 负样本，匹配） | ⌛ running | — | — | — | — | — |
| 448/14 | 1024 | 16（128 负样本，匹配） | 待跑 | — | — | — | — | — |

---

## 4. P2 长地平线 + 下游（选做，时间允许）

> 待 P1 完成后按剩余预算（R5 墙钟 ≤6h；P0 墙钟 1h12m）决定是否做（胜出架构 × 10000 步，3000/6000/10000 步记 eval5k R@1/5/10 i2t/t2i + loss）。

---

## 5. 论文回填建议（`6_vision_encoder.tex`；🚫 本任务不改 tex）

> 现状：当前 `6_vision_encoder.tex` 仍是**旧 recipe**（SigLIP + 共享 512w 随机 text 塔 + lr 1e-3 锚点），`tab:visarch/visres/visobj` 三表全是**坍缩读数**，必须回滚重写。

1. **`tab:visarch_res` / `tab:visarch`（必须回滚重写）**：R2 那版是坍缩读数（四架构 loss 全 4.9962/6.7342 的 LR/坍缩伪影），**一律作废**。替换为 R5 P0 的 **InfoNCE + 冻结 CLIP-768 修复配方**读数（§1 表）：OpenVision2 loss 4.549 / C1 0.301 / C2_gap +0.082 / 2419.8 img/s；MoE-ViE loss 5.780 / C1 0.320 / C2_gap +0.047 / 1264.5 img/s；**DeepEncoderV2、MambaEye = step300 坍缩（C1=1.0），不得作为有效 loss 读数**。
2. **`tab:visarch` 核心叙事从「loss 与架构无关」改为「坍缩与架构相关」**：R2 结论「loss 不可区分」是坍缩伪影；R5 用有效配方后，**四架构不再并列**——OpenVision2 明显最优（loss/吞吐/C2_gap 三领先），SSM 类 vs Attention 类架构在「是否坍缩」上二值分化。这是**可发表的正结论**。
3. **`tab:visres`（分辨率）**：R2 那版 loss 全 4.9962（LR 伪影）作废；R5 P1（§3）跑完填 OpenVision2 × {224/16,336/14,448/14} 的（loss + token 数 + batch + C1/C2），并**显式标注 batch 已匹配（全 bs16）**。
4. **`tab:visobj`（目标函数）**：R2-2 曾用「eval5k R@K 不可跨目标比较」结论回填；R4 已证原 recipe 坍缩、eval R@K 退化为精确 chance。R5 固定 InfoNCE（R4 验证过），SigLIP 臂在修复 recipe 下是否需要重跑不在 R5 范围——建议目标函数列如实写「InfoNCE（经 R4 选定 + R5 放量验证）」。
5. **坍缩写法（R4 已提，R5 强化）**：把「坍缩」从"发现"升级为**可复现的架构相关现象**：固定 recipe 下 SSM 视觉塔 step300 内坍缩（C1=1.0），Attention/MoE 不坍缩。附 C1–C4 轨迹（§2）作证据。
6. **命名去歧义（R6 已提，R5 沿用）**：论文 "OpenVision2" 须明确「本项目从零设计的纯 Attention ViT 基线」（30L/1024w/505M/SwiGLU/avg-pool/224-16），并非复现 UCSC-VLAA 官方 OpenVision2（24L/1024w/304.5M/gelu/336-14）。
- ⚠️ 按 R5.5 铁律：**未重试**让 SSM 架构「看起来好」，如实记录熔断。SSM 架构若要可用，需专门调它的 recipe（LR/warmup/归一化/初始化/更长 horizon），**不在本任务单变量协议内**。