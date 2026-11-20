# EXPERIMENTS_VISION_ROUND6.md — 文本塔上下文（77）与数据切换的裁定

> **BaiZe Stage(iii) 视觉编码器预训练 · Round 6**（纯 CPU，与 R5 P0 并行，不占卡）
> 目标：R6.1 后续数据是否切 GPIC；R6.2 77 截断根因核实（官方 OpenVision2 config vs open_clip 默认）；R6.3 正式训练时 77 能否变长（技术上 + 该不该）。
> 铁律：**不许猜**，每条结论附证据出处（文件路径+行号 / config 字段 / 命令+输出）。
> 日期：2026-10-01。PHASE=R6_probe（与 R5_active 并存）。

---

## 0. TL;DR 裁定表（三选一，不许"视情况"）

| 问题 | 结论 | 证据出处 |
|:--|:--|:--|
| 后续数据是否切 GPIC | **分阶段切**：R5 P0/P1/P2 保持 en500k（LLaVA 长 recaption，作对照臂，**不中断已跑的 P0**）；**正式训练（Stage(iii) 编码器训练，Stage(iv) 之前）切到 GPIC `short`** | 实测：`/nas_inference/.../gpic/train/*.tar`（见 §1） |
| 77 的根因 | ✅ **已核实**：直接出处 = 官方 OpenVision2 `open_clip_config.json → text_cfg.context_length=77`（字段 `vocab_size=49408/width=512/heads=8/layers=12` 是 OpenAI-CLIP 谱系指纹）；官方另有**不受 77 限制**的 caption decoder（prefix-LM，无 text 位置编码）。⚠️ 精确到位的补充：open_clip `TextTransformer` 类默认值**恰好也是 77**（见 §2.5 的如实追注） | `open_clip_config.json`（已抓取原文）；`run/vision/train.py:50-52`；open_clip `transformer.py:952-956` |
| 官方 `open_clip_pytorch_model.bin` 是否含训练过的 text tower | **无**。state_dict 294 个 key = 纯 vision 编码器（24 层 ViT + conv1/cls/pos-embed/ln_post/proj，304.55M 参数），**无任何 text 塔、无 logit_scale** → **无法**用官方 text 塔替代 `clip-vit-large-patch14-336`（官方根本没 ship 训练好的 text tower 权重） | `torch.load(bin, map_location='meta')` 的 key 列表 + shape（§2.3） |
| 正式训练能否变长 | **保持 77，不能也不该在冻结 CLIP 塔下放开**。冻结塔 `max_position_embeddings=77`（`nn.Embedding(77,768)`），>77 直接 `ValueError`；R4 已证截断非坍缩主因，正式训练改用 GPIC `short`（≈20 token，0% 截断）最省 | CLIP `text_config.max_position_embeddings=77` + 实测（§3.A） |

---

## 1. R6.1 —— 后续数据是否切换为 GPIC（结论：分阶段切）

### 1.1 事实①：GPIC 盘上真实规模（实测）

| 项 | 实测值 | 证据 |
|:--|:--|:--|
| train tar 数（落盘） | **462**（全量 8000，**下载仍在进行**，30 分钟内 460→462） | `ls /nas_inference/.../gpic/train/*.tar \| wc -l` → `462`（两次取样间隔增长） |
| 总字节 | **685G**（460 tar 时） | `du -sh .../train/` → `685G` |
| 单 tar 大小 | ~1.49–1.63 GB | `ls -la` 首尾 tar：00000=1,631,979,520B、00459=1,615,370,240B |
| 单 tar 图文对数 | **≈12.4K–12.7K**（json=image 数一致） | 6 个 tar 实测：00000=12639、00100=12363、00200=12739、00300=12424、00400=12442、00455=12511 |

**每 tar 内 `{key}.json` + `{key}.jpg|png` 成对、交替存储**（README + 实测 tar 00000：json=12639、jpg=11042、png=1597，pairs=12639）。

**→ 现有量能提供多少图文对**：**462 tar × ≈12.5K ≈ 5.8M 对**（若只取 `short` 档 ≈ 45% → ≈ 2.6M 对）。

### 1.2 硬约束检查：现有量够不够 R5？

