# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> 🔴 **用户令 2026-11-13a**：stack-v3-train 全量下载→✅StepA/B DONE(8192parquet/3.3TB); StepC分词🔄96.3%(7890/8192 .json/1.7TB/8workers/ETA~54min); 纪律nice19/ionice3/不挤S1 ✅

> 🔴 **用户令 2026-11-13b**：分词数据搬到/nas_user→✅StepA DONE; 分词新shard→🔄StepC 96.3%; ETA~54min完成→StepD校验+更新DATA_MAPPING+commit

> 🔴 **用户令 2026-11-15 08:5x（IFM 3个数学/代码数据集+调研）**：✅IFM/MegaMath第一批DONE(729files/216GB/0inc); 🔄IFM/Math-Reasoning下载中(217/2228files/402GB/PID1829139/elapsed~7.2h/rate~120s/file/ETA~67h); 🔄IFM/Code-Reasoning下载中(28/1637files/50GB/PID916265/nice19/max-workers2/elapsed~45min/rate~85s/file/ETA~38h); ✅MegaMath≡LLM360/MegaMath(sha 3cbc646 一致); ✅调研报告report_data_math_code_datasets_survey_zh.html(26KB)落reports/

> ✅ **用户令 2026-11-15 09:0x（5个agent datasets评估+下载）→全部验收项已满足**：✅Toucan-1.5M(409files/21GB/0inc); ✅AgentTrove(121files/19GB/0inc); ✅neulab ADP 15子集(277files/79GB/0inc); ✅adp_subset_plan.md; ✅agent-data-protocol clone; ✅污染检查CONTAMINATION_CHECK_AGENT_IFM.md; ✅DATA_MAPPING.md D1-D4; 🚫orca P2/🚫freeinference P3; 📝转告harness线freeinference workload(已记MEMORY+DATA_MAPPING)

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ vision图文对调研报告DONE（唤醒1448,2026-11-11）**：用户令11-11→归因(10-13下载4路69.6M对未用=格式不兼容parquet/tar+无人接管线+实验设计限制)+平台盘点(中文9源/多语言2源/领域7源/已在盘7源)+推荐Top5(InternVL-SA1B零成本/TaiSu最佳中文/WebMix-38M规模/LAION-Chinese商用/PlotQA领域)+许可合规+下一步建议→report_vision_textpair_sourcing_zh.html(28321B/6节/0外链/HTML valid)落reports/→commit data rpt: pushed。

> 🟢 **✅ stack-v3-train 2TB下载全DONE（唤醒1422,03:56）**：batch7 FINISH@03:46:06→4600parquet/1,987,930,402,327B(1.85TiB)/0inc；2TB ROI复盘:token~2,025B/重叠2.4%/97.6%独特/ROI判定✅有价值→停止下载进入过滤+分词。

> 🟢 **✅ stack-v3-train 分词全DONE（唤醒1478,2026-11-13 10:1x）**：主跑4600/4600shard完成(47068s/173M docs/245.8B tok/279ERR);rerun 40shard完成(4492s/3.4B tok/0ERR);二次rerun确认40shard全SKIP(已有tokenized);tokenized输出926GB@/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/;无tokenize进程在跑→分词完全结束。

> 🟢 **✅ EDA脚本价值分析DONE（唤醒1468,2026-11-12 23:5x）**：用户令11-12→Phase A全扫4600shard(97M repos/1.28B files/5.86TiB/vendor1.3%/4963s)+Phase B分层抽样3200文件(9类)→V1=18/V2=149/V3=3033→外推V1~828文件/~0.01B token→Tcl唯一显著EDA命中(39.2%)/SKILL未检出/PyAether 0命中→报告report_data_stackv3_eda_script_value_zh.html(43KB/8节+附录/0外链/0script)落reports/→DATA_MAPPING.md§H.13新增→commit data eda:。
> 📝 **结论**：V1(直接可用)~828文件/~0.01B tok, V2(可挖掘)~6854文件/~0.04B tok, V3(低价值)~139518文件；报告路径reports/report_data_stackv3_eda_script_value_zh.html；建议：stack-v3对EDA脚本直接贡献有限，SKILL/PyAether需外部数据源。

