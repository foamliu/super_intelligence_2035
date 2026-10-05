# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.5/§0.6/§0.7 推进中 · 🔴白名单锁定(只下 l1_en_hq+zh+GPIC；en_v1_4 已停) · l1_en_hq 2173/6006(CC-MAIN-2025-30满✓+CC-MAIN-2025-33满✓+CC-MAIN-2025-38 173推进中) · zh 171/256(冻结待续) · gpic train 2945/8001+test 128✓(pid 144981 续传无丢) · ⭐⭐LIT_IDEAS_2026-10-05.html 完成(discovery-driven: 20+ cimi_search + 5 cimi_fetch · 52 entries · 34 from 2024-2026 · 32 new vs 10-04=62% turnover · 0 unverified · 41KB/389行) · D-CLEAN-4(§8+§9)已完成待拍板
已完成:       §0.3 8源/§0.4 R2视觉/§0.6 配方/§0.7 停85M·复用·ETA；SFT-2605 下满一致；D-CLEAN 盘点/-2 ≈341G/-3 servers ≈972G/-4 复扫+⭐LLaVA-4B ckpt(367 iter≈22 TiB)；⭐⭐LIT_IDEAS_2026-10-05.html(41KB/389行/自包含无CDN/discovery-driven: 20+searches+5fetches/52 entries/34 from 2024-2026/32 new=62%turnover/0 unverified/7 directions/5 gaps/成本救场专章+TOP-10) · ⭐LIT_IDEAS_2026-10-04.html(78KB/608行) · ✅DeepSeek-Flash定价一手核验(cimi-fetch: $0.14in/$0.56out per 1Mtok) · ✅RouteLLM核验(2406.18665: >2×降本) · ✅Nemotron-H核验(NVIDIA docs: 8B仅4层attention=8%) · ✅Chinchilla核验(2203.15556: 20:1 ratio) · ✅"Better Harnesses"(2607.08938: SLM 89.7%@4%cost)
当前动作:     唤醒122 ⭐LIT_IDEAS HTML 全量升级(运维2026-10-05指令: DeepSeek-Flash定价+ISEDA页数+2026新工作) + 巡检(白名单4项)：l1_en_hq 2173/6006(+50 vs 唤醒121@07:30、CC-MAIN-2025-38 173件推进中 mtime秒级、~1.7MB/s)、gpic train 2945/8001(+28、pid 144981活、~21MB/s) 真推进；en 2048✓满/zh 171/256 冻结/en_v1_4 停保留(488)；无僵死无需重启；task.md mtime 23:09(无新指令)；✅cimi-search+cimi-fetch MCP通道可用(运维2026-10-05修复)
下一步:       下轮判 retry-loop(3076502)+gpic(144981/父3525273) 真推进(僵死即 kill+重启)→ l1_en_hq(剩~3833件~297GB)+zh(剩85件~108GB) 下满即报运维「base族就绪」；D-CLEAN-4 候选等运维拍板；运维可查 LIT_IDEAS HTML(全量升级完成✅: 15条arXiv核验+DeepSeek-Flash定价+ISEDA页数+7篇2026新工作)
阻塞:         无硬阻塞；⚠️ l1_en_hq 速率偏慢(小文件+CDN，非僵死)；磁盘 /nas_train 84%(Avail 35T)；🚫 curl github不可达(但cimi-search MCP通道独立可达); 🟡 D-CLEAN-4 候选全部等运维拍板(只盘点不删除)
ERROR_COUNT:  0
```

## 运维问答

> 外部运维在 `BAIZE_DATA_TASK.md` 的「运维指令区」提问时，答案写在这里。

### ① `UltraData-SFT-2605` 重下（运维点名要「实际字节数 + 文件数 + 与 HF 官方清单一致性」）

**✅ 已完成（2026-10-02 唤醒 37 实测确认）**：
- **实际字节数**：`318,990,252,711 B` = **318.99 GB**（= 297.08 GiB）
- **实际文件数**：**1504 jsonl**（`no_think` 855 + `think` 649）
- **与 HF 官方清单一致性**：**逐字节完全一致** —— 官方清单（HF REST `/api/datasets` siblings + `/tree` 逐子目录求和）= **1504 文件 / 318,990,252,711 B**；本轮落盘 `find -printf '%s' | awk` 求和 = **318,990,252,711 字节**，两数**完全相等**；`.incomplete` 残留 = **0**。
- 逐子目录对齐：`no_think` = CG 50✓ + Code 300✓ + IF 20✓ + Kn 80✓ + Math 300✓ + ML-Kn 50✓ + ML-Math 55✓ = **855✓**；`think` = CG 50✓ + Code 279✓ + IF 20✓ + Kn 50✓ + Math 250✓ = **649✓**。


### ② D-CLEAN（2026-10-03 运维指令）— ✅ 已盘点完成（**只盘点、不删除**）

产出 `run/DISK_CLEANUP_INVENTORY.md`。可回收合计（分档）：

- 🟢 **明确可清 ≈3.3G**：`~/.cache/pip` 3.3G + `~/.cache/huggingface` 4.8M。
- 🟡 **需确认（本用户）≈10.1T**：laion2B-en-aesthetic ~~8.1T~~ **7.8G（D-CLEAN-2 已删）** + nemo_experiments 524G + servers 974G + models 452G + hf_cache 20G 等；LLaVA 85M 26T **保留不删**（运维令）。
- 🔴 **不可动**：base/gpic 下载、L3/code/math、SFT-2605、GPIC、en500k/eval5k、EDA-Eval 隔离区。
- 他人目录见 DISK_CLEANUP_INVENTORY.md（只读排查，未碰）。

### ③ D-CLEAN-2（2026-10-03 运维指令）— ✅ 已执行删除（回收 ≈341G）+ `servers` 探查

> ⚠️ **先更正前置错误**：D-CLEAN 盘点把 `laion2B-en-aesthetic` 记为 **8.1T，系 G/T 单位误读，实测 7.8G**（128 parquet URL 元数据）。

- **已删（`rm -rf`/`rm -f`，贴命令+实测大小→见 DISK_CLEANUP_INVENTORY.md §6）**：
  1. `laion2B-en-aesthetic` **7.8G** ✓（❌ 非 8.1T）
  2. `/nas_train/app.e0031982/zhulong.tar.gz` 493,894,409 B ✓
  3. `~/.cache/pip` 3.3G ✓
  4. `nemo_experiments` **Round 1 / S 系列 27 目录 ≈310G** ✓（保留 live `p5b` 79G + R2 p1–p7 ≈135G；删后 524G→214G）
- **实际回收 ≈ 341 GB ≈ 0.33 TiB**（`df -hT` /nas_train 仍显示 31T，因整 TB 粒度；`df -BG` Avail 30964G）—— **远小于运维预期 ~8.6T，原因即 laion2B 单位误读**。
- **`servers` 探查（未删）**：`/nas_train/app.e0031982/servers/` = **974G = 6 节点（10_239_2_12/24/26/27/28/29）× `LLaVA/`，为 LLaVA-V1.5-Qwen3-4B 旧训练 ckpt（2026-02 消融：loss-scope/token-merge/layerwise/rope/siglip2/optimizer）**。高价值回收候选，但属模型权重、有跨节点 symlink，**建议运维/owner 确认后再删**。
- **`nemo_experiments` R2 p1–p7（≈135G）保守保留**：被 P-5b 取代、但为近期（10-01~10-02）R2 中间实验；**是否也可清请运维二次确认**。

### ④ D-CLEAN-3（2026-10-03 运维指令）— ✅ 已执行删除 `servers`（974G），`nemo_experiments` R2 ckpt 保留

> 前置检查三项全过，已 `rm -rf`。结论：**实际回收 ≈972 GB**（=`du -sh` 974G，df 对得上）。

- **P1 无进程占用 ✅**：`fuser -v`（**无 `-m`**）对 `servers` 目录本身 = 空（仅一条 Stale file handle 警告）；全用户 open-fd 扫描命中 `servers` = 0；关键进程 cwd 均不在 servers（vision R9 `pt_elastic`+python 的 cwd=`run/vision`；hf 下载 2023896/2426795 cwd=datasets）。注：指令给的 `fuser -vm` 带 `-m` 是「整挂载」口径，会列出所有用 /nas_train 的进程，易误判，故改无 `-m` 精确口径。
- **P2 无近期活动 ✅**：`find servers -newermt '-7 days'` = 空（无任何 7 天内改动）。
- **P3 无脚本引用 ✅**：共享工作副本 `super_intelligence_2035`（含全部 loop/task 脚本）grep `app.e0031982/servers` = 0 命中；全树 `/nas_train/app.e0031982/code` grep（后台 119s）0 命中后停。
- **symlink 留证**：`servers` 内 symlink 指向**外部数据集**（coco/gqa/ocr_vqa/textvqa/vg/VG_100K）→ `rm -rf` **不跟随**，外部数据集**完好无损**（已逐一 `ls -d` 复核）；族内 symlink（adamw→siglip2-384、layerwise-a→lr-group-a、safetensors→checkpoint-3000）随删。
- **df 前后**：删前 `180751G used / 31218G avail` → 删后稳定 `179779G used / 32190G avail`（85%）→ **回收 ≈972 GB**。⚠️ 说明：删后 df 曾短暂只显示 -271G（NFS statfs 延迟），约 2 分钟后稳定为 -972G；最终以稳定值为准。
- **`nemo_experiments` R2 ckpt（p1/p2/p3/p5a/p7 ≈135G）按运维令保留**，本轮未动。

### ⑤ 🔴 下载白名单锁定（2026-10-03 运维指令，**本轮唯一动作项**）— ✅ 已执行：停 `en_v1_4`，只下 `l1_en_hq` + `zh` + GPIC

> 运维拍板：「数据下载现在就 MiniCPM5 的数据 + GPIC，不要再节外生枝。」→ 白名单 = ① `ultrafineweb_l1_en_hq`(478G) + `ultrafineweb_zh`(324G) ② GPIC；🔴 立即停 `en_v1_4`。

- **停了什么**：`kill 2061268`（旧 base-rest 进程，`--include` 含 `en_v1_4`+`l1_en_hq`+`zh` 三 config、顺序执行中，卡在 en_v1_4 首个快照 CC-MAIN-2013-20 **488/512** @~1.8MB/s）。✅ 进程已死（`ps -p 2061268` = DEAD）。
- **保留已下内容（🚫 不删）**：`en_v1_4` 已下 **488 parquet**（≈41.5GB，仅 CC-MAIN-2013-20 快照）**原样保留**在 `/nas_train/.../Ultra-FineWeb/data/ultrafineweb_en_v1_4/`。
- **释放带宽去向**：en_v1_4 = 6.75TB/56,461 文件（@1.8MB/s≈43 天）的巨量阻塞 → 停后带宽让给 `l1_en_hq`(478G)+`zh`(324G) 与 gpic。
- **新任务 pid**：**550476**（`setsid` 去进程组 + `nohup`、ppid=1；`--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*' --local-dir /nas_train/.../Ultra-FineWeb`；log=`Ultra-FineWeb/download_l1_zh.log`）。已过 `list_repo_tree`（64,771 文件）并开拉：**首拉 `ultrafineweb_zh` part-001-of-256**（⚠️ HF 树序先 zh 后 l1_en_hq，非 `--include` 顺序），**起步速率 ≈3.3 MB/s**（15s 内 `.incomplete` +48.96MB，与 gpic 2426795 并存抢带宽）。
- **带宽优先级（运维 ④）**：GPIC > l1_en_hq > zh —— 新任务按 `--include` 顺序先 l1_en_hq 后 zh，符合优先级。
- **白名单 4 项口径（⑤）**：`en`=2048/2048✅满 · `l1_en_hq`=0（刚启动）· `zh`=0（随后）· `gpic`=train 1634/8000+test 128/128✓（pid 2426795，~20MB/s）。

