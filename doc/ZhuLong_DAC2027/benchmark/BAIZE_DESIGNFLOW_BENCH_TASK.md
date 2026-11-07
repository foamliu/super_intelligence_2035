# BAIZE_DESIGNFLOW_BENCH_TASK.md — 设计流 Benchmark 任务书（2026-10-30 重构版）

### 📌 常驻 · 论文观察日报（research 线产出 · 2026-11-07 用户令）

> 索引：`doc/personal-watch/run/research/daily/index.html`｜最新一期：`doc/personal-watch/run/research/daily/<日期>.html`
> 更新：每日 06:00 / 18:00（本地时区）。每期含「对各线的可执行建议」节，覆盖 pretrain / vision / harness / data / zhulong / designflow（含本 benchmark 的造题/保真度/判分）。
> 用法：每次唤醒 `git pull` 后先看索引最新一期；若「designflow 建议」有相关条目 -> 纳入本轮计划，并在心跳注明「来自 research 日报 <日期>」；无相关条目则忽略，不影响既有排期。
> 定位：仅作输入参考、不构成新指令；与本任务书冲突时以本任务书为准。

### ✅ 用户令 · 2026-11-03 22:3x（**LLM trace triage pilot**）·【已完成 11-04：mc>=30 候选池 1369 session + 0.8B 两级预筛（规则+0.8B），0 reject，见 trace_prefilter.py】

> 执行 `benchmark/designflow/llm_trace_triage/LLM_TRACE_TRIAGE_ORDER.md`（以该文件全文为准）。
> 一句话：本机 `Qwen3.5-0.8B Q8_0` 对 4 个 mc 箱各 8 条（共 32）做语义判定 → 量化「mc>=100 误命中率」与「mc<100 漏检数」→ 产出 `pool_llm_v1.tsv`。
> 硬约束：**0.8B 只做 triage，不替代 deepread**；原始 messages 不入库；不占 8090（用 18081）；不改现有 case 队列。
> 交付：`reports/report_designflow_llm_triage_zh.html` + `compare.json` + `pool_llm_v1.tsv` + MEMORY + commit `designflow triage:`。
> 判据：金标一致率 >=80%；**PASS 后先报告再等令**，不要擅自扩量或改阈值。

### 🚨 2026-11-02 运维令：被测换 cline + PreToolUse 防泄题 hook · 用户直令 · 最高优先

> **背景**：pi 有 bash/read/write 工具，能任意读 cwd 里所有文件。benchmark agent 在 `.pi_debug/<case>/` 里放了 `_reference_check.py`（= check.py 判分器），pi 直接 `import _reference_check` 跑了它——**判分标准（答案）直接放在考生面前**。这是通过率偏高的主因，不是模型强。
>
> **用户直令**：「把被测换成 cline，参考 zhulong 评测现有的防泄题 hook 机制（PreToolUse）。」

**一、换被测：pi → cline**

1. **被测 agent 改为 cline CLI**（已安装 `~/.local/bin/cline` v3.0.51）：
   ```bash
   cline -c <workdir> -m <model> -k <key> --auto-approve true --json --thinking medium "<prompt>"
   ```
   - `-c <workdir>`：独立 session workdir（**不放 check.py / reference / jsonl**）
   - `-m <model>`：用 `deepseek-v4-pro-cloud`（与 pi 同模型，公平对比）
   - `--auto-approve true`：自动批准工具调用（headless）
   - `--json`：结构化输出
   - key 从 `~/.cline/data/secrets.json` 或 `$OPENAI_API_KEY` 解析

2. **cline 的 MCP 配置**：cline 也要能调 eda_flow MCP（和 pi 一样）。复用 `~/.cline/data/settings/cline_mcp_settings.json`（已配 eda_flow @ `http://127.0.0.1:18891/mcp`）。如果 cline 用独立 data-dir（如 `--data-dir ~/.cline_eval`），需把 MCP 配置复制过去。

3. **不再用 `.pi_debug/`**：废弃所有 pi_debug 目录。新评测目录改用 `designflow/cline_eval/<case_id>/`。

**二、PreToolUse 防泄题 hook（复用 EDA-Flow-Bench 现有机制）**

