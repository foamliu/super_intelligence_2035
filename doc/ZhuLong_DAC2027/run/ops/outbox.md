# OPS OUTBOX — 中继回收的执行结果（ZhuLong DAC2027 版）

> **只增不改（append-only）**：每次执行在**文件末尾**追加一节。
> **最新结果在文件最下方**——`git pull` 后 `tail` 即可。
> 由 `zhulong_ops_relay.sh` 写入；**运维只读**，人不要手改本文件。

---

_（尚无执行结果。等待 `ops/inbox.md` 的 RUN_ID 1 被执行。）_

---

---

## RUN_ID 1 · 2026-10-04 16:53:58 · host=`hfeg0tedaap02` · exit=0

**命令**
```bash
# GIT_ROOT: 自动检测仓库根目录（36.15 → /nasdata/；2.12 → /nas_train/）
_GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '/nasdata/app.e0031982/code/super_intelligence_2035')"
echo "=========== 0. HOST/TIME ==========="; hostname; date '+%F %T'; id
echo "   GIT_ROOT=$_GIT_ROOT"
echo
echo "=========== 1. DISK (关键路径 + /home) ==========="
echo "-- /home --"; df -BG /home 2>/dev/null | tail -1
# 以下路径根据实际服务器挂载点自动探测
for mp in /nasdata /nas_train /nas_inference; do
  [ -d "$mp" ] && echo "-- $mp --" && df -BG "$mp" 2>/dev/null | tail -1
done
echo "-- /tmp --"; df -BG /tmp 2>/dev/null | tail -1
echo
echo "=========== 2. SHARD 端口（四路） ==========="
for port in 8664 8665 8653 8669; do
  if timeout 3 bash -c "echo >/dev/tcp/127.0.0.1/$port" 2>/dev/null; then
    echo "   port $port : ✅ OPEN"
  else
    echo "   port $port : ❌ CLOSED / UNREACHABLE"
  fi
done
echo
echo "=========== 3. EDA LICENSE（run_code 可用性） ==========="
# 自动检测 eda_fastmcp 位置
CODE_BASE=""
for cand in /nasdata/app.e0031982/code/eda_fastmcp /nas_train/app.e0031982/code/eda_fastmcp; do
  [ -d "$cand" ] && { CODE_BASE="$cand"; break; }
done
if [ -n "$CODE_BASE" ]; then
  echo "   eda_fastmcp 目录存在: $CODE_BASE"
  ls -1 "$CODE_BASE" 2>/dev/null | head -10 | sed 's/^/     /'
  for f in run_code run_code.sh; do
    if [ -f "$CODE_BASE/$f" ]; then
      echo "   $f 文件存在"
    fi
  done
  if [ ! -f "$CODE_BASE/run_code" ] && [ ! -f "$CODE_BASE/run_code.sh" ]; then
    echo "   ⚠️ run_code/run_code.sh 均未找到，检查实际入口"
    ls -1 "$CODE_BASE"/*run* 2>/dev/null | sed 's/^/     /'
    echo "   ❌ 无 run_code 入口"
  fi
else
  echo "   ❌ eda_fastmcp 目录不存在（在两台服务器上均未找到）"
fi
echo
echo "=========== 4. RUNNING PROCESSES ==========="
echo "-- zhulong loops --"
pgrep -af 'zhulong_loop\\.sh|zhulong_ops_relay' || echo "   (no zhulong processes)"
echo "-- other loops (Baize / data) --"
pgrep -af 'baize.*loop\\.sh|ops_relay\\.sh' || echo "   (no other loop processes)"
echo "-- eda/eval --"
pgrep -af 'eda_fastmcp|run_code|sandbox|eval' || echo "   (no eda/eval processes)"
echo
echo "=========== 4b. ZHULONG LOOP / RELAY 日志尾 ==========="
echo "-- tail /tmp/zhulong_loop.log --"
tail -n 8 /tmp/zhulong_loop.log 2>/dev/null | cut -c1-140 || echo "   (no /tmp/zhulong_loop.log)"
echo "-- tail /tmp/zhulong_ops_relay.log --"
tail -n 8 /tmp/zhulong_ops_relay.log 2>/dev/null | cut -c1-140 || echo "   (no /tmp/zhulong_ops_relay.log)"
echo
echo "=========== 4c. EDA_FASTMCP .env 关键 flag + git ==========="
if [ -n "$CODE_BASE" ] && [ -f "$CODE_BASE/.env" ]; then
  grep -iE 'OMEGA|READBACK|PHI|ABLATION|DISABLE|BUDGET|RECALL|PORT' "$CODE_BASE/.env" 2>/dev/null | cut -c1-140 | sed 's/^/     /'
  echo "   -- eda_fastmcp git --"
  ( cd "$CODE_BASE" && git status -sb 2>/dev/null | head -3 && git log --oneline -3 2>/dev/null ) | sed 's/^/     /'
else
  echo "   (no .env / CODE_BASE not found)"
fi
echo
echo "=========== 5. GIT STATUS ==========="
cd "$_GIT_ROOT" && git status -sb | head -8
echo "-- last 3 commits --"
git log --oneline -3
echo
echo "=========== 6. ZHULONG RUN DIR ==========="
ls -la "$_GIT_ROOT/doc/ZhuLong_DAC2027/run/" 2>/dev/null | head -25
echo
echo "=========== 7. CPU / MEM / GPU ==========="
lscpu 2>/dev/null | grep -E '^Model name|^CPU\\(s\\):|^Socket' || true
free -g 2>/dev/null | head -2
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader 2>/dev/null | head -2 || echo "   (nvidia-smi not available)"
echo
echo "=========== DONE ==========="
```

