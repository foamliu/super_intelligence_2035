# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0


> 🟢 **心跳 · 2026-11-22 (R145) — 例行巡检（无新令）：git fetch origin 无新 data 令（所有用户令已交付，HEAD=origin=1304a92be2）；pretrain #2904 报 iter=277800/700k=39.69% step avg7.19s（末20步全<7.4s✅） loss2.00 / latest ckpt=276k（278k待落盘）/ 350k ETA≈6.0天(~11-28不变) / 700k ETA≈35.1天(~12-26不变)；v3 报告(R143)iter=277.5k 与当前 277.8k 偏差 0.3k(~36min)不刷新（ETA日期不变）；数据侧无新变化：PC-1~PC-5 全✅ / 污染扫描✅268K docs 0命中 / blend TSV 12源main版就绪 / 无后台任务（无pc2/tokenize/blend/contam进程）/ .12 load=24.6✅<120 / /nas_user 42T✅>5T红线。research 日报 11-22 data 建议「纯网页 vs 混合策展对照臂」（非约束参考，S1/S2配比已定不纳入本轮）。MEMORY_DATA 35KB✅<40KB / TASK 37.8KB✅<40KB。WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R144) — 例行巡检（无新令）：git fetch origin 无新 data 令（所有用户令已交付，HEAD=origin=f9e8e90cfb）；pretrain #2901 报 iter=277610/700k=39.66% step avg7.17s（全<7.4s✅） loss1.99 / latest ckpt=276k / 350k ETA≈5.9天(~11-28) / 700k ETA≈35.1天(~12-26)；v3 报告(R143)iter=277.5k 与当前 277.6k 偏差 0.1k(~12min)不刷新；数据侧无新变化：PC-1~PC-5 全✅ / 污染扫描✅268K docs 0命中 / blend TSV 12源main版就绪 / 无后台任务 / .12 load=24.4✅<120 / /nas_user 42T✅>5T红线。research 日报 11-22 data 建议「纯网页 vs 混合策展对照臂」（非约束参考，S1/S2配比已定不纳入本轮）。WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R143) — v3 报告路径 `run/reports/report_s1s2_split_data_v3_zh.html` + R143 刷新点（iter 进度同步）：v3 报告全文 iter 277.1k→277.5k / 39.6%→39.7% / step 7.23s→7.21s（pretrain #2900，20/21步<7.4s✅）/ 350k ETA 6.1→6.0 天（~11-28不变）/ 700k ETA 35.4→35.3 天（~12-26不变）/ gantt note + G5 Go/No-Go + risk#7 + footer 同步更新。数据侧无新变化：PC-1~PC-5 全✅ / 污染扫描✅268K docs 0命中 / blend TSV 12源main版就绪 / 无后台任务 / .12 load~26✅ .29 load~34✅ / /nas_user 42T✅ / v2 preserved / commit `data report:`+push / WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R142) — BAIZE_DATA_TASK.md 体积归档（硬上限修复）：3 个已闭合运维令（11-15 08:5x IFM下载+调研 / 11-13b 分词搬迁 / 11-13a stack-v3全量下载）原文搬入 `ARCHIVE_OPERATOR_DATA.md` 留 1 行指针；任务书 51381→37804 bytes（<40KB 硬上限 ✅）；归档口径=只搬迁留指针不改结论（口径仲裁表/工作约定/红线/任务目标等常驻段未动）。例行巡检：git fetch 无新 data 令（所有用户令已交付）；v3 报告(R140/v3.101) sound iter~277.1k；pretrain iter~277.3k step 7.18s；PC-1~PC-5 全✅；污染扫描✅268K docs 0 命中；blend TSV 12源 main 版就绪；.12 load~26✅ .29 load~28✅ /nas_user 42T✅；无后台任务。MEMORY_DATA 32950 bytes（<40KB✅）。WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R141) — 例行巡检 + /tmp 清理（step ③ 完成）：git fetch origin 无新 data 令（HEAD=origin=183b0ed4db）；pretrain #2896 报 iter~277.3k step 7.18s（<7.4s ✅）/ latest ckpt=276k / 350k ETA≈6.0天(~11-28) / 700k ETA≈35.1天(~12-26)；.12 load=26.1✅<120 / .29 load=28.1✅ / /nas_user 42T✅>5T红线 / 无后台任务 / PC-1~PC-5全✅ / 污染扫描✅268K docs 0命中 / blend TSV 12源main版就绪。**清理 /tmp 临时文件**：删除 ~24 个旧 pc2_*.log/py + tokenize_*.log + contam_*.md（MegaMath/stack-v3 分词已完成，日志无用）；保留 /tmp/contam_venv(152MB, pyarrow 环境) 供 S2 投料前可选全量扫描复用。research 日报 11-22 data 建议启动「纯网页 vs 混合策展」对照臂（非约束参考，当前 S1/S2 配比已定不纳入本轮）。v3 报告(R140)iter=277.1k 与当前 277.3k 偏差 0.2k(~24min)不刷新。WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R140) — v3 报告 iter 进度同步刷新：pretrain #2892 报 iter=277100 step 7.23s（<7.4s ✅），278k ckpt 待落盘。v3 报告 `report_s1s2_split_data_v3_zh.html` 全文 iter 数字 276.4k→277.1k / 39.5%→39.6% / step 7.4s→7.23s / 350k ETA 6.0→6.1 天 / 700k ETA 34.5→35.4 天（350k~11-28 700k~12-26 不变）；gantt note + G5 Go/No-Go + risk#7 + footer 同步更新。数据侧无新变化：PC-1~PC-5 全✅ / 污染扫描✅ 268K docs 0命中 / blend TSV 12源 main 版 / 无后台任务 / .12 load~25✅ .29 load~25✅ / /nas_user 42T✅ / commit `data report:`+push / WAITING=0**。

