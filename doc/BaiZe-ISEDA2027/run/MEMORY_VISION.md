# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

> 🔄 **ArmC 训练监控中 · wake #156（2026-10-18 22:0x）**：用户直令「开启 ArmC」+ 追加令「wd 0.1→0.01」⇒ **ArmC = 两个变量**（min_lr 1e-4→1e-5 + wd 0.1→0.01），非单变量消融，报告须如实披露。①训练✅运行中（wake #153 启动，setsid PID 4154284）：复制 run_armB_openclip.sh→run_armC_openclip.sh（仅改 OUT=armC_20261018_*/--min-lr 1e-5/--wd 0.01，.py 复用 armB_aimv2_openclip.py）；8 DDP worker，log 判据行 `lr=0.001 warmup=2000 cos->min_lr=1e-05 steps=57250 wd=0.01` ✓（注：每步打印前缀仍为 `[ArmB]`，因 .py 复用硬编码，output_dir 已确认指向 armC_20261018_*，非误跑）；**step 12580/57250(22.0%)**，loss~0.3-0.5(硬分片抖动非坍缩)，C1~0.61 正常振荡，0.86 it/s 稳态，8 卡 96-100%@50.5GB peak 50.4GB 无 OOM，grep error/nan/oom=0，**ckpt@10000 已存**(open_clip_state_dict 598MB+latest.pt+predictor.pt+config.json)；ETA~14.4h→约 10-19 12:35 训完。②ProtB 脚本 run_armC_protb_eval.sh ✅就绪（待训完起）。⏳ ③MLLM 三阶段 + ④12集 待训完串行。**WAITING=1**（ArmC 训练运行中）。
 > 📦 2026-10-18 16:38–17:05（wake #152: ArmB→MLLM 12集评测DONE）已归档 → daily-memories-vision/2026-10-18.md；**结论**：ArmB 平均(除MME)=26.10% vs ④-4ep 25.68% Δ+0.42pp，裁定**不可分辨(边界值)**；产物 report_vision_armB_mllm_stage4_zh.html + EXPERIMENTS_VISION.md§12。
 > 📦 2026-10-18 15:12（wake #151 Stage-2 DONE+切ArmB768塔+12集首跑启动）已归档 → daily-memories-vision/2026-10-18.md；**结论**：Stage-2 DONE(15.3min,loss1.4779)；lmms-eval加vision_backend开关；ai2d冒烟PASS；12集首跑@15:12启动(后证实FAILED,见#152)。
 > 📦 2026-10-18 08:25~13:53（wake #146~#150: ArmB训完57250步+ProtB评测+Stage-1 DONE+Stage-1.5 DONE 86.1min+Stage-2启动）已归档 → daily-memories-vision/2026-10-18.md。
 > 📦 2026-10-18 00:50~06:5x（wake #141~#145: ArmB训练监控 step35440→53740→57250健康,0.86-0.87 it/s,07:55训完）已归档 → daily-memories-vision/2026-10-18.md。
 > 📦 2026-10-17 23:37（wake #140: ArmB step31480(55%)健康,ETA~07:50 10-18）已归档 → daily-memories-vision/2026-10-17.md。
