# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> 🔴 **用户令 2026-11-13a**：stack-v3-train 全量下载→✅StepA/B DONE(8192parquet/3.3TB); StepC分词→✅全DONE(8192/8192/476B tok/1.8TB/0ERR/92041s); StepD校验→✅通过(0ERR/no failed_shards/0 zero-byte/MANIFEST✅); ✅源清理(/nas_train+/nas_inference=0files); DATA_MAPPING H.14已更新

> 🔴 **用户令 2026-11-13b**：分词数据搬到/nas_user→✅StepA DONE; 分词新shard→✅StepC全DONE(8192/8192/476B tok); StepD校验→✅通过→DATA_MAPPING更新→commit

> 🔴 **用户令 2026-11-15 08:5x（IFM 3个数学/代码数据集+调研）**：✅IFM/MegaMath第一批DONE(364parquet/216GB/0inc/5子集:web-pro100+code16+qa32+text-code-block200+translated-code16); 🔄IFM/Math-Reasoning下载中(553/2228parquet/25%/1.1TB/2inc/PID2351909/ni=19/elapsed~4.8h/math-dialogue子集(1/5)下载中/rate持续减速(2.93→27.92s/it)⚠️/log→/tmp/dl_math_reasoning_restart.log/0error/ETA~13h+→~18:00CST 11-17但rate减速可能更长至20h+); 🔄IFM/Code-Reasoning下载中(1036/1637parquet/63%/1.9TB/4inc/PID3336545/ni=19/elapsed~5.5h/rate~19s/it/code-no-thinking✅309+code-no-thinking-hard✅235+code-task-synthesis✅198+code-thinking-hard✅198+code-thinking-v0🔄96(下载中)/剩余2子集(code-thinking-v1+codeio)/log→/tmp/dl_master_orchestrator.log/ETA~3.2h→~10:00CST 11-17); ✅MegaMath≡LLM360/MegaMath(sha 3cbc646 一致); ✅调研报告report_data_math_code_datasets_survey_zh.html落reports/(17KB/Top5+总表+污染+重叠+SVG); ⏳MegaMath第二批(megamath-web~1TB)待两路下载完成后启动; /nas_user 113T/64T已用/49T可用(57%)→✅红线≥5T; IFM总~3.2T/1953parquet(364+1036+553)/6inc(0+4+2); ⚠️Math-Reasoning rate减速严重(chunk0→chunk1文件变大+可能HF限速)→持续监控,若停滞>2h考虑重启

> ✅ **用户令 2026-11-15 09:0x（5个agent datasets评估+下载）→全部验收项已满足**：✅Toucan-1.5M(409files/21GB/0inc); ✅AgentTrove(121files/19GB/0inc); ✅neulab ADP 15子集(277files/79GB/0inc); ✅adp_subset_plan.md; ✅agent-data-protocol clone; ✅污染检查CONTAMINATION_CHECK_AGENT_IFM.md; ✅DATA_MAPPING.md D1-D4; 🚫orca P2/🚫freeinference P3; 📝转告harness线freeinference workload(已记MEMORY+DATA_MAPPING)

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ vision图文对调研报告DONE（唤醒1448,2026-11-11）**：用户令11-11→归因(10-13下载4路69.6M对未用=格式不兼容parquet/tar+无人接管线+实验设计限制)+平台盘点(中文9源/多语言2源/领域7源/已在盘7源)+推荐Top5(InternVL-SA1B零成本/TaiSu最佳中文/WebMix-38M规模/LAION-Chinese商用/PlotQA领域)+许可合规+下一步建议→report_vision_textpair_sourcing_zh.html(28321B/6节/0外链/HTML valid)落reports/→commit data rpt: pushed。

> 🟢 **✅ stack-v3-train 2TB下载全DONE（唤醒1422,03:56）**：batch7 FINISH@03:46:06→4600parquet/1,987,930,402,327B(1.85TiB)/0inc；2TB ROI复盘:token~2,025B/重叠2.4%/97.6%独特/ROI判定✅有价值→停止下载进入过滤+分词。

