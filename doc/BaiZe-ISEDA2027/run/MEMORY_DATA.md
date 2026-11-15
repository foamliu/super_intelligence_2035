# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> 🔴 **用户令 2026-11-13a**：把 stack-v3-train **全量**（~3.546TB compressed / 8192 parquet，⚠️ 非 15.9TB——15.9TB 是未压缩 content size）下载到 `/nas_user/app.e0031982/datasets/`；已下载的 2TB（4600 parquet @ `/nas_inference`）搬过去不重下。执行顺序：①等分词主跑+rerun完成 ②rsync 2TB→/nas_user + 校验字节 ③hf download 全量剩余（自动跳已存在）④更新 DATA_MAPPING ⑤commit。纪律：nice19/max-workers2/不挤S1/不碰分词产物。

> 🔴 **用户令 2026-11-13b**：把第一批 2TB 的**分词数据**（926GB @ `/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/`）也搬到 `/nas_user`；等全量下载完成后**立即分词新 shard**（已分词的 4600 跳过）。执行顺序：①rsync 926GB→/nas_user+校验+删源 ②等 hf download 完成 ③分词脚本改 PARQUET_DIR/OUTPUT_DIR 指向 /nas_user ④只分词新 shard（part-04600+）⑤更新 DATA_MAPPING ⑥commit。纪律：nice19/ionice3/不挤S1/跳过已有.json。

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ vision图文对调研报告DONE（唤醒1448,2026-11-11）**：用户令11-11→归因(10-13下载4路69.6M对未用=格式不兼容parquet/tar+无人接管线+实验设计限制)+平台盘点(中文9源/多语言2源/领域7源/已在盘7源)+推荐Top5(InternVL-SA1B零成本/TaiSu最佳中文/WebMix-38M规模/LAION-Chinese商用/PlotQA领域)+许可合规+下一步建议→report_vision_textpair_sourcing_zh.html(28321B/6节/0外链/HTML valid)落reports/→commit data rpt: pushed。

> 🟢 **✅ stack-v3-train 2TB下载全DONE（唤醒1422,03:56）**：batch7 FINISH@03:46:06→4600parquet/1,987,930,402,327B(1.85TiB)/0inc；2TB ROI复盘:token~2,025B/重叠2.4%/97.6%独特/ROI判定✅有价值→停止下载进入过滤+分词。

> 🟢 **✅ stack-v3-train 分词全DONE（唤醒1478,2026-11-13 10:1x）**：主跑4600/4600shard完成(47068s/173M docs/245.8B tok/279ERR);rerun 40shard完成(4492s/3.4B tok/0ERR);二次rerun确认40shard全SKIP(已有tokenized);tokenized输出926GB@/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/;无tokenize进程在跑→分词完全结束。

> 🟢 **✅ EDA脚本价值分析DONE（唤醒1468,2026-11-12 23:5x）**：用户令11-12→Phase A全扫4600shard(97M repos/1.28B files/5.86TiB/vendor1.3%/4963s)+Phase B分层抽样3200文件(9类)→V1=18/V2=149/V3=3033→外推V1~828文件/~0.01B token→Tcl唯一显著EDA命中(39.2%)/SKILL未检出/PyAether 0命中→报告report_data_stackv3_eda_script_value_zh.html(43KB/8节+附录/0外链/0script)落reports/→DATA_MAPPING.md§H.13新增→commit data eda:。
> 📝 **结论**：V1(直接可用)~828文件/~0.01B tok, V2(可挖掘)~6854文件/~0.04B tok, V3(低价值)~139518文件；报告路径reports/report_data_stackv3_eda_script_value_zh.html；建议：stack-v3对EDA脚本直接贡献有限，SKILL/PyAether需外部数据源。

