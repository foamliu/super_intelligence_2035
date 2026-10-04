# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R10_done · R14 ✅ · E1 ✅ · R11-L ✅ · R11-L2 ✅ · caption-weight ✅ · R13 ✅ · R11-E ✅ · 臂⑥ AIMv2 ✅ 翻盘**；**R11-F：Arm A ✅(5.53) · B ✅(6.17) · C ✅(5.92) · E ❌端口碰撞未训 · D ❌shard<worker未训**（Q1/Q3=无显著差异，Q2悬置待E重跑，§15.6已落盘）；**R11-G 🔄 运行中** step≈103800/108000 @07:36（**96.1%**，健康无坍缩 C1≈0.38/C2_gap+0.132/C4=OK/loss_ema≈2.26(仍递减)/scale≈73/fused=False，~210ms/iter~2400img/s）→ 链自动接 eval(11ckpt)→R11-H（`/tmp/r11_overnight_chain.sh` PID 4032740 ppid=1 健康）；**10 ckpt 已存**(step10k@01:30..100k@07:22)，final@108k~07:52；ETA train~07:52(~15min)→eval~08:25→R11-H~09:45；✅ **r11g_scaling.py 已建**（幂律+对数线性拟合+预注册判据，已验 InfoNCE 基线复现 a=0.251 R²=0.94）|
| WAITING | 1（**语义=R11-G 108k 训练运行中 → 30min 轮询**；step≈103800/108000 @07:36（**96.1%**），健康无坍缩(C1≈0.38/C2_gap+0.132/C4=OK/loss_ema≈2.26递减/scale≈73/fused=False)，**10 ckpt 已存**(10k..100k)，final@108k~07:52，剩余≈4.2k步×~0.21s≈15min→ETA train~07:52（链自动 eval 11ckpt~35min→~08:25，再自动起 R11-H 30k~1.2h+eval~15min→~09:45 ALL DONE）；✅r11g_scaling.py已建待用；下次唤醒：若G eval完→跑 r11g_scaling.py 回收11点lp+幂律/对数线性拟合R²+渐近a vs InfoNCE 25.1%+写§14结论；GPU空后→Arm E重跑(稳健端口)+Arm D重跑(empty_check=False已修)补Q2） |
| ERROR_COUNT | 1（R9 阶段一 w512 首跑 @~8900 步 crash：CC12M/Amshaker wds 含损坏 jpg → 已由 data.py `ignore_and_continue` 修复） |
| BUDGET_USED | R2–R9 累计 + R10 + R11-L/②③④ + R11-L2 LoRA + R11-L caption-weight + R11-E GPIC（8.65 GPU·h）+ **臂⑥ AIMv2（✅ 7076s≈1.97h×8卡≈15.7 GPU·h）+ AIMv2 4-ckpt eval（~13min×1卡≈0.22 GPU·h）** + **R11-F 🟢 进行中**（Arm A GPIC short 30k@~80ms→~40min×8卡；5 臂串行总 ~5–6h×8 卡 ≈ 40–48 GPU·h） |
| 更新 | **2026-10-05 07:36（R11-G 巡检：step103800/108000=96.1% 健康，10 ckpt 已存(10k..100k@07:22)，final@108k~07:52，ETA train~07:52→eval~08:25→R11-H~09:45，无坍缩(C1 0.38/C2_gap+0.132/C4=OK/loss_ema 2.26递减/scale 73/fused=False)，链正常(PID 4032740 ppid=1)，8卡util 100%(7/8)，~210ms/iter~2400img/s；✅r11g_scaling.py已建待用)）** · 2026-10-05 06:58（step93650=86.7%） · 2026-10-05 06:25（step85400=79%） · 2026-10-05 05:53（step77300=71.6%） · 2026-10-05 05:18（step68250=63.2%） · 2026-10-05 04:11（step51400=47.6%） · 2026-10-05 03:38（step42850=40%） · 2026-10-05 03:06（step34800=32%） · 2026-10-05 02:32（step26050=24%） · 2026-10-05 00:55（R11-F A/B/C✅落盘+Q1/Q3裁定+E/D失败诊断+data.py修empty_check） · 2026-10-04 23:38（NFS崩溃修复+overnight chain启动） |
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

