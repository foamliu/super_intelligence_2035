# ZHULONG_TASK.md — ZhuLong（DAC2027）EDA 消融评测 · 合并任务书

## 🔧 运维指令区（OPERATOR NOTES）— 每次唤醒必须先读本区

### 🧹 运维总则 · 2026-10-18（禁令作用域清理）
- **保留（全局有效）**：不伪造、不泄密、不杀健康训练、不覆盖他线产物、不绕过验证/实名/风控。
- **降级为局部**：旧块里的“等运维许可 / 不重启 / 暂停 / 不开跑 / 不碰 X”只在**该块任务**内有效；与最新用户令或最新任务块冲突时，**以最新块为准**。
- **已闭合旧块**不再作为禁令来源；唤醒时按各线体积规程归档到 `ARCHIVE_*`，不要让它继续占用 prompt。


> 本节由**外部运维**通过 git 修改。**agent 禁止修改本节**（只写 `MEMORY_ZHULONG.md` / `daily-memories/` / `run/` 下自建脚本 / 论文树 `ZhuLong_DAC2027/ZhuLong_DAC2027/`）。

### 🔄 运维指令 · 2026-10-20 09:0x（**先 regrade r4′ 看成绩，再决定是否换端口**）· 用户直令 · 最高优先

> 用户令（09:0x 决策）：r4′ 已自己收口，MCP timeout=156 低于基线 r2 的 235，**先 regrade r4′ 看 Pass@1，若有效则用 r4′，不急着换端口重跑**。
> **背景**：08:2x 令「停 r4′ → 换端口重跑」基于"r4′ 有很多沙盒超时"的判断。但 ops RUN_ID 94（09:03:29）实测：
> - r4′ PID 1462342 **已 GONE**（06:31 起跑，09:03 前收口，约 2.5h）—— agent 08:55 那轮 git pull 时机早于 08:50 push，**未拉到 08:2x 令**，r4′ 在旧端口 8666/8667/8669/8670 上自己跑完了。
> - r4′ 最终 **real_MCP_32001=156**（**低于**历史基线 r2 的 235）·run_code_calls=930（正常，r4 旧轮 928）·pass_rate_lines=0（**尚未评分**）。
> - 新端口 8663/8666/8667/8670 **全可达**（6-11ms）；旧端口 8669 也 OK（没坏，之前 BUSY 是 worker 轮换）。
> ⇒ **08:2x 令"停 r4′"动作无意义（r4′ 已不在跑），作废；改为先 regrade r4′ 看成绩再决定**。

#### ① 手动 regrade r4′（batch `2026_1020_063134`）
- 照 r4 regrade 模板 `/tmp/run_readback_none_retest_r4_regrade.sh`，**改 GEN_FILE=batch `2026_1020_063134`** + 端口 8666-8670 + `unset https_proxy http_proxy` + `NO_PROXY=10.129.32.75` + `EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework`。
- regrade 前先 grep log 确认 r4′ 收口状态：`grep -ac 'pass ([0-9]' /tmp/ABL_readback_none_retest_r4b.log`（应为 0 或评分行）、`tail -5 /tmp/ABL_readback_none_retest_r4b.log`（看收口尾）。
- regrade 输出到独立目录，**不覆盖 r4′ 原始产物**。
- 记录：Pass@1（pass/158）、task timeout 数、exec_err、infra error、gen-success/fail。

#### ② 判据（判据十三 + 本令补充）
- **r4′ 有效** ⟺ Pass@1 ≥ **75%** 且 task timeout ≤ 10 且 0 infra 且 0 exec_err。
  - ⚠️ 注意：判据十三的 "timeout" 指**任务级 task timeout**（单次执行 2500s 超时），**非** MCP 60s 客户端超时。r4′ 的 156 次 MCP 60s-timeout 是客户端侧，**不计入** task timeout 判据（r1/r2/r3 也有类似量级 MCP timeout 但均判有效）。
