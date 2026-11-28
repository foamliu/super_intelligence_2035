# OPS INBOX — 运维下发命令（外部运维编辑，中继只读）
<!-- RUN_ID: 296 -->
## RUN_ID 296 — **重启 harness agent loop（llm_rotate 已移除 · 2026-11-28 09:2x 用户令）**

> **用户令**：「清理 baize_harness_loop.sh 中 llm_rotate.sh/llm_pick 相关代码，直接使用 cline 原来配的大模型。然后用 ops 中继重启 harness 的 agent loop」
> **已完成**：脚本已改（commit `7454560a89`），删除 `llm_rotate.sh` 加载与 `llm_pick` 分支，`cline -m $MODEL -k $CLINE_KEY` 直接用脚本内置 glm-5.2。
> **本块动作**：kill 旧 loop（空转那个）→ 启动新 loop → 验证 cline 真的被调用。

```bash
set -u
LOOP=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo

echo "== A. 前置：确认脚本已是新版 =="
grep -c 'llm_pick' "$LOOP" 2>/dev/null | sed 's/^/  llm_pick_occurrences=/'
grep -n 'cline -c' "$LOOP" 2>/dev/null | cut -c1-200
echo "  (应看到 -m \"\$MODEL\" -k \"\$CLINE_KEY\"，且 llm_pick 只在注释里出现 1 次)"
echo

echo "== B. 语法校验 =="
bash -n "$LOOP" && echo "  bash -n OK" || { echo "ABORT: 语法错误"; echo "=== DONE 296 (ABORT) ==="; exit 9; }
echo

echo "== C. 停掉旧 loop（空转那个）=="
OLD=$(pgrep -f 'baize_harness_loop' 2>/dev/null | tr '\n' ' ')
echo "  old_pids=[$OLD]"
for p in $OLD; do
  echo "  kill $p"; kill "$p" 2>/dev/null; sleep 3
  kill -0 "$p" 2>/dev/null && { echo "  kill -9 $p"; kill -9 "$p" 2>/dev/null; }
done
sleep 3
echo "  after_kill_count=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)"
echo

echo "== D. 启动新 loop =="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run || { echo "ABORT cd"; exit 9; }
mv -f /tmp/baize_harness_loop.log /tmp/baize_harness_loop.log.old.$(date +%H%M%S) 2>/dev/null
setsid bash "$LOOP" > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
NEWPID=$!
echo "  launched PID=$NEWPID"
sleep 20
echo

echo "== E. 启动后核验 =="
echo "  alive=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
echo "  loop_count=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)"
ps -eo pid,ppid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-150
echo

echo "== F. 日志（关键：应出现 invoking cline，且【不应】出现 llm_pick not found / 无可用 LLM 候选）=="
head -n 50 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-210
echo "  --- grep 判定 ---"
echo "  has_llm_pick_error=$(grep -c 'llm_pick: command not found' /tmp/baize_harness_loop.log 2>/dev/null || echo 0)"
echo "  has_skip_no_llm=$(grep -c '无可用 LLM 候选' /tmp/baize_harness_loop.log 2>/dev/null || echo 0)"
echo "  has_invoking=$(grep -c 'invoking cline' /tmp/baize_harness_loop.log 2>/dev/null || echo 0)"
echo

echo "== G. 等 90s 再看 cline 是否真跑起来 =="
sleep 90
echo "  loop_alive=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
echo "  cline_procs=$(pgrep -fc 'cline ' 2>/dev/null || echo 0)"
ps -eo pid,etime,rss,args | grep -E '[c]line ' | grep -i 'BaiZe' | cut -c1-170 | head -5
echo "  --- log tail ---"
tail -n 25 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-210
echo

echo "（仅重启 harness loop，未动别线、未改配置）"
echo "=== DONE 296 | $(date '+%F %T') ==="
```


