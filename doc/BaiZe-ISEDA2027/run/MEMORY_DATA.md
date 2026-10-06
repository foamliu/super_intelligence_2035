# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.6-B 配比实验改道 → Step0 kill完成 + 代理模型标定完成 + held-out bin创建 + BO搜索脚本就位 + smoke test通过 → 待启动200trial搜索(GPU2-7)
已完成:       §0.3/§0.4/§0.6/§0.7；SFT-2605下满一致(20.97B tok)；SFT-Agent-2609全4shard(4/4 done)；base分词(22.05B tok)；LIT_IDEAS HTML；D-CLEAN-1/2/3/4(保留不动)；🔴 S0a 2.2B单臂已kill(2026-10-06 08:06)；baize_mix_stable_s0a.sh标注DEPRECATED；mamba2_hybrid_proxy/(provider+recipe)创建；pretrain_proxy_launcher.py创建；baize_mix_calibrate.sh创建；标定完成(LR=1e-3最优, 92.7M params, s/step=1.5s, T≈691>400)；create_heldout_bins.py创建+运行(held_out_base/code/math各~2M tok)；baize_mix_optuna.py创建(GP-EI surrogate, 6并行trial, SQLite存储, 中位数pruning, ckpt自动清理)；smoke test通过(20步, s/step=1.4s warmup后, val loss正确提取)
当前动作:     唤醒146(08:50) ①held-out bin创建完成(base:2451doc/2.0M tok, code:1451doc/2.0M tok, math:4618doc/2.0M tok)；②baize_mix_optuna.py创建完成(GP-EI替代TPE, .29离线无法pip install optuna, 使用sklearn GPR+scipy EI)；③smoke test通过(GPU2, 20步, blend=0.85/0.08/0.07, train loss 10.72→8.70, val loss 9.34→8.23, s/step=1.4s warmup后)；④ checkpoint自动清理已加入(避免200trial×400MB=80GB填盘)；⑤ 待运维指令启动200trial BO搜索
下一步:       ⓪ 标定结果→实测s/step→反推24h trial数→锁定模型尺寸(§③.6阶梯表)；① 创建held-out验证bin(3域各1-2M token, hash切分, §③.7.①)；② Optuna study(TPESampler+MedianPruner, sqlite storage, 6卡并行trial, §④搜索空间)；③ Day1搜Stable段(base:code:math simplex)；④ Day2搜Decay段(SFT占比+SFT内部5类)
阻塞:         🔄标定中(等待3个LR trial的50步完成, ETA~5-10min)；held-out bin待创建；optuna待装独立env
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
| PHASE | **§0.6-B 配比实验改道 → 🔴Step0 kill完成+代理模型(h=512/L=14/96.8M)就位+🔄标定中(GPU2-4, LR sweep)→Optuna BO搜索；§0.5/§0.6/§0.7定稿✅；base22.05B✅；SFT-2605(20.97B)✅；Agent-2609(4/4)✅；baize_mix_eval.sh✅；D-CLEAN-1/2/3/4✅保留不动** |
| WAITING | 1（🔄标定中：GPU2-4 跑3×LR(3e-4/1e-3/3e-3)×50步，96.8M proxy h512/L14，ETA~5min；🔴S0a已kill(step1470/5000作废, ~100 GPU·h浪费, GPU2-7全释放); held-out bin待创建; optuna study脚本待写） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.29`（GPU2-4标定中，GPU0-1/5-7空闲） |
| 更新 | 2026-10-06 |

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
- 2026-10-05 —— 唤醒137（19:23 S0a step260/5000+Agent-2609 2/4+下载巡检+内存滚动）（详情已归档至 daily-memories-data/2026-10-05.md）

- 2026-10-05 —— 唤醒138（20:02 S0a step330/5000+Agent-2609 s0/s1进行中+D-CLEAN-4定案确认）（详情已归档至 daily-memories-data/2026-10-05.md）
 - 2026-10-05 —— 唤醒139（20:45 S0a step390/5000 loss4.07+✅Agent-2609 s0完成2.58B tok→3/4 done+下载l1_en_hq 3157+git proxy同步）：① ⭐ **S0a健康推进**：step390/5000, loss 4.07（稳定下降 4.56@300→4.46@310→4.42@320→4.36@330→4.29@340→4.25@350→4.20@360→4.15@370→4.13@380→4.07@390, LR=1.0e-3达峰, 0NaN/0skipped），~37.8s/iter, GPU2-7 6卡38-86%util ~39GB。**ETA=(5000-390)×37.8≈48.4h→~Oct7 21:00**。PID 2528081-2528090。② ✅ **SFT-Agent-2609分词**：**s0✅完成** — 2,578,877,685 tokens (2.58B) / 69,895 docs, .bin 10.3G + .idx 1.4M + .json (20:21完成)；s2✅(1.23G)；s3✅(2.6G)；**s1🟡仍跑** — .bin 12.9G增长中(~2.2MB/s, PID 166424, etime~1h48m, 输入=sft_General_Agent.parquet symlink, 无.idx=未完)。→ **3/4 shard完成**。③ 下载l1_en_hq **3157/6006**(+51, retry-loop PID 3076502+hf PID 3076519活)、zh **171/256**(冻结)、gpic **3486 tars**(PID 144981活)、en **2048✓**。④ ✅ **git fetch via proxy成功**(与origin/main同步, 无behind/ahead)。⑤ GPU0-1 on .29空闲(4MiB, 0%util, pretrain P-9.10已完成)；GPU2-7 S0a训练中。磁盘/nas_train 84%(34T free) /nas_inference 65%。MEMORY_DATA.md=27.5KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 21:00)→ckpt→HF→lm_eval Table2(8集)；判Agent-2609 s1完→Decay段全备料(SFT-2605✅20.97B+Agent✅)→起Decay臂；填DATA_MIX_RECIPE.md实测值；下载续推。
 - 2026-10-06 —— 唤醒140（01:13 ⭐report_data_mix_s0a.html实时更新+S0a step820/5000 loss3.23+✅✅Agent-2609全4shard完成→Decay全料就绪+下载巡检+git proxy同步）：① ⭐ **S0a健康推进**：step820/5000, loss 3.23（稳定下降 10.84@10→4.93@250(LR达峰)→3.57@600→3.40@700→3.25@800→3.23@820, LR=1.0e-3, 0NaN/0skip），~37.6s/iter, GPU2-7 6卡30-82%util ~39GB。**ETA=(5000-820)×37.6≈43.7h→~Oct7 20:53**。PID 2525319(etimes=31703≈8h48m)。② ✅✅ **SFT-Agent-2609分词全完成**：s0✅(2.58B tok)+**s1✅**(.bin 18G+.idx 6.2M+.json, 21:27完成)+s2✅(1.23G)+s3✅(2.6G)→**4/4 done! Decay段全料就绪**。③ ✅ **report_data_mix_s0a.html已更新**（运维指令2026-10-05深夜2⑤）：实时数据step760→820/loss3.30→3.23/ETA→Oct7 20:53/GPU表/SVG图表修正(82个数据点逐10步, 修正了旧版y坐标映射错误)/日志附录/里程碑表。纯CPU写作,不占GPU。④ 下载l1_en_hq巡检(进行中)。⑤ ✅git fetch via proxy成功(无behind/ahead)。GPU0-1空闲。磁盘/nas_train 84%。MEMORY_DATA.md≈29KB(≤32KB✓)。下一步=⏳等S0a完(~Oct7 20:53)→ckpt→HF→lm_eval Table2(8集)；✅Decay段全料就绪→可起Decay臂(SFT占比搜索)；填DATA_MIX_RECIPE.md实测值。
 - 2026-10-06 —— 唤醒145（08:06 🔴 Step0 kill S0a 2.2B单臂 → 代理模型创建 → 标定启动 → MEMORY/GPU更新）：① 🔴 **Step0 kill**（运维指令 §「Step 0」kill）：
   - **kill 目标**：`mix_stable_s0a` = watchdog PID 2525272 → torchrun PID 2525319 → 6 workers 2528081-2528090
   - **kill 命令**：`kill 2525272 && sleep 2 && kill 2525319 2528081 2528082 2528083 2528084 2528085 2528086 2528087 2528088 2528089 2528090`
   - **GPU 释放验证**：`nvidia-smi` → GPU2-7 all 0 MiB / 0% util ✅
   - **watchdog restart script**：`/tmp/restart_mix_stable_s0a.sh` 已 `rm -f` ✅
   - **DEPRECATED**：`baize_mix_stable_s0a.sh` 已加 `exit 1` + 注释 `DEPRECATED: killed 2026-10-06 per ops §Step0` ✅
   - **作废**：step1470/5000 loss2.76，~100 GPU·h 浪费（已记录教训）→ 改道代理模型 BO 搜索
   ② **代理模型创建**：
   - `mamba2_hybrid_proxy/__init__.py` ✅
   - `mamba2_hybrid_proxy/provider.py`：`NVIDIAMambaHybridModelProviderProxy` — h=512, L=14, pattern="M-M-M--M-M*-M-", tie embed, GQA 4Q/1KV, mamba_groups=2, ce_fusion=True
   - `mamba2_hybrid_proxy/recipe.py`：`pretrain_config` — WSD scheduler, GBS=16, seq=2048, train_iters=13700, bf16_mixed
   - `pretrain_proxy_launcher.py`：standalone argparse launcher（复用 bridge_compat + forward_step）
   - `baize_mix_calibrate.sh`：3 LR × 50 steps 并行（GPU2=3e-4, GPU3=1e-3, GPU4=3e-3）
   - **修正**：`context_model_parallel_size` → `context_parallel_size`（dataclass 字段名差异）
   ③ 🔄 **标定进行中**：GPU2/3/4 各 ~6.5GB / 54-86% util（对比 2.2B 的 39GB！）；日志在 /tmp/baize_calib_lr{0,1,2}.log；ETA ~5min
   ④ 下一步：等标定完成 → 实测 s/step → 锁定模型尺寸 → 创建 held-out bin → 写 Optuna study → Day1/Day2 搜索

### 标定结果（2026-10-06 08:22 完成）

| LR | s/step (avg) | loss@50 | grad norm@50 | TFLOP/s |
|---|---|---|---|---|
| 3e-4 | 1.57s | 7.692 | 0.472 | 14.8 |
| **1e-3** | **1.56s** | **7.081** | **0.509** | 15.0 |
| 3e-3 | 1.60s | 7.274 | 0.325 | 14.7 |

- **s/step ≈ 1.5s**（目标 0.095s，差 16×，瓶颈=data loading，GPU util 仅 ~15 TFLOP/s / 1000）
- **精确参数量**：`sum(p.numel())` = **92,711,712** (~92.7M)
  - Embed (tied): 129408×512 = 66.3M (71.5%)
  - Body: 26.5M (28.5%)
  - 比例 2.220B/92.7M ≈ 1/24（目标 1/23，偏差 ~4%）
  - vocab: 129281→padded 129408 (÷128)
  - 层分配: 6 Mamba + 1 attention + 7 MLP = 14 ✓
- **Trial 预算**：500 步/trial × 1.5s = 12.5 min/trial × 6 GPU → **T≈691 > 400 ✅**（锁定 h=512/L=14，不需缩尺）
- **LR 选择**：LR=1e-3（与 2B recipe 一致，loss@50 最优）
- **校准 checkpoint 已清理**（`rm -rf nemo_experiments/calib_lr*`）

### Held-out 验证集 + BO 搜索脚本 + Smoke Test（2026-10-06 08:50 完成）

#### ① create_heldout_bins.py — 已创建并运行
- 脚本位置：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/create_heldout_bins.py`
- 方法：hash-split（`md5(salt:doc_idx) % 100 < valid_pct`），salt=42，valid_pct=5%
- 用 `_IndexReader(path, multimodal=False)` 读 .idx，`numpy.memmap` 读 .bin，`IndexedDatasetBuilder` 写出
- **运行结果**：
  | 域 | 源 | docs | tokens | 文件大小 |
  |---|---|---|---|---|
  | base | mix_base_train_s0 | 2451 | 2,003,023 | 7.7M bin + 48K idx |
  | code | anneal_code | 1451 | 2,000,625 | 7.7M bin + 29K idx |
  | math | anneal_math2 | 4618 | 2,000,101 | 7.7M bin + 91K idx |
  | **合计** | | **8520** | **6,003,749** | **~24M** |
