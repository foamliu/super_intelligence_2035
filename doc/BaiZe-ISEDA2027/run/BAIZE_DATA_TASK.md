# BAIZE_DATA_TASK.md

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_DATA.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🆕 运维指令 · 2026-10-14（💾 新增下载落盘位置 `/nas_env`）· 用户直令 · 常驻

> **用户令（2026-10-14）**：「告知 data，以后数据也可以下载到 `/nas_env`，目录仍然是 `app.e0031982/datasets`。」

**① 新增可落盘位置（常驻，与现有并列）**：`/nas_env/app.e0031982/datasets/`。落盘路径形式仍是 `<盘>/app.e0031982/datasets/<publisher>/<name>/`。

**② 现有落盘位置白名单（更新后）**：
- ✅ `/nas_inference/app.e0031982/datasets/`
- ✅ `/nas_user/<用户>/datasets/`（或 `/nas_user/app.e0031982/datasets/`）
- ✅ **`/nas_env/app.e0031982/datasets/`（新增）**
- 🚫 `/nas_train` 仍不放（已 ~85%）。

**③ 纪律（不变）**：下载前 `df -h` 确认目标盘已挂载 + 剩余空间 ≥ 预计总量；`setsid` 守护 + 断点续传；纳入「死/僵/速率趋零即 kill+restart」看护；实际落盘路径写进心跳；commit 前缀 `data dl:`；任务书 >32KB 自滚归档。

### 🆕 运维指令 · 2026-10-13（⏸ 暂停 85M + 📥 下载 HF 图文对 TOP-5 中「未下载」的 4 个 · 落 `/nas_inference` 或 `/nas_user` 的 datasets（🚫 不放 `/nas_train`））· 用户直令 · 最高优先

> 用户令（2026-10-13）：「data：暂停 85M，开始下载推荐的 TOP-5 中还没有下载的其它 4 个数据集。不要放在 `/nas_train`，放在 `/nas_user` 或 `/nas_inference`，我的 datasets 目录下。」

① 暂停 85M：
1. 停 data 线 85M 的 retry-loop（PID 2420118）+ hf download（PID 2420132）：先杀 wrapper 再杀 hf（`pkill -f` 或 `kill`），`pgrep -af` 复核已退。
2. 🚫 保留已下内容（不删任何 parquet）；`.incomplete` 默认保留（便于将来续传），仅在确认不再续传时才清。
3. 心跳把 85M 标 `⏸ 暂停（用户令 2026-10-13）` + 记已下进度（~8385/12124 ≈ 69.2%）。

② 下载 TOP-5 中「未下载」的 4 个（TOP-3 已在本地盘，跳过）：
| # | HF id | 规模 | 格式 |
|:--|:--|:--|:--|
| TOP-1 | `MVRL/WebMix-38M` | 38.8M 对 / ~2 TB | parquet(Image) |
| TOP-2 | `VedaLabs/wit_base`（= wikimedia/wit_base） | 6.48M 对 / ~200–400 GB | parquet(Image) |
| TOP-4 | `hanlincs/InternVL-SA1B-Caption-WebDataset` | ~22.4M 对 / ~1–1.5 TB | webdataset tar |
| TOP-5 | `HuggingFaceM4/the_cauldron` | ~1.9M 对 / 50 子集 | parquet(Image list) |
- ⚠️ 下载前先核实每个 repo 的实际大小 / 文件数 / 是否 gated（`huggingface_hub` API 或 `hf download --dry-run`），如实回报；不可达/gated 的标「不可达」跳过。
- 优先序：TOP-1 → TOP-2 → TOP-4 → TOP-5（TOP-5 `the_cauldron` 是 VQA/SFT 格式，非纯预训练，最后下）。

