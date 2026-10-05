# BAIZE_DATA_TASK.md

> ⚠️ 本文件为**指令文件**，agent **只读**（禁止修改）。
> 运行时状态写 `MEMORY_DATA.md` / `DATA_LEDGER.md` / `CONTAMINATION_CHECK.md` / `daily-memories-data/`。

---

## 🔧 运维指令区（OPERATOR NOTES）— **每次唤醒必须先读本区**

> 📦 **历史运维指令已归档** → `run/ARCHIVE_OPERATOR_DATA.md`（已执行完 / 已作废的块；**需要时再读**，不要读进上下文）。

> 本节由**外部运维**通过 git 修改，用于**远程派活 / 改优先级 / 索取状态 / 暂停**。
> **agent 禁止修改本节**（只写别的区）。本节为「无」时，按下方默认阶段顺序自主推进。
### 🔴 运维指令 · 2026-10-06（**配比实验改道**：废弃「目标尺寸模型 + 手挑单臂」→ 改「**小代理模型 + Optuna 贝叶斯优化 + 每卡独立 trial**」；**1 天搜 Stable / 1 天搜 Decay**）· **最高优先 · 立即执行**

> **用户 2026-10-06 复核裁定**：现方案**方法学错 + 成本失控**，**即刻改道**。
> - ❌ **错在哪**：S0a 用的是 `pretrain_launcher.py --arch mamba2` = **与目标 P-8 同尺寸的 2.2B（`NVIDIAMambaHybridModelProvider2B`，2.220B）** ——
>   `DATA_MIX_RECIPE.md §6` 标题写着「无需全量 2.2B」，**执行却照跑全量**；且**只有 1 条臂 / 1 个 seed / 无中间 ckpt / 手挑网格**（全仓库 **0 命中** `optuna` / 贝叶斯 / grid / random search）。
> - ❌ **成本**：实测 **≈312 GPU·h / 臂**（配方里原估 0.5–1 GPU·h，**差 ~50×**）；按 40 臂算 ≈ **12,480 GPU·h ≈ 5.2× P-8 本体（~2,400 GPU·h）** —— **搜索比被优化的训练还贵，不可接受**。
> - ✅ **正解（对齐 `ye2024datamixinglaws` / Xmodel-2）**：**小代理模型** × **很多配比点** × **贝叶斯响应面优化** × **外推到 2.2B**。
>   Xmodel-2 正是这么干的：**`xmodel-2.tex:144-154` 跑了 400+ 次试验**才把搜索收敛到两问（SFT 占比 60–69% / SFT 内部 5 类分布）——**我们照抄这条路线**。

#### ① 立即动作（**第 0 步，先做这个**）

- 🔴 **kill 当前 `mix_stable_s0a`**（**data 线自己的进程**，重启后 PID `2528081`–`2528090`，端口 `29950`）→ **释放 `.29` GPU2–7**。
- 已跑的 **~1350 步作废**；**如实**记进 `MEMORY_DATA.md` 流水（**不许粉饰**、不许写成「阶段性成果」）。
- `report_data_mix_s0a.html` **保留为历史**：标题加后缀「（**已废弃方法 · 目标尺寸单臂**）」，**不再更新**。
- `run/baize_mix_stable_s0a.sh` **停止调用**（保留文件，标注 `# DEPRECATED 2026-10-06：2.2B 单臂方案作废`）。

#### ② 硬约束（**用户给定，不许自行放宽**）

| 项 | 值 |
|:--|:--|
| **算力** | `.29` **GPU2–7（6 卡）**（卡账本见 `run/GPU29_ALLOC.md`） |
| **并行方式** | ⭐ **每张卡独立跑一个 trial**（`torchrun --nproc_per_node=1`，**TP1 / DP1**，**各自 `master_port`**，`CUDA_VISIBLE_DEVICES=<i>`）→ **6 个 trial 并行**；🚫 **不要**再用 DP6 跑单个大模型 |
| **GBS** | **8–16**（小 batch，用户指定） |
| **seq_len** | **2048**（用户指定；可更小，但**同一 study 内必须固定**） |
| **吞吐目标（硬指标）** | **24h（6×H100）跑 200–400 个 trial** → 即 **≈144 GPU·h ÷ (200–400) ≈ 0.36–0.72 GPU·h/trial**，换算**单 trial wall ≈ 22–43 min**；**按富余取 ≤ ~20–30 min/trial** |
| **代理模型** | 🚫 **不是 2.2B**。必须是**同族 mamba2-hybrid 小代理**；规模 = **能塞进上面时限的最大值**；**起手建议 ~50–150M 参数**（≈目标 2.2B 的 **1/15–1/45**） |
| **搜索算法** | **Optuna**（`TPESampler` 贝叶斯优化 + `MedianPruner` 早停）—— **用户指定**（他此前即用 Optuna 做 BO） |
| **预算** | ⭐ **Day1 = 搜 Stable 段配比；Day2 = 搜 Decay 段配比**，**各 1 天** |

#### ③ 标定（**先标定，再开搜 —— 不许跳过**）

1. **先跑 1 个 trial（1 卡）**，实测 **tok/s** 与 **s/step**（固定 `GBS=16` / `seq=2048`）→ 贴**原始输出**。
2. **反推**：`单 trial 时长 = 步数 × s/step`；**若 > 30 min → 继续缩小模型**（**先减层数，再减 hidden**），直到满足 **200–400 trial / 24h**。
   - 🔢 **可直接算的公式**：`N_trial/天 ≈ 6 × 86400 ÷ (步数 × s/step)`；即要求 **`步数 × s/step ≤ 1728 s`**（= 300 trial/天）；`≤ 2160 s` 对应 240 trial/天。
   - 💡 反过来：**若标定后 24h 能跑远超 400 trial → 把模型调大**（larger proxy = 更好的迁移性），**而不是**把 trial 数堆到上千。
3. **步数**初值建议 **~2000–4000 步/trial**（≈ 65–130M token），按上面反推结果调整。
4. 把 **实测 tok/s · s/step · 选定模型配置（层数/hidden/参数量）· 预计总 trial 数 · 预计总时长** 写进 `MEMORY_DATA.md` + 报告。
5. ⚠️ **标定若显示 24h 跑不到 200 trial → 再缩小模型**，**不是**延长时间、**不是**减 trial 数。

#### ④ 搜索空间（Optuna `suggest_*`）

- **Day1 · Stable 段（WSD 的 stable 主体）**：`web`（base / UltraX；**UltraX 🚫 未下 → 本轴降级为「仅 base」**，沿用 §0.6-B 既有口径）· `code` · `math` **三点、`sum=1`**。
  初值域：`web ∈ [0.80, 0.95]`、`code ∈ [0.03, 0.12]`、`math = 1 − web − code`（**让 BO 自己找，别把先验钉死**）。