> 🟢 **心跳 · 2026-11-22 (R139) — S2 新源污染扫描全部完成（Go/No-Go #5 前置②✅）：用 `uv venv /tmp/contam_venv`（Python 3.10 + pyarrow 25.0.1，经代理安装）解决 pyarrow 缺失；新增采样脚本 `data_pipeline/sample_s2_new_sources.py`（每源 12 parquet 均匀采样 × ~1000 docs/file = 12,000 docs/源）；对 S2 blend 4 个零重叠新源各抽样 12,000 docs（合计 48,000 docs）用 `blacklist_extended`（5359 任务 / 4,847,354 去重 13-gram）跑 `check_contamination.py`：stack-v3-train(嵌套 files[].content, 12/8192 parquet)→12000 docs/76短文本兜底/**0命中**✅；finemath-3plus(顶层text, 12/128)→12000/**0**✅；Nemotron-CC-Math(顶层text, 12/57)→12000/**0**✅；MegaMath-web-pro(顶层text, 12/100)→12000/**0**✅。报告落 `data_pipeline/contam_s2_reports/`（4份+SUMMARY.md）。CONTAMINATION_CHECK.md §7 已更新为 [x]。**累计扫描总计 S1(220K)+S2新源(48K)=268,000 docs 全 0 命中**。iter~276.4k/700k step<7.4s / PC-1~PC-5全✅ / 无后台任务 / .12 load~26✅ .29 load~25✅ / /nas_user 42T✅ / commit `data contam:`+push / WAITING=0**。

> 🟢 **心跳 · 2026-11-21 (R138) — S2 扩展污染黑名单 `blacklist_extended/` 已建成（Go/No-Go #5 前置①完成）：新增 `data_pipeline/build_blacklist_extended.py`，在 EDA-Eval 536 任务基础上并入 HumanEval(164)/MBPP(500)/GSM8K(1319)/MATH(546)/SWE-bench(2294)，**合计 5359 任务 / 4,847,354 去重 13-gram 哈希**。各 benchmark schema 经 field_map 适配到统一禁止字段集；指纹方法与 build_blacklist.py 一致（仅落盘哈希，绝不含原始评测内容，P0 红线遵守）。正控验证：① shingle 比对 humaneval/gsm8k/swebench task-0 均 100% 命中；② 扫描器端到端 check_contamination.py --blacklist-dir blacklist_extended 扫 humaneval.jsonl = 164/164 命中 ✅。产物 gitignore 可再生。**下一步②（待办）**：4 新源(stack-v3/finemath/Nemotron/MegaMath-web)各抽样≥10K docs 跑扫描，前置=定位 pyarrow 环境（分词管线已有，下次唤醒 PYTHONPATH 复用）。本轮另核验：v3 报告(R136)+论文 Fig-1/Fig-2/TABLE IV/引用(#2/#3 令)均已 commit 完成且 sound。iter~276.4k/700k step<7.4s / PC-1~PC-5 全✅ / 无后台任务 / .12 load~25✅ .29 load~25✅ / /nas_user 42T✅ / commit `data contam:`+push / WAITING=0**。


