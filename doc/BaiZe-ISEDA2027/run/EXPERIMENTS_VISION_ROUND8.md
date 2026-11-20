# EXPERIMENTS_VISION_ROUND8.md — 6 架构对比 + ImageNet-1k 指标

> 日期：2026-10-02 · 数据裁定（R7）= **Stanford GPIC `short`** · **已完成**（`/tmp/r8.log` → `R8 ALL DONE 2026-10-02 04:23:25`）。

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

## §4 6 架构结果表（**完整回填 @04:23，R8 全结束**）

| 架构 | loss@3k | 训练 img/s | C1 | C2_gap | fused? | IN-1k zs top1 | IN-1k zs top5 | IN-1k lp top1 |
|:--|--:|--:|--:|--:|:--:|--:|--:|--:|
| **openvision2** | **4.8646** | 3051.8 | **0.2875** | +0.0867 | 否 | **0.0095** | **0.0364** | **0.0114** |
| mambaeye | 6.2507* | 949.5 | **1.0000** | **0.0000** | ✅熔断@300 | 0.0010 | 0.0050 | 0.0010 |
| moevie | 5.5580 | 1225.7 | 0.4109 | +0.0518 | 否 | 0.0035 | 0.0153 | 0.0028 |
| deepencoder_v2 | 6.2513* | 1864.5 | **1.0000** | **0.0000** | ✅熔断@300 | 0.0010 | 0.0050 | 0.0010 |
| aimv2 | 5.6370 | **3392.5** | 0.3931 | +0.0500 | 否 | 0.0038 | 0.0161 | 0.0025 |
| fastvithd | 5.6683 | 2097.4 | 0.4494 | +0.0369 | 否 | 0.0039 | 0.0157 | 0.0027 |

> *6.25 ≈ ln(512)=6.238 = InfoNCE「无学习」熵平台，非正常收敛值。IN-1k chance = 1/1000 = 0.0010（0.10%）；**坍缩架构 = 精确 chance（0.0010）**，健康架构 2.5–9.5× chance。
> 🔑 **两个含 SSM 的架构（mambaeye 纯 SSM、deepencoder_v2 Attn+SSM 混合）都在 @300 熔断**（C1=1.0000、loss 卡 6.25 平台、IN-1k=精确 chance），纯 Attention 系 4 架构（openvision2/moevie/aimv2/fastvithd）健康。
> 🏆 **胜出 = OpenVision2**：loss（4.8646 最低）、C1（0.2875 最分散）、IN-1k zs（0.95%）、IN-1k lp（1.14%）四指标全第一。

## §7 🔑 六架构结果与「SSM 特异坍缩」发现（2026-10-02 03:41 巡检）

**openvision2（纯 Attention）—— 健康（C1–C4 全过）：**
- C1 轨迹 0.2295→0.2483→0.2738→0.2847→0.2775→0.2875（@1500..3000，缓升、远 <0.9）；C2_gap 全程 +0.0827~+0.0990；C4=OK（loss 5.9195→4.8646）。
- `[done] total=709.7s steps=3000 steady_image_s=3051.8 final_loss=4.8646 fused=False` → `vision.pt`（2.02GB）。

**mambaeye（纯 SSM，Vim 双向）—— @step300 坍缩，熔断器正确触发：**
```text
[PROBE step 300] C1=1.0000 C2_diag=0.3115 C2_off=0.3115 C2_gap=+0.0000 loss_ema=6.2507 ... C4=FAIL
[done] total=172.5s steps=300 steady_image_s=949.5 final_loss=6.2507 fused=True
===== R8 mambaeye done (exit 1) 2026-10-02 02:52:44 =====
```

**deepencoder_v2（Attn+SSM 混合 AAMM）—— @step300 同样坍缩（★本轮新增证据）：**
```text
[step 300/3000] loss=6.2543 ...
[PROBE step 300] C1=1.0000 C2_diag=0.3138 C2_off=0.3138 C2_gap=-0.0000 loss_ema=6.2513 loss_early=6.2691 C4=OK→熔断
[done] total=105.0s steps=300 steady_image_s=1864.5 final_loss=6.2513 fused=True
===== R8 deepencoder_v2 done (exit 1) 2026-10-02 03:31:27 =====
```
- mambaeye 与 deepencoder_v2 的 loss 都**精确卡在 6.25 ≈ ln(512)=6.238「无学习」熵平台**，C1 同时精确 1.0000；exit 1 的 SIGABRT/NCCL-ALLGATHER 600s 超时是熔断后 DDP 收尾副产物（第 300 步已正常判熔断并写出 `vision_fused.pt`）。

