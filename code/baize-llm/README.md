# baize-llm — BaiZe-2B 预训练项目

> 2026-10-26 定案：**Mamba2-hybrid 2.2B / 16K / 16 卡（CP1·DP16）/ graph-OFF / AdamW / WSD（D 段 exponential）/ TensorBoard 6006**。
> 本目录是**唯一**的预训练启动入口。`run/baize_*.sh` 里历史脚本仅作留档，不再新增。

---

## 1. 目录结构

```
code/baize-llm/
├── README.md                     # 本文件（结构 / 快速开始 / 验收 / 排错）
├── configs/
│   ├── common.env                # 全局：路径、模型、并行、精度、优化器、LR、TB
│   ├── s1.env                    # S：4M tok/step 档 · 700k 步 · 2.94T token（S1+S2 合并）
│   ├── s2.env                    # ⚠️ 回退用：原 S2 配置（已被合并 S 取代，保留恢复 3 阶段用）
│   ├── decay.env                 # Decay：4M 档 · 20k 步（指数衰减 D 段）
│   ├── longctx.env               # 长上下文扩展（ABF）：阶梯默认值
│   ├── longctx_ladder.tsv        # 阶梯表：32K/64K/128K × token 预算 × CP
│   ├── blend_s1.tsv              # S 数据配比（原始 tokenized 路径版）
│   ├── blend_s1_preblend.tsv     # S 数据配比（pre-blend 版 · 当前使用）
│   └── blend_decay.tsv           # Decay 数据配比
├── scripts/
│   ├── lib.sh                    # 公共函数（日志 / GPU 门禁 / 特性探测）
│   ├── preflight.sh              # 开跑前自检（一条命令跑完）
│   ├── gen_blend.py              # 由 tokenized 目录 + 配比生成 --train-data-path
│   ├── pre_blend.py              # 数据 pre-blend：合并小 shard → 大 shard（减索引/降 COW）
│   ├── activate_preblend.sh      # pre-blend 完成后激活：切 TSV 绝对路径 + common.env nw=8
│   ├── train.sh                  # 统一入口：s1 | s2 | decay（支持 --smoke/--dry-run）
│   ├── tb_6006.sh                # TensorBoard 启停（.29:6006）
│   ├── lr_schedule.py            # WSD-指数 LR 曲线打印 / 与 TB 对账
│   ├── check_rope.py             # 校验 56 层 / 4 注意力 / max_pos=1M / theta=1e6
│   ├── export_hf.sh              # mcore ckpt → HF 导出 + config patch + check_rope（一键）
│   ├── abf_plan.py               # ABF 表：θ_ABF / CP / DP / gbs（长上下文准备）
│   ├── check_longctx_data.py     # 长上下文数据体检（EOD 切分 → 文档长度分布）
│   ├── longctx_ladder.sh         # 32K→64K→128K 阶梯扩展（逐级门禁）
│   ├── prune_ckpts.sh            # ckpt 保留策略清理（默认 dry-run）
│   └── status.sh                 # 进程 / 显存 / 最新步数 / LR / TB 健康一览
└── docs/
    ├── LAUNCHER_PATCH_EXP_DECAY.md   # 若 launcher 缺 --lr-decay-shape / --rotary-base 的补丁规格
    └── LONGCTX_ABF_PLAN.md           # 长上下文 ABF 准备方案（口径/阶梯/数据体检/评测矩阵）
```

**部署位置**：本目录随仓库走（`<repo>/code/baize-llm`）。训练机期望路径是
`/nas_train/app.e0031982/code/baize-llm/baize-llm`（外层 `baize-llm` 是 git 仓库或 symlink），二选一：

```bash
# A) 软链接（推荐，仓库更新即生效）
ln -sfn /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm \
        /nas_train/app.e0031982/code/baize-llm/baize-llm
# B) 直接 cp -a（仓库后续更新需重新同步）
```

> ⚠️ 2026-10-28 用户令：**后续训练一律从项目目录启动**：
> `bash /nas_train/app.e0031982/code/baize-llm/baize-llm/scripts/train.sh <stage>`
> 🚫 不再从 `run/` 散落脚本启动。

