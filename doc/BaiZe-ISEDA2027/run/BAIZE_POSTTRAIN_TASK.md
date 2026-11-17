# BAIZE_POSTTRAIN_TASK.md

### 🔴 用户令 · 2026-11-16 22:0x（自建沙盒池/MCP，别再跟 zhulong 互相等）· ✅ 已闭合（wake628 全流程闭环）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：STEP1 verdict=共用 8090 池+-p2（`SandboxEndpointPool` 独占租借+asyncio.Queue 池满排队，`cap`=池总并发=4，不起新 MCP，同 workdir `t0002997_1..4`⇒与 run1-4 同口径可并入 5run mean）；run5 Pass@1=4.43%(7/158,exec44 行 VALID)+冒烟 PASS+`env_fingerprint.json` 在位(pool_mode=shared_8090_exclusive_queue/shared_with_zhulong=true/new_mcp=false)；5-run 收口 n=5 mean=6.84%±6.12% [18.99,4.43,2.53,3.80,4.43]% rca_status=CLEAN，McNemar chi2=13.5 p<0.001 vs 旧.17 3.04%±0.74%；报告§10/§8 5-run 同表+口径 caveat。需要时再读。


### 📦 用户令 · 2026-11-16 20:5x（取消全局排队·8650–8670 端口池并行）· ✅ 已闭合（被 22:0x STEP1 取代）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：客户端不可重路由 code-gen（cline_mcp_settings.json 硬编码 8090、main.py 启动建池），8656–8670 均他人 daemon（t0002441_*）无可用 4 口独立池；改由 22:0x「共用 8090 池 + -p2」路径取代。需要时再读。

### 📦 用户令 · 2026-11-16 18:3x（恢复「干净 5-run」· 已授权）· ✅ 已闭合（wake628）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：run5 完成 Pass@1=4.43%(7/158, exec44 行 VALID)；5-run 收口 n=5 mean=6.84%±6.12% [18.99,4.43,2.53,3.80,4.43]% rca_status=CLEAN，McNemar chi2=13.5 p<0.001 vs 旧.17 3.04%±0.74%；报告 §10/§8 已改 5-run 同表+口径 caveat。需要时再读。

### 📦 用户令 · 2026-11-15 23:0x（停止盲跑·先查 trace/管线）· ✅ 已闭合（RCA 交付）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：run2/3/4「各仅 1 条 execution_result=0.0%」主因=管线 ws/no-ws 路径失配（抽取器 format_cline_cli_output.py:163 ws-only 无回退），非模型 collapse；rca_recover_extract.py 回补后干净 Pass@1 run2/3/4=4.43/2.53/3.80% exec43/28/35≫1，已接入链脚本自愈。报告 reports/report_posttrain_collapse_rca_zh.html。需要时再读。

### 📦 用户令 · 2026-11-15 08:1x（158 评测改用 zhulong 方式·36.15 eda_fastmcp）· ✅ 已闭合（wake628 全流程闭环）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：36.15 zhulong 口径重测完成（PreToolUse 白名单 run_commands 禁用 + RAG + 沙盒 MCP）；cline 版本补齐(zhulong fork 3.0.29 / cline 3.0.51)；真 MCP 拒绝率(排除 run_commands)=6.3%；5-run mean=6.84%±6.12% rca_status=CLEAN；旧 .17 报告已加 PENDING-REMOTEST banner。需要时再读。

> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不猜不编、infra≠能力、失败分类由你自己提炼）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定 SFT/RL 技术路线、超参与实验设计；结果说话。**

### 📦 用户令 · 2026-11-14 23:4x（隧道怎么坏的·自己查清出报告）· ✅ 已闭合（wake507）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：隧道坏过现已恢复（最后通 20:41:50 / 首断 22:4x / 恢复 23:26 / 故障域=中继侧 / 非本线造成亦非本线修复）。报告 reports/report_infra_tunnel_postmortem_zh.html。需要时再读。