③ 落盘路径（用户硬要求）：
- 🚫 绝不放 `/nas_train`（其已 ~85%，逼近红线）。
- ✅ 放 `/nas_inference/app.e0031982/datasets/`（与 GPIC 同一 datasets 根）或 `/nas_user/<你的用户>/datasets/`；建议 `<...>/datasets/<publisher>/<name>/`（如 `.../datasets/MVRL/WebMix-38M/`、`.../datasets/VedaLabs/wit_base/`…）。以实测为准，把实际落盘路径写进心跳。
- ⚠️ 先 `df -h` 确认目标盘剩余空间 ≥ 预计总量（~2 + 0.4 + 1.5 + 少量 TB）。

④ 纪律：`setsid` 守护 + 断点续传；纳入「死/僵/速率趋零即 kill+restart」看护；与仍在下行的 en_v1_4 报各自速度 + 带宽争用；🚫 不删任何已有数据；commit 前缀 `data dl:`；任务书 >32KB 自滚归档。


### 🆕 运维指令 · 2026-10-13（🔍 为 vision encoder 训练在 HuggingFace 找「图文对」数据集 · 要求 image 带 bytes（非 url）· 中文 HTML 报告）· 用户直令 · 高优先

> 用户令（2026-10-13）：「data：使用 web search 给 vision encoder 训练在 huggingface 上找图文对数据集（要求 image 带 bytes 而非 url），输出 html 报告（中文）。」
> 性质：纯 web 调研 + 写报告，CPU/网络，不占 GPU；web 请求不占 NFS 带宽，不打断 en_v1_4 / 85M 下载。

① 目标：为 Stage (iii) 视觉编码器对比预训练（现有 = GPIC + CC12M + Amshaker ≈59M 对）寻找可直接下载即用的图文对数据集，重点是 image 列存的是真实像素 bytes（HF `Image` feature / parquet 内嵌二进制），而非仅 URL。

② 逐条筛选口径（每项给证据）：
1. image 载体：确认 image 列 feature 类型 —— ✅ `Image`(bytes) / `{bytes,path}` vs ❌ `string`(url) / `{url}`。最硬证据 = HF `datasets-server` `/info` 或 `/first-rows` 返回 `features['image'] == {'_type':'Image'}`（仅看文字描述不算）。
2. 规模：图片对数 + 总字节（可估）。
3. 许可：license（cc-by(-sa) / mit / apache / 未标注）。
4. caption：短/长 caption、alt-text；语言 en / zh / multi。
5. 是否已用（GPIC / CC12M / Amshaker / LAION 系须标注，避免重复）。
6. 可达性：HF 直连/镜像、是否 gated。

③ 方法：HF Hub + `datasets-server` API 检索（`image-text pairs` · `caption` · `interleaved` · `alt-text` · `DataComp` · `pixelprose` · `redcaps` · `mmc4` · `OBELICS` · `MINT` · `wit` · `datacomp`…）；可用 `huggingface_hub` 列 features 佐证。

④ 交付：`doc/BaiZe-ISEDA2027/report_data_hf_imagetext_datasets_zh.html`（中文 · 自包含 · 内联 CSS · 零外链 · ≤200KB）。必需节：① HERO+TL;DR（TOP 3–5 推荐）② 口径与 bytes/url 判定法 ③ 主表（HF id · 对数 · 总大小 · image 载体证据 · caption · 语言 · 许可 · gated · 是否已用 · 推荐度）④ 三分类（✅bytes 可直接训 / ⚠️url 需抓 / ❌不可用）⑤ 下载命令模板 + 落盘路径建议 + 预估磁盘 ⑥ 与 GPIC/CC12M/Amshaker 互补性 ⑦ 风险/诚实条款。

⑤ 纪律：🚫 不占 GPU · 🚫 不 kill / 不打断 en_v1_4、85M 下载 · 🚫 本令只调研+出报告，不下数据（真下载须运维二次确认）· 每条带 HF url + 访问日 · commit 前缀 `data rpt:` · 任务书 >32KB 自滚归档。


### 🆕 运维指令 · 2026-10-13（📥 把 85M 下载从「用户自管」移交给 data 线启动 + 看护）· 用户直令 · 最高优先