- 输出路径：`data/heldout/held_out_{base,code,math}.{bin,idx}`

#### ② baize_mix_optuna.py — 已创建并通过语法检查
- 脚本位置：`run/baize_mix_optuna.py`（336行）
- **替代 Optuna**：`.29` 离线（`pip install optuna` → Network is unreachable），改用 **GP-EI**（sklearn GPR + scipy Expected Improvement）
  - sklearn 1.7.2 + scipy 1.15.3 已可用
  - Matern(ν=2.5) kernel + L-BFGS-B 优化 EI（20 random restarts）
  - 前 12 trial 随机采样，之后 GP-EI 引导
  - 中位数 pruning：intermediate val loss > 1.5× 已完成 trial 中位数 → kill
- **搜索空间**：
  - Stable (Day1)：web ∈ [0.80, 0.95], code ∈ [0.03, 0.12], math = 1 - web - code
  - Decay (Day2)：sft_pct ∈ [0.40, 0.80] + 4D SFT class simplex（待 SFT shard 准备后启用）
- **训练参数**：500 steps/trial, eval_interval=100, eval_iters=10, GBS=16, seq=2048, LR=1e-3, WSD(50 warmup/450 decay), bf16_mixed
- **并行**：6 GPU（2-7）ThreadPoolExecutor + Queue 管理 GPU 分配
- **存储**：SQLite（`nemo_experiments/mix_search/mix_search.db`），支持断点续跑
- **Checkpoint 自动清理**：trial 结束后 `shutil.rmtree(ckpt_dir)`，避免 200×400MB=80GB 填盘
- **日志解析**：`VAL_LOSS_RE = r"validation loss at iteration\s+(\d+).*?lm loss value:\s*([\d.eE+-]+)"`

