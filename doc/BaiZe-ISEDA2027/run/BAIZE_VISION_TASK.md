# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

### 🆕 运维指令 · 2026-10-10（🧭 **外部评审回应：③口径修订 → ①同模型 zs → ②probe 对照 → ④epoch 缩放**）· 用户直令 · **最高优先**

> **用户令（2026-10-10 晚）**：外部评审质疑 **`E1fair` ProtB = 62.34% 偏低**；经两轮辨析，**一致口径 = 按 `③ → ① → ② → ④` 顺序下发**（收**回参照系**，不再用外部不可比数字）。

**③ 口径修订（**先做 · 零 GPU**）**
- 本线**所有**报告/口径（先 `report_vision_scaling_fair.html`）：凡出现**绝对 lp**，必须标注 **"BaiZe internal protocol (ProtB)"**，并**显式声明不可与外部数字同表**，原因逐条写清：**目标函数**（AIMv2-style `InfoNCE + 1.0×masked-patch-MSE`）≠ CLIP(对比) ≠ MAE/DINOv2(纯视觉自监督)；**数据**（图文对 **95.8M**、**1 epoch**）≠ LAION-2B(多 epoch/batch32k) ≠ IN-1k/LVD-142M；**文本塔冻结**；**协议** ProtA/B 相差 ~10pp。
- 新增一节 **「参照系说明」**：**只有「同目标 + 同数据量级 + 同 epoch + 同协议」的（内部）基线才可直接比较**。
- **清理**：凡此前出现的外部数字比较（CLIP zs / OpenCLIP / MAE / DINOv2）→ **加不可比标注或删除**。

**① 同模型 zero-shot（回答「特征有没有从文本对齐获益」）**
- 用**本模型自己的** IN-1k **zero-shot**，再做 **同模型 `lp` vs `zs`** 对照。**须说明构造**（走哪条通路：冻结 CLIP-768 文本塔 / InfoNCE 头 / CoCa / AR 解码器；给出精确用法与类名 prompt 策略）。
- 产出：**同模型 `lp / zs` 表（ProtB，3 seeds）**。
- 构造上做不到（如对比头与文本塔空间不对齐）→ **如实报** + 说明障碍与替代。

**② 更强 probe 对照（分离「特征差」vs「探针欠拟合」）**
- **同一 ckpt** 上加：**k-NN probe** · **更长 probe 步数**（如 ×5）· **wd / LR 微扫**。
- 产出：**lp 随 probe 配置变化表** ⇒ 若显著抬升 ⇒ **探针仍欠拟合**（真实特征质量 > 当前读数）。

**④ epoch 缩放点（**最有决策价值**）**
- **同数据、同目标、同协议、同 schedule**：在 `E1fair` 基础上补 **2 epoch**（必要时 **4 epoch**），画 **lp vs epoch** 曲线。
  - 若 2 epoch **显著抬升**（如 ≥70%）⇒ **62.34% 是预算不足**；
  - 若 4 epoch 仍 ~63% **横盘** ⇒ **特征/目标函数问题**。
- ⚠️ 与在飞的「变体实验」**共用 `.12` 8 卡** ⇒ **排期协调**；**先出 2-epoch 一点**再定是否上 4。

**优先级 / 排期**：**`③①②` 立即可做**（零/轻 GPU，**不占 8 卡训练**）；**`④` 与「变体实验（①Muon → ②全量数据）」统一排 GPU 档期**。
**产出**：③ 改后口径节（贴 diff 摘要）+ ① 同模型 `lp/zs` 表 + ② probe 对照表 + ④ `lp–epoch` 曲线（先 2 ep）。
**边界**：🚫 **不改已发布的实验数值**（只加标注/口径）；🚫 **不放弃在飞变体实验**。

### 🆕 运维指令 · 2026-10-10（🧪 **变体实验：① 优化器 AdamW→Muon → ② 全量数据 GPIC+CC12M+Amshaker；③ 分辨率暂缓**）· 用户直令 · **最高优先**

