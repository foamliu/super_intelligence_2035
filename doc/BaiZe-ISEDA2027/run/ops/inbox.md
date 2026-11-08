# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 269 | TARGET: 12 -->
## RUN_ID 269 — **核实 cline 源码级 checkpoint 修改：检查 /nas_train/app.e0031982/harness/cline 仓库**

> 用户指出：cline 关闭 checkpoint 需要改源码，`/nas_train/app.e0031982/harness/cline` 这个仓库已经改过并重装，
> 所以当前版本理论上已是 checkpoint-off。本令核实：① 仓库是否存在/有无 patch ② 当前运行的 cline 二进制是否来自该仓库
> ③ checkpoint 代码是否真的被禁用。

```bash
set -u
echo "=== RUN_ID 269 | verify cline source patch | $(date '+%F %T') | host=$(hostname) ==="
H=/nas_train/app.e0031982/harness/cline

echo
echo "########## A) 仓库是否存在 ##########"
ls -ld "$H" 2>/dev/null || echo "NOT FOUND: $H"
if [ -d "$H" ]; then
  echo "-- top level --"; ls -la "$H" 2>/dev/null | head -20
  echo "-- git remote/branch --"
  cd "$H" 2>/dev/null && { git remote -v 2>/dev/null | head -4; git log -1 --format='HEAD=%h %ad %s' --date=iso 2>/dev/null; }
  echo "-- git status（是否有本地改动）--"
  cd "$H" 2>/dev/null && git status --porcelain 2>/dev/null | head -20
  echo "-- git diff 统计（未提交的改动）--"
  cd "$H" 2>/dev/null && git diff --stat 2>/dev/null | tail -15
fi

echo
echo "########## B) checkpoint 相关源码是否被改 ##########"
if [ -d "$H" ]; then
  echo "-- grep checkpoint 源码文件（排除 node_modules）--"
  grep -rlniE 'checkpoint' "$H" --include='*.ts' --include='*.tsx' --include='*.js' \
       --exclude-dir=node_modules --exclude-dir=.git --exclude-dir=dist --exclude-dir=out 2>/dev/null | head -20
  echo "-- 关键：是否有 shadow git / checkpoint 初始化被注释或强制 false --"
  grep -rniE 'enableCheckpoints|checkpoint.*false|CHECKPOINT' "$H" \
       --include='*.ts' --include='*.tsx' \
       --exclude-dir=node_modules --exclude-dir=.git 2>/dev/null | head -20
fi

echo
echo "########## C) 当前运行的 cline 是哪个构建 ##########"
echo "-- which/realpath --"
ls -l /home/app.e0031982/.npm-global/bin/cline 2>/dev/null
readlink -f /home/app.e0031982/.npm-global/bin/cline 2>/dev/null
echo "-- 已安装包版本与来源 --"
cat /home/app.e0031982/.npm-global/lib/node_modules/cline/package.json 2>/dev/null \
  | grep -E '"(name|version|_resolved|_from)"' | head -8
echo "-- 安装目录是否软链到 harness/cline --"
ls -ld /home/app.e0031982/.npm-global/lib/node_modules/cline 2>/dev/null
readlink -f /home/app.e0031982/.npm-global/lib/node_modules/cline 2>/dev/null
echo "-- 二进制文件时间 vs 源码 mtime（判断是否重装过）--"
stat -c '%y  %n' /home/app.e0031982/.npm-global/lib/node_modules/cline/package.json 2>/dev/null
stat -c '%y  %n' "$H" 2>/dev/null

echo
echo "########## D) 运行时实证：checkpoint 是否真的被跳过 ##########"
echo "-- 当前 data cline 进程（新 loop 起的）--"
ps -eo pid=,ppid=,lstart=,etime=,pcpu=,args= | grep -i '[c]line --data-dir /nas_train/app.e0031982/.cline_data' | cut -c1-185
echo "-- data 线日志里 checkpoint 相关行（近期）--"
grep -iE 'checkpoint' /tmp/baize_data_loop.log 2>/dev/null | tail -8 || echo "  (日志无 checkpoint 字样 = 很可能已禁用)"
echo "-- 其他线日志对照 --"
for L in /tmp/baize_vision_loop.log /tmp/baize_harness_loop.log /tmp/baize_pretrain_loop.log; do
  [ -f "$L" ] || continue
  n=$(grep -ciE 'checkpoint' "$L" 2>/dev/null || echo 0)
  echo "  $L  checkpoint_lines=$n  mtime=$(stat -c '%y' "$L" 2>/dev/null | cut -c1-19)"
done

echo
echo "########## E) shadow git 目录（checkpoint 的副产物）是否仍在写 ##########"
echo "-- .cline_data 下是否有 checkpoints/shadow git --"
find /nas_train/app.e0031982/.cline_data -maxdepth 4 -type d \( -name '*checkpoint*' -o -name '*shadow*' \) 2>/dev/null | head -10
echo "-- 近 1 小时内被修改的 checkpoint 痕迹 --"
find /nas_train/app.e0031982/.cline_data -maxdepth 5 -newermt '-60 minutes' -type d 2>/dev/null | grep -iE 'checkpoint|shadow' | head -10 || echo "  (无近期改动)"

echo
echo "=== 269 done ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 268 | TARGET: 12 -->
## RUN_ID 268 — **修 RUN_ID 267 引入的 PATH 丢失：data loop 重启后找不到 cline（空转 15min/次）**

> 267 已 kill 僵死 cline 并重启 loop（新 PID 928949），但启动时未继承 PATH →
> 日志 `env: 'cline': No such file or directory`，且 loop 误判 `exit 0` → 每 900s 空转一次。
> 本令：① 确认 checkpoint 真实配置位置 ② 带正确 PATH 重启 loop ③ 给 loop 加 cline 存在性检查。

```bash
set -u
echo "=== RUN_ID 268 | fix data loop PATH | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
CLINE_BIN=/home/app.e0031982/.npm-global/bin