> 用户令（2026-10-13）：「把运维（用户）起的 85M 下载停掉，由 data 启动和看护这个数据下载。」
> 背景：`mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` 目前由用户自管进程在跑（此前 PID 1015571→555408，ppid 非 data 线），不在 data 线 kill+restart 看护纪律内，CDN 抖动崩了会静默卡住。现正式移交 data 线。

① 停掉用户进程（先定位再杀）：
1. `pgrep -af 'LLaVA-OneVision-1.5-Mid-Training-85M'`（或 `ps aux | grep 'hf download.*mvp-lab'`）定位当前 85M 进程（`hf download` 的 child，ppid 非 data 线）。
2. `kill <pid>`（SIGTERM）→ 等 10–20s → `pgrep` 复核已退；僵死则 `kill -9`。
3. ⚠️ 安全：`hf download` 可断点续传，杀进程不丢已下 parquet；`.incomplete` 残留见下清理。

② 由 data 线重启并接管（复用你现有 en_v1_4/GPIC 的「setsid 重启续传」套路，即唤醒 33/35 处置 base/SFT-2605 的同一套）：
1. 先核实落盘路径（`ls -d` / `du -sh`）：`/nas_train/app.e0031982/datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M`（以实测为准，若实际在别处如实记「实际路径=X」）。
2. 清残留：`find <dir> -name '*.incomplete' -delete`（只删 `.incomplete`，勿动已下 parquet）。
3. 重启（断点续传，绝不重下）：`setsid -f nohup hf download --repo-type dataset mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M --local-dir <dir> > /tmp/85M_dl.log 2>&1`（如需 token 照旧加 `--token <HF_TOKEN>`；并发/workers 你按「不与 en_v1_4 互相饿死」自行定，如 `HF_HUB_ENABLE_HF_TRANSFER=1` 或有限并发）。
4. 记新 PID，写进 `MEMORY_DATA.md` 心跳，把「85M 用户自管」改为「85M data 线看护 PID=xxx」。

③ 纳入看护纪律（与 en_v1_4 / GPIC 相同）：
- 每唤醒 `pgrep` 判活；死/僵/速率趋零 → 立即 kill+重启续传（前置清 `.incomplete`），不必等运维点名。
- 心跳逐子集报（8 子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics/sa1b/zero250m 各自 file 数），重点盯 `sa1b`+`zero250m` 两个一直未开始的子集（≈9.85TB，是剩余大头）。
- 速度/ETA 用「字节增量 + 仓库总量 46.66TB 分母」口径（延续 2026-10-10 更正；✅ 不用本地 `.metadata` 当分母）。
- 与 en_v1_4 并行，两条各自报速度 + 注明共享带宽争用。

④ 磁盘注意：`/nas_train` 现 ~85%（剩 ~32T），85M 剩余 ~17TB → 够放但告警；逼近 90% 或 85M 会越界就心跳标红 + 停 85M 等运维，🚫 不自作主张删任何数据。

⑤ 完成后：85M 下满 → `du -sh` 全量核实 ≈46.66TB / 12,124 files → 心跳报「85M 完成」→ 等运维指示再决定后续打包/对齐（85M 是多模态 mid-training 数据，非 P-8 LLM 投料，⚠️ 不并入 86:10:4 混料）。

> 📦 历史运维指令已归档 → `run/ARCHIVE_OPERATOR_DATA.md`（已执行完 / 已作废的块；需要时再读，不要读进上下文）。

> 本节由外部运维通过 git 修改，用于远程派活 / 改优先级 / 索取状态 / 暂停。
> agent 禁止修改本节（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。

> 📦 §运维指令·昨夜汇报HTML（2026-10-07）已执行完毕 → report_10_07_data_overnight.html 已交付；详细指令已归档 → run/ARCHIVE_OPERATOR_DATA.md。需要时再读。

