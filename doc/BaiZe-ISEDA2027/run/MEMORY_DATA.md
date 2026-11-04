# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

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
PHASE:        🟢运维令11-04 09:2x 下载长上下文(A类)数据到/nas_inference(~250GiB,9源,后台进行中)+09:1x 85M确认完成
已完成:       ✅85M下载正式翻转✅已完成(进程已停+0 .incomplete+运维09:1x已核);✅运维令10-31调研报告v6已交付;✅长上下文下载脚本download_longctx_datasets.sh已写+已启动(setsid后台,PID3129416,日志/tmp/data_download_lc_20261104_101957.log)
当前动作:     唤醒1170(2026-11-04 10:20):运维令09:2x执行中→①9源HF核实(8公开gated=False+caskcsg/NExtLong原id 401私有→改用公开变体NExtLong-128K-dataset;oellm pilot-v1精确id=birgermoell/oellm-longctx-tokenized-natural-128k-256k-pilot-v1);②脚本download_longctx_datasets.sh写入run/data/(落盘/nas_inference/app.e0031982/datasets/<org>/<name>/,nice -n10,hf_transfer=0,max-workers4,断点续传,3次重试);③已setsid后台启动,首源ysngkil/whole-books下载中(6%/256M);④85M:进程0+.incomplete0→正式✅已完成;⑤WAITING=0(下载在跑,未完成指令=有)
下一步:       下轮唤醒:①监控下载进度(tail /tmp/data_download_lc_*.log + du -sh 各源);②全部落地后校验(0 .incomplete+文件数+字节),按镜像下载路径写DATA_MAPPING.md;③落地后WAITING置回1
阻塞:         无(下载后台进行中,不占GPU,限并发≤4)
ERROR_COUNT:  11
未完成指令:   有(长上下文9源下载进行中,待全部落地)
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [11-04 10:20] 唤醒1170：运维令09:2x(下载长上下文A类~250GiB)+09:1x(85M确认完成)→①85M核实:进程0+find .incomplete=0→正式翻转✅已完成;②9源HF核实(dataset_info):ysngkil/whole-books·princeton-nlp/prolong-data-512K·openbmb/InfLLM-V2-data-5B·self-long/RULER-llama3-1M·THUDM/LongAlign-10k·deepmind/pg19·ghostcc3/mix-context-post-training-128k·birgermoell/oellm-longctx-tokenized-natural-128k-256k-pilot-v1 均 gated=False公开✓;caskcsg/NExtLong原id 401私有→改用公开变体caskcsg/NExtLong-128K-dataset(gated=False,209files,64K/512K变体另存待定);③写脚本run/data/download_longctx_datasets.sh(落盘/nas_inference/app.e0031982/datasets/<org>/<name>/,nice -n10,hf_transfer=0,max-workers4,断点续传,3次重试,状态写/tmp/data_download_lc_status.tsv);④setsid后台启动PID3129416,首源ysngkil/whole-books下载中(6%/256M,日志/tmp/data_download_lc_20261104_101957.log);⑤WAITING置0(下载在跑,未完成指令=有);⑥待落地后校验+写DATA_MAPPING.md
> [11-04 09:54] 唤醒1169：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链/47<table>=47</table>平衡✓/7节sec1-7齐/36unique HF数据集链接;②generator重跑产出逐字节一致(幂等✓,cmp /tmp/report_before.html identical);③git fetch synced(0 ahead/0 behind origin/main,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:PID1252810 ALIVE(hf download mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M)✓—前数轮心跳误报"无进程",本轮pgrep实测有进程,下载仍在运行;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥MEMORY=40373B>40KB→归档唤醒1117-1160心跳(44轮)到daily-memories-data/2026-11-04.md→MEMORY=15296B;⑦TASK=27958B(27.3KB)→任务已交付,心跳WAITING=1
> [11-04 08:58] 唤醒1168：运维令10-31交付物健康巡检全PASS→①report=115558B(=91300chars,≥25KB✓)/0<script>/0CDN/47<table平衡✓/7节sec1-7齐/50「未核到」/14gated✓;②generator generate_html()=91300chars与文件逐字一致(matches file?True)+--check-idempotent OK(91300chars两次相同✓);③git fetch synced(##main...origin/main无ahead/behind,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:无hf download进程→疑似已完成待运维确认;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈38KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 08:21] 唤醒1167：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(80HF链接全huggingface.co)/47<table>=47</table>平衡✓/HTMLParser errors=0 unclosed=0 stack=EMPTY✓/7节sec1-7齐/49「未核到」/14gated/Chinese✓;②generator --check-idempotent OK(91300B逐字节不变✓);③git fetch origin synced(##main...origin/main无ahead/behind,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:无hf download进程→疑似已完成待运维确认;⑤TASK=27958B(27.3KB)/MEMORY≈38KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 08:02] 唤醒1166：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(80HF链接全huggingface.co)/47<table>=47</table>平衡✓/HTMLParser unclosed=0 mismatch=0 stack=EMPTY✓/7节sec1-7齐/49「未核到」/14gated/Chinese✓;②generator --check-idempotent OK(91300B逐字节不变✓);③git fetch origin synced(##main...origin/main无ahead/behind,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:无hf download进程→疑似已完成待运维确认;⑤TASK=27958B(27.3KB)/MEMORY≈38KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 07:43] 唤醒1165：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(80HF链接全huggingface.co)/47<table>=47</table>平衡✓/7节sec1-7齐/50「未核到」/14gated/Chinese✓;②generator --check-idempotent OK(91300chars逐字节不变✓);③git fetch origin synced(##main...origin/main无ahead/behind,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:无hf download进程→疑似已完成待运维确认;⑤TASK=27958B(27.3KB)/MEMORY≈38KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 07:24] 唤醒1164：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(82HF链接全huggingface.co)/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/HTMLParser 0errors stack EMPTY✓/49「未核到」/14gated/56处32K/82处128K;②generator --check-idempotent OK(91300B逐字节不变✓);③git fetch origin synced(##main...origin/main无ahead/behind,data线clean✓,report+generator均在commit ab6f89572已push);④85M下载:无hf download进程→疑似已完成待运维确认;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B(27.3KB)/MEMORY≈37KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 07:06] 唤醒1163：运维令10-31交付物健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/0非HF外链(80HF链接)/47<table>=47</table>平衡✓/53<div>=53</div>平衡✓/7节sec1-7齐/HTMLParser 0errors stack EMPTY✓/49「未核到」/14gated/56处32K占比/82处128K占比;②generator --check-idempotent OK(91300bytes逐字节不变✓);③git fetch origin synced(##main...origin/main无ahead/behind,data线clean✓,git diff HEAD=0无改动);④85M下载:无hf download进程→疑似已完成待运维确认;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B(27.3KB)/MEMORY≈36KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 05:56] 唤醒1162：运维令10-31交付物例行健康巡检全PASS→①report=115558B(112.8KB≥25KB✓)/0<script>/0CDN/80 HF链接/47<table>=47</table>平衡✓/7节sec1-7齐/50「未核到」/14gated/HTMLParser 0errors✓;②generator --check-idempotent OK(91300B逐字节不变✓);③git pull --rebase synced(##main...origin/main无ahead/behind,behind-1=designflow shard C已合并,data线clean✓);④85M下载:无hf download进程→疑似已完成待运维确认;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B(27.3KB)/MEMORY≈36KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
> [11-04 05:36] 唤醒1161：运维令10-31交付物例行健康巡检全PASS→①report=115558B(≥25KB✓)/0<script>/0CDN/0非HF外链(80HF链接)/47<table>=47</table>平衡✓/7节sec1-7齐/HTMLParser 0errors✓;②generator --check-idempotent OK(91300bytes逐字节不变✓);③git synced(##main...origin/main无ahead/behind,data线clean✓);④85M下载:pgrep无hf download进程→疑似已完成待运维确认;⑤df:/nas_train179T/87%(29T可用),/nas_env8.3T/84%(1.7T可用);⑥TASK=27958B/MEMORY≈36KB(均<40KB无需归档)→任务已交付,心跳WAITING=1
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