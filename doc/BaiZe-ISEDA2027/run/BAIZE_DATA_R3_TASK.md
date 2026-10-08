# BAIZE_DATA_R3_TASK.md — Round 3 数据配比 BO 搜索（Stable 段 · 6 源 · 100 trial · 全量评测）

> **状态**：方案已定 → 交接给 pretrain 团队落地执行。
> **下游**：pretrain 在 Stage (i) Stable 热身启动 **之前**执行此搜索，结果决定 P-8 的 Stable 段配比。
> **交付物**：`mix_search_eval_r3.db`（最佳 trial + top-K → 全量 lm_eval 验证），以及手给 pretrain 团队的配比推荐（`r3_best_blend.txt` 或 inline 输出）。

---

## 0. 一句话规格

| 项 | 值 |
|:--|:--|
| **搜索阶段** | Stable（proxy d=128/L=14 ≈ 18.36M） |
| **搜索空间** | 6 维单纯形：ultrafineweb_en / ultrafineweb_zh / ultrafineweb_l1_en_hq / UltraX-Preview / UltraData-Code / UltraData-MATH |
| **trial 数** | 100 |
| **D/trial** | 1B token（≈ 30518 步 @ GBS=16, seq=2048） |
| **客观指标** | 全量 8 任务 lm_eval avg accuracy（`arc_challenge` `arc_easy` `boolq` `hellaswag` `openbookqa` `piqa` `sciq` `winogrande`，每任务 acc_norm/acc，无 `--limit`） |
| **GPU** | 8 张 H100（`--gpus 0,1,2,3,4,5,6,7`），每卡单 trial（TP1/DP1） |
| **预算** | **~19.5h ≤ 24h**（含 1h buffer） |
| **前置依赖** | 6 个小样本分词（~30min 并行） |

---

## 1. 为什么需要 Round 3（vs R2）

| 对比项 | R2（已完成） | R3（本次） |
|:--|:--|:--|
| 搜索空间 | 3 维单纯形 `base:code:math` | **6 维**单纯形：`ultrafineweb_en` / `zh` / `l1_en_hq` / `UltraX-Preview` / `UltraData-Code` / `UltraData-MATH` |
| base 粒度 | 已混合的 `mix_base` 24 shard 作为一个源 | **下钻**到 3 个 ultrafineweb 子源（en/zh/l1_en_hq）各独立，再加 UltraX-Preview |
| code/math | `anneal_code`(90M tok) / `anneal_math2`(430M tok) —— FineVision 子集 | **UltraData-Code**(1.22TB) / **UltraData-MATH**(552GB) —— 全量精筛源 |
| 评测 | `--limit 500`（sampled，top-K ρ=−0.80） | **全量** 73106 requests（无 `--limit`，~3.6 分钟/trial） |
| trial 数 | 200 | **100**（预算压缩到 24h） |
| D/trial | 0.5B | **1B**（信噪比更高） |

---

## 2. 预算细账（实测锚点，非估算）

所有耗时数字来自 R2 top-K 全量评测日志 + s_step 归因实验，**可直接信**。

| 操作 | 单 trial 耗时 | 依据 |
|:--|:--|:--|
| **训练**（1B token, MBS=16, GBS=16, seq=2048） | 30518 步 × **166ms** = **5066s ≈ 84.4 min** | s_step 归因实验（MEMORY_DATA.md §⭐），MBS=16 实测 166ms/step |
| **HF 转换**（ckpt → HF config） | ≈ **2 min** | R2 top-K 日志（hf_model mtime vs ckpt mtime） |
| **全量 lm_eval**（8 任务, 73106 loglikelihood req） | ≈ **3.6 min** | topk_t0079 日志：00:22:09 start → 00:26:54 done ≈ 285s |
| **清理**（rm -rf trial dir） | ≈ **0**（后台） | |
| **单 trial 合计** | ≈ **90 min** | 84.4 + 2 + 3.6 + 缓冲 |

| 并行预算 | 计算 |
|:--|:--|
| 100 trials ÷ 8 GPU | = **13 轮**（12 轮满 8 + 末轮 4） |
| 13 轮 × 90 min | = **1170 min = 19.5 h** |
| 含 1h 容错/排队 | ✅ **≤ 24h** |

