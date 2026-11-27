# S2 Blend Hot-Switch Runbook — Bridge Edition · 2026-11-27

> **状态**: ✅ READY — Bridge Edition shim 已验证，所有交付物就位，等待 350k ckpt
> **作者**: pretrain agent (updated #3477)
> **用户令**: 2026-11-27 08:3x「按照方案 A 做准备」
> **数据线**: data R874 (2026-11-27 11:0x) 已回复所有疑问，Bridge Edition 10/10 PASS

---

## 0. 方案概述

BaiZe 训练使用 **Megatron Bridge**（非标准 Megatron-LM）。data 线原有的
`blend_hotswitch.patch`（针对标准 Megatron-LM）**不适用**（详见 #3475/#3476 证据链）。

**替代方案 = runtime monkey-patch shim**（`blend_hot_switch_bridge_compat.py`），
遵循现有 `bridge_compat.py` 的同一模式：在 `pretrain_launcher.py` 中 import 并调用，
不修改 site-packages。切换方式 = **冷切换**（stop → set env → restart from 350k ckpt）。

**零重叠保证**: cursor_offsets_350k.json 预计算了 S1 消费 350k×256=89.6M 样本的
per-source 游标。S2 的 BlendedDataset 构建后，shim 将共享源的 `dataset_sample_index`
加上 S1 消费偏移 → S1 已消费的 shuffle 位置被跳过 → zero_overlap=0（已验证）。

---

## 1. 交付物清单（全部已验证存在 ✅）

| 文件 | 位置 | 状态 | 用途 |
|:--|:--|:--|:--|
| `blend_hot_switch_bridge_compat.py` | `code/BaiZe-ISEDA2027/` | ✅ 4226B, commit 3dbf056 | 运行时 shim |
| `pretrain_launcher.py` L302-310 | `code/BaiZe-ISEDA2027/` | ✅ 已加 try/import shim | 自动加载 shim |
| `cursor_offsets_350k.json` | `run/data/blendswitch/` | ✅ 1093B | 350k 切换点 cursor offsets |
| `blend_s2_preblend.tsv` | `code/baize-llm/configs/` | ✅ 3625B | S2 blend TSV (12 源) |
| `train.sh` (modified) | `code/baize-llm/scripts/` | ✅ +4 lines | BLEND_CURSOR_OFFSETS_JSON 透传双节点 |
| `verify_results_bridge.json` | `run/data/blendswitch/` | ✅ 10/10 PASS | Bridge Edition 验证结果 |

---

## 2. 关键参数

| 参数 | 值 | 说明 |
|:--|:--|:--|
| 切换步 | 350000 | save-interval=2000, 350k 自然落盘 |
| 开关 | env `BLEND_CURSOR_OFFSETS_JSON` | 不设=stock; 设=应用 cursor offsets |
| S2 TSV | `blend_s2_preblend.tsv` | 12 源: web40/code40/math20 |
| 共享源 | 7 | 获得 cursor offset (跳过 S1 已消费) |
| 新源 | 5 | offset=0 (零重叠, 从头开始) |
| 总消费 | 89,600,000 | 350000 步 × GBS 256 |
| 训练参数 | 不变 | LR=1e-3, warmup=2000, seq=16K |

### cursor_offsets_350k.json（S2 源顺序）

| # | Source Key | Shared | Offset |
|:--|:--|:--|:--|
| 0 | en_v1_4 | ✅ | 58,240,000 |
| 1 | ufw_l1_en_hq | ✅ | 4,480,000 |
| 2 | ufw_zh | ✅ | 3,584,000 |
| 3 | code_l2 | ✅ | 13,440,000 |
| 4 | code_l3 | ✅ | 3,584,000 |
| 5 | stackv3_filt | ❌ new | 0 |
| 6 | math_l1 | ✅ | 4,480,000 |
| 7 | math_l3 | ✅ | 1,792,000 |
| 8-11 | megamath/finemath/nemotron/megamath_web | ❌ new | 0 |

---

## 3. 🔧 train.sh 修改（已完成）

**问题**: `train.sh` 的 SSH 命令只导出 `NCCL_ENV` + `PYTORCH_ENV` 到远程节点 (.12)。
`BLEND_CURSOR_OFFSETS_JSON` 不在其中 → rank0 (.12) 不会应用 cursor offsets →
rank0 读 S1 数据, rank1 读 S2 数据 → DDP 数据不一致 → 训练异常。

**修复**: 在 `PYTORCH_ENV` 构建中加一行（与 BAIZE_NUM_WORKERS #801 同机制）:
```bash
PYTORCH_ENV="$PYTORCH_ENV BLEND_CURSOR_OFFSETS_JSON=${BLEND_CURSOR_OFFSETS_JSON:-}"
```
位置: `train.sh` L202-206 (PYTHONNOUSERSITE 行之后)。空值=no-op (stock 行为)。

---

## 4. 切换操作步骤（350k 时执行）

### 步骤 1: 确认 350k ckpt 落盘
```bash
cat .../checkpoints/latest_checkpointed_iteration.txt  # 应输出 350000
ls -d .../checkpoints/iter_0350000
```

### 步骤 2: 记录切换前状态
```bash
tail -3 /tmp/baize_s1_baize2b_worker.log   # iter / step / loss
ps -eo pid=,ppid=,etimes=,args= | grep -E 'pretrain_launcher|train.sh' | grep -v grep
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader
```

### 步骤 3: Kill 训练（两节点）
```bash
kill <train.sh PID>     # 在 .29 上 kill train.sh
sleep 5
ssh -n -o BatchMode=yes 10.239.2.12 'pgrep -af pretrain_launcher || echo "CLEAN"'
# 如有残留: ssh 10.239.2.12 'kill <PID>'
```

### 步骤 4: 验证代码就位
```bash
ls -la /nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py
grep -n 'blend_hot_switch_bridge_compat' .../pretrain_launcher.py
grep -n 'BLEND_CURSOR_OFFSETS_JSON' .../baize-llm/scripts/train.sh
ls -la .../baize-llm/configs/blend_s2_preblend.tsv
ls -la .../run/data/blendswitch/cursor_offsets_350k.json
cd .../BaiZe-ISEDA2027 && python -c \
  'from blend_hot_switch_bridge_compat import apply_blend_cursor_offset_shim; print("OK")'
```

### 步骤 5: 设置环境变量 + 重启训练
```bash
setsid bash -c 'cd /nas_train/app.e0031982/code/baize-llm && \
  export BLEND_TSV=/nas_train/app.e0031982/code/baize-llm/configs/blend_s2_preblend.tsv && \
  export BLEND_CURSOR_OFFSETS_JSON=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json && \
  bash scripts/train.sh s1' > /tmp/baize_s1_s2_launch.log 2>&1 < /dev/null &
echo "LAUNCHED PID=$!"
```
> `s1.env` 的 `BLEND_TSV="${BLEND_TSV:-...}"` 不会覆盖已设置的值。

### 步骤 6: 验证切换成功（前 100 步）
```bash
grep '\[blend-hot-switch\]' /tmp/baize_s1_baize2b_master.log
grep '\[blend-hot-switch\]' /tmp/baize_s1_baize2b_worker.log
tail -20 /tmp/baize_s1_baize2b_worker.log
```
| 指标 | 预期 | 异常阈值 | 处置 |
|:--|:--|:--|:--|
| loss | 微跳 ±5% | >±15% | 调查 → 可能 rollback |
| step time | ≤+2% vs ~7.3s | >+5% (>7.7s) | 调查 |
| NaN/skip | 0 | >0 | 立即 rollback |
| LR | 恒定 1e-3 | 任何变化 | 调查 |

### 步骤 7: 继续监控 + L1 评测 350k
- 350k 是 10k 边界 → L1 评测照做（S1 最后一个点）
- 切换后恢复维护态（不再自行重启）

---

## 5. 回退（如切换后异常）
```bash
# 1. Kill 训练 (同步骤 3)
# 2. 撤销环境变量:
unset BLEND_CURSOR_OFFSETS_JSON
# 3. 恢复 S1 blend TSV + resume:
setsid bash -c 'cd /nas_train/app.e0031982/code/baize-llm && \
  export BLEND_TSV=/nas_train/app.e0031982/code/baize-llm/configs/blend_s1_preblend.tsv && \
  bash scripts/train.sh s1' > /tmp/baize_s1_rollback.log 2>&1 < /dev/null &
# 4. 标 ⚠️ 待运维处理, WAITING=1
```

---

## 6. 验证状态汇总

| 测试 | 结果 |
|:--|:--|
| Bridge shim importable | ✅ IMPORT OK (本轮实测) |
| standalone 10/10 | ✅ PASS |
| integration 7/7 | ✅ PASS |
| zero_overlap (7→12) | ✅ overlap=0 |
| flag-off stock equivalence | ✅ byte-identical |
| pretrain_launcher.py modified | ✅ L302-310, commit 3dbf056 |
| train.sh BLEND_CURSOR_OFFSETS_JSON | ✅ L202-206 (本轮修改) |
| blend_s2_preblend.tsv | ✅ 3625B |
| S2 12/12 source data | ✅ (data R874 确认) |

---

## 7. 历史（#3475/#3476 已解决）
- **#3475 (09:0x)**: 发现原 patch 不兼容 Bridge → 提出 Option A/B/C
- **#3476 (09:2x)**: 终确认 4/6 目标文件不存在 → 推荐 Option B
- **data R874 (11:0x)**: Bridge Edition shim 已解决 → 10/10 PASS
- **#3477 (本轮)**: 确认 Bridge Edition 可用 + 修复 SSH env 透传 → READY