- **Day2 · Decay 段（带 SFT 的退火）**：**`SFT 总占比 ∈ [0.40, 0.80]`**（⚠️ Xmodel-2 最优落在 **60–69%（取 64%）**，**是文献锚点不是答案**——**让 BO 自己搜**）+ **SFT 内部 5 类**（`Mathematics` / `Code` / `Logic` / `Knowledge` / `Commonsense`，**CoT 归 Logic**）**单纯形采样**。
- 搜索空间若有物理约束（`sum=1`、非负）→ 用 **`suggest_float` + 归一化**，**不要**用会越界的独立 `suggest_float`。

#### ⑤ 目标函数（objective）与收尾

- **主 objective = 固定 held-out 验证集 loss**（⭐ **整轮固定同一个 held-out bin，防泄**；用 `suggest=` 采样出的配比去训，在**同一验证 bin** 上测）。
  → 便宜、信号密、**可早停**；**别对 300+ 个模型都跑 `lm_eval`**。
- **早停**：`MedianPruner`（如 **1/3 步处 loss 显著差于中位 → prune**）→ 同 24h 内能跑**更多** trial。
- **收尾**：取 **top-K（如 5）** 配比跑 **`lm_eval` Table 2（8 集）/ Table 3（6 集）** 复核（复用 pretrain 已打通的 `ckpt → HF → lm_eval` 管线）。
- **可复现**：每 trial 落盘 **Optuna `sqlite` storage** + **trial 配置 CSV**（`number / params / steps / loss / status / created`）。
- **依赖安装**：`optuna` **装进独立 env**（🚫 **不许污染共享 `py310`**，见上方「环境隔离纪律」）；**外网命令显式带 proxy**（见上方 proxy 口径块）。

#### ⑥ 交付 & 纪律

- **交付**：**重写 `DATA_MIX_RECIPE.md §6`** = **① Optuna study 定义（搜索空间/采样器/pruner/objective）② trial 数（实测）③ 两段各自的最优配比百分比 ④ 外推到 2.2B 的迁移性说明**（引用 `ye2024datamixinglaws`；**如实标注「代理规模 ≠ 2.2B」这一限制**）；每 trial 一行进实验记录（`MEMORY_DATA.md` / `DATA_LEDGER.md`）。
- **口径统一**：`DATA_MIX_RECIPE.md` 里 §6 的模型尺寸数字**有 2.2B / 2.47B / 3B 三种写法** → **一并订正**（以 `pretrain_launcher.py` 的 `NVIDIAMambaHybridModelProvider2B` = **2.220B** 为唯一准据）。
- **纪律（不变）**：🚫 不改 pretrain 的脚本 / 🚫 不碰 `.29` GPU0–1 / 🚫 **不 kill 对方进程** / 🚫 **全轮不出现领域化** / 重 I/O 避让（`.29` 与 `.12` 共享 `/nas_train`）。
- **回写**：`MEMORY_DATA.md` 的「进度快照」+「运维问答」须写清 **标定结果** 与 **最终两段配比**。

> ✅ **本块生效即视为已批准**，**无需再等拍板**。**这是当前 data 线唯一主攻**（白名单下载巡检照常后台低强度进行）。
> 📌 **一句话**：**用小模型跑几百次试验去拟合配比，而不是用 2.2B 跑一次；两天（Stable / Decay 各一天）出配方。**

---

### 🆕 运维指令 · 2026-10-05（深夜2 · ⑤ **写一份 HTML 报告讲清「Stable S0a 配比实验是什么 + 现在到哪了」**）· 高优先

> **用户 2026-10-05 深夜**：「**数据配比实验（Stable S0a）是做什么，写个 html 报告**」。

- **报告必须讲清**（面向「领导 / 1400 DE」读者，不是只给本线看）：
  1. **它是什么**：**§0.6-B「P-8 数据配方」实验** —— 用 **MiniCPM5 / Xmodel-2 的 WSD 双阶段配比**思路，在**小规模代理预算**下搜索 **Stable 段（base 主体）** 与 **Decay 段（L3+Math+Code+SFT = 带 SFT 的退火）** 的最佳配比。
  2. **Stable S0a 臂具体是什么**：**`base:code:math = 88:8:4`** · **6 卡 DP6** · `seq=4094` · `mb=1` · **`GBS=1020`**（因 DP6 整除，较基线 1024 **−0.4%**，**须标注可比性**）· **5000 步** · bf16 · seed1234 · 脚本 `run/baize_mix_stable_s0a.sh`。
  3. **为什么这么设计**：搜索空间 = §0.6-B 的 **Stable / Decay 两张表**；每臂跑完用**两套代理指标**：**Table 2 的 8 个**（`ARC-C`/`ARC-E`/`BoolQ`/`HellaSwag`/`OpenBookQA`/`PiQA`/`SciQ`/`Winogrande`）+ **Table 3 的 6 个**（`GSM8K`/`MATH`/`BBH`/`MMLU`/`HumanEval`/`MBPP`）。
  4. **当前状态（用代码里的实时数，别照抄旧数）**：`step 330/5000`、`~37.6 s/iter`、`ETA ~2026-10-07 21:00`、`loss 4.36↓`、health OK（0 NaN/0 skip）；⚠️ **`SAVE_INTERVAL=5000` → 无中间 ckpt**（如实写风险）。
  5. **下一步**：5000 步完 → ckpt → HF → `lm_eval` Table 2（8 集）→ 填 `DATA_MIX_RECIPE.md` 实测值；**Decay 臂**待 `SFT-Agent-2609` s0/s1 分词完成。
  6. **它最终服务于什么**：**P-8（正式预训练）的投料配比** —— 即论文 Stage (i) 的配方依据。
- **数据来源**：`BAIZE_DATA_TASK.md §0.6-B` · `MEMORY_DATA.md` · `EXPERIMENTS*` · `run/baize_mix_stable_s0a.sh`（**贴命令 + 原始输出 + 路径**，铁律）。
- **产出**：`report_data_mix_s0a.html`（**自包含、无 CDN**，放 `doc/BaiZe-ISEDA2027/`）。

> ✅ 本块生效即视为已批准；**纯 CPU/写作，不占 GPU、不干扰 S0a 训练**。


### 🆕 运维指令 · 2026-10-05（晚 · ✅ **D-CLEAN-4 定案：保留不动**；+ 环境隔离纪律）

> **用户裁定（2026-10-05 晚）**：「**D-CLEAN-4 …… 不是昨天已经说了，剩下的保留不动嘛**。」

- ⇒ **D-CLEAN-4 终止**：**不再删除、也不再盘点**（此前「待拍板」**作废**）。请把 `MEMORY_DATA.md` / `run/DISK_CLEANUP_INVENTORY.md` 里 D-CLEAN-4 的状态改为「**已裁定 · 保留不动**」，并**停止**在报告/流水里把它列为「待拍板」。
- **红线重申（不变）**：`EDA-Eval-PyAether` 只读隔离区、base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k **均不可动**。

