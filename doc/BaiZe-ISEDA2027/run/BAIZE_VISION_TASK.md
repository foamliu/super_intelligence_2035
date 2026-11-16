# BAIZE_VISION_TASK.md

> 🔴 **用户令 · 2026-11-16 21:2x（vision 自行到 36.15 挖 waveview case · 不再等 designflow task2）· 未完成**
>
> **用户原话**：「vision：可以自己去 36.15 找 designflow 的 jsonl 文件，自己筛选 waveview 的 case 吗」→ **答案：可以，本令授权你自行挖掘并跑，不必等 designflow 交付 task2。**
>
> **背景（运维已核）**：designflow 的 task2（VQA 对照）长期 infra-block；waveview 题池 `A.jsonl / B.jsonl / C.jsonl / D.jsonl` **只在 36.15**（本仓只有导出的 10 题 `doc/ZhuLong_DAC2027/benchmark/designflow/waveview_real_cases.jsonl`）；vision 在 `.17` 已有 `ssh -p 3333 app.e0031982@localhost` 通道（与 posttrain 同一条，`~/.ssh` 已免密）。
>
> **执行步骤**
> 1. **通道自检**：`ssh -p 3333 -o BatchMode=yes -o ConnectTimeout=15 app.e0031982@localhost 'hostname; date'`。不通 ⇒ 报运维，🚫 自建新隧道/改防火墙。
> 2. **只读定位题池**：`find /nasdata/app.e0031982/code -maxdepth 7 -name 'A.jsonl' -o -name 'B.jsonl' -o -name 'C.jsonl' -o -name 'D.jsonl' 2>/dev/null`；同时定位 designflow 评测根（含 `cline_eval/` 与 `reference/`）。**把绝对路径 + 每个 jsonl 行数写进报告**（路径不许估）。
> 3. **筛选（字段级 + 语义级双判）**：`domain=waveform`，或 case 名 / skill 标签 / prompt 正文含 `wave|fsdb|vcd|wlf|waveform|waveview|波形|eye|transient|sweep|duty|jitter`；且必须**可判分**（`check.py` 文件存在、`k_conditions` 可数）。逐条记录：`source_pool`、`pool_line`、`case_id`、`check_path`、`sha256(check.py)`、`image_paths`、`asset_fidelity`。
> 4. **两级分类（关键，决定能不能立刻跑）**：
>    - **V-A 型 = answer-validation（check.py 只校验答案文件/图读数，不需要 EDA 沙盒执行）** ⇒ **立刻纳入 V0（无 VQA）/ V1（+VQA）跑**，这批才是能扩样的；
>    - **V-B 型 = 需 `wv`/FineSim/沙盒执行（L2 工具型）** ⇒ 只出**清单 + 依赖项 + 预计耗时**，等沙盒窗口（当前 8090 池被 zhulong 占用）再跑，🚫 硬跑。
> 5. **三方对账**：`vision/real_waveview_index.json`（10 题）× designflow `waveview_real_cases.jsonl`（10 题）× 本次挖掘结果 ⇒ **新增 / 重合 / 缺失** 表。重合判定用 `case_id` + `sha256(check.py)`，别用名字模糊匹配。
> 6. **防伪底线（不变）**：🚫 不读 `hidden/` 的 B 图或隐藏答案来构造 prompt；🚫 不为凑数放宽 `check.py`（k 数原样，导出一律 `modified=false`）；🚫 **不改 designflow 任何文件**（全只读）；`image_paths=[]` 的 case 照样登记但标 `image_missing`，**不计入可跑集**；`asset_fidelity` 必须区分 `real-private / synthesized-image-restored / synthesized-reframe`。
> 7. **交付**
>    - `vision/waveview_cases_mined.jsonl`（一行一题，字段沿用 designflow 口径 + `vision_run_type`(A/B) + `source_pool` + `pool_line`）；
>    - `reports/report_vision_waveview_mining_zh.html`（中文 / 单文件 / 0 外链 / 0 script）：首屏三行结论（挖掘 N 题 / V-A 可跑 M 题 / 三方新增 K 题）+ 筛选漏斗表（总池 → waveview → 可判分 → A/B 型）+ 三方对账 + V-A 清单 + V-B 依赖清单；
>    - `MEMORY_VISION.md` 一行 + daily + commit 前缀 `vision mining:`。
> 8. **若 V-A 型新增 ≥3 题**：本轮就按既有自测规格跑 V0/V1 并出**逐题翻转表**；n 不足要写清统计力（McNemar 需 ≥6 不一致对），别硬报 p 值。


> 🧹 **2026-11-15 用户令 · 本任务书已做「去禁令化」清理**：删除限制探索与创造力的禁令，保留全部**防伪底线**（不编造数字/文献、负结果照写）。判断标准只有一条：**这条约束是为了「防止说谎」还是「防止尝试」？** 前者保留，后者删除。**默认立场：你有权自主决定技术路线、实验设计与工具选择；用证据说话，用结果说服。**

### 🧭 工作约定（常驻 · 中性表述，替代旧「收尾铁律／体积规程／归档纪律／报告纪律」四段）

1. **每轮收尾**：体积自检 → `MEMORY` 写一行心跳 → 当日日报一行 →
   `git add <本线文件>`（**不用 `-A`**，共享副本上别把别线在途改动卷进提交）→ `commit + push` →
   `git status -sb` 应干净、`git log -1` 时间戳 = 本轮。
2. **体积**：本任务书与 `MEMORY` 各自 **≤32KB**（40KB 为硬上限）；超了就把**已闭合**的段落原文搬进本线
   `ARCHIVE_*.md`、留 1 行指针。**尚未交付的运维令留在正文**，搬完当轮继续把它做完。
