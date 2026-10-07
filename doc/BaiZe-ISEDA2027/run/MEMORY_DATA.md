# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验 → ①BO R1 200/200✅+Spearman+σ ✅ → ②s_step归因✅(MBS16:8.6×) → ③Round2 BO 🚀运行中(129trial:114✅/15❌,8GPU,rate~13/h,ETA~19:30,⭐new best t75=0.373) → 🎉base下载✅完成 → 🔓白名单解禁 → 🚀UltraX下载进行中(123/483,122GB,rate~10s/file加速!,ETA~15:00) → 🔧zh分词进行中(s4.bin=13GB,nice-19,ETA~16:00) → ⚠GPIC降速至5.5/h(受UltraX分流,ETA~22天)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py；5项必验全通过；BO R1 200/200+Spearman+σ=0+report; s_step归因(MBS16:8.6×,166ms)+report; Round2 BO(PID=3614158@.29)启动+修3bug+修ckpt2HF; ⭐base下载完成→MiniCPM5 base族就绪; ✅R1 lm_eval errata更正+归档; ✅stale en_v1_4 .incomplete已清理; ✅运维三问已答(唤醒185); ✅白名单解禁→UltraX下载启动(PID=2850809)+zh分词启动(PID=2850810,nice-19); ✅BO 8GPU运行(GPU0-1已释放,新best t75=0.373)
当前动作:     唤醒189(14:04@.12) ①4进程全活巡检：UltraX(PID=2850809,123/483files,122GB,rate~10s/file加速,ETA~15:00)+zh分词(PID=2850810,s4.bin=13GB,ETA~16:00)+GPIC(PID=144981,5131/8001,rate~5.5/h,ETA~22天)+BO(PID=3614158@.29,129trial:114✅/15❌,⭐new best t75=0.373,8GPU,ETA~19:30) ②GPU .29:8active(0-7,50-77%/62GB)→BO已用满8卡 ③git fetch成功无新指令 ④TASK=30.3KB✅/MEMORY=19.8KB✅
下一步:       ①监控BO(71remaining,ETA~19:30到200trial); ②BO跑完→top-K全量lm_eval→report_data_mix_eval_r2.html; ③监控UltraX下载(ETA~15:00,加速中)+GPIC(⚠受UltraX分流降速至5.5/h,ETA~22天); ④zh分词完成后→启动l1_en_hq分词(6000parquet,2-4进程nice-19); ⑤UltraX完成后→启动en_v1_4下载(6.75TB); ⑥GPIC续下至8001tar(⚠需运维决策是否暂停UltraX优先GPIC)
阻塞:         Round2 BO运行中(129/200trial,ETA~19:30); GPIC下载进行中(5131/8001,⚠降速至5.5/h); UltraX下载进行中(123/483,122GB/487GB)
ERROR_COUNT:  0
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
- [14:04] **唤醒189**：①本机=`.12`。②**4进程全活**：UltraX(PID=2850809/1448940,ppid=1✅,etimes~7070s)+zh分词(PID=2850810/2851334,ppid=1✅,nice=19,etimes~7070s)+GPIC(PID=144981,etimes~67h,CWD=/nas_inference/.../datasets)+BO(PID=3614158@.29,etimes~43991s≈12.2h)。③**UltraX**:123/483parquet(25%),122GB,rate~10s/file(⚠从58s/file大幅加速!),8 incomplete,log `25%|██▌|123/483[22:28<1:05:46]`→ETA~60min→~15:00。④**zh分词**:s4.bin=13GB(growing~90MB/min,no .idx yet,256parquet→mix_base_train_s4)→ETA~2h→~16:00。⑤**GPIC**:5131/8001(+5 since 188)+test 128/128✅,rate~5.5/h(05129@13:52→05130@14:03,~11min/tar,UltraX分流带宽)→ETA~22天。⑥⭐**Round2 BO**:DB(129trial:114✅/15❌,+8 since 188),**新best t75(0.373)**,top5:t75(0.373)/t110(0.375)/t70(0.37725)/t96(0.37775)/t53(0.378)。8trial并发(t0129-t0136 on gpu0-7),rate~13/h→71remaining→ETA~5.5h→~19:30。GPU .29:**8active(GPU0-7,50-77%/62GB)**→BO已用满8卡(GPU0-1已释放!)。⑦git fetch(proxy)成功,behind0→**无新data指令**。⑧磁盘:34T free(85%)。⑨**联合ETA**:GPIC~10-29(⚠受UltraX降速,ETA~22天)|UltraX~10-07_15:00(加速!)|en_v1_4排队(UltraX后)|zh分词~10-07_16:00|BO~10-07_19:30。📦 体积：TASK=30.3KB✅ / MEMORY=19.8KB✅。下载线心跳：base ✅全满 | GPIC 5131/8001（活PID144981,⚠rate~5.5/h,ETA~22天）| UltraX 123/483 122GB/487GB（活PID2850809,rate~10s/file加速,ETA~15:00）| zh分词 s4.bin=13GB（活PID2850810,nice-19,ETA~16:00）。
- [13:25] **唤醒188**：①本机=`.12`。②**4进程全活**：UltraX(PID=2850809/2850817,ppid=1✅,etimes~78min)+zh分词(PID=2850810/2851334,ppid=1✅,nice=19,etimes~83min)+GPIC(PID=144981,etimes~66h)+BO(PID=3614158@.29,etimes~11.5h)。③**UltraX**:78/483parquet(16%),81GB/487GB,rate~58s/file,8 incomplete→ETA~6.5h→~20:00。④**zh分词**:s4.bin=8.75GB(growing~55MB/min,no .idx yet,256parquet→mix_base_train_s4)→ETA~3-4h→~17:00。⑤**GPIC**:5126/8001(+2 since 187)+test 128/128✅,rate~3.4/h(⚠⚠极慢：05123@12:31→05124@12:46→05125@13:13→05126下载中,avg~17min/tar,UltraX分流带宽)→ETA~35天。⑥**Round2 BO**:DB(121trial:106✅/15❌,+5 since 187),best=t23(0.4155不变),top5:t23(0.4155)/t38(0.4138)/t118(0.413,新)/t33(0.409)/t57(0.4058)。rate~8.6/h,79remaining→ETA~22:40。GPU .29:5active(GPU2-6,40-62%/62GB),2idle(GPU0-1,0%),1between(GPU7,0%/60GB)。⑦git fetch(proxy)成功,pulled zhulong+harness commits,behind0→**无新data指令**。⑧磁盘:34T free(84%)。⑨**联合ETA**:GPIC~10-12(⚠受UltraX降速,ETA极长~35天,需运维决策)|UltraX~10-07_20:00|en_v1_4排队(UltraX后)|zh分词~10-07_17:00|BO~10-07_22:40。📦 体积：TASK=32.8KB⚠微超→归档运维问询块 / MEMORY更新后~19KB。下载线心跳：base ✅全满 | GPIC 5126/8001（活PID144981,⚠rate~3.4/h极慢,ETA~35天）| UltraX 78/483 81GB/487GB（活PID2850809,ETA~20:00）| zh分词 s4.bin=8.75GB（活PID2850810,nice-19,ETA~17:00）。
- [12:46] **唤醒187**：①本机=`.12`。②**4进程全活**：UltraX(PID=2850809,ppid=1✅,etimes~39min)+zh分词(PID=2850810,ppid=1✅)+GPIC(PID=144981)+BO(PID=3614158@.29,etimes~10.9h)。③**UltraX**:36/483files(7.5%),34GB/487GB,rate~68s/file→ETA~8.4h→~21:00。④**zh分词**:s4.bin=4.3GB(growing~100MB/min,no .idx yet)→ETA~5-6h→~18:00。⑤**GPIC**:5124/8001(+21 since 185),rate~20/h(**⚠从45.5/h降速→UltraX分流带宽**)→ETA~6天→~10-13。⑥**Round2 BO**:DB(116trial:101✅/15❌),best=t23(0.4155不变),top5:t23/t38/t33/t57/t105。rate~8.8/h(波gap~37min),84remaining→ETA~22:00。GPU:3active(0=46%/1=91%/7=66%),5idle。⑦vmstat .29:**wa=0**,CPU idle=96%→**分词未影响BO**。⑧git fetch(proxy)成功,behind0→**无新运维指令**。⑨磁盘:34T free(84%)。**联合ETA**:GPIC~10-13(受UltraX降速)|UltraX~10-07_21:00|en_v1_4排队(UltraX后)|zh分词~10-07_18:00。下载线心跳：base ✅全满 | GPIC 5124/8001（活,rate~20/h⚠降速,ETA~6天）| UltraX 36/483 34GB/487GB（活PID2850809,ETA~21:00）| zh分词 s4.bin=4.3GB（活PID2850810,nice-19,ETA~18:00）。
- [12:03] **唤醒186**：①本机=`.12`。②⭐**收到新运维指令`9471ed9b`(解禁白名单)**：立即下载UltraX-Preview(487GB,483files,5config)+en_v1_4排队(6.75TB)+已下载base开始分词扩展22.05B→~100B tok。优先级:GPIC>UltraX>en_v1_4；分词nice-19+限2-4进程+盯BO速率。③⭐**UltraX-Preview下载已启动**：PID=2850809(ppid=1✅),`hf download --repo-type dataset openbmb/UltraX-Preview`,8 parallel,489MB/487GB,speed~4MB/s(起步),落`/nas_train/.../openbmb/UltraX-Preview/`。④⭐**zh分词已启动**：PID=2850810(ppid=1✅),nice-19,1进程,256 parquet→mix_base_train_s4(.bin=190MB增长中,ETA~10h)。⑤**Round2 BO**:111trial(97✅/14❌),best=t23(0.4155不变),t107-t111在12:00-12:03连续complete→**BO未受分词影响**。⑥GPIC PID=144981存活(5103/8001)。⑦磁盘:/nas_train 34T free(84%)。⑧脚本已创建:`baize_download_ultrax.sh`+`baize_tokenize_zh.sh`。📦 体积：TASK~32KB / MEMORY更新后~33KB（需归档唤醒184→daily）。下载线心跳：base ✅全满 | GPIC 5103/8001（活PID144981,ETA~2.7天）| UltraX 489MB/487GB（活PID2850809,起步~4MB/s）| zh分词 s4.bin=190MB（活PID2850810,nice-19）。
- [11:43] **唤醒185**：①本机=`.12`。②**base✅全满**（en 2048+l1_en_hq 6000+zh 256,0 .incomplete,stale en_v1_4 .incomplete已rm清理）。③**GPIC** PID=144981+3525273存活,train **5103/8001**（+27 since唤醒184)+test 128/128✅,mtime 11:44秒级活跃(gpic_train_05102.tar)→无需重启。④**Round2 BO** DB(mtime=11:21):**105trial(91✅/14❌)**,best=t23(0.4155不变),top5:t23(0.4155)/t38(0.4138)/t33(0.4090)/t57(0.4058)/t105(0.4055,新)。⑤波分析:end_time波间gap稳定37-40min(12波),8trial/波=**12.5/h无变慢**→95remaining→ETA~7.6h→~19:20。⑥vmstat .29:**wa(iowait)=0**,CPU idle 87-94%,GPU 48-88%util→**无I/O争用**;harness跑/dev/shm不抢NFS。⑦✅**运维三问已答**(见运维问答⑩)。⑧git fetch(proxy=172.19.92.25:13128)成功,behind0→无新运维指令。📦 体积：TASK=28.3KB / MEMORY更新后~32KB（归档~1.5KB→daily 10-06）。下载线心跳：base l1_en_hq ✅6000/6000 · zh ✅256/256 | GPIC 5103/8001（活PID144981,ETA~63h）。
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
| PHASE | **§0.6-B 配比实验 → ①BO R1 200/200✅+Spearman ρ=−0.43 ②s_step归因✅(MBS1→16:8.6×) ③Round2 BO🚀运行中(PID=3614158@.29,116trial:101✅/15❌,rate~8.8/h,ETA~22:00) ④🔓白名单解禁→UltraX下载进行中(PID=2850809,36/483,34GB)+zh分词进行中(PID=2850810,s4.bin=4.3GB,nice-19)** |
| WAITING | 1（Round2 BO在跑,116/200trial,ETA~22:00到200trial完成;等BO完成后跑top-K全量lm_eval; UltraX下载+zh分词后台进行中） |
| ERROR_COUNT | 0（batch1 arch mismatch已修+batch2 port冲突已修,修复后连续101trial✅; BO未受分词影响,vmstat wa=0） |
| 节点 | `10.239.2.29`（GPU0-7=Round2 BO,3active/5idle; 116trial运行中; vmstat wa=0无I/O争用）+`.12`（UltraX下载PID=2850809+zh分词PID=2850810 nice-19） |
| 更新 | 2026-10-07 12:46 |

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