> **用户令**：「你用 ops 中继排查一下 harness 的问题」；补充「harness 应该是在 .29 机器上」
> **已知**：RUN_ID 295 在 **`.12`** 上拉起 loop，日志报 `line 133: llm_pick: command not found`，
> 遂每轮「跳过 cline」、`WAITING=1`、sleep 900s ⇒ agent 从未运行 ⇒ **MEMORY 不更新**。
> **本块目标**：查清 `llm_rotate.sh`（`llm_pick` 定义处）到底在哪台机器、是否还存在，以及 loop 该在哪台跑。
> **只读**：不 kill / 不重启 / 不改文件。

```bash
set -u
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "[0] exec_host=$(hostname)  ips=$(hostname -I 2>/dev/null)  date=$(date '+%F %T')"
echo

echo "== A. loop 脚本第 45-52 行（llm_rotate.sh 加载处）=="
sed -n '45,52p' "$RUN/baize_harness_loop.sh" 2>/dev/null
echo

echo "== B. llm_rotate.sh 是否存在 =="
ls -l "$RUN/llm_rotate.sh" 2>&1
echo "  exist_test: $([ -f "$RUN/llm_rotate.sh" ] && echo YES || echo NO)"
echo

echo "== C. 全机搜 llm_rotate*（本机）=="
timeout 60 find /nas_train/app.e0031982 -maxdepth 6 -name 'llm_rotate*' -not -path '*/.git/*' 2>/dev/null | head -10
echo "  --- /tmp ---"
ls -l /tmp/llm_* 2>/dev/null | head -5
echo "  --- PATH 中 ---"
command -v llm_pick 2>&1 || echo "  llm_pick 不在 PATH"
echo

echo "== D. 两节点对比（.29 / .12 互相 ssh）=="
for h in 10.239.2.29 10.239.2.12; do
  echo "--- $h ---"
  timeout 30 ssh -n -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no app.e0031982@$h \
    "echo host=\$(hostname); echo -n 'llm_rotate='; [ -f $RUN/llm_rotate.sh ] && echo YES || echo NO; echo -n 'loop_procs='; pgrep -fc baize_harness_loop 2>/dev/null || echo 0" 2>&1 | sed 's/^/    /'
done
echo

echo "== E. 当前两节点 harness loop 进程 =="
for h in 10.239.2.29 10.239.2.12; do
  echo "--- $h ---"
  timeout 30 ssh -n -o BatchMode=yes -o ConnectTimeout=8 -o StrictHostKeyChecking=no app.e0031982@$h \
    "ps -eo pid,ppid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-150" 2>&1 | sed 's/^/    /'
done
echo

echo "== F. 本机 loop 日志（最近 30 行）=="
tail -n 30 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-190
echo

echo "== G. hit：loop 脚本对 llm_pick 的依赖与兜底 =="
grep -n 'llm_rotate\|llm_pick\|LLM_KEY\|CLINE_KEY' "$RUN/baize_harness_loop.sh" | cut -c1-170
echo

echo "（只读：未 kill / 未重启 / 未改文件）"
echo "=== DONE 296 | $(date '+%F %T') ==="
```

## RUN_ID 295 — **拉起已死的 harness loop（2026-11-28 09:0x · 用户令）**

> **用户令**：「启动一个已经死掉的 loop 有啥风险，已经不能更坏了」
> **依据**：RUN_ID 294 已确认 `baize_harness_loop` 进程数=0、日志文件不存在、`MEMORY_HARNESS.md` mtime 停在 11-27 16:41。
> **动作**：仅启动，不 kill 任何进程、不改任何配置、不动任何文件。
> **前置**：先复查确认仍为 0 个；若已有 1 个在跑则**不启动**（避免双实例）。