3. **报告**：默认不新开文件——维护本线既定的固定报告（原地覆盖）；
   只有**用户点名**或**里程碑**才新增，文件名写里程碑；产物一律落 `reports/`。
4. **边界**：只写本线文件与目录；跨线需要改动时先在自己的 MEMORY 里记一行，再交给对应线。
5. **数字与证据**：结论要能追到落盘文件（路径/行号/命令输出）；取不到就标 `TODO/BLOCKED`，不要估。

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「本线建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### 📦 §用户令·2026-11-07 10:10（阶段2 放行·CPU 放开试各种 idea）✅ 已交付（wake#893：6 项授权变更 v2–v5 全试，v5 获统计显著正结果 A16%→B37%→C53% p=0.0009）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。

### 📦 §用户令·2026-11-07 09:2x（走出「干等 GPU」·用 .12/.29 CPU 设计有效 RL 证明 Qwen3.5-2B 波形理解显著提升）✅ 已交付（wake#893：数据集调研+技术栈冒烟+RL 方案+CPU 实验(含对照与显著性)+中文 HTML 报告 全部交付）→ 原文见 `run/ARCHIVE_OPERATOR_VISION.md`（2026-11-14 wake#1212 归档）。需要时再读。


> 📦 已归档（2026-10-30~31，ViT-L 68.236% / MLLM 26.10% 写进论文 ch6/ch7、6_vision_encoder.tex 重写、第6章审校修订、波形图强化 RL 计划书、2B MLLM 看懂波形图能力报告）→ run/ARCHIVE_OPERATOR_VISION.md（wake#424/#435/#436/#437/#439）。需要时再读。

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 用户裁令 · 2026-11-15 07:2x（**解掉两条「真阻塞」：① 走 SSH 自建 VQA 通道 ② 自行 SSH 去 36.15 取 WaveView 真题**）· 最高优先 · 未完成

> **用户原话**：「vision：目前隧道只保证 10.251.36.15 <-> .17 SSH 畅通，30002 不能保证，需要基于SSH，自己（vision在.17）想办法。关于【缺 >10 道 WaveView 真题】，放行vision自行SSH到36.15，检查designflow放置case的目录，自行检出。」

**一、口径变更（先读，别再用旧结论）**

| 旧状态（wake#1275–#1283 心跳里写的） | **新口径** |
|:--|:--|
| 阻塞② task2「评测机 → .17:30002 TCP 超时，待 ops/网管放行」 | **不成立了**。运维**不会再放行 30002**；**隧道只保证 `10.251.36.15 ↔ .17` 的 SSH**（`.17:3333`）。⇒ 由**你自己**基于 SSH 建通道 |
| 阻塞① 「缺 >10 道 WaveView 真题，待 designflow 供给」 | **已解阻**。用户**放行你自行 SSH 到 36.15**，去 designflow 放 case 的目录**自行检出** |
| 等 ops / 等 designflow | 🚫 **不许再写「待 ops 放行」「待 designflow 供给」** —— 这两条现在都是**你自己的工作项** |

**二、任务 ①：基于 SSH 自建「评测机（36.15）→ VQA 后端（.17:30001/30002/30003）」通道**

- 事实：评测跑在 **36.15**（评测/沙盒容器在 36.15 侧），VQA 服务在 **.17**（`:30001` 基模 / `:30002` MCP / `:30003` +rft2_adapter）。36.15→.17 的 TCP 打不通，但 **36.15 能 SSH 到 .17**（隧道保障）。
- **做法（任选一，择优并写清理由）**：
  1. **SSH 端口转发**：先 `ssh -v` 核实握手方向（哪端是 sshd），再决定 `-L` 还是 `-R`；例：`.17` 侧 `ssh -N -R 30001:127.0.0.1:30001 -R 30002:127.0.0.1:30002 -R 30003:127.0.0.1:30003 <user>@<36.15>`。`.17` 侧若 `GatewayPorts=no`，就只能监听 `127.0.0.1` ⇒ 让评测容器走 `--network host` 或经宿主机网关 IP 访问。**实测命令 + `ss -ltnp` 输出必须落盘**。
  2. **SSH 隧道 + 本地 socat/nginx 暴露**（容器内可达宿主机时用 `host.docker.internal` 或宿主机网关 IP）。
  3. **HTTP-over-SSH 桥**（最抗断）：转发 `/health`、`/v1/chat/completions`、`/mcp` 三类端点。
- **必须做到**：
  - **连通性预注册验证**：从 **36.15 侧宿主** + **评测容器内部** 各 `curl -sS -m 10 http://<桥地址>/health`（三端口各一次），输出落 `run/vision_ssh_bridge_proof.txt`；**容器视角才是评测视角**。
  - **断线自愈**：`autossh` 或 watchdog（`while true; do ssh -o ServerAliveInterval=15 ...; sleep 30; done`），重连日志落盘；🚫 只建一次性连接不算完。
  - **不可放宽判据**：换的只是传输层，**题目 / designflow check 判分 / 防作弊（禁 PIL·OCR·base64·搜答案）全不变**。
- **交付**：`run/vision_vqa_ssh_bridge.md`（方案选择 + 实测命令 + 三方证据：36.15 宿主 / 容器内 / 断线重连实验）+ 用**桥接后**的通道重跑 task2 对照，证明「VQA tool 在评测环境里真的可用」。

**三、任务 ②：自行 SSH 到 36.15 检出 WaveView 真题（>10 道）**

