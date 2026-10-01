# EXPERIMENTS_VISION_ROUND7.md — 数据臂对比（en500k vs GPIC vs CC12M）

> **BaiZe Stage(iii) 视觉编码器预训练 · Round 7**（排在 R5 完全结束之后，2026-10-02 启动）
> 定位：R6 已裁定「77 是硬的（冻结 CLIP text tower `max_position_embeddings=77`）」，因此
> 「让数据适配 77」升级为正式训练的头等决策。本轮用 **R5 胜出架构 OpenVision2** × 3000 步、
> **与 R5 P0 完全同口径**（冻结 CLIP-768 text + InfoNCE + lr 3e-3/warmup 20 + @224/16 bs64=512 负样本），
> **只换数据**，对比三条数据臂；并做**两套 held-out 交叉评测**（eval5k + GPIC test）。
> 铁律：不许猜；每条结论附证据（路径+行号/命令+输出）。

---

## 0. 结论（跑完后回填）

| 臂 | 训练数据 | caption 形态 | final_loss | C1@终 | C2_gap@终 | eval5k R@1 (t2i/i2t) | GPIC-test R@1 (t2i/i2t) |
|:--|:--|:--|:--|:--|:--|:--|:--|
| A | en500k（LLaVA recaption，500K 对） | 长 ~219 BPE / 100% 截断 | **4.549**（R5 P0 复用） | 0.3008 | +0.0818 | ⏳待跑 | ⏳待跑 |
| B | Stanford GPIC `short`（~2.77M 对） | 短 20 tok / 0% 截断 | ⏳训练中 | ⏳ | ⏳ | ⏳ | ⏳ |
| C′ | CC12M webdataset（~11M 对） | 短 mean 20.9 / 98% ≤77 | ⏳训练中 | ⏳ | ⏳ | ⏳ | ⏳ |

> **正式训练数据裁定（最终一句话）**：⏳ 待 B/C′ 训练 + 交叉评测完成后写在此处。

---

## 1. R7.1 前置检查（实证）

### 1.1 臂 C′ 的来源 —— data agent `BAIZE_DATA_TASK.md` §0.4（已交付 R2 视觉侧）

data agent 已把 §0.4「去 HF 找更多通用图文对」做完并推远端（`MEMORY_DATA.md` 唤醒 11/12，
commit `12553d7`）。其结论（`DATA_RESEARCH.md` R2-视觉侧，逐字）：

> **本地早已躺着一批「bytes + 短 caption」的通用图文对** ——
> `CC12M webdataset ≈11M`、`Amshaker Mobile-O ≈6M`、`LLaVA-Pretrain/CC3M ≈1.15M`，三者 ≤77 率 98–100%。
> **前 3 推荐（CC12M + Amshaker + LLaVA）全本地、无需新下载**。

| 候选 | 本地路径 | 图像形态 | 规模 | 短 caption 率 | 判定 |
|:--|:--|:--|:--|:--|:--|
| **CC12M**（**选定为臂 C′**） | `/nas_train/app.e0031982/datasets/conceptual-captions-12m-webdataset/data/*.tar` | ✅ bytes（`tar -tf`＝`.jpg/.json/.txt` 三件套） | **1100 tar / 1.2T / ≈11M 对** | **98.0% ≤77**（mean 20.9） | ✅ **臂 C′** |
| Amshaker Mobile-O | `/nas_user/app.e0031982/datasets/Amshaker/Mobile-O-Pre-Train/*.tar` | ✅ bytes（`.jpg/.txt`） | 2250 tar / 3.7T / ≈6M 对 | 100% ≤77 | 备选（未用） |
| Recap-DataComp-1B | — | 🚫 URL-only（已确认） | — | — | 淘汰 |

**选 CC12M 为臂 C′ 的理由**：① bytes（一票否决项通过）；② 规模最大（≈11M，是 GPIC short 的 ~4×、en500k 的 ~22×）；
③ 短 caption 率 98% ≤77；④ 已是 webdataset（`.txt` caption），**无需任何打包**，可直接喂 `data.py build_loader`。
（Amshaker 同为可选项，但 11M > 6M，CC12M 优先。）

### 1.2 GPIC 盘上量（R6 后复查，仍在下载）

- `ls /nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar | wc -l` → **489**（R6 时 462，下载中）
- `ls .../gpic/test/*.tar | wc -l` → **128**（全量，已齐）
- 每 tar 实测（R6 沿用）：`gpic_train_00000.tar` = json 12639 + jpg 11042 + png 1597，`caption_type` = short 5716 / medium 5713 / tag 123 / long 1087。
- → GPIC `short` ≈ 45% × 489 tar × ~12.5K ≈ **2.77M 对**，是 R7 单臂需求（3000×512=1.536M 对）的 ~1.8×，够。

### 1.3 磁盘（df 原文）

```
Filesystem                     Size  Used Avail Use% Mounted on
10.239.22.31:/vol_CTE0_data01  207T  176T   32T  85% /nas_train
10.239.22.32:/vol_CTE0_data03   45T   25T   21T  54% /nas_inference
10.239.22.32:/vol_CTE0_data02  108T   80T   29T  74% /nas_user
```

