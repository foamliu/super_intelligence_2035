# S1→S2 Blend Hot-Switch · 操作速查（给 pretrain 用）

> **版本**：2026-11-27 · **data 交付，pretrain 执行**
> **patch 路径**：`run/data/blendswitch/blend_hotswitch.patch`
> **验证状态**：standalone 8/8 PASS · integration 7/7 PASS · zero_overlap = 0

---

## 1. patch 怎么应用

### 1.1 先备份（铁律）

```bash
# 在 .29 上，先确认 Megatron-LM 代码目录
BAIZE_TRAIN_CODE=/nas_train/app.e0031982/code/super_intelligence_2035/code/Megatron-LM  # ← 按实际路径改
cd "$BAIZE_TRAIN_CODE"
git log -1 --oneline  # 记录当前 commit hash
git stash             # 保存任何未提交改动
```

### 1.2 应用 patch

```bash
cd "$BAIZE_TRAIN_CODE"
# 方式 A（推荐）：git apply
PATCH=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/blend_hotswitch.patch
git apply --check "$PATCH"
git apply      "$PATCH"

# 方式 B（如果 git apply 失败，手动 cp 核心文件）
# patch 改动 7 个文件（6 个修改 + 1 个新建）：
#   megatron/core/datasets/blend_switcher.py         ← 新建
#   megatron/core/datasets/blended_dataset.py         ← 修改
#   megatron/legacy/data/data_samplers.py             ← 修改
#   megatron/training/arguments.py                    ← 修改
#   megatron/training/checkpointing.py                ← 修改
#   megatron/training/training.py                     ← 修改
#   tests/test_blend_hot_switch_integration.py        ← 新建（仅测试）
```

### 1.3 验证 patch 已应用

```bash
ls -la megatron/core/datasets/blend_switcher.py  # 应存在
grep -c 'blend.hot.switch' megatron/training/arguments.py  # 应 ≥ 1
grep -c 'maybe_trigger_blend_switch' megatron/training/training.py  # 应 ≥ 2
```

---

## 2. `--blend-hot-switch` 开关怎么传

### 2.1 新增 3 个命令行参数

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `--blend-hot-switch` | flag (store_true) | `False` | 总开关。**关闭时 = stock 逐字节等价** |
| `--blend-switch-step` | int | `0` | 触发切换的全局训练 step（350000） |
| `--blend-switch-config` | str | `None` | S2 切换配置 JSON 路径 |

### 2.2 在 train.sh 里怎么加

在 `train.sh` 的 `ARGS=(...)` 数组末尾追加：

```bash
ARGS+=( --blend-hot-switch
        --blend-switch-step 350000
        --blend-switch-config /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/s2_blend_switch_config.json )
```

**推荐直接改 train.sh 的 ARGS 数组**，改动量最小且显式。

### 2.3 ⚠️ 不需要改 BLEND_TSV

**S1 blend TSV 保持不变**（`blend_s1_preblend.tsv`）。切换发生在训练循环内部：
- 训练启动时用 S1 blend TSV 构建 BlendedDataset（7 源）
- 到 step 350000 时，`maybe_trigger_blend_switch()` 读取 config JSON，在内存中重建 blend 索引为 S2 配比（12 源）
- **不需要重启训练、不需要换 TSV、不需要 kill 进程**

S2 blend TSV（`blend_s2_preblend.tsv`）仅作为**参考文件**，记录 S2 的完整 12 源配比。

---

## 3. S2 切换配置（config JSON）

**路径**：`run/data/blendswitch/s2_blend_switch_config.json`

关键字段：
- `new_size` = 350,000 步 × 256 GBS = **89,600,000**（S2 阶段总样本数）
- `new_weights`：12 源的目标配比（web=0.40, code=0.40, math=0.20）
- `shared_source_mask`：`true` = S1/S2 共享源（需游标映射），`false` = S2 新源（offset=0）
- `s2_source_keys`：按 key 映射 S2 源 → S1 源（S1=7源 vs S2=12源，顺序不同）

---

## 4. 切换后前 100 步的预期行为

