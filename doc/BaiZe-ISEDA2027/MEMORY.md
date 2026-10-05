# MEMORY.md — BaiZe-ISEDA2027 **运维（operator）** 长期记忆 · **醒来先读本文件**

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

## 3. 在途任务（截至 2026-10-04 深夜 ~22:30）

| 线 | 在飞 | 预期产物 | 状态 |
|:--|:--|:--|:--|
| **pretrain** | ✅ P-5b(20B) + P-9.1–9.6①② + **P-9.7 A1 稳态**（~249K tok/s，ETA ~22:39 定稿）→ ⭐ **P-9.8 bf16 vs FP8 长程一致性 A/B（各 1000 步）已批准** → P-9.5 复跑 → P-6② → P-8 暂缓 | `run/EXPERIMENTS_PRETRAIN_2B_ROUND2.md` | 🟢 **`.cline_pretrain` 隔离目录**；凌晨空窗已排（P-9.5 → **P-9.8** → P-6②） |
| **vision** | ✅ R9/R10/R14/E1 + R11-L 四臂 + R11-L2 + caption-weight + **R11-E(未抬高)** + **R13(官方 OV2 79.81%)** 全完成 → ⭐ **臂⑥ AIMv2 翻盘**（lp 12.08% vs 基线 6.08%，**+6pp → 25.1% 渐近局部推翻**）→ 🔄 **R11-F 数据源横比运行中** → 🟢 **R11-G(AIMv2 长跑重拟合 scaling) + R11-H(⑥-B 纯 AR) 已批准**（见 `BAIZE_VISION_TASK.md`「运维指令 · 2026-10-04（七）」） | `run/EXPERIMENTS_VISION_ROUND11.md` · `VISION_OFFICIAL_REPOS_SURVEY.md` | 🔄 **`.cline_vision` 隔离目录**；凌晨空窗 ≈4–5h 已排满 |
| **data** | 下载巡检（白名单 = `l1_en_hq` + `zh` + GPIC；D-CLEAN ✅ 全完成）+ ⭐ **论文文献调研：`LIT_IDEAS_2026-10-04.html` 已交付（50 条/7 方向/成本专章）→ 已下发「在线核验」续任务** | `run/DISK_CLEANUP_INVENTORY.md` · **`LIT_IDEAS_2026-10-04.html`** | 🟢 **MCP（`cimi_search`/`cimi_fetch`）已修复并双机实测可用** → 核验任务已下发 |
| **harness** | ✅ **4/5 harness 端到端 `resolved=true`**（cline / codex / opencode / **claude-code**）→ **步4：300 × 5 全量按序跑** | `run/harness/SWEBENCH_LITE_FEASIBILITY.md` · `r1_eval.py` | ⚠️ **H-A pilot 扩容受阻**（github 网络瞬断，base_commit shallow clone 缺）；deepseek-harness 缺工具链 |

> ✅ **vision 叙事已决（2026-10-03 用户）：走 A = 保持「从零训练」**（"A 本身也是为了学习"）。
> → R9 的 **~25.1% 渐近 = 从零路线的如实上限**（负结果有价值）；**loss 轴 R11 = 主线**；**架构轴非主要杠杆**。
> → 登记 **R12（候选）**：仅补 **iGVLM 式指令条件化**（TuringViT 低优先 —— attention 仅占 0.7%）；**须先报"值不值得"再批**。
> → 参考 **`run/VISION_ARCH_FRONTIER_2026.md`**（前沿 5 方向 vs 我们 R8 已测 4 个的逐项对照）。

---

## 4. 待拍板 / 我欠的答复

