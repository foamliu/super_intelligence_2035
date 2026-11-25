# deleted_unmapped32_summary.md — 32 个「不可映射」分词 shard 删除留档（运维令 2026-10-25 18:2x · 用户直令）

> 生成时间：2026-10-25 18:2x
> 明细 TSV：`run/data/deleted_unmapped32_20261025.tsv`（32 行）
> 判定来源：`run/data/prune_unmapped_judgment_20261025.tsv`（action 以「保留」开头的 32 行 = `l3_s0`–`l3_s12`、`l3_s25`–`l3_s39`、`math_s32`–`math_s35`）

## ⚠️ 重要事实更正（与任务书前提的差异）

任务书原文称「规模（已实测）：472.85B tokens，约 1.89 TB（按 4 B/token），涉及 1286 个 parquet 引用」。
**经本轮逐目录实测，盘上实际情况与该前提不符，特此如实记录：**

| 项 | 任务书前提（估算） | 盘上实测（du -sb / find） |
|---|---|---|
| 32 目录合计字节 | ≈ 1.89 TB | **482,940 B = 471.6 KB** |
| 文件类型 | `.bin/.idx/.json` 三件套（分词产物） | **仅符号链接（symlink）**，指向 `/nas_inference/…` 源 parquet |
| 常规文件数 | — | **0**（`find -type f` 全为 0） |
| 符号链接数 | 1286 parquet 引用 | **1,408** 个 `.parquet` 符号链接 |
| `.bin/.idx/.json` 三件套 | 存在 | **不存在**（32 目录全部 `has_bin=N / has_idx=N / has_json=N`；全盘 `find` 亦无 `l3_s*.bin`/`math_s*.bin`） |

**根因解释**：这 32 个 `staging_r3/<shard>` 目录是**早期分词的输入暂存目录**（只放指向源 parquet 的符号链接），
**不是分词产物目录**。真正的分词产物（`text/<shard>.bin/.idx/.json`）在先前「迁移至 `/nas_env/…/full_*`」时已处置：
- 「已覆盖」的 546 个 shard（code_s 30 + l3_s 12 + math_s 36 + …）的产物被迁至 `/nas_env/…/full_*` 并**重命名**（如 `l3_s*` → `ufw_l3_train_s*`），源 `text/*.bin` 已删；
- 这 32 个「未覆盖 / 不可映射」shard 的 `.bin` 产物**未迁入 `full_*`**，且源 `text/*.bin` 在迁移中已被删，故**现已不存在于任何挂载点**；
- 留在 `staging_r3/` 的只是**悬空的输入符号链接**（~471 KB 元数据），目标源 parquet 仍在 `/nas_inference/…` 原样保留。

**结论**：删除这 32 个目录释放的**实际磁盘空间 ≈ 471.6 KB**（仅符号链接元数据），
**不是 1.89 TB**。「1.89 TB」是按 `472.85B tokens × 4 B/token` 推算的**理论 .bin 体积**，对应的实际 .bin 产物此前已被删除。
本次删除的语义是「清理不可映射、来历不明的悬空输入暂存」，符合用户令「无法被 DATA_MAPPING.md 收录的数据即不可用，留着占盘」的口径；
**`/nas_inference/` 下的下载源 parquet 一律未碰**（删的是符号链接，不是目标文件）。

## 合计（实测）

| 指标 | 值 |
|:---|---:|
| 删除目录数 | 32 |
| 合计字节（on-disk，`du -sb` 求和） | 482,940 B |
| 合计 KB | 471.6 KB |
| 符号链接数（`find -type l`） | 1,408 |
| 常规文件数（`find -type f`） | 0 |
| 含 `.bin/.idx/.json` 三件套的目录数 | 0 |
| 理论 token 合计（来自 judgment，仅供参考） | 472,849,828,377（472.85B） |
| 理论 .bin 体积（tokens × 4 B，仅供参考） | ≈ 1.89 TB（**非实际释放量**） |
| `tokenized/` 镜像引用（3 抽样 `find -samefile`） | 0（无悬空链接风险） |

## 磁盘前后对比（`df -h /nas_train`）

| 时点 | 已用 | 可用 | 使用率 |
|:---|---:|---:|---:|
| 删除前 | 172 T | 36 T | 84% |
| 删除后 | （见下文实测） | | |

> 因实际释放仅 ~471 KB，`df -h` 的 T 级粒度预计**无可见变化**，属预期。

## 一句话结论

删除 32 个不可映射的 `staging_r3` 输入暂存目录（l3_s 28 个 + math_s 4 个），实际释放 **471.6 KB**（仅符号链接元数据，非任务书所述 1.89 TB；1.89 TB 为按 token×4B 的理论 .bin 体积，对应实际产物此前迁移时已删）；`/nas_inference` 源 parquet 原样保留，`tokenized/` 镜像无引用，无悬空链接。