> 📦 §运维指令·2026-10-08论文更新（§4 Data Mixture Search+§5 SFT/污染, main.pdf 9pp 0err, commit cbe0b641）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：4_llm_pretrain.tex+5_llm_posttrain.tex已更新,main.pdf编译0err,commit cbe0b641→debb3260。需要时再读。

> 📦 §运维指令·2026-10-08数据准备全链路状态报告HTML（report_data_pipeline_status.html 31KB）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：8节全链路报告已交付,含TL;DR/数据全景/下载/分词/配比/污染/磁盘/下一步。需要时再读。

> 📦 §运维指令·2026-10-07⑥配比实验收官总报告HTML（report_data_mix_summary.html 29KB）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：R1→s_step→R2→top-K全弧线报告已交付,ρ=−0.80排名反转+0.6pp不可分辨+88:8:4先验。需要时再读。


> 📦 §运维指令·2026-10-11文献借鉴报告（report_data_lit_ideas.html 36KB, 25篇→TOP-5+3附录, commit c80c7a74）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：25篇arXiv日报筛出8条可借鉴,TOP-1=Conditional Transfer(2610.11548)三信号配比框架→P-8, TOP-4=Beyond Owls(2610.10657)污染检测盲区, 全25篇ID经papers.jsonl核实✅。需要时再读。

---


> 📦 §运维指令·2026-10-10（更正85M总量=46.7TB,否7701/27T）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：85M 8子集精确总量12,124files/46.663TB已核实,纠正旧口径。需要时再读。

> 📦 §运维指令·2026-10-10（巡检并发下载85M+en_v1_4,回报各自速度/ETA）已归档 → run/ARCHIVE_OPERATOR_DATA.md；**结论**：两路并发巡检已执行,85M+en_v1_4各自速度/ETA已报,持续看护中。需要时再读。

> 📦 §运维指令·2026-10-10（🔄重启en_v1_4下载）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：en_v1_4已重启(PID2535486,parallel 24+hf_transfer),GPIC✅全完成→放行条件满足。需要时再读。

> 📦 §运维口径·2026-10-10（en_v1_4放行·用户再确认）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：GPIC完成即满足放行条件,data不自行启动(由运维/用户改白名单后下指令)。需要时再读。

> 📦 §运维口径·2026-10-09④（en_v1_4放行时点·用户裁定）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：en_v1_4在GPIC完成后放行(已被10-10块取代执行)。需要时再读。


> 📦 §运维指令·2026-10-09③（停②:停掉Code/Math重头来+加Ultra-FineWeb-L3+放开并发）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：全7项完成✅(①kill34旧进程+删46产物 ②R3全量分词110/110 DONE(1483.91B tok/5.94TB) ③并发110进程 ④197GB→2.0TB核实合理(524.43B×4≈2.1TB) ⑤6目录盘点全✅ ⑥污染扫描30/30 DONE(60K docs,0命中) ⑦铁律已遵守)。需要时再读。


> 📦 §运维指令·2026-10-07⑤（分词加大并发+.29 8卡空口径+推进顺序）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：分词并发化已完成(zh 8进程→全 web 44 shards 524.42B tok),.29 8卡空已确认,推进顺序被2026-10-09②覆盖。需要时再读。


> 📦 §运维指令·2026-10-07④（撤销定时停UltraX+续传下完479/479+GPIC让回）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：UltraX✅479/479全下完,GPIC恢复全速,en_v1_4继续排队。需要时再读。

> 📦 §运维指令·2026-10-07③（GPIC优先序裁定+BO方向核对）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：①GPIC优先序被④块作废(改为UltraX续传到底) ②BO方向bug=报告bug非code bug,TRUE best=t23(0.4155),t75(0.373)=MIN,R1 ρ=−0.43不受影响,已创建query_bo_r2.py。需要时再读。


> 📦 §运维指令·2026-10-07②（解除白名单锁定：UltraX-Preview下载+en_v1_4排队+分词）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：UltraX下载已启动(唤醒186)+zh分词已启动+en_v1_4排队；唤醒192续传重启UltraX。白名单新增UltraX-Preview+en_v1_4（用户主动解禁）。需要时再读。


