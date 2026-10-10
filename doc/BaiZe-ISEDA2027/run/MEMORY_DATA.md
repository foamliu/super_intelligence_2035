# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅web分词完成(524.43B)+✅全量污染扫描清洁(160K docs全0)+GPIC train 7920/8001(99.0%,ETA~2h→~11:00)+🔄R3全量分词108/110done(2活,nice-10,ppid=1✅,0 fatal,108.idx[40l3✅+28code+40math✅],code 28/30,2rem=s8/s9 .bin=126-132G actively writing,~92-96% of s10 ref,ETA~1-2h)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43; s_step归因(MBS16:8.6×,166ms); Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); zh分词8/8✅(112.47B); 论文更新(4+5节,main.pdf 0err); l1_en_hq分词12/12✅(152.17B); ultrax分词s34-s43✅(30.97B); en_base分词s24-s33✅(206.76B); ✅投料前污染采样扫描(10K docs,0命中); ✅全量污染扫描(30 parquet×5K=150K docs,0命中,累计160K docs全0命中); ✅④Ultra-FineWeb核实(197GB=nas_inference小副本≠tokenization源,524.43B×4B=2.1T≈2.0T .bin✅); ✅R3 L3全完工(40/40=658.91B tok); ✅R3 math全完工(40/40=274.92B tok); ✅R3 code_s10完工(34.44B tok/137.8GB); R3 108/110done(40l3=658.91B+28code done=482.34B+2code growing~64.8B+40math=274.92B=1416.18B done+2growing,2进程继续)
当前动作:     唤醒286(09:08@.12) R3全量分词监控:108/110done(+1 since 285,code_s10✅COMPLETE=34.44B tok/137.8GB json finalized process gone),2活=2code[s8(PID3752686,php-00030/38files,.bin=126.2GB=92%of s10,mtime09:10 actively writing),s9(PID3752952,php-00068/38files,.bin=132.2GB=96%of s10,mtime09:10 actively writing)],ppid=1✅,0 fatal,nice=10,stat=RNl,runtime=22.7h,.bin=5.6TB(l3=2.4T+code=2.0T+math=1.1T),108.idx+108.json(l3=40[658.91B]+code=28done[482.34B]+math=40[274.92B]=1416.18B done+2code growing[~64.8B]=~1481B total),L3✅40/40,math✅40/40,code 28/30done,2rem:s8/s9 all PHP,ETA~1-2h→~10:00-11:00,load=21/224(↓from 93),disk 83%38T free✅;GPIC train=7920/8001(+23 since 285,~42tar/h,活PID144981[ppid=3525273],latest=07918.tar,128test✅,1.incomplete,ETA~2h→~11:00);run_contam_scan_r3.sh就绪(30files×2K=60K docs,待code 30/30后启动);6目录盘点:①Ultra-FineWeb 197G/162pq✅524.43B(产物已清) ②L3 1.8T/1764pq✅40/40=658.91B ③Code 1.2T/1121pq🔄28/30=482.34B+growing ④Math 515G/1823pq✅40/40=274.92B ⑤SFT-2605 298G/1504jsonl✅20.96B(产物已清) ⑥SFT-Agent 51G/50jsonl✅8.04B(产物已清)
下一步:       ①R3全量分词监控(108/110done,2活,code ETA:s8/s9~1-2h→~10:00-11:00)→全部完成后启动run_contam_scan_r3.sh→报"P-8数据层全就绪"; ②GPIC续下(train 7920/8001,ETA~2h→~11:00); ③en_v1_4排队等运维放行(GPIC完成后,用户操作)
阻塞:         R3全量分词进行中(108/110done,2活,ETA:s8/s9~10:00-11:00); GPIC下载进行中(train 7920/8001,ETA~2h→~11:00)
ERROR_COUNT:  1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒185-190 已归档 → `daily-memories-data/2026-10-07.md`（含BO方向bug调查全链+UltraX启动+zh分词启动详情）
> 📦 唤醒201-203 已归档 → `daily-memories-data/2026-10-08.md`（含report_data_mix_summary.html产出+zh分词8进程启动+GPIC巡检）
> 📦 唤醒220-224 已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq 12进程巡检全链+en_base/ultrax启动+GPIC巡检）
> 📦 唤醒223-224 已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq 86-94%巡检+en_base/ultrax起步巡检+GPIC巡检）
> 📦 唤醒225-226 原文已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq s12-s15完成+en_base起步+ultrax s34-s42完成+GPIC巡检）
> 📦 唤醒253-255 原文已归档 → `daily-memories-data/2026-10-09.md`（含运维指令③执行:kill34旧进程+删46产物+smoke test 7源+核实197GB+创建run_tokenize_r3.sh+启动110进程+6目录盘点）
> 📦 唤醒256-259 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 110进程启动巡检全链+GPIC巡检+l3_s39首shard完工+6目录盘点+④核实结论）