- 任务书口径：R5 需 **4 架构 × 3000 步 × bs64 ≈ 19.2 万对/架构**（= 192K/架构；4 架构合计 ≈ 768K 对）。
- **结论：现有量远超需求，不是硬约束。** 5.8M 对（全档）是 192K/架构的 **≈30×**；单 `short` 档 2.6M 对也是需求的 **≈13×**。即便按更保守的"global batch=512"口径（3000×512=1.536M/架构），`short` 档 2.6M 仍能覆盖 4 架构复用同一池。
- → **无需等下载、也无需"数据量不足"字样**；现盘 462 tar 已足够 R5 与正式训练的前期使用。

### 1.3 事实②：caption 质量对比（复用 R4 `r4_gpic.py` 同口径，本轮重扫 6 tar）

| 档位 | n | 占比 | BPE mean/med/p90/max | 词数 mean | 77 截断率 | 空 |
|:--|:--|:--|:--|:--|:--|:--|
| tag | 710 | 0.9% | 11.4 / 11 / 14 / 40 | 7.1 | 0.00% | 0 |
| **short** | 33994 | 45.3% | **20.2 / 19 / 27 / 83** | 17.5 | **0.00%** | 0 |
| medium | 33656 | 44.8% | 46.0 / 46 / 56 / 132 | 39.3 | 0.18% | 0 |
| long | 6758 | 9.0% | 158.1 / 156 / 180 / 410 | 132.4 | **100.00%** | 0 |

- 区分度（引用 R4 实测，`r4_semantic.py` 冻结 CLIP 文本塔 off-diag 余弦）：**GPIC-short 0.2447 最分散**（p90 0.37），LLaVA(trunc77) 0.2937，RANDOM text 0.7258（退化）。→ `short` 最优，`long` 与 LLaVA 同病（100% 截断）。
- **抽 25 条 `short` 原文（verbatim，本轮实测见 §4.4）**：可读完确认——短、具体、可区分（"Two women stand in front of a large screen displaying Quiz Show…"、"A giraffe's face is displayed on a large screen in a busy city at night…" 等，非通篇公式化）。

### 1.4 事实③：与 Stage(iv) 的关系

- GPIC 官方定位是 **"for Visual Generation"**（100M 训练，VLM 生成 caption，用于视觉生成模型），不是对比学习，也不是 MLLM 指令数据。
- 四档 caption（tag/short/medium/long）中：`short`/`medium` 切合 CLIP 式短文本对比；`long` 可作 captioning 数据 → **GPIC 只能"部分顺带"服务 MLLM 对齐（作为多粒度 caption 语料），不是完整 MLLM 指令集**。完整 MLLM 对齐仍由 LLaVA-OneVision Mid-Training 承担（它本就是为 MLLM 设计的）。
- → 换 GPIC **不会**与 Stage(iv) 数据重复投入冲突；但 GPIC **不能取代** LLaVA 的 MLLM 对齐角色。

### 1.5 事实④：代价（切 GPIC 要下多少/多久/放哪）

- **无需再下载**：现盘 462 tar（5.8M 对）已覆盖 R5 + 正式训练前期；**上游 GPIC 下载由 data 链路后台进行**，本任务不额外触发大下载。
- 若需全量 8000：剩余 7538 tar × ~1.49GB ≈ **11.2TB**；当前下载速率 ≈ 1 tar/分钟 → 约 **5 天**。
- 落盘：原始 in `/nas_inference`（源，21T 可用）；如需在 `/nas_train` 重新打包成 webdataset，11TB 装得下（`/nas_train` 剩 32T），但**现阶段没必要**（462 tar 已够）。

### 1.6 必须算清的一笔账：切 GPIC 后 R5 与 R1/R2 历史可比性

- **独立确认推理**：切数据后 R5 的 loss 与 R1/R2 历史数字**不可比**（数据变了）。但 **R1/R2 的全部 loss 类数字已因坍缩作废（R3/R4 已证）**，故**不构成阻碍**。✅ 推理成立。
- **"数据全换"对 R5 表格内部各格子可比性的影响**：只要**同一张对比表内所有格子用同一份数据**，架构/分辨率之间仍可比。风险只在"**混用**"——即 P0 用 en500k、P1/P2 换 GPIC——那会让"数据 + 分辨率"同时变，无法归因。
- → 分阶段切的具体纪律：**R5 阶段统一 en500k（含 P1/P2），GPIC 只作为"并行对照臂"（另开一组，不混入主表）；正式训练整体切 GPIC `short`。**

### 1.7 R6.1 结论（三选一）与 R5 联动