- [ ] **P-9 结果** → 定 **P-8 的 seq(4096/8192) / MBS / 精度(bf16/FP8)**（含 16384 是否 OOM 的长上下文边界）。
- [ ] ⭐ **P-8 配置拍板**（等 **P-9.7 定稿 + P-9.8 长程一致性 + P-6② token 预算**三件齐 → 再定）。现有建议 = **候选A `TP4·SP·MBS8·seq8192·FP8·MAX_CONN=1`（235K tok/s）**；⚠️ 前置未齐（base 下满 ~2.7 天 + 配比 §0.6 未做）→ 🚫 **不得顺手启动 P-8**。
- [ ] ⭐ **AIMv2 翻盘 ⇒ 论文 / scaling 结论必须改写**（2026-10-04 新增）：`6_vision_encoder.tex`/§6 现在写的是「**25.1% 是从零路线的诚实天花板**」，而 **R11-G/⑥-B 结果**要改成「**换 caption-无关的稠密目标可突破该上限**」。**等 R11-G（108k 重拟合）+ R11-H（⑥-B 纯 AR）出数后与其余 3 项润色一次性回填**。
- [ ] **data：D-CLEAN-4 候选等拍板**（**只盘点不删除**）—— 本用户：`datasets/FineVision` **4.32T**（最大单点）· `HuggingFaceFW` 1.24T · CC12M 1.13T（⚠️ 是 vision 数据臂之一）· `chip_expert`+`models` 0.92T；跨用户：`wangcongtao` 2.42T + `app.e0025692` 0.95T（**需 sudo/owner**）。
- [ ] **harness：`deepseek-harness` 缺工具链**（node ≥22.13 + rust；镜像全 000/301/404）→ **需内网镜像或装工具链**；另 **H-A pilot 扩容被 github 网络瞬时中断挡住**（base_commit 在 shallow clone 中缺失）。
- [ ] 💬 **另一「运维会话」在并行活动**（2026-10-04 深夜发现：origin 上出现**我没写过的 RUN_ID 63 诊断记录**）→ **需与用户确认是否统一到单一会话**，以免重复下发/互相覆盖。
> 📦 **下列「当日已完成（[x]）」条目已原文滚动归档 → `daily-memories/2026-10-03.md`「从 MEMORY.md 滚动归档」A 节**：D-CLEAN-2/-3 与回收量核实 · harness R1 沙箱路线 · GPIC E1 实测 + C1 口径 · H-A′ 放行 · docker 系降末选 · sudo 口令 · `ops_relay` 「2 副本」误判结案 · 论文冻结 · vision 队列裁定 · data 白名单锁定。**（查旧决策请去该归档，勿再塞回本文件。）**
- [ ] ⛔ **loop 优化：暂不做（用户 2026-10-03 决定）** —— `SLEEP_WAIT 1800→3600` 与「训练未完成就跳过 cline 调用」的前置检查，**都需在公司重启 loop**（假期内做不了），且 1800→3600 **会让反应变慢**。→ **待回公司后择机**。
- [ ] 🚩 **R9 的「本地 53M 上限」是 `r9_scaling.py` 的假设常量（default=53），非实测** → 按 GPIC 采样应为 **≈103M**；**必须用真实 cap 重算所有 "×N 缺口"**（已在 vision 任务书下达「口径修正」）。
- [ ] 🚩 **R8 的 6 架构是「自研 from-scratch 等参改编」，非官方实现** → 「SSM 坍缩」不得推广为对官方架构的否定；要下"前沿行不行"的结论需做 **R13（官方 vs 自研 对照）**。
- [ ] **文档口径统一**：seq 已定 4096（P-8 起），README/论文里残留的 4094 需对齐。
- [ ] 是否把关键决策合并进 `BAIZE_PROGRESS.html`（单一事实来源）。

---

## 5. 铁律与纪律

- 🚫 **绝不打断正在跑的 long-run**（尤其 **P-5b**：改 MBS/精度/seq 会让 20B loss 曲线作废）。
- 🚫 **绝不 kill 各线 watchdog loop**（`baize_*_loop.sh`）；收敛后只置 `WAITING=1` 长睡。
- **`WAITING:` 纪律**：只在各 `MEMORY_*.md` **顶部出现一次**（否则误触发 30 分钟长睡）。
- **记忆体量 ≤32KB**（4 线已达标；超限滚动到 `daily-memories*/`）。
- **不许猜**：源码结论贴 `路径:行号`；实验结论贴 **命令 + 原始输出**。
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
- **两条硬口径（2026-10-03 定）**：
  - **seq 统一 4096**（P-8 起）；`4094` 仅存于正在跑的 P-5b。
  - **每步 ≈ 4M token 不变量**：`4096↔GBS1024` · `8192↔512` · `16384↔256` · `2048↔2048`。**总步数 = 总token/4M，与 seq 无关**。
