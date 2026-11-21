# eda_flow MCP 健康自检报告 — r934 · 2026-11-21

> 任务书：BAIZE_DESIGNFLOW_BENCH_TASK_A.md 顶部「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检」第三十八次复测（r897-r933 同令同日已三十七测，本 r934 为全新 agent session 实测）。
> 运行环境：本机 10.251.36.15（36.15）→ eda_flow MCP `http://127.0.0.1:18891/mcp` → `.75`（10.129.32.75 / hfhds201）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 两者皆通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r934_20261121.md`

## §1 端口监听（ss -ltnp | grep -E '18891|8651|8652|8654'）

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening — eda_flow MCP 主端口，python pid=3365754（与 r897-r933 同进程持续在线，未重启）。
- `:8652` listening（pyAether/sandbox 侧端口之一）。
- `:8651` / `:8654` 本轮未在监听表出现（与历史一致，非必需端口）。

进程持续性：pid=3365754 与 r897-r933 报告记录的 pid 完全一致，确认**同一进程持续在线未重启**（自 r897 起跨 38 轮稳定）。

## §2 MCP 握手（curl initialize，🚫 非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（HTTP 200，time_total=0.003021s）：
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
  task_id: "shardA-health-r934",
  eval_id: "designflow-healthcheck-20261121",
  user: "e0031982",
  sample: "ro_home"
})
```

返回（耗时 40ms）：
- `workdir` = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r934_ro_home`
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

返回（耗时 28ms wall）：
```json
[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r934_ro_home\ne0031982\n","stderr":"","duration_ms":11,"timed_out":false}]
```

- exit_code = **0**
- stdout = `ok` / `<workdir 路径>` / `e0031982`（三行，与 `echo ok; pwd; id -un` 预期一致）
- stderr = 空
- `duration_ms` = 11（cmd 自身），wall = 28ms（MCP 往返开销）
- `timed_out` = false
- `error_log` = 空
- 本轮未用 ssh 故无 hang 风险（`</dev/null` 仍按纪律加上）

### §3.3 close_session

返回（耗时 17ms）：
- `cleaned` = **true**
- `response` = `session workdir cleaned`
- `error_log` = 空

## §4 ip route 可达性（NETBLOCK 排除）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

本机 36.15 → .75 路由可达，非 NETBLOCK。

## §5 §三 OK 分支 — 造题尝试与 0-case 判定

依令 §三「OK ⇒ 本轮按 §6 转造题 1 条」，本轮在健康自检后尝试造题，结果 **0-case**，依据：

1. **扫描快照无变化**：`summary_stats.json.scan_path` 仍为 `ssh_eda_search_20261121_005100`（11-21 03:19，与 r897-r933 同源），mc10=3164，无新 trace 进入候选池。
2. **ledger `next --n 5` 仅回吐 scansync 命令模板**（无 fresh 候选清单）：`stats` 显示 covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285 / claimed 0），剩余可做 ≈ 2511 但**池内去重后无未触碰的 A-pure fresh 候选**——A-pure fresh 池枯竭第 **38** 次确认（r877 终证 / r883 / r885 / r897-r933 再确认 / 本 r934 复确认）。
3. **pool_reaudit_A.tsv "可造" 行已全部落库**：jeij7(r844) / plk7n(r894) / bdhyb(r895+r896) 均已造完入 jsonl，台账陈旧但实际无未造可造候选。
4. **NOFILE 假阴性复活已用尽**：r893-r896 三条 subdir-path 复活（g7hp7/plk7n/bdhyb）已全部造完，r897 起再无可复活条目。
5. **预算不足**：健康自检令已交付（约 5 分钟），剩余预算不够完成「deepread + ≥8 断言 check.py + 5 neg + 自验」全闭环。
6. **质量硬要求**：§4.3 / 顶部令 21:5x 规定未过闸门 case 标 `incomplete`，🚫 不许落 jsonl、🚫 不许计入通过率——故不凑数。

**0-case 不是能力结论，是选料枯竭 + 预算不足的事实**（§四 纪律：infra 失败 ≠ 能力结论；本轮 infra 实测 OK）。

## §6 eda_flow session 状态

r934 session 已 `close_session`，`cleaned=true`，无残留 workdir。

## §7 心跳口径数字

- 📊 trace 覆盖率：400 / 3164 ≈ **12.6%**（不变）
- 📦 体积：TASK_A ≈ 41KB（只读指令文件，非本 agent 编辑）/ MEMORY_A ≈ 29.4KB
- 🎯 通过率：观察值（本轮无新 case）
