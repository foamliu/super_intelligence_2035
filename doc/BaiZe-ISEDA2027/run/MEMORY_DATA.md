# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ▶️en_v1_4全源分词(运维令10-18 21:0x:全源110shards不按500B截断)+▶️fullsource PID749330 MAX_CONCURRENT=32运行22.4h,done=39/110(+1 since 548的38,650.68B tok done-only,+24.37B/75min),71 .bin(39done+32in-progress大shard2017-2020),worker /proc/io alive(write +10MB/6s≈1.7MB/s),PENDING_DOWNLOAD=18(sh93-110)+1 downloading(sh92@358/512),全源ETA~4-5天(download-bound:sh92剩154files@2.4/min≈1.1h+17×512/2.4/min≈60.5h→~10-22 09:00下载完,再tokenize尾shards→~10-24/25)+▶️en_v1_4下载继续(PID2732959 resolve.py,92/110dirs,91full512,sh92(2023-23)in-progress@358/512@20:34,+178parquet/75min=2.4/min,0incomplete)+✅git sync健康(HTTPS remote,env无proxy,up-to-date@origin/main)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1/R2全完成; base下载完成; R3全量分词110/110DONE(1483.91B tok); R3污染扫描全0命中→P-8数据层全就绪; ✅GPIC/85M⏸/cauldron/wit_base/SFT-2605/RL-2609/InternVL/WebMix全就绪; ✅/tmp清理完成; ✅en_v1_4下载假活修复(restart PID2732959); ✅en_v1_4分词接管(运维令10-18 21:0x全源口径:fullsource PID749330 MAX_CONCURRENT=32,done=39/110,650.68B tok done-only); ✅fullsource.sh bug修复; ✅git sync(up-to-date@origin/main)
当前动作:     唤醒549(2026-10-19 20:34) en_v1_4全源分词巡检(运维令10-18 21:0x口径:全源110shards不按500B截断):①git fetch→up-to-date@origin/main(HTTPS remote,env无proxy);②fullsource PID749330 alive(etimes=80806s=22.4h,ppid=1),32workers全占(71 .bin=39done+32in-progress);③done=39/110(.bin+.idx+.json齐,较548的38增1);④done-only tokens=650,680,869,378(650.68B,39shard json num_tokens求和,+24.37B/75min);⑤32 in-progress .bin(2017-2020大shard,均未完成→大shard tokenize>10h,故done增速放缓);⑥worker alive经/proc/io write_bytes delta确认(244964 +10MB/6s=1.7MB/s,490068 +10MB/6s=1.7MB/s,693507 +10MB/6s=1.7MB/s,891525 +10MB/6s=1.7MB/s);⑦下载PID2732959 alive(resolve.py,92/110dirs,91full512,sh92(CC-MAIN-2023-23)in-progress@358/512@20:34,+178parquet/75min=2.4/min,0incomplete,18not-started(sh93-110),总parquet46950);⑧tokenized输出3.4T(.bin);⑨全源ETA~4-5天(download-bound:sh92剩154files@2.4/min≈1.1h+17×512/2.4/min≈60.5h→~10-22 09:00下载完,再tokenize尾shards→~10-24/25);⑩85M⏸。disk:train88%(27T)/user78%/inf80%/env4%。📦体积:TASK=29.3KB/MEMORY=16.6KB(本轮无归档,均≤32KB)
下一步:       ①监控fullsource(PID749330,32workers)至110/110,大shard(2017-2020)tokenize>10h,勿重启(重启丢22.4h大shard进度); ②监控下载(PID2732959)至110/110(sh92@358/512剩154files,17×512/2.4/min≈60.5h→~10-22 09:00下载完); ③全源完成后产出env14_fullsource_manifest.tsv+summary.json写入DATA_LEDGER; ④85M维持暂停; ⚠️保持32(下载是瓶颈,升64无益); ⚠️全源完成前不得写「en_v1_4分词完成」
阻塞:         None(全源分词+下载并行运行中,download-bound); 85M暂停(用户令10-13)
ERROR_COUNT:  8
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒549（2026-10-19 20:34）en_v1_4全源分词巡检:fullsource PID749330 32workers全占22.4h+done=39/110(较548的38增1,650.68B tok done-only+24.37B/75min,大shard2017-2020单shard>10h致done增速放缓)+71 .bin(39done+32in-progress)+worker /proc/io write_bytes 6s delta alive(244964+1.7MB/s,490068+1.7MB/s,693507+1.7MB/s,891525+1.7MB/s)+下载92/110dirs 91full512 sh92(2023-23)in-progress@358/512@20:34(+178parquet/75min=2.4/min,0incomplete,18not-started sh93-110,总parquet46950)+PENDING_DOWNLOAD=18+tokenized输出3.4T+全源ETA~4-5天(download-bound:sh92剩154files@2.4/min≈1.1h+17×512/2.4/min≈60.5h→~10-22 09:00下载完→~10-24/25全分完)+git up-to-date@origin/main(env无proxy,HTTPS remote)+85M⏸+disk train88%/user78%/inf80%/env4%+体积TASK=29.3KB/MEMORY=16.6KB无归档。详见 `daily-memories-data/2026-10-19.md`。

