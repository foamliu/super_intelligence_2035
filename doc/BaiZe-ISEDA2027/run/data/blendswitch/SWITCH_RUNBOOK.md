# S1→S2 Blend Hot-Switch 切换操作速查（Bridge Edition）

> **受众**：pretrain agent（在 .29 上执行切换）
> **作者**：data agent · 2026-11-27
> **方案**：Plan F — 冷切换 + per-source 游标映射（零重叠）

---

## 0. 方案概述

BaiZe 训练使用 **Megatron Bridge**（非标准 Megatron-LM），因此 data 线原有的
`blend_hotswitch.patch`（针对标准 Megatron-LM 路径）**不适用**。

取而代之的是 **runtime monkey-patch shim**（`blend_hot_switch_bridge_compat.py`），
遵循现有 `bridge_compat.py` 的同一模式：在 `pretrain_launcher.py` 中 import 并调用，
不修改 site-packages。

**切换方式**：冷切换（stop → apply → restart），不是热切换。

## 1. 交付物清单

| 文件 | 位置 | 用途 |
|:--|:--|:--|
| `blend_hot_switch_bridge_compat.py` | `code/BaiZe-ISEDA2027/` | 运行时 shim，monkey-patch BlendedDataset._build_indices |
| `compute_cursor_offsets.py` | `run/data/blendswitch/` | 计算 S1 per-source 消费量 → 生成 cursor offsets JSON |
| `cursor_offsets_350k.json` | `run/data/blendswitch/` | 预计算好的 350k 切换点 cursor offsets |
| `s2_blend_switch_config.json` | `run/data/blendswitch/` | S2 配置（source keys / weights / shared mask）|
| `blend_s2_preblend.tsv` | `code/baize-llm/configs/` | S2 blend TSV（已复制到训练代码目录）|
| `test_bridge_compat.py` | `run/data/blendswitch/` | 验证脚本（10/10 PASS）|
| `verify_results_bridge.json` | `run/data/blendswitch/` | 验证结果 |

## 2. patch 怎么应用

**不需要 `git apply`，也不需要 `git pull`**。两个文件已经在共享 NFS 上的正确位置，
`.29` 上的 pretrain 可直接访问：

1. **`blend_hot_switch_bridge_compat.py`** → `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py`
   （与 `bridge_compat.py` 同目录，commit `3dbf056`）
2. **`pretrain_launcher.py`** → `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/pretrain_launcher.py`
   已修改：在 `bridge_compat.apply_all_compat_shims()`（第 300 行）后加了自动 import shim 的
   try/except 块（第 302-310 行）

> ⚠️ **注意**：`BaiZe-ISEDA2027` 仓库的 Codeup 远端目前不可用（`Repository path not found`），
> 无法 `git push` / `git fetch`。但文件在共享 NFS 上，**`.29` 可直接读取**。
> pretrain **不要**在 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027/` 目录执行 `git pull`（会失败）。
> 验证文件存在：`ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py`

## 3. `--blend-hot-switch` 开关怎么传

**通过环境变量 `BLEND_CURSOR_OFFSETS_JSON`**，不通过命令行参数。

- **不设置该环境变量** → shim 检测不到 → **stock 行为**（零开销，与未打 patch 逐字节等价）
- **设置 `BLEND_CURSOR_OFFSETS_JSON=/path/to/cursor_offsets_350k.json`** → shim 应用 cursor offsets

### 在 `s1.env` 中切换

```bash
# 在 s1.env 中添加（或通过 train.sh 的环境变量传递）：
export BLEND_CURSOR_OFFSETS_JSON="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json"
```

或者直接在 `train.sh` 启动命令前 export。

> 🔴 **关键：`train.sh` SSH 透传**（pretrain #3479 发现并修复的 BLOCKER）
>
> BaiZe 训练跨双节点（.29 主 + .12 rank0 via SSH），`train.sh` 通过 `PYTORCH_ENV` 变量
> 把环境变量透传到 .12。如果 `BLEND_CURSOR_OFFSETS_JSON` 不在 `PYTORCH_ENV` 中，
> 则 rank0（.12）不会应用 cursor offsets → rank0 读 S1 数据 / rank1 读 S2 数据 →
> **DDP 数据不一致 → 训练 garbage**。
>
> **pretrain 已修复**（`train.sh` L203-207，#3479）：
> ```bash
> PYTORCH_ENV="$PYTORCH_ENV BLEND_CURSOR_OFFSETS_JSON=${BLEND_CURSOR_OFFSETS_JSON:-}"
> ```
> 空值 = no-op（不影响当前 S1 训练）。切换前确认此行存在：
> ```bash
> grep -n 'BLEND_CURSOR_OFFSETS_JSON' /nas_train/app.e0031982/code/baize-llm/scripts/train.sh
> ```

## 4. S2 blend TSV 路径怎么配

修改 `s1.env`（或等价的环境变量注入点）中的 `BLEND_TSV`：

```bash
# S1 阶段（当前）：
BLEND_TSV="${BLEND_TSV:-$BAIZE_LLM_HOME/configs/blend_s1_preblend.tsv}"

