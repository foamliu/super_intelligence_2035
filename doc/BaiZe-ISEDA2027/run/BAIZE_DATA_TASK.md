# BAIZE_DATA_TASK.md

> ⚠️ 本文件为指令文件，agent 只读（禁止修改）。⚠️ 唯一例外（2026-10-06）：按「📉 体积维护规程」，agent 可把「已闭合」的运维块/旧正文【原文】搬入 `run/ARCHIVE_OPERATOR_DATA.md`（只搬迁、留 1 行指针；不新增/不改写任何指令）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔥 运维指令 · 2026-10-21 04:0x（**MiniCPM5 全量数据完整分词 · 224 核全开**）· 用户直令 · 最高优先

> 用户原话：「那就完整分词啊，交代给 data，CPU核有224个，把已经下载的 MiniCPM5 的数据，完整分词！！」
> **背景（decay v2 差 20pp 的核心数据侧根因）**：UltraData-Code **411B token 全量仍未分词**，decay 只用了 `anneal_code` 90M + r3 小样本 140M = **0.23B**，导致 **code 被重复 26 个 epoch**；UltraData-Math（303B）同样只有 ~1B 小样本。**这不是配比问题，是"有数据没用"的问题。**

**① 任务：把下列「已下载但未分词」的数据源做完整分词（不做小样本、不切 mix）**

| 数据源 | 路径 | 规模 | 现状 | 目标产物 |
|:--|:--|--:|:--|:--|
| **UltraData-Code L3** | `/nas_inference/.../openbmb/UltraData-Code/data/UltraData-Code-L3/` | **56B tok** | ❌ 未分词 | `data/full_ultradata_code_l3/…` |
| **UltraData-Code L2** | 同上 `L2/` | **355B tok** | ❌ 未分词 | `data/full_ultradata_code_l2/…` |
| **UltraData-Math L3** | `/nas_inference/.../openbmb/UltraData-Math/data/UltraData-Math-L3/` | **87B tok** | ❌ 未分词 | `data/full_ultradata_math_l3/…` |
| **UltraData-Math L1** | 同上 `L1/` | **184B tok** | ❌ 未分词 | `data/full_ultradata_math_l1/…` |
| **Ultra-FineWeb-L3** | `/nas_inference/.../openbmb/Ultra-FineWeb-L3/data/ultrafineweb_en_l3/qa` | **690B tok** | 部分（仅 p5b_l3 20.56B） | `data/full_ufw_l3/…` |

> ⚠️ **优先级**：**Code L3 → Math L3 → Code L2 → UFW-L3 → Math L1**。理由：decay 20B 实验只需 code 1.6B / math 0.8B，**L3 层 56B+87B 足以支撑，且 L3 是最高质量层，decay 本就该用 L3**。先把 L3 两批分完，**20B decay 实验即可解除数据阻塞**。

**② 并发：用满 224 核**

- 现 en_v1_4 全源分词只用了 **32 workers（throttle@32）**，`nproc`=224 ⇒ **绝大部分 CPU 闲置**。
- 新任务要求：
  - **按 CPU 核数自动定并发**：`NPROC=$(nproc)`；分词进程 **≤ NPROC × 0.85**（留余量给 I/O 与 en_v1_4 现有 worker），即 **~190 并发**。
  - 建议先用 **64 并发做 5 分钟测速**（tok/s、MB/s、CPU 利用率、内存），再按线性外推拉到 **160~190**。
  - `nice -n 10`（不抢 en_v1_4 已有 worker 的交互）。
  - **内存/IO 是真实瓶颈**：每进程读 parquet 解压需内存，先确认 `free -g` 剩余足够（每并发约 1~2GB），不够就按 `可用内存/2GB` 定并发，**不要盲目拉满导致 OOM**。

**③ 产出规范（必须与现有 decay 脚本兼容）**
- 输出 **Megatron `.bin` + `.idx`**（int32）到 `data/full_*` 目录，命名 `<src>_train_s{0..N}` 分片（与 `baize_xmodel25_decay_v2.py:472` 的 `sources.append` 格式一致，便于直接改数据源）。
- tokenizer：**Xmodel-2.5 原生 tokenizer**（vocab 129280，`/nas_train/app.e0031982/models/...`），避免 vocab 不兼容。
- **入库登记**：每完成一个源，把「源 / 路径 / 实际 token 数 / shard 数 / 耗时」写入 `DATA_LEDGER.md` + `MEMORY_DATA.md`。