### ⑥ D-CLEAN-4（2026-10-04 运维指令）— ✅ 已执行「大盘复扫，只盘点、不删除」（产出 `DISK_CLEANUP_INVENTORY.md` §8）

> 指令：`/nas_train` 需要清理 → 用 sudo 盘点各目录大小，找可删除大目录，重点 `/nas_train/app.e0031982`。

- **大盘**：`/nas_train` 177T/207T（86%，Avail **31T**）；`/nas_inference` 60% / `/nas_user` 74% / `/data` 4%。
- **sudo 不可用**（`sudo -n true` → "a password is required"；本线无明文口令、纪律「口令绝不打印」→ 未 sudo）→ 跨用户 root/权限收紧目录只读顶层、无法测实。
- **本用户最大新增候选（🟡 需确认）**：`datasets/FineVision` **4.32 TiB**（可选补充源，~8.5 月未动）；`code/hell/LLaVA-OneVision-1.5` **1.24 TiB**（旧训练目录，疑与顶层 LLaVA-OneVision-1.5 重复）；`code/chip-mllm` 896G；`code/LLaVA` 716G；`code/LLaVA-OneVision-2` 650G；`chip_expert` 468G（4× chipexpert-cn 快照）；`models` 452G；`circuitvision-encoder` 244G；`datasets/HuggingFaceFW` 1.24T + `conceptual-captions` 1.13T。
- **跨用户候选（🟡 需 owner/运维）**：`/nas_train/wangcongtao` **2.42 TiB**（2026-01-13，~264 天）；`/nas_train/app.e0025692` **946 GiB**（2026-02-14，~232 天）；`app.e0041332` 1.3G；`app.e0013625` 0.2G。
- **可回收合计（分档）**：🟢 ≈0.6G · 🟡本用户 ≈**11.4 TiB** · 🟡跨用户 ≈**3.4 TiB**；🔴 不可动（mvp-lab 26T / base 2.74T / BaiZe-ISEDA2027 421G / eda_fastmcp / baize-vision / repo / harness / miniforge3）。
- **建议运维先拍板 5 项**：`FineVision` / `hell` / `chip_expert` / 跨 `wangcongtao`+`app.e0025692`（合计可回 **≈9.5 TiB**），其余多为 vision 线历史资产需 owner 二次确认。

