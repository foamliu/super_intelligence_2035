# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ⏸85M暂停(用户令2026-10-13,8436/12124=69.6%,保留已下~29T不删)+🔄4路HF图文对新下载→/nas_user(WebMix-38M 33GB+wit_base 54GB+InternVL-SA1B 110GB+the_cauldron 118GB,合计~315GB已下/~4TB目标)+🔄en_v1_4(PID2535486,31412/56461=55.6%,62/110dirs)+✅GPIC全完成(8000tar/12T)+✅R3分词110/110+✅HF imagetext报告→P-8数据层全就绪
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200(ρ=−0.43); s_step归因; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); R3全量分词110/110DONE(1483.91B tok/5.94TB); R3污染扫描30/30DONE(60K,0命中,累计220K全0)→P-8数据层全就绪; ✅GPIC下载完成(8160tar@/nas_inference,12T); ✅文献借鉴报告(c80c7a74); ✅85M用户进程移交data线; ✅HfApi核实85M总量(12,124files/46.663TB); ✅HF imagetext数据集调研报告(唤醒404); ✅85M暂停(用户令10-13,kill PID2420118+2420132,保留8436/12124=69.6%); ✅4路HF图文对下载启动(唤醒405,落/nas_user/datasets/,retry-loop守护)
当前动作:     唤醒418(06:25@.12) 巡检5路下载全活。en_v1_4 PID2535486活(ppid=1,etimes~305799s≈3.5d,31412/56461=55.6%,62/110dirs,+151parquet vs 417,0.incomplete✅)。4路新下载全活:WebMix-38M(33GB/138files)+wit_base(54GB/192files)+InternVL-SA1B(110GB/444files)+the_cauldron(118GB/2562files),retry-loop wrappers ppid=1✅(PID1601763/1604572/1604593/1604595,etimes~27970s≈7.8h),各1.incomplete(正常),合计~315GB/~4TB目标,4路+31GB vs 417(~36min≈14.4MB/s)。85M⏸暂停(无进程,8436parquet保留)。GPIC✅8000tar/12T。disk:/nas_user 75%/28T✅,/nas_train 85%/33T✅,/nas_inference 80%/9.4T✅
下一步:       ①每唤醒监控4路新下载+en_v1_4进度(PID/文件数/.incomplete/磁盘,死即重启); ②85M保持暂停(用户令,不重启,保留已下内容); ③en_v1_4下满56461后经check_contamination.py再报"完成"; ④4路下满后逐个核实文件数+du -sh→心跳报完成; ⑤⚠️/nas_user逼近90%时停新下载等运维; ⑥P-8投料等运维指示
阻塞:         4路HF图文对下载进行中(合计~4TB,ETA数天~数周,带宽争用); en_v1_4下载进行中(ETA~3天); 85M暂停中(用户令2026-10-13,不重启); P-8投料等运维指示
ERROR_COUNT:  3
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒407 原文已归档 → `daily-memories-data/2026-10-14.md`（含6路下载巡检+en_v1_4 29091/56461=51.5%+4路新下载全活+disk 85%）
> 📦 唤醒406 原文已归档 → `daily-memories-data/2026-10-13.md`（含6路下载巡检+en_v1_4 28853/56461=51.1%+误启2nd进程2s内kill+4路新下载全活+disk 85%）
> 📦 唤醒408 原文已归档 → `daily-memories-data/2026-10-14.md`（含6路下载巡检+en_v1_4 29330/56461=51.9%+4路新下载全活+disk 85%）
> 📦 唤醒409 原文已归档 → `daily-memories-data/2026-10-14.md`（含6路下载巡检+en_v1_4 29494/56461=52.2%+4路新下载全活+GPIC✅8160tar+disk 85%）
> 📦 唤醒410 原文已归档 → `daily-memories-data/2026-10-14.md`（含6路下载巡检+en_v1_4 29696/56461=52.6%+4路新下载全活+GPIC✅8160tar+disk 85%）
> 📦 唤醒411 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 29997/56461=53.1%+4路新下载全活+disk 85%）
> 📦 唤醒412 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 30197/56461=53.5%+4路新下载全活+disk 85%）
> 📦 唤醒413 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 30362/56461=53.8%+4路新下载全活合计~201GB+disk 85%）
> 📦 唤醒414 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 30578/56461=54.1%+4路新下载全活合计~224GB+disk 85%）
> 📦 唤醒415 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 30896/56461=54.7%+4路新下载全活合计~234GB+disk 85%）
- [06:25] **唤醒418**：巡检5路下载全活。①en_v1_4 PID2535486活(ppid=1,etimes~305799s≈3.5d,31412/56461=55.6%,62/110dirs,+151parquet vs 417,0.incomplete✅)。②4路新下载全活且健康:WebMix-38M(33GB/138files)+wit_base(54GB/192files)+InternVL-SA1B(110GB/444files)+the_cauldron(118GB/2562files),retry-loop wrappers ppid=1✅(PID1601763/1604572/1604593/1604595,etimes~27970s≈7.8h),各1.incomplete(正常),合计~315GB/~4TB目标。进度增量vs 417(~36min):WebMix+2GB/+9files,wit_base+3GB/+9files,InternVL+15GB/+57files,cauldron+11GB/+81files,4路合计+31GB≈14.4MB/s。③85M⏸暂停(无进程,用户令,8436parquet保留)。④GPIC✅8000tar/12T。⑤disk:/nas_user 75%/28T✅,/nas_train 85%/33T✅,/nas_inference 80%/9.4T✅。⑥📦体积:TASK=32.0KB(32738B,逼近32KB红线⚠️)/MEMORY=24.0KB(均≤32KB✅)。下载线心跳：85M⏸暂停(69.6%,用户令)|en_v1_4🔄31412/56461(55.6%,PID2535486活)|WebMix-38M🔄33GB|wit_base🔄54GB|InternVL-SA1B🔄110GB|the_cauldron🔄118GB|GPIC✅8000tar/12T|P-8数据层✅全就绪
> 📦 唤醒417 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 31261/56461=55.4%+4路新下载全活合计~284GB+disk 85%）
> 📦 唤醒416 原文已归档 → `daily-memories-data/2026-10-14.md`（含5路下载巡检+en_v1_4 31104/56461=55.1%+4路新下载全活合计~256GB+disk 85%）
> 📦 唤醒405 原文已归档 → `daily-memories-data/2026-10-13.md`（含4路HF图文对下载启动+85M kill+en_v1_4 28732/56461=50.9%+disk 85%）
> 📦 唤醒404 原文已归档 → `daily-memories-data/2026-10-13.md`（含HF imagetext调研报告生成+85M 8427/12124=69.5%+en_v1_4 36962/56461=65.5%+disk 85%）

