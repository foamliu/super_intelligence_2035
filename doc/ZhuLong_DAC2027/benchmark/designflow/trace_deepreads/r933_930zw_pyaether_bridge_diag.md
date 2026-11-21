# Deepread · r933 · 930zw · pyAether bridge protocol diagnosis

- **session**: `1795144070819_930zw.messages.json` (107 msgs, 389KB)
- **user/host**: felixw @ hfeg0plg79 (also synced to hfeg0pfn015/hfeg0pkn004/hfeg0plg06/hfeg0plg46/hfeg0plg54/hfeg0plg72)
- **mc**: 103 · keywords: aether:520;pyaether:301;drc:215;lib.defs:119;calibre:39;cmos:26;.gds:26;cadence:17;gdsii:9;lvs:7;pdk:6
- **timestamp**: 2026-11-19 ~ 2026-11-20 14:47
- **domain**: layout_aether (physical_verify borderline; pyAether bridge connectivity diagnosis)
- **shard**: C

## 真实用户意图

felixw (CXMT DRGQX engineer) 的会话有两个阶段：

### Phase 1 (msg 0-54): Calibre DRC streamout prep
- msg 0: "跑一个 calibre 的 DRC，文件放 `/proj/drgqx/V0/agentdir/felixw/DRC_test`，cell 是 `A_felixw_test/test1`，先 stream out 出一个 gds，aether 平台通过 `asOut` 命令"
- agent 排查环境：`asOut` 在 `/apps/empyrean/tools/aether_new/bin/asOut`，layerMap=`/apps/imctf/libs/dfii/cxmtG4C/current/layer.map`，从 `lib.defs` 第 63-64 行找到 `DEFINE A_felixw_test /proj/drgqx/V0/workdir/felixw/A_felixw_test`
- msg 48-50: **asOut 成功**，`test1.gds` 生成 (2048 bytes, 0 errors, 12 paths + 5 inst)

### Phase 2 (msg 55-106): pyAether sandbox 故障诊断 (核心意图)
- msg 55: "ip_port.json 这里是 ip_port 文件吧，你再试试" — felixw 让 agent 重试 pyAether sandbox
- msg 84/97: "测试一下 pyAether 的沙箱功能是否正常" — 明确要求诊断 sandbox 连通性
- agent 诊断链：
  1. SandBox MCP 服务报 `Cannot reach sandbox [pyAether]: sandbox config not found: /home/felixw/.cline/data/settings/ip_port.json`（文件实际存在，权限 0664）
  2. **关键发现**：SandBox MCP 服务远程运行在 `10.129.8.86:9082`，读本机文件系统看不到 `ip_port.json`（不同 fs context）
  3. agent 读到 `ip_port.json` 内容：`{"pyAether": "10.129.8.110:31236", ...}`
  4. **TCP 直连 bridge 31236 = OPEN**（bridge 自 11-19 16:32 起在 Aether GUI 里运行）
  5. agent **逆向 bridge 协议**：
     - 请求：4 字节大端 uint32 长度前缀 + JSON body `{"code": "...", "lang": "..."}`
     - 响应：**裸 JSON**（无长度前缀）`{"response": "successful"|"failed", "print_log": "...", "error_log": "..."}`
     - 验证：发 `GET /` HTTP 请求 → bridge 回 `Invalid message length: 1195725856`（=0x47455420 = "GET " 大端）→ 证实 4 字节长度前缀
  6. **核心 bug 发现**：bridge 回 `"successful"` 但 `print_log`/`error_log` 全空，连 `1/0` 都不报错 → **代码没真正执行**（请求 JSON 键名不对，bridge 执行了"空代码"）
  7. msg 98-101: 测 3 种 lang (pyAether/skill/tcl) 全部同样报错 → 不是单 lang 问题
  8. msg 106: agent 最终结论分两块：sandbox 配置可见性问题 + bridge 协议键名不匹配

## trace gold (可提炼的判定知识)

1. **pyAether bridge 协议**：4-byte BE length prefix + JSON request, bare JSON response (no prefix)
2. **4 类 failure mode 分类**：
   - `unreachable`: TCP connect 失败 (timeout/refused)
   - `code_executed`: response="successful" AND print_log 含探针 token
   - `code_not_executed`: response="successful" AND print_log 空 (trace 核心 bug)
   - `error_returned`: response="failed"
3. **诊断报告结构**：per-bridge {name, host, port, tcp_reachable, classification, print_log, error_log}

## 跨 shard 串台检查

- 4-shard ledger: 930zw 0 hit (fresh, r933 claim)
- 4-shard jsonl trace_source: 0 hit
- 同 domain 已落库 case 全正交：
  - AetherLayerPurposeExplainer (layer 用途解释) ≠ bridge 协议诊断
  - VirtuosoDaemonReviewFix (SKILL daemon review) ≠ pyAether bridge
  - VirEnvCancelInitFix (vir 环境变量初始化) ≠ bridge 协议
  - AetherRcShortSync / AetherSmashCliPort (aether CLI) ≠ bridge 诊断
- 子型 "pyaether_bridge_protocol_diag" 首例

## reframe 决策

trace gold = bridge 协议逆向 + 4 类 failure mode 分类（非工具执行，是 debug-Q&A on env-connectivity）→ **档 B fixture-driven reframe**：
- agent 写 `bridge_diag.py`：读 ip_port.json，按 4-byte BE length-prefix JSON 协议探针每个 bridge，分类 4 种 failure mode，emit JSON 报告
- env_A (visible): 3 bridges (pyAether=works / skill=closed / tcl=not_executed) + mock_bridge.py 供本地测试
- hidden B: 4 bridges 不同名/端口/行为 (aether_main=works / aether_aux=error / le_shell=closed / py_console=not_executed)
- check.py 内嵌 mock bridge server (threading socket)，启动 B 的 4 个 bridge，跑 agent 脚本，断言分类

case-id: `EDA-Eval-DesignFlow-PyAetherBridgeDiagClassifier-001`
