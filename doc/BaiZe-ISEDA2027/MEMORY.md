# MEMORY.md — BaiZe-ISEDA2027 **运维（operator）** 长期记忆 · **醒来先读本文件**


## 🆕 最近操作（2026-10-08）

### 🔬 给 pretrain 下发 Round 3 数据配比 BO 搜索指令
- **背景**：data agent 已完成 R3 方案定型（`run/BAIZE_DATA_R3_TASK.md`），正式交接给 pretrain 团队执行。交接文档明确写「pretrain 负责：代码改造、脚本落地、执行」。
- **R3 搜索规格**：6 维单纯形（ultrafineweb_en/zh/l1_en_hq + UltraX-Preview + UltraData-Code/MATH），100 trial × 1B token/trial，全量 lm_eval（无 `--limit`），~19.5h ≤ 24h，8 卡满跑。
- **为什么现在做**：pretrain 全 8 GPU 空闲（等 P-8 分词/下载就绪至少还需 2–3 天），R3 只需要小样本分词 ~30min + 19.5h BO，**正好利用空窗期**，跑完直接定 P-8 Stable 配比，不占 P-8 时间。
- **指令已下发至** `run/BAIZE_PRETRAIN_2B_TASK.md` 顶部（最高优先级，置于论文更新/报告之前）。
- 同期义务（论文更新/R2 报告）：**抽空做**（纯 CPU），不延迟 R3 主干 Step 1–3。

### 💬 给 vision / harness 下发「下一步工作建议」征询指令
- **背景**：两条线（vision R2–R14 全线收敛、harness 7-way 横评全完成）均已空闲（WAITING=1, GPU idle），全部交付物已完成。距 ISEDA 2027 投稿还有 ~4 个月，在 Stage (iv)/(ii) 正式启动前有大量前置准备空间。
- **指令**：在 `BAIZE_VISION_TASK.md` / `BAIZE_HARNESS_TASK.md` 各新增运维指令块（2026-10-08③ / ④），要求 agent **不执行实验、纯写作**，在各自 `MEMORY_*.md` 的「运维问答」区回答 4–5 个问题（未验证假设 / Stage 前置准备 / GPU 空窗期利用 / 论文补充建议 / harness 侧多了 backbone 网格 pilot + 评测管线搭建）。
- **为什么**：运维不替 agent 拍脑袋——agent 自己最清楚实验数据里还有什么值得挖、什么前置工作能提前做。先听建议再拍板。

**commit pending**（待编辑本文件和更新 daily-memories 后一并提交）

WAITING: 0

> ⚠️ **本文件在项目根**（`doc/BaiZe-ISEDA2027/`），是**运维侧**（指挥 4 条线的那个"我"）的状态文件。
> **不属于任何 agent 线** —— 4 条线的记忆在 `run/` 下：`MEMORY_PRETRAIN_2B.md` / `MEMORY_DATA.md` / `MEMORY_VISION.md` / `MEMORY_HARNESS.md`。
> 日流水在根目录 `daily-memories/`（**不要**与 `run/daily-memories*/` 混）。
> 纪律：**`WAITING:` 只在顶部出现一次**；**≤32KB**，超限滚动到 `daily-memories/`。

---

## 0. 我是谁 / 我的角色

- 我是本项目 `doc/BaiZe-ISEDA2027` 的**外部运维**：**不登录训练机**。
- **下达通道** = 各任务书的 `## 🔧 运维指令区（OPERATOR NOTES）`（**改文件 + git commit/push**）。
- **查看通道** = 读各线的 `run/MEMORY_*.md` 顶部「进度快照」/「运维问答」+ `run/` 产物（`git pull` 即可，**不登录服务器**）。
- 我指挥的 4 条线：**pretrain**（`10.239.2.29`）· **data**（`.12`）· **vision**（`.12`）· **harness**（`.29`）。另有 **ops relay**（RUN_ID 机制，见 `run/ops/`）。

---

## 1. 每次「醒来」的固定动作（SOP）

1. **先同步**：`git fetch origin` → `git pull --rebase --autostash origin main`
   （远端推进很快——各 agent 每次唤醒都可能 push；**不 pull 直接改会冲突**）。
2. **读本文件**：尤其 §3 在途任务 / §4 待拍板 / §5 铁律。
3. **读 4 条线状态**：各 `run/MEMORY_*.md` 顶部 + `git log --oneline -20` + `run/ops/.last_run_id`。
4. **处理回写**：有 agent 产物/答复 → 读、核、必要时答复（写进对应任务书运维指令区或该线「运维问答」）。
5. **下发新任务**：在对应任务书运维指令区加 **带日期的 block**（**越靠前越优先**；老块不改，留作历史）。
6. **提交**：`git add` **只加自己动的文件** → `commit` → `push`。**不要 `git add -A`**。
7. **回写本文件 + 当日 `daily-memories/<date>.md`**。

