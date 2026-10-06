# BAIZE_VISION_TASK.md
## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_VISION.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_VISION.md` / `EXPERIMENTS_VISION*` / `daily-memories-vision/` / `vision/`）。

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
   判据：两者都应 **≤ 32KB**；任一 **> 40KB（红线）** ⇒ 🚫 **不要自己归档**（`BAIZE_*_TASK.md` 你只读）⇒ 在心跳里写一行
   `📦 体积上报：<文件> = nKB 超红线，建议运维归档 §X–§Y（约 nKB）`。去向/红线/指针格式见本文件「📉 体积维护规程」。

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

### 🆕 运维指令 · 2026-10-05（深夜2 · ⑥ **两份 HTML 报告：A. lp 评测细节 · B. AIMv2 架构实现细节**）· 高优先

> **用户 2026-10-05 深夜**：「vision 的 **lp 评测细节**和 **AIMv2 架构实现细节**，**分别写（两个）html 报告**。」

**A. `report_vision_lp_eval.html` —— 「frozen-trunk linear-probe」评测细节**（可复现级别）
- **协议**：自切 IN-1k `val50000 / probe49970`（与 R8–R13 一致）；**冻结 trunk**、只训一个 `Linear(d→1000)`；优化器 / 步数 / bs / 是否 full-batch；**top-1 / top-5** 定义。
- **口径**：`lp` vs `zs`（zero-shot）各自怎么算；**为什么 frozen-trunk lp 是我们横比的主指标**；**噪声带 ±1.5 pp** 的来源（ROUND10 §1.5）。
- **in-domain / 不可比**：`en500k`（= LLaVA imagenet/EN，~30 epochs）**单列不排名**（R8.2 红线）。
- **代码路径**：`run/vision/r8_eval_in1k.py`（**贴关键行号**）+ ckpt 加载 / 特征抽取方式。
- **各轮实测 lp 汇总表**（R9 / R10 / R11-F 五臂 / R11-G / R11-H / R12 …）。

**B. `report_vision_aimv2_impl.html` —— AIMv2-style 架构与实现细节**
- **架构**：OpenVision2 **w512 / depth30 / patch16 / 224²**（126.78M）+ **`PatchPredictor` 0.66M**（`Linear(w→w)→LN→GELU→Linear(w→768)`，fc2 `N(0,0.02)` / bias 0）→ 总 **127.44M**；**文本塔 = 冻结 CLIP-768**（`openai/clip-vit-large-patch14-336`，ctx 77）。
- **前向 / 目标**：`--loss aimv2` = **InfoNCE(pooled) + 1.0×masked-patch-MSE**；**`mask_ratio=0.6`**；`mae_norm_pix_target`（反 CLIP 归一化 → fold → 逐 patch 标准化）；**trunk forward 不变（全 patch 可见、无 mask token）** ⇒ frozen-trunk lp 可比（**关键设计理由**，务必写清）。
- **与官方 AIMv2 的差异（C2 限定）**：官方 = **纯 AR（vision AR + text AR）、无对比项、α≈0.4、prefix-attention、~12B 对**；我们保留 InfoNCE、α=1.0、随机 mask、58.8M 对。
- **代码路径**：`run/vision/models.py` 的 `PatchPredictor` + `r9_train.py` 的 `--loss aimv2` 分支（**贴行号**）。
- **四臂因果分解**（① 6.08 / ④ CoCa 0.47 / ⑥-B 6.23 / ⑥-A 12.08）作为「为什么保留对比项」的证据。

> 两份都要求：**自包含、无 CDN**，写进 `doc/BaiZe-ISEDA2027/`；**命令 + 原始输出 + 路径**（铁律）；**不改论文 .tex**。
> ⚠️ **R12 训练仍在跑（`.12` 8 卡）—— 两份报告是纯 CPU/写作，不得干扰 R12**；写作与训练可并行。
> ✅ 本块生效即视为已批准。


### 🆕 运维指令 · 2026-10-05（深夜 · ① **R12 后「续跑到 3 epoch」+ 逐 epoch 评测 + 重拟合 scaling 刷新 25.1% 上限** ② **自提 ≥3 个下一步方向**）· 高优先 · **已批准**

> **用户拍板（2026-10-05 深夜）**：
> ①「**R12 结束后安排续跑到 3 个 epoch，在 epoch=1/2/3 时分别评测对比（也可多几个点），做 scaling law 的计算，刷新原来的数据无限外推上限（25.1%）**。」
> ②「**让 vision agent 自己建议下一步方向（≥3 个）**。」