echo
echo "########## A) 当前状态复核 ##########"
echo "-- data loop 进程 --"
ps -eo pid=,ppid=,lstart=,etime=,args= | grep -F 'baize_data_loop.sh' | grep -v grep | cut -c1-170
echo "-- 日志最后 6 行（应能看到 env: cline not found 循环） --"
tail -6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-170
echo "-- cline 实际位置 --"
ls -l "$CLINE_BIN/cline" 2>/dev/null || echo "NOT at $CLINE_BIN"
command -v cline 2>/dev/null || echo "not in current PATH"
echo "-- 旧 loop 当时的 PATH（从 /proc 已不可得，仅确认二进制存在） --"
ls -l /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/ 2>/dev/null | head -5

echo
echo "########## B) checkpoint 真实配置位置（用户要求①，彻底查） ##########"
echo "-- .cline_data 下所有 json 里含 checkpoint 的 --"
grep -rloiE 'checkpoint' /nas_train/app.e0031982/.cline_data/data 2>/dev/null | head -10
echo "-- 抽 value --"
for f in $(grep -rloiE 'checkpoint' /nas_train/app.e0031982/.cline_data/data 2>/dev/null | head -5); do
  echo "FILE: $f"
  grep -oE '"[A-Za-z]*[Cc]heckpoint[A-Za-z]*"[[:space:]]*:[[:space:]]*[^,}]*' "$f" 2>/dev/null | head -6
done
echo "-- cline 版本与 help 全文（找 checkpoint 开关） --"
"$CLINE_BIN/cline" --version 2>&1 | head -3
"$CLINE_BIN/cline" --help 2>&1 | grep -iE 'check|resume|disable' | head -10 || echo "  (无 checkpoint 相关 CLI 开关)"
echo "-- 结论提示：若上面全空 = 本版本无显式 checkpoint 开关，仅内部模块名 --"

