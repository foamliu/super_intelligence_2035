# eda_flow MCP 健康自检 · r927 · 2026-11-21

> 用户令（2026-11-21 最高优先 · shard A）：实测澄清 eda_flow MCP 是否还在线、能否 open_session + run_commands。
> 本机：10.251.36.15（36.15）。eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（10.129.32.75 / hfhds201）。
> 全新 agent session，第三十二次复测（r897–r926 同日已三十一测，本测为 r927）。

## §0 结论

**EDA_FLOW_OK** — `open_session` 与 `run_commands` 均通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r927_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891`（eda_flow MCP）= **listening**，进程 `python pid=3365754`
- `:8652` = **listening**
- `:8651` / `:8654` = 未匹配（本测未使用 pyAether / Innovus 通道，无需关心）

进程信息：
```
PID       ELAPSED   CMD
3365754   2149133   /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```
- `etimes=2149133s` ≈ 24 天 20:58:53。与 r926（etimes=2148853s）相差 +280s ≈ 4:40，吻合两次自检间隔。**与 r897–r926 同进程持续在线，未重启。**

### 1.2 握手（curl POST initialize，🚫 非 curl 裸 GET）

```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

返回（截断显示，HTTP 200，前 2000 字符）：
```json
{"jsonrpc":"2.0","id":1,"result":{
  "protocolVersion":"2024-11-05",
  "capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},
  "serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},
  "instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools ..."}}
```

- HTTP 码：**200**
- `serverInfo`：**EDA-FastMCP-Flow v1.25.0** ✓ 存在
- `protocolVersion`：2024-11-05 回显 ✓
- 报错原文：无

### 1.3 open_session → run_commands → close（耗时 + 返回前 200 字符）

**open_session（四参齐全）**
```json
{
  "task_id": "shardA-health-r927",
  "eval_id": "designflow-healthcheck-20261121",
  "user": "e0031982",
  "sample": "ro_home"
}
```
- 耗时：**26ms**
- 返回前 200 字符：
  ```
  workdir=/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r927_ro_home
  response=session workdir ready
  error_log=（空）
  ```
- ✅ 四参齐全，**无 `Missing key`**（对照 D 线 r1037 根因：传 `{}` 会 Missing key 被误判 infra 断，本测已避免）

**run_commands**（命令 `echo ok; pwd; id -un </dev/null`，⚠️ `</dev/null` 防 ssh hang）
- 耗时：wall **167ms** / cmd duration_ms **149ms**，1 cmd exit_code=**0**
- 返回前 200 字符：
  ```
  ok
  /proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r927_ro_home
  e0031982
  ```
  stdout 三行：`ok` / pwd 工作目录 / `e0031982`（id -un）✓
- `timed_out=false`，`stderr=（空）`，`error_log=（空）`

**close_session**
- 耗时：**30ms**
- 返回前 200 字符：
  ```
  workdir=/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r927_ro_home
  cleaned=true
  response=session workdir cleaned
  error_log=（空）
  ```

### 1.4 附：ip route get 10.129.32.75

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
✅ .75 网络可达（via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013）。

## §2 四选一结论

| 候选 | 触发条件 | 本测结果 |
|:--|:--|:--|
| `EDA_FLOW_OK` | initialize + open_session + run_commands 全通 | ✅ **本测命中** |
| `EDA_FLOW_PARTIAL` | 通但 run_commands 受限 | — |
| `EDA_FLOW_DOWN` | initialize 即 refused | — |
| `EDA_FLOW_NETBLOCK` | 本机发不出去 | — |

判定依据：
- initialize：HTTP 200 + serverInfo 在场 ✓
- open_session：26ms，workdir ready，四参齐无 Missing key ✓
- run_commands：167ms wall / 149ms cmd，1 cmd exit0，stdout 正确 ✓
- close_session：cleaned=true ✓
- :18891 listening，python pid 3365754 与 r897–r926 同进程持续在线（etimes +280s 与间隔吻合）✓

## §3 按结论走

`OK` 分支 ⇒ 本轮按 §6 转造题 1 条。

但本测为 2026-11-21 最高优先用户令「eda_flow MCP 健康自检」的第三十二次复测，**健康自检本身已交付**。§6 造题方面：
- 扫描快照同 r897–r926（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace）
- `trace_ledger --shard A stats`：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），剩余可做 ≈2511，`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）
- A-pure fresh 池枯竭第 32 次确认（r877 终证 / r883 / r885 / r897–r926 再确认）：
  - `pool_reaudit_A.tsv` 唯一「可造」jeij7（e0039102@hfeg0pbn16 mc143 verification）已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl/assets+reference 齐全），该行未同步标「已造」属台账陈旧，实际无未造可造候选
  - ledger A parked 条目经复核均合理（wrong-domain / thin-session / GUI-dependent / no-gold）
  - NOFILE 假阴性复活 r893–r896 已用尽（g7hp7 / plk7n / bdhyb / fkrdf 四条 subdir-path 复活均落库）
- 本测剩余预算不足完成 1 条过闸门 case（深读 + ≥8 断言 check.py + 5 neg + 自验），质量硬要求禁 incomplete 入 jsonl，故不凑数

## §4 纪律

- 🚫 不改题/图/check.py、不动别 shard、不 `git add -A`
- ✅ infra 失败 ≠ 能力结论（本测 infra 通过）
- ✅ 报告随心跳提交（§8.3）
- ✅ eda_flow session r927 cleaned（cleaned=true）

---
*本报告为只读自检产物，原始输出逐字抄录，未做任何修饰。*
