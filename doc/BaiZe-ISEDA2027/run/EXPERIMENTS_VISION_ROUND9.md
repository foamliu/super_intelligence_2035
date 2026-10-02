# EXPERIMENTS_VISION_ROUND9.md — R9 数据扩容 + 长训练（scaling law 先导）

> 第九轮：把数据从 ~2.77M 对扩到 **~18.5M 对**（CC12M 11M + Amshaker 6M + 其他），
> 用「缩塔先导」找该数据规模下最合适的塔规模，再做长训练 + scaling 曲线 + 外推。
> recipe / 文本塔 / 目标函数一律不变（R8 已验证：冻结 CLIP-768 text + InfoNCE + lr 3e-3 / warmup 20 / bs64×8=512 负样本 / @224/16）。

- **状态**：✅ 阶段一完成（缩塔 3 臂 × 30k + IN-1k 全收齐）→ **w512（126.8M）胜出** → 🚧 阶段二 w512 × 108k 步运行中（16:38 启动）。
- 更新时间：2026-10-02 16:45。

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

| 臂 | width | 参数量 | 步数 | loss(ema) | C1 | 吞吐(img/s) | IN-1k zs top-1/5 / lp top-1 | 状态 |
|:--|--:|--:|--:|--:|--:|--:|--:|:--|
| a | 512 | 126.8M | 30000 | **4.0496** | **0.3502** | 2938.6 | **2.74% / 9.25% / 6.10%** 🥇 | ✅ 完成 |
| b | 768 | 284.5M | 30000 | **4.0448** | **0.3813** | 2978.2 | 1.91% / 6.57% / 3.63% | ✅ 完成 |
| c | 1024 | 505.0M | 30000 | **4.9200** | **0.3700** | 3461.5 | 1.02% / 3.98% / 1.03% | ✅ 完成 |

> w512 终值（证据 = `R9_stage1_w512/train.log` 末行 & `/tmp/r9.log`）：
> `final_loss=4.0496 (ema)` / 末 PROBE `C1=0.3502, C2_gap=+0.1079, C4=OK` / `steady_image_s=2938.6` /
> 总 6948.1s。4 ckpt（step10000/20000/30000 + final）全落盘，各 507MB。
>
> w768 终值（证据 = `R9_stage1_w768/train.log` 末行 & `/tmp/r9.log`）：
> `final_loss=4.0448 (ema)` / 末 PROBE `C1=0.3813, C2_gap=+0.0939, C4=OK` / `steady_image_s=2978.2` /
> 总 6880.8s。4 ckpt（step10000/20000/30000 + final）全落盘，各 1.14GB。
>
> ✅ **IN-1k 最终裁决（阶段一主指标，证据 = `/tmp/r9.log` IN-1K 段 16:16:25→16:29:27，各 ckpt = `R9_stage1_w*/vision.pt`）**：
> - **w512 (126.8M)**：zs 2.74% / top5 9.25% / **lp 6.10%** 🥇
> - w768 (284.5M)：zs 1.91% / top5 6.57% / lp 3.63%
> - w1024 (505.0M)：zs 1.02% / top5 3.98% / lp 1.03%
>
> **→ 选 w512（126.8M）为阶段二塔。** 结论单调且干净：**塔越小、每样本效率越高**（lp 6.10% → 3.63% → 1.03%），
> loss 也同步变差（4.05 → 4.04 → **4.92**），w1024 loss 反而最高 —— 在 ~15.4M 样本下 505M 严重**欠拟合**
> （样本/参数 ≈ 0.03），126.8M 才是适配这个数据量的塔。这与 R9.3 阶段一的「样本/参数失衡」动机完全吻合。
> ⚠️ **趋势单调向下**：可能更小的塔（如 w384≈71M）会更优，但 R9.3 阶段一只设 3 臂，w512 已是其中最优；
> 是否下探更小塔记为**后续可选（R10）**，本轮按任务书直接进阶段二。

> 首跑 w512 健康轨迹（已作废，仅供对照）：~step 8900 loss_ema≈4.49、C1≈0.35（健康无坍缩）。

## 4. 阶段二（🚧 运行中：w512 × 108k 步，2026-10-02 16:38 启动）

- **选定塔 = w512（OpenVision2 depth=30，126.8M）**；命令 `bash r9_run_stage2.sh 512 108000 6`。
- 首次启动证据（`/tmp/r9_stage2.log`）：`[params] tower=openvision2 total=126.8M`、
  `[start] steps=108000 shards=419/rank bs=64 world=8 negatives=512`；首步 loss 5.68 → 5.14（健康下降）；
  GPU 0–7 8×~16.3GB、100% util。
- 每 10k 步存 ckpt（10 个周期 + 终 `vision.pt` = 11 点），每个 ckpt 测 IN-1k zs + lp → scaling 曲线。
- **ETA**：w512 稳态 ~2939 img/s → 108000×512/2939 ≈ **5.2h** 训练 + 11 ckpt IN-1k 评测 ~0.7h ≈ **~6h → ~22:45 完成**。
- 产出：scaling law 曲线（log-x：累计样本数 → IN-1k lp top-1）+ 外推（20/40/60% 需多少样本）+ 与 AIMv2（12B 对）量级对照。
- ⚠️ 已 CPU 预验证 wds 多 epoch 重迭代（`iter(loader)` 二次可用：nw0 [5,5]、nw2 [4,4]）—— 108k 步 ≈ 3.3 epoch 无 StopIteration 风险。

## 5. 待办 / 备注

- **论文回填建议**：`6_vision_encoder.tex` 写数据来源时注明「CC12M 11M + Amshaker 6M，webdataset，含少量损坏 jpg 已由 loader 容错跳过」。
- ⚠️ IN-1k 与 en500k 同源问题沿用 R8（§6 #16 污染核查），R9 用 CC12M+Amshaker（非 ImageNet 域）→ 更干净 out-of-domain。
- 未改 `*.tex`；未碰 pretrain/data/ops 文件。