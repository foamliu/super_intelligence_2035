# EXPERIMENTS — 视觉编码器 Round 3（R3）：eval5k 精确随机的根因判定

> 生成时间：2026-10-01。任务书 `BAIZE_VISION_TASK.md` 第三轮（R3）。
> **R3 一句话结论**：eval5k 检索 R@1/5/10 = 1/5000·5/5000·10/5000（精确随机）既不是「训练不足（A）」，也不是「评测脚本 bug（B）」，而是**模型训练坍缩**（vision+text 双塔退化为常量特征输出）——第三条成因，且比 A/B 更根本。

---

## 0. 环境与预算记录（R3.0 要求原文照录）

**GPU 独占状态（实测原文）**：
```
nvidia-smi --query-gpu=index,memory.used,utilization.gpu --format=csv
0, 0 MiB, 0 %
1, 0 MiB, 0 %
2, 0 MiB, 0 %
3, 0 MiB, 0 %
4, 0 MiB, 0 %
5, 0 MiB, 0 %
6, 4 MiB, 0 %
7, 4 MiB, 0 %
nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv
（仅表头，无任何 compute 进程）
```
→ 本机（10.239.2.12）GPU 0–7 全空闲、无争用。

**NFS 争用状态（对照组 pretrain，原文照录 MEMORY_PRETRAIN_2B.md 头部）**：
```
- STAGE: **R2 第二轮进行中**（… S4 退火消融 ✅ L3+code+math 86:10:4 胜出（2.629822），S5 长跑+多seed ✅ 4/4 完成 …）
- PHASE: **R2_active**（R2 进行中 … 胜出配置 = LR=1e-3 / WSD / warmup=250 / decay=500 / min_lr=1e-5 …）
- WAITING: 1（R2 编排链 running：P-1 ✅ 全回收 → P-2 补 seed → P-3 架构 5000 步 串行，30min 长轮询）
```
→ pretrain 在 10.239.2.29 上 8 卡进行中（共享 NFS）。**本步骤 A 全程为轻量核验/诊断（只前向 128–256 张图），无重训练或重 I/O**，故 NFS 争用不影响本文所有测量结论；修复探针（第 5 节）为单卡 300 步短训（~63s 墙钟），亦不与 pretrain 争 GPU（不同机器）。

**预算**：R3 步骤 A 判定 + 控制实验 + 修复探针，无实质 GPU·h 新增（短训合计 <4 GPU·min）。

---

## 1. 任务与判定总览

| 步骤 | 状态 | 结论 |
|:---|:---|:---|
| R3.0 唤醒 · 状态切换 | ✅ | `R2_complete` → `R3_active`，WAITING 1→0，流水追加 R3 启动记录 |
| R3.2 步骤 A「评测自查」 | ✅ **决定性** | eval 脚本**无 bug**；模型**特征坍缩**（双塔常量输出）。见 §2 |
| R3.1 裁定（A vs B） | ✅ | **既非 A 也非 B**，属「训练坍缩」第三条成因。见 §3 |
| R3.3 步骤 B「延长 horizon」 | ⏭️ **裁减** | 坍缩是损失地形均衡，>horizon 无用（R2-0 已证 5k→10k 平台在 4.45）。见 §4 |
| R3.4 步骤 C「换同源 held-out」 | ⏭️ **裁减** | 特征恒为常量，换任何 eval 集都随机。见 §4 |
| 修复探针（额外） | ✅ | 300 步复现坍缩；简单修法（冻结 text 塔/固定 bias）**均不能阻止**。见 §5 |
| R3.5 交付 1 报告 / 交付 2 HTML / 交付 3 状态 | ✅ | 本报告 + `BAIZE_VISION_ENCODER_RESULT_ROUND3.html` + MEMORY/EXPERIMENTS 更新 |

---

## 2. 步骤 A「评测自查」—— 证据链（5 条，全部落盘）

### 2.1 排除「text tower 随机 init」假设（keys 检查）
`r3_stepA_diag.py --mode keys` 对 R2-2 双臂检查点逐字比对 key 集：
```
=== S8_ov2_lr3e-3/vision.pt ===        # R2-2 SigLIP 臂的复用权重
  top-level keys: ['config','logit_bias','logit_scale','text','vision']
  config: {tower:'openvision2', resolution:224, patch:16, steps:3000, loss:'siglip'}
  vision params: 505.0M | text params: 63.4M | has_text=True
  vision keys match: True (missing=set(), extra=set())
  text keys match:   True (missing=set(), extra=set())
=== R2_ov2_clip_lr3e-3/vision.pt ===    # R2-2 CLIP 臂
  config: {... steps:3000, loss:'clip'}
  vision params: 505.0M | text params: 63.4M | has_text=True
  vision keys match: True | text keys match: True
=== S3_openvision2/vision.pt ===        # Round 1 遗留（对照）
  top-level keys: ['config','vision']   → has_text=False（vision-only）
```
→ **R2-2 两臂 eval 用的都是「含 63.4M 参数、key 集与全新 TextTransformer 逐字吻合」的完整 text 塔**；只有 Round 1 的 S3 是 vision-only。**「随机 text 塔导致检索随机」假设被证伪。**

