# EXPERIMENTS_VISION_ROUND2.md — BaiZe Stage(iii) 视觉编码器 · Round 2

> 第二轮：修复 Round 1 论文 §6 的三处硬伤，全部基于现有数据（en500k / eval5k）与现有代码重跑。
> **R2 全局锚点改动：lr 1e-3 → 3e-3**（依据：Round 1 S8 实测 3e-3 → loss 4.4562 显著优于 1e-3 → 4.9962，即 1e-3 在 3000 步 cosine 下是退化配置）。
> 其余锚点不变：SigLIP / AdamW(0.9,0.95) / warmup 100 + cosine / seed 1234 / bf16 / batch 32×6 / en500k / steps 3000。

---

## R2-0 数字核对（零成本，最先做）

### 四架构「步数 → loss」映射表（S3 长跑，lr=1e-3，SigLIP，224/16）

| 架构 | loss@1000 | loss@3000 | loss@5000 | loss@10000 |
|:---|:---|:---|:---|:---|
| OpenVision2 | 5.9180 | 4.4653 | **4.4560** | 4.4540 |
| DeepEncoderV2 | 5.9277 | 4.4723 | **4.4662** | —（仅 5k）|
| MambaEye | 5.9463 | 4.4725 | **4.4700** | — |
| MoE-ViE | 5.9406 | 4.4723 | **4.4661** | — |

> 数据来源：`out/S3_<tower>/train.log` 的 `[step N/... ] loss=...` 行（原值，非 4 位截断）。
> S8 lr=3e-3 @3000 步 OpenVision2 = **4.4562**（`out/S8_ov2_lr3e-3/train.log` 末行）。

### `tab:visarch` 的 `Loss@5k` 判定：**标注正确，无需修改**

| 表格值 | 实际来源 | 判定 |
|:---|:---|:---|
| OpenVision2 **4.456** | S3@5000 步 = 4.4560 | ✅ 正确 |
| DeepEncoderV2 **4.466** | S3@5000 = 4.4662 | ✅ 正确 |
| MambaEye **4.470** | S3@5000 = 4.4700 | ✅ 正确 |
| MoE-ViE **4.466** | S3@5000 = 4.4661 | ✅ 正确 |

- 关键澄清：OpenVision2 的 `4.456` 对应 **S3 10k 长跑的第 5000 步（4.4560，lr=1e-3）**，**不是** 10k 终值 4.4540、也**不是** S8 lr=3e-3 的 4.4562。三者差 <0.0002（噪声级，纯属巧合），但**正确归属是 S3@5000@lr=1e-3**。因此表格四值均出自「同一 LR（1e-3）、同一 5000 步」口径，**内部一致**，R2.0 的疑点（可能混入 3e-3 的 4.4562）经核对**不成立**。

### 其余 `tab:visarch` 数值核对

| 值 | 表格 | 最新记录 | 判定 |
|:---|:---|:---|:---|
| 训练 img/s | OpenVision2=2139 | S3 `steady_image_s=2139.5` | ✅ |
| 训练 img/s | DeepEncoderV2=1459 | S3 =1458.7 | ✅ |
| 训练 img/s | MambaEye=790 | S3 =790.0 | ✅ |
| 训练 img/s | MoE-ViE=852 | S3 =852.3 | ✅ |
| 参数量 | OpenVision2=505.0M | numel 505.0M | ✅ |
| 推理 ms/img | MoE-ViE=141.7 | S2 bench 141.72ms | ✅ |
| 推理 ms/img | OpenVision2=6.51 | S2 bench 6.508ms ⚠️ | 见下 |

> ⚠️ **唯一待查项**：`tab:visarch` 的 OpenVision2 推理 `6.51 ms/img` 出自 S2 原始 bench（6.508ms / 153.7 img/s）；
> 但 S9 干净复测（同 `bench.py`、batch=1、224/16）得到 **10.07ms / 99.3 img/s**（约 1.5× 差异）。
> 二者同为 `bench.py`（autocast bf16、torch.cuda.Event），差异疑为 warmup 深度（S2 warmup=30/iter=100 vs S9 warmup=10/iter=50）或测量时 GPU 时钟状态。
> **交由 R2-4 干净复测裁决**——这是论文头条数字（"6.51ms 最快"），必须闭环。

---

## R2-1 分辨率/patch 消融重跑（@ lr=3e-3）—— **运行中**

> 目标：替换 `tab:visres`（Round 1 六格 loss 全 4.9962 零信息量）。
> 6 组 `{224,336,448}×{14,16}` @ lr=3e-3 × 3000 步 + 1 组坍缩对照 `(224,16)@lr=1e-3`。
> `(224,16)@3e-3` 复用 S8（4.4562），`(224,16)@1e-3` 复用 S8（4.9962，坍缩对照）。