1. **hook 脚本**：`EDA-Flow-Bench/scripts/cline_hooks/PreToolUse`（已存在，可直接用）。
   - 作用：拦截 cline 的 `read_files`/`list_files`/`write`/`search_codebase`/`run_commands` 工具，只允许访问 workspace 内文件；MCP 工具（`mcp__eda_flow__*`）放行。
   - `hook_scope.txt` 机制：同目录写 `hook_scope.txt`（本批次根路径），hook 只对 workspace 落在该路径内的会话启用限制，其余 cline 会话放行。

2. **部署**：评测前把 hook 复制到 `~/.cline/hooks/PreToolUse`（cline 的全局 hook 搜索路径）：
   ```bash
   cp EDA-Flow-Bench/scripts/cline_hooks/PreToolUse ~/.cline/hooks/PreToolUse
   chmod +x ~/.cline/hooks/PreToolUse
   # 写 scope（本批次 workdir 根）
   echo "<workdir_root>" > ~/.cline/hooks/hook_scope.txt
   ```
   评测结束后移除（或保留——scope 机制会让非评测会话放行）。

3. **关键：workdir 里只放 prompt + assets（A 输入）+ task_brief**：
   - ✅ 放：`prompt.txt`、`assets/`（case 的真实输入文件 A）、`task_brief.md`（≤3 行交付接口说明）
   - 🚫 不放：`check.py`、`_reference_check.py`、`reference/`、`negative/`、`hidden/`、jsonl、test 字段
   - cline 只产出 `outputs/submit.zip`，然后退出

4. **判分在 cline 退出后独立跑**（不在 cline 的 cwd 里）：
   ```bash
   # cline 跑完，退出
   # 独立进程判分：
   cp <workdir>/outputs/submit.zip /tmp/judge_<case>/
   cp reference/<case>/check.py /tmp/judge_<case>/
   cd /tmp/judge_<case>/ && python3 -c "from check import check; print(check('submit.zip', '.'))"
   ```
   判分器（check.py）**绝不进 cline 的 workdir**。

**三、pi_debug_status.jsonl → cline_eval_status.jsonl**

1. 新建 `designflow/cline_eval_status.jsonl`（格式同 pi_debug_status.jsonl，追加 `harness:"cline"` 字段）
2. pi_debug_status.jsonl 保留作历史（不删），但新评测只写 cline_eval_status.jsonl
3. 日报 `gen_daily_report.py` 改为读 cline_eval_status.jsonl（pi 数据标"历史"）

**四、执行**

1. 先建一个 `designflow/cline_eval/run_one.sh` 脚本：部署 hook → 建 workdir（只放 prompt+assets+task_brief）→ 跑 cline → 独立判分 → 记 status
2. 拿一条现有 PASS 的 case（如 Schematic-001）用 cline + hook 重跑，验证：
   - hook 生效（cline 试图读 workdir 外文件被拦）
   - cline 看不到 check.py
   - 判分独立跑，结果真实
3. 逐步把存量 case 用 cline 重跑一遍，得到真实通过率
4. 收尾铁律提交

**五、为什么换 cline**

| 项 | pi | cline |
|---|---|---|
| shell 工具 | 有 bash/read/write/edit（任意访问） | 有 read/write/bash（但被 PreToolUse hook 拦截） |
| 防泄题 hook | 无 | PreToolUse（EDA-Flow-Bench 现成） |
| session 日志 | `~/.pi/agent/sessions/` | `~/.cline/data/sessions/`（结构化 JSONL） |
| MCP 支持 | 有 eda_flow | 有 eda_flow（已配） |
| headless | `--print --no-approve` | `--auto-approve true --json` |

cline + PreToolUse hook = agent 只能看 workspace 内文件（prompt + assets），判分器在 workspace 外独立跑，**彻底消除泄题**。

### 🚨 2026-10-31 21:5x 运维令：`test 思路` 必须是「k 条断言」（**硬闸门 + 打回重写**）· 用户直令 · 最高优先

> **背景**：§4.6 昨天已要求 `k 条断言：①…`，但 10_31 日报 **30 条 case 里 0 条达标**（全文“断言”出现 0 次，全部仍是散文式，如「解 zip 校验 5 文件…」）。原因不是理解偏差，是**没有闸门**。本轮起改成硬闸门。