- **结论 = 分阶段切**：
  - **R5 P0/P1/P2（架构/分辨率对比）＝ 保持 en500k**（LLaVA 长 recaption）。理由：它是 R4/R5 已 C1–C4 验证、**零额外 I/O**、且是任务书要求的"必留 LLaVA 对照臂"。
  - **正式训练（Stage(iii) 编码器训练，Stage(iv) 之前）＝ 切 GPIC `short`**。理由：0% 截断、off-diag 0.245 最分散、许可全 permissive，是更优的 CLIP 式对比数据；且 462 tar 已足够启动。
- **R5 联动（写入 MEMORY_VISION.md）**：R5 默认数据 en500k **不变**（报告注明"依据来自 R6 分阶段切裁定"）；P1/P2 **不换数据**，可加 GPIC 臂作对照（加分项非必需）。

---

## 2. R6.2 —— 77 截断的根因（核实运维裁定，非重查）

### 2.1 事实①：官方 config 确有这五个字段（已抓原文）

抓取命令（`hf` CLI；`curl https://huggingface.co/UCSC-VLAA/...` 返回 `307` 重定向 → 网络可用）：

```bash
/nas_train/app.e0031982/miniforge3/envs/py310/bin/hf download \
  UCSC-VLAA/openvision2-vit-large-patch14-336-vision-only open_clip_config.json --local-dir /tmp/r6_ov2
cat /tmp/r6_ov2/open_clip_config.json
```

`open_clip_config.json` 原文（491 字节，逐字）：

```json
{
  "model_cfg": {
    "embed_dim": 1024,
    "vision_cfg": {
      "layers": 24, "width": 1024, "patch_size": 14, "image_size": 336,
      "pool_type": "avg", "output_tokens": true,
      "norm_kwargs": { "eps": 1e-06 }
    },
    "text_cfg": {
      "context_length": 77,
      "vocab_size": 49408,
      "width": 512,
      "heads": 8,
      "layers": 12
    }
  }
}
```

→ **五个字段逐一在官方 config 里**：`context_length=77`、`vocab_size=49408`、`width=512`、`heads=8`、`layers=12` ✅。

### 2.2 事实②：`run/vision/train.py:50-52` 与官方 `text_cfg` 逐字段一致

```python
# run/vision/train.py:50-52
def build_text_tower(embed_dim=EMBED_DIM):
    return TextTransformer(context_length=77, vocab_size=49408, width=512,
                           heads=8, layers=12, output_dim=embed_dim)
```

| 字段 | 官方 `text_cfg` | `train.py` | 一致 |
|:--|:--|:--|:--|
| context_length | 77 | 77 | ✅ |
| vocab_size | 49408 | 49408 | ✅ |
| width | 512 | 512 | ✅ |
| heads | 8 | 8 | ✅ |
| layers | 12 | 12 | ✅ |

（`train.py` 多一个 `output_dim=embed_dim` 是投影维，非 text_cfg 字段；R1 时 `EMBED_DIM=512` 与官方 `width=512` 同维。逐字段一致 ✅。）

### 2.3 事实③（⭐⭐）：`open_clip_pytorch_model.bin` 里**没有**训练过的 text tower

抓取：`hf download ... open_clip_pytorch_model.bin --local-dir /tmp/r6_ov2`（1,218,313,907 字节，已完成）。
只读 key（不物化张量）：

```bash
torch.load('/tmp/r6_ov2/open_clip_pytorch_model.bin', map_location='meta')
```

**key 清单（294 个）**：

```
type: dict  n_keys: 294
first keys: positional_embedding / transformer.resblocks.0.ln_1.bias ... .mlp.c_fc/.attn.in_proj ...
last keys : ... transformer.resblocks.9.attn.out_proj.weight / class_embedding / conv1.weight / ln_post.bias / ln_post.weight / proj
top-level prefix counts: transformer=288, ln_post=2, positional_embedding=1, class_embedding=1, conv1=1, proj=1
has visual.* keys : False
has text.* keys   : False    (唯一条含 "positional" 的是 vision 的 positional_embedding)
has logit_scale   : False
```

**张量 shape（决定它是什么）**：

```
conv1.weight                (1024, 3, 14, 14)   # patch embed, patch=14, width=1024
class_embedding             (1024,)             # CLS token
positional_embedding        (577, 1024)         # (336/14)^2 + 1 = 576+1
ln_post.{bias,weight}       (1024,)
proj                        (1024, 1024)        # 视觉投影头 embed_dim 1024→1024
resblocks.23.attn.in_proj    (3072, 1024)       # 第24层(末层)
resblocks.23.mlp.c_fc        (4096, 1024)       # MLP 4096
total params = 304,553,984  (304.55 M)          # 纯 vision
```

