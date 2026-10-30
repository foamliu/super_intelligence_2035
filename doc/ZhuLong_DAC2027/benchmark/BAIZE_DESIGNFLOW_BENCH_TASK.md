# BAIZE_DESIGNFLOW_BENCH_TASK.md

## 🔧 运维指令区（每次唤醒先读）

### 🚨 2026-10-30 运维即时令 X：workspace 已迁移到 ZhuLong_DAC2027/benchmark/ · 最高优先（先读）

> **运维令**：「你的 workspace 已从 `EDA-Flow-Bench/agent_workspace/` 迁到 `super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/`，和 zhulong agent 统一管理。你写的用例还是提交到 EDA-Flow-Bench。读完这条继续执行即时令 VII/VIII/IX。」

**一、新路径（硬，记住）**
- **workspace**（你的状态/任务书/心跳/脚本）：`/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/`
- **用例产物**（你建的 jsonl/assets/reports）：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/` + `docs/reports/`（**没变**）
- **历史快照**（bench_v0.1~v0.50）：仍在 `/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/designflow/`（不迁，用绝对路径访问，只读）
- **运行时 cwd**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/`（loop 脚本已设，方便读写 benchmarks/ + docs/reports/）

**二、双仓库提交（重要，别搞混）**
- **workspace 文件** → `git -C /nasdata/app.e0031982/code/super_intelligence_2035 add -- doc/ZhuLong_DAC2027/benchmark/...` → **`push origin main`**（分支=main！）
- **用例产物** → `git -C /nasdata/app.e0031982/code/EDA-Flow-Bench add -- benchmarks/EDA-Eval-DesignFlow docs/reports` → **`push origin master`**（分支=master！）
- 两个仓库分支不同：**super_intelligence_2035=main，EDA-Flow-Bench=master**。push 错分支会失败。
- 收尾铁律的 git 命令已更新为双仓库版（见文末），照抄即可。

**三、gen_daily_report.py 路径已改**
- 日报脚本现在用 `EDA_FLOW_BENCH_ROOT` 环境变量或硬编码 `/nasdata/app.e0031982/code/EDA-Flow-Bench` 找用例和 reports 目录。
- 跑法不变：`cd <benchmark>/designflow && python3 gen_daily_report.py`，产物落到 `super_intelligence_2035/doc/ZhuLong_DAC2027/reports/report_benchmark_MM_DD.html`（workspace 仓库，提交时走 main）。

**四、旧 workspace 不删（作备份）**
- `EDA-Flow-Bench/agent_workspace/` 保留，但**你不再往那写**。新写入只去 `benchmark/`。
- 旧位置的 bench_v0.x 历史快照照常用（统计 release 数等），只读。

**五、执行**
- 读完这条，继续执行即时令 VII（读 docs）→ VIII（合并 jsonl，若已合并跳过）→ IX（深读真实 trace）。
- 第一轮先在 MEMORY 记一行"[迁移] workspace 已在 ZhuLong_DAC2027/benchmark/，双仓库提交规则已理解"。

### 🆕 <YYYY-MM-DD> 初始化：构建设计流 Benchmark · 用户直令 · 最高优先

> **用户令**：「构建一个真实场景的设计流 Benchmark。真实用户约 500 且持续增长。」

**执行位置（硬）** · ⚠️ 2026-10-30 迁移：workspace 已从 EDA-Flow-Bench/agent_workspace 迁到 ZhuLong_DAC2027/benchmark/
- **workspace 目录（你的状态/任务书/心跳/脚本）**：`/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/`
  - 任务书：`benchmark/BAIZE_DESIGNFLOW_BENCH_TASK.md`（即本文件）
  - 心跳：`benchmark/MEMORY_DESIGNFLOW.md`
  - 日报脚本：`benchmark/designflow/gen_daily_report.py`
  - 历史快照（bench_v0.1~v0.50）：**仍在** `/nasdata/app.e0031982/code/EDA-Flow-Bench/agent_workspace/designflow/`（不迁，用绝对路径访问）