> **用户令（2026-10-10 晚）**：「vision：**用 `E1fair`(w512) 做 baseline** 做下列几组实验：**① 224→336 分辨率/patch token 消融**；**② 优化器 adamw → `dist_muon`**；**③ GPIC 已下载完，用全量数据**。因为 **baseline `E1fair` 已存在，因此只需跑三个变体**。」

**① Baseline（已存在，🚫 不重跑）**
- `E1fair` = OV2 **w512**/d30 · **224/p16** · from scratch · **187,101 步** · `lr=5e-4` / `warmup=2000` / **cosine** / `min_lr=5e-5` · 冻结快照 `total_shards=10787`。
- Baseline 指标：**ProtB lp = 62.34±0.01%**（3 seeds）· ProtA = 49.70%。
- **判据（预注册）**：各变体 vs baseline 的 **Δlp（Protocol B，3 seeds）**；**|Δlp| < 1.5pp 判「不可分辨」**（沿用既有口径）。

**② 执行次序与变体（用户 2026-10-10 晚调整）** —— **先 `1`（Muon）→ 再 `2`（全量数据）；`3`（分辨率）暂缓**。各 1 臂；除被检验的单一变量外，与 baseline 逐字节相同。

1. **V1 · 优化器：AdamW → Muon**【**本轮第一优先** · 原 V2】
   - 🔎 **框架事实（运维已核实 · 用户 2026-10-10 追问）**：`r9_train.py` = **纯 PyTorch DDP**（`dist.init_process_group('nccl')` + `torch.nn.parallel.DistributedDataParallel` + `torch.optim.AdamW`；`python -m torch.distributed.run --nproc_per_node=8`）—— **不是 Megatron-LM / NeMo** ⇒ **没有现成的 `dist_muon` 开关**（`dist_muon` 是 **Megatron-Core** 的 layer-wise distributed 优化器，vision 栈里不存在）。
   - ✅ **但 Muon 无需自行实现**：**直接用上游 `emerging_optimizers`**（`pip install emerging_optimizers`；**Megatron-Core 的 `core/optimizer/muon.py` 就是它的 shim**）接入 `r9_train.py`（torch.optim 风格 API）。**参考 pretrain 最近的 dist_muon 实验**：`run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md`「**dist_muon 实测验证（三路对比）**」节 · `doc/BaiZe-ISEDA2027/report_pretrain_muon_vs_adamw.html §8`。
   - **超参基线（照 pretrain）**：Muon = `momentum=0.95` / **nesterov** / `ns_steps=5`；AdamW 对照 = `β=(0.9,0.95)`、`ε`、`wd=0.1`（`r9_train.py` 现值 `betas=(0.9,0.95), eps=1e-6`）。
   - **LR**：pretrain 的 `dist_muon` **沿用与 AdamW 相同的 `lr=1e-3`（未单独扫 LR）** ⇒ vision **可先沿用 `lr=5e-4`**；但**仍做小规模 lr 探针**（如 ~200–500 步 ×2 点）作保险，loss 轨迹异常再扫；**记录探针协议**。
   - ⚠️ **「layer-wise distributed `dist_muon`」的严格语义**（整层分给各 DP rank、正交化与梯度同步重叠）**在纯 DDP 下拿不到**；若必须复刻该语义 ⇒ 需把该臂**迁到 Megatron-Bridge 栈**（成本大）。
   - ➡️ **本轮执行口径（用户 2026-10-10 确认「好的」）**：**V2 按 (A) 库级 Muon 执行** —— 即 **`emerging_optimizers` 接入现有 DDP trainer**；**(B) 严格 `dist_muon` 本轮只报「可行性 + 成本」**，🚫 **不实施**（待运维拍板再定）。
