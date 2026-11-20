# dyvlr — Virtuoso/SKILL/pyAether 桥接服务状态诊断 + 当前打开 lib 查询

- session: `1793084699921_dyvlr` @ hfeg0plg55 (10.129.35.74)
- user: colinxu · mc=64 · domain: layout_virtuoso (pyaether:90;virtuoso:71;analog:23;cellview:18;schematic:13;...)
- msgs: 38 (单 user_input 轮，U#0)
- ledger 旧状态: D-ledger parked (11-05) 「NOFILE (colinxu wrong host)」——path-bug 时代误判；现文件可读 (79KB messages.json)。
- 2026-11-15 reaudit: env-config / flow-driving + 真实交付物（_check_bridge.py 诊断脚本）合法 ⇒ revival 候选（C 域，跨 D wrong-host parked 已订正，本 r855 via `mark --force`）。

## 真实用户意图（U#0 原文，未脱敏）

> 帮我查看桥接服务是否正常？目前打开的lib是？

两件事：(1) 桥接服务（Virtuoso/SKILL + pyAether 双桥）是否正常；(2) 当前打开的 lib 是什么。
属 env-config / flow-driving（运行时桥接可达性诊断 + 当前会话查询），非"产出一个版图/DRC 报告"——按 11-15 reaudit 是合法 C 域任务。

## 助手 gold 链（msg 1→37）

1. `list_allowed_files`(/home/colinxu/agentdir/train/V0_NCG_HF_Virtuoso) + `get_agent_policy_status` → 工作区是 Virtuoso SKILL 脚本集（add_testpin.il / delete_testpin.il …）。
2. `read_files` + `run_commands`（被 policy 禁用，须 `run_approved_command`）→ 切到 `run_approved_command`。
3. `run_approved_command` (shell-runner, whoami) → `colinxu`；`/proj` 顶层 commonIP/shdc；进程表未见 virtuoso 进程，仅 code-sidecar 守护。
4. 试 `SandBox_MCP_Server__run_code` 两路：
   - lang=skill → **Connection refused** @ `10.129.8.132:21773`
   - lang=pyAether → **Connection refused** @ `10.129.8.132:49109`
5. editor 创建 `_check_bridge.py`，定位桥接配置 `ip_port.json`：
   - 活跃配置: `~/.cline/data/settings/ip_port.json`
     - pyAether: `10.129.8.132:49109`
     - skill: `10.129.8.132:21773`
   - 与 SandBox 拒绝的地址完全一致。
6. `_check_bridge.py` 显式 TCP 探测（socket connect）→ pyAether:49109 **REFUSED (errno 111)**；skill:21773 **REFUSED (errno 111)**。
7. 结论：**桥接服务当前不可用（DOWN），无法查询当前打开的 lib**。
8. editor 创建 `_cleanup.sh`，`run_approved_command` 清理临时脚本，工作区复原。

## 关键事实（金标准 = trace 末尾用户实际接受的结果）

- 活跃桥接配置路径: `/home/colinxu/.cline/data/settings/ip_port.json`
- 两座桥: pyAether(10.129.8.132:49109, kind=pyaether) + skill(10.129.8.132:21773, kind=skill)
- 两座桥 TCP 探测结果: 双 REFUSED (errno 111)
- overall_status: DOWN
- can_query_open_lib: false
- current_lib / current_cell / current_view: null（未能查询）
- recommendation: 桥接服务不可用，无法查询当前打开的 lib

## 档 B reframe（接地，非加难）

A 档 gold = 助手在 live 内网环境对真实 ip_port.json 的 free-text 诊断 prose（依赖 live 桥接 / Virtuoso 进程不可复现，且无 ≥8 独立硬断言牙）→ reframe 为**纯 stdlib 桥接状态诊断器** `virt_bridge_status_diag.py`：

- CLI: `python3 <script> <config.json> [-o out.json]`
- 读 config JSON: `active_config_path` / `probe_timeout_ms` / `bridges[]`({name,ip,port,kind}) / `open_lib_query`({enabled,bridge,query_string,response_pattern})
- 对每座桥做 TCP socket connect 探测 → 分类 status ∈ {UP, REFUSED, TIMEOUT, UNREACHABLE}，记录 errno + latency_ms
- 若 `open_lib_query.enabled` 且目标桥 UP: 连接目标桥，发送 `query_string`，读响应，用 `response_pattern` (regex named groups lib/cell/view) 解析 → current_lib/cell/view
- overall_status: UP (任一桥 UP) else DOWN
- can_query_open_lib: open_lib_query.enabled AND 目标桥 UP
- 输出结构化 JSON（9 顶层键）+ recommendation（DOWN→"不可用/无法"；UP+可查→"正常/可查询 ... lib/cell/view"）

判分用 **隐藏 B** 跑：B 由 check() 在判分时起一个本地 TCP 监听器（响应 `lib=analogLib cell=inv_x4 view=schematic\n`），把监听端口写入 B config 的两座桥（UP），第三座桥指向 127.0.0.1:1（REFUSED）→ overall UP、can_query true、current_lib=analogLib。
visible A 忠实 trace：两座桥均 127.0.0.1:1/2 → 双 REFUSED → overall DOWN、can_query false、current_lib null、recommendation "桥接服务不可用...无法查询..."。A 的 active_config_path 用 trace 真实路径 `/home/colinxu/.cline/data/settings/ip_port.json`。
B 与 A 在 7+ 轴全异（active_config_path / 桥数 2→3 / 桥名集 / 端口 / open_lib_query.enabled false→true / overall_status DOWN→UP / current_lib null→analogLib / recommendation 反义），防硬编 A；同时反硬编 guard 用 A 跑候选并校验 A 输出不含 B 独有 token（analogLib/inv_x4/schematic），防硬编 B。

## 子型定位（C 域 layout_virtuoso reframe 谱系）

本案 = **桥接可达性 TCP 探测 + open-lib 协议查询诊断器**。与既有 C 域 reframe 正交：
- VirtuosoOpenCellQueryGen-001 (r854, 同 user colinxu): SKILL .il 脚本**生成器**（query-spec → .il 代码生成）
- DrcJobExitCwdDiag-001 (r851): LSF 作业退出 CWD 错配 vs license 失败差分诊断
- ConnPathResolve-001 (r852): DRC connectivity sub-stack 路径解析
- 本案: 桥接服务**可达性 + 协议查询**诊断（TCP probe + 桥接协议响应解析），首例 bridge-liveness-diagnosis 子型。

## 意图审计

**keep** —— colinxu 真实意图（查桥接服务是否正常 + 当前打开 lib）完全保留。reframe 是 grounding（把"按需桥接探测+协议查询"沉淀为可复用 parametric 诊断器，单文件化+离线化+真实 TCP 探测），非加难。11-15 reaudit 后 env-config/flow-driving 合法第 N 例。
