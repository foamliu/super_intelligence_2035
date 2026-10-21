# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🔴 运维指令 · 2026-10-20 21:4x（**用户直令：杀 r4/r5/regrade → 端口换 8650/8651/8652/8654 → 重启 r4**）· 最高优先

> 用户原话：「杀掉 r4/r5，regrade 也杀掉，端口换到 8650,8651,8652,8654，重启 r4」。
> **现状**：r4''' 21:09 已收口但判 INVALID（70/158 字面量 "pass" + breaker OPEN 98 consecutive worker spawn failures@8667）；4 旧端口 8663/8666/8667/8670 全不可达。r4/r4'/r4''/r4''' 全 INVALID ⇒ **本轮 r4 是第 5 次尝试**，编号用 **r4⁗（r4-4）**，batch 自动生成。

**① 执行顺序（运维已下发 RUN_ID 99 做①②，你负责③④⑤）**
1. **杀残留**：`pkill -f 'run_readback_none_retest_r4d3_regrade'`、`pkill -f 'run_pipeline.py.*evaluation'`、`pkill -f 'run_cline_script.*readback_none'`。⚠️ **不碰** t0002147、loop、ops_relay。
2. **端口切换**：`SANDBOX_ENDPOINTS=8650,8651,8652,8654@10.129.32.75`。
   - 🔴 **必须先在 `.env` 或启动脚本中确认这四个端口归本线所有**（历史上 8650/8651/8652/8654 被 **t0002147** 占用，r3 regrade 曾因抢占全 timeout）。若被 t0002147 占用 → **不要抢，报 blocker**。
   - 4 端口逐个 `timeout 5 bash -c "</dev/tcp/10.129.32.75/$p"` 必须 **4/4 OPEN** 才起跑。