- **用例产物目录（你建的 jsonl/assets/reports）**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/` + `docs/reports/`
- **agent 运行时 cwd**：`/nasdata/app.e0031982/code/EDA-Flow-Bench/`（loop 脚本已设，方便读写 benchmarks/ + docs/reports/）
- **双仓库提交规则（重要）**：
  - workspace 文件（TASK/MEMORY/EXPERIMENTS/ARCHIVE/designflow/pi_debug/daily-memories）→ `git -C /nasdata/app.e0031982/code/super_intelligence_2035 add -- doc/ZhuLong_DAC2027/benchmark/...` → `push origin main`
  - 用例产物（benchmarks/EDA-Eval-DesignFlow + docs/reports）→ `git -C /nasdata/app.e0031982/code/EDA-Flow-Bench add -- benchmarks/EDA-Eval-DesignFlow docs/reports` → `push origin master`
  - **两个仓库分支不同**：super_intelligence_2035 用 `main`，EDA-Flow-Bench 用 `master`。别搞混。
- 本机 IP：`10.251.36.15`
- MCP 入口：`eda_flow`（`127.0.0.1:18891`，已注册 opencode）→ `.75`（`hfhds201`，`10.129.32.75`）
- 跳板机：EDA 服务器 `.75`；目标机：内网 698 台 Linux（SSH 只读，增补 IV）

**需求**
- 从 EDA 服务器 `.75`（经本机 `127.0.0.1:8092` MCP 执行命令）探查内网 Linux 服务器，
  扫描 `/home/*/.cline/data/sessions/` 下**真实 agent 交互轨迹**，据此构建设计流 Benchmark。
- 样本来自真实用户，**数量持续增长**；Benchmark 必须**可复现、可评分、可扩增**。

**验收（满足即算这条线完成）**
1. 拿到内网 cline 用户 / sessions 轨迹的**资产盘点数字**（目标机数、用户数、轨迹数）。
2. 交付一个**版本化 benchmark**（v0.1 起），含：任务集、评分口径、每类样例、复现脚本。
3. 交付 HTML 报告 + 数据清单，说明规模、分类、评分方式、局限。
4. 全链路脚本化可复现（从探查到生成 benchmark 一条命令跑通）。

**红线（硬，不许碰）**
- 🚫 SSH 目标机**只读**：不改文件、不删目录、不装包、不写目标机磁盘。
- 🚫 不碰他人进程；连接失败记原文，不静默重试掩盖。
- 🚫 **隐私脱敏**：key/token/密码/域名/人名/邮箱入库前脱敏；**未脱敏样本不入 git**。
- 🚫 主动扫描（如 `nmap -sn`）**必须先获书面授权**，否则只用被动发现。
- 🚫 原始轨迹不入库，只入脱敏样本与统计。
- 🚫 不因"样本还不够 500"就等——边采集边构建，版本化交付。
- 🚫 本线不用 GPU，不与 pretrain/vision 抢资源。

**纪律**
- 三个口径数字（目标机数/用户数/轨迹数）每次唤醒从 `.75` 现查，写入心跳。
- 连续 3 轮同一卡点 → 上报，不静默硬撑。
- 共享工作副本，git 规则见文末。

### 🆕 2026-10-29 运维增补：真正出口 = eda_fastmcp_flow（18891），不是 8092 · 最高优先

> **运维令**：「8092 是 research MCP，没有 exec/ssh 能力——之前任务书写错了。真正到 .75 的出口是 `eda_fastmcp_flow` 项目，已在 opencode 注册为 `eda_flow` MCP。立即停止 lineage 自审计空转，转用 eda_flow 多机扩样。」

**前情纠错**（2026-10-29 运维实测）
- ❌ 旧任务书"经 `127.0.0.1:8092` MCP 执行命令到 .75"是**错的**。8092 = `RESEARCH-MCP-SERVER` v1.25.0，只有 `cimi_search`/`cimi_fetch`/`vqa`/`text_to_image`，**无 exec/ssh**。
- ✅ 真正出口 = **`eda_fastmcp_flow`**（`/nasdata/app.e0031982/code/eda_fastmcp_flow`），MCP 端口 **`127.0.0.1:18891`**（streamable-http → `/mcp`），后端 HTTP 转发到 `http://10.129.32.75:8670`（`eda_sandbox_flow`）。
- ✅ **已在 `~/.config/opencode/opencode.json` 注册为 `eda_flow` MCP**，opencode 启动即可用（无需额外配置）。工具：`open_session` / `close_session` / `declare_done` / `run_commands` / `run_code` / `read_file` / `list_files` / `write_file`（+ 可选 `search_apis*`）。

**实测链路（2026-10-29 运维 probe，已验证）**
- `open_session` → 返回 workdir（在 .75 的 `/proj/train/AI/workdir/.../sessions/<user>_<eval_id>_<task_id>_<sample>`）。
- `run_commands`（参数：`commands: list[str]` + `workdir: str`，**workdir 必填**）→ 在 .75 上 `bash -lc` 串行执行，cwd=workdir（**非 chroot，可访问全局 FS**）。实测 `hostname`=`hfhds201`，`ls /home` 看到真实多用户（aryaoy/dandans/daweiy/ericw/fanyang/jianwang/jiuzhou/tzuo…，**与本机 hfeg0tedaap02 完全不同**），`find /home -name sessions` 跑通。
- `read_file` / `list_files` 有 **allowed-prefixes 限制**（`/home` 不在允许前缀，返回 `dir outside allowed prefixes`）。**扫 sessions 必须走 `run_commands`，不能走 `read_file`/`list_files`。**
- `.75` hostname = `hfhds201`；本机 hostname = `hfeg0tedaap02`。**.75 是另一台机**，别再当成本机。
- probe session 用完**必须 `close_session` 清理**（红线：不写目标机磁盘→不留垃圾）。

**新工作流（替代旧的 8092 路径）**
1. `open_session(task_id="BENCH-SCAN", eval_id="<日期>-scan", user="bench_scan", sample="0")` → 拿 workdir。
2. `run_commands(workdir, commands=[...])` 在 .75 上**只读**扫描：
   - `find /home -maxdepth 5 -type d -path '*/.cline/data/sessions'` → 列所有 cline 用户
   - `find /home -maxdepth 6 -type d -path '*/.cline/data/sessions/*' | wc -l` → session 轨迹总数
   - `cat <session>/*.messages.json`（用 `head -c` 限量，避免大输出）→ 采样轨迹
   - 🚫 **只读**：不 `rm`/`mv`/`>`/`tee`/`mkdir`/`pip install` 任何东西到 .75（红线）
3. `close_session(workdir)` 清理。
4. 脱敏后入 `designflow/bench_v0.X/`，写心跳+日报+push。

**指令（最高优先，覆盖之前的"等运维"阻塞）**
- 🛑 **立即停止** v0.23/v0.30/v0.34/v0.40/v0.44/v0.46/v0.48/v0.50… 这类**纯 lineage sha256 自审计层**。已做 7 次全树审计，足够了；再造同类层 = 空转烧 token，违规。
- 🛑 **禁止 §X 递归**：不再生成"整合层→构造层→整合层"的纯元数据版本（v0.45/47/49 模式）。
- ✅ **本轮起用 `eda_flow` 重新扫 .75**：拿到 .75 真实的三个口径数字（目标机数=至少 1 台 hfhds201、.75 上的用户数、.75 上的 session 轨迹数），与本机 hfeg0tedaap02 的 3487 合并，出**多机版 benchmark**（v0.50 起 = 多机扩样层，不是审计层）。
- ✅ 三口径数字现查时**必须经 `eda_flow.run_commands` 在 .75 上现跑**，不再只查本机。
- ✅ 上报（MEMORY 里"连续 49 轮同卡点"）**作废**——卡点已解（出口已给），删掉上报段。
- 若 `eda_flow` MCP 调用失败：记原文 + `WAITING=1`，**不要**回退到 lineage 自审计。

**待确认项更新**
- ~~8092 MCP 协议~~ → 已确认是 research MCP，不是出口，作废。
- ~~SSH 账号是否免密只读~~ → 作废，不走 SSH，走 eda_flow MCP。
- sessions 文件格式：仍需在 .75 上探明（`find ... -name '*.messages.json'` 等同本机？还是不同？首轮探明写入 MEMORY）。
- 是否允许主动扫描：仍默认**否**，只用 `find`/`ls`/`cat` 被动发现 .75 上的 cline 目录。
- Benchmark 是否对外：默认先内部，不变。

### 🆕 2026-10-29 运维增补 II：沈佳成已完成 698 机扫描，结果落盘 .75，停止重扫转构建 · 最高优先（覆盖增补 I 的"重扫"指令）

> **运维令**：「不要在本机 10.251.36.15 捞交互轨迹——agent 自己就在这台机器上，分析自己的轨迹没意义，强制 RSI 循环迭代容易造成不动点。必须从 `eda_fastmcp_flow` 出口到 EDA 环境（.75 及其可达的内网机）。沈佳成已做过初步分析，最终结果全部落盘在 .75 服务器，直接用，不要重扫。」

**🛑 本机自扫禁令（硬）**
- ❌ **禁止**再扫描本机 `10.251.36.15`（`hfeg0tedaap02`）的 `/home/*/.cline/data/sessions/`。本机 3487 sessions 是 agent 自身轨迹污染，**不入 benchmark**。
- ❌ 之前 v0.1 的 2112 任务来自本机自扫，**作废**，不作为多机版基础。
- 理由：agent 在本机跑 → 本机 sessions 含大量 agent 自身的 lineage 审计/自指循环轨迹 → RSI 不动点污染。

**✅ 沈佳成扫描结果（已落盘 .75，运维 2026-10-29 经 eda_flow 实测确认可读）**