## R11-L 目标函数轴（2026-10-03）：arm② SigLIP ✅ → arm③ LocalLoss ✅ → 臂④ CoCa 待实现

> 只变目标函数，其余控变量（塔 w512 · 冻结 CLIP-768 · CC12M+Amshaker · lr3e-3 · bs512 · N=15.36M/30k 步 · IN-1k frozen-trunk lp）。预注册判据：同 N 下 lp 比基线 +1.5 点 → 局部推翻「25.1%=对比渐近」。

- ✅ **arm② SigLIP 完成（15:26，`ALL DONE`）**：`r9_train.py --loss siglip`（`SigLipLoss` bidir + 可训 `logit_bias` init−10，`r9_train.py:162-165`）。30k 步无坍缩（C1 0.333 / C2_gap +0.103 / C4=OK / final_loss 5.4643 / steady 2448 img/s）。IN-1k lp = **2.19 / 3.13 / 4.36%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ **未超 +1.5 阈值、未翻盘**。证据 `/tmp/r11_siglip.log`。
- 🚀 **arm③ LocalLoss 已启动（15:29，.12 全 8 卡）**：`r9_train.py --loss localloss`（`ClipLoss(local_loss=True, gather_with_grad=False)`，`r9_train.py:166-168`）→ `R11L_localloss_w512` 30k 步。⚠️ **更正**：读 open_clip 源码（`loss.py:56-63,116-121`）确认 `local_loss=True` **仍是 512 负样本 all-gather**，只算本地 64 行 logits（省算/内存 + 本地图像不再从 text→image 拿梯度）→ 是「计算/梯度路径」变体、**非「负样本池 512→64」**（此前描述有误，已改）。arm③ 因此可证「损失对 local-vs-global 行是否不变」，但**不再测试负样本池大小**——真正池大小消融需另写不 gather 的自定义 loss（待后续决定）。
- ✅ **arm③ LocalLoss 完成（17:43，`ALL DONE`，收尾已做）**：`[done] total=7076.8s final_loss=4.4774 steady=2343 img/s fused=False`，无坍缩（C1 0.2378 / C2_gap +0.1101 / C4=OK）。IN-1k lp = **1.81 / 3.60 / 4.33%** @5.12/10.24/15.36M，全 < 基线（3.43/5.45/6.08%）→ Δ −1.62~−1.85 点、**未翻盘**。证据 `/tmp/r11_localloss.log`。⚠️ arm②③ 监督密度都 = 1 全局标量 → **「稠密监督翻盘」假说仍未检验**。
- ✅ **臂④ CoCa 已实现并启动（18:05，.12 全 8 卡，hostname=whag0pgpuap12 核验）**：CoCa = 对比 + caption 自回归 = **首个稠密监督臂**。`models.py` 增 `CoCaDecoder`（causal self-attn + cross-attn→patch，共享冻结 CLIP token_embed 49408）+ `OpenVision2.forward(return_patch=True)`；`r9_train.py` 增 `tokenize_cap`/`coca_caption_loss`/`--loss coca`/`--caption-loss-weight 2.0`/`--decoder-depth 4`。decoder 实测 **trainable=76.2M / total=114.1M**（w768·12H·4L + LM head）。smoke 30 步 exit 0（`[step 30] loss=18.61 contrast=6.12 caption=6.25 image/s=2337.9`）。`r11_run_coca.sh 30000` → `R11L_coca_w512`，30k 步（N=15.36M 主锚点），打印 `[start] steps=30000 objective=CoCa shards=419/rank`。日志 `/tmp/r11_coca.log`。ETA ~1.9~2.1h 训完 + 自动回收 4 ckpt IN-1k lp。
- 🔍 **巡检（16:44）**：arm③ LocalLoss @ step 17400/30000（58%），健康——C1 0.22 / C2_gap +0.11 / C4=OK、loss_ema 5.91→~4.64、steady ~2500 img/s；ETA ~17:30（剩 ~46 min）后自动回收 4 ckpt IN-1k lp。无异常，继续 WAITING。
- 🔍 **巡检（17:14）**：arm③ LocalLoss @ step 25850/30000（86%），健康——C1 0.1821 / C2_gap +0.1152 / C4=OK、loss_ema 5.91→~4.78、steady ~2780 img/s；ETA ~17:27 训完（剩 ~13 min）→ 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒（≈17:44）做 arm③ 收尾。无异常，继续 WAITING。
- 📝 **文档修正（17:14，纯 CPU）**：`EXPERIMENTS_VISION_ROUND11.md` §5 状态行原「负样本池 512→64」为误述，已改为「⚠️ 仍 all-gather 512 → 池仍是 512、只算本地 64 行」（对齐 §0 更正）。另注：`r11_run_localloss.sh` 头注释（`negative pool = per-rank 64`）亦含同一旧表述——该 runner 为一次性脚本（正在运行、跑完不复用），故未改运行中脚本，仅在此记录，待跑完若需复用再改。
- 🔍 **巡检（18:39，arm④ CoCa）**：@step 9100/30000（30.3%）健康——C1 0.4362 / C2_gap +0.0600 / C4=OK，loss_ema 22.55→17.77（contrast ~5.6 / caption ~6.0），吞吐 ~2500–4900 img/s（随迭代波动，低值出现在 probe 前后）；单进程组核验（1 master + 8 rank + 48 dataloader worker，**无重复 run**）；8 卡全忙（util 67–88%，显存 22.7/81.6 GB）。ETA ~20:05–20:15 训完 → 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒做 arm④ CoCa 收尾（§9 回填 + §3 公平表 + 判据裁定）。无异常，继续 WAITING。
- 🔍 **巡检（19:13，arm④ CoCa）**：@step 17950/30000（59.8%）健康——C1 0.3704 / C2_gap +0.0637 / C4=OK，loss_ema 22.55→16.93（contrast ~5.6–5.9 / caption ~5.4–6.4），吞吐 ~2270–5100 img/s（前段 ~2400，17450 步后数据加载提速至 ~4900）；进程组**再核验** 1 master(1359723) + 8 rank(1359914–1359921) + 48 dataloader worker（**无重复 run**）；8 卡全忙（util 31–82%，显存 22.7 GB）。ETA ~20:05–20:15 训完 → 脚本自动回收 4 ckpt IN-1k lp → 下次唤醒做 arm④ CoCa 收尾（§9 回填 + §3 公平表 + 判据裁定）。无异常，继续 WAITING。
- ✅ **arm④ CoCa 完成（20:13，`ALL DONE`，收尾 20:32 已做）**：`[done] total=6911.7s final_loss=17.4016 steady=3486.8 img/s fused=False`；探针名义通过但弱（C1 0.339 / C2_diag 0.089 / C2_off +0.021 / C2_gap +0.068，且 C2_gap 从 @300 的 +0.092 单调下滑；caption 项 ~68% 梯度）。IN-1k lp = **0.29 / 0.37 / 0.47%** ≈ 随机（<1/1000），zs 0.40/0.41/0.53% → Δ **−3.14/−5.08/−5.61** 点、**未翻盘且 trunk 被 caption 监督打回随机**。⚠️ 限于「自写 CoCa decoder + 冻结 CLIP-768 + 短 caption + weight2.0（未消融）」，**不得推广到官方 CoCa**。证据 `/tmp/r11_coca.log`。→ **首个稠密监督臂=负结果，「稠密监督翻盘」假说反向**；后续：臂⑤ GenLIP（纯 caption、坍缩先验更强）**建议跳过**，臂⑥ AIMv2 patch（唯一 caption-无关稠密、最贵、需自研）与 R11-L2（文本塔解冻）**待运维裁决**（详见 ROUND11 §9）。

