# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        🔄en_v1_4下载进行中(PID2535486,9660/56461 parquet,19/110 snapshots(s19 CC-MAIN-2015-40 400/513 downloading),764G,parallel 24+hf_transfer,实测~7.6MB/s(39min avg,速率恢复⬆️),ETA~9天)+🔄85M部分完成(PID1192761用户管理~5.3h,7912/12361 parquet=64.0%,~27T du/46.66T,sa1b+zero250m未开始,obelics4048/5902=68.6%,实测~13.6MB/s(40min avg),ETA~17天,用户自管)+✅GPIC全完成(8129tar已核实)+✅R3全量分词110/110+✅污染扫描220K docs 0命中→P-8数据层全就绪
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128 provider+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200+Spearman ρ=−0.43; s_step归因(MBS16:8.6×,166ms); Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); zh分词8/8✅(112.47B); 论文更新(4+5节,main.pdf 0err); l1_en_hq分词12/12✅(152.17B); ultrax分词s34-s43✅(30.97B); en_base分词s24-s33✅(206.76B); ✅投料前污染采样扫描(10K docs,0命中); ✅全量污染扫描(30 parquet×5K=150K docs,0命中); ✅④Ultra-FineWeb核实; ✅R3全量分词110/110DONE(1483.91B tok/5.94TB); ✅R3投料前污染扫描30/30DONE(60K docs,0命中,累计220K docs全0命中)→P-8数据层全就绪; ✅GPIC下载全部完成(8129tar已核实@/nas_inference); 🔄en_v1_4下载进行中(PID2535486,9660/56461,764G,19/110snapshots,~7.6MB/s avg⬆️恢复,ETA~9天); 🔄85M部分完成(PID1192761用户管理~5.3h,7912/12361=64.0%,~27T/46.66T,sa1b+zero250m未开始,obelics4048/5902=68.6%,~13.6MB/s avg,ETA~17天,用户自管); ✅HfApi核实85M 8子集精确总量(12,361files/46.66TB,5子集93-98%+obelics68.6%+sa1b/zero250m未开始)
当前动作:     唤醒331(15:37@.12) 并发下载巡检(85M+en_v1_4各自速度/ETA 第二十九次采样):85M PID1192761活(ppid=2000875 bash download.sh,~5.3h,用户管理),7912 parquet/27T du/1 .incomplete(obelics/EN/part54 0B mtime15:38 stale),per-subdir:coyo1940✅|datacomp575✅|imagenet82✅|laioncn562✅|mint705✅|obelics4048/5902=68.6%(+9 vs唤醒330)|sa1b0❌未开始|zero250m0❌未开始,真实进度64.0%files(7912/12361)/~57.8%bytes(27T/46.66T),write_bytes 254.806GB(T1 15:38:45)→254.806GB(T2 15:39:56)=Δ100KB/71s→1.4KB/s(瞬时bursty间隙),40min avg 222.078GB(唤醒330 15:00)→254.806GB=Δ32.728GB/2370s→13.6MB/s,parquet+9/37min=0.24fpm,ETA~17天(~19.66TB@13.6MB/s字节口径);en_v1_4 PID2535486活(ppid=1,~22.2h),9660 parquet/764G/0 .incomplete,19/110 snapshots(s19 CC-MAIN-2015-40 400/513@15:37 downloading),write_bytes 719.277GB(T1 15:38:43)→719.704GB(T2 15:39:56)=Δ407.7MB/73s→5.59MB/s(瞬时),39min avg 701.906GB(唤醒330 15:00)→719.704GB=Δ17.798GB/2370s→7.6MB/s⬆️(vs上轮1.55MB/s,速率恢复389%!),parquet+251/37min=6.8fpm,ETA~9天(~6.0TB@7.6MB/s字节口径=9.1天/46,801files@6.8fpm=4.6天);log有proxy MaxRetryError但retrying&progressing;争用合计21.2MB/s(40min avg)/5.59MB/s(瞬时73s,85M bursty间隙);GPIC✅8129tar(8001train+128test@/nas_inference);disk 36T/84%;load 203.15/194.27/193.84;📦TASK=29.0KB✅/MEMORY=26.1KB✅
下一步:       ①监控en_v1_4+85M下载进度(每唤醒检查PID/parquet/.incomplete/磁盘); ②85M剩余~19.66TB含sa1b5.09T+zero250m4.76T+obelics~6.25T+5子集余量(用户自管,data线仅巡检); ③en_v1_4下满56461后必经check_contamination.py再报"en_v1_4下载完成"; ④en_v1_4速率恢复至7.6MB/s(从1.55MB/s回升),proxy偶有MaxRetryError但retry成功,继续观察; ⑤P-8投料等运维指示
阻塞:         en_v1_4下载进行中(ETA~9天@7.6MB/s⬆️速率恢复,46,801 remaining,~6.0TB); 85M下载进行中(ETA~17天@13.6MB/s,~19.66TB remaining,用户自管); P-8投料等运维指示
ERROR_COUNT:  1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
- [15:37] **唤醒331**：①本机=`.12`,load~203/194(高,疑vision训练)。②并发下载巡检第二十九次采样(85M+en_v1_4)。③85M:PID1192761活(~5.3h,用户管理),7912/12361 parquet=64.0%,27T du/46.66T,obelics4048/5902=68.6%(+9),sa1b+zero250m未开始,1 .incomplete(obelics/EN/part54 0B mtime15:38 stale),40min avg 222.078→254.806GB=Δ32.728GB/2370s→13.6MB/s,瞬时1.4KB/s(bursty间隙),ETA~17天。④en_v1_4:PID2535486活(~22.2h),9660/56461 parquet=17.1%,764G,19/110 snapshots(s19 CC-MAIN-2015-40 400/513),0 .incomplete,39min avg 701.906→719.704GB=Δ17.798GB/2370s→7.6MB/s⬆️(vs上轮1.55MB/s恢复389%!),瞬时5.59MB/s,parquet+251/37min=6.8fpm,log有proxy MaxRetryError但retrying&progressing,ETA~9天。⑤GPIC✅8129tar(8001train+128test@/nas_inference/.../gpic/)。⑥disk 36T/84%;load 203/194。⑦📦体积:TASK=29.0KB✅/MEMORY=26.1KB✅(无需归档)。下载线心跳：base✅全满|GPIC✅8129tar|en_v1_4🔄9660/56461(19/110,PID2535486,~7.6MB/s avg⬆️恢复,ETA~9天)|85M🔄7912/12361(64.0%,sa1b+zero250m未开始,PID1192761用户管理,~13.6MB/s avg,ETA~17天,用户自管)|P-8数据层✅全就绪。
> 📦 唤醒330 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十八次采样：85M obelics4039/5902+en_v1_4 s19 200/513+争用20.05MB/s avg+en_v1_4速率降至1.55MB/s⚠️）

