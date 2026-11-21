# eda_flow MCP 健康自检报告 — r897 · 2026-11-21

> 用户令（2026-11-21，最高优先级，一轮内做完）：「请 designflow A 看看 eda_flow MCP 还在吗？还能 open_session 和 run_commands 吗？」
> 背景：本机 36.15 跑，eda_flow MCP = `http://127.0.0.1:18891/mcp` → `.75`（hfhds201 / 10.129.32.75）。C 线 r889 起 7 轮 INFRA-BLOCK，r891 仍 `scp fkrdf 665KB` 成功。本报告实测澄清。

## §0 结论

**`EDA_FLOW_OK`** — initialize 握手 + open_session + run_commands + close_session 四步全部通过。

- `open_session` = ok（0.02s，error_log 空，workdir 就绪）
- `run_commands` = ok（0.04s，exit_code=0，stdout 含 `ok` / workdir / `e0031982`）
- `:18891` = listening（python pid=3365754）
- `ip route get 10.129.32.75` = 可达（via 10.251.36.1 dev bond0 src 10.251.36.15）

按任务书 §三「OK ⇒ 本轮按 §6 转造题 1 条」。

## §1 本机端口 `ss -ltnp | grep -E '18891|8651|8652|8654'`

```
LISTEN 0      2048              0.0.0.0:18891      0.0.0.0:*    users:(("python",pid=3365754,fd=6))
LISTEN 0      128               0.0.0.0:8652       0.0.0.0:*
```

- `:18891` = **listening**（eda_flow MCP 主端口，python pid=3365754）
- `:8652` = listening（无 users 标注，可能是 pyAether / waveview 相关旁路；非本次探测目标）
- `:8651` / `:8654` = **未监听**（grep 无匹配；8651 此前 r896 报 `Connection refused`，本轮未起）
- 旁证（同段端口扫描）：`:18890` / `:18892` listening（无 users），`:8655` listening，`:18656` listening（python pid=2264511，127.0.0.1 only）

## §2 initialize 握手（curl POST，非裸 GET）

命令（逐字抄任务书 §一）：
```bash
curl -sS -m 8 -X POST http://127.0.0.1:18891/mcp \
  -H 'Content-Type: application/json' \
  -H 'Accept: application/json, text/event-stream' \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"probe-a","version":"1"}}}'
```

- **HTTP 码**：`200`（`-w` 输出 `[HTTP_CODE=200 TIME=0.003285s]`）
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
- `task_id` = `shardA-health-r897`
- `eval_id` = `designflow-healthcheck-20261121`
- `user` = `e0031982`
- `sample` = `ro_home`（read-only home 口径标签）

- **耗时**：`0.02s`
- **error_log**：`` （空 = 成功）
- **response**：`session workdir ready`
- **workdir**：`/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r897_ro_home`
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r897_ro_home","response":"session workdir ready","error_log":"","print_log"`

> ✅ 四参齐全 → 无 `Missing key` 误判（避免 D 线 r1037 那种「传 `{}` 被误判成 infra 断」的坑）。

### §3.2 run_commands

命令：`echo ok; pwd; id -un`（按任务书 §二，仅此一条只读探针，未跑 ssh，无需 `</dev/null`）

- **耗时**：`0.04s`
- **error_log**：`` （空）
- **response**：`ran 1 command(s)`
- **results[0]**：
  - `cmd` = `echo ok; pwd; id -un`
  - `exit_code` = `0`
  - `stdout` = `ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r897_ro_home\ne0031982\n`
  - `stderr` = ``
  - `duration_ms` = `19`
  - `timed_out` = `false`
- 返回前 200 字符：
  `{"results":[{"cmd":"echo ok; pwd; id -un","exit_code":0,"stdout":"ok\n/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r897_ro_home\ne00`

### §3.3 close_session

- **耗时**：`0.02s`
- **cleaned**：`true`
- **response**：`session workdir cleaned`
- **error_log**：`` （空）
- 返回前 200 字符：
  `{"workdir":"/proj/train/AI/workdir/e0031982/eda_sandbox_flow/sessions/e0031982_designflow-healthcheck-20261121_shardA-health-r897_ro_home","cleaned":true,"response":"session workdir cleaned","error_lo`

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
| run_commands ok | ✅ 0.04s exit 0 |
| close_session ok | ✅ 0.02s cleaned |
| .75 路由可达 | ✅ |

**结论**：`EDA_FLOW_OK`（两者都通）。

**处置**（按任务书 §三「OK ⇒」分支）：本轮按 §6 转造题 1 条。本 healthcheck MCP session 已 `close`，未留残留 workdir（`cleaned: true`）。

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
报告生成时间：2026-11-21（r897）· shard A · 工作区 `/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow/reports/`
