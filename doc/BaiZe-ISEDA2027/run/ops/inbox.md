# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 10 -->

> **用法**：把命令写进下面的 ```bash 块 → 把 `RUN_ID` 加 1 → `git push`。
> 中继（`ops_relay.sh`）轮询到 `RUN_ID` 增大后执行，结果追加到 `ops/outbox.md`（只增不改）。
> 危险模式会被拦截；单块总超时 600s，超长输出截断 20000 字符。
>
> ⚠️ **两条纪律**（前两批的教训）：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② **绝不整树 `du`** —— `/nas_train` 有 175 TB，全量 `du` 会跑几小时。**只用 `df` + 有界定向 `du`（每条带 `timeout`）**。
>
> ## 🚨🚨 **中继的真实行为（2026-10-02 实测，务必遵守）**
> `ops_relay.sh:46` 的 `inbox_cmd_block()` 是：
> ```bash
> awk '/^```bash/{f=1;next} /^```/{if(f){exit}} f' "$INBOX"
> ```
> **→ 它只执行文件里<u>第一个</u> ```bash 块**，后面的块**永远不会被执行**。
>
> **我们已因此踩了一次坑**：RUN_ID 从 3 加到 4 时，中继**又把 RUN_ID 3 的磁盘勘察跑了一遍**，
> 新写的命令被静默忽略（outbox 里 RUN_ID 4 记录的命令文本就是 RUN_ID 3 的）。
>
> ### ✅ 下发新命令的铁律
> 1. **把要执行的块放在文件的<u>最前面</u>**（任何 `## RUN_ID N` 标题之前的位置无所谓，关键是**第一个 ```bash**）。
> 2. **把旧块降级为 ```text**（或删掉）—— 否则它一直霸占"第一个块"。
> 3. **每次 `RUN_ID` 都要 +1**（中继靠"变大"触发）。
>
> > 🔧 **根治方案（待中继重启时再改，勿改运行中的脚本）**：
> > 把 `inbox_cmd_block()` 改成按最新 RUN_ID 取块，例如
> > `awk -v rid="$rid" '/^## RUN_ID /{cur=$3} /^```bash/{if(cur==rid){f=1;next}} /^```/{if(f)exit} f' "$INBOX"`。

---

## RUN_ID 10 — 🔍 **定位 `Forbidden` 根因**（**纯只读，不写任何东西**）（**本块为最新，优先执行**）

**RUN_ID 9 已定位（2026-10-04 07:13）**：
- ✅ 两条 `.29` loop **进程都活着**（`baize_pretrain_loop.sh` / `baize_harness_loop.sh`）
- ✅ **P-5b 已于 10-04 01:37 跑完**（`successfully saved checkpoint from iteration 4771`）→ **8 卡全空闲（0% / 0 MiB）已 ~5.6h**
- 🔴 **根因候选**：`/tmp/baize_*_loop.log` 每个 30min 周期都是 **`error: Forbidden`**，而 **`cline returned (exit 0)`** → loop 分辨不出失败 → **静默空转 ~9h**。**不是 token 额度，是 `Forbidden`（鉴权 / 模型名 / 网关）**
- ✅ `.12` 正常（vision/data loop 活着且干活）→ **问题只在 `.29`**

**本块目标**：判定 `Forbidden` 属于哪一种，并验证 `-k $OPENAI_API_KEY` 能否修好：
① **key 不对**（`~/.cline/data/secrets.json` 里的 stale key）② **模型名不对**（`MODEL=` 变量已失效）③ **网关/base-url 不对**（cline 没用内网网关）。

🚫 **纯只读** —— 不 kill / 不重启 / **不写任何文件**；smoke 测试只往 `/tmp` 落地（可接受）。