### 🚨 运维指令 · 2026-10-07（P0 · 两条下载线（base + GPIC）继续 / 立即重启 —— 正文口径统一为「数据下载失败需主动重启」）· 最高优先 · 用户直令

> 用户 2026-10-07 直令：data 的两条数据下载线必须继续跑 —— base 死了 / 僵死就重启，从来没有过「拖着不动」的指令（用户原话逐字见 `run/ARCHIVE_OPERATOR_DATA.md`「2026-10-07 口径修正」块）。
> ⇒ ① 两条下载线必须持续在跑：base（`ultrafineweb_l1_en_hq` + `ultrafineweb_zh`）+ GPIC；② 从来没有过「base 死了就拖着不动」的指令 —— 你心跳里连写的 `Base 下载: 进程已死（按指令保持不动）` 属误读，立即废止该口径。

> 🔍 误读溯源（运维自查，如实说）：旧第 36 行那句 `🚫 不改白名单 / 不动下载`，本是 2026-10-03 白名单锁定时的巡检纪律，原意 =「不要擅自改白名单、不要乱动［健康的］下载」，不是「下载失败也不许重启」。2026-10-06 15:1x 用户已直令重启 base，那个 P0 块处置完后被归档进 `ARCHIVE_OPERATOR_DATA.md`（唤醒 167）⇒ 正文只剩「不动」半句，重启授权随归档一并消失。表述缺陷在运维，不在你。 完整溯源（含用户原话 + 被替换掉的旧字句原文）见归档「口径修正 · 2026-10-07」块。
> ✅ 永久口径（即刻生效，覆盖旧表述）：数据下载失败需主动重启 —— 白名单内任一下载「失败 / 僵死 / 速率趋零 / PID 已死」⇒ 立即 `kill`（若还在）+ 重启（沿用既有 retry-loop 规程），报告里标「已重启」+ 新 PID；不再需要等运维点名。
> 🚫 该条纪律今后只剩一种含义：不改白名单、不起白名单外的新下载；白名单内下载失败 ⇒ 按「数据下载失败需主动重启」处理，不许再写「保持不动」。

> 本轮唤醒内做完（不许拖到下轮）：
> 1. 取证：`ps -ef | grep -Ei 'hf download|huggingface-cli|hf_transfer|download_it_pairs'`（留原文）+ 两目录 `.incomplete` 计数 + 最新 mtime。
> 2. 重启 base（`l1_en_hq` 停在 5476/6006 ≈91%、`zh` ✅ 256/256 已满）：
>    - `--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*'`（config 级）；🚫 绝不拉 `en_v1_4`；
>    - retry-loop 包裹（失败 `sleep 30` 自愈 —— 你 2026-10-04 唤醒 85 用过、有效）+ `setsid nohup`（`ppid=1`）+ log `Ultra-FineWeb/download_l1_zh.log`；
>    - ⚠️ 外网命令显式带 proxy（`.12` 用你 `~/.bashrc` 里的那个值）；
>    - 命令原文 + 首次输出（起步 part 号）贴心跳。
> 3. GPIC 判活（PID / `gpic_train_XXXX.tar` mtime / 24h 新增 tar 数）→ 死即重启（父 `download_it_pairs.sh` 一并核）；目标 8001 tar + test 128 ✓。
> 4. 心跳格式（本轮起固定写一行）：`下载线：base l1_en_hq <n>/6006（+Δ, 活/已重启 PID, ETA）· zh ✅256/256 | GPIC <n>/8001（+Δ, 活/已重启 PID, ETA）`。
> 5. P-8 关联（为什么急）：base = P-8（Stage (i) 本体）硬前置（已分词仅 22.05B tok，P-8 需 ~100B）⇒ base 下满即解锁 P-8 备料；`l1_en_hq` + `zh` 双满 ⇒ 报运维「MiniCPM5 base 族就绪」。