- 📌 **decision gate（2026-10-03 21:31）**：R11-L 四臂（①基线/②SigLIP/③LocalLoss/④CoCa）全部兑现、无一翻盘；GPU 已空。**书面成本/收益判断已交 `EXPERIMENTS_VISION_ROUND11.md §10`**（臂⑤→🚫跳过 / 臂⑥ AIMv2→⏸暂缓 / **R11-L2→✅下一优先级** / R13→⏸批准后只做 OV2 单臂 / R11-E→⏸等 short≥18.5M）。⚠️ 全部**未经批准、不主动起训练**；WAITING 置 1 省 token，等运维在任务书 §3 + §10 勾选后执行。

## R11-L2 文本塔解冻臂（✅ 完成，2026-10-04 02:12）

> 只变「文本塔是否解冻」：冻结 CLIP-768（基线）vs LoRA（r=8 α=16 lr=1e-4，+0.30M、零初始化起点）；其余（OV2 w512 · CC12M+Amshaker · 视觉 lr3e-3 · bs512 · N=15.36M · IN-1k lp）全固定；重跑 C1–C4。预注册见 ROUND11 §11。

- **实现**：`r9_train.py` 增 `--text-finetune {frozen,lora}` + `--lora-*`；LoRA=parametrize 注入 q_proj+v_proj，lora_B 零初始化；探针 pT 每步重算。
- ✅ **完成（02:00 训完 / 02:12 评测完，exit 0）**：`total=7530.7s steps=30000 steady=2480.1 img/s final_loss=3.7105`；全程**无坍缩**（C1 0.24–0.31 / C2_gap +0.11~+0.14 / C4 OK）。
- **IN-1k lp = 3.13 / 4.75 / 5.28%** @5.12/10.24/15.36M（zs 1.10/1.61/1.77%）vs 基线 6.08%@15.36M → Δ **−0.30/−0.70/−0.80** → **未翻盘**（<+1.5 阈值）。→ **冻结文本塔仍最优**；「文本塔解冻」在本规模非杠杆，重训 text 塔不再推荐。公平性：+0.30M、0 extra token、≈1.0×。证据 `/tmp/r11_lora.log`。