**规则（每条 case、每一轮都必须过）**
1. **写**：`metadata.test_rationale` 必须**以 `k 条断言：` 开头**，后接 ①②③…，**与 `check()` 中可独立失败的条件一一对应**，每条写「对象 + 判定」。🚫 散文 / 🚫 实现细节（`raise`、`zipfile`）/ 🚫 「校验交付件完整性」式废话。
2. **对账（落 jsonl 之前）**：agent 必须**先把 `check.py` 的条件标签列出来**（a–n，或 `CONDITIONS = [("a","…"), …]` 表），数出 `k_check`；判据 **`k_rationale == k_check` 且 `k_check ≥ 8`**。
3. **不过就滚回去改**：`k_rationale ≠ k_check` 或 `k_check < 8` ⇒ 该 case 标 **`incomplete`**：🚫 不许 `mark --status case`、🚫 不许追加进 jsonl、🚫 不计入通过率；写入 `designflow/rewrite_queue.tsv`，**下一轮第一件事就是修它**，修完才准开新 case。
4. **日报必须自证**：`gen_daily_report.py` 的 case 表**新增三列** `k(断言)` / `k(check)` / `一致`；任一 case 显示 `✗` 或 `—` ⇒ 当日日报判「未交付」，心跳写 `DEBT:<n>`。
5. **存量 30 条**：按 §4.6 全部视为未完成；每轮从 `rewrite_queue.tsv` **修 1 条**，直到清零，心跳写 `断言清单 x/30`。
6. **心跳新增一行**：`🧾 断言: k_rationale=k_check=n ✓/✗（今日 x/30 达标）`。

> 📦 体积：本令约 1.5KB；TASK 现 17KB，远低于 40KB 红线。


### 🚨 2026-10-31 21:3x 运维令：A/B 双档 casemaking（trace-faithful 试点 10 条）· 用户直令 · 最高优先

> **用户原话**：「如果只把真实 trace 中用户的意图作为任务说明，不妄做修改，是否难度就可以提升、通过率下降？」→「好的试试看」
> **判断（运维）**：当前通过率偏高，主因不是模型强，而是**合成的 `task_brief.md` 替模型把题读懂了**——交付形态、资产用途、验收点全写明，难度被稀释。本轮起引入 **A 档（trace-faithful）**。

#### ① A 档（本轮试点 10 条，唯一硬交付）
1. **任务说明 = 该轮用户原话逐字原文**：按红线 #2 **不脱敏、不改写、不补全**（仅 key/token/密码掩码）。🚫 不许把口语改写成规整需求。
2. **选轮规则（关键）**：只取「**提出需求 / 表达目标**」的用户轮；🚫 **凡用户已指出根因或给出修复方案的轮，一律不得用作 A 档任务说明**（可另存为 hint，不进 prompt）。
3. **接口固定 ≠ 改意图**：契约照旧 —— `mode:design_flow` + `entry_point=outputs/submit.zip` + `test=check(deliverable, workdir)` 双参；`task_brief.md` **只写「交付接口与文件位置」≤3 行，不写「要做什么」**。
4. **金标准** = trace 末尾**用户实际接受的结果**（工具真实产物），人工复核一次；断言只对事实（数值容差 / 拓扑等价 / 产物确由工具生成），🚫 不对措辞、不许拿合成 brief 反推答案。
5. **隐藏 B 照旧**（换输入 / 反转结构 / 多 seed），防硬编码与猜答案。
6. **资产用该轮真实 attachments**（原文），不加说明性注解。

#### ② B 档（synthesized）= 现有做法
保留作 L1 补牙 / 教学 / 消融。**A、B 两档通过率分开报，🚫 混算**（这同时修掉「最近 20 条混算 L1+L2」的口径缺陷）。

#### ③ 试点与判据
- 先做 **10 条 A 档**，优先覆盖 **L2 真跑商业工具**的域（spice_sim / physical_verify / schematic_netlist / layout_*）。
- 每条用同一口径跑 pi（`pi 1.4.0` / `deepseek-v4-pro-cloud` / `--thinking medium`），记录 pass/fail + **失败归因四类**：①交付形态/位置错 ②前提缺失（需澄清/需上一轮状态）③能力不足 ④判分歧义。
- **判据**：A 档通过率 **≤10%**，且「①+④」类失败占比 **≤30%**（否则先修接口与判分，不许把格式失败当难度）。
- 交付：10 条追加进同一 jsonl（加 `metadata.track: "faithful"`；🚫 不新建 jsonl）；日报加「A/B 分档通过率」两行；中文 HTML 报告落 `doc/ZhuLong_DAC2027/reports/`。