- **放行范围**：你有权 SSH 到 36.15，读取 designflow 放 case 的目录。已知线索（据此定位，不要凭猜）：
  - 交接区：`doc/ZhuLong_DAC2027/benchmark/designflow/WAVEVIEW_COLLAB.md`（「交付记录」表）
  - 恢复计划：`doc/ZhuLong_DAC2027/benchmark/designflow/waveview_restore_plan_D.md`（α1–α4 / β7–β11 逐题恢复路径 + 图类型）
  - 你侧清单：`run/reports/waveview_need_image_handoff.md`（α4+β7=11；**已订正 β5 不存在、真·可恢复分母=4**）
  - 评测目录：36.15 侧 `.../designflow/cline_eval/EDA-Eval-DesignFlow-<CaseName>/`（每题一目录）；题库 jsonl = **`A.jsonl / B.jsonl / C.jsonl / D.jsonl`**；已有基线 `waveview_baseline_results.{B,D}.json`
  - 📌 designflow 已被同时下达「把 WaveView 真题整理成单独 jsonl」的令 ⇒ 优先认 **`waveview_real_cases.jsonl`**（落地后你直接读它，别自己重新解析 4 个 shard jsonl）
- **步骤**：
  1. 在 36.15 上 `ls` / `grep -l -i wave` 找出**同时**满足：`domain=waveform`、**case 目录内真有图片（PNG/截图）**、有 `check.py`、**已跑过基线**的题；
  2. **逐题登记**：题名 / shard jsonl / 图文件路径 + sha256 / `check.py` 的 k 条件数 / 基线 PASS·FAIL / failure_mode_tier（若有）；
  3. 产出 **`run/vision/real_waveview_index.json`**（机器可读）+ `run/vision_real_waveview_intake.md`（人读）；**只读复制**到你自己的数据目录，🚫 **不许改 designflow 的题目/图片/check**；
  4. 目标 **>10 道真题**；**实测**不足就写「实际可用 = N 道 + 每道为何不可用」，🚫 **不许拿合成集冒充真题**（纪律不变）。
- **交付**：上述 index/md + 用**真题**重跑的对照（无 VQA / 有 VQA / agent 臂，同口径），并**原地覆盖**更新 `reports/report_vision_waveview_selftest_agent_zh.html`。

**四、验收（本轮必须能回答）**
1. 36.15 → .17 三条 VQA 通道，**评测容器内部** `curl /health` 是否 ok？（贴命令 + 输出）
2. 断线 30s 后是否自动重连？（贴日志）
3. 真题实得 **N 道**（N>10，或写清为何不足）；每题 `check.py` 是否原样未改？
4. 真题重跑后，「VQA tool 在评测环境下」翻转题数 + McNemar（n 不足写「仅参考」）。


### 🔴 用户令 · 2026-11-14 17:2x（**为 v2 显著正结果写一份正式成果报告**）· 未完成 · 最高优先

> **用户原话**：「① vision —— 出了显著正结果（这是今天最有价值的成果之一）。安排 vision 写个成果报告（中文 HTML）。」

**一、背景**

你 wake#1229 交付的 **v2（CoT 推理链 SFT+RFT）** 是这条线**自 v5 之后第一个显著正结果**，
且**预注册判据全部满足**（post-RFT_v2 ≥ post-SFT_v1 + 5pp、p<0.05、≥3 seed、cheat=0）。

> **这是今天全项目最有价值的成果之一**，用户要求**单独出一份正式成果报告**，而不是只留在 MEMORY 心跳里。

**二、报告定位（与既有报告区分）**

- 你已有 `reports/report_vision_vqa_strengthen_v2_zh.html`（11KB，过程性/结果记录）。
- **本令要的是「成果报告」**：面向**外部读者**（评审/论文写作/领导汇报），讲清**这件事的价值与可复现路径**，不是再复述一遍数字。
- **新文件**：`reports/report_vision_cot_vqa_result_zh.html`（中文、单文件自包含、0 外链、0 script、图表用内联 SVG）。

**三、报告必含内容**

1. **一句话结论 + 关键数字卡片**
   - 拿到什么：**60.0% → 90.0%**（v2-RFT），McNemar **b=7/c=0, p=0.0156**
   - 判据：预注册 4 项**逐条列出 + 是否满足**

2. **问题从哪来（溯源）**
   - **#3 后半探针**（wake#1227/#1228）发现的缺口：`看懂图是什么` ≠ `读得准图上的数`
   - 给出探针实测：6 题合并 **14/46 = 30.4%** vs 基线 text-only **0/46**
   - **稳定 gap 模式**：正确项集中在分类/轴标签/约束筛选；失败项集中在**精确计数**、**精确数值**、**跨面板反推**

3. **方法：为什么是「推理链」**
   - v1（plain target，wake#1209）为何失败：**p=0.5 未达判据**
   - v2 的单一变量：三个技能（`cycle_count` / `amplitude_read` / `duty_cycle`）的 SFT target 改为「**读数推理链 + Final Answer: X**」
   - 为什么这样能闭合缺口：模型不是不知道看图，而是**没有"从坐标轴读数"的中间过程**
   - **数据集构造的防泄漏设计**（重要）：训练 seed=20261114 / held-out seed=20261115 不同 → **cheat_rate=0 由构造保证**，不是事后过滤

4. **结果（完整、可复现）**
   - 全链路对比表：`before 60.0% → v1-SFT 64.4±1.6 → v1-RFT 73.3% → v2-SFT 74.4±4.2 → v2-RFT 90.0%`
   - **3 seed 明细**（seed11=70 / seed22=80 / seed33=73.3）
   - **技能分解表**：`duty_cycle 0→80%`、`amplitude_read 20→60%`、`cycle_count 66.7→100%`、`type_classification 恢复 100%`、`freq/rise 维持 100%`
   - **翻转 7 题 0 回退**（列出具体题号）
   - 图表：折线（各阶段）+ 技能柱状对比（内联 SVG）