---

## 2. 通讯协议 / 接口（关键认知）

- **接口 = 任务书的「运维指令区」**，四条线**现在都有**：
  - `run/BAIZE_PRETRAIN_2B_TASK.md` · `run/BAIZE_DATA_TASK.md` · `run/BAIZE_VISION_TASK.md` · `run/BAIZE_HARNESS_TASK.md`
  - ⚠️ **pretrain / vision 的任务书原本没有该区，是 2026-10-03 由运维补上的**。
- **下发格式**：`### 🆕 运维指令 · <日期>（摘要）` + 正文；**新块放前面**，写清 **优先级 / 顺序 / 判据 / 铁律**。
- **各线回写位置**：`run/MEMORY_*.md`（状态头 + 进度快照 + 运维问答 + 流水）、`run/daily-memories*/`、`run/EXPERIMENTS_*.md`、各线产物目录。
- **ops relay**：还可经 `run/ops/inbox.md` 下 RUN_ID 命令（⚠️ **只执行第一个 ```bash 块**；下发须把新块放最前、旧块降级为 ```text、RUN_ID +1）。

---

## 3. 在途任务（截至 2026-10-08）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | 🔄 **R3 数据配比 BO（6 维 / 100 trial）运行中**：DB 32 行（31 complete + 1 failed=#24），best=**trial#8 score=0.4032**；第 5 批 trials 32–39 训练中 ~62–75%，**0 NaN**；PID 2637043（ppid=1），8 卡 62GB/55–90% util，**ETA ~05:50 Oct 9**。R2 全线 ✅ / 论文 ✅ / 收官报告 ✅ / R3 脚本 + 小样本分词 6/6 ✅（10-07⑤ T1–T4 ✅：float32 vs bf16 SSM **无差异**，「dense 3.3× faster」系 warmup 假象已撤回） | `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` · `BAIZE_DATA_R3_TASK.md` | 🟢 `.cline_pretrain`；**P-8 暂缓令（10-02）仍未撤** |
| **vision** | 🔄 从「全线收敛」转入 **AIMv2 缩放对比实验（2026-10-08⑤，用户直令；同日修订）**：**E1 = 同族 OV2 w512/d30 126.78M** vs **E2 = 同族 w768/d30 284.54M（2.24×，只差宽度）**，均 224/p16、**从零**、同 AIMv2 objective + 同 94.9M + 同 1 epoch；主指标 **IN-1k lp Protocol B**（3 seeds）；预注册 Δlp ±1.5pp。⚠️ R9 实测 w768 吞吐 ≈ w512（2978 vs 2938 img/s）⇒ 两臂 ETA 同量级。顺序：登记 `.12` 8 卡 → smoke 报 ETA → 开跑。背景：BP-1/2/3 已锁定；R9 阶段一（InfoNCE/15.36M）w512 6.10% > w768 3.63% | `run/EXPERIMENTS_VISION*.md` · `report_vision_aimv2_scaling.html`（待出） | 🟢 `.cline_vision`；`.12` 8 卡空闲 |
| **data** | 🔄 分词收尾 + 下载：`zh` 8/8 ✅112.47B · `l1_en_hq` 12/12 ✅152.17B · `ultrax` 10/10 ✅30.97B · `en_base` s24–s33 @24%（ETA ~04:30 Oct 9）；**累计 317.67B tok（≫ P-8 目标 100B）**；GPIC **6167/8001**（ETA ~1.7d）；base ✅ / UltraX ✅479 / `en_v1_4` 排队 | `report_data_*.html` · `DATA_MIX_RECIPE.md` · `BAIZE_DATA_R3_TASK.md` | 🟢 `.cline_data`；**配比实验已交接 pretrain 执行（R3）** |
| **harness** | ✅ **7-way × 30 全完成**（cline-patched 60.0% · Pi 60.0% · Hermes 53.3% · opencode 50.0% · codex 46.7% · claude-code 43.3% · deepseek-harness 40.0%）；报告 4 份已交付；无运行中 chain → 🆕 **已下发 2026-10-08⑤：① 第二轮 7×100 横评（先报 ETA）② 深挖第一轮交互轨迹 + 逐 harness 特点对比表** | `run/harness/SWEBENCH_COMPARE.html` · `kimi_pilot_results.json` | 🟢 `.cline_harness`；**先做②（纯 CPU）再跑①** |

> ✅ **vision 叙事已决（2026-10-03 用户）：走 A = 保持「从零训练」**（"A 本身也是为了学习"）。
> → R9 的 **~25.1% 渐近 = 从零路线的如实上限**（负结果有价值）；**loss 轴 R11 = 主线**；**架构轴非主要杠杆**。
> → 登记 **R12（候选）**：仅补 **iGVLM 式指令条件化**（TuringViT 低优先 —— attention 仅占 0.7%）；**须先报"值不值得"再批**。
> → 参考 **`run/VISION_ARCH_FRONTIER_2026.md`**（前沿 5 方向 vs 我们 R8 已测 4 个的逐项对照）。