2. **V2 · 全量数据：`GPIC 全量` + `CC12M` + `Amshaker`**【原 V3 · 扩展 · **本轮第二优先**】
   - **数据构成（用户令）**：**GPIC 全量**（train 8000 + val 32 + test 128）**＋ `CC12M` ＋ `Amshaker`**。**逐项列明各子集规模**（样本数 / tar 数 / 字节），并与 baseline 的 `total_shards=10787` 快照做**对比表**。
   - **步数按数据量计算**（用户令，**允许 > 187,101**）：**给出公式与代入值** —— 例如 `steps ≈ ⌈(总样本 × epoch) / (MBS × world_size × grad_accum)⌉`，并说明所取 `epoch` 数及其依据。
   - ⚠️ **披露**：本臂相对 baseline **同时变了「数据量」与「步数」** ⇒ 结论只能表述为「**全量配方（数据+步数整体） vs baseline**」，🚫 **不得表述成「纯数据消融」**；若成本允许，**可选**附一条**同步数（187,101）对照**做部分归因。
3. **V3 · 分辨率 224 → 336**：⏸ **暂缓（用户 2026-10-10：「明天再说」）** ⇒ **本轮不跑**。
   - （设计备案：保持 **p16** ⇒ patch 数 196→**441**；pos-emb 重建；**≈2.25× 计算 / ~20h**；若认为 **p14@336=576 token** 更合理须说明理由。）

**③ 执行要求**
- **预注册先行**：每变体的**臂定义 / 判据 / 阈值**先写入 `EXPERIMENTS_VISION.md` 新节（**结果后填**）。
- **公平性**：除单一变量外，**其余（步数/schedule/seed/评测协议/数据快照）必须与 `E1fair` 一致**。
- **空间**：`.12` 8 卡（已释放）；**默认串行跑 3 臂**（除非卡数/显存允许并行且不互相污染）。
- **成本**：逐臂报 **GPU·h + 墙钟**（V1 ≈2.25× 计算量）。
- **报告**：跑完出**自包含 HTML**，含**各变体 vs baseline 的 Δlp + 「是否可分辨」结论**。

**④ 产出**：本块下贴 —— 预注册（臂/判据）+ 各臂 `lp ProtA/ProtB（3 seeds）` + **Δlp vs baseline 对照表** + 成本。

> 📦 §运维征询 · 2026-10-10（下一步工作建议）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：已回答 → MEMORY_VISION.md「运维问答 · 2026-10-10」节。建议含 Stage(iv) MLLM 对齐、w384、C1-lp trade-off、336 分辨率、论文呈现等。需要时再读。

> 📦 §运维指令 · 2026-10-10（📄 Scaling fair rerun 成果报告 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：`report_vision_scaling_fair.html`（36.7KB）已交付，Δlp=+0.17pp 不可分辨，⛔ 横幅已加。需要时再读。

