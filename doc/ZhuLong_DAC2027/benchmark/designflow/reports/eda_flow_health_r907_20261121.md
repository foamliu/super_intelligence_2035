# eda_flow MCP 健康自检 r907 · 2026-11-21

> 用户令（2026-11-21 最高优先）：designflow A 实测 eda_flow MCP 是否还在、open_session/run_commands 是否可用。
> 背景：36.15 跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（10.129.32.75 / hfhds201）。
> 本轮为全新 agent session 第 11 次复测（r897/r898/r899/r900/r901/r902/r903/r904/r905/r906 同令同日已十测）。

## §0 结论

**`EDA_FLOW_OK`** — open_session 与 run_commands 两者都通。

- `open_session=ok` · `run_commands=ok` · `:18891=listening`
- 报告路径：`designflow/reports/eda_flow_health_r907_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` 监听中（python pid=3365754，与 r897–r906 同进程持续在线未重启；ELAPSED 估算 ~24-19:13:xx）。
- `:8652` 监听中（无 users 字段，非本次关注）。
- `:8651` / `:8654` 无监听（与 r897–r906 一致）。

### 1.2 握手（initialize，🚫 未 curl 裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（前 200 字符 + 关键字段）：
- **HTTP 码**：`HTTP 200`（`time_total=0.003103s`）
- **`serverInfo`**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- **`protocolVersion`** 回显：`2024-11-05`
- **`capabilities`**：`prompts` / `resources` / `tools` 均回显
- **报错原文**：无（response 完整，无 error 字段）

响应体节选：
```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow ..."}}
```

### 1.3 `open_session → run_commands → close_session`（各记耗时 + 返回前 200 字符）

**open_session（0.029s）** — 四参齐全，无 Missing key：
```
task_id  = shardA-health-r907
eval_id  = designflow-healthcheck-20261121
user     = e0031982
sample   = ro_home
```
返回（前 200 字符）：
```
workdir = /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r907_ro_home
response = "session workdir ready"
error_log = ""   (空 = 成功，无 Missing key)
```

**run_commands（0.043s）** — 仅跑 `echo ok; pwd; id -un`（只读，3 cmd 全 exit 0，error_log 空）：
```
cmd[0] echo ok    : exit 0, stdout="ok\n",           stderr=""
cmd[1] pwd        : exit 0, stdout="<workdir>\n",    stderr=""
cmd[2] id -un     : exit 0, stdout="e0031982\n",     stderr=""
response = "ran 3 command(s)"
error_log = ""   (空 = 无受限)
```

**close_session（0.021s）**：
```
cleaned  = true
response = "session workdir cleaned"
error_log = ""
```

### 1.4 网络可达性（补充证据）

```
$ ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
本机（36.15 / 10.251.36.15）可经 `10.251.36.1` 到达 `.75`，无 NETBLOCK。

## §2 §三 分支处置

结论 = `EDA_FLOW_OK` ⇒ 按令「本轮按 §6 转造题 1 条」。

**但本轮实际 0-case**，原因（与 r897–r906 同，已 11 次复核）：

1. **扫描快照无变化**：`ssh_eda_search_20261121_005100`（最新，11-21 00:51，5434 行 summary.tsv）与 r897–r906 同源，**无新 trace**。
2. **A-pure fresh 池枯竭第 13 次确认**（r877 终证 / r883 / r885 / r897–r906 再确认）：
   - `pool_reaudit_A.tsv` 唯一标「可造」的 `jeij7`（e0039102@hfeg0pbn16, mc143, verification）已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets / reference 齐全），该行未同步标「已造」属台账陈旧，**实际无未造可造候选**。
   - ledger A parked 条目经复核均合理 parked（wrong-domain / thin-session / GUI-dependent / no-gold）。
   - NOFILE 假阴性复活机会 r893–r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）。
3. **预算不足**：剩余 ~30 min 不够完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验 + hidden B）。
4. **质量硬要求**：禁 `incomplete` 入 jsonl，故不凑数。

> ⚠️ infra 失败 ≠ 能力结论。本轮 infra = OK，0-case 是选料枯竭 + 预算不足，**非 eda_flow 故障**。

## §3 备注

- eda_flow session r907 cleaned（`cleaned=true`），未留残留。
- 健康自检为本次最高优先用户令，已实测交付（全新 session 第 11 次复测）。
- 建议运维侧：若需进一步验证，可重跑 `ssh_eda_search` 全量扫描以确认是否有新会话涌现（当前快照 11-21 00:51 至今 ~12h 未更新）。
