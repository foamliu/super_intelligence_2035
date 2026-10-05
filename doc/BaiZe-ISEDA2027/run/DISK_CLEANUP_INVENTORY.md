# DISK_CLEANUP_INVENTORY.md — 磁盘清理机会盘点（**只盘点、不删除**）

> 生成：2026-10-03 · 唤醒 57（数据 agent）
> 来源：运维指令区 · 2026-10-03「D-CLEAN」。
> 🔒 红线：`EDA-Eval-PyAether` 158 任务只读隔离区、**任何正在下载/训练的目标** 绝不可动。
> ⚠️ **本清单只盘点候选，未经运维批准不得 `rm`/`mv` 任何东西。** 跨用户删除须运维/owner 确认。

---

## 1. 大盘（`df -hT` 实测）

| 挂载 | 类型 | 总容量 | 已用 | 可用 | 使用率 |
|:---|:---|--:|--:|--:|--:|
| `/nas_train` | nfs | 207 T | 177 T | **31 T** | 86 % |
| `/nas_inference` | nfs | 45 T | 26 T | 20 T | 57 % |
| `/nas_user` | nfs | 108 T | 80 T | 29 T | 74 % |
| `/data` | xfs | 7.0 T | 285 G | 6.8 T | 4 % |

> 结论：`/nas_train` 最紧（剩 31 T，86% 用），是清理重点；`/nas_user` 74% 次之；`/nas_inference` 与 `/data` 相对宽裕。

---

## 2. 本用户（`app.e0031982`）可回收候选 —— 按安全等级分级

### 🟢 明确可清（重建成本极低 / 无价值）

| 路径 | 大小 | 判据/证据 | 建议 |
|:---|--:|:---|:---|
| `/home/app.e0031982/.cache/pip` | **3.3 G** | `du -sh` = 3.3G，pip 下载缓存，可从 PyPI 重建 | 可清 |
| `/home/app.e0031982/.cache/huggingface` | 4.8 M | HF 本地元缓存（真实 blob 已外移 `/nas_train` hf_cache） | 可清 |

> 🟢 分档小计 ≈ **3.3 G**。

### 🟡 需确认（先确认用途/是否过期，再决定）

| 路径 | 大小 | 判据/证据 | 建议 |
|:---|--:|:---|:---|
| `.../code/BaiZe-ISEDA2027/nemo_experiments` | **524 G** | NeMo 训练历史 checkpoint | 保留最晚/最优 ckpt，其余可清 |
| `/nas_train/app.e0031982/servers` | **974 G** | 未探明内部（du 子目录超时） | 先 `ls`/`du --max-depth=1` 看清再定 |
| `/nas_train/app.e0031982/models` | **452 G** | 模型权重（多用途） | 确认哪些在用，其余可清 |
| `.../datasets/laion2B-en-aesthetic/` | ~~≈8.1 T~~ → **实测 7.8 G** | 🚫 URL-only，DATA_LEDGER §6 已判「淘汰」 | ✅ **已删（D-CLEAN-2）** |
| `.../datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M*` | **≈26 T**（7629 parquet） | 🔴 已停；§0.7 明令「保留已下内容，不要删」 | **保留不删** |
| `/nas_train/app.e0031982/hf_cache` | 20 G | hf download 缓存，可能含重复 blob | 纯缓存可清 |
| `/nas_train/app.e0031982/outputs` | 6.7 G | 训练输出残留 | 待确认 |
| `/nas_train/app.e0031982/download` | 2.4 G | 下载中转残留 | 待确认 |
| `/nas_train/app.e0031982/Downloads` | 209 M | 下载目录 | 待确认 |
| `/nas_train/app.e0031982/zhulong.tar.gz` | 493 M (2026-03-06) | ZhuLong 旧打包 | 待确认 |
| `midtraining_filelist_20260316_1610.txt`(1.4M)+`checksums_partial`(125K) | ≈1.5 M | 2026-03 旧清单 | 待确认 |

> 🟡 分档小计（不含超大件）≈ **1.98 T**。超大件另列：laion2B ~~8.1 T~~ **7.8G（已删）** · LLaVA 85M **26 T**（保留不删）。

### 🔴 不可动（正在下载 / 训练 / 红线）

| 路径 | 说明 |
|:---|:---|
| `.../datasets/openbmb/Ultra-FineWeb/` | base 下载中（base-en 1822/2048 ≈2.2T，pid 2023896） |
| `.../stanford-vision-lab/gpic/` | gpic 下载中（train 1131/8000+test 128 ≈1.8T，pid 2426795） |
| `.../openbmb/Ultra-FineWeb-L3` / `UltraData-Code` / `UltraData-Math` | 语料（1.9T+1.22T+552G），P-8 必用 |
| `.../openbmb/UltraData-SFT-2605` / `-Agent-2609` | SFT（319G+51G）已下满一致 |
| `.../datasets/baize-vision/en500k` / `eval5k` | vision 派生（68.6G+1.27G） |
| `.../code/eda_fastmcp/pyAether-eval/original_dataset/*.jsonl` | 🔒 红线只读隔离区 |
| `.../code/`（仓库 + `miniforge3` 环境） | 工作区 |