**→ 结论：bin 是「vision-only」**（24 层 ViT，width 1024，patch 14，image 336，CLS 池化，embed_dim 1024，304.55M）。**无 `text.*` / `token_embedding` / `text_projection` / `logit_scale` / `logit_bias`。**

**为什么这点要紧**：官方根本没有发布**训练好的** CLIP 式对比 text tower 权重——`text_cfg` 只是 open_clip 框架**要构建的那个 text 塔的 config**（open_clip 加载 config 会 new 一个 text 塔，但 checkpoint 不含其权重）。因此：

- **不能**用官方 text tower 权重去替换 `clip-vit-large-patch14-336` —— **没有权重可提取**。
- 官方 repo 唯一文本侧权重是 `caption_decoder.safetensors`（540MB），那是 **caption 生成解码器**（§2.4），非对比学习文本编码器，规格/目标都不同，**不能**用于 CLIP InfoNCE 对比。
- 本项目 R1 确实把这个 text 塔**随机初始化**过（`EXPERIMENTS_VISION.md:24`「四架构共用随机 init」），R4/S5 认定这正是坍缩主因。
- **替代方案与代价**：改用现成 `clip-vit-large-patch14-336` text tower（768 维，**非**官方 512 维）——正是 R4/R5 已做的修复。改回 512 维无权重可用 → **不推荐**；保持 768 维冻结 CLIP text tower → C1–C4 已在 R4 验证通过（**无需重验**），只需 vision 读出头 `embed_dim→768`（R5 已做）。**结论：继续用 `clip-vit-large-patch14-336`（768 维），不加投影、不改回 512。**

### 2.4 事实④：官方还有第二套文本侧（caption decoder，不受 77 限制）

`text_decoder_config.json`（464 字节，原文）：

```json
{
  "architecture": "OpenVision2TextDecoder",
  "fusion_style": "concat",
  "width": 768, "depth": 12, "num_heads": 12, "mlp_dim": 3072,
  "vocab_size": 32000, "vision_width": 1024,
  "pad_id": 0, "bos_id": 1, "eos_id": 2,
  "tokenizer": "bert wordpiece (bert_base_vocab_bos_eos.txt), lowercase, [PAD]=0 [bos]=1 [eos]=2"
}
```

`modeling_openvision2_decoder.py:10,22`：`text_embeds = Embed(text_tokens)  # no positional embedding`；`NO positional embedding on the text stream.`。README 亦写「no positional embedding on the text stream」。
→ **官方自己的 image→caption 走 caption decoder（concat/prefix-LM，无 text 位置编码），不受 77 限制；77 只属于那个 CLIP 式对比学习的 `text_cfg`。** ✅ 与运维裁定一致。

### 2.5 事实⑤（如实追注，不回避）：open_clip `TextTransformer` 类默认值恰好也是 77

运维裁定「不是 open_clip 的默认，是官方 config」。**证据核查结果是一条精确 nuance**：

- open_clip `transformer.py:952-956`（类签名）：`TextTransformer(context_length: int = 77, vocab_size: int = 49408, width: int = 512, heads: int = 8, layers: int = 12, ...)` —— **类默认值本身就是 77/49408/512/8/12**。
- open_clip `tokenizer.py:23`：`DEFAULT_CONTEXT_LENGTH = 77`。
- open_clip `factory.py:708`：`context_length = text_config.get('context_length', DEFAULT_CONTEXT_LENGTH)`。

**精确表述**：`77` 同时是 (a) open_clip `TextTransformer` 类默认、(b) open_clip `SimpleTokenizer.DEFAULT_CONTEXT_LENGTH`、(c) 官方 `text_cfg.context_length` 三者的同值——同源于 OpenAI CLIP 谱系（`vocab_size=49408` 是 OpenAI CLIP BPE 词表大小）。**本项目「直接来源」确为官方 config**：`train.py:51` 是**显式硬编码**这五个值（而非无参 `TextTransformer()` 依赖默认），硬编码的 `vocab_size=49408` 指纹指向 OpenAI-CLIP 谱系。运维裁定「直接来源=官方 config」在来源/意图层面成立；本注仅作事实补充（值本身三者相等），不影响裁定。

### 2.6 事实⑥：本项目与官方的其他差异（已确认两处 + 补全）