### 2.2 检索本身：精确 chance（坍缩的外显症状）
在 eval5k（n=5000）上，若所有余弦相似度相等（读到的 `mean_diag=0.9961 = mean_offdiag`，`max_offdiag=1.0000`），则 ranking 由数值噪声决定 → R@1=R@5=R@10 恰等于 chance：`1/5000=0.0002, 5/5000=0.0010, 10/5000=0.0020`，与 R2 落盘的 `0.0002/0.0010/0.0020` 完全一致（n=1000 复测同样得 `0.001/0.005/0.010`）。

### 2.3 坍缩定位（`r3_collapse_diag.py`，三架构对比）
```
S8_ov2 (SigLIP): IMAGE cos same-tower mean/min/max = 1.0000/1.0000/1.0000
                 TEXT  cos same-tower mean/min/max = 1.0000/1.0000/1.0000
                 CROSS diag=0.9956 = offdiag=0.9956
R2_mambaeye(SigLIP): IMAGE/TEXT cos = 1.0000/1.0000/1.0000；CROSS diag=offdiag=0.9955
R2_ov2_clip(CLIP): IMAGE cos mean=0.9992 (min 0.9905)；TEXT 0.9990；
                   CROSS diag=0.9916 vs offdiag=0.9913（略比 SigLIP 轻，但同数量级近坍缩）
```
配套：原始特征 per-dim std ≈ 0（SigLIP IMAGE per-dim std 范围 `[0.0000, 0.1252]`、TEXT `[0.0000, 0.0576]`）→ **跨样本每个维度几乎恒定**，即输出几乎与输入无关。
→ **OpenVision2（Attention ViT）与 MambaEye（纯 SSM）双双精确坍缩到 cos=1.0** → 坍缩与架构/目标函数类型无关（两目标都坍缩），是**训练 recipe 的属性**。

### 2.4 控制实验（排除评测/输入 bug）
同一批 eval5k 输入喂给**全新随机初始化**（未训练）的 OpenVision2 双塔：
```
[FRESH-RANDOM] IMAGE same-tower offdiag mean/min/max = 0.1725/-0.7735/0.9991   ← 发散
[FRESH-RANDOM] TEXT  same-tower offdiag mean/min/max = 0.6792/0.4302/0.8730    ← text 塔随机 init 本身就偏高（共享 token 结构）
[FRESH-RANDOM] CROSS diag=-0.0079 offdiag mean=-0.0070 (range -0.1431..0.1180) ← 随机
```
→ **输入与评测无 bug**：随机塔对同样输入给出发散特征。训练后的塔坍缩到 cos=1.0 是**训练造成的**。

### 2.5 损失恒等式（坍缩均衡的算术值）
4 个 SigLIP 检查点学习到的标量几乎完全一致（跨架构）：
```
S8_ov2:          scale=5.6827 (exp=293.75)  bias=-9.0937
R2_deepencoder:  scale=5.6547 (exp=285.64)  bias=-9.0738
R2_moevie:       scale=5.6641 (exp=288.32)  bias=-9.0699
R2_mambaeye:     scale=5.6057 (exp=271.96)  bias=-9.0113
R2_ov2_clip:     scale=6.0177 (exp=410.62)  bias=None（CLIP 无 bias 项）
```
SigLipLoss `= -logsigmoid(label·(sim·scale+bias)).sum()/N`。在坍缩态（sim≈0.9956）代入 S8 的 scale/bias：
`logit = 0.9956×5.6827 − 9.0937 = −3.4361` → `f_pos=−logsigmoid(−3.4361)=3.467`，`f_neg=−logsigmoid(+3.4361)=0.0320`，
`loss = 3.467 + 31×0.0320 = 4.459 ≈ 实测 4.456`。✅ **分毫不差**。
→ Round 1/2 的「loss=4.45 且四架构不可区分」是**坍缩均衡 loss**（3.44 正例项 + 1.00 负例项），不是有效学习结论；CLIP 臂则把温度 `exp(scale)=410` 放大去锐化噪声，同样是坍缩的自一致读数。

---

## 3. R3.1 裁定：A / B / 第三条