> 纪律（不变）：🚫 不 kill 正在跑的 BO；🚫 不在 pretrain 释放前碰 GPU0-1；🚫 重 I/O 与 `.29` 抢 `/nas_train`；心跳 ≤60 min 且每步 commit + push；`TASK/MEMORY` ≤32KB。

---
> 📦 §运维问询·2026-10-07（三个现状问题）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：三问已答(唤醒185)①GPIC无加速②base下载全满只剩分词③BO变慢=波次锯齿非I/O。需要时再读。


> 📦 §📎 运维转发·R1 lm_eval结论更正（2026-10-07）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：名次方向bug+ρ符号+表格错字+结论改"代理无分辨力+证据不足"全部落地✅(唤醒181)。R2收尾操作提醒(§⑤)仍在归档中,收尾时需读。需要时再读。


> 📦 §运维指令·2026-10-06三步令（①200trial+top-K ②s_step归因 ③Round2 BO）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：三步全完成✅(①200trial+Spearman ρ=−0.43 ②MBS16→s_step 166ms=8.6×,D=0.5B ③Round2 200/200+top-K lm_eval ρ=−0.80)。需要时再读。

> 📦 §P0 base下载重启（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：base下载已重启(PID 3520692,l1_en_hq 89%+zh✅256/256),proxy=172.19.92.25:13128,白名单不变。需要时再读。


> 📦 §目标函数错了（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：6项全执行✅(Round2用lm_eval 8集均分作objective, Spearman ρ=−0.43证实loss≠能力)。需要时再读。


### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 📦 §运维规程·agent归档（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：agent自滚MEMORY+任务书,判据≤32KB/红线40KB,做法=只搬迁留指针（与「体积维护规程」同口径）。需要时再读。


### 🧭 收尾铁律 · 2026-10-06（用户指令 · 每轮唤醒必须执行，不许省）

> 📦 §收尾铁律·事故背景（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：心跳2h未更新致误判卡死→立「每轮必commit+push」硬约束。需要时再读。

每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：

0. 体积自检（先跑，数字要抄进下一步的心跳）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 ≤ 32KB；任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档（见本文件「📉 体积维护规程」：只把已闭合内容原文移入 `run/ARCHIVE_OPERATOR_DATA.md`、留 1 行指针），直到两者都 ≤ 32KB；> 40KB（红线）⇒ 必须先归档再提交（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_DATA.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. 写心跳：更新 `run/MEMORY_DATA.md` 顶部进度快照（`PHASE` / `已完成` / `当前动作` / `下一步` / `阻塞`），并追加 1 行「本唤醒流水」：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. 写日报：`run/daily-memories-data/<YYYY-MM-DD>.md` 追加本轮记录（当天文件必须建，不许攒着最后补）。
3. 自己提交 + 推送（不许等 loop 兜底）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md doc/BaiZe-ISEDA2027/run/DATA_LEDGER.md \
              doc/BaiZe-ISEDA2027/run/CONTAMINATION_CHECK.md doc/BaiZe-ISEDA2027/run/BAIZE_DATA_TASK.md \
              doc/BaiZe-ISEDA2027/run/DATA_MIX_RECIPE.md doc/BaiZe-ISEDA2027/run/DISK_CLEANUP_INVENTORY.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-data doc/BaiZe-ISEDA2027/run/data_pipeline
   git commit -m "data <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 绝不用 `git add -A` —— 这是共享工作副本，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已因此出过事故：`restore other agents files from dropped auto-commit`），后果是提交归属不可溯（运维查不出谁在干活）。
4. 闭环自检：`git status -sb` ⇒ 无 ahead / 无 behind；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   push 失败（`error: Forbidden` / 网络）：重试 1 次；仍失败 ⇒ 把报错原文写进心跳，下一轮唤醒第一件事就是补推。

> ⏱️ 运维判死判据（硬）：心跳文件 >60 min 无新提交 ⇒ 按卡死处理（派人上机 kill / 重排卡），不再等你。你干得再多，心跳不动 = 仍会被判死。