**输出**
```
=========== 0. HOST/TIME ===========
hfeg0tedaap02
2026-10-04 16:53:58
uid=9013(app.e0031982) gid=6002(app.adm) groups=6002(app.adm)
   GIT_ROOT=/nasdata/app.e0031982/code/super_intelligence_2035

=========== 1. DISK (关键路径 + /home) ===========
-- /home --
/dev/mapper/vgroot-lv_home      394G  371G        6G  99% /home
-- /nasdata --
10.251.9.180:/g0tedaap      527G  151G      377G  29% /nasdata
-- /tmp --
/dev/mapper/vgroot-lv_tmp       49G   25G       22G  54% /tmp

=========== 2. SHARD 端口（四路） ===========
   port 8664 : ✅ OPEN
   port 8665 : ✅ OPEN
   port 8653 : ✅ OPEN
   port 8669 : ✅ OPEN

=========== 3. EDA LICENSE（run_code 可用性） ===========
   eda_fastmcp 目录存在: /nasdata/app.e0031982/code/eda_fastmcp
     CLAUDE.md
     cleanup_tmp_gt.sh
     daily-memories
     Dockerfile
     docs
     kb
     logs
     main.py
     memory_bank
     MEMORY.md
   ⚠️ run_code/run_code.sh 均未找到，检查实际入口
     /nasdata/app.e0031982/code/eda_fastmcp/run_monday_eval.sh
     /nasdata/app.e0031982/code/eda_fastmcp/run_monday.sh
   ❌ 无 run_code 入口

=========== 4. RUNNING PROCESSES ===========
-- zhulong loops --
1071337 bash zhulong_ops_relay.sh
1071692 tail -f /tmp/zhulong_ops_relay.log
1239220 bash zhulong_ops_relay.sh
-- other loops (Baize / data) --
   (no other loop processes)
-- eda/eval --
21179 /home/app.e0030884/bin/bun /home/app.e0030884/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.js
28673 /home/app.t0002949/.local/bin/bun --inspect=127.0.0.1:0 --enable-source-maps -e const createJiti = require("/home/app.t0002949/T0002949/zhulong/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.t0002949/T0002949/zhulong/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.t0002949/T0002949/zhulong/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
31531 /home/app.vendor.ai.ruide01/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.vendor.ai.ruide01/sjp/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
36970 /home/app.vendor.ai.ruide01/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.vendor.ai.ruide01/sjp/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
407751 /home/app.e0041392/sandbox_fastmcp/.venv/bin/python /home/app.e0041392/sandbox_fastmcp/main.py
409936 /home/app.vendor.ai.ruide01/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.vendor.ai.ruide01/sjp/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
490382 /home/app.t0002596/miniforge3/envs/py310_env/bin/python /home/app.t0002596/devops/eda_fastmcp/main.py
502036 python /home/app.t0002147/mcp_0917/eda_fastmcp/main.py
574820 /home/app.vendor.ai.ruide01/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.vendor.ai.ruide01/sjp/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.vendor.ai.ruide01/sjp/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
633507 /home/app.vendor.ai.ruide01/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.vendor.ai.ruide01/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.vendor.ai.ruide01/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.vendor.ai.ruide01/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
691966 /nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python /nasdata/app.e0031982/code/eda_fastmcp/main.py
1136643 /home/app.e0023936/miniforge3/envs/py310_env/bin/python /home/app.t0002643/devops/eda_fastmcp/main.py
1260545 /home/app.e0017912/.local/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.e0017912/zl_dev1/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev1/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev1/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1265152 /home/app.e0017912/.local/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.e0017912/zl_dev1/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev1/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev1/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1591827 /usr/bin/node -e const createJiti = require("/home/app.e0017912/zl_dev/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1629574 /usr/bin/node -e const createJiti = require("/home/app.e0017912/zl_dev/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1680200 /home/app.t0002965/eda_fastmcp/.venv/bin/python /home/app.t0002965/eda_fastmcp/main.py
1684985 /usr/bin/node -e const createJiti = require("/home/app.e0017912/zl_dev/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1771968 /usr/bin/node -e const createJiti = require("/home/app.e0017912/zl_dev/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
1777403 /usr/bin/node -e const createJiti = require("/home/app.e0017912/zl_dev/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0017912/zl_dev/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
2135871 /bin/bash -c source /home/app.e0030209/.claude/shell-snapshots/snapshot-bash-1772583573099-yv16rh.sh && shopt -u extglob 2>/dev/null || true && eval 'export https_proxy=http://172.19.92.23:13128 && export http_proxy=http://172.19.92.23:13128 && source .venv/bin/activate && nohup python -m ops_agent.mcp.telemetry_api --host 0.0.0.0 --port 8080 > /home/app.e0030209/yc/product_ops_agent/logs/api.log 2>&1 & echo $! > /home/app.e0030209/yc/product_ops_agent/.pids/api.pid sleep 3 echo "API PID: $(cat /home/app.e0030209/yc/product_ops_agent/.pids/api.pid)" ps -p $(cat /home/app.e0030209/yc/product_ops_agent/.pids/api.pid) && echo "API service running" || echo "API service failed"' < /dev/null && pwd -P >| /tmp/claude-4699-cwd
2425434 python /home/app.t0002147/zhulong_mcp_self_evolution/eda_fastmcp/main.py
2691602 /home/app.e0023936/miniforge3/envs/py310_env/bin/python /home/app.e0023936/devops/2026-07-05/eda_fastmcp/main.py
2825718 tmux new -s eda_fastmcp_ser
2873402 python /home/app.t0002147/eda_fastmcp_tcl/eda_fastmcp/tcl_kb/eda_api_recall.py
3001278 bash /home/app.t0002965/eda_code_eval/watch_sandbox.sh
3278615 /home/app.e0023936/miniforge3/envs/py310_env/bin/python /home/app.e0023936/devops/eda_aether_sandbox/main.py
3511262 python /nasdata/app.t0002997/app.t0002997/proj/eda_fastmcp/main.py
3562386 /home/app.e0042624/.local/node/lib/node_modules/bun/bin/bun.exe --inspect=127.0.0.1:0 --enable-source-maps -e const createJiti = require("/home/app.e0042624/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
3565132 /home/app.e0042624/.local/node/lib/node_modules/bun/bin/bun.exe -e const createJiti = require("/home/app.e0042624/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
3565861 /home/app.e0042624/.local/node/lib/node_modules/bun/bin/bun.exe --inspect=127.0.0.1:0 --enable-source-maps -e const createJiti = require("/home/app.e0042624/eda_platform/node_modules/.bun/jiti@2.7.0/node_modules/jiti/lib/jiti.cjs"); const jiti = createJiti("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", { cache: false, requireCache: false, esmResolve: true, interopDefault: false }); Promise.resolve(jiti.import("/home/app.e0042624/eda_platform/sdk/packages/core/src/extensions/plugin/plugin-sandbox-bootstrap.ts", {})).catch((error) => {   console.error(error);   process.exitCode = 1; });
3596122 python3 -u server/sandbox_server/proxy_server.py
3820519 /nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python -m uvicorn eda_api_recall:app --host 0.0.0.0 --port 9006 --log-level info
4166747 /bin/bash -l -c cd /home/app.t0002638/eda_fastmcp && EDA_MCP_PORT=8661 nohup /home/app.e0023936/miniforge3/envs/py310_env/bin/python main.py > /tmp/eda_mcp_server.log 2>&1 & echo "Started with PID $!" sleep 3 ss -tlnp | grep 8661

=========== 4b. ZHULONG LOOP / RELAY 日志尾 ===========
-- tail /tmp/zhulong_loop.log --
[loop] 2026-10-04 16:52:19 wake up, invoking cline ...
[31merror:[0m error: unknown option '-b'
[loop] 2026-10-04 16:52:19 cline returned (exit 0), checking git sync ...
[loop] 2026-10-04 16:52:19 WAITING=0 (no blocker) → sleep 60s
[loop] 2026-10-04 16:53:19 wake up, invoking cline ...
[31merror:[0m error: unknown option '-b'
[loop] 2026-10-04 16:53:20 cline returned (exit 0), checking git sync ...
[loop] 2026-10-04 16:53:20 WAITING=0 (no blocker) → sleep 60s
-- tail /tmp/zhulong_ops_relay.log --
[zhulong-relay] 2026-10-04 15:20:25 started. repo=/nasdata/app.e0031982/code/super_intelligence_2035  poll=20s  fetch_every=3x

=========== 4c. EDA_FASTMCP .env 关键 flag + git ===========
     # EDA_MCP_PORT=19999 
     EDA_MCP_PORT=${EDA_MCP_PORT:=18890}
     EDA_MCP_TRANSPORT=sse
     # 格式: http://<host>:<port>/v1/traces
     # PROXY_PORTS=8664,8665,8653,8669
     PROXY_PORTS=8650,8651,8652,8654
     SANDBOX_PORT_HTTP=8655
     SANDBOX_PORT_TCP=8668
     # 格式: port:workdir,port:workdir,... (workdir 须用绝对路径)
     # 空/不设 → 回退单端口(SANDBOX_HOST:SANDBOX_PORT_HTTP / SANDBOX_WORKDIR, 行同旧版)
     # 启动: ./scripts/start_recall_api.sh  停止: ./scripts/stop_recall_api.sh
     RAG_RECALL_URL=http://localhost:9006/recall
     # RAG_RECALL_URL=http://localhost:9002/recall
     # RAG_RECALL_URL=http://10.252.32.15:9001/recall
     RAG_RECALL_TIMEOUT=25
     RAG_RECALL_URL_LOCAL=http://localhost:9010/recall
     # EDA_MCP_TOOLS_DISABLED = 当前被禁用的 MCP 工具（逗号分隔）
     EDA_MCP_TOOLS_DISABLED=clean_workdir,probe_pyAether_code,cimi_search,cimi_fetch,vqa,query_memory_bank,get_api_details,search_apis,search_api
     # 各 run_cline_script*.sh 读取自己对应的变量并 export 为 EDA_PROMPT_TEMPLATE，
     # S2 Φ 轴消融: 预算/滞后(由 scripts/set_s2_phi.py 维护; 改后须重启 MCP)
     EDA_PHI_BUDGET=0
     EDA_PHI_LAGGED=0
     EDA_OMEGA_FIDELITY=high
     EDA_RUNCODE_READBACK=full
   -- eda_fastmcp git --
     ## master...origin/master
      M .env
     ?? cleanup_tmp_gt.sh
     cb5c402c feat(ablation): S1 保真度轴 + S2 Φ 轴消融（hook/handler/检索降保真 + 元数据）
     5bdf4e87 refactor: 防泄题 hook 升级为白名单 + workspace 沙箱
     b2eda64e feat: 新增 PreToolUse 防泄题 hook（黑名单拦截 benchmark 答案/判题）

=========== 5. GIT STATUS ===========
## main...origin/main
?? doc/ZhuLong_DAC2027/run/.nfs00000000244eea8300001304
-- last 3 commits --
354d4dc zhulong-ops: dispatch RUN_ID 1 (36.15 environment survey, +loop/relay log tails + .env flags)
866f465 ops-relay: result @ 2026-10-04 16:51:25
19b2fe7 data: wake99 patrol l1_en_hq 916/6006 gpic 2260/8001 progressing; roll wake90 to daily archive (MEMORY<=32KB)

=========== 6. ZHULONG RUN DIR ===========
total 620
drwxr-x--- 6 app.e0031982 app.adm   4096 Oct  4 16:46 .
drwxr-x--- 7 app.e0031982 app.adm   4096 Oct  4 16:46 ..
-rw-r----- 1 app.e0031982 app.adm   5213 Oct  4 14:25 ablation_run_conductor_serial.sh
-rw-r----- 1 app.e0031982 app.adm   1440 Oct  4 14:25 ablation_run_loop_1shot.sh
-rw-r----- 1 app.e0031982 app.adm   1605 Oct  4 14:25 ablation_run_loop_component_s2_full.sh
-rw-r----- 1 app.e0031982 app.adm   1449 Oct  4 14:25 ablation_run_loop_model_1shot.sh
-rw-r----- 1 app.e0031982 app.adm   2051 Oct  4 14:25 ablation_run_loop_model_full.sh
-rw-r----- 1 app.e0031982 app.adm   1467 Oct  4 14:25 ablation_run_loop_s1_1shot.sh
-rw-r----- 1 app.e0031982 app.adm   1461 Oct  4 14:25 ablation_run_loop_s1_full.sh
-rw-r----- 1 app.e0031982 app.adm   1443 Oct  4 14:25 ablation_run_loop_s2_1shot.sh
-rw-r----- 1 app.e0031982 app.adm   1397 Oct  4 14:25 ablation_run_loop.sh
-rw-r----- 1 app.e0031982 app.adm   6070 Oct  4 14:25 ablation_run_task_1shot.md
-rw-r----- 1 app.e0031982 app.adm  10921 Oct  4 14:45 ablation_run_task_component_s2_full.md
-rw-r----- 1 app.e0031982 app.adm   5938 Oct  4 14:25 ablation_run_task.md
-rw-r----- 1 app.e0031982 app.adm   6465 Oct  4 14:25 ablation_run_task_model_1shot.md
-rw-r----- 1 app.e0031982 app.adm   6349 Oct  4 14:25 ablation_run_task_model_full.md
-rw-r----- 1 app.e0031982 app.adm   7127 Oct  4 14:25 ablation_run_task_s1_1shot.md
-rw-r----- 1 app.e0031982 app.adm   7014 Oct  4 14:25 ablation_run_task_s1_full.md
-rw-r----- 1 app.e0031982 app.adm  11646 Oct  4 14:25 ablation_run_task_s2_1shot.md
-rw-r----- 1 app.e0031982 app.adm  11609 Oct  4 14:25 ablation_s2_phi_1shot_report.html
-rw-r----- 1 app.e0031982 app.adm   4181 Oct  4 16:46 AGENTS.md
-rw-r----- 1 app.e0031982 app.adm   6802 Oct  4 14:25 benchmark_parallel_guide.md
drwxr-x--- 2 app.e0031982 app.adm   4096 Oct  4 14:45 daily-memories
-rw-r----- 1 app.e0031982 app.adm  15491 Oct  4 14:25 eda_fastmcp_commit_prep_report.html

=========== 7. CPU / MEM / GPU ===========
Model name:                           INTEL(R) XEON(R) PLATINUM 8562Y+
Socket(s):                            2
               total        used        free      shared  buff/cache   available
Mem:            1007         190         206           0         621         816

=========== DONE ===========
```