→ `/nas_train` 剩 32T。臂 B（GPIC 直接读 `/nas_inference`，**不重打包、不写大文件**）、臂 C′（CC12M 本地直读）——
**两臂均无需任何新下载**，磁盘无压力。

### 1.4 NFS 并发 / GPU 核验（原文）

- **GPU**：`nvidia-smi --query-compute-apps` 空（8×H100 全空闲）→ R7 独占，无争用。
- **pretrain**（`10.239.2.29`，共享 `/nas_train`）：`MEMORY_PRETRAIN_2B.md` PHASE=`R2_active`、WAITING=1，
  最近一条「本唤醒推进」= **P-7 吞吐幅度核查定稿（~00:41）**，其 GPU 全空闲（P-6 lm_eval 尚未启动）→ 无训练 I/O 争用。
- **data agent**（4 路 `hf download` 存活）：`pgrep -af 'hf download'` 见 `base/Ultra-FineWeb 2.99TB`、`LLaVA-OneVision-85M`、
  `gpic 843G`、`SFT-2605 97.6GB` 仍在下载 → **重 I/O 需避让**。本轮 GPIC 用**轻量直读 loader（不解包不重写）**回避争用。

---

## 2. R7.2 交叉评测设计（照任务书，不许各自 eval 自评）

1. **两套 held-out eval**：
   - `eval5k` = en500k 自带 held-out（`/nas_train/app.e0031982/datasets/baize-vision/eval5k/*.tar`，LLaVA 长 caption）。
   - **GPIC `test`**（128 tar，`/nas_inference/.../gpic/test/*.tar`）。
2. **每个臂在两套 eval 上都评** → 3 臂 × 2 eval 交叉表，用 `r7_eval.py`（冻结 CLIP-768 text tower，
   与训练完全一致，`max_length=77`）。
3. **报告 metric**：C1/C2/C4（训练期每 300 步）+ loss + 两套 eval 的 R@1/5/10（i2t 与 t2i）。

---

## 3. R7.3 实验矩阵（与 R5 P0 同口径，只换数据）

| 臂 | 数据 | 命令（摘要） | 状态 |
|:--|:--|:--|:--|
| A | en500k | 复用 R5 P0 OpenVision2（`out/R5_P0_openvision2/vision.pt`，loss 4.549，**不重跑**） | ✅ 已复用 |
| C′ | CC12M | `r7_train.py --tower openvision2 --data-source wds --data '<cc12m>/*.tar' --steps 3000` | 🔄 训练中（先跑） |
| B | GPIC short | `r7_train.py --tower openvision2 --data-source gpic --data '<gpic>/train/*.tar' --steps 3000` | 🔄 训练中（后跑） |

- 相同锚点：`@224/16`、`bs64`（8 卡 → 512 负样本）、`lr 3e-3`、`warmup 20`、`seed 1234`、冻结 CLIP-768 text + InfoNCE。
- 脚本：`vision/r7_train.py`（= r5_train.py + `--data-source` 分支）、`vision/data.py`（新增 `build_gpic_loader`）、
  `vision/r7_run.sh`（串行 C′→B）、`vision/r7_eval.py`（交叉评测）。
- 日志 `/tmp/r7.log`；ckpt `/nas_train/app.e0031982/datasets/baize-vision/out/{R7_C_cc12m,R7_B_gpic}/vision.pt`。

### 3.1 冒烟验证（30 步，两条 loader 均 exit 0）

```
[start] ... data-source=wds ... shards=138/rank   # CC12M 1100/8=137.5
[step 30/30] loss=6.0221 ms/iter=334.9 image/s=1528.9   → [done] final_loss=6.1940
[start] ... data-source=gpic ... shards=62/rank   # GPIC 489/8=61.1
[step 30/30] loss=5.6577 ms/iter=390.2 image/s=1312.1   → [done] final_loss=6.0905
[saved] .../R7_C_cc12m/vision.pt (fused=False)
[saved] .../R7_B_gpic/vision.pt (fused=False)
```

---

## 4. 交付物进度

- [x] `run/EXPERIMENTS_VISION_ROUND7.md`（本文件）
- [x] 训练脚本 `vision/{data.py 扩展, r7_train.py, r7_run.sh, r7_eval.py}`
- [x] R7 两条训练臂已 `setsid` 后台启动（下一步：回收 loss + C1/C2/C4 + 交叉评测）
- [ ] 交叉评测表（B/C′ vs eval5k + GPIC-test）与最终数据裁定（待训练完成）
- [ ] 更新 `MEMORY_VISION.md` + `daily-memories-vision/` + git commit+push（随下一唤醒）
- 🚫 不改 `*.tex`；不碰 pretrain/data/ops 文件。

## 5. 论文回填建议（占位，待跑完填）

- `6_vision_encoder.tex` 数据来源段：R5 架构/分辨率对比 = en500k（LLaVA 长 recaption，作对照臂）；
  正式训练数据 = 由 R7 三臂对比裁定（GPIC short vs CC12M 二选一，均 0–2% 截断、适配冻结 CLIP-77 text tower）。
- 待 B/C′ 训练完成后，给出「正式训练用哪一臂、为什么」的最终一句结论。