5. **诚实性声明（必写，不许省）**
   - **scope 限定**：结论仅适用**合成波形识图**，**不可外推到 designflow 真实 EDA 波形**（需 #3 跨线对照）
   - **跨面板反推仍待解**（β10 vth_high/low/hysteresis 全 fail）
   - 探针图与 designflow **等价但非字节相同**，不可当作官方通过率
   - RFT 的 accepted 样本量（207/600）与选择偏差说明

6. **可复现性清单**
   - 脚本路径、数据路径、adapter 路径、3 seed、判据公式、复算命令
   - 让第三方能按文档一步步重跑

7. **下一步与可复用价值**
   - 这套「CoT 读数推理链」能否迁移到其他读数类任务
   - 对 #3（与 designflow 官方对照）和 #4 后续强化的意义

**四、写作要求**

- **面向外部读者**：不假设读者读过你的 MEMORY；每个缩写首次出现给全称；
- **数字优先**：能用表格就不用散文；
- **诚实**：负结果与局限照写，🚫 不要为了好看而弱化 scope 限定；
- 🚫 不编造数字，每个数字可追到落盘文件（附路径 + 复算命令）。

---

### 🔴 用户令 · 2026-11-14 10:3x（**与 designflow 的协作通道已建好 —— 你的「跨线无法驱动」已不再是阻塞**）· 未完成

> **用户原话**：「请你帮助 vision 完成跟 designflow 的工作协调（#3 / #4）」

**一、我已替你打通的三件事**

1. **发现并修掉了一个真问题**：designflow 的 4 个 shard loop 读的是**各自专属任务书**
   `BAIZE_DESIGNFLOW_BENCH_TASK_{A,B,C,D}.md`，而此前「不降级」令写进了 4 shard **共用**的那份
   ⇒ **四个 shard 实际都读不到，指令等于没下发**。现已把协作令写入**四份专属任务书顶部**。
2. **建立了交接区**：`doc/ZhuLong_DAC2027/benchmark/designflow/WAVEVIEW_COLLAB.md`
   —— 含「认领记录 / 交付记录」两张表，designflow 任一空闲 shard 认领后会在表里留痕。
3. **你的交底清单已在位**：`run/reports/waveview_need_image_handoff.md`（α4+β7=11 题），
   协作令里已直接引用它作为 designflow 的输入。

**二、你现在做什么（不要再等）**

你的 #3 / #4 拆成「可并行」与「需等待」两部分，**先做可并行的那半**：

- **✅ 立即可做（不依赖 designflow）**：
  1. **把 Qwen3.5-2B 封装成 VQA tool**（#3 的前半）——定义调用接口（输入：波形图 + 问题；输出：答案），
     跑通单题样例，写清调用方式（供 cline 调用）。这是纯本线工作，**没有理由再等**。
  2. **准备 #4 的训练/合成数据管线**（合成波形图-问答对、SFT 数据格式、RL 奖励设计），
     先用合成数据自测能力基线，**不等 designflow 的用例**。
- **⏳ 需等待**：用 designflow 恢复原形态后的用例做「无 VQA vs 有 VQA」对照。

- **解除阻塞**：🚫 不要再写「单 agent 无法跨线驱动 designflow」——通道已建好，
  designflow 会自己认领；你只需**定期查 `WAVEVIEW_COLLAB.md` 的「交付记录」**，有结果就接上 #3 后半。

---

### 🔴 用户令 · 2026-11-14 09:5x（**口径变更：designflow 不再降级多模态题 → 你的 waveview 结论前提已变**）· 未完成

> **用户原话**：「这样不对，告诉 designflow 复查。对这些需要多模态的题不要降级，暂时没有多模态能力，就让它们 fail。这样才好度量多模态带来的增益。」

**要你知道的三件事**

1. **我已向 designflow 下发复查令**：要求它把「被降级成文本/Tcl」的 waveview 题**恢复原本需要看图的形态**；当前无多模态能力的系统**就该在这些题上 fail**，这是正确行为，不是缺陷。
2. **你上一份报告的结论前提已改变**：报告里「已评测 7 题全 PASS 且全 γ、所以无因看不见波形而失败」——那是因为**题被降级了**。降级取消后，这些题会**重新变成会 fail 的题**，你的 α/β/γ 统计基础需要据此更新。
3. **你要做的事**（designflow 复查是并行输入，不构成阻塞；你可以同时按自己的判断推进）：
   - 待 designflow 恢复原形态后，**重新统计** waveview 用例的 α/β/γ 分布与新基线通过率；
   - 把这批题作为 **「多模态增益」的度量基准**：`基线 fail → 上 VQA 后 pass` 的差值才是核心指标；
   - 这正是你手上四件事（NeurIPS §6 / 协调 designflow 评 waveview / Qwen3.5-2B 封 VQA tool / 强化识图能力）的**共同前提**。

- **现在可做**：主动与 designflow 对接，把你筛出的 37 题清单里**哪些是"原意图需看图"的**交底给它（它需要据此判断恢复哪些题）。
- **纪律**：🚫 不要再基于"降级后"的数据下结论；更新后的统计要写明数据时点与 designflow 恢复进度。

---

### 🔴 用户令 · 2026-11-14 09:1x（**四件事：NeurIPS §6 刷新 / 协调 designflow 评 waveview / Qwen3.5-2B 封装 VQA tool 对比 / 强化波形识图能力**）· 未完成 · 最高优先

> **用户原话（逐字，共 4 条）**：
> 1.「刷新 `doc/BaiZe-ISEDA2027/BaiZe-NeurIPS2027`，特别是第六节。期望：有想象力&创造力（提醒：它有 cimi-search 这个网搜工具，善用）。」
> 2.「协调空闲的 designflow shard agent(A/B/C/D) 帮忙评测这些 waveview 相关用例」
> 3.「协调空闲的 designflow shard agent(A/B/C/D)，把 Qwen3.5-2B 封装成 vqa tool 给 cline 后，再次评测，写报告对比二者。」
> 4.「在 #3 基础上强化 VQA 工具读懂波形图的能力，使用合成数据/SFT/RL 各种手段，提升基模（Qwen3.5-2B），争取通过率得到显著提升。」