三口径数字（多机版，**以此为准**）：
| 口径 | 数值 |
|---|---|
| 目标机数 | **698** 台（全部可达；`10.129.8.86` 因会话多 905 单独重扫补全） |
| 用户数 | **2850** 个 home 目录有 `.cline/data/sessions` |
| 会话文件数 | **52,698** 个 `*.json` |
| IC/EDA 命中 | **24,085** 个会话文件（涉及 EDA 软件调用） |

EDA 调用 top（含该调用的会话数）：
- virtuoso 13263 · calibre 12664 · hspice 10757 · cellview 9389
- `"lang":"pyAether"` 3638 · `"lang":"skill"` 3334 · spectre 3279
- dbGet 2597 · waveview 2127 · synthesis 1639 · skipper 1475 · innovus 952
- dbCreateInst 925 · dbCreateRect 457 · dc_shell 181 · genus 77

热点机器（按命中会话数）：
- hfeg0plg49(2409) · hfeg0pkn003(825) · hfeg0plg17(730) · hfeg0pkn001(710)
- hfeg0pkn004(685) · hfeg0pkn002(655) · hfeg0plg76(506) · hfeg0pkn005(501)
- hfeg0plg16(477) · hfeg0plg104(471) …（top-20 见 REPORT.md）

热点用户：t0002965(2094) · e0014566(2080) · xinqiaoz(1430) · rongjiez(738) · colinxu(712) · lizwen(684) · johnl(560) · dandans(556) …

**.75 上的数据文件清单**（经 `eda_flow.run_commands` 在 .75 上 `cat`/`head`/`wc` 实测可读）

根目录 `/home/t0002965/log/`：
```
REPORT_ssh_eda_search.md      # 摘要报告（2.3KB，运维已 cat 确认）
orchestrator.sh               # 扫描编排脚本
probe_remote.sh               # 单机 probe 脚本（含 RE1/RE2 匹配正则）
run.log / orch_run.log        # 运行日志
reshoot_10.129.8.86.tsv       # 超时机重扫结果（408KB）
ssh_eda_search_20261028_174426/  # 主扫描结果子目录 ↓
```

子目录 `/home/t0002965/log/ssh_eda_search_20261028_174426/`：
```
REPORT.md       (2.3KB)   # 同根目录报告
scan.tsv        (23KB,  699 行)  # 表头 + 698 机：ip\thost\tusers_with_cline\tfiles_scanned\tmatched
summary.tsv     (4.1MB, 24086 行) # 表头 + 24085 命中：ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools
raw.tsv         (4.1MB)   # 原始 probe 输出
stderr.log      (53KB)    # ssh 警告
unreachable.log (空)      # 无不可达机
```

IP 清单：`/home/t0002965/ssh_auth_ok.txt`（698 个唯一 IP，运维已 `wc -l` 确认）。

**关键 schema（运维实测）**
- `scan.tsv` 每行一台机：`ip\thost\tusers_with_cline\tfiles_scanned\tmatched`
  例：`10.129.32.189\thfeg0pnd001\t3\t31\t9`
- `summary.tsv` 每行一个命中会话：`ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools`
  例：`10.129.32.189\thfeg0pnd001\te0045140\t1792637822804_6xv88.messages.json\t9\t.def:13;synopsys:2;\t`
  - `session_file` 是相对路径文件名，实际在 `<ip>:/home/<user>/.cline/data/sessions/<session_file>`
  - `keywords` 格式 `kw1:cnt1;kw2:cnt2;`，`tools` 可空
- 匹配规则见 `probe_remote.sh` 的 `RE1`/`RE2`（virtuoso/calibre/hspice/cellview/pyAether/skill/dbGet/waveview/synthesis/skipper/innovus/…）

**新工作流（覆盖增补 I 的"自己扫"指令；沈佳成已扫完，首选拉取已有结果）**
1. `open_session(task_id="BENCH-BUILD", eval_id="<日期>", user="bench_build", sample="0")` → 拿 workdir。
2. `run_commands(workdir, commands=[...])` **只读拉取** .75 上已有扫描结果：
   - `cat /home/t0002965/log/ssh_eda_search_20261028_174426/REPORT.md` → 全貌
   - `cat /home/t0002965/log/ssh_eda_search_20261028_174426/scan.tsv` → 698 机覆盖率（23KB，一次性拉）
   - `head -N .../summary.tsv` / `awk` 过滤 → 分批拉 24085 命中行（4.1MB，**分批 head/awk/sed 限量**，别一次 cat 全部撑爆输出）
   - `cat /home/t0002965/log/probe_remote.sh` → 匹配规则
   - 🚫 **只读**：不 `rm`/`mv`/`>`/`tee`/`mkdir`/`pip install`（红线）
3. `close_session(workdir)` 清理。
4. 把拉到的 `scan.tsv` / `summary.tsv`（或脱敏切片）存到本机 `designflow/bench_v0.X/out/`，**脱敏后**入 git（user 名 → hash，ip → 网段或 hash，session_file 名 → hash；保留 host/category/tools 统计）。
5. 基于 summary.tsv 的 24085 命中会话，**按 EDA 工具/类别分桶**构建 benchmark 任务集（不是再扫一遍）。需要深挖某会话内容时，再 `run_commands` 去 `<ip>` 上 `head -c` 采样（按需，不批量）。
6. 写心跳+日报+push。

**指令（最高优先，覆盖增补 I）**
- 🛑 **禁止本机自扫**（见上"本机自扫禁令"）；v0.1 单机集作废。
- 🛑 仍禁止 lineage 自审计层 / §X 递归（同增补 I）。
- ✅ 沈佳成已扫完 698 机，结果在 .75 上，**首选** `run_commands` 拉取已有结果（省时省资源）；如确有必要对个别机补扫，自行判断，不必请示。
- ✅ **本轮起基于 .75 上的 `summary.tsv`（24085 命中）构建多机版 benchmark** v0.50 起。
- ✅ 三口径数字 = 698 机 / 2850 用户 / 52698 会话文件（24085 IC/EDA 命中），**不再现查**，直接引用本块数字（已是 .75 落盘实测值）。
- ✅ 上报（MEMORY"连续 49 轮同卡点"）作废，删掉。
- 若 `eda_flow` 调用失败：记原文 + `WAITING=1`，不回退到本机自扫或 lineage 审计。

**待确认项更新**
- ~~sessions 文件格式~~ → 已确认 `*.messages.json`（同本机命名，见 summary.tsv 的 session_file 列）。
- ~~是否允许主动扫描~~ → 沈佳成已扫完 698 机（被动 SSH 发现 + 关键词匹配），无需 agent 再扫；agent 只读拉取结果。
- Benchmark 是否对外：默认先内部，不变。

### 🆕 2026-10-29 运维增补 III：三条新任务（评测用例落盘 / pi 被测调试 / 每日中文 HTML 日报）· 最高优先

