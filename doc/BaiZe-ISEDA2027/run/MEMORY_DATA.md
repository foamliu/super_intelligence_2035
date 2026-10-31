# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ 运维令13:3x DONE（唤醒690,15:0x）**：分词 SFT-2605(94 shard/18.89B tok/75.87GB)+Agent-2609(13 shard/5.97B tok/23.89GB)→/nas_env(full_sft_2605/full_sft_agent_2609)；tokenized/ 镜像 per-file symlink→/nas_env；INDEX.tsv 922 shard triplet全OK inode_ok；DATA_MAPPING.md(10603B)行11-12=镜像完整；report_data_mapping_zh.html(20764B)12源全量更新；commit 44b512316 pushed。

> 🟢 **✅ 迁移5/5源全DONE**：math_l3✅+code_l3✅+math_l1✅+ufw_l3✅+code_l2✅(5源574bins/4.24TB全迁/nas_env,软链接全建好,源已删)。
> 🟢 **✅ 3稳定源迁移FINALIZE(唤醒678,00:3x)**：l1_en_hq(94shards)+zh(4)+AICC(1)→build_tokenized_mirror.py改symlink指向/nas_env/full_*→INDEX.tsv rebuild(815shard全triplet=OK inode=OK,3源storage=symlink)→DATA_MAPPING.md regen(指纹2953/7f2a09fb2920/00:34)→report_data_mapping_zh.html全量更新(总17.47TB,df 85%/82%)。源文件run4已删。
> 🟢 **✅ ufw_en迁移DONE(唤醒682,05:2x)**：ufw_en 32 shard / 3,222,004,397,626 B / 905.92B tokens → /nas_env/full_ufw_en/。text/源文件已删,tokenized/ 96 hardlink → per-file symlink指向/nas_env。build_tokenized_mirror.py改ufw_en ENTRIES(src_dir→/nas_env,storage=symlink)→INDEX.tsv rebuild(storage=symlink,triplet=OK,inode_ok=32)→DATA_MAPPING.md regen(bytes=3,222,004,397,626,storage=symlink)→gen_report_data_mapping_html.py新增报告生成脚本→report_data_mapping_zh.html重生成(9 symlink+1 hardlink,correct bytes)。commit ace6fac0b pushed。
> 🟢 **✅ 4源迁移全部完成**：ufw_en(32)+l1_en_hq(94)+zh(4)+AICC(1)=131 shard ≈ 4.05 TB → /nas_env。连同此前5源(574 shard/4.24TB)，/nas_env共承载9源/705 shard/~8.3TB；env14(110 shard)仍hardlink留/nas_train。
> 🟢 **✅ df实测(05:2x)**：/nas_train 174T已用/34T可用(84%,较迁移前177T/86%释放~3TB)；/nas_env 8.2T已用/1.8T可用(83%)。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        🔴运维令10-30恢复85M下载+盘点/nas_train.下载运行中(86.5%,字节增长确认+268MB/10s≈26.8MB/s).候选表49行已交付
已完成:       ✅A.85M下载已恢复(PID2668156脚本+PID471618 hf download运行中,10488/12126parquet=86.5%,8.incomplete活跃,无失败shard);✅B./nas_train盘点完成(cleanup_candidates_20261030.tsv 49行+DATA_MAPPING.md D节)
当前动作:     唤醒1011(2026-10-31 09:17):复核85M下载→du -sb 3次:40,470,325,465,205→40,470,593,745,911→40,470,593,745,911(+268,280,706B/10s=26.8MB/s✓,T3flat=NFS缓存间隙)→字节增长确认✓+8.incomplete(全sa1b/EN/part01_1,0-3.1G mtime09:13-09:17新鲜,非失败)+候选表49行✓→心跳
下一步:       下轮唤醒:①查85M下载进度(parquet数+incomplete数+字节增长,剩余1638parquet≈6.2TB@27MB/s≈2.7天);②待运维批准后执行删除
阻塞:         无
ERROR_COUNT:  11
未完成指令:   无(A+B均已交付)
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [09:17] 唤醒1011：复核85M下载 → ①ps确认PID2668156(bash,ppid=1,etimes=37188s≈10.3h)+PID471618(hf download,ppid=2668156,etimes=8021s≈2.2h)活跃;②du -sb 3次判活:40,470,325,465,205→40,470,593,745,911→40,470,593,745,911(T1→T2+268,280,706B/10s=26.8MB/s✓,T2=T3 flat=NFS缓存flush间隙);③parquet10,488/12,126=86.5%(+1 vs唤醒1010);④8 .incomplete(全sa1b/EN/part01_1:0-3.1G mtime09:13-09:17新鲜,非失败shard);⑤候选表49行✓(4可删+9保留+36待定)+DATA_MAPPING.md D节✓;⑥df:/nas_train173T/207T(84%),35T可用,/nas_env8.3T/10T(84%),1.7T可用;⑦ETA:剩余1638parquet≈6.2TB@~27MB/s→~2.7天→心跳
> 📦 唤醒1010(09:12)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长26.8MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1009(09:09)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长36.9MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1008(09:03)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长19.2MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1007(09:00)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长16.8MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1006(08:53)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长5.6MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1003(08:36)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载du-sb字节增长49.8MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1002(08:29)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长12.8MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒1000(08:19)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长17.9MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒999(10-31 08:15)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长49.2MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒998(10-31 08:1x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长17.9MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒996(10-31 08:2x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长26.8MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒995(10-31 08:1x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长6.7-20MB/s✓+候选表49行确认,详见日文件）
> 📦 唤醒994(10-31 08:0x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长31-33MB/s✓+修复D节5处缺失du -sb,详见日文件）
> 📦 唤醒992(10-31 07:41)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长402MB+候选表49行确认,详见日文件）
> 📦 唤醒991(10-31 07:35)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长959MB+候选表49行确认,详见日文件）
> 📦 唤醒990(10-31 07:32)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长10.9MB/s+候选表49行确认,详见日文件）
> 📦 唤醒989(10-31 07:15)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长22-49MB/s+候选表扩充至49行,详见日文件）
> 📦 唤醒987(10-31 07:00)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长34MB/s+候选表确认,详见日文件）
> 📦 唤醒986(10-31 06:55)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长22MB/s+候选表确认,详见日文件）
> 📦 唤醒985(10-31 06:52)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长68MB/s+候选表确认,详见日文件）
> 📦 唤醒984(06:45)：复核85M下载持续运行 → ①ps确认PID2668156(bash脚本,etimes=28048s≈7h47m,ppid=1)+PID3425450(hf download,etimes=3346s≈55min,ppid=2668156)活跃;②du -sb=40,278,787,659,547(vs唤醒983@06:40=40,273,398,652,223,+5,389,007,324B/5min≈18MB/s✓);③parquet 10,445/12,126=86.3%(+2 vs唤醒983);④10.incomplete(sa1b/EN/part01_0,sizes 0-4.0GB,mtime 06:45活跃,无失败shard);⑤log tail"Fetching 12126 files: 86%|10450/12126 [53:30<08:34, 3.25it/s] Download complete";⑥候选表38行✓+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用,/nas_env 8.3T/10T(84%),1.7T可用;⑧ETA:剩余1681parquet≈6.7TB@18MB/s→~4.3天→更新心跳
> 📦 唤醒983(10-31 06:40)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒981(10-31 06:33)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [06:24] 唤醒979：复核85M下载持续运行 → ①ps确认PID2668156(bash脚本,etimes=26604s≈7h23m)+PID3425450(hf download,etimes=1902s≈31min,ppid=2668156)活跃;②2组du -sb判活:第1组T1=40,247,976,569,920→T2=40,248,043,673,631(+671MB/10s=67.1MB/s✓)→T3=flat;第2组T4=40,248,848,531,489→T5=40,249,049,711,190(+201MB/15s=13.4MB/s✓);整体T1→T5=+1,073,141,270B/35s=30.7MB/s均值✓;③parquet 10,441/12,126=86.1%(+1 vs唤醒978);④8.incomplete全活跃(sa1b/EN/part01_0,sizes 0-1.5GB,mtime 06:17-06:20新鲜,无失败shard);⑤候选表38行(3可删/6保留/26待定)✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用,/nas_env 8.3T/10T(84%),1.7T可用;⑦ETA:剩余1685parquet≈6.7TB@30.7MB/s→~2.5天→更新心跳
> 📦 唤醒978(10-31 06:16)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [06:16] 唤醒978：复核85M下载持续运行 → ①ps确认PID2668156(bash脚本,etimes=26350s≈7h19m)+PID3425450(hf download,etimes=1648s≈27min,ppid=2668156)活跃;②3x du -sb铁证连续递增:T1=40,243,103,428,643→T2=40,243,304,595,324→T3=40,243,706,995,521(Delta1=201,166,681B/10s=20.1MB/s✓ Delta2=402,400,197B/10s=40.2MB/s✓);③8.incomplete(1活跃3.82GB sa1b/EN/part01_0 +7队列0B);④parquet 10,440/12,126=86.1%(+7 vs唤醒977);⑤per-subset:coyo1940✅imagenet82✅laioncn562✅datacomp1b575✅mint705✅obelics5803✅sa1b774/1147(67.5%,+8)zero250m0/1310(0%);⑥候选表38行(3可删/6保留/26待定)✓+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用;⑧ETA:剩余1686parquet(sa1b373+zero250m1310)≈6.7TB→更新心跳
> 📦 唤醒977(10-31 06:12)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [06:12] 唤醒977（归档）：复核85M下载持续运行 → ①ps确认PID2668156(bash脚本,etimes=26051s≈7h14m)+PID3425450(hf download,etimes=1349s≈22min,ppid=2668156)活跃;②3x du -sb铁证连续递增:T1=40,236,658,058,761→T2=40,236,926,205,138→T3=40,237,194,771,040(Delta1=268,146,377B/10s=26.8MB/s✓ Delta2=268,565,902B/10s=26.9MB/s✓稳定);③8 .incomplete全活跃(mtime 06:12:30-06:12:47,sizes 0-4.36G,total 23.41GB,全在sa1b/EN/part01_0);④parquet 10,433/12,126=86.1%(flat vs唤醒976,因incomplete未完成不rename);⑤per-subset:coyo1940✅imagenet82✅laioncn562✅datacomp1b575✅mint705✅obelics5803✅sa1b766/1147(66.8%)zero250m0/1310(0%);⑥候选表38行(3可删/6保留/26待定)✓+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用,/nas_env 8.3T/10T(84%),1.7T可用;⑧ETA:剩余1691parquet(sa1b381+zero250m1310)≈6.7TB@26.9MB/s→~2.9天→更新心跳
> 📦 唤醒976(10-31 06:08)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒975(10-31 06:05)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒974(10-31 05:57)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒973(10-31 05:51)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [05:51] 唤醒973：复核85M下载 → ①ps确认PID2668156(bash脚本,etimes=24743s≈6.9h)alive,旧hf子进程PID3043316已退出(日志显示proxy 503→MaxRetryError崩溃),脚本自动重启新hf子进程PID3425450(etimes~2min,ppid=2668156);②du -sb超时(NFS 40TB目录慢),改用.incomplete文件判活:15s内AVXiG4 768M→805M(+37MB=2.5MB/s)+VtNVjj 268M→335M(+67MB=4.5MB/s)+Jc1qbA 1024M(持平,可能写满一块)=3活跃增长+5起步(0字节建立连接);③/proc/3425450/io:wchar=268MB write_bytes=268MB(2min内已写268MB≈2.2MB/s均速,含建立连接开销,将逐步加速);④parquet 10,433/12,126=86.1%(+6 vs唤醒972);⑤8 .incomplete(sa1b/EN/part01_0/train-00011~18),0失败shard(proxy 503已自动恢复);⑥候选表38行✓+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用;⑧ETA:剩余1693 parquet≈6.5TB,当前~7MB/s(刚重启爬坡),之前稳态~20-25MB/s→ETA~3天@25MB/s→更新心跳
> 📦 唤醒972(10-31 05:42)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [05:39] 唤醒971：复核85M下载持续运行 → ①ps确认PID2668156+3043316活跃(etimes=24082s≈6.7h+3137s≈52min,ppid=1/2668156);②du -sb 2次判活:40195231399324→40195432501121(+201MB/10s=20.1MB/s,严格递增✓);③.incomplete 9文件:7活跃(mtime05:38sizes128M-3.5G实时写入)+2队列(0字节,mtime05:15);④parquet 10,425/12,126=86.1%(持平唤醒970);⑤候选表39行✓(3可删+9保留+26待定)+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3天@20MB/s(剩余1701parquet≈6.6TB)→更新心跳
> 📦 唤醒970(10-31 05:34)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒969(10-31 05:29)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [05:34] 唤醒970：复核85M下载持续运行 → ①ps确认PID2668156+3043316活跃(etimes=23760s≈6.6h+2815s≈47min,ppid=1/2668156);②du -sb 3次判活:40188478676244→40188679863577→40188948014094(T1→T2+201MB/10s=20.1MB/s,T2→T3+268MB/10s=26.8MB/s,严格递增✓总+469MB/20s≈23.5MB/s);③.incomplete 9文件:7活跃(mtime05:33sizes1.3G-2.5G实时写入)+2队列(0字节,mtime05:15);④parquet 10,425/12,126=86.1%(+1 vs唤醒969);⑤候选表39行✓(3可删+9保留+26待定)+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3天@25MB/s(剩余1701parquet≈6.6TB)→更新心跳
> 📦 唤醒968(10-31 05:24)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒967(10-31 05:20)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒966(10-31 05:13)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒965(10-31 05:07)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒964(10-31 05:04)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒963(10-31 05:00)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [05:00] 唤醒963：复核85M下载持续运行 → ①ps确认PID2668156+3043316活跃(etimes=21656s≈6h+711s新hf子进程,ppid=1/2668156);②du -sb 3次判活:40142859100469→40143060221506→40143462545133(T1→T2+201MB/10s=20.1MB/s,T2→T3+402MB/10s=40.2MB/s,总+603MB/20s≈30.2MB/s✓严格递增);③parquet 10,415/12,126=86.0%(同962);④8 incomplete(活跃下载,无失败shard);⑤per-subset:coyo1940✅datacomp1b575✅imagenet82✅laioncn562✅mint705✅obelics5803✅sa1b748/1147(65.2%)zero250m0/1310(未开始);⑥候选表39行✓(3可删+9保留+26待定)+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用;⑧ETA~2.5天@30MB/s(剩余1711parquet:sa1b399+zero250m1310≈6.6TB)→更新心跳
> 📦 唤醒962(10-31 04:51)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [04:51] 唤醒962：复核85M下载持续运行 → ①ps确认PID2668156+3043316活跃(etimes=21162s≈5h52m+217s新hf子进程,ppid=1/2668156);②du -sb 4次判活:40131793901275→40131806040593→40131806040593→40132665638751(T1→T2+12.1MB,T2→T3flat=NFS缓存,T3→T4+859.6MB,总+872MB/30s≈29MB/s✓);③parquet 10,415/12,126=86.0%(+1vs961);④8 incomplete(sa1b/EN/part00_9:2+part01_0:6,sizes 268MB-1024MB,mtime04:49-04:51新鲜活跃,无失败shard);⑤per-subset:coyo1940✅datacomp1b575✅imagenet82✅laioncn562✅mint705✅obelics5803✅sa1b748/1147(65.2%)zero250m0/1310(未开始);⑥候选表39行✓(3可删+9保留+26待定)+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用;⑧ETA~2.5天@29MB/s(剩余1711parquet:sa1b399+zero250m1310≈6.6TB)→更新心跳
> 📦 唤醒961(10-31 04:46)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒960(10-31 04:38)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒959(10-31 04:34)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒957(10-31 04:23)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒956(10-31 04:14)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒955(10-31 04:11)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒954(10-31 04:06)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒953(10-31 04:01)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒952(10-31 03:58)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒951(10-31 03:53)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:53] 唤醒951：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=17640s≈4h54m,ppid=1/2668156);②du -sb 3次判活:40,056,628,208,862→40,056,762,368,813→40,058,360,252,167(+134MB/10s+1.73GB/2min≈24.5MB/s✓连续递增);③parquet 10,394/12,126=85.8%(+1 vs唤醒950);④incomplete 8文件(sa1b/EN/part00_9)mtime 03:48-03:52新鲜,sizes 0-3.9G,无失败shard;⑤候选表39行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.1天@24.5MB/s(剩余1732parquet≈6.67TB)→更新心跳
> 📦 唤醒950(10-31 03:47)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒949(10-31 03:43)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒947(10-31 03:31)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒946(10-31 03:26)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒945(10-31 03:22)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:22] 唤醒945：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=15867s≈4h24m,ppid=1/2668156);②3x连续du -sb判活:40,017,078,047,460→40,017,288,382,991→40,017,748,673,447(+460MB/20s≈23MB/s✓连续递增);③parquet 10,385/12,126=85.7%;④incomplete 8文件(sa1b/EN/part00_9全活跃),无失败shard;⑤候选表39行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.4天@23MB/s(剩余1741parquet≈6.7TB)→更新心跳
> 📦 唤醒944(10-31 03:17)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:17] 唤醒944：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=15573s≈4h19m,ppid=1/2668156);②du -sb 2次判活:40,012,285,692,233→40,012,486,847,362(+201MB/15s≈13.4MB/s✓);③parquet 10,385/12,126=85.7%;④incomplete 8文件(sa1b/EN/part00_9全活跃),无失败shard;⑤候选表39行✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~5.8天@13.4MB/s(剩余1741parquet≈6.7TB)→更新心跳
> 📦 唤醒943(10-31 03:15)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:15] 唤醒943：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=15241s≈4h14m,ppid=1/2668156);②du -sb 2次判活:40,005,897,845,276→40,006,233,147,960(+335MB/20s≈15MB/s✓);③parquet 10,386/12,126=85.7%(+2 vs唤醒942);④per-subset:coyo1940✅datacomp575✅imagenet82✅laioncn562✅mint705✅obelics5803✅sa1b717/1147(62.5%)zero250m0/1310;⑤incomplete 8文件(sa1b/EN/part00_9,64M-4.0G全活跃增长,mtime 03:11新鲜),无失败shard;⑥候选表38行✓+DATA_MAPPING.md D节✓;⑦df:/nas_train 173T/207T(84%),35T可用;⑧ETA~5.1天@15MB/s(剩余1740parquet≈6.7TB)→更新心跳
> 📦 唤醒942(10-31 03:08)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:08] 唤醒942：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=15002s≈4h10m,ppid=1/2668156);②du -sb 2次判活:39,998,790,330,001→39,999,527,979,396(+737MB/3min≈4.1MB/s瞬时✓,自唤醒941 +7.73GB/8min≈16.1MB/s均值✓);③parquet 10,384/12,126=85.6%(+3 vs唤醒941);④incomplete 8文件(sa1b/EN/part00_9,5个活跃增长3.2G/2.7G/1.0G/896M/128M+3个刚启0B,mtime 03:03-03:07新鲜),无失败shard;⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~4.8天@16.1MB/s(剩余1742parquet≈6.7TB)→更新心跳
> 📦 唤醒941(10-31 03:0x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [03:00] 唤醒941：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=14626s≈4h4m,ppid=1/2668156);②du -sb 2次判活:39,991,397,015,987→39,991,799,348,871(+402MB/~1min≈6.7MB/s瞬时✓,自唤醒940 +6.87GB/5min≈22.9MB/s均值✓);③parquet 10,381/12,126=85.6%(+1 vs唤醒940);④incomplete 8文件(sa1b/EN/part00_9)0-4.16GB全活跃增长(mtime 02:57-03:01新鲜),总14.76GB,无失败shard;⑤候选表39行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.4天@22.9MB/s(剩余1745parquet≈6.7TB)→更新心跳
> 📦 唤醒940(10-31 02:5x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:5x] 唤醒940：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=14292s≈3h58m,ppid=1/2668156);②du -sb 3次判活:39,984,331,524,788→39,984,532,749,792→39,984,532,749,792(T1→T2 +201MB/15s≈13.4MB/s✓,T2=T3为NFS写缓冲flush间隙但.incomplete mtime 02:55新鲜+log活跃Downloading);③parquet 10,378/12,126=85.6%(log tail已到10380);④incomplete 8文件(sa1b/EN/part00_9)256M-3.8G全活跃增长(mtime 02:55),无失败shard;⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~5.8天@13.4MB/s(剩余1748parquet≈6.7TB)→更新心跳
> 📦 唤醒939(10-31 02:5x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:5x] 唤醒939：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=14015s≈3h54m,ppid=1/2668156);②du -sb 3次判活:39,977,617,879,064→39,977,752,032,465→39,979,227,421,126(连续3次递增✓+1.6GB/~3min≈9MB/s);③parquet 10,378/12,126=85.6%(+2 vs唤醒938);④incomplete 8文件(sa1b/EN/part00_9)mtime 02:50-51新鲜(128M-3.0G,全活跃增长),无失败shard;⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~4.2天@9MB/s(剩余1748parquet≈5.8TB)→更新心跳
> 📦 唤醒938(10-31 02:46)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒937(10-31 02:41)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:41] 唤醒937：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=13419s≈3h44m,ppid=1/2668156);②du -sb 3次判活:39,965,707,049,729→39,966,042,432,274→39,966,176,571,401(连续3次递增✓+335MB+134MB/10s≈21MB/s);③parquet 10,376/12,126=85.6%(+2 vs唤醒936);④incomplete 8文件(sa1b/EN/part00_9)mtime 02:38-41新鲜(6个有数据335MB-3.3GB,2个0byte刚启动),无失败shard;⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.2天@21MB/s(剩余1750parquet≈5.8TB)→更新心跳
> 📦 唤醒936(10-31 02:35)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:35] 唤醒936：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=13068s≈3h37m,ppid=1);②du -sb 3次判活:39,957,889,415,119→39,958,165,841,481→39,958,414,650,131(连续3次递增✓+276MB+249MB/10s≈26MB/s);③parquet 10,374/12,126=85.5%(+1 vs唤醒935);④incomplete 8文件(sa1b/EN/part00_9)mtime 02:34-35新鲜,无失败shard;⑤候选表39行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.0天@26MB/s(剩余1752parquet≈6.8TB)→更新心跳
> 📦 唤醒935(10-31 02:32)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒934(10-31 02:27)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒933(10-31 02:35)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:35] 唤醒933：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=12338s≈3h26m);②du -sb 3次判活:39,941,072,377,341→39,941,340,483,544→39,941,504,961,082(+432MB/20s≈21.6MB/s✓连续2次递增);③parquet 10,368/12,126=85.5%(flat vs唤醒932);④incomplete 8文件(sa1b/EN/part00_9)mtime 02:22新鲜,无失败shard;⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~3.7天@21.6MB/s(剩余1758parquet≈6.8TB)→更新心跳
> 📦 唤醒932(10-31 02:25)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [02:25] 唤醒932：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=11912s≈3h18m);②du -sb:39,932,841,057,620→39,933,493,792,822→39,933,493,792,822(+652MB,后次flat=NFS缓存);③incomplete 8文件(sa1b/EN/part00_9)总14.15GB,mtime 02:17新鲜,15s窗口flat=网络波动;④parquet 10,368/12,126=85.5%(+2 vs唤醒931);⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦git data线clean→更新心跳
> 📦 唤醒931(10-31 02:20)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒930(10-31 02:11)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒929(10-31 02:02)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒928(10-31 01:59)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒927(10-31 01:54)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒926(10-31 01:50)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒925(10-31 01:46)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒924(10-31 01:43)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒922(10-31 01:29)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒921(10-31 01:25)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒920(10-31 01:21)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒919(10-31 01:2x)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒918(10-31 01:12)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒917(10-31 01:09)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [01:09] 唤醒917：复核85M下载持续运行 → ①ps确认PID2668156活跃(etimes=7846s≈2h11m);②字节增长判活(du -sb 2次):39,845,063,904,502→39,845,331,122,469(+268MB/15s≈17.9MB/s✓);③parquet 10,348/12,126=85.3%(+3 since唤醒916);④8.incomplete=活跃下载(sa1b/EN/part00_8);⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~4天@17.9MB/s(剩余1778parquet≈6.8TB)→更新心跳
> 📦 唤醒916(10-31 01:06)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒915(10-31 01:09)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒914(10-31 00:53)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> [00:53] 唤醒914：复核85M下载持续运行 → ①ps确认PID2668156+2668173活跃(etimes=6926s≈1h55m);②字节增长判活(du -sb):39,824,460,233,351→39,824,712,801,274(+252MB/15s≈16.8MB/s✓);③parquet 10,343/12,126=85.3%(+1 since唤醒913);④8.incomplete=活跃下载(sa1b/EN/part00_8,sizes 0-4.0GB);⑤候选表38行✓+DATA_MAPPING.md D节✓;⑥df:/nas_train 173T/207T(84%),35T可用;⑦ETA~4.7天@16.8MB/s(剩余1783parquet)→更新心跳
> 📦 唤醒913(10-31 01:02)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒912(10-31 00:44)原文归档 → daily-memories-data/2026-10-31.md（复核85M下载字节增长+候选表确认,详见日文件）
> 📦 唤醒833-910 原文已归档 → daily-memories-data/2026-10-30.md ~ 2026-10-31.md（例行巡检+85M字节增长复核,详见日文件）
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

> 📦 §⑪ 分词5worker+85M线路（2026-10-24 用户质询）已归档 → daily-memories-data/2026-10-24.md；**结论**：Q1=5worker因串行+剩余shard少,升级65并发后110/110 DONE@11:48;Q2=92.25+hf.co直连✓(无HF_ENDPOINT)。需要时再读。

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