**环境隔离纪律（治「同机争用」—— 用户裁定）**
- **训练/长跑 = 共享 `py310`**（不动）；分词/转换等 CPU 重活照旧；**需要大量装包时另起独立 conda env**（🚫 别动共享 `py310`，避免重蹈 P-9.8 armB 被污染崩溃）。
- 你与 pretrain 共用 `.29` GPU（**GPU2–7 归你 / GPU0–1 归 pretrain**）—— **不许 kill 对方进程**，重 I/O 继续避让。

> ✅ 本块生效即视为已裁定。


### 🆕 运维口径 · 2026-10-05（**你的 shell 被剥了代理 ⇒ 一切「外网不可达」先按本口径显式带 proxy 复测**）

> **定位（运维 2026-10-05 13:2x，跨线）**：三条 loop 启动 cline 时都执行 `env -u http_proxy -u https_proxy -u … cline …`（见 `baize_data_loop.sh:114-120` / `baize_harness_loop.sh:106-116`）——**目的是给内网网关鉴权**（不剥 → 网关 `error: Forbidden`，且 cline 仍 exit 0 → 静默空转）。⇒ **你（agent）会话里每条命令都继承了「无代理」env。**
> ⇒ 因此 `pip` / `git fetch|push github` / `hf` 报 **`Network is unreachable`（Errno 101）/ http `000`** 是**预期现象**：🚫 **不代表集群禁网、不代表镜像被墙、也不代表 key/repo/凭据问题**——**别把它写进结论**。
> 🔧 **正确用法（🚫 不要去改 loop 的剥代理，改了会让网关 403）**：**凡访问外网的那一条命令，自己显式带上代理**（内网 hub / 网关 / `ssh 10.239.2.29|.12` 都**不要**带）：
> ```bash
> P=http://172.19.92.25:13128                          # `.29` 的代理（见 ~/.bashrc:140）；在 `.12` 上请用你自己 ~/.bashrc 里的那个值
> https_proxy=$P http_proxy=$P git fetch origin        # git 拉
> https_proxy=$P http_proxy=$P git push origin main    # git 推（本地已 ahead 的提交这样就上去了）
> python -m pip install --proxy $P --index-url https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com <pkg>
> ```
> ✅ **同机反证**：`run/harness/r1_eval.py:144-148` 正是**显式钉 proxy + 阿里云索引**，所以**同一台 `.29`** 上 pip 装包一直成功；relay 侧 git 也通（`run/ops/outbox.md` RUN_ID 28：「外网 无 proxy=FAIL / 有 proxy=OK」，内网网关两种都 200）。
> 🚫 **装包别动共享 py310 env**（P-9.8 arm B 崩溃即「共享 env 被污染」所致；P-9.9 现在还在跑）→ 用 `--target` 或独立 venv，起服时补 `PYTHONPATH`。

### 🆕 运维指令 · 2026-10-05（**🟢 分卡协调：`.29` GPU2–7（6 卡）归你 → 开始做「配比实验」，与 pretrain 的对比评测并行**）⭐ 高优先 · **已批准**

> **用户拍板（2026-10-05）**：「**给 pretrain 补一个对比评测任务**（要 GPU）——**它不需要 8 张卡**；**让它和 data 协调一下：pretrain 做对比评测时，data 可以同时做数据配比试验**。」
> ⇒ **§0.6-B 的配比实验，卡终于有了**（此前一直卡在「等 `.29` 让卡」）。

#### ① 卡的分配（**铁律** —— 完整账本见 **`run/GPU29_ALLOC.md`**）

| 机器 | 卡 | 归谁 | 用途 |
|:--|:--|:--|:--|
| `.29` | **GPU 0–1** | pretrain | P-9.10 推理对比评测（≤2 卡） |
| `.29` | **GPU 2–7（6 卡）** | **data（你）** | **数据配比实验** |

- ⏳ **起跑前置**：**先等 P-9.8 arm B(FP8) 跑完**（它现在占满 8 卡，ETA ~09:49）——
  判断依据：`run/MEMORY_PRETRAIN_2B.md` 状态头 + `ssh 10.239.2.29 nvidia-smi`。
  **等待期间你继续做「文献调研重做」（上方块）—— 那是当前最高优先。**
- 📢 **动态让卡（双向）**：你**只碰 GPU2–7**；要更多卡（或 pretrain 要更多卡）→ **在 `run/GPU29_ALLOC.md` 的「申请区」写一行**（几张/多久/为什么），
  **等对方在「臂边界 / step 边界 / 任务边界」让出**；🚫 **不许抢跑、不许 kill 对方进程**。
  **你自己的「臂与臂之间」就是天然让卡点**（每臂约 25–50 min）。
- 🚫 **`/nas_train` 是 `.12` 与 `.29` 共享的同一块 NFS**：你与 pretrain、vision 同盘 ⇒ **重 I/O（全量扫描 / 解包 / `du`）照旧避让**。

#### ② 怎么在 `.29` 上跑（你常驻 `.12`）
- **代码/数据不用搬**：工作副本是**共享 NFS**（`/nas_train/app.e0031982/code/super_intelligence_2035`，两台看到的是同一份）。
- 用 **`ssh 10.239.2.29 '<cmd>'`（免密已通）** 起训练；🚫 **不要在 `.12` 上再跑同一任务**。
- **第一件要做的事 = 只读可行性核查**（把**原文**贴进 `MEMORY_DATA.md`）：
  1. `ssh 10.239.2.29 'nvidia-smi --query-compute-apps=pid,process_name,used_memory --format=csv'` → 确认 **GPU2–7 空**（若有**他人进程 → 停手报告**）；
  2. 找 pretrain 的现成脚本 / recipe：`run/baize_p5b_train.sh`、`run/baize_p9*.sh`、`code/BaiZe-ISEDA2027/scripts/train.sh`、`code/BaiZe-ISEDA2027/pretrain_launcher.py`
     （参考 `run/BAIZE_PRETRAIN_2B_TASK.md` §R2.2 的固定口径）；
  3. 训练数据 `.bin/.idx` 是否就位；`PYTHONPATH` / python 环境能否起（见 `MEMORY_PRETRAIN_2B.md`「关键笔记」）。
- 🔑 **不要从零发明**：**复制** pretrain 的脚本成**你自己的** `run/baize_mix_*.sh` 再改配比；🚫 **不要改 pretrain 正在用的脚本文件**。
- ⚠️ **若环境/权限确实起不来**（ssh 不通、环境装不上…）→ **立即如实报告**（贴原文）并在 `run/GPU29_ALLOC.md` 写一行
  → **降级方案：你出「配比矩阵 + 数据切分 + 评测口径」，由 pretrain 代跑**（它已在 `.29` 上）。