#### ④ 口径调整（覆盖 §0 的单一目标）
- B 档：通过率目标 **20–30% 不变**；
- A 档：**本轮不设目标、只报数**，试点后用实测定档；
- 任何对外数字必须标档位（A / B），🚫 用 B 档数字代表真实难度。

> 📦 体积：本令约 1.7KB，TASK 已超 40KB 红线（agent 只读）；运维下轮归档已闭合块。



> **本文件由运维维护（agent 只读）**。运行时状态写 `MEMORY_DESIGNFLOW.md`、`EXPERIMENTS_DESIGNFLOW.md`、`daily-memories-designflow/`。
> 旧版全文（即时令 VII/VIII/IX/X/XI/XII、运维增补 I–IV、收尾铁律、体积规程）已**原文归档** → `ARCHIVE_OPERATOR_DESIGNFLOW.md`「归档批次 48」。本版把上述指令**按主题融合**，不再按时间堆叠。

## 0. 目标（一句话）

用 `.75` 内网 **698 台机 / 2,850 用户 / 52,698 会话（24,085 条 IC-EDA 命中）** 的真实 cline 轨迹，构建「设计流编排」评测集；**难度必须校准到 pi-SUT 通过率 20–30%**——不是"能跑通就算过"。

## 1. 红线（不可协商）

1. **真实 trace 才有资格**：每条 case 必带 `metadata.trace_source{user, host, session_file, match_count, real_task_summary}`。没有真实 trace 的 case 一律删除，🚫 不许改个名字保留。
2. **不脱敏（全产物）**：`user` / `host` / `session_file` / `/home/<user>` 路径 / `prompt` / `attachments` / 深读笔记 / 日报 / MEMORY **一律保留原值**；只有 **key / token / 密码** 需掩码。🚫 prompt 里出现"脱敏""不要出现真实用户名"字样视为违规。
3. **单一 jsonl**：只往 `benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl` 追加；🚫 新建 jsonl（>500 条才按 `metadata.domain` 拆 4 个）。
4. **只读纪律**：对 698 机只 `find`/`ls`/`cat`/`head -c`/`awk`/`python3` 只读；🚫 写目标机、🚫 `rm`/`tee`/`>`；🚫 本机自扫；🚫 lineage 自审计 / §X 递归。
5. **git 双仓**：workspace + 日报 → `super_intelligence_2035` **main**；用例产物 → `EDA-Flow-Bench` **master**；🚫 `git add -A`。
6. **体积**：本 TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限按 §8 归档（原文搬 ARCHIVE，留 1 行指针）。

## 2. 环境速查

| 项 | 值 |
|:--|:--|
| workspace | `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/` |
| 用例仓库 | `/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（jsonl / assets / reference） |
| 历史快照 | `EDA-Flow-Bench/agent_workspace/designflow/`（bench_v0.1~v0.50，只读，不迁） |
| 运行时 cwd | `/nasdata/app.e0031982/code/EDA-Flow-Bench/` |
| 沙盒入口 | `eda_flow` MCP `http://127.0.0.1:18891/mcp` → `.75`（`hfhds201` / `10.129.32.75`）`run_commands`·`run_code`·`read_file`·`write_file` |
| 扫描结果 | `.75:/home/t0002965/log/ssh_eda_search_20261028_174426/summary.tsv`（列：`ip host user session_file match_count keywords tools`） |
| 评测框架 | `./RUN_EVAL.sh --design-flow` / `--design-flow-agent`；`scripts/run_design_flow_batch.py`；`config.yaml`；`docs/design_flow_session_backend.md`（§3 接口 / §9 判分两步）；`docs/设计流Benchmark-{测试用例编写指南,框架改进设计文档}.html` |
| pi（被测） | `pi` 1.4.0，provider `cxmt` / `deepseek-v4-pro-cloud`，已配 `eda_flow` MCP。调用：`pi --print --no-approve --model deepseek-v4-pro-cloud --thinking medium "<prompt>"`（Node 22 需在 PATH：`export PATH=/nasdata/app.e0031982/.local/node-22/bin:$PATH`） |
| 日报 | `cd <benchmark>/designflow && python3 gen_daily_report.py` → `doc/ZhuLong_DAC2027/reports/report_benchmark_MM_DD.html`（运维已加独立「用户」列，**别再重复改**） |