3. **起 r4⁗**（与 r4''' 同配置同模型同 readback=none，仅换端口）：
   ```bash
   cd /nasdata/app.e0031982/code/ZhuLong_DAC2027
   export PYTHON=$PWD/venv/bin/python        # 🔴 必须，漏了必崩 pydantic ModuleNotFoundError
   export SANDBOX_ENDPOINTS=8650,8651,8652,8654@10.129.32.75
   unset http_proxy https_proxy ALL_PROXY
   export NO_PROXY=10.129.32.75,localhost,127.0.0.1
   setsid bash scripts/run_cline_script.sh -p 4 -n > /tmp/ABL_readback_none_retest_r4d4.log 2>&1 < /dev/null &
   ```
   起跑后 5 分钟内核验：`pgrep -af run_cline_script` 有 1 launcher + 4 worker、log 在增长、首题已开始。
4. **启动后立刻回报**：PID / batch 号 / 4 端口状态 / 首 5 分钟 log 行数。
5. **监控口径（强制，纠正此前误判）**：
   - ✅ **健康判据 = task 完成数单调增长**（从 **codegen jsonl 行数**数，不是 log 行数）。
   - ✅ **每轮巡检必须 grep codegen jsonl 里字面量 `"pass"` 数量**——这是退化的唯一早期信号（20:30 前四轮巡检都只 grep log，错过 70 条退化的早期发现）。
   - 停手阈值不变：literal-pass >10 或 MCP 率 ≥5/min → 停手报运维。

**② 若有任何一个前置不满足（端口被占 / 端口不可达 / 启动即崩）→ 立刻报 blocker，不要盲重试。**

### 🔴 运维指令 · 2026-10-20 21:2x（r4 疑似停滞·只读取证）·【已归档·历史·已被 21:4x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 🔄 运维指令 · 2026-10-21 10:4x（**参考 t0002147 配置修复 cline settings + .env → 重跑 r4⁗**）· 用户直令 · 最高优先

> 用户令（原文）：「请你分析一下代码，看看问题能否修复」+「好的 按照 t0002147（陈熙元）的做法改 cline settings 好了。其它的配置也可以参考他们」
> **根因分析结论**（代码层面，带行号证据）：r4 家族 5/5 全 INVALID 的根因 = **cline 客户端 MCP 60s 缺省超时**（`~/.cline/data/settings/cline_mcp_settings.json` 无 `timeout` 字段 → 回退 60s）× **t0002147 的 64 worker 在同一台 10.129.32.75 + 同一 FlexLM 并发争用** → run_code P95 从 <60s 抬到 >60s → cline 单方面 abort 产生 -32001 风暴 → 模型在持续 tool-call 失败后退化为输出 literal "pass"。
> - **对照 t0002147**：他们的 `cline_mcp_settings.json` 有 `"timeout": 600`（10min）→ 所以他们的 64 worker 不中招。**这就是现成的成功案例。**
> - **服务端无 60s 超时**：eda_fastmcp `SANDBOX_TIMEOUT=150s` + eda_sandbox_lite `EXEC_TIMEOUT` 都 >60s → 客户端先放弃。
> - **换端口无效**：8650/8651/8652/8654 都在同一台 10.129.32.75 + 同一 FlexLM → 端口隔离不了 CPU/licence。
> - **licence fix（15:4x）已压住 breaker**：r4‴/r4⁗ 的 circuit_breaker=0 → 剩下的纯粹是 client-side 60s timeout。
> - **退化签名**：literal "pass" 不是 eda_fastmcp 返回的（`tools/run_code.py:62` 成功路径只回 `{"response":"executed"}`），是 cline 在 60s abort 后把 -32001 喂回模型 → 模型退化为输出文本 "pass" 结束 turn。

#### ① 参考 t0002147 改 cline_mcp_settings.json（核心修复）

t0002147 的配置（`/home/app.t0002147/.cline/data/settings/cline_mcp_settings.json`，已实测读取）：
```json
{
  "mcpServers": {
    "EDA_MCP_server": {
      "url": "http://10.251.36.15:18889/mcp",
      "type": "streamableHttp",
      "timeout": 600,
      "disabled": false,
      "autoApprove": [
        "search_apis",
        "get_api_details",
        "search_apis_by_keyword",
        "run_code"
      ]
    }
  }
}
```

**ZhuLong 当前配置**（`/home/app.e0031982/.cline/data/settings/cline_mcp_settings.json`）缺 `timeout` 字段 + autoApprove 用旧工具名 `run_pyAether_code_tool`（0731 已改名 `run_code`）。

**改成**（对齐 t0002147，但 url 指向 ZhuLong 自己的 8090）：
```json
{
  "mcpServers": {
    "pyAether_MCP_server": {
      "url": "http://10.251.36.15:8090/mcp",
      "type": "streamableHttp",
      "timeout": 600,
      "disabled": false,
      "autoApprove": [
        "search_apis",
        "get_api_details",
        "search_apis_by_keyword",
        "run_code"
      ]
    }
  }
}
```

**改动点**：
1. **加 `"timeout": 600`**（对齐 t0002147，10min，>服务端 150s HTTP timeout，让服务端先返回真实结果）
2. **autoApprove 改 `run_pyAether_code_tool` → `run_code`**（0731 改名后的正确工具名，t0002147 用的是 `run_code`）
3. **autoApprove 加 `search_apis_by_keyword`**（t0002147 有，ZhuLong 缺）

**备份**：改前 `cp ~/.cline/data/settings/cline_mcp_settings.json ~/.cline/data/settings/cline_mcp_settings.json.bak.20261021_104x`。

#### ② 参考 t0002147 改 .env（辅助配置对齐）

t0002147 的 `.env`（`/home/app.t0002147/mcp_0917/eda_fastmcp/.env`，已实测）与 ZhuLong 对比，**以下对齐**（仅加缺失项，不动已有值）：

| 配置项 | t0002147 | ZhuLong 当前 | 操作 |
|:--|:--|:--|:--|
| `RAG_RECALL_TIMEOUT` | `25` | **未设** | 加 `RAG_RECALL_TIMEOUT=25` |
| `EDA_RUNCODE_GUARDRAILS` | `false` | **未设** | 加 `EDA_RUNCODE_GUARDRAILS=false` |
| `EDA_RUNCODE_READBACK` | **未设**（t0002147 不做 readback 消融）| `none` | **不动**（ZhuLong (N′) 唯一变量，保留）|
| `PROXY_PORTS` | `8656,8658,8661,8662`（他们的）| `8650,8651,8652,8654` | **不动**（ZhuLong 自己的端口，与 t0002147 不冲突）|
| `SANDBOX_ENDPOINTS` | `8656:t0002441_9,...`（他们的）| `8650:t0002997_1,...` | **不动**（同上）|
| `EDA_OMEGA_FIDELITY` | `high` | `high` | 已一致 ✅ |
| `EDA_PHI_BUDGET` | `0` | `0` | 已一致 ✅ |
| `EDA_PHI_LAGGED` | `0` | `0` | 已一致 ✅ |
| `SKILL_DATA_DIR` | `./docs/skill_data_selfexpl` | `./docs/skill_data_selfexpl` | 已一致 ✅ |
| `SANDBOX_TIMEOUT` | `150` | `150` | 已一致 ✅ |
| `EVAL_SANDBOX_WORKERS` | `4` | `4` | 已一致 ✅ |

**注意**：
- t0002147 用 cline 3.0.66，ZhuLong 用 cline 3.0.51。**不升级 cline 版本**（3.0.51 是 ZhuLong 锚点臂的复用基线，升级会破坏与 r1/r2/r3 的口径一致性）。
- t0002147 用自己的端口 8656/8658/8661/8662（workdir t0002441_9..12），ZhuLong 用 8650/8651/8652/8654（workdir t0002997_1..4）→ **端口不冲突，各用各的**。

#### ③ 重启 8090 + 验证 4 端口健康
- 改完 .env 后重启 8090（pick up 新配置）。
- 4 端口 run_code 健康探针（8650/8651/8652/8654 × 2 次，确认返回 `{"response":...}` 且无 breaker/空响应）。
- MCP 冒烟 5/5。

#### ④ 重跑 r4⁗（第 6 次，配置同 r1-r3 + 新 cline settings）
- **先标 r4 家族 5/5 全 INVALID**（r4/r4′/r4″/r4‴/r4⁗ 均作废不进 5-run，产物日志留证）。
- **r4⁗ 起跑**：配置与 r1-r3 完全一致 + 新 cline settings（timeout=600）—— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3自探索ON / full harness / `-p 4` / 模型 `deepseek-v4-pro-fp4` / 端口 `8650,8651,8652,8654` / `export PYTHON=$PWD/venv/bin/python`。
- 日志 `/tmp/ABL_readback_none_retest_r4e.log`（r4⁗ 已用 r4d4，本次用 r4e）；batch 新建。
- **r4⁗ 30min 内必报**：real_MCP_32001 计数 + literal "pass" 计数 + 4 端口可达性。
  - **判据**：超时率 ≤ ~0.001/行 + literal-pass ≈ 0 → fix 根治。
  - **若 30min 内仍 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**（client timeout 修复无效，需考虑换沙盒机）。
- r4⁗ 收口 → r5⁗（同配置同端口）→ 5/5 mean±std（r1,r2,r3,r4⁗,r5⁗）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′/r4″/r4‴/r4⁗ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不升级 cline 版本（保持 3.0.51）。
- 改 cline settings + .env 前**先备份**。
- **若 r4⁗ 30min 仍退化 → 停手报运维**，不盲目第 7 次重跑（考虑换沙盒机/错峰）。
- commit：`zhulong S1: 参考 t0002147 修复 cline settings(timeout=600) + .env 对齐 -> 重跑 r4''''`。

