# 深读笔记 — btze4 (xiwang@hfeg0pkn002, mc=65) — DDGOA vs DDCPC EccTop 电路对比

## 会话元信息
- session_file: `1794039608709_btze4.messages.json`（dir-based: `1794039608709_btze4/`）
- user: xiwang, host: hfeg0pkn002, match_count: 65 (schematic:744 netlist:58 hspice:4 cellview...)
- msgs: 120 (user 65 / assistant 55)，单用户轮（一个真实需求）
- cron 11-08 log fresh 候选（不在 11-05 summary.tsv，未入任何 shard 台账）
- 状态：trace 末态用户接受 agent 产出的对比报告 `DDGOA_vs_DDCPC_EccTop_compare.md`

## 用户原话（U#0，逐字）
> 帮我对比一下DDGOA和DDCPC在EccTop这个电路的差异

## agent 工具链（关键路径）
1. `get_agent_policy_status` / `read_files` / `search_codebase` — 探工作区上下文（find_ecc_dsa.py 等）
2. `list_allowed_files` — 探 `/ai_sandbox/ddgoa/V0` → 发现只有 agentdir
3. `run_approved_command` (shell-runner) — `ls /proj/` → 找到 `/proj/ddgoa` 和 `/proj/ddcpc` 两个工程
4. `list_allowed_files` `/proj/ddcpc/V0/libs` — 确认 DDCPC 库 `ddcpc_*`
5. `SandBox_MCP_Server__run_code` (pyAether) — 探测 pyAether：可用但只配置了 DDGOA 工程，无法打开 DDCPC 库
6. `RAG_MCP_Server__search_apis`/`get_api_details` — 查 `dbSwitchLibDefsPath`（切换库定义）→ 会超时挂起，放弃
7. **关键转折**：OA 原理图是二进制 `schematic/sch.oa`，agent 改用 `strings` 命令提取二进制中的实例/子单元名
8. `run_approved_command` explore10-14.sh — 对 DDGOA 的 `EccTop128x2New`、`EccTop_Scmos`、`EccTop128x1` 和 DDCPC 的 `DVFSCEccTop`/`SCmosEccTop` 各 sch.oa 跑 `strings`，提取子模块组成
9. `editor` — 写对比报告 `DDGOA_vs_DDCPC_EccTop_compare.md`

## 金标准（trace 末态用户接受的结果）
agent 产出的核心结论：
- **DDGOA** — 顶层 ECC 是数字 stdcell 容器：调用链 `BankTopX2_gut_0820` → `EccTop128x2New_DDGOA_plan5_new_Rev28`（I76）；内部 = `EccTop_Scmos`(×1) + `EccTop128x1New`(×2) + `RedCPTop`(冗余) + `RWEccCtrl/RWEccx8/YsaBnkDrv`；SCmos 使能用 `SCmosEnBuf*`(N/P ×500/1000/4000)；电源 `vssz/vccz`
- **DDCPC** — 没有同名顶层，拆两套并行架构：(1) DVFSC 系（双电压/FSC 开关）：`DVFSCEccTop`→`DVFSCSwEccTop/DVFSCSwDrvEccTop`→`DVFSCSwDPHalf/ArrayCtrlX2/DataABusChan/AbusMux/RWABus/UnitSet`+`lvlshftVcc2Vpcsg`；(2) SCmos 系：`SCmosEccTop`→`SCmosDataUnit/Ary/Dbus/OutCtrl/Pad/RWCBtopMid/SCmosSpineRowBufA/SCmosAryBnkRpt`；电源 `vccsc/vpcsg/vdd2h/vdd2l` 双电压 + `lvlshft`；控制集中在 `EccCtrl`
- 最大结构性差异：DDCPC 引入双电压电源开关架构 + 大批电平移位器，DDGOA 用常规数字域 + `vssz/vccz` SCmos 使能缓冲

## 资产可访问性
- `/proj/ddgoa`、`/proj/ddcpc` 在 pkn002 上 xiwang 可读（agent 以 xiwang 身份跑 shell-runner）
- 从 .75（e0031982）经 ssh pkn002 可 scp 到 sch.oa 文件（920KB messages.json 已 scp 验证）
- 但 sch.oa 是二进制 OA 格式，无法直接打包进 benchmark assets 作为可读输入
- → B-grade synthesized：依据 trace 中真实的子模块名/电源标记结构，合成 A/B 两套 sch.oa 二进制 blob（内嵌 `inst:`/`net:` ASCII token，用 `strings` 提取），离线验证候选 Python 脚本 `ecc_top_compare.py` 的结构对比逻辑

## case 设计（EccTopCircuitCompare-001）
- domain: schematic_netlist（ECC 顶层结构对比）
- grade: B synthesized（真实 trace + 合成 sch.oa 资产）
- track: synthesized
- level: L2（候选用 subprocess `strings` 在二进制 sch.oa 上提取 token = 真跑候选 §4.2）
- 12 条独立条件 a-l：见 D.jsonl test_rationale
- A≠B：cell 名（EccTop128x2New vs EccTop256x1New）、子模块名（带 2 后缀）、电源标记（vssz/vccz vs vssz2/vccz2；vccsc vs vccsc2）全不同；反硬编码（条件 l 检查 A 特有名不在 B 报告的解析列表里）
- byte-sync: check_sha256=d54ad937... size=10274