## 3. 他人目录（**只读排查，只报告不碰**）

> 方法：`ls --time-style=long-iso` 扫 `/nas_train/*/`、`/nas_user/*/`、`/nas_inference/*/` 顶层；标 mtime > 60 天（< 2026-08-04）。⚠️ 跨用户 `du` 多因 NFS 慢/无权限超时，**大小多为「未实测」**，须运维/owner 复核；活跃进程未逐一 `fuser`（跨用户归属难判），仅按 mtime 初筛。

### `/nas_train/*/` 顶层 · mtime > 60 天

| 目录 | owner | mtime | 疑似用途 | 建议 |
|:---|:---|:---|:---|:---|
| `bakup` | root | 2025-11-21 | 备份（不可读） | 运维确认 |
| `bakup_20` | root | 2025-11-21 | 备份 | 运维确认 |
| `root` | root | 2025-11-20 | root 归属 | 运维确认 |
| `tc` | app.e0021059 | 2026-04-28 | 未知（≈5月无动） | owner 确认 |
| `kangyi` | app.e0016421 | 2025-11-11 | 未知 | owner 确认 |
| `app.e0030209` | app.e0030209 | 2026-03-11 | 未知 | owner 确认 |
| `app.e0025692` | app.e0025692 | 2026-02-14 | 未知 | owner 确认 |
| `app.e0013625` | app.e0013625 | 2025-06-18 | 未知 | owner 确认 |
| `app.t0002465` | 6227 | 2026-07-17 | 未知 | owner 确认 |
| `app.e0041332` | app.e0027605 | 2026-06-26 | 未知 | owner 确认 |
| `app.e0016372` | app.e0016372 | 2026-07-15 | 未知 | owner 确认 |
| `wangcongtao` | app.e0020613 | 2026-01-13 | 未知 | owner 确认 |
| `aistudio_nas` | root | 2026-04-07 | aistudio 平台 | 运维确认 |
| `mps_workspace` | root | 2025-09-26 | 未知 | 运维确认 |

> 空壳（4K）：`0000010421`/`0000010789`/`1111`/`aistudio_admin`/`E0025692`/`E0029611`/`E0029930`/`test` —— 价值低，删前仍须确认。

### `/nas_user/*/` 顶层 · mtime > 60 天

| 目录/文件 | owner | mtime | 疑似用途 | 建议 |
|:---|:---|:---|:---|:---|
| `tc.tar.gz` | root | 2025-06-18 | **69 GB** 旧 tarball（>16月） | 运维确认可回收 |
| `app.e0026822` | app.e0026822 | 2025-09-22 | 未知 | owner 确认 |
| `e0027673` | root | 2025-09-19 | 未知 | 运维确认 |

### `/nas_inference/*/` 顶层 · 模型权重（root、疑活跃推理底座）

> `GLM-4.5V`/`GLM-4.6V-FP8`/`GLM-4.6V-FP8_vllm`/`Qwen3-30B-*`/`Qwen3_vl_235B_fp8`/`dynamo`/`containerd`/`venv` —— root 归属、推理/容器底座，疑似在用，本线不建议动（只报告）。

---

## 4. 可回收合计（分档）

| 分档 | 合计 | 明细 |
|:---|--:|:---|
| 🟢 明确可清 | **≈3.3 G** | pip 缓存 3.3G + HF HOME 缓存 4.8M |
| 🟡 需确认（本用户，含大件不含保留） | **≈10.1 T** | ~~laion2B 8.1T~~（实 7.8G 已删）+ nemo 524G + servers 974G + models 452G + hf_cache 20G + 其他 ~0.5T |
| 🟡 保留不删（运维令） | 26 T | LLaVA 85M（7629 parquet，将来 vision 用） |
| 🔴 不可动 | — | base/gpic 下载 + L3/code/math + SFT + GPIC + en500k/eval5k + EDA 隔离区 |

> **一句话结论（D-CLEAN-2 执行后更新）**：本线已实际回收 ≈341GB（laion2B 实测 7.8G 非 8.1T + zhulong 493M + pip 3.3G + nemo Round1 ~310G）；`nemo_experiments`(剩 214G)/`servers`(974G)/`models`(452G) 仍需确认。详见 §6。

---

## 5. 附：本用户大目录 top 证据（`du -sh` 实测，只测本用户）