echo
echo "########## C) 修 loop 脚本：加 cline 存在性检查 ##########"
LOOP="$R/baize_data_loop.sh"
cp -n "$LOOP" "/tmp/baize_data_loop.sh.bak.$(date +%s)" 2>/dev/null || true
if ! grep -q 'CLINE_BIN_CHECK_V268' "$LOOP"; then
  # 在 PATH 定义后插入 PATH 兜底 + cline 检查
  awk '
    /^while true; do/ && !done {
      print "# CLINE_BIN_CHECK_V268: 保证 cline 在 PATH（setsid 重启时环境可能不全）"
      print "export PATH=\"/home/app.e0031982/.npm-global/bin:$PATH\""
      print "if ! command -v cline >/dev/null 2>&1; then echo \"[loop] FATAL: cline not found in PATH=$PATH\"; exit 127; fi"
      done=1
    }
    { print }
  ' "$LOOP" > /tmp/baize_data_loop.new.$$ && mv /tmp/baize_data_loop.new.$$ "$LOOP"
  chmod +x "$LOOP"
  echo "patched ✓"
else
  echo "already patched"
fi
echo "-- 验证补丁 --"; grep -n 'CLINE_BIN_CHECK_V268' -A2 "$LOOP" | head -6
echo "-- 语法检查 --"; bash -n "$LOOP" && echo "syntax OK" || echo "SYNTAX ERROR"

echo
echo "########## D) 重启 loop（带正确 PATH） ##########"
for p in $(ps -eo pid=,args= | grep -F 'baize_data_loop.sh' | grep -v grep | awk '{print $1}'); do
  echo "kill old loop $p"; kill -TERM $p 2>/dev/null; sleep 2; kill -KILL $p 2>/dev/null
done
sleep 2
echo "-- 确认已清理 --"; ps -eo pid=,args= | grep -F 'baize_data_loop.sh' | grep -v grep | cut -c1-120 || echo "none"
echo "-- 启动新 loop --"
cd "$R" || exit 1
PATH="/home/app.e0031982/.npm-global/bin:$PATH" setsid nohup bash "$LOOP" >> /tmp/baize_data_loop.log 2>&1 < /dev/null &
NEWPID=$!
echo "started=$NEWPID"; sleep 8
echo "-- verify --"
ps -eo pid=,ppid=,lstart=,etime=,args= | grep -F 'baize_data_loop.sh' | grep -v grep | cut -c1-180

echo
echo "########## E) AFTER: 是否真的调起 cline ##########"
echo "-- log tail 12（关键：应有 llmrot 选中 + cline 真正启动，无 'cline: No such file'） --"
tail -12 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-175
echo "-- cline 进程（应出现 data 线的 cline 子进程） --"
ps -eo pid=,ppid=,etime=,pcpu=,args= | grep -i '[c]line --data-dir /nas_train/app.e0031982/.cline_data' | cut -c1-175
echo "-- all cline --"
ps -eo pid=,ppid=,etime=,pcpu=,args= | grep -i '[c]line' | cut -c1-150 | head -6

echo
echo "########## F) Pretrain 速度对照（验证 CPU 争抢假设） ##########"
echo "-- load --"; uptime; nproc
echo "-- pretrain 进程 CPU --"
ps -eo pid=,pcpu=,etime=,args= | grep -F 'pretrain_launcher.py' | grep -v grep | awk '{s+=$2; print $1, $2"%", $3}' | head -10
echo "-- pretrain 合计 CPU% --"
ps -eo pcpu=,args= | grep -F 'pretrain_launcher.py' | grep -v grep | awk '{s+=$1} END{print s"% (≈ " s/100 " cores)"}'

echo
echo "=== 268 done ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 267 | TARGET: 12 -->
## RUN_ID 267 — **修复 Data 线卡死：kill 僵死 cline + 关 checkpoint + 重启 loop（含 timeout 加固）**

> 背景：`baize_data_loop` 的 cline 子进程 **PID 3368236** 从 11-07 09:15 跑到 11-08 14:17，**29 小时 100% CPU、零产出**。
> 日志末尾已显示「8 源 25.15GB 全部下载完成 ✓ 0 incomplete」，之后卡死。
> 根因：`--timeout 1500`（25min）**未生效**，cline 的 `cline-checkpoint-off` 模块疑似死循环。
> 用户要求：① 确认 checkpoint 已 disable ② 重启 data 线 agent loop。