> 📦 §运维指令 · 2026-10-10（📄 昨夜工作汇报 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：`report_10_09_vision_overnight.html`（61.9KB）已交付，含 E1fair/E2fair 全程+最终 Δlp=+0.17pp。需要时再读。
> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_VISION.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_VISION.md` / `EXPERIMENTS_VISION*` / `daily-memories-vision/` / `vision/`）。⚠️ **唯一例外（2026-10-06）**：按「📉 体积维护规程」，agent **可把「已闭合」的运维块/旧正文【原文】搬入** `run/ARCHIVE_OPERATOR_VISION.md`（**只搬迁、留 1 行指针**；不新增/不改写任何指令）。

---

> 📦 §运维指令 · 2026-10-09⑨（🔁 公平性重跑）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：E1fair(62.34±0.01%) vs E2fair(62.51%)，Δlp=+0.17pp 不可分辨；旧「Bigger is WORSE −5.59pp」= schedule 伪影；`r9_train.py` cosine/min-lr 已加；两臂同一冻结快照 total_shards=10787。需要时再读。

---

> 📦 **2026-10-08⑥（E2 变更：作废官方 OV2 L/14@336 → w768/d30）已归档** → `ARCHIVE_OPERATOR_VISION.md`。**结论**：E2(w768/d30,284.54M) 已跑完+eval；配方公平性已被 2026-10-09⑨ 定性问题。需要时再读。


> 📦 **2026-10-08⑤（缩放对比实验）已归档** → `ARCHIVE_OPERATOR_VISION.md`。**结论**：E1(w512) vs E2(w768/d30) Δlp=−5.59pp，但建立在 `--lr 3e-3 --warmup 20`（warmup≈0%）上 ⇒ 公平性存疑，结论已作废 → 见 2026-10-09⑨ 公平重跑。需要时再读。


### 🆕 运维指令 · 2026-10-08④（📐 **回答：用「现有全部数据（含 GPIC 6167/8001）」训练 1 epoch 需要多久**）· **用户直问** · 高优先

> 📦 §运维指令 · 2026-10-08④（📐 全量 1-epoch 耗时估算）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：已用 scaling smoke 实测回答（E1=4697 img/s → 5.66h；区间 5.2–9.1h/epoch；1 epoch 足够）。需要时再读。


### 🏆 最佳实践（BEST PRACTICES）— **2026-10-08 锁定 · 如无特殊指定，一律按此执行**

> 以下三项由 R2–R14 全线实验**预注册 + 收敛**后裁定，证据见对应报告/实验记录。
> **默认执行**：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> **不得回退**：禁止在未经运维明确批准的情况下，使用以下已被实验否定的旧配置。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| **损失** | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| **文本塔** | 冻结 CLIP-ViT-L/14-336（768-d），**不**解冻 / **不**用 LoRA |
| **注意力** | **双向**（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| **证据** | R11-G：lp 7.40% → **19.76%**（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 **20.27%** |
| **否决项** | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| **报告** | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | **0.6** | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | **1.0 / 1.0**（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | **SGD + momentum 0.9 + cosine**（5-ep warmup） |
| Batch size | full-batch（49,970） | **mini-batch 1024** |
| Epochs | 100（= 100 次梯度更新） | **90**（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | **IN-1k full train = 1,281,167 张** |
| Eval 集 | 自切分 val（50/类 = 5,000） | **IN-1k 官方 validation（50k）** |
| Normalization | CLIP mean/std | **ImageNet mean/std** |
| 重复 | seed 0 单次 | **3 seeds（0,1,2）→ mean ± σ** |
| **证据** | Δlp ≈ **+10.05 pp**（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| **内部横比** | 旧实验（R2–R14）均用 Protocol A，相对排序**仍有效**（A/B 排序一致）；但**绝对数字**须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；**与 DINOv2/MAE/iBOT 等公开值可直接横比** |

> ⚠️ **Protocol A → B 迁移说明**：旧实验的**相对结论**（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，**不混表**。

---


> 📦 §运维指令 · 2026-10-08①（📝 更新论文 LaTeX）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：6_vision_encoder.tex 已更新（mask-ratio 表 + weight-ratio 表 + §VI-D AR 范式探索），main.pdf 11p 0err，commit 6f2baa2b。需要时再读。

> 📦 §运维指令 · 2026-10-08②（📄 全线总结报告 HTML）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；**结论**：report_vision_encoder_final.html（28.6KB, 10 节/4SVG）+ report_vision_final_20261008.html（v2 最终版）已交付，commit 67a306f8。需要时再读。

> 📦 §运维指令 · 2026-10-07③（mask-ratio 消融报告 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_mask_ratio.html 已交付（34.3KB, 8节+2SVG, 倒U形 0.6 最优, commit ee9db3ca）。需要时再读。

> 📦 §运维指令 · 2026-10-07②（GPU12 对账簿）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：pretrain 借 GPU1–7 跑完长上下文成本矩阵后 09:44 已归还，GPU12_ALLOC.md 已建。需要时再读。

> 📦 §运维指令 · 2026-10-07（📊 昨夜工作汇报 HTML）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_10_07_vision_overnight.html 已交付（自包含 27.7KB，内联 SVG，零外部依赖）。需要时再读。

> 📦 §运维指令 · 2026-10-08③（💬 下一步工作建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：4 题已答（未验证假设/Stage iv 前置/GPU 利用/论文补充），写入 MEMORY_VISION.md「运维问答」区，commit 0bb4dc24。需要时再读。


> 📦 §运维指令 · 2026-10-06（✅ 批准 AIMv2 官方 AR 范式 + 6 点修订）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：6 点修订已落实，Arm A baseline lp=13.49% 最优 / Arm B pure AR 坍缩@step600 / Arm B-hybrid lp=1.37% Δ−12.1pp，report_vision_aimv2_official_vs_ours.html 已交付。需要时再读。


> 📦 §运维指令 · 2026-10-06（📋 vision 后续队列裁定）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：队列全部完成（① lp 协议 A/B → ② mask-ratio 5 臂 0.6 最优 → ③ weight-ratio 4 臂 1:1 最优 → ④ 官方 AIMv2 AR Arm A/B/B-hybrid）。方向 1 待 GPIC 下载；方向 4 已作废。需要时再读。


> 📦 §运维指令 · 2026-10-06（🔬 lp 评测协议与主流对齐研究）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_lp_protocol.html 已交付（21.2KB, 2026-10-07）。需要时再读。


### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**（「收尾铁律」第 0 步已同步此判据）。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）**原文**搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `vision 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**24KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，**优先滚它**）。


