# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验 → 🚀 Stable S0a 臂运行中(step 390/5000, loss 4.07, ~37.8s/iter, LR达峰, ETA ~Oct7 21:00)·loss稳定下降·✅✅SFT-2605全4shard完成(20.97B tok)!·✅SFT-Agent-2609 s0完成(2.58B tok)! 3/4 done(s0✅s2✅s3✅,s1🟡12.9G增长中)·baize_mix_eval.sh已备·白名单4项巡检正常·D-CLEAN-4已裁定保留不动
已完成:       §0.3/§0.4/§0.6/§0.7；SFT-2605下满一致；D-CLEAN-1/2/3/4(已裁定保留不动)；LIT_IDEAS_2026-10-05.html；✅base分词(22.05B tok)；✅✅SFT-2605全4shard分词(20.97B tok,79G)；✅baize_mix_eval.sh；🚀Stable S0a臂运行中(step390/5000,健康)；🔄SFT-Agent-2609分词(s0✅2.58B/s2✅/s3✅=3/4 done,s1🟡进行中)
当前动作:     唤醒139(20:45) S0a训练监控+Agent-2609分词进度+下载巡检+git proxy同步：① ⭐ S0a健康推进step390/5000 loss4.07(4.56@300→4.07@390稳定下降,LR=1.0e-3达峰,0NaN/0skip)~37.8s/iter GPU2-7 6卡38-86%util~39GB ETA=(5000-390)×37.8≈48.4h→~Oct7 21:00；② ✅ SFT-Agent-2609分词: s0✅(2.58B tok,69.9K docs,.bin10.3G+.idx+.json)+s2✅(1.23G)+s3✅(2.6G)+s1🟡(.bin12.9G增长中~2.2MB/s,PID166424,etime~1h48m,输入sft_General_Agent.parquet)→3/4完成；③ 下载l1_en_hq 3157/6006(+51)/zh 171(冻结)/gpic 3486tars/en 2048✓；④ ✅git fetch via proxy成功(无behind/ahead)；⑤ GPU0-1空闲(pretrain P-9.10已完成)
下一步:       ⏳等S0a 5000步完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s1分词完→Decay段全备料(SFT-2605✅20.97B+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推
阻塞:         ⏳ S0a训练中(5000步,ETA~Oct7 21:00,SAVE_INTERVAL=5000无中间ckpt)；🔄 SFT-Agent-2609 s1分词进行中(Decay段最后一项)；⚠️ zh下载冻结171/256；磁盘/nas_train 84%(34T free)；✅ D-CLEAN-4已裁定·保留不动
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
- **⭐⭐ LIT_IDEAS_2026-10-05.html（重做版）已产出**（唤醒 124 前）：**52 entries / 34 from 2024-2026 / 62% turnover vs 10-04 版 / 0 unverified**，用 cimi_search+cimi_fetch 从一开始就联网 discovery-driven。旧版 10-04 保留作对照。

### ⑨ 🔴 配比实验可行性核查（2026-10-05 运维分卡指令 · §0.6-B）— ✅ 可行性核查完成，⏳ 等 GPU2-7

> 运维 2026-10-05 批准：`.29` GPU2-7（6 卡）归 data 跑配比实验，与 pretrain 推理评测并行。**起跑前置 = 先等 P-9.8 armB(FP8) 跑完**。

**① GPU2-7 核查（10:26 实测原文）**：
```
ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'
→ 8 个 python 进程各 ~72GB，PID 4044610-4044617
ssh 10.239.2.29 'nvidia-smi --query-gpu=index,memory.used,memory.total,utilization.gpu --format=csv'
→ 8 卡各 100% util / ~72GB used
```
**结论**：❌ **GPU2-7 当前不空** —— P-9.8 armB 已于 ~09:49 完成，但 pretrain 随即启动 **P-9.9**（tensorwise FP8 1000 步跑，PID 4044534，~10:02 起，**占满 8 卡**，ETA ~15:00）。**不 kill（铁律）**，等 P-9.9 完。

**② 脚本/recipe 核查（✅ 全部就位）**：
- `run/baize_p5b_train.sh`：8 卡 TP1/DP8 模板（GBS=1024/seq=4094/WSD/bf16）—— **已复制为** `run/baize_mix_train_template.sh`（改为 6 卡 TP1/DP6，CUDA_VISIBLE_DEVICES=2,3,4,5,6,7）
- `code/BaiZe-ISEDA2027/pretrain_launcher.py`：✅ 支持 `--train-data-path` blend `[w, prefix, w2, prefix2, ...]`
- `code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py`：✅ parquet→.bin/.idx（需 `*.snappy.parquet` 后缀；base 文件名是 `*.parquet`→已用软链加 `.snappy` 后缀解决）

**③ 训练数据 .bin/.idx 核查（.29 上）**：
| 源 | 状态 | 路径 | token 估 |
|:--|:--|:--|--:|
| `p5b_l3` (L3 web) | ✅ 16 片 | `data/p5b_l3/p5b_l3_train_s{0..15}.bin` | ~20.6B |
| `anneal_code` | ✅ | `data/anneal_code.bin` (345M) | ~180M |
| `anneal_math2` | ✅ | `data/anneal_math2.bin` (1.7G) | ~860M |
| `ultrafineweb_l3_qa_700m` | ✅ | `data/ultrafineweb_l3_qa_700m.bin` (2.97G) | ~1.5B |
| `tokenizer_eod` | ✅ | `data/tokenizer_eod` | — |
| **base (ultrafineweb_en)** | 🔜 **分词中** | `data/mix_base/mix_base_train_s{0..3}` | ~21B（48 parquet→4 shard，4 进程并行 @ 10:32 起） |
| **SFT-2605** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-2605/data/` (1504 jsonl, 298G) | 需写 jsonl→text 转换器（chat 格式，preprocess_data.py 只认 parquet content 列） |
| **SFT-Agent-2609** | ❌ 未分词 | `/nas_inference/.../UltraData-SFT-Agent-2609/` (50 shard, 51G) | 同上 |

**④ 环境（✅）**：`PYTHONPATH=/nas_train/app.e0031982/omegaconf_230`；python=`/nas_train/app.e0031982/miniforge3/envs/py310/bin`；tokenizer=`/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash`；ssh .29 免密 ✅。

**⑤ 已创建脚本**：`run/baize_mix_tokenize_base.sh`（base 分词，已启动）+ `run/baize_mix_train_template.sh`（6 卡训练模板，待 GPU 就绪）。

**⑥ 下一步**：base 分词完成（ETA ~1-2h）→ 汇总 token 数 → P-9.9 完成（~15:00）→ GPU2-7 空 → 起 Stable 段 S0a 臂（base:code:math=88:8:4, 5000 步）→ ckpt→HF→lm_eval Table 2（8 集）。

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **§0.6-B 配比实验 🚀 进行中：Stable S0a 臂运行(step330/5000, loss4.36, LR达峰, ETA~Oct7 21:00)；§0.5/§0.6/§0.7 方案定稿✅；base分词22.05B✅；✅✅SFT-2605全4shard分词完成(20.97B tok,79G)；🔄SFT-Agent-2609分词中(s2✅s3✅,s0 7.8G/s1 7.7G进行中)；baize_mix_eval.sh✅；LIT_IDEAS_2026-10-05.html✅；SFT-2605下满一致✅；D-CLEAN-1/2/3/4✅** |
| WAITING | 1（🚀Stable S0a臂运行中(step330/5000, PID 2528081, GPU2-7, ~37.6s/iter, ETA~Oct7 21:00)；✅SFT-2605全4shard完成(20.97B)；🔄SFT-Agent-2609分词中(s2✅s3✅,s0/s1进行中)；下载l1_en_hq 3106/6006+zh 171冻结+gpic 3457tars+en 2048✓；baize_mix_eval.sh✅已备） |
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
- 2026-10-05 —— 唤醒 119（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 120（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 121（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 122（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 123（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 124（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 125（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 126（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 127（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒 128（已滚动归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒129~130（✅base分词完成22.05B tok+SFT s2✅3.58B+s1冲突修复+P-9.9仍占8卡+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒131~132（🚀S0a臂启动step60/5000+ETA更正312GPU·h/臂+baize_mix_eval.sh✅创建+SFT分词进度+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒133~134（⚠️S0a crash/重启→step84/5000+SFT分词进度+git proxy同步成功+下载巡检）（详情已归档至 daily-memories-data/2026-10-05.md）
- 2026-10-05 —— 唤醒135~136（S0a step145→200/5000+✅✅SFT-2605全4shard完成20.97B tok!+🔄Agent-2609分词启动+git pull proxy同步）（详情已归档）
- 2026-10-05 —— 唤醒137（19:23 S0a step260/5000 loss4.88 warmup完LR达峰+Agent-2609 s2✅s3✅ s0/s1进行中+下载l1_en_hq 3057+gpic 3556+内存滚动33.5KB→≤32KB+git proxy同步）：① ⭐ **S0a健康推进**：step260/5000, loss 4.88（稳定下降 9.55@20→7.16@60→5.45@200→4.88@260, warmup完LR=1.0e-3达峰, 0NaN/0skipped），~38s/iter, GPU2-7 6卡50-76%util ~39GB。**ETA=(5000-260)×38≈50.2h→~Oct7 21:00**。PID 2528081-2528090, TB events mtime 19:23(活跃)。② **🔄 SFT-Agent-2609分词进度**：s2✅(1.23G.bin+.idx+.json, 19:06) + s3✅(2.6G.bin+.idx+.json, 19:16) + s0🟡(3.3G.bin增长中, PID 166419) + s1🟡(3.5G.bin增长中, PID 166424)。→ **2/4 shard完成, s0/s1仍跑**。③ **下载巡检**：l1_en_hq **3057/6006**(+52, retry-loop PID 3076502活)、zh **171/256**(冻结)、gpic **3556 tars**(+29, PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步,无behind/ahead)。BAIZE_DATA_TASK.md无新指令(mtime未变)。⑤ 📉 **内存滚动**：MEMORY_DATA.md 33.5KB→目标≤32KB, 唤醒129-134详情已归档至 daily-memories-data/2026-10-05.md。⑥ GPU0-1 on .29空闲(4MiB,0%util)。磁盘 /nas_train 84%(34T free) /nas_inference 65%。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s0/s1完→Decay段全备料(SFT-2605✅+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。

 - 2026-10-05 —— 唤醒138（20:02 S0a step330/5000 loss4.36+Agent-2609 s0 7.8G/s1 7.7G进行中+下载l1_en_hq 3106+git proxy同步+D-CLEAN-4定案确认已更新）：① ⭐ **S0a健康推进**：step330/5000, loss 4.36（稳定下降 5.98@140→4.88@260→4.36@330, LR=1.0e-3达峰, 0NaN/0skipped），~37.6s/iter, GPU2-7 6卡31-85%util ~39GB。**ETA=(5000-330)×37.6≈48.7h→~Oct7 21:00**。PID 2528081-2528090(restart@16:32, 被 P-9.10 benchmark端口冲突kill后重启, /tmp/restart_mix_stable_s0a.sh)。② **🔄 SFT-Agent-2609分词**：s2✅(1.23G)+s3✅(2.6G)+s0🟡(7.8G.bin增长中, PID166419, ~67min)+s1🟡(7.7G.bin增长中, PID166424, ~67min)→2/4完成, s0/s1无.idx(未完)。③ 下载l1_en_hq **3106/6006**(+49, retry-loop PID 3076502活)、zh **171/256**(冻结)、gpic **3457 tars**(PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步)。⑤ **D-CLEAN-4定案**：BAIZE_DATA_TASK.md顶部新指令块确认「保留不动」→ MEMORY_DATA.md/DISK_CLEANUP_INVENTORY.md状态均已更新为「已裁定·保留不动」✅。环境隔离纪律+代理口径已读知。GPU0-1 on .29空闲(pretrain P-9.10已完成)。磁盘/nas_train 84%(34T free)。MEMORY_DATA.md=26.2KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s0/s1完→Decay段全备料→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。
 - 2026-10-05 —— 唤醒139（20:45 S0a step390/5000 loss4.07+✅Agent-2609 s0完成2.58B tok→3/4 done+下载l1_en_hq 3157+git proxy同步）：① ⭐ **S0a健康推进**：step390/5000, loss 4.07（稳定下降 4.56@300→4.46@310→4.42@320→4.36@330→4.29@340→4.25@350→4.20@360→4.15@370→4.13@380→4.07@390, LR=1.0e-3达峰, 0NaN/0skipped），~37.8s/iter, GPU2-7 6卡38-86%util ~39GB。**ETA=(5000-390)×37.8≈48.4h→~Oct7 21:00**。PID 2528081-2528090。② ✅ **SFT-Agent-2609分词**：**s0✅完成** — 2,578,877,685 tokens (2.58B) / 69,895 docs, .bin 10.3G + .idx 1.4M + .json (20:21完成)；s2✅(1.23G)；s3✅(2.6G)；**s1🟡仍跑** — .bin 12.9G增长中(~2.2MB/s, PID 166424, etime~1h48m, 输入=sft_General_Agent.parquet symlink, 无.idx=未完)。→ **3/4 shard完成**。③ 下载l1_en_hq **3157/6006**(+51, retry-loop PID 3076502+hf PID 3076519活)、zh **171/256**(冻结)、gpic **3486 tars**(PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步, 无behind/ahead)。⑤ GPU0-1 on .29空闲(4MiB, 0%util, pretrain P-9.10已完成)；GPU2-7 S0a训练中。磁盘/nas_train 84%(34T free) /nas_inference 65%。MEMORY_DATA.md=27.5KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s1完→Decay段全备料(SFT-2605✅20.97B+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。







## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