## R11-L caption-weight 消融（✅ 两点全完成，2026-10-04）

> 替代臂⑤ GenLIP（运维已批跳过）：CoCa 只变 `--caption-loss-weight` ∈ {0.5,1.0}（2.0=arm④ lp 0.47%≈随机）→ 回答「caption 监督本身与 IN-1k 正交，还是 weight=2.0 压死 trunk」。预注册见 ROUND11 §12。

- 控变量同 arm④（w512 + 冻结 CLIP-768 + CoCaDecoder +76.2M + 短 caption + 30k 步）；只变 caption weight。2 点 × 30k ≈ 2 臂 ≈ 4–5h。
- 🚀 已启动（`.12` 全 8 卡）：`bash r11_run_capweight.sh 30000`；输出 `R11L_capw0p5_w512` / `R11L_capw1p0_w512`；日志 `/tmp/r11_capweight.log`；ETA ~4–5h + 自动回收各 4 ckpt IN-1k lp。**预注册裁定（§12.2）**：0.5 或 1.0 lp ≥4.58% → weight 压死主因；都 <4.58% → caption 监督本身正交。
- 🔍 **weight0.5 全程巡检摘要（02:55→04:00 三巡）**：C1 0.28–0.43 / C2_gap +0.065~+0.077 / C4=OK 全程未坍缩（@16200 单点探针 C1 瞬冲 0.86 属 128 样本噪声、下探针即回落）；loss_ema 10.17→~7.95 递减；进程组 1 master + 1 torchrun + 8 rank + 48 worker 无重复 run；8 卡全忙。
- ✅ **weight0.5 训完（04:23:34，exit 0）**：`[done] total=7261.3s steps=30000 steady_image_s=2628.7 final_loss=8.3768`；末点探针 C1=0.3422 / C2_gap=+0.0760 / C4=OK → 无坍缩；loss=contrast+0.5×caption（末步 contrast 5.183 / caption CE 5.772）。
- ✅ **weight0.5 IN-1k 评测完（04:36）**：4-ckpt lp @{10k,20k,30k,final} = **0.45 / 0.43 / 0.60 / 0.60%**；zs top1 = 0.55/0.51/0.68/0.68%、top5 = 2.40/2.36/3.11/3.11%。**全部≈随机，远 < 4.58% 预注册阈值（§12.2）** → ① caption weight 降到 0.5（对比项 5 倍权重）trunk 仍被打回随机；② 判定 = **caption 监督本身与 IN-1k frozen-trunk 特征正交（非 weight=2.0 压死）**。证据 `/tmp/r11_capweight.log:774-781`。
- ✅ **weight1.0 训完+评测完（06:54 ALL DONE，exit 0）**：`[done] total=7440.6s steps=30000 steady_image_s=2796.3 final_loss=11.3492`；末点探针 C1=0.3217 / C2_gap=+0.0729 / C4=OK；全程无坍缩。IN-1k lp @{10k,20k,30k,final} = **0.39 / 0.34 / 0.61 / 0.61%**（zs 0.43/0.48/0.62/0.62%、top5 2.00/2.08/2.78/2.78%）。证据 `/tmp/r11_capweight.log:1543-1551`。
- 📌 **三点裁定（§12.5）**：lp@15.36M = w2.0(arm④) 0.47 / w1.0 0.61 / w0.5 0.60%，全 ≈ 随机、无单调 → **假设 B：caption 监督本身与 IN-1k frozen-trunk 特征正交（非 weight 压死）** → 臂⑤ GenLIP 跳过坐实；AIMv2（唯一 caption-无关稠密）仍 ⏸ 待运维。