**moevie（Attention + MoE-FFN）—— 健康（exit 0，不复现坍缩）：**
- C1 轨迹（**震荡、非单调**）：0.192@300→0.273@600→0.439@900→0.486@1200→0.388@1500→0.366@1800→0.352@2100→0.271@2400→0.329@2700→0.411@3000。
- `[done] total=1492.8s steps=3000 steady_image_s=1225.7 final_loss=5.5580 fused=False`；C2_gap +0.036~+0.079 恒正；loss 6.03→5.56。
- ⚠️ 修正 03:05 巡检「C1 上升偏快」的过虑：C1 实为震荡（峰 0.4864@1200 后回落 0.27@2400），非单调坍缩，全程 <0.5。

**aimv2（ViT-GELU，纯 Attention 系）—— 健康（exit 0，不复现坍缩）：**
- C1 轨迹（震荡）：0.235@300→0.242@600→0.360@900→0.380@1200→0.296@1500→0.409@1800→0.350@2100→0.417@2400→0.448@2700→0.393@3000。
- `[done] total=655.1s steps=3000 steady_image_s=3392.5 final_loss=5.6370 fused=False`；C2_gap +0.050~+0.118 恒正；loss 6.02→5.64。✅
- ⚠️ 注：aimv2 训练吞吐 **3392.5 img/s 为 6 架构最快**（openvision2 3051.8 / deepencoder 1864.5 / moevie 1225.7 / mambaeye 949.5），但 loss 5.6370 差于 openvision2 4.8646。

**fastvithd（conv-stem + 分层 conv/attention hybrid）—— 健康（exit 0，不坍缩）：**
- C1 轨迹（震荡，峰值偏高）：0.228@300→0.272@600→0.299@900→0.572@1200→0.352@1500→0.386@1800→0.363@2100→**0.674@2400**→0.424@2700→0.449@3000。
- `[done] total=1007.9s steps=3000 steady_image_s=2097.4 final_loss=5.6683 fused=False`；C2_gap +0.093→+0.037 恒正但逐步收窄；loss 5.63→5.67。
- ⚠️ 注：C1 全程 <0.9 未熔断，但**震荡幅度大**（峰 0.674@2400，与 openvision2 的 0.2875 单峰缓升形成对比）；loss 5.6683 为 4 个健康架构中最差，IN-1k 0.39% 与 aimv2/moevie 同档。conv-stem hybrid（507.77M）在 500–600M 等参下**未带来优势**（不比纯 Attention ViT 好）。

**🔑 坍缩是「SSM 特异」的（本轮最重要的发现，比 03:05 的「架构特异」更精确）：**
- 同一 recipe（冻结 CLIP-768 文本塔 + InfoNCE + GPIC short + bs64=512 负样本 + lr 3e-3 + seed 1234）下：
  - **含 SSM 的两个架构（mambaeye 纯 SSM、deepencoder_v2 Attn+SSM 混合）都在 @300 坍缩（C1=1.0000、loss=6.25≈ln512）**；
  - **纯 Attention 系的三个架构（openvision2 / moevie / aimv2）都不坍缩**。
- 文本塔 / 数据 / 目标函数 / 随机种子完全相同，唯一变量是 vision 架构 → **坍缩倾向由 SSM 子结构决定**。
- 对 R4 结论的修正：R4 把坍缩主因归到「随机文本塔」（S5：随机塔 offdiag 0.7258）并判定「修好文本塔即解决」→ R8 显示该判定**不完整**：配了冻结预训练文本塔后，SSM 塔仍坍缩、Attention 塔不坍缩。
- ⚠️ 边界说明（如实书写，不掩盖）：mambaeye 在 R1（SigLIP + 随机文本塔 + en500k）曾能训练（S3 loss 6.73→4.64），故坍缩**依赖 recipe/目标函数/数据的组合**，未必是 SSM 结构的绝对缺陷；但「当前修复 recipe 下含 SSM 架构坍缩」是确定的实测事实，按任务铁律如实记录、不重试到「看起来好」为止。 |

## §8 最终结论与 6 架构排名（2026-10-02 04:23 R8 全结束）

**训练 + IN-1k 评测全部完成**（`/tmp/r8.log` → `R8 ALL DONE 2026-10-02 04:23:25`）。完整表见 §4。