### 🧭 收尾铁律 · 2026-10-06（**用户指令 · 每轮唤醒必须执行，不许省**）

> **为什么新增（真实事故）**：2026-10-06 06:55 → 08:30，**data 线心跳文件 `MEMORY_DATA.md` 近 2 小时未更新**（其间 agent 在改别的文件、push 得出去），**外部运维只能靠 git 判断死活** ⇒ 被**误判成静默卡死并上机排查**。
> 根因：**「更新记忆 + push」以前只是建议、没有硬约束**；loop 的兜底 push 间隔是 **5h**（本日已缩短），且只覆盖固定白名单 —— **不许依赖兜底**。
> 🚫 **旧口径（已废）**：「每 5 小时由 loop 兜底 push 一次」**不再作为交付保障** —— 兜底只是保险丝，**不是你的提交手段**。

**每轮唤醒（一次 cline 会话）结束前，按顺序做完这 5 件事，再置 `WAITING` / 去睡：**

0. **体积自检（先跑，数字要抄进下一步的心跳）**：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   for f in doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md; do
     printf '%-46s %7s B\n' "$f" "$(wc -c < "$f")"; done
   ```
   判据：两者都应 **≤ 32KB**；**任一 > 32KB ⇒ 本轮收尾前【你自己】滚动归档**（见本文件「📉 体积维护规程」：只把**已闭合**内容**原文**移入 `run/ARCHIVE_OPERATOR_VISION.md`、留 1 行指针），直到两者都 ≤ 32KB；**> 40KB（红线）⇒ 必须先归档再提交**（不许只上报等运维）。
   收尾把两文件体积 + 本轮归档量抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_VISION.md）`。去向/指针格式见本文件「📉 体积维护规程」。

1. **写心跳**：更新 `run/MEMORY_VISION.md` 顶部进度快照（`PHASE` / `WAITING` / `已完成` / `当前动作` / `下一步` / `阻塞`），并**追加 1 行「本唤醒流水」**：`[HH:MM] 干了什么 + 关键原始输出 1–2 行`。
2. **写日报**：`run/daily-memories-vision/<YYYY-MM-DD>.md` 追加本轮记录（**当天文件必须建**）。
3. **自己提交 + 推送**（**不许等 loop 兜底**）：
   ```bash
   cd /nas_train/app.e0031982/code/super_intelligence_2035
   git add -- doc/BaiZe-ISEDA2027/run/MEMORY_VISION.md doc/BaiZe-ISEDA2027/run/EXPERIMENTS_VISION.md \
              doc/BaiZe-ISEDA2027/run/BAIZE_VISION_TASK.md \
              doc/BaiZe-ISEDA2027/run/daily-memories-vision doc/BaiZe-ISEDA2027/run/vision
   git commit -m "vision <轮次>: <一句话>"      # 🚫 提交信息必须带线名前缀，否则运维无法溯源
   git push origin main
   ```
   🚫 **绝不用 `git add -A`** —— 这是**共享工作副本**，`-A` 会把别线尚未完成的在途文件一并卷进你的提交（10-05 已出事故：`restore other agents files from dropped auto-commit`），后果是**提交归属不可溯**（运维查不出谁在干活）。
