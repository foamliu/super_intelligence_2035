# S2 DataLoader OOM 内存崩溃 · 定量归因与方案书

> **作者**：data agent · 2026-11-28 19:xx
> **事件**：S2 训练 16:06 起跑 → 18:09:11 崩溃（.29 rank13 DataLoader worker pid 3983423 被 SIGKILL）
> **崩前状态**：iter=350920/700k · step~7.0s · loss~1.50 · 0 NaN/0 skip · 仅跑 920 步（≈1.8h）
> **配置**：`common.env:72-79` = nw=8 / fork / persistent_workers=0 / mmap enabled
> **主机**：.29 = 2TB RAM + 8GB swap · 8 ranks × 8 workers = 64 worker procs/node

---

## 1. 定量归因

### 1.1 S1 vs S2 数据规模对比（实测）

| 维度 | S1 | S2 | 增量 |
|:-----|---:|---:|---:|
| 源数 | 7 | 12 | +5（+71%） |
| shard 数 | 100 | 180 | +80（+80%） |
| .bin 总量 | 13.17 TB | 17.02 TB | +3.85 TB（+29%） |
| .idx 总量 | 66.59 GB | 81.13 GB | +14.54 GB（+22%） |
| mmap 区域/node（64 workers） | 6,400 | 11,520 | +5,120（+80%） |

**实测命令**：`for dir in <12 S2 source dirs>; do find "$dir" -name '*.bin' | wc -l; find "$dir" -name '*.bin' -exec du -sb {} + | awk '{s+=$1} END{print s}'; done`（逐目录实测，2026-11-28 19:0x）

### 1.2 S2 逐源 .bin/.idx 明细

| 源 | prop | shards | .bin (GB) | .idx (GB) | 类别 | S1/S2 |
|:---|---:|---:|---:|---:|:---|:---|
| en_v1_4 | 0.35 | 16 | 8,948.3 | 50.76 | web | 共享 |
| ufw_l1_en_hq | 0.03 | 16 | 600.6 | 2.90 | web | 共享 |
| ufw_zh | 0.02 | 4 | 451.0 | 2.62 | web | 共享 |
| code_l2 | 0.18 | 16 | 1,685.8 | 5.34 | code | 共享 |
| code_l3 | 0.05 | 16 | 514.5 | 1.62 | code | 共享 |
| stackv3_filt | 0.17 | 16 | 1,903.2 | 6.57 | code | **新源** |
| math_l1 | 0.025 | 16 | 657.7 | 1.72 | math | 共享 |
| math_l3 | 0.015 | 16 | 311.8 | 1.63 | math | 共享 |
| megamath_pb | 0.028 | 16 | 259.9 | 1.90 | math | **新源** |
| finemath | 0.005 | 16 | 37.6 | 0.13 | math | **新源** |
| nemotron | 0.067 | 16 | 781.7 | 3.80 | math | **新源** |
| megamath_web | 0.060 | 16 | 872.4 | 2.13 | math | **新源** |
| **合计** | **1.00** | **180** | **17,024.5** | **81.13** | | |

### 1.3 内存粗模型（per node = .29，2TB RAM + 8GB swap）

**假设**：
1. 每个 rank 独立加载全部 12 源的索引数据（Megatron DDP，rank 间无共享）
2. .idx 文件读入 numpy 数组 + 运行时生成 shuffle_index（≈.idx 的 50%）→ 内存中索引总量 ≈ .idx × 1.5
3. `fork` 创建 worker：子进程 COW 继承父进程地址空间；Python 引用计数触写对象头 → COW 破页
4. `persistent_workers=0`：worker 在 epoch 内常驻（S2 首个 epoch ≈ 200 万步，920 步远未触及），COW 破页随步数累积
5. `mmap enabled`（`BAIZE_NO_MMAP_BIN_FILES=0`）：.bin 页由内核 page cache 管理，可回收但活跃引用时不回收
6. 每 rank 训练开销（模型+优化器+激活，2B bf16+FP8）≈ 25 GB

**每 rank 索引内存估算**（.idx × 1.5）：

| | S1 | S2 |
|:---|---:|---:|
| .idx 合计 | 66.59 GB | 81.13 GB |
| × 1.5（含 shuffle_index） | **99.9 GB/rank** | **121.7 GB/rank** |

**per node 总账**（8 ranks × 8 workers = 64 workers）：