- **r4′ 有效** → 用 r4′，**起 r5′**（同 r4′ 配置：fp4/READBACK=none/OMEGA=high/BUDGET=0/LAGGED=0/V3自探索ON/-p 4/**端口 8666/8667/8669/8670 即可，不必换端口**/cline 3.0.51·`export PYTHON=$PWD/venv/bin/python`）→ 5/5 mean±std（r1,r2,r3,r4′,r5′）→ 更新 zhulong_results.md / 6_exp.tex → full@pro-cloud 5 轮。
- **r4′ 无效**（Pass@1 <75% 或异常）→ 按 08:2x 令换端口 **8663/8666/8667/8670** 重跑 r4″（ops RUN_ID 94 已确认 4 端口全可达）。r4′ 标 INVALID 不用。

#### ③ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env`；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- **本令优先级高于 08:2x**：若 r4′ 有效则**不必换端口重跑**（省 3-4h）；仅当 r4′ 无效才回退到 08:2x 换端口方案。
- commit：`zhulong S1: r4' 收口(MCP 156<基线235) -> 先 regrade 看成绩 -> 有效则用 r4' 起 r5' / 无效则换端口重跑`。

### 🔄 运维指令 · 2026-10-20 08:2x（**停 r4′ → 重启 8090 → 换端口 8663/8666/8667/8670 重跑 r4″**）· 用户直令 · 最高优先【已被 09:0x 取代·历史·仅 r4′ 无效时回退】

> 用户令（原文）：「**监测到 r4' 有很多沙盒超时。重启，使用下面4个端口：8663,8666,8667,8670**」
> **背景**：r4′（PID 1462342·batch `2026_1020_063134`）06:3x 起跑，巡检 #1（30min）real_MCP_32001=6 表观正常，但巡检 #2（65min）已升至 62、巡检 #3（100min）升至 110，**率 ~1.33/min 且持续抬头** ⇒ 沙盒后端再次进入降级轨迹（与 r4 旧轮 680 timeout 同型）。用户判定不可继续，令换端口重跑。
> **端口变更**：原 8666/8667/**8669**/8670 → 新 **8663**/8666/8667/8670（**替换 8669 → 8663**；8669 在历次巡检里多次显示 BUSY/worker 占用，疑似被邻居或自身 worker 拖累）。⚠️ **8663 此前在根 `MEMORY.md` §6 标记"作废"**，**本用户直令显式复活该端口**——按运维总则 2026-10-18「与最新用户令冲突时以最新块为准」，本次以本块为最新口径；agent 不必再核对旧"作废"标记。其余 3 端口（8666/8667/8670）不变。
> **本次唯一目标**：把 r4′ 干净停掉 → 重启 8090 wrapper（清累积降级）→ 用新 4 端口起 r4″，使 MCP 超时率回到历史基线（≈235/25 万行 量级，即 ≤ ~0.001/行）。

