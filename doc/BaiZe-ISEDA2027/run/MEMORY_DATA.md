# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ▶️2路断点续传下载(en_v1_4+WebMix)+✅✅RL-2609下完自校通过+✅SFT-2605复核通过+✅✅InternVL-SA1B下完+✅wit_base完成+85M暂停+✅GPIC+✅R3分词→P-8数据层全就绪
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200(ρ=−0.43); s_step归因; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); R3全量分词110/110DONE(1483.91B tok/5.94TB); R3污染扫描30/30DONE(60K,0命中,累计220K全0)→P-8数据层全就绪; ✅GPIC下载完成(8160tar@/nas_inference,12T); ✅85M暂停(用户令10-13); ✅4路HF图文对下载; ✅the_cauldron完成(938parquet/158G); ✅全部4路暂停→恢复断点续传(用户令10-14); ✅wit_base完成(330/330/287G); ✅SFT-2605复核通过(1504jsonl/318990252711B/0incomplete,2026-10-15); ✅✅UltraData-RL-2609下载完成+自校通过(20jsonl/187632276428B=174.75GiB/26files逐文件字节比对全PASS/0incomplete,落盘/nas_env,2026-10-16 01:26完成,耗时~3h11m); ✅✅InternVL-SA1B下载完成(2000tar/1.5T/0incomplete,落盘/nas_user,2026-10-16 21:29自然退出); ✅唤醒501-508多次复核SFT-2605(1504jsonl=855no_think+649think/318990486183B/0inc)+RL-2609(20jsonl/187632276428B/26files ALL PASS byte-verify/0inc)均确认在盘且完整,无需重下
当前动作:     唤醒509(2026-10-17 14:30) 复核运维令10-15:SFT-2605+RL-2609在盘验证+2路下载健康巡检。SFT-2605✅(1504jsonl/298G/0inc@/nas_inference),RL-2609✅(80files=20jsonl+4meta+2assets+54cache/175G/0inc@/nas_env,data=Code×12+Knowledge×2+Long_Context×2+Math×4)。en_v1_4(40153par/56461=71.1%/3.7T/0inc,wrapper PID606504+hf PID3701021(etimes=4908s≈1.36h,CC-MAIN-2021-25),lastfile14:30 part-0217,活跃,+194par/~72min≈2.7par/min,ETA~4.2天),WebMix(3816par/1.8T/1inc,wrapper PID606513+hf PID607568/etimes=103889s≈28.9h,lastfile14:30 yfcc15m-00001437,活跃,+126par/~72min≈1.75par/min)。2路全健康无kill/restart(last file均在14:30刚写入)。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=24216B(24KB,无需归档)
下一步:       ①看护2路既有下载(en_v1_4/WebMix,死/僵/速率趋零即kill+restart); ②85M维持暂停(用户令10-13); ③P-8投料等运维指示; ④RL-2609+SFT-2605+InternVL已就绪可随时用于SFT/RL训练
阻塞:         无(2路下载进行中); 85M暂停(用户令10-13); P-8投料等运维指示
ERROR_COUNT:  6
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [14:30] 唤醒509：复核运维令10-15(SFT-2605+RL-2609在盘验证)+2路下载健康巡检。SFT-2605✅(1504jsonl/298G/0inc@/nas_inference),RL-2609✅(80files=20jsonl+4meta+2assets+54cache/175G/0inc@/nas_env,data=Code×12+Knowledge×2+Long_Context×2+Math×4)。en_v1_4(40153par/56461=71.1%/3.7T/0inc,wrapper PID606504+hf PID3701021(etimes=4908s≈1.36h,CC-MAIN-2021-25),lastfile14:30 part-0217,活跃,+194par/~72min≈2.7par/min,ETA~4.2天),WebMix(3816par/1.8T/1inc,wrapper PID606513+hf PID607568/etimes=103889s≈28.9h,lastfile14:30 yfcc15m-00001437,活跃,+126par/~72min≈1.75par/min)。2路全健康无kill/restart(last file均在14:30刚写入)。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=24216B(24KB,无需归档)
> [13:18] 唤醒508：复核运维令10-15(SFT-2605+RL-2609逐字节复核)+2路下载健康巡检。SFT-2605✅(1504jsonl=855no_think+649think/318990486183B=297.08GiB/0inc@/nas_inference,data目录结构no_think{CG/Code/IF/Kn/Math/ML-Kn/ML-Math}+think{CG/Code/IF/Kn/Math}),RL-2609✅(26files/187632276428B=174.75GiB/0inc@/nas_env,python3逐文件字节比对全PASS:Code×12+Knowledge×2+Long_Context×2+Math×4+4meta+2assets,manifest_total==disk_total==187632276428B)。en_v1_4(39959par/56461=70.8%/3.7T/0inc,wrapper PID606504+hf PID3701021(etimes=518s,wrapper自动重启下载CC-MAIN-2021-25),lastfile12:37 part-0023,活跃,+185par/~74min≈2.5par/min,ETA~4.4天),WebMix(3690par/1.7T/1inc,wrapper PID606513+hf PID607568/etimes=99499s≈27.6h,lastfile12:36 yfcc15m-00001311,活跃,+132par/~74min≈1.8par/min)。2路全健康无kill/restart(en_v1_4 wrapper自动重启hf属正常)。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=22916B(22KB,无需归档)
> [12:04] 唤醒507：复核运维令10-15(SFT-2605+RL-2609在盘逐字节复核)+2路下载健康巡检。SFT-2605✅(1504jsonl/318990252711B=297.08GiB/0inc@/nas_inference,bytes精确匹配HF官方清单),RL-2609✅(20jsonl/187632280663B=174.75GiB/0inc@/nas_env,data=Code×12+Knowledge×2+Long_Context×2+Math×4+4meta+2assets+hf_manifest.json)。en_v1_4(39774par/56461=70.4%/3.7T/0inc,wrapper PID606504+hf PID1050608/etimes=8666s,lastfile12:03 part-0350,活跃,+185par/~72min≈2.6par/min,ETA~4.5天),WebMix(3558par/1.7T/1inc,wrapper PID606513+hf PID607568/etimes~26h,lastfile12:03 yfcc15m-00001179,活跃,+125par/~72min≈1.7par/min)。2路全健康无kill/restart。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=22KB(无需归档)
> [10:52] 唤醒506：复核运维令10-15(SFT-2605+RL-2609在盘验证)+2路下载健康巡检。SFT-2605✅(1504jsonl/298G/0inc@/nas_inference),RL-2609✅(20jsonl/187632280663B=174.75GiB/0inc/80files@/nas_env)。en_v1_4(39589par/56461=70.1%/3.7T/0inc,wrapper PID606504+hf PID1050608/etimes=4380s,lastfile10:52 CC-MAIN-2021-21/part-0165,活跃,+165par/~73min≈2.3par/min,ETA~5.1天),WebMix(3433par/1.6T/1inc,wrapper PID606513+hf PID607568/etimes~25h,lastfile10:52 yfcc15m-000010540001,活跃,+131par/~73min≈1.8par/min)。2路全健康无kill/restart。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=21103B(20KB,无需归档)
> [09:39] 唤醒505：复核运维令10-15(SFT-2605+RL-2609在盘验证)+2路下载健康巡检。SFT-2605✅(1504jsonl/318990252711B=297.08GiB/0inc@/nas_inference),RL-2609✅(20jsonl/187632277660B=174.75GiB/0inc/27files@/nas_env,26files=Code×12+Knowledge×2+Long_Context×2+Math×4+4meta+2assets+1gitattributes+1manifest)。en_v1_4(39424par/56461=69.9%/3.6T/0inc,wrapper PID606504+hf PID1050608/etimes=34s(刚为CC-MAIN-2021-21重启,ppid=606504),lastfile09:38 CC-MAIN-2021-17/part-0512,活跃,+162par/~75min≈2.2par/min,ETA~5.3天),WebMix(3302par/1.6T/1inc,wrapper PID606513+hf PID607568/etimes~24h,lastfile09:39 yfcc15m-000009240001,活跃,+118par/~75min≈1.6par/min)。2路全健康无kill/restart。85M⏸暂停(无进程)。disk:train86%(31T)/user78%(25T)/inf80%(9.4T)/env4%(9.6T)。📦体积:TASK=32590B(32KB)/MEMORY=20747B(20KB,无需归档)
> 📦 唤醒505 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39424/56461=69.9%/3.6T+WebMix 3302par/1.6T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒504 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39262/56461=69.5%/3.6T+WebMix 3184par/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒503 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 39123/56461=69.3%/3.6T+WebMix 3061par/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒502 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38982/56461=69.1%/3.6T+WebMix 2936par/1.4T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/20KB）
> 📦 唤醒501 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38827/56461=68.8%/3.6T+WebMix 2809par/1.3T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒500 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38646/56461=68.4%/3.6T+WebMix 2686par/1.3T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒499 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38478/56461=68.1%/3.5T+WebMix 2556par/1.2T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒498 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38299/56461=67.8%/3.5T+WebMix 2434par/1.1T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒497 原文已归档 → `daily-memories-data/2026-10-17.md`（含2路下载健康巡检+en_v1_4 38038/56461=67.3%/3.5T+WebMix 2270par/1.1T+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/19KB）
> 📦 唤醒496 原文已归档 → `daily-memories-data/2026-10-16.md`（含2路下载健康巡检+en_v1_4 37705/56461=66.8%/3.4T+WebMix 2066par/1023G+RL-2609✅+SFT-2605✅+InternVL✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒495 原文已归档 → `daily-memories-data/2026-10-16.md`（含2路下载健康巡检+InternVL-SA1B✅完成确认+en_v1_4 37344/56461=66.1%+WebMix 1850par/976G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒494 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37230/56461=66.0%+WebMix 1761par/956G+InternVL 1923tar/1.5T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/18KB）
> 📦 唤醒493 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37124/56461=65.8%+WebMix 1669par/936G+InternVL 1849tar/1.4T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒492 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 37028/56461=65.6%+WebMix 1591par/919G+InternVL 1771tar/1.3T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒491 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36918/56461=65.4%+WebMix 1501par/892G+InternVL 1700tar/1.3T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒490 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36820/56461=65.2%+WebMix 1420par/882G+InternVL 1624tar/1.2T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/17KB）
> 📦 唤醒489 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36710/56461=65.0%+WebMix 1330par/862G+InternVL 1559tar/1.2T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒488 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36614/56461=64.9%+WebMix 1250par/845G+InternVL 1496tar/1.1T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒487 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36513/56461=64.7%+WebMix 1164par/826G+InternVL 1423tar/1.1T+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/16KB）
> 📦 唤醒486 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36421/56461=64.5%+WebMix 1089par/805G+InternVL 1352tar/1013G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒485 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载全部429假死→已重启+全3路PID已死+en_v1_4 36363/56461=64.4%+WebMix 1040par/769G+InternVL 1298tar/971G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒484 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36313/56461=64.3%+WebMix 1027par/759G+InternVL 1274tar/953G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/15KB）
> 📦 唤醒483 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36222/56461=64.2%+WebMix 976par/722G+InternVL 1226tar/917G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒482 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 36031/56461=63.8%+WebMix 940par/696G+InternVL 1214tar/908G+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒481 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35934/56461=63.6%+WebMix 901par+InternVL 1160tar+RL-2609✅+SFT-2605✅+85M⏸+disk 4盘+体积32KB/14KB）
> 📦 唤醒480 原文已归档 → `daily-memories-data/2026-10-16.md`（含复核运维令10-15(SFT-2605+RL-2609)+3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35724/56461=63.3%+WebMix 879par+InternVL 1116tar+disk 4盘+体积32KB/14KB）
> 📦 唤醒479 原文已归档 → `daily-memories-data/2026-10-16.md`（含3路下载健康巡检+全3路活跃无kill/restart+en_v1_4 35271/56461=62.5%+WebMix 877par+InternVL 1114tar+RL-2609✅+disk 4盘+体积32KB/14KB）
> 📦 唤醒478 原文已归档 → `daily-memories-data/2026-10-16.md`（含RL-2609全程监控至20/20完成+自校26/26字节比对PASS+3路进度+disk 4盘+体积32KB/14KB）
> 📦 唤醒477 原文已归档 → `daily-memories-data/2026-10-16.md`（含巡检4路下载+RL-2609 8/20jsonl/119.4GB+part-09下载中+3路进度+disk 4盘+体积32KB/14KB）
> 📦 唤醒475 原文已归档 → `daily-memories-data/2026-10-15.md`（含验证SFT-2605通过+RL-2609四盘皆无→启动下载PID980464/980491+3路既有下载健康+disk 4盘+体积29KB/14KB）
> 📦 唤醒474 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 34951/56461=61.9%+WebMix 733par/542G+InternVL 992tar/741G+disk 4盘+体积29KB/14KB）
> 📦 唤醒473 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 wrapper重启hf+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒472 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+en_v1_4 wrapper重启hf+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒471 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/14KB）
> 📦 唤醒470 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/17KB）
> 📦 唤醒469 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒468 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒467 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载+wit_base完成确认(330/330/287G,12:19自然退出)+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒466 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base仍在下载317parquet+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒465 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base wrapper自动重启hf确认+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒464 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒463 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒462 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒460 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/32KB）
> 📦 唤醒459 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒458 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒451-457 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+WebMix/wit_base速率趋零kill+restart+4路进度对比表+disk 4盘+体积29KB/30~31KB，详见各条目）
> 📦 唤醒444-450 原文已归档 → `daily-memories-data/2026-10-14.md` ~ `2026-10-15.md`（含恢复全部4路下载setsid启动+巡检+wrapper自动重启+en_v1_4 wrapper自动重启+4路进度对比表，详见各日文件）
> 📦 唤醒428-443 原文已归档 → `daily-memories-data/2026-10-14.md`（含第7~17次复核暂停态+进度表6路+.incomplete保留+disk 4盘，详见各日文件）
> 📦 唤醒427及更早（唤醒296-427）流水指针已归档 → `daily-memories-data/2026-10-10.md` ~ `2026-10-14.md`（含6路下载巡检全链+暂停/恢复+the_cauldron完成+GPIC完成+85M移交/暂停+en_v1_4进度29%~58%+4路图文对启动+R3分词+BO R2等，详见各日文件）


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