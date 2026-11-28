
---

## RUN_ID 302 · 2026-11-28 22:15:30 · host=`s0pgpuap12` · exit=0

**命令**
```bash
echo "[0] host=$(hostname) date=$(date '+%F %T')"
W=/tmp/baize_s1_baize2b_worker.log
ls -l --time-style=+%F_%T "$W" /tmp/baize_s1_baize2b_master.log 2>/dev/null
echo "--- worker tail 12 ---"
tail -n 12 "$W" 2>/dev/null | cut -c1-220
echo "--- 最近 5 条 iter ---"
grep -E 'iteration[ =]|iter[ =]' "$W" 2>/dev/null | tail -5 | cut -c1-220
echo "--- nan_hits=$(grep -ci 'nan' "$W" 2>/dev/null || echo 0)  skip_hits=$(grep -ci 'skip' "$W" 2>/dev/null || echo 0)  blend_switch_hits=$(grep -ci 'blend.hot.switch' "$W" 2>/dev/null || echo 0) ---"
echo "=== DONE 302 | $(date '+%F %T') ==="
```

**输出**
```
[0] host=s0pgpuap12 date=2026-11-28 22:15:31
--- worker tail 12 ---
--- 最近 5 条 iter ---
--- nan_hits=0  skip_hits=0  blend_switch_hits=0 ---
=== DONE 302 | 2026-11-28 22:15:32 ===
```


---

## RUN_ID 291 · 2026-11-25 08:37:11 · host=`whag0pgpuap12` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap12  date=2026-11-25 08:37:11

== A. 本机基础 ==
 08:37:11 up 298 days, 17:19,  2 users,  load average: 40.18, 36.37, 31.00
mem_used=666G / 2015G
Filesystem                     Size  Used Avail Use% Mounted on
/dev/mapper/vgroot-lv_home     196G  155G   31G  84% /home
10.239.22.31:/vol_CTE0_data01  207T  184T   24T  89% /nas_train
DSTATE=0

== B. 进程（pretrain / data / relay / loop）==
1032513       1 31-13:02:46 Ss    0.0  3460 bash ./ops_relay_v2.sh
1439817 1439816  4-17:55:25 Ssl   0.1 276752 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nnodes=
1453120 1439817  4-17:55:13 Ssl   149 22218120 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453121 1439817  4-17:55:13 Ssl   146 22172388 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453122 1439817  4-17:55:13 Ssl   148 21890540 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453123 1439817  4-17:55:13 Rsl   150 21895104 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453124 1439817  4-17:55:13 Ssl   134 21788048 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453125 1439817  4-17:55:13 Ssl   136 21805048 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453126 1439817  4-17:55:13 Ssl   136 21790248 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1453127 1439817  4-17:55:13 Ssl   138 21788916 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1597712 1943222       01:55 Sl    0.0 35644 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/s
1597803 1597712       01:55 Sl   30.5 367396 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train
1706427 1453120  4-17:51:42 Sl    9.9 38541924 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1707045 1453120  4-17:51:42 Sl   10.2 38063408 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1707444 1453120  4-17:51:42 Sl   10.2 40109596 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1707834 1453120  4-17:51:42 Sl   10.5 36678880 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1708218 1453120  4-17:51:42 Sl   10.3 38969144 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1708585 1453120  4-17:51:42 Sl   10.5 38096884 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1708761 1453120  4-17:51:42 Sl   10.0 37804604 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1708929 1453120  4-17:51:42 Sl   10.4 36642580 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1748210 1032513       00:00 S     0.0  1820 bash ./ops_relay_v2.sh
1753943 1453127  4-17:51:04 Sl    9.0 42616648 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1753944 1453127  4-17:51:04 Sl    9.7 44729900 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1753945 1453127  4-17:51:04 Sl    9.4 35568844 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
1753946 1453127  4-17:51:04 Sl    9.7 40938376 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr

== C. GPU（若有）==
0, 96 %, 75627 MiB, 57
1, 100 %, 75183 MiB, 62
2, 100 %, 75181 MiB, 59
3, 100 %, 75067 MiB, 63
4, 100 %, 75051 MiB, 57
5, 100 %, 74595 MiB, 64
6, 100 %, 74819 MiB, 57
7, 100 %, 74971 MiB, 61