#### ③ Smoke Test — 通过 ✅
- GPU2, 20 steps, blend=0.85/0.08/0.07, eval@10/20
- **结果**：
  | 指标 | 值 |
  |---|---|
  | s/step (warmup, 前10步) | 9.7s |
  | s/step (warmup后, 后10步) | **1.4s** ✅ |
  | train loss (step 10→20) | 10.72→8.70 |
  | val loss (step 10→20) | 9.34→8.23 |
  | log parser 提取 | `{10: 9.344584, 20: 8.227096}` ✅ |
- Smoke test checkpoint 已清理

#### ④ 启动命令（待运维批准）
```bash
ssh 10.239.2.29 'export PYTHONPATH=/nas_train/app.e0031982/omegaconf_230; \
  nohup /nas_train/app.e0031982/miniforge3/envs/py310/bin/python \
  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_optuna.py \
  --phase stable --n-trials 200 --gpus 2,3,4,5,6,7 --n-random 12 \
  > /tmp/mix_search_main.log 2>&1 &'
```
- ETA：200 trials × 12.5 min / 6 GPU ≈ 6.9h
- 监控：`sqlite3 nemo_experiments/mix_search/mix_search.db "SELECT id,params,loss,status FROM trials ORDER BY loss LIMIT 10"`

## 🔴 事故复盘 — S0a 2.2B 单臂 kill（2026-10-06 08:06）

