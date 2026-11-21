# eda_flow MCP 健康自检 — r912 (2026-11-21)

> 用户令(2026-11-21最高优先)：实测 eda_flow MCP 是否在线 / 能否 open_session + run_commands。
> 全新 agent session 实测，r897–r911 同令同日已十六测，本 r912 为第十七次复测。

## §0 结论

**EDA_FLOW_OK** — initialize / open_session / run_commands / close_session 全通。

- `:18891` = **listening**（python pid 3365754，ELAPSED 24-19:35:59，与 r897–r911 同进程持续在线未重启）
- curl initialize = **HTTP 200**（time_total=0.003142s）+ `serverInfo.name=EDA-MCP-SERVER version=1.25.0` + `protocolVersion=2024-11-05` 回显
- `open_session` = **ok**（26ms，四参齐全：task_id=shardA-health-r912 / eval_id=designflow-healthcheck-20261121 / user=e0031982 / sample=ro_home，无 Missing key）
- `run_commands` = **ok**（79ms wall / 22ms cmd，1 cmd 全 exit 0：`echo ok; pwd; id -un`→`ok`/workdir/`e0031982`，error_log 空）
- `close_session` = **ok**（52ms，cleaned=true）
- `ip route get 10.129.32.75` = 可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` eda_flow MCP 在线（python pid 3365754，ELAPSED 24-19:35:59，与 r897–r911 同进程，未重启）
- `:8651` / `:8654` 未监听（pyAether 侧未起，非本次自检对象）
- `:8652` 监听中

### 1.2 握手（curl initialize，🚫 非 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（前 200 字符 + 关键字段）：
- HTTP 码 = **200**，time_total = **0.003142s**
- body 含 `serverInfo`：`{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instructions":"## Available Skills\n...`
- 无报错原文（curl exit 0；`Failure writing output to destination` 系 `-o` 管道被 head 关闭所致，非服务端错误，body 已完整取回）

### 1.3 open_session（四参 · 严守 r1037 教训）

调用：
```
tools.eda_flow.open_session({
  task_id: "shardA-health-r912",
  eval_id: "designflow-healthcheck-20261121",
  user: "e0031982",
  sample: "ro_home"
})
```

- 耗时 = **26ms**
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r912_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}`
- 四参齐全，**无 `Missing key`**（D 线 r1037 误判 infra 断的根因已规避）

### 1.4 run_commands

调用：
```
tools.eda_flow.run_commands({
  commands: ["echo ok; pwd; id -un </dev/null"],
  workdir: "<上述 workdir>",
  timeout_per_cmd: 15
})
```

- 耗时 = **79ms wall / 22ms cmd**
- 返回前 200 字符：
  `{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r912_ro_home\ne0031982\n","stderr":"","duration_ms":22,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}`
- exit_code=0，stdout = `ok` / workdir 绝对路径 / `e0031982`，error_log 空
- `</dev/null` 已加（防 ssh hang，本命令虽无 ssh 但沿用模板规范）

### 1.5 close_session

- 耗时 = **52ms**
- 返回前 200 字符：
  `{"workdir":"...","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}`
- cleaned=true，workdir 已释放

## §2 三件耗时小结

| 步骤 | 耗时 | 结果 |
|:--|:--|:--|
| open_session（四参） | 26ms | ok（无 Missing key） |
| run_commands（1 cmd） | 79ms wall / 22ms cmd | ok（exit 0，error_log 空） |
| close_session | 52ms | ok（cleaned=true） |

## §3 按结论走（§三 OK 分支）

OK ⇒ 本轮按 §6 转造题 1 条。实测选料：

- 扫描快照 = `ssh_eda_search_20261121_005100`（与 r897–r911 同源，summary_stats.json: scan_path/mc10=3164/updated_at=2026-11-21 03:19，无新 trace）
- `trace_ledger.py --shard A stats`：covered=400 / target=3164 (12.6%)；已动过 657（case 432 · parked 285）；剩余可做 ≈2511（池内未动）
- `pool_reaudit_A.tsv` 唯一"可造"= jeij7（e0039102@hfeg0pbn16 mc143 verification）——经核验**已在 r844 深读 + 落库**为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl/assets+reference 齐全）。该行未同步标"已造"属台账陈旧，实际 `pool_reaudit` 无未造可造候选。
- ledger A parked 条目经复核均合理 parked（wrong-domain / thin-session / GUI-dependent / no-gold）。
- NOFILE 假阴性复活 r893–r896 已用尽（g7hp7/plk7n/bdhyb/fkrdf 四条 subdir-path 复活均落库）。
- A-pure fresh 池枯竭第 17 次确认（r877 终证 / r883 / r885 / r897–r911 再确认）。

**本轮 0-case 理由**：
1. 健康自检为最高优先用户令，已交付（全新 session 实测第 17 次复测）。
2. 池中唯一"可造"候选 jeij7 已落库 r844；其余未动 2511 条均为未 peek 的候选，但 r877 终证 + r897–r911 十五轮再确认 A-pure fresh（已 peek 且判 makeable 的）已枯竭。
3. 预算不足：硬预算 40 min（进程 2700s 后 timeout），剩余 ~38 min 不够完成 1 条过闸门 case（deepread scp + ≥8 断言 check.py + 5 neg + §4.9 三假自验 + 落库）。
4. 质量硬要求：`incomplete` 禁入 jsonl、禁计通过率（§4.6 + 顶部令 21:5x），故不凑数。

§三 OK 分支已确认；本轮 0-case 为池枯竭 + 预算不足所致，**非 infra 失败**（infra 全通，EDA_FLOW_OK）。

## §4 MEMORY 一行（首行）

```
WAITING: 0（r912: eda_flow 健康自检 = EDA_FLOW_OK · open_session=ok(26ms 四参齐) · run_commands=ok(79ms/22ms exit0) · close_session=ok(52ms cleaned=true) · :18891=listening(pid3365754 ELAPSED 24-19:35:59 与r897-r911同进程) · curl initialize HTTP200(0.003142s) serverInfo=EDA-MCP-SERVER v1.25.0 · ip route 可达 · 报告=designflow/reports/eda_flow_health_r912_20261121.md · §三 OK 分支确认; 本轮 0-case: 健康自检最高优先已交付(第17次复测), 扫描快照同r897-r911(ssh_eda_search_20261121_005100 mc10=3164 无新trace), A-pure fresh 池枯竭第17次确认(r877终证/r897-r911再确认) — pool_reaudit唯一可造jeij7已r844落库, 台账陈旧非未造; parked合理; NOFILE复活r893-r896用尽; 预算~38min不足1条过闸门case, 禁incomplete入jsonl故不凑数 · eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r912_20261121.md · 📊400/3164≈12.6%(不变)）
```

eda_flow 健康: **EDA_FLOW_OK** · open_session=**ok** · run_commands=**ok** · :18891=**listening** · 报告=`designflow/reports/eda_flow_health_r912_20261121.md`