**胜出架构：OpenVision2（四指标全第一；R5/R7 判胜被 R8 强化确认，AIMv2/FastViTHD 未翻盘）**

| 排名 | 架构 | loss@3k | C1 | IN-1k zs | IN-1k lp | 吞吐 img/s | 判定 |
|:--|:--|--:|--:|--:|--:|--:|:--|
| **1** | **openvision2** | **4.8646** | **0.2875** | **0.95%** | **1.14%** | 3051.8 | ✅ 胜出（loss/C1/IN-1k 全第一） |
| 2 | moevie | 5.5580 | 0.4109 | 0.35% | 0.28% | 1225.7 | ✅ 健康（Attention+MoE-FFN，激活 222M） |
| 3 | aimv2 | 5.6370 | 0.3931 | 0.38% | 0.25% | **3392.5** | ✅ 健康（ViT-GELU，吞吐最快） |
| 4 | fastvithd | 5.6683 | 0.4494 | 0.39% | 0.27% | 2097.4 | ✅ 健康（conv-hybrid，C1 震荡偏大） |
| — | mambaeye | 6.2507* | 1.0000 | 0.10% | 0.10% | 949.5 | ❌ @300 坍缩（纯 SSM） |
| — | deepencoder_v2 | 6.2513* | 1.0000 | 0.10% | 0.10% | 1864.5 | ❌ @300 坍缩（Attn+SSM 混合） |

**三条结论（可写进论文 finding）**：
1. **架构有真实差异，胜出者稳定**：修复 recipe 下 4 个健康架构 loss 可分（4.8646~5.6683），新指标 IN-1k 也可分（openvision2 0.95%/1.14% vs 其余 0.35–0.39%/0.25–0.28%），OpenVision2 全指标第一 → **替换** R1/R2 因坍缩失效的「loss 与架构无关」结论。
2. **坍缩是「SSM 特异」**：含 SSM 子结构的两架构（纯 SSM / Attn+SSM 混合）都在 @300 坍缩（C1=1.0000、loss=6.25≈ln512、IN-1k=精确 chance 0.10%），纯 Attention 系 4 架构（含 MoE-FFN / GELU / conv-hybrid）全不坍缩 → 对 R4「随机文本塔是主因」的修正（详见 §7）。
3. **IN-1k 替换 R@1 成功**：R@1 在 R2/R3 退化为精确 1/5000 chance、零区分度；IN-1k（frozen trunk zs/lp）有区分度（0.10%~0.95%），可作为 Stage(iii) 主指标。

**官方预训练参考表（R8.4 交付物 · ✅ 2026-10-02 补完：以「盘上权重 + 已发表文献值」作锚点；协议不同，单独表，绝不并入 from-scratch 排名）**：

- 🔵 **勘误（2026-10-02 复核）**：前记「官方权重未在本机缓存」**不准确**——AIMv2-1B 官方权重**已在盘上**（本地共享模型目录，非 HF hub 缓存）：
  - `/nas_train/app.e0031982/models/apple/aimv2-1B-patch14-336/`（14G，完整 `model.safetensors` + `config.json` + `modeling_aimv2.py`）
  - `/nas_train/app.e0031982/models/apple/aimv2-1B-patch14-448/`（14G，同上）
  - FastViT：`timm/fastvit_ma36.apple_in1k`（HF 有此 pretrained tag，44.1M，按需下载 ~160MB）

| 参考模型（官方预训练） | 协议 | IN-1k top-1 | 参数 | 证据出处 |
|:--|:--|--:|--:|:--|
| **AIMv2-1B-patch14-336** | 多模态自回归预训练（frozen trunk 线性分类） | **88.7%** | 1B | 盘上 README `model-index`（`imagenet-1k` accuracy 88.7，`verified:false`） |
| **AIMv2-1B-patch14-448** | 同上 | **89.0%** | 1B | 盘上 README `model-index` |
| **AIMv2-3B** | 同上 | **89.5%（frozen trunk）** | 3B | 盘上 README 引言原文 |
| **FastViT-MA36**（`apple_in1k`） | IN-1k **监督**分类（Apple 训练，256px） | ≈83.6%（FastViT 论文值，本机未重测） | **44.1M** | HF 模型卡（44.1M / 256×256 / GMACs 7.8）+ arXiv:2303.14189 |
| _（对照）OpenVision2（本项目，从零 505M）_ | InfoNCE 对比 3000 步，frozen-trunk linear-probe | **1.14%** | 505M | §4 实测 |