> **背景**：运维指令 §「Step 0」要求 kill `mix_stable_s0a`，改用代理模型 BO 搜索路线。
> **决策理由**：单臂 2.2B 跑 5000 步 × 6 卡 ≈ 310 GPU·h 才出一个数据点；代理模型 96.8M 单卡 50 步 ≈ 5 min 出一个数据点，T≥400 才有统计意义。
> **浪费**：step1470/5000 ≈ 1470/5000 × 310 ≈ 91 GPU·h（~100 GPU·h，保守估计含 overhead）。
> **教训**：数据配比搜索不应直接跑 full-size 模型，应先小 proxy 模型快速扫配比，再选 top-K 跑 full-size 确认。
> **kill 原始输出**：
> ```
> # kill watchdog → torchrun → 6 workers
> $ kill 2525272 && sleep 2 && kill 2525319 2528081 ... 2528090
> # GPU verify
> $ nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv,noheader
> 2, 0 MiB, 0 %    ← released ✅
> 3, 0 MiB, 0 %    ← released ✅
> 4, 0 MiB, 0 %    ← released ✅
> 5, 0 MiB, 0 %    ← released ✅
> 6, 0 MiB, 0 %    ← released ✅
> 7, 0 MiB, 0 %    ← released ✅
> # rm restart script
> $ rm -f /tmp/restart_mix_stable_s0a.sh
> ```







## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

