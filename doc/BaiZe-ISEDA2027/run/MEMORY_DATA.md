# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验改道 → d=128/L=14 proxy(18.36M) → 🔄 BO搜索Stable段进行中(18/200 trial完成, PID 2483227, GPU2-7)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a 2.2B单臂已kill；proxy d128 provider+recipe创建；held-out bin(base/code/math各~2M tok)；baize_mix_optuna.py创建(GP-EI)；5项必验全部通过(09:48)；BO搜索Stable段已启动(10:01)；**任务书归档完成(79.8KB→39.5KB)**
当前动作:     唤醒149(10:42) ①查BO搜索进度:18/200 trial完成,best=4.7115(#16:web0.82/code0.06/math0.12),先验点(88:8:4)Δ=0.20(排~7th);②任务书归档(79.8KB→39.5KB,移出改道方案①②③+2026-10-05块+§0/§0.6/§1.1/§2/§4/§5→ARCHIVE_OPERATOR_DATA.md+ARCHIVE_DATA_SPEC_HISTORY.md);③query_search.py创建;④更新心跳+日报+commit
下一步:       ① BO搜索继续(~5h剩余,ETA~16:00);② 每~30-60min查进度+commit心跳;③ 200 trial完成→出top-K表+先验点对比+best-so-far曲线;④ Day2搜Decay段
阻塞:         无
ERROR_COUNT:  0
```

## 🔬 开工前 5 项必验结果（2026-10-06 09:48，全部通过）

> 任务书 §B 要求的 5 项必验，在 .29 GPU2-7 上完成。**全部 PASS**，d=128/L=14 proxy 可开工。

### 必验 #2: d=128 结构合法性 ✅

| 项 | 实测值 | 预期值 | 判定 |
|:--|:--|:--|:--|
| **N（总参数）** | **18,355,656** | ≈18.5M | ✅ 差 < 1% |
| **E（embedding）** | 16,560,256 (=129,408×128) | 16.56M (90%) | ✅ |
| **body（N-E）** | 1,795,400 | ≈1.91M | ✅ (系数差异因 heads=1/groups=1，见下) |
| **heads=1, n_groups=1** | 构建成功，10 runs 0 NaN | edge case | ✅ |
| **vocab** | 129,408 (padded from 129,281) | 129,408 | ✅ |

- 结构：d=128 · L=14 · ffn=512 · mamba d_inner=256 · ssm_state=128 · heads=1 · tie embed · pattern `M-M-M--M-M*-M-`
- 原始输出（torchrun 1 GPU）：`number of parameters on (tensor, pipeline) model parallel rank (0, 0): 18355656`

### 必验 #3: 2B tie/untie 系数 ✅

| 项 | 实测值 | 说明 |
|:--|:--|:--|
| **2B N（总参数）** | **2,220,909,056** (TP=2, 每卡 1,110,454,528) | ≈2.221B ✅ |
| **2B vocab** | 129,536 (padded from 129,281) | |
| **share_embeddings_and_output_weights** | **False** | **UNTIE** |
| **E = V×d** | 265,429,888 (=129,536×2048) | |
| **body(N-E) coeff** | **8.324 ≈ 8.32** | body 含 output layer（untie） |
| **body(N-2E) coeff** | **7.194 ≈ 7.19** | decoder only（不含 output） |
| **d=128 body(N-E) coeff** | **7.825** | tie，body 仅 decoder；与 2B 差异因 heads/groups 比例不同 |

> **结论**：2B 模型为 UNTIE（`share_embeddings_and_output_weights=False`）；body(N-E) 系数 = 8.32，body(N-2E) 系数 = 7.19。d=128 proxy 为 TIE，body 系数 = 7.825（与 2B 不同因架构比例差异，不影响迁移性论证——比例 `24M:4*:28-` 一致）。

### 必验 #4: s_step 实测 ✅

| 口径 | 值 | 说明 |
|:--|:--|:--|
| **s_step (median, iter 20-50)** | **1,503.65 ms ≈ 1.50s** | 16 次测量（4 runs × 4 iters），范围 1,425–1,582 ms |
| **每 trial 总时间** | ≈100s | 50步×1.50s + init(15s) + eval(10s) |
| **T (1 GPU/day)** | **864** | 86400÷100 |
| **T (6 GPU/day)** | **5,184** | 864×6 |
| **512 组需要** | < 1.5h | 512÷5,184×24 ≈ 2.4h → 远超需求 |

> s_step 原始数据（ms）：1512.5, 1472.8, 1564.7, 1490.8, 1480.3, 1437.0, 1559.0, 1425.4, 1455.0, 1511.4, 1582.0, 1534.7, 1495.9, 1538.5, 1563.0, 1493.7

### 必验 #5: LR 三点重扫 ✅

| LR | val_loss@iter50 (held_out_base) | PPL | 判定 |
|:--|:--|:--|:--|
| **3e-4** | 10.194 | 26,746 | ❌ 太慢 |
| **1e-3** | 8.044 | 3,102 | 🟡 可用 |
| **3e-3** | **7.403** | **1,641** | ✅ **最优，选定** |

> 选定 **LR=3e-3** 作为固定 LR。50 步内 loss 单调下降，grad norm 稳定（0.28–0.59），0 NaN。

### 必验 #1: 判别力（可分辨性证伪）✅✅✅

> **最关键验证**：code=0% vs code=30%，各 3 seed，eval on held_out_code，LR=3e-3，50 steps。

| 配比 | seed=1234 | seed=2345 | seed=3456 | **mean** | **σ** |
|:--|:--|:--|:--|:--|:--|
| **code=0%** | 8.6805 | 8.6794 | 8.7790 | **8.7130** | **0.057** |
| **code=30%** | 7.2746 | 7.2479 | 7.1316 | **7.2180** | **0.076** |

| 指标 | 值 | 阈值 | 判定 |
|:--|:--|:--|:--|
| **Δloss** | **1.495** | > 2σ | ✅ |
| **2σ (pooled)** | 0.190 | — | — |
| **Δloss / 2σ** | **7.9×** | > 1× | ✅✅✅ 远超 |

> **结论**：d=128/L=14 proxy 的判别力**极强**（Δloss/2σ = 7.9×），可清晰区分 code=0% vs code=30% 配比。**规模可用，配比实验可开工。**

## 📋 本唤醒流水

- [10:01] **唤醒148**：⭐ **BO搜索Stable段已启动！** LR修正1e-3→3e-3(必验#5选定)+添加--proxy-size d128显式参数→语法OK→启动`baize_mix_optuna.py --phase stable --n-trials 200 --gpus 2,3,4,5,6,7`(PID 2483227 nohup)。6 trial并行(t0000-t0005)，GPU2-7各~6.7GB/~10%util。t0000 step20/500 `lm loss: 1.104813E+01` s/step=1.56s LR=1.2e-3(warming→3e-3) 0NaN ✅健康。ETA~7h(200trial×13min/6GPU)。

- [10:42] **唤醒149**：①BO搜索进度=**18/200 trial完成**(t0000-t0018),best=**4.7115**(#16:web=0.8222/code=0.0607/math=0.1170),先验点(88:8:4)最近trial=#13(web=0.8906/code=0.0757)loss=4.9135,**Δ(prior-best)=0.2020**(先验排~7th,BO已找到更优点→更多math/更少web);GP-EI已接管(trial≥12为BO引导,非随机);t0018运行中(GPU5)。②**任务书归档**:79.8KB→39.5KB(红线40KB内),移出→ARCHIVE_OPERATOR_DATA.md(改道方案①+2026-10-05三块)+ARCHIVE_DATA_SPEC_HISTORY.md(改道方案②③+§0/§0.6/§1.1/§2/§4/§5),留10条📦指针。③创建query_search.py(DB查询脚本)。📦 体积：TASK=39.5KB / MEMORY=25.8KB（归档 ~40KB → ARCHIVE_OPERATOR_DATA.md + ARCHIVE_DATA_SPEC_HISTORY.md）。

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
| PHASE | **§0.6-B 配比实验改道 → 🔄 BO搜索Stable段进行中(18/200, PID 2483227, GPU2-7); 任务书归档完成(79.8KB→39.5KB)** |
| WAITING | 1（🔄 BO搜索Stable段运行中: 18/200 trial完成, best=4.7115(#16), 先验Δ=0.20, ETA~16:00; 每30-60min查进度+commit心跳） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.29`（GPU2-4标定中，GPU0-1/5-7空闲） |
| 更新 | 2026-10-06 |

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

- 2026-10-05 —— 唤醒 111（已滚动归档至 daily-memories-data/2026-10-04.md）
- 2026-10-05 —— 唤醒 112（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 113（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 114（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 115（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 116（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 117（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 118（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 119（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 120（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 121（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 122（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 123（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 124（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 125（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 126（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 127（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 128（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒129~130（✅base分词完成22.05B tok+SFT s2✅3.58B+s1冲突修复+P-9.9仍占8卡+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒131~132（🚀S0a臂启动step60/5000+ETA更正312GPU·h/臂+baize_mix_eval.sh✅创建+SFT分词进度+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒133~134（⚠️S0a crash/重启→step84/5000+SFT分词进度+git proxy同步成功+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒135~136（S0a step145→200/5000+✅✅SFT-2605全4shard完成20.97B tok!+🔄Agent-2609分词启动+git pull proxy同步）（详情已归档）
- 2026-10-05 —— 唤醒137（19:23 S0a step260/5000+Agent-2609 2/4+下载巡检+内存滚动）（详情已归档至 daily-memories-data/2026-10-05.md）

- 2026-10-05 —— 唤醒138（20:02 S0a step330/5000+Agent-2609 s0/s1进行中+D-CLEAN-4定案确认）（详情已归档至 daily-memories-data/2026-10-05.md）
 - 2026-10-05 —— 唤醒139（20:45 S0a step390/5000 loss4.07+✅Agent-2609 s0完成2.58B tok→3/4 done+下载l1_en_hq 3157+git proxy同步）：① ⭐ **S0a健康推进**：step390/5000, loss 4.07（稳定下降 4.56@300→4.46@310→4.42@320→4.36@330→4.29@340→4.25@350→4.20@360→4.15@370→4.13@380→4.07@390, LR=1.0e-3达峰, 0NaN/0skipped），~37.8s/iter, GPU2-7 6卡38-86%util ~39GB。**ETA=(5000-390)×37.8≈48.4h→~Oct7 21:00**。PID 2528081-2528090。② ✅ **SFT-Agent-2609分词**：**s0✅完成** — 2,578,877,685 tokens (2.58B) / 69,895 docs, .bin 10.3G + .idx 1.4M + .json (20:21完成)；s2✅(1.23G)；s3✅(2.6G)；**s1🟡仍跑** — .bin 12.9G增长中(~2.2MB/s, PID 166424, etime~1h48m, 输入=sft_General_Agent.parquet symlink, 无.idx=未完)。→ **3/4 shard完成**。③ 下载l1_en_hq **3157/6006**(+51, retry-loop PID 3076502+hf PID 3076519活)、zh **171/256**(冻结)、gpic **3486 tars**(PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步, 无behind/ahead)。⑤ GPU0-1 on .29空闲(4MiB, 0%util, pretrain P-9.10已完成)；GPU2-7 S0a训练中。磁盘/nas_train 84%(34T free) /nas_inference 65%。MEMORY_DATA.md=27.5KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s1完→Decay段全备料(SFT-2605✅20.97B+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。
 - 2026-10-06 —— 唤醒140（01:13 ⭐report_data_mix_s0a.html实时更新+S0a step820/5000 loss3.23+✅✅Agent-2609全4shard完成→Decay全料就绪+下载巡检+git proxy同步）：① ⭐ **S0a健康推进**：step820/5000, loss 3.23（稳定下降 10.84@10→4.93@250(LR达峰)→3.57@600→3.40@700→3.25@800→3.23@820, LR=1.0e-3, 0NaN/0skip），~37.6s/iter, GPU2-7 6卡30-82%util ~39GB。**ETA=(5000-820)×37.6≈43.7h→~Oct7 20:53**。PID 2525319(etimes=31703≈8h48m)。② ✅✅ **SFT-Agent-2609分词全完成**：s0✅(2.58B tok)+**s1✅**(.bin 18G+.idx 6.2M+.json, 21:27完成)+s2✅(1.23G)+s3✅(2.6G)→**4/4 done! Decay段全料就绪**。③ ✅ **report_data_mix_s0a.html已更新**（运维指令2026-10-05深夜2⑤）：实时数据step760→820/loss3.30→3.23/ETA→Oct7 20:53/GPU表/SVG图表修正(82个数据点逐10步, 修正了旧版y坐标映射错误)/日志附录/里程碑表。纯CPU写作,不占GPU。④ 下载l1_en_hq巡检(进行中)。⑤ ✅git fetch via proxy成功(无behind/ahead)。GPU0-1空闲。磁盘/nas_train 84%。MEMORY_DATA.md≈29KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 20:53)→ckpt→HF→lm_eval Table2(8集)；✅Decay段全料就绪→可起Decay臂(SFT占比搜索)；填DATA_MIX_RECIPE.md实测值。
 - 2026-10-06 —— 唤醒145（08:06 🔴 Step0 kill S0a 2.2B单臂 → 代理模型创建 → 标定启动 → MEMORY/GPU更新）：① 🔴 **Step0 kill**（运维指令 §「Step 0」kill）：
   - **kill 目标**：`mix_stable_s0a` = watchdog PID 2525272 → torchrun PID 2525319 → 6 workers 2528081-2528090
   - **kill 命令**：`kill 2525272 && sleep 2 && kill 2525319 2528081 2528082 2528083 2528084 2528085 2528086 2528087 2528088 2528089 2528090`
   - **GPU 释放验证**：`nvidia-smi` → GPU2-7 all 0 MiB / 0% util ✅
   - **watchdog restart script**：`/tmp/restart_mix_stable_s0a.sh` 已 `rm -f` ✅
   - **DEPRECATED**：`baize_mix_stable_s0a.sh` 已加 `exit 1` + 注释 `DEPRECATED: killed 2026-10-06 per ops §Step0` ✅
   - **作废**：step1470/5000 loss2.76，~100 GPU·h 浪费（已记录教训）→ 改道代理模型 BO 搜索
   ② **代理模型创建**：
   - `mamba2_hybrid_proxy/__init__.py` ✅
   - `mamba2_hybrid_proxy/provider.py`：`NVIDIAMambaHybridModelProviderProxy` — h=512, L=14, pattern="M-M-M--M-M*-M-", tie embed, GQA 4Q/1KV, mamba_groups=2, ce_fusion=True
   - `mamba2_hybrid_proxy/recipe.py`：`pretrain_config` — WSD scheduler, GBS=16, seq=2048, train_iters=13700, bf16_mixed
   - `pretrain_proxy_launcher.py`：standalone argparse launcher（复用 bridge_compat + forward_step）
   - `baize_mix_calibrate.sh`：3 LR × 50 steps 并行（GPU2=3e-4, GPU3=1e-3, GPU4=3e-3）
   - **修正**：`context_model_parallel_size` → `context_parallel_size`（dataclass 字段名差异）
   ③ 🔄 **标定进行中**：GPU2/3/4 各 ~6.5GB / 54-86% util（对比 2.2B 的 39GB！）；日志在 /tmp/baize_calib_lr{0,1,2}.log；ETA ~5min
   ④ 下一步：等标定完成 → 实测 s/step → 锁定模型尺寸 → 创建 held-out bin → 写 Optuna study → Day1/Day2 搜索

### 标定结果（2026-10-06 08:22 完成）

| LR | s/step (avg) | loss@50 | grad norm@50 | TFLOP/s |
|---|---|---|---|---|
| 3e-4 | 1.57s | 7.692 | 0.472 | 14.8 |
| **1e-3** | **1.56s** | **7.081** | **0.509** | 15.0 |
| 3e-3 | 1.60s | 7.274 | 0.325 | 14.7 |

- **s/step ≈ 1.5s**（目标 0.095s，差 16×，瓶颈=data loading，GPU util 仅 ~15 TFLOP/s / 1000）
- **精确参数量**：`sum(p.numel())` = **92,711,712** (~92.7M)
  - Embed (tied): 129408×512 = 66.3M (71.5%)
  - Body: 26.5M (28.5%)
  - 比例 2.220B/92.7M ≈ 1/24（目标 1/23，偏差 ~4%）
  - vocab: 129281→padded 129408 (÷128)
  - 层分配: 6 Mamba + 1 attention + 7 MLP = 14 ✓
- **Trial 预算**：500 步/trial × 1.5s = 12.5 min/trial × 6 GPU → **T≈691 > 400 ✅**（锁定 h=512/L=14，不需缩尺）
- **LR 选择**：LR=1e-3（与 2B recipe 一致，loss@50 最优）
- **校准 checkpoint 已清理**（`rm -rf nemo_experiments/calib_lr*`）

### Held-out 验证集 + BO 搜索脚本 + Smoke Test（2026-10-06 08:50 完成）

#### ① create_heldout_bins.py — 已创建并运行
- 脚本位置：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/create_heldout_bins.py`
- 方法：hash-split（`md5(salt:doc_idx) % 100 < valid_pct`），salt=42，valid_pct=5%
- 用 `_IndexReader(path, multimodal=False)` 读 .idx，`numpy.memmap` 读 .bin，`IndexedDatasetBuilder` 写出
- **运行结果**：
  | 域 | 源 | docs | tokens | 文件大小 |
  |---|---|---|---|---|
  | base | mix_base_train_s0 | 2451 | 2,003,023 | 7.7M bin + 48K idx |
  | code | anneal_code | 1451 | 2,000,625 | 7.7M bin + 29K idx |
  | math | anneal_math2 | 4618 | 2,000,101 | 7.7M bin + 91K idx |
  | **合计** | | **8520** | **6,003,749** | **~24M** |
- 输出路径：`data/heldout/held_out_{base,code,math}.{bin,idx}`

#### ② baize_mix_optuna.py — 已创建并通过语法检查
- 脚本位置：`run/baize_mix_optuna.py`（336行）
- **替代 Optuna**：`.29` 离线（`pip install optuna` → Network is unreachable），改用 **GP-EI**（sklearn GPR + scipy Expected Improvement）
  - sklearn 1.7.2 + scipy 1.15.3 已可用
  - Matern(ν=2.5) kernel + L-BFGS-B 优化 EI（20 random restarts）
  - 前 12 trial 随机采样，之后 GP-EI 引导
  - 中位数 pruning：intermediate val loss > 1.5× 已完成 trial 中位数 → kill
- **搜索空间**：
  - Stable (Day1)：web ∈ [0.80, 0.95], code ∈ [0.03, 0.12], math = 1 - web - code
  - Decay (Day2)：sft_pct ∈ [0.40, 0.80] + 4D SFT class simplex（待 SFT shard 准备后启用）
- **训练参数**：500 steps/trial, eval_interval=100, eval_iters=10, GBS=16, seq=2048, LR=1e-3, WSD(50 warmup/450 decay), bf16_mixed
- **并行**：6 GPU（2-7）ThreadPoolExecutor + Queue 管理 GPU 分配
- **存储**：SQLite（`nemo_experiments/mix_search/mix_search.db`），支持断点续跑
- **Checkpoint 自动清理**：trial 结束后 `shutil.rmtree(ckpt_dir)`，避免 200×400MB=80GB 填盘
- **日志解析**：`VAL_LOSS_RE = r"validation loss at iteration\s+(\d+).*?lm loss value:\s*([\d.eE+-]+)"`

#### ③ Smoke Test — 通过 ✅
- GPU2, 20 steps, blend=0.85/0.08/0.07, eval@10/20
- **结果**：
  | 指标 | 值 |
  |---|---|
  | s/step (warmup, 前10步) | 9.7s |
  | s/step (warmup后, 后10步) | **1.4s** ✅ |
  | train loss (step 10→20) | 10.72→8.70 |
  | val loss (step 10→20) | 9.34→8.23 |
  | log parser 提取 | `{10: 9.344584, 20: 8.227096}` ✅ |
- Smoke test checkpoint 已清理

#### ④ 启动命令（待运维批准）
```bash
ssh 10.239.2.29 'export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230; \
  nohup /nas_train/app.e0031982/miniforge3/envs/py310/bin/python \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_optuna.py \
  --phase stable --n-trials 200 --gpus 2,3,4,5,6,7 --n-random 12 \
  > /tmp/mix_search_main.log 2>&1 &'
```
- ETA：200 trials × 12.5 min / 6 GPU ≈ 6.9h
- 监控：`sqlite3 nemo_experiments/mix_search/mix_search.db "SELECT id,params,loss,status FROM trials ORDER BY loss LIMIT 10"`

## 🔴 事故复盘 — S0a 2.2B 单臂 kill（2026-10-06 08:06）

> **背景**：运维指令 §「Step 0」要求 kill `mix_stable_s0a`，改用代理模型 BO 搜索路线。
> **决策理由**：单臂 2.2B 跑 5000 步 × 6 卡 ≈ 310 GPU·h 才出一个数据点；代理模型 96.8M 单卡 50 步 ≈ 5 min 出一个数据点，T≥400 才有统计意义。
> **浪费**：step1470/5000 ≈ 1470/5000 × 310 ≈ 91 GPU·h（~100 GPU·h，保守估计含 overhead）。
> **教训**：数据配比搜索不应直接跑 full-size 模型，应先小 proxy 模型快速扫配比，再选 top-K 跑 full-size 确认。
> **kill 原始输出**：
> ```
> # kill watchdog → torchrun → 6 workers
> $ kill 2525272 && sleep 2 && kill 2525319 2528081 ... 2528090
> # GPU verify
> $ nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
> 2, 0 MiB, 0 %    ← released ✅
> 3, 0 MiB, 0 %    ← released ✅
> 4, 0 MiB, 0 %    ← released ✅
> 5, 0 MiB, 0 %    ← released ✅
> 6, 0 MiB, 0 %    ← released ✅
> 7, 0 MiB, 0 %    ← released ✅
> # rm restart script
> $ rm -f /tmp/restart_mix_stable_s0a.sh
> ```







## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

