# VISION_OFFICIAL_REPOS_SURVEY.md — R14 官方仓库调研

> 目的：在 R10-③ denseM 训练等待窗口，对官方可比仓库做 CPU-only 源码普查，
> 逐仓库产出 ① 目标函数 ② 数据 pipeline ③ config/超参 ④ 与我们 `vision/models.py` 的结构差异
> ⑤ 可复用资产 ⑥ LICENSE ⑦「能直接抄 / 要改 / 成本」三清单。
>
> 纪律：每条结论贴 `路径:行号`；不许猜；拿不到的明确写「不在仓库中，见论文」。

最后更新：2026-10-03（第一阶段：两个 ⭐⭐⭐ 仓库已完成源码级普查）

---

## 0. 阶段小结

| 仓库 | 优先级 | 状态 | 关键结论一句话 |
|:---|:---|:---|:---|
| **OpenVision**（UCSC-VLAA） | ⭐⭐⭐ | ✅ 源码普查完成 | JAX/TPU 全开源训练栈；文本用 **BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35 掩码**，与我们的「CLIP-77 + 短 caption + 纯对比」**目标函数完全不同** |
| **ml-aim**（apple-aiml-research / AIMv2） | ⭐⭐⭐ | ✅ 源码普查完成 | 仓库只含**模型接口**（无训练/损失/数据代码）；LICENSE 是 **Apple Sample Code License**，**不可抄代码进我们仓库** |
| OpenVision2 权重是否真开源 | ⭐⭐ | ⏳ 待办 | 需核 HF/release 页（下轮） |
| FastVLM | ⭐⭐ | ⏳ 待办 | 下轮 |
| MambaEye / MoE-ViE / iGVLM / TuringViT 等疑似不存在 | ⭐ | ⏳ 待办 | 下轮逐字核实 |

---

## 1. OpenVision（UCSC-VLAA/OpenVision） ⭐⭐⭐

- Clone：`/tmp/ov_survey` @ HEAD `c3f7d96`（JAX/TPU，**big_vision 派生**）。
- 训练入口：`src/main_openvision2.py`；config：`src/configs/openvision2.py`。
- 关键组件：`src/losses/common.py`、`src/models/{vit,text_decoder,text_decoder_v2,text_transformer,two_towers}.py`、
  `src/datasets/input_pipeline.py`、`src/convert_upload/transfer_jax2hf.py`（JAX→HF 转换）。

### 1.1 ① 目标函数（`src/losses/common.py`）

官方 loss 模块同时提供 4 个损失，**训练主目标 = 双向对比 + caption 自回归生成**（另备 MAE 重建）：

| 函数 | 位置 | 语义 |
|:---|:---|:---|
| `sigmoid_xent` | `common.py:40` | SigLIP 风格双向 sigmoid 对比 |
| `bidirectional_contrastive_loss` | `common.py:50` | CLIP InfoNCE 双向 softmax（global/siglip/FLIP-efficient 三实现） |
| `weighted_softmax_xent` | `common.py:281` | caption 自回归 CE（label_smoothing / normalize 可选） |
| `mae_loss` | `common.py:327` | 像素重建（norm_pix_loss=True） |

- caption 生成权重：`openvision2.py:236` → `config.coca_caption_loss_weight = 2`（生成是主目标之一）。
### 1.2 ② 数据 pipeline（`openvision2.py:120-162`）

- 数据集占位：`config.input.data = {name='datacomp1b', split='full', data_dir='gs://…'}`（`openvision2.py:122-126`）；
  shuffle buffer 250k（`:128`）。
- **文本侧（与我们的最大差异点）**：
  - tokenizer：**BERT**，词表 `assets/bert_base_vocab_bos_eos.txt`，`add_bos=True, add_eos=True`（`openvision2.py:135-142`）。
  - `config.input.txt_token_length = arg.token_len`（默认 **128**，非 77）（`openvision2.py:129`）。
  - **`txt_key='llava_llama3_condition_True_dense_weighted_topk'`**（`openvision2.py:46`）→ caption 来自
    **LLaVA 指令 + LLaMA3 生成的 dense weighted（ReCap 式）长 caption**，不是简单 alt-text。
  - `get_autoreg_label(pad_token=0)` 生成 `autoreg_labels` + `cap_loss_mask`（`:144-147`）→ 只对 caption 词监督。
  - 可选 `use_openclip_tokenizer=True` 分支（默认 False，`:47`）。
- **图片侧**：`inception_crop(area_min=40)` + `simclr_jitter_gray(0.4)`（`:150-159`）。