```bash
set -u
LOOP=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo

echo "== A. 前置复查 =="
if [ ! -f "$LOOP" ]; then echo "ABORT: loop 脚本不存在 $LOOP"; echo "=== DONE 295 (ABORT) ==="; exit 9; fi
echo "  script: $(stat -c '%s B  %y' "$LOOP")"
N=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)
echo "  existing_loop_count=$N"
if [ "$N" -gt 0 ]; then
  echo "SKIP: 已有 loop 在跑，不重复启动"
  ps -eo pid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-160
  echo "=== DONE 295 (SKIPPED) ==="; exit 0
fi
echo "  确认无 loop → 可以启动"
echo

echo "== B. 启动 =="
cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run || { echo "ABORT cd"; exit 9; }
setsid bash "$LOOP" > /tmp/baize_harness_loop.log 2>&1 < /dev/null &
NEWPID=$!
echo "  launched PID=$NEWPID"
sleep 15
echo

echo "== C. 启动后核验 =="
echo "  PID $NEWPID alive=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
echo "  loop_count_now=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)"
ps -eo pid,ppid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-160
echo

echo "== D. 日志（前 40 行，确认真的在推进）=="
if [ -f /tmp/baize_harness_loop.log ]; then
  echo "  log size=$(stat -c '%s' /tmp/baize_harness_loop.log) B"
  head -n 40 /tmp/baize_harness_loop.log | cut -c1-200
else
  echo "  WARN 日志未生成"
fi
echo

echo "== E. 等 60s 再确认未秒退 =="
sleep 60
echo "  after60s_alive=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
echo "  after60s_count=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)"
tail -n 15 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-200
echo

echo "（只启动，未 kill / 未改配置 / 未动文件）"
echo "=== DONE 295 | $(date '+%F %T') ==="
```

## RUN_ID 294 — **检查 harness agent loop 是否还在（只读 · 2026-11-28 09:0x）**

> **用户令**：「安排 .29 的 ops 中继看看 harness agent loop 是否还在」
> **背景**：harness 最后提交 2026-11-27 16:41（约 16h 前），`MEMORY_HARNESS.md` = `WAITING: 1`。
> **只读**：不 kill / 不重启 / 不改配置。只查进程、日志、状态。

```bash
set -u
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo

echo "== A. harness loop 进程 =="
ps -eo pid,ppid,etime,stat,rss,args | grep -E '[b]aize_harness_loop' | cut -c1-180
echo "  loop_count=$(pgrep -fc 'baize_harness_loop' 2>/dev/null || echo 0)"
echo

echo "== B. harness 的 cline 进程（loop 派生的）=="
ps -eo pid,ppid,etime,stat,rss,args | grep -E '[c]line ' | grep -iE 'harness' | cut -c1-180
echo "  (空=当前没有 cline 在跑)"
echo

echo "== C. 所有 cline 进程（含别线，用于分辨）=="
ps -eo pid,ppid,etime,rss,args | grep -E '[c]line --data-dir' | cut -c1-200
echo

echo "== D. harness loop 日志尾部 =="
for f in /tmp/baize_harness_loop.log /tmp/baize_harness.log; do
  if [ -f "$f" ]; then
    echo "--- $f  [$(stat -c '%y  %s B' "$f")]"
    tail -n 20 "$f" | cut -c1-200
  fi
done
echo

echo "== E. harness 相关其他日志 =="
ls -lt /tmp/*harness* 2>/dev/null | head -8 | awk '{print $6, $7, $8, $9}'
echo

echo "== F. MEMORY_HARNESS 状态 =="
grep -nE '^WAITING' "$RUN/MEMORY_HARNESS.md" 2>/dev/null
echo "  mtime: $(stat -c '%y' "$RUN/MEMORY_HARNESS.md" 2>/dev/null)"
echo "  size:  $(stat -c '%s' "$RUN/MEMORY_HARNESS.md" 2>/dev/null) B"
echo

echo "== G. opencode / 7-way 评测进程（harness 的任务对象）=="
ps -eo pid,etime,args | grep -E '[o]pencode|[s]webench|predict|launch_doubao' | cut -c1-170 | head -12
echo "  (空=harness 的评测任务当前无进程)"
echo

echo "== H. gw_proxy（harness 依赖的 9090/9091/9092）=="
ss -ltnp 2>/dev/null | grep -E ':909[0-2]' | cut -c1-140 || echo "  ss 不可用"
ps -eo pid,etime,args | grep -E '[g]w_proxy' | cut -c1-140 | head -5
echo

echo "== I. harness 相关文件 mtime（判断是否在动）=="
R=/nas_train/app.e0031982/code/super_intelligence_2035
ls -l --time-style=+%F_%T "$R/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md" 2>/dev/null | awk '{print $6, $7}'
ls -lt --time-style=+%F_%T "$R/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/" 2>/dev/null | head -5 | awk '{print $6, $7, $8}'
echo

echo "（只读：未 kill / 未重启 / 未改配置）"
echo "=== DONE 294 | $(date '+%F %T') ==="
```

