# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.5/§0.6/§0.7 推进中 · 🔴白名单锁定(只下 l1_en_hq+zh+GPIC；en_v1_4 已停) · l1_en_hq 423/6000 · zh 171/256(待续) · gpic train 1988/8001+test 128✓ · D-CLEAN-4 复扫+⭐LLaVA-4B ckpt 专项(只盘点)
已完成:       §0.3 8源/§0.4 R2视觉/§0.6 配方/§0.7 停85M·复用·ETA；SFT-2605 下满一致；D-CLEAN 盘点/-2 ≈341G/-3 servers ≈972G/-4 复扫；⭐ LLaVA-OneVision-1.5 4B ckpt 专项(367 iter≈22 TiB 可回收)
当前动作:     唤醒91 巡检+D-CLEAN-4 ⭐LLaVA专项盘点：l1_en_hq 423/6000(+61)、gpic train 1988/8001(+34) 真推进；定位 code/LLaVA-OneVision-1.5 → 367 iter ckpt≈22 TiB；产出 §8+§9
下一步:       下轮判 retry-loop(3076502)+gpic(2426795) 真推进(僵死即 kill+重启)→ l1_en_hq(剩~420GB)+zh(剩85件107GB) 下满即报运维；D-CLEAN-4 候选(LLaVA≈22T/FineVision 4.3T/hell 1.24T/跨用户 3.4T)等运维拍板
阻塞:         无硬阻塞；⚠️ l1_en_hq 速率 ~1.5MB/s 偏慢(74MB 小文件+CDN 慢，非僵死)；磁盘 /nas_train 84%(Avail 35T)；🟡 D-CLEAN-4 候选全部等运维拍板(只盘点不删除)
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

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R research ✅ + R2 LLM 侧 ✅（8 源满填 / base vs L3 重叠 0% / P-8 86:10:4）+ R2 视觉侧 ✅（§0.4：本地 bytes 图文对实测 / 13 HF 候选 / 前 3 推荐）+ phase5 isolation v0.3 + phase1/2 脚本就绪；§0.5/§0.6/§0.7 推进中（§0.6 配方✅ / §0.7 停85M·复用·ETA✅ / SFT-2605 下满一致✅）** |
| WAITING | 1（下载中：白名单锁定——retry-loop 3076502+hf 3076519 先拉 l1_en_hq(423/6000)+zh(171/256 待续)；gpic 2426795 train 1988/8001+test 128✓；en 2048/2048 满；en_v1_4 已停(489 保留)；LLaVA 85M 停无进程；D-CLEAN-4 大盘复扫+⭐LLaVA-4B ckpt 专项(367 iter≈22 TiB 可回收) done（只盘点，Avail 35T/84%）；重 I/O 推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-04 |

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
- 2026-10-04 —— 唤醒 84（白名单 4 项巡检，无假活、无重启）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base **550476**（etime ~4h48m）真推进：拉 **zh**（256 文件 flat/302GiB=324GB）已 **152/256**、0 .incomplete（part-152-of-256@04:28，~1.265GB/件；上轮 137@03:57→本轮 +15 件/31min ≈~10MB/s；write_bytes 累计 193GB）；**l1_en_hq=0/6006**（445.1GiB=478GB，随 zh 之后按 HF 树序串行执行，目录尚未创建）。🔵 gpic **2426795**（etime ~1d10h）真推进：train **1745/8001** + test 128/128✓、0 .incomplete（gpic_train_01744.tar@04:29 ~1.55GB/件；上轮 1731@03:56→+14 件/33min ≈~11MB/s；write_bytes 累计 1.5TB）。🔴 en_v1_4 无进程（✅ 已停，488 parquet/≈41.5GB 保留未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA（@~10-11MB/s）：zh 剩 104 件≈130GB≈3.7h；l1_en_hq 478GB≈13h → **l1_en_hq+zh 合计 ≈17h≈0.7 天**（吻合运维 1–2 天预估）；gpic 剩 6256 件≈9.4TiB @~11MB/s≈10 天（波动 8–16 天）。磁盘 /nas_train 86%(31T)、/nas_inference 59%(19T)、/nas_user 74%(29T) 均够，WAITING 保持 1。📉 MEMORY 体量 26KB ≤32KB，本轮无需滚动。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 l1_en_hq/zh(550476)、gpic(2426795) 真推进（僵死即 kill+重启）→ zh(剩104件)+l1_en_hq(478GB) 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 85（🔴 base 进程崩溃，已重启 + 白名单 4 项巡检）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔴 **事件**：base 进程 **550476** 已在两次唤醒间**崩溃退出**（`ps -p 550476` = 空）—— `download_l1_zh.log` tail 显示在 `ultrafineweb-zh-part-172-of-256` 处 `ConnectionError: Network error: ... us.aws.cdn.hf.co/xorbs/...`（**hf CLI 无自动重试，直接崩**）。**处置（已重启，标「已重启」）**：重启为 **retry-loop**（bash wrapper pid **3076502** + hf 子进程 **3076519**，`--include 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*'` → `/nas_train/.../Ultra-FineWeb`，300 次重试、失败 `sleep 30` 自愈，log=`download_l1_zh.log`）。**重启后顺序反转（符合运维 ④ 优先级 l1_en_hq>zh）**：先拉 **l1_en_hq** `CC-MAIN-2025-30` part-0001-of-1000 ✓（**73.8MB/件**，05:05:42）→ part-0002 处 **CDN 慢段**（`.incomplete` 0 字节 ~1.5min、但进程存活 `Sl` + 5 ESTAB 到代理 `172.19.92.25:13128`、mtime 05:06:54 活跃，**非僵死**，retry-loop 崩即自愈）。🔵 zh **171/256**、0 .incomplete（上轮 152→171，即崩溃前又 +19 件）。🔵 gpic **2426795**（etime ~1d11h）真推进：train **1759/8001**（上轮 1745→+14）+ test 128/128✓、0 .incomplete。🔴 en_v1_4 无进程（✅ 已停，488 parquet/≈41.5GB 保留未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA：zh 剩 85 件≈107GB + l1_en_hq 6000 件≈443GB ≈ **550GB**，@历史 7-14MB/s ≈ 11-22h（当前 l1_en_hq CDN 偏慢、按恢复常态计）→ 下满即「MiniCPM5 base 族就绪」；gpic 剩 6242 件≈9.4TiB。磁盘 /nas_train 86%(31T)、/nas_inference 59%(19T)、/nas_user 74%(29T)、/data 4%(6.8T) 均够，WAITING 保持 1。📉 MEMORY 体量 28KB ≤32KB，本轮无需滚动。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop(3076502) 真推进（僵死即看 retry 是否自愈；连崩则查 CDN/代理链路）→ l1_en_hq+zh 下满即报运维 → gpic 续下至 8001 tar。
- 2026-10-04 —— 唤醒 86（白名单 4 项巡检，无假活、无重启）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~2h06m）真推进：重启后**顺序反转、先拉 l1_en_hq**（符合运维 ④ 优先级 l1_en_hq>zh）——**l1_en_hq = 177/6006**（CC-MAIN-2025-30 part-0177-of-1000 在途，~74.1MB/件；part-0001@05:05:42→part-0177@07:10:40 = 177 件/125min，近 5 件 cadence 27–40s/件 ≈ **~2.2MB/s**；⚠️ 远慢于 zh/gpic 历史 7–14MB/s，疑小文件(74MB)连接开销 + 该 CDN 端点偏慢，**非僵死**、进程存活 + .incomplete mtime 07:10:41 逐件推进，retry-loop 崩即自愈故不重启）。🔵 zh **171/256**、0 .incomplete（冻结于 04:59，随 l1_en_hq 之后串行续）。🔵 gpic **2426795**（etime ~1d13h）真推进：train **1850/8001** + test 128/128✓、1 .incomplete=在途（gpic_train_01849.tar@07:10 ~1.59GB/件；上轮 1759@05:07→+91 件/123min ≈ **~20MB/s**，因 base 让出带宽）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈41.5GB 保留未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA：l1_en_hq 剩 5829 件≈431GB @~2.2MB/s ≈ **54h≈2.3 天**（⚠️ 已超运维 1–2 天预估；若速率回升 7–10MB/s 则 ≈12–17h）；zh 剩 85 件≈107GB @~10MB/s ≈3h → **l1_en_hq+zh 合计 ≈2.4 天（偏慢口径）/ ≈0.7 天（乐观口径）**；gpic 剩 6151 件≈9.8TiB @~20MB/s ≈ **6 天**（优于前估 8–16 天）。磁盘 /nas_train 86%(31T)、/nas_inference 60%(19T)、/nas_user 74%(29T)、/data 4%(6.8T) 均够，WAITING 保持 1。📉 MEMORY 滚动：唤醒 76/77 迁 daily-memories-data（原文不改），体量回到 ≤32KB。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop(3076502)、gpic(2426795) 真推进（僵死即 kill+重启；l1_en_hq 连崩则查 CDN/代理链路）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。
- 2026-10-04 —— 唤醒 87（白名单 4 项巡检，无假活、无重启）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~2h43m）真推进：**l1_en_hq = 231/6006**（CC-MAIN-2025-30 part-0232-of-1000 在途，~74.1MB/件；上轮 177@07:10→本轮 231@07:48 = +54 件/38min ≈ **~1.8MB/s**；log 逐件 `Download complete` 连续推进、进程存活 `Sl`、write_bytes 16.9G 递增、retry-loop 崩即自愈 → **非僵死，不重启**；⚠️ 速率仍偏慢、疑 74MB 小文件连接开销 + 该 CDN 端点慢）。🔵 zh **171/256**、0 .incomplete（冻结于 04:59，随 l1_en_hq 之后串行续）。🔵 gpic **2426795**（etime ~1d13.5h）真推进：train **1877/8001** + test 128/128✓、1 .incomplete=在途（.cache）（上轮 1850@07:10→+27 件/38min ≈ **~19MB/s**）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈41.5GB 保留未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA：l1_en_hq 剩 5775 件≈426GB @~1.8MB/s ≈ **2.9 天**（⚠️ 已超运维 1–2 天预估；若回升 7–10MB/s 则 ≈12–17h）；zh 剩 85 件≈107GB @~10MB/s ≈3h → **l1_en_hq+zh 合计 ≈3 天（偏慢口径）/ ≈0.7 天（乐观口径）**；gpic 剩 6124 件≈9.8TiB @~19MB/s ≈ **6.3 天**。磁盘 /nas_train 86%(31T)、/nas_inference 60%(19T)、/nas_user 74%(29T)、/data 4%(6.8T) 均够，WAITING 保持 1。📉 MEMORY 体量 31KB ≤32KB，本轮无需滚动。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop(3076502)、gpic(2426795) 真推进（僵死即 kill+重启；l1_en_hq 连崩则查 CDN/代理链路）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。
- 2026-10-04 —— 唤醒 88（白名单 4 项巡检，无假活、无重启）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~3h19m）真推进：**l1_en_hq = 278/6006**（CC-MAIN-2025-30 part-0279-of-1000 在途，~74.1MB/件；上轮 231@07:48→本轮 278@08:23 = +47 件/35min ≈ **~1.7MB/s**；log 逐件 `Download complete` part-0272→0278 连续推进、进程存活 `Sl`、write_bytes 20.3G 递增、retry-loop 崩即自愈 → **非僵死，不重启**；⚠️ 速率仍偏慢、疑 74MB 小文件连接开销 + 该 CDN 端点慢）。🔵 zh **171/256**、0 .incomplete（冻结，随 l1_en_hq 之后串行续）。🔵 gpic **2426795**（etime ~1d14h）真推进：train **1903/8001** + test 128/128✓、1 .incomplete=在途 gpic_train_01902.tar@08:22（~1.6GB/件；上轮 1877@07:48→+26 件/35min ≈ **~20MB/s**）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈41.5GB 保留 CC-MAIN-2013-20 未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA：l1_en_hq 剩 5728 件≈424GB @~1.7MB/s ≈ **~2.9 天**（⚠️ 已超运维 1–2 天预估；若回升 7–10MB/s 则 ≈12–17h）；zh 剩 85 件≈107GB @~10MB/s ≈3h → **l1_en_hq+zh 合计 ≈3 天（偏慢口径）/ ≈0.7 天（乐观口径）**；gpic 剩 6098 件≈9.8TiB @~20MB/s ≈ **~5.7 天**。磁盘 /nas_train 86%(31T)、/nas_inference 60%(19T)、/nas_user 74%(29T)、/data 4%(6.8T) 均够，WAITING 保持 1。📉 MEMORY 体量 31KB ≤32KB，本轮无需滚动。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop(3076502)、gpic(2426795) 真推进（僵死即 kill+重启；l1_en_hq 连崩则查 CDN/代理链路）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 89（白名单 4 项巡检，无假活、无重启）：复核运维指令未变（下载白名单锁定：只下 l1_en_hq+zh+GPIC、停 en_v1_4；D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~3h51m）真推进：**l1_en_hq = 325/6000**（CC-MAIN-2025-30 part-0325-of-1000 在途，~74.1MB/件；上轮 278@08:23→本轮 325@08:56 = +47 件/33min ≈ **~1.75MB/s**；log 逐件 `Download complete` part-0312→0323 连续推进、进程存活 `Sl`、retry-loop 崩即自愈 → **非僵死，不重启**；⚠️ 速率仍偏慢、疑 74MB 小文件连接开销 + 该 CDN 端点慢；分母 6006→**6000** 更正=6 子目录×1000 件）。🔵 zh **171/256**、0 .incomplete（冻结，随 l1_en_hq 之后串行续）。🔵 gpic **2426795**（etime ~1d14.7h）真推进：train **1926/8001** + test 128/128✓、1 .incomplete=在途（上轮 1903@08:23→+23 件/33min ≈ **~19MB/s**）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈41.5GB 保留 CC-MAIN-2013-20 未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满（1T tok）。✅ SFT-2605 1504/1504 intact。✅ servers GONE。ETA：l1_en_hq 剩 5675 件≈420GB @~1.75MB/s ≈ **~2.9 天**（⚠️ 已超运维 1–2 天预估；若回升 7–10MB/s 则 ≈12–17h）；zh 剩 85 件≈107GB @~10MB/s ≈3h → **l1_en_hq+zh 合计 ≈3 天（偏慢口径）/ ≈0.7 天（乐观口径）**；gpic 剩 6075 件≈9.5TiB @~19MB/s ≈ **~6 天**。磁盘 /nas_train 86%(31T)、/nas_inference 60%(19T)、/nas_user 74%(29T) 均够，WAITING 保持 1。📉 MEMORY 滚动：唤醒 78–83 共 6 条迁 daily-memories-data/2026-10-04.md（原文不改），体量 33.7KB→22.8KB(≤32KB)。⚠️ 安全：gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop(3076502)、gpic(2426795) 真推进（僵死即 kill+重启；l1_en_hq 连崩则查 CDN/代理链路）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 90（🔴 D-CLEAN-4 大盘复扫 + 白名单 4 项巡检）：复核运维指令新增 **D-CLEAN-4**（`/nas_train` 清理 → sudo 盘点各目录大小、找可删除大目录、重点本用户目录，**只盘点不删除**）；下载白名单不变（只下 l1_en_hq+zh+GPIC）。**D-CLEAN-4 盘点（未删任何东西）**：`df` /nas_train 177T/207T(86%、Avail 31T)；`sudo -n true`=需密码→未 sudo（跨用户 root/权限收紧目录只读顶层）；`ls /nas_train/*/`+stat 见 33 顶层 mtime/owner。本用户一级 du（超时大项用二级钻取补）**新发现 🟡 大候选**：`datasets/FineVision` 4.32T、`code/hell/LLaVA-OneVision-1.5` 1.24T、`datasets/HuggingFaceFW` 1.24T、`conceptual-captions` 1.13T、`code/chip-mllm` 896G、`code/LLaVA` 716G、`code/LLaVA-OneVision-2` 650G、`chip_expert` 468G(4× chipexpert-cn 快照)、`models` 452G、`circuitvision-encoder` 244G；🔴 不可动=mvp-lab 26T/`datasets/openbmb` 2.74T(下载中)/BaiZe-ISEDA2027 421G(nemo_exp 280G live P-5b+P-9)/eda_fastmcp/baize-vision/repo/harness/miniforge3。跨用户：`wangcongtao` 2.42T(2026-01-13)、`app.e0025692` 946G(2026-02-14)。可回收分档：🟢≈0.6G、🟡本用户≈**11.4T**、🟡跨用户≈**3.4T**。产出 §8。🔵 base retry-loop **3076502**+hf **3076519** 真推进：**l1_en_hq 362/6000**（CC-MAIN-2025-30 part-0362-of-1000；上轮 325@08:56→362 ≈ +37 件/~40min ≈ ~1.5MB/s，非僵死不重启）；zh 171/256 冻结(随 l1_en_hq 后串行)；gpic **2426795** 真推进：train 1954/8001+test 128✓（上轮 1926→+28/~40min）。en 2048✅满、en_v1_4 无进程(488 保留)、SFT-2605 intact、servers GONE。磁盘 31T/86% 够。📉 MEMORY ≈28KB≤32KB 无需滚动。git 本轮回写后提交。下一步=下轮判 retry-loop+gpic 真推进→l1_en_hq+zh 下满报运维；D-CLEAN-4 候选(FineVision/hell/chip_expert/wangcongtao+app.e0025692 ≈9.5T)等运维拍板。