---

## 4. 待拍板 / 我欠的答复

- [ ] **P-9 结果** → 定 **P-8 的 seq(4096/8192) / MBS / 精度(bf16/FP8)**（含 16384 是否 OOM 的长上下文边界）。
- [ ] ⭐ **P-8 配置拍板**（等 **P-9.7 定稿 + P-9.8 长程一致性 + P-6② token 预算**三件齐 → 再定）。现有建议 = **候选A `TP4·SP·MBS8·seq8192·FP8·MAX_CONN=1`（235K tok/s）**；⚠️ 前置未齐（base 下满 ~2.7 天 + 配比 §0.6 未做）→ 🚫 **不得顺手启动 P-8**。
- [ ] ⭐ **vision AIMv2 缩放对比实验（2026-10-08⑤，用户直令）**：**E1** = 同族 OV2 **w512/d30 126.78M** vs **E2** = 同族 **w768/d30 284.54M（2.24×）**，均 224/p16、**从零**、同 AIMv2 objective + 同 94.9M + **同 1 epoch**；主指标 **IN-1k lp Protocol B**（3 seeds → mean±σ），辅报 Protocol A + C1–C4 + 公平表；预注册 **Δlp ±1.5pp**（σ>Δ 判「不可分辨」）。**待回报**：smoke 两臂 ETA（R9 实测 w768 吞吐 ≈ w512 ⇒ ETA 同量级）→ 开跑。⚙️ 原「官方 L/14@336 304M」臂已按用户裁定**改为同族 w768**（只差宽度，避免 4 变量同变）；若仍要官方臂则另议。
- [ ] 🆕 **P-8 启动令再评估（2026-10-08）**：前置已大幅改善（分词 **317.67B ≫ 目标 100B**；GPIC 6167/8001 未满但 P-8 未必依赖）⇒ **待用户拍板是否撤 10-02「⏸ P-8 暂缓」令**；未撤前 🚫 不得启动。
- [ ] 🆕 **harness 第二轮 7×100 ETA（2026-10-08 下发）**：待回报总 ETA（首轮 210 run ≈34h 串行 ⇒ 700 run 估 ≈4.5–5 天）；**若不接受需另定**（减题量 / 允许并发 = 改口径）。
- [ ] 🆕 **vision / harness 各一份「运维问答」待我答复**：vision 2026-10-08③ 四问（未验证假设 / Stage iv 前置 / GPU 空窗 / 论文补充）· harness 2026-10-08④ 五问（横评深挖 / BaiZe 接入前置 / 扩规模 / 多 backbone pilot / 论文补充）。
> 📦 **§4 已闭合条目滚动归档**（2026-10-08 执行，原文未改一字）→ `daily-memories/2026-10-08.md`「从 MEMORY.md §4 滚动归档」= pretrain 四件（10-05 深夜2）· data/vision 三份 HTML（10-05 深夜2）· AIMv2 提速归因前置（10-05 晚）· data 三步令（10-06）· **harness deepseek 工具链（10-05，已装通）** · **R9「53M cap」口径修正（10-03）** · **R8「六架构=自研改编」结论边界（10-03，R13 官方对照已完成 79.81%）**。
- [ ] 💬 **另一「运维会话」在并行活动**（2026-10-04 深夜发现：origin 上出现**我没写过的 RUN_ID 63 诊断记录**）→ **需与用户确认是否统一到单一会话**，以免重复下发/互相覆盖。
> 📦 **data 三步令（2026-10-06）已闭合**（Stable 200-trial ✅ · `s_step` 归因 ✅ 166 ms · Round2 BO 200/200 ✅）→ 原文见 `daily-memories/2026-10-08.md`「从 MEMORY.md §4 滚动归档」。
> 📦 **归档指针（查旧决策去这里，勿再塞回本文件）**：① **`daily-memories/2026-10-03.md`「从 MEMORY.md 滚动归档」A 节** = D-CLEAN-2/-3 与回收量核实 · harness R1 沙箱路线 · GPIC E1 实测 + C1 口径 · H-A′ 放行 · docker 系降末选 · sudo 口令 · `ops_relay`「2 副本」误判结案 · 论文冻结 · vision 队列裁定 · data 白名单锁定；② **`daily-memories/2026-10-05.md`「从 MEMORY.md §4 滚动归档」** = 本区已闭合的 `[x]` 条目（AIMv2 改写授权 · D-CLEAN-4 定案 · harness 取 kimi · sglang 走 conda · 环境隔离纪律 · proxy 口径 · Claude Code 合规口径定案）—— **原文未改一字**。

