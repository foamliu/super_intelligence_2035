# VISION_OFFICIAL_REPOS_SURVEY.md — R14 官方仓库调研

> 目的：在 R10-③ denseM 训练等待窗口，对官方可比仓库做 CPU-only 源码普查，
> 逐仓库产出 ① 目标函数 ② 数据 pipeline ③ config/超参 ④ 与我们 `vision/models.py` 的结构差异
> ⑤ 可复用资产 ⑥ LICENSE ⑦「能直接抄 / 要改 / 成本」三清单。
>
> 纪律：每条结论贴 `路径:行号`；不许猜；拿不到的明确写「不在仓库中，见论文」。

最后更新：2026-10-03（第二阶段：全部核毕 —— OpenVision2 权重 ✅ 含 decoder、FastVLM ✅、MambaEye ✅、MoE-ViE ✅、iGVLM/TuringViT 🚫 未找到官方实现）

---

## 0. 阶段小结

| 仓库 | 优先级 | 状态 | 关键结论一句话 |
|:---|:---|:---|:---|
| **OpenVision**（UCSC-VLAA） | ⭐⭐⭐ | ✅ 源码普查完成 | JAX/TPU 全开源训练栈；文本用 **BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35 掩码**，与我们的「CLIP-77 + 短 caption + 纯对比」**目标函数完全不同** |
| **ml-aim**（apple-aiml-research / AIMv2） | ⭐⭐⭐ | ✅ 源码普查完成 | 仓库只含**模型接口**（无训练/损失/数据代码）；LICENSE 是 **Apple Sample Code License**，**不可抄代码进我们仓库** |
| OpenVision2 权重 | ⭐⭐ | ✅ 已核 | **真带 caption decoder**（`caption_decoder.safetensors`）；官方 L/14=w1024/d24/**patch14**，⚠️ 我们=patch16/d30 |
| FastVLM | ⭐⭐ | ✅ 已核 | LLaVA 内 FastViTHD（1024² conv-hybrid RepMixer）；LICENSE=Apple Sample Code（research-only） |
| MambaEye | ⭐ | ✅ 存在（MIT） | usingcolor/MambaEye：纯 Mamba2、**小模型监督分类**（非对比） |
| MoE-ViE | ⭐ | ✅ 存在（CC BY-NC 4.0） | facebookresearch/moe_vie：CLIP 风格 MoE-ViT，官方权重 HF |
| iGVLM / TuringViT | ⭐ | 🚫 未找到官方实现 | iGVLM 同名 IG-VLM 是视频QA（非目标）；TuringViT 仅项目主页 |

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

## 3. OpenVision2 权重核实（HF） ⭐⭐

- ✅ **确实已放出**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only` 共 7 个（`library_name=open_clip`，`pipeline_tag=image-to-text`，`tags=[open_clip,openvision2]`）。
- ✅ **真带 caption decoder 权重**（README 原话："the encoder files are unchanged; only the decoder (and this card) were added"）：
  `openvision2-vit-large-patch14-224-vision-only` 的 files：`open_clip_pytorch_model.bin`（视觉塔）+ **`caption_decoder.safetensors` + `text_decoder_config.json` + `modeling_openvision2_decoder.py`**（生成解码器）+ `bert_base_vocab_bos_eos.txt`（BERT wordpiece 词表，`[PAD]=0 [bos]=1 [eos]=2`）+ `caption_example.py`。
- 视觉塔 config（`open_clip_config.json`）：`L/14 @224` = width **1024** / layers **24** / heads 64 / patch_size **14** / pool_type=avg / `output_tokens=True` / embed_dim 1024 / `no_ln_pre`。
- 解码器（`text_decoder_config.json`）：**concat / prefix-LM**（**非 CoCa cross-attn**），12 层 / width 768 / 12 heads / mlp 3072 / vocab 32000 / vision_width 1024；ViT patch token 线性投影后**作为双向前缀 prepend**，文本**因果**生成（`vision` 侧无 text 位置编码）。
- 🔑 **对 R13 的硬约束**：官方权重是 **patch14 / depth 24**，而我们 `vision/models.py:168-170` 的 OpenVision2 塔是 **patch16 / depth 30**（自研改编）→ **官方权重无法直接 load 进我们的塔**（patch embedding 尺度和深度都不匹配）；要跑「官方 vs 自研」对照必须**用官方 patch14/d24 结构另建塔**（或改写 patch/深度）。
- ⑥ LICENSE：README tags 标 `license:apache-2.0`（weights 与 OpenVision 代码同 Apache-2.0）。
- ⑦ 三清单：能直接抄（concat/prefix-LM 解码器结构）；要改（patch14→patch16、depth24→30、open_clip 需打 patched fork `create_vision_encoder_and_transforms`）；成本（若做生成头 / R13 对照，需另建官方结构塔 + 打补丁 open_clip，成本中等）。

## 4. FastVLM / FastViTHD（apple/ml-fastvlm） ⭐⭐

- Clone：`/tmp/fastvlm_survey` @ HEAD `6f7b131`。arXiv 2412.13303（CVPR 2025）。
- 定位：**VLM 的视觉编码器**（非独立对比预训练兽）；训练用 **LLaVA 代码库**（README:26 "use LLaVA codebase to train FastVLM variants"）。
- ②③ 结构：FastViTHD 编码器在 `llava/model/multimodal_encoder/mobileclip/mci.py:1455`（`fastvithd()`）：**5 阶段 hybrid**（`token_mixers = repmixer×3 + attention×2`）、`layers=[2,12,24,4,2]`、`embed_dims=[96,192,384,768,1536]`、mlp_ratio=4；`configs/mobileclip_l.json`：image_size **1024**、embed_dim 3072、patch_size **64**（conv stem + RepMixer conv-FFN + RepCPE）。
- ① 目标：VLM 端到端（LLaVA 风格）；仓库无独立预训练 loss/脚本（`predict.py` 仅推理）。
- ④ 结构差异：官方 FastViTHD 是 **1024² 高分辨率 conv-hybrid**；我们 `vision/models.py:359` 的 FastViTHD 是 **RepMixer conv-FFN 缩到 ~500M 的 224/16 改编**（R8 标「等参改编」）。
- ⑤ 可复用资产：RepMixer / RepCPE / TrainableCPE 结构（`mci.py:1210+`）；官方权重（`get_models.sh` 指向 **Apple CDN**，非 HF）——可作 R13 hybrid 参照标尺。
- ⑥ LICENSE：code = **Apple Sample Code License**（`LICENSE:1-49`，不授专利）；weights = **LICENSE_MODEL research-only 非商用**（`LICENSE_MODEL` 头 + `get_models.sh` 头）→ 🔴 **不可抄进拟开源仓库**。
- ⑦ 三清单：能直接抄（RepMixer conv-FFN 思路）；要改（1024²→224、+对比 readout）；成本（conv-hybrid 对 224/16 几乎无收益，R8 已证）。

## 5. MambaEye（usingcolor/MambaEye，MIT） ⭐

- ✅ **存在**：`https://github.com/usingcolor/MambaEye`（CVPR 2026 Findings，arXiv 2511.19963）。Clone `/tmp/mambaeye`。
- 结构：**纯 Mamba2 因果序列**编码器（README:35 "linear memory/complexity by Mamba2"），尺寸无关、多分辨率/任意宽高比（size-agnostic，`scan.py` 扫描路径 + 位置编码）。
- 训练：PyTorch Lightning + Hydra；**监督 ImageNet 分类**（`train.py model=base_48layers`），**非对比预训练**。
- 权重：HF `usingcolor/MambaEye-{tiny,small,base}[-ft]`；Tiny 5.8M @66.2%、Base 21.3M @73.5%（IN-1k@512，README:74-79）。
- ⑥ LICENSE：**MIT**（`/tmp/mambaeye/LICENSE`）→ ✅ 可抄。
- ⑦ 关键对照：官方 MambaEye 是**小模型（5.8–21.3M）监督分类**且**不冻结 text 塔**；我们 R8 的 mambaeye 是 **534.9M 等参 from-scratch 对比改编** → **协议完全不同**；⚠️ R8「SSM 坍缩」**只对**我们 recipe 成立，不适用官方（C2 限定）。

## 6. MoE-ViE（facebookresearch/moe_vie，CC BY-NC 4.0） ⭐

- ✅ **存在**：`https://github.com/facebookresearch/moe_vie`（ECCV 2026，arXiv 2608.17402）。官方 code release（模型定义 + config + 零样本评测套件）。
- 结构：**CLIP 风格对比预训练 + 细粒度 MoE 视觉 transformer**（自定义 Triton kernel，需 CUDA）。
- 规模/性能（README）：B/16@224 **79.3%**、L/16@384 **83.6%**、H/14@448 **85.1%**（IN-1k top-1）+ retrieval；权重 HF `facebook/MoEViE-*`。
- ⑥ LICENSE：**CC BY-NC 4.0（非商用）**（`LICENSE`）→ 🔴 不可用于商用开源，只可学术对照。
- ⑦ 关键对照：官方 MoE-ViE = **官方对比预训练 + 大模型**；我们 R8 moevie = **505.9M 等参 from-scratch 改编 @3000 步，loss 与 OV2 噪声级不可区分**（R8）→ 无法据此裁决 MoE，需「官方 vs 自研」对照（R13）。

## 7. iGVLM / TuringViT 逐字核实（🚫 均未找到官方实现） ⭐

- **iGVLM（AdaLN 指令/文本条件化，`VISION_ARCH_FRONTIER_2026.md` §1/§3 所指）**：🚫 **未找到对应开源仓库**。GitHub 搜索 `iGVLM` 仅 1 命中 = `doublekwsj/IGVLM`，但那是 **IG-VLM（Image-Grid VLM，零样本视频问答）**，与「指令条件化视觉编码器」**不是同一工作**（无 LICENSE、无 AdaLN 相关代码）。→ 结论：**iGVLM(AdaLN) 官方实现未公开**。
- **TuringViT（小鹏，线性注意力混合 Block）**：🚫 **未找到代码仓库**；仅找到**项目主页** `https://github.com/TuringViT/turingvit.github.io`（github.io，非代码）。→ 结论：**官方代码未公开**。且按 R12 裁定，TuringViT 对本线价值低（attention 仅占 0.7%、224/16 只有 256 token，O(n²) 不痛）。
- 📌 附（OpenVision 代码 config，`openvision2.py:237-239`）：`loss_use_global_batch=True`、`local_loss=True`、`cpu_unit8=True`；MM1.5 / SPACL 仍**未核实**（不在 R14 五仓清单内，留待后续）。

## 8. 阶段小结（R14 全部完成）

| 仓库 | 优先级 | LICENSE | 对我们价值 |
|:--|:--|:--|:--|
| OpenVision | ⭐⭐⭐ | Apache-2.0 | 目标函数/解码器/损失可抄（JAX→PyTorch 要改） |
| OpenVision2 权重 | ⭐⭐ | Apache-2.0 | ✅ 含 decoder；R13 对照需建官方 patch14/d24 塔 |
| ml-aim / AIMv2 | ⭐⭐⭐ | Apple Sample Code | 官方权重作 baseline 标尺（不可抄代码） |
| FastVLM | ⭐⭐ | Apple Sample Code（research-only） | hybrid 无 224/16 收益 |
| MambaEye | ⭐ | MIT | 官方=小模型监督分类，协议不同 |
| MoE-ViE | ⭐ | CC BY-NC 4.0 | 官方权重作 R13 参照 |
| iGVLM(AdaLN) | ⭐ | — | 🚫 未找到（同名 IG-VLM 是视频QA） |
| TuringViT | ⭐ | — | 🚫 仅项目主页；价值低（O(n²) 不痛） |