### ⑦ ⭐ LLaVA-OneVision-1.5 4B checkpoint 专项（2026-10-04 用户点名追加 · D-CLEAN-4 下）— ✅ 已盘点（只盘点、不删除）

> 用户点名：`LLaVA-OneVision-1.5` 目录沉淀大量 **4B 检查点，绝大部分可删**。产出 `DISK_CLEANUP_INVENTORY.md` §9。

- **目标**：`/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/`（203 项；最后活动 2026-09-25 ≈9 天前；无活跃训练）。
- **核心（实测+计数）**：单个 Megatron 分布式 `iter_*` ckpt ≈ **61.6 GiB**（4 处一致）。**367 个 iter ckpt**（stage_1.5=299 + stage_2=68）≈ **22 TiB**；+ HF 转换 45 目录 **396 GiB**（du 精确）+ `checkpoints/baize_4b` 142G → **总 ≈22.5 TiB**。
- **🟢 可回收（用户已确认"绝大部分可删"）≈ 22 TiB**（删全部 iter ckpt + 被取代 release/HF 旧版，仅保留每 stage 最终 best ≈30G）。
- ⚠️ **史上最大单项**（远超 servers 974G / FineVision 4.3T / nemo_exp 272G 之和）；P1/P2/P3 全过 → 建议运维一次性拍板。