### 🔄 运维指令 · 2026-10-20 15:4x（**licence fix 已部署 → 验证 4 端口 → 重启 8090 → 重跑 r4‴**）· 用户直令 · 最高优先【已被 10:4x 取代·历史·未根治】

> 用户令（原文）：「**我刚提交了一个沙盒license泄露问题的fix并已部署到8663,8666,8667,8670四个端口。请重启r4，用这四个端口。重启之前先验证这四个端口健康。**」
> **背景**：14:12 BLOCKER 根因 = pyAether licence 断路器 OPEN（100+ 连续失败→深度 cooling-off，4 端口全 0 响应 ~2.5h）。三轮 r4/r4′/r4″ 共 680/156/575 次 MCP timeout → literal "pass" 退化（r4″ 79/158 gen-fail）。**用户已定位根因为 licence 泄露并部署 fix**。本令取代 08:2x 的"停手报 blocker"处置，恢复重跑。
> **端口**：8663/8666/8667/8670（与 08:2x 同，fix 已部署到这 4 个）。

#### ① 先验证 4 端口健康（**必须全过才重启 8090**）
- 用**真实 pyAether run_code 调用**（带 lang=pyAether, host=aether 或你已知正确参数格式）探 4 端口，每个至少 2 次，确认返回 `{"response":...}` 且**无** `licence unavailable` / `circuit breaker` / 空响应。
- 对照 14:56/15:33 的故障态（breaker open / 0 字节空响应），确认 fix 生效。
- **若任一端口仍返回 breaker/空响应 → 停手报运维**（fix 可能未完全生效），不重启 8090、不起 r4‴。
```bash
# 4 端口 run_code 健康探针（lang/host 参数照你已知正确格式）
for P in 8663 8666 8667 8670; do
  echo "=== port $P ==="
  for i in 1 2; do
    T0=$(date +%s%N)
    R=$(timeout 30 curl -s -m 25 -X POST "http://10.129.32.75:$P/v1/run_code" \
        -H 'Content-Type: application/json' \
        -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null | head -c 200)
    T1=$(date +%s%N); MS=$(( (T1-T0)/1000000 ))
    echo "  #$i ${MS}ms :: $(echo "$R" | cut -c1-150)"
  done
done
# 判据：4 端口 × 2 次 = 8 次全返回 {"response":... 且无 licence/breaker/空 → 健康通过
```

#### ② 重启 8090 wrapper（清累积状态，pick up fix 后的端口）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
P8090=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$P8090 etime=$(ps -o etimes= -p $P8090 2>/dev/null|tr -d ' ')s"
echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
PNEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$PNEW（旧 $P8090）"
echo "== 8090 MCP 冒烟 5/5 =="
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 100)
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK"; else FAIL=$((FAIL+1)); echo "  #$i FAIL"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 额外：8090 透传 run_code 端到端秒回
echo "run_code via 8090:"
timeout 30 curl -s -m 25 -X POST http://localhost:8090/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"pyAether_MCP_server__run_code","arguments":{"code":"print(1)","lang":"pyAether","host":"aether"}}}' 2>/dev/null | head -c 300
echo ""
```

#### ③ 起 r4‴（端口 8663/8666/8667/8670，配置同 r1–r3）
- **先标 r4/r4′/r4″ 全部 INVALID**（680/156/575 MCP timeout → literal "pass" 退化，均不进 5-run）：
  - r4 旧轮 `2026_1019_235040` INVALID(680 timeout, 99 literal-pass, 31.0%)
  - r4′ `2026_1020_063134` INVALID(110→156 timeout 抬头)
  - r4″ `2026_1020_090900` INVALID(575 timeout, 79 literal-pass, licence breaker)
  - 🚫 不覆盖原始产物与日志（留证）。
- **r4‴ 起跑**：配置与 r1–r3 完全一致 —— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / **V3 自探索 ON** / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / **端口 `8663,8666,8667,8670`** / `export PYTHON=$PWD/venv/bin/python`。
- 日志 `/tmp/ABL_readback_none_retest_r4d.log`；batch 新建。
- **r4‴ 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数 + 4 端口各自可达性 + **literal "pass" 计数**（grep completed jsonl 中字面量 `"pass"` 数量），确认 fix 生效（超时率 ≤ ~0.001/行 + literal-pass ≈ 0）。
- r4‴ 收口 → 立即起 **r5‴**（同配置同端口）→ 5/5 齐（r1,r2,r3,r4‴,r5‴）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex` → full@pro-cloud 5 轮。

#### ④ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′/r4″ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED。
- kill 一律显式 PID + cmdline 核对（避 opencode 误匹配）。
- **若 4 端口验证仍不健康（breaker/空响应）→ 停手报运维**，不重启 8090、不起 r4‴（fix 可能未完全生效）。
- **若 r4‴ 30min 内再现 MCP timeout 风暴（率 ≥5/min）或 literal-pass >10 → 停手报运维**（fix 可能未根治）。
- commit：`zhulong S1: licence fix 部署 → 验证 4 端口 → 重启 8090 → 重跑 r4''' (端口 8663/8666/8667/8670)`。

### 🔄 运维指令 · 2026-10-20 10:1x（09:0x 令作废·继续按 08:2x 跑 r4″→r5″）·【已归档·历史·已被 15:4x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 09:0x（先 regrade r4′ 看成绩）·【已归档·历史·作废·基于误判·已被 10:1x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 08:2x（停 r4′→重启 8090→换端口 8663/8666/8667/8670 重跑 r4″）·【已归档·历史·已被 09:0x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。


### 🔄 运维指令 · 2026-10-20 06:3x（停 r5→重启 8090→重跑 r4/r5）·【已归档·历史·已被 08:2x 取代】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。



### 🔬 运维指令 · 2026-10-20 06:0x（P0：r4=31% 根因排查·680 timeout 归因）·【已归档·历史·已闭合】→ 原文移至 `run/ARCHIVE_ZHULONG_TASK.md` §归档 batch 8。