- **FP8 机制**：`s` 取决于 **GEMM 的 M**，大 GEMM `M = MBS × seq`；**`M≳16K` 才 `s>1`**（seq 与 MBS 是等价杠杆）。
- **vision 现状**：R9 lp 渐近 **25.1%**（当前路线 = **OpenVision2 w512 + CC12M+Amshaker + 冻结CLIP文本塔 + InfoNCE**；⚠️ **不是 GPIC**）；`attention flash` 仅占 GPU 自耗 **0.7%**（P-4 profile）。
- 🚩 **`launcher` 只暴露 MBS / TP / SP / seq-length / precision**（agent P-9 非 GPU 预研，2026-10-03）→ **P-9 只用已暴露开关、不改 recipe**；B/C/E/F 类（recompute / 通信重叠 / dataloader / attn-backend）**冻结**，其中 **NCCL（P-4 占 41.7%）** 收益最大 → 记录在案、**待批准后另开**。
- **磁盘**：`/nas_train` 207T/剩 ~31T（86%）· `/nas_inference` 剩 20T · `/nas_user` 剩 29T。
- 🪶 **任务书瘦身（2026-10-03，为省 agent key 的 token）**：loop 是 `prompt="$(< TASK_MD)"` → **任务书全文 = 每次唤醒的 prompt**。
  已把**已完成轮次**移出 prompt：**vision 92.5→11.7KB** · **pretrain 57.1→32.9KB** · **data 60.1→42KB**
  （归档：`run/vision/ARCHIVE_ROUNDS_2-9.md` · `run/ARCHIVE_PRETRAIN_ROUND1_AND_DONE_R2.md` · `run/ARCHIVE_DATA_R_AND_R2_RESEARCH.md`）。
  → **4 份活跃任务书 237.2 → 114.1 KB（-52%）**，每次全唤醒省 ≈**41K prompt token**。
  ⚠️ 归档文件**不进 prompt**；agent **需要时才去读**（已在各任务书里写明指引）。
- **本机（Windows 侧）**：`C:\Users\liuyu\super_intelligence_2035`（git clone）；**可 fetch/pull/push GitHub**；**不能直连 `.12`/`.29`**（SSH 超时）——**通道就是 git**。
- 🔒 **cline 隔离目录（NFS 共享）**：`.cline_pretrain`（`.29`）· `.cline_vision` / `.cline_data`（`.12`）**均已切**、`Forbidden=0`、model=glm-5.2；`.cline_harness`（`.29`）**已建未切**。目录路径：`/nas_train/app.e0031982/.cline_<line>`。
- 🔎 **MCP / web search（2026-10-05 已四线打通）**：`.29:8090` 的 **`eda_fastmcp` SSE MCP** 暴露 **`cimi_search` / `cimi_fetch`**（服务绑 `0.0.0.0`、`.12` 可跨机用）。⚠️ **cline 的 MCP 配置走「共享」路径** `~/.cline/data/settings/cline_mcp_settings.json`（**不随 `--data-dir` 变**；`.29`/`.12` **各自本地一份**）→ 修 MCP **要两台都修**。**四线均已逐一实测 `cimi_search` 成功（rc=0）**：pretrain/harness（`.29`）· vision/data（`.12`）。

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
- 🔎 **MCP 配置不走 `--data-dir`（2026-10-05 实测，会复发）**：cline 的 MCP 配置固定读 **共享** 的 `<config>/data/settings/cline_mcp_settings.json`（`~/.cline/data/settings/`），**与 `--data-dir` 无关**；且 `.29`/`.12` **各自本地一份**（**不是 NFS**）→ **修 MCP 必须两台都修**。⚠️ **两个探针坑**：① **SSE 端点不能用 `curl -w '%{http_code}'` 探测**（长连接永不结束 → 超时被杀 → **空输出**，会误判成"服务不可用"）→ 应 **只取响应头**（`curl -sS -D - -o /dev/null`）或抓首帧（`curl -sN`）；② **`cline mcp list` 不是有效子命令** → 正解 **`cline config mcp`**。
- 💡 **诊断教训**：`baize_p5b_train.log` **只在 START/END 写**；**逐迭代日志是 `/tmp/baize_p5b.log`**（我 tail 错了文件，下次注意）。

---

## 8. 记忆维护规程（对我自己）