**④ 与 en_v1_4 的关系**
- en_v1_4 下载（PID1875054）+ 全源分词（PID749330）**继续跑，不要 kill**。
- 新增分词进程**共用机器**，但要 `nice` 降权；若出现 IO 打满导致 en_v1_4 速率跌破 1MB/s，**降低新任务并发**，不要停下载。

**⑤ 回报**
- 每轮写：`源 / 已完成 shard / 累计 token / 并发数 / tok/s / CPU 与内存占用 / ETA`。
- **全部 L3 完成后立刻报**（这是 pretrain 20B decay 实验的解锁条件）。

### ▶️ 运维指令 · 2026-10-20 15:5x（✅ 恢复 en_v1_4 数据下载）· 用户直令 · 已执行

> 用户原话：「data: 可以恢复下载了」。
>
> **动作（本轮唤醒立即执行）**：
> 1. **重启下载**（从暂停点续传，脚本幂等、自动 SKIP 已完成文件）：
>    ```bash
>    cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
>    export HF_PROXY=http://172.19.92.23:13128 HF_ENDPOINT=https://hf-mirror.com
>    export https_proxy=$HF_PROXY http_proxy=$HF_PROXY
>    setsid -f nohup python3 download_en_v1_4_resolve.py > /tmp/en_v1_4_dl_dot23.log 2>&1 &
>    ```
>    （暂停点：**sh95(CC-MAIN-2024-10)@139/512**，95/110 dirs，48267 parquet）；续传从 sh95 起，sh96–110 尚未创建。
> 2. **恢复旧「下载口径」**（2026-10-07 起生效版）：下载**失败 / 僵死 / 速率趋零 / PID 已死就 kill+重启**，报告标「已重启」+ 新 PID，不必等运维点名。
> 3. **分词不受影响**：`run_tokenize_env14_fullsource.sh`（PID 749330）继续跑，下载续上的 shard 落盘后自动排队分词。
> 4. **报告**：报重启后 PID + 续传起点 + 实测 MB/s + 剩余 shard ETA；`DATA_LEDGER.md` 的 en_v1_4 行改回「🟢 下载中」。

### ⏸️ 运维指令 · 2026-10-20（🔴 暂停 en_v1_4 数据下载）· 用户直令 · 最高优先 · 覆盖旧「下载口径」

> **用户原话**：「让 data 暂停数据下载」。
>
> **动作（本轮唤醒立即执行）**：
> 1. **kill 下载进程**：停掉 en_v1_4 下载 —— `download_en_v1_4.py` / `download_en_v1_4_resolve.py`（当前 PID 2732959，resolve.py）及其子进程。**只杀下载，不动分词**。
> 2. **保留分词进程**：`run_tokenize_env14_fullsource.sh`（PID 749330）及其 `preprocess_data_cm` 子进程**继续跑**，把已下载的 shard 分完（**不暂停分词**）。
> 3. **保持暂停**：🚫 **覆盖**旧「下载口径（失败/僵死/速率趋零就 kill+重启）」—— 本轮起**下载保持暂停**，agent **不得重启下载**，直到收到新的「恢复 en_v1_4 下载」指令。
> 4. **记录暂停位置**：在 `MEMORY_DATA.md` 进度快照 + `DATA_LEDGER.md` 记下暂停点（当前 sh94 / 总 parquet 数 / 已下载 dir 数），便于将来续传。
>
> **报告**：本轮唤醒回报「下载已暂停」+ 暂停位置 + 分词仍进行的 done/110 快照。

### 🆕 运维指令 · 2026-10-18 21:0x（🔴 分词口径纠正：不按 1.5T/500B 预算截断；要分就某个数据源全部分词）· 用户直令 · 最高优先 · 覆盖旧「到 500B」表述