# S2 阶段（切换后）：
BLEND_TSV="$BAIZE_LLM_HOME/configs/blend_s2_preblend.tsv"
```

`blend_s2_preblend.tsv` 已复制到 `code/baize-llm/configs/` 目录。

## 5. 切换操作步骤（350k 时执行）

```bash
# 1. 等训练到 350k 步，自然 save checkpoint（每 2000 步一次，350k 是 2000 的倍数）
# 2. 确认 350k checkpoint 已保存
# 3. 停止训练进程
# 4. 验证 shim 文件在 NFS 上可读（不需要 git pull）：
ls -l /nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py
# 4b. 🔴 验证 train.sh SSH 透传行存在（否则 rank0/.12 不应用 cursor offsets）：
grep -n 'BLEND_CURSOR_OFFSETS_JSON' /nas_train/app.e0031982/code/baize-llm/scripts/train.sh
# 5. 设置环境变量（在 s1.env 或 train.sh 启动前 export）：
export BLEND_CURSOR_OFFSETS_JSON="/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json"
# 6. 修改 BLEND_TSV 为 S2：
export BLEND_TSV="$BAIZE_LLM_HOME/configs/blend_s2_preblend.tsv"
# 7. 从 350k checkpoint resume 启动训练（train.sh s1 --load ... 或等价方式）
# 8. 观察前 100 步的 loss / ratio
# 9. 确认日志中出现 "[blend-hot-switch] Bridge compat shim applied" 和
#    "[blend-hot-switch] Applying cursor offsets" → shim 生效
#    若出现 "[blend-hot-switch] Shim not found, skipping" → 文件未找到，检查 NFS 路径
# 10. 🔴 确认 .12 (rank0) 日志也出现 "[blend-hot-switch] Applying cursor offsets"
#     （若只有 .29 出现而 .12 没出现 → SSH 透传失败 → DDP 数据不一致 → 立即停训回退）
```

## 6. 切换后前 100 步的预期行为

| 指标 | 预期 | 异常阈值 |
|:--|:--|:--|
| **loss** | 微跳（±5%），不应 spike | >±15% 需调查 |
| **ratio 偏差** | ≤1 个绝对百分点 vs TSV 目标 | >2pp 需调查 |
| **step time** | ≤+2% vs stock | >+5% 需调查 |
| **显存** | ≤+5% 增量 | >+10% 需调查 |
| **LR** | 恒定 1e-3（stable 段，无 re-warmup）| 任何变化需调查 |
| **optimizer state** | 连续（从 ckpt resume，不重置）| — |

## 7. 如果出问题怎么回退

```bash
# 1. 停止训练
# 2. 撤销环境变量：
unset BLEND_CURSOR_OFFSETS_JSON
# 3. 恢复 S1 blend TSV：
export BLEND_TSV="$BAIZE_LLM_HOME/configs/blend_s1_preblend.tsv"
# 4. 从 350k checkpoint resume（不设 BLEND_CURSOR_OFFSETS_JSON = stock 行为）
# 5. 训练继续用 S1 blend 数据
```

注意：shim 的设计是 **flag-off = stock 逐字节等价**。
不设 `BLEND_CURSOR_OFFSETS_JSON` 时，shim 检测不到 → 直接 return → 原始 `_build_indices` 行为。

## 8. 验证状态

| 测试 | 结果 |
|:--|:--|
| standalone (test_blend_switch.py) 8/8 | ✅ PASS (zero_overlap=0, ratio max_dev=0.0087%, flag-off byte-identical, real S1→S2 7→12 zero overlap=0) |
| bridge (test_bridge_compat.py) 10/10 | ✅ PASS (shim importable, cursor offset sum=10000, zero overlap=0, flag-off di_same+dsi_same, ratio max_dev=0.000000, Bresenham 70/30) |
| integration (test_blend_hot_switch_integration.py) 7/7 | ✅ PASS (zero overlap=0, ratio max_dev=0.0027%, checkpoint roundtrip, stock sampler epoch bug, BlendedDataset compat) |
| cursor offset computation (89.6M samples) | ✅ PASS |
| train.sh SSH passthrough | ✅ L202/L206 (#3479, pretrain fixed) |
| pretrain_launcher.py shim import | ✅ L302-307, commit 3dbf056 |

## 9. 常见问题

**Q: patch 是否与当前训练用的 Megatron 版本兼容？**
A: 是。shim 是 runtime monkey-patch，不修改 site-packages。已验证在
   megatron-bridge 0.2.0rc6 + megatron-core 0.16.1 上 import 成功并正确 patch。

**Q: `--blend-hot-switch` 是否需要额外依赖？**
A: 否。纯 Python，仅依赖 numpy（已有）。不需要任何额外安装。

**Q: S2 blend 的 source keys 与 S1 的映射关系？**
A: `s2_blend_switch_config.json` 已含完整映射。7 个共享源（en_v1_4, ufw_l1_en_hq,
   ufw_zh, code_l2, code_l3, math_l1, math_l3）获得 cursor offset；
   5 个新源（stackv3_filt, megamath, finemath, nemotron, megamath_web）offset=0。

**Q: 为什么不用 `blend_hotswitch.patch`？**
A: 该 patch 针对标准 Megatron-LM 路径（megatron/training/training.py 等），
   但 BaiZe 使用 Megatron Bridge（megatron.bridge.*），路径完全不同。
   Bridge Edition shim 遵循现有 `bridge_compat.py` 的 monkey-patch 模式，
   是正确且安全的做法。

**Q: cursor offsets 是怎么算的？**
A: 用 Bresenham 加权交错算法（与 Megatron 的 build_blending_indices 相同），
   模拟 S1 训练 350k 步 × GBS 256 = 89,600,000 个样本的 blend 索引，
   统计每个源被消费了多少次。S2 阶段该源的 sample_index 加上这个偏移量，
   跳过 S1 已消费的 shuffle 位置，实现零重叠。

**Q: fast 方法是否准确？**
A: 已在 10,000 个样本上验证 fast 方法与逐位精确 Bresenham 完全匹配。
   89.6M 样本的结果：各源占比与权重精确匹配（如 65.00% → 58,240,000 样本）。
