# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅web分词完成(524.43B tok)+✅全量污染扫描清洁(160K docs全0)+GPIC 7327/8001(ETA~14h→~10:00Oct10)+🔄R3全量分词49/110done(61活,.bin=3.4TB,nice-10,ppid=1✅,0 fatal,49.idx[1l3+15code+33math,303.11B tok],ETA~4-8h→~23:00-03:00Oct10)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43; s_step归因(MBS16:8.6×,166ms); Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); zh分词8/8✅(112.47B); 论文更新(4+5节,main.pdf 0err); l1_en_hq分词12/12✅(152.17B); ultrax分词s34-s43✅(30.97B); en_base分词s24-s33✅(206.76B); ✅投料前污染采样扫描(10K docs,0命中); ✅全量污染扫描(30 parquet×5K=150K docs,0命中,累计160K docs全0命中); ✅④Ultra-FineWeb核实(197GB=nas_inference小副本≠tokenization源,524.43B×4B=2.1T≈2.0T .bin✅); ✅R3 49shards部分完工(l3_s39=3.75B+15code=128.62B+33math=170.74B,合计303.11B tok,61进程继续)
当前动作:     唤醒267(19:48@.12) R3全量分词监控:49/110done(61活=39l3+15code+7math,ppid=1✅,0 fatal error,nice=10),runtime=9.4h(10:24启动),.bin=3.4TB,49.idx+49.json(303.11B tok=l3=3.75B+code=128.62B+math=170.74B),math 33/40done(7rem→~1-2h),code 15/30done(15rem→~2-4h),l3 1/40done(39rem→~3-8h),2 logs有seq-length警告(非fatal,code_s0+code_s11),load=166/224,disk 40T free✅,ETA~4-8h→~23:00-03:00Oct10;GPIC=7327/8001(+34 since 19:05,~47tar/h,活PID144981[ppid=3525273],latest=07326.tar@19:48,128test✅,0.incomplete,ETA~14h→~10:00Oct10)
下一步:       ①R3全量分词监控(49/110done,61活,math近完工7rem→~1-2h,code15rem→~2-4h,l3 39rem→~3-8h,总体ETA~4-8h→~23:00-03:00Oct10)→全部完成后跑污染扫描→报"P-8数据层全就绪"; ②GPIC续下(7327/8001,ETA~14h→~10:00Oct10); ③en_v1_4排队等运维放行
阻塞:         R3全量分词进行中(49/110done,61活,ETA~4-8h→~23:00-03:00Oct10); GPIC下载进行中(7327/8001,ETA~14h→~10:00Oct10); en_v1_4排队等运维放行
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
- [19:48] **唤醒267**：①本机=`.12`,load=166/224。②R3分词巡检:**49/110done**(61活=39l3+15code+7math,ppid=1✅,**0 fatal error**,nice=10),runtime=9.4h(10:24启动),.bin=**3.4TB**,**49.idx+49.json**(l3=1[3.75B]+code=15[128.62B]+math=33[170.74B]=**303.11B tok**),2 logs有seq-length警告(非fatal,code_s0[1334159>1048576]+code_s11[1191062>1048576]),math 33/40(7rem→~1-2h),code 15/30(15rem→~2-4h),l3 1/40(39rem→~3-8h),disk 40T free✅。③GPIC=**7327**/8001(+34 since 19:05,~47tar/h,活PID144981[ppid=3525273],latest=07326.tar@19:48,128test✅,0.incomplete,ETA~14h→~10:00Oct10)。④**6目录全量盘点**(按原始目录):[1]Ultra-FineWeb(base)=3.2T/8792pq(4config:en2048+en_v1_4 488+l1_en_hq 6000+zh256)→✅524.43B/2.0T .bin(.29 mix_base/44shards); [2]Ultra-FineWeb-L3=1.8T/1764pq→🔄1/40done(3.75B); [3]UltraData-Code=1.2T/1121pq(L2=content+L3=full_content)→🔄15/30done(128.62B); [4]UltraData-Math=515G/1823pq→🔄33/40done(170.74B); [5]UltraData-SFT-2605=298G/1504jsonl→✅20.96B/79G(.29 mix_sft_tok/4shards); [6]UltraData-SFT-Agent-2609=51G/50jsonl→✅8.04B/30G(.29 mix_sft_agent_tok/4shards)。⑤**④核实再确认**:197GB=nas_inference小副本≠tokenization源;实际源=nas_train 3.2T全量下载(4config);524.43B×4B(int32)=2.1T≈2.0T .bin✅合理。📦体积:TASK=27.3KB/MEMORY=25.6KB(均≤32KB✅,无需归档)
- [16:20] **唤醒262**：①本机=`.12`,load=127/224。②R3分词巡检:**91/110进程活**(19done=1l3+0code+18math,39l3+30code+22math=91,ppid=1✅,**0 error**,nice=10),runtime=5.95h(10:24启动),.bin=**2.3TB**(l3=869G+code=682G+math=767G),**19.idx+19.json**(l3_s39=3.75B+18math=84.5B,合计~88B tok),0 Traceback,grep logs 0 error,disk 41T free✅。③GPIC=**7169**/8001(+32,~32tar/h,活PID144981,128test✅,0.incomplete,ETA~26h)。④base✅全满。⑤全量盘点6目录同w263。⑥ETA~15-20h→~07:00-12:00Oct10。⑦④Ultra-FineWeb核实(已闭合):197GB=nas_inference小副本≠源;524.43B×4B=2.1T≈2.0T✅。📦体积：TASK=27.3KB✅/MEMORY=23.9KB✅。
- [17:06] **唤醒263**：①本机=`.12`,load=125/224。②R3分词巡检:**80/110进程活**(30done=1l3+1code+28math,39l3+29code+12math=80,ppid=1✅,**0 error**,nice=10),runtime=6.7h(10:23启动),.bin=**2.56TB**(l3=981G+code=769G+math=813G),**30.idx+30.json**(l3_s39=3.75B+code_s29=6.39B+28math=132.86B,合计**143B tok**),0 Traceback,code_s29@16:23(6h,4.1M docs/6.39B tok),math_s9@17:05(latest),math剩余12proc即将完成,code/l3 .bin仍在增长(26-29G/shard),disk 41T free✅。③GPIC=**7201**/8001(+32 since 16:20,~48tar/h,活PID144981[ppid=3525273],latest=07200.tar@16:58,128test✅,**0.incomplete**,ETA~17h→~10:00Oct10)。④base✅全满。⑤**全量盘点(6原始目录)**:1.Ultra-FineWeb base=3.2TB(nas_train)/8792pq(✅44shards/524.43B/2.0T@BaiZe/data/mix_base/)|2.Ultra-FineWeb-L3=1.8T/1764pq(🔄1/40done,39proc,.bin=981G)|3.UltraData-Code=1.2T/1121pq(🔄1/30done,29proc,.bin=769G)|4.UltraData-Math=515G/1823pq(🔄28/40done,12proc,.bin=813G)|5.UltraData-SFT-2605=298G/1504jsonl(✅20.96B/79G)|6.UltraData-SFT-Agent-2609=51G/50jsonl(✅8.04B/30G)。⑥ETA修正:math~12remaining→~1-2h(即将完成);code~29remaining(1done@6h,.bin 26-29G/shard growing)→~3-5h→~20:00-22:00;l3~39remaining(1done@3.5h,.bin 22-28G/shard growing)→~4-6h→~21:00-23:00;总体ETA~4-6h→~21:00-23:00Oct9。⑦④Ultra-FineWeb核实(已闭合):197GB=/nas_inference小副本(162pq)≠tokenization源;实际源=/nas_train 3.2TB(4config);524.43B×4B=2.1T≈2.0T .bin✅。下载线心跳：base✅全满|GPIC 7201/8001(活PID144981,+32,~48tar/h,ETA~17h→~10:00Oct10)|R3分词 80/110活(.bin=2.56TB,30.idx[1l3+1code+28math,143B tok],ETA~4-6h→~21:00-23:00Oct9)|web分词 44/44✅(524.43B)|全量污染扫描✅(160K docs,0命中)。📦体积：TASK=27.3KB✅/MEMORY=25.1KB✅(无需归档)。