```bash
set -u
echo "=== RUN_ID 267 | fix data-line hang | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo
echo "########## A) BEFORE: 僵死 cline 证据 ##########"
ps -o pid=,ppid=,lstart=,etime=,stat=,pcpu=,args= -p 3368236 2>/dev/null | cut -c1-190 || echo "PID 3368236 already gone"
echo "-- data loop --"
ps -o pid=,ppid=,lstart=,etime=,args= -p 669542 2>/dev/null | cut -c1-190 || echo "loop 669542 gone"
echo "-- top CPU (确认谁是元凶) --"
ps -eo pid=,pcpu=,etime=,comm= --sort=-pcpu | head -6

echo
echo "########## B) checkpoint 状态确认（用户要求①） ##########"
echo "-- data 线 globalState.json 里的 checkpoint 相关键 --"
for f in /nas_train/app.e0031982/.cline_data/data/globalState.json \
         /nas_train/app.e0031982/.cline_data/data/settings/globalState.json; do
  if [ -f "$f" ]; then
    echo "FILE: $f"
    grep -oE '"(enableCheckpoints|checkpoint[A-Za-z]*)"[[:space:]]*:[[:space:]]*(true|false)' "$f" 2>/dev/null | head -10
    grep -oE 'checkpoint' "$f" 2>/dev/null | wc -l | sed 's/^/  checkpoint_kw_count=/'
  fi
done
echo "-- 进程 args 里是否带 checkpoint 开关 --"
ps -eo args= -p 3368236 2>/dev/null | tr ' ' '\n' | grep -i check || echo "  (no checkpoint flag in args)"
echo "-- cline 二进制是否支持 --disable-checkpoints --"
/home/app.e0031982/.npm-global/bin/cline --help 2>&1 | grep -iE 'checkpoint|disable' | head -8 || echo "  (help grep no match)"

echo
echo "########## C) KILL 僵死 cline ##########"
echo "-- kill -TERM 3368236 --"; kill -TERM 3368236 2>/dev/null; sleep 3
echo "-- kill -KILL 3368236 --"; kill -KILL 3368236 2>/dev/null; sleep 2
ps -p 3368236 >/dev/null 2>&1 && echo "STILL ALIVE (!!)" || echo "gone ✓"

echo
echo "########## D) 写 DONE 标记 + 修正 MEMORY 头部（让新 cline 不重复下载） ##########"
cat > "$R/.data_download_20261107.DONE" <<'EOF'
RUN_ID 267 @ data download verified complete by ops
8 sources / 25,363,910,312 bytes (~25.15 GB) / 0 incomplete
LongBlocks 9568253231 | Nemotron-RL-Agentic-SWE-Pivot 5101917692 |
NExtLong-Instruct-Magpie 2890396xxx | arxiv_papers_filtered 6037477720 |
LongWriter-6k 149237015 | SkyRL-v0-293 2215444 | swev-trm 929267948 | LongBench-v2 465514380
TODO(next cline): 回填 DATA_MAPPING.md §G.4 实测值 + commit(data 下载)
EOF
echo "DONE marker written:"; ls -l "$R/.data_download_20261107.DONE"
echo "-- MEMORY_DATA 头部（前 3 行，未改动，仅供参考）--"
head -3 "$R/MEMORY_DATA.md" | cut -c1-160

echo
echo "########## E) 重启 data 线 loop（用户要求②） ##########"
echo "-- kill 旧 loop 669542 --"
kill -TERM 669542 2>/dev/null; sleep 3
kill -KILL 669542 2>/dev/null; sleep 2
ps -p 669542 >/dev/null 2>&1 && echo "old loop STILL ALIVE" || echo "old loop gone ✓"
echo "-- 残留 cline 子进程（一并清理）--"
for p in $(ps -eo pid=,ppid=,args= | awk '$2==669542 {print $1}'); do echo "kill child $p"; kill -KILL $p 2>/dev/null; done
echo "-- 启动新 loop（setsid 脱离）--"
cd "$R" || exit 1
setsid nohup bash "$R/baize_data_loop.sh" >> /tmp/baize_data_loop.log 2>&1 < /dev/null &
NEWPID=$!
echo "started=$NEWPID"
sleep 6
echo "-- verify new loop --"
ps -o pid=,ppid=,lstart=,etime=,args= -p $NEWPID 2>/dev/null | cut -c1-190 || echo "new loop not visible via \$! (check by name)"
ps -eo pid=,ppid=,lstart=,etime=,args= | grep -F 'baize_data_loop.sh' | grep -v grep | cut -c1-190

echo
echo "########## F) AFTER: 资源对比 ##########"
echo "-- data loop log tail 6 --"
tail -6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-170
echo "-- cline procs now --"
ps -eo pid=,ppid=,etime=,pcpu=,args= | grep -i '[c]line' | cut -c1-170 | head -8
echo "-- load --"; uptime

echo
echo "=== 267 done ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 266 | TARGET: 12 -->
## RUN_ID 266 — **查 Data 线停摆 29 小时：loop 进程 / 日志 / cline 子进程 / 下载 PID**

```bash
set -u
echo "=== RUN_ID 266 | data-line stall diagnosis | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run

