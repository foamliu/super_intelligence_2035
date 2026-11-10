# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ stack-v3-train 2TB下载全DONE（唤醒1422,03:56）**：batch7 FINISH@03:46:06→4600parquet/1,987,930,402,327B(1.85TiB)/0inc；batch7 QC(3shard×200repos):6885files/20.6MiB/vendor1.0%/>1MB0/empty0/PHP12.4%/Java10.4%/Python6.2%/EDA(14)12.3%/Target(32)58.1%；2TB ROI复盘:token~2,025B(全语种)/~1,019B per TB(压缩)；重叠度stack→UDC L2=2.4%(97.6%独特)；丢弃漏斗L0→L4保留~60%(目标语言)；ROI判定✅有价值→停止下载进入过滤+分词；DATA_MAPPING.md §H.11+§H.12已写；commit data stackv3: pushed。

> 🟢 **✅ 运维令13:3x DONE（唤醒690,15:0x）**：分词 SFT-2605(94 shard/18.89B tok/75.87GB)+Agent-2609(13 shard/5.97B tok/23.89GB)→/nas_env(full_sft_2605/full_sft_agent_2609)；tokenized/ 镜像 per-file symlink→/nas_env；INDEX.tsv 922 shard triplet全OK inode_ok；DATA_MAPPING.md(10603B)行11-12=镜像完整；report_data_mapping_zh.html(20764B)12源全量更新；commit 44b512316 pushed。

