# OPS INBOX — 运维下发命令（supervisor 编辑，中继只读执行）

<!-- RUN_ID: 3 -->

> **用法**：在下面**新增一段** `## RUN_ID N`（N 递增）+ **一个 ```bash 块** → `git push`。
> 中继（`ops_relay.sh`）轮询发现 **RUN_ID 变大** → 执行 → 结果 append 到 `ops/outbox.md` → push。
>
> ✅ **本中继已修掉 BaiZe 的已知坑**：那边"**只执行第一个 ```bash 块**"（新命令会静默失效）；
> 我们**支持多段 RUN_ID 历史共存，总是执行 RUN_ID 最大那一段的块** → **老块不用删、不用降级**。
>
> **纪律**：
> ① 长输出一律加 `cut -c1-140`（`pgrep -af` 会把整份任务书打出来）；
> ② 🚫 **绝不整树 `du`**（大目录会跑很久）—— 只用 `df` + 有界定向 `du`（每条带 `timeout`）；
> ③ 单块总超时 **600s**，输出超 **20000 字符**会被截断；
> ④ 危险模式（`rm -rf /`、`mkfs`、**`git clean -fdx`**、**`git reset --hard`**、**杀 ops_relay**）会被**拒绝**。

---
## RUN_ID 3 — 🚨 紧急体检：**语料体积**（禁止 GB 级数据进 GitHub！）

**背景（supervisor 判定为红线事故）**：`git status` 显示
`news/archive/chinanews-2017.jsonl.gz` **已被 git 跟踪且 modified**，另有 **untracked `chinanews-2016.jsonl.gz`**。
→ ⚠️ **一年中国新闻语料打包进 git 仓库 = 仓库膨胀 / clone 变慢 / 超 GitHub 硬限（单文件 100MB 会直接拒收）**。
→ **任务：先量体积与仓库历史占用，判定是否已污染历史**。**本块只读，不做删除**（清理由 supervisor 定夺后下发 RUN_ID 4）。

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


## RUN_ID 2 — 🩺 追因：research 线为何缺席？loop 靠什么保活？

**背景（RUN_ID 1 的结论）**：
- **无 OOM**、内存 available 2661M、swap 用 0、CPU top1 2.2%、磁盘 11% → **停摆与资源无关**；
- ⚠️ **§1 只看到 `watch_news_loop.sh`（PID 98701），没有 research 线** → 两条线**不是同时死的**；
- `uptime` = **up 3:21**（12:31 时）→ 机器约 **09:10 重启**过，而停摆从 10-04 09:31 就开始了。

**要回答**：① research loop 是**没起**还是**起了又死**？② loop 靠 **cron / systemd / nohup / screen** 哪样保活？③ **重启后是谁把 news 拉起来的**？

```bash
echo "=== 0. 基本信息 ==="
hostname; date '+%F %T %Z'; uptime
echo
echo "=== 1. 所有 watch/ops 进程（含完整命令行，找保活父进程）==="
pgrep -af 'watch_(news|research|ops)' | cut -c1-160 || echo "(无任何 watch_* 进程)"
echo '--- 进程树（看谁是父进程/是否被 nohup、screen、tmux 托管）---'
ps -eo pid,ppid,etime,stat,args 2>/dev/null | grep -E 'watch_|cline' | grep -v grep | cut -c1-160
echo
echo "=== 2. 两条 loop 日志（存在性 + 大小 + 尾部）==="
for f in /tmp/watch_news_loop.log /tmp/watch_research_loop.log /tmp/watch_ops_relay.log; do
  echo "--- $f ---"
  if [ -e "$f" ]; then ls -la "$f" | cut -c1-120; tail -6 "$f" 2>/dev/null | cut -c1-160; else echo "(不存在)"; fi
done
echo
echo "=== 3. ⭐ 保活机制排查 ==="
echo '--- (a) crontab ---'
crontab -l 2>/dev/null | cut -c1-160 || echo "(无用户 crontab)"
sudo -n crontab -l 2>/dev/null | cut -c1-160 || true
echo '--- (b) systemd 单元 ---'
systemctl list-units --type=service --all 2>/dev/null | grep -iE 'watch|cline|relay' | cut -c1-140 || echo "(无匹配 systemd 单元)"
ls -la /etc/systemd/system/ 2>/dev/null | grep -iE 'watch|cline|relay' || echo "(无匹配 unit 文件)"
echo '--- (c) screen / tmux ---'
screen -ls 2>/dev/null | cut -c1-140 || echo "(无 screen)"
tmux ls 2>/dev/null | cut -c1-140 || echo "(无 tmux)"
echo '--- (d) 开机自启脚本 ---'
grep -rl 'watch_.*loop' /etc/rc.local /etc/cron.d /etc/crontab ~/.bashrc ~/.profile 2>/dev/null || echo "(常见自启位置未见 watch loop)"
echo
echo "=== 4. 机器重启 & 用户登录记录（解释 up 3:21）==="
who -b 2>/dev/null; last -n 8 reboot 2>/dev/null | cut -c1-100 || echo "(无 last 记录)"
echo
echo "=== 5. loop 脚本本体（看它自己有没有守护/重启逻辑）==="
cd ~/super_intelligence_2035/doc/personal-watch/run 2>/dev/null && {
  ls -la *.sh 2>/dev/null | cut -c1-140
  echo '--- watch_news_loop.sh 里的重启/守护相关行 ---'
  grep -nE 'nohup|while|trap|systemctl|sleep|exit|restart' watch_news_loop.sh 2>/dev/null | head -20 | cut -c1-160 || echo "(无此脚本)"
}
echo
echo "=== 6. git（确认 research 线是否已恢复提交）==="
cd ~/super_intelligence_2035 2>/dev/null && git log --oneline -8 | cut -c1-160
echo '--- dirty（只列前 12）---'
git status --short 2>/dev/null | head -12 | cut -c1-160
```

**阅读指引（我来判）**：
- §1 若 research **仍无** → 它是"**没被拉起**"，与 news 是**两套独立启动**（重启后靠手工/半自动）→ **根因是缺保活**；
- §3(a)(d) 若**有 cron/自启** → 说明**本该能自愈**，那"27h 未起"就是**保活条目本身失效**（要修）；若**全无** → **保活根本没建**，重启即停，**必须补**；
- §5 若 loop 内**有 `while` 但无 `trap`** → agent 被 kill 后脚本会**静默退出**（呼应"无日志、无痕迹"）。


**背景**：10-04 09:31 → 10-05 12:20 两条线无提交；BaiZe 线同期正常。机器为 **2 vCPU / 2 GiB**。

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