> **运维令**：「1. 评测用例保存到 `benchmarks/EDA-Eval-DesignFlow/`，可新建 jsonl，每次睡去前提交。2. 用本机已装的 `pi` agent 作被测，调试新建的评测用例——把 `eda_fastmcp_flow` 这个 MCP 端口给 pi 配上，让它在 EDA 环境中探索和调试。3. 每天下午 4 点生成中文 HTML 日报，存 `doc/ZhuLong_DAC2027/reports/`，文件名 `report_benchmark_MM_DD.html`。」

#### 已就绪环境（运维 2026-10-29 实测确认，直接用）

**pi agent（被测）**
- 可执行：`pi`（已 symlink 到 `/nasdata/app.e0031982/.local/bin/pi` ← `node-22/bin/pi`，在 PATH）
- 版本：`pi --version` = `1.4.0`（`@earendil-works/pi-coding-agent`）
- provider：`cxmt`（`http://agi-gateway.cxmt.com/cloud/v1`，key 已配 `~/.pi/agent/models.json`），默认模型 `deepseek-v4-pro-cloud`
- MCP：**`eda_flow` 已配**（`pi mcp add eda_flow --url http://127.0.0.1:18891/mcp`，`pi mcp list` 显示 connected, 8 tools），配置在 `~/.pi/agent/mcp.json`。pi 可直接调 `open_session`/`run_commands`/`run_code`/`read_file`/`list_files`/`write_file`/`close_session`/`declare_done` 操作 .75 EDA 沙盒。
- 会话/凭证目录：`~/.pi/agent/`（settings.json / models.json / auth.json / sessions/）
- 调用示例（非交互单轮）：`pi --no-approve -m deepseek-v4-pro-cloud "<prompt>"`；多轮工具循环见 pi 文档 `--tools` / codemode。pi 是被测，编排 agent（你）不要替它写代码，让它自己跑。

**评测框架（本仓库已有）**
- 入口：`RUN_EVAL.sh`（repo 根目录）
  - `./RUN_EVAL.sh --design-flow-agent [ARGS...]` → 真实 LLM agent 多轮工具循环 pass@k 评测
  - `./RUN_EVAL.sh --design-flow [ARGS...]` → design_flow 交付件判分
- 批量驱动：`scripts/run_design_flow_batch.py`（`--session-backend http://...` / `--num-samples k` / `--resume`）
- 配置：`config.yaml`（benchmark_file / sandbox url / system_prompt_templates / workers / quota）
- 沙盒后端：`eda_fastmcp_flow` 的 `run_commands`/`run_code`（.75），或 config.yaml 里 `sandbox.url`（`http://10.129.32.75:8669/v1/run_code`）
- 接口协议文档：`docs/design_flow_session_backend.md`（§3 接口规格 / §9 判分两步：交付件存在性 + test 校验器 / `reference_deliverable` / `candidate_exec: shell`）
- 用例编写指南：`docs/设计流Benchmark-测试用例编写指南.html`
- 框架设计文档：`docs/设计流Benchmark-框架改进设计文档.html`

**已有用例格式（`benchmarks/EDA-Eval-DesignFlow/`，照此 schema 新建 jsonl）**
- 现有：`EDA-Eval-DesignFlow-001.jsonl`（1 行）、`EDA-Eval-DesignFlow-RTL-Digital.jsonl`（4 行）、`assets/`（每题一个目录，含 spec/tb/run 脚本）、`reference/`（参考交付件）
- 每行一个 JSON 对象，字段：
  - `task_id`（如 `EDA-Eval-DesignFlow-Digital-001`）
  - `prompt`（给被测 agent 的任务描述，含场景/要求/签名）
  - `entry_point`（被测要实现的 proc/func 名）
  - `test`（校验器：`proc check {candidate} {...}` 或 `def check(candidate): ...`，含 setup + assert）
  - `metadata`（task_name/direction/scenario/layer/topic/difficulty/design/tcr_refs/heavy/wall_time_sec）
  - `mode`: `"design_flow"`
  - `runtime`: `{"lang": "tcl"|"pyAether"|"skill", "host": "innovus"|"aether"|"virtuoso"|"waveview"}`
  - `attachments`: `[]` 或引用 assets/ 下文件
  - `budget`: `{"max_turns": 40, "wall_time_sec": 1800}`
- 用例来源：基于增补 II 的 `summary.tsv`（24085 命中会话）按 EDA 工具/类别分桶，把真实用户场景提炼成 task。新 jsonl 命名建议：`EDA-Eval-DesignFlow-<类别>-<编号>.jsonl`（如 `EDA-Eval-DesignFlow-Virtuoso-Layout.jsonl`）。

#### 三条任务