| res/patch | lr | 状态 | loss@3000 | train img/s | 推理 ms/img(bs=1) | tokens/img | eval5k R@1/5/10 |
|:---|:---|:---|:---|:---|:---|:---|:---|
| 224/16 | 3e-3 | ✅ 复用 S8 | 4.4562 | 1645.1 | _待测_ | 196 | _待测_ |
| 224/16 | 1e-3 | ✅ 复用 S8（坍缩对照）| 4.9962 | 1651.3 | _待测_ | 196 | _待测_ |
| 336/16 | 3e-3 | 🔄 运行中 | _待补_ | _待补_ | _待补_ | 441 | _待补_ |
| 448/16 | 3e-3 | ⏳ 排队 | | | | 784 | |
| 224/14 | 3e-3 | ⏳ 排队 | | | | 256 | |
| 336/14 | 3e-3 | ⏳ 排队 | | | | 576 | |
| 448/14 | 3e-3 | ⏳ 排队 | | | | 1024 | |

> 预期判读：若 lr=3e-3 下六格 loss 出现 v形分化（而非 Round 1 的 4.9962 全同平台），即证明 Round 1 那张全同表实为 LR 伪影；坍缩对照 `(224,16)@1e-3=4.9962` 提供**显式对照证据**。

---

## R2-2 目标函数消融（可通约指标 @ lr=3e-3）—— 待运行

> 2 臂 SigLIP / CLIP InfoNCE @ lr=3e-3 × 3000 步。**主指标 = eval5k 检索 R@1/5/10**（跨目标可通约）；loss 并列但标注「不可跨目标比较」。

| 目标 | 状态 | loss@3000 | train img/s | eval5k R@1/5/10 |
|:---|:---|:---|:---|:---|
| SigLIP | ✅ 复用 S8 lr3e-3 | 4.4562 | 1645.1 | _待补_ |
| CLIP InfoNCE | ⏳ 待跑 | | | |

---

## R2-3 架构 × 分辨率矩阵（patch=14，@ lr=3e-3）—— 待运行

> 12 组 = 4 架构 × 3 分辨率（224/14=256、336/14=576、448/14=1024 token），@ lr=3e-3 × 3000 步。
> 每组记录：loss、train img/s、推理 ms/img（batch=1 与 batch=8）、tokens/img、R@1。
> 局判读：若 256→1024 token 区间四架构仍不可区分 → 「架构 loss 不可区分」结论跨 token 预算稳健；若分化 → 找到真实架构结论。

| 架构 | 224/14 | 336/14 | 448/14 |
|:---|:---|:---|:---|
| OpenVision2 | ⏳ | ⏳ | ⏳ |
| DeepEncoderV2 | ⏳ | ⏳ | ⏳ |
| MoE-ViE | ⏳ | ⏳ | ⏳ |
| MambaEye | ⏳ | ⏳ | ⏳ |

---

## R2-4 干净吞吐复测（消除共享集群争用 caveat）—— 待运行

> 4 架构 × 锚点配置（224/16），≥300 步稳态 img/s + 推理 ms/img。
> GPU 独占核验 + NFS 并发核验原文记入报告。

| 核验项 | 结果 |
|:---|:---|
| GPU 0–5 独占 | 核验时刻（10:51）`nvidia-smi` 显示 GPU0-5 = 0 MiB / 0%（仅 GPU6-7 被他人 sglang 占 72GB） |
| NFS 并发 | pretrain 任务（10.239.2.29）已 converged/stopped（04:03 kill 了 loop），无训练在跑 |

| 架构 | 稳态 img/s | 推理 ms/img(bs=1) |
|:---|:---|:---|
| OpenVision2 | 待补 | 待补 |
| DeepEncoderV2 | | |
| MoE-ViE | | |
| MambaEye | | |

---

## R2-5 MambaEye batch=1 停摆诊断（时间盒 40min）—— 待运行

> 二分 batch∈{1,2,4,8} 找停摆阈值；查 mamba_ssm 版本 / selective_scan kernel。

---

## 论文表格回填建议（最终，待 R2 结果齐后补全）

- `tab:visarch`：**Loss@5k 四值核对无误，无需改**；唯一建议核实 `6.51ms`（见 R2-0 / R2-4）。
- `tab:visres`：用 R2-1 的 lr=3e-3 真实值替换（**补 R2-1 结果后填**）。
- `tab:visobj`：用 R2-2 的 R@1/5/10 主指标替换（**补 R2-2 结果后填**）。

---
## 可复现命令（R2 全局）

```bash
conda activate py310   # 或直接用 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
# R2 主 pipeline（R2-1→R2-4→R2-2→R2-3→R2-5 串行，日志 /tmp/vision_r2.log）
bash run_r2.sh
# 单点复现示例（分辨率/patch 消融之一）：
bash run_train.sh openvision2 3000 <out> --data '/nas_train/app.e0031982/datasets/baize-vision/en500k/*.tar' \
    --batch-size 32 --log-every 50 --resolution 336 --patch 16 --lr 3e-3
```