- [17:42] **唤醒264**：①本机=`.12`,load=118/224。②R3分词巡检:**76/110进程活**(34done=1l3+1code+32math,39l3+29code+8math=76,ppid=1✅,**0 error**,nice=10),runtime=7.3h(10:23启动),.bin=**2.8TB**(l3=1130G+code=883G+math=865G),**34.idx+34.json**(l3_s39=3.75B+code_s29=6.39B+32math=163.18B,合计**173.32B tok**),math近完工(32/40done,8remaining→~1-2h),l3+code大shard仍在跑(39l3+29code),0 Traceback,disk 40T free✅。③GPIC=**7233**/8001(+32 since 17:06,~53tar/h,活PID144981[ppid=3525273,etimes~5d],latest=07232.tar,128test✅,**0.incomplete**,ETA~14.5h→~08:00Oct10)。④base✅全满(l1_en_hq 6000/6000+zh 256/256+en 2048/2048)。⑤**全量盘点(6原始目录)**:1.Ultra-FineWeb base=3.2TB(nas_train)/8792pq(✅44shards/524.43B/2.0T@BaiZe/data/mix_base/)|2.Ultra-FineWeb-L3=1.8T/1764pq(4subdirs:en_l3/qa=616+zh_l3+multi_style+more,🔄1/40done,39proc,.bin=1130G)|3.UltraData-Code=1.2T/1121pq(🔄1/30done,29proc,.bin=883G)|4.UltraData-Math=515G/1823pq(🔄32/40done,8proc,.bin=865G)|5.UltraData-SFT-2605=298G/1504jsonl(✅20.96B/79G)|6.UltraData-SFT-Agent-2609=51G/50jsonl(✅8.04B/30G)。⑥ETA:math~8remaining→~1-2h→~19:00-20:00;code~29remaining(1done@6h,big shards)→~4-8h→~22:00-02:00;l3~39remaining(1done@3.5h,big shards)→~4-8h→~22:00-02:00;总体ETA~4-8h→~22:00-02:00Oct10。⑦④Ultra-FineWeb核实(已闭合):197GB=nas_inference小副本(162pq)≠源;524.43B×4B=2.1T≈2.0T✅。下载线心跳：base✅全满|GPIC 7233/8001(活PID144981,+32,~53tar/h,ETA~14.5h→~08:00Oct10)|R3分词 76/110活(.bin=2.8TB,34.idx[1l3+1code+32math,173.32B tok],ETA~4-8h→~22:00-02:00Oct10)|web分词 44/44✅(524.43B)|全量污染扫描✅(160K docs,0命中)。📦体积：TASK=27.3KB✅/MEMORY=25.6KB✅(无需归档)。

