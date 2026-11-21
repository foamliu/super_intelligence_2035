# eda_flow MCP 健康自检报告 · r923 · 2026-11-21

> 用户令（最高优先）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 本轮为该令第二十八次复测（全新 agent session 实测，r897-r922 同令同日已二十七测）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 均通；:18891 listening；curl initialize HTTP 200 + serverInfo 回显；ip route 10.129.32.75 可达。

## §1 原始输出

### 1.1 本机端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP，python pid=3365754（与 r897-r922 同进程持续在线未重启；r922 时 ELAPSED 24-20:34:56[2147696s]，本轮 24-20:39:45[2147985s]，增长 ~4:49[289s] 吻合两次复测间隔）。
- `:8652` 监听中（无 users 标注，非本测试对象）。
- `:8651` / `:8654` 未监听。

### 1.2 MCP 握手 curl（initialize，非裸 GET）

```
HTTP_CODE=200
TIME_TOTAL=0.003173s
```

响应体（前 800 字符）：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instructions":"## Available Skills\n\nThe following Skills are available. Use them when the task matches their description:\n\n- **eda-aether-init**: Ensure pyAether environment is activated before any EDA layout or design operations. ...
```

- HTTP 200；有 `serverInfo`：`EDA-MCP-SERVER v1.25.0`；`protocolVersion` 2024-11-05 回显；无报错。

### 1.3 ip route（NETBLOCK 判据，本轮非阻塞故仅记录）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
```
本机 → `.75` 路由可达。

### 1.4 open_session（四参齐全）

```
耗时: 17ms
入参: task_id=shardA-health-r923 / eval_id=designflow-healthcheck-20261121 / user=e0031982 / sample=ro_home
返回(前600字符):
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r923_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- `response = session workdir ready`；`error_log` 空；**无 `Missing key`**（四参全部被接受）。
- workdir = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r923_ro_home`

### 1.5 run_commands（echo ok; pwd; id -un）

```
耗时: 24ms wall / 9ms cmd
返回(前800字符):
{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r923_ro_home\ne0031982\n","stderr":"","duration_ms":9,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
```
- 1 cmd exit_code=0；stdout = `ok` / workdir 路径 / `e0031982`；stderr 空；`timed_out=false`；`error_log` 空。⚠️ `ssh` 已加 `</dev/null` 防 hang（本轮未用 ssh，但按令保留习惯）。

### 1.6 close_session

```
耗时: 30ms
返回(前400字符):
{"workdir":"...","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- `cleaned=true`，session workdir 已清理。

## §2 结论分项

| 项 | 结果 |
|:--|:--|
| eda_flow 健康 | **EDA_FLOW_OK** |
| open_session | ok（17ms，四参齐，无 Missing key） |
| run_commands | ok（24ms wall / 9ms cmd，1cmd exit0，stdout ok/pwd/e0031982，error_log 空，timed_out=false） |
| close_session | ok（30ms，cleaned=true） |
| :18891 | listening（python pid3365754 ELAPSED 24-20:39:45[etimes=2147985s]，与 r897-r922 同进程持续在线未重启） |
| curl initialize | HTTP 200，serverInfo=EDA-MCP-SERVER v1.25.0，protocolVersion 2024-11-05 回显 |
| ip route .75 | 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013） |

## §3 OK 分支处置

§三令：`OK` ⇒ 本轮按 §6 转造题 1 条。本轮 0-case：扫描快照同 r897-r922（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）；ledger stats covered=400 / target=3164 (12.6%) 已动 657（case432 / parked285）剩余可做 ≈2511；`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）；A-pure fresh 池枯竭第二十八次确认（r877 终证 / r883 / r885 / r897-r922 再确认）—— `pool_reaudit_A.tsv` 唯一"可造" `jeij7` 经核验已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets+reference 齐全），该行未同步标"已造"属台账陈旧，实际无未造可造候选；余下预算不足完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5neg + 自验），质量硬要求禁 `incomplete` 入 jsonl，故不凑数。**infra 失败 ≠ 能力结论** —— 本轮 infra 全通，0-case 系选料枯竭而非 infra 阻塞。

## §4 纪律自检

- 🚫 未改题 / 图 / check.py / 别 shard 文件 / `git add -A`
- 🚫 未深读 / 造题（健康自检为最高优先用户令，测完 `close`）
- ✅ open_session 四参齐全（task_id / eval_id / user / sample）
- ✅ ssh 习惯加 `</dev/null`（本轮未用 ssh）
- ✅ close_session cleaned=true
