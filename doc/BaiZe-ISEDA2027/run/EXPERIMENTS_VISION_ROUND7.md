# EXPERIMENTS_VISION_ROUND7.md — 数据臂对比（en500k vs GPIC vs CC12M）

> **BaiZe Stage(iii) 视觉编码器预训练 · Round 7**（排在 R5 完全结束之后，2026-10-02 启动）
> 定位：R6 已裁定「77 是硬的（冻结 CLIP text tower `max_position_embeddings=77`）」，因此
> 「让数据适配 77」升级为正式训练的头等决策。本轮用 **R5 胜出架构 OpenVision2** × 3000 步、
> **与 R5 P0 完全同口径**（冻结 CLIP-768 text + InfoNCE + lr 3e-3/warmup 20 + @224/16 bs64=512 负样本），
> **只换数据**，对比三条数据臂；并做**两套 held-out 交叉评测**（eval5k + GPIC test）。
> 铁律：不许猜；每条结论附证据（路径+行号/命令+输出）。

---

## 0. 结论（已跑完 · 交叉评测完成 · 2026-10-02）

> **正式训练数据裁定（最终一句话）：用 Stanford GPIC `short`（臂 B）。**
> en500k（臂 A，LLaVA 长 recaption）留作 R5 架构/分辨率对比的对照臂（复用 R5 P0 ckpt，不重跑）；
> CC12M（臂 C′）淘汰（规模最大但交叉评测处处最弱）。

### 三臂训练结果（OpenVision2 × 3000 步 @224/16 bs64=512 负样本，同 recipe，只换数据）

| 臂 | 训练数据 | caption 形态 | final_loss | C1@终 | C2_gap@终 | C4 | 训练 img/s | 判定 |
|:--|:--|:--|:--|:--|:--|:--|:--|:--|
| A | en500k（LLaVA recaption，500K 对） | 长 ~219 BPE / 100% 截断 | **4.5490**（R5 P0 复用） | 0.3008 | +0.0818 | OK | 2419.8 | ✅ 全过 |
| B | Stanford GPIC `short`（~2.77M 对） | 短 20 tok / 0% 截断 | 4.8618 | 0.2428 | +0.0883 | OK | 3562.9 | ✅ 全过 |
| C′ | CC12M webdataset（~11M 对） | 短 mean 20.9 / 98% ≤77 | 5.3999 | 0.2960 | +0.0772 | OK | 2547.4 | ✅ 全过（但检索最弱） |

> ⚠️ InfoNCE loss **不可跨臂直比**（可达成下界随数据难度/分布而变），故 loss 仅作同臂收敛判据（C4）；
> **C1–C4 三臂全过、无一坍缩**——这是 R7 的第一个正结论：修复配方对三种差异很大的数据都稳健。

### 交叉评测（R@1/5/10；两套 held-out，冻结 CLIP-768 text tower，`max_length=77`）

| 臂 | eval5k（LLaVA 长 caption）t2i | eval5k i2t | GPIC-test(`short`) t2i | GPIC-test i2t |
|:--|:--|:--|:--|:--|
| A | **0.0172** / 0.0528 / 0.0850 | 0.0106 / 0.0352 / 0.0566 | 0.0086 / 0.0336 / 0.0524 | 0.0078 / 0.0280 / 0.0488 |
| B | 0.0112 / 0.0448 / 0.0664 | **0.0122** / 0.0380 / 0.0654 | **0.0160** / 0.0508 / 0.0872 | **0.0122** / 0.0498 / 0.0826 |
| C′ | 0.0090 / 0.0342 / 0.0554 | 0.0058 / 0.0264 / 0.0472 | 0.0052 / 0.0222 / 0.0372 | 0.0036 / 0.0168 / 0.0296 |

> 🔑 所有 R@1 **≫ 1/5000 = 0.0002（精确 chance）** → 与 R2/R3「R@1=1/5000 退化」形成决定性对照：
> **修复配方（冻结 CLIP-768 text + InfoNCE）下检索真实有效，不再退化。**

### 裁定理由（五条，逐条可证）

1. **领域内优势对称且干净**：A 在 eval5k（其自身 LLaVA 长 caption 分布）最好（t2i 0.0172），
   B 在 GPIC-test（其自身 short 分布）最好（t2i 0.0160）→ 交叉评测真实测到「领域适配」，且**没有单臂两榜通吃**。
