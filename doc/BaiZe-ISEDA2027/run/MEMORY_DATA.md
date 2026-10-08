# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅全分词完成(44 shards=524.42B tok)+✅全量污染扫描清洁(30 parquet×5K=150K docs,0命中,累计160K docs全0)+GPIC 6708/8001(ETA~29h→~10:48Oct10)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；D-CLEAN-1/2/3/4；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43; s_step归因(MBS16:8.6×,166ms); Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); zh分词8/8✅(112.47B); 论文更新(4+5节,main.pdf 0err); l1_en_hq分词12/12✅(152.17B); ultrax分词s34-s43✅(30.97B); en_base分词s24-s33✅(206.76B); ✅投料前污染采样扫描(10K docs,0命中); ✅全量污染扫描(30 parquet×5K=150K docs,0命中,累计160K docs全0命中)
当前动作:     唤醒246(05:48@.12) 全量污染扫描确认完成(30/32files,150K docs,0命中✅)+GPIC 6708/8001(+31,~45tar/h)+CONTAMINATION_CHECK更新+心跳
下一步:       ①GPIC续下(6708/8001,ETA~29h→~10:48Oct10); ②en_v1_4排队等运维放行; ③报运维"全分词完成+全量污染扫描清洁,数据就绪"
阻塞:         GPIC下载进行中(6708/8001,ETA~29h→~10:48Oct10); en_v1_4排队等运维放行
ERROR_COUNT:  1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒185-190 已归档 → `daily-memories-data/2026-10-07.md`（含BO方向bug调查全链+UltraX启动+zh分词启动详情）
> 📦 唤醒201-203 已归档 → `daily-memories-data/2026-10-08.md`（含report_data_mix_summary.html产出+zh分词8进程启动+GPIC巡检）
> 📦 唤醒220-224 已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq 12进程巡检全链+en_base/ultrax启动+GPIC巡检）
> 📦 唤醒223-224 已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq 86-94%巡检+en_base/ultrax起步巡检+GPIC巡检）
> 📦 唤醒225-226 原文已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq s12-s15完成+en_base起步+ultrax s34-s42完成+GPIC巡检）
> 📦 唤醒227-233 原文已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq s18-s19完成+en_base起步+ETA纠正+GPIC巡检全链）
- [05:48] **唤醒246**：①本机=`.12`。②**✅全量污染扫描完成**：后台PID1942365已退出（05:34完成），扫描30/32 parquet(en_base×10+l1_en_hq×12+zh×8)×5K docs=150K docs，**0命中**✅。结合唤醒244采样(10K docs,0命中)，累计160K docs全0命中→Ultra-FineWeb全系与EDA-Eval不同源，**数据清洁，可投料**。summary→`run/data_pipeline/contam_scan_full_summary.md`。③**GPIC** 6708/8001(+31 since 05:07,~45tar/h)+128/128test✅,PID144981活(cwd=/nas_inference/.../datasets,etimes~5d),latest=06707@05:48,0.incomplete,ETA(8001-6708)/45≈29h→**~10:48Oct10**。④**.29 GPU**:GPU6=6525MiB/16%(pretrain),其余7卡全空(0MiB/0%)→.29有7卡空闲。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(无data新指令)。⑦load=104.13/224核(偏高:GPIC+vision R9@.12+pretrain@.29,可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.2KB✅/MEMORY=20.0KB✅(无需归档)。下载线心跳：base✅全满|GPIC 6708/8001(活PID144981,+31,~45tar/h,ETA~29h→~10:48Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|en_base 10/10✅(206.76B)|**全量污染扫描:✅完成(150K docs,0命中,累计160K docs全清洁)**。
- [05:07] **唤醒245**：①本机=`.12`。②**🔄全量污染扫描启动**：创建`run_contam_scan_full.sh`并后台启动(setsid,PID1942365,ppid=1✅),扫描32 parquet(en_base×10+l1_en_hq×12+zh×10)×5K docs=160K docs(16×采样扫描量),全部在/nas_train(避/nas_inference与GPIC争I/O)。当前4/32完成(20K docs,**0命中**✅),ETA~30min。③**GPIC** 6677/8001(+31 since 04:27,~46.5tar/h)+128/128test✅,PID144981活(cwd=/nas_inference/.../datasets,etimes~5d),latest=06676@05:08,1.incomplete(正常),ETA~28h→~10:00Oct10。④**.29 GPU**:GPU0,1,2,3,5=0MiB/0%(5卡空),GPU4,6,7=62.6GB/52-91%(pretrain R3 BO)→.29有5卡空闲。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(无data新指令)。⑦load=95.32/224核(偏高:GPIC+vision R9@.12+pretrain BO@.29,可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.8KB✅/MEMORY=18.6KB✅(归档唤醒234-242→daily-memories,释放~12KB)。下载线心跳：base✅全满|GPIC 6677/8001(活PID144981,+31,~46.5tar/h,ETA~28h→~10:00Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|en_base 10/10✅(206.76B)|**全量污染扫描:4/32完成,20K docs 0命中✅(后台运行中)**。
- [04:27] **唤醒244**：①本机=`.12`。②**✅投料前污染采样扫描**：对en_base(3 parquet:part-0001/1000/2048-of-2048)+l1_en_hq(1 parquet:CC-MAIN-2025-30 part-0001)+zh(1 parquet:part-001-of-256)各跑`check_contamination.py`(blacklist=6快照并集536任务/193,295 13-gram+10 8-gram,--max-docs 2000),**5×2000=10,000 docs 全部0命中**✅。与phase5负控(L3 qa 0命中)一致→Ultra-FineWeb全系与EDA-Eval不同源。⚠️正式投料前需补全量扫描(2048+6000+256 parquet)。③**GPIC** 6646/8001(+28 since 03:50,~45tar/h)+128/128test✅,PID144981活(cwd=/nas_inference/.../datasets,etimes~5d),latest=06645@04:27,0.incomplete,ETA~30h→~10:00Oct10。④**.29 GPU**(运维指令⑤②口径):GPU0,1,2,3,5=0MiB/0%(5卡空),GPU4,6,7=62.6GB/31-62%(pretrain R3 BO)→.29有5卡空闲,data如需GPU可登记GPU29_ALLOC.md。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(无data新指令)。⑦load=101.28/224核(偏高:GPIC+vision R9@.12+pretrain BO@.29 ssh探测,本机可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.8KB✅/MEMORY=30.96KB✅(无需归档)。下载线心跳：base✅全满|GPIC 6646/8001(活PID144981,+28,~45tar/h,ETA~30h→~10:00Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|en_base 10/10✅(206.76B)|**投料前污染扫描:10K docs 0命中✅**。
- [03:50] **唤醒243**：①本机=`.12`。②**🎉en_base s24-s33✅全完成**！10/10 shards全部完成(进程已退出),各.bin/.idx/.json均存在(mtime 03:32-03:45Oct9)。**精确token(from .json)**:s24=20.696B·s25=20.690B·s26=20.667B·s27=20.676B·s28=20.665B·s29=20.676B·s30=20.665B·s31=20.675B·s32=20.679B·s33=20.671B→**TOTAL=206,761,737,329=206.76B tok**。⚠️main.log报全部10个rc=135(SIGBUS),但s24.log末行`[done] 25470511文档/20695615606 tokens in 52338.3s;产物:...s24.bin/.idx/.json`→**数据已完整写入后SIGBUS(NFS mmap cleanup,非data loss)**。③**Token inventory(44 shards with .idx)**:s0-s3=22.05B·s4-s11=112.47B·s12-s23=152.17B·**s24-s33=206.76B(NEW!)**·s34-s43=30.97B→**total=524.42B(P-8~100B exceeded5.2x!)**。④**GPIC** 6618/8001(+27 since 03:13,~43tar/h)+128/128test✅,PID144981活,latest=06617@03:50,0.incomplete,ETA~32h→~12:00Oct10。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(仅zhulong/pretrain/vision/harness新提交,无data新指令)。⑦load=44.75/224核(en_base已退出,仅GPIC+vision R9@.12GPU,可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.8KB✅/MEMORY=29.0KB✅(无需归档)。下载线心跳：base✅全满|GPIC 6618/8001(活PID144981,+27,~43tar/h,ETA~32h→~12:00Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|**en_base s24-s33 ✅10/10全完成(206.76B tok)**。
> 📦 唤醒234-242 原文已归档 → `daily-memories-data/2026-10-09.md`（含en_base s24-s33巡检全链+GPIC巡检+ETA纠正）
> 📦 唤醒219-221 已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq分词12进程启动+巡检进度+GPIC计数）
> 📦 唤醒211-218 原文已归档 → `daily-memories-data/2026-10-08.md`（含zh s9完成+论文更新+l1_en_hq巡检全链+GPIC巡检）
> 📦 唤醒207-210 原文已归档 → `daily-memories-data/2026-10-08.md`（含zh分词巡检+report修正+GPIC巡检）
> 📦 唤醒204-206 原文已归档 → `daily-memories-data/2026-10-08.md`（含s9崩溃修复+zh分词ETA修正+GPIC巡检）
> 📦 唤醒201-203 原文已归档 → `daily-memories-data/2026-10-08.md`
> 📦 唤醒191-200 原文已归档 → `daily-memories-data/2026-10-08.md`（含zh分词并行化启动+BO R2完成+top-K收尾+UltraX续传/完成+Spearman ρ=−0.80）




> 📦 唤醒190 已归档 → `daily-memories-data/2026-10-07.md`
> 📦 唤醒185 已归档 → `daily-memories-data/2026-10-07.md`
> 📦 唤醒184 已归档 → `daily-memories-data/2026-10-07.md`
> 📦 唤醒171-183 已归档 → `daily-memories-data/2026-10-07.md`
> 📦 旧流水（唤醒156-166）已归档 → `daily-memories-data/2026-10-06.md`

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

### ⑩ 运维三问（2026-10-07）— ✅ 已答（唤醒185,11:43@.12,只答不动）

**① base 下完后 GPIC 加快？→ 没有显著加速。** base 完成于 08:16。GPIC tar 计数（按 mtime）：≤06:00=4846, ≤08:16=4945, ≤11:44=5103。前(06:00→08:16,2.27h)：99 tar→**43.6 tar/h**；后(08:16→11:44,3.47h)：158 tar→**45.5 tar/h**。差异+4.4%（噪声范围）→**没加速**。GPIC 走 stanford-vision-lab CDN（与 base 的 openbmb 独立）。剩余 2898 tar @~45.5/h→ETA~63.7h≈2.7天。

**② base 还有其它数据待下载？→ 下载已全部结束。** 白名单：`en` 2048/2048✅(2.66TB,R1) · `l1_en_hq` 6000/6000✅(478GB,08:16) · `zh` 256/256✅(301GB) · GPIC 5103/8001(下载中)+128/128✅。白名单外(纪律不下载)：`en_v1_4`(stale 0-byte .incomplete **已清理**) · `UltraX-Preview`(未下)。**一句话：base「下载」已全部结束(3 config 全满)，只剩 GPIC 在下；后续 P-8 备料是「分词扩展 22.05B→~100B tok」不是下载。**

**③ Round2 BO 为什么变慢？→ 没有变慢。** 波派发：8 trial 同时派发(8 GPU 各 1)，~38min 后同时完成→burst of 8 + 38min gap。波间 gap 稳定 37-40min(12 波全程一致)，rate=**12.5/h**。每 trial=train ~30min(15258步@MBS16/D=0.5B)+lm_eval 8集 ~8min(--limit 500)。vmstat .29:**wa=0**,iowait=0,CPU idle 87-94%→**无 I/O 争用**；harness 跑 /dev/shm 不抢 NFS。14 fail 全早期(t0-t13)，修复后连续 91✅。**结论：BO 没变慢，12.5/h 稳定；"变慢"印象来自 8 卡波派发的 bursty 节奏。** 95 remaining→ETA~7.6h→~19:20。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **✅全分词完成(44 shards=524.42B tok) + 全量污染扫描进行中(32 parquet×5K=160K docs,后台PID1942365) + GPIC 6677/8001(ETA~28h)** |
| WAITING | 1（GPIC 6677/8001 ETA~28h→~10:00Oct10; 全量污染扫描后台运行中ETA~30min; en_v1_4排队等放行） |
| ERROR_COUNT | 1（s9崩溃重启后已完成） |
| 节点 | `10.239.2.12`（GPIC下载PID=144981活, .29有5卡空闲） |
| 更新 | 2026-10-09 05:07 |

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