### 🔒 运维指令 · 2026-10-19 23:2x（**模型口径锁定：r4/r5 用 fp4；full 用 pro-cloud**）· 用户直令 · 与 23:0x 块同等最高优先

> 用户确认（原文）：「**r4/r5 继续用 fp4，但跑 full 的时候，切换到 deepseek-v4-pro-cloud。**」
> 这是对 23:0x 块的**最终口径裁定**，覆盖任何歧义。

**① 臂 × 模型对照（严格照此执行，不得自行调换）**

| 阶段 | readback 档 | **模型 / endpoint / key** | 轮数 |
|:--|:--|:--|:--:|
| r4, r5 | (N′) `READBACK=none` | **`deepseek-v4-pro-fp4`** @ `/cloud/v1`，key 末 8 = **`8aa0785e`** | 各 1 轮 → 凑满 5/5 |
| full 复测 | (F) `READBACK=full` | **`deepseek-v4-pro-cloud`** @ `/cloud/v1`，key 末 8 = **`8aa0785e`** | 5 轮 |

> ⚠️ **两臂用的可能是同一个 key `...8aa0785e`**（03:50 探针显示该 key 对 fp4 与 cloud 都返回 200）。**“用 deepseek-v4-pro-cloud 的 apikey” = 换模型名 + 用能访问 pro 族的那个 key**；`88ea2f23`（glm 的）对 pro 族**必 403**，禁用。

**② 起跑前必做「模型落点自检」（防止模板复制带错模型）**
> 背景：源码注释显示 worker 的 `settings/providers.json` 由 `prepare_cli_env` 从 `$CLI_DATA_DIR(~/.zhulong)` 复制而来，而 `~/.zhulong/settings/providers.json` 当前是 **`glm-5.2`**（那是**编排模型**，给 opencode 用）。RUN_ID 89 实测该字段确实是 `glm-5.2` —— 所以**不能只看它**，必须看 **worker 实际生效的那份**。
- **r4/r5 起跑前**：`ls -dt ${CLI_ISOLATION_DIR}/worker_*/data/settings/providers.json | head -1 | xargs grep -o '"model"[^,]*'`
  → **必须是 `deepseek-v4-pro-fp4`**；若是 `glm-5.2` / `pro-cloud` / 其它 → **先修正模板再起跑**，并把 before/after 原文贴进回报。
- **full 臂起跑前**：同一检查点 → **必须是 `deepseek-v4-pro-cloud`**。
- 同时贴 `/proc/<cline worker pid>/environ` 里与模型相关的键（若有），双证。

**③ 口令（两臂都要在日志首行写明）**
- r4/r5：`ARM=(N') MODEL=deepseek-v4-pro-fp4 KEY=...8aa0785e READBACK=none`
- full：`ARM=(F) MODEL=deepseek-v4-pro-cloud KEY=...8aa0785e READBACK=full`

**④ 报告口径**
- `(N′) 5/5` 与 `(F)@pro-cloud 5/5` **分表列示**，不得合并计算。
- full 臂须注明：「**与既有 (F)（fp4）相比，模型部署不同（cloud vs fp4），不可直接混算**」。
- n<5 不写 ±。

**⑤ 端口（两臂统一·用户 23:3x 直令）**
- **`8666 / 8667 / 8669 / 8670` @ 10.129.32.75** —— RUN_ID 90 普查（23:21，21 端口 × TCP+真实执行）：这 4 个 `TCP_OPEN` 且 **14/15/15/14 ms**，全部 USABLE；**远离 t0002147 长期占用的 8650/8652/8654**，撞车概率最低。
- 起跑前逐端口 10s 内 POST 探活；BUSY 按序降级：`8665 → 8664 → 8663 → 8662 → 8661 → 8660 → 8658 → 8657`。
- 🚫 禁用 `8650/8652/8654`（占）、`8659/8668`（7.1–7.3s 慢，会拖慢整轮）。
- 报告里列出**实际使用的 4 个端口 + 每次探活结果**。



> 用户令（原文）：「zhulong 启动 r4/r5。跑完 (N′) 5-run后，再测一次 full，这次用 deepseek-v4-pro-cloud 的apikey」
> 前置已达成：**r3 ✅ 81.5% (123/151)**（Path A 修复，4 shard 31/30/31/31 极一致）；当前 3/5，mean 76.97% provisional。

**① r4 + r5（串行，先把 (N′) 5-run 补齐）**
- 配置**完全不变**：(N′) 唯一变量 `EDA_RUNCODE_READBACK=none`、OMEGA=high、BUDGET=0、LAGGED=0、V3 自探索 ON、full harness、`-p 4`、模型 **`deepseek-v4-pro-fp4`**（**不要换**）、cline 3.0.51 不动。
- **端口**：**统一用 `8666 / 8667 / 8669 / 8670`**（用户 23:3x 直令；RUN_ID 90 实测 14–19ms 全可用，且远离 t0002147 占用的 8650/8652/8654 段）⇒ **起跑前对每个端口做 1 次 10s 内 POST 探活，BUSY 的按序换下一组：`8665 → 8664 → 8663 → 8662 → 8661 → 8660 → 8658 → 8657`**（🚫 **禁用** 8650/8652/8654 被占、8659/8668 慢 7s）。
- 每轮结束：`ps -p <PID>` 判 GONE → 若 Step 7.1 auto-grade 报 FileNotFoundError，**沿用 r1/r2 的手动 regrade 模板**（`unset proxy` + `NO_PROXY=10.129.32.75` + `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`）。
- **若 regrade 再次出现 shard 全 timeout**：直接复用 r3 成功的 Path A 手法 —— `run_on_sandbox.py` 按 shard 直跑、绕开 `run_eval.py` 分片，写**独立输出文件**（`execution_results_shard_N_retest.jsonl`），不覆盖原产物。
- 判据（十三）：`timeout ≤ 10`、0 infra、0 exec_err。Pass@1 任何值有效，**不因低分重跑**。
- 收口后：**5/5 mean ± std** 写入 `zhulong_results.md` S1.readback_none 节 + `6_exp.tex` `tab:readback-cost` (N′) 行 + `tab:ablation-harness` (N) Mean read-backs；**n<5 不得写 ±**。

