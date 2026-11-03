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
PHASE:        🟢运维令10-31 web search调研HF长上下文+agentic数据集.报告v6已交付+已commit+push
已完成:       ✅A.LC+Agentic调研报告v6(report_data_lc_agentic_survey_zh.html 115558B/47table/0script/19+18候选/80 HF链接/36unique)+生成器(gen_lc_agentic_survey_report.py 幂等);✅B.v6新增3个HF核实数据集(SWE-smith-trajectories/MIT/HTTP200 + harborframework/terminal-bench-2.1/Apache-2.0/HTTP200 + ghostcc3/mix-context-post-training-128k/MIT/HTTP200);✅C.85M下载持续运行;✅D.报告全量验证(7节/0script/0CDN/0外链/幂等OK/47table平衡/0未闭合标签)
当前动作:     唤醒1150(2026-11-04 00:4x):运维令10-31交付物例行健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(全href=huggingface.co)/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/HTMLParser 0err 0未闭合;②generator=95012B(幂等:重跑md5=7803ee89db87f1cd35310f3bfb84aa08,git diff为空=与提交一致);③git synced(git fetch OK,##main...origin/main,0ahead/0behind,commit 66807cdaa已push,data线clean,working tree仅harness线改动非本线);④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈29KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
下一步:       下轮唤醒:①查85M下载进度(是否已完成);②待运维批准后执行下载(P0:whole-books+SWE-smith+Nemotron-Terminal-Corpus+SWE-rebench;P2新增:SWE-smith-trajectories;P3新增:mix-ctx-128k/terminal-bench-2.1)
阻塞:         无
ERROR_COUNT:  11
未完成指令:   无(调研报告v6已交付+验证完成)
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-04 00:4x] 唤醒1150：运维令10-31交付物例行健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/HTMLParser 0err 0未闭合;②generator=95012B(幂等:重跑md5=7803ee89db87f1cd35310f3bfb84aa08,git diff为空=与提交一致);③git:fetch OK(##main...origin/main,0ahead/0behind,commit 66807cdaa已push,data线clean,working tree仅harness线改动非本线);④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈29KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 00:2x] 唤醒1149：运维令10-31交付物例行健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(全href=huggingface.co)/47<table>=47</table>平衡✓/7节sec1-7齐;②generator=95012B(幂等);③git:fetch+pull--rebase--autostash OK(##main...origin/main,0ahead/0behind,commit ab6f89572已push,data线clean,working tree仅pretrain/ZhuLong线改动非本线);④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈28KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 00:0x] 唤醒1148：运维令10-31交付物例行健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链/80链接全HF/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/HTMLParser 0err 0未闭合/≥32K×76/≥128K×117/未核到×50/gated×52/SWE-bench×74/Terminal×112;②generator--check-idempotent PASS(91300 bytes✓);③git:fetch+pull--rebase--autostash OK(##main...origin/main,0ahead/0behind,commit ab6f89572已push,data线clean,working tree仅pretrain/ZhuLong线改动非本线);④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈27KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 23:4x] 唤醒1147：运维令10-31交付物例行健康巡检全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/7节sec1-7齐/80HF链接;②generator幂等OK(91300 chars=115558 bytes,--check-idempotent PASS,与committed文件逐字符一致✓);③git synced(##main...origin/main,0ahead/0behind,commit ab6f89572已push,data线clean);④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T),/nas_env8.3T/84%(1.7T);⑥TASK=27958B/MEMORY≈27KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 22:0x] 唤醒1146：运维令10-31交付物例行健康巡检全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/80HF链接;②generator重跑输出115558B逐字节一致(git diff空=真幂等✓)+--check-idempotent PASS;③git synced(##main...origin/main,0ahead/0behind,commit ab6f89572已push,data线clean);④85M下载:pgrep未见hf download进程(LLaVA-OneVision-1.5-Mid-Training-85M目录36381文件/最后活动~11-01,可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T),/nas_env8.3T/84%(1.7T);⑥TASK=27958B/MEMORY≈27KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 21:2x] 唤醒1145：运维令10-31交付物深度复验+HF API实查→①HF API核实23个关键repo_id(代理172.19.92.25):22个HTTP 200 OK(whole-books/prolong-data-512K/NExtLong/LongBlocks/common-pile(arxiv+gutenberg)/pg19/LongData-Corpus/Nemotron-Terminal-Corpus/SWE-rebench/Orchard/Nemotron-Cascade-RL-SWE/SkyRL/AgentTrove/SWE-ZERO-12M/RULER-llama3-1M/LongAlign-10k/LongWriter-6k/InfLLM-V2-data-5B/to-tool-call/Nemotron-RL-Agentic-SWE-Pivot/Nemotron-Cascade-SFT-SWE/LongBench-v2)+1个系列子URL(kl3m-data系列);②另补查16个补充repo_id(terminal-bench→harborframework/SWE-smith→SWE-bench/Nemotron-v1/v2→nvidia/BFCL→gorilla-llm/InfiniteBench/LongBench/pile/fineweb等全OK);③report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>平衡✓/7节齐/80HF链接/49未核到/14gated/19处13-gram/3处193295;④generator幂等OK(重跑git diff空✓);⑤临时调研文件清理(8_*.py+6_*.json+2_*.log删);⑥git:data线clean(commit ab6f89572已push,[ahead 1]=harness线非本线)→任务已交付,心跳WAITING=1
> [11-03 20:00] 唤醒1144：运维令10-31交付物复验全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/HTMLParser 0unclosed 0stack_remaining/80 HF链接;②generator --check-idempotent OK(91300B✓);③git synced(##main...origin/main,0 ahead/0 behind,commit ab6f89572);④TASK=27958B/MEMORY≈24KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 19:26] 唤醒1143：运维令10-31交付物复验全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/HTMLParser 0unclosed 0mismatch/7节sec1-7齐/80 HF链接；②generator --check-idempotent OK(91300B✓)；③git synced(##main...origin/main,0 ahead/0 behind,commit ab6f89572)；④85M下载:pgrep未见hf download进程(可能已完成或需运维确认);⑤df:/nas_train179T/87%(29T),/nas_env8.3T/84%(1.7T);⑥TASK=27958B/MEMORY≈24KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 18:49] 唤醒1142：运维令10-31交付物复验全PASS→①report=115558B(≥25KB✓)/0<script>/0 ext-src/href域仅huggingface.co(0非HF外链)/47<table>=47</table>平衡✓/HTMLParser 0err 0unclosed/7节§1~§7齐(§1 TL;DR·§2检索方法·§3A类主表·§4B类主表·§5污染·§6下载方案·§7诚实条款)；②generator --check-idempotent OK(91300B✓)；③git synced(##main...origin/main,0 ahead/0 behind,report commit ab6f89572)；④df:/nas_train179T/87%(29T),/nas_env8.3T/84%(1.7T)；⑤TASK=27958B/MEMORY=23635B(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 18:30] 唤醒1141：运维令10-31交付物完整复验全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0外链(80 HF链接·0非HF)/47<table>=47</table>平衡✓/HTMLParser严格检查unclosed:0 mismatch:0 PASS✓/7节§1~§7全齐/49「未核到」/52 gated/106 SWE-bench·TB污染/60 长文档占比；②generator --check-idempotent OK(91300B逐字节不变✓)；③git synced(##main...origin/main,0 ahead/0 behind,commit ab6f89572)；④TASK=27958B/MEMORY≈22KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 17:39] 唤醒1140：运维令10-31交付物例行复验全PASS→①report=115558B(≥25KB✓)/0<script>/47<table>=47</table>平衡✓/generator --check-idempotent OK(91300B逐字节不变✓)；②git synced(##main...origin/main,0 ahead/0 behind)；③85M下载运行中(PID212578 alive,etimes≈32089s≈9h,43T/36377files)；④df:/nas_train179T/87%(29T),/nas_env8.3T/84%(1.7T)；⑤TASK=27958B/MEMORY≈22KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 16:42] 唤醒1139：运维令10-31交付物再次复验全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/80链接全huggingface.co·0非HF外链/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节§1~§7齐(TL;DR·检索方法·A类主表·B类主表·污染·下载方案·诚实条款)；②generator --check-idempotent OK(91300bytes逐字节不变✓)；③git synced(HEAD=origin/main=ee5334e2c,0 ahead/0 behind)→任务已交付,心跳WAITING=1
> [11-03 16:05] 唤醒1138：运维令10-31交付物独立复验全PASS→①report=115558B(≥25KB✓)/0<script>/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/HTMLParser 0err·0未闭合/0非HF外链/0CDN；②generator --check-idempotent OK(逐字节不变✓)；③git synced(0 ahead/0 behind origin/main,commit ab6f89572)→任务已交付,心跳WAITING=1
> [11-03 15:46] 唤醒1137：运维令10-31交付物独立复验全PASS→①report=115558B(91300chars,≥25KB✓)/0<script>/0CDN/0外链(80链接全huggingface.co·36unique·0非HF)/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/HTMLParser 0err·0未闭合·剩余栈EMPTY/7节§1~§7齐(§1 TL;DR·§2检索口径·§3 A类主表·§4 B类主表·§5污染去重·§6下载方案·§7诚实条款)/77处32K占比·143处128K·132处SWE-bench·81处TerminalBench·52处gated·52处未核到；②generator --check-idempotent OK(91300chars·output文件逐字节不变✓)；③git diff HEAD 空(report+generator与已提交版ab6f89572完全一致)→git synced(0 ahead/0 behind origin/main)；④TASK=27958B/MEMORY≈21KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 14:5x] 唤醒1136：运维令10-31报告v5→v6增强→①web search复查HF发现3个v5未覆盖数据集(SWE-bench/SWE-smith-trajectories/MIT/1K-10K/SWE轨迹+SFT/RL · harborframework/terminal-bench-2.1/Apache-2.0/2026-09-14/最新官方TB评测集本体 · ghostcc3/mix-context-post-training-128k/MIT/128K LC post-training packed)；②curl HF API(带proxy 92.25)逐条核实→3个HTTP 200确认+license/downloads/lastModified/tags核到；③生成器(gen_lc_agentic_survey_report.py)+3数据集条目(LONG_CONTEXT +1=19,AGENTIC +2=18)+污染表TB升级为TB2.1高危+TL;DR补充候选3条+下载方案表+3行+hf命令+3条；④重生成→全量验证PASS=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡/HTMLParser严格检查0未闭合0误配/7节§1~§7齐/80 HF链接36unique/3新数据集全在/50「未核到」52「gated」✓；⑤generator --check-idempotent OK(91300chars=115558bytes,逐字节不变✓)；⑥85M:PID212578 alive✓；⑦git synced→commit data survey: v6→push→心跳WAITING=1
> [11-03 12:47] 唤醒1135：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/0CDN/0外链/44<table>=44</table>平衡✓/div 50=50平衡✓/7节§1~§7✓/33 unique HF数据集链接/34「未核到」✓/meta×2为void元素非失衡;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(hf download mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M)✓;④git synced(##main...origin/main,data线clean✓,仅ZhuLong/Harness线改动非本线);⑤TASK=27958B/MEMORY≈19KB(均<40KB无需归档)→任务已交付,心跳WAITING=1

> [11-03 12:27] 唤醒1134：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/div 50=50平衡✓/7节§1~§7✓/74 HF链接/34「未核到」✓/0CDN;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈13385s≈3.7h)✓,parquet12017/8.incomplete;④git synced(##main...origin/main,data线clean✓,仅ZhuLong线改动非本线);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈21KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 11:33] 唤醒1133：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/div 50=50平衡✓/7节§1~§7✓/76 HF链接/34「未核到」✓/0CDN;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈10168s≈2.8h)✓,parquet11996/8.incomplete;④git synced(##main...origin/main,data线clean✓,仅ZhuLong线改动非本线);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈20.5KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 11:13] 唤醒1132：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/7节§1~§7✓/74 HF链接/34「未核到」✓/0CDN;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈8969s≈2.5h)✓,parquet20783/8.incomplete;④git synced(##main...origin/main,data线clean✓,仅ZhuLong线改动非本线);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈19.8KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 10:52] 唤醒1131：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/7节§1~§7✓/74 HF链接/34「未核到」✓/0CDN;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈7678s≈2.1h)✓,parquet11984/12126=98.8%,8 .incomplete;④git synced(##main...origin/main,data线clean✓,仅ZhuLong线改动非本线);⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈19.8KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 10:05] 唤醒1130：运维令10-31交付物例行复核全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/7节§1~§7✓/33 unique HF链接/34「未核到」✓/0CDN;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈4881s≈1.4h)✓;④git synced(##main...origin/main,data线clean✓);⑤df:/nas_train179T/86%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥MEMORY>40KB→归档唤醒1065-1106流水→daily-memories-data/2026-11-03.md,MEMORY 41KB→19KB;⑦TASK=27958B(<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 09:09] 唤醒1129：运维令10-31交付物深度复验全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/HTMLParser严格tag-balance检查=unclosed:none mismatch:0 RESULT:PASS✓/7节§1~§7全在✓/0CDN/0外链(仅2条内网proxy)/74 huggingface.co链接/34「未核到」✓;②generator --check-idempotent OK(84252B,输出逐字节不变✓);③git synced(##main...origin/main,report最后commit=46998fb11@11-02 07:07 v5,本线无未提交改动);④df:/nas_train178T/86%,/nas_env8.3T/84%;⑤TASK=27958B/MEMORY≈39.5KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 08:50] 唤醒1128：运维令10-31交付物健康巡检全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/74 HF链接/34「未核到」✓;②generator --check-idempotent OK(84252B✓);③85M:PID212578 alive(etimes≈394s≈6.5min,新重启),parquet11946/12126=98.6%(+14 vs唤醒1127),8 .incomplete;④git synced(##main...origin/main✓,仅vision/ZhuLong线改动非本线);⑤df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~39KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 08:1x] 唤醒1127：运维令10-31交付物健康巡检全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/74 huggingface.co链接(33 unique)/34「未核到」✓;②generator --check-idempotent OK(84252B✓);③85M:PID3389173 alive(etimes≈2545s≈42min),parquet11932/12126=98.4%(+464 vs唤醒1088),8 .incomplete;④git synced(##main...origin/main✓,仅ZhuLong线改动非本线);⑤df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~39KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-03 07:4x] 唤醒1126：运维令10-31交付物复验全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/7节§1~§7✓/74 HF链接/0CDN/34「未核到」✓/48 gated/58 SWE-bench/54 Terminal-Bench;②generator重跑→106569B一致(幂等✓)+--check-idempotent OK(84252chars);③85M:PID3389173 alive(hf download mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M,ppid=2668156)✓;④git synced(##main...origin/main,commit46998fb11,仅ZhuLong线改动非本线);⑤df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY<40KB(均无需归档)→任务已交付,心跳WAITING=1
> [11-03 07:0x] 唤醒1125：运维令10-31交付物复验全PASS→①report=106569B(≥25KB✓)/0<script>/44<table>=44</table>平衡✓/7节sec1~sec7✓/33 unique HF链接/0CDN/34「未核到」✓;②generator --check-idempotent OK(84252B)+重跑输出无git diff(真幂等✓);③85M:PID2668156 alive(hf download mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M)✓;④git synced(##main...origin/main,commit46998fb11,仅ZhuLong线文件改动非本线);⑤TASK=27958B/MEMORY<40KB(均无需归档)→任务已交付,心跳WAITING=1
> [11-03 06:30] 唤醒1124：运维令10-31交付物健康巡检全PASS→①report=106569B/0<script>/44<table>=44</table>平衡✓/7节/74 HF链接/0非HF链接/0CDN;②generator--check-idempotent OK(84252B);③85M:PID4174877 alive(etimes≈50680s≈14.1h)✓;④df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑤git synced(##main...origin/main,commit 46998fb11,仅ZhuLong线文件改动非本线);⑥TASK=27958B/MEMORY~39KB(均<40KB无需归档)→心跳WAITING=1
> [11-03 06:08] 唤醒1123：运维令10-31交付物健康巡检全PASS→①report=106569B/0<script>/44<table>=44</table>平衡✓/7节/0非HF链接/0CDN;②generator--check-idempotent OK(84252B);③85M:PID4174877 alive(etimes≈49506s≈13.8h)✓;④df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑤git synced(##main...origin/main,commit 46998fb11,仅ZhuLong线文件改动非本线);⑥TASK=27958B/MEMORY~39KB(均<40KB无需归档)→心跳WAITING=1
> [11-03 05:49] 唤醒1122：运维令10-31交付物复核全PASS→①report=106569B/0<script>/44<table>平衡/7节sec1~7/0非HF链接/0CDN;②generator重跑产出逐字节一致(git diff空=真幂等);③git synced(##main...origin/main,commit 46998fb11已push);④TASK=27958B/MEMORY=40070B(均<40KB)→任务已交付,心跳WAITING=1
> [11-03 05:31] 唤醒1121：运维令10-31交付物全量复核全PASS→①report=106569B(≥25KB✓)/0<script>/0<link>/74链接全HF(0非HF)/44<table>=44</table>平衡✓/50<div>=50</div>平衡✓/HTMLParser 0err/7节sec1~sec7齐/≥32K×37/≥128K×36/奖励信号×18/gated×48/未核到×34/SWE-bench×66/TerminalBench×54/0CDN;②generator --check-idempotent OK(84252B✓);③git synced(##main...origin/main,data线clean✓,commit 46998fb11);④MEMORY=39440B(<40KB无需归档)→任务已交付,心跳WAITING=1

> [11-03 03:1x] 唤醒1119：运维令10-31交付物全量复核全PASS→①report=106569B(≥25KB✓)/0<script>/HTMLParser parse_ok/44<table>=44</table>平衡✓/7节sec1~sec7齐/74链接全huggingface.co(0非HF)/34「未核到」/0CDN;②generator --check-idempotent OK(84252bytes✓);③git synced(##main...origin/main,data线clean✓,commit 46998fb11);④MEMORY=38716B(<40KB无需归档)→任务已交付,心跳WAITING=1

> [11-03 02:55] 唤醒1118：运维令10-31交付物全量复核全PASS→①report=106569B(≥25KB✓)/0<script>/HTMLParser 0errors/44<table>=44</table>平衡✓/7节§1~§7齐/74 HF链接/34「未核到」/0CDN;②generator --check-idempotent OK(84252bytes✓);③pretrain训练运行中(torchrun alive✓);④git synced(##main...origin/main,data线clean✓,commit 46998fb11);⑤df:/nas_train178T/86%(30T),/nas_env8.3T/84%(1.7T);⑥MEMORY=38241B(<40KB无需归档)→任务已交付,心跳WAITING=1

> [11-03 02:22] 唤醒1117：运维令10-31交付物全量复核全PASS→①report=106569B(≥25KB✓)/0<script>/HTMLParser 0unclosed 0errors/44<table>=44</table>平衡✓/7节§1~§7齐/74链接全huggingface.co(0非HF)/34「未核到」/0CDN;②generator --check-idempotent OK(84252chars✓);③85M:PID4174877 alive(etimes≈35953s≈10h)✓;④git synced(##main...origin/main,data线clean✓,commit 46998fb11);⑤df:/nas_train178T/86%(30T),/nas_env8.3T/84%(1.7T);⑥TASK=27958B/MEMORY~37KB(均<40KB无需归档)→任务已交付,心跳WAITING=1

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
## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污