> 🟢 **✅ 迁移5/5源全DONE**：math_l3✅+code_l3✅+math_l1✅+ufw_l3✅+code_l2✅(5源574bins/4.24TB全迁/nas_env,软链接全建好,源已删)。
> 🟢 **✅ 3稳定源迁移FINALIZE(唤醒678,00:3x)**：l1_en_hq(94shards)+zh(4)+AICC(1)→build_tokenized_mirror.py改symlink指向/nas_env/full_*→INDEX.tsv rebuild(815shard全triplet=OK inode=OK,3源storage=symlink)→DATA_MAPPING.md regen(指纹2953/7f2a09fb2920/00:34)→report_data_mapping_zh.html全量更新(总17.47TB,df 85%/82%)。源文件run4已删。
> 🟢 **✅ ufw_en迁移DONE(唤醒682,05:2x)**：ufw_en 32 shard / 3,222,004,397,626 B / 905.92B tokens → /nas_env/full_ufw_en/。text/源文件已删,tokenized/ 96 hardlink → per-file symlink指向/nas_env。build_tokenized_mirror.py改ufw_en ENTRIES(src_dir→/nas_env,storage=symlink)→INDEX.tsv rebuild(storage=symlink,triplet=OK,inode_ok=32)→DATA_MAPPING.md regen(bytes=3,222,004,397,626,storage=symlink)→gen_report_data_mapping_html.py新增报告生成脚本→report_data_mapping_zh.html重生成(9 symlink+1 hardlink,correct bytes)。commit ace6fac0b pushed。
> 🟢 **✅ 4源迁移全部完成**：ufw_en(32)+l1_en_hq(94)+zh(4)+AICC(1)=131 shard ≈ 4.05 TB → /nas_env。连同此前5源(574 shard/4.24TB)，/nas_env共承载9源/705 shard/~8.3TB；env14(110 shard)仍hardlink留/nas_train。
> 🟢 **✅ df实测(05:2x)**：/nas_train 174T已用/34T可用(84%,较迁移前177T/86%释放~3TB)；/nas_env 8.2T已用/1.8T可用(83%)。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ✅stack-v3-train 2TB下载全DONE→进入过滤+分词阶段(待运维指令) → ✅论文数据节更新(11-10令) → WAITING=1
已完成:       ✅85M;✅10-31报告;✅09:4x报告;✅09:2x长上下文10/10(249.48GiB);✅13:2x#2 RL报告;✅13:2x#1 B类12/12(78.73GiB);✅11-07 ROI 8源DONE(25.14GB/135文件/0inc);✅stack-v3-train调研DONE(8192shard/EDA语言27.1%);✅batch1-7全DONE(累计1,987,930,402,327B/4600parquet/0inc);✅batch7 QC(6885files/vendor1.0%/EDA12.3%);✅2TB ROI复盘(token~2,025B/重叠2.4%/97.6%独特/ROI判定✅有价值);✅论文pretrain数据节更新(淡化数据源名+Stable/Decay双饼图+中文图注,ERR=0,5pages)
当前动作:     唤醒1429(2026-11-10 10:3x):执行运维令08:1x(更新论文pretrain数据部分)→①pretrain线已先在commit b56ce5f79做了核心改动(移除Ultra-FineWeb/UltraData品牌名+补TikZ双饼图+main.tex加tikz包);②data线复核+补齐:正文line24"instruction-style"→"instruction-SFT and agentic-SFT"(对齐令§②.1类别名);caption移除过时"pending tokenization"(SFT-2605/Agent-2609已分词,见DATA_MAPPING.md行26-27镜像完整)+加中文图注注释(令§②.2"图注用中文");③pdflatex×3+bibtex:ERR=0/UNDEF=0/5pages/211KB;④Data节无品牌名(仅Architecture节保留MiniCPM5-2B引用,非数据源);⑤更新心跳+日报→commit data paper:
下一步:       等运维指令→若批准stack-v3 L4/L5 parquet级过滤+分词→用tokenizer_eod分词→落baize-data/tokenized/→更新INDEX.tsv+DATA_MAPPING.md;若无新指令→WAITING=1例行巡检
阻塞:         无(2TB下载已完成,论文数据节已更新,/nas_inference 27T可用≥5T红线)
ERROR_COUNT:  11
未完成指令:   无(11-10 08:1x论文数据节更新✅已交付;10:10令2TB下载+ROI复盘✅已交付;08:5x令ROI排序+下载✅已交付)→WAITING=1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-10 10:3x] 唤醒1429：执行运维令08:1x(更新论文pretrain数据部分)→①git pull发现pretrain线已先commit b56ce5f79做了核心改动(4_llm_pretrain.tex Data节移除Ultra-FineWeb/UltraData-Code/UltraData-Math品牌名→只说web/code/math;补fig:data-mix TikZ双饼图:Stable web74%/code19%/math7% + Decay instr-SFT60%/agentic12%/web22%/math4%/code2%;main.tex加\usepackage{tikz});②data线复核+补齐2处:line24正文"instruction-style and agentic"→"instruction-SFT and agentic-SFT"(对齐令§②.1五类别名);caption移除过时"pending tokenization"(SFT-2605 94shard/Agent-2609 13shard均已分词,DATA_MAPPING.md行26-27=镜像完整)+加%中文图注注释(令§②.2"图注用中文");③编译验证:pdflatex×3+bibtex→ERR=0/UNDEF=0/5pages/211058B;④grep确认Data节(lines21-73)无任何Ultra-/MiniCPM品牌名(仅Architecture节line7-8保留MiniCPM5-2B架构对比引用,非数据源,不在本令范围);⑤体积MEMORY32KB/TASK35KB均≤40KB无需归档→commit data paper:→WAITING=1
> [11-10 09:29] 唤醒1428：例行巡检+staleness复审→①git pull --rebase --autostash(Already up to date,TASK.md diff origin/main=空→无新data令);②research日报11-10(06:11)data建议=「路径台账staleness审计」已在唤醒1425执行完毕,本轮复审:INDEX.tsv 12条tokenized_dir全stat→12/12 OK+11条symlink download_dir全stat→11/11 OK→确认0 stale entries,0需更正;③stack-v3下载复核:/nas_inference/app.e0031982/datasets/HuggingFaceCode/stack-v3-train/=find 4600parquet/du -sb=1,987,932,716,336B(1.85TiB)/0 inc→确认完整;④pgrep无下载进程运行(2TB已停止);⑤df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;/nas_train 180T/28T可用(87%);/nas_env 8.3T/1.7T可用(84%);⑥DATA_MAPPING.md(615行/60827B)含stack-v3 §H全量+ROI复盘完整;⑦体积MEMORY 31,505B/TASK 37,391B均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 08:31] 唤醒1427：例行巡检→①git pull --rebase(Already up to date,TASK.md diff origin/main=空→无新data令);②research日报11-10(06:11)data建议=「路径台账staleness审计」已在唤醒1425执行完毕(0 stale entries),本轮无需重复;③stack-v3下载复核:find=4600parquet/du -sb=1,987,930,402,327B(1.85TiB)/0inc→确认完整;④pgrep无下载进程运行;⑤df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;/nas_train 180T/28T可用(87%);/nas_env 8.3T/1.7T可用(84%);⑥体积MEMORY 30,859B/TASK 34,967B均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 07:37] 唤醒1426：例行巡检→①git pull --rebase(c0970b5d8..d60e5d21a成功,TASK.md diff origin/main=空→无新data令);②research日报11-10(06:11)data建议=「路径台账staleness审计」已在唤醒1425执行完毕(0 stale entries),本轮无需重复执行;③stack-v3下载复核:find=4600parquet/du -sb=1,987,932,712,240B(1.85TiB)/0inc→确认完整;④pgrep无下载进程运行;⑤df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;/nas_train 180T/28T可用(87%);/nas_env 8.3T/1.7T可用(84%);⑥体积MEMORY 30,310B/TASK 34,967B均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 06:42] 唤醒1425：例行巡检+research日报2026-11-10建议执行(来自research日报2026-11-10)→①git pull --rebase(Already up to date,无新data令,TASK.md无变化);②research日报11-10(06:11)已发布,data建议=「路径台账staleness审计」(arXiv 2611.09802 Instruction Files Go Stale):逐条验证DATA_MAPPING.md §H.11/§H.12与INDEX.tsv路径+tokenized/软链目标是否仍可解析;③执行审计:INDEX.tsv 12条tokenized_dir全stat→12/12 OK;12条download_dir全stat→12/12 OK(1 hardlink+11 symlink);5条symlink源抽样readlink→全resolve至/nas_env/app.e0031982/baize-data/full_*目标存在;§H stack-v3-train data/路径stat OK+4600parquet确认→**0 stale entries,0需更正**;④stack-v3下载复核:4600parquet/1,987,932,712,240B(1.85TiB)/0inc→确认完整;⑤pgrep无下载进程运行;⑥df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;⑦体积MEMORY~29KB/TASK~35KB均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 05:47] 唤醒1424：例行巡检→①git fetch origin(代理,Already up to date,无新data令,TASK.md无变化,0ahead/0behind);②research日报仍11-09(06:10),11-10 06:00新报未到点;③stack-v3下载复核:4600parquet/1,987,932,712,240B(1.85TiB)/0inc→确认完整;④pgrep无下载进程运行;⑤df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;⑥体积MEMORY~29KB/TASK~35KB均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 04:51] 唤醒1423：例行巡检→①git fetch origin(代理,Already up to date,无新data令,TASK.md无变化);②research日报11-09(06:10)已阅:data建议=「丢弃漏斗+偏差声明」(每级过滤记输入/输出/丢弃率/原因分布,按语言/文件类型分层,3级:规则级+一致性级+可解性级,声明偏差方向,arXiv 2611.07634),纳注用于2TB L4/L5过滤阶段(来自research日报2026-11-09),本轮不执行(待运维批准过滤);③stack-v3下载复核:4600parquet/1,987,932,712,240B(1.85TiB)/0inc→确认完整无遗漏;④pgrep无下载进程运行(2TB已停止);⑤df:/nas_inference 19T已用/27T可用(42%)≥5T红线OK;⑥体积MEMORY~28KB/TASK~35KB均≤40KB无需归档→更新心跳→commit→WAITING=1
> [11-10 03:56] 唤醒1422：batch7完成确认+QC+2TB ROI复盘→①git fetch origin(无新data令);②batch7 FINISH@03:46:06:4600parquet/1,987,930,402,327B(1.85TiB)/0inc(全部7批完成,无hf download进程);③batch7 QC(3shard×200repos=600repos):6885files/20.6MiB/vendor67(1.0%)/>1MB0/empty0/PHP12.4%/Java10.4%/Jupyter9.4%/Python6.2%/EDA(14)12.3%/Target(32)58.1%;④2TB ROI复盘:token~2,025B(3.6T×56.2%比例外推)/~1,019B per TB(压缩)/~313B per TB(解压);重叠度stack→UDC L2=2.4%(5,061/210,776repos)/97.6%独特(repo级集合交集,UDC L3 schema不同未纳入);丢弃漏斗L0→L4:1.99TB→~1.0TB(保留~60%目标语言);ROI判定✅有价值→停止下载;⑤DATA_MAPPING.md §H.11(batch7QC)+§H.12(2TB ROI复盘)已写;⑥QC脚本+重叠分析脚本已存run/data/;⑦体积MEMORY~27KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> 📦 唤醒1421 原文已归档(见下行,batch7进度巡检)→①git fetch origin(无新data令);②batch7进度:part-042✅(100/100)+part-043✅(100/100)+part-044@38/100files(38%,rate~22s/file,part-04400~04437已下完)+part-045待开;③du -sb=1.918TB累计/4435parquet/2inc(part-04438~04439在途,非阻塞);④PID3757293(hf download part-044*,nice=10,--max-workers2,etimes~799s)alive,父PID1031702(batch script,etimes~13449s≈3.7h);⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算95.9%已用(1.918TB/2TB),余~82.3GB;⑦ETA:part-044余62files@22s≈23min+part-045(100files)@22s≈37min→batch7预计~11-10 03:5x完成,累计~1.99TB≈2TB达标;⑧research日报11-09AM已阅(下次06:00):data建议=「丢弃漏斗+偏差声明」用于2TB ROI复盘(已在计划,本轮不执行);⑨体积MEMORY~26KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> [11-10 01:53] 唤醒1420：batch7进度巡检→①git fetch origin(无新data令);②batch7进度:hundred042@77/100files(77%,+56files since wake1419),part-04200~04276已下完,速率从~315s/it恢复至~1file/min;③du -sb=1,847,201,688,395B(1.847TB累计)/4275parquet/2inc(在途非阻塞);④PID1031713(hf download part-042*,nice=10,--max-workers2,etimes~10106s≈2.8h)alive;⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算92.4%已用(1.847TB/2TB),余~153GB;⑦ETA:hundred042余23files~23min+043-045(300files)~5h→batch7预计~11-10 07:0x完成;⑧research日报无新报(下次06:00);⑨体积MEMORY~25KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> [11-10 00:58] 唤醒1419：batch7进度巡检→①git pull origin main --rebase(Already up to date,运维无新data令);②batch7进度:hundred042@21/100files(21%),21parquet(part-04200~04220)已下完,04221~04222在途,速率从~60s/it降至~315s/it(网络波动,非阻塞);③du -sb=1,821,964,101,439B(1.822TB累计)/4221parquet/2inc(在途非阻塞);④PID1031713(hf download part-042*,nice=10,--max-workers2,etimes~6729s≈1.9h)alive;⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算91.1%已用(1.822TB/2TB),余~178GB,batch7(4hundreds×~43.4GB≈174GB)将凑满~1.996TB≈2TB;⑦ETA:042余79files@~315s/it≈6.9h+043-045(300files)≈26.3h→batch7预计~11-11 10:0x完成;⑧research日报11-09AM已阅:data建议=「丢弃漏斗+偏差声明」用于2TB ROI复盘(已在计划,本轮不执行);⑨体积MEMORY~24KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> [11-10 00:02] 唤醒1418：batch7进度巡检→①git pull --rebase --autostash(Already up to date,运维无新data令);②batch7进度:hundred042@13/100files(13%),13parquet(04200-04212)已下完,04213-04214在途,速率从前期~60s/it降至~250s/it(网络波动,非阻塞);③du -sb=1,818,502,543,760B(1.819TB累计)/4213parquet/2inc(在途非阻塞);④PID1031696(batch script,etimes~3384s≈56min)+PID1031713(hf download part-042*,nice=10,--max-workers2)alive;⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算90.9%已用(1.819TB/2TB),余~181GB,batch7~164GB将凑满~1.98TB≈2TB;⑦ETA:042@13/100→~7h,4hundreds共~28h→batch7预计~11-11 04:0x完成;⑧research日报11-09已阅(唤醒1416):data建议=「丢弃漏斗+偏差声明」用于2TB ROI复盘,本轮不执行;⑨体积MEMORY~23KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> [11-09 23:0x] 唤醒1417：batch6完成验收+batch7启动→①git pull --rebase --autostash(Already up to date,运维无新data令);②batch6已完成:4200parquet/1,812,676,831,055B(1.813TB)/0inc,batch6_status.tsv确认035-041全OK,FINISH@22:44:05;③batch6 QC(§H.10):3shard(part-03500/03850/04199)×200repos=600repos抽样,5428files/14.6MiB,Java17.4%/Python7.8%/Jupyter7.7%/JS7.4%/C++4.7%/EDA(14)17.6%/Target(32)59.1%/vendor1.1%/>1MB0/空仓0,质量稳定;④DATA_MAPPING.md H.4表batch6行+H.10质检报告已回填;⑤batch7已启动(042-045,4hundreds~164GB末批),PID1031702+PID1031713(hf download part-042*,nice=10,--max-workers2)alive;⑥df:/nas_inference 27T可用≥5T红线OK;⑦2TB预算90.6%已用,batch7~164GB将凑满~1.977TB≈2TB;⑧体积MEMORY~23KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1

