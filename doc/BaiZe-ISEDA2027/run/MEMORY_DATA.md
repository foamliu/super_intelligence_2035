# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 0

> 🔴 **用户令 2026-11-13a**：把 stack-v3-train **全量**（~15.9TB train split）下载到 `/nas_user/app.e0031982/datasets/`；已下载的 2TB（4600 parquet @ `/nas_inference`）搬过去不重下。执行顺序：①等分词主跑+rerun完成 ②rsync 2TB→/nas_user + 校验字节 ③hf download 全量剩余（自动跳已存在）④更新 DATA_MAPPING ⑤commit。纪律：nice19/max-workers2/不挤S1/不碰分词产物。

> 🔴 **用户令 2026-11-13b**：把第一批 2TB 的**分词数据**（926GB @ `/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/`）也搬到 `/nas_user`；等全量下载完成后**立即分词新 shard**（已分词的 4600 跳过）。执行顺序：①rsync 926GB→/nas_user+校验+删源 ②等 hf download 完成 ③分词脚本改 PARQUET_DIR/OUTPUT_DIR 指向 /nas_user ④只分词新 shard（part-04600+）⑤更新 DATA_MAPPING ⑥commit。纪律：nice19/ionice3/不挤S1/跳过已有.json。

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🟢 **✅ vision图文对调研报告DONE（唤醒1448,2026-11-11）**：用户令11-11→归因(10-13下载4路69.6M对未用=格式不兼容parquet/tar+无人接管线+实验设计限制)+平台盘点(中文9源/多语言2源/领域7源/已在盘7源)+推荐Top5(InternVL-SA1B零成本/TaiSu最佳中文/WebMix-38M规模/LAION-Chinese商用/PlotQA领域)+许可合规+下一步建议→report_vision_textpair_sourcing_zh.html(28321B/6节/0外链/HTML valid)落reports/→commit data rpt: pushed。

> 🟢 **✅ stack-v3-train 2TB下载全DONE（唤醒1422,03:56）**：batch7 FINISH@03:46:06→4600parquet/1,987,930,402,327B(1.85TiB)/0inc；2TB ROI复盘:token~2,025B/重叠2.4%/97.6%独特/ROI判定✅有价值→停止下载进入过滤+分词。

> 🟢 **✅ stack-v3-train 分词全DONE（唤醒1478,2026-11-13 10:1x）**：主跑4600/4600shard完成(47068s/173M docs/245.8B tok/279ERR);rerun 40shard完成(4492s/3.4B tok/0ERR);二次rerun确认40shard全SKIP(已有tokenized);tokenized输出926GB@/nas_train/.../tokenized/HuggingFaceCode/stack-v3-train/;无tokenize进程在跑→分词完全结束。

> 🟢 **✅ EDA脚本价值分析DONE（唤醒1468,2026-11-12 23:5x）**：用户令11-12→Phase A全扫4600shard(97M repos/1.28B files/5.86TiB/vendor1.3%/4963s)+Phase B分层抽样3200文件(9类)→V1=18/V2=149/V3=3033→外推V1~828文件/~0.01B token→Tcl唯一显著EDA命中(39.2%)/SKILL未检出/PyAether 0命中→报告report_data_stackv3_eda_script_value_zh.html(43KB/8节+附录/0外链/0script)落reports/→DATA_MAPPING.md§H.13新增→commit data eda:。
> 📝 **结论**：V1(直接可用)~828文件/~0.01B tok, V2(可挖掘)~6854文件/~0.04B tok, V3(低价值)~139518文件；报告路径reports/report_data_stackv3_eda_script_value_zh.html；建议：stack-v3对EDA脚本直接贡献有限，SKILL/PyAether需外部数据源。

