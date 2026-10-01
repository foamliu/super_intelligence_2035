# EXPERIMENTS_VISION_ROUND8.md — 6 架构对比 + ImageNet-1k 指标

> 日期：2026-10-02 · 数据裁定（R7）= **Stanford GPIC `short`** · 训练中（`/tmp/r8.log`）。

## §0 协议（与 R5 P0 / R7 B_gpic 同口径，只扩架构 + 换指标）

| 项 | 值 |
|:--|:--|
| 架构 | 6 个：openvision2 / mambaeye / moevie / deepencoder_v2 / **aimv2** / **fastvithd**（均等参 500–600M） |
| 数据 | Stanford GPIC `short`（20 tok / 0% 截断，~2.77M 对） |
| 步数 | 3000 步 @224/16, bs64 × 8 卡 = 512 负样本/步 |
| 目标 | InfoNCE，冻结 CLIP-768 text（77 硬约束），lr 3e-3 / warmup 20 / seed 1234 / bf16 |
| 训练中探针 | C1（same-tower 余弦）/ C2（cross diag-off gap）/ C4（loss 下降），熔断阈值同 R5.2 |
| **新指标** | **ImageNet-1k zero-shot top-1/5 + linear-probe top-1**（frozen trunk，替换退化的 R@1） |

**IN-1k 评测协议（frozen trunk，不 finetune）** — 见 `r8_eval_in1k.py`：
- zero-shot：1000 类 × 80 个 open_clip 模板 → 冻结 CLIP-768 text 平均成 1000 类向量，图像特征 L2 归一化后 argmax。
- linear-probe：冻结 trunk 特征上训**单个线性层**（768→1000，AdamW 3e-3 × 100 epoch，full-batch），probe-train 50/类，评 val 50/类。
- 两指标都报（zero-shot 依赖文本塔/77，linear-probe 不依赖）。

## §1 R8.2 污染核查结论（实测，做之前先查——已查）

**盘上 IN-1k 事实（`/nas_train/app.e0031982/datasets/imagenet-1k`）**：
- `train-*.parquet`：1,281,167 张**有标签**图（label 0..999），`image.bytes` 内嵌，尺寸为**原始 ILSVRC**（500×375 / 689×1024 / 74×56 等任意分辨率），文件名如 `n03954731_53652_n03954731.JPEG`。
- `test-*.parquet`：100,000 张，**label=-1（无标签）** → **不能当 val**。
- **无官方 50k val 分片** → 只能自切（见 §2）。

**en500k（R5 臂 A = LLaVA `imagenet/EN`）与 IN-1k 的关系（实测）**：
- en500k 源 parquet（LLaVA-OneVision `imagenet/EN`）`image.path` = **None**（原始 ILSVRC 文件名已丢），打包成 webdataset 时又重键为 `000000000.png`。
- 实测其 `image.bytes` 已被 LLaVA **重缩放**：所有图 min-dim=256（如 (420,256)/(256,321)/(376,256)…），与 IN-1k 的原始 ILSVRC 尺寸完全不同样式。
- → **按文件名 / 按字节 hash 匹配都不可行**（LLaVA 重编码，字节不同）。

**结论（判定 R8.2 规则 3）**：
- en500k = ImageNet train 照片的**重述版**（同域、大概率同图，仅重缩放/重述 caption）。用它测 IN-1k 是 **in-domain / possibly-same-image 污染** → 其 IN-1k 数字须标 **`in-domain（污染，不可比）`**，并从跨域比较剔除。
- GPIC（Flickr 系）与 ImageNet **不同域** → **R8 的 6 架构（GPIC short 训练）测 IN-1k 是干净 out-of-domain**，可并排比较。

## §2 IN-1k 自切协议（因无官方 val，必须固定、可复现）

- **val** = 每个类前 50 张（按 train parquet 文件顺序，deterministic）= 50,000 张。
- **probe-train** = 每个类接下去 50 张 = 50,000 张（线性分类器训练用）。
- 二者与 R8 的 GPIC 训练数据**不同源、不相交**。`r8_eval_in1k.py` 一次解码 100k 图复用给全部 6 个 checkpoint。

## §3 6 架构参数量（2026-10-02 实测 `sum(numel())`，均落 500–600M）

| 架构 | total | active（MoE）| 说明 |
|:--|--:|--:|:--|
| openvision2 | 505.22M | 505.22M | 纯 Attention ViT（depth 30） |
| mambaeye | 535.16M | 535.16M | 纯视觉 SSM（Vim 双向） |
| moevie | 505.46M | 222.22M | Attention + MoE-FFN |
| deepencoder_v2 | 517.19M | 517.19M | Attn+SSM 混合 |
| **aimv2** | 505.46M | 505.46M | AIMv2 风格 ViT-GELU（depth 40） |
| **fastvithd** | **507.77M** | 507.77M | FastViT-HD 风格 conv-stem + 分层 conv/attention（conv 28×28 → down 14×14 → 37 attention） |

> ⚠️ FastViTHD 首次实现把 37 个 attention 块都放 28×28（token 数 = ViT 的 4×），bs64 单卡 80GB **OOM**（实测 78.9GB）。已改为 FastViT 原生**分层**结构（conv 阶段 28×28 → stride-2 下采样 → attention 阶段 14×14），峰值显存降到 ~28GB、参数量 503→508M，仍在范围内。

## §4 6 架构结果表（**训练中，回填后覆盖本节**）

| 架构 | loss@3k | 训练 img/s | C1 | C2_gap | fused? | IN-1k zs top1 | IN-1k zs top5 | IN-1k lp top1 |
|:--|--:|--:|--:|--:|:--:|--:|--:|--:|
| openvision2 | ⏳ | ⏳ | | | | | | |
| mambaeye | ⏳ | ⏳ | | | | | | |
| moevie | ⏳ | ⏳ | | | | | | |
| deepencoder_v2 | ⏳ | ⏳ | | | | | | |
| aimv2 | ⏳ | ⏳ | | | | | | |
| fastvithd | ⏳ | ⏳ | | | | | | |

## §5 代码产物

- `vision/models.py`：新增 `AIMv2`（ViT-GELU）与 `FastViTHD`（conv-stem 分层 hybrid），均注册进 `get_vision_tower()`；修 FastViTHD 分层下采样（OOM 修复）+ 删除死 `self.norm`。
- `vision/r8_run.sh`：6 架构 × 3000 步（复用 `r7_train.py --tower`，GPIC short）串行 → 末了自动跑 IN-1k 评测。
- `vision/r8_eval_in1k.py`：zero-shot + linear-probe（自切 val 50/类，一次解码复用 6 ckpt）。

## §6 冒烟验证（2026-10-02）

- 6 架构 forward+backward：全过，none param 无梯度（0 死参）。
- `fastvithd` 8 卡 DDP 冒烟 3 步 exit 0：loss 6.30、`[saved] vision_fused.pt`（C1 熔断是 3 步冒烟的预期，非 bug）。
- `r8_eval_in1k.py` 端到端冒烟（R7_B_gpic ckpt、per-class=1）：zero-shot top1=0.0100 / top5=0.0460 / lp=0.0040，管线跑通（3000 步从零模型 1% zs top1 = 10× chance，意义正常）。