- **上限 ≤32KB**；超限把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，长期归档）。
- **顶部永久保留**：`WAITING:` 行 · §1 SOP · §5 铁律 · §4 待拍板（未完成项）。
- 每天一条 `daily-memories/<YYYY-MM-DD>.md`：**用户指令 → 处置 → commit → agent 回报**。
- ⚠️ **本文件在项目根**；agent 线的记忆在 `run/`——**不要混**。

---

## 9. 流水（倒序）

- **2026-10-05（早 · 🔧 修好 data agent 的「网络问题」：EDA MCP 全链路打通）** —— 用户指出 `.29:8090` 有 `eda_fastmcp` 的 SSE MCP（含 `cimi_search`/`cimi_fetch`）、与中继同机、跑通后 `.12` 也能共用。**RUN_ID 64→69 一路做完**：④ 服务**本来就在跑**（`pid=111692`、**绑 `0.0.0.0:8090`**、`.env` 已有 `EDA_MCP_PORT=8090`）· ⑤ 用**正确探针**（SSE 长连接不能用 `curl -w http_code`）确认 **`/sse` 200 + `event: endpoint`**、**`.12` TCP/HTTP 均可达**、工具名 **`cimi_search`/`cimi_fetch`** · ⑥ 发现 **`--data-dir` 不改变 MCP 配置读取路径**（cline 固定读共享 `~/.cline/data/settings/cline_mcp_settings.json`），且 **`.cline_vision`/`.cline_data` 是 22B 空**（RUN_ID 55 重播覆盖所致）· ⑦ 修回 **206B**（含 cimi 工具入 autoApprove）· ⑧ **`.29` 真跑 `cimi_search` → `rc=0` 返回真实结果** · ⑨ **`.12` 的共享配置同样为空（22B）→ 备份并补上** → **`.12` 真跑 `cimi_search` → `rc=0`**。⇒ **两机都能用 MCP 搜索**（此前「`api.bocha.cn` SSL 阻断」已不复现）。**顺带三处自查**：SSE 探针方法错（我的锅）· `cline mcp list` 不是有效子命令（正解 `cline config mcp`）· smoke 一度用错 key 报 Forbidden（同 RUN_ID 56 的老坑）。**已下发续任务**：让 data agent 用 MCP 把 `LIT_IDEAS_2026-10-04.html` 的 15 条未核验 + DeepSeek-Flash 定价 + ISEDA 页数 + 2026 最新工作补齐为「全部一手核验」。**随后（RUN_ID 70）把 web search 扩到其余三线**：`.29` 共享配置的 `autoApprove` 补上 `cimi_search`/`cimi_fetch`（265B→206B，已备份）→ **pretrain / harness（`.29`）与 vision（`.12`）各真跑一次 `cimi_search`，均 `rc=0`、Tool available=yes**；四线 `cline config mcp` 全部显示 `pyAether_MCP_server [sse]` ⇒ **四条线都可联网检索了**。

- **2026-10-04（深夜 · 论文定位 + 文献调研下发）** —— 用户给出**论文定位与商业命题**：① 第 1 读者 = **公司领导 + 约 1400 位 DE**（目的是**技术影响力**，投中 ISEDA 是加分）；② 核心命题 = **ZhuLong 让 1400 DE 用上 EDA agent → token 成本急剧上涨 → ≈2027 H2 BaiZe「救场」分档承接流量（达到 DeepSeek-Flash 的 70–80% 指标，成本 ~1/100）**；③ 前沿+经典平衡；④「录用率」次要；⑤ 不必刻意逐条对照现有结果。**关键澄清**：data agent 有**我没有**的 MCP 工具 **`cimi-search` / `cimi-fetch`** → 「集群能不能上网」的可行性问题解决，调研交它做。→ 下发 **`BAIZE_DATA_TASK.md` 顶部「附加任务 · 最高优先」**：7 个方向（**方向 0 = 成本/服务经济性（蒸馏·级联·路由·推理成本口径）为最高优先**；1 SLM 预训练 / 2 LLM 后训练 / 3 vision encoder / 4 MLLM 训练 / 5 MLLM 后训练 / 6 论文质量横切）、**证据规则**（一手优先、可核验标识、二手须标"未核"）、**交付** = 自包含 `LIT_IDEAS_2026-10-04.html`（TL;DR + 主表 8 列 + 三档 + 「成本救场」专章 + 参考清单；按可行性×潜力排序 + TOP-10），**明早 08:30 前**；完不成交「已完成 + 缺口」。巡检 4 项并行照做。