```bash
echo "=== 0. HOST / TIME / CLINE ==="; hostname; date '+%F %T %Z'
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
CLINE=$(command -v cline 2>/dev/null || echo "$HOME/.bun/bin/cline"); echo "CLINE=$CLINE"

echo; echo "=== 1. 两条 loop 的 cline 调用行 + 关键变量 ==="
for f in baize_pretrain_loop.sh baize_harness_loop.sh; do
  echo "-- $f"; grep -nE 'cline |^MODEL=|^CLINE_TIMEOUT=|^SLEEP_|^PUSH_' "$RUN/$f" 2>/dev/null | cut -c1-190
done

echo; echo "=== 2. Forbidden 时间线（总数 / 首次 / 最近）+ 最后一次正常周期 ==="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log; do
  echo "-- $f : Forbidden 总数=$(grep -c 'Forbidden' "$f" 2>/dev/null)"
  grep -n 'Forbidden' "$f" 2>/dev/null | head -1 | cut -c1-120
done
grep -nE 'Forbidden|wake up|push OK|nothing to commit' /tmp/baize_pretrain_loop.log 2>/dev/null | tail -14 | cut -c1-130

echo; echo "=== 3. secrets.json（脱敏）==="
python3 -c "import json,pathlib;p=pathlib.Path.home()/'.cline/data/secrets.json';print('exists',p.exists(),'mtime',__import__('datetime').datetime.fromtimestamp(p.stat().st_mtime).isoformat() if p.exists() else '');d=json.loads(p.read_text()) if p.exists() else {};[print(' ',k,'=',(str(v)[:6]+'...len'+str(len(str(v)))) if any(t in k.lower() for t in ('key','token','secret')) else v) for k,v in d.items()]" 2>&1 | cut -c1-200

echo; echo "=== 4. 环境变量凭据（脱敏：只看名字/length/前 8 位）==="
python3 -c "import os;[print(' ',k,'len',len(v),'prefix',v[:8]) for k,v in sorted(os.environ.items()) if any(t in k.upper() for t in ('KEY','TOKEN','API','PROXY'))]" 2>&1 | cut -c1-160

echo; echo "=== 5. cline smoke ——【不带 -k】（复现 loop 的失败）==="
cd /tmp && timeout 150 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 --auto-approve true -t 60 "reply with exactly OK" 2>&1 | tail -6 | cut -c1-170

echo; echo "=== 6. cline smoke ——【带 -k \$OPENAI_API_KEY】==="
cd /tmp && timeout 150 "$CLINE" -c /tmp -m deepseek-v4-pro-fp4 -k "$OPENAI_API_KEY" --auto-approve true -t 60 "reply with exactly OK" 2>&1 | tail -6 | cut -c1-170

echo; echo "=== 7. 对照：.12 用的是哪个 MODEL（为什么它没 Forbidden）==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'grep -nE "^MODEL=|cline " /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_vision_loop.sh | cut -c1-190; echo "-- .12 secrets --"; python3 -c "import json,pathlib;p=pathlib.Path.home()/\".cline/data/secrets.json\";d=json.loads(p.read_text()) if p.exists() else {};[print(k,len(str(v)),str(v)[:6]) for k,v in d.items() if \"key\" in k.lower()]"' 2>&1 | cut -c1-170 || echo "ssh .12 FAILED"

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 9**（`.29` 静默探查，**✅ 已执行 07:13:17 exit=0**）为 ```text —— 它不再霸占「第一个块」。

## RUN_ID 9 — 🔍 **只读探查：`.29` 的 pretrain / harness 为何静默 ~9 小时**（✅ 已执行，本块不再运行）

**背景**：`MEMORY_PRETRAIN_2B.md` 最后更新停在 **10-03 22:05**（第 54 次巡检，P-5b **90.97%**，final ETA 10-04 ~01:36）；`MEMORY_HARNESS.md` 停在 **10-03 22:43**。
**10-04 全天只有 vision / data 在写文件**（07:06 仍在写）→ 而 pretrain/harness **零文件变更**。
**怀疑**：**pretrain/vision/data/harness 四条线共用同一 cline key** → vision+data 整夜抢占 → **pretrain/harness 被 Token 额度饿死**（已知坑：cline 额度耗尽**仍返回 `exit 0`**，loop 分辨不出，只睡 30min 再试 = **静默变慢而非崩溃**）。
**要回答的 4 个问题**：① loop 进程还在不在？② 日志里有没有「额度已用完」？③ **P-5b 到底跑完没有 / GPU 是否在空转**？④ `.12` 侧是否正常（做对照）。

