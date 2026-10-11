# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 34 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`zhulong_ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> 危险模式会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **两条纪律**（跟随 BaiZe ops 的教训）：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② **绝不整树 `du`** —— `/nasdata` / `/nas_train` 有 175+ TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`（每条带 `timeout`）**。
>
> ## 🚨🚨 **中继的真实行为（从 BaiZe ops_relay.sh 继承的规则）**
> `zhulong_ops_relay.sh` 的 `inbox_cmd_block()` 是：
> ```bash
> awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"
> ```
> **→ 它只执行文件里<u>第一个</u> ```bash 块**，后面的块**永远不会被执行**。
>
> ### ✅ 下发新命令的铁律
> 1. **把要执行的块放在文件的<u>最前面</u>**（任何标题之前的位置无所谓，关键是**第一个 ```bash**）。
> 2. **把旧块降级为 ```text**（或删掉）—— 否则它一直霸占"第一个块"。
> 3. **每次 `RUN_ID` 都要 +1**（中继靠"变大"触发）。

---

## RUN_ID 34 — 🚀 起跑 r2：确认/启动 MCP(eda_fastmcp) + 确认/重启 RAG recall `:9006` + 4 端口复检 → **用户授权带 4G 起跑**

> **用户令（2026-10-11）**：「**授权带 4G 起跑**。先要启动 MCP，在 `eda_fastmcp` 下边 `bash scripts/start.sh`；**rag recall 服务在本机(36.15)的 9006 端口（如果未监听也需重启 `bash scripts/start_recalling_api.sh`）**。」
> **已知事实（RUN_ID 33 查明）**：36.15 的 MCP **实际监听 `:18890`**（启动横幅「监听地址: 0.0.0.0:18890」），**已在运行**（3 个 `python main.py`）⇒ `start.sh` 的 `exit=1` 只是因为日志报 **「端口 18890 已被占用」**（**不是故障**）。`:8090` 是 `~/.cline/data/settings/` 里的旧口径，与 eval 侧（`CLI_DATA_DIR=/nasdata/…/.cline_prof4_eval/data`）无关。
> **本块**：① `df` 记录（用户已授权放宽 `/home` 门槛）→ ② MCP：现状 + 按用户令**照跑一次 `start.sh`** 并解读（占用=已在跑）+ `:18890` HTTP 探活 → ③ RAG：`:9006` 若在监听则只探活；**未监听才** `bash scripts/start_recalling_api.sh` → ④ 4 端口复检（TCP + `run_code` 实跑）→ ⑤ **仅当 EVAL_ALIVE=0 且 4/4 健康**才起 C1.full r2（四 override + `log=/tmp/ABL_full_r2_8650set.log`）+ 核验（新 PID / 四 override / **hook 是否重新部署** / log 头尾）→ ⑥ 快照。**`/home` 门槛经用户授权放宽，其余硬闸不变。**

```bash
# ═══ RUN_ID 34 — ZhuLong：MCP 启动确认 + RAG :9006 + 4 端口复检 → 带 4G 起跑 C1.full r2 ═══
echo "== RUN_ID 34 @ $(date '+%F %T') host=$(hostname) =="
EDA=/nasdata/app.e0031982/code/eda_fastmcp
W=/nasdata/app.e0031982/code/super_intelligence_2035
LOG=/tmp/ABL_full_r2_8650set.log
PORTS="8650 8651 8652 8654"
SHOST=10.129.32.75
TS=$(date '+%Y%m%d_%H%M%S')

echo
echo "=========== 0. 磁盘（用户已授权带 4G 起跑，仅记录）==========="
timeout 20 df -BG /home /nasdata /tmp 2>/dev/null | cut -c1-120

echo
echo "=========== 1. MCP(eda_fastmcp)：现状 + 按用户令跑 start.sh + :18890 探活 ==========="
timeout 20 ss -lntp 2>/dev/null | grep -E ':(8090|18890)' | cut -c1-150 || echo "   ⚠️ :8090/:18890 均未监听"
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v cline | cut -c1-130 | head -4
echo "   :18890 http_code=$(timeout 15 curl -s -m 8 -o /dev/null -w '%{http_code}' http://localhost:18890/ 2>/dev/null) （非 000 = HTTP 层在）"
echo "-- 按用户令执行 bash scripts/start.sh（幂等；报『端口 18890 已被占用』= 服务已在跑，属正常）--"
( cd "$EDA" && timeout 120 bash scripts/start.sh ) > "/tmp/eda_start_runid34.log" 2>&1; echo "   start.sh exit=$?"
timeout 20 tail -12 "/tmp/eda_start_runid34.log" 2>/dev/null | cut -c1-180
sleep 3
echo "-- AFTER --"
timeout 20 ss -lntp 2>/dev/null | grep -E ':(8090|18890)' | cut -c1-150 || echo "   ⚠️ 仍未监听"
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v cline | cut -c1-130 | head -4

echo
echo "=========== 2. RAG recall :9006（在监听则只探活；未监听才按用户令重启）==========="
if timeout 20 ss -lntp 2>/dev/null | grep -q ':9006'; then
  echo "   ✅ :9006 已在监听（无需重启）"
  timeout 20 ss -lntp 2>/dev/null | grep ':9006' | cut -c1-150
else
  echo "   ⚠️ :9006 未监听 ⇒ 执行 bash scripts/start_recalling_api.sh"
  echo "   脚本: $(timeout 20 ls -l "$EDA/scripts/start_recalling_api.sh" 2>&1 | cut -c1-140)"
  ( cd "$EDA" && setsid bash scripts/start_recalling_api.sh > "/tmp/rag_recall_$TS.log" 2>&1 < /dev/null & )
  sleep 10
  timeout 20 ss -lntp 2>/dev/null | grep ':9006' | cut -c1-150 || echo "   ⚠️ 起来后仍未监听"
  timeout 20 tail -12 "/tmp/rag_recall_$TS.log" 2>/dev/null | cut -c1-180
fi
echo "   recall 探活 http_code=$(timeout 20 curl -s -m 10 -o /dev/null -w '%{http_code}' http://localhost:9006/recall 2>/dev/null) （400/403/404/405 = 服务在；000 = 不通）"