> [11-09 21:3x] 唤醒1416：batch6进度巡检→①git pull --rebase --autostash(Already up to date,运维无新data令);②research日报11-09 06:10已阅:data建议=「丢弃漏斗+偏差声明」+「stack-v3重叠度改结构指纹+5-gram双口径」(用于2TB ROI复盘,本轮不执行);③batch6进度:hundred035✅036✅037✅038✅039✅040✅全DONE(600parquet)+hundred041@37/100下载中(~46s/it,ETA~49min);④du -sb=1,784,816,838,147B(1.785TB累计)/4135parquet/2inc(041在途非阻塞);⑤PID83585 alive(batch script,etimes~24642s≈6.8h)+PID2722658 alive(hf download part-041*,nice=10,--max-workers2,etimes~1764s≈29min);⑥df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑦2TB预算89.2%已用(1.785TB/2TB),余0.215TB;⑧体积MEMORY~22KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1
> [11-09 21:05] 唤醒1415：batch6进度巡检→①git pull --rebase --autostash(Already up to date,运维无新data令);②batch6进度:hundred035✅036✅037✅038✅039✅全DONE(500parquet)+hundred040@69/100下载中(~135s/it,ETA~70min),041待下;③du -sb=1,757,675,589,988B(1.758TB累计)/4069parquet/2inc(在途非阻塞);④PID83585 alive(batch script,etimes~21221s≈5.9h)+PID1877185 alive(hf download part-040*,nice=10,--max-workers2,etimes~9389s≈2.6h);⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算87.9%已用(1.758TB/2TB),余0.242TB;⑦体积MEMORY~21KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1继续监控batch6