**约束**：🚫 **纯只读** —— 不 kill / 不重启 / 不 `rm` / 不改任何文件；长输出 `cut -c1-140`；**不整树 `du`**。

```text
echo "=== 0. HOST / TIME ==="; hostname; date '+%F %T %Z'

echo; echo "=== 1. [.29] LOOPS ==="
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"

echo; echo "=== 2. [.29] LOOP LOGS (tail 18 + Token额度 命中数) ==="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_harness_loop.log; do
  echo "-- $f  mtime=$(stat -c %y "$f" 2>/dev/null | cut -c1-19)  size=$(stat -c %s "$f" 2>/dev/null)"
  printf '   Token额度相关行数 = '; grep -c '额度\|quota\|Token\|Forbidden' "$f" 2>/dev/null || echo 0
  tail -n 18 "$f" 2>/dev/null | cut -c1-160
  echo
done

echo "=== 3. [.29] /tmp 最近改动的日志（判断最后一次唤醒时间）==="
ls -lt --time-style=long-iso /tmp/*.log 2>/dev/null | head -12

echo; echo "=== 4. [.29] 训练进程 + GPU（P-5b 是否还在跑）==="
pgrep -af 'pretrain_launcher|torchrun|p5b' | cut -c1-140 | head -10 || echo "(NO torchrun => 训练已结束)"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null || echo "(nvidia-smi failed)"
echo "-- /tmp/baize_p5b.log tail 10 --"; tail -n 10 /tmp/baize_p5b.log 2>/dev/null | cut -c1-160 || echo "(no p5b log)"

echo; echo "=== 5. [.29] P-5b ckpt（看 final @4771 是否落盘）==="
CK=/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments
ls -1 "$CK" 2>/dev/null | head -15
for d in "$CK"/p5b "$CK"/p5b_*; do [ -d "$d" ] && { echo "-- $d"; ls -1t "$d" 2>/dev/null | head -8; }; done
echo "-- 含 4771 的路径 --"; find "$CK" -maxdepth 2 -name '*4771*' 2>/dev/null | head -5

echo; echo "=== 6. [.12] 远端（ssh）loops + GPU —— 做对照 ==="
timeout 25 ssh -o BatchMode=yes -o StrictHostKeyChecking=no 10.239.2.12 'hostname; echo "-- loops --"; pgrep -af "baize_.*_loop\.sh" | cut -c1-140; echo "-- gpu --"; nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader' 2>&1 | cut -c1-160 || echo "ssh 10.239.2.12 FAILED"

echo; echo "=== 7. 共享工作副本 git 状态 ==="
git -C /nas_train/app.e0031982/code/super_intelligence_2035 log --oneline -3 2>/dev/null
git -C /nas_train/app.e0031982/code/super_intelligence_2035 status -sb 2>/dev/null | head -6

echo; echo "=== DONE ==="
```

> ⛔ **已降级 RUN_ID 8**（清 relay 副本）为 ```text —— 它现在**不再**霸占「第一个块」。

## RUN_ID 8 — 🧹 **清 ops_relay 重复副本**（⚠️ **已被 RUN_ID 9 接管，本块不再执行**）

**背景**：`.29` 上又见 **2 个 `ops_relay.sh`**（`2489749` etimes≈42.8h + `2315903` etimes≈0）。
**目标**：只保留「运行最久」的那个；**若清理有任何不确定，就不杀、只报告**。
**底线**：**执行完必须仍有 ≥1 个 relay 存活**（否则假期无法通讯）。

```text
echo "=========== 0. 时间 ==========="
hostname; date '+%F %T %Z'
echo