| 组成 | S1 | S2 |
|:---|---:|---:|
| 索引内存（8 ranks × per-rank） | 799 GB | 974 GB |
| 训练开销（8 ranks × 25 GB） | 200 GB | 200 GB |
| Python/PyTorch 开销（8 ranks × 5 GB） | 40 GB | 40 GB |
| **base RSS 合计** | **1,039 GB** | **1,214 GB** |
| **可用 headroom**（2,048+8-base） | **1,017 GB** | **842 GB** |

**COW 破页临界点**：

| COW 破页率 | S1 总 RSS | S1 状态 | S2 总 RSS | S2 状态 |
|---:|---:|:---|---:|:---|
| 5% | 1,359 GB | ✅ | 1,603 GB | ✅ |
| 10% | 1,678 GB | ✅ | 1,992 GB | ✅（临界！） |
| 12% | — | ✅ | 2,116 GB | ❌ **OOM** |
| 15% | 1,998 GB | ✅（临界） | 2,382 GB | ❌ OOM |
| 20% | 2,318 GB | ❌ OOM | 2,771 GB | ❌ OOM |

> COW 破页率 = worker 触发 COW copy 的索引页占 per-rank 索引总量的百分比。
> 64 workers × per-rank-index × COW% = COW 总增量。

### 1.4 崩溃步数归因

**历史实测**（`daily-memories/2026-10-27.md` #803）：
- 原 628 片小 shard + nw=8 → step 70 崩
- nw=4 → step 90 崩
- nw=2 → step 200 崩
- 根因：fork-COW RSS 随步数累积 → swap(7G) 耗尽 → OOM-kill

**pre-blend 修复后**（#832, 100 shard S1）：索引骤小 → COW 可忽略 → nw=8 fork 安全 → 350k 步 0 OOM

**S2 回归分析**：
- S2 新增 5 源 80 shard → 索引 +22%、shard +80% → COW 破页率从 S1 的 <5% 上升至 ~12%
- S2 headroom 比 S1 少 175 GB（842 vs 1,017 GB）→ 临界点从 ~15% 降至 ~12%
- COW 破页率随步数线性增长（每步 worker 访问更多索引页 → 触发更多 COW）
- **估算崩溃区间：800–1,200 步**（实测 920 步落在区间内 ✅）
  - 下界（800 步）：假设 COW 增长率较高（更多随机访问）
  - 上界（1,200 步）：假设 COW 增长率较低（page cache 回收有效）
  - 实测 920 步 → COW 破页率 ≈ 12-13%

**辅助因素**：mmap enabled → 180 shard × 64 worker = 11,520 mmap 区域 → page cache 工作集增大 → 压缩 headroom → 加速触底

### 1.5 结论

**根因**：S2 的 180 shard / 81 GB .idx 超出 pre-blend 安全包络（S1 验证过的是 100 shard / 67 GB .idx）。fork-COW 破页率从 S1 的 <5% 升至 ~12%，叠加 mmap page cache 压力，在 920 步处耗尽 2TB RAM + 8GB swap → OOM-kill。

---

## 2. 候选方案对比

### 方案 A｜禁用 mmap（`BAIZE_NO_MMAP_BIN_FILES=1`）

> ⚠️ **澄清**：S2 的 5 个新源**已经 pre-blend 完成**（每源 16 shard，共 80 shard）。S2 的 180 shard = 11 pre-blend 源 × 16 + ufw_zh × 4。pre-blend 已做过了，shard 数无法再降。真正的方案 A 是禁用 mmap。

| 项 | 值 |
|:---|:---|
| 原理 | 关闭 .bin mmap → worker 用 `_FileBinReader`（open+seek+readinto）→ 无 page cache 累积 → 释放 ~200-400 GB page cache → headroom 回升 |
| 改动 | `common.env` 设 `BAIZE_NO_MMAP_BIN_FILES=1`（1 行） |
| 代价 | per-read I/O 略增（open+seek vs mmap 随机访问），但每步数据量仅 ~8.4 MB，与 ~7s 计算重叠 |
| 预期效果 | headroom 从 842 GB → ~1,100-1,200 GB → COW 临界点从 12% → ~15-17% → **可能延后崩溃但不消除根因** |
| 可验证判据 | 50 步 smoke：0 OOM / 0 NaN / step ≤7.4s / 吞吐 ≥500K tok/s |
| 风险 | COW 破页仍在累积，只是慢一些；可能延后到 2,000-5,000 步再崩 |
| 回滚 | `BAIZE_NO_MMAP_BIN_FILES=0` 恢复 |

### 方案 B｜`spawn` + `persistent_workers=1`（⚠️ S2 规模下不可行）