> **用户原话**：「Data 分词我没有说按 1.5T 分，要分就某个数据源全部分词。」
> **纠正**：**1.5T / 500B 是 v5 训练取用量估算，不是分词目标、不是停止条件**；分词必须按**某个数据源全量**执行。
>
> **当前源 = `en_v1_4`**：对 `CC-MAIN-*` 全部 **110 个 snapshot 目录**逐 shard 分词，直到 **110/110** 都有 `.bin/.idx/.json`；**不要在第 8 个 shard、92.6B tok 或 500B tok 处停止/宣告完成**。
>
> **执行口径**：
> 1. 当前 `run_tokenize_env14_resume.sh`（PID 2446254）继续跑完已下载 shards；
> 2. 下载完成的 shard（512 parquet 且无 `.incomplete`）立即排队分词；
> 3. 下载未完成的 shard **不提前分词**，标 `PENDING_DOWNLOAD`；
> 4. 全部 110 shard 完成后产出 `env14_fullsource_manifest.tsv` + `env14_fullsource_summary.json`（每 shard tokens/bytes/status + 全源总 tokens），并写入 `DATA_LEDGER.md`；
> 5. 全源完成前，任何报告**不得**写「en_v1_4 分词完成」；
> 6. 当前 `run_tokenize_env14_resume.sh` 退出后，用 **`data_pipeline/run_tokenize_env14_fullsource.sh`** 接管（本次已新增）：自动扫描 110 个 shard、跳过 DONE/RUNNING、下载完成后自动补分，直到 **110/110**；启动：
>    `setsid -f nohup bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/run_tokenize_env14_fullsource.sh > /tmp/run_tokenize_env14_fullsource.log 2>&1 &`
>    （脚本内置等待 resume 退出，避免双 launcher；不要手工再起第二份）。
>
> **报告**：每次唤醒报 `done/110`、`tokens 累计`、`PENDING_DOWNLOAD`、`全源 ETA`。
>
> **并发（2026-10-18 21:0x 用户批准）**：分词可用 **32 或 64 核**。默认 **32**；按当前 8 workers ≈230B tok/day 线性外推：32 ≈ **2.5 天**、64 ≈ **1.3–1.5 天**（全源 2.31T；实际受 NFS/内存影响）。先以 32 起跑，10–15 分钟后看 `pgrep -c preprocess_data_cm`、`/proc/io`、NFS 延迟与 tok/s；若近似线性且内存充足，再升 64。
>
> **接管方式**：当前 `run_tokenize_env14_resume.sh`（PID 2446254）只是发射器；先 `kill 2446254`（**不要杀 8 个 `preprocess_data_cm.py` 子进程**），确认子进程仍 alive 后，立即：
> `MAX_CONCURRENT=32 setsid -f nohup bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline/run_tokenize_env14_fullsource.sh > /tmp/run_tokenize_env14_fullsource.log 2>&1 &`
> 若 kill 把子进程也带走，等子进程退出后再启动；DONE shard 自动跳过，不会重复分词。
>
> 🚫 不为凑 500B/1.5T 跳 shard、不混源部分分词、不把训练取用量当分词上限。


### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


### 🆕 运维指令 · 2026-10-18 10:2x（🔧 **P0：恢复 git push（换代理疑似污染全局 proxy 环境）**）· 用户直令 · 与续传令并行

> **判断**：换 `.23` 代理过程中可能在 shell/服务里全局 export 了 `http_proxy/https_proxy/ALL_PROXY`，导致 `git push` 走不通（尤其远端是 HTTPS 时）。**下载用 HF 代理 ≠ git 走代理**。
> **要求**：
> 1. 先只读诊断：`git remote -v`、`git status -sb`、`env | grep -iE 'proxy|HF_'`、`git config --get-regexp '.*proxy'`、`ls .git/index.lock`。
> 2. `git` 一律**剥离 HF 代理**执行：`env -u http_proxy -u https_proxy -u ALL_PROXY -u all_proxy git fetch/pull/push origin main`；🚫 不要为 git 永久写 `git config --global http.proxy`。
> 3. 若远端是 SSH（`git@github.com:`），代理环境本不影响；若仍失败，贴 `GIT_SSH_COMMAND="ssh -v" git ls-remote origin HEAD` 原文。
> 4. 修好后**立刻执行同日②的续传令**（`.23+hf-mirror`，25 shard）+ 启分词；ops 中继会在恢复后执行 RUN_ID 123 的 `.12` git 只读诊断，可与中继结论互相印证。