echo "=========== 1. 现有 relay 清单（pid / ppid / etimes） ==========="
ps -eo pid=,ppid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-150
echo

echo "=========== 2. 定位【执行本命令的】relay（沿祖先进程回溯） ==========="
SELF=""
p=$$
for i in 1 2 3 4 5 6 7 8 9 10; do
  [ -z "$p" ] && break; [ "$p" = "0" ] && break; [ "$p" = "1" ] && break
  c=$(ps -o args= -p "$p" 2>/dev/null)
  case "$c" in *ops_relay.sh*) SELF="$p"; break;; esac
  p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' ')
done
echo "SELF = ${SELF:-<not found>}"

echo "=========== 3. KEEP = 运行最久者（etimes 最大） ==========="
KEEP=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | sort -k2 -nr | awk 'NR==1{print $1}')
echo "KEEP = ${KEEP:-<none>}"

echo "=========== 4. 清理（**只杀** 既非 KEEP 也非 SELF 的副本） ==========="
COUNT=$(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | wc -l)
echo "relay count before = $COUNT"
if [ -z "$KEEP" ]; then
  echo "!!! 未找到任何 relay → 不杀任何进程（fail-safe）"
elif [ "$COUNT" -le 1 ]; then
  echo "只有 1 个 → 无需清理"
else
  for pid in $(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | awk '{print $1}'); do
    if [ "$pid" = "$KEEP" ]; then echo "keep   pid=$pid (longest-running)"; continue; fi
    if [ -n "$SELF" ] && [ "$pid" = "$SELF" ]; then echo "keep   pid=$pid (=== SELF，延后处理)"; continue; fi
    echo "kill   pid=$pid (duplicate)"
    kill -TERM "$pid" 2>/dev/null
  done
fi
sleep 3

echo "=========== 5. 若 SELF 是副本 → **延后 90s 自行退出**（先让 outbox 写完并 push） ==========="
if [ -n "$SELF" ] && [ "$SELF" != "$KEEP" ]; then
  echo "SELF=$SELF ≠ KEEP=$KEEP → 本进程为副本，90s 后自行退出（setsid 脱离，保证 outbox 先落地）"
  setsid sh -c "sleep 90; kill -TERM $SELF" >/dev/null 2>&1 < /dev/null &
else
  echo "SELF == KEEP（或未定位）→ 无需自退"
fi

echo "=========== 6. 收尾核对（**必须 ≥1 存活**） ==========="
sleep 2
REMAIN=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-150)
echo "$REMAIN"
n=$(ps -eo pid=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | wc -l)
echo "relay count after = $n"
if [ "$n" -ge 1 ]; then echo "OK: 至少 1 个存活（通讯可用）"; else echo "!!! 警告：0 个存活 —— 需人工重启 relay（勿删本目录）"; fi
echo
echo "=========== DONE ==========="
```

---

## RUN_ID 7（**已被 RUN_ID 8 接管，本块不再执行**）— 只读诊断

**背景（运维 2026-10-03 10:57）**：`09:00` 之后**没有 agent 的提交**（只有运维自己的），而各线 `WAITING=1` 预期约每 50 分钟一轮。
→ 疑因：某线 cline 会话较长（data 可能在 `rm -rf` 8.1T）、或 `git pull --rebase` 撞上运维的密集推送而跳过 push 周期。
**本块只读，不改任何东西、不 kill 任何进程。**

```text
echo "=========== 0. 时间（host / date） ==========="
hostname; date '+%F %T %Z'
echo

echo "=========== 1. loop / relay 进程（预期 4 loop + 1 relay） ==========="
ps -eo pid=,etimes=,stat=,args= 2>/dev/null | grep -E 'baize_.*_loop\.sh|ops_relay\.sh' | grep -v grep | cut -c1-150
echo

