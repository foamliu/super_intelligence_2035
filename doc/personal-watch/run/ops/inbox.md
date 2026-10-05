# OPS INBOX — 运维下发命令（supervisor 编辑，中继只读执行）

<!-- RUN_ID: 0 -->

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

## RUN_ID 1 — 🩺 诊断：两条 loop 为何停了 27h？（OOM / 额度 / 进程没了）

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
