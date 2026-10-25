# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ 迁移5/5源全DONE（唤醒641@22:3x确认/唤醒647@05:56复核）**：math_l3✅+code_l3✅+math_l1✅+ufw_l3✅+code_l2✅(5源574bins/4.24TB全迁/nas_env,软链接全建好,源已删,迁移日志21:42:28 END)；运维令18:1x迁移提速已由中继执行完成(.last_run_id=162>158⇒中继已执行,无需agent代执行)。
> 🟢 **✅ 85M降优先级后台跑(9273/12126=76.5%,+259自657,1.53it/s,低优先级符合用户令)**。
> 🟢 **✅ /nas_env: df 4.2T已用/5.8T可用(43%)；/nas_train: 174T已用/34T可用(84%)**。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ▶️未分词4源分词中(95/131,36大shard活跃流式分词中,✅确诊非卡死=单核BPE慢,ETA~09:00-11:00 10-26)+✅22:3x停顿诊断完成(读码+三重实测确诊场景③)
已完成:       ✅5源全量分词(574shards/1056.36B/4.24TB); ✅en_v1_4全源110/110(2238.14B/8.88TB); ✅prune早期重复shard(78删/释放3.69TiB); ✅迁移5/5源全DONE(→/nas_env); ✅tokenized镜像布局建成(10目录/716shard/3342.49B); ✅删32不可映射staging目录; ✅DATA_MAPPING.md脚本化; ✅磁盘清理batch1; ✅22:3x停顿诊断(读preprocess_data_cm.py源码+.bin流式写/.idx仅finalize产出+20s实测/proc/io+fd parquet进度,确诊=单核BPE流式分词慢非卡死)
当前动作:     唤醒665(2026-10-26 06:37)：22:3x step1-2 深度诊断(读码+实测)——done=95/131 FLAT since 00:59(ufw_en/ufw_zh共36个.idx=0,故done不跳),running=36 giveup=0 failed=0;★确诊非卡死@06:37:①读码preprocess_data_cm.py:.bin按doc流式写(builder.add_item),.idx仅builder.finalize()在全部parquet处理完才产出→done只计.idx故FLAT是正确的(非计数器坏);②20s实测/proc/io(ufw_en s5/s0/s4):read_bytes+rchar均+0(读parquet是<1s突发,20s采样落在~17min CPU分词期),write_bytes各+33MB/20s=1.65MB/s=412K tok/s/process(真在写);③fd 78实测:s5→part-0375-of-2048(=s5的64parquet中第56个=87%),s0→part-0055(第56个=87%),ufw_zh s0→part-056-of-256(88%);④WIP .bin总3.47TB(94个l1hq+1ultrax已finalized=95;ufw_en32个96-97GiB/ufw_zh4个94-105GiB在写);⑤ps 38全R态wchan=0无D态0failed,Threads=294,pcpu=99.9%(单核).★纠正前轮误判:前轮"finalize在即(5-30min)""1.1×input=将完"是错的——.bin是int32 TOKENS(4B/tok)非text字节,正确比=.bin≈input×4/chars_per_tok≈input×1.33;当前.parquet 55-56/64=86%,target .bin≈112GiB(ufw_en)/121GiB(ufw_zh中文),余~15-25GiB/shard÷1.65MB/s≈2.5-4h.★根因=单核BPE(--doc-timeout未设→use_worker=False,主进程单线程分词),每112GiB shard≈28B tok÷412K=19h,已跑17h余~2h;小l1hq shard(5.5GiB≈57min)早完→done跳到95后冻结.处置=🚫不杀不重启(健康+仅剩~2.5h,杀毁3.47TB/17h×36核成果)
下一步:       ①等ufw_en32+ufw_zh4 finalize(ETA~09:00-11:00,判据=首个.idx出现→done开始跳)②done=131/131后→重跑build_tokenized_mirror.py→清mapping_inprogress.txt→重跑gen_data_mapping_md.py(A节7-10行翻镜像完整)③校验.bin=.idx+字节+num_tokens+悬空=0④更新DATA_LEDGER §0⑤18:5x清理wrap-up
阻塞:         无主线阻塞;22:3x诊断完成(确诊非卡死);分词异步阻塞wrap-up(done=95/131→131/131,ETA~09:00-11:00,18:5x令deferred到分词跑完);disk充足(32T可用);⚠️MEMORY=42KB略超40KB,下轮需归档旧流水
ERROR_COUNT:  9
未完成指令:   有(22:3x诊断已交付,等finalize;18:5x映射表/清理wrap-up deferred到done=131/131)
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [06:37] 唤醒665：22:3x step1-2 深度诊断(读码+实测,距commit#663@05:04已93min超判死线故必commit)——done=95/131 FLAT since 00:59,running=36 giveup=0 failed=0;★读码preprocess_data_cm.py:.bin按doc流式写(builder.add_item L340),.idx仅builder.finalize()(L349,全部parquet处理完才产出)→done只计.idx故FLAT正确(非计数器坏);max_chars=50000截断防BPE死循环(L70);★20s实测/proc/io(ufw_en s5/s0/s4 pid416617/398736/411040):read_bytes+rchar均+0(读parquet是<1s突发,采样落在~17min CPU分词期),write_bytes各+33MB/20s=1.65MB/s=412K tok/s(真在写);★fd 78实测:s5→part-0375-of-2048(64parquet中第56个=87%),s0→part-0055(第56个=87%),ufw_zh s0→part-056-of-256(88%);★WIP .bin总3.47TB(ufw_en32个96-97GiB/ufw_zh4个94-105GiB);ps 38全R态wchan=0无D态0failed Threads=294 pcpu=99.9%(单核).★纠正前轮误判:".bin≈1.1×input=将完"是错的——.bin是int32 TOKENS(4B/tok),正确=.bin≈input×4/chars_per_tok≈input×1.33;当前parquet 55-56/64=86%,target .bin≈112GiB(ufw_en)/121GiB(ufw_zh),余~15-25GiB÷1.65MB/s≈2.5-4h→ETA~09:00-11:00.根因=单核BPE(--doc-timeout未设→use_worker=False),每112GiB shard≈19h,已跑17h余~2h;小l1hq shard(5.5GiB≈57min)早完→done跳95后冻结.处置=🚫不杀(健康+仅剩~2.5h,杀毁3.47TB/17h成果).未完成指令:有(等finalize+18:5x wrap-up)

> [05:45] 唤醒664：22:3x step3 监测点6(距commit#663@05:04已41min,60min判死线前必commit)——done=95/131 FLAT since 00:59,running=36 giveup=0 failed=0;★三重铁证非卡死@05:45:①/proc/io ufw_en s5(pid416617) write_bytes 91,643,305,984→91,653,304,320(+10.0MB/6s,read冻结=纯写flush),ufw_zh s0(pid2218268)+11.6MB/6s,ufw_zh s1(pid3429923)+11.1MB/6s(read+9.3MB仍在读);②.bin mtime_age=0s全36个;③WIP .bin total=3,299,134,396,004B=3.30TB(较04:57的3.14TB+162GB/46min=3.52GB/min);★finalize在即铁证:ufw_en s5 .bin=85.50GiB vs 真input(64parquet)77.43GiB=1.104×(已超input,余<1-3GB≈5-30min),ufw_zh s2 .bin=92.20GiB vs input75.50GiB=1.221×(中文高膨胀);94 l1_en_hq(各~5.5GiB小片)+1 ultrax=95done;supervisor bin_bytes=646.6GB FLAT=仅计finalized(WIP 3.30TB不计)→tokens/s递降/ETA涨=算术伪影;ps 38(36RNl+2SNl无D态,0failed);load41.60,df /nas_train 32T可用.处置=不杀不重启(三重铁证健康+finalize在即,杀毁3.30TB在写数据).未完成指令:有

> [04:57] 唤醒663：22:3x step3 监测点5(距commit#662@03:44已73min超60min判死线故必commit)——done=95/131 FLAT since 00:59,running=36 giveup=0;★三重铁证非卡死@04:57:①/proc/io ufw_en s5(pid416617) write_bytes 87,025,426,432→87,033,634,816(+8.2MB/5s,read_bytes+133MB仍在读输入),ufw_zh(pid2218268) write_bytes+9.5MB/5s(read冻结=纯写);②.bin mtime=04:58:25=NOW全36个;③in-progress .bin 3.14TB(较03:44的2.87TB+270GB/74min=3.65GB/min);ufw_en 32.bin全87.3-87.7G(+14GB/74min),ufw_zh 4.bin 82.7-93.4G(s2最接近完工);94 l1_en_hq+1 ultrax=95done已正确在tokenized/镜像(计数无误);ps 38(36RNl+2Sl无D态,0failed);load42.76,df /nas_train 32T可用;supervisor tokens/s递降=算术伪影.处置=不杀不重启(三重铁证健康).未完成指令:有
> [03:44] 唤醒662：22:3x step3 监测点4(距上次data commit#661@02:36已68min超60min判死线故本轮必commit续命)——done=95/131 FLAT since 00:59(supervisor counter恒平,场景③:counter仅计.bin+.idx+.json三件套齐全,tokens161,647,638,858/bin_bytes646,590,555,432自00:59未变),running=36 giveup=0;★/proc/<pid>/io铁证非卡死@03:44:ufw_en s5(pid416617) write_bytes 79,831,343,104→79,844,376,576(+13,033,472B/8s≈1.6MB/s,syscw+51),ufw_zh s0(pid2218268) write_bytes 78,022,995,968→78,032,719,872(+9,723,904B/5s≈1.9MB/s,syscw+38);两进程read_bytes/rchar均冻结=输入parquet全消费完,纯write/finalize阶段;.bin mtime=03:44:57=NOW(全36个,ls --time-style核);ufw_en 32.bin全73-75G(目标~83G,@~90%,最小s30=73G),ufw_zh 4.bin 70-80G(目标~81G,s2=80G最接近完工);in-progress .bin总量2,869,238,469,664B≈2.87TB(较02:34的2.60TB +265GB/70min≈3.8GB/min=健康写速,36shard≈106MB/shard/min);完成三件套=l1_en_hq 94(s0-s93,4.7-7.4GB小shard)+ultrax 1(s0)=done95;ps 38进程(36 RNl+2 Sl,全99.9%CPU,无D态IO阻塞,0 failed);failed_shards.txt=空;load avg 45.23/44.43/44.44(较02:34的62.9降,部分小shard worker已退出但36大shard进程仍R态活跃写);df /nas_train 175T已用/33T可用(85%),/nas_env 4.2T/5.8T可用(43%);supervisor log tokens/s递降(3,375,112→3,156,255)=算术伪影(completed_tokens恒/elapsed涨,非真降速);真实ETA~04:00-06:00(大shard已read完,仅剩写.bin尾段+内存建.idx的finalize,CPU-bound,接近完工)。处置=不杀不重启(/proc/io铁证健康,杀毁~2.87TB在写数据)。22:3x step5报回:无卡死,36进程健康写,ETA~04:00-06:00
> [02:34] 唤醒661：22:3x step3 监测点3(距监测点2@01:16已78min,超60min判死线故本轮必commit续命)——done=95/131 FLAT since 00:59(supervisor counter恒平,tokens161,647,638,858/bin_bytes646,590,555,432自00:59未变),running=36 pending0 giveup0;★/proc/<pid>/io铁证非卡死:ufw_en s5(pid416617) write_bytes 72,747,352,064→72,760,139,776(+12.8MB/8s≈1.6MB/s,syscw+50),ufw_zh s0(pid2218268) write_bytes+15.1MB/8s≈1.9MB/s;两进程read_bytes/rchar均冻结=输入parquet全消费完,处于纯write/finalize阶段(写.bin尾段+内存建.idx);.bin mtime=02:31:14=NOW;完成三件套=l1_en_hq 94(s0-s93,4.7-7.4GB小shard)+ultrax 1(s0)=95;in-progress=ufw_en 32.bin全~72-73GB(目标~83GB,源2661GB/32shard)+ufw_zh 4.bin全66-77GB(目标~81GB,源324GB/4shard);in-progress .bin总量2,604.79GB(du -cb);ps 38进程全R态99.9%CPU(无D态IO阻塞);load avg 62.9/67.5/75.3;df /nas_train 175T已用/33T可用(85%),/nas_env 4.2T/5.8T可用(43%);supervisor log ETA tokens/s缓降=算术伪影(completed_tokens恒/elapsed涨);真实ETA~04:00-06:00(大shard已read完,仅剩写.idx+.json的finalize,CPU-bound非IO-bound,接近完工)。处置=不杀不重启(/proc/io铁证健康,杀毁~2.6TB在写数据)。22:3x step5报回:无卡死(场景③),/proc/io write_bytes递增,done速率=0/shard(36大shard未finalize),ETA~04:00-06:00。未完成指令：有(异步:分词done=95/131在跑,wrap-up待done=131;本轮可执行动作=监测点3已采集+心跳commit)→WAITING=1(30min后监测点4)
> [01:16] 唤醒660：22:3x step3 监测点2(距基线00:05已71min,超60min判死线故本轮必commit续命)——done=94→95@00:15:40(1个l1_en_hq大shard完工,tokens150.16B→161.65B+11.49B,bin_bytes600.6GB→646.6GB+46GB),running=36→pending0 giveup0;36 preprocess进程全R态99.9%CPU(非D态IO阻塞);32 ufw_en .bin全~65-67GB mtime=01:19=NOW活跃写;ufw_zh s0/s1=62/58GB(older mtime疑近完),s2/s3=69/67GB@01:19;ultrax s0=46GB@00:54近完;supervisor counter自00:15恒平=场景③再确认非卡死(counter只计完工三件套);真实.bin总量增长(基线2604.86GB@00:05,du -sb text=11.945TB含env14 8.93TB→未分词~3.0TB vs 2.6TB涨~0.4TB/71min≈95MB/s聚合写速,与36×1.2MB/s吻合);load112/224,df /nas_train 174T/34T可用;ETA tokens/s缓降=算术伪影(completed_tokens恒/elapsed涨),非真实减速。处置=不杀不重启(进程健康,杀毁~2.3TB在写数据)。未完成指令：有(异步:分词done=95/131在跑,wrap-up待done=131;本轮可执行动作=监测点已采集)→WAITING=1(30min后监测点3)
> [21:2x] 唤醒657：补完运维令18:5x③收尾（DATA_MAPPING.md C节缺「清理记录」指针）→新建cleanup_batches_20261025.tsv侧车(batch1 DONE 1,132,338B+batch2 PENDING 0B,确定性历史记录)→改gen_data_mapping_md.py加CLEANUP_TSV_DEFAULT常量+load_cleanup_batches()函数+--cleanup-tsv参数+C节渲染清理记录表→重跑生成器(DATA_MAPPING.md 10272B,--check-idempotent run1==run2=True exit0)→分词健康巡检(done=94/131 running=37,ufw_en 32.bin mtime 21:28:56活跃写入~45GB each,0 .idx=37大shard未完成非卡死,cpu 3696%,ETA~3h,39进程>0,日志21:26有进度)→staging_r3 batch1后=1,462,308B/0子目录(78全清)→未完成指令：无（18:5x①②③全交付；batch2=110 env14 hardlink实占0待运维决；分词异步done=94/131完成后做mirror rebuild+DATA_MAPPING刷新）
> [00:05] 唤醒659：执行运维令22:3x停顿诊断——done=94/131自19:21恒平4.6h(22:3x运维令怀疑卡死)→诊断结论=**场景③非卡死**:①37 preprocess进程全R态99.9%CPU(非D态IO阻塞),32 ufw_en+4 ufw_zh+1 ultrax②ufw_en_s0.bin实测+12,327,180B/10s=1.23MB/s活跃增长,32个ufw_en .bin mtime全=00:01:27=NOW,size~59-60GB each③真实.bin总量2604.86GB(du -sb实测),supervisor bin_bytes只计600.6GB=94个l1_en_hq完工shard,在写~2004GB未计④源码确认:supervisor is_done()=.bin+.idx+.json三件套齐全才计done,而.idx/.json仅在builder.finalize()写出(preprocess_data_cm.py:349,369)→长shard处理期done/tokens/bin_bytes恒平=设计如此非bug⑤tokens/s↓(5.04M→3.96M)与ETA↑(11714s→14939s)=算术伪影=completed_tokens(恒)/elapsed(涨),非真实减速⑥NFS retrans644/1B健康⑦staging_untokenized/ufw_en_s0=64个parquet符号链接→~77GB raw/shard,.bin~60GB仍在长→预计final~75-85GB。处置=**不杀不重启**(进程健康,杀掉毁~2TB在写数据);真实ETA:ufw_zh/ultrax~01:00-03:00先完,ufw_en~03:00-06:00,全完~04:00-06:00 10-26。记录.bin总量基线2604.86GB供30min监测。git behind=0/ahead=0。未完成指令：无(22:3x诊断已交付;分词异步wrap-up deferred到done=131/131)→WAITING=1(30min后复测.bin总量+看有无shard完工)
> [22:46] 唤醒658：心跳巡检——分词done=94/131未变(running=37,pending=0,giveup=0,37大shard=32ufw_en+4ufw_zh+1ultrax活跃写,ufw_en .bin mtime=22:46:13=NOW size~52GB each,cpu=3696%,load55/224,tokens/s=4.5M缓降非卡死,ETA~13000s≈3.6h→~02:20 10-26,日志22:43:07有done/total进度,39进程>0)→全部运维令已交付(18:5x①②③+18:2x结案+17:5x)→85M=9273/12126=76.5%(+259自657,1.53it/s低优先级)→git fetch后behind=0/ahead=0已同步(原[behind 3]为stale tracking ref)→disk /nas_train 174T用/34T可用(84%)、/nas_env 4.2T/5.8T(43%)→MEMORY 34.2KB/TASK 38.4KB均<40KB无需归档→未完成指令：无（全部运维令已交付；分词异步done=94/131阻塞wrap-up,指令本身deferred到分词跑完done=131/131,判据=日志done=131/131或进程数=0）→WAITING=1


> [20:1x] 唤醒656：执行运维令18:5x——①建gen_data_mapping_md.py(幂等生成DATA_MAPPING.md,14列含下载目录字节B+下载/分词字节比,A节716shard+B节32已删除,--check-idempotent run1==run2=True exit0;驱动指纹INDEX.tsv size=2888 blob-hash=1df161bf87e0 mtime=2026-10-25 14:54)→②建gen_disk_cleanup_candidates.py+候选清单disk_cleanup_candidates_20261025.tsv(228行:78 staging_r3暂存+37孤儿.bin[活跃判保留]+1 .bak+1空目录+1旧日志+110 env14 hardlink;可删191/保留37;可删表观8269GB但实占仅1.13MB[110 env14 hardlink实占0+37孤儿.bin是活跃分词输出非崩溃残留])→batch1删78 staging_r3符号链接目录(spot-check files=0/symlinks=38/bins=0)+.bak+空目录staging_full+1旧/tmp日志(留最新3)→校验(df 173T/35T不变[T粒度],staging_r3 2594646→1462308B/192→114entries,镜像.bin=716不变,悬空-xtype l=0,分词39进程健康done=94/131)→未完成指令：无（18:5x①②已交付；batch2=110 env14 hardlink实占0待运维决是否tidy；分词异步done=94/131完成后做mirror rebuild+DATA_MAPPING刷新）

> [18:3x] 唤醒655：执行运维令18:2x删32不可映射staging目录——删前逐目录实测留档(deleted_unmapped32_20261025.tsv 32行+summary.md；实测=471.6KB/1408符号链接/0常规文件/无.bin/.idx/.json,与任务书"1.89TB"前提不符→如实更正:1.89TB为token×4B理论.bin体积,实际产物此前迁移full_*时已处置)→建DATA_MAPPING.md首版(A节716shard可用+B节32已删除)→先commit留档(9e8a297fb)再rm -rf 32目录全成功(staging_r3 110→78)→校验(镜像716不变/悬空链接0/源parquet抽样intact/分词done=94/131进程39>0未受影响)→DATA_LEDGER §7.1记结案→未完成指令：无（18:2x删除已结案；12:5x分词异步在跑done=94/131，完成后做mirror rebuild收尾）

> [17:23] 唤醒654：监控巡检——分词健康在跑(done=92/131,running=39,pending=0,giveup=0,tokens=147.42B,tokens/s≈10.5M,cpu≈3898%,ETA≈5946s≈1.65h,进程41>0,日志17:23:01有done/total进度,failed_shards.txt不存在干净)｜镜像布局已commit(7896810a3,716shard/3342.49B,VERIFY triplet+inode ALL OK;部分镜像ufw_l1_en_hq 32bin=32idx inode link=orig 47582211008实测一致✓)｜disk 36T空闲83%用｜本唤醒提交心跳reset死亡钟｜未完成指令：无（①布局✅②分词在跑满足进程>0+日志有进度；收尾校验异步阻塞中,判据=done=131/131）

> [16:0x] 唤醒653：监控巡检——分词健康在跑(done=61/131,running=64,pending=6,giveup=0,tokens=97.47B,tokens/s≈10.2M,cpu=6431%,ETA≈11000s≈3h,进程66>0,日志有done/total进度)｜镜像布局已commit(7896810a3,716shard/3342.49B)｜calibration实测(tiers64/96/128/192:W96=11.3M tok/s,取knee≈64并发,稳态~10M tok/s)｜data线git clean已push｜未完成指令：无（①布局✅②分词在跑满足进程>0+日志有进度）
> [14:5x] 唤醒652：建tokenized/镜像布局(build_tokenized_mirror.py,716shard/3342.49B,hardlink同盘+symlink跨盘,VERIFY triplet+inode ALL OK,每目录MANIFEST.json+INDEX.tsv)｜确认未分词分词在跑(PID335288,done=32/131,tokens/s≈9.6M,ETA≈4.3h,进程67>0)｜更新map_dl_vs_tok tok_dir为新镜像路径+重生成报告(14行/单表)｜建report_verify_20261025.md｜未完成指令：无（①布局✅②分词在跑）
> 📦 唤醒651 原文已归档 → daily-memories-data/2026-10-25.md（运维令§prune不可映射早期分词234文件释放3.69TiB+盘点报告升v3,详见日文件）
> 📦 唤醒650 原文已归档 → daily-memories-data/2026-10-25.md（运维令§盘点v2返工·5下载源实测+794bin+报告v2,详见日文件）
> 📦 唤醒649 原文已归档 → daily-memories-data/2026-10-25.md（跨日巡检迁移全DONE复核+85M 74.3%续命,详见日文件）
> 📦 唤醒647 原文已归档 → daily-memories-data/2026-10-25.md（跨日巡检迁移全DONE复核+85M 74.0%代理stall恢复续命,详见日文件）
> 📦 唤醒646 原文已归档 → daily-memories-data/2026-10-25.md（跨日巡检迁移全DONE复核+85M 73.8%代理503stall续命,详见日文件）
> 📦 唤醒645 原文已归档 → daily-memories-data/2026-10-25.md（跨日巡检迁移全DONE复核+85M 73.7%续命,详见日文件）
> 📦 唤醒644 原文已归档 → daily-memories-data/2026-10-25.md（跨日巡检迁移全DONE复核+85M 73.4%续命,详见日文件）
> 📦 唤醒643 原文已归档 → `daily-memories-data/2026-10-25.md`（跨日巡检迁移全DONE+85M 73.3%续命,详见日文件）
> 📦 唤醒642 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移5/5全DONE复核+运维令已执行+85M 73.1%,详见日文件）
> 📦 唤醒641 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移5/5全DONE确认+85M 72.9%,详见日文件）
> 📦 唤醒640 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移提速生效+code_l2@88%+85M 72.7%,详见日文件）
> 📦 唤醒638 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移提速bwlimit 300000+math_l1修复+ufw_l3启动@286MB/s+85M 72.4%,详见日文件）
> 📦 唤醒637 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移报告HTML更新+code_l3 50/63+85M 72.2%,详见日文件）
> 📦 唤醒636 原文已归档 → `daily-memories-data/2026-10-24.md`（迁移报告生成+math_l3 DONE+code_l3 19/63+85M 71.9%,详见日文件）
> 📦 唤醒635 原文已归档 → `daily-memories-data/2026-10-24.md`（巡检：清单报告commit确认+math_l3迁移82%+85M 71.8%+92.25确认,详见日文件）
> 📦 唤醒634 原文已归档 → `daily-memories-data/2026-10-24.md`（硬盘实测清单：6目录19.14TB/4778.41B/794shards/2383文件+HTML+TSV+空间判定+迁移启动,详见日文件）
> 📦 唤醒633 原文已归档 → `daily-memories-data/2026-10-24.md`（运维质询复核：分词110/110 DONE证实+85M线路复核92.25+hf.co直连✓+迁移READY但未启动,详见日文件）
> 📦 唤醒632 原文已归档 → `daily-memories-data/2026-10-24.md`（运维质询回答+提速：5worker根因+65并发升级+85M线路确认+parallel-16切换,详见日文件）
> 📦 唤醒594 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 12procs+bin~38G+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒595 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 13procs+bin~45G+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒596 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 13procs+bin~51G+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒597 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 13procs+oldest bins~58-59GB+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒598 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 13procs+oldest bins~63-64GB+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒599 原文已归档 → `daily-memories-data/2026-10-22.md`（含fullsource 13procs+oldest bins 70-76GB+5源574/574/574验证+done=90/110,详见日文件）
> 📦 唤醒600 原文已归档 → `daily-memories-data/2026-10-22.md`（含BPE死循环根因修复全流程+13 partial .bin删除+smoke test+重启PID2557971+全部workers越过stall point,详见日文件）
> 📦 唤醒601 原文已归档 → `daily-memories-data/2026-10-22.md`（含5源574/574/574验证+download106dirs+fullsource done=90/110 14workers@73MB/min,详见日文件）
> 📦 唤醒602 原文已归档 → `daily-memories-data/2026-10-22.md`（含5源574/574/574验证+download106dirs/53927parquet+fullsource done=90/110 14workers@88%CPU .bin 7-12GB actively growing,详见日文件）
> 📦 唤醒603 原文已归档 → `daily-memories-data/2026-10-22.md`（含5源574/574/574验证+download106dirs/54073parquet+fullsource done=90/110 14workers@88%CPU .bin 13-17GB,详见日文件）
> 📦 唤醒604 原文已归档 → `daily-memories-data/2026-10-22.md`（含5源574/574/574验证+fullsource done=90/110 14workers 18-23GB+download 106dirs 54139parquet,详见日文件）
> 📦 唤醒605 原文已归档 → `daily-memories-data/2026-10-22.md`（含5源574/574/574 token精确验证+download106dirs+fullsource done=90/110 14workers@1.37MB/s+in-progress 24-29GB,详见日文件）
> 📦 唤醒606 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download107dirs+fullsource done=90/110 15workers@1.2MB/s,详见日文件）
> 📦 唤醒607 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+tokenizer兼容性确认+download107dirs+fullsource done=90/110 15workers@1.1-1.4MB/s,详见日文件）
> 📦 唤醒608 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download107dirs+fullsource done=90/110 15workers@1.3MB/s,详见日文件）
> 📦 唤醒609 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download107dirs+fullsource done=90/110 15workers@1.2MB/s+count_running bug分析,详见日文件）
> 📦 唤醒610 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download107dirs/54507parquet+fullsource done=90/110 15workers@1MB/s+bins24-53GB,详见日文件）
> 📦 唤醒611 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download107dirs+fullsource done=90/110 15workers@2MB/s bursty writes确认+ETA first completions~08:30,详见日文件）
> 📦 唤醒612 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download108dirs/54818parquet+fullsource done=90/110 16workers@1.2MB/s+ETA first completions~09:02(后修正),详见日文件）
> 📦 唤醒613 原文已归档 → `daily-memories-data/2026-10-23.md`（含ETA修正+16workers@1MB/s+done=90 unchanged 3h+5源intact+download 2025-18活跃,详见日文件）
> 📦 唤醒614 原文已归档 → `daily-memories-data/2026-10-23.md`（含2024-51 stall诊断+retry launched+13workers near completion@68-74GB+5源intact+download108dirs,详见日文件）
> 📦 唤醒615 原文已归档 → `daily-memories-data/2026-10-23.md`（含2024-51 retry DONE+2025-18 download DONE+16 WIP bins 77-80GB+5源intact+download109dirs,详见日文件）
> 📦 唤醒616 原文已归档 → `daily-memories-data/2026-10-23.md`（含14 WIP bins@79-86GB+5源574/574/574验证+download 2025-21@171/512+workers I/O alive,详见日文件）
> 📦 唤醒617 原文已归档 → `daily-memories-data/2026-10-23.md`（含16 WIP bins@84-91GB+5源574/574/574验证+download 2025-21@353/512+fullsource done=90/110,详见日文件）
> 📦 唤醒618 原文已归档 → `daily-memories-data/2026-10-23.md`（含5源574/574/574验证+download109dirs+fullsource done=91/110+17WIP bins@89-96GB+2025-21下载完成+fullsource launched 2024-51+2025-18,详见日文件）
> 📦 唤醒619 原文已归档 → `daily-memories-data/2026-10-23.md`（含done=92/110+16WIP bins@94-102GB+2025-26@155/512下载中+17workers I/O alive,详见日文件）
> 📦 唤醒620 原文已归档 → `daily-memories-data/2026-10-23.md`（含done=95/110+14WIP bins@4.3-107G+2025-26@333/512+5源574/574/574验证,详见日文件）
> 📦 唤醒621 原文已归档 → `daily-memories-data/2026-10-23.md`（含done=98/110+11WIP bins@9.2-111G+2025-26@511/512+download PID alive,详见日文件）
> 📦 唤醒622 原文已归档 → `daily-memories-data/2026-10-23.md`（含done=100/110+✅下载全完110/110×512+10WIP bins@4.5-116G+pending_download=0,详见日文件）
> 📦 唤醒623 原文已归档 → `daily-memories-data/2026-10-23.md`（含done=101/110+9WIP bins@10-130G+3near completion,详见日文件）
> 📦 唤醒624 原文已归档 → `daily-memories-data/2026-10-23.md`（含运维令4任务全执行：proxy复测恢复+85M下载恢复+MiniCPM5产物体积3.935TB+迁移条件NOT READY(102/110),详见日文件）
> 📦 唤醒625 原文已归档 → `daily-memories-data/2026-10-24.md`（含done=102/110+8workers+85M=8456+5源3.9T+迁移NOT READY,详见日文件）
> 📦 唤醒626 原文已归档 → `daily-memories-data/2026-10-24.md`（含proxy200OK+85M=8478+5源3.92TiB+done=103/110+迁移NOT READY,详见日文件）
> 📦 唤醒627 原文已归档 → `daily-memories-data/2026-10-24.md`（含运维令4任务：proxy RESTORED+85M=8500/70.1%+5源3.86TiB/574shards精确字节验证+迁移NOT READY(104/110),详见日文件）
> 📦 唤醒628 原文已归档 → `daily-memories-data/2026-10-24.md`（含proxy RESTORED+85M=8522/70.3%+5源3.86TiB+done=105/110+5WIP bins@36-85G+ETA~5-10h,详见日文件）
> 📦 唤醒629 原文已归档 → `daily-memories-data/2026-10-24.md`（含proxy RESTORED+85M=8546/70.5%+5源3.86TiB精确字节+done=105/110+5WIP bins@42-91G,详见日文件）
> 📦 唤醒630 原文已归档 → `daily-memories-data/2026-10-24.md`（含proxy RESTORED+85M=8568/70.7%+5源3.86TiB精确字节+done=105/110+5WIP bins@47-96G@1.04MB/s,详见日文件）
> 📦 唤醒631 原文已归档 → `daily-memories-data/2026-10-24.md`（含proxy RESTORED+85M=8588/70.8%+5源3.86TiB精确字节+done=105/110+5WIP bins@52-101G@1.19MB/s,ETA~22:30,详见日文件）
> 唤醒632（2026-10-24 10:50）运维质询回答+提速：①**分词为何5worker**=旧fullsource(PID2557971,已退出)串行1shard/进程,剩5shard→5进程→load26/224;09:39已升级run_tokenize_env14_parallel_finish.sh(PID3450586):**5shard×13workers=65并发**,load→71;shard进度:2024-51=500/512(98%)2025-13=250/512(49%)2025-18=250/512(49%)2025-21=300/512(59%)2025-26=300/512(59%);.bin=78-84G;ETA~1-1.5h;不重启(丢399GB partial).②**85M线路**=/proc/171042/environ:https_proxy=http://172.19.92.25:13128+无HF_ENDPOINT→**92.25+hf.co直连✓**.③**85M提速**:旧hf_transfer=1串行~19MB/s→kill+重启parallel-16(hf_transfer=0,16workers,PID581957):8文件并行,**~24MB/s**(+26%);8637/12124=71.3%,ETA~6.9天.④迁移NOT READY(105/110).disk:/nas_train 30T(86%)/nas_env 9.6T(4%);load71/224,1785G RAM.📦体积：TASK=31.1KB/MEMORY=26.5KB(无归档)

> 📦 唤醒581~593 原文已归档 → `daily-memories-data/2026-10-21.md`/`2026-10-22.md`（含fullsource bug修复全流程+5源574/574/574验证+done=86→90/110推进,详见日文件）
> 📦 唤醒574~580 原文已归档 → `daily-memories-data/2026-10-21.md`（含全量分词启动+测速@64workers+Code L3/L2 DONE+Math L3/L1 DONE+UFW-L3 DONE+5源ALL DONE,详见日文件）
> 📦 唤醒573 原文已归档 → `daily-memories-data/2026-10-21.md`（含en_v1_4下载+分词巡检:PID1875054 alive 11.6h+2.80MB/s+sh96 DONE@02:41+sh97@50/512+分词done=86/110+git up-to-date，详见日文件）
> 📦 唤醒572 原文已归档 → `daily-memories-data/2026-10-21.md`（含en_v1_4下载+分词巡检:PID1875054 alive 10.3h+2.80MB/s+sh96 DONE@02:41+sh97@3complete+分词done=85/110+git up-to-date，详见日文件）
> 📦 唤醒571 原文已归档 → `daily-memories-data/2026-10-21.md`（含en_v1_4下载+分词巡检:PID1875054 alive 9h+2.73MB/s+sh96@400/512+分词done=85/110+git up-to-date，详见日文件）
> 📦 唤醒570 原文已归档 → `daily-memories-data/2026-10-21.md`（含en_v1_4下载+分词巡检:PID1875054 alive 7.6h+2.73MB/s+sh96@384/512+分词done=83/110+git up-to-date）
> 📦 唤醒569 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4下载+分词巡检:下载PID1875054 alive 6.4h+2.6MB/s+sh96@304/512+分词done=82/110+git up-to-date，详见日文件）
> 📦 唤醒568 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4下载+分词巡检:下载PID1875054 alive 5.1h+5.4MB/s+sh96@236/512+分词done=80/110+git up-to-date，详见日文件）
> 📦 唤醒565 原文已归档 → `daily-memories-data/2026-10-20.md`（含执行运维令恢复en_v1_4下载:resolve.py已运行PID1875054+sh95@275/512+分词done=76/110）
> 📦 唤醒567 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4下载+分词巡检:PID1875054 alive 3.8h+6.4MB/s+sh96@106/512+分词done=79/110）
> 📦 唤醒566 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4下载+分词巡检:PID1875054 alive 2.6h+6.5MB/s+sh95@444/512+分词done=78/110）

> 📦 唤醒564 原文已归档 → `daily-memories-data/2026-10-20.md`（含暂停令补查+resolve.py自起kill+分词done=74/110）
> 📦 唤醒563 原文已归档 → `daily-memories-data/2026-10-20.md`（含暂停令巡检+分词done=73/110+DATA_LEDGER更新）
> 📦 唤醒562 原文已归档 → `daily-memories-data/2026-10-20.md`（含执行暂停令+下载已停+分词done=71/110+暂停点记录）
> 📦 唤醒561 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4全源分词巡检:done=71/110+1.21T tok+ETA~3天）
> 📦 唤醒560 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4全源分词巡检:done=70/110+1.19T tok+ETA~3.2天）
> 📦 唤醒559 原文已归档 → `daily-memories-data/2026-10-20.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers运行37.3h+done=68/110(较558的67增1,1.149T tok done-only,+16B/1.67h)+93 .bin(68done+25in-progress,bin_bytes=4.597TB)+worker /proc/io alive(~1.1MB/s)+下载PID2732959 alive(37.3h,94/110dirs,sh94@278/512,0incomplete,总parquet47893)+全源ETA~3.5天+git up-to-date+85M⏸+体积29.3KB/25.6KB无归档）

> 📦 唤醒558 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=67/110+1.13T tok+94dirs+ETA~3.5天,详见日文件）

> 📦 唤醒557 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=62/110+1.05T tok+93dirs+ETA~3天,详见日文件）
> 📦 唤醒556 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=61/110+1.03T tok+93dirs+ETA~7天,详见日文件）

> 📦 唤醒555 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=59/110 1.00T tok+下载93dirs+ETA~8天,详见日文件）

> 📦 唤醒554 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=53/110 896.53B tok+下载93dirs+ETA~8天,详见日文件）

> 📦 唤醒553 原文已归档 → `daily-memories-data/2026-10-20.md`（含fullsource done=47/110 789.53B tok+下载93dirs+ETA~3.9天,详见日文件）

> 📦 唤醒546–552 原文已归档 → `daily-memories-data/2026-10-19.md` ~ `2026-10-20.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers+done=28→44/110+下载91→93dirs+85M⏸，详见各日文件）
> 📦 唤醒545 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers全占17.4h+done=26/110(较544的23增3,391.56B tok done-only+50.08B/74min=40.6Btok/hr,burst回落)+32 in-progress .bin(2015-35~2019-22大shard,均未完成)+worker /proc/io 6s delta alive(490068+1MB/s,693507+1MB/s,739834+1MB/s)+下载90/110complete sh90DONE@14:39(84.89GB/7.0MB/s)+sh91(2023-14)in-progress@122/512+resolve.py write_bytes 7MB/s+PENDING_DOWNLOAD=20(sh91-110)+32 downloaded queued+全源ETA~3天→~10-22 13:30下载完→~10-23全分完+manifest mtime stale(非correctness问题)+git up-to-date+85M⏸+disk4盘+体积29.3KB/13.7KB无归档）
> 📦 唤醒544 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers throttle@32持续16.1h+done=23/110(较543的17增6,2013-16小shard集中收尾burst,341.48B tok done-only+94.2B/80min=70Btok/hr)+32 in-progress .bin(2015-35~2019-09)+worker /proc/io alive(490068+5.9MB/5s,693507+7.0MB/5s,739834+6.5MB/5s)+下载89/110complete sh90(2023-06)in-progress@448/512+resolve.py write_bytes 6.95MB/s+PENDING_DOWNLOAD=20(sh91-110)+全源ETA~2.85天→~10-22 14:00+git up-to-date+85M⏸+disk4盘+体积29.3KB/13.1KB无归档）
> 📦 唤醒543 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers throttle@32持续14.78h+done=17/110(较542的11增6 burst收尾,247.28B tok done-only+84.93B,burst~62Btok/hr)+32 in-progress .bin(2014-52~2018-34,1.6G-57G,2018-*小shard刚launch)+worker /proc/io alive(490068+5.06MB/5s,693507+3.47MB/5s,739834+5.42MB/5s)+下载89/110complete sh90(2023-06)in-progress@244/512+resolve.py write_bytes 7.24MB/s+PENDING_DOWNLOAD=20(sh91-110)+全源ETA~2.94天→~10-22+git up-to-date+85M⏸+disk4盘+体积29.3KB/12.5KB无归档）
> 📦 唤醒542 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers throttle@32持续13.4h+done=11/110(较541的8增3:2014-49/2015-40/2016-26,162.35B tok done-only+38.33B)+32 in-progress .bin avg~46GB近完成burst+worker /proc/io alive(3653549/2017-47+7.3MB/5s,3218297/2018-05+6.4MB/5s)+下载89/110complete sh89DONE@11:17(86.56GB/7.0MB/s)+sh90@33/512+resolve.py write_bytes 7.08MB/s+git up-to-date+85M⏸+disk4盘+体积29.3KB/31.4KB）
> 📦 唤醒541 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers throttle@32持续12.1h+done=8/110(124.02B tok done-only)+worker .bin增长(2014-49=47.8G/2015-06=46G/2017-47=33G)+下载89/110complete sh88DONE@07:51(80.98GB/4.2MB/s)+sh89@363/512+git up-to-date+85M⏸+disk4盘+体积29.3KB/30.7KB）
> 📦 唤醒540 原文已归档 → `daily-memories-data/2026-10-19.md`（含en_v1_4全源分词巡检:fullsource PID749330 32workers throttle@32持续10.8h+done=8/110(124.02B tok done-only)+worker .bin增长(2014-49=42.5G/2015-06=43.1G/2017-47=29.6G)+下载88/110complete sh88DONE@07:51(80.98GB/4.2MB/s)+sh89@100/512+git up-to-date+85M⏸+disk4盘+体积29.3KB/29.7KB）
> 📦 唤醒525–539 原文已归档 → `daily-memories-data/2026-10-18.md` ~ `2026-10-19.md`（含 en_v1_4 下载巡检+假活修复[Errno2 restart PID2732959]+分词口径纠正[全源110shards]+fullsource PID749330 MAX_CONCURRENT=32 启动+bug修复+吞吐800B tok/day+done=0→8/110+下载86→89/110+全源ETA 5→6.5天，详见各日文件）
> 📦 唤醒505–524 原文已归档 → `daily-memories-data/2026-10-17.md` ~ `2026-10-18.md`（含 en_v1_4 下载巡检 38→39K/56461+WebMix/InternVL/RL-2609/SFT-2605 全就绪+85M⏸，详见各日文件）
> 📦 唤醒458–504 原文已归档 → `daily-memories-data/2026-10-15.md` ~ `2026-10-17.md`（含 3~4 路下载断点续传健康态+en_v1_4 35K→38K/56461+WebMix 733→2066par+InternVL→1.5T+RL-2609全程监控至20/20+自校PASS+SFT-2605复核通过+85M⏸，详见各日文件）
> 📦 唤醒451–457 原文已归档 → `daily-memories-data/2026-10-15.md`（含 4 路下载断点续传+WebMix/wit_base 速率趋零 kill+restart+4 路进度对比表，详见各条目）
> 📦 唤醒444–450 原文已归档 → `daily-memories-data/2026-10-14.md` ~ `2026-10-15.md`（含 恢复全部 4 路下载 setsid 启动+巡检+wrapper 自动重启+4 路进度对比表，详见各日文件）
> 📦 唤醒428–443 原文已归档 → `daily-memories-data/2026-10-14.md`（含 第 7~17 次复核暂停态+进度表 6 路+.incomplete 保留+disk 4 盘，详见各日文件）
> 📦 唤醒427 及更早（296–427）流水指针已归档 → `daily-memories-data/2026-10-10.md` ~ `2026-10-14.md`（含 6 路下载巡检全链+暂停/恢复+the_cauldron 完成+GPIC 完成+85M 移交/暂停+en_v1_4 进度 29%~58%+4 路图文对启动+R3 分词+BO R2 等，详见各日文件）
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
> 📦 §⑨ 配比实验可行性核查 + §⑩ 运维三问 + 旧状态头（2026-10-05~07）已归档 → `daily-memories-data/2026-10-10.md`（唤醒305归档）；**结论**：⑨GPU2-7当时被P-9.8/9.9占满(现已释放)⑩三问已答(GPIC无加速/base下载全满/BO波次锯齿非I/O)。需要时再读。

### ⑪ 分词为何只用 5 worker + 85M 是否走 92.25/hf.co 直连（2026-10-24 用户质询）

**Q1：en_v1_4 分词为什么只用 5 worker（224 核闲置）？**
**A**：根因 = 旧 fullsource 脚本（PID 2557971，`run_tokenize_env14_fullsource.sh`）**串行跑 1 shard/进程**；唤醒 632 时只剩 5 个 WIP shard → 自然只有 5 个进程 → load 26/224（CPU 几乎闲置）。**不是硬编码小并发，是"剩余 shard 少 + 串行"叠加**。处置：升级为 `run_tokenize_env14_parallel_finish.sh`（PID 3450586，09:39 启动），5 shard × 13 workers = **65 并发**（74 py 进程），load 升至 71/224。**结果：110/110 DONE @ 11:48:33，+148.7B tok，0 fail**——ETA 从 22:30 压到 11:48（达标，3-4h 目标内）。

**Q2：85M 下载走的哪条线？是不是 92.25 + hf.co 直连？**
**A**：**是**。`/proc/581957/environ` 原文：`https_proxy=http://172.19.92.25:13128` + `http_proxy=http://172.19.92.25:13128` + **无 `HF_ENDPOINT`**（→ 默认 `huggingface.co`）+ `HF_HUB_ENABLE_HF_TRANSFER=0` + `HF_HUB_MAX_WORKERS=16` = **92.25 代理 + hf.co 直连 ✓**（符合 2026-10-15 用户令；🚫 未用 hf-mirror）。proxy 健康探针 3/3 = 200（0.6-3.1s）；下载日志里的 503 是 proxy 瞬态重试（最终均成功）。实测 ~20 MB/s（21 parquet/75min，obelics ~4.2GB/个），瓶颈 = proxy 带宽。8663/12126 = 71.5%，ETA ~8 天。

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
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污