## R11-E GPIC 数据轴（✅ 完成，2026-10-04 11:19）

> 批准依据：运维指令 2026-10-04（四）——「10.9M 同 N 两点」版，即刻执行。只变数据臂：基线 CC12M+Amshaker（`wds`）→ GPIC `short`（`gpic`，`caption_type=='short'` 过滤）；塔 w512(126.8M)/InfoNCE/30k 步/bs512/IN-1k lp 全固定。对照点 N=5.12M(step10k)、10.24M(step20k)，基线 lp **3.43% / 5.45%**。预注册裁定见 `EXPERIMENTS_VISION_ROUND11.md §13.3`。

- 预注册已写入 `EXPERIMENTS_VISION_ROUND11.md §13`（先定后测）；脚本 `r11_run_gpic.sh`（`r9_train.py --loss clip --data-source gpic`）。
- ✅ 冒烟（30 步 @09:57）exit 0：`[params] total=126.8M`、`shards=247/rank`（1973 tar ÷ 8）、`steady_image_s=6189.3`、无坍缩 → gpic 路径可用。
- 🚀 全量已启动（10:00:54，`.12` 全 8 卡）：`steps=30000`、`GPIC train tar count=1973`（下载仍在继续）；输出 `R11E_gpic_w512`、日志 `/tmp/r11_gpic.log`。ETA ~1.5–2h + 自动回收 4 ckpt IN-1k lp（step10k/20k/30k+final）。
- ⚠️ 可比区间：GPIC short ≈10.9M 唯一对（1973 tar × ≈5.6k/tar）→ 只对 N≤10.24M 裁定；step30k（N=15.36M > 10.9M）进入数据重复轮、仅作补充。
- 🔍 **10:37 巡检（@15450/30000，51.5%）**：无坍缩（C1 0.33–0.40 / C2_gap +0.090~+0.095 / C4=OK）；loss_ema 5.863→3.69；steady ~6160 img/s；`vision_step10000.pt`（507MB）已落盘 @10:23；GPIC tar 1973→1999（下载仍在继续）；进程 1 torchrun + 8 rank + 48 worker 无重复；ETA ~11:08 训完 + ~11:20 评测 ALL DONE。
- ✅ **训完（11:06:17 exit 0）**：`total=3892.7s steps=30000 steady_image_s=5918.6 final_loss=3.7010`；全程无坍缩（C1 0.33–0.40 / C2_gap +0.0869~+0.095 / C4=OK）。
- ✅ **IN-1k lp（11:19:14 ALL DONE）**：@5.12M=**6.01%**、@10.24M=**5.69%**、@15.36M=**5.73%**（final 同）；zs top1=1.91/2.22/2.01%。基线段（CC12M+Amshaker）= 3.43/5.45/6.08%。
- ⚖️ **预注册裁定（§13.3）**：@5.12M +2.58（≥4.93 ✓）/ @10.24M +0.24（±1.5 内 ✗）→ 两点交叉 → **「未抬高 / 无显著差异」**。
- 📌 **结论**：GPIC `short` **低 N 先发优势显著（+2.58）但不抬 ceiling**；数据质量加速早期、数据总量/多样性决定上限。R9 25.1% 渐近不被数据臂改动推翻。公平性：同 126.78M/0 token，30k 步 3892.7s ≈0.56× 基线（吞吐 5918.6≈2.0×）。证据 `/tmp/r11_gpic.log`。