4. **闭环自检**：`git status -sb` ⇒ **无 ahead / 无 behind**；`git log -1 --format='%h %ad %s' --date=format:'%H:%M'` 的时间戳 = 本轮。
   **push 失败（`error: Forbidden` / 网络）**：重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下一轮唤醒第一件事就是补推**。

> ⏱️ **运维判死判据（硬）**：**心跳文件 >60 min 无新提交 ⇒ 按卡死处理**，**不再等你**。**你干得再多，心跳不动 = 仍会被判死。**

### 0. 🎯 当前状态速览（**每次唤醒先看这里**）

| 项 | 值（**2026-10-05 晚 运维更新**） |
|:--|:--|
| **GPU 状态** | 🚀 **R12 全量数据 AIMv2 训练中**（`.12` 8 卡，120k 步，16:43 起；吞吐随 NFS 争用波动 ~2300–5600 img/s）· **3-epoch 续跑 watcher 已就绪**（R12+eval 完自动接续）· 另有 **两份 HTML 报告**（纯 CPU/写作）待写 |
| **已完成** | ✅ R9/R10/R14/E1/R11-L 四臂/R11-L2/caption-weight/R11-E/R13（官方 OV2 **79.81%**）· ⭐ **臂⑥ AIMv2 翻盘**（lp 12.08% vs 6.08%，**+6.00 pp → 25.1% 局部推翻**）· ✅ **R11-F 五臂**（A/B/C/E/D）· ✅ **R11-G**（108k 长跑：lp@55.3M **19.76%** vs 基线 7.40%，幂律 **R²=0.91**）· ✅ **R11-H**（纯 AR **无翻盘** ⇒ 翻盘依赖对比项） |
| **🔜 下一步（✅ 已批准 · 严格按此顺序）** | 🔒 **①先「AIMv2 提速」**（归因实测 → 数据管线优化，见「运维前置」块）→ **②再用「全部现有数据」（GPIC ≈41% + CC12M + Amshaker ≈59.5M 对）跑 AIMv2**（先交**提速后**的「时长 / epoch」估算）→ **③训练稳态后自改论文 §6**（可用 `cimi_search`，仅该段解冻） |
| **可立即开跑** | ✅ **① AIMv2 提速（归因实测 + 数据管线优化）** —— `.12` 8 卡已空；**② 全量训练须待 ① 完成**（硬性前置） |
| **🚫 已裁定不做** | **臂⑤ GenLIP**（→ 用 `caption-loss-weight` 三点消融替代）· **R12 iGVLM / TuringViT**（无官方仓库，取消） |
| **⏸ 暂缓** | 无 —— 原「GPIC 到齐后重跑 scaling」已被用户**改为「用现有全部数据直接跑」**（见新块）；`R13` 已完成 |
| **叙事** | ✅ **锁定 A = 从零训练**（不改用预训练权重） |

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。


> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（**一次性质，对所有 R 生效**）


