# OPS OUTBOX — 中继执行结果（**只增不改**，审计留痕）

> 由 `ops_relay.sh` 自动追加：每段含 `RUN_ID · 时间 · host · exit code`、**命令原文**、**输出**。
> 🚫 **不要手改本文件**。

---

## RUN_ID 1 · 2026-10-05 12:31:28 · host=`VM-0-6-ubuntu` · exit=0

**命令**
```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. loop 进程（应为各 1 个）==="
pgrep -af 'watch_(news|research)_loop.sh' | cut -c1-140 || echo "(没有 watch_*_loop.sh 在跑)"
echo
echo "=== 2. loop 日志尾部（找 额度已用完 / 403 / 429）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log; do
  echo "--- $f ---"; tail -20 "$f" 2>/dev/null | cut -c1-200 || echo "(无此日志)"
done
echo
echo "=== 3. ⭐OOM 痕迹（2G 机器的头号嫌疑）==="
(dmesg -T 2>/dev/null || sudo -n dmesg -T 2>/dev/null) | grep -iE 'oom|killed process' | tail -15 || echo "(读不到 dmesg 或无 OOM 记录)"
echo
echo "=== 4. 资源 ==="
free -m; echo; df -h / /home 2>/dev/null | head -5
echo
echo "=== 5. CPU top5 ==="
ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu 2>/dev/null | head -6 | cut -c1-140
echo
echo "=== 6. cline base（只看 base，不打 key）==="
grep -o '"openAiBaseUrl"[^,}]*' ~/.cline/data/globalState.json 2>/dev/null || echo "(无 globalState.json)"
echo
echo "=== 7. git 状态 ==="
cd ~/super_intelligence_2035 2>/dev/null && git log --oneline -3 && echo '--- dirty ---' && git status --short | head -10
```