> ⚠️ **本令优先于 idle-spin 处置**：先做这四件，停不停 loop 另议。
> ⚠️ **#2/#3 需要跨线协调**：designflow 是独立线（`doc/ZhuLong_DAC2027/benchmark/`，4 个 shard 共用同一 git 工作区，有严格同步纪律）。**协调方式由你与 designflow 线对接确定**（写协作请求到其任务书/ops 通道，或自行按 `designflow_bench_loop_shard.sh` 口径起评测），**不要违反其「不 clean/reset/stash 别人改动」铁律**。

---

#### ① NeurIPS2027 论文刷新（尤其第六节）

- **文件**：`doc/BaiZe-ISEDA2027/BaiZe-NeurIPS2027/NeurIPS2027/6_domain_rl.tex`（当前 `\section{Semiconductor Domain Adaptation}`，结果仍是 `\textbf{[TBD]}`）；其余 0–7 各节亦在刷新范围。
- **用户要的是「想象力 + 创造力」**，不是把现有文字润色一遍。
- **善用 cimi-search 网搜工具**（用户点名提醒）：检索 2026 年 NeurIPS/ICML/ICLR 相关工作、最新 benchmark、领域适配/偏好学习/波形多模态的前沿方法与可引用数据，把**外部证据**带进正文（每条引用必须真实可查，🚫 不许编造文献）。
- **第六节必须脱掉 [TBD]**：用你已有的真实结果填（waveview 37 题/30 failed/α 13.3%、v5 typecls C=53%>B=37%>A=16% p=0.0009、v6–v11 负结果、Qwen3.5-2B 现状），**负结果也照实写**。
- 判据：编译 0 error；引用可查；无 `[TBD]` 残留（或明确列出仍缺哪些数据、需要什么补）。

#### ② 协调 designflow 评 waveview 用例

- 你已有 waveview 筛选结果（37 题 / 30 failed），**把这份清单作为评测输入**交接给 designflow shard。
- 目标：由 designflow（有 pi_debug 与真实 EDA 环境）**跑一遍这些用例**，拿到**基准口径下的当前通过率**，作为 #3 的对照底数。
- 交付：评测清单 + 环境/口径说明 + 结果表；交接过程与结果写进 MEMORY。

#### ③ Qwen3.5-2B 封装为 VQA tool 给 cline，二次评测并对比

- 把 **Qwen3.5-2B** 封装成「看图答波形问题」的 **VQA tool**（供 cline 调用；模型已在用，见 `run/launch_qwen35_server.sh` 与 `run/longctx_eval_results/`）。
- 由 designflow shard 用**同一批 waveview 用例**再评一遍（**唯一变量 = 有没有 VQA tool**）。
- 交付：**对比报告（中文 HTML）**——两次评测同表并列，明确「哪些题靠 VQA tool 翻转了」，以及**未翻转的为什么**。
- 纪律：两次评测的题目、环境、判据必须一致，否则不可比。

#### ④ 强化 VQA tool 读波形图的能力（合成数据 / SFT / RL）

- 在 #3 的 VQA tool 基础上提升基模（Qwen3.5-2B）的波形识图能力。
- **手段自选**：合成数据、SFT、RL 皆可（你任务书已指定 LLaMA-Factory + KTransformers + LoRA 栈，CPU 可跑，不必等 GPU）。
- **判据（用户明确要）**：**通过率得到显著提升** —— 必须有**对照**（pre / post 同口径、≥3 run，给 mean±std）与**显著性**；负结果照实记录，🚫 不许挑好看的 run 上报。
- 交付：中文 HTML 报告（做了什么 / 数据怎么造 / 训练配置 / 对照结果 / 哪些题翻转过来了 / 下一步）。

---

**统一纪律**
- 所有数字可复算（路径 + 命令）；取不到的标 `TODO/BLOCKED`，🚫 不许估、不许编。
- 报告一律中文 HTML、单文件自包含、0 外链、0 script。
- #1 完成即可先出；#2→#3→#4 是依赖链，按序推进，每步完成即写 MEMORY 心跳。

---

### 🔴 用户令 · 2026-11-14 08:4x（**分析 designflow 评测中的 waveview 用例：哪些 failed 在「有波形图识图能力」下大概率能过**）· 未完成 · 优先于 idle-spin 告警

> **用户原话**：「vision：看下 designflow 做的评测，先筛出 waveview 相关的用例，然后出一份数据分析报告（中文 HTML）。哪些 waveview 相关的 failed case，在有波形图多模态识图能力的情况下，大概率能过。这个比例有多大，请做出有想象力创造力的分析报告。」

- **📌 本条优先于「idle-spin 第 35 轮」告警**：这是一条**新的实质研究方向**，先做完这份报告再谈是否停 loop。
- **数据源（都在本仓，只读）**：designflow 线（`doc/ZhuLong_DAC2027/benchmark/designflow/`）的评测记录 —— 已确认存在下列 wave 线索，请**自己再全量筛一遍**（别只抄这几个）：
  - 深度阅读记录：`trace_deepreads/` 下 `*wave*` / `*fsdb*` / `*openwave*` / `*tranwave*` 等（如 `3qe6x_wavecmp_wrap.md`、`7fcir_openwave_fmt.md`、`as67p_waveview_ace_fsdb_signal_extractor.md`、`1790241096712_s0t3i_waveview_panel_height.md`、`1788919426197_cjcn7_tranwave-repair.md`）
  - 用例台账：`designflow/A.jsonl` / `B.jsonl` / `C.jsonl` / `D.jsonl`（或对应 ledger `*.tsv`）中 task 名/skill 标签含 wave / fsdb / vcd / waveform / waveview / 波形 的条目
  - 调试现场：`.pi_debug/EDA-Eval-DesignFlow-Wave-00x/`、`EDA-Eval-DesignFlow-Analog-004/_waveview_ref.tcl` 等
