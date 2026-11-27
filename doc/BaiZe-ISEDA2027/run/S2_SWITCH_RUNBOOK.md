# S2 Blend Hot-Switch Runbook — 2026-11-27

> **状态**: 🔴 CRITICAL — data 线 patch 架构不兼容，需运维/data 拍板选路后才能执行
> **作者**: pretrain agent #3475
> **用户令**: 2026-11-27 08:3x「按照方案 A 做准备」

---

## 1. 问题核心：patch 架构不兼容

### 1.1 data 线 patch 目标

data 线 `blend_hotswitch.patch` 修改 6 个文件，全在**标准 Megatron-LM** 路径：
- `megatron/core/datasets/blend_switcher.py`（新建）
- `megatron/core/datasets/blended_dataset.py`（加 update_weights）
- `megatron/legacy/data/data_samplers.py`（加 BlendHotSwitchRandomSampler）
- `megatron/training/arguments.py`（加 --blend-hot-switch 等 CLI args）
- `megatron/training/training.py`（train loop 加 maybe_trigger_blend_switch 调用）
- `megatron/training/checkpointing.py`（保存/恢复 _blend_switch_done）

### 1.2 BaiZe 实际训练架构

BaiZe 训练走 **Megatron Bridge** 路径（完全不同的代码）：
- `pretrain_launcher.py:147` → `from megatron.bridge.training.pretrain import pretrain`
- `pretrain_launcher.py:306` → `pretrain(cfg, forward_step_func=forward_step)`
- → `megatron.bridge.training.train.train()`（lines 71-466，无 blend switch 调用）
- → `megatron.bridge.data.samplers.MegatronPretrainingSampler`（无 BlendHotSwitchRandomSampler）

### 1.3 证据链（7 项）

1. Launcher 明确调用 bridge API（pretrain_launcher.py:147,306）
2. BAIZE_TRAIN_CODE = BaiZe-ISEDA2027（common.env:12，NOT Megatron-LM）
3. megatron 包来自 conda 安装（miniforge3/envs/py310/site-packages/megatron）
4. bridge train loop 无 maybe_trigger_blend_switch 调用（train.py:71-466）
5. bridge 用 ConfigContainer dataclass，非 get_args() argparse → CLI arg 不存在
6. bridge sampler 无 BlendHotSwitchRandomSampler
7. blend_switcher.py 不在安装包 MCore 中

### 1.4 额外发现

- `blend_s2_preblend.tsv` **不存在**（data runbook 声称已交付但两处路径均无）
- `Megatron-LM-blendswitch` fork 有 patch 但训练不使用此 fork
- data runbook 假设错误：line15 BAIZE_TRAIN_CODE、line78 不需重启、line145 base commit


---

## 2. 三个选项（待运维/data 拍板）

### Option A：适配 bridge 路径（完整热切换）

将 data 线 patch 逻辑移植到 bridge 代码路径。需改 5 个 conda 安装包文件：
1. `bridge/data/samplers.py` — 加 BlendHotSwitchRandomSampler
2. `bridge/training/train.py` — train loop 加 maybe_trigger_blend_switch 调用
3. `core/datasets/blended_dataset.py` — 加 update_weights + blend_switcher 属性
4. 新建 `core/datasets/blend_switcher.py` — 从 data 线交付物复制
5. `bridge/training/config.py` 或 launcher — 加配置项

额外需创建 `blend_s2_preblend.tsv`。
工时 ~2-4h。风险=改 conda 包。优点=保留 zero-overlap。回退=从 350k 用 S1 resume。

### Option B：冷切换（kill + 改 TSV + resume）

350k ckpt 保存后 kill 训练，修改 BLEND_TSV 环境变量指向 S2 blend，从 350k resume。
工时 ~30min。风险=无 zero-overlap 保证（但 S1/S2 数据源重叠可控）。
优点=简单可靠不碰 conda 包。回退=从 350k 用 S1 resume。

### Option C：推迟切换

暂不执行 350k 切换，等 data 线适配 bridge 路径后再切。
工时 0。风险=切换点后移。优点=最安全不改代码。

---

## 3. 当前训练状态快照（2026-11-27 09:0x）

- iter=340100/700000 (48.6%), loss≈1.99, step~7.4s, 0NaN/0skip ✅
- GPU .29 8×95-100% / 74-75GB / 43-62°C ✅
- latest ckpt=iter_0340000 (saved 08:34:42)
- 350k ETA ≈ 11-28 01:00 (≈16.5h)
- daemon PID 501728 idle, autoqueue 57/57 (10k-330k, 330k=57.50%)
- eval_next=340k (ON DISK ✅)

---

## 4. 执行切换通用步骤（选项确定后）

> 授权在 350k 时 kill + 应用修改 + 重启（仅限此次）

### 切换前
- [x] 阅读 data 交付物
- [x] 代码核查（发现不兼容）
- [x] 制定 runbook
- [ ] 运维/data 确认选项
- [ ] 执行所选选项的准备步骤
- [ ] commit 记录现场

### 切换时
1. 确认 350k ckpt 落盘
2. 记录切换前状态
3. Kill 训练（两节点）
4. 应用修改
5. 从 350k resume
6. 验证 step time / loss / ratio

### 切换后
- 继续监控 + L1 评测 350k
- 恢复维护态
- 异常 → kill + 从 350k S1 resume → 标 ⚠️ 待运维处理

---

## 5. 待确认问题（给 data 线）

1. `blend_s2_preblend.tsv` 在哪里？
2. data 线是否知道 BaiZe 训练用 Megatron Bridge？
3. 如选 Option A，data 线能否协助适配 bridge？
4. S2 blend 的 10 源具体是哪些？