### 📦 用户令 · 2026-11-14 21:5x（今晚自己出计划并直接执行）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：POSTTRAIN_PLAN_NEXT.md 已填并执行；归因夜报 + A1/A3 两臂 40 题 + T6 归因表 + 补丁 dev 前后对比交付。需要时再读。

## 🎯 本线使命（常驻 · 2026-11-14 用户订正 · **每轮开始先读这一块**）

**一句话**：把 2B 基模在 EDA 脚本任务上的通过率，用 SFT/RL 做**显著提升**。

**唯一主线（四步）**：
1. **基模 = `minicpm5-2b`**（MiniCPM5-2B；2026-11-12 用户令已解除对 BaiZe 预训练模型的依赖）。
2. **测基线**：`EDA-Eval-PyAether` **158 题**（写 PyAether 脚本的能力），5-run Pass@1。
3. **领域适配**：**SFT**（agentic 轨迹）→ **RL**（可验证奖励 GRPO），一步一拍，每步单独测。
4. **交付判据**：**同测法下**，post-SFT / post-RL 的通过率相对基线**显著提升**（预注册判据 + 配对检验），并出中文 HTML 报告。

**不是主业（做了也不算产出）**：造题 / 写 `check.py`（designflow 的活）· 评测框架开发 · 环境排障 · 监控心跳 · 报告美化。这些是**必要手段**，只有当它直接服务于「拿到可信的提升数字」时才值得花轮次。

**每轮自检三问**：
① 本轮是否让「基线 → SFT → RL」这条链更清楚、或更接近交付？
② 我报的数字是否**同测法、可复现、有配对检验**？跨测法的差值一律标「不可比」。
③ 若本轮只做了监控/报告，那「未完成指令」是什么、ETA 多少？

---