**输出**
```
=== 0. 基本信息 ===
VM-0-6-ubuntu
2026-10-05 12:31:28 CST
 12:31:28 up  3:21,  5 users,  load average: 0.22, 0.44, 0.24

=== 1. loop 进程（应为各 1 个）===
98701 bash watch_news_loop.sh
98707 node /home/liuyang/.nvm/versions/node/v24.21.0/bin/cline -c /home/liuyang/super_intelligence_2035/doc/personal-watch/run --auto-approv
98716 /home/liuyang/.nvm/versions/node/v24.21.0/lib/node_modules/cline/bin/.cline -c /home/liuyang/super_intelligence_2035/doc/personal-watc

=== 2. loop 日志尾部（找 额度已用完 / 403 / 429）===
--- /tmp/watch_news_loop.log ---

[0m[2mActually[0m[2m,[0m[2m h[0m[2mmm[0m[2m,[0m[2m the[0m[2m point[0m[2m of[0m[2m the[0m[2m log[0m[2m is[0m[2m genuine[0m[2m periodic[0m[2m runs[0m[2m.[0m[2m This[0m[

[0m[2mTrade[0m[2m-off[0m[2m:[0m[2m authenticity[0m[2m vs[0m[2m time[0m[2m.[0m[2m I[0m[2m think[0m[2m running[0m[2m full[0m[2m mode[0m[2m once[0m[2m is[0m[2m the[0m[2m r

[0m[2mLet[0m[2m me[0m[2m check[0m[2m pip[0m[2m progress[0m[2m first[0m[2m.[0m
[36m[run_commands][0m tail -15 /tmp/pip_boot.log 2>/dev/null; echo '--- proc ---'; ps aux | grep -E 'get-pip|pip install' | grep -v grep | ...
   [90m⎿ [0m[2m+ rm -f /tmp/get-pip.py + curl -sS -m 120 -o /tmp/get-pip.py https://bootstra...[0m
[2m[thinking] [0m[2mStill[0m[2m downloading[0m[2m get[0m[2m-p[0m[2mip[0m[2m.py[0m[2m ([0m[2mslow[0m[2m from[0m[2m bootstrap[0m[2m.p[0m[2myp[0m[2ma[0m[2m.io[0m[2m).[0m[

[0m[2mActually[0m[2m let[0m[2m me[0m[2m use[0m[2m the[0m[2m time[0m[2m:[0m[2m run[0m[2m the[0m[2m cycle[0m[2m_run[0m[2m.py[0m[2m in[0m[2m --[0m[2mrecord[0m[2m mode[0m

[0m[2mLet[0m[2m me[0m[2m instead[0m[2m do[0m[2m useful[0m[2m independent[0m[2m work[0m[2m:[0m[2m prepare[0m[2m the[0m[2m memory[0m[2m updates[0m[2m ([0m[2md[0m[2mraft[0m

[0m[2mLet[0m[2m me[0m[2m read[0m[2m fetch[0m[2m_[0m[2marchive[0m[2m.py[0m[2m argparse[0m[2m section[0m[2m.

[0m[2mMeanwhile[0m[2m poll[0m[2m pip[0m[2m.

[0m[2mLet[0m[2m me[0m[2m do[0m[2m both[0m[2m in[0m[2m one[0m[2m call[0m[2m:[0m[2m poll[0m[2m +[0m[2m grep[0m[2m fetch[0m[2m args[0m[2m.[0m
[36m[run_commands][0m cd /home/liuyang/super_intelligence_2035/doc/personal-watch/run && grep -n 'add_argument\|args\.' news/archive/fetch_...
--- /tmp/watch_research_loop.log ---

=== 3. ⭐OOM 痕迹（2G 机器的头号嫌疑）===

=== 4. 资源 ===
               total        used        free      shared  buff/cache   available
Mem:            3723        1062        1345           2        1608        2661
Swap:           1987           0        1987

Filesystem      Size  Used Avail Use% Mounted on
/dev/vda2        69G  6.8G   60G  11% /
/dev/vda2        69G  6.8G   60G  11% /

=== 5. CPU top5 ===
    PID %CPU %MEM     ELAPSED COMMAND
  98716  2.2  8.9       04:53 /home/liuyang/.nvm/versions/node/v24.21.0/lib/node_modules/cline/bin/.cline -c /home/liuyang/super_intelligenc
   7493  1.1  1.8    03:20:01 /usr/local/qcloud/YunJing/YDEyes/YDService
   6375  1.0  0.7    03:21:15 barad_agent
  13993  0.2  6.0    03:01:16 /home/liuyang/.nvm/versions/node/v24.21.0/lib/node_modules/cline/bin/.cline --cline-hub-daemon --cwd /home/liu
 101488  0.2  0.3       00:35 curl -sS -m 120 -o /tmp/get-pip.py https://bootstrap.pypa.io/get-pip.py

=== 6. cline base（只看 base，不打 key）===
(无 globalState.json)

=== 7. git 状态 ===
6ba3957 harness: R68 kimi serial 10/30 scored (8 resolved, 0 quota-blocked) + SWEBENCH_COMPARE.html regenerated (kimi single-model) + gen_kimi_compare.py
8067230 personal-watch: 新建 ops 中继 ops_relay.sh + ops/{inbox,outbox,README}（纯bash零token，loop停着也能远程运维；修掉 BaiZe'只执行第一个bash块'的坑+加 git clean/reset/杀中继 拦截）；内置 RUN_ID 1 诊断块（进程/日志/OOM/资源/cline base）
1407390 update
--- dirty ---
 M doc/personal-watch/run/news/policy/EARLY_WARNING.md
 M doc/personal-watch/run/news/policy/EDA.md
 M doc/personal-watch/run/news/policy/EVENTS.csv
 M doc/personal-watch/run/news/policy/EVENTS.md
 M doc/personal-watch/run/news/policy/INDEX_FILES.md
 M doc/personal-watch/run/news/policy/SIGNALS.md
 M doc/personal-watch/run/news/policy/TAXONOMY.md
?? doc/personal-watch/run/daily-memories-news/2026-10-05.md
?? doc/personal-watch/run/news/policy/cycle_run.py
```