echo "=========== 2. 共享工作副本：未提交 / 未推送 / 最近提交 ==========="
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null || { echo "REPO MISSING"; exit 0; }
git status -sb 2>&1 | head -25
echo "-- 最近 6 条本地提交 --"
git --no-pager log --oneline -6 2>&1 | cut -c1-120
echo "-- 与远端 leading/behind（L=ahead R=behind，fetch 由 relay 自己做过） --"
git rev-list --left-right --count origin/main...HEAD 2>/dev/null || echo "(no origin/main ref)"
echo

echo "=========== 3. 各 loop 日志尾部（是否在跑 / 报错） ==========="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_vision_loop.log /tmp/baize_data_loop.log /tmp/baize_harness_loop.log; do
  if [ -f "$f" ]; then
    printf '== %s (mtime %s)\n' "$f" "$(date -r "$f" '+%F %T' 2>/dev/null)"
    tail -4 "$f" | cut -c1-160
  else
    printf '== %s : (no log)\n' "$f"
  fi
done
echo "-- ops relay 日志 --"
tail -6 /tmp/ops_relay.log 2>/dev/null | cut -c1-160 || echo "(no /tmp/ops_relay.log)"
echo

echo "=========== 4. GPU 占用（谁在跑） ==========="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | cut -c1-60 || echo "(no nvidia-smi)"
echo

echo "=========== 5. 关键训练日志 ==========="
for f in /tmp/r10_denseM.log /tmp/baize_p5b_train.log; do
  [ -f "$f" ] && { printf '== %s (mtime %s)\n' "$f" "$(date -r "$f" '+%F %T')"; tail -3 "$f" | cut -c1-160; }
done
echo "-- R10③ 是否 DONE（预期 0→1） --"
grep -c 'denseM ALL DONE' /tmp/r10_denseM.log 2>/dev/null || echo 0
echo

