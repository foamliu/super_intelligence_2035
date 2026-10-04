# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）

<!-- RUN_ID: 10 -->

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

## RUN_ID 10 — 🔎 只读侦察：另一个 agent 的目录 `/nasdata/app.e0031982/code/ZhuLong_DAC2027`

**背景**：用户告知**另有一个 agent 在跑任务**，地址 `=` `/nasdata/app.e0031982/code/ZhuLong_DAC2027`（**不是**本合并线所在的 `super_intelligence_2035/doc/ZhuLong_DAC2027`）。目标：**观摩 & 理解它的工作，为接管做准备**。本块**只读**：目录结构、是否 git 仓库、进程、最近改动、文档/脚本清单。

```bash
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