> [11-09 20:0x] 唤醒1414：batch6进度巡检→①git pull --rebase --autostash(Already up to date,运维无新data令);②batch6进度:hundred035✅036✅037✅038✅039✅全DONE(500parquet)+hundred040@44/100下载中(part-04045,~135s/it,ETA~2.1h),041待下;③du -sb=1,747,181,416,152B(1.747TB累计)/4044parquet/2inc(04044-04045在途非阻塞);④PID83585 alive(batch script,etimes~17792s)+PID1877185 alive(hf download part-040*,nice=10,--max-workers2,etimes~5960s);⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算87.3%已用(1.747TB/2TB),余0.253TB;⑦research日报11-09建议「丢弃漏斗」(每级过滤记输入/输出/丢弃率/原因)纳入ROI复盘;⑧体积MEMORY~20KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1继续监控batch6
> [11-09 19:1x] 唤醒1413：batch6进度巡检→①git pull --rebase --autostash(origin/main前进=designflow/harness非本线,运维无新data令);②batch6进度:hundred035✅036✅037✅038✅039✅全DONE(500parquet)+hundred040@18/100下载中(part-04017 last,part-04018-04019在.incomplete,~133s/it,ETA~3h),041待下;③du -sb=1,736,888,248,379B(1.737TB累计)/4018parquet/2inc(在途非阻塞);④PID83585(parent batch script,etimes~14296s)+PID1877185(hf download part-040*,nice=10,--max-workers2,etimes~2464s)均alive;⑤df:/nas_inference 19T/27T可用(42%)≥5T红线OK;⑥2TB预算86.8%已用(1.737TB/2TB),余0.263TB;⑦体积MEMORY~20KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1继续监控batch6
> [11-09 18:1x] 唤醒1412：batch6进度巡检→①git fetch origin(代理,origin/main+1=harness r1988非本线,运维无新data令);②batch6进度:hundred035✅036✅037✅038✅全DONE(各100parquet/400parquet batch6已完成)+hundred039@81/100下载中(part-03979,~19s/it,ETA~6min),040-041待下;③du -sb=1,720,792,612,130B(1.721TB累计)/3980parquet/2inc(0B stubs非阻塞);④PID1255226 alive(hf download part-039*,nice=10,etimes~3031s~50min);⑤df:/nas_inference 19T/27T可用(41%)≥5T红线OK;⑥2TB预算86%已用(1.721TB/2TB),余0.279TB;⑦速率~100parquet/hr(~42GB/hr),batch6 ETA~19:3x;⑧体积MEMORY~19KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1继续监控batch6