---

## RUN_ID 2 · 2026-10-04 16:57:07 · host=`hfeg0tedaap02` · exit=0

**命令**
```bash
# RUN_ID 2 — 只读诊断
_GIT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || echo '/nasdata/app.e0031982/code/super_intelligence_2035')"
RUN_DIR="$_GIT_ROOT/doc/ZhuLong_DAC2027/run"
GP="/nasdata/app.e0031982/code/eda_fastmcp"

echo "===== 0. TIME ====="; date '+%F %T'; hostname

echo; echo "===== 1. loop / relay 进程（含 ppid）====="
ps -eo pid=,ppid=,etimes=,args= | grep -E 'zhulong_loop|zhulong_ops_relay' | grep -v grep | cut -c1-160

echo; echo "===== 2. loop 脚本实际 cline 调用行 ====="
grep -nE 'cline |CLINE_KEY=|MODEL=' "$RUN_DIR/zhulong_loop.sh" 2>/dev/null | cut -c1-160

echo; echo "===== 3. MEMORY_ZHULONG 顶部 WAITING ====="
grep -nE '^WAITING:' "$RUN_DIR/MEMORY_ZHULONG.md" 2>/dev/null | head -3

echo; echo "===== 4. /home 大头（有界 du）====="
df -BG /home | tail -1
timeout 45 du -x -d1 -h /home 2>/dev/null | sort -h | tail -15

echo; echo "===== 5. run_code 入口在哪 ====="
echo "-- eda_fastmcp 根 --"; ls -1 "$GP" 2>/dev/null | head -20
echo "-- scripts/ --"; ls -1 "$GP/scripts" 2>/dev/null | head -25
echo "-- grep run_code 定义文件 --"
timeout 30 grep -rln 'def run_code\|run_code(' "$GP" --include=*.py 2>/dev/null | head -8

echo; echo "===== 6. 端口口径（.env vs ss 监听）====="
grep -nE 'PROXY_PORTS|SANDBOX_PORT|EDA_MCP_PORT' "$GP/.env" 2>/dev/null | cut -c1-120
echo "-- ss tlnp 相关端口 --"
ss -tlnp 2>/dev/null | grep -oE ':(8650|8651|8652|8653|8654|8655|8664|8665|8668|8669|18890|9006)\b' | sort -u | tr '\n' ' '; echo

echo; echo "===== 7. loop 日志体检 ====="
echo -n "unknown option 次数: "; grep -c 'unknown option' /tmp/zhulong_loop.log 2>/dev/null || echo 0
echo -n "Forbidden 次数: "; grep -c 'Forbidden' /tmp/zhulong_loop.log 2>/dev/null || echo 0
tail -n 4 /tmp/zhulong_loop.log 2>/dev/null | cut -c1-140

echo; echo "===== DONE ====="
```

