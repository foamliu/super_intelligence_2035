
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