- **不是 A（训练不足）**：S3 已跑到 10k 步仍钉在 4.45（R2-0 结论），延长 horizon 无意义；修复探针更进一步——坍缩在 **300 步内**就已精确达成（§5），证明它是**损失地形的吸引子/均衡**，而非收敛不充分。
- **不是 B（评测脚本 bug，狭义）**：`eval_downstream.py` 正确、`r3_stepA_diag.py` 复算一致；自检索 sanity 也“看似 100%”（diag≈offdiag≈0.996）——但这是因为**连 off-diagonal 也是 0.996**（坍缩签名），而非评测配对正确。
- **是「训练坍缩」（representation/modal collapse）**：vision 与 text 双塔均退化为近常量输出（cos 1.0），与输入无关，因此检索排序全随机。这**外显为 B 的症状**（精确 chance），但要靠**训练侧**修复而非评测侧。

**一句话**：`eval5k R@K=精确随机` 是「特征坍缩」的下游症状；真正需要修的是预训练 recipe。

---

## 4. 步骤 B / C 裁减说明（优先级 A>B>C，逆序裁剪）

- **B（R3.3 延长至 20k 步）裁减**：坍缩是损失均衡平台（S3 10k 已平台），延长 horizon 不会离开坍缩态；证据充分（§2.5 算术值 + §5 三百步内坍缩）。
- **C（R3.4 换同源 held-out）裁减**：特征与输入无关（恒为常量），同一源/跨源/自检索都只能是随机；换 eval 集不解决「模型已坍缩」。
- 二者浪费预算且无信息增益，按任务书「超时按逆序裁剪」原则裁减，预算让给「控制实验 + 修复探针」。

---

## 5. 修复探针（300 步短训复现 + 简单修法验证）

`r3_fix_probe.py`：单卡、en500k、batch=64、SigLIP、300 步、随机 init，末态量双塔 same-tower 余弦。三配置：

| 配置 | vision cos(mean) | text cos(mean) | cross diag / offdiag | 判定 |
|:---|:---|:---|:---|:---|
| **baseline**（text 联合训练 + bias 可学习 init −10） | **1.0000** | **1.0000** | 0.9999 / 0.9999 | **坍缩（精确复现）** |
| **frozen-text**（text 随机冻结 + bias 可学习） | 0.9965 | 0.6689 | 0.7995 / 0.7984 | 视觉塔**仍近坍缩**，仅 ~1e-3 的 diag>offdiag 空隙 |
| **fixed-bias**（text 联合训练 + bias 冻结于 0） | **1.0000** | **1.0000** | **−0.9999 / −0.9999** | 双塔仍坍缩，且翻成**反平行坍缩**（vision→+v、text→−v） |

**解读**：
1. **300 步、单卡、64 batch 即精确复现全量训练（3000 步·6 卡·32 batch）的坍缩** → 坍缩不是 DDP/batch-size/horizon 副产物，是 objective 的固有吸引子。
2. **冻结 text 塔（随机 init）不够**：视觉塔仍坍缩到 0.9965。因为随机 text 塔自身特征就高度相关（cos≈0.67），且视觉塔可直接退化到「平均文本方向」而不必学到区分。
3. **固定 bias=0 也不够**：偏置只是坍缩「模式」的旋钮（同向 → 反平行），不是坍缩「是否发生」的开关。真正的坍缩驱动力是「从零/随机 init + 每 batch 对比（少量负样本：32/64）+ 500k 对 + 可学习 scale/bias 梯度饥饿」这一步式 recipe。
4. 学到的 `scale→5.68 / bias→−9.09`（4 架构几乎同值）是坍缩态的**共点解**：`bias≈−9` 使正例对 logit 恒为负、`scale` 只放大噪声；特征梯度被 scale/bias 吸收（梯度饥饿），特征本身走不动。

**结论**：修复不能靠一行改动；需要换 recipe（见 §7）。这解释了为什么 R2 的“提高 LR / 换分辨率 / 换架构 / 换目标函数”全都钉在坍缩态。

---

## 6. 论文回填建议（关键，直接可用）

**原则：R2 及更早的「loss」与「eval5k R@K」读数全部作废为「坍缩伪阅读数」，不得作为 encoder 质量的代理指标。**