**输出**
```
===== 0. TIME =====
2026-10-04 16:57:07
hfeg0tedaap02

===== 1. loop / relay 进程（含 ppid）=====
1069304       1    5848 bash /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/zhulong_loop.sh
1069705  953319    5839 tail -f /tmp/zhulong_loop.log
1071337       1    5802 bash zhulong_ops_relay.sh
1071692  981989    5793 tail -f /tmp/zhulong_ops_relay.log
1245242 1071337       0 bash zhulong_ops_relay.sh

===== 2. loop 脚本实际 cline 调用行 =====
3:# 让 cline 读任务书连续推进，并每约 PUSH_INTERVAL 秒兜底做一次 git 同步 + commit + push。
32:#   本 loop 的 `-m "$MODEL"` 只负责读 MEMORY / pgrep / 打分 / 切臂 / cline auth。
33:#   被评测的求解 agent 由任务书内 `cline auth -m <MODEL_ID>` 切换（见 ablation_run_task_model_full.md），
35:MODEL="glm-5.2"
38:CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
40:CLINE_TIMEOUT=2700              # 单次编排 cline 最多 45 分钟（读态+打分+切臂+启动，足够）
105:    echo "[loop] $(date '+%F %T') wake up, invoking cline ..."
112:          cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
113:        echo "[loop] $(date '+%F %T') cline returned (exit $?), checking git sync ..."

===== 3. MEMORY_ZHULONG 顶部 WAITING =====
3:WAITING: 0

===== 4. /home 大头（有界 du）=====
/dev/mapper/vgroot-lv_home      394G  371G        6G  99% /home
7.2G	/home/app.e0019946
7.3G	/home/app.t0002987
8.4G	/home/app.e0014566
8.6G	/home/app.e0017912
9.1G	/home/app.e0042624
9.1G	/home/app.t0002965
14G	/home/app.e0026456
15G	/home/app.e0044587
16G	/home/app.e0030544
16G	/home/app.e0041392
16G	/home/app.t0002147
24G	/home/app.vendor.ai.ruide01
41G	/home/app.e0025768
71G	/home/app.e0023936
299G	/home

===== 5. run_code 入口在哪 =====
-- eda_fastmcp 根 --
CLAUDE.md
cleanup_tmp_gt.sh
daily-memories
Dockerfile
docs
kb
logs
main.py
memory_bank
MEMORY.md
monday_eval.log
prompts
pyAether-eval
__pycache__
pyproject.toml
README.md
requirements.txt
Rules
run_monday_eval.sh
run_monday.sh
-- scripts/ --
clean_sandbox.sh
cline_hooks
common.sh
dev
merge_retry_results.sh
__pycache__
README.md
reset_memory_bank.sh
run_cline_script.sh
run_cline_script_skill.sh
run_cline_script_tcl.sh
run_cli.sh
run_eval.py
run_pipeline.sh
sediment
set_ablation.py
set_s1_fidelity.py
set_s2_phi.py
start_recall_api.sh
start_recall_local.sh
start.sh
stop_recall_api.sh
stop_recall_local.sh
stop.sh
trace_phi_meta.py
-- grep run_code 定义文件 --
/nasdata/app.e0031982/code/eda_fastmcp/main.py
/nasdata/app.e0031982/code/eda_fastmcp/server/sandbox_server/exec_code.py
/nasdata/app.e0031982/code/eda_fastmcp/tools/run_code.py

===== 6. 端口口径（.env vs ss 监听）=====
30:# EDA_MCP_PORT=19999 
31:EDA_MCP_PORT=${EDA_MCP_PORT:=18890}
58:# PROXY_PORTS=8664,8665,8653,8669
59:PROXY_PORTS=8650,8651,8652,8654
62:SANDBOX_PORT_HTTP=8655
65:SANDBOX_PORT_TCP=8668
81:# 空/不设 → 回退单端口(SANDBOX_HOST:SANDBOX_PORT_HTTP / SANDBOX_WORKDIR, 行同旧版)
-- ss tlnp 相关端口 --
:18890 :8652 :8653 :8655 :8664 :8665 :8668 :8669 :9006 

===== 7. loop 日志体检 =====
unknown option 次数: 69
Forbidden 次数: 0
0
[loop] 2026-10-04 16:57:22 wake up, invoking cline ...
[31merror:[0m error: unknown option '-b'
[loop] 2026-10-04 16:57:22 cline returned (exit 0), checking git sync ...
[loop] 2026-10-04 16:57:22 WAITING=0 (no blocker) → sleep 60s

===== DONE =====
```