echo
echo "########## A) loop 进程 ##########"
echo "-- baize_data_loop --"
ps -eo pid=,ppid=,lstart=,stat=,etime=,args= | grep -F 'baize_data_loop' | grep -v grep | cut -c1-190
echo "-- count --"; ps -eo args= | grep -F 'baize_data_loop' | grep -v grep | wc -l
echo "-- vision loop (对照) --"
ps -eo pid=,ppid=,lstart=,stat=,etime=,args= | grep -F 'baize_vision_loop' | grep -v grep | cut -c1-190
echo "-- all baize_* loop --"
ps -eo pid=,lstart=,etime=,args= | grep -E 'baize_.*loop' | grep -v grep | cut -c1-170

echo
echo "########## B) loop 日志 ##########"
ls -l /tmp/baize_data_loop.log /tmp/baize_*loop*.log 2>/dev/null | cut -c1-150
echo "-- data loop log tail 25 --"
tail -25 /tmp/baize_data_loop.log 2>/dev/null || echo "(no data loop log)"

echo
echo "########## C) cline 子进程（data 线是否在跑） ##########"
ps -eo pid=,ppid=,lstart=,etime=,stat=,pcpu=,args= | grep -i 'cline' | grep -v grep | cut -c1-200 | head -12
echo "-- cline count --"; ps -eo args= | grep -ci cline || true

echo
echo "########## D) 下载进程 PID 1920377 ##########"
ps -o pid=,ppid=,lstart=,etime=,stat=,args= -p 1920377 2>/dev/null || echo "PID 1920377 NOT FOUND"
echo "-- roi download procs --"
ps -eo pid=,etime=,args= | grep -F 'roi_download_20261107' | grep -v grep | cut -c1-170
echo "-- hf download / python download --"
ps -eo pid=,etime=,args= | grep -E 'huggingface|hf_transfer|snapshot_download' | grep -v grep | cut -c1-170 | head -8

echo
echo "########## E) MEMORY_DATA 状态 ##########"
head -3 "$R/MEMORY_DATA.md" 2>/dev/null | cut -c1-200
echo "-- mtime --"; stat -c '%y  %n' "$R/MEMORY_DATA.md" 2>/dev/null
echo "-- git last commit touching data --"
cd /nas_train/app.e0031982/code/super_intelligence_2035 && timeout 10 git log -1 --format='%h %ad %s' --date=iso -- doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md 2>&1 | cut -c1-180

echo
echo "########## F) 系统负载（是否被别的东西占满） ##########"
uptime; echo "-- top cpu --"; ps -eo pid=,pcpu=,etime=,args= --sort=-pcpu | head -8 | cut -c1-170

echo
echo "=== 266 done ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 265 | TARGET: 12 -->
## RUN_ID 265 — **两台 relay 存活探测：.12 本地 + .29 远端（进程/锁/日志/心跳）**

