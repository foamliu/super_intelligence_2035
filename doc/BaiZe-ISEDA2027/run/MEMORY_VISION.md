# MEMORY_VISION.md — BaiZe Stage(iii) 视觉编码器预训练 · 运行时状态

WAITING: 1

## 状态头

| 字段 | 值 |
|:---|:---|
| PHASE | **R10_active**（① 回收 stage-1 周期 ckpt IN-1k ✅ → ② 拟合二维 (N,M) scaling ✅ → ③ 补密 M 轴 **w384/w640 训练中**） |
| WAITING | 1（R10-③ 补密 M 轴训练后台运行：`r10_run_denseM.sh`，8 卡，ETL ~3.5h） |
| ERROR_COUNT | 1（R9 阶段一 w512 首跑 @~8900 步 crash：CC12M/Amshaker wds 含损坏 jpg → 已由 data.py `ignore_and_continue` 修复） |
| BUDGET_USED | R2–R9 累计 + R10（R10-① IN-1k ~1 GPU·h ✅；R10-③ w384+w640 在跑，详见 EXPERIMENTS_VISION_ROUND10.md） |
| 更新 | 2026-10-03（R10 ①② 完成、③ 触发启动；live MEMORY ≤32KB 已维持） |
| WINNER | OpenVision2（R8 六架构四指标第一；R9 选中 w512=126.8M 缩塔，不改架构排名） |

## R9 完成（converged）结论速查（2026-10-03，权威详见 EXPERIMENTS_VISION_ROUND9.md）

- **阶段一缩塔先导**（OpenVision2 × width{512,768,1024} × 30k，同 recipe/数据/batch512）：IN-1k lp = **6.10% / 3.63% / 1.03%**（zs 2.74/1.91/1.02）→ **塔越小每样本效率越高** → 选 **w512（126.8M）**。
- **阶段二**（w512 × 108k 步 = 55.3M 样本）：无坍缩（C1≈0.36 / C2_gap≈+0.10 / loss_ema 5.99→3.71，steady 2904 img/s）；IN-1k lp 峰值 **7.70%**@51.2M，zs top-1 3.59% / top-5 11.47%。
- **scaling 拟合**（11 点 R²≈0.94）：幂律 acc=0.251−0.864·N^−0.090（渐近 **25.1%**）；对数线性 acc=−0.229+0.0398·log10(N)。外推 20% 需 619 亿（对数）/ 41 万亿（幂律）样本 → **本地 53M 唯一对上限够不到 20%+**。
- **结论**：瓶颈在数据量与目标函数（AIMv2 ≈120 亿对，我们 649× 少），非架构。详见 EXPERIMENTS_VISION_ROUND9.md §4–§5。

## R10（2026-10-03）：补全 M 轴的 scaling law

> 运维指出 R9 只扫了数据侧 N（固定 w512），M 轴没做；R10 复用阶段一已落盘三档塔宽 ckpt 补 M 轴，拟合 (N,M) 二维 scaling law。

- ✅ **R10-① 回收 12 点 IN-1k 完成**：3 塔 × step{10k,20k,30k}，`r10_eval_stage1.sh` → `r8_eval_in1k.py --ckpts`（exit 0）。lp(w512/w768/w1024 @N=5.12/10.24/15.36M)：3.43/5.45/**6.08**%、1.14/2.03/**3.63**%、0.67/0.99/**0.93**%（证据 `/tmp/r10_stage1_in1k.log`）。
- ✅ **R10-② 2D 拟合完成（3 点 M 轴）**：`r10_scaling2d.py`，19 点 → 带交互 R²=0.980：`acc=-1.737+0.333·log10(N)+0.185·log10(M)-0.036·log10(N)·log10(M)`；M 边际效应**全区间为负** ≈ **−2.2 lp pp/参数翻倍**（无交互 c=−0.070，R²=0.975）。→ 数据受限区间**加宽塔是负收益**。
- 🔄 **R10-③ 已触发并启动**：M 轴太稀（3 点、无 <126.8M）+ 最优 M 落在观测下界之下 → `r10_run_denseM.sh` 训 w384(≈71M)+w640(≈197M) 各 30k 步（同数据 CC12M+Amshaker、同 recipe），完成后自动回收 8 ckpt IN-1k，拼 5 点 M 轴。
- **铁律**：不重跑阶段一训练；每条结论贴证据（命令 + 原始输出 + 路径）；不许猜。

### 🕐 本轮等待（WAITING=1）
- **等什么**：R10-③ 训练+自动评测（后台 `/tmp/r10_denseM.log`，10.239.2.12 全 8 卡）。
- **判结束**：`grep -c 'denseM ALL DONE' /tmp/r10_denseM.log` == 1。
- **收尾步骤**（下次唤醒先查是否 DONE，若 DONE 再执行）：① 从 `/tmp/r10_denseM.log` 取 w384/w640 的 8 个 [R8-IN1K] point + 实际 numel；② 用 5 点 M 轴 {71,126.8,197,284.5,505.2}M 重跑 2D 拟合（`r10_scaling2d.py` 需把 WIDTH_PARAMS 加入 384:70.8M/640:196.6M、WIDTH_RE 加 `R10_denseM_w(\d+)`，或用实际 numel）；③ 回填 `EXPERIMENTS_VISION_ROUND10.md` §2/§3/§4 最终值 + `EXPERIMENTS_VISION.md` 顶部 + 本状态头；④ git push。

## 历史条目已滚动归档（2026-10-03）

- 更早的全部巡检/流水（R1–R9 完整过程，live MEMORY 原 95.7KB）已滚动归档至 `daily-memories-vision/2026-10-03.md`（追加「滚动归档快照」）+ 各日期 daily 文件（2026-09-30 / 10-01 / 10-02）。live MEMORY 已压至 ≤32KB。
- 结论性产物（架构排名 / scaling / 回填建议）以 `EXPERIMENTS_VISION.md` 顶部与 `EXPERIMENTS_VISION_ROUND{2..9}.md` 为权威，不受滚动影响。