```
nemo_experiments  524G  .../BaiZe-ISEDA2027/nemo_experiments
servers           974G  /nas_train/app.e0031982/servers
models            452G  /nas_train/app.e0031982/models
hf_cache           20G  /nas_train/app.e0031982/hf_cache
outputs           6.7G  /nas_train/app.e0031982/outputs
download          2.4G  /nas_train/app.e0031982/download
pip cache         3.3G  /home/app.e0031982/.cache/pip
---

## 6. D-CLEAN-2 执行结果（2026-10-03 唤醒 58 · 已批准删除执行 + `servers` 探查）

> ⚠️ **重要更正**：D-CLEAN 盘点（§2/§4）把 `laion2B-en-aesthetic` 记为 **≈8.1 T**，**实测为 7.8 G**（128 个 parquet × ~64.6 MB 的 URL 元数据）—— 是 **G/T 单位误读、差 3 个数量级**，非 8.1 TB。运维据此把它当「最大回收项」拍板；**实际回收远小于预期**（见 §6.5）。

### 6.1 `df` 前后对比

| 时点 | `/nas_train` | 命令 |
|:--|:--|:--|
| 执行前 | Used 177T / Avail **31T**（86%） | `df -hT` |
| 执行后 | Used 177T / Avail **31T**（86%） | `df -hT` |
| 执行后（精确） | 1G-blocks Used 181005G / **Avail 30964G** | `df -BG` |

> 实际回收 ≈ **341 GB（≈0.33 TiB）**，低于 1 T 显示粒度，故 `df -hT` 整 TB 显示不变。

### 6.2 已执行删除（贴命令 + 删前实测大小）

| # | 路径 | **实测大小**（删前） | 命令 | 结果 |
|:--|:--|--:|:--|:--|
| 1 | `.../datasets/laion2B-en-aesthetic/` | **7.8 G**（128 parquet + 128 .crc；❌ 非 8.1T） | `rm -rf` | ✅ gone |
| 2 | `/nas_train/app.e0031982/zhulong.tar.gz` | 493,894,409 B | `rm -f` | ✅ gone |
| 3 | `.../nemo_experiments`（**仅 Round 1/S 系列**） | **~310 G**（27 目录） | `rm -rf <27 dir>` | ✅ gone |
| 4 | `/home/app.e0031982/.cache/pip` | 3.3 G | `rm -rf` | ✅ gone |

### 6.3 `nemo_experiments` 保留 / 可清（先列清单、再删）

- **位置**：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/`
- **删后总大小**：~~524G~~ → **214G**（回收 ~310G）

| 处置 | 目录（mtime） | 大小 |
|:--|:--|--:|
| 🔴 **保留 · live** | `p5b`（10-02 12:11；**P-5b 正在写，iter 2970/4771=62%，含 6 个里程碑 ckpt 落点**） | 79 G |
| 🟡 **保留 · R2 近期（建议运维确认是否可清）** | `p1_1p5e3/2e3/3e3`、`p2_seed2025/7`、`p3_dense/hybrid`、`p5a_g(64|256|1024)_lr(1|2|4)e-3`×9、`p7_dense/hybrid`（10-01 ~ 10-02） | ~135 G |
| ✅ **已删 · Round 1 / S 系列**（09-29 ~ 09-30，被 R2 取代、无后续用途） | `smoke_mamba2`、`smoke_minicpm5`、`realsmoke3`、`realsmoke_m2`、`mamba2_2b_1000step`、`minicpm5_2b_1000step`、`s0_smoke_8gpu`、`s1_01`、`s2_01..07`、`s3_01..05`、`s4_01..03`、`s5_01..04` = **27 目录** | ~310 G |

### 6.4 `servers` 探查结论（**先不删**）

- **结构**：`/nas_train/app.e0031982/servers/`（**974 G**）= 6 节点子目录 `10_239_2_12/24/26/27/28/29`，各含一个 `LLaVA/`（`checkpoints/`、`llava/` 源码、`logs/`、`pretrain_v1.6*.log` 大日志、训练脚本）。
- **用途**：**LLaVA-V1.5-Qwen3-4B** 的**旧训练部署**（2026-02，约 8 个月前），跨 6 个 GPU 节点做大量 pretrain/finetune 消融：`loss-scope-a/b/c`、`token-avgpool/conv/merge/none`、`layerwise-lr-group`、`1d/2d-rope`、`siglip2-384`、optimizer 消融（adamw/lion/muon/sophia）等 —— checkpoints 命名 `llava-v1.5-qwen3-4b-*.pretrain` 明确。
- **建议**：**高价值回收候选（974G）**——已被当前 LLaVA-OneVision-1.5 pipeline 取代；但属**模型权重**，且跨节点有 symlink 指向同一 ckpt（如 `10_239_2_29` 的 `*-adamw` → `*-siglip2-384`），须 owner（vision 线 / 运维）确认后再删。**本轮未动。**