### 🆕 运维指令 · 2026-10-18②（🔴 **P0：立即改用 `172.19.92.23:13128` + hf-mirror 续 `en_v1_4` 最后 25 个 shard**）· 用户直令 · 覆盖同日①的"先探针"

> **背景**：你已经连续多轮报 `.25` → `huggingface.co HTTP=000 timeout`，但 **`.23 + hf-mirror` 已由中继在 `.12`/`.29` 双机实测为 200**：
> `.23→hf-mirror` **200 / 0.33s**、`.23→hf-mirror API tree` **200 / 0.35–0.57s**（RUN_ID 122，2026-10-18 07:31）。⇒ **不要再等 `.25`**。
> 现状：**43,520 parquet / 0 incomplete / 4.1T / 85 of 110 shard 完成，只差 25 个**。

**① 立即执行（不再探针、不再等待）**
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data_pipeline
export HF_PROXY=http://172.19.92.23:13128
export HF_ENDPOINT=https://hf-mirror.com
export https_proxy=$HF_PROXY; export http_proxy=$HF_PROXY
export HF_HUB_ENABLE_HF_TRANSFER=1; export HF_HUB_DOWNLOAD_TIMEOUT=120
setsid -f nohup bash download_en_v1_4.sh > /tmp/en_v1_4_dl_dot23.log 2>&1
```
- ⚠️ **脚本已由运维改成读 `HF_PROXY`/`HF_ENDPOINT`**（原 L26-27 硬编码 `.25` 已移除）⇒ **必须先 `git pull`**，否则仍会走 `.25`。
- 若 `.sh` 的 API 列目录失败 ⇒ 改 `setsid -f nohup python3 download_en_v1_4.py > /tmp/en_v1_4_dl_dot23.log 2>&1`（24 workers 并行版）。
- **已完成的 85 个 shard 自动 SKIP，不要删、不要重下。**

**② 判活（10–15 min 内给结论，🚫 不看进程存活，只看字节增长）**
- `du -s` 目标目录两次（间隔 120s）必须增长；或 `/proc/<pid>/io` 的 `write_bytes` 增长；或日志出现新的 `downloading/DONE`。
- **零增长 ⇒ 判假活**：kill wrapper → 换 ① 的 Python 并行版 → 仍零增长则报 blocker（贴报错原文）。

**③ 回报（本轮就要）**
1. `.23 + hf-mirror` 下的实测：**MB/s**、已完成 shard 数（从 85 起算）、**25 个剩余 shard 的 ETA**（按实测速率算，禁止沿用旧 7–8 天口径）。
2. 日志路径 `/tmp/en_v1_4_dl_dot23.log` + `pgrep -af download_en_v1_4` 原文。
3. 完成后自校：`parquet` 数 vs HF 清单、`.incomplete==0`，写入 `DATA_LEDGER.md`。

**④ 紧接着（本令的第二优先，不阻塞 ①）**
- **en_v1_4 开始分词**（P-8/v5 的 S1 要 500B token）：复用 `preprocess_data.py` + `tokenizer_eod`，`nice -19`，并发 4–8；**先报预计 B tok/天 与到 500B 的天数**。
- 🚫 85M 维持暂停；🚫 不动 GPIC/WebMix/InternVL/wit_base/cauldron/SFT-2605/RL-2609；🚫 不改 `.12` 上 vision 正在用的 GPU 任务（vision P0 已占用 8 卡，分词只用 CPU）。


> **用户令（2026-10-18）**：「data: 既然 172.19.92.25:13128 返回503，那就尝试用 172.19.92.23:13128+hf-mirror 来续传」

**① 范围（只动 `en_v1_4` 一路）**
- 目标：`openbmb/Ultra-FineWeb · data/ultrafineweb_en_v1_4/`（56,461 文件 / 6.75TB），落盘 `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/` 不变。
- 现状（唤醒 522）：**43,520 parquet / 0 `.incomplete` / 4.1T / 85 of 110 snapshot 目录完成**；wrapper 已退出（03:59，`completed=14 skipped=71 failed=25`）⇒ **只需续 25 个失败 shard**，已有的 85 个目录自动 SKIP（🚫 不要删、不要重下）。
- 🚫 **不动**：85M（维持用户令 10-13 暂停）、GPIC、WebMix-38M、InternVL-SA1B、wit_base、the_cauldron、SFT-2605、RL-2609；不动 `.25` 上任何已完数据。

**② proxy 口径（本令覆盖 10-15「.12 下数据一律 .25 直连 hf.co」——仅限 `en_v1_4` 这一路）**
```bash
export HF_PROXY=http://172.19.92.23:13128     # ⚠️ 不是 .25
export HF_ENDPOINT=https://hf-mirror.com      # 92.23 恒配 hf-mirror（用户 10-15 口径）
export https_proxy="$HF_PROXY"; export http_proxy="$HF_PROXY"
export HF_HUB_DOWNLOAD_TIMEOUT=120
export HF_HUB_ENABLE_HF_TRANSFER=1
```
- 若 `.23` 恢复后改用 `.25`：`HF_PROXY=http://172.19.92.25:13128` 且 **unset HF_ENDPOINT**（直连 hf.co）。
- ⚠️ **脚本已改（运维 2026-10-18 直接提交）**：`run/data_pipeline/download_en_v1_4.py` 原先在 **L26-27 硬编码 `.25`**、`.sh` 在 L11-12 硬编码 `.25` ⇒ **只 export 环境变量无效**。现两脚本均改为读 `HF_PROXY` / `HF_ENDPOINT`（未设时默认 `.23` + hf-mirror）。**先 `git pull` 拿到新版再起**；若你本地有未提交改动，以本令为准合并，别把硬编码 `.25` 带回来。