> [11-14 22:4x] 唤醒1513：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~14859s≈4.1h),4908/8192processed(59.9%);SKIP phase COMPLETE(4488SKIP shards0-4599 ended@elapsed7256s);new shard phase RUNNING(309 new OK shards4600+,rate~24.6s/shard wall time);0ERR in current run(17 BrokenPipeError lines in log are from previous crash,already fixed);0 zero-byte .bin;no failed_shards.txt;.json=4906/.bin=4912/.idx=4905/du=1.1T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤⚠️脚本ETA误导：script ETA~9942s≈2.76h(averages fast SKIP+slow new),real ETA=3284remaining×24.6s≈80786s≈22.4h;⑥源清理确认:/nas_train tokenized=已删,/nas_inference parquet=已删;⑦下一步：等新shard分词全部完成(real ETA~22h)→StepD校验du+find.json+failed_shards.txt→更新DATA_MAPPING→commit
> [11-15 00:09] 唤醒1514：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~17470s≈4.85h),5018/8192processed(61.3%);SKIP phase COMPLETE(4488SKIP shards0-4599);new shard phase RUNNING(530 new OK shards4600+);rate~21-24s/shard wall time(8workers);0ERR;0 zero-byte .bin;no failed_shards.txt;.json=5019/.bin=5025/.idx=5018/du=1.1T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~11042s≈3.1h(misleading,averages fast SKIP+slow new),real ETA=3174remaining×~23s≈73000s≈20.3h→预计~2026-11-15 20:30CST完成;⑥源清理确认:/nas_train tokenized=已删,/nas_inference parquet=已删;⑦research日报11-15 data建议="建立每千条成本+每美元胜率两列,替代按条数排序;对偏好数据源做交叉一致性检查"(记为future work,不阻塞当前);⑧pretrain训练在.12上跑(torchrun可见)→nice19/ionice3正确;⑨下一步：等新shard分词全部完成(real ETA~20h)→StepD校验du+find.json+failed_shards.txt→更新DATA_MAPPING→commit
> [11-15 00:56] 唤醒1515：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~20264s≈5.6h),5129/8192processed(62.6%);SKIP phase COMPLETE(4600SKIP shards0-4599);new shard phase RUNNING(529 new OK shards4600+,rate~24.6s/shard wall time);0ERR;0 zero-byte .bin;no failed_shards.txt;.json=5129/.bin=5135/.idx=5128/du=1.1T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~12093s≈3.4h(misleading,averages fast SKIP+slow new),real ETA=3063remaining new shards×~24.6s≈75350s≈20.9h→预计~2026-11-15 22:00CST完成;⑥源清理确认:/nas_train tokenized=已删,/nas_inference parquet=已删;⑦pretrain训练在.12上跑(torchrun可见,nice0)→分词nice19/ionice3正确不挤;⑧下一步：等新shard分词全部完成(real ETA~21h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 01:51] 唤醒1516：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~23676s≈6.6h),5268/8192processed(64.3%);SKIP phase COMPLETE(4600SKIP shards0-4599);new shard phase RUNNING(668 new OK shards4600+);rate~24.5s/shard wall time(8workers);0ERR;0 zero-byte .bin;no failed_shards.txt;.json=5266/.bin=5272/.idx=5265/du=1.2T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~13141s≈3.6h(misleading,averages fast SKIP+slow new),real ETA=2924remaining×~24.5s≈71638s≈19.9h→预计~2026-11-15 22:00CST完成;⑥源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑦research日报11-15 data建议已记为future work(不阻塞);⑧下一步：等新shard分词全部完成(real ETA~20h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 02:48] 唤醒1517：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~26997s≈7.5h),5414/8192processed(66.1%);SKIP phase COMPLETE(4600SKIP shards0-4599);new shard phase RUNNING(814 new OK shards4600+);rate~24.6s/shard wall time(8workers);0ERR in current run(8 BrokenPipeError lines in log from previous crash,already fixed);0 zero-byte .bin;no failed_shards.txt;.json=5415/.bin=5421/.idx=5414/du=1.2T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~13850s≈3.85h(misleading,averages fast SKIP+slow new),real ETA=2778remaining×~24.6s≈68339s≈19.0h→预计~2026-11-15 22:00CST完成;⑥源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑦research日报11-15 data建议=\"建立每千条成本+每美元胜率两列\"+\"对偏好数据源做交叉一致性检查\"(同11-14,已记为future work,不阻塞);⑧loop健康(baize_data_loop PID1943222 alive,cline in PATH✅);git up-to-date with origin✅;⑨下一步：等新shard分词全部完成(real ETA~19h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 07:27] 唤醒1518：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~43677s≈12.1h),6124/8192processed(74.8%);SKIP phase COMPLETE(4600SKIP shards0-4599);new shard phase RUNNING(1524 new OK shards4600+);rate~23.9s/shard wall time(8workers,new phase only:36421s/1524=23.9s);0ERR in current run(8 BrokenPipeError lines in log from previous crash,already fixed);0 zero-byte .bin;no failed_shards.txt;.json=6125/.bin=6131/.idx=6124/du=1.4T;MANIFEST.json exists(822KB);④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~14749s≈4.1h(misleading,averages fast SKIP+slow new),real ETA=2068remaining×~23.9s≈49425s≈13.7h→预计~2026-11-15 21:00CST完成;⑥源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑦log末行=[6124/8192]shard=6123 OK tokens=40779822 elapsed=43677s ETA=14749s→运行正常;⑧下一步：等新shard分词全部完成(real ETA~14h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 03:45] 唤醒1518：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~30464s≈8.5h),5569/8192processed(68.0%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(969 new OK shards4600+,rate~22.1s/shard wall);0ERR in current run;0 zero-byte .bin(transient earlier,now clean);no failed_shards.txt;.json=5569(excl MANIFEST)/.bin=5576/.idx=5569/du=1.2T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~14341s≈4.0h(misleading,averages fast SKIP+slow new),real ETA=2623remaining×~22.1s≈57968s≈16.1h→预计~2026-11-15 19:50CST完成;⑥源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑦research日报11-15 data建议已记为future work(不阻塞);⑧pretrain训练在.12上跑(torchrun可见)→nice19/ionice3正确;⑨下一步：等新shard分词全部完成(real ETA~16h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 08:2x] 唤醒1519：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~47111s≈13.1h),6266/8192processed(76.5%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(1666 new OK shards4600+,rate~22.4s/shard wall);0ERR in current run(9 Traceback lines in log are from previous crash,already fixed);no failed_shards.txt;.json=6267/.bin=6273/.idx=6268/du=1.4T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~14472s≈4.0h(misleading,averages fast SKIP+slow new),real ETA=1926remaining×~22.4s≈43142s≈12.0h→预计~2026-11-15 20:30CST完成;⑥源清理确认:/nas_train tokenized=已删✅,/nas_inference parquet=已删✅;⑦下一步：等新shard分词全部完成(real ETA~12h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> 📦 唤醒1493-1512 原文已归档 → daily-memories-data/2026-11-14.md（StepB下载完成+StepC分词启动+16w崩溃修复(→8w)+SKIP phase巡检×20轮,详见日文件）
> 📦 唤醒1490-1492 原文已归档 → daily-memories-data/2026-11-13.md（StepB下载进度巡检+StepC auto-wait修复重启×3轮,详见日文件）
> ⚠️ [11-14 19:2x] 运维介入修复记录：StepC 16workers在shard5350处BrokenPipeError崩溃(OOM→Pool pipe断裂→NFS写入未flush→989新shard输出丢失)→修复:fsync+maxtasksperchild50+BrokenPipeError异常处理+workers 16→8→PID1677655重启,nice19/ionice3,日志/tmp/tokenize_stackv3_new.log