> ③ **`daily-memories/2026-10-06.md`「从 MEMORY.md §4 滚动归档」**（2026-10-07 滚动）= **配比实验改道裁定 · 「实验」定义 5 条判据**。**原文未改一字。**
- [ ] ⛔ **loop 优化：暂不做（用户 2026-10-03 决定）** —— `SLEEP_WAIT 1800→3600` 与「训练未完成就跳过 cline 调用」都要重启 loop（需回公司），且会让反应变慢 → **待回公司后择机**。
- [ ] **文档口径统一**：seq 已定 4096（P-8 起），README/论文里残留的 4094 需对齐。
- [ ] 是否把关键决策合并进 `BAIZE_PROGRESS.html`（单一事实来源）。

---

## 5. 铁律与纪律

- 🚫 **绝不打断正在跑的 long-run**（尤其 **P-5b**：改 MBS/精度/seq 会让 20B loss 曲线作废）。
- 🚫 **绝不 kill 各线 watchdog loop**（`baize_*_loop.sh`）；收敛后只置 `WAITING=1` 长睡。
- **`WAITING:` 纪律**：只在各 `MEMORY_*.md` **顶部出现一次**（否则误触发 30 分钟长睡）。
- **记忆体量 ≤32KB**（**本文件 + 4 线 `MEMORY_*.md` 均适用**；超限滚动到 `daily-memories*/`）。
- **不许猜**：源码结论贴 `路径:行号`；实验结论贴 **命令 + 原始输出**。
- 🧷 **两条常驻纪律（细则在任务书「常驻规则」区）**：**① 环境隔离** —— 训练/长跑 = 共享 `py310`，需大量装包 = 另起独立 conda env（P-9.8 armB 被污染崩溃的教训）；**② 外网命令带 proxy** —— cline 会话继承「无代理」env，`pip`/`git fetch|push`/`hf` 报 `Errno 101`/`http 000` 是**预期**（非禁网/非 key 问题），**凡访问外网的那条命令自己显式带 proxy**（内网 hub/网关/ssh 不带）。
- 🚫 **不许闭门造车**（**2026-10-03 教训**）：凡涉及"别人怎么做"的结论（架构 / loss / 评测 / 数据），**必须去读官方仓库或论文原文**（能 `git clone` 就 clone），**不得凭印象或二手描述下结论**——当天我就把 R8 的**自研改编**误当成"官方实现"来下了结论。
- **预注册判据先定后测**（P-9a-ext G、R11 都用了）。
- 🔒 **红线**：`EDA-Eval-PyAether` 158 任务只读隔离区**绝不可动**；base/gpic 下载目标、L3/code/math、SFT、GPIC、en500k/eval5k 均不可删。
- ⚠️ **`run/nemo_experiments` 含 P-5b 正在写的 ckpt**，且 **P-6② 要用其中 6 个里程碑 ckpt** → 只能「先列清单、保住最晚/最优 + 里程碑，再删早期项」。
- **不占 GPU 的线**（data/harness）也要**避让 `.29`/`.12` 的训练 I/O**。
- 🚫 **不得让多条线共用一份可变配置目录**（cline 已按线 `--data-dir` 隔离）—— **共用 = 迟早互相踩**（2026-10-04 的反复 Forbidden 就是这么来的）。
- 🚫 **relay 块内每条可能慢的命令都必须有界**（`timeout N`）；重活丢 **后台 `setsid nice -n 19` + 落盘 + `.done`**；**绝不对大目录做全树遍历**。

---

## 6. 关键路径与事实速查

- **关键路径**：`P-5b → P-9 → P-6② → P-8`（P-8 = Stage(i) 本体，周级墙钟，仍暂缓等 base + 配比）。
- 🔴 **配比搜索形态已改（2026-10-06）**：**不再用 2.2B 跑单臂**，改 **小代理（定案 `h=512/L=14`=96.8M = 1/23）× Optuna BO × 6 卡并行 × 1 天/段**；**24h 目标 200–400 trial**。锚点 = `ye2024datamixinglaws` + Xmodel-2 `400+ 次试验`。⇒ **「等配比」的等待时间从「周级」降到「2 天」。**
- **两条硬口径（2026-10-03 定）**：
  - **seq 统一 4096**（P-8 起）；`4094` 仅存于正在跑的 P-5b。
  - **每步 ≈ 4M token 不变量**：`4096↔GBS1024` · `8192↔512` · `16384↔256` · `2048↔2048`。**总步数 = 总token/4M，与 seq 无关**。