---

## RUN_ID 2 · 2026-10-05 14:40:24 · host=`VM-0-6-ubuntu` · exit=0

**命令**
```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. loop 进程（应为各 1 个）==="
pgrep -af 'watch_(news|research)_loop.sh' | cut -c1-140 || echo "(没有 watch_*_loop.sh 在跑)"
echo
echo "=== 2. loop 日志尾部（找 额度已用完 / 403 / 429）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log; do
  echo "--- $f ---"; tail -20 "$f" 2>/dev/null | cut -c1-200 || echo "(无此日志)"
done
echo
echo "=== 3. ⭐OOM 痕迹（2G 机器的头号嫌疑）==="
(dmesg -T 2>/dev/null || sudo -n dmesg -T 2>/dev/null) | grep -iE 'oom|killed process' | tail -15 || echo "(读不到 dmesg 或无 OOM 记录)"
echo
echo "=== 4. 资源 ==="
free -m; echo; df -h / /home 2>/dev/null | head -5
echo
echo "=== 5. CPU top5 ==="
ps -eo pid,pcpu,pmem,etime,args --sort=-pcpu 2>/dev/null | head -6 | cut -c1-140
echo
echo "=== 6. cline base（只看 base，不打 key）==="
grep -o '"openAiBaseUrl"[^,}]*' ~/.cline/data/globalState.json 2>/dev/null || echo "(无 globalState.json)"
echo
echo "=== 7. git 状态 ==="
cd ~/super_intelligence_2035 2>/dev/null && git log --oneline -3 && echo '--- dirty ---' && git status --short | head -10
```