echo "=========== 6. 磁盘 + GPIC / laion2B ==========="
df -hT /nas_train 2>/dev/null | tail -1
echo "-- gpic train tar 数（预期 ≥1131/8000） --"
ls -1 /nas_inference/app.e0031982/datasets/stanford-vision-lab/gpic/train/*.tar 2>/dev/null | wc -l
echo "-- laion2B-en-aesthetic 是否已删 --"
if [ -d /nas_train/app.e0031982/datasets/laion2B-en-aesthetic ]; then echo "STILL EXISTS"; else echo "GONE (deleted)"; fi
echo

echo "=========== DONE ==========="
```

---

## RUN_ID 6（**已被 RUN_ID 7 接管，本块不再执行**）— 清重复 relay + 勘查既有 harness 研究线

**目标**：① 清掉重复的 `ops_relay.sh`；② **只读**勘查 `/nas_train/app.e0031982/harness/` 里那条**既有的** harness 研究线（运维指示：**可以合并**）。

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 当前 relay / loop 进程 ==========="
pgrep -af 'ops_relay.sh|baize_.*_loop\.sh' | cut -c1-140
echo

echo "=========== 2. 清重复的 ops_relay.sh（保留【启动最早】的那个） ==========="
echo "⚠️ 用 etimes(已运行秒数) 排序取最早，不用 PID 数字 —— PID 会回绕，数字小不代表更早"
echo "   证据：两次独立观测（RUN_ID 2 与 5）都看到【2 个】relay，其中 2489749 跨两次存活，"
echo "         另一个从 1276654 变成 2228582 → 2489749 是更早/更稳的那个。"
ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-140
KEEP=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | sort -k2 -nr | awk 'NR==1{print $1}')
RELAYS=$(ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | awk '{print $1}')
echo "keep (longest-running) = $KEEP ; all = $(echo $RELAYS | tr '\n' ' ')"
for p in $RELAYS; do
  if [ "$p" != "$KEEP" ]; then
    echo "killing duplicate relay pid=$p"
    kill "$p" 2>/dev/null
  fi
done
sleep 3
echo "-- after（预期只剩 1 个） --"
ps -eo pid=,etimes=,args= 2>/dev/null | grep 'ops_relay\.sh' | grep -v grep | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 勘查【既有】harness 研究线（只读，不改动） ==========="
H=/nas_train/app.e0031982/harness
echo "-- 顶层（含日期，用于确认它早于我们） --"
ls -la "$H" 2>/dev/null | cut -c1-140
echo
echo "-- 它的 loop.sh 是否在跑？ --"
pgrep -af 'harness/loop.sh' | cut -c1-140 || echo "(NOT running)"
echo
echo "-- MEMORY.md 顶部 25 行 --"
head -25 "$H/MEMORY.md" 2>/dev/null | cut -c1-170 || echo "(no MEMORY.md)"
echo
echo "-- analyze_harness_sources.md 的章节标题 --"
grep -nE '^#{1,3} ' "$H/analyze_harness_sources.md" 2>/dev/null | head -25 | cut -c1-150 || echo "(none)"
echo
echo "-- report.html 的 title/h1/h2（看它覆盖了什么） --"
grep -oE '<(title|h1|h2)[^>]*>[^<]{0,90}' "$H/report.html" 2>/dev/null | head -18 || echo "(none)"
echo
echo "-- evidence/ --"
ls -la "$H/evidence" 2>/dev/null | head -15 | cut -c1-140
echo "-- mechanisms/ --"
ls -la "$H/mechanisms" 2>/dev/null | head -15 | cut -c1-140
echo
echo "-- daily-memories/ 最近 5 个 --"
ls -1t "$H/daily-memories" 2>/dev/null | head -5
echo

echo "=========== 4. 5 个 harness 的形态（目录 + README 首 3 行） ==========="
for d in cline opencode deepseek-harness codex claude-code; do
  if [ -d "$H/$d" ]; then
    echo "---- $d ----"
    ls "$H/$d" 2>/dev/null | head -14 | tr '\n' ' '; echo
    head -3 "$H/$d/README.md" 2>/dev/null | cut -c1-150
    echo
  else
    echo "---- $d : MISSING ----"
  fi
done

echo "=========== DONE ==========="
```

---

## RUN_ID 5 — 启动 harness 线（✅ **已执行 2026-10-02 22:20, exit=0**）

> ✅ **已生效**：`baize_harness_loop.sh` 已启动（pid 2228938），agent 已接单并读到任务书。
> ⚠️ 围栏已降级为 ```text，**避免霸占"第一个块"**（本文件太长，只认第一个是 relay 的既有行为）。

**目标**：起 `baize_harness_loop.sh`（H-A: SWE-bench 横评 / H-B: harness 源码分析），并校验它接单。

**背景**：运维新建了第 4 条线 ——
任务书 `BAIZE_HARNESS_TASK.md`、loop `baize_harness_loop.sh`、状态 `MEMORY_HARNESS.md`、
产物 `harness/`、日志 `daily-memories-harness/`。**已在 `AGENTS.md` 登记。**

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 前置校验（任务书 / loop / 状态文件） ==========="
for f in BAIZE_HARNESS_TASK.md baize_harness_loop.sh MEMORY_HARNESS.md; do
  if [ -f "$f" ]; then printf '%-28s : OK (%s bytes)\n' "$f" "$(stat -c%s "$f")"; else printf '%-28s : MISSING !!!\n' "$f"; fi
done
echo
echo "-- H-B 的分析对象：harness 源码目录 --"
ls -la /nas_train/app.e0031982/harness/ 2>/dev/null | head -30 || echo "MISSING: /nas_train/app.e0031982/harness/"
echo

echo "=========== 2. 资源摸底（harness 线跑在本机，先看余量 + Docker） ==========="
echo "-- CPU / 内存 --"
nproc; free -g | head -2
echo "-- 磁盘 --"
df -h /nas_train /tmp 2>/dev/null
echo "-- Docker（H-A 的 SWE-bench 评测依赖它） --"
docker info >/dev/null 2>&1 && echo "docker: AVAILABLE" || echo "docker: NOT AVAILABLE (H-A 会因此受阻，如实上报)"
echo "-- 本机已有 loop（预期 3 个：vision/pretrain/data） --"
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 查重（避免起两个） ==========="
if pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  echo "ALREADY RUNNING - skip launch:"
  pgrep -af 'baize_harness_loop.sh' | cut -c1-140
else
  echo "(not running yet — will launch)"
fi
echo

echo "=========== 4. 启动（脱离进程组，防工具超时误杀） ==========="
if ! pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  chmod +x baize_harness_loop.sh
  touch MEMORY_HARNESS.md
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 8
  echo "launched."
else
  echo "skip (already running)."
fi
echo

echo "=========== 5. 验证（应恰好 1 个进程 + 日志出现 [loop] 行） ==========="
pgrep -af 'baize_harness_loop.sh' | cut -c1-140 || echo "!!! NOT RUNNING — 需排查 /tmp/baize_harness_loop.log"
echo "-- log tail --"
tail -8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-160 || echo "(no log yet)"
echo

echo "=========== 6. 全量 loop 一览（预期 4 个） ==========="
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' | cut -c1-140
echo

echo "=========== DONE ==========="
```

---

## RUN_ID 3 — 磁盘空间与占用分布（**已执行，归档**）

> ⚠️ **本块已从 ```bash 降级为 ```text** —— 因为中继**只认第一个 ```bash 块**，
> 留着会让它每次都把这条勘察重跑一遍（实测踩过：RUN_ID 3→4 时中继又跑了这条）。

**目标**：确认 `df -h` 实况；定位 `/nas_train` 175 TB 被什么占用；核对数据准备所需空间与剩余空间。

```text
echo "=========== DF -H (ALL MOUNTS) ==========="
df -h
echo
echo "=========== DF -H (NAS + ROOT, explicit) ==========="
df -h /nas_train /nas_inference /nas_user /nas_env / 2>/dev/null
echo
echo "=========== DF -I (INODES — large-corpus trap) ==========="
df -i /nas_train /nas_inference /nas_user / 2>/dev/null
echo
echo "=========== TARGETED DU (bounded, timeout 150s each) ==========="
for d in \
  /nas_train/app.e0031982/datasets/baize-vision \
  /nas_train/app.e0031982/datasets/baize-data \
  /nas_train/app.e0031982/datasets/mvp-lab \
  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/data \
  /nas_train/app.e0031982/models \
  /nas_inference/app.e0031982/datasets/openbmb ; do
  if [ -e "$d" ]; then
    printf '%-58s : ' "$d"
    timeout 150 du -sh "$d" 2>/dev/null | cut -f1 || echo "(du timeout/fail)"
  else
    echo "$d : MISSING"
  fi
done
echo
echo "=========== TOP-LEVEL LISTING (no du, just names) ==========="
echo "-- /nas_train/app.e0031982 --"
ls -1 /nas_train/app.e0031982 2>/dev/null | head -20
echo "-- /nas_train/app.e0031982/datasets --"
ls -1 /nas_train/app.e0031982/datasets 2>/dev/null | head -40
echo "-- /nas_user/app.e0031982/datasets --"
ls -1 /nas_user/app.e0031982/datasets 2>/dev/null | head -40
echo
echo "=========== BAZE-VISION DETAIL (stage iii/iv) ==========="
ls -1 /nas_train/app.e0031982/datasets/baize-vision 2>/dev/null || echo "MISSING"
timeout 60 du -sh /nas_train/app.e0031982/datasets/baize-vision/* 2>/dev/null | cut -f1,2 | head -10
echo
echo "=========== ANY IN-PROGRESS DOWNLOAD? ==========="
ps -eo pid=,etime=,comm=,args= 2>/dev/null | grep -E 'wget|curl|hf_transfer|datasets|nohup' | grep -v grep | cut -c1-140 | head -10 || echo "(none)"
echo "-- nohup.out tail (if a download is logging) --"
for f in /nas_inference/app.e0031982/datasets/nohup.out /nas_train/app.e0031982/datasets/nohup.out; do
  [ -f "$f" ] && { echo "== $f"; tail -5 "$f" | cut -c1-140; }
done
echo
echo "=========== DONE ==========="
```

---

## RUN_ID 4 — **启动 harness 线**（⛔ **已作废：当时并未生效**）

> ⛔ **本块从未被执行** —— 因为中继只认文件里**第一个** ```bash 块，而它在 RUN_ID 3 的块之后。
> **已由 RUN_ID 5 接管**（见文件最前面）。本块仅作归档，围栏已降级为 ```text。

**目标**：起 `baize_harness_loop.sh`（H-A: SWE-bench 横评 / H-B: harness 源码分析），并校验它接单。

**背景**：运维新建了第 4 条线 ——
任务书 `BAIZE_HARNESS_TASK.md`、loop `baize_harness_loop.sh`、状态 `MEMORY_HARNESS.md`、
产物 `harness/`、日志 `daily-memories-harness/`。**已在 `AGENTS.md` 登记。**

```text
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo "=========== 1. 前置校验（任务书 / loop / 状态文件） ==========="
for f in BAIZE_HARNESS_TASK.md baize_harness_loop.sh MEMORY_HARNESS.md; do
  if [ -f "$f" ]; then printf '%-28s : OK (%s bytes)\n' "$f" "$(stat -c%s "$f")"; else printf '%-28s : MISSING !!!\n' "$f"; fi
done
echo
echo "-- H-B 的分析对象：harness 源码目录 --"
ls -la /nas_train/app.e0031982/harness/ 2>/dev/null | head -30 || echo "MISSING: /nas_train/app.e0031982/harness/"
echo

echo "=========== 2. 资源摸底（harness 线跑在本机，先看余量 + Docker） ==========="
echo "-- CPU / 内存 --"
nproc; free -g | head -2
echo "-- 磁盘 --"
df -h /nas_train /tmp 2>/dev/null
echo "-- Docker（H-A 的 SWE-bench 评测依赖它） --"
docker info >/dev/null 2>&1 && echo "docker: AVAILABLE" || echo "docker: NOT AVAILABLE (H-A 会因此受阻，如实上报)"
echo "-- 本机已有 loop（预期 3 个：vision/pretrain/data） --"
pgrep -af 'baize_.*_loop\.sh' | cut -c1-140 || echo "(none)"
echo

echo "=========== 3. 查重（避免起两个） ==========="
if pgrep -af 'baize_harness_loop.sh' | grep -v grep >/dev/null 2>&1; then
  echo "ALREADY RUNNING - skip launch:"
  pgrep -af 'baize_harness_loop.sh' | cut -c1-140
else
  echo "(not running yet — will launch)"
fi
echo

echo "=========== 4. 启动（脱离进程组，防工具超时误杀） ==========="
if ! pgrep -f 'baize_harness_loop.sh' >/dev/null 2>&1; then
  chmod +x baize_harness_loop.sh
  setsid bash baize_harness_loop.sh > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
  sleep 8
  echo "launched."
else
  echo "skip (already running)."
fi
echo

echo "=========== 5. 验证（应恰好 1 个进程 + 日志出现 [loop] 行） ==========="
pgrep -af 'baize_harness_loop.sh' | cut -c1-140 || echo "!!! NOT RUNNING — 需排查 /tmp/baize_harness_loop.log"
echo "-- log tail --"
tail -8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-160 || echo "(no log yet)"
echo

echo "=========== 6. 全量 loop 一览（预期 4 个） ==========="
pgrep -af 'baize_.*_loop\.sh|ops_relay\.sh' | cut -c1-140
echo

echo "=========== DONE ==========="
```
