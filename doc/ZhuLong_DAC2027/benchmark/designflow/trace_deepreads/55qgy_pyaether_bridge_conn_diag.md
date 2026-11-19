# Deepread — 55qgy (jzeng @ hfeg0plg85, mc=97, physical_verify) — pyAether Bridge 连接失败诊断

- session: `1794357795851_55qgy.messages.json` · user: jzeng · host: hfeg0plg85 (10.129.8.136 / 也可经 172.16.8.162/hfeg0plg17) · mc=97
- scan: ssh_eda_search_20261119_172105/summary.tsv (kw: aether:1401; drc:493; schematic:492; netlist:396; pyaether:287; virtuoso:85; waveview:66; cellview:35)
- trace: 60 msgs / 37 user turns / 34 tool_uses · model deepseek-v4-flash · cwd /ai_sandbox/...
- domain: **physical_verify** (pyAether bridge 连接诊断 = env-config/debug-Q&A, 2026-11-15 reaudit 后合法)
- ledger: r537 旧判 `REJECT (Q&A/sim/run-existing/done)` → r847 revival per 2026-11-15 用户令 (旧 weak 筛子作废, env-config/debug-Q&A 合法) → claimed

## 用户意图流（真实 user_input，逐字）

- **U#1**「桥接连接失败是怎么回事」— 提出问题（bridge 连接失败，问原因）★ A-档需求轮候选
- **U#2**「1.pyAether bridge」— 选项选择（pyAether bridge 类型）
- **U#3 (★ 核心 produce-task seed，A-档合规)** 逐字:
```
连接检测 → 10.129.8.96:21694 · 08:51:04
桥接连接失败
{
  "status": "dead",
  "latency_ms": 7,
  "response": "connect ECONNREFUSED 10.129.8.96:21694"
}
```
→ 用户提供连接检测报告 JSON，要求诊断桥接连接失败根因。

U#1/U#2/U#3 均为「提出需求/表达目标」轮（U#3 给出待诊断的连接报告），🚫 用户未指出根因或给出修复方案 → 合 A-档选轮规则。

## assistant 工具链 + gold 产物

工具: ask_question / get_agent_policy_status / list_allowed_files×7 / read_files×6 / skills×2 / search_apis×2 / RAG_MCP_Server__search_apis×3 / get_api_details×2 / run_approved_command×4

**gold 诊断报告**（assistant #16/#18，prose markdown）:

1. **ECONNREFUSED 含义** = 网络可达，但目标端口没有任何进程在监听。延迟 7ms 说明网络没问题，问题在服务端。
2. **根本原因** = pyAether Bridge Server 没有在 10.129.8.96:21694 启动监听。
3. **pyAether 桥接架构**: 客户端(SandBox_MCP_Server/脚本) → TCP connect → 目标服务器 IP:Port (无 listener → ECONNREFUSED)。
4. **端口生成规约**: 端口按 UID 确定性生成 = `20000 + (uid * 10010) % 45533`；连接信息记录在 `ip_port.json`。
5. **WaveView Tcl bridge vs pyAether bridge** 区别: WaveView 需在 GUI 启动 server.tcl 监听 127.0.0.1；pyAether 需在 Aether 启动 Python bridge。
6. **解决方法**: 先在 Aether GUI 启动 bridge 服务 → 再做连接检测；检查 ip_port.json 端口与监听端口一致。

## reframe 决策（档 B）

- **形态**: env-config/debug-Q&A 诊断（看连接报告 JSON 定位桥接失败根因）→ 按任务初衷属合法真实用户意图（2026-11-15 reaudit: env-config/debug-Q&A 全部合法）
- **可便携性**: 高（纯文本/JSON 后处理，不依赖 live pyAether/Aether GUI/真实网络）
- **reframe** = produce 型参数化桥接连接诊断器 `bridge_conn_diag.py <conn_report.json> <bridge_config.json> <network_probe.txt> <listener_check.txt> [-o out.json]`
  - 解析 conn_report (status/latency_ms/response/target_ip/target_port)
  - 解析 response 串抽 error_type (ECONNREFUSED/ETIMEDOUT/EHOSTUNREACH/ENETUNREACH/none)
  - 解析 network_probe (ping packet loss → network_layer reachable/unreachable + latency)
  - 解析 listener_check (ss/netstat grep → service_layer listening/not_listening/unknown)
  - 解析 bridge_config (bridge_type/uid/ip/port)
  - 计算 expected_port = 20000 + (uid*10010)%45533，比 config_port → config_mismatch
  - 分类 root_cause (优先级: network_unreachable > service_not_listening > config_mismatch > unknown)
  - 输出结构化 JSON (16 顶层键 + fixes 列表 + diagnosis_summary)
