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
│   ├── s1.env                    # S1：2M tok/step 档 · 700k 步
│   ├── s2.env                    # S2：4M tok/step 档 · 350k 步（承接 S1 ckpt）
│   ├── decay.env                 # Decay：4M 档 · 20k 步（指数衰减 D 段）
│   ├── blend_s1.tsv              # S1/S2 数据配比（prop / epochs）
│   └── blend_decay.tsv           # Decay 数据配比
├── scripts/
│   ├── lib.sh                    # 公共函数（日志 / GPU 门禁 / 特性探测）
│   ├── preflight.sh              # 开跑前自检（一条命令跑完）
│   ├── gen_blend.py              # 由 tokenized 目录 + 配比生成 --train-data-path
│   ├── train.sh                  # 统一入口：s1 | s2 | decay（支持 --smoke/--dry-run）
│   ├── tb_6006.sh                # TensorBoard 启停（.29:6006）
│   ├── lr_schedule.py            # WSD-指数 LR 曲线打印 / 与 TB 对账
│   └── status.sh                 # 进程 / 显存 / 最新步数 / LR / TB 健康一览
└── docs/
    └── LAUNCHER_PATCH_EXP_DECAY.md   # 若 launcher 不支持 --lr-decay-shape 的补丁规格
```

**部署位置**：本目录随仓库走（`<repo>/code/baize-llm`）。训练机期望路径是
`/nas_train/app.e0031982/code/baize-llm`，二选一：

```bash
# A) 软链接（推荐，仓库更新即生效）
ln -sfn /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm \
        /nas_train/app.e0031982/code/baize-llm
# B) 直接 cp -a（仓库后续更新需重新同步）
```

脚本不依赖被 cp 的位置：用 `BAIZE_LLM_HOME`（默认=脚本所在目录的上一级）定位配置，
用 `BAIZE_TRAIN_CODE` 定位训练代码（默认 `/nas_train/app.e0031982/code/BaiZe-ISEDA2027`，
内含 `pretrain_launcher.py`）。

---

## 2. 阶段与可实现档位

| 阶段 | seq | mbs | gbs | accum | tok/step（精确） | 步数 | token 合计 | LR |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| S1 | 16384 | 1 | **128** | 8 | **2,097,152** | 700,000 | 1.468 T | warmup 2000 → 1e-3 恒定 |
| S2 | 16384 | 1 | **256** | 16 | **4,194,304** | 350,000 | 1.468 T | 1e-3 恒定 |
| Decay | 16384 | 1 | **256** | 16 | **4,194,304** | 20,000 | 83.9 B | 1e-3 → 1e-4（**指数**） |

> ⚠️ 构想里的「2M / 4M」是名义值。DP16 × seq16384 = **262,144** tok/microstep，
> gbs 必须取它的整数倍 ⇒ 2M 只能取 128（=2.097M），4M 取 256（=4.194M，与 #792 E1 实测同一档）。
> 因此总 token 由 2.88T 变为 **3.02T**，纯训练 ETA 由 54.3 天变为 **56.9 天**（含 20% 预留 68.3 天）。

**三个阶段的 `--train-iters` 是累计值**（S1 700,000 → S2 1,050,000 → Decay 1,070,000），
共用同一个 `--name baize2b`：每阶段启动时自动从上一阶段最后一个 checkpoint 续跑，
LR 由绝对迭代数决定，所以 S1/S2 不设 decay（`--lr-decay-iters 0`），
Decay 设 `--lr-decay-iters 20000` ⇒ 衰减恰好覆盖 1,050,000→1,070,000。

**数据处理**：`gen_blend.py` 把每源 prop 均分到该源所有 shard（`prop / n_shards`，浮点权重，
Megatron blended dataset 支持浮点），并在 `--verify` 时用 `.bin` 字节 / 4 反算 token 数与 epochs，
与 `configs/blend_*.tsv` 的 epochs 列对账（偏差 >10% 会告警）。

---

## 3. 快速开始

```bash
cd /nas_train/app.e0031982/code/baize-llm

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
bash scripts/train.sh s1
bash scripts/train.sh s2        # S1 收尾后
bash scripts/train.sh decay     # S2 收尾后
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
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --decay-iters 20000 --total-iters 1070000
# 用 TB 导出的 csv 对账（columns: step,learning-rate）
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --decay-iters 20000 --total-iters 1070000 \
    --tb-csv /tmp/lr_from_tb.csv --tol 1e-3
```

---

## 5. 验收标准（每阶段）

| 项 | 判据 |
|:--|:--|
| 优化器 | 日志/`--optimizer adam`；首 10 步 `grad-norm` 有限，无 NaN |
| LR（S1） | 2000 步内 0→1e-3 线性；之后恒定 1e-3（TB `learning-rate` ±1e-9） |
| LR（Decay） | D 段 `lr(p)=peak·(min/peak)^p`，20,000 步从 1e-3 降到 1e-4。抽查 p=0.25/0.5/0.75 与 `lr_schedule.py` 输出一致（相对误差 ≤0.1%） |
| CUDA Graph | **必须 OFF**（日志无 "cuda graph" capture；否则 16K 会掉到 ~110K tok/s） |
| 吞吐 | S2/Decay 应 ≥ **550K tok/s**（#792 实测 613,992 的 90%）；S1 允许 480–550K（tok/step 减半） |
| 显存 | 峰值 ≤ 78 GB（#792 实测 75.2 GB） |
| TensorBoard | `.29:6006` 可访问，`learning-rate` 标量随步数变化 |

---

## 6. 前置阻塞（必须先解决）

1. **Decay 阶段数据未就绪**：`UltraData-SFT-2605`（0.60）与 `UltraData-SFT-Agent-2609`（0.12）
   在 `DATA_MAPPING.md` 里仍是**未分词**（0 shard）。`configs/blend_decay.tsv` 已如实登记，
   `gen_blend.py` 会直接报错退出 —— **Decay 不得开跑**，需 data 线先分词。
   S1/S2 不受影响（7 源均在 tokenized 镜像内、状态「镜像完整」）。
2. **16 卡 = 借用 .12**：`train.sh` 内置「.12 非空闲即 SKIP」门禁（不抢 vision）。若 .12 被占用，
   只能单机 8 卡跑 S1（吞吐约减半，ETA 翻倍），需另行决策。
3. **launcher 特性**：`--lr-decay-shape` 若不存在，`preflight.sh` 会红字提示，
   按 `docs/LAUNCHER_PATCH_EXP_DECAY.md` 打补丁（单函数改动）。

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
