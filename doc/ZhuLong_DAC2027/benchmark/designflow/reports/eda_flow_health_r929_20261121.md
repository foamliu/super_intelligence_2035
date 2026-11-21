# eda_flow MCP 健康自检 · r929 · 2026-11-21

> 用户令（2026-11-21 最高优先）：实测 eda_flow MCP 是否还在、能否 open_session + run_commands。
> 本轮为全新 agent session 第 **34** 次复测（r897–r928 同令同日已 33 测，均 EDA_FLOW_OK）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 均通，:18891 listening，curl initialize HTTP 200 回显 serverInfo，ip route 可达 .75。

- `open_session` = ok（四参齐全，无 Missing key）
- `run_commands` = ok（3 cmd 全 exit0，stdout 正确，error_log 空）
- `:18891` = listening（python pid 3365754，与 r897–r928 同进程持续在线未重启）
- 报告路径 = `designflow/reports/eda_flow_health_r929_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP 主端口，监听进程 `python pid=3365754`
- `:8652` 监听（无 users 信息，系统级 socket）
- `:8651` / `:8654` 本轮未监听（与 r897–r928 一致，非本轮所需）

进程 ELAPSED：
```
PID 3365754  ELAPSED 24-21:10:08  ETIMES 2149808
/nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python .../eda_fastmcp_flow/main.py
```
r928 时为 `24-21:04:20`（etimes=2149460s），增长 ~5:48（348s），与本轮间隔（14:07 → 14:11 ≈ 4min）吻合 ⇒ **同进程未重启**。

### 1.2 握手（curl initialize，🚫 非 GET）

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 200**（`curl: (23) Failure writing output to destination` 是 `-o` 重定向的尾部 pipe 噪声，body 已完整捕获到 /tmp/mcp_init.txt，非网络错误）
- **有 serverInfo**：`"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"}`
- protocolVersion 回显 `2024-11-05` ✓
- capabilities 回显 `tools/prompts/resources` ✓
- 无 JSON-RPC error

返回前 200 字符：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instruct
```

### 1.3 open_session → run_commands → close 各耗时 + 返回前 200 字符

四参（按令二）：
- `task_id = "shardA-health-r929"`
- `eval_id = "designflow-healthcheck-20261121"`
- `user = "e0031982"`
- `sample = "0"`（只读 home 目录口径，与 r928 一致）

**open_session（29 ms）**：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r929_0","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- error_log 空 ✓，无 `Missing key` ✓
- workdir 路径含 user/eval_id/task_id/sample 四元，符合 §二去重布局

**run_commands（28 ms wall；3 cmd 各 duration_ms 2/1/7）**：
命令 `["echo ok", "pwd", "id -un"]`（🚫 ssh hang 风险：本轮未用 ssh，无需 `</dev/null`）。
```
results[0]: cmd="echo ok"      exit_code=0 stdout="ok\n"                          stderr="" duration_ms=2 timed_out=false
results[1]: cmd="pwd"          exit_code=0 stdout="/proj/.../sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r929_0\n" stderr="" duration_ms=1 timed_out=false
results[2]: cmd="id -un"       exit_code=0 stdout="e0031982\n"                    stderr="" duration_ms=7 timed_out=false
response="ran 3 command(s)"  error_log=""  files={}
```
- 3 cmd 全 exit0 ✓，stdout 依次为 `ok` / workdir 绝对路径 / `e0031982`（与 §四 user 身份一致）✓
- error_log 空 ✓，无 timed_out ✓

**close_session（20 ms）**：
```
{"workdir":".../e0031982_designflow-healthcheck-20261121_shardA-health-r929_0","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- cleaned=true ✓（workdir 已 rm）

### 1.4 ip route 可达性（NETBLOCK 判据备用）

```
ip route get 10.129.32.75
→ 10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
```
本机 10.251.36.15 → .75 路由可达，非 NETBLOCK。

## §2 §三 OK 分支后续动作

按令三 `OK ⇒ 本轮按 §6 转造题 1 条`，本轮已尝试转造题，结果 **0-case**（同 r897–r928）：

- 扫描快照同 r897–r928：`ssh_eda_search_20261121_005100`，`mc10=3164`，`updated_at=2026-11-21 03:19`，无新 trace。
- `trace_ledger --shard A stats`：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），剩余可做 ≈2511。
- `trace_ledger --shard A next --n 3`：仅回吐 scansync 命令模板，**无 fresh 候选清单**。
- A-pure fresh 池枯竭第 **34** 次确认（r877 终证 / r883 / r885 / r897–r928 再确认）：
  - `pool_reaudit_A.tsv` 唯一"可造"候选 `jeij7`（e0039102@hfeg0pbn16 mc143 verification）已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRedrDriverGenProduce-001`（A.jsonl / assets+reference 齐全），该行未同步标"已造"属台账陈旧。
  - 其余 pool_reaudit "可造" 行（`plk7n` r894、`bdhyb` r895+r896 sister）均已落库。
  - 台账 A `parked` 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）。
  - NOFILE 假阴性复活 r893–r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）。
- A.jsonl 当前 433 行（case 432 + header）。
- 质量硬要求禁 `incomplete` 入 jsonl，故不凑数。

## §3 结构性 DEBT

MEMORY_A ≈ 75 KB（超 32 KB 红线，r897–r928 累积）。归档（搬 r897–r920 原文至 ARCHIVE_OPERATOR_DESIGNFLOW.md）持续被健康自检轮占用未做，标记为下轮归档目标。TASK_A ≈ 40 KB（红线 40 KB，临边）。
