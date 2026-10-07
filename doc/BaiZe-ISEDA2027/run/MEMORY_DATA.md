# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B配比实验全交付✅ → 后台: zh分词7/8shard完成(98.80B tok)+s9~74%done + l1_en_hq分词12进程运行中(s12-s23,各~3.85GB.bin) + GPIC 5714/8001
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43+report; s_step归因(MBS16:8.6×,166ms)+report; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾全完成(ρ=−0.80); report_data_mix_eval_r2.html(18KB)+report_data_mix_summary.html(29KB); zh分词并行化(1→8进程); ✅zh分词7shard(s4-s8,s10,s11)完成(98.80B tok,各~14.1B/56.5GB.bin); ✅l1_en_hq分词启动(12进程s12-s23,6000 parquet/446GB)
当前动作:     唤醒214(07:29@.12) 巡检zh s9(~74%done,ETA~09:45)+l1_en_hq 12进程(各~3.85GB.bin)+GPIC 5714/8001+心跳更新
下一步:       ①s9完成后报zh总token(~113B); ②l1_en_hq分词完成(ETA~15:00-16:00)→报l1总token; ③GPIC续下(5714/8001,ETA~2.1d); ④en_v1_4排队等放行; ⑤新分词产物投料前过check_contamination.py
阻塞:         s9 zh分词进行中(42GB.bin,ETA~09:45); l1_en_hq分词12进程进行中(各3.85GB.bin,ETA~15:00-16:00); GPIC下载进行中(5714/8001,ETA~2.1d)
ERROR_COUNT:  1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒185-190 已归档 → `daily-memories-data/2026-10-07.md`（含BO方向bug调查全链+UltraX启动+zh分词启动详情）
> 📦 唤醒201-203 已归档 → `daily-memories-data/2026-10-08.md`（含report_data_mix_summary.html产出+zh分词8进程启动+GPIC巡检）
- [07:29] **唤醒214**：①本机=`.12`。②**zh s9巡检**：log@12.1M docs/10.43B tok(23341.8s≈6.48h),.bin=41.98GB(无.idx,仍在写),PID286565活(99%CPU,ppid=286557✅)。对比已完成shard(.bin~56.5GB=~14.1B tok),s9~74%done by .bin。rate~1.8MB/s,remaining~14.5GB→ETA~09:45。s4-s8,s10,s11✅(.bin56.5GB+.idx327MB each,98.80B tok)。s0-s3✅(en base,22.05B tok)。③**l1_en_hq巡检**：12进程(s12-s23)全活(99%CPU,PID759478~787625,ppid=758456✅,nice-10),各.bin~3.85GB@07:29(37min in,rate~1.73MB/s/shard),无.idx。按input~37GB/shard+expansion~1.5x→final~56GB→ETA~15:00-16:00。load=18.68/224核(可控)。④**GPIC** 5714/8001(+28 since 06:52,~45tar/h)+128/128 test✅,PID144981活,latest tar=gpic_train_05713@07:29,ETA(8001-5714)/45≈50.7h≈2.1d。⑤base✅全满·UltraX✅479/479·en_v1_4排队。⑥git pull(proxy)=Already up to date,无新运维指令。⑦📦体积:TASK=30.1KB✅/MEMORY=23.4KB✅。下载线心跳：base ✅全满 | GPIC 5714/8001（活PID144981,+28,~45tar/h,ETA~2.1d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7/8shard完成(98.80B tok)+s9运行中(42GB,~74%,ETA~09:45) | l1_en_hq 12进程运行中(s12-s23,各3.85GB.bin,ETA~15:00-16:00)。
- [06:52] **唤醒213**：①本机=`.12`。②**zh分词7shard(s4-s8,s10,s11)全部完成✅**：各~16.375M docs/~14.1B tok/~56.5GB.bin+327MB.idx,合计=**98.80B tokens**,耗时~8.9h/shard(~32000s).输出@`code/BaiZe-ISEDA2027/data/mix_base/mix_base_train_s{4,5,6,7,8,10,11}.bin/.idx`.s9仍在跑(37.8GB.bin,log@6.05M docs/5.22B tok,12495s,ETA~11:00).③**l1_en_hq分词启动✅**：12进程(s12-s23),各500 parquet/~37GB input,setsid ppid=1✅,主PID=758456+子PID759478~787625,nice-10,log@/tmp/baize_tokenize_l1_par/.load=15.33/224(可控).④**GPIC** 5686/8001(+1 since 06:52,rate~48tar/h,未受影响),PID144981活.⑤git pull=Already up to date,无新运维指令.⑥📦体积:TASK=30.1KB✅/MEMORY=21.6KB✅.下载线心跳：base ✅全满 | GPIC 5686/8001（活PID144981,~48tar/h,ETA~2.2d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7/8shard完成(98.80B tok)+s9运行中(37.8GB,ETA~11:00) | l1_en_hq 12进程启动(s12-s23,ETA~16:00)。
- [06:04] **唤醒212**：①本机=`.12`。②**zh分词巡检**：7shard(s4-s8,s10,s11)各.bin=49.6-53.2GB@06:05(mtime活跃,bin仍在写,无.idx),log@12.1M docs/10.4B tok(24262-24818s,**自~04:25未更新~100min=logs已停在12.1M docs=全部32 parquet读完,进入final write/index phase**),进程全活(PID2574412~2575292,etimes=30561s≈8.5h,ppid=2574340✅).按log 7×10.4B=72.8B tok(按.bin~50GB/int32则~12.5B/shard=87.5B合计,差异=final flush尚未完成).**ETA:7shard.idx应~1h内出现**.s9@31.9GB(+6.6GB since唤醒211@05:27,rate~9.9GB/h),log@6.05M docs/5.22B tok(12495s,stalled~98min),PID286565活(etimes=18551s≈5.1h,ppid=286557✅),~60%done by .bin,ETA~10:00.s0-s3✅(en base,21GB+.idx,22.05B tok).③**GPIC** 5650/8001(+31 since唤醒211@05:27,~46.5tar/h)+128/128 test✅,PID144981活(etimes≈302000s≈83.9h,cwd=/nas_inference/.../datasets),latest tar=gpic_train_05649@06:06,无.incomplete,ETA(8001-5650)/46.5≈50.6h≈2.1d.④**base**✅全满·**UltraX**✅479/479·**en_v1_4**排队.⑤git pull(proxy)成功=Already up to date,无新运维指令.⑥load=13.76/224核(I/O争用已消退).⑦📦体积:TASK=30.1KB✅/MEMORY=归档前31.4KB→归档唤醒191-200(9条→daily-memories-data/2026-10-08.md)→待测.⑧l1_en_hq分词脚本就绪(baize_tokenize_l1_en_hq_parallel.sh,bash -n✅),待zh跑完后启动.下载线心跳：base ✅全满 | GPIC 5650/8001（活PID144981,+31,~47tar/h,ETA~2.1d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7进程@50GB final-write-phase无.idx+s9@32GB~60%（ETA~07:30/10:00）。
- [05:27] **唤醒211**：①本机=`.12`。②**zh分词巡检**：7shard(s4-s8,s10,s11)各.bin=44-45GB@05:26(mtime活跃,bin仍在写,无.idx),log@12.1M docs/10.4B tok(24261s,自04:49未更新=rate<225docs/s,接近收尾),进程全活(PID2574412~2575292,etimes=28080s≈7.8h,ppid=2574340✅).按.bin 45GB/int32~11.3B tok/shard,7shard合计~79B tok→接近完成(ETA~07:00).s9@25.3GB(+2.3GB since 04:49,rate~3.7GB/h),log@6.05M docs/5.22B tok(12495s),PID286565活(etimes=15967s≈4.4h,ppid=286557✅),~56%done,ETA~09:00.s0-s3✅(en base,20.5GB+.idx,22.05B tok).③**GPIC** 5619/8001(+27 since 04:49,~43.8tar/h)+128/128 test✅,PID144981活(etimes=297091s≈82.5h,cwd=/nas_inference/.../datasets),latest tar=gpic_train_05619@05:26,ETA(8001-5619)/43.8≈54.4h≈2.3d,无.incomplete.④**base**✅全满·**UltraX**✅479/479·**en_v1_4**排队.⑤git pull(proxy)成功,无新运维指令.⑥load=13.81/224核(I/O争用已消退).⑦📦体积:TASK=30.1KB✅/MEMORY=30.6KB✅.⑧⭐**l1_en_hq分词脚本就绪**:`baize_tokenize_l1_en_hq_parallel.sh`(12 shard s12-s23,6000 parquet/446GB,6 CC-MAIN snapshots×1000 files,bash -n✅),待zh跑完后启动.下载线心跳：base ✅全满 | GPIC 5619/8001（活PID144981,+27,~44tar/h,ETA~2.3d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7进程@45GB~97%by_bin+s9@25GB~56%by_bin（ETA~07:00/09:00）。
- [04:49] **唤醒210**：①本机=`.12`。②**zh分词巡检**：7shard(s4-s8,s10,s11)各.bin=42-44GB@04:49(+6GB since 04:11,rate~9.5GB/h/shard,I/O争用已缓解),log@12.1M docs/10.4B tok(24262s),进程全活(PID2574412~2575292,etimes~25824s,ppid=2574340✅),无.idx.按.bin估算~79%done,ETA~07:00.s9@23GB(+5GB since 04:11,rate~7.9GB/h),log@6.05M docs/5.2B tok(12495s),PID286565活(etimes~13800s,ppid=286557✅),~41%done,ETA~10:00.s0-s3✅(en base,21GB+.idx).③**GPIC** 5592/8001(+29 since 04:11,~46tar/h)+128/128 test✅,PID144981活(etimes~295000s≈82h,cwd=/nas_inference/.../datasets),latest tar=gpic_train_05591@04:50,ETA(8001-5592)/46≈52.4h≈2.2d.④**base**✅全满·**UltraX**✅479/479·**en_v1_4**排队.⑤git fetch(proxy)成功,无新运维指令.⑥load=54.8/224核.⑦📦体积:TASK=30.1KB✅/MEMORY=29.6KB✅.下载线心跳：base ✅全满 | GPIC 5592/8001（活PID144981,+29,~46tar/h,ETA~2.2d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7进程@44GB~79%by_bin+s9@23GB~41%by_bin（ETA~07:00/10:00）。
- [04:11] **唤醒209**：①本机=`.12`。②**zh分词巡检**：7shard(s4-s8,s10,s11)各.bin=37-38GB@04:11(+1.5GB since 03:35,rate~2.5GB/h/shard,I/O争用减速),log仍@6.05M docs/5.22B tok(buffer lag,实际>6.05M),进程全活(PID2574412~2575292,etimes=23579s,ppid=2574340✅),无.idx.按.bin估算~68%done,ETA~07:00.s9@18GB(+2.7GB,rate~4.5GB/h),log@5.6M docs/4.83B tok(10797s),PID286565活(etimes=11569s,ppid=286557✅),~32%done,ETA~10:30.s0-s3✅(en base,21GB+.idx).③**GPIC** 5563/8001(+29 since 03:35,~48tar/h)+128/128 test✅,PID144981活(etimes=292693s≈81h),ETA(8001-5563)/48≈50.8h≈2.1d.④**base**✅全满·**UltraX**✅479/479·**en_v1_4**排队.⑤git fetch(proxy)成功,无新运维指令.⑥load=50.6/224核.⑦📦体积:TASK=30.1KB✅/MEMORY=31.5KB✅.下载线心跳：base ✅全满 | GPIC 5563/8001（活PID144981,+29,~48tar/h,ETA~2.1d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7进程@38GB~68%by_bin+s9@18GB~32%（ETA~07:00/10:30）。
- [03:35] **唤醒208**：①本机=`.12`。②**zh分词巡检**：7shard(s4-s8,s10,s11)全同步@6.05M docs/5.22B tok/.bin~36.5GB(log@~11750s),进程全活(PID2574412~2575292,etimes=21270s,ppid=2574340✅),log缓冲滞后(actual>6.05M,by .bin~65%done).s9@15.32GB(PID286565,etimes=9260s,ppid=286557✅),log含旧run条目(10797s系崩溃前),当前run~4.8M docs~28%done.ETA:7shard~07:00/s9~10:30.③**GPIC** 5534/8001(+58 since 02:18,~46tar/h)+128/128 test✅,PID144981活(etimes=290384s≈80h),ETA~2.2d.④**base**✅全满·**UltraX**✅479/479·**en_v1_4**排队.⑤git fetch(proxy)成功,无新运维指令.⑥load=48.2/224核.⑦📦体积:TASK=30.1KB✅/MEMORY=31.2KB✅.下载线心跳：base ✅全满 | GPIC 5534/8001（活PID144981,+58,~46tar/h,ETA~2.2d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 7进程@36.5GB~65%by_bin+s9@15.3GB~28%（ETA~07:00/10:30）。
- [03:00] **唤醒207**：①本机=`.12`。②⭐**修report_data_mix_summary.html数据错误**：复核topk_lmeval_results_r2.json发现t38的math值报告写0.005(系1−web−code残差),JSON实际为0.01(搜索空间下界)。Top-10表(line113)+核心结论表(line215)两处已修正为0.010。修正后top-5中4/5 math=0.01(TL;DR/§5.3原文即如此写,此前表格与文字矛盾,现已一致)。③全量数字复核:5 trial的web/code/math/bo_score/full_avg全部与JSON逐位匹配✅;Spearman ρ=−0.80(d²=36,n=5)手算确认✅。④📦体积:TASK=30.1KB✅/MEMORY=30.7KB✅。⑤zh分词/GPIC后台进行中(未巡检,下轮补)。
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
| PHASE | **配比实验全部交付✅ → 后台: zh分词7/8shard完成(98.80B tok)+s9~74%done + l1_en_hq分词12进程(s12-s23,各~3.85GB.bin) + GPIC 5714/8001** |
| WAITING | 1（GPIC下载进行中5714/8001 ETA~2.1d; s9 zh分词进行中ETA~09:45; l1_en_hq分词12进程进行中ETA~15:00-16:00） |
| ERROR_COUNT | 1（s9崩溃重启后稳定运行,part-172待s9完成后补tokenize） |
| 节点 | `10.239.2.29`（全8GPU空闲0MiB）+`.12`（GPIC下载PID=144981活 + zh分词s9 PID286565活 + l1_en_hq分词12进程PID759478~787625活 nice-10） |
| 更新 | 2026-10-08 07:29 |

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

