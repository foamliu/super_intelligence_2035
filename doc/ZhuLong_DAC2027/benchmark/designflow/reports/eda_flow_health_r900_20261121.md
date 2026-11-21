# eda_flow MCP 健康自检报告 — r900 · 2026-11-21

> 用户令（2026-11-21，最高优先级，一轮内做完）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 背景：本机 36.15 跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。C 线 r889 起 7 轮 INFRA-BLOCK，r891 仍 `scp fkrdf 665KB` 成功。本报告实测澄清。
> 本轮（r900）为同日该健康令的第四次复测（r897 / r898 / r899 已交付 EDA_FLOW_OK），由全新 agent session 实测，复测确认 MCP 仍健康。

## §0 结论

**`EDA_FLOW_OK`** — initialize 握手 + open_session + run_commands + close_session 四步全部通过。

- `open_session` = ok（0.034s，error_log 空，workdir 就绪，四参齐全无 `Missing key`）
- `run_commands` = ok（0.105s，3 条命令 exit_code=0，stdout 含 `ok` / workdir / `e0031982`）
- `close_session` = ok（0.016s，cleaned=true）
- `:18891` = listening（python pid=3365754，与 r897 / r898 / r899 同进程，持续在线未重启）
- `ip route get 10.129.32.75` = 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

按任务书 §三「OK ⇒ 本轮按 §6 转造题 1 条」。本轮 0-case 原因见 §5（A-pure fresh 池枯竭 + 预算不足，非 infra 问题）。

## §1 本机端口 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = **listening**（eda_flow MCP 主端口，python pid=3365754，与 r897 / r898 / r899 同 pid ⇒ 进程未重启，持续在线）
- `:8652` = listening（无 users 标注，旁路端口；非本次探测目标）
- `:8651` / `:8654` = **未监听**（grep 无匹配）

## §2 initialize 握手（curl POST，非裸 GET）

命令（逐字抄任务书 §一）：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`（`-w` 输出 `HTTP 200`）
- **有 `serverInfo`**：✅ 是
  - `serverInfo.name` = `EDA-FastMCP-Flow`
  - `serverInfo.version` = `1.25.0`
- **`protocolVersion`** = `2024-11-05`（回显一致）
- **`capabilities`**：`prompts` / `resources` / `tools`（均 `listChanged: false`）+ `experimental: {}`
- **报错原文**：无（响应体为合法 JSON-RPC `result`，无 `error` 字段）
- 响应含 `instructions` 字段（EDA FastMCP Flow 工具说明，与 MCP server 文档一致）
- 响应前 200 字符：`{"jsonrpc":"2.0","id":1,"result":{"protocolVersion":"2024-11-05","capabilities":{"experimental":{},"prompts":{"listChanged":false},"resources":{"subscribe":false,"listChanged":false},"tools":{"listChanged":false}},"serverInfo":{"name":"EDA-FastMCP-Flow","version":"1.25.0"}...`

## §3 open_session → run_commands → close 实测

### §3.1 open_session（四参齐全，未传 `{}`）

参数（按任务书 §二自检取值）：
- `task_id` = `shardA-health-r900`
- `eval_id` = `designflow-healthcheck-20261121`
- `user` = `e0031982`
- `sample` = `ro_home`（read-only home 口径标签）

- **耗时**：`0.034s`（34ms）
- **error_log**：`` （空 = 成功，无 `Missing key`）
- **response**：`session workdir ready`
- **workdir**（前 200 字符）：`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r900_ro_home`

### §3.2 run_commands（`echo ok; pwd; id -un`）

- **耗时**：`0.105s`（105ms，3 条命令串行）
- **error_log**：`` （空）
- **response**：`ran 3 command(s)`
- 逐命令结果（前 200 字符）：
  - `echo ok` → exit_code=0, stdout=`ok\n`
  - `pwd` → exit_code=0, stdout=`/proj/train/AI/workdir/.../shardA-health-r900_ro_home\n`
  - `id -un` → exit_code=0, stdout=`e0031982\n`

### §3.3 close_session

- **耗时**：`0.016s`（16ms）
- **cleaned**：`true`
- **response**：`session workdir cleaned`
- **error_log**：`` （空）

## §4 网络可达性 `ip route get 10.129.32.75`

```
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

- `.75` 可达（via 10.251.36.1 dev bond0 src 10.251.36.15），与 r897 / r898 / r899 一致。

## §5 本轮 0-case 说明（非 infra 阻塞）

健康自检 = `EDA_FLOW_OK`，按 §三 OK 分支应转造题 1 条。本轮 0-case 原因如下，**全部为选料/预算约束，非 infra 问题**：

1. **A-pure fresh 池枯竭（第 6 次确认）**：r877 终证 + r883 / r885 / r897 / r898 / r899 / r900 再确认。`pool_reaudit_A.tsv` 中唯一标 `可造` 的候选 `jeij7`（e0039102@hfeg0pbn16, mc143, verification）经核验**已在 r844 深读 + 落库为 `EDA-Eval-DesignFlow-RunRegrDriverGenProduce-001`**（A.jsonl 433 行，assets/reference 目录齐全）；`pool_reaudit_A.tsv` 该行未同步标 `已造`，属台账陈旧，实际已造。故 pool_reaudit 中无未造的可造候选。
2. **扫描快照同源无新 trace**：当前 `summary_stats.json.scan_path` = `ssh_eda_search_20261121_005100`（11-21 03:19，mc10=3164），与 r897 / r898 / r899 同源，无新增 trace 可选料。
3. **预算不足**：剩余预算（~25 min）不足以完成 1 条过闸门 case（deepread + ≥8 断言 check.py + 5 neg + 自验 + §4.9 三假 FAIL）。质量硬要求禁止 `incomplete` 入 jsonl，故不凑数。
4. **mc≥5 扩池已落地**（`shard_mc.A=5`，summary_stats `mc5=4483`，`mc5_recompute` 显示 fresh=310），但 A-pure 候选经多轮核查均为已占 / 跨域（C/D）/ intent-dup，无新增可造。

## §6 MEMORY 一行（结论回写）

`eda_flow 健康: EDA_FLOW_OK · open_session=ok · run_commands=ok · :18891=listening · 报告=designflow/reports/eda_flow_health_r900_20261121.md`

## §7 结论四选一对照

| 选项 | 命中？ | 证据 |
|:--|:--:|:--|
| `EDA_FLOW_OK`（两者都通） | ✅ | §3 open+run+close 全 ok |
| `EDA_FLOW_PARTIAL`（通但 run_commands 受限） | ✗ | run_commands 无限制，3 命令全 exit0 |
| `EDA_FLOW_DOWN`（initialize 即 refused） | ✗ | curl HTTP 200 + serverInfo |
| `EDA_FLOW_NETBLOCK`（本机发不出去） | ✗ | §4 ip route 可达 |

**最终结论：`EDA_FLOW_OK`。** infra 健康，本轮 0-case 纯属选料枯竭 + 预算约束，非能力结论。
