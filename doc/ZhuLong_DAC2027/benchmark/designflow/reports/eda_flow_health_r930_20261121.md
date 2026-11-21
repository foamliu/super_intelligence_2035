# eda_flow MCP 健康自检 r930 · 2026-11-21

> 用户令（2026-11-21 最高优先）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 本轮 = 第 35 次复测（r897–r929 同令同日已三十四测，全新 agent session 实测）。

## §0 结论

**EDA_FLOW_OK** —— initialize / open_session / run_commands / close_session 全通。

| 项 | 结果 |
|:--|:--|
| 结论 | `EDA_FLOW_OK`（两者都通） |
| open_session | ok（70ms，四参齐全，无 Missing key） |
| run_commands | ok（57ms wall，3 cmd 各 duration_ms 4/0/25，全 exit 0，error_log 空） |
| close_session | ok（35ms，cleaned=true） |
| :18891 | listening（python pid=3365754，ELAPSED 24-21:15:21[etimes=2150121s]，与 r897–r929 同进程未重启） |
| curl initialize | HTTP 200 + serverInfo=EDA-MCP-SERVER v1.25.0 + protocolVersion 2024-11-05 |
| ip route 10.129.32.75 | 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013） |

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```
（:8651 / :8654 未监听；与 r897–r929 一致）

### 1.2 MCP initialize 握手（POST，非裸 GET）

```
$ curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
    -H 'Content-Type: application/json' \
    -H 'Accept: application/json, text/event-stream' \
    -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'

HTTP 200
```
返回体前 1200 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instructions":"## Available Skills\n\nThe following Skills are available. Use them when the task matches its description:\n\n- **eda-aether-init**: Ensure pyAether environment is activated before any EDA layout or design operations. This skill MUST be applied before generating any code that uses pyAether library.\n- **pyAether-mcp-safe-execution**: Safe code execution guidelines for pyAether MCP tool calls. Prevents Unicode/encoding errors when using run_code in Python 3.9 ASCII environment.\n- **eda-emydesign-attributes**: Guide for using emyDesign object properties and methods returned by aeGetCurDesign(). Essential for any EDA layout/schematic operations in Aether.\n- **eda-highlight-by-name-pattern**: 根据名称模式（前缀、后缀、包含、正则等）高亮当前Aether原理图中的线（net）或器件（instance）。适用于用户要求"高亮...的线"的场景。\n- **eda-snap-origin":...
```
- HTTP 码：**200**
- serverInfo：**有**（`EDA-MCP-SERVER v1.25.0`）
- 报错原文：无

### 1.3 open_session（70ms，四参齐全）

入参（按用户令自检取值，传 `{}` 会 Missing key）：
```json
{
  "task_id": "shardA-health-r930",
  "eval_id": "designflow-healthcheck-20261121",
  "user": "e0031982",
  "sample": "0"
}
```
返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r930_0","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- error_log：**空**（成功，无 Missing key）

### 1.4 run_commands（57ms wall，3 cmd）

命令（用户令指定：`echo ok; pwd; id -un`；本轮未用 ssh，无 hang 风险）：
```json
{
  "workdir": "/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r930_0",
  "commands": ["echo ok", "pwd", "id -un"]
}
```
返回（每个 CommandResult）：
| cmd | exit_code | stdout | stderr | duration_ms | timed_out |
|:--|--:|:--|:--|--:|:--|
| echo ok | 0 | `ok\n` | `` | 4 | false |
| pwd | 0 | `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r930_0\n` | `` | 0 | false |
| id -un | 0 | `e0031982\n` | `` | 25 | false |

- error_log：**空**
- response：`ran 3 command(s)`

### 1.5 close_session（35ms）

```
{"workdir":".../e0031982_designflow-healthcheck-20261121_shardA-health-r930_0","cleaned":true,"response":"session workdir cleaned","error_log":""}
```
- cleaned：**true**

## §2 §三 分支处置

按用户令 §三：`OK ⇒ 本轮按 §6 转造题 1 条`。

继承 r897–r929 三十四轮的结构性结论：
- 扫描快照同源（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）。
- ledger stats：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），剩余可做 ≈2511。
- `trace_ledger --shard A next` 仅回吐 scansync 命令模板，无 fresh 候选清单。
- A-pure fresh 池枯竭第 35 次确认（r877 终证 / r883 / r885 / r897–r929 再确认）：`pool_reaudit_A.tsv` "可造" 行（jeij7 r844 / plk7n r894 / bdhyb r895+r896）均已落库；台账陈旧但实际无未造可造候选；NOFILE 假阴性复活 r893–r896 已用尽。
- 本轮预算（健康自检令已交付）剩余不足以完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验）。
- 质量硬要求：禁 incomplete 入 jsonl，故不凑数。

**本轮 0-case**（与 r897–r929 同；非能力结论，infra 失败 ≠ 能力结论）。

## §3 结构性 DEBT 提示（供下轮归档）

- MEMORY_DESIGNFLOW_A.md ≈ **82KB**（远超 32KB 红线，r897–r929 累积重复健康自检流水所致）。
- TASK_A.md ≈ **41KB**（超 32KB 红线，红线 40KB）。
- 建议：将 r897–r928 的逐轮健康自检流水归档到 `ARCHIVE_OPERATOR_DESIGNFLOW.md`，仅在 MEMORY 顶部留指针 + 保留最近 2–3 轮流水。

## §4 一行 MEMORY

```
eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r930_20261121.md
```
