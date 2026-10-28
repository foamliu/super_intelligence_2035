# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

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
PHASE:        ✅运维令10:1x暂停下载DONE.无活跃下载/迁移进程(.12验),12源全部镜像完整.例行巡检中
已完成:       ✅运维令10:1x暂停下载(pgrep验.12无download_85m/hf/rsync/wget/aria2进程,判据满足);✅运维令13:3x SFT分词全DONE;✅运维令08:3x刷新两文件;✅12源全部镜像完整(922shard)
当前动作:     唤醒736(2026-10-28 22:47):例行心跳巡检(上次心跳@22:28距今~19min)→①git fetch=无新运维令✓;②pgrep验无下载/迁移进程✓;③df /nas_train 173T/84%(35T可用)+/nas_env 8.3T/84%(1.7T可用)✓;④体积MEMORY 39.8KB/TASK 35.7KB均≤40KB✓;⑤git status -sb=无ahead/behind(他线文件不碰)✓;⑥更新心跳+日报+commit+push
下一步:       待「恢复下载」新令.此前不发起新下载/迁移.WAITING:1
阻塞:         无
ERROR_COUNT:  10
未完成指令:   无(所有运维令已DONE)→WAITING:1
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [22:47] 唤醒736：例行心跳巡检(上次心跳@22:28距今~19min) → ①git fetch=无新运维令✓;②pgrep验无下载/迁移进程✓;③df /nas_train 173T/84%(35T可用)+/nas_env 8.3T/84%(1.7T可用)✓;④体积MEMORY 39.8KB/TASK 35.7KB均≤40KB✓;⑤git status -sb=无ahead/behind(他线文件不碰)✓;⑥更新心跳+日报+commit+push.未完成指令:无(所有运维令已DONE)→WAITING:1
>
> 📦 唤醒735(10-28 22:28)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒734(10-28 22:10)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒732(10-28 21:33)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒731(10-28 21:15)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒729(10-28 20:40)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒728(10-28 20:22)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒726(10-28 19:44)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒725(10-28 19:27)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒724(10-28 19:09)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒723(10-28 18:51)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒722(10-28 18:33)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒721(10-28 18:16)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒719(10-28 17:41)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒717(10-28 17:03)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒715(10-28 16:27)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒714(10-28 16:10)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒713(10-28 15:52)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒712(10-28 15:34)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒711(10-28 15:15)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒710(10-28 15:09)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒708(10-28 14:47)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒707(10-28 14:29)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒706(10-28 13:2x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒705(10-28 12:2x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒704(10-28 11:5x)原文归档 → daily-memories-data/2026-10-28.md（暂停下载执行,详见日文件）
>
> 📦 唤醒703(10-28 10:5x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒702(10-28 09:5x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒701(10-28 08:4x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）
>
> 📦 唤醒700(10-28 07:3x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）

> 📦 唤醒699(10-28 05:1x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）

> 📦 唤醒698(10-28 02:5x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）

> 📦 唤醒697(10-28 01:4x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）

> 📦 唤醒696(10-28 00:4x)原文归档 → daily-memories-data/2026-10-28.md（例行巡检,详见日文件）

> 📦 唤醒695(10-27 23:3x)原文归档 → daily-memories-data/2026-10-27.md（例行巡检,详见日文件）

> 📦 唤醒694(10-27 22:2x)原文归档 → daily-memories-data/2026-10-27.md（例行巡检,详见日文件）

> 📦 唤醒693(10-27 21:1x)原文归档 → daily-memories-data/2026-10-27.md（例行巡检,详见日文件）

> 📦 唤醒692(10-27 20:0x)原文归档 → daily-memories-data/2026-10-27.md（例行巡检,详见日文件）

> [20:0x] 唤醒692：例行心跳巡检(无新运维令,上次data commit bd523902c@18:5x≈1.2h前) → ①git fetch无BAIZE_DATA_TASK.md新提交(13:3x仍最高且DONE)✓;②复核运维令13:3x全DONE:INDEX.tsv L12-13 SFT-2605(94shard/triplet=OK/inode_ok=94/symlink)+Agent-2609(13shard/triplet=OK/inode_ok=13/symlink)✓;SFT-2605 94.bin+94.idx+95.json 0悬空✓;Agent-2609 13.bin+13.idx+14.json 0悬空✓;/nas_env full_sft_2605=71G+full_sft_agent_2609=23G✓;③DATA_MAPPING.md=10603B行11-12=镜像完整✓;report=20764B(12源)✓;④df /nas_env 8.3T/84% /nas_train 175T/85%✓;⑤git main...origin/main无ahead/behind✓;⑥无runner进程残留✓;⑦体积MEMORY 34.6KB/TASK 34.7KB均≤40KB✓;⑧更新心跳+日报+commit+push。未完成指令:无→WAITING:1

> 📦 唤醒691(10-27 18:5x)原文归档 → daily-memories-data/2026-10-27.md（例行巡检+补提交.du_download_cache.tsv,详见日文件）

> [18:5x] 唤醒691：例行心跳巡检(无新运维令,上次data commit bd523902c@15:2x≈3h前) → ①git fetch无BAIZE_DATA_TASK.md新提交(13:3x仍最高且DONE)✓;②复核运维令13:3x全DONE:INDEX.tsv 14行(12源+合计)L12-13 SFT-2605(94shard/triplet=OK/inode_ok=94/symlink)+Agent-2609(13shard/triplet=OK/inode_ok=13/symlink)✓;SFT-2605 tokenized/94.bin+94.idx+95.json 0悬空✓;Agent-2609 13.bin+13.idx+14.json 0悬空✓;/nas_env full_sft_2605=71G+full_sft_agent_2609=23G✓;③DATA_MAPPING.md=10603B行11-12=镜像完整✓;report=20764B(12源)✓;④df /nas_env 8.3T/84% /nas_train 175T/85%✓;⑤git main...origin/main无ahead/behind✓;⑥发现.du_download_cache.tsv未提交(runner git add遗漏,含SFT-2605+Agent-2609两行du缓存)→本轮补提交;⑦体积MEMORY 33.5KB/TASK 34.7KB均≤40KB✓;⑧无runner进程残留✓;⑨更新心跳+日报+commit .du_download_cache.tsv+push。未完成指令:无→WAITING:1

> 📦 唤醒690(10-27 15:2x)原文归档 → daily-memories-data/2026-10-27.md（13:3x验证:runner完成无残留/SFT-2605 94shard+Agent-2609 13shard 0悬空/INDEX.tsv 922shard/DMM 10603B/report 20764B/commit 44b512316 pushed,详见日文件）

> [15:2x] 唤醒690：验证运维令13:3x交付完成 → ①runner PID1054237已完成(ps无进程残留,无preprocess_data子进程);②验证SFT-2605 tokenized/(94 .bin+94 .idx+94 .json,symlink→/nas_env/app.e0031982/baize-data/full_sft_2605/,find -type l ! -exec test -e = 0悬空✓);③验证Agent-2609 tokenized/(13 .bin+13 .idx+13 .json,symlink→/nas_env/app.e0031982/baize-data/full_sft_agent_2609/,0悬空✓);④/nas_env/full_sft_2605/(74092556KB≈74GB)+full_sft_agent_2609/(23326764KB≈23GB)实文件在位✓;⑤INDEX.tsv L12-13: SFT-2605 triplet=OK inode_ok=94 / Agent-2609 triplet=OK inode_ok=13 / TOTAL=922shard/4498619063829tok/17666524644830B✓;⑥DATA_MAPPING.md=10603B行11-12=镜像完整(commit44b512316)✓;⑦report_data_mapping_zh.html=20764B(12源)✓;⑧git origin/main=0fd247d89(harness建于44b512316之上=data commit已push)✓;⑨更新心跳快照+流水+日报,commit data heartbeat:。未完成指令:无→WAITING:1

> 📦 唤醒689(10-27 14:1x)原文归档 → daily-memories-data/2026-10-27.md（13:3x令执行：新建convert_sft_jsonl_to_parquet.py+run_tokenize_sft.sh三阶段自治runner+build_tokenized_mirror.py+2ENTRIES+gen_report改;smoke-test PASS;full runner PID1054237 launched Phase1 convert进行中;脚本commit e254a4c2e pushed;runner后自治完成Phase1→Phase2→Phase3,commit 44b512316 at 15:06推送DATA_MAPPING.md+report）

> [14:1x] 唤醒689：执行运维令13:3x（分词SFT-2605+Agent-2609→/nas_env·用户直令·最高优先）→ ①读BAIZE_DATA_TASK.md发现13:3x新令(比pasted的08:3x更高优先,08:3x刷新两文件已DONE commit 42bf3a52f);②新建convert_sft_jsonl_to_parquet.py(~180行,--kind{sft2605,agent2609},SFT-2605 role-tagged content串行化,Agent-2609 tool_calls/reasoning_content/tools/tool-role全序列化带<|tools|>/<tool_calls>/<reasoning>/<|tool|>标签,无字段丢失);③smoke-test两kind均PASS;④新建run_tokenize_sft.sh三阶段自治runner(Phase1 convert 16子集并行幂等→Phase2 size-balanced round-robin分shard PPS_SFT=16/PPS_AGENT=4≈107shard 96并发preprocess_data_cm.py --mode content resume+failed→Phase3 finalize清空untokenized_sft_sources.tsv+build_tokenized_mirror.py+gen_data_mapping_md.py --measure+gen_report_data_mapping_html.py+git commit+push);⑤build_tokenized_mirror.py +2 ENTRIES(SFT-2605/Agent-2609 src_dir=/nas_env/full_sft_2605|full_sft_agent_2609 storage=symlink);⑥gen_report_data_mapping_html.py结论/footer改"SFT已分词入镜像";⑦smoke-test端到端PASS(Search_Agent 2jsonl→2parquet→PLAN gen→1shard tokenized→.bin 650MB/.idx 200KB/.json 508B,num_tokens=162707719,num_errors=0,num_timeout_skips=0);⑧修复bug:SFT-2605 --kind sft2609→sft2605(argparse choices={sft2605,agent2609});⑨full runner PID1054237 launched setsid,Phase1 convert进行中(SFT-2605 602/1504+Agent-2609 20/50 parquet,7 converts running,3 Agent subsets已skip幂等);⑩脚本commit e254a4c2e pushed。未完成指令:有(SFT分词runner在跑·异步)→WAITING:1

> [12:29] 唤醒688：防判死心跳轮(上次data commit 11:15=74min>60min阈值,无新运维令)。①复核运维令08:3x刷新两文件DONE:DATA_MAPPING.md 10997B(行2-10=9源storage=symlink指向/nas_env+行1 env14 hardlink+行11-12 SFT-2605/Agent-2609未分词保留,815shards/4473.76B/17.57TB)✓;report_data_mapping_zh.html 20624B(df /nas_train 84%/nas_env 83%,与实测df 12:29一致)✓;②生成器幂等铁证:python3 gen_data_mapping_md.py --out /tmp/DMM_test.md→wc -c 10997B==提交版+diff TEST==REAL+grep SFT-2605/Agent-2609=2行(print的"8852 bytes"=Python len(md)字符数,wc -c=10997字节数,UTF-8 CJK多字节致差异,非缺行)✓;③commit 42bf3a52f已push,git status main...origin/main无ahead/behind✓;④BAIZE_DATA_TASK.md无新运维令(08:3x最高且DONE,其余全📦归档/已闭合)✓;⑤df实测12:29 /nas_train 174T/84%(34T可用) /nas_env 8.2T/83%(1.8T可用)与报告一致✓;⑥体积MEMORY 27.6KB/TASK 32.0KB均≤40KB✓;⑦无未完成指令→本轮仅写心跳防判死+commit/push。未完成指令:无→WAITING:1
> [11:12] 唤醒687：防判死心跳轮(上次data commit 10:03=69min>60min阈值,无新运维令)。①复核运维令08:3x刷新两文件DONE:DATA_MAPPING.md 10997B(行2-10=9源storage=symlink指向/nas_env+行1 env14 hardlink+行11-12 SFT-2605/Agent-2609未分词保留,合计815shards/4473.76B/17.57TB)✓;report_data_mapping_zh.html 20624B(df /nas_train 84%/nas_env 83%,与实测df一致)✓;两文件mtime Oct27 09:56-09:57新鲜✓;②commit 42bf3a52f已push,git status main...origin/main无ahead/behind✓;③BAIZE_DATA_TASK.md无新运维令(08:3x最高且DONE,其余全📦归档/已闭合)✓;④git status无本线未提交改动(其余??属p8/ops/harness/pretrain线,不动)✓;⑤df实测11:12 /nas_train 174T/84%(34T可用) /nas_env 8.2T/83%(1.8T可用)与报告一致✓;⑥体积MEMORY 27.6KB/TASK 32.0KB均≤40KB✓;⑦无未完成指令→本轮仅写心跳防判死+commit/push。未完成指令:无→WAITING:1

> [09:57] 唤醒686：执行运维令08:3x刷新DATA_MAPPING.md+report_data_mapping_zh.html。①git pull(已是最新);②gen_data_mapping_md.py --measure重测10下载目录字节=与缓存完全一致→DATA_MAPPING.md 10997B(逐字节同HEAD,9源storage=symlink指向/nas_env+env14 hardlink+SFT-2605/Agent-2609未分词行11-12保留,815shard/4473.76B/17.57TB);③gen_report_data_mapping_html.py重生成report 20624B(df /nas_train 84%/nas_env 83%实测09:57,timestamp 05:40→09:57刷新);④commit 42bf3a52f+push origin main成功;⑤git status无ahead/behind✓;⑥体积MEMORY 26.9KB/TASK 31.9KB均≤40KB✓;⑦无未完成指令→WAITING:1。未完成指令:无→WAITING:1

> [08:42] 唤醒685：防判死心跳轮(无新运维令,上次commit 07:34=68min>60min阈值)。①复核4条活跃运维令全DONE：13:1x迁移4源→DATA_MAPPING.md行7-10 storage=symlink/状态=镜像完整✓;10:4x报告report_data_mapping_zh.html 20,624B(Oct27 05:40)✓;09:5x分词131/131 DONE✓;08:2x报告report_data_recent_work_zh.html 28,443B(Oct26 09:06)✓;②git fetch无BAIZE_DATA_TASK.md新提交(03:46后未改)✓;③git status无本线未提交改动✓;④df /nas_train 174T/84%(34T可用)+/nas_env 8.2T/83%(1.8T可用)✓;⑤体积自检MEMORY 26.8KB/TASK 31.9KB均≤40KB✓;⑥无未完成指令→WAITING:1。未完成指令:无→WAITING:1

> [07:32] 唤醒684：防判死心跳轮(无新运维令,上次commit 06:25=67min>60min阈值)。①复核4条活跃运维令仍全DONE：13:1x迁移4源→DATA_MAPPING.md行7-10 storage=symlink/状态=镜像完整✓;10:4x报告report_data_mapping_zh.html 20,624B(Oct27 05:40)✓;09:5x分词131/131 DONE✓;08:2x报告report_data_recent_work_zh.html 28,443B(Oct26 09:06)✓;②git status无本线未提交改动✓;③df /nas_train 174T/84%(34T可用) /nas_env 8.2T/83%(1.8T可用)✓;④体积自检 MEMORY 26.3KB/TASK 31.9KB 均≤40KB✓;⑤无未完成指令→WAITING:1。未完成指令:无→WAITING:1

> [06:23] 唤醒683：全量复核轮(无新运维令)。①复核4条活跃运维令全DONE：13:1x迁移4源→DATA_MAPPING.md行7-10 storage=symlink/状态=镜像完整/合计815shard/17,566,770,958,858B/4,473,758,257,769tok(commit ace6fac0b);10:4x报告report_data_mapping_zh.html 20,624B(Oct27 05:40)✓;09:5x分词131/131 DONE(10源全镜像完整);08:2x报告report_data_recent_work_zh.html 28,443B(Oct26 09:06)✓;②git status无本线未提交改动(git status --porcelain grep本线路径=空)✓;③df /nas_train 174T/84%(34T可用,较迁移前177T/86%释放~3TB)+/nas_env 8.2T/83%(1.8T可用);④体积自检MEMORY 25.4KB/TASK 31.9KB均≤40KB✓;⑤★纠正WAITING:0→WAITING:1(无未完成指令,按harness/pretrain惯例睡30min省token,避免每60s空唤醒烧token);⑥心跳+日报+commit。未完成指令:无→WAITING:1

> [05:2x] 唤醒682：★ufw_en迁移COMPLETE + 4源迁移全部完成。①ufw_en迁移：text/源文件删除(deleted parquet text source files)+tokenized/ 96 hardlink删除→build_tokenized_mirror.py重建96 per-file symlink指向/nas_env/full_ufw_en/(ufw_en_train_s{0..31}.{bin,idx,json}=96 files);②INDEX.tsv rebuild: ufw_en行 storage=hardlink→symlink, triplet=OK, inode_ok=32/32, bytes=3,222,004,397,626;③DATA_MAPPING.md regen(gen_data_mapping_md.py): ufw_en行 bytes=3,222,004,397,626/GB=3001/storage=symlink/状态=镜像完整, 合计17,566,770,958,858B/4,473,758,257,769tok/815shard;④★gen_report_data_mapping_html.py新增报告生成脚本(从DATA_MAPPING.md+INDEX.tsv+df→自包含HTML,5节:总览KPI+磁盘/逐源列表/重点10源/未分词源/结论);⑤report_data_mapping_zh.html重生成20624B: ufw_en行 storage=symlink/bytes=3,222,004,397,626, 全表9 symlink+1 hardlink(env14), 旧值3,215,632,049,746已清除;⑥★NFS缓存踩坑: gen_data_mapping_md.py首跑输出stale(hardlink/旧bytes),因NFS attr-cache返回旧INDEX.tsv→重跑后correct; gen_report首次grep也读stale HTML→Python fresh read确认correct;⑦commit ace6fac0b `data migrate: ufw_en 32 shard 迁移 /nas_env 完成` pushed;⑧df实测/nas_train 174T已用/34T可用(84%,较迁移前177T/86%释放~3TB)+/nas_env 8.2T已用/1.8T可用(83%);⑨4源迁移全部完成: ufw_en(32)+l1_en_hq(94)+zh(4)+AICC(1)=131shard≈4.05TB→/nas_env, 连同此前5源(574shard/4.24TB), /nas_env共承载9源/705shard/~8.3TB。未完成指令:无→WAITING:0

> [03:0x] 唤醒681：复核+归档轮（无新运维令）。①★复核最高优先14:4x令=DONE：git log 86431cfb4 `data report: 加入SFT-2605+Agent-2609到DATA_MAPPING.md+报告删第4节`；实测验证 SFT-2605=1504 jsonl/du -sb=318,990,486,183 B(0 .bin/.idx/.json)→DATA_MAPPING.md 行11=未分词✓；Agent-2609=50 jsonl/du -sb=54,220,373,384 B(0 .bin/.idx/.json)→行12=未分词✓；报告 report_data_mapping_zh.html 行11-12未分词+旧第4节「其余状态源」已删(现4节:总览/逐源列表/10已镜像源/结论,节号顺延)✓；untokenized_sft_sources.tsv 侧车✓。②14:4x块归档→ARCHIVE_OPERATOR_DATA.md(原文+执行结论)+BAIZE_DATA_TASK.md 留1行📦指针。③08:2x报告 report_data_recent_work_zh.html 28,443B EXISTS✓。④ufw_en迁移仍BLOCKED：df /nas_env=1852G可用<ufw_en需3.0T(du -sh=3.0T)，s17已稳定(非移动靶)，需运维决定(腾空间/暂留hardlink/删旧数据)。⑤git status=main...origin/main 无ahead/behind✓；df /nas_train 86%(31T) /nas_env 82%(1.85T)；MEMORY 22.7KB/TASK~31KB 均≤40KB✓。⑥心跳+日报+commit。未完成指令:无→WAITING:0

> [02:5x] 唤醒680：①复核22:0x坏shard修复=DONE(commit 1cfb5e7dd data fix:,证据bad_shard_...txt §8-9,DATA_MAPPING.md env14行=镜像完整110/110/8,999,055,538,432B/2,237,073,612,082tok,LEDGER §7.2已记录);②s17稳定性复测=STABLE(mtime 02:31:24,size 113,238,901,184B,8s间隔二次stat完全一致,不再是移动靶);③★发现ufw_en迁移新阻塞=/nas_env仅1.85T可用(df -BG=1852G)<ufw_en需3.0T(du -sh=3.0T)⇒空间不足无法迁移,需运维决定(腾空间/暂留hardlink/删旧数据);④tokenization确认全DONE(log:131/131 failed:0 END 10:33:21,lock释放);⑤体积维护:MEMORY_DATA.md 44,557B→22,204B(唤醒674-677/661-665转📦+删唤醒650及以下旧📦)+BAIZE_DATA_TASK.md 22:0x块归档ARCHIVE_OPERATOR_DATA.md留1行指针(34.7KB→~33KB);⑥日报补680。未完成指令:无→WAITING:0

> [02:0x] 唤醒679：✅22:0x坏shard修复DONE。①retok完成验证(.idx max_ptr=118,227,700,960<bin=118,227,705,972,num_tokens29.56B=bin/4逐字节自洽,32.85M docs不变,较原始30.62B降1.067B/-3.5%并行切分边界差异);②原子替换(rm tokenized旧硬链→mv RETOK→text正名→build_tokenized_mirror.py重建hardlink links=2+INDEX.tsv 815shard inode_ok=815→gen_data_mapping_md.py刷新DATA_MAPPING.md env14 8,929,852,999,497→8,999,055,538,432B/2,238,140,710,284→2,237,073,612,082tok,合计4474.83→4473.76B/17.47→17.56TB;★NFS attr-cache踩坑首次run读旧缓存,二次fresh process读新);③report_data_mapping_zh.html全量更新(env14行+ufw_en移动靶GB2977→2995+总计+df 86%/82% 02:0x+footer);④DATA_LEDGER §7.2待完成→已完成+§7表env14/合计cell更新;⑤证据文件§8-9(retok结果+原子替换+复验+结论);⑥commit data fix:。未完成指令:无→WAITING:0
> [00:3x] 唤醒678：①3源迁移FINALIZE(l1_en_hq/zh/AICC)：build_tokenized_mirror.py ENTRIES L32-34改src_dir→/nas_env/full_*+storage→symlink→rerun重建INDEX.tsv(815shard全triplet=OK inode=OK,3源storage=symlink,ufw_en/env14仍hardlink)+gen_data_mapping_md.py刷新DATA_MAPPING.md(指纹size=2953 hash=7f2a09fb2920 mtime=00:34,3源evidence列symlink,ufw_en bytes 2.98→3.20TB移动靶,合计17.26→17.47TB)+report_data_mapping_zh.html全量更新(2表3源hardlink→symlink,ufw_en GB 2777→2977,总17.26→17.47TB,df 85%/82% 00:35,footer+结论同步);②retok监控:200/512 parquet(39%),12.95B tokens@3222s,RETOK bin 51.8GB/122.5GB(42%),ETA~01:48;③ufw_en仍hardlink DEFERRED(s17移动靶)。待commit+push。未完成指令:有(retok在跑·异步阻塞§8)→WAITING:1
> 📦 唤醒677(10-27 23:4x)原文归档 → daily-memories-data/2026-10-27.md（22:0x坏shard定性=.bin截断49GB/40%+裁决重分词启动PID352806/48worker ETA~01:50;13:1x迁移run4复核FAILED/ufw_en s17/s21移动靶;3稳定源已拷/nas_env未finalize,详见日文件）
> 📦 唤醒676(10-26 22:1x)原文归档 → daily-memories-data/2026-10-26.md（13:1x迁移run3=FAILED:ufw_en s17/s21移动靶跨NFS在写verify必MISMATCH;run4策略先迁3稳定源ufw_en deferred;脚本改stability guard,详见日文件）
> 📦 唤醒675(10-26 20:5x)原文归档 → daily-memories-data/2026-10-26.md（14:4x=DONE commit86431cfb4;13:1x迁移run2=FAILED du -sb跨NFS误报→改stat逐文件校验;run3重启拷s17+s21,详见日文件）
> 📦 唤醒674(10-26 19:3x)原文归档 → daily-memories-data/2026-10-26.md（14:4x复核DONE;13:1x迁移run1=FAILED rsync rc=23 NFS temp-file rename race;ufw_en 31/32.bin s0 MISSING+s17 PARTIAL,详见日文件）
> [17:0x] 唤醒673：核查全部活跃指令状态（无新运维令，复核672交付+盘点在跑异步任务）→ ①14:4x已由唤醒672交付并commit/push：实测验证SFT-2605=1504jsonl/318990486183B+Agent-2609=50jsonl/54220373384B，tokenized镜像无对应.bin/.idx→未分词判定正确；DATA_MAPPING.md行11-12未分词+报告report_data_mapping_zh.html删第4节(现4节:总览/逐源列表/10已镜像源/结论)+git status无ahead/behind。②★**修正唤醒672的遗漏**：13:1x迁移4源→/nas_env**仍在跑**（672误报"未完成指令:无"）！证据：`migrate_4sources_to_nas_env.sh` PID1170559(ppid=1守护,etimes9664s≈2.68h)+rsync PID1170713(RN态)在跑，ufw_en→full_ufw_en 85.3%(2,651,505,982,786B/3,108,332,056,695B)@~280MB/s,bwlimit300000KiB/s；full_ufw_en 22/32 shard完整+5 partial(s0/s6/s7/s8/s9未拷贝)，l1_en_hq/zh/AICC 3源未开始；wrapper(/tmp/migrate_4sources_to_nas_env.log)自动 rsync+校验+rm text/+rm tokenized hardlink名(释放/nas_train)，但**finalize需rsync完后由agent做**：改build_tokenized_mirror.py ENTRIES(31-34行src_dir→/nas_env/full_*,storage→symlink)+rerun(重建per-file symlink+INDEX.tsv)+gen_data_mapping_md.py --measure(刷新DATA_MAPPING.md storage=symlink)+report refresh+commit data migrate:；ETA ufw_en~18:00+其余3源~19:10。/nas_env余量3.4T>剩余1.68T需求→够装。③df实测/nas_train 177T/31T(86%)+/nas_env 6.6T/3.4T(66%,因ufw_en迁移在填充,较672报的54%增长)。④轻归档：MEMORY47KB/TASK46.5KB均>40KB→搬已闭合22:3x诊断块+12:5x⓪①②+18:2x删32块到ARCHIVE_OPERATOR_DATA.md(留1行指针),压缩流水666-671到daily-memories-data/2026-10-26.md。未完成指令:有(13:1x迁移在跑·异步阻塞§8)→WAITING:1

> [16:3x] 唤醒672：执行运维令14:4x（SFT-2605+Agent-2609加入映射表+报告删第4节·用户直令·最高优先）→ ①核查分词状态:tokenized镜像无SFT对应.bin/.idx/.json→判定未分词(不伪造镜像完整);②实测:SFT-2605=1504jsonl/318990486183B(297GB,no_think855:Chinese-general50/Code300/IF20/Knowledge80/Math300/Multi-lang-Knowledge50/Multi-lang-Math55+think649:Chinese-general50/Code279/IF20/Knowledge50/Math250),Agent-2609=50jsonl/54220373384B(50GB,Code_Agent7/General_Agent32/Search_Agent2/Tool_Use9);③新建untokenized_sft_sources.tsv+改gen_data_mapping_md.py(load_untokenized+--untokenized-tsv,A节追加2行未分词,分词目录=—,下载字节计入合计)→DATA_MAPPING.md重生成103行/11001B(★字节数变化:10093B→11001B,+908B;合计815shards/4474.83B/17.26TB分词产物/下载13021192793759B=12127GB,未分词小计2源1554jsonl/373210859567B=347.6GB,幂等run1==run2=True);④报告report_data_mapping_zh.html更新(★字节数变化:25112B→20434B,-4678B;总览数据源10→12+下载12647.98→13021.19GB+磁盘86%/54%,逐源列表加行11(SFT-2605未分词)+12(Agent-2609未分词)+合计13021192793759B/12127GB,删第4节其余状态源(32已删除表+状态汇总),5→4结论(加SFT未分词说明),footer更新);⑤HTML校验tag平衡(table2/tr26/div42)。commit data report:。未完成指令:无→WAITING:1
> [13:40] 唤醒671：复核运维令10:4x交付物。证据链：①report_data_mapping_zh.html已落盘28076B(mtime 12:29,自包含中文HTML,5节:总览/逐源列表/10个已镜像源/其余状态源(32已删除)/结论,数字溯源到DATA_MAPPING.md L16-L99+INDEX.tsv+df)；②git log 76940c627@12:31 "data report: 围绕DATA_MAPPING.md写数据情况列表报告 report_data_mapping_zh.html 28KB 5节 815shards/4474.83B/17.26TB 全镜像完整"+fa782486f@13:22 "迁移后刷新DATA_MAPPING.md+report_data_mapping_zh.html并提交推送"；③git status -sb=main...origin/main无ahead/behind,本线无未提交文件(其余M/??属harness/pretrain/vision/p8线,不动)；④df实测/nas_train 176T已用/32T可用(86%)+/nas_env 4.2T已用/5.8T可用(43%)与报告§总览一致；⑤DATA_MAPPING.md A节10行全镜像完整(815shards/4474.83B/17.26TB/下载12647.98GB)+B节32行已删除(实占~471.6KB)。★结论：全部活跃指令(10:4x报告+09:5x分词并发MOOT+08:2x报告+22:3x诊断+18:5x映射/磁盘batch1+18:2x删32)均已交付/闭合,无未完成指令。仅磁盘batch2 PENDING运维裁决(0实占tidy,非阻塞)。未完成指令:无→WAITING:1
> 📦 唤醒670(10-26 12:2x)原文归档 → daily-memories-data/2026-10-26.md（10:4x报告report_data_mapping_zh.html 28KB 5节交付,数字溯源DATA_MAPPING.md,详见日文件）
> 📦 唤醒669(10-26 11:08)原文归档 → daily-memories-data/2026-10-26.md（09:5x提高并发令复核=MOOT,分词09:43:35早完成,详见日文件）
> 📦 唤醒668(10-26 09:5x)原文归档 → daily-memories-data/2026-10-26.md（★分词09:43:35 RUN COMPLETE 131/131/1.18T/4.05TB+18:5x wrap-up全链mirror rebuild815shard+DATA_MAPPING刷新+DATA_LEDGER,详见日文件）
> 📦 唤醒667(10-26 08:13)原文归档 → daily-memories-data/2026-10-26.md（22:3x三度复核:done95→97恢复确认,非卡死自证,处置不杀,详见日文件）
> 📦 唤醒666(10-26 07:24)原文归档 → daily-memories-data/2026-10-26.md（22:3x二度复核:/proc/io铁证非卡死,supervisor计数artifact,真ETA~2-3.5h,详见日文件）

> 📦 唤醒665(10-26 06:37)原文归档 → daily-memories-data/2026-10-26.md（22:3x深度诊断:done95/131 FLAT确诊非卡死=单核BPE慢412K tok/s/proc ETA~2h,处置不杀,详见日文件）
> 📦 唤醒664(10-26 05:45)原文归档 → daily-memories-data/2026-10-26.md（22:3x监测点6:done95/131 FLAT三重铁证非卡死finalize在即,详见日文件）
> 📦 唤醒663(10-26 04:57)原文归档 → daily-memories-data/2026-10-26.md（22:3x监测点5:done95/131 FLAT三重铁证非卡死WIP 3.14TB,详见日文件）
> 📦 唤醒662(10-26 03:44)原文归档 → daily-memories-data/2026-10-26.md（22:3x监测点4:/proc/io铁证非卡死@1.6MB/s,在写2.87TB,处置不杀,详见日文件）
> 📦 唤醒661(10-26 02:34)原文归档 → daily-memories-data/2026-10-26.md（22:3x监测点3:done95/131 /proc/io铁证非卡死in-progress 2.60TB,处置不杀,详见日文件）
> 📦 唤醒660(10-26 01:16)原文归档 → daily-memories-data/2026-10-26.md（22:3x监测点2:done94→95@00:15,1 shard完工,36进程健康,处置不杀,详见日文件）
> 📦 唤醒657(10-25 21:2x)原文归档 → daily-memories-data/2026-10-25.md（18:5x③收尾:cleanup_batches侧车+gen_data_mapping_md.py加清理记录,详见日文件）
> 📦 唤醒659(10-26 00:05)原文归档 → daily-memories-data/2026-10-26.md（22:3x停顿诊断:场景③非卡死,supervisor只计finalize故假停,处置不杀不重启,详见日文件）
> 📦 唤醒658(10-25 22:46)原文归档 → daily-memories-data/2026-10-25.md（心跳巡检:分词94/131健康在写,全部运维令已交付,85M76.5%,详见日文件）

> 📦 唤醒656(10-25 20:1x)原文归档 → daily-memories-data/2026-10-25.md（18:5x执行:gen_data_mapping_md.py幂等+磁盘清理batch1删78staging,详见日文件）

> 📦 唤醒655(10-25 18:3x)原文归档 → daily-memories-data/2026-10-25.md（18:2x删32不可映射staging:留档+rm+校验,终裁结案,详见日文件）

> 📦 唤醒654(10-25 17:23)原文归档 → daily-memories-data/2026-10-25.md（监控巡检:分词92/131健康,镜像布局commit7896810a3,详见日文件）

> 📦 唤醒653(10-25 16:0x)原文归档 → daily-memories-data/2026-10-25.md（监控巡检:分词61/131,calibration实测W96=11.3M tok/s,详见日文件）
> 📦 唤醒652(10-25 14:5x)原文归档 → daily-memories-data/2026-10-25.md（建tokenized/镜像布局716shard+确认分词在跑,详见日文件）
> 📦 唤醒651 原文已归档 → daily-memories-data/2026-10-25.md（运维令§prune不可映射早期分词234文件释放3.69TiB+盘点报告升v3,详见日文件）
> 唤醒632（2026-10-24 10:50）运维质询回答+提速：①**分词为何5worker**=旧fullsource(PID2557971,已退出)串行1shard/进程,剩5shard→5进程→load26/224;09:39已升级run_tokenize_env14_parallel_finish.sh(PID3450586):**5shard×13workers=65并发**,load→71;shard进度:2024-51=500/512(98%)2025-13=250/512(49%)2025-18=250/512(49%)2025-21=300/512(59%)2025-26=300/512(59%);.bin=78-84G;ETA~1-1.5h;不重启(丢399GB partial).②**85M线路**=/proc/171042/environ:https_proxy=http://172.19.92.25:13128+无HF_ENDPOINT→**92.25+hf.co直连✓**.③**85M提速**:旧hf_transfer=1串行~19MB/s→kill+重启parallel-16(hf_transfer=0,16workers,PID581957):8文件并行,**~24MB/s**(+26%);8637/12124=71.3%,ETA~6.9天.④迁移NOT READY(105/110).disk:/nas_train 30T(86%)/nas_env 9.6T(4%);load71/224,1785G RAM.📦体积：TASK=31.1KB/MEMORY=26.5KB(无归档)

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