- **tab:visobj（目标函数 SigLIP vs CLIP）**：❌ 不可用 `4.456 vs 3.270`（SigLIP 是坍缩均衡 loss、CLIP 是温度爆表后的锐化噪声，二者量纲与含义都无意义）。✅ 如实在表注写：**「从零 recipe 下，SigLIP 与 CLIP 均发生表征坍缩，无有效 loss 代理指标」**。仅「训练吞吐≈相等（1645 vs 1657 img/s）」这一计算侧数据可保留。
- **tab:visarch（架构对比）**：❌ 不可用「loss 4.45 四架构不可区分」——它只是**坍缩均衡点，与架构无关**，不是「架构对表示学习无影响」的证据。✅ 保留**吞吐/延迟排序**（OpenVision2 训练 2017 img/s / 推理 6.87ms 双最优，R2-4 干净复测），此为架构结构属性、**不受坍缩影响**。
- **tab:visres（分辨率对比）**：❌ 不可用「256/576/1024 token 的 loss 并列」——同样坍缩。✅ 仅保留吞吐/延迟随 token 的趋势（注意 R2-3 已记的 batch 不一致 caveat）。
- **总建议（R3.5 允许的「如实写无有效代理指标」）**：论文应落一句方法论说明——**「在 500k 对、从零初始化、双塔联合训练的 recipe 下，contrastive 预训练双塔发生表征坍缩，loss 与检索 Recall 均为坍缩的下游读数；本项目现阶段不提供有效的 semantic 质量代理指标，仅提供计算侧（吞吐/延迟）对比。」**
- **把坍缩本身写成发现**：这本身就是个可发表的方法论警示（`contrastive collapse under small-data from-scratch joint training`），比硬凑一个不存在的指标更诚实、更有价值。

---

## 7. 修复方向（Stage iv / 未来工作，超出 R3 范围）

按「见效预期」排序：
1. **换初始化**：text 塔用**预训练/固定的语义 text encoder**（设计意图本就是「固定 text tower，只动 vision」——当前代码 `train.py` 把双塔都塞进 optimizer 联合训练，偏离了设计意图）。仅冻结随机塔不够（§5），需要**有语义的** text 塔让 diag/offdiag 可分。
2. **压住 scale/bias**：冻结 `logit_scale`（合理初值）与 `logit_bias`（0 或冻结），阻断梯度饥饿。
3. **加大负样本 / 更大 batch**：标准 CLIP 需数百万对与上千负样本，500k 对 + 32 batch 的每-batch 对比先天易坍缩。
4. **换目标**：若要小数据自监督，用**重构型（MAE/MIM）**或加 uniformity/anti-collapse 正则，而非纯 contrastive。
5. 上述均需重训并重评；在此之前，论文**不要**给出任何 semantic 代理指标读数。

---

## 8. 可复现命令

```bash
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision
export LD_LIBRARY_PATH=/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/lib:${LD_LIBRARY_PATH:-}
PY=/nas_train/app.e0031982/miniforge3/envs/py310/bin/python

# (1) keys 检查（text 塔是否就位）
$PY r3_stepA_diag.py --mode keys \
  --ckpts /nas_train/app.e0031982/datasets/baize-vision/out/S8_ov2_lr3e-3/vision.pt \
          /nas_train/app.e0031982/datasets/baize-vision/out/R2_ov2_clip_lr3e-3/vision.pt \
          /nas_train/app.e0031982/datasets/baize-vision/out/S3_openvision2/vision.pt

# (2) 检索复算（n=1000，应见精确 chance 与 diag≈offdiag）
$PY r3_stepA_diag.py --mode retrieval --tower openvision2 \
  --ckpt /nas_train/app.e0031982/datasets/baize-vision/out/S8_ov2_lr3e-3/vision.pt --n 1000

# (3) 坍缩定位（双塔 same-tower 余弦；三架构对比）
for CK in S8_ov2_lr3e-3 R2_ov2_clip_lr3e-3; do
  $PY r3_collapse_diag.py --ckpt /nas_train/app.e0031982/datasets/baize-vision/out/$CK/vision.pt --tower openvision2
done
$PY r3_collapse_diag.py --ckpt /nas_train/app.e0031982/datasets/baize-vision/out/R2_mambaeye_r224_p14/vision.pt --tower mambaeye

# (4) 修复探针（三配置 × 300 步短训）
$PY r3_fix_probe.py --config all --steps 300
```

**诊断脚本**：`vision/r3_stepA_diag.py`、`vision/r3_collapse_diag.py`、`vision/r3_fix_probe.py`（本次新增，均已落盘）。

---

## 9. 状态

- 判定结论已回填 `MEMORY_VISION.md`（状态头 **PHASE=R3_complete**、WAITING=1 终局 idle、新 R3 小节）+ `daily-memories-vision/2026-10-01.md`。已 git commit + push。
- HTML 交付：`BAIZE_VISION_ENCODER_RESULT_ROUND3.html`（自包含，0 外部引用）。
- 未改动任何 `.tex`（R3.5 约束「只回填建议，不改 tex」）。