- 🚫 **不许闭门造车**：涉及"别人怎么做"（架构/loss/评测/数据）**必须去读官方仓库或论文原文**（能 clone 就 clone）—— **不得凭二手描述下结论**（本线已因此出错一次）。
- **不重跑已落盘训练**；**不改 R8/R9/R10 已落盘结论**（只在 §2 明确"修正"条目下补限定）。
- **控变量**：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- **公平性**：加 decoder 的臂**必须报「参数量 + 训练 token + 每步耗时」**，不许只比 acc。
- **预注册**：判据**先定后测**，不许事后改。
- **体积**：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` **各 ≤32KB**（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列（**按优先级；不要跳序、并行不超过 2 项**）

| 序 | 任务 | 类型 | 前置 | 状态 |
|:--|:--|:--|:--|:--|
| **1** | **R14 官方仓库资源调研** | 调研 · 纯 CPU | — | ✅ **已完成** |
| **2** | **E1 GPIC 规模实测** + **R11-E 数据轴** | 轻(测) / **训** | 抽 tar | ✅ **E1 完成**（GPIC 全量 ≈**100.3M**）· 🟢 **R11-E 已批准 · 即刻执行**（「10.9M 同 N 两点」版，见上「运维指令 · 2026-10-04（四）」） |
| **3** | **R11-L loss 轴** | GPU | R14 完成 | ✅ **四臂全兑现、无一翻盘**（①基线 ②SigLIP ③LocalLoss ④CoCa） |
| **4** | ⭐ **R11-L2 文本塔解冻（LoRA/Adapter）** | GPU | — | 🟢 **已批准 · 下一优先级 · 立即执行**（见上「运维指令 · 2026-10-03（三）」） |
| **5** | 🆕 **`caption-loss-weight` 三点消融**（替代臂⑤ GenLIP） | GPU · 轻 | **R11-L2 之后** | 🆕 **已排期**（0.5 / 1.0 / 2.0，≈0.5–1 臂） |
| **6** | **R13 官方 vs 自研对照** | GPU · 轻 | ✅ **已批准** | ✅ **完成**（2026-10-04：官方 OV2 L/14@224 同口径 IN-1k lp=79.81% vs 自研 7.99%，补结论边界） |
| **7** | **臂⑥ AIMv2 式（patch + text 双 AR）** | GPU · 重 | **R11-L2 结果** | ⏸ **暂缓** |
| **8** | ~~**R12 iGVLM 指令条件化**~~ | — | — | ❌ **已取消**（**无官方仓库** → 不值得自研） |
| **9** | 🆕 **R11-F 数据源横向对比（含 GPIC caption 粒度轴）** | GPU | — | 🟢 **已批准 · 立即执行**（GPIC `short`/`medium`/`short+medium`(90%) vs en500k vs CC12M；见「运维指令 · 2026-10-04（六）」） |
| **10** | 🆕 **R11-G — AIMv2 长跑（108k 步）→ 重拟合 scaling 并外推** | GPU | R11-F | 🟢 **已批准**（见「运维指令 · 2026-10-04（七）」） |
| **11** | 🆕 **R11-H — 臂⑥-B 纯 AR（去对比项）** | GPU | R11-G | 🟢 **已批准**（同上） |

> **已合并（不再单列）**：**「R11-L3 读 OpenVision 官方代码」→ 并入 R14**；**「R11-D 的先验证 GPIC tar」→ 并入 E1/C1**。

---

### 5. 📚 背景参考（**输入素材，不是任务**）

- **`run/VISION_ARCH_FRONTIER_2026.md`** —— 2026 前沿架构调研（iGVLM / TuringViT / MambaEye / MoE-ViE / FastVLM）+ **与 R8 的逐项对照** + **§5 数据量口径错误更正**。
- **关键事实速查**：
  - R9 lp 渐近 **25.1%**（幂律 `acc=0.251−0.864·N^−0.090`，R²≈0.94）· 当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结 CLIP-768 文本塔 + InfoNCE**。
  - R10-② 二维拟合（3 点 M 轴）：**M 边际效应全区间为负**（≈ −2.2 lp pp/参数翻倍）→ 数据受限区间**加宽塔是负收益**。
  - `attention flash` 仅占 GPU 自耗 **0.7%**（P-4）· 分辨率 **224/16**。
- **已核实官方资源**（运维 2026-10-03）：
  - `UCSC-VLAA/OpenVision`（**Apache-2.0**；**同时支持「对比+生成」与「caption-only」两套目标**；**2026-08 已放出 decoder**；训练栈 **TPU/JAX**，PyTorch 侧基于 OpenCLIP fork）。
  - `apple-aiml-research/ml-aim`（**AIMv2-L 0.3B = 87.6% 冻结 trunk / 77.0% LiT zero-shot**；代码与权重均已发布；LICENSE 待逐字核实）。
- **数据侧硬约束（机制推断，⚠️ 须 R11 实测验证，不得当结论引用）**：我们 caption **偏短**（CC12M = alt-text 短句 / Amshaker = 中长 / GPIC short = 20 tok），官方用 **ReCap-DataComp-1B v2 的 LLaMA-3 长合成 caption** → **caption-only 生成式的监督密度会被我们的短 caption 拖累**；**AIMv2 式（含 patch 预测）不依赖 caption 丰富度**。
- **口径提醒**：R6/R7 的「**正式训练**切 GPIC `short`」是**另一条线**；**R9/R10 的 scaling 实际用的是 CC12M+Amshaker** —— 报告里必须写清这条区分。

### 📉 体积维护规程（2026-10-03 立 → **2026-10-06 升级为「记忆 + 任务书」双约束**，硬性）

> 理由：`MEMORY_*.md` 与 `BAIZE_<线>_TASK.md` **都每次唤醒被全文读进 prompt**（`prompt="$(< "$TASK_MD")"`）⇒ 越大越烧 token。
> 📊 2026-10-06 实测：本线任务书 `BAIZE_VISION_TASK.md` ≈ **21KB**、`MEMORY_VISION.md` ≈ **32KB（已贴上限）**。
- **上限（两者相同）**：**≤ 32KB**；**红线 40KB** ⇒ **超红线当轮必须先归档才能收尾**。
- **自检**：见「收尾铁律」第 0 条（`wc -c` 两文件，**数字抄进心跳**）。
- **归档去向（只归档「历史」，🚫 不许归档「活口径」）**：
  ① 已执行完/已作废的**运维指令块** → `run/ARCHIVE_OPERATOR_VISION.md`（**留下 1 行指针**）；
  ② 被取代的**候选表/推导过程**（保留现行档 + 实测结果） → `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）；
  ③ 已完成轮次原文 → 沿用 `run/vision/ARCHIVE_ROUNDS_2-9.md` 等；
  ④ 较早的**巡检/流水条目**（保留最近 ~20 条） → `daily-memories-vision/<条目日期>.md`（原文不改）。
