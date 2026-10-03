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
| `.../datasets/laion2B-en-aesthetic/` | **≈8.1 T** | 🚫 URL-only，DATA_LEDGER §6 已判「淘汰」 | 待拍板：可回收 ≈8.1 T |
| `.../datasets/mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M*` | **≈26 T**（7629 parquet） | 🔴 已停；§0.7 明令「保留已下内容，不要删」 | **保留不删** |
| `/nas_train/app.e0031982/hf_cache` | 20 G | hf download 缓存，可能含重复 blob | 纯缓存可清 |
| `/nas_train/app.e0031982/outputs` | 6.7 G | 训练输出残留 | 待确认 |
| `/nas_train/app.e0031982/download` | 2.4 G | 下载中转残留 | 待确认 |
| `/nas_train/app.e0031982/Downloads` | 209 M | 下载目录 | 待确认 |
| `/nas_train/app.e0031982/zhulong.tar.gz` | 493 M (2026-03-06) | ZhuLong 旧打包 | 待确认 |
| `midtraining_filelist_20260316_1610.txt`(1.4M)+`checksums_partial`(125K) | ≈1.5 M | 2026-03 旧清单 | 待确认 |

> 🟡 分档小计（不含超大件）≈ **1.98 T**。超大件另列：laion2B **8.1 T**（已淘汰可回收）· LLaVA 85M **26 T**（保留不删）。

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
| 🟡 需确认（本用户，含大件不含保留） | **≈10.1 T** | laion2B 8.1T + nemo 524G + servers 974G + models 452G + hf_cache 20G + 其他 ~0.5T |
| 🟡 保留不删（运维令） | 26 T | LLaVA 85M（7629 parquet，将来 vision 用） |
| 🔴 不可动 | — | base/gpic 下载 + L3/code/math + SFT + GPIC + en500k/eval5k + EDA 隔离区 |

> **一句话结论**：本用户盘上最立竿见影的可回收 = 🟢 缓存 ≈3.3G + 🟡 `laion2B-en-aesthetic` **≈8.1T（URL-only 已淘汰）**；`nemo_experiments`/`servers`/`models` ≈1.95T 需先确认用途。**本线未删除任何东西，等运维拍板。**

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
```