### 1.3 ③ config / 超参（`openvision2.py:32-62`）

- 核心 arg：`res=112`（usage 例 84）、`token_len=128`、`keep_ratio=0.35`、`img='L/16'`、
  `txt_decoder_name='L'`【**DECODER_NAME**】、`vocab_size=32000`、`remat='full'`、`img_head=True`。
- 模型（`openvision2.py:170-192`）：
  - `image`：vit `L/16`，`posemb='sincos2d'`，`pool_type='gap'`，`output_tokens=True`；
    宽度表 `L:1024`（`openvision2.py:194-198`）。
  - `text_decoder`：`text_decoder_v2`，`variant=arg.txt_decoder_name`（L），`vocab_size=32000`，
    `fusion_style='concat'`，`casual_mask=True`，`remat_policy='none'`（`:172-179`）。
- 优化/调度（`openvision2.py:200-231`）：`scale_by_adam`（AdamW），`b1=0.9 b2=0.95`，**`wd=0.2`**，
  cosine 调度 `min_lr=0`，`base_lr=8e-6 × 64 × batch_factor`（随 global batch 线性放大）；
  `batch_size = 1024*16*batch_factor`（默认 gbs≈16k，`:208`）。
- Eval：ImageNet 零样本分类、COCO / Flickr30k retrieval（`openvision2.py:267-310`）。

### 1.4 ④ 结构差异 vs 我们 `vision/models.py`

| 维度 | 官方 OpenVision2 | 我们 BaiZe 实现 | 证据 |
|:---|:---|:---|:---|
| 塔宽/深/头/mlp | ViT-L/16：w**1024**/d**24**/h16/m4096（≈304M） | OpenVision2：w1024/d**30**/h16/m4096（≈505M） | 官方 `vit.py:829-832`；我们 `vision/models.py:168-177` |
| readout 头 | caption decoder 直出 vocab logits | `ReadoutHead(width→EMBED_DIM=512)` 对比 | 官方 `text_decoder_v2.py:437-447`；我们 `models.py:16,157-160` |
| 文本塔 | BERT-128 + LLaMA3 dense caption | 我们冻结 CLIP-768、context 77、短 caption | 官方 `openvision2.py:46,129`；我们 recipe |
| 图像掩码 | `keep_ratio=0.35` 随机块掩码（`vit.py:465+`） | 无 | 官方 `openvision2.py:49,200` |
| head 语义 | patch / caption 生成 | 纯对比 readout | — |

一句话：官方 OpenVision2 =「多头图像掩码 + LLaVA/LLaMA3 长 caption + 生成解码器」的多任务生成式框架；
我们 =「CLIP 式纯对比 + 短 caption」判别式框架。**目标函数与监督信号都不同**。

### 1.5 ⑤ 可复用资产

- `src/losses/common.py`：`sigmoid_xent` / InfoNCE / caption CE / `mae_loss` 的 JAX 稳定实现（可对照转 PyTorch）。
- `src/models/text_decoder_v2.py`：cross-attn caption decoder（`fusion_style='concat'/'cross_attn'`）可作未来生成头参考。
- `src/models/vit.py:465+`：`keep_ratio` 块级随机掩码生成（可作图像重建任务参考）。
- `src/convert_upload/transfer_jax2hf.py`：JAX→HF 权重转换脚本（未来灌官方权重到我们 torch 塔）。

### 1.6 ⑥ LICENSE

- 每文件头 **Apache-2.0**，声明基于 `google-research/big_vision`（`losses/common.py:1-14`）。✅ 可照抄/改（保留 NOTICE）。

### 1.7 ⑦ 三清单

- **能直接抄**：`bidirectional_contrastive_loss` 数值稳定写法；caption CE 的 `label_smoothing/normalize` 写法。
- **要改**：BERT-128→CLIP-77 tokenizer 对齐；JAX/flax→PyTorch；`datacomp1b` GCS 占位→我们本地 CC12M+Amshaker。
- **成本**：若照搬「LLaMA3 dense caption + 生成解码器」目标函数，需① 重新生成长 caption（LLaVA+LLaMA3 推理）② 新写 caption decoder ③ 数据/损失/评测全套改动 → 属**目标函数大改**，非架构微调。
---

## 2. ml-aim（apple-aiml-research / AIMv2） ⭐⭐⭐

- Clone：`/tmp/mlaim_survey` @ HEAD `a018ae32`。论文 arXiv:2411.14402（CVPR 2025 Highlight）。
- 仓库定位（README:9）：AIM 系列入口；`aim-v2/` 子包只**打包模型**，不含训练。