> 🟢 **心跳 · 2026-11-21 (R137) — 黑名单可再生中间物重建：发现 `data_pipeline/blacklist/` 因 commit 931cc40e30 取消跟踪而缺失（gitignore 第30-33行标记为可再生），已用 build_blacklist.py + 6 评测快照 jsonl(EDA-Eval v20260311/148/46/Updated102/TEST/cuhk@/nas_train/.../eda_fastmcp/pyAether-eval/original_dataset/) **重跑复现**：536任务/193,295 13-gram/10 8-gram/4 短任务，与 v0.2 文档逐数一致(meta.json 2.13MB/ngram_hashes.txt 3.29MB/short 170B/ep 60KB)；正控冒烟(扫v20260311.jsonl自身)=158/158命中✅；S1污染闸门已就绪可复用。CONTAMINATION_CHECK.md §4+§7 已更新(标注 gitignore+重跑证据+S2新源扫描待办)。v3报告(R136)与blend TSV(12源/main)未动仍sound。iter~276.4k/700k step<7.4s / PC-1~PC-5 全✅ / 无后台任务 / .12✅ .29✅ / 9277-task 扩展黑名单(blacklist_extended/)尚未建(PC-3已下6 benchmark待转jsonl入指纹)**。

> 🟢 **心跳 · 2026-11-21 (R136) — v3 报告路径 `run/reports/report_s1s2_split_data_v3_zh.html` + R136 刷新点（main版blend TSV更新）：S2 blend TSV 从 fallback(10源) 更新为 main(12源)，加入 nemotron(prop=0.067/195.4B tok) + megamath_web(prop=0.060/218.1B tok)，megamath Batch1 epoch 1.69→0.62，math_l1/l3 降权(0.08→0.025/0.04→0.015)优先零重叠新源，math 类别 epoch 0.48→0.54，gen_blend.py --verify 通过(weight_sum=1.000000/13847 shards) / iter ~275.3k(ckpt274k)/700k(39.3%) step~7.23s / PC-1~PC-5 全部✅完成 / 无后台任务运行 / .12 load=27.4✅ .29 load=28.8✅ / /nas_user 42T✅ / fallback版存为blend_s2_preblend_fallback.tsv / v2 preserved / commit+push**。

> 🟢 **心跳 · 2026-11-21 (R135) — v3 报告路径 `run/reports/report_s1s2_split_data_v3_zh.html` + R135 刷新点（MegaMath-web分词✅100%完成）：iter ~275.3k(ckpt274k)/700k(39.3%) step~7.23s / 350k~11-28 700k~12-26 / MegaMath-web 分词✅100%(4950/4950=100%,磁盘 megamath_web_*.json 实测 sum ~218.1B tok,进程已退出) / Nemotron-CC-Math ✅完成(193/193,195.4B tok) / finemath ✅完成(9.4B tok) / Math-Reasoning ✅完成(2228/2228) / Code-Reasoning ✅完成(1637/1637) / MegaMath-web下载✅完成(4950/4950) / latest ckpt=274k / .12 load=25.3✅ .29 load=27.2✅ / /nas_user 42T✅ / **PC-1~PC-5 全部✅完成** / v2 preserved / commit+push**。

> _(R134~R116 心跳已归档 daily-memories-data/2026-11-21.md · iter~275.1k→273.0k step~7.23~7.13s MM-web 98.8%→89.8% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R115~R108 心跳已归档 daily-memories-data/2026-11-21.md · iter~272.3k→271.6k step~7.16~7.17s MM-web 87.7%→85.6% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R107~R97 心跳已归档 daily-memories-data/2026-11-21.md · iter~271.6k→270k step~7.12~7.17s MM-web 85.3%→79.9% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R96~R85 心跳已归档 daily-memories-data/2026-11-21.md · iter~269.8k→267.9k step~7.09~7.16s MM-web 78.9%→72.1% Nemotron✅ finemath✅ Math-Reasoning✅ Code-Reasoning✅)_