- 🚫 **不许归档**：硬规则 / 验收标准 / **现行口径** / `WAITING:` 状态头 / 「运维问答」区。
- 指针（**必须留、只 1 行**）：`> 📦 §<标题>（<日期>）已归档 → run/ARCHIVE_….md；**结论**：<一句话>。需要时再读。`
  🚫 **不许改小节编号/标题**（别处有交叉引用）。
- **谁做（2026-10-06 改 · 与 MEMORY 自滚同机制 = agent 自己做）**：`MEMORY_*.md` 一直由 agent 自滚，**任务书同理** —— **本线 agent 自己**把「已闭合」内容**原文**移入对应归档文件、留 1 行指针。⚠️ **本文件「agent 只读」的唯一例外 = 仅此「搬迁」**：原文一字不改、不动小节编号/标题、**不新增/不改写任何运维指令**（本区作者仍是运维）。**并发安全**：归档前先 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `<线> 归档: …` 前缀。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 ③ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（**为省 prompt token**）

ROUND 2–9 的完整任务原文已移至 **`run/vision/ARCHIVE_ROUNDS_2-9.md`**。

- 这些轮次**均已完成**；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- **需要查旧轮细节时**再去读归档文件；**不要**把整份归档读进上下文。
- 当前指令全部在**本文件上半部分**（运维指令区）。