> 🟢 **✅ stack-v3-train 分词全DONE（唤醒1478,2026-11-13 10:1x）**：主跑4600/4600shard完成(47068s/173M docs/245.8B tok/279ERR);rerun 40shard完成(4492s/3.4B tok/0ERR);二次rerun确认40shard全SKIP(已有tokenized);tokenized输出926GB@/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/;无tokenize进程在跑→分词完全结束。

> 🟢 **✅ EDA脚本价值分析DONE（唤醒1468,2026-11-12 23:5x）**：用户令11-12→Phase A全扫4600shard(97M repos/1.28B files/5.86TiB/vendor1.3%/4963s)+Phase B分层抽样3200文件(9类)→V1=18/V2=149/V3=3033→外推V1~828文件/~0.01B token→Tcl唯一显著EDA命中(39.2%)/SKILL未检出/PyAether 0命中→报告report_data_stackv3_eda_script_value_zh.html(43KB/8节+附录/0外链/0script)落reports/→DATA_MAPPING.md§H.13新增→commit data eda:。
> 📝 **结论**：V1(直接可用)~828文件/~0.01B tok, V2(可挖掘)~6854文件/~0.04B tok, V3(低价值)~139518文件；报告路径reports/report_data_stackv3_eda_script_value_zh.html；建议：stack-v3对EDA脚本直接贡献有限，SKILL/PyAether需外部数据源。