| 项 | 官方 | 本项目 R1 | 本项目 R4/R5 | 有意/无意 |
|:--|:--|:--|:--|:--|
| vision 层数（depth） | **24**（`vision_cfg.layers=24`） | **30**（`models.py:170 depth=30`） | 30 | **有意**（凑 500–600M → 505.0M） |
| `embed_dim` | **1024**（`model_cfg.embed_dim=1024`；`proj (1024,1024)`） | **512**（`models.py:16 EMBED_DIM=512`） | **768**（`r5_train.py:32 EMBED=768`） | **有意**（R1 对齐随机 512w；R4/R5 对齐冻结 CLIP 768） |
| （补充）图像档 | 336/14（pos-emb 577） | 224/16（默认锚点） | 224/16（P0） | 有意（4 架构统一锚点） |
| （补充）FFN | gelu 双层 MLP（`mlp.c_fc/c_proj`） | SwiGLU（`models.py SwiGLU`） | 同 R1 | 有意（本项目设计） |
| （补充）池化 | CLS（`class_embedding`） | avg-pool（`ReadoutHead.mean`） | 同 R1 | 有意（本项目设计） |
| （补充）vision 参数 | 304.55M | 505.0M | 505.0M | 有意（规模目标不同） |

**对"与官方可比性"的影响（论文必须交代）**：本项目 `OpenVision2` **不是** UCSC-VLAA 官方 OpenVision2 的忠实复现——同名但**架构不同**（30 vs 24 层、SwiGLU vs gelu、avg-pool vs cls-pool、505M vs 304.5M）。这是「从零 500–600M 四架构公平对比」的**有意**设计（任务书决策 1），**并非**复现官方。⚠️ 论文若写「复现官方 OpenVision2 架构」是**误导**；应写明「OpenVision2 = 本项目从零设计的纯 Attention ViT 基线（30L·1024w·16h·SwiGLU、avg-pool），与 UCSC-VLAA 官方同名模型不同」。`depth 30 vs 24` 与 `embed_dim 512/768 vs 1024` 两处即需显式交代的关键差异。

---

## 3. R6.3 —— 正式训练时 77 能否变长（分开回答"能不能"与"该不该"）

> 先分清旋钮：**77 = text 塔侧的「文本上下文长度」**（由配给它的文本塔决定）；**图像 token 数 = vision 塔侧**（R5 P1 负责），两者无关，本任务只答 text 侧 77。

### 3.A 技术上能不能（当前 R4/R5 recipe：冻结 CLIP 文本塔）

**当前文本塔** = `openai/clip-vit-large-patch14-336` 的 text tower（冻结，768 维）。实测其位置编码：

```
# transformers CLIPTextModel 实测（r6_clip77_test.py，CPU，local_files_only）
position_embedding shape: (77, 768)  => max_position_embeddings = 77
config.max_position_embeddings = 77
config.vocab_size = 49408 / hidden_size = 768 / layers = 12 / heads = 12
```

- 源码（`transformers/models/clip/modeling_clip.py:221-225`）：`CLIPTextEmbeddings.__init__` 里 `self.position_embedding = nn.Embedding(config.max_position_embeddings, embed_dim)` = `nn.Embedding(77, 768)`；`forward`（`:235-239`）有显式守卫：`if seq_length > max_position_embedding: raise ValueError("Sequence length must be less than max_position_embeddings ...")`。

**超过 77 会怎样（实测，非猜）**：

| 情形 | 结果 |
|:--|:--|
| `truncation=True`（R5 现行 `r5_train.py:58-59` `max_length=77, truncation=True`） | **静默截断**到 77（input_ids shape=(1,77)），无报错，嵌入正常出 (1,77,768) |
| `truncation=False`（>77 词，实测 277 token） | **`ValueError: Sequence length must be less than max_position_embeddings (got 277 and 77)`**（同时 tokenizer 打 warning「longer than the specified maximum ... will result in indexing errors」） |

**→ 判定：保持冻结塔的前提下，77 不能变长，上限就是 77。** 因为位置编码是固定的 `nn.Embedding(77,768)`，前向对 `seq_length>77` 直接抛 `ValueError`（**非静默截断、非输出错乱，是硬报错**）；唯一"绕过"方式是靠 tokenizer 的 `truncation=True` 静默裁掉尾巴。

### 3.B 若要变长，有哪些路（逐条代价/风险 + 推荐）

