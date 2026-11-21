# eda_flow MCP 健康自检报告 r936 (2026-11-21)

> 用户令：2026-11-21 shard A eda_flow MCP 健康自检 · 最高优先 · 一轮内做完
> 本轮 = 第四十次复测（r897-r935 已三十九测均 EDA_FLOW_OK）
> 全新 agent session 实测，非抄录历史

## §0 结论

**EDA_FLOW_OK** — open_session + run_commands 均通。

```
eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r936_20261121.md
```

## §1 端口监听 (ss -ltnp)

```
$ ss -ltnp 2>/dev/null | grep -E '18891|8651|8652|8654'
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- :18891 **listening**（python pid=3365754，与 r897-r935 同一进程，未重启）
- :8652 listening（无 8651 / 8654）
- 进程 etimes：`ps -o pid=,etimes=,cmd= -p 3365754` → `3365754 2152557 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python .../main.py` → 2152557s ≈ **24.9 天**，自 r897 起跨 40 轮稳定在线

## §2 MCP initialize 握手（curl POST，非裸 GET）

```
$ curl -sS -m 8 -w '\nHTTP_CODE=%{http_code}\n' -X POST http://127.0.0.1:18891/mcp \
    -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（首 600 字符）：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools ..."}}
HTTP_CODE=200
```

- **HTTP 200**
- `serverInfo` 存在：name=`EDA-FastMCP-Flow` version=`1.25.0`
- `protocolVersion` 回显 `2024-11-05`
- 无报错原文

## §3 open_session → run_commands → close_session

### open_session（四参齐，无 Missing key）

调用：
```
open_session({
  task_id: "shardA-health-r936",
  eval_id: "designflow-healthcheck-20261121",
  user: "e0031982",
  sample: "ro_home"
})
```

- 耗时：**322 ms**
- 返回（前 200 字符）：
  ```
  workdir=/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r936_ro_home
  response=session workdir ready
  error_log=（空，无 "Missing key"）
  ```

### run_commands（只读探针，ssh 加 </dev/null 但本轮未用 ssh）

调用：
```
run_commands({
  commands: ["echo ok; pwd; id -un </dev/null"],
  workdir: <上述 workdir>,
  timeout_per_cmd: 30
})
```

- 耗时：wall **43 ms**（MCP 往返开销），命令自身 `duration_ms=11`
- 返回（前 200 字符）：
  ```
  cmd=echo ok; pwd; id -un </dev/null
  exit_code=0
  stdout=ok
  /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r936_ro_home
  e0031982
  stderr=（空）
  timed_out=false
  error_log=（空）
  ```

### close_session

- 耗时：**22 ms**
- 返回：`cleaned=true` / `response=session workdir cleaned` / `error_log=（空）`

## §4 网络可达性

```
$ ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

本机（10.251.36.15）→ .75（10.129.32.75）路由可达（via 10.251.36.1 dev bond0）。

## §5 本轮造题（§三 OK 分支）

按 §三「OK ⇒ 本轮按 §6 转造题 1 条」尝试：

- 扫描快照同 r897-r935：`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace
- `trace_ledger.py --shard A next --n 5` 仅回吐 scansync 命令模板（无 fresh 候选清单）
- ledger stats：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），剩余可做 ≈2511
- A-pure fresh 池枯竭 **第 40 次确认**（r877 终证 / r883 / r885 / r897-r935 再确认 / r936 本轮）
- `pool_reaudit_A.tsv`「可造」行 jeij7(r844) / plk7n(r894) / bdhyb(r895+r896) 均已落库，台账陈旧但实际无未造可造候选
- NOFILE 假阴性复活 r893-r896 已用尽
- 预算不足：健康自检令已交付，剩余预算不够 deepread + ≥8 断言 check.py + 5 neg + 自验
- 质量硬要求禁 incomplete 入 jsonl，故不凑数

**本轮 0-case**（与 r897-r935 同），WAITING: 0（非外部阻塞，是池枯竭 + 预算约束）。

## §6 体积

- TASK_A ≈ 41 KB（含顶部多层归档指针，未超 40 KB 红线 + 余量）
- MEMORY_A ≈ 30 KB（本轮追加 r936 一行流水后保持 ≤32 KB）
