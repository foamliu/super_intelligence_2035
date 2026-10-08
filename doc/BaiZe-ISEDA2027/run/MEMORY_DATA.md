# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        后台巡检: l1_en_hq 10/12done(122.94B)+s18-s19进行中(2进程,ETA~16:30-17:00) + en_base 10进程(s24-s33,~20%,ETA~21:00-22:00) + ultrax 9/10done(26.66B)+s43进行中(ETA~min) + GPIC 6089/8001
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43+report; s_step归因(MBS16:8.6×,166ms)+report; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾全完成(ρ=−0.80); report_data_mix_eval_r2.html+report_data_mix_summary.html+report_data_pipeline_status.html; zh分词8/8✅(113.47B tok); ✅论文更新(4+5节,main.pdf 0err); ✅l1_en_hq分词s12-s17+s20-s23完成(122.94B tok); ✅ultrax分词s34-s42完成(26.66B tok); ✅en_base分词启动(s24-s33); ✅ultrax分词启动(s34-s43)
当前动作:     唤醒226(16:01@.12) 巡检后台(l1_en_hq 10/12done+s18-s19进行中+en_base+ultrax 9/10done+s43即将完成+GPIC 6089/8001)+心跳更新
下一步:       ①s18-s19完成(ETA~16:30-17:00)→报l1总token+过check_contamination; ②s43完成(ETA~min)→报ultrax总token; ③en_base s24-s33完成(ETA~21:00-22:00); ④GPIC续下(6089/8001,ETA~1.77d); ⑤en_v1_4排队等放行; ⑥新分词产物投料前过check_contamination.py
阻塞:         l1_en_hq s18-s19进行中(ETA~16:30-17:00); en_base s24-s33进行中(ETA~21:00-22:00); ultrax s43进行中(ETA~min); GPIC下载进行中(6089/8001,ETA~1.77d)
ERROR_COUNT:  1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒185-190 已归档 → `daily-memories-data/2026-10-07.md`（含BO方向bug调查全链+UltraX启动+zh分词启动详情）
> 📦 唤醒201-203 已归档 → `daily-memories-data/2026-10-08.md`（含report_data_mix_summary.html产出+zh分词8进程启动+GPIC巡检）
- [12:01] **唤醒220**：①本机=`.12`。②**l1_en_hq分词巡检**：12进程(s12-s23)全活(100%CPU,PID759478~787625,ppid=758456✅,nice-10,etimes~18540s≈5.15h,06:52:45启动)。shard日志显示各@6,050,000 docs/~6.0-6.55B tok（rate~432 docs/s）。各.bin~26.4-26.9GB(总s12-s23=~319GB=86B tok current)。无.idx(仍在写)。ETA按.bin growth法：26.6GB@5.15h,expected~47GB→remaining~20GB→~4h→finish~16:00。load=19.48/224核(可控)。③**GPIC** 5917/8001(+26 since 11:26,~44.6tar/h)+128/128 test✅,PID144981活(etimes~320897s≈3.7d),cwd=/nas_inference/.../datasets,latest tar=gpic_train_05916@~11:50,正在下gpic_train_05917.tar,ETA(8001-5917)/44.6≈46.7h≈1.9d。④**Token inventory**：s0-s3(en base)=20B✅(.idx有)·s4-s11(zh)=109B✅(.idx有)·s12-s23(l1_en_hq)=86B进行中→预计~155B→grand total~284B(P-8 target~100B✅远超)。⑤base✅全满·UltraX✅479/479·en_v1_4排队。⑥git fetch(proxy)=up to date,无新运维指令。⑦📦体积:TASK=28.8KB✅/MEMORY=~31KB✅(无需归档)。下载线心跳：base ✅全满 | GPIC 5917/8001（活PID144981,+26,~44.6tar/h,ETA~1.9d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(~109B tok) | l1_en_hq 12进程(s12-s23,各26.6GB.bin,6.05M docs,86B tok,ETA~16:00)。
- [12:41] **唤醒221**：①本机=`.12`。②**l1_en_hq分词巡检**：12进程(s12-s23)全活(100%CPU,PID759478~787625,ppid=758456✅,nice-10,etimes~20800s≈5.78h,06:52:45启动)。通过/proc/PID/fd检查当前处理文件：s12@CC-2025-30/part-0348/500,s13@CC-2025-30/part-0846/500,s23@CC-2025-51/part-0832/500→各~68%files done。各.bin~30-31GB(总s12-s23=~366GB=97B tok current,总mix_base=894GB)。无.idx(仍在写)。ETA按file-count法：68%@5.78h→total~8.5h→finish~15:22。load=19.65/224核(可控)。③**GPIC** 5945/8001(+28 since 12:01,~45.4tar/h)+128/128 test✅,PID144981活(etimes~323122s≈3.7d),latest tar=gpic_train_05944@12:38,ETA(8001-5945)/45.4≈45.3h≈1.9d。④**Token inventory**：s0-s3(en base)=20B✅(.idx有)·s4-s11(zh)=109B✅(.idx有)·s12-s23(l1_en_hq)=97B进行中→预计~130B→grand total~259B(P-8 target~100B✅远超)。⑤base✅全满·UltraX✅479/479·en_v1_4排队。⑥git fetch(proxy)=up to date,无新运维指令。⑦📦体积:TASK=28.1KB✅/MEMORY=30.9KB✅(归档唤醒207-210→daily)。下载线心跳：base ✅全满 | GPIC 5945/8001（活PID144981,+28,~45.4tar/h,ETA~1.9d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(~109B tok) | l1_en_hq 12进程(s12-s23,各30.5GB.bin,68%files,97B tok,ETA~15:30)。
- [13:21] **唤醒222**：①本机=`.12`。②**l1_en_hq分词巡检**：12进程(s12-s23)全活(100%CPU,PID759478~787625,ppid=758456✅,nice-10,etimes~23116s≈6.4h,06:52:45启动)。/proc/PID/fd: s12@CC-2025-30/part-0392/500→78%files done。各.bin~36-37GB(总s12-s23=410.8GB≈100B tok current)。无.idx(仍在写)。ETA: 78%@6.4h→remaining~108files@66files/h→~1.6h→finish~15:00。③**🆕en_base分词**(s24-s33): 10进程(PPID 3251929=baize_tokenize_en_base_parallel.sh,ppid=1✅,nice-10,13:12启动,~8min)。450 files(part-0049..0498,~202B tok预期),45 files/shard。.bin总8.26GB(刚起步)。④**🆕ultrax分词**(s34-s43): 10进程(PPID 3440299=baize_tokenize_ultrax_parallel.sh,ppid=1✅,nice-10,13:14启动,~6min)。165 files(104 FineWeb+61 AICC,~100B tok预期),~17 files/shard。.bin总6.12GB(刚起步)。两脚本未提交→本轮补提交。⑤load=37.94/224核(32进程@100%CPU=14.3%,可控)。⑥**GPIC** 5972/8001(+27 since 12:41,~42.6tar/h)+128/128 test✅,PID144981活(etimes~328000s≈3.8d),latest tar=gpic_train_05971@13:19,ETA(8001-5972)/42.6≈47.6h≈2.0d。⑦**Token inventory**: s0-s3(en base)=20B✅(.idx有)·s4-s11(zh)=109B✅(.idx有)·s12-s23(l1_en_hq)=100B进行中(78%,ETA~15:00)·s24-s33(en_base)=起步→预期~202B·s34-s43(ultrax)=起步→预期~100B→grand total预期~531B(P-8 target~100B✅远超)。⑧.29: 8GPU占(pretrain R3 BO,各62.6GB,25-91%util)。⑨base✅全满·UltraX✅479/479·en_v1_4排队。⑩git fetch(proxy)=up to date,无新运维指令。⑪📦体积:TASK=28.2KB✅/MEMORY=28.8KB✅(无需归档)。下载线心跳：base ✅全满 | GPIC 5972/8001（活PID144981,+27,~42.6tar/h,ETA~2.0d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(~109B tok) | l1_en_hq 78%files(s12-s23,各36GB.bin,100B tok,ETA~15:00) | en_base s24-s33起步(8.3GB.bin,~202B tok预期) | ultrax s34-s43起步(6.1GB.bin,~100B tok预期)。
- [13:57] **唤醒223**：①本机=`.12`。②**l1_en_hq分词巡检**：12进程(s12-s23)全活(100%CPU,PID759478~787625,ppid=758456✅,nice-10,etimes~25480s≈7.1h)。s12@part-0429-of-1000→429/500=85.8%files done。各.bin~37.0-37.8GB(总s12-s23=~449GB≈109B tok current)。无.idx(仍在写)。rate:+37files in 36min→61.7files/h。ETA:(500-429)/61.7≈1.15h→finish~15:10。s12 log@6.05M docs/6.07B tok(16209s),s23 log@6.05M docs/6.55B tok(17035s)。③**en_base分词**(s24-s33): 10进程全活(100%CPU,PPID3251929,ppid=1✅,nice-10,etimes~2700s≈45min)。s24@part-0051→3/45files≈6.7%。.bin各~4.0GB(总~40GB≈10B tok)。刚起步,ETA待估。④**ultrax分词**(s34-s43): 10进程全活(100%CPU,PPID3440299,ppid=1✅,nice-10,etimes~2549s≈42min)。s34@UltraX-FineWeb-en-part-0006→6/~17files≈35%。.bin各~3.9GB(总~39GB≈10B tok)。刚起步,ETA待估。⑤load=37.36/224核(32进程@100%CPU=14.3%,可控)。⑥**GPIC** 6000/8001(+28 since 13:21,~46.7tar/h)+128/128 test✅,PID144981活(etimes~327835s≈3.8d),downloading gpic_train_06000.tar,latest=gpic_train_05999@13:58,ETA(8001-6000)/46.7≈42.9h≈1.8d。⑦**Token inventory**: s0-s3=20B✅(.idx)·s4-s11=109B✅(.idx)·s12-s23=109B(86%,ETA~15:10)·s24-s33=10B(7%,起步)·s34-s43=10B(35%,起步)→grand total~258B current→~558B expected(P-8 target~100B✅远超)。⑧.29: 8GPU占(pretrain R3 BO,各62.6GB,41-80%util)。⑨base✅全满·UltraX✅479/479·en_v1_4排队。⑩git fetch(proxy)=up to date,无新运维指令。⑪📦体积:TASK=28.1KB✅/MEMORY=30.0KB✅(无需归档)。下载线心跳：base ✅全满 | GPIC 6000/8001（活PID144981,+28,~46.7tar/h,ETA~1.8d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(~109B tok) | l1_en_hq 86%files(s12-s23,各37.4GB.bin,109B tok,ETA~15:10) | en_base s24-s33起步(4GB.bin,~10B tok) | ultrax s34-s43起步(3.9GB.bin,~10B tok)。
- [14:36] **唤醒224**：①本机=`.12`。②**l1_en_hq分词巡检**：12进程(s12-s23)全活(100%CPU,PID759478~787625,ppid=758456✅,nice-10,etimes~27853s≈7.7h)。s12@part-0470-of-1000→470/500=94%files done。各.bin~41-42GB(总s12-s23=~498GB≈124B tok current)。无.idx(仍在写)。rate:+41files in 39min→63files/h。ETA:(500-470)/63≈0.48h→finish~15:05。③**en_base分词**(s24-s33): 10进程全活(100%CPU,PPID3251929,ppid=1✅,nice-10,etimes~5040s≈1.4h)。各shard 45 files(part-0049..0498),.bin各~7.4GB(总~74GB≈18.5B tok)。ETA~8-12h。④**ultrax分词**(s34-s43): 10进程全活(100%CPU,PPID3440299,ppid=1✅,nice-10,etimes~4920s≈1.4h)。各shard 16-21 files(165 total),.bin各~7.35GB(总~73.5GB≈18.4B tok)。ETA~4-6h。⑤load=38.39/224核(32进程@100%CPU=14.3%,可控)。⑥**GPIC** 6029/8001(+29 since 13:57,~44.6tar/h)+128/128 test✅,PID144981活(etimes~331000s≈3.8d),latest=gpic_train_06028@14:36,ETA(8001-6029)/44.6≈44.2h≈1.84d。⑦**Token inventory**: s0-s3=20B✅(.idx)·s4-s11=109B✅(.idx)·s12-s23=124B(94%,ETA~15:05)·s24-s33=18.5B(起步)·s34-s43=18.4B(起步)→grand total~290B current→~531B expected(P-8 target~100B✅远超)。⑧.29: 8GPU占(pretrain R3 BO,各62.6GB,51-81%util)。⑨base✅全满·UltraX✅479/479·en_v1_4排队。⑩git fetch(proxy)=up to date,无新运维指令。⑪📦体积:TASK=28.8KB✅/MEMORY=归档前31.8KB→归档唤醒211-218(8条→daily)→23.5KB✅。下载线心跳：base ✅全满 | GPIC 6029/8001（活PID144981,+29,~44.6tar/h,ETA~1.84d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(~109B tok) | l1_en_hq 94%files(s12-s23,各41.5GB.bin,124B tok,ETA~15:05) | en_base s24-s33(7.4GB.bin,~18.5B tok) | ultrax s34-s43(7.35GB.bin,~18.4B tok)。
- [15:19] **唤醒225**：①本机=`.12`。②**l1_en_hq分词**：s12-s15 DONE(4/12, s12=11.66B+s13=11.65B+s14=12.08B+s15=12.08B=47.47B tok, .idx/.json✅), s16-s23进行中(8进程,各.bin~45-46G,与完成shard同尺寸→即将完成,ETA~15:30-16:00)。Parent PID758456 ppid=1✅。③**en_base分词**(s24-s33): 10进程全活(PPID3251929,ppid=1✅,nice-10,~2.1h)。各.bin~12G(s0-s3完成时21G→~60%done),45 files/shard,ETA~16:30。④**ultrax分词**(s34-s43): s34-s40 DONE(7/10,19.80B tok,.idx/.json✅),s41-s43进行中(3进程,.bin~12G,与完成shard同尺寸→即将完成,ETA~15:30)。Parent PID3440299 ppid=1✅。⑤**Token inventory(确认)**：s0-s3=22.05B✅·s4-s11=113.58B✅·s12-s15=47.47B✅·s34-s40=19.80B✅→**已完成202.90B**·s16-s23预期~96B·s24-s33预期~52B·s41-s43预期~9B→grand total预期~360B(P-8 target~100B✅远超)。⑥**GPIC** 6062/8001(+33 since 14:36,~46tar/h)+128/128 test✅,PID144981活(~3.86d),latest=gpic_train_06061@15:20,1 .incomplete(正常),ETA(8001-6062)/46≈42.2h≈1.76d。⑦load=29.87/224核(21进程@100%CPU=9.4%,可控)。⑧disk:/nas_train 85%(32T free),/tmp 24%(72G free),mix_base=1.3T。⑨base✅全满·UltraX✅479/479·en_v1_4排队。⑩git fetch(proxy)=up to date,无新运维指令。⑪📦体积:TASK=28.8KB✅/MEMORY=23.5KB✅(无需归档)。下载线心跳：base ✅全满 | GPIC 6062/8001（活PID144981,+33,~46tar/h,ETA~1.76d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(113.58B tok) | l1_en_hq 4/12done(s12-s15=47.47B)+8进程(s16-s23,各45G.bin,ETA~15:30-16:00) | en_base 10进程(s24-s33,12G.bin,~60%,ETA~16:30) | ultrax 7/10done(s34-s40=19.80B)+3进程(s41-s43,ETA~15:30)。
- [16:01] **唤醒226**：①本机=`.12`。②**l1_en_hq分词**：10/12 DONE(s12-s17,s20-s23=.idx/.json✅=122.94B tok), s18-s19进行中(2进程:PID776097@part-0450/500=90%, PID779098@part-0947/500=95%, .bin各~49G, etimes~32821s≈9.1h, ETA~16:30-17:00)。Parent PID758456 ppid=1✅。③**en_base分词**(s24-s33): 10进程全活(PPID3251929,ppid=1✅,nice-10,~2.8h)。各.bin~16.5G(s24@part-0057/45files≈20%),45 files/shard,rate~5.9G/h→final~50G→ETA~21:00-22:00。④**ultrax分词**(s34-s43): 9/10 DONE(s34-s42=.idx/.json✅=26.66B tok), s43进行中(PID3441227@part-0060/0061≈98%,.bin~17G,即将完成ETA~min)。Parent PID3440299 ppid=1✅。⑤**Token inventory(确认)**：s0-s3=22.05B✅·s4-s11=113.47B✅·s12-s17+s20-s23=122.94B✅·s34-s42=26.66B✅→**已完成284.12B(31 shards with .idx)**·s18-s19预期~26B·s24-s33预期~200-400B·s43预期~4B→grand total预期~510-710B(P-8 target~100B✅远超)。⑥**GPIC** 6089/8001(+27 since 15:19,~45tar/h)+128/128 test✅,PID144981活(~3.9d),latest=gpic_train_06088@15:58,ETA(8001-6089)/45≈42.5h≈1.77d。⑦load=18.28/224核(13进程@100%CPU=5.8%,可控,s18-s19+s43即将完成→load将降)。⑧disk:mix_base=1.4T。⑨base✅全满·UltraX✅479/479·en_v1_4排队。⑩git fetch(proxy)=up to date,无新运维指令。⑪📦体积:TASK=28.8KB✅/MEMORY=25.9KB✅(无需归档)。下载线心跳：base ✅全满 | GPIC 6089/8001（活PID144981,+27,~45tar/h,ETA~1.77d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8/8✅(113.47B tok) | l1_en_hq 10/12done(122.94B)+s18-s19进行中(各49G.bin,90-95%,ETA~16:30-17:00) | en_base 10进程(s24-s33,16.5G.bin,~20%,ETA~21:00) | ultrax 9/10done(26.66B)+s43即将完成(17G.bin,98%)。
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
| PHASE | **后台: l1_en_hq 10/12done(122.94B)+s18-s19进行中(2进程,ETA~16:30-17:00) + en_base 10进程(s24-s33,~20%,ETA~21:00-22:00) + ultrax 9/10done(26.66B)+s43即将完成 + GPIC 6089/8001** |
| WAITING | 1（GPIC下载进行中6089/8001 ETA~1.77d; l1_en_hq s18-s19 ETA~16:30-17:00; en_base s24-s33 ETA~21:00; ultrax s43 ETA~min） |
| ERROR_COUNT | 1（s9崩溃重启后已完成,part-172待s9完成后补tokenize） |
| 节点 | `10.239.2.29`（8GPU占=pretrain R3 BO）+`.12`（GPIC下载PID=144981活 + l1_en_hq分词2进程(s18-s19) + en_base分词10进程(s24-s33) + ultrax分词1进程(s43), nice-10） |
| 更新 | 2026-10-08 16:01 |

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

