# eda_flow MCP 健康自检 — r911 (2026-11-21)

> 用户令(2026-11-21最高优先)：实测 eda_flow MCP 是否在线 / 能否 open_session + run_commands。
> 全新 agent session 实测，r897–r910 同令同日已十五测，本 r911 为第十六次复测。

## §0 结论

**EDA_FLOW_OK** — initialize / open_session / run_commands / close_session 全通。

- `:18891` = **listening**（python pid 3365754，与 r897–r910 同进程持续在线未重启）
- curl initialize = **HTTP 200**（time_total=0.004642s）+ `serverInfo.name=EDA-FastMCP-Flow version=1.25.0` + `protocolVersion=2024-11-05` 回显
- `open_session` = **ok**（26ms，四参齐全：task_id=shardA-health-r911 / eval_id=designflow-healthcheck-20261121 / user=e0031982 / sample=ro_home，无 Missing key）
- `run_commands` = **ok**（43ms，1 cmd 全 exit 0：`echo ok; pwd; id -un`→`ok`/workdir/`e0031982`，error_log 空）
- `close_session` = **ok**（18ms，cleaned=true）
- `ip route get 10.129.32.75` = 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` eda_flow MCP 在线（python pid 3365754，与 r897–r910 同进程，未重启）
- `:8651` / `:8654` 未监听（pyAether 侧未起，非本次自检对象）
- `:8652` 监听中

### 1.2 握手（curl initialize，🚫 非 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

结果：**HTTP=200**，`time_total=0.004642s`

body 前 600 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools\n\nThis MCP server provides tools for design-flow EDA evaluation agents.\n\n## Design-flow session tools\n\n- **open_session**: Create a session workdir on the EDA sandbox (.75).\n  Returns the workdir path — pass it to every subsequent tool call.\n- **clos
```

有 `serverInfo`（name=EDA-FastMCP-Flow, version=1.25.0），有 `protocolVersion` 回显，无报错。

### 1.3 open_session → run_commands → close（含耗时 + 返回前 200 字符）

**open_session**（耗时 26ms）

四参：`task_id=shardA-health-r911` / `eval_id=designflow-healthcheck-20261121` / `user=e0031982` / `sample=ro_home`

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r911_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```

无 Missing key，error_log 空。

**run_commands**（耗时 43ms）— 仅跑 `echo ok; pwd; id -un`

返回前 200 字符：
```
{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r911_ro_home\ne0031982\n","stderr":"","duration_ms":28,"timed_out":false}],"files":{},"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r911_ro_home","response":"ran 1 command(s)"
```

1 cmd 全 exit 0，stdout = `ok` / workdir / `e0031982`，error_log 空。

**close_session**（耗时 18ms）

返回前 200 字符：
```
{"workdir":"..._shardA-health-r911_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```

cleaned=true。

### 1.4 `ip route get 10.129.32.75`

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

`.75` 可达。

## §2 MEMORY 一行

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r911_20261121.md`

## §三 OK 分支处置

本轮 0-case（非能力结论，infra 全通）。沿用 r897–r910 三层原因：
1. 扫描快照与 r897–r910 同源 `ssh_eda_search_20261121_005100`（5434 行）无新 trace；
2. A-pure fresh 池枯竭第 17 次确认（r877 终证 / r883 / r885 / r897–r910 再确认）— `pool_reaudit_A.tsv` 唯一「可造」jeij7 已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`，无未造可造候选；ledger A parked 条目经复核均合理（wrong-domain / thin / GUI / no-gold），NOFILE 复活机会 r893–r896 已用尽；
3. 剩余预算（~30min）不足完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5neg + 自验），质量硬要求禁 `incomplete` 入 jsonl 故不凑数。

按纪律 MEMORY 写 `WAITING: 0`（非 WAITING:1）。✅ infra 失败 ≠ 能力结论。

## 统计

📊 400/3164 ≈ 12.6%（不变，本轮 0-case）。📦 TASK_A≈40KB / MEMORY_A≈32KB。
