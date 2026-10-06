# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验 → ①BO 200/200+top-K lm_eval+Spearman+σ+report ✅完成 → ②s_step归因✅(MBS1→16:8.6×) → ③第二轮BO脚本就绪,待GPU0释放
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe创建；held-out bin+held_out_eval; baize_mix_optuna.py；5项必验全通过；BO 200/200完成(best=#182 loss=5.822); top-K lm_eval 8集完成(6 configs); Spearman ρ=−0.43(负相关!); σ=0; report_data_mix_eval.html; s_step归因完成(MBS1→16:8.6×,166ms); report_data_mix_sstep.html; **baize_mix_optuna_r2.py已创建**(lm_eval objective,MBS=16,D=0.5B,ckpt→HF→lm_eval); DATA_MIX_RECIPE.md §9.2.1/§9.2.2已更新
当前动作:     唤醒169(01:20) ①**baize_mix_optuna_r2.py已创建**(Round2 BO: lm_eval objective, MBS=16, D=0.5B→15259步, --limit 500, 独立DB mix_search_eval_r2.db, 语法验证✅) ②**DATA_MIX_RECIPE.md §9.2.1/§9.2.2已更新**(Round1结论+Round2设计对比表) ③**GPU0仍被pretrain bbh_4771占用**(84%,ETA~10min) ④base下载l1_en_hq 5476/6006(91%)
下一步:       ①待pretrain释放GPU0-1→ssh .29 跑 `python baize_mix_optuna_r2.py --gpus 0,1,2,3,4,5,6,7 --n-trials 200`; ②base下载监控(l1_en_hq 91%); ③Round2完成后top-K full lm_eval+σ+report_data_mix_eval_r2.html
阻塞:         GPU0仍被pretrain bbh_4771占用(84%,ETA~10min),步骤③需GPU0-1全释放
ERROR_COUNT:  0
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
- [01:20] **唤醒169**：①本机=`.12`。②**baize_mix_optuna_r2.py已创建**(389行,语法验证✅)：Round2 BO脚本，关键改动=objective改为lm_eval 8集均分(非val-loss proxy)、MBS=16(非1)、D=0.5B→15259步、save final ckpt→HF转换→lm_eval(subsampled --limit 500)→parse score→cleanup、独立DB mix_search_eval_r2.db、支持8卡。GP surrogate存储negated score(minimize→maximize)。每trial≈42min训练+5min评测≈47min，200trial/8卡≈20h。③**DATA_MIX_RECIPE.md §9.2.1/§9.2.2已更新**：§9.2改为"Round1 ✅完成"、新增§9.2.1(Round1关键结论：Spearman ρ=−0.43负相关+top-K表+σ=0+spread=0.0053)、新增§9.2.2(Round2设计对比表)。§9.5下载进度更新(l1_en_hq 5476/6006=91%)。④**GPU0仍被pretrain bbh_4771占用**(84% 2269/2700, ETA~10min)，GPU1-7空闲。步骤③触发条件(GPU0-1全释放)未满足。⑤base下载l1_en_hq 5476/6006(91.2%)。📦 体积：TASK=34.3KB / MEMORY=15.0KB（归档0KB,TASK略超32KB但<40KB红线）。
- [22:39] **唤醒166**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~7h,`--objective eval`):**187/200 complete**(0 pruned,6 in-flight t186-191)。**best=5.831981**(#155:web=0.847/code=0.035/math=0.118),top5=#155/149/96/125/55。先验88:8:4=#59(loss=5.856989,**rank27/187,Δ=0.025→先验竞争力上升**)。rate:168→187 in 34min=~33.5/h,13剩余,ETA~23:30。GPU2-7各6.7GB/~10%util,GPU0=pretrain lm_eval,GPU1已释放(sglang停)。③⭐**s_step归因实验完成**！`baize_sstep_profile.py`在GPU1@.29测MBS∈{1,4,8,16}(GBS=16,seq=2048,50step,88:8:4 blend):**MBS=1 median=1432ms**(16μbatch)→**MBS=4=418ms**(3.4×)→**MBS=8=220ms**(6.5×)→**MBS=16=166ms**(8.6×)。Peak mem: 3→11→20→42GB(均<80GB)。结论：**overhead-bound(每μbatch~90-170ms Python/kernel-launch)，非compute-bound**。MBS=16使D=0.5B/trial(15259步×0.166s=42min→205trial/24h/6GPU)可行。结果存`sstep_profile/sstep_profile_results.json`。④base下载:zh✅256/256(301G),l1_en_hq 5128/6006(382G,85.4%)。📦 体积：TASK=31.7KB/MEMORY待更新。
- [22:05] **唤醒165**：①本机=`.12`。②**BO eval study**(mix_search_eval.db,PID 1011682@.29 alive~6h35m,`--objective eval`):**168/200 complete**(0 pruned,6 in-flight t168-173)。**新best=5.831981**(#155:web=0.847/code=0.035/math=0.118),top5=#155/149/96/125/55(loss 5.832~5.833)。先验88:8:4=#79(loss=5.886048,**rank~92/168,Δ=0.054→先验不竞争力**)。rate:150→168 in 38min=~28.4/h,32剩余,ETA~23:12。GPU2-7各6.7GB/~10%util,GPU0-1=pretrain。③⭐**base下载**: zh✅**256/256下满**(301G)! l1_en_hq **5088/6006**(379G,84.7%,5snap×1000✅+CC-2025-51@89 actively downloading part-0090),0 incomplete,PID 3076519+retry-loop 3076502 alive。l1_en_hq余918→ETA~11:15 Oct7(速率~70/h)。④vision占.12 GPU0-7(R12b,与data无冲突,data用.29 GPU2-7)。⑤**BO完成后计划**:top-5(#155/149/96/125/55)+先验88:8:4(#79)共6个config需重跑带ckpt→lm_eval 8集取均分→Spearman秩相关验证代理有效性→噪声σ→report。📦 体积：TASK=31.7KB / MEMORY=30.8KB（归档 0KB,均≤32KB ✅）。
> 📦 旧流水（唤醒156-164）已归档 → `daily-memories-data/2026-10-06.md`

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。
### ①-⑧ 已归档（详见 `daily-memories-data/2026-10-06.md`）

| # | 主题 | 结论 | 日期 |
|:--|:--|:--|:--|
| ① | SFT-2605 重下 | ✅ 1504 jsonl / 318.99 GB，与 HF 官方清单逐字节一致 | 10-02 |
| ②-④ | D-CLEAN-1/2/3 | ✅ 盘点 + 删除 servers(974G)+nemo R1(310G)+laion(7.8G)+pip(3.3G) ≈1.3T；nemo R2 ckpt 保留 | 10-03 |
| ⑤ | 下载白名单 | ✅ 停 en_v1_4，只下 l1_en_hq+zh+GPIC | 10-03 |
| ⑥-⑦ | D-CLEAN-4 + LLaVA ckpt | ✅ 盘点：本用户可回收 ≈11.4TiB(含 LLaVA-OV 22TiB iter ckpt)，待运维拍板 | 10-04 |
| ⑧ | LIT_IDEAS HTML | ✅ 产出 `LIT_IDEAS_2026-10-05.html`（52 entries/0 unverified/62% turnover），含成本专章+ISEDA投稿要求(4-6页) | 10-04 |
### ⑨ 🔴 配比实验可行性核查（2026-10-05 运维分卡指令 · §0.6-B）— ✅ 可行性核查完成，⏳ 等 GPU2-7

> 运维 2026-10-05 批准：`.29` GPU2-7（6 卡）归 data 跑配比实验，与 pretrain 推理评测并行。**起跑前置 = 先等 P-9.8 armB(FP8) 跑完**。

**① GPU2-7 核查（10:26 实测原文）**：
```
ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'
→ 8 个 python 进程各 ~72GB，PID 4044610-4044617
ssh 10.239.2.29 'nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv'
→ 8 卡各 100% util / ~72GB used
```
**结论**：❌ **GPU2-7 当前不空** —— P-9.8 armB 已于 ~09:49 完成，但 pretrain 随即启动 **P-9.9**（tensorwise FP8 1000 步跑，PID 4044534，~10:02 起，**占满 8 卡**，ETA ~15:00）。**不 kill（铁律）**，等 P-9.9 完。

**② 脚本/recipe 核查（✅ 全部就位）**：
- `run/baize_p5b_train.sh`：8 卡 TP1/DP8 模板（GBS=1024/seq=4094/WSD/bf16）—— **已复制为** `run/baize_mix_train_template.sh`（改为 6 卡 TP1/DP6，CUDA_VISIBLE_DEVICES=2,3,4,5,6,7）
- `code/BaiZe-ISEDA2027/pretrain_launcher.py`：✅ 支持 `--train-data-path` blend `[w, prefix, w2, prefix2, ...]`
- `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py`：✅ parquet→.bin/.idx（需 `*.snappy.parquet` 后缀；base 文件名是 `*.parquet`→已用软链加 `.snappy` 后缀解决）

**③ 训练数据 .bin/.idx 核查（.29 上）**：
| 源 | 状态 | 路径 | token 估 |
|:--|:--|:--|--:|
| `p5b_l3` (L3 web) | ✅ 16 片 | `data/p5b_l3/p5b_l3_train_s{0..15}.bin` | ~20.6B |
| `anneal_code` | ✅ | `data/anneal_code.bin` (345M) | ~180M |
| `anneal_math2` | ✅ | `data/anneal_math2.bin` (1.7G) | ~860M |
| `ultrafineweb_l3_qa_700m` | ✅ | `data/ultrafineweb_l3_qa_700m.bin` (2.97G) | ~1.5B |
| `tokenizer_eod` | ✅ | `data/tokenizer_eod` | — |
| **base (ultrafineweb_en)** | 🔜 **分词中** | `data/mix_base/mix_base_train_s{0..3}` | ~21B（48 parquet→4 shard，4 进程并行 @ 10:32 起） |
| **SFT-2605** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-2605/data/` (1504 jsonl, 298G) | 需写 jsonl→text 转换器（chat 格式，preprocess_data.py 只认 parquet content 列） |
| **SFT-Agent-2609** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-Agent-2609/` (50 shard, 51G) | 同上 |

**④ 环境（✅）**：`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`；tokenizer=`/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash`；ssh .29 免密 ✅。

**⑤ 已创建脚本**：`run/baize_mix_tokenize_base.sh`（base 分词，已启动）+ `run/baize_mix_train_template.sh`（6 卡训练模板，待 GPU 就绪）。

**⑥ 下一步**：base 分词完成（ETA ~1-2h）→ 汇总 token 数 → P-9.9 完成（~15:00）→ GPU2-7 空 → 起 Stable 段 S0a 臂（base:code:math=88:8:4, 5000 步）→ ckpt→HF→lm_eval Table 2（8 集）。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **§0.6-B 配比实验 → ①BO 200/200✅+Spearman ρ=−0.43(负相关!)+σ=0 ②s_step归因✅(MBS1→16:8.6×) ③Round2脚本就绪(baize_mix_optuna_r2.py),待GPU0释放; base下载: zh✅, l1_en_hq 91%** |
| WAITING | 0（步骤①②完成; Round2脚本就绪待GPU0-1释放; pretrain bbh_4771@84% ETA~10min; base下载l1_en_hq 91%） |
| ERROR_COUNT | 0（历史②项已修复归档） |
| 节点 | `10.239.2.29`（GPU0=pretrain bbh_4771, GPU1-7空闲; Round2需GPU0-7全释放） |
| 更新 | 2026-10-07 01:20 |

## 看板（按推荐执行顺序）

| 阶段 | 状态 |
|:---|:---:|
| R research（🎯 只答 §0 两问） | ✅ 完成（DATA_RESEARCH v1.1：LLM 够/走路线A；Vision 换 GPIC short 消截断） |
| R2 LLM 数据侧调研（任务书两项优先） | ✅ 完成（DATA_RESEARCH R2 节：8 源事实表满填 / base vs L3 重叠实测 0% / P-8 三档 44B·100B·200B = base-en(86):code(10):math(4)；base 2.99TB 下载已启动） |
| R2 视觉侧调研（§0.4 去 HF 找通用图文对） | ✅ 完成（DATA_RESEARCH R2-视觉侧：本地 12 源图像形态+≤77 实测 / 13 HF 候选其中 7 URL-only 淘汰 / 前 3 推荐 CC12M≈11M + Amshaker≈6M + LLaVA≈1.15M，50 万→1800 万对 ×35，无需新下载） |
| phase0 inventory（实测盘点） | ✅ 完成（DATA_LEDGER v0） |
| phase5 isolation（**先立闸**） | ✅ 完成（v0.3：536 任务 + NFKC/Unicode 归一化 + 8-gram 兜底 + **SFT 嵌套 jsonl 目录同闸扫描**，全快照正控 100%） |
| phase1 validate（完整性校验） | 🟡 校验脚本已备（validate_data.py），全量跑待下载完成后 |
| phase2 text（通用文本 .bin/.idx） | 🟡 分词打包 wrapper 已备（preprocess_text.sh + 污染闸门），跑待下载完成后 |
| phase3 domain（EDA 领域语料排查） | 🚫 **已取消**（运维 2026-10-01 夜：评测 prompt 由 docstring 生成、与语料天然同源，入库无意义）；但 EDA-Eval 158 任务黑名单红线**依然有效、继续执行** |
| phase4 mm（多模态打包） | ⬜（待下载完成） |
| phase6 handoff（清单/报告/HTML） | ⬜ |

## 待确认（需要人工提供）

- [x] ~~EDA API 知识库能否导出纯文本~~ → **已确认可行**：`eda_fastmcp/docs/` 本就是 md/json 纯文本（≈45MB，见 DATA_LEDGER §5）。
- [x] ~~EDA 语料入库授权~~ → **整条线已取消**（运维 2026-10-01 夜）：评测 prompt 由 docstring 生成、与语料天然同源，"把测试集放进训练集"无意义 → phase3_domain 不再调研/入库。**但 EDA-Eval-PyAether 158 任务黑名单红线照常执行。**
- [x] ~~内部培训材料 / 脱敏 CAD 案例能否用于训练~~ → 随 phase3_domain 一并取消。
- [ ] 多模态下载预计完成时间
- [x] ~~`UltraData-SFT-2605/-Agent-2609` 具体存储格式~~ → **已实测**：Agent-2609 = **jsonl**（50 shard / 51 GiB，2GB/shard）；**2605 = 落盘为空**（仅 179 个 `.lock` 缓存文件 / 22.4KiB，无数据，需重下）
- [x] ~~`UltraData-SFT-2605` 重新下载~~ → **✅ 已下满并核验一致（2026-10-02 唤醒 37）**：落盘 **1504 jsonl / 318,990,252,711 B = 318.99GB（297.08 GiB）**，`.incomplete` = 0，**与 HF 官方清单（1504 文件 / 318,990,252,711 B）逐字节完全一致**；逐子目录 `no_think` 855✓（CG 50/Code 300/IF 20/Kn 80/Math 300/ML-Kn 50/ML-Math 55）+ `think` 649✓（CG 50/Code 279/IF 20/Kn 50/Math 250）。token `hf_lqLxH…`（用户 foamliu）。

> 📦 旧流水（唤醒111-145, S0a训练+分词+kill改道全程）已归档 → `daily-memories-data/2026-10-05.md` 及 `2026-10-06.md`
> 关键结论：①base分词22.05B tok✅ ②SFT-2605 20.97B+Agent-2609 全4shard✅ ③S0a 2.2B单臂浪费~100 GPU·h→改道proxy BO搜索 ④proxy模型92.7M(d=512/L=14)标定s/step=1.5s ⑤smoke test✅

## ⭐ s_step 归因实验（2026-10-06 22:48-22:56, GPU1@.29, d=128 proxy 18.36M, 88:8:4 blend）

> **目的**：定位 s_step=1.5s 的瓶颈，将 D（=步数×GBS×seq）从 0.016B/trial 抬到 0.5–1B/trial。
> **方法**：`baize_sstep_profile.py`，固定 GBS=16/seq=2048/50步，测 MBS∈{1,4,8,16}，记录 elapsed time per iteration（去掉 step 10 warmup）。
> **结果存**：`nemo_experiments/sstep_profile/sstep_profile_results.json`

| MBS | μbatch/step | 中位 s_step (ms) | tok/s | 峰值显存 (MB) | 加速比 |
|:---:|:---:|:---:|:---:|:---:|:---:|
| 1   | 16 | **1432** | 22,893 | 3,024 | 1.0× (基线) |
| 4   | 4  | **418**  | 78,431 | 10,851 | 3.4× |
| 8   | 2  | **220**  | 149,211 | ~20,000 | 6.5× |
| 16  | 1  | **166**  | 197,831 | 42,164 | **8.6×** |

**结论**：
- **瓶颈 = overhead-bound**（每 μbatch ~90-170ms Python/kernel-launch overhead × 16 μbatch = 1.5s），非 compute-bound。
- **MBS=16 使 s_step 从 1432ms→166ms（8.6×）**，峰值显存 42GB（80GB H100 可容纳，即使与 sglang 27GB 共存也只需 69GB）。
- **D 投影（6 GPU, 24h, GBS=16, seq=2048）**：
  - MBS=1（当前）：500步×1.432s=716s/trial → D=0.016B/trial
  - MBS=16, D=0.5B/trial：15259步×0.166s=2533s=42min/trial → 205 trial/24h ✅
  - MBS=16, D=1B/trial：30518步×0.166s=5066s=84min/trial → 103 trial/24h ✅
- **进一步优化目标（≤100ms）**：CUDA graph（消除 kernel launch）+ CE fusion（减少 42GB logits 显存开销）
- **第二轮 BO 建议**：用 MBS=16，D=0.5B/trial（200 trial/24h/6GPU），或 8 卡（GPU0-7）→400 trial/24h
## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