== D. 关键日志尾部（含 push 错误）==
--- /tmp/baize_data_loop.log  [2026-11-25 08:37:11.211526181 +0800  111398178 B]
[2m[thinking] [0m[2mThe[0m[2m merge has[0m[2m conflicts on[0m[2m personal[0m[2m-watch files ([0m[2mnot[0m[2m data agent files).[0m[2m These are modify/delete[0m[2m conflicts where[

Actually[0m[2m, looking[0m[2m at this[0m[2m more carefully:[0m[2m "[0m[2mdeleted in HEAD and[0m[2m modified in eba[0m[2mab9e90[0m[2m..."[0m[2m - HEAD[0m[2m is our[0m[2m local com

Let me resolve by[0m[2m keeping[0m[2m the remote version[0m[2m for all conflicting[0m[2m files.[0m
The conflicts are all in `doc/personal-watch/` — not data agent files. The local commit deleted them but remote modified them. I'll accept the remote versions and complete the merge.
--- /tmp/baize_ops_relay.12.log  [2026-11-25 08:33:44.674305313 +0800  3655 B]
./ops_relay_v2.sh: line 77: 1323933 Bus error               (core dumped) git pull --rebase --autostash origin main > /dev/null 2>&1
./ops_relay_v2.sh: line 77: 822557 Bus error               (core dumped) git pull --rebase --autostash origin main > /dev/null 2>&1
[relay-12] RUN_ID=291 executed, exit=0, appended to outbox.
[relay-12] push FAILED (will retry next cycle)
[relay-12] RUN_ID=291 executed, exit=0, appended to outbox.
[relay-12] push FAILED (will retry next cycle)
-- 最近 push/git 错误 --
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Exiting because of an unresolved conflict.
fatal: Unable to create '/nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock': File exists.

== E. 共享仓状态 ==
-rw-r--r-- 1 app.e0031982 app.adm 30490 Nov 25 08:37 /nas_train/app.e0031982/code/super_intelligence_2035/.git/index
no rebase-merge
HEAD 2be0088aff 2026-11-24 20:00:17 +0800 zhulong eval wake#2012: doubao-pro 3-run r1 收口=5.44% valid + r2 VOID(hub 过载) + r2r3 续跑(hub-restart+strict canary 修复)
dirty=865  ahead_behind=1	246
## main...origin/main [ahead 1, behind 246]
A  doc/BaiZe-ISEDA2027/daily-memories-posttrain/2026-11-25.md
DU doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md
-- 本线关键文件 mtime --
2026-11-25_08:35:12 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md
2026-11-25_08:35:12 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md

== F. pretrain 训练实况 ==
  .29|  [2026-11-25 08:33:52] iteration   316760/  700000 | consumed samples:     81090560 | elapsed time per iteration (ms): 7416.3 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9885
  .29|  [2026-11-25 08:35:07] iteration   316770/  700000 | consumed samples:     81093120 | elapsed time per iteration (ms): 7473.4 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9826
  .29|  [2026-11-25 08:36:23] iteration   316780/  700000 | consumed samples:     81095680 | elapsed time per iteration (ms): 7607.6 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9830
  .29|  310443       06:07 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/Bai
  .29| 2547366  4-17:55:56 bash -c cd /nas_train/app.e0031982/code/baize-llm && setsid bash scripts/train.sh s1 > /tmp/baize_s1_launch.log 2>&1 < /
  .29| 2547367  4-17:55:56 bash scripts/train.sh s1
  .29_ssh_rc=0

== G. data 线实况 ==
  (local on .12)
DeprecationWarning: AI SDK Warning (openai-compatible.chat / glm-5.2): Deprecated: "providerOptions key 'openai-compatible'". Use 'openaiCompatible' instead.
      at SX (/$bunfs/root/chunk-mbnfmz12.js:24:45839)
      at uZ (/$bunfs/root/chunk-mbnfmz12.js:24:46138)
      at transform (/$bunfs/root/chunk-mbnfmz12.js:42:42571)

   [90m⎿ [0m[2mdoc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md doc/BaiZe-ISEDA2027/run/MEMORY_VI... (+1 more)[0m
1439817  4-17:55:27 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nn
1453120  4-17:55:15 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
1453121  4-17:55:15 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
1453122  4-17:55:15 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
1453123  4-17:55:15 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas

== H. github 连通性（.12 需要代理 92.23）==
github=000

（只读：未 kill / 未重启 / 未改配置）
=== DONE 291 | 2026-11-25 08:37:13 ===
```

---

## RUN_ID 291 · 2026-11-25 08:37:37 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  date=2026-11-25 08:37:37

== A. 本机基础 ==
 08:37:37 up 4 days, 18:33,  4 users,  load average: 23.38, 24.94, 23.98
mem_used=665G / 2015G
Filesystem                     Size  Used Avail Use% Mounted on
/dev/mapper/vgroot-lv_home     196G  143G   44G  77% /home
10.239.23.31:/vol_CTE0_data01  207T  184T   24T  89% /nas_train
DSTATE=0

== B. 进程（pretrain / data / relay / loop）==
  45764       1  4-16:35:46 Ss    0.0  3956 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
 310443 1475330       06:32 Sl   23.6 483128 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-IS
 457879 1081392       04:34 S     0.0  1064 tee -a /tmp/baize_l1_autoqueue_continuous.log
 782229 1479210       00:01 S     0.0  2092 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops_relay.sh
1081392       1  3-12:39:56 Ss    0.0  3872 bash /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/eval/baize_l1_autoqueue_continuous.sh
1475330       1  4-18:11:02 Ss    0.0  3728 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh
1479210       1  4-18:11:00 Ss    0.0  3684 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops_relay.sh
2547366       1  4-17:56:21 S     0.0    64 bash -c cd /nas_train/app.e0031982/code/baize-llm && setsid bash scripts/train.sh s1 > /tmp/baize_s1_launch.log 2>&1 < /dev/nu
2579711 2547367  4-17:55:53 S     0.0  8484 ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o BatchMode=yes 10.239.2.12 ulimit -n 65536 && cd /nas_train/app
2588244 2547367  4-17:55:42 Sl    0.1 162056 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nnodes=
2601324 2588244  4-17:55:40 Rsl   131 30451888 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601327 2588244  4-17:55:40 Rsl   130 29903480 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601330 2588244  4-17:55:40 Rsl   141 30246444 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601331 2588244  4-17:55:40 Rsl   143 30448540 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601334 2588244  4-17:55:40 Rsl   132 30475876 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601335 2588244  4-17:55:40 Rsl   131 30061392 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601338 2588244  4-17:55:40 Rsl   140 30241904 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2601340 2588244  4-17:55:40 Rsl   143 30392036 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904976 2601335  4-17:51:29 Sl    8.2 41196444 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904977 2601334  4-17:51:29 Sl    8.8 41855488 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904978 2601338  4-17:51:29 Sl    8.2 40531272 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904979 2601340  4-17:51:29 Sl    8.3 40715644 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904980 2601327  4-17:51:29 Sl    9.2 46250224 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904981 2601331  4-17:51:29 Sl    9.3 47641476 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr
2904982 2601324  4-17:51:29 Sl    9.3 47308684 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas_tr

== C. GPU（若有）==
0, 100 %, 74501 MiB, 56
1, 100 %, 74713 MiB, 61
2, 100 %, 74657 MiB, 57
3, 100 %, 74915 MiB, 61
4, 97 %, 74959 MiB, 58
5, 97 %, 74713 MiB, 60
6, 89 %, 74957 MiB, 58
7, 100 %, 74699 MiB, 60

== D. 关键日志尾部（含 push 错误）==
--- /tmp/baize_pretrain_loop.log  [2026-11-25 08:37:38.333980299 +0800  57083144 B]
2[0m[2m. Check if[0m[2m MEMORY is git[0m[2mignored
3.[0m[2m Check the report[0m[2m content (is it[0m[2m stale?)
4.[0m[2m Calculate[0m[2m the[0m[2m step time trend[0m[2m
5. Update[0m[2m MEMORY with heartbeat[0m[2m

Actually[0m[2m, I should[0m[2m also do[0m[2m a `[0m[2mgit pull` to[0m[2m get the[0m[2m latest changes[0m[2m ([0m[2mwe[0m[2m're behind 24[0m[2m6 commits). But[0m[2m I need to be[
-- 最近 push/git 错误 --
Push rejected - remote has new commits. Let me pull --rebase and push again.
   [90m⎿ [0m[2m[Command exited with code 128]  [stderr] fatal: Unable to create '/nas_train/...[0m
[36m[run_commands][0m ls -la /nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock 2>&1; pgrep -a 'git' | head -5
   [90m⎿ [0m[2m[Command exited with code 128]  [stderr] fatal: Unable to create '/nas_train/...[0m
[36m[run_commands][0m sleep 5 && ls /nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock 2>&1 || echo 'lock gone'
   [90m⎿ [0m[2mfatal: No rebase in progress?[0m
[2m[thinking] [0m[2mThe[0m[2m push[0m[2m was rejected because the[0m[2m remote has new[0m[2m commits. I need[0m[2m to pull first and[0m[2m re[0m[2mbase. The[0m[2m earlier pull[0m[
   [90m⎿ [0m[2mfatal: Cannot rebase onto multiple branches.[0m

== E. 共享仓状态 ==
-rw-r--r-- 1 app.e0031982 app.adm 30208 Nov 25 08:37 /nas_train/app.e0031982/code/super_intelligence_2035/.git/index
no rebase-merge
HEAD 2be0088aff 2026-11-24 20:00:17 +0800 zhulong eval wake#2012: doubao-pro 3-run r1 收口=5.44% valid + r2 VOID(hub 过载) + r2r3 续跑(hub-restart+strict canary 修复)
dirty=867  ahead_behind=1	246
## main...origin/main [ahead 1, behind 246]
AD doc/BaiZe-ISEDA2027/daily-memories-posttrain/2026-11-25.md
A  doc/BaiZe-ISEDA2027/run/MEMORY_POSTTRAIN.md
-- 本线关键文件 mtime --
2026-11-25_08:35:12 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md
2026-11-25_08:35:12 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md

== F. pretrain 训练实况 ==
  (local on .29)
 [2026-11-25 08:35:07] iteration   316770/  700000 | consumed samples:     81093120 | elapsed time per iteration (ms): 7473.4 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9826
 [2026-11-25 08:36:23] iteration   316780/  700000 | consumed samples:     81095680 | elapsed time per iteration (ms): 7607.6 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9830
 [2026-11-25 08:37:36] iteration   316790/  700000 | consumed samples:     81098240 | elapsed time per iteration (ms): 7325.6 | learning rate: 1.000000E-03 | global batch size:   256 | lm loss: 1.9787
 310443       06:32 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/Bai
2547366  4-17:56:21 bash -c cd /nas_train/app.e0031982/code/baize-llm && setsid bash scripts/train.sh s1 > /tmp/baize_s1_launch.log 2>&1 < /
2547367  4-17:56:21 bash scripts/train.sh s1

== G. data 线实况 ==
  .12|    [90m⎿ [0m[2m"doc/personal-watch/run/news/toutiao/\345\217\260\350\264\246.md" "doc/person...[0m
  .12| [2m[thinking] [0m[2mThe[0m[2m files with[0m[2m Chinese names[0m[2m are still showing as[0m[2m unresolved[0m[2m. Let me try[0m[2m a[0m[2m different approach -[0m[2m use git add[0m[
  .12| 
  .12| Actually, the issue[0m[2m might be that these[0m[2m files don[0m[2m't actually[0m[2m exist on disk ([0m[2mthey were deleted locally[0m[2m and modified[0m[2m remotely,[0m[2m so[0m[2m 
  .12| 
  .12| Wait, for[0m[2m modify/delete conflicts ([0m[2mDU), the file[0m[2m exists[0m[2m in the working tree[0m[2m (from the remote[0m[2m side). The problem[0m[2m is that the file[0m[2m path co
  .12| 1439817  4-17:55:53 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nn
  .12| 1453120  4-17:55:41 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
  .12| 1453121  4-17:55:41 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
  .12| 1453122  4-17:55:41 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
  .12| 1453123  4-17:55:41 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python -u pretrain_launcher.py --arch mamba2 --name baize2b --dir /nas
  .12_ssh_rc=0

== H. github 连通性（.12 需要代理 92.23）==
github=200

（只读：未 kill / 未重启 / 未改配置）
=== DONE 291 | 2026-11-25 08:37:40 ===
```

---

## RUN_ID 292 · 2026-11-28 08:00:57 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  date=2026-11-28 08:00:57

== A. 停止前：真实训练进度与 ckpt 安全 ==
  warnings.warn('resource_tracker: There appear to be %d '
/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/multiprocessing/resource_tracker.py:224: UserWarning: resource_tracker: There appear to be 3 leaked semaphore objects to clean up at shutdown
  warnings.warn('resource_tracker: There appear to be %d '
latest_ckpt_iter=350000
/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0350000
ckpt_dir_exists=YES
ckpt_disk=4.2G
ckpt_mtime=2026-11-28 05:18:17.145762320 +0800

== B. 停止前：训练进程清单（两节点）==
-- .29 --
3912946       04:24 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --a
-- .12 --
  .12| 2405252 13-16:22:04 bash -c cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>&1; echo "

== C. 先杀 eval daemon（防止它把训练重新拉起）==
  kill daemon PID=3912946
  daemon cleaned

== D. 停 .29 训练 ==

== E. 停 .12 训练 ==
  .12|   .12 kill -9 PID=2405252
  .12|   .12 remaining=0

== F. 停止后核验 ==
-- .29 残留进程 --
  .29_still_running=0
-- .12 残留进程 --
  .12_count=0

-- GPU（确认已释放，给 S2 切换让路）--
0, 0 MiB
1, 0 MiB
2, 0 MiB
3, 0 MiB
4, 0 MiB
5, 0 MiB
6, 0 MiB
7, 0 MiB
-- .12 --
  .12| 0, 0 MiB
  .12| 1, 0 MiB
  .12| 2, 0 MiB
  .12| 3, 0 MiB
  .12| 4, 0 MiB
  .12| 5, 0 MiB
  .12| 6, 4 MiB
  .12| 7, 4 MiB

== G. 确认没有 self-restart ==
  .29_after10s=0
  (0 = 已停稳，未被自动拉起)

（未重启 S1 · 未动别线 · 未改配置）
=== DONE 292 | 2026-11-28 08:01:34 ===
```

---

## RUN_ID 292 · 2026-11-28 08:01:14 · host=`whag0pgpuap12` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap12  date=2026-11-28 08:01:14

== A. 停止前：真实训练进度与 ckpt 安全 ==
latest_ckpt_iter=350000
/nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/iter_0350000
ckpt_dir_exists=YES
ckpt_disk=4.2G
ckpt_mtime=2026-11-28 05:18:17.145762320 +0800

== B. 停止前：训练进程清单（两节点）==
-- .29 --
-- .12 --

== C. 先杀 eval daemon（防止它把训练重新拉起）==
  daemon cleaned

== D. 停 .29 训练 ==

== E. 停 .12 训练 ==
  .12|   .12 remaining=0

== F. 停止后核验 ==
-- .29 残留进程 --
  .29_still_running=0
-- .12 残留进程 --
  .12_count=0

-- GPU（确认已释放，给 S2 切换让路）--
0, 0 MiB
1, 0 MiB
2, 0 MiB
3, 0 MiB
4, 0 MiB
5, 0 MiB
6, 4 MiB
7, 4 MiB
-- .12 --
  .12| 0, 0 MiB
  .12| 1, 0 MiB
  .12| 2, 0 MiB
  .12| 3, 0 MiB
  .12| 4, 0 MiB
  .12| 5, 0 MiB
  .12| 6, 4 MiB
  .12| 7, 4 MiB

== G. 确认没有 self-restart ==
  .29_after10s=0
  (0 = 已停稳，未被自动拉起)

（未重启 S1 · 未动别线 · 未改配置）
=== DONE 292 | 2026-11-28 08:01:47 ===
```

---

## RUN_ID 293 · 2026-11-28 08:06:04 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  date=2026-11-28 08:06:04

== A. 前置核验（缺一即 abort，绝不回退 S1）==
  OK   14778 B  2026-11-27 10:08:59.034326875 +0800  /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh
  OK   3625 B  2026-11-25 09:09:38.184548002 +0800  /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/configs/blend_s2_preblend.tsv
  OK   1093 B  2026-11-27 09:25:19.735170452 +0800  /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json
  OK   4226 B  2026-11-27 09:21:29.370543534 +0800  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/blend_hot_switch_bridge_compat.py
  latest_ckpt=350000
  OK   ckpt dir iter_0350000
  shim_import=SHIM_OK

== B. 确认 16 卡全空 ==
-- .29 --
0, 0 MiB
1, 0 MiB
2, 0 MiB
3, 0 MiB
4, 0 MiB
5, 0 MiB
6, 0 MiB
7, 0 MiB
-- .12 --
  .12| 0, 0 MiB
  .12| 1, 0 MiB
  .12| 2, 0 MiB
  .12| 3, 0 MiB
  .12| 4, 0 MiB
  .12| 5, 0 MiB
  .12| 6, 4 MiB
  .12| 7, 4 MiB
  残留进程 .29=1

== C. 启动 S2（从 350k resume，S2 TSV + cursor offsets）==
  BLEND_TSV=/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/configs/blend_s2_preblend.tsv
  BLEND_CURSOR_OFFSETS_JSON=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/blendswitch/cursor_offsets_350k.json
  S2 launch PID=428912

== D. 启动后 60s 存活检查 ==
  PID 428912 DIED <60s
  launcher .29=1
  .12| .12_launcher=0
-- launch log tail --
[2026-11-28 08:06:09] WARN: launcher 无 --max-position-embeddings（训练不受影响，RoPE 逐位置计算）；导出 HF config 时必须写 max_position_embeddings=1048576，由 scripts/check_rope.py 把�
[2026-11-28 08:06:10] TensorBoard 已在运行 pid=2571921（端口 6006）
--- TensorBoard @ 2026-11-28 08:06:10 ---
  host/port : whag0pgpuap29 / 6006 (bind 0.0.0.0)
  pid       : 2571921
  logdir    : /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments
  listen    : LISTEN 0 128 0.0.0.0:6006 0.0.0.0:* 
  http      : 200
  events    :
      2026-11-28 07:55      615562  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795815979.whag0pgpuap29.2245446.0
      2026-11-28 05:30       14596  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795814828.whag0pgpuap29.780408.0
      2026-11-28 05:18    50221762  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795157328.whag0pgpuap29.2601340.0
      2026-11-20 01:22     9728818  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794982260.whag0pgpuap29.3800664.0
      2026-11-18 13:56       45844  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794980435.whag0pgpuap29.1801089.0
  log tail  :
      NOTE: Using experimental fast data loading logic. To disable, pass
          "--load_fast=false" and report issues on GitHub. More details:
          https://github.com/tensorflow/tensorboard/issues/4784
      
      TensorBoard 2.20.0 at http://0.0.0.0:6006/ (Press CTRL+C to quit)
[2026-11-28 08:06:10] rank0 @ 10.239.2.12（后台 ssh）
[2026-11-28 08:06:20] rank1 @ whag0pgpuap29（前台）
[2026-11-28 08:06:20] 结束：worker_rc=126 master_rc=126
[2026-11-28 08:06:20] 日志：/tmp/baize_s1_baize2b_worker.log / /tmp/baize_s1_baize2b_master.log ；摘要：/tmp/baize_s1_baize2b.log
  | /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh: line 282: /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun: Argument list too long

== E. GPU 占用（应看到两节点都在吃显存）==
0, 0 MiB
1, 0 MiB
2, 0 MiB
3, 0 MiB
4, 0 MiB
5, 0 MiB
6, 0 MiB
7, 0 MiB

== F. 等 240s 再看训练是否进入 step ==
-- worker log --
/nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh: line 282: /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun: Argument list too long
-- shim 生效证据 (双节点) --
  .29: 0 行
  .12|   .12: 0 行

== G. 健康判据 ==
  iter=  loss=  step_ms=  nan=
  (期望: iter>=350000 resume 起点, nan=0, step<=7400ms)
  S2_PID=428912

（未启动 S1 · 未动别线 · 未改配置）
=== DONE 293 | 2026-11-28 08:11:07 ===
```

---

## RUN_ID 294 · 2026-11-28 08:53:17 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  date=2026-11-28 08:53:17

== A. harness loop 进程 ==
  loop_count=0
0

== B. harness 的 cline 进程（loop 派生的）==
1800276 1475330       28:18 Sl   525084 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --a
  (空=当前没有 cline 在跑)

== C. 所有 cline 进程（含别线，用于分辨）==
1800276 1475330       28:18 525348 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --auto-approve true -m glm-5

== D. harness loop 日志尾部 ==
--- /tmp/baize_harness_loop.log  [2026-11-27 08:33:21.444205469 +0800  26367606 B]
[push] ahead=0 behind=0
warning: adding embedded git repository: doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/sympy_fix
hint: You've added another git repository inside your current repository.
hint: Clones of the outer repository will not contain the contents of
hint: the embedded repository and will not know how to obtain it.
hint: If you meant to add a submodule, use:
hint: 
hint: 	git submodule add <url> doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/sympy_fix
hint: 
hint: If you added this path by mistake, you can remove it from the
hint: index with:
hint: 
hint: 	git rm --cached doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/sympy_fix
hint: 
hint: See "git help submodule" for more information.
[push] committed.
To https://github.com/foamliu/super_intelligence_2035.git
   7255c7655f..b117372d21  main -> main
[push] push OK.
[loop] 2026-11-27 08:33:21 WAITING=1 (async task running) → sleep 900s

== E. harness 相关其他日志 ==
Nov 27 08:33 /tmp/baize_harness_loop.log
Nov 27 08:33 /tmp/baize_harness_last_push
Nov 27 08:33 /tmp/baize_harness_llm_idx
Nov 26 05:56 /tmp/harness_resource_guard.last_action.last_ts
Nov 26 05:56 /tmp/harness_resource_guard.log
Nov 25 12:11 /tmp/harness_check.py
Nov 23 12:19 /tmp/harness_route_counts.py
Nov 23 08:39 /tmp/update_harness_memory.py

== F. MEMORY_HARNESS 状态 ==
3:WAITING: 1
  mtime: 2026-11-27 16:41:14.553910280 +0800
  size:  4141 B

== G. opencode / 7-way 评测进程（harness 的任务对象）==
 769492  3-12:45:24 /home/app.e0016372/.nvm/versions/node/v26.13.1/lib/node_modules/@opencode/cli/bin/opencode.exe serve --service
3803645    22:09:43 opencode
3834898       00:00 grep -E [o]pencode|[s]webench|predict|launch_doubao
  (空=harness 的评测任务当前无进程)

== H. gw_proxy（harness 依赖的 9090/9091/9092）==
LISTEN 0      5          127.0.0.1:9090       0.0.0.0:*    users:(("python3",pid=3990243,fd=3))         
LISTEN 0      5          127.0.0.1:9091       0.0.0.0:*    users:(("python3",pid=3990288,fd=3))         
LISTEN 0      5          127.0.0.1:9092       0.0.0.0:*    users:(("python3",pid=3990275,fd=3))         
3990243  1-20:52:05 python3 /nas_train/app.e0031982/harness_work/gw_proxy.py
3990275  1-20:52:04 python3 /nas_train/app.e0031982/harness_work/gw_proxy.py
3990288  1-20:52:03 python3 /nas_train/app.e0031982/harness_work/gw_proxy_dsh.py

== I. harness 相关文件 mtime（判断是否在动）==
2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md
  
2026-11-28_08:22:12 test_min_count_fix.py 
2026-11-28_08:22:12 test_dateformat_y.py 
2026-11-28_08:22:12 test_alter_together_optimization.py 
2026-11-28_08:22:11 verify_fix.py 

（只读：未 kill / 未重启 / 未改配置）
=== DONE 294 | 2026-11-28 08:53:17 ===
```

---

## RUN_ID 294 · 2026-11-28 08:53:29 · host=`whag0pgpuap12` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap12  date=2026-11-28 08:53:30

== A. harness loop 进程 ==
  loop_count=0
0

== B. harness 的 cline 进程（loop 派生的）==
1347998 1943222       26:30 Sl   34876 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligen
1348096 1347998       26:30 Sl   424488 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/c
  (空=当前没有 cline 在跑)

== C. 所有 cline 进程（含别线，用于分辨）==
1347998 1943222       26:30 34876 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA20
1348096 1347998       26:30 424524 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligence_20

== D. harness loop 日志尾部 ==

== E. harness 相关其他日志 ==

== F. MEMORY_HARNESS 状态 ==
3:WAITING: 1
  mtime: 2026-11-27 16:41:14.553910280 +0800
  size:  4141 B

== G. opencode / 7-way 评测进程（harness 的任务对象）==
  68092    17:59:58 opencode
 997794  1-23:29:46 opencode -s ses_e32ba4e8dffeBI590zks0BsxCR
1347998       26:30 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligence_2035/d
1348096       26:30 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_
3273090       00:00 grep -E [o]pencode|[s]webench|predict|launch_doubao
  (空=harness 的评测任务当前无进程)

== H. gw_proxy（harness 依赖的 9090/9091/9092）==
 341580 42-09:52:31 python3 /nas_train/app.e0031982/harness_work/gw_proxy_dsh.py

== I. harness 相关文件 mtime（判断是否在动）==
2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md
  
2026-11-28_08:22:12 test_min_count_fix.py 
2026-11-28_08:22:12 test_dateformat_y.py 
2026-11-28_08:22:12 test_alter_together_optimization.py 
2026-11-28_08:22:11 verify_fix.py 

（只读：未 kill / 未重启 / 未改配置）
=== DONE 294 | 2026-11-28 08:53:30 ===
```

---

## RUN_ID 295 · 2026-11-28 08:56:33 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  date=2026-11-28 08:56:33

== A. 前置复查 ==
  script: 8808 B  2026-11-26 10:36:49.054467158 +0800
  existing_loop_count=0
0
/tmp/tmp.UGvm7c37pV: line 11: [: 0
0: integer expression expected
  确认无 loop → 可以启动

== B. 启动 ==
  launched PID=4066583

== C. 启动后核验 ==
  PID 4066583 alive=YES
  loop_count_now=1
4066583 4066577       00:16 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh

== D. 日志（前 40 行，确认真的在推进）==
  log size=1001 B
[loop] 2026-11-28 08:56:33 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 08:56:33 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 08:56:33 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:33 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=0 behind=0
[push] committed.
To https://github.com/foamliu/super_intelligence_2035.git
   db6f7c306d..cd403d13f1  main -> main
[push] push OK.
[loop] 2026-11-28 08:56:39 WAITING=1 (async task running) → sleep 900s

== E. 等 60s 再确认未秒退 ==
  after60s_alive=YES
  after60s_count=1
[push] 2026-11-28 08:56:33 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=0 behind=0
[push] committed.
To https://github.com/foamliu/super_intelligence_2035.git
   db6f7c306d..cd403d13f1  main -> main
[push] push OK.
[loop] 2026-11-28 08:56:39 WAITING=1 (async task running) → sleep 900s

（只启动，未 kill / 未改配置 / 未动文件）
=== DONE 295 | 2026-11-28 08:57:49 ===
```

---

## RUN_ID 295 · 2026-11-28 08:56:37 · host=`whag0pgpuap12` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap12  date=2026-11-28 08:56:37

== A. 前置复查 ==
  script: 8808 B  2026-11-26 10:36:49.054467158 +0800
  existing_loop_count=0
0
/tmp/tmp.h8MszLndUs: line 11: [: 0
0: integer expression expected
  确认无 loop → 可以启动

== B. 启动 ==
  launched PID=3498993

== C. 启动后核验 ==
  PID 3498993 alive=YES
  loop_count_now=1
3498993 3498982       00:15 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh

== D. 日志（前 40 行，确认真的在推进）==
  log size=941 B
[loop] 2026-11-28 08:56:37 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 08:56:37 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 08:56:37 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:37 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=1 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 08:56:40 WAITING=1 (async task running) → sleep 900s

== E. 等 60s 再确认未秒退 ==
  after60s_alive=YES
  after60s_count=1
[loop] 2026-11-28 08:56:37 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:37 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=1 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 08:56:40 WAITING=1 (async task running) → sleep 900s

（只启动，未 kill / 未改配置 / 未动文件）
=== DONE 295 | 2026-11-28 08:57:52 ===
```

---

## RUN_ID 296 · 2026-11-28 09:09:15 · host=`whag0pgpuap12` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap12  ips=10.239.8.12 10.239.9.12 10.239.10.12 10.239.11.12 10.239.22.12 10.239.12.12 10.239.13.12 10.239.14.12 10.239.15.12 10.239.23.12 10.239.2.12 172.17.0.1   date=2026-11-28 09:09:15

== A. loop 脚本第 45-52 行（llm_rotate.sh 加载处）==
#   候选来自 doc/keys.txt（10 项 → 取 8 个 chat/coding LLM，排除 ASR/文生图）；
#   探针 = curl /chat/completions（200 可用 / 429 额度耗尽 / 403 base 不匹配）——现场实测见 run/ops/outbox.md RUN_ID 43/44。
#   ⚠️ base 必须与模型匹配（flash@/v1=200 但 flash@/cloud/v1=403）→ llm_pick 会自动改写 cline 的 openAiBaseUrl（首次改动前备份 .llmrot.bak）。
KEYS_TXT="$GIT_ROOT/doc/keys.txt"
LLM_STATE="/tmp/baize_harness_llm_idx"
[ -f "$SCRIPT_DIR/llm_rotate.sh" ] && . "$SCRIPT_DIR/llm_rotate.sh"

git_sync_and_push() {

== B. llm_rotate.sh 是否存在 ==
ls: cannot access '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/llm_rotate.sh': No such file or directory
  exist_test: NO

== C. 全机搜 llm_rotate*（本机）==
  --- /tmp ---
  --- PATH 中 ---
  llm_pick 不在 PATH

== D. 两节点对比（.29 / .12 互相 ssh）==
--- 10.239.2.29 ---
    host=whag0pgpuap29
    llm_rotate=NO
    loop_procs=2
--- 10.239.2.12 ---
    host=whag0pgpuap12
    llm_rotate=NO
    loop_procs=4

== E. 当前两节点 harness loop 进程 ==
--- 10.239.2.29 ---
    4066583       1       13:44 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
--- 10.239.2.12 ---
    3498993       1       13:40 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh

== F. 本机 loop 日志（最近 30 行）==
[loop] 2026-11-28 08:56:37 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 08:56:37 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 08:56:37 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:37 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=1 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 08:56:40 WAITING=1 (async task running) → sleep 900s

== G. hit：loop 脚本对 llm_pick 的依赖与兜底 ==
28:CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
47:#   ⚠️ base 必须与模型匹配（flash@/v1=200 但 flash@/cloud/v1=403）→ llm_pick 会自动改写 cline 的 openAiBaseUrl（首次改动前备份 .llmrot.ba
50:[ -f "$SCRIPT_DIR/llm_rotate.sh" ] && . "$SCRIPT_DIR/llm_rotate.sh"
133:          if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
141:          "${taskline[@]}" cline -c "$CWD" --auto-approve true -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null

（只读：未 kill / 未重启 / 未改文件）
=== DONE 296 | 2026-11-28 09:10:17 ===
```

---

## RUN_ID 296 · 2026-11-28 09:09:31 · host=`whag0pgpuap29` · exit=0

**命令**
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

**输出**
```
[0] exec_host=whag0pgpuap29  ips=10.239.8.29 10.239.9.29 10.239.10.29 10.239.11.29 10.239.22.29 10.239.12.29 10.239.13.29 10.239.14.29 10.239.15.29 10.239.23.29 10.239.2.29 10.247.36.1 10.247.35.1 10.247.34.1   date=2026-11-28 09:09:31

== A. loop 脚本第 45-52 行（llm_rotate.sh 加载处）==
#   候选来自 doc/keys.txt（10 项 → 取 8 个 chat/coding LLM，排除 ASR/文生图）；
#   探针 = curl /chat/completions（200 可用 / 429 额度耗尽 / 403 base 不匹配）——现场实测见 run/ops/outbox.md RUN_ID 43/44。
#   ⚠️ base 必须与模型匹配（flash@/v1=200 但 flash@/cloud/v1=403）→ llm_pick 会自动改写 cline 的 openAiBaseUrl（首次改动前备份 .llmrot.bak）。
KEYS_TXT="$GIT_ROOT/doc/keys.txt"
LLM_STATE="/tmp/baize_harness_llm_idx"
[ -f "$SCRIPT_DIR/llm_rotate.sh" ] && . "$SCRIPT_DIR/llm_rotate.sh"

git_sync_and_push() {

== B. llm_rotate.sh 是否存在 ==
ls: cannot access '/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/llm_rotate.sh': No such file or directory
  exist_test: NO

== C. 全机搜 llm_rotate*（本机）==
  --- /tmp ---
  --- PATH 中 ---
  llm_pick 不在 PATH

== D. 两节点对比（.29 / .12 互相 ssh）==
--- 10.239.2.29 ---
    host=whag0pgpuap29
    llm_rotate=NO
    loop_procs=4
--- 10.239.2.12 ---
    host=whag0pgpuap12
    llm_rotate=NO
    loop_procs=2

== E. 当前两节点 harness loop 进程 ==
--- 10.239.2.29 ---
    4066583       1       13:59 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
--- 10.239.2.12 ---
    3498993       1       13:56 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh

== F. 本机 loop 日志（最近 30 行）==
[loop] 2026-11-28 08:56:33 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 08:56:33 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 08:56:33 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:33 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=0 behind=0
[push] committed.
To https://github.com/foamliu/super_intelligence_2035.git
   db6f7c306d..cd403d13f1  main -> main
[push] push OK.
[loop] 2026-11-28 08:56:39 WAITING=1 (async task running) → sleep 900s

== G. hit：loop 脚本对 llm_pick 的依赖与兜底 ==
28:CLINE_KEY="02_088EE9051AAE4BF0ABFC7130331BF697_c2759d74-49f1-410a-89ea-2cf188ea2f23"
47:#   ⚠️ base 必须与模型匹配（flash@/v1=200 但 flash@/cloud/v1=403）→ llm_pick 会自动改写 cline 的 openAiBaseUrl（首次改动前备份 .llmrot.ba
50:[ -f "$SCRIPT_DIR/llm_rotate.sh" ] && . "$SCRIPT_DIR/llm_rotate.sh"
133:          if llm_pick "$LLM_STATE" "$KEYS_TXT"; then
141:          "${taskline[@]}" cline -c "$CWD" --auto-approve true -m "$LLM_MODEL" -k "$LLM_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null

（只读：未 kill / 未重启 / 未改文件）
=== DONE 296 | 2026-11-28 09:10:33 ===
```

---

## RUN_ID 297 · 2026-11-28 09:55:34 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T') who=$(whoami)"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
L=/tmp/baize_harness_loop.log
echo
echo "== A. loop 进程（pid / cwd / etime）=="
pids=$(pgrep -f 'baize_harness_loop.sh' 2>/dev/null | tr '\n' ' ')
echo "  loop_pids=[$pids] count=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
for p in $pids; do
  echo "    pid=$p cwd=$(readlink /proc/$p/cwd) start=$(ps -o lstart= -p $p 2>/dev/null) etime=$(ps -o etime= -p $p 2>/dev/null) stat=$(ps -o stat= -p $p 2>/dev/null)"
done
echo
echo "== B. cline 子进程（有则在真干活）=="
pgrep -af 'cline' 2>/dev/null | cut -c1-180 | head -8
echo "  cline_count=$(pgrep -fc 'cline' 2>/dev/null || echo 0)"
echo
echo "== C. loop 日志（尾 30 行）=="
ls -l --time-style=+%F_%T /tmp/baize_harness_loop.log* 2>/dev/null
tail -n 30 "$L" 2>/dev/null | cut -c1-220
echo
echo "== D. 关键计数（判定空转）=="
for pat in 'wake up' 'invoking cline' 'cline returned' '无可用 LLM 候选' 'llm_pick: command not found' 'SKIP cline' 'push OK' 'push FAILED' 'WAITING=1' 'WAITING=0'; do
  echo "  [$pat] = $(grep -c -- "$pat" "$L" 2>/dev/null || echo 0)"
done
echo "  --- 最近 5 次 wake ---"
grep -E '\[loop\].*wake up' "$L" 2>/dev/null | tail -5
echo "  --- 最近 6 条 push ---"
grep -E '\[push\]' "$L" 2>/dev/null | tail -6
echo
echo "== E. 最近 push 时间 / WAITING / 关键文件 mtime =="
if [ -f /tmp/baize_harness_last_push ]; then
  ts=$(cat /tmp/baize_harness_last_push 2>/dev/null)
  echo "  last_push_epoch=$ts -> $(date -d @$ts '+%F %T' 2>/dev/null) age_min=$(( ( $(date +%s) - ts ) / 60 ))"
else
  echo "  /tmp/baize_harness_last_push 不存在"
fi
grep -n '^WAITING' "$RUN/MEMORY_HARNESS.md" 2>/dev/null || echo "  WAITING 行缺失"
ls -l --time-style=+%F_%T "$RUN/MEMORY_HARNESS.md" "$RUN/BAIZE_HARNESS_TASK.md" 2>/dev/null
echo
echo "== F. 负载（>HARNESS_LOAD_MAX=120 会 SKIP cline）=="
echo "  load=$(cat /proc/loadavg) nproc=$(nproc 2>/dev/null)"
echo
echo "== G. git 状态 =="
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null || cd "$(git -C "$RUN" rev-parse --show-toplevel)"
git log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git status --porcelain | wc -l) ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
echo
echo "== H. harness 进度证据 =="
H="$RUN/harness/swebench_verified_full"
ls -ld --time-style=+%F_%T "$H/predictions_doubao_pro" 2>/dev/null || echo "  predictions_doubao_pro MISSING"
if [ -d "$H/predictions_doubao_pro" ]; then ls -l --time-style=+%F_%T "$H/predictions_doubao_pro" | head -12; fi
for f in "$RUN"/harness/logs_doubao_pro/*.log; do [ -f "$f" ] && echo "  $(stat -c '%y %sB' "$f") $(basename "$f")"; done
echo "  --- opencode 日志尾部 ---"
tail -n 6 "$RUN/harness/logs_doubao_pro/opencode_doubao_pro.log" 2>/dev/null | cut -c1-200
echo "  --- 最新 harness 报告 ---"
ls -lt --time-style=+%F_%T "$RUN"/harness/reports/*.html 2>/dev/null | head -4
echo
echo "== I. 最近 24h 本线改动 top10 =="
find "$RUN" -maxdepth 2 -type f -mmin -1440 -printf '%TY-%Tm-%Td_%TH:%TM %p\n' 2>/dev/null | sort -r | head -10
echo
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 297 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap12 date=2026-11-28 09:55:34 who=app.e0031982

== A. loop 进程（pid / cwd / etime）==
  loop_pids=[3498993 ] count=1
    pid=3498993 cwd=/nas_train/app.e0031982/code/super_intelligence_2035 start=Sat Nov 28 08:56:36 2026 etime=      58:57 stat=Ss

== B. cline 子进程（有则在真干活）==
2854433 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
2854514 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/
3041408 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --cline-hub-daemon --cwd /nas_train/app.e0031982 --host 127.0.0.1 --port 25463 --pathname /hub
  cline_count=3

== C. loop 日志（尾 30 行）==
-rw-r--r-- 1 app.e0031982 app.adm 7710 2026-11-28_09:41:49 /tmp/baize_harness_loop.log
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
fatal: Unable to create '/nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
fatal: Unable to create '/nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
fatal: Unable to create '/nas_train/app.e0031982/code/super_intelligence_2035/.git/index.lock': File exists.

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
[push] nothing of ours to commit.
To https://github.com/foamliu/super_intelligence_2035.git
   14f932711e..0383227cc3  main -> main
[push] push OK.
[loop] 2026-11-28 09:41:49 WAITING=1 (async task running) → sleep 900s

== D. 关键计数（判定空转）==
  [wake up] = 4
  [invoking cline] = 4
  [cline returned] = 4
  [无可用 LLM 候选] = 4
  [llm_pick: command not found] = 4
  [SKIP cline] = 0
0
  [push OK] = 4
  [push FAILED] = 0
0
  [WAITING=1] = 4
  [WAITING=0] = 0
0
  --- 最近 5 次 wake ---
[loop] 2026-11-28 08:56:37 wake up, invoking cline ...
[loop] 2026-11-28 09:11:40 wake up, invoking cline ...
[loop] 2026-11-28 09:26:42 wake up, invoking cline ...
[loop] 2026-11-28 09:41:45 wake up, invoking cline ...
  --- 最近 6 条 push ---
[push] nothing of ours to commit.
[push] push OK.
[push] 2026-11-28 09:41:45 push interval reached, syncing ...
[push] ahead=1 behind=0
[push] nothing of ours to commit.
[push] push OK.

== E. 最近 push 时间 / WAITING / 关键文件 mtime ==
  last_push_epoch=1795830109 -> 2026-11-28 09:41:49 age_min=13
3:WAITING: 1
-rw-r----- 1 app.e0031982 app.adm 29733 2026-11-27_16:41:03 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md
-rw-r----- 1 app.e0031982 app.adm  4141 2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md

== F. 负载（>HARNESS_LOAD_MAX=120 会 SKIP cline）==
  load=11.92 10.32 11.19 14/5983 3637312 nproc=224

== G. git 状态 ==
  HEAD fb2309858f 2026-11-28 09:54:52 +0800 ops RUN_ID 297: harness loop 健康体检（只读·用户令）
  dirty=208 ahead_behind=0	0

== H. harness 进度证据 ==
drwxr-x--- 2 app.e0031982 app.adm 466944 2026-11-28_08:13:03 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_doubao_pro
total 143472
-rw-r----- 1 app.e0031982 app.adm     2283 2026-11-26_12:02:09 claude-code__astropy__astropy-12907.json
-rw-r----- 1 app.e0031982 app.adm     2546 2026-11-26_12:03:27 claude-code__astropy__astropy-13033.json
-rw-r----- 1 app.e0031982 app.adm     2683 2026-11-26_12:04:24 claude-code__astropy__astropy-13236.json
-rw-r----- 1 app.e0031982 app.adm     5427 2026-11-26_12:06:33 claude-code__astropy__astropy-13398.json
-rw-r----- 1 app.e0031982 app.adm      978 2026-11-26_12:09:27 claude-code__astropy__astropy-13453.json
-rw-r----- 1 app.e0031982 app.adm     1334 2026-11-26_12:11:02 claude-code__astropy__astropy-13579.json
-rw-r----- 1 app.e0031982 app.adm     1269 2026-11-26_12:11:52 claude-code__astropy__astropy-13977.json
-rw-r----- 1 app.e0031982 app.adm     1354 2026-11-26_12:14:43 claude-code__astropy__astropy-14096.json
-rw-r----- 1 app.e0031982 app.adm     1346 2026-11-26_12:16:08 claude-code__astropy__astropy-14182.json
-rw-r----- 1 app.e0031982 app.adm      850 2026-11-26_12:16:45 claude-code__astropy__astropy-14309.json
-rw-r----- 1 app.e0031982 app.adm      921 2026-11-26_12:17:49 claude-code__astropy__astropy-14365.json
  2026-11-27 18:06:26.513131376 +0800 43718B claude-code_doubao_pro.log
  2026-11-26 10:12:55.408022300 +0800 40796B claude-code_doubao_pro_rerun2.log
  2026-11-26 10:12:55.364662270 +0800 29311B claude-code_doubao_pro_rerun3.log
  2026-11-26 10:12:55.506122843 +0800 29311B claude-code_doubao_pro_rerun.log
  2026-11-27 18:06:26.515265685 +0800 43742B cline-patched_doubao_pro.log
  2026-11-26 10:12:55.426519999 +0800 2730B cline-patched_doubao_pro_rerun.log
  2026-11-27 18:06:26.450891920 +0800 43796B codex_doubao_pro.log
  2026-11-27 18:06:26.520106732 +0800 43096B deepseek-harness_doubao_pro.log
  2026-11-26 10:12:55.518016826 +0800 33949B deepseek-harness_doubao_pro_rerun.log
  2026-11-27 18:06:26.456073690 +0800 43434B hermes_doubao_pro.log
  2026-11-27 18:06:26.516714770 +0800 259B opencode_doubao_pro.log
  2026-11-26 13:05:26.605381696 +0800 752B opencode_doubao_pro_rerun.log
  2026-11-27 18:06:26.460901170 +0800 43751B pi_doubao_pro.log
  2026-11-27 17:11:42.783013200 +0800 30378B zhulong_doubao_pro.log
  --- opencode 日志尾部 ---
[verified-full 16:38:25] resume: loaded 60 existing results
[verified-full 16:38:26] predict opencode: workers=4 pending=500 (parallel)
[verified-full 16:39:49]   -> no-patch (patch=0B wall=82.9s)
[verified-full 16:43:37]   -> no-patch (patch=0B wall=227.8s)
  --- 最新 harness 报告 ---
-rw-r--r-- 1 app.e0031982 app.adm 24908 2026-11-26_10:12:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/reports/report_harness_adapter_0pass_rootcause_zh.html
-rw-r--r-- 1 app.e0031982 app.adm 19975 2026-11-26_10:12:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/reports/report_harness_glm53_7x300_zh.html

== I. 最近 24h 本线改动 top10 ==
2026-11-28_09:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/inbox.md
2026-11-28_09:40 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md
2026-11-28_09:21 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/daily-memories-data/2026-11-28.md
2026-11-28_09:16 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
2026-11-28_09:10 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/outbox.md
2026-11-28_09:10 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.12
2026-11-28_09:10 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id
2026-11-28_08:53 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/convert_idx_format.py
2026-11-28_08:32 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md
2026-11-28_08:25 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md

（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 297 | 2026-11-28 09:55:35 ===
```

---

## RUN_ID 297 · 2026-11-28 09:55:38 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T') who=$(whoami)"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
L=/tmp/baize_harness_loop.log
echo
echo "== A. loop 进程（pid / cwd / etime）=="
pids=$(pgrep -f 'baize_harness_loop.sh' 2>/dev/null | tr '\n' ' ')
echo "  loop_pids=[$pids] count=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
for p in $pids; do
  echo "    pid=$p cwd=$(readlink /proc/$p/cwd) start=$(ps -o lstart= -p $p 2>/dev/null) etime=$(ps -o etime= -p $p 2>/dev/null) stat=$(ps -o stat= -p $p 2>/dev/null)"
done
echo
echo "== B. cline 子进程（有则在真干活）=="
pgrep -af 'cline' 2>/dev/null | cut -c1-180 | head -8
echo "  cline_count=$(pgrep -fc 'cline' 2>/dev/null || echo 0)"
echo
echo "== C. loop 日志（尾 30 行）=="
ls -l --time-style=+%F_%T /tmp/baize_harness_loop.log* 2>/dev/null
tail -n 30 "$L" 2>/dev/null | cut -c1-220
echo
echo "== D. 关键计数（判定空转）=="
for pat in 'wake up' 'invoking cline' 'cline returned' '无可用 LLM 候选' 'llm_pick: command not found' 'SKIP cline' 'push OK' 'push FAILED' 'WAITING=1' 'WAITING=0'; do
  echo "  [$pat] = $(grep -c -- "$pat" "$L" 2>/dev/null || echo 0)"
done
echo "  --- 最近 5 次 wake ---"
grep -E '\[loop\].*wake up' "$L" 2>/dev/null | tail -5
echo "  --- 最近 6 条 push ---"
grep -E '\[push\]' "$L" 2>/dev/null | tail -6
echo
echo "== E. 最近 push 时间 / WAITING / 关键文件 mtime =="
if [ -f /tmp/baize_harness_last_push ]; then
  ts=$(cat /tmp/baize_harness_last_push 2>/dev/null)
  echo "  last_push_epoch=$ts -> $(date -d @$ts '+%F %T' 2>/dev/null) age_min=$(( ( $(date +%s) - ts ) / 60 ))"
else
  echo "  /tmp/baize_harness_last_push 不存在"
fi
grep -n '^WAITING' "$RUN/MEMORY_HARNESS.md" 2>/dev/null || echo "  WAITING 行缺失"
ls -l --time-style=+%F_%T "$RUN/MEMORY_HARNESS.md" "$RUN/BAIZE_HARNESS_TASK.md" 2>/dev/null
echo
echo "== F. 负载（>HARNESS_LOAD_MAX=120 会 SKIP cline）=="
echo "  load=$(cat /proc/loadavg) nproc=$(nproc 2>/dev/null)"
echo
echo "== G. git 状态 =="
cd /nas_train/app.e0031982/code/super_intelligence_2035 2>/dev/null || cd "$(git -C "$RUN" rev-parse --show-toplevel)"
git log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git status --porcelain | wc -l) ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
echo
echo "== H. harness 进度证据 =="
H="$RUN/harness/swebench_verified_full"
ls -ld --time-style=+%F_%T "$H/predictions_doubao_pro" 2>/dev/null || echo "  predictions_doubao_pro MISSING"
if [ -d "$H/predictions_doubao_pro" ]; then ls -l --time-style=+%F_%T "$H/predictions_doubao_pro" | head -12; fi
for f in "$RUN"/harness/logs_doubao_pro/*.log; do [ -f "$f" ] && echo "  $(stat -c '%y %sB' "$f") $(basename "$f")"; done
echo "  --- opencode 日志尾部 ---"
tail -n 6 "$RUN/harness/logs_doubao_pro/opencode_doubao_pro.log" 2>/dev/null | cut -c1-200
echo "  --- 最新 harness 报告 ---"
ls -lt --time-style=+%F_%T "$RUN"/harness/reports/*.html 2>/dev/null | head -4
echo
echo "== I. 最近 24h 本线改动 top10 =="
find "$RUN" -maxdepth 2 -type f -mmin -1440 -printf '%TY-%Tm-%Td_%TH:%TM %p\n' 2>/dev/null | sort -r | head -10
echo
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 297 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap29 date=2026-11-28 09:55:38 who=app.e0031982

== A. loop 进程（pid / cwd / etime）==
  loop_pids=[4066583 ] count=1
    pid=4066583 cwd=/nas_train/app.e0031982/code/super_intelligence_2035 start=Sat Nov 28 08:56:32 2026 etime=      59:05 stat=Ss

== B. cline 子进程（有则在真干活）==
1800276 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --auto-approve true -m glm-5.2 -k 0
3449130 /nas_train/app.e0031982/harness/cline/dist/cline-checkpoint-off --cline-hub-daemon --cwd /nas_train/app.e0031982
  cline_count=2

== C. loop 日志（尾 30 行）==
-rw-r----- 1 app.e0031982 app.adm 6093 2026-11-28_09:41:49 /tmp/baize_harness_loop.log

Another git process seems to be running in this repository, e.g.
an editor opened by 'git commit'. Please make sure all processes
are terminated then try again. If it still fails, a git process
may have crashed in this repository earlier:
remove the file manually to continue.
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 09:26:44 WAITING=1 (async task running) → sleep 900s
[loop] 2026-11-28 09:41:44 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 09:41:44 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 09:41:44 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 09:41:44 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=1 behind=0
[push] nothing of ours to commit.
To https://github.com/foamliu/super_intelligence_2035.git
 ! [remote rejected]       main -> main (cannot lock ref 'refs/heads/main': is at 0383227cc3a6727f40192da84405cf18cc27596a but expected 14f932711e450a8f04a75657d5e574cb810871a1)
error: failed to push some refs to 'https://github.com/foamliu/super_intelligence_2035.git'
[push] push FAILED (will retry next cycle).
[loop] 2026-11-28 09:41:49 WAITING=1 (async task running) → sleep 900s

== D. 关键计数（判定空转）==
  [wake up] = 4
  [invoking cline] = 4
  [cline returned] = 4
  [无可用 LLM 候选] = 4
  [llm_pick: command not found] = 4
  [SKIP cline] = 0
0
  [push OK] = 3
  [push FAILED] = 1
  [WAITING=1] = 4
  [WAITING=0] = 0
0
  --- 最近 5 次 wake ---
[loop] 2026-11-28 08:56:33 wake up, invoking cline ...
[loop] 2026-11-28 09:11:39 wake up, invoking cline ...
[loop] 2026-11-28 09:26:42 wake up, invoking cline ...
[loop] 2026-11-28 09:41:44 wake up, invoking cline ...
  --- 最近 6 条 push ---
[push] nothing of ours to commit.
[push] push OK.
[push] 2026-11-28 09:41:44 push interval reached, syncing ...
[push] ahead=1 behind=0
[push] nothing of ours to commit.
[push] push FAILED (will retry next cycle).

== E. 最近 push 时间 / WAITING / 关键文件 mtime ==
  last_push_epoch=1795830109 -> 2026-11-28 09:41:49 age_min=13
3:WAITING: 1
-rw-r----- 1 app.e0031982 app.adm 29733 2026-11-27_16:41:03 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_HARNESS_TASK.md
-rw-r----- 1 app.e0031982 app.adm  4141 2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md

== F. 负载（>HARNESS_LOAD_MAX=120 会 SKIP cline）==
  load=8.09 7.13 7.89 21/4505 4102392 nproc=224

== G. git 状态 ==
  HEAD d19854eb44 2026-11-28 09:55:36 +0800 ops-relay[12]: result @ 2026-11-28 09:55:36
  dirty=208 ahead_behind=0	0

== H. harness 进度证据 ==
drwxr-x--- 2 app.e0031982 app.adm 466944 2026-11-28_08:13:03 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_full/predictions_doubao_pro
total 143472
-rw-r----- 1 app.e0031982 app.adm     2283 2026-11-26_12:02:09 claude-code__astropy__astropy-12907.json
-rw-r----- 1 app.e0031982 app.adm     2546 2026-11-26_12:03:27 claude-code__astropy__astropy-13033.json
-rw-r----- 1 app.e0031982 app.adm     2683 2026-11-26_12:04:24 claude-code__astropy__astropy-13236.json
-rw-r----- 1 app.e0031982 app.adm     5427 2026-11-26_12:06:33 claude-code__astropy__astropy-13398.json
-rw-r----- 1 app.e0031982 app.adm      978 2026-11-26_12:09:27 claude-code__astropy__astropy-13453.json
-rw-r----- 1 app.e0031982 app.adm     1334 2026-11-26_12:11:02 claude-code__astropy__astropy-13579.json
-rw-r----- 1 app.e0031982 app.adm     1269 2026-11-26_12:11:52 claude-code__astropy__astropy-13977.json
-rw-r----- 1 app.e0031982 app.adm     1354 2026-11-26_12:14:43 claude-code__astropy__astropy-14096.json
-rw-r----- 1 app.e0031982 app.adm     1346 2026-11-26_12:16:08 claude-code__astropy__astropy-14182.json
-rw-r----- 1 app.e0031982 app.adm      850 2026-11-26_12:16:45 claude-code__astropy__astropy-14309.json
-rw-r----- 1 app.e0031982 app.adm      921 2026-11-26_12:17:49 claude-code__astropy__astropy-14365.json
  2026-11-27 18:06:26.513131376 +0800 43718B claude-code_doubao_pro.log
  2026-11-26 10:12:55.408022300 +0800 40796B claude-code_doubao_pro_rerun2.log
  2026-11-26 10:12:55.364662270 +0800 29311B claude-code_doubao_pro_rerun3.log
  2026-11-26 10:12:55.506122843 +0800 29311B claude-code_doubao_pro_rerun.log
  2026-11-27 18:06:26.515265685 +0800 43742B cline-patched_doubao_pro.log
  2026-11-26 10:12:55.426519999 +0800 2730B cline-patched_doubao_pro_rerun.log
  2026-11-27 18:06:26.450891920 +0800 43796B codex_doubao_pro.log
  2026-11-27 18:06:26.520106732 +0800 43096B deepseek-harness_doubao_pro.log
  2026-11-26 10:12:55.518016826 +0800 33949B deepseek-harness_doubao_pro_rerun.log
  2026-11-27 18:06:26.456073690 +0800 43434B hermes_doubao_pro.log
  2026-11-27 18:06:26.516714770 +0800 259B opencode_doubao_pro.log
  2026-11-26 13:05:26.605381696 +0800 752B opencode_doubao_pro_rerun.log
  2026-11-27 18:06:26.460901170 +0800 43751B pi_doubao_pro.log
  2026-11-27 17:11:42.783013200 +0800 30378B zhulong_doubao_pro.log
  --- opencode 日志尾部 ---
[verified-full 16:38:25] resume: loaded 60 existing results
[verified-full 16:38:26] predict opencode: workers=4 pending=500 (parallel)
[verified-full 16:39:49]   -> no-patch (patch=0B wall=82.9s)
[verified-full 16:43:37]   -> no-patch (patch=0B wall=227.8s)
  --- 最新 harness 报告 ---
-rw-r--r-- 1 app.e0031982 app.adm 24908 2026-11-26_10:12:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/reports/report_harness_adapter_0pass_rootcause_zh.html
-rw-r--r-- 1 app.e0031982 app.adm 19975 2026-11-26_10:12:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/reports/report_harness_glm53_7x300_zh.html

== I. 最近 24h 本线改动 top10 ==
2026-11-28_09:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/outbox.md
2026-11-28_09:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id.12
2026-11-28_09:55 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/inbox.md
2026-11-28_09:40 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_DATA.md
2026-11-28_09:21 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/daily-memories-data/2026-11-28.md
2026-11-28_09:16 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
2026-11-28_09:10 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/ops/.last_run_id
2026-11-28_08:53 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/data/convert_idx_format.py
2026-11-28_08:32 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md
2026-11-28_08:25 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md

（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 297 | 2026-11-28 09:55:41 ===
```

---

## RUN_ID 298 · 2026-11-28 10:01:12 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T') who=$(whoami)"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
LOOP=$RUN/baize_harness_loop.sh
GIT=/nas_train/app.e0031982/code/super_intelligence_2035
LOG=/tmp/baize_harness_loop.log
H=$(hostname)
echo
echo "== A. 前置：脚本版本 / 语法 =="
echo "  mtime=$(stat -c '%y' "$LOOP" 2>/dev/null)"
echo "  llm_pick_occurrences=$(grep -c 'llm_pick' "$LOOP" 2>/dev/null || echo 0)  (期望=1，仅注释)"
grep -n 'llm_pick' "$LOOP" 2>/dev/null | cut -c1-170
echo "  cline_call:"; grep -n 'cline -c' "$LOOP" 2>/dev/null | cut -c1-200
bash -n "$LOOP" && echo "  bash -n OK" || { echo "ABORT: 语法错误"; echo "=== DONE 298 (ABORT) ==="; exit 9; }
echo
echo "== B. 清 stale git 锁（仅当无活跃 git 且锁龄>300s）=="
cd "$GIT" || { echo "ABORT cd"; exit 9; }
if [ -f .git/index.lock ]; then
  age=$(( $(date +%s) - $(stat -c %Y .git/index.lock) ))
  echo "  index.lock age=${age}s size=$(stat -c %s .git/index.lock)"
  if [ "$age" -gt 300 ] && [ "$(pgrep -x git | wc -l)" -eq 0 ]; then
    rm -f .git/index.lock && echo "  removed stale index.lock"
  else
    echo "  KEEP (fresh lock or active git: $(pgrep -x git | tr '\n' ' '))"
  fi
else
  echo "  no index.lock"
fi
if [ -f .git/gc.log ]; then head -3 .git/gc.log; rm -f .git/gc.log; echo "  removed gc.log"; else echo "  no gc.log"; fi
echo
echo "== C. 停旧 loop（精确 PID + 兜底）=="
OLD=$(pgrep -f 'baize_harness_loop.sh' 2>/dev/null | tr '\n' ' ')
echo "  old_pids=[$OLD]"
for p in $OLD; do kill -9 "$p" 2>/dev/null && echo "  killed $p"; done
sleep 2
echo "  alive_after_kill=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
echo
echo "== D. 单实例：只 .29 起 loop =="
if [ "$(hostname -I | grep -c '10.239.2.29')" -gt 0 ]; then
  echo "  host=.29 -> START"
  mv -f "$LOG" "$LOG.old.$(date +%H%M%S)" 2>/dev/null
  cd "$RUN" || exit 9
  setsid bash "$LOOP" > "$LOG" 2>&1 < /dev/null &
  NEWPID=$!
  echo "  launched PID=$NEWPID"
  sleep 20
  echo "  alive_20s=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
  echo "  loop_count=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
  ps -eo pid,ppid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-150
else
  echo "  host=$H -> KEEP STOPPED (single-instance on .29)"
fi
echo
echo "== E. 90s 后四证 =="
sleep 70
echo "  --- 新日志头 20 行 ---"
head -n 20 "$LOG" 2>/dev/null | cut -c1-220
echo "  --- 判定（期望：1>=1 / 2=0 / 3=0 / 4>=1 / 5>=1）---"
echo "  proof1_loop_procs=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
echo "  proof2_llm_pick_err=$(grep -c 'llm_pick: command not found' "$LOG" 2>/dev/null || echo 0)"
echo "  proof3_no_llm_skip=$(grep -c '无可用 LLM 候选' "$LOG" 2>/dev/null || echo 0)"
echo "  proof4_invoking=$(grep -c 'invoking cline' "$LOG" 2>/dev/null || echo 0)"
echo "  proof5_cline_procs=$(ps -eo args | grep '[c]line ' | grep -c 'glm-5.2' || echo 0)"
ps -eo pid,ppid,etime,args | grep '[c]line ' | grep 'glm-5.2' | cut -c1-170
echo
echo "== F. 日志尾部 =="
tail -n 15 "$LOG" 2>/dev/null | cut -c1-220
echo
echo "== G. git 状态（不清脏文件）=="
git -C "$GIT" log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git -C "$GIT" status --porcelain | wc -l)  ahead_behind=$(git -C "$GIT" rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
git -C "$GIT" status --porcelain | awk '{print $2}' | cut -d/ -f1-3 | sort | uniq -c | sort -rn | head -8
echo
echo "（写操作仅限：kill 本线 loop / 重启 .29 loop / 删 stale lock+gc.log）"
echo "=== DONE 298 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap12 date=2026-11-28 10:01:12 who=app.e0031982

== A. 前置：脚本版本 / 语法 ==
  mtime=2026-11-28 09:16:29.842285770 +0800
  llm_pick_occurrences=1  (期望=1，仅注释)
124:        # 2026-11-28 用户令：移除 llm_rotate.sh / llm_pick 额度轮换，直接用脚本内配好的 MODEL/CLINE_KEY
  cline_call:
132:          "${taskline[@]}" cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
  bash -n OK

== B. 清 stale git 锁（仅当无活跃 git 且锁龄>300s）==
  no index.lock
head: cannot open '.git/gc.log' for reading: No such file or directory
  removed gc.log

== C. 停旧 loop（精确 PID + 兜底）==
  old_pids=[3498993 ]
  killed 3498993
  alive_after_kill=0
0

== D. 单实例：只 .29 起 loop ==
  host=whag0pgpuap12 -> KEEP STOPPED (single-instance on .29)

== E. 90s 后四证 ==
  --- 新日志头 20 行 ---
[loop] 2026-11-28 08:56:37 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
[loop] 2026-11-28 08:56:37 !!! 无可用 LLM 候选 → 跳过本轮 cline
[loop] 2026-11-28 08:56:37 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 08:56:37 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=1 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 08:56:40 WAITING=1 (async task running) → sleep 900s
[loop] 2026-11-28 09:11:40 wake up, invoking cline ...
/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh: line 133: llm_pick: command not found
  --- 判定（期望：1>=1 / 2=0 / 3=0 / 4>=1 / 5>=1）---
  proof1_loop_procs=0
0
  proof2_llm_pick_err=5
  proof3_no_llm_skip=5
  proof4_invoking=5
  proof5_cline_procs=0
0

== F. 日志尾部 ==
[loop] 2026-11-28 09:56:49 cline returned (exit 0), checking git sync ...
[push] 2026-11-28 09:56:49 push interval reached, syncing ...
Auto packing the repository in background for optimum performance.
See "git help gc" for manual housekeeping.
warning: The last gc run reported the following. Please correct the root cause
and remove .git/gc.log
Automatic cleanup will not be performed until the file is removed.

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=0 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 09:56:52 WAITING=1 (async task running) → sleep 900s

== G. git 状态（不清脏文件）==
  HEAD a512f8f94e 2026-11-28 10:00:49 +0800 ops RUN_ID 298: fix harness loop (restart .29 + 4-proof) [repair empty-inbox commit]
  dirty=208  ahead_behind=0	0
    197 doc/BaiZe-ISEDA2027/run
      1 test_simple.py
      1 test_random_order_aggregation.py
      1 test_named_tuple_range.py
      1 test_formfield_callback.py
      1 test_fix2.py
      1 test_auth_form.py
      1 doc/BaiZe-ISEDA2027/Xmodel-LM

（写操作仅限：kill 本线 loop / 重启 .29 loop / 删 stale lock+gc.log）
=== DONE 298 | 2026-11-28 10:02:28 ===
```

---

## RUN_ID 298 · 2026-11-28 10:00:58 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T') who=$(whoami)"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
LOOP=$RUN/baize_harness_loop.sh
GIT=/nas_train/app.e0031982/code/super_intelligence_2035
LOG=/tmp/baize_harness_loop.log
H=$(hostname)
echo
echo "== A. 前置：脚本版本 / 语法 =="
echo "  mtime=$(stat -c '%y' "$LOOP" 2>/dev/null)"
echo "  llm_pick_occurrences=$(grep -c 'llm_pick' "$LOOP" 2>/dev/null || echo 0)  (期望=1，仅注释)"
grep -n 'llm_pick' "$LOOP" 2>/dev/null | cut -c1-170
echo "  cline_call:"; grep -n 'cline -c' "$LOOP" 2>/dev/null | cut -c1-200
bash -n "$LOOP" && echo "  bash -n OK" || { echo "ABORT: 语法错误"; echo "=== DONE 298 (ABORT) ==="; exit 9; }
echo
echo "== B. 清 stale git 锁（仅当无活跃 git 且锁龄>300s）=="
cd "$GIT" || { echo "ABORT cd"; exit 9; }
if [ -f .git/index.lock ]; then
  age=$(( $(date +%s) - $(stat -c %Y .git/index.lock) ))
  echo "  index.lock age=${age}s size=$(stat -c %s .git/index.lock)"
  if [ "$age" -gt 300 ] && [ "$(pgrep -x git | wc -l)" -eq 0 ]; then
    rm -f .git/index.lock && echo "  removed stale index.lock"
  else
    echo "  KEEP (fresh lock or active git: $(pgrep -x git | tr '\n' ' '))"
  fi
else
  echo "  no index.lock"
fi
if [ -f .git/gc.log ]; then head -3 .git/gc.log; rm -f .git/gc.log; echo "  removed gc.log"; else echo "  no gc.log"; fi
echo
echo "== C. 停旧 loop（精确 PID + 兜底）=="
OLD=$(pgrep -f 'baize_harness_loop.sh' 2>/dev/null | tr '\n' ' ')
echo "  old_pids=[$OLD]"
for p in $OLD; do kill -9 "$p" 2>/dev/null && echo "  killed $p"; done
sleep 2
echo "  alive_after_kill=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
echo
echo "== D. 单实例：只 .29 起 loop =="
if [ "$(hostname -I | grep -c '10.239.2.29')" -gt 0 ]; then
  echo "  host=.29 -> START"
  mv -f "$LOG" "$LOG.old.$(date +%H%M%S)" 2>/dev/null
  cd "$RUN" || exit 9
  setsid bash "$LOOP" > "$LOG" 2>&1 < /dev/null &
  NEWPID=$!
  echo "  launched PID=$NEWPID"
  sleep 20
  echo "  alive_20s=$(kill -0 "$NEWPID" 2>/dev/null && echo YES || echo NO)"
  echo "  loop_count=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
  ps -eo pid,ppid,etime,args | grep -E '[b]aize_harness_loop' | cut -c1-150
else
  echo "  host=$H -> KEEP STOPPED (single-instance on .29)"
fi
echo
echo "== E. 90s 后四证 =="
sleep 70
echo "  --- 新日志头 20 行 ---"
head -n 20 "$LOG" 2>/dev/null | cut -c1-220
echo "  --- 判定（期望：1>=1 / 2=0 / 3=0 / 4>=1 / 5>=1）---"
echo "  proof1_loop_procs=$(pgrep -fc 'baize_harness_loop.sh' 2>/dev/null || echo 0)"
echo "  proof2_llm_pick_err=$(grep -c 'llm_pick: command not found' "$LOG" 2>/dev/null || echo 0)"
echo "  proof3_no_llm_skip=$(grep -c '无可用 LLM 候选' "$LOG" 2>/dev/null || echo 0)"
echo "  proof4_invoking=$(grep -c 'invoking cline' "$LOG" 2>/dev/null || echo 0)"
echo "  proof5_cline_procs=$(ps -eo args | grep '[c]line ' | grep -c 'glm-5.2' || echo 0)"
ps -eo pid,ppid,etime,args | grep '[c]line ' | grep 'glm-5.2' | cut -c1-170
echo
echo "== F. 日志尾部 =="
tail -n 15 "$LOG" 2>/dev/null | cut -c1-220
echo
echo "== G. git 状态（不清脏文件）=="
git -C "$GIT" log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git -C "$GIT" status --porcelain | wc -l)  ahead_behind=$(git -C "$GIT" rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
git -C "$GIT" status --porcelain | awk '{print $2}' | cut -d/ -f1-3 | sort | uniq -c | sort -rn | head -8
echo
echo "（写操作仅限：kill 本线 loop / 重启 .29 loop / 删 stale lock+gc.log）"
echo "=== DONE 298 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap29 date=2026-11-28 10:00:58 who=app.e0031982

== A. 前置：脚本版本 / 语法 ==
  mtime=2026-11-28 09:16:29.842285770 +0800
  llm_pick_occurrences=1  (期望=1，仅注释)
124:        # 2026-11-28 用户令：移除 llm_rotate.sh / llm_pick 额度轮换，直接用脚本内配好的 MODEL/CLINE_KEY
  cline_call:
132:          "${taskline[@]}" cline -c "$CWD" --auto-approve true -m "$MODEL" -k "$CLINE_KEY" -P openai-compatible -t "$CLINE_TIMEOUT" "$prompt" < /dev/null
  bash -n OK

== B. 清 stale git 锁（仅当无活跃 git 且锁龄>300s）==
  no index.lock
warning: There are too many unreachable loose objects; run 'git prune' to remove them.
  removed gc.log

== C. 停旧 loop（精确 PID + 兜底）==
  old_pids=[4066583 ]
  killed 4066583
  alive_after_kill=0
0

== D. 单实例：只 .29 起 loop ==
  host=.29 -> START
  launched PID=299357
  alive_20s=YES
  loop_count=2
 299357  299327       00:20 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
 299369  299357       00:20 cline -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --auto-approve true -m glm-5.2 -k 02

== E. 90s 后四证 ==
  --- 新日志头 20 行 ---
[loop] 2026-11-28 10:01:00 wake up, invoking cline ...
[2m[thinking] [0m[2mThe[0m[2m user has[0m[2m shared a very[0m[2m large task document[0m[2m (BAIZE[0m[2m_HARNESS_TASK[0m[2m.md).[0m[2m Let[0m[2m me understand[0m[2m what they're[0m[2m asking. Actual

Wait[0m[2m, let me re[0m[2m-read. The entire[0m[2m content[0m[2m appears[0m[2m to be the BA[0m[2mIZE_HARNESS[0m[2m_TASK.md file.[0m[2m There's no actual[0m[2m user question beyond[0m[2m sharing[0m[2

Actually[0m[2m, I think the[0m[2m user is showing[0m[2m me this[0m[2m task file and expects[0m[2m me to act as[0m[2m the harness agent —[0m[2m to[0m[2m read the task[0m[2m, understand the current[0m

But[0m[2m wait[0m[2m — there's no[0m[2m explicit "[0m[2muser[0m[2m_input" tag or[0m[2m mode indicator[0m[2m in[0m[2m this message. The[0m[2m message is just the[0m[2m raw[0m[2m content of the task

Given[0m[2m the context ([0m[2mthis is a coding[0m[2m agent environment[0m[2m, the[0m[2m working[0m[2m directory is the run[0m[2m/ folder[0m[2m,[0m[2m and the content[0m[2m is the harness[0m[2m task
1. Read[0m[2m and[0m[2m understand the current state[0m[2m of the harness task[0m[2m
2. Check[0m[2m on[0m[2m the progress[0m[2m of the running[0m[2m evaluation[0m[2m
3. Take[0m[2m appropriate action based[0m[2m on the operator[0m[2m instructions

Let me[0m[2m start by gathering context[0m[2m —[0m[2m reading the MEMORY[0m[2m_HARNESS.md[0m[2m file[0m[2m and[0m[2m checking the current state[0m[2m of things[0m[2m.[0m[2m Let me also[0m[2m check

Actually[0m[2m, I should be[0m[2m careful. Let[0m[2m me look[0m[2m at the actual files[0m[2m to[0m[2m understand the current state[0m[2m before[0m[2m doing[0m[2m anything. Let[0m[2m me read MEMORY[0m

Let me start[0m[2m by gathering context in[0m[2m parallel:[0m[2m
-[0m[2m Read MEMORY_HAR[0m[2mNESS.md
  --- 判定（期望：1>=1 / 2=0 / 3=0 / 4>=1 / 5>=1）---
  proof1_loop_procs=2
  proof2_llm_pick_err=0
0
  proof3_no_llm_skip=0
0
  proof4_invoking=1
  proof5_cline_procs=2
 299369  299357       01:30 cline -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --auto-approve true -m glm-5.2 -k 02_088EE9051AAE4BF0ABF
1800276 1475330    01:37:31 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run --aut

== F. 日志尾部 ==
[2m[thinking] [0m[2mSo[0m[2m the predictions are all[0m[2m flat files[0m[2m in a single directory[0m[2m (not per[0m[2m-harness subdirectories[0m[2m). The files[0m[2m are named like[0m[2m `[0m[2m<harn
The predictions are flat files prefixed by harness name. Let me count per-harness and find the progress files and launch script.
[36m[run_commands][0m bash -c 'cd /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/harness/swebench_verified_fu...
DeprecationWarning: AI SDK Warning (openai-compatible.chat / glm-5.2): Deprecated: "providerOptions key 'openai-compatible'". Use 'openaiCompatible' instead.
      at emitWarning (/$bunfs/root/cline-checkpoint-off:168902:24)
      at logWarnings (/$bunfs/root/cline-checkpoint-off:179200:16)
      at transform (/$bunfs/root/cline-checkpoint-off:179957:22)

DeprecationWarning: AI SDK Warning (openai-compatible.chat / glm-5.2): Deprecated: "providerOptions key 'openai-compatible'". Use 'openaiCompatible' instead.
      at emitWarning (/$bunfs/root/cline-checkpoint-off:168902:24)
      at logWarnings (/$bunfs/root/cline-checkpoint-off:179200:16)
      at transform (/$bunfs/root/cline-checkpoint-off:179957:22)

   [90m⎿ [0m[2m500 pi     500 opencode     500 hermes     500 deepseek-harness     500 codex... (+2 more)[0m
[2m[thinking] [0m[2mNow[0m[2m I have a[0m

== G. git 状态（不清脏文件）==
  HEAD 4ec7c75204 2026-11-28 10:02:28 +0800 ops-relay[12]: result @ 2026-11-28 10:02:28
  dirty=208  ahead_behind=0	0
    197 doc/BaiZe-ISEDA2027/run
      1 test_simple.py
      1 test_random_order_aggregation.py
      1 test_named_tuple_range.py
      1 test_formfield_callback.py
      1 test_fix2.py
      1 test_auth_form.py
      1 doc/BaiZe-ISEDA2027/Xmodel-LM

（写操作仅限：kill 本线 loop / 重启 .29 loop / 删 stale lock+gc.log）
=== DONE 298 | 2026-11-28 10:02:33 ===
```

---

## RUN_ID 299 · 2026-11-28 11:08:03 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
GIT=/nas_train/app.e0031982/code/super_intelligence_2035
echo "== A. pretrain S2 =="
ps -eo pid,ppid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt|[t]orchrun' | cut -c1-160 | head -8
ls -l --time-style=+%F_%T /tmp/baize_s2_launch.log /tmp/baize_s1_baize2b_worker.log 2>/dev/null
echo "  --- s2_launch tail ---"; tail -n 12 /tmp/baize_s2_launch.log 2>/dev/null | cut -c1-200
echo "  --- worker tail ---"; tail -n 4 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200
echo "  blend_hot_switch_hits=$(grep -c 'blend.hot.switch' /tmp/baize_s1_baize2b_worker.log 2>/dev/null || echo 0)"
echo "  latest_ckpt=$(cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null | head -8
echo
echo "== B. harness =="
ps -eo pid,ppid,etime,args | grep '[b]aize_harness_loop' | cut -c1-140
ps -eo pid,ppid,etime,args | grep '[c]line ' | grep 'glm-5.2' | cut -c1-160
tail -n 8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-200
ls -l --time-style=+%F_%T "$RUN/MEMORY_HARNESS.md"
echo
echo "== C. posttrain A5 =="
curl -s -m 3 -o /dev/null -w "  8097=%{http_code}\n" http://127.0.0.1:8097/v1/models 2>/dev/null || echo "  8097 DOWN"
curl -s -m 3 -o /dev/null -w "  tunnel3333=%{http_code}\n" http://127.0.0.1:3333 2>/dev/null || echo "  tunnel3333 DOWN"
ps -eo pid,etime,args | grep -E '[5]run_eval|[r]un_cline_script|[b]aize_posttrain' | cut -c1-140 | head -6
echo
echo "== D. zhulong thermo =="
ps -eo pid,etime,args | grep -E '[r]un_batch.sh|[r]un_one.sh' | cut -c1-140 | head -5
echo
echo "== E. git =="
cd "$GIT" && git log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git status --porcelain | wc -l) ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 299 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap12 date=2026-11-28 11:08:03
== A. pretrain S2 ==
-rw-r--r-- 1 app.e0031982 app.adm 62760 2026-11-28_11:00:37 /tmp/baize_s1_baize2b_worker.log
-rw-r--r-- 1 app.e0031982 app.adm  4036 2026-11-28_08:06:45 /tmp/baize_s2_launch.log
  --- s2_launch tail ---
  events    :
      2026-11-28 07:55      615562  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795815979.whag0pgpuap29.2245446.0
      2026-11-28 05:30       14596  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795814828.whag0pgpuap29.780408.0
      2026-11-28 05:18    50221762  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1795157328.whag0pgpuap29.2601340.0
      2026-11-20 01:22     9728818  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794982260.whag0pgpuap29.3800664.0
      2026-11-18 13:56       45844  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794980435.whag0pgpuap29.1801089.0
  log tail  :
[2026-11-28 08:06:35] rank0 @ 10.239.2.12（后台 ssh）
[2026-11-28 08:06:45] rank1 @ whag0pgpuap12（前台）
[2026-11-28 08:06:45] 结束：worker_rc=126 master_rc=126
[2026-11-28 08:06:45] 日志：/tmp/baize_s1_baize2b_worker.log / /tmp/baize_s1_baize2b_master.log ；摘要：/tmp/baize_s1_baize2b.log
  | /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh: line 282: /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun: Argument list too long
  --- worker tail ---
[rank9]: torch.distributed.DistBackendError: NCCL error in: /pytorch/torch/csrc/distributed/c10d/NCCLUtils.cpp:77, remote process exited or there was a network error, NCCL version 2.27.3
[rank9]: ncclRemoteError: A call failed possibly due to a network error or a remote process exiting prematurely.
[rank9]: Last error:
[rank9]: socketPollConnect: connect to 10.239.8.12<48213> returned Connection refused, exceeded error retry count after 35 attempts
  blend_hot_switch_hits=0
0
  latest_ckpt=350000
0, 0 %, 1455 MiB, 28
1, 0 %, 4 MiB, 26
2, 0 %, 4 MiB, 26
3, 0 %, 1455 MiB, 28
4, 0 %, 4 MiB, 27
5, 0 %, 4 MiB, 25
6, 0 %, 729 MiB, 29
7, 0 %, 4 MiB, 26

== B. harness ==

warning: There are too many unreachable loose objects; run 'git prune' to remove them.

[push] ahead=0 behind=0
[push] nothing of ours to commit.
Everything up-to-date
[push] push OK.
[loop] 2026-11-28 09:56:52 WAITING=1 (async task running) → sleep 900s
-rw-r----- 1 app.e0031982 app.adm 4141 2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md

== C. posttrain A5 ==
  8097=000
  8097 DOWN
  tunnel3333=000
  tunnel3333 DOWN

== D. zhulong thermo ==

== E. git ==
  HEAD 5e05bc8dba 2026-11-28 11:07:54 +0800 ops RUN_ID 299: all-line read-only status (pretrain S2 / harness / posttrain / zhulong)
  dirty=212 ahead_behind=0	0
（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 299 | 2026-11-28 11:08:05 ===
```

---

## RUN_ID 299 · 2026-11-28 11:08:07 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
GIT=/nas_train/app.e0031982/code/super_intelligence_2035
echo "== A. pretrain S2 =="
ps -eo pid,ppid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt|[t]orchrun' | cut -c1-160 | head -8
ls -l --time-style=+%F_%T /tmp/baize_s2_launch.log /tmp/baize_s1_baize2b_worker.log 2>/dev/null
echo "  --- s2_launch tail ---"; tail -n 12 /tmp/baize_s2_launch.log 2>/dev/null | cut -c1-200
echo "  --- worker tail ---"; tail -n 4 /tmp/baize_s1_baize2b_worker.log 2>/dev/null | cut -c1-200
echo "  blend_hot_switch_hits=$(grep -c 'blend.hot.switch' /tmp/baize_s1_baize2b_worker.log 2>/dev/null || echo 0)"
echo "  latest_ckpt=$(cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null)"
nvidia-smi --query-gpu=index,utilization.gpu,memory.used,temperature.gpu --format=csv,noheader 2>/dev/null | head -8
echo
echo "== B. harness =="
ps -eo pid,ppid,etime,args | grep '[b]aize_harness_loop' | cut -c1-140
ps -eo pid,ppid,etime,args | grep '[c]line ' | grep 'glm-5.2' | cut -c1-160
tail -n 8 /tmp/baize_harness_loop.log 2>/dev/null | cut -c1-200
ls -l --time-style=+%F_%T "$RUN/MEMORY_HARNESS.md"
echo
echo "== C. posttrain A5 =="
curl -s -m 3 -o /dev/null -w "  8097=%{http_code}\n" http://127.0.0.1:8097/v1/models 2>/dev/null || echo "  8097 DOWN"
curl -s -m 3 -o /dev/null -w "  tunnel3333=%{http_code}\n" http://127.0.0.1:3333 2>/dev/null || echo "  tunnel3333 DOWN"
ps -eo pid,etime,args | grep -E '[5]run_eval|[r]un_cline_script|[b]aize_posttrain' | cut -c1-140 | head -6
echo
echo "== D. zhulong thermo =="
ps -eo pid,etime,args | grep -E '[r]un_batch.sh|[r]un_one.sh' | cut -c1-140 | head -5
echo
echo "== E. git =="
cd "$GIT" && git log -1 --format='  HEAD %h %ad %s' --date=iso
echo "  dirty=$(git status --porcelain | wc -l) ahead_behind=$(git rev-list --left-right --count HEAD...origin/main 2>/dev/null)"
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 299 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap29 date=2026-11-28 11:08:07
== A. pretrain S2 ==
1800276 1475330    02:43:08 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
-rw-r--r-- 1 app.e0031982 app.adm 105325 2026-11-28_09:36:10 /tmp/baize_s1_baize2b_worker.log
-rw-r----- 1 app.e0031982 app.adm   4327 2026-11-28_08:06:20 /tmp/baize_s2_launch.log
  --- s2_launch tail ---
      2026-11-18 13:56       45844  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794980435.whag0pgpuap29.1801089.0
  log tail  :
      NOTE: Using experimental fast data loading logic. To disable, pass
          "--load_fast=false" and report issues on GitHub. More details:
          https://github.com/tensorflow/tensorboard/issues/4784
      
      TensorBoard 2.20.0 at http://0.0.0.0:6006/ (Press CTRL+C to quit)
[2026-11-28 08:06:10] rank0 @ 10.239.2.12（后台 ssh）
[2026-11-28 08:06:20] rank1 @ whag0pgpuap29（前台）
[2026-11-28 08:06:20] 结束：worker_rc=126 master_rc=126
[2026-11-28 08:06:20] 日志：/tmp/baize_s1_baize2b_worker.log / /tmp/baize_s1_baize2b_master.log ；摘要：/tmp/baize_s1_baize2b.log
  | /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh: line 282: /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun: Argument list too long
  --- worker tail ---
    time.sleep(monitor_interval)
  File "/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/distributed/elastic/multiprocessing/api.py", line 84, in _terminate_process_handler
    raise SignalException(f"Process {os.getpid()} got signal: {sigval}", sigval=sigval)
torch.distributed.elastic.multiprocessing.api.SignalException: Process 1832016 got signal: 15
  blend_hot_switch_hits=8
  latest_ckpt=350000
0, 0 %, 0 MiB, 25
1, 0 %, 0 MiB, 25
2, 0 %, 0 MiB, 27
3, 0 %, 0 MiB, 25
4, 0 %, 0 MiB, 28
5, 0 %, 0 MiB, 26
6, 0 %, 0 MiB, 25
7, 0 %, 0 MiB, 24

== B. harness ==
 299357       1    01:07:07 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_harness_loop.sh
1800276 1475330    02:43:08 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027
 create mode 100644 doc/ZhuLong_DAC2027/benchmark/daily-memories-designflow/daily_D_2026-11-28_r1649.md
Applied autostash.
[push] pull --rebase OK.
[push] committed.
To https://github.com/foamliu/super_intelligence_2035.git
   f7cee891e0..64c9475fa8  main -> main
[push] push OK.
[loop] 2026-11-28 11:00:31 WAITING=1 (async task running) → sleep 900s
-rw-r----- 1 app.e0031982 app.adm 4141 2026-11-27_16:41:14 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_HARNESS.md

== C. posttrain A5 ==
  8097=000
  8097 DOWN
  tunnel3333=000
  tunnel3333 DOWN

== D. zhulong thermo ==

== E. git ==
  HEAD 28374c6071 2026-11-28 11:08:05 +0800 ops-relay[12]: result @ 2026-11-28 11:08:05
  dirty=212 ahead_behind=0	0
（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 299 | 2026-11-28 11:08:09 ===
```

---

## RUN_ID 300 · 2026-11-28 11:09:10 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "== A. pretrain loop / cline 进程树 =="
ps -eo pid,ppid,stat,etime,pcpu,args | grep -E '[b]aize_pretrain_loop|[b]aize_s2_switch|[s]2_switch_executor' | cut -c1-170
P=$(pgrep -f 'cline.*cline_pretrain' | head -1)
echo "  pretrain_cline_pid=$P"
if [ -n "$P" ]; then
  echo "  ppid=$(ps -o ppid= -p $P) etime=$(ps -o etime= -p $P) stat=$(ps -o stat= -p $P) cpu=$(ps -o pcpu= -p $P) wchan=$(cat /proc/$P/wchan 2>/dev/null)"
  echo "  parent_chain:"; ps -o pid,ppid,args -p $(ps -o ppid= -p $P | tr -d ' ') 2>/dev/null | cut -c1-160
fi
echo
echo "== B. pretrain loop 日志（尾 30 行）=="
ls -l --time-style=+%F_%T /tmp/baize_pretrain_loop.log 2>/dev/null
tail -n 30 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo
echo "== C. 关键计数 =="
L=/tmp/baize_pretrain_loop.log
for pat in 'wake up' 'invoking cline' 'cline returned' '无可用 LLM 候选' 'llm_pick' 'S2' 'torchrun' 'E2BIG' 'Argument list too long'; do
  echo "  [$pat] = $(grep -c -- "$pat" "$L" 2>/dev/null || echo 0)"
done
echo
echo "== D. 最近 6 条非空日志 =="
grep -v '^$' "$L" 2>/dev/null | tail -6 | cut -c1-200
echo
echo "== E. 关键文件 mtime / WAITING =="
ls -l --time-style=+%F_%T "$RUN/MEMORY_PRETRAIN_2B.md" "$RUN/BAIZE_PRETRAIN_2B_TASK.md" 2>/dev/null
grep -n '^WAITING' "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null || echo '  WAITING 行缺失'
echo
echo "== F. S2 executor / launch 日志 =="
ls -l --time-style=+%F_%T /tmp/s2_switch_execution.log /tmp/baize_s2_launch.log /tmp/baize_s2_switch_train.log 2>/dev/null
tail -n 6 /tmp/s2_switch_execution.log 2>/dev/null | cut -c1-200
echo
echo "== G. GPU =="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -8
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 300 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap12 date=2026-11-28 11:09:10
== A. pretrain loop / cline 进程树 ==
  pretrain_cline_pid=

== B. pretrain loop 日志（尾 30 行）==

== C. 关键计数 ==
  [wake up] = 0
  [invoking cline] = 0
  [cline returned] = 0
  [无可用 LLM 候选] = 0
  [llm_pick] = 0
  [S2] = 0
  [torchrun] = 0
  [E2BIG] = 0
  [Argument list too long] = 0

== D. 最近 6 条非空日志 ==

== E. 关键文件 mtime / WAITING ==
-rw-r--r-- 1 app.e0031982 app.adm 30770 2026-11-28_08:32:34 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md
-rw-r--r-- 1 app.e0031982 app.adm 33286 2026-11-28_08:25:09 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md
184:WAITING: 0

== F. S2 executor / launch 日志 ==
-rw-r--r-- 1 app.e0031982 app.adm 4036 2026-11-28_08:06:45 /tmp/baize_s2_launch.log

== G. GPU ==
0, 0 %, 1455 MiB
1, 0 %, 4 MiB
2, 0 %, 4 MiB
3, 0 %, 1455 MiB
4, 0 %, 4 MiB
5, 0 %, 4 MiB
6, 0 %, 729 MiB
7, 0 %, 4 MiB
（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 300 | 2026-11-28 11:09:10 ===
```

---

## RUN_ID 300 · 2026-11-28 11:09:13 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "== A. pretrain loop / cline 进程树 =="
ps -eo pid,ppid,stat,etime,pcpu,args | grep -E '[b]aize_pretrain_loop|[b]aize_s2_switch|[s]2_switch_executor' | cut -c1-170
P=$(pgrep -f 'cline.*cline_pretrain' | head -1)
echo "  pretrain_cline_pid=$P"
if [ -n "$P" ]; then
  echo "  ppid=$(ps -o ppid= -p $P) etime=$(ps -o etime= -p $P) stat=$(ps -o stat= -p $P) cpu=$(ps -o pcpu= -p $P) wchan=$(cat /proc/$P/wchan 2>/dev/null)"
  echo "  parent_chain:"; ps -o pid,ppid,args -p $(ps -o ppid= -p $P | tr -d ' ') 2>/dev/null | cut -c1-160
fi
echo
echo "== B. pretrain loop 日志（尾 30 行）=="
ls -l --time-style=+%F_%T /tmp/baize_pretrain_loop.log 2>/dev/null
tail -n 30 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo
echo "== C. 关键计数 =="
L=/tmp/baize_pretrain_loop.log
for pat in 'wake up' 'invoking cline' 'cline returned' '无可用 LLM 候选' 'llm_pick' 'S2' 'torchrun' 'E2BIG' 'Argument list too long'; do
  echo "  [$pat] = $(grep -c -- "$pat" "$L" 2>/dev/null || echo 0)"
done
echo
echo "== D. 最近 6 条非空日志 =="
grep -v '^$' "$L" 2>/dev/null | tail -6 | cut -c1-200
echo
echo "== E. 关键文件 mtime / WAITING =="
ls -l --time-style=+%F_%T "$RUN/MEMORY_PRETRAIN_2B.md" "$RUN/BAIZE_PRETRAIN_2B_TASK.md" 2>/dev/null
grep -n '^WAITING' "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null || echo '  WAITING 行缺失'
echo
echo "== F. S2 executor / launch 日志 =="
ls -l --time-style=+%F_%T /tmp/s2_switch_execution.log /tmp/baize_s2_launch.log /tmp/baize_s2_switch_train.log 2>/dev/null
tail -n 6 /tmp/s2_switch_execution.log 2>/dev/null | cut -c1-200
echo
echo "== G. GPU =="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -8
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 300 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap29 date=2026-11-28 11:09:13
== A. pretrain loop / cline 进程树 ==
1475330       1 Ss    7-20:42:37  0.0 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh
  pretrain_cline_pid=1800276
  ppid=1475330 etime=   02:44:15 stat=Sl cpu=40.8 wchan=ep_poll
  parent_chain:
    PID    PPID COMMAND
1475330       1 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh

== B. pretrain loop 日志（尾 30 行）==
-rw-r----- 1 app.e0031982 app.adm 87465156 2026-11-28_11:09:14 /tmp/baize_pretrain_loop.log
2. Edit[0m[2m train.sh line[0m[2m 280: `"[0m[2mulimit -n[0m[2m 65536[0m[2m && cd ...[0m[2m`[0m[2m → `"[0m[2mulimit -H[0m[2mn 10485[0m[2m76 2[0m[2m>/dev/null;[0m[2m ulimit -n
3. Restart[0m[2m S2[0m[2m

Let me read the[0m[2m exact lines to edit[0m[2m.[0m[2m

Actually, I realize[0m[2m I need[0m[2m to be careful[0m[2m.[0m[2m The MEMORY[0m[2m line 38 says[0m[2m the[0m[2m 09:2[0m[2mx user[0m[2m command was[0m[2m "stop[0m[2m S1" and[0m[

But wait[0m[2m - the[0m[2m 09:2x[0m[2m command says "停[0m[2m了之后不要自己[0m[2m重启 S1"[0m[2m (don't restart[0m[2m S1).[0m[2m The[0m[2m 10:1[0m[2mx says[0m[2m "直接

But[0m[2m the 09[0m[2m:2x also[0m[2m says "本轮这是[0m[2m唯一动作" ([0m[2mthis round[0m[2m,[0m[2m this[0m[2m is the only action[0m[2m). Does[0m[2m this mean I[0m[2m shoul

OK[0m[2m, let me just[0m[2m proceed with fixing[0m[2m S[0m[2m2 and restarting it[0m[2m. The user[0m[2m's latest command[0m[2m (10:1[0m[2mx) is to[0m[2m start S2.[0m[2m

Actually, I need[0m[2m to reconsider[0m[2m. The user's[0m[2m CURRENT input is the[0m[2m task book,[0m[2m which has the[0m[2m 09:2x[0m[2m "stop S1[0m[2m" command[0m[2m at the top.[0m

I[0m[2m think what[0m[2m happened is:
1[0m[2m. The user[0m[2m gave the[0m[2m 08[0m[2m:1x command[0m[2m (start[0m[2m S2)
2[0m[2m. I stopped[0m[2m S1,[0m[2m started S2,[0m[2m S2 crashed[0m[2m
3. The[0m[2m user gave the[0m[2m 09:2x[0m[2m command (stop S[0m[2m1 - maybe[0m[2m they saw S2[0m[2m running and[0m[2m thought it was S[0m[2m1)[0m[2m
4. I confirmed[0m[2m S1 was stopped[0m[2m, updated[0m[2m MEMORY
5.[0m[2m The user gave the[0m[2m 10:1[0m[2mx command (start[0m[2m S2 directly)[0m[2m
6. I started[0m[2m S2 again[0m[2m, it crashed again[0m[2m (EMFILE)[0m[2m
7. Context[0m[2m was compacted[0m[2m
8. Now the[0m[2m agent loop is waking[0m[2m me up again[0m[2m with the task book[0m[2m

So[0m[2m the[0m[2m 10:1x[0m[2m is still[0m[2m the active[0m[2m command. I[0m[2m need to fix[0m[2m S[0m[2m2 and restart it[0m[2m.

But wait -[0m[2m looking[0m[2m at the task book[0m[2m,[0m[2m the 09:[0m[2m2x is at[0m[2m the TOP ([0m[2mmost recent in[0m[2m the task book).[0m[2m The 10:[0m[2m1x is in[0m[2m the

Actually, looking at[0m

== C. 关键计数 ==
  [wake up] = 1711
  [invoking cline] = 1685
  [cline returned] = 916
  [无可用 LLM 候选] = 0
0
  [llm_pick] = 0
0
  [S2] = 6572
  [torchrun] = 2612
  [E2BIG] = 133
  [Argument list too long] = 11

== D. 最近 6 条非空日志 ==
6. I started[0m[2m S2 again[0m[2m, it crashed again[0m[2m (EMFILE)[0m[2m
7. Context[0m[2m was compacted[0m[2m
8. Now the[0m[2m agent loop is waking[0m[2m me up again[0m[2m with the task book[0m[2m
So[0m[2m the[0m[2m 10:1x[0m[2m is still[0m[2m the active[0m[2m command. I[0m[2m need to fix[0m[2m S[0m[2m2 and restart it[0m[2m.
But wait -[0m[2m looking[0m[2m at the task book[0m[2m,[0m[2m the 09:[0m[2m2x is at[0m[2m the TOP ([0m[2mmost recent in[0m[2m the task book).[0m[2m The 10:[0m[2m1x is in[0m[2m the
Actually, looking at[0m[2m the MEMORY line[0m

== E. 关键文件 mtime / WAITING ==
-rw-r--r-- 1 app.e0031982 app.adm 30770 2026-11-28_08:32:34 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/BAIZE_PRETRAIN_2B_TASK.md
-rw-r--r-- 1 app.e0031982 app.adm 33286 2026-11-28_08:25:09 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md
184:WAITING: 0

== F. S2 executor / launch 日志 ==
-rw-r----- 1 app.e0031982 app.adm 4327 2026-11-28_08:06:20 /tmp/baize_s2_launch.log
-rw-r----- 1 app.e0031982 app.adm 2430 2026-11-28_05:19:17 /tmp/baize_s2_switch_train.log
-rw-r----- 1 app.e0031982 app.adm 3684 2026-11-28_05:22:27 /tmp/s2_switch_execution.log
[2026-11-28 05:22:11]   [2026-11-28 05:19:15] blend 就绪：13847 个 shard（权重+前缀对）
[2026-11-28 05:22:11]   [2026-11-28 05:19:15] WARN: launcher 无 --max-position-embeddings（训练不受影响，RoPE 逐位置计算）；导出 HF config 时必须写 max_position_embeddings=104857
[2026-11-28 05:22:11]   [2026-11-28 05:19:17] FATAL: 10.239.2.12 GPU 非空闲（vision 在跑？铁律：不抢）
[2026-11-28 05:22:11] ROLLBACK: killing+restarting with S1
[2026-11-28 05:22:27] ROLLBACK done PID=756629
[2026-11-28 05:22:27] ===== FAILED — ROLLED BACK =====

== G. GPU ==
0, 0 %, 0 MiB
1, 0 %, 0 MiB
2, 0 %, 0 MiB
3, 0 %, 0 MiB
4, 0 %, 0 MiB
5, 0 %, 0 MiB
6, 0 %, 0 MiB
7, 0 %, 0 MiB
（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 300 | 2026-11-28 11:09:15 ===
```

---

## RUN_ID 301 · 2026-11-28 12:03:36 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "== A. 训练进程 =="
ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt|[t]orchrun' | cut -c1-150 | head -6
echo "== B. GPU =="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -8
echo "== C. pretrain loop / cline =="
ps -eo pid,ppid,etime,pcpu,args | grep -E '[b]aize_pretrain_loop|[c]line.*cline_pretrain' | cut -c1-150
echo "== D. loop 日志 =="
ls -l --time-style=+%F_%T /tmp/baize_pretrain_loop.log 2>/dev/null
tail -n 8 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo "== E. MEMORY 顶部（是否已读到 data 通报）=="
head -n 3 "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null
ls -l --time-style=+%F_%T "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null
echo "== F. S2 启动日志 =="
ls -l --time-style=+%F_%T /tmp/baize_s2_launch.log 2>/dev/null
tail -n 8 /tmp/baize_s2_launch.log 2>/dev/null | cut -c1-200
echo "== G. ckpt =="
cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 301 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap12 date=2026-11-28 12:03:36
== A. 训练进程 ==
  28497       04:33 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nnodes=2 --n
  57352       04:11 node /home/app.e0031982/.npm-global/bin/cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.e0031982/code/super
  57359       04:11 /home/app.e0031982/.npm-global/lib/node_modules/cline/bin/.cline --data-dir /nas_train/app.e0031982/.cline_data -c /nas_train/app.
== B. GPU ==
0, 0 %, 17488 MiB
1, 100 %, 15871 MiB
2, 100 %, 15859 MiB
3, 100 %, 17286 MiB
4, 100 %, 15775 MiB
5, 100 %, 15781 MiB
6, 100 %, 16509 MiB
7, 100 %, 15797 MiB
== C. pretrain loop / cline ==
== D. loop 日志 ==
== E. MEMORY 顶部（是否已读到 data 通报）==
> 📎 **2026-11-28 11:1x · data 进展通报（供 pretrain 参考，非强制要求）**
>
> **一句话**：方案 C 全部完成、连续 fresh 复验 PASS；`blend_s2_preblend.tsv` 已 **13,847 → 180 shards / BLEND 14KB**，E2BIG 消除。data **WAITING=0**，无待答问题。
-rw-r--r-- 1 app.e0031982 app.adm 35673 2026-11-28_12:03:36 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md
== F. S2 启动日志 ==
-rw-r--r-- 1 app.e0031982 app.adm 4036 2026-11-28_08:06:45 /tmp/baize_s2_launch.log
      2026-11-20 01:22     9728818  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794982260.whag0pgpuap29.3800664.0
      2026-11-18 13:56       45844  /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/tb_logs/events.out.tfevents.1794980435.whag0pgpuap29.1801089.0
  log tail  :
[2026-11-28 08:06:35] rank0 @ 10.239.2.12（后台 ssh）
[2026-11-28 08:06:45] rank1 @ whag0pgpuap12（前台）
[2026-11-28 08:06:45] 结束：worker_rc=126 master_rc=126
[2026-11-28 08:06:45] 日志：/tmp/baize_s1_baize2b_worker.log / /tmp/baize_s1_baize2b_master.log ；摘要：/tmp/baize_s1_baize2b.log
  | /nas_train/app.e0031982/code/super_intelligence_2035/code/baize-llm/scripts/train.sh: line 282: /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun: Argument list too long
== G. ckpt ==
350000（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 301 | 2026-11-28 12:03:37 ===
```

---

## RUN_ID 301 · 2026-11-28 12:03:55 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] exec_host=$(hostname) date=$(date '+%F %T')"
RUN=/nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run
echo "== A. 训练进程 =="
ps -eo pid,etime,args | grep -E '[t]rain\.sh|[p]retrain_gpt|[t]orchrun' | cut -c1-150 | head -6
echo "== B. GPU =="
nvidia-smi --query-gpu=index,utilization.gpu,memory.used --format=csv,noheader 2>/dev/null | head -8
echo "== C. pretrain loop / cline =="
ps -eo pid,ppid,etime,pcpu,args | grep -E '[b]aize_pretrain_loop|[c]line.*cline_pretrain' | cut -c1-150
echo "== D. loop 日志 =="
ls -l --time-style=+%F_%T /tmp/baize_pretrain_loop.log 2>/dev/null
tail -n 8 /tmp/baize_pretrain_loop.log 2>/dev/null | cut -c1-200
echo "== E. MEMORY 顶部（是否已读到 data 通报）=="
head -n 3 "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null
ls -l --time-style=+%F_%T "$RUN/MEMORY_PRETRAIN_2B.md" 2>/dev/null
echo "== F. S2 启动日志 =="
ls -l --time-style=+%F_%T /tmp/baize_s2_launch.log 2>/dev/null
tail -n 8 /tmp/baize_s2_launch.log 2>/dev/null | cut -c1-200
echo "== G. ckpt =="
cat /nas_train/app.e0031982/code/BaiZe-ISEDA2027/nemo_experiments/baize2b/checkpoints/latest_checkpointed_iteration.txt 2>/dev/null
echo "（只读：未 kill / 未重启 / 未改任何文件）"
echo "=== DONE 301 | $(date '+%F %T') ==="
```

**输出**
```
[0] exec_host=whag0pgpuap29 date=2026-11-28 12:03:55
== A. 训练进程 ==
1094575       04:54 bash scripts/train.sh s1
1094656       04:53 ssh -n -o StrictHostKeyChecking=no -o ServerAliveInterval=30 -o BatchMode=yes 10.239.2.12 ulimit -n 1048576 && cd /nas_train/app.e
1106528       04:43 /nas_train/app.e0031982/miniforge3/envs/py310/bin/python /nas_train/app.e0031982/miniforge3/envs/py310/bin/torchrun --nnodes=2 --n
1800276    03:38:56 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA20
== B. GPU ==
0, 100 %, 15737 MiB
1, 100 %, 15719 MiB
2, 100 %, 15717 MiB
3, 100 %, 15711 MiB
4, 100 %, 15717 MiB
5, 100 %, 15719 MiB
6, 100 %, 15675 MiB
7, 100 %, 15707 MiB
== C. pretrain loop / cline ==
1475330       1  7-21:37:19  0.0 bash /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/baize_pretrain_loop.sh
1800276 1475330    03:38:56 41.2 cline --data-dir /nas_train/app.e0031982/.cline_pretrain -c /nas_train/app.e0031982/code/super_intelligence_2035/doc/
== D. loop 日志 ==
-rw-r----- 1 app.e0031982 app.adm 88231233 2026-11-28_12:03:32 /tmp/baize_pretrain_loop.log
      at logWarnings (/$bunfs/root/cline-checkpoint-off:179200:16)
      at transform (/$bunfs/root/cline-checkpoint-off:179957:22)

DeprecationWarning: AI SDK Warning (openai-compatible.chat / glm-5.2): Deprecated: "providerOptions key 'openai-compatible'". Use 'openaiCompatible' instead.
      at emitWarning (/$bunfs/root/cline-checkpoint-off:168902:24)
      at logWarnings (/$bunfs/root/cline-checkpoint-off:179200:16)
      at transform (/$bunfs/root/cline-checkpoint-off:179957:22)

== E. MEMORY 顶部（是否已读到 data 通报）==
> 📎 **2026-11-28 11:1x · data 进展通报（供 pretrain 参考，非强制要求）**
>
> **一句话**：方案 C 全部完成、连续 fresh 复验 PASS；`blend_s2_preblend.tsv` 已 **13,847 → 180 shards / BLEND 14KB**，E2BIG 消除。data **WAITING=0**，无待答问题。
-rw-r--r-- 1 app.e0031982 app.adm 35673 2026-11-28_12:03:36 /nas_train/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/MEMORY_PRETRAIN_2B.md
== F. S2 启动日志 ==
-rw-r----- 1 app.e0031982 app.adm 3944 2026-11-28_11:59:12 /tmp/baize_s2_launch.log
  log tail  :
      NOTE: Using experimental fast data loading logic. To disable, pass
          "--load_fast=false" and report issues on GitHub. More details:
          https://github.com/tensorflow/tensorboard/issues/4784
      
      TensorBoard 2.20.0 at http://0.0.0.0:6006/ (Press CTRL+C to quit)
[2026-11-28 11:59:02] rank0 @ 10.239.2.12（后台 ssh）
[2026-11-28 11:59:12] rank1 @ whag0pgpuap29（前台）
== G. ckpt ==
350000（只读：未 kill / 未重启 / 未改任何文件）
=== DONE 301 | 2026-11-28 12:03:55 ===
```

---

## RUN_ID 302 · 2026-11-28 12:04:41 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] host=$(hostname) date=$(date '+%F %T')"
W=/tmp/baize_s1_baize2b_worker.log
ls -l --time-style=+%F_%T "$W" /tmp/baize_s1_baize2b_master.log 2>/dev/null
echo "--- worker tail 12 ---"
tail -n 12 "$W" 2>/dev/null | cut -c1-220
echo "--- 最近 5 条 iter ---"
grep -E 'iteration[ =]|iter[ =]' "$W" 2>/dev/null | tail -5 | cut -c1-220
echo "--- nan_hits=$(grep -ci 'nan' "$W" 2>/dev/null || echo 0)  skip_hits=$(grep -ci 'skip' "$W" 2>/dev/null || echo 0)  blend_switch_hits=$(grep -ci 'blend.hot.switch' "$W" 2>/dev/null || echo 0) ---"
echo "=== DONE 302 | $(date '+%F %T') ==="
```

**输出**
```
[0] host=whag0pgpuap12 date=2026-11-28 12:04:41
-rw-r--r-- 1 app.e0031982 app.adm 10239 2026-11-28_10:57:50 /tmp/baize_s1_baize2b_master.log
-rw-r--r-- 1 app.e0031982 app.adm 62760 2026-11-28_11:00:37 /tmp/baize_s1_baize2b_worker.log
--- worker tail 12 ---
[rank10]: socketPollConnect: connect to 10.239.8.12<48213> returned Connection refused, exceeded error retry count after 35 attempts
[rank9]: Traceback (most recent call last):
[rank9]:   File "/nas_train/app.e0031982/code/BaiZe-ISEDA2027/pretrain_launcher.py", line 113, in <module>
[rank9]:     torch.distributed.barrier()
[rank9]:   File "/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/distributed/c10d_logger.py", line 81, in wrapper
[rank9]:     return func(*args, **kwargs)
[rank9]:   File "/nas_train/app.e0031982/miniforge3/envs/py310/lib/python3.10/site-packages/torch/distributed/distributed_c10d.py", line 4811, in barrier
[rank9]:     work = group.barrier(opts=opts)
[rank9]: torch.distributed.DistBackendError: NCCL error in: /pytorch/torch/csrc/distributed/c10d/NCCLUtils.cpp:77, remote process exited or there was a network error, NCCL version 2.27.3
[rank9]: ncclRemoteError: A call failed possibly due to a network error or a remote process exiting prematurely.
[rank9]: Last error:
[rank9]: socketPollConnect: connect to 10.239.8.12<48213> returned Connection refused, exceeded error retry count after 35 attempts
--- 最近 5 条 iter ---
--- nan_hits=0
0  skip_hits=0
0  blend_switch_hits=0
0 ---
=== DONE 302 | 2026-11-28 12:04:41 ===
```

---

## RUN_ID 302 · 2026-11-28 12:04:42 · host=`whag0pgpuap29` · exit=0

**命令**
```bash
echo "[0] host=$(hostname) date=$(date '+%F %T')"
W=/tmp/baize_s1_baize2b_worker.log
ls -l --time-style=+%F_%T "$W" /tmp/baize_s1_baize2b_master.log 2>/dev/null
echo "--- worker tail 12 ---"
tail -n 12 "$W" 2>/dev/null | cut -c1-220
echo "--- 最近 5 条 iter ---"
grep -E 'iteration[ =]|iter[ =]' "$W" 2>/dev/null | tail -5 | cut -c1-220
echo "--- nan_hits=$(grep -ci 'nan' "$W" 2>/dev/null || echo 0)  skip_hits=$(grep -ci 'skip' "$W" 2>/dev/null || echo 0)  blend_switch_hits=$(grep -ci 'blend.hot.switch' "$W" 2>/dev/null || echo 0) ---"
echo "=== DONE 302 | $(date '+%F %T') ==="
```

**输出**
```
[0] host=whag0pgpuap29 date=2026-11-28 12:04:42
-rw-r--r-- 1 app.e0031982 app.adm 157602 2026-11-28_12:04:41 /tmp/baize_s1_baize2b_master.log
-rw-r--r-- 1 app.e0031982 app.adm  99934 2026-11-28_11:59:53 /tmp/baize_s1_baize2b_worker.log
--- worker tail 12 ---
whag0pgpuap29:1107188:1154816 [1] NCCL INFO Channel 01/1 : 0[0] -> 9[1] [receive] via NET/IB/2/Shared
whag0pgpuap29:1107193:1154818 [4] NCCL INFO Channel 01/1 : 0[0] -> 12[4] [receive] via NET/IB/6/Shared
whag0pgpuap29:1107200:1154815 [6] NCCL INFO Channel 05/1 : 0[0] -> 14[6] [receive] via NET/IB/7/Shared
whag0pgpuap29:1107203:1154814 [7] NCCL INFO Channel 05/1 : 0[0] -> 15[7] [receive] via NET/IB/9/Shared
whag0pgpuap29:1107195:1154817 [5] NCCL INFO Channel 01/1 : 0[0] -> 13[5] [receive] via NET/IB/8/Shared
whag0pgpuap29:1107193:1154818 [4] NCCL INFO Channel 05/1 : 0[0] -> 12[4] [receive] via NET/IB/6/Shared
whag0pgpuap29:1107188:1154816 [1] NCCL INFO Channel 05/1 : 0[0] -> 9[1] [receive] via NET/IB/2/Shared
whag0pgpuap29:1107192:1154819 [3] NCCL INFO Channel 01/1 : 0[0] -> 11[3] [receive] via NET/IB/3/Shared
whag0pgpuap29:1107195:1154817 [5] NCCL INFO Channel 05/1 : 0[0] -> 13[5] [receive] via NET/IB/8/Shared
whag0pgpuap29:1107192:1154819 [3] NCCL INFO Channel 05/1 : 0[0] -> 11[3] [receive] via NET/IB/3/Shared
INFO:megatron.core.timers:(min, max) time across ranks (ms):
    load-checkpoint ................................: (4843.52, 4844.01)
--- 最近 5 条 iter ---
--- nan_hits=0
0  skip_hits=0
0  blend_switch_hits=8 ---
=== DONE 302 | 2026-11-28 12:04:42 ===
```

---

## RUN_ID 302 · 2026-11-28 15:35:48 · host=`whag0pgpuap12` · exit=0

**命令**
```bash
echo "[0] host=$(hostname) date=$(date '+%F %T')"
W=/tmp/baize_s1_baize2b_worker.log
ls -l --time-style=+%F_%T "$W" /tmp/baize_s1_baize2b_master.log 2>/dev/null
echo "--- worker tail 12 ---"
tail -n 12 "$W" 2>/dev/null | cut -c1-220
echo "--- 最近 5 条 iter ---"
grep -E 'iteration[ =]|iter[ =]' "$W" 2>/dev/null | tail -5 | cut -c1-220
echo "--- nan_hits=$(grep -ci 'nan' "$W" 2>/dev/null || echo 0)  skip_hits=$(grep -ci 'skip' "$W" 2>/dev/null || echo 0)  blend_switch_hits=$(grep -ci 'blend.hot.switch' "$W" 2>/dev/null || echo 0) ---"
echo "=== DONE 302 | $(date '+%F %T') ==="
```

**输出**
```
[0] host=whag0pgpuap12 date=2026-11-28 15:35:48
-rw-r--r-- 1 app.e0031982 app.adm 33689 2026-11-28_15:28:06 /tmp/baize_s1_baize2b_master.log
-rw-r--r-- 1 app.e0031982 app.adm 33785 2026-11-28_15:28:07 /tmp/baize_s1_baize2b_worker.log
--- worker tail 12 ---
[rank10]: torch.distributed.DistBackendError: NCCL error in: /pytorch/torch/csrc/distributed/c10d/NCCLUtils.cpp:77, invalid usage (run with NCCL_DEBUG=WARN for details), NCCL version 2.27.3
[rank10]: ncclInvalidUsage: This usually reflects invalid usage of NCCL library.
[rank10]: Last error:
[rank10]: Duplicate GPU detected : rank 10 and rank 2 both on CUDA device 40000
[rank8]:[W1128 15:28:06.491471174 ProcessGroupNCCL.cpp:1538] Warning: WARNING: destroy_process_group() was not called before program exit, which can leak resources. For more info, please see https://pytorch.org/docs/stab
W1128 15:28:07.144000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690444 closing signal SIGTERM
W1128 15:28:07.145000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690446 closing signal SIGTERM
W1128 15:28:07.145000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690448 closing signal SIGTERM
W1128 15:28:07.146000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690450 closing signal SIGTERM
W1128 15:28:07.146000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690451 closing signal SIGTERM
W1128 15:28:07.146000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690453 closing signal SIGTERM
W1128 15:28:07.147000 2690347 site-packages/torch/distributed/elastic/multiprocessing/api.py:900] Sending process 2690455 closing signal SIGTERM
--- 最近 5 条 iter ---
--- nan_hits=0
0  skip_hits=0
0  blend_switch_hits=0
0 ---
=== DONE 302 | 2026-11-28 15:35:48 ===
```
