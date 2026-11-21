# eda_flow MCP 健康自检 · r905 · 2026-11-21

> 最高优先用户令（2026-11-21）·「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 全新 agent session 实测第 9 次（r897/r898/r899/r900/r901/r902/r903/r904 同令同日已八测，本 r905 为第 9 测）

## §0 结论

**`EDA_FLOW_OK`** — open_session 与 run_commands 均通。

- open_session = **ok**（0.024s，四参齐全 task_id/eval_id/user/sample，无 `Missing key`）
- run_commands = **ok**（0.176s，3 cmd 全 exit 0，stdout = `ok` / pwd / `e0031982`，error_log 空）
- close_session = **ok**（0.033s，cleaned=true）
- `:18891` = **listening**（python pid=3365754，etime 24-19:03:28，与 r897-r904 同进程持续在线未重启）
- curl initialize = **HTTP 200** + `serverInfo=EDA-FastMCP-Flow v1.25.0` + `protocolVersion 2024-11-05` 回显
- ip route 10.129.32.75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

按 §三 OK 分支：本轮可转造题；实际 0-case 原因见 §四。

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP 入口，python pid=3365754 在线
- `:8652` = 旁路监听（非本次判定对象）
- `:8651` / `:8654` = 未监听（无 match）

### 1.2 进程 uptime（pid 3365754）

```
3365754 24-19:03:28 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```

- etime = 24 天 19 小时 03 分 28 秒
- 与 r904（24-18:57:08）相差 ~6min20s，吻合单进程持续在线、未重启

### 1.3 ip route 10.129.32.75

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

- .75 可达（via 10.251.36.1 dev bond0，src 10.251.36.15 = 本机 36.15）

### 1.4 curl initialize 握手（HTTP 码 / serverInfo / 报错原文）

请求：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

响应（前 2000 字符，截取关键段）：
```json
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2024-11-05",
    "capabilities": {
      "experimental": {},
      "prompts": {"listChanged": false},
      "resources": {"subscribe": false, "listChanged": false},
      "tools": {"listChanged": false}
    },
    "serverInfo": {
      "name": "EDA-FastMCP-Flow",
      "version": "1.25.0"
    },
    "instructions": "# EDA FastMCP Flow — Design-Flow EDA Agent Tools ..."
  }
}
```

- **HTTP 码 = 200**（curl -w 回显 `---HTTP_CODE:200 TIME:0.003xxx s---`）
- **serverInfo 存在**：`name=EDA-FastMCP-Flow`, `version=1.25.0`
- **protocolVersion 回显**：`2024-11-05`（与请求一致）
- **报错原文**：无（无 error 字段，无 stderr）

### 1.5 open_session（耗时 + 返回前 200 字符）

调用（四参齐全，🚫 不传 `{}`）：
```
task_id   = "shardA-health-r905"
eval_id   = "designflow-healthcheck-20261121"
user      = "e0031982"
sample    = "ro_home"
```

- **耗时**：0.024s（24ms）
- **error_log**：`""`（空 ⇒ 无 `Missing key`，四参被正确接收）
- **返回前 200 字符**：
  ```
  workdir=/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r905_ro_home
  response=session workdir ready
  error_log=
  ```

### 1.6 run_commands（耗时 + 返回前 200 字符）

命令序列（只读自检，ssh hang 已规避，本组不含 ssh）：
```
echo ok
pwd
id -un
```

- **耗时**：0.176s（176ms，3 cmd 串行）
- **error_log**：`""`（空）
- **逐 cmd 结果**：

| cmd | exit_code | stdout | stderr | duration_ms |
|:--|:--|:--|:--|:--|
| `echo ok` | 0 | `ok\n` | `` | 2 |
| `pwd` | 0 | `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r905_ro_home\n` | `` | 1 |
| `id -un` | 0 | `e0031982\n` | `` | 144 |

- **返回前 200 字符**：`ran 3 command(s)` + 上述 results，error_log 空。

### 1.7 close_session（耗时 + 返回前 200 字符）

- **耗时**：0.033s（33ms）
- **cleaned**：`true`
- **返回前 200 字符**：`session workdir cleaned`，error_log 空。

## §2 四选一结论矩阵

| 结论 | 判据 | 本轮 |
|:--|:--|:--|
| `EDA_FLOW_OK` | open_session + run_commands 均通 | ✅ **本轮结论** |
| `EDA_FLOW_PARTIAL` | 通但 run_commands 受限 | |
| `EDA_FLOW_DOWN` | initialize 即 refused | |
| `EDA_FLOW_NETBLOCK` | 本机发不出去 | |

## §3 MEMORY 一行（首行）

```
eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r905_20261121.md
```

## §4 §三 OK 分支处置：本轮 0-case 说明

按 §三 OK 分支应「转造题 1 条」，但本轮实际 **0-case**，理由（同 r897-r904，扫描口径未变）：

1. **扫描快照与 r897-r904 同源**：`ssh_eda_search_20261121_005100`（mc10=3164，dedup 3846），无新 trace 进入候选池。
2. **A-pure fresh 池枯竭第 11 次确认**（r877 终证 / r883 / r885 / r897-r904 再确认 / r905 再确认）：
   - `pool_reaudit_A.tsv` 唯一"可造" `jeij7`（e0039102@hfeg0pbn16 mc143 verification）已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets + reference 齐全），该行未同步标"已造"属台账陈旧，实际无未造可造候选。
   - ledger A parked 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）。
   - NOFILE 假阴性复活机会 r893-r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）。
3. **预算不足**：剩余 ~30min 不够完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验 + pi 实跑）。
4. **质量硬要求禁 incomplete 入 jsonl**，故不凑数。

健康自检为最高优先用户令，已交付（全新 session 实测第 9 次复测）。`eda_flow 健康 = EDA_FLOW_OK`，下游造题无 infra 阻塞，仅因选料池枯竭 + 预算不足本轮 0-case。

## §5 纪律自检

- 🚫 不改题 / 图 / check.py — 未触碰
- 🚫 不动别 shard — 未触碰
- 🚫 不 `git add -A` — 仅 add 本 shard 文件
- ✅ open_session 传四参（非 `{}`）— 已遵守
- ✅ run_commands 只跑 `echo ok; pwd; id -un` — 已遵守
- ✅ 测完 `close`（cleaned=true）— 已遵守
- ✅ ssh hang 规避：本组自检不含 ssh，无需 `</dev/null`
- ✅ infra 失败 ≠ 能力结论：本轮 infra 全通，0-case 来自选料池 + 预算，非 infra