> 📦 唤醒259 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 109/110进程巡检+l3_s39完工+GPIC纠正误计+6目录盘点+ETA重估1.404T tok→5.6TB .bin）
> 📦 唤醒260-261 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 102-109进程巡检+.bin 1.49→2.0TB+8.idx[1l3+7math]+GPIC 7106→7137+ETA 10-15h）
> 📦 唤醒279 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 96/110巡检+L3✅40/40+创建run_contam_scan_r3.sh+GPIC 7726/8001）




> 📦 唤醒273-279 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3分词72→97/110全程巡检+GPIC 7528→7726+code_s13完工+6目录盘点+体积自检）

> 📦 唤醒280 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 97/110巡检+code 17/30+GPIC 7757/8001+体积归档）

> 📦 唤醒271-272 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3分词59-60/110巡检+GPIC 7453-7489+6目录盘点）

- [09:08] **唤醒286**：①本机=`.12`,load=21.21/224(↓↓from 93,code进程大幅减少)。②R3分词巡检:**108/110done**(+1 since 285,**code_s10✅COMPLETE**=34.44B tok/9.49M docs/137.8GB.bin/.idx/.json all finalized,process gone),**2活=2code**[s8(PID3752686,php-00030/38files,.bin=126.2GB=92%of s10 ref,mtime09:10 actively writing),s9(PID3752952,php-00068/38files,.bin=132.2GB=96%of s10 ref,mtime09:10 actively writing)],ppid=1✅,0 fatal,nice=10,stat=RNl,runtime=22.7h(10:23 Oct9启动),.bin=**5.6TB**(l3=2.4T+code=2.0T+math=1.1T,code含growing),**108.idx+108.json**(l3=40[658.91B]+code=28done[**482.34B**]+math=40[274.92B]=**1416.18B done**+2code growing[~64.8B est]=**~1481B total**),L3✅40/40,math✅40/40,**code 28/30done**(+s10 since 285),2rem:s8/s9 **all PHP**(s8 on php-00030/38files s9 on php-00068/38files,both .bin=126-132GB≈92-96% of s10=137.8GB→near final,ETA~1-2h→~10:00-11:00),disk 83%38T free✅。③**GPIC train=7920/8001**(+23 since 285@08:28,~42tar/h,活PID144981[ppid=3525273],latest=07918.tar,**128test✅**,1.incomplete(downloading 07920),ETA~2h→~11:00)。④run_contam_scan_r3.sh就绪(30files×2K=60K docs,待code 30/30后启动→写CONTAMINATION_CHECK.md→报"P-8数据层全就绪")。⑤**6目录盘点**:①Ultra-FineWeb 197G/162pq✅524.43B(产物已清) ②L3 1.8T/1764pq✅40/40=658.91B ③Code 1.2T/1121pq🔄28/30=482.34B+growing ④Math 515G/1823pq✅40/40=274.92B ⑤SFT-2605 298G/1504jsonl✅20.96B(产物已清) ⑥SFT-Agent 51G/50jsonl✅8.04B(产物已清)。⑥git fetch(proxy)=up to date(无data新指令)。⑦📦体积:TASK=28.7KB/MEMORY=24.4KB✅(归档唤醒245/279/280/281/283→daily-memories-data/2026-10-10.md,释放~6KB)。下载线心跳：base✅全满|GPIC train 7920/8001(活PID144981,+23,~42tar/h,ETA~2h→~11:00)|R3 108/110done(.bin=5.6T,1416.18B+growing tok,L3✅+Math✅,code 2活 ETA~10:00-11:00)。