脚本不依赖被 cp 的位置：用 `BAIZE_LLM_HOME`（默认=脚本所在目录的上一级）定位配置，
用 `BAIZE_TRAIN_CODE` 定位训练代码（默认 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`，
内含 `pretrain_launcher.py`）。

---

## 2. 阶段与可实现档位

> 2026-10-28 定稿：原 S1（GBS128）+ S2（GBS256）**合并为 S**（GBS256，700k 步）。
> `s2.env` 保留为回退选项（恢复 3 阶段时启用），主路 = **2 阶段 S → Decay**。

| 阶段 | seq | mbs | gbs | accum | tok/step（精确） | 步数 | token 合计 | LR |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| **S** | 16384 | 1 | **256** | 16 | **4,194,304** | 700,000 | **2.94 T** | warmup 2000 → 1e-3 恒定 |
| Decay | 16384 | 1 | **256** | 16 | **4,194,304** | 20,000 | 83.9 B | 1e-3 → 1e-4（**指数**） |

> ⚠️ 构想里的「4M」是名义值。DP16 × seq16384 = **262,144** tok/microstep，
> gbs 必须取它的整数倍 ⇒ 4M 取 256（=4.194M，与 #792 E1 实测同一档）。
> 总 token **2.94T + 83.9B ≈ 3.02T**，纯训练 ETA ≈ **56.9 天**（含 20% 预留 68.3 天）。

**两个阶段的 `--train-iters` 是累计值**（S 700,000 → Decay 720,000），
共用同一个 `--name baize2b`：每阶段启动时自动从上一阶段最后一个 checkpoint 续跑，
LR 由绝对迭代数决定，所以 S 不设 decay（`--lr-decay-iters 0`），
Decay 设 `--lr-decay-iters 20000` ⇒ 衰减恰好覆盖 700,000→720,000。

**数据处理**：`gen_blend.py` 把每源 prop 均分到该源所有 shard（`prop / n_shards`，浮点权重，
Megatron blended dataset 支持浮点），并在 `--verify` 时用 `.bin` 字节 / 4 反算 token 数与 epochs，
与 `configs/blend_*.tsv` 的 epochs 列对账（偏差 >10% 会告警）。

### 2.1 checkpoint 策略（用户令：**每 2000 步一个**）

三阶段 `SAVE_INTERVAL` 统一 **2000**（`configs/s1|s2|decay.env`）：

| 阶段 | 步数 | ckpt 个数 | 模型权重(≈4.4GB/个) | 含 Adam 状态(≈30GB/个) |
|:--|--:|--:|--:|--:|
| S | 700,000 | 350 | 1.54 TB | 10.5 TB |
| Decay | 20,000 | 10 | 44 GB | 300 GB |

（单个 ckpt 体积实测口径：torch_dist 模型态 ≈4.4GB / 含 Adam 状态 ≈30GB，见
`EXPERIMENTS_PRETRAIN_2B_ROUND2.md` §P-5b/P-8。是否存 optimizer 由 launcher 的 `save_optim` 决定。）

**所以必须配合保留策略**（否则 2000 步间隔会写满 `/nas_train`）：

```bash
# 先 dry-run 看保留/删除清单
bash scripts/prune_ckpts.sh --keep-last 3 --milestone-every 25000
# 确认后执行（训练中的 latest 与 latest_checkpointed_iteration.txt 永远受保护）
bash scripts/prune_ckpts.sh --keep-last 3 --milestone-every 25000 --apply
```

默认策略 = **最近 3 个 + 每 25,000 步一个里程碑**（S 700k → 约 28 + 3 = 31 个；按 4.4GB ≈ 136GB，
按 30GB ≈ 930GB）。建议：**每 20k 步（10 个 ckpt）跑一次 dry-run，每 50k 步执行一次 --apply**。

### 2.2 RoPE / 1M 位置（用户令 2026-10-26）

56 层 = **4 层全注意力（吃 RoPE）** + 24 层 Mamba2 + 28 层 MLP；本次要求把 RoPE 的
**max embedding position 设为 1M**：

| 项 | 取值 | 说明 |
|:--|:--|:--|
| `ROPE_MAX_POS` | **1,048,576**（2^20） | 不是十进制 1,000,000（与 `run/baize_b1_longctx_extend.py` 的 ABF_1e6 一致） |
| `ROPE_THETA` | **1,000,000**（ABF） | ⚠️ **必须与 max_pos 同时改**：本项目 2026-10-06 实测「只抬 max_pos 不改 theta」⇒ cos/sin 高频分量溢出 ⇒ **全 NaN（连 4K 都 NaN）** |
| `ROPE_SCALING` | 空 | 训练期不启 PI/NTK/YaRN（theta=1e6 已覆盖 1M 位置） |
| 生效位置 | `--rotary-base`（训练） + `max_position_embeddings`（导出/推理 config） | Megatron 侧 RoPE 逐位置计算，训练真正吃的是 theta |

- `train.sh` 会传 `--rotary-base 1000000`；launcher 若没有该参数 ⇒ **默认拒绝开跑**
  （`ROPE_REQUIRED=1`），按 `docs/LAUNCHER_PATCH_EXP_DECAY.md` §RoPE 打补丁。
- 若 launcher 无 `--max-position-embeddings`：训练不受影响，但**导出 HF config 必须写 1048576**，
  由 `scripts/check_rope.py` 卡口：

```bash
python scripts/check_rope.py --hf-dir $EXP_ROOT/baize2b/hf_iter_2000
# ⇒ PASS: 56 层 / attention=4 / max_pos=1048576 / theta=1e6 / rope_scaling=None
```

> ⚠️ 已知代价：既有推理侧实测（在 4K 训练的 ckpt 上事后做 ABF）4K PPL 83.24 vs 基线 75.36（+10.5%）。
> 本次是**从头训练**、theta 初始即 1e6，不存在「事后换 theta」的税；但必须盯**前 500 步 loss**
> 与同时长 baseline 对照，异常升高（>5%）要在心跳里标出来。

### 2.3 长上下文：ABF（用户令 2026-10-26「长上下文用 ABF，要为此做好准备」）

**口径**：训练主配方保持 **16K**；长上下文能力 = **ABF 外推（θ=1e6，已覆盖到 1M，B1 实测）+ 可选序列阶梯扩展**。
**产品目标 = 1M**（16K 起步就是为把外推倍数压到 64×）；路径 = 16K → 阶梯 32K/64K/128K(/256K) → ABF 外推 1M。完整方案见 `docs/LONGCTX_ABF_PLAN.md`。

| 工具 | 作用 | 命令 |
|:--|:--|:--|
| `scripts/abf_plan.py` | 打印 θ_ABF / CP / DP / gbs 表（16 卡可行性） | `python scripts/abf_plan.py` |
| `scripts/check_longctx_data.py` | 按 EOD（129280）统计文档长度分布 → 有多少 token 真能进 32K/128K | `python scripts/check_longctx_data.py --shards <dir> --targets 32768,131072 --sample 8` |
| `scripts/longctx_ladder.sh` | 32K→64K→128K 阶梯扩展（逐级 0 NaN / 吞吐门禁，累计 iters 续跑） | `bash scripts/longctx_ladder.sh --dry-run` |
| 评测 | 复用 `run/baize_b1_longctx_extend.py` 的 PPL/passkey | 见方案 §4 |

**三条硬判据**（写进方案，不可省）：
1. **数据侧**：≥32K 文档的 token 占比应 ≥20%，≥128K 应 ≥5%；不达标要「长文档优先采样或补源」，否则长上下文只是学会拼接。
2. **配置侧**：θ 与 max_pos 必须成对（只抬 max_pos ⇒ 全 NaN，2026-10-06 实测）；导出后 `check_rope.py` 必须 PASS。
3. **效果侧**：PPL 相对上一级抬升 ≤5%，passkey ≥95%，CS8 退化 ≤1pp；θ 升级后必须复测 16K 不退化（≤1%）。

> 阶梯预算（可选）：32K/20B ≈15.8h + 64K/10B ≈15.4h + 128K/5B ≈15.4h ≈ **47h / 750 GPU·h**；
> 只做 32K 则 ~16h。32K 的 CP 开销是结构性的（351,526 tok/s = 16K 的 59%），不承诺长上下文满速。

---



---

## 3. 快速开始

### 3.0 数据 pre-blend（首次开跑前必做）

> 2026-10-28 定稿：627 片小 shard 的 blend 索引撑大 fork-COW → OOM → 被迫 nw=0 → 吞吐仅 308K。
> **pre-blend** 把各源合并成 ~16 片大 shard → 索引骤小 → 恢复 nw=8 → 趋近 614K tok/s。

```bash
cd /nas_train/app.e0031982/code/baize-llm/baize-llm