> 📦 唤醒329 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十七次采样：85M obelics4027/5902+en_v1_4 s19 100/513+争用20.3MB/s avg+en_v1_4速率骤降3.7MB/s）
> 📦 唤醒318 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十六次采样：85M obelics3950/5902+en_v1_4 s13 372/513+争用20.1MB/s avg+proxy 503影响）
> 📦 唤醒322 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十次采样：85M obelics3976/5902+en_v1_4 s15 400/513+争用~21MB/s avg）
> 📦 唤醒323 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十一次采样：85M PID2783115 obelics3984/5902+en_v1_4 s16 100/513+争用~20.8MB/s）
> 📦 唤醒324 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十二次采样：85M PID1192761用户重启+obelics3991/5902+en_v1_4 s16 450/513+争用21.4MB/s）
> 📦 唤醒325 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十三次采样：85M obelics3997/5902+en_v1_4 s17 243/513+争用21.1MB/s avg）
> 📦 唤醒327 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十五次采样：85M obelics4010/5902+en_v1_4 s18 282/513+争用22.3MB/s avg+load 188）
> 📦 唤醒328 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十六次采样：85M obelics4018/5902+en_v1_4 s19 started+争用20.8MB/s avg）
> [14:17] **唤醒329**(14:17@.12) 并发下载巡检(85M+en_v1_4各自速度/ETA 第二十七次采样):85M PID1192761活(ppid=2000875,~4.0h,用户管理),7891 parquet/27T du/1 .incomplete(obelics/EN/part54活跃),per-subdir:coyo1940/1971(98.4%)|datacomp575/590(97.5%)|imagenet82/88(93.2%)|laioncn562/577(97.4%)|mint705/727(97.0%)|obelics4027/5902=68.2%(+9)|sa1b0❌|zero250m0❌,63.8%files(7891/12361)/~57.8%bytes(27T/46.66T),write_bytes 174.853→175.329GB(94s→5.1MB/s瞬时,35min avg 138.414→175.329GB/2134s→17.3MB/s),ETA~12-17天;en_v1_4 PID2535486活(ppid=1,~20.9h),9355 parquet/744G/0 .incomplete,19/110(s19 CC-MAIN-2015-40 100/513,latest parquet part-0143活跃),write_bytes 697.909→697.980GB(94s→0.76MB/s瞬时,35min avg 689.802→697.980GB/2134s→3.7MB/s),parquet+115/35min=3.3fpm,ETA~8-19天(速率骤降需观察);争用20.3MB/s(35min avg)/5.9MB/s(瞬时);GPIC✅8128tar(8000train+128test,hf PID1838177已退出);disk 36T/83%;load 103.34/98.26/96.21;📦TASK=29.0KB✅/MEMORY=23.7KB✅。下载线心跳：base✅全满|GPIC✅8128tar|en_v1_4🔄9355/56461(19/110,PID2535486,~3.7MB/s avg,ETA~8-19天,速率下降)|85M🔄7891/12361(63.8%,sa1b+zero250m未开始,PID1192761用户管理,~17.3MB/s avg,ETA~12-17天,用户自管)|P-8数据层✅全就绪。
> 📦 唤醒326 原文已归档 → `daily-memories-data/2026-10-11.md`（含第二十四次采样：85M obelics4004/5902+en_v1_4 s17 500/513+争用20.1MB/s avg）
> 📦 唤醒321 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十九次采样：85M obelics3970/5902+en_v1_4 s15 100/513+争用25.1MB/s）
> 📦 唤醒320 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十八次采样：85M obelics3965/5902+en_v1_4 s14 350/513+争用16.7MB/s）
> 📦 唤醒319 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十七次采样：85M新PID2783115重启+obelics3958/5902+en_v1_4 s14 100/513+争用23.5MB/s）
> 📦 唤醒317 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十五次采样：85M obelics3943/5902+en_v1_4 s12 DONE+s13 started+争用22.4MB/s）


