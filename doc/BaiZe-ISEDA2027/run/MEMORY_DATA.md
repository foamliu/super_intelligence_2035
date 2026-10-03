# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.5/§0.6/§0.7 推进中 · base-en 2048/2048 下满(1T tok) · base-rest(2061268) en_v1_4 355/512 · gpic train 1556/8000+test✓ · D-CLEAN 全完成(回收≈1.31TiB)
已完成:       §0.3 8源/§0.4 R2视觉/§0.6 配方/§0.7 停85M·复用·ETA 交付；SFT-2605 下满一致；D-CLEAN 盘点/D-CLEAN-2 ≈341G/D-CLEAN-3 servers ≈972G；base-en 2048/2048 下满
当前动作:     唤醒 73：轻 I/O 巡检 —— base-rest 2061268 真推进（en_v1_4 首快照 CC-MAIN-2013-20 355/512 ~1.9MB/s）；gpic 2426795 真推进（train 1556/8000+test 128✓ ~19MB/s）
下一步:       持续巡检 base-rest/gpic 真推进（僵死即 kill+重启）；🔑 en_v1_4(6.7TB≈41天) 非 P-8 必需（base-en 1T tok 已够）→ 待运维拍板：停 en_v1_4 只续 l1_en_hq(478G)+zh(324G) / 继续全下 / 停 gpic 让带宽
阻塞:         无硬阻塞；磁盘 /nas_train 85%（Avail 32T）；⚠️ 待运维拍板 en_v1_4 是否全下（~6.7TB@1.9MB/s≈41天）
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

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R research ✅ + R2 LLM 侧 ✅（8 源满填 / base vs L3 重叠 0% / P-8 86:10:4）+ R2 视觉侧 ✅（§0.4：本地 bytes 图文对实测 / 13 HF 候选 / 前 3 推荐）+ phase5 isolation v0.3 + phase1/2 脚本就绪；§0.5/§0.6/§0.7 推进中（§0.6 配方✅ / §0.7 停85M·复用·ETA✅ / SFT-2605 下满一致✅）** |
| WAITING | 1（下载中：base-rest 3 config en_v1_4+l1_en_hq+zh ≈7.54T（pid 2061268，/nas_train；en_v1_4 首快照 355/512、l1_en_hq/zh 未开）· gpic train 1556/8000 + test 128✓（pid 2426795）；base-en 1T token 已下满 2048/2048；🔴 LLaVA 85M 已停无进程 7629/26T 未删；✅ D-CLEAN-3 servers 已删（GONE，Avail 32T/85%）；重 I/O 阶段继续推迟） |
| ERROR_COUNT | 0 |
| 节点 | `10.239.2.12`（主机 `whag0pgpuap12`；NFS：`/nas_inference` 只读源，`/nas_train` 产出） |
| 更新 | 2026-10-03 |

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

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

## 操作流水