- 2026-10-04 —— 唤醒 91（🔴 D-CLEAN-4 ⭐用户点名 LLaVA-4B ckpt 专项 + 白名单巡检）：复核指令：D-CLEAN-4 追加「⭐用户点名 LLaVA-OneVision-1.5 4B ckpt 绝大部分可删」→ 单列专节定位盘点（产出 §9）。**专项结论（只盘点不删除）**：`/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/`（203 项，最后活动 09-25）= Megatron 训练 run `stage_1.5_*` 21 dir(299 iter) + `stage_2_*` 23(68 iter) + HF `4B-*` 23 + `*_release*` 19 + `checkpoints/baize_4b` 142G；**单 iter ckpt ≈61.6GiB**（804/13·928/15·1.1T/18·186/3 一致）→ **367 iter ≈22 TiB** + HF 45 dir 396GiB ≈ **总 22.5 TiB · 🟢可回收≈22 TiB**。安全：fuser 无训练/inference（他人 app.t0002965 tensorboard 指其自身 outputs）；BaiZe repo grep 0 命中。🔵 base **3076502/3076519** 真推进 l1_en_hq **423/6000**(+61)；zh 171/256 冻结；gpic **2426795** train **1988/8001**+test 128✓(+34)。en 2048✓、en_v1_4 489 停、servers GONE。磁盘 84%(Avail 35T)。📉 MEMORY ≈30KB 无需滚动。git 提交。下一步=下轮判 retry-loop+gpic 真推进→l1_en_hq+zh 下满报运维；D-CLEAN-4 候选(LLaVA 22T/FineVision 4.3T/hell 1.24T/跨 3.4T)等运维拍板。

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

