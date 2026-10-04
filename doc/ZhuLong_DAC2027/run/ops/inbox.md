# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 0 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`zhulong_ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> 危险模式会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **两条纪律**（跟随 BaiZe ops 的教训）：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② **绝不整树 `du`** —— `/nas_train` 有 175 TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`（每条带 `timeout`）**。
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

## RUN_ID 1 — 🔍 **ZhuLong 环境摸底（磁盘 / EDA 端口 / license / 进程 / git）**

**目标**：确认 ZhuLong 评测所需基础设施就绪，作为运维解除冻结令的前置检查。

```bash
echo "=========== 0. HOST/TIME ==========="; hostname; date '+%F %T'; id
echo
echo "=========== 1. DISK (关键路径 + /home) ==========="
echo "-- /home --"; df -BG /home 2>/dev/null | tail -1
echo "-- /nas_train --"; df -BG /nas_train 2>/dev/null | tail -1
echo "-- /tmp --"; df -BG /tmp 2>/dev/null | tail -1
echo "-- /nas_inference --"; df -BG /nas_inference 2>/dev/null | tail -1
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
CODE_BASE=/nas_train/app.e0031982/code/eda_fastmcp
if [ -d "$CODE_BASE" ]; then
  echo "   eda_fastmcp 目录存在: $CODE_BASE"
  ls -1 "$CODE_BASE" 2>/dev/null | head -10 | sed 's/^/     /'
  if [ -f "$CODE_BASE/run_code" ]; then
    echo "   run_code 文件存在"
  elif [ -f "$CODE_BASE/run_code.sh" ]; then
    echo "   run_code.sh 文件存在"
  else
    echo "   ⚠️ run_code 未找到，检查实际入口"
    ls -1 "$CODE_BASE"/*run* 2>/dev/null | sed 's/^/     /' || echo "   ❌ 无 run_code 入口"
  fi
else
  echo "   ❌ eda_fastmcp 目录不存在！"
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
echo "=========== 5. GIT STATUS ==========="
cd /nas_train/app.e0031982/code/super_intelligence_2035 && git status -sb | head -8
echo "-- last 3 commits --"
git log --oneline -3
echo
echo "=========== 6. ZHULONG RUN DIR ==========="
ls -la /nas_train/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/run/ 2>/dev/null | head -25
echo
echo "=========== 7. CPU / MEM / GPU ==========="
lscpu 2>/dev/null | grep -E '^Model name|^CPU\\(s\\):|^Socket' || true
free -g 2>/dev/null | head -2
nvidia-smi --query-gpu=index,name,utilization.gpu,memory.used,memory.total --format=csv,noheader 2>/dev/null | head -2 || echo "   (nvidia-smi not available)"
echo
echo "=========== DONE ==========="
```

> ⛔ *历史命令往后追加，RUN_ID +1 后把旧块降级为 ```text。*