**② 5-run 收口后 → 再测一次 full（用 `deepseek-v4-pro-cloud` 的 key）**
> ⚠️ 用户指定「用 deepseek-v4-pro-cloud 的 apikey」。**执行前必须先做 canary**，不许直接开 5-run：
> 1. **canary**（本机 `.29` 直连、剥 proxy、**不打印 key**）：`deepseek-v4-pro-cloud` @ `/cloud/v1`，用**现有 key 逐个试**，记录 `HTTP` + `model` 字段 + `content` 是否非空。
>    - 已知可用：key 末 8 位 **`8aa0785e`**（`02_088EE9...e13f4f37-...-044c8aa0785e`）→ 10-19 03:50 探针 `deepseek-v4-pro-cloud` **HTTP 200** ✅。
>    - 已知不可用：`88ea2f23`（glm 的 key）访问 pro 族 **必 403**（该 key 无 pro 家族权限）。
> 2. **只有 canary 200 且 content 非空**才开跑；403/429/空内容 → **报 blocker，贴 HTTP 原文，不自行改用其他 key 硬跑**。
> 3. **「full」= readback 的 F 档（`EDA_RUNCODE_READBACK=full`）**，不是 (N′)。这是**新的对照臂**：`(F) 档 × deepseek-v4-pro-cloud`。
>    - 其余配置对齐现有 (F) fresh 5-run（OMEGA=high / BUDGET=0 / LAGGED=0 / V3 自探索 ON / full harness / `-p 4`）。
>    - 跑 **5 轮**，每轮同 ① 的 regrade 与 Path A 兜底手法。
> 4. **口径披露（必须写进报告）**：这一臂与既有 (F) 的差别是 **模型部署不同（cloud vs fp4）**，须在 `zhulong_results.md` 与论文表**显式注明**「cloud vs fp4 部署不同，不可与既有 (F) 行直接混算」；n<5 不写 ±。
> 5. 5 轮收口后：mean±std → 新表行 `(F) @ pro-cloud` → 更新 MEMORY + `zhulong_results.md`，commit `zhulong B: full × pro-cloud 5/5`。

**③ 纪律**
- 串行：先 r4→r5 收口，**再**做 ②，不得交叉并行抢端口。
- 🚫 不改 `run_cli.sh` / `run_cline_script.sh` / cline 版本；🚫 不动 t0002147；🚫 不杀 loop/relay。
- 端口探活与 kill 一律**显式 PID**（🚫 `pkill -f` 带自身子串）；长输出必须 `cut`。
- MEMORY 心跳 **≤6 行**（文件已 33KB，每次唤醒先滚 1-2 条旧 📦 块到 daily）。


### 📦 已归档（06:3x，batch 5）：三十（P1 排队 N′/B 成本）

> **已闭合**：(B) 成本 5-run 零 GPU 完成（22.3±3.3 / 3.73±0.72h / 7.6±3.4）；(N′) 5-run 进行中（本文件 06:3x 块承接）。原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 0. 🎯 当前状态速览（每次唤醒先看这里）

| 项 | 值（**2026-10-04 运维更新**）|
|:--|:--|
| **环境** | ⚠️ **两服务器独立挂载**：当前 2.12 开发机路径前缀为 <code>/nas_train/</code>；最终运行目标 36.15 路径前缀为 <code>/nasdata/</code>。评测代码 <code>eda_fastmcp</code> 在 36.15 上位于 <code>/nasdata/app.e0031982/code/eda_fastmcp</code>（未迁移）。旧 task book 中 <code>/nasdata/</code> 开头的路径仍然有效。 |
| **当前阶段** | ✅ **冻结令已解除；编排模型已切换为 glm-5.2（deepseek-v4-pro-fp4 额度已耗尽）；agent 可正常推进。** |
| **编排模型** | `glm-5.2`（`02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23` · `http://agi-gateway.cxmt.com/cloud/v1`） |
| **已完成（探路 1-shot）** | ✅ 组件 `pure_llm` 11.4% / `rag` 70.3% / `wo_retrieval` 81.6% / `full` 84.8%；✅ S2 Φ `k10` 75.3% / `k3` 69.0% / `k1` 60.8% / `lagged` 84.2%（r2 修复后 98.1% 满分） |
| **旧 5-run 进行到哪** | ⏸ 旧 S1（`omega_low`）r1=81.6 / r2=82.3 ✅；r3 因 **infra 作废**（license 耗尽 + shard0/1 端口 8664/8665 宕 + `/home` 磁盘 <8G）自 9/30 停摆至今 |
| **🚫 不做** | `(H+E)` 档 · `phi_unbounded`（≡ full 锚点）· 主基座 `deepseek-v4-pro-fp4` 的模型消融臂（≡ full×5 锚点，不重跑）。**注**：`wo_sandbox`(=rag 已测) / `wo_selfexpl`(已测·运维令二十六排队干净重测) 不再「暂缓」。 |
| **🔄 试验次序** | **已调换：Phase B（大模型消融）→ C1（组件）→ C2（S2Φ）→ S1（保真度）**。因 `deepseek-v4-pro-fp4` 额度 403 阻塞 C1，先跑 Phase B（4 模型均使用独立 key/endpoint，不受 pro-fp4 限制）|
| **叙事** | 一顿合并：**B → C1 → C2 → S1**，「单任务书 + 单循环」串行 75 轮全量 mean±std，回填 6 表 56 个 `[TBD]` |