- **筛选口径（请明确定义并写进报告）**：什么算「waveview 相关」？建议三维判定并给每题的判定依据：
  ① **任务要求**涉及波形文件操作（VCD/FSDB/WLF 解析、信号提取、测量、对比、修复、绘图面板）；
  ② **判据/checker** 需要看波形数值或形状；
  ③ **失败原因**是否与"看不见波形/只能读文本"相关。
  注意：**Aether/纯脚本类**（只改 tcl/python、不涉及波形可视化）不算。

**必做内容（报告五部分）**

1. **筛选结果表**：waveview 相关用例总数 / 其中 passed / failed（给出题名列表与判定依据）；
2. **失败逐个分类**（关键）：把每个 waveview failed case 归到
   - **α 强相关 · 识图可解**：失败直接因为"模型看不到波形形状"（例如判断毛刺/时序错位/眼图/上升沿、从截图里读数值），**给了图像大概率能过**
   - **β 弱相关 · 识图有帮助**：需要波形信息但也可用脚本读数值替代，识图能降低难度但非决定性
   - **γ 不相关 · 识图无用**：失败原因是脚本语法/环境/API/约束理解，与"看不看得见"无关
   **每类给题数、占比、2–3 个具体例证（含 trace 原文摘引 + 路径）**
3. **核心结论数字**：`waveview failed 共 N 题，其中 α(大概率能过) = n 题，α/N = x%；α+β = y%`。**同时给保守/乐观区间**，并说明区间来源（哪几题判不准、为什么）；
4. **"想象力"部分（用户明确要）**：
   - 反事实推演：如果给模型**波形截图 + 数值双通道**，这几题的解题路径会变成什么样？举 2–3 个 case 画出**前后对比的推演流程**；
   - 反向思考：**哪些看起来能过的其实过不了**（例如识图能看出问题但改不对代码）；
   - 延伸机会：这份分析能否反向指导设计 **"waveform-VQA 专项评测集"**？给出题源与构造思路（这是本报告对后续 vision 实验的价值输出）。
5. **可视化**：桑基/堆叠条 or 饼图（α/β/γ 占比）+ 结论卡片。**必须内联 SVG，单文件自包含，0 外链 0 script。**

**纪律**
- 数字全部可复算（路径 + 命令）；拿不到就标 `TODO/BLOCKED`，🚫 **不许编造 case 或 trace 原文**；
- 报告落 `reports/report_vision_waveview_failed_analysis_zh.html`（中文 / 单文件 / 0 外链 / 0 script / 内联 SVG）；
- MEMORY 心跳一行：`waveview分析: 相关=N题 failed=M · α=a(x%) β=b γ=c · 结论=<识图可解比例> · 报告已出`；
- **本报告只做分析，不起训练/实验**（与 idle-spin 处置解耦，处置另议）。

---

> 📦 §用户令·2026-11-06 21:3x（advantage 方差诊断）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：wake#838 判定 PARTIAL（std=0=78.7%/全0=0%/全同档=无信号根因），建议 group_size→8+按目标差异化+奖励连续化(需批)。需要时再读。

> 📦 §用户令·2026-11-06 18:5x（vision 先上 CPU）**✅ 已交付**（wake#827-#835：P0 冒烟 5 步 365s（73s/步）、P1 50 步 ~2min/步、4 个 eval JSON、报告 15058B、EXPERIMENTS §21；结论 post-GRPO 6.2% < post-SFT 9.2% 未提升）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

### 📦 §运维令·2026-11-05 17:5x（执行波形 RL 计划：Stage-1W SFT → Stage-2W GRPO · 分阶段）· ✅ 阶段0+阶段1 已交付 → 原文见 `ARCHIVE_OPERATOR_VISION.md`

> **用户令**：「vision：执行 2026-10-31 波形 RL 计划书（`reports/report_vision_wave_rl_plan_zh.html`），让 2B MLLM 通过与 WaveView 交互学会看懂波形图。分阶段，先解锁待核项再训练。」
> **交付进展**：阶段0（WaveView/FSDB 解锁 + Gym 冒烟）✅ · 阶段1 SFT 验收 PASS（format 100%/submit 100%）✅ · Phase2 **CPU pilot 全链路 PASS**（诚实负结果 post-GRPO 6.2% < post-SFT 9.2%）✅ · advantage 诊断 gs4/gs8 双轮 ✅（PARTIAL，离散分档是全同档根因）。**阶段2 正式 GRPO 需 GPU —— 已被 2026-11-07 用户令改为「改用 CPU 重新设计」路线，见顶部新令。** 需要细节读 archive / 各阶段报告。
> 📦 已归档（2026-10-17 ~ 10-26）：ArmA/B/C/D 系列指令 + OCR 三条调研/路线令 + Milestone 报告令 + 08:2x ArmD-R2 整块→ `run/ARCHIVE_OPERATOR_VISION.md`（wake#133/#247/#250/#271/#272/#275/#279 交付）。需要时再读。
### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。

### 📦 运维指令 · 2026-10-18 17:1x（ArmC：min_lr 1e-4→1e-5 + wd 0.1→0.01 · 4 阶段）— 已归档