# 1) pre-blend 各源（每源做完即可换入 gen_blend，无需等全部完成）
#    只 pre-blend Stable 7 源（Decay 暂不）
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python
$PY scripts/pre_blend.py \
  --src-dir /nas_train/app.e0031982/datasets/baize-data/tokenized/Ultra-FineWeb/ultrafineweb_en_v1_4 \
  --out-dir /nas_user/app.e0031982/datasets/pre-blend/en_v1_4 \
  --prefix en_v1_4_pb --target-shards 16 --skip-existing
# （对其余 5 源重复，改 --src-dir / --out-dir / --prefix）

# 2) 全部完成后，激活 pre-blend（更新 TSV 绝对路径 + common.env nw=8 + 重启 mmap）
bash scripts/activate_preblend.sh
```

### 3.1 训练启动

```bash
cd /nas_train/app.e0031982/code/baize-llm/baize-llm

# 0) 一次性自检（GPU / 数据 / tokenizer / 磁盘 / launcher 特性 / 端口）
bash scripts/preflight.sh

# 1) 只看 blend 展开结果，不启动训练
bash scripts/train.sh s1 --dry-run

# 2) 20 步冒烟（单机 8 卡，不与 vision 抢 .12；名字带 _smoke，不污染正式 ckpt）
bash scripts/train.sh s1 --smoke 20

