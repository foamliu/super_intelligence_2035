# deepread — 1789711703059_os004 (e0039602@hfeg0plg95, mc25, analog_context)

**revival-from-parked (r933)**：r666 (2026-11-14) 以「Q&A/teaching walkthrough of finesim-fsdb-reader skill, no produce-task deliverable」parked。2026-11-15 候选重审令将 Q&A / teaching / explain / walkthrough 全部恢复为可造。承 r928/r929/r930/r932 「manual-grounded howto produce reframe」范式可造。

## trace 概览

- 用户 e0039602 在 hfeg0plg95 上有自建 skill `finesim-fsdb-reader`（目录 `/home/e0039602/Documents/finesim-fsdb-reader/`，含 `SKILL.md` + `fsdb_reader.py` ~470 行）。
- 98 msgs，6 个用户轮，会话总长 ~1.5 小时（ts 1789711704 → 1789887995）。
- domain 复核：keywords 含 `waveview|netlist|analog|schematic` 命中（mc25 是 keywords 中 D-正向词的累计计数），fsdb 波形分析属 D 域（waveform/analog_context 边界）。

## 用户轮原文（A 档合规判定）

| 轮 | ts | 原文 | A档合规 |
|----|----|------|---------|
| U#0 | 1789711704167 | 请你阅读这个目录当中的skill，给我解释他的功能以及实现原理 | ✅ 提出需求✓ 未给根因/修复✗ → **选用** |
| U#10 | 1789714160720 | 所以这个本质上就是个脚本？？AI并没有在其中发挥太大作用 | ✗ 评价/追问，非新需求 |
| U#12 | 1789714542983 | 我是小白，请你用大白话给我逐行仔细解释这个项目的代码 | ✗ 复述请求（细化版） |
| U#18 | 1789716993287 | 我理解一下，所以是通过官方的工具，给定要读取的接口引脚的名称…最后会输出一个什么结果 | ✗ 复述理解 + 追问输出格式 |
| U#20 | 1789885503624 | 所以我如果想让你运行这个skill，应该给你提供哪些信息后你可以去运行呢 | ✗ 运行前置条件追问 |
| U#38 | 1789886606756 | 帮我分析…test.fsdb当中…bl47_dq0在6.06us-6.16us之间的信号 | ✗ 实际运行请求（已在后续轮跑出真实结果） |

**主意图 = U#0**：解释 skill 的功能与实现原理（teaching/explain Q&A）。后续轮是用户在理解过程中的追问/运行请求，验证了 assistant 解释的实操可落地性。

## assistant 工具链（前 8 轮）

- A#1: `list_allowed_files /home/e0039602/Documents/finesim-fsdb-reader depth=3` — 列目录
- A#3: `read_files [SKILL.md, fsdb_reader.py]` — 读 skill 元数据 + 参考实现
- A#5: `read_files fsdb_reader.py L85-400` — 读 run_fscript / parse_table 段
- A#7: `read_files fsdb_reader.py L180-310` — 读 analyze_signal 段
- A#9: **完整解释（5008 字，GOLD）** — 这是 A 档金标准的合成来源
- A#19: 补充输出格式样例（数字/模拟信号报告片段，2568 字）

## GOLD 关键内容（A#9 + A#19 合成 handbook 的依据）

### §1 整体功能
- 名 `finesim-fsdb-reader` v0.1.0 priority=high
- 从 Synopsys FineSim 仿真生成的 `.fsdb` 波形文件读取指定 hierarchy 信号采样值，自动判型（数字/模拟）后分别分析
- 数字：边沿检测（rise/fall）、脉冲检测（start/end/width）、计数
- 模拟：v_min/v_max/v_mean + 时间、过零检测（时刻 + 方向）
- 明确不做：不生成 FSDB、不解析 vec/vecreport、不做 RAS/CAS 协议检查、不做 layout/pyAether

### §2 实现架构 — 4 阶段流水线
1. `run_fscript()` L35-117 — 生成 `.fscr` 脚本调用 Synopsys `fscript`，把 FSDB dump 成文本表格；3 模式（use_bsub True/False/None，None=bsub 失败自动回退直接跑）；超时 1800s，失败透传 stdout/stderr 前 500 字符
2. `parse_table()` L130-191 — 解析 fscript dump 的 `out.tbl`；`parse_time()` 支持 ps/ns/us/ms 后缀转秒，处理首行裸数字；`parse_value()` 支持 m/u/n/p/k/M/G/T 工程后缀；构建 `{signal: [(t,v),...]}`
3. `analyze_signal()` L358-383 — 核心智能
   - `detect_signal_type()` L215-245：swing = v_max-v_min，tol = 5% × swing，f_low/f_high = 靠近极值样本比例；digital if (f_low≥5% AND f_high≥5%) AND swing≥0.25 else analog
   - `detect_edges()` L252：阈值穿越（默认 0.25V），v_prev<thresh≤v_curr → rise
   - `detect_pulses()` L267：状态机式扫描高电平区间
   - `zero_crossings()` L288：相邻采样符号反转 + 线性插值 `t_cross = t_prev + (0-v_prev)*(t_curr-t_prev)/(v_curr-v_prev)`
   - `analog_stats()` L304：v_min/v_max/v_mean + 时间戳、首末值、持续时间