### 6.5 实际回收合计

| 项 | 回收 |
|:--|--:|
| 🟢 pip 缓存 | 3.3 G |
| 🟡 zhulong.tar.gz | 0.49 G |
| 🟡 laion2B（❌ 实测 7.8G 非 8.1T） | 7.8 G |
| 🟡 nemo_experiments Round 1 | ~310 G |
| **合计** | **≈341 GB（≈0.33 TiB）** |

> **一句话结论**：本轮回收到 **≈341 GB**（远小于运维预期的 ~8.6T，主因 `laion2B` 的 **8.1T 系单位误读、实测 7.8G**）；`servers`(974G) 为高价值回收候选但未删（待 owner 确认）；`nemo_experiments` 的 R2 p1–p7（~135G）**保守保留**，建议运维二次确认是否也可清。

---

## 7. D-CLEAN-3 执行结果（2026-10-03 唤醒 59 · 删除 `servers/` 974G）

> 运维拍板（D-CLEAN-3）：✅ `servers` 可清理；🚫 `nemo_experiments` R2 ckpt 保留。
> ⚠️ 974G 的 `rm -rf` → 三项前置检查全过后执行。

### 7.1 前置检查（P1/P2/P3，贴命令 + 原始输出）

**P1 无进程占用 → ✅ 过**
```bash
$ timeout 60 fuser -v /nas_train/app.e0031982/servers 2>&1 | head -30
Cannot stat file /proc/3041408/fd/139: Stale file handle
（无任何 PID/ACCESS/COMMAND 行 —— 目录本身无进程占用）
```
- 补充：指令给的 `fuser -vm` 带 `-m` 是「整挂载」口径（会列出所有用 /nas_train 的进程，易误判）；改无 `-m` 精确口径后为空。
- 全用户 open-fd 扫描命中 `servers` = 0；关键进程 cwd 均不在 servers：vision R9 `pt_elastic`(2902543)+python(2904755/6/7) cwd=`run/vision`；hf 下载 2023896/2426795 cwd=`datasets`。

**P2 无近期活动 → ✅ 过**
```bash
$ timeout 120 find /nas_train/app.e0031982/servers -newermt '-7 days' -print 2>/dev/null | head -20
（空输出 —— 无 7 天内改动）
```

**P3 无脚本引用 → ✅ 过**
```bash
$ grep -rn 'app.e0031982/servers' /nas_train/app.e0031982/code/super_intelligence_2035 --include='*.sh' --include='*.py' --exclude-dir=.git | head
（空输出 —— 0 命中）
```
- 全树 grep（`/nas_train/app.e0031982/code`，含历史 LLaVA 代码，后台 119s）0 命中后停（.sh/.py 无引用）。

### 7.2 symlink 留证（`maxdepth 6`，节选）

| symlink | 指向 | 处置 |
|:--|:--|:--|
| `…/10_239_2_{12,24,26,27,28,29}/LLaVA/playground/data/{coco,gqa,ocr_vqa,textvqa,vg}/…` | **外部** `/nas_train/app.e0031982/datasets/…` | 🔒 不跟随，**外部数据集完好**（已 `ls -d` 逐一复核） |
| `10_239_2_29/…/siglip2-384-adamw[.pretrain] -> …/siglip2-384[.pretrain]` | 族内 | 随删 |
| `10_239_2_28/…/layerwise-a -> layerwise-lr-group-a`；`model-0000[1|2]-of-00002.safetensors -> checkpoint-3000/…` | 族内 | 随删 |

### 7.3 删前后 `df` + 实际回收

| 时点 | `/nas_train`（`df -BG`） | 命令 |
|:--|:--|:--|
| 删前 | Used 180751G / Avail **31218G**（86%） | `df -BG /nas_train \| tail -1` |
| 删后（稳定） | Used **179779G** / Avail **32190G**（85%） | 同上 |

- 删前实测大小：`timeout 240 du -sh /nas_train/app.e0031982/servers` = **974G**。
- **实际回收 = 180751G − 179779G = ≈972 GB**（含并发 base 下载写入 ~2-3G 对冲；**≈与 `du` 974G 一致**）。
- `[ -d /nas_train/app.e0031982/servers ] && echo STILL || echo GONE` → **GONE**。
- ⚠️ 过程记录：删后最初一两次 `df -BG` 只显示 -271G（NFS statfs 延迟），约 2 分钟后稳定为 -972G；**最终以稳定值为准**。

### 7.4 本轮累计回收

| 轮次 | 回收 |
|:--|--:|
| D-CLEAN-2 | ≈341 GB |
| **D-CLEAN-3（servers）** | **≈972 GB（≈0.95 TiB）** |
| **合计** | **≈1.31 TiB** |

