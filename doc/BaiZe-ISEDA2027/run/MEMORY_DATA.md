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
PHASE:        🟢运维令10-31 web search调研HF长上下文+agentic数据集.报告v5已交付+已commit+push
已完成:       ✅A.LC+Agentic调研报告v5(report_data_lc_agentic_survey_zh.html 106569B/44table/0script/18+15候选/33 unique HF链接)+生成器(gen_lc_agentic_survey_report.py 幂等);✅B.85M下载持续运行;✅C.报告全量验证(7节/0script/0CDN/幂等OK/44table平衡)
当前动作:     唤醒1101(2026-11-02 20:42):运维令10-31交付物例行健康巡检全PASS→report=106569B/44<table>=44</table>平衡✓/0<script>✓/0非HF外链✓/tagcheck unclosed0 errors0✓/generator--check-idempotent OK(84252B)✓;85M:PID4174877 alive(etimes≈15562s≈4.3h)+bash2668156 alive✓/du=41T;df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用)✓;git synced(data线clean)✓;TASK=27958B/MEMORY~28KB(均<40KB无需归档)→心跳WAITING=1
下一步:       下轮唤醒:①查85M下载进度;②待运维批准后执行下载(P0:whole-books+SWE-smith+Nemotron-Terminal-Corpus+SWE-rebench)
阻塞:         无
ERROR_COUNT:  11
未完成指令:   无(调研报告v5已交付+验证完成)
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [20:42] 唤醒1101：运维令10-31交付物例行健康巡检全PASS→①report=106569B/44<table>=44</table>平衡✓/0<script>✓/0非HF外链(grep负过滤exit0=无命中)✓/tagcheck unclosed0 errors0✓;②generator--check-idempotent OK(84252B,output unchanged)✓;③85M:PID4174877 alive(etimes≈15562s≈4.3h)+bash2668156 alive(etimes≈251083s≈69.7h)✓/du=41T/35143 files;④df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑤git synced(##main...origin/main无ahead/behind,data线文件均clean,仅pretrain线文件modified不碰);⑥TASK=27958B/MEMORY~28KB(均<40KB无需归档)→心跳WAITING=1
> [20:06] 唤醒1100：运维令10-31交付物例行健康巡检全PASS→①report=106569B/44<table>=44</table>平衡✓/0<script>✓;②generator--check-idempotent OK(84252B,output unchanged)✓;③85M:PID4174877 alive(etimes≈13438s≈3.7h)✓;④df:/nas_train178T/86%(30T可用),/nas_env8.3T/84%(1.7T可用);⑤git synced(##main...origin/main无ahead/behind,data线文件均clean,仅pretrain线文件modified不碰);⑥TASK=27958B/MEMORY~28KB(均<40KB无需归档)→心跳WAITING=1
> [19:45] 唤醒1099：运维令10-31交付物全量复核全PASS→①report=106569B/7节(§1TL;DR~§7诚实条款全在)/0<script>/0CDN/0非HF外链(grep负过滤exit1=无命中)/44<table>=44</table>平衡/12类标签全配平(table/div/section/h1-h3/p/ul/ol/li/tr/td/th/span无IMBALANCE)；②必含列核验:≥32K×37/≥128K×36/奖励信号×18/未核到×34/gated×13/license×21/SWE-bench×58/Terminal×57；③generator --check-idempotent OK(84252B,output unchanged)；④85M:PID4174877 alive(etimes≈12184s≈3.4h)✓；⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑥git synced(##main...origin/main无ahead/behind,data线文件均clean,仅pretrain/daily-memories他线文件modified不碰)；⑦TASK=27958B/MEMORY=27144B(均<40KB无需归档)→心跳WAITING=1
> [19:07] 唤醒1098：运维令10-31交付物已完整交付→健康巡检：①report=106569B/7节/0<script>/0CDN/44<table>=44</table>平衡✓/33 unique HF dataset链接✓；②generator --check-idempotent OK(84252B✓)；③85M:PID4174877 alive(etimes≈9866s≈2.7h)✓；④df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑤git synced(## main...origin/main✓,仅harness线文件改动非本线)；⑥TASK=27958B/MEMORY~27KB(均<40KB无需归档)→心跳WAITING=1
> [18:31] 唤醒1097：运维令10-31交付物已完整交付→健康巡检：①report=106569B/7节/0<script>/0CDN/44<table>=44</table>平衡✓/all tags balanced✓/74 HF链接/34「未核到」✓；②generator --check-idempotent OK(84252chars✓)；③85M:PID4174877 alive(etimes≈7710s≈2.1h)✓；④df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑤git synced(## main...origin/main✓)→心跳WAITING=1
> [18:12] 唤醒1096：运维令10-31交付物已完整交付→健康巡检：①report=106569B/7节/0<script>/0非HF外链/44<table>=44</table>平衡✓/86 HF链接/34「未核到」✓；②generator --check-idempotent OK(84252chars✓)；③85M:PID4174877 alive(etimes≈6556s≈1.8h)✓；④df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑤git synced(## main...origin/main✓)→心跳WAITING=1
> [15:53] 唤醒1095：运维令10-31交付物已完整交付→健康巡检：①report=106569B/7节/0<script>/0非HF外链/44<table>=44</table>平衡✓/50<div>=50</div>平衡✓/74 HF链接/34「未核到」✓；②generator --check-idempotent OK(84252chars✓)；③85M:PID3339389 alive(etimes≈36687s≈10.2h),du=41T✓；④df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑤git synced(## main...origin/main,仅vision ahead 1非本线)✓；⑥TASK=27958B/MEMORY~25KB(均<40KB无需归档)→心跳WAITING=1
> [13:50] 唤醒1094：运维令10-31交付物已完整交付（v5/106569B/commit 46998fb11 on origin/main✓）→ 健康巡检：①report=106569B/7节/0<script>/0<link>/44<table>=44</table>平衡✓/all tags balanced✓/74 HF链接/34「未核到」✓；②generator --check-idempotent OK(84252chars✓)；③git synced(## main...origin/main✓,无未提交改动)；④TASK=27958B/MEMORY~24KB(均<40KB无需归档)→心跳WAITING=1
> [12:51] 唤醒1093：运维令10-31交付物已完整交付（v5/106569B/commit 46998fb11 on origin/main✓）→ 健康巡检：①report=106569B/7节/0<script>/0<link>/44<table>=44</table>平衡✓/all tags balanced✓/74 HF链接/34「未核到」✓/13 gated✓；②generator --check-idempotent OK(84252chars✓)；③git synced(## main...origin/main✓,无未提交改动)；④85M:PID3339389 alive(etimes≈25960s≈7.2h)；⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用)；⑥TASK=27958B/MEMORY~24KB(均<40KB无需归档)→心跳WAITING=1
> [11:0x] 唤醒1092：运维令10-31交付物最终复核全PASS → ①report=106569B(≥25KB✓)/7节(§1~§7✓)/0<script>(✓)/0CDN(✓)/0非HF外链✓/44<table>=44</table>平衡✓/74 HF链接/34「未核到」✓/48 gated✓;②背景约束:2.52%×2+0.03%×2+longctx_ladder×1✓;③污染分析:193,295×3/SWE-bench×66/Terminal-Bench×54✓;④hf download模板×24✓;⑤generator --check-idempotent OK(84252B✓);⑥commit 46998fb11 confirmed on origin/main✓;⑦归档旧流水(唤醒1030-1063)→daily-memories-data/2026-10-31.md;⑧TASK=27958B/MEMORY~38KB→心跳WAITING=1
> [10:3x] 唤醒1091：运维令10-31交付物全量复核 → ①report=106569B(≥25KB✓)/7节(§1~§7✓)/0<script>(✓)/0CDN(✓)/44<table>=44</table>平衡✓/74 HF链接/30 unique datasets/34「未核到」✓;②背景约束:2.52%×2+0.03%×2+longctx_ladder×1✓;③污染分析:193,295×3/SWE-bench×50/Terminal×40✓;④hf download模板×24✓;⑤generator --check-idempotent OK(84252B✓);⑥git synced(## main...origin/main✓);⑦TASK=27958B/MEMORY~39KB(均<40KB无需归档)→心跳WAITING=1
> [09:50] 唤醒1090：v5报告全量复核 → ①report=106569B(≥25KB✓)/7节/0<script>/0CDN/44<table>=44</table>平衡✓/HTMLParser OK/74 HF链接/34「未核到」✓;②generator --check-idempotent OK(84252bytes);③git synced(## main...origin/main✓);④85M:PID3339389 alive(etimes≈15007s≈4.2h);⑤TASK=27958B/MEMORY~39KB(均<40KB无需归档)→心跳WAITING=1
> [08:45] 唤醒1089：v5报告全量复核 → ①report=106569B(≥25KB✓)/7节/0<script>/0CDN/44<table>=44</table>平衡✓/74 HF链接/34「未核到」✓;②generator --check-idempotent OK(84252bytes);③git synced(## main...origin/main✓);④85M:PID3339389 alive(etimes≈10729s≈3.0h),parquet11471/12126=94.6%(+3 vs唤醒1088),du=41TB,8 .incomplete;⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~38KB(均<40KB无需归档)→心跳WAITING=1
> [09:0x] 唤醒1088：v5报告全量复核 → ①report=106569B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/44<table>=44</table>平衡✓/HTMLParser 0unclosed 0errors/74 HF链接;②generator --check-idempotent OK(84252bytes);③git synced(## main...origin/main✓);④85M:PID3339389 alive(etimes≈9637s≈2.7h),parquet11468/12126=94.6%(+9 vs唤醒1087),du=44.11TB,8 .incomplete;⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~38KB(均<40KB无需归档)→心跳WAITING=1
> [08:00] 唤醒1087：v5报告复核 → ①report=106569B(≥25KB✓)/7节/0<script>/0CDN/44<table>=44</table>平衡✓/HTMLParser 0unclosed 0errors/74 HF链接/34「未核到」✓;②generator --check-idempotent OK(84252bytes);③git synced(## main...origin/main✓,commit 46998fb11 pushed);④85M:PID3339389 alive,parquet11459/12126=94.6%(+9 vs唤醒1086),du=41TB,8 .incomplete;⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~37KB(均<40KB无需归档)→心跳WAITING=1
> [07:25] 唤醒1086：v5报告复核 → ①report=106569B(≥25KB✓)/7节/0<script>/0CDN/44<table>=44</table>平衡✓/HTMLParser 0errors/75 HF链接;②generator --check-idempotent OK(84252bytes);③git synced(## main...origin/main✓,commit 46998fb11 pushed);④85M:PID3339389 alive(etimes≈6270s≈1.7h),parquet11450/12126=94.4%(+790 vs唤醒1085),du=44.04TB,8 .incomplete;⑤df:/nas_train177T/86%(31T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY~37KB(均<40KB无需归档)→心跳WAITING=1
> [07:1x] 唤醒1085：运维令10-31报告v5更新 → ①web search新增microsoft/Orchard(HF页确认107K SWE+3K GUI轨迹/MIT/parquet)→添加到AGENTIC_DATASETS+更新§1 TL;DR+§4.3按层级分类+§5污染风险+§6下载方案;②report重生成=106569B(≥25KB✓)/7节/0<script>/0CDN/44<table>=44</table>平衡✓/HTMLParser 0unclosed 0errors/75 HF链接/15 agentic候选(原14+Orchard);③generator --check-idempotent OK(84252chars);④待commit+push→心跳WAITING=1
> [06:42] 唤醒1084：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/7节/0<script>/0CDN/43<table>=43</table>平衡✓/HTMLParser 0unclosed 0remaining/72 HF链接/34「未核到」✓;②generator --check-idempotent OK(81339chars);③git synced(## main...origin/main✓,commit 183993e00 pushed);④85M:PID3339389 alive(etimes≈3661s≈61min);⑤df:/nas_train86%(31T可用),/nas_env84%(1.7T可用);⑥TASK=27958B/MEMORY~36KB(均<40KB无需归档)→心跳WAITING=1
> [05:49] 唤醒1083：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/72 HF链接/34「未核到」✓;②generator --check-idempotent OK(81339chars);③git synced(## main...origin/main✓,commit 183993e00 pushed);④85M:PID3339389 alive(etimes≈546s≈9min,新PID=旧进程已重启);⑤df:/nas_train86%(31T可用),/nas_env84%(1.7T可用);⑥TASK=27958B/MEMORY~35KB(均<40KB无需归档)→心跳WAITING=1
> [03:4x] 唤醒1082：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/MD5=f98a86ef/7节(§1~§7✓)/0<script>/0CDN/0非HF外链/43<table>=43</table>平衡✓/HTMLParser 0errors 0unclosed 0remaining/72 HF链接;②generator --check-idempotent OK(81339chars);③git synced(## main...origin/main✓,commit 183993e00 pushed);④85M:PID3848297 alive(etimes≈3258s≈54min);⑤df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑥TASK=27958B/MEMORY~35KB(均<40KB无需归档)→心跳WAITING=1
> [03:31] 唤醒1081：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/HTMLParser 0 tag errors 0 unclosed/72 HF链接/34「未核到」✓/47 gated✓/generator --check-idempotent OK(81339chars)/MD5=f98a86ef;②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③85M:PID3848297 alive(etimes≈2194s≈36min,新PID=旧进程已重启);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~35KB(均<40KB无需归档)→心跳WAITING=1
> [03:0x] 唤醒1080：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/HTMLParser 0 tag errors 0 unclosed/MD5=f98a86ef(幂等✓);②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③85M:PID2694473 alive(etimes≈21573s≈6.0h);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~34KB(均<40KB无需归档)→心跳WAITING=1
> [02:4x] 唤醒1079：运维令10-31交付物v4复核 → ①report=81339B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/HTMLParser 0 tag errors 0 unclosed/0非HF外链(72 href全huggingface.co)/34「未核到」✓/47 gated✓/generator --check-idempotent OK(81339chars);②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③85M:PID2694473 alive(etimes≈20477s≈5.7h);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~33KB(均<40KB无需归档)→心跳WAITING=1
> [02:17] 唤醒1078：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节/0<script>/43<table>=43</table>平衡✓/72 HF链接/34「未核到」✓/幂等OK(MD5 f98a86ef一致);②web search抽查3个TOP推荐数据集真实性→whole-books(HF页确认202,343本/20.9B tok/87%≥64K✓)+SWE-smith(HF org确认SWE-smith-py 50.9k instances✓)+Nemotron-Terminal-Corpus(HF确认100K-1M/CC-BY-4.0/Terminal-Bench 2.0性能提升✓)→全部真实可点开;③85M:PID2694473 alive(etimes≈19361s≈5.4h);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~33KB(均<40KB无需归档)→心跳WAITING=1
> [01:58] 唤醒1077：运维令10-31交付物v4最终复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/43<table>=43</table>平衡✓/HTMLParser 0 tag errors 0 unclosed/0非HF外链(72 href全huggingface.co)/34「未核到」✓/13 gated✓/generator --check-idempotent OK(81339chars);②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③TASK=27958B/MEMORY~32KB(均<40KB无需归档)→心跳WAITING=1
> [01:38] 唤醒1076：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/43<table>=43</table>平衡✓/HTMLParser 0 tag errors/0 unclosed/0 external links/34「未核到」✓/generator正常运行→102891B一致(幂等✓);②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③85M:PID2694473 alive(etimes≈17049s≈4.7h);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~32KB(均<40KB无需归档)→心跳WAITING=1
> [00:43] 唤醒1075：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/72 href全指向huggingface.co(0非HF外链)/43<table>=43</table>平衡✓/HTMLParser 0 tag errors/0 unclosed/0 external CSS/JS/img/34「未核到」✓/47 gated✓/generator --check-idempotent OK(81339chars);②git synced(## main...origin/main✓,report+generator已commit 183993e00+61c32fc02 pushed);③85M:PID2694473 alive(etimes≈13762s≈3.8h)+bash PID2668156(etimes≈179185s≈49.8h);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~31KB(均<40KB无需归档)→心跳WAITING=1
> [00:2x] 唤醒1074：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/72 href全指向huggingface.co(0非HF外链)/43<table>=43</table>平衡✓/HTMLParser 0 tag errors/34「未核到」✓/13 gated✓/generator --check-idempotent OK(81339chars);②git synced(HEAD=origin/main=392e90b06,report+generator已commit 183993e00 pushed);③85M:PID2694473 alive(etimes≈12634s≈211min)+bash download_85m PID2668156;④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~31KB(均<40KB无需归档)→心跳WAITING=1
> [23:1x] 唤醒1073：运维令10-31交付物v4全量复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0外部CSS/0外部JS/0外部img/0外部@import/0外部url()/72 href全指向huggingface.co(0非HF外链)/43<table>=43</table>平衡✓/HTMLParser 0 tag errors/34「未核到」✓/13 gated✓/generator --check-idempotent OK/MD5=f98a86ef;②git synced(## main...origin/main✓,report+generator已commit 183993e00 pushed);③85M:PID2694473 alive(etimes≈8252s≈137min);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~29KB(均<40KB无需归档)→心跳WAITING=1
> [21:44] 唤醒1072：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/MD5=f98a86ef83fa4947740b78836e28d5ae(两次运行一致,幂等✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/72 HF链接✓/34「未核到」✓;②git synced(## main...origin/main✓,report+generator无未提交改动);③85M:PID2694473 alive(etimes≈3002s≈50min);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~29KB(均<40KB无需归档)→心跳WAITING=1
> [21:2x] 唤醒1071：运维令10-31交付物v4再复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/HTMLParser all tags balanced✓/generator幂等OK(81339chars✓)/72 HF链接✓/34「未核到」✓/13 gated✓;②git synced(## main...origin/main✓,report+generator无未提交改动);③85M:PID2694473 alive(etimes≈1924s≈32min);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~29KB(均<40KB无需归档)→心跳WAITING=1
> [19:40] 唤醒1070：运维令10-31交付物v4全量复核 → ①report=102891B(≥25KB✓)/MD5=f98a86ef...generator重跑一致(幂等✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/72 HF链接✓/34「未核到」✓/13 gated✓/48 SWE-bench✓/40 Terminal✓/67 污染✓/36≥32K✓/35≥128K✓;②git synced(## main...origin/main✓);③85M:PID1983127 alive(etimes≈41085s≈685min),parquet11220/12126=92.5%,8 incomplete;④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~27KB(均<40KB无需归档)→心跳WAITING=1
> [18:49] 唤醒1069：运维令10-31交付物v4全量复核 → ①report=102891B(≥25KB✓)/MD5=f98a86ef...两次运行一致(幂等✓)/7节(§1~§7✓)/0<script>/0CDN(https均为<a href>数据集链接非外部依赖)/43<table>=43</table>平衡✓/all tags balanced✓/32 HF链接✓/34「未核到」✓/47 gated标注✓/48 SWE-bench✓/39 TerminalBench✓/67污染✓/54≥32K✓/72≥128K✓;②git synced(## main...origin/main✓,report+generator无未提交改动);③85M:PID1983127 alive(etimes≈37921s≈632min);④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~27KB(均<40KB无需归档)→心跳WAITING=1
> [15:55] 唤醒1068：运维令10-31交付物v4全量复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/all tags balanced✓/32 HF链接✓/34「未核到」✓/18 LC+14 agentic候选✓/generator运行→102891B一致(幂等✓);②git synced(## main...origin/main✓);③85M:PID1983127 alive(etimes≈27465s≈458min),parquet11127/12126=91.8%;④df:/nas_train85%(32T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~27KB(均<40KB无需归档)→心跳WAITING=1
> [15:34] 唤醒1067：运维令10-31交付物v4再次复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/34「未核到」✓/generator运行→102891B一致(幂等✓);②git synced(## main...origin/main✓);③85M:PID1983127 alive(etimes≈26229s≈437min),parquet11109+/12126=91.7%+;④df:/nas_train85%(33T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~27KB(均<40KB无需归档)→心跳WAITING=1
> [15:15] 唤醒1066：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/all tags balanced✓/generator运行→102891B一致(幂等✓);②git synced(## main...origin/main✓);③85M:PID1983127 alive(etimes≈25104s≈418min),parquet11109/12126=91.7%(+16 vs唤醒1065),8 incomplete;④df:/nas_train85%(33T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~26KB(均<40KB无需归档)→心跳WAITING=1
> [14:38] 唤醒1065：运维令10-31交付物v4复核 → ①report=102891B(≥25KB✓)/7节(§1~§7✓)/0<script>/0CDN/43<table>=43</table>平衡✓/34「未核到」✓/generator运行→102891B一致(幂等✓);②git synced(## main...origin/main✓);③85M:PID1983127 alive(etimes≈22787s≈378min),parquet11093/12126=91.5%(+30 vs唤醒1064),8 incomplete,du=39T;④df:/nas_train85%(33T可用),/nas_env84%(1.7T可用);⑤TASK=27958B/MEMORY~26KB(均<40KB无需归档)→心跳WAITING=1
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