| 指标 | 预期 | 阈值 |
|---|---|---|
| **loss** | 微跳（配比变化），然后平稳回落 | 跳幅 ≤ 5%·100 步内回归趋势线 |
| **每源样本占比** | 立即反映 S2 目标配比 | 偏差 ≤ 1pp（实测 0.0087%） |
| **step time** | 与 S1 基本持平 | 偏差 ≤ 2%（切换是一次性索引重建） |
| **显存** | 无显著增量 | ≤ 5% |
| **LR / optimizer** | 连续，无 re-warmup | stable 段 LR 恒 1e-3 |

日志中应看到：
```
[blend-hot-switch] S1->S2 switch at iteration 350000: consumed_per_source=[...], new_weights=[...], new_size=89600000
```

⚠️ **异常信号**（需立即关注）：
- loss spike > 10% → 可能配比或游标错误
- 某源占比严重偏离目标 → 可能 source_keys 映射错误
- 日志无 `[blend-hot-switch]` 行 → patch 未生效，检查应用状态

---

## 5. 如果出问题怎么回退

### 5.1 快速回退

```bash
# 1. kill 训练进程
# 2. 撤 patch
cd "$BAIZE_TRAIN_CODE"
git checkout -- .
git clean -fd megatron/core/datasets/blend_switcher.py tests/test_blend_hot_switch_integration.py
# 3. 从 348k 或 350k ckpt resume（ckpt 间隔=2000 步）
# 4. s1.env 的 BLEND_TSV 不用改（本来就指向 blend_s1_preblend.tsv）
# 5. 确认 train.sh ARGS 里没有 --blend-hot-switch 等参数
# 6. 重启：bash scripts/train.sh s1
```

### 5.2 回退后影响

- 回退 = 继续 S1 配比训练至 700k（不做 S2 切换）
- 已消耗的 350k 步 S1 数据不浪费
- 零重叠保证不再适用（但 stock 模式不影响已完成训练）

---

## 6. 常见问题预判

**Q: patch 是否与当前训练用的 Megatron 版本兼容？**
A: 兼容。base commit = `14c215dc1472ca75d6f3ce27e423bedfdc51614b`。已验证参数签名一致。应用前确认 `git log -1` 的 hash 一致或在其之后。

**Q: `--blend-hot-switch` 是否需要额外依赖？**
A: 否。纯 Python + numpy（训练环境已有）。无新 pip 包、无 C++ 编译。

**Q: S2 source keys 与 S1 的映射关系？**
A: 见 config JSON 的 `s2_source_keys` + `shared_source_mask`。共享源（7个）按 key 映射（如 S2 的 `code_l2` 位置3 → S1 的 `code_l2` 位置5）。新源（5个）offset=0，天然零重叠。

**Q: checkpoint 里会多存什么？**
A: 切换后 ckpt 多一个 `blend_switch_state` 字段。切换前无此字段（stock 格式）。flag OFF 时不存在。

**Q: 切换是一次性的还是每步都触发？**
A: 一次性。`_blend_switch_done` flag 保证只执行一次。

**Q: S2 阶段 crash 了怎么办？**
A: 当前 patch 版本的 S2 resume 逻辑尚未完整。**建议**：从 350k ckpt 重新开始 S2 阶段。data 线正在完善。

---

## 7. 交付物清单

| 文件 | 路径 | 状态 |
|---|---|---|
| patch 本体 | `run/data/blendswitch/blend_hotswitch.patch` (43,650B) | ✅ |
| 核心逻辑 | `run/data/blendswitch/blend_switcher.py` (17,966B) | ✅ |
| 安装步骤 | `run/data/blendswitch/README_PATCH.md` (10,603B) | ✅ |
| S2 切换配置 | `run/data/blendswitch/s2_blend_switch_config.json` | ✅ |
| 验证脚本 | `run/data/blendswitch/test_blend_switch.py` (14,307B) | ✅ |
| standalone 结果 | `run/data/blendswitch/verify_results.json` | ✅ 8/8 PASS |
| integration 结果 | `run/data/blendswitch/verify_results_integration.json` | ✅ 7/7 PASS |
| S2 blend TSV | `code/baize-llm/configs/blend_s2_preblend.tsv` (3,625B) | ✅ 参考用 |
| **本速查** | `run/data/blendswitch/SWITCH_RUNBOOK.md` | ✅ 本文件 |