# 3) TensorBoard（.29 上监听 6006）
bash scripts/tb_6006.sh start
#    → http://10.239.2.29:6006

# 4) 正式启动（16 卡 = .12 master + .29 worker；.12 非空闲会自动跳过）
bash scripts/train.sh s1          # S stable · 700k 步 · 2.94T token
bash scripts/train.sh decay       # S 收尾后 · 20k 步 · 指数衰减
```

后台运行一律 `setsid`：

```bash

---

## 4. 监控（TensorBoard · .29:6006）

- 日志目录：`$BAIZE_TRAIN_CODE/nemo_experiments`（每个 `--name` 一个子目录，内含 `tb_logs/`）。
- 启动：`bash scripts/tb_6006.sh start` → `tensorboard --logdir <exp_root> --host 0.0.0.0 --port 6006 --reload_interval 30`
- 健康检查：`bash scripts/tb_6006.sh status`（`ss -ltn` + `curl 127.0.0.1:6006` + 事件文件最新 mtime）
- 关键标量：`training/loss`、`learning-rate`、`grad-norm`、`throughput`（tok/s）。
- **LR 对账**（验收 D 段是否真是指数衰减）：

```bash
# 打印理论曲线
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 --decay-iters 20000 --total-iters 720000
# 用 TB 导出的 csv 对账（columns: step,learning-rate）
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 --decay-iters 20000 --total-iters 720000 \
    --tb-csv /tmp/lr_from_tb.csv --tol 1e-3
```

---

## 4.5 HF 导出与 RoPE 验证

首个 checkpoint 落盘后（默认 `--save-interval 2000`，即 iter 2000），导出 HF 格式并验证 1M 位置编码：

```bash
# 一键导出 + patch config + check_rope.py 验证
bash scripts/export_hf.sh 2000
# → 产出: $EXP_ROOT/baize2b/hf_iter_2000/
# → check_rope.py 自动跑：56 层 / 4 注意力 / max_pos=1048576 / theta=1e6 / rope_scaling=None → PASS
```

如需手动导出（分步）：

```bash
# 1) mcore → HF safetensors（convert_mcore_to_hf.py 在 $BAIZE_TRAIN_CODE 下）
python $BAIZE_TRAIN_CODE/convert_mcore_to_hf.py \
    --arch hybrid \
    --ckpt-dir $EXP_ROOT/baize2b/checkpoints/iter_2000 \
    --output-dir $EXP_ROOT/baize2b/hf_iter_2000

# 2) Patch config.json（转换器默认 max_pos=4096，需改为 1M + theta=1e6）
python -c "
import json
p = '$EXP_ROOT/baize2b/hf_iter_2000/config.json'
cfg = json.load(open(p))
cfg['max_position_embeddings'] = 1048576
cfg['rope_theta'] = 1000000
cfg['rope_scaling'] = None
json.dump(cfg, open(p, 'w'), indent=2)
"

# 3) 验证
python scripts/check_rope.py --hf-dir $EXP_ROOT/baize2b/hf_iter_2000
```

---

## 5. 验收标准（每阶段）