> _(R84~R70 心跳已归档 daily-memories-data/2026-11-21.md · iter~265.4k→267.6k step~7.0~7.1s MM-web 61.3%→70.8% Nemotron✅ Math-Reasoning✅ Code-Reasoning✅)_
> _(R69~R49 心跳已归档 daily-memories-data/2026-11-21.md · iter~261.3k→265.2k step~7.0~7.2s MM-web 43.3%→60.6% Nemotron✅ Math-Reasoning✅ Code-Reasoning✅)_

> _(R48 心跳已归档 daily-memories-data/2026-11-20.md · iter~261.1k step~7.32s MM-web 42.6% Math-Reasoning ✅100%)_

> _(R44~R48 心跳已归档 daily-memories-data/2026-11-20.md · iter~260k~261.1k step~7.1~7.32s MM-web 38.8%→42.6% Math-Reasoning 97.5%→100%)_

> _(R43 心跳已归档 daily-memories-data/2026-11-20.md · iter~260k step~7.0s MM-web 37.7% Math-Reasoning 97.5%)_

> _(R41~R13 心跳已归档 daily-memories-data/2026-11-20.md · iter~261k→267k step~7.0~8.2s MM-web 5.9%→32.3% Math-Reasoning 72%→92.8% Nemotron✅完成 193/193 195.4B tok / Code-Reasoning✅ / R18 Nemotron 完成里程碑)_
> _(R9, R8, R7, R4 心跳已归档 daily-memories-data/2026-11-19.md · iter~260k step~7.05s Nemotron 82-88% MM-web分词启动(ETA~40h) Math-Reasoning 72%)_


> 🔴 **用户令 2026-11-18 — S2 overlap 研究 + PC-4 blend TSV + Nemotron/finemath 分词 · 已交付**：
> **S2 overlap 报告**：`reports/report_s2_data_overlap_study.md`（455行/6方案/Megatron源码逐行分析）。结论：当前blend不排除S1已训数据；同种子重叠~83-100%；推荐方案D+E（补新源stack-v3/MegaMath天然零重叠 + S2换SEED=5678）；完全排除不可行。
> **PC-4 blend TSV**：`code/baize-llm/configs/blend_s2_preblend.tsv`（fallback版, 10源/prop=1.0/web40/code40/math20, 已加入finemath-4plus prop=0.005/epoch=0.78）。待Nemotron分词完成更新为main版。
> **Nemotron-CC-Math 分词**：🔄后台运行中 PID 1791931（27/193 shards, ~1.35B tok/shard, ~36.6B tok已产出, ETA~36.6h, RAYON=8, nice19, ionice3, log→/tmp/tok_nemotron_math.log）。
> **finemath-4plus 分词**：✅DONE（64/64 shards, 9.4B tokens, 0 errors, 5528s）→已加入blend TSV(prop=0.005)。
> **MegaMath PC-2 分词**：✅ALL DONE（5 subsets: text-code-block 200 shards + web-pro 100 + qa 32 + translated-code 16 + code 16 = 364 .json / 243GB; pc2_fast_split .12+.29 均已完成退出）。
> **MegaMath-web 下载**：🔄运行中 PID 489801（3252/4950=66%, 断点续传, nice19/ionice3/max-workers2, log→/tmp/dl_megamath_web_restart.log）。
> **Code-Reasoning 下载**：🔄运行中 PID 489797（1532/1637=94%, 2.8TB已落盘, 2 .incomplete, ETA~17min, 断点续传, nice19/ionice3/max-workers2, log→/tmp/dl_code_reasoning_restart3.log）。
> **Math-Reasoning 下载**：🔄运行中 PID 3697171（1076/2228=48%, 2.0TB已落盘, 断点续传稳定无崩溃, nice19/ionice3/max-workers2, log→/tmp/dl_math_reasoning_restart4.log）。
> **.12 负载**：33.82 ✅ (<120 红线, 不挤 pretrain)；.29 负载：38.75 ✅。