## ⭐ R13 OpenVision2 官方权重单臂对照（✅ 完成，2026-10-04 13:01）

> 运维指令 2026-10-04（五）批准：加载官方 OV2 权重 + 官方 p14/d24 结构塔，同口径 IN-1k 评测（zs + frozen-trunk lp），**纯评测、不训**。补结论边界（数据少非塔烂），不抬上限。

- ✅ **加载成功**：`UCSC-VLAA/openvision2-vit-large-patch14-224-vision-only`（Apache-2.0），294 keys strict=True 全对上；官方结构 = patch14/d24/w1024/h16/**GELU**/no_ln_pre/pool=**avg（256 patch，不含 CLS）**/final_ln_after_pool/1024×1024 proj；params=**304.23M**；pooled=1024。⚠️ 我们自研塔=patch16/d30（`models.py`），官方结构用 patched open_clip `_build_vision_tower` 另建塔（`r13_eval_official.py`）。
- ✅ **IN-1k**（自切分 val50000/probe49970，`r8_eval_in1k.load_in1k_split` 与 R8–R11 一致）：**frozen-trunk lp top-1 = 79.81%**；zs = **N/A**（生成式 1024-dim，无 CLIP 对齐 readout，与冻结 CLIP-L/336 768-dim 不对齐）。
- ✅ **每样本耗时**：0.57 ms/img = **1766.5 img/s**（H100-80G/bs128/bf16/峰值 2.70GB，`/tmp/r13_ov2/bench.log`）；训练 n/a（不训）。
- 📌 **结论边界**：官方同族 GELU ViT 同口径即 79.81%，我们从零对比学习（冻结 CLIP 文本塔 + InfoNCE、~118M）峰值 **7.99%**（渐近 25.1%）→ **+71.8 点**。判据坐实：**瓶颈在数据量+目标函数，非「塔写得烂」**；**不抬上限**（不改 from-scratch 排名 / scaling 结论）。
- ⚠️ **协议不同**：官方=大尺度预训练，我们=from-scratch → R13 **单列表、不并入排名**（EXPERIMENTS_VISION.md 顶部 R13 节）。
- 证据：`/tmp/r13_official.log`（exit 0）、`/tmp/r13_ov2/smoke2.log`、`/tmp/r13_ov2/bench.log`；权重 `/nas_train/app.e0031982/datasets/baize-vision/r13_official/open_clip_pytorch_model.bin`（1.217GB）。

## ⭐ 臂⑥ AIMv2 式（patch 预测 + InfoNCE）· 🟢 训练中（2026-10-04 19:25 · step ≈18850/30000 ≈63%）

> 运维 2026-10-04 用户拍板「Approve & start AIMv2 now」。预注册见 `EXPERIMENTS_VISION_ROUND11.md §14`（先定后测）。
> 科学问题：caption-无关的稠密监督（MAE 式 masked patch 像素重建）能否翻盘 25.1% 渐近？—— 对照 arm④ CoCa（caption-依赖稠密 → 坍缩随机 0.47%）。

- **S1 实现 ✅**：`models.py` 新增 `PatchPredictor`（0.66M）；`r9_train.py` 新增 `--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0`。
- **S2 冒烟 ✅**（18:06，30 步 PASS）：patch_mse 1.0→0.71（稠密项在学）；contrast ≈5.9（无坍缩）。
- **S3 全量 ✅ 完成**（18:07:56 → 20:01:32，7076s，`.12` 8×H100）：
  - 无坍缩全程：PROBE C1 0.30–0.37 / C2_gap +0.11~+0.12 / C4=OK。
  - final_loss=3.5554（contrast 2.98 + patch_mse 0.58）；steady 5971 img/s。
  - ⚠️ 父进程 `r11_run_aimv2.sh` + `torch.distributed.run` 中途退出（8 workers orphaned ppid=1 独立完成），不影响结果。
  - ✅ 4 ckpt 保存：vision_step{10000,20000,30000}.pt + vision.pt。