4. `format_report()` L386-427 — 格式化为人类可读文本

### §3 SKILL.md 工程价值 — 8 个已知陷阱
| 陷阱 | 应对 |
|------|------|
| 系统 PATH python3 损坏（3.7.1 库缺失） | 强制 `/usr/bin/python3.11`（WORKING_PYTHON） |
| bsub pincheck 队列满（rc=246, Terminated while pending） | use_bsub=None 自动回退 |
| 大 FSDB（375MB）全量 dump 30~90s | timeout=1800s |
| fscript 首行时间无后缀（`0.0`） | parse_time 回退裸 float |
| 对模拟信号做边沿检测产出伪边沿 | 先 detect_signal_type 判型再分支 |
| 遗漏 v() 包裹导致 signal not found | CLI 自动包裹，模块调用需调用方负责 |
| 临时目录堆积占满磁盘 | 提供 cleanup()，或路径报告给用户 |
| 错误信息被封装丢失根因 | 失败透传 stdout/stderr 前 500 字符 |

### §4 使用方式
- CLI（推荐）：`/usr/bin/python3.11 fsdb_reader.py finesim.fsdb <signal> 0.1n`
- 模块：`from fsdb_reader import run_fscript, parse_table, analyze_signal, format_report, cleanup`

### §5 输出格式（A#19 补充）
- 数字信号报告：Type/Data points/Time range/Total edges/Total pulses/Edge List/Pulse List
- 模拟信号报告：Type/Data points/Time range/Duration/Value min/max/mean + 时间/First-Last/Zero crossings
- INFO 行：`[INFO] FSDB : ...`、`[INFO] Signal: ...`、`[INFO] Step : ...`、`[INFO] Running fscript...`、`[INFO] Temp dir: ...`

## 造题形态决定

- **形态**：manual-grounded howto produce reframe（承 r928/r929/r930/r932 范式）
- **A 档 prompt** = U#0 verbatim「请你阅读这个目录当中的skill，给我解释他的功能以及实现原理」
- **A 手册**：从 A#9 + A#19 GOLD 合成 `finesim_fsdb_reader_skill_explain_A.md`（保留真实结构：§1-§5 + 4 阶段 + 8 陷阱表 + CLI/模块双入口 + 输出格式）
- **B 平行场景**（hidden）：合成 `verdi_fsdb_signal_extractor_skill_explain_B.md` —— 另一个 skill「verdi-fsdb-signal-extractor」用 Synopsys Verdi `fsdbreport` 命令，平行 4 阶段流水线（fsdbreport_dump → tbl_decode → sig_classify → render_summary），平行陷阱表（8 个 B-only 陷阱），平行 CLI + Python API 双入口，平行输出格式（数字/混合信号报告）。B-only token 反硬编码 A-only {finesim-fsdb-reader, fscript, run_fscript, parse_table, analyze_signal, format_report, detect_signal_type, detect_edges, detect_pulses, zero_crossings, analog_stats, fsdb_reader, SKILL.md, .fscr, use_bsub, pincheck, WORKING_PYTHON, /usr/bin/python3.11, 0.25V, 5%, 1800s}
- **candidate_ref.py** = `skill_explain_parser.py` —— 通用 markdown 手册解析器（同 r932 范式），输出 JSON {question, methods, prerequisites, parameters, cited_sections, primary_method, overall}
- **check.py**：12 断言 a-l（同 r932 结构，调整 kind 检测 marker + A-only token + prerequisite 关键词）

## buildable 判定

✅ 真实 trace（trace_source 完整：user e0039602 / host hfeg0plg95 / session 1789711703059_os004 / mc25 / real_task_summary）
✅ A 档合规（U#0 提出需求，未给根因/修复）
✅ GOLD 可合成（A#9 5008 字完整解释 + A#19 输出格式补充）
✅ check() 有牙（B 平行场景 + 反硬编码 + 3 seed idempotence + 3 假提交 FAIL）
✅ 11-15 reaudit §r733 已判可造（Q&A/teaching/walkthrough 恢复为可造）