**命令模板（只读抓 trace）**
```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
ssh -o BatchMode=yes -o ConnectTimeout=8 <ip> "ls /home/*/.cline/data/sessions/*.messages.json | head -20"
```
> `.75` 已对 **697/698** 台免密（`e0031982` 身份）。**分批 5–10 台/次**，别一次扫 698 台（会超时）。

**三个已知坑（别再踩）**
1. **GitHub 假阴性**：`curl https://github.com` 在剥掉 proxy 的环境里返回 `000`，但 `git push` 走 `git config --global http.proxy` 仍可通。**判据用 `git ls-remote origin HEAD`，不要用 curl**。（确需代理：`git config --global http.proxy http://172.19.92.23:13128`）
2. **`write_file(content_base64=...)` 会腐蚀内容**（`$dA` → `$d\x01`）：一律用 plain `content` 字符串，或 `run_commands` 里 `base64 -d` 在本机解码。
3. **`ssh` 在 eda_flow 里会 hang**：命令前加 `</dev/null`（`-n` 反而会断 stdin pipe）。

## 3. 用例契约（proper `design_flow`）

```text
mode:        "design_flow"
entry_point: "outputs/submit.zip"
test:        "def check(deliverable, workdir): ..."   # 双参，返回通过 / 抛异常失败
prompt:      自然语言，写真实场景（真实用户名/路径/工具/指标），不是函数签名题
attachments: [assets/<task_id>/...]                    # 真实输入文件
metadata:    { trace_source{...}, domain, test_rationale }
```
🚫 不带 `lang` / `host` / `runtime`；🚫 不写"实现 `xxx(args)->dict`"这类抽象题。

**单轮闭环 + 交付定义（DoD）**

一轮 = 一条 case 从选料到落库，**不要拆成两轮**：
`选料 → 深读 → 合成 → 自验(ref PASS + §4.9 三假提交 FAIL) → 追加 jsonl → 日报一行`

- **深读是硬闸门，但不是独立的一轮**：必须先解析完整对话流（`scp` `messages.json` → user 意图 / assistant 工具链 / 关键产物 → `designflow/trace_deepreads/<sid>_<主题>.md`）才允许合成；已有笔记可直接复用，不重复深读。
- **DoD（交付定义）**：1 条 case 通过自验并写进 `EDA-Eval-DesignFlow.jsonl` 才算交付；**深读笔记是中间产物，不算交付**。
- **每轮只做 1 条 case**：做完即收尾，**不在同一轮开第二条**（控制上下文不膨胀）；交付后首行 `WAITING: 0`，loop 60s 后唤醒做下一条。
- **唯一例外**：单条 trace 过大（>2MB 或 >600 msgs）允许本轮只深读，但**下一轮必须先交付 case**，心跳记 `DEBT: 1 deepread 未合成`；🚫 禁止连续两轮只深读。
- **选 trace 一律走台账（唯一去重口径）**：`python3 designflow/trace_ledger.py next --n 5` → 按它给出的 awk 在 `.75` 上取候选（**已自动排除台账里的 session**）→ 选第一条 → `claim` 落台账。
  - 出完 case：`mark --session <s> --status case --case-id <EDA-Eval-DesignFlow-XXX>`（覆盖率的唯一分子）；
  - 暂缓：`mark --session <s> --status parked --note "<原因>"`（如 aether 超时），**不重复捡**。
  - 🚫 禁止凭记忆/凭 jsonl 目测选 trace；🚫 禁止跳过 claim 直接开工（去重与进度都会失真）。
- 选料偏好：`match_count` 高 + **该 domain 尚无 case**（domain 覆盖优先于纯命中数）。

## 4. 判分质量（"有牙"，缺一不可）