- **2026-10-04（深夜 · 本文件维护）** —— MEMORY.md 一度达 **31.8KB**（逼近上限）→ 按 §8 规程**滚动归档**：把 **2026-10-03 的 §4 已完成项 + §9 流水**原文迁入 `daily-memories/2026-10-03.md`「从 MEMORY.md 滚动归档」（A 节 / B 节）；同时把本轮新认知写进 **§4**（P-8 拍板 / **AIMv2 翻盘 ⇒ 论文·scaling 改写** / D-CLEAN-4 / deepseek-harness / 并行会话）、**§5**（不得共用可变配置目录 · relay 有界）、**§6**（cline 隔离目录）、**§7**（共用 `~/.cline/data` 的真因与 3 坑 · smoke 必带 `< /dev/null` · 必须复现真实 (model,base) 配对 · RUN_ID 头标 · **`origin` 落后 ≠ 停摆** · 并行会话 · Windows 工具坑）。**现 29.7KB ≤ 32KB ✅**。

- **2026-10-04（深夜 · pretrain 填卡）** —— 用户指出「pretrain 也有凌晨 GPU 空闲」→ 先核 **pretrain 自己的规划**（`MEMORY_PRETRAIN_2B.md`「下一步」）：**P-9.7 定稿（~22:39）→ P-9.5 复跑（修 `torch.profiler`）→ P-6②（能力 vs token scaling + 外推，决定 P-8 token 预算）→ P-8 暂缓**（前置未齐：base 下满 ~2.7 天 + 配比 §0.6）。我补的填卡项：**P-9.8 = bf16 vs FP8 长程一致性 A/B（各 1000 步）**，依据是 **P-9.6② 自己标注的风险**「60 步短测 loss 持平 ≠ 长跑收敛一致，若 P-8 用 FP8 前 500 步须与 bf16 对照」而 **P-8 推荐候选A 正是 FP8**。用户选定「**队列照跑 + 追加 P-9.8**」→ 下发 **`BAIZE_PRETRAIN_2B_TASK.md`「运维指令 · 2026-10-04（P-9.8）」**（载体 TP4·SP·MBS8·seq8192=FP8 转正点；两臂各 1000 步 / GBS512；**四条预注册判据**：同步 loss 差 ≤1% · nan/skip=0 · grad-norm 漂移 ≤10% · 逐 100 步最大偏离 ≤2%；四条全过才「FP8 可用于 P-8」；**08:30 硬截断**纪律）；顺序定为 **P-9.7 → P-9.5 → P-9.8（长杆先跑）→ P-6②**。同步更新 P-9 分节索引（+P-9.7/P-9.8）+ 优先级覆盖行。

- **2026-10-04（深夜 · vision 双批准）** —— ① **臂⑥ AIMv2 翻盘**（用户先前批准，20:01 训完 / 20:25 eval 完）：IN-1k lp **11.39 / 11.14 / 12.08%** vs 基线 3.43/5.45/6.08% → Δ **+7.96 / +5.69 / +6.00 pp**，两点均 ≥ +1.5 → **`§14.3` 预注册裁定「翻盘」→ R9 的 25.1% 渐近被局部推翻**；机制 = 坍缩归因 **caption 依赖**（arm④ CoCa 0.47% vs ⑥-A 12.08%），非稠密监督本身。② 用户选定「**凌晨 6h 窗口**」方案 → 下发 **`BAIZE_VISION_TASK.md`「运维指令 · 2026-10-04（七）」**：**R11-G = AIMv2 长跑（108k 步，对齐 R9 阶段二）→ 重拟合 scaling 并外推**（≈3.5h）+ **R11-H = 臂⑥-B 纯 AR（去对比项）**（≈1.4h）→ 合计 ≈4–5h，**由 auto-launcher 串在 R11-F 之后自动接力**（R11-F 5 臂预计 ~02:30–03:00 结束）。两臂均含预注册判据 + 公平表 + C2 限定要求。同步更新 §0 速览 + §3 队列（+第 10/11 行）。