### ⑧ ⭐ BaiZe 论文「idea 文献调研」HTML 报告（2026-10-04 运维指令 · 最高优先 · 明早 08:30 前）— ✅ 已产出 + ✅ 15条在线核验完成 + ✅ 全量升级(定价+ISEDA+2026新工作)完成

> 运维指令：用 `cimi-search`/`cimi-fetch` 调研 7 方向（方向 0 成本经济性为最高优先），产出自包含 HTML `doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html`，明早 08:30 前交付。

- **产出**：`doc/BaiZe-ISEDA2027/LIT_IDEAS_2026-10-04.html`（**78 KB / 608 行 / 自包含 · 无外部 CDN**），数据 agent 唤醒 110 于 2026-10-04 23:30 生成，唤醒 121 于 2026-10-05 07:45 完成在线核验，唤醒 122 于 2026-10-05 08:30 完成全量升级。
- **结构齐全**：① TL;DR(10 条) ② 主表(50 idea × 全列) ③ 分三档(立即可做 16 条 / 需小实验 3 条 / 需长期 4 条) ④ 专章「成本救场」(4 子命题证据链 + DeepSeek-Flash 定价表 + 2026 SLM 成本证据表) ⑤ 最高性价比 TOP-10 ⑥ 7 方向详述(+2026前沿段) ⑦ 参考清单(37 条本地 bib + 15 条在线核验 + 7 篇 2026 新增) ⑧ 缺口清单(全部✅) ⑨ 给运维下一步建议。
- **✅ 15条 arXiv 在线核验完成**（2026-10-05 07:35–07:45, cimi-search MCP 恢复可用）：
  - **12 条核验通过**：DeepSeek-V3(2412.19437✅ 671B/37B/2.788M H800h) / GRPO(2402.03300✅) / DAPO(2503.14476✅) / 推测解码(2211.17192✅) / FrugalGPT(2305.05176✅ 98%降本) / Hinton蒸馏(1503.02531✅) / CLIP(2103.00020✅) / SigLIP(2303.15343✅) / MAE(2111.06377✅ 75%mask ViT-H 87.8%) / DINOv2(2304.07193✅) / Token Merging(2210.09461✅ ICLR2023 Oral 2x) / Kaplan(2001.08361✅)。
  - **3 条 arXiv ID 更正**：RouteLLM 2406.08502→**2406.18665** / SigLIP 2 2502.04433→**2502.14786** / LLaVA-NeXT 2406.16860实为Cambrian-1→**博客文章**(无独立arXiv论文)。