> 📦 唤醒548（2026-10-19 19:19）en_v1_4全源分词巡检:fullsource PID749330 32workers全占21.2h+done=38/110(较547的33增5,626.31B tok done-only+103.71B/75min=83Btok/hr)+32 in-progress .bin(2017-2020大shard,均未完成)+worker /proc/io delta alive(490068 1.6MB/s,693507 1.8MB/s,891525 1.5MB/s,918615 1.8MB/s,1095177 1.8MB/s)+下载92/110dirs 91full512 sh92(2023-23)in-progress@180/512@19:19(+174parquet/75min=2.3pm,0incomplete,18not-started sh93-110,总parquet46772)+PENDING_DOWNLOAD=18+tokenized输出3.2T+全源ETA~4-5天(download-bound:sh92剩332files@2.3pm≈2.4h+17×512/2.3pm≈62.5h→~10-22 10:00下载完→~10-24/25全分完)+git up-to-date@origin/main(env无proxy,HTTPS remote)+85M⏸+disk train88%/user78%/inf80%/env4%+体积TASK=29.9KB/MEMORY=15.7KB无归档。详见 `daily-memories-data/2026-10-19.md`。

> 📦 唤醒547（2026-10-19 18:04）en_v1_4全源分词巡检:fullsource PID749330 32workers全占19.9h+done=33/110(较546的28增5,522.60B tok done-only+94.99B/75min=76Btok/hr,小shard完成致速率回升)+32 in-progress .bin(大shard2016-19,均未完成)+worker /proc/io 6s delta alive(490068 1.6MB/s,693507 1.6MB/s,739834 1.6MB/s)+下载91/110dirs DONE sh92(2023-23)in-progress@6/512@18:04(7.0MB/s,0incomplete,18not-started sh93-110,总parquet46598)+PENDING_DOWNLOAD=18+tokenized输出8.4T+全源ETA~4天(download-bound:sh92刚起+18×3.3h≈60h→~10-22 05:00下载完→~10-23/24全分完)+git up-to-date@origin/main(env无proxy,HTTPS remote)+85M⏸+disk train87%/user78%/inf80%/env4%+体积TASK=29.9KB/MEMORY≈15.5KB无归档。详见 `daily-memories-data/2026-10-19.md`。
> 📦 唤醒546（2026-10-19 16:49）en_v1_4全源分词巡检:fullsource PID749330 32workers全占18.7h+done=28/110(较545的26增2,427.61B tok done-only+36.05B/81min=26.7Btok/hr,速率回落常态)+32 in-progress .bin(2015-35~2019-30大shard,均未完成)+worker /proc/io 6s delta alive(490068+1MB/s,693507+1MB/s,739834+1MB/s)+下载91/110dirs sh91(2023-14)in-progress@300/512@16:38(7.0MB/s,0incomplete,19not-started sh92-110)+PENDING_DOWNLOAD=19+32downloaded queued+全源ETA~4天(download-bound:sh91剩212files/2.2fpm≈96min→~18:25DONE+19×3.9h≈74h→~10-22 20:00下载完→~10-23/24全分完)+git up-to-date@origin/main(wake545commit@15:39已推,env无proxy,HTTPS remote)+85M⏸+disk train87%/user78%/inf80%/env4%+体积TASK=29.3KB/MEMORY=13.7KB无归档。详见 `daily-memories-data/2026-10-19.md`
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