> 📦 唤醒316 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十四次采样：85M obelics3935/5902+en_v1_4 s12 DONE+s13 at 300/513+争用23.6MB/s）
> 📦 唤醒315 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十三次采样：85M obelics3928/5902+en_v1_4 s11 DONE+s12 at 317+争用19.4MB/s）

> 📦 唤醒314 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十二次采样：85M obelics3920/5902+en_v1_4 s11 at 200/513+GPIC PID3041212已死）

> 📦 唤醒313 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十一次采样：85M obelics3913/5902+en_v1_4 s10 at 473/513+GPIC 8160tar核实）

> 📦 唤醒312 原文已归档 → `daily-memories-data/2026-10-11.md`（含第十次采样：85M obelics3907/5902+en_v1_4 s10 at 150/513+HfApi 8子集精确总量表）

> 📦 唤醒311 原文已归档 → `daily-memories-data/2026-10-11.md`（含第九次采样+HfApi核实85M精确总量=12,361files/46.663TB）

> 📦 唤醒308-309 原文已归档 → `daily-memories-data/2026-10-11.md`（含第六~七次采样：85M obelics3879-3885+en_v1_4 s7-s8）
> 📦 唤醒310 原文已归档 → `daily-memories-data/2026-10-11.md`（含第八次采样：85M obelics3892/5803=67.1%+en_v1_4 s8 DONE/s9 at 100/513+push 503失败已补推）

> 📦 唤醒307 原文已归档 → `daily-memories-data/2026-10-10.md`（含第五次采样：85M obelics3872/5803=66.7%+en_v1_4 7/110+GPIC 8000tar+用户自管GPIC hf下载）
> 📦 唤醒306 原文已归档 → `daily-memories-data/2026-10-10.md`（含并发下载巡检85M/en_v1_4各自速度ETA第四次采样+85M 8子集更正表+obelics3865/5803=66.6%）
> 📦 唤醒305 原文已归档 → `daily-memories-data/2026-10-10.md`（含并发下载巡检85M/en_v1_4各自速度ETA第三次采样+85M总量更正表(8子集)+obelics3857/5803=66%）
> 📦 唤醒303 原文已归档 → `daily-memories-data/2026-10-10.md`（含运维令更正85M总量46.7TB+并发下载巡检85M/en_v1_4各自速度ETA+HfApi逐子集核实表）
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

> 📦 唤醒303 原文已归档 → `daily-memories-data/2026-10-10.md`（含HfApi核实85M 8子集精确总量12124files/46.66TB+obelics3844/5803+en_v1_4 5/110+争用26.4MB/s）

> ⚠️ **唤醒302"关键更正:85M总量=7701/27T"❌作废**（唤醒303已用HfApi核实：真实总量=12,124files/46.66TB，302漏了sa1b+zero250m两子集+混淆已下/总量+obelics非100%）。见上方唤醒303。