**③ 第一步：连通性探针（必须先做；单行命令，可直接复制到 `.12` 的 bash）**
```bash
curl -sS -m 20 -o /dev/null -w '.25 baseline -> hf.co: %{http_code} %{time_total}s\n' -x http://172.19.92.25:13128 https://huggingface.co
curl -sS -m 20 -o /dev/null -w '.23 -> hf-mirror: %{http_code} %{time_total}s\n' -x http://172.19.92.23:13128 https://hf-mirror.com
curl -sS -m 25 -o /dev/null -w '.23 -> hf-mirror API: %{http_code}\n' -x http://172.19.92.23:13128 https://hf-mirror.com/api/datasets/openbmb/Ultra-FineWeb/tree/main/data/ultrafineweb_en_v1_4
curl -sS -m 20 -o /dev/null -w '.23 -> 无 mirror: %{http_code}\n' -x http://172.19.92.23:13128 https://huggingface.co
```
- **过闸判据**：`.23→hf-mirror` 与 `.23→hf-mirror API` **都返回 200/3xx**。任一非 200/3xx ⇒ **不要把 wrapper 起满**，按 ④ 的 B/C 处理并回报原文。

**④ 起训（按探针结果选一条；同样单行，避免续行符被 Markdown 吞掉）**
```bash
# A 默认（探针全通）——脚本已改读 HF_PROXY/HF_ENDPOINT，默认即 .23 + hf-mirror
export HF_PROXY=http://172.19.92.23:13128; export HF_ENDPOINT=https://hf-mirror.com; setsid -f nohup bash download_en_v1_4.sh > /tmp/en_v1_4_dl_dot23.log 2>&1
# B `.23` 通但 hf download 列目录失败——改 Python 并行版（24 workers，per-snapshot 非递归 listing）
export HF_PROXY=http://172.19.92.23:13128; export HF_ENDPOINT=https://hf-mirror.com; setsid -f nohup python3 download_en_v1_4.py > /tmp/en_v1_4_dl_dot23.log 2>&1
```
- 日志用**新文件名** `en_v1_4_dl_dot23.log`，保留旧 `en_v1_4_dl.log` 作证据；起 wrapper 前确认 `pgrep -af download_en_v1_4` 无残留旧进程。
- **C（`.23` 也不通）**：**不许空转重试**——停手，把探针四条原文 + `.25` 恢复时的重启用命令写进心跳，报 blocker 等运维。