> **已闭合**（ArmC 全链路 DONE 2026-10-19）。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`（2026-10-19 归档）。**结论**：ArmC = 两变量；训练 57250 步 ✓ / ProtB lp 62.332·5-NN 54.718 / MLLM 三阶段 ✓ / 12 集 12/12 DONE avg 25.78%（vs ArmB 26.10%，**不可分辨**）。ArmC 配置已被 ArmD 承接（见顶部 ArmD 块，**wd 0.01 沿用**）。需要时再读。

### 📦 运维指令 · 2026-10-17 12:4x/12:2x/12:0x（kill .12 pretrain→起 ArmB / .12 专属 / 启动 ArmB）— 已归档

> **已闭合**：ArmB 已训完并评测（ProtB 62.093/58.102、MLLM 26.10%），ArmC/ArmD 依次承接。原文移至 `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### [已归档] §运维令·2026-10-17（ArmA 中文报告 + open_clip×AIMv2-style 兼容性评估）**已完成**（wake#133：数字全溯源 EXPERIMENTS §10，不得写「AIMv2好 9pp」）→ 全文见 `run/ARCHIVE_OPERATOR_VISION.md`。

> 📦 2026-10-13 ~ 10-16 历史运维指令指针（~90 条单行摘要）已原文归档 → `run/ARCHIVE_OPERATOR_VISION.md`；需要时再查，不要读进上下文。
### 🏆 最佳实践（BEST PRACTICES）— 2026-10-08 锁定 · 如无特殊指定，一律按此执行

> 以下三项由 R2–R14 全线实验预注册 + 收敛后裁定，证据见对应报告/实验记录。
> 默认执行：除非运维另有指令，所有视觉编码器训练与评测一律遵循以下配置。
> **历史配置参考**（不是禁令）：下表是已实验过的旧配置及其结果，供**知情决策**用。若你想重试，请说明「为什么这次会不同」（新数据/新方法/新预算），并把两者结果并列上报。

#### BP-1 · 目标函数 = AIMv2-style dense objective（`--loss aimv2`）

| 项 | 值 |
|:--|:--|
| 损失 | `1.0 × InfoNCE + 1.0 × masked-patch-MSE`（双向 ViT + 随机掩码） |
| 文本塔 | 冻结 CLIP-ViT-L/14-336（768-d），不解冻 / 不用 LoRA |
| 注意力 | 双向（bidirectional）—— 🚫 禁用 causal AR（④ 已证明坍缩或 lp 极低） |
| 证据 | R11-G：lp 7.40% → 19.76%（+12.36 pp，11 点全单调，R²=0.91，无饱和）；3-epoch 续跑达 20.27% |
| 否决项 | ❌ 纯 InfoNCE（天花板 ~7.4%）· ❌ CoCa（caption-CE 坍缩 trunk）· ❌ 纯 AR（step 600 坍缩 C1=0.97）· ❌ AR+InfoNCE hybrid（lp=1.37%，−12.1 pp）· ❌ SigLIP / LocalLoss（均低于基线）· ❌ 文本塔 LoRA 解冻（−0.30~−0.80 pp） |
| 报告 | `report_vision_aimv2_impl.html` · `EXPERIMENTS_VISION_ROUND11.md §14–§17` |

#### BP-2 · 超参 = mask-ratio 0.6 + contrast:patch weight-ratio 1:1

| 超参 | 最优值 | 消融设计 | 证据 |
|:--|:--|:--|:--|
| `--mask_ratio` | 0.6 | 5 臂（0.3/0.5/0.6/0.75/0.9），倒 U 形，lp@30k=13.49% 为峰 | `EXPERIMENTS_VISION.md` mask-ratio 节 · `report_vision_mask_ratio.html` |
| `--contrast_weight` / `--patch_loss_weight` | 1.0 / 1.0（即 1:1） | 4 臂（1:2 / 1:0.5 / 0.5:1 / 2:1），1:1 最优；patch-heavy 方向更宽容但无翻盘；contrast 过高显著有害（−3.28 pp） | `EXPERIMENTS_VISION.md` weight-ratio 节 |

#### BP-3 · 评测协议 = Protocol B（主流对齐）

| 项 | Protocol A（旧 · 🚫 废弃为默认） | Protocol B（新 · ✅ 默认） |
|:--|:--|:--|
| 优化器 | AdamW lr=3e-3，无 schedule | SGD + momentum 0.9 + cosine（5-ep warmup） |
| Batch size | full-batch（49,970） | mini-batch 1024 |
| Epochs | 100（= 100 次梯度更新） | 90（≈ 112,605 次更新） |
| Probe-train | 50/类 = 49,970 张 | IN-1k full train = 1,281,167 张 |
| Eval 集 | 自切分 val（50/类 = 5,000） | IN-1k 官方 validation（50k） |
| Normalization | CLIP mean/std | ImageNet mean/std |
| 重复 | seed 0 单次 | 3 seeds（0,1,2）→ mean ± σ |
| 证据 | Δlp ≈ +10.05 pp（B−A，3 ckpts: +10.05/+10.05/+10.17，σ_cross-ckpt=0.06 pp）；主因 = 更新次数 100 vs 112,605（1126×）+ probe-train 25.7× 小 → 分类器欠拟合 | `report_vision_lp_protocol.html` · `vision/lp_protocol_bridge.py` |
| 内部横比 | 旧实验（R2–R14）均用 Protocol A，相对排序仍有效（A/B 排序一致）；但绝对数字须标注 "BaiZe internal protocol" | 新实验一律用 Protocol B；与 DINOv2/MAE/iBOT 等公开值可直接横比 |

> ⚠️ Protocol A → B 迁移说明：旧实验的相对结论（架构排名、目标函数翻盘、消融排序）不受协议切换影响—— Protocol A/B 排序一致（20.22>19.77>18.79 vs 30.27>29.94>28.84）。正式训练后的评测一律用 Protocol B；论文中旧数据标 "BaiZe internal protocol"，新数据标 "mainstream protocol"，不混表。

