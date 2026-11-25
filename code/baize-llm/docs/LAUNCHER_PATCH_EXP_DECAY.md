# Launcher 补丁规格：WSD 的 D 段改为 exponential（指数衰减）

> 适用：`/nas_train/app.e0031982/code/BaiZe-ISEDA2027/pretrain_launcher.py`（及其调用的 LR scheduler）
> 目的：让 `--lr-decay-style WSD` 的 **Decay 段**支持 `--lr-decay-shape exponential`。
> 默认行为不变（不传该参数 = 原来的形状），因此**不影响任何历史实验**。

## 1. 先探测（1 分钟）

```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
grep -n "lr-decay-style\|lr_decay_style\|WSD" pretrain_launcher.py | head -20
grep -rn "class .*Scheduler\|def get_lr\|lr_decay_style" --include=*.py . | head -20
python pretrain_launcher.py --help | grep -E "lr-decay|weight-decay|enable-cuda-graph"
```

- 若 `--help` 里**已有** `--lr-decay-shape`：什么都不用改，直接 `bash scripts/train.sh decay`。
- 若没有：按下面三步改。

## 2. 三处改动

### ① 加命令行参数

```python
group.add_argument("--lr-decay-shape", type=str, default="linear",
                   choices=["linear", "cosine", "exponential"],
                   help="WSD 的 D 段衰减形状（linear=旧行为；exponential=本计划要求）")
```

### ② 传进 scheduler 配置

```python
config.lr_decay_shape = args.lr_decay_shape
# 或（若走 NeMo/mcore dataclass）
scheduler_cfg.lr_decay_shape = args.lr_decay_shape
```

### ③ scheduler 的 WSD 分支里按 shape 计算

原逻辑（大致）：

```python
if style == "WSD":
    if iteration < warmup:      lr = peak * iteration / warmup
    elif iteration < total-decay: lr = peak
    else:
        p = (iteration - (total - decay)) / decay
        lr = min_lr + (peak - min_lr) * (1 - p)      # ← 线性，需替换
```

改成：

```python
def wsd_decay_lr(peak, min_lr, p, shape):
    p = min(max(p, 0.0), 1.0)
    if shape == "exponential":
        return peak * (min_lr / peak) ** p            # 纯指数：p=0→peak, p=1→min_lr
    if shape == "cosine":
        return min_lr + 0.5 * (peak - min_lr) * (1 + math.cos(math.pi * p))
    return min_lr + (peak - min_lr) * (1 - p)         # linear（旧行为，默认）
```

并在初始化日志里打印：`lr_decay_shape=<shape> peak=<peak> min=<min_lr> decay_iters=<decay>`。

## 3. 验收（必须做，否则等于没改）

**A. 单元级（10 秒）**

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 \
       --decay-iters 20000 --total-iters 1070000
```

D 段理论值（必须与训练日志/TB 一致）：

| D 段进度 p | step | 期望 LR |
|--:|--:|--:|
| 0.00 | 1,050,000 | 1.000e-3 |
| 0.25 | 1,055,000 | 5.623e-4 |
| 0.50 | 1,060,000 | 3.162e-4 |
| 0.75 | 1,065,000 | 1.778e-4 |
| 1.00 | 1,070,000 | 1.000e-4 |

**B. 冒烟级（~10 分钟，单机 8 卡）**

```bash
# 用极短的 decay 窗口验证形状：total=40, decay=20 ⇒ 第 21..40 步走 D 段
bash scripts/train.sh s1 --smoke 40 --dry-run     # 先看命令拼装
# 然后把 ITERS/decay 临时改成 total=40/decay=20 跑（或用下面的最小命令）
```

最小验证命令（单机 8 卡，20 步，只验证 LR 与 AdamW 不炸）：

```bash
cd /nas_train/app.e0031982/code/BaiZe-ISEDA2027
/nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nnodes=1 --nproc_per_node=8 \
  --master_port=29599 pretrain_launcher.py \
  --arch mamba2 --name lrprobe --dir /tmp/baize_lrprobe_exp \
  --tokenizer-path /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data/tokenizer_eod \
  --train-data-path "<1 个 shard 前缀>" \
  --train-iters 20 --global-batch-size 8 --micro-batch-size 1 --seq-length 16384 \
  --eval-interval 99999 --eval-iters 0 --save-interval 0 \
  --lr 1e-3 --min-lr 1e-4 --lr-warmup-iters 0 --lr-decay-iters 10 \
  --lr-decay-style WSD --lr-decay-shape exponential \
  --optimizer adam --seed 1234 --precision bf16_mixed --fp8-recipe tensorwise