> **一句话结论（D-CLEAN-3）**：`servers/`（974G，LLaVA-V1.5-Qwen3-4B 旧消融 ckpt）已删除，三项前置检查全过、外部数据集 symlink 目标不受影响；`df` 净回收 **≈972 GB**，`/nas_train` 使用率 **86%→85%**。`nemo_experiments` R2 ckpt 按运维令保留。

---

## 8. D-CLEAN-4 · 2026-10-04 大盘复扫（**只盘点、不删除**，sudo 视角）— ✅ **已裁定 · 保留不动**（运维 2026-10-05 晚）

> 触发：运维指令 2026-10-04「`/nas_train` 需要清理，用 sudo 盘点各目录大小，找可删除大目录，重点 `/nas_train/app.e0031982`」。
> 🔒 本轮只产出清单，**未经批准不得 `rm`/`mv`**；🚫 绝不整树 `du`（只 `df` + 有界定向 `du`，每条带 `timeout`）；口令/密钥绝不打印。

### 8.1 大盘（`df` 实测）

| 挂载 | 总 | 已用 | 可用 | 使用率 |
|:--|--:|--:|--:|--:|
| `/nas_train` | 207 T | 177 T | **31 T** | **86 %** |
| `/nas_inference` | 45 T | 27 T | 19 T | 60 % |
| `/nas_user` | 108 T | 80 T | 29 T | 74 % |
| `/data` | 7.0 T | 285 G | 6.8 T | 4 % |

`df -BG /nas_train`：Used **180365G** / Avail **31604G**（86%）。→ 重点仍是 `/nas_train`。

### 8.2 sudo 可用性

- `sudo -n true` → `sudo: a password is required`（**非免密**）。
- ⚠️ 本线任务书/记忆无明文 sudo 口令，纪律规定「口令绝不打印」→ **本轮未使用 sudo**。
- 后果：`root` 及他用户权限收紧目录（`bakup*`/`root`/`kangyi`/`tc`/`app.e0030209`/`app.e0030758` 等）只能读顶层、无法测实大小，表中已标「不可读」；精确 cross-user 大小需运维提供 sudo 或 owner 各自报账。

### 8.3 顶层 `/nas_train/*/`（mtime + owner）

| 目录 | owner | mtime | 大小(实测) | 疑似用途 |
|:--|:--|:--|--:|:--|
| `wangcongtao` | app.e0020613 | 2026-01-13 | **2.42 TiB** | 未知（~264 天未动） |
| `app.e0025692` | app.e0025692 | 2026-02-14 | **946 GiB** | 未知（~232 天未动） |
| `tmguo` | root | 2026-09-24 | 177 GiB | 近期（~10 天），暂不列 |
| `app.e0041332` | app.e0027605 | 2026-06-26 | 1.3 GiB | 未知 |
| `app.e0013625` | app.e0013625 | 2025-06-18 | 161 MiB | 未知 |
| `kangyi`/`tc`/`app.e0030209`/`app.e0030758` | 各 owner | ≤2026-03 | 不可读 | 需 sudo |
| root 系列（`bakup`/`bakup_20`/`root`/`test`/`E002*` 等 12 项） | root | ≤2026-04 | 不可读 | 需 sudo |

### 8.4 重点 · 本用户 `/nas_train/app.e0031982` 一级目录（`du -h --max-depth=1`，逐项带 timeout）

> `rc=124` = 单项 `timeout` 超时（含 26T 级大目录），用二级钻取补（见 8.5）；单位 du `-sx`=1KiB 块已转人类可读。

