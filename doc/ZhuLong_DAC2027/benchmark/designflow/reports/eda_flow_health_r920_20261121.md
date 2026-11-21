# eda_flow MCP 健康自检 r920 · 2026-11-21

> 用户令（2026-11-21 最高优先）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 本轮 = r897-r919 同令第二十五次复测（全新 agent session 实测）。

## §0 结论

**EDA_FLOW_OK** — open_session 与 run_commands 均通。

```
eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r920_20261121.md
```

## §1 原始输出

### 1.1 端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening，python pid=3365754（`eda_fastmcp_flow/main.py`），与 r897-r919 同进程持续在线未重启。
- 进程 ELAPSED = `24-20:23:37`（`ps -o etimes` = 2147017s；r919 时为 `24-20:18:46`，增长 ~4:51 吻合本轮间隔，进程未重启）。
- `:8652` 亦 listening（无 pid 显示，非本次自检对象）。
- `:8651` / `:8654` 未监听（grep 无命中，正常）。

### 1.2 MCP 握手（initialize，🚫 未用裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码 = 200**（curl `-w` 回显 `HTTP_CODE=200`；`TIME_TOTAL=0.003080s`）。
- **serverInfo 存在**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`。
- **protocolVersion 回显**：`2024-11-05`。
- capabilities 回显：prompts/resources/tools 均声明，listChanged=false。
- 无报错原文。

### 1.3 open_session → run_commands → close 各耗时 + 返回前 200 字符

**open_session**（四参齐全：task_id/eval_id/user/sample）
- 耗时：**18 ms**
- 入参：`task_id="shardA-health-r920"` / `eval_id="designflow-healthcheck-20261121"` / `user="e0031982"` / `sample="0"`
- 返回（前 200 字符）：
  ```
  workdir=/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r920_0
  response="session workdir ready"
  error_log=""  (空 = 无 Missing key，无 infra 误判)
  ```

**run_commands**（单命令 `echo ok; pwd; id -un`）
- 耗时：**36 ms** wall（cmd duration_ms=21）
- 返回（前 200 字符）：
  ```
  results[0]: cmd="echo ok; pwd; id -un" exit_code=0
    stdout="ok\n/proj/train/AI/workdir/.../e0031982_designflow-healthcheck-20261121_shardA-health-r920_0\ne0031982\n"
    stderr=""  duration_ms=21  timed_out=false
  response="ran 1 command(s)"  error_log=""
  ```

**close_session**
- 耗时：**18 ms**
- 返回（前 200 字符）：
  ```
  workdir=/proj/train/AI/workdir/.../e0031982_designflow-healthcheck-20261121_shardA-health-r920_0
  cleaned=true  response="session workdir cleaned"  error_log=""
  ```

总耗时（三步串行）：**72 ms**。

## §2 网络可达性

`ip route get 10.129.32.75`：
```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
本机（10.251.36.15）可路由至 .75，非 NETBLOCK。

## §3 按结论走（§三 OK 分支）

`EDA_FLOW_OK` ⇒ 本轮按 §6 转造题 1 条。

实测后（详见 MEMORY r920 流水）：扫描快照与 r897-r919 同源（`ssh_eda_search_20261121_005100`，mc10=3164，updated_at=2026-11-21 03:19，无新 trace），`trace_ledger.py --shard A stats` 显示 covered=400/target=3164(12.6%)，已动 657（case 432 / parked 285），剩余可做 ≈ 2511，`next` 仅回吐 scansync 命令模板（无 fresh 候选清单），A-pure fresh 池枯竭第二十五次确认（r877 终证 / r883 / r885 / r897-r919 再确认）。pool_reaudit_A.tsv 唯一「可造」jeij7 经核验已在 r844 落库为 EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001（A.jsonl/assets+reference 齐全），该行未同步标「已造」属台账陈旧，实际无未造可造候选。剩余预算（~30min）不足以完成一条过闸门 case（deepread + ≥8 断言 check.py + 5neg + 自验），质量硬要求禁 incomplete 入 jsonl，故不凑数。

**本轮 0-case**：健康自检为最高优先用户令已交付（第二十五次复测），infra 实测 EDA_FLOW_OK，能力侧无新 case 系 fresh 池枯竭 + 预算不足，**infra 失败 ≠ 能力结论**。

## §4 纪律自检

- 🚫 未改题/图/check.py；未动别 shard；未 `git add -A`。
- ✅ open_session 四参齐全（task_id/eval_id/user/sample），未传 `{}`，无 Missing key 误判。
- ✅ ssh 类命令本自检未涉及（run_commands 仅 `echo/pwd/id`，无 hang 风险）。
- ✅ 测完 close（cleaned=true）。
- ✅ 报告随心跳提交。
