# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

> 🚨 **下载口径（2026-10-07 起生效，覆盖本文件内所有旧写法）**：三条下载线 —— **base**（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）· **GPIC** —— 只要**失败 / 僵死 / 速率趋零 / PID 已死，就立即 kill + 重启**，报告标「**已重启**」+ **新 PID**，**不必等运维点名**。**「按指令保持不动」一类旧写法全部作废。** 细则见 `BAIZE_DATA_TASK.md` 顶部「运维指令 · 2026-10-07」P0 块。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        ▶️3路下载断点续传进行中+✅wit_base完成(330/330parquet/287G)+85M暂停(用户令2026-10-13,8436/12124=69.6%)+✅the_cauldron完成+✅GPIC全完成+✅R3分词110/110+✅HF imagetext报告→P-8数据层全就绪
已完成:       §0.3/§0.4/§0.6/§0.7；SFT/SFT-Agent下满+分词；D-CLEAN-1/2/3/4；proxy d128+recipe；held-out bin+held_out_eval; baize_mix_optuna.py+r2; 5项必验全通过；BO R1 200/200(ρ=−0.43); s_step归因; Round2 BO✅200/200(best=t23=0.4155); base下载完成; UltraX✅479; top-K收尾(ρ=−0.80); R3全量分词110/110DONE(1483.91B tok/5.94TB); R3污染扫描30/30DONE(60K,0命中,累计220K全0)→P-8数据层全就绪; ✅GPIC下载完成(8160tar@/nas_inference,12T); ✅文献借鉴报告(c80c7a74); ✅85M用户进程移交data线; ✅HfApi核实85M总量(12,124files/46.663TB); ✅HF imagetext数据集调研报告(唤醒404); ✅85M暂停(用户令10-13); ✅4路HF图文对下载启动(唤醒405); ✅the_cauldron下载完成(938parquet/158G,唤醒422); ✅全部4路下载暂停(用户令2026-10-14); ✅全部4路下载恢复断点续传(用户令2026-10-14 resume,唤醒444); ✅wit_base下载完成(330/330parquet/287G,2026-10-15 12:19,retry-loop自然退出)
当前动作:     唤醒471(2026-10-15 17:17) 巡检3路下载断点续传健康态(唤醒470后~69min)。3路全健康✅无需kill/restart：en_v1_4 PID805947(wrap766325,34641/56461=61.4%,3.1T,68dirs,+263par,0incomplete,last file 17:17,~3.8par/min,ETA~4天)|WebMix PID2798086(wrap766313,578parquet/428G,+34par/+25G,1incomplete=正在下,last file 17:17,~0.49par/min,ETA~3天)|InternVL PID766408(wrap766323,858tar/641G,+27tar/+19G,1incomplete=正在下,last file 17:17,~0.39tar/min,ETA~1.4天)。3路HTTPS ESTAB✅(55 conn via proxy)。wit_base✅330/330/287G(已完成)。85M⏸暂停(0进程)✅。disk:train85%/user76%/inf80%/env1%。📦体积:TASK=29KB/MEMORY=17KB(无需归档)。⚠️git push失败(proxy 503+direct unreachable,待下一轮补推)
下一步:       ①看护3路剩余下载(死/僵/速率趋零即kill+restart); ②85M维持暂停(用户令10-13); ③巡检进度/速率/ETA; ④P-8投料等运维指示; ⑤下一轮唤醒第一件事补推git
阻塞:         无(3路下载进行中全部健康); 85M暂停(用户令10-13); P-8投料等运维指示; git push暂时不可达(proxy 503)
ERROR_COUNT:  6
```

> 📦 §🔬 开工前 5 项必验结果（2026-10-06 09:48）已归档 → daily-memories-data/2026-10-06.md；**结论**：5 项全 PASS（N=18.36M/s_step=1.50s/LR=3e-3/Δloss÷2σ=7.9×），d=128 proxy 可开工。需要时再读。

## 📋 本唤醒流水
> [17:17] 唤醒471：巡检3路下载断点续传健康态(唤醒470后~69min)。3路全健康✅无需kill/restart：en_v1_4 PID805947(wrap766325,34641/56461=61.4%,3.1T,68dirs,+263par,0incomplete,last file 17:17:16,~3.8par/min,ETA~4天)|WebMix PID2798086(wrap766313,578parquet/428G,+34par/+25G,1incomplete=正在下,last file 17:17:29,~0.49par/min,ETA~3天)|InternVL PID766408(wrap766323,858tar/641G,+27tar/+19G,1incomplete=正在下,last file 17:17:13,~0.39tar/min,ETA~1.4天)。3路HTTPS ESTAB✅(55 conn via proxy 172.19.92.25:13128)。wit_base✅330/330/287G(已完成)。85M⏸暂停(0进程)✅。disk:train85%/user76%/inf80%/env1%。📦体积:TASK=29KB/MEMORY=17KB(无需归档)。⚠️git push失败(proxy 503+direct unreachable,commit已本地,待下一轮补推)
> 📦 唤醒470 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/17KB）
> 📦 唤醒469 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒468 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载断点续传健康态+3路全健康无kill/restart+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒467 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检3路下载+wit_base完成确认(330/330/287G,12:19自然退出)+3路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒466 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base仍在下载317parquet+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒465 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base wrapper自动重启hf确认+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒464 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒463 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒462 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/16KB）
> 📦 唤醒460 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/32KB）
> 📦 唤醒459 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒458 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒457 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+wit_base重启恢复确认+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒456 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载+wit_base速率趋零kill+restart PID1675681+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒455 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载+WebMix速率趋零kill+restart PID2798086+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒454 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路全健康无kill/restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒453 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载+WebMix速率趋零kill+restart+4路进度对比表+disk 4盘+体积29KB/31KB）
> 📦 唤醒452 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路进度对比表+速率估计+disk 4盘+体积29KB/31KB）
> 📦 唤醒451 原文已归档 → `daily-memories-data/2026-10-15.md`（含巡检4路下载断点续传健康态+4路进度对比表+速率估计+disk 4盘+体积29KB/30KB）
> 📦 唤醒444-450 原文已归档 → `daily-memories-data/2026-10-14.md` ~ `2026-10-15.md`（含恢复全部4路下载setsid启动+巡检+wrapper自动重启+en_v1_4 wrapper自动重启+4路进度对比表，详见各日文件）
> 📦 唤醒428-443 原文已归档 → `daily-memories-data/2026-10-14.md`（含第7~17次复核暂停态+进度表6路+.incomplete保留+disk 4盘，详见各日文件）
> 📦 唤醒427及更早（唤醒296-427）流水指针已归档 → `daily-memories-data/2026-10-10.md` ~ `2026-10-14.md`（含6路下载巡检全链+暂停/恢复+the_cauldron完成+GPIC完成+85M移交/暂停+en_v1_4进度29%~58%+4路图文对启动+R3分词+BO R2等，详见各日文件）


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