> 📦 §第5轮·代理规模定案 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：d=128/L=14/N≈18.5M定案+5项必验全PASS+评测硬规则+第0步分工,详见各子指针。需要时再读。

> 📦 §用户复核② 全块（2026-10-06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：5条判据(BO 200/200已满足)+先验88:8:4对照(进行中,见三步令①)+心跳纪律(已由收尾铁律覆盖)。需要时再读。

---

> 📦 §运维指令·2026-10-06配比实验改道（小代理+BO搜索空间/目标函数/交付§④⑤⑥）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：改道执行✅,BO R1+R2全完成,搜索空间/objective/交付已落地。需要时再读。

---

> 📦 §运维指令 · 2026-10-05（HTML报告 + D-CLEAN-4 定案 + 环境隔离）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：report_data_mix_s0a.html 已产出（已废弃）、D-CLEAN-4 保留不动、环境隔离纪律见 proxy 口径块。需要时再读。


### 🆕 运维口径 · 2026-10-05（你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测）

> 📦 §proxy口径·定位与反证段（2026-10-05）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：loop剥代理致外网不可达是预期→外网命令显式带proxy(见下方用法)。需要时再读。
> 🔧 正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）：凡访问外网的那一条命令，自己显式带上代理（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都不要带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> 🚫 装包别动共享 py310 env（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

> 📦 §运维指令 · 2026-10-05（分卡协调 GPU2-7）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：GPU2-7 归 data、配比实验已开工。需要时再读。

### 📉 体积维护规程（2026-10-03 立 → 2026-10-06 升级为「记忆 + 任务书」双约束，硬性）

> 📦 §体积维护规程·理由段（2026-10-03~06）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：TASK/MEMORY每次唤醒全文读入→越大约烧token→≤32KB硬约束。需要时再读。
- 上限（两者相同）：≤ 32KB；红线 40KB ⇒ 超红线当轮必须先归档才能收尾。
- 自检：见「收尾铁律」第 0 条（`wc -c` 两文件，数字抄进心跳）。
- 归档去向（只归档「历史」，🚫 不许归档「活口径」）：
  ① 已执行完/已作废的运维指令块 → `run/ARCHIVE_OPERATOR_DATA.md`（留下 1 行指针）；
  ② 被取代的候选表/推导过程（保留现行档 + 实测结果） → `run/ARCHIVE_DATA_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成的调研轮次原文 → 沿用 `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md` 等；
  ④ 较早的唤醒流水（保留最近 ~20 条） → `daily-memories-data/<条目日期>.md`（原文不改）。
- 🚫 不许归档：硬规则 / 验收标准 / 现行口径 / `WAITING:` 状态头 / 「运维问答」区。
- 指针（必须留、只 1 行）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 不许改小节编号/标题（别处有「见 §③.9」「上方块」这类交叉引用）。
- 谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）：`MEMORY_*.md` 一直由 agent 自滚，任务书同理 —— 本线 agent 自己把「已闭合」内容原文移入对应归档文件、留 1 行指针。⚠️ 本文件「agent 只读」的唯一例外 = 仅此「搬迁」：原文一字不改、不动小节编号/标题、不新增/不改写任何运维指令（本区作者仍是运维）。并发安全：归档前先 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `<线> 归档: …` 前缀。
- 顶部必须保留：① `WAITING:` 行（仍只出现一次）② 「进度快照」③ 「运维问答」（这一区不清，运维靠它读答复）④ 最近 ~20 条流水。
- 纪律：归档不改变任何结论；`WAITING:` 纪律不变。

---


| 项 | 当前值 |
|:---|:---|
| 🆕 下载白名单（2026-10-03 立 · 2026-10-09 用户裁定修订） | 只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族）② GPIC；🟡 `ultrafineweb_en_v1_4`：停用中 → 待 GPIC 下完后放行（用户 2026-10-09 裁定：放行时点 = GPIC 完成后、预计 10-10 上午、用户本人操作）；🚫 白名单外一律不下载、不调研、不推荐 |
| 历史指令 | 📦 D-CLEAN-4/当前指令/优先级覆盖/状态索取/暂停标志（2026-10-01~04）已归档 → run/ARCHIVE_OPERATOR_DATA.md；结论：全部已闭合/被运维指令区新块取代（配比实验改道为BO搜索，见上方活跃块）。需要时再读。 |

---

## 📊 进度快照（每次唤醒必须更新，供远程巡检）

> 固定格式写在 `MEMORY_DATA.md` 最顶部，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ `WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