**输出**
```
=== 0. 基本信息 ===
VM-0-6-ubuntu
2026-10-05 14:40:24 CST
 14:40:24 up  5:30,  4 users,  load average: 0.09, 0.09, 0.15

=== 1. loop 进程（应为各 1 个）===
98701 bash watch_news_loop.sh
108954 bash watch_research_loop.sh

=== 2. loop 日志尾部（找 额度已用完 / 403 / 429）===
--- /tmp/watch_news_loop.log ---
- `MEMORY_NEWS.md`：滚动归档两段旧文（`2026-10-03`/`2026-10-04.md`）后 **31,967 B → 27,588 B**（≤32 KB 达标）；更新进度快照（第 5 轮完成态 + 第 6 轮启动 + pid）�
- `daily-memories-news/2026-10-05.md`：追加心跳 `[14:30] wake …` + 第 5 轮完整轮次记录（含 pid/日志）
- `news/policy/README.md` §4 同步（语料 / EVENTS 63,398 / q<0.05=44、门槛=19 / 最高 AUC `A13 Δ=30` 0.740 / STABILITY_LOG 6 行）

**3. 提交与推送**
- 提交第 5 轮 N1 产物（EVENTS 63,398 等 22 个本线文件，含新增 `chinanews-2017/2018.jsonl.gz` 分片）→ `2009a94`
- 补提 pid 记录 → `7b93644`，均已 `push origin main` ✅

**4. 启动 N1 第 6 轮**
- 后台抓取（倒序 `2017-10-30 → 2016-01-01`，`fetch pid 160525`/`python 160527`）+ watcher（`pid 160526`，按 `kill -0` 判定，抓完自动 `--index` + `cycle_run.py --with-l2`，日志 
- 已确认在跑：`next_day 2017-10-26 / done_days 3264 / recs 1,954,543`

## 校验结果
- 本线工作区**无未提交文件**（git 干净）
- 抓取进程唯一（1 个 python）、watcher 按 pid 等待（避开了历史 `pgrep -f` 自匹配死锁）
- `MEMORY_NEWS.md` 27,588 B < 32 KB；`WAITING:` 仅顶部出现一次

下一轮唤醒时：等第 6 轮抓取 + 链跑完，核对 `STABILITY_LOG.md` 第 7 行与产物，并继续常态新闻采集。
[loop] 2026-10-05 14:25:31 cline returned (exit 0); log=/tmp/watch_news_cline_last.log
[loop] 2026-10-05 14:25:31 WAITING=1 (no pending follow-up) → sleep 1800s
--- /tmp/watch_research_loop.log ---
- 原因：**UTC 仍为周一**，arXiv **周一公告尚未刷新**（最近批次仍 `2026-10-02`，与第十五~十七轮同批去重），**0 新增属正常，非「无数据」**。实际日期�

### 3. 落盘（只 add 本线文件）
- `research/2026-10-05.md`（追加「第十八轮」章节 + R1′ 表）
- `research/ARXIV_API.md`（新增 **§9.20**；并修正插入顺序为 9.17→9.18→9.19→9.20）
- `research/INDEX.md`（＋🗓 第十八轮行）、`research/SEEN.md`（＋第十八轮备注，无新行）
- `research/papers.jsonl`（不变，本轮 0 收录）；累计仍 **收录 91 / 候选 487 / 累计抓取 578**
- `MEMORY_RESEARCH.md`（快照 + 状态头 + 流水更新；**32604 B ≤ 32KB**；`WAITING: 1` 仍仅顶部 1 处）
- `daily-memories-research/2026-10-05.md`（💓 心跳行 + 第十八轮记录）

### 4. 复核第 3 批 A/B 交付
TOP-K（`takeaway`/`action` 20 条）+ `TAKEAWAYS.md`（5 条）+ 视频线（`SHORTLIST.md` 17 / `scripts/` 3）**已交付未变**；无新增 → 不重跑（诚实标注）。📧 邮件职能**�

### 5. 回归 & 提交
- `test_arxiv_fetch.py` **49/49 PASS** · `test_top_k.py` **25/25 PASS**（离线）。
- commit `22fa5e4` → **已 push**（`af30d1f..22fa5e4 main -> main`）；`git status` 本线工作树 clean，未卷入 news 线在途文件（未用 `git add -A`）。

**下一步建议**：留意 **周一 20:00 ET（= 周二 UTC 00:00）后公告刷新**，下轮预计会有新增；视频 **V3（生成）仍待用户确认运行机工具链**后再动。
[loop] 2026-10-05 14:35:11 cline returned (exit 0); log=/tmp/watch_research_cline_last.log
[loop] 2026-10-05 14:35:11 WAITING=1 (no pending follow-up) → sleep 1800s

=== 3. ⭐OOM 痕迹（2G 机器的头号嫌疑）===

=== 4. 资源 ===
               total        used        free      shared  buff/cache   available
Mem:            3723        1383        1240           2        1384        2340
Swap:           1987           2        1985

Filesystem      Size  Used Avail Use% Mounted on
/dev/vda2        69G  7.4G   59G  12% /
/dev/vda2        69G  7.4G   59G  12% /

=== 5. CPU top5 ===
    PID %CPU %MEM     ELAPSED COMMAND
 170503 98.7 13.4       00:03 /usr/bin/python3 /home/liuyang/super_intelligence_2035/doc/personal-watch/run/news/policy/eda.py
  13993  1.5  9.9    05:10:12 /home/liuyang/.nvm/versions/node/v24.21.0/lib/node_modules/cline/bin/.cline --cline-hub-daemon --cwd /home/liu
   7493  1.2  1.9    05:28:57 /usr/local/qcloud/YunJing/YDEyes/YDService
   6375  1.0  0.7    05:30:11 barad_agent
 170502  0.9  0.4       00:03 python3 news/policy/cycle_run.py --with-l2

=== 6. cline base（只看 base，不打 key）===
(无 globalState.json)

=== 7. git 状态 ===
1c1f3f3 ops: RUN_ID 2 诊断块 — 追因 research 线为何缺席 + loop 保活机制排查(cron/systemd/screen/自启/进程树/脚本守护逻辑)，并记录 RUN_ID 1 结论(非OOM/非资源; 只有 news 在跑; 机器 09:10 左右重启过)
5eaaa72 personal-watch/news: 🚨 台账诚信处置 — ① G2'④ 改为可达成且可核验(连续7自然日/每天>=1次真实重跑/间隔>=20h; record-only不计入; 未达标要如实写) ② §4 新增铁律⑨台账诚信+⑩指标未达标如实写(禁补造/回填/模拟/改口径/刷台账); 并记录诊断结论(非OOM/非资源)
f8bfbb5 personal-watch/ops_relay: 修根因 — git_publish 推送前先 fetch+pull --rebase（仓库与 4 条 BaiZe 线共享远端，不 rebase 必被拒），否则中继结果永远推不上来
--- dirty ---
 M doc/personal-watch/run/news/archive/.progress.json
 M doc/personal-watch/run/news/archive/INDEX_FILES.md
 M doc/personal-watch/run/news/archive/PROGRESS.md
 M doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz
?? doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz
```