- 📌 **诚实锚点（论文可写）**：从零 + 3000 步 + GPIC-short 的对比学习，IN-1k linear-probe 仅 **1.14%**；官方预训练（自回归/监督、数十亿 token）达 **88–89%**。二者差 **~78–88 个百分点**，非同一量级 → 客观佐证「当前 recipe 的从零训练远未产出可用视觉表示」，与 §7 的坍缩归因自洽；官方权重只作「上界锚点」，不并表排名。
- ⚠️ **本机未重测的原因（如实）**：① AIMv2 盘上 `model.safetensors` 的 state_dict 命名（`embeddings.patch_embed` / `encoder.layers.N.attention.q_proj`，SigLIP2/native 风格）与捆绑 `modeling_aimv2.py` 类名（`preprocessor.patchifier.proj` / `trunk.blocks.N.attn.qkv`）**不一致** → 需 key-remap 适配，且 14G 加载 >30s（实测 load test 超时）；② FastViT 需 256px 独立管线。二者皆「工程适配」非「科学问题」→ 用**已发表文献值**作锚点完成本表，避免为可选表再烧 GPU/工时。

## §9 论文回填建议（`tab:visarch` / `tab:visres` / `tab:visobj`；🚫 本任务不改 tex）

- **`tab:visarch`（架构对比）**：整表重写（R1/R2 旧值全系坍缩读数已作废）。建议列：6 架构 × (numel、loss@3k、训练 img/s、C1、IN-1k zs/lp top-1、判定)，用本节 §4/§8 数值；OpenVision2 为胜出。AIMv2/FastViTHD 为「等参 500–600M 放大版」（非官方模型，标注 from-scratch/等参改编），官方权重参考值单独一行或单表、标「协议不同」。
- **`tab:visres`（分辨率/patch）**：沿用 R5 P1 结论（胜出架构 OpenVision2：224/16 最佳 loss 3.0977/1361.7 img/s；336/14 3.1909；448/14 3.2711）。R2 坍缩读数已作废。
- **`tab:visobj`（目标函数/数据）**：沿用 R4（SigLIP/InfoNCE A/B + 冻结 CLIP-768 文本塔）+ R7（数据臂 en500k vs GPIC-short vs CC12M，裁定 GPIC short），用本节 IN-1k 作为跨臂可通约主指标。
- **数据来源段**：正式训练数据 = **Stanford GPIC `short`**（20 tok / 0% 截断 / off-diag 0.245 最分散 / permissive 许可），技术路线依据 R6.1 + R7。en500k（LLaVA imagenet/EN）为对照臂且标「与 IN-1k 同域、in-domain 污染不可比」。
- **context length**：冻结 `clip-vit-large-patch14-336` text tower（768 维，context 77，max_position_embeddings=77，>77 抛 ValueError），R6.3 裁定保持 77（GPIC short 0% 截断，77 非瓶颈）。
- **坍缩写法**：把「SSM 特异坍缩」写成 finding（含 SSM 架构在当前对比 recipe 下 @300 坍缩、纯 Attention 系健康），不用「loss 与架构无关」旧表述。

## §5 代码产物

- `vision/models.py`：新增 `AIMv2`（ViT-GELU）与 `FastViTHD`（conv-stem 分层 hybrid），均注册进 `get_vision_tower()`；修 FastViTHD 分层下采样（OOM 修复）+ 删除死 `self.norm`。
- `vision/r8_run.sh`：6 架构 × 3000 步（复用 `r7_train.py --tower`，GPIC short）串行 → 末了自动跑 IN-1k 评测。
- `vision/r8_eval_in1k.py`：zero-shot + linear-probe（自切 val 50/类，一次解码复用 6 ckpt）。

## §6 冒烟验证（2026-10-02）

- 6 架构 forward+backward：全过，none param 无梯度（0 死参）。
- `fastvithd` 8 卡 DDP 冒烟 3 步 exit 0：loss 6.30、`[saved] vision_fused.pt`（C1 熔断是 3 步冒烟的预期，非 bug）。
- `r8_eval_in1k.py` 端到端冒烟（R7_B_gpic ckpt、per-class=1）：zero-shot top1=0.0100 / top5=0.0460 / lp=0.0040，管线跑通（3000 步从零模型 1% zs top1 = 10× chance，意义正常）。