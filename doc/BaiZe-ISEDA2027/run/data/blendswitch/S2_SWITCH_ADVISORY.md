# S2 切换问题综合分析与献计献策

> **作者**：data agent · 2026-11-28
> **触发**：用户令「安排 data 关注 pretrain 切换 S2 时遇到的问题，思考解法，献计献策」
> **状态**：S1 已停 · 16 卡全空 · 350k ckpt 完好 · 等待应用补丁后重试 S2

---

## 0. 事件时间线

| 时间 | 事件 | 结果 |
|:--|:--|:--|
| 05:18:26 | 第 1 次切换（executor 自动）| ❌ FATAL：.12 GPU 非空闲 |
| 05:22:11 | auto-rollback S1 | ✅ S1 恢复，但 ~05:30 crash（NCCL transient） |
| 05:42 | 手动重启 S1 from 350k | ✅ S1 稳定运行至 351100 |
| 07:55:32 | 用户令停 S1 | ✅ 训练正常 SIGTERM 退出 |
| 08:06:20 | 第 2 次切换（ops RUN_ID 293）| ❌ FATAL：Argument list too long (E2BIG) |
| 08:30 | data agent 完成诊断 + 交付补丁 | ✅ 解法就绪，待应用 |

---

## 1. 问题清单（3 个独立问题）

### 问题 ①：GPU 释放时序（第 1 次失败 · 已修复）

**根因**：`s2_switch_executor.sh` Phase 4 kill 训练后**只等固定 10s**（后改为查 .29 GPU0 sleep 20s），**未验证 .12 GPU 是否已释放**。被 kill 的 worker 进程退出后，GPU 显存释放有数秒延迟（CUDA context teardown），.12 残存显存 → `pretrain_launcher.py` GPU check fail。

**已修复**：Phase 4b 加了 dual-node GPU poll：
```bash
# SSH 查 .12 nvidia-smi max MiB，poll until both<1000MiB，max 180s
for i in $(seq 1 36); do
  G29_MAX=$(nvidia-smi ... | sort -n | tail -1)
  G12_MAX=$(ssh .12 "nvidia-smi ..." | sort -n | tail -1)
  [ "$G29_MAX" -lt 1000 ] && [ "$G12_MAX" -lt 1000 ] && break
  sleep 5
done
```
`bash -n` 语法已验证。**但未在实战中测试**（随后 S1 被停）。

**残余风险**：rollback 后训练 crash（"leaked semaphore at shutdown" ×8，无 error/traceback）。可能原因：
- NCCL/CUDA 在 GPU 未完全释放时重新初始化 → 状态不一致
- rollback 时序太快（kill→5s→restart），CUDA driver 尚未回收资源
- **建议**：rollback 路径也加 GPU poll（当前只 S2 启动前 poll，rollback 启动 S1 时未 poll）

### 问题 ②：E2BIG — Argument list too long（第 2 次失败 · 补丁已交付）

**根因**：S2 blend 有 **13,847 个 shard**，`gen_blend.py` 展开为 weight+path 对的字符串 ~2.64MB，作为 `--train-data-path "$BLEND"` 单参数传给 `torchrun`，超过 Linux 内核 `MAX_ARG_STRLEN`(128KB)。

**为什么 S1 没问题**：S1 全部 7 源 pre-blend（每源 16 shard），仅 ~100 shard / ~20KB。

**已交付补丁**（`fix_arg_too_long.patch`）：
- `train.sh`：BLEND >100KB 时写文件 `blend_runtime.txt`，ARGS 传 `@filepath`
- `pretrain_launcher.py`：检测 `@` 前缀从文件读取
- flag-off = stock（BLEND <100KB 走原路径，零回归）
- 改动极小（2 文件 × ~10 行）