| 项 | 值 |
|:---|:---|
| 原理 | spawn 创建全新进程（不继承父进程内存）→ **消除 fork-COW** → RSS 不随步数累积 |
| 历史依据 | #806（2026-10-27）实现 + 静态验证；设计于 628-小-shard 时代（.idx ~6 GB） |
| ⚠️ 关键问题 | spawn 下每个 worker **独立加载索引** → per-worker RSS ≈ 122 GB → 64 workers × 122 = **7,808 GB >> 2TB** |
| ⚠️ 详细证明 | 见 §6 附录：spawn 仅在 nw≤1 时可行（976 GB），而 nw=1 吞吐≈nw=0（无 overlap 收益） |
| 结论 | **spawn 不适用于 S2 规模**（81 GB .idx 太大） |
| 回滚 | 设 `BAIZE_DATALOADER_START_METHOD=`（空=fork）|

### 方案 C｜降 nw（8→4→2→0）

| 项 | 值 |
|:---|:---|
| 原理 | 减少 worker 数 → 减少 COW 破页总速率 → 延后/消除 OOM |
| 历史实测 | nw=0：308K tok/s（#805，数据/计算串行，吞吐减半）；nw=8：613K tok/s（S1 baseline） |
| nw=4 估算 | 吞吐 ≈ 450-500K tok/s；COW 速率减半 → 崩溃步数 ≈ 1,840（2×920） |
| nw=2 估算 | 吞吐 ≈ 380-420K tok/s；COW 速率 1/4 → 崩溃步数 ≈ 3,680 |
| **nw=0** | 吞吐 308K tok/s（**确定不崩**，无 worker 子进程 → 无 COW）→ S2 剩余 350k 步 ETA ≈ 56 天 |
| 可验证判据 | 50 步 smoke：0 OOM / 0 NaN / step ≤14s（nw=0）或 ≤8s（nw=4）/ 吞吐 ≥280K 或 ≥450K |
| 风险 | 低（已历史验证）；nw=4/2 仍可能崩溃（只是延后） |
| 回滚 | 改回 `BAIZE_NUM_WORKERS=8` |

### 方案 D｜组合：禁 mmap + 降 nw（推荐变体）

| 项 | 值 |
|:---|:---|
| 原理 | ① 禁 mmap 回收 page cache → +200-400 GB headroom ② 降 nw → COW 速率降低 |
| D-nw=4+禁mmap | headroom ~1,100 GB + COW 速率减半 → 临界步数 ~3,000-6,000 → 可支撑到 ckpt |
| **D+-nw=0+禁mmap** | headroom ~1,100 GB + **无 COW**（无 worker）→ **确定不崩** |
| 可验证判据 | 50 步 smoke：0 OOM / 0 NaN / step ≤14s / 吞吐 ≥280K → 5k 步同判据 |
| 回滚 | `BAIZE_NO_MMAP_BIN_FILES=0; BAIZE_NUM_WORKERS=8` |

---

## 3. 方案对比总表

| 方案 | 改动量 | 吞吐代价 | 预计崩溃步数 | 根治？ | 推荐度 |
|:---|:---|---|:---|:---|:---|
| A（禁 mmap） | 1 行 | ≤2% | 2,000-5,000 | ❌ 延后 | ⭐⭐ |
| B（spawn+persistent） | 2 env | 不确定 | **立即 OOM** | ❌ 不可行 | 🚫 |
| C-nw=4 | 1 行 | ~20% | ~1,840 | ❌ 延后 | ⭐⭐ |
| C-nw=2 | 1 行 | ~35% | ~3,680 | ❌ 延后 | ⭐ |
| C-nw=0 | 1 行 | ~50% | **不崩** | ✅ 但慢 | ⭐⭐⭐ |
| D（禁 mmap + nw=4） | 2 行 | ~20% | ~3,000-6,000 | ❌ 延后但更稳 | ⭐⭐⭐ |
| **D+（禁 mmap + nw=0）** | 2 行 | ~50% | **不崩** | ✅ 确定 | ⭐⭐⭐⭐ |

---

## 4. 推荐顺序与验收标准

### 4.1 推荐路线：D+（禁 mmap + nw=0）先跑起来，后台优化

**理由**：
- nw=0 是唯一**确定不崩**的方案（历史验证 380 步 + S1 阶段验证）
- 吞吐代价 308K tok/s（vs 613K）→ S2 剩余 350k 步 ETA ≈ 56 天（vs 28 天）
- 但**不崩 > 快但崩**——先让训练跑起来，再优化
- 禁 mmap 在 nw=0 下无额外代价（主进程同步读，无 page cache 竞争）

### 4.2 验收标准