| 项 | 判据 |
|:--|:--|
| 优化器 | 日志/`--optimizer adam`；首 10 步 `grad-norm` 有限，无 NaN |
| LR（S） | 2000 步内 0→1e-3 线性；之后恒定 1e-3（TB `learning-rate` ±1e-9） |
| LR（Decay） | D 段 `lr(p)=peak·(min/peak)^p`，20,000 步从 1e-3 降到 1e-4。抽查 p=0.25/0.5/0.75 与 `lr_schedule.py` 输出一致（相对误差 ≤0.1%） |
| CUDA Graph | **必须 OFF**（日志无 "cuda graph" capture；否则 16K 会掉到 ~110K tok/s） |
| 吞吐 | S/Decay 应 ≥ **550K tok/s**（#792 实测 613,992 的 90%）；pre-blend + nw=8 后目标趋近 614K |
| 显存 | 峰值 ≤ 78 GB（#792 实测 75.2 GB） |
| TensorBoard | `.29:6006` 可访问，`learning-rate` 标量随步数变化 |
| RoPE / 1M | 启动命令含 `--rotary-base 1000000`；导出 config 经 `check_rope.py` **PASS**（56 层 / attention=4 / max_pos=1048576 / theta=1e6）；前 500 步 loss 无异常抬升（>5%） |
| checkpoint | **每 2000 步落一个**（`ls checkpoints/iter_* | wc -l` 随时间线性增长）；磁盘由 `prune_ckpts.sh` 控（保留最近 3 + 每 25k 里程碑） |

---

## 6. 前置阻塞（必须先解决）

1. **Decay 阶段数据未就绪**：`UltraData-SFT-2605`（0.60）与 `UltraData-SFT-Agent-2609`（0.12）
   在 `DATA_MAPPING.md` 里仍是**未分词**（0 shard）。`configs/blend_decay.tsv` 已如实登记，
   `gen_blend.py` 会直接报错退出 —— **Decay 不得开跑**，需 data 线先分词。
   S 不受影响（7 源均在 tokenized 镜像内、状态「镜像完整」）。
2. **16 卡 = 借用 .12**：`train.sh` 内置「.12 非空闲即 SKIP」门禁（不抢 vision）。若 .12 被占用，
   只能单机 8 卡跑 S（吞吐约减半，ETA 翻倍），需另行决策。
3. **launcher 特性**：`--lr-decay-shape` 若不存在，`preflight.sh` 会红字提示，
   按 `docs/LAUNCHER_PATCH_EXP_DECAY.md` 打补丁（单函数改动）。
4. **数据 pre-blend**：627 片小 shard 会导致 DataLoader fork-COW OOM（实测 nw=0 → 吞吐仅 308K）。
   pre-blend 把 7 源合并成 ~16 片大 shard 后恢复 nw=8 → 趋近 614K tok/s。
   `scripts/pre_blend.py` + `scripts/activate_preblend.sh` 完成此流程（见 §3.0）。

---

## 7. 常见问题

| 现象 | 处理 |
|:--|:--|
| `SKIP: .12 not idle` | vision 在用 .12；等空闲或改单机 8 卡（`NNODES=1` 覆盖） |
| 吞吐掉到 ~110K | CUDA graph 被打开（不要传 `--enable-cuda-graph`）；见 #786/#788 |
| `--lr-decay-shape` 不识别 | 打补丁（docs/LAUNCHER_PATCH_EXP_DECAY.md）或临时用 `LR_DECAY_SHAPE=linear` 并在心跳标注 |
| TB 6006 打不开 | `bash scripts/tb_6006.sh status`；若进程在但端口不通，查 `ss -ltn` 是否绑定 0.0.0.0 |
| TB 无新点 | 看 `nemo_experiments/<name>/tb_logs/` 最新 `events.out.tfevents.*` mtime 是否在增长 |
| 续跑后步数不对 | `--train-iters` 必须是**累计值**（见 §2），否则会误判为「已到终点」直接退出 |

---

## 8. 变更纪律

- 改配方（LR / 配比 / 并行 / batch）必须改 `configs/*.env` 并 commit，禁止在命令行临时覆盖后不留痕。
- 每次开跑/收尾写心跳：`run/MEMORY_PRETRAIN_2B.md` + `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`。
- commit 前缀：`pretrain train:`（脚本/配置改动）、`pretrain run:`（实跑结果）。
- 禁止 `git add -A`（共享工作副本，会卷入他线在途文件）。