- **FP8 机制**：`s` 取决于 **GEMM 的 M**，大 GEMM `M = MBS × seq`；**`M≳16K` 才 `s>1`**（seq 与 MBS 是等价杠杆）。
- **vision 现状**：R9 lp 渐近 **25.1%**（当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结CLIP文本塔 + InfoNCE**；⚠️ **不是 GPIC**）；`attention flash` 仅占 GPU 自耗 **0.7%**（P-4 profile）。
- 🚩 **`launcher` 只暴露 MBS / TP / SP / seq-length / precision**（agent P-9 非 GPU 预研，2026-10-03）→ **P-9 只用已暴露开关、不改 recipe**；B/C/E/F 类（recompute / 通信重叠 / dataloader / attn-backend）**冻结**，其中 **NCCL（P-4 占 41.7%）** 收益最大 → 记录在案、**待批准后另开**。
- **磁盘**：`/nas_train` 207T/剩 ~31T（86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- 🪶 **任务书瘦身（长期纪律）**：loop 是 `prompt="$(< TASK_MD)"` → **任务书全文 = 每次唤醒的 prompt**，必须保持小；已闭合块要移出（归档不进 prompt）。历次瘦身数字见 `daily-memories/2026-10-0{3,5}.md`。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——**通道就是 git**。
- 🔒 **cline 隔离目录（NFS 共享）**：`.cline_pretrain`（`.29`）· `.cline_vision` / `.cline_data`（`.12`）**均已切**、`Forbidden=0`、model=glm-5.2；`.cline_harness`（`.29`）**已建未切**。目录路径：`/nas_train/app.e0031982/.cline_<line>`。
- 🔎 **MCP / web search（2026-10-05 四线打通）**：`.29:8090` 的 `eda_fastmcp` SSE MCP 暴露 `cimi_search` / `cimi_fetch`（绑 `0.0.0.0` ⇒ `.12` 可跨机用）；**四线均实测成功（rc=0）**。⚠️ 配置路径「两台各一份」的坑见 §7。

---

## 7. 已知坑（会复发）

- 🟡 **`baize_vision_loop.sh` 无 `git pull`**（2026-10-03 复核脚本原文：只做 `git add -A` + `commit` + `push`，每 5h）—— **✅ 但不构成阻塞（用户 2026-10-03 确认）**：
  → **机制**：**仓库是共享的** —— **别的线（`baize_pretrain_loop.sh` / `baize_data_loop.sh` 都会 `fetch + pull --rebase --autostash`）拉一次，vision 在同一工作副本上就看到**我的任务书更新。→ 所以 `84d7990`（R11-L2 批准）**会经由 pretrain/data 的 pull 自然到达**，**无需任何专门处理**。
  → 🔧 **可选根治（需登机；非必须）**：`pkill -f baize_vision_loop.sh` → 照抄 `baize_pretrain_loop.sh`（自带 pull + 行首 `^WAITING:` 正则 + 只 add 本任务文件）→ 再 `setsid` 起。
  → ⚠️ 附带注意：它的 `git add -A` 会把**整棵树**的改动一起提交（不只 vision 文件）——共享副本上叠加时**可能误提交别线在途文件**。
- 🔴 **ops relay 的命令块：每一步都必须有界（2026-10-04 实测，我自己踩的坑）**：
  - **症状**：我在 RUN_ID 34 里写了 ① `fuser -v <dir>`（**没加 `timeout`**）② `grep -rln … /nas_train/app.e0031982/code`（该目录 **8 TiB**、海量文件）→ **块被卡住**，`timeout` 只杀 leader、**继承了 stdout 的子进程仍活着** → 中继读管道被挂住 → **`.last_run_id` 停摆 ~11 分钟**（自设 600s 超时都救不回）。
  - **铁律**：**每一条可能慢的命令都必须 `timeout N`**；**绝不对大目录做 `grep -r`/`du`/`find` 全树遍历**（改用：只扫小目录、`stat` 取 mtime、或把重活丢给**后台 `setsid nice -n 19`** + 写文件 + `.done` 标记，再由下一轮读）。
  - **正确的重活姿势**：`setsid nice -n 19 bash -c '… > /tmp/x.log 2>&1; echo done > /tmp/x.done' &` → 块本身秒回，结果边跑边落盘。
  - ℹ️ **中继会自愈**：RUN_ID 34 最终 `exit=124`（超时），但**它被杀之前已经把 `rm -rf` 跑了** → 后续块看到 "GONE" 秒过。⚠️ 所以**超时不等于没做**，务必用后续只读块核验事实（别信日志的"瞬时完成"）。

- `ops_relay.sh` 会跑出**多副本**（共享 `.last_run_id` → 重复执行）→ 保留 **`etimes` 最大**者。
- **WAITING 正则**：旧版 `WAITING:[* ]*1` 误匹配正文散文 → 已收紧为行首 `^WAITING:[[:space:]]*1`。
- `baize_vision_loop.sh` 只 push 不 pull 的缺陷**未修**（运行时不宜改脚本）→ 等它停再照抄 pretrain 新版。
- 本机 PowerShell 读 UTF-8 中文会乱码——**只影响显示**；校验用 `read_files`。
- 🌐 **本机外网「时通时断」的原因已查明（2026-10-03 用户确认）**：**用户开 VPN（用于 Google 搜索）时 GitHub 不通，关掉即通** → 抓 GitHub / HF 前先确认 **VPN 已关**；断连**重试即可**，不是仓库/权限问题。
- 🔴 **cline Token 额度会耗尽（2026-10-03 实测，重要）**：`/tmp/baize_harness_loop.log` 原文
  `error: 本次Token额度已用完，请等待16分钟6秒后重试` —— **但 cline 仍返回 `exit 0`** →
  **loop 分辨不出失败，只睡 30min 再试** → 表现为**"静默变慢"**（不是挂了）。4 线**共用同一 cline 模型**时会互相抢额度。
  → 排查入口：`/tmp/baize_*_loop.log`（**注意：`.29` 上只有 pretrain/harness；vision/data 在 `.12`，其日志不在 .29**）。
