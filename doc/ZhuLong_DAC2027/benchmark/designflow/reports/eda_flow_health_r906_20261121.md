# eda_flow MCP 健康自检 · r906 · 2026-11-21

> 全新 agent session 实测（同令第十次复测；r897/r898/r899/r900/r901/r902/r903/r904/r905 同令同日已九测）。
> 用户令：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」

## §0 结论

**`EDA_FLOW_OK`** — open_session 与 run_commands 均通。

- open_session=ok（0.022s，四参齐全：task_id=`shardA-health-r906` / eval_id=`designflow-healthcheck-20261121` / user=`e0031982` / sample=`ro_home`，无 `Missing key`）
- run_commands=ok（0.060s，3 cmd 全 exit 0，stdout=`ok` / pwd / `e0031982`，error_log 空）
- close_session=ok（0.015s，cleaned=true）

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*  users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP 主端口，**listening**（python pid 3365754）
- `:8652` = listening（无 users 标注，进程归属未识别，非本自检对象）
- `:8651` / `:8654` = 未监听（无匹配行）

进程 ELAPSED（pid 3365754）：

```
PID    ELAPSED      CMD
3365754 24-19:08:32  /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```

与 r897–r905 同进程持续在线（r905 为 `24-19:03:28`，本测 `24-19:08:32`，增长 ~5 min 吻合时间推进，**未重启**）。

### 1.2 握手 curl initialize（HTTP 码 / serverInfo / 报错原文）

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`
- **time_total**：0.002961 s
- **serverInfo**：`{"name":"EDA-MCP-SERVER","version":"1.25.0"}` ✓ 存在
- **protocolVersion 回显**：`2024-11-05` ✓
- **报错原文**：无（无 error 字段，result 正常返回）
- 回显节选（前 600 字符）：
  ```
  {"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instructions":"## Available Skills\n\nThe following Skills are available...
  ```

### 1.3 open_session → run_commands → close_session 各耗时 + 返回前 200 字符

**open_session**（耗时 0.022 s，返回前 200 字符）：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r906_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- workdir = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r906_ro_home`
- error_log = ``（空，无 `Missing key`）
- 四参齐：task_id=`shardA-health-r906` / eval_id=`designflow-healthcheck-20261121` / user=`e0031982` / sample=`ro_home`

**run_commands**（耗时 0.060 s，返回前 200 字符）：
```
{"results":[{"cmd":"echo ok","exit_code":0,"stdout":"ok\n","stderr":"","duration_ms":1,"timed_out":false},{"cmd":"pwd","exit_code":0,"stdout":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r906_ro_home\n","stderr":"","duration_ms":0,"timed_out":false},{"cmd":"id -un","exit_code":0,"stdout":"e0031982\n","stderr":"","duration_ms":42,"timed_out":false}],"files":{},"workdir":"...","response":"ran 3 command(s)","error_log":"","print_log":"","result":""}
```
- 3 cmd 全 exit_code=0
- stdout：`ok` / workdir 绝对路径 / `e0031982`
- error_log = ``（空）

**close_session**（耗时 0.015 s，返回前 200 字符）：
```
{"workdir":"...","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- cleaned=true，workdir 已清理

### 1.4 ip route get 10.129.32.75（NETBLOCK 判据备查）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
- 本机（10.251.36.15）→ .75（10.129.32.75）路由可达，via 10.251.36.1 dev bond0。

## §2 分支处置

§三 OK 分支已确认。本轮 0-case：健康自检为 2026-11-21 最高优先用户令已交付（全新 session 实测第十次复测）。扫描快照与 r897–r905 同源（`ssh_eda_search_20261121_005100`，mc10=3164，无新 trace）；A-pure fresh 池枯竭第 12 次确认（r877 终证 / r883 / r885 / r897–r905 再确认）。质量硬要求禁 incomplete 入 jsonl，剩余预算不足完成 1 条过闸门 case，故不凑数。

## §3 备忘

- eda_flow session r906 已 cleaned（cleaned=true）。
- 与 r897–r905 一致：MCP 服务进程 pid 3365754 自 r897 起持续在线未重启，稳定性良好。
- 本轮为同令第十次复测；如需进一步造题请确认是否切换产出方向（如重启全量扫描 / 转其他 domain）。