### 📦 已归档（2026-10-20，batch 6）：运维令 十四 ~ 二十四（10-13 ~ 10-15 批次）

> 均已闭合（echo 数据/消融建议书/paper 编译/SKILL-Tcl 并入/沙盒暂停-恢复撤销等）。**常驻纪律保留**：每次刷新论文前 `git pull` 读 `doc/ZhuLong_DAC2027/zhulong_results.md`；口径=EDA-Scripting-Bench 449（PyAether 158 + SKILL 158 + Tcl 133）；SKILL/Tcl 数字只认 zhulong_results.md 现存值，未齐标 pending，🚫 凭印象编造。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 📦 已归档（06:4x，batch 7）：十三（75% 下限规则）+ 预留追加块

> 均已闭合/长期未使用，原文移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 🧭 运维规程 · 2026-10-06（**【agent 归档 MEMORY + 任务书】** —— 由你自己滚，不再由运维代劳）· 常驻

> **用户裁定**：「运维归档任务书不是长久之计」。`MEMORY_ZHULONG.md` 一直是 **agent 自滚**（不经运维）⇒ **任务书同理**。**本轮起：MEMORY + 任务书，两样都由你自己滚。**
> **判据**：两者 **均 ≤32KB**；**>40KB = 红线 ⇒ 必须先归档再提交**。
> **做法 = 只「搬迁」、不改内容**：① 已闭合内容（已执行完/已作废的运维块、已完成轮次正文、较早流水）**原文**搬入 `run/ZHULONG_TASK_ARCHIVE.md`（无则新建）/ `daily-memories/<日期>.md`；② **留 1 行指针**；🚫 不改小节编号/标题；🚫 **不新增/不改写任何指令**（本区作者仍是运维）。
> **护栏**：搬前 `git pull --rebase --autostash`；**只搬「最新活跃块之下」的已闭合块**（保留最上面 1–2 个未完成块）；冲突**保留双方**；提交用 `zhulong 归档: …` 前缀。
> **本轮动作**：本任务书现 ≈**29KB**（在上限内）⇒ 暂时**无需归档**；一旦 >32KB 即自行滚动。


### 🧭 运维规程 · 2026-10-06（**【每轮唤醒必须自己 commit+push】** —— 不许依赖 loop 兜底）· 常驻

> **用户指令（2026-10-06）**：与 BaiZe 四线同口径 —— **每条线每次唤醒都要推送**。本线此前明文写「靠外层 loop 每 ~5h 兜底」⇒ **自本轮起作废该口径**（§11 已同步修改）。
> **为什么**：运维**只能靠 git 判断你是死是活** —— 2026-10-06 data 线心跳文件近 2h 未更新，被**误判成卡死并上机排查**。🚫「loop 每 N 小时兜底」**不再作为交付保障**，只是保险丝。
> **每轮唤醒结束前，按顺序做完这 4 件事，再置 `WAITING` / 去睡**：
> 1. **写心跳**：更新 `run/MEMORY_ZHULONG.md` 顶部状态头 / 执行看板 / 成绩表 + 追加 1 行操作流水（`[HH:MM] 干了什么 + 关键原始输出 1–2 行`）。
> 2. **写日报**：`run/daily-memories/<YYYY-MM-DD>.md` 追加本轮（**当天文件必须建**）。
> 3. **自己提交 + 推送**（🚫 不许等 loop 兜底）：`git pull --rebase --autostash` → `git add -- doc/ZhuLong_DAC2027/run doc/ZhuLong_DAC2027/ZhuLong_DAC2027` → `git commit -m "zhulong <阶段/轮次>: <一句话>"` → `git push origin main`。🚫 **绝不用 `git add -A`**（多项目共用工作副本，会卷入别线在途文件）。
> 4. **闭环自检**：`git status -sb` ⇒ 无 ahead / 无 behind。**push 失败**（Forbidden / 网络）重试 1 次；仍失败 ⇒ 把**报错原文**写进心跳，**下轮第一件事补推**。
> ⏱️ **判死判据（硬）**：**心跳文件 >60min 无新提交 ⇒ 按卡死处理**（不再等你）。**你干得再多，心跳不动 = 仍会被判死。**


### 📦 已归档（2026-10-20，batch 4）：运维令 十二 / 十一 / 十 / 九 / (一)~(八)10-10 / (二)~(五)10-09

> 均已闭合（full_v3 5/5=82.1±3.0% 已交付、r2–r5 已完成、RAG/沙盒排查已收口）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。需要时再读。


> **来源**：用户 2026-10-08 观察。根因 = **loop 进程环境里没有 `https_proxy`**（脚本不 export 代理、完全继承启动 shell；只在调 cline 时 `env -u` 剥代理，而 **git 访问 GitHub 必须走代理**）。

**现状（已核对 `zhulong_loop.sh` 源码）**：
- 脚本**无**任何 `export https_proxy=...` —— 代理靠启动 shell 注入。
- 第 117 行 cline 调用 `env -u http_proxy -u https_proxy ...`（剥代理给 cline）—— **这只作用于 cline 那一行**，不影响 loop 自身的 git。
- `git_sync_and_push()`（第 54–103 行）里的 `git fetch origin` / `git push origin main` **直接用 loop 进程的环境** → 若该环境无 `https_proxy` → GitHub 不通 → `timeout 120 git fetch` 触发 → `[push] fetch FAILED (network?) - skip this cycle.` → 永远推不出去 / 拉不回来。

**正确代理值**（与 eval 启动、BaiZe 线一致）：
```
https_proxy=http://172.19.92.23:13128
http_proxy=http://172.19.92.23:13128
```

**你要做的（每次唤醒自检 + 必要时修复）**：