> 🔴 **不变量**：若 GPU < 8 或 训练变慢，按比例延长——但 **不允许砍 D、不允许切回 `--limit`**。

---

## 3. 数据源全景——6 源原始 parquet 清单

### 3.1 各源位置与列名

| 源 | 磁盘路径 | 列（文本列 → `--mode` 参数） | 总规模 | R3 小样本规模 |
|:--|:--|:--|:--|:--|
| **ultrafineweb_en** | `/nas_train/.../Ultra-FineWeb/data/ultrafineweb_en/` | `content` | 2048 parquet, ~2.66TB | **2 parquet** → ~500M tok |
| **ultrafineweb_zh** | `/nas_train/.../Ultra-FineWeb/data/ultrafineweb_zh/` | `content` | 256 parquet, ~324GB | **1 parquet** → ~500M tok |
| **ultrafineweb_l1_en_hq** | `/nas_train/.../Ultra-FineWeb/data/ultrafineweb_l1_en_hq/` | `content` | 6006 parquet, ~478GB | **2 parquet** → ~500M tok |
| **UltraX-Preview** | `/nas_train/.../openbmb/UltraX-Preview/data/UltraX-FineWeb/` | `cleaned_content` | 104 parquet/en, 454G 总 | **2 parquet** → ~300M tok |
| **UltraData-Code** | `/nas_inference/.../openbmb/UltraData-Code/data/UltraData-Code-L3/`（子目录按语言：cpp/py/js/...） | `content` | L3 11 语言，~1.22TB 总 | **2 parquet（跨语言）** → ~500M tok |
| **UltraData-MATH** | `/nas_inference/.../openbmb/UltraData-Math/data/UltraData-Math-L1/CC-MAIN-*/` | `content` | L1 15 CC-MAIN shards, ~552GB | **2 parquet** → ~500M tok |

### 3.2 小样本分词——唯一前置，~30 分钟

对 R3 的 100 trial（共 100B token 消耗）而言，**不需要等全量分词**。只需要给每个源取 2 个 parquet 文件，tokenize 成 6 个独立的 `.bin/.idx` 对。

**复用现有 tokenize 脚本模式**（三者已经验证可用）：
- `baize_mix_tokenize_base.sh`（ultrafineweb_en → mix_base shard）
- `baize_tokenize_zh.sh`（ultrafineweb_zh → mix_base shard）
- `baize_tokenize_l1_en_hq_parallel.sh`（ultrafineweb_l1_en_hq → mix_base shard）

**新增 `baize_tokenize_r3_sources.sh`**（可直接基于上述脚本改）：
- INPUT: 每源 2 个 parquet, symlink 到 `$WORK/r3_{source_name}/` 下
- CMD: `preprocess_data.py --input-dir $WORK/r3_{name} --output-prefix data/r3_sources/r3_{name} --tokenizer $TOKENIZER --tokenizer-output-dir /tmp/r3_tok_{name} --mode {content|cleaned_content} --dtype int32`
- OUTPUT: `data/r3_sources/r3_ultrafineweb_en.bin/.idx/ .json`, `r3_ultrafineweb_zh.*`, `r3_ultrafineweb_l1_en_hq.*`, `r3_ultrax_preview.*`, `r3_ultradata_code.*`, `r3_ultradata_math.*`
- 6 进程并行（每个源独立进程）
- 大小: 每个 .bin ~1.5–2.5 GiB（~500M tok）

> ⚠️ **UltraX-Preview** 文本列名是 `cleaned_content`（非 `content`），tokenize 时 `--mode cleaned_content`。其他 5 源均为 `--mode content`。

> ⚠️ **UltraData-Code** 的 parquet 在 `<language>/` 子目录下，symlink 时需 `find` 收集。

> 总用时估算：6 个小型 tok job 并行 → 约 **30 分钟**（实测 500M tok 分词约 15–20 min/进程，6 进程并行受 I/O 带宽限制，不会线性加速，但实测 30 min 足够）。

---

## 4. R3 搜索空间设计

### 4.1 6 维单纯形