> 🔴 **用户直令 · 2026-11-14 19:2x — 「3.04% → 15.82%」≈5× 跳升归因 + prompt 迭代（最高优先，压过例行巡检）**
>
> **用户原话**：「请 posttrain 分析一下这 ≈5 倍跳升从何而来……如果系统 PROMPT 差异这么大，那么看看 trace，是否还能继续优化系统 PROMPT 来提分？」
>
> **完整规格 → `run/POSTTRAIN_ENV_ATTRIBUTION_SPEC.md`（含 4 变量前提纠正 / A0–A3 单变量消融 / P1–P3 最小补丁 / train-dev 79:79 / 预注册判据），本令只强调三件事**：
> 1. 目的 = **钉死评测口径**，让「基线 → SFT → RL」三段可比；跨测法的差值一律标「不可比」。
> 2. **不许**把 5× 归给 prompt —— 同时变了「系统提示 / RAG 后端 / 沙盒可达性 / 网络延迟」四件事。
> 3. 🚫 不改 benchmark / check.py / 题面、不挑题、不引用未跑完的 run；commit 前缀 `posttrain attribution:`。
> 4. ⚠️ 本任务书已超 40KB 硬上限 ⇒ 下轮**先**归档已闭合块；**本使命块与本令不得被归档**。

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）（本线现有：`reports/report_posttrain_research_zh.html`）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 📦 2026-11-14 已闭合两条令（16:3x RCA 重写 / 16:1x 看 trace 判定工具调用）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`
> **结论**：v2 RCA 报告已交付并独立复验 PASS（`reports/report_posttrain_pyaether_rca_v2_zh.html`）；工具调用画像已入报告核心章（MCP 6051 / submit_and_exit 13,699 次 91.77% 报错 / degenerate pass 479-790=60.63% / 仅 9.88% 题进入「检索→执行→修错」）。
> **仍有效**：15:4x「在 36.15 启动评测」与 09:0x「先分析基线」两条仍在办（5-run RUNNING），正文保留。需要时再读

### 📦 用户令 · 2026-11-14 15:4x（PyAether 评测必须在 36.15 启动·非 .17）· ✅ 已闭合（wake628）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：36.15 zhulong 口径重测完成，旧 .17 3.04% 基线口径存疑已用 6.84%±6.12%(n=5) 取代；环境差异已标注（旧=.17 无 RAG/无 MCP vs 新=36.15 有 RAG+MCP+沙盒）；旧 RCA 报告已加 SUPERSEDED/PENDING-REMOTEST 声明。需要时再读。

### 📦 用户令 · 2026-11-14 09:0x（暂停 RL·分析基线 3.04% 与 trace）· ✅ 已闭合（RCA 交付）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：基线 RCA 报告交付（reports/report_posttrain_baseline_pyaether_rca_zh.html + v2），158 题逐题结果核对 3.04% 对账，失败逐类统计+饼图+表格+逐类 fix 方案；后经 15:4x 令在 36.15 重测取代。需要时再读。

### 🔴 用户令 · 2026-11-12（**L4 领域评测改由 post-train 主责**）· 用户直令 · 最高优先 · 未完成

> **用户原话**：「既然后训练说『隧道第 4 次复验 OK』，那么 Pretrain 说的 L4 BLOCKED 就不成立了。这件事 Pretrain 不要管，由 Post-Train 负责。」

**背景**：R331 已实测 `ssh -p 3333 app.e0031982@localhost` → TUNNEL_OK（hfeg0tedaap02 = 10.251.36.15），`run_code` 端到端 PASS（2+2=4，py3.9.0）。即 pretrain 报的「.15/.17 SSH 不通 ⇒ L4 BLOCKED」在你这套隧道方案下**不成立**。

**立即执行**（与现有 post-SFT eval 主线并行，不得因此停 SFT eval）：

1. **L4 定义**：① zhulong 消融评测（EDA-Eval-PyAether 158 题，cline harness，`model` 可配）；② designflow（EDA-Flow-Bench，`cline_eval/`，61 任务）。
2. **先出基线**：选 1 个已导出的 BaiZe ckpt（优先 170k/180k HF 目录），经隧道在 36.15 起 OpenAI-compatible 服务（vLLM/SGLang/llama-server 三选一，按可用性），用两个 bench 的 `--model` 指过去，各跑**最小可跑子集**（zhulong 先 5–10 题、designflow 先 5 个任务）→ 出基线数 + 复现命令。
3. **再扩到全量**：最小子集 PASS 后，zhulong 158 题；designflow 按其 README 全量。记录 Pass@1、耗时、失败分类（infra vs 能力）。
4. **落盘**：`MEMORY_POSTTRAIN.md` 关键事实段写清「隧道→36.15→EDA 环境→bench 启动」的实际命令链；结果进 `EXPERIMENTS_POSTTRAIN.md` 与对应报告；勿把凭证写进仓库/日志。
5. **对 pretrain**：L4 数字由你产出后，pretrain 只读引用；不要再让 pretrain 碰 .15/.17。

**边界**：不改变 Phase1/Phase2/Phase3 主线优先级；L4 是并行交付项，出数即可，不为追分改 benchmark 协议。

---


### 📦 用户令 · 2026-11-12 11:2x（沙盒隧道 SSH 到 36.15）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：dual-nix-tunnel 已通（TUNNEL_OK 实测、run_code e2e PASS 2+2=4），连通配置已落 eda_fastmcp .env + MEMORY 关键事实段。需要时再读。

### 📦 用户令 · 2026-11-10 17:10（serve 占住 GPU5-7 防挖用）· ✅ 已闭合（前提已消失：沙盒已通）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：占位目的达成后 GPU5 转交 vision R9、GPU6/7 转为 step105/R2 eval serve。需要时再读。

### 📦 用户令 · 2026-11-10 13:40（GPU 4-7 到位·三阶段替身计划启动）· ✅ 已闭合（三阶段均交付）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：Phase1 基线评测完成（MiniCPM5-2B 36% / step105 3.04%±0.83% locked）；Phase2 替身 SFT 完成（v39 step105）；Phase3 替身 RL/GRPO 完成（R0 200步诚实负结果 + R2 200步 4-run mean≈0.475% decisively 负）。报告 report_posttrain_{baseline_3model,sft_surrogate,rl_surrogate}_zh.html。需要时再读。

### 📦 §用户令·2026-11-07 10:10（GPU 11/9 到位是既定安排，不要再问；等待期继续深入调研）· ✅ 已闭合 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：R1-R143 调研全完成（EDA交互RL方案/造题/奖励设计/失败模式/GRPO超参/rollout调度/verl hooks），GPU 11/9 已到位并启动 Phase 1。

> **用户原话**：「posttrain：不是说了11/9吗，还问啥。继续调研啊。」

#### 0. 口径澄清（一次性钉死，之后不得再问）

- `.17` 的 4 张 A40 于 **2026-11-09** 到位，这是**既定安排**，不需要用户再确认、不需要运维协调。
- 后续任何唤醒：🚫 **不得**再把「什么时候给 GPU」「是否现在腾卡」「要不要等 11/9」写成阻塞项或待用户决策。
- 正确做法：按 11/9 倒排准备，**到位当天自动起跑**（不等到下次唤醒再问）。

#### 1. 11-07 -> 11-09 的主任务 = 深入调研（不是例行巡检）

每轮唤醒必须至少产出**一项实质内容**并落盘，从下列任选（鼓励都做）：（🚨 注意：**不是每轮一份 HTML 报告**；HTML 按顶部「报告生成纪律」执行，日常产出写 EXPERIMENTS/MEMORY 即可）

| 编号 | 调研方向 | 必须回答的问题 |
|:--|:--|:--|
| R1 | **EDA 环境交互式 RL 的可执行方案** | 环境接口（SSH/双向隧道/本地 clone）如何稳定调用？奖励如何自动可判定？单题 rollout 预算？超时与部分失败的恢复策略？ |
| R2 | **PyAether 造题与难度分层** | 把 500 题模板扩展到可自动判定正确性的规模（目标 2k-5k）；难度标定方法（pass@8 profiling 还是规则分层）；每档题的区分度证据 |
| R3 | **奖励设计与 GRPO 稳定性** | 连续化/分档混合、省 GPU 的 group 配置、长度与格式作弊的抑制、KL 与 clip 的取值依据；失败模式（对照 vision 线离散奖励教训） |
| R4 | **35% 侧失败模式分类** | 从 MiniCPM5-2B 36% 基线出发，按 API 类别/错误类型（语法错、API 误用、逻辑错、超时、缺依赖）建分类法；等 GPU 后用真实轨迹校正 |

#### 2. 反空转条款

- 🚫 禁止「只写心跳 + 置 `WAITING: 1`」式空转。
- **连续两轮无新增调研产出 = 未完成任务**，必须 `WAITING: 0` 继续做。
- 每轮心跳必须写清：`本轮新增调研产出：<文件/章节/结论>`；没有就说明为什么。

#### 3. 交付物

1. 调研结论写入 `EXPERIMENTS_POSTTRAIN.md` 新节（或扩写既有节），带检索词与来源链接；
2. 需要时产出中文 HTML 报告到 `doc/BaiZe-ISEDA2027/reports/`（单文件自包含）；
3. 可执行脚本/配置/数据落 `run/`，须 `bash -n` / `--help` 可跑通；
4. commit 前缀 `posttrain research:` 或 `posttrain prep:`。

#### 4. 11/9 GPU 到位后的第一件事（预先写死）

1. `vllm serve /tmp/models/MiniCPM5-2B`（venv 已就绪）-> 复测 36% 基线（同口径 5-run）；
2. 采集真实失败轨迹，**用实测替换 R4 调研中的假设**；
3. 按 R1/R2/R3 结论起第一轮 EDA 交互式 RL（替身预演），报告显著标注「收益不可迁移到白泽」。

---


### 📦 §用户令·2026-11-07（替身模型 × EDA 交互式 RL 预演）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`；**结论**：L1.0 eda_fastmcp 本地克隆✅ + L1.1 API 分级(3276纯函数/1652副作用/3535不适用)✅ + L2 500题✅(0污染命中) + synth_rl_plan HTML✅ + Tunnel-SOP✅ + SFT-Verify✅(99.76G=75.87+23.89分词产物,.29/.12 NFS可达)。需要时再读。

