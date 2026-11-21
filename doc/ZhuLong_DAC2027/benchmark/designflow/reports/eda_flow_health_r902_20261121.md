# eda_flow MCP 健康自检 · r902 · 2026-11-21

> 用户令（最高优先 · 2026-11-21 shard A）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 背景：本机 = 36.15（`10.251.36.15`），eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（`10.129.32.75` / `hfhds201`）。
> 这是该令的第 **6** 次复测（全新 agent session 实测），前 5 次 = r897/r898/r899/r900/r901，结论均为 `EDA_FLOW_OK`。

## §0 结论

**`EDA_FLOW_OK`** — `open_session` 与 `run_commands` 两者都通。

- `open_session` = **ok**（0.025s，四参齐全 task_id/eval_id/user/sample，无 `Missing key`）
- `run_commands` = **ok**（0.045s，3 条命令全部 exit 0，stdout = `ok` / `<workdir>` / `e0031982`，error_log 空）
- `close_session` = **ok**（0.033s，cleaned=true）
- `:18891` = **listening**（python pid=3365754，与 r897/r898/r899/r900/r901 同进程，未重启；ELAPSED 24-18:42:51）
- curl `initialize` = **HTTP 200** + `serverInfo=EDA-FastMCP-Flow v1.25.0` + `protocolVersion 2024-11-05` 回显

MEMORY 首行：`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r902_20261121.md`

按 §三 OK 分支：本轮应转造题 1 条。**本轮实际 0-case**：扫描快照与 r897–r901 同源（`ssh_eda_search_20261121_005100`，无新 trace），A-pure fresh 池枯竭第 8 次确认（r877 终证 / r883 / r885 / r897 / r898 / r899 / r900 / r901 再确认）；`pool_reaudit_A.tsv` 唯一「可造」jeij7 经核验已在 r844 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets + reference 齐全），实际无未造可造候选；ledger A 已 parked 条目经复核均为合理 parked（wrong-domain / thin-session / GUI-dependent / no-gold），NOFILE 假阴性复活机会已在 r893–r896 用尽；余下预算（~30 min）不足以完成 1 条过闸门 case（深读 + ≥8 断言 check.py + 5 neg + 自验 + hidden B），质量硬要求禁 `incomplete` 入 jsonl 故不凑数。✅ infra 失败 ≠ 能力结论（本轮 infra 通畅，0-case 是选料枯竭 + 预算约束，非能力问题）。

## §1 原始输出

### 1.1 端口监听 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = listening（eda_flow MCP，python pid=3365754，与 r897/r898/r899/r900/r901 同进程，未重启）
- `:8652` = listening（其他服务，非本自检对象）
- `:8651` / `:8654` = 未监听（pyAether :8651 本轮未触及，不影响 eda_flow 自检结论）

进程详情（`ps -o pid,etime,cmd -p 3365754`）：
```
    PID     ELAPSED CMD
3365754 24-18:42:51 /nasdata/app.e0031982/code/eda_fastmcp_flow/.venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp_flow/main.py
```
进程持续在线 ~24 天 18 小时 42 分，与 r897/r898/r899/r900/r901 报告的同一 pid 一致，**MCP 服务未发生重启**。

### 1.2 MCP 握手（initialize · 🚫 非 curl 裸 GET）

命令：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

结果：
- **HTTP 码 = 200**（`time_total=0.0031s`）
- **有 `serverInfo`**：`{"name":"EDA-FastMCP-Flow","version":"1.25.0"}`
- `protocolVersion` 回显 = `2024-11-05`
- `capabilities` 回显 = `{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}}`
- `instructions` 字段回显 EDA-FastMCP-Flow 工具说明（open_session / close_session / declare_done / run_commands / run_code / read_file / write_file / list_files）
- **无报错**

响应体前 800 字符截取：
```
{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"},"instructions":"# EDA FastMCP Flow — Design-Flow EDA Agent Tools\n\nThis MCP server provides tools for design-flow EDA evaluation agents.\n\n## Design-flow session tools\n\n- **open_session**: Create a session workdir on the EDA sandbox (.75).\n  Returns the workdir path — pass it to every subsequent tool call.\n- **close_session**: Release the workdir (archives then removes it).\n- **declare_done**: Signal that the agent has finished its work. The eval\n  driver will then run the test checker on the workdir.\n\n## E
```

### 1.3 `open_session` → `run_commands` → `close_session`（四参齐全 · 实测）

**open_session 四参**（自检取值，符合 §二要求）：
- `task_id = "shardA-health-r902"`
- `eval_id = "designflow-healthcheck-20261121"`
- `user = "e0031982"`
- `sample = "ro_home"`（只读 home 目录）

**open_session**（耗时 0.025s）：
- workdir = `/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r902_ro_home`
- response = `session workdir ready`
- error_log = ``（空，无 `Missing key`）
- 返回前 200 字符：
  ```
  {"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r902_ro_home","response":"session workdir ready","error_log":"","print_log"
  ```