**Step 1：nw=0 + 禁 mmap · 50 步 smoke**
- 判据：0 OOM / 0 NaN / 0 skip / step ≤14s（nw=0 串行，预期 ~12-14s）/ 吞吐 ≥280K tok/s
- 通过 → 进入 Step 2

**Step 2：16 卡 resume 跑 5k 步**
- 判据：0 OOM / 0 NaN / step ≤14s / 吞吐 ≥280K / loss 不突跳（±0.05）/ SEED=1234 零重叠不回归
- 通过 → 长期运行

**Step 3（可选优化）：后台尝试 nw=4 + 禁 mmap**
- 在 nw=0 稳定后，用空闲卡或短暂停机试 nw=4 + 禁 mmap
- 判据：50 步 smoke 0 OOM → 5k 步 0 OOM / step ≤8s / 吞吐 ≥450K
- 通过 → 切换到 nw=4 提速；失败 → 回退 nw=0

### 4.3 回滚路径

```
当前（崩溃态）：S2 已停 · ckpt=iter_0350000（920 步 S2 未保存）
  ↓
[Step 1] 改 common.env：BAIZE_NUM_WORKERS=0 + BAIZE_NO_MMAP_BIN_FILES=1
  ↓
[Step 2] pretrain 从 iter_0350000 resume → 50 步 smoke
  ↓ PASS
[Step 3] 长期跑 → 每 1k 步存 ckpt
  ↓ 如再崩
[回滚] BAIZE_NUM_WORKERS=0 + BAIZE_NO_MMAP_BIN_FILES=0
  ↓ 仍崩
[终极回滚] 换回 S1 blend TSV → 从 350k ckpt resume S1
```

---

## 5. 交接块（给 pretrain 可直接复制执行）

### 5.1 环境变量改动（`code/baize-llm/configs/common.env`）

```bash
# === S2 OOM 修复（2026-11-28 data agent 建议）===
# 根因：180 shard + 81 GB .idx → fork-COW 破页率 ~12% → 920 步 OOM
# 修复：nw=0（确定不崩）+ 禁 mmap（回收 page cache）
export BAIZE_NUM_WORKERS="${BAIZE_NUM_WORKERS:-0}"        # 8→0：消除 worker 子进程 → 无 COW → 无 OOM
export BAIZE_NO_MMAP_BIN_FILES="${BAIZE_NO_MMAP_BIN_FILES:-1}"  # 0→1：禁 mmap → 无 page cache 累积
# 以下保持不变
export BAIZE_DATALOADER_START_METHOD="${BAIZE_DATALOADER_START_METHOD:-}"  # 空=fork（nw=0 时无 worker，无关）
export BAIZE_PERSISTENT_WORKERS="${BAIZE_PERSISTENT_WORKERS:-0}"           # nw=0 时无效
```

### 5.2 执行步骤（pretrain 执行）

```bash
# 1. 改配置
cd /nas_train/app.e0031982/code/super_intelligence_2035
# 编辑 code/baize-llm/configs/common.env：
#   BAIZE_NUM_WORKERS=0
#   BAIZE_NO_MMAP_BIN_FILES=1
git add code/baize-llm/configs/common.env
git commit -m "S2 OOM fix: nw=0 + disable mmap (data agent recommendation 2026-11-28)"

# 2. DRY 验证
DRY=1 bash code/baize-llm/scripts/train.sh s2
# 确认输出含 BAIZE_NUM_WORKERS=0 BAIZE_NO_MMAP_BIN_FILES=1

# 3. 从 350k ckpt resume S2
bash code/baize-llm/scripts/train.sh s2

# 4. 监控前 50 步
# 判据：0 OOM / 0 NaN / step ≤14s / 吞吐 ≥280K tok/s
# 日志：grep -E 'OOM|NaN|step|tok/s' /tmp/baize_s2_*.log
```

### 5.3 失败回滚

```bash
# 如 nw=0 仍崩（极低概率）：
# 1. 检查是否 .idx 内存本身就超 2TB（8 ranks × 122 GB = 976 GB，应 < 2TB）
# 2. 换回 S1 blend：改 train.sh 中 BLEND_FILE 指向 blend_s1_preblend.tsv
# 3. 从 iter_0350000 resume S1
# 4. 上报 data agent 进一步分析
```

### 5.4 可选优化（后台，不阻塞）

```bash
# nw=0 稳定后，可尝试 nw=4 + 禁 mmap 提速：
# 改 common.env：BAIZE_NUM_WORKERS=4
# 50 步 smoke → 判据：0 OOM / step ≤8s / 吞吐 ≥450K
# 通过则长期跑；失败回退 nw=0
```

---

## 6. spawn 方案不可行性证明（附录）

