# S2 切换 E2BIG 诊断与解法（Argument list too long）

> **作者**：data agent · 2026-11-28
> **事件**：RUN_ID 293 S2 冷切换启动失败（08:06:45）
> **错误**：`torchrun: Argument list too long` (errno=E2BIG)
> **状态**：🔴 阻塞 S2 切换 · S1 已停 · 16 卡全空 · 350k ckpt 完好

---

## 1. 根因

### 1.1 直接原因

`train.sh` 把 `gen_blend.py` 输出的 **blend 字符串**（weight+path 对）通过
`--train-data-path "$BLEND"` 作为**单个命令行参数**传给 `torchrun` → `pretrain_launcher.py`。

S2 blend 有 **13,847 个 shard**，展开后的字符串约 **2.64 MB**，超过 Linux 内核两个硬限制：

| 限制 | 值 | 说明 |
|:--|--:|:--|
| `MAX_ARG_STRLEN` | 128 KB | 单个参数字符串最大长度（`32 × PAGE_SIZE`，x86_64 编译期常量，**不可运行时修改**） |
| `ARG_MAX` | 2 MB | argv + envp 总大小上限（`getconf ARG_MAX` = 2,097,152） |

→ bash exec `torchrun` 时内核返回 `E2BIG` → `Argument list too long`。

### 1.2 为什么 S1 没问题

| | S1 | S2 |
|:--|:--|:--|
| 源数 | 7 | 12 |
| shard 总数 | ~100（pre-blend × 16） | **13,847** |
| BLEND 字符串大小 | ~20 KB ✅ | **~2.64 MB** ❌ |

S1 的 7 个源全部使用 pre-blend（每个源 16 个大 shard）。S2 新增了 5 个**未 pre-blend** 的源：

| 源 | shard 数 | 是否 pre-blend | .bin 总量 |
|:--|--:|:--|:--|
| stackv3_filt | **8,192** | ❌ 否 | 1.8 TB |
| megamath_web | **4,950** | ❌ 否 | 813 GB |
| megamath | **348** | ❌ 否（pre-blend 目录下是 symlink，未合并） | symlink |
| nemotron | **193** | ❌ 否 | ~78 GB |
| finemath | **64** | ❌ 否 | ~3.8 GB |
| **小计** | **13,747** | | |
| 其余 7 源 | 100 | ✅ pre-blend | — |
| **合计** | **13,847** | | |

### 1.3 代码路径

```
gen_blend.py → BLEND 变量（13,847 × 2 个空格分隔的 token）
  → train.sh L101: ARGS=( ... --train-data-path "$BLEND" ... )
    → train.sh L282: "$PY/torchrun" ... pretrain_launcher.py "${ARGS[@]}"
      → 内核 exec: argv[某元素] = 2.64MB > MAX_ARG_STRLEN(128KB)
        → E2BIG → "Argument list too long"
```

---

## 2. 解法对比

### 方案 A：BLEND 写文件（最快 · ~15 分钟改 2 个文件）

**原理**：把 BLEND 字符串写到 NFS 上的文件，命令行只传文件路径（`@filepath`），
`pretrain_launcher.py` 检测 `@` 前缀并从文件读取。

**改动**：
1. `train.sh`：写 BLEND 到 `/nas_train/.../BaiZe-ISEDA2027/blend_runtime.txt`，
   ARGS 中改为 `--train-data-path "@$BLEND_FILE"`
2. `pretrain_launcher.py`：在 normalize 逻辑中加 `@` 文件读取

**优点**：
- 改动极小（2 文件 × ~10 行）
- **不需任何数据处理**
- NFS 文件双节点 (.29/.12) 均可读
- flag-off = stock 行为（BLEND 小时走原路径，大时走文件）

**缺点**：
- 需改 pretrain 代码（但改动极小且有明确边界）

**补丁**：见 `fix_arg_too_long.patch`

### 方案 B：Pre-blend 大源（更优 · ~2-6h 数据处理）

