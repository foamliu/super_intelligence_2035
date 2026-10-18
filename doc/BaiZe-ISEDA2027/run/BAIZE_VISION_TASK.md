# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 🆕 运维指令 · 2026-10-18 17:0x（🚀 **ArmC：只改 min_lr 的 4 阶段完整实验**）· 用户直令 · 最高优先

> 用户令：「vision：开启 ArmC。跟 ArmB 相比，只有一个变量：学习率。LR=1e-3，min_LR=1e-5。1.训练；2.评测 ProtB；3.MLLM 对齐；4.MLLM 12 集评测。」
> **ArmB 实际配置（已核对）**：open_clip ViT-B/16 224；AIMv2-style（InfoNCE 1.0 + masked patch MSE 1.0，mask 0.6）；GPIC 8000 + CC12M 1100 + Amshaker 2250 = 11,350 shards；GBS 8192/MBS 512/accum 2（OOM 回退 4096/256）；warmup 2000；4 epoch/**57,250 步**；AdamW wd0.1 betas(0.9,0.98)、bf16、grad_clip 1.0、seed 1234；save 10k/keep 2；**LR 1e-3 / min_lr 1e-4**。
> **ArmC = 只把 min_lr 1e-4 → 1e-5**；`--lr 1e-3`、warmup、4 epoch/57250、GBS/MBS、数据、目标、seed 全部不变。⚠️ 若发现 ArmB 实际值与上表不符，只允许改 LR/min_lr 到 **1e-3/1e-5**，其余照 ArmB 原值，并在回报里列 diff。

**① 训练 ArmC（串行第 1 步）**
- 复制 `run_armB_openclip.sh` → `run_armC_openclip.sh`，只改：`OUT=.../armC_aimv2_openclip_vitb16_224`、`--lr 1e-3 --min-lr 1e-5`；其余参数/脚本原样。
- `setsid bash run_armC_openclip.sh > /tmp/armC_openclip_train.log 2>&1 < /dev/null &`
- 判据：8 卡 100%；log 打印 `lr=1e-3 ... min_lr=1e-5`；57250 步；ckpt 10k/20k/…；ETA 参考 ArmB **~18.4h**。
- 🚫 不 resume ArmB、不覆盖 `armB_*` 目录、不改数据/目标/GBS/seed。

**② ProtB（训练完立即）**
- 复制 `run_armB_protb_eval.sh` → `run_armC_protb_eval.sh`，只把 ckpt 指向 `armC_.../open_clip_state_dict.pt`；3 seeds、同 Protocol B、同 IN-1k 1.28M/50k。
- 产出 `vision/armC_protb_vitb16_224_results.json`；报 lp/5-NN；对比 ArmB **62.093/58.102**、④-4ep **67.05**。

**③ MLLM 对齐（ProtB 完成后）**
- 复用 ArmB 三阶段脚本，只把视觉塔 ckpt 换成 ArmC、输出目录改 `*_armC`：
  - Stage-1：projector 768→2560，2500 步（ArmB 6.7min）
  - Stage-1.5：LoRA r=64/α128 + proj，20,000 步（ArmB 86min）
  - Stage-2：3500 步，LLaVA-NeXT-780k（ArmB 15.3min）
- 🚫 不改 LLaVA-OV1.5 配方/LoRA/数据/步数；只换塔。

**④ MLLM 12 集（对齐完成后）**
- 用 `lmms_eval` ArmC backend（新增 `vision_backend=armC` / `create_baize_vitb16_768` ArmC ckpt），`results_dir=mllm_eval_results_armC`，12 集同 ArmB：batch32、无 limit。
- 报平均（除 MME）+ 每集 Δ；对比 **ArmB 26.10%**、④-4ep 25.68%、RiCEViT 60.08%；沿用 ArmB 预注册判据（≥30% 强成功 / >24% 且 DocVQA/ChartQA/OCRBench 任一 +10pp 成功 / 22–26% 不可分辨 / ≤22% 失败），ArmC vs ArmB 的 Δ 只作描述，不事后改判据。
- 报告 `reports/report_vision_armC_mllm_stage4_zh.html` + `EXPERIMENTS_VISION.md §13` + MEMORY；commit `vision armC:`。

**⑤ 纪律**
- 严格串行：①→②→③→④；每步完成再下一步。
- 只有 LR/min_lr 是变量；其他任何差异都要在报告里列 diff 并说明。
- 不占 `.29`、不碰 data/pretrain/harness 线；`.12` 8 卡由 ArmC 独占。
- ETA：训练 ~18.4h + ProtB ~1h + MLLM 三阶段 ~1.8h + 12 集 ~1.5h ≈ **22–24h**。

### 🆕 运维指令 · 2026-10-18（🚀 **P0：`.12` 空档跑 ArmB → MLLM 三阶段 → lmms-eval 12 集**，用 open_clip 接口，对照 ④-4ep 基线）· 用户直令 · 最高优先

> **用户令（2026-10-18）**：「P0：.12 空档跑 ArmB→MLLM 三阶段 + 12 集」
> **目的（先讲清要回答什么）**：ArmB（86.2M, open_clip + AIMv2-style）接 LLaVA-OV1.5 三阶段后，**12 集能不能超过 ④-4ep 的 ≈24%**。这是"open_clip 接口 + 更好表征"能否兑现到 MLLM 下游的**唯一直接证据**。

**① 基线（必须写在报告里，不得改写）**
- ④-4ep（126.8M, w512, 224px）→ Stage-iv 三阶段 → lmms-eval 12 集：ai2d 60.04 / RealWorldQA 43.01 / MMMU 42.89 / Blink 38.52 / MMStar 26.81 / MMMU-Pro 23.12 / InfoVQA 16.58 / ChartQA 12.24 / CountBench 10.79 / DocVQA 7.41 / OCRBench 1.10 / MME 847.5（perc 596.75 + cog 250.71）；**平均（除 MME）≈ 24%**（`reports/report_vision_stage4_mllm_result_zh.html` §4/§6）。
- 官方 RiCEViT 同配方：平均 **60.08%**（上限参照，不作为本次判据）。
- ArmB：**ProtB lp 62.09±0.01% / 5-NN 58.10%**（ckpt = `…/armB_aimv2_openclip_vitb16_224/open_clip_state_dict.pt`）。

**② 预注册判据（先定后测，🚫 不许事后改）**
| 判定 | 条件 |
|:--|:--|
| **强成功** | 12 集平均（除 MME）**≥ 30%** |
| **成功** | 平均 **> 24%（基线）** 且 DocVQA/ChartQA/OCRBench **任一项 ≥ +10pp** |
| **不可分辨** | 平均 22%–26% |
| **失败** | 平均 **≤ 22%** |
- 另必须报：**MME 总分**与 **perc/cog 拆分**；每集与 ④-4ep 的 Δ 表。

**③ 前置（先做，任一不过就停并报 blocker）**
1. `.12` **8×H100 全空**（`nvidia-smi` 0 MiB、无 compute apps）；若被占用 ⇒ 报占用者与 ETA，**不抢**。
2. **ArmB → open_clip/LLaVA-OV 导出**：`run/vision/mllm_bridge/open_clip_vitb16_768.py`（注册 `baize-vitb16-768`，`encode_image → [B,196,768]`）+ `export_for_llava_ov.py`；**strict load 校验**（ArmB ckpt 是 `open_clip_state_dict.pt`，**无需**剥 `clip.` 前缀，那是 full ckpt 的处理）+ 打印 matched/missing/unexpected。
3. **projector 维度改口**：ArmB 输出 **768** 而非 ④-4ep 的 512 ⇒ 2 层 MLP projector 为 **768→2560**（不是 1024→2560、也不是 512→2560）。改完跑 `test_wrapper_cpu.py` 等价单测（形状 `[1,196,768] → [1,196,2560]`）。
4. `gate_check_stage1.py` 的阈值沿用 ④ 的口径；若形状相关断言写死 512，**只改维度、不改判据**，并在报告注明。
5. lmms-eval 12 集数据缓存已在盘（`LMMS_EVAL_DATASETS_CACHE=/data/app.e0031982/lmms_eval_cache`）；先 `--limit 5` 跑 ai2d 冒烟（期望 ≈0.60 量级，与 ④ 的 smoke 同法）。

**④ 训练（配方与 ④-4ep / LLaVA-OV1.5 **逐项一致**，只换视觉塔与 projector 宽度）**
| 阶段 | 步数 | 训练什么 | LR | 其他 |
|:--|:-:|:--|:--|:--|
| Stage-1 Alignment | 2500 | 冻结 vision+LLM，只训 projector | 1e-4（不收敛再扫 5e-5/2e-4/5e-4） | 224px，196 tokens，无 spatial-merge |
| Stage-1.5 Mid | 20000 | LoRA r=64（LLM）+ projector | 沿用 `stage15_train.py` 默认 | 8×H100 DDP |
| Stage-2 Instruct | 3500 | LoRA + projector | LoRA 1e-5 / Proj 5e-6，cosine | LLaVA-NeXT-780k |
- 数据：558K / 3M / 780k 三套 WebDataset（均在盘），**与 ④ 完全相同**。
- **成本参考（10-16 实测反推）**：Stage-1 ≈3h、Stage-1.5 = 91.8min（3.63 steps/s）、Stage-2 ≈0.5h、12 集评测 ≈3–5h ⇒ **合计约 7–9h**。**每阶段结束报一次实际耗时**。

**⑤ 评测与交付**
1. 用 `launch_12benchmarks.sh`（每卡 1 benchmark、`--batch_size 32`、8 GPU、**无 --limit**）→ `consolidated_12benchmarks.json`。
2. 中文报告：`reports/report_vision_armB_mllm_stage4_zh.html`（自包含）必须含：
   - 配置表（ArmB 86.2M / 768-dim / projector 768→2560 / Qwen3-4B-instruct-2507）；
   - **12 集完整表 + 与 ④-4ep 的 Δ + 与 RiCEViT 的 Δ**；
   - **判据裁定**（强成功/成功/不可分辨/失败）；
   - **诚实声明**：不与 LLaVA-OV 官方公开榜同框（塔规模 86M、196 tokens 无 anyres、4 epoch）；ProtB 与 MLLM 分数非单调（④ 就是反例）。
3. 同步 `EXPERIMENTS_VISION.md` 新 §（ArmB-Stage4）+ `MEMORY_VISION.md` 指针；commit 前缀 `vision armB-mllm:`。

**⑥ 纪律**
- 🚫 不动 cline / pretrain / harness / data 的任何进程；不抢 `.29`；`.12` 独占。
- 🚫 不因为"分数低"就中途改配方/改判据；低分照实报（低分本身就是结论）。
- ✅ 每轮只推进一步（前置 → 导出 → smoke → Stage-1 → 1.5 → 2 → 评测 → 报告）；`WAITING=1` 仅在实际训练/评测运行时置位。
- 体积：任务书 ≤32KB（超了自滚，只搬已闭合块原文）。


> **用户令（2026-10-18）**：「vision 回放 1/2/3 epoch 要不要做：之前没有存检查点吗？如果没有存，还需要重新训练，那就不做了。」

**① 结论：不做。** 已核实（机读证据，不是推测）：
- `run/vision/armB_aimv2_openclip.py:349-354`：`--keep-ckpts 2` ⇒ 每保存一个新 ckpt，就删最老的 → **盘上永远只留最近 2 个 `checkpoint_*.pt`**；
- 训练日志/流水实证：`keep-ckpts=2 已回收 checkpoint_10000`（10-17 14:5x）、`checkpoint_30000.pt 已自动删(keep-ckpts 2)`（10-18 05:37）、`[ArmB] removed old ckpt checkpoint_30000.pt`；
- ⇒ **1ep=14313、2ep=28626、3ep=42939 三个步点的权重都已不存在**，要拿只能**从零重训≈27.6h** ⇒ 投入产出不成立，**取消**。

**② 你要做的事（只做收尾，不占 GPU）**
1. **不做任何回放/重训**；🚫 不启动训练；🚫 不改 `--keep-ckpts`；🚫 不动已有 final 产物。
2. 若已按上一条指令开始任何动作 ⇒ **立即停止**（`pkill -f armB_aimv2_openclip` 仅限回放进程；若无则 no-op），并在心跳写"未启动/已停止"。
3. 在 `MEMORY_VISION.md` 状态头写明：**「ArmB 1/2/3 epoch 曲线：取消（ckpt 未保留，重训 27.6h 不划算）」**，并标注"今后若需 epoch 曲线，须在训练前把 `--keep-ckpts` 设为 ≥4 或 `--save-every` 调小"。
4. `reports/report_vision_armB_openclip_result_zh.html` 里**不要**出现 epoch 曲线/1-2-3ep 占位；若已有相关小节，改成一句说明：**"epoch 1/2/3 检查点未保留（keep-ckpts=2），故本报告只给 final(4ep)"**。
5. commit 前缀 `vision armB-noep:`；`MEMORY_VISION.md` 保持 ≤32KB（自滚）。

**③ 顺带（同一轮可做，零 GPU）**：把「ArmB 4ep final」这一行正式并进 `zhulong_results` 式的成绩表（在 `EXPERIMENTS_VISION.md §11` 已有的话核对一遍数字）：**lp 62.09±0.01% / 5-NN 58.10%**，并保留"与 ArmA 的 +4.06pp/+4.12pp 是 recipe 综合效应"的诚实注脚。


> ⛔ **旧指令已作废（2026-10-18运维裁定）**：原要求测 1/2/3 epoch 的 ProtB，因 `--keep-ckpts 2` 已把这些 `checkpoint_*.pt` 滚动删除，取回需重训 ≈27.6h ⇒ **做罢**。
> 仅保留事实：ArmB `--save-every 10000 --keep-ckpts 2`；1ep≈14313 / 2ep≈28626 / 3ep≈42939。
### 🆕 运维指令 · 2026-10-17 12:4x（⚔️ 立即 kill `.12` pretrain 进程 → 起 ArmB；**改 4 epoch** → 训完评 ProtB）· 用户直令 · 最高优先
> ⏩ 已执行并归档（杀 pretrain → ArmB 4-epoch）已完成；详情 → `daily-memories-vision/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-17 12:2x（🖥️ `.12` 专属 vision；pretrain 迁 `.29`）· 用户直令 · 最高优先
> ⏩ 已执行并归档（`.12` 专属 vision）已生效；详情 → `daily-memories-vision/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-17 12:0x（🚀 启动 ArmB：open_clip ViT-B/16 + AIMv2-style · 全量 8000 GPIC · 3 epoch）· 用户直令 · 最高优先

> **用户令（原文）**：「vision：启动下边实验 目标=AIMv2-style 数据=全量8000 tar GPIC + CC12M + Amshaker 塔=open_clip ViT-B/16 86.2M warmup=2000步 LR=1e-3，min_lr=1e-4 GBS=8192，MBS=512(如果OOM，则GBS=4096，MBS=256) epoch=3 按照这个配方训练，给个ETA 使用 open_clip接口（便于嵌入LLaVA-OneVision架构用lmms-eval评测）」

**⓪ 与上一条的关系**：本块**取代**上一条（2026-10-17 报告块）的 ③ ArmB 配方与排队；上一条的 **① ArmA 报告 / ② 兼容性附录仍要交**（训练起来后 CPU 补，见 ⑤）。

**① 配方（逐字执行，不改）**：
- 目标：**AIMv2-style** = `contrast_weight×InfoNCE + patch_loss_weight×MSE(predictor(patches[mask]), target[mask])`；`contrast_weight=1.0, patch_loss_weight=1.0, mask_ratio=0.6`（沿用 `r9_train.py:782-807` 口径；报告写清）。
- 数据：**GPIC 全量 8000 tar + CC12M 1100 + Amshaker 2250 = 11,350 shards ≈117.3M 对**；新建 `data_snapshot_20261017_gpic8000.txt`；起训前 `ls | wc -l` + `find -name '*.incomplete'` 核，**实际数字写进 log/report**（若不足/路径不同，按实际并声明）。
- 塔：**open_clip ViT-B/16 224**（visual 86.2M / total 149.6M，双塔随机初始化）。
- 优化：**warmup=2000 步**；**LR 1e-3 → min 1e-4（cosine）**；AdamW wd=0.1、betas=(0.9,0.98)、grad_clip=1.0、bf16、seed=1234（未指定项沿用 ArmA，报告列明）。
- 批：**GBS=8192, MBS=512/卡（累加 2）**；**OOM 回退 GBS=4096, MBS=256/卡（累加 2）**；实际档位 + 峰值显存必须记录。
- 步数：**3 epoch**；N≈117.25M → **GBS8192 ≈42,940 步**（14,313/epoch）；回退 GBS4096 ≈85,876 步；以实际 N 重算并写进报告。
- save every **10,000** 步 + final；保留 latest + 最近 2 个 ckpt（省盘）。

**② open_clip 接口（硬要求）**：
- 必须 `open_clip.create_model_and_transforms('ViT-B-16', pretrained=None)`；不得改模型类/换自研塔。
- **predictor 只作训练辅助头**；取 patch tokens 必须**复用同一次 vision 前向**（forward hook / `forward_intermediates`），**禁止二次 forward**（否则 ETA +35–45%）。
- 保存：`open_clip_state_dict.pt`（**剥离 predictor**）+ `predictor.pt` + `config.json`；验收 `open_clip.create_model_and_transforms('ViT-B-16', pretrained=<ckpt>)` **strict load 通过**。
- LLaVA-OV/lmms-eval：新增 `mllm_bridge/open_clip_vitb16_768.py`（注册 `baize-vitb16-768`；`encode_image` → `[B,196,768]`；image_size 224 / patch 16 / 无 spatial merge）+ `export_for_llava_ov.py`；CPU 单测：open_clip 加载 / `encode_image` 形状 / wrapper 与原生 allclose / projector 768→LLM dim 形状。lmms-eval 用 1 个小样本冒烟（不阻塞训练）。

**③ 起训（先探再起；🚫 不 kill pretrain）**：
- 起训前 `nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv` 原文落盘。
- `.12` 8×H100 正被 **pretrain 80B decay** 全占（ETA ~10-20 02:30）⇒ **不得 kill/降速/抢卡**。
- 先试 `.29`（`ssh -o BatchMode=yes -o ConnectTimeout=5 10.239.2.29 'nvidia-smi'`）：若 8 卡空闲且同一 NFS 的 `py310` + open_clip 可用 → **立即在 .29 起训**；SSH 不通/环境缺 ⇒ 记 blocker（原文），**不得擅自装包/改共享 env**。
- `.29` 不可用 ⇒ 写 `run/vision/run_armB_when_free.sh`：每 5min 轮询 `.12` 8 卡（无 compute apps 且每卡显存 >70GB）→ 满足即 `setsid` 起训；记录 pretrain 实际结束时间。
- 若用户明确要求「停 pretrain 抢卡」才可停；本指令默认**不抢**。

**④ ETA（按实测公式，起训后用自己的实测值刷新）**：
- N≈117.3M（GPIC 8000×12,537≈100.3M + CC12M 11.0M + Amshaker 6.0M）；3 epoch = **351.9M samples**。
- 吞吐：ArmA 实测 **3.37 it/s @ GBS2048 = 6,902 samples/s**；MBS512 预计 +0–5%，AIMv2 头 <1%（前提 = 复用前向）⇒ **6,900–7,300 samples/s**。
- **纯训练 ≈13.4–14.2h**；+启动/ckpt/最终 ProtB（3 seeds）≈1–2h ⇒ **总 ETA ≈15–16.5h**；GPU·h ≈ **110–120**。
- 若二次前向（禁止）→ 19–21h；若实测吞吐 6,000 → 16.3h 纯训练。
- **两条起训情景**：① `.29` 空 → 代码 1–2h 后起（约 13:00–14:00）→ **10-18 04:00–06:30 完成**；② 只能等 `.12` → 10-20 02:30 起 → **10-20 17:00–19:00 完成**。
- 报告必须给：实际 N / steps / samples/s / 墙钟 / 峰值显存 / 是否 OOM 回退。

**⑤ 交付与次序**：
1. **P0**：`run/vision/armB_aimv2_openclip.py` + `run/vision/run_armB_openclip.sh` + `run/vision/run_armB_when_free.sh` + CPU 单测（1–2h）。
2. **P0**：起训（.29 优先，否则排队 .12）。
3. **P1**：训练起来后用 CPU 补 **ArmA 中文报告 + 兼容性附录**（上一条要求）。
4. `MEMORY_VISION.md` 状态头 + `daily-memories-vision/2026-10-17.md`；commit `vision armB:`。

**⑥ 纪律**：不改配方；不 kill pretrain；不伪造 ETA/结果；不占 GPU 做 CPU 工作；任务书/MEMORY ≤32KB 自滚。


### 🆕 运维指令 · 2026-10-17（📄 ArmA 结果中文报告 + 归档 · 🔌 open_clip × AIMv2-style 兼容性工程评估）· 用户直令 · 最高优先

> **用户令（2026-10-17）**：「vision：把 ArmA 结果写成中文报告并归档。问题：open_clip 接口和AIMv2-style不能兼容吗？」

**① 报告（先做，纯写作零 GPU）**：`reports/report_vision_armA_openclip_result_zh.html`，中文自包含，必须含：
- **协议**：ProtB（full IN-1k 1.28M train + 50k val，SGD 90 epochs，seeds 0/1/2），`feature=projected`，ckpt=`latest.pt`；数字取 `run/vision/armA_protb_vitb16_224_results.json`（lp 58.02/58.07/58.02 → **58.03±0.02%**；5-NN **53.98%**）。
- **训练口径**：open_clip **ViT-B/16 224**（visual 86.2M / total 149.6M，双塔随机初始化）、**ClipLoss InfoNCE**、GBS 2048（MBS 256×8）、LR 2e-3→2e-4（warmup 8000）、**154,500 步**、数据 GPIC(7437)+CC12M(1100)+Amshaker(2250)=10,787 shards ≈118M 对；证据 `run_armA_openclip.sh:13-15,45-52` + `armA_openclip_train.py:169-187,256-316`。
- **对比表**（同表列：协议/塔/参数量/目标/步数/数据/ProtB lp/5-NN）：ArmA vs **④-4ep（67.05±0.02 / 42.35）**、④-2ep、V3、R11-G 等，数值以 `EXPERIMENTS_VISION.md` 既有记录为准。
- **关键解读（必须写）**：ArmA = **lp −9.02pp / 5-NN +11.63pp** ⇒ 检索型表征强、线性可分性弱，与「C1/lp 背离」假设一致；⚠️ **不是单变量对照**（塔 86.2M vs 126.8M、目标 InfoNCE vs AIMv2-style dense、步数/样本不同）⇒ **不得写成「AIMv2 目标比 InfoNCE 好 9pp」**。
- **诚实条款**：内部 ProtB 口径、非官方榜；单 backbone/单预算点；5-NN 与 lp 口径不同；仅评测 3 seeds（训练单 seed）。
- **归档**：报告 + 结果 JSON + 训练/评测日志路径写入 `MEMORY_VISION.md` 与 `EXPERIMENTS_VISION.md` 新 §「ArmA（open_clip ViT-B/16, 2026-10-17）」；commit `vision armA:`。

**② 回答问题（报告附录 A，必须给结论 + 代码行号）**：
- **结论：分两层 —— 模型/推理接口兼容；open_clip 自带「训练损失/循环」不兼容（需自定义，不是不能做）。**
- **兼容证据**：ArmA 用的就是 open_clip 模型，`model(imgs, texts) → (img_feat, txt_feat, logit_scale)` + `ClipLoss`（`armA_openclip_train.py:286-287`）；导出侧只需 `encode_image` 的 pooled/patch 输出（`mllm_bridge/open_clip_baize.py:8-16,26-34`）。predictor 是训练期辅助头，**不进入推理图** ⇒ 不影响 open_clip 加载/评测。
- **不兼容点**：open_clip 的 loss 家族（Clip/SigLIP/CoCa/GenLIP…）**没有 patch 级重建目标**；其训练循环只吃 `(image,text)`，不提供 mask 采样/patch 目标。我们这套 AIMv2-style 是**自研训练环**：`loss = contrast_weight×InfoNCE + patch_loss_weight×MSE(predictor(patches[mask]), target[mask])`，`mask_ratio=0.6`（`r9_train.py:782-807`；实现说明 `reports/report_vision_aimv2_impl.html`）。
- **做「open_clip 模型 + AIMv2-style」需要 4 件事（≈1–2 人日，纯 CPU）**：
  1. 在 open_clip ViT 上挂 `PatchPredictor`（≈0.66M）；
  2. 取 patch tokens（按 open_clip 版本用 `visual.forward_features` / `visual.trunk.patch_embed` / `forward_intermediates` 之一，或用 forward hook **复用同一次前向**，避免二次算力；实现前先 `python -c` 打印 `type(model.visual)` 与可用方法并截图/日志存证）；
  3. 自定义 loss + 训练步（照 ArmA 循环改 ≈50 行）；
  4. ckpt 存 predictor；**导出 open_clip 权重时必须剥离 predictor**（或单独存 `predictor.pt`），否则 `load_state_dict(strict=True)` 会报 unexpected keys；若 `contrast_weight=0`（纯 AR）→ `find_unused_parameters=True` 或冻结文本塔（ArmA 现为 `False`）。
- **概念澄清**：官方 AIMv2 = 多模态自回归（图文 token + decoder，弃用对比），open_clip 的对比接口无法表达；本仓 `r9_train.py` 的 `aimv2_ar` + `decoder_depth` 才是那一支。报告须分开写，避免混淆。

**③ ArmB**：配方/起训/排队**已被 2026-10-17 12:0x 顶部指令取代**（open_clip ViT-B/16 + AIMv2-style，全量 8000 GPIC，3 epoch）；本条只保留 **① 报告** 与 **② 兼容性附录**。预注册判据仍有效：lp ≥58.03% 不倒退；≥61.0% 且 5-NN ≥48.98% → 接受混合；否则写负面结论。

**④ 纪律**：不占 GPU（除放行）；每个数字可溯源到 `文件:行`/原始日志；不改已发布数值；与 pretrain 线 IO 错峰。


> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> 不得回退：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---


> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 为什么新增（真实事故）：2026-10-06 06:55 → 08:30，data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新（其间 agent 在改别的文件、push 得出去），外部运维只能靠 git 判断死活 ⇒ 被误判成静默卡死并上机排查。
> 根因：「更新记忆 + push」以前只是建议、没有硬约束；loop 的兜底 push 间隔是 5h（本日已缩短），且只覆盖固定白名单 —— 不许依赖兜底。
> 🚫 旧口径（已废）：「每 5 小时由 loop 兜底 push 一次」不再作为交付保障 —— 兜底只是保险丝，不是你的提交手段。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理，不再等你。你干得再多，心跳不动 = 仍会被判死。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）


- 🚫 不许闭门造车：涉及"别人怎么做"（架构/loss/评测/数据）必须去读官方仓库或论文原文（能 clone 就 clone）—— 不得凭二手描述下结论（本线已因此出错一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂必须报「参数量 + 训练 token + 每步耗时」，不许只比 acc。
- 预注册：判据先定后测，不许事后改。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` 都每次唤醒被全文读进 prompt（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ 21KB、`MEMORY_VISION.md` ≈ 32KB（已贴上限）。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_VISION.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的巡检/流水条目（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 状态头 ③ 最近 ~20 条。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