---

## RUN_ID 3 · 2026-10-04 17:01:50 · host=`hfeg0tedaap02` · exit=0

**命令**
```bash
# RUN_ID 3 — 只读盘点（不删除）
H="/home/app.e0031982"
echo "===== 0. TIME ====="; date '+%F %T'; hostname
echo "===== 1. /home 大盘 ====="; df -BG /home | tail -1

echo; echo "===== 2. $H 一级（体积，有界 du）====="
timeout 60 du -x -d1 -h "$H" 2>/dev/null | sort -h | tail -25

echo; echo "===== 3. 常见缓存/会话目录体积 ====="
for d in .cache .cline .bun .npm .local .npm-global .vscode-server .triton .config .nv .conda; do
  [ -e "$H/$d" ] && timeout 25 du -x -sh "$H/$d" 2>/dev/null
done

echo; echo "===== 4. .cache 下二级 ====="
[ -d "$H/.cache" ] && timeout 40 du -x -d1 -h "$H/.cache" 2>/dev/null | sort -h | tail -15

echo; echo "===== 5. eda_code_eval 评测产物 ====="
if [ -d "$H/eda_code_eval" ]; then
  echo -n "   批次数: "; ls -1 "$H/eda_code_eval" 2>/dev/null | wc -l
  echo -n "   总大小: "; timeout 45 du -x -sh "$H/eda_code_eval" 2>/dev/null | cut -f1
  echo "   -- 最新 8 个批次 --"; ls -1t "$H/eda_code_eval" 2>/dev/null | head -8
  echo "   -- 最旧 8 个批次 --"; ls -1t "$H/eda_code_eval" 2>/dev/null | tail -8
  echo "   -- 按批次大小 top10 --"; timeout 40 du -x -d1 -h "$H/eda_code_eval" 2>/dev/null | sort -h | tail -10
else
  echo "   (无 $H/eda_code_eval)"
fi

echo; echo "===== 6. 其它可能产物区 + HOME 一级清单 ====="
for d in eda_platform zhulong runs experiments .ena_feature_cache .hf_cache hf_cache; do
  [ -e "$H/$d" ] && echo "   存在: $d ($(timeout 20 du -x -sh "$H/$d" 2>/dev/null | cut -f1))"
done
echo "   -- ls -1 $H --"; ls -1 "$H" 2>/dev/null | head -40

echo; echo "===== 7. 大文件 top15（>100M）====="
timeout 60 find "$H" -xdev -type f -size +100M -printf '%s\t%p\n' 2>/dev/null | sort -nr | head -15 | awk '{printf "   %.2fG\t%s\n", $1/1073741824, $2}'

echo; echo "===== DONE ====="
```