## RUN_ID 293 — **🚀 执行 S2 切换（2026-11-28 09:4x · 用户令 · 16 卡已全空）**

> **背景**：RUN_ID 292 已停 S1（两节点进程=0，16 卡全 0MiB）。350k ckpt 完好（4.2G）。
> 用户令：「你来直接执行 S2 切换」。
> **本次直接启动**（不再走 s2_switch_executor.sh，因为它内含 rollback 逻辑）。
> **前置**：shim / S2 TSV / cursor / train.sh 四项必须存在，缺一即 abort 且**不启动 S1**。
> **启动后**：验证双节点 shim 生效 + 前若干 step 的 iter/loss/step/NaN。

```bash
set -u
LLM_HOME=/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm
BI=/nas_train/app.e0031982/code/BaiZe-ISEDA2027
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
TRAIN_SH=$LLM_HOME/scripts/train.sh
S2_TSV=$LLM_HOME/configs/blend_s2_preblend.tsv
CURSOR=$RUN/data/blendswitch/cursor_offsets_350k.json
SHIM=$BI/blend_hot_switch_bridge_compat.py
CKPTDIR=$BI/nemo_experiments/baize2b/checkpoints

echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo

echo "== A. 前置核验（缺一即 abort，绝不回退 S1）=="
FAIL=0
for f in "$TRAIN_SH" "$S2_TSV" "$CURSOR" "$SHIM"; do
  if [ -f "$f" ]; then echo "  OK   $(stat -c '%s B  %y' "$f")  $f"; else echo "  MISS $f"; FAIL=1; fi
done
CK=$(cat "$CKPTDIR/latest_checkpointed_iteration.txt" 2>/dev/null)
echo "  latest_ckpt=$CK"
[ -d "$CKPTDIR/iter_0${CK}" ] && echo "  OK   ckpt dir iter_0${CK}" || { echo "  MISS ckpt dir"; FAIL=1; }
echo "  shim_import=$(cd "$BI" && /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -c 'from blend_hot_switch_bridge_compat import apply_blend_cursor_offset_shim; print("SHIM_OK")' 2>&1 | tail -1)"
echo

echo "== B. 确认 16 卡全空 =="
echo "-- .29 --"; nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null
echo "-- .12 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "nvidia-smi --query-gpu=index,memory.used --format=csv,noheader" 2>&1 | sed 's/^/  .12| /'
echo "  残留进程 .29=$(ps -eo args= | grep -cE '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun')"
echo

if [ "$FAIL" != "0" ]; then
  echo "ABORT: 前置不全，未启动任何训练"
  echo "=== DONE 293 (ABORTED) | $(date '+%F %T') ==="
  exit 9
fi

echo "== C. 启动 S2（从 350k resume，S2 TSV + cursor offsets）=="
cd "$LLM_HOME" || { echo "ABORT cd failed"; exit 9; }
export BLEND_TSV="$S2_TSV"
export BLEND_CURSOR_OFFSETS_JSON="$CURSOR"
echo "  BLEND_TSV=$BLEND_TSV"
echo "  BLEND_CURSOR_OFFSETS_JSON=$BLEND_CURSOR_OFFSETS_JSON"
setsid bash "$TRAIN_SH" s1 > /tmp/baize_s2_launch.log 2>&1 < /dev/null &
NEWPID=$!
echo "  S2 launch PID=$NEWPID"
echo

echo "== D. 启动后 60s 存活检查 =="
sleep 60
if kill -0 "$NEWPID" 2>/dev/null; then echo "  PID $NEWPID ALIVE after 60s OK"; else echo "  PID $NEWPID DIED <60s"; fi
echo "  launcher .29=$(ps -eo args= | grep -cE '[p]retrain_launcher')"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "echo .12_launcher=\$(ps -eo args= | grep -cE '[p]retrain_launcher')" 2>&1 | sed 's/^/  .12| /'
echo "-- launch log tail --"
tail -n 25 /tmp/baize_s2_launch.log 2>/dev/null | cut -c1-210
echo

echo "== E. GPU 占用（应看到两节点都在吃显存）=="
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null | head -8
echo

echo "== F. 等 240s 再看训练是否进入 step =="
sleep 240
echo "-- worker log --"
tail -n 6 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-215
echo "-- shim 生效证据 (双节点) --"
echo "  .29: $(grep -ci 'blend.hot.switch' /tmp/baize_s1_baize2b_worker.log 2>/dev/null) 行"
grep -i 'blend.hot.switch' /tmp/baize_s1_baize2b_worker.log 2>/dev/null | tail -3 | cut -c1-200
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "echo '  .12: '\$(grep -ci 'blend.hot.switch' /tmp/baize_s1_baize2b_master.log 2>/dev/null) 行; grep -i 'blend.hot.switch' /tmp/baize_s1_baize2b_master.log 2>/dev/null | tail -3 | cut -c1-200" 2>&1 | sed 's/^/  .12| /'
echo

echo "== G. 健康判据 =="
IT=$(tail -20 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | grep -oP 'iteration\s+\K\d+' | tail -1)
LS=$(tail -20 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | grep -oP 'lm loss:\s+\K[\d.E+]+' | tail -1)
ST=$(tail -20 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | grep -oP 'elapsed time per iteration \(ms\):\s+\K[\d.]+' | tail -1)
NN=$(tail -20 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | grep -oP 'nan iterations:\s+\K\d+' | tail -1)
echo "  iter=$IT  loss=$LS  step_ms=$ST  nan=$NN"
echo "  (期望: iter>=350000 resume 起点, nan=0, step<=7400ms)"
echo "  S2_PID=$NEWPID"
echo
echo "（未启动 S1 · 未动别线 · 未改配置）"
echo "=== DONE 293 | $(date '+%F %T') ==="
```

