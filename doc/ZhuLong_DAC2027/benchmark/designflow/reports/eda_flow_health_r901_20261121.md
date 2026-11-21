# eda_flow MCP 健康自检 · r901 · 2026-11-21

> 用户令（最高优先 · 2026-11-21 shard A）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 背景：本机 = 36.15（`10.251.36.15`），eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（`10.129.32.75` / `hfhds201`）。
> 这是该令的第 **5** 次复测（全新 agent session 实测），前 4 次 = r897/r898/r899/r900，结论均为 `EDA_FLOW_OK`。

## §0 结论

**`EDA_FLOW_OK`** — `open_session` 与 `run_commands` 两者都通。

- `open_session` = **ok**（0.035s，四参齐全 task_id/eval_id/user/sample，无 `Missing key`）
- `run_commands` = **ok**（5.220s，3 条命令全部 exit 0，stdout = `ok` / `<workdir>` / `e0031982`，error_log 空）
- `close_session` = **ok**（0.029s，cleaned=true）
- `:18891` = **listening**（python pid=3365754，与 r897/r898/r899/r900 同进程，未重启；ELAPSED 24-18:36:51）
- curl `initialize` = **HTTP 200** + `serverInfo=EDA-FastMCP-Flow v1.25.0` + `protocolVersion 2024-11-05` 回显

MEMORY 首行：`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r901_20261121.md`

按 §三 OK 分支：本轮应转造题 1 条。**本轮实际 0-case**：扫描快照与 r897–r900 同源（`ssh_eda_search_20261121_005100`，无新 trace），A-pure fresh 池枯竭第 7 次确认（r877 终证 / r883 / r885 / r897 / r898 / r899 / r900 再确认）；`pool_reaudit_A.tsv` 唯一「可造」jeij7 经核验已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl 433 行 / assets + reference 齐全），实际无未造可造候选；余下预算不足以完成 1 条过闸门 case（深读 + ≥8 断言 check.py + 5 neg + 自验），质量硬要求禁 `incomplete` 入 jsonl 故不凑数。✅ infra 失败 ≠ 能力结论（本轮 infra 通畅，0-case 是选料枯竭 + 预算约束，非能力问题）。

## §1 原始输出

### 1.1 端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = listening（eda_flow MCP，python pid=3365754，与 r897/r898/r899/r900 同进程，未重启）
- `:8652` = listening（其他服务，非本自检对象）
- `:8651` / `:8654` = 未监听（未匹配，pyAether :8651 本轮未触及，不影响 eda_flow 自检结论）

进程详情（`ps -o pid,etime,cmd -p 3365754`）：
```
    PID     ELAPSED CMD
3365754 24-18:36:51 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```
进程持续在线 ~24 天 18 小时，与 r897/r898/r899/r900 报告的同一 pid 一致，**MCP 服务未发生重启**。

### 1.2 MCP 握手（initialize · 🚫 非 curl 裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

结果：
- **HTTP 码 = 200**
- **有 `serverInfo`**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- `protocolVersion` 回显 = `2024-11-05`
- `capabilities` 回显 = `{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}}`
- `instructions` 字段回显 EDA-FastMCP-Flow 工具说明（open_session / close_session / declare_done / run_commands / run_code / read_file / write_file / list_files）
- **无报错**

响应体前 1500 字符截取：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools\n\nThis MCP server provides tools for design-flow EDA evaluation agents.\n\n## Design-flow session tools\n\n- **open_session**: Create a session workdir on the EDA sandbox (.75).\n  Returns the workdir path — pass it to every subsequent tool call.\n- **close_session**: Release the workdir (archives then removes it).\n- **declare_done**: Signal that the agent has finished its work.\n\n## Execution tools\n\n- **run_commands**: Run a sequence of shell/EDA commands in the session\n  workdir.\n- **run_code**: Execute code in an EDA interpreter (pyAether/SKILL/Tcl) on\n  the sandbox.\n\n## File tools\n\n- **read_file**: Read a file from the sandbox.\n- **list_files**: List files in a directory on the sandbox.\n- **write_file**: Write a file into a session workdir on the sandbox."}}
```

### 1.3 `open_session → run_commands → close` 各耗时 + 返回前 200 字符

**open_session**（四参齐全，符合 §二「必须传四参」要求）：
- 参数：`task_id="shardA-health-r901"` / `eval_id="designflow-healthcheck-20261121"` / `user="e0031982"` / `sample="ro_home"`
- **耗时 = 0.035s**
- `workdir` = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r901_ro_home`
- `response` = `session workdir ready`
- `error_log` = **空**（无 `Missing key`，D 线 r1037 根因未复现）
- 返回前 200 字符：`{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r901_ro_home","response":"session workdir ready","error_log":""}`