**输出**
```
===== 0. TIME =====
2026-10-04 17:01:50
hfeg0tedaap02
===== 1. /home 大盘 =====
/dev/mapper/vgroot-lv_home      394G  371G        6G  99% /home

===== 2. /home/app.e0031982 一级（体积，有界 du）=====
4.0K	/home/app.e0031982/logs
8.0K	/home/app.e0031982/.pip
12K	/home/app.e0031982/Cline
16K	/home/app.e0031982/.copilot
24K	/home/app.e0031982/mcp_tmp
24K	/home/app.e0031982/.ssh
32K	/home/app.e0031982/.config
68K	/home/app.e0031982/.eda_mcp
3.6M	/home/app.e0031982/.nvm
3.8M	/home/app.e0031982

===== 3. 常见缓存/会话目录体积 =====
0	/home/app.e0031982/.cache
0	/home/app.e0031982/.cline
0	/home/app.e0031982/.npm
0	/home/app.e0031982/.local
0	/home/app.e0031982/.vscode-server
32K	/home/app.e0031982/.config

===== 4. .cache 下二级 =====
0	/home/app.e0031982/.cache

===== 5. eda_code_eval 评测产物 =====
   批次数: 87
   总大小: 0
   -- 最新 8 个批次 --
2026_1004_122050
completed_code_generation_2026_1004_122050.jsonl
code_generation_2026_1004_122050.jsonl
2026_1004_111533
completed_code_generation_2026_1004_111533.jsonl
code_generation_2026_1004_111533.jsonl
2026_1004_090528
completed_code_generation_2026_1004_090528.jsonl
   -- 最旧 8 个批次 --
completed_code_generation_2026_0930_090126.jsonl
code_generation_2026_0930_090126.jsonl
2026_0929_214931
completed_code_generation_2026_0929_214931.jsonl
code_generation_2026_0929_214931.jsonl
2026_0929_181818
completed_code_generation_2026_0929_181818.jsonl
code_generation_2026_0929_181818.jsonl
   -- 按批次大小 top10 --
0	/home/app.e0031982/eda_code_eval

===== 6. 其它可能产物区 + HOME 一级清单 =====
   -- ls -1 /home/app.e0031982 --
Cline
eda_code_eval
logs
mcp_tmp
n#

===== 7. 大文件 top15（>100M）=====

===== DONE =====
```