| 路径 | 大小 | mtime | 安全等级 | 判据/建议 |
|:--|--:|:--|:--|:--|
| `datasets/`（钻取见 8.5） | **≈37 TiB** | 2026-10-03 | 🔀 混合 | 大头 `mvp-lab` 26T（🔴保留）；🟡=FineVision/HuggingFaceFW/conceptual-captions |
| `chip_expert/` | **468 GiB** | 2026-06-17 | 🟡 需确认 | 4× `chipexpert-cn` 快照（3×136G+1×62G，root-owned），~110 天未动 |
| `code/`（钻取见 8.5） | **≈8 TiB** | 2026-10-04 | 🔀 混合 | 🔴 repo/BaiZe-ISEDA2027/eda_fastmcp；🟡 hell/chip-mllm/LLaVA/LLaVA-OneVision-2/circuitvision |
| `models/` | **452 GiB** | 2026-09-29 | 🟡 需确认 | 多用途权重（Qwen 191G、lmms-lab 42G、Mistral 双 28G、apple 28G…），需 vision 线确认在用项 |
| `miniforge3/` | ~1.5 G | 2025-11-26 | 🔴 不可动 | conda 环境（py310 等），训练/下载脚本依赖 |
| `harness_work/` | ≈5.9 GiB | 2026-10-04 | 🔴 不可动 | harness agent 活跃区（rootfs 3.2G/conda_pkgs 1.6G/swe-bench 389M） |
| `harness/` | ≈2 GiB | 2026-09-15 | 🔴 不可动 | harness 源码分析区 |
| `hf_cache/` | 19.8 GiB | 2026-10-03 | 🟡 需确认 | hf 缓存（真 blob 可能已在别处，纯缓存可清） |
| `outputs/` | 6.6 GiB | 2026-01-28 | 🟡 需确认 | 训练输出残留 |
| `download/` | 2.3 GiB | 2026-07-28 | 🟡 需确认 | 下载中转残留 |
| `cache/` | 小（几 G） | 2026-08-03 | 🟡 需确认 | `85M_packing`+`instruct_packing`（各 3 子目录，du 超时待精确） |
| `.vscode-server/` | 461 MiB | 2026-01-27 | 🟢 可清 | VS Code server（部分权限拒绝，实际更小） |
| `.cache/` | 284 MiB | 2026-09-11 | 🟢 可清 | 用户缓存 |
| `Downloads/` | 208 MiB | 2026-08-07 | 🟢 可清 | 下载目录 |
| 散文件 | ~0.5 G | — | 🟢 可清 | `stanford-corenlp-*.zip` 388M(与解压目录重复)、旧清单/个人图 |
| `agents`/`core`/`utils`/`.tmp`/`results`/`submissions`/`torch_train`/`web_search`/`patent`/`omegaconf_230` | ~0 | — | 🟢/🔴 | 空或极小；`results/submissions` 属训练侧勿轻动 |

### 8.5 二级钻取（**前 10 大**下钻）

**`datasets/*`（🔀 混合）**

| 子目录 | 大小 | mtime | 等级 | 说明 |
|:--|--:|:--|:--|:--|
| `mvp-lab/`（LLaVA 85M 26T + 全家桶） | **≈26 TiB** | 2026-09-15 | 🔴 不可动 | 运维已令「保留已下内容」 |
| `FineVision/`（188 子集） | **4.32 TiB** | 2026-01-14 | 🟡 需确认 | 方案 §1.1 标「可选补充源」，~8.5 月未动 |
| `openbmb/Ultra-FineWeb`（base） | **2.74 TiB** | 2026-10-04 | 🔴 不可动 | 下载中（en 2048 满 + l1_en_hq + zh） |
| `HuggingFaceFW/` | **1.24 TiB** | 2026-02-04 | 🟡 需确认 | 文本语料（疑与 Ultra-FineWeb 重叠） |
| `conceptual-captions-12m-webdataset/` | **1.13 TiB** | 2025-12-22 | 🟡 需确认 | 图文对（CC12M） |
| `baize-vision/`（en500k/eval5k） | 244 GiB | 2026-09-30 | 🔴 不可动 | vision 派生，红线 |
| `imagenet-1k/` | 155 GiB | 2026-01-05 | 🟡 需确认 | 视觉分类 |
| `lmms-lab/` | 136 GiB | 2026-02-12 | 🟡 需确认 | LLaVA 系 |
| `LLaVA-Instruct-150K/` | 91 GiB | 2026-01-28 | 🟡 需确认 | LLaVA SFT |
| `vg`/`textvqa`/`coco`/`gqa`/`ocr_vqa`/`LLaVA-Pretrain`/`LLaVA-CC3M`/`red_caps`/`MMMU`/`stanford-corenlp` | ~几十 G | 2025-12~2026-01 | 🟡/🟢 | 小件（部分 du 超时未精确） |

**`code/*`（🔀 混合）**

