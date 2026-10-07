# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验全流程交付✅(含收官HTML) → 后台: GPIC 5386/8001 + zh分词并行化(8进程s4-s11,~17.2GB/shard@00:19,78%of en's22GB,ETA~01-02AM)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满；base分词(22.05B tok)；D-CLEAN-1/2/3/4；S0a已kill；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43+report; s_step归因(MBS16:8.6×,166ms)+report; Round2 BO✅200/200(166✅+34❌,best=t23=0.4155); base下载完成; R1 lm_eval errata更正; UltraX✅479 parquet(454GB,5config); ✅top-K收尾全完成(retrain5/5+HF转换+全量lm_eval+topk_lmeval_results_r2.json@19:40); ✅report_data_mix_eval_r2.html(18KB); Spearman ρ=−0.80(BO score vs full eval,n=5); ✅zh分词并行化(1→8进程,ETA 2.5d→~9.8h); ✅report_data_mix_summary.html(28.4KB,配比收官总报告,house style浅色,3内联SVG,8节全)
当前动作:     唤醒203(00:19@.12) 后台巡检: zh分词8进程s4-s11活(~17.2GB/shard@00:19,78%of en's22GB,no .idx yet,ETA~01-02AM)·GPIC 5386/8001(+53,~45tar/h,PID144981活)·base✅全满·UltraX✅479·report_data_mix_summary.html✅已交付(28.4KB)
下一步:       ①zh分词8进程跑完(ETA~01-02AM 10/8)→合入blend+报zh总token数; ②启动l1_en_hq分词(6000 parquet); ③GPIC续下(5386/8001,ETA~2.4d); ④en_v1_4排队等放行
阻塞:         zh分词并行化进行中(8进程s4-s11,~17.2GB/shard@00:19,ETA~01-02AM); GPIC下载进行中(5386/8001,ETA~2.4d)
ERROR_COUNT:  0
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒185-190 已归档 → `daily-memories-data/2026-10-07.md`（含BO方向bug调查全链+UltraX启动+zh分词启动详情）
- [00:19] **唤醒203**：①本机=`.12`。②**后台巡检**（运维指令⑤④P0全在跑，无需动作）：**zh分词**8进程s4-s11活(PID2574412~2575292,ppid=2574340→ppid=1✅,etimes=9695s≈2h41m)，各shard .bin=17.0-17.3GB@00:19（23:08时9.2GB→+8.0GB/71min=**6.8GB/h/shard,54.4GB/h total**），为en基线22GB的78%，no .idx yet（8进程仍99%CPU活），rate稳定，ETA~01-02AM 10/8（**远早于原估07AM**）。**GPIC** 5386/8001 train tar(+53 since 23:08,~44.8tar/h)+128/128 test✅，PID144981活(etimes≈76h+)，latest=gpic_train_05385.tar@00:19，ETA(8001-5386)/44.8≈58h≈2.4d。**base**✅全满(en2048+l1_en_hq 6006files/6dirs+zh256)。**UltraX**✅479/479。**en_v1_4**排队。③git fetch(proxy)成功，无新运维指令（最新ops=21:39 report令已执行）。④load=50.3/224核(nice-10可控)。⑤📦体积:TASK=30.8KB✅/MEMORY=29.8KB✅(均<32KB,无需归档)。⑥上轮push失败已恢复(commit6711eef5在origin/main✅,git status无ahead)。下载线心跳：base ✅全满 | GPIC 5386/8001（活PID144981,+53,~45tar/h,ETA~2.4d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8进程s4-s11（PID2574412~2575292,ppid=1✅,~17.2GB/shard@00:19,ETA~01-02AM）。
- [23:08] **唤醒202**：①本机=`.12`。②**后台巡检**（运维指令⑤④P0全在跑，无需动作）：**zh分词**8进程s4-s11活(PID2574412~2575292,ppid=2574340→ppid=1✅,etimes=5371s≈1.5h)，各shard .bin=9.1-9.3GB@23:08（22:35时5.8GB→+3.3GB/33min=**6.0GB/h/shard,48GB/h total**），no .idx yet（无shard完成），rate稳定，ETA~7h→~07AM 10/8。**GPIC** 5333/8001 train tar(+24 since 22:35,~43.6tar/h)+128/128 test✅，PID144981活(etimes=274619s≈76h)，ETA(8001-5333)/43.6≈61h≈2.5d。**base**✅全满(l1_en_hq 446GB/6006files+zh 256/256+en 2048/2048)，无hf download进程(base已结束)。**UltraX**✅479/479。**en_v1_4**排队。③load=52.5/224核(nice-10可控)。④📦体积:TASK=30.1KB✅/MEMORY=28.1KB✅(均<32KB,无需归档)。⑤⚠️**push失败**：GitHub Internal Server Error(Request ID DF24/DF28, 2次重试均失败)，commit 280b332c已本地[ahead 1]，**下一轮唤醒第一件事补推**。下载线心跳：base ✅全满 | GPIC 5333/8001（活PID144981,+24,~44tar/h,ETA~2.5d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8进程s4-s11（PID2574412~2575292,ppid=1✅,~9.2GB/shard@23:08,ETA~07AM）。
- [22:35] **唤醒201**：①本机=`.12`。②⭐**运维指令⑥: 配比收官总报告HTML**——产出`report_data_mix_summary.html`(28.4KB,落`doc/BaiZe-ISEDA2027/`)。8节全:TL;DR(5条)/实验设计(代理d=128/L=14/N≈18.36M+BO配置+R1vsR2 objective)/时间线(R1→s_step→R2→top-K→收官)/R2结果(Top-10配比表+score分布直方图SVG+score收敛曲线SVG)/核心结论(ρ=−0.80排名反转+0.6pp不可分辨+math贴下界+R1 ρ=−0.43对比)/口径局限(7项)/P-8建议(沿用88:8:4)/下一步(6方向)/数据来源(5文件可复算)。house style浅色(参照report_10_07_data_overnight.html)+3内联SVG+零外链+数字全可由topk_lmeval_results_r2.json/mix_search_eval_r2.db复算。③数据核对:R2 DB=166complete+34failed,score 0.3730-0.4155(avg0.3908);top-K 5trial全量avg 0.3835-0.3899(极差0.6pp);Spearman ρ=−0.80(d²=36,n=5,p≈0.10);R1 DB=200complete,loss 5.822-5.995。④zh分词:8进程s4-s11活(PID2574412~2575292,ppid=1✅),s4.bin=5.8GB@22:35(57min,~5.74GB/h/proc),ETA~9h。⑤GPIC:5309/8001(+31since21:36,~31tar/h,PID144981活)。⑥📦体积:TASK=30.8KB/MEMORY=待测。下载线心跳：base ✅全满 | GPIC 5309/8001（活PID144981,+31,~31tar/h,ETA~2.7d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8进程s4-s11（PID2574412~2575292,ppid=1✅,~5.8GB/shard@22:35,ETA~9h）。
- [21:33] **唤醒200**：①本机=`.12`。②⭐**运维指令⑤: zh分词并行化**——nproc=224,load=46,起步N=8(min(8,112))。kill旧单进程(PID2851334+2850810,33/256files,58GB s4.bin无idx=不可用),删s4.bin(58GB)。建`baize_tokenize_zh_parallel.sh`:256file→8组×32file→s4-s11,symlink到/tmp/mix_base_tok_zh_work/s{4..11},nice-n10,setsid(ppid=1✅),各独立log。21:38:45启动8×preprocess_data.py(PID2574412~2575292)。③⭐**实测吞吐**:T1(21:40:48)=1310MB→T3(21:49:11)=7728MB,delta=6418MB/503s=**45.9GB/h total(5.74GB/h/proc)**,7.8×speedup vs单进程(6.1GB/h)。每shard~56GB@5.74GB/h→**ETA~9.8h(~07:30AM 10/8)**,≤12h目标✅。④GPIC:5278/8001(+9since21:36,~42tar/h,**未掉速✅**),PID144981活。⑤load=47(nice-10可控,224核)。⑥📦体积:TASK=36.5KB→归档2块(三步令+配比改道→ARCHIVE)→**30.1KB✅**,MEMORY=待测。⑦⑥块(配比收官HTML)待写→下一步。下载线心跳：base ✅全满 | GPIC 5278/8001（活PID144981,+9,~42tar/h,ETA~2.7d）| UltraX ✅479完成 | en_v1_4 排队 | zh分词 8进程s4-s11（PID2574412~2575292,ppid=1✅,~7.7GB@21:49,45.9GB/h,ETA~9.8h）。
- [20:59] **唤醒199**：①本机=`.12`。②巡检所有后台任务——GPIC:5241/8001(+33since198,0incomplete,PID144981活,latest=05240,rate~40tar/h,ETA~2.7d)。UltraX:✅479parquet/454GB完成(0incomplete,进程已退出rc=0)。zh分词:s4.bin=57.5GB(+7.5GBsince198,PID2851334活99%CPU,fd77→正在读part-033-of-256,log buffered至18:34最后行=12.1Mdocs/10.43Btok/23359s,无.idx,按file33/256估算ETA~2.5d)。.29全8GPU空闲(0MiB,0%)。③无新运维指令(git log origin/main无新data相关提交)。④📦体积:TASK=31.2KB/MEMORY=26.8KB(均✅≤32KB,本轮无需归档)。下载线心跳：base ✅全满 | GPIC 5241/8001（活PID144981,+33,~40tar/h,ETA~2.7d）| UltraX ✅479parquet完成 | en_v1_4 排队 | zh分词 s4.bin=57.5GB（活PID2851334,file33/256,ETA~2.5d）。
- [20:09] **唤醒198**：①本机=`.12`。②⭐**top-K收尾全完成**：PID1985872已退出(进程不存在)，.29全8GPU空闲(0MiB)。`topk_lmeval_results_r2.json`(4014B,19:40)已生成——5 trial全量lm_eval(8 tasks,no limit)结果：t199 avg=0.3899(best)>t33=0.3897>t118=0.3877>t23=0.3846>t38=0.3835。**BO score排名与全量排名几乎完全反转**，Spearman ρ=−0.80(n=5)。③⭐**UltraX下完**：479parquet(454GB,5config),0incomplete,rc=0@19:52。进程已自然退出。④⭐**report_data_mix_eval_r2.html已生成**(18KB)。⑤GPIC(5208/8001+128test✅,PID144981活)。⑥zh分词(s4.bin=50GB,PID2851334 nice-19活)。⑦📦体积:TASK=30.5KB/MEMORY=待测。
- [19:33] **唤醒197**：①本机=`.12`。②⭐**top-K retrain 5/5全完成**：TB log t0023最后step=14593/15258(loss=4.029),所有5个目录(r2_topk_t0023_gpu2~t0033_gpu6)均已出现`checkpoints/iter_0015258/`(含__0_0.distcp+common.pt+train_state.pt,~37MB)。GPU2-6已释放(仅GPU4保留60GB=HF转换中)。脚本PID1985872(ppid=1✅)仍活,进入ckpt→HF(baize_p6_ckpt_to_hf.py)→full lm_eval(8tasks,no limit)→Spearman→topk_lmeval_results_r2.json阶段,ETA~20:00。③UltraX(458/483,95%,PID3883720 ppid=1✅,462fetched/8incomplete,rate~26.5s/file,21remaining,ETA~19:42,435GB) ④GPIC(5318/8001+128test✅,PID144981,latest tar 05188@19:29,rate慢因UltraX分流) ⑤zh分词(s4.bin=46GB,+1.6GBsince196,PID2851334 nice-19,无.idx)。⑥📦体积:TASK=30.5KB/MEMORY=23.9KB均≤32KB✅。下载线心跳：base ✅全满 | GPIC 5318/8001（活PID144981,rate慢因UltraX分流）| UltraX 458/483（活PID3883720 ppid=1✅,ETA~19:42）| en_v1_4 排队 | zh分词 s4.bin=46GB（活PID2851334,nice-19）。
- [18:50] **唤醒196**：①本机=`.12`。②⭐**BO R2已完成**：DB查询(nemo_experiments/mix_search/mix_search_eval_r2.db,86KB@18:37)→**200/200(166✅+34❌)**。BO进程PID3614158已退出,GPU0-7全空(pretrain sglang benchmark也已完成)。Top5(score DESC):t23(0.4155,web=0.941,code=0.109)>t38(0.4138)>t118(0.4130)>t199(0.4123)>t33(0.4090)。MIN/MAX/AVG=0.373/0.4155/0.3908。每trial已有lm_eval 8task detail(--limit 500)存于DB.lm_eval_detail列。③🚀**top-K收尾已启动**：创建`run/baize_mix_topk_eval_r2.py`(303行)，在.29后台启动(PID1985872,ppid=1✅)，5 retrains并行on GPU2-6(t23/g2,t38/g3,t118/g4,t199/g5,t33/g6)，MBS=16/15258steps/D=0.5B/同R2参数+save-interval=train_iters。iter110/15258,step~0.16s,loss~10.4,GPU2-6各62GB/47-62%util。流程:retrain(~40min)→ckpt→HF(baize_p6_ckpt_to_hf.py)→full lm_eval(8tasks,no limit)→Spearman→topk_lmeval_results_r2.json。ETA~19:35 retrain+~10min lm_eval。④UltraX(420/483,87%,PID3883720 ppid=1✅,rate~24s/file,63remaining,ETA~19:22) ⑤GPIC(5187/8001+128test✅,PID144981,latest tar@18:43,rate慢因UltraX分流) ⑥zh分词(s4.bin=44.4GB,+5.2GBsince195,PID2851334 nice-19,无.idx)。⑦体积:TASK=31.2KB/MEMORY=待测。下载线心跳：base ✅全满 | GPIC 5187/8001（活PID144981,rate慢因UltraX分流）| UltraX 420/483（活PID3883720 ppid=1✅,ETA~19:22）| en_v1_4 排队 | zh分词 s4.bin=44.4GB（活PID2851334,nice-19）。
- [15:23] **唤醒191**：①本机=`.12`。②✅**UltraX已kill**（运维指令2026-10-07③①）：15:27 kill PID 2850809(retry-loop)+1448940(hf download)+清理leftover sleep timer(PID 2201734/2201735)。UltraX停时=210/479parquet(215GB/487GB,44%),已下部分保留不删。**带宽全部让回GPIC**，en_v1_4继续排队不启动。③✅**BO方向bug复核**（运维指令2026-10-07③②）：用query_bo_r2.py实测DB——Top5(score DESC,正确):t23(0.4155)>t38(0.4138)>t118(0.4130)>t33(0.4090)>t134(0.4068);Bottom5(score ASC,唤醒189误用):t75(0.373)=MIN/worst。MIN/MAX/AVG=0.373/0.4155/0.3906。BO code正确(gp.add(-score)→minimize(-score)=maximize(score)✓+argmax(scores)✓+argsort[::-1]✓)。bug仅在agent报告查询方向,**不影响BO搜索本身,R1 Spearman ρ=−0.43不受影响**(R1用独立DB mix_search_eval.db with loss列)。④✅**query_bo_r2.py创建**：`run/query_bo_r2.py`(ORDER BY score DESC=正确),已scp到.29:/tmp/并验证输出。⑤**3进程全活**：GPIC(PID=144981,5137/8001,1新tar@15:28=UltraX kill后1min,恢复迹象但需更长观察窗)+BO(PID=3614158@.29,130✅/15❌=145total,rate~9.4/h,55remaining,ETA~21:20)+zh分词(PID=2851334,s4.bin=21GB,无.idx仍处理中)。⑥体积:TASK=32.5KB/MEMORY=24.2KB均≤32KB(注:TASK微超32KB但<40KB红线)。下载线心跳：base ✅全满 | GPIC 5137/8001（活PID144981,恢复中,ETA待确认）| UltraX ✅已停(210/479保留) | en_v1_4 排队 | zh分词 s4.bin=21GB（活PID2851334,nice-19）。
- [16:04] **唤醒192**：①本机=`.12`。②⭐**UltraX续传重启（用户直令2026-10-07④）**：重启1个干净实例PID=3883720(ppid=1✅)+3883723。续传验证：跳过214个已完成parquet+续传8个.incomplete。218/483进度,rate~50s/file,ETA~20:00-21:00。不再设定时终止。③✅BO方向复核Top5不变。④4进程全活。⑤新收尾顺序:UltraX下完→带宽让回GPIC→再决定en_v1_4。📦 体积：TASK=36.8KB / MEMORY=26KB。
- [16:50] **唤醒193**：①本机=`.12`。②**4进程巡检全活**（无重启需要）：
  - **UltraX**：PID3883720(bash,ppid=1✅)+3883723(hf download)。**253/479 parquet**（+35 since唤醒192@16:04,46min），257GB,8 .incomplete续传中。rate~50s/file（46min/35file≈1.3min/file）。226 remaining→**ETA~20:00-20:30**。✅续传正常,已下部分保留不删。
  - **GPIC**：PID144981(hf download)+3525273(download_it_pairs.sh)。**5175/8001 train tar**（+6 since唤醒192）+ **128/128 test tar✅**。7.7TB。rate~7.8 tar/h（⚠从45.7/h降速=UltraX带宽分流,运维指令④③预期行为）。2826 remaining→ETA~2.6天（UltraX下完后恢复45/h）。最新tar mtime=16:47（3min前,活跃）。GPIC不kill不重启（④③）。
  - **BO R2**：PID3614158@.29(8GPU,01:48起跑)。DB查询：**146✅/16❌=162total**（+8 since唤醒192,46min→rate~10.4/h）。Top5 score DESC不变：t23(0.4155)>t38(0.4138)>t118(0.4130)>t33(0.4090)>t134(0.4068)。MIN/MAX/AVG=0.373/0.4155/0.3906。38 remaining→**ETA~20:30**。GPU 8卡各62GB/55-84%util,正常。
  - **zh分词**：PID2850810(bash,ppid=1)+2851334(preprocess_data.py,12:03起跑)。**s4.bin=29GB**（+4GB since唤醒192,47min→~8.5GB/h），无.idx（仍处理中）。s0-s3已完成（各21GB+.idx+json）。处理shard s4 parts 247-256/256。nice-19。
  ③**无运维新指令**（git fetch未执行——本唤醒专注巡检,下轮fetch）。④磁盘：/nas_train 33T free(85%)。📦 体积：TASK=31.2KB✅ / MEMORY=28.3KB✅。下载线心跳：base ✅全满 | GPIC 5175/8001（活PID144981,rate~7.8/h因UltraX分流,ETA~2.6天after UltraX）| UltraX 253/479（活PID3883720 ppid=1✅,续传中,ETA~20:00）| en_v1_4 排队 | zh分词 s4.bin=29GB（活PID2851334,nice-19）。
- [18:10] **唤醒195**：①本机=`.12`。②**4进程巡检全活**（无重启需要）：
  - **UltraX**：PID3883720(bash,ppid=1✅)+3883723(hf download)。**355/483 files**（+63 since唤醒194@17:29,41min），339GB,8 .incomplete续传中。download.log显示rate~20.4s/file（加速！从60s→20s），128 remaining→**ETA~18:53**（44min）。✅续传正常,已下部分保留不删。4 config: AICC(61)+FineWeb(104)+ProX-Doc(100)+RedPajama-V2(82+downloading)。
  - **GPIC**：PID144981(hf download)+3525273(download_it_pairs.sh)。**5183/8001 train tar**（+3 since唤醒194）+ **128/128 test tar✅**。latest tar mtime=18:03（7min前,活跃）。rate~4.4 tar/h（⚠进一步降速=UltraX带宽分流加剧,运维指令④③预期行为）。2818 remaining→ETA~2.9天（UltraX下完后恢复45/h）。GPIC不kill不重启（④③）。
  - **BO R2**：PID3614158@.29(8GPU,01:48起跑)。DB查询(nemo_experiments/mix_search/mix_search_eval_r2.db)：**162✅/34❌=196total**（+8✅+8❌ since唤醒194,41min）。**4 remaining**→**ETA~18:40-18:50**。4 torchrun active(GPU0/4/5/7,55-91%util,62GB each)。Top5 score DESC不变：t23(0.4155)>t38(0.4138)>t118(0.4130)>t33(0.4090)>t134(0.4068)。MIN/MAX/AVG=0.3730/0.4155/0.3906。
  - **zh分词**：PID2850810(bash,ppid=1)+2851334(preprocess_data.py,nice=19)。**s4.bin=39.2GB**（+6.2GB since唤醒194,41min→~9.1GB/h），无.idx（仍处理中）。s0-s3已完成（各21GB+.idx+json）。处理shard s4。
  ③下载线心跳：base ✅全满 | GPIC 5183/8001（活PID144981,rate~4.4/h因UltraX分流,ETA~2.9天after UltraX）| UltraX 355/483（活PID3883720 ppid=1✅,续传中,rate~20.4s/file,ETA~18:53）| en_v1_4 排队 | zh分词 s4.bin=39.2GB（活PID2851334,nice-19）。📦 体积：TASK=31.2KB✅ / MEMORY=21.5KB✅。
- [17:29] **唤醒194**：①本机=`.12`。②**4进程巡检全活**（无重启需要）：
  - **UltraX**：PID3883720(bash,ppid=1✅,etimes=4832s)+3883723(hf download)。**292/479 parquet**（+39 since唤醒193@16:50,39min），298GB,8 .incomplete续传中。rate~60s/file（39min/39file）。187 remaining→**ETA~20:35**。✅续传正常,已下部分保留不删。
  - **GPIC**：PID144981(hf download)+3525273(download_it_pairs.sh)。**5180/8001 train tar**（+5 since唤醒193）+ **128/128 test tar✅**。latest tar mtime=17:32（1min前,活跃）。rate~7.7 tar/h（UltraX带宽分流,运维指令④③预期行为）。2821 remaining→ETA~2.6天（UltraX下完后恢复45/h）。
  - **BO R2**：PID3614158@.29(8GPU,01:48起跑)。DB查询：**154✅/26❌=180total**（+8✅+10❌ since唤醒193,39min）。Top5 score DESC不变：t23(0.4155)>t38(0.4138)>t118(0.4130)>t33(0.4090)>t134(0.4068)。MIN/MAX/AVG=0.373/0.4155/0.3906。20 remaining→**ETA~19:00-19:30**。新fails含t175(training rc=1),BO自动重试t176@GPU2。sklearn ConvergenceWarning=GP优化警告非trial失败。
  - **zh分词**：PID2850810(bash,ppid=1)+2851334(preprocess_data.py,nice=19)。**s4.bin=33GB**（+4GB since唤醒193,41min→~5.9GB/h），无.idx（仍处理中）。s0-s3已完成（各21GB+.idx+json）。处理shard s4。
  ③下载线心跳：base ✅全满 | GPIC 5180/8001（活PID144981,rate~7.7/h因UltraX分流,ETA~2.6天after UltraX）| UltraX 292/479（活PID3883720 ppid=1✅,续传中,ETA~20:35）| en_v1_4 排队 | zh分词 s4.bin=33GB（活PID2851334,nice-19）。📦 体积：TASK=30.5KB✅ / MEMORY=19.2KB✅。
> 📦 唤醒193 已归档 → `daily-memories-data/2026-10-07.md`
> 📦 唤醒191 已归档 → `daily-memories-data/2026-10-07.md`
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
| PHASE | **配比实验全部交付✅ → 后台: GPIC 5278/8001 + zh分词并行化(8进程s4-s11,45.9GB/h,ETA~9.8h)** |
| WAITING | 1（GPIC下载进行中5278/8001 ETA~2.7d; zh分词8进程进行中ETA~9.8h; ⑥块HTML报告待写） |
| ERROR_COUNT | 0（所有后台任务健康运行中） |
| 节点 | `10.239.2.29`（全8GPU空闲0MiB）+`.12`（GPIC下载PID=144981活 + zh分词8进程PID2574412~2575292活 nice-10） |
| 更新 | 2026-10-07 21:50 |

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