| # | 路径 | 代价 / 风险 |
|:--|:--|:--|
| 1 | **位置编码插值/扩展**（对 1D 文本 pos-embed 插值到 N） | 文本 pos-embed 是**学习得到的 1D 向量序列**，与图像 2D bicubic 插值不同，插值质量差；新位置需微调才有效 → **破坏"纯冻结预训练"前提**；只为 77→n 不值得。**不推荐** |
| 2 | **换文本塔** | SigLIP 默认 context **64（更短）**（open_clip `tokenizer.py:575 SigLipTokenizer context_length=64`）；LongCLIP/LM 系（2K–32K）→ **换语义空间**，R4 的 C1–C4 要**重验**。**代价高** |
| 3 | **解冻当前 CLIP 塔继续微调** | 解冻需复训、要重验 C1–C4；**失去"纯冻结"可控性**。⚠️ **但未必坍缩**（R4 证伪的是"随机文本塔"，**不是**"微调预训练塔"，见 §3.C）——尚无实验证据，需专门验证 |
| 4 | **从零训文本塔** | 🚫 **R3/R4 已证这条路坍缩**（随机塔 off-diag **0.7258**）→ **明确不推荐** |
| 5 | **分块 + 聚合**（chunked pooling，长 caption 切段分别编码再池化） | 可行，但**引入池化偏差**（不同段信息权重、梯度借用复杂），且对当前 20-token 短 caption 无意义 |
| 6 | **不放开，改用短 caption**（= GPIC `short`） | **成本最低**：0% 截断、off-diag 0.245 最分散，直接规避 77 问题 |

**推荐 = 第 6 条（改用短 caption），即与 R6.1 的「分阶段切」一致。**

### 3.C ⭐ 该不该（结合 R4 既有结论）

- **先讲准 R4 结论，别用过头**：R4 证伪的是「**随机初始化文本塔**」（S5 实测 RANDOM text same-tower off-diag = **0.7258**），**不是**「微调一个预训练文本塔」。→ **"解冻当前 CLIP 塔继续微调"是一个尚未验证的选项，不等于一定坍缩**。如实如此表述。
- **独立确认 R4 的推理**：R4 决定性实验（`r4_s1_dec.py`）：被截断丢弃的尾部 off-diag **0.372** 比保留的头部 **0.295** **更相似** → 截断是**背景事实**，不是坍缩推手。→ **"放开 77" 不是修复坍缩的必要条件** ✅（初判得到确认）。
- **放开 77 的真实收益**只在两种场景：① 若坚持吃 LLaVA 长 recaption（100% 截断、通篇公式化）；② Stage(iv) 要保留长描述能力。**但对 Stage(iii) 的 CLIP 式对比预训练，短 caption（GPIC short，≈20 token）已 0% 截断、区分度最优，77 完全够用**；长描述能力应交给 Stage(iv) 的 caption decoder / MLLM（官方 OpenVision2 就是走 caption decoder 处理长文本，见 §2.4），**不是**靠对比式 text 塔变长。

**→ 可执行结论**：正式训练时选 **保持 77**（text 塔仍冻结 `clip-vit-large-patch14-336`，768 维）。理由：① 冻结塔硬上限 77（§3.A）；② 截断已证非坍缩主因，放开 77 无收益（§3.C）；③ 配合 R6.1 分阶段切，用 GPIC `short`（0% 截断）让 77 天然冗余。代价 = 0（不用改 recipe、不用重验 C1–C4）。**不推荐的任何"变长"方案**（插值/换塔/解冻/分块）要么破坏冻结前提、要么换语义空间需重验、要么已证坍缩。

---

## 4. 取证的原文摘录（命令 + 输出，逐字）

### 4.1 GPIC per-tar 对数 + license（本轮 `r6_gpic_probe.py` 输出）

```
[R6 GPIC] total tars on disk = 462 (full=8000)
--- per-tar member counts (json / jpg / png) ---
gpic_train_00000.tar: json=12639 jpg=11042 png=1597 (pairs=12639)
gpic_train_00100.tar: json=12363 jpg=10827 png=1536 (pairs=12363)
gpic_train_00200.tar: json=12739 jpg=11154 png=1585 (pairs=12739)
gpic_train_00300.tar: json=12424 jpg=10888 png=1536 (pairs=12424)
gpic_train_00400.tar: json=12442 jpg=10929 png=1513 (pairs=12442)
gpic_train_00455.tar: json=12511 jpg=10965 png=1546 (pairs=12511)
--- license mix ---
  CC BY 2.0                     54100 (72.0%)
  Public Domain Mark 1.0        10312 (13.7%)
  CC BY 4.0                      4274 (5.7%)
  CC0 1.0                        3268 (4.4%)
  CC BY 3.0                      2230 (3.0%)
  No known copyright restrictions  557 (0.7%)
  ...（其余均为 permissive）
```