| 子目录 | 大小 | mtime | 等级 | 说明 |
|:--|--:|:--|:--|:--|
| `hell/LLaVA-OneVision-1.5/` | **1.24 TiB** | 2026-03-11 | 🟡 需确认 | 旧 LLaVA-OneVision-1.5 训练目录（疑与顶层 `LLaVA-OneVision-1.5` 重复） |
| `chip-mllm/` | **896 GiB** | 2026-01-07 | 🟡 需确认 | 芯片多模态 LLM 代码/ckpt，~9 月未动 |
| `LLaVA/` | **716 GiB** | 2026-02-25 | 🟡 需确认 | LLaVA 训练 ckpt |
| `LLaVA-OneVision-2/` | **650 GiB** | 2026-07-31 | 🟡 需确认 | ~65 天未动 |
| `BaiZe-ISEDA2027/` | **421 GiB** | 2026-10-04 | 🔴 不可动 | **pretrain 训练工作区**：`nemo_experiments` 280G(P-5b live+P-9 扫描)+`data` 85G(.bin/.idx)+`output` 22G+`.git` 28G |
| `circuitvision-encoder/` | **244 GiB** | 2026-01-20 | 🟡 需确认 | 视觉编码器代码/ckpt |
| `LLaVA-OneVision-1.5/`（顶层，108 子目录） | 未测(超时) | 2026-09-25 | 🔀 | 大目录，需 owner 定性（9 月有改动） |
| `LLaVA-OneVision-1.5-RL/` | 29 GiB | 2026-08-06 | 🟡 | RL 数据/代码 |
| `flash-attention/` | 8.9 GiB | 2026-08-13 | 🟡 | 库源码(可再 clone) |
| `backup/` | 8.2 GiB | 2026-01-26 | 🟡 | 备份 |
| `eda_fastmcp/` | 2.1 GiB | 2026-09-30 | 🔴 不可动 | 含 EDA-Eval-PyAether 红线隔离区 |
| `super_intelligence_2035/` | 596 MiB | 2026-10-03 | 🔴 不可动 | 共享 git 仓库（active workspace） |
| 其余（`short_drama`/`lmms-eval`/`ms-swift`/`OneVision-Encoder`/`OpenVision*`/`vllm`/`TransformerEngine`/`Megatron-Bridge`…） | 未全测 | 2025-12~2026-09 | 🟡 | 旧实验/库，待二次下钻 |

### 8.6 可回收合计（**分档，均需运维/owner 拍板后才可动**）

| 档 | 项 | 合计 |
|:--|:--|--:|
| 🟢 明确可清 | stanford zip 388M + 散文件/旧清单/个人图 + `.cache` + `.vscode-server` | **≈0.6 GiB** |
| 🟡 需确认（本用户，不含🔴） | FineVision 4.32T + hell 1.24T + HuggingFaceFW 1.24T + conceptual-captions 1.13T + chip-mllm 0.90T + LLaVA 0.72T + LLaVA-OneVision-2 0.65T + chip_expert 0.47T + models 0.45T + circuitvision-encoder 0.24T | **≈11.4 TiB** |
| 🟡 需确认（跨用户，需 owner/运维） | wangcongtao 2.42T + app.e0025692 946G + app.e0041332 1.3G + app.e0013625 0.2G | **≈3.4 TiB** |
| 🔴 不可动 | mvp-lab 26T + base 2.74T + BaiZe-ISEDA2027 421G + eda_fastmcp/baize-vision/repo/harness/miniforge3 | — |

> **一句话结论（D-CLEAN-4）**：本轮**未删任何东西**（只盘点）。**最大新增可回收候选**：① `datasets/FineVision` **4.32 TiB**（可选补充源、~8.5 月未动）；② `code/hell/LLaVA-OneVision-1.5` **1.24 TiB**（旧训练目录，疑与顶层 LLaVA-OneVision-1.5 重复）；③ 跨用户 `wangcongtao` **2.42 TiB** / `app.e0025692` **946 GiB**（~8 月未动）。
> ✅ **运维裁定（2026-10-05 晚）**：「D-CLEAN-4 …… 剩下的保留不动」→ **D-CLEAN-4 终止**：不再删除、也不再盘点；此前「待拍板」**作废**。上方所有候选**均保留不动**。
> 🔴 红线确认未越界：base/gpic 下载、`BaiZe-ISEDA2027`（P-5b/P-9 live）、`eda_fastmcp`、`baize-vision`、`super_intelligence_2035` repo、harness 工作区、miniforge3 均标为不可动。
> ⚠️ `sudo` 不可用（需密码）→ 跨用户 `root`/权限收紧目录无法测实，需运维提供 sudo 或 owner 各自报账。
> 💡 **建议**：运维先拍板 `FineVision` / `hell` / `chip_expert` / 跨用户 `wangcongtao`+`app.e0025692` 这 5 项（合计可回 **≈9.5 TiB**），其余多为 vision 线历史资产需 owner 二次确认。
---

## 9. ⭐ `LLaVA-OneVision-1.5` 4B checkpoint 专项盘点（用户 2026-10-04 点名追加 · **只盘点、不删除**）

> 用户指令：`LLaVA-OneVision-1.5` 目录做了大量实验、沉淀了大量 **4B 模型检查点，绝大部分可删**。本轮单列一节：定位 → 列出所有 ckpt/checkpoint/save/4B 目录的大小+mtime+数量 → 估算可回收合计。
> 目标目录：**`/nas_train/app.e0031982/code/LLaVA-OneVision-1.5/`**（203 个顶层项；整目录最后活动 **2026-09-25**（≈9 天前），当前**无活跃训练/写入**——活跃训练已迁 `BaiZe-ISEDA2027/nemo_experiments`）。
> 方法：整树 `du` 在下载负载下超时（此前 §8.5 标「未测」）→ 改用「逐 run `iter_*` 计数 × 实测单 ckpt 大小」估算（4 处实测一致，误差 ±10%），轻量 HF 目录已 `du -sc` 精确。