> [11-13 18:35] 唤醒1488：用户令11-13a+b巡检→①StepA DONE(确认,926GB分词@/nas_user,源已删,4361json+MANIFEST/4565bin/4361idx);②StepB hf download:PID3112439 alive(etimes~23570s~6.5h,nice19),5297parquet/8207=65%/0inc/2.1TB/速率~4.1s/file/ETA~3.3h(~21:50CST),最后文件part-05296;③StepC tokenize_new_launch.sh:PID2869127 alive(ppid=1,etimes~9947s~2.8h),轮询等待中,日志最后行"parquet=5296/8207 incomplete=0";④df:/nas_user 113T/53%(54T余),/nas_train 207T/87%(28T余),/nas_inference 45T/38%(29T余)全OK;⑤三个后台进程全健康(hf download PID3112439+post_rsync parent PID3572574+tokenize launch PID2869127);⑥git fetch origin无新data令;⑦体积MEMORY归档20KB→更新进度快照→commit data stackv3-full:→WAITING=0继续巡检
> [11-13 17:55] 唤醒1487：用户令11-13a+b巡检→①StepA DONE(确认,926GB分词@/nas_user,源已删,4362json);②StepB hf download:PID3112439 alive(etimes~21068s~5.9h,nice19),5294parquet/8207=65%/0inc/2.1TB/速率~3.8s/file/ETA~3.1h(~21:00CST),最后文件part-05295;③StepC tokenize_new_launch.sh:PID2869127 alive(ppid=1,etimes~7445s~2.1h),轮询等待中,日志最后行"parquet=5294/8207 incomplete=0";④df:/nas_user 113T/52%(55T余),/nas_train 207T/87%(28T余),/nas_inference 45T/38%(29T余)全OK;⑤三个后台进程全健康(hf download+post_rsync parent PID3572574+tokenize launch);⑥/nas_inference源已清理(0parquet),/nas_train源已清理(空目录);⑦体积MEMORY~40KB→更新进度快照→commit data stackv3-full:→WAITING=0继续巡检
> 📦 唤醒1483-1486 原文已归档 → daily-memories-data/2026-11-13.md（StepA DONE确认+StepB下载进度巡检+StepC launch启动,共4轮,详见日文件）
> 📦 唤醒1471-1482 原文已归档 → daily-memories-data/2026-11-13.md（分词完成+全量下载启动+rsync 2TB+源删除+hf download全量+用户令11-13b启动,共12轮,详见日文件）

> 📦 迁移完成块(运维令13:3x+SFT/Agent分词+5源+4源+3稳定源+ufw_en,共9源705shard~8.3TB→/nas_env)已归档 → daily-memories-data/2026-11-13.md；结论见DATA_MAPPING.md

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        用户令2026-11-13a+b执行阶段（StepA DONE / StepB hf download 65% / StepC auto-wait脚本运行中） → WAITING=0
已完成:       ✅分词全DONE;✅EDA分析DONE;✅2TB下载DONE;✅batch1-7全DONE;✅2TB ROI复盘;✅vision图文对调研报告;✅tokenize脚本修复v3/v4;✅rsync 2TB→/nas_user(校验通过);✅源删除DONE;✅rsync 926GB分词→/nas_user(校验通过993,704,584,371B/13288files/4361json);✅/nas_train源删除DONE(释放993GB);✅/nas_inference源删除DONE(0parquet残留);✅StepC launch脚本就绪并后台启动(PID2869127,等待下载完成后自动分词)
当前动作:     ①StepA DONE:rsync 926GB分词数据/nas_train→/nas_user校验通过+源已删除;②StepB 进行中:hf download全量后台跑中(PID3112439,nice19/max-workers2,5297parquet/8207=65%/0inc/2.1TB/速率~4.1s/file/ETA~3.3h/~21:50CST/日志/tmp/stackv3_post_rsync.log);③StepC auto-wait脚本后台运行中(PID2869127,轮询等待hf download进程退出→自动启动分词,nice19/ionice3,16workers,跳过已有.json,日志/tmp/tokenize_stackv3_new.log)
下一步:       ①等hf download完成(ETA~3.3h,~21:50CST)→StepC脚本自动启动分词新shard(part-04600+,跳过已有4361json);②分词完成后校验du+find.json+failed_shards.txt;③更新DATA_MAPPING.md(新位置/总token/总字节);④更新MEMORY_DATA.md进度快照+一行结论;⑤commit data stackv3-full-tok:+push
阻塞:         无(StepA DONE,StepB下载中65%,StepC auto-wait已启动,WAITING=0短睡巡检)
ERROR_COUNT:  0
未完成指令:   有(stack-v3-train全量下载65%+StepC分词待启动)→WAITING=0
```

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