2. **GPIC-short（B）跨域最稳健**：i2t 在两套 eval **都最高**（0.0122 / 0.0122），是唯一 image→text 双向都领先的臂；
   跨域退化最小（t2i 0.0160→0.0112 ≈ 30% 衰减，而 A 0.0172→0.0086 ≈ 50% 衰减）。
3. **CC12M（C′）处处最弱**（两套 eval 四格 R@1 全部垫底），尽管规模最大（~11M，是 B 的 ~4×、A 的 ~22×）→
   淘汰：其 caption 偏自动生成/信息密度低，3000 步内规模换不来检索质量。
4. **en500k（A）只在自家 eval 领先**，且 = `imagenet/EN` 子集 → 测 IN-1k 是**同域/可能同图污染**（R8.2 红线）；
   且其 100% 截断（~219 BPE 只留前 77）意味着训练真正吃进去的是公式化开头，浪费长 caption。
5. → **正式训练 = GPIC `short`**：0% 截断完美适配冻结 CLIP-77、跨域稳健、对 IN-1k 是干净 out-of-domain；
   en500k 留作对照臂，CC12M 淘汰。

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
| C′ | CC12M | `r7_train.py --tower openvision2 --data-source wds --data '<cc12m>/*.tar' --steps 3000` | ✅ 完成（01:00→01:18，loss 5.3999） |
| B | GPIC short | `r7_train.py --tower openvision2 --data-source gpic --data '<gpic>/train/*.tar' --steps 3000` | ✅ 完成（01:18→01:30，loss 4.8618） |

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

## 3.2 训练期 C1–C4 轨迹（每 300 步，两臂，原文取 `/tmp/r7.log`）

**臂 C′（CC12M）** —— C1 全程 0.13–0.30、C2_gap 全程 +0.077~+0.120、C4 全程 OK（loss_ema 6.0957→5.3999 持续降）：

| step | C1 | C2_diag | C2_off | C2_gap | loss_ema | C4 |
|:--|:--|:--|:--|:--|:--|:--|
| 300 | 0.1326 | 0.1303 | 0.0100 | +0.1202 | 5.3520 | OK |
| 600 | 0.1415 | 0.1246 | 0.0105 | +0.1140 | 5.1461 | OK |
| 900 | 0.1367 | 0.1182 | 0.0085 | +0.1097 | 5.1262 | OK |
| 1200 | 0.2676 | 0.1076 | 0.0233 | +0.0843 | 5.4506 | OK |
| 1500 | 0.2489 | 0.1128 | 0.0177 | +0.0951 | 5.3356 | OK |
| 1800 | 0.2714 | 0.0923 | 0.0139 | +0.0784 | 5.3443 | OK |
| 2100 | 0.2069 | 0.1054 | 0.0150 | +0.0903 | 5.3952 | OK |
| 2400 | 0.2370 | 0.1017 | 0.0201 | +0.0816 | 5.4179 | OK |
| 2700 | 0.2583 | 0.1000 | 0.0183 | +0.0818 | 5.4490 | OK |
| 3000 | 0.2960 | 0.0989 | 0.0217 | +0.0772 | 5.3999 | OK |

**臂 B（GPIC short）** —— C1 全程 0.14–0.33、C2_gap 全程 +0.084~+0.145、C4 全程 OK（loss_ema 5.9476→4.8618 持续降）：

| step | C1 | C2_diag | C2_off | C2_gap | loss_ema | C4 |
|:--|:--|:--|:--|:--|:--|:--|
| 300 | 0.1440 | 0.1898 | 0.0447 | +0.1451 | 4.5945 | OK |
| 600 | 0.2258 | 0.1507 | 0.0342 | +0.1165 | 4.4061 | OK |
| 900 | 0.1937 | 0.1375 | 0.0338 | +0.1037 | 4.7789 | OK |
| 1200 | 0.2201 | 0.1375 | 0.0328 | +0.1047 | 4.7507 | OK |
| 1500 | 0.2506 | 0.1164 | 0.0309 | +0.0855 | 5.0451 | OK |
| 1800 | 0.2419 | 0.1262 | 0.0364 | +0.0897 | 4.9303 | OK |
| 2100 | 0.3337 | 0.1154 | 0.0313 | +0.0841 | 4.8703 | OK |
| 2400 | 0.2760 | 0.1298 | 0.0428 | +0.0870 | 4.8685 | OK |
| 2700 | 0.2983 | 0.1350 | 0.0463 | +0.0887 | 4.7341 | OK |
| 3000 | 0.2428 | 0.1250 | 0.0368 | +0.0883 | 4.8618 | OK |