#### ③ 实验设计（**沿用 §0.6-B，不要重造**）
- 搜索空间照 §0.6-B 的 **Stable / Decay 两张表**。
- **口径**：**6 卡 · TP1/DP6 · `seq=4094` · `mb=1`** · **GBS 与既有基线对齐**（若必须改 GBS → **在报告里显式写出并说明可比性**）· **5000 步短地平线**（或更短，但**所有臂必须一致**）。
- 每臂跑完 → 跑 **§0.6-B 的两套代理指标**：
  **Table 2 的 8 个**（`ARC-C` / `ARC-E` / `BoolQ` / `HellaSwag` / `OpenBookQA` / `PiQA` / `SciQ` / `Winogrande`）+
  **Table 3 的 6 个**（`GSM8K` / `MATH` / `BBH` / `MMLU` / `HumanEval` / `MBPP`）。
- **评测基建请复用 pretrain 已打通的 `ckpt → HF → lm_eval`**（见 `MEMORY_PRETRAIN_2B.md`）；Table 3 那 6 个若缺 → **先评估工作量并报告**，不要闷头造。
- **每臂必记**：配比百分比 · loss · 代理指标分项 · 命令 · 路径 · **GPU 核验原文**。

#### ④ 交付与优先级
- 交付：`run/DATA_MIX_RECIPE.md`（§0.6-C 原定：**具体百分比 + 试验次数 + 实测值 + 可复现命令**）；
  每臂一行进 `MEMORY_DATA.md` / `DATA_LEDGER.md`；**做不完就交「已完成臂 + 缺口」**，🚫 **不许凑数**。
- **优先级**：**文献调研重做（上方块）≥ 本块** —— 等 armB（~09:49）这段时间**先干文献**；armB 一完就**两件事并行**（你 6 卡 / pretrain 2 卡）。
- 🚫 **全轮不得出现领域化相关内容**（既有硬规矩，不变）。

> ✅ **本区块生效即视为已批准** —— 无需再等拍板。

### 📉 记忆维护规程（2026-10-03 运维新增，**硬性**）
> 理由：`MEMORY_*.md` **每次唤醒都被 agent 全文读取** → 越大越烧 token。当前 `MEMORY_DATA.md` ≈ **85KB（超标）**。
- **上限**：本线 `MEMORY_DATA.md` 控制在 **≤ 32KB**；**下次唤醒立即执行一次滚动归档**。
- **滚动**：把**较早的唤醒流水条目**（保留最近 ~20 条）**追加**到 `daily-memories-data/<条目日期>.md`（原文不改），再从 MEMORY 删除。
- **顶部必须保留**：① `WAITING:` 行（**仍只出现一次**）② 「进度快照」③ 「运维问答」（**这一区不清**，因运维靠它读答复）④ 最近 ~20 条流水。
- **纪律**：归档**不改变任何结论**；`WAITING:` 纪律不变。

---



| 项 | 当前值 |
|:---|:---|
| **🆕 D-CLEAN-4（2026-10-04 · 最新）** | 🔴 **`/nas_train` 需要清理 → 用 sudo 盘点各目录大小，找可删除的大目录，重点 `/nas_train/app.e0031982`**；**只盘点不删除**；🚫 绝不整树 `du`（只用 `df` + 有界定向 `du`，每条带 `timeout`）→ 详见顶部「运维指令 · 2026-10-04（D-CLEAN-4）」 |
| **🆕 下载白名单（2026-10-03 最新 · 覆盖一切下载类指令）** | **只下 ① `ultrafineweb_l1_en_hq` + `ultrafineweb_zh`（base 族剩余）② GPIC**；🔴 **立即停 `ultrafineweb_en_v1_4`**（43 天 / 非必需 / 阻塞后两项）；🚫 **白名单外一律不下载、不调研、不推荐**（含 `UltraX-Preview`）→ 详见顶部「运维指令 · 2026-10-03（下载白名单锁定）」 |
| **当前指令** | 🎯 **（2026-10-01 夜 · 三次修订）按序做这几件**：<br>**① ⭐ 重下 `UltraData-SFT-2605`** —— 运维**已在 HF 网页点同意条款**（原先 `gated=auto` 卡住，落盘只有 README + LICENSE + 179 个 `.lock`）。下完报**实际字节数 + 文件数 + 与 HF 官方清单的一致性**。<br>**② 🔴 当前主攻 = §0.3 + §0.4「R2 阶段」** —— 上一轮 R 的**事实层合格、结论层不合格**（两处）：<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.3（LLM 侧 / P-8 数据方案）**：你拿 **"BaiZe 计划未用"** 当理由跳过了 `Ultra-FineWeb`(base) / `UltraX-Preview` / `UltraData-RL-2609`，**那是循环论证**（计划是在不知道这些源存在时定的）。<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.4（视觉侧 / 找更多图文对）**：你**自己**给了「视觉编码器训练数据**严重不足**」的结论（`en500k` 仅 50 万对、LLaVA 85M 的 caption 99.7–100% 被截断），**却从没去 HF 找过任何通用图文对** —— 反而把问题缩小成「要不要找 EDA 版图/原理图」然后答「不值得」。**那是答错了题。**<br>&nbsp;&nbsp;&nbsp;&nbsp;**本轮两份都要交**：**8 源事实表填满（无 `?`）· base vs L3 重叠率数字 · P-8 三档投料+下载清单** **＋** **本地多模态源逐条实测 · ≥10 个 HF 通用图文对候选（含实测短 caption 率）· 前 3 推荐 + 下载命令**。<br>&nbsp;&nbsp;&nbsp;&nbsp;🚫 **禁止"待定"/"视情况"/"不在计划内"/"不值得找"（除非先给出找过的清单与规模）**；**若判定为新增且磁盘允许 → 直接开始下载**。<br>&nbsp;&nbsp;&nbsp;&nbsp;💡 **⚠️ 一条新增的硬筛条件（运维补充）**：**必须筛掉「只有 image URL、没有 image bytes」的数据集** —— 本地 `Recap-DataComp-1B` 就是**只有 URL**，而那些 URL **绝大多数被公司网络限制、下不下来**，**等于不可用**。<br>&nbsp;&nbsp;&nbsp;&nbsp;**→ A / B 两表都要新增「图像形态」列（`bytes` / `URL-only` / 待抽验），且必须抽分片实测取证（贴原文）；URL-only 一票否决、不得进推荐。**<br>&nbsp;&nbsp;&nbsp;&nbsp;⚠️ 预期会被淘汰的"大集"：`LAION-*` / `COYO-700M` / `DataComp-1B` / `DFN-*` / `RedCaps` / `YFCC` / `CC12M` / `CC3M` / `SBU` / `WIT` / `PixelProse` / **`Recap-DataComp-1B`（已确认）** —— 若大集普遍 URL-only，<b>请把重心转到"小一些但真的带图"的集</b>，并如实说明这个现实。<br>**③ 🚫 两条硬规矩（运维 2026-10-02）**：**（a）10 月份不要再提任何"领域化"相关的事** —— EDA / 领域语料 / Stage (ii)「领域模型」**全部留白**（运维：「一段时间有一段时间的主要矛盾」→ 当月专注 **Stage (i) 与 Stage (iii)**）；⚠️ 唯一例外：`EDA-Eval-PyAether` 158 任务的**黑名单红线照常执行**。**（b）当前主攻 = §0.5 + §0.6 + §0.7** —— **§0.5**：推 `Ultra-FineWeb`(base) 下载 + 处置 `/nas_train` 1.67TB 旧副本；**§0.6**：🎯 **P-8 数据配方 —— follow MiniCPM5/Xmodel-2 的 WSD 双阶段配比**（用 Xmodel-2 Table 2 的 8 个 + Table 3 的 6 个做代理指标做实验定）；<br>&nbsp;&nbsp;&nbsp;&nbsp;**§0.7 🆕（运维 2026-10-02 追加）**：① 🚫 **停掉 85M（LLaVA）下载**（优先级最低，释放带宽给 base 与 gpic）；② ⭐ **给出 base 下载 ETA**（分"复用旧副本/不复用"两种）；③ ⭐⭐ **复用 `/nas_train` 那 1286 个 `ultrafineweb_en`（≈1.67TB ≈ 全量 56%，省 ≈2 天）**；<br>&nbsp;&nbsp;&nbsp;&nbsp;**优先级**：**base（stage (i) 要用）> 配比实验 > gpic（stage (iii) 要用）> 85M（已停）**。 |
| **优先级覆盖** | **§0.5/§0.6/§0.7（base 下载与估时 / base-en 复用 / P-8 配比实验）> 其他一切**；<br>SFT-2605 重下**继续并行**（已过半）；<br>🚫 **85M（LLaVA）下载已按要求停下**；<br>`phase1/2/4`（重 I/O，等下载）**本阶段不碰**；<br>🚫 **领域化相关一律不碰**（10 月份） |
| **状态索取** | `<无>`（若运维写入具体问题，本轮**先答该问题**再干活，答案写进 `MEMORY_DATA.md` 顶部的"运维问答"区） |
| **暂停标志** | `<无>`（若写入 `STOP`，本轮**只更新记忆、不做任何 I/O 与数据处理**，然后退出） |