### 4.2 GPIC caption 档位长度（本轮 `r6_gpic_probe.py`，open_clip SimpleTokenizer）

```
type            n      %   tok_mean tok_med tok_p90 tok_max  w_mean trunc77%  empty
tag           710   0.9%      11.4      11      14      40     7.1    0.00%      0
short       33994  45.3%      20.2      19      27      83    17.5    0.00%      0
medium      33656  44.8%      46.0      46      56     132    39.3    0.18%      0
long         6758   9.0%     158.1     156     180     410   132.4  100.00%      0
```

### 4.3 LLaVA en500k（R4 引用，对比基准）

> `EXPERIMENTS_VISION_ROUND4.md:38-39`：LLaVA en500k caption mean **219 BPE**、**100% 截断**（只留 34%）、`the image` 开头占 30.3%。→ 与上表 `short`（20 token / 0% 截断）形成鲜明对照。

### 4.4 抽 25 条 GPIC `short` 原文（verbatim）

```
[01] Two women stand in front of a large screen displaying "Quiz Show" and "Squats" graphics at an event.
[02] Inside a grand church, tall columns and arched windows let sunlight shine through stained glass.
[03] Ice hockey players in maroon and yellow jerseys celebrate on the ice during a game.
[04] An orange and white shipping container sits on train tracks, covered in graffiti and labeled "J.B. HUNT Intermodal."
[05] A colorful pillar with painted faces stands in a modern shopping mall near glass storefronts.
[06] Several people in formal attire stand together indoors, holding programs and a bouquet of flowers.
[07] A bush with shiny green leaves grows in a shady forest area.
[08] A swimmer in a TYR cap and goggles rests at the pool edge, holding a starting block.
[09] A woman sits at a sewing machine with two cats nearby. One cat stands on the machine, another walks on the floor.
[10] Three men in white robes walk on a street, one holding a rosary and wearing glasses.
[11] A woman in a black top stands in front of a screen, smiling while holding papers.
[12] A giraffe's face is displayed on a large screen in a busy city at night, surrounded by bright neon signs and tall buildings.
[13] A man sits on a throne surrounded by many people in robes and turbans, all facing him.
[14] A plain, off-white piece of paper with slight yellowing and faint stains along the edges.
[15] Two cyclists ride on a snowy mountain road, wearing helmets and racing gear.
[16] A woman and a man stand together in a crowded market, surrounded by people and hanging goods.
[17] People gather on a crowded beach with umbrellas and towels. The weather is sunny with 75°F air and 71°F water.
[18] Two soccer players run across a green field, one in a white jersey with the number 4, as a ball rolls nearby.
[19] A green informational sign stands near a muddy path beside a river, surrounded by trees and fallen logs.
[20] A man in a red vest paddles a kayak on a river, near a concrete barrier with bare trees in the background.
[21] A man in a yellow shirt and black cap stands in a stadium with spectators in the background.
[22] A man in a green wig and striped shirt holds an orange balloon while dancing on a street. A person with pink hair dances nearby as spectators watch.
[23] A person with red hair stands on grass, facing a tall monument under a colorful sunset sky.
[24] A smiling woman with blonde hair sits at a table with cups and food, surrounded by people at a gathering.
[25] A woman holds a sign saying "15 mins left" while standing behind a door. Two people sit nearby in a room.
```

### 4.5 冻结 CLIP 文本塔 >77 实测（`r6_clip77_test.py` 输出，逐字）

```
position_embedding shape: (77, 768) => max_position_embeddings = 77
config.max_position_embeddings = 77
config.vocab_size = 49408 hidden_size = 768 layers = 12 heads = 12
[truncation=True] input_ids shape: (1, 77)
[truncation=True] OK, last_hidden_state: (1, 77, 768)
Token indices sequence length is longer than the specified maximum sequence length for this model (277 > 77). Running this sequence through the model will result in indexing errors
[truncation=False] input_ids shape: (1, 277)
[truncation=False] RAISED: ValueError : Sequence length must be less than max_position_embeddings (got `sequence length`: 277 and max_position_embeddings: 77
```

