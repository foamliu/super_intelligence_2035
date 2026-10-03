# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 0

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R10_done**（① 回收 12 点 IN-1k ✅ → ② 3 点 M 拟合 ✅ → ③ 补密 w384/w640 + **5 点 M 重拟合 ✅**）；**R14 ✅ · E1 ✅**；**R11-L 预注册 ✅**（`EXPERIMENTS_VISION_ROUND11.md`，判据+公平表+6 臂）→ 下一步实现+启动臂② SigLIP（8 卡）；R13 待运维批准 |
| WAITING | 0（R10-③ `denseM ALL DONE @13:00:30`；收尾 4 步已执行：5-M 拟合 + 回填 §2/§3/§4 + 状态头 + push） |
| ERROR_COUNT | 1（R9 阶段一 w512 首跑 @~8900 步 crash：CC12M/Amshaker wds 含损坏 jpg → 已由 data.py `ignore_and_continue` 修复） |
| BUDGET_USED | R2–R9 累计 + R10（R10-① IN-1k ~1 GPU·h；R10-③ w384+w640 各 30k 步 ≈2×1.98h×8 卡，详见 EXPERIMENTS_VISION_ROUND10.md） |
| 更新 | 2026-10-03（R10 全部完成：③ denseM w384/w640 ✅ → 5 点 M 重拟合 R²=0.960 → **w384@15.36M=7.99% 全宽最高、无饱和点**；收尾回填 + push） |
| WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

## R9 完成（converged）结论速查（2026-10-03，权威详见 EXPERIMENTS_VISION_ROUND9.md）

- **阶段一缩塔先导**（OpenVision2 × width{512,768,1024} × 30k，同 recipe/数据/batch512）：IN-1k lp = **6.10% / 3.63% / 1.03%**（zs 2.74/1.91/1.02）→ **塔越小每样本效率越高** → 选 **w512（126.8M）**。
- **阶段二**（w512 × 108k 步 = 55.3M 样本）：无坍缩（C1≈0.36 / C2_gap≈+0.10 / loss_ema 5.99→3.71，steady 2904 img/s）；IN-1k lp 峰值 **7.70%**@51.2M，zs top-1 3.59% / top-5 11.47%。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 acc=0.251−0.864·N^−0.090（渐近 **25.1%**）；对数线性 acc=−0.229+0.0398·log10(N)。外推 20% 需 619 亿（对数）/ 41 万亿（幂律）样本 → **本地 ≈118M 唯一对上限（C1 修正）够不到 20%+**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对，我们 649× 少），非架构。详见 EXPERIMENTS_VISION_ROUND9.md §4–§5。

## R10（2026-10-03）：补全 M 轴的 scaling law

> 运维指出 R9 只扫了数据侧 N（固定 w512），M 轴没做；R10 复用阶段一已落盘三档塔宽 ckpt 补 M 轴，拟合 (N,M) 二维 scaling law。