---

### 📦 §用户令·2026-11-06 22:5x（后训练各阶段数据调研 + 本机硬盘体检）· ✅ 已交付 → 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`

> 交付：`reports/report_posttrain_stage_data_survey_zh.html`（45.4KB / 10 节 / 0 script / 0 外链）+ `EXPERIMENTS_POSTTRAIN.md` §E + 硬盘体检附节。**关键结论**：`/` 386G 可用(84%)、`/nas_data` 20T 可用(85%)，后训练全流程预估 200–300GB ⇒ **存储非瓶颈**；可清理候选 ≈4.7G（Qwen3.5-2B 4.3G 用途待确认）；`/nas_inference` 与 `/nas_env` 在 .17 **未挂载**。需要细节再读 archive。

### 📦 2026-11-06 运维直令（建立 post-train 线 · P0 诊断 + P1 数据盘点 + P2 方案书 + P3 脚本骨架）· ✅ 已闭合（P0/P1/P2/P3预备 全部 ✅；P3 正式训练 ⏻ 等 pretrain ckpt，已在「阻塞项」单列）→ 原文见 `ARCHIVE_OPERATOR_POSTTRAIN.md`。需要时再读。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理，沿用）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的「等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X」只在该块任务内有效；与最新用户令或最新任务块冲突时，以最新块为准。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`。