---

## 📊 进度快照（**每次唤醒必须更新**，供远程巡检）

> 固定格式写在 **`MEMORY_DATA.md` 最顶部**，便于运维一条命令读到全局状态。

```
PHASE:        <当前阶段>
已完成:       <阶段清单>
当前动作:     <本次唤醒在做什么>
下一步:       <下次唤醒要做什么>
阻塞:         <无 / 具体阻塞 + 需要运维做什么>
ERROR_COUNT:  <n>
```

⚠️ **`WAITING` 只写在 `MEMORY_DATA.md` 的顶部单独一行**（`baize_data_loop.sh` 用 `^WAITING:[[:space:]]*1` 匹配它来决定睡眠时长）。
**绝不要在正文、快照或流水里再出现以 `WAITING:` 开头的行**——否则会误触发 30 分钟长睡。
（pretrain loop 就是因为正文里出现了一句 `WAITING: **1**` 的散文而被误匹配，一直在长睡。）

**运维巡检方式**：外部运维通过 `git pull` 读取 `MEMORY_DATA.md` 顶部 + `DATA_LEDGER.md` + `CONTAMINATION_CHECK.md` 即可掌握进度；**不需要登录服务器**。

---

## 0. 🎯 当前主攻

> **R 阶段（只答两问）✅ 已收敛** → 产出 `run/DATA_RESEARCH.md` v1.1（事实层扎实）。
>
> | 节 | 状态 |
> |:--|:--|
> | §0.1 / §0.2 | ⏹ **历史**（R 阶段的两问，已完成；§0.2 已被 §0.4 取代） |
> | **§0.3** | 🔴 **当前主攻（LLM 侧）** —— P-8 数据方案 |
> | **§0.4** | 🔴 **当前主攻（视觉侧）** —— vision encoder 训练数据：去 HF 找更多通用图文对 |
>
> 原因：上一轮 R 的**事实层合格、结论层不合格**（两处，详见 §0.3 与 §0.4 开头）。
> **本轮两份都必须给出可执行的结论。**

---


---

## 📁 调研轮次已归档（**为省 prompt token**）

`§0.1 / §0.2 / §0.3 / §0.4`（R 与 R2 调研）的完整任务原文已移至 **`run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`**。

- 这些**均已完成**；结论以 `DATA_RESEARCH.md` / `DATA_LEDGER.md` / `MEMORY_DATA.md` 为准。
- **需要时再去读归档**；**不要**把整份归档读进上下文。
- 当前主攻 = **§0.5 / §0.6 / §0.7**（见下方）。

## 0.6 🎯 R4 阶段 —— **P-8 数据配方：follow MiniCPM5 / Xmodel-2 的 WSD 双阶段配比**（运维 2026-10-02 指令）

> ### 定位
> 运维明确：**P-8 的数据方案要「follow MiniCPM5」** —— 即 **WSD 的两段各用不同配比**：
>
> | 阶段 | 数据源（运维给的假设） | 主次 |
> |:--|:--|:--|
> | **Stable**（WSD 的 S 段） | `Ultra-FineWeb`(**base**) · `UltraX-Preview` · `UltraData-Math` · `UltraData-Code` | **以前两者为主** |
> | **Decay**（WSD 的 D 段） | `Ultra-FineWeb-L3` · `UltraData-Math` · `UltraData-Code` · **`UltraData-SFT-2605`** · **`UltraData-SFT-Agent-2609`** | 适当配比 |
>
> **配比不是拍的，要做实验定** —— 由你（data agent）来设计并跑。

### 🔴 一条可能改变全局的发现（来自 `Xmodel-2/xmodel-2.tex:144-154`，请务必读原节）

Xmodel-2 的 decay 段配比搜索结论：

> - 把搜索空间收敛到**两个问题**：**① SFT 数据的总体占比；② SFT 内部的类别分布**
> - **跑了 400+ 次试验** → 最优 **SFT 占比落在 60%–69%**，实际取 **64%**
> - SFT-Mixed 由 **5 类构成：Mathematics / Code / Logic / Knowledge / Commonsense**（**CoT 归入 Logic**）
> - **数学与代码的「指令格式」数据 > 「预训练格式」数据**
> - SimHash 去重（bucket 1M）**+1.7%**；整体复杂推理 **+29.31%**

⚠️ **关键含义**：**SFT 数据是进到「预训练 decay 段」里的，而不是事后再做一遍独立的 SFT** ——
这与运维给的 decay 假设（含 `SFT-2605` + `SFT-Agent-2609`）**一致**，也与 MiniCPM 的路线一致。
→ **它模糊了 Stage (i)/(ii) 的边界**：**decay 段本身就是"带 SFT 数据的退火"**。
→ **必须在报告里点明这一点**（这是 P-8 配方的核心）。