1. **隐藏输入 B**：A 给 SUT 看，B 放 `assets/<id>/hidden/` + `hidden_manifest.json`，**不进 SUT 沙箱**；`check()` **只跑 B**，B 与 A 在规模/取值/结构上必须不同（不是换文件名）。
2. **真跑候选**：≥1 个条件用 `subprocess` 在 B 上执行候选脚本，断言**输出结构**（解析成字段/拓扑/计数再比较），不是文本相似。
3. **≥8 个独立条件**，每个单独可 FAIL；🚫 "仅成员名 / 仅子串出现"式断言。
4. **负样本入库**：`reference/<id>/negative/` ≥2 个错解（naive / always-XXX stub）+ `negative_selftest.py`，一次跑完必须**全 FAIL**；每轮抽查 1 条重跑。
5. **随机化**：在 B 上随机抽子集（net / signal / 行），3 个随机种子跑 3 次结论一致；🚫 把期望值硬编码成固定串。
6. **`metadata.test_rationale` = 逐条断言清单（不是摘要）**：格式固定 `k 条断言：①<验什么> ②<验什么> …`，**一条对应 `check()` 里一个可独立失败的条件**，写清"对象 + 判定"。
   - ✅ `7 条断言：① zip 内 5 个文件齐全 ② mac4.v 有 module mac4 且端口 clk/rst_n/acc0 齐全 ③ 累加为 32-bit 有符号饱和（边界 0x7fffffff/0x80000000） ④ sim_mac4.log 含 MAC4_SIM_PASS 且无 MAC4_SIM_FAIL ⑤ …`
   - 🚫 废话：`解 zip 校验 3 文件`、`校验交付件完整性`、`断言内容达标`
   - 🚫 实现细节：`raise AssertionError(...)`、`zipfile.ZipFile(...)`、`z.read(...).decode(...)`
   - 自检：`k` 必须等于 §4.3 要求的独立条件数（≥8）；两者对不上 = 未完成。⇒ 按顶部令 21:5x 执行：标 `incomplete`、进 `designflow/rewrite_queue.tsv`、🚫 不许落 jsonl、🚫 不许计入通过率。
7. `check()` 在**独立临时目录**解 zip；🚫 在 SUT workdir 留 `__chk`。
8. **泄漏隔离**：SUT 沙箱不得包含 `benchmarks/EDA-Eval-DesignFlow/`（`reference/`、jsonl、`test` 字段）；结论写 MEMORY 一行。
9. **退化提交回归**：每条 case 必须让 (a) 空壳 (b) 只 print 期望串 (c) 参考解删核心 三种假提交**全部 FAIL**；任一 PASS ⇒ 该 case 判分不合格，限期整改或下线。

## 5. 难度校准（立即生效）

| 层 | 定义 | 配额 |
|:--|:--|--:|
| L1 | 离线 Python 复刻（读附件写脚本） | **≤30%** |
| L2 | 真跑沙盒工具（calibre LVS/DRC、Virtuoso、PrimeTime、VCS，经 eda_flow / .75） | **≥50%** |
| L3 | 多工具链路 + 修复 + 回归（DRC 179→0、LVS 干净 CORRECT、ERC 全清） | **≥20%** |

- 新建 case **只做 L2 / L3**；L1 仅用于补牙维护。
- 总样本 **<30 条前不报通过率**，只写"已跑 n 条中 x PASS"（6 条算百分比没有统计意义）。
- 滚动窗口（最近 20 条已跑）目标 **20–30%**：
  - **>50% ⇒ 自动判"太简单"**：上隐藏输入 B / 加条件 / 换更难 trace，下轮重跑；
  - **<10% ⇒ 先查 `check()` 误判**（ref 是否真能 PASS），再考虑降难；
  - 20–30% ⇒ 保持。
- 心跳每轮写一行：`🎯 通过率: 最近20条 x/20 = y%（目标20–30%）`。

## 6. 每轮流程