**run_commands**（只跑 `echo ok` / `pwd` / `id -un` 三条，无 ssh 故无需 `</dev/null`）：
- **耗时 = 5.220s**（含 .75 远端 bash -lc 串行执行开销；3 条命令各自 exit 0）
- 命令 1 `echo ok`：exit 0，stdout=`ok\n`，stderr 空，duration_ms=2
- 命令 2 `pwd`：exit 0，stdout=`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r901_ro_home\n`，stderr 空，duration_ms=0
- 命令 3 `id -un`：exit 0，stdout=`e0031982\n`，stderr 空，duration_ms=9
- `response` = `ran 3 command(s)`
- `error_log` = **空**
- 返回前 200 字符：`{"results":[{"cmd":"echo ok","exit_code":0,"stdout":"ok\n","stderr":"","duration_ms":2,"timed_out":false},{"cmd":"pwd","exit_code":0,"stdout":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r901_ro_home\n","stderr":"","duration_ms":0,"timed_out":false},{"cmd":"id -un","exit_code":0,"stdout":"e0031982\n","stderr":"","duration_ms":9,"timed_out":false}],"files":{},"response":"ran 3 command(s)","error_log":""}`

**close_session**（`keep=false`）：
- **耗时 = 0.029s**
- `cleaned` = **true**
- `response` = `session workdir cleaned`
- `error_log` = **空**
- 返回前 200 字符：`{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r901_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":""}`

### 1.4 .75 网络可达性（OK 分支无需附，NETBLOCK 分支才需要；此处补记完整性）

```
ip route get 10.129.32.75
→ 10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
```
本机 36.15 → .75 路由可达（via 10.251.36.1 dev bond0 src 10.251.36.15）。

## §2 四选一判定依据

| 判定 | 触发条件 | 本轮 |
|:--|:--|:--|
| `EDA_FLOW_OK` | open_session 与 run_commands 两者都通 | ✅ **命中** |
| `EDA_FLOW_PARTIAL` | 通但 run_commands 受限 | — |
| `EDA_FLOW_DOWN` | initialize 即 refused | — |
| `EDA_FLOW_NETBLOCK` | 本机发不出去 | — |

判定 = `EDA_FLOW_OK`。open_session 0.035s + run_commands 5.220s（3 cmd 全 exit 0）+ close_session 0.029s（cleaned=true），全程 error_log 空，无任何 infra 拦截迹象。

## §3 OK 分支处置

按 §三：`OK` ⇒ 本轮按 §6 转造题 1 条。

**本轮实际 0-case**，原因（三层，非能力结论）：
1. **扫描快照无变化**：当前 `summary_stats.json.scan_path` = `ssh_eda_search_20261121_005100`（5434 行 / 3846 dedup），与 r897/r898/r899/r900 同源，无新 trace 流入。
2. **A-pure fresh 池枯竭第 7 次确认**（r877 终证 / r883 / r885 / r897 / r898 / r899 / r900 再确认）：`pool_reaudit_A.tsv` 唯一「可造」jeij7（e0039102@hfeg0pbn16 mc143 verification）经核验已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl 433 行 / assets + reference 齐全），该行未同步标「已造」属台账陈旧，实际无未造可造候选。
3. **预算约束**：本 session 剩余预算不足以完成 1 条过闸门 case（深读 + ≥8 断言 check.py + 5 neg + 自验 + pi 实跑），质量硬要求禁 `incomplete` 入 jsonl，故不凑数。

按 §三 OK 分支纪律：本轮 0-case 但 infra 通畅，**MEMORY 首行写 `WAITING: 0`**（非 `WAITING: 1`；WAITING:1 仅限真外部阻塞如 pi 异步未回 / 推送失败 / 等人工）。✅ infra 失败 ≠ 能力结论（本轮无 infra 失败）。

## §4 纪律自查

- ✅ open_session 传齐四参（task_id/eval_id/user/sample），无 `{}` ⇒ 无 `Missing key` 误判
- ✅ run_commands 只跑 `echo ok; pwd; id -un`（三条只读命令），无深读/造题
- ✅ 测完 close_session（cleaned=true），不留残留 workdir
- ✅ 未改题/图/check.py，未动别 shard，未 `git add -A`
- ✅ 本报告随心跳提交（§8.3）

## §5 与前序同令复测的对照

| 轮次 | 结论 | open_session | run_commands | close_session | :18891 pid | curl HTTP |
|:--|:--|:--|:--|:--|:--|:--|
| r897 | EDA_FLOW_OK | ok | ok | ok | 3365754 | 200 |
| r898 | EDA_FLOW_OK | ok | ok | ok | 3365754 | 200 |
| r899 | EDA_FLOW_OK | ok | ok | ok | 3365754 | 200 |
| r900 | EDA_FLOW_OK | ok (0.034s) | ok (0.105s) | ok (0.016s) | 3365754 | 200 |
| **r901** | **EDA_FLOW_OK** | **ok (0.035s)** | **ok (5.220s)** | **ok (0.029s)** | **3365754** | **200** |

MCP 服务进程（pid 3365754）自 r897 起持续在线未重启，5 次复测结论一致 = `EDA_FLOW_OK`。本轮 run_commands 耗时（5.220s）较 r900（0.105s）偏高，但 3 条命令全部 exit 0、error_log 空，属正常远端执行抖动，不影响 OK 判定。