---

> 📦 2026-10-06~08 运维指令（8 条：①论文LaTeX ②全线报告 ③mask-ratio消融 ④GPU12对账 ⑤昨夜汇报 ⑥下一步建议 ⑦AIMv2 AR范式 ⑧队列裁定 ⑨lp协议研究）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`。需要时再读。

### 🧭 运维规程 · 2026-10-06（【agent 归档 MEMORY + 任务书】 —— 由你自己滚，不再由运维代劳）· 常驻

> 用户裁定：「运维归档任务书不是长久之计」。`MEMORY_*.md` 一直是 agent 自滚（不经运维）⇒ 任务书同理。本轮起：MEMORY + 任务书，两样都由你自己滚。
> 判据：两者 均 ≤32KB；>40KB = 红线 ⇒ 必须先归档再提交（「收尾铁律」第 0 步已同步此判据）。
> 做法 = 只「搬迁」、不改内容：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早巡检流水）原文搬入 `run/ARCHIVE_OPERATOR_VISION.md` / `run/ARCHIVE_VISION_SPEC_HISTORY.md`（无则新建）/ `daily-memories-vision/<日期>.md`；② 留 1 行指针；🚫 不改小节编号/标题；🚫 不新增/不改写任何指令（本区作者仍是运维）。
> 护栏：搬前 `git pull --rebase --autostash`；只搬「最新活跃块之下」的已闭合块（保留最上面 1–2 个未完成块）；冲突保留双方；提交用 `vision 归档: …` 前缀。
> 本轮动作：本任务书现 ≈24KB（在上限内）⇒ 暂时无需归档；一旦 >32KB 即自行滚动（`MEMORY_VISION.md` 已贴 32KB 上限，优先滚它）。

### 0. 🎯 当前状态速览

> 📦 §0 当前状态速览（2026-10-05 晚版本，已过时）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；当前状态以 `MEMORY_VISION.md` 顶部状态头为准。需要时再读。

> 📦 §运维指令（2026-10-05 深夜2 · 两份 HTML 报告）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：report_vision_lp_eval.html + report_vision_aimv2_impl.html 已产出并提交。需要时再读。

> 📦 §运维指令（2026-10-05 深夜 · R12→3epoch + 方向建议）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：3-epoch 续跑 lp=20.27%（35 点 R²=0.94）；VISION_NEXT_DIRECTIONS.md 已交（方向2/3已批，方向4作废）。需要时再读。

> 📦 §运维指令 · 2026-10-05（晚 · 全量 AIMv2 训练 + 论文 §6 改写 + proxy/环境隔离口径）已归档 → run/ARCHIVE_OPERATOR_VISION.md；结论：R12b 训练完成(lp_max=18.81%) + 论文 §6 改写完成 + proxy/env 口径已同步。需要时再读。

### 1. 📌 全局口径与铁律（一次性质，对所有 R 生效）

- **外部证据**：涉及"别人怎么做"（架构/loss/评测/数据），优先读官方仓库或论文原文（能 clone 就 clone）；二手描述可以当线索，但结论要自己有依据（本线曾因此出错过一次）。
- 不重跑已落盘训练；不改 R8/R9/R10 已落盘结论（只在 §2 明确"修正"条目下补限定）。
- 控变量：除被考察变量外，数据/塔/步数/优化器/评测口径全部固定。
- 公平性：加 decoder 的臂需报「参数量 + 训练 token + 每步耗时」，与 acc 并列（否则不是同一把尺子）。
- **判据先行**：判据在测之前定好，测完就按那个判；若中途发现判据本身有问题，写清「原判据 → 为何要改 → 改后的结论是否仍成立」。
- 体积：`MEMORY_VISION.md` 与 `BAIZE_VISION_TASK.md` 各 ≤32KB（超限滚动，见「📉 体积维护规程」）。

### 2. 🚩 必做修正（✅ C1/C2 均已完成 → 归档 `ARCHIVE_OPERATOR_VISION.md`）

> 📦 C1（数据量口径）✅ 已在报告中统一三类分母（18.5M/29M/103M）；C2（R8 结论限定）✅ 已在报告中标注「自研改编版，非官方模型」。需要时读归档。

### 3. 🔜 任务队列

> 📦 §3 任务队列（全部已完成/取消/暂缓）已归档 → `run/ARCHIVE_OPERATOR_VISION.md`；结论：R14/E1/R11-L/L2/F/G/H/R13 全部完成，臂⑤/iGVLM 已取消。当前活跃任务见运维指令区（④-4ep 训练 + LLaVA-OV1.5 复现计划 + 中文报告）。需要时再读。

---

### 5. 📚 背景参考（输入素材，不是任务）

> 📦 §5 背景参考（2026-10-03）已归档 → run/ARCHIVE_OPERATOR_VISION.md；**结论**：含 R9/R10 关键事实 + 官方资源核实 + 数据侧硬约束 + 口径提醒。需要时再读。
> ⚠️ **口径提醒（现行）**：R6/R7 的「正式训练切 GPIC `short`」是另一条线；R9/R10 的 scaling 实际用的是 CC12M+Amshaker —— 报告里必须写清这条区分。

## 📁 历史轮次已归档（为省 prompt token）

ROUND 2–9 的完整任务原文已移至 `run/vision/ARCHIVE_ROUNDS_2-9.md`。

- 这些轮次均已完成；结论以 `EXPERIMENTS_VISION_ROUND{2..9}.md` + `EXPERIMENTS_VISION.md` 顶部为准。
- 需要查旧轮细节时再去读归档文件；不要把整份归档读进上下文。
- 当前指令全部在本文件上半部分（运维指令区）。