```

判据：`/tmp/baize_lrprobe_exp/lrprobe/tb_logs/` 的 `learning-rate` 在第 10..20 步呈
**指数下降**（10→1e-3、15→3.16e-4、20→1e-4），且 `--optimizer adam` 生效、无 NaN。

**C. 与 TB 对账（正式跑后）**

```bash
# 从 TB 导出 csv（step, learning-rate）后：
python scripts/lr_schedule.py --peak 1e-3 --min 1e-4 --warmup 2000 \
       --decay-iters 20000 --total-iters 1070000 --tb-csv /tmp/lr_from_tb.csv --tol 1e-3
# ⇒ 打印「最大相对误差 ... PASS」
```

## 4. 回滚

改动只新增一个参数与一个分支；回滚 = `git -C /nas_train/app.e0031982/code/BaiZe-ISEDA2027 checkout -- <改动文件>`，
或直接不传 `--lr-decay-shape`（默认 linear，等价旧行为）。

## 5. 附：RoPE 参数（`--rotary-base` / `--max-position-embeddings`）

用户令 2026-10-26：56 层中 **4 层注意力**的 RoPE **max embedding position = 1M**。
本计划的实现口径 = **`rotary_base`（theta）1e6 + `max_position_embeddings` 1,048,576** 同时设置。

```bash
# 先探测
grep -rn "rotary_base\|rotary-base\|rope_theta" pretrain_launcher.py
python pretrain_launcher.py --help | grep -E "rotary|max-position"
```

- 若 `--help` 里**已有** `--rotary-base`：不需要改，`train.sh` 会自动传 `1000000`。
- 若没有：在 Megatron args 里补一个参数并透传给 transformer config：

```python
group.add_argument("--rotary-base", type=int, default=10000,
                   help="RoPE theta（ABF）。本项目正式训练 = 1000000")
# 透传
config.rotary_base = args.rotary_base
# 导出/推理侧（若 launcher 自己写 config）
config.max_position_embeddings = getattr(args, "max_position_embeddings", 4096)
```

**为什么必须两个一起改**：本项目 2026-10-06 的 B1 实验实测——
只把 `max_position_embeddings` 抬到 131072 而 `rope_theta` 仍是 1e4 ⇒ cos/sin 高频分量溢出
⇒ **全 NaN（连 4K 都 NaN）**；`ABF_1e6`（max_pos=1048576 + theta=1e6）才降到可用
（4K/128K/1M PPL 83.24/54.66/55.42）。
参见 `reports/report_pretrain_research4_longctx_1m_p8.html` §2.2、`run/baize_b1_longctx_extend.py`。

**验收**

```bash
# ① 启动命令里必须出现 --rotary-base 1000000（train.sh --dry-run 可看）
bash scripts/train.sh s1 --dry-run | tr ' ' '\n' | grep -A1 rotary-base
# ② 导出 HF config 后做结构校验（必须 PASS）
python scripts/check_rope.py --hf-dir <hf_dir>
# ③ 训练日志：前 500 步 loss 稳定、0 NaN；与 baseline 同时长对照抬升 ≤5%
```

> 训练期 RoPE 是逐位置计算的，`max_position_embeddings` 不影响显存/吞吐；它只在导出
> `config.json`（HF/SGLang）时生效，所以**训练能跑 ≠ 配置达标**，必须用 ② 卡口。