- 2026-10-03 —— 唤醒 73（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base-rest 2061268 真推进（etime 4h38m；en_v1_4 首快照 CC-MAIN-2013-20 = 355/512 件、0 .incomplete；part-0355-of-512@21:54，~85MB/件；上轮 311@21:21→+44 件 ≈~1.9MB/s；🔻 l1_en_hq/zh 目录仍未创建=0/0，尚未轮到，`--include` 多 pattern 顺序执行中）；🔵 gpic 2426795 真推进（train 1556/8000 + test 128/128✓、1 .incomplete=在途 01555；gpic_train_01555.tar@21:54，~1.6GB/件；上轮 1530@21:19→+26 件 ≈~19MB/s）；🔴 LLaVA 85M 仍停无进程（`pgrep -af 'hf download'` 仅 base-rest 2061268 + gpic 2426795 两个真进程）；✅ SFT-2605 1504/1504 intact；✅ servers GONE；✅ base-en 2048/2048 满。🔑 持续建议（未拍板，连续多轮）：**en_v1_4 = v1.4 升级版（2.2T token，不在 P-8 配方内），6.7TB @1.9MB/s ≈41 天**（仅首快照 CC-MAIN-2013-20 就 512×85MB≈43.5GB）；而 l1_en_hq(478G)+zh(324G)=802GB 尚未开始 → **建议停 en_v1_4 只续 l1_en_hq+zh（释放带宽给 gpic）**，待运维拍板。gpic 剩 6444 件 ≈10.3TB @19MB/s ≈6.3 天。磁盘 /nas_train 32T(85%)、/nas_inference 19T(59%)、/nas_user 29T(74%)、/data 6.8T(4%) 均够，WAITING=1。git 本轮回写后提交。下一步 = 下轮判 base-rest/gpic 真推进（僵死即 kill+重启）→ 待运维对 en_v1_4 拍板 → base-en 已可过闸分词（重 I/O 待下载窗口）→ gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 72（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base-rest 2061268 真推进（etime 4h02m；en_v1_4 首快照 CC-MAIN-2013-20 = 311/512 件、0 .incomplete；part-0311@21:21，~85MB/件；上轮 140@19:08→+171 件 ≈~1.8MB/s；🔻 l1_en_hq/zh 目录仍未创建=0/0）；🔵 gpic 2426795 真推进（train 1530/8000 + test 128/128✓，0 .incomplete；gpic_train_01530@21:19，~1.6GB/件；上轮 1436@19:08→+94 件 ≈~19MB/s）；🔴 LLaVA 85M 仍停无进程（`hf download` 仅 base-rest 2061268 + gpic 2426795 两个真进程）；✅ SFT-2605 1504/1504 intact；✅ servers GONE；✅ base-en 2048/2048 满。🔑 en_v1_4 结构复核（HF API tree=110 快照目录 ×~512 件 ≈56.3k 文件 ≈6.7TB，与 wake 69 实测 6,747GB 一致）；当前 ~1.8MB/s → 剩余 ≈6.72TB @1.8MB/s ≈43 天 / @10MB/s ≈7.8 天；**建议维持：停 en_v1_4 只续 l1_en_hq(478G)+zh(324G)=802GB（@19MB/s≈12h）**，待运维拍板。gpic 剩 6470 件 ≈10.3TB @19MB/s ≈6.3 天。磁盘 /nas_train 31928G(85%)、/nas_inference 19T(59%)、/nas_user 29T(74%) 均够，WAITING=1。git 本轮回写后提交。下一步 = 下轮判 base-rest/gpic 真推进（僵死即 kill+重启）→ 待运维对 en_v1_4 拍板 → base-en 已可过闸分词（重 I/O 待下载窗口）→ gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 71（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base-rest 2061268 真推进（etime 1h52m；en_v1_4 首快照 CC-MAIN-2013-20 = 140/512 件、0 .incomplete；part-0140@19:08，~85MB/件；上轮 90@18:34→+50 件 ≈~2.1MB/s；🔻 l1_en_hq/zh 目录仍未创建=0/0）；🔵 gpic 2426795 真推进（train 1436/8000 + test 128/128✓，0 .incomplete；gpic_train_01435@19:08，~1.55GB/件；上轮 1411→+25 件 ≈~20MB/s）；🔴 LLaVA 85M 仍停无进程（`hf download` 仅 base-rest 2061268 + gpic 2426795 两个真进程）；✅ SFT-2605 1504/1504 intact；✅ servers GONE；✅ base-en 2048/2048 满（末件 part-2048@17:12，0 .incomplete）。🔑 关键结论：**base-en=ultrafineweb_en(v1, 2.66TB/1T token) 已下满 → P-8 Stable 段"base"主料已就绪**（配方需 ~70–160B ≪ 1T token，量冗余 ~7–14x）；**en_v1_4 是 v1.4 升级版（2.2T token，2025-12-10 发布，Apr2024–Jun2025 快照），不在 P-8 配方内**（配方=base+UltraX-Preview+code+math），6.75TB @2MB/s≈39–58 天 → **建议运维拍板：停 en_v1_4（省 6.75TB+释放带宽给 gpic），仅续 l1_en_hq(478G)+zh(324G) 两个小 config**。磁盘 /nas_train 31963G(85%)、/nas_inference 19T(58%)、/nas_user 29T(74%) 均够，WAITING=1。git 本轮回写后提交。下一步 = 下轮判 base-rest/gpic 真推进（僵死即 kill+重启）→ 待运维对 en_v1_4 拍板 → base-en 已可过闸分词（重 I/O 待下载窗口）→ gpic 续下至 8000 tar。

