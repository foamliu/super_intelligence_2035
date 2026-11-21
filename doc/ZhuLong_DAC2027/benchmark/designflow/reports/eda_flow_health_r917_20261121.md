# eda_flow MCP 健康自检 · r917 · 2026-11-21

> 用户令（2026-11-21，最高优先，一轮内做完）：实测 eda_flow MCP 是否还在、能否 open_session + run_commands。
> 背景：36.15 本机跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。
> 本轮为同令第 22 次复测（全新 agent session 实测，r897–r916 同令同日已二十一测）。

## §0 结论

**`EDA_FLOW_OK`** — initialize + open_session + run_commands + close_session 全通。

一句话：`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r917_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP，监听中（python pid 3365754）。
- `:8652` 监听（无 users 元数据，本自检未触达，仅记录）。
- `:8651` / `:8654` 本次未在监听列表中出现。
- 进程 uptime（`ps -o pid,etime -p 3365754`）：`ELAPSED 24-20:07:38`，与 r897–r916 同进程（pid 未变、etime 单调增长，r916 时为 24-20:02:20，本轮增长 ≈5.3min 吻合，无重启）。

### 1.2 curl initialize 握手（POST，非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`（`time_total=0.003194s`）
- **serverInfo**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}` ✅
- **protocolVersion 回显**：`2024-11-05` ✅
- **报错原文**：无（response 完整 JSON-RPC result，无 error 字段）
- 响应 instructions 段含 open_session / run_commands / close_session 工具说明，确认服务在线且工具集齐全。

### 1.3 open_session → run_commands → close_session（各记耗时 + 返回前 200 字符）

**open_session**（耗时 **20ms**，四参齐全：`task_id=shardA-health-r917` / `eval_id=designflow-healthcheck-20261121` / `user=e0031982` / `sample=ro_home`）：

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r917_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- `error_log` 为空（无 `Missing key`，四参校验通过）✅
- workdir 已就绪。

**run_commands**（耗时 **30ms** wall（MCP 往返）/ cmd `duration_ms=10`，仅 1 条 `echo ok; pwd; id -un`）：

返回前 200 字符（cmd 结果部分）：
```
{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r917_ro_home\ne0031982\n","stderr":"","duration_ms":10,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
```
- `exit_code=0`，`stdout` = `ok` / workdir 绝对路径 / `e0031982` 三行齐全 ✅
- `stderr` 空、`timed_out=false`、`error_log` 空 ✅

**close_session**（耗时 **27ms**）：

返回前 200 字符：
```
{"workdir":"...r917_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- `cleaned=true` ✅（workdir 已清理，session 闭环）

### 1.4 网络可达性（佐证）

`ip route get 10.129.32.75`：
```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
- 本机（36.15）→ .75 路由可达，无 NETBLOCK。

## §2 结论判据核对

| 判据 | 结果 |
|:--|:--|
| `:18891` 监听 | ✅ listening（python pid 3365754） |
| curl initialize HTTP 200 + serverInfo | ✅ 200 + EDA-FastMCP-Flow v1.25.0 |
| open_session 四参齐全无 Missing key | ✅ 20ms，error_log 空 |
| run_commands 真跑 exit 0 | ✅ 30ms wall / 10ms cmd，stdout=ok/pwd/e0031982 |
| close_session cleaned | ✅ 27ms，cleaned=true |
| .75 路由可达 | ✅ via 10.251.36.1 dev bond0 |

→ 四选一结论：**`EDA_FLOW_OK`**（两者都通）。

## §3 按结论走

OK 分支已确认。本轮按 §6 应转造题 1 条，但实测：

- **ledger `next --n 3` 仅回吐 scansync 命令模板**（无 fresh 候选清单）—— A-pure fresh 池枯竭第 22 次确认（r877 终证 / r883 / r885 / r897–r916 再确认）。
- `pool_reaudit_A.tsv` 唯一「可造」jeij7（e0039102@hfeg0pbn16 mc143 verification）已于 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets + reference 齐全），该行未同步标「已造」属台账陈旧，故 pool_reaudit 无未造可造候选。
- ledger A parked 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold），NOFILE 假阴性复活 r893–r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）。
- 扫描快照同 r897–r916（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）。
- 余下预算不足完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验），质量硬要求禁 `incomplete` 入 jsonl，故不凑数。

本轮 **0-case**：健康自检为最高优先用户令已交付（全新 session 实测第 22 次复测），并非能力结论（§4 纪律：infra 失败 ≠ 能力结论；本轮 infra 实为 OK，0-case 系选料枯竭 + 预算不足，非判分/能力问题）。

## §4 纪律自检

- 🚫 未改题 / 图 / check.py
- 🚫 未动别 shard（MEMORY_B/C/D、ledger_B/C/D、jsonl_B/C/D）
- 🚫 未 `git add -A`
- ✅ open_session 传四参（避免 D 线 r1037 `Missing key` 误判）
- ✅ run_commands 仅 `echo ok; pwd; id -un`（只读 home 目录级）
- ✅ 测完即 `close_session`（cleaned=true）
- ✅ ssh 未触达（本轮无 ssh 调用，无需 `</dev/null`）