> 📦 2026-10-17 21:1x~19:5x（🔄 ArmB 监控 · wake #136~#139）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step15960→27540 健康, 0.85-0.87 it/s, ckpt@20000+10000已存, P1 ArmA 报告交付, ETA~08:00 10-18。
> 📦 2026-10-17 14:5x~17:27（🔄 ArmB 监控 · wake #133~#135）已归档 → daily-memories-vision/2026-10-17.md；**结论**：ArmB step4540→12120 健康, P1 ArmA 中文报告交付(commit 2f15f88e), 0.86 it/s 稳态, checkpoint_10000 已存。
>
> 📦 2026-10-17 13:3x（🔄 ArmB 改 4 epoch 重启 · wake #132）已归档；**结论**：4-epoch run(steps=57250)由 wake #132 启动(PID 1203148)，wake #133 确认健康运行中(step 4540)。
>
> 📦 2026-10-17 09:1x~12:4x（wake #128~#131: ArmA 训练完成154500步 + ProtB lp=58.03±0.02%/5-NN=53.98% + Stage(iv)报告闭环(da8e9cd1) + ArmB 3-epoch 启动后被 #132 改 4-epoch）已归档 → daily-memories-vision/2026-10-17.md。
>
> 📦 **改动清单 + 10-14~16 全天流水**（wake #106~#128, ArmA 起训/12集 eval/Stage-1/1.5/2/open_clip wrapper）已归档 → daily-memories-vision/2026-10-{14,15,16}.md + ARCHIVE_OPERATOR_VISION.md；**结论**：✅ ArmA 全链路完成, 改动清单(LPT/workers/cudnn/fused)已落地, 配方不变。
> ✅ **④-4ep 基线（COMPLETE）**: ProtB 67.05±0.02% / ProtA 56.70% / zs 40.64%/72.64% / k-NN 42.35%. final_loss=0.0805, C1=0.5932, 748,404 steps, 60,545s. VERDICT: MODERATE, DIMINISHING. 详见 EXPERIMENTS_VISION.md §9.5/§9.7.
> 📦 ④-2ep / V2 Muon / V3 / ② probe / ④-4ep评测（2026-10-11~13）已归档 → daily-memories-vision/2026-10-14.md + ARCHIVE_OPERATOR_VISION.md；**结论**：V2 Muon 坍缩❌；V3 不可分辨；② probe=ceiling；④-2ep MODERATE；④-4ep 67.05% 递减确认。
> ✅ **③ 参照系说明** in `EXPERIMENTS_VISION.md §8.3`: BaiZe internal protocol labeling rules, 不可比原因逐条.