- [08:28] **唤醒285**：①本机=`.12`,load=93.14/224。②R3分词巡检:**107/110done**(+1 since 284,3活=3code[s8,s9,s10],ppid=1✅,0 fatal,nice=10,stat=RNl),runtime=22h(10:23启动),.bin=**5.6TB**(l3=2.4T+code=2.2T+math=1.1T,code含growing),**107.idx+107.json**(l3=40[658.91B]+code=27done[447.90B]+math=40[274.92B]=**1381.73B done**+3code growing[~90B est]=**~1472B total**),L3✅40/40,math✅40/40,**code 27/30done**(+1 since 284:code_s1@~08:15 completed[29.24B,109G.bin]),3rem:s8/s9/s10 **all PHP**(s8=31php+7js,s9=38php,s10=38php,/proc/fd shows s8 reading php-0028/38files s9 reading php-0067/38files s10 reading php-0106/38files),.bin=113-134G **actively writing**(mtime08:28,growth~2.2-2.4MB/s,ETA:s10~1h→~09:30 s9~1.5h→~10:00 s8~5-7h→~14:00-16:00[10files rem:3php+7js]),disk 83%38T free✅。③**GPIC train=7897/8001**(+23 since 284@07:55,~42tar/h,活PID144981[ppid=3525273],latest=07896.tar,**128test✅**,1.incomplete,ETA~2.5h→~11:00)。④run_contam_scan_r3.sh就绪(30files×2K=60K docs,待code 30/30后启动→写CONTAMINATION_CHECK.md→报"P-8数据层全就绪")。⑤6目录盘点:①Ultra-FineWeb 197G/162pq✅524.43B(产物已清) ②L3 1.8T/1764pq✅40/40=658.91B ③Code 1.2T/1121pq🔄27/30=447.90B+growing ④Math 515G/1823pq✅40/40=274.92B ⑤SFT-2605 298G/1504jsonl✅20.96B(产物已清) ⑥SFT-Agent 51G/50jsonl✅8.04B(产物已清)。⑥git pull(proxy)=up to date(无data新指令)。⑦📦体积:TASK=28.7KB/MEMORY=28.8KB✅(无需归档)。下载线心跳：base✅全满|GPIC train 7897/8001(活PID144981,+23,~42tar/h,ETA~11:00)|R3 107/110done(.bin=5.6T,1381.73B+growing tok,L3✅+Math✅,code 3活 ETA:s10~09:30 s9~10:00 s8~14:00-16:00)。

- [07:55] **唤醒284**：①本机=`.12`,load=100.95/224。②R3分词巡检:**106/110done**(+2 since 283,4活=4code[code_s1,s8,s9,s10],ppid=1✅,0 fatal,nice=10,stat=RNl),runtime=21.5h(10:23启动),.bin=**5.4TB**(l3=2.4T+code=2.0T+math=1.1T,code含growing),**106.idx+106.json**(l3=40[658.91B]+code=26done[418.66B]+math=40[274.92B]=**1352.49B done**+4code growing[~120B est]=**~1472B total**),L3✅40/40,math✅40/40,**code 26/30done**(+2 since 283:s0@07:19[29.47B]+s5@07:38),4rem:s1/s8/s9/s10 .bin=114-128G **actively writing**(mtime07:53,each 38pq/~39-40GB input,s1=114.5G s8=116.8G s9=122.4G s10=128.7G,completed ref:s0=109.8G s4=102.9G,these are larger→denser lang/more tokens,ETA~1-3h→~09:00-11:00),disk 83%38T free✅。③**GPIC train=7874/8001**(+29 since 283@07:13,~44tar/h,活PID144981[ppid=3525273],latest=07873.tar,**128test✅**,1.incomplete,ETA~2.9h→~10:50)。④run_contam_scan_r3.sh就绪(30files×2K=60K docs,待code 30/30后启动→写CONTAMINATION_CHECK.md→报"P-8数据层全就绪")。⑤6目录盘点:①Ultra-FineWeb 197G/162pq✅524.43B(产物已清) ②L3 1.8T/1764pq✅40/40=658.91B ③Code 1.2T/1121pq🔄26/30=418.66B+growing ④Math 515G/1823pq✅40/40=274.92B ⑤SFT-2605 298G/1504jsonl✅20.96B(产物已清) ⑥SFT-Agent 51G/50jsonl✅8.04B(产物已清)。⑥git pull(proxy)=up to date(无data新指令)。⑦📦体积:TASK=28.7KB/MEMORY=27.2KB✅(无需归档)。下载线心跳：base✅全满|GPIC train 7874/8001(活PID144981,+29,~44tar/h,ETA~10:50)|R3 106/110done(.bin=5.4T,1352.49B+growing tok,L3✅+Math✅,code 4活 ETA~09:00-11:00)。

> 📦 唤醒283 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 104/110巡检+code 24/30+GPIC 7845/8001）