**run_commands**（耗时 0.045s，3 条命令 `echo ok; pwd; id -un`）：
- 3 条命令全部 `exit_code=0`，error_log 空
- `echo ok` → stdout=`ok\n`（5ms）
- `pwd` → stdout=`<workdir>\n`（1ms）
- `id -un` → stdout=`e0031982\n`（15ms）
- 返回前 200 字符：
  ```
  {"results":[{"cmd":"echo ok","exit_code":0,"stdout":"ok\n","stderr":"","duration_ms":5,"timed_out":false},{"cmd":"pwd","exit_code":0,"stdout":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions
  ```

**close_session**（耗时 0.033s）：
- cleaned = `true`
- response = `session workdir cleaned`
- error_log = ``（空）
- 返回前 200 字符：
  ```
  {"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r902_ro_home","cleaned":true,"response":"session workdir cleaned","error_lo
  ```

### 1.4 网络可达性 `ip route get 10.129.32.75`

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```
本机 `10.251.36.15` 经 `bond0` → 网关 `10.251.36.1` 可达 `.75`（`10.129.32.75`），与 r897–r901 一致，无 NETBLOCK。

## §2 结论依据汇总

| 检查项 | 结果 | 证据 |
|:--|:--|:--|
| `:18891` 监听 | ✅ listening | `ss` python pid=3365754 fd=6 |
| MCP 进程持续 | ✅ 未重启 | ELAPSED 24-18:42:51，与 r897–r901 同 pid |
| initialize 握手 | ✅ HTTP 200 | serverInfo + protocolVersion 回显，无报错 |
| `open_session`（四参） | ✅ ok 0.025s | workdir ready，error_log 空，无 Missing key |
| `run_commands` | ✅ ok 0.045s | 3 cmd exit 0，stdout 正确，error_log 空 |
| `close_session` | ✅ ok 0.033s | cleaned=true |
| `.75` 网络可达 | ✅ reachable | ip route via bond0 |

**四选一结论：`EDA_FLOW_OK`**（两者都通）。

## §3 §三 OK 分支处置

§三规定 `OK ⇒ 本轮按 §6 转造题 1 条`。本轮实际 **0-case**，理由（非能力问题，选料枯竭 + 预算约束）：

1. **扫描快照无新 trace**：`ssh_eda_search_20261121_005100`（与 r897–r901 同源），mc10=3164，无新会话进入候选池。
2. **A-pure fresh 池枯竭第 8 次确认**（r877 终证 / r883 / r885 / r897 / r898 / r899 / r900 / r901 / r902）：`pool_reaudit_A.tsv` 唯一「可造」jeij7（e0039102@hfeg0pbn16 mc143 verification）已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`（A.jsonl / assets + reference 齐全），该行未同步标「已造」属台账陈旧，实际无未造可造候选。
3. **ledger A 已 parked 条目经复核均为合理 parked**：wrong-domain（char→C / layout_aether→C / Linux-IM-config）、thin-session（templated 启动业务场景 / 单 turn）、GUI-dependent（GenLEF PyQt5 / live-Aether cellview）、no-gold（pure Q&A 咨询）。NOFILE 假阴性复活机会已在 r893–r896 用尽（g7hp7/plk7n/bdhyb/fkrdf 四条 subdir-path 复活均已落库）。
4. **预算不足**：本轮硬预算 40 min，健康自检已耗用部分，剩余 ~30 min 不足以完成 1 条过闸门 case（深读 messages.json + 合成 + ≥8 独立断言 check.py + 5 neg + negative_selftest + §4.9 三假 FAIL + hidden B + 自验）。
5. **质量硬要求**：§4.3 ≥8 独立条件 / §4.6 k_rationale==k_check≥8 / §4.9 三假 FAIL / 禁 `incomplete` 入 jsonl。不凑数。

✅ **infra 失败 ≠ 能力结论**（本轮 infra 通畅，0-case 是选料枯竭 + 预算约束）。

## §4 与历史复测一致性

| 轮次 | 结论 | open_session | run_commands | close_session | :18891 pid |
|:--|:--|:--|:--|:--|:--|
| r897 | EDA_FLOW_OK | ok | ok | ok | 3365754 |
| r898 | EDA_FLOW_OK | ok | ok | ok | 3365754 |
| r899 | EDA_FLOW_OK | ok | ok | ok | 3365754 |
| r900 | EDA_FLOW_OK | ok | ok | ok | 3365754 |
| r901 | EDA_FLOW_OK | ok 0.035s | ok 5.220s | ok 0.029s | 3365754 |
| **r902** | **EDA_FLOW_OK** | **ok 0.025s** | **ok 0.045s** | **ok 0.033s** | **3365754** |

6 次复测结论一致，MCP 服务进程（pid 3365754）持续在线 ~24 天 18 小时未重启，eda_flow MCP 健康。
