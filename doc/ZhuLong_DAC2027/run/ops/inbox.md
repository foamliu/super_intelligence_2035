# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 4 -->

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

## RUN_ID 4（**轻量重发**）— 确认 home symlink（**全部命令带 timeout、不跟 symlink**）

**背景**：首版 RUN_ID 4 用 `du -sh -L` + 未 `timeout` 的 `df` → **疑似卡死中继**（见 MEMORY §7 教训）。本版每条命令都 `timeout` 包裹、不跟随 symlink。

```bash
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