> [11-09 17:1x] 唤醒1411：batch6进度巡检→①git fetch origin(代理,gc.log+loose objects warning非阻塞,0ahead/0behind);git diff origin/main--BAIZE_DATA_TASK.md=空(运维无新令);②batch6进度:hundred035✅036✅037✅全DONE(各100parquet/1,643,510,225,328B累计)+hundred038@81/100下载中(~19s/it,ETA~6min),039-041待下;③du -sb=1,675,556,536,886B(1.676TB累计)/3877parquet/2inc(038在途非阻塞);④PID3084288 alive(hf download part-038*,nice=10,etimes~1505s);⑤df:/nas_inference 19T/27T可用(41%)≥5T红线OK;⑥2TB预算83.8%已用(1.676TB/2TB),余0.324TB;⑦体积MEMORY~18KB/TASK~35KB均≤40KB无需归档→commit data stackv3:→WAITING=1继续监控batch6

> [11-09 16:1x] 唤醒1410：batch6进度巡检→①git fetch origin(代理,gc.log+loose objects warning非阻塞,0ahead/0behind);git diff origin/main--BAIZE_DATA_TASK.md=空(运维无新令);②batch6进度:hundred035✅DONE(100parquet/1,559,762,533,192B累计)+hundred036@81/100下载中(~20s/it,ETA~6min),037-041待下;③du -sb=1,592,819,356,101B(1.593TB累计)/3678parquet/2inc(036在途非阻塞);④进程核验:PID2525411(hf download part-036*,nice=10,etimes~1552s)alive,batch6脚本PID alive;⑤df:/nas_inference 19T已用/27T可用(41%)≥5T红线OK;/nas_train 180T/87%;⑥2TB预算79.7%已用(1.593TB/2TB),余0.407TB→batch6完成后batch7(042~045,4hundreds~173GB)凑~1,990GB≈2TB;⑦research日报11-09已阅(丢弃漏斗建议已纳注2TB复盘,本轮不执行);⑧体积MEMORY40.3KB>40KB→归档唤醒1389-1404旧流水(16轮batch1-4巡检)→commit data stackv3:→WAITING=1继续监控batch6
> [11-09 15:0x] 唤醒1409：batch5完成验收+batch6启动→①git fetch origin(代理,0ahead/0behind,运维无新令);②batch5实测:du=1,517,036,967,760B(1.517TB累计)/3500parquet/0inc✅FINISH@14:48:55(batch5_status.tsv:028-034全OK/7hundreds/303,379,488,262B delta);③batch5 QC:3shard(part-02800/03150/03499)×200repos=600repos抽样,11,233files/21.6MiB,Java16.1%/JS10.5%/C++8.2%/Python7.8%/Markdown6.6%/EDA(14)20.1%/Target(32)63.7%/Vendor0.6%/>1MB0%/空仓库0%;④DATA_MAPPING.md §H.4 batch5行回填(303,379,488,262B/700parquet/0inc/✅已完成14:48)+§H.9 batch5 QC报告新增(五批合计EDA~17%/累计token~1,546B);⑤batch6启动:PID83585(bash stackv3_batch_download.sh 6 035 041)+PID83596(hf download part-035*,nice=10),7hundreds~303GB,ETA~4h;⑥df:/nas_inference 19T已用/27T可用(41%)≥5T红线OK;⑦2TB预算76%已用(1.517TB/2TB),余0.483TB→batch7(042~045,4hundreds~173GB)凑满~1,990GB≈2TB;⑧体积MEMORY39.1KB/TASK~35KB均≤40KB无需归档;⑨research日报11-09已阅(wake1406纳注:丢弃漏斗+偏差声明用于2TB复盘,本轮不执行)→更新心跳→commit data stackv3:→WAITING=1继续监控batch6
> [11-09 14:0x] 唤醒1408：batch5巡检→①git fetch origin(代理,0ahead/0behind,运维无新令);②batch5进度:hundred028✅DONE+hundred029✅DONE+hundred030✅DONE+hundred031✅DONE+hundred032✅DONE+hundred033✅DONE(600parquet/1,473,909,446,660B累计)+hundred034下载中(34/100files,~53s/it,34%,ETA~58min);③du -sb=1,488,063,543,632B(1.49TB累计)/3433parquet/0inc(34已完成34个parquet在data/,.incomplete在.cache/非阻塞);④df:/nas_inference 19T已用/27T可用(41%)≥5T红线OK;⑤进程核验:PID1647569(hf download part-034*,nice=10,etimes~1728s)alive,batch5脚本PID3721737(etimes~13868s)alive;⑥2TB预算74.5%已用(1.49TB/2TB),余0.51TB;⑦体积MEMORY~37.5KB/TASK~35KB均≤40KB无需归档;⑧research日报11-09已阅(wake1406纳注:丢弃漏斗+偏差声明用于2TB复盘)→更新心跳→commit data stackv3:→WAITING=1继续监控batch5
> [11-09 13:1x] 唤醒1407：batch5巡检→①git fetch origin(代理,0ahead/0behind,task diff=空,运维无新令);②batch5进度:hundred028✅DONE+hundred029✅DONE+hundred030✅DONE+hundred031✅DONE+hundred032✅DONE(500parquet/1,431,937,581,769B累计)+hundred033下载中(6/100files,刚启动~96s)+hundred034待下;③du -sb=1,433,526,771,155B(1.43TB累计)/3304parquet/2inc(033在途非阻塞);④df:/nas_inference 19T已用/27T可用(41%)≥5T红线OK;⑤进程核验:PID3452541(hf download part-033*,nice=10,etimes~96s)alive,batch5脚本PID3721737(etimes~10268s)alive;⑥2TB预算71.7%已用(1.43TB/2TB),余0.57TB;⑦体积MEMORY~37.5KB/TASK~35KB均≤40KB无需归档→更新心跳→commit data stackv3:→WAITING=1继续监控batch5
> [11-09 12:08] 唤醒1406：batch5巡检→①git fetch origin(代理,gc.log+loose objects warning非阻塞,0ahead/0behind);git diff origin/main--BAIZE_DATA_TASK.md=空(运维无新令);②research日报11-09 06:10已阅:data建议=「丢弃漏斗+偏差声明」(每级过滤记输入/输出/丢弃率/原因,按语言/文件类型分层,声明偏差方向),纳注:用于2TB复盘§4(来自research日报2026-11-09),本轮不执行;③batch5进度:hundred028✅DONE(100parquet/1,260,415,551,950B累计)+hundred029✅DONE(100parquet/1,300,598,111,613B累计)+hundred030✅DONE(100parquet/1,344,488,957,634B累计)+hundred031下载中(35/100files,~21s/it,29%|29/100,ETA~23min)+hundred032-034待下;④du -sb=1,359,401,419,881B(1.36TB累计)/3135parquet/2inc(031在途非阻塞);⑤df:/nas_inference 19T已用/27T可用(41%)≥5T红线OK;/nas_train 179T/87%;⑥进程核验:PID2695727(hf download part-031*,nice=10,etimes~562s)alive,log正常(21s/it,29%|29/100);⑦2TB预算68%已用(1.36TB/2TB),余0.64TB;⑧体积MEMORY~36KB/TASK~35KB均≤40KB无需归档→更新心跳→commit data stackv3:→WAITING=1继续监控batch5
> [11-09 10:12] 唤醒1405：batch4完成确认+QC+batch5启动→①git pull --rebase(Already up to date,无新data令);②batch4已FINISH@09:20:52:2800parquet/1,213,655,597,615B/0inc,batch4_status.tsv:hundred021-027全OK(0failed);③QC抽样3 shard(part-02100/02450/02799×200repos=600repos):7587files/19.1MiB/Java23.1%/Jupyter9.4%/Python7.3%/C++6.1%/C4.3%/EDA(14)18.2%/Target(32)57.1%/Vendor71(0.9%)/>1MB=0/Empty=0;④batch4 delta=304,095,658,670B(283.2GiB),累计b1+b2+b3+b4=1,213,655,597,615B(1,129.7GiB≈1.10TiB)=2TB预算57%;⑤DATA_MAPPING.md更新:§H.4 batch4行→✅已完成(304,095,658,670B/700parquet/0inc)+batch5行→🔄下载中+累计行→1,213,655,597,615B/2800parquet/57%;§H.8质检报告新增;⑥df:/nas_inference 18T已用/28T可用(40%)≥5T红线OK;⑦batch5已启动(028-034,setsid后台PID3721737,stackv3_batch_download.sh 5 028 034);⑧体积MEMORY~35KB/TASK~35KB均≤40KB无需归档→更新心跳→commit data stackv3:→WAITING=1继续监控batch5
> 📦 唤醒1386-1404 原文已归档 → daily-memories-data/2026-11-08.md~2026-11-09.md（batch1-4进度巡检+batch2-4启动/QC,共19轮,详见日文件）
> [11-07 08:55] 唤醒1385：执行11-07运维令(代码语料放行ROI下载)→①git fetch(代理)0behind/0ahead;②检测到TASK.md新令(stack-v2禁下/stack-v3-train可考虑/单集<1TB放行/自排ROI);③HF API核实10候选体量(LongBlocks9.57G/Nemotron-RL-Agentic5.1G/NExtLong-Instruct2.89G/arxiv6.04G/LongWriter0.15G/SkyRL0.002G/swev-trm0.93G/LongBench-v2 0.47G/gutenberg7.63G/kl3m~16.9G);④ROI评估表(5维度)写DATA_MAPPING.md §G.1(8下载/3跳过/1报运维);⑤下载脚本roi_download_20261107.sh启动setsid后台PID1920377(nice -n10/--max-workers4/代理/断点续传);⑥LongBlocks下载中9/39~23%;⑦跳过gutenberg(冗余whole-books)+kl3m(域不匹配+tokenizer不兼容)+terminal-bench-2(401);⑧stack-v3-train(15.9TB)≥1TB报运维待批;⑨DATA_MAPPING.md §G.2跳过清单+§G.3≥1TB待批+§G.4下载登记已写;→更新心跳→commit+push→WAITING=1继续监控下载
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