**⑤ 保活 / 判活（10–15 min 内必须给一次结论）**
- 进程：`pgrep -af 'download_en_v1_4'`（应见 wrapper PID + hf/python 子进程）。
- **真推进（硬判据，🚫 不看进程存活）**：日志里出现 `[n/110] CC-MAIN-XXXX: downloading/DONE` **且** 目标目录 `du` 或 `/proc/<hf-pid>/io write_bytes` **在 120s 内增长**；或 `.incomplete` 字节增长。
- 若 10 min 内 0 字节增长 ⇒ 视为假活：kill 该 wrapper → 换 ④-B 或 ④-C。

**⑥ 回报（这一轮就要）**
1. 探针 4 行原文（`.25` / `.23→mirror` / `.23→mirror API` / `.23→无 mirror`）。
2. 用的哪条路径（A/B/C）+ wrapper PID + 日志路径 + 实际 `HF_PROXY` / `HF_ENDPOINT` 值。
3. 25 个待续 shard 名单（从旧日志 `failed` 行取），完成后逐 shard 的 parquet 计数。
4. **速率 + ETA**：先报 **MB/s（或 files/min）实测**，再给「25 shard 剩余 GB ÷ 速率」的 ETA；不许沿用旧的 7–8 天口径。
5. 完成后自校：`parquet` 计数 vs HF 清单、`.incomplete == 0`，写入 `DATA_LEDGER.md`。
6. 写 `MEMORY_DATA.md` 进度快照（PHASE/当前动作/下一步/阻塞 四行必须提到「`.23`+hf-mirror」）+ `daily-memories-data/2026-10-18.md`；commit 前缀 `data dl:`。

**⑦ 纪律**
- 只在这条线上换 proxy；**别线（vision 的 HF 评测、harness 安装包、git push）仍按 `run/ops/README.md §7` 口径**，🚫 不要顺手改全局 `~/.bashrc` / `git config`。
- `git pull --rebase --autostash` 后如遇 `.25` 与 `.23` 记录冲突：**保留双方**（两条探针结果都要留档）。
- 任务书 >32KB 自滚归档（只搬已闭合块原文 + 1 行指针）。


### 🆕 运维指令 · 2026-10-17（🧹 清理本线 .12 /tmp 残留）· 用户直令
> 📦 已闭合（/tmp 清理已完成，残留=0）→ 原文 `daily-memories-data/2026-10-17.md`。

### 🆕 运维指令 · 2026-10-15（⬇️ **补下 `UltraData-RL-2609`** + 复核 SFT-2605）· 用户直令 · 最高优先

> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-15（补下 RL-2609 + 复核 SFT-2605）」。
> **结论**：RL-2609 已下满并逐文件字节自校通过（20 jsonl / 174.75 GiB）；SFT-2605 复核通过（1504 jsonl / 0 incomplete），🚫 不需重下。需要时再读。


> **用户令（2026-10-15）**：「data：验证一下 `UltraData-SFT-2605`、`UltraData-RL-2609` 是否真的没有，没有就重新下载。」

### 🆕 运维指令 · 2026-10-14（▶️ 恢复全部 4 路下载 · 断点续传）· 用户直令 · 最高优先> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§运维指令·2026-10-14（恢复全部 4 路下载·断点续传）」。
> **结论**：WebMix-38M / InternVL-SA1B / wit_base 已下满；en_v1_4 由 2026-10-18（.23 + hf-mirror 续传）接管。需要时再读。

### 🆕 运维指令 · 2026-10-14（💾 新增下载落盘位置 `/nas_env`）· 用户直令 · 常驻> 📦 **已归档（2026-10-18 运维滚动，原文未改）** → `run/ARCHIVE_OPERATOR_DATA.md`「§2026-10-14（新增落盘位置 `/nas_env`）」。常驻口径不变：`/nas_env` 仍为合法落盘地（仅用于新增下载）。需要时再读。

### 🆕 运维指令 · 2026-10-13（⏸ 暂停 85M + 📥 下载 HF 图文对 TOP-5 中「未下载」的 4 个 · 落 `/nas_inference` 或 `/nas_user` 的 datasets（🚫 不放 `/nas_train`））· 用户直令 · 最高优先
> 📦 已闭合（TOP-5 4 路均下完；85M 仍暂停）→ 原文 `daily-memories-data/2026-10-13.md`。

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