echo
echo "=========== 3. 4 sandbox 端口复检（TCP + run_code 实跑）==========="
OK=0
for p in $PORTS; do
  if timeout 5 bash -c "echo > /dev/tcp/$SHOST/$p" 2>/dev/null; then tcp=OK; else tcp=CLOSED; fi
  body=$(timeout 40 curl -s -m 30 -X POST "http://$SHOST:$p/v1/run_code" -H 'Content-Type: application/json' -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null)
  n=${#body}
  if [ "$n" -gt 0 ]; then rc=OK; OK=$((OK+1)); else rc="FAIL(0byte)"; fi
  echo "   port $p : TCP=$tcp run_code=$rc resp_len=$n | $(printf '%s' "$body" | cut -c1-80)"
done
echo "   ▶ 健康端口 = $OK / 4"
EVAL_ALIVE=$(timeout 20 pgrep -f '^bash scripts/run_cline_script' 2>/dev/null | wc -l)
echo "   eval 在跑？ EVAL_ALIVE=$EVAL_ALIVE"

echo
echo "=========== 4. 起动 C1.full r2（硬闸：EVAL_ALIVE=0 且 4/4；/home 门槛经用户授权放宽）==========="
if [ "$EVAL_ALIVE" -eq 0 ] && [ "$OK" -eq 4 ]; then
  ( cd "$EDA"
    export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
    export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data
    export PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python
    export https_proxy=http://172.19.92.23:13128
    setsid bash scripts/run_cline_script.sh -p 8 -n > "$LOG" 2>&1 < /dev/null &
  )
  echo "   已下发 setsid 起动，等 20s 核验 ..."
  sleep 20
  NEW=$(timeout 20 pgrep -f '^bash scripts/run_cline_script' 2>/dev/null | head -1)
  echo "   新 eval PID=${NEW:-<none>}"
  if [ -n "$NEW" ]; then
    echo "   -- 四 override（/proc/$NEW/environ）--"
    timeout 20 tr '\0' '\n' < /proc/$NEW/environ 2>/dev/null | grep -E '^(EVAL_FW_DIR|CLI_DATA_DIR|PYTHON|https_proxy)=' | cut -c1-170
    echo "   -- 反作弊 hook 是否被本轮重新部署（删完必检）--"
    timeout 20 ls -l ~/.cline/hooks/PreToolUse 2>&1 | cut -c1-140
    timeout 20 ls -l /nasdata/app.e0031982/.cline_prof4_eval/data/hooks/ 2>&1 | cut -c1-140
  fi
  echo "   -- log 头 45 行 --"; timeout 20 head -45 "$LOG" 2>/dev/null | cut -c1-180
  echo "   -- log 尾 10 行 --"; timeout 20 tail -10 "$LOG" 2>/dev/null | cut -c1-180
else
  echo "   ⛔ 未起动（EVAL_ALIVE=$EVAL_ALIVE，健康端口=$OK/4）"
fi

echo
echo "=========== 5. 快照 ==========="
timeout 20 df -BG /home 2>/dev/null | cut -c1-120
timeout 20 grep -nE '^(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' "$EDA/.env" 2>/dev/null | cut -c1-260
echo "   last_run_id=$(cat "$W/doc/ZhuLong_DAC2027/run/ops/.last_run_id" 2>/dev/null)"
echo
echo "== DONE — RUN_ID 34（MCP 确认 + RAG 9006 + 4 端口复检 + 起 r2）=="
```

---

## RUN_ID 33 — 🩺 跟进：诊断 `eda_fastmcp` 启动失败 + sandbox 4 端口「TCP 通但 `run_code` 0 字节」+ **重启已死的 loop**

> **为什么发这一块（RUN_ID 32 的结果）**：32 已于 **2026-10-11 08:07:38 执行（host=`hfeg0tedaap02`，exit=0）**，做到：停评测（`残留=0`）/ 删 hook（本就已不存在）/ `.env` 备份 + `stash` 回退 / 写回 `PROXY_PORTS=8650,8651,8652,8654` + `RAG_RECALL_URL=9006` / **`timeout:180` 精确回退 1 处**（`~/.cline/data/settings/...`，`removed=1`、JSON OK；`~/.cline_prof4_eval/` 目录**已不存在**）/ 实测 4 端口。**但环境仍不健康**：
> - `bash scripts/start.sh` **exit=1** ⇒ MCP `:8090` 未起；
> - 4 端口 **TCP=OK 但 `run_code` 全部 0 字节** ⇒ **健康端口 0/4** ⇒ **硬闸生效，未启动 r2**（符合 (八)⑤ 纪律）；
> - 另发现 `loop pid=<none>` ⇒ **zhulong loop 也死了**（agent 自 07:13 未再唤醒）；
> - `/home` **100%（4G 可用）**。
> **本块**：① 读上次 `start.sh` 日志找真因 → ② 幂等重试启动 + 复核 `:8090` → ③ sandbox 主机与 4 端口：`ping` + TCP + **长超时（60s）单口实跑** + HTTP 探活 → ④ **用正确 PATH+proxy 重启 loop**（配方同 BaiZe RUN_ID 85）→ ⑤ 快照。**不带病开跑 r2。**

```text
# ═══ RUN_ID 33 — ZhuLong：诊断 MCP 启动失败 + sandbox 4 端口 0 字节 + 重启已死的 loop ═══
echo "== RUN_ID 33 @ $(date '+%F %T') host=$(hostname) =="
EDA=/nasdata/app.e0031982/code/eda_fastmcp
W=/nasdata/app.e0031982/code/super_intelligence_2035
CDIR=/home/app.e0031982/.local/node-20/bin
PX=http://172.19.92.23:13128
SHOST=10.129.32.75
PORTS="8650 8651 8652 8654"
TS=$(date '+%Y%m%d_%H%M%S')

echo
echo "=========== 1. MCP(:8090) 现状 + 上次 start.sh 失败真因（只读）==========="
timeout 20 ss -lntp 2>/dev/null | grep -E ':8090' | cut -c1-150 || echo "   :8090 未监听"
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v cline | cut -c1-130 | head -3 || echo "   (无 python main.py 进程)"
echo "-- RUN_ID 32 那次 /tmp/eda_start_runid32.log 尾部 25 行 --"
timeout 20 tail -25 /tmp/eda_start_runid32.log 2>/dev/null | cut -c1-190

echo
echo "=========== 2. 幂等重试启动 MCP ==========="
( cd "$EDA" && timeout 180 bash scripts/start.sh ) > "/tmp/eda_start_runid33.log" 2>&1; echo "   start.sh exit=$?"
sleep 6
echo "-- 新日志尾 20 行 --"
timeout 20 tail -20 "/tmp/eda_start_runid33.log" 2>/dev/null | cut -c1-190
echo "-- AFTER --"
timeout 20 ss -lntp 2>/dev/null | grep -E ':8090' | cut -c1-150 || echo "   ⚠️ :8090 仍未监听"
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v cline | cut -c1-130 | head -3

echo
echo "=========== 3. sandbox 主机 $SHOST / 4 端口（TCP + HTTP 探活 + 长超时 run_code）==========="
timeout 10 ping -c 2 -W 2 "$SHOST" 2>&1 | tail -2 | cut -c1-140
for p in $PORTS; do
  if timeout 5 bash -c "echo > /dev/tcp/$SHOST/$p" 2>/dev/null; then tcp=OK; else tcp=CLOSED; fi
  code=$(timeout 20 curl -s -m 12 -o /dev/null -w '%{http_code}' "http://$SHOST:$p/" 2>/dev/null)
  echo "   port $p : TCP=$tcp  http_get=$code"
done
echo "-- 8650 单口长超时（curl -m 60）run_code 实跑（判定「慢」还是「死」）--"
body=$(timeout 80 curl -s -m 60 -X POST "http://$SHOST:8650/v1/run_code" -H 'Content-Type: application/json' -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null)
echo "   resp_len=${#body} | $(printf '%s' "$body" | cut -c1-170)"

echo
echo "=========== 4. 重启已死的 loop（正确 PATH(含 cline) + proxy；幂等，不动 relay）==========="
timeout 20 pgrep -af 'zhulong_loop[.]sh' 2>/dev/null | grep -v pgrep | cut -c1-130 || echo "   (重启前 loop 不在跑)"
export PATH="$CDIR:$HOME/.bun/bin:$PATH"; export https_proxy="$PX"; export http_proxy="$PX"
command -v cline >/dev/null 2>&1 && echo "   cline OK -> $(command -v cline)" || echo "   ⚠️ cline 不在 PATH（loop 会空转，需人工处理）"
timeout 30 cp -f /tmp/zhulong_loop.log "/tmp/zhulong_loop.log.bak.$TS" 2>/dev/null
timeout 20 pkill -f 'zhulong_loop[.]sh' 2>/dev/null; sleep 2
setsid bash "$W/doc/ZhuLong_DAC2027/run/zhulong_loop.sh" > /tmp/zhulong_loop.log 2>&1 < /dev/null &
sleep 8
timeout 20 pgrep -af 'zhulong_loop[.]sh' 2>/dev/null | grep -v pgrep | cut -c1-130 || echo "   ⚠️ loop 未起来"
echo "-- 新 loop 日志头 6 行（应见 wake up, invoking cline，且无 No such file）--"
timeout 20 head -6 /tmp/zhulong_loop.log 2>/dev/null | cut -c1-180

echo
echo "=========== 5. 快照 ==========="
timeout 20 df -BG /home /nasdata /tmp 2>/dev/null | cut -c1-120
echo "-- .env 关键行 --"
timeout 20 grep -nE '^(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' "$EDA/.env" 2>/dev/null | cut -c1-260
echo "-- 中继自身 --"
timeout 20 pgrep -af 'zhulong_ops_relay[.]sh' 2>/dev/null | grep -v pgrep | cut -c1-130
echo "   last_run_id=$(cat "$W/doc/ZhuLong_DAC2027/run/ops/.last_run_id" 2>/dev/null)"
echo "   hook: $(timeout 20 ls -l ~/.cline/hooks/PreToolUse 2>&1 | cut -c1-120)"

echo
echo "== DONE — RUN_ID 33（MCP 诊断/重试 + 4 端口长超时实测 + loop 重启）=="
```

---

## RUN_ID 32 — 🛑 停评测 + 删 hook + `.env` 回退(stash) + 换端口集 `8650/8651/8652/8654` + RAG→`9006` + 回退 `cline_mcp_settings.json` 的 `timeout:180` + 实测 + 重启 `eda_fastmcp` + 起动 C1.full r2

**用户令（2026-10-11 上午）**：「用 ops relay 发布指令：**停掉当前评测**，**删除 `~/.cline/hooks/PreToolUse`**，把 **`eda_fastmcp/.env` 本地改动 stash**，**把昨晚做的改动回退**。**测试/应用端口 `8650`、`8651`、`8652`、`8654`**，修改 `.env`，**ragrecall 端口重新设为 9006**，**重启 full r2-r5 及后续评测**。」

**用户追加令（2026-10-11，二段）**：「**昨晚的改动都是垃圾，全部回退。没有任何亮点。**」⇒ 本块**连同 `(八)`③ 在 `cline_mcp_settings.json` 加的 `"timeout": 180` 一并回退**（`r2_new` 那轮 timeout 427→10 的记录**不作为保留理由**，用户已否决）；before/after 快照见 **3.6** 与 **⑧**。

**背景（为什么换回旧端口集）**：(八) 的 4 个新端口（`8663/8666/8667/8670`）在 **10-11 早间再次全部挂死**（0 字节 / 超时），`8670` 还进了 license 断路器（83 consecutive）→ r2_new（batch `2026_1010_234408`）code-gen 跑完 146/158/2 fail，但 **eval Steps 5–7.1 未跑 = 无 official Pass@1**。而 (六) 实测**旧 4 端口 `8650/8651/8652/8654` 全健康 3/3 @0.01s**；RAG recall 端口 `9012` 已死、`9006` 健康（`chroma_db_v20260522`）。⇒ **换回旧端口集 + 修 RAG 端口 + 重启 r2–r5**。

**本块动作（幂等；旧的第一块已降级为 text 围栏）**：
1. **停评测**（只杀评测侧进程：用 `/proc/PID/environ` 的 `EVAL_FW_DIR|CLI_DATA_DIR` 签名 + 锚定 `^bash scripts/run_cline_script`，**绝不误杀编排侧 cline**——任务书全文在它 cmdline 里）。
2. **删 `~/.cline/hooks/PreToolUse`**（先 `ls`/`stat`，后 `ls` 复核；⚠️ 每轮 eval 启动会自动重新部署，见 ⑦ 核验）。
3. **`.env` 备份 + `git stash push -- .env`**（= 回退昨晚端口改动；备份落 `/tmp/eda_fastmcp.env.bak.*`）。
4. **写新 `.env`**：`PROXY_PORTS=8650,8651,8652,8654` + `SANDBOX_ENDPOINTS`（**优先沿用 git HEAD 既有映射**，取不到才用 `t0002997_1..4` 兜底并标「待核」）+ `RAG_RECALL_URL=http://localhost:9006/recall`。
5. **重启 `eda_fastmcp`**（MCP `:8090`）并核验。
6. **4 端口双测**：TCP 连通 + `run_code` 实跑（非 curl 端口可达）。
7. **仅当「eval 未在跑」且「4/4 健康」**才起动 C1.full r2（四 override + `log=/tmp/ABL_full_r2_8650set.log`）；否则**不启、只报**（沿用 (八)⑤ 硬闸）。
8. **环境核验 + 披露**：loop / MCP / RAG `9006` / `df` / `cline_mcp_settings.json` 的 `timeout` **回退后**快照 + 备份清单。
9. **（用户 10-11 追加令）回退 `cline_mcp_settings.json` 的 `"timeout": 180`**：两处（`~/.cline/data/settings/`、`~/.cline_prof4_eval/data/settings/`）先备份 → python **精确删 `timeout==180` 键**（其他 timeout 值保留）→ JSON 合法性校验 → before/after 快照 + 旧备份参考 `/tmp/*cline_mcp_settings*`。

**边界**：✅ **`timeout:180` 本块回退**（用户 10-11：「昨晚的改动都是垃圾，全部回退，没有任何亮点」）；🚫 不动 RAG/Memory 服务本体；🚫 不 `git add -A`；🚫 不 `git pull/fetch`。

```text
# ═══ RUN_ID 32 — ZhuLong：停评测 + 删 hook + .env 回退(stash) + 端口集换 8650/8651/8652/8654 + RAG→9006 + 回退 cline_mcp_settings.json 的 timeout:180 + 实测 + (4/4 健康才) 重启 MCP + 起动 C1.full r2 ═══
echo "== RUN_ID 32 @ $(date '+%F %T') host=$(hostname) =="
EDA=/nasdata/app.e0031982/code/eda_fastmcp
ENVF=$EDA/.env
SHOST=10.129.32.75
TS=$(date '+%Y%m%d_%H%M%S')
LOG=/tmp/ABL_full_r2_8650set.log
PORTS="8650 8651 8652 8654"

# ── 评测侧进程判定：env 里有 EVAL_FW_DIR / CLI_DATA_DIR / SANDBOX_CONFIG_JSON 才算评测侧 ──
is_eval_proc() {
  n=$(tr '\0' '\n' < /proc/$1/environ 2>/dev/null | grep -cE '^(EVAL_FW_DIR|CLI_DATA_DIR|EVAL_SANDBOX_WORKERS|SANDBOX_CONFIG_JSON)=')
  [ "${n:-0}" -gt 0 ]
}
my_pg=$(ps -o pgid= -p $$ 2>/dev/null | tr -d ' ')

echo
echo "=========== 1. 停掉当前评测（幂等）==========="
echo "-- BEFORE：候选进程（含排除理由）--"
CAND=""
for p in $(timeout 20 pgrep -f 'run_cline_script|run_eval\.py|run_on_sandbox' 2>/dev/null); do
  case "$p" in "$$"|"$PPID") continue;; esac
  cl=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | cut -c1-110)
  case "$cl" in
    *zhulong_loop*|*ZHULONG_TASK*)
      echo "   SKIP(编排侧) pid=$p $cl"; continue;;
  esac
  if is_eval_proc "$p" || echo "$cl" | grep -q '^bash scripts/run_cline_script'; then
    CAND="$CAND $p"; echo "   KILL-TARGET pid=$p $cl"
  else
    echo "   SKIP(无评测侧签名) pid=$p $cl"
  fi
done
[ -z "$CAND" ] && echo "   （无候选 = 当前没有评测在跑）"
for round in TERM KILL; do
  for p in $CAND; do
    [ -d /proc/$p ] || continue
    pg=$(ps -o pgid= -p "$p" 2>/dev/null | tr -d ' ')
    if [ -n "$pg" ] && [ "$pg" != "1" ] && [ "$pg" != "$my_pg" ]; then
      timeout 30 kill -$round -"$pg" 2>/dev/null
    else
      timeout 30 kill -$round "$p" 2>/dev/null
    fi
  done
  [ "$round" = "TERM" ] && sleep 8
done
sleep 3
LEFT=0
for p in $(timeout 20 pgrep -f 'run_cline_script|run_eval\.py|run_on_sandbox' 2>/dev/null); do
  case "$p" in "$$"|"$PPID") continue;; esac
  cl=$(tr '\0' ' ' < /proc/$p/cmdline 2>/dev/null | cut -c1-110)
  case "$cl" in *zhulong_loop*|*ZHULONG_TASK*) continue;; esac
  if is_eval_proc "$p" || echo "$cl" | grep -q '^bash scripts/run_cline_script'; then
    LEFT=$((LEFT+1)); echo "   ⚠️ 残留 pid=$p $cl"
  fi
done
echo "   AFTER：评测侧残留计数=$LEFT （0 = 已停干净）"
EVAL_ALIVE=$(timeout 20 pgrep -f '^bash scripts/run_cline_script' 2>/dev/null | wc -l)
echo "   仍存活的评测编排进程数（锚定匹配）= $EVAL_ALIVE"

echo
echo "=========== 2. 删除 ~/.cline/hooks/PreToolUse ==========="
echo "-- BEFORE --"
timeout 20 ls -l ~/.cline/hooks/ 2>&1 | cut -c1-140
timeout 20 stat -c '%n %s bytes mtime=%y' ~/.cline/hooks/PreToolUse 2>&1 | cut -c1-160
timeout 20 rm -f ~/.cline/hooks/PreToolUse; echo "   rm exit=$?"
echo "-- AFTER（应为空或不存在）--"
timeout 20 ls -l ~/.cline/hooks/ 2>&1 | cut -c1-140
echo "-- 参考：eval 侧 hooks 目录（run_cli.sh 的部署目标）--"
timeout 20 ls -l ~/.cline_prof4_eval/data/hooks/ 2>&1 | cut -c1-140

echo
echo "=========== 3. eda_fastmcp/.env —— 备份 + git stash（回退昨晚改动）==========="
echo "-- 3.1 .env 关键行（改动前）--"
timeout 20 grep -nE '^[[:space:]]*(export[[:space:]]+)?(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL|EDA_MCP_PORT)=' "$ENVF" 2>&1 | cut -c1-260
echo "-- 3.2 git 状态（eda_fastmcp 仓库）--"
timeout 60 git -C "$EDA" status --porcelain 2>&1 | head -12 | cut -c1-120
echo "   .env 是否被 git 跟踪：$(timeout 60 git -C "$EDA" ls-files .env 2>/dev/null | head -1)"
echo "-- 3.3 git HEAD 版 .env 关键行（= stash 回退后的目标基线）--"
timeout 60 git -C "$EDA" show HEAD:.env 2>/dev/null | grep -nE '^[[:space:]]*(export[[:space:]]+)?(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' | cut -c1-280
echo "-- 3.4 备份 + stash --"
timeout 30 cp -p "$ENVF" "/tmp/eda_fastmcp.env.bak.$TS" && echo "   backup=/tmp/eda_fastmcp.env.bak.$TS"
timeout 60 git -C "$EDA" stash push -m "RUN_ID32: stash .env (回退昨晚端口改动) @ $TS" -- .env 2>&1 | cut -c1-160
echo "   stash exit=$?"
timeout 30 git -C "$EDA" stash list 2>&1 | head -3 | cut -c1-140
echo "-- 3.5 .env 关键行（stash 回退后，应 = HEAD 基线）--"
timeout 20 grep -nE '^[[:space:]]*(export[[:space:]]+)?(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' "$ENVF" 2>&1 | cut -c1-260

echo
echo "=========== 3.6 回退 cline_mcp_settings.json 的 \"timeout\": 180（用户 10-11 追加令：昨晚改动全部回退）==========="
PY=$(command -v python3 || command -v python || true)
echo "   python = ${PY:-<none>}"
echo "-- 旧备份参考（(八) 若留过备份，可作还原依据）--"
timeout 20 ls -lt /tmp/*cline_mcp_settings* 2>/dev/null | head -5 | cut -c1-150
for f in ~/.cline/data/settings/cline_mcp_settings.json ~/.cline_prof4_eval/data/settings/cline_mcp_settings.json; do
  echo "-- $f --"
  if [ ! -f "$f" ]; then echo "   （不存在，跳过）"; continue; fi
  timeout 20 stat -c '   BEFORE mtime=%y size=%s' "$f"
  timeout 20 grep -oE '"timeout"[[:space:]]*:[[:space:]]*[0-9]+' "$f" | head -4 | sed 's/^/   BEFORE /'
  BK="/tmp/cline_mcp_settings.$(echo "$f" | tr '/.' '__').bak.$TS"
  timeout 30 cp -p "$f" "$BK" && echo "   backup=$BK"
  if [ -z "$PY" ]; then
    echo "   ⚠️ 无 python → 为免写坏 JSON，本文件不改（需人工处理）"
  else
    "$PY" - "$f" <<'PYEOF'
import json, sys
p = sys.argv[1]
try:
    d = json.load(open(p, encoding='utf-8'))
except Exception as e:
    print("   \u26a0 JSON \u89e3\u6790\u5931\u8d25\uff0c\u672a\u6539\uff1a", e); sys.exit(0)
rem = []
def walk(o, path=''):
    if isinstance(o, dict):
        for k in list(o.keys()):
            if k == 'timeout' and isinstance(o[k], int) and o[k] == 180:
                o.pop(k); rem.append(path + '/' + k + '=180')
            else:
                walk(o[k], path + '/' + k)
    elif isinstance(o, list):
        for i, v in enumerate(o):
            walk(v, path + '/[%d]' % i)
walk(d)
if rem:
    with open(p, 'w', encoding='utf-8') as fh:
        fh.write(json.dumps(d, ensure_ascii=False, indent=2) + "\n")
print("   removed timeout=180 keys =", len(rem), rem[:5])
if not rem:
    print("   (no timeout=180 found -> idempotent) ")
PYEOF
    echo "   python exit=$?"
    timeout 20 "$PY" -c "import json,sys; json.load(open(sys.argv[1],encoding='utf-8')); print('   JSON 校验=OK')" "$f" 2>&1 | tail -1
  fi
  timeout 20 grep -oE '"timeout"[[:space:]]*:[[:space:]]*[0-9]+' "$f" | head -4 | sed 's/^/   AFTER /'
  if timeout 20 grep -q '"timeout"' "$f"; then echo "   AFTER ⚠️ 仍有 timeout 键（见上；非 180 的值保留）"; else echo "   AFTER ✅ 已无任何 timeout 键"; fi
done

echo
echo "=========== 3.7 其它可能受昨晚改动影响的本地状态（只读，不改）==========="
for r in "$EDA" /nasdata/app.e0031982/code/EDA-Eval-Framework; do
  [ -d "$r/.git" ] || { echo "   [$r] 非 git 仓库，跳过"; continue; }
  echo "   [$r] status --porcelain（前 8 行）:"
  timeout 60 git -C "$r" status --porcelain 2>/dev/null | head -8 | sed 's/^/      /' | cut -c1-140
  echo "   [$r] stash list（前 3 行）:"
  timeout 60 git -C "$r" stash list 2>/dev/null | head -3 | sed 's/^/      /' | cut -c1-140
done
echo "   -- ~/.cline* 近 24h 被改过的 json（有界扫描，仅列出）--"
timeout 60 find ~/.cline ~/.cline_prof4_eval -maxdepth 3 -name '*.json' -newermt '24 hours ago' 2>/dev/null | head -10 | cut -c1-150
echo "   -- ~/.cline/hooks 内容（删除前已由 ②记录；此处为 3.6 之后状态）--"
timeout 20 ls -l ~/.cline/hooks/ 2>&1 | cut -c1-140

echo
echo "=========== 4. 写新 .env：端口集 8650/8651/8652/8654 + RAG 9006 ==========="
HEAD_SE=$(timeout 60 git -C "$EDA" show HEAD:.env 2>/dev/null | sed -n 's/^[[:space:]]*SANDBOX_ENDPOINTS=//p' | tail -1)
CUR_SE=$(sed -n 's/^[[:space:]]*SANDBOX_ENDPOINTS=//p' "$ENVF" 2>/dev/null | tail -1)
SRC_SE="${CUR_SE:-$HEAD_SE}"
NEW_SE=$(printf '%s' "$SRC_SE" | tr ',' '\n' | grep -E '^(8650|8651|8652|8654):' | tr '\n' ',' | sed 's/,$//')
SE_SRC="来自 .env/HEAD 既有映射"
if [ -z "$NEW_SE" ] || [ "$(printf '%s' "$NEW_SE" | tr ',' '\n' | grep -c ':')" -ne 4 ]; then
  NEW_SE="8650:/proj/train/AI/workdir/t0002997_1,8651:/proj/train/AI/workdir/t0002997_2,8652:/proj/train/AI/workdir/t0002997_3,8654:/proj/train/AI/workdir/t0002997_4"
  SE_SRC="⚠️ 兜底默认值（.env/HEAD 无可用映射）→ 必须人工核对 workdir"
fi
echo "   SANDBOX_ENDPOINTS 来源 = $SE_SRC"
echo "   SANDBOX_ENDPOINTS 新值 = $NEW_SE"
grep -vE '^[[:space:]]*(export[[:space:]]+)?(PROXY_PORTS|SANDBOX_ENDPOINTS|RAG_RECALL_URL)=' "$ENVF" > "$ENVF.tmp32"
cat >> "$ENVF.tmp32" <<EOF
PROXY_PORTS=8650,8651,8652,8654
SANDBOX_ENDPOINTS=$NEW_SE
RAG_RECALL_URL=http://localhost:9006/recall
EOF
timeout 30 mv "$ENVF.tmp32" "$ENVF"; echo "   写入 exit=$?"
timeout 30 cp -p "$ENVF" "/tmp/eda_fastmcp.env.RUNID32.$TS" && echo "   新 .env 副本=/tmp/eda_fastmcp.env.RUNID32.$TS"
echo "-- 4.1 校验（关键行，应各 1 行）--"
timeout 20 grep -nE '^[[:space:]]*(export[[:space:]]+)?(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' "$ENVF" 2>&1 | cut -c1-300
echo "   行数：PROXY_PORTS=$(timeout 20 grep -cE '^PROXY_PORTS=' "$ENVF") SANDBOX_ENDPOINTS=$(timeout 20 grep -cE '^SANDBOX_ENDPOINTS=' "$ENVF") RAG_RECALL_URL=$(timeout 20 grep -cE '^RAG_RECALL_URL=' "$ENVF")"
echo "-- 4.2 diff（备份 vs 现在，仅关键行）--"
timeout 20 diff <(grep -E '^(PROXY_PORTS|SANDBOX_ENDPOINTS|RAG_RECALL_URL)=' "/tmp/eda_fastmcp.env.bak.$TS" 2>/dev/null) <(grep -E '^(PROXY_PORTS|SANDBOX_ENDPOINTS|RAG_RECALL_URL)=' "$ENVF" 2>/dev/null) | cut -c1-320

echo
echo "=========== 5. 重启 eda_fastmcp（MCP :8090）+ 核验 ==========="
echo "-- BEFORE --"
timeout 20 ss -lntp 2>/dev/null | grep -E ':8090' | cut -c1-150
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v 'cline' | cut -c1-130 | head -3
( cd "$EDA" && timeout 120 bash scripts/stop.sh ) >/tmp/eda_stop_runid32.log 2>&1; echo "   stop.sh exit=$?"
sleep 3
( cd "$EDA" && timeout 180 bash scripts/start.sh ) >/tmp/eda_start_runid32.log 2>&1; echo "   start.sh exit=$?"
timeout 20 tail -3 /tmp/eda_start_runid32.log 2>/dev/null | cut -c1-170
sleep 5
echo "-- AFTER --"
timeout 20 ss -lntp 2>/dev/null | grep -E ':8090' | cut -c1-150
timeout 20 pgrep -af 'python main\.py' 2>/dev/null | grep -v 'cline' | cut -c1-130 | head -3

echo
echo "=========== 6. 4 端口实测（TCP + run_code 实跑）==========="
OK=0
if [ "$EVAL_ALIVE" -gt 0 ]; then
  echo "   ⏭ eval 仍在跑（EVAL_ALIVE=$EVAL_ALIVE）→ 跳过 run_code 探测（端口被占，探测结果不可判）"
else
  for p in $PORTS; do
    if timeout 5 bash -c "echo > /dev/tcp/$SHOST/$p" 2>/dev/null; then tcp="OK"; else tcp="CLOSED"; fi
    body=$(timeout 25 curl -s -m 12 -X POST "http://$SHOST:$p/v1/run_code" -H 'Content-Type: application/json' -d '{"code":"print(1)","lang":"pyAether","host":"aether"}' 2>/dev/null)
    n=${#body}
    if [ "$n" -gt 0 ]; then rc="OK"; OK=$((OK+1)); else rc="FAIL(0byte)"; fi
    echo "   port $p : TCP=$tcp  run_code=$rc  resp_len=$n  | $(printf '%s' "$body" | cut -c1-90)"
  done
fi
echo "   ▶ 健康端口数 = $OK / 4"

echo
echo "=========== 7. 起动 C1.full r2（硬闸：EVAL_ALIVE=0 且 4/4 健康）==========="
if [ "$EVAL_ALIVE" -eq 0 ] && [ "$OK" -eq 4 ]; then
  ( cd "$EDA"
    export EVAL_FW_DIR=/nasdata/app.e0031982/code/EDA-Eval-Framework
    export CLI_DATA_DIR=/nasdata/app.e0031982/.cline_prof4_eval/data
    export PYTHON=/nasdata/app.e0031982/code/eda_fastmcp/venv/bin/python
    export https_proxy=http://172.19.92.23:13128
    setsid bash scripts/run_cline_script.sh -p 8 -n > "$LOG" 2>&1 < /dev/null &
  )
  echo "   已下发 setsid 起动，等待 20s 后核验 ..."
  sleep 20
  NEW=$(timeout 20 pgrep -f '^bash scripts/run_cline_script' 2>/dev/null | head -1)
  echo "   新 eval PID=${NEW:-<none>}"
  if [ -n "$NEW" ]; then
    echo "   -- 四 override 核验（/proc/$NEW/environ）--"
    timeout 20 tr '\0' '\n' < /proc/$NEW/environ 2>/dev/null | grep -E '^(EVAL_FW_DIR|CLI_DATA_DIR|PYTHON|https_proxy)=' | cut -c1-170
    echo "   -- 反作弊 hook 是否被本轮重新部署（删完必检）--"
    timeout 20 ls -l ~/.cline/hooks/PreToolUse 2>&1 | cut -c1-140
    timeout 20 ls -l ~/.cline_prof4_eval/data/hooks/PreToolUse 2>&1 | cut -c1-140
  fi
  echo "   -- log head（前 45 行）--"
  timeout 20 head -45 "$LOG" 2>/dev/null | cut -c1-180
else
  echo "   ⛔ 未起动 eval（EVAL_ALIVE=$EVAL_ALIVE，健康端口=$OK/4）—— 按 (八)⑤ 硬闸：不健康不开跑，等运维裁定"
fi

echo
echo "=========== 8. 环境核验 + 披露快照 ==========="
echo "-- loop --"
LPID=$(timeout 20 pgrep -f 'zhulong_loop\.sh' 2>/dev/null | head -1)
echo "   loop pid=${LPID:-<none>}"
[ -n "${LPID:-}" ] && timeout 20 tr '\0' '\n' < /proc/$LPID/environ 2>/dev/null | grep -E '^https_proxy=' | cut -c1-90
echo "-- RAG recall 9006 --"
timeout 20 ss -lntp 2>/dev/null | grep -E ':9006' | cut -c1-150
timeout 20 curl -s -m 8 -o /dev/null -w '   http_code=%{http_code} (400/404/405 = 服务在，连通 OK)\n' http://localhost:9006/recall 2>&1
echo "-- 磁盘（<8G = 起跑前须复核）--"
timeout 20 df -BG /home /nasdata /tmp 2>/dev/null | cut -c1-120
echo "-- 披露快照：cline_mcp_settings.json 的 timeout（本块已回退 timeout=180；输出为空 = 已无该键）--"
for f in ~/.cline/data/settings/cline_mcp_settings.json ~/.cline_prof4_eval/data/settings/cline_mcp_settings.json; do
  echo "   $f -> $(timeout 20 grep -oE '"timeout"[[:space:]]*:[[:space:]]*[0-9]+' "$f" 2>/dev/null | head -1)"
  timeout 20 stat -c '      mtime=%y' "$f" 2>/dev/null
done
echo "-- 回退备份清单（settings / .env）--"
timeout 20 ls -lt /tmp/cline_mcp_settings* /tmp/eda_fastmcp.env*.bak.* /tmp/eda_fastmcp.env.RUNID32.* 2>/dev/null | head -8 | cut -c1-150
echo "-- .env 最终关键行 --"
timeout 20 grep -nE '^(PROXY_PORTS|SANDBOX_ENDPOINTS|SANDBOX_HOST|RAG_RECALL_URL)=' "$ENVF" 2>&1 | cut -c1-300

echo
echo "== DONE — RUN_ID 32（停评测 / 删hook / stash回退 / .env 换 8650-8654+RAG9006 / 回退 timeout:180 / 重启MCP / 实测 / 起 r2）=="
```

## RUN_ID 31 — 🔎 验证 EDA_MCP_PORT=8090 是否被继承（中继是「非交互 bash」，不读 ~/.bashrc）

**背景**：用户 2026-10-10 指出 MCP 端口 = **8090**（非 18889），并说已在 36.15 `~/.bashrc` 设置该环境变量"应该可以继承"。但 **RUN_ID 29 已证明中继（非交互 bash）不读 `~/.bashrc`**（loop 找不到 `cline`）。本块核实：中继 env / `.bashrc` / loop environ / MCP 监听 / cline MCP 配置。

```text
# RUN_ID 31 — verify EDA_MCP_PORT=8090 inheritance
echo "== RUN_ID 31 @ $(date '+%F %T') host=$(hostname) =="

echo "== 1. relay env (non-interactive bash) =="
echo "EDA_MCP_PORT=[${EDA_MCP_PORT:-<UNSET>}]"
echo "PATH=[$PATH]" | cut -c1-200

echo "== 2. ~/.bashrc has EDA_MCP_PORT? =="
grep -n 'EDA_MCP_PORT' ~/.bashrc 2>&1 | cut -c1-160

echo "== 3. MCP server listening on 8090? =="
ss -lntp 2>/dev/null | grep -E ':8090' | cut -c1-160
timeout 10 pgrep -af 'eda_fastmcp|main.py' | cut -c1-160

echo "== 4. eda_fastmcp/.env port =="
grep -nE '^#?[[:space:]]*EDA_MCP_PORT' /nasdata/app.e0031982/code/eda_fastmcp/.env 2>&1 | cut -c1-120

echo "== 5. restarted loop environ (has EDA_MCP_PORT? PATH ok?) =="
LPID=$(pgrep -f 'zhulong_loop.sh' | head -1); echo "loop pid=${LPID:-<none>}"
[ -n "${LPID:-}" ] && tr '\0' '\n' < /proc/$LPID/environ 2>/dev/null | grep -E 'EDA_MCP_PORT|^PATH=' | cut -c1-220

echo "== 6. which port does cline's MCP config point to? =="
grep -rnE '8090|pyAether|eda_fastmcp' ~/.cline/data/settings/ 2>/dev/null | cut -c1-160 | head -8
grep -rnE '8090|pyAether|eda_fastmcp' /nasdata/app.e0031982/.cline_zhulong/ 2>/dev/null | cut -c1-160 | head -8

echo "== DONE =="
```

## RUN_ID 30 — 🔧 修 loop PATH（cline@~/.bun/bin）+ 去重保证单个 loop

**背景**：RUN_ID 29 重启的 loop 日志报 `env: 'cline': No such file or directory`（中继非交互 env 缺 `~/.bun/bin`）→ loop **静默失效**；且出现 **2 个 loop 进程**。本条：停全部 loop → 带 `~/.bun/bin` PATH 重启**单个** loop，并校验 `cline` 可解析、loop 能真正拉起 cline。

```text
# RUN_ID 30 — fix loop PATH (cline@~/.bun/bin) + ensure single loop
echo "== RUN_ID 30 @ $(date '+%F %T') host=$(hostname) =="
cd /nasdata/app.e0031982/code/super_intelligence_2035 2>/dev/null || cd /nas_train/app.e0031982/code/super_intelligence_2035 || true

echo "== 1. locate cline =="
ls -l ~/.bun/bin/cline 2>&1 | cut -c1-160
ls -l ~/.local/bin/cline 2>&1 | cut -c1-160

echo "== 2. BEFORE: all loops =="
ps -eo pid,ppid,etime,cmd | grep 'zhulong_loop.sh' | grep -v grep | cut -c1-160

echo "== 3. stop ALL loops =="
pkill -f 'zhulong_loop.sh' 2>&1; echo "pkill exit=$?"; sleep 3
ps -eo pid,cmd | grep 'zhulong_loop.sh' | grep -v grep | cut -c1-160
echo "(empty above = all stopped)"

echo "== 4. restart ONE loop with correct PATH =="
export PATH="$HOME/.bun/bin:$HOME/.local/bin:$PATH"
export https_proxy=http://172.19.92.23:13128
export http_proxy=http://172.19.92.23:13128
echo "cline -> $(command -v cline)"
setsid bash doc/ZhuLong_DAC2027/run/zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
sleep 8
echo "-- loops now (expect exactly 1) --"; ps -eo pid,ppid,etime,cmd | grep 'zhulong_loop.sh' | grep -v grep | cut -c1-160
echo "-- loop log tail --"; tail -6 /tmp/zhulong_loop.log 2>&1 | cut -c1-200
echo "== DONE =="
```

## RUN_ID 29 — 🛑 删防作弊 hook + 停评测 + 重启 zhulong loop + 采集 timeout 取证

**背景**：用户令「先用 ops 中继：① 删 `~/.cline/hooks/PreToolUse` ② 停下评测 ③ 重启 zhulong loop（重启前把唤醒周期降到 30min —— 经确认 `SLEEP_WAIT=1800s` 本就是 30min，无需改）」，并要求排查连续多日的评测 timeout 根因。

```text
# RUN_ID 29 — del hook + stop eval + restart loop + timeout evidence
echo "== RUN_ID 29 @ $(date '+%F %T') host=$(hostname) =="
cd /nasdata/app.e0031982/code/super_intelligence_2035 2>/dev/null || cd /nas_train/app.e0031982/code/super_intelligence_2035 || true
echo "cwd=$(pwd)"

echo "== 1. BEFORE: eval / loop state =="
ps -eo pid,ppid,etime,state,cmd | grep -E 'run_cline_script|run_eval|zhulong_loop' | grep -v grep | cut -c1-160

echo "== 2. DELETE anti-cheat hook ~/.cline/hooks/PreToolUse =="
ls -la ~/.cline/hooks/ 2>&1 | cut -c1-160
if [ -e ~/.cline/hooks/PreToolUse ]; then
  echo "type=$(stat -c '%F' ~/.cline/hooks/PreToolUse 2>/dev/null)"
  rm -rf ~/.cline/hooks/PreToolUse 2>&1; echo "rm exit=$?"
else
  echo "(PreToolUse not present)"
fi
echo "-- after --"; ls -la ~/.cline/hooks/ 2>&1 | cut -c1-160

echo "== 3. STOP eval (r2_new2 retry#1) =="
pkill -TERM -f 'run_cline_script' 2>&1; echo "pkill -TERM run_cline exit=$?"
pkill -TERM -f 'run_eval.py' 2>&1; echo "pkill -TERM run_eval exit=$?"
sleep 4
pkill -KILL -f 'run_cline_script' 2>&1; echo "pkill -KILL run_cline exit=$?"
pkill -KILL -f 'run_eval.py' 2>&1; echo "pkill -KILL run_eval exit=$?"
sleep 2
echo "-- after: expect empty --"
ps -eo pid,ppid,etime,cmd | grep -E 'run_cline_script|run_eval' | grep -v grep | cut -c1-160

echo "== 4. EVIDENCE: timeout / MCP / hook in eval logs =="
for f in /tmp/ABL_full_r2_new2.log /tmp/ABL_full_r2_new.log; do
  [ -f "$f" ] || { echo "$f (missing)"; continue; }
  echo "--- $f : $(wc -l < "$f") lines / $(du -h "$f" | cut -f1) ---"
  echo "timeout(all)=$(grep -c -i 'timeout' "$f")  MCP-32001=$(grep -c '32001' "$f")  ACCESS_RESTRICTED=$(grep -c 'ACCESS RESTRICTED' "$f")  Forbidden=$(grep -c 'Forbidden' "$f")"
  echo "PASS_RATE lines:"; grep -E 'PASS_RATE|评估结果汇总' "$f" | tail -3 | cut -c1-200
  echo "sample timeout lines:"; grep -i 'timeout' "$f" | head -3 | cut -c1-200
  echo "last 5 lines:"; tail -5 "$f" | cut -c1-200
done

echo "== 5. Port TCP connect probe (9 ports, 10.129.32.75) =="
for p in 8663 8666 8667 8670 8650 8651 8652 8653 8654; do
  (timeout 5 bash -c "echo > /dev/tcp/10.129.32.75/$p" 2>/dev/null && echo "port $p: TCP-OPEN") || echo "port $p: CLOSED/UNREACHABLE"
done

echo "== 6. RESTART zhulong loop (SLEEP_WAIT should be 1800=30min) =="
grep -E '^SLEEP_BUSY=|^SLEEP_WAIT=|^CLINE_TIMEOUT=' doc/ZhuLong_DAC2027/run/zhulong_loop.sh
pkill -f 'zhulong_loop.sh' 2>&1; echo "pkill loop exit=$?"; sleep 3
ps -eo pid,cmd | grep 'zhulong_loop.sh' | grep -v grep | cut -c1-160
export https_proxy=http://172.19.92.23:13128
export http_proxy=http://172.19.92.23:13128
setsid bash doc/ZhuLong_DAC2027/run/zhulong_loop.sh > /tmp/zhulong_loop.log 2>&1 < /dev/null &
sleep 4
echo "-- new loop --"; ps -eo pid,ppid,etime,cmd | grep 'zhulong_loop.sh' | grep -v grep | cut -c1-160
echo "-- loop log tail --"; tail -3 /tmp/zhulong_loop.log 2>&1 | cut -c1-200

echo "== DONE (hook deleted / eval stopped / loop restarted) =="
```

## RUN_ID 28 — 🛑 kill r2-retest#5 (PID 1471081, 旧沙盒) + 验证新专属端口 8663/8666/8667/8670

**背景**：agent 在读新指令前已启动 r2-retest#5（PID 1471081, ~10:19, 旧沙盒 8650-8654）。.env 已改为新端口 8663/8666/8667/8670。需 kill r2-retest#5 让 agent 发现 IDLE → 读 2026-10-10(一) 指令 → 从 r1 重测。同时验证新端口可达。

```text
# RUN_ID 28 — kill r2-retest#5 + verify new dedicated sandbox ports
echo "== RUN_ID 28: kill r2-retest#5 + verify new ports @ $(date '+%F %T') =="

echo "== 1. BEFORE kill: current eval process =="
ps -eo pid,ppid,etime,state,cmd | grep -E '1471081|run_cline_script|run_eval' | grep -v grep | cut -c1-140

echo "== 2. KILL r2-retest#5 (PID 1471081) + children =="
kill -TERM 1471081 2>&1; echo "kill -TERM 1471081 exit=$?"
sleep 3
pkill -TERM -P 1471081 2>&1; echo "pkill -P 1471081 exit=$?"
sleep 2
kill -KILL 1471081 2>&1; echo "kill -KILL 1471081 exit=$?"
pkill -KILL -P 1471081 2>&1; echo "pkill -KILL -P 1471081 exit=$?"
sleep 1

echo "== 3. KILL any stray run_eval.py =="
pkill -KILL -f 'run_eval.py' 2>&1; echo "pkill run_eval exit=$?"
pkill -KILL -f 'run_cline_script' 2>&1; echo "pkill run_cline exit=$?"
sleep 1

echo "== 4. AFTER kill: verify no eval processes remain =="
ps -eo pid,ppid,etime,state,cmd | grep -E 'run_cline_script|run_eval' | grep -v grep | cut -c1-140
echo "(empty above = clean kill ✅)"

echo "== 5. Verify NEW dedicated sandbox ports 8663/8666/8667/8670 =="
for p in 8663 8666 8667 8670; do
  echo -n "port $p: "; timeout 10 curl -s -o /dev/null -w 'HTTP=%{http_code} TIME=%{time_total}s' http://10.129.32.75:$p 2>&1; echo
done

echo "== 6. .env verify (should show 8663/8666/8667/8670) =="
grep -E '^PROXY_PORTS|^SANDBOX_ENDPOINTS' /nasdata/app.e0031982/code/eda_fastmcp/.env

echo "== 7. pro-fp4 new key still 200? =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer 02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -3

echo "== 8. zhulong_loop alive? (PID 3579323 - DO NOT KILL) =="
ps -eo pid,ppid,etime,state,cmd | grep '3579323' | grep -v grep | cut -c1-140

echo "== DONE — r2-retest#5 killed, new ports verified, agent will restart C1.full from r1 =="

**背景**：用户 2026-10-10 通知切换到专属沙盒端口 8663/8666/8667/8670（workdir e0031982_1~4, host 不变 10.129.32.75），.env 已改。C1.full 现有评测全部作废需重测。当前 r2-retest#4（PID 459294）仍在旧沙盒上跑，需 kill 后验证新端口可达。

```bash
# RUN_ID 27 — kill r2-retest#4 + verify new dedicated sandbox ports
echo "== RUN_ID 27: kill r2-retest#4 + verify new ports @ $(date '+%F %T') =="

echo "== 1. BEFORE kill: r2-retest#4 process tree =="
ps -eo pid,ppid,etime,state,cmd | grep -E '459294|run_cline_script|run_eval' | grep -v grep | cut -c1-140

echo "== 2. KILL r2-retest#4 (PID 459294) + children =="
kill -TERM 459294 2>&1; echo "kill -TERM 459294 exit=$?"
sleep 3
pkill -TERM -P 459294 2>&1; echo "pkill -P 459294 exit=$?"
sleep 2
kill -KILL 459294 2>&1; echo "kill -KILL 459294 exit=$?"
pkill -KILL -P 459294 2>&1; echo "pkill -KILL -P 459294 exit=$?"
sleep 1

echo "== 3. KILL any stray run_eval.py / run_cline_script =="
pkill -KILL -f 'run_eval.py.*2026_1010_062131' 2>&1; echo "pkill run_eval exit=$?"
pkill -KILL -f 'run_cline_script.*r2_retest4' 2>&1; echo "pkill run_cline exit=$?"
sleep 1

echo "== 4. AFTER kill: verify no eval processes remain =="
ps -eo pid,ppid,etime,state,cmd | grep -E '459294|run_cline_script|run_eval' | grep -v grep | cut -c1-140
echo "(empty above = clean kill ✅)"

echo "== 5. Verify NEW dedicated sandbox ports 8663/8666/8667/8670 reachable =="
for p in 8663 8666 8667 8670; do
  echo -n "port $p: "; timeout 10 curl -s -o /dev/null -w 'HTTP=%{http_code} TIME=%{time_total}s' http://10.129.32.75:$p 2>&1; echo
done

echo "== 6. Verify OLD sandbox ports 8650/8651/8652/8654 (should still respond, just not used) =="
for p in 8650 8651 8652 8654; do
  echo -n "port $p: "; timeout 5 curl -s -o /dev/null -w 'HTTP=%{http_code}' http://10.129.32.75:$p 2>&1; echo
done

echo "== 7. pro-fp4 new key still 200? =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer 02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -3

echo "== 8. zhulong_loop still alive? (PID 3579323 - DO NOT KILL) =="
ps -eo pid,ppid,etime,state,cmd | grep '3579323' | grep -v grep | cut -c1-140

echo "== 9. .env SANDBOX_ENDPOINTS verify (should show 8663/8666/8667/8670) =="
grep -E 'PROXY_PORTS|SANDBOX_ENDPOINTS' /nasdata/app.e0031982/code/eda_fastmcp/.env | grep -v '^#'

echo "== DONE — r2-retest#4 killed, new ports verified, standby for C1.full restart =="

**背景**：用户 2026-10-09 17:00 通知「沙盒坏了，下发指令把 r4 停下来，待命」。r4 grading 阶段异常缓慢（r1=8min/150脚本 vs r4=1h48m+/140脚本，13×+慢），log 沉默 2h+，沙盒端口 8650/8651/8652/8654 全部无响应（RUN_ID 24 诊断已确认沙盒坏了）。需 kill r4 整个进程树（主进程 PID 3302534 + run_eval.py 子进程 PID 611439 + 所有 worker），确认干净退出，然后待命。

```text
# RUN_ID 26 — ARCHIVED (already executed, see outbox.md RUN_ID 26)
echo "== RUN_ID 26: kill r4 @ $(date '+%F %T') =="

echo "== 1. BEFORE kill: r4 process tree =="
ps -eo pid,ppid,etime,state,cmd | grep -E '3302534|run_cline_script|run_eval' | grep -v grep | cut -c1-140

echo "== 2. KILL r4 main process (PID 3302534) + children =="
kill -TERM 3302534 2>&1; echo "kill -TERM 3302534 exit=$?"
sleep 3
# kill any remaining children (run_eval.py etc.)
pkill -TERM -P 3302534 2>&1; echo "pkill -P 3302534 exit=$?"
sleep 2
# force kill if still alive
kill -KILL 3302534 2>&1; echo "kill -KILL 3302534 exit=$?"
pkill -KILL -P 3302534 2>&1; echo "pkill -KILL -P 3302534 exit=$?"
sleep 1

echo "== 3. KILL any stray run_eval.py from this batch =="
pkill -KILL -f 'run_eval.py.*2026_1009_094504' 2>&1; echo "pkill run_eval exit=$?"
pkill -KILL -f 'run_cline_script.*ABL_full_r4' 2>&1; echo "pkill run_cline exit=$?"
sleep 1

echo "== 4. AFTER kill: verify no r4 processes remain =="
ps -eo pid,ppid,etime,state,cmd | grep -E '3302534|run_cline_script|run_eval' | grep -v grep | cut -c1-140
echo "(empty above = clean kill ✅)"

echo "== 5. r4 log final state =="
timeout 10 wc -l /tmp/ABL_full_r4.log 2>&1
timeout 10 tail -5 /tmp/ABL_full_r4.log 2>&1

echo "== 6. zhulong_loop still alive? (PID 3579323 - DO NOT KILL) =="
ps -eo pid,ppid,etime,state,cmd | grep '3579323' | grep -v grep | cut -c1-140
echo "(loop should be alive - we only killed eval, not loop)"

echo "== 7. sandbox ports status =="
for p in 8650 8651 8652 8654; do
  echo -n "port $p: "; timeout 5 curl -s -o /dev/null -w '%{http_code}' http://10.129.32.75:$p 2>&1; echo
done

echo "== 8. pro-fp4 new key still 200? =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer 02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -3

echo "== DONE — r4 killed, standby =="
```

> ⚠️ 本块 kill r4 eval 进程树（PID 3302534 + 子进程），**不 kill zhulong_loop（PID 3579323）**、不 kill ops relay、不 kill legacy loop。kill 后验证干净退出 + 沙盒/pro-fp4 状态。总超时 <60s。

---

## RUN_ID 24 — 🚨 诊断：agent 4.5h 无心跳，检查 loop/eval 进程 + r4 日志状态【已执行·已归档】

**背景**：agent 自 09:54 commit 后无心跳，MEMORY/daily-memories 均未更新。r4 batch b2026_1009_094504 PID 3302534 仍标「运行中」，但已跑 4.5h（远超正常 30-40min）。需诊断 loop 进程是否存活、eval 是否卡住/已结束、r4 log 内容。

```text
# RUN_ID 24 — ARCHIVED (already executed, see outbox.md RUN_ID 24)
echo "== RUN_ID 24: diagnostic @ $(date '+%F %T') =="

echo "== 1. zhulong_loop process (PID 3579323 expected) =="
ps -eo pid,ppid,etime,state,cmd | grep -E 'zhulong_loop|3579323' | grep -v grep | cut -c1-140

echo "== 2. eval process (PID 3302534 expected) =="
ps -eo pid,ppid,etime,state,cmd | grep -E 'run_cline_script|3302534' | grep -v grep | cut -c1-140

echo "== 3. any cline processes alive? =="
pgrep -af cline | grep -v grep | cut -c1-140

echo "== 4. r4 log tail (last 20 lines) =="
timeout 10 tail -20 /tmp/ABL_full_r4.log 2>&1

echo "== 5. r4 log size + grep PASS_RATE/timeout/pass =="
timeout 10 wc -l /tmp/ABL_full_r4.log 2>&1
timeout 10 grep -cE 'timeout|timed.?out' /tmp/ABL_full_r4.log 2>&1
timeout 10 grep -E 'PASS_RATE|pass \(|评估结果汇总' /tmp/ABL_full_r4.log 2>&1 | tail -5

echo "== 6. ops relay alive? (PID 888464) =="
ps -eo pid,ppid,etime,state,cmd | grep -E 'ops_relay|888464' | grep -v grep | cut -c1-140

echo "== 7. /home disk space =="
df -h /home 2>&1 | tail -2

echo "== 8. pro-fp4 still 200? (new key quick check) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer 02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e" \
  -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -3

echo "== 9. sandbox ports reachable? =="
for p in 8650 8651 8652 8654; do
  echo -n "port $p: "; timeout 5 curl -s -o /dev/null -w '%{http_code}' http://10.129.32.75:$p 2>&1; echo
done

echo "== DONE =="
```

> 本块纯只读诊断（ps/grep/df/curl），不改文件不动进程。总超时 <120s。

---

## RUN_ID 23 — 🔬 测试新 key + deepseek-v4-pro-cloud 是否可绕过 pro-fp4 的 403（6 组合）【已执行·已归档】

**背景**：pro-fp4 额度 HTTP 403 阻塞 C1.full r4/r5（已复检 9 次未恢复）。用户提供新 key（e13f4f37）+ 模型名 deepseek-v4-pro-cloud，问能否绕过。本块纯只读 curl，测 6 个组合以区分 403 根因 = key 额度 / 模型额度 / endpoint 差异。

```text
# RUN_ID 23 — ARCHIVED (already executed, see outbox.md RUN_ID 23)
echo "== RUN_ID 23: key/model/endpoint test =="; timeout 10 date '+%F %T'
OLDKEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
NEWKEY="02_088EE9051AAE4BF0ABFC7130331BF697_e13f4f37-836a-48a5-b149-044c8aa0785e"

echo "== 1. NEW key + pro-cloud @ /cloud/v1 (user suggestion) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer $NEWKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-cloud","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== 2. NEW key + pro-fp4 @ /cloud/v1 (does new key fix 403 for ORIGINAL model?) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer $NEWKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== 3. NEW key + pro-fp4 @ /v1 (original pro-fp4 endpoint) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/v1/chat/completions \
  -H "Authorization: Bearer $NEWKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== 4. OLD key + pro-fp4 @ /cloud/v1 (confirm 403 baseline) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/cloud/v1/chat/completions \
  -H "Authorization: Bearer $OLDKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== 5. OLD key + pro-fp4 @ /v1 (original endpoint baseline) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/v1/chat/completions \
  -H "Authorization: Bearer $OLDKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-fp4","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== 6. NEW key + pro-cloud @ /v1 (is cloud model also on /v1?) =="
timeout 15 curl --noproxy '*' -s -w '\nHTTP=%{http_code} TIME=%{time_total}s SIZE=%{size_download}B\n' \
  -X POST http://agi-gateway.cxmt.com/v1/chat/completions \
  -H "Authorization: Bearer $NEWKEY" -H 'Content-Type: application/json' \
  -d '{"model":"deepseek-v4-pro-cloud","messages":[{"role":"user","content":"Say OK"}],"max_tokens":10}' 2>&1 | tail -5

echo "== DONE =="
```

> 本块纯只读 curl，不改文件不动进程。每条 timeout 15，总超时小于120s。

---

## RUN_ID 21 — 🔍 只读：评测侧怎么调 cline + 把防作弊 hook 装到哪（为“评测对象也隔离 config dir”定位改动点）

**目标**（用户/运维）：让**合并线的评测对象**也用**独立配置目录**（hook 装到那里），使 `~/.cline` 保持干净 → **合并线与 legacy 彻底互不干扰**。本块**只读**定位：`run_cli.sh` / `run_cline_script.sh` 里 ① cline 的调用点；② hook 的安装/移除点；③ 是否已支持 `--config` / `CLINE_CONFIG_DIR`；④ 评测模型的 auth 在哪设。

```text
# RUN_ID 21 — read-only: eval-side cline invocation + hook install (for config-dir isolation)
GP=/nasdata/app.e0031982/code/eda_fastmcp
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. run_cli.sh: hook + cline + config refs =="
timeout 15 grep -nE 'seed_cline_hooks|cline/hooks|PreToolUse|--config|CLINE_CONFIG_DIR|--data-dir|--hooks-dir' "$GP/scripts/run_cli.sh" 2>/dev/null | head -40 | cut -c1-190
echo "== 2. run_cli.sh: cline invocation lines =="
timeout 15 grep -nE '(^|[^-])cline ' "$GP/scripts/run_cli.sh" 2>/dev/null | head -20 | cut -c1-190
echo "== 3. run_cline_script.sh: cline/config/hook refs =="
timeout 15 grep -nE 'cline|--config|CLINE_CONFIG_DIR|PreToolUse|hooks|run_cli\.sh' "$GP/scripts/run_cline_script.sh" 2>/dev/null | head -30 | cut -c1-190
echo "== 4. which scripts mention cline or PreToolUse =="
timeout 20 grep -rlnE '(^|[^-])cline |PreToolUse' "$GP/scripts" 2>/dev/null | head -20 | cut -c1-160
echo "== 5. eval auth / model refs =="
timeout 15 grep -nE 'cline auth|models\.json|providers\.json|openAiBaseUrl|MODEL=|CLINE_MODEL' "$GP/scripts/run_cli.sh" "$GP/scripts/run_cline_script.sh" 2>/dev/null | head -20 | cut -c1-190
echo "== DONE =="
```

> ⚠️ 本块**纯只读**（grep/sed），不改任何文件、不动任何进程。

---

## RUN_ID 20 — 🚑 补救：**把 legacy 组件 loop 拉回来**（若已停）；不要动合并线 loop

**背景**：运维失误（RUN_ID 18 把 legacy 的 `pkill` 与 `git pull` 放同一块）→ 中继可能卡住、legacy 可能已被停。**本轮唯一目标 = 让 legacy 回到运行态**（幂等：只在没跑时拉起）。用户在家、要 3 天后才能登机 → 这是"通道一恢复即自动复活"的保险。

> ⛔ **已作废**（已执行于 2026-10-05 11:04:10；legacy 本就活着）——降级为 text。

```text
# RUN_ID 20 — REVIVE legacy component loop (idempotent); leave merged loop alone
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027/run
LD="$D/ablation_run_loop_component_s2_full.sh"
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. legacy loop running? =="; timeout 10 pgrep -af 'ablation_run_loop_component_s2_full' | cut -c1-140; echo "(end)"
echo "== 2. start if absent =="
if ! pgrep -f ablation_run_loop_component_s2_full.sh >/dev/null 2>&1; then
  cd "$D"; setsid bash "$LD" > /tmp/ablation_loop_component_s2_full.log 2>&1 < /dev/null & sleep 4
  echo "   (re)started."
else echo "   already running, skip."; fi
echo "== 3. verify =="; timeout 10 pgrep -af 'ablation_run_loop_component_s2_full' | cut -c1-140; echo "(end2)"
echo "== 4. relay alive? =="; timeout 10 pgrep -af zhulong_ops_relay.sh | cut -c1-140
echo "== 5. merged loop (leave as-is) =="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140
echo "== DONE =="
```

> ⚠️ 本块**只复活 legacy**，**不重启合并线 loop、不停任何东西**。接管（停 legacy + 换新 loop）**暂缓**，等用户重新拍板。

---

## RUN_ID 19 — ♻️ 重试接管（**块内无任何 git 命令**！中继自己的 git_sync 已做 pull）

**背景**：RUN_ID 18 疑似**卡住中继**——块内 `git pull --rebase --autostash` 的网络子进程**继承了 stdout 管道**，`timeout` 只杀 leader → 中继读不到 EOF（**BaiZe §7 同型坑**）。本版**去掉所有 git 命令**（中继主循环的 `git_sync` 会自己 pull），只做幂等的「停 legacy + 重启 loop」。

> ⛔ **已作废**（被 RUN_ID 20 取代：暂缓接管、先复活 legacy）——降级为 text。

```text
# RUN_ID 19 — RETRY takeover (NO git commands in block)
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
LD="$REPO/doc/ZhuLong_DAC2027/run/zhulong_loop.sh"
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. legacy procs =="; timeout 10 pgrep -af 'ablation_run_loop|ablation_run_conductor' | cut -c1-150; echo "(end)"
echo "== 2. stop legacy (idempotent) =="; pkill -f ablation_run_loop_component_s2_full.sh; pkill -f ablation_run_conductor_serial.sh; sleep 3
timeout 10 pgrep -af 'ablation_run_loop|ablation_run_conductor' | cut -c1-150; echo "(end2)"
echo "== 3. loop script has --config count =="; timeout 10 grep -c 'CLINE_CONFIG_DIR' "$LD"
echo "== 4. restart merged loop =="; pkill -f zhulong_loop.sh; sleep 3; setsid bash "$LD" > /tmp/zhulong_loop.log 2>&1 < /dev/null & sleep 10
echo "== 5. loop proc + log =="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140; timeout 10 tail -n 10 /tmp/zhulong_loop.log | cut -c1-170
echo "== 6. relay alive =="; timeout 10 pgrep -af zhulong_ops_relay.sh | cut -c1-140
echo "== DONE =="
```

> ⚠️ **纪律（本次教训，已入 MEMORY）**：relay 块内**禁止 `git pull`/`git fetch`** —— 中继主循环的 `git_sync` 已负责同步；块内再 pull 会因网络子进程持有 stdout 而**卡死中继**。

---

## RUN_ID 18 — 🚀 执行接管：停 legacy 两进程 + pull + 重启合并线 loop（带隔离 `--config`）

**决策**：用户批准。停 `ablation_run_loop_component_s2_full.sh`（组件线）+ `ablation_run_conductor_serial.sh`（conductor）；合并线从 `C1.wo_retrieval R2` 续跑。隔离已验证（RUN_ID 17）。

> ⛔ **已作废**（块内含 `git pull`，疑似卡死中继）——降级为 text，让位给 RUN_ID 19。

```text
# RUN_ID 18 — TAKEOVER: stop legacy, pull, restart merged loop (isolated --config)
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
LD="$REPO/doc/ZhuLong_DAC2027/run/zhulong_loop.sh"
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. BEFORE procs =="; timeout 10 pgrep -af 'ablation_run_loop|ablation_run_conductor|zhulong_loop' | cut -c1-160
echo "== 2. stop legacy procs =="
pkill -f ablation_run_loop_component_s2_full.sh; pkill -f ablation_run_conductor_serial.sh; sleep 3
echo "== 3. verify legacy gone (expect empty) =="; timeout 10 pgrep -af 'ablation_run_loop|ablation_run_conductor' | cut -c1-160; echo "(end-legacy)"
echo "== 4. pull repo =="; timeout 90 git -C "$REPO" pull --rebase --autostash 2>&1 | tail -4 | cut -c1-160
echo "== 5. loop script has --config? =="; timeout 10 grep -n 'CLINE_CONFIG_DIR' "$LD" | cut -c1-160
echo "== 6. restart merged loop =="; pkill -f zhulong_loop.sh; sleep 3; setsid bash "$LD" > /tmp/zhulong_loop.log 2>&1 < /dev/null & sleep 12
echo "== 7. AFTER: loop proc + log tail =="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140; timeout 10 tail -n 12 /tmp/zhulong_loop.log | cut -c1-170
echo "== 8. relay alive =="; timeout 10 pgrep -af zhulong_ops_relay.sh | cut -c1-140
echo "== DONE =="
```

---

## RUN_ID 17 — 🧪 落地隔离 A（编排侧 `--config`）+ 验证（hooks 是否隔离 / 是否 env 泄漏）

**依据**：RUN_ID 16 实测 `cline --config <dir>` = 配置目录（默认 `~/.cline`），且 **hook 发现跟随 `--config`**（`<config-dir>/hooks`）；`--hooks-dir` 无效。**决策**：给合并线编排 agent 用 `--config /nasdata/app.e0031982/.cline_zhulong`。本块：建隔离目录 + 写入 auth + 用**可分辨 canary hook** 验证 ① 编排读的是 `<ISO>/hooks` 而非 `~/.cline/hooks`；② `--config` **不**把 `CLINE_*` 泄漏给子进程（否则会破坏评测对象的防作弊 hook）。

> ⛔ **已作废**（已执行于 22:49:52，隔离已验证）——降级为 text，让位给 RUN_ID 18。

```text
# RUN_ID 17 — build isolated --config dir + verify hooks/env (bounded)
K=02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23
BASE=http://agi-gateway.cxmt.com/cloud/v1
ISO=/nasdata/app.e0031982/.cline_zhulong
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. create isolated config dir + auth (--config) =="
mkdir -p "$ISO/hooks"
timeout 90 cline --config "$ISO" auth -p openai -k "$K" -b "$BASE" -m "glm-5.2" 2>&1 | tail -4 | cut -c1-170
echo "== 2. isolated dir layout =="; timeout 10 find "$ISO" -maxdepth 2 2>&1 | head -25 | cut -c1-150
echo "== 3. isolated auth present? =="; timeout 10 grep -rho '"openAiBaseUrl"[^,]*' "$ISO" 2>/dev/null | head -3
echo "== 4. install distinguishable canary hooks =="
rm -f ~/.cline/hooks/PreToolUse "$ISO/hooks/PreToolUse"
printf '#!/bin/bash\necho "DEFAULT_DIR_READ" >> /tmp/zhulong_hook_probe.log\nexit 0\n' > ~/.cline/hooks/PreToolUse; chmod +x ~/.cline/hooks/PreToolUse
printf '#!/bin/bash\necho "ISO_DIR_READ" >> /tmp/zhulong_hook_probe.log\nexit 0\n' > "$ISO/hooks/PreToolUse"; chmod +x "$ISO/hooks/PreToolUse"
rm -f /tmp/zhulong_hook_probe.log
echo "== 5. SMOKE: cline --config ISO, ask for printenv =="
cd /tmp
timeout 200 env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY -u OPENAI_API_KEY -u OPENAI_API_URL -u API_TYPE \
  cline --config "$ISO" -c /tmp --auto-approve true -m glm-5.2 -k "$K" -P openai-compatible -t 180 \
  "Run exactly one shell command and return its raw output: printenv | grep -iE 'CLINE|HOOK' ; echo END" < /dev/null 2>&1 | tail -22 | cut -c1-180
echo "== 6. probe (which hooks dir read) =="; timeout 10 cat /tmp/zhulong_hook_probe.log 2>&1 | head; echo "(end-probe)"
echo "== 7. cleanup canary =="; rm -f ~/.cline/hooks/PreToolUse "$ISO/hooks/PreToolUse"; timeout 10 ls -la ~/.cline/hooks/ | head -4 | cut -c1-140
echo "== DONE =="
```

---

## RUN_ID 16 — 🧪 隔离前置侦察：`--data-dir` 语义 + hook 安装点 + 要拷的配置

**决策（用户 22:4x）**：隔离走 **A（编排侧）**；停 legacy 两进程；合并线从 **`C1.wo_retrieval R2`** 续跑（复用 legacy 数据）。落地前先搞清：① `cline --data-dir` 改的是哪层（base=`~/.cline` 还是 data=`~/.cline/data`）；② hook 是**哪段脚本**拷进 `~/.cline/hooks` 的；③ 隔离目录要拷哪些配置（auth）。

> ⛔ **已作废**（已执行于 22:47:46）——降级为 text，让位给 RUN_ID 17。

```text
# RUN_ID 16 — prep for isolation (read-only)
GP=/nasdata/app.e0031982/code/eda_fastmcp
echo "== 0. TIME =="; timeout 10 date '+%F %T'
echo "== 1. cline --help (data/hook/config) =="; timeout 25 cline --help 2>&1 | grep -iE 'data|hook|dir|config|auth' | head -25 | cut -c1-160
echo "== 2. cline_hooks source dir =="; timeout 10 ls -la "$GP/scripts/cline_hooks/" 2>&1 | head -20 | cut -c1-160
echo "== 3. who installs ~/.cline/hooks =="; timeout 20 grep -rnE 'cline/hooks|hooks' "$GP/scripts" 2>/dev/null | head -25 | cut -c1-190
echo "== 4. ~/.cline/data contents (config to copy) =="; timeout 10 ls -la ~/.cline/data/ 2>&1 | head -22 | cut -c1-140
echo "== 5. --data-dir usage in our repo =="; timeout 20 grep -rnE -- '--data-dir' /nasdata/app.e0031982/code/super_intelligence_2035/doc 2>/dev/null | head -10 | cut -c1-190
echo "== 6. ~/.cline/data/settings =="; timeout 10 ls -la ~/.cline/data/settings/ 2>&1 | head -15 | cut -c1-140
echo "== DONE =="
```

---

## RUN_ID 15 — 🪝 确认防作弊 hook 落点 + 评测脚本是否设 `--data-dir`（定隔离方案）

**背景**：用户澄清"沙箱阻断"实为**防作弊 PreToolUse hook 污染**（hook 拷进 `~/.cline/hooks`，评测对象与编排 agent 共用 `~/.cline`）。本块**只读**确认：① hook 落在哪（`~/.cline/hooks`？`~/.cline/data/hooks`？）；② 评测脚本 `run_cline_script.sh` 是否给评测对象设了 `--data-dir`（决定隔离放"编排侧"还是"评测侧"）；③ 是否有现成的隔离目录可照抄。

> ⛔ **已作废**（已执行于 22:41:33）——降级为 text，让位给 RUN_ID 16。

```text
# RUN_ID 15 — locate anti-cheat hook + how eval sets cline config (read-only)
GP=/nasdata/app.e0031982/code/eda_fastmcp
echo "== 0. TIME =="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "== 1. ~/.cline top + hooks dirs =="; timeout 10 ls -la ~/.cline/ 2>&1 | head -18 | cut -c1-150
echo "-- ~/.cline/hooks --"; timeout 10 ls -la ~/.cline/hooks/ 2>&1 | head -12 | cut -c1-150
echo "-- ~/.cline/data/hooks --"; timeout 10 ls -la ~/.cline/data/hooks/ 2>&1 | head -12 | cut -c1-150
echo "== 2. run_cline_script: hook / data-dir / .cline refs =="; timeout 15 grep -nE 'hook|Hook|--data-dir|data-dir|data_dir|CLINE_|\\.cline' "$GP/scripts/run_cline_script.sh" 2>/dev/null | head -30 | cut -c1-190
echo "== 3. hook files on disk (eda_fastmcp) =="; timeout 15 find "$GP" -maxdepth 3 -iname '*hook*' 2>/dev/null | head -20 | cut -c1-160
echo "== 4. isolate dirs that already exist =="; timeout 10 ls -ld /nasdata/app.e0031982/.cline_data /nas_train/app.e0031982/.cline_data /home/app.e0031982/.cline_eval 2>&1 | cut -c1-150
echo "== DONE =="
```

---

## RUN_ID 14 — 🧭 接管尽调：legacy 两进程是否还在动？当前臂？我方合并线状态？

**背景**：接管前最后确认——① legacy conductor（PID 1381975，已 3.3 天）与组件 loop（2455466）是否还在有效推进；② 评测 infra（MCP/eval）当前占用；③ 当前 `.env` 臂；④ 我方合并线 agent 现状。**只读**。

> ⛔ **已作废**（已执行于 22:20:02）——降级为 text，让位给 RUN_ID 15。

```text
# RUN_ID 14 — takeover due diligence (read-only)
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027/run
M=/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run
echo "== 0. TIME =="; timeout 10 date '+%F %T'
echo "== 1. legacy conductor log tail =="; timeout 10 tail -n 15 /tmp/ablation_conductor.log 2>&1 | cut -c1-160
echo "== 2. legacy component loop log tail =="; timeout 10 tail -n 15 /tmp/ablation_loop_component_s2_full.log 2>&1 | cut -c1-160
echo "== 3. zhulong-related procs =="; timeout 10 pgrep -af 'ZhuLong_DAC2027' | head -20 | cut -c1-160
echo "== 4. eda_fastmcp .env key arm lines =="; timeout 10 grep -nE 'EDA_MCP_TOOLS_DISABLED|EDA_OMEGA_FIDELITY|EDA_RUNCODE_READBACK|EDA_PHI_BUDGET|EDA_PHI_LAGGED|RAG_RECALL_URL' /nasdata/app.e0031982/code/eda_fastmcp/.env 2>/dev/null | cut -c1-200
echo "== 5. MCP / eval infra procs =="; timeout 10 pgrep -af 'eda_fastmcp|run_cline_script|8090' | head -15 | cut -c1-160
echo "== 6. our merged line: procs + WAITING =="; timeout 10 pgrep -af 'zhulong_loop|zhulong_ops_relay|-m glm-5.2' | head -10 | cut -c1-150; timeout 10 sed -n '1,3p' "$M/MEMORY_ZHULONG.md" 2>&1
echo "== 7. our merged agent daily-memory tail =="; timeout 10 tail -n 8 "$M/daily-memories/2026-10-04.md" 2>&1 | cut -c1-160
echo "== DONE =="
```

---

## RUN_ID 13 — 📊 legacy 线：已完成的实测成绩 + conductor + 产出批次（接管清点）

**背景**：为接管清点——查明 legacy 线**到底已跑出哪些有效成绩**、另一进程 `ablation_run_conductor_serial.sh` 是干嘛的、以及评测产出批次。**只读**。

> ⛔ **已作废**（已执行于 22:17:55）——降级为 text，让位给 RUN_ID 14。

```text
# RUN_ID 13 — legacy line: exact completed results + conductor + outputs (read-only)
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027/run
echo "== 0. TIME =="; timeout 10 date '+%F %T'
echo "== 1. legacy MEMORY score/dashboard/PHASE =="; timeout 10 grep -nE 'mean|±|pure_llm|rag|wo_retrieval|phi_|done_all|PHASE|CONFIG' "$D/MEMORY_component_full.md" | head -45 | cut -c1-200
echo "== 2. conductor script head =="; timeout 10 sed -n '1,28p' "$D/ablation_run_conductor_serial.sh" 2>&1 | cut -c1-180
echo "== 3. conductor proc args =="; timeout 10 ps -o pid=,ppid=,etimes=,args= -p 1381975 2>&1 | cut -c1-200
echo "== 4. eval output batches =="; timeout 25 ls -lt /nasdata/app.e0031982/eda_code_eval 2>/dev/null | head -25 | cut -c1-140
echo "== 5. wo_retrieval r1 final result =="; timeout 10 grep -E 'pass \(|Pass@1|评估完成' /tmp/ABL_wo_retrieval_r1.log 2>/dev/null | tail -6 | cut -c1-180
echo "== 6. old one-shot r1 results =="; for f in ABL_full_r1 ABL_k10_r1 ABL_k3_r1 ABL_k1_r1 ABL_lagged_r1 ABL_lagged_r2 ABL_omega_low_r1 ABL_omega_low_r2; do printf '%-20s ' "$f"; timeout 8 grep -oE '[0-9]+/158 pass \([0-9.]+%\)' "/tmp/$f.log" 2>/dev/null | tail -1; echo; done
echo "== DONE =="
```

---

## RUN_ID 12 — 🧩 legacy 组件线 loop 内部 + 实时进度（为接管做底）

**背景**：RUN_ID 10/11 查明「另一个 agent」= **legacy 组件线**（`ablation_run_loop_component_s2_full.sh`，跑在**非 git** 独立副本 `/nasdata/app.e0031982/code/ZhuLong_DAC2027`），其日报显示**连续 ≥4 周期被 agent 沙箱阻断**（`run_commands`→ACCESS RESTRICTED）。本块读它的 **loop 全脚本 + 进程 + r1 日志 + MEMORY 现状**。

> ⛔ **已作废**（已执行于 22:16:50）——降级为 text，让位给 RUN_ID 13。

```text
# RUN_ID 12 — legacy component loop internals + live progress (read-only)
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027/run
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'
echo "===== 1. component loop script (FULL) ====="; timeout 10 cat "$D/ablation_run_loop_component_s2_full.sh" 2>&1 | cut -c1-200
echo "===== 2. related live procs ====="; timeout 10 pgrep -af 'ablation_run_loop|run_cline_script|ablation_run_conductor' | head -20 | cut -c1-160
echo "===== 3. eval PID 692552 alive? ====="; timeout 10 ps -o pid=,ppid=,etimes=,args= -p 692552 2>&1 | cut -c1-160
echo "===== 4. wo_retrieval r1 log tail ====="; timeout 10 tail -n 18 /tmp/ABL_wo_retrieval_r1.log 2>&1 | cut -c1-180
echo "===== 5. MEMORY_component_full.md status head ====="; timeout 10 sed -n '1,20p' "$D/MEMORY_component_full.md" 2>&1 | cut -c1-200
echo "===== 6. MEMORY_component_full.md operation-log tail ====="; timeout 10 tail -n 24 "$D/MEMORY_component_full.md" 2>&1 | cut -c1-200
echo "===== 7. /tmp ABL + loop logs ====="; timeout 10 ls -la /tmp/ABL_*.log /tmp/*loop*.log 2>&1 | head -20 | cut -c1-160
echo "===== DONE ====="
```

---

## RUN_ID 11 — 📖 读「另一个 agent」（legacy 组件线）的任务书 / MEMORY / 日报 / loop

**背景**：RUN_ID 10 查明「另一个 agent」= **legacy 组件线**，进程 `2455466 bash …/code/ZhuLong_DAC2027/run/ablation_run_loop_component_s2_full.sh`，跑在**独立（非 git）项目副本** `/nasdata/app.e0031982/code/ZhuLong_DAC2027/` 里。本块**只读**读它的 4 份关键文件，理解其工作与进度，为接管做准备。

> ⛔ **已作废**（已执行于 22:15:45）——降级为 text，让位给 RUN_ID 12。

```text
# RUN_ID 11 — read the OTHER (legacy component) agent's docs & loop
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027/run
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'
echo "===== 1. ls run/ ====="; timeout 15 ls -la "$D" 2>&1 | head -40 | cut -c1-160
echo "===== 2. component loop script (head 45) ====="; timeout 10 sed -n '1,45p' "$D/ablation_run_loop_component_s2_full.sh" 2>&1 | cut -c1-180
echo "===== 3. MEMORY_component_full.md (head 55) ====="; timeout 10 sed -n '1,55p' "$D/MEMORY_component_full.md" 2>&1 | cut -c1-200
echo "===== 4. daily-memories/2026-10-04.md (tail 55) ====="; timeout 10 tail -n 55 "$D/daily-memories/2026-10-04.md" 2>&1 | cut -c1-200
echo "===== 5. taskbook (head 70) ====="; timeout 10 sed -n '1,70p' "$D/ablation_run_task_component_s2_full.md" 2>&1 | cut -c1-200
echo "===== DONE ====="
```

---

## RUN_ID 10 — 🔎 只读侦察：另一个 agent 的目录 `/nasdata/app.e0031982/code/ZhuLong_DAC2027`

**背景**：用户告知**另有一个 agent 在跑任务**，地址 `=` `/nasdata/app.e0031982/code/ZhuLong_DAC2027`（**不是**本合并线所在的 `super_intelligence_2035/doc/ZhuLong_DAC2027`）。目标：**观摩 & 理解它的工作，为接管做准备**。本块**只读**：目录结构、是否 git 仓库、进程、最近改动、文档/脚本清单。

> ⛔ **已作废**（已执行于 22:13:39）——降级为 text，让位给 RUN_ID 11。

```text
# RUN_ID 10 — read-only recon of the OTHER agent dir
D=/nasdata/app.e0031982/code/ZhuLong_DAC2027
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== 1. exists? ====="; timeout 10 ls -ld "$D" 2>&1 | cut -c1-160
echo "===== 2. top-level listing ====="; timeout 15 ls -la "$D" 2>&1 | head -40 | cut -c1-160
echo "===== 3. is it a git repo? ====="
timeout 15 git -C "$D" rev-parse --show-toplevel 2>&1 | head -1 | cut -c1-160
timeout 15 git -C "$D" log --oneline -8 2>&1 | cut -c1-160
timeout 15 git -C "$D" status -sb 2>&1 | head -12 | cut -c1-160
echo "===== 4. processes referencing ZhuLong_DAC2027 ====="; timeout 10 pgrep -af 'ZhuLong_DAC2027' | head -20 | cut -c1-160
echo "===== 5. dirs (maxdepth 2) ====="; timeout 20 find "$D" -maxdepth 2 -type d 2>/dev/null | head -40 | cut -c1-160
echo "===== 6. recently modified files (<24h, maxdepth 3) ====="; timeout 25 find "$D" -maxdepth 3 -type f -mmin -1440 2>/dev/null | head -40 | cut -c1-160
echo "===== 7. md / sh files at top ====="; timeout 15 ls -la "$D"/*.md "$D"/*.sh 2>/dev/null | head -30 | cut -c1-160
echo "===== DONE ====="
```

---

## RUN_ID 9 — 🟢 唤醒后快照：agent 首轮在做什么？

**背景**：RUN_ID 8 已把 `openAiBaseUrl` 修成 `/cloud/v1` 并重启 loop，**agent 首次被唤醒**（loop 日志出现真实推理）。本块**只读**快照：loop/cline 进程、loop 日志、`MEMORY_ZHULONG.md` 现状、`run/` 最新文件、agent 日报、git 状态。

> ⛔ **已作废**（已执行于 21:56:15）——降级为 text，让位给 RUN_ID 10。

```text
# RUN_ID 9 — post-wake snapshot (read-only)
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
CWD="$REPO/doc/ZhuLong_DAC2027/run"
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'
echo "===== 1. procs (loop + cline) ====="; timeout 10 pgrep -af 'zhulong_loop.sh|cline ' | cut -c1-140
echo "===== 2. loop log tail (last 30) ====="; timeout 10 tail -n 30 /tmp/zhulong_loop.log | cut -c1-160
echo "===== 3. MEMORY_ZHULONG (mtime + head) ====="; timeout 10 ls -la "$CWD/MEMORY_ZHULONG.md"; timeout 10 sed -n '1,5p' "$CWD/MEMORY_ZHULONG.md"
echo "===== 4. newest files in run/ ====="; timeout 10 ls -lat "$CWD" | head -12
echo "===== 5. agent daily-memory tail ====="; timeout 10 tail -n 15 "$CWD/daily-memories/2026-10-04.md" 2>/dev/null | cut -c1-160
echo "===== 6. repo git status / log ====="; timeout 20 git -C "$REPO" status -sb | head -8; timeout 20 git -C "$REPO" log --oneline -3
echo "===== DONE ====="
```

---

## RUN_ID 8 — 🔑 修 `error: Forbidden`：给 glm-5.2 写 cline 的 base URL（`cline auth`）+ 重启 loop

**根因（RUN_ID 7 + 对照 BaiZe 可用 loop）**：新 loop 已能调用 cline，但报 `error: Forbidden`；而 `curl -H "Authorization: Bearer <key>" http://agi-gateway.cxmt.com/cloud/v1/models` = **HTTP 200**（key 有效、网关可达）。`~/.cline` 下**查不到 settings/globalState 的 base URL 配置** → cline 只拿到 `-k/-P`、**不知道网关地址** → 打到默认端点被 `Forbidden`。BaiZe 的可用 loop 之所以正常，是因为其 cline 配置里 `openAiBaseUrl=agi-gateway …/cloud/v1`（见 `baize_data_loop.sh` §27–46：**base 必须与模型匹配**，glm-5.2 → `/cloud/v1`）。仓库文档给出的正确写法 = **`cline auth -p openai -k <key> -b <base> -m <model>`**（`ablation_run_task_model_full.md`）。

> ⛔ **已作废**（已执行于 21:53:51，base url 已修、agent 已唤醒）——降级为 text，让位给 RUN_ID 9。

```text
# RUN_ID 8 — set cline base URL for glm-5.2 (fix Forbidden), then restart loop
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
LD="$REPO/doc/ZhuLong_DAC2027/run/zhulong_loop.sh"
K=02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23
BASE=http://agi-gateway.cxmt.com/cloud/v1
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== 1. current cline config ====="; timeout 15 ls -la ~/.cline/data/ 2>/dev/null | head -20
echo "   openAiBaseUrl now:"; timeout 10 grep -o '"openAiBaseUrl"[^,]*' ~/.cline/data/globalState.json 2>/dev/null | head -2
echo "===== 2. cline auth (write glm-5.2 base url) ====="
timeout 60 cline auth -p openai -k "$K" -b "$BASE" -m "glm-5.2" 2>&1 | tail -6 | cut -c1-160
echo "===== 3. after: openAiBaseUrl ====="; timeout 10 grep -o '"openAiBaseUrl"[^,]*' ~/.cline/data/globalState.json 2>/dev/null | head -2
echo "===== 4. restart loop ====="; pkill -f zhulong_loop.sh; sleep 3; setsid bash "$LD" > /tmp/zhulong_loop.log 2>&1 < /dev/null & sleep 12
echo "===== 5. loop log tail (Forbidden gone?) ====="; timeout 10 tail -n 12 /tmp/zhulong_loop.log | cut -c1-160
echo "===== 6. loop proc ====="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140
echo "===== DONE ====="
```

---

## RUN_ID 7 — 🩺 诊断 loop 的 `error: Forbidden`（agent 仍未被唤醒的**真正根因**）

**背景**：RUN_ID 6 重启 loop 成功（非法 `-b` 已消除、脚本第 112 行确认为 `-P openai-compatible`），但**新 loop 每周期报 `error: Forbidden`**（cline 调用被网关拒绝）→ agent 仍无法唤醒。本块**只读**采集：① loop 日志近况；② cline 用的完整命令行；③ proxy / OPENAI 环境；④ `~/.cline` 里的 base URL / provider 配置；⑤ 直接 `curl` 网关确认 key 是否有效。

> ⛔ **已作废**（已执行于 21:46:39）——降级为 text，让位给 RUN_ID 8。

```text
# RUN_ID 7 — diagnose "error: Forbidden" (read-only, no agent call)
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
CWD="$REPO/doc/ZhuLong_DAC2027/run"
K="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== 1. loop log tail (last 16) ====="; timeout 10 tail -n 16 /tmp/zhulong_loop.log | cut -c1-160
echo "===== 2. script cline line (104-113) ====="; timeout 10 sed -n '104,113p' "$CWD/zhulong_loop.sh" | cut -c1-160
echo "===== 3. proxy / OPENAI env ====="; env | grep -iE 'proxy|OPENAI|API_TYPE' | cut -c1-140
echo "===== 4. cline settings files ====="; timeout 20 find ~/.cline -maxdepth 3 -name 'settings*' 2>/dev/null | head
for f in $(timeout 20 find ~/.cline -maxdepth 3 -name 'settings*' 2>/dev/null); do echo "-- $f --"; timeout 10 grep -iE 'url|baseurl|base_url|provider|"model"' "$f" | head -20 | cut -c1-160; done
echo "===== 5. cline version ====="; timeout 20 cline --version 2>&1 | head -3
echo "===== 6. curl gateway /models (WITH current env) ====="; timeout 20 curl -sS -m 15 -o /dev/null -w "HTTP=%{http_code}\n" -H "Authorization: Bearer $K" "http://agi-gateway.cxmt.com/cloud/v1/models" 2>&1 | cut -c1-160
echo "===== 7. curl gateway /models (WITHOUT proxy) ====="; timeout 20 env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u all_proxy -u ALL_PROXY -u ftp_proxy -u FTP_PROXY curl -sS -m 15 -o /dev/null -w "HTTP=%{http_code}\n" -H "Authorization: Bearer $K" "http://agi-gateway.cxmt.com/cloud/v1/models" 2>&1 | cut -c1-160
echo "===== DONE ====="
```

---

## RUN_ID 6 — 🔧 重启 `zhulong_loop.sh`（清掉旧版 `-b`，让 agent 真正被唤醒）——**本次首要**

**背景**：RUN_ID 5（21:43:20）实测 —— 中继健康（RUN_ID 1–5 全 `exit=0`）；但 **loop 仍是旧版**，`/tmp/zhulong_loop.log` 每次唤醒都 `error: unknown option '-b'`（累计 **352** 次），**cline 从未运行 → agent 从未被唤醒**。磁盘脚本已是新版（无 `-b`）→ **重启进程即修复**。本块：先确认脚本已新，再 `pkill` + `setsid` 重启 loop，最后复核进程与日志。

> ⛔ **已作废**（已执行于 21:45:27，loop 已重启）——降级为 text，让位给 RUN_ID 7。

```text
# RUN_ID 6 — restart zhulong_loop to clear stale -b (agent never woke)
REPO=/nasdata/app.e0031982/code/super_intelligence_2035
LD="$REPO/doc/ZhuLong_DAC2027/run/zhulong_loop.sh"
echo "===== 0. TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== 1. before: loop proc ====="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140
echo "===== 2. loop script line112 (should be -P openai-compatible, NO -b) ====="; timeout 10 sed -n '112p' "$LD" | cut -c1-160
echo "===== 3. restart loop ====="
pkill -f zhulong_loop.sh; sleep 3
setsid bash "$LD" > /tmp/zhulong_loop.log 2>&1 < /dev/null &
sleep 4
echo "===== 4. after: loop proc ====="; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140
echo "===== 5. loop log tail ====="; timeout 10 tail -n 8 /tmp/zhulong_loop.log | cut -c1-160
echo "===== 6. relay still alive ====="; timeout 10 pgrep -af zhulong_ops_relay.sh | cut -c1-140
echo "===== DONE ====="
```

---

## RUN_ID 5 — 🩺 只读健康探针：中继 / loop 是否活着（**本次首要**）

**背景**：RUN_ID 4（heavy）已由中继于 **17:05:57 成功执行并回推**（`.last_run_id=4`）→ 中继看似已恢复。本块**只读**确认三件事：① `zhulong_ops_relay.sh` / `zhulong_loop.sh` 进程是否在；② loop 是否仍在报非法 `-b`（静默失效，见 MEMORY §7-10）；③ loop 日志里 `cline returned` 计数（判断 agent 是否真被唤醒）。**全部命令带 `timeout`、不跟 symlink。**

> ⛔ **已作废**（已执行于 21:43:20）——降级为 text，让位给 RUN_ID 6。

```text
# RUN_ID 5 — read-only relay/loop health probe
echo "===== TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== 1. processes ====="
echo "-- relay --"; timeout 10 pgrep -af zhulong_ops_relay.sh | cut -c1-140
echo "-- loop  --"; timeout 10 pgrep -af zhulong_loop.sh | cut -c1-140
echo "===== 2. relay log tail ====="; timeout 10 tail -n 8 /tmp/zhulong_ops_relay.log 2>/dev/null | cut -c1-140
echo "===== 3. loop log tail =====";  timeout 10 tail -n 14 /tmp/zhulong_loop.log 2>/dev/null | cut -c1-140
echo "===== 4. loop log health counts ====="
echo -n "unknown option -b : "; timeout 20 grep -c "unknown option '-b'" /tmp/zhulong_loop.log 2>/dev/null
echo -n "Forbidden         : "; timeout 20 grep -c "Forbidden"                /tmp/zhulong_loop.log 2>/dev/null
echo -n "cline returned    : "; timeout 20 grep -c "cline returned"          /tmp/zhulong_loop.log 2>/dev/null
echo "===== 5. /home =====";  timeout 15 df -BG /home | tail -1
echo "===== 6. MEMORY_ZHULONG WAITING (line1) ====="; timeout 10 grep -m1 "^WAITING" /nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/MEMORY_ZHULONG.md
echo "===== DONE ====="
```

---

## RUN_ID 4（**轻量重发**）— 确认 home symlink（**全部命令带 timeout、不跟 symlink**）

**背景**：首版 RUN_ID 4 用 `du -sh -L` + 未 `timeout` 的 `df` → **疑似卡死中继**（见 MEMORY §7 教训）。本版每条命令都 `timeout` 包裹、不跟随 symlink。

> ⛔ **本块已作废**（中继已用 heavy 版于 17:05:57 成功执行）——降级为 text，让位给 RUN_ID 5。

```text
# RUN_ID 4 (light) — 每条命令带 timeout；不用 du -L
H="/home/app.e0031982"
echo "===== TIME ====="; timeout 10 date '+%F %T'; timeout 10 hostname
echo "===== /home ====="; timeout 15 df -BG /home | tail -1
echo "===== ls -la HOME（看 symlink '->'）====="; timeout 15 ls -la "$H" 2>/dev/null | cut -c1-170
echo "===== realpath（不调 df）====="
for d in .cache .cline .npm .local .bun .vscode-server eda_code_eval; do
  p="$H/$d"
  if [ -e "$p" ] || [ -L "$p" ]; then printf "%-16s -> %s\n" "$d" "$(timeout 8 readlink -f "$p" 2>/dev/null)"; fi
done
echo "===== HOME 同文件系统体积（du -x，不跟 symlink）====="; timeout 30 du -x -sh "$H" 2>/dev/null
echo "===== eda_code_eval 目录类型 ====="; timeout 10 ls -ld "$H/eda_code_eval" 2>/dev/null | cut -c1-170
echo "===== /home top15（du -x）====="; timeout 40 du -x -d1 -h /home 2>/dev/null | sort -h | tail -15
echo "===== DONE ====="
```

> ⛔ 下方为 heavy 版（**已作废**，触发了卡死）。

---

## RUN_ID 4 — 🔎 确认「我方 home 是否真有可回收空间」（heavy · 已作废）

**背景**：RUN_ID 3 显示 `/home/app.e0031982` 同文件系统仅 **3.8M**、各缓存目录 `du -x` 报 **0** → 疑似**符号链接到 `/nasdata`**（`du` 默认不跟随 symlink）。本块确认并定位评测写入路径。

```text
# RUN_ID 4 (heavy DISABLED) — 只读
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

> ⛔ RUN_ID 3 已降级为 ```text（见下）。

---

## RUN_ID 3 — 🧹 只读盘点 `/home/app.e0031982`（历史，已执行）

**目标**：找出我们自己 home 里可安全回收的缓存/产物，判断能否把 `/home` 从 6G 解放到 ≥8G。**只读，不删任何东西。**

```text
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

> ⛔ RUN_ID 2 已降级为 ```text（见下）。

---

## RUN_ID 2 — 🩺 36.15 聚焦诊断（历史，已执行）

**目标**：为「清 `/home` + 重启 loop + 定起始点」提供判据。**只读**。

```text
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

> ⛔ RUN_ID 1 已降级为 ```text（见下）。

---

## RUN_ID 1 — 🔍 **ZhuLong 环境摸底（历史，已执行）**


**目标**：确认 ZhuLong 评测所需基础设施就绪，作为运维解除冻结令的前置检查。

```text
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

> ⛔ *历史命令往后追加，RUN_ID +1 后把旧块降级为 ```text。*