**另一条法理依据**（供报告引用）：`xmodel-2.tex:142` 引 `ye2024datamixinglaws` ——
**「小模型上的配比实验可以有效迁移到更大模型」** → **所以我们可以在小规模上搜配比**，不必在全量上试。

### A. 先**核实**运维的假设（不许直接采信，也不许否掉）

1. **MiniCPM5 的 stable/decay 两段各用了哪些源、什么占比？**
   - 上轮结论是「模型卡**未公开逐源百分比**」→ **本轮再查**：模型卡 / 技术报告 / `openbmb/MiniCPM5` collection 的 dataset card / UltraData 平台论文（arxiv 2602.09003）。
   - **若仍查不到** → 写「未找到」+ 列出查阅清单，**但运维给的这张表就作为"待验证的工作假设"直接用**（见 B）。
2. **确认 `UltraX-Preview` 与 `Ultra-FineWeb`(base) 的关系**（上轮已知 UltraX 里有一支叫 `UltraX-Ultra-FineWeb`）→ **是否重复**？

### B. ⭐⭐ 配比搜索实验（**本轮的核心**）

**搜索设计（照 Xmodel-2 的思路收敛空间）**：

| 段 | 候选源 | 代理指标 | 备注 |
|:--|:--|:--|:--|
| **Stable** | `base` · `UltraX-Preview` · `Math` · `Code` | **Xmodel-2 Table 2 的 8 个**（Commonsense） | 运维假设"以 base / UltraX 为主" |
| **Decay** | `L3` · `Math` · `Code` · `SFT-2605` · `SFT-Agent-2609` | **Xmodel-2 Table 3 的 6 个**（Complex Reasoning） | ⚠️ **必查 SFT 占比**（Xmodel-2 是 **60–69%**） |

**两套代理指标的确切清单**（已从本地 tex 核出，照用）：
- **Table 2（8 个）**：`ARC-C` · `ARC-E` · `BoolQ` · `HellaSwag` · `OpenBookQA` · `PiQA` · `SciQ` · `Winogrande`（+ Avg）
  —— 出处 `Xmodel-2/xmodel-2.tex:198,207`
- **Table 3（6 个）**：`GSM8K` · `MATH` · `BBH` · `MMLU` · `HumanEval` · `MBPP`
  —— 出处 `Xmodel-2/xmodel-2.tex:73,253,260`

**执行要求**：
1. **不要在 2.2B 全量上试** —— 用**小模型 / 短跑**搜（依据 Data Mixing Laws）。
   **基线口径**：复用 Round 1/2 的 8 卡 setup 与 5000 步短地平线，或更短。
2. **每轮训练后跑上面两套指标**（**评测基建已就绪**：P-6 已把 `ckpt → HF → lm_eval 8 集` 打通，
   见 `MEMORY_PRETRAIN_2B.md`；Table 3 的 6 个需另接，评估一下工作量）。
3. **给出可执行的配比建议**（不是"趋势"，是**具体百分比**），并说明**试验次数与置信度**。
4. **明确 SFT 占比**：这是 Xmodel-2 说最关键的一个轴。

> ### 🎯 **用哪台机器 —— 运维定的规则（2026-10-02）**
> **配比实验用「它所服务的那个正式训练」所用的机器**（因为配比实验与正式训练之间有依赖关系）：
>
> | 配比实验服务于谁 | 用哪台 | 卡 |
> |:--|:--|:--|
> | **LLM pretrain（P-8，即 §0.6 的 WSD 双阶段）** | **`.29`** | LLM 的卡 |
> | **vision（若将来也做配比）** | **`.12`** | vision 的卡 |
>
> **→ 本节 §0.6 的配比实验用 `.29`**（运维原话：**LLM pretrain 的正式训练依赖配比实验**）。
> ⚠️ **`.29` 上的排期**：P-4R（1 卡，≤2h）→ **配比实验** → 恢复 P-5b。
> **三者都在 `.29`，需要串行/让卡 —— 请先出方案与 ETA，再由运维排。**
> ⚠️ **`.12` 上 vision 的 R9 正在用 8 卡 → 不要占 `.12`。**

### C. 交付物
1. **`run/DATA_MIX_RECIPE.md`**（新文件）：
   - 运维假设的**核实结论**（或"未找到"+采纳为工作假设）
   - **两段的配比建议**（具体百分比 + 理由 + 试验次数）
   - **代理指标的实测值**（Table 2 / Table 3 分项 + Avg）
   - **可复现命令**
2. **P-8 数据就绪清单**：每个源是否就位、缺多少、下载/切分 ETA。
3. 更新 `MEMORY_DATA.md` + `DATA_LEDGER.md` + git push。

### 完成判据
- [ ] 运维假设**已核实**（或明确"未找到"+ 列出查阅清单）
- [ ] **Stable 段**配比给出**具体百分比** + Table 2 实测
- [ ] **Decay 段**配比给出**具体百分比**（**含 SFT 占比**）+ Table 3 实测
- [ ] 报告里**点明"decay 段即带 SFT 的退火"**这一含义
- [ ] 🚫 **全轮不得出现领域化相关内容**（运维硬规矩）

---


---
## 1. 任务目标

把已在盘上的原始语料，变成**训练可直接消费、配比正确、且不污染评测集**的形式。产出五类（见方案文档 §2.2）：

1. 通用文本 stable 主体（mcore `.bin/.idx`）
2. 退火混合源（code / math）　~~EDA~~ **← 🚫 已取消**（运维指令区 ②；与评测集同源，无意义）
3. 多模态训练集（webdataset tar）
4. 多模态 held-out 评估集
5. **污染隔离白/黑名单 + 校验脚本（红线，P0）**

**上游方案文档（先读它）**：`doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_PLAN.html`
**时间线约束**：ISEDA 2027 投稿截止 ≈ **2027-02-01**；本任务必须在 **2026-11 底**前可交接（见方案 §6）。

> **注意本任务的定位**：瓶颈是**算力窗口**不是数据量（方案 §2.1）。
> 所以**不要**把精力花在"下载/切分更多数据"上，而要花在**质量、配比、格式可用性、隔离**上。

## 1.1 数据落盘地图（实测背景 · 2026-10-01 勘定）

> 本节由**实地探查**得出，用于纠正本任务书成稿时对数据位置的误记。
> 每轮唤醒 / phase 复核时以此节为索引，`DATA_LEDGER.md` 为实测明细，二者互相印证；**最终一律以实测为准**。

**三块挂载 + 三条 HF 组织名线索**（HuggingFace 数据集按 `org/repo` 落盘）：