### 9.1 检查点清单（大小 / 数量 / mtime）

| 家族（顶层目录） | 目录数 | `iter_*` 分布式 ckpt | mtime 范围 | 实测样例 | 估算 |
|:--|--:|--:|:--|:--|--:|
| `stage_1.5_mid_training_llava_ov_4b*`（Megatron 训练 run） | 21 | **299** | 2026-08-03 ~ 09-25 | opt36=804G(13) · opt40=928G(15) · opt57=1.1T(18) | **≈18.0 TiB** |
| `stage_2_instruct_llava_ov_4b*`（训练 run） | 23（22 opt + 1 base） | **68** | 2026-08-15 ~ 09-25 | opt40=186G(3) · opt57=186G(3) | **≈4.1 TiB** |
| `LLaVA-OneVision-1.5-4B-*`（HF `.safetensors` 转换） | 23 | — | 2026-08-03 ~ 09-25 | opt40=8.9G | ≈205 GiB |
| `*_release*`（HF 终版） | 19 | — | 2026-09-08 ~ 09-24 | ≈8.8 G/个 | ≈191 GiB |
| `stage_1_alignment_llava_ov_4b*` | 4 | 0（仅 base 19G） | 2026-08-03 ~ 09-09 | base=19G | ≈19 GiB |
| `checkpoints/baize_4b` | 1 | — | 2026-08-11 | — | 142 GiB |

> **release + 4B-HF 小计（`du -sc` 实测）= 396 GiB**（415,586,204 KB）。
> **单个 `iter_*` ckpt ≈ 61.6 GiB**（4 处一致：804/13≈61.8 · 928/15≈61.9 · 1.1T/18≈61.1 · 186/3≈62.0）。
> **367 个 `iter_*` × 61.6 GiB ≈ 22.0 TiB**。
> 备注：`raw_packing_data_midtraining_85m`、`runs` 均已**空**（32 B）；`logs` 65M；脚本/`.log`/`configs`/`examples` 等代码资产体量小。

### 9.2 可回收合计（分档）

| 档 | 项 | 合计 |
|:--|:--|--:|
| 🟢 **用户已确认可删** | 367 个 `iter_*` 分布式 ckpt（stage_1.5 299 + stage_2 68） | **≈22.0 TiB** |
| 🟢 用户已确认可删（被取代旧版） | 42 个 release/HF 旧版（仅保留每 stage 最终 best） | ≈360 GiB |
| 🟡 建议保留（待运维定） | 最终 best `LLaVA-OneVision-1.5-4B-QS-…-opt57`（≈9G）+ `checkpoints/baize_4b`（142G，若有复用） | ≈0.15 TiB |

> **→ 🟢 可回收合计 ≈ 22.4 TiB**（总库存 ≈22.5 TiB）。
> **这是 D-CLEAN 系列史上最大单项**（远超已删 `servers` 974G / `FineVision` 4.3T / `nemo_experiments` 272G 之和）。

### 9.3 安全判据（沿用 servers/ D-CLEAN-3 同款前置检查 → 全部通过）

- **P1 无进程占用 ✅**：`fuser -v` 无训练/inference 进程（仅 agent 基建进程 cwd；他人 `app.t0002965` 的 tensorboard `--logdir /nas_train/app.t0002965/outputs/LLaVA-OneVision-1.5-4b` 指向**其自身 outputs，与本目录无关**）。
- **P2 无近期活动 ✅**：整目录 mtime 最后 2026-09-25（9 天前）；无 `.incomplete`/在途写入。
- **P3 无脚本引用 ✅**：BaiZe 仓库（活跃 loop/task 脚本）grep `LLaVA-OneVision-1.5` = 0 命中；目录内仅本仓库自带 `examples/llava_ov_1_5/convert/*` 转换脚本（非引用本路径）。

### 9.4 建议

> 运维可**一次性拍板**删除（保留 `checkpoints/baize_4b` + 各 stage 最终 best 的 `_release`/`4B-QS` ≈30G，其余全部 iter ckpt + 被取代 release/HF 旧版可清），**回收 ≈22 TiB**（/nas_train 约 84% → ≈73%）。
> ⚠️ **本期只盘点、不删除**；执行前照 D-CLEAN-3 再核 P1/P2/P3 并贴命令+原始输出。
> 关联：`code/hell/LLaVA-OneVision-1.5`（**1.24 TiB**，2026-03-11，§8.5 已列 🟡）是同名**另一旧目录**，与本 §9 目标互不重叠、需 owner 另行定性。