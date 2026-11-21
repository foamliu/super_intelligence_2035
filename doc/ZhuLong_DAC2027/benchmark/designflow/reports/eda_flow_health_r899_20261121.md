# eda_flow MCP 健康自检报告 — r899 · 2026-11-21

> 用户令（2026-11-21，最高优先级，一轮内做完）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 背景：本机 36.15 跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。C 线 r889 起 7 轮 INFRA-BLOCK，r891 仍 `scp fkrdf 665KB` 成功。本报告实测澄清。
> 本轮（r899）为同日该健康令的第三次复测（r897 / r898 已交付 EDA_FLOW_OK），扫描快照与 r897 / r898 同源（`ssh_eda_search_20261121_005100`），复测确认 MCP 仍健康。

## §0 结论

**`EDA_FLOW_OK`** — initialize 握手 + open_session + run_commands + close_session 四步全部通过。

- `open_session` = ok（0.02s，error_log 空，workdir 就绪，四参齐全无 `Missing key`）
- `run_commands` = ok（0.02s，exit_code=0，stdout 含 `ok` / workdir / `e0031982`）
- `:18891` = listening（python pid=3365754，与 r897 / r898 同进程，持续在线）
- `ip route get 10.129.32.75` = 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

按任务书 §三「OK ⇒ 本轮按 §6 转造题 1 条」。本轮 0-case 原因见 §5（A-pure fresh 池枯竭 + 预算不足，非 infra 问题）。

## §1 本机端口 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = **listening**（eda_flow MCP 主端口，python pid=3365754，与 r897 / r898 同 pid ⇒ 进程未重启，持续在线）
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

- **HTTP 码**：`200`（`-w` 输出 `HTTP_CODE=200`）
- **有 `serverInfo`**：✅ 是
  - `serverInfo.name` = `EDA-FastMCP-Flow`
  - `serverInfo.version` = `1.25.0`
- **`protocolVersion`** = `2024-11-05`（回显一致）
- **`capabilities`**：`prompts` / `resources` / `tools`（均 `listChanged: false`）+ `experimental: {}`
- **报错原文**：无（响应体为合法 JSON-RPC `result`，无 `error` 字段）
- 响应含 `instructions` 字段（EDA FastMCP Flow 工具说明，与 MCP server 文档一致）

## §3 open_session → run_commands → close 实测

### §3.1 open_session（四参齐全，未传 `{}`）

参数（按任务书 §二自检取值）：
- `task_id` = `shardA-health-r899`
- `eval_id` = `designflow-healthcheck-20261121`
- `user` = `e0031982`
- `sample` = `ro_home`（read-only home 口径标签）

- **耗时**：`0.02s`（19ms）
- **error_log**：`` （空 = 成功）
- **response**：`session workdir ready`
- **workdir**：`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r899_ro_home`
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r899_ro_home","response":"session workdir ready","error_log":"","print_log`

> ✅ 四参齐全 → 无 `Missing key` 误判（避免 D 线 r1037 那种「传 `{}` 被误判成 infra 断」的坑）。

### §3.2 run_commands

命令：`echo ok; pwd; id -un`（按任务书 §二，仅此一条只读探针，未跑 ssh，无需 `</dev/null`）

- **耗时**：`0.02s`（24ms）
- **error_log**：`` （空）
- **response**：`ran 1 command(s)`
- **results[0]**：
  - `cmd` = `echo ok; pwd; id -un`
  - `exit_code` = `0`
  - `stdout` = `ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r899_ro_home\ne0031982\n`
  - `stderr` = ``
  - `duration_ms` = `11`
  - `timed_out` = `false`
- 返回前 200 字符：
  `{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r899_ro_home\ne00319`

### §3.3 close_session

- **耗时**：`0.01s`（13ms）
- **cleaned**：`true`
- **response**：`session workdir cleaned`
- **error_log**：`` （空）
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r899_ro_home","cleaned":true,"response":"session workdir cleaned","error_lo`

## §4 旁证：到 .75 的网络可达性

```
$ ip route get 10.129.32.75
10.129.32.75 via 10.251.36.1 dev bond0 src 10.251.36.15 uid 9013
    cache
```

- 本机 36.15（`src 10.251.36.15`）→ `.75`（`10.129.32.75`）经 `bond0` 下一跳 `10.251.36.1`，路由存在。
- run_commands 在 .75 上成功执行 `id -un` 返回 `e0031982`，证明 .75 侧执行链路通畅（不仅路由可达，且 sandbox 命令分发正常）。

## §5 结论与处置

| 判据 | 结果 |
|:--|:--|
| `:18891` listening | ✅ |
| initialize 握手 HTTP 200 + serverInfo | ✅ |
| open_session（四参）ok | ✅ 0.02s |
| run_commands ok | ✅ 0.02s exit 0 |
| close_session ok | ✅ 0.01s cleaned |
| .75 路由可达 | ✅ |

**结论**：`EDA_FLOW_OK`（两者都通）。

**处置**（按任务书 §三「OK ⇒」分支）：本轮按 §6 转造题 1 条。本 healthcheck MCP session 已 `close`，未留残留 workdir（`cleaned: true`）。

**本轮 0-case 说明**（infra 全通，0-case 非 infra 原因）：
- 扫描快照与 r897 / r898 同源（`summary_stats.json.scan_path` = `ssh_eda_search_20261121_005100`，`mc10=3164`，`updated_at=2026-11-21 03:19`），无新 trace 进入。
- A-pure fresh 池枯竭已由 r877（终证）/ r883 / r885 / r897 / r898 多轮确认（top A-domain 候选全已占或跨域 C/D）。
- 一条过闸门 case 需 deepread + ≥8 独立断言 check.py + ≥5 negative + 自验 + §4.9 三假 FAIL，剩余预算（~30min）不足以完成且不降质。
- 质量硬要求禁止 `incomplete` 入 jsonl，故不凑数。`WAITING: 0`（非外部阻塞，是池枯竭 + 预算约束）。

## §6 纪律自检

- 🚫 未改题 / 图 / `check.py`
- 🚫 未动别 shard 文件
- 🚫 未 `git add -A`
- ✅ open_session 传四参（未传 `{}`）
- ✅ run_commands 仅 `echo ok; pwd; id -un`（无 ssh，无需 `</dev/null`）
- ✅ 测完即 `close_session`（cleaned=true）
- ✅ infra 失败 ≠ 能力结论（本轮 infra 全通，无此问题）
- ✅ 报告随心跳提交（§8.3）

---
报告生成时间：2026-11-21（r899）· shard A · 工作区 `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/reports/`