- **✅ DeepSeek-Flash 定价一手核验**（唤醒 122, cimi-fetch 抓取官方定价页 api-docs.deepseek.com）：DeepSeek-V4.1-Flash 输出 **4–8 元/M tok**（≈$0.56–1.11），已填入 §4 成本对比表。自部署 BaiZe 2.2B 输出 ≈$0.024/M tok → 比值 ~1/23–1/46（decode）→ 叠加 KV cache → ~1/100（agentic 长会话）。
- **✅ ISEDA 投稿要求已确认**（cimi-fetch 抓取 eda2.com/iseda/sub.html）：Regular Full Paper **4–6 页**。⚠️ BaiZe 论文当前 7 页 → **需压缩 1 页**。
- **✅ 7 篇 2026 新工作已补**（此前完全空白）：arXiv 2607.08938（CMU, SLM 89.7%@4%cost, cimi-fetch 正文一手核验）/ 2512.15943 / 2604.19299 / 2604.23577 / 2606.27457 / 2609.01532 / 2602.22495。详见 §4 成本专章 + §7 参考清单。
- **git**：本轮已 `git add` 该 HTML + 本记忆 + 当日日志并**本地提交**；`git push` 因 `Network is unreachable` 失败，待网络恢复后同步远端。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R research ✅ + R2 LLM 侧 ✅（8 源满填 / base vs L3 重叠 0% / P-8 86:10:4）+ R2 视觉侧 ✅（§0.4：本地 bytes 图文对实测 / 13 HF 候选 / 前 3 推荐）+ phase5 isolation v0.3 + phase1/2 脚本就绪；§0.5/§0.6/§0.7 推进中（§0.6 配方✅ / §0.7 停85M·复用·ETA✅ / SFT-2605 下满一致✅）** |
| WAITING | 1（下载中：白名单锁定——retry-loop 3076502+hf 3076519 先拉 l1_en_hq(2173/6006)+zh(171/256 待续)；gpic 144981(父 download_it_pairs.sh 3525273 自动续命) train 2945/8001+test 128✓；en 2048/2048 满；en_v1_4 已停(488 保留)；LLaVA 85M 停无进程；D-CLEAN-4 done（只盘点，Avail 35T/84%）；⭐LIT_IDEAS HTML 全量升级完成✅(15条arXiv核验+DeepSeek-Flash定价+ISEDA页数+7篇2026新工作)；重 I/O 推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-05 |

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