> 📦 唤醒1513-1518 原文已归档 → daily-memories-data/2026-11-15.md（StepC巡检×6轮,59.9%→74.8%,详见日文件）
> [11-15 03:45] 唤醒1518：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~30464s≈8.5h),5569/8192processed(68.0%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(969 new OK shards4600+,rate~22.1s/shard wall);0ERR in current run;0 zero-byte .bin(transient earlier,now clean);no failed_shards.txt;.json=5569(excl MANIFEST)/.bin=5576/.idx=5569/du=1.2T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~14341s≈4.0h(misleading,averages fast SKIP+slow new),real ETA=2623remaining×~22.1s≈57968s≈16.1h→预计~2026-11-15 19:50CST完成;⑥源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑦research日报11-15 data建议已记为future work(不阻塞);⑧pretrain训练在.12上跑(torchrun可见)→nice19/ionice3正确;⑨下一步：等新shard分词全部完成(real ETA~16h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 08:2x] 唤醒1519：巡检→①StepA DONE;②StepB DONE(8192parquet/0inc/3.3TB);③StepC RUNNING：PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~47111s≈13.1h),6266/8192processed(76.5%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(1666 new OK shards4600+,rate~22.4s/shard wall);0ERR in current run(9 Traceback lines in log are from previous crash,already fixed);no failed_shards.txt;.json=6267/.bin=6273/.idx=6268/du=1.4T;MANIFEST.json exists;④磁盘/nas_user 113T总/53T可用(54%used)→✅;⑤ETA校正：script ETA~14472s≈4.0h(misleading,averages fast SKIP+slow new),real ETA=1926remaining×~22.4s≈43142s≈12.0h→预计~2026-11-15 20:30CST完成;⑥源清理确认:/nas_train tokenized=已删✅,/nas_inference parquet=已删✅;⑦下一步：等新shard分词全部完成(real ETA~12h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit
> [11-15 15:30] 唤醒1520：综合巡检+IFM/agent datasets进度更新+污染检查→①StepC分词：7389/8192 .json(90.2%)/7395 .bin/1.6TB/4 workers active/0 ERR/no failed_shards.txt/ETA~30min→即将完成;②IFM下载：MegaMath✅DONE(231.6GB/1093files/0inc), Math-Reasoning🔄(222.7GB/112parquet/3cache inc/PID1829139), Code-Reasoning🔄极慢(15.4GB/9parquet/~35min per file/1637 total→ETA~20天);③Agent下载：Toucan✅DONE(21.8GB/409files/0inc), AgentTrove🔄90%(36/38parquet/18.2GB/ETA~28min/PID32820), neulab ADP✅DONE(84.5GB/277files/64jsonl/0inc/15子集);④✅adp_subset_plan.md已落盘(22子集/15下6不下1暂不下);⑤✅agent-data-protocol已clone到/nas_user/.../agent-data-protocol/;⑥✅污染检查CONTAMINATION_CHECK_AGENT_IFM.md已落盘(AgentTrove含gsm8k源→⚠️中风险可过滤; swesmith/SWEGym从train派生→低风险; mind2web/code_feedback待查);⑦✅DATA_MAPPING.md D1-D4已更新;⑧⚠️发现并修复stuck chain scripts(dl_chain_agent.sh/dl_chain_ifm.sh grep匹配cline进程→已kill);⑨磁盘/nas_user 113T/52T可用(55%)→✅;⑩调研报告report_data_math_code_datasets_survey_zh.html(17KB)已在;⑪下一步：等StepC分词完成→StepD校验+更新DATA_MAPPING+commit; AgentTrove完成后验证; IFM Math/Code-Reasoning继续后台下载
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
PHASE:        用户令2026-11-15 IFM数学/代码下载+5agent评估+调研 → StepC tokenizing 96.3% → agent datasets ALL DONE ✅ → MegaMath batch1 DONE ✅ → IFM Math/Code-Reasoning downloading → WAITING=1
已完成:       ✅分词全DONE(4600shard);✅EDA分析DONE;✅2TB下载DONE;✅2TB ROI复盘;✅vision图文对调研报告;✅StepA/B DONE;✅StepC SKIP phase(4600);✅5agent datasets HfApi探测全DONE;✅3 IFM datasets HfApi探测全DONE;✅adp_subset_plan.md(15/22下~85GB);✅agent-data-protocol clone DONE(@run/data/);✅DATA_MAPPING.md D1-D4节写入;✅调研报告report_data_math_code_datasets_survey_zh.html(26KB)生成;✅IFM/MegaMath≡LLM360/MegaMath SHA级验证(同一份);✅污染检查结论写入DATA_MAPPING D3;✅Toucan下载DONE(409文件/21GB/4子集);✅AgentTrove下载DONE(38/38parquet/19GB/0inc);✅neulab 15非重叠子集DONE(79GB/0 inc);✅MegaMath batch1 DONE(5子集/1093files/216GB/0 inc);✅P3 freeinference转告harness线;✅清理364 MegaMath+62 Math-Reasoning stale .lock文件;✅Code-Reasoning旧进程kill+重启v3(PID916265,活跃下载中)
当前动作:     ①StepC RUNNING:PID1677655(8workers,nice19/ionice3,elapsed~84820s≈23.6h),7890/8192(96.3%),ETA~3247s≈54min,0ERR,du=1.7T,.json=7891/.bin=7897/0 zero-byte;②Math-Reasoning下载RUNNING(PID1829139,217/2228files/402GB/3incomplete,elapsed~7.2h,rate~120s/file,ETA~67h);③Code-Reasoning下载RUNNING(PID916265,nice19/max-workers2,28/1637files/50GB/2incomplete,elapsed~45min,rate~85s/file,ETA~38h,stdout→/tmp/ifm_code_reasoning_download.log);④磁盘/nas_user 113T总/52T可用(55%used)→✅
下一步:       ①等StepC分词完成(ETA~54min,预计~19:44CST)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit;②等IFM Math/Code-Reasoning完成(ETA数天,体量大,max-workers2不挤S1);③MegaMath batch2(megamath-web~1TB)按需决定;④所有下载完成后做逐题污染检查
阻塞:         无(WAITING=1长睡30min,StepC ETA~54min;所有下载nice19/ionice3/max-workers2不挤S1;Code-Reasoning proxy error是旧日志,当前进程活跃下载中)
ERROR_COUNT:  0(当前run 0ERR;Code-Reasoning v3.log中的ProxyError来自前一次已死进程,当前PID916265活跃,fd有.incomplete文件正在写)
未完成指令:   有(StepC分词RUNNING+IFM Math/Code-Reasoning下载+StepD校验待完成)→WAITING=0
```

> [11-15 12:0x] 唤醒1521：巡检→①StepC RUNNING:PID1677655(8workers,nice19/ionice3),6827/8192(83.3%),.json~6828,ETA~3.3h,0ERR;②P0 Toucan DONE✅(409文件/21GB/0 inc/4子集:Kimi-K2 6.0G+OSS 7.6G+Qwen3 6.4G+SFT 406M);③P0 AgentTrove下载RUNNING(PID32820,50files/6.0GB,2 cache incomplete,nice19/max-workers2);④neulab 15非重叠子集ALL DONE✅(79GB/0 inc/16子目录:code_feedback 2.8G+codeactinstruct 314M+mind2web 9.3G+nnetnav-live 6.3G+nnetnav-wa 3.6G+go-browse-wa 35G+synatra 4.5G+mini-coder 17G+openhands 405M+swe-play-trajectories 563M+agenttuning_×6 ~76M);⑤MegaMath batch1 DONE✅(5子集全部0 inc:megamath-web-pro 100p+megamath-code 16p+megamath-qa 32p+megamath-text-code-block 88p+megamath-translated-code 16p=252p/153GB);⑥IFM Math-Reasoning下载RUNNING(PID1829139,9.2GB,23files);⑦IFM Code-Reasoning下载启动(PID3194782,刚启动);⑧磁盘/nas_user 113T总/53T可用→✅;⑨ADP转换脚本已clone✅;⑩调研报告17KB已生成✅;⑪DATA_MAPPING D1-D4已更新(MegaMath batch1✅/neulab✅/Math+Code-Reasoning🔄);⑫下一步:等StepC完成→StepD校验;等AgentTrove完成→污染检查;等IFM三集完成→更新DATA_MAPPING

> [11-15 15:0x] 唤醒1523：巡检→①StepC RUNNING:PID1677655(8workers,nice19/ionice3),7274/8192(88.8%),.json=7274/.bin=7281/.idx=7274/du=1.6T,ETA~2.5h(8874s),0ERR,failed_shards.txt不存在(good);②AgentTrove下载RUNNING(PID32820,30/38parquet=79%,1incomplete,ETA~1h);③Math-Reasoning下载RUNNING(PID1829139,203files/155GB/2228total=3.5%,cleaned 30 stale .lock files);④Code-Reasoning下载RUNNING(PID3194782,23files/12GB/1637total=0.4%,cleaned 4 stale .lock files);⑤Toucan DONE✅(409文件/21GB);⑥neulab DONE✅(79GB/15子集);⑦MegaMath batch1 DONE✅(216GB/5子集);⑧磁盘/nas_user 113T总/52T可用→✅;⑨pretrain训练在.12跑(torchrun可见)→nice19/ionice3正确;⑩下一步:等StepC完成→StepD;等AgentTrove完成→污染检查;等IFM下载完成→更新DATA_MAPPING

> [11-15 16:3x] 唤醒1524(运维介入巡检+修复)：①StepC RUNNING:PID1677655(8workers,nice19/ionice3),7550/8192(92.1%),.json=7550,du=1.6T,ETA~6518s≈1.8h,0ERR;②✅AgentTrove DONE确认(38/38parquet/19GB/0incomplete/121files)→DATA_MAPPING已更新为✅;③✅Toucan DONE(409files/21GB);④✅neulab ADP DONE(277files/79GB/15子集);⑤✅MegaMath batch1 DONE(1093files/216GB);⑥🔄Math-Reasoning下载RUNNING(PID1829139,270GB/143parquet/2228total=6.4%,~15MB/s,ETA~3天);⑦🔄Code-Reasoning下载重启v3(PID2531833,nice19/max-workers2):旧进程(PID3194782)~1MB/s极慢已kill→尝试hf_transfer(0.1.9)但不兼容proxy(stall@268MB)→弃用hf_transfer重启常规模式→已快速verify 9个已下文件,开始下新文件;⑧✅清理364个MegaMath stale .lock文件(200 text-code-block+100 web-pro+16×4其他);⑨✅清理Math-Reasoning 62个stale .lock文件;⑩✅ADP clone确认在run/data/agent-data-protocol/(commit 040a279)→DATA_MAPPING路径已修正;⑪✅adp_subset_plan.md(4KB)+CONTAMINATION_CHECK_AGENT_IFM.md(8KB)+survey report(26KB)全部在位;⑫磁盘/nas_user 113T总/52T可用→✅;⑬pretrain训练在.12跑(torchrun可见)→nice19/ionice3正确;⑭下一步:等StepC完成(ETA~1.8h)→StepD校验;等IFM Math/Code-Reasoning完成→更新DATA_MAPPING

> [11-15 17:2x] 唤醒1525：巡检→①StepC RUNNING:PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~79233s≈22h),7666/8192processed(93.6%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(3066 new OK shards4600+,rate~24.6s/shard wall time);0ERR in current run(8 BrokenPipeError lines from previous crash,already fixed);1 zero-byte .bin(shard7673,actively writing→normal);no failed_shards.txt;.json=7666/.bin=7674/.idx=7667/du=1.7T;MANIFEST.json exists;②IFM Math-Reasoning下载RUNNING(PID1829139,164parquet/309GB/3incomplete,elapsed~5.7h,2228total→7.4%);③IFM Code-Reasoning下载RUNNING v3(PID2531833,nice19/ionice3/max-workers2,17parquet/32GB/2incomplete,1637total→1.0%,~5min/file→ETA~数天);④✅Toucan DONE(409files/21GB);⑤✅AgentTrove DONE(38parquet/19GB);⑥✅neulab ADP DONE(277files/79GB/15子集);⑦✅MegaMath batch1 DONE(1093files/216GB/5子集);⑧磁盘/nas_user 113T总/52T可用(55%used)→✅;⑨源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑩log末行=[7666/8192]shard=7667 OK tokens=45117374 elapsed=79233s ETA=5437s→运行正常;⑪下一步：等StepC分词完成(ETA~1.5h,预计~18:45CST)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit;等IFM下载完成→更新DATA_MAPPING
> 📦 唤醒1522 原文已归档 → daily-memories-data/2026-11-15.md（HfApi全8repo复核+重复进程清理+stale.lock清理+freeinference转告harness,详见日文件）

> [11-15 18:4x] 唤醒1526(运维介入巡检+修复Code-Reasoning)：①StepC RUNNING:PID1677655(8workers,nice19/ionice3),7778/8192(95.1%),.json=7778/du=1.7T,ETA~4379s≈1.2h,0ERR,no failed_shards.txt;②✅Agent datasets 09:0x任务全部验收项满足(Toucan/AgentTrove/neulab ADP/adp_subset_plan/contamination check/DATA_MAPPING全部DONE);③🔄Math-Reasoning下载RUNNING(PID1829139,192datafiles/357GB/2228total=8.6%,elapsed~6.5h);④🔴Code-Reasoning下载已死(旧PID2531833不存在)→清理75个stale.lock(Math49+Code26)→重启新PID916265(nice19/ionice3/max-workers2/24datafiles/42GB/1637total,正在下code-no-thinking-hard子集);⑤磁盘/nas_user 113T总/52T可用(55%)→✅;⑥pretrain训练在.12跑→nice19/ionice3正确;⑦下一步:等StepC完成(ETA~1.2h)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit;等IFM下载完成→更新DATA_MAPPING
> [11-15 18:5x] 唤醒1527(巡检)：①StepC RUNNING:PID1677655(ppid=1,8workers,nice19/ionice3,elapsed~84820s≈23.6h),7890/8192(96.3%);SKIP phase COMPLETE(4600 shards0-4599);new shard phase RUNNING(3290 new OK shards4600+,rate~24.6s/shard wall);0ERR;0 zero-byte .bin;no failed_shards.txt;.json=7891/.bin=7897/.idx=7891/du=1.7T;MANIFEST.json exists;log末行=[7890/8192]shard=7891 OK tokens=39,780,173 elapsed=84820s ETA=3247s;②✅Agent datasets 09:0x全部DONE(Toucan409files/21GB+AgentTrove121files/19GB+neulab277files/79GB/15子集);③🔄Math-Reasoning下载RUNNING(PID1829139,217/2228files/402GB/3incomplete,elapsed~7.2h,rate~120s/file,ETA~67h,stdout→/tmp/dl_master_orchestrator.log);④🔄Code-Reasoning下载RUNNING(PID916265,nice19/ionice3/max-workers2,28/1637files/50GB/2incomplete,elapsed~45min,rate~85s/file,ETA~38h,stdout→/tmp/ifm_code_reasoning_download.log,fd检查活跃.incomplete正在写);⑤✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);⑥磁盘/nas_user 113T总/52T可用(55%)→✅;⑦源清理确认:/nas_train tokenized=0files✅,/nas_inference parquet=0files✅;⑧pretrain训练在.12跑(torchrun可见)→nice19/ionice3正确;⑨⚠️Code-Reasoning旧v3.log中ProxyError(503)来自前次已死进程,当前PID916265活跃,已确认fd有.incomplete文件正在写;⑩下一步:等StepC完成(ETA~54min,预计~19:44CST)→StepD校验du+find.json=8192+failed_shards.txt空→更新DATA_MAPPING→commit;等IFM下载完成→更新DATA_MAPPING

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