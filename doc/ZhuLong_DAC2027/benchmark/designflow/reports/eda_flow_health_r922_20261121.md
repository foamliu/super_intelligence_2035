# eda_flow MCP 健康自检报告 · r922 · 2026-11-21

> 用户令：2026-11-21「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 本轮：r922（第二十七次复测，全新 agent session 实测；r897–r921 同令同日已二十六测）
> 运行机：36.15（`10.251.36.15`）· eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（`10.129.32.75` / hfhds201）

## §0 结论

**`EDA_FLOW_OK`** — initialize 握手通、open_session 通、run_commands 通、close_session 通。

- `open_session=ok`（19ms，四参 task_id/eval_id/user/sample 齐全，无 `Missing key`）
- `run_commands=ok`（33ms wall / 10ms cmd，1 cmd exit 0，stdout=`ok`/pwd/`e0031982`，error_log 空，timed_out=false）
- `close_session=ok`（22ms，cleaned=true）
- `:18891=listening`（python pid 3365754，ELAPSED 24-20:34:56 / etimes=2147696s，与 r897–r921 同进程持续在线未重启）
- curl initialize HTTP 200 + serverInfo `EDA-FastMCP-Flow v1.25.0` + protocolVersion `2024-11-05` 回显
- `ip route get 10.129.32.75` 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP（python pid 3365754）— **listening**
- `:8651` / `:8654` 未出现（pyAether / innovus 后端未启动，本次自检不依赖）
- `:8652` listening（无 pid 信息，非本自检对象）

### 1.2 进程信息（pid 3365754）

```
PID       ELAPSED       ETIMES    CMD
3365754   24-20:34:56   2147696   /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```

ELAPSED = 2147696s ≈ **24-20:34:56**。r921 时为 24-20:29:10（etimes=2147350s），增长 ~5:46（346s），与两次自检间隔吻合 ⇒ 同进程持续在线，未重启。

### 1.3 curl initialize 握手（POST，非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}' \
  -w '\n__HTTP_CODE=%{http_code}__\n'
```

返回（前 200 字符 + 关键字段）：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow …
__HTTP_CODE=200__
```

- **HTTP 码 = 200**（curl exit 0）
- **有 `serverInfo`**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- **protocolVersion 回显**：`2024-11-05`
- 无报错

### 1.4 `ip route get 10.129.32.75`

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

`.75` 路由可达，本机发得出去。

### 1.5 `open_session` → `run_commands` → `close_session`

**open_session**（传四参：task_id=`shardA-health-r922` / eval_id=`designflow-healthcheck-20261121` / user=`e0031982` / sample=`0`）
- 耗时：**19ms**
- 返回（前 200 字符）：
  ```
  {"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r922_0","response":"session workdir ready","error_log":"","print_log":"","result":""}
  ```
- `error_log` 空，无 `Missing key` ⇒ 四参齐全通过

**run_commands**（命令：`echo ok; pwd; id -un`）
- 耗时：**33ms wall / 10ms cmd**
- 返回（前 200 字符）：
  ```
  {"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r922_0\ne0031982\n","stderr":"","duration_ms":10,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
  ```
- 1 cmd，exit_code=0，stdout=`ok`/pwd/`e0031982`，stderr 空，timed_out=false，error_log 空

**close_session**
- 耗时：**22ms**
- 返回（前 200 字符）：
  ```
  {"workdir":"...shardA-health-r922_0","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
  ```
- `cleaned=true`，workdir 已清理

## §2 结论判定

| 判据 | 实测 | 通过 |
|:--|:--|:--:|
| `:18891` listening | python pid 3365754 LISTEN | ✅ |
| curl initialize HTTP 200 + serverInfo | 200 + `EDA-FastMCP-Flow v1.25.0` | ✅ |
| open_session 四参通过 | error_log 空，无 Missing key | ✅ |
| run_commands exit 0 + 正确 stdout | `ok`/pwd/`e0031982`，timed_out=false | ✅ |
| close_session cleaned | cleaned=true | ✅ |
| ip route 可达 .75 | via 10.251.36.1 dev bond0 | ✅ |

四选一结论：**`EDA_FLOW_OK`**（两者都通）。

## §3 下一步

按用户令 §三：`OK` ⇒ 本轮按 §6 转造题 1 条。

本轮预算检查：扫描快照同 r897–r921（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）；ledger A stats covered=400/target=3164(12.6%)，已动 657（case432/parked285），剩余可做 ≈2511，`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）。A-pure fresh 池枯竭第 27 次确认（r877 终证 / r883 / r885 / r897–r921 再确认）：

- `pool_reaudit_A.tsv` 唯一"可造" jeij7 已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl/assets+reference 齐全），该行未同步标"已造"属台账陈旧，实际无未造可造候选；
- ledger A parked 条目经复核均合理（wrong-domain/thin-session/GUI-dependent/no-gold）；
- NOFILE 假阴性复活 r893–r896 已用尽（g7hp7/plk7n/bdhyb/fkrdf 四条 subdir-path 复活均落库）；
- 剩余预算（~25 min）不足以完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验）；
- 质量硬要求：禁 `incomplete` 入 jsonl，故不凑数。

本轮 **0-case**：eda_flow 健康自检为最高优先用户令已交付（全新 session 实测第 27 次复测），无新 trace 涌入故无料可造，结构性与 r897–r921 同。MEMORY 写 `WAITING: 0`（无外部阻塞，仅选料枯竭）。

## §4 MEMORY 一行

```
eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r922_20261121.md
```