---

## RUN_ID 4 · 2026-10-04 17:05:57 · host=`hfeg0tedaap02` · exit=0

**命令**
```bash
# RUN_ID 4 — 只读
H="/home/app.e0031982"; GP="/nasdata/app.e0031982/code/eda_fastmcp"
echo "===== 0. TIME ====="; date '+%F %T'; hostname
echo "===== 1. /home 大盘 ====="; df -BG /home | tail -1

echo; echo "===== 2. HOME 一级（ls -la，看 symlink '->'）====="
ls -la "$H" 2>/dev/null | cut -c1-170

echo; echo "===== 3. 关键目录 realpath + 所在文件系统 ====="
for d in .cache .cline .npm .local .bun .vscode-server .config eda_code_eval; do
  p="$H/$d"
  if [ -e "$p" ] || [ -L "$p" ]; then
    printf "%-16s -> %-52s fs:%s\n" "$d" "$(readlink -f "$p" 2>/dev/null)" "$(df -h "$p" 2>/dev/null | tail -1 | awk '{print $1}')"
  fi
done

echo; echo "===== 4. HOME 真实体积（follow symlinks，有界）====="
timeout 90 du -sh -L "$H" 2>/dev/null
echo -n "   eda_code_eval 真实体积: "; timeout 60 du -sh -L "$H/eda_code_eval" 2>/dev/null | cut -f1

echo; echo "===== 5. /home 各用户 top20（有界）====="
timeout 60 du -x -d1 -h /home 2>/dev/null | sort -h | tail -20

echo; echo "===== 6. 评测输出目录在脚本里怎么设的 ====="
grep -rnE 'eda_code_eval|OUTPUT_DIR|EVAL_OUT|HOME|/home/app' "$GP/scripts/run_cline_script.sh" "$GP/scripts/common.sh" 2>/dev/null | cut -c1-160 | head -20

echo; echo "===== 7. 我方 home 内大文件（follow，>100M，限深度 4）====="
timeout 60 find "$H/" -maxdepth 4 -type f -size +100M -printf '%s\t%p\n' 2>/dev/null | sort -nr | head -15 | awk '{printf "   %.2fG\t%s\n", $1/1073741824, $2}'

echo; echo "===== DONE ====="
```