> 📦 唤醒302 原文已归档 → `daily-memories-data/2026-10-10.md`（含并发下载巡检85M/en_v1_4+85M PID2171453重启+en_v1_4 5/110+争用~20MB/s）

> 📦 唤醒301 原文已归档 → `daily-memories-data/2026-10-10.md`（含并发下载巡检3次采样85M bursty+en_v1_4 4/110+争用~21-28MB/s+TASK归档3块）

> 📦 唤醒300 原文已归档 → `daily-memories-data/2026-10-10.md`（含并发下载巡检85M/en_v1_4+85M 7684/12124=63%+en_v1_4 4/110+争用~21MB/s）

> 📦 唤醒299 原文已归档 → `daily-memories-data/2026-10-10.md`（含en_v1_4巡检snapshot 3/110+rate~6.5fpm+GPIC全完成+R3 110/110）

> 📦 唤醒298 原文已归档 → `daily-memories-data/2026-10-10.md`（含en_v1_4重启PID2535486+24workers+snapshot 3/110+6目录盘点全✅）

> 📦 唤醒297 原文已归档 → `daily-memories-data/2026-10-10.md`（含en_v1_4巡检snapshot 2/110+清201 stale .lock+GPIC全完成+6目录盘点）

- [16:01] **唤醒296**：①本机=`.12`,load~40/224。②en_v1_4下载优化:唤醒295的sequential Python脚本(~2 files/min)太慢→改写为parallel版本(ThreadPoolExecutor 8 workers+HF_HUB_ENABLE_HF_TRANSFER=1),4x加速到~7-8 files/min。③过程:kill旧PID1490375→试shell script(hf download --include per-snapshot)→发现需list全repo(56K files)也慢→kill shell PID57396→kill残留orphan PID61215(hf download child)→清理142 stale .lock文件→launch改进Python脚本PID349049。④当前:snapshot 1/110 SKIP(513 complete),snapshot 2/110 CC-MAIN-2013-48 downloading(115/513),634/56461 total,51GB,ETA~5.5天。⑤6目录盘点:Ultra-FineWeb base 524.43B/2.0TB✅|L3 40 shards✅|Code 30 shards✅|Math 40 shards✅|SFT-2605 20.96B/79GB✅|SFT-Agent 8.04B/30GB✅;R3合计110 .bin/5.4TB。⑥disk 37T free✅。⑦📦体积:TASK=30.1KB✅/MEMORY=20.3KB✅(无需归档)。下载线心跳：base✅全满|GPIC✅全满|en_v1_4🔄634/56461(2/110,PID349049,parallel 8+hf_transfer)|P-8数据层✅全就绪。

> 📦 唤醒295 原文已归档 → `daily-memories-data/2026-10-10.md`（含en_v1_4首次启动+hf download CLI超时+Python per-file脚本创建+PID1490375启动）

> 📦 唤醒293 原文已归档 → `daily-memories-data/2026-10-10.md`（含GPIC train 8000完成+val 14下载中+P-8全就绪+6目录盘点）

> 📦 唤醒292 原文已归档 → `daily-memories-data/2026-10-10.md`（含P-8全就绪巡检+GPIC 7982/8001+6目录盘点全完成）

> 📦 唤醒282-284 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 101-106/110巡检+code 21-26/30+GPIC 7817-7897+6目录盘点）

> 📦 唤醒290-291 原文已归档 → `daily-memories-data/2026-10-10.md`（含P-8全就绪巡检+GPIC 7946-7957/8001+6目录盘点）

> 📦 唤醒288 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 110/110DONE+contam scan启动+GPIC 7941/8001）

> 📦 唤醒282-289 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 101-109/110巡检全程+code 21-29/30+contam scan 30/30 DONE+GPIC 7817-7944/8001+6目录盘点）

> 📦 唤醒283 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 104/110巡检+code 24/30+GPIC 7845/8001）




> 📦 唤醒284-287 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 106-109/110巡检+code 26-29/30+GPIC 7874-7939/8001+6目录盘点）

> 📦 唤醒283 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 104/110巡检+code 24/30+GPIC 7845/8001）

> 📦 唤醒282 原文已归档 → `daily-memories-data/2026-10-10.md`（含R3 101/110巡检+code 21/30+GPIC 7817/8001）

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
> 📦 §⑨ 配比实验可行性核查 + §⑩ 运维三问 + 旧状态头（2026-10-05~07）已归档 → `daily-memories-data/2026-10-10.md`（唤醒305归档）；**结论**：⑨GPU2-7当时被P-9.8/9.9占满(现已释放)⑩三问已答(GPIC无加速/base下载全满/BO波次锯齿非I/O)。需要时再读。

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