- 🔴🔴 **`.29` 的 cline 必须显式 `-k <key>`（2026-10-04 实战定位，~9h 停摆的真凶；含我自己的 4 次误修）**：
  - **现象**：`.29` 的 pretrain/harness 每个唤醒周期只打印 **`error: Forbidden`** + `cline returned (exit 0)` → loop 当成功、继续睡 → **完全静默**（pretrain 18 次 / harness 37 次）；同段 `.12` 的 vision/data 整夜正常。
  - **四路矩阵实证（RUN_ID 26，唯一可信依据）**：
    | 组 | env | 结果 |
    |:--|:--|:--|
    | V0 | 原样 | ❌ Forbidden |
    | V1 | 剥 `OPENAI_API_KEY+OPENAI_API_URL+API_TYPE` | ❌ |
    | V2 | V1 **+ 剥所有 `*_proxy`** | ❌ |
    | **V3** | **V2 + 显式 `-k <secrets 里的有效 key>`** | ✅ **OK** |
  - **叠加的两个故障**：① loop 继承的 `OPENAI_API_KEY=01_549…` 是**已吊销**的旧 key，**会覆盖** secrets.json 的有效 key（`02_088…`）→ 22:10–07:28 全程 Forbidden；② **即便**换掉/剥掉它，`.29` 的 cline **仍需显式 `-k`**（⚠️ **机制未完全解释**：07:28 那版不带 `-k` 也曾成功 11 分钟；而 `.12` 不带 `-k` 一直能跑）→ 故 **以 V3 为定稿**。
  - **已排除（都实测过）**：proxy 单独（`直连 200 / 走代理 503`，但剥掉不够）· `OPENAI_API_URL/API_TYPE` 单独 · 模型名 · `globalState.json`（`.29`/`.12` 字段一致）· **cline CLI 版本**（两台都是 **3.0.51**、安装于 2026-09-08；globalState 里的 4.1.21/4.0.8 是 VSCode 扩展版本，无关）· token 额度 · `.env` 里那几把 `*_API_KEY`（curl 全 **403**，不可用）。
  - **定稿修法**：两条 loop 顶部 `CLINE_KEY="$(sed -n 's/.*"openAiApiKey"…/\1/p' "$HOME/.cline/data/secrets.json")"`，cline 行 = `env -u <所有 *_proxy> -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE cline … -k "$CLINE_KEY" …`。**key 不落仓库**。
  - **可复用排查法（ops relay 只读块）**：① `pgrep -af 'baize_.*_loop.sh'` ② `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`（**精确探针**；`grep -c Forbidden` 会数到 agent 散文，**假阳性**）③ `nvidia-smi` 看 GPU 是否空转 ④ **多把 key 分别 `curl /v1/chat/completions`** ⑤ **env 矩阵 smoke**（**必须逐一控制变量**）。
  - ⚠️ **我的两次次生错误（务必引以为戒）**：**(a)** 用 `python3 -c` 在 loop 里取 key → relay 的非交互 shell **PATH 里没有 python3** → 静默取不到、退回 stale key；**(b)** 写 env 矩阵时**漏剥 proxy** → 三组全红、得出"key 失效"的错误结论，白绕 3 轮。→ **每次只改一个变量，并在同一块里验证该变量确实生效**。
  - ⚠️ **复发预防**：轮换 cline key 时**必须同时更新 `.12` 与 `.29`**；日常体检跑 `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`。
  - ✂️ **源头加固（RUN_ID 29，2026-10-04，用户批准）**：`.29` 的 **`~/.bashrc:170` 的 `export OPENAI_API_KEY=` 已原地注释**（**原值保留为注记**；备份 `~/.bashrc.bak.20261004-081247`）→ 目标是**单一真源 = `~/.cline/data/secrets.json`**。**`https_proxy`（同文件 :140）保留不动** —— 实测 `git ls-remote github` **无 proxy = FAIL / 有 proxy = OK**，删了 loop 的 push 就废。`API_TYPE`:169 / `OPENAI_API_URL`:171 保留（实测剥掉不足以修复）。
  - 📌 **`.12` 是现成范本**：它的 `.bashrc:143` 早就注释着 `# disabled: proxy DNS cannot resolve internal agi-gateway.cxmt.com`（9/29 那次修的）。
  - 🔧 **配套改动**：`run/harness/run_harness.py` 的 `ClineDriver` 改为 **`resolve_cline_key()` = env 优先、否则回退读 `~/.cline/data/secrets.json`**（并**纠正了原先写反的 GOTCHA 注释**）。→ 这样即使 env 里没有 key，driver 的 `available()` 也不会变 False。
  - ℹ️ **注意**：改 `.bashrc` **不影响已在运行的 loop**（进程 env 已固化），属"防未来"；loop 侧 V3 配方（剥 proxy + 显式 `-k`）保持不变。
