# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.5/§0.6/§0.7 推进中 · base 下载巡检中（base-en 1911/2048）· D-CLEAN 系列已全部完成（回收 ≈1.31TiB）
已完成:       §0.3 8源/§0.4 R2视觉/§0.6 配方/§0.7 停85M·复用·ETA 均已交付；SFT-2605 下满一致；D-CLEAN 盘点；D-CLEAN-2 已删 laion2B(7.8G)·zhulong(493M)·pip(3.3G)·nemo Round1(~310G)；🆕 D-CLEAN-3 已删 servers(974G)
当前动作:     唤醒 60：轻 I/O 下载巡检（base 1911/2048·gpic 1241/8000 真推进；无新指令/索取/STOP）
下一步:       base-en 剩 137 件下满 2048 → 重启 en_v1_4/zh/l1_en_hq → base 过闸分词；gpic 续下至 8000 tar
阻塞:         无硬阻塞；磁盘 /nas_train 已回收 ≈1.31TiB（Avail 32T，85%）
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
| WAITING | 1（下载中：base-en 1911/2048（pid 2023896）· gpic train 1241/8000 + test 128✓（pid 2426795）；🔴 LLaVA 85M 已停无进程 7629/26T 未删；✅ D-CLEAN-3 已删 servers 974G（Avail 32T/85%）；重 I/O 阶段继续推迟） |
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