### 2.1 ① 目标函数

- README:27-33：AIMv2 = "multimodal autoregressive objective"（多模态自回归预训练）；AIMv2-3B **89.5% ImageNet frozen trunk**。
- **代码侧只到模型前向**，无损失/训练代码：
  - `aim/v2/mixins.py:11-42`：`AIMv2VisionMixin.forward = preprocessor → trunk(x, mask) → head(x)`；
    `AIMv2TextMixin` 同构（`:28-42`），text 侧带 `eos_token_mask`。
  - 三个 backend：`aim/v2/{torch,jax,mlx}/models.py` + `layers.py`（纯模型实现，无 loss / optimizer / dataloader）。
- **patch+text AR 的具体损失 / 采样 / 掩码率 不在仓库中**，只能读论文 §方法。

### 2.2 ② 数据 pipeline

- **不在仓库中**（无 dataset / 训练脚本 / yaml）。数据结论只能取自论文（论文报告大数据集池）。

### 2.3 ③ config / 超参

- 仓库无训练 config/hp。可见的是模型画廊 + 权重（README:38-52, 141-222）：
  - 系列：`aimv2-{large,huge,1B,3B}-patch14-{224,336,448}` + native-res + distilled ViT-L + zero-shot adapted。
  - 例：`aimv2-large-patch14-336` frozen trunk **87.6%**（README:199）。
  - 权重：HF `apple/aimv2-*`（`model.safetensors` + torch/mlx/jax backend；README:79-135）。

### 2.4 ④ 结构差异 vs 我们 `vision/models.py`

- 我们 `vision/models.py:293-303` `AIMv2` 塔（`VitGeluBlock`）：w1024/d**40**/h16/m4096、**GELU 4x MLP（非 SwiGLU）**，
  注释明确 "official GELU 4x MLP (NOT SwiGLU), keeping width/heads at AIMv2-L values"。
- 官方 AIMv2 trunk 的 head 输出 **patch prediction logits**（`head(x)` 在 `AIMv2VisionMixin.forward`）；
  我们 head 是 `ReadoutHead(width→512)` 对比 readout。→ **监督/输出语义不同**（预测 patch vs 对比嵌入）。

### 2.5 ⑤ 可复用资产

- `aim/v2/{torch,jax,mlx}/models.py` 的 trunk + patch-predictor head 结构（可精读对照我们 AIMv2 塔 head 是否该换）。
- `apple/aimv2-large-patch14-*` 官方权重 → 可作我们 AIMv2 塔的 **official baseline 特征质量标尺**（用途按 HF 页面 license 再核）。

### 2.6 ⑥ LICENSE（已逐字读 `/tmp/mlaim_survey/LICENSE`）

- **Apple Sample Code License**，非 Apache/MIT（`LICENSE:1-39`）：
  - 允许 use/reproduce/modify/redistribute（保留 notice、不得用 Apple 名义背书）；
  - **不授予 patent rights**（`LICENSE:22-24`）；AS-IS、无 warranty、无侵权担保（`LICENSE:26-39`）。
  - `LICENSE:42-45`：AIMv2 含第三方 subcomponents，各自 license 见 `ACKNOWLEDGEMENTS`。
- **结论**：可**学术对照 / 跑官方权重**；🔴 **不可把其代码逐字 COPY 进我们（拟开源）仓库**；权重用途按 HF `apple/aimv2-*` 页 license 再核。

### 2.7 ⑦ 三清单

- **能直接抄**：几乎无——它是闭门训练 + 公开模型，无训练损失/数据可抄。
- **要改**：若复现 AR 目标，得照论文从零写 patch+text AR 损失 + 掩码 + 分块，非「改」而是「造」。
- **成本**：复现 AIMv2 目标 = 大改（mask 设计 + 双流 text/patch 自回归 + 大数据）；官方权重可作 baseline 标尺。

---

## 3. ⭐⭐ / ⭐ 待办（下一 cycle）

- [ ] **OpenVision2 权重是否真开源**（HF / release 资产核实 + MD5）—— ⭐⭐。
- [ ] **FastVLM**（图像理解；查独立纬线结果）—— ⭐⭐。
- [ ] **疑似不存在条目逐字核实**：MambaEye、MoE-ViE、iGVLM、TuringViT、MM1.5、SPACL —— ⭐（先确认无此开源仓库，再决定是否从基准表删除）。
- `openvision2.py:237-239`：`loss_use_global_batch=True`、`local_loss=True`、`cpu_unit8=True`。