**① R12 → 续跑到 3 epoch + 逐 epoch 评测 + 重拟合 scaling（刷新 25.1%）**
- **起点**：R12 已跑 120k 步（≈1.05 epoch, N≈61.4M）；**从 R12 final ckpt 续训**到 **≈3 epoch**（≈3×114,746 ≈ **344,000 步**，N≈176M）。
- **采点（≥6 点）**：**epoch=1 / 2 / 3 必测**；**建议加密到每 0.5 epoch 一点**（1.0/1.5/2.0/2.5/3.0，含 R12 已有的 ~1.05 epoch 点）。每点跑 IN-1k **frozen-trunk lp**（同 R8–R12 口径）。
- **scaling 计算**：与 R11-G 同法（幂律 `a−b·N^−c` + 对数线性），报 **R² + 渐近 a**，与 **R9 的 InfoNCE 25.1%** 并列 → **刷新「数据无限外推上限」**。
- **🔒 预注册判据（先定后测）**：**R²≥0.90 且 a 显著 >25.1%** → 正面（「换目标函数抬高渐近」）；**R²<0.90 或非单调** → 如实写「非简单幂律，需更多点」，🚫 不得强行外推。
- **口径（全不变）**：AIMv2-style（InfoNCE + 1.0×patch-MSE）· w512 · 冻结 CLIP-768 · bs64×8=512 · seed1234 · bf16 · `.12` 8 卡；`--save-interval` 对齐采点。
- **成本**：**先按实测 img/s 报「墙钟 / GPU·h / epoch」估算再起跑**（沿用「先报估算」铁律；R12 ~5400 img/s，3 epoch ≈344k 步）。
- **产出**：`EXPERIMENTS_VISION_ROUND11.md` 新 §19（或新建 `EXPERIMENTS_VISION_ROUND12.md`）写 (lp,N) 新点 + 拟合式 + R² + 与 25.1% 对照；**回填论文 §6.3 的 scaling 数字**（该段已解冻）。

**② 自提 ≥3 个下一步方向（只建议、未批不得起跑）**
- 基于现有结果（AIMv2 翻盘 / R11-H 纯 AR 无翻盘 / R11-G scaling / R11-F 数据源横比 / OpenVision2 官方=纯生成 / R13 官方 79.81%），**书面提出 ≥3 个候选方向**；每个给：**动机 · 成本（GPU·h + 墙钟）· 预注册判据 · 预期产出 · 风险/边界**。
- 交付：`run/VISION_NEXT_DIRECTIONS.md`（写入并在 MEMORY / 日报里引用）。**仅建议 —— 等运维批准后才可执行。**

> ✅ 本块生效即视为已批准：**R12 训完 + eval 后，按序执行 ①（续跑 3 epoch）并交 ②（方向建议）**，无需再等唤醒。

### 🆕 运维指令 · 2026-10-05（晚 · ① **用全部现有数据跑当前最佳配方 AIMv2（先交「时长 / epoch」估算）** ② **论文 §6 由你改写** ③ 「外网命令带 proxy」口径同步 + 环境隔离）· 高优先 · **已批准**

> **用户拍板（2026-10-05 晚）**：「vision 已空闲，**用全部现有的数据训练（41% 的 GPIC + 以前的两个数据集）**；当前的最佳配方 **AIMv2 估计要多久，>1 epoch 呢**」；「**论文改写：让 vision agent 在起完训练后自己改吧，它还可以用 web search**」。

**① 用全部现有数据跑「当前最佳配方 AIMv2」—— 但必须先交估算（不占卡）**

> 🔒 **起跑前置（用户 2026-10-05 晚 拍板）**：**先完成上方「运维前置 · AIMv2 提速」块**（归因实测 → 数据管线提速，保持 `--batch-size 64` / global 512 可比），**把实测 steady img/s 提上去之后**才允许起本全量训练；下面的估算一律用**提速后的实测 img/s**（不是 R11-G 的 2485）。
- **配方** = **AIMv2-style = ⑥-A / R11-G 同款**：`InfoNCE + 1.0×masked-patch-MSE`（`--loss aimv2 --mask-ratio 0.6 --patch-loss-weight 1.0`），w512（OpenVision2）+ **冻结 CLIP-768**；其余口径照旧，**唯一变化 = 数据量/步数**。
- **数据 = 现有全部**：**GPIC（当前 ≈3229/8000 tar ≈41%）** + **CC12M + Amshaker**（≈18.5M）。先**核清各源实际可用对数与 tar/shard 数**（贴 `ls/find` 原文）。
- ⏳ **先报「估算」再开跑**（硬性前置）：给出 **总样本数 N · 实测 steady img/s · 总步数 · 墙钟 · GPU·h · 折算 epoch 数**。
  - **运维粗估（待你精算）**：R11-G 稳态 **≈2485 img/s**；若总量 ≈ **59M 对**（GPIC≈40.5M + CC12M+Amshaker≈18.5M）⇒ **1 epoch ≈ 6.6h**；**>1 epoch**（如 2 epoch ≈ 13h）。**请用实测 img/s 取代该粗估，并明确回答「是否 >1 epoch」。**
- 起跑前在 `EXPERIMENTS_VISION_ROUND11.md`（或新 ROUND12 节）写**预注册判据**（先定后测）；公平表照旧（参数量 + token + 每步耗时）；**GPU 用你 `.12` 的 8 卡**（`.29` 的 8 卡是 pretrain/data 的，别碰）。
- 产出：新数据量的 (lp, N) 轨迹 + 与 R11-G（55.3M）的对照 + scaling 是否延续。