#### ① 先取证再停 r4′（**先留证再杀**）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
L=/tmp/ABL_readback_none_retest_r4b.log
echo "== r4' 停前取证 | $(date '+%F %T') =="
[ -f "$L" ] && {
  echo "  log_size=$(du -h "$L" | cut -f1)  lines=$(wc -l < "$L")"
  echo "  mention_timeout  = $(grep -ac 'timed out after 60s' "$L")"
  echo "  real_MCP_32001   = $(grep -ac 'MCP error -32001' "$L")"
  echo "  ACCESS_RESTRICTED= $(grep -ac 'ACCESS RESTRICTED' "$L")"
  echo "  run_code_calls   = $(grep -ac 'pyAether_MCP_server__run_code' "$L")"
  echo "  search_apis_calls= $(grep -ac 'pyAether_MCP_server__search_apis' "$L")"
  echo "  pass_rate_lines  = $(grep -ac 'pass ([0-9]' "$L")"
  echo "  32001 对应工具Top:"
  grep -a -B3 'MCP error -32001' "$L" | grep -aoE 'pyAether_MCP_server__[a-z_]+' | sort | uniq -c | head -6
}
echo "== r4' 进程清单（kill 前）=="
pgrep -af 'run_cline_script' | cut -c1-110
```
**停 r4′**：显式 PID 杀主进程 `1462342`，再扫孤儿 worker。⚠️ **教训（10-20 06:3x 已踩）**：`pgrep -f 'run_cline_script\.sh'` 会**误匹配 opencode 进程**（其 cmdline 含 ZHULONG_TASK.md 全文）→ **杀前必须核对 cmdline 是否真的是 `bash scripts/run_cline_script.sh ...`**，不可盲目 `pkill -f`。
```bash
# 只杀 cmdline 真正是 run_cline_script.sh 的进程（避开 opencode 误匹配）
for pid in $(pgrep -f 'run_cline_script\.sh'); do
  cmd=$(tr '\0' ' ' < /proc/$pid/cmdline 2>/dev/null | cut -c1-100)
  case "$cmd" in
    *bash\ scripts/run_cline_script.sh*|*run_cline_script.sh\ -p*)
      kill -TERM "$pid" && echo "TERM $pid :: $cmd" ;;
    *) echo "SKIP $pid (非 run_cline_script 主进程) :: $cmd" ;;
  esac
done
sleep 10
# 复检：剩余 run_cline_script 应只剩 opencode 误匹配（其 PPID 非 1 且 args 含 ZHULONG_TASK）
pgrep -af 'run_cline_script' | cut -c1-110 || echo "r4' 已停（无任何匹配）"
# 清孤儿 cline worker（batch 2026_1020_063134 的残留 task）
for pid in $(pgrep -f '2026_1020_063134'); do kill -TERM "$pid" 2>/dev/null && echo "orphan TERM $pid"; done
```

#### ② 记录 8090 状态 → 重启 → 验证（与 06:3x 块 ② 同型）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
PID=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$PID etime=$(ps -o etimes= -p $PID 2>/dev/null|tr -d ' ')s nlwp=$(ps -o nlwp= -p $PID 2>/dev/null|tr -d ' ')"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
NEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$NEW（旧 $PID）"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
```