- [06:35] **唤醒282**：①本机=`.12`,load=53.87/224。②R3分词巡检:**101/110done**(+2 since 281,9活=9code[code_s0,s1,s5-s11],ppid=1✅,0 fatal,nice=10,stat=RNl/SNl),runtime=20.2h(10:23启动),.bin=**5.4TB**(l3=2.4T+code=2.0T+math=1.1T,code含growing),**101.idx+101.json**(l3=40[658.91B]+code=21[279.85B]+math=40[274.92B]=**1213.68B tok**),L3✅40/40,math✅40/40,**code 21/30done**(s2/s3/s4/s12-s29 done,+s2=26.42B+s4=27.62B since 281),9rem:s0/s1/s5-s11 .bin=96-113GB,**actively writing**(mtime06:37),s0=113.4G≥completed s4=110.5G→near final,completed ref:s2=105.7G/26.42B,s3=104G/26.0B,s4=110.5G/27.62B,ETA~30-60min→~07:15,disk 83%38T free✅。③**GPIC train=7817/8001**(+29 since 281@05:57,~46tar/h,活PID144981[ppid=3525273],latest=07816.tar@06:34,**128test✅**,1.incomplete,ETA~4h→~10:30)。④run_contam_scan_r3.sh就绪(30files×2K=60K docs,待code 30/30后启动→写CONTAMINATION_CHECK.md→报"P-8数据层全就绪")。⑤6目录盘点:①Ultra-FineWeb 197G/162pq✅524.43B(产物已清) ②L3 1.8T/1764pq✅40/40=658.91B ③Code 1.2T/1121pq🔄21/30=279.85B ④Math 515G/1823pq✅40/40=274.92B ⑤SFT-2605 298G/1504jsonl✅20.96B(产物已清) ⑥SFT-Agent 51G/50jsonl✅8.04B(产物已清)。⑥git fetch(proxy)=up to date(无data新指令)。⑦📦体积:TASK=28.7KB/MEMORY=24.1KB✅(无需归档)。下载线心跳：base✅全满|GPIC train 7817/8001(活PID144981,+29,~46tar/h,ETA~10:30)|R3 101/110done(.bin=5.4T,1213.68B tok,L3✅+Math✅,code 9活 ETA~07:15)。

> 📦 唤醒281 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 99/110巡检+code 19/30+GPIC 7916/8001）



> 📦 唤醒262-267 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3分词巡检全链+GPIC巡检+6目录盘点+④核实结论+ETA递进）

> 📦 唤醒256-258 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 110进程启动后2h巡检全链+.bin从736GB→1.3TB增长+GPIC 6987→7019+6目录盘点）

> 📦 唤醒247-251 原文已归档 → `daily-memories-data/2026-10-09.md`（含运维指令①②执行+smoke test+11进程启动+GPIC 6734→6839巡检全链）

> 📦 唤醒227-246 原文已归档 → `daily-memories-data/2026-10-08.md` 及 `2026-10-09.md`（含l1_en_hq/en_base/ultrax分词全链+全量污染扫描✅150K docs 0命中+GPIC巡检）

> 📦 唤醒256-258 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 110进程启动后2h巡检全链+.bin从736GB→1.3TB增长+GPIC 6987→7019+6目录盘点）

> 📦 唤醒247-251 原文已归档 → `daily-memories-data/2026-10-09.md`（含运维指令①②执行+smoke test+11进程启动+GPIC 6734→6839巡检全链）

> 📦 唤醒227-233 原文已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq s18-s19完成+en_base起步+ETA纠正+GPIC巡检全链）





> 📦 唤醒245 原文已归档 → `daily-memories-data/2026-10-10.md`（含全量污染扫描启动+GPIC 6677/8001+.29 GPU空5卡+体积18.6KB）
> 📦 唤醒243-244 原文已归档 → `daily-memories-data/2026-10-09.md`（含en_base s24-s33全完成206.76B+投料前污染扫描10K docs 0命中+GPIC巡检）
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
| PHASE | **✅web分词完成(524.43B tok) + ✅全量污染扫描完成(160K docs,0命中) + GPIC train 7897/8001(ETA~2.5h→~11:00) + 🔄R3全量分词107/110done(3活,.bin=5.6TB,107.idx[40l3✅+27code+40math✅,1381.73B+growing tok],code_s8/s9/s10 actively writing ETA:s10~09:30 s9~10:00 s8~14:00-16:00)** |
| WAITING | 1（R3分词ETA:s10~09:30 s9~10:00 s8~14:00-16:00; GPIC train 7897/8001 ETA~2.5h→~11:00; en_v1_4排队等放行GPIC完成后） |
| ERROR_COUNT | 1（s9崩溃重启后已完成） |
| 节点 | `10.239.2.12`（GPIC下载PID=144981活, .12 GPU全忙vision R9, .29 GPU全忙pretrain, R3分词3进程nice-10） |
| 更新 | 2026-10-10 08:28 |

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

> 📦 §s_step归因实验（2026-10-06）已归档 → `daily-memories-data/2026-10-06.md`；**结论**：MBS=16使s_step 1432ms→166ms(8.6×),overhead-bound,D=0.5B/trial→205trial/24h。需要时再读。
## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

