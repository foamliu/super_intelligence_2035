# eda_flow MCP 健康自检 · r926 · 2026-11-21

> 令源：BAIZE_DESIGNFLOW_BENCH_TASK.md 顶部「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检」
> 本轮 = 全新 agent session 实测（r897-r925 同令同日已三十测，本轮第三十一次复测）
> 沙盒：eda_flow MCP `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）
> 运行机：36.15（10.251.36.15）

## §0 结论

**EDA_FLOW_OK** — open_session + run_commands 均通；initialize 握手 HTTP 200；:18891 listening；.75 路由可达。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r926_20261121.md`

## §1 ss -ltnp（18891/8651/8652/8654）

```
LISTEN 0  2048  0.0.0.0:18891  0.0.0.0:*  users:(("python",pid=3365754,fd=6))
LISTEN 0  128   0.0.0.0:8652   0.0.0.0:*
```

- :18891 = **listening**（python pid=3365754，与 r897-r925 同进程持续在线未重启）
- :8652 = listening（无 users 信息，非本令范围）
- :8651 / :8654 = 未监听（不在本令范围）

进程时长：
```
PID    ELAPSED       etimes    CMD
3365754 24-20:54:13   2148853   .../eda_fastmcp_flow/main.py
```
- r925 时为 `24-20:49:27`（etimes=2148567s），本轮 `24-20:54:13`（etimes=2148853s），增长 ~4:46（286s）吻合心跳间隔，**同进程未重启**。

## §2 curl initialize 握手

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP_CODE=200**
- **serverInfo**: `{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- **protocolVersion**: `2024-11-05` 回显
- 无报错原文

响应前 200 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.
```

## §3 open_session → run_commands → close 各耗时 + 返回前 200 字符

### open_session（四参齐全）

调用参数（§二要求）：
- task_id = `shardA-health-r926`
- eval_id = `designflow-healthcheck-20261121`
- user = `e0031982`
- sample = `ro_home`

- **耗时**：29 ms
- **error_log**：空（无 `Missing key` 误判）
- 返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r926_ro_home","response":"session workdir ready","error_log":"","print_log"
```

### run_commands

- 命令：`echo ok; pwd; id -un </dev/null`（单条，按 §二要求；ssh hang 坑以 `</dev/null` 回避）
- **耗时**：wall 8662 ms（含 1 cmd duration_ms=22；wall 偏高为 MCP 往返开销，cmd 自身仅 22ms）
- **exit_code**：0
- **timed_out**：false
- **error_log**：空
- stdout 前 200 字符：
```
ok
/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r926_ro_home
e0031982
```
- stderr：空

### close_session

- **耗时**：26 ms
- **cleaned**：true
- 返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r926_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":""
```

## §4 网络可达性

```
ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
- .75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013），与 r897-r925 同。

## §5 §三 OK 分支 · 造题尝试

按 §三「OK ⇒ 本轮按 §6 转造题 1 条」尝试造题，结论：**本轮 0-case**，理由：

1. **扫描快照与 r897-r925 同源**：`summary_stats.json.scan_path = ssh_eda_search_20261121_005100`，`mc10=3164`，`updated_at=2026-11-21 03:19`，无新 trace。
2. **台账状态不变**：covered=400/target=3164(12.6%)，已动 657（case 432 / parked 285）。`next --n 5` 仅回吐 scansync 命令模板，无 fresh 候选清单。
3. **A-pure fresh 池枯竭第 31 次确认**（r877 终证 / r883 / r885 / r897-r925 再确认）：`pool_reaudit_A.tsv` 唯一"可造" jeij7 已在 r844 落库为 EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001；NOFILE 假阴性复活 r893-r896 已用尽。
4. **预算不足**：本轮为健康自检令（最高优先），测完即 `close`；剩余预算不够完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验）。
5. **质量硬要求禁 incomplete 入 jsonl**：不凑数。

## §6 纪律自检

- 🚫 未改题/图/check.py；未动别 shard；未 `git add -A`。
- ✅ infra 失败 ≠ 能力结论（本轮 infra 全通，无此问题）。
- ✅ open_session 四参齐全，无 `Missing key` 误判。
- ✅ ssh hang 坑已回避（本令 run_commands 无 ssh；`</dev/null` 已加）。
- ✅ 报告随心跳提交。