### 4.6 源码行摘录（关键出处）

- `run/vision/train.py:50-52`（§2.2 已贴）：`TextTransformer(context_length=77, vocab_size=49408, width=512, heads=8, layers=12, output_dim=embed_dim)`。
- `run/vision/r5_train.py:32,57-59`：`EMBED = 768`；`self.tok(caps, return_tensors='pt', padding='max_length', max_length=77, truncation=True)['input_ids']`；`:155` `D.build_loader(..., text.tokenize, ...)` → R5 文本侧 = `CLIPTokenizer(max_length=77, truncation=True)`。
- `run/vision/models.py:16` `EMBED_DIM = 512`；`:168-177` `OpenVision2(... depth=30 ... mlp_dim=4096)` + `SwiGLU`（`:24-32`）+ `ReadoutHead.mean`（avg-pool，`:162-164`）。
- `open_clip/transformer.py:947-956` `TextTransformer(context_length:int=77, vocab_size:int=49408, width:int=512, heads:int=8, layers:int=12, ...)`。
- `open_clip/tokenizer.py:23` `DEFAULT_CONTEXT_LENGTH = 77`；`:572-575` `SigLipTokenizer(... context_length: Optional[int] = 64)`。

---

## 5. 论文回填建议（`6_vision_encoder.tex`；🚫 本任务不改 tex）

> 现状：当前 `6_vision_encoder.tex`（9437B，2026-10-01 17:51）仍是**旧 recipe**（SigLIP + 共享 512w text 塔 + lr 1e-3 锚点），`tab:visarch/visres/visobj` 三表全是**坍缩读数**，R4/R5 已要求回滚重写；R6 额外补充以下几点。

1. **数据来源段（该写，且要更新）**：现状只写"unified 500K subset of LLaVA-OneVision-1.5 (imagenet/EN)"。按 R6.1 分阶段切，应写两级：
   - R5 架构/分辨率对比 = en500k（LLaVA imagenet/EN 500K 对，webdataset 25 shard / 68.59 GiB）；并在 caption 段注明「LLaVA recaption mean 219 BPE、100% 截断、通篇公式化（the image 占 30%）」（R4 已证）。
   - 正式训练（Stage(iii) 编码器训练，Stage(iv) 之前） = **GPIC `short`**（20 token、0% 截断、off-diag 0.245 最分散、许可全 permissive）。
2. **context length 段（该写，一句话即可）**：`text tower = 冻结 clip-vit-large-patch14-336（768 维，context 77，max_position_embeddings=77）`。可选补一句 R6 裁定：「77 是冻结 CLIP 文本塔的位置编码上限（>77 抛 ValueError）；因正式数据用 GPIC short（0% 截断），77 非瓶颈」。
3. **坍缩改写（R4 已提，R6 重申）**：正文 finding 的 loss 排名与 eval R@1 均为坍缩读数，须标注作废，替换为 R5 P0 的 InfoNCE + 冻结 CLIP 修复配方读数。
4. **命名去歧义（R6 新增，重要）**：论文 "OpenVision2" 必须**不再**暗示复现 UCSC-VLAA 官方 OpenVision2（官方 24L/1024w/304.5M/gelu/cls-pool/336-14）；本项目是**从零 30L/1024w/505M/SwiGLU/avg-pool/224-16**。应写「本项目从零设计的纯 Attention ViT 基线」，并交代 depth(30 vs 24) 与 embed_dim(512/768 vs 1024) 两处差异，避免"复现官方"的误导。

---

## 6. 附录：本任务触碰的文件 / 临时产物

- 产出（需入库）：`run/EXPERIMENTS_VISION_ROUND6.md`（本文件）、`run/MEMORY_VISION.md`（更新）、`run/daily-memories-vision/2026-10-01.md`（追加）。
- 临时证据（未入库，可清理）：`/tmp/r6_ov2/`（含 `open_clip_pytorch_model.bin` 1.22GB + config 4 小文件）、`/tmp/r6_gpic_probe.py`、`/tmp/r6_clip77_test.py`、`/tmp/r6_bin_keys.py`、`/tmp/r6_bin_shapes.py`。
- 约束核验：**纯 CPU、未占 GPU、未中断 R5 P0**（R5 P0 仍在跑，末架构 moevie step100/3000）；未修改任何 `*.tex`；未碰 pretrain/data/ops 文件。