> 🔴 **用户令 2026-11-18 14:2x — .12 CPU 僵尸清理 + 分词分机 · 已执行**：
> **清理清单**：KILL PID 2350098 (`pc2_fast.py --subset megamath-text-code-block`, 9449%CPU=94核, ppid=1孤儿, 跑9h, batch encode用94线程抢CPU) + KILL PID 4060821 (`pc2_v3.py`, 99%CPU=1核, 跑8.5h, 与pc2_fast重叠做text-code-block但web-pro/qa/translated-code已完成→wasteful overlap)。
> **分机方案**：.12 `pc2_fast_split.py --subset megamath-text-code-block --start-idx 155 --end-idx 178` (shards 155-177/23个, RAYON_NUM_THREADS=8, nice=19, ionice=3, PID 2430086) + .29 `pc2_fast_split.py --subset megamath-text-code-block --start-idx 178 --end-idx 200` (shards 178-199/22个, RAYON_NUM_THREADS=16, nice=19, ionice=3, PID 3935896)。megamath-code 16 parquets schema不含text列(file_info/repo_info struct)→pc2_fast.py不兼容, 待后续单独处理。
> **处理后负载**：.12 loadavg 214→27.9(1min) ✅ (目标<120)；.29 loadavg 39 ✅；pretrain训练(torchrun PID 2501551)拿到CPU。脚本 /tmp/pc2_fast_split.py 已部署 .12+.29。

> 🔴 **用户令 2026-11-13a**：stack-v3-train 全量下载→✅StepA/B DONE(8192parquet/3.3TB); StepC分词→✅全DONE(8192/8192/476B tok/1.8TB/0ERR/92041s); StepD校验→✅通过(0ERR/no failed_shards/0 zero-byte/MANIFEST✅); ✅源清理(/nas_train+/nas_inference=0files); DATA_MAPPING H.14已更新

> 🔴 **用户令 2026-11-13b**：分词数据搬到/nas_user→✅StepA DONE; 分词新shard→✅StepC全DONE(8192/8192/476B tok); StepD校验→✅通过→DATA_MAPPING更新→commit