> 📦 唤醒402 原文已归档 → `daily-memories-data/2026-10-13.md`（含85M健康检查：retry-loop PID2420118活 8376/12124=69.1% obelics4512/5803=77.8% 12.5MB/s avg+en_v1_4 27658/56461=49.0% 55/110+disk 85%）
> 📦 唤醒401 原文已归档 → `daily-memories-data/2026-10-13.md`（含85M健康检查：retry-loop PID2420118活 8368/12124=69.0% obelics4504/5803=77.6% 3.36MB/s inst/10.19MB/s avg+en_v1_4 27522/56461=48.7% 55/110+disk 85%）
> 📦 唤醒400 原文已归档 → `daily-memories-data/2026-10-13.md`（含85M PID506606 proxy 503崩溃→retry-loop脚本重启PID2420118+2420132断点续传obelics/EN/part63+en_v1_4 27329/56461=48.4%+disk 85%）
> 📦 唤醒399 原文已归档 → `daily-memories-data/2026-10-13.md`（含第九十五次采样：85M PID506606活 8361/12124=69.0% obelics4497/5803=77.5% 62MB/s+en_v1_4 35109/56461=62.2% 53/110 21.8MB/s+disk 85% 32T avail）
> 📦 唤醒398 原文已归档 → `daily-memories-data/2026-10-13.md`（含85M用户进程移交data线：kill用户PID555408+download.sh+自动重启子进程,清.incomplete,setsid重启PID506606 ppid=1,断点续传obelics/EN/part63,12MB/s initial）
> 📦 唤醒397 原文已归档 → `daily-memories-data/2026-10-13.md`（含第九十四次采样：en_v1_4 26385/56461=46.7% 52/110+s52 CC-MAIN-2018-47 250/512+85M 8348/12124=68.9% obelics4484/5803=77.3% 5.04MB/s(19s)/3.73MB/s(40min)+12.86MB/s(19s)/16.64MB/s(40min)+争用20.37MB/s(40min)）
> 📦 唤醒396 原文已归档 → `daily-memories-data/2026-10-13.md`（含第九十三次采样：en_v1_4 26291/56461=46.6% 52/110+s52 CC-MAIN-2018-47 150/512+85M 8338/12124=68.8% obelics4474/5803=77.1% 2.78MB/s(184s)/4.66MB/s(41min)+19.75MB/s(184s)/15.36MB/s(avg since restart)+争用20.02MB/s(41min)）
> 📦 唤醒393 原文已归档 → `daily-memories-data/2026-10-13.md`（含第九十次采样：en_v1_4 25924/56461=45.9% 51/110+s51 CC-MAIN-2018-43 300/512+85M 8309/12124=68.5% obelics4445/5803=76.6% 15.15MB/s(57s)/13.57MB/s(38min)+8.25MB/s(57s)/8.56MB/s(38min)+争用22.13MB/s(38min)）
> 📦 唤醒391 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十八次采样：en_v1_4 25436/56461=45.0% 50/110+s50 CC-MAIN-2018-39 300/512+85M 8299/12124=68.4% obelics4435/5803=76.4%+争用20.19MB/s(39min)）
> 📦 唤醒390 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十七次采样：en_v1_4 25173/56461=44.6% 50/110+s50 CC-MAIN-2018-39 50/512+85M 8294/12124=68.4% obelics4430/5803=76.3%+争用20.02MB/s(37min)）
> 📦 唤醒389 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十六次采样：en_v1_4 24936/56461=44.2% 49/110+s49 CC-MAIN-2018-34 350/512+85M 8287/12124=68.3% obelics4423/5803=76.2%+争用20.66MB/s(39min)）
> 📦 唤醒388 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十五次采样：en_v1_4 24823/56461=44.0% 49/110+s49 CC-MAIN-2018-34 200/512+85M 8279/12124=68.3% obelics4415/5803=76.1%+争用20.39MB/s(36min)）
> 📦 唤醒387 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十四次采样：en_v1_4 24741/56461=43.8% 49/110+s49 CC-MAIN-2018-34 150/512+85M 8270/12124=68.2% obelics4405/5803=75.9%+争用20.15MB/s(38min)）
> 📦 唤醒386 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十三次采样：en_v1_4 24631/56461=43.6% 49/110+s49 CC-MAIN-2018-34 50/512+85M 8261/12124=68.1% obelics4397/5803=75.8%+争用20.12MB/s(37min)）
> 📦 唤醒385 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十二次采样：en_v1_4 24491/56461=43.3% 48/110+s48 CC-MAIN-2018-30+85M 8253/12124=68.1% obelics4389/5803=75.6% 8.85MB/s(75s)/3.52MB/s(41min)+36.3MB/s(75s burst)/16.40MB/s(41min)+争用19.92MB/s(41min)）
> 📦 唤醒384 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十一次采样：en_v1_4 24411/56461=43.2% 48/110+s48 CC-MAIN-2018-30+85M 8243/12124=68.0% obelics4379/5803=75.5% 5.48MB/s(119s)/10.38MB/s(41min)+24.83MB/s(119s)/11.04MB/s(41min)+争用21.42MB/s(41min)）
> 📦 唤醒383 原文已归档 → `daily-memories-data/2026-10-13.md`（含第八十次采样：en_v1_4 24185/56461=42.8% 48/110+s48 CC-MAIN-2018-30+85M 8237/12124=67.9% obelics4373/5803=75.3% 4.85MB/s(30s)/5.12MB/s(35min)+6.40MB/s(30s)/16.13MB/s(35min)+争用21.25MB/s(35min)）
> 📦 唤醒382 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十九次采样：en_v1_4 24084/56461=42.6% 48/110+s48刚启动+85M 8230/12124=67.8% obelics4366/5803=75.2% 1.0MB/s(40s↓)/3.70MB/s(39min)+54.6MB/s(40s burst)/16.77MB/s(39min)+争用20.47MB/s(39min)）
> 📦 唤醒381 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十八次采样：en_v1_4 24000/56461=42.5% 47/110+s47 400/512+85M 8220/12124=67.8% obelics4356/5803=75.1% 1.0MB/s(31s↓)/3.40MB/s(37min↓)+7.8MB/s(31s)/16.44MB/s(37min)+争用19.84MB/s(37min)）
> 📦 唤醒380 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十七次采样：en_v1_4 23930/56461=42.4% 47/110+s47 ~350/512+85M 8211/12124=67.7% obelics4347/5803=74.9% 5.5MB/s(56s)/5.25MB/s(81min)+17.5MB/s(56s)/15.8MB/s(81min)+争用21.1MB/s(81min)）
> 📦 唤醒379 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十六次采样：en_v1_4 23827/56461=42.2% 47/110+s47 ~283/512+85M 8201/12124=67.6% obelics4337/5803=74.7% 5.2MB/s(83s)/5.9MB/s(40min)+2.4MB/s(83s)/14.4MB/s(40min)+争用20.3MB/s(40min)）
> 📦 唤醒378 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十五次采样：en_v1_4 23697/56461=42.0% 47/110+s47 150/512+85M 8193/12124=67.6% obelics4329/5803=74.6% 8.3MB/s(83min)/12.8MB/s(83min)+争用21.1MB/s(83min)）
> 📦 唤醒377 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十四次采样：en_v1_4 23568/56461=41.7% 47/110+s47 512files+85M 8183/12124=67.5% obelics4319/5803=74.4% 10.1MB/s(41min)/9.9MB/s(41min)+争用20.0MB/s(41min)）
> 📦 唤醒376 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十三次采样：en_v1_4 23258/56461=41.2% 46/110+s46 200/512+85M 8177/12124=67.4% obelics4313/5803=74.3% 10.4MB/s(39min)/11.0MB/s(39min)+争用21.4MB/s(39min)）
> 📦 唤醒375 原文已归档 → `daily-memories-data/2026-10-13.md`（含第七十二次采样：en_v1_4 22989/56461=40.7% 45/110+s45 450/512+85M 8171/12124=67.4% obelics4307/5803=74.2% 10.4MB/s(41min)/10.5MB/s(39min)+争用20.9MB/s(41min)）
> 📦 唤醒374 原文已归档 → `daily-memories-data/2026-10-12.md`（含第七十一次采样：en_v1_4 22718/56461=40.2% 45/110+s45 200/512+85M 8165/12124=67.3% obelics4301/5803=74.1% 11.2MB/s(43min)/9.9MB/s(43min)+争用21.1MB/s(43min)）
> 📦 唤醒373 原文已归档 → `daily-memories-data/2026-10-12.md`（含第七十次采样：en_v1_4 22432/56461=39.7% 44/110+s44 400/512+85M 8159/12124=67.3% obelics4295/5803=74.0% 8.9MB/s(180s)/11.8MB/s(37min)+3.4MB/s(180s)/11.3MB/s(37min)+争用23.1MB/s(37min)）
> 📦 唤醒372 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十九次采样：en_v1_4 22155/56461=39.2% 44/110+s44 100/512+85M 8154/12124=67.2% obelics4289/5803=73.9% 5.4MB/s(240s)/10.9MB/s(41min)+2.2MB/s(240s)/8.5MB/s(41min)+争用19.4MB/s(41min)）
> 📦 唤醒371 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十八次采样：en_v1_4 21869/56461=38.7% 43/110+s43 350/512+85M 8148/12124=67.2% obelics4284/5803=73.8% 21.5MB/s(99s)/13.1MB/s(38.5min)+8.1MB/s(38.5min)+争用21.2MB/s(38.5min)）
> 📦 唤醒370 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十七次采样：en_v1_4 21583/56461=38.2% 43/110+s43 50/512+85M 8144/12124=67.1% obelics4280/5803=73.8% 10.55MB/s(74s)/13.67MB/s(41min)+8.16MB/s(74s)/6.84MB/s(41min)+争用18.70MB/s(74s)）
> 📦 唤醒369 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十六次采样：en_v1_4 21303/56461=37.7% 42/110+s42 300/512+85M 8140/12124=67.1% obelics4276/5803=73.7% 12.85MB/s(82s)/12.50MB/s(44min)+3.27MB/s(82s)/8.43MB/s(44min)+争用16.12MB/s(82s)）
> 📦 唤醒368 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十五次采样：en_v1_4 21024/56461=37.2% 42/110+s42+85M 8135/12124=67.1% obelics4271/5803=73.6% 7.95MB/s(56s)/0.005MB/s(85M瞬时近零)/12.07MB/s(40min)+争用7.96MB/s(56s)）
> 📦 唤醒367 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十四次采样：en_v1_4 20723/56461=36.7% 40/110+s41 250/512+85M 8130/12124=67.1% obelics4266/5803=73.5% 13.73MB/s(141s)/10.04MB/s+争用23.77MB/s）
> 📦 唤醒366 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十三次采样：en_v1_4 20444/56461=36.2% 40/110+s40 450/512+85M 8124/12124=67.0% obelics4260/5803=73.4% 8.43MB/s(77s)/16.55MB/s(burst)+争用24.98MB/s）
> 📦 唤醒365 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十二次采样：en_v1_4 20178/56461=35.7% 40/110+s40 200/512+85M 8119/12124=67.0% obelics4255/5803=73.3% 17.1MB/s(76s)+争用26.0MB/s）
> 📦 唤醒364 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十一次采样：en_v1_4 19943/56461=35.3% 38/110+s38 450/512+85M 8113/12124=66.9% obelics4249/5803=73.2% 8.16MB/s(128s)有retry+争用9.2MB/s↓）
> 📦 唤醒363 原文已归档 → `daily-memories-data/2026-10-12.md`（含第六十次采样：en_v1_4 19666/56461=34.8% 38/110+s38 200/512+85M 8109/12124=66.9% obelics4245/5803=73.1% 11.3MB/s burst窗口+争用25.2MB/s）
> 📦 唤醒361 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十八次采样：en_v1_4 19082/56461=33.8% 38/110+s38 100/512+85M 8100/12124=66.8% obelics4236/5803=73.0% 14.2MB/s✅稳态+争用26.2MB/s）
> 📦 唤醒360 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十七次采样：85M旧PID1192761已死→用户重启PID1015571初始扫描7.6MB/s+en_v1_4 18797/56461=33.3% 37/110+s37 350/512+争用22.8MB/s）
> 📦 唤醒359 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十六次采样：en_v1_4 18449/56461=32.7% 37/110+s37 CC-MAIN-2017-34+85M 8093/12124=66.8% obelics4229/5803=72.9%+争用57s窗口63.7MB/s/39min avg19.2MB/s）
> 📦 唤醒358 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十五次采样：en_v1_4 18155/56461=32.1% 35/110+s36 200/512+85M obelics4225/5803=72.8%+争用106s窗口20.20MB/s/39min avg19.69MB/s）
> 📦 唤醒356 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十三次采样：en_v1_4 17669/56461=31.3% 35/110+s35 250/512+85M obelics4214/5803=72.6%+争用23.0MB/s 111s窗口+GPIC新下载PID3230354+40min avg=19.66MB/s）
> 📦 唤醒355 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十二次采样：en_v1_4 17479/56461=31.0% 35/110+s35 50/512+85M obelics4208/5803=72.5%+争用13.0MB/s 160s窗口(85M临时速降2.52MB/s)+40min avg=21.7MB/s）
> 📦 唤醒354 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十一次采样：en_v1_4 17184/56461=30.4% 34/110+85M obelics4203/5803=72.4%+争用21.9MB/s 159s窗口+两路均分带宽）
> 📦 唤醒353 原文已归档 → `daily-memories-data/2026-10-12.md`（含第五十次采样：en_v1_4 16936/56461=30.0% 34/110+85M obelics4197/5803=72.3%+争用24.8MB/s 60s窗口+无ReadTimeout）
> 📦 唤醒352 原文已归档 → `daily-memories-data/2026-10-12.md`（含第四十九次采样：en_v1_4 16674/56461=29.5% 33/110+85M obelics4195/5803=72.3%+争用28.2MB/s 89s avg+无ReadTimeout）
> 📦 唤醒351 原文已归档 → `daily-memories-data/2026-10-12.md`（含第四十八次采样：en_v1_4 16399/56461=29.0% 33/110+85M obelics4192/5803=72.2%+争用19.5MB/s 41min avg+两路均遇huggingface.co ReadTimeoutError）

> 📦 唤醒350 原文已归档 → `daily-memories-data/2026-10-12.md`（含第四十七次采样：en_v1_4 16152/56461=28.6% 30/110+85M obelics4189/5803=72.2%+争用21.7MB/s 38min avg+proxy 503缓解）
> 📦 唤醒296-349 及更早流水指针已归档 → `daily-memories-data/2026-10-10.md` ~ `2026-10-12.md`（含并发下载巡检全链+R3分词+GPIC+BO R2+论文更新等，详见各日文件）

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