**任务 1：评测用例落盘 + 每次睡去前提交**
- 用例保存目录：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/`（已存在，已有 jsonl + assets + reference）
- 可新建 jsonl（按上述 schema），也可往现有 jsonl 追加行；assets/ 下按题放参考文件。
- **每次睡去前**（收尾铁律第 3 步）必须 `git add -- benchmarks/EDA-Eval-DesignFlow/` 并提交推送。不要等"凑够一批"才提交，每轮有新增就提交。
- 用例数据来源 = 增补 II 的 .75 上 `summary.tsv`（24085 命中）经 eda_flow 拉取 + 脱敏 + 提炼。**原始 session 内容不入 git**，只入提炼后的 prompt/test/metadata。

**任务 2：用 pi agent 作被测调试用例**
- 每新建/修改一条用例，**用 `pi` 实际跑一遍**验证可执行、test 能正确判 PASS/FAIL。
- pi 已配 eda_flow MCP，能 open_session → run_commands/run_code（在 .75 EDA 沙盒）→ declare_done → close_session。
- 调试方式（自行判断，示例）：
  - 把用例 prompt 喂给 pi：`pi --no-approve -m deepseek-v4-pro-cloud "$(jq -r .prompt <用例jsonl>)"`，观察 pi 能否调 eda_flow 完成。
  - 或用框架：`./RUN_EVAL.sh --design-flow-agent` 配合新 jsonl（改 config.yaml 的 benchmark_file 指向新 jsonl）。
  - 用例 test 要能在 .75 沙盒跑（runtime.host 对应 innovus/aether/virtuoso/waveview）。
- pi 是被测：让它自己探索/写代码/调工具，**编排 agent（你）只负责建用例 + 跑框架 + 看结果 + 修用例**，不替 pi 写实现。
- 调试失败（pi 跑不通 / test 永远 FAIL）→ 记原文到 MEMORY，标该用例 `status: draft`，继续下一条，不卡死。

**任务 3：每天下午 4 点生成中文 HTML 日报**
- 路径：`/nasdata/app.e0031982/code/EDA-Flow-Bench/docs/reports/`（**不存在则 `mkdir -p` 创建**）
- 文件名：`report_benchmark_<MM>_<DD>.html`（如 `report_benchmark_10_29.html`，月份/日补零两位）
- 内容（中文）：当日新增用例数 + 累计用例数 + 用例分类分布 + pi 调试结果（PASS/FAIL/draft 统计）+ 三口径数字（698机/2850用户/24085命中）+ 当日流水摘要 + 阻塞/下一步
- 触发：每天 **16:00**（本机时间）。loop 自适应睡眠唤醒时检查"当前时间 ≥ 16:00 且今天还没生成 report_benchmark_MM_DD.html"→ 生成；或用 `at`/cron（若可用）。优先用 loop 内判断，不依赖 cron。
- 生成后按收尾铁律 `git add -- docs/reports/` 提交推送。
- HTML 要纯静态（CSS 内联，不引外链），可在浏览器直接打开。

#### 优先级与节奏
- 三条任务并行推进，不要串行死等。
- 任务 1（建用例）是主轴；任务 2（pi 调试）随建随调；任务 3（日报）每天 16:00 一次。
- 仍遵守增补 II：禁本机自扫、禁 lineage 自审计/§X 递归；用例数据来自 .75 已有扫描结果。
- 若 pi 不可用（`pi --version` 失败）或 eda_flow MCP 断：记原文 + `WAITING=1`，不回退到本机自扫。

### 🆕 2026-10-29 运维增补 IV：698 机免密 SSH 已打通，可抓真实 session 内容 · 最高优先

> **运维令**：「e0031982 的公钥已部署到 698 台机（697 成功 + 1 失败），从 .75 经 `eda_flow.run_commands` 免密 ssh 到内网任意一台已通。不要再靠 keyword 分布合成用例——直接 ssh 到 698 机抓真实 session 内容建用例。」

**已验证能力（运维 2026-10-29 实测）**
- ✅ `.75`（`hfhds201`，`e0031982` 身份）→ 免密 ssh 到内网 698 台机，**BatchMode 免密直接通**。
  实测：`ssh -o BatchMode=yes 10.129.32.189 'hostname'` → `hfeg0pnd001`；`ssh hfeg0plg49 'hostname'` → `hfeg0plg49`。
- ✅ 697/698 成功（1 台失败，可忽略，不影响 benchmark）。
- ✅ 抓真实 session 内容跑通：`ssh hfeg0plg49 'ls /home/*/.cline/data/sessions/*.messages.json | wc -l'` → 有数据。

**怎么用（替代增补 III 里的"合成用例"fallback）**
1. `open_session(task_id="BENCH-MINE", eval_id="<日期>", user="bench_mine", sample="0")` → 拿 workdir。
2. `run_commands(workdir, commands=[...])` 里用 **ssh 免密**抓真实 session：
   ```bash
   # 从 summary.tsv 取一批命中会话的 (ip, user, session_file)
   # 然后对每条 ssh 过去抓内容（只读，限量 head -c 避免撑爆输出）：
   ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no <ip> \
     "head -c 4000 /home/<user>/.cline/data/sessions/<session_file>"
   ```
   - `summary.tsv` 每行有 `ip\thost\tuser\tsession_file\tmatch_count\tkeywords\ttools`
   - `session_file` 是文件名（如 `1792637822804_6xv88.messages.json`），实际路径 `<ip>:/home/<user>/.cline/data/sessions/<session_file>`
   - **分批抓**：一次 run_commands 里 ssh 5-10 台够了（每台 head -c 4000），别一次扫 698 台会超时
   - 优先抓**热点机 + 高 match_count 会话**（hfeg0plg49/hfeg0pkn003/hfeg0plg17/…，summary.tsv 按 match_count 排序）
   - 🚫 **只读**：不 `>`/`tee`/`rm` 任何东西到目标机（红线）
3. `close_session(workdir)` 清理。
4. 从真实 session 内容提炼 prompt/test → 落 `benchmarks/EDA-Eval-DesignFlow/` 新 jsonl（按增补 III schema）。
5. **脱敏**：session 里的真实用户名/路径/IP/key 入库前脱敏（user→hash, ip→hash, 路径里的人名→占位）。
6. 用 pi 调试用例（增补 III 任务 2）。

**SSH 命令模板（直接抄）**
```bash
# 抓单台单会话内容（head -c 限量）
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no <IP> \
  "head -c 4000 /home/<USER>/.cline/data/sessions/<SESSION_FILE>"
# 列某机所有 cline 用户的 sessions
ssh -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no <IP> \
  "ls -la /home/*/.cline/data/sessions/*.messages.json 2>/dev/null | head -20"
# 抓某会话的 first user prompt（python 解析 messages.json）
ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no <IP> \
  "python3 -c \"import json; d=json.load(open('/home/<USER>/.cline/data/sessions/<F>')); ms=d.get('messages',d) if isinstance(d,dict) else d; [print('['+str(m.get('role','?'))+']',(b.get('text','') if isinstance(b,dict) else str(b))[:500]) for m in (ms if isinstance(ms,list) else [])[:6] for b in (m.get('content') if isinstance(m.get('content'),list) else [m.get('content') or '']) if (b.get('text','') if isinstance(b,dict) else str(b)).strip()]\""
