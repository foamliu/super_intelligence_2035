# eda_flow MCP 健康自检 r931 · 2026-11-21

> 任务书顶部令「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检 · 最高优先 · 一轮内做完」第三十五次复测。
> 全新 agent session 实测。r897-r930 同令同日已三十四测，本轮 r931。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 均通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r931_20261121.md`

## §1 本机端口监听（ss -ltnp）

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- :18891 = listening（python pid=3365754，与 r897-r930 同进程持续在线，未重启）
- :8652 = listening
- :8651 / :8654 = 未监听（无匹配）

进程信息：
```
PID     ELAPSED        ELAPSED    CMD
3365754 24-21:20:27     2150427    /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```
（r930 时 etimes=2150121s，本轮 2150427s，增长 ~306s ≈ 5:06，与每轮间隔吻合，确认同进程未重启）

## §2 curl initialize 握手（POST，非裸 GET）

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：200
- **serverInfo**：`EDA-MCP-SERVER` v1.25.0
- **protocolVersion 回显**：2024-11-05
- **报错原文**：无（curl writing output 警告系 -o 重定向管道无关，body 完整）
- body 前 200 字符：
  `{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SER`

## §3 open_session → run_commands → close 各耗时 + 返回前 200 字符

### open_session（54ms · 四参齐）

参数：
- `task_id="shardA-health-r931"`
- `eval_id="designflow-healthcheck-20261121"`
- `user="e0031982"`
- `sample="ro_home"`

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r931_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- 耗时：54ms
- error_log：空（成功）
- workdir：`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r931_ro_home`
- 无 `Missing key` 报错

### run_commands（24ms wall · cmd duration_ms=8 · 1 cmd · exit 0）

命令：`echo ok; pwd; id -un </dev/null`（加 `</dev/null` 防 ssh hang；本轮未用 ssh 故无 hang 风险）

返回前 200 字符：
```
{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r931_ro_home\ne0031982\n","stderr":"","duration_ms":8,"timed_out":false}],"files":{},"workdir":"/proj/train/AI/wo
```
- 耗时：24ms（wall） / 8ms（cmd duration）
- exit_code：0
- stdout：`ok` / workdir 路径 / `e0031982`
- stderr：空
- timed_out：false
- error_log：空

### close_session（16ms · cleaned=true）

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r931_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- 耗时：16ms
- cleaned：true

## §4 网络可达性（ip route）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
- .75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

## §5 结论与处置

**EDA_FLOW_OK** — open_session + run_commands + close_session 三件全通，:18891 持续 listening，curl initialize HTTP 200 + serverInfo 回显，.75 路由可达。

按任务书 §三「OK ⇒ 本轮按 §6 转造题 1 条」执行尝试，结果：本轮 0-case。原因见 MEMORY 流水（池枯竭第 35 次确认 + 预算不足 + 质量硬要求禁 incomplete 入 jsonl）。