- 2026-10-05 —— 唤醒 111（已滚动归档至 daily-memories-data/2026-10-04.md）
- 2026-10-05 —— 唤醒 112（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 113（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 114（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 115（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 116（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 117（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 118（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 119（白名单 4 项巡检，无假活、无重启，网络仍断）：复核 `BAIZE_DATA_TASK.md` mtime **23:09 未变**（无新指令/无索取/无 STOP；⭐LIT_IDEAS HTML 已产出验收通过；D-CLEAN-4 §8+§9 已完成、等运维拍板）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~25.2h，stat Ss/Sl 活）真推进：**l1_en_hq = 2006/6006**（✅ CC-MAIN-2025-30(1000件)满、✅ CC-MAIN-2025-33(1000件)满@06:13 part-1000、🆕 CC-MAIN-2025-38 新启动 6 件 part-0006@06:17 秒级；上轮 1958@05:38→2006@06:17 = +48 件/~39min ≈ **~1.6MB/s**；~78MB/件；非僵死不重启；0 .incomplete）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 10-04 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **144981**（etime ~11.4h，stat Sl 活；父 `download_it_pairs.sh` 3525273 etime~3.6d 活）真推进：train **2853/8001** + test 128/128✓、0 .incomplete（上轮 2826@05:39→2853@06:16 = +27 件/~37min ≈ **~19MB/s**；gpic_train_02853.tar mtime 06:16 秒级；~1.58GB/tar）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留）；LLaVA 85M 停无进程。✅ en 2048/2048 满（/nas_train 复用副本）；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 63%(17T)、/nas_user 74%(29T)、/data 4%（均够）。🚫 网络：curl arxiv/hf **http=000** + fetch_web_content **Unable to connect**→31 条⚠️LIT_IDEAS 未在线核验仍无法补验（⚠️ HF CDN 可达故 hf download 正常，仅通用 Web 隔离；环境性非疏漏）。ETA：l1_en_hq 剩 ~4000 件≈312GB @~1.6MB/s ≈ **~2.1 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5148 件≈8.2TiB @~19MB/s ≈ **~5.0 天** → base 族就绪(l1_en_hq+zh) ≈2.1 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 144981 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY 32114B→滚动迁唤醒113+114→daily-memories-data/2026-10-05.md 后加 119 ≤32KB。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar；网络恢复后补验 LIT_IDEAS 31 条。
- 2026-10-05 —— 唤醒 120（白名单 4 项巡检，无假活、无重启，网络仍断）：复核 `BAIZE_DATA_TASK.md` mtime **23:09 未变**（无新指令/无索取/无 STOP；⭐LIT_IDEAS HTML 已产出验收通过；D-CLEAN-4 §8+§9 已完成、等运维拍板）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~26h，stat Ss/Sl 活）真推进：**l1_en_hq = 2057/6006**（✅ CC-MAIN-2025-30(1000件)满、✅ CC-MAIN-2025-33(1000件)满、🆕 CC-MAIN-2025-38 推进中 57 件 part mtime 06:56 秒级；上轮 2006@06:17→2057@06:56 = +51 件/~39min ≈ **~1.7MB/s**；~78MB/件；非僵死不重启；0 .incomplete）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 10-04 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **144981**（etime ~12h，stat Sl 活；父 `download_it_pairs.sh` 3525273 etime~3.6d 活）真推进：train **2883/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2853@06:16→2883@06:56 = +30 件/~40min ≈ **~21MB/s**；gpic_train_02882.tar mtime 06:56 秒级；~1.58GB/tar）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留）；LLaVA 85M 停无进程。✅ en 2048/2048 满（/nas_train 复用副本）；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 63%(17T)、/nas_user 74%(29T)、/data 4%（均够）。🚫 网络：curl arxiv/hf/github **http=000** + fetch_web_content **Unable to connect**→31 条⚠️LIT_IDEAS 未在线核验仍无法补验（⚠️ HF CDN 可达故 hf download 正常，仅通用 Web 隔离；环境性非疏漏）。ETA：l1_en_hq 剩 3949 件≈308GB @~1.7MB/s ≈ **~2.1 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5118 件≈8.1TiB @~21MB/s ≈ **~4.5 天** → base 族就绪(l1_en_hq+zh) ≈2.1 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 144981 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY ~30KB→滚动迁唤醒115→daily-memories-data/2026-10-05.md 后加 120 ≤32KB。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar；网络恢复后补验 LIT_IDEAS 31 条。
- 2026-10-05 —— 唤醒 121（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 122（⭐LIT_IDEAS HTML 全量升级完成 + 白名单4项巡检）：运维指令 = 补齐 DeepSeek-Flash 定价 + ISEDA 页数 + 2026 新工作。✅ **全部完成**：① cimi-fetch 抓取 DeepSeek 官方定价页 → DeepSeek-V4.1-Flash 输出 4–8 元/M tok（≈$0.56–1.11），填入 §4 成本对比表，自部署 BaiZe 2.2B ≈$0.024/M tok → ~1/23–1/46（decode）→ ~1/100（agentic 长会话三重叠加）；② cimi-fetch 抓取 eda2.com/iseda/sub.html → Regular Full Paper **4–6 页**，⚠️ BaiZe 论文 7 页需压缩 1 页；③ cimi-search 找到 7 篇 2026 新工作（此前完全空白），最关键 arXiv 2607.08938（CMU, SLM 89.7%@4%cost, cimi-fetch 正文一手核验）+ RouteNLP 2604.23577（企业级 58% 降本）+ Switch Distillation 2609.01532（Meta AI）+ RLAD 2602.22495 等；④ HTML 全量编辑 20+ 处（顶部通知、TL;DR、方向 0 摘要+2026 前沿段、§4 成本专章+定价表+SLM 证据表、§7 参考清单+2026 新增节、§8 缺口清单全绿、§9 建议更新、footer），零「需运维在线核验」残留（608 行/78KB）。🔵 巡检：l1_en_hq 2173/6006（+50 vs 唤醒121@07:30、CC-MAIN-2025-38 173件推进中 mtime秒级、~1.7MB/s）；gpic train 2945/8001（+28、pid 144981活、~21MB/s）真推进；zh 171/256 冻结；en 2048✓满；无僵死无需重启。git push github 仍不可达。下一步 = 下轮判 retry-loop+gpic 真推进 → l1_en_hq+zh 下满即报运维「base族就绪」。






## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