> 📦 唤醒1522-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC完成+IFM下载启动+Code-Reasoning崩溃修复重启+多轮巡检,共10轮,详见日文件）
> 📦 唤醒1493-1520 原文已归档 → daily-memories-data/2026-11-14.md~2026-11-15.md（StepB完成+StepC分词启动+崩溃修复+IFM/agent datasets进度,共~25轮,详见日文件）
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
PHASE:        IFM Math/Code-Reasoning后台下载中(Math 24%/Code 55%) → WAITING=1(30min长睡监控)
已完成:       ✅分词全DONE(8192shard/476B tok/1.8TB/0ERR);✅StepA/B/D全完成;✅EDA分析DONE;✅2TB下载DONE+ROI复盘;✅vision图文对调研报告;✅5agent datasets DONE;✅3 IFM datasets HfApi探测全DONE;✅adp_subset_plan.md;✅agent-data-protocol clone;✅DATA_MAPPING.md D1-D4+H.14;✅调研报告report_data_math_code_datasets_survey_zh.html;✅IFM/MegaMath≡LLM360/MegaMath SHA验证;✅污染检查结论;✅Toucan(21GB)+AgentTrove(19GB)+neulab(79GB);✅MegaMath batch1(216GB/5子集);✅P3 freeinference转告harness线
当前动作:     例行巡检:两路IFM下载后台运行中(Math-Reasoning 540/2228=24%/1010GB/PID2351909/ni=19/elapsed~1h/ETA~108h;Code-Reasoning 898/1637=55%/1.7TB/PID3336545/ni=19/elapsed~1.7h/ETA~1.3h→~04:22);nice19/max-workers2不挤S1;磁盘/nas_user 113T/50T可用(57%)✅;IFM总~2.93T/1802parquet/6inc;新Math restart log 0error;orchestrator log有8条旧ProxyError(503)已被restart替代
下一步:       ①等IFM Code-Reasoning完成(ETA~1.3h→~04:22)→更新DATA_MAPPING+commit+启动MegaMath batch2(megamath-web~1TB);②等IFM Math-Reasoning完成(ETA~108h→~11-21)→更新DATA_MAPPING+commit;③所有下载完成后做逐题污染检查→闭合IFM令
阻塞:         无(IFM下载nice19/max-workers2后台运行,WAITING=1长睡30min监控)
ERROR_COUNT:  0(StepC 0ERR;IFM下载正常运行;Code-Reasoning orchestrator.log 0新错误;Math-Reasoning restart.log 0error;orchestrator log 8条旧ProxyError已被restart替代)
未完成指令:   有(IFM Math/Code-Reasoning下载未完成)→WAITING=1(后台下载,30min长睡监控)
```

> 📦 唤醒1521-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC巡检+Agent/IFM下载进度+Code-Reasoning重启+IFM多轮巡检,详见日文件）

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-17 05:5x] 唤醒1545（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc:web-pro100+text-code-block200+qa32+code16+translated-code16);②🔄Math-Reasoning RUNNING(PID2351909/ppid=2351906/ni=19/elapsed~3.8h/551parquet/2inc/1.1TB/25%/math-dialogue子集(1/5)下载中/rate~21s/it且持续减速中(2.93→24.17s/it)/log→/tmp/dl_math_reasoning_restart.log/0error/ETA~9.8h+→~15:30CST 11-17但rate减速可能更长);③🔄Code-Reasoning RUNNING(PID3336545/ppid=1829136/ni=19/elapsed~4.6h/999parquet/4inc/1.9TB/61%/code-no-thinking✅309+code-no-thinking-hard✅235+code-task-synthesis✅198+code-thinking-hard✅198+code-thinking-v0🔄60(下载中)/剩余2子集(code-thinking-v1+codeio)/rate~16s/it/log→/tmp/dl_master_orchestrator.log/0current-error/ETA~2.8h→~08:45CST 11-17);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/49T可用(57%)→✅(红线≥5T);⑥IFM总~3.2T/1914parquet(364+999+551)/6inc(0+4+2);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1(pretrain 8GPU 100%在.12跑中);⑧两路log均0error/0traceback;⑨下一步：等Code-Reasoning完成(~2.8h,~08:45)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~9.8h+,~15:30+)→最终校验+登记→闭合IFM令

> [11-17 04:0x] 唤醒1543（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID2351909/ppid=2351906/ni=19/elapsed~2h since 02:05 restart/543parquet/2inc/1015GB/24%/math-dialogue子集(1/5)下载中/rate~12s-it tqdm但实际~13min-file大文件/log→/tmp/dl_math_reasoning_restart.log/0error-0traceback/ETA很长~8天+→~11-25);③🔄Code-Reasoning RUNNING(PID3336545/ppid=1829136/ni=19/elapsed~2.6h/931parquet/4inc/1.7TB/57%/code-no-thinking✅309parquet+code-no-thinking-hard✅235parquet+code-task-synthesis✅198parquet完成+code-thinking-hard🔄190parquet(下载中)/剩余3子集(code-thinking-v1+code-thinking-v0+codeio)/rate~10s-it/log→/tmp/dl_master_orchestrator.log/ETA~8-12h→~12:00-16:00CST 11-17);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/50T可用(57%)→✅(红线≥5T);⑥IFM总3.0T/1838parquet(364+931+543)/6inc(0+4+2);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧⚠️orchestrator log有21条ProxyError(503)→经查全部来自旧Math-Reasoning进程(已被02:05restart替代)→新restart log 0error→非当前问题;⑨下一步：等Code-Reasoning完成(~8-12h,~12:00-16:00 11-17)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~8天+,~11-25)→最终校验+登记→闭合IFM令

> [11-17 06:5x] 唤醒1545（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID2351909/ppid=2351906/ni=19/elapsed~4.8h/553parquet/2inc/1.1TB/25%/math-dialogue子集(1/5)下载中/rate持续减速(2.93→27.92s/it)⚠️/log→/tmp/dl_math_reasoning_restart.log/0error/ETA~13h+→~19:30CST 11-17但rate减速可能至20h+);③🔄Code-Reasoning RUNNING(PID3336545/ppid=1829136/ni=19/elapsed~5.5h/1036parquet/4inc/1.9TB/63%/code-no-thinking✅309+code-no-thinking-hard✅235+code-task-synthesis✅198+code-thinking-hard✅198+code-thinking-v0🔄96(下载中)/剩余2子集(code-thinking-v1+codeio)/rate~19s/it/log→/tmp/dl_master_orchestrator.log/0error/ETA~3.2h→~10:00CST 11-17);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/49T可用(57%)→✅(红线≥5T);⑥IFM总~3.2T/1953parquet(364+1036+553)/6inc(0+4+2);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0error/0traceback;⑨⚠️Math-Reasoning rate减速严重(chunk0快→chunk1文件变大+可能HF限速)→持续监控,若停滞>2h考虑重启;⑩pretrain训练在.12跑中(PID2612442/torchrun/正常);⑪下一步：等Code-Reasoning完成(~3.2h,~10:00)→更新DATA_MAPPING+commit+启动MegaMath batch2→等Math-Reasoning完成(~13h+,~19:30+)→最终校验+登记→闭合IFM令

> [11-17 04:5x] 唤醒1544（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc:web-pro100/53G+text-code-block200/121G+qa32/19G+translated-code16/23G+code16/1.8G);②🔄Math-Reasoning RUNNING(PID2351909/ppid=2351906/ni=19/elapsed~2.9h/547parquet/2inc/1020GB/25%/math-dialogue子集(1/5)下载中/rate~16s/it且减速中(2.93→16.06s/it)/log→/tmp/dl_math_reasoning_restart.log/0error/ETA~7.5h→~12:27CST但rate减速可能更长);③🔄Code-Reasoning RUNNING(PID3336545/ppid=1829136/ni=19/elapsed~3.6h/971parquet/4inc/1.8TB/59%/code-no-thinking✅309/577G+code-no-thinking-hard✅235/439G+code-task-synthesis✅198/369G+code-thinking-hard✅198/369G+code-thinking-v0🔄28/53G(下载中)/剩余2子集(code-thinking-v1+codeio)/rate~13s/it/log→/tmp/dl_master_orchestrator.log/0current-error(9条ProxyError来自旧进程已替代)/ETA~2.5h→~07:24CST 11-17);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/49T可用(57%)→✅(红线≥5T);⑥IFM总~3.0T/1882parquet(364+971+547)/6inc(0+4+2);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0error/0traceback;⑨下一步：等Code-Reasoning完成(~2.5h,~07:24)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~7.5h+,~12:27+)→最终校验+登记→闭合IFM令

> [11-17 03:0x] 唤醒1542（IFM下载巡检+proxy错误溯源+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc:web-pro100/53G+text-code-block200/121G+qa32/19G+translated-code16/23G+code16/1.8G);②🔄Math-Reasoning RUNNING(PID2351909/ppid=2351906/ni=19/elapsed~1h/540parquet/2inc/1010GB/24%/math-dialogue子集(1/5)下载中/rate~230s-it新文件/log→/tmp/dl_math_reasoning_restart.log/0error-0traceback/ETA~108h→~11-21);③🔄Code-Reasoning RUNNING(PID3336545/ppid=1829136/ni=19/elapsed~1.7h/898parquet/4inc/1.7TB/55%/code-no-thinking✅309parquet/577G+code-no-thinking-hard✅235/439G+code-task-synthesis✅198/369G+code-thinking-hard🔄157/294G(下载中)/剩余3子集(code-thinking-v1+code-thinking-v0+codeio)/rate~6.6s-it/log→/tmp/dl_master_orchestrator.log/ETA~1.3h→~04:22CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/50T可用(57%)→✅(红线≥5T);⑥IFM总~2.93T/1802parquet(364+898+540)/6inc(0+4+2);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧⚠️orchestrator log有8条ProxyError(503)→经查全部来自旧Math-Reasoning进程(chunk1-00243.parquet HEAD请求×6+xet-read-token refresh×1+ConnectionError×1)→已被02:05restart替代→新restart log 0error→非当前问题;⑨下一步：等Code-Reasoning完成(~1.3h,~04:22)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~108h,~11-21)→最终校验+登记→闭合IFM令

> [11-16 21:2x] 唤醒1540（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/231.6GB/5子集/0inc/megamath-web-pro 53G+megamath-text-code-block 121G+megamath-qa 19G+megamath-code 1.8G+megamath-translated-code 23G);②🔄Math-Reasoning RUNNING(PID1829139/ppid=1829136/ni=19/elapsed~33.8h/526parquet/3inc/1058GB/24%/当前下math-dialogue子集(5子集中第1个)/rate~230s/it/log→/tmp/dl_master_orchestrator.log健康无错误/grep error/traceback 0命中/.incomplete活跃写入/ETA~108h→预计~11-21~04CST);③🔄Code-Reasoning RUNNING(PID922699/ppid=922695/ni=19/elapsed~19.6h/699parquet/2inc/1400GB/43%/code-no-thinking✅309parquet(577G)+code-no-thinking-hard✅235parquet(439G)完成+code-task-synthesis子集下载中(155parquet/290G)/剩余4子集(code-thinking-v1+code-thinking-hard+code-thinking-v0+codeio)/rate~99s/it/v2.log健康无错误/grep error/traceback 0命中/ETA~25h→预计~11-17~22CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/50T可用(57%)→✅(红线≥5T);⑥IFM总2.69T/1589parquet(364+699+526)/5inc(0+2+3);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0 error/0 traceback/0 broken;⑨下一步：等Code-Reasoning完成(~25h,~11-17 22:00)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~108h,~11-21 04:00)→最终校验+登记→闭合IFM令

> [11-16 19:3x] 唤醒1538（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID1829139/ppid=1829136/ni=19/elapsed~32.4h/514parquet/3inc/962GB/23%/当前下math-dialogue子集(5子集中第1个)/rate~224s/it/log→/tmp/dl_master_orchestrator.log健康无错误/ETA~106h→预计~11-21~03CST);③🔄Code-Reasoning RUNNING(PID922699/ppid=922695/ni=19/elapsed~18.3h/683parquet/2inc/1.3TB/42%/code-no-thinking✅309parquet+code-no-thinking-hard✅235parquet完成+code-task-synthesis子集下载中(139parquet)/剩余4子集(code-thinking-v1+code-thinking-hard+code-thinking-v0+codeio)/rate~94s/it/v2.log健康无错误/ETA~25h→预计~11-17~20CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/63T已用/50T可用(56%)→✅(红线≥5T);⑥IFM总~2.48T/1561parquet(364+683+514)/5inc(0+2+3);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0 error/0 traceback/0 broken;⑨research日报11-16有data线建议(预训练数据统计→合成数据配比实验163M×三档×Zipf/均匀)但属参考非指令;⑩下一步：等Code-Reasoning完成(~25h,~11-17 20:00)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~106h,~11-21 03:00)→最终校验+登记→闭合IFM令

> [11-17 00:1x] 唤醒1540（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID1829139/elapsed~36.2h/538parquet/3inc/1002GB/24%/math-dialogue子集538parquet(5子集中第1个)/rate~242s/it/rate略升/log健康无错误/ETA~114h→~11-21~14CST);③🔄Code-Reasoning RUNNING(PID922699/elapsed~22.4h/802parquet/2inc/1.5TB/49%/code-no-thinking✅309+code-no-thinking-hard✅235+code-task-synthesis✅198完成+code-thinking-hard🔄58(下载中)/剩余3子集(code-thinking-v1+code-thinking-v0+codeio)/rate~101s/it/log健康无错误/ETA~23h→~11-17~23CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/50T可用(57%)→✅(红线≥5T);⑥IFM总2.7T/1702parquet(364+802+538)/5inc(0+2+3);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0 error/0 traceback/0 broken;⑨pretrain训练在.12跑中(PID2612442/torchrun/正常);⑩下一步：等Code-Reasoning完成(~23h,~11-17 23:00)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~114h,~11-21 14:00)→最终校验+登记→闭合IFM令

> [11-16 22:2x] 唤醒1539（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/231.6GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID1829139/elapsed~34.7h/532parquet/3inc/1069GB/24%/math-dialogue子集532parquet(5子集中第1个)/rate~230s/it/log健康无错误/ETA~108h→~11-21~11CST);③🔄Code-Reasoning RUNNING(PID922699/elapsed~20.5h/729parquet/2inc/1461GB/45%/code-no-thinking✅309parquet+code-no-thinking-hard✅235parquet完成+code-task-synthesis子集下载中(185parquet)/剩余4子集/rate~101s/it/log健康无错误/ETA~25.5h→~11-17~24CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/64T已用/50T可用(57%)→✅(红线≥5T);⑥IFM总2.76T/1625parquet(364+729+532)/5inc(0+2+3);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0 error/0 traceback/0 broken;⑨下一步：等Code-Reasoning完成(~25.5h,~11-17 24:00)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~108h,~11-21 11:00)→最终校验+登记→闭合IFM令

> [11-16 19:0x] 唤醒1537（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID1829139/ppid=1829136/ni=19/elapsed~31.5h/506parquet/3inc/947GB/23%/当前下math-dialogue子集(5子集中第1个)/rate~222s/it/log→/tmp/dl_master_orchestrator.log健康无错误/.incomplete活跃写入/ETA~106h→预计~11-20~21CST);③🔄Code-Reasoning RUNNING(PID922699/ppid=922695/ni=19/elapsed~17.3h/668parquet/2inc/1.3TB/41%/code-no-thinking✅309parquet+code-no-thinking-hard✅235parquet完成+code-task-synthesis子集下载中(124parquet)/剩余4子集(code-thinking-v1+code-thinking-hard+code-thinking-v0+codeio)/rate~93s/it/v2.log健康无错误/ETA~25h→预计~11-17~18CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 113T/63T已用/50T可用(56%)→✅(红线≥5T);⑥IFM总~2.46T/1538parquet(364+668+506)/5inc(0+2+3);⑦两路下载并行各max-workers2/ni=19→总4并发HF请求不挤S1;⑧两路log均0 error/0 traceback/0 broken;⑨research日报11-16有data线建议(预训练数据统计→合成数据配比实验163M×三档×Zipf/均匀)但属参考非指令;⑩下一步：等Code-Reasoning完成(~25h,~11-17 18:00)→更新DATA_MAPPING+commit+启动MegaMath第二批→等Math-Reasoning完成(~106h,~11-20 21:00)→最终校验+登记→闭合IFM令

> [11-16 17:0x] 唤醒1536（IFM下载巡检+进度更新+commit）：①✅MegaMath batch1 DONE(364parquet/216GB/5子集/0inc);②🔄Math-Reasoning RUNNING(PID1829139/elapsed~29.6h/492parquet/3inc/922GB/22%/rate~214s/it/ETA~103h→~11-20~22CST);③🔄Code-Reasoning RUNNING(PID922699/elapsed~15.5h/608parquet/2inc/1.2TB/37%/rate~91s/it/ETA~26h→~11-17~19CST);④✅调研报告DONE(17KB);⑤磁盘/nas_user 50T可用(56%)✅;⑥IFM总2.3T/1464parquet/5inc;⑦两路log均0 error;⑧下一步：等Code-Reasoning完成→更新DATA_MAPPING+启动MegaMath batch2→等Math-Reasoning完成→闭合IFM令
> 📦 唤醒1522-1532 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC完成+IFM下载启动+Code-Reasoning崩溃修复重启+多轮巡检,共11轮,详见日文件）
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