1. `trace_ledger.py next --n 5` 取候选 → `claim` → 深读（有笔记就复用）→ 合成（`assets/` `reference/` `hidden/` `negative/`）。
2. 自验：`reference/` 参考解跑 `check()` 必 PASS；§4.9 (a)(b)(c) 三假提交必 FAIL；`negative_selftest.py` 全 FAIL。
3. pi 实跑：`designflow/pi_debug_status.jsonl` 追加一行，记 `pi_model / pi_thinking / pi_dur_sec / pi_verdict / ref_check`。
4. **先过断言闸门**（`k_rationale == k_check ≥ 8`；不过 ⇒ 标 `incomplete` 进 `rewrite_queue.tsv`，本轮只改它、不开新 case）→ 追加 jsonl → **`mark --status case --case-id <id>`** → 日报：`python3 designflow/gen_daily_report.py`（含「用户」列、`k 条断言` 清单、trace 覆盖率进度条）。
5. 难度回路：按 §5 判定"加难 / 保持 / 查判分"，结论写进当日日报的"阻塞/下一步"。
6. 收尾：`WAITING: 0`（下一轮 60s 后立即开下一条 case）；仅真外部阻塞（pi 异步未回 / 推送失败 / 等人工）才写 `WAITING: 1`。

## 7. 当前基线（每轮只更新这一行，不堆历史）

`11 条 proper（10 域）· 已跑 6 条 = 6 PASS · 6 trace_deepreads · test_rationale 断言清单 0/30（硬闸门见顶部令 21:5x）· 目标通过率（B 档）20–30%`
`📊 trace 覆盖率：见 designflow/trace_ledger.py stats（covered / mc≥30 候选池）`
明细看日报 `reports/report_benchmark_MM_DD.html`；历史结论看 `EXPERIMENTS_DESIGNFLOW.md`。
> 现存 11 条的 `test_rationale` 本轮内全部改写成 `k 条断言：①…`（k = 该 case `check()` 的独立条件数）。

## 8. 收尾（轻量结账，不是每轮做全套）

> 收尾是"结账"：**一轮 = 1 条 case = 1 次结账**。别把结账做成产出，也别攒着不提交。

0. **体积自检**：TASK ≤32KB（红线 40KB）、MEMORY ≤32KB；超限先把已闭合块**原文**搬 `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针），搬前 `git pull --rebase --autostash`，🚫 不改小节编号/标题。数字抄进心跳：`📦 体积：TASK=nKB / MEMORY=nKB`。
1. **心跳（轻）**：`MEMORY_DESIGNFLOW.md` 顶部快照**只改变化的几行** + **追加 1 行流水**（三口径 + `🎯 通过率` + `📊 trace 覆盖率 x/y=z%` + `DEBT`）；🚫 每轮重写整份快照。
   - 顺带刷新候选池：在 `.75` 上跑一次 `awk` 统计 `sessions / mc30 / mc100 / mc300`，然后
     `python3 designflow/trace_ledger.py refresh --json '{"sessions":N,"mc30":1369,"mc100":696,"mc300":1001,"target_mc":30}'`
     （进度条的分母与"新增 traces"都来自这里）。
2. **日记忆**：`daily-memories-designflow/<YYYY-MM-DD>.md` **当天首轮创建，之后只追加**。
3. **提交**：**每轮（1 条 case）结束即提交**（loop 另有每 30 分钟兜底）；🚫 把工作留在工作树过夜。双仓命令：
```bash
cd /nasdata/app.e0031982/code/super_intelligence_2035 && git fetch origin && git pull --rebase --autostash origin main
git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
           doc/ZhuLong_DAC2027/benchmark/designflow \
           doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
           doc/ZhuLong_DAC2027/reports
git commit -m "designflow #<轮次>: <一句话>" && git push origin main

cd /nasdata/app.e0031982/code/EDA-Flow-Bench && git fetch origin && git pull --rebase --autostash origin master
git add -- benchmarks/EDA-Eval-DesignFlow
git commit -m "designflow #<轮次>: <一句话>" && git push origin master
```
4. **闭环自检**：`git status -sb` 无 ahead/behind；push 失败重试 1 次并记报错原文。

> ⏱ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

## 9. 待确认（未确认前按默认走）

- Benchmark 是否对外（默认：先内部）
- 是否允许主动扫描 698 机（默认：否，只被动只读发现）

---

> ⚠️ 本文件为**只读指令文件**，agent 禁止修改；有异议写进 MEMORY 并存疑执行。