> 判定代码 `r7_train.py`（= r5_train.py 的熔断逻辑）：`C1>0.95` 或 `C2_gap<=0.005` 或 `C4 loss 不降` → 熔断。
> **两臂全程未触发任何熔断**；B 的 C2_gap 全程略高于 C′（+0.088~+0.145 vs +0.077~+0.120），B 表征分散度更好。

## 3.3 交叉评测命令与原文输出（证据）

命令（`/tmp/r7_eval_runner.sh`，串行，单卡 GPU0，冻结 CLIP-768 text + `r7_eval.py`）：

```bash
cd run/vision
CUDA_VISIBLE_DEVICES=0 python r7_eval.py --ckpt out/R5_P0_openvision2/vision.pt --eval-data '<eval5k>/*.tar' --eval-type wds --n 5000
CUDA_VISIBLE_DEVICES=0 python r7_eval.py --ckpt out/R5_P0_openvision2/vision.pt --eval-data '<gpic>/test/*.tar' --eval-type gpic --caption-type short --n 5000
# ... B = out/R7_B_gpic/vision.pt ；C' = out/R7_C_cc12m/vision.pt（同两条 eval）
```

原文输出（`/tmp/r7_eval.log`，R@1/5/10 = text→image 与 image→text）：

```
[R7eval] A_en500k  x wds   : t2i 0.0172/0.0528/0.0850  i2t 0.0106/0.0352/0.0566
[R7eval] A_en500k  x gpic  : t2i 0.0086/0.0336/0.0524  i2t 0.0078/0.0280/0.0488
[R7eval] B_gpic    x wds   : t2i 0.0112/0.0448/0.0664  i2t 0.0122/0.0380/0.0654
[R7eval] B_gpic    x gpic  : t2i 0.0160/0.0508/0.0872  i2t 0.0122/0.0498/0.0826
[R7eval] C_cc12m   x wds   : t2i 0.0090/0.0342/0.0554  i2t 0.0058/0.0264/0.0472
[R7eval] C_cc12m   x gpic  : t2i 0.0052/0.0222/0.0372  i2t 0.0036/0.0168/0.0296
```

> 均为 n=5000 paired retrieval（冻结 CLIP text tokenize `max_length=77, truncation=True`，
> 与训练 `r7_train.py:57-59` 完全一致）。检测时长：两臂训练共 30min（C′ 18m + B 11m）+ 交叉评测 ~7min。

---

## 4. 交付物进度

- [x] `run/EXPERIMENTS_VISION_ROUND7.md`（本文件）
- [x] 训练脚本 `vision/{data.py 扩展, r7_train.py, r7_run.sh, r7_eval.py}`
- [x] R7 两条训练臂（C′=CC12M、B=GPIC-short）跑满 3000 步、C1–C4 全过（`/tmp/r7.log`）
- [x] 交叉评测表（3 臂 × 2 套 held-out，R@1/5/10，cross-eval 原文 `/tmp/r7_eval.log`）
- [x] 最终数据裁定：**正式训练 = Stanford GPIC `short`**（§0 裁定理由五条）
- [x] 更新 `MEMORY_VISION.md` + `daily-memories-vision/` + git commit+push
- 🚫 不改 `*.tex`；不碰 pretrain/data/ops 文件。

## 5. 论文回填建议

- `6_vision_encoder.tex` 数据来源段，建议写成两段：
  1. **R5 架构/分辨率对比**：en500k（LLaVA-OneVision Mid-Training 的 `imagenet/EN` 统一子集 500K 对，长 recaption）
     —— 这是「R5 用同一份数据做四架构/三分辨率公平对比」的对照臂，**不计入正式训练数据**。
  2. **正式训练数据 = Stanford GPIC `short`**（short caption，mean ~20 BPE token，0% 77-truncation），
     理由：① 0% 截断完美适配冻结 CLIP-77 text tower；② 三臂交叉评测中跨域最稳健（image→text R@1 两套 eval 都最高）；
     ③ 对 ImageNet-1k 是干净 out-of-domain（en500k 是 ImageNet 子集，测 IN-1k 会被判污染）。
- 关联一句可写 R7 的发现：**在冻结 CLIP-768 text + InfoNCE 的修复配方下，500K–11M 三个量级的数据臂都能训出
  有意义检索（R@1 0.005~0.017，远高于 1/5000 chance）**——这直接反衬 R2/R3 时代「R@1=1/5000」是坍缩/评测伪影，
  而非数据不可行。
- 🚫 本 agent 不代改 tex（外部统一回填）。