- [18:25] **唤醒265**：①本机=`.12`,load=176/224。②R3分词:**71/110活**(41done=1l3+7code+33math),.bin=3.1TB,41.idx(232.19B tok),math 33/40,code 7/30,l3 1/40,0 error,disk 40T✅。③GPIC=7262/8001(+29,~22.6tar/h,ETA~33h)。④base✅全满。⑤6目录盘点:base=3.2T/8792pq✅524.43B|L3=1.8T/1764pq🔄1/40|Code=1.2T/1121pq🔄7/30|Math=515G/1823pq🔄33/40|SFT=298G/1504jl✅20.96B|Agent=51G/50jl✅8.04B。⑥ETA~4-10h→~22:00-04:00Oct10。📦体积：TASK=27.3KB✅/MEMORY=27.4KB✅。

- [19:06] **唤醒266**：①本机=`.12`,load=141/224。②R3分词巡检:**49/110done(61活=39l3+15code+7math)**,ppid=1✅,**0 error**,nice=10,runtime=8.7h(10:24启动),.bin=**3.2TB**(l3=1.4T/40files+code=1012G/30files+math=892G/40files),**49.idx+49.json**(**303.11B tok**=l3=3.75B[1shard]+code=128.62B[15shards]+math=170.74B[33shards]),math 33/40done(7rem→~1-2h),code 15/30done(15rem→~2-4h),l3 1/40done(39rem→~3-8h),0 Traceback,grep logs 0 error,disk 40T free✅。③GPIC=**7293**/8001(+31 since 18:25,~46.5tar/h,活PID144981[ppid=3525273,etimes~5d],latest=07293.tar@19:05,128test✅,1.incomplete(active),ETA~15h→~10:00Oct10)。④base✅全满(l1_en_hq 6000/6000+zh 256/256+en 2048/2048)。⑤**全量盘点(6原始目录)**:1.Ultra-FineWeb base=3.2TB(nas_train)/8792pq(✅44shards/524.43B/2.0T@BaiZe/data/mix_base/);nas_inference小副本197G/162pq≠源|2.Ultra-FineWeb-L3=1.8T/1764pq(🔄1/40done,39proc,.bin=1.4T)|3.UltraData-Code=1.2T/1121pq(🔄15/30done,15proc,.bin=1012G)|4.UltraData-Math=515G/1823pq(🔄33/40done,7proc,.bin=892G)|5.UltraData-SFT-2605=298G/1504jsonl(✅20.96B/79G@mix_sft_tok)|6.UltraData-SFT-Agent-2609=51G/50jsonl(✅8.04B/30G@mix_sft_agent_tok)。⑥ETA:math~7rem→~1-2h→~20:00-21:00;code~15rem→~2-4h→~21:00-23:00;l3~39rem→~3-8h→~22:00-03:00;总体ETA~4-8h→~23:00-03:00Oct10。⑦④Ultra-FineWeb核实(已闭合):197GB=nas_inference小副本(162pq)≠源;524.43B×4B=2.1T≈2.0T✅。下载线心跳：base✅全满|GPIC 7293/8001(活PID144981,+31,~46.5tar/h,ETA~15h→~10:00Oct10)|R3分词 49/110done 61活(.bin=3.2TB,49.idx[1l3+15code+33math,303.11B tok],ETA~4-8h→~23:00-03:00Oct10)|web分词 44/44✅(524.43B)|全量污染扫描✅(160K docs,0命中)。📦体积：TASK=27.3KB✅/MEMORY=?KB(归档w259-261后检查)。