> 🔴 **用户令 2026-11-17 下载优先级调整**：按S2落地需求排序,预训练语料优先。下载优先级#1 MegaMath-web(142/4950files/3%/PID26529/log→/tmp/dl_megamath_web.log); #2 Nemotron-CC-Math-v1(130/196files/184GB/66%)→原PID3734806因ProxyError503崩溃,已重启PID318055/log→/tmp/dl_nemotron_math_v3.log(--token认证); #3 finemath→✅DONE(288parquet/140GB/0inc); #4 Code-Reasoning(1301/1637/80%/2.4TB/PID3734799); #5 Math-Reasoning(809/2228/36%/1.5TB/PID3734800); #6-10小数据集全✅DONE(OpenMathInstruct-2 12GB/OpenCodeReasoning 9.1GB/OpenCodeInstruct 6.4GB/code_contests 7.2GB/NuminaMath-1.5 507MB); 所有日志→/tmp/dl_*; nice19/ionice3/max-workers2/HF_HUB_DISABLE_XET=1; /nas_user 48T可用✅(≥5T红线)
>
> ✅ **用户令 2026-11-17 — S1/S2报告两份均已交付并commit**：①可行性报告report_s1s2_split_data.md(28KB/7节/commit cb4c93743) ②细化方案v2 report_s1s2_split_data_v2_zh.html(52KB/中文HTML/7节含blend TSV/甘特图/epoch核算/污染检查/Go-NoGo)。结论：4:4:2可行，stack-v3补code缺口(476B→过滤后286~405B)，MegaMath补math缺口(92~371B)，关键路径PC-1~PC-4预计11-23前就绪
>
> ✅ **用户令 2026-11-17 16:3x — 修正v2报告重大错误·已完成(v2.6, commit 53986ea18, pushed)**：①350k切换点修正为~11-26(原误为12-25) ②700k终点修正为~12-25 ③甘特图改为11-17→11-30 ④余量修正为~3天(原误为4周) ⑤Go/No-Go时间项全部更新 ⑥前置截止日期前移(PC-1 11-19/PC-2 11-21/PC-3 11-21/PC-4 11-23/PC-5 11-25) ⑦新增§2.1下载优先级表(10项,S2预训练语料#1~#3优先) ⑧epoch核算增Nemotron-CC-Math/finemath改善分析 ⑨全文数值审计通过(prop/epoch/timing均一致)
>
> 🔴 **用户令 2026-11-15 08:5x（IFM 3个数学/代码数据集+调研）**：✅IFM/MegaMath第一批DONE(364parquet/216GB/0inc/5子集); ✅MegaMath≡LLM360/MegaMath(sha 3cbc646); ✅调研报告DONE(17KB/6节含Top5+总表+污染检查+SVG); ✅HfApi实测3repo精确文件数/字节已写入DATA_MAPPING(MegaMath=5314parquet/1.118TB/Math-Reasoning=2226parquet/4.463TB/Code-Reasoning=1635parquet/3.277TB); ⏳MegaMath第二批(megamath-web 4950files/887GB)待IFM完成后启动; /nas_user 49T可用→✅红线≥5T

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
PHASE:        S2前置+污染闸门全完成 — PC-1✅~PC-5✅ + 扩展黑名单✅ + S2新源扫描✅(48K docs/0命中) → WAITING=0
已完成:       ✅PC-1 L4过滤(430.7B/90.5%);✅PC-2 MegaMath分词ALL DONE(5 subsets/364 shards/243GB);✅PC-3污染闸门(6benchmark/9277tasks);✅PC-4 main版blend_s2_preblend.tsv(12源/含nemotron 0.067+megamath_web 0.060+finemath 0.005/weight_sum=1.0/gen_blend --verify通过);✅S2重叠研究报告;✅finemath-4plus分词DONE(9.4B tok);✅v3报告(R136刷新main版/pushed);✅MegaMath-web下载DONE(4950parquet/826GB);✅MegaMath-web分词DONE(4950/4950=100%/218.1B tok);✅Code-Reasoning下载DONE(1637parquet/0inc);✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors);✅Math-Reasoning下载DONE(2228parquet/0inc);✅DATA_MAPPING.md更新;✅论文Fig-1三饼图+Fig-2调优+TABLE IV精简+数据源/Decay/LongCtx引用补齐(latexmk 0err);✅EDA-Eval 536-task黑名单重跑复现(R137/正控158/158);✅扩展黑名单blacklist_extended建成(R138/5359tasks/4847354 13-gram/正控164/164);✅S2新源污染扫描(R139/4源×12K=48K docs/全0命中)
当前动作:     R144:例行巡检;git fetch无新令(HEAD=origin=f9e8e90cfb);pretrain #2901 iter=277610/700k=39.66% step7.17s;v3报告(R143)iter=277.5k偏差0.1k不刷新;PC-1~PC-5全✅/污染扫描✅268K docs 0命中;无后台任务
下一步:       ①等pretrain到350k(~11-28)启动S2(blend TSV已就绪/SEED=5678待转告pretrain线) ②S2投料前可按S1口径对4新源做全量扫描(>150K docs)作为加强验证(非阻塞/contam_venv已就绪)
阻塞:         无(全部前置完成;无后台任务;.12 load≈24<120✅;/nas_user 42T可用✅>5T红线)
ERROR_COUNT:  0
未完成指令:   无(全部用户令已交付;PC-1~PC-5全部完成;main版blend TSV已就绪)→WAITING=0
```

> 📦 唤醒1521-1531 原文已归档 → daily-memories-data/2026-11-15.md~2026-11-16.md（StepC巡检+Agent/IFM下载进度+Code-Reasoning重启+IFM多轮巡检,详见日文件）

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-21 16:2x] 唤醒1557（v3报告R116刷新·例行巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(4445/4950=89.8%/~195.9B tok/ETA~4.7h/PID3028119+3028124/nice19/ionice3/RAYON=8/428%CPU=4核/etime~1d17h)；②✅Nemotron-CC-Math分词DONE(193/193/195.4B tok)；③✅finemath分词DONE(9.4B tok)；④✅Math-Reasoning下载DONE(2228/0inc)；⑤✅Code-Reasoning下载DONE(1637/0inc)；⑥✅.12 load=29.7✅<120红线；⑦✅.29 load=26.6✅；⑧✅磁盘/nas_user 113T/71T已用/42T可用(63%)→✅红线≥5T；⑨✅pretrain训练正常(iter~273.0k/step~7.13s/latest ckpt=272k)；⑩✅v3报告R116刷新(MegaMath-web 4445/4950=89.8%/load 29.7)；⑪✅git up-to-date with origin(无新data令/所有用户令已交付)；⑫下一步：等MegaMath-web分词完成(~4.7h)→更新main版blend TSV(加Nemotron)→逐源13-gram污染扫描→commit+push
> [11-20 10:00] 唤醒1556（v3报告R36刷新·2后台任务巡检·所有用户令已交付）：①🔄MegaMath-web分词RUNNING(1398/4950=28.2%/~55.4B tok/ETA~28.3h/PID3028124/nice19/ionice3/RAYON=8/438%CPU=4核)；②🔄Math-Reasoning下载RUNNING(1994/2228=89.5%/2inc/ETA~4.1h/PID3697171/nice19/ionice3/max-workers2)；③✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；④✅Code-Reasoning下载DONE(1635/0inc)；⑤✅.12 load=11.40✅<120红线；⑥✅磁盘/nas_user 113T/70T已用/43T可用(63%)→✅红线≥5T；⑦✅v3报告R36刷新(MegaMath-web 1398/4950=28.2%/Math-Reasoning 89.5%/load 11.40)；⑧✅git up-to-date with origin(无新data令)；⑨所有3条11-19用户令(v3报告/Fig-2饼图+TABLE IV/数据源引用+Fig-1三饼图)均已交付✅；⑩下一步：等MegaMath-web分词完成(~28h)→更新main版blend TSV(加Nemoton)→13-gram污染扫描→commit+push
> [11-20 ~04:00] 唤醒1555（v3报告R20刷新·3后台任务巡检）：①✅Nemotron-CC-Math分词DONE(193/193/195.4B tok/0errors)；②🔄MegaMath-web分词RUNNING(702/4950=14.2%/~26.4B tok/ETA~31h/PID3028119/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载RUNNING(1764/2228=79.1%/3.3TB/2inc/ETA~8h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=9.59✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告R20刷新(MegaMath-web 702/4950=14.2%/Math-Reasoning 79.1%/load 11.97)；⑦✅git pulled origin(d950d2c09/无新data令/所有用户令已交付)；⑧下一步：等MegaMath-web分词完成(~31h)→更新main版blend TSV→13-gram污染扫描→commit+push
> [11-20 02:10] 唤醒1554（例行巡检·v3报告刷新·3后台任务健康·Nemotron即将完成）：①🔄Nemotron-CC-Math分词 RUNNING(189/193=97.9%/~150B tok已产出/ETA~38min即将完成/PID1791934/nice19/ionice3/RAYON=8)；②🔄MegaMath-web分词 RUNNING(426/4950=8.6%/~15.7B tok/ETA~35h/PID3028124/nice19/ionice3/RAYON=8)；③🔄Math-Reasoning下载 RUNNING(1690/2228=76%/ETA~9h/PID3697171/nice19/ionice3/max-workers2)；④✅.12 load=13.34✅<120红线；⑤✅磁盘/nas_user 113T/70T已用/44T可用(62%)→✅红线≥5T；⑥✅v3报告已刷新最新live numbers(Nemotron 97.9%/MegaMath-web 8.6%/Math-Reasoning 76%/load 13.34)；⑦✅git up-to-date with origin；⑧下一步：Nemotron分词即将完成(~38min)→完成后立即更新main版blend TSV(加入Nemotron源/下调megamath prop/epoch从1.69降到~0.62)→更新v3报告→commit+push

> 📦 唤醒1552 原文已归档 → daily-memories-data/2026-11-19.md（例行巡检·4后台任务健康·Code-Reasoning 93%·Nemotron 21/193,详见日文件）

> 📦 唤醒1549-1551 原文已归档 → daily-memories-data/2026-11-18.md（例行巡检×3轮·4后台任务健康·Code-Reasoning渐进93%·Nemotron分词21/193,详见日文件）

> 📦 唤醒1548 原文已归档 → daily-memories-data/2026-11-18.md（3个崩溃下载重启+finemath分词DONE+Nemotron进度巡检,详见日文件）

> 📦 唤醒1547 原文已归档 → daily-memories-data/2026-11-18.md（后台任务巡检+IFM下载重启+进度更新,详见日文件）

> 📦 唤醒1536-1546 原文已归档 → daily-memories-data/2026-11-16.md~2026-11-17.md（IFM下载多轮巡检+Code-Reasoning崩溃修复重启+MegaMath batch2启动+HfApi实测,共11轮,详见日文件）
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