## RUN_ID 292 — **🔴 立刻停止 S1 训练（2026-11-28 09:3x · 用户令）**

> **用户原话**：「让 pretrain 立刻把 S1 训练停下」
> **目标**：`.29` + `.12` 两节点的 S1 训练全部停下，**不要重启 S1**。
> **顺序**：先确认 ckpt 安全 → 记录停止前状态 → 停 daemon（避免 restart）→ 停训练 → 记录杀掉的 PID。
> **注意**：`.29` 与 `.12` 共享 NFS 工作副本，本命令**在任一中继执行**，会对另一节点做 bounded ssh。
> **不要动**：别的线进程、GPU0-3 上的 root 服务、文件。

```bash
set -u
R=/nas_train/app.e0031982/code/super_intelligence_2035
H=$(hostname)
echo "[0] exec_host=$H  date=$(date '+%F %T')"
echo

echo "== A. 停止前：真实训练进度与 ckpt 安全 =="
tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-210
CK=$(cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)
echo "latest_ckpt_iter=$CK"
ls -d /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0${CK} 2>/dev/null && echo "ckpt_dir_exists=YES"
echo "ckpt_disk=$(du -sh /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0${CK} 2>/dev/null | awk '{print $1}')"
echo "ckpt_mtime=$(stat -c '%y' /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)"
echo

echo "== B. 停止前：训练进程清单（两节点）=="
echo "-- .29 --"
ps -eo pid,etime,args | grep -E '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun' | cut -c1-160
echo "-- .12 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "ps -eo pid,etime,args | grep -E '[p]retrain_launcher|[t]orchrun' | cut -c1-160" 2>&1 | sed 's/^/  .12| /'
echo

echo "== C. 先杀 eval daemon（防止它把训练重新拉起）=="
for p in $(ps -eo pid,args= | grep 'baize_l1_autoqueue_continuous' | grep -v grep | awk '{print $1}'); do
  echo "  kill daemon PID=$p"; kill "$p" 2>/dev/null; sleep 2; kill -9 "$p" 2>/dev/null
done
pgrep -f 'llama-server' 2>/dev/null | xargs -r kill 2>/dev/null
echo "  daemon cleaned"
echo

echo "== D. 停 .29 训练 =="
for p in $(ps -eo pid,args= | grep -E 'train\.sh s1' | grep -v grep | awk '{print $1}'); do
  echo "  kill train.sh PID=$p"; kill "$p" 2>/dev/null
done
sleep 6
for p in $(ps -eo pid,args= | grep -E 'train\.sh s1' | grep -v grep | awk '{print $1}'); do
  echo "  kill -9 train.sh PID=$p"; kill -9 "$p" 2>/dev/null
done
sleep 4
for p in $(ps -eo pid,args= | grep -E '[p]retrain_launcher\.py|[t]orchrun' | grep -v grep | awk '{print $1}'); do
  echo "  kill -9 local PID=$p"; kill -9 "$p" 2>/dev/null
done
echo

echo "== E. 停 .12 训练 =="
timeout 90 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 '
  for p in $(ps -eo pid,args= | grep -E "[p]retrain_launcher|[t]orchrun" | awk "{print \$1}"); do
    echo "  .12 kill -9 PID=$p"; kill -9 "$p" 2>/dev/null
  done
  sleep 3
  echo "  .12 remaining=$(ps -eo args= | grep -cE "[p]retrain_launcher|[t]orchrun")"
' 2>&1 | sed 's/^/  .12| /'
echo

echo "== F. 停止后核验 =="
sleep 8
echo "-- .29 残留进程 --"
ps -eo pid,etime,args | grep -E '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun' | cut -c1-160 || echo "  (none)"
echo "  .29_still_running=$(ps -eo args= | grep -cE '[t]rain\.sh s1|[p]retrain_launcher|[t]orchrun')"
echo "-- .12 残留进程 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "ps -eo args= | grep -cE '[p]retrain_launcher|[t]orchrun'" 2>&1 | sed 's/^/  .12_count=/'
echo
echo "-- GPU（确认已释放，给 S2 切换让路）--"
nvidia-smi --query-gpu=index,memory.used --format=csv,noheader 2>/dev/null
echo "-- .12 --"
timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
  "nvidia-smi --query-gpu=index,memory.used --format=csv,noheader" 2>&1 | sed 's/^/  .12| /'
echo

echo "== G. 确认没有 self-restart =="
sleep 10
echo "  .29_after10s=$(ps -eo args= | grep -cE '[t]rain\.sh s1|[p]retrain_launcher')"
echo "  (0 = 已停稳，未被自动拉起)"
echo
echo "（未重启 S1 · 未动别线 · 未改配置）"
echo "=== DONE 292 | $(date '+%F %T') ==="
```