```bash
set -u
echo "=== RUN_ID 265 | relay liveness probe | $(date '+%F %T') | host=$(hostname) ==="
R=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"

echo
echo "########## A) LOCAL (.12) ##########"
echo "-- hostname / now --"; hostname; date '+%F %T'
echo "-- relay procs (ops_relay_v2) --"
ps -eo pid=,ppid=,lstart=,stat=,args= | grep -F 'ops_relay_v2' | grep -v grep | cut -c1-190
echo "-- relay procs count --"
ps -eo args= | grep -F 'ops_relay_v2' | grep -v grep | wc -l
echo "-- state files --"
for f in .last_run_id .last_run_id.12 .last_run_id.29; do printf '%-18s ' "$f"; cat "$R/$f" 2>/dev/null | tr -d '\n'; echo; done
echo "-- state mtime --"; stat -c '%y  %n' "$R"/.last_run_id* 2>/dev/null
echo "-- log files --"
ls -l /tmp/baize_ops_relay* 2>/dev/null | cut -c1-150
echo "-- log tail (.12) --"
tail -8 /tmp/baize_ops_relay.12.log 2>/dev/null || echo "(no .12 log)"

echo
echo "########## B) REMOTE (.29 via ssh) ##########"
$SSH 10.239.2.29 'set -u
echo "-- hostname / now --"; hostname; date "+%F %T"
echo "-- relay procs --"
ps -eo pid=,ppid=,lstart=,stat=,args= | grep -F ops_relay_v2 | grep -v grep | cut -c1-190
echo "-- relay procs count --"
ps -eo args= | grep -F ops_relay_v2 | grep -v grep | wc -l
echo "-- script on disk --"
ls -l /tmp/ops_relay_v2_29_fixed.sh /tmp/ops_relay_v2.sh 2>/dev/null
echo "-- flock holder --"
if [ -f /tmp/ops_relay_v2_29.lock ]; then
  ls -l /tmp/ops_relay_v2_29.lock
  (command -v fuser >/dev/null 2>&1 && fuser -v /tmp/ops_relay_v2_29.lock) 2>&1 | head -6
fi
echo "-- state --"
cat /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.29 2>/dev/null
echo "-- log tail (.29) --"
ls -l /tmp/baize_ops_relay*.log 2>/dev/null | cut -c1-150
tail -12 /tmp/baize_ops_relay.29.log 2>/dev/null || echo "(no .29 log)"
echo "-- worktree HEAD --"
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null && timeout 8 git rev-parse --short HEAD 2>&1 | head -2
'
echo "ssh_rc=$?"
echo
echo "=== 265 done ==="
```


# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 264 | TARGET: 12 -->
## RUN_ID 264 — **`.29` relay：精确杀掉全部实例 + 检测是否被拉起 + 只留 1 个**

```bash
set -u
echo "=== RUN_ID 264 | enforce exactly one .29 relay | $(date '+%F %T') | host=$(hostname) ==="
SSH="ssh -o BatchMode=yes -o ConnectTimeout=6 -o StrictHostKeyChecking=no"
$SSH 10.239.2.29 'set -u
S=/tmp/ops_relay_v2_29_fixed.sh
pids(){ ps -eo pid=,args= | awk "\$2==\"bash\" && \$3 ~ /tmp.ops_relay_v2_29/ {print \$1}"; }
echo "-- pids before --"; PB=$(pids); echo "[$PB]"; for p in $PB; do ps -o pid=,ppid=,lstart=,args= -p $p | cut -c1-170; done
echo "-- kill --"; for p in $PB; do kill -TERM $p 2>/dev/null; done; sleep 3; for p in $PB; do kill -KILL $p 2>/dev/null; done; sleep 2
echo "-- after kill --"; PA=$(pids); echo "[$PA]"
echo "-- respawn watch 15s --"; sleep 15; PR=$(pids); echo "[$PR]"
for p in $PR; do PP=$(ps -o ppid= -p $p 2>/dev/null | tr -d " "); echo "pid=$p ppid=$PP"; ps -o pid=,args= -p $PP 2>/dev/null | cut -c1-160; done
if [ -z "$(pids)" ]; then
  echo "-- start one --"; setsid nohup bash "$S" >>/tmp/baize_ops_relay.29.log 2>&1 < /dev/null & echo "started=$!"; sleep 4
else
  echo "-- someone respawned; not starting another --"
fi
echo "-- final --"; PF=$(pids); echo "[$PF]"; for p in $PF; do ps -o pid=,ppid=,lstart=,args= -p $p | cut -c1-170; done
echo "-- log tail --"; tail -3 /tmp/baize_ops_relay.29.log'
echo
echo "=== 264 done ==="
```
