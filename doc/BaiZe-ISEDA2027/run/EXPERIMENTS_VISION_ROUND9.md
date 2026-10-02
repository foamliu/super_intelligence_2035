# EXPERIMENTS_VISION_ROUND9.md — R9 数据扩容 + 长训练（scaling law 先导）

> 第九轮：把数据从 ~2.77M 对扩到 **~18.5M 对**（CC12M 11M + Amshaker 6M + 其他），
> 用「缩塔先导」找该数据规模下最合适的塔规模，再做长训练 + scaling 曲线 + 外推。
> recipe / 文本塔 / 目标函数一律不变（R8 已验证：冻结 CLIP-768 text + InfoNCE + lr 3e-3 / warmup 20 / bs64×8=512 负样本 / @224/16）。

- **状态**：🚧 阶段一（缩塔 3 臂 × 30k）**运行中**（首跑 crash 后已修复重启）。
- 更新时间：2026-10-02 10:30。

---

## 1. R9.0 所需时长估计（实测冒烟，非拍脑袋）

| 塔规模 | width(depth=30) | 参数量(实测) | 稳态 img/s (nw2) | 稳态 img/s (nw6) |
|:--|--:|--:|--:|--:|
| 小 | 512 | **126.8M** | 2321.6 | （未单测） |
| 中 | 768 | **284.5M** | 1975.6 | （未单测） |
| 大（R8 基线） | 1024 | **505.0M** | 2083.7 | **2826.9** |

- 🔑 CC12M+Amshaker 多源 pipeline 是**数据瓶颈**：nw2 三塔 ~2000–2300 img/s 几乎不随塔缩小而变快；nw6 把 w1024 拉到 2827 img/s（+36%）→ 用 nw6。
- **ETA ≈ 阶段一(3×30k)≈4.3h + 阶段二(1×108k)≈5.4h + IN-1k 评测≈1h ≈ 11h 总量级**（以实测吞吐精修为准）。

## 2. 🐛 阶段一首跑 crash 与修复（重要，2026-10-02）

### 2.1 crash 现象（证据 = `/tmp/r9.log`，备份 `/tmp/r9.log.crash_w512_*.bak`）

- `w512`（126.8M）首跑至 **~step 8900/30000** 崩，`[rank6]` 抛：
  ```
  webdataset.autodecode.DecodingError: Caught DecodingError in DataLoader worker process 4.
  PIL.UnidentifiedImageError: cannot identify image file <_io.BytesIO object ...>
  torch.distributed.elastic.multiprocessing.errors.ChildFailedError
  ```
- 影响：`r9_train.py` 只在循环末尾存 ckpt → 崩溃即全损；w512 首跑 8900 步健康轨迹（loss→4.4、C1≈0.35、C2_gap≈+0.095）**作废、无 ckpt**。
- 后续 w768 也会在同点崩（shard 序确定），stage1 脚本 `run_one` **不查 exit code**，静默续跑 → 必须重启。

### 2.2 根因 + 修复

- 根因：CC12M / Amshaker wds shard 含**损坏 .jpg**；`data.py build_loader`（wds 路径）`.decode('pil')` 无脏图容错。
- 修复 ①（`data.py`）：`.decode('pil', handler=wds.ignore_and_continue)` + `.map(..., handler=wds.ignore_and_continue)`。
  - ⚠️ 实测发现：webdataset **1.0.2** `handler` 是**逐 stage** 默认参数，`WebDataset(handler=...)` 构造器传参**不传播** → 必须传在 `.decode/.map` 上。
  - 选 `ignore_and_continue`（静默跳过）而非 `warn_and_continue`（含 `time.sleep(0.5)`/样本）。
  - 实测：`/tmp/test_wds_fix.py` → `[num_workers=0/1] yielded 2 samples`，坏图跳过不崩。
- 修复 ②（`r9_train.py`）：加 `--save-every`（默认 10000）周期存 `vision_step{N}.pt`（防再被单张脏图全毁 + 供阶段二 scaling 曲线）。

## 3. 阶段一矩阵（缩塔先导，运行中）

OpenVision2（depth=30）× width ∈ {512, 768, 1024} × 30000 步，同 recipe / 同数据 / 同 batch(512)。

| 臂 | width | 参数量 | 步数 | loss | C1 | 吞吐 | IN-1k zs / lp | 状态 |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| a | 512 | 126.8M | 30000 | 待回收 | 待回收 | 待回收 | 待回收 | 🔄 重跑中 |
| b | 768 | 284.5M | 30000 | 待回收 | 待回收 | 待回收 | 待回收 | ⏳ 排队 |
| c | 1024 | 505.0M | 30000 | 待回收 | 待回收 | 待回收 | 待回收 | ⏳ 排队 |

> 首跑 w512 健康轨迹（已作废，仅供对照）：~step 8900 loss_ema≈4.49、C1≈0.35（健康无坍缩）。

## 4. 阶段二（待阶段一选定塔后启动）

- 选定塔 × 108000 步（≈18.5M 对吃 ~3 epoch），每 10k 步存 ckpt（11 点），每个 ckpt 测 IN-1k zs + lp。
- 产出：scaling law 曲线（log-x：累计样本数 → IN-1k lp top-1）+ 外推（20/40/60% 需多少样本）+ 与 AIMv2（12B 对）量级对照。

## 5. 待办 / 备注

- **论文回填建议**：`6_vision_encoder.tex` 写数据来源时注明「CC12M 11M + Amshaker 6M，webdataset，含少量损坏 jpg 已由 loader 容错跳过」。
- ⚠️ IN-1k 与 en500k 同源问题沿用 R8（§6 #16 污染核查），R9 用 CC12M+Amshaker（非 ImageNet 域）→ 更干净 out-of-domain。
- 未改 `*.tex`；未碰 pretrain/data/ops 文件。