## RUN_ID 291 — **pretrain / data 静默体检（只读 · 2026-11-24 22:4x）**

> 背景：pretrain 自 **19:17**、data 自 **19:57** 起无新提交（静默 2.5–3.2h，常态 10–20min/条），
> 怀疑 ① loop 已死 ② `git push` 失败（.12 的 github 需要代理 92.23）③ `.git/index` 损坏 / `index.lock` 残留 ④ NFS D-state。
> 另：`.29` 与 `.12` 共享同一 NFS 工作副本，**本令不设 TARGET（任一中继可执行）；命令可能落在任一台**；本块会打印 `exec_host` 并对另一台做 bounded ssh。
> **只读**：不 kill / 不重启 / 不改配置 / 不删文件。

```bash
set -u
echo "[0] exec_host=$(hostname)  date=$(date '+%F %T')"
echo
echo "== A. 本机基础 =="
uptime
free -g | awk '/Mem:/{print "mem_used="$3"G / "$2"G"}'
df -h /home /nas_train 2>/dev/null | tail -3
echo "DSTATE=$(ps -eo stat= | cut -c1 | grep -c D)"
echo
echo "== B. 进程（pretrain / data / relay / loop）=="
ps -eo pid,ppid,etime,stat,pcpu,rss,args | grep -E 'baize_|torchrun|pretrain_gpt|megatron|blend|data_loop|ops_relay|watch_.*_loop' | grep -v grep | cut -c1-170 | head -25
echo
echo "== C. GPU（若有）=="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null | head -8 || echo "  no nvidia-smi"
echo
echo "== D. 关键日志尾部（含 push 错误）=="
for f in /tmp/baize_pretrain_loop.log /tmp/baize_data_loop.log /tmp/baize_ops_relay.29.log /tmp/baize_ops_relay.12.log; do
  if [ -f "$f" ]; then
    echo "--- $f  [$(stat -c '%y  %s B' "$f")]"
    tail -n 6 "$f" | cut -c1-200
  fi
done
echo "-- 最近 push/git 错误 --"
grep -hE 'push FAILED|rejected|Network is unreachable|index\.lock|smaller than expected|fatal:' \
  /tmp/baize_pretrain_loop.log /tmp/baize_data_loop.log 2>/dev/null | tail -8 | cut -c1-200
echo
echo "== E. 共享仓状态 =="
R=/nas_train/app.e0031982/code/super_intelligence_2035
ls -l "$R/.git/index" "$R/.git/index.lock" 2>/dev/null
if [ -d "$R/.git/rebase-merge" ]; then echo "WARN rebase-merge 残留"; else echo "no rebase-merge"; fi
cd "$R" 2>/dev/null && {
  git log -1 --format='HEAD %h %ad %s' --date=iso
  echo "dirty=$(git status --porcelain | wc -l)  ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
  git status -sb | head -3
}
echo "-- 本线关键文件 mtime --"
ls -l --time-style=+%F_%T "$R/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md" \
                        "$R/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md" \
                        "$R/doc/BaiZe-ISEDA2027/run/reports/report_pretrain_llamacpp_scaling_zh.html" 2>/dev/null \
  | awk '{print $6, $7}'
echo
echo "== F. pretrain 训练实况 =="
H=$(hostname)
if echo "$H" | grep -q '29$'; then
  echo "  (local on .29)"
  tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200
  ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt' | cut -c1-140 | head -5
else
  timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.29 \
    "tail -n 3 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200; ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt' | cut -c1-140 | head -5" 2>&1 \
    | sed 's/^/  .29| /' | head -12
  echo "  .29_ssh_rc=$?"
fi
echo
echo "== G. data 线实况 =="
if echo "$H" | grep -q '12$' && ! echo "$H" | grep -q 's0pgpuap12'; then
  echo "  (local on .12)"
  tail -n 6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-200
  ps -eo pid,etime,args | grep -E '[d]ata_loop|[b]lend' | cut -c1-140 | head -5
else
  timeout 60 ssh -o BatchMode=yes -o ConnectTimeout=10 -o StrictHostKeyChecking=no app.e0031982@10.239.2.12 \
    "tail -n 6 /tmp/baize_data_loop.log 2>/dev/null | cut -c1-200; ps -eo pid,etime,args | grep -E '[d]ata_loop|[b]lend' | cut -c1-140 | head -5" 2>&1 \
    | sed 's/^/  .12| /' | head -12
  echo "  .12_ssh_rc=$?"
fi
echo
echo "== H. github 连通性（.12 需要代理 92.23）=="
timeout 15 curl -sS -o /dev/null -w "github=%{http_code}\n" https://github.com 2>&1 | tail -1
echo
echo "（只读：未 kill / 未重启 / 未改配置）"
echo "=== DONE 291 | $(date '+%F %T') ==="
```