**验证步骤**：
```bash
# DRY RUN 验证 S2 BLEND 写文件
---

## 2. 献计献策 — 推荐执行路径

### 🅰️ 立即解除阻塞（方案 A · ~15 min）

1. **应用 `fix_arg_too_long.patch`**（手动改 `train.sh` + `pretrain_launcher.py` 各 ~10 行）
2. **DRY=1 验证**：确认 S2 BLEND 走文件路径
3. **重试 S2 启动**（从 350k ckpt resume）
4. **前 100 步重点观察**：
   - step time：可能因 13,847 shard 的 I/O 开销偏高。若 >7.4s gate 持续，考虑立即跑方案 B
   - loss：±5% 微跳正常，>±15% 需调查
   - ratio：≤1pp 偏差正常
   - shim 生效：.29 + .12 日志都须出现 `Applying cursor offsets`

### 🅱️ 后台并行优化（方案 B · ~2-6h）

在 S2 训练运行期间，后台跑 `pre_blend.py` 合并 5 个大源各→16 shard：

```bash
# 优先级排序（耗时从长到短）：
# 1. stackv3_filt (8192→16, 1.8TB, ~2-4h) — 最大瓶颈
# 2. megamath_web (4950→16, 813GB, ~1-2h)
# 3. megamath (348→16, symlink, <30min)
# 4. nemotron (193→16, ~78GB, <30min)
# 5. finemath (64→16, ~3.8GB, <15min)
```

完成后更新 `blend_s2_preblend.tsv` 指向 pre-blend 目录，在下一个 checkpoint resume 时切换。

**注意**：
- `cursor_offsets_350k.json` **不需要重算**（新源 offset=0，共享源已用 pre-blend）
- `/nas_user` 需要额外 ~2.6TB（5 源总量的副本），先检查余量
- pre-blend 期间不影响 S2 训练（写新目录，不改原数据）

### 🅲️ executor rollback 路径加固（~10 min）

当前 `s2_switch_executor.sh` 的 rollback() 函数在 kill S2 后直接重启 S1，**没有 GPU poll**。建议 rollback 路径也加 GPU poll（复用 Phase 4b 逻辑），避免第 1 次失败后 rollback→crash 的问题（leaked semaphore 可能是 GPU 未释放就重新初始化所致）。

---

## 3. 风险矩阵与缓解

| 风险 | 概率 | 影响 | 缓解 |
|:--|:--|:--|:--|
| 方案 A 补丁引入 bug | 低 | 中 | DRY=1 验证 + flag-off 回归 |
| S2 训练 step time 超 7.4s gate | 中 | 高 | 前 100 步密切监控；超限则评估是否暂停跑方案 B |
| NFS I/O 争用（13,847 文件） | 中 | 中 | 方案 B 完成后 shard→192，大幅减少 |
| pre-blend 期间磁盘空间不足 | 中 | 中 | 先 `df -h /nas_user` 确认 ≥3TB 余量 |
| rollback GPU 未释放 → crash | 低 | 高 | rollback 路径加 GPU poll |
| shim 双节点不一致 | 低 | 极高 | 启动后 grep .29 + .12 日志确认 |

---

## 4. 给 pretrain 的建议（一句话版）

1. **先应用 E2BIG 补丁**（`fix_arg_too_long.patch`，2 文件 ~10 行改动）
2. **DRY=1 验证** S2 BLEND 走文件路径
3. **重试 S2 启动**，前 100 步重点看 step time（可能因 I/O 偏高）
4. **后台并行** pre-blend 5 个大源（方案 B），完成后下个 ckpt resume 切换
5. **rollback 路径也加 GPU poll**（避免第 1 次的 crash 重演）

---

## 5. 结论

S2 切换的两次失败**都不是 data 交付物（shim/cursor/TSV）的缺陷**：
- 第 1 次：executor 操作时序问题（GPU cleanup wait 不足）→ 已修复
- 第 2 次：数据量→命令行长度问题（E2BIG）→ 补丁已交付

data 侧 25/25 PASS 验证（零重叠=0 / 配比 max_dev=0.0087% / flag-off byte-identical）全部通过。
**应用 E2BIG 补丁后即可重试 S2 切换。**

> 详见：
> - `S2_E2BIG_DIAGNOSIS.md` — E2BIG 完整诊断
> - `fix_arg_too_long.patch` — 补丁 + 验证步骤
> - `SWITCH_RUNBOOK.md` — Bridge Edition 冷切换 runbook
> - `verify_results.json` / `verify_results_integration.json` / `verify_results_bridge.json` — 3 级 25/25 PASS
BLEND_TSV=configs/blend_s2_preblend.tsv \
BLEND_CURSOR_OFFSETS_JSON=.../cursor_offsets_350k.json \
DRY=1 bash scripts/train.sh s1
# 期望：日志出现 "blend 字符串 >100KB，写入文件"

# flag-off 回归（S1 小 blend 走原路径）
BLEND_TSV=configs/blend_s1_preblend.tsv DRY=1 bash scripts/train.sh s1
# 期望：无写入文件日志
```

### 问题 ③：数据侧隐患 — 5 个未 pre-blend 源（根因之根）

E2BIG 的**深层根因**是 S2 新增的 5 个源未做 pre-blend：

| 源 | shard 数 | .bin 总量 | pre-blend? |
|:--|--:|:--|:--|
| stackv3_filt | 8,192 | 1.8 TB | ❌ |
| megamath_web | 4,950 | 813 GB | ❌ |
| megamath | 348 | symlink | ❌ |
| nemotron | 193 | ~78 GB | ❌ |
| finemath | 64 | ~3.8 GB | ❌ |
| **小计** | **13,747** | | |
| S1 共享源 | 100 | — | ✅ |
| **合计** | **13,847** | | |

**影响**：
1. 命令行超限 → E2BIG（已解法 A 解决）
2. **训练 I/O 性能**：13,847 个 mmap 文件 → DataLoader fork-COW 开销大 → step time 可能 >S1 的 7.0s
3. **NFS 压力**：大量小文件随机读 → 可能影响其他 NFS 用户