> 📦 唤醒1489 原文已归档 → daily-memories-data/2026-11-13.md（ETA审计完成+StepC护栏修复+任务书归档,详见日文件）
> 📦 唤醒1487-1488 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检×2轮,旧ETA~3.3h已被本轮纠正,详见日文件）
> 📦 唤醒1483-1486 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检+StepC launch启动,共4轮,详见日文件）
> 📦 唤醒1471-1482 原文已归档 → daily-memories-data/2026-11-13.md（分词完成+全量下载启动+rsync 2TB+源删除+hf download全量+用户令11-13b启动,共12轮,详见日文件）

> 📦 迁移完成块(运维令13:3x+SFT/Agent分词+5源+4源+3稳定源+ufw_en,共9源705shard~8.3TB→/nas_env)已归档 → daily-memories-data/2026-11-13.md；结论见DATA_MAPPING.md

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        用户令2026-11-15 IFM数学/代码下载+5agent评估+调研 → StepC tokenizing 89% → P0 Toucan DONE ✅ → P0 AgentTrove 79% downloading → MegaMath batch1 DONE ✅ → neulab 15子集 DONE ✅ → IFM Math+Code-Reasoning downloading (locks cleaned) → WAITING=0
已完成:       ✅分词全DONE(4600shard);✅EDA分析DONE;✅2TB下载DONE;✅2TB ROI复盘;✅vision图文对调研报告;✅StepA/B DONE;✅StepC SKIP phase(4600);✅5agent datasets HfApi探测全DONE;✅3 IFM datasets HfApi探测全DONE;✅adp_subset_plan.md(15/22下~85GB);✅agent-data-protocol clone DONE;✅DATA_MAPPING.md D1-D4节写入;✅调研报告report_data_math_code_datasets_survey_zh.html(17KB)生成;✅IFM/MegaMath≡LLM360/MegaMath SHA级验证(同一份);✅污染检查结论写入DATA_MAPPING D3;✅Toucan下载DONE(409文件/21GB/4子集);✅neulab 15非重叠子集DONE(79GB/0 inc);✅MegaMath batch1 DONE(5子集/252 parquet/216GB/0 inc);✅P3 freeinference转告harness线
当前动作:     ①StepC RUNNING:PID1677655(8workers,nice19/ionice3),7274/8192(88.8%),ETA~2.5h,0ERR;②AgentTrove下载RUNNING(PID32820,30/38parquet=79%,1incomplete,ETA~1h);③Math-Reasoning下载RUNNING(PID1829139,203files/155GB/2228total=3.5%,cleaned 30 stale locks);④Code-Reasoning下载RUNNING(PID3194782,23files/12GB/1637total=0.4%,cleaned 4 stale locks);⑤磁盘/nas_user 113T总/52T可用→✅
下一步:       ①等StepC分词完成(ETA~2.5h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit;②等AgentTrove完成(ETA~1h)→逐题污染检查SWE-bench重叠;③等IFM Math/Code-Reasoning完成(ETA数天,体量大)→更新DATA_MAPPING;④MegaMath batch2(megamath-web~1TB)按需决定;⑤所有下载完成后做逐题污染检查
阻塞:         无(WAITING=0短睡巡检,所有下载nice19/ionice3/max-workers2不挤S1;stale locks已清理)
ERROR_COUNT:  0(当前run 0ERR;本轮清理30+4 stale locks)
未完成指令:   有(StepC分词RUNNING+AgentTrove下载+IFM Math/Code-Reasoning下载+StepD校验+AgentTrove污染检查待完成)→WAITING=0
```

> [11-15 12:0x] 唤醒1521：巡检→①StepC RUNNING:PID1677655(8workers,nice19/ionice3),6827/8192(83.3%),.json~6828,ETA~3.3h,0ERR;②P0 Toucan DONE✅(409文件/21GB/0 inc/4子集:Kimi-K2 6.0G+OSS 7.6G+Qwen3 6.4G+SFT 406M);③P0 AgentTrove下载RUNNING(PID32820,50files/6.0GB,2 cache incomplete,nice19/max-workers2);④neulab 15非重叠子集ALL DONE✅(79GB/0 inc/16子目录:code_feedback 2.8G+codeactinstruct 314M+mind2web 9.3G+nnetnav-live 6.3G+nnetnav-wa 3.6G+go-browse-wa 35G+synatra 4.5G+mini-coder 17G+openhands 405M+swe-play-trajectories 563M+agenttuning_×6 ~76M);⑤MegaMath batch1 DONE✅(5子集全部0 inc:megamath-web-pro 100p+megamath-code 16p+megamath-qa 32p+megamath-text-code-block 88p+megamath-translated-code 16p=252p/153GB);⑥IFM Math-Reasoning下载RUNNING(PID1829139,9.2GB,23files);⑦IFM Code-Reasoning下载启动(PID3194782,刚启动);⑧磁盘/nas_user 113T总/53T可用→✅;⑨ADP转换脚本已clone✅;⑩调研报告17KB已生成✅;⑪DATA_MAPPING D1-D4已更新(MegaMath batch1✅/neulab✅/Math+Code-Reasoning🔄);⑫下一步:等StepC完成→StepD校验;等AgentTrove完成→污染检查;等IFM三集完成→更新DATA_MAPPING

> [11-15 15:0x] 唤醒1523：巡检→①StepC RUNNING:PID1677655(8workers,nice19/ionice3),7274/8192(88.8%),.json=7274/.bin=7281/.idx=7274/du=1.6T,ETA~2.5h(8874s),0ERR,failed_shards.txt不存在(good);②AgentTrove下载RUNNING(PID32820,30/38parquet=79%,1incomplete,ETA~1h);③Math-Reasoning下载RUNNING(PID1829139,203files/155GB/2228total=3.5%,cleaned 30 stale .lock files);④Code-Reasoning下载RUNNING(PID3194782,23files/12GB/1637total=0.4%,cleaned 4 stale .lock files);⑤Toucan DONE✅(409文件/21GB);⑥neulab DONE✅(79GB/15子集);⑦MegaMath batch1 DONE✅(216GB/5子集);⑧磁盘/nas_user 113T总/52T可用→✅;⑨pretrain训练在.12跑(torchrun可见)→nice19/ionice3正确;⑩下一步:等StepC完成→StepD;等AgentTrove完成→污染检查;等IFM下载完成→更新DATA_MAPPING

> [11-15 14:0x] 唤醒1522(运维介入巡检+清理)：①HfApi全8repo复核DONE(实测元数据：orca-agentinstruct 22files/2.38GB/cdla-permissive;Toucan 136files/21.81GB/apache-2.0;AgentTrove 40files/19.55GB/apache-2.0;neulab 130files/498.66GB/license未标;freeinference 217files/8.93GB/cc-by-4.0;MegaMath 5317files/1118GB/odc-by;Math-Reasoning 2228files/4462GB/apache-2.0;Code-Reasoning 1637files/3277GB/apache-2.0)；②🔴发现重复进程：Math-Reasoning有3个hf download进程(PID1327150+1375641+1829139)→kill 2个保留最老PID1829139;Code-Reasoning有3个(PID3194782+3823814+3823825)→kill 2个保留最老PID3194782；③🔴发现stale .lock文件阻塞下载：Math-Reasoning 60个.lock+Code-Reasoning 8个.lock→全部删除；④清理后验证：Math-Reasoning文件数5s内121→122确认下载恢复;AgentTrove 27/40files(68%)继续;⑤StepC RUNNING:7150/8192(87.3%),ETA~2.7h,0ERR;⑥P3 freeinference转告harness线→已记入MEMORY(14种harness含claude-code/267账户/16周真实workload/1.19M请求/1.21M工具调用,无消息文本不能训练,可用于harness线workload特征分析+性能建模);⑦调研报告26KB完整(Top-5推荐+总表27数据集+缺口分析+HfApi实测证据+污染风险表+内联SVG);⑧磁盘/nas_user 113T总/52T可用→✅;⑨下一步:等StepC完成→StepD校验;等AgentTrove完成→逐题污染检查;等IFM下载完成→更新DATA_MAPPING

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> 📦 唤醒1473-1478 原文已归档 → daily-memories-data/2026-11-13.md（分词DONE确认+全量下载启动+脚本v4修复+EDA分析交付,共6轮,详见日文件）
> 📦 唤醒1457-1465 原文已归档 → daily-memories-data/2026-11-12.md~2026-11-13.md（例行巡检×9轮,stack-v3-train稳定1.9T,无新data令,详见日文件）
> 📦 唤醒1458 原文已归档 → daily-memories-data/2026-11-13.md（例行巡检,无新data令,详见日文件）
> 📦 唤醒1410-1420 原文已归档 → daily-memories-data/2026-11-13.md（batch6-7进度巡检×11轮,batch6完成1.813TB+batch7启动,2TB预算92.4%,详见日文件）
> 📦 唤醒1444-1456 原文已归档 → daily-memories-data/2026-11-11.md~2026-11-12.md（例行巡检+vision图文对调研报告交付,共13轮,详见日文件）
> 📦 唤醒1425-1440 原文已归档 → daily-memories-data/2026-11-10.md（例行巡检+staleness审计+论文数据节更新+TASK.md标记更新,共16轮,详见日文件）
> 📦 唤醒1422-1424 原文已归档 → daily-memories-data/2026-11-10.md（batch7完成+QC+2TB ROI复盘+例行巡检,共3轮,详见日文件）
> 📦 唤醒1385 原文已归档 → daily-memories-data/2026-11-13.md（11-07运维令执行:代码语料放行ROI下载,详见日文件）
> 📦 唤醒1374-1384 原文已归档 → daily-memories-data/2026-11-07.md（例行空唤醒巡检,共11轮,详见日文件）
> 📦 唤醒1346-1373 原文已归档 → daily-memories-data/2026-11-06.md~2026-11-07.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1319-1345 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共27轮,详见日文件）
> 📦 唤醒1283-1318 原文已归档 → daily-memories-data/2026-11-06.md（例行空唤醒巡检,共36轮,详见日文件）
> 📦 唤醒1282-1241 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共42轮,详见日文件）
> 📦 唤醒1240-1213 原文已归档 → daily-memories-data/2026-11-05.md（例行空唤醒巡检,共28轮,详见日文件）
> 📦 唤醒1180-1212 原文已归档 → daily-memories-data/2026-11-04.md（例行空唤醒巡检+09:2x下载巡检+09:4x报告复核,共33轮,详见日文件）
> 📦 唤醒1161-1179 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检+09:2x下载巡检,共19轮,详见日文件）
> 📦 唤醒1117-1160 原文已归档 → daily-memories-data/2026-11-04.md（运维令10-31交付物v6例行复核+85M下载进度巡检,共44轮,详见日文件）
> 📦 唤醒1107-1116 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v5例行复核+85M下载进度巡检+HF链接真实性抽检7个数据集HTTP 200全PASS,共10轮,详见日文件）

> 📦 唤醒1065-1106 原文已归档 → daily-memories-data/2026-11-03.md（运维令10-31交付物v4-v5例行复核+85M下载进度巡检,共42轮,详见日文件）
> 📦 唤醒1030-1063 原文已归档 → daily-memories-data/2026-10-31.md（运维令10-31报告v3-v4复核+85M下载进度巡检,详见日文件）
> 📦 唤醒833-1023 原文已归档 → daily-memories-data/2026-10-30.md ~ 2026-10-31.md（例行巡检+85M字节增长复核,详见日文件）
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
## �