运维巡检方式：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；不需要登录服务器。

---

> 📦 §0「当前主攻」+ §0.6「R4阶段 P-8 数据配方」（2026-10-02）已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/R2 调研完成、配比实验已改道为小代理+BO（见运维指令区改道方案块）。需要时再读。
---
## 1. 任务目标

把已在盘上的原始语料，变成训练可直接消费、配比正确、且不污染评测集的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ ← 🚫 已取消（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. 污染隔离白/黑名单 + 校验脚本（红线，P0）

上游方案文档（先读它）：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
时间线约束：ISEDA 2027 投稿截止 ≈ 2027-02-01；本任务必须在 2026-11 底前可交接（见方案 §6）。

> 注意本任务的定位：瓶颈是算力窗口不是数据量（方案 §2.1）。
> 所以不要把精力花在"下载/切分更多数据"上，而要花在质量、配比、格式可用性、隔离上。

> 📦 §1.1「数据落盘地图」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：实测数据位置详见 DATA_LEDGER.md。需要时再读。

> 📦 §2「阶段与推荐执行顺序」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：R/phase0/phase5 完成，当前主攻=配比实验（见运维指令区）。需要时再读。

## 3. 红线：污染隔离（违反则全部下游结论作废）

🚨 `EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。 改写/paraphrase 也不洗白。

- ✅ 允许入训练集：PyAether / SKILL 的 API 参考文档（它是任务的"来源材料"）
- ❌ 禁止入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ 阈值写明可复现 ④ SFT 语料同闸 ⑤ 独立报告
- 同一条规则适用于多模态 held-out 评估集（如 `eval5k`）：与训练集不同源 + 跨集去重比对

评测集本体路径（用于建黑名单，只读，绝不写入任何训练集）：
`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`

---

> 📦 §4「git 与共享工作区规则」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：git 规程见「收尾铁律」§3 + AGENTS.md §4。需要时再读。

## 5. 资源与约束
> 📦 §5「资源与约束」已归档 → run/ARCHIVE_DATA_SPEC_HISTORY.md；结论：常驻 .12、GPU2-7 归 data（见运维指令区）、重 I/O 避让。需要时再读。


## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：顶部"进度快照"（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| `run/DATA_RESEARCH.md` | 🎯 调研报告（当前主攻）：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | 数据清单（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | 污染隔离报告（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 `DATA_RESEARCH.md`（调研报告，当前主攻） —— 两个问题各四小项全部有结论，每条关键结论可顺 URL 复核
2. `DATA_LEDGER.md`（数据清单，含实测规模与与方案文档的差异）
3. `CONTAMINATION_CHECK.md`（污染隔离规则 + 阈值 + 扫描量 + 命中 + 处置）
4. `run/data_pipeline/`（可复现脚本，至少含盘点、校验、分词打包、指纹比对）
5. 训练可消费的产物（`.bin/.idx` + webdataset），路径与校验和写入清单
6. `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html`（自包含，与既有 HTML 报告同风格）
7. git commit + push（只提交 doc/ 文本与 run/ 脚本）

---

## 8. 推进原则

- 无阻塞时连续推进：把能立即做完的步骤一口气做完（可跨多个阶段），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟）。
- 有异步阻塞时：回写记忆并把 `WAITING` 置 `1`，记录"等待什么、如何判断结束"，然后退出。
- 不确定就如实记录并上报，不要编造数据、不要产出"看起来对"的合成语料。