- 2026-10-03 —— 唤醒 60（轻 I/O 巡检，无假活、无重启）：复核运维指令未变（D-CLEAN-3 servers 删除已在 唤醒 59 完成并提交、无新增指令）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1911/2048，0 .incomplete，du 2.3T；log 尾部「Download complete part-1911」+ 在途 part-1912；mtime 1907@12:23→1911@12:36 ≈4件/13min ≈~7MB/s 发布率；`/proc/io` write 6s +1.23GB 为缓冲高速）；🔵 gpic 2426795 真推进（train 1241/8000 + test 128/128✓，du 1.8T；`/proc/io` write 6s 仅 +16KB → 本轮显著让位 base，符合 §0.7 base>gpic；1 .incomplete 为在途件）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504 intact。本轮无 CDN 假活。ETA：base-en 剩 137 件 ≈178GB，@~7MB/s ≈7h / @~14MB/s ≈3.5h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈11.5~19h（≈0.5~0.8 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6759 ≈11TB，@base 完 ~12MB/s ≈~10 天 / @保守 ~8.7MB/s ≈~15 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/* → 下满 2048 后自动退出，下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 32T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 log/mtime 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~3.5-7h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 59（🆕 D-CLEAN-3 servers 删除 + 轻巡检）：复核运维指令（新增 D-CLEAN-3：删 servers 974G、nemo R2 ckpt 不删）、无索取、无 STOP。✅ 三项前置检查全过：P1 `fuser -v`(无 -m) 空 / open-fd 0 / 关键进程 cwd 均不在 servers（vision R9 在 run/vision，hf 下载在 datasets）；P2 `find -newermt '-7 days'` 空；P3 共享副本 grep 0 命中（全树 grep 后台 119s 亦 0）。→ `rm -rf /nas_train/app.e0031982/servers` 完成、`ls -d`=GONE；symlink 指向外部数据集（coco/gqa/ocr_vqa/textvqa/vg）不跟随、逐一 `ls -d` 完好。df 删前 180751G→删后 179779G = **回收 ≈972G（=du 974G，86%→85%）**（⚠️ 删后 df 曾短暂显示仅 -271G 系 NFS statfs 延迟，2 分钟后稳定）。🔵 base 2023896 真推进（base-en 1897/2048，0 .incomplete）；🔵 gpic 2426795 真推进（train 1223/8000 + test 128✓）；🔴 LLaVA 85M 仍停（无进程）；✅ SFT-2605 1504/1504 intact。磁盘 /nas_train Avail 32190G（85%）、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。下一步 = 下轮按 log/mtime 判 base/gpic 真推进（僵死即 kill+重启）→ base-en 下满 2048（剩 ~147 件预计 ~4-8h）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 58（🆕 D-CLEAN-2 执行 + servers 探查 + 轻巡检）：复核运维指令（新增 D-CLEAN-2 已批准删除项 + servers 探查）、无索取、无 STOP。✅ 已执行删除：laion2B-en-aesthetic **实测 7.8G（⚠️ 纠正：D-CLEAN 记的 8.1T 是 G/T 单位误读，128 parquet URL 元数据，非 8.1TB）** + zhulong.tar.gz 493,894,409B + `~/.cache/pip` 3.3G + nemo_experiments **Round1/S系列 27 目录 ≈310G**（保留 live p5b 79G + R2 p1–p7 ≈135G；524G→214G）→ 实际回收 ≈341G（df -hT /nas_train 仍 31T 整 TB 粒度不变，df -BG Avail 30964G）。🔍 servers 探查（未删）：974G = 6 节点 × LLaVA-V1.5-Qwen3-4B 旧训练 ckpt（2026-02），高价值回收候选待 owner 确认。🔵 base 2023896 真推进（base-en 1882/2048，0 .incomplete）；🔵 gpic 2426795 真推进（train 1203/8000 + test 128✓）；🔴 LLaVA 85M 仍停（无进程）；✅ SFT-2605 1504/1504 不变。磁盘 /nas_train 30.96T、/nas_inference 20T、/nas_user 29T，WAITING=1。下一步 = 下轮判 base/gpic 真推进 → base-en 下满 2048（剩 166 件）→ 重启 en_v1_4/zh/l1_en_hq → base 过闸 → phase2 分词；gpic 续下至 8000。git 回写后提交。
- 2026-10-03 —— 唤醒 55（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1795/2048，0 .incomplete 残留，du 2.2T；log 尾部「Download complete part-1795」+ 在途 part-1796；/proc/io write 8s 内 +67MB ≈~8.4MB/s）；🔵 gpic 2426795 真推进（train 1117/8000 + test 128/128✓，du 1.8T；gpic_train 01114@07:12→01116@07:17 ≈3件/5min ≈~15MB/s，1 .incomplete 为在途 01117）；🔴 LLaVA 85M 仍停（无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504 = 318,990,252,711 B、0 .incomplete 一致。本轮无 CDN 假活。ETA：base-en 剩 253 件 ≈329GB，@~7-9MB/s ≈10~13h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈18~25h（≈0.75~1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic train 剩 6883 ≈10.7TB，@近端 ~15MB/s ≈~8 天 / @保守 ~8.7MB/s ≈~14 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 /proc/io + log 尾部判 base 2023896 / gpic 2426795 真推进 → base-en 下满 2048（约 10-13h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 48（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2275253 真推进（base-en 1705/2048，0 .incomplete，du 2.1T；本轮改用 `/proc/2275253/io` 判活：write_bytes 20s 内 206,970,019,840→208,005,234,688 = +1,035,214,848 B ≈ ~52MB/s，远快于上轮 ~14MB/s，带宽显著回升）；🔵 gpic 2426795 真推进（train 994/8000 + test 128/128✓，du 1.6T；`/proc/2426795/io` write 20s 内 305,552,965,632→306,022,330,368 = +469,364,736 B ≈ ~24MB/s，与本轮 base 并行高位，总出口 ~75MB/s，不再"让位"）；🔴 LLaVA 85M 仍停（`pgrep` 无进程，7629/26T 冻结未删）；✅ SFT-2605 维持 1504/1504 = 318,990,252,711 B 一致。本轮以 /proc/io 判活（比 .incomplete 更准），无 CDN 假活。ETA：base-en 剩 343 件 ≈446GB，@本轮 ~52MB/s ≈2.5h / @保守 ~14MB/s ≈9h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈10.5~21h（≈0.4~0.9 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 7006 ≈11.2TB，@本轮 ~24MB/s ≈~5.5 天 / @保守 ~8.7MB/s ≈~15 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮先按 /proc/io write（或 .incomplete 字节）增长判 base 2275253 / gpic 2426795 真推进 → base-en 下满 2048（预计 ~2.5-9h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 49（轻 I/O 巡检 + 🔴 重启 base 假活进程）：复核运维指令未变、无索取、无 STOP。🔴 base 巡检发现 pid 2275253 **假活（僵死）**——仅进程存活、实则 base-en 1708/2048 时 part-1709 `.incomplete` 冻结 268,141,750 B、mtime 03:40:17、多次采样 03:43→03:45 全程 0 增长（/proc/io write 20s 仅 +8KB），且 part-1707→1708 耗时 23min（03:12→03:35）→ 定性 CDN 劣化掉连接后 hf_transfer 挂死（同唤醒 40，已是第 4 次）。🔴 处置：kill 2275253（SIGTERM）→ 同命令重启 → 新 pid 2023896（hf_transfer=True；list_repo_tree 全树 64624 文件慢、删 268MB 残留 .incomplete、part-1709 从 0 重下）→ ✅ 复测确认恢复：part-1709 0→871MB→1.2GB、/proc/io write 20s +335,388,672 B ≈~16MB/s 稳态，base-en 已推进至 1709/2048。🔵 gpic 2426795 真推进（train 1023/8000 + test 128/128✓，du 1.6T，~7.4MB/s 健康）。🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）。✅ SFT-2605 维持 1504/1504、0 .incomplete = 318,990,252,711 B。ETA：base-en 剩 ≈339 件 ≈440GB，@本轮 ~16MB/s ≈7.5h / @保守 ~14MB/s ≈9h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈15.5~21h（≈0.65~0.9 天）；gpic 剩 6977 ≈11.2TB，@当前 ~7.4MB/s ≈~17 天 / @base 完 ~24MB/s ≈~5.5 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 /proc/io write（或 .incomplete 字节）增长判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~7.5-9h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 50（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1723/2048，part-1724@04:26 在途，0 .incomplete；/proc/io write_bytes 15s 19,965,919,232→20,796,772,352 B ≈ +55MB/s，mtime 1720@04:13→1723@04:24 ≈~7MB/s 发布率）；🔵 gpic 2426795 真推进（train 1039/8000 + test 128/128✓，du 1.7T；/proc/io write 15s 376,211,009,536→377,751,789,568 B ≈ +103MB/s 高速）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 维持 1504/1504 = 318,990,252,711 B intact。本轮无 CDN 假活。ETA：base-en 剩 325 件 ≈423GB，@发布 ~7MB/s ≈17h / @中位 ~15MB/s ≈8h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈16~29h（≈0.7~1.2 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6961 ≈11.1TB，@当前 ~7-14MB/s ≈~9-18 天 / @base 完 ~24MB/s ≈~5.5 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/*，下满 2048 后自动退出 → 下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 /proc/io write 增长判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~8-17h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 51（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1740/2048，0 .incomplete；log 尾部连续完成至 part-1740@04:58，在途 1741；mtime 1737@04:50→1740@04:58 ≈3 件/8min ≈~8-9MB/s 稳态）；🔵 gpic 2426795 真推进（train 1054/8000 + test 128/128✓，du 1.7T；gpic_train 01051@04:58→01053@05:01 ≈1min/件 ≈~27MB/s 高速；相对 `--local-dir stanford-vision-lab/gpic` 经 `/proc/2426795/cwd=/nas_inference/.../datasets` 落盘正确）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete = intact。本轮无 CDN 假活。ETA：base-en 剩 308 件 ≈400GB，@~8-9MB/s ≈12~13h / @~15MB/s ≈7.5h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈16~25h（≈0.7~1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6946 ≈11.1TB，@当前 ~27MB/s ≈~5 天 / @保守 ~8.7MB/s ≈~15 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~7.5-13h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 52（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1753 完成 + part-1754 在途 = 1754/2048，0 .incomplete 残留，du 2.1T；log 尾部连续完成至 part-1753@05:36；mtime 1746@05:14→1753@05:36 ≈7 件/22min ≈ ~7-8MB/s 稳态）。🔵 gpic 2426795 真推进（train 1072/8000 + test 128/128✓，du 1.7T；gpic_train 01068@05:30→01071@05:36 ≈~1.5min/件 ≈ ~18MB/s 高速；1 .incomplete 为在途件）。🔴 LLaVA 85M 仍停（无进程，7629/26T 冻结未删）。✅ SFT-2605 1504/1504、0 .incomplete intact。本轮无 CDN 假活。ETA：base-en 剩 294 件 ≈382GB，@~7-8MB/s ≈13~15h / @~15MB/s ≈7h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈21~27h（≈0.9~1.1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6928 ≈11.1TB，@当前 ~18MB/s ≈~7 天 / @保守 ~8.7MB/s ≈~15 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 mtime/log 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~7-15h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 53（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1773/2048，0 .incomplete 残留，du 2.1T；/proc/io write_bytes 12s 83,519,442,944→84,190,175,232 = +670,732,288 B ≈ ~53MB/s 缓冲高位；mtime 1771@06:05→1772@06:07→1773@06:11 ≈3min/件 ≈~7MB/s 发布率——缓冲与发布差说明有并发分片缓冲）；🔵 gpic 2426795 真推进（train 1084/8000 + test 128/128✓，du 1.7T；/proc/io write 12s 448,246,677,504→449,320,660,992 = +1,073,983,488 B ≈ ~85MB/s 高速；gpic_train 01081@06:07→01083@06:11 ≈2min/件 ≈~13MB/s 发布率；1 .incomplete 为在途件）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 维持 1504/1504 = 318,990,252,711 B intact。本轮无 CDN 假活。ETA：base-en 剩 275 件 ≈357GB，@发布 ~7MB/s ≈~14h / @缓冲 ~53MB/s（理论）≈~2h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈22~26h（≈0.9~1.1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6916 ≈11.1TB，@当前 ~13MB/s ≈~10 天 / @保守 ~8.7MB/s ≈~15 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/*，下满 2048 后自动退出 → 下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 /proc/io write + mtime/log 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~7-14h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 54（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1787/2048，0 .incomplete 残留，du 2.2T；log 尾部 1786→1787→在途 1788@06:45，mtime 1783@06:33→1787@06:45 ≈1件/2-3min ≈~7-9MB/s 稳态）；🔵 gpic 2426795 真推进（train 1100/8000 + test 128/128✓，du 1.8T；06:11→06:46 +16件/35min ≈~12MB/s，1 .incomplete 为在途件）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete intact。本轮无 CDN 假活。ETA：base-en 剩 261 件 ≈339GB，@~7-9MB/s ≈10.5~13.5h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈19~25h（≈0.8~1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6900 ≈11.3TB，@当前 ~12MB/s ≈~10.5 天 / @保守 ~8.7MB/s ≈~15 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/*，下满 2048 后自动退出 → 下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 log 尾部/mtime 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~10-13.5h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 56（轻 I/O 巡检，无假活、无重启）：复核运维指令未变、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1810/2048，0 .incomplete 残留，du 2.2T；log 尾部「Download complete part-1809」+ 在途 part-1810；mtime 1803@07:45→1810@07:55 ≈7件/10min ≈~14-15MB/s 发布率）；🔵 gpic 2426795 真推进（train 1120/8000 + test 128/128✓，du 1.8T；gpic_train 01115@07:13→01119@07:46 ≈1.6GB/件，1 .incomplete 为在途 01120）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504 = 318,990,252,711 B、0 .incomplete intact。本轮无 CDN 假活。ETA：base-en 剩 238 件 ≈309GB，@~14MB/s ≈~6h / @~8MB/s ≈~11h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h → 复用路线全 base ≈14~23h（≈0.6~1 天）；不复用 ≈64~88h → 复用已省 ≈1.67TB ≈44~65h；gpic 剩 6880 ≈10.7TB，@近端 ~15MB/s ≈~8 天 / @保守 ~8.7MB/s ≈~14 天。⚠️ 交接：base 现进程 2023896 只 --include data/ultrafineweb_en/* → 下满 2048 后自动退出，下轮若见 en=2048 须重启 hf download 加 --include 拉 en_v1_4/zh/l1_en_hq。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 log 尾部/mtime 判 base 2023896 / gpic 2426795 真推进（发现僵死即 kill+重启）→ base-en 下满 2048（预计 ~6-11h 内）→ 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
- 2026-10-03 —— 唤醒 57（轻 I/O 巡检 + 🆕 D-CLEAN 盘点 + 📉 记忆滚动）：复核运维指令（新增 D-CLEAN 磁盘清理盘点 + 记忆维护规程）、无索取、无 STOP。🔵 base 2023896 真推进（base-en 1822/2048，0 .incomplete，du 2.2T；上轮 1810→本轮 1822 = +12 件）；🔵 gpic 2426795 真推进（train 1131/8000 + test 128/128✓，du 1.7T+119G；+11 件）；🔴 LLaVA 85M 仍停（pgrep 无进程，7629/26T 冻结未删）；✅ SFT-2605 1504/1504、0 .incomplete intact。🆕 产出 DISK_CLEANUP_INVENTORY.md（大盘 + 本用户分级候选 + 他人只读清单，未删除任何）。📉 MEMORY_DATA.md 滚动归档：87KB→≈30KB（旧 42 条迁 daily-memories-data）。ETA：base-en 剩 226 件 ≈294GB，@~14MB/s ≈6h / @~8MB/s ≈10h；en 后接 en_v1_4/zh/l1_en_hq ≈0.33TB ≈8~12h；gpic 剩 6869 ≈10.7TB，@~13MB/s ≈~10 天。磁盘 /nas_train 31T、/nas_inference 20T、/nas_user 29T 均够，WAITING 保持 1。git 本轮回写后提交。下一步 = 下轮按 log/mtime 判 base/gpic 真推进（发现僵死即 kill+重启）→ base-en 下满 2048 → 重启 en_v1_4/zh/l1_en_hq（config 级 --include）→ base 落地过闸 → phase2 分词（base-en 86:10:4）；gpic 续下至 8000 tar。
