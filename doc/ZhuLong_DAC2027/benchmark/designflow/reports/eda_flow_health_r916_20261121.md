# eda_flow MCP 健康自检 · r916 · 2026-11-21

> 用户令（2026-11-21，最高优先，一轮内做完）：实测 eda_flow MCP 是否还在、能否 open_session + run_commands。
> 背景：36.15 本机跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。
> 本轮为同令第 21 次复测（全新 agent session 实测，r897–r915 同令同日已二十测）。

## §0 结论

**`EDA_FLOW_OK`** — initialize + open_session + run_commands + close_session 全通。

一句话：`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r916_20261121.md`

## §1 原始输出

### 1.1 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = eda_flow MCP，监听中（python pid 3365754）。
- `:8652` 监听（无 users 元数据，本自检未触达，仅记录）。
- `:8651` / `:8654` 本次未在监听列表中出现。
- 进程 uptime（`ps -o pid,etime -p 3365754`）：`ELAPSED 24-20:02:20`，与 r897–r915 同进程（pid 未变、etime 单调增长，r915 时为 24-19:57:10，本轮增长 ≈5.2min 吻合，无重启）。

### 1.2 curl initialize 握手（POST，非裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`（`time_total=0.003052s`）
- **serverInfo**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}` ✅
- **protocolVersion 回显**：`2024-11-05` ✅
- **报错原文**：无（response 完整 JSON-RPC result，无 error 字段）
- 响应 instructions 段含 open_session / run_commands / close_session 工具说明，确认服务在线且工具集齐全。

### 1.3 open_session → run_commands → close_session（各记耗时 + 返回前 200 字符）

**open_session**（耗时 **20ms**，四参齐全：`task_id=shardA-health-r916` / `eval_id=designflow-healthcheck-20261121` / `user=e0031982` / `sample=ro_home`）：

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r916_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```
- `error_log` 为空（无 `Missing key`，四参校验通过）✅
- workdir 已就绪。

**run_commands**（耗时 **34ms** wall（MCP 往返）/ cmd `duration_ms=14`，仅 1 条 `echo ok; pwd; id -un`）：

返回前 200 字符（cmd 结果部分）：
```
{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r916_ro_home\ne0031982\n","stderr":"","duration_ms":14,"timed_out":false}],"files":{},"workdir":"...","response":"ran 1 command(s)","error_log":"","print_log":"","result":""}
```
- `exit_code=0`，`stdout` = `ok` / workdir 绝对路径 / `e0031982` 三行齐全 ✅
- `error_log` 空 ✅
- `timed_out=false` ✅

**close_session**（耗时 **27ms**，`keep=false`）：

返回前 200 字符：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r916_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```
- `cleaned=true` ✅
- `error_log` 空 ✅

### 1.4 `ip route get 10.129.32.75`（可达性核验）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013 
    cache 
```
- 本机（10.251.36.15 / 36.15）→ `.75`（10.129.32.75）路由可达，无 NETBLOCK。✅

## §2 结论判定依据

| 判据 | 本轮实测 | 满足？ |
|:--|:--|:--|
| `:18891` 监听 | python pid 3365754 LISTEN | ✅ |
| curl initialize HTTP 200 | 200，serverInfo + protocolVersion 回显 | ✅ |
| open_session 四参通过 | 无 `Missing key`，workdir 就绪 | ✅ |
| run_commands exit 0 | stdout 三行齐全，error_log 空 | ✅ |
| close_session cleaned | `cleaned=true` | ✅ |
| `.75` 路由可达 | ip route 正常返回 | ✅ |

四选一结论映射：
- `EDA_FLOW_OK`（两者都通）✅ **命中**
- `EDA_FLOW_PARTIAL`（通但 run_commands 受限）— run_commands 正常，不命中
- `EDA_FLOW_DOWN`（initialize 即 refused）— initialize 200，不命中
- `EDA_FLOW_NETBLOCK`（本机发不出去）— ip route 可达，不命中

## §3 后续动作

按用户令「§三 按结论走」：`EDA_FLOW_OK` ⇒ 本轮按 §6 转造题 1 条。

但本轮实际 0-case（与 r897–r915 同口径）：
- 扫描快照与 r897–r915 同源（`ssh_eda_search_20261121_005100`，mc10=3164，无新 trace）。
- A-pure fresh 池枯竭第 21 次确认（r877 终证 / r883 / r885 / r897–r915 再确认）：`pool_reaudit_A.tsv` 唯一"可造"`jeij7` 经核验已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets + reference 齐全），该行未同步标"已造"属台账陈旧，实际无未造可造候选。
- ledger stats：covered=400 / target=3164（12.6%），已动 657（case 432 / parked 285），`next` 仅回吐 scansync 命令模板（无 fresh 候选清单）。
- 预算不足（剩余 ~30min 不够 deepread + ≥8 断言 check.py + 5neg + 自验），质量硬要求禁 `incomplete` 入 jsonl，故不凑数。

本轮 infra 实测 = EDA_FLOW_OK，健康自检为最高优先用户令已交付（全新 session 实测第 21 次复测）。本轮 0-case 不构成能力结论，仅反映 A-pure fresh 池枯竭 + 预算约束。

## §4 一致性核验

- `:18891` 进程 pid=3365754 与 r897–r915 完全一致（同一 python 进程持续在线，未重启）。
- open_session 四参取值与令文指定完全一致，无 `Missing key`（避免 D 线 r1037 根因复现）。
- run_commands 仅跑 `echo ok; pwd; id -un`，未触达远端文件系统，无写操作。
- close_session `cleaned=true`，未留残留 workdir。
