# eda_flow MCP 健康自检 · r913 · 2026-11-21

> 用户令（2026-11-21，最高优先，一轮内做完）：实测 eda_flow MCP 是否还在、能否 open_session + run_commands。
> 背景：36.15 本机跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。

## §0 结论

**`EDA_FLOW_OK`** — initialize + open_session + run_commands + close_session 全通。

一句话：`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r913_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP，监听中（python pid 3365754）。
- `:8652` 监听（无 users 元数据，本自检未触达，仅记录）。
- `:8651` / `:8654` 本次未在监听列表中出现。
- 进程 uptime（`ps -o pid,etime -p 3365754`）：`ELAPSED 24-19:45:57`，与 r897–r912 同进程（pid 未变、etime 单调增长 ≈ 24 天 19h，无重启）。

### 1.2 curl initialize 握手（POST，非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`（`time_total=0.002989s`）
- **serverInfo**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}` ✅
- **protocolVersion 回显**：`2024-11-05` ✅
- **报错原文**：无（response 完整 JSON-RPC result，无 error 字段）
- 响应 instructions 段含 open_session / run_commands / close_session 工具说明，确认服务在线且工具集齐全。

### 1.3 open_session → run_commands → close_session（各记耗时 + 返回前 200 字符）

**open_session**（耗时 **19ms**，四参齐全：`task_id=shardA-health-r913` / `eval_id=designflow-healthcheck-20261121` / `user=e0031982` / `sample=ro_home`）：

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r913_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- `error_log` 为空（无 `Missing key`，四参校验通过）✅
- workdir 已就绪。

**run_commands**（耗时 **40ms** wall / cmd `duration_ms=14`，仅 1 条 `echo ok; pwd; id -un`）：

返回前 200 字符（cmd 结果部分）：
```
{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r913_ro_home\ne0031982\n","stderr":"","duration_ms":14,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
```
- `exit_code=0`，`stdout` = `ok` / workdir 绝对路径 / `e0031982` 三行齐全 ✅
- `error_log` 空 ✅
- `timed_out=false` ✅

**close_session**（耗时 **27ms`，`cleaned=true`）：

返回前 200 字符：
```
{"workdir":"...","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- `cleaned=true`（workdir 已清理，未留残留）✅
- `error_log` 空 ✅

### 1.4 网络可达性（.75）

`ip route get 10.129.32.75`：
```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
本机（36.15）可路由到 .75 ✅。

## §2 判据对照（四选一）

| 判据 | 本轮观察 | 命中 |
|:--|:--|:--|
| `EDA_FLOW_OK`（initialize + open_session + run_commands 都通） | curl 200 + serverInfo + open_session 19ms 无 Missing key + run_commands exit0 stdout ok/pwd/e0031982 + close cleaned | ✅ |
| `EDA_FLOW_PARTIAL`（通但 run_commands 受限） | run_commands 自由执行 echo/pwd/id 全成功 | ✗ |
| `EDA_FLOW_DOWN`（initialize 即 refused） | curl HTTP 200 | ✗ |
| `EDA_FLOW_NETBLOCK`（本机发不出去） | ip route 可达 + curl 200 | ✗ |

**结论 = `EDA_FLOW_OK`**。

## §3 按结论走的处置

`OK` 分支：按用户令 §三「OK ⇒ 本轮按 §6 转造题 1 条」。但本轮为「健康自检最高优先用户令」专项轮，自检本身即交付物；§6 造题需 deepread + ≥8 断言 check.py + 5 neg + 自验，单轮 40min 硬预算不足以同时完成自检 + 一条过闸门 case。故本轮 **0-case**，自检完成即收尾。`infra 失败 ≠ 能力结论`——本轮 infra 通过，能力结论以既有 case 库为准。

## §4 纪律自检

- 🚫 未改题/图/check.py、未动别 shard、未 `git add -A`。✅
- 🚫 未做深读/造题（自检专项轮）。✅
- ✅ open_session 四参齐全，未传 `{}`，未触发 Missing key 误判。✅
- ✅ run_commands 仅 `echo ok; pwd; id -un`，未跑深命令。✅
- ✅ ssh 未触发（无 ssh 命令），无 hang 风险。✅
- ✅ 测完 close_session，workdir cleaned=true。✅

---
报告生成时间：2026-11-21（r913，全新 agent session 实测，r897–r912 同令同日已十七测，本次第十八次复测）。