1. **查 loop 进程环境有没有代理**：
   ```bash
   _LPID="$(pgrep -f 'zhulong_loop.sh' | head -1)"
   [ -n "$_LPID" ] && tr '\0' '\n' < /proc/$_LPID/environ | grep -iE 'https_proxy|http_proxy' || echo "NO_PROXY_IN_LOOP"
   ```
   - 有 `https_proxy=http://172.19.92.23:13128` → ✅ 正常，无需操作。
   - 无 / 值不对 → ❌ 进入第 2 步修复。

2. **若 loop 缺代理 → 重启 loop 并显式注入代理**（详细 bash 脚本已归档至 `ZHULONG_TASK_ARCHIVE.md`·2026-10-18·该修复已于 10-08 执行完毕，loop 持续带代理运行）：核心 = `pkill -f zhulong_loop.sh` → `export https_proxy=http://172.19.92.23:13128 http_proxy=...` → `setsid bash zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &` → 复核 `/proc/$PID/environ` 含 `https_proxy`。

3. **回报**：把自检结果（有无代理 / 是否重启 / 新 PID + environ 证据）写进 `MEMORY_ZHULONG.md` 操作流水 1 行。

**红线**：
- 🚫 **不要改 `zhulong_loop.sh` 源码**（加 `export` 是可选项，但当前先靠启动环境注入；若你判断有必要在脚本里加 `export https_proxy=...`，**先在流水里写明理由再改**，且只加在 `git_sync_and_push` 之前、不要影响 cline 那行的 `env -u`）。
- 🚫 重启 loop **必须带 `setsid` + 重定向**（否则随 ssh 会话断开而死，血的教训）。
- ✅ 若 loop 当前正带代理且健康，**什么都不用做**，流水记一句「自检通过」即可。
- ✅ 这条指令**常驻**：以后每次唤醒顺手 `tr '\0' '\n' < /proc/$(pgrep -f zhulong_loop.sh|head -1)/environ | grep -i proxy` 扫一眼。

### 📦 已归档（2026-10-20，batch 5）：运维令 10-08(一) / 10-05(四~八) / 10-04(全)

> 均已闭合（HTML 报告已交、ops 中继稳定、config dir 隔离已落地、试验次序 B→C1→C2→S1 已生效、环境迁移已落地）。原文（1-line 指针）移至 `run/ARCHIVE_ZHULONG_TASK.md`。

### 切臂（5 轮跑完、算好 mean±std 后，启动下一臂前执行）

```bash
cd $BASE_DIR
# 按 STAGE 选一条切换脚本（S1/C1/C2；B 不切 set_ablation，改用 cline auth，见下）
$BASE_DIR/venv/bin/python scripts/set_s1_fidelity.py <ARM>      # S1: <ARM>∈{omega_low, readback_binary, readback_none}
$BASE_DIR/venv/bin/python scripts/set_ablation.py <CONFIG>      # C1: <CONFIG>∈{pure_llm, rag, wo_retrieval, full}
$BASE_DIR/venv/bin/python scripts/set_s2_phi.py <ARM>           # C2: <ARM>∈{phi_k10, phi_k3, phi_k1, phi_lagged}
bash scripts/stop.sh && bash scripts/start.sh && sleep 3 && tail -20 logs/app.log
```

> ⚠️ **改写 `.env` 的脚本必须串行 `&&` 链执行，严禁并发**（曾并发截断 `.env`）。核对：核心 4 工具 visibility 正确，对应 ENV flag 已写入。

### 启动一轮（脱离进程组）

```bash
cd $BASE_DIR
setsid bash scripts/run_cline_script.sh -p 8 -n > /tmp/ABL_<TAG>_r<N>.log 2>&1 < /dev/null &
```

> 工具可能超时/无输出，但进程已脱离 → **不算失败**；不要重复启动同一轮。启动后 `PHASE=running`、`WAITING=1`。

### 检查本轮是否结束

```bash
cd $BASE_DIR
pgrep -f '^bash scripts/run_cline_script'
```

- 有输出 → 还在跑，**什么都不做**退出（`WAITING` 保持 1）。
- 无输出 → 已结束，进入打分。

### 打分（Pass@1；用 grep，别用 run_eval.py）

```bash
cd $BASE_DIR
grep -E 'pass \(|评估结果汇总|PASS_RATE' /tmp/ABL_<TAG>_r<N>.log | tail -5
```

> 以 log 里 `pass (xx.x%)` 为 Pass@1 口径。`run_eval.py --latest 1` 是完整重评会超时，**不用它做口径**。

### 模型切换（仅 STAGE=B；full 配置不切 set_ablation）

| 模型 | `-m` 参数 | `cline auth` 命令（⚠️ key 可能过期，启动 Phase B 前先核；完整 key 以 `ablation_run_task_model_full.md` 为唯一源）|
|:--|:--|:--|
| `glm-5.2` | `glm-5.2` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23 -b http://agi-gateway.cxmt.com/cloud/v1 -m glm-5.2` |
| `deepseek-v4-flash` | `deepseek-v4-flash` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_c43c1f4a-03c6-4148-b722-f4c8604c78d3 -b http://agi-gateway.cxmt.com/v1 -m deepseek-v4-flash` |
| `kimi-k2.6-cloud` | `kimi-k2.6-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_80a707b0-4402-4c19-88d1-a3d4ebbf9a9f -b http://agi-gateway.cxmt.com/cloud/v1 -m kimi-k2.6-cloud` |
| `doubao-seed-2.0-pro-cloud` | `doubao-seed-2.0-pro-cloud` | `cline auth -p openai -k 02_088EE9051AAE4BF0ABFC7130331BF697_3dd97aea-258e-4a53-a290-4f1425cdc15f -b http://agi-gateway.cxmt.com/cloud/v1 -m doubao-seed-2.0-pro-cloud` |

## 7. 🧭 推进逻辑（每次唤醒严格只走一步）