---

## RUN_ID 3 · 2026-10-05 15:28:08 · host=`VM-0-6-ubuntu` · exit=0

**命令**
```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'
cd ~/super_intelligence_2035 2>/dev/null || exit 1
echo
echo "=== 1. ⭐ 语料文件体积（重点）==="
ls -lh doc/personal-watch/run/news/archive/*.jsonl* 2>/dev/null | cut -c1-140 || echo "(无 jsonl 语料)"
echo '--- 精确字节数（便于判断能否进 git）---'
du -b doc/personal-watch/run/news/archive/*.jsonl* 2>/dev/null | sort -rn | head -10
echo
echo "=== 2. 整个 news/archive 目录占用 ==="
du -sh doc/personal-watch/run/news/archive 2>/dev/null
du -sh doc/personal-watch/run/news 2>/dev/null
echo
echo "=== 3. 是否已被 git 跟踪（关键！）==="
git ls-files -s doc/personal-watch/run/news/archive/ | cut -c1-140
echo
echo "=== 4. ⭐ 历史污染程度（该文件在 git 历史里累计占多少）==="
for f in doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz; do
  echo "--- $f ---"
  git log --oneline -- "$f" 2>/dev/null | head -5 | cut -c1-120
done
echo '--- 仓库 .git 实际体积 ---'
du -sh .git 2>/dev/null
echo
echo "=== 5. 是否已 push 到远端（污染是否传出去了）==="
git log --oneline -5 -- doc/personal-watch/run/news/archive/ | cut -c1-140
echo '--- 远端是否已含该文件 ---'
git cat-file -e origin/main:doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz 2>/dev/null && echo "⚠️ 远端已含 2017 语料（已污染）" || echo "✅ 远端不含 2017 语料"
echo
echo "=== 6. 是否有 .gitignore / .gitattributes 规则 ==="
for f in .gitignore .gitattributes doc/personal-watch/run/news/archive/.gitignore doc/personal-watch/run/news/.gitignore; do
  echo "--- $f ---"; cat "$f" 2>/dev/null | cut -c1-140 || echo "(不存在)"
done
echo
echo "=== 7. 每轮抓取是否会持续生成新分片（判断增长趋势）==="
ls -la doc/personal-watch/run/news/archive/ 2>/dev/null | grep -E 'jsonl|progress|PROGRESS' | cut -c1-140
```