| 挂载 | 定位 | 关键内容 |
|:---|:---|:---|
| `/nas_train/app.e0031982/datasets/` | **多模态主库**（生产 + 派生） | `mvp-lab/`（LLaVA-OneVision-1.5 全家桶）、`baize-vision/`、coco/gqa/imagenet/laion2B/FineVision/LLaVA-Pretrain/MMMU… |
| `/nas_inference/app.e0031982/datasets/` | **只读源 / 下载中转**（**纯文本主力在此**） | `openbmb/`（Ultra-FineWeb-L3、UltraData-Code/Math/SFT-2605/SFT-Agent-2609）、`stanford-vision-lab/gpic` |
| `/nas_user/app.e0031982/datasets/` | 少量多模态 / 领域语料 | `mvp-lab/`（OV1.5 webdataset、OV2）、`BLIP3o/`、`UCSC-VLAA/`、`Amshaker/`、`ayoubkirouane/`、`cxmt/` |

**① 多模态主库 —— `/nas_train/app.e0031982/datasets/`**
- `mvp-lab/`（⚠️ 是连字符 **`mvp-lab`**，不是 `mvp_lab`）— LLaVA-OneVision-1.5 系列：
  - `LLaVA-OneVision-1.5-Instruct-Data`（183 个任务子集，SFT / 对齐主体）
  - `LLaVA-OneVision-1.5-Mid-Training-85M`（子集 coyo/datacomp1b/imagenet/laioncn/mint/obelics —— 即 phase0 已盘点项）
  - webdataset 派生：`-packed-webdataset` / `-webdataset` / `-webdataset-16384` / `Quick-Start-3M` / `MultiMixQA-opt46|47`
  - `LLaVA-OneVision-1.5-RL-Data`、`LLaVA-558K-Webdataset`、`LLaVA-NeXT-780k*`
- `openbmb/Ultra-FineWeb`（纯文本，**仅** Ultra-FineWeb 基础版，非完整 Ultra-* 套件）
- `baize-vision/`（en500k / eval5k —— vision agent 派生产出）
- 其他多模态（可选补充源）：`coco`、`gqa`、`imagenet-1k`、`laion2B-en-aesthetic`、`FineVision`(188 子集)、`LLaVA-Pretrain`(664 子集)、`MMMU`、`ocr_vqa`、`textvqa`、`vg`、`conceptual-captions-12m-webdataset`、`LLaVA-CC3M-Pretrain-595K`、`LLaVA-Instruct-150K`
- 非数据（勿混）：`stanford-corenlp-full-2016-10-31`（NLP 工具，非斯坦福视觉数据）