### 前置校验
读 `MEMORY_ZHULONG.md`「操作流水」最后 3 条，检查有无 `❌ EVAL_FAILED` 或 `⚠️`；有未处理异常 → 先重试（重打分 / 重启本轮）再按正常流程推进。

### 步骤 0（PHASE=init）
1. infra 三项校验（见运维指令区）：`/home` 磁盘 ≥~8G + 8664/8665/8653/8669 全 OPEN + `run_code` 可执行。
   - 不满足 → `WAITING=1` 原地等，退出（下轮复检）。
2. canary：故意触发一次应被拒的调用，确认反作弊 PreToolUse hook 生效；**未被拒 → 立即停，本批作废**。
3. 切 `S1.omega_low` → 启动 r1 → `PHASE=running`、`WAITING=1`。

### 步骤 A（PHASE=running）
执行「检查本轮是否结束」：
- **pgrep 有输出** → 什么都不做，退出。
- **pgrep 无输出** → 「打分」：
  - 成功 → 记成绩，`ROUND+=1`：
    - `ROUND<=5` → 启动本臂下一轮（`PHASE=running`、`WAITING=1`）
    - `ROUND>5` → 算 mean±std（± 只加 Pass@1），`PHASE=just_finished`、`WAITING=0`
  - 失败 → `❌ EVAL_FAILED`、`ERROR_COUNT+=1`；<3 重试，>=3 强制推进并照实记。

### 步骤 B（PHASE=just_finished）
按 §5 轮转矩阵切下一臂（或 `done_all`）。切到新 STAGE 先 canary；切完启动该臂 r1。

### 步骤 C（PHASE=done_all）
什么都不做，退出。

### infra 作废规则（吸取旧 S1 停摆教训）
打分时发现整批作废（license 耗尽 / 端口宕 / 磁盘 <8G）→ **不计数**、记 `⚠️ infra`、`WAITING=1` 原地复检，三项恢复后再重跑该轮。**绝不拿作废批冒充有效分。**

## 8. ⚠️ S2 Φ 语义约束（最容易做错，逐字遵守）

1. 预算约束的是「能执行 / 能观测多少次」，不是「何时提交」；在工具边界拒绝调用，agent 收 error 后继续自主跑，**严禁**逼迫/提示提前提交。
2. 必须同步报告 `Converged (%)`（`finish_reason==completed` 占比），紧挨 Pass@1。
3. k 臂：`deny_reason` 含 `[PHI-BUDGET-EXHAUSTED]` 的 trace 数 >0，并记 `Mean read-backs`。
4. lagged：单槽缓冲滞后 1 次执行；核对 `reported_call_index` 与实际调用差 ==1（否则该臂作废）。trace_key 已在探路修复（SSE session 身份作键），Phase C2 前 `grep 'ctx.session' main.py` 核修复仍在。
5. 详见 `ablation_run_task_component_s2_full.md` §语义约束 与 `ablation_run_task_s2_1shot.md`。

## 9. 📊 成绩记录口径（README §4.1，写 MEMORY 成绩表）

- `Pass@1` → `mean ± std`（5 轮；`std=sqrt(Σ(xᵢ-μ)²/(n-1))`，1 位小数）。
- `Δ` 列 → 由 mean 相减，**不加 ±**。
- `Converged (%)` / `Mean read-backs` / `Avg/Trace` → 单值，**不加 ±**。
- S2 臂额外记 `Converged (%)` + `Mean read-backs`；模型臂额外记 `Δ vs 主基座`。

## 10. 📉 记忆维护规程（硬性）

- `MEMORY_ZHULONG.md` **与 `ZHULONG_TASK.md`（全文=prompt）** 上限均 **≤ 32KB**（红线 40KB）；超了就把较早流水滚动到 `daily-memories/<条目日期>.md`（原文不改，追加）。
- **任务书自己滚（2026-10-06 用户裁定）**：任务书的归档**由本线 agent 自己做**（与 MEMORY 同机制）—— 只把「已闭合」内容**【原文】搬入** `run/ZHULONG_TASK_ARCHIVE.md`（**留 1 行指针**；**不新增/不改写任何指令**，本区作者仍是运维）。
- 顶部必须保留：`WAITING:`（行首，只出现一次）+ 状态头 + 执行看板 + 成绩记录 + 最近 ~20 条流水。
- 旧文件（`MEMORY.md` / `MEMORY_s1_full.md` / `MEMORY_s2_1shot.md` / 三个 `ablation_run_task_*.md`）为**只读历史参考**，不改。
- `WAITING` 纪律：eval 跑起来置 1；打分推进后视情况置 0；infra 不就绪置 1。

## 11. 🔀 git 规程

- 成果落 `MEMORY_ZHULONG.md` + `daily-memories/` + 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`（回填 `[TBD]` 时）。
- ⚠️ **你自己每轮唤醒必须 commit+push**（见上方「🧭 运维规程 · 2026-10-06」）；外层 loop 每 ~5h 兜底 commit+push **只是保险丝、不是你的交付手段**（只 add `doc/ZhuLong_DAC2027/run` + `doc/ZhuLong_DAC2027/ZhuLong_DAC2027`）。
- 评测代码 `eda_fastmcp` 在仓库外，由它自己的 git 管理，不在此提交。
- 回填论文数字前按 README §6.1 规则：同表 `Δ` 列与正文引用的同一数字**必须同步改**，防表文矛盾。

## 12. 📁 历史与详细规格归档

- 三个旧 task book（`ablation_run_task_{s1_full,component_s2_full,model_full}.md`）保留，作为**逐臂详细规格**（尤其 S2 代码前置依赖、模型切换明细）。
- `ablation_run_conductor_serial.sh` 及其它 `ablation_run_loop_*.sh` **不再使用**（已被本单任务书 + 单 loop 取代；只读参照）。
- 权威口径以 `doc/ZhuLong_DAC2027/README.md` §2/§4.1/§5/§6/§8 为准。