- 2026-10-03 —— 唤醒 70（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令、无索取、无 STOP）。🔵 base-rest 2061268 真推进（etime 1h18m；en_v1_4 仍只在首快照 CC-MAIN-2013-20 = 90/512 件（`find en_v1_4 -name '*.parquet'`=90）、0 .incomplete；part-0089@18:34，~85MB/件；上轮 50@17:57→本轮 +40 件，≈40件/37min ≈~1.5MB/s；🔻 l1_en_hq 与 zh 目录仍未创建=0/0，尚未轮到）；🔵 gpic 2426795 真推进（train 1411/8000 + test 128/128✓，1 .incomplete=在途 01411；gpic_train_01410.tar@18:34，~1.6GB/件；上轮 1383→本轮 +28 件，≈28件/37min ≈~20MB/s）；🔴 LLaVA 85M 仍停无进程（`pgrep -af 'hf download'` 仅 base-rest 2061268 + gpic 2426795 两个真进程）；✅ SFT-2605 1504/1504、0 .incomplete intact；✅ servers GONE（复核）；✅ base-en 2048/2048、0 .incomplete 满。本轮无 CDN 假活。⚠️ 带宽分配实测：gpic ≈20MB/s 占大头、en_v1_4 ≈1.5MB/s（小文件 + 争带宽）→ 剩余 en_v1_4(6740G)+l1_en_hq(478G)+zh(324G) ≈7.54TB @1.5MB/s ≈58 天 / @10MB/s ≈8.7 天。磁盘 /nas_train 31970G(85%)、/nas_inference 19.4T(58%)、/nas_user 29T(74%) 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/io 判 base-rest 2061268 / gpic 2426795 真推进（僵死即 kill+重启）→ base 3 config 续下 → base 落地过 check_contamination → phase2 分词（base-en 86:10:4）；⚠️ 上报运维：en_v1_4(6.75TB) 若需全下、@当前 1.5MB/s 不现实，需运维拍板（是否停 gpic 让带宽给 base / 是否放弃 en_v1_4 只留 base-en）。