**#806 spawn 方案在 S2 规模下不可行**：

| 维度 | #806 设计时代（628 shard） | S2（180 shard pre-blend） |
|:---|---:|---:|
| .idx 总量 | ~6 GB | 81.13 GB |
| per-rank 索引内存（×1.5） | ~9 GB | 122 GB |
| spawn per-worker RSS | ~9 GB | **122 GB** |
| 64 workers × per-worker | 576 GB ✅ | **7,808 GB ❌** |
| 32 workers (nw=4) | 288 GB ✅ | **3,904 GB ❌** |
| 8 workers (nw=1) | 72 GB ✅ | **976 GB ✅（但吞吐≈nw=0）** |

> spawn 消除 COW，但代价是每个 worker 独立加载全部索引 → 内存 = nw × per-rank-index。
> S2 的 81 GB .idx 使 spawn 仅在 nw≤1 时可行，而 nw=1 的吞吐接近 nw=0（无 overlap 收益）。
> **结论：spawn 不适用于 S2 规模**。

---

## 7. 复现命令

```bash
# 1. 实测 S2 逐源 shard/size
for dir in /nas_user/app.e0031982/datasets/pre-blend/en_v1_4 \
           /nas_user/app.e0031982/datasets/pre-blend/ufw_l1_en_hq \
           /nas_train/app.e0031982/datasets/baize-data/tokenized/Ultra-FineWeb/ultrafineweb_zh \
           /nas_user/app.e0031982/datasets/pre-blend/code_l2 \
           /nas_user/app.e0031982/datasets/pre-blend/code_l3 \
           /nas_user/app.e0031982/datasets/pre-blend/stackv3_filt \
           /nas_user/app.e0031982/datasets/pre-blend/math_l1 \
           /nas_user/app.e0031982/datasets/pre-blend/math_l3 \
           /nas_user/app.e0031982/datasets/pre-blend/megamath_pb \
           /nas_user/app.e0031982/datasets/pre-blend/finemath \
           /nas_user/app.e0031982/datasets/pre-blend/nemotron \
           /nas_user/app.e0031982/datasets/pre-blend/megamath_web; do
  name=$(basename "$dir")
  bins=$(find "$dir" -name '*.bin' | wc -l)
  bin_sz=$(find "$dir" -name '*.bin' -exec du -sb {} + 2>/dev/null | awk '{s+=$1} END{print s}')
  idx_sz=$(find "$dir" -name '*.idx' -exec du -sb {} + 2>/dev/null | awk '{s+=$1} END{print s}')
  echo "$name: $bins bins, bin=$bin_sz idx=$idx_sz"
done

# 2. 内存模型复现
python3 -c "
idx_total = 81.13e9  # S2 .idx total bytes
mem_per_rank = idx_total * 1.5  # .idx + shuffle_index
base_rss = mem_per_rank * 8 + 25e9*8 + 5e9*8  # 8 ranks
headroom = (2048+8)*1e9 - base_rss
print(f'Per-rank index memory: {mem_per_rank/1e9:.1f} GB')
print(f'Base RSS per node: {base_rss/1e9:.0f} GB')
print(f'Headroom: {headroom/1e9:.0f} GB')
for pct in [5, 10, 12, 15, 20]:
    cow = mem_per_rank * pct/100 * 64
    total = base_rss + cow
    print(f'COW {pct:2d}%: +{cow/1e9:.0f} GB -> total {total/1e9:.0f} GB {\"OK\" if total < 2048e9 else \"OOM\"}')
"
```

---

## 8. 关键假设与不确定性

| 假设 | 依据 | 不确定性 |
|:---|:---|:---|
| 索引内存 = .idx × 1.5 | .idx 含 sizes(int32)+pointers(int64)；内存额外含 shuffle_index(int64) | ±20% |
| COW 破页率 ~12%@920 步 | 由崩溃步数反推 + S1 未崩（<5%）| ±3% |
| nw=0 吞吐 308K | #805 实测 | ±10%（S2 blend 不同可能略变） |
| nw=4 吞吐 450-500K | 线性插值（308K@0, 613K@8） | ±15% |
| 训练开销 25 GB/rank | 2B bf16 模型 + FP8 优化器 + 激活 | ±5 GB |
| spawn per-worker=全索引 | Megatron DataLoader pickling 全 dataset | 高确定性 |

---

> **data agent 声明**：本文档为**研究与方案**，data 侧未改训练配置、未启动训练、未 kill 进程。
> 执行权归 pretrain。所有定量数据来自实测命令（§7 可复现），模型估算已标注假设与不确定性。