- ⚠️ **`.29` 与 `.12` 的 `/tmp` 不共享** → 诊断 loop 日志必须**指明机器**；而**共享工作副本在 NFS**，所以**跨机能看到"别的线未提交的在途文件"**（这正是判断"某线是否在干活"的好办法）。
- ⚠️ **`ops_relay.sh` 的「多副本」是误判（2026-10-03 更正）**：`ps | grep ops_relay` 会看到 **2 行**，但其中一行是 relay **执行命令块时 fork 的子 shell**（`ppid` = 真 relay、`etimes≈0`）。→ **判别看 `ppid`**；**唯一真 relay 的 `ppid=1`**。🚫 **绝不要"把两个都杀掉"**（会切断远程通讯）。详见 `run/AGENTS.md` §3.5(1)。
- 🔴🔴 **4 条线共用一份 `~/.cline/data`（2026-10-04 深夜定位 —— 比 `-k` 更根本，且会反复复发）**：
  - **机制**：`.29` 上 pretrain 与 harness **共用 `globalState.json`**；harness 把它改成自己的 `gw_proxy`（`127.0.0.1:9090`）→ pretrain 的 cline 被指向**本地死代理** → `Forbidden`（而 cline 仍 `exit 0` → 静默）。**这解释了「修好 key 后还会复发」。**
  - **修法**：**按线隔离 `--data-dir`** —— `/nas_train/app.e0031982/.cline_{pretrain,harness,vision,data}`；pretrain/vision/data 已切（`Forbidden=0`），harness 目录已建、**按用户指示暂未切**。
  - **三个坑（都已解决）**：① **`--data-dir` 指向的是 data 目录本身**（文件放 `<D>/` 根，**不是** `<D>/data/`）；② **只播 `globalState.json`+`secrets.json` 不够** —— provider/base 也在 **`settings/`**（`providers.json`/`models.json`），漏了就 **`Cannot connect to API`**（**不是** Forbidden）；③ **ssh 非交互 shell 的 PATH 里没有 `bun`** → 需 `export PATH=$HOME/.bun/bin:$PATH`（否则 `/usr/bin/env: 'bun': No such file`）。
