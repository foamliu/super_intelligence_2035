# MEMORY_DATA.md — BaiZe 正式训练数据准备 · 运行时状态

WAITING: 1

> ⚠️ **`WAITING` 只认本文件顶部这一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配）。
> **不要在正文/流水里再写任何以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。

---

## 📊 进度快照（固定格式，每次唤醒必须更新）

```
PHASE:        §0.5/§0.6/§0.7 推进中 · 🔴白名单锁定(只下 l1_en_hq+zh+GPIC；en_v1_4 已停) · l1_en_hq 1114/6006(CC-MAIN-2025-33 part-0117) · zh 171/256(冻结待续) · gpic train 2361/8001+test 128✓(pid 重启 2426795→144981 已续传无丢) · D-CLEAN-4 复扫(§8)+⭐LLaVA-4B ckpt 专项(§9)已完成待拍板
已完成:       §0.3 8源/§0.4 R2视觉/§0.6 配方/§0.7 停85M·复用·ETA；SFT-2605 下满一致；D-CLEAN 盘点/-2 ≈341G/-3 servers ≈972G/-4 复扫(§8)+⭐LLaVA-4B ckpt 专项(§9)·367 iter≈22 TiB 可回收
当前动作:     唤醒103 巡检(白名单4项)：l1_en_hq 1114/6006(+46 vs 唤醒102，CC-MAIN-2025-33 part-0117在途)、gpic train 2361/8001(+27，pid 2426795→144981 父脚本 download_it_pairs.sh 自动重启续传无丢、gpic_train_02361.tar@19:00 秒级落盘) 真推进；en 2048✓满/zh 171/256 冻结(随 l1 后串行)/en_v1_4 停保留(489·40G)；无僵死无需重启；task.md mtime 09:39 未变、无新指令；git fetch/push github 不可达(Network unreachable)
下一步:       下轮判 retry-loop(3076502)+gpic(144981/父3525273) 真推进(僵死即 kill+重启)→ l1_en_hq(剩4892件~360GB)+zh(剩85件~108GB) 下满即报运维；D-CLEAN-4 候选(LLaVA≈22T/FineVision 4.3T/hell 1.24T/跨用户 3.4T)等运维拍板
阻塞:         无硬阻塞；⚠️ l1_en_hq 速率偏慢(小文件+CDN，非僵死)；磁盘 /nas_train 84%(Avail 35T)；🟡 D-CLEAN-4 候选全部等运维拍板(只盘点不删除)
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
| WAITING | 1（下载中：白名单锁定——retry-loop 3076502+hf 3076519 先拉 l1_en_hq(1114/6006)+zh(171/256 待续)；gpic 144981(父 download_it_pairs.sh 3525273 自动续命) train 2361/8001+test 128✓；en 2048/2048 满；en_v1_4 已停(489 保留)；LLaVA 85M 停无进程；D-CLEAN-4 大盘复扫+⭐LLaVA-4B ckpt 专项(367 iter≈22 TiB 可回收) done（只盘点，Avail 35T/84%）；重 I/O 推迟） |
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

- 2026-10-04 —— 唤醒 97（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成提交、等运维拍板；⭐LLaVA-4B ckpt 目录实测 mtime 2026-09-25 无新写、§9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519** 真推进：**l1_en_hq = 720/6006**（CC-MAIN-2025-30 part-0720-of-1000 在途，~74MB/件；上轮 628@12:56→720@14:04 = +92 件/68min ≈ **~1.65MB/s**，log 逐件 `Download complete` 连续、mtime 14:04 每秒级落盘、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 74MB 小文件连接开销+CDN 慢）。🔵 zh **171/256**、0 .incomplete（冻结，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（ppid=3525273 `download_it_pairs.sh`=gpic 父脚本，cwd /nas_inference/datasets）真推进：train **2147/8001** + test 128/128✓、0 .incomplete（上轮 2098→2147 = +49 件/68min ≈ **~19MB/s**）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留 CC-MAIN-2013-20 未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE（D-CLEAN-3）。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。`sudo -n true` 仍 = password required（D-CLEAN-4 §8 已注）。ETA：l1_en_hq 剩 5286 件≈391GB @~1.65MB/s ≈ **~2.8 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5854 件≈9.4TiB @~19MB/s ≈ **~5.7 天** → base 族就绪(l1_en_hq+zh) ≈2.8 天(偏慢)/0.7 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git 本轮回写后提交。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 98（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成提交、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519** 真推进：**l1_en_hq = 866/6006**（CC-MAIN-2025-30 part-0864-of-1000 在途→实测 864→866 在 ~1min 内 +2，~74MB/件；上轮 720@14:04→866@16:05 = +146 件/~2h ≈ **~1.5MB/s**，mtime 16:03 秒级落盘、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 74MB 小文件连接开销+CDN 慢；⚠️ 路径更正：实测下载 `--local-dir` = `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb`（非 /nas_inference；/nas_inference 那份是 ultrafineweb_en 162 件旧部分副本，勿混））。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（ppid=3525273 `download_it_pairs.sh`=gpic 父脚本，cwd /nas_inference/datasets）真推进：train **2234/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2147→2234 = +87 件/~2h ≈ **~20MB/s**）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留 CC-MAIN-2013-20 未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE（D-CLEAN-3）。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。`sudo -n true` 仍 = password required（D-CLEAN-4 §8 已注）。ETA：l1_en_hq 剩 5140 件≈380GB @~1.5MB/s ≈ **~2.9 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5767 件≈9.3TiB @~20MB/s ≈ **~5.5 天** → base 族就绪(l1_en_hq+zh) ≈2.9 天(偏慢)/0.7 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常（共享 NFS 副本其余 agent 可读）。📉 MEMORY 28.7KB+本条 ≈≤32KB 无需滚动。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。
- 2026-10-04 —— 唤醒 99（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成提交、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~7h）真推进：**l1_en_hq = 916/6006**（CC-MAIN-2025-30 part-0916 区段、~73MB/件；上轮 866@16:05→916@16:39 = +50 件/~34min ≈ **~1.8MB/s**；实测近 10min 落盘 15 件、mtime 16:40:32 秒级、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 73MB 小文件连接开销+CDN 慢；路径实测 `--local-dir`=/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（ppid=3525273 `download_it_pairs.sh`=gpic 父脚本，cwd /nas_inference/datasets）真推进：train **2260/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2234→2260 = +26 件/~34min ≈ **~20MB/s**；近 10min 落盘 7 件、gpic_train_02260.tar mtime 16:40:35）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留 CC-MAIN-2013-20 未删）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE（D-CLEAN-3）。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。`sudo -n true` 仍 = password required（D-CLEAN-4 §8 已注）。ETA：l1_en_hq 剩 5090 件≈376GB @~1.8MB/s ≈ **~2.4 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5741 件≈9.2TiB @~20MB/s ≈ **~5.2 天** → base 族就绪(l1_en_hq+zh) ≈2.4 天(偏慢)/0.7 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换，勿写入文档/日志）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常（共享 NFS 副本其余 agent 可读）。📉 MEMORY ≈31.5KB+本条 ≈≤32KB 无需滚动。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 100（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成提交、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~12.2h）真推进：**l1_en_hq = 974/6006**（CC-MAIN-2025-30 part-0975-of-1000 在途、~73MB/件；上轮 916@16:40→974@17:17 = +58 件/~37min ≈ **~1.9MB/s**；实测近 1min 落盘 part-0974 mtime 17:16:59 秒级、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 73MB 小文件连接开销+CDN 慢；当前仍在 CC-MAIN-2025-30 首个快照(974/1000)，6 快照共 6006 件）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（etime ~47h）真推进：train **2287/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2260→2287 = +27 件/~37min ≈ **~19.5MB/s**；gpic_train_02286.tar mtime 17:16:38）。🔴 en_v1_4 无进程（✅ 已停）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。ETA：l1_en_hq 剩 5032 件≈367GB @~1.9MB/s ≈ **~2.2 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5714 件≈9.1TiB @~19.5MB/s ≈ **~5.6 天** → base 族就绪(l1_en_hq+zh) ≈2.7 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY ≈31.4KB+本条 ≈≤32KB 无需滚动。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。



- 2026-10-04 —— 唤醒 101（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~12.8h，stat Sl/Ss 活）真推进：**l1_en_hq = 1031/6006**（✅ 已完成第 1 快照 CC-MAIN-2025-30(1000 件)、进入第 2 快照 CC-MAIN-2025-33 part-0031-of-1000 在途、~73MB/件；上轮 974@17:17→1031@17:54 = +57 件/~37min ≈ **~1.9MB/s**；log 17:54 实时下载 part-0032、mtime 17:54:09 秒级、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 73MB 小文件连接开销+CDN 慢；6 快照共 6006 件）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（etime ~47.7h，stat Sl 活）真推进：train **2314/8001** + test 128/128✓、0 .incomplete（上轮 2287→2314 = +27 件/~37min ≈ **~19.5MB/s**；gpic_train_02313.tar mtime 17:54:02 秒级）。🔴 en_v1_4 无进程（✅ 已停，488 parquet≈40G 保留）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。ETA：l1_en_hq 剩 4975 件≈363GB @~1.9MB/s ≈ **~2.2 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5687 件≈9.1TiB @~19.5MB/s ≈ **~5.6 天** → base 族就绪(l1_en_hq+zh) ≈2.3 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY ≈29.3KB+本条 ≈≤32KB 无需滚动。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。


- 2026-10-04 —— 唤醒 102（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~13.4h，stat Sl 活）真推进：**l1_en_hq = 1068/6006**（✅ CC-MAIN-2025-30(1000件)已满、CC-MAIN-2025-33 part-0070-of-1000 在途、~73MB/件；上轮 1031@17:54→1068@18:19 = +37 件/~25min ≈ **~1.8MB/s**；log 18:21 实时下载 part-0070、mtime 18:21:18 秒级、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 73MB 小文件连接开销+CDN 慢；6 快照共 6006 件）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **2426795**（etime ~48.3h，stat Sl 活）真推进：train **2334/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2314→2334 = +20 件/~25min ≈ **~21MB/s**；gpic_train_02333.tar mtime 18:21:19 秒级）。🔴 en_v1_4 无进程（✅ 已停，489 parquet≈40G 保留）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。ETA：l1_en_hq 剩 4938 件≈360GB @~1.8MB/s ≈ **~2.3 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5667 件≈9.1TiB @~21MB/s ≈ **~5.2 天** → base 族就绪(l1_en_hq+zh) ≈2.3 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 2426795 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY 滚动迁唤醒93/94/95→daily-memories-data/2026-10-04.md，现≈26KB+本条≈≤32KB。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

- 2026-10-04 —— 唤醒 103（白名单 4 项巡检，无假活、无重启）：复核 `BAIZE_DATA_TASK.md` mtime **09:39 未变**（无新增指令/无索取/无 STOP；D-CLEAN-4 §8+§9 已完成、等运维拍板；⭐LLaVA-4B ckpt §9 ≈22TiB 候选仍 in-place）。🔵 base retry-loop **3076502**+hf **3076519**（etime ~13.9h，stat Sl 活）真推进：**l1_en_hq = 1114/6006**（CC-MAIN-2025-33 part-0117-of-1000 在途、~73MB/件；上轮 1068@18:19→1114@19:01 = +46 件/~42min ≈ **~1.4MB/s**；log 19:00 实时下载 part-0117、mtime 秒级、进程存活 → **非僵死不重启**；⚠️ 速率偏慢疑 73MB 小文件连接开销+CDN 慢；6 快照共 6006 件）。🔵 zh **171/256**、0 .incomplete（冻结，最后 mtime 04:59 part-171，随 l1_en_hq 后串行续）。🔵 gpic **进程已重启 2426795→144981**（父 `download_it_pairs.sh` 3525273 etime~3.1d 自动续命，~18:57 重启、从 gpic_train_02359.tar@18:57:55 续传无丢）真推进：train **2361/8001** + test 128/128✓、1 .incomplete（在途正常）（上轮 2334→2361 = +27 件/~42min ≈ **~19MB/s**；gpic_train_02361.tar mtime 19:00:42 秒级）。🔴 en_v1_4 无进程（✅ 已停，489 parquet≈40G 保留）；LLaVA 85M 停无进程。✅ en 2048/2048 满；✅ SFT-2605 1504/1504 intact；✅ servers GONE。磁盘：/nas_train 173T/207T(84%、Avail **35T**)、/nas_inference 61%(18T)、/nas_user 74%(29T)、/data 4%（均够）。ETA：l1_en_hq 剩 4892 件≈360GB @~1.4MB/s ≈ **~3 天**（偏慢）/乐观 11–16h；zh 剩 85 件≈108GB ≈3h；gpic 剩 5640 件≈8.7TiB @~19MB/s ≈ **~5.3 天** → base 族就绪(l1_en_hq+zh) ≈3 天(偏慢)/~1 天(乐观)。⚠️ gpic 进程 144981 命令行仍暴露 HF token（建议运维轮换）。git：fetch/push 至 github 不可达(Network unreachable)，本地 commit 照常。📉 MEMORY ≈28.4KB+本条≈≤32KB 无需滚动。下一步 = 下轮判 retry-loop+gpic 真推进（僵死即 kill+重启）→ l1_en_hq+zh 下满即「MiniCPM5 base 族就绪」报运维 → gpic 续下至 8001 tar。

## 关键路径速查（供恢复）

- 训练仓库 `BASE_DIR` = `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`（复用其 `mamba2_hybrid_2b/preprocess_data.py` + `data/tokenizer_eod` + `pretrain_launcher.py`）。
- 评测集（只读红线）：`/nas_train/app.e0031982/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`（158 任务，**无 canonical_solution 字段**）。
- 黑名单产物：`run/data_pipeline/blacklist/`（并集 6 快照 536 任务 / 193,295 `ngram_hashes.txt` / 10 `short_ngram_hashes.txt` / meta.json / entry_points.sha256）。
- 校验/打包脚本：`run/data_pipeline/validate_data.py`（phase1 完整性校验，默认轻 I/O）+ `preprocess_text.sh`（phase2 分词打包，复用 Round1 `preprocess_data.py` + 污染闸门）。