**输出**
```
=== 0. 基本信息 ===
VM-0-6-ubuntu
2026-10-05 15:28:08 CST

=== 1. ⭐ 语料文件体积（重点）===
-rw-rw-r-- 1 liuyang liuyang  15M Oct  5 15:28 doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  11M Oct  5 14:53 doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  11M Oct  5 13:58 doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  12M Oct  5 13:46 doc/personal-watch/run/news/archive/chinanews-2019.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  12M Oct  5 13:43 doc/personal-watch/run/news/archive/chinanews-2020.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 9.3M Oct  5 13:22 doc/personal-watch/run/news/archive/chinanews-2021.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 9.9M Oct  5 12:46 doc/personal-watch/run/news/archive/chinanews-2022.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 7.4M Oct  5 12:46 doc/personal-watch/run/news/archive/chinanews-2023.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 7.2M Oct  5 12:46 doc/personal-watch/run/news/archive/chinanews-2024.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 6.9M Oct  5 12:46 doc/personal-watch/run/news/archive/chinanews-2025.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 5.6M Oct  5 12:46 doc/personal-watch/run/news/archive/chinanews-2026.jsonl.gz
--- 精确字节数（便于判断能否进 git）---
15556999	doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz
12265872	doc/personal-watch/run/news/archive/chinanews-2019.jsonl.gz
12228659	doc/personal-watch/run/news/archive/chinanews-2020.jsonl.gz
11145051	doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz
10616975	doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz
10319596	doc/personal-watch/run/news/archive/chinanews-2022.jsonl.gz
9707401	doc/personal-watch/run/news/archive/chinanews-2021.jsonl.gz
7660242	doc/personal-watch/run/news/archive/chinanews-2023.jsonl.gz
7449410	doc/personal-watch/run/news/archive/chinanews-2024.jsonl.gz
7130667	doc/personal-watch/run/news/archive/chinanews-2025.jsonl.gz

=== 2. 整个 news/archive 目录占用 ===
105M	doc/personal-watch/run/news/archive
124M	doc/personal-watch/run/news

=== 3. 是否已被 git 跟踪（关键！）===
100644 c7861e05262d29e1af1d64fc1d54c2bb8fa02c0f 0	doc/personal-watch/run/news/archive/.gitignore
100644 2374326527ac2c16f965360c31284734f70ab244 0	doc/personal-watch/run/news/archive/.progress.json
100644 e5b8dee487a69001e700993f16f12f2188724143 0	doc/personal-watch/run/news/archive/INDEX_FILES.md
100644 ae9123c4e5808704cec18e5de7431051716595fc 0	doc/personal-watch/run/news/archive/PROGRESS.md
100644 0f849e7d2db14cb66783b6490458eb73daaed759 0	doc/personal-watch/run/news/archive/README.md
100644 db49562036054b3f64cfe074c2f8de072f9721fd 0	doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz
100644 995e32ce026b602d51d2e43f086fce9fbe593ecd 0	doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz
100644 811974a26f677c52108e08747c219c69e83b8b4d 0	doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz
100644 9cb1fb1e964294f20773f356a124fac9b2244317 0	doc/personal-watch/run/news/archive/chinanews-2019.jsonl.gz
100644 cfd2ddf8d8b78334d373f7ddfec3f0976f15a286 0	doc/personal-watch/run/news/archive/chinanews-2020.jsonl.gz
100644 aa25e37aba7ca4f938f44b52c2715e425786ca24 0	doc/personal-watch/run/news/archive/chinanews-2021.jsonl.gz
100644 bdafbb69a08e724bd78c5825f2b457910310302e 0	doc/personal-watch/run/news/archive/chinanews-2022.jsonl.gz
100644 ab5d41a800876415f38eef7f85c2ca29548c5cd3 0	doc/personal-watch/run/news/archive/chinanews-2023.jsonl.gz
100644 a33a1a17b598241662357535c824a81df52e0161 0	doc/personal-watch/run/news/archive/chinanews-2024.jsonl.gz
100644 a55d024ff0dfdaed8ac00eaef50add648016d778 0	doc/personal-watch/run/news/archive/chinanews-2025.jsonl.gz
100644 42c88594c9075d92497ff5a10e05b029c4f026ea 0	doc/personal-watch/run/news/archive/chinanews-2026.jsonl.gz
100644 b32c2c4d8bc40db58dceebf64000c4cab899ca6d 0	doc/personal-watch/run/news/archive/fetch_archive.py

=== 4. ⭐ 历史污染程度（该文件在 git 历史里累计占多少）===
--- doc/personal-watch/run/news/archive/chinanews-2016.jsonl.gz ---
b139a9e news 2026-10-05: N1 r6 语料→2,267,862/11片(2016起) + 第十五轮 news +4(华为×高通专利·台达×�
--- doc/personal-watch/run/news/archive/chinanews-2017.jsonl.gz ---
b139a9e news 2026-10-05: N1 r6 语料→2,267,862/11片(2016起) + 第十五轮 news +4(华为×高通专利·台达×�
2009a94 news 2026-10-05 第5轮: N1 语料→1,952,411条/10片(进2017-2018); 全链重跑 EVENTS 63,398(q<0.05=44,门�
--- doc/personal-watch/run/news/archive/chinanews-2018.jsonl.gz ---
2009a94 news 2026-10-05 第5轮: N1 语料→1,952,411条/10片(进2017-2018); 全链重跑 EVENTS 63,398(q<0.05=44,门�
--- 仓库 .git 实际体积 ---
592M	.git

=== 5. 是否已 push 到远端（污染是否传出去了）===
ecbc9c0 perf(guard): 体积红线(用户明令) — 单个文件>=5MB 一律不入 git, 改走百度云盘; 旧口径'>20MB'作废(漏掉了
b139a9e news 2026-10-05: N1 r6 语料→2,267,862/11片(2016起) + 第十五轮 news +4(华为×高通专利·台达×英伟达Hyperion·机
2009a94 news 2026-10-05 第5轮: N1 语料→1,952,411条/10片(进2017-2018); 全链重跑 EVENTS 63,398(q<0.05=44,门槛19); 第十四轮�
e4712e9 news 2026-10-05 第十三轮10条 + N1语料1645640条/8片 全链重跑(EVENTS 54485,门槛18,STABILITY 第5行)
177f640 news: N1 续抓进 2020 -> 游标 2020-04-19 (1,288,020 条/7 片); 全链重跑 EVENTS 44,782 (q<0.05=39, 门槛=14); 修 watcher p
--- 远端是否已含该文件 ---
⚠️ 远端已含 2017 语料（已污染）

=== 6. 是否有 .gitignore / .gitattributes 规则 ===
--- .gitignore ---
__pycache__/
*.pyc
*.pyo
*~
.DS_Store
--- .gitattributes ---
--- doc/personal-watch/run/news/archive/.gitignore ---
# 📦 体积红线（2026-10-05）：本目录语料分片普遍 6–12 MB（≥5MB）→ **一律不入 git**
#    改走百度云盘；清单登记在 INDEX_FILES.md（网盘路径 / 字节数 / sha256 / 存放位置）
#    规则出处：WATCH_NEWS_TASK.md §4-11 · news/archive/README.md §5
#
# ⚠️ 仅拦新文件；已跟踪的 chinanews-2016~2025.jsonl.gz 需 git rm --cached 才移出索引
*.jsonl.gz
*.gz
*.zip
*.tar.gz

# 抓取中间产物
fetch_raw/
*.part
--- doc/personal-watch/run/news/.gitignore ---

=== 7. 每轮抓取是否会持续生成新分片（判断增长趋势）===
-rw-rw-r-- 1 liuyang liuyang 15556999 Oct  5 15:28 chinanews-2016.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 10616975 Oct  5 14:53 chinanews-2017.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 11145051 Oct  5 13:58 chinanews-2018.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 12265872 Oct  5 13:46 chinanews-2019.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 12228659 Oct  5 13:43 chinanews-2020.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  9707401 Oct  5 13:22 chinanews-2021.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang 10319596 Oct  5 12:46 chinanews-2022.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  7660242 Oct  5 12:46 chinanews-2023.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  7449410 Oct  5 12:46 chinanews-2024.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  7130667 Oct  5 12:46 chinanews-2025.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang  5779016 Oct  5 12:46 chinanews-2026.jsonl.gz
-rw-rw-r-- 1 liuyang liuyang      463 Oct  5 15:28 .progress.json
-rw-rw-r-- 1 liuyang liuyang     2180 Oct  5 15:28 PROGRESS.md
```
