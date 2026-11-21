# eda_flow MCP 健康自检 · r938 · 2026-11-21

> 用户令（2026-11-21 最高优先）：shard A 实测澄清 eda_flow MCP 是否还在、能否 open_session / run_commands。
> 本轮 = r938（全新 agent session 第 42 次复测，r897–r937 同令同日已四十一测均 EDA_FLOW_OK）。
> 纪律遵守：§二「🚫 本 session 不做深读/造题，测完 close」——本轮仅自检，不造题。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 均通。

- open_session = **ok**（17ms，四参齐 task_id=shardA-health-r938 / eval_id=designflow-healthcheck-20261121 / user=e0031982 / sample=ro_home，无 Missing key，error_log 空）
- run_commands = **ok**（wall 26ms，cmd duration_ms=10，exit 0，stdout=ok/workdir/e0031982，stderr 空，timed_out=false，error_log 空）
- close_session = **ok**（25ms，cleaned=true）
- `:18891` = **listening**（python pid 3365754，与 r897–r937 同进程持续在线未重启，etimes=2153159s≈24.9 天）
- curl `initialize` HTTP 200 + serverInfo `EDA-FastMCP-Flow v1.25.0` + protocolVersion `2024-11-05` 回显
- ip route 10.129.32.75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）

## §1 原始输出

### 1.1 端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening（eda_flow MCP，python pid 3365754）
- `:8652` listening（pyAether 副端口，无 pid 信息）
- `:8651` / `:8654` 未监听（本轮未用，不影响 eda_flow 主路径）

### 1.2 curl initialize 握手（非裸 GET）

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- HTTP 码 = **200**，time_total = 0.003588s
- 有 `serverInfo` = `{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- protocolVersion 回显 = `2024-11-05`
- 报错原文 = 无

响应 body 前 600 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools\n\nThis MCP server provides tools for design-flow EDA evaluation agents.\n\n## Design-flow session tools\n\n- **open_session**: Create a session workdir on the EDA sandbox (.75).\n  Returns the workdir path — pass it to every subsequent tool call.\n- **clos
```

### 1.3 open_session（四参齐）

```
elapsed_ms: 17
workdir:    /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r938_ro_home
response:   session workdir ready
error_log:  (空)
```

返回前 200 字符：
`{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r938_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}`

无 `Missing key` 报错（对比 D 线 r1037 根因：传 `{}` 会被误判 infra 断；本轮四参齐通过）。

### 1.4 run_commands（只跑 `echo ok; pwd; id -un </dev/null`）

```
elapsed_ms: 26 (wall, 含 MCP 往返开销)
cmd:        echo ok; pwd; id -un </dev/null
exit_code:  0
duration_ms: 10 (cmd 本身)
timed_out:  false
stdout:     ok
            /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r938_ro_home
            e0031982
stderr:     (空)
error_log:  (空)
```

返回前 200 字符：
`{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/.../e0031982_designflow-healthcheck-20261121_shardA-health-r938_ro_home\ne0031982\n","stderr":"","duration_ms":10,"timed_out":false}],"files":{},"workdir":"/proj/.../e0031982_designflow-healthcheck-20261121_shardA-health-r938_ro_home","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}`

本轮未用 ssh，故无 hang 风险（`</dev/null` 仍按令加上）。

### 1.5 close_session

```
elapsed_ms: 25
cleaned:    true
response:   session workdir cleaned
error_log:  (空)
```

### 1.6 旁证：进程在线时长 + 路由可达

```
ps -o pid=,etimes=,cmd= -p 3365754
3365754 2153159 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py

ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

- etimes=2153159s ≈ 24.9 天，与 r897–r937 同进程（pid 未变），跨 42 轮稳定在线未重启。
- .75（10.129.32.75）路由可达，src 10.251.36.15（本机 36.15）。

## §2 结论与处置

**EDA_FLOW_OK**（四选一中的第一项）。

- 本轮按 §二「🚫 本 session 不做深读/造题，测完 close」执行，不转造题。
- 历史对照：r897–r937 共 41 轮同令同日复测均 EDA_FLOW_OK，本轮第 42 测结果一致，eda_flow MCP 主路径（:18891 → .75）持续健康。
- 本轮 0-case（自检令已交付；§二明令本 session 不造题）。

## §3 纪律自查

- ✅ open_session 四参齐（task_id/eval_id/user/sample），非 `{}`，无 Missing key 误判。
- ✅ run_commands 只跑 `echo ok; pwd; id -un`，未做深读/造题/写远端。
- ✅ ssh 未使用（命令不涉 ssh），`</dev/null` 仍按令加上。
- ✅ 未改题/图/check.py，未动别 shard，未 `git add -A`。
- ✅ infra 通过 ≠ 能力结论（本轮仅自检，不做能力判定）。
- ✅ close 已执行（cleaned=true）。