| 字段 | 值 |
|:---|:---|
| PHASE | 🔄 **ArmC 训练监控（wake #156, .12 8卡独占）**。用户直令 ArmC = min_lr 1e-4→1e-5 + wd 0.1→0.01（**两变量，非单变量消融**）。①训练✅运行中(step 12580/57250=22.0%, 0.86it/s 稳态, 8卡96-100%@50.5GB peak50.4GB, log lr=1e-3/min_lr=1e-5/wd=0.01 ✓, C1~0.61 正常, ckpt@10000已存, ETA~14.4h→~10-19 12:35). ②ProtB 脚本✅就绪(待训完). ③MLLM+④12集 待串行. ArmB 全链路✅(12集26.10% 不可分辨). **WAITING=1**（ArmC 训练运行中）。 || ERROR_COUNT | 20（同前） |
| BUDGET_USED | ~999 GPU·h (V3 ~106, ② ~1, ④-2ep ~80, ④-4ep ~134 incl. eval) |
| 更新 | **2026-10-18 22:09 (wake #156)**: 🔄ArmC 训练监控健康。step 12580/57250(22.0%), loss~0.3-0.5(硬分片抖动非坍缩), C1~0.61(正常振荡), lr=9.13e-04(cosine, warmup已过), 0.86it/s, 8×H100 96-100%/50.5GB peak50.4GB 无OOM, t=244min(4.06h)。✅log 判据行 lr=1e-3 cos->min_lr=1e-05 wd=0.01 ✓(两变量正确)；✅grep error/nan/oom/traceback=0；✅ckpt@10000 已存(open_clip_state_dict 598MB+latest.pt+predictor.pt+config.json, 21:22)；✅ArmB OUT dir 未被触碰(ckpt 10-18 07:54 完好)；✅run_armC_protb_eval.sh 就绪(待训完)；⚠️每步打印前缀为 `[ArmB]`(.py 复用硬编码), output_dir 已确认指向 armC_20261018_*, 非误跑。ETA (57250−12580)/0.86≈14.4h→~10-19 12:35；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒~10-19 17:00 全链路。下一步: 监控→训完 run_armC_protb_eval.sh→MLLM三阶段→12集→报告。 || WINNER | OpenVision2（R8 六架构四指标第一；R9/R10 证「塔越小越高」，w512=126.8M 是既有对比基线，不改架构排名） |

### 评测耗时归因（2026-10-15）

| 环节 | 耗时(估) | 说明 |
|:--|:--|:--|
| 训练链 (Stage-1/1.5/2) | ~4h | Stage-1 2500步(~1.5h) + Stage-1.5 20000步(~2h) + Stage-2 3500步(0.26h) + gate check/smoke(~0.3h) |
| adapter 适配 (lmms-eval wrapper) | ~3h | `lmms_eval_baize_llava.py` 编写+调试(generate_until/loglikelihood/multi-GPU LOCAL_RANK/batch_size) |
| 数据通道 (HF 下载) | ~1.5h | proxy 直连 hf.co；ai2d smoke 77MB OK；17 集首次下载是大头(预建缓存中) |
| 磁盘满崩溃 + 修复 | ~0.5h | limit50 8卡同时写 `/home`(47G)→崩；修复=迁 HF_HOME→/nas_env + 单进程预建缓存 |
| git 推送阻塞 | ~6h | `.12` 直连 github 不通(无 proxy)→ 6h 推不上来(运维已配 git config http.proxy=92.23 修复) |
| generate 输出 bug | ~0.5h | 早期 ai2d 输出解析调试(`HF_TOKEN=hf_dummy` + adapter 输出格式) |
> 📦 「运维问答·下一步工作建议 · 2026-10-08③」（1-A~1-D / 2-A~2-E / 3 GPU空窗 / 4-A~4-E 论文）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：旧版下一步建议（w384/336 AIMv2、C1-lp 消融、Stage-iv 前置、论文补 Limitations），多数已被后续 ArmA/ArmB/ArmC 工作覆盖（④-4ep 67.05%、V2全量=ArmB 62.09%、MLLM=ArmB 12集 26.10%）。需要时再读。
> 📦 「运维问答·下一步工作建议 · 2026-10-10」（④epoch缩放 / V2全量 / MLLM前置 / 论文 / w384 / 336 / C1-lp 排序）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：④epoch→④-4ep(67.05% MODERATE/DIMINISHING)；V2全量→ArmB(62.09%)；MLLM前置→ArmB Stage-iv 完成(12集 26.10% 不可分辨)。需要时再读。




## R9 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND9.md）

- 阶段一：w512/w768/w1024 lp = 6.10/3.63/1.03% → 选 **w512（126.8M）**。阶段二：w512×108k=55.3M，lp 峰值 7.70%@51.2M。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 `acc=0.251−0.864·N^−0.090`（渐近 **25.1%**）；外推 20% 需 41 万亿样本 → **本地 ≈118M 上限够不到**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对 vs 我们 649× 少），非架构。

## R10 完成（converged）结论速查（权威详见 EXPERIMENTS_VISION_ROUND10.md）

- 2D 拟合（19 点 R²=0.980）：M 边际效应**全区间为负** ≈ −2.2 lp pp/参数翻倍 → 数据受限区间**加宽塔是负收益**。
- **w384@15.36M=7.99% 为全部宽度最高**；最优 M 仍在观测下界（71.5M）之下 → 无饱和点、更小塔持续更优。

## R14 官方仓库调研（✅ 全部完成，2026-10-03）

- CPU-only 源码普查，与 R10-③ denseM 训练并行。产物：`VISION_OFFICIAL_REPOS_SURVEY.md`（①目标②数据③config④结构差异⑤可复用资产⑥LICENSE⑦三清单）。
- ✅ 两个 ⭐⭐⭐ 仓库源码普查完成（上一 cycle）：**OpenVision**（JAX/TPU，官方 ViT-L/16 = w1024/d24/h16；文本 = BERT-128 + LLaMA3 dense caption + caption decoder + keep_ratio=0.35）；**ml-aim/AIMv2**（仅模型接口，无训练/损失/数据；LICENSE = Apple Sample Code，🔴 不可 COPY）。
- ✅ 第二阶段（本轮）全部核毕：
> 📦 [06:45 Oct08] weight-ratio 消融流水已归档 → daily-memories-vision/2026-10-11.md「Archived」节。**结论**：4臂无翻盘，1:1最优，contrast过高显著有害。
  - **OpenVision2 权重 = ✅ 已放出且真带 caption decoder**：HF `UCSC-VLAA/openvision2-vit-{so400m,large,huge,giant}-patch14-{224,336,384,448}-vision-only`；含 `caption_decoder.safetensors` + `text_decoder_config.json`（concat/prefix-LM，非 CoCa cross-attn）。🔑 官方 = **patch14/d24**，我们 = **patch16/d30**（models.py:170）→ R13 需另建官方结构塔才能 load。
  - **FastVLM** = ✅ `apple/ml-fastvlm`（FastViTHD 1024² conv-hybrid RepMixer）；LICENSE = Apple Sample Code（research-only，不可抄）。
  - **MambaEye** = ✅ `usingcolor/MambaEye`（MIT）：纯 Mamba2、**小模型监督分类**（非对比）；**MoE-ViE** = ✅ `facebookresearch/moe_vie`（CC BY-NC 4.0）：CLIP 风格 MoE-ViT，官方权重 HF；**iGVLM(AdaLN)/TuringViT** = 🚫 **未找到官方实现**（iGVLM 同名 IG-VLM 是视频QA；TuringViT 仅项目主页）。
- 关键产出（对 R13/R12）：官方 MoE-ViE/FastVLM/MambaEye/AIMv2 权重均可作「官方 vs 自研」对照标尺；OpenVision2 官方是 patch14/d24，需建官方结构塔。

## E1 GPIC 规模实测（✅ 完成，2026-10-03）

- 抽 **8 个 tar 均匀抽样**（index 0..1212）实测：**12,537 图文对/tar**（稳定 ±2%）→ **GPIC 全量 ≈ 100.3M**（证官方 100M 卡；旧「5 tar=86M」少计 png 作废）；**已下 1213/8000 tar ≈ 15.2M**。
- `caption_type` mix：short **45.0%** / medium 45.1% / long 9.0% / tag 1.0% → **可训练 short 子类：全量 ≈45M / 已下 ≈6.8M**。
- 🔑 **C1 口径定案**：R9 用过 18.5M / 盘上现有 ≈32M / 本地全量 ≈118M（动态、仍在下载）——与 `r9_scaling.py --local-cap-m default=118.0` 一致；R11-E「同 N」可比区间被压到 ≈6.8M（short 已下 < 18.5M），须如实说明。已回填 `VISION_ARCH_FRONTIER_2026.md §5`。

## R11-L / R11-L2 / caption-weight / R11-F / R11-G / R11-H / R12 / 3-epoch 全部完成

> 📦 以上全部已闭合实验（R11-L 四臂→R11-L2→caption-weight→R11-F→R11-G→R11-H→R12→3-epoch 续跑）的详细流水已滚动归档 → `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（**原文未改**）。**结论以 `EXPERIMENTS_VISION_ROUND11.md` + `EXPERIMENTS_VISION_ROUND12.md` 为权威。**

**一句话结论**：R11-L 四臂（SigLIP/LocalLoss/CoCa/基线）**无一翻盘**；R11-L2 文本塔解冻（LoRA）**未翻盘**（−0.80 pp）；caption-weight 三点消融 → **caption 监督与 IN-1k 正交**；R11-F 数据源横比 → GPIC short/medium/short+medium **无显著差异**；⭐ **R11-G AIMv2 长跑翻盘**（lp@55.3M=19.76% vs 基线 7.40%，R²=0.91，渐近 >>25.1%）；R11-H 纯 AR **无翻盘**（翻盘依赖对比项）；R12 全量 58.8M 1.05 epoch lp@61.4M=17.57%（< R11-G 同 N）；3-epoch 续跑 344k/176M lp=20.27%，35 点 scaling R²=0.94，非单调 7/34，a 撞上界不可定。

> 📦 [04:20 Oct12] 全量 1-epoch 耗时估算 + AIMv2 提速归因实测（bs/nw 扫描）已归档 → daily-memories-vision/2026-10-12.md「Archived from MEMORY_VISION.md」节。**结论**：bs=64 下数据/IO 受限（GPU util~70%），~5000 img/s 是 NFS 架构上限；1 epoch ≈ 5.2–9.1h。需要时再读。

## 本唤醒流水

> 📦 [Oct 13~14] 本唤醒流水旧条目（Wake #45~#84, 含 ArmC 监控/MLLM bridge/报告刷新/④-4ep eval/外部编码器, ~15条）已归档 → daily-memories-vision/2026-10-{13,14}.md。**关键结论**：ArmC 154500步完成(ProtB 68.25%), ④-4ep ProtB 67.05%, MLLM bridge 5/5 PASSED, 外部编码器 SigLIP2 87.46% 最高。需要时再读。
> 📦 10-06~10-12 早期流水（R12b/scaling/fair-rerun/V3/②probe/④-2ep/④-4ep, ~40条）已归档 → daily-memories-vision/2026-10-{06..12}.md。**关键结论**：E1fair vs E2fair Δlp=+0.17pp indistinguishable; ④-4ep ProtB 67.05% MODERATE/DIMINISHING; ④-2ep ProtB 65.37%。需要时再读。
> 📦 [Oct 16] 本唤醒流水旧条目（Wake #108~#115, 含 precache 监控/Part B 验收/limit50 abort/12集 eval 完成/keepalive, 5条）已归档 → daily-memories-vision/2026-10-16.md。**关键结论**：✅ Part B 三项验收全通过(ai2d=0.60)；✅ 12/12 benchmarks 全量 eval 完成(ai2d 60.04%/mmmu 42.89%/realworldqa 43.01%)；consolidated_12benchmarks.json 交付。需要时再读。
> 📦 [Oct16 20:50~23:1x] Wake #118~#120（ArmA 监控+效率专项落地）已归档 → daily-memories-vision/2026-10-16.md；**结论**：ArmA step21940 健康；效率优化一揽子落地(修前2.40→修后3.35 it/s +40%, util 95-100%全卡, 三项验收全达标)。
> 📦 [00:30~17:27 Oct17] Wake #121~#135 内联流水（ArmA 监控 step59480→103400 + ArmA 训完154500步/ProtB 58.03% + ArmB 起训 step4540→12120 + P1 ArmA 中文报告交付, 6条）已归档 → daily-memories-vision/2026-10-17.md。**关键结论**：ArmA 3.35-3.37 it/s 稳定训完, ProtB lp 58.03±0.02%/5-NN 53.98%, ArmB 4-epoch 起(PID 1203148→1203161), 0.86-0.89 it/s, 无 OOM/无错误。需要时再读。
- [18:39 Oct17] **Wake #136**: 🔄 **ArmB 训练监控** — step 15960/57250(27.9%), loss=0.53, 0.87 it/s, ETA~08:00 10-18。详见 daily-memories-vision/2026-10-17.md。
- [19:5x Oct17] **Wake #137**: 🔄 **ArmB 训练监控 + ✅ ProtB eval 脚本就绪** — git pull up to date，无新运维指令。✅ ArmB 4-epoch 训练健康: step **20520/57250(35.8%)**, loss=0.36(contr=0.33 patch=0.026), C1~0.72, lr=7.73e-4, **0.88 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=390min(6.5h)。✅ checkpoint_20000(@19:53)+10000+latest+open_clip_state_dict(598MB)+predictor+config。✅ **新建 `armB_protb_eval.py`(386行)+`run_armB_protb_eval.sh`** — CPU单测3/3 PASSED: open_clip_state_dict.pt(302keys)与latest.pt(308→302keys, predictor剥离)两条加载路径权重一致, visual=86.2M；复用ArmA ProtB口径(feature=projected, full IN-1k, SGD 90ep, seeds 0/1/2, 5-NN, OMP_NUM_THREADS=8修复)。ETA (57250−20520)/0.88≈**11.6h→~07:30 10-18**; +ProtB 1–2h⇒**~09:00 10-18**。下一步: 监控→训完`run_armB_protb_eval.sh`→报告。📦 体积：TASK=26.2KB / MEMORY=31.3KB。
- [21:1x Oct17] **Wake #138**: 🔄 **ArmB 训练监控** — git pull fast-forward(1 commit, personal-watch), 无新运维指令。✅ ArmB 4-epoch 训练健康: step **23680/57250(41.4%)**, loss=0.27(contr=0.245 patch=0.023), C1~0.78, lr=6.99e-4, **0.85 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=462min(7.7h)。ETA (57250−23680)/0.85≈**11.0h→~08:00 10-18**。📦 体积：TASK=26.9KB / MEMORY=30.3KB。
- [22:26 Oct17] **Wake #139**: 🔄 **ArmB 训练监控** — git pull up to date，无新运维指令。✅ ArmB 4-epoch 训练健康: step **27540/57250(48.1%)**, loss=0.32(contr=0.30 patch=0.022), C1~0.74(正常振荡 0.69–0.85), lr=6.03e-4, **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=533min(8.9h)。✅ checkpoint_10000+20000+latest+open_clip_state_dict(598MB)+predictor(4.7MB)+config.json 均在。ETA (57250−27540)/0.86≈**9.6h→~08:00 10-18**; +ProtB 1–2h⇒**~09:00–10:00 10-18**。下一步: 监控→训完`run_armB_protb_eval.sh`→报告。📦 体积：TASK=26.9KB / MEMORY=30.2KB（均<32KB）。
- [06:5x Oct18] **Wake #145**: 🔄 **ArmB 训练监控** — git pull up to date, 无新运维指令（顶部 12:4x kill+ArmB+ProtB 已执行）。✅ ArmB 4-epoch 训练健康: step **53740/57250(93.9%)**, loss~0.22(contr~0.20 patch~0.016, 硬分片抖动非坍缩), C1~0.82–0.90(正常), lr=1.09e-04(cosine→1e-4), **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=1039min(17.3h)。✅ ckpt@50000(@05:28)+40000+latest+open_clip_state_dict(598MB)+predictor+config 均在, next=final@57250。✅ grep error/nan/oom/traceback=**0**。✅ ProtB 脚本预检(OUT_DIR 对齐, 偏好 open_clip_state_dict.pt 已存在, OMP_NUM_THREADS=8)。ETA (57250−53740)/0.86≈**1.1h→~08:00 10-18**; +ProtB 1–2h⇒**~09:00–10:00 10-18**。下一步: 训完立即 .12 跑 `run_armB_protb_eval.sh`→armB 中文报告。📦 体积：TASK=26.2KB / MEMORY≈30.0KB（归档 #121~#135 内联→指针）。
- [11:2x Oct18] **Wake #148**: ✅ **Stage-1 ArmB 训完 + Stage-1.5 ArmB 启动** — Stage-1 DONE(2500步/6.7min, final loss4.5765, proj768→2560 8.52M)；Stage-1.5 启动(20000步, LoRA r=64+proj, ETA~12:48)。详见 daily-memories-vision/2026-10-18.md。
- [15:12 Oct18] **Wake #151**: ✅ **Stage-2 DONE + lmms-eval 切 ArmB768 塔 + 12集全量启动** — Stage-2 DONE(15.3min exit0 @14:10:09 final loss1.4779, ckpt `mllm_stage2_armB/step3500/`)。代码改动：`lmms_eval_baize_llava.py` 加 `vision_backend` 开关(armB→`create_baize_vitb16_768` 768d / baize_4ep→原512d)；`run_lmms_eval.py` 加 `--vision_backend/--ckpt/--stage2_base`(ArmB 独立结果目录 `mllm_eval_results_armB/`)；新增 `launch_12benchmarks_armB.sh`；`consolidate_12benchmarks.py` 加 `--results_dir`。✅ ai2d --limit5 冒烟 PASSED(768塔 strict load/LoRA merge/生成单字母答案/exact_match=0.40/img_feat 无NaN)。🔄 12集全量 @15:12:33 启动(8 GPU, batch32, 无limit, log→`/tmp/launch_12b_armB.log`, 结果→`mllm_eval_results_armB/`)。⚠️**mmmu_pro 首跑 exit=1**(MMMU-Pro 数据集未缓存+offline→ConnectionError；其余7集OK：mmmu_val exit0/realworldqa 0.4549 等)。**mmmu_pro 已用 online 模式重跑**(GPU1, PID613521, `HF_HUB_DOWNLOAD_TIMEOUT=120` 解 10s 读超时, 输出覆写 `eval_mmmu_pro.json`)。docvqa(GPU2)仍在跑。**下一唤醒务必：等 docvqa+mmmu_pro 都完成后重新 `consolidate_12benchmarks.py --results_dir mllm_eval_results_armB`**（主 launch 的 consolidate 时 mmmu_pro 可能仍缺）。ETA~3-5h。📦 体积：TASK=31.7KB / MEMORY≈31.2KB（均≤32KB）。
- [16:38–17:05 Oct18] **Wake #152**: ✅ **12集评测DONE + 报告** — 12集首跑FAILED(15:12→15:21, 只所4集, 根因=nas_env缓存缺MMStar/MME/blink/CountBench/MMMU_Pro+offline→整组GPU崩溃)。FIX: 改指/tmp缓存(全12集预缓存), 补跑8集16:38→16:42 exit=0。ArmB平均=26.10%, ␖=25.68%, Δ=+0.42pp。**裁定: 不可分辨(边界值)**。产物: report_vision_armB_mllm_stage4_zh.html + EXPERIMENTS_VISION.md§12。详见 daily-memories-vision/2026-10-18.md。
- [18:0x Oct18] **Wake #153**: 🚀 **ArmC 训练启动** — 用户直令「开启 ArmC」+追加「wd 0.1→0.01」⇒ ArmC=两变量(min_lr 1e-4→1e-5 + wd 0.1→0.01)。✅run_armC_openclip.sh(复制 ArmB, 仅改 OUT=armC_20261018_*/min_lr 1e-5/wd 0.01, .py 复用 armB_aimv2_openclip.py)；✅run_armC_protb_eval.sh 已备(ckpt→ArmC dir)。✅.12 8卡全空(4MiB/0%)→setsid 起 ArmC 训练：8 DDP worker, log 判据行 `lr=0.001 warmup=2000 cos->min_lr=1e-05 steps=57250 wd=0.01` ✓, step60/57250 loss 8.99↓ 0.73it/s 爬坡, 8卡100%@50.5GB peak50.3GB 无OOM/无error, LPT 0.0% imbalance 11350 shards。ETA~18.4h→约 10-19 12:00。📦 体积：TASK 36208→29653B(归档 P0 ArmB→MLLM + epoch-replay 两块→ARCHIVE) / MEMORY 31166B（均≤32KB）。下一步: 监控→训完 ProtB→MLLM→12集。
- [19:31 Oct18] **Wake #154**: 🔄 **ArmC 训练监控** — git pull up to date, 无新运维指令（顶部 17:1x ArmC 块为当前最高优先, ①训练已由 #153 启动）。✅ ArmC 训练健康: step **4600/57250(8.0%)**, loss~0.73(contr~0.68 patch~0.042, 硬分片抖动非坍缩), C1~0.19–0.50(早期振荡正常), lr=9.95e-04(warmup→1e-3), **0.89 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=86min。✅ log 判据行确认 `lr=1e-3 cos->min_lr=1e-05 wd=0.01` ✓（两变量正确）；✅ grep error/nan/oom/traceback=**0**；✅ diff 确认 run_armC_openclip.sh 仅改 OUT/min_lr/wd（无意外改动）；✅ ArmB OUT dir 未被触碰（ckpt 10-18 07:54 完好）；✅ run_armC_protb_eval.sh 就绪(待训完)；③④MLLM+12集 待串行。ETA (57250−4600)/0.86≈**16.5h→~10-19 12:00**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 16:30 全链路完成**。下一步: 监控→训完`run_armC_protb_eval.sh`→MLLM三阶段→12集→报告。📦 体积：TASK=28.95KB / MEMORY=31.58KB（均≤32KB，无需归档）。
- [20:52 Oct18] **Wake #155**: 🔄 **ArmC 训练监控 + 体积归档** — git pull up to date, 无新运维指令（顶部 17:1x ArmC 块为最高优先, ①训练已由 #153 启动）。✅ ArmC 训练健康: step **8600/57250(15.0%)**, loss~0.70(contr~0.66 patch~0.031, 硬分片抖动非坍缩), C1~0.51(正常振荡), lr=9.66e-04(warmup→1e-3), **0.86 it/s**(稳态), 8×H100 100%/50.5GB(peak=50.4GB 无OOM), t=166min(2.77h)。✅ log 判据行确认 `lr=1e-3 cos->min_lr=1e-05 wd=0.01` ✓（两变量正确）；✅ grep error/nan/oom/traceback=**0**；✅ ArmB OUT dir 未被触碰（ckpt 10-18 07:54 完好, open_clip_state_dict 598MB）；✅ ArmC OUT dir 存在但空（首 ckpt @10000, step 8600 未到, ~30min 后出现）；✅ run_armC_protb_eval.sh 就绪(待训完)。📦 体积：MEMORY 33534B(>32KB)→**归档两节「运维问答·下一步工作建议」(10-08③+10-10, 137行原文未改)→ARCHIVE_OPERATOR_VISION.md**→21618B / TASK=29653B（均≤32KB✓）。③④MLLM+12集 待串行。ETA (57250−8600)/0.86≈**15.7h→~10-19 12:30**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 17:00 全链路完成**。下一步: 监控→训完`run_armC_protb_eval.sh`→MLLM三阶段→12集→报告。
- [22:09 Oct18] **Wake #156**: 🔄 **ArmC 训练监控** — git pull(behind1, video线bc5d4def)→rebase autostash→up to date; 无新运维指令（顶部 17:1x ArmC 块为最高优先, ①训练已由 #153 启动）。✅ ArmC 训练健康: step **12580/57250(22.0%)**, loss~0.3-0.5(硬分片抖动非坍缩, 同 ArmB 模式), C1~0.61(正常振荡), lr=9.13e-04(cosine, warmup=2000 已过), **0.86 it/s**(稳态), 8×H100 96-100%/50.5GB(peak=50.4GB 无OOM), t=244min(4.06h)。✅ log 判据行确认 `lr=1e-3 cos->min_lr=1e-05 wd=0.01` ✓（两变量正确）；✅ grep error/nan/oom/traceback=**0**；✅ **ckpt@10000 已存**(21:22, open_clip_state_dict 598MB+latest.pt 1.8GB+predictor.pt+config.json)；✅ ArmB OUT dir 未被触碰（ckpt 10-18 07:54 完好）；✅ run_armC_protb_eval.sh 就绪(待训完)；⚠️每步打印前缀为 `[ArmB]`（.py 复用 armB_aimv2_openclip.py 硬编码），已核对 output_dir 指向 armC_20261018_aimv2_openclip_vitb16_224，**非误跑 ArmB**。③④MLLM+12集 待串行。ETA (57250−12580)/0.86≈**14.4h→~10-19 12:35**；+ProtB 1h+MLLM 1.8h+12集 1.5h⇒**~10-19 17:00 全链路完成**。下一步: 监控→训完`run_armC_protb_eval.sh`→MLLM三阶段→12集→报告。📦 体积：TASK≈29.7KB / MEMORY≈21.6KB（均≤32KB✓，无需归档）。






## 历史条目已滚动归档（2026-10-03 / 2026-10-06）

- 更早的全部巡检/流水（R1–R9 完整过程）已归档至 `daily-memories-vision/2026-10-03.md` + 各日期文件。
- R11-L→R12→3-epoch 续跑的详细流水已归档至 `daily-memories-vision/2026-10-06.md`「从 MEMORY_VISION.md 滚动归档」节（原文未改）。
- Wakes #47/#49/#50/#51（2026-10-13）已归档至 `daily-memories-vision/2026-10-13.md`（原文未改）。
- 结论性产物以 `EXPERIMENTS_VISION_ROUND{2..12}.md` + `EXPERIMENTS_VISION.md` 顶部为权威，不受滚动影响。