```
dims = [
  "ultrafineweb_en",       # 范围 [0.01, 0.50]
  "ultrafineweb_zh",       # 范围 [0.01, 0.40]
  "ultrafineweb_l1_en_hq", # 范围 [0.01, 0.40]
  "ultrax_preview",        # 范围 [0.01, 0.30]
  "ultradata_code",        # 范围 [0.01, 0.20]
  "ultradata_math",        # 范围 [0.01, 0.10]
]
约束: sum(dims) == 1.0
```

各维上下界的含义：
- **ultrafineweb_en**: web 英文主体，预期最优 30–50%
- **ultrafineweb_zh**: web 中文主体，预期 10–30%
- **ultrafineweb_l1_en_hq**: web 英文高质量（L1 = 高质量筛选），预期 5–20%
- **ultrax_preview**: MiniCPM5 新增精筛 web（与以上同族但非完全重叠），预期 5–20%
- **ultradata_code**: 精筛代码，预期 3–15%（参考 R2 最优区 code 6–12%）
- **ultradata_math**: 精筛数学，预期 1–8%（参考 R2 最优区 math≈1–4%）

### 4.2 为什么不分层（直接 6 维搜）

100 trial 对 5 自由度（6−1 = 5），**每自由度 20 个 trial**，对 BO（Gaussian Process / TPE）而言足以找到粗粒度最优区域。分层搜索（先搜 web:code:math，再下钻 web 内部）的代价是引入离散假设分支、且各层试验数被摊薄——不必要。**直接 6 维单纯形，100 trial 足够。**

---

## 5. 代码改动——基于 `baize_mix_optuna_r2.py`

> ⚠️ 前置确认：以下**所有行号以 R2 脚本当前版本为准**，改造前先对照实际文件核对；本表给出的是相对稳定的锚点。

### 5.1 改动清单

| # | 改动点 | 说明 |
|:--|:--|:--|
| 1 | 复制 `baize_mix_optuna_r2.py` → `baize_mix_optuna_r3.py` | 全局替换 R2→R3 命名，改 DB 后缀 |
| 2 | 顶部常量 | `D_TOKENS=1_000_000_000`, `N_TRIALS=100`, `EVAL_LIMIT=None` |
| 3 | `SPACES["stable"]` 的 `dims` / `bounds` / `data_paths` | 替换为 6 源（§5.2） |
| 4 | `build_blend_stable()` | 改为 6 源加权 blend string（§5.3） |
| 5 | lm_eval 命令行 | 去掉 `--limit`（§5.4） |
| 6 | DB 路径 | `mix_search_eval_r3.db` |
| 7 | lm_eval timeout | 从 1800s → 3600s（全量余量） |

### 5.2 新的 SPACES 定义

```python
SPACES = {
    "stable": {
        "dims": ["ultrafineweb_en", "ultrafineweb_zh", "ultrafineweb_l1_en_hq",
                  "ultrax_preview", "ultradata_code", "ultradata_math"],
        "bounds": [(0.01, 0.50), (0.01, 0.40), (0.01, 0.40),
                   (0.01, 0.30), (0.01, 0.20), (0.01, 0.10)],
        "data_paths": {
            "ultrafineweb_en":       f"{DATA}/r3_sources/r3_ultrafineweb_en",
            "ultrafineweb_zh":       f"{DATA}/r3_sources/r3_ultrafineweb_zh",
            "ultrafineweb_l1_en_hq": f"{DATA}/r3_sources/r3_ultrafineweb_l1_en_hq",
            "ultrax_preview":        f"{DATA}/r3_sources/r3_ultrax_preview",
            "ultradata_code":        f"{DATA}/r3_sources/r3_ultradata_code",
            "ultradata_math":        f"{DATA}/r3_sources/r3_ultradata_math",
        },
    },
    # decay 段保持 R2 原样（本轮不动）
}
```

### 5.3 新的 `build_blend_stable()`

