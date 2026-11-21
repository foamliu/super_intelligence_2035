# eda_flow MCP 健康自检报告 — r933 · 2026-11-21

> 任务书：BAIZE_DESIGNFLOW_BENCH_TASK_A.md 顶部「2026-11-21 用户令 · shard A：eda_flow MCP 健康自检」第三十七次复测（r897-r932 同令同日已三十六测，本 r933 为全新 agent session 实测）。
> 运行环境：本机 10.251.36.15（36.15）→ eda_flow MCP `http://127.0.0.1:18891/mcp` → `.75`（10.129.32.75 / hfhds201）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 两者皆通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r933_20261121.md`

## §1 端口监听（ss -ltnp | grep -E '18891|8651|8652|8654'）

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening — eda_flow MCP 主端口，python pid=3365754（与 r897-r932 同进程持续在线，未重启）。
- `:8652` listening（pyAether/sandbox 侧端口之一）。
- `:8651` / `:8654` 本轮未在监听表出现（与历史一致，非必需端口）。

进程 etimes：`ps -o etimes=` → **2151210s**（≈ 24d21h33m30s，即 `ELAPSED=24-21:33:30`）。r932 时为 2150817s（24-21:26:57），增长 393s ≈ 6:33，与本轮 r932→r933 间隔吻合，确认**同一进程持续在线未重启**。

## §2 MCP 握手（curl initialize，🚫 非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（HTTP 200，time_total=0.002802s）：
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools ..."}}
__HTTP=200 TIME=0.002802s
```

- **HTTP 码 = 200**
- **serverInfo** = `EDA-FastMCP-Flow` v1.25.0 ✓
- **protocolVersion** = `2024-11-05` ✓ 回显
- 无报错原文（无 JSON-RPC error、无 connection refused）。

## §3 open_session → run_commands → close（含耗时 + 返回前 200 字符）

四参齐全：`task_id="shardA-health-r933"` / `eval_id="designflow-healthcheck-20261121"` / `user="e0031982"` / `sample="ro_home"`（ro_home = 只读 home 目录，符合自检取值要求）。

### open_session — ok（21ms）
- 耗时：21ms
- 无 `Missing key` 报错（四参齐全）
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r933_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}`
- workdir = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r933_ro_home`

### run_commands — ok（wall 6947ms / cmd duration_ms=10）
- 命令：`echo ok; pwd; id -un </dev/null`（已加 `</dev/null` 防 ssh hang；本轮未用 ssh，无 hang 风险）
- wall 6947ms 偏高 = MCP 往返开销，cmd 自身仅 10ms（duration_ms=10）
- exit_code=0，timed_out=false，error_log 空
- stdout（前 200 字符）：
  `ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r933_ro_home\ne0031982\n`
  → `ok` / workdir 路径 / `e0031982`（id -un）三项齐全
- stderr 空

### close_session — ok（21ms）
- 耗时：21ms
- `cleaned=true`（workdir 已清理）

## §4 网络可达性（ip route get 10.129.32.75）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

`.75` 可达（via 10.251.36.1 dev bond0 src 10.251.36.15），非 NETBLOCK。

## §5 §三 OK 分支 — 本轮 0-case 说明

健康自检为最高优先用户令，已交付（全新 session 实测第 37 次复测，结论 EDA_FLOW_OK）。按 §三「OK ⇒ 本轮按 §6 转造题 1 条」尝试造题，但本轮 0-case，原因：

- 扫描快照与 r897-r932 同源（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，**无新 trace**）。
- `trace_ledger --shard A stats`：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），剩余可做 ≈2511；`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）。
- **A-pure fresh 池枯竭第 37 次确认**（r877 终证 / r883 / r885 / r897-r932 再确认）：
  - `pool_reaudit_A.tsv` "可造" 行（jeij7 r844 / plk7n r894 / bdhyb r895+r896）均已落库，台账陈旧但实际无未造可造候选。
  - ledger A parked 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）。
  - NOFILE 假阴性复活 r893-r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）。
- 余下预算不足以完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验）；质量硬要求禁 incomplete 入 jsonl，故不凑数。

## §6 体积

- TASK_A ≈ 41KB（接近 40KB 红线）
- MEMORY_A ≈ 85KB（超 32KB 红线，r897-r932 累积，结构性 DEBT）— 本 r933 **已执行归档瘦身**：将 r897-r932 共 36 条健康自检流水原文搬入 `ARCHIVE_OPERATOR_DESIGNFLOW.md`，MEMORY_A 仅保留 r933 + r932 单行指针 + r892 及之前的造题流水。
