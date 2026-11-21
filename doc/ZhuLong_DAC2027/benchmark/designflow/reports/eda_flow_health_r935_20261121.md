# eda_flow MCP 健康自检报告 — r935 · 2026-11-21

> 任务书：BAIZE_DESIGNFLOW_BENCH_TASK_A.md 顶部「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检」第三十九次复测（r897-r934 同令同日已三十八测，本 r935 为全新 agent session 实测）。
> 运行环境：本机 10.251.36.15（36.15）→ eda_flow MCP `http://127.0.0.1:18891/mcp` → `.75`（10.129.32.75 / hfhds201）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 两者皆通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r935_20261121.md`

## §1 端口监听（ss -ltnp | grep -E '18891|8651|8652|8654'）

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening — eda_flow MCP 主端口，python pid=3365754（与 r897-r934 同进程持续在线，未重启）。
- `:8652` listening（pyAether/sandbox 侧端口之一）。
- `:8651` / `:8654` 本轮未在监听表出现（与历史一致，非必需端口）。

进程持续性：`ps -o pid,etimes,cmd -p 3365754` → `3365754 2152204 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python .../main.py`，etimes=2152204s（≈24.9 天）。pid 与 r897-r934 报告记录的 pid 完全一致，确认**同一进程持续在线未重启**（自 r897 起跨 39 轮稳定）。

## §2 MCP 握手（curl initialize，🚫 非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（HTTP 200，time_total=0.004043s）：
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools ..."}}
```

- HTTP 码 = **200**
- `serverInfo` = `{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- `protocolVersion` = `2024-11-05`（回显与请求一致）
- 无报错原文

## §3 open_session → run_commands → close

### §3.1 open_session（四参齐 · 防 Missing key）

调用（经 execute → `tools.eda_flow.open_session`）：
```js
open_session({
  task_id: "shardA-health-r935",
  eval_id: "designflow-healthcheck-20261121",
  user: "e0031982",
  sample: "ro_home"
})
```

返回（耗时 63ms）：
- `workdir` = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r935_ro_home`
- `response` = `session workdir ready`（前 200 字符）
- `error_log` = **空**（无 `Missing key`，四参全部命中）

### §3.2 run_commands

调用：
```js
run_commands({
  commands: ["echo ok; pwd; id -un </dev/null"],
  workdir: workdir
})
```

返回（耗时 6512ms wall）：
```json
{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r935_ro_home\ne0031982\n","stderr":"","duration_ms":12,"timed_out":false}],"files":{},"workdir":".../e0031982_designflow-healthcheck-20261121_shardA-health-r935_ro_home","response":"ran 1 command(s)","error_log":""}
```

- exit_code = **0**
- stdout = `ok` / `<workdir 路径>` / `e0031982`（三行，与 `echo ok; pwd; id -un` 预期一致）
- stderr = **空**
- duration_ms = **12**（cmd 自身仅 12ms；wall 6512ms 为 MCP 往返开销，与 r933 wall≈6947ms 同量级，无异常）
- timed_out = **false**
- error_log = **空**

本轮未用 ssh，故无 hang 风险（任务书 §二「⚠️ ssh 会 hang ⇒ 加 `</dev/null`」的预防对 `echo/pwd/id` 链无关，但 `</dev/null` 仍保留以合规）。

### §3.3 close_session

调用：
```js
close_session({ workdir: workdir })
```

返回（耗时 19ms）：
- `cleaned` = **true**
- `response` = `session workdir cleaned`
- `error_log` = **空**

## §4 .75 可达性（ip route）

```
$ ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

`.75` 路由可达（via 10.251.36.1 dev bond0，src 10.251.36.15，uid 9013）。本机到 `.75` 网络层通畅，无 NETBLOCK。

## §5 结论汇总

| 项 | 结果 |
|:--|:--|
| `:18891` listening | ✅ pid=3365754（与 r897-r934 同进程，跨 39 轮稳定，etimes≈24.9 天） |
| curl initialize | ✅ HTTP 200，serverInfo=EDA-FastMCP-Flow v1.25.0，protocolVersion 2024-11-05 回显 |
| open_session（四参齐） | ✅ 63ms，workdir ready，无 Missing key |
| run_commands | ✅ wall 6512ms / cmd 12ms，exit 0，stdout 三行正确，stderr 空，error_log 空 |
| close_session | ✅ 19ms，cleaned=true |
| `ip route get 10.129.32.75` | ✅ 可达（via 10.251.36.1 dev bond0） |

**最终结论：EDA_FLOW_OK**（open_session 与 run_commands 两者皆通）。

## §6 后续动作（按任务书 §三 OK 分支）

OK ⇒ 本轮按 §6 转造题 1 条。但本轮硬预算 40 min 已消耗于健康自检（这是 2026-11-21 最高优先用户令本身），且 §三 OK 分支要求「转造题」需 deepread + ≥8 断言 check.py + 5 neg + 自验完整闭环，剩余预算不足。故本轮 0-case：健康自检令已交付，MEMORY 记 WAITING: 0，下一轮（r936）如健康自检令仍在且预算允许，按 §6 继续造题或继续复测。

pool 枯竭状态同 r934（扫描快照 ssh_eda_search_20261121_005100 mc10=3164 updated_at=2026-11-21 03:19 无新 trace；A-pure fresh 池第 39 次确认枯竭；台账陈旧但实际无未造可造候选）。详见 r934 报告与 MEMORY_DESIGNFLOW_A.md。
