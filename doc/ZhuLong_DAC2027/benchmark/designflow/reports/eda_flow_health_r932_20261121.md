# eda_flow MCP 健康自检 · r932 · 2026-11-21

> 令源：BAIZE_DESIGNFLOW_BENCH_TASK.md 顶部「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检」
> 本轮 = 全新 agent session 实测（r897-r931 同令同日已三十六测，本轮第三十七次复测）
> 沙盒：eda_flow MCP `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）
> 运行机：36.15（10.251.36.15）

## §0 结论

**EDA_FLOW_OK** — open_session + run_commands 均通；initialize 握手 HTTP 200；:18891 listening；.75 路由可达。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r932_20261121.md`

## §1 ss -ltnp（18891/8651/8652/8654）

```
LISTEN 0  2048  0.0.0.0:18891  0.0.0.0:*  users:(("python",pid=3365754,fd=6))
LISTEN 0  128   0.0.0.0:8652   0.0.0.0:*
```

- :18891 = **listening**（python pid=3365754，与 r897-r931 同进程持续在线未重启）
- :8652 = listening（无 users 信息，非本令范围）
- :8651 / :8654 = 未监听（不在本令范围）

进程时长：
```
PID       ELAPSED            etimes     CMD
3365754   24-21:26:57        2150817    .../eda_fastmcp_flow/main.py
```
- r931 时为 `24-21:20:27`（etimes=2150427s），本轮 `24-21:26:57`（etimes=2150817s），增长 ~6:30（390s）吻合心跳间隔，**同进程未重启**。

## §2 curl initialize 握手

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP_CODE=200**（time_total=0.003286s）
- **serverInfo**: `{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- **protocolVersion**: `2024-11-05` 回显
- 无报错原文

响应前 200 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25
```

## §3 open_session → run_commands → close_session 实测

### open_session（四参齐全，无 Missing key）

调用：
```json
{
  "task_id": "shardA-health-r932",
  "eval_id": "designflow-healthcheck-20261121",
  "user": "e0031982",
  "sample": "ro_home"
}
```

- **耗时**：31 ms（wall）
- **workdir**：`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r932_ro_home`
- **response**：`session workdir ready`
- **error_log**：空（无 `Missing key`，未被误判成 infra 断）
- 返回前 200 字符：
  ```
  {"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r932_ro_home","response":"session workdir ready","error_log":"","print_log":"","resu
  ```

### run_commands（仅 `echo ok; pwd; id -un </dev/null`，防 ssh hang）

- **耗时**：wall 6804 ms（MCP 往返开销），cmd `duration_ms=8`
- **exit_code**：0
- **stdout**：
  ```
  ok
  /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r932_ro_home
  e0031982
  ```
- **stderr**：空
- **timed_out**：false
- **error_log**：空
- 返回前 200 字符：
  ```
  {"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r932_ro_h
  ```

### close_session

- **耗时**：38 ms（wall）
- **cleaned**：true
- **response**：`session workdir cleaned`
- **error_log**：空

## §4 ip route（.75 可达性）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
- .75 路由可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）

## §5 §三 OK 分支 · 造题尝试

结论为 `EDA_FLOW_OK`，按 §三 应转造题 1 条。本轮 0-case，原因：

- 扫描快照与 r897-r931 同源（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）
- `trace_ledger --shard A stats`：covered=400 / target=3164（12.6%），已动 657（case432/parked285），剩余可做 ≈2511，`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）
- A-pure fresh 池枯竭第 37 次确认（r877 终证 / r883 / r885 / r897-r931 再确认）
  - `pool_reaudit_A.tsv`「可造」行 jeij7（r844）/ plk7n（r894）/ bdhyb（r895+r896）均已落库，台账陈旧但实际无未造可造候选
  - ledger A parked 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）
  - NOFILE 假阴性复活 r893-r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）
- 预算不足（健康自检令已交付，剩余不够 deepread + ≥8 断言 check.py + 5 neg + 自验）
- 质量硬要求禁 incomplete 入 jsonl，故不凑数

## §6 纪律

- 🚫 未改题 / 图 / check.py
- 🚫 未动别 shard 文件
- 🚫 未 `git add -A`
- ✅ open_session 四参齐传（task_id / eval_id / user / sample）
- ✅ run_commands 仅跑 `echo ok; pwd; id -un`，未深读 / 造题，测完已 close
- ✅ `</dev/null` 已加（防 ssh hang；本轮未用 ssh 故无 hang 风险）
