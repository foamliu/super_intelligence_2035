# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ 迁移5/5源全DONE（唤醒641@22:3x确认/唤醒642@23:5x复核）**：math_l3✅+code_l3✅+math_l1✅+ufw_l3✅+code_l2✅(5源574bins/4.24TB全迁/nas_env,软链接全建好,源已删,迁移日志21:42:28 END)；85M降优先级后台跑(8926/12126=73.7%)。
> 🟢 **✅ /nas_env: 4.24TB已用/5.8T可用(43%)；/nas_train: 175T已用/33T可用(85%)**。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅全量分词5源DONE+✅en_v1_4全源110/110DONE+✅硬盘实测清单+✅迁移报告HTML+✅迁移5/5源全DONE(574bins/4.24TB→/nas_env,软链接✓)+▶️85M下载(8926/12126=73.7%)+✅git sync
已完成:       ✅5源全量分词(574shards/1056.36B/4.24TB); ✅en_v1_4全源110/110(2238.14B/8.88TB); ✅硬盘实测清单(HTML+TSV); ✅迁移报告HTML; ✅math_l3迁移DONE(67/67,313GB,软链接✓); ✅code_l3迁移DONE(63/63,516GB,软链接✓); ✅math_l1迁移DONE(149/149,614GB,软链接✓); ✅ufw_l3迁移DONE(154/154,990GB,软链接✓); ✅code_l2迁移DONE(141/141,1691GB,软链接✓); ✅迁移提速生效(50→271MB/s); ✅迁移全部完成(5/5源,574bins/4.24TB→/nas_env); ▶️85M下载(8926/12126=73.7%)
当前动作:     唤醒645(2026-10-25 03:24)：①跨日巡检续命：迁移=5/5源全DONE复核(无rsync/migrate进程,migrate_fast.log END@21:42:28,运维令18:1x迁移提速已由中继执行完成) ②85M 8926/12126(73.7%,+24自644,8incomplete,PID236391 hf download alive+PID581946 parallel16 alive,log显示正在下obelics/EN/part74,5.12s/it,ETA~4.5h,低优先级符合用户令) ③磁盘/nas_env 5.8T可用(43%)/nas_train 33T可用(85%) ④git sync正常(无ahead/behind,本线文件无改动,他线在途文件不动) ⑤体积TASK=30.2KB/MEMORY=29.0KB(均≤32KB✓) ⑥距上次data commit 02:17已~67min→超60min判死阈值→本轮必commit续命.📦体积：TASK=30.2KB/MEMORY=29.0KB（归档0KB，本轮无需归档）
下一步:       ①迁移全部完成→已交接pretrain(软链接可访问/nas_env数据) ②监控85M(8926/12126=73.7%,ETA~4.5h,低优先级,后台跑即可) ③text/14.90TB留/nas_train(en_v1_4分词产物,太大无法迁/nas_env) ④commit+push(data 645: 跨日巡检迁移全DONE复核+85M 73.7%续命)
阻塞:         无新阻塞;迁移全部完成;85M ETA~4.5h;text/14.90TB无法迁/nas_env需留/nas_train
ERROR_COUNT:  9
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [03:24] 唤醒645：跨日巡检续命（距上次data commit 02:17已~67min→超60min判死阈值→本轮必commit续命）①迁移=5/5源全DONE复核(无rsync/migrate进程,ps grep=0行,migrate_fast.log END@21:42:28,运维令18:1x迁移提速已由中继执行完成,无需agent代执行) ②85M 8926/12126(73.7%,+24自644,8incomplete;PID236391 hf download alive+PID581946 download_85m_parallel16.sh alive;/tmp/85M_dl_parallel.log tail显示正在下obelics/EN/part74,8926/12126 files 74%,5.12s/it;ETA~4.5h,低优先级符合用户令「85M下载优先级不高」) ③磁盘/nas_env 4.2T已用/5.8T可用(43%)/nas_train 175T已用/33T可用(85%) ④git sync正常(git status -sb无ahead/behind;本线文件无改动,他线在途文件baize_dualnode_16gpu_test.sh/harness/p8脚本/ops/.switch_to_relay_v2.sh等一律不动) ⑤体积TASK=30957B(30.2KB)/MEMORY=29696B(29.0KB)均≤32KB✓ ⑥无新运维令(所有顶部运维令均已闭合:迁移提速DONE+硬盘清单DONE+代理复测DONE) ⑦WAITING=1
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