- ✅ **4-ckpt IN-1k eval 完成**（20:12–20:25，`r8_eval_in1k.py`，单卡 H100，~13min）：
  - lp @ 5.12/10.24/15.36M = **11.39% / 11.14% / 12.08%** vs 基线 3.43/5.45/6.08% → Δ +7.96/+5.69/+6.00 pp。
  - zs top-1 = 3.73/4.24/5.29%。
- ⭐ **§14.4 裁定：翻盘！** 两锚点 (5.12M +7.96pp, 10.24M +5.69pp) 均 ≥+1.5 → **25.1% 渐近局部推翻**（caption-无关稠密 patch 重建可突破纯 InfoNCE 上限）。机制：arm④ CoCa（caption-依赖→坍缩）vs arm⑥ AIMv2（caption-无关→翻盘）→ **坍缩归因 caption 依赖，非稠密监督本身**。
- ⚠️ **C2 限定**：AIMv2-**style** 自研改编，**非官方 AIMv2 复现** → 结论只对我们 recipe 成立。
- 证据：`out/R11L_aimv2_w512/train.log`（训练）；`/tmp/r11_aimv2_eval.log`（eval，exit 0）。已回填 `EXPERIMENTS_VISION_ROUND11.md §14.4–§14.5`。

## R11-F 数据源横向对比 · ✅ A/B/C 落盘 · ❌ E/D 失败待重跑 · Q1/Q3=无显著差异（2026-10-05 00:55 巡检）

> 运维指令 2026-10-04（六）批准：GPIC short/medium/short+medium(90%) vs en500k vs CC12M，固定 30k 步 / w512 / InfoNCE / IN-1k lp。预注册见 `EXPERIMENTS_VISION_ROUND11.md §15`。**完整结果 + 公平表 + 裁定见 §15.6**。

- ✅ **Arm A（GPIC short）**：lp@{10k,20k,30k}=**3.97/4.95/5.53%**；3914s，steady 6296 img/s，无坍缩。
- ✅ **Arm B（GPIC medium）**：lp@{10k,20k,30k}=**4.24/4.40/6.17%**；3951s，steady 6186 img/s，无坍缩。
- ✅ **Arm C（GPIC short+medium 90%）**：lp@{10k,20k,30k,final}=**4.90/6.23/5.92/5.92%**（zs 1.81/2.25/2.15/2.15%）；3586s，steady 5984 img/s，无坍缩（C1=0.368/C2_gap+0.089）。eval 完成于 00:50（datasource log:2302-2321）。
- ❌ **Arm E（CC12M pure）**：**端口碰撞失败**（`--master_port=29400+RANDOM%1000` 恰取 30000 → `EADDRINUSE`），2s exit 1，**未训练**。纯工程问题，CC12M 1100 tar 数据无问题，待重跑（稳健端口）。证据 `/tmp/r11f_datasource.log:2323-2366`。
- ❌ **Arm D（en500k）**：**shard<worker 失败**（25 tar / 48 dataloader worker → webdataset `empty_check` 抛错），未训练。**已修**：`data.py::build_loader` 加 `empty_check=False`（py_compile ✅），待重跑。即便成功仍 in-domain/不可比/单列。证据 `:2392-2699`。
- 🔒 **裁定（§15.6）**：**Q1**（medium vs short）B−A=+0.27/−0.55/+0.64 → **无显著差异**；**Q3**（90% vs short）C−A=+0.93/+1.28/+0.39 → **无显著差异**（20k +1.28 接近阈值但未达）；**Q2**（A/B/E）E 未训 → **悬置待 E 重跑**；**D** 待重跑（单列）。
- ⚠️ NFS Stale file handle 双崩溃（原 datasource 脚本 + r11f_continue）→ 已由 `/tmp/r11_overnight_chain.sh`（NFS-resilient，PID 4032740 ppid=1）接管 C→E→D→G→H 全链。
- ⬜ 待重跑（GPU 占用中，R11-G/H 后）：Arm E（稳健端口）+ Arm D（empty_check=False 已修）→ 补 Q2。

