# eda_flow MCP 健康自检 · r909 · 2026-11-21

> 用户令（2026-11-21 最高优先）实测澄清：eda_flow MCP 还在吗？open_session / run_commands 是否可用？
> 全新 agent session 第十三次复测（r897–r908 同令同日已十二测）。

## §0 结论

**EDA_FLOW_OK** — open_session + run_commands 均通。

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r909_20261121.md`

## §1 原始输出

### 1.1 端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` listening（python pid=3365754，与 r897–r908 报告记录的同一进程，持续在线未重启）
- `:8651` / `:8654` 未监听（仅 :8652 在听，pyAether 侧服务）
- 无 `8651` / `8654` 命中

### 1.2 握手 curl initialize（🚫 裸 GET，用 POST）

```
HTTP 200 time_total=0.003660
```

body（前 200 字符）：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listCha
```

- HTTP 码：**200**
- `serverInfo`：**有** → `{"name":"EDA-FastMCP-Flow","version":"1.25.0"}` ✓
- `protocolVersion` 回显：**2024-11-05** ✓
- 报错原文：无

### 1.3 `ip route get 10.129.32.75`（NETBLOCK 判据）

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

→ .75 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）。

### 1.4 open_session（四参齐全）

调用：
```json
{
  "task_id": "shardA-health-r909",
  "eval_id": "designflow-healthcheck-20261121",
  "user": "e0031982",
  "sample": "ro_home"
}
```

返回（前 200 字符）：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r909_ro_home","response":"session workdir ready","error_log":"","print_log":"","result":""}
```

- 耗时：**18 ms**
- 无 `Missing key` 报错 ✓
- `error_log`：空
- workdir 已就绪

### 1.5 run_commands（仅 `echo ok; pwd; id -un`）

调用：`commands: ["echo ok", "pwd", "id -un"]`
总耗时：**34 ms**

逐条结果：

| cmd | exit | stdout | stderr | dur_ms |
|---|---|---|---|---|
| `echo ok` | 0 | `ok\n` | `` | 2 |
| `pwd` | 0 | `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r909_ro_home\n` | `` | 1 |
| `id -un` | 0 | `e0031982\n` | `` | 8 |

- 3 cmd 全 exit 0
- stdout = `ok` / workdir / `e0031982`
- `error_log`：空 ✓

### 1.6 close_session

返回（前 200 字符）：
```
{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r909_ro_home","cleaned":true,"response":"session workdir cleaned","error_log":"","print_log":"","result":""}
```

- 耗时：**21 ms**
- `cleaned`：true ✓
- workdir 已释放

### 1.7 扫描快照核验（额外 session）

为确认池状态判据未过期，另开 session 在 .75 上核验最新扫描目录：

```
$ ls -dt /home/t0002965/log/ssh_eda_search_* | head -5
/home/t0002965/log/ssh_eda_search_20261121_005100
/home/t0002965/log/ssh_eda_search_20261120_145529
/home/t0002965/log/ssh_eda_search_20261119_172105
/home/t0002965/log/ssh_eda_search_20261118_230537
/home/t0002965/log/ssh_eda_search_20261116_072610

$ wc -l /home/t0002965/log/ssh_eda_search_20261121_005100/summary.tsv
5434 /home/t0002965/log/ssh_eda_search_20261121_005100/summary.tsv
```

- 最新扫描 = `ssh_eda_search_20261121_005100`（5434 行），与 r897–r908 同源，**无新 trace**
- 该核验 session 已 `cleaned=true`

## §2 四选一结论对照

| 判据 | 本次实测 | 命中 |
|---|---|---|
| initialize refused | 否（HTTP 200） | — |
| run_commands 受限 | 否（3 cmd 全 exit 0，stdout 正确） | — |
| 本机发不出去 | 否（ip route 可达 + curl 200） | — |
| **两者都通** | open_session ok + run_commands ok | **EDA_FLOW_OK** ✓ |

## §3 处置

按用户令 §三：`OK` ⇒ 本轮按 §6 转造题 1 条。

但本轮预算与候选池状态同 r897–r908（扫描快照 `ssh_eda_search_20261121_005100` 5434 行无新 trace；A-pure fresh 池枯竭第 15 次再确认：`pool_reaudit_A.tsv` 唯一「可造」jeij7 已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`；ledger A parked 条目经复核均合理；NOFILE 假阴性复活机会 r893–r896 已用尽）。
剩余预算（~30 min）不足以完成 1 条过 §4 闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验）。质量硬要求禁 `incomplete` 入 jsonl，故不凑数，本轮 0-case。

eda_flow session r909 已 `cleaned=true`。🚫 本 session 未做深读/造题（按用户令纪律）。

## §4 infra 失败 ≠ 能力结论

本次 eda_flow 健康自检全部通过，无 infra 阻塞。