- ✅ **R10-① 回收 12 点 IN-1k 完成**：3 塔 × step{10k,20k,30k}，`r10_eval_stage1.sh` → `r8_eval_in1k.py --ckpts`（exit 0）。lp(w512/w768/w1024 @N=5.12/10.24/15.36M)：3.43/5.45/**6.08**%、1.14/2.03/**3.63**%、0.67/0.99/**0.93**%（证据 `/tmp/r10_stage1_in1k.log`）。
- ✅ **R10-② 2D 拟合完成（3 点 M 轴）**：`r10_scaling2d.py`，19 点 → 带交互 R²=0.980：`acc=-1.737+0.333·log10(N)+0.185·log10(M)-0.036·log10(N)·log10(M)`；M 边际效应**全区间为负** ≈ **−2.2 lp pp/参数翻倍**（无交互 c=−0.070，R²=0.975）。→ 数据受限区间**加宽塔是负收益**。
- ✅ **R10-③ 完成（`denseM ALL DONE @13:00:30`，exit 0）**：`r10_run_denseM.sh` 训 w384(71.49M)+w640(197.80M) 各 30k 步（同数据/recipe）+ 自动回收 8 ckpt IN-1k。结果 lp（@N=5.12/10.24/15.36M）：**w384 = 5.77/6.92/7.99%**、**w640 = 1.66/1.99/3.62%**；w384 吞吐 6583 img/s（w640 2418）、final_loss 3.7769（w640 4.3485）。
- ✅ **5 点 M 重拟合完成**：带交互 R²=0.960 `acc=-1.452+0.298·log10(N)+0.150·log10(M)-0.0318·log10(N)·log10(M)`；M 边际 ≈ **−2.2~−2.4 lp pp/参数翻倍**；最优 M 仍在观测下界（71.5M）之下 → **无饱和点、更小塔持续更优**。**w384@15.36M=7.99% 为全部宽度最高**。
- **铁律**：不重跑阶段一训练；每条结论贴证据（命令 + 原始输出 + 路径）；不许猜。

### 🕐 R10-③ 等待已结束（收尾 4 步已执行完毕）
- **结果**：5-M 拟合 R²=0.960（§2.3）+ 最优 N/M（§2.4）+ denseM 8 点表（§3）+ 结论（§4）均已回填 `EXPERIMENTS_VISION_ROUND10.md`；`EXPERIMENTS_VISION.md` 顶部 R10 节 + 本状态头已更新，随后 push。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

- CPU-only 源码普查，与 R10-③ denseM 训练并行。产物：`VISION_OFFICIAL_REPOS_SURVEY.md`（①目标②数据③config④结构差异⑤可复用资产⑥LICENSE⑦三清单）。
- ✅ 两个 ⭐⭐⭐ 仓库源码普查完成（上一 cycle）：**OpenVision**（JAX/TPU，官方 ViT-L/16 = w1024/d24/h16；文本 = BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35）；**ml-aim/AIMv2**（仅模型接口，无训练/损失/数据；LICENSE = Apple Sample Code，🔴 不可 COPY）。
- ✅ 第二阶段（本轮）全部核毕：
  - **OpenVision2 权重 = ✅ 已放出且真带 caption decoder**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only`；含 `caption_decoder.safetensors` + `text_decoder_config.json`（concat/prefix-LM，非 CoCa cross-attn）。🔑 官方 = **patch14/d24**，我们 = **patch16/d30**（models.py:170）→ R13 需另建官方结构塔才能 load。
  - **FastVLM** = ✅ `apple/ml-fastvlm`（FastViTHD 1024² conv-hybrid RepMixer）；LICENSE = Apple Sample Code（research-only，不可抄）。
  - **MambaEye** = ✅ `usingcolor/MambaEye`（MIT）：纯 Mamba2、**小模型监督分类**（非对比）；**MoE-ViE** = ✅ `facebookresearch/moe_vie`（CC BY-NC 4.0）：CLIP 风格 MoE-ViT，官方权重 HF；**iGVLM(AdaLN)/TuringViT** = 🚫 **未找到官方实现**（iGVLM 同名 IG-VLM 是视频QA；TuringViT 仅项目主页）。
- 关键产出（对 R13/R12）：官方 MoE-ViE/FastVLM/MambaEye/AIMv2 权重均可作「官方 vs 自研」对照标尺；OpenVision2 官方是 patch14/d24，需建官方结构塔。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

- 抽 **8 个 tar 均匀抽样**（index 0..1212）实测：**12,537 图文对/tar**（稳定 ±2%）→ **GPIC 全量 ≈ 100.3M**（证官方 100M 卡；旧「5 tar=86M」少计 png 作废）；**已下 1213/8000 tar ≈ 15.2M**。
- `caption_type` mix：short **45.0%** / medium 45.1% / long 9.0% / tag 1.0% → **可训练 short 子类：全量 ≈45M / 已下 ≈6.8M**。
- 🔑 **C1 口径定案**：R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态、仍在下载）——与 `r9_scaling.py --local-cap-m default=118.0` 一致；R11-E「同 N」可比区间被压到 ≈6.8M（short 已下 < 18.5M），须如实说明。已回填 `VISION_ARCH_FRONTIER_2026.md §5`。

## 历史条目已滚动归档（2026-10-03）

- 更早的全部巡检/流水（R1–R9 完整过程，live MEMORY 原 95.7KB）已滚动归档至 `daily-memories-vision/2026-10-03.md`（追加「滚动归档快照」）+ 各日期 daily 文件（2026-09-30 / 10-01 / 10-02）。live MEMORY 已压至 ≤32KB。
- 结论性产物（架构排名 / scaling / 回填建议）以 `EXPERIMENTS_VISION.md` 顶部与 `EXPERIMENTS_VISION_ROUND{2..9}.md` 为权威，不受滚动影响。