**输出**
```
===== 0. TIME =====
2026-10-04 17:05:57
hfeg0tedaap02
===== 1. /home 大盘 =====
/dev/mapper/vgroot-lv_home      394G  371G        6G  99% /home

===== 2. HOME 一级（ls -la，看 symlink '->'）=====
total 76
drwxr-x--- 11 app.e0031982 app.adm 4096 Oct  4 14:25 .
drwxr-xr-x 67 root         root    4096 Sep 22 16:50 ..
-rw-r-----  1 app.e0031982 app.adm  527 Oct  4 15:15 .bash_history
-rw-r--r--  1 app.e0031982 app.adm  220 Mar 31  2024 .bash_logout
-rw-r--r--  1 app.e0031982 app.adm 4499 Oct  4 14:25 .bashrc
lrwxrwxrwx  1 app.e0031982 app.adm   28 Sep 30 08:47 .cache -> /nasdata/app.e0031982/.cache
lrwxrwxrwx  1 app.e0031982 app.adm   28 Sep 30 08:48 .cline -> /nasdata/app.e0031982/.cline
drwxr-xr-x  4 app.e0031982 app.adm 4096 Sep 29 16:16 Cline
-rw-r-----  1 app.e0031982 app.adm  166 Aug 11 09:53 .condarc
drwx------  5 app.e0031982 app.adm 4096 Sep 29 13:36 .config
drwx------  3 app.e0031982 app.adm 4096 Sep 29 13:38 .copilot
lrwxrwxrwx  1 app.e0031982 app.adm   35 Sep 30 08:48 eda_code_eval -> /nasdata/app.e0031982/eda_code_eval
drwxr-x---  3 app.e0031982 app.adm 4096 Sep 15 15:13 .eda_mcp
-rw-r-----  1 app.e0031982 app.adm   51 Sep  4 14:17 .gitconfig
-rw-------  1 app.e0031982 app.adm   20 Sep 29 11:08 .lesshst
lrwxrwxrwx  1 app.e0031982 app.adm   28 Sep 30 08:53 .local -> /nasdata/app.e0031982/.local
drwxr-x---  2 app.e0031982 app.adm 4096 Sep 23 23:04 logs
drwxr-x---  2 app.e0031982 app.adm 4096 Sep 22 07:24 mcp_tmp
-rw-r-----  1 app.e0031982 app.adm    0 Aug  4 15:16 n#
lrwxrwxrwx  1 app.e0031982 app.adm   26 Sep 30 08:52 .npm -> /nasdata/app.e0031982/.npm
drwxr-x---  6 app.e0031982 app.adm 4096 Jul 28 17:37 .nvm
drwxr-x---  2 app.e0031982 app.adm 4096 Aug  7 08:49 .pip
-rw-r--r--  1 app.e0031982 app.adm  807 Mar 31  2024 .profile
drwx------  2 app.e0031982 app.adm 4096 Oct  4 13:53 .ssh
lrwxrwxrwx  1 app.e0031982 app.adm   36 Sep 30 08:53 .vscode-server -> /nasdata/app.e0031982/.vscode-server

===== 3. 关键目录 realpath + 所在文件系统 =====
.cache           -> /nasdata/app.e0031982/.cache                         fs:10.251.9.180:/g0tedaap
.cline           -> /nasdata/app.e0031982/.cline                         fs:10.251.9.180:/g0tedaap
.npm             -> /nasdata/app.e0031982/.npm                           fs:10.251.9.180:/g0tedaap
.local           -> /nasdata/app.e0031982/.local                         fs:10.251.9.180:/g0tedaap
.vscode-server   -> /nasdata/app.e0031982/.vscode-server                 fs:10.251.9.180:/g0tedaap
.config          -> /home/app.e0031982/.config                           fs:/dev/mapper/vgroot-lv_home
eda_code_eval    -> /nasdata/app.e0031982/eda_code_eval                  fs:10.251.9.180:/g0tedaap

===== 4. HOME 真实体积（follow symlinks，有界）=====
   eda_code_eval 真实体积: 5.7G

===== 5. /home 各用户 top20（有界）=====
4.3G	/home/app.e0030884
4.5G	/home/app.vendor.aix.huib01
5.1G	/home/app.t0002596
5.2G	/home/app.e0027465
6.1G	/home/app.e0040224
7.2G	/home/app.e0019946
7.3G	/home/app.t0002987
8.4G	/home/app.e0014566
8.6G	/home/app.e0017912
9.1G	/home/app.e0042624
9.1G	/home/app.t0002965
14G	/home/app.e0026456
15G	/home/app.e0044587
16G	/home/app.e0030544
16G	/home/app.e0041392
16G	/home/app.t0002147
24G	/home/app.vendor.ai.ruide01
41G	/home/app.e0025768
71G	/home/app.e0023936
299G	/home

===== 6. 评测输出目录在脚本里怎么设的 =====
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:40:readonly EVAL_ROOT_DIR="$HOME/eda_code_eval"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:51:# 任务输入目录（由 Step 2 写入 ~/eda_code_eval/<batch_id>/full_tasks/；--tasks 
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:173:        BENCHMARK_FILE="${HOME}${BENCHMARK_FILE:1}"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:193:    local memory_base="${HOME}/Cline/Memory"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:308:    CLI_OUTPUT_DIR="${EVAL_ROOT_DIR}/${BATCH_ID}/code"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:310:    if [[ ! -d "$CLI_OUTPUT_DIR" ]]; then
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:311:        print_error "输出目录不存在: $CLI_OUTPUT_DIR"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:315:    export CLI_OUTPUT_DIR
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:328:    run_python_script "$FORMAT_OUTPUT_SCRIPT" "--input_dir=$CLI_OUTPUT_DIR" "--output_fil
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:418:        trace_src="$HOME/.cline/data/tasks"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:499:        local sessions_dir="$HOME/.cline/data/sessions"
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:633:    run_python_script "scripts/sediment/evaluate_skills.py" "--skills-dir=$HOME/.cline/sk
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:644:    run_python_script "scripts/sediment/evaluate_skills.py" "--skills-dir=$HOME/.cline/sk
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:751:    if [[ -d "${HOME}/Cline/Memory/L0_raw/task_artifacts" ]] && \
/nasdata/app.e0031982/code/eda_fastmcp/scripts/run_cline_script.sh:752:       [[ -n "$(ls -A "${HOME}/Cline/Memory/L0_raw/task_artifacts/" 2>/dev/null)" ]]; the
/nasdata/app.e0031982/code/eda_fastmcp/scripts/common.sh:86:    # local py="${PYTHON:-/home/app.t0002596/miniforge3/envs/py310_env/bin/python}"

===== 7. 我方 home 内大文件（follow，>100M，限深度 4）=====

===== DONE =====
```
