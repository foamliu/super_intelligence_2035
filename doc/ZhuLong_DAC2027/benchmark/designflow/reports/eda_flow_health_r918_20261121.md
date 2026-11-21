# eda_flow MCP 健康自检 · r918 · 2026-11-21

> 用户令（2026-11-21 最高优先）：实测 eda_flow MCP 是否在线、能否 open_session + run_commands。
> 本轮为该令的第 **23** 次复测（r897–r917 已二十二测，结论一致）；全新 agent session 实测。

## §0 结论

**`EDA_FLOW_OK`** —— `open_session` 与 `run_commands` 均通，initialize 握手成功。

- `open_session` = **ok**（18ms，四参齐全，无 Missing key）
- `run_commands` = **ok**（26ms wall / 10ms cmd，exit_code=0，stdout 正确）
- `:18891` = **listening**（python pid 3365754，ELAPSED 24-20:13:41，与 r897–r917 同进程持续在线未重启）
- curl `initialize` = **HTTP 200** + `serverInfo` 回显
- `ip route 10.129.32.75` = 可达

## §1 原始输出

### 1.1 端口监听

```
$ ss -ltnp | grep -E '18891|8651|8652|8654'
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

`:18891` = eda_flow MCP（在线）。`:8652` 在听但不在本次自检范围内（pyAether :8651 未听，与 run_commands 无关）。

### 1.2 MCP initialize 握手（🚫 未 curl 裸 GET，按令 POST initialize）

```
HTTP_CODE=200
```

响应体（前 2000 字符）：

```json
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-MCP-SERVER","version":"1.25.0"},"instructions":"## Available Skills ... eda-aether-init / pyAether-mcp-safe-execution / eda-emydesign-attributes / eda-highlight-by-name-pattern / eda-snap-origin ..."}}
```

- HTTP 码 = **200**
- 有 `serverInfo` = **是**（name=`EDA-MCP-SERVER`，version=`1.25.0`；与 r897–r917 一致）
- `protocolVersion` = **2024-11-05** 回显正确
- 报错原文 = **无**

> 注：serverInfo.name 在 r912/r906/r903 等轮曾记为 `EDA-FastMCP-Flow`，本轮与 r911 等轮回显为 `EDA-MCP-SERVER`；二者指同一服务（v1.25.0 不变），属 serverInfo 字段在不同会话的回显差异，不影响握手结论。

### 1.3 open_session → run_commands → close（各记耗时 + 返回前 200 字符）

**open_session**（耗时 18ms）—— 四参按令传入：
`task_id="shardA-health-r918"` / `eval_id="designflow-healthcheck-20261121"` / `user="e0031982"` / `sample="0"`

```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r918_0","response":"session workdir ready","error_log":"","print_log":"","result":""}
```

- workdir 已创建，`error_log` 空，无 `Missing key`。

**run_commands**（耗时 26ms wall / 单 cmd 10ms）—— 仅跑 `echo ok; pwd; id -un </dev/null`：

```
{"results":[{"cmd":"echo ok; pwd; id -un </dev/null","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r918_0\ne0031982\n","stderr":"","duration_ms":10,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
```

- exit_code = **0**，stdout = `ok` / workdir / `e0031982`，`error_log` 空，`timed_out=false`。✅ run_commands 完全可用。
- `ssh` hang 坑已规避（命令加 `</dev/null`）。

**close_session**（耗时 16ms）：

```
{"workdir":"...","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```

- `cleaned=true`，workdir 已释放。

### 1.4 网络可达性

```
$ ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

本机（10.251.36.15）→ `.75`（10.129.32.75）路由可达，无 NETBLOCK。

## §2 与 C 线 INFRA-BLOCK 报告的关系

C 线 r889 起报 7 轮 INFRA-BLOCK，但本 A 线 r891 起（含本轮 r918，共 28 轮）持续 `EDA_FLOW_OK`：open_session / run_commands / initialize 全通，`:18891` 进程 pid 3365754 自 r897 起未重启（ELAPSED 24-20:13:41 持续增长）。结合 r891 `scp fkrdf 665KB` 成功的历史记录，**eda_flow MCP 与 `.75` 链路在本机视角始终在线**；C 线的 INFRA-BLOCK 更可能是 C 线侧（host/凭据/沙盒配额/特定命令路径）问题，而非全局 eda_flow 故障。建议 C 线对照本报告的 `ss`/`ps`/`ip route`/initialize 四件套自查。

## §3 按结论走的处置

`EDA_FLOW_OK` ⇒ 按令 §三「OK 分支」应转 §6 造题 1 条。

**本轮 0-case，理由（与 r897–r917 一致，已 22 轮再确认）**：

1. **扫描快照无新 trace**：当前 `summary_stats.json.scan_path` = `ssh_eda_search_20261121_005100`（mc10=3164），与 r897–r917 同源，无新候选进入池中。
2. **A-pure fresh 池枯竭第 23 次确认**（r877 终证 → r883/r885/r897–r917 再确认）：
   - `pool_reaudit_A.tsv` 唯一「可造」候选 `jeij7`（e0039102@hfeg0pbn16，mc143，verification）已在 **r844 深读并落库**为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl + assets + reference 齐全）；该行未同步标「已造」属台账陈旧，故 pool_reaudit 实际无未造可造候选。
   - ledger A 的 `parked` 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）。
   - NOFILE 假阴性复活（r893–r896：g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活）已用尽并落库。
3. **预算不足**：本轮剩余约 35 min，不足以完成一条过闸门 case（深读 + ≥8 断言 check.py + 5 neg + 自验 + pi 实跑）。
4. **质量硬要求**：顶部令与 §4 明确「k≥8、3 neg FAIL、hidden B、A 档自包含、真实 trace 溯源」一条都不放松；禁 `incomplete` 入 jsonl，故不凑数。

**结论**：健康自检为最高优先用户令，已交付（全新 session 实测第 23 次复测）。本轮 `WAITING: 0`（非外部阻塞，而是池枯竭 + 预算不足下的如实 0-case，按 §6 收尾纪律不写 `WAITING: 1`）。

## §4 纪律遵守

- 🚫 未改题/图/`check.py`、未动别 shard、未 `git add -A`。
- ✅ `open_session` 四参齐全（避免 D 线 r1037「Missing key 误判 infra 断」根因）。
- ✅ `ssh` 命令加 `</dev/null` 防 hang。
- ✅ 测完即 `close`，未在 eda_flow session 内做深读/造题。
- ✅ infra 失败 ≠ 能力结论（本轮 infra 实为 OK）。

---
报告路径：`designflow/reports/eda_flow_health_r918_20261121.md`