> 📦 唤醒256-258 原文已归档 → `daily-memories-data/2026-10-09.md`（含R3 110进程启动后2h巡检全链+.bin从736GB→1.3TB增长+GPIC 6987→7019+6目录盘点）

> 📦 唤醒247-251 原文已归档 → `daily-memories-data/2026-10-09.md`（含运维指令①②执行+smoke test+11进程启动+GPIC 6734→6839巡检全链）

> 📦 唤醒227-233 原文已归档 → `daily-memories-data/2026-10-08.md`（含l1_en_hq s18-s19完成+en_base起步+ETA纠正+GPIC巡检全链）



- [05:48] **唤醒246**：①本机=`.12`。②**✅全量污染扫描完成**：后台PID1942365已退出（05:34完成），扫描30/32 parquet(en_base×10+l1_en_hq×12+zh×8)×5K docs=150K docs，**0命中**✅。结合唤醒244采样(10K docs,0命中)，累计160K docs全0命中→Ultra-FineWeb全系与EDA-Eval不同源，**数据清洁，可投料**。summary→`run/data_pipeline/contam_scan_full_summary.md`。③**GPIC** 6708/8001(+31 since 05:07,~45tar/h)+128/128test✅,PID144981活(cwd=/nas_inference/.../datasets,etimes~5d),latest=06707@05:48,0.incomplete,ETA(8001-6708)/45≈29h→**~10:48Oct10**。④**.29 GPU**:GPU6=6525MiB/16%(pretrain),其余7卡全空(0MiB/0%)→.29有7卡空闲。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(无data新指令)。⑦load=104.13/224核(偏高:GPIC+vision R9@.12+pretrain@.29,可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.2KB✅/MEMORY=20.0KB✅(无需归档)。下载线心跳：base✅全满|GPIC 6708/8001(活PID144981,+31,~45tar/h,ETA~29h→~10:48Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|en_base 10/10✅(206.76B)|**全量污染扫描:✅完成(150K docs,0命中,累计160K docs全清洁)**。
- [05:07] **唤醒245**：①本机=`.12`。②**🔄全量污染扫描启动**：创建`run_contam_scan_full.sh`并后台启动(setsid,PID1942365,ppid=1✅),扫描32 parquet(en_base×10+l1_en_hq×12+zh×10)×5K docs=160K docs(16×采样扫描量),全部在/nas_train(避/nas_inference与GPIC争I/O)。当前4/32完成(20K docs,**0命中**✅),ETA~30min。③**GPIC** 6677/8001(+31 since 04:27,~46.5tar/h)+128/128test✅,PID144981活(cwd=/nas_inference/.../datasets,etimes~5d),latest=06676@05:08,1.incomplete(正常),ETA~28h→~10:00Oct10。④**.29 GPU**:GPU0,1,2,3,5=0MiB/0%(5卡空),GPU4,6,7=62.6GB/52-91%(pretrain R3 BO)→.29有5卡空闲。⑤base✅全满·UltraX✅479·en_v1_4排队。⑥git fetch(proxy)=up to date(无data新指令)。⑦load=95.32/224核(偏高:GPIC+vision R9@.12+pretrain BO@.29,可控)。⑧disk:/nas_train 80%(43T free)。⑨📦体积:TASK=28.8KB✅/MEMORY=18.6KB✅(归档唤醒234-242→daily-memories,释放~12KB)。下载线心跳：base✅全满|GPIC 6677/8001(活PID144981,+31,~46.5tar/h,ETA~28h→~10:00Oct10)|UltraX✅479|en_v1_4排队|zh 8/8✅(112.47B)|l1_en_hq 12/12✅(152.17B)|ultrax 10/10✅(30.97B)|en_base 10/10✅(206.76B)|**全量污染扫描:4/32完成,20K docs 0命中✅(后台运行中)**。
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
| PHASE | **✅web分词完成(524.43B tok) + ✅全量污染扫描完成(160K docs,0命中) + GPIC 7327/8001(ETA~14h→~10:00Oct10) + 🔄R3全量分词49/110done(61活,.bin=3.4TB,49.idx[1l3+15code+33math,303.11B tok],ETA~4-8h→~23:00-03:00Oct10)** |
| WAITING | 1（R3分词ETA~4-8h→~23:00-03:00Oct10; GPIC 7327/8001 ETA~14h→~10:00Oct10; en_v1_4排队等放行） |
| ERROR_COUNT | 1（s9崩溃重启后已完成） |
| 节点 | `10.239.2.12`（GPIC下载PID=144981活, .12 GPU全忙vision R9, .29 GPU全空, R3分词61进程nice-10） |
| 更新 | 2026-10-09 19:48 |

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