### 💡 最佳实践 / 硬口径（常驻 · 每次唤醒先看）

> ⚠️ **红线（违反则整节作废，见总纲 §5）**：
> 1. **污染隔离**：EDA-Eval-PyAether 的 158 个任务（prompt + 函数签名 + 断言代码）**绝对不能进任何训练集**。允许用 API 参考文档合成训练对，但必须按 API 名/函数签名隔离，论文写明隔离规则。
> 2. **反作弊**：`PreToolUse` hook 全程启用，所有实验臂逐字一致；BaiZe 的 RL 也挂同一套 anti-cheat；必须报告 cheat rate。
> 3. **口径一致**：5-run mean ± std，不得报单次值；158 任务固定集上两系统比较优先用配对检验（McNemar / paired bootstrap）。
> 4. **评测协议冻结项不得改动**（总纲 §2）：158 任务 / Pass@1 / 2500s 超时 / 单 trace 原则 / 5 次独立运行 / `-p 8 -n`。

> 📋 **评测关键资产**（总纲 §3）：
> - 代码生成 driver：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh`
> - 评分：`/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_eval.py`
> - 158-case 数据集：`eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl`
> - `BASE_DIR`：`/nasdata/app.e0031982/code/eda_fastmcp`
> - BaiZe 接入：通过 vLLM/SGLang 暴露 OpenAI-compatible endpoint，`cline auth -p openai -k <KEY> -b <BASE_URL> -m <MODEL_ID>`，换 backbone 成本≈0。

> 🎯 **成功阶梯（预注册 · 先定后测 · 总纲 §4 步骤 4）**：
> | 里程碑 | Pass@1 | 含义 | 先验判断 |
> |:--|:--|:--|:--|
> | 起点 | 36% | MiniCPM5-2B，通用模型，零适配 | ✅ 已实测 |
> | M1 | 50% | 工具协议修好（D1/D2/D6 改善） | 几近必然 |
> | M2 | 65% | + 领域继续预训练 + SFT | 大概率 |
> | M3 | 75% | + RL | 有望，已是强结果 |
> | M4 | 85%+ | 逼近 DeepSeek-V4-Pro | 惊喜级别 |
> 阶梯意义：无论落在哪一档，结论都能成立且都值得发表（落在 M1/M2 则支持「规模非瓶颈」论，与 ZhuLong 互证）。

### 🧭 运维规程 · 2026-10-06（agent 归档 MEMORY + 任务书，常驻）

> 用户裁定：MEMORY + 任务书两样都由 agent 自己滚。
> 判据：两者均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交。
> 做法 = 只「搬迁」、不改内容：① 已闭合运维块原文搬入 `run/ARCHIVE_OPERATOR_POSTTRAIN.md`（无则新建）；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块；冲突保留双方；提交用 `posttrain 归档:` 前缀。

## ⚠️ git 同步规则（必读，每次唤醒都要走）

## ══════════════ Stage (ii) 任务定义 ══════════════

你是推进 BaiZe Stage(ii) LLM Post-Training（领域退火 → SFT → RLVR-GRPO → EDA-Eval-PyAether 评测）的自动化 agent（Cline），被唤醒时按 `MEMORY_POSTTRAIN.md` 恢复状态、只推进一步、更新记忆后立刻退出。不 sleep/等待；执行 shell 直接调工具。

### 阶段总览（与论文 `5_llm_posttrain.tex` 对齐）

| 步骤 | 名称 | 论文节 | 依赖 | 状态 |
|:--|:--|:--|:--|:--|
| 0 | 领域退火（Domain Annealing） | §5.1 | pretrain ckpt | ⬜ 等 pretrain |
| 1 | SFT | §5.2 | 退火 ckpt 或 pretrain ckpt + SFT 数据 | ⬜ 等 P0/P1/P2 |
| 2 | RLVR + GRPO（4 臂奖励 R1–R4） | §5.3 | SFT ckpt + 沙盒 | ⬜ 等 SFT |
| 3 | EDA-Eval-PyAether 评测（backbone × harness 网格） | §5.5 | 各阶段 ckpt | ⬜ 等 ckpt |
| — | Anima 协议 + 本地自纠错（部署） | §5.4 | RL ckpt | ⬜ 部署阶段 |

### 当前可做（不依赖 pretrain ckpt，零/低 GPU）

- **P0**：§7.0 诊断清单 D1–D6（从已有 36% 运行的 `final_report.json` 提取，零 GPU）。
- **P1**：数据盘点 + PyAether 语料调研 + 污染隔离规则草案（零/低 GPU）。
- **P2**：三步训练方案书（纯设计，零 GPU）。
- **P3 预备**：训练/评测脚本骨架（零 GPU，只写不跑）。

### 阻塞项（等依赖就绪）

- **正式训练（退火/SFT/RL/评测）** 阻塞于 pretrain S1 收敛 ckpt（ETA≈2026-12-25）。
- **GPU**：post-train 线在 `10.252.32.17`；正式训练的 GPU 待 pretrain 完成或运维协调分卡（见 `GPU29_ALLOC.md`）。P0/P1/P2/P3预备 纯 CPU/IO 在 `.17` 本机跑。

### 红线（违反则整节作废）

1. **污染隔离**（总纲 §5.1）：158 任务的 prompt + 函数签名 + 断言代码绝对不能进任何训练集。
2. **反作弊**（总纲 §5.2）：`PreToolUse` hook 全程启用；RL 挂同一套 anti-cheat；报告 cheat rate。
3. **口径一致**（总纲 §5.3）：5-run mean ± std；配对检验；引用 ZhuLong 数字前确认口径。
4. **评测协议冻结**（总纲 §2）：158 任务 / Pass@1 / 2500s / 单 trace / 5-run / `-p 8 -n` 不得改动。
5. **预注册**：成功阶梯 M1–M4 + 判定阈值先定后测，避免事后合理化。

### 与他线边界

- **pretrain 线**：提供 base ckpt；post-train 从其收敛 ckpt resume。不 kill pretrain 训练。
- **data 线**：提供 SFT/退火语料的分词镜像；PyAether 语料若需新分词，提需求给 data 线或自行分词（避免重 I/O 撞训练）。
- **harness 线**：提供评测 driver / 评分脚本 / 158-case 数据集的接入方式；post-train 评测复用同一套，只换 backbone。
- **vision 线**：独立，post-train（纯文本）不与 vision 交叉；Stage(iv) MLLM 对齐是另一阶段。

---

> ⚠️ 本文件为只读指令文件，agent 禁止修改本文件。所有运行时状态写入 `MEMORY_POSTTRAIN.md`、`EXPERIMENTS_POSTTRAIN.md` 和 `daily-memories-posttrain/`。