```python
def build_blend_stable(en, zh, l1, ultrax, code, math):
    total = en + zh + l1 + ultrax + code + math
    if abs(total - 1.0) > 1e-4:
        zh = max(zh + 1.0 - total, 0.01)
    en = max(1.0 - zh - l1 - ultrax - code - math, 0.01)
    sp = SPACES["stable"]["data_paths"]
    return (f"{en:.6f} {sp['ultrafineweb_en']} "
            f"{zh:.6f} {sp['ultrafineweb_zh']} "
            f"{l1:.6f} {sp['ultrafineweb_l1_en_hq']} "
            f"{ultrax:.6f} {sp['ultrax_preview']} "
            f"{code:.6f} {sp['ultradata_code']} "
            f"{math:.6f} {sp['ultradata_math']}")
```

---

## 6. 执行顺序（交接给 pretrain）

```
Step 0  备份 R2 脚本 → 改出 baize_mix_optuna_r3.py（§5）
Step 1  跑 baize_tokenize_r3_sources.sh（6 源小样本分词, ~30 min）
Step 2  python baize_mix_optuna_r3.py --phase stable --n-trials 100 \
            --gpus 0,1,2,3,4,5,6,7        # ~19.5h
Step 3  等 100 trial 完成（含第 13 轮最后的 4-trial 收尾）
Step 4  top-K（K≥5）不同 seed 全量验证，确认泛化
Step 5  输出 r3_best_blend.txt → 交 Stage (i) Stable 热身
```

> 收尾 guard：末轮不足 8 trial 时，`--gpus` 改传实际空闲卡号即可；DB 会正确推进，不会因缺卡卡死。

---

## 7. 风险与缓解

| 风险 | 概率 | 缓解 |
|:--|:--|:--|
| 小样本 bin 不代表全量源分布 | 低 | 每源取 2 parquet（非 1）跨 shard 覆盖面足够；top-K 仍用全量验证 |
| UltraX 与 ultrafineweb_en 重叠 → identifiability 差 | 中 | 观察 GP 后验方差，若某维方差始终大 → 该维无信号，后处理固定降维 |
| 6 维 BO 收敛到局部最优 | 中 | GP Matern(2.5) kernel + `--n-random 12` + n_startup_trials=15 提升覆盖 |
| 24h 不足（trial 失败率高） | 低 | 19.5h 基线 + 1h buffer = 20.5h，空余 3.5h；若超时优先**减少 n_random 而不减总 trial**，或扩卡到 24 卡 |
| UltraData-Code 子目录 grab 漏文件 | 低 | 用 `find` 收集 symlink，勿用 `glob` 平铺 |

---

## 8. 交付协议（给 pretrain 的明确边界）

- **本轮负责人（data）**：方案定型 + 此文档 + 数据活性核查（已完成）。
- **pretrain 负责**：§5 代码改造、§3.2 小样本分词脚本落地、§6 执行、top-K 验证与配比推荐输出。
- **时间不变量**：8 卡 / ~19.5h（≤24h），不可砍 D、不可加 `--limit`。
- **完成信号**：`r3_best_blend.txt` 生成 + `mix_search_eval_r3.db` 存在，Stable 热身引用之。

---

## A. 附录：引用路径摘要

| 资源 | 路径 |
|:--|:--|
| **R2 脚本（basis）** | `/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_optuna_r2.py` |
| **R2 DB（参考结构）** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/mix_search/mix_search_eval_r2.db` |
| **Ultra-FineWeb base** | `/nas_train/app.e0031982/datasets/openbmb/Ultra-FineWeb/data/` |
| **UltraX-Preview** | `/nas_train/app.e0031982/datasets/openbmb/UltraX-Preview/data/` |
| **UltraData-Code L3** | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Code/data/UltraData-Code-L3/` |
| **UltraData-Math L1** | `/nas_inference/app.e0031982/datasets/openbmb/UltraData-Math/data/UltraData-Math-L1/CC-MAIN-*/` |
| **tokenize 参考脚本** | `/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_mix_tokenize_base.sh` |
| **preprocess_data.py** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/mamba2_hybrid_2b/preprocess_data.py` |
| **分词器** | `/nas_train/app.e0031982/models/DeepSeek-V4.1-Flash` |
| **工作区 BASE** | `/nas_train/app.e0031982/code/BaiZe-ISEDA2027` |
| **R3 数据输出目录（需创建）** | `{BASE}/data/r3_sources/` |

---

*文档：data agent · 2026-10-08 · R2→R3 改造规格 v1.0*