- **visible A** (faithful to trace, service_not_listening): conn_report_A (ECONNREFUSED, dead, latency 7, 10.129.8.96:21694) + bridge_config_A (pyAether, uid=30122, port=21694, 期望端口=21694 一致) + network_probe_A (reachable, 0% loss, rtt 7ms) + listener_check_A (ss grep 21694 空无监听)
- **hidden B** (network_unreachable + config_mismatch): conn_report_B (ETIMEDOUT, dead, latency null, 10.129.40.190:31055) + bridge_config_B (WaveView, uid=4321, port=31055, 期望端口=62393 不一致→config_mismatch=True) + network_probe_B (unreachable, 100% loss) + listener_check_B (ssh No route to host → unknown)
- cross-input guard: A vs B 在 error_type/network_layer/service_layer/bridge_type/root_cause/config_mismatch/expected_port 全异，防硬编码 A 答案

## trace_source
- user: jzeng · host: hfeg0plg85 · session_file: 1794357795851_55qgy · match_count: 97
- real_task_summary: 用户(jzeng)做 pyAether bridge 连接检测，连接失败(status=dead, ECONNREFUSED @ 10.129.8.96:21694, latency 7ms)，问「桥接连接失败是怎么回事」。assistant 诊断根因为 pyAether Bridge Server 未在目标端口启动监听(ECONNREFUSED=网络可达但无监听)，并解释端口生成规约(20000+(uid*10010)%45533)、ip_port.json 配置、WaveView vs pyAether bridge 区别、启动 bridge 服务修复方法。本 case 改造为通用桥接连接诊断器 bridge_conn_diag.py <conn_report> <bridge_config> <network_probe> <listener_check>，覆盖 error_type 解析/network_layer 分类/service_layer 判定/expected_port 计算/config_mismatch 检测/root_cause 优先级分类/fixes 生成。

## 去重检查
- jzeng 同 user 已有 case: 未查到 jzeng 名下 case (jzeng 非高频 case user)
- pyAether/env-config 诊断类已建: AetherEnvBootstrap-001 (LD_PRELOAD libstdc++/GLIBCXX home-dir bootstrap), AetherLauncherSkill-001 (aether-launcher skill 改 setup.bash), DrcPyEnvDiag-001 (Python initfsencoding/encodings module error), AetherSmashCliPort-001 (CLI port), ConnChkSummaryGen-001 (DRC connectivity check tool report)
- 本案 = **pyAether bridge 网络连接根因诊断** (ECONNREFUSED/ETIMEDOUT/EHOSTUNREACH + network_layer + service_layer + uid-port-formula + config_mismatch) — 与上述正交：env-bootstrap 是 LD_PRELOAD 库缺失，py-env 是 Python 解释器初始化，launcher 是 skill 改 setup.bash，conn-chk 是 DRC 连通性工具报告，本案是 **TCP 桥接连接失败根因诊断**(网络层 vs 服务层 vs 配置层 + UID 端口公式)。C 域 physical_verify env-config/debug-Q&A bridge-connection 诊断 reframe 子型首例。

## 意图审计
**keep** — jzeng 真实意图(诊断 pyAether bridge 连接失败根因)完全保留，reframe 把「看连接报告→分析 ECONNREFUSED→给根因+修复」抽离成纯 stdlib 诊断脚本是 grounding 非加难(prose 诊断报告无 ≥8 硬断言牙，脚本化 JSON 输出可逐项断言)。2026-11-15 reaudit 后 env-config/debug-Q&A 合法第 N 例。