#### ③ 起跑前健康冒烟（**必须 5/5 通过才起 r4″**，否则停手报 blocker）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  t0=$(date +%s%N)
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 200)
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK ${ms}ms"; else FAIL=$((FAIL+1)); echo "  #$i FAIL ${ms}ms"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 额外：用 run_code 打一次真实 pyAether 代码，确认沙盒端到端秒回
echo "run_code smoke:"
timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp -H 'Content-Type: application/json' \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"pyAether_MCP_server__run_code","arguments":{"code":"print(1)"}}}' 2>/dev/null | head -c 300
echo ""
```

#### ④ 用新端口起 r4″（**端口 = 8663,8666,8667,8670**）
- **先标 r4′ INVALID**（与 r4 旧轮同处置）：把 batch `2026_1020_063134` 在台账标注 **`INVALID(MCP timeout 抬头, 巡检 #3=110 且率持续上行)`**，**不参与 5-run 统计**；🚫 不覆盖其原始产物与日志（留作诊断证据）。
- **r4″ 起跑**：配置与 r1–r3 **完全一致**，**唯一变更是端口** ——
  - `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / **V3 自探索 ON** / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / **端口 `8663,8666,8667,8670`** / `export PYTHON=$PWD/venv/bin/python`（**别再漏**）。
  - 日志 `/tmp/ABL_readback_none_retest_r4c.log`；batch 新建。
  - ⚠️ **端口参数传递方式**：照 06:3x 块 r4′ 的起法（`run_cline_script.sh -p 4` + 显式 PORTS 环境变量或脚本参数），**只替换端口列表**；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED。
- **r4″ 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数 + 4 个新端口各自的可达性（`curl -s -m 5 http://10.129.32.75:<port>/` 或等价探活），确认新超时率回到历史水平（≤ ~0.001/行）、4 端口全部可达。
- r4″ 收口 → 立即起 **r5″**（同配置同端口）→ 5/5 齐（r1,r2,r3,r4″,r5″）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex` → 接 full@pro-cloud 5 轮。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 r4/r4′ 原始产物与日志（留证）；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- kill 一律**显式 PID + cmdline 核对**（避开 opencode 误匹配）；长输出 `cut`。
- 若重启 + 换端口后冒烟仍大面积超时 → **停手报 blocker**（届时再查 9006/沙盒机本身/8663 是否真可用），不要盲目第三次重跑。
- commit：`zhulong S1: r4' MCP timeout 抬头(110+) -> 停 r4' -> 重启 8090 -> 换端口 8663/8666/8667/8670 起 r4''`。

### 🔄 运维指令 · 2026-10-20 06:3x（**停 r5 → 重启 8090 → 重跑 r4/r5**）· 用户直令 · 最高优先【已被 08:2x 取代·历史】

> 用户令（原文）：「**停 r5 → 重启 8090 → 重跑 r4、r5**」
> **依据（运维实测对照）**：
> - 历史：`ABL_full_r2_new.log` **MCP-32001=235 次**，PASS_RATE **73.4% 仍正常**；`r2_new2` 72 次。
> - r4：**MCP 超时 680 次** ⇒ 结果 **31.0%**，99 个 completion 退化成字面量 `"pass"`。
> ⇒ 存在「超时比例临界点」，r4 已越过；**r4 数据不可用，不能进 5-run 统计**。
> - 「680」是**提及次数**，须与「实际 `error: MCP error -32001` 报错次数」分开计（本轮第 ① 步会分开记录）。
> - 8090 是**无状态 wrapper**（`main.py` + 4 工具透传；重活在 9006 RAG 与 10.129.32.75 沙盒），**重启无副作用**，且是历史常规操作（每次切消融都 `stop.sh && start.sh`）。

#### ① 停 r5 并留证（**先取证再杀**）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
L4=/tmp/ABL_readback_none_retest_r4.log
L5=/tmp/ABL_readback_none_retest_r5.log
# 分开统计：提及 vs 真正报错
for f in "$L4" "$L5"; do [ -f "$f" ] || continue
  echo "== $f ($(du -h "$f"|cut -f1)) =="
  echo "  mention_timeout = $(grep -ac 'timed out after 60s' "$f")"
  echo "  real_MCP_32001  = $(grep -ac 'MCP error -32001' "$f")"
  echo "  ACCESS_RESTRICTED = $(grep -ac 'ACCESS RESTRICTED' "$f")"
  echo "  run_code_calls   = $(grep -ac 'pyAether_MCP_server__run_code' "$f")"
  echo "  search_apis_calls= $(grep -ac 'pyAether_MCP_server__search_apis' "$f")"
  echo "  get_details_calls= $(grep -ac 'pyAether_MCP_server__get_api_details' "$f")"
  echo "  32001 对应工具Top:"
  grep -a -B3 'MCP error -32001' "$f" | grep -aoE 'pyAether_MCP_server__[a-z_]+' | sort | uniq -c | head -6
done
# 停 r5（只杀 run_cline_script 主进程及其子进程，显式 PID）
pgrep -af 'run_cline_script' | cut -c1-100
for pid in $(pgrep -f 'run_cline_script\.sh'); do kill -TERM "$pid" 2>/dev/null && echo "TERM $pid"; done
sleep 10
pgrep -af 'run_cline_script' | cut -c1-100 || echo "r5 已停"
```

#### ② 记录 8090 状态 → 重启 → 验证
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
echo "== 重启前 8090 =="
PID=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  pid=$PID etime=$(ps -o etimes= -p $PID 2>/dev/null|tr -d ' ')s"
ps -o pid,nlwp,rss,pcpu,args -p "$PID" 2>/dev/null | cut -c1-120
echo "  fd_count=$(ls /proc/$PID/fd 2>/dev/null | wc -l)"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"

echo "== 重启 =="
bash scripts/stop.sh; sleep 3
bash scripts/start.sh; sleep 8
NEW=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "  新 PID=$NEW（旧 $PID）"
echo "  health=$(curl -s -m 5 -o /dev/null -w '%{http_code}' http://localhost:8090/health 2>/dev/null)"
echo "  tools=$(curl -s -m 8 http://localhost:8090/tools 2>/dev/null | head -c 300)"
```

#### ③ 起跑前健康冒烟（**必须 5/5 通过才起 r4**，否则停）
```bash
cd /nasdata/app.e0031982/code/eda_fastmcp
OK=0; FAIL=0
for i in 1 2 3 4 5; do
  t0=$(date +%s%N)
  r=$(timeout 70 curl -s -m 65 -X POST http://localhost:8090/mcp \
      -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}' 2>/dev/null | head -c 200)
  t1=$(date +%s%N); ms=$(( (t1-t0)/1000000 ))
  if [ -n "$r" ]; then OK=$((OK+1)); echo "  #$i OK ${ms}ms"; else FAIL=$((FAIL+1)); echo "  #$i FAIL ${ms}ms"; fi
done
echo "SMOKE: ok=$OK fail=$FAIL"
# 若 tools/list 端点不对，改用你已知可用的 MCP 调用方式；核心判据是「5 次全部 <5s 返回」
```

#### ④ 重跑 r4'（替换 r4），收口后接 r5'
- **先删/隔离 r4 旧结果**（🚫 不要覆盖原始产物）：把 `2026_1019_235040` 相关 completion 在台账中标注 **`INVALID(680 MCP timeout, 99 gen-fail)`**，**不参与 5-run 统计**。
- **r4' 起跑**：配置与 r1–r3 **完全一致** —— `READBACK=none` / OMEGA=high / BUDGET=0 / LAGGED=0 / V3 自探索 ON / full harness / **`-p 4`** / 模型 **`deepseek-v4-pro-fp4`** / 端口 **8666,8667,8669,8670** / `export PYTHON=$PWD/venv/bin/python`（**这次别再漏**）。
- 日志 `/tmp/ABL_readback_none_retest_r4b.log`；batch 新建。
- **r4' 跑起来 30 分钟内必须报一次**：`real_MCP_32001` 计数 + `run_code` 调用数，确认新超时率是否回到历史水平（≈235/25万行 量级）。
- r4' 收口 → 立即起 **r5'**（同配置）→ 5/5 齐（r1,r2,r3,r4',r5'）→ mean±std → 更新 `zhulong_results.md` / `6_exp.tex`。

#### ⑤ 纪律
- 🚫 不覆盖 r1/r2/r3 产物与 r3 backup；🚫 不动 t0002147；🚫 不改 `.env` 的 READBACK/OMEGA/BUDGET/LAGGED；🚫 不启 full@pro-cloud（等 5/5 干净后再做）。
- kill 一律 **显式 PID**（🚫 `pkill -f` 带子串）；长输出 `cut`。
- 若重启后冒烟仍大面积超时 → **说明不是 8090 的问题，停手报 blocker**（届时再查 9006/沙盒）。
- commit：`zhulong S1: r4 INVALID(680 MCP timeouts) -> restart 8090 -> rerun r4/r5`。


### 🔬 运维指令 · 2026-10-20 06:0x（**P0：r4=31% 根因排查 —— 680 次 timeout 到底卡在哪个环节**）· 用户直令 · 最高优先

> 用户令（原文）：「zhulong r4 首先需要排查一下。你给我的只有现象，没有根因。比如 680 次 MCP timeout，到底是哪个环节超时？是 8090 的 MCP 服务呢，还是在 RAG 服务，还是在 run code .75 服务器的端口上。总归可以让 zhulong agent 调研一下啊。」
> **本次唯一目标**：把「680 次 `MCP request to pyAether_MCP_server timed out after 60s`」**拆成按调用点的归因表**，不允许只给现象。
> **本次不做**：不重跑 r4、不启 5-run、不改配置。**纯诊断**（可写脚本/可抓日志，但不动 `.env` 与运行中进程）。

#### 0. 已知事实（供你验证/推翻）
- r4 batch `2026_1019_235040`（23:50:40 起，~04:35 收口，约 5h），`-p 4`，端口 8666/8667/8669/8670，模型 fp4。
- gen-success **59** / gen-fail **99**（99 个 completion 是字面量 `"pass"`），exec_err 0。
- 已执行 59 题里 **49 通过（83%）** ⇒ 模型能力本身没问题，指向**调用链某一环降级**。
- eval log 计到 **680 次** `MCP request to pyAether_MCP_server timed out after 60s`。
- ⚠️ 该 60s 是 **MCP 客户端侧超时**，与会话无关，需定位它落在**哪个 server / 哪个工具 / 哪个端口**。

#### 1. 必须产出的「环节级归因表」（核心交付）

先把 log 里 680 次 timeout 的**原始行**抓出来，再按下列维度**逐条归类计数**（要求给出每类的数量 + 2–3 条样例行 + 行号/时间戳区间）：

| # | 环节 | 判定依据（从 timeout 行及其上下文提取） |
|:--|:--|:--|
| **A** | **8090 MCP server 本体**（进程在但无响应/被打满） | timeout 行前后是否有 `EDA_MCP_PORT=8090` 相关；同时查 8090 进程 CPU/线程/连接数随时间曲线 |
| **B** | **9006 RAG 服务**（检索服务超时，会导致 `search_apis`/`get_api_details` 卡住） | timeout 行是否伴随 `RAG`/`recall`/`search_apis`/`get_api_details` 字样；查 9006 进程状态 |
| **C** | **10.129.32.75 沙盒端口**（run_code 执行槽被占/慢） | timeout 行是否伴随 `run_code`/`/v1/run_code`/端口号 8666/8667/8669/8670；查是否出现 150s 级等待 |
| **D** | **本机 CPU/内存/负载**（`.29` 本身被压垮） | 用 r4 时段（23:50–04:35）的 `sar`/`vmstat`/`uptime` 或 dmesg OOM 记录佐证 |
| **E** | **外部争用**（t0002147 等同机邻居） | r4 时段是否有别的用户进程抢 CPU/端口；`/proc/pressure/*` 若有则贴 |

#### 2. 具体取证步骤（按序，全部只读）

**① log 原文挖掘**
```bash
L=/tmp/ABL_readback_none_retest_r4.log
# 1) timeout 总次数与时间分布（按 10 分钟分桶）
grep -a "timed out after 60s" "$L" | wc -l
grep -a "timed out after 60s" "$L" | grep -oE '^[0-9-]+ [0-9]{2}:[0-9]' | sort | uniq -c | tail -40
# 2) 每条 timeout 的上下文（前后 3 行），抽样 30 条
grep -a -n -B3 -A3 "timed out after 60s" "$L" | head -200 | cut -c1-180
# 3) 按工具名归类：timeout 行附近出现的工具名
grep -a "timed out after 60s" "$L" | grep -oE 'run_code|search_apis|search_apis_by_keyword|get_api_details|query_memory_bank|cimi_[a-z]+|probe_pyAether_code' | sort | uniq -c
# 4) 全 log 各工具的调用总数与失败数（做分母）
for t in run_code search_apis search_apis_by_keyword get_api_details; do
  printf "%-26s calls=%s\n" "$t" "$(grep -ac "$t" "$L")"
done
# 5) 是否有 150s / 连接错误 / RAG 字样
grep -acE '150 ?s|150s|Connection refused|ConnectionError|RAG|recall' "$L"
```

**② 三个候选环节的组件级健康（r4 时段是否降级）**
```bash
# 8090 MCP
ss -ltnp 2>/dev/null | grep -E ':8090|:9006' | cut -c1-140
PID8090=$(ss -ltnp 2>/dev/null | grep ':8090' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "8090 pid=$PID8090"; ps -o pid,ppid,etimes,pcpu,pmem,nlwp,args -p "$PID8090" 2>/dev/null | cut -c1-160
# 9006 RAG
PID9006=$(ss -ltnp 2>/dev/null | grep ':9006' | grep -oE 'pid=[0-9]+' | cut -d= -f2 | head -1)
echo "9006 pid=$PID9006"; ps -o pid,ppid,etimes,pcpu,pmem,nlwp,args -p "$PID9006" 2>/dev/null | cut -c1-160
# 关键：这两个进程的「启动时间」是否在 r4 时段内重启过（etimes < 现在-23:50）
date; echo "--- 若 etimes 小于距 23:50 的秒数 => r4 期间重启过 ---"
```

**③ 沙盒端口侧证据（区分「端口慢」与「MCP 侧慢」）**
```bash
# r4 时段端口是否有 150s 级等待（这正是 r3 被 t0002147 抢占的特征）
L=/tmp/ABL_readback_none_retest_r4.log
grep -acE 'run_code.*timed out|Request timeout \(150s\)|/v1/run_code' "$L"
grep -a -E 'Request timeout \(150s\)|8666|8667|8669|8670' "$L" | tail -10 | cut -c1-160
# 现在这 4 个端口是否仍健康（对照）
for p in 8666 8667 8669 8670; do
  ( out=$(timeout 10 curl -s --max-time 8 -X POST "http://10.129.32.75:$p/v1/run_code" -H 'Content-Type: application/json' -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null | head -c 12)
    [ -z "$out" ] && echo "$p BUSY" > /tmp/p20_$p || echo "$p OK" > /tmp/p20_$p ) &
done; wait
for p in 8666 8667 8669 8670; do echo "  $(cat /tmp/p20_$p 2>/dev/null)"; rm -f /tmp/p20_$p; done
```

**④ 系统层佐证（r4 那 5 小时 `.29` 是否被压垮）**
```bash
uptime; free -g | head -3
ps -eo pid,etimes,pcpu,pmem,user,args --sort=-pcpu 2>/dev/null | head -12 | cut -c1-150
dmesg -T 2>/dev/null | grep -iE 'oom|killed process' | tail -10 || echo "dmesg 不可读（正常）"
cat /proc/pressure/cpu /proc/pressure/io 2>/dev/null | cut -c1-120 || true
# 同期邻居占用
ps -eo user,etimes,pcpu,args 2>/dev/null | grep -E 't0002147|t0002997' | grep -v grep | head -6 | cut -c1-130
```

#### 3. 结论要求（**必须分档，不允许只写"MCP 超时"**）

产出下面这张表并给结论：
- 680 次中，**A/B/C/D/E 各占多少**（必须能加总到 680，或说明为何有未归类项）
- **主因是哪个环节** + 证据（贴 log 行号/时间戳 + 进程/端口状态）
- **是否存在「r4 时段某组件重启/降级」的时间吻合**（例如 8090 在 00:xx 重启，而 timeout 集中在那之后）
- **可复现性判断**：现在（诊断时）该环节是否已恢复？若已恢复 ⇒ 支持"瞬时降级"而非"配置错误"
- **对 r4 的处置建议**：**INVALID（infra 降级，应补跑 r4'）** / **有效（属模型方差，保留）** —— 给出你的依据，由运维拍板

#### 4. 纪律
- **纯只读**：不 kill、不重启 8090/9006/沙盒、不改 `.env`、不启任何 eval。
- 长输出 `cut -c1-180`；log grep 必须带 `-a`（二进制/长行），并用 `head`/`tail` 限流。
- 结果写 `MEMORY_ZHULONG.md` 心跳（≤6 行）+ `daily-memories/2026-10-20.md` 详细节，commit `zhulong diag: r4 680 MCP timeout attribution`。
- 🔴 **r5 继续跑，不要打扰**（PID 1296715）；本诊断与 r5 并行、互不影响。


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
