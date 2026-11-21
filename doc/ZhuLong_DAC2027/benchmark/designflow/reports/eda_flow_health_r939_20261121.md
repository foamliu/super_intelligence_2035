# eda_flow MCP 健康自检 · r939 · 2026-11-21

> 用户令：2026-11-21 shard A eda_flow MCP 健康自检（最高优先 · 一轮内做完）。
> 本轮 = 第四十三次复测（r897-r938 已四十二测，本轮 r939 全新 agent session 实测）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 两者都通。

- open_session = ok（16ms，四参齐：task_id=shardA-health-r939 / eval_id=designflow-healthcheck-20261121 / user=e0031982 / sample=ro_home，无 Missing key）
- run_commands = ok（wall 22ms，cmd duration_ms=8，1 cmd `echo ok; pwd; id -un </dev/null` exit 0，stdout=ok / workdir 路径 / e0031982，stderr 空，error_log 空，timed_out=false）
- close_session = ok（16ms，cleaned=true）
- :18891 = listening（python pid 3365754，与 r897-r938 同进程持续在线未重启，自 r897 起跨 43 轮稳定）
- curl initialize HTTP 200（time_total=0.002849s）+ serverInfo=EDA-FastMCP-Flow v1.25.0 + protocolVersion 2024-11-05 回显
- ip route 10.129.32.75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）
- :8652 = listening；:8651 / :8654 未监听（本轮未用，不影响主路径）

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- :18891 listening，pid 3365754（与 r897-r938 同进程，持续在线未重启）。
- :8652 listening（无 owner 显示）。
- :8651 / :8654 未监听（grep 未匹配）。

### 1.2 curl initialize 握手（🚫 未用裸 GET，按令用 POST initialize）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

HTTP 码：**200**，time_total=**0.002849s**。

响应 body 前 600 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools\n\nThis MCP server provides tools for design-flow EDA evaluation agents.\n\n## Design-flow session tools\n\n- **open_session**: Create a session workdir on the EDA sandbox (.75).\n  Returns the workdir path — pass it to every subsequent tool call.\n- **close_session**: Release the workdir (archives then removes it).\n- **declare_done**: Signal that the agent has finished its work. The eval\n  driver will then run the test checker on the workdir.\n\n## Execution tools\n\n- **run_commands**: Run a sequence of shell/EDA commands in the session\n  workdir. Returns per-command exit_code/stdout/stderr plus any `return_files` content. Single command\n  failure does NOT abort the sequence.\n- **run_code**: Execute code in an EDA interpreter (pyAether/SKILL/Tcl) on\n  the sandbox. Pass `workdir` to exe
```

- ✅ serverInfo 出现：`EDA-FastMCP-Flow v1.25.0`
- ✅ protocolVersion 2024-11-05 回显
- ✅ 无报错原文

### 1.3 `ip route get 10.129.32.75`

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

- .75 可达（非 NETBLOCK）。

### 1.4 open_session → run_commands → close 全程

**open_session（16ms）** — 四参齐，无 Missing key：
```json
{
  "workdir": "/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r939_ro_home",
  "response": "session workdir ready",
  "error_log": "",
  "print_log": "",
  "result": ""
}
```

**run_commands（wall 22ms，cmd duration_ms=8，1 cmd `echo ok; pwd; id -un </dev/null`）**：
```json
{
  "results": [{
    "cmd": "echo ok; pwd; id -un </dev/null",
    "exit_code": 0,
    "stdout": "ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r939_ro_home\ne0031982\n",
    "stderr": "",
    "duration_ms": 8,
    "timed_out": false
  }],
  "files": {},
  "workdir": "/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r939_ro_home",
  "response": "ran 1 command(s)",
  "error_log": "",
  "print_log": "",
  "result": ""
}
```

- exit 0；stdout 三行：`ok` / workdir 路径 / `e0031982`；stderr 空；error_log 空；timed_out=false。
- cmd 自身 8ms，wall 22ms 为 MCP 往返开销。本轮未用 ssh，故无 hang 风险。

**close_session（16ms，cleaned=true）**：
```json
{
  "workdir": "/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r939_ro_home",
  "cleaned": true,
  "response": "session workdir cleaned",
  "error_log": "",
  "print_log": "",
  "result": ""
}
```

- eda_flow session r939 cleaned（cleaned=true）。

## §2 本轮产出

**0-case**。§二明令「🚫 本 session 不做深读/造题，测完 close」故不转造题（r897-r938 同令同日四十二测均 OK，本轮第 43 测结果一致，eda_flow MCP 主路径 :18891→.75 持续健康）。

## §3 结论四选一

**EDA_FLOW_OK** — open_session 与 run_commands 两者都通。