```

**优先级**
- 这条**覆盖增补 III 里"远程不可达→合成用例"的 fallback**。现在能抓真实内容，就抓真实的，不合成。
- 仍遵守：禁本机自扫、禁 lineage 自审计/§X 递归。
- 若某台 ssh 偶发失败（网络瞬断）：跳过该台，记原文，继续下一台，不 `WAITING`。
- 若 ssh 大规模失败（>50% 不通）：记原文 + `WAITING=1`，可能是网络问题，等下轮重试。

### 🆕 2026-10-30 运维即时令 VII：纠正方向——按 docs 文档写"设计流编排评测 Case" + 改日报表格 · 最高优先（覆盖 VI）

> **运维令**：「方向歪了。当前写的全是"脚本生成评测 Case"（让 agent 实现一个 proc 返回 dict），不是"设计流编排评测 Case"。立即认真读 `docs/` 里的 4 份文档，按文档契约重写用例。下次日报表格也要改：每行一个 Case，呈现 trace 来源/要解决的问题/任务说明/交付件要求/test 思路/test 语言。」

**一、先读文档（本轮第一件事，不许跳过）**

逐字读这 4 份文档，理解"设计流 case"的正确契约：
1. `docs/设计流Benchmark-测试用例编写指南.html` ← **用例编写规范**，必读
2. `docs/rtl_design_flow_case_design.md` ← **真实 trace→case 的完整范例**（4 道已验证 case），必读
3. `docs/design_flow_session_backend.md` ← 框架如何执行 case + 判分通路
4. `docs/设计流Benchmark-框架改进设计文档.html` ← 框架整体设计

读完在 MEMORY 记一行"已读 docs 4 文档，理解设计流 case 契约"。

**二、当前用例的根本错误（对照文档自查）**

当前 67 条用例**几乎全部**是 scripting 口径（函数实现题），不是设计流口径。3 个根本错误：

| 字段 | 当前（错） | 文档要求（对） | 出处 |
|---|---|---|---|
| `entry_point` | 函数名（如 `logicsynth_build_lint_scaffold`） | **交付件路径**（如 `outputs/submit.zip`） | 指南 §4.4/§5 |
| `test` 签名 | `check(candidate)` 单参，校验函数返回值 | `check(deliverable, workdir)` 双参，校验**交付件** | 指南 §2.1/§7 |
| `prompt` | "实现 `xxx(args) -> dict`"（含函数签名） | 自然语言**任务目标**（无函数体/签名） | 指南 §4.3 |
| `lang`/`host` | 带 `runtime:{lang,host}` | **抛弃**（设计流不限定单一语言，agent 混用 SKILL/Tcl/shell） | 指南 §4.6 |
| `mode` | 部分缺失 | 必须 `"design_flow"` | 指南 §4.2 |
| `attachments` | 多数无 | 真实 case 需注入输入文件（网表/库/TB 模板） | 指南 §6 |

**正确的设计流 case 契约（一句话）**：
> 你写 `prompt`（任务目标）+ `attachments`（输入文件）+ `entry_point`（交付件路径，如 `outputs/submit.zip`）+ `test`（`check(deliverable, workdir)` 校验交付件）。框架负责开 session、把附件放进 workdir、让 agent 多步工作、收交付件、跑校验器、判分。**agent 在一个 session 里多步驱动 flow（画图/仿真/跑工具/看报告）→ 产出交付件**，不是写一个函数。

**正确范例**（见 `docs/rtl_design_flow_case_design.md` §3 + `docs/example/`）：
- `EDA-Eval-DesignFlow-Digital-010`：prompt=按 spec 实现 RTL + 跑 VCS 仿真，entry_point=`outputs/submit.zip`(5 文件)，test=`check(deliverable, workdir)` Python，校验 zip 内含 `mac4.v`/`sim_mac4.log` 且 log 含 `MAC4_SIM_PASS`
- `EDA-Eval-DesignFlow-Analog-001`（docs/example/）：prompt=建 CMOS 反相器原理图 + 仿真，entry_point=`outputs/submit.zip`(5 文件)，test=SKILL `check(deliverable, workdir)`，校验 zip 内含 5 文件 + 拓扑 + 波形反相
- 这些 case 里 agent 要**多步工作**（建图→仿真→看报告→打包），不是写一个 proc

**三、整改要求**

1. **现有 67 条用例**：标记为 `status: legacy_scripting`（不删，保留作 scripting 口径存量），**不再往这个口径追加**。
2. **新建用例**必须严格按设计流契约：
   - `mode: "design_flow"`
   - `entry_point`: 交付件路径（`outputs/submit.zip`）
   - `test`: `check(deliverable, workdir)` 双参，校验交付件（解 zip + 断言内含文件 + 内容达标）
   - `prompt`: 自然语言任务目标，**无函数签名**，描述要完成什么设计流 + 交付什么 + 约束
   - `attachments`: 注入真实输入文件（从 698 机 SSH 抓的真实数据，脱敏后入 assets/）
   - **不带** `lang`/`host`/`runtime` 字段
   - `metadata.domain`: digital/analog/verification/test
   - `budget`: `{max_turns, wall_time_sec, max_tool_calls}`
3. **用例来源**：基于真实 trace（增补 IV 的 SSH 抓取能力），从真实 session 里提炼"用户完成的一个设计流任务"→ 写成 case。参考 `rtl_design_flow_case_design.md` 的做法：trace 提取清单 → 主题聚类 → 选可判分主题 → 固化 case。
4. **test 语言**：Python（`def check(deliverable, workdir)`）或 SKILL（`procedure(check(deliverable workdir) ...)`) 或 Tcl（`proc check {deliverable workdir} {...}`），按 case 的 EDA 域选。Python 交付件题可全本地自测（session_backend §6.B）。

**四、日报表格改进（下次日报立即生效）**

改 `gen_daily_report.py`，用例盘点表格改为**每行一个 Case**，列：

| 列 | 内容 |
|---|---|
| task_id | 用例 ID |
| trace 来源 | 基于哪个用户/什么时间的 trace 构建（如 `t0002948/1789900011859_zpx23`，无则标 `synthesized`） |
| 解决问题 | 这个 trace 里用户要解决什么问题（一句话） |
| 任务说明(prompt) | 如何构建任务说明（一句话摘要：给 agent 什么目标） |
| 交付件要求 | entry_point + 期望产物清单（如 `outputs/submit.zip` 内含 mac4.v/sim_mac4.log） |
| test 思路 | 基于什么思路构建校验脚本（如"校验 zip 内含 5 文件 + log 含 PASS 标记 + 真值断言"） |
| test 语言 | Python / SKILL / Tcl |
| pi 结果 | PASS/FAIL/draft/未跑 |

- 旧表格（按文件分布 + KPI 数字）保留在表格上方作汇总，但主表改为上述 per-case 行。
- 表格按 trace 来源分组（有真实 trace 的在上，synthesized 在下）。

**五、执行优先级**
1. 先读文档（本轮第一件事）
2. 改 `gen_daily_report.py` 表格格式（本轮内完成，立即刷一次今日日报）
3. 开始按设计流契约建新用例（从真实 trace 提炼，第一目标是产 1 条合格的设计流 case 而非 10 条 scripting 题）
4. 现有 67 条 legacy_scripting 不删不补，标记即可

**六、体积维护**
本指令写入后任务书又大了。执行完"读文档+改日报"后，按收尾铁律把已完成的即时令 V、VI 归档到 ARCHIVE（留 1 行指针）。

### 🆕 2026-10-30 运维即时令 VIII：清理错误 jsonl + 合并为单一 jsonl · 最高优先

> **运维令**：「你建的 15 个 jsonl 太散了，而且都是错误口径（scripting 不是 design_flow）。自己清理：(1) 把所有错误 jsonl 合并成一个，标记 legacy；(2) 以后新建用例只往这一个 jsonl 追加，不要再创建新文件。」

**一、现状问题**
- `benchmarks/EDA-Eval-DesignFlow/` 下有 **15 个 jsonl**（Aether-Layout/Analog/EdaOther/Innovus-*/LogicSynth/PV/PnR/RTL-Digital/Sch/Skipper/Spice/Virtuoso/WaveView/001），按 EDA 工具类别分文件——**这是错的**。
- 框架和文档约定的是**一个 benchmark 集合用一个 jsonl**（参考 `docs/rtl_design_flow_case_design.md` §5：`EDA-Eval-DesignFlow-RTL-Digital.jsonl` 一个文件含 4 道数字方向 case）。
- 按工具分文件是 agent 自创的坏习惯，给框架加载/统计/分类都添麻烦。

**二、清理要求（本轮内完成）**

1. **合并为一个 jsonl**：把现有 15 个 jsonl 的所有行合并到**一个文件**：
   - 目标文件名：`benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl`（单一集合文件）
   - 合并时给每行加一个字段 `"legacy": true` 标记这是旧的 scripting 口径用例（即时令 VII 已要求标记 `status: legacy_scripting`，这里用 `legacy: true` 即可）
   - 合并后逐行校验是合法 JSON（`python3 -c "import json; [json.loads(l) for l in open('...jsonl')]"`）
   - 合并后保留原 15 个文件的 git 历史，但 `git rm` 删除它们（让仓库只留一个 jsonl）
   - `assets/` 和 `reference/` 目录**不动**（里面是真资产，按 task_id 子目录组织，与 jsonl 文件数无关）

2. **合并后核对**：
   - 行数 = 原 15 文件行数之和（当前 67 条）
   - 每行有 `task_id` 且全局唯一
   - `python3 -c "import json; lines=[json.loads(l) for l in open('...jsonl')]; print(len(lines), 'rows,', len(set(d['task_id'] for d in lines)), 'unique ids')"` 输出 67 rows, 67 unique ids

3. **git 操作**：
   ```bash
   cd /nasdata/app.e0031982/code/EDA-Flow-Bench
   # 先合并到新文件
   cat benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-*.jsonl > benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl
   # 校验合法 + 去重
   # 删除旧 15 文件
   git rm benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-001.jsonl \
           benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-Aether-Layout.jsonl \
           ... (所有旧 jsonl)
   git add -- benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow.jsonl
   git commit -m "运维即时令VIII: 合并15个jsonl为单一EDA-Eval-DesignFlow.jsonl(67条legacy标记); 以后只往这一文件追加"
   git push origin master
   ```
   （实际合并时注意：`cat` 拼接可能产生空行，用 python 合并更稳：`python3 -c "import json,glob; w=open('out.jsonl','w'); [w.write(json.dumps(json.loads(l),ensure_ascii=False)+'\n') for f in sorted(glob.glob('benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow-*.jsonl')) for l in open(f) if l.strip()]"`，合并前给每行加 `legacy:true`）

4. **更新 `gen_daily_report.py`**：读用例的 glob 从 `benchmarks/EDA-Eval-DesignFlow/*.jsonl` 改为只读 `EDA-Eval-DesignFlow.jsonl`（或保持 glob 但适配单文件）。

**三、以后规则（硬性，永久）**

- **新建用例只往 `EDA-Eval-DesignFlow.jsonl` 追加**，不再按工具/类别建新文件。
- 用例的类别归属放 `metadata.domain`（digital/analog/verification/test）或 `metadata.task_name`，不靠文件名分类。
- 若日后用例数大到单文件难管理（如 >500 条），再按 `metadata.domain` 拆 4 个文件（digital/analog/verification/test），**不按 EDA 工具拆**。

**四、执行顺序**
1. 读文档（即时令 VII 要求，若还没读先读）
2. 合并 jsonl + 删旧文件（本指令）
3. 改日报表格（即时令 VII 要求）
4. 开始按设计流契约建新用例（追加到合并后的单一 jsonl）

### 🆕 2026-10-30 运维即时令 IX：深入读真实 trace 完整对话流，不要止步于汇总 · 最高优先

> **运维令**：「你之前确实 SSH 读了真实 messages.json（commit message 里有 "scp'd 1MB .messages.json"、"mined xxx/yyy" 的记录），这点做对了。但你把真实 trace 浪费了——68 条用例里 67 条 prompt 是通用的，真实用户名/路径/对话上下文全没进用例。从现在起，每条用例必须从一条真实 trace 的**完整对话流**提炼，prompt 要反映真实场景，test 要校验真实交付件。不要再造抽象题。」

**一、当前问题（查证结果）**

- ✅ agent 确实 SSH 到 698 机读了真实 messages.json（commit `6e226e0` 记录 "scp'd 1MB .messages.json to .75 workdir, parsed"）
- ❌ 但 68 条用例里 **67 条 prompt 是通用的**（不含真实用户名/路径/对话细节），真实 trace 只记在 commit message 里，没进用例
- ❌ 真实 session 里用户是**多步驱动 flow**（读报告→诊断→改脚本→重跑→看结果）→ agent 却压成"实现 `xxx(args)->dict`"的单步函数题
- ❌ 这等于把"原生的馒头"（真实 trace）嚼完了又吐成"嚼过的馒头"（抽象题），浪费了 SSH 能力

**二、什么是"深入读真实 trace"**

不止于 summary.tsv 的 keywords/tools 元数据，不止于 head -c 4000 看个开头。要：

1. **SSH 到目标机，读完整 messages.json**（不是 head -c 4000）：
   ```bash
   # scp 完整文件到 .75 workdir 再解析（agent 之前 6e226e0 commit 这样做过，继续这样做）
   ssh -o BatchMode=yes -o ConnectTimeout=10 <IP> "cat /home/<USER>/.cline/data/sessions/<SESSION_FILE>" > /workdir/trace.json
   # 或 scp
   scp <IP>:/home/<USER>/.cline/data/sessions/<SESSION_FILE> /workdir/trace.json
   ```
2. **解析完整对话流**（用 python 解析 messages.json）：
   - 提取所有 user message（用户的真实需求/指令/反馈）
   - 提取所有 assistant message（agent 的分析/代码/工具调用）
   - 提取所有 tool_result（EDA 工具的真实输出/报告/报错）
   - 理解用户的**完整工作过程**：用户给了什么目标 → agent 做了什么 → 遇到什么问题 → 怎么解决 → 最终交付什么
3. **从完整对话流提炼 case**（不是从 keywords 猜）：
   - prompt = 真实用户的第一条需求（改写脱敏，但保留真实场景细节：设计什么电路/用什么工具/什么指标/什么约束）
   - attachments = 真实 session 里的输入文件（RTL/网表/TB/报告，脱敏后入 assets/）
   - entry_point = 真实 session 里用户最终交付的产物（zip 包）
   - test = 校验交付件是否达到真实 session 里的验收标准

**三、具体要求**

1. **每条新用例必须记录 trace 来源**（metadata 里加字段）：
   ```json
   "metadata": {
     "trace_source": {
       "host": "hfeg0plg49",
       "user_hash": "sha1[:12] of real username",
       "session_file": "1792719811850_q5ogm",
       "session_msgs": 337,
       "real_task_summary": "DC NXT WLM 综合 0% multi-bit banking 诊断"
     }
   }
   ```
   脱敏：user → hash，但 host/session_file 可保留（用于溯源）。

2. **prompt 要反映真实场景**（不是通用抽象）：
   - ❌ 错："实现 `logicsynth_build_lint_scaffold(rtl, mod) -> dict`"
   - ✅ 对："这是 cfreq_ctrl.v（VCO 自动校准 RTL），请在 .75 沙盒里用 SpyGlass 跑 lint 检查，修复所有 Error 级违规，产出 lint 报告 + 修复后的 RTL，打包成 outputs/submit.zip。约束：不改模块接口，只改 RTL 内部逻辑消除 lint 违规。"
   - prompt 里可以有真实文件名/电路名/工具名/指标，但要脱敏真实用户名/路径

3. **test 要校验真实交付件**（不是函数返回值）：
   - `check(deliverable, workdir)` 双参
   - 解 zip 包，校验内含文件 + 内容达标（报告无 Error / RTL 编译通过 / 时序达标等）
   - 参考 `docs/rtl_design_flow_case_design.md` §3 的 4 道已验证 case 的 test 写法

4. **工作量预期**：深读一条真实 trace（scp + 解析 + 理解 + 提炼 case）可能要 1-2 轮。宁可 1 轮出 1 条真实 case，不要 1 轮出 5 条抽象题。

**四、优先选哪些 trace**

从 summary.tsv 里选**高 match_count + 多 message**的 session（真实工作量大，case 有区分度）：
- 热点机：hfeg0plg49(2409命中) / hfeg0pkn003(825) / hfeg0plg17(730) / hfeg0pkn001(710)
- 优先选**多轮工具调用**的 session（用户调了 5+ 次 EDA 工具才完成的任务），不是单步任务
- 优先选**有真实报错+修复过程**的 session（这种 case 天然有区分度——agent 要能复现修复过程）

**五、执行**
- 本指令不要求本轮就出 case——先深读 1 条真实 trace，理解完整对话流，下一轮提炼成 case
- 在 MEMORY 记录"本轮深读了 xxx/yyy trace，共 N 条 message，用户目标是 ..., agent 做了 ..., 最终交付 ..."
- 后续每条新 case 都按本指令要求，从真实 trace 完整对话流提炼

### 🧭 收尾铁律（每轮唤醒必做，不许省）

结束前按顺序做完，再置 `WAITING`：

0. **体积自检**：`BAIZE_DESIGNFLOW_BENCH_TASK.md` 与 `MEMORY_DESIGNFLOW.md` 都 **≤32KB**；
   **>40KB 红线 ⇒ 先归档再提交**。数字抄进心跳：
   `📦 体积：TASK=nKB / MEMORY=nKB（归档 nKB → ARCHIVE_OPERATOR_DESIGNFLOW.md）`
1. **写心跳** `MEMORY_DESIGNFLOW.md`：更新顶部快照
   （`PHASE/WAITING/已完成/当前动作/下一步/阻塞`），追加 1 行流水
   `[HH:MM] 干了什么 + 关键原始输出 1–2 行`（含三个口径数字）。
2. **写日报** `daily-memories-designflow/<YYYY-MM-DD>.md`（当天必建）。
3. **提交+推送**（不许等 loop 兜底）· **双仓库**：
   ```bash
   # (A) workspace 仓库：super_intelligence_2035 (main 分支) — 含 workspace + 日报
   cd /nasdata/app.e0031982/code/super_intelligence_2035
   git fetch origin && git pull --rebase --autostash origin main
   git add -- doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW.md \
              doc/ZhuLong_DAC2027/benchmark/EXPERIMENTS_DESIGNFLOW.md \
              doc/ZhuLong_DAC2027/benchmark/BAIZE_DESIGNFLOW_BENCH_TASK.md \
              doc/ZhuLong_DAC2027/benchmark/ARCHIVE_OPERATOR_DESIGNFLOW.md \
              doc/ZhuLong_DAC2027/benchmark/designflow \
              doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow \
              doc/ZhuLong_DAC2027/reports
   git commit -m "designflow #<轮次>: <一句话>"
   git push origin main

   # (B) 用例仓库：EDA-Flow-Bench (master 分支) — 仅用例产物
   cd /nasdata/app.e0031982/code/EDA-Flow-Bench
   git fetch origin && git pull --rebase --autostash origin master
   git add -- benchmarks/EDA-Eval-DesignFlow
   git commit -m "designflow #<轮次>: <一句话>"
   git push origin master
   ```
   🚫 绝不用 `git add -A`（两个仓库都是共享工作副本）。
   ⚠️ 分支别搞混：workspace+日报→main，用例→master。
4. **闭环自检**：`git status -sb` 无 ahead/behind；`git log -1` 时间戳 = 本轮。
   push 失败重试 1 次，仍失败把报错原文写进心跳，下轮第一件事补推。

> ⏱️ 心跳 **>60 min 无新提交 ⇒ 按卡死处理**。

### 📉 体积维护规程（硬性）
> 两文件 ≤32KB，红线 40KB；已闭合内容**原文**搬入
> `ARCHIVE_OPERATOR_DESIGNFLOW.md`（留 1 行指针）；搬前 `git pull --rebase --autostash`；
> 只搬最新活跃块之下的已闭合块；🚫 不改小节编号/标题/运维指令。

---

## 现行部分（Design-Flow Benchmark）

**目标**：用 `.75` 内网真实 cline 用户轨迹（约 500 用户、持续增长），构建真实场景设计流 Benchmark。

**输入**：`eda_flow` MCP（`127.0.0.1:18891`，已注册到 opencode）→ `.75`（`hfhds201`，`10.129.32.75:8670`）→ `run_commands` 只读扫 `/home/*/.cline/data/sessions/`。详见上方「2026-10-29 运维增补」。

**交付物**
1. 资产盘点报告（目标机/用户/轨迹三个数字）。
2. `bench_v0.1/`：脱敏任务集 + 评分器 + 复现脚本。
3. HTML 交付报告（规模、分类、评分、局限）。
4. `MEMORY_DESIGNFLOW.md` / `EXPERIMENTS_DESIGNFLOW.md` / 日报。

**验收标准**：见上方「验收」4 条；红线与纪律同上。

**待确认项**（首轮先探明并写入 MEMORY，未确认前按默认走）
- ~~8092 MCP 协议~~ → 已确认是 research MCP，作废（见运维增补）
- sessions 文件格式（.75 上是否同本机 `*.messages.json`？首轮探明）
- ~~SSH 账号是否免密只读~~ → 作废，走 eda_flow MCP
- 是否允许主动扫描（默认否，只 `find`/`ls`/`cat` 被动发现）
- Benchmark 是否对外（默认先内部）

**失败处理**：连通/权限/解析失败 → 记原文 + 留中间产物 + `WAITING=1` 轮询；
样本 <100 任务 → 先交付 v0.1 小集，标注"持续扩增"，不阻塞。

---

> ⚠️ 本文件为只读指令文件，agent 禁止修改。运行时状态写入 `MEMORY_DESIGNFLOW.md`、
> `EXPERIMENTS_DESIGNFLOW.md`、`daily-memories-designflow/`。