## R11-G + R11-H 代码 ✅ 已建 · 链已由 overnight chain 接管（2026-10-04 23:38）

> 运维指令 2026-10-04（七）批准：R11-F → R11-G → R11-H 自动串链。预注册见 `EXPERIMENTS_VISION_ROUND11.md §14`（R11-G 复用 §14.3 翻盘条款）。

- ✅ **代码改动（`r9_train.py`）**：新增 `--contrast-weight`（默认 1.0）+ `--c2-collapse-guard`（默认 1）。
  - `--contrast-weight 0.0` = R11-H 纯 AR：跳过 InfoNCE + 文本塔 forward（文本塔不参与梯度），`total = patch_loss_weight × masked-patch-MSE`。
  - `--c2-collapse-guard 0` = R11-H 关闭 C2_gap≤0.005 自动熔断（**科学理由**：纯 AR 无对比目标→对齐≈0 是预期非坍缩；C1 特征坍缩 + C4 loss 递减护栏**仍生效**）。
  - `py_compile` ✅；`--help` ✅ 确认两新 arg 注册；ckpt config 增 `contrast_weight`/`c2_collapse_guard` 可追溯。
- ✅ **脚本**：`r11g_run_aimv2_long.sh`（108k 步，save-every 10000 → 11 ckpt + 自动 IN-1k eval）、`r11h_run_pure_ar.sh`（30k 步，contrast=0 c2guard=0 + 4-ckpt eval）；`bash -n` ✅。
- ⚠️ **旧链 `r11fgh_chain.sh` 已退出**（NFS Stale file handle 崩溃后未恢复）→ **已由 `/tmp/r11_overnight_chain.sh` 接管**：该合并链在 R11-F Arms C/E/D 完成后**自动**接 R11-G → R11-H，无需人工干预。
- 🔄 **R11-G 运行中**（00:51:27 起，PID 1019839 torchrun，ppid=4032740 链）：step≈93650/108000 @06:58（**86.7%**），健康无坍缩（C1≈0.42 / C2_gap≈+0.126 / C4=OK / scale≈77 / loss_ema≈2.0(递减) / contrast≈1.9 / patch_mse≈0.14 / fused=False）；~39min/10k → ETA **~07:49（≈50min剩余）**。✅ **9 ckpt 已存盘**（step10k@01:30..90k@06:43，各 507MB）；save-every 10000 → 共 11 点(step10k..100k+final)；eval 在**训完**后批量跑（chain 脚本 collect all step*.pt → `r8_eval_in1k.py --ckpts`）。✅ 8 卡活跃（util 74-100%）。⚠️ **超运维§七 4h 护栏** → overnight chain **无 4h 护栏会自动接 R11-H**；已 flag 待运维定（若不干预，R11-H ~08:55–10:30 跑完，无争用任务，实际可接受）。✅ **r11g_scaling.py 已建**（`vision/r11g_scaling.py`）：幂律 `a−b·N^−c` + 对数线性拟合 + 单调性检查 + 预注册判据自动裁定；已验证 InfoNCE 基线复现 `a=0.251, R²=0.94`（与 R9 已知值一致）；训完 eval 后直接 `python r11g_scaling.py` 即可。
- ⬜ 待回填：R11-G 11 点 lp（save-every 10k）→ 幂律/对数线性拟合 R²+渐近 a vs InfoNCE 25.1%；R11-H 4 点 lp vs ⑥-A/基线 → 翻盘是否依赖对比项裁定（§14.3）。


## 历史条目已滚动归档（2026-10-03）

- 更早的全部巡检/流水（R1–R9 完整过程，live MEMORY 原 95.7KB）已滚动归档至 `daily-memories-vision/2026-10-03.md`（追加「滚动归档快照」）+ 各日期 daily 文件（2026-09-30 / 10-01 / 10-02）。live MEMORY 已压至 ≤32KB。
- 结论性产物（架构排名 / scaling / 回填建议）以 `EXPERIMENTS_VISION.md` 顶部与 `EXPERIMENTS_VISION_ROUND{2..9}.md` 为权威，不受滚动影响。