**② 纯文本主力 —— `/nas_inference/app.e0031982/datasets/openbmb/`**
- `Ultra-FineWeb-L3`（Stage(i) 主体）、`UltraData-Code` / `UltraData-Math`（退火源）、`UltraData-SFT-2605` / `UltraData-SFT-Agent-2609`（Stage(ii) SFT）
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/openbmb`，实际在 **`/nas_inference`** 挂载。

**③ 斯坦福视觉数据 —— `/nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic`**
- ⚠️ 成稿时误写为 `/nas_train/.../code/super_intelligence_2035/stanford-vision-lab`，实际在 **`/nas_inference`**。`gpic`（含 train / test / reference_stats）。

**④ 少量多模态 / 领域 —— `/nas_user/app.e0031982/datasets/`**
- `mvp-lab/`：`LLaVA-OneVision-1.5-Mid-Training-85M-webdataset`、`LLaVA-OneVision-2-Data`、`ov2_quickstart`
- `BLIP3o/BLIP3o-Pretrain-Long-Caption`、`UCSC-VLAA/Recap-DataComp-1B`、`Recap-DataComp-1B`
- `Amshaker/Mobile-O-Pre-Train`、`ayoubkirouane/CircuitVQA`
- `cxmt/`（EDA / 电路相关标注与 benchmark —— ~~phase3 领域排查时可查~~ **🚫 该线已取消，不再排查**）

> 对数据 agent 的影响：phase0 已盘点的主路径（`/nas_inference/openbmb`、`/nas_train/datasets/mvp-lab`）正确；
> 但 phase0 尚未覆盖 `②` 里的 Ultra-FineWeb 基础版（`/nas_train/.../openbmb`）、`③ stanford-vision-lab/gpic`、`④ /nas_user` 整块 —— 后续 phase 复核时把这些补齐进 DATA_LEDGER。

---

## 2. 阶段与推荐执行顺序

```
推荐顺序： 【🎯 当前】phase1 validate（含 ① SFT-2605 重下） → phase0 inventory ✅ → phase5 isolation ✅ → phase2 text → phase4 mm → phase6 handoff
🚫 phase3 domain —— **已取消，从流水线移除**（见运维指令区 ②）
```

> **为什么 phase5（污染隔离）排在最前**：它必须在**任何"训练可消费产物"产出之前**就位。
> 如果先切了数据再立闸，已经切好的数据要全部重扫、甚至重切——**白做一遍**。

| 阶段 | 做什么 | 完成判据 |
|:---|:---|:---|
| **R** `research` 🎯 **当前主攻** | 用 `cimi-search` / `cimi-fetch` **只回答 §0 的两个问题**（LLM 数据够不够+配比 / Vision 数据够不够+配比） | `DATA_RESEARCH.md`：两问各四小项全有结论 |
| **phase0** `inventory` ✅ | 对 `/nas_inference` 与 `/nas_train` 上每条数据线**实测**：文件数、总字节、目录结构、抽样看格式；确认哪些路径真实存在 | `DATA_LEDGER.md` 初版；**与方案 §1 的差异逐条列出** |
| **phase5** `isolation` | 建 EDA-Eval-PyAether 的黑名单指纹 + 训练集侧扫描脚本 + SFT 同闸 | `CONTAMINATION_CHECK.md` 初版 + 可复用脚本 |
| **phase1** `validate` | 下载完整性（parquet 全量可开 / tar 可解 / shard 无缺号）；损坏清单 | 损坏/缺失清单 + 校验命令 |
| **phase2** `text` | 通用文本分词打包成 `.bin/.idx`（stable 主体 + 退火源），**复用 Round 1 脚本** | 训练实测能加载并跑 10 步冒烟 |
| **phase3** `domain` 🚫 **已取消** | ~~EDA 领域语料排查（有哪些、在哪、能否导出/授权）→ 确认后入库并过闸~~<br>**运维 2026-10-01 正式取消**：评测 prompt 由 docstring 生成、**与语料天然同源**，"把测试集放进训练集"没有意义 | —（不再产出） |
| **phase4** `mm` | 多模态下载完成后：校验 → 统计 → 切子集 → webdataset 打包 → held-out 评估集 | Stage (iii) 能直接开跑 |
| **phase6** `handoff` | 清单终版 + 污染报告终版 + 结果 HTML + 可复现命令 | 可交接给训练 |

---

## 3. 红线：污染隔离（**违反则全部下游结论作废**）

🚨 **`EDA-Eval-PyAether` 的 158 个任务内容（`prompt` / `entry_point` / `test` 断言；注：v20260311 版无 `canonical_solution` 字段，见 DATA_LEDGER §1.3）
绝对不能进入任何训练集。** 改写/paraphrase 也不洗白。

- ✅ **允许**入训练集：PyAether / SKILL 的 **API 参考文档**（它是任务的"来源材料"）
- ❌ **禁止**入训练集：评测任务的 prompt、函数名、参考解、断言代码，及其改写版
- 机制必须包含：① 黑名单指纹 ② 训练集侧扫描 ③ **阈值写明可复现** ④ **SFT 语料同闸** ⑤ 独立报告
- 同一条规则适用于**多模态 held-out 评估集**（如 `eval5k`）：与训练集不同源 + 跨集去重比对

**评测集本体路径**（用于建黑名单，**只读，绝不写入任何训练集**）：
`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`

---

## 4. git 与共享工作区规则

### 4.1 前提：这是一个**共享工作副本**

**本任务、vision 任务、pretrain 任务共用同一份工作副本**——同一个 NFS 路径
`/nas_train/app.e0031982/code/super_intelligence_2035`（两节点共享同一块盘）。

- **只需一个人 pull，其余立刻看到**：别的 agent 拉取后，你读到的 `$TASK_MD` 与所有文件同步更新。**不要重复 pull。**
- 工作区里**陌生的未提交改动很可能是别的任务的在途文件**。🚫 绝不为此执行
  `git checkout -- <file>` / `git clean` / `git stash` / `git reset --hard`——那会毁掉别人的成果。
- 多个 loop 各自 `git add -A && commit && push`（每 5 小时），**会互相把对方在途文件一起提交**，这是既有设计的已知副作用，**不要去"修正"它**。

### 4.2 你的 git 操作规程

1. `git fetch origin` + `git status -sb`，看 ahead/behind。
2. **提交时显式指定你自己的文件**：
   `git add MEMORY_DATA.md DATA_LEDGER.md CONTAMINATION_CHECK.md run/data_pipeline/ daily-memories-data/`
   🚫 **不要用 `git add -A`**——会把别的任务的在途文件卷进你的提交。
3. 若 behind / diverged：`git pull --rebase origin main`。
   - `cannot rebase: You have unstaged changes` → 是**多方在途改动**：先 commit 自己要提交的文件再 rebase；🚫 不要 stash/丢弃别人的改动。
   - `Unable to create '.git/index.lock'` → **另一个 agent 正在做 git 操作**：等 30–60 秒重试（≤3 次）；仍失败就记一行流水并**跳过本次 git 操作**。
   - 🚫 **绝不** `git push --force`；🚫 **绝不** `git reset --hard`。
4. `git push origin main`；确认 `git status -sb` 无 ahead/behind。
5. 流水记一行 git 结果。

> 参照：vision agent 在 `daily-memories-vision/2026-10-01.md:198` 用 `git pull --rebase` 恢复过，沿用同一做法。

### 4.3 数据产物**不入库**

`.bin/.idx`、webdataset tar、原始数据集**一律不提交 git**。只提交：`doc/` 下的文本（md/html/json）与 `run/` 下的**脚本**。
在报告与流水中写清产物的**绝对路径 + 规模 + 校验和**，训练侧据此取用。

---

## 5. 资源与约束

- **节点**：本 agent 常驻 `10.239.2.12`（主机 `whag0pgpuap12`）；数据在 NFS（`/nas_inference` 只读源、`/nas_train` 产出）。
- ⚠️ **与 GPU 任务共享 NFS 与带宽**：
  - **本节点 `.12` 有 2 个 HF 下载任务在跑**（`hf download`，2026-10-01 实测，各已运行约 1 小时+）：
    1. `mvp-lab/LLaVA-OneVision-1.5-Mid-Training-85M` → 写入 `/nas_train/app.e0031982/datasets/`（多模态下载进行中）
    2. `stanford-vision-lab/gpic` → 写入 `/nas_inference/app.e0031982/datasets/`（带 HF token；⚠️ token 已暴露在进程参数里，建议轮换，勿写进文档/日志）
    **下载期间不要做重 I/O / 全量扫描**，会互相拖慢
  - vision 任务需要一次"**无争用的干净吞吐测量**（R2-4）" → 启动重 I/O 前先读 `run/MEMORY_VISION.md` 看它进度，**优先避让**
  - pretrain 任务在 `10.239.2.29` 跑训练（另有协调规则）
- **不占用 GPU**（本任务不是 GPU 任务）；也**绝不杀他人进程**。
- **每轮唤醒单次预算 ≈ 25 分钟**；有长时任务时把 `WAITING` 置 1 让 loop 拉长睡眠。

---

## 6. 记忆管理

| 文件 | 作用 |
|:---|:---|
| `run/MEMORY_DATA.md` | 运行时状态：**顶部"进度快照"**（固定格式，供远程巡检）+ PHASE/WAITING/看板/流水 |
| **`run/DATA_RESEARCH.md`** | 🎯 **调研报告（当前主攻）**：只回答两个问题（LLM / Vision 的数据够不够 + 配比），每条含 URL / 规模 / 许可 / 可得性 / 建议 |
| `run/DATA_LEDGER.md` | **数据清单**（核心产出）：路径 / 规模 / 用途 / 状态 / 与方案 §1 的差异 |
| `run/CONTAMINATION_CHECK.md` | **污染隔离报告**（红线留证）：规则 / 阈值 / 扫描量 / 命中 / 处置 |
| `run/data_pipeline/` | 可复现脚本（盘点 / 校验 / 去重 / 分词打包 / 指纹比对） |
| `run/daily-memories-data/$(date +%F).md` | 当日操作日志 |

启动恢复：读本文件 → 读 `MEMORY_DATA.md` → 读 `DATA_LEDGER.md` → 读当日日志 → 判断下一步 → 执行 → 回写。

---

## 7. 验收产出

1. 🎯 **`DATA_RESEARCH.md`（调研报告，当前主攻）** —— **两个问题各四小项全部有结论**，每条关键结论可顺 URL 复核
2. `DATA_LEDGER.md`（数据清单，含**实测**规模与与方案文档的差异）
3. `CONTAMINATION_CHECK.md`（污染隔离规则 + 阈值 + 扫描量 + 命中 + 处置）
4. `run/data_pipeline/`（可复现脚本，至少含盘点、校验、分词打包、指纹比对）
5. 训练可消费的产物（`.bin/.idx` + webdataset），**路径与校验和写入清单**
6. `doc/BaiZe-ISEDA2027/BAIZE_DATA_PREP_RESULT.html`（自包含，与既有 HTML 报告同风格）
7. git commit + push（只提交 doc/ 文本与 run/ 脚本）

---

## 8. 推进原则

- **无阻塞时连续推进**：把能立即做完的步骤一口气做完（可跨多个阶段），直到遇到必须等待的异步任务或单次预算将尽（约 25 分钟）。
- **有异步阻塞时**：回写记忆并把 `WAITING` 置 `1`，记录"等待什么、如何判断结束"，然后退出。
- **不确定就如实记录并上报**，不要编造数据、不要产出"看起来对"的合成语料。