- 🔴 **relay 块里凡「可能读 stdin」的命令（尤其是 cline smoke）必须加 `< /dev/null`** —— 否则它会把 ssh heredoc 里**剩余的脚本当 stdin 吃掉** → 输出莫名截断，我因此**误判成「嵌套 heredoc bug」白绕两轮**。
- 🔴 **relay smoke 必须复现「loop 的真实 (model, base) 配对」** —— `llm_pick` 会选中「**curl 探针 200 但 cline 实际 403**」的候选（`deepseek-v4-flash @ /v1`）→ 我已给 `llm_rotate.sh` 加 **「优先 glm-5.2」**（`glm-5.2 @ /cloud/v1` 实测 cline 可用）。
- 🔴 **下发 relay 块的「最后一步」= 核对两件事**：顶部 `<!-- RUN_ID -->` **已 +1**，且 **文件已 push**。RUN_ID 50 曾因头标没加（`rid == last`）**卡了整整一轮**。
- 🌐 **`.29`/`.12` 的 GitHub 通道会「时通时断」⇒ `origin/main` 落后 ≠ 线停摆！** 判据 = `grep -c 'error:.*Forbidden' /tmp/baize_*_loop.log`（应 0）+ `nvidia-smi` util（是否真空转）。抖动时 agent **照常在本地提交**、只是推不上（曾见 `.12` `ahead 16`、`.29` `fetch FAILED`）；恢复后**积压会自动回补**。
- 💬 **可能另有「并行运维会话」** —— 2026-10-04 深夜在 origin 见到**我没写过的 RUN_ID 63 记录** → **下发前先 `git pull --rebase`**，遇冲突**保留双方**，勿互相覆盖。
- 🪟 **本机（Windows）工具坑**：① PowerShell 下 `git commit -m "…"` 遇 `()` / `->` / 全角括号会报「字符串缺少终止符」→ **一律 `git commit -F <临时文件>`**；② `Select-String` 对**中文/`$tag[...]` 插值**匹配不可靠 → **中文校验改用 Python**；③ 控制台是 GBK → Python `print` 中文/emoji 会 `UnicodeEncodeError` → **把结果写文件再 `read_files`**。
- 🔎 **MCP 配置不走 `--data-dir`（会复发）**：固定读共享 `~/.cline/data/settings/cline_mcp_settings.json`（与 `--data-dir` 无关）；`.29`/`.12` **各自本地一份**（非 NFS）→ **修 MCP 两台都要修**。⚠️ 探针坑：① SSE 端点不能 `curl -w '%{http_code}'`（长连接 → 空输出 → 误判）→ 只取响应头 `curl -sS -D - -o /dev/null`；② `cline mcp list` 无效 → 正解 `cline config mcp`。
- 💡 **诊断教训**：`baize_p5b_train.log` **只在 START/END 写**；**逐迭代日志是 `/tmp/baize_p5b.log`**（我 tail 错了文件，下次注意）。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **任务书同样 ≤32KB，且由各线 agent 自己滚动归档**（2026-10-06 用户裁定：与 MEMORY 同机制，**不再由运维代劳**；护栏 = 只搬迁已闭合块原文 + 留 1 行指针，不新增/不改写指令）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **🔬 2026-10-08（用户两条指令：harness 第二轮 7×100 + 交互轨迹深挖；vision 全量 1-epoch 耗时）** —— 已下发：
  - `BAIZE_HARNESS_TASK.md` 新增 **2026-10-08⑤**（① 第二轮 **7×100** 同题集横评，**先报 ETA**、口径与首轮逐字一致 ② **深挖首轮 7×30 交互轨迹** → 新报告 `report_harness_interaction_traces.html` + 逐 harness 特点对比表；**② 先做**，纯 CPU）。
  - `BAIZE_VISION_TASK.md` 新增 **2026-10-08④**（答「现有全部数据含 GPIC 6167/8001 训 1 epoch 多久」：逐源列 N=**≈94.9M 对**、两个 img/s 口径（R12 干净 4993 / R12b 有效 ≈2909）、墙钟 **≈5.5–9 h/epoch**、是否 >1 epoch；**纯 CPU 估算，非批准开跑**）。
  - 同步：`MEMORY.md §3` 四行状态更新为 10-08 实测 · §4 滚动归档 · 本日 `daily-memories/2026-10-08.md`。
  - ➕ **同日再下一条（用户直令）**：`BAIZE_VISION_TASK.md` 新增 **2026-10-08⑤ AIMv2 缩放对比实验** —— **E1**（同族 OV2 w512/d30 **126.78M**）vs **E2**（同族 **w768/d30 284.54M**，**2.24×，只差宽度**），均 224/p16、从零；**同 AIMv2 objective + 同 94.9M + 同 1 epoch**；主指标 **IN-1k lp Protocol B**，预注册 Δlp ±1.5pp；先登记 `.12` 8 卡 + smoke 报 ETA 再跑。⚙️ **同日晚修订**：E2 原为「官方 OV2 L/14@336 304M」⇒ 运维指出那会**同时改 4 个变量**（参数量/结构/patch/分辨率），**用户裁定改用同族 w768**（只差宽度）；官方臂若仍要则另议。

> 📦 **2026-10-08 早/午两条运维流水已滚动归档** → `daily-memories/2026-10-08.md`（**原文未改一字**：①「让 pretrain/vision/data 更新论文」`5cf87a53` ②「各线自己写报告」`e3afb272`）。**勿再塞回本文件。**


> 📦 **2026-10-07 流水已滚动归档** → `daily-memories/2026-10-07.md`（**原文未改一字**：harness 30 横评 · pretrain 2M–16M+显存归因+5 份研究 · data 解禁白名单 ＋ 撤销「15:30 定时停 UltraX」）。

- **🎯 2026-10-06（用户三步令 · data）** —— ① 收 200-trial（top-K `lm_eval`+Spearman+σ）② **`s_step` 归因**（1.5 s→**166 ms**，真凶 = `MBS=1`+GBS16 ⇒ 每步 16 个 microbatch；已升级 MBS×GBS 网格）③ `.29` GPU0-1 释放后 8 卡搜第二轮。**明细见 `daily-memories/2026-10-06.md`。**

- **📦 旧流水已滚动归档** → `daily-memories/2026-10-06.md`（**原文未改一字**：10-06「第 6 轮」/「第 5 轮块」/「两条流水（复核②、改道）」）。**勿再塞回本文件。**



- **📦 2026-10-04 / 2026-10-05 的 §9 流水已滚动归档**（2026-10-06 执行，压回 §8 上限；**原文未改一字**）→ `daily-memories/2026-10-05.md` / `daily-memories/2026-10-04.md` 之「从 MEMORY.md §9 滚动归档」（内容：合规口径·红线·任务书瘦身·FP8 裁定·harness 换模型·文献重做·EDA MCP ＋ vision 双批准·R11-F·`.29` 停摆事故）。**勿再塞回本文件。**