- **2026-10-04（晚 · vision 数据源横比）** —— 用户指令「把几个数据源**横着比**一下，**GPIC 至少 short 和 medium（合计 90%）**，跟 **en500k、CC12M** 一起比」→ 下发 **`run/BAIZE_VISION_TASK.md`「运维指令 · 2026-10-04（六）」= R11-F**：5 臂（GPIC `short` / `medium` / **`short+medium`(≈90%)** / en500k / CC12M）× **固定 30k 步** × w512/InfoNCE/**IN-1k lp**；**预注册判据** Q1（medium vs short）/ Q2（数据源）/ Q3（90% 合并），**en500k 单列**（in-domain + ~30 epochs）；成本 ≈8–10h（5 臂串行）；需最小代码改动（`vision/data.py` 加 `caption_type`、`r9_train.py` 加 `--caption-type`、新 `r11_run_datasource.sh`）。**依据**：R4 实测 GPIC `short`=20 tok/0%、**`medium`=46 tok/仅 0.1% 截断**、`long`=157 tok/100% 截断；原 R7 只比过 3 个**数据源**（R@1/3000 步），**caption 粒度轴从未做**。已同步更新 §0 速览 + §3 队列（新增第 9 行）。

- **2026-10-04（🔴 重大事故 + 定位 + 修复，耗时 ~1.5h 的 18 轮 ops 探查）** —— **`.29` 的 pretrain + harness 静默停摆 ≈9 小时（10-03 22:10 → 10-04 08:01）**：
  - **现象**：两线文件零变更；`/tmp/baize_*_loop.log` 每周期只有 **`error: Forbidden` + `cline returned (exit 0)`**（pretrain 18 / harness 37 次）→ loop 当成功 → **完全静默**；同期 `.12` 的 vision/data 整夜正常。
  - **顺手捞回来的事实**：**P-5b 其实 01:37 就跑完了**（final ckpt `iter_0004771`），因 loop 静默而**未被记录**，随后 **P-9.1 已在 GPU 上跑起来**（8 卡 80%+）。复工后 pretrain 首条提交 = **`beea3f1` P-5b 完成(20B final loss 1.9141) + P-9.1 MBS 吞吐扫描启动**。
  - **定位过程（ops relay RUN_ID 9→27，全部留痕在 `run/ops/outbox.md`）**：逐条否证 token 额度 · proxy 单独 · `OPENAI_*`/`API_TYPE` 单独 · 模型名 · `globalState.json` · **cline CLI 版本（两台都是 3.0.51）** · `.env` 里的 key（curl 全 403）；最后用 **四路 env 矩阵**收敛到 **V3**。
  - **真凶**：**`.29` 的 cline 必须显式 `-k <有效key>`**（V0/V1/V2 全 Forbidden，唯 V3 = V2 + `-k` 通过）；叠加故障 = loop 继承的 `OPENAI_API_KEY=01_549…`（**已吊销**）会覆盖 secrets.json 的有效 key。⚠️ 机制未完全解释（`.12` 不带 `-k` 也能跑），故以**可复现的 V3** 定稿。
  - **修复（RUN_ID 15/27，用户批准）**：把 `.12` 的有效 key 写入 `.29` secrets（凭据经管道、不回显）→ 两条 loop 改为 **`env -u <所有*_proxy> -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE cline … -k "$CLINE_KEY"`**（`CLINE_KEY` 启动时从 secrets.json 现读）→ 重启 → **前置 V3 复核 + `error:.*Forbidden == 0` 校验通过** ✅ 两线复工、均在正常推理。
  - **我自己犯的错（已写入 §7 引以为戒）**：① 用 `python3 -c` 在 loop 里取 key → relay 非交互 shell 无 python3 → 静默退回 stale key；② env 矩阵**漏剥 proxy** → 三组全红、误判"key 失效"，白绕 3 轮；③ 一度把"修 driver"的改动引入，反而改坏了能跑的版本。
  - 详见 `daily-memories/2026-10-04.md`；**坑已入 §7**。
- **2026-10-03（共 3 条）** —— 已原文滚动归档 → `daily-memories/2026-10-03.md`「从 MEMORY.md 滚动归档」**B 节**：① **三项拍板**（论文冻结 / vision 队列裁定 = R11-L2 批准 / data 白名单锁定 + docker 降末选）② **建记忆机制**（迁到项目根 + 滚动规程）③ **论文陈旧性审计 + §6 整节重写**（渐近 25.1% 诚实负结果；`afa2624`）。