**原理**：用 `pre_blend.py` 把 5 个未 pre-blend 的源各合并为 16 个大 shard，
shard 总数从 13,847 降到 ~192 → BLEND ~40KB → 远低于限制。

**操作**：
```bash
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
# stackv3_filt (8192→16, 1.8TB, 预计 ~2-4h)
$PY /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/pre_blend.py \
    --src-dir /nas_user/app.e0031982/datasets/baize-data/tokenized/HuggingFaceCode/stack-v3-train \
    --out-dir /nas_user/app.e0031982/datasets/pre-blend/stackv3_filt \
    --prefix stackv3_filt --target-shards 16 --verify
# megamath_web (4950→16, 813GB, 预计 ~1-2h)
$PY .../pre_blend.py --src-dir .../megamath-web --out-dir .../pre-blend/megamath_web --prefix megamath_web --target-shards 16 --verify
# nemotron (193→16), finemath (64→16), megamath (348→16) — 各 <30min
```
然后更新 `blend_s2_preblend.tsv` 把 5 个源的路径改为 pre-blend 目录。

**优点**：
- S1 已验证的方法
- 减少 mmap 文件数 → DataLoader fork-COW 开销降低 → 训练吞吐更好
- 不需改代码

**缺点**：
- stackv3_filt 1.8TB → pre-blend 耗时 ~2-4h（NFS I/O 瓶颈）
- 需更新 TSV + 重新验证 blend 生成
- cursor_offsets_350k.json **不需要重算**（新源 offset=0，共享源已用 pre-blend）

### 方案 C：A + B 组合（推荐）

1. **立即**：应用方案 A 补丁 → 解除 E2BIG 阻塞 → S2 可启动
2. **后台并行**：跑方案 B pre-blend → 后续 checkpoint resume 时切换到 pre-blend TSV

---

## 3. 推荐执行路径

```
[现在] S1 已停 · 16 卡空 · 350k ckpt 完好
  ↓
[Step 1] pretrain 审查并应用 fix_arg_too_long.patch（~15 min）
  ↓
[Step 2] 验证：DRY=1 bash train.sh s1（确认 ARGS 不含大字符串）
  ↓
[Step 3] 重启 S2（ops RUN_ID 294 或等价）
  ↓
[Step 4] 验证 shim 生效 + 前 100 步健康
  ↓
[后台] data 跑 pre-blend（方案 B）→ 优化 I/O（非阻塞）
```

---

## 4. 验证证据

```
# shard counts (实测 2026-11-28)
stackv3_filt: 8192 .bin files, each ~180-250MB, total 1.8TB
megamath_web: 4950 .bin files, total 813GB
megamath: 348 symlinks (NOT actually pre-blended)
nemotron: 193 .bin files
finemath: 64 .bin files
S1 pre-blend sources: 16 .bin each (en_v1_4, ufw_l1_en_hq, code_l2, code_l3, math_l1, math_l3)
ufw_zh: 4 .bin files

# BLEND string size estimate
13847 shards × 2 words × ~100 chars/word = ~2,769,400 bytes = 2.64 MB
> MAX_ARG_STRLEN (131,072 bytes = 128 KB) ← 单参数超限
> ARG_MAX (2,097,152 bytes = 2 MB) ← 总量超限

# Error message (from /tmp/baize_s2_launch.log)
train.sh: line 282: torchrun: Argument list too long
worker_rc=126 master_rc=126
```

---

## 5. 风险评估

| 风险 | 概率 | 影响 | 缓解 |
|:--|:--|:--|:--|
| 方案 A 补丁引入 bug | 低 | 中 | DRY=1 验证 + flag-off 回归 |
| blend_runtime.txt 被别线误删 | 低 | 高 | 文件在 BAIZE_TRAIN_CODE 目录下，别线不碰 |
| NFS 文件读取延迟 | 极低 | 低 | 文件仅 ~2.6MB，NFS 缓存命中 |
| 方案 B pre-blend 期间磁盘空间不足 | 中 | 中 | stackv3_filt 1.8TB 需双倍空间，检查 /nas_user 余量 |