- 2026-10-03 —— 唤醒 69（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已完成提交；无新增指令）、无索取、无 STOP。🔵 base-rest 2061268 真推进（etime 40m；en_v1_4 首快照 CC-MAIN-2013-20/ 已 50/512 件、0 .incomplete、~85MB/件，part-0001@17:17→part-0050@17:57 ≈50件/40min ≈~1.8MB/s，wchar 4.28GB）；🔵 gpic 2426795 真推进（train 1383/8000 + test 128/128✓，gpic_train_01383@17:57，~1.6GB/件，累计 write_bytes 930GB）；🔴 LLaVA 85M 仍停无进程；✅ SFT-2605 1504/1504 intact；✅ servers GONE（复核）。⚠️ 实测 en_v1_4 结构更正：文件在子目录 CC-MAIN-20xx-xx/（每快照 ~512 件、~85MB/件，非 1.3GB），110 快照 56,461 文件 6,747GB；当前 ~1.8MB/s 偏慢（与 gpic 争带宽 + 小文件开销）→ en_v1_4 单独 @1.8MB/s ≈43 天 / @10MB/s ≈7.8 天；剩余 en_v1_4+l1_en_hq(478G)+zh(324G) ≈7.55TB @10MB/s ≈8.7 天 / @1.8MB/s ≈50 天。磁盘 /nas_train 32T(85%)、/nas_inference 19T(58%)、/nas_user 29T(74%) 均够，WAITING 保持 1。📉 MEMORY_DATA.md 滚动：唤醒 60/61 迁 daily-memories-data（原文不改），30020B→26347B(<26KB)。git 本轮回写后提交。下一步 = 下轮按 mtime/io 判 base-rest 2061268 / gpic 2426795 真推进（僵死即 kill+重启）→ base 3 config 续下 → base 落地过 check_contamination → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 68（🔴 base-en 下满 + 重启剩余 config + ⚠️ 实测 base 全量=10.21TB）：复核运维指令未变（D-CLEAN 系列已完成提交；无新增指令）、无索取、无 STOP。🔴 **base-en 2048/2048 已下满**（`ls data/ultrafineweb_en/*.parquet`=2048、0 `.incomplete`；base 旧进程 2023896 已自动退出，`pgrep /bin/hf` 现仅 gpic 2426795 + 新 base-rest 2061268）。→ **已重启 hf download 拉剩余 3 config**：pid **2061268**，`--include 'data/ultrafineweb_en_v1_4/*' 'data/ultrafineweb_l1_en_hq/*' 'data/ultrafineweb_zh/*' --local-dir /nas_train/.../Ultra-FineWeb`，log 确认下 en_v1_4（CC-MAIN-2013-20 part-0001~0008 已落盘，真推进）。🔵 gpic 2426795 真推进（train 1355/8000 + test 128✓，+18 件）；🔴 LLaVA 85M 仍停无进程；✅ SFT-2605 1504/1504 intact；✅ servers GONE。⚠️ **重大更正（HfApi.list_repo_tree 全树实测 64,771 文件）**：base 全量 **不是 2.99TB 而是 10.21TB（≈3.4x 历史低估）** = `ultrafineweb_en` 2048/2661.4GB✅已满 + `ultrafineweb_en_v1_4` **56,461 文件/6747.4GB**（CC-MAIN 110 快照）+ `ultrafineweb_l1_en_hq` **6006 文件/478.0GB**（6 快照）+ `ultrafineweb_zh` 256/324.3GB → **剩余待下 = 7549.7GB ≈ 7.55TB**（旧记「en 后 0.33TB」偏低 ≈23x）。ETA（剩余 7.55TB）：@10MB/s ≈8.7 天 / @12MB/s ≈7.3 天 / @15MB/s ≈5.8 天；gpic 剩 6645 ≈10.6TB、让位 base。磁盘 /nas_train 85%(32T)、/nas_inference 58%(20T)、/nas_user 74%(29T) 均够（base 10.2TB 全落 /nas_train，Avail 32T 足够）。⚠️ **上报运维**：base「2.99TB」系历史低估，真实 **10.21TB**；P-8 主料 **base-en(2.66TB) 已下满、可先过闸分词**；en_v1_4(6.75TB) 是否全下（~6-9 天、占 6.75TB）请拍板——本线按「保持推进不中断」继续下。WAITING=1。git 回写后提交。
- 2026-10-03 —— 唤醒 67（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 2034/2048，data 目录 0 .incomplete；log 尾部「Download complete part-2034」+ 在途 part-2035；mtime 2031@16:33→2034@16:40 ≈3件/7min ≈~10MB/s 发布率，~1.3GB/件）；🔵 gpic 2426795 真推进（train 1337/8000 + test 128/128✓；gpic_train 01334@16:35→01336@16:39 ≈1件/2min ≈~13MB/s，~1.6GB/件；1 .incomplete 为在途 01337）；🔴 LLaVA 85M 仍停（`pgrep -af 'hf download'` 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete intact；✅ servers 已删（`[ -d ]`=GONE，D-CLEAN-3 复核）。本轮无 CDN 假活。ETA：base-en 剩 14 件 ≈18GB，@~10MB/s ≈~30min；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈8.5~12.5h；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6663 ≈10.6TB，@当前 ~13MB/s ≈~9.5 天 / @保守 ~8.7MB/s ≈~14 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/* → 下满 2048 后自动退出，下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq（目录名已实测 = ultrafineweb_en / ultrafineweb_en_v1_4 / ultrafineweb_l1_en_hq / ultrafineweb_zh）。磁盘 /nas_train 32T(85%)、/nas_inference 20T(58%)、/nas_user 29T(74%) 均够，WAITING 保持 1。📉 MEMORY_DATA.md 体量 28861B(≈28KB)<32KB，本轮不滚动。git 本轮回写后提交。下一步 = 下轮按 log 尾部/mtime 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~30min 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 66（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 2021/2048，0 .incomplete/0 .lock；最新 ultrafineweb-en-part-2021-of-2048 已落盘、在途 part-2022；~1.30GB/件；上轮 2002@15:30→本轮 +19 件，约 1 件/1.7min ≈~12-13MB/s；log 尾部「Download complete part-2021」）；🔵 gpic 2426795 真推进（train 1319/8000 + test 128/128✓，1 .incomplete 为在途 gpic_train_01319；~1.6GB/件；上轮 1306→本轮 +13 件）；🔴 LLaVA 85M 仍停（`pgrep -af 'hf download'` 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete intact；✅ servers 已删（D-CLEAN-3 完成，GONE）。本轮无 CDN 假活。ETA：base-en 剩 27 件 ≈35GB，@~12MB/s ≈~1h / @~8MB/s ≈~1.5h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈9~13h；gpic 剩 6681 ≈10.7TB，@~11MB/s ≈~11 天。⚠️ 交接（下轮必看）：base 现进程仅 `--include data/ultrafineweb_en/*` → 下满 2048 后自动退出；下轮若见 en=2048 须**重启**下载其余 config（`ultrafineweb_en_v1_4` / `ultrafineweb_l1_en_hq` / `ultrafineweb_zh`）：`hf download --repo-type dataset openbmb/Ultra-FineWeb --include 'data/ultrafineweb_en_v1_4/*' --include 'data/ultrafineweb_l1_en_hq/*' --include 'data/ultrafineweb_zh/*' --local-dir /nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb`。磁盘 /nas_train 85%（32024G）、/nas_inference 58%（19550G）、/nas_user 74%（28988G）均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base/gpic 真推进（僵死即 kill+重启）→ base-en 下满 2048（预计 ~1-1.5h）→ 重启 hf download 拉 en_v1_4/zh/l1_en_hq → base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 65（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 2002/2048，0 .incomplete/0 .lock；最新 ultrafineweb-en-part-2002-of-2048@15:30，~1.30GB/件；上轮 1990→本轮 +12 件，约 1 件/2min ≈~11MB/s；log 尾部「Download complete part-2002」+ 在途 part-2003）；🔵 gpic 2426795 真推进（train 1306/8000 + test 128/128✓，0 .incomplete；`/proc/io` write +67MB/8s ≈~8.4MB/s；上轮 1288→本轮 +18 件）；🔴 LLaVA 85M 仍停（`pgrep -af 'hf download'` 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete intact；✅ servers 已删（`[ -d ]` = GONE）。本轮无 CDN 假活。ETA：base-en 剩 46 件 ≈60GB，@~11MB/s ≈~1.5h / @~8MB/s ≈~2h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈10~14h（≈0.4~0.6 天）；gpic 剩 6694 ≈10.7TB，@~8.4MB/s ≈~15 天。⚠️ 交接（下轮必看）：base 现进程仅 `--include data/ultrafineweb_en/*` → 下满 2048 后自动退出；下轮若见 en=2048 须**重启**下载其余 config（目录名已用 HF API `/api/datasets/openbmb/Ultra-FineWeb/tree/main/data` 实测确认 = `ultrafineweb_en` / `ultrafineweb_en_v1_4` / `ultrafineweb_l1_en_hq` / `ultrafineweb_zh`）：`hf download --repo-type dataset openbmb/Ultra-FineWeb --include 'data/ultrafineweb_en_v1_4/*' --include 'data/ultrafineweb_l1_en_hq/*' --include 'data/ultrafineweb_zh/*' --local-dir /nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb`。磁盘 /nas_train 32T(85%)、/nas_inference 20T(58%)、/nas_user 29T(74%) 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base/gpic 真推进 → base-en 下满 2048（预计 ~1.5-2h）→ 重启 hf download 拉 en_v1_4/zh/l1_en_hq → base 过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 64（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；记忆维护 MEMORY_DATA.md ≈23KB < 32KB 无需再滚动）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1990/2048，0 .incomplete/0 .lock；最新 ultrafineweb-en-part-1990-of-2048@14:55，1.297GB/件；etimes 11h09m；上轮 1975→本轮 +15 件，~15件/33min ≈~10MB/s）；🔵 gpic 2426795 真推进（train 1288/8000 + test 128/128✓，0 .incomplete；gpic_train_01288.tar@14:56，~1.59GB/件；etimes 20h42m；上轮 1274→本轮 +14 件，~14件/34min ≈~10.7MB/s）；🔴 LLaVA 85M 仍停（`pgrep -af 'hf download'` 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504 intact（未变）；✅ servers 已删（D-CLEAN-3 完成）。本轮无 CDN 假活。ETA：base-en 剩 58 件 ≈75GB，@~10MB/s ≈~2.1h / @~8MB/s ≈~2.6h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈10~15h（≈0.4~0.6 天）；gpic 剩 6712 ≈10.7TB，@~10.7MB/s ≈~12 天 / @~8MB/s ≈~15 天。磁盘 /nas_train 32T(85%)、/nas_inference 20T(58%)、/nas_user 29T(74%) 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base 2023896 / gpic 2426795 真推进（僵死即 kill+重启）→ base-en 下满 2048（预计 ~2-2.6h；若见 en=2048 须**重启 hf download 加 `--include` 拉 en_v1_4/zh/l1_en_hq**）→ base 过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 63（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；记忆维护：MEMORY_DATA.md ≈21.7KB < 32KB 无需滚动）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1975/2048，0 .incomplete/0 .lock；最新 ultrafineweb-en-part-1975-of-2048@14:22，etimes 10h35m；上轮 1954→本轮 +21 件，≈7 件/13min ≈~12MB/s、~1.30GB/件）；🔵 gpic 2426795 真推进（train 1274/8000 + test 128/128✓，0 .incomplete；gpic_train_01273.tar@14:22，~1.6GB/件；上轮 1261→本轮 +13 件）；🔴 LLaVA 85M 仍停（pgrep -af 'hf download' 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504 intact；✅ servers 已删（D-CLEAN-3 完成）。本轮无 CDN 假活。ETA：base-en 剩 73 件 ≈95GB，@~12MB/s ≈~2.2h / @~8MB/s ≈~3.3h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h（⚠️ 需重启 hf download 加 --include）→ 复用路线全 base ≈10~15h（≈0.4~0.6 天）；gpic 剩 6726 ≈10.8TB，@~12MB/s ≈~10.5 天。磁盘 /nas_train 32T(85%)、/nas_inference 20T(58%) 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base 2023896 / gpic 2426795 真推进（僵死即 kill+重启）→ base-en 下满 2048（预计 ~2-3.5h；若见 en=2048 须重启 hf download 拉 en_v1_4/zh/l1_en_hq）→ base 过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 62（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN 系列已全部完成并提交；无新增指令）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1954/2048，0 .incomplete，进程存活 9h58m；mtime 1953@13:44→1954@13:45 ≈~14-15MB/s，~1.30GB/件；上轮 1932@13:11→本轮 +22 件）；🔵 gpic 2426795 真推进（train 1261/8000 + test 128/128✓，0 .incomplete；gpic_train_01260.tar@13:45，~1.65GB/件；上轮 1251→本轮 +10 件）；🔴 LLaVA 85M 仍停（`pgrep -af 'hf download'` 仅 base 2023896 + gpic 2426795 两个真进程，无 LLaVA 进程；7629/26T 冻结未删）；✅ SFT-2605 1504/1504 intact；✅ servers 已删（`[ -d ]` = GONE，D-CLEAN-3 复核）。本轮无 CDN 假活。ETA：base-en 剩 94 件 ≈122GB，@~14MB/s ≈~2.4h / @保守 ~8MB/s ≈~4.2h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈10.5~16h（≈0.45~0.7 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6739 ≈11.1TB，@当前 ~8MB/s ≈~16 天 / @base 完回升 ~12MB/s ≈~10.5 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/* → 下满 2048 后自动退出，下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 32T(85%)、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。📉 MEMORY_DATA.md 滚动归档：唤醒 48–55 共 8 条迁 daily-memories-data/2026-10-03.md（原文不改），本文件 32416B→19779B(<20KB)。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~2.4-4.2h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