**② 论文 §6 改写 —— 本指令授权由你执行（**训练起跑并进入稳态后**再做）**
- ✅ **原「论文冻结」对本项解冻**：授权改 `code/BaiZe-ISEDA2027/ISEDA2027/6_vision_encoder.tex`（及 §6 相关段落）中关于 **「25.1% 是从零路线的诚实天花板」** 的表述。
- **改法**：改为「**换 caption-无关的稠密目标（+ 保留对比项）可突破该上限**」，并**如实写清边界**（C2：自研 AIMv2-style 改编、非官方复现；精确渐近不可定；R11-H 证明翻盘依赖对比项）。
- 依据数字：R11-G **R²=0.91 / lp@55.3M 19.76% vs 基线 7.40%**（Δ 随 N 增大 +7.5→+12.4 pp）；R11-H **6.23%（+0.15）⇒ 无翻盘**；四臂因果分解（①6.08 / ④0.47 / ⑥-B 6.23 / ⑥-A 12.08）。
- **可用 `cimi_search`/`cimi_fetch` 补一手引用**（§16.8 已有 AIMv2 / MAE / XTRA / SigLIP2 / OpenVision2 锚点）；**每条引用给 URL + 年份**，核不到写「未核实」。
- 🚫 **只改该结论相关段落**（别顺手重写整章）；改完把 **diff 摘要** 回填 `EXPERIMENTS_VISION_ROUND11.md` + 日报。

**③ 「外网命令带 proxy」口径同步到本线（与 data / harness / pretrain 一致）**
- 你的 shell 被 loop 剥了 `*_PROXY`（内网网关鉴权用，**不能改**）⇒ 外网命令自己带：`P=http://172.19.92.25:13128`（`.12` 用你 `~/.bashrc` 里的值）；`https_proxy=$P http_proxy=$P <cmd>`；pip 加 `--proxy $P` + 阿里/腾讯索引。
- 🔑 `Errno 101 / http 000` = **shell 没带 proxy**，≠ 集群禁网/镜像被墙。MCP `cimi_search`/`cimi_fetch` 走内网 gateway，**不需要** proxy。

**④ 环境隔离纪律（治「同机争用」—— 用户裁定）**：训练/长跑 = 共享 `py310`；大量装包 = 另起独立 conda env；🚫 不动共享 env。

> ✅ 本块生效即视为已批准：**先交流程/时长估算 → 起训练 → 训练稳态后自行改论文 §6**。


### 1. 📌 全局口径与铁律（**一次性质，对所有 R 生效**）


- 🚫 **不许闭门造车**：涉及"别人怎么做"（架构/loss/评测/数据）**必须去读官方仓库或论文原文**（能 clone 就 clone）—— **不得凭二手描述下结论**（本线已因此出错一次）。
- **不重跑已落盘训练**；**不改 R8/R9/R10 已落盘结论**（只在 §2 明确"修正"条目下补限定）。
- **控变量**：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- **公平性**：加 decoder 的臂**必须报「参数量 + 训练 token + 每步耗时」**，不许只比 acc。
- **预注册**：判据**先定后测**，不许事后改。
- **体积**：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` **各 ≤32KB**（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（**最高优先 · 纯 CPU · 与 R14/E1 合并做**）

| # | 修正 | 要点 |
|:--|:--|:--|
| **C1** | **数据量口径** | `r9_scaling.py:158` 的「本地 53M 上限」是 **`--local-cap-m default=53.0`＝假设、非实测**。按 DATA_RESEARCH 实测（GPIC **5 tar=53,637 图 → ~10,727/tar × 8000 ≈ 86M**）外推 → **本地全量上限 ≈103M**（GPIC 86M + CC12M 11M + Amshaker 6M）。→ 用**真实 cap 重算** R9 所有 "×N 缺口"（含 "226× the 53M cap"）；报告中**统一三类分母**：**R9 用过 18.5M / 盘上现有 ≈29M / 本地全量 ≈103M**，并标注**数据仍在下载（动态值）**。 |
| **C2** | **R8 结论加限定** | R8 的 6 架构**全是自研 from-scratch 等参改编**（`run/vision/models.py` 头行自证；R8 亦标「等参改编（非官方模型）」）→ **「SSM 坍缩」只能表述为「我们 recipe（冻结语义文本塔 + InfoNCE）下、我们自研改编版的坍缩」**，🚫 **不得**推广成「官方 MambaEye/DeepEncoderV2 会坍缩」。 |

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
- **谁做**：本文件写明「agent 只读」⇒ **归档动作由运维在中继块执行**；agent 只负责 ①抄体积数字 ②超红线时给「建议归档 §X–§Y（约 nKB）」。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 状态头 ③ 最近 ~20 条。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---




---

## 📁 历史轮次已归档（**为省 prompt token**）

ROUND 2–9 的完整任务原文已移至 **`run/vision/ARCHIVE_ROUNDS_2-9.md`**。

- 这些轮次**均已完成**；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- **需要查旧轮细节时**再去读归档文件；**不要**把整份归档读进上下文。
